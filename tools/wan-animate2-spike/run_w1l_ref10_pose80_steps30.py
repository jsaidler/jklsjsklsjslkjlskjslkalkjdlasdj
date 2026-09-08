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

EXPECTED_WIDTH = 512
EXPECTED_HEIGHT = 912
EXPECTED_PARENT_REFERENCE_STRENGTH = 1.5
TARGET_REFERENCE_STRENGTH = 1.0
EXPECTED_PARENT_POSE_STRENGTH = 1.0
TARGET_POSE_STRENGTH = 0.80
EXPECTED_POSE_START = 0.0
EXPECTED_POSE_END = 1.0
EXPECTED_PARENT_STEPS = 20
TARGET_STEPS = 30


def fail(message, code=2):
    print(f"W1L: FAIL - {message}", file=sys.stderr, flush=True)
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

    parent_prompt_path = os.path.join(workspace, "w1h_api_prompt.json")
    parent_manifest_path = os.path.join(workspace, "w1h_run_manifest.json")
    for path in (parent_prompt_path, parent_manifest_path):
        if not os.path.isfile(path):
            fail(f"required W1H evidence missing: {path}")

    with open(parent_manifest_path, "r", encoding="utf-8-sig") as fh:
        parent_manifest = json.load(fh)
    if parent_manifest.get("status") != "INFERENCE_COMPLETE":
        fail(f"W1H manifest is not complete: {parent_manifest.get('status')}")
    if int(parent_manifest.get("width", 0)) != EXPECTED_WIDTH or int(parent_manifest.get("height", 0)) != EXPECTED_HEIGHT:
        fail(f"W1L must branch from W1H 512x912 geometry, found {parent_manifest.get('width')}x{parent_manifest.get('height')}")
    if float(parent_manifest.get("reference_image_strength", -1)) != EXPECTED_PARENT_REFERENCE_STRENGTH:
        fail("W1L must branch from W1H reference_image_strength=1.5")
    if float(parent_manifest.get("pose_strength", -1)) != EXPECTED_PARENT_POSE_STRENGTH:
        fail("W1L must branch from W1H pose_strength=1.0")
    if int(parent_manifest.get("steps", 0)) != EXPECTED_PARENT_STEPS:
        fail(f"W1L must branch from W1H steps=20, found {parent_manifest.get('steps')}")

    with open(parent_prompt_path, "r", encoding="utf-8-sig") as fh:
        raw_prompt = json.load(fh)
    prompt = raw_prompt.get("prompt") if isinstance(raw_prompt, dict) and "prompt" in raw_prompt else raw_prompt
    if not isinstance(prompt, dict) or not prompt:
        fail("w1h_api_prompt.json does not contain a usable ComfyUI API prompt")

    wan_nodes = [(nid, node) for nid, node in prompt.items() if node.get("class_type") == "WanAnimate2ToVideo"]
    if len(wan_nodes) != 1:
        fail(f"expected exactly one WanAnimate2ToVideo node, found {len(wan_nodes)}")
    wan_node_id, wan_node = wan_nodes[0]
    inputs = wan_node.setdefault("inputs", {})

    if int(inputs.get("width", 0)) != EXPECTED_WIDTH or int(inputs.get("height", 0)) != EXPECTED_HEIGHT:
        fail(f"W1H prompt geometry is not 512x912: {inputs.get('width')}x{inputs.get('height')}")
    before_reference_strength = float(inputs.get("reference_image_strength", -1))
    if before_reference_strength != EXPECTED_PARENT_REFERENCE_STRENGTH:
        fail(f"W1H reference_image_strength is not 1.5: {before_reference_strength}")
    before_pose_strength = float(inputs.get("pose_strength", -1))
    if before_pose_strength != EXPECTED_PARENT_POSE_STRENGTH:
        fail(f"W1H pose_strength is not 1.0: {before_pose_strength}")
    if float(inputs.get("pose_start_percent", -1)) != EXPECTED_POSE_START:
        fail(f"W1H pose_start_percent is not 0.0: {inputs.get('pose_start_percent')}")
    if float(inputs.get("pose_end_percent", -1)) != EXPECTED_POSE_END:
        fail(f"W1H pose_end_percent is not 1.0: {inputs.get('pose_end_percent')}")

    sampler_nodes = [(nid, node) for nid, node in prompt.items() if node.get("class_type") == "KSampler"]
    if len(sampler_nodes) != 1:
        fail(f"expected exactly one KSampler node, found {len(sampler_nodes)}")
    sampler_node_id, sampler_node = sampler_nodes[0]
    sampler_inputs = sampler_node.setdefault("inputs", {})
    before_steps = int(sampler_inputs.get("steps", 0))
    if before_steps != EXPECTED_PARENT_STEPS:
        fail(f"W1H KSampler steps is not 20: {before_steps}")

    inputs["reference_image_strength"] = TARGET_REFERENCE_STRENGTH
    inputs["pose_strength"] = TARGET_POSE_STRENGTH
    sampler_inputs["steps"] = TARGET_STEPS

    save_nodes = [(nid, node) for nid, node in prompt.items() if node.get("class_type") == "SaveVideo"]
    if len(save_nodes) != 1:
        fail(f"expected exactly one SaveVideo node, found {len(save_nodes)}")
    save_node_id, save_node = save_nodes[0]
    new_prefix = "roguelite_w1l/wan_animate2_bf16_exilada_aspectmatched_ref10_pose080_steps30"
    prefix_keys = [k for k, v in save_node.get("inputs", {}).items() if isinstance(v, str) and "roguelite_w1" in v]
    if len(prefix_keys) != 1:
        fail(f"could not uniquely resolve W1H SaveVideo prefix field: {prefix_keys}")
    save_node["inputs"][prefix_keys[0]] = new_prefix

    prompt_out = os.path.join(workspace, "w1l_api_prompt.json")
    with open(prompt_out, "w", encoding="utf-8") as fh:
        json.dump(prompt, fh, ensure_ascii=False, indent=2)

    print(
        "W1L: submitting exact W1H branch with a deliberate three-control compound test: "
        f"reference_image_strength {before_reference_strength:.1f} -> {TARGET_REFERENCE_STRENGTH:.1f}; "
        f"pose_strength {before_pose_strength:.2f} -> {TARGET_POSE_STRENGTH:.2f}; "
        f"steps {before_steps} -> {TARGET_STEPS}.",
        flush=True,
    )
    print(
        "W1L: purpose = attack the remaining heavy motion-phase blur and structural drift together. "
        "This run is a configuration search, not a one-variable causal attribution test.",
        flush=True,
    )
    print(
        "W1L: unchanged = raw driver, 512x912 geometry, full pose window 0.0-1.0, seed0, CFG1, "
        "Euler/simple, shift5, Exilada reference/prompt, CLIP pose branch and negative prompt.",
        flush=True,
    )

    started = time.time()
    response = request_json(base + "/prompt", {"prompt": prompt}, timeout=120)
    prompt_id = response.get("prompt_id")
    if not prompt_id:
        fail(f"ComfyUI did not return prompt_id: {response}")
    print(f"W1L: prompt_id={prompt_id}", flush=True)

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
            print(f"W1L: inference running for {int(now - started)} seconds...", flush=True)
            next_report = now + 60
        time.sleep(5)
    else:
        fail(f"timeout after {args.timeout_minutes} minutes")

    elapsed = round(time.time() - started, 2)
    output_path = newest_output(comfy_root, new_prefix, started)
    if not output_path:
        fail(f"ComfyUI completed prompt {prompt_id} but no new video matching {new_prefix} was found")

    canonical_output = os.path.join(workspace, "w1l_exilada_aspectmatched_ref10_pose80_steps30.mp4")
    shutil.copy2(output_path, canonical_output)

    manifest = dict(parent_manifest)
    manifest.update({
        "gate": "WAN_ANIMATE2_W1L_BF16_EXILADA_ASPECTMATCHED_REF10_POSE080_STEPS30",
        "status": "INFERENCE_COMPLETE",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "parent_w1h_prompt_id": parent_manifest.get("prompt_id"),
        "reference_image_strength": TARGET_REFERENCE_STRENGTH,
        "pose_strength": TARGET_POSE_STRENGTH,
        "pose_start_percent": EXPECTED_POSE_START,
        "pose_end_percent": EXPECTED_POSE_END,
        "steps": TARGET_STEPS,
        "changed_from_w1h": [
            "reference_image_strength_1.5_to_1.0",
            "pose_strength_1.0_to_0.80",
            "steps_20_to_30",
            "output_prefix"
        ],
        "unchanged_from_w1h": [
            "reference_image", "positive_prompt", "negative_prompt", "raw_driver", "main_model", "text_encoder",
            "clip_vision", "vae", "width", "height", "frame_count", "fps", "cfg", "sampler", "scheduler",
            "shift", "seed", "pose_start_percent", "pose_end_percent", "positive_pose", "clip_vision_output_pose"
        ],
        "experiment_policy": "COMPOUND_CONFIGURATION_SEARCH",
        "hypothesis": "W1H solved the dominant framing failure but retained heavy fast-motion smear and structural deformation. W1I showed that pose_end_percent=0.70 is ineffective. The user requested a deliberate combined test that lowers reference adherence to 1.0, reduces pose forcing to 0.80, and increases sampling steps from 20 to 30. This run searches for a materially better operating point and must not be interpreted as isolating the causal contribution of any one of the three controls.",
        "prompt_file": prompt_out,
        "save_node": save_node_id,
        "wan_node": wan_node_id,
        "sampler_node": sampler_node_id,
        "output_prefix": new_prefix,
        "prompt_id": prompt_id,
        "elapsed_seconds": elapsed,
        "comfy_output": output_path,
        "canonical_output": canonical_output,
        "output_bytes": os.path.getsize(canonical_output),
        "output_sha256": sha256_file(canonical_output),
    })
    manifest_path = os.path.join(workspace, "w1l_run_manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, ensure_ascii=False, indent=2)

    print(f"W1L: PASS - generated {canonical_output}", flush=True)
    print(f"W1L: manifest {manifest_path}", flush=True)
    print(f"W1L: elapsed {elapsed} seconds", flush=True)


if __name__ == "__main__":
    main()
