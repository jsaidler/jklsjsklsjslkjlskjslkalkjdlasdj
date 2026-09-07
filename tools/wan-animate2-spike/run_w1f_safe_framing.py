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
    print(f"W1F: FAIL - {message}", file=sys.stderr, flush=True)
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


def prepare_safe_driver(src, dst, target_w=640, target_h=800, safe_scale=0.80):
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

    # Estimate a single neutral pad colour from corner pixels across an initial sample.
    samples = []
    sample_limit = min(frame_count if frame_count > 0 else 16, 16)
    for _ in range(sample_limit):
        ok, frame = cap.read()
        if not ok:
            break
        h, w = frame.shape[:2]
        s = max(4, min(h, w) // 20)
        corners = np.concatenate([
            frame[:s, :s].reshape(-1, 3),
            frame[:s, -s:].reshape(-1, 3),
            frame[-s:, :s].reshape(-1, 3),
            frame[-s:, -s:].reshape(-1, 3),
        ], axis=0)
        samples.append(np.median(corners, axis=0))
    if samples:
        pad_bgr = np.median(np.stack(samples, axis=0), axis=0).astype(np.uint8)
    else:
        pad_bgr = np.array([127, 127, 127], dtype=np.uint8)

    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    inner_w = max(2, int(round(target_w * safe_scale)))
    inner_h = max(2, int(round(target_h * safe_scale)))
    fit = min(inner_w / src_w, inner_h / src_h)
    new_w = max(2, int(round(src_w * fit)))
    new_h = max(2, int(round(src_h * fit)))
    # MPEG-4 encoders are happier with even dimensions.
    new_w -= new_w % 2
    new_h -= new_h % 2
    x0 = (target_w - new_w) // 2
    y0 = (target_h - new_h) // 2

    os.makedirs(os.path.dirname(dst), exist_ok=True)
    writer = cv2.VideoWriter(dst, cv2.VideoWriter_fourcc(*"mp4v"), fps, (target_w, target_h))
    if not writer.isOpened():
        cap.release()
        fail(f"could not create safe-framed driver: {dst}")

    written = 0
    interpolation = cv2.INTER_AREA if fit < 1.0 else cv2.INTER_LINEAR
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        resized = cv2.resize(frame, (new_w, new_h), interpolation=interpolation)
        canvas = np.empty((target_h, target_w, 3), dtype=np.uint8)
        canvas[:, :] = pad_bgr
        canvas[y0:y0 + new_h, x0:x0 + new_w] = resized
        writer.write(canvas)
        written += 1

    cap.release()
    writer.release()
    if written <= 0 or not os.path.isfile(dst) or os.path.getsize(dst) <= 0:
        fail("safe-framing preprocessor produced no usable video")

    return {
        "source_width": src_w,
        "source_height": src_h,
        "source_fps": fps,
        "source_frame_count": frame_count,
        "target_width": target_w,
        "target_height": target_h,
        "safe_scale": safe_scale,
        "inner_box_width": inner_w,
        "inner_box_height": inner_h,
        "placed_width": new_w,
        "placed_height": new_h,
        "offset_x": x0,
        "offset_y": y0,
        "pad_bgr": [int(v) for v in pad_bgr.tolist()],
        "written_frames": written,
        "policy": "contain entire original frame inside a fixed centered 80% safe box; no temporal tracking, no crop, no manual alignment",
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workspace", required=True)
    ap.add_argument("--comfy-root", required=True)
    ap.add_argument("--port", type=int, default=8188)
    ap.add_argument("--timeout-minutes", type=int, default=240)
    ap.add_argument("--safe-scale", type=float, default=0.80)
    args = ap.parse_args()

    if not (0.50 <= args.safe_scale <= 1.0):
        fail("safe-scale must be between 0.50 and 1.0")

    workspace = os.path.abspath(args.workspace)
    comfy_root = os.path.abspath(args.comfy_root)
    base = f"http://127.0.0.1:{args.port}"

    w1_prompt_path = os.path.join(workspace, "w1_api_prompt.json")
    w1_manifest_path = os.path.join(workspace, "w1_run_manifest.json")
    for path in (w1_prompt_path, w1_manifest_path):
        if not os.path.isfile(path):
            fail(f"required W1 evidence missing: {path}")

    with open(w1_manifest_path, "r", encoding="utf-8-sig") as fh:
        w1_manifest = json.load(fh)
    if w1_manifest.get("status") != "INFERENCE_COMPLETE":
        fail(f"W1 manifest is not complete: {w1_manifest.get('status')}")
    if float(w1_manifest.get("reference_image_strength", -1)) != 1.0:
        fail("W1F must branch from W1 reference strength 1.0, the current preferred motion/appearance balance")

    with open(w1_prompt_path, "r", encoding="utf-8-sig") as fh:
        raw_prompt = json.load(fh)
    prompt = raw_prompt.get("prompt") if isinstance(raw_prompt, dict) and "prompt" in raw_prompt else raw_prompt
    if not isinstance(prompt, dict) or not prompt:
        fail("w1_api_prompt.json does not contain a usable ComfyUI API prompt")

    driver_rel = w1_manifest.get("driver")
    if not driver_rel:
        fail("W1 manifest does not identify the official driver")
    input_root = os.path.join(comfy_root, "input")
    driver_abs = os.path.join(input_root, *driver_rel.replace("\\", "/").split("/"))
    if not os.path.isfile(driver_abs):
        fail(f"source driver missing: {driver_abs}")

    safe_rel = "wan_animate2_w1f/official_demo1_template_safe80.mp4"
    safe_abs = os.path.join(input_root, *safe_rel.split("/"))
    prep = prepare_safe_driver(driver_abs, safe_abs, target_w=640, target_h=800, safe_scale=args.safe_scale)
    prep["source_sha256"] = sha256_file(driver_abs)
    prep["safe_driver_sha256"] = sha256_file(safe_abs)
    prep["safe_driver_bytes"] = os.path.getsize(safe_abs)
    prep_path = os.path.join(workspace, "w1f_safe_driver_manifest.json")
    with open(prep_path, "w", encoding="utf-8") as fh:
        json.dump(prep, fh, ensure_ascii=False, indent=2)
    print(f"W1F: safe driver prepared at {safe_abs}", flush=True)
    print(f"W1F: fixed canvas {prep['target_width']}x{prep['target_height']}, inner safe box {prep['inner_box_width']}x{prep['inner_box_height']}, placed source {prep['placed_width']}x{prep['placed_height']}", flush=True)

    load_video_nodes = [(nid, node) for nid, node in prompt.items() if node.get("class_type") == "LoadVideo"]
    matches = []
    for nid, node in load_video_nodes:
        for key, value in node.get("inputs", {}).items():
            if isinstance(value, str) and value.replace("\\", "/") == driver_rel.replace("\\", "/"):
                matches.append((nid, key))
    if len(matches) != 1:
        fail(f"could not uniquely resolve W1 LoadVideo driver field: {matches}")
    video_node_id, video_key = matches[0]
    prompt[video_node_id]["inputs"][video_key] = safe_rel

    wan_nodes = [(nid, node) for nid, node in prompt.items() if node.get("class_type") == "WanAnimate2ToVideo"]
    if len(wan_nodes) != 1:
        fail(f"expected exactly one WanAnimate2ToVideo node, found {len(wan_nodes)}")
    wan_node_id, wan_node = wan_nodes[0]
    if float(wan_node.get("inputs", {}).get("reference_image_strength", -1)) != 1.0:
        fail("W1F prompt unexpectedly does not use reference_image_strength 1.0")

    new_prefix = "roguelite_w1f/wan_animate2_bf16_exilada_safe_framing80"
    save_nodes = [(nid, node) for nid, node in prompt.items() if node.get("class_type") == "SaveVideo"]
    if len(save_nodes) != 1:
        fail(f"expected exactly one SaveVideo node, found {len(save_nodes)}")
    save_node_id, save_node = save_nodes[0]
    prefix_keys = [k for k, v in save_node.get("inputs", {}).items() if isinstance(v, str) and "roguelite_w1" in v]
    if len(prefix_keys) != 1:
        fail(f"could not uniquely resolve W1 SaveVideo prefix field: {prefix_keys}")
    save_node["inputs"][prefix_keys[0]] = new_prefix

    w1f_prompt_path = os.path.join(workspace, "w1f_api_prompt.json")
    with open(w1f_prompt_path, "w", encoding="utf-8") as fh:
        json.dump(prompt, fh, ensure_ascii=False, indent=2)

    print("W1F: submitting W1 appearance/model settings with only a fixed safe-contained driver framing change...", flush=True)
    started = time.time()
    response = request_json(base + "/prompt", {"prompt": prompt}, timeout=120)
    prompt_id = response.get("prompt_id")
    if not prompt_id:
        fail(f"ComfyUI did not return prompt_id: {response}")
    print(f"W1F: prompt_id={prompt_id}", flush=True)

    deadline = started + args.timeout_minutes * 60
    next_report = started + 60
    while time.time() < deadline:
        history = request_json(base + f"/history/{prompt_id}", timeout=120)
        history_item = history.get(prompt_id) if isinstance(history, dict) else None
        if history_item:
            status = history_item.get("status") or {}
            messages = status.get("messages") or []
            for message in messages:
                if isinstance(message, (list, tuple)) and message and message[0] == "execution_error":
                    fail(f"ComfyUI execution_error: {message}")
            if status.get("completed") is True:
                break
        now = time.time()
        if now >= next_report:
            print(f"W1F: inference running for {int(now - started)} seconds...", flush=True)
            next_report = now + 60
        time.sleep(5)
    else:
        fail(f"timeout after {args.timeout_minutes} minutes")

    elapsed = round(time.time() - started, 2)
    output_path = newest_output(comfy_root, new_prefix, started)
    if not output_path:
        fail(f"ComfyUI completed prompt {prompt_id} but no new video matching {new_prefix} was found")

    canonical_output = os.path.join(workspace, "w1f_exilada_safe_framing80.mp4")
    shutil.copy2(output_path, canonical_output)

    manifest = dict(w1_manifest)
    manifest.update({
        "gate": "WAN_ANIMATE2_W1F_BF16_EXILADA_SAFE_FRAMING_80",
        "status": "INFERENCE_COMPLETE",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "parent_w1_prompt_id": w1_manifest.get("prompt_id"),
        "driver": safe_rel,
        "driver_preprocess": prep,
        "reference_image_strength": 1.0,
        "prompt_file": w1f_prompt_path,
        "save_node": save_node_id,
        "wan_node": wan_node_id,
        "output_prefix": new_prefix,
        "prompt_id": prompt_id,
        "elapsed_seconds": elapsed,
        "comfy_output": output_path,
        "canonical_output": canonical_output,
        "output_bytes": os.path.getsize(canonical_output),
        "output_sha256": sha256_file(canonical_output),
        "changed_from_w1": ["driver_preprocess_fixed_safe_contain_80", "output_prefix"],
        "unchanged_from_w1": [
            "reference_image", "positive_prompt", "negative_prompt", "main_model", "text_encoder", "clip_vision", "vae",
            "resolution", "frame_count", "fps", "steps", "cfg", "sampler", "scheduler", "shift", "seed",
            "pose_strength", "reference_image_strength"
        ],
        "hypothesis": "Containing the entire raw driving frame inside a fixed centered 80% safe box before Wan should prevent inherited head/body edge cropping without temporal camera breathing or manual alignment.",
    })
    manifest_path = os.path.join(workspace, "w1f_run_manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, ensure_ascii=False, indent=2)

    print(f"W1F: PASS - generated {canonical_output}", flush=True)
    print(f"W1F: manifest {manifest_path}", flush=True)
    print(f"W1F: safe-driver manifest {prep_path}", flush=True)
    print(f"W1F: elapsed {elapsed} seconds", flush=True)


if __name__ == "__main__":
    main()
