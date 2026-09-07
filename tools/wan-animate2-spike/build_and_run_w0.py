#!/usr/bin/env python3
import argparse
import glob
import json
import os
import shutil
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

UPSTREAM_PROMPT = (
    "人物外观描述：一只银灰色虎斑纹的小猫，拥有圆润的脸庞、竖立的耳朵和巨大的圆形眼睛。"
    "它身穿一套深蓝色的制服套装，包括一件带有金色纽扣的西装外套和一条百褶裙。"
    "外套里面搭配着白色衬衫，领口处系着一个红色的蝴蝶结，袖口露出白色的衬衫边缘。"
    "背景描述：背景为纯白色，光线均匀明亮，无其他杂物或装饰。"
)

UPSTREAM_NEGATIVE = (
    "色调艳丽，过曝，静态，细节模糊不清，字幕，风格，作品，画作，画面，静止，整体发灰，"
    "最差质量，低质量，JPEG压缩残留，丑陋的，残缺的，多余的手指，画得不好的手部，"
    "画得不好的脸部，畸形的，毁容的，形态畸形的肢体，手指融合，静止不动的画面，"
    "杂乱的背景，三条腿，背景人很多，倒着走"
)


def fail(message, code=2):
    print(f"W0: FAIL - {message}", file=sys.stderr, flush=True)
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


def node_inputs(info, class_type):
    spec = info[class_type].get("input", {})
    names = set()
    for bucket in ("required", "optional"):
        values = spec.get(bucket, {})
        if isinstance(values, dict):
            names.update(values.keys())
    return names


def has_input(info, class_type, name):
    return name in node_inputs(info, class_type)


def output_index(info, class_type, *candidates):
    names = info[class_type].get("output_name") or []
    lowered = [str(n).lower() for n in names]
    for candidate in candidates:
        if candidate in names:
            return names.index(candidate)
        lc = candidate.lower()
        if lc in lowered:
            return lowered.index(lc)
    if len(names) == 1:
        return 0
    raise RuntimeError(
        f"Could not resolve output {candidates} for {class_type}; installed outputs are {names}"
    )


def choose_input_name(info, class_type, *candidates):
    available = node_inputs(info, class_type)
    for candidate in candidates:
        if candidate in available:
            return candidate
    raise RuntimeError(
        f"Could not resolve input {candidates} for {class_type}; installed inputs are {sorted(available)}"
    )


def required_defaults(info, class_type, supplied):
    result = dict(supplied)
    required = info[class_type].get("input", {}).get("required", {})
    if not isinstance(required, dict):
        return result
    for name, schema in required.items():
        if name in result:
            continue
        default = None
        have_default = False
        if isinstance(schema, (list, tuple)):
            if len(schema) > 1 and isinstance(schema[1], dict) and "default" in schema[1]:
                default = schema[1]["default"]
                have_default = True
            elif len(schema) > 0 and isinstance(schema[0], list) and schema[0]:
                default = schema[0][0]
                have_default = True
        if have_default:
            result[name] = default
            continue
        raise RuntimeError(
            f"Required input {class_type}.{name} has no supplied value and no installed-schema default"
        )
    return result


class PromptBuilder:
    def __init__(self, info):
        self.info = info
        self.prompt = {}
        self._counter = 1

    def add(self, class_type, inputs):
        if class_type not in self.info:
            raise RuntimeError(f"Required node class is absent: {class_type}")
        node_id = str(self._counter)
        self._counter += 1
        inputs = required_defaults(self.info, class_type, inputs)
        self.prompt[node_id] = {"class_type": class_type, "inputs": inputs}
        return node_id

    def link(self, node_id, class_type, *output_names):
        return [node_id, output_index(self.info, class_type, *output_names)]


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
    if not candidates:
        return None
    return max(candidates, key=os.path.getmtime)


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
    saved_schema = os.path.join(workspace, "object_info_wan_bf16.json")
    route_manifest = os.path.join(workspace, "wan_bf16_route.json")
    if not os.path.isfile(saved_schema):
        fail(f"schema proof missing: {saved_schema}")
    if not os.path.isfile(route_manifest):
        fail(f"route manifest missing: {route_manifest}")

    with open(route_manifest, "r", encoding="utf-8-sig") as fh:
        route = json.load(fh)

    print("W0: querying live ComfyUI node schema...", flush=True)
    info = request_json(base + "/object_info", timeout=120)
    live_schema_path = os.path.join(workspace, "object_info_w0_live.json")
    with open(live_schema_path, "w", encoding="utf-8") as fh:
        json.dump(info, fh, ensure_ascii=False, indent=2)

    required_classes = [
        "LoadImage",
        "LoadVideo",
        "GetVideoComponents",
        "ImageFromBatch",
        "CLIPLoader",
        "CLIPTextEncode",
        "CLIPVisionLoader",
        "CLIPVisionEncode",
        "VAELoader",
        "UNETLoader",
        "ModelSamplingSD3",
        "WanAnimate2ToVideo",
        "KSampler",
        "TrimVideoLatent",
        "VAEDecode",
        "CreateVideo",
        "SaveVideo",
    ]
    missing = [name for name in required_classes if name not in info]
    if missing:
        fail(f"live ComfyUI is missing required W0 node classes: {missing}")

    model_name = os.path.basename(route["model"])
    text_name = os.path.basename(route["text_encoder"])
    clip_name = os.path.basename(route["clip_vision"])
    vae_name = os.path.basename(route["vae"])
    ref_abs = route["official_w0_reference"]
    driver_abs = route["official_w0_driver"]
    for path in (route["model"], route["text_encoder"], route["clip_vision"], route["vae"], ref_abs, driver_abs):
        if not os.path.isfile(path):
            fail(f"W0 asset missing: {path}")

    input_root = os.path.join(comfy_root, "input")
    ref_rel = os.path.relpath(ref_abs, input_root).replace("\\", "/")
    driver_rel = os.path.relpath(driver_abs, input_root).replace("\\", "/")
    if ref_rel.startswith("../") or driver_rel.startswith("../"):
        fail("official W0 inputs are not under the active ComfyUI input directory")

    b = PromptBuilder(info)

    unet_inputs = {}
    unet_inputs[choose_input_name(info, "UNETLoader", "unet_name", "model_name")] = model_name
    if has_input(info, "UNETLoader", "weight_dtype"):
        unet_inputs["weight_dtype"] = "default"
    unet = b.add("UNETLoader", unet_inputs)

    sampled_model = b.add(
        "ModelSamplingSD3",
        {
            choose_input_name(info, "ModelSamplingSD3", "model"): b.link(unet, "UNETLoader", "MODEL", "model"),
            choose_input_name(info, "ModelSamplingSD3", "shift"): 5.0,
        },
    )

    clip_loader_inputs = {}
    clip_loader_inputs[choose_input_name(info, "CLIPLoader", "clip_name", "model_name")] = text_name
    if has_input(info, "CLIPLoader", "type"):
        clip_loader_inputs["type"] = "wan"
    if has_input(info, "CLIPLoader", "device"):
        clip_loader_inputs["device"] = "default"
    clip_text = b.add("CLIPLoader", clip_loader_inputs)

    positive = b.add(
        "CLIPTextEncode",
        {
            "text": UPSTREAM_PROMPT,
            "clip": b.link(clip_text, "CLIPLoader", "CLIP", "clip"),
        },
    )
    negative = b.add(
        "CLIPTextEncode",
        {
            "text": UPSTREAM_NEGATIVE,
            "clip": b.link(clip_text, "CLIPLoader", "CLIP", "clip"),
        },
    )

    vae = b.add(
        "VAELoader",
        {choose_input_name(info, "VAELoader", "vae_name", "model_name"): vae_name},
    )
    clip_vision = b.add(
        "CLIPVisionLoader",
        {choose_input_name(info, "CLIPVisionLoader", "clip_name", "model_name"): clip_name},
    )

    ref_load = b.add(
        "LoadImage",
        {choose_input_name(info, "LoadImage", "image", "file"): ref_rel},
    )
    video_load = b.add(
        "LoadVideo",
        {choose_input_name(info, "LoadVideo", "file", "video"): driver_rel},
    )
    video_components = b.add(
        "GetVideoComponents",
        {"video": b.link(video_load, "LoadVideo", "VIDEO", "video")},
    )
    first_driver = b.add(
        "ImageFromBatch",
        {
            "image": b.link(video_components, "GetVideoComponents", "images", "IMAGE"),
            "batch_index": 0,
            "length": 1,
        },
    )

    ref_cv = b.add(
        "CLIPVisionEncode",
        {
            "clip_vision": b.link(clip_vision, "CLIPVisionLoader", "CLIP_VISION", "clip_vision"),
            "image": b.link(ref_load, "LoadImage", "IMAGE", "image"),
        },
    )
    driver_cv = b.add(
        "CLIPVisionEncode",
        {
            "clip_vision": b.link(clip_vision, "CLIPVisionLoader", "CLIP_VISION", "clip_vision"),
            "image": b.link(first_driver, "ImageFromBatch", "IMAGE", "image"),
        },
    )

    wan_inputs = {
        "positive": b.link(positive, "CLIPTextEncode", "CONDITIONING", "conditioning"),
        "negative": b.link(negative, "CLIPTextEncode", "CONDITIONING", "conditioning"),
        "vae": b.link(vae, "VAELoader", "VAE", "vae"),
        "width": 640,
        "height": 800,
        "length": 37,
        "batch_size": 1,
        "reference_image": b.link(ref_load, "LoadImage", "IMAGE", "image"),
        "pose_video": b.link(video_components, "GetVideoComponents", "images", "IMAGE"),
        "clip_vision_output": b.link(ref_cv, "CLIPVisionEncode", "CLIP_VISION_OUTPUT", "clip_vision_output"),
        "video_frame_offset": 0,
        "pose_strength": 1.0,
        "pose_start_percent": 0.0,
        "pose_end_percent": 1.0,
        "reference_image_strength": 1.0,
    }
    if has_input(info, "WanAnimate2ToVideo", "positive_pose"):
        wan_inputs["positive_pose"] = b.link(positive, "CLIPTextEncode", "CONDITIONING", "conditioning")
    if has_input(info, "WanAnimate2ToVideo", "clip_vision_output_pose"):
        wan_inputs["clip_vision_output_pose"] = b.link(
            driver_cv, "CLIPVisionEncode", "CLIP_VISION_OUTPUT", "clip_vision_output"
        )
    wan_inputs = {k: v for k, v in wan_inputs.items() if has_input(info, "WanAnimate2ToVideo", k)}
    wan = b.add("WanAnimate2ToVideo", wan_inputs)

    sampler = b.add(
        "KSampler",
        {
            "model": b.link(sampled_model, "ModelSamplingSD3", "MODEL", "model"),
            "positive": b.link(wan, "WanAnimate2ToVideo", "positive"),
            "negative": b.link(wan, "WanAnimate2ToVideo", "negative"),
            "latent_image": b.link(wan, "WanAnimate2ToVideo", "latent"),
            "seed": 0,
            "steps": 20,
            "cfg": 1.0,
            "sampler_name": "euler",
            "scheduler": "simple",
            "denoise": 1.0,
        },
    )

    trimmed = b.add(
        "TrimVideoLatent",
        {
            "samples": b.link(sampler, "KSampler", "LATENT", "latent"),
            "trim_amount": b.link(wan, "WanAnimate2ToVideo", "trim_latent"),
        },
    )
    decoded = b.add(
        "VAEDecode",
        {
            "samples": b.link(trimmed, "TrimVideoLatent", "LATENT", "latent"),
            "vae": b.link(vae, "VAELoader", "VAE", "vae"),
        },
    )
    video = b.add(
        "CreateVideo",
        {
            "images": b.link(decoded, "VAEDecode", "IMAGE", "image"),
            "fps": 16.0,
        },
    )

    output_prefix = "roguelite_w0/wan_animate2_bf16_official"
    save_inputs = {
        "video": b.link(video, "CreateVideo", "VIDEO", "output", "video"),
        "filename_prefix": output_prefix,
        "format": "mp4",
        "codec": "h264",
    }
    save_inputs = {k: v for k, v in save_inputs.items() if has_input(info, "SaveVideo", k)}
    save = b.add("SaveVideo", save_inputs)

    prompt_path = os.path.join(workspace, "w0_api_prompt.json")
    with open(prompt_path, "w", encoding="utf-8") as fh:
        json.dump(b.prompt, fh, ensure_ascii=False, indent=2)

    run_manifest = {
        "gate": "WAN_ANIMATE2_W0_BF16_OFFICIAL_BASELINE",
        "status": "PROMPT_BUILT",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "route": "base_bf16_repo_yaml_semantics",
        "model": model_name,
        "text_encoder": text_name,
        "clip_vision": clip_name,
        "vae": vae_name,
        "reference": ref_rel,
        "driver": driver_rel,
        "width": 640,
        "height": 800,
        "length": 37,
        "fps": 16,
        "steps": 20,
        "cfg": 1.0,
        "sampler": "euler",
        "scheduler": "simple",
        "shift": 5.0,
        "seed": 0,
        "pose_strength": 1.0,
        "reference_image_strength": 1.0,
        "prompt": UPSTREAM_PROMPT,
        "negative_prompt": UPSTREAM_NEGATIVE,
        "prompt_file": prompt_path,
        "live_schema_file": live_schema_path,
        "save_node": save,
        "output_prefix": output_prefix,
    }
    run_manifest_path = os.path.join(workspace, "w0_run_manifest.json")
    with open(run_manifest_path, "w", encoding="utf-8") as fh:
        json.dump(run_manifest, fh, ensure_ascii=False, indent=2)

    print("W0: API prompt built from the live installed schema.", flush=True)
    print(f"W0: prompt file: {prompt_path}", flush=True)
    print("W0: submitting official reference + official driver...", flush=True)
    started = time.time()
    response = request_json(base + "/prompt", {"prompt": b.prompt}, timeout=120)
    prompt_id = response.get("prompt_id")
    if not prompt_id:
        fail(f"ComfyUI did not return prompt_id: {response}")
    print(f"W0: prompt_id={prompt_id}", flush=True)

    deadline = started + args.timeout_minutes * 60
    last_report = 0
    final_entry = None
    while time.time() < deadline:
        history = request_json(base + f"/history/{prompt_id}", timeout=120)
        entry = history.get(prompt_id)
        if entry:
            status = entry.get("status", {})
            if status.get("completed"):
                final_entry = entry
                break
            messages = status.get("messages") or []
            for message in messages:
                if isinstance(message, list) and message and message[0] == "execution_error":
                    run_manifest["status"] = "INFERENCE_ERROR"
                    run_manifest["error"] = message
                    with open(run_manifest_path, "w", encoding="utf-8") as fh:
                        json.dump(run_manifest, fh, ensure_ascii=False, indent=2)
                    fail(f"ComfyUI execution_error: {message}")
        now = time.time()
        if now - last_report >= 30:
            elapsed = int(now - started)
            print(f"W0: inference still running... {elapsed // 60}m {elapsed % 60:02d}s", flush=True)
            last_report = now
        time.sleep(5)

    if final_entry is None:
        run_manifest["status"] = "TIMEOUT"
        with open(run_manifest_path, "w", encoding="utf-8") as fh:
            json.dump(run_manifest, fh, ensure_ascii=False, indent=2)
        fail(f"inference did not complete within {args.timeout_minutes} minutes")

    output_file = newest_output(comfy_root, output_prefix, started)
    if not output_file:
        run_manifest["status"] = "OUTPUT_NOT_FOUND"
        run_manifest["history"] = final_entry
        with open(run_manifest_path, "w", encoding="utf-8") as fh:
            json.dump(run_manifest, fh, ensure_ascii=False, indent=2)
        fail("ComfyUI completed the prompt but the expected saved video could not be located")

    canonical = os.path.join(workspace, "w0_official_baseline.mp4")
    shutil.copy2(output_file, canonical)
    run_manifest["status"] = "INFERENCE_COMPLETE"
    run_manifest["prompt_id"] = prompt_id
    run_manifest["elapsed_seconds"] = round(time.time() - started, 2)
    run_manifest["comfy_output"] = output_file
    run_manifest["canonical_output"] = canonical
    run_manifest["output_bytes"] = os.path.getsize(canonical)
    with open(run_manifest_path, "w", encoding="utf-8") as fh:
        json.dump(run_manifest, fh, ensure_ascii=False, indent=2)

    print("", flush=True)
    print("WAN-ANIMATE2 W0 BF16: INFERENCE COMPLETE", flush=True)
    print(f"Output:   {canonical}", flush=True)
    print(f"Manifest: {run_manifest_path}", flush=True)
    print("The output is now ready for visual W0 baseline judgment; no Exilada inference has been run yet.", flush=True)


if __name__ == "__main__":
    main()
