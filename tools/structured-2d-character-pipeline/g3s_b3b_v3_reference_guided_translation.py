from __future__ import annotations

import argparse
import hashlib
import json
import os
from collections import deque
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

EXPECTED_SHA256 = "2773c199b3ff28ad5a72e33feb97201a9567a633f8466620084362fd9aae7474"
EXPECTED_SIZE = (1168, 784)
CANVAS = (128, 128)
GAMEPLAY = (640, 360)
THREEQ_BOX = (876, 0, 1168, 784)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def candidate_roots() -> list[Path]:
    home = Path.home()
    names = ["Downloads", "Desktop", "Pictures", "Documents", "OneDrive", "Google Drive", "GoogleDrive"]
    roots: list[Path] = []
    for name in names:
        p = home / name
        if p.exists():
            roots.append(p)
    userprofile = os.environ.get("USERPROFILE")
    if userprofile:
        up = Path(userprofile)
        for name in names:
            p = up / name
            if p.exists() and p not in roots:
                roots.append(p)
    return roots


def find_reference(explicit: str | None) -> Path:
    if explicit:
        p = Path(explicit)
        if not p.is_file():
            raise FileNotFoundError(f"reference not found: {p}")
        got = sha256_file(p)
        if got != EXPECTED_SHA256:
            raise RuntimeError(f"reference SHA mismatch: got={got} expected={EXPECTED_SHA256}")
        return p

    checked = 0
    for root in candidate_roots():
        try:
            paths = root.rglob("*")
        except OSError:
            continue
        for p in paths:
            if checked >= 5000:
                break
            try:
                if not p.is_file() or p.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp"}:
                    continue
                if p.stat().st_size > 30 * 1024 * 1024:
                    continue
                checked += 1
                if sha256_file(p) == EXPECTED_SHA256:
                    return p
            except (OSError, PermissionError):
                continue
    raise FileNotFoundError(
        "approved body reference was not found automatically. "
        f"Expected SHA256={EXPECTED_SHA256}. Checked common user image folders."
    )


def largest_component(mask: np.ndarray) -> np.ndarray:
    h, w = mask.shape
    seen = np.zeros_like(mask, dtype=np.uint8)
    best: list[tuple[int, int]] = []
    for y in range(h):
        for x in range(w):
            if not mask[y, x] or seen[y, x]:
                continue
            q: deque[tuple[int, int]] = deque([(y, x)])
            seen[y, x] = 1
            comp: list[tuple[int, int]] = []
            while q:
                cy, cx = q.popleft()
                comp.append((cy, cx))
                for ny, nx in ((cy - 1, cx), (cy + 1, cx), (cy, cx - 1), (cy, cx + 1)):
                    if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and not seen[ny, nx]:
                        seen[ny, nx] = 1
                        q.append((ny, nx))
            if len(comp) > len(best):
                best = comp
    out = np.zeros_like(mask, dtype=bool)
    for y, x in best:
        out[y, x] = True
    return out


def build_native_guide(reference: Image.Image) -> tuple[Image.Image, Image.Image, dict]:
    panel = reference.crop(THREEQ_BOX).convert("RGB")
    arr = np.asarray(panel, dtype=np.uint8)
    luma = arr.mean(axis=2)
    raw = luma > 55.0
    comp = largest_component(raw)
    ys, xs = np.where(comp)
    if len(xs) == 0:
        raise RuntimeError("could not isolate three-quarter body reference")
    x0, x1 = int(xs.min()), int(xs.max())
    y0, y1 = int(ys.min()), int(ys.max())
    body_rgb = panel.crop((x0, y0, x1 + 1, y1 + 1))
    body_mask = Image.fromarray((comp[y0 : y1 + 1, x0 : x1 + 1] * 255).astype(np.uint8), "L")

    new_h = 128
    new_w = max(1, round(body_rgb.width * (new_h / body_rgb.height)))
    guide_rgb = body_rgb.resize((new_w, new_h), Image.Resampling.LANCZOS)
    guide_mask = body_mask.resize((new_w, new_h), Image.Resampling.NEAREST)

    canvas = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    xoff = (CANVAS[0] - new_w) // 2
    rgba = guide_rgb.convert("RGBA")
    rgba.putalpha(guide_mask)
    canvas.alpha_composite(rgba, (xoff, 0))

    mask_canvas = Image.new("L", CANVAS, 0)
    mask_canvas.paste(guide_mask, (xoff, 0))
    meta = {
        "panel_box": list(THREEQ_BOX),
        "isolated_bbox_in_panel": [x0, y0, x1, y1],
        "native_body_width": new_w,
        "native_body_height": 128,
        "native_x_offset": xoff,
    }
    return canvas, mask_canvas, meta


def mode_cleanup(indexed: np.ndarray, alpha: np.ndarray) -> np.ndarray:
    out = indexed.copy()
    h, w = indexed.shape
    for y in range(1, h - 1):
        for x in range(1, w - 1):
            if not alpha[y, x]:
                continue
            vals = indexed[y - 1 : y + 2, x - 1 : x + 2][alpha[y - 1 : y + 2, x - 1 : x + 2]]
            if len(vals) < 5:
                continue
            unique, counts = np.unique(vals, return_counts=True)
            majority = int(unique[np.argmax(counts)])
            if counts.max() >= 6 and indexed[y, x] != majority:
                out[y, x] = majority
    return out


def repair_pelvis(rgb: np.ndarray, alpha: np.ndarray) -> np.ndarray:
    out = rgb.copy()
    # Native coordinates correspond to the approved 3/4 view after 128 px normalization.
    y0, y1 = 53, 68
    x0, x1 = 53, 72
    region = out[y0:y1, x0:x1]
    reg_a = alpha[y0:y1, x0:x1]
    lum = region.mean(axis=2)
    skin_candidates = region[(reg_a) & (lum > 72)]
    if len(skin_candidates):
        base = np.median(skin_candidates, axis=0).astype(np.uint8)
        dark = (reg_a) & (lum < 60)
        region[dark] = base
    # Explicit native-pixel anatomical V/central crease in skin tones, not garment ownership.
    shadow = np.array([82, 57, 38], dtype=np.uint8)
    deep = np.array([61, 41, 28], dtype=np.uint8)
    for x, y in [(58, 58), (59, 59), (60, 60), (61, 61), (67, 58), (66, 59), (65, 60), (64, 61)]:
        if 0 <= y < 128 and 0 <= x < 128 and alpha[y, x]:
            out[y, x] = shadow
    for x, y in [(62, 63), (63, 63)]:
        if alpha[y, x]:
            out[y, x] = deep
    return out


def build_translation_candidate(guide: Image.Image, mask_img: Image.Image) -> tuple[Image.Image, dict]:
    guide_rgb = guide.convert("RGB")
    alpha = np.asarray(mask_img, dtype=np.uint8) > 0

    # This is a bounded visual-translation spike, not a production-authority conversion.
    # Native 128x128 is established before palette/cluster decisions; no hidden 3D input is used.
    q = guide_rgb.quantize(colors=24, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    indexed = np.asarray(q, dtype=np.uint8)
    indexed = mode_cleanup(indexed, alpha)

    pal = np.asarray(q.getpalette(), dtype=np.uint8).reshape(-1, 3)
    rgb = pal[indexed]
    rgb = repair_pelvis(rgb, alpha)

    out = np.zeros((128, 128, 4), dtype=np.uint8)
    out[..., :3] = rgb
    out[..., 3] = np.where(alpha, 255, 0).astype(np.uint8)

    visible = out[..., 3] > 0
    colors = np.unique(out[visible, :3], axis=0)
    ys, xs = np.where(visible)
    bbox = [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())]
    meta = {
        "canvas": [128, 128],
        "visible_bbox": bbox,
        "visible_height": bbox[3] - bbox[1] + 1,
        "visible_width": bbox[2] - bbox[0] + 1,
        "opaque_palette_colors": int(len(colors)),
        "binary_alpha": bool(np.all(np.isin(out[..., 3], [0, 255]))),
        "method": "REFERENCE_GUIDED_NATIVE_2D_ABSTRACTION_SPIKE_V3",
        "production_authority": False,
        "warning": "visual candidate only; direct promotion to B3B is forbidden without review and explicit acceptance of the native cluster language",
    }
    return Image.fromarray(out, "RGBA"), meta


def checker(size: tuple[int, int], cell: int = 16) -> Image.Image:
    w, h = size
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    for y in range(h):
        for x in range(w):
            v = 25 if ((x // cell) + (y // cell)) % 2 == 0 else 32
            arr[y, x] = (v, v, v + 3)
    return Image.fromarray(arr, "RGB")


def label(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str) -> None:
    draw.text(xy, text, fill=(235, 235, 235), font=ImageFont.load_default())


def make_contact_sheet(reference: Image.Image, guide: Image.Image, candidate: Image.Image, meta: dict) -> Image.Image:
    sheet = Image.new("RGB", (1280, 720), (15, 15, 18))
    draw = ImageDraw.Draw(sheet)

    ref_panel = reference.crop(THREEQ_BOX).convert("RGB")
    ref_panel.thumbnail((280, 620), Image.Resampling.LANCZOS)
    sheet.paste(ref_panel, (20, 50))
    label(draw, (20, 20), "A  APPROVED BODY REFERENCE - 3/4 CROP (REFERENCE ONLY)")

    guide4 = guide.resize((512, 512), Image.Resampling.NEAREST)
    bg = checker((512, 512), 32).convert("RGBA")
    bg.alpha_composite(guide4)
    sheet.paste(bg.convert("RGB"), (330, 70))
    label(draw, (330, 20), "B  NATIVE 128px GUIDE x4 - NOT FINAL ART")

    cand4 = candidate.resize((384, 384), Image.Resampling.NEAREST)
    bg2 = checker((384, 384), 24).convert("RGBA")
    bg2.alpha_composite(cand4)
    sheet.paste(bg2.convert("RGB"), (870, 70))
    label(draw, (870, 20), "C  V3 PIXEL TRANSLATION CANDIDATE x3")

    gameplay = Image.new("RGB", GAMEPLAY, (22, 22, 25))
    gd = ImageDraw.Draw(gameplay)
    gd.rectangle((0, 245, 639, 359), fill=(34, 31, 29))
    sprite_x = (640 - 128) // 2
    sprite_y = 115
    gp = gameplay.convert("RGBA")
    gp.alpha_composite(candidate, (sprite_x, sprite_y))
    gameplay = gp.convert("RGB")
    gameplay = gameplay.resize((320, 180), Image.Resampling.NEAREST)
    sheet.paste(gameplay, (870, 470))
    label(draw, (870, 450), "D  640x360 GAMEPLAY PREVIEW - SPRITE AT NATIVE 1x")

    silhouette = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    a = np.asarray(candidate)[..., 3] > 0
    s = np.zeros((128, 128, 4), dtype=np.uint8)
    s[a] = (255, 255, 255, 255)
    silhouette = Image.fromarray(s, "RGBA").resize((192, 192), Image.Resampling.NEAREST)
    sbg = Image.new("RGBA", (192, 192), (0, 0, 0, 255))
    sbg.alpha_composite(silhouette)
    sheet.paste(sbg.convert("RGB"), (330, 520))
    label(draw, (530, 530), f"canvas: {meta['canvas']}")
    label(draw, (530, 548), f"bbox: {meta['visible_bbox']}")
    label(draw, (530, 566), f"visible height: {meta['visible_height']} px")
    label(draw, (530, 584), f"palette: {meta['opaque_palette_colors']} opaque colors")
    label(draw, (530, 602), "NO HAIR / CLOTHING / RESTRAINT OWNERSHIP")
    label(draw, (530, 620), "SPIKE ONLY - VISUAL PASS REQUIRED BEFORE PRODUCTION SOURCE")
    return sheet


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--reference", default=None)
    ap.add_argument("--output-dir", required=True)
    args = ap.parse_args()

    outdir = Path(args.output_dir)
    outdir.mkdir(parents=True, exist_ok=True)

    ref_path = find_reference(args.reference)
    got_sha = sha256_file(ref_path)
    reference = Image.open(ref_path).convert("RGB")
    if reference.size != EXPECTED_SIZE:
        raise RuntimeError(f"reference dimensions mismatch: got={reference.size} expected={EXPECTED_SIZE}")

    guide, guide_mask, guide_meta = build_native_guide(reference)
    candidate, cand_meta = build_translation_candidate(guide, guide_mask)
    contact = make_contact_sheet(reference, guide, candidate, cand_meta)

    guide_path = outdir / "g3s_b3b_v3_native_guide.png"
    cand_path = outdir / "g3s_b3b_v3_translation_candidate.png"
    contact_path = outdir / "g3s_b3b_v3_contact_sheet.png"
    result_path = outdir / "g3s_b3b_v3_result.json"

    guide.save(guide_path)
    candidate.save(cand_path)
    contact.save(contact_path)

    result = {
        "gate": "G3S-B3B-V3-REFERENCE-GUIDED-PIXEL-TRANSLATION-SPIKE",
        "status": "REVIEW_REQUIRED_NOT_PRODUCTION_PASS",
        "reference": {
            "path": str(ref_path),
            "sha256": got_sha,
            "dimensions": list(reference.size),
            "approved_reference_marker": "tools/structured-2d-character-pipeline/g3s_b3b_body_reference_approval.json",
        },
        "guide": guide_meta,
        "candidate": cand_meta,
        "ownership": {
            "hidden_3d_used_for_visible_pixels": False,
            "reference_is_final_art_authority": False,
            "candidate_is_production_B3B": False,
            "hair_owned": False,
            "clothing_owned": False,
            "restraint_owned": False,
        },
        "outputs": {
            "guide": str(guide_path),
            "candidate": str(cand_path),
            "contact_sheet": str(contact_path),
        },
        "review_rule": "PASS only if result reads as intentional modern pixel art rather than reduced illustration/filter/mannequin; otherwise close V3 and do not promote.",
    }
    result_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    print(f"REFERENCE: {ref_path}")
    print(f"REFERENCE_SHA256: {got_sha}")
    print(f"GUIDE: {guide_path}")
    print(f"CANDIDATE: {cand_path}")
    print(f"CONTACT_SHEET: {contact_path}")
    print(f"RESULT: {result_path}")
    print("STATUS: REVIEW_REQUIRED_NOT_PRODUCTION_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
