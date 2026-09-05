from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

SIZE = 128
BG = (18, 18, 22)
REVISION = "G3S_B2_LAYER_STACK_PREFLIGHT_V1"


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
    got = sha256(control_path)
    if got != source["control_sha256"]:
        raise RuntimeError(f"Qwen control SHA mismatch: got={got} expected={source['control_sha256']}")
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
    crop = crop.resize((target_w, target_h), Image.Resampling.NEAREST)
    canvas = Image.new("RGBA", tuple(source["native_canvas"]), (0, 0, 0, 0))
    canvas.alpha_composite(crop, tuple(source["subject_xy"]))
    return canvas, {"background_rgb": [round(float(v), 4) for v in bg.tolist()], "subject_bbox": bb}


def polygon_mask(polygons: list, size=(SIZE, SIZE)) -> np.ndarray:
    im = Image.new("L", size, 0)
    d = ImageDraw.Draw(im)
    for poly in polygons:
        d.polygon([(int(x), int(y)) for x, y in poly], fill=255)
    return np.asarray(im, dtype=np.uint8) >= 128


def collect_seed_pixels(rgba: np.ndarray, boxes: list[list[int]]) -> np.ndarray:
    out = []
    for x0, y0, x1, y1 in boxes:
        crop = rgba[y0:y1, x0:x1]
        m = crop[:, :, 3] >= 128
        if m.any():
            out.append(crop[m, :3].astype(np.float32))
    if not out:
        raise RuntimeError("Seed boxes produced no opaque pixels")
    return np.concatenate(out, axis=0)


def shade_centroids(pixels: np.ndarray, k: int) -> np.ndarray:
    luma = pixels[:, 0] * 0.2126 + pixels[:, 1] * 0.7152 + pixels[:, 2] * 0.0722
    order = np.argsort(luma)
    chunks = np.array_split(pixels[order], min(k, len(pixels)))
    centers = [c.mean(axis=0) for c in chunks if len(c)]
    return np.stack(centers, axis=0)


def classify_materials(image: Image.Image, spec: dict):
    rgba = np.asarray(image.convert("RGBA"), dtype=np.uint8)
    opaque = rgba[:, :, 3] >= 128
    rgb = rgba[:, :, :3].astype(np.float32)

    names = ["skin", "hair", "cloth"]
    centroids = {}
    for name in names:
        seeds = collect_seed_pixels(rgba, spec["seed_boxes"][name])
        centroids[name] = shade_centroids(seeds, int(spec["class_centroids_per_material"]))

    distances = []
    for name in names:
        c = centroids[name]
        diff = rgb[:, :, None, :] - c[None, None, :, :]
        distances.append(np.sqrt(np.sum(diff * diff, axis=3)).min(axis=2))
    stack = np.stack(distances, axis=2)
    cls = np.argmin(stack, axis=2)

    hair_allowed = polygon_mask(spec["allowed_regions"]["hair"])
    cloth_allowed = polygon_mask(spec["allowed_regions"]["cloth"])
    hair = opaque & hair_allowed & (cls == names.index("hair"))
    cloth = opaque & cloth_allowed & (cls == names.index("cloth")) & ~hair

    # The remaining visible composite pixels are treated as currently visible body/residual anatomy.
    # This is deliberately NOT claimed to be the complete body base.
    body_visible = opaque & ~hair & ~cloth
    return rgba, opaque, body_visible, hair, cloth, {k: np.round(v, 2).tolist() for k, v in centroids.items()}


def layer_image(rgba: np.ndarray, mask: np.ndarray) -> Image.Image:
    out = np.zeros_like(rgba)
    out[mask] = rgba[mask]
    return Image.fromarray(out, "RGBA")


def compose_layers(layers: list[Image.Image]) -> Image.Image:
    out = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    for layer in layers:
        out.alpha_composite(layer)
    return out


def pixel_diff(a: Image.Image, b: Image.Image) -> int:
    aa = np.asarray(a.convert("RGBA"), dtype=np.int16)
    bb = np.asarray(b.convert("RGBA"), dtype=np.int16)
    return int(np.abs(aa - bb).max())


def panel(image: Image.Image, label: str, size=(640, 360), nearest=True) -> Image.Image:
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
    d.rectangle([4, 4, min(size[0] - 4, 632), 26], fill=(0, 0, 0))
    d.text((10, 9), label, fill=(240, 240, 240), font=ImageFont.load_default())
    return out


def unresolved_preview(source: Image.Image, unresolved: np.ndarray) -> Image.Image:
    base = source.convert("RGBA")
    overlay = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    arr = np.zeros((SIZE, SIZE, 4), dtype=np.uint8)
    arr[unresolved] = np.array([255, 0, 180, 230], dtype=np.uint8)
    overlay = Image.fromarray(arr, "RGBA")
    base.alpha_composite(overlay)
    return base


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--control", required=True)
    ap.add_argument("--spec", required=True)
    ap.add_argument("--output-dir", required=True)
    args = ap.parse_args()

    control = Path(args.control)
    spec_path = Path(args.spec)
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    if not control.is_file():
        raise FileNotFoundError(control)
    if not spec_path.is_file():
        raise FileNotFoundError(spec_path)

    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    if spec.get("revision") != "G3S_B2_LAYER_STACK_PREFLIGHT_SPEC_V1":
        raise RuntimeError(f"Unexpected spec revision: {spec.get('revision')}")

    source, prep = build_scaffold(control, spec["source"])
    rgba, opaque, body_visible_mask, hair_mask, cloth_mask, centroids = classify_materials(source, spec)

    body_visible = layer_image(rgba, body_visible_mask)
    hair = layer_image(rgba, hair_mask)
    clothing = layer_image(rgba, cloth_mask)
    recomposed = compose_layers([body_visible, hair, clothing])
    max_diff = pixel_diff(source, recomposed)
    if max_diff != 0:
        raise RuntimeError(f"Layer partition failed exact recomposition: max_channel_diff={max_diff}")

    expected_body = polygon_mask(spec["expected_body_regions"])
    unresolved = expected_body & (hair_mask | cloth_mask)
    unresolved_count = int(unresolved.sum())
    if unresolved_count < 50:
        raise RuntimeError(f"Unexpectedly small hidden-body requirement: {unresolved_count} pixels")

    paths = {
        "source": out / "g3s_b2_source128.png",
        "body_visible": out / "g3s_b2_body_visible_incomplete.png",
        "hair": out / "g3s_b2_hair_layer.png",
        "clothing": out / "g3s_b2_clothing_layer.png",
        "recomposed": out / "g3s_b2_recomposed.png",
        "unresolved": out / "g3s_b2_unresolved_underbody.png",
        "contact": out / "g3s_b2_contact_sheet.png",
        "manifest": out / "g3s_b2_layer_manifest.json",
        "result": out / "g3s_b2_result.json",
    }
    source.save(paths["source"])
    body_visible.save(paths["body_visible"])
    hair.save(paths["hair"])
    clothing.save(paths["clothing"])
    recomposed.save(paths["recomposed"])
    unresolved_img = unresolved_preview(source, unresolved)
    unresolved_img.save(paths["unresolved"])

    cells = [
        panel(source, "A provisional composite source - clothing/hair currently baked in"),
        panel(body_visible, "B visible body pixels only - INCOMPLETE under occluders"),
        panel(hair, "C hair-only persistent layer family - separate from body"),
        panel(clothing, "D clothing-only overlay family - separate/removable"),
        panel(recomposed, "E exact recomposition from body-visible + hair + clothing"),
        panel(unresolved_img, "F MAGENTA = body pixels still required under hair/clothing"),
    ]
    sheet = Image.new("RGB", (1280, 1080), BG)
    for cell, pos in zip(cells, [(0,0),(640,0),(0,360),(640,360),(0,720),(640,720)]):
        sheet.paste(cell, pos)
    sheet.save(paths["contact"])

    manifest = {
        "revision": REVISION,
        "source": str(paths["source"]),
        "source_sha256": sha256(paths["source"]),
        "layers": {
            "body_visible_incomplete": {"file": str(paths["body_visible"]), "alpha_pixels": int(body_visible_mask.sum()), "complete_body_base": False},
            "hair": {"file": str(paths["hair"]), "alpha_pixels": int(hair_mask.sum()), "owner": "SEPARATE_PERSISTENT_SECONDARY_LAYER_FAMILY"},
            "clothing": {"file": str(paths["clothing"]), "alpha_pixels": int(cloth_mask.sum()), "owner": "SEPARATE_OVERLAY_LAYER_FAMILY"},
        },
        "hidden_body_requirement": {
            "mask_file": str(paths["unresolved"]),
            "pixels": unresolved_count,
            "status": "UNRESOLVED_BODY_BASE_COMPLETION_REQUIRED"
        },
        "layer_contract": spec["layer_contract"],
        "material_centroids_rgb": centroids,
        "next_gate": "G3S-B3-BODY-BASE-COMPLETION",
        "animation_blocked": True,
    }
    paths["manifest"].write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    result = {
        "gate": "G3S-B2-LAYER-STACK-PREFLIGHT",
        "status": "REVIEW_REQUIRED",
        "revision": REVISION,
        "technical_audit": {
            "exact_recomposition": True,
            "max_channel_diff": max_diff,
            "source_alpha_pixels": int(opaque.sum()),
            "body_visible_pixels": int(body_visible_mask.sum()),
            "hair_pixels": int(hair_mask.sum()),
            "clothing_pixels": int(cloth_mask.sum()),
            "unresolved_underbody_pixels": unresolved_count,
        },
        "architectural_decision": {
            "body_base_must_be_unclothed": True,
            "hair_must_be_separate": True,
            "clothing_must_be_overlay": True,
            "chains_must_be_accessories": True,
            "g3s_c_animation_blocked_until_complete_body_base": True,
        },
        "contact_sheet": str(paths["contact"]),
        "manifest": str(paths["manifest"]),
        "prep": prep,
    }
    paths["result"].write_text(json.dumps(result, indent=2), encoding="utf-8")

    print(f"G3S_B2_REVISION={REVISION}")
    print("G3S_B2_EXACT_RECOMPOSITION=PASS")
    print("G3S_B2_BODY_BASE=INCOMPLETE")
    print("G3S_B2_HAIR_OWNER=SEPARATE_PERSISTENT_LAYER")
    print("G3S_B2_CLOTHING_OWNER=SEPARATE_OVERLAY_LAYER")
    print(f"G3S_B2_UNRESOLVED_UNDERBODY_PIXELS={unresolved_count}")
    print(f"G3S_B2_CONTACT={paths['contact']}")


if __name__ == "__main__":
    main()
