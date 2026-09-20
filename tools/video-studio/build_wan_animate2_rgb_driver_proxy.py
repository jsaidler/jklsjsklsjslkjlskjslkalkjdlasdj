#!/usr/bin/env python3
"""Build a dense RGB driving-video proxy for Wan-Animate-2 from a validated COCO-133 driver.

Wan-Animate-2 consumes raw RGB driving-video frames directly through its VAE. The
validated behavioral driver is pose-domain data, so this adapter turns it into a
human-shaped RGB proxy without invoking another generative model.

Strategy:
- select one clean real João frame automatically from eligible PRIMARY footage;
- use that real frame as a texture atlas;
- piecewise-affine warp it with a fixed Delaunay mesh driven by the synthesized
  COCO WholeBody 133 trajectory;
- keep the background neutral so acquisition geometry/background motion is not
  injected into the motion signal;
- preserve the full 24 fps driver and also emit a 65-frame 4n+1 spike clip that
  includes the complete primary->SIENA overlap.

No DWPose and no Wan inference are invoked.
"""

from __future__ import annotations

import argparse
import json
import math
import shutil
import statistics
import subprocess
from pathlib import Path

import cv2
import numpy as np

CONF = 0.20
BODY_HEAD = list(range(0, 13))
FACE = list(range(23, 91))
LEFT_HAND = list(range(91, 112))
RIGHT_HAND = list(range(112, 133))
RELEVANT = BODY_HEAD + FACE + LEFT_HAND + RIGHT_HAND


def finite(v):
    return v is not None and math.isfinite(float(v))


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def load_json(path: Path):
    if not path.is_file():
        raise SystemExit(f"Missing input: {path}")
    return json.loads(path.read_text(encoding="utf-8-sig"))


def load_track(path: Path):
    if not path.is_file():
        raise SystemExit(f"Missing pose track: {path}")
    rows = []
    for n, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        if not line.strip():
            continue
        row = json.loads(line)
        if row.get("schema") != "coco_wholebody_133" or len(row.get("keypoints") or []) != 133:
            raise SystemExit(f"Invalid COCO-133 row at {path}:{n}")
        rows.append(row)
    if not rows:
        raise SystemExit(f"Empty pose track: {path}")
    return rows


def shoulder_geom(kp):
    a, b = kp[5], kp[6]
    if not all(finite(v) for v in (*a[:3], *b[:3])):
        return None
    if float(a[2]) < CONF or float(b[2]) < CONF:
        return None
    ax, ay, bx, by = map(float, (a[0], a[1], b[0], b[1]))
    vx, vy = bx - ax, by - ay
    w = math.hypot(vx, vy)
    if w <= 1e-8:
        return None
    return {"cx": (ax + bx) / 2.0, "cy": (ay + by) / 2.0, "w": w, "angle": math.atan2(vy, vx)}


def normalized_points(kp, ids):
    g = shoulder_geom(kp)
    if g is None:
        return {}
    ca, sa = math.cos(g["angle"]), math.sin(g["angle"])
    out = {}
    for i in ids:
        x, y, c = kp[i]
        if not (finite(x) and finite(y) and finite(c) and float(c) >= CONF):
            continue
        dx, dy = float(x) - g["cx"], float(y) - g["cy"]
        out[i] = ((dx * ca + dy * sa) / g["w"], (-dx * sa + dy * ca) / g["w"])
    return out


def normalized_pose_distance(a, b):
    na, nb = normalized_points(a, BODY_HEAD + LEFT_HAND + RIGHT_HAND)
    ids = set(na) & set(nb)
    if len(ids) < 12:
        return 1.0
    return math.sqrt(statistics.fmean((na[i][0] - nb[i][0]) ** 2 + (na[i][1] - nb[i][1]) ** 2 for i in ids))


def visibility(kp, ids, margin=0.015):
    seen = 0
    inside = 0
    for i in ids:
        x, y, c = kp[i]
        if not (finite(x) and finite(y) and finite(c) and float(c) >= CONF):
            continue
        seen += 1
        if margin <= float(x) <= 1.0 - margin and margin <= float(y) <= 1.0 - margin:
            inside += 1
    return (inside / len(ids), seen / len(ids)) if ids else (0.0, 0.0)


def in_allowed_ranges(t, ranges):
    return any(a - 1e-6 <= t <= b + 1e-6 for a, b in ranges)


def choose_primary_anchor(library, target_frames):
    units = [u for u in (library.get("units") or []) if u.get("source_key") == "primary"]
    if not units:
        raise SystemExit("Unified library contains no PRIMARY units")
    source_videos = {u.get("source_video") for u in units if u.get("source_video")}
    pose_tracks = {u.get("pose_track") for u in units if u.get("pose_track")}
    if len(source_videos) != 1:
        raise SystemExit(f"Expected one PRIMARY source_video, found {sorted(str(x) for x in source_videos)}")
    if len(pose_tracks) != 1:
        raise SystemExit(f"Expected one PRIMARY pose_track, found {sorted(str(x) for x in pose_tracks)}")
    source_video = Path(next(iter(source_videos)))
    pose_track = Path(next(iter(pose_tracks)))
    if not source_video.is_file():
        raise SystemExit(f"PRIMARY source video missing: {source_video}")
    rows = load_track(pose_track)
    ranges = [(float(u["source_start_s"]), float(u["source_end_s"])) for u in units]

    # First third of the synthesized driver is PRIMARY-led and gives a stable anchor target.
    target_idx = min(len(target_frames) - 1, max(0, int(round(len(target_frames) * 0.18))))
    target = target_frames[target_idx]["keypoints"]

    best = None
    for rec in rows:
        t = float(rec["t"])
        if not in_allowed_ranges(t, ranges):
            continue
        kp = rec["keypoints"]
        if shoulder_geom(kp) is None:
            continue
        body_in, body_seen = visibility(kp, BODY_HEAD)
        face_in, face_seen = visibility(kp, FACE)
        lh_in, lh_seen = visibility(kp, LEFT_HAND)
        rh_in, rh_seen = visibility(kp, RIGHT_HAND)
        hand_in = (lh_in + rh_in) / 2.0
        hand_seen = (lh_seen + rh_seen) / 2.0
        # Require a genuinely useful texture atlas, not merely a detectable body.
        if body_seen < 0.85 or face_seen < 0.80 or hand_seen < 0.70:
            continue
        dist = normalized_pose_distance(kp, target)
        pose_match = 1.0 / (1.0 + 4.0 * dist)
        score = 0.34 * pose_match + 0.22 * body_in + 0.18 * face_in + 0.26 * hand_in
        row = {
            "score": score,
            "t": t,
            "pose_match": pose_match,
            "body_in": body_in,
            "face_in": face_in,
            "hand_in": hand_in,
            "keypoints": kp,
        }
        if best is None or row["score"] > best["score"]:
            best = row
    if best is None:
        raise SystemExit("Could not find a clean PRIMARY RGB anchor with sufficiently visible face/hands")
    best["source_video"] = str(source_video)
    best["pose_track"] = str(pose_track)
    best["target_driver_frame"] = target_idx
    return best


def extract_anchor_frame(ffmpeg, source_video: Path, t: float, output: Path, width: int, height: int):
    exe = shutil.which(ffmpeg) or ffmpeg
    output.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        exe, "-y", "-hide_banner", "-loglevel", "error",
        "-ss", f"{t:.6f}", "-i", str(source_video),
        "-frames:v", "1",
        "-vf", f"scale={width}:{height}:flags=lanczos",
        str(output),
    ]
    p = subprocess.run(cmd, capture_output=True)
    if p.returncode != 0:
        raise SystemExit("FFmpeg anchor extraction failed: " + p.stderr.decode("utf-8", "replace"))
    img = cv2.imread(str(output), cv2.IMREAD_COLOR)
    if img is None or img.shape[1] != width or img.shape[0] != height:
        raise SystemExit(f"Anchor extraction produced invalid image: {output}")
    return img


def reliable_control_indices(anchor_kp, target_frames, min_target_ratio=0.92):
    counts = {i: 0 for i in RELEVANT}
    total = len(target_frames)
    for rec in target_frames:
        kp = rec["keypoints"]
        for i in RELEVANT:
            x, y, c = kp[i]
            if finite(x) and finite(y) and finite(c) and float(c) >= CONF:
                counts[i] += 1

    # Body first, then face/hands. This ordering also decides which nearly-duplicate
    # point survives (e.g. body wrist vs hand root).
    ordered = BODY_HEAD + FACE + LEFT_HAND + RIGHT_HAND
    selected = []
    selected_xy = []
    for i in ordered:
        x, y, c = anchor_kp[i]
        if not (finite(x) and finite(y) and finite(c) and float(c) >= CONF):
            continue
        if counts[i] / max(total, 1) < min_target_ratio:
            continue
        px, py = float(x), float(y)
        if not (0.005 <= px <= 0.995 and 0.005 <= py <= 0.995):
            continue
        # Avoid Subdiv2D duplicate-point failures.
        if any((px - qx) ** 2 + (py - qy) ** 2 < (0.0025 ** 2) for qx, qy in selected_xy):
            continue
        selected.append(i)
        selected_xy.append((px, py))
    return selected


def delaunay_triangles(src_pts, width, height):
    subdiv = cv2.Subdiv2D((0, 0, width, height))
    for p in src_pts:
        subdiv.insert((float(p[0]), float(p[1])))
    raw = subdiv.getTriangleList()
    pts = np.asarray(src_pts, dtype=np.float32)
    triangles = set()
    for tr in raw:
        verts = [(float(tr[0]), float(tr[1])), (float(tr[2]), float(tr[3])), (float(tr[4]), float(tr[5]))]
        idxs = []
        ok = True
        for vx, vy in verts:
            ds = np.sum((pts - np.array([vx, vy], dtype=np.float32)) ** 2, axis=1)
            j = int(np.argmin(ds))
            if float(ds[j]) > 9.0:  # 3 px tolerance
                ok = False
                break
            idxs.append(j)
        if not ok or len(set(idxs)) != 3:
            continue
        a, b, c = pts[idxs[0]], pts[idxs[1]], pts[idxs[2]]
        area = abs(np.cross(b - a, c - a)) * 0.5
        if area < 2.0:
            continue
        triangles.add(tuple(sorted(idxs)))
    out = sorted(triangles)
    if len(out) < 20:
        raise SystemExit(f"Too few usable Delaunay triangles: {len(out)}")
    return out


def warp_triangle(src, dst, src_tri, dst_tri):
    src_tri = np.float32(src_tri)
    dst_tri = np.float32(dst_tri)
    r1 = cv2.boundingRect(src_tri)
    r2 = cv2.boundingRect(dst_tri)
    x1, y1, w1, h1 = r1
    x2, y2, w2, h2 = r2
    if w1 <= 0 or h1 <= 0 or w2 <= 0 or h2 <= 0:
        return
    if x2 < 0 or y2 < 0 or x2 + w2 > dst.shape[1] or y2 + h2 > dst.shape[0]:
        return
    src_crop = src[y1:y1+h1, x1:x1+w1]
    if src_crop.size == 0:
        return
    t1 = src_tri - np.array([x1, y1], dtype=np.float32)
    t2 = dst_tri - np.array([x2, y2], dtype=np.float32)
    M = cv2.getAffineTransform(t1, t2)
    warped = cv2.warpAffine(src_crop, M, (w2, h2), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT_101)
    mask = np.zeros((h2, w2), dtype=np.float32)
    cv2.fillConvexPoly(mask, np.int32(np.round(t2)), 1.0, lineType=cv2.LINE_AA)
    mask3 = mask[:, :, None]
    roi = dst[y2:y2+h2, x2:x2+w2].astype(np.float32)
    dst[y2:y2+h2, x2:x2+w2] = np.clip(roi * (1.0 - mask3) + warped.astype(np.float32) * mask3, 0, 255).astype(np.uint8)


def render_proxy_frame(anchor_img, anchor_kp, target_kp, control_ids, triangles, width, height, background=127):
    src_pts = []
    dst_pts = []
    for i in control_ids:
        sx, sy, _ = anchor_kp[i]
        tx, ty, _ = target_kp[i]
        src_pts.append([clamp(float(sx), 0, 1) * (width - 1), clamp(float(sy), 0, 1) * (height - 1)])
        dst_pts.append([clamp(float(tx), 0, 1) * (width - 1), clamp(float(ty), 0, 1) * (height - 1)])
    dst = np.full((height, width, 3), int(background), dtype=np.uint8)
    for ia, ib, ic in triangles:
        warp_triangle(anchor_img, dst,
                      [src_pts[ia], src_pts[ib], src_pts[ic]],
                      [dst_pts[ia], dst_pts[ib], dst_pts[ic]])
    return dst


def write_contact(frames, path: Path, fps: float):
    if not frames:
        return
    n = 9
    ids = [int(round(i * (len(frames) - 1) / (n - 1))) for i in range(n)]
    thumbs = []
    for idx in ids:
        img = frames[idx].copy()
        cv2.putText(img, f"f={idx} t={idx/fps:.2f}s", (12, 28), cv2.FONT_HERSHEY_SIMPLEX, .55, (255,255,255), 2, cv2.LINE_AA)
        small = cv2.resize(img, (256, 456), interpolation=cv2.INTER_AREA)
        thumbs.append(small)
    sheet = np.full((456 * 3, 256 * 3, 3), 32, dtype=np.uint8)
    for j, img in enumerate(thumbs):
        y = (j // 3) * 456
        x = (j % 3) * 256
        sheet[y:y+456, x:x+256] = img
    cv2.imwrite(str(path), sheet)


def write_video(path: Path, frames, fps: float):
    if not frames:
        raise SystemExit("No frames to encode")
    h, w = frames[0].shape[:2]
    vw = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))
    if not vw.isOpened():
        raise SystemExit(f"Could not open video writer: {path}")
    for frame in frames:
        vw.write(frame)
    vw.release()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--library", type=Path, required=True)
    ap.add_argument("--pose-driver", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path, required=True)
    ap.add_argument("--width", type=int, default=512)
    ap.add_argument("--height", type=int, default=912)
    ap.add_argument("--fps", type=float, default=24.0)
    ap.add_argument("--spike-frames", type=int, default=65)
    ap.add_argument("--ffmpeg", default="ffmpeg")
    args = ap.parse_args()
    if args.width <= 0 or args.height <= 0 or args.fps <= 0:
        raise SystemExit("Invalid width/height/fps")

    lib = load_json(args.library)
    if lib.get("schema") != "joao-motion-library/v1":
        raise SystemExit(f"Unexpected library schema: {lib.get('schema')}")
    target_frames = load_track(args.pose_driver)
    if args.spike_frames < 1 or args.spike_frames > len(target_frames):
        raise SystemExit(f"--spike-frames must be 1..{len(target_frames)}")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    anchor = choose_primary_anchor(lib, target_frames)
    anchor_png = args.output_dir / "rgb_proxy_anchor_reference.png"
    anchor_img = extract_anchor_frame(args.ffmpeg, Path(anchor["source_video"]), anchor["t"], anchor_png, args.width, args.height)

    control_ids = reliable_control_indices(anchor["keypoints"], target_frames)
    if len(control_ids) < 40:
        raise SystemExit(f"Too few reliable control points: {len(control_ids)}")
    src_pts = [[float(anchor["keypoints"][i][0]) * (args.width - 1), float(anchor["keypoints"][i][1]) * (args.height - 1)] for i in control_ids]
    triangles = delaunay_triangles(src_pts, args.width, args.height)

    print("WAN-ANIMATE-2 RGB DRIVER PROXY")
    print("==============================")
    print(f"Anchor source: {anchor['source_video']}")
    print(f"Anchor time: {anchor['t']:.3f}s / score={anchor['score']:.6f} / pose_match={anchor['pose_match']:.6f}")
    print(f"Anchor framing: body={anchor['body_in']:.3f} face={anchor['face_in']:.3f} hands={anchor['hand_in']:.3f}")
    print(f"Control points: {len(control_ids)} / Delaunay triangles: {len(triangles)}")
    print(f"Canvas: {args.width}x{args.height} @ {args.fps} fps")
    print("Rendering RGB motion proxy from validated COCO-133 driver...")

    frames = []
    total = len(target_frames)
    for i, rec in enumerate(target_frames):
        frames.append(render_proxy_frame(anchor_img, anchor["keypoints"], rec["keypoints"], control_ids, triangles, args.width, args.height))
        if (i + 1) % 12 == 0 or i + 1 == total:
            print(f"  progress {i+1}/{total} ({100.0*(i+1)/total:.1f}%)")

    full_video = args.output_dir / "behavioral_driver_rgb_proxy.mp4"
    spike_video = args.output_dir / f"behavioral_driver_rgb_proxy_spike{args.spike_frames}.mp4"
    contact = args.output_dir / "behavioral_driver_rgb_proxy_contact.jpg"
    write_video(full_video, frames, args.fps)
    write_video(spike_video, frames[:args.spike_frames], args.fps)
    write_contact(frames, contact, args.fps)

    manifest = {
        "schema": "wan-animate2-rgb-driver-proxy/v1",
        "contract": "WanAnimate2ToVideo pose_video is raw IMAGE frames VAE-encoded directly; this proxy is therefore RGB, not a skeleton video",
        "library": str(args.library.resolve()),
        "pose_driver": str(args.pose_driver.resolve()),
        "width": args.width,
        "height": args.height,
        "fps": args.fps,
        "frames": len(frames),
        "spike_frames": args.spike_frames,
        "anchor": {k: v for k, v in anchor.items() if k != "keypoints"},
        "control_point_count": len(control_ids),
        "control_indices": control_ids,
        "triangle_count": len(triangles),
        "outputs": {
            "anchor_reference": str(anchor_png.resolve()),
            "full_driver": str(full_video.resolve()),
            "spike_driver": str(spike_video.resolve()),
            "contact_sheet": str(contact.resolve()),
        },
        "limitations": [
            "This is a non-generative real-pixel piecewise-affine proxy, not photorealistic resynthesis.",
            "The first Wan spike tests whether the end-to-end raw-video pose branch accepts this synthesized dense motion proxy.",
            "A failure here does not invalidate the validated pose-domain behavior library/compositor.",
        ],
    }
    manifest_path = args.output_dir / "rgb_driver_proxy_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    print("")
    print("RGB DRIVER PROXY: COMPLETE")
    print(f"Anchor/reference: {anchor_png}")
    print(f"Full 108-frame driver: {full_video}")
    print(f"65-frame render-spike driver: {spike_video}")
    print(f"Contact sheet: {contact}")
    print(f"Manifest: {manifest_path}")
    print("Wan-Animate-2: NOT INVOKED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
