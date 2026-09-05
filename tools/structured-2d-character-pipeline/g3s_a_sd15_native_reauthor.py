from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import time
import urllib.request
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageStat

W, H, HERO = 640, 360, 128
BG = (18, 18, 22)
CHECKPOINT = "v1-5-pruned-emaonly.safetensors"
LORA = "pixel-art-sd15.safetensors"
REVISION = "SD15_NATIVE_PIXEL_REAUTHOR_V1"

PROMPT = """pixel art sprite, full body adult woman, same subject and design as the input image, lean resilient anatomy, olive brown skin, severe face silhouette, extremely long heavy black hair, minimal degraded asymmetric beige cloth, wrist and ankle shackles, barefoot, no weapon, lateral slight three-quarter gameplay view facing right, exactly one head, one torso, two arms, two hands, two legs, two feet, deliberate connected pixel clusters, hard pixel edges, restrained palette, crisp material separation, empty solid dark background, game sprite"""

NEGATIVE = """extra limb, third leg, extra foot, duplicated hand, missing limb, fused limb, malformed anatomy, weapon, shoes, boots, floor, scenery, shadow, text, UI, frame, photorealistic, 3d render, smooth gradients, painterly, soft focus, anti-aliased edges, blurry, noisy, dithering, jpeg artifacts"""


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def http_json(url: str, method: str = "GET", payload=None, timeout: int = 30):
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
        "CheckpointLoaderSimple", "LoraLoader", "LoadImage", "VAEEncode",
        "CLIPTextEncode", "KSampler", "VAEDecode", "SaveImage",
    ]
    missing = [n for n in required if n not in schema]
    if missing:
        raise RuntimeError("G3S-A SD15 runtime missing nodes: " + ", ".join(missing))
    for node, field, expected in [
        ("CheckpointLoaderSimple", "ckpt_name", CHECKPOINT),
        ("LoraLoader", "lora_name", LORA),
    ]:
        values = choice_values(schema[node], field)
        if values and expected not in values:
            raise RuntimeError(f"Runtime {node}.{field} does not expose {expected}")


def estimate_background(im: Image.Image):
    px = im.load()
    samples = []
    w, h = im.size
    for y in range(0, min(32, h)):
        for x in range(0, min(32, w)):
            samples.append(px[x, y])
            samples.append(px[w - 1 - x, y])
            samples.append(px[x, h - 1 - y])
            samples.append(px[w - 1 - x, h - 1 - y])
    samples.sort(key=lambda p: sum(p))
    mid = samples[len(samples) // 2]
    return tuple(int(v) for v in mid)


def subject_bbox(im: Image.Image):
    bg = estimate_background(im)
    bgim = Image.new("RGB", im.size, bg)
    diff = ImageChops.difference(im, bgim).convert("L")
    mask = diff.point(lambda p: 255 if p >= 10 else 0)
    mask = mask.filter(ImageFilter.MaxFilter(5))
    bbox = mask.getbbox()
    if not bbox:
        raise RuntimeError("Could not segment Qwen control subject from background")
    x0, y0, x1, y1 = bbox
    pad = 10
    return (
        max(0, x0 - pad), max(0, y0 - pad),
        min(im.width, x1 + pad), min(im.height, y1 + pad),
    )


def make_reauthor_guide(control_path: Path, out_path: Path):
    src = Image.open(control_path).convert("RGB")
    bbox = subject_bbox(src)
    crop = src.crop(bbox)
    scale = HERO / max(1, crop.height)
    nw = max(1, round(crop.width * scale))
    resized = crop.resize((nw, HERO), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", (W, H), BG)
    x = W // 2 - nw // 2
    y = 116
    canvas.paste(resized, (x, y))
    canvas.save(out_path, "PNG")
    return {"source_size": list(src.size), "source_bbox": list(bbox), "guide_subject_size": [nw, HERO], "guide_xy": [x, y]}


def graph(source_name: str, seed: int):
    return {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": CHECKPOINT}},
        "2": {"class_type": "LoraLoader", "inputs": {
            "model": ["1", 0], "clip": ["1", 1], "lora_name": LORA,
            "strength_model": 1.0, "strength_clip": 1.0}},
        "3": {"class_type": "LoadImage", "inputs": {"image": source_name}},
        "4": {"class_type": "VAEEncode", "inputs": {"pixels": ["3", 0], "vae": ["1", 2]}},
        "5": {"class_type": "CLIPTextEncode", "inputs": {"text": PROMPT, "clip": ["2", 1]}},
        "6": {"class_type": "CLIPTextEncode", "inputs": {"text": NEGATIVE, "clip": ["2", 1]}},
        "7": {"class_type": "KSampler", "inputs": {
            "seed": int(seed), "steps": 30, "cfg": 6.0,
            "sampler_name": "dpmpp_2m", "scheduler": "karras", "denoise": 0.72,
            "model": ["2", 0], "positive": ["5", 0], "negative": ["6", 0], "latent_image": ["4", 0]}},
        "8": {"class_type": "VAEDecode", "inputs": {"samples": ["7", 0], "vae": ["1", 2]}},
        "9": {"class_type": "SaveImage", "inputs": {"filename_prefix": "G3SA_SD15_NativeReauthor", "images": ["8", 0]}},
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
    raise RuntimeError(f"Timed out waiting for SD1.5 native reauthor after {timeout_s}s")


def saved_image(item, comfy_root: Path):
    outputs = item.get("outputs") or {}
    images = (outputs.get("9") or {}).get("images") or []
    if not images:
        raise RuntimeError("ComfyUI history contains no SD1.5 output image")
    info = images[0]
    kind = info.get("type") or "output"
    base = comfy_root / ("output" if kind == "output" else kind)
    p = base / (info.get("subfolder") or "") / info["filename"]
    if not p.exists():
        raise RuntimeError(f"ComfyUI reported output missing: {p}")
    return p


def raw_metrics(path: Path):
    im = Image.open(path).convert("RGB")
    if im.size != (W, H):
        raise RuntimeError(f"Native reauthor must remain {W}x{H}; got {im.size}")
    gray = im.convert("L")
    st = ImageStat.Stat(gray)
    return {"size": list(im.size), "mean_luma": round(float(st.mean[0]), 4), "std_luma": round(float(st.stddev[0]), 4)}


def quantize_same_raster(raw: Path, out: Path):
    im = Image.open(raw).convert("RGB")
    q = im.quantize(colors=32, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).convert("RGB")
    q.save(out, "PNG")
    return len(set(q.getdata()))


def make_sheet(guide: Path, raw: Path, quant: Path, out: Path):
    a = Image.open(guide).convert("RGB")
    b = Image.open(raw).convert("RGB")
    c = Image.open(quant).convert("RGB")
    crop = c.crop((260, 92, 380, 264))
    zoom = crop.resize((480, 688), Image.Resampling.NEAREST)
    dpanel = Image.new("RGB", (W, H), (34, 34, 40))
    dpanel.paste(zoom.crop((0, 164, 480, 524)), ((W - 480) // 2, 0))
    panels = [a, b, c, dpanel]
    labels = [
        "A conditioning guide from Qwen control - NOT final art",
        "B SD1.5 + pixel LoRA raw native 640x360",
        "C 32-color same-raster inspection - no resize",
        "D nearest-neighbor zoom of target area",
    ]
    sheet = Image.new("RGB", (W * 2, H * 2), (8, 8, 10))
    dr = ImageDraw.Draw(sheet)
    for i, panel in enumerate(panels):
        ox, oy = (i % 2) * W, (i // 2) * H
        sheet.paste(panel, (ox, oy))
        dr.rectangle((ox + 6, oy + 6, ox + 500, oy + 30), fill=(0, 0, 0))
        dr.text((ox + 12, oy + 11), labels[i], fill=(255, 255, 255))
    sheet.save(out, "PNG")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--api", required=True)
    ap.add_argument("--comfy-root", required=True)
    ap.add_argument("--control", required=True)
    ap.add_argument("--output-dir", required=True)
    ap.add_argument("--seed", type=int, default=20260905)
    ap.add_argument("--timeout-seconds", type=int, default=1800)
    a = ap.parse_args()

    api = a.api.rstrip("/")
    comfy_root = Path(a.comfy_root).resolve()
    control = Path(a.control).resolve()
    out = Path(a.output_dir).resolve()
    inp = comfy_root / "input"
    out.mkdir(parents=True, exist_ok=True)
    inp.mkdir(parents=True, exist_ok=True)
    if not control.exists():
        raise RuntimeError(f"Qwen official control image missing: {control}")

    guide_local = out / "g3s_a_sd15_conditioning_guide.png"
    prep = make_reauthor_guide(control, guide_local)
    source_name = "g3s_a_sd15_conditioning_guide.png"
    shutil.copy2(guide_local, inp / source_name)

    schema = http_json(f"{api}/object_info", timeout=30)
    validate_schema(schema)
    print("G3S_A_SD15_SCHEMA=PASS")
    print("G3S_A_SD15_REVISION=" + REVISION)
    print("G3S_A_SD15_FINAL_RASTER=640x360_NATIVE")
    print("G3S_A_SD15_FINAL_POST_RESIZE=DISABLED")
    print("G3S_A_SD15_HIGHRES_QWEN_USED_AS_CONDITIONING_ONLY=TRUE")
    print("G3S_A_SD15_SOURCE_PREP=" + json.dumps(prep, sort_keys=True))

    wf = graph(source_name, a.seed)
    wf_path = out / "g3s_a_sd15_workflow_api.json"
    wf_path.write_text(json.dumps(wf, indent=2), encoding="utf-8")
    submitted = http_json(f"{api}/prompt", method="POST", payload={"prompt": wf, "client_id": "roguelite-g3s-a-sd15"}, timeout=60)
    prompt_id = submitted.get("prompt_id")
    if not prompt_id:
        raise RuntimeError("ComfyUI did not return SD1.5 prompt_id: " + repr(submitted))
    print("G3S_A_SD15_SUBMITTED=" + prompt_id)

    item = wait_history(api, prompt_id, a.timeout_seconds)
    source = saved_image(item, comfy_root)
    raw = out / "g3s_a_sd15_raw.png"
    shutil.copy2(source, raw)
    metrics = raw_metrics(raw)
    if metrics["std_luma"] < 4.0:
        raise RuntimeError("SD1.5 native reauthor output is implausibly flat: " + repr(metrics))
    print("G3S_A_SD15_RAW_SANITY=PASS " + json.dumps(metrics, sort_keys=True))

    quant = out / "g3s_a_sd15_same_raster_32color.png"
    colors = quantize_same_raster(raw, quant)
    contact = out / "g3s_a_sd15_contact_sheet.png"
    make_sheet(guide_local, raw, quant, contact)

    result = {
        "gate": "G3S-A-SD15",
        "status": "REVIEW_REQUIRED",
        "revision": REVISION,
        "purpose": "native-raster pixel reauthor of the coherent Qwen control, not a high-res shrink",
        "checkpoint": CHECKPOINT,
        "lora": LORA,
        "seed": a.seed,
        "sampling": {"steps": 30, "cfg": 6.0, "sampler": "dpmpp_2m", "scheduler": "karras", "denoise": 0.72},
        "control_source": str(control),
        "control_source_sha256": sha256(control),
        "conditioning_guide": str(guide_local),
        "conditioning_prep": prep,
        "raw": str(raw),
        "raw_sha256": sha256(raw),
        "raw_metrics": metrics,
        "same_raster_32color": str(quant),
        "same_raster_colors": colors,
        "contact_sheet": str(contact),
        "workflow_api": str(wf_path),
        "rules": {
            "final_raster": [W, H],
            "final_post_resize": False,
            "highres_qwen_is_conditioning_only": True,
            "same_raster_quantization_is_inspection_only": True,
            "direct_frame_animation_generation": False,
            "visual_review_required": True,
        },
    }
    rp = out / "g3s_a_sd15_result.json"
    rp.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print("G3S_A_SD15_CONTACT_SHEET=" + str(contact))
    print("G3S_A_SD15_RESULT=" + str(rp))
    print("G3S_A_SD15=REVIEW_REQUIRED")


if __name__ == "__main__":
    main()
