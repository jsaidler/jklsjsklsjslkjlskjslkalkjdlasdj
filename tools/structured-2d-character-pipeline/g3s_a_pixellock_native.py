from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import shutil
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

# This helper intentionally reuses PixelLock's production engine verbatim
# (pixel_editor.py / validate.py) from a pinned MIT-licensed checkout.
# PixelLock itself is not vendored into this repository.

LOGICAL = 64
OUTPUT = 128
GAME_W = 640
GAME_H = 360
TARGET_LOGICAL_H = 62
GAME_X = 256
GAME_Y = 116
BG = (18, 18, 22)
REVISION = "PIXELLOCK_64_TO_128_FOOTPRINT_LOCKED_V1"

PROMPT = (
    "Reauthor this full-body woman as the Exilada, a severe sword-and-sorcery "
    "protagonist. Preserve the exact silhouette/pose footprint. Use deliberate "
    "modern pixel-art clusters, not smooth illustration. Adult lean resilient "
    "female anatomy; olive-brown skin; extremely long heavy near-black hair as "
    "the dominant silhouette mass; minimal degraded asymmetric beige cloth; "
    "wounds/scars; visible wrist and ankle restraints in dull metal; barefoot; "
    "no weapon. Keep skin, hair, cloth and metal materially distinct. Use a "
    "restrained readable palette, strong value grouping, coherent upper-left "
    "lighting, hard cluster edges and purposeful highlights. Avoid neon colors, "
    "purple clothing, generic armor, shoes, smooth gradients and painterly noise."
)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def alpha_bbox(path: Path):
    a = Image.open(path).convert("RGBA").getchannel("A")
    return a.getbbox()


def _border_pixels(arr: np.ndarray, n: int = 16) -> np.ndarray:
    return np.concatenate(
        [
            arr[:n].reshape(-1, 3),
            arr[-n:].reshape(-1, 3),
            arr[:, :n].reshape(-1, 3),
            arr[:, -n:].reshape(-1, 3),
        ],
        axis=0,
    )


def make_scaffold(control: Path, scaffold: Path) -> dict:
    src = Image.open(control).convert("RGB")
    arr = np.asarray(src, dtype=np.float32)
    border = _border_pixels(arr)
    bg = np.median(border, axis=0)
    border_spread = float(np.mean(np.std(border, axis=0)))
    threshold = max(8.0, border_spread * 5.0)
    dist = np.linalg.norm(arr - bg[None, None, :], axis=2)
    mask = dist > threshold
    ys, xs = np.where(mask)
    if xs.size == 0:
        raise RuntimeError("PixelLock scaffold extraction found no subject foreground")
    bbox = (int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1)

    crop = src.crop(bbox)
    mask_full = Image.fromarray((mask.astype(np.uint8) * 255), mode="L")
    mask_crop = mask_full.crop(bbox)
    scale = TARGET_LOGICAL_H / crop.height
    target_w = max(1, round(crop.width * scale))
    if target_w > LOGICAL - 2:
        target_w = LOGICAL - 2
    target_h = TARGET_LOGICAL_H

    rgb_small = crop.resize((target_w, target_h), Image.Resampling.LANCZOS)
    alpha_small = mask_crop.resize((target_w, target_h), Image.Resampling.LANCZOS)
    alpha_small = alpha_small.point(lambda v: 255 if v >= 96 else 0)

    # Conditioning-only palette scaffold. These colors are not final art.
    # Quantization exists only to give PixelLock a compact native-grid texture.
    rgb_small = rgb_small.quantize(
        colors=16, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE
    ).convert("RGB")
    rgba_small = Image.merge("RGBA", (*rgb_small.split(), alpha_small))

    canvas = Image.new("RGBA", (LOGICAL, LOGICAL), (0, 0, 0, 0))
    x = (LOGICAL - target_w) // 2
    y = 1
    canvas.alpha_composite(rgba_small, (x, y))
    scaffold.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(scaffold, "PNG")
    bb = canvas.getchannel("A").getbbox()
    if bb is None:
        raise RuntimeError("PixelLock scaffold alpha is empty after placement")
    logical_h = bb[3] - bb[1]
    if logical_h < 58 or logical_h > 64:
        raise RuntimeError(f"PixelLock scaffold height out of range: {logical_h}px bbox={bb}")
    return {
        "control_size": list(src.size),
        "control_background_rgb": [round(float(v), 3) for v in bg],
        "control_background_spread": round(border_spread, 4),
        "foreground_threshold": round(threshold, 4),
        "control_subject_bbox": list(bbox),
        "logical_canvas": [LOGICAL, LOGICAL],
        "logical_subject_bbox": list(bb),
        "logical_subject_height": logical_h,
        "logical_subject_width": bb[2] - bb[0],
    }


def composite_dark(sprite: Image.Image, panel_size=(GAME_W, GAME_H), scale=1) -> Image.Image:
    panel = Image.new("RGB", panel_size, BG)
    if scale != 1:
        sprite = sprite.resize(
            (sprite.width * scale, sprite.height * scale), Image.Resampling.NEAREST
        )
    rgba = sprite.convert("RGBA")
    x = (panel.width - rgba.width) // 2
    y = (panel.height - rgba.height) // 2
    panel.paste(rgba.convert("RGB"), (x, y), rgba.getchannel("A"))
    return panel


def gameplay_preview(raw: Path, out: Path) -> None:
    sprite = Image.open(raw).convert("RGBA")
    if sprite.size != (OUTPUT, OUTPUT):
        raise RuntimeError(f"PixelLock raw must be {OUTPUT}x{OUTPUT}; got {sprite.size}")
    game = Image.new("RGB", (GAME_W, GAME_H), BG)
    game.paste(sprite.convert("RGB"), (GAME_X, GAME_Y), sprite.getchannel("A"))
    game.save(out, "PNG")


def label_panel(panel: Image.Image, text: str) -> Image.Image:
    panel = panel.copy()
    d = ImageDraw.Draw(panel)
    d.rectangle((6, 6, min(panel.width - 6, 560), 30), fill=(0, 0, 0))
    d.text((12, 11), text, fill=(255, 255, 255))
    return panel


def make_contact(control: Path, scaffold: Path, raw: Path, game: Path, out: Path) -> None:
    ctl = Image.open(control).convert("RGB")
    ctl.thumbnail((GAME_W - 30, GAME_H - 45), Image.Resampling.LANCZOS)
    p0 = Image.new("RGB", (GAME_W, GAME_H), BG)
    p0.paste(ctl, ((GAME_W - ctl.width) // 2, (GAME_H - ctl.height) // 2))
    p0 = label_panel(p0, "A Qwen control - design/pose conditioning only, NOT final art")

    sc = Image.open(scaffold).convert("RGBA")
    p1 = label_panel(composite_dark(sc, scale=4), "B 64x64 conditioning scaffold - NOT final art")

    rr = Image.open(raw).convert("RGBA")
    p2 = label_panel(composite_dark(rr, scale=2), "C PixelLock generated 128x128 native grid - no post resize")

    p3 = label_panel(Image.open(game).convert("RGB"), "D gameplay preview at 640x360 - 1 asset pixel = 1 screen pixel")

    sheet = Image.new("RGB", (GAME_W * 2, GAME_H * 2), (8, 8, 10))
    for i, panel in enumerate((p0, p1, p2, p3)):
        sheet.paste(panel, ((i % 2) * GAME_W, (i // 2) * GAME_H))
    sheet.save(out, "PNG")


async def run_pixellock(pixellock_root: Path, api: str, scaffold: Path, out_dir: Path):
    app_dir = pixellock_root / "app"
    if not (app_dir / "pixel_editor.py").exists():
        raise RuntimeError(f"Pinned PixelLock checkout missing app/pixel_editor.py: {app_dir}")
    sys.path.insert(0, str(app_dir))
    import pixel_editor  # type: ignore

    pixel_editor.URL = api.rstrip("/") + "/v1/chat/completions"
    result = await pixel_editor.edit_file(scaffold, PROMPT, True, out_dir)
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--api", required=True)
    ap.add_argument("--pixellock-root", required=True)
    ap.add_argument("--control", required=True)
    ap.add_argument("--output-dir", required=True)
    ap.add_argument("--model-path", required=True)
    ap.add_argument("--model-revision", required=True)
    ap.add_argument("--pixellock-commit", required=True)
    ap.add_argument("--llama-build", required=True)
    args = ap.parse_args()

    control = Path(args.control).resolve()
    out = Path(args.output_dir).resolve()
    pixellock_root = Path(args.pixellock_root).resolve()
    model_path = Path(args.model_path).resolve()
    out.mkdir(parents=True, exist_ok=True)
    if not control.exists():
        raise RuntimeError(f"Qwen control source missing: {control}")
    if not model_path.exists():
        raise RuntimeError(f"PixelLock GGUF missing: {model_path}")

    scaffold = out / "g3s_a_pixellock_scaffold64.png"
    prep = make_scaffold(control, scaffold)
    print("G3S_A_PIXELLOCK_SCAFFOLD=PASS " + json.dumps(prep, sort_keys=True))
    print("G3S_A_PIXELLOCK_LOGICAL_SOURCE=64x64")
    print("G3S_A_PIXELLOCK_GENERATED_OUTPUT=128x128")
    print("G3S_A_PIXELLOCK_POST_RESIZE=FALSE")

    engine_out = out / "engine"
    engine_out.mkdir(parents=True, exist_ok=True)
    result = asyncio.run(run_pixellock(pixellock_root, args.api, scaffold, engine_out))
    print("G3S_A_PIXELLOCK_ENGINE=" + json.dumps(result, sort_keys=True))
    if not result.get("parsed"):
        raise RuntimeError("PixelLock output did not parse: " + repr(result))
    if result.get("footprint_perfect") is not True:
        raise RuntimeError("PixelLock footprint lock failed: " + repr(result))

    produced = engine_out / "g3s_a_pixellock_scaffold64__2x.png"
    if not produced.exists():
        raise RuntimeError(f"PixelLock expected generated PNG missing: {produced}")
    raw = out / "g3s_a_pixellock_raw128.png"
    shutil.copy2(produced, raw)
    if Image.open(raw).size != (OUTPUT, OUTPUT):
        raise RuntimeError(f"PixelLock output wrong dimensions: {Image.open(raw).size}")
    bb = alpha_bbox(raw)
    if bb is None:
        raise RuntimeError("PixelLock output alpha is empty")
    hero_h = bb[3] - bb[1]
    if hero_h < 116 or hero_h > 128:
        raise RuntimeError(f"PixelLock generated hero height out of range: {hero_h}px bbox={bb}")

    game = out / "g3s_a_pixellock_gameplay_preview.png"
    gameplay_preview(raw, game)
    contact = out / "g3s_a_pixellock_contact_sheet.png"
    make_contact(control, scaffold, raw, game, contact)

    receipt = {
        "gate": "G3S-A-PIXELLOCK",
        "status": "REVIEW_REQUIRED",
        "revision": REVISION,
        "purpose": "native pixel-grid static Exilada source test after latent-diffusion native routes failed",
        "qwen_control": str(control),
        "qwen_control_sha256": sha256(control),
        "qwen_role": "design/pose conditioning only; its RGB pixels are not final art",
        "scaffold": str(scaffold),
        "scaffold_sha256": sha256(scaffold),
        "scaffold_prep": prep,
        "pixellock_commit": args.pixellock_commit,
        "pixellock_model_revision": args.model_revision,
        "pixellock_model": str(model_path),
        "pixellock_model_sha256": sha256(model_path),
        "llama_cpp_build": args.llama_build,
        "engine_result": result,
        "raw": str(raw),
        "raw_sha256": sha256(raw),
        "raw_size": [OUTPUT, OUTPUT],
        "raw_alpha_bbox": list(bb),
        "raw_visible_height": hero_h,
        "gameplay_preview": str(game),
        "gameplay_preview_sha256": sha256(game),
        "contact_sheet": str(contact),
        "contact_sheet_sha256": sha256(contact),
        "rules": {
            "footprint_locked_by_gbnf": True,
            "post_generation_resize": False,
            "qwen_control_final_art_eligible": False,
            "direct_frame_animation_generation": False,
            "visual_review_required": True,
            "review_order": [
                "major topology and readable hands/feet",
                "Exilada identity: hair/skin/cloth/restraints/bare feet",
                "intentional native pixel clusters rather than block mannequin",
                "gameplay readability at 640x360",
            ],
        },
    }
    result_path = out / "g3s_a_pixellock_result.json"
    result_path.write_text(json.dumps(receipt, indent=2, ensure_ascii=False), encoding="utf-8")
    print("G3S_A_PIXELLOCK_FOOTPRINT=PASS")
    print("G3S_A_PIXELLOCK_RAW=" + str(raw))
    print("G3S_A_PIXELLOCK_CONTACT=" + str(contact))
    print("G3S_A_PIXELLOCK_RESULT=" + str(result_path))
    print("G3S_A_PIXELLOCK=REVIEW_REQUIRED")


if __name__ == "__main__":
    main()
