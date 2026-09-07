#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image


def fail(message: str) -> None:
    raise RuntimeError(message)


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def image_bbox(path: Path) -> tuple[int, int, int, int]:
    arr = np.array(Image.open(path).convert("RGB"))
    mask = np.any(arr != 0, axis=2)
    ys, xs = np.where(mask)
    if len(xs) == 0 or len(ys) == 0:
        fail(f"pose image has no nonzero pixels: {path}")
    return int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())


def bbox_wh(bbox: tuple[int, int, int, int]) -> tuple[int, int]:
    x0, y0, x1, y1 = bbox
    return x1 - x0 + 1, y1 - y0 + 1


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    if len(sys.argv) != 2:
        fail("usage: g3s_ssd_align_walk8_poses.py <request.json>")

    req_path = Path(sys.argv[1]).resolve()
    req = read_json(req_path)

    model_training = Path(req["model_training"]).resolve()
    input_marker = Path(req["input_marker"]).resolve()
    output_root = Path(req["output_root"]).resolve()
    output_marker = Path(req["output_marker"]).resolve()

    if not model_training.is_dir():
        fail(f"ModelTraining directory missing: {model_training}")
    if not input_marker.is_file():
        fail(f"baseline walk8 marker missing: {input_marker}")

    prepared = read_json(input_marker)
    if prepared.get("status") != "PASS":
        fail("baseline walk8 input marker is not PASS")
    if int(prepared.get("target_pose_count", 0)) != 8:
        fail("baseline walk8 input marker does not contain exactly 8 target poses")

    master = Path(prepared["master"]).resolve()
    guide_path = Path(prepared["guide"]).resolve()
    reference_pose = Path(prepared["reference_pose"]).resolve()
    baseline_pose_paths = [Path(row["path"]).resolve() for row in prepared["poses"]]

    for required in (master, guide_path, reference_pose, *baseline_pose_paths):
        if not required.is_file():
            fail(f"required aligned-pose input missing: {required}")

    guide = read_json(guide_path)
    frames = guide.get("frames", [])
    if guide.get("gate") != "G3S-C1A" or len(frames) != 8:
        fail("approved C1A guide is not the expected eight-frame gate")

    expected_events = [
        "left_contact", "left_down", "left_passing", "left_up",
        "right_contact", "right_down", "right_passing", "right_up",
    ]
    actual_events = [str(f.get("event")) for f in frames]
    if actual_events != expected_events:
        fail(f"C1A event order mismatch: {actual_events}")

    # The original C1A guide is in the locked 640x360 gameplay projection.
    # Runner 29's preparation normalized X by 640 and Y by 360, then rendered
    # both into 512x512. That creates an anisotropic transform:
    # X scale = 512/640 = 0.8; Y scale = 512/360 = 1.4222..., so vertical
    # geometry is stretched 1.7777... relative to horizontal geometry.
    # This experiment removes that distortion and spatially registers the
    # target skeleton to the DWPose body footprint extracted from the master.
    source_w, source_h = 640.0, 360.0
    canvas = 512
    margin = 20.0

    ref_bbox = image_bbox(reference_pose)
    ref_w, ref_h = bbox_wh(ref_bbox)
    ref_x0, ref_y0, ref_x1, ref_y1 = ref_bbox
    ref_center_x = (ref_x0 + ref_x1) / 2.0
    ref_bottom_y = float(ref_y1)

    baseline_bboxes = [image_bbox(p) for p in baseline_pose_paths]
    baseline_heights = [bbox_wh(b)[1] for b in baseline_bboxes]
    baseline_widths = [bbox_wh(b)[0] for b in baseline_bboxes]

    names = [
        "right_shoulder", "right_elbow", "right_wrist",
        "left_shoulder", "left_elbow", "left_wrist",
        "right_hip", "right_knee", "right_ankle",
        "left_hip", "left_knee", "left_ankle",
    ]

    def xy(frame: dict, name: str) -> tuple[float, float]:
        rec = frame["joints"][name]
        return float(rec["x"]), float(rec["y"])

    def body_xy(frame: dict) -> list[tuple[float, float] | None]:
        neck = xy(frame, "neck")
        head = xy(frame, "head")
        nose = (
            neck[0] + (head[0] - neck[0]) * 0.72,
            neck[1] + (head[1] - neck[1]) * 0.72,
        )
        pts = {name: xy(frame, name) for name in names}
        return [
            nose,
            neck,
            pts["right_shoulder"], pts["right_elbow"], pts["right_wrist"],
            pts["left_shoulder"], pts["left_elbow"], pts["left_wrist"],
            pts["right_hip"], pts["right_knee"], pts["right_ankle"],
            pts["left_hip"], pts["left_knee"], pts["left_ankle"],
            None, None, None, None,
        ]

    raw_bodies = [body_xy(frame) for frame in frames]
    raw_heights: list[float] = []
    max_left = max_right = max_up = 0.0
    frame_anchors: list[tuple[float, float]] = []

    for frame, body in zip(frames, raw_bodies):
        points = [p for p in body if p is not None]
        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        raw_heights.append(max(ys) - min(ys))

        rh = xy(frame, "right_hip")
        lh = xy(frame, "left_hip")
        pelvis_x = (rh[0] + lh[0]) / 2.0
        ra = xy(frame, "right_ankle")
        la = xy(frame, "left_ankle")
        ankle_y = max(ra[1], la[1])
        frame_anchors.append((pelvis_x, ankle_y))

        max_left = max(max_left, pelvis_x - min(xs))
        max_right = max(max_right, max(xs) - pelvis_x)
        max_up = max(max_up, ankle_y - min(ys))

    median_raw_height = float(np.median(np.array(raw_heights, dtype=np.float64)))
    if median_raw_height <= 1.0:
        fail("C1A raw body height is invalid")

    desired_scale = float(ref_h) / median_raw_height

    scale_limits = [desired_scale]
    if max_left > 0:
        scale_limits.append((ref_center_x - margin) / max_left)
    if max_right > 0:
        scale_limits.append((canvas - 1.0 - margin - ref_center_x) / max_right)
    if max_up > 0:
        scale_limits.append((ref_bottom_y - margin) / max_up)
    scale = min(scale_limits)
    if scale <= 0:
        fail("computed aligned-pose scale is not positive")
    if scale < desired_scale * 0.80:
        fail(
            "master-reference registration would require shrinking C1A below 80% "
            f"of the desired body scale ({scale:.4f} vs {desired_scale:.4f})"
        )

    # Import the exact pose renderer already used by the SSD preparation.
    sys.path.insert(0, str(model_training))
    from openpose import draw_poses  # noqa: E402
    from openpose.types import BodyResult, HumanPoseResult, Keypoint  # noqa: E402

    poses_dir = output_root / "poses"
    poses_dir.mkdir(parents=True, exist_ok=True)

    pose_records: list[dict] = []
    aligned_paths: list[Path] = []
    transformed_metrics: list[dict] = []

    for index, (frame, body, anchor) in enumerate(zip(frames, raw_bodies, frame_anchors), start=1):
        pelvis_x, ankle_y = anchor
        transformed: list[Keypoint | None] = []
        mapped_xy: list[tuple[float, float]] = []

        for p in body:
            if p is None:
                transformed.append(None)
                continue
            tx = ref_center_x + (p[0] - pelvis_x) * scale
            ty = ref_bottom_y + (p[1] - ankle_y) * scale
            if tx < margin or tx > (canvas - 1 - margin) or ty < margin or ty > (canvas - 1 - margin):
                fail(
                    f"aligned C1A joint leaves safe canvas in frame {index}: "
                    f"({tx:.2f}, {ty:.2f})"
                )
            mapped_xy.append((tx, ty))
            transformed.append(Keypoint(x=tx / canvas, y=ty / canvas, score=1.0))

        human = HumanPoseResult(
            body=BodyResult(keypoints=transformed, total_score=14.0, total_parts=14),
            left_hand=None,
            right_hand=None,
            face=None,
        )
        rendered = draw_poses(
            [human],
            canvas,
            canvas,
            draw_body=True,
            draw_hand=False,
            draw_face=False,
        )
        pose_path = poses_dir / f"frame_{index:03d}_{frame['event']}.png"
        Image.fromarray(rendered).save(pose_path)
        aligned_paths.append(pose_path)

        xs = [p[0] for p in mapped_xy]
        ys = [p[1] for p in mapped_xy]
        transformed_metrics.append({
            "index": index - 1,
            "event": str(frame["event"]),
            "mapped_joint_bbox": [min(xs), min(ys), max(xs), max(ys)],
            "mapped_joint_height": max(ys) - min(ys),
        })
        pose_records.append({
            "index": index - 1,
            "source_frame": int(frame["frame"]),
            "event": str(frame["event"]),
            "support_foot": str(frame["support_foot"]),
            "path": str(pose_path),
        })

    aligned_bboxes = [image_bbox(p) for p in aligned_paths]
    aligned_heights = [bbox_wh(b)[1] for b in aligned_bboxes]
    aligned_widths = [bbox_wh(b)[0] for b in aligned_bboxes]
    aligned_median_height = float(np.median(np.array(aligned_heights, dtype=np.float64)))
    ref_ratio = aligned_median_height / float(ref_h)
    if not 0.85 <= ref_ratio <= 1.15:
        fail(
            "aligned target pose median height is not registered to the master reference: "
            f"ratio={ref_ratio:.4f}"
        )

    hashes = [sha256(p) for p in aligned_paths]
    if len(set(hashes)) != 8:
        fail("aligned target pose maps are not eight unique images")

    # 3x3 diagnostic: reference pose followed by the eight aligned targets.
    review_path = output_root / "exilada_walk8_pose_alignment_review.png"
    review = Image.new("RGB", (canvas * 3, canvas * 3))
    review.paste(Image.open(reference_pose).convert("RGB"), (0, 0))
    for i, path in enumerate(aligned_paths, start=1):
        review.paste(Image.open(path).convert("RGB"), ((i % 3) * canvas, (i // 3) * canvas))
    review.save(review_path)

    result = {
        "gate": "SSD_EXILADA_WALK8_POSE_ALIGNMENT",
        "status": "PASS",
        "experiment": "RUNNER_30_POSE_SCALE_REGISTRATION_DISCRIMINANT",
        "master": str(master),
        "guide": str(guide_path),
        "reference_pose": str(reference_pose),
        "reference_pose_bbox": list(ref_bbox),
        "reference_pose_bbox_wh": [ref_w, ref_h],
        "source_projection": [int(source_w), int(source_h)],
        "target_canvas": [canvas, canvas],
        "runner29_original_xy_scales": [canvas / source_w, canvas / source_h],
        "runner29_original_vertical_relative_stretch": (canvas / source_h) / (canvas / source_w),
        "baseline_pose_median_bbox_wh": [
            float(np.median(np.array(baseline_widths, dtype=np.float64))),
            float(np.median(np.array(baseline_heights, dtype=np.float64))),
        ],
        "aligned_uniform_scale": scale,
        "desired_reference_scale": desired_scale,
        "alignment_method": "uniform C1A geometry scale; pelvis-X registered to reference body center; lowest ankle-Y registered to reference body bottom; per-frame root travel removed for in-place sprite authoring",
        "aligned_pose_median_bbox_wh": [
            float(np.median(np.array(aligned_widths, dtype=np.float64))),
            aligned_median_height,
        ],
        "aligned_to_reference_height_ratio": ref_ratio,
        "target_pose_count": 8,
        "poses": pose_records,
        "transformed_metrics": transformed_metrics,
        "review": str(review_path),
        "visual_qa_required": True,
    }
    output_marker.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    print("SSD-WALK8-POSE-ALIGN: PASS")
    print(f"REFERENCE BBOX: {ref_bbox} ({ref_w}x{ref_h})")
    print(
        "RUNNER29 XY SCALE: "
        f"{canvas/source_w:.4f} x {canvas/source_h:.4f}; "
        f"relative vertical stretch {(canvas/source_h)/(canvas/source_w):.4f}x"
    )
    print(f"ALIGNED UNIFORM SCALE: {scale:.4f}")
    print(f"ALIGNED/REFERENCE HEIGHT: {ref_ratio:.4f}")
    print(f"POSES:  {poses_dir}")
    print(f"REVIEW: {review_path}")
    print(f"MARKER: {output_marker}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"SSD-WALK8-POSE-ALIGN: FAIL - {exc}")
        raise SystemExit(1)
