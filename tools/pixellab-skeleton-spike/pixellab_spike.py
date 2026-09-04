from __future__ import annotations

import argparse
import base64
import json
import math
import os
import sys
import time
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import requests
from PIL import Image, ImageDraw

API_BASE = "https://api.pixellab.ai/v2"
REQUIRED_LABELS = {
    "NOSE", "NECK",
    "RIGHT SHOULDER", "RIGHT ELBOW", "RIGHT ARM",
    "LEFT SHOULDER", "LEFT ELBOW", "LEFT ARM",
    "RIGHT HIP", "RIGHT KNEE", "RIGHT LEG",
    "LEFT HIP", "LEFT KNEE", "LEFT LEG",
}
CONNECTIONS = [
    ("NOSE", "NECK"),
    ("NECK", "RIGHT SHOULDER"), ("RIGHT SHOULDER", "RIGHT ELBOW"), ("RIGHT ELBOW", "RIGHT ARM"),
    ("NECK", "LEFT SHOULDER"), ("LEFT SHOULDER", "LEFT ELBOW"), ("LEFT ELBOW", "LEFT ARM"),
    ("RIGHT SHOULDER", "RIGHT HIP"), ("LEFT SHOULDER", "LEFT HIP"),
    ("RIGHT HIP", "LEFT HIP"),
    ("RIGHT HIP", "RIGHT KNEE"), ("RIGHT KNEE", "RIGHT LEG"),
    ("LEFT HIP", "LEFT KNEE"), ("LEFT KNEE", "LEFT LEG"),
]


class SpikeError(RuntimeError):
    pass


@dataclass
class Config:
    master: Path
    workspace: Path
    size: int = 128
    seed: int = 20260904
    palette_colors: int = 24
    view: str = "side"
    direction: str = "south-east"
    reference_guidance_scale: float = 1.1
    pose_guidance_scale: float = 3.0
    max_expected_usd: float = 0.06


def image_obj(path: Path) -> dict[str, str]:
    return {
        "type": "base64",
        "base64": base64.b64encode(path.read_bytes()).decode("ascii"),
        "format": "png",
    }


def save_base64_image(obj: dict[str, Any], path: Path) -> None:
    path.write_bytes(base64.b64decode(obj["base64"]))


def request_json(method: str, url: str, token: str, *, payload: dict[str, Any] | None = None, timeout: int = 180) -> requests.Response:
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    if payload is not None:
        headers["Content-Type"] = "application/json"
    return requests.request(method, url, headers=headers, json=payload, timeout=timeout)


def require_ok(resp: requests.Response, label: str) -> dict[str, Any]:
    try:
        data = resp.json()
    except Exception:
        data = {"raw": resp.text[:4000]}
    if not resp.ok:
        raise SpikeError(f"{label} failed: HTTP {resp.status_code}\n{json.dumps(data, indent=2, ensure_ascii=False)}")
    if not isinstance(data, dict):
        raise SpikeError(f"{label} returned an unexpected response shape")
    return data


def get_balance(token: str) -> float | None:
    for base in (API_BASE, "https://api.pixellab.ai/v1"):
        try:
            resp = request_json("GET", f"{base}/balance", token, timeout=30)
            if resp.ok:
                data = resp.json()
                if isinstance(data, dict) and isinstance(data.get("usd"), (int, float)):
                    return float(data["usd"])
        except requests.RequestException:
            pass
    return None


def estimate_skeleton(token: str, image_path: Path) -> tuple[list[dict[str, Any]], float]:
    payload = {"image": image_obj(image_path)}
    data = require_ok(request_json("POST", f"{API_BASE}/estimate-skeleton", token, payload=payload), "estimate-skeleton")
    keypoints = data.get("keypoints")
    if not isinstance(keypoints, list) or not keypoints:
        raise SpikeError("estimate-skeleton returned no keypoints")
    usage = float(((data.get("usage") or {}).get("usd") or 0.0))
    return keypoints, usage


def extract_images_from_response(data: dict[str, Any], token: str) -> tuple[list[dict[str, Any]], float, str | None]:
    usage = float(((data.get("usage") or {}).get("usd") or 0.0))
    images = data.get("images")
    if isinstance(images, list) and images:
        return images, usage, None
    job_id = data.get("job_id") or data.get("id")
    if not job_id:
        raise SpikeError("animate-with-skeleton returned neither images nor a job id")
    deadline = time.time() + 900
    while time.time() < deadline:
        status = require_ok(request_json("GET", f"{API_BASE}/background-jobs/{job_id}", token, timeout=30), "background job poll")
        state = str(status.get("status") or status.get("state") or "").lower()
        candidate = status.get("result") if isinstance(status.get("result"), dict) else status
        images = candidate.get("images") if isinstance(candidate, dict) else None
        if isinstance(images, list) and images:
            usage = float(((candidate.get("usage") or status.get("usage") or {}).get("usd") or usage))
            return images, usage, str(job_id)
        if state in {"failed", "error", "cancelled", "canceled"}:
            raise SpikeError(f"PixelLab background job {job_id} failed: {json.dumps(status, indent=2, ensure_ascii=False)}")
        time.sleep(3)
    raise SpikeError(f"Timed out waiting for PixelLab background job {job_id}")


def animate_with_skeleton(token: str, cfg: Config, reference: Path, palette_image: Path, pose_frames: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], float, dict[str, Any]]:
    common = {
        "image_size": {"width": cfg.size, "height": cfg.size},
        "reference_image": image_obj(reference),
        "view": cfg.view,
        "direction": cfg.direction,
        "isometric": False,
        "oblique_projection": False,
        "reference_guidance_scale": cfg.reference_guidance_scale,
        "pose_guidance_scale": cfg.pose_guidance_scale,
        "color_image": image_obj(palette_image),
        "seed": cfg.seed,
    }
    schema_a = dict(common)
    schema_a["skeleton_keypoints"] = pose_frames
    attempts = [("frame_objects", schema_a)]
    schema_b = dict(common)
    schema_b["skeleton_keypoints"] = [f["keypoints"] for f in pose_frames]
    attempts.append(("nested_arrays", schema_b))

    errors: list[str] = []
    for schema_name, payload in attempts:
        resp = request_json("POST", f"{API_BASE}/animate-with-skeleton", token, payload=payload, timeout=300)
        if resp.status_code == 422:
            errors.append(f"{schema_name}: {resp.text[:3000]}")
            continue
        data = require_ok(resp, "animate-with-skeleton")
        images, usage, job_id = extract_images_from_response(data, token)
        meta = {"schema": schema_name, "job_id": job_id, "response_keys": sorted(data.keys())}
        return images, usage, meta
    raise SpikeError("animate-with-skeleton schema validation failed for both known public shapes:\n" + "\n".join(errors))


def corner_background_rgb(im: Image.Image) -> np.ndarray:
    rgb = np.asarray(im.convert("RGB"), dtype=np.int16)
    h, w, _ = rgb.shape
    k = max(2, min(h, w) // 20)
    patches = [rgb[:k, :k], rgb[:k, -k:], rgb[-k:, :k], rgb[-k:, -k:]]
    samples = np.concatenate([p.reshape(-1, 3) for p in patches], axis=0)
    return np.median(samples, axis=0)


def foreground_mask(im: Image.Image) -> np.ndarray:
    rgba = np.asarray(im.convert("RGBA"), dtype=np.int16)
    alpha = rgba[..., 3]
    if np.mean(alpha < 16) > 0.01:
        return alpha > 16
    bg = corner_background_rgb(im)
    d = np.linalg.norm(rgba[..., :3] - bg[None, None, :], axis=2)
    return d > 18.0


def normalize_reference(master: Path, out: Path, size: int) -> tuple[Image.Image, np.ndarray]:
    im = Image.open(master).convert("RGBA")
    mask = foreground_mask(im)
    ys, xs = np.where(mask)
    if len(xs) < 50:
        raise SpikeError("Could not isolate the character from the master background automatically")
    x0, x1 = int(xs.min()), int(xs.max()) + 1
    y0, y1 = int(ys.min()), int(ys.max()) + 1
    crop = im.crop((x0, y0, x1, y1))
    crop_mask = Image.fromarray((mask[y0:y1, x0:x1] * 255).astype(np.uint8), mode="L")
    crop.putalpha(crop_mask)
    margin = max(4, size // 20)
    scale = min((size - 2 * margin) / crop.width, (size - 2 * margin) / crop.height)
    new_size = (max(1, round(crop.width * scale)), max(1, round(crop.height * scale)))
    crop = crop.resize(new_size, Image.Resampling.NEAREST)
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    ox = (size - new_size[0]) // 2
    oy = (size - new_size[1]) // 2
    canvas.alpha_composite(crop, (ox, oy))
    canvas.save(out)
    return canvas, np.asarray(canvas)[..., 3] > 16


def extract_palette(im: Image.Image, mask: np.ndarray, n: int) -> list[tuple[int, int, int]]:
    rgb = np.asarray(im.convert("RGB"))
    pixels = [tuple(map(int, p)) for p in rgb[mask].reshape(-1, 3)]
    counts = Counter(pixels)
    palette = [c for c, _ in counts.most_common(n)]
    if not palette:
        raise SpikeError("No foreground colors available for palette extraction")
    return palette


def make_palette_image(palette: list[tuple[int, int, int]], size: int, out: Path) -> None:
    im = Image.new("RGB", (size, size), palette[0])
    draw = ImageDraw.Draw(im)
    n = len(palette)
    cols = math.ceil(math.sqrt(n))
    rows = math.ceil(n / cols)
    cw = math.ceil(size / cols)
    ch = math.ceil(size / rows)
    for i, color in enumerate(palette):
        x = (i % cols) * cw
        y = (i // cols) * ch
        draw.rectangle([x, y, min(size - 1, x + cw - 1), min(size - 1, y + ch - 1)], fill=color)
    im.save(out)


def kp_normalization_mode(keypoints: list[dict[str, Any]], size: int) -> str:
    vals = [float(k.get("x", 0)) for k in keypoints] + [float(k.get("y", 0)) for k in keypoints]
    return "normalized" if max(vals) <= 2.0 else "pixels"


def normalize_keypoints(keypoints: list[dict[str, Any]], size: int) -> tuple[dict[str, dict[str, float]], str]:
    mode = kp_normalization_mode(keypoints, size)
    out: dict[str, dict[str, float]] = {}
    for k in keypoints:
        label = str(k.get("label", "")).upper()
        x, y = float(k["x"]), float(k["y"])
        if mode == "pixels":
            x /= size
            y /= size
        out[label] = {"x": x, "y": y, "z": float(k.get("z_index", k.get("zIndex", 0.0)) or 0.0)}
    missing = sorted(REQUIRED_LABELS - set(out))
    if missing:
        raise SpikeError("Estimated skeleton lacks required biped keypoints: " + ", ".join(missing))
    return out, mode


def denormalize_keypoints(points: dict[str, dict[str, float]], size: int, mode: str) -> list[dict[str, Any]]:
    result = []
    for label, p in points.items():
        x, y = p["x"], p["y"]
        if mode == "pixels":
            x, y = x * size, y * size
        result.append({"x": round(x, 6), "y": round(y, 6), "label": label, "z_index": int(round(p.get("z", 0.0)))})
    return result


def clamp_point(p: dict[str, float]) -> None:
    p["x"] = min(0.98, max(0.02, p["x"]))
    p["y"] = min(0.98, max(0.02, p["y"]))


def copy_points(points: dict[str, dict[str, float]]) -> dict[str, dict[str, float]]:
    return {k: dict(v) for k, v in points.items()}


def root_shift(points: dict[str, dict[str, float]], dy: float) -> None:
    for label in points:
        if label not in {"LEFT LEG", "RIGHT LEG"}:
            points[label]["y"] += dy


def build_walk_poses(base: dict[str, dict[str, float]], size: int, mode: str) -> list[dict[str, Any]]:
    body_height = max(base["LEFT LEG"]["y"], base["RIGHT LEG"]["y"]) - base["NOSE"]["y"]
    body_height = max(0.45, min(0.95, body_height))
    stride = 0.075 * body_height
    lift = 0.055 * body_height
    arm = 0.055 * body_height
    knee_bias = 0.020 * body_height
    bob = 0.012 * body_height

    phases = [
        ("left_contact", +1.0, 0.0),
        ("left_pass", 0.0, -bob),
        ("right_contact", -1.0, 0.0),
        ("right_pass", 0.0, -bob),
    ]
    output = []
    for name, sign, dy in phases:
        p = copy_points(base)
        root_shift(p, dy)
        if "contact" in name:
            p["LEFT LEG"]["x"] += sign * stride
            p["RIGHT LEG"]["x"] -= sign * stride
            p["LEFT KNEE"]["x"] += sign * stride * 0.45 + sign * knee_bias
            p["RIGHT KNEE"]["x"] -= sign * stride * 0.45 - sign * knee_bias
            p["LEFT ARM"]["x"] -= sign * arm
            p["RIGHT ARM"]["x"] += sign * arm
            p["LEFT ELBOW"]["x"] -= sign * arm * 0.45
            p["RIGHT ELBOW"]["x"] += sign * arm * 0.45
        else:
            left_pass = name == "left_pass"
            swing_leg = "LEFT" if left_pass else "RIGHT"
            support_leg = "RIGHT" if left_pass else "LEFT"
            s = +1.0 if left_pass else -1.0
            p[f"{swing_leg} LEG"]["x"] += s * stride * 0.22
            p[f"{swing_leg} LEG"]["y"] -= lift
            p[f"{swing_leg} KNEE"]["x"] += s * stride * 0.38
            p[f"{swing_leg} KNEE"]["y"] -= lift * 0.45
            p[f"{support_leg} LEG"]["x"] -= s * stride * 0.10
            p["LEFT ARM"]["x"] -= s * arm * 0.35
            p["RIGHT ARM"]["x"] += s * arm * 0.35
            p["LEFT ELBOW"]["x"] -= s * arm * 0.20
            p["RIGHT ELBOW"]["x"] += s * arm * 0.20
        for q in p.values():
            clamp_point(q)
        output.append({"name": name, "keypoints": denormalize_keypoints(p, size, mode), "normalized": p})
    return output


def draw_skeleton(base_image: Image.Image, points: dict[str, dict[str, float]], out: Path, title: str) -> None:
    im = base_image.convert("RGBA").copy()
    overlay = Image.new("RGBA", im.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    w, h = im.size
    def xy(label: str) -> tuple[int, int]:
        p = points[label]
        return int(round(p["x"] * w)), int(round(p["y"] * h))
    for a, b in CONNECTIONS:
        if a in points and b in points:
            draw.line([xy(a), xy(b)], fill=(255, 64, 64, 220), width=max(1, w // 64))
    for label in REQUIRED_LABELS:
        if label in points:
            x, y = xy(label)
            r = max(1, w // 64)
            draw.ellipse([x-r, y-r, x+r, y+r], fill=(255, 255, 0, 255))
    im = Image.alpha_composite(im, overlay)
    draw2 = ImageDraw.Draw(im)
    draw2.rectangle([0, 0, w, 14], fill=(0, 0, 0, 180))
    draw2.text((3, 2), title, fill=(255, 255, 255, 255))
    im.save(out)


def nearest_palette_indices(im: Image.Image, palette: list[tuple[int, int, int]]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    arr = np.asarray(im.convert("RGBA"))
    mask = foreground_mask(im)
    rgb = arr[..., :3].astype(np.int16)
    pal = np.asarray(palette, dtype=np.int16)
    flat = rgb.reshape(-1, 3)
    idx = np.empty((flat.shape[0],), dtype=np.int16)
    dist = np.empty((flat.shape[0],), dtype=np.float32)
    for start in range(0, len(flat), 16384):
        chunk = flat[start:start+16384]
        d2 = ((chunk[:, None, :] - pal[None, :, :]) ** 2).sum(axis=2)
        i = d2.argmin(axis=1)
        idx[start:start+len(chunk)] = i
        dist[start:start+len(chunk)] = np.sqrt(d2[np.arange(len(chunk)), i])
    return idx.reshape(mask.shape), dist.reshape(mask.shape), mask


def palette_hist(im: Image.Image, palette: list[tuple[int, int, int]], crop: tuple[int, int, int, int] | None = None) -> np.ndarray:
    if crop:
        im = im.crop(crop)
    idx, _, mask = nearest_palette_indices(im, palette)
    vals = idx[mask]
    hist = np.bincount(vals, minlength=len(palette)).astype(np.float64)
    if hist.sum() > 0:
        hist /= hist.sum()
    return hist


def tv_distance(a: np.ndarray, b: np.ndarray) -> float:
    return float(0.5 * np.abs(a - b).sum())


def skeleton_crop(points: dict[str, dict[str, float]], labels: list[str], size: int, margin: float) -> tuple[int, int, int, int]:
    xs = [points[l]["x"] for l in labels if l in points]
    ys = [points[l]["y"] for l in labels if l in points]
    if not xs:
        return (0, 0, size, size)
    x0 = max(0, int((min(xs) - margin) * size))
    y0 = max(0, int((min(ys) - margin) * size))
    x1 = min(size, int(math.ceil((max(xs) + margin) * size)))
    y1 = min(size, int(math.ceil((max(ys) + margin) * size)))
    return (x0, y0, max(x0+1, x1), max(y0+1, y1))


def common_labels(a: dict[str, dict[str, float]], b: dict[str, dict[str, float]]) -> list[str]:
    return sorted((set(a) & set(b)) & REQUIRED_LABELS)


def pose_error(target: dict[str, dict[str, float]], actual: dict[str, dict[str, float]]) -> tuple[float, float]:
    labels = common_labels(target, actual)
    if not labels:
        return 1.0, 1.0
    d = np.array([math.hypot(target[l]["x"] - actual[l]["x"], target[l]["y"] - actual[l]["y"]) for l in labels])
    return float(d.mean()), float(np.percentile(d, 90))


def pose_distance(a: dict[str, dict[str, float]], b: dict[str, dict[str, float]]) -> float:
    labels = common_labels(a, b)
    if not labels:
        return 0.0
    return float(np.mean([math.hypot(a[l]["x"] - b[l]["x"], a[l]["y"] - b[l]["y"]) for l in labels]))


def bbox_metrics(im: Image.Image) -> tuple[float, float, tuple[int, int, int, int]]:
    alpha = foreground_mask(im)
    ys, xs = np.where(alpha)
    if len(xs) == 0:
        return 0.0, 0.0, (0, 0, 1, 1)
    bbox = (int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1)
    area = float(alpha.mean())
    height = (bbox[3] - bbox[1]) / im.height
    return area, height, bbox


def make_contact_sheet(reference: Image.Image, frames: list[Image.Image], out: Path) -> None:
    tiles = [reference] + frames
    labels = ["reference", "left contact", "left pass", "right contact", "right pass"]
    size = reference.width
    sheet = Image.new("RGBA", (size * len(tiles), size + 18), (28, 28, 28, 255))
    draw = ImageDraw.Draw(sheet)
    for i, (tile, label) in enumerate(zip(tiles, labels)):
        sheet.alpha_composite(tile.convert("RGBA"), (i * size, 18))
        draw.text((i * size + 3, 3), label, fill=(255, 255, 255, 255))
    sheet.save(out)


def run(cfg: Config, token: str) -> int:
    cfg.workspace.mkdir(parents=True, exist_ok=True)
    normalized = cfg.workspace / "exilada_reference_128.png"
    palette_png = cfg.workspace / "palette.png"
    palette_json = cfg.workspace / "palette.json"

    ref_im, ref_mask = normalize_reference(cfg.master, normalized, cfg.size)
    palette = extract_palette(ref_im, ref_mask, cfg.palette_colors)
    make_palette_image(palette, cfg.size, palette_png)
    palette_json.write_text(json.dumps(["#%02X%02X%02X" % c for c in palette], indent=2), encoding="utf-8")

    balance = get_balance(token)
    if balance is not None:
        print(f"PixelLab balance: ${balance:.4f}")
        if balance < cfg.max_expected_usd:
            raise SpikeError(f"Balance ${balance:.4f} is below the conservative spike budget ${cfg.max_expected_usd:.2f}")

    print("Estimating canonical Exilada skeleton...")
    ref_raw, usage_ref = estimate_skeleton(token, normalized)
    ref_points, coord_mode = normalize_keypoints(ref_raw, cfg.size)
    (cfg.workspace / "reference_skeleton.json").write_text(json.dumps(ref_raw, indent=2), encoding="utf-8")
    draw_skeleton(ref_im, ref_points, cfg.workspace / "reference_skeleton.png", "estimated reference skeleton")

    poses = build_walk_poses(ref_points, cfg.size, coord_mode)
    pose_frames: list[dict[str, Any]] = []
    for i, pose in enumerate(poses):
        pose_frames.append({"keypoints": pose["keypoints"]})
        (cfg.workspace / f"target_pose_{i}.json").write_text(json.dumps(pose["keypoints"], indent=2), encoding="utf-8")
        draw_skeleton(ref_im, pose["normalized"], cfg.workspace / f"target_pose_{i}.png", pose["name"])

    manifest = {
        "master": str(cfg.master), "normalized_reference": str(normalized),
        "size": cfg.size, "seed": cfg.seed, "palette": ["#%02X%02X%02X" % c for c in palette],
        "view": cfg.view, "direction": cfg.direction,
        "reference_guidance_scale": cfg.reference_guidance_scale,
        "pose_guidance_scale": cfg.pose_guidance_scale,
        "coordinate_mode_from_estimator": coord_mode,
        "policy": "one generation only; no retries/seed fishing/manual fixes; Pixel Engine forbidden until PASS",
    }
    (cfg.workspace / "spike_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print("Submitting ONE PixelLab animate-with-skeleton request (4 walk key poses)...")
    images_data, usage_anim, api_meta = animate_with_skeleton(token, cfg, normalized, palette_png, pose_frames)
    if len(images_data) != 4:
        raise SpikeError(f"Expected exactly 4 output frames, got {len(images_data)}")

    frames: list[Image.Image] = []
    for i, obj in enumerate(images_data):
        path = cfg.workspace / f"frame_{i}.png"
        save_base64_image(obj, path)
        im = Image.open(path).convert("RGBA")
        if im.size != (cfg.size, cfg.size):
            raise SpikeError(f"Frame {i} returned unexpected size {im.size}")
        frames.append(im)
    make_contact_sheet(ref_im, frames, cfg.workspace / "contact_sheet.png")

    print("Re-estimating output skeletons for automatic pose QA...")
    total_usage = usage_ref + usage_anim
    generated_points: list[dict[str, dict[str, float]]] = []
    frame_metrics: list[dict[str, Any]] = []
    ref_area, ref_height, _ = bbox_metrics(ref_im)
    ref_head_crop = skeleton_crop(ref_points, ["LEFT EAR", "RIGHT EAR", "LEFT EYE", "RIGHT EYE", "NOSE", "NECK"], cfg.size, 0.055)
    ref_torso_crop = skeleton_crop(ref_points, ["LEFT SHOULDER", "RIGHT SHOULDER", "LEFT HIP", "RIGHT HIP"], cfg.size, 0.045)
    ref_head_hist = palette_hist(ref_im, palette, ref_head_crop)
    ref_torso_hist = palette_hist(ref_im, palette, ref_torso_crop)

    for i, im in enumerate(frames):
        raw, u = estimate_skeleton(token, cfg.workspace / f"frame_{i}.png")
        total_usage += u
        actual, _ = normalize_keypoints(raw, cfg.size)
        generated_points.append(actual)
        target = poses[i]["normalized"]
        mean_err, p90_err = pose_error(target, actual)
        _, dist, mask = nearest_palette_indices(im, palette)
        near_ratio = float((dist[mask] <= 18.0).mean()) if mask.any() else 0.0
        unique_colors = len(set(map(tuple, np.asarray(im.convert("RGB"))[mask].reshape(-1, 3).tolist()))) if mask.any() else 0
        area, height, _ = bbox_metrics(im)
        head_crop = skeleton_crop(actual, ["LEFT EAR", "RIGHT EAR", "LEFT EYE", "RIGHT EYE", "NOSE", "NECK"], cfg.size, 0.055)
        torso_crop = skeleton_crop(actual, ["LEFT SHOULDER", "RIGHT SHOULDER", "LEFT HIP", "RIGHT HIP"], cfg.size, 0.045)
        head_tv = tv_distance(ref_head_hist, palette_hist(im, palette, head_crop))
        torso_tv = tv_distance(ref_torso_hist, palette_hist(im, palette, torso_crop))
        metrics = {
            "frame": i,
            "pose_mean_error": round(mean_err, 4),
            "pose_p90_error": round(p90_err, 4),
            "palette_near_ratio": round(near_ratio, 4),
            "unique_colors": unique_colors,
            "foreground_area_ratio": round(area / max(ref_area, 1e-6), 4),
            "bbox_height_ratio": round(height / max(ref_height, 1e-6), 4),
            "head_palette_tv": round(head_tv, 4),
            "torso_palette_tv": round(torso_tv, 4),
        }
        frame_metrics.append(metrics)
        draw_skeleton(im, actual, cfg.workspace / f"frame_{i}_estimated_skeleton.png", f"output {i} skeleton")
        (cfg.workspace / f"frame_{i}_estimated_skeleton.json").write_text(json.dumps(raw, indent=2), encoding="utf-8")

    target_amp = pose_distance(poses[0]["normalized"], poses[2]["normalized"])
    actual_amp = pose_distance(generated_points[0], generated_points[2])
    motion_ratio = actual_amp / max(target_amp, 1e-6)

    failures: list[str] = []
    for m in frame_metrics:
        i = m["frame"]
        if m["pose_mean_error"] > 0.10: failures.append(f"frame {i}: pose_mean_error > 0.10")
        if m["pose_p90_error"] > 0.18: failures.append(f"frame {i}: pose_p90_error > 0.18")
        if m["palette_near_ratio"] < 0.80: failures.append(f"frame {i}: palette_near_ratio < 0.80")
        if m["unique_colors"] > max(96, len(palette) * 4): failures.append(f"frame {i}: too many colors for fixed-palette pixel art")
        if not (0.65 <= m["foreground_area_ratio"] <= 1.35): failures.append(f"frame {i}: foreground area drift")
        if not (0.75 <= m["bbox_height_ratio"] <= 1.25): failures.append(f"frame {i}: character height drift")
        if m["head_palette_tv"] > 0.60: failures.append(f"frame {i}: head palette/identity drift")
        if m["torso_palette_tv"] > 0.50: failures.append(f"frame {i}: torso palette/clothing drift")
    if not (0.50 <= motion_ratio <= 1.80):
        failures.append(f"motion amplitude ratio {motion_ratio:.3f} outside 0.50..1.80")

    verdict = "PASS" if not failures else "FAIL"
    report = {
        "verdict": verdict,
        "pixel_engine_allowed": verdict == "PASS",
        "total_reported_usage_usd": round(total_usage, 5),
        "motion_amplitude_ratio": round(motion_ratio, 4),
        "frames": frame_metrics,
        "failures": failures,
        "api": api_meta,
        "limitations": [
            "Automatic QA is a deterministic pre-gate, not a semantic proof of perfect character identity.",
            "Final production acceptance still requires visual inspection of contact_sheet.png; no frame may be manually repaired.",
        ],
    }
    (cfg.workspace / "qa_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    md = [
        f"# PixelLab skeleton spike QA — {verdict}", "",
        f"- Pixel Engine allowed: **{'YES' if verdict == 'PASS' else 'NO'}**",
        f"- Reported API usage: **${total_usage:.5f}**",
        f"- Motion amplitude ratio: **{motion_ratio:.3f}** (gate 0.50–1.80)", "",
        "| frame | pose mean | pose p90 | palette near | colors | area ratio | height ratio | head TV | torso TV |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for m in frame_metrics:
        md.append(f"| {m['frame']} | {m['pose_mean_error']:.4f} | {m['pose_p90_error']:.4f} | {m['palette_near_ratio']:.4f} | {m['unique_colors']} | {m['foreground_area_ratio']:.4f} | {m['bbox_height_ratio']:.4f} | {m['head_palette_tv']:.4f} | {m['torso_palette_tv']:.4f} |")
    if failures:
        md += ["", "## Failures"] + [f"- {x}" for x in failures]
    md += ["", "No retries, seed fishing, inpainting, manual skeleton edits or frame repainting were used."]
    (cfg.workspace / "qa_report.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    print(f"\nQA VERDICT: {verdict}")
    print(f"Contact sheet: {cfg.workspace / 'contact_sheet.png'}")
    print(f"QA report:     {cfg.workspace / 'qa_report.md'}")
    print(f"Reported cost: ${total_usage:.5f}")
    if failures:
        print("Pixel Engine remains FORBIDDEN for this pipeline.")
        for x in failures:
            print(f"  - {x}")
        return 2
    print("Automatic pre-gate passed. Pixel Engine may be considered ONLY after visual acceptance of the four key poses.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Minimal PixelLab skeleton spike for the canonical Exilada")
    ap.add_argument("--master", required=True, type=Path)
    ap.add_argument("--workspace", type=Path, default=Path(r"D:\AI\PixelLabSkeletonSpike"))
    ap.add_argument("--size", type=int, default=128, choices=[16, 32, 64, 128, 256])
    ap.add_argument("--seed", type=int, default=20260904)
    ap.add_argument("--palette-colors", type=int, default=24)
    ap.add_argument("--view", default="side", choices=["side", "low top-down", "high top-down"])
    ap.add_argument("--direction", default="south-east", choices=["south", "south-east", "east", "north-east", "north", "north-west", "west", "south-west"])
    args = ap.parse_args()
    token = os.environ.get("PIXELLAB_SECRET", "").strip()
    if not token:
        raise SpikeError("PIXELLAB_SECRET is not set")
    if not args.master.exists():
        raise SpikeError(f"Canonical master not found: {args.master}")
    cfg = Config(master=args.master, workspace=args.workspace, size=args.size, seed=args.seed, palette_colors=args.palette_colors, view=args.view, direction=args.direction)
    return run(cfg, token)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SpikeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
