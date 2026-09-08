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


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def build_subject_framed_driver(src, dst, manifest_path, analysis_frames, target_w=640, target_h=800,
                                target_subject_height_ratio=0.48, target_center_x=300.0,
                                target_bottom_y=620.0):
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
        corners = np.concatenate([
            frame[:s, :s].reshape(-1, 3),
            frame[:s, -s:].reshape(-1, 3),
            frame[-s:, :s].reshape(-1, 3),
            frame[-s:, -s:].reshape(-1, 3),
        ], axis=0)
        corner_samples.append(np.median(corners, axis=0))

    if len(frames) < 8:
        cap.release()
        fail(f"not enough source frames for automatic subject analysis: {len(frames)}")

    stack_gray = np.stack([cv2.cvtColor(f, cv2.COLOR_BGR2GRAY) for f in frames], axis=0).astype(np.float32)
    std_map = np.std(stack_gray, axis=0)
    p99 = float(np.percentile(std_map, 99.0))
    if p99 <= 1e-6:
        cap.release()
        fail("automatic subject analysis found essentially no temporal activity in the driver")

    activity_u8 = np.clip(std_map * (255.0 / p99), 0, 255).astype(np.uint8)
    otsu, activity_mask = cv2.threshold(activity_u8, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    min_threshold = max(18, int(round(otsu)))
    _, activity_mask = cv2.threshold(activity_u8, min_threshold, 255, cv2.THRESH_BINARY)
    activity_mask = cv2.morphologyEx(activity_mask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    activity_mask = cv2.morphologyEx(activity_mask, cv2.MORPH_CLOSE, np.ones((15, 15), np.uint8))
    activity_mask = cv2.dilate(activity_mask, np.ones((11, 11), np.uint8), iterations=1)

    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(activity_mask, connectivity=8)
    components = []
    frame_area = src_w * src_h
    for label in range(1, num_labels):
        x, y, w, h, area = [int(v) for v in stats[label]]
        if area < max(64, int(frame_area * 0.0015)):
            continue
        components.append((area, x, y, w, h))
    if not components:
        cap.release()
        fail("automatic subject analysis found no credible moving component")

    components.sort(reverse=True)
    _, ax, ay, aw, ah = components[0]

    # Merge nearby temporal-activity components into one movement envelope. This keeps
    # a fixed camera transform for the whole clip and avoids per-frame camera breathing.
    ex0, ey0, ex1, ey1 = ax, ay, ax + aw, ay + ah
    grow_x = max(12, int(round(aw * 0.35)))
    grow_y = max(12, int(round(ah * 0.35)))
    region = (ax - grow_x, ay - grow_y, ax + aw + grow_x, ay + ah + grow_y)
    for area, x, y, w, h in components[1:]:
        cx = x + w / 2.0
        cy = y + h / 2.0
        if region[0] <= cx <= region[2] and region[1] <= cy <= region[3]:
            ex0 = min(ex0, x)
            ey0 = min(ey0, y)
            ex1 = max(ex1, x + w)
            ey1 = max(ey1, y + h)

    raw_bbox = [int(ex0), int(ey0), int(ex1 - ex0), int(ey1 - ey0)]

    # Expand beyond the motion envelope to include static body mass, head/hair and feet.
    x, y, w, h = raw_bbox
    side = int(round(w * 0.28))
    top = int(round(h * 0.34))
    bottom = int(round(h * 0.24))
    sx0 = clamp(x - side, 0, src_w - 1)
    sy0 = clamp(y - top, 0, src_h - 1)
    sx1 = clamp(x + w + side, sx0 + 2, src_w)
    sy1 = clamp(y + h + bottom, sy0 + 2, src_h)
    subject_bbox = [int(sx0), int(sy0), int(sx1 - sx0), int(sy1 - sy0)]

    bx, by, bw, bh = subject_bbox
    bbox_area_ratio = (bw * bh) / float(frame_area)
    if bh < src_h * 0.12 or bw < src_w * 0.08:
        cap.release()
        fail(f"automatic subject bbox is implausibly small: {subject_bbox}")
    if bbox_area_ratio > 0.92:
        cap.release()
        fail(f"automatic subject bbox covers almost the whole source frame ({bbox_area_ratio:.3f}); refusing a meaningless subject-framing inference")

    desired_h = target_h * float(target_subject_height_ratio)
    desired_w_cap = target_w * 0.52
    scale = min(desired_h / bh, desired_w_cap / bw)
    if scale <= 0:
        cap.release()
        fail("automatic subject transform produced a non-positive scale")

    subject_cx = bx + bw / 2.0
    subject_bottom = by + bh
    tx = float(target_center_x) - scale * subject_cx
    ty = float(target_bottom_y) - scale * subject_bottom

    out_x0 = scale * bx + tx
    out_y0 = scale * by + ty
    out_x1 = scale * (bx + bw) + tx
    out_y1 = scale * (by + bh) + ty
    margins = {
        "left": round(out_x0, 2),
        "top": round(out_y0, 2),
        "right": round(target_w - out_x1, 2),
        "bottom": round(target_h - out_y1, 2),
    }

    # CLIPVisionEncode in the current prompt uses crop='center'. On a 640x800 driver,
    # its square crop effectively discards about 80 px top and bottom. Keep the whole
    # detected subject envelope safely inside that central 640x640 region as well.
    clip_crop_top = (target_h - target_w) / 2.0
    clip_crop_bottom = clip_crop_top + target_w
    clip_margins = {
        "top_inside_center_square": round(out_y0 - clip_crop_top, 2),
        "bottom_inside_center_square": round(clip_crop_bottom - out_y1, 2),
        "left": round(out_x0, 2),
        "right": round(target_w - out_x1, 2),
    }

    guard_failures = []
    if margins["top"] < 90:
        guard_failures.append(f"top margin {margins['top']} < 90")
    if margins["bottom"] < 90:
        guard_failures.append(f"bottom margin {margins['bottom']} < 90")
    if margins["left"] < 70:
        guard_failures.append(f"left margin {margins['left']} < 70")
    if margins["right"] < 70:
        guard_failures.append(f"right margin {margins['right']} < 70")
    if clip_margins["top_inside_center_square"] < 24:
        guard_failures.append(f"CLIP center-crop top margin {clip_margins['top_inside_center_square']} < 24")
    if clip_margins["bottom_inside_center_square"] < 24:
        guard_failures.append(f"CLIP center-crop bottom margin {clip_margins['bottom_inside_center_square']} < 24")
    if guard_failures:
        cap.release()
        fail("FAIL_PREINFER_MARGIN_GUARD: " + "; ".join(guard_failures))

    pad_bgr = np.median(np.stack(corner_samples, axis=0), axis=0).astype(np.uint8) if corner_samples else np.array([32, 32, 32], dtype=np.uint8)
    matrix = np.array([[scale, 0.0, tx], [0.0, scale, ty]], dtype=np.float32)

    os.makedirs(os.path.dirname(dst), exist_ok=True)
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    writer = cv2.VideoWriter(dst, cv2.VideoWriter_fourcc(*"mp4v"), fps, (target_w, target_h))
    if not writer.isOpened():
        cap.release()
        fail(f"could not create subject-framed driver: {dst}")

    written = 0
    interpolation = cv2.INTER_AREA if scale < 1.0 else cv2.INTER_LINEAR
    border_value = tuple(int(v) for v in pad_bgr.tolist())
    while True:
        ok, frame = cap.read()
        if not ok:
            break
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
    if written <= 0 or not os.path.isfile(dst) or os.path.getsize(dst) <= 0:
        fail("subject-framing preprocessor produced no usable video")

    manifest = {
        "gate": "W1G_SUBJECT_FRAMING_V1",
        "status": "PASS_DRIVER_READY",
        "method": "fixed global temporal-activity subject envelope; one affine transform for the whole clip; no per-frame camera breathing",
        "source_width": src_w,
        "source_height": src_h,
        "source_fps": fps,
        "source_frame_count": frame_count,
        "analysis_frames": len(frames),
        "activity_otsu_threshold": float(otsu),
        "activity_threshold_used": int(min_threshold),
        "raw_activity_bbox": raw_bbox,
        "expanded_subject_bbox": subject_bbox,
        "subject_bbox_area_ratio": round(bbox_area_ratio, 6),
        "target_width": target_w,
        "target_height": target_h,
        "target_subject_height_ratio": target_subject_height_ratio,
        "target_center_x": target_center_x,
        "target_bottom_y": target_bottom_y,
        "affine_scale": float(scale),
        "affine_tx": float(tx),
        "affine_ty": float(ty),
        "transformed_subject_bbox": [round(out_x0, 2), round(out_y0, 2), round(out_x1 - out_x0, 2), round(out_y1 - out_y0, 2)],
        "output_margins": margins,
        "clipvision_center_crop_guard": clip_margins,
        "pad_bgr": [int(v) for v in pad_bgr.tolist()],
        "written_frames": written,
        "policy": "normalize the automatically detected moving-subject envelope, not merely the whole source frame; preserve a fixed camera transform and explicit head/foot/side safety inside both 640x800 pose-video and the center-square CLIP pose crop",
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
        fail("W1G must branch from W1A reference_image_strength=1.5 so framing is the only model-input variable changed from that structural branch")

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
    print(f"W1G: detected envelope={prep['expanded_subject_bbox']} transformed={prep['transformed_subject_bbox']}", flush=True)
    print(f"W1G: output margins={prep['output_margins']} CLIP-center-crop guard={prep['clipvision_center_crop_guard']}", flush=True)

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

    print("W1G: submitting exact W1A structural branch with only automatic subject-framing replacing the raw driver geometry...", flush=True)
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
    manifest.update({
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
        "changed_from_w1a": ["driver_preprocess_subject_normalization", "output_prefix"],
        "unchanged_from_w1a": [
            "reference_image", "positive_prompt", "negative_prompt", "main_model", "text_encoder", "clip_vision", "vae",
            "resolution", "frame_count", "fps", "steps", "cfg", "sampler", "scheduler", "shift", "seed",
            "pose_strength", "reference_image_strength"
        ],
        "hypothesis": "W1F proved whole-frame letterboxing does not control Wan framing. W1G therefore normalizes the automatically detected moving-subject envelope itself, keeps it safe inside both the 640x800 pose-video canvas and the center-square CLIP pose crop, and branches from the structurally preferred W1A reference strength 1.5 without changing any model/sampler/seed setting.",
    })
    manifest_path = os.path.join(workspace, "w1g_run_manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, ensure_ascii=False, indent=2)

    print(f"W1G: PASS - generated {canonical_output}", flush=True)
    print(f"W1G: manifest {manifest_path}", flush=True)
    print(f"W1G: driver manifest {subject_manifest_path}", flush=True)
    print(f"W1G: elapsed {elapsed} seconds", flush=True)


if __name__ == "__main__":
    main()
