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

TARGET_WIDTH = 512
TARGET_HEIGHT = 912
EXPECTED_REFERENCE_STRENGTH = 1.5


def fail(message, code=2):
    print(f"W1H: FAIL - {message}", file=sys.stderr, flush=True)
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


def retained_fraction_for_center_crop(source_w, source_h, target_w, target_h):
    source_aspect = source_w / source_h
    target_aspect = target_w / target_h
    if abs(source_aspect - target_aspect) < 1e-12:
        return 1.0, "none"
    if target_aspect > source_aspect:
        kept_h = source_w / target_aspect
        return kept_h / source_h, "vertical"
    kept_w = source_h * target_aspect
    return kept_w / source_w, "horizontal"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workspace", required=True)
    ap.add_argument("--comfy-root", required=True)
    ap.add_argument("--port", type=int, default=8188)
    ap.add_argument("--timeout-minutes", type=int, default=240)
    args = ap.parse_args()

    workspace = os.path.abspath(args.workspace)
    comfy_root = os.path.abspath(args.comfy_root)
    base = f"http://127.0.0.1:{args.port}"

    parent_prompt_path = os.path.join(workspace, "w1a_api_prompt.json")
    parent_manifest_path = os.path.join(workspace, "w1a_run_manifest.json")
    for path in (parent_prompt_path, parent_manifest_path):
        if not os.path.isfile(path):
            fail(f"required W1A evidence missing: {path}")

    with open(parent_manifest_path, "r", encoding="utf-8-sig") as fh:
        parent_manifest = json.load(fh)
    if parent_manifest.get("status") != "INFERENCE_COMPLETE":
        fail(f"W1A manifest is not complete: {parent_manifest.get('status')}")
    if float(parent_manifest.get("reference_image_strength", -1)) != EXPECTED_REFERENCE_STRENGTH:
        fail("W1H must branch from W1A reference_image_strength=1.5")

    with open(parent_prompt_path, "r", encoding="utf-8-sig") as fh:
        raw_prompt = json.load(fh)
    prompt = raw_prompt.get("prompt") if isinstance(raw_prompt, dict) and "prompt" in raw_prompt else raw_prompt
    if not isinstance(prompt, dict) or not prompt:
        fail("w1a_api_prompt.json does not contain a usable ComfyUI API prompt")

    wan_nodes = [(nid, node) for nid, node in prompt.items() if node.get("class_type") == "WanAnimate2ToVideo"]
    if len(wan_nodes) != 1:
        fail(f"expected exactly one WanAnimate2ToVideo node, found {len(wan_nodes)}")
    wan_node_id, wan_node = wan_nodes[0]
    inputs = wan_node.setdefault("inputs", {})
    if float(inputs.get("reference_image_strength", -1)) != EXPECTED_REFERENCE_STRENGTH:
        fail("W1A prompt unexpectedly does not use reference_image_strength 1.5")
    parent_width = int(inputs.get("width", 0))
    parent_height = int(inputs.get("height", 0))
    if (parent_width, parent_height) != (640, 800):
        fail(f"unexpected W1A output geometry: {parent_width}x{parent_height}")

    driver_rel = parent_manifest.get("driver")
    if not driver_rel:
        fail("W1A manifest does not identify its raw source driver")
    input_root = os.path.join(comfy_root, "input")
    driver_abs = os.path.join(input_root, *driver_rel.replace("\\", "/").split("/"))
    if not os.path.isfile(driver_abs):
        fail(f"raw W1A source driver missing: {driver_abs}")

    try:
        import cv2
    except Exception as exc:
        fail(f"OpenCV unavailable for W1H geometry preflight: {exc}")
    cap = cv2.VideoCapture(driver_abs)
    if not cap.isOpened():
        fail(f"could not open raw source driver: {driver_abs}")
    source_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    source_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    source_fps = float(cap.get(cv2.CAP_PROP_FPS) or 0.0)
    source_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    cap.release()
    if source_w <= 0 or source_h <= 0:
        fail(f"invalid raw driver geometry: {source_w}x{source_h}")

    source_aspect = source_w / source_h
    parent_aspect = parent_width / parent_height
    target_aspect = TARGET_WIDTH / TARGET_HEIGHT
    parent_keep, parent_crop_axis = retained_fraction_for_center_crop(source_w, source_h, parent_width, parent_height)
    target_keep, target_crop_axis = retained_fraction_for_center_crop(source_w, source_h, TARGET_WIDTH, TARGET_HEIGHT)
    aspect_error_pct = abs(target_aspect / source_aspect - 1.0) * 100.0
    if aspect_error_pct > 1.0:
        fail(f"target aspect mismatch is unexpectedly large: {aspect_error_pct:.3f}%")

    print(
        f"W1H: raw driver={source_w}x{source_h} aspect={source_aspect:.6f}; "
        f"W1A canvas={parent_width}x{parent_height} aspect={parent_aspect:.6f}; "
        f"target={TARGET_WIDTH}x{TARGET_HEIGHT} aspect={target_aspect:.6f}",
        flush=True,
    )
    print(
        f"W1H: Comfy center-crop geometry estimate: W1A retained={parent_keep*100:.2f}% "
        f"({parent_crop_axis} crop); W1H retained={target_keep*100:.2f}% ({target_crop_axis} crop)",
        flush=True,
    )

    inputs["width"] = TARGET_WIDTH
    inputs["height"] = TARGET_HEIGHT

    save_nodes = [(nid, node) for nid, node in prompt.items() if node.get("class_type") == "SaveVideo"]
    if len(save_nodes) != 1:
        fail(f"expected exactly one SaveVideo node, found {len(save_nodes)}")
    save_node_id, save_node = save_nodes[0]
    new_prefix = "roguelite_w1h/wan_animate2_bf16_exilada_rawdriver_aspectmatched_ref15"
    prefix_keys = [k for k, v in save_node.get("inputs", {}).items() if isinstance(v, str) and "roguelite_w1" in v]
    if len(prefix_keys) != 1:
        fail(f"could not uniquely resolve W1A SaveVideo prefix field: {prefix_keys}")
    save_node["inputs"][prefix_keys[0]] = new_prefix

    prompt_out = os.path.join(workspace, "w1h_api_prompt.json")
    with open(prompt_out, "w", encoding="utf-8") as fh:
        json.dump(prompt, fh, ensure_ascii=False, indent=2)

    print(
        "W1H: submitting exact W1A structural branch with the original raw driver untouched; "
        f"only Wan output geometry changes {parent_width}x{parent_height} -> {TARGET_WIDTH}x{TARGET_HEIGHT}.",
        flush=True,
    )
    started = time.time()
    response = request_json(base + "/prompt", {"prompt": prompt}, timeout=120)
    prompt_id = response.get("prompt_id")
    if not prompt_id:
        fail(f"ComfyUI did not return prompt_id: {response}")
    print(f"W1H: prompt_id={prompt_id}", flush=True)

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
            print(f"W1H: inference running for {int(now - started)} seconds...", flush=True)
            next_report = now + 60
        time.sleep(5)
    else:
        fail(f"timeout after {args.timeout_minutes} minutes")

    elapsed = round(time.time() - started, 2)
    output_path = newest_output(comfy_root, new_prefix, started)
    if not output_path:
        fail(f"ComfyUI completed prompt {prompt_id} but no new video matching {new_prefix} was found")

    canonical_output = os.path.join(workspace, "w1h_exilada_aspectmatched_ref15.mp4")
    shutil.copy2(output_path, canonical_output)

    manifest = dict(parent_manifest)
    manifest.update({
        "gate": "WAN_ANIMATE2_W1H_BF16_EXILADA_RAWDRIVER_ASPECT_MATCHED_REF15",
        "status": "INFERENCE_COMPLETE",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "parent_w1a_prompt_id": parent_manifest.get("prompt_id"),
        "driver": driver_rel,
        "width": TARGET_WIDTH,
        "height": TARGET_HEIGHT,
        "reference_image_strength": EXPECTED_REFERENCE_STRENGTH,
        "geometry_diagnostic": {
            "source_width": source_w,
            "source_height": source_h,
            "source_fps": source_fps,
            "source_frame_count": source_frames,
            "source_aspect": source_aspect,
            "parent_width": parent_width,
            "parent_height": parent_height,
            "parent_aspect": parent_aspect,
            "parent_center_crop_retained_fraction_estimate": parent_keep,
            "parent_center_crop_axis": parent_crop_axis,
            "target_width": TARGET_WIDTH,
            "target_height": TARGET_HEIGHT,
            "target_aspect": target_aspect,
            "target_aspect_error_pct_vs_driver": aspect_error_pct,
            "target_center_crop_retained_fraction_estimate": target_keep,
            "target_center_crop_axis": target_crop_axis,
        },
        "changed_from_w1a": ["wan_output_geometry_640x800_to_512x912", "output_prefix"],
        "unchanged_from_w1a": [
            "reference_image", "positive_prompt", "negative_prompt", "raw_driver", "main_model", "text_encoder",
            "clip_vision", "vae", "frame_count", "fps", "steps", "cfg", "sampler", "scheduler", "shift",
            "seed", "pose_strength", "pose_start_percent", "pose_end_percent", "reference_image_strength",
            "positive_pose", "clip_vision_output_pose"
        ],
        "hypothesis": "W1F and W1G show that altering raw-driver pixels or trajectory does not solve framing and can damage motion. ComfyUI center-resizes pose_video to the requested Wan canvas; the 480x854 driver nearly matches upstream Wan Animate 2's portrait aspect but W1A used 640x800. W1H therefore leaves the raw driver untouched and changes only the generation canvas to 512x912, closely matching the driver aspect, to preserve full-body spatial conditioning without synthetic camera motion.",
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
    })
    manifest_path = os.path.join(workspace, "w1h_run_manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, ensure_ascii=False, indent=2)

    print(f"W1H: PASS - generated {canonical_output}", flush=True)
    print(f"W1H: manifest {manifest_path}", flush=True)
    print(f"W1H: elapsed {elapsed} seconds", flush=True)


if __name__ == "__main__":
    main()
