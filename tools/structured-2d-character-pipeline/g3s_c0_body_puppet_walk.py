#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

EXPECTED_SIZE = (37, 128)
EXPECTED_PNG_SHA = "702e2d95325049b5d99ea66db4fbbb9b41d6d24813efb0b1c3a37e112b1c2858"
EXPECTED_RAW_SHA = "818f0538a145917eac921ad708b3cdf30f87b2c76bc1413aa59305556af7f25c"
LOGICAL = (96, 160)
BODY_ANCHOR = (29, 24)
SCENE = (640, 360)
GROUND_Y = 286

# Assistant-owned rig calibration for the already-approved 37x128 sprite.
# These are 2D deformation pivots, not replacement visual anatomy and not user-authored keyframes.
S = {
    "pelvis": (49.0, 88.0),
    "neck": (49.0, 48.0),
    "head": (48.0, 35.0),
    "left_shoulder": (43.0, 53.0),
    "left_elbow": (39.0, 71.0),
    "left_wrist": (38.0, 89.0),
    "right_shoulder": (55.0, 54.0),
    "right_elbow": (60.0, 72.0),
    "right_wrist": (58.0, 91.0),
    "left_hip": (45.0, 88.0),
    "left_knee": (43.0, 115.0),
    "left_ankle": (42.0, 141.0),
    "left_toe": (36.0, 150.0),
    "right_hip": (53.0, 89.0),
    "right_knee": (55.0, 117.0),
    "right_ankle": (55.0, 143.0),
    "right_toe": (61.0, 151.0),
}

PARTS = {
    "torso": ("pelvis", "neck", 10.0),
    "head": ("neck", "head", 7.0),
    "left_upper_arm": ("left_shoulder", "left_elbow", 4.5),
    "left_forearm": ("left_elbow", "left_wrist", 4.0),
    "right_upper_arm": ("right_shoulder", "right_elbow", 4.5),
    "right_forearm": ("right_elbow", "right_wrist", 4.0),
    "left_thigh": ("left_hip", "left_knee", 7.0),
    "left_shin": ("left_knee", "left_ankle", 5.0),
    "left_foot": ("left_ankle", "left_toe", 4.0),
    "right_thigh": ("right_hip", "right_knee", 7.0),
    "right_shin": ("right_knee", "right_ankle", 5.0),
    "right_foot": ("right_ankle", "right_toe", 4.0),
}

DEPTH_JOINTS = {
    "torso": ("pelvis", "neck"),
    "head": ("neck", "head"),
    "left_upper_arm": ("left_shoulder", "left_elbow"),
    "left_forearm": ("left_elbow", "left_wrist"),
    "right_upper_arm": ("right_shoulder", "right_elbow"),
    "right_forearm": ("right_elbow", "right_wrist"),
    "left_thigh": ("left_hip", "left_knee"),
    "left_shin": ("left_knee", "left_ankle"),
    "left_foot": ("left_ankle", "left_toe"),
    "right_thigh": ("right_hip", "right_knee"),
    "right_shin": ("right_knee", "right_ankle"),
    "right_foot": ("right_ankle", "right_toe"),
}


def sha_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def sha_raw(im: Image.Image) -> str:
    return hashlib.sha256(im.convert("RGBA").tobytes()).hexdigest()


def dist_seg(px, py, a, b):
    ax, ay = a; bx, by = b
    vx, vy = bx - ax, by - ay
    wx, wy = px - ax, py - ay
    vv = vx * vx + vy * vy
    if vv <= 1e-9:
        return math.hypot(wx, wy)
    t = max(0.0, min(1.0, (wx * vx + wy * vy) / vv))
    qx, qy = ax + t * vx, ay + t * vy
    return math.hypot(px - qx, py - qy)


def angle(a, b):
    return math.atan2(b[1] - a[1], b[0] - a[0])


def wrap(a):
    while a > math.pi: a -= 2 * math.pi
    while a < -math.pi: a += 2 * math.pi
    return a


def rotate_vec(v, a):
    c, s = math.cos(a), math.sin(a)
    return (v[0] * c - v[1] * s, v[0] * s + v[1] * c)


def add(a, b): return (a[0] + b[0], a[1] + b[1])
def sub(a, b): return (a[0] - b[0], a[1] - b[1])


def motion_xy(frame, name):
    j = frame["joints"][name]
    return (float(j["x"]), float(j["y"]))


def delta_angle(frame, ref, a, b):
    return wrap(angle(motion_xy(frame, a), motion_xy(frame, b)) - angle(motion_xy(ref, a), motion_xy(ref, b)))


def target_skeleton(frame, ref):
    # Root travel is removed for the local puppet; vertical pelvis motion is retained.
    rp = motion_xy(ref, "pelvis")
    fp = motion_xy(frame, "pelvis")
    bob = max(-5.0, min(5.0, (fp[1] - rp[1]) * 0.7))
    sway = max(-2.0, min(2.0, (fp[0] - rp[0]) * 0.12))
    t = {"pelvis": (S["pelvis"][0] + sway, S["pelvis"][1] + bob)}

    torso_da = delta_angle(frame, ref, "pelvis", "neck")
    t["neck"] = add(t["pelvis"], rotate_vec(sub(S["neck"], S["pelvis"]), torso_da))
    head_da = delta_angle(frame, ref, "neck", "head")
    t["head"] = add(t["neck"], rotate_vec(sub(S["head"], S["neck"]), head_da))

    for side in ("left", "right"):
        shoulder = f"{side}_shoulder"; elbow = f"{side}_elbow"; wrist = f"{side}_wrist"
        hip = f"{side}_hip"; knee = f"{side}_knee"; ankle = f"{side}_ankle"; toe = f"{side}_toe"

        sh_da = delta_angle(frame, ref, "neck", shoulder)
        t[shoulder] = add(t["neck"], rotate_vec(sub(S[shoulder], S["neck"]), sh_da))
        ua_da = delta_angle(frame, ref, shoulder, elbow)
        t[elbow] = add(t[shoulder], rotate_vec(sub(S[elbow], S[shoulder]), ua_da))
        fa_da = delta_angle(frame, ref, elbow, wrist)
        t[wrist] = add(t[elbow], rotate_vec(sub(S[wrist], S[elbow]), fa_da))

        hip_da = delta_angle(frame, ref, "pelvis", hip)
        t[hip] = add(t["pelvis"], rotate_vec(sub(S[hip], S["pelvis"]), hip_da))
        th_da = delta_angle(frame, ref, hip, knee)
        t[knee] = add(t[hip], rotate_vec(sub(S[knee], S[hip]), th_da))
        shn_da = delta_angle(frame, ref, knee, ankle)
        t[ankle] = add(t[knee], rotate_vec(sub(S[ankle], S[knee]), shn_da))
        ft_da = delta_angle(frame, ref, ankle, toe)
        t[toe] = add(t[ankle], rotate_vec(sub(S[toe], S[ankle]), ft_da))
    return t


def partition_parts(body_canvas: Image.Image):
    alpha = body_canvas.getchannel("A")
    labels = {name: Image.new("L", LOGICAL, 0) for name in PARTS}
    pix = alpha.load()
    lp = {name: labels[name].load() for name in PARTS}
    for y in range(LOGICAL[1]):
        for x in range(LOGICAL[0]):
            if pix[x, y] == 0:
                continue
            best_name, best_score = None, 1e9
            for name, (a, b, radius) in PARTS.items():
                score = dist_seg(x + 0.5, y + 0.5, S[a], S[b]) / radius
                # Preserve central trunk against nearby limbs.
                if name != "torso" and 43 <= x <= 55 and 49 <= y <= 92:
                    score += 1.4
                if name == "head" and y <= 47:
                    score -= 0.35
                if name == "torso" and y >= 98:
                    score += 1.0
                if score < best_score:
                    best_name, best_score = name, score
            lp[best_name][x, y] = 255

    parts = {}
    counts = {}
    for name, mask in labels.items():
        # One-pixel source overlap reduces rotation seams without painting new colors.
        dm = mask.filter(ImageFilter.MaxFilter(3))
        dm = ImageChops.multiply(dm, alpha)
        part = body_canvas.copy()
        part.putalpha(dm)
        parts[name] = part
        counts[name] = sum(1 for v in mask.getdata() if v)
    return parts, counts


def transform_part(part, name, target):
    a_name, b_name, _ = PARTS[name]
    sa, sb = S[a_name], S[b_name]
    ta, tb = target[a_name], target[b_name]
    da = wrap(angle(ta, tb) - angle(sa, sb))
    # PIL positive rotation is visual CCW; image-coordinate positive angle is visual CW.
    deg = -math.degrees(da)
    dx = int(round(ta[0] - sa[0])); dy = int(round(ta[1] - sa[1]))
    return part.rotate(deg, resample=Image.Resampling.NEAREST, center=sa, translate=(dx, dy), expand=False)


def depth_order(frame):
    rows = []
    for name, (a, b) in DEPTH_JOINTS.items():
        d = (float(frame["joints"][a]["depth"]) + float(frame["joints"][b]["depth"])) * 0.5
        rows.append((d, name))
    # Larger camera distance = farther = compose first.
    rows.sort(reverse=True)
    return [n for _, n in rows]


def logical_frame(parts, frame, ref):
    target = target_skeleton(frame, ref)
    transformed = {name: transform_part(parts[name], name, target) for name in parts}
    out = Image.new("RGBA", LOGICAL, (0, 0, 0, 0))
    for name in depth_order(frame):
        out.alpha_composite(transformed[name])
    return out, target


def scene_frame(logical, x_center, travel=False):
    scene = Image.new("RGBA", SCENE, (18, 18, 21, 255))
    d = ImageDraw.Draw(scene)
    d.rectangle((0, GROUND_Y, SCENE[0], SCENE[1]), fill=(38, 31, 27, 255))
    bbox = logical.getchannel("A").getbbox()
    if bbox is None:
        raise RuntimeError("empty animated logical frame")
    crop = logical.crop(bbox)
    x = int(round(x_center - crop.width / 2))
    y = GROUND_Y - crop.height
    scene.alpha_composite(crop, (x, y))
    return scene


def make_contact(frames, out_path):
    cell_w, cell_h = 320, 180
    sheet = Image.new("RGBA", (cell_w * 4, cell_h * 2), (12, 12, 15, 255))
    font = ImageFont.load_default()
    for i, fr in enumerate(frames):
        small = fr.resize((cell_w, cell_h), Image.Resampling.NEAREST)
        x = (i % 4) * cell_w; y = (i // 4) * cell_h
        sheet.alpha_composite(small, (x, y))
        ImageDraw.Draw(sheet).text((x + 8, y + 8), f"C0 frame {i}", fill=(235, 235, 240), font=font)
    sheet.convert("RGB").save(out_path, quality=95)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--body", required=True)
    ap.add_argument("--motion", required=True)
    ap.add_argument("--workspace", required=True)
    args = ap.parse_args()

    body_path = Path(args.body)
    motion_path = Path(args.motion)
    workspace = Path(args.workspace)
    workspace.mkdir(parents=True, exist_ok=True)
    if not body_path.is_file() or not motion_path.is_file():
        raise FileNotFoundError("body or motion projection missing")

    body = Image.open(body_path).convert("RGBA")
    if body.size != EXPECTED_SIZE:
        raise RuntimeError(f"body dimensions changed: {body.size}")
    if sha_file(body_path) != EXPECTED_PNG_SHA or sha_raw(body) != EXPECTED_RAW_SHA:
        raise RuntimeError("canonical B3B body hash mismatch")

    motion = json.loads(motion_path.read_text(encoding="utf-8-sig"))
    frames = motion.get("frames", [])
    if len(frames) != 8:
        raise RuntimeError(f"expected 8 real-motion frames, got {len(frames)}")

    canvas = Image.new("RGBA", LOGICAL, (0, 0, 0, 0))
    canvas.alpha_composite(body, BODY_ANCHOR)
    parts, counts = partition_parts(canvas)
    if any(v < 8 for v in counts.values()):
        raise RuntimeError(f"body partition produced implausibly small part: {counts}")

    ref = frames[0]
    logical_frames = []
    target_skeletons = []
    for i, frame in enumerate(frames):
        lf, target = logical_frame(parts, frame, ref)
        logical_frames.append(lf)
        target_skeletons.append(target)
        lf.save(workspace / f"g3s_c0_body_frame_{i:02d}.png")

    in_place = [scene_frame(lf, 320) for lf in logical_frames]
    travel = [scene_frame(lf, 250 + i * (140 / 7.0), travel=True) for i, lf in enumerate(logical_frames)]
    duration_ms = 83

    in_gif = workspace / "g3s_c0_body_walk_in_place.gif"
    travel_gif = workspace / "g3s_c0_body_walk_travel.gif"
    in_place[0].convert("P", palette=Image.Palette.ADAPTIVE).save(
        in_gif, save_all=True,
        append_images=[f.convert("P", palette=Image.Palette.ADAPTIVE) for f in in_place[1:]],
        duration=duration_ms, loop=0, disposal=2, optimize=False)
    travel[0].convert("P", palette=Image.Palette.ADAPTIVE).save(
        travel_gif, save_all=True,
        append_images=[f.convert("P", palette=Image.Palette.ADAPTIVE) for f in travel[1:]],
        duration=duration_ms, loop=0, disposal=2, optimize=False)

    contact = workspace / "g3s_c0_body_walk_contact_sheet.png"
    make_contact(in_place, contact)

    report = {
        "gate": "G3S-C0",
        "revision": "BODY_ONLY_DIRECTION_SPACE_PUPPET_V1",
        "status": "REVIEW_REQUIRED",
        "canonical_body_png_sha256": EXPECTED_PNG_SHA,
        "canonical_body_raw_rgba_sha256": EXPECTED_RAW_SHA,
        "canonical_body_modified": False,
        "motion_source": motion.get("source_motion"),
        "motion_sample_frames": motion.get("sample_frames"),
        "direction_space_method": motion.get("direction_space_method"),
        "part_pixel_counts_before_overlap": counts,
        "source_rig_points": {k: list(v) for k, v in S.items()},
        "frame_duration_ms": duration_ms,
        "frame_count": len(frames),
        "per_frame_diffusion": False,
        "hidden_3d_rgb_used": False,
        "automatic_promotion": False,
        "outputs": {
            "in_place_gif": str(in_gif),
            "travel_gif": str(travel_gif),
            "contact_sheet": str(contact),
        },
        "output_sha256": {
            "in_place_gif": sha_file(in_gif),
            "travel_gif": sha_file(travel_gif),
            "contact_sheet": sha_file(contact),
        },
        "diagnostic_limit": "This is a body-only cutout/deformation proof. Seams and rigid-part artifacts are evidence for the next deformation refinement, not accepted final animation quality."
    }
    report_path = workspace / "g3s_c0_body_walk_report.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print("G3S-C0: BODY WALK REVIEW PACKAGE READY")
    print(f"IN-PLACE GIF: {in_gif}")
    print(f"TRAVEL GIF:   {travel_gif}")
    print(f"CONTACT:      {contact}")
    print(f"REPORT:       {report_path}")
    print("STOP. Review motion before any production promotion or hair/clothing work.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
