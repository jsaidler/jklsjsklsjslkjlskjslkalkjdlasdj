#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from fractions import Fraction


def fail(message: str, code: int = 2) -> None:
    print(f"H3-H0-DRIVER: FAIL - {message}", file=sys.stderr, flush=True)
    raise SystemExit(code)


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def frame_time_seconds(frame, fallback_index: int, fallback_fps: float) -> float:
    if frame.pts is not None and frame.time_base is not None:
        return float(frame.pts * frame.time_base)
    return fallback_index / fallback_fps


def main() -> None:
    ap = argparse.ArgumentParser(description="Normalize the Roguelite H3 H0 reference video to 24 fps / 124 frames without crop or resize.")
    ap.add_argument("--source", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--fps", type=int, default=24)
    ap.add_argument("--frames", type=int, default=124)
    args = ap.parse_args()

    if args.fps <= 0:
        fail("fps must be positive")
    if args.frames <= 0 or args.frames % 17 != 5:
        fail(f"frame count must satisfy H3 17k+5 rule; got {args.frames}")

    source = os.path.abspath(args.source)
    output = os.path.abspath(args.output)
    manifest_path = os.path.abspath(args.manifest)
    if not os.path.isfile(source):
        fail(f"source video missing: {source}")

    try:
        import av
    except Exception as exc:
        fail(f"PyAV unavailable in the pinned ComfyUI environment: {exc}")

    os.makedirs(os.path.dirname(output), exist_ok=True)
    os.makedirs(os.path.dirname(manifest_path), exist_ok=True)
    if os.path.exists(output):
        os.remove(output)

    src = av.open(source)
    video_streams = [s for s in src.streams if s.type == "video"]
    if not video_streams:
        src.close()
        fail("source has no video stream")
    stream = video_streams[0]

    source_width = int(stream.codec_context.width or 0)
    source_height = int(stream.codec_context.height or 0)
    if source_width <= 0 or source_height <= 0:
        src.close()
        fail(f"invalid source geometry {source_width}x{source_height}")

    source_fps = None
    for candidate in (stream.average_rate, stream.base_rate, stream.guessed_rate):
        if candidate:
            try:
                source_fps = float(candidate)
                if source_fps > 0:
                    break
            except Exception:
                pass
    if not source_fps or source_fps <= 0:
        source_fps = 30.0

    source_duration = None
    if stream.duration is not None and stream.time_base is not None:
        source_duration = float(stream.duration * stream.time_base)
    elif src.duration is not None:
        source_duration = float(src.duration) / 1_000_000.0

    required_duration = (args.frames - 1) / float(args.fps)
    if source_duration is not None and source_duration + (1.0 / args.fps) < required_duration:
        src.close()
        fail(
            f"source duration {source_duration:.3f}s is too short for {args.frames} frames at {args.fps} fps "
            f"(needs about {required_duration:.3f}s)"
        )

    try:
        dst = av.open(output, mode="w")
        out_stream = dst.add_stream("libx264", rate=args.fps)
        out_stream.width = source_width
        out_stream.height = source_height
        out_stream.pix_fmt = "yuv420p"
        out_stream.options = {"crf": "12", "preset": "slow"}
        out_stream.time_base = Fraction(1, args.fps)
    except Exception as exc:
        src.close()
        try:
            if os.path.exists(output):
                os.remove(output)
        except OSError:
            pass
        fail(f"could not create H.264 output with the pinned PyAV build: {exc}")

    out_count = 0
    decoded_count = 0
    next_target = 0.0
    last_source_time = None

    try:
        for frame in src.decode(stream):
            t = frame_time_seconds(frame, decoded_count, source_fps)
            decoded_count += 1
            last_source_time = t

            while out_count < args.frames and t + 1e-9 >= next_target:
                encoded = frame.reformat(width=source_width, height=source_height, format="yuv420p")
                encoded.pts = out_count
                encoded.time_base = Fraction(1, args.fps)
                for packet in out_stream.encode(encoded):
                    dst.mux(packet)
                out_count += 1
                next_target = out_count / float(args.fps)

            if out_count >= args.frames:
                break

        for packet in out_stream.encode():
            dst.mux(packet)
    except Exception as exc:
        fail(f"decode/resample/encode failed after {out_count} output frames: {exc}")
    finally:
        src.close()
        dst.close()

    if out_count != args.frames:
        try:
            os.remove(output)
        except OSError:
            pass
        fail(
            f"source ended before target sequence was complete: wrote {out_count}/{args.frames} frames; "
            f"last source timestamp={last_source_time}"
        )

    manifest = {
        "gate": "MINIMAX_H3_H0_DRIVER_NORMALIZATION",
        "status": "PREPARED",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "source": source,
        "source_sha256": sha256_file(source),
        "source_width": source_width,
        "source_height": source_height,
        "source_fps_estimate": source_fps,
        "source_duration_seconds": source_duration,
        "decoded_source_frames_until_completion": decoded_count,
        "output": output,
        "output_sha256": sha256_file(output),
        "output_bytes": os.path.getsize(output),
        "output_width": source_width,
        "output_height": source_height,
        "output_fps": args.fps,
        "output_frames": out_count,
        "output_duration_seconds": out_count / float(args.fps),
        "spatial_transform": "NONE",
        "crop": "NONE",
        "resize": "NONE",
        "temporal_transform": "timestamp resample to 24 fps; first decoded source frame at or after each target timestamp",
        "audio": "REMOVED_FOR_H0_MOTION_REFERENCE",
        "encoder": "libx264 crf12 preset=slow yuv420p",
        "purpose": "Preserve source geometry and trajectory while satisfying MiniMax H3 Ref2VA's 24 fps reference-video contract and H0 124-frame comparison window.",
    }
    with open(manifest_path, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, ensure_ascii=False, indent=2)

    print(
        f"H3-H0-DRIVER: PASS - {source_width}x{source_height}, {args.fps} fps, {out_count} frames -> {output}",
        flush=True,
    )
    print(f"H3-H0-DRIVER: manifest {manifest_path}", flush=True)


if __name__ == "__main__":
    main()
