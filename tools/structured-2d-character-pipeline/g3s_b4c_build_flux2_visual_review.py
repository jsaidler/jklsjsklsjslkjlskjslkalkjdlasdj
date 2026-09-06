#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

LOGICAL_CANVAS = (96, 160)
UPSCALE = 6
MODEL_CANVAS = (LOGICAL_CANVAS[0] * UPSCALE, LOGICAL_CANVAS[1] * UPSCALE)
GAMEPLAY_CANVAS = (640, 360)


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def fit_inside(im: Image.Image, box: tuple[int, int]) -> Image.Image:
    bw, bh = box
    scale = min(bw / im.width, bh / im.height)
    size = (max(1, round(im.width * scale)), max(1, round(im.height * scale)))
    return im.resize(size, Image.Resampling.LANCZOS)


def paste_center(dst: Image.Image, src: Image.Image, box: tuple[int, int, int, int]) -> None:
    x0, y0, x1, y1 = box
    x = x0 + (x1 - x0 - src.width) // 2
    y = y0 + (y1 - y0 - src.height) // 2
    dst.alpha_composite(src.convert("RGBA"), (x, y))


def logical_mode_image(model_im: Image.Image) -> tuple[Image.Image, float]:
    rgb = model_im.convert("RGB")
    if rgb.size != MODEL_CANVAS:
        raise RuntimeError(f"generated image size mismatch: got={rgb.size} expected={MODEL_CANVAS}")
    out = Image.new("RGB", LOGICAL_CANVAS)
    src = rgb.load()
    dst = out.load()
    coherence_sum = 0.0
    count = 0
    for ly in range(LOGICAL_CANVAS[1]):
        for lx in range(LOGICAL_CANVAS[0]):
            colors = []
            x0 = lx * UPSCALE
            y0 = ly * UPSCALE
            for yy in range(y0, y0 + UPSCALE):
                for xx in range(x0, x0 + UPSCALE):
                    colors.append(src[xx, yy])
            color, n = Counter(colors).most_common(1)[0]
            dst[lx, ly] = color
            coherence_sum += n / float(UPSCALE * UPSCALE)
            count += 1
    return out, coherence_sum / max(1, count)


def gameplay_preview(logical: Image.Image) -> Image.Image:
    scene = Image.new("RGB", GAMEPLAY_CANVAS, (18, 18, 21))
    d = ImageDraw.Draw(scene)
    ground_y = 286
    d.rectangle((0, ground_y, GAMEPLAY_CANVAS[0], GAMEPLAY_CANVAS[1]), fill=(38, 31, 27))
    # The logical review frame already includes a flat conditioning field; crop a centered body zone for gameplay review.
    crop = logical.crop((18, 8, 80, 154))
    x = GAMEPLAY_CANVAS[0] // 2 - crop.width // 2
    y = ground_y - crop.height
    scene.paste(crop, (x, y))
    return scene


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--master", required=True)
    ap.add_argument("--body-logical", required=True)
    ap.add_argument("--generated", required=True)
    ap.add_argument("--workspace", required=True)
    ap.add_argument("--prompt", required=True)
    args = ap.parse_args()

    master_path = Path(args.master)
    body_logical_path = Path(args.body_logical)
    generated_path = Path(args.generated)
    workspace = Path(args.workspace)
    workspace.mkdir(parents=True, exist_ok=True)
    for p in (master_path, body_logical_path, generated_path):
        if not p.is_file():
            raise FileNotFoundError(p)

    master = Image.open(master_path).convert("RGBA")
    body_logical = Image.open(body_logical_path).convert("RGB")
    generated = Image.open(generated_path).convert("RGB")
    logical, block_coherence = logical_mode_image(generated)
    gameplay = gameplay_preview(logical)

    logical_path = workspace / "g3s_b4c_flux2_logical_review.png"
    gameplay_path = workspace / "g3s_b4c_flux2_gameplay_review.png"
    sheet_path = workspace / "g3s_b4c_flux2_contact_sheet.png"
    meta_path = workspace / "g3s_b4c_flux2_review.json"
    logical.save(logical_path)
    gameplay.save(gameplay_path)

    sheet = Image.new("RGBA", (1600, 900), (16, 16, 19, 255))
    d = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()
    d.text((24, 18), "G3S-B4C FLUX2 VISUAL HAIR ADAPTER — REVIEW ONLY", fill=(238,238,242), font=font)
    d.text((24, 42), "GOAL: prove real visual adaptation of canonical hair identity to the actual B3B pose; no procedural hair geometry", fill=(220,180,90), font=font)
    d.text((24, 64), "NO PRODUCTION PROMOTION IN THIS STEP", fill=(220,180,90), font=font)

    d.text((24, 96), "A  CANONICAL MASTER / HAIR IDENTITY", fill=(220,220,225), font=font)
    paste_center(sheet, fit_inside(master, (350, 650)), (20, 120, 390, 800))

    d.text((420, 96), "B  EXACT B3B BODY CONDITIONING REFERENCE (logical 96x160 shown 3x)", fill=(220,220,225), font=font)
    body_big = body_logical.resize((body_logical.width*3, body_logical.height*3), Image.Resampling.NEAREST).convert("RGBA")
    sheet.alpha_composite(body_big, (450, 150))

    d.text((770, 96), "C  FLUX2 GENERATED VISUAL ADAPTATION", fill=(220,220,225), font=font)
    paste_center(sheet, fit_inside(generated.convert("RGBA"), (360, 650)), (740, 120, 1130, 800))

    d.text((1160, 96), "D  LOGICAL 96x160 MODE-SAMPLE REVIEW 3x", fill=(220,220,225), font=font)
    logical_big = logical.resize((logical.width*3, logical.height*3), Image.Resampling.NEAREST).convert("RGBA")
    sheet.alpha_composite(logical_big, (1190, 150))

    d.text((420, 690), "E  640x360 GAMEPLAY-SCALE REVIEW", fill=(220,220,225), font=font)
    gp_small = gameplay.resize((640,360), Image.Resampling.NEAREST).convert("RGBA")
    gp_small.thumbnail((640, 180), Image.Resampling.NEAREST)
    sheet.alpha_composite(gp_small, (420, 715))

    d.text((1160, 690), "F  REVIEW FACTS", fill=(220,220,225), font=font)
    facts = [
        f"generated SHA256: {file_sha256(generated_path)[:16]}...",
        f"6x6 block coherence: {block_coherence:.4f}",
        "body production asset modified: NO",
        "master used as pose template: NO",
        "procedural Pillow hair geometry: NO",
        "external paid API: NO",
        "automatic promotion: NO",
    ]
    yy = 720
    for fact in facts:
        d.text((1160, yy), fact, fill=(190,190,196), font=font)
        yy += 24

    sheet.convert("RGB").save(sheet_path, quality=95)

    meta = {
        "gate": "G3S-B4",
        "revision": "B4C_FLUX2_VISUAL_ADAPTER_V1",
        "status": "VISUAL_REVIEW_REQUIRED",
        "purpose": "visual adaptation proof only; generated pixels are not production hair layers",
        "generated_path": str(generated_path),
        "generated_sha256": file_sha256(generated_path),
        "logical_review_path": str(logical_path),
        "gameplay_review_path": str(gameplay_path),
        "contact_sheet": str(sheet_path),
        "contact_sheet_sha256": file_sha256(sheet_path),
        "model_canvas": list(MODEL_CANVAS),
        "logical_canvas": list(LOGICAL_CANVAS),
        "integer_reference_upscale": UPSCALE,
        "block_coherence_6x6": block_coherence,
        "prompt": args.prompt,
        "production_body_modified": False,
        "automatic_promotion": False,
        "next_if_visual_pass": "author separate rear_hair and front_hair passes using the same visual adapter, then validate/persist native 2D layers"
    }
    meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print("G3S-B4C REVIEW BUILD: PASS")
    print(f"CONTACT: {sheet_path}")
    print(f"META:    {meta_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
