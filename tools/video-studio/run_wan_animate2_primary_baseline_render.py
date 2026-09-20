#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any

WAN_ROOT = Path(r"Z:\AI\WanAnimate2")
UNIFIED_ROOT = Path(r"Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\unified")
RUN_ROOT = Path(r"Z:\AI\VideoStudioRuns\wan-animate2-behavior")
PORTABLE_CANDIDATES = [
    Path(r"Z:\AI\Flux2Klein\ComfyUI_windows_portable"),
    Path(r"Z:\AI\MiniMaxH3\ComfyUI_windows_portable"),
    Path(r"Z:\AI\QwenImageEdit\ComfyUI_windows_portable"),
]
DIFFUSION = "wan_animate_2_bf16.safetensors"
WIDTH = 512
HEIGHT = 912
FRAMES = 65
FPS = 24.0
VIDEO_EXTS = {".mp4", ".mov", ".mkv", ".webm", ".avi"}
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}


class GateError(RuntimeError):
    pass


def load_json(path: Path) -> Any:
    if not path.is_file():
        raise GateError(f"Missing JSON: {path}")
    return json.loads(path.read_text(encoding="utf-8-sig"))


def request_json(url: str, payload: Any | None = None, timeout: float = 120.0) -> Any:
    data = None
    headers = {"Accept": "application/json"}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")
        raise GateError(f"HTTP {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise GateError(f"Could not reach {url}: {exc}") from exc
    return json.loads(raw.decode("utf-8")) if raw else {}


def ping(base_url: str, timeout: float = 2.0) -> bool:
    try:
        request_json(base_url + "/system_stats", timeout=timeout)
        return True
    except Exception:
        return False


def find_portable() -> Path:
    for p in PORTABLE_CANDIDATES:
        if (p / "python_embeded" / "python.exe").is_file() and (p / "ComfyUI" / "main.py").is_file():
            return p
    raise GateError("No usable ComfyUI portable runtime found in protected AI roots.")


def write_extra_paths() -> Path:
    out = WAN_ROOT / "wan_animate2_behavior_extra_model_paths.yaml"
    out.write_text(
        "wan_animate2_behavior:\n"
        "    base_path: \"Z:/AI/WanAnimate2\"\n"
        "    diffusion_models: models/diffusion_models/\n"
        "    text_encoders: models/text_encoders/\n"
        "    vae: models/vae/\n"
        "    clip_vision: models/clip_vision/\n",
        encoding="utf-8",
    )
    return out


def start_comfy(portable: Path, port: int, extra_paths: Path, log_path: Path) -> tuple[subprocess.Popen | None, Any]:
    base_url = f"http://127.0.0.1:{port}"
    if ping(base_url):
        print(f"stage=comfy_reuse url={base_url}", flush=True)
        return None, None

    print(f"stage=comfy_start portable={portable}", flush=True)
    python = portable / "python_embeded" / "python.exe"
    main_py = portable / "ComfyUI" / "main.py"
    log_handle = log_path.open("w", encoding="utf-8", errors="replace")
    cmd = [
        str(python), "-s", str(main_py), "--windows-standalone-build",
        "--listen", "127.0.0.1", "--port", str(port),
        "--extra-model-paths-config", str(extra_paths), "--lowvram",
    ]
    creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0) if os.name == "nt" else 0
    proc = subprocess.Popen(cmd, cwd=str(portable), stdout=log_handle, stderr=subprocess.STDOUT, creationflags=creationflags)
    deadline = time.time() + 300
    while time.time() < deadline:
        if proc.poll() is not None:
            log_handle.flush()
            raise GateError(f"ComfyUI exited during startup. See {log_path}")
        if ping(base_url, 3):
            print(f"stage=comfy_ready url={base_url}", flush=True)
            return proc, log_handle
        time.sleep(2)
    raise GateError(f"ComfyUI did not answer within 300 s. See {log_path}")


def api_nodes(obj: Any) -> dict[str, Any]:
    if not isinstance(obj, dict):
        return {}
    if obj and all(isinstance(v, dict) and "class_type" in v for v in obj.values()):
        return {str(k): v for k, v in obj.items()}
    for key in ("prompt", "workflow", "nodes"):
        v = obj.get(key)
        if isinstance(v, dict) and v:
            return {str(k): n for k, n in v.items() if isinstance(n, dict) and "class_type" in n}
    return {}


def graph_has_model(nodes: dict[str, Any], model_name: str) -> bool:
    return model_name.lower() in json.dumps(nodes, ensure_ascii=False).lower()


def choose_template() -> tuple[Path, dict[str, Any], str]:
    candidates = []
    for p in WAN_ROOT.glob("w*_api_prompt.json"):
        try:
            obj = load_json(p)
        except Exception:
            continue
        nodes = api_nodes(obj)
        wan_ids = [nid for nid, node in nodes.items() if node.get("class_type") == "WanAnimate2ToVideo"]
        if not wan_ids:
            continue
        score = 0
        if graph_has_model(nodes, DIFFUSION):
            score += 100
        score += int(p.stat().st_mtime)
        candidates.append((score, p, nodes, wan_ids[0]))
    if not candidates:
        raise GateError(r"No w*_api_prompt.json with WanAnimate2ToVideo found under Z:\AI\WanAnimate2")
    candidates.sort(key=lambda x: x[0], reverse=True)
    score, path, nodes, wan_id = candidates[0]
    if not graph_has_model(nodes, DIFFUSION):
        raise GateError(f"Best Animate2 prompt does not reference required {DIFFUSION}: {path}")
    print(f"stage=template prompt={path.name} wan_node={wan_id}", flush=True)
    return path, nodes, wan_id


def link_node(value: Any) -> str | None:
    if isinstance(value, list) and len(value) >= 1 and isinstance(value[0], (str, int)):
        return str(value[0])
    return None


def ancestors(nodes: dict[str, Any], root_value: Any) -> set[str]:
    first = link_node(root_value)
    if first is None:
        return set()
    seen: set[str] = set()
    stack = [first]
    while stack:
        nid = stack.pop()
        if nid in seen or nid not in nodes:
            continue
        seen.add(nid)
        for v in (nodes[nid].get("inputs") or {}).values():
            up = link_node(v)
            if up is not None and up not in seen:
                stack.append(up)
    return seen


def patch_media_branch(nodes: dict[str, Any], ids: set[str], replacement: str, kind: str) -> list[tuple[str, str, str]]:
    exts = VIDEO_EXTS if kind == "video" else IMAGE_EXTS
    key_hints = ("video", "path", "file", "filename") if kind == "video" else ("image", "path", "file", "filename")
    patched = []
    for nid in ids:
        inputs = nodes[nid].get("inputs") or {}
        for key, value in list(inputs.items()):
            if not isinstance(value, str):
                continue
            suffix = Path(value).suffix.lower()
            hinted = any(h in key.lower() for h in key_hints)
            if suffix in exts or (hinted and suffix in exts):
                inputs[key] = replacement
                patched.append((nid, key, value))
    return patched


def patch_wan_node(nodes: dict[str, Any], wan_id: str) -> None:
    inputs = nodes[wan_id].setdefault("inputs", {})
    inputs["width"] = WIDTH
    inputs["height"] = HEIGHT
    inputs["length"] = FRAMES
    inputs["batch_size"] = 1
    inputs["video_frame_offset"] = 0
    if "pose_strength" in inputs:
        inputs["pose_strength"] = 1.0
    if "pose_start_percent" in inputs:
        inputs["pose_start_percent"] = 0.0
    if "pose_end_percent" in inputs:
        inputs["pose_end_percent"] = 1.0
    if "reference_image_strength" in inputs:
        inputs["reference_image_strength"] = 1.0


def patch_length_consumers(nodes: dict[str, Any]) -> None:
    for node in nodes.values():
        ct = str(node.get("class_type") or "")
        inputs = node.get("inputs") or {}
        if ct in {"ImageFromBatch", "VHS_VideoCombine", "CreateVideo"}:
            if "length" in inputs and isinstance(inputs["length"], (int, float)):
                inputs["length"] = FRAMES
            if "frame_rate" in inputs and isinstance(inputs["frame_rate"], (int, float)):
                inputs["frame_rate"] = FPS
            if "fps" in inputs and isinstance(inputs["fps"], (int, float)):
                inputs["fps"] = FPS


def validate_graph_runtime(base_url: str, nodes: dict[str, Any]) -> None:
    print("stage=runtime_validate", flush=True)
    info = request_json(base_url + "/object_info", timeout=180)
    missing = sorted({str(n.get("class_type")) for n in nodes.values() if str(n.get("class_type")) not in info})
    if missing:
        raise GateError("Selected prior Animate2 prompt requires missing runtime nodes: " + ", ".join(missing))
    unet_info = info.get("UNETLoader") or {}
    combo = (((unet_info.get("input") or {}).get("required") or {}).get("unet_name") or [[], {}])[0]
    if isinstance(combo, list) and combo and DIFFUSION not in combo:
        raise GateError(f"Runtime cannot see required model {DIFFUSION}")


def find_unit(library: dict[str, Any], unit_id: str) -> dict[str, Any]:
    for u in library.get("units") or []:
        if u.get("library_unit_id") == unit_id:
            return u
    raise GateError(f"Library unit not found: {unit_id}")


def run(cmd: list[str], stage: str) -> None:
    print(f"stage={stage}", flush=True)
    p = subprocess.run(cmd, text=True, capture_output=True)
    if p.returncode != 0:
        raise GateError(f"{stage} failed: {(p.stderr or p.stdout).strip()}")


def prepare_primary_baseline(run_dir: Path) -> tuple[Path, Path]:
    lib = load_json(UNIFIED_ROOT / "joao_motion_library_v1.json")
    plan = load_json(UNIFIED_ROOT / "first_driver_v3" / "driver_plan.json")
    unit_id = plan["windows"][0]["base"]["unit"]
    unit = find_unit(lib, unit_id)
    src = Path(unit["source_video"])
    if not src.is_file():
        raise GateError(f"PRIMARY source missing: {src}")
    s0 = float(unit["source_start_s"])
    s1 = float(unit["source_end_s"])
    src_d = s1 - s0
    out_d = FRAMES / FPS
    if src_d <= 0:
        raise GateError("Invalid PRIMARY unit duration")
    retime = out_d / src_d
    ffmpeg = shutil.which("ffmpeg") or shutil.which("ffmpeg.exe")
    if not ffmpeg:
        raise GateError("ffmpeg not found in PATH")

    driver = run_dir / "pose_video_primary_baseline65.mp4"
    reference = run_dir / "reference_image_primary_baseline.png"
    vf = (
        f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=increase:flags=lanczos,"
        f"crop={WIDTH}:{HEIGHT},setsar=1,setpts={retime:.12f}*(PTS-STARTPTS),fps={FPS:.12f}"
    )
    run([
        ffmpeg, "-y", "-hide_banner", "-loglevel", "error",
        "-ss", f"{s0:.6f}", "-t", f"{src_d:.6f}", "-i", str(src),
        "-vf", vf, "-an", "-frames:v", str(FRAMES),
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", str(driver),
    ], "prepare_primary_driver")
    ref_t = s0 + src_d * 0.5
    run([
        ffmpeg, "-y", "-hide_banner", "-loglevel", "error", "-ss", f"{ref_t:.6f}", "-i", str(src),
        "-frames:v", "1", "-vf", f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=increase:flags=lanczos,crop={WIDTH}:{HEIGHT},setsar=1", str(reference),
    ], "prepare_reference")
    print(f"baseline unit={unit_id} source={s0:.3f}-{s1:.3f}s retime={retime:.6f}x", flush=True)
    return driver, reference


def copy_inputs(comfy_root: Path, driver: Path, reference: Path) -> tuple[str, str]:
    sub = Path("video_studio") / "wan_animate2_primary_baseline"
    target = comfy_root / "input" / sub
    target.mkdir(parents=True, exist_ok=True)
    dname = "pose_video_primary_baseline65.mp4"
    rname = "reference_image_primary_baseline.png"
    shutil.copy2(driver, target / dname)
    shutil.copy2(reference, target / rname)
    return (str(sub / dname).replace("\\", "/"), str(sub / rname).replace("\\", "/"))


def submit(base_url: str, graph: dict[str, Any]) -> str:
    result = request_json(base_url + "/prompt", {"prompt": graph}, timeout=180)
    pid = result.get("prompt_id") if isinstance(result, dict) else None
    if not pid:
        raise GateError(f"ComfyUI did not return prompt_id: {result}")
    return str(pid)


def wait_prompt(base_url: str, prompt_id: str, timeout_minutes: int) -> dict[str, Any]:
    print(f"stage=inference prompt_id={prompt_id}", flush=True)
    start = time.time()
    deadline = start + timeout_minutes * 60
    next_report = start
    while time.time() < deadline:
        hist = request_json(base_url + f"/history/{prompt_id}", timeout=120)
        item = hist.get(prompt_id) if isinstance(hist, dict) else None
        if item:
            status = item.get("status") or {}
            for message in status.get("messages") or []:
                if isinstance(message, (list, tuple)) and message and message[0] == "execution_error":
                    raise GateError(f"ComfyUI execution_error: {message}")
            if status.get("completed") is True:
                return item
        now = time.time()
        if now >= next_report:
            print(f"  inference active elapsed={int(now-start)}s", flush=True)
            next_report = now + 20
        time.sleep(3)
    raise GateError(f"Timeout after {timeout_minutes} min waiting for {prompt_id}")


def copy_history_outputs(comfy_root: Path, item: dict[str, Any], run_dir: Path) -> list[Path]:
    out_dir = run_dir / "outputs"
    out_dir.mkdir(parents=True, exist_ok=True)
    copied = []
    outputs = item.get("outputs") or {}
    for node_out in outputs.values():
        if not isinstance(node_out, dict):
            continue
        for key in ("images", "gifs", "videos"):
            entries = node_out.get(key) or []
            for e in entries:
                if not isinstance(e, dict) or not e.get("filename"):
                    continue
                typ = e.get("type") or "output"
                base = comfy_root / ("output" if typ == "output" else "temp" if typ == "temp" else "input")
                src = base / str(e.get("subfolder") or "") / str(e["filename"])
                if src.is_file():
                    dst = out_dir / src.name
                    shutil.copy2(src, dst)
                    copied.append(dst)
    return copied


def assemble_if_frames(copied: list[Path], run_dir: Path) -> Path | None:
    videos = [p for p in copied if p.suffix.lower() in VIDEO_EXTS]
    if videos:
        dst = run_dir / "wan_animate2_primary_baseline65.mp4"
        shutil.copy2(videos[0], dst)
        return dst
    images = sorted([p for p in copied if p.suffix.lower() in IMAGE_EXTS], key=lambda p: p.name.lower())
    if len(images) < FRAMES:
        return None
    frames_dir = run_dir / "frames"
    frames_dir.mkdir(exist_ok=True)
    for i, p in enumerate(images[:FRAMES], 1):
        shutil.copy2(p, frames_dir / f"frame_{i:04d}.png")
    ffmpeg = shutil.which("ffmpeg") or shutil.which("ffmpeg.exe")
    if not ffmpeg:
        return None
    dst = run_dir / "wan_animate2_primary_baseline65.mp4"
    run([
        ffmpeg, "-y", "-hide_banner", "-loglevel", "error", "-framerate", str(FPS),
        "-i", str(frames_dir / "frame_%04d.png"), "-frames:v", str(FRAMES),
        "-c:v", "libx264", "-preset", "slow", "-crf", "14", "-pix_fmt", "yuv420p", str(dst),
    ], "assemble_output_video")
    return dst


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8192)
    ap.add_argument("--timeout-minutes", type=int, default=180)
    args = ap.parse_args()

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = RUN_ROOT / f"primary-baseline-{stamp}"
    run_dir.mkdir(parents=True, exist_ok=False)
    log_path = run_dir / "comfy_server.log"
    proc = None
    log_handle = None

    try:
        print("WAN-ANIMATE-2 PRIMARY BASELINE RENDER GATE")
        print("========================================")
        print("Purpose: isolate the local Animate2 renderer from multi-source RGB stitching.", flush=True)
        print("stage=prepare_baseline", flush=True)
        driver, reference = prepare_primary_baseline(run_dir)

        template_path, nodes, wan_id = choose_template()
        wan_inputs = nodes[wan_id].get("inputs") or {}
        if "pose_video" not in wan_inputs or "reference_image" not in wan_inputs:
            raise GateError("Selected Animate2 template does not link both pose_video and reference_image")

        portable = find_portable()
        comfy_root = portable / "ComfyUI"
        video_rel, image_rel = copy_inputs(comfy_root, driver, reference)

        pose_branch = ancestors(nodes, wan_inputs["pose_video"])
        ref_branch = ancestors(nodes, wan_inputs["reference_image"])
        pose_patches = patch_media_branch(nodes, pose_branch, video_rel, "video")
        ref_patches = patch_media_branch(nodes, ref_branch, image_rel, "image")
        if not pose_patches:
            raise GateError(f"Could not locate a patchable video loader upstream of Wan node. Branch nodes={sorted(pose_branch)}")
        if not ref_patches:
            raise GateError(f"Could not locate a patchable image loader upstream of Wan node. Branch nodes={sorted(ref_branch)}")
        patch_wan_node(nodes, wan_id)
        patch_length_consumers(nodes)

        patched_path = run_dir / "patched_api_prompt.json"
        patched_path.write_text(json.dumps(nodes, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"stage=prompt_patch video={pose_patches} reference={ref_patches}", flush=True)

        extra_paths = write_extra_paths()
        proc, log_handle = start_comfy(portable, args.port, extra_paths, log_path)
        base_url = f"http://127.0.0.1:{args.port}"
        validate_graph_runtime(base_url, nodes)

        prompt_id = submit(base_url, nodes)
        item = wait_prompt(base_url, prompt_id, args.timeout_minutes)
        copied = copy_history_outputs(comfy_root, item, run_dir)
        final_video = assemble_if_frames(copied, run_dir)

        manifest = {
            "schema": "wan-animate2-primary-baseline-render/v1",
            "purpose": "renderer isolation gate before multi-source RGB driving",
            "template": str(template_path),
            "prompt_id": prompt_id,
            "driver": str(driver),
            "reference": str(reference),
            "width": WIDTH, "height": HEIGHT, "frames": FRAMES, "fps": FPS,
            "copied_outputs": [str(p) for p in copied],
            "final_video": str(final_video) if final_video else None,
            "server_log": str(log_path),
        }
        (run_dir / "run_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

        print("stage=complete", flush=True)
        print(f"Run dir: {run_dir}")
        print(f"Final video: {final_video if final_video else 'NOT ASSEMBLED - inspect copied outputs'}")
        print(f"Manifest: {run_dir / 'run_manifest.json'}")
        print(f"Server log: {log_path}")
        return 0
    finally:
        if proc is not None and proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=15)
            except subprocess.TimeoutExpired:
                proc.kill()
        if log_handle is not None:
            log_handle.close()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except GateError as exc:
        print(f"WAN BASELINE GATE ERROR: {exc}", flush=True)
        raise SystemExit(2)
