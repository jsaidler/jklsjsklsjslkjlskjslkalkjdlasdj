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

EXILADA_PROMPT = (
    "Adult woman, lean and resilient natural feminine build, olive-brown skin, hard mature face, "
    "very long heavy voluminous messy black hair. She wears minimal asymmetrical degraded captivity clothing: "
    "dirty ragged beige chest wrap/bandeau, torn asymmetrical hip cloth/loincloth, sparse worn cloth bindings, "
    "bare feet, visible metal shackles/cuffs and broken chain segments, no weapon. Preserve the complete appearance, "
    "body proportions, face, hair mass, clothing layout, restraints and material wear from the reference image. "
    "Modern 2D game pixel-art appearance with crisp discrete pixel clusters and strong silhouette; do not reinterpret "
    "the character as smooth painterly illustration. Plain neutral background, no extra objects."
)


def fail(message, code=2):
    print(f"W1: FAIL - {message}", file=sys.stderr, flush=True)
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

    w0_prompt_path = os.path.join(workspace, "w0_api_prompt.json")
    w0_manifest_path = os.path.join(workspace, "w0_run_manifest.json")
    route_path = os.path.join(workspace, "wan_bf16_route.json")
    exilada_abs = os.path.join(comfy_root, "input", "exilada_master.png")
    for path in (w0_prompt_path, w0_manifest_path, route_path, exilada_abs):
        if not os.path.isfile(path):
            fail(f"required W1 input missing: {path}")

    with open(w0_manifest_path, "r", encoding="utf-8-sig") as fh:
        w0_manifest = json.load(fh)
    if w0_manifest.get("status") != "INFERENCE_COMPLETE":
        fail(f"W0 manifest is not complete: {w0_manifest.get('status')}")

    with open(w0_prompt_path, "r", encoding="utf-8-sig") as fh:
        raw_prompt = json.load(fh)
    prompt = raw_prompt.get("prompt") if isinstance(raw_prompt, dict) and "prompt" in raw_prompt else raw_prompt
    if not isinstance(prompt, dict) or not prompt:
        fail("w0_api_prompt.json does not contain a usable ComfyUI API prompt")

    load_image_nodes = [(nid, node) for nid, node in prompt.items() if node.get("class_type") == "LoadImage"]
    ref_candidates = []
    for nid, node in load_image_nodes:
        for key, value in node.get("inputs", {}).items():
            if isinstance(value, str) and "official_demo1_reference" in value:
                ref_candidates.append((nid, key))
    if len(ref_candidates) != 1:
        fail(f"expected exactly one official W0 reference LoadImage node, found {ref_candidates}")
    ref_node_id, ref_key = ref_candidates[0]
    prompt[ref_node_id]["inputs"][ref_key] = "exilada_master.png"

    wan_nodes = [(nid, node) for nid, node in prompt.items() if node.get("class_type") == "WanAnimate2ToVideo"]
    if len(wan_nodes) != 1:
        fail(f"expected exactly one WanAnimate2ToVideo node, found {len(wan_nodes)}")
    wan_node_id, wan_node = wan_nodes[0]
    positive_link = wan_node.get("inputs", {}).get("positive")
    if not (isinstance(positive_link, list) and len(positive_link) >= 1):
        fail("could not resolve positive-conditioning node from W0 prompt")
    positive_node_id = str(positive_link[0])
    positive_node = prompt.get(positive_node_id)
    if not positive_node or positive_node.get("class_type") != "CLIPTextEncode":
        fail(f"positive-conditioning source is not CLIPTextEncode: node {positive_node_id}")
    if "text" not in positive_node.get("inputs", {}):
        fail("positive CLIPTextEncode node has no text input")
    positive_node["inputs"]["text"] = EXILADA_PROMPT

    # Preserve the known-good W0 driver, model, seed, sampler, resolution, temporal window,
    # strengths and negative prompt. Only the target appearance package changes here:
    # reference image + its matching positive appearance description.
    new_prefix = "roguelite_w1/wan_animate2_bf16_exilada_official_driver"
    save_nodes = [(nid, node) for nid, node in prompt.items() if node.get("class_type") == "SaveVideo"]
    if len(save_nodes) != 1:
        fail(f"expected exactly one SaveVideo node, found {len(save_nodes)}")
    save_node_id, save_node = save_nodes[0]
    prefix_keys = [k for k, v in save_node.get("inputs", {}).items() if isinstance(v, str) and "roguelite_w0" in v]
    if len(prefix_keys) != 1:
        fail(f"could not uniquely resolve W0 SaveVideo prefix field: {prefix_keys}")
    save_node["inputs"][prefix_keys[0]] = new_prefix

    w1_prompt_path = os.path.join(workspace, "w1_api_prompt.json")
    with open(w1_prompt_path, "w", encoding="utf-8") as fh:
        json.dump(prompt, fh, ensure_ascii=False, indent=2)

    print("W1: submitting Exilada reference package with unchanged official W0 driving/execution settings...", flush=True)
    started = time.time()
    response = request_json(base + "/prompt", {"prompt": prompt}, timeout=120)
    prompt_id = response.get("prompt_id")
    if not prompt_id:
        fail(f"ComfyUI did not return prompt_id: {response}")
    print(f"W1: prompt_id={prompt_id}", flush=True)

    deadline = started + args.timeout_minutes * 60
    next_report = started + 60
    history_item = None
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
            print(f"W1: inference running for {int(now - started)} seconds...", flush=True)
            next_report = now + 60
        time.sleep(5)
    else:
        fail(f"timeout after {args.timeout_minutes} minutes")

    elapsed = round(time.time() - started, 2)
    output_path = newest_output(comfy_root, new_prefix, started)
    if not output_path:
        fail(f"ComfyUI completed prompt {prompt_id} but no new video matching {new_prefix} was found")

    canonical_output = os.path.join(workspace, "w1_exilada_official_driver.mp4")
    shutil.copy2(output_path, canonical_output)

    manifest = {
        "gate": "WAN_ANIMATE2_W1_BF16_EXILADA_OFFICIAL_DRIVER",
        "status": "INFERENCE_COMPLETE",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "parent_w0_prompt_id": w0_manifest.get("prompt_id"),
        "model": w0_manifest.get("model"),
        "text_encoder": w0_manifest.get("text_encoder"),
        "clip_vision": w0_manifest.get("clip_vision"),
        "vae": w0_manifest.get("vae"),
        "reference": "exilada_master.png",
        "reference_sha256": sha256_file(exilada_abs),
        "driver": w0_manifest.get("driver"),
        "width": w0_manifest.get("width"),
        "height": w0_manifest.get("height"),
        "length": w0_manifest.get("length"),
        "fps": w0_manifest.get("fps"),
        "steps": w0_manifest.get("steps"),
        "cfg": w0_manifest.get("cfg"),
        "sampler": w0_manifest.get("sampler"),
        "scheduler": w0_manifest.get("scheduler"),
        "shift": w0_manifest.get("shift"),
        "seed": w0_manifest.get("seed"),
        "pose_strength": w0_manifest.get("pose_strength"),
        "reference_image_strength": w0_manifest.get("reference_image_strength"),
        "positive_prompt": EXILADA_PROMPT,
        "negative_prompt_policy": "unchanged from successful W0 official baseline",
        "changed_from_w0": ["reference_image", "matching_positive_appearance_prompt", "output_prefix"],
        "unchanged_from_w0": ["official_driver", "main_model", "text_encoder", "clip_vision", "vae", "resolution", "frame_count", "fps", "steps", "cfg", "sampler", "scheduler", "shift", "seed", "pose_strength", "reference_image_strength", "negative_prompt"],
        "prompt_file": w1_prompt_path,
        "save_node": save_node_id,
        "output_prefix": new_prefix,
        "prompt_id": prompt_id,
        "elapsed_seconds": elapsed,
        "comfy_output": output_path,
        "canonical_output": canonical_output,
        "output_bytes": os.path.getsize(canonical_output),
        "output_sha256": sha256_file(canonical_output),
    }
    manifest_path = os.path.join(workspace, "w1_run_manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, ensure_ascii=False, indent=2)

    print(f"W1: PASS - generated {canonical_output}", flush=True)
    print(f"W1: manifest {manifest_path}", flush=True)
    print(f"W1: elapsed {elapsed} seconds", flush=True)


if __name__ == "__main__":
    main()
