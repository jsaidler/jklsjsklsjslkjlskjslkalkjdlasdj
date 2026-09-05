from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

SIZE = 128
GAME_W, GAME_H = 640, 360
BG = (18, 18, 22)
REVISION = "G3S_A_AUTHORED_NATIVE_V1"


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


def build_scaffold(control_path: Path, patch: dict) -> tuple[Image.Image, dict]:
    expected = patch["provenance"]
    if sha256(control_path) != expected["control_sha256"]:
        raise RuntimeError("Qwen control SHA256 mismatch; authored coordinates are pinned to a different source")

    src = Image.open(control_path).convert("RGB")
    if list(src.size) != expected["control_size"]:
        raise RuntimeError(f"Qwen control size mismatch: got={list(src.size)} expected={expected['control_size']}")

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
    if bb != expected["subject_bbox"]:
        raise RuntimeError(f"Subject bbox drift: got={bb} expected={expected['subject_bbox']}")

    x0, y0, x1, y1 = bb
    crop_rgb = arr[y0 : y1 + 1, x0 : x1 + 1].astype(np.uint8)
    crop_mask = mask[y0 : y1 + 1, x0 : x1 + 1]
    rgba = np.zeros((crop_rgb.shape[0], crop_rgb.shape[1], 4), dtype=np.uint8)
    rgba[:, :, :3] = crop_rgb
    rgba[:, :, 3] = np.where(crop_mask, 255, 0).astype(np.uint8)
    crop = Image.fromarray(rgba, "RGBA")

    target_w, target_h = expected["subject_size"]
    resized = crop.resize((target_w, target_h), Image.Resampling.NEAREST)
    canvas = Image.new("RGBA", tuple(expected["native_canvas"]), (0, 0, 0, 0))
    xy = tuple(expected["subject_xy"])
    canvas.alpha_composite(resized, xy)

    return canvas, {
        "background_rgb": [round(float(v), 4) for v in bg.tolist()],
        "subject_bbox": bb,
        "subject_size": [target_w, target_h],
        "subject_xy": list(xy),
    }


def apply_patch(base: Image.Image, patch: dict) -> tuple[Image.Image, dict]:
    out = base.copy().convert("RGBA")
    px = out.load()
    colors = {k: tuple(v) for k, v in patch["colors"].items()}
    counts: dict[str, int] = {}

    def set_pixel(x: int, y: int, color_name: str, only_if_opaque: bool = False):
        if not (0 <= x < out.width and 0 <= y < out.height):
            raise RuntimeError(f"Patch pixel out of bounds: {(x, y)}")
        if only_if_opaque and px[x, y][3] < 128:
            return False
        px[x, y] = colors[color_name]
        return True

    for op in patch["operations"]:
        kind = op["op"]
        color_name = op["color"]
        if color_name not in colors:
            raise RuntimeError(f"Unknown patch color: {color_name}")
        applied = 0
        only_if_opaque = bool(op.get("only_if_opaque", False))

        if kind == "pixel":
            applied += int(set_pixel(int(op["x"]), int(op["y"]), color_name, only_if_opaque))
        elif kind == "hline":
            x0, x1, y = int(op["x0"]), int(op["x1"]), int(op["y"])
            if x1 < x0:
                raise RuntimeError(f"Invalid hline: {op}")
            for x in range(x0, x1 + 1):
                applied += int(set_pixel(x, y, color_name, only_if_opaque))
        elif kind == "pixels":
            for x, y in op["points"]:
                applied += int(set_pixel(int(x), int(y), color_name, only_if_opaque))
        else:
            raise RuntimeError(f"Unsupported patch operation: {kind}")

        key = op.get("semantic", kind)
        counts[key] = counts.get(key, 0) + applied

    return out, counts


def alpha_stats(image: Image.Image) -> dict:
    rgba = np.asarray(image.convert("RGBA"), dtype=np.uint8)
    mask = rgba[:, :, 3] >= 128
    bb = bbox_from_mask(mask)
    opaque = rgba[mask, :3]
    unique = len(np.unique(opaque, axis=0)) if len(opaque) else 0
    return {
        "alpha_pixels": int(mask.sum()),
        "alpha_bbox": bb,
        "visible_height": 0 if bb is None else int(bb[3] - bb[1] + 1),
        "visible_width": 0 if bb is None else int(bb[2] - bb[0] + 1),
        "unique_opaque_rgb": int(unique),
    }


def gameplay_preview(sprite: Image.Image, out_path: Path) -> Image.Image:
    bg = Image.new("RGBA", (GAME_W, GAME_H), (*BG, 255))
    x = (GAME_W - sprite.width) // 2
    y = (GAME_H - sprite.height) // 2
    bg.alpha_composite(sprite.convert("RGBA"), (x, y))
    rgb = bg.convert("RGB")
    rgb.save(out_path)
    return rgb


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
    d.rectangle([4, 4, min(size[0] - 4, 625), 26], fill=(0, 0, 0))
    d.text((10, 9), label, fill=(240, 240, 240), font=ImageFont.load_default())
    return out


def contact_sheet(control: Image.Image, base: Image.Image, candidate: Image.Image, gameplay: Image.Image, out_path: Path) -> None:
    cells = [
        panel(control, "A Qwen design control - scaffold provenance only, NOT final art"),
        panel(base, "B native 128 scaffold before authored corrections - NOT final art", nearest=True),
        panel(candidate, "C authored native 128 candidate v1 - deterministic pixel patch", nearest=True),
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
    if patch.get("revision") != "G3S_A_AUTHORED_NATIVE_PATCH_V1":
        raise RuntimeError(f"Unexpected patch revision: {patch.get('revision')}")

    base, prep = build_scaffold(control_path, patch)
    candidate, patch_counts = apply_patch(base, patch)

    base_path = out / "g3s_a_authored_base128.png"
    candidate_path = out / "g3s_a_authored_candidate_v1.png"
    preview_path = out / "g3s_a_authored_gameplay_preview.png"
    sheet_path = out / "g3s_a_authored_contact_sheet.png"
    result_path = out / "g3s_a_authored_result.json"

    base.save(base_path)
    candidate.save(candidate_path)
    gameplay = gameplay_preview(candidate, preview_path)
    control = Image.open(control_path).convert("RGBA")
    contact_sheet(control, base, candidate, gameplay, sheet_path)

    stats = alpha_stats(candidate)
    if stats["visible_height"] < 118 or stats["visible_height"] > 128:
        raise RuntimeError(f"Authored candidate visible height out of gate range: {stats}")
    if stats["alpha_pixels"] < 800:
        raise RuntimeError(f"Authored candidate unexpectedly sparse: {stats}")

    # Explicit native feature guards for the user-observed mouth loss and the canonical restraints.
    mouth = [candidate.getpixel((x, 20)) for x in range(58, 62)]
    if all(px[3] < 128 for px in mouth):
        raise RuntimeError("Authored mouth guard failed: mouth pixels are transparent")
    for xy in [(44, 62), (79, 62), (75, 115)]:
        if candidate.getpixel(xy)[3] < 128:
            raise RuntimeError(f"Authored restraint guard failed at {xy}")

    result = {
        "gate": "G3S-A-AUTHORED-NATIVE",
        "status": "REVIEW_REQUIRED",
        "revision": REVISION,
        "method": "Qwen design scaffold -> explicit deterministic native-grid authoring patch",
        "control": str(control_path),
        "control_sha256": sha256(control_path),
        "patch": str(patch_path),
        "patch_sha256": sha256(patch_path),
        "scaffold": str(base_path),
        "scaffold_sha256": sha256(base_path),
        "candidate": str(candidate_path),
        "candidate_sha256": sha256(candidate_path),
        "gameplay_preview": str(preview_path),
        "contact_sheet": str(sheet_path),
        "prep": prep,
        "patch_counts": patch_counts,
        "candidate_stats": stats,
        "rules": {
            "native_canvas": [128, 128],
            "candidate_post_generation_resize": False,
            "qwen_is_animation_owner": False,
            "qwen_scaffold_is_final_art": False,
            "future_refinement_edits_patch_data_not_model_parameters": True,
            "visual_review_required": True,
        },
    }
    result_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    print(f"G3S_A_AUTHORED_REVISION={REVISION}")
    print("G3S_A_AUTHORED_MODEL_SEARCH=CLOSED")
    print("G3S_A_AUTHORED_NATIVE_PATCH=PASS")
    print(f"G3S_A_AUTHORED_CANDIDATE={candidate_path}")
    print(f"G3S_A_AUTHORED_CONTACT={sheet_path}")
    print(f"G3S_A_AUTHORED_STATS={json.dumps(stats, separators=(',', ':'))}")


if __name__ == "__main__":
    main()
