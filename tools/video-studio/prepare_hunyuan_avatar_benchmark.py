from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import time
from pathlib import Path

from huggingface_hub import hf_hub_download

REPO_ID = "DeepBeepMeep/HunyuanVideo"
MODEL_FILE = "hunyuan_video_avatar_720_quanto_bf16_int8.safetensors"
TEXT_ENCODER_FILE = "llava-llama-3-8b/llava-llama-3-8b-v1_1_vlm_quanto_int8.safetensors"

# Mirrors the current Wan2GP Hunyuan dependency layout, plus the selected
# Avatar transformer and selected INT8 text encoder.
FILES = [
    MODEL_FILE,
    TEXT_ENCODER_FILE,
    "llava-llama-3-8b/config.json",
    "llava-llama-3-8b/special_tokens_map.json",
    "llava-llama-3-8b/tokenizer.json",
    "llava-llama-3-8b/tokenizer_config.json",
    "llava-llama-3-8b/preprocessor_config.json",
    "clip_vit_large_patch14/text_config.json",
    "clip_vit_large_patch14/merges.txt",
    "clip_vit_large_patch14/model.safetensors",
    "clip_vit_large_patch14/preprocessor_config.json",
    "clip_vit_large_patch14/special_tokens_map.json",
    "clip_vit_large_patch14/tokenizer.json",
    "clip_vit_large_patch14/tokenizer_config.json",
    "clip_vit_large_patch14/vocab.json",
    "whisper-tiny/config.json",
    "whisper-tiny/model.safetensors",
    "whisper-tiny/preprocessor_config.json",
    "whisper-tiny/special_tokens_map.json",
    "whisper-tiny/tokenizer_config.json",
    "det_align/detface.pt",
    "hunyuan_video_720_quanto_int8_map.json",
    "hunyuan_video_custom_VAE_fp32.safetensors",
    "hunyuan_video_custom_VAE_config.json",
    "hunyuan_video_VAE_fp32.safetensors",
    "hunyuan_video_VAE_config.json",
]

EXPECTED_SHA256 = {
    MODEL_FILE: "cfaa6328f7a86d371cfa8e1ddea67685eac99d1fe26ef5d80bab4afd8927d5cf",
    TEXT_ENCODER_FILE: "378c1a2fe0b45ff39b3a5ab33437559a260e0439291cbf572b8540454205ccd7",
    "whisper-tiny/model.safetensors": "7ebd0e69e78190ffe1438491fa05cc1f5c1aa3a4c4db3bc1723adbb551ea2395",
    "hunyuan_video_VAE_fp32.safetensors": "7c68a6295f9034a88225fbafb1f3258291a08d57a1fdb938233fa57b1b8f4883",
}


def sha256_file(path: Path, chunk_size: int = 16 * 1024 * 1024) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            block = f.read(chunk_size)
            if not block:
                break
            h.update(block)
    return h.hexdigest()


def free_gb(path: Path) -> float:
    return shutil.disk_usage(path).free / (1024 ** 3)


def size_gb(path: Path) -> float:
    return path.stat().st_size / (1024 ** 3)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--wangp-root", default=r"Z:\AI\WanGP")
    p.add_argument(
        "--reference-image",
        default=r"Z:\AI\WanAnimate2\input\video_studio\wan_s2v_benchmark\joao_wan_s2v_ref.png",
    )
    p.add_argument(
        "--speech-audio",
        default=r"Z:\AI\WanAnimate2\input\video_studio\wan_s2v_benchmark\joao_wan_s2v_test_4p5s.wav",
    )
    p.add_argument("--download", action="store_true")
    p.add_argument("--verify-large-sha", action="store_true")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.wangp_root)
    ckpts = root / "ckpts"
    ref_src = Path(args.reference_image)
    audio_src = Path(args.speech_audio)
    benchmark_dir = root / "inputs" / "video_studio" / "hunyuan_avatar_benchmark"
    ref_dst = benchmark_dir / "joao_hunyuan_avatar_ref.png"
    audio_dst = benchmark_dir / "joao_hunyuan_avatar_test_4p5s.wav"
    manifest_path = root / "hunyuan_avatar_benchmark_prepare_manifest.json"

    print("HUNYUAN-AVATAR-PREPARE-01", flush=True)
    print("=========================", flush=True)
    print(f"WanGP root: {root}", flush=True)
    print(f"Download enabled: {args.download}", flush=True)
    print(flush=True)

    wan_python = root / "env_uv" / "Scripts" / "python.exe"
    if not root.is_dir():
        raise SystemExit(f"WanGP root missing: {root}")
    if not wan_python.is_file():
        raise SystemExit(f"WanGP runtime missing: {wan_python}")
    if not ref_src.is_file():
        raise SystemExit(f"Reference image missing: {ref_src}")
    if not audio_src.is_file():
        raise SystemExit(f"Speech audio missing: {audio_src}")

    ckpts.mkdir(parents=True, exist_ok=True)
    benchmark_dir.mkdir(parents=True, exist_ok=True)

    print("DISK SPACE", flush=True)
    print("==========", flush=True)
    before_free = free_gb(root)
    print(f"Free space before payload: {before_free:.2f} GB", flush=True)
    if args.download and before_free < 30.0:
        raise SystemExit("Less than 30 GB free. Refusing Hunyuan payload download.")
    print("Payload reserve gate: PASS", flush=True)
    print(flush=True)

    print("BENCHMARK INPUTS", flush=True)
    print("================", flush=True)
    shutil.copy2(ref_src, ref_dst)
    shutil.copy2(audio_src, audio_dst)
    print(f"Reference image: {ref_dst}", flush=True)
    print(f"Speech audio: {audio_dst}", flush=True)
    print(flush=True)

    print("PAYLOAD", flush=True)
    print("=======", flush=True)
    downloaded: list[str] = []
    reused: list[str] = []
    missing: list[str] = []
    started = time.time()

    for rel in FILES:
        dst = ckpts / Path(rel)
        if dst.is_file() and dst.stat().st_size > 0:
            reused.append(rel)
            print(f"REUSE     {rel}  ({size_gb(dst):.3f} GB)", flush=True)
            continue

        if not args.download:
            missing.append(rel)
            print(f"MISSING   {rel}", flush=True)
            continue

        dst.parent.mkdir(parents=True, exist_ok=True)
        print(f"DOWNLOAD  {rel}", flush=True)
        resolved = hf_hub_download(
            repo_id=REPO_ID,
            filename=rel,
            local_dir=str(ckpts),
        )
        resolved_path = Path(resolved)
        if not resolved_path.is_file() or resolved_path.stat().st_size <= 0:
            raise RuntimeError(f"Download did not produce a valid file: {rel}")
        downloaded.append(rel)

    print(flush=True)
    print("VALIDATION", flush=True)
    print("==========", flush=True)
    critical = [
        MODEL_FILE,
        TEXT_ENCODER_FILE,
        "clip_vit_large_patch14/model.safetensors",
        "whisper-tiny/model.safetensors",
        "det_align/detface.pt",
        "hunyuan_video_custom_VAE_fp32.safetensors",
        "hunyuan_video_custom_VAE_config.json",
    ]
    for rel in critical:
        path = ckpts / Path(rel)
        if path.is_file() and path.stat().st_size > 0:
            print(f"PASS      {rel}  ({size_gb(path):.3f} GB)", flush=True)
        else:
            print(f"FAIL      {rel}", flush=True)
            missing.append(rel)

    sha_results: dict[str, dict[str, str | bool]] = {}
    if args.verify_large_sha:
        print(flush=True)
        print("SHA256", flush=True)
        print("======", flush=True)
        for rel, expected in EXPECTED_SHA256.items():
            path = ckpts / Path(rel)
            if not path.is_file():
                continue
            actual = sha256_file(path)
            ok = actual.lower() == expected.lower()
            sha_results[rel] = {"expected": expected, "actual": actual, "ok": ok}
            print(("PASS" if ok else "FAIL") + f"  {rel}", flush=True)
            if not ok:
                raise RuntimeError(f"SHA256 mismatch: {rel}")

    after_free = free_gb(root)
    elapsed = time.time() - started

    manifest = {
        "schema": "HUNYUAN-AVATAR-PREPARE-01",
        "repo_id": REPO_ID,
        "wangp_root": str(root),
        "ckpts_root": str(ckpts),
        "model": MODEL_FILE,
        "text_encoder": TEXT_ENCODER_FILE,
        "reference_image": str(ref_dst),
        "speech_audio": str(audio_dst),
        "downloaded": downloaded,
        "reused": reused,
        "missing": sorted(set(missing)),
        "sha256": sha_results,
        "free_gb_before": round(before_free, 2),
        "free_gb_after": round(after_free, 2),
        "elapsed_seconds": elapsed,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print(flush=True)
    print("MANIFEST", flush=True)
    print("========", flush=True)
    print(manifest_path, flush=True)
    print(flush=True)
    print("RESULT", flush=True)
    print("======", flush=True)
    if missing:
        print("HUNYUAN AVATAR BENCHMARK ASSETS NOT COMPLETE", flush=True)
        print("Run again with -Download.", flush=True)
        return 2

    print("HUNYUAN AVATAR BENCHMARK ASSETS PREPARED", flush=True)
    print(f"Downloaded: {len(downloaded)} files", flush=True)
    print(f"Reused: {len(reused)} files", flush=True)
    print(f"Free Z after payload: {after_free:.2f} GB", flush=True)
    print("Next: run one direct Avatar benchmark with the same image and 4.5 s speech audio.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
