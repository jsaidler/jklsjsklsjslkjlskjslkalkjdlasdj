#!/usr/bin/env python3
import argparse
import glob
import hashlib
import json
import os
import shutil
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone


def fail(message, code=2):
    print(f"W1G: FAIL - {message}", file=sys.stderr, flush=True)
    raise SystemExit(code)


def request_json(url, payload=None, timeout=120):
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            raw = response.read()
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", "replace")
        raise RuntimeError(f"HTTP {exc.code} from {url}: {body}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Could not reach {url}: {exc}") from exc
    return json.loads(raw.decode("utf-8")) if raw else {}


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def newest_output(comfy_root, prefix, since_epoch):
    output_root = os.path.join(comfy_root, "output")
    patterns = [
        os.path.join(output_root, prefix + "*.mp4"),
        os.path.join(output_root, prefix + "*.mkv"),
        os.path.join(output_root, prefix + "*.webm"),
        os.path.join(output_root, "video", os.path.basename(prefix) + "*.mp4"),
        os.path.join(output_root, "video", os.path.basename(prefix) + "*.mkv"),
        os.path.join(output_root, "video", os.path.basename(prefix) + "*.webm"),
    ]
    candidates = []
    for pattern in patterns:
        candidates.extend(glob.glob(pattern))
    candidates = [p for p in candidates if os.path.getmtime(p) >= since_epoch - 2]
    return max(candidates, key=os.path.getmtime) if candidates else None


def _iou(a, b):
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    ax1, ay1 = ax + aw, ay + ah
    bx1, by1 = bx + bw, by + bh
    ix0, iy0 = max(ax, bx), max(ay, by)
    ix1, iy1 = min(ax1, bx1), min(ay1, by1)
    iw, ih = max(0.0, ix1 - ix0), max(0.0, iy1 - iy0)
    inter = iw * ih
    union = aw * ah + bw * bh - inter
    return inter / union if union > 0 else 0.0


def _interpolate_series(values, np):
    arr = np.asarray(values, dtype=np.float64)
    xx = np.arange(len(arr), dtype=np.float64)
    valid = np.isfinite(arr)
    if valid.sum() == 0:
        raise ValueError("no valid samples")
    if valid.sum() == 1:
        arr[:] = arr[valid][0]
        return arr
    return np.interp(xx, xx[valid], arr[valid])


def _smooth_series(values, np, radius=3):
    arr = np.asarray(values, dtype=np.float64)
    if len(arr) <= 2 or radius <= 0:
        return arr
    kernel = np.arange(1, radius + 2, dtype=np.float64)
    kernel = np.concatenate([kernel, kernel[-2::-1]])
    kernel /= kernel.sum()
    padded = np.pad(arr, (radius, radius), mode="edge")
    return np.convolve(padded, kernel, mode="valid")


def _choose_foreground_box(components, frame_w, frame_h, previous=None):
    if not components:
        return None
    frame_area = float(frame_w * frame_h)
    best = None
    best_score = -1e18
    for x, y, w, h, area in components:
        box_area = float(w * h)
        box_ratio = box_area / frame_area
        if box_ratio < 0.003 or box_ratio > 0.78:
            continue
        cx = x + w / 2.0
        cy = y + h / 2.0
        center_penalty = abs(cx - frame_w / 2.0) / frame_w + 0.25 * abs(cy - frame_h / 2.0) / frame_h
        continuity = 0.0
        if previous is not None:
            continuity += 3.0 * _iou((x, y, w, h), previous)
            pcx = previous[0] + previous[2] / 2.0
            pcy = previous[1] + previous[3] / 2.0
            dist = ((cx - pcx) ** 2 + (cy - pcy) ** 2) ** 0.5
            continuity -= 1.0 * dist / max(frame_w, frame_h)
        density = float(area) / max(1.0, box_area)
        score = 3.0 * box_ratio + 0.8 * density - 0.30 * center_penalty + continuity
        if score > best_score:
            best_score = score
            best = (float(x), float(y), float(w), float(h))
    return best


def _merge_nearby_components(primary, components, frame_w, frame_h):
    if primary is None:
        return None
    px, py, pw, ph = primary
    gx = max(10.0, pw * 0.45)
    gy = max(10.0, ph * 0.35)
    rx0, ry0 = px - gx, py - gy
    rx1, ry1 = px + pw + gx, py + ph + gy
    x0, y0, x1, y1 = px, py, px + pw, py + ph
    for x, y, w, h, area in components:
        cx = x + w / 2.0
        cy = y + h / 2.0
        if rx0 <= cx <= rx1 and ry0 <= cy <= ry1:
            x0 = min(x0, x)
            y0 = min(y0, y)
            x1 = max(x1, x + w)
            y1 = max(y1, y + h)
    x0 = max(0.0, x0)
    y0 = max(0.0, y0)
    x1 = min(float(frame_w), x1)
    y1 = min(float(frame_h), y1)
    return (x0, y0, max(1.0, x1 - x0), max(1.0, y1 - y0))


def build_subject_framed_driver(
    src,
    dst,
    manifest_path,
    analysis_frames,
    target_w=640,
    target_h=800,
    target_subject_height_ratio=0.48,
    target_center_x=300.0,
    target_bottom_y=620.0,
):
    try:
        import cv2
        import numpy as np
    except Exception as exc:
        fail(f"OpenCV/numpy unavailable in the ComfyUI Python environment: {exc}")

    cap = cv2.VideoCapture(src)
    if not cap.isOpened():
        fail(f"could not open source driver: {src}")

    src_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    src_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = float(cap.get(cv2.CAP_PROP_FPS) or 0.0)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    if src_w <= 0 or src_h <= 0:
        cap.release()
        fail(f"invalid source driver dimensions: {src_w}x{src_h}")
    if fps <= 0:
        fps = 16.0

    n = min(max(8, int(analysis_frames)), frame_count if frame_count > 0 else int(analysis_frames))
    frames = []
    corner_samples = []
    for _ in range(n):
        ok, frame = cap.read()
        if not ok:
            break
        frames.append(frame)
        h, w = frame.shape[:2]
        s = max(4, min(h, w) // 24)
        corners = np.concatenate(
            [
                frame[:s, :s].reshape(-1, 3),
                frame[:s, -s:].reshape(-1, 3),
                frame[-s:, :s].reshape(-1, 3),
                frame[-s:, -s:].reshape(-1, 3),
            ],
            axis=0,
        )
        corner_samples.append(np.median(corners, axis=0))

    if len(frames) < 8:
        cap.release()
        fail(f"not enough source frames for automatic subject analysis: {len(frames)}")

    # V1 unioned all temporal activity and collapsed to the whole frame.
    # V2 used a HOG *person* detector, which is semantically too brittle for the
    # production contract (drivers may be arbitrary and poses may be non-upright).
    # V3 is detector-agnostic for this fixed-camera official baseline: estimate a
    # temporal-median background, segment foreground independently per frame, track
    # the dominant coherent component, interpolate misses, smooth translation only,
    # and keep one constant scale for the whole clip.
    stack = np.stack(frames, axis=0)
    background = np.median(stack, axis=0).astype(np.uint8)
    frame_area = float(src_w * src_h)
    detections = []
    detection_indices = []
    global_activity_indices = []
    thresholds = []
    foreground_ratios = []
    previous = None

    kernel_open = np.ones((3, 3), np.uint8)
    kernel_close = np.ones((9, 9), np.uint8)
    kernel_dilate = np.ones((7, 7), np.uint8)

    for idx, frame in enumerate(frames):
        diff = cv2.absdiff(frame, background)
        activity = np.max(diff, axis=2).astype(np.uint8)
        activity = cv2.GaussianBlur(activity, (5, 5), 0)
        otsu, _ = cv2.threshold(activity, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        threshold_used = int(max(18, min(96, round(float(otsu)))))
        thresholds.append(threshold_used)
        _, mask = cv2.threshold(activity, threshold_used, 255, cv2.THRESH_BINARY)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel_open)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel_close)
        mask = cv2.dilate(mask, kernel_dilate, iterations=1)

        fg_ratio = float(np.count_nonzero(mask)) / frame_area
        foreground_ratios.append(fg_ratio)
        if fg_ratio > 0.72:
            global_activity_indices.append(idx)
            detections.append(None)
            continue

        num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=8)
        components = []
        for label in range(1, num_labels):
            x, y, w, h, area = [int(v) for v in stats[label]]
            if area < max(80, int(frame_area * 0.0015)):
                continue
            components.append((x, y, w, h, area))

        chosen = _choose_foreground_box(components, src_w, src_h, previous=previous)
        chosen = _merge_nearby_components(chosen, components, src_w, src_h)
        detections.append(chosen)
        if chosen is not None:
            previous = chosen
            detection_indices.append(idx)

    print(
        f"W1G: foreground tracker diagnostics: detected={len(detection_indices)}/{len(frames)} "
        f"global_activity_frames={len(global_activity_indices)} "
        f"median_threshold={float(np.median(thresholds)):.1f} "
        f"median_foreground_ratio={float(np.median(foreground_ratios)):.3f}",
        flush=True,
    )

    min_required = max(6, int(round(len(frames) * 0.16)))
    if len(detection_indices) < min_required:
        cap.release()
        fail(
            "automatic detector-agnostic foreground tracker found too few credible subject boxes "
            f"({len(detection_indices)}/{len(frames)}, need {min_required}); "
            f"global-activity frames={global_activity_indices}"
        )

    xs = [d[0] if d else float("nan") for d in detections]
    ys = [d[1] if d else float("nan") for d in detections]
    ws = [d[2] if d else float("nan") for d in detections]
    hs = [d[3] if d else float("nan") for d in detections]
    try:
        xs = _interpolate_series(xs, np)
        ys = _interpolate_series(ys, np)
        ws = _interpolate_series(ws, np)
        hs = _interpolate_series(hs, np)
    except ValueError as exc:
        cap.release()
        fail(f"foreground track interpolation failed: {exc}")

    # Foreground masks often cover the actively moving portion rather than every
    # static pixel of the performer. Expand asymmetrically for head/hair, hands and feet.
    expanded_x0 = xs - ws * 0.25
    expanded_x1 = xs + ws * 1.25
    expanded_y0 = ys - hs * 0.30
    expanded_y1 = ys + hs * 1.18
    expanded_w = expanded_x1 - expanded_x0
    expanded_h = expanded_y1 - expanded_y0
    expanded_cx = (expanded_x0 + expanded_x1) / 2.0
    expanded_bottom = expanded_y1

    robust_h = float(np.percentile(expanded_h, 90.0))
    robust_w = float(np.percentile(expanded_w, 90.0))
    desired_h = target_h * float(target_subject_height_ratio)
    scale = min(desired_h / robust_h, (target_w * 0.50) / robust_w)
    if not np.isfinite(scale) or scale <= 0:
        cap.release()
        fail("automatic foreground tracking produced an invalid constant scale")

    tracked_center = _smooth_series(expanded_cx, np, radius=3)
    tracked_bottom = _smooth_series(expanded_bottom, np, radius=3)
    tx = float(target_center_x) - scale * tracked_center
    ty = float(target_bottom_y) - scale * tracked_bottom

    out_x0 = scale * expanded_x0 + tx
    out_x1 = scale * expanded_x1 + tx
    out_y0 = scale * expanded_y0 + ty
    out_y1 = scale * expanded_y1 + ty

    margins_per_frame = {
        "left": out_x0,
        "top": out_y0,
        "right": target_w - out_x1,
        "bottom": target_h - out_y1,
    }
    min_margins = {k: round(float(np.min(v)), 2) for k, v in margins_per_frame.items()}

    clip_crop_top = (target_h - target_w) / 2.0
    clip_crop_bottom = clip_crop_top + target_w
    min_clip_margins = {
        "top_inside_center_square": round(float(np.min(out_y0 - clip_crop_top)), 2),
        "bottom_inside_center_square": round(float(np.min(clip_crop_bottom - out_y1)), 2),
        "left": min_margins["left"],
        "right": min_margins["right"],
    }

    print(
        f"W1G: framing diagnostics: constant_scale={scale:.4f} "
        f"min_output_margins={min_margins} "
        f"min_clip_margins={min_clip_margins}",
        flush=True,
    )

    guard_failures = []
    if min_margins["top"] < 70:
        guard_failures.append(f"top margin {min_margins['top']} < 70")
    if min_margins["bottom"] < 70:
        guard_failures.append(f"bottom margin {min_margins['bottom']} < 70")
    if min_margins["left"] < 55:
        guard_failures.append(f"left margin {min_margins['left']} < 55")
    if min_margins["right"] < 55:
        guard_failures.append(f"right margin {min_margins['right']} < 55")
    if min_clip_margins["top_inside_center_square"] < 16:
        guard_failures.append(
            f"CLIP center-crop top margin {min_clip_margins['top_inside_center_square']} < 16"
        )
    if min_clip_margins["bottom_inside_center_square"] < 16:
        guard_failures.append(
            f"CLIP center-crop bottom margin {min_clip_margins['bottom_inside_center_square']} < 16"
        )
    if guard_failures:
        cap.release()
        fail("FAIL_PREINFER_MARGIN_GUARD: " + "; ".join(guard_failures))

    pad_bgr = (
        np.median(np.stack(corner_samples, axis=0), axis=0).astype(np.uint8)
        if corner_samples
        else np.array([32, 32, 32], dtype=np.uint8)
    )
    border_value = tuple(int(v) for v in pad_bgr.tolist())

    os.makedirs(os.path.dirname(dst), exist_ok=True)
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    writer = cv2.VideoWriter(dst, cv2.VideoWriter_fourcc(*"mp4v"), fps, (target_w, target_h))
    if not writer.isOpened():
        cap.release()
        fail(f"could not create subject-framed driver: {dst}")

    written = 0
    interpolation = cv2.INTER_AREA if scale < 1.0 else cv2.INTER_LINEAR
    while written < len(frames):
        ok, frame = cap.read()
        if not ok:
            break
        matrix = np.array([[scale, 0.0, tx[written]], [0.0, scale, ty[written]]], dtype=np.float32)
        warped = cv2.warpAffine(
            frame,
            matrix,
            (target_w, target_h),
            flags=interpolation,
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=border_value,
        )
        writer.write(warped)
        written += 1

    cap.release()
    writer.release()
    if written != len(frames) or written <= 0 or not os.path.isfile(dst) or os.path.getsize(dst) <= 0:
        fail(f"subject-framing preprocessor wrote {written}/{len(frames)} analyzed frames")

    manifest = {
        "gate": "W1G_SUBJECT_FRAMING_V3_FOREGROUND_TRACKED_TRANSLATION",
        "status": "PASS_DRIVER_READY",
        "method": "temporal-median background + per-frame foreground segmentation + coherent component tracking + interpolation + smoothed translation; constant scale; no per-frame zoom",
        "source_width": src_w,
        "source_height": src_h,
        "source_fps": fps,
        "source_frame_count": frame_count,
        "analysis_frames": len(frames),
        "detected_frames": len(detection_indices),
        "detected_frame_indices": detection_indices,
        "global_activity_frame_indices": global_activity_indices,
        "median_activity_threshold": float(np.median(thresholds)),
        "median_foreground_ratio": float(np.median(foreground_ratios)),
        "target_width": target_w,
        "target_height": target_h,
        "target_subject_height_ratio": target_subject_height_ratio,
        "target_center_x": target_center_x,
        "target_bottom_y": target_bottom_y,
        "constant_scale": float(scale),
        "robust_expanded_subject_height": robust_h,
        "robust_expanded_subject_width": robust_w,
        "min_output_margins": min_margins,
        "min_clipvision_center_crop_margins": min_clip_margins,
        "pad_bgr": [int(v) for v in pad_bgr.tolist()],
        "written_frames": written,
        "policy": "track the visible moving subject without assuming person/cat/dog identity; follow translation with temporal smoothing, keep constant scale, and enforce subject safety in both 640x800 pose-video and center-square CLIP pose crop",
    }
    with open(manifest_path, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, ensure_ascii=False, indent=2)
    return manifest


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workspace", required=True)
    ap.add_argument("--comfy-root", required=True)
    ap.add_argument("--port", type=int, default=8188)
    ap.add_argument("--timeout-minutes", type=int, default=240)
    ap.add_argument("--target-subject-height-ratio", type=float, default=0.48)
    ap.add_argument("--target-center-x", type=float, default=300.0)
    ap.add_argument("--target-bottom-y", type=float, default=620.0)
    args = ap.parse_args()

    workspace = os.path.abspath(args.workspace)
    comfy_root = os.path.abspath(args.comfy_root)
    base = f"http://127.0.0.1:{args.port}"

    if not (0.30 <= args.target_subject_height_ratio <= 0.70):
        fail("target-subject-height-ratio must be between 0.30 and 0.70")

    parent_prompt_path = os.path.join(workspace, "w1a_api_prompt.json")
    parent_manifest_path = os.path.join(workspace, "w1a_run_manifest.json")
    for path in (parent_prompt_path, parent_manifest_path):
        if not os.path.isfile(path):
            fail(f"required W1A evidence missing: {path}")

    with open(parent_manifest_path, "r", encoding="utf-8-sig") as fh:
        parent_manifest = json.load(fh)
    if parent_manifest.get("status") != "INFERENCE_COMPLETE":
        fail(f"W1A manifest is not complete: {parent_manifest.get('status')}")
    if float(parent_manifest.get("reference_image_strength", -1)) != 1.5:
        fail("W1G must branch from W1A reference_image_strength=1.5")

    with open(parent_prompt_path, "r", encoding="utf-8-sig") as fh:
        raw_prompt = json.load(fh)
    prompt = raw_prompt.get("prompt") if isinstance(raw_prompt, dict) and "prompt" in raw_prompt else raw_prompt
    if not isinstance(prompt, dict) or not prompt:
        fail("w1a_api_prompt.json does not contain a usable ComfyUI API prompt")

    wan_nodes = [(nid, node) for nid, node in prompt.items() if node.get("class_type") == "WanAnimate2ToVideo"]
    if len(wan_nodes) != 1:
        fail(f"expected exactly one WanAnimate2ToVideo node, found {len(wan_nodes)}")
    wan_node_id, wan_node = wan_nodes[0]
    if float(wan_node.get("inputs", {}).get("reference_image_strength", -1)) != 1.5:
        fail("W1A prompt unexpectedly does not use reference_image_strength 1.5")

    driver_rel = parent_manifest.get("driver")
    if not driver_rel:
        fail("W1A manifest does not identify its source driver")
    input_root = os.path.join(comfy_root, "input")
    driver_abs = os.path.join(input_root, *driver_rel.replace("\\", "/").split("/"))
    if not os.path.isfile(driver_abs):
        fail(f"source driver missing: {driver_abs}")

    length = int(parent_manifest.get("length") or 37)
    subject_rel = "wan_animate2_w1g/official_demo1_template_subjectframed_ref15.mp4"
    subject_abs = os.path.join(input_root, *subject_rel.split("/"))
    subject_manifest_path = os.path.join(workspace, "w1g_subject_driver_manifest.json")
    prep = build_subject_framed_driver(
        driver_abs,
        subject_abs,
        subject_manifest_path,
        analysis_frames=length,
        target_w=640,
        target_h=800,
        target_subject_height_ratio=args.target_subject_height_ratio,
        target_center_x=args.target_center_x,
        target_bottom_y=args.target_bottom_y,
    )
    prep["source_sha256"] = sha256_file(driver_abs)
    prep["subject_driver_sha256"] = sha256_file(subject_abs)
    prep["subject_driver_bytes"] = os.path.getsize(subject_abs)
    with open(subject_manifest_path, "w", encoding="utf-8") as fh:
        json.dump(prep, fh, ensure_ascii=False, indent=2)

    print(f"W1G: subject-framed driver prepared at {subject_abs}", flush=True)
    print(
        f"W1G: detected_frames={prep['detected_frames']}/{prep['analysis_frames']} "
        f"constant_scale={prep['constant_scale']:.4f}",
        flush=True,
    )
    print(
        f"W1G: min output margins={prep['min_output_margins']} "
        f"CLIP-center-crop margins={prep['min_clipvision_center_crop_margins']}",
        flush=True,
    )

    load_video_nodes = [(nid, node) for nid, node in prompt.items() if node.get("class_type") == "LoadVideo"]
    matches = []
    for nid, node in load_video_nodes:
        for key, value in node.get("inputs", {}).items():
            if isinstance(value, str) and value.replace("\\", "/") == driver_rel.replace("\\", "/"):
                matches.append((nid, key))
    if len(matches) != 1:
        fail(f"could not uniquely resolve W1A LoadVideo driver field: {matches}")
    video_node_id, video_key = matches[0]
    prompt[video_node_id]["inputs"][video_key] = subject_rel

    save_nodes = [(nid, node) for nid, node in prompt.items() if node.get("class_type") == "SaveVideo"]
    if len(save_nodes) != 1:
        fail(f"expected exactly one SaveVideo node, found {len(save_nodes)}")
    save_node_id, save_node = save_nodes[0]
    new_prefix = "roguelite_w1g/wan_animate2_bf16_exilada_subjectframed_ref15"
    prefix_keys = [k for k, v in save_node.get("inputs", {}).items() if isinstance(v, str) and "roguelite_w1" in v]
    if len(prefix_keys) != 1:
        fail(f"could not uniquely resolve W1A SaveVideo prefix field: {prefix_keys}")
    save_node["inputs"][prefix_keys[0]] = new_prefix

    prompt_out = os.path.join(workspace, "w1g_api_prompt.json")
    with open(prompt_out, "w", encoding="utf-8") as fh:
        json.dump(prompt, fh, ensure_ascii=False, indent=2)

    print(
        "W1G: submitting exact W1A structural branch with only detector-agnostic tracked subject-framing replacing driver geometry...",
        flush=True,
    )
    started = time.time()
    response = request_json(base + "/prompt", {"prompt": prompt}, timeout=120)
    prompt_id = response.get("prompt_id")
    if not prompt_id:
        fail(f"ComfyUI did not return prompt_id: {response}")
    print(f"W1G: prompt_id={prompt_id}", flush=True)

    deadline = started + args.timeout_minutes * 60
    next_report = started + 60
    while time.time() < deadline:
        history = request_json(base + f"/history/{prompt_id}", timeout=120)
        item = history.get(prompt_id) if isinstance(history, dict) else None
        if item:
            status = item.get("status") or {}
            for message in status.get("messages") or []:
                if isinstance(message, (list, tuple)) and message and message[0] == "execution_error":
                    fail(f"ComfyUI execution_error: {message}")
            if status.get("completed") is True:
                break
        now = time.time()
        if now >= next_report:
            print(f"W1G: inference running for {int(now - started)} seconds...", flush=True)
            next_report = now + 60
        time.sleep(5)
    else:
        fail(f"timeout after {args.timeout_minutes} minutes")

    elapsed = round(time.time() - started, 2)
    output_path = newest_output(comfy_root, new_prefix, started)
    if not output_path:
        fail(f"ComfyUI completed prompt {prompt_id} but no new video matching {new_prefix} was found")

    canonical_output = os.path.join(workspace, "w1g_exilada_subject_framed_ref15.mp4")
    shutil.copy2(output_path, canonical_output)

    manifest = dict(parent_manifest)
    manifest.update(
        {
            "gate": "WAN_ANIMATE2_W1G_BF16_EXILADA_SUBJECT_FRAMING_REF15",
            "status": "INFERENCE_COMPLETE",
            "created_utc": datetime.now(timezone.utc).isoformat(),
            "parent_w1a_prompt_id": parent_manifest.get("prompt_id"),
            "driver": subject_rel,
            "driver_preprocess": prep,
            "reference_image_strength": 1.5,
            "prompt_file": prompt_out,
            "save_node": save_node_id,
            "wan_node": wan_node_id,
            "output_prefix": new_prefix,
            "prompt_id": prompt_id,
            "elapsed_seconds": elapsed,
            "comfy_output": output_path,
            "canonical_output": canonical_output,
            "output_bytes": os.path.getsize(canonical_output),
            "output_sha256": sha256_file(canonical_output),
            "changed_from_w1a": ["driver_preprocess_detector_agnostic_subject_tracking", "output_prefix"],
            "unchanged_from_w1a": [
                "reference_image",
                "positive_prompt",
                "negative_prompt",
                "main_model",
                "text_encoder",
                "clip_vision",
                "vae",
                "resolution",
                "frame_count",
                "fps",
                "steps",
                "cfg",
                "sampler",
                "scheduler",
                "shift",
                "seed",
                "pose_strength",
                "reference_image_strength",
            ],
            "hypothesis": "W1G v3 tracks the visible moving subject without assuming a human detector, interpolates misses, smooths translation, and uses one constant scale. This should remove source-frame traversal from conditioning while preserving W1A reference strength 1.5 and avoiding zoom breathing.",
        }
    )
    manifest_path = os.path.join(workspace, "w1g_run_manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, ensure_ascii=False, indent=2)

    print(f"W1G: PASS - generated {canonical_output}", flush=True)
    print(f"W1G: manifest {manifest_path}", flush=True)
    print(f"W1G: driver manifest {subject_manifest_path}", flush=True)
    print(f"W1G: elapsed {elapsed} seconds", flush=True)


if __name__ == "__main__":
    main()
