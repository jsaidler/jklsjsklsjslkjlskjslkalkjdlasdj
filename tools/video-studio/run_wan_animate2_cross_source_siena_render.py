#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
BASE_PATH = HERE / "run_wan_animate2_primary_baseline_render.py"
SPEC = importlib.util.spec_from_file_location("wan_primary_baseline", BASE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Could not import baseline runner: {BASE_PATH}")
base = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(base)

WIDTH = 512
HEIGHT = 912
FRAMES = 65
FPS = 24.0


def run(cmd: list[str], stage: str) -> None:
    print(f"stage={stage}", flush=True)
    p = subprocess.run(cmd, text=True, capture_output=True)
    if p.returncode != 0:
        raise base.GateError(f"{stage} failed: {(p.stderr or p.stdout).strip()}")


def prepare_assets(run_dir: Path) -> tuple[Path, Path, dict[str, Any]]:
    library = base.load_json(base.UNIFIED_ROOT / "joao_motion_library_v1.json")
    plan = base.load_json(base.UNIFIED_ROOT / "first_driver_v3" / "driver_plan.json")

    primary_id = plan["windows"][0]["base"]["unit"]
    siena_id = plan["windows"][1]["base"]["unit"]
    primary = base.find_unit(library, primary_id)
    siena = base.find_unit(library, siena_id)

    primary_src = Path(primary["source_video"])
    siena_src = Path(siena["source_video"])
    if not primary_src.is_file():
        raise base.GateError(f"PRIMARY source missing: {primary_src}")
    if not siena_src.is_file():
        raise base.GateError(f"SIENA source missing: {siena_src}")

    p0, p1 = float(primary["source_start_s"]), float(primary["source_end_s"])
    s0, s1 = float(siena["source_start_s"]), float(siena["source_end_s"])
    src_d = s1 - s0
    if src_d <= 0:
        raise base.GateError("Invalid SIENA unit duration")

    out_d = FRAMES / FPS
    retime = out_d / src_d
    ffmpeg = shutil.which("ffmpeg") or shutil.which("ffmpeg.exe")
    if not ffmpeg:
        raise base.GateError("ffmpeg not found in PATH")

    driver = run_dir / "pose_video_siena_cross_source65.mp4"
    reference = run_dir / "reference_image_primary_identity.png"

    vf = (
        f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=increase:flags=lanczos,"
        f"crop={WIDTH}:{HEIGHT},setsar=1,setpts={retime:.12f}*(PTS-STARTPTS),fps={FPS:.12f}"
    )
    run([
        ffmpeg, "-y", "-hide_banner", "-loglevel", "error",
        "-ss", f"{s0:.6f}", "-t", f"{src_d:.6f}", "-i", str(siena_src),
        "-vf", vf, "-an", "-frames:v", str(FRAMES),
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", str(driver),
    ], "prepare_siena_driver")

    ref_t = p0 + (p1 - p0) * 0.5
    run([
        ffmpeg, "-y", "-hide_banner", "-loglevel", "error",
        "-ss", f"{ref_t:.6f}", "-i", str(primary_src), "-frames:v", "1",
        "-vf", f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=increase:flags=lanczos,crop={WIDTH}:{HEIGHT},setsar=1",
        str(reference),
    ], "prepare_primary_reference")

    meta = {
        "primary_reference_unit": primary_id,
        "primary_reference_source": str(primary_src),
        "primary_reference_time_s": ref_t,
        "siena_driver_unit": siena_id,
        "siena_driver_source": str(siena_src),
        "siena_driver_start_s": s0,
        "siena_driver_end_s": s1,
        "retime": retime,
    }
    print(
        f"cross-source reference={primary_id} driver={siena_id} "
        f"siena={s0:.3f}-{s1:.3f}s retime={retime:.6f}x",
        flush=True,
    )
    return driver, reference, meta


def copy_inputs(comfy_root: Path, driver: Path, reference: Path) -> tuple[str, str]:
    sub = Path("video_studio") / "wan_animate2_cross_source_siena"
    target = comfy_root / "input" / sub
    target.mkdir(parents=True, exist_ok=True)
    dname = driver.name
    rname = reference.name
    shutil.copy2(driver, target / dname)
    shutil.copy2(reference, target / rname)
    return (str(sub / dname).replace("\\", "/"), str(sub / rname).replace("\\", "/"))


def choose_generated_video(copied: list[Path], driver_name: str, run_dir: Path) -> Path:
    videos = [p for p in copied if p.suffix.lower() in base.VIDEO_EXTS and p.name != driver_name]
    if not videos:
        raise base.GateError(
            "Inference completed but no generated video distinct from the driving input was found. "
            f"Copied={[p.name for p in copied]}"
        )
    preferred = [p for p in videos if "wan" in p.name.lower() or "animate" in p.name.lower()]
    source = preferred[0] if preferred else max(videos, key=lambda p: p.stat().st_size)
    final = run_dir / "wan_animate2_cross_source_siena65_GENERATED.mp4"
    shutil.copy2(source, final)
    return final


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8192)
    ap.add_argument("--timeout-minutes", type=int, default=180)
    args = ap.parse_args()

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = base.RUN_ROOT / f"cross-source-siena-{stamp}"
    run_dir.mkdir(parents=True, exist_ok=False)
    log_path = run_dir / "comfy_server.log"
    proc = None
    log_handle = None

    try:
        print("WAN-ANIMATE-2 CROSS-SOURCE SIENA RENDER GATE")
        print("===========================================")
        print("Purpose: prove motion transfer from a different RGB source while preserving PRIMARY reference identity.", flush=True)

        driver, reference, meta = prepare_assets(run_dir)
        template_path, nodes, wan_id = base.choose_template()
        wan_inputs = nodes[wan_id].get("inputs") or {}
        if "pose_video" not in wan_inputs or "reference_image" not in wan_inputs:
            raise base.GateError("Selected Animate2 template does not link both pose_video and reference_image")

        portable = base.find_portable()
        comfy_root = portable / "ComfyUI"
        video_rel, image_rel = copy_inputs(comfy_root, driver, reference)

        pose_branch = base.ancestors(nodes, wan_inputs["pose_video"])
        ref_branch = base.ancestors(nodes, wan_inputs["reference_image"])
        pose_patches = base.patch_media_branch(nodes, pose_branch, video_rel, "video")
        ref_patches = base.patch_media_branch(nodes, ref_branch, image_rel, "image")
        if not pose_patches:
            raise base.GateError(f"Could not locate video loader upstream of Wan node. Branch={sorted(pose_branch)}")
        if not ref_patches:
            raise base.GateError(f"Could not locate image loader upstream of Wan node. Branch={sorted(ref_branch)}")

        base.patch_wan_node(nodes, wan_id)
        base.patch_length_consumers(nodes)
        patched_path = run_dir / "patched_api_prompt.json"
        patched_path.write_text(json.dumps(nodes, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"stage=prompt_patch video={pose_patches} reference={ref_patches}", flush=True)

        extra_paths = base.write_extra_paths()
        proc, log_handle = base.start_comfy(portable, args.port, extra_paths, log_path)
        base_url = f"http://127.0.0.1:{args.port}"
        base.validate_graph_runtime(base_url, nodes)

        prompt_id = base.submit(base_url, nodes)
        item = base.wait_prompt(base_url, prompt_id, args.timeout_minutes)
        copied = base.copy_history_outputs(comfy_root, item, run_dir)
        final_video = choose_generated_video(copied, driver.name, run_dir)

        manifest = {
            "schema": "wan-animate2-cross-source-siena-render/v1",
            "purpose": "cross-source motion transfer gate after PRIMARY baseline PASS",
            "template": str(template_path),
            "prompt_id": prompt_id,
            "driver": str(driver),
            "reference": str(reference),
            "width": WIDTH,
            "height": HEIGHT,
            "frames": FRAMES,
            "fps": FPS,
            "source_meta": meta,
            "copied_outputs": [str(p) for p in copied],
            "final_video": str(final_video),
            "server_log": str(log_path),
        }
        (run_dir / "run_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

        print("stage=complete", flush=True)
        print(f"Run dir: {run_dir}")
        print(f"Generated video: {final_video}")
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
    except base.GateError as exc:
        print(f"WAN CROSS-SOURCE SIENA GATE ERROR: {exc}", flush=True)
        raise SystemExit(2)
