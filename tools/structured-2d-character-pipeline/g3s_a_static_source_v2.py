from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import time
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageStat

W, H, HERO = 640, 360, 128
BG = (18, 18, 22)
MODEL = "Qwen-Image-Edit-2509-Q4_0.gguf"
CLIP = "qwen_2.5_vl_7b_fp8_scaled.safetensors"
VAE = "qwen_image_vae.safetensors"
WORKFLOW_REVISION = "QWEN2509_OFFICIAL_ALIGNED_NATIVE_V2"
OFFICIAL_BLUEPRINT = "Comfy-Org/ComfyUI blueprints/Image Edit (Qwen 2509).json @ 250b2e9551a7bc7a8ebb5beb07e0fecd2983e04a"

PROMPT = """Picture 1 is the target gameplay canvas and pose/placement/scale guide that must be transformed. Picture 2 is the exact Exilada identity/design reference.

Replace the guide figure in Picture 1 with exactly one full-body Exilada gameplay sprite while keeping the 640x360 canvas, the indicated placement, and approximately 128 pixels of visible character height. Use a lateral/slight three-quarter view facing screen-right.

Preserve Picture 2 identity/design: adult lean resilient female anatomy, severe readable head/face silhouette, olive-brown skin, extremely long heavy black hair as a dominant silhouette mass, minimal degraded asymmetric beige cloth, scars/wounds, wrist shackles, ankle shackles, barefoot, no weapon.

Topology is strict: exactly one head, one torso, two arms, two hands, two legs and two feet. No duplicated, missing, fused or extra major limbs. Both feet and both hands must remain readable and anatomically distinct.

Visible style must read as intentional modern pixel art at the native gameplay raster: deliberate connected pixel clusters, hard pixel edges, restrained 24-32 color character palette, purposeful value grouping, and material-specific cluster language for hair, skin, cloth and metal. Do not make a conventional 3D render blocky. Do not use smooth gradients, painterly brush texture, soft focus, faux CRT effects, or antialiased pseudo-pixels.

The background must remain completely empty and visually flat, as close as possible to RGB 18,18,22 (#121216). No floor, cast shadow, scenery, text, interface, border, particles or props."""

# The official Qwen 2509 blueprint uses an empty negative prompt with the same
# reference images and VAE wiring. Keep that structure here; topology/style
# constraints live in the positive instruction.
NEGATIVE = ""


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda: f.read(1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()


def http_json(url: str, method="GET", payload=None, timeout=30):
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    headers = {} if payload is None else {"Content-Type": "application/json"}
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def choice_values(node, name):
    for bucket in ("required", "optional"):
        spec = (node.get("input", {}).get(bucket, {}) or {}).get(name)
        if isinstance(spec, list) and spec and isinstance(spec[0], list):
            return list(spec[0])
    return []


def validate_schema(schema):
    required = [
        "UnetLoaderGGUF", "CLIPLoader", "VAELoader", "LoadImage",
        "TextEncodeQwenImageEditPlus", "ModelSamplingAuraFlow", "CFGNorm",
        "VAEEncode", "KSampler", "VAEDecode", "SaveImage",
    ]
    missing = [n for n in required if n not in schema]
    if missing:
        raise RuntimeError("G3S-A V2 runtime missing nodes: " + ", ".join(missing))

    plus = set()
    for bucket in ("required", "optional"):
        plus.update((schema["TextEncodeQwenImageEditPlus"].get("input", {}).get(bucket, {}) or {}).keys())
    need = {"clip", "prompt", "vae", "image1", "image2"}
    if not need.issubset(plus):
        raise RuntimeError("TextEncodeQwenImageEditPlus missing inputs: " + ", ".join(sorted(need - plus)))

    checks = [
        ("UnetLoaderGGUF", "unet_name", MODEL),
        ("CLIPLoader", "clip_name", CLIP),
        ("CLIPLoader", "type", "qwen_image"),
        ("VAELoader", "vae_name", VAE),
    ]
    for node, field, expected in checks:
        values = choice_values(schema[node], field)
        if values and expected not in values:
            raise RuntimeError(f"Runtime {node}.{field} does not expose {expected}")


def make_guide(path: Path):
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    p = {
        "head": (320, 122), "neck": (320, 140), "hip": (319, 184),
        "ls": (312, 145), "le": (304, 168), "lh": (309, 190),
        "rs": (328, 145), "re": (337, 168), "rh": (342, 187),
        "lk": (309, 211), "lf": (300, 242), "rk": (328, 210), "rf": (338, 242),
    }
    lines = [
        ("head", "neck"), ("neck", "hip"),
        ("neck", "ls"), ("ls", "le"), ("le", "lh"),
        ("neck", "rs"), ("rs", "re"), ("re", "rh"),
        ("hip", "lk"), ("lk", "lf"), ("hip", "rk"), ("rk", "rf"),
    ]
    for a, b in lines:
        d.line([p[a], p[b]], fill=(185, 185, 195), width=5)
    d.ellipse((311, 112, 329, 130), outline=(185, 185, 195), width=4)
    for x, y in p.values():
        d.ellipse((x - 3, y - 3, x + 3, y + 3), fill=(235, 210, 90))
    for x, y, sx, sy in [(290,116,1,1),(350,116,-1,1),(290,243,1,-1),(350,243,-1,-1)]:
        d.line((x, y, x + 8 * sx, y), fill=(75, 75, 90), width=1)
        d.line((x, y, x, y + 8 * sy), fill=(75, 75, 90), width=1)
    im.save(path, "PNG")


def graph(master_name: str, guide_name: str, seed: int):
    # Native-raster adaptation of the official ComfyUI Qwen 2509 blueprint.
    # Critical invariants versus the rejected V1 graph:
    # - image1 is the SAME guide image used as latent_image;
    # - image2 is the canonical identity reference;
    # - positive and negative conditioning receive the same refs + VAE;
    # - model path includes ModelSamplingAuraFlow -> CFGNorm;
    # - non-Lightning Comfy-original sampling uses 20 steps / CFG 2.5.
    # FluxKontextImageScale is intentionally omitted because it would upscale
    # image1 to a preferred ~1MP raster; G3S-A must test a real 640x360 output.
    return {
        "1": {"class_type":"UnetLoaderGGUF", "inputs":{"unet_name":MODEL}},
        "2": {"class_type":"ModelSamplingAuraFlow", "inputs":{"shift":3.0, "model":["1",0]}},
        "3": {"class_type":"CFGNorm", "inputs":{"strength":1.0, "model":["2",0]}},
        "4": {"class_type":"CLIPLoader", "inputs":{"clip_name":CLIP, "type":"qwen_image", "device":"default"}},
        "5": {"class_type":"VAELoader", "inputs":{"vae_name":VAE}},
        "6": {"class_type":"LoadImage", "inputs":{"image":guide_name}},
        "7": {"class_type":"LoadImage", "inputs":{"image":master_name}},
        "8": {"class_type":"TextEncodeQwenImageEditPlus", "inputs":{
            "clip":["4",0], "vae":["5",0], "image1":["6",0], "image2":["7",0], "prompt":PROMPT}},
        "9": {"class_type":"TextEncodeQwenImageEditPlus", "inputs":{
            "clip":["4",0], "vae":["5",0], "image1":["6",0], "image2":["7",0], "prompt":NEGATIVE}},
        "10": {"class_type":"VAEEncode", "inputs":{"pixels":["6",0], "vae":["5",0]}},
        "11": {"class_type":"KSampler", "inputs":{
            "seed":int(seed), "steps":20, "cfg":2.5,
            "sampler_name":"euler", "scheduler":"simple", "denoise":1.0,
            "model":["3",0], "positive":["8",0], "negative":["9",0], "latent_image":["10",0]}},
        "12": {"class_type":"VAEDecode", "inputs":{"samples":["11",0], "vae":["5",0]}},
        "13": {"class_type":"SaveImage", "inputs":{"filename_prefix":"G3SA_Qwen2509_Static_V2", "images":["12",0]}},
    }


def wait_history(api: str, prompt_id: str, timeout_s: int):
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        try:
            hist = http_json(f"{api}/history/{prompt_id}", timeout=20)
            item = hist.get(prompt_id)
            if item:
                status = item.get("status") or {}
                if status.get("completed") is True:
                    return item
                for msg in status.get("messages") or []:
                    if isinstance(msg, list) and msg and msg[0] == "execution_error":
                        raise RuntimeError("ComfyUI execution_error: " + repr(msg))
        except urllib.request.URLError:
            pass
        time.sleep(1)
    raise RuntimeError(f"Timed out waiting for Qwen inference after {timeout_s}s")


def saved_image(item, comfy_root: Path):
    outputs = item.get("outputs") or {}
    images = (outputs.get("13") or {}).get("images") or []
    if not images:
        for out in outputs.values():
            if isinstance(out, dict) and out.get("images"):
                images = out["images"]
                break
    if not images:
        raise RuntimeError("ComfyUI history contains no saved image")
    info = images[0]
    kind = info.get("type") or "output"
    base = comfy_root / ("output" if kind == "output" else kind)
    p = base / (info.get("subfolder") or "") / info["filename"]
    if not p.exists():
        raise RuntimeError(f"ComfyUI reported output missing on disk: {p}")
    return p


def percentile_from_hist(hist, q: float) -> int:
    total = sum(hist)
    target = total * q
    acc = 0
    for value, count in enumerate(hist):
        acc += count
        if acc >= target:
            return value
    return 255


def sanity_metrics(raw_path: Path):
    im = Image.open(raw_path).convert("RGB")
    if im.size != (W, H):
        raise RuntimeError(f"G3S-A V2 must remain native {W}x{H}; got {im.size}")
    gray = im.convert("L")
    hist = gray.histogram()
    p99 = percentile_from_hist(hist, 0.99)
    mean = float(ImageStat.Stat(gray).mean[0])
    target = gray.crop((270, 96, 370, 260))
    target_hist = target.histogram()
    target_p95 = percentile_from_hist(target_hist, 0.95)
    target_mean = float(ImageStat.Stat(target).mean[0])
    target_std = float(ImageStat.Stat(target).stddev[0])
    metrics = {
        "mean_luma": round(mean, 4),
        "p99_luma": int(p99),
        "target_mean_luma": round(target_mean, 4),
        "target_p95_luma": int(target_p95),
        "target_std_luma": round(target_std, 4),
    }
    # The V1 black-collapse output had essentially no usable dynamic range in
    # the target area. These bounds are deliberately loose; they only reject
    # empty/near-black inference, not artistic quality.
    if p99 < 24 or target_p95 < 28 or target_std < 4.0:
        raise RuntimeError("G3S-A V2 invalid near-black/flat inference: " + repr(metrics))
    return metrics


def same_raster_quantized(raw_path: Path, out_path: Path):
    im = Image.open(raw_path).convert("RGB")
    if im.size != (W, H):
        raise RuntimeError(f"G3S-A must remain native {W}x{H}; got {im.size}")
    q = im.quantize(colors=32, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).convert("RGB")
    q.save(out_path, "PNG")
    return len(set(q.getdata()))


def make_sheet(guide_path: Path, raw_path: Path, q_path: Path, out_path: Path):
    guide = Image.open(guide_path).convert("RGB")
    raw = Image.open(raw_path).convert("RGB")
    q = Image.open(q_path).convert("RGB")
    crop = q.crop((270, 96, 370, 260))
    zoom = crop.resize((400, 656), Image.Resampling.NEAREST)
    zoom_panel = Image.new("RGB", (W, H), (34, 34, 40))
    zc = zoom.crop((0, 148, 400, 508))
    zoom_panel.paste(zc, ((W - 400) // 2, 0))
    panels = [guide, raw, q, zoom_panel]
    labels = [
        "A guide - primary edit image / latent",
        "B Qwen V2 raw native 640x360",
        "C 32-color same-raster inspection, no resize",
        "D nearest-neighbor zoom of target area",
    ]
    sheet = Image.new("RGB", (W * 2, H * 2), (8, 8, 10))
    d = ImageDraw.Draw(sheet)
    for i, panel in enumerate(panels):
        ox = (i % 2) * W
        oy = (i // 2) * H
        sheet.paste(panel, (ox, oy))
        d.rectangle((ox + 6, oy + 6, ox + 465, oy + 30), fill=(0, 0, 0))
        d.text((ox + 12, oy + 11), labels[i], fill=(255, 255, 255))
    sheet.save(out_path, "PNG")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--api", required=True)
    ap.add_argument("--comfy-root", required=True)
    ap.add_argument("--master", required=True)
    ap.add_argument("--output-dir", required=True)
    ap.add_argument("--seed", type=int, default=20260905)
    ap.add_argument("--timeout-seconds", type=int, default=2700)
    a = ap.parse_args()

    api = a.api.rstrip("/")
    comfy_root = Path(a.comfy_root).resolve()
    master = Path(a.master).resolve()
    out = Path(a.output_dir).resolve()
    inp = comfy_root / "input"
    out.mkdir(parents=True, exist_ok=True)
    inp.mkdir(parents=True, exist_ok=True)
    if not master.exists():
        raise RuntimeError(f"Canonical Exilada master missing: {master}")

    master_name = "g3s_a_exilada_master.png"
    guide_name = "g3s_a_layout_640x360.png"
    master_copy = inp / master_name
    guide_copy = inp / guide_name
    shutil.copy2(master, master_copy)
    if sha256(master) != sha256(master_copy):
        raise RuntimeError("Canonical master copy SHA256 mismatch")
    make_guide(guide_copy)
    guide_out = out / "g3s_a_layout_guide.png"
    shutil.copy2(guide_copy, guide_out)

    schema = http_json(f"{api}/object_info", timeout=30)
    validate_schema(schema)
    print("G3S_A_SCHEMA=PASS")
    print("G3S_A_WORKFLOW=" + WORKFLOW_REVISION)
    print("G3S_A_PRIMARY_IMAGE=LAYOUT_GUIDE")
    print("G3S_A_PRIMARY_IMAGE_EQUALS_LATENT=TRUE")
    print("G3S_A_IDENTITY_REFERENCE=CANONICAL_MASTER_IMAGE2")
    print("G3S_A_CFGNORM=ENABLED_STRENGTH_1")
    print("G3S_A_SAMPLING=20_STEPS_CFG_2.5_EULER_SIMPLE")
    print("G3S_A_GENERATIVE_SCOPE=STATIC_SOURCE_ONLY")
    print("G3S_A_CANVAS=640x360")
    print("G3S_A_TARGET_HERO_PX=128")
    print("G3S_A_POST_INFERENCE_RESIZE=DISABLED")

    wf = graph(master_name, guide_name, a.seed)
    wf_path = out / "g3s_a_workflow_api.json"
    wf_path.write_text(json.dumps(wf, indent=2), encoding="utf-8")
    submitted = http_json(f"{api}/prompt", method="POST", payload={"prompt":wf, "client_id":"roguelite-g3s-a-v2"}, timeout=60)
    prompt_id = submitted.get("prompt_id")
    if not prompt_id:
        raise RuntimeError("ComfyUI did not return prompt_id: " + repr(submitted))
    print("G3S_A_INFERENCE_SUBMITTED=" + prompt_id)

    item = wait_history(api, prompt_id, a.timeout_seconds)
    source = saved_image(item, comfy_root)
    raw = out / "g3s_a_qwen_raw.png"
    shutil.copy2(source, raw)

    try:
        metrics = sanity_metrics(raw)
    except Exception as exc:
        invalid = {
            "gate":"G3S-A",
            "status":"FAIL_INVALID_INFERENCE",
            "workflow_revision":WORKFLOW_REVISION,
            "raw":str(raw),
            "raw_sha256":sha256(raw),
            "reason":str(exc),
        }
        (out / "g3s_a_invalid_inference.json").write_text(json.dumps(invalid, indent=2), encoding="utf-8")
        raise
    print("G3S_A_RAW_SANITY=PASS " + json.dumps(metrics, sort_keys=True))

    q = out / "g3s_a_same_raster_32color.png"
    colors = same_raster_quantized(raw, q)
    contact = out / "g3s_a_contact_sheet.png"
    make_sheet(guide_out, raw, q, contact)

    result = {
        "gate":"G3S-A",
        "status":"REVIEW_REQUIRED",
        "purpose":"one static gameplay-scale Exilada source-art candidate before any 2D decomposition or animation",
        "workflow_revision":WORKFLOW_REVISION,
        "workflow_reference":OFFICIAL_BLUEPRINT,
        "native_deviation":"FluxKontextImageScale intentionally omitted so primary latent remains 640x360; all critical Qwen edit conditioning/model-chain relationships follow the official blueprint.",
        "model":MODEL,
        "clip":CLIP,
        "vae":VAE,
        "seed":a.seed,
        "sampling":{"steps":20,"cfg":2.5,"sampler":"euler","scheduler":"simple","denoise":1.0,"model_sampling_shift":3.0,"cfg_norm_strength":1.0},
        "master":str(master),
        "master_sha256":sha256(master),
        "canvas":[W,H],
        "target_visible_height_px":HERO,
        "prompt":PROMPT,
        "negative":NEGATIVE,
        "raw":str(raw),
        "raw_sha256":sha256(raw),
        "raw_sanity":metrics,
        "same_raster_32color":str(q),
        "same_raster_32color_sha256":sha256(q),
        "same_raster_visible_colors":colors,
        "contact_sheet":str(contact),
        "contact_sheet_sha256":sha256(contact),
        "workflow_api":str(wf_path),
        "rules":{
            "post_inference_resize":False,
            "same_raster_quantization_is_inspection_only":True,
            "direct_frame_animation_generation":False,
            "visual_review_required":True,
            "review_order":[
                "topology: exactly one head/torso, two arms/hands, two legs/feet",
                "Exilada identity/design continuity",
                "approximately 128 px gameplay scale and slight 3/4 side presentation",
                "intentional modern pixel cluster language at native 1x",
                "hair/cloth/restraint readability",
            ],
        },
    }
    result_path = out / "g3s_a_result.json"
    result_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"G3S_A_NATIVE_COLORS={colors}")
    print("G3S_A_NO_RESIZE=TRUE")
    print("G3S_A_CONTACT_SHEET=" + str(contact))
    print("G3S_A_RESULT=" + str(result_path))
    print("G3S_A=REVIEW_REQUIRED")


if __name__ == "__main__":
    main()
