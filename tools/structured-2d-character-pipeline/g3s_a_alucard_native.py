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
REVISION = "ALUCARD_NATIVE_128_REFERENCE_CONDITIONED_V1"

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


def make_reference(control_path: Path, out_path: Path) -> dict:
    src = Image.open(control_path).convert("RGB")
    arr = np.asarray(src, dtype=np.float32)
    h, w = arr.shape[:2]

    corner = max(8, min(w, h) // 24)
    samples = np.concatenate(
        [
            arr[:corner, :corner].reshape(-1, 3),
            arr[:corner, -corner:].reshape(-1, 3),
            arr[-corner:, :corner].reshape(-1, 3),
            arr[-corner:, -corner:].reshape(-1, 3),
        ],
        axis=0,
    )
    bg = np.median(samples, axis=0)
    dist = np.sqrt(np.sum((arr - bg[None, None, :]) ** 2, axis=2))
    mask = dist > 12.0

    bb = bbox_from_mask(mask)
    if bb is None:
        raise RuntimeError("Alucard conditioning prep could not isolate a subject from the Qwen control")
    x0, y0, x1, y1 = bb
    crop_rgb = arr[y0 : y1 + 1, x0 : x1 + 1].astype(np.uint8)
    crop_mask = mask[y0 : y1 + 1, x0 : x1 + 1]

    rgba = np.zeros((crop_rgb.shape[0], crop_rgb.shape[1], 4), dtype=np.uint8)
    rgba[:, :, :3] = crop_rgb
    rgba[:, :, 3] = np.where(crop_mask, 255, 0).astype(np.uint8)
    crop = Image.fromarray(rgba, "RGBA")

    target_h = 122
    scale = target_h / crop.height
    target_w = max(1, min(SIZE, round(crop.width * scale)))
    resized = crop.resize((target_w, target_h), Image.Resampling.NEAREST)
    canvas = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    xy = ((SIZE - target_w) // 2, (SIZE - target_h) // 2)
    canvas.alpha_composite(resized, xy)
    canvas.save(out_path)

    return {
        "control_size": [w, h],
        "background_rgb": [round(float(v), 4) for v in bg.tolist()],
        "subject_bbox": bb,
        "reference_size": [SIZE, SIZE],
        "reference_subject_size": [target_w, target_h],
        "reference_xy": list(xy),
    }


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
    sprite = sprite.convert("RGBA")
    x = (GAME_W - sprite.width) // 2
    y = (GAME_H - sprite.height) // 2
    bg.alpha_composite(sprite, (x, y))
    bg.convert("RGB").save(out_path)


def panel(image: Image.Image, label: str, size=(640, 360), nearest=False) -> Image.Image:
    out = Image.new("RGB", size, BG)
    im = image.convert("RGBA")
    max_w, max_h = size[0] - 32, size[1] - 48
    scale = min(max_w / im.width, max_h / im.height)
    nw, nh = max(1, round(im.width * scale)), max(1, round(im.height * scale))
    resample = Image.Resampling.NEAREST if nearest else Image.Resampling.LANCZOS
    im = im.resize((nw, nh), resample)
    tmp = Image.new("RGBA", size, (*BG, 255))
    tmp.alpha_composite(im, ((size[0] - nw) // 2, 28 + (max_h - nh) // 2))
    out = tmp.convert("RGB")
    d = ImageDraw.Draw(out)
    d.rectangle([4, 4, min(size[0] - 4, 610), 26], fill=(0, 0, 0))
    d.text((10, 9), label, fill=(240, 240, 240), font=ImageFont.load_default())
    return out


def contact_sheet(control: Image.Image, ref: Image.Image, raw: Image.Image, gameplay: Image.Image, out_path: Path) -> None:
    cells = [
        panel(control, "A Qwen control - conditioning only, NOT final art"),
        panel(ref, "B 128x128 RGBA conditioning reference - NOT final art", nearest=True),
        panel(raw, "C Alucard generated native 128x128 RGBA - no post resize", nearest=True),
        panel(gameplay, "D gameplay preview 640x360 - 1 asset pixel = 1 screen pixel", nearest=True),
    ]
    sheet = Image.new("RGB", (1280, 720), BG)
    sheet.paste(cells[0], (0, 0))
    sheet.paste(cells[1], (640, 0))
    sheet.paste(cells[2], (0, 360))
    sheet.paste(cells[3], (640, 360))
    sheet.save(out_path)


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
    control_path = Path(args.control)
    model_path = Path(args.model)
    pydeps_path = Path(args.pydeps)
    alucard_root = Path(args.alucard_root)
    if not control_path.is_file():
        raise FileNotFoundError(control_path)
    if not model_path.is_file():
        raise FileNotFoundError(model_path)
    if not pydeps_path.is_dir():
        raise FileNotFoundError(pydeps_path)
    if not alucard_root.is_dir():
        raise FileNotFoundError(alucard_root)

    # The Windows embeddable Python used by ComfyUI runs in isolated-path mode
    # when python._pth is present, so PYTHONPATH can be ignored. Inject the two
    # isolated Alucard paths explicitly before importing Alucard/OpenCLIP.
    sys.path.insert(0, str(pydeps_path))
    sys.path.insert(0, str(alucard_root))
    print("G3S_A_ALUCARD_IMPORT_PATH_MODE=EXPLICIT_SYS_PATH")
    print(f"G3S_A_ALUCARD_PYDEPS={pydeps_path}")

    import torch
    from alucard import Alucard

    if not torch.cuda.is_available():
        raise RuntimeError("Alucard spike requires CUDA; torch.cuda.is_available() is false")

    ref_path = out / "g3s_a_alucard_ref128.png"
    prep = make_reference(control_path, ref_path)

    print(f"G3S_A_ALUCARD_REVISION={REVISION}")
    print(f"G3S_A_ALUCARD_DEVICE={torch.cuda.get_device_name(0)}")
    print("G3S_A_ALUCARD_OUTPUT=NATIVE_128_RGBA")
    print("G3S_A_ALUCARD_QWEN_ROLE=CONDITIONING_ONLY")
    print("G3S_A_ALUCARD_POST_RESIZE=FALSE")

    model = Alucard.from_pretrained(str(model_path), device="cuda")
    sprite = model(
        PROMPT,
        ref=str(ref_path),
        num_samples=1,
        num_steps=20,
        cfg_text=5.0,
        cfg_ref=2.0,
        seed=args.seed,
    ).convert("RGBA")

    if sprite.size != (SIZE, SIZE):
        raise RuntimeError(f"Alucard returned {sprite.size}; expected native 128x128")

    raw_path = out / "g3s_a_alucard_raw128.png"
    sprite.save(raw_path)
    stats = alpha_stats(sprite)
    if stats["alpha_pixels"] < 128 or stats["visible_height"] < 48:
        raise RuntimeError(f"Alucard native output is effectively empty/tiny: {stats}")
    if stats["unique_opaque_rgb"] < 6:
        raise RuntimeError(f"Alucard native output is palette-collapsed: {stats}")

    preview_path = out / "g3s_a_alucard_gameplay_preview.png"
    gameplay_preview(sprite, preview_path)

    control = Image.open(control_path).convert("RGBA")
    ref = Image.open(ref_path).convert("RGBA")
    gameplay = Image.open(preview_path).convert("RGBA")
    sheet_path = out / "g3s_a_alucard_contact_sheet.png"
    contact_sheet(control, ref, sprite, gameplay, sheet_path)

    result = {
        "gate": "G3S-A-ALUCARD",
        "status": "REVIEW_REQUIRED",
        "revision": REVISION,
        "purpose": "one native 128x128 RGBA source-art architecture proof after PixelLock source failure",
        "seed": args.seed,
        "prompt": PROMPT,
        "sampling": {"steps": 20, "cfg_text": 5.0, "cfg_ref": 2.0},
        "alucard_code_commit": args.code_commit,
        "alucard_model_revision": args.model_revision,
        "model_sha256": sha256(model_path),
        "control_sha256": sha256(control_path),
        "conditioning_reference": str(ref_path),
        "conditioning_prep": prep,
        "raw": str(raw_path),
        "raw_sha256": sha256(raw_path),
        "raw_stats": stats,
        "gameplay_preview": str(preview_path),
        "contact_sheet": str(sheet_path),
        "rules": {
            "native_asset_raster": [128, 128],
            "post_generation_resize": False,
            "qwen_control_final_art_eligible": False,
            "direct_frame_animation_generation": False,
            "visual_review_required": True,
            "license_status": "RESEARCH_ONLY_PENDING_PRODUCTION_LICENSE_DECISION",
        },
    }
    (out / "g3s_a_alucard_result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"G3S_A_ALUCARD_RAW={raw_path}")
    print(f"G3S_A_ALUCARD_CONTACT={sheet_path}")
    print(f"G3S_A_ALUCARD_STATS={json.dumps(stats, separators=(',', ':'))}")


if __name__ == "__main__":
    main()
