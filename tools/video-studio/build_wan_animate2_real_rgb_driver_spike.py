#!/usr/bin/env python3
"""Build a real-RGB 65-frame Wan-Animate-2 driving spike from validated v3 base units.

This deliberately does NOT warp a still image. It uses the actual RGB spans of the
base units already selected by driver_plan.json, retimes them to the validated v3
segment durations, and crossfades them across the validated overlap.

The installed WanAnimate2ToVideo has a single raw RGB pose_video input and no
separate face_video input. Therefore this first end-to-end renderer gate validates
real body/head/gesture driving. The v3 secondary facial donor remains canonical
pose-domain evidence but is not represented as a separate Wan input in this gate.

No DWPose and no Wan inference are invoked.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path


def load_json(path: Path):
    if not path.is_file():
        raise SystemExit(f"Missing input: {path}")
    return json.loads(path.read_text(encoding="utf-8-sig"))


def find_unit(library, library_unit_id: str):
    for u in library.get("units") or []:
        if u.get("library_unit_id") == library_unit_id:
            return u
    raise SystemExit(f"Unit not found in library: {library_unit_id}")


def require_exe(name_or_path: str) -> str:
    found = shutil.which(name_or_path)
    if found:
        return found
    p = Path(name_or_path)
    if p.is_file():
        return str(p)
    raise SystemExit(f"Executable not found: {name_or_path}")


def run_checked(cmd, stage: str):
    print(f"stage={stage}", flush=True)
    p = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode != 0:
        if p.stdout:
            print(p.stdout, file=sys.stderr)
        if p.stderr:
            print(p.stderr, file=sys.stderr)
        raise SystemExit(f"{stage} failed with exit code {p.returncode}")
    return p.stdout


def run_ffmpeg_progress(cmd, stage: str, total_frames: int | None = None):
    print(f"stage={stage}", flush=True)
    full = cmd[:-1] + ["-progress", "pipe:1", "-nostats", cmd[-1]] if False else cmd
    # Caller already includes -progress pipe:1 before output so stdout is machine-readable.
    proc = subprocess.Popen(full, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)
    last_frame = -1
    assert proc.stdout is not None
    for raw in proc.stdout:
        line = raw.strip()
        if line.startswith("frame="):
            try:
                f = int(line.split("=", 1)[1])
            except ValueError:
                continue
            if f != last_frame:
                last_frame = f
                if total_frames:
                    print(f"  frame {f}/{total_frames}", flush=True)
                else:
                    print(f"  frame {f}", flush=True)
    stderr = proc.stderr.read() if proc.stderr is not None else ""
    code = proc.wait()
    if code != 0:
        if stderr:
            print(stderr, file=sys.stderr)
        raise SystemExit(f"{stage} failed with exit code {code}")


def ffprobe_video(ffprobe: str, path: Path):
    cmd = [
        ffprobe, "-v", "error", "-count_frames", "-select_streams", "v:0",
        "-show_entries", "stream=width,height,r_frame_rate,nb_read_frames,duration",
        "-of", "json", str(path),
    ]
    out = run_checked(cmd, "probe_output")
    data = json.loads(out)
    streams = data.get("streams") or []
    if not streams:
        raise SystemExit(f"No video stream in output: {path}")
    return streams[0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--library", type=Path, required=True)
    ap.add_argument("--plan", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path, required=True)
    ap.add_argument("--width", type=int, default=512)
    ap.add_argument("--height", type=int, default=912)
    ap.add_argument("--fps", type=float, default=24.0)
    ap.add_argument("--frames", type=int, default=65)
    ap.add_argument("--ffmpeg", default="ffmpeg")
    ap.add_argument("--ffprobe", default="ffprobe")
    args = ap.parse_args()

    if args.frames < 1 or args.frames % 4 != 1:
        raise SystemExit("--frames must be positive and 4n+1 for this Wan spike")
    if args.width <= 0 or args.height <= 0 or args.fps <= 0:
        raise SystemExit("Invalid width/height/fps")

    ffmpeg = require_exe(args.ffmpeg)
    ffprobe = require_exe(args.ffprobe)

    print("stage=load_inputs", flush=True)
    lib = load_json(args.library)
    plan = load_json(args.plan)
    if lib.get("schema") != "joao-motion-library/v1":
        raise SystemExit(f"Unexpected library schema: {lib.get('schema')}")
    if plan.get("schema") != "behavioral-pose-driver-plan/v3":
        raise SystemExit(f"Unexpected driver plan schema: {plan.get('schema')}")
    windows = plan.get("windows") or []
    if len(windows) != 2:
        raise SystemExit(f"Expected exactly 2 v3 windows, got {len(windows)}")

    base_ids = [windows[0]["base"]["unit"], windows[1]["base"]["unit"]]
    u0, u1 = find_unit(lib, base_ids[0]), find_unit(lib, base_ids[1])
    for u in (u0, u1):
        p = Path(u.get("source_video") or "")
        if not p.is_file():
            raise SystemExit(f"Source video missing for {u['library_unit_id']}: {p}")

    seg_d = float(plan["segment_duration_s"])
    overlap = float(plan["transition_blend_s"])
    overlap_start = float(plan["overlap_start_s"])
    if abs((seg_d - overlap) - overlap_start) > 1e-4:
        raise SystemExit("Plan overlap geometry is inconsistent")

    src0_d = float(u0["source_end_s"]) - float(u0["source_start_s"])
    src1_d = float(u1["source_end_s"]) - float(u1["source_start_s"])
    if src0_d <= 0 or src1_d <= 0:
        raise SystemExit("Invalid source unit duration")
    retime0 = seg_d / src0_d
    retime1 = seg_d / src1_d

    args.output_dir.mkdir(parents=True, exist_ok=True)
    out_video = args.output_dir / f"pose_video_real_spike{args.frames}.mp4"
    ref_image = args.output_dir / "reference_image_real.png"
    contact = args.output_dir / "pose_video_real_contact.jpg"
    manifest_path = args.output_dir / "real_rgb_spike_manifest.json"

    vf0 = (
        f"scale={args.width}:{args.height}:force_original_aspect_ratio=increase:flags=lanczos,"
        f"crop={args.width}:{args.height},setsar=1,"
        f"setpts={retime0:.12f}*(PTS-STARTPTS),fps={args.fps:.12f},"
        f"trim=duration={seg_d:.12f}[v0]"
    )
    vf1 = (
        f"scale={args.width}:{args.height}:force_original_aspect_ratio=increase:flags=lanczos,"
        f"crop={args.width}:{args.height},setsar=1,"
        f"setpts={retime1:.12f}*(PTS-STARTPTS),fps={args.fps:.12f},"
        f"trim=duration={seg_d:.12f}[v1]"
    )
    filter_complex = (
        f"[0:v]{vf0};[1:v]{vf1};"
        f"[v0][v1]xfade=transition=fade:duration={overlap:.12f}:offset={overlap_start:.12f},"
        f"fps={args.fps:.12f},format=yuv420p[outv]"
    )

    print("REAL RGB WAN DRIVER SPIKE")
    print("========================")
    print(f"Window 0: {u0['library_unit_id']} / {u0['source_start_s']:.3f}-{u0['source_end_s']:.3f}s")
    print(f"Window 1: {u1['library_unit_id']} / {u1['source_start_s']:.3f}-{u1['source_end_s']:.3f}s")
    print(f"Retiming: {retime0:.6f}x / {retime1:.6f}x -> {seg_d:.3f}s each")
    print(f"Overlap: {overlap_start:.3f}-{seg_d:.3f}s / {overlap:.3f}s")
    print(f"Output: {args.width}x{args.height} @ {args.fps:g} fps / {args.frames} frames")
    print("No still-image warp. No DWPose. No Wan inference.", flush=True)

    cmd = [
        ffmpeg, "-y", "-hide_banner", "-loglevel", "error",
        "-ss", f"{float(u0['source_start_s']):.6f}", "-t", f"{src0_d:.6f}", "-i", str(Path(u0["source_video"])),
        "-ss", f"{float(u1['source_start_s']):.6f}", "-t", f"{src1_d:.6f}", "-i", str(Path(u1["source_video"])),
        "-filter_complex", filter_complex,
        "-map", "[outv]", "-an", "-frames:v", str(args.frames),
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p",
        "-progress", "pipe:1", "-nostats", str(out_video),
    ]
    run_ffmpeg_progress(cmd, "assemble_real_rgb", args.frames)

    # Reference image: midpoint of first validated PRIMARY-led base unit.
    ref_t = float(u0["source_start_s"]) + src0_d * 0.5
    ref_filter = (
        f"scale={args.width}:{args.height}:force_original_aspect_ratio=increase:flags=lanczos,"
        f"crop={args.width}:{args.height},setsar=1"
    )
    ref_cmd = [
        ffmpeg, "-y", "-hide_banner", "-loglevel", "error", "-ss", f"{ref_t:.6f}",
        "-i", str(Path(u0["source_video"])), "-frames:v", "1", "-vf", ref_filter, str(ref_image),
    ]
    run_checked(ref_cmd, "extract_reference")

    ids = [0, 8, 16, 24, 32, 40, 48, 56, 64]
    expr = "+".join(f"eq(n\\,{i})" for i in ids if i < args.frames)
    contact_filter = (
        f"select='{expr}',scale=256:456:flags=lanczos,"
        "drawtext=text='f=%{n}':x=8:y=8:fontsize=18:fontcolor=white:borderw=2,"
        "tile=3x3:padding=4:margin=4"
    )
    contact_cmd = [
        ffmpeg, "-y", "-hide_banner", "-loglevel", "error", "-i", str(out_video),
        "-vf", contact_filter, "-frames:v", "1", str(contact),
    ]
    # Some Windows ffmpeg builds lack drawtext/fontconfig. Fall back without labels.
    try:
        run_checked(contact_cmd, "contact_sheet")
    except SystemExit:
        contact_filter = f"select='{expr}',scale=256:456:flags=lanczos,tile=3x3:padding=4:margin=4"
        contact_cmd = [
            ffmpeg, "-y", "-hide_banner", "-loglevel", "error", "-i", str(out_video),
            "-vf", contact_filter, "-frames:v", "1", str(contact),
        ]
        run_checked(contact_cmd, "contact_sheet_fallback")

    meta = ffprobe_video(ffprobe, out_video)
    got_frames = int(meta.get("nb_read_frames") or 0)
    got_w = int(meta.get("width") or 0)
    got_h = int(meta.get("height") or 0)
    if got_frames != args.frames:
        raise SystemExit(f"Output frame count mismatch: expected {args.frames}, got {got_frames}")
    if got_w != args.width or got_h != args.height:
        raise SystemExit(f"Output size mismatch: expected {args.width}x{args.height}, got {got_w}x{got_h}")

    manifest = {
        "schema": "wan-animate2-real-rgb-driver-spike/v1",
        "driver_plan": str(args.plan.resolve()),
        "library": str(args.library.resolve()),
        "wan_contract": "single raw RGB pose_video; no separate face_video input in installed WanAnimate2ToVideo",
        "purpose": "first real-RGB end-to-end body/head/gesture driving gate",
        "face_note": "v3 secondary facial donor remains canonical pose-domain evidence but is not separately injected in this first Wan gate",
        "width": args.width,
        "height": args.height,
        "fps": args.fps,
        "frames": args.frames,
        "segment_duration_s": seg_d,
        "overlap_s": overlap,
        "overlap_start_s": overlap_start,
        "windows": [
            {
                "unit": u0["library_unit_id"], "source": u0["source_video"],
                "source_start_s": u0["source_start_s"], "source_end_s": u0["source_end_s"],
                "retime_factor": retime0,
            },
            {
                "unit": u1["library_unit_id"], "source": u1["source_video"],
                "source_start_s": u1["source_start_s"], "source_end_s": u1["source_end_s"],
                "retime_factor": retime1,
            },
        ],
        "outputs": {
            "pose_video": str(out_video.resolve()),
            "reference_image": str(ref_image.resolve()),
            "contact_sheet": str(contact.resolve()),
        },
        "probe": meta,
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    print("stage=complete", flush=True)
    print(f"Pose video: {out_video}")
    print(f"Reference: {ref_image}")
    print(f"Contact: {contact}")
    print(f"Manifest: {manifest_path}")
    print("Wan-Animate-2: NOT INVOKED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
