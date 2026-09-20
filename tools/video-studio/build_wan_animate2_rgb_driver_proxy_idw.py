#!/usr/bin/env python3
"""Fast RGB driving proxy for Wan-Animate-2 using a single dense remap per frame.

This replaces the earlier triangle-by-triangle piecewise affine renderer, which
proved unacceptably slow on the local Windows/OpenCV runtime. The validated
COCO-133 driver remains canonical; this file only adapts it to the raw RGB
`pose_video` contract used by WanAnimate2ToVideo.

Method:
- reuse the validated PRIMARY anchor-selection logic;
- build a neutral-background anchor image from real local João pixels;
- choose a reduced stable set of body/face/hand controls;
- for each target frame, compute an inverse-distance-weighted target->source map
  on a coarse grid;
- upscale that map and perform exactly ONE cv2.remap for the frame;
- render only the 65-frame 4n+1 spike needed for the first Wan gate.

No DWPose and no Wan inference are invoked.
"""
from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path

import cv2
import numpy as np

import build_wan_animate2_rgb_driver_proxy as base

BG = 127


def control_arrays(anchor_kp, target_kp, control_ids):
    src = []
    dst = []
    for i in control_ids:
        sx, sy, _ = anchor_kp[i]
        tx, ty, _ = target_kp[i]
        src.append([base.clamp(float(sx), 0.0, 1.0), base.clamp(float(sy), 0.0, 1.0)])
        dst.append([base.clamp(float(tx), 0.0, 1.0), base.clamp(float(ty), 0.0, 1.0)])
    return np.asarray(src, dtype=np.float32), np.asarray(dst, dtype=np.float32)


def add_stabilizers(src, dst):
    # Keep the canvas perimeter effectively fixed so the background does not
    # become a second motion source. Duplicate rings increase their influence.
    ring = np.asarray([
        [0.00, 0.00], [0.25, 0.00], [0.50, 0.00], [0.75, 0.00], [1.00, 0.00],
        [0.00, 0.25], [1.00, 0.25],
        [0.00, 0.50], [1.00, 0.50],
        [0.00, 0.75], [1.00, 0.75],
        [0.00, 1.00], [0.25, 1.00], [0.50, 1.00], [0.75, 1.00], [1.00, 1.00],
    ], dtype=np.float32)
    src2 = np.concatenate([src, ring, ring], axis=0)
    dst2 = np.concatenate([dst, ring, ring], axis=0)
    return src2, dst2


def build_neutral_anchor(anchor_img, src_norm, width, height):
    pts = np.stack([src_norm[:, 0] * (width - 1), src_norm[:, 1] * (height - 1)], axis=1)
    pts = np.int32(np.round(pts))
    hull = cv2.convexHull(pts)
    mask = np.zeros((height, width), dtype=np.uint8)
    if hull is not None and len(hull) >= 3:
        cv2.fillConvexPoly(mask, hull, 255, lineType=cv2.LINE_8)
    # Expand enough to retain clothing/hair around landmarks, then feather.
    k = max(5, int(round(min(width, height) * 0.055)))
    if k % 2 == 0:
        k += 1
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k))
    mask = cv2.dilate(mask, kernel, iterations=1)
    blur = max(3, int(round(min(width, height) * 0.025)))
    if blur % 2 == 0:
        blur += 1
    alpha = cv2.GaussianBlur(mask, (blur, blur), 0).astype(np.float32) / 255.0
    alpha = alpha[:, :, None]
    bg = np.full_like(anchor_img, BG)
    return np.clip(anchor_img.astype(np.float32) * alpha + bg.astype(np.float32) * (1.0 - alpha), 0, 255).astype(np.uint8), mask


def idw_inverse_map(src_norm, dst_norm, width, height, grid_w=64, grid_h=114, power=2.4):
    # Build target->source mapping on a coarse normalized grid. Vectorized: no
    # per-pixel Python loops and no per-triangle OpenCV calls.
    xs = np.linspace(0.0, 1.0, grid_w, dtype=np.float32)
    ys = np.linspace(0.0, 1.0, grid_h, dtype=np.float32)
    gx, gy = np.meshgrid(xs, ys)
    q = np.stack([gx.ravel(), gy.ravel()], axis=1)  # P x 2

    # P x C distances to target controls.
    d = q[:, None, :] - dst_norm[None, :, :]
    d2 = np.sum(d * d, axis=2)
    # IDW. Epsilon prevents singularities; exact landmarks still dominate.
    w = 1.0 / np.power(d2 + 1e-5, power / 2.0)
    denom = np.sum(w, axis=1, keepdims=True)
    mapped = (w @ src_norm) / np.maximum(denom, 1e-12)

    mx = mapped[:, 0].reshape(grid_h, grid_w) * (width - 1)
    my = mapped[:, 1].reshape(grid_h, grid_w) * (height - 1)
    mapx = cv2.resize(mx.astype(np.float32), (width, height), interpolation=cv2.INTER_CUBIC)
    mapy = cv2.resize(my.astype(np.float32), (width, height), interpolation=cv2.INTER_CUBIC)
    np.clip(mapx, 0, width - 1, out=mapx)
    np.clip(mapy, 0, height - 1, out=mapy)
    return mapx, mapy


def write_contact(frames, path: Path, fps: float):
    n = 9
    ids = [int(round(i * (len(frames) - 1) / (n - 1))) for i in range(n)]
    thumbs = []
    for idx in ids:
        img = frames[idx].copy()
        cv2.putText(img, f"f={idx} t={idx/fps:.2f}s", (8, 20), cv2.FONT_HERSHEY_SIMPLEX, .38, (255,255,255), 1, cv2.LINE_AA)
        thumbs.append(cv2.resize(img, (192, 342), interpolation=cv2.INTER_AREA))
    sheet = np.full((342 * 3, 192 * 3, 3), 32, dtype=np.uint8)
    for j, img in enumerate(thumbs):
        y = (j // 3) * 342
        x = (j % 3) * 192
        sheet[y:y+342, x:x+192] = img
    cv2.imwrite(str(path), sheet)


def write_video(path: Path, frames, fps: float):
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
    ap.add_argument("--width", type=int, default=256)
    ap.add_argument("--height", type=int, default=456)
    ap.add_argument("--fps", type=float, default=24.0)
    ap.add_argument("--spike-frames", type=int, default=65)
    ap.add_argument("--ffmpeg", default="ffmpeg")
    ap.add_argument("--grid-width", type=int, default=64)
    ap.add_argument("--grid-height", type=int, default=114)
    args = ap.parse_args()

    print("stage=load_inputs", flush=True)
    lib = base.load_json(args.library)
    if lib.get("schema") != "joao-motion-library/v1":
        raise SystemExit(f"Unexpected library schema: {lib.get('schema')}")
    all_frames = base.load_track(args.pose_driver)
    if args.spike_frames < 1 or args.spike_frames > len(all_frames):
        raise SystemExit(f"--spike-frames must be 1..{len(all_frames)}")
    target_frames = all_frames[:args.spike_frames]

    args.output_dir.mkdir(parents=True, exist_ok=True)

    print("stage=select_anchor", flush=True)
    anchor = base.choose_primary_anchor(lib, target_frames)
    anchor_png = args.output_dir / "rgb_proxy_anchor_reference.png"

    print("stage=extract_anchor", flush=True)
    anchor_img = base.extract_anchor_frame(args.ffmpeg, Path(anchor["source_video"]), anchor["t"], anchor_png, args.width, args.height)

    print("stage=select_controls", flush=True)
    control_ids = base.reliable_control_indices(anchor["keypoints"], target_frames, min_target_ratio=0.90)
    if len(control_ids) < 24:
        raise SystemExit(f"Too few reliable controls for IDW proxy: {len(control_ids)}")
    anchor_src, _ = control_arrays(anchor["keypoints"], target_frames[0]["keypoints"], control_ids)
    neutral_anchor, _ = build_neutral_anchor(anchor_img, anchor_src, args.width, args.height)
    neutral_png = args.output_dir / "rgb_proxy_anchor_neutral.png"
    cv2.imwrite(str(neutral_png), neutral_anchor)

    print("WAN-ANIMATE-2 RGB DRIVER PROXY / IDW")
    print("====================================")
    print(f"Anchor source: {anchor['source_video']}")
    print(f"Anchor time: {anchor['t']:.3f}s / score={anchor['score']:.6f} / pose_match={anchor['pose_match']:.6f}")
    print(f"Anchor framing: body={anchor['body_in']:.3f} face={anchor['face_in']:.3f} hands={anchor['hand_in']:.3f}")
    print(f"Controls: {len(control_ids)}")
    print(f"Canvas: {args.width}x{args.height} @ {args.fps} fps")
    print(f"IDW grid: {args.grid_width}x{args.grid_height}; one cv2.remap per frame")
    print(f"Frames: {len(target_frames)}")
    print("stage=render", flush=True)

    frames = []
    t0 = time.perf_counter()
    for i, rec in enumerate(target_frames):
        ft0 = time.perf_counter()
        src, dst = control_arrays(anchor["keypoints"], rec["keypoints"], control_ids)
        src, dst = add_stabilizers(src, dst)
        mapx, mapy = idw_inverse_map(src, dst, args.width, args.height, args.grid_width, args.grid_height)
        frame = cv2.remap(neutral_anchor, mapx, mapy, interpolation=cv2.INTER_LINEAR,
                          borderMode=cv2.BORDER_CONSTANT, borderValue=(BG, BG, BG))
        frames.append(frame)
        frame_s = time.perf_counter() - ft0
        elapsed = time.perf_counter() - t0
        rate = elapsed / (i + 1)
        eta = rate * (len(target_frames) - i - 1)
        print(f"frame {i+1:02d}/{len(target_frames)} frame_s={frame_s:.3f} elapsed={elapsed:.1f}s eta={eta:.1f}s", flush=True)
        if i == 0 and frame_s > 15.0:
            raise SystemExit(f"IDW proxy first frame too slow ({frame_s:.1f}s); aborting instead of wasting time")

    print("stage=encode", flush=True)
    spike_video = args.output_dir / f"behavioral_driver_rgb_proxy_spike{args.spike_frames}.mp4"
    contact = args.output_dir / "behavioral_driver_rgb_proxy_contact.jpg"
    write_video(spike_video, frames, args.fps)
    write_contact(frames, contact, args.fps)

    manifest = {
        "schema": "wan-animate2-rgb-driver-proxy/v2-idw",
        "contract": "WanAnimate2ToVideo pose_video is raw RGB IMAGE frames VAE-encoded directly",
        "adapter": "coarse-grid inverse-distance target->source warp; one cv2.remap per frame",
        "library": str(args.library.resolve()),
        "pose_driver": str(args.pose_driver.resolve()),
        "width": args.width,
        "height": args.height,
        "fps": args.fps,
        "frames": len(frames),
        "spike_frames": args.spike_frames,
        "grid": [args.grid_width, args.grid_height],
        "anchor": {k: v for k, v in anchor.items() if k != "keypoints"},
        "control_point_count": len(control_ids),
        "control_indices": control_ids,
        "outputs": {
            "anchor_reference": str(anchor_png.resolve()),
            "anchor_neutral": str(neutral_png.resolve()),
            "spike_driver": str(spike_video.resolve()),
            "contact_sheet": str(contact.resolve()),
        },
        "limitations": [
            "Non-generative real-pixel proxy for motion conditioning only.",
            "Background is neutralized and canvas perimeter stabilized so source-camera/background motion is not treated as behavior.",
            "A Wan failure does not invalidate the validated pose-domain behavior library/compositor.",
        ],
    }
    manifest_path = args.output_dir / "rgb_driver_proxy_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    print("stage=complete", flush=True)
    print("RGB DRIVER PROXY / IDW: COMPLETE")
    print(f"Anchor/reference: {anchor_png}")
    print(f"Neutral anchor: {neutral_png}")
    print(f"Spike driver: {spike_video}")
    print(f"Contact sheet: {contact}")
    print(f"Manifest: {manifest_path}")
    print("Wan-Animate-2: NOT INVOKED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
