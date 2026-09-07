#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Dict, Tuple

from PIL import Image, ImageDraw, ImageFont

BODY_SIZE = (37, 128)
BODY_SHA256 = "702e2d95325049b5d99ea66db4fbbb9b41d6d24813efb0b1c3a37e112b1c2858"
LOGICAL = (96, 160)
GROUND_Y = 152
CENTER_X = 48
SCENE = (640, 360)

BG = (16, 16, 20)
GROUND = (42, 35, 30)
TEXT = (235, 235, 240)
DIM = (165, 165, 175)
SKEL = (80, 190, 255, 150)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def font():
    return ImageFont.load_default()


def alpha_bbox(mask: Image.Image):
    return mask.getbbox()


def alpha_pixels(alpha: Image.Image, y0: int, y1: int):
    pix = alpha.load()
    pts = []
    y0 = max(0, y0)
    y1 = min(alpha.height - 1, y1)
    for y in range(y0, y1 + 1):
        for x in range(alpha.width):
            if pix[x, y] > 16:
                pts.append((x, y))
    return pts


def center_in_band(alpha: Image.Image, y: int, radius: int = 2) -> Tuple[float, float]:
    pts = alpha_pixels(alpha, y - radius, y + radius)
    if not pts:
        return (alpha.width * 0.5, float(y))
    return (sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts))


def side_anchor(alpha: Image.Image, y: int, side: str, radius: int = 2, inset: float = 0.18) -> Tuple[float, float]:
    pts = alpha_pixels(alpha, y - radius, y + radius)
    if not pts:
        x = alpha.width * (0.3 if side == "left" else 0.7)
        return (x, float(y))
    xs = [p[0] for p in pts]
    lo, hi = min(xs), max(xs)
    if hi <= lo:
        return (float(lo), float(y))
    x = lo + (hi - lo) * (inset if side == "left" else (1.0 - inset))
    return (float(x), float(y))


def circle_mask(size, center, radius):
    im = Image.new("L", size, 0)
    d = ImageDraw.Draw(im)
    x, y = center
    d.ellipse((x-radius, y-radius, x+radius, y+radius), fill=255)
    return im


def capsule_mask(size, a, b, radius):
    im = Image.new("L", size, 0)
    d = ImageDraw.Draw(im)
    width = int(max(1, round(radius * 2 + 1)))
    d.line((a[0], a[1], b[0], b[1]), fill=255, width=width)
    for p in (a, b):
        d.ellipse((p[0]-radius, p[1]-radius, p[0]+radius, p[1]+radius), fill=255)
    return im


def mask_and(a: Image.Image, b: Image.Image) -> Image.Image:
    pa, pb = a.load(), b.load()
    out = Image.new("L", a.size, 0)
    po = out.load()
    for y in range(a.height):
        for x in range(a.width):
            po[x, y] = min(pa[x, y], pb[x, y])
    return out


def mask_or(masks) -> Image.Image:
    if not masks:
        raise ValueError("empty mask list")
    out = Image.new("L", masks[0].size, 0)
    po = out.load()
    ps = [m.load() for m in masks]
    for y in range(out.height):
        for x in range(out.width):
            po[x, y] = max(p[x, y] for p in ps)
    return out


def mask_subtract(a: Image.Image, b: Image.Image) -> Image.Image:
    pa, pb = a.load(), b.load()
    out = Image.new("L", a.size, 0)
    po = out.load()
    for y in range(a.height):
        for x in range(a.width):
            po[x, y] = max(0, pa[x, y] - pb[x, y])
    return out


def apply_mask(src: Image.Image, mask: Image.Image) -> Image.Image:
    out = src.copy()
    alpha = out.getchannel("A")
    alpha = mask_and(alpha, mask)
    out.putalpha(alpha)
    return out


def derive_rest_rig(body: Image.Image):
    alpha = body.getchannel("A")
    # Y levels are deliberate beat-em-up puppet bind landmarks. X positions are
    # fitted to the actual B3B silhouette so the script does not assume a generic
    # body width. Anatomical left is bound to the screen-left rest limb for this
    # one directional family; ownership remains explicit in the manifest.
    rig = {
        "head": center_in_band(alpha, 9, 5),
        "neck": center_in_band(alpha, 24, 2),
        "chest": center_in_band(alpha, 39, 3),
        "pelvis": center_in_band(alpha, 61, 3),
    }
    for side in ("left", "right"):
        rig[f"{side}_shoulder"] = side_anchor(alpha, 30, side, 3, 0.16)
        rig[f"{side}_elbow"] = side_anchor(alpha, 49, side, 3, 0.12)
        rig[f"{side}_wrist"] = side_anchor(alpha, 67, side, 4, 0.08)
        rig[f"{side}_hip"] = side_anchor(alpha, 63, side, 3, 0.28)
        rig[f"{side}_knee"] = side_anchor(alpha, 90, side, 4, 0.22)
        rig[f"{side}_ankle"] = side_anchor(alpha, 116, side, 3, 0.18)
        rig[f"{side}_toe"] = side_anchor(alpha, 125, side, 2, 0.10)
    return rig


def build_parts(body: Image.Image, rest: dict):
    alpha = body.getchannel("A")
    parts_masks: Dict[str, Image.Image] = {}

    head_mask = Image.new("L", BODY_SIZE, 0)
    ImageDraw.Draw(head_mask).rectangle((0, 0, BODY_SIZE[0]-1, 30), fill=255)
    parts_masks["head_neck"] = mask_and(alpha, head_mask)

    limb_masks = []
    for side in ("left", "right"):
        defs = [
            (f"{side}_upper_arm", rest[f"{side}_shoulder"], rest[f"{side}_elbow"], 4.1),
            (f"{side}_forearm", rest[f"{side}_elbow"], rest[f"{side}_wrist"], 3.7),
            (f"{side}_thigh", rest[f"{side}_hip"], rest[f"{side}_knee"], 5.3),
            (f"{side}_shin", rest[f"{side}_knee"], rest[f"{side}_ankle"], 4.4),
            (f"{side}_foot", rest[f"{side}_ankle"], rest[f"{side}_toe"], 4.2),
        ]
        for name, a, b, r in defs:
            m = mask_and(alpha, capsule_mask(BODY_SIZE, a, b, r))
            parts_masks[name] = m
            limb_masks.append(m)
        hand = mask_and(alpha, circle_mask(BODY_SIZE, rest[f"{side}_wrist"], 5.0))
        parts_masks[f"{side}_hand"] = hand
        limb_masks.append(hand)

    # Core is intentionally one persistent chest/pelvis unit for the first
    # belt-scroller proof. Limbs are removed, but shoulder/hip cap pixels are
    # restored so the core itself covers attachment seams.
    remove = mask_or(limb_masks + [parts_masks["head_neck"]])
    core = mask_subtract(alpha, remove)
    cap_masks = []
    for side in ("left", "right"):
        cap_masks.append(circle_mask(BODY_SIZE, rest[f"{side}_shoulder"], 4.6))
        cap_masks.append(circle_mask(BODY_SIZE, rest[f"{side}_hip"], 5.3))
    cap_union = mask_and(alpha, mask_or(cap_masks))
    core = mask_or([core, cap_union])
    # Keep a small neck overlap in the torso as well.
    core = mask_or([core, mask_and(alpha, circle_mask(BODY_SIZE, rest["neck"], 4.2))])
    parts_masks["core"] = core

    parts = {name: apply_mask(body, m) for name, m in parts_masks.items()}
    empty = [name for name, im in parts.items() if im.getbbox() is None]
    if empty:
        raise RuntimeError("empty puppet parts: " + ", ".join(empty))
    return parts, parts_masks


def angle_len(a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    return math.atan2(dy, dx), math.hypot(dx, dy)


def transform_part(src: Image.Image, pivot_rest, end_rest, target_a, target_b, canvas=LOGICAL,
                   scale_min=0.62, scale_max=1.45):
    rest_angle, rest_len = angle_len(pivot_rest, end_rest)
    target_angle, target_len = angle_len(target_a, target_b)
    if rest_len < 1e-6 or target_len < 1e-6:
        scale = 1.0
        delta = 0.0
    else:
        scale = max(scale_min, min(scale_max, target_len / rest_len))
        delta = target_angle - rest_angle
    c = math.cos(delta)
    s = math.sin(delta)
    inv = 1.0 / scale
    tx, ty = target_a
    px, py = pivot_rest
    # PIL affine is inverse mapping output -> input.
    coeffs = (
        inv * c,
        inv * s,
        px - inv * (c * tx + s * ty),
        -inv * s,
        inv * c,
        py + inv * (s * tx - c * ty),
    )
    return src.transform(canvas, Image.Transform.AFFINE, coeffs, resample=Image.Resampling.NEAREST)


def extrapolate(a, b, length):
    dx, dy = b[0] - a[0], b[1] - a[1]
    n = math.hypot(dx, dy)
    if n < 1e-6:
        return b
    return (b[0] + dx / n * length, b[1] + dy / n * length)


def localize_guide(guide):
    frames = guide["frames"]
    cam = guide.get("camera", {})
    measured = float(cam.get("max_measured_skeleton_height_px", 128.0))
    scale = 128.0 / measured if measured > 1e-6 else 1.0
    first_pelvis_x = float(frames[0]["joints"]["pelvis"]["x"])
    global_ground = max(
        float(f["joints"][name]["y"])
        for f in frames
        for name in ("left_ankle", "left_toe", "right_ankle", "right_toe")
    )

    out = []
    for frame in frames:
        joints = {}
        for name, rec in frame["joints"].items():
            joints[name] = {
                "x": CENTER_X + (float(rec["x"]) - first_pelvis_x) * scale,
                "y": GROUND_Y + (float(rec["y"]) - global_ground) * scale,
                "depth": float(rec.get("depth", 0.0)),
                "anatomical_side": rec.get("anatomical_side", "center"),
            }
        row = dict(frame)
        row["local_joints"] = joints
        out.append(row)
    return out, {"scale": scale, "first_pelvis_x": first_pelvis_x, "global_ground_y": global_ground}


def part_depth(joints, a, b):
    return (float(joints[a]["depth"]) + float(joints[b]["depth"])) * 0.5


def composite_frame(parts, rest, frame):
    j = frame["local_joints"]
    layers = []

    def add(name, a_rest, b_rest, a_tgt, b_tgt, depth):
        layers.append((depth, name, transform_part(parts[name], a_rest, b_rest, a_tgt, b_tgt)))

    # Center pieces.
    add("core", rest["pelvis"], rest["chest"],
        (j["pelvis"]["x"], j["pelvis"]["y"]), (j["chest"]["x"], j["chest"]["y"]),
        part_depth(j, "pelvis", "chest"))
    add("head_neck", rest["neck"], rest["head"],
        (j["neck"]["x"], j["neck"]["y"]), (j["head"]["x"], j["head"]["y"]),
        part_depth(j, "neck", "head"))

    for side in ("left", "right"):
        shoulder = (j[f"{side}_shoulder"]["x"], j[f"{side}_shoulder"]["y"])
        elbow = (j[f"{side}_elbow"]["x"], j[f"{side}_elbow"]["y"])
        wrist = (j[f"{side}_wrist"]["x"], j[f"{side}_wrist"]["y"])
        hip = (j[f"{side}_hip"]["x"], j[f"{side}_hip"]["y"])
        knee = (j[f"{side}_knee"]["x"], j[f"{side}_knee"]["y"])
        ankle = (j[f"{side}_ankle"]["x"], j[f"{side}_ankle"]["y"])
        toe = (j[f"{side}_toe"]["x"], j[f"{side}_toe"]["y"])
        add(f"{side}_upper_arm", rest[f"{side}_shoulder"], rest[f"{side}_elbow"], shoulder, elbow,
            part_depth(j, f"{side}_shoulder", f"{side}_elbow"))
        add(f"{side}_forearm", rest[f"{side}_elbow"], rest[f"{side}_wrist"], elbow, wrist,
            part_depth(j, f"{side}_elbow", f"{side}_wrist"))
        hand_rest_end = extrapolate(rest[f"{side}_elbow"], rest[f"{side}_wrist"], 6.0)
        hand_tgt_end = extrapolate(elbow, wrist, 6.0)
        add(f"{side}_hand", rest[f"{side}_wrist"], hand_rest_end, wrist, hand_tgt_end,
            float(j[f"{side}_wrist"]["depth"]) - 0.002)
        add(f"{side}_thigh", rest[f"{side}_hip"], rest[f"{side}_knee"], hip, knee,
            part_depth(j, f"{side}_hip", f"{side}_knee"))
        add(f"{side}_shin", rest[f"{side}_knee"], rest[f"{side}_ankle"], knee, ankle,
            part_depth(j, f"{side}_knee", f"{side}_ankle"))
        add(f"{side}_foot", rest[f"{side}_ankle"], rest[f"{side}_toe"], ankle, toe,
            part_depth(j, f"{side}_ankle", f"{side}_toe"))

    # Larger camera-space depth is farther away in C1A. Draw far -> near.
    layers.sort(key=lambda row: row[0], reverse=True)
    out = Image.new("RGBA", LOGICAL, (0, 0, 0, 0))
    for _depth, _name, im in layers:
        out.alpha_composite(im)
    return out, [name for _depth, name, _im in layers]


def draw_skeleton_overlay(im, frame):
    out = im.copy()
    d = ImageDraw.Draw(out, "RGBA")
    j = frame["local_joints"]
    chains = [
        ("head", "neck"), ("neck", "chest"), ("chest", "pelvis"),
        ("left_shoulder", "left_elbow"), ("left_elbow", "left_wrist"),
        ("right_shoulder", "right_elbow"), ("right_elbow", "right_wrist"),
        ("left_hip", "left_knee"), ("left_knee", "left_ankle"), ("left_ankle", "left_toe"),
        ("right_hip", "right_knee"), ("right_knee", "right_ankle"), ("right_ankle", "right_toe"),
    ]
    for a, b in chains:
        d.line((j[a]["x"], j[a]["y"], j[b]["x"], j[b]["y"]), fill=SKEL, width=1)
    return out


def save_gif(path: Path, frames, duration):
    rgb = []
    for f in frames:
        bg = Image.new("RGB", f.size, BG)
        if f.mode == "RGBA":
            bg.paste(f, (0, 0), f)
        else:
            bg.paste(f)
        rgb.append(bg)
    rgb[0].save(path, save_all=True, append_images=rgb[1:], duration=duration, loop=0,
                disposal=2, optimize=False)


def make_atlas(parts, rest, ws: Path):
    names = ["head_neck", "core",
             "left_upper_arm", "left_forearm", "left_hand", "right_upper_arm", "right_forearm", "right_hand",
             "left_thigh", "left_shin", "left_foot", "right_thigh", "right_shin", "right_foot"]
    crops = {}
    maxw, maxh = 1, 1
    for name in names:
        bbox = parts[name].getbbox()
        crop = parts[name].crop(bbox)
        crops[name] = (bbox, crop)
        maxw, maxh = max(maxw, crop.width), max(maxh, crop.height)
        crop.save(ws / f"part_{name}.png")
    scale = 4
    cell_w = max(100, maxw * scale + 20)
    cell_h = max(120, maxh * scale + 32)
    atlas = Image.new("RGB", (cell_w * 4, cell_h * 4), BG)
    d = ImageDraw.Draw(atlas)
    manifest = {}
    for i, name in enumerate(names):
        bbox, crop = crops[name]
        x0 = (i % 4) * cell_w
        y0 = (i // 4) * cell_h
        zoom = crop.resize((crop.width * scale, crop.height * scale), Image.Resampling.NEAREST)
        atlas.paste(zoom, (x0 + 8, y0 + 22), zoom)
        d.text((x0 + 8, y0 + 6), name, fill=TEXT, font=font())
        manifest[name] = {"bbox_in_b3b": list(bbox), "file": f"part_{name}.png"}
    atlas_path = ws / "g3s_c1b_segmented_part_atlas.png"
    atlas.save(atlas_path)
    return atlas_path, manifest


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--body", required=True)
    ap.add_argument("--guide", required=True)
    ap.add_argument("--approval", required=True)
    ap.add_argument("--spec", required=True)
    ap.add_argument("--workspace", required=True)
    args = ap.parse_args()

    body_path = Path(args.body)
    guide_path = Path(args.guide)
    approval_path = Path(args.approval)
    spec_path = Path(args.spec)
    ws = Path(args.workspace)
    for p in (body_path, guide_path, approval_path, spec_path):
        if not p.is_file():
            raise FileNotFoundError(p)
    ws.mkdir(parents=True, exist_ok=True)

    if sha256(body_path) != BODY_SHA256:
        raise RuntimeError("canonical B3B hash mismatch")
    body = Image.open(body_path).convert("RGBA")
    if body.size != BODY_SIZE:
        raise RuntimeError(f"canonical B3B dimensions changed: {body.size}")

    approval = json.loads(approval_path.read_text(encoding="utf-8-sig"))
    if approval.get("gate") != "G3S-C1A" or approval.get("status") != "PASS":
        raise RuntimeError("C1A skeleton walk is not approved PASS")
    guide = json.loads(guide_path.read_text(encoding="utf-8-sig"))
    if guide.get("gate") != "G3S-C1A" or len(guide.get("frames", [])) != 8:
        raise RuntimeError("unexpected C1A guide")
    spec = json.loads(spec_path.read_text(encoding="utf-8-sig"))
    if spec.get("gate") != "G3S-C1B" or spec.get("revision") != "MINIMAL_BEATEMUP_SEGMENTED_PUPPET_V2":
        raise RuntimeError("unexpected segmented puppet spec")

    rest = derive_rest_rig(body)
    parts, _masks = build_parts(body, rest)
    atlas_path, part_manifest = make_atlas(parts, rest, ws)
    localized, mapping = localize_guide(guide)

    native_frames = []
    overlay_frames = []
    draw_orders = []
    frame_paths = []
    for i, frame in enumerate(localized):
        composed, order = composite_frame(parts, rest, frame)
        native_frames.append(composed)
        overlay_frames.append(draw_skeleton_overlay(composed, frame))
        draw_orders.append(order)
        path = ws / f"g3s_c1b_puppet_{i:02d}_{frame['event']}.png"
        composed.save(path)
        frame_paths.append(str(path))

    duration = int(guide.get("frame_duration_ms", 83))
    in_place = ws / "g3s_c1b_puppet_walk_in_place.gif"
    save_gif(in_place, native_frames, duration)
    zoom_frames = [f.resize((LOGICAL[0]*4, LOGICAL[1]*4), Image.Resampling.NEAREST) for f in native_frames]
    zoom = ws / "g3s_c1b_puppet_walk_zoom.gif"
    save_gif(zoom, zoom_frames, duration)

    # Travel preview at gameplay raster. The local puppet remains the same; only
    # root travel translates the composed sprite screen-left.
    travel_frames = []
    for f, frame in zip(native_frames, localized):
        scene = Image.new("RGB", SCENE, BG)
        d = ImageDraw.Draw(scene)
        ground_y = 288
        d.rectangle((0, ground_y, SCENE[0], SCENE[1]), fill=GROUND)
        d.line((0, ground_y, SCENE[0], ground_y), fill=(92, 78, 66), width=1)
        dx = float(frame.get("root_travel_dx_px", 0.0))
        x = int(round(360 - CENTER_X + dx))
        y = int(round(ground_y - GROUND_Y))
        scene.paste(f, (x, y), f)
        travel_frames.append(scene)
    travel = ws / "g3s_c1b_puppet_walk_travel.gif"
    travel_frames[0].save(travel, save_all=True, append_images=travel_frames[1:], duration=duration,
                          loop=0, disposal=2, optimize=False)

    # 4x2 review sheets: clean and skeleton overlay.
    cell = (LOGICAL[0]*3, LOGICAL[1]*3)
    footer = 92
    sheet = Image.new("RGB", (cell[0]*4, cell[1]*2 + footer), BG)
    sheet_overlay = Image.new("RGB", sheet.size, BG)
    for i, (clean, over, frame) in enumerate(zip(native_frames, overlay_frames, localized)):
        x = (i % 4) * cell[0]
        y = (i // 4) * cell[1]
        c = clean.resize(cell, Image.Resampling.NEAREST)
        o = over.resize(cell, Image.Resampling.NEAREST)
        bg1 = Image.new("RGB", cell, (226, 226, 222)); bg1.paste(c, (0, 0), c)
        bg2 = Image.new("RGB", cell, (226, 226, 222)); bg2.paste(o, (0, 0), o)
        sheet.paste(bg1, (x, y)); sheet_overlay.paste(bg2, (x, y))
        for target in (sheet, sheet_overlay):
            dd = ImageDraw.Draw(target)
            dd.rectangle((x, y, x+cell[0]-1, y+22), fill=(8, 8, 11))
            dd.text((x+6, y+7), f"{frame['event']} | src {frame['frame']} | support {frame['support_foot']}", fill=TEXT, font=font())
    y0 = cell[1]*2
    for target, label in ((sheet, "CLEAN"), (sheet_overlay, "SKELETON OVERLAY")):
        dd = ImageDraw.Draw(target)
        dd.text((12, y0+12), f"C1B MINIMAL BEAT-EM-UP 2D PUPPET | {label}", fill=TEXT, font=font())
        dd.text((12, y0+32), "Same persistent B3B pixels/parts in all 8 states. No per-frame generation. No MPFB body. Hair deferred.", fill=DIM, font=font())
        dd.text((12, y0+52), "This proof deliberately uses one directional family and the minimum part set. Variants are forbidden until a concrete defect requires one.", fill=DIM, font=font())
    sheet_path = ws / "g3s_c1b_puppet_contact_sheet.png"
    overlay_path = ws / "g3s_c1b_puppet_contact_sheet_skeleton_overlay.png"
    sheet.save(sheet_path); sheet_overlay.save(overlay_path)

    bind_manifest = {
        "gate": "G3S-C1B",
        "revision": "MINIMAL_BEATEMUP_SEGMENTED_PUPPET_V2",
        "status": "REVIEW_REQUIRED",
        "canonical_body_sha256": BODY_SHA256,
        "logical_canvas": list(LOGICAL),
        "ground_y": GROUND_Y,
        "rest_screen_side_mapping": {"anatomical_left": "screen_left", "anatomical_right": "screen_right"},
        "rest_joints": {k: [round(v[0], 4), round(v[1], 4)] for k, v in rest.items()},
        "parts": part_manifest,
        "joint_overlap": "capsule masks overlap at elbow/knee/wrist/ankle; torso core retains shoulder/hip/neck caps",
        "guide_mapping": mapping,
        "draw_orders_far_to_near": draw_orders,
        "frame_pngs": frame_paths,
        "outputs": {
            "atlas": str(atlas_path),
            "in_place_gif": str(in_place),
            "zoom_gif": str(zoom),
            "travel_gif": str(travel),
            "contact_sheet": str(sheet_path),
            "overlay_contact_sheet": str(overlay_path),
        },
        "hard_locks": {
            "per_frame_generation": False,
            "mpfb_body": False,
            "full_body_warp": False,
            "nearest_segment_exclusive_partition": False,
            "persistent_b3b_pixels": True,
            "part_variants_used": False,
            "hair": False,
        },
    }
    manifest_path = ws / "g3s_c1b_puppet_bind_manifest.json"
    manifest_path.write_text(json.dumps(bind_manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print("G3S-C1B MINIMAL SEGMENTED PUPPET REVIEW PACKAGE READY")
    print(f"ATLAS:   {atlas_path}")
    print(f"INPLACE: {in_place}")
    print(f"ZOOM:    {zoom}")
    print(f"TRAVEL:  {travel}")
    print(f"SHEET:   {sheet_path}")
    print(f"OVERLAY: {overlay_path}")
    print(f"BIND:    {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
