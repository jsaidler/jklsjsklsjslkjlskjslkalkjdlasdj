#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw

EXPECTED_SHA256 = "f2ba82dbcd759c55cbc1c70cf1100bd85a0319cf5fe53258e461406ba55cd08a"
EXPECTED_SIZE = (1168, 784)
# Locked final visual reference: rightmost front-three-quarter figure.
SOURCE_CROP = (894, 36, 1089, 717)  # x0, y0, x1, y1; 195x681 visible-source crop
TARGET_VISIBLE_HEIGHT = 128
BG = (2, 5, 12)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def find_reference(explicit: str | None, repo_root: Path) -> Path:
    candidates: list[Path] = []
    if explicit:
        candidates.append(Path(explicit))
    candidates.append(repo_root / "assets/source/characters/exilada/reference/exilada_body_pixel_turnaround_locked.jpg")

    home = Path.home()
    for base in (home / "Downloads", home / "Desktop", home / "Pictures"):
        if base.exists():
            candidates.extend(base.glob("*.jpg"))
            candidates.extend(base.glob("*.jpeg"))
            candidates.extend(base.glob("*.png"))

    seen: set[Path] = set()
    for p in candidates:
        try:
            rp = p.resolve()
        except Exception:
            rp = p
        if rp in seen or not p.is_file():
            continue
        seen.add(rp)
        try:
            if sha256(p).lower() == EXPECTED_SHA256:
                return p
        except OSError:
            pass

    raise FileNotFoundError(
        "locked pixel-art body reference not found. "
        f"Expected SHA256={EXPECTED_SHA256}. "
        "Place the exact image at assets/source/characters/exilada/reference/"
        "exilada_body_pixel_turnaround_locked.jpg or keep it in Downloads/Desktop/Pictures."
    )


def key_background(crop: Image.Image) -> Image.Image:
    rgb = crop.convert("RGB")
    px = rgb.load()
    out = Image.new("RGBA", rgb.size, (0, 0, 0, 0))
    op = out.load()

    # Conservative chroma key for the nearly-black/navy flat background.
    # It only removes pixels close to the known background family; dark brown outline pixels survive.
    for y in range(rgb.height):
        for x in range(rgb.width):
            r, g, b = px[x, y]
            dr, dg, db = r - BG[0], g - BG[1], b - BG[2]
            dist2 = dr * dr + dg * dg + db * db
            # JPEG background variation is tiny; keep threshold deliberately low.
            a = 0 if dist2 <= 18 * 18 and max(r, g, b) < 40 else 255
            op[x, y] = (r, g, b, a)
    return out


def alpha_bbox(im: Image.Image) -> tuple[int, int, int, int]:
    a = im.getchannel("A")
    b = a.getbbox()
    if not b:
        raise RuntimeError("foreground alpha is empty")
    return b


def checker(size: tuple[int, int], cell: int = 8) -> Image.Image:
    w, h = size
    out = Image.new("RGB", size, (32, 32, 34))
    d = ImageDraw.Draw(out)
    c1, c2 = (39, 39, 42), (52, 52, 56)
    for y in range(0, h, cell):
        for x in range(0, w, cell):
            d.rectangle([x, y, x + cell - 1, y + cell - 1], fill=c1 if ((x // cell + y // cell) & 1) == 0 else c2)
    return out


def composite_checker(sprite: Image.Image, scale: int = 4, pad: int = 24) -> Image.Image:
    enlarged = sprite.resize((sprite.width * scale, sprite.height * scale), Image.Resampling.NEAREST)
    bg = checker((enlarged.width + pad * 2, enlarged.height + pad * 2), 16)
    bg.paste(enlarged, (pad, pad), enlarged)
    return bg


def gameplay_preview(sprite: Image.Image) -> Image.Image:
    scene = Image.new("RGB", (640, 360), (17, 17, 19))
    d = ImageDraw.Draw(scene)
    d.rectangle([0, 275, 639, 359], fill=(35, 30, 27))
    x = 320 - sprite.width // 2
    y = 275 - sprite.height
    scene.paste(sprite, (x, y), sprite)
    return scene


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", required=True)
    ap.add_argument("--output-dir", required=True)
    ap.add_argument("--reference", default=None)
    args = ap.parse_args()

    repo_root = Path(args.repo_root)
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    ref = find_reference(args.reference, repo_root)
    if sha256(ref).lower() != EXPECTED_SHA256:
        raise RuntimeError("reference SHA mismatch")

    source = Image.open(ref).convert("RGB")
    if source.size != EXPECTED_SIZE:
        raise RuntimeError(f"reference size mismatch: got={source.size} expected={EXPECTED_SIZE}")

    crop = source.crop(SOURCE_CROP)
    rgba = key_background(crop)
    b = alpha_bbox(rgba)
    rgba = rgba.crop(b)

    target_w = max(1, round(rgba.width * TARGET_VISIBLE_HEIGHT / rgba.height))
    # The locked source is already pixel-art imagery. This is scale normalization only:
    # nearest-neighbor, no averaging, no palette synthesis, no anatomy repair.
    sprite = rgba.resize((target_w, TARGET_VISIBLE_HEIGHT), Image.Resampling.NEAREST)

    candidate = out_dir / "g3s_b3b_v4_pixel_reference_candidate.png"
    enlarged = out_dir / "g3s_b3b_v4_pixel_reference_candidate_4x.png"
    gameplay = out_dir / "g3s_b3b_v4_gameplay_preview_640x360.png"
    contact = out_dir / "g3s_b3b_v4_contact_sheet.png"
    manifest = out_dir / "g3s_b3b_v4_result.json"

    sprite.save(candidate)
    composite_checker(sprite, 4).save(enlarged)
    gameplay_preview(sprite).save(gameplay)

    ref_preview = crop.resize((195, 681), Image.Resampling.NEAREST)
    panel_a = Image.new("RGB", (260, 720), (15, 15, 17))
    panel_a.paste(ref_preview, (32, 20))
    panel_b = composite_checker(sprite, 4)
    panel_c = gameplay_preview(sprite)
    sheet = Image.new("RGB", (260 + panel_b.width + 640 + 40, 720), (12, 12, 14))
    sheet.paste(panel_a, (0, 0))
    sheet.paste(panel_b, (280, 70))
    sheet.paste(panel_c, (300 + panel_b.width, 180))
    d = ImageDraw.Draw(sheet)
    d.text((10, 5), "A LOCKED PIXEL-ART REFERENCE: 3/4 CROP", fill=(235, 235, 235))
    d.text((280, 45), f"B NATIVE CANDIDATE: {sprite.width}x{sprite.height} @4x", fill=(235, 235, 235))
    d.text((300 + panel_b.width, 155), "C 640x360 GAMEPLAY PREVIEW", fill=(235, 235, 235))
    sheet.save(contact)

    data = {
        "gate": "G3S-B3B-V4-PIXEL-REFERENCE-NORMALIZATION",
        "status": "REVIEW_REQUIRED_NOT_PRODUCTION_PASS",
        "reference": str(ref),
        "reference_sha256": EXPECTED_SHA256,
        "reference_size": list(EXPECTED_SIZE),
        "source_crop": list(SOURCE_CROP),
        "candidate_size": list(sprite.size),
        "visible_height_px": TARGET_VISIBLE_HEIGHT,
        "method": "locked pixel-art source crop -> conservative flat-background key -> nearest-neighbor scale normalization only",
        "forbidden_operations_used": [],
        "automatic_promotion": False,
        "note": "This is valid to review because the locked source is already pixel-art imagery; no render-to-pixel conversion, palette synthesis, filtering, anatomy repair, or procedural silhouette authoring is performed. Visual PASS is still mandatory."
    }
    manifest.write_text(json.dumps(data, indent=2), encoding="utf-8")

    print(f"REFERENCE: {ref}")
    print(f"CANDIDATE: {candidate}")
    print(f"CONTACT:   {contact}")
    print(f"GAMEPLAY:  {gameplay}")
    print("STATUS: REVIEW REQUIRED - NOT AUTOMATICALLY APPROVED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
