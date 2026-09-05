from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

import g3s_a_authored_native_v1 as v1

SIZE = 128
GAME_W, GAME_H = 640, 360
BG = (18, 18, 22)
REVISION = "G3S_A1_FACIAL_ANATOMY_LOCK_V2"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def region_alpha_count(image: Image.Image, box: list[int]) -> int:
    arr = np.asarray(image.convert("RGBA"), dtype=np.uint8)
    x0, y0, x1, y1 = box
    return int((arr[y0:y1, x0:x1, 3] >= 128).sum())


def mean_rgb(image: Image.Image, points: list[list[int]]) -> np.ndarray:
    values = []
    for x, y in points:
        p = image.getpixel((int(x), int(y)))
        values.append(p[:3])
    return np.asarray(values, dtype=np.float32).mean(axis=0)


def zoom_region(image: Image.Image, box: list[int], scale: int, out_path: Path, title: str) -> Image.Image:
    x0, y0, x1, y1 = box
    crop = image.convert("RGBA").crop((x0, y0, x1, y1))
    zoom = crop.resize((crop.width * scale, crop.height * scale), Image.Resampling.NEAREST)
    canvas = Image.new("RGB", (max(320, zoom.width + 24), max(240, zoom.height + 44)), BG)
    tmp = Image.new("RGBA", canvas.size, (*BG, 255))
    tmp.alpha_composite(zoom, ((canvas.width - zoom.width) // 2, 30))
    canvas = tmp.convert("RGB")
    d = ImageDraw.Draw(canvas)
    d.rectangle([4, 4, canvas.width - 4, 25], fill=(0, 0, 0))
    d.text((10, 9), title, fill=(240, 240, 240), font=ImageFont.load_default())
    canvas.save(out_path)
    return canvas


def extremity_montage(image: Image.Image, regions: dict[str, list[int]], out_path: Path) -> Image.Image:
    names = ["left_hand", "right_hand", "left_foot", "right_foot"]
    cell_w, cell_h = 220, 250
    sheet = Image.new("RGB", (cell_w * 2, cell_h * 2), BG)
    for idx, name in enumerate(names):
        box = regions[name]
        x0, y0, x1, y1 = box
        crop = image.convert("RGBA").crop((x0, y0, x1, y1))
        scale = min((cell_w - 24) // max(1, crop.width), (cell_h - 54) // max(1, crop.height))
        scale = max(1, scale)
        zoom = crop.resize((crop.width * scale, crop.height * scale), Image.Resampling.NEAREST)
        cell = Image.new("RGBA", (cell_w, cell_h), (*BG, 255))
        cell.alpha_composite(zoom, ((cell_w - zoom.width) // 2, 34 + (cell_h - 54 - zoom.height) // 2))
        rgb = cell.convert("RGB")
        d = ImageDraw.Draw(rgb)
        d.rectangle([4, 4, cell_w - 4, 26], fill=(0, 0, 0))
        d.text((10, 9), name.replace("_", " "), fill=(240, 240, 240), font=ImageFont.load_default())
        sheet.paste(rgb, ((idx % 2) * cell_w, (idx // 2) * cell_h))
    sheet.save(out_path)
    return sheet


def fit_panel(image: Image.Image, label: str, size=(640, 360), nearest=False) -> Image.Image:
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
    d.rectangle([4, 4, min(size[0] - 4, 630), 26], fill=(0, 0, 0))
    d.text((10, 9), label, fill=(240, 240, 240), font=ImageFont.load_default())
    return out


def make_contact_sheet(
    control: Image.Image,
    base: Image.Image,
    candidate: Image.Image,
    face_zoom: Image.Image,
    extremities: Image.Image,
    gameplay: Image.Image,
    out_path: Path,
) -> None:
    cells = [
        fit_panel(control, "A Qwen design control - provenance only, NOT final art"),
        fit_panel(base, "B native 128 scaffold before anatomy lock - NOT final art", nearest=True),
        fit_panel(candidate, "C G3S-A1 candidate V2 - native 128 anatomy lock", nearest=True),
        fit_panel(face_zoom, "D FACE DIAGNOSTIC - nearest-neighbor, mouth must read", nearest=True),
        fit_panel(extremities, "E HANDS / FEET DIAGNOSTIC - anatomy review", nearest=True),
        fit_panel(gameplay, "F gameplay preview 640x360 - 1 asset px = 1 screen px", nearest=True),
    ]
    sheet = Image.new("RGB", (1280, 1080), BG)
    positions = [(0, 0), (640, 0), (0, 360), (640, 360), (0, 720), (640, 720)]
    for cell, pos in zip(cells, positions):
        sheet.paste(cell, pos)
    sheet.save(out_path)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--control", required=True)
    ap.add_argument("--patch", required=True)
    ap.add_argument("--output-dir", required=True)
    args = ap.parse_args()

    control_path = Path(args.control)
    patch_path = Path(args.patch)
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    if not control_path.is_file():
        raise FileNotFoundError(control_path)
    if not patch_path.is_file():
        raise FileNotFoundError(patch_path)

    patch = json.loads(patch_path.read_text(encoding="utf-8"))
    if patch.get("revision") != "G3S_A1_FACIAL_ANATOMY_LOCK_PATCH_V2":
        raise RuntimeError(f"Unexpected patch revision: {patch.get('revision')}")

    base, prep = v1.build_scaffold(control_path, patch)
    candidate, patch_counts = v1.apply_patch(base, patch)
    stats = v1.alpha_stats(candidate)

    if candidate.size != (SIZE, SIZE):
        raise RuntimeError(f"Candidate size drift: {candidate.size}")
    if stats["visible_height"] < 118 or stats["visible_height"] > 128:
        raise RuntimeError(f"Candidate visible height out of gate range: {stats}")

    facial = patch["facial_lock"]
    core_points = facial["mouth_core_points"]
    lip_points = facial["lower_lip_points"]
    skin_points = [[58,18],[59,18],[60,18],[61,18],[58,19],[59,19],[60,19],[61,19]]
    mouth_mean = mean_rgb(candidate, core_points)
    skin_mean = mean_rgb(candidate, skin_points)
    mouth_contrast = float(np.linalg.norm(mouth_mean - skin_mean))
    required_contrast = float(facial["minimum_mouth_local_rgb_contrast"])
    if mouth_contrast < required_contrast:
        raise RuntimeError(
            f"Facial lock failed: mouth local RGB contrast {mouth_contrast:.2f} < {required_contrast:.2f}"
        )

    core_colors = {candidate.getpixel(tuple(p)) for p in core_points}
    lip_colors = {candidate.getpixel(tuple(p)) for p in lip_points}
    if not core_colors or not lip_colors or core_colors == lip_colors:
        raise RuntimeError("Facial lock failed: mouth does not occupy two semantically distinct rows")

    regions = patch["diagnostic_regions"]
    region_counts = {name: region_alpha_count(candidate, box) for name, box in regions.items()}
    if region_counts["face"] < 30:
        raise RuntimeError(f"Face region unexpectedly sparse: {region_counts}")
    for name in ("left_hand", "right_hand"):
        if region_counts[name] < 5:
            raise RuntimeError(f"Hand anatomy region unexpectedly sparse: {name}={region_counts[name]}")
    for name in ("left_foot", "right_foot"):
        if region_counts[name] < 10:
            raise RuntimeError(f"Foot anatomy region unexpectedly sparse: {name}={region_counts[name]}")

    base_path = out / "g3s_a1_base128.png"
    candidate_path = out / "g3s_a1_candidate_v2.png"
    face_path = out / "g3s_a1_face_zoom.png"
    extremities_path = out / "g3s_a1_extremities_zoom.png"
    gameplay_path = out / "g3s_a1_gameplay_preview.png"
    sheet_path = out / "g3s_a1_contact_sheet.png"
    result_path = out / "g3s_a1_result.json"

    base.save(base_path)
    candidate.save(candidate_path)
    face_zoom = zoom_region(candidate, regions["face"], 18, face_path, "FACE 18x nearest - judge mouth / nose / jaw")
    extremities = extremity_montage(candidate, regions, extremities_path)
    gameplay = v1.gameplay_preview(candidate, gameplay_path)
    control = Image.open(control_path).convert("RGBA")
    make_contact_sheet(control, base, candidate, face_zoom, extremities, gameplay, sheet_path)

    result = {
        "gate": "G3S-A1-FACIAL-ANATOMY-LOCK",
        "status": "REVIEW_REQUIRED",
        "revision": REVISION,
        "control": str(control_path),
        "control_sha256": sha256(control_path),
        "patch": str(patch_path),
        "patch_sha256": sha256(patch_path),
        "candidate": str(candidate_path),
        "candidate_sha256": sha256(candidate_path),
        "contact_sheet": str(sheet_path),
        "face_zoom": str(face_path),
        "extremities_zoom": str(extremities_path),
        "gameplay_preview": str(gameplay_path),
        "prep": prep,
        "patch_counts": patch_counts,
        "candidate_stats": stats,
        "anatomy_audit": {
            "mouth_local_rgb_contrast": round(mouth_contrast, 4),
            "mouth_required_contrast": required_contrast,
            "mouth_two_rows": True,
            "region_alpha_pixels": region_counts,
            "technical_audit": "PASS",
            "visual_review_at_1x": "REQUIRED"
        },
        "rules": {
            "anatomical_detail_is_gate_critical": True,
            "alpha_presence_alone_is_not_feature_readability": True,
            "native_canvas": [128,128],
            "candidate_post_resize": False,
            "no_model_search": True,
            "no_animation_before_static_anatomy_pass": True
        }
    }
    result_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    print(f"G3S_A1_REVISION={REVISION}")
    print("G3S_A1_V1_FAILURE=ACKNOWLEDGED")
    print("G3S_A1_MOUTH_GUARD=SEMANTIC_TWO_ROW_CONTRAST")
    print(f"G3S_A1_MOUTH_CONTRAST={mouth_contrast:.4f}")
    print(f"G3S_A1_REGION_ALPHA={json.dumps(region_counts, separators=(',', ':'))}")
    print("G3S_A1_TECHNICAL_ANATOMY_AUDIT=PASS")
    print(f"G3S_A1_CANDIDATE={candidate_path}")
    print(f"G3S_A1_CONTACT={sheet_path}")


if __name__ == "__main__":
    main()
