#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageOps, ImageDraw


def fail(message: str) -> None:
    raise RuntimeError(message)


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def normalized_xy(rec: dict, source_w: float, source_h: float) -> tuple[float, float]:
    x = float(rec["x"]) / source_w
    y = float(rec["y"]) / source_h
    return max(0.0, min(1.0, x)), max(0.0, min(1.0, y))


def prepare(args: argparse.Namespace) -> int:
    model_training = Path(args.model_training).resolve()
    guide_path = Path(args.guide).resolve()
    master_path = Path(args.master).resolve()
    dataset_root = model_training / "data" / "exilada_walk8_ssd"
    character_root = dataset_root / "characters" / "exilada"
    motion_root = character_root / "motions" / "walk8"
    ground_truth = motion_root / "ground_truth"
    poses_dir = motion_root / "poses"
    reference_pose_path = dataset_root / "reference_pose.png"
    config_path = model_training / "configs" / "prompts" / "inference_exilada_walk8.yaml"
    patched_inference = model_training / "inference_roguelite_walk8.py"
    prep_marker = Path(args.marker).resolve()

    if not model_training.is_dir():
        fail(f"ModelTraining directory missing: {model_training}")
    if not guide_path.is_file():
        fail(f"approved C1A guide missing: {guide_path}")
    if not master_path.is_file():
        fail(f"Exilada master missing: {master_path}")

    guide = read_json(guide_path)
    frames = guide.get("frames", [])
    if guide.get("gate") != "G3S-C1A":
        fail("unexpected guide gate; expected G3S-C1A")
    if len(frames) != 8:
        fail(f"expected 8 approved C1A frames, got {len(frames)}")

    expected_events = [
        "left_contact", "left_down", "left_passing", "left_up",
        "right_contact", "right_down", "right_passing", "right_up",
    ]
    actual_events = [str(f.get("event")) for f in frames]
    if actual_events != expected_events:
        fail(f"C1A event order mismatch: {actual_events}")

    # The C1A guide was authored in the locked gameplay projection.
    source_w, source_h = 640.0, 360.0

    # Reset only the dedicated SSD smoke-test dataset.
    if dataset_root.exists():
        shutil.rmtree(dataset_root)
    ground_truth.mkdir(parents=True, exist_ok=True)
    poses_dir.mkdir(parents=True, exist_ok=True)

    # SSD upstream inference uses ground_truth[0] as the appearance reference.
    shutil.copy2(master_path, ground_truth / "frame_000_reference.png")

    # Openpose/DWPose model paths in the upstream code are relative to ModelTraining.
    os.chdir(model_training)
    sys.path.insert(0, str(model_training))
    from openpose import OpenposeDetector, draw_poses  # noqa: E402
    from openpose.types import BodyResult, HumanPoseResult, Keypoint  # noqa: E402

    # IMPORTANT: use the downloaded DWPose AI to extract the pose of the actual
    # Exilada master. This is a separate reference pose; it is not one of the 8
    # walk targets.
    master_rgb = Image.open(master_path).convert("RGB")
    master_bgr = cv2.cvtColor(np.array(master_rgb), cv2.COLOR_RGB2BGR)
    master_bgr = cv2.resize(master_bgr, (512, 512), interpolation=cv2.INTER_NEAREST)
    detector = OpenposeDetector()
    ref_pose = detector(
        master_bgr,
        include_body=True,
        include_hand=False,
        include_face=False,
        use_dw_pose=True,
    )
    nonzero = int(np.count_nonzero(ref_pose))
    if nonzero < 200:
        fail(
            "DWPose could not extract a usable body pose from exilada_master.png "
            f"(only {nonzero} nonzero pose pixels)."
        )
    Image.fromarray(ref_pose).save(reference_pose_path)

    # Convert the already-approved C1A skeleton coordinates directly into the
    # exact OpenPose-style body map expected by the SSD pose guider. We do NOT
    # re-detect these eight poses with AI: doing so would add avoidable detector
    # error to motion data we already own exactly.
    pose_paths: list[str] = []
    pose_records: list[dict] = []

    def kp(frame: dict, name: str) -> Keypoint:
        x, y = normalized_xy(frame["joints"][name], source_w, source_h)
        return Keypoint(x=x, y=y, score=1.0)

    def lerp_kp(a: Keypoint, b: Keypoint, t: float) -> Keypoint:
        return Keypoint(x=a.x + (b.x - a.x) * t, y=a.y + (b.y - a.y) * t, score=1.0)

    for index, frame in enumerate(frames, start=1):
        neck = kp(frame, "neck")
        head_top = kp(frame, "head")
        nose = lerp_kp(neck, head_top, 0.72)

        # OpenPose BODY_18 order:
        # nose, neck, R shoulder/elbow/wrist, L shoulder/elbow/wrist,
        # R hip/knee/ankle, L hip/knee/ankle, R eye, L eye, R ear, L ear.
        body = [
            nose,
            neck,
            kp(frame, "right_shoulder"),
            kp(frame, "right_elbow"),
            kp(frame, "right_wrist"),
            kp(frame, "left_shoulder"),
            kp(frame, "left_elbow"),
            kp(frame, "left_wrist"),
            kp(frame, "right_hip"),
            kp(frame, "right_knee"),
            kp(frame, "right_ankle"),
            kp(frame, "left_hip"),
            kp(frame, "left_knee"),
            kp(frame, "left_ankle"),
            None, None, None, None,
        ]
        human = HumanPoseResult(
            body=BodyResult(keypoints=body, total_score=14.0, total_parts=14),
            left_hand=None,
            right_hand=None,
            face=None,
        )
        canvas = draw_poses(
            [human],
            512,
            512,
            draw_body=True,
            draw_hand=False,
            draw_face=False,
        )
        pose_path = poses_dir / f"frame_{index:03d}_{frame['event']}.png"
        Image.fromarray(canvas).save(pose_path)
        pose_paths.append(str(pose_path))
        pose_records.append({
            "index": index - 1,
            "source_frame": int(frame["frame"]),
            "event": str(frame["event"]),
            "support_foot": str(frame["support_foot"]),
            "path": str(pose_path),
        })

    # The upstream inference script incorrectly assumes target pose #1 is also
    # the reference-image pose. For Exilada that is false. Generate a local,
    # deterministic copy with one narrow project patch: reference_pose_path is
    # read from config while the target list remains exactly the 8 walk states.
    upstream_inference = model_training / "inference.py"
    source = upstream_inference.read_text(encoding="utf-8")
    needle = 'ref_pose = Image.open(pose_image_paths[0]).convert("RGB")'
    if source.count(needle) != 1:
        fail("upstream inference.py reference-pose anchor changed; refusing unsafe patch")
    replacement = (
        'ref_pose_cfg = config.get("reference_pose_path", None)\n'
        '                    if ref_pose_cfg:\n'
        '                        ref_pose = Image.open(ref_pose_cfg).convert("RGB")\n'
        '                    else:\n'
        '                        ref_pose = Image.open(pose_image_paths[0]).convert("RGB")'
    )
    patched = source.replace(needle, replacement)
    patched_inference.write_text(patched, encoding="utf-8")

    config_text = "\n".join([
        "pretrained_base_model_path: './pretrained_model/stable-diffusion-v1-5'",
        "pretrained_vae_path: './pretrained_model/sd-vae-ft-mse'",
        "image_encoder_path: './pretrained_model/image_encoder'",
        "",
        'denoising_unet_path: "./pretrained_model/denoising_unet.pth"',
        'reference_unet_path: "./pretrained_model/reference_unet.pth"',
        'pose_guider_path: "./pretrained_model/pose_guider.pth"',
        'motion_module_path: "./pretrained_model/motion_module.pth"',
        "",
        'inference_config: "./configs/inference/inference_v2.yaml"',
        "weight_dtype: 'fp16'",
        "test_dir: 'data/exilada_walk8_ssd/characters'",
        "reference_pose_path: 'data/exilada_walk8_ssd/reference_pose.png'",
        "output_format: 'image'",
        "",
    ])
    config_path.write_text(config_text, encoding="utf-8")

    marker = {
        "gate": "SSD_EXILADA_WALK8_INPUT",
        "status": "PASS",
        "master": str(master_path),
        "guide": str(guide_path),
        "reference_pose": str(reference_pose_path),
        "reference_pose_method": "DWPose from exilada_master.png",
        "target_pose_method": "deterministic OpenPose-style rendering from approved C1A coordinates",
        "target_pose_count": len(pose_paths),
        "poses": pose_records,
        "config": str(config_path),
        "patched_inference": str(patched_inference),
        "resolution": [512, 512],
        "film_enabled": False,
    }
    prep_marker.write_text(json.dumps(marker, indent=2) + "\n", encoding="utf-8")

    print("SSD-WALK8-INPUT: PASS")
    print(f"REFERENCE POSE: {reference_pose_path}")
    print(f"TARGET POSES:   {len(pose_paths)} clean maps")
    print(f"CONFIG:         {config_path}")
    print(f"INFERENCE:      {patched_inference}")
    print(f"MARKER:         {prep_marker}")
    return 0


def review(args: argparse.Namespace) -> int:
    predict_dir = Path(args.predict_dir).resolve()
    review_root = Path(args.review_root).resolve()
    marker = Path(args.marker).resolve()

    frames = sorted(predict_dir.glob("frame_*.png"))
    if len(frames) != 8:
        fail(f"expected exactly 8 generated frames, got {len(frames)} in {predict_dir}")

    review_root.mkdir(parents=True, exist_ok=True)
    images = [Image.open(p).convert("RGB") for p in frames]

    # 4x2 contact sheet; no resampling so generated pixels are not altered.
    w, h = images[0].size
    sheet = Image.new("RGB", (w * 4, h * 2))
    for i, im in enumerate(images):
        sheet.paste(im, ((i % 4) * w, (i // 4) * h))
    sheet_path = review_root / "exilada_walk8_contact_sheet.png"
    sheet.save(sheet_path)

    gif_path = review_root / "exilada_walk8.gif"
    images[0].save(
        gif_path,
        save_all=True,
        append_images=images[1:],
        duration=125,
        loop=0,
        disposal=2,
        optimize=False,
    )

    out = {
        "gate": "SSD_EXILADA_WALK8_INFERENCE",
        "status": "PASS_OUTPUT_READY_FOR_VISUAL_QA",
        "predict_dir": str(predict_dir),
        "frame_count": 8,
        "frames": [str(p) for p in frames],
        "contact_sheet": str(sheet_path),
        "gif": str(gif_path),
        "visual_qa_required": True,
    }
    marker.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")

    print("SSD-WALK8: OUTPUT READY FOR VISUAL QA")
    print(f"FRAMES: {predict_dir}")
    print(f"SHEET:  {sheet_path}")
    print(f"GIF:    {gif_path}")
    print(f"MARKER: {marker}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="command", required=True)

    prep = sub.add_parser("prepare")
    prep.add_argument("--model-training", required=True)
    prep.add_argument("--guide", required=True)
    prep.add_argument("--master", required=True)
    prep.add_argument("--marker", required=True)

    rev = sub.add_parser("review")
    rev.add_argument("--predict-dir", required=True)
    rev.add_argument("--review-root", required=True)
    rev.add_argument("--marker", required=True)

    args = ap.parse_args()
    if args.command == "prepare":
        return prepare(args)
    return review(args)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"SSD-WALK8: FAIL - {exc}")
        raise SystemExit(1)
