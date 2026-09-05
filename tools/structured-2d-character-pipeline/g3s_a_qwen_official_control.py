from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import time
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageStat

W, H = 640, 360
BG = (18, 18, 22)
MODEL = "Qwen-Image-Edit-2509-Q4_0.gguf"
CLIP = "qwen_2.5_vl_7b_fp8_scaled.safetensors"
VAE = "qwen_image_vae.safetensors"
REVISION = "QWEN2509_OFFICIAL_RESOLUTION_CONTROL_V1"

PROMPT = """Picture 1 is the target gameplay composition guide. Picture 2 is the exact Exilada identity/design reference.

Replace the guide figure in Picture 1 with exactly one full-body Exilada character in a lateral/slight three-quarter view facing screen-right. Preserve Picture 2 identity/design: adult lean resilient woman, olive-brown skin, severe head silhouette, extremely long heavy black hair, degraded asymmetric beige cloth, wrist and ankle shackles, bare feet, no weapon. Exactly one head and torso, two arms/hands and two legs/feet. Empty flat dark background, no floor, shadow, scenery, text or props.

This run is a model-function control, not final production art."""


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
        "FluxKontextImageScale", "TextEncodeQwenImageEditPlus",
        "ModelSamplingAuraFlow", "CFGNorm", "VAEEncode", "KSampler",
        "VAEDecode", "SaveImage",
    ]
    missing = [n for n in required if n not in schema]
    if missing:
        raise RuntimeError("Qwen official control missing runtime nodes: " + ", ".join(missing))
    for node, field, expected in [
        ("UnetLoaderGGUF", "unet_name", MODEL),
        ("CLIPLoader", "clip_name", CLIP),
        ("CLIPLoader", "type", "qwen_image"),
        ("VAELoader", "vae_name", VAE),
    ]:
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
    im.save(path, "PNG")


def graph(master_name: str, guide_name: str, seed: int):
    # This deliberately restores FluxKontextImageScale from the official
    # ComfyUI Qwen 2509 blueprint. The resulting raster is NOT a production
    # sprite candidate and MUST NOT be downscaled/promoted by this script.
    return {
        "1": {"class_type":"UnetLoaderGGUF", "inputs":{"unet_name":MODEL}},
        "2": {"class_type":"ModelSamplingAuraFlow", "inputs":{"shift":3.0, "model":["1",0]}},
        "3": {"class_type":"CFGNorm", "inputs":{"strength":1.0, "model":["2",0]}},
        "4": {"class_type":"CLIPLoader", "inputs":{"clip_name":CLIP, "type":"qwen_image", "device":"default"}},
        "5": {"class_type":"VAELoader", "inputs":{"vae_name":VAE}},
        "6": {"class_type":"LoadImage", "inputs":{"image":guide_name}},
        "7": {"class_type":"LoadImage", "inputs":{"image":master_name}},
        "8": {"class_type":"FluxKontextImageScale", "inputs":{"image":["6",0]}},
        "9": {"class_type":"TextEncodeQwenImageEditPlus", "inputs":{
            "clip":["4",0], "vae":["5",0], "image1":["8",0], "image2":["7",0], "prompt":PROMPT}},
        "10": {"class_type":"TextEncodeQwenImageEditPlus", "inputs":{
            "clip":["4",0], "vae":["5",0], "image1":["8",0], "image2":["7",0], "prompt":""}},
        "11": {"class_type":"VAEEncode", "inputs":{"pixels":["8",0], "vae":["5",0]}},
        "12": {"class_type":"KSampler", "inputs":{
            "seed":int(seed), "steps":20, "cfg":2.5,
            "sampler_name":"euler", "scheduler":"simple", "denoise":1.0,
            "model":["3",0], "positive":["9",0], "negative":["10",0], "latent_image":["11",0]}},
        "13": {"class_type":"VAEDecode", "inputs":{"samples":["12",0], "vae":["5",0]}},
        "14": {"class_type":"SaveImage", "inputs":{"filename_prefix":"G3SA_Qwen2509_OfficialControl", "images":["13",0]}},
    }


def wait_history(api: str, prompt_id: str, timeout_s: int):
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        hist = http_json(f"{api}/history/{prompt_id}", timeout=20)
        item = hist.get(prompt_id)
        if item:
            status = item.get("status") or {}
            if status.get("completed") is True:
                return item
            for msg in status.get("messages") or []:
                if isinstance(msg, list) and msg and msg[0] == "execution_error":
                    raise RuntimeError("ComfyUI execution_error: " + repr(msg))
        time.sleep(1)
    raise RuntimeError(f"Timed out waiting for Qwen control after {timeout_s}s")


def saved_image(item, comfy_root: Path):
    outputs = item.get("outputs") or {}
    images = (outputs.get("14") or {}).get("images") or []
    if not images:
        raise RuntimeError("ComfyUI history contains no control image")
    info = images[0]
    base = comfy_root / ("output" if (info.get("type") or "output") == "output" else info.get("type"))
    p = base / (info.get("subfolder") or "") / info["filename"]
    if not p.exists():
        raise RuntimeError(f"ComfyUI reported control output missing: {p}")
    return p


def metrics(path: Path):
    im = Image.open(path).convert("RGB")
    gray = im.convert("L")
    st = ImageStat.Stat(gray)
    hist = gray.histogram()
    total = sum(hist)
    acc = 0
    p99 = 255
    for i, n in enumerate(hist):
        acc += n
        if acc >= total * 0.99:
            p99 = i
            break
    return {
        "size": list(im.size),
        "mean_luma": round(float(st.mean[0]), 4),
        "std_luma": round(float(st.stddev[0]), 4),
        "p99_luma": int(p99),
    }


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

    master_name = "g3s_a_control_exilada_master.png"
    guide_name = "g3s_a_control_layout.png"
    shutil.copy2(master, inp / master_name)
    make_guide(inp / guide_name)

    schema = http_json(f"{api}/object_info", timeout=30)
    validate_schema(schema)
    print("G3S_A_CONTROL_SCHEMA=PASS")
    print("G3S_A_CONTROL_REVISION=" + REVISION)
    print("G3S_A_CONTROL_FLUX_KONTEXT_SCALE=ENABLED")
    print("G3S_A_CONTROL_FINAL_ART_ELIGIBLE=FALSE")
    print("G3S_A_CONTROL_POST_RESIZE=FORBIDDEN")

    wf = graph(master_name, guide_name, a.seed)
    (out / "g3s_a_control_workflow_api.json").write_text(json.dumps(wf, indent=2), encoding="utf-8")
    submitted = http_json(f"{api}/prompt", method="POST", payload={"prompt":wf,"client_id":"roguelite-g3s-a-control"}, timeout=60)
    prompt_id = submitted.get("prompt_id")
    if not prompt_id:
        raise RuntimeError("ComfyUI did not return control prompt_id: " + repr(submitted))
    print("G3S_A_CONTROL_SUBMITTED=" + prompt_id)

    item = wait_history(api, prompt_id, a.timeout_seconds)
    source = saved_image(item, comfy_root)
    raw = out / "g3s_a_control_official_raw.png"
    shutil.copy2(source, raw)
    m = metrics(raw)
    collapsed = m["std_luma"] < 3.0 or m["p99_luma"] < 24
    result = {
        "gate":"G3S-A-CONTROL",
        "revision":REVISION,
        "status":"FAIL_MODEL_COLLAPSE" if collapsed else "REVIEW_CONTROL",
        "purpose":"determine whether Qwen 2509 functions under official preferred-resolution preprocessing; never a final sprite candidate",
        "model":MODEL,
        "seed":a.seed,
        "raw":str(raw),
        "raw_sha256":sha256(raw),
        "metrics":m,
        "rules":{
            "final_art_eligible":False,
            "post_resize_allowed":False,
            "native_640_route_already_failed":True,
        },
    }
    rp = out / "g3s_a_control_result.json"
    rp.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print("G3S_A_CONTROL_METRICS=" + json.dumps(m, sort_keys=True))
    print("G3S_A_CONTROL_RAW=" + str(raw))
    print("G3S_A_CONTROL_RESULT=" + str(rp))
    if collapsed:
        raise RuntimeError("Qwen official-resolution control also collapsed: " + repr(m))
    print("G3S_A_CONTROL=REVIEW_CONTROL")


if __name__ == "__main__":
    main()
