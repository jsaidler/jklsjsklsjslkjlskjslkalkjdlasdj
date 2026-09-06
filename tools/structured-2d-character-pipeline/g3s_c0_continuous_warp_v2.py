#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import Counter
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

EXPECTED_SIZE = (37, 128)
EXPECTED_PNG_SHA = "702e2d95325049b5d99ea66db4fbbb9b41d6d24813efb0b1c3a37e112b1c2858"
EXPECTED_RAW_SHA = "818f0538a145917eac921ad708b3cdf30f87b2c76bc1413aa59305556af7f25c"
LOGICAL = (96, 160)
BODY_ANCHOR = (29, 24)
SCENE = (640, 360)
GROUND_Y = 286

# Calibrated against the promoted B3B body. These points drive deformation only.
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

CHAINS = {
    "torso": (["pelvis", "neck"], 11.0),
    "head": (["neck", "head"], 7.0),
    "left_arm": (["left_shoulder", "left_elbow", "left_wrist"], 5.0),
    "right_arm": (["right_shoulder", "right_elbow", "right_wrist"], 5.0),
    "left_leg": (["left_hip", "left_knee", "left_ankle", "left_toe"], 7.5),
    "right_leg": (["right_hip", "right_knee", "right_ankle", "right_toe"], 7.5),
}


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def sha_raw(im: Image.Image) -> str:
    return hashlib.sha256(im.convert("RGBA").tobytes()).hexdigest()


def add(a, b):
    return (a[0] + b[0], a[1] + b[1])


def sub(a, b):
    return (a[0] - b[0], a[1] - b[1])


def angle(a, b):
    return math.atan2(b[1] - a[1], b[0] - a[0])


def wrap(a):
    while a > math.pi:
        a -= 2 * math.pi
    while a < -math.pi:
        a += 2 * math.pi
    return a


def rotate_vec(v, a):
    c, s = math.cos(a), math.sin(a)
    return (v[0] * c - v[1] * s, v[0] * s + v[1] * c)


def motion_xy(frame, name):
    j = frame["joints"][name]
    return (float(j["x"]), float(j["y"]))


def delta_angle(frame, ref, a, b):
    return wrap(
        angle(motion_xy(frame, a), motion_xy(frame, b))
        - angle(motion_xy(ref, a), motion_xy(ref, b))
    )


def target_skeleton(frame, ref):
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
        shoulder = f"{side}_shoulder"
        elbow = f"{side}_elbow"
        wrist = f"{side}_wrist"
        hip = f"{side}_hip"
        knee = f"{side}_knee"
        ankle = f"{side}_ankle"
        toe = f"{side}_toe"

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


def point_segment_distance(p, a, b):
    ax, ay = a
    bx, by = b
    px, py = p
    vx, vy = bx - ax, by - ay
    vv = vx * vx + vy * vy
    if vv <= 1e-9:
        return math.hypot(px - ax, py - ay), 0.0
    t = ((px - ax) * vx + (py - ay) * vy) / vv
    tc = max(0.0, min(1.0, t))
    qx = ax + tc * vx
    qy = ay + tc * vy
    return math.hypot(px - qx, py - qy), tc


def chain_distance(p, names):
    best = (1e9, 0, 0.0)
    for i in range(len(names) - 1):
        d, t = point_segment_distance(p, S[names[i]], S[names[i + 1]])
        if d < best[0]:
            best = (d, i, t)
    return best


def ownership_score(entity, x, y):
    names, radius = CHAINS[entity]
    d, _, _ = chain_distance((x + 0.5, y + 0.5), names)
    score = d / radius

    if entity == "head":
        score += -0.65 if y <= 48 else 1.2
    elif entity == "torso":
        if 42 <= x <= 57 and 45 <= y <= 99:
            score -= 0.70
        if y < 38:
            score += 1.0
        if y >= 104:
            score += 1.5
    elif entity == "left_arm":
        if x <= 46 and 50 <= y <= 98:
            score -= 0.30
        if x >= 52:
            score += 0.85
        if y >= 106:
            score += 1.4
    elif entity == "right_arm":
        if x >= 52 and 50 <= y <= 100:
            score -= 0.30
        if x <= 46:
            score += 0.85
        if y >= 108:
            score += 1.4
    elif entity == "left_leg":
        if y >= 86:
            score -= 0.45
        else:
            score += 1.3
        if x <= 49:
            score -= 0.12
        if x >= 57:
            score += 0.45
    elif entity == "right_leg":
        if y >= 86:
            score -= 0.45
        else:
            score += 1.3
        if x >= 49:
            score -= 0.12
        if x <= 41:
            score += 0.45
    return score


def build_owner_map(body_canvas):
    alpha = body_canvas.getchannel("A")
    ap = alpha.load()
    owner = {}
    counts = Counter()
    for y in range(LOGICAL[1]):
        for x in range(LOGICAL[0]):
            if ap[x, y] == 0:
                continue
            entity = min(CHAINS, key=lambda e: ownership_score(e, x, y))
            owner[(x, y)] = entity
            counts[entity] += 1
    missing = [e for e in CHAINS if counts[e] < 20]
    if missing:
        raise RuntimeError(
            f"implausible ownership partition; tiny entities={missing}; counts={dict(counts)}"
        )
    return owner, dict(counts)


def map_on_segment(p, sa, sb, ta, tb):
    sx, sy = sa
    ex, ey = sb
    px, py = p
    svx, svy = ex - sx, ey - sy
    sl = math.hypot(svx, svy)
    if sl <= 1e-8:
        return ta
    sux, suy = svx / sl, svy / sl
    snx, sny = -suy, sux
    relx, rely = px - sx, py - sy
    u = (relx * sux + rely * suy) / sl
    n = relx * snx + rely * sny

    tx, ty = ta
    qx, qy = tb
    tvx, tvy = qx - tx, qy - ty
    tl = math.hypot(tvx, tvy)
    if tl <= 1e-8:
        return ta
    tux, tuy = tvx / tl, tvy / tl
    tnx, tny = -tuy, tux
    return (
        tx + u * tl * tux + n * tnx,
        ty + u * tl * tuy + n * tny,
    )


def map_chain_point(p, names, target):
    candidates = []
    for i in range(len(names) - 1):
        d, t = point_segment_distance(p, S[names[i]], S[names[i + 1]])
        candidates.append((d, i, t))
    candidates.sort(key=lambda r: r[0])
    _, i, t = candidates[0]
    mapped = map_on_segment(
        p,
        S[names[i]],
        S[names[i + 1]],
        target[names[i]],
        target[names[i + 1]],
    )

    blend_radius = 5.5
    if i > 0 and t < 0.34:
        joint = S[names[i]]
        jd = math.hypot(p[0] - joint[0], p[1] - joint[1])
        if jd < blend_radius:
            alt = map_on_segment(
                p,
                S[names[i - 1]],
                S[names[i]],
                target[names[i - 1]],
                target[names[i]],
            )
            w = max(0.0, min(1.0, (blend_radius - jd) / blend_radius)) * (0.34 - t) / 0.34
            mapped = (
                mapped[0] * (1 - w) + alt[0] * w,
                mapped[1] * (1 - w) + alt[1] * w,
            )
    if i < len(names) - 2 and t > 0.66:
        joint = S[names[i + 1]]
        jd = math.hypot(p[0] - joint[0], p[1] - joint[1])
        if jd < blend_radius:
            alt = map_on_segment(
                p,
                S[names[i + 1]],
                S[names[i + 2]],
                target[names[i + 1]],
                target[names[i + 2]],
            )
            w = max(0.0, min(1.0, (blend_radius - jd) / blend_radius)) * (t - 0.66) / 0.34
            mapped = (
                mapped[0] * (1 - w) + alt[0] * w,
                mapped[1] * (1 - w) + alt[1] * w,
            )
    return mapped


def entity_depth(frame, entity):
    names, _ = CHAINS[entity]
    vals = [float(frame["joints"][n]["depth"]) for n in names if n in frame["joints"]]
    return sum(vals) / len(vals)


def warp_entity(body_canvas, owner, entity, target):
    out = Image.new("RGBA", LOGICAL, (0, 0, 0, 0))
    draw = ImageDraw.Draw(out)
    src = body_canvas.load()
    names, _ = CHAINS[entity]

    for (x, y), own in owner.items():
        if own != entity:
            continue
        color = src[x, y]
        if color[3] == 0:
            continue
        corners = [
            map_chain_point((x, y), names, target),
            map_chain_point((x + 1, y), names, target),
            map_chain_point((x + 1, y + 1), names, target),
            map_chain_point((x, y + 1), names, target),
        ]
        poly = [(int(round(px)), int(round(py))) for px, py in corners]
        draw.polygon(poly, fill=color)
    return out


def fill_pinholes(im):
    src = im.copy()
    p = src.load()
    out = src.copy()
    op = out.load()
    for y in range(1, LOGICAL[1] - 1):
        for x in range(1, LOGICAL[0] - 1):
            if p[x, y][3] != 0:
                continue
            neigh = [p[x - 1, y], p[x + 1, y], p[x, y - 1], p[x, y + 1]]
            opaque = [c for c in neigh if c[3] != 0]
            if len(opaque) >= 3:
                op[x, y] = Counter(opaque).most_common(1)[0][0]
    return out


def logical_frame(body_canvas, owner, frame, ref):
    target = target_skeleton(frame, ref)
    layers = {e: warp_entity(body_canvas, owner, e, target) for e in CHAINS}
    order = sorted(CHAINS.keys(), key=lambda e: entity_depth(frame, e), reverse=True)
    out = Image.new("RGBA", LOGICAL, (0, 0, 0, 0))
    for entity in order:
        out.alpha_composite(layers[entity])
    out = fill_pinholes(out)
    return out, target, order


def scene_frame(logical, x_center):
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


def save_gif(frames, path, duration_ms=83):
    pal = [
        f.convert("RGB").quantize(
            colors=256,
            method=Image.Quantize.FASTOCTREE,
            dither=Image.Dither.NONE,
        )
        for f in frames
    ]
    pal[0].save(
        path,
        save_all=True,
        append_images=pal[1:],
        duration=duration_ms,
        loop=0,
        disposal=2,
        optimize=False,
    )


def make_contact(frames, path, label):
    cell_w, cell_h = 320, 180
    sheet = Image.new("RGBA", (cell_w * 4, cell_h * 2), (12, 12, 15, 255))
    font = ImageFont.load_default()
    for i, fr in enumerate(frames):
        small = fr.resize((cell_w, cell_h), Image.Resampling.NEAREST)
        x = (i % 4) * cell_w
        y = (i // 4) * cell_h
        sheet.alpha_composite(small, (x, y))
        ImageDraw.Draw(sheet).text(
            (x + 8, y + 8),
            f"{label} frame {i}",
            fill=(235, 235, 240),
            font=font,
        )
    sheet.convert("RGB").save(path)


def make_zoom_contact(logical_frames, path):
    cell_w, cell_h = 240, 320
    sheet = Image.new("RGBA", (cell_w * 4, cell_h * 2), (18, 18, 21, 255))
    font = ImageFont.load_default()
    for i, lf in enumerate(logical_frames):
        bbox = lf.getchannel("A").getbbox()
        if bbox is None:
            raise RuntimeError(f"empty logical frame {i}")
        crop = lf.crop(bbox)
        zoom = crop.resize((crop.width * 4, crop.height * 4), Image.Resampling.NEAREST)
        x0 = (i % 4) * cell_w
        y0 = (i // 4) * cell_h
        x = x0 + (cell_w - zoom.width) // 2
        y = y0 + max(24, (cell_h - zoom.height) // 2)
        sheet.alpha_composite(zoom, (x, y))
        ImageDraw.Draw(sheet).text(
            (x0 + 6, y0 + 6),
            f"V2 frame {i}",
            fill=(235, 235, 240),
            font=font,
        )
    sheet.convert("RGB").save(path)


def connected_components(alpha):
    pix = alpha.load()
    seen = set()
    comps = []
    w, h = alpha.size
    for y in range(h):
        for x in range(w):
            if pix[x, y] == 0 or (x, y) in seen:
                continue
            stack = [(x, y)]
            seen.add((x, y))
            n = 0
            while stack:
                cx, cy = stack.pop()
                n += 1
                for nx, ny in (
                    (cx - 1, cy),
                    (cx + 1, cy),
                    (cx, cy - 1),
                    (cx, cy + 1),
                ):
                    if (
                        0 <= nx < w
                        and 0 <= ny < h
                        and pix[nx, ny] != 0
                        and (nx, ny) not in seen
                    ):
                        seen.add((nx, ny))
                        stack.append((nx, ny))
            comps.append(n)
    return sorted(comps, reverse=True)


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

    body = Image.open(body_path).convert("RGBA")
    if body.size != EXPECTED_SIZE:
        raise RuntimeError(f"body dimensions changed: {body.size}")
    if sha_file(body_path) != EXPECTED_PNG_SHA or sha_raw(body) != EXPECTED_RAW_SHA:
        raise RuntimeError("canonical B3B body hash mismatch")

    motion = json.loads(motion_path.read_text(encoding="utf-8-sig"))
    frames = motion.get("frames", [])
    if len(frames) != 8:
        raise RuntimeError(f"expected 8 real-motion frames, got {len(frames)}")

    body_canvas = Image.new("RGBA", LOGICAL, (0, 0, 0, 0))
    body_canvas.alpha_composite(body, BODY_ANCHOR)
    owner, counts = build_owner_map(body_canvas)

    ref = frames[0]
    logical_frames = []
    qa = []
    for i, frame in enumerate(frames):
        lf, _, order = logical_frame(body_canvas, owner, frame, ref)
        logical_frames.append(lf)
        lf.save(workspace / f"g3s_c0_v2_body_frame_{i:02d}.png")
        comps = connected_components(lf.getchannel("A"))
        qa.append(
            {
                "frame_index": i,
                "source_motion_frame": int(frame["frame"]),
                "alpha_bbox": list(lf.getchannel("A").getbbox() or ()),
                "connected_components": comps[:8],
                "dominant_component_ratio": (comps[0] / sum(comps)) if comps else 0.0,
                "depth_order_far_to_near": order,
            }
        )

    in_place = [scene_frame(lf, 320) for lf in logical_frames]
    travel = [scene_frame(lf, 250 + i * (140.0 / 7.0)) for i, lf in enumerate(logical_frames)]

    in_gif = workspace / "g3s_c0_v2_body_walk_in_place.gif"
    travel_gif = workspace / "g3s_c0_v2_body_walk_travel.gif"
    contact = workspace / "g3s_c0_v2_contact_sheet.png"
    zoom_contact = workspace / "g3s_c0_v2_zoom_contact_sheet.png"
    report_path = workspace / "g3s_c0_v2_report.json"

    save_gif(in_place, in_gif)
    save_gif(travel, travel_gif)
    make_contact(in_place, contact, "C0 V2")
    make_zoom_contact(logical_frames, zoom_contact)

    report = {
        "gate": "G3S-C0",
        "revision": "CONTINUOUS_CHAIN_WARP_V2",
        "status": "REVIEW_REQUIRED",
        "canonical_body_png_sha256": sha_file(body_path),
        "canonical_body_raw_rgba_sha256": sha_raw(body),
        "motion_revision": motion.get("revision"),
        "source_motion": motion.get("source_motion"),
        "source_frames": [int(f["frame"]) for f in frames],
        "method": "continuous chain warp per persistent body region; source pixels rasterized as nearest-grid quads; no independent rigid limb slabs",
        "owner_pixel_counts": counts,
        "frame_qa": qa,
        "hidden_3d_rgb_used": False,
        "per_frame_diffusion": False,
        "new_visual_colors_synthesized": False,
        "canonical_body_modified": False,
        "automatic_promotion": False,
        "outputs": {
            "in_place_gif": str(in_gif),
            "travel_gif": str(travel_gif),
            "contact_sheet": str(contact),
            "zoom_contact_sheet": str(zoom_contact),
        },
    }
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print("G3S-C0 V2: REVIEW PACKAGE READY")
    print(f"IN-PLACE: {in_gif}")
    print(f"TRAVEL:   {travel_gif}")
    print(f"CONTACT:  {contact}")
    print(f"ZOOM:     {zoom_contact}")
    print(f"REPORT:   {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
