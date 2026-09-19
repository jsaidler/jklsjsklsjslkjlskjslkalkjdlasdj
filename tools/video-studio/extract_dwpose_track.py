#!/usr/bin/env python3
"""Extract normalized COCO WholeBody 133 pose JSONL from a local video.

Designed specifically to reuse the already-installed WanGP DWPose code and ONNX
weights. No download, training or renderer invocation occurs here.
"""

from __future__ import annotations

import argparse
import json
import math
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

DEFAULT_SOURCE = Path(r"Z:\AI\VideoStudio\profiles\joao\behavior\avatar_v\sources\VID_20260911_140124885.mp4")
DEFAULT_WANGP = Path(r"Z:\AI\WanGP")
DEFAULT_OUTPUT = Path(r"Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\VID_20260911_140124885\pose_coco133.jsonl")
DEFAULT_DET = Path(r"Z:\AI\WanGP\ckpts\pose\yolox_l.onnx")
DEFAULT_POSE = Path(r"Z:\AI\WanGP\ckpts\pose\dw-ll_ucoco_384.onnx")


class PoseError(RuntimeError):
    pass


def find_exe(name: str) -> str:
    p = Path(name)
    if p.is_file():
        return str(p)
    found = shutil.which(name)
    if not found:
        raise PoseError(f"Executable not found: {name}")
    return found


def _stream_rotation_degrees(stream: dict[str, Any]) -> int:
    """Return display rotation reported by ffprobe, normalized to [0, 360)."""
    rotation = None
    for side in stream.get("side_data_list") or []:
        if "rotation" in side:
            rotation = side.get("rotation")
            break
    if rotation is None:
        rotation = (stream.get("tags") or {}).get("rotate")
    try:
        value = int(round(float(rotation))) if rotation is not None else 0
    except (TypeError, ValueError):
        value = 0
    return value % 360


def ffprobe_video(source: Path, ffprobe: str) -> dict[str, Any]:
    run = subprocess.run(
        [
            ffprobe,
            "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=width,height:stream_tags=rotate:stream_side_data=rotation",
            "-show_entries", "format=duration",
            "-of", "json",
            str(source),
        ],
        capture_output=True,
        text=True,
    )
    if run.returncode:
        raise PoseError(run.stderr.strip() or "ffprobe failed")
    data = json.loads(run.stdout)
    stream = data["streams"][0]
    coded_width = int(stream["width"])
    coded_height = int(stream["height"])
    rotation = _stream_rotation_degrees(stream)
    if rotation in (90, 270):
        display_width, display_height = coded_height, coded_width
    else:
        display_width, display_height = coded_width, coded_height
    return {
        "coded_width": coded_width,
        "coded_height": coded_height,
        "display_width": display_width,
        "display_height": display_height,
        "rotation_degrees": rotation,
        "duration_s": float(data["format"]["duration"]),
    }


def analysis_size(width: int, height: int, long_side: int) -> tuple[int, int]:
    if width >= height:
        w = long_side
        h = max(2, int(round(height * long_side / width / 2.0)) * 2)
    else:
        h = long_side
        w = max(2, int(round(width * long_side / height / 2.0)) * 2)
    return w, h


def read_exact(stream, size: int) -> bytes:
    chunks: list[bytes] = []
    remaining = size
    while remaining > 0:
        chunk = stream.read(remaining)
        if not chunk:
            break
        chunks.append(chunk)
        remaining -= len(chunk)
    return b"".join(chunks)


def bbox_center(box) -> tuple[float, float]:
    return (float(box[0] + box[2]) * 0.5, float(box[1] + box[3]) * 0.5)


def bbox_area(box) -> float:
    return max(0.0, float(box[2] - box[0])) * max(0.0, float(box[3] - box[1]))


def choose_box(boxes, previous, width: int, height: int):
    if len(boxes) == 0:
        return None
    if previous is None:
        return boxes[max(range(len(boxes)), key=lambda i: bbox_area(boxes[i]))]
    pcx, pcy = bbox_center(previous)
    diag = max(1.0, math.hypot(width, height))
    prev_area = max(1.0, bbox_area(previous))
    best = None
    best_score = None
    for box in boxes:
        cx, cy = bbox_center(box)
        center_distance = math.hypot(cx - pcx, cy - pcy) / diag
        area_ratio = min(bbox_area(box), prev_area) / max(bbox_area(box), prev_area, 1.0)
        score = center_distance + 0.35 * (1.0 - area_ratio)
        if best_score is None or score < best_score:
            best_score = score
            best = box
    return best


def session_pair(ort, det_path: Path, pose_path: Path, provider_mode: str):
    available = ort.get_available_providers()
    candidates: list[str]
    if provider_mode == "cuda":
        candidates = ["CUDAExecutionProvider"]
    elif provider_mode == "cpu":
        candidates = ["CPUExecutionProvider"]
    else:
        candidates = []
        if "CUDAExecutionProvider" in available:
            candidates.append("CUDAExecutionProvider")
        candidates.append("CPUExecutionProvider")

    errors: list[str] = []
    for provider in candidates:
        if provider not in available:
            errors.append(f"{provider} not available")
            continue
        try:
            det = ort.InferenceSession(str(det_path), providers=[provider])
            pose = ort.InferenceSession(str(pose_path), providers=[provider])
            return det, pose, provider, available
        except Exception as exc:
            errors.append(f"{provider}: {exc}")
    raise PoseError("Could not create DWPose ONNX sessions: " + "; ".join(errors))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    ap.add_argument("--wangp-root", type=Path, default=DEFAULT_WANGP)
    ap.add_argument("--det-model", type=Path, default=DEFAULT_DET)
    ap.add_argument("--pose-model", type=Path, default=DEFAULT_POSE)
    ap.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    ap.add_argument("--fps", type=float, default=6.0)
    ap.add_argument("--long-side", type=int, default=960)
    ap.add_argument("--provider", choices=["auto", "cuda", "cpu"], default="auto")
    ap.add_argument("--start", type=float, default=0.0)
    ap.add_argument("--duration", type=float)
    ap.add_argument("--max-frames", type=int)
    ap.add_argument("--ffmpeg", default="ffmpeg")
    ap.add_argument("--ffprobe", default="ffprobe")
    args = ap.parse_args()

    source = args.source.resolve()
    root = args.wangp_root.resolve()
    det_path = args.det_model.resolve()
    pose_path = args.pose_model.resolve()
    output = args.output.resolve()
    for label, path in [("source", source), ("WanGP root", root), ("detector", det_path), ("pose model", pose_path)]:
        if not path.exists():
            raise PoseError(f"Missing {label}: {path}")
    if args.fps <= 0:
        raise PoseError("--fps must be > 0")

    sys.path.insert(0, str(root))
    try:
        import cv2
        import numpy as np
        import onnxruntime as ort
        from preprocessing.dwpose.onnxdet import inference_detector
        from preprocessing.dwpose.onnxpose import inference_pose
    except Exception as exc:
        raise PoseError(f"WanGP DWPose imports failed: {exc}") from exc

    ffmpeg = find_exe(args.ffmpeg)
    ffprobe = find_exe(args.ffprobe)
    info = ffprobe_video(source, ffprobe)
    aw, ah = analysis_size(info["display_width"], info["display_height"], args.long_side)
    det_session, pose_session, provider, available = session_pair(ort, det_path, pose_path, args.provider)

    cmd = [ffmpeg, "-hide_banner", "-loglevel", "error"]
    if args.start > 0:
        cmd += ["-ss", f"{args.start:.6f}"]
    cmd += ["-i", str(source)]
    if args.duration is not None:
        cmd += ["-t", f"{args.duration:.6f}"]
    # FFmpeg autorotates by default. aw/ah are therefore derived from display,
    # not coded, dimensions so portrait sources are not distorted before DWPose.
    cmd += ["-an", "-vf", f"fps={args.fps:g},scale={aw}:{ah}:flags=area", "-f", "rawvideo", "-pix_fmt", "bgr24", "pipe:1"]

    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    assert proc.stdout is not None
    frame_bytes = aw * ah * 3
    output.parent.mkdir(parents=True, exist_ok=True)
    summary_path = output.with_suffix(output.suffix + ".summary.json")

    previous_box = None
    frames = 0
    fallback_frames = 0
    score_acc = 0.0
    score_count = 0
    started = time.time()

    with output.open("w", encoding="utf-8", newline="\n") as fh:
        while True:
            raw = read_exact(proc.stdout, frame_bytes)
            if len(raw) != frame_bytes:
                break
            image = np.frombuffer(raw, dtype=np.uint8).reshape((ah, aw, 3))
            boxes = inference_detector(det_session, image)
            box = choose_box(boxes, previous_box, aw, ah)
            detector_fallback = box is None
            if detector_fallback:
                pose_boxes = np.empty((0, 4), dtype=np.float32)
                fallback_frames += 1
            else:
                previous_box = np.asarray(box, dtype=np.float32)
                pose_boxes = np.asarray([previous_box], dtype=np.float32)

            keypoints, scores = inference_pose(pose_session, pose_boxes, image)
            if len(keypoints) == 0 or keypoints.shape[1] != 133:
                raise PoseError(f"Unexpected pose shape at frame {frames}: {getattr(keypoints, 'shape', None)}")
            pts = keypoints[0]
            scr = scores[0]
            kp_out = []
            for (x, y), score in zip(pts, scr):
                xf = float(x) / aw if math.isfinite(float(x)) else None
                yf = float(y) / ah if math.isfinite(float(y)) else None
                if xf is not None:
                    xf = max(0.0, min(1.0, xf))
                if yf is not None:
                    yf = max(0.0, min(1.0, yf))
                sf = float(score) if math.isfinite(float(score)) else 0.0
                kp_out.append([xf, yf, sf])
                score_acc += sf
                score_count += 1

            bbox_norm = None
            if box is not None:
                bbox_norm = [
                    max(0.0, min(1.0, float(box[0]) / aw)),
                    max(0.0, min(1.0, float(box[1]) / ah)),
                    max(0.0, min(1.0, float(box[2]) / aw)),
                    max(0.0, min(1.0, float(box[3]) / ah)),
                ]

            record = {
                "t": round(args.start + frames / args.fps, 6),
                "schema": "coco_wholebody_133",
                "keypoints": kp_out,
                "bbox_norm": bbox_norm,
                "detector_fallback": detector_fallback,
                "provider": provider,
            }
            fh.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")
            frames += 1
            if frames % 60 == 0:
                elapsed = time.time() - started
                print(f"frames={frames} elapsed={elapsed:.1f}s provider={provider}", flush=True)
            if args.max_frames is not None and frames >= args.max_frames:
                break

    proc.stdout.close()
    if args.max_frames is not None and frames >= args.max_frames:
        proc.terminate()
    err = proc.stderr.read() if proc.stderr is not None else b""
    rc = proc.wait()
    if rc not in (0, 255) and not (args.max_frames is not None and frames >= args.max_frames):
        raise PoseError("ffmpeg pose decode failed: " + err.decode("utf-8", "replace"))
    if frames == 0:
        raise PoseError("No frames were decoded for pose extraction.")

    elapsed = time.time() - started
    summary = {
        "schema": "coco_wholebody_133",
        "source": str(source),
        "output": str(output),
        "source_duration_s": info["duration_s"],
        "coded_width": info["coded_width"],
        "coded_height": info["coded_height"],
        "display_width": info["display_width"],
        "display_height": info["display_height"],
        "rotation_degrees": info["rotation_degrees"],
        "start_s": args.start,
        "requested_duration_s": args.duration,
        "sample_fps": args.fps,
        "analysis_width": aw,
        "analysis_height": ah,
        "frames": frames,
        "last_timestamp_s": round(args.start + (frames - 1) / args.fps, 6),
        "detector_fallback_frames": fallback_frames,
        "detector_fallback_ratio": fallback_frames / frames,
        "mean_keypoint_score": (score_acc / score_count) if score_count else None,
        "onnx_provider": provider,
        "available_onnx_providers": available,
        "elapsed_s": elapsed,
        "frames_per_second_wall": frames / elapsed if elapsed > 0 else None,
    }
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except PoseError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
