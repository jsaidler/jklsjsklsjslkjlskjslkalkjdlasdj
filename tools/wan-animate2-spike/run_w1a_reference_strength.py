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

TARGET_REFERENCE_STRENGTH = 1.5


def fail(message, code=2):
    print(f"W1A: FAIL - {message}", file=sys.stderr, flush=True)
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

    w1_prompt_path = os.path.join(workspace, "w1_api_prompt.json")
    w1_manifest_path = os.path.join(workspace, "w1_run_manifest.json")
    for path in (w1_prompt_path, w1_manifest_path):
        if not os.path.isfile(path):
            fail(f"required W1 evidence missing: {path}")

    with open(w1_manifest_path, "r", encoding="utf-8-sig") as fh:
        w1_manifest = json.load(fh)
    if w1_manifest.get("status") != "INFERENCE_COMPLETE":
        fail(f"W1 manifest is not complete: {w1_manifest.get('status')}")

    with open(w1_prompt_path, "r", encoding="utf-8-sig") as fh:
        raw = json.load(fh)
    prompt = raw.get("prompt") if isinstance(raw, dict) and "prompt" in raw else raw
    if not isinstance(prompt, dict) or not prompt:
        fail("w1_api_prompt.json does not contain a usable ComfyUI API prompt")

    wan_nodes = [(nid, node) for nid, node in prompt.items() if node.get("class_type") == "WanAnimate2ToVideo"]
    if len(wan_nodes) != 1:
        fail(f"expected exactly one WanAnimate2ToVideo node, found {len(wan_nodes)}")
    wan_node_id, wan_node = wan_nodes[0]
    inputs = wan_node.setdefault("inputs", {})
    before = inputs.get("reference_image_strength")
    if before is None:
        fail("installed W1 prompt has no reference_image_strength input")
    if float(before) != 1.0:
        fail(f"W1 baseline reference_image_strength is not 1.0: {before}")
    inputs["reference_image_strength"] = TARGET_REFERENCE_STRENGTH

    save_nodes = [(nid, node) for nid, node in prompt.items() if node.get("class_type") == "SaveVideo"]
    if len(save_nodes) != 1:
        fail(f"expected exactly one SaveVideo node, found {len(save_nodes)}")
    save_node_id, save_node = save_nodes[0]
    new_prefix = "roguelite_w1a/wan_animate2_bf16_exilada_refstrength15"
    prefix_keys = [k for k, v in save_node.get("inputs", {}).items() if isinstance(v, str) and "roguelite_w1" in v]
    if len(prefix_keys) != 1:
        fail(f"could not uniquely resolve W1 SaveVideo prefix field: {prefix_keys}")
    save_node["inputs"][prefix_keys[0]] = new_prefix

    prompt_out = os.path.join(workspace, "w1a_api_prompt.json")
    with open(prompt_out, "w", encoding="utf-8") as fh:
        json.dump(prompt, fh, ensure_ascii=False, indent=2)

    print(
        "W1A: submitting exact W1 graph with one changed variable only: "
        f"reference_image_strength 1.0 -> {TARGET_REFERENCE_STRENGTH}",
        flush=True,
    )
    started = time.time()
    response = request_json(base + "/prompt", {"prompt": prompt}, timeout=120)
    prompt_id = response.get("prompt_id")
    if not prompt_id:
        fail(f"ComfyUI did not return prompt_id: {response}")
    print(f"W1A: prompt_id={prompt_id}", flush=True)

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
            print(f"W1A: inference running for {int(now - started)} seconds...", flush=True)
            next_report = now + 60
        time.sleep(5)
    else:
        fail(f"timeout after {args.timeout_minutes} minutes")

    elapsed = round(time.time() - started, 2)
    output_path = newest_output(comfy_root, new_prefix, started)
    if not output_path:
        fail(f"ComfyUI completed prompt {prompt_id} but no new video matching {new_prefix} was found")

    canonical_output = os.path.join(workspace, "w1a_exilada_refstrength15.mp4")
    shutil.copy2(output_path, canonical_output)

    manifest = dict(w1_manifest)
    manifest.update({
        "gate": "WAN_ANIMATE2_W1A_BF16_EXILADA_REFERENCE_STRENGTH_1_5",
        "status": "INFERENCE_COMPLETE",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "parent_w1_prompt_id": w1_manifest.get("prompt_id"),
        "reference_image_strength": TARGET_REFERENCE_STRENGTH,
        "changed_from_w1": ["reference_image_strength", "output_prefix"],
        "unchanged_from_w1": [
            "reference_image", "positive_prompt", "negative_prompt", "official_driver", "main_model",
            "text_encoder", "clip_vision", "vae", "resolution", "frame_count", "fps", "steps",
            "cfg", "sampler", "scheduler", "shift", "seed", "pose_strength"
        ],
        "hypothesis": "Increasing native WanAnimate2ToVideo reference_image_strength from 1.0 to 1.5 should tighten identity/appearance adherence without changing motion source or sampler settings.",
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
    manifest_path = os.path.join(workspace, "w1a_run_manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, ensure_ascii=False, indent=2)

    print(f"W1A: PASS - generated {canonical_output}", flush=True)
    print(f"W1A: manifest {manifest_path}", flush=True)
    print(f"W1A: elapsed {elapsed} seconds", flush=True)


if __name__ == "__main__":
    main()
