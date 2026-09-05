from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

REVISION = "G3S_B3B_NATIVE_NUDE_BODY_SOURCE_V1"
SIZE = 128
GAME_W, GAME_H = 640, 360
BG = (18, 18, 22)

PALETTE = {
    "outline": (49, 32, 26, 255),
    "deep": (79, 48, 36, 255),
    "shadow": (111, 68, 48, 255),
    "mid": (145, 93, 63, 255),
    "warm": (163, 103, 70, 255),
    "light": (184, 126, 88, 255),
    "high": (211, 158, 111, 255),
    "detail": (84, 45, 37, 255),
}


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


def validate_b3a(manifest: dict) -> None:
    if manifest.get("gate") != "G3S-B3-A-NUDE-ANATOMY-GUIDE":
        raise RuntimeError("Unexpected B3A manifest gate")
    if manifest.get("revision") != "G3S_B3A_NUDE_ANATOMY_GUIDE_V2":
        raise RuntimeError(f"B3A V2 required, got {manifest.get('revision')}")
    if manifest.get("status") != "REVIEW_REQUIRED":
        raise RuntimeError(f"Unexpected B3A state: {manifest.get('status')}")
    audit = manifest.get("phenotype_audit", {})
    if audit.get("resolved_gender") != "female":
        raise RuntimeError("B3A phenotype is not resolved female")
    if audit.get("resolved_life_stage") != "adult":
        raise RuntimeError("B3A phenotype is not resolved adult")
    if int(audit.get("male_target_count", -1)) != 0 or int(audit.get("minor_target_count", -1)) != 0:
        raise RuntimeError("B3A phenotype audit contains male/minor targets")
    layers = manifest.get("layer_audit", {})
    if not bool(layers.get("complete_body_geometry")):
        raise RuntimeError("B3A complete body geometry did not pass")
    for key in ("hair_objects", "clothing_objects", "restraint_objects", "chains_objects"):
        if int(layers.get(key, -1)) != 0:
            raise RuntimeError(f"B3A forbidden layer count is nonzero: {key}={layers.get(key)}")
    if manifest.get("art_authority") != "STRUCTURAL_GUIDE_ONLY_NOT_FINAL_PIXEL_ART":
        raise RuntimeError("B3A must remain structural guide only")


def load_structural_mask(manifest: dict) -> tuple[np.ndarray, Path]:
    mask_path = Path(manifest["outputs"]["mask"])
    if not mask_path.is_file():
        raise FileNotFoundError(mask_path)
    im = Image.open(mask_path).convert("RGB")
    expected = tuple(manifest["camera"]["resolution"])
    if im.size != expected:
        raise RuntimeError(f"B3A mask size drift: got={im.size}, expected={expected}")
    arr = np.asarray(im, dtype=np.uint8)
    luma = arr.astype(np.uint16).sum(axis=2)
    mask = luma >= (3 * 128)
    bb = bbox_from_mask(mask)
    if bb is None:
        raise RuntimeError("B3A mask contains no body pixels")
    visible_h = bb[3] - bb[1] + 1
    if visible_h < 126 or visible_h > 130:
        raise RuntimeError(f"B3A structural visible height out of range: {visible_h}")
    return mask, mask_path


def crop_native(mask: np.ndarray) -> tuple[np.ndarray, dict]:
    h, w = mask.shape
    bb = bbox_from_mask(mask)
    assert bb is not None
    x0, y0, x1, y1 = bb
    cx = (x0 + x1) / 2.0
    cy = (y0 + y1) / 2.0
    left = int(round(cx - SIZE / 2))
    top = int(round(cy - SIZE / 2))
    left = max(0, min(w - SIZE, left))
    top = max(0, min(h - SIZE, top))
    native = mask[top : top + SIZE, left : left + SIZE].copy()
    nbb = bbox_from_mask(native)
    if nbb is None:
        raise RuntimeError("Native crop lost body")
    if nbb[3] - nbb[1] + 1 < 126:
        top = max(0, min(h - SIZE, y0))
        native = mask[top : top + SIZE, left : left + SIZE].copy()
        nbb = bbox_from_mask(native)
        if nbb is None or nbb[3] - nbb[1] + 1 < 126:
            raise RuntimeError(f"Native crop clipped body: {nbb}")
    return native, {
        "source_bbox_game": bb,
        "crop_xy_game": [left, top],
        "native_bbox": nbb,
    }


def neighbor_count(mask: np.ndarray) -> np.ndarray:
    p = np.pad(mask.astype(np.uint8), 1, mode="constant")
    out = np.zeros_like(mask, dtype=np.uint8)
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            out += p[1 + dy : 1 + dy + mask.shape[0], 1 + dx : 1 + dx + mask.shape[1]]
    return out


def row_geometry(mask: np.ndarray):
    centers = np.full(mask.shape[0], np.nan, dtype=np.float32)
    mins = np.full(mask.shape[0], -1, dtype=np.int16)
    maxs = np.full(mask.shape[0], -1, dtype=np.int16)
    for y in range(mask.shape[0]):
        xs = np.where(mask[y])[0]
        if len(xs):
            mins[y], maxs[y] = int(xs.min()), int(xs.max())
            centers[y] = float(xs.mean())
    valid = np.where(~np.isnan(centers))[0]
    if len(valid):
        centers = np.interp(np.arange(mask.shape[0]), valid, centers[valid]).astype(np.float32)
    return mins, maxs, centers


def transform_joint(manifest: dict, crop: dict, name: str):
    p = manifest.get("joints_px", {}).get(name)
    if p is None:
        return None
    return [float(p[0]) - crop["crop_xy_game"][0], float(p[1]) - crop["crop_xy_game"][1]]


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def author_native(mask: np.ndarray, manifest: dict, crop: dict) -> tuple[Image.Image, dict]:
    rgba = np.zeros((SIZE, SIZE, 4), dtype=np.uint8)
    rgba[mask] = PALETTE["mid"]

    ncount = neighbor_count(mask)
    edge = mask & (ncount < 8)
    rgba[edge] = PALETTE["outline"]

    mins, maxs, centers = row_geometry(mask)
    bb = bbox_from_mask(mask)
    assert bb is not None
    bx0, by0, bx1, by1 = bb
    body_h = max(1, by1 - by0)

    for y in range(by0, by1 + 1):
        if mins[y] < 0:
            continue
        width = max(1, maxs[y] - mins[y] + 1)
        c = centers[y]
        for x in range(mins[y], maxs[y] + 1):
            if not mask[y, x] or edge[y, x]:
                continue
            rel = (x - c) / width
            yn = (y - by0) / body_h
            color = "mid"
            if rel < -0.28:
                color = "light"
            if rel < -0.40:
                color = "high"
            if rel > 0.26:
                color = "shadow"
            if rel > 0.40:
                color = "deep"
            if yn > 0.64 and color == "mid":
                color = "warm"
            if 0.24 < yn < 0.54 and color == "mid":
                color = "warm"
            rgba[y, x] = PALETTE[color]

    interior = mask & ~edge

    def put(x, y, color="detail"):
        x, y = int(round(x)), int(round(y))
        if 0 <= x < SIZE and 0 <= y < SIZE and interior[y, x]:
            rgba[y, x] = PALETTE[color]
            return True
        return False

    def put_near(x, y, color="detail"):
        x0, y0 = int(round(x)), int(round(y))
        candidates = [(0,0),(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,-1),(-1,1),(1,1)]
        for dx, dy in candidates:
            if put(x0 + dx, y0 + dy, color):
                return [x0 + dx, y0 + dy]
        return None

    hips = transform_joint(manifest, crop, "Hips")
    spine = transform_joint(manifest, crop, "Spine1")
    neck = transform_joint(manifest, crop, "Neck1")
    head = transform_joint(manifest, crop, "Head")
    larm = transform_joint(manifest, crop, "LeftArm")
    rarm = transform_joint(manifest, crop, "RightArm")
    lleg = transform_joint(manifest, crop, "LeftLeg")
    rleg = transform_joint(manifest, crop, "RightLeg")

    cx = float(np.nanmean(centers[by0:by1+1]))
    y_neck = neck[1] if neck else by0 + 0.17 * body_h
    y_spine = spine[1] if spine else by0 + 0.36 * body_h
    y_hips = hips[1] if hips else by0 + 0.53 * body_h

    head_y = int(round(clamp((by0 + y_neck) * 0.5, by0 + 3, y_neck - 2)))
    head_center = centers[head_y] if 0 <= head_y < SIZE else cx
    put_near(head_center - 2, head_y, "detail")
    put_near(head_center + 2, head_y, "detail")
    put_near(head_center + 0.5, head_y + 4, "deep")
    put_near(head_center - 1.0, head_y - 2, "high")

    chest_y = int(round(clamp((y_neck + y_spine) * 0.52, by0 + 16, y_hips - 10)))
    chest_c = centers[chest_y] if 0 <= chest_y < SIZE else cx
    row_w = max(8, maxs[chest_y] - mins[chest_y] + 1) if 0 <= chest_y < SIZE and mins[chest_y] >= 0 else 24
    breast_dx = max(3, min(7, row_w * 0.16))
    for sx in (-1, 1):
        put_near(chest_c + sx * breast_dx, chest_y + 2, "deep")
        put_near(chest_c + sx * (breast_dx - 1), chest_y, "light")
    for dx in (-3, -2, 2, 3):
        put_near(chest_c + dx, chest_y - 4, "light")

    put_near(chest_c, chest_y + 5, "shadow")
    abdomen_y = int(round(clamp((y_spine + y_hips) * 0.56, chest_y + 5, y_hips - 3)))
    abdomen_c = centers[abdomen_y] if 0 <= abdomen_y < SIZE else cx
    put_near(abdomen_c, abdomen_y, "deep")
    pelvis_y = int(round(clamp(y_hips + 4, abdomen_y + 3, by1 - 30)))
    pelvis_c = centers[pelvis_y] if 0 <= pelvis_y < SIZE else cx
    put_near(pelvis_c, pelvis_y, "detail")
    put_near(pelvis_c - 2, pelvis_y - 2, "shadow")
    put_near(pelvis_c + 2, pelvis_y - 2, "shadow")

    for p in (larm, rarm):
        if p:
            put_near(p[0], p[1] + 1, "light")
    for p in (lleg, rleg):
        if p:
            put_near(p[0] - 1, p[1], "light")
            put_near(p[0] + 1, p[1] + 1, "shadow")

    out = Image.fromarray(rgba, "RGBA")
    unique = np.unique(rgba[rgba[:, :, 3] > 0][:, :3], axis=0)
    stats = {
        "alpha_pixels": int(mask.sum()),
        "visible_bbox": bbox_from_mask(mask),
        "visible_height": int(by1 - by0 + 1),
        "visible_width": int(bx1 - bx0 + 1),
        "unique_opaque_rgb": int(len(unique)),
        "partial_alpha_pixels": int(np.logical_and(rgba[:, :, 3] > 0, rgba[:, :, 3] < 255).sum()),
        "rgb_authority": "EXPLICIT_NATIVE_PALETTE_AND_CLUSTER_RULES",
        "b3a_rgb_sampled": False,
        "b3a_mask_used_for_structure_only": True,
    }
    return out, stats


def make_mask_png(mask: np.ndarray) -> Image.Image:
    arr = np.zeros((SIZE, SIZE, 4), dtype=np.uint8)
    arr[mask] = (255, 255, 255, 255)
    return Image.fromarray(arr, "RGBA")


def gameplay_preview(sprite: Image.Image) -> Image.Image:
    out = Image.new("RGBA", (GAME_W, GAME_H), (*BG, 255))
    x = (GAME_W - SIZE) // 2
    y = (GAME_H - SIZE) // 2
    out.alpha_composite(sprite, (x, y))
    return out.convert("RGB")


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
    d.rectangle([4, 4, size[0] - 4, 26], fill=(0, 0, 0))
    d.text((10, 9), label, fill=(238, 238, 238), font=ImageFont.load_default())
    return out


def info_panel(stats: dict, crop: dict, size=(640, 360)) -> Image.Image:
    out = Image.new("RGB", size, BG)
    d = ImageDraw.Draw(out)
    f = ImageFont.load_default()
    d.rectangle([4, 4, size[0] - 4, 26], fill=(0, 0, 0))
    d.text((10, 9), "D B3B audit - NATIVE BODY SOURCE CANDIDATE, REVIEW REQUIRED", fill=(238,238,238), font=f)
    lines = [
        "G3S-B3B owns visible body pixels. B3A remains structural guide only.",
        "",
        f"native_canvas = 128x128 | visible_height = {stats['visible_height']} px",
        f"visible_width = {stats['visible_width']} px | alpha_pixels = {stats['alpha_pixels']}",
        f"unique opaque RGB = {stats['unique_opaque_rgb']} | partial alpha = {stats['partial_alpha_pixels']}",
        f"B3A structural crop = {crop['crop_xy_game']} | source bbox = {crop['source_bbox_game']}",
        "",
        "NO lit-guide RGB/shading transfer.",
        "NO hair, clothing, bindings, cuffs, shackles or chains.",
        "Palette + anatomy clusters are explicit native-grid authored data.",
        "",
        "REVIEW AT 1x: silhouette / female anatomy / chest / pelvis / face / hands / feet / pixel language.",
        "If B3B passes, only then author G3S-B4 hair.",
    ]
    y = 48
    for line in lines:
        d.text((24, y), line, fill=(238,238,238), font=f)
        y += 18
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--b3a-manifest", required=True)
    ap.add_argument("--output-dir", required=True)
    args = ap.parse_args()

    manifest_path = Path(args.b3a_manifest)
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    validate_b3a(manifest)

    game_mask, game_mask_path = load_structural_mask(manifest)
    native_mask, crop = crop_native(game_mask)
    sprite, stats = author_native(native_mask, manifest, crop)

    if stats["visible_height"] < 126 or stats["visible_height"] > 128:
        raise RuntimeError(f"B3B native visible height out of range: {stats}")
    if stats["alpha_pixels"] < 1200:
        raise RuntimeError(f"B3B body unexpectedly sparse: {stats}")
    if stats["partial_alpha_pixels"] != 0:
        raise RuntimeError(f"B3B must have binary alpha: {stats}")
    if stats["unique_opaque_rgb"] < 5 or stats["unique_opaque_rgb"] > len(PALETTE):
        raise RuntimeError(f"B3B palette audit failed: {stats}")

    source_path = out / "g3s_b3b_nude_body_source_v1.png"
    mask_path = out / "g3s_b3b_nude_body_mask_v1.png"
    preview_path = out / "g3s_b3b_gameplay_preview.png"
    contact_path = out / "g3s_b3b_contact_sheet.png"
    result_path = out / "g3s_b3b_manifest.json"

    sprite.save(source_path)
    make_mask_png(native_mask).save(mask_path)
    preview = gameplay_preview(sprite)
    preview.save(preview_path)

    guide = Image.open(manifest["outputs"]["lit"]).convert("RGBA")
    cells = [
        panel(guide, "A B3A structural adult-female guide - GUIDE ONLY, NOT final art", nearest=False),
        panel(sprite.resize((SIZE * 4, SIZE * 4), Image.Resampling.NEAREST), "B B3B native 128 nude body source V1 - 4x nearest", nearest=True),
        panel(preview, "C gameplay preview 640x360 - 1 asset pixel = 1 screen pixel", nearest=True),
        info_panel(stats, crop),
    ]
    sheet = Image.new("RGB", (1280, 720), BG)
    for cell, pos in zip(cells, [(0,0),(640,0),(0,360),(640,360)]):
        sheet.paste(cell, pos)
    sheet.save(contact_path)

    result = {
        "gate": "G3S-B3-B-NATIVE-NUDE-BODY-SOURCE",
        "status": "REVIEW_REQUIRED",
        "revision": REVISION,
        "source_authority": "NATIVE_128_EXPLICIT_PALETTE_AND_CLUSTER_AUTHORING",
        "b3a_manifest": str(manifest_path),
        "b3a_manifest_sha256": sha256(manifest_path),
        "b3a_mask": str(game_mask_path),
        "b3a_mask_sha256": sha256(game_mask_path),
        "crop": crop,
        "palette": PALETTE,
        "stats": stats,
        "outputs": {
            "source": str(source_path),
            "source_sha256": sha256(source_path),
            "mask": str(mask_path),
            "mask_sha256": sha256(mask_path),
            "gameplay_preview": str(preview_path),
            "gameplay_preview_sha256": sha256(preview_path),
            "contact_sheet": str(contact_path),
            "contact_sheet_sha256": sha256(contact_path),
        },
        "layer_audit": {
            "body_complete": True,
            "hair_pixels": 0,
            "clothing_pixels": 0,
            "binding_pixels": 0,
            "restraint_pixels": 0,
            "chain_pixels": 0,
        },
        "rules": {
            "native_canvas": [128, 128],
            "post_generation_resize": False,
            "b3a_is_structural_guide_only": True,
            "b3a_rgb_sampled": False,
            "b3a_mask_used_for_structure_only": True,
            "final_visible_rgb_owned_by_b3b": True,
            "modern_pixel_art_review_required": True,
            "no_hair_before_b3b_pass": True,
            "no_clothing_before_b3b_pass": True,
            "no_animation_before_b3b_pass": True,
        },
        "next_if_pass": "G3S-B4 HAIR ASSET",
    }
    result_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    print(f"G3S_B3B_REVISION={REVISION}")
    print("G3S_B3B_NATIVE_CANVAS=128x128")
    print("G3S_B3B_B3A_RGB_SAMPLED=FALSE")
    print("G3S_B3B_FORBIDDEN_LAYER_PIXELS=0")
    print(f"G3S_B3B_VISIBLE_HEIGHT={stats['visible_height']}")
    print(f"G3S_B3B_SOURCE={source_path}")
    print(f"G3S_B3B_CONTACT={contact_path}")
    print("G3S_B3B_STATUS=REVIEW_REQUIRED")


if __name__ == "__main__":
    main()
