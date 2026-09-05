from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

SIZE = 128
BG = (18, 18, 22)
REVISION = "G3S_B_PERSISTENT_PART_DECOMPOSITION_V1"


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


def build_scaffold(control_path: Path, source: dict) -> tuple[Image.Image, dict]:
    got_sha = sha256(control_path)
    if got_sha != source["control_sha256"]:
        raise RuntimeError(f"Qwen control SHA mismatch: got={got_sha} expected={source['control_sha256']}")
    src = Image.open(control_path).convert("RGB")
    if list(src.size) != source["control_size"]:
        raise RuntimeError(f"Qwen control size mismatch: got={list(src.size)} expected={source['control_size']}")

    arr = np.asarray(src, dtype=np.float32)
    h, w = arr.shape[:2]
    corner = max(8, min(w, h) // 24)
    samples = np.concatenate([
        arr[:corner, :corner].reshape(-1, 3),
        arr[:corner, -corner:].reshape(-1, 3),
        arr[-corner:, :corner].reshape(-1, 3),
        arr[-corner:, -corner:].reshape(-1, 3),
    ], axis=0)
    bg = np.median(samples, axis=0)
    dist = np.sqrt(np.sum((arr - bg[None, None, :]) ** 2, axis=2))
    mask = dist > 12.0
    bb = bbox_from_mask(mask)
    if bb != source["subject_bbox"]:
        raise RuntimeError(f"Subject bbox drift: got={bb} expected={source['subject_bbox']}")

    x0, y0, x1, y1 = bb
    crop_rgb = arr[y0:y1 + 1, x0:x1 + 1].astype(np.uint8)
    crop_mask = mask[y0:y1 + 1, x0:x1 + 1]
    rgba = np.zeros((crop_rgb.shape[0], crop_rgb.shape[1], 4), dtype=np.uint8)
    rgba[:, :, :3] = crop_rgb
    rgba[:, :, 3] = np.where(crop_mask, 255, 0).astype(np.uint8)
    crop = Image.fromarray(rgba, "RGBA")

    target_w, target_h = source["subject_size"]
    resized = crop.resize((target_w, target_h), Image.Resampling.NEAREST)
    canvas = Image.new("RGBA", tuple(source["native_canvas"]), (0, 0, 0, 0))
    xy = tuple(source["subject_xy"])
    canvas.alpha_composite(resized, xy)
    return canvas, {
        "background_rgb": [round(float(v), 4) for v in bg.tolist()],
        "subject_bbox": bb,
        "subject_size": [target_w, target_h],
        "subject_xy": list(xy),
    }


def polygon_mask(part: dict) -> np.ndarray:
    m = Image.new("L", (SIZE, SIZE), 0)
    d = ImageDraw.Draw(m)
    for poly in part["polygons"]:
        d.polygon([(int(x), int(y)) for x, y in poly], fill=255)
    return np.asarray(m, dtype=np.uint8) >= 128


def selector_mask(source_rgba: np.ndarray, selector: dict) -> np.ndarray:
    mode = selector.get("mode", "all")
    alpha = source_rgba[:, :, 3] >= 128
    if mode == "all":
        return alpha
    if mode == "dark_luma":
        rgb = source_rgba[:, :, :3].astype(np.float32)
        luma = rgb[:, :, 0] * 0.2126 + rgb[:, :, 1] * 0.7152 + rgb[:, :, 2] * 0.0722
        return alpha & (luma <= float(selector["max_luma"]))
    raise RuntimeError(f"Unknown selector mode: {mode}")


def extract_part(source: Image.Image, part: dict) -> tuple[Image.Image, dict]:
    rgba = np.asarray(source.convert("RGBA"), dtype=np.uint8)
    keep = polygon_mask(part) & selector_mask(rgba, part["selector"])
    count = int(keep.sum())
    if count < int(part["min_alpha_pixels"]):
        raise RuntimeError(f"Part {part['id']} unexpectedly sparse: alpha_pixels={count} min={part['min_alpha_pixels']}")
    full = np.zeros_like(rgba)
    full[keep] = rgba[keep]
    bb = bbox_from_mask(keep)
    assert bb is not None
    x0, y0, x1, y1 = bb
    crop = Image.fromarray(full[y0:y1 + 1, x0:x1 + 1], "RGBA")
    pivot_canvas = [int(part["pivot"][0]), int(part["pivot"][1])]
    pivot_local = [pivot_canvas[0] - x0, pivot_canvas[1] - y0]
    return crop, {
        "id": part["id"],
        "label": part["label"],
        "role": part["role"],
        "screen_side": part["screen_side"],
        "anatomical_side": part["anatomical_side"],
        "depth": int(part["depth"]),
        "alpha_pixels": count,
        "canvas_bbox": bb,
        "pivot_canvas": pivot_canvas,
        "pivot_local": pivot_local,
    }


def full_canvas_from_crop(crop: Image.Image, bbox: list[int]) -> Image.Image:
    out = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    out.alpha_composite(crop, (bbox[0], bbox[1]))
    return out


def overlay_parts(source: Image.Image, records: list[dict], crops: dict[str, Image.Image]) -> Image.Image:
    colors = [
        (235, 80, 80, 150), (80, 180, 255, 150), (120, 220, 120, 150), (240, 180, 70, 150),
        (190, 100, 240, 150), (80, 230, 210, 150), (245, 120, 180, 150), (180, 180, 80, 150),
    ]
    canvas = source.convert("RGBA")
    tint = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    for i, rec in enumerate(records):
        full = full_canvas_from_crop(crops[rec["id"]], rec["canvas_bbox"])
        a = np.asarray(full, dtype=np.uint8)[:, :, 3]
        layer = np.zeros((SIZE, SIZE, 4), dtype=np.uint8)
        color = colors[i % len(colors)]
        layer[:, :, 0] = color[0]
        layer[:, :, 1] = color[1]
        layer[:, :, 2] = color[2]
        layer[:, :, 3] = np.where(a >= 128, color[3], 0).astype(np.uint8)
        tint = Image.alpha_composite(tint, Image.fromarray(layer, "RGBA"))
    return Image.alpha_composite(canvas, tint)


def recompose(source: Image.Image, records: list[dict], crops: dict[str, Image.Image]) -> tuple[Image.Image, dict]:
    out = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    coverage = np.zeros((SIZE, SIZE), dtype=bool)
    for rec in sorted(records, key=lambda r: r["depth"]):
        crop = crops[rec["id"]]
        out.alpha_composite(crop, (rec["canvas_bbox"][0], rec["canvas_bbox"][1]))
        full = full_canvas_from_crop(crop, rec["canvas_bbox"])
        coverage |= np.asarray(full, dtype=np.uint8)[:, :, 3] >= 128

    src_rgba = np.asarray(source.convert("RGBA"), dtype=np.uint8)
    src_alpha = src_rgba[:, :, 3] >= 128
    residual = src_alpha & ~coverage
    residual_count = int(residual.sum())

    if residual_count:
        residual_rgba = np.zeros_like(src_rgba)
        residual_rgba[residual] = src_rgba[residual]
        out = Image.alpha_composite(out, Image.fromarray(residual_rgba, "RGBA"))

    out_arr = np.asarray(out.convert("RGBA"), dtype=np.uint8)
    diff = np.abs(out_arr.astype(np.int16) - src_rgba.astype(np.int16))
    exact = bool(np.max(diff) == 0)
    return out, {
        "source_alpha_pixels": int(src_alpha.sum()),
        "covered_by_named_parts": int((src_alpha & coverage).sum()),
        "residual_pixels": residual_count,
        "residual_fraction": 0.0 if int(src_alpha.sum()) == 0 else round(residual_count / int(src_alpha.sum()), 6),
        "exact_recomposition": exact,
        "max_channel_diff": int(np.max(diff)),
    }


def draw_pivots(source: Image.Image, records: list[dict], accessories: list[dict]) -> Image.Image:
    out = source.convert("RGBA").copy()
    d = ImageDraw.Draw(out)
    for rec in records:
        x, y = rec["pivot_canvas"]
        d.line((x - 2, y, x + 2, y), fill=(255, 220, 40, 255), width=1)
        d.line((x, y - 2, x, y + 2), fill=(255, 220, 40, 255), width=1)
    for acc in accessories:
        x, y = acc["socket_canvas"]
        d.rectangle((x - 1, y - 1, x + 1, y + 1), outline=(80, 220, 255, 255))
    return out


def nearest_panel(image: Image.Image, label: str, size=(640, 360)) -> Image.Image:
    im = image.convert("RGBA")
    max_w, max_h = size[0] - 32, size[1] - 50
    scale = max(1, int(min(max_w / im.width, max_h / im.height)))
    zoom = im.resize((im.width * scale, im.height * scale), Image.Resampling.NEAREST)
    tmp = Image.new("RGBA", size, (*BG, 255))
    tmp.alpha_composite(zoom, ((size[0] - zoom.width) // 2, 30 + (max_h - zoom.height) // 2))
    rgb = tmp.convert("RGB")
    d = ImageDraw.Draw(rgb)
    d.rectangle([4, 4, min(size[0] - 4, 630), 26], fill=(0, 0, 0))
    d.text((10, 9), label, fill=(240, 240, 240), font=ImageFont.load_default())
    return rgb


def parts_atlas(records: list[dict], crops: dict[str, Image.Image], out_path: Path) -> Image.Image:
    cols, rows = 4, 5
    cell_w, cell_h = 240, 210
    atlas = Image.new("RGB", (cols * cell_w, rows * cell_h), BG)
    for i, rec in enumerate(records[:cols * rows]):
        crop = crops[rec["id"]].convert("RGBA")
        max_w, max_h = cell_w - 24, cell_h - 48
        scale = max(1, int(min(max_w / crop.width, max_h / crop.height)))
        zoom = crop.resize((crop.width * scale, crop.height * scale), Image.Resampling.NEAREST)
        cell = Image.new("RGBA", (cell_w, cell_h), (*BG, 255))
        cell.alpha_composite(zoom, ((cell_w - zoom.width) // 2, 30 + (max_h - zoom.height) // 2))
        rgb = cell.convert("RGB")
        d = ImageDraw.Draw(rgb)
        d.rectangle([3, 3, cell_w - 3, 25], fill=(0, 0, 0))
        d.text((8, 8), rec["id"], fill=(240, 240, 240), font=ImageFont.load_default())
        atlas.paste(rgb, ((i % cols) * cell_w, (i // cols) * cell_h))
    atlas.save(out_path)
    return atlas


def contact_sheet(source: Image.Image, recomposed: Image.Image, overlay: Image.Image, pivot_view: Image.Image, atlas: Image.Image, out_path: Path) -> None:
    cells = [
        nearest_panel(source, "A provisional native scaffold - decomposition source"),
        nearest_panel(recomposed, "B recomposed from persistent parts + residual audit"),
        nearest_panel(overlay, "C part coverage overlay - visual mask review"),
        nearest_panel(pivot_view, "D pivots + initial chain sockets; chains are NOT body pixels"),
    ]
    sheet = Image.new("RGB", (1280, 1080), BG)
    sheet.paste(cells[0], (0, 0))
    sheet.paste(cells[1], (640, 0))
    sheet.paste(cells[2], (0, 360))
    sheet.paste(cells[3], (640, 360))
    atlas_fit = atlas.copy()
    atlas_fit.thumbnail((1240, 330), Image.Resampling.NEAREST)
    sheet.paste(atlas_fit, ((1280 - atlas_fit.width) // 2, 730))
    d = ImageDraw.Draw(sheet)
    d.rectangle([4, 704, 1276, 728], fill=(0, 0, 0))
    d.text((10, 710), "E persistent part atlas - head/face remains replaceable; screen-side mapping resolves to anatomy in G3S-C", fill=(240,240,240), font=ImageFont.load_default())
    sheet.save(out_path)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--control", required=True)
    ap.add_argument("--spec", required=True)
    ap.add_argument("--output-dir", required=True)
    args = ap.parse_args()

    control_path = Path(args.control)
    spec_path = Path(args.spec)
    out_dir = Path(args.output_dir)
    parts_dir = out_dir / "parts"
    out_dir.mkdir(parents=True, exist_ok=True)
    parts_dir.mkdir(parents=True, exist_ok=True)

    if not control_path.is_file():
        raise FileNotFoundError(control_path)
    if not spec_path.is_file():
        raise FileNotFoundError(spec_path)

    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    if spec.get("revision") != "G3S_B_PARTS_SPEC_V1":
        raise RuntimeError(f"Unexpected spec revision: {spec.get('revision')}")

    source, prep = build_scaffold(control_path, spec["source"])
    source_path = out_dir / "g3s_b_source128.png"
    source.save(source_path)

    crops: dict[str, Image.Image] = {}
    records: list[dict] = []
    for part in spec["parts"]:
        crop, rec = extract_part(source, part)
        path = parts_dir / f"{part['id']}.png"
        crop.save(path)
        rec["file"] = str(path)
        rec["sha256"] = sha256(path)
        records.append(rec)
        crops[part["id"]] = crop

    recomposed, audit = recompose(source, records, crops)
    if not audit["exact_recomposition"]:
        raise RuntimeError(f"Recomposition is not pixel-exact: {audit}")
    recomposed_path = out_dir / "g3s_b_recomposed.png"
    recomposed.save(recomposed_path)

    overlay = overlay_parts(source, records, crops)
    overlay_path = out_dir / "g3s_b_part_overlay.png"
    overlay.save(overlay_path)

    pivot_view = draw_pivots(source, records, spec["initial_accessories"])
    pivot_path = out_dir / "g3s_b_pivots_and_sockets.png"
    pivot_view.save(pivot_path)

    atlas_path = out_dir / "g3s_b_parts_atlas.png"
    atlas = parts_atlas(records, crops, atlas_path)

    sheet_path = out_dir / "g3s_b_contact_sheet.png"
    contact_sheet(source, recomposed, overlay, pivot_view, atlas, sheet_path)

    manifest_path = out_dir / "g3s_b_runtime_manifest.json"
    result_path = out_dir / "g3s_b_result.json"
    manifest = {
        "revision": REVISION,
        "source": str(source_path),
        "source_sha256": sha256(source_path),
        "parts": records,
        "initial_accessories": spec["initial_accessories"],
        "source_status": spec["source_status"],
        "rules": spec["rules"],
    }
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    result = {
        "gate": "G3S-B-PERSISTENT-PART-DECOMPOSITION",
        "status": "REVIEW_REQUIRED",
        "revision": REVISION,
        "control": str(control_path),
        "control_sha256": sha256(control_path),
        "spec": str(spec_path),
        "spec_sha256": sha256(spec_path),
        "source": str(source_path),
        "source_sha256": sha256(source_path),
        "runtime_manifest": str(manifest_path),
        "contact_sheet": str(sheet_path),
        "parts_atlas": str(atlas_path),
        "recomposition_audit": audit,
        "prep": prep,
        "part_count": len(records),
        "head_face_status": "UNRESOLVED_REPLACEABLE_PART",
        "chains": "SEPARATE_INITIAL_ACCESSORY_SLOTS_NOT_BAKED_INTO_BODY_PATCH",
        "technical_audit": "PASS",
        "visual_review": "REQUIRED"
    }
    result_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    print(f"G3S_B_REVISION={REVISION}")
    print(f"G3S_B_PART_COUNT={len(records)}")
    print(f"G3S_B_RESIDUAL_PIXELS={audit['residual_pixels']}")
    print(f"G3S_B_RESIDUAL_FRACTION={audit['residual_fraction']}")
    print("G3S_B_RECOMPOSITION=PIXEL_EXACT_PASS")
    print("G3S_B_HEAD_FACE=UNRESOLVED_REPLACEABLE_PART")
    print("G3S_B_CHAINS=SEPARATE_INITIAL_ACCESSORY_SLOTS")
    print(f"G3S_B_CONTACT={sheet_path}")
    print(f"G3S_B_MANIFEST={manifest_path}")


if __name__ == "__main__":
    main()
