from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

SIZE = 128
GAME_W, GAME_H = 640, 360
BG = (18, 18, 22)
REVISION = "ALUCARD_NATIVE_128_TEXT_ONLY_UPSTREAM_CONTROL_V1"
PROMPT = (
    "pixel art, colorful, medium-sized warrior woman, three-quarter view facing right, "
    "adult woman, lean resilient body, olive brown skin, very long heavy black hair, "
    "minimal ragged beige cloth, wrist shackles, ankle shackles, barefoot, no weapon"
)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def bbox_from_mask(mask: np.ndarray):
    ys, xs = np.where(mask)
    if len(xs) == 0:
        return None
    return [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())]


def alpha_stats(image: Image.Image) -> dict:
    rgba = np.asarray(image.convert("RGBA"), dtype=np.uint8)
    mask = rgba[:, :, 3] >= 128
    bb = bbox_from_mask(mask)
    opaque = rgba[mask, :3]
    unique = len({tuple(v) for v in opaque.tolist()}) if len(opaque) else 0
    return {
        "alpha_pixels": int(mask.sum()),
        "alpha_bbox": bb,
        "visible_height": 0 if bb is None else int(bb[3] - bb[1] + 1),
        "visible_width": 0 if bb is None else int(bb[2] - bb[0] + 1),
        "unique_opaque_rgb": int(unique),
    }


def gameplay_preview(sprite: Image.Image, out_path: Path) -> None:
    bg = Image.new("RGBA", (GAME_W, GAME_H), (*BG, 255))
    s = sprite.convert("RGBA")
    bg.alpha_composite(s, ((GAME_W - SIZE) // 2, (GAME_H - SIZE) // 2))
    bg.convert("RGB").save(out_path)


def panel(image: Image.Image, label: str, size=(640, 360), nearest=False) -> Image.Image:
    out = Image.new("RGBA", size, (*BG, 255))
    im = image.convert("RGBA")
    max_w, max_h = size[0] - 32, size[1] - 48
    scale = min(max_w / im.width, max_h / im.height)
    nw, nh = max(1, round(im.width * scale)), max(1, round(im.height * scale))
    im = im.resize((nw, nh), Image.Resampling.NEAREST if nearest else Image.Resampling.LANCZOS)
    out.alpha_composite(im, ((size[0] - nw) // 2, 28 + (max_h - nh) // 2))
    rgb = out.convert("RGB")
    d = ImageDraw.Draw(rgb)
    d.rectangle([4, 4, min(size[0] - 4, 620), 26], fill=(0, 0, 0))
    d.text((10, 9), label, fill=(240, 240, 240), font=ImageFont.load_default())
    return rgb


def alpha_panel(sprite: Image.Image) -> Image.Image:
    a = sprite.convert("RGBA").getchannel("A")
    rgba = Image.new("RGBA", (128, 128), (255, 255, 255, 255))
    rgba.putalpha(a)
    return rgba


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--alucard-root", required=True)
    ap.add_argument("--pydeps", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--control", required=True)
    ap.add_argument("--output-dir", required=True)
    ap.add_argument("--seed", type=int, default=20260905)
    ap.add_argument("--code-commit", required=True)
    ap.add_argument("--model-revision", required=True)
    args = ap.parse_args()

    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    model_path = Path(args.model)
    control_path = Path(args.control)
    pydeps = Path(args.pydeps)
    alucard_root = Path(args.alucard_root)
    for p in (model_path, control_path):
        if not p.is_file():
            raise FileNotFoundError(p)
    for p in (pydeps, alucard_root):
        if not p.is_dir():
            raise FileNotFoundError(p)

    sys.path.insert(0, str(pydeps))
    sys.path.insert(0, str(alucard_root))
    import torch
    from alucard import Alucard

    if not torch.cuda.is_available():
        raise RuntimeError("Alucard text-only control requires CUDA")

    print(f"G3S_A_ALUCARD_CONTROL_REVISION={REVISION}")
    print("G3S_A_ALUCARD_CONTROL_MODE=TEXT_ONLY_UPSTREAM_SUPPORTED")
    print("G3S_A_ALUCARD_REFERENCE_INPUT=NONE")
    print("G3S_A_ALUCARD_QWEN_ROLE=DISPLAY_ONLY_NOT_MODEL_INPUT")
    print(f"G3S_A_ALUCARD_DEVICE={torch.cuda.get_device_name(0)}")

    model = Alucard.from_pretrained(str(model_path), device="cuda")
    sprite = model(
        PROMPT,
        ref=None,
        num_samples=1,
        num_steps=20,
        cfg_text=5.0,
        seed=args.seed,
    ).convert("RGBA")
    if sprite.size != (SIZE, SIZE):
        raise RuntimeError(f"Alucard returned {sprite.size}; expected 128x128")

    raw_path = out / "g3s_a_alucard_text_raw128.png"
    sprite.save(raw_path)
    stats = alpha_stats(sprite)

    preview_path = out / "g3s_a_alucard_text_gameplay_preview.png"
    gameplay_preview(sprite, preview_path)

    control = Image.open(control_path).convert("RGBA")
    preview = Image.open(preview_path).convert("RGBA")
    cells = [
        panel(control, "A Qwen design reference - DISPLAY ONLY, not Alucard input"),
        panel(sprite, "B Alucard text-only native 128x128 RGBA", nearest=True),
        panel(preview, "C gameplay preview 640x360 - 1 asset px = 1 screen px", nearest=True),
        panel(alpha_panel(sprite), "D generated alpha footprint inspection", nearest=True),
    ]
    sheet = Image.new("RGB", (1280, 720), BG)
    sheet.paste(cells[0], (0, 0)); sheet.paste(cells[1], (640, 0))
    sheet.paste(cells[2], (0, 360)); sheet.paste(cells[3], (640, 360))
    sheet_path = out / "g3s_a_alucard_text_contact_sheet.png"
    sheet.save(sheet_path)

    result = {
        "gate": "G3S-A-ALUCARD-TEXT-CONTROL",
        "status": "REVIEW_REQUIRED",
        "revision": REVISION,
        "purpose": "validate Alucard in its documented text-to-sprite mode after invalid arbitrary-reference test",
        "seed": args.seed,
        "prompt": PROMPT,
        "sampling": {"steps": 20, "cfg_text": 5.0, "reference": None},
        "alucard_code_commit": args.code_commit,
        "alucard_model_revision": args.model_revision,
        "model_sha256": sha256(model_path),
        "qwen_control_sha256": sha256(control_path),
        "qwen_role": "display/design comparison only; not passed to model",
        "raw": str(raw_path),
        "raw_sha256": sha256(raw_path),
        "raw_stats": stats,
        "gameplay_preview": str(preview_path),
        "contact_sheet": str(sheet_path),
        "rules": {
            "native_asset_raster": [128, 128],
            "post_generation_resize": False,
            "reference_input": None,
            "visual_review_required": True,
            "production_adoption": False,
        },
    }
    (out / "g3s_a_alucard_text_result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"G3S_A_ALUCARD_CONTROL_STATS={json.dumps(stats, separators=(',', ':'))}")
    print(f"G3S_A_ALUCARD_CONTROL_CONTACT={sheet_path}")


if __name__ == "__main__":
    main()
