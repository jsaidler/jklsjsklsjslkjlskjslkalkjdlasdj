#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import json
import statistics
from pathlib import Path


def fail(message: str) -> None:
    raise RuntimeError(message)


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def median(values: list[float]) -> float:
    if not values:
        fail("cannot compute median of empty list")
    return float(statistics.median(values))


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input-guide", required=True)
    ap.add_argument("--output-guide", required=True)
    ap.add_argument("--marker", required=True)
    args = ap.parse_args()

    input_path = Path(args.input_guide).resolve()
    output_path = Path(args.output_guide).resolve()
    marker_path = Path(args.marker).resolve()

    if not input_path.is_file():
        fail(f"input guide missing: {input_path}")

    source = read_json(input_path)
    if source.get("gate") != "G3S-C1A" or source.get("revision") != "SKELETON_ONLY_WALK_CYCLE_V1":
        fail("unexpected source guide; expected canonical C1A skeleton schema")
    frames = source.get("frames", [])
    if len(frames) != 8:
        fail(f"expected 8 gait frames, got {len(frames)}")

    azimuth = float(source.get("camera", {}).get("azimuth_from_motion_heading_deg", -1))
    if abs(azimuth - 72.0) > 0.01:
        fail(f"gameplay overlay requires the approved 72-degree facing baseline, got {azimuth}")

    # C1C GAMEPLAY WALK OVERLAY V1
    #
    # These are deliberately modest screen-space authoring adjustments applied
    # after the real gait has been projected into the locked 2D gameplay family.
    # We keep real phase timing/support ordering, but stop treating raw CMU
    # NormalWalk as final animation art direction.
    params = {
        "pelvis_bob_scale": 0.55,
        "leg_x_scale": {
            "hip": 0.97,
            "knee": 0.90,
            "ankle": 0.84,
            "toe": 0.84,
        },
        "torso_forward_shear_px_at_head": 4.5,
        "arm_swing_x_scale": {
            "elbow": 0.74,
            "wrist": 0.62,
        },
        "arm_swing_y_scale": {
            "elbow": 0.92,
            "wrist": 0.88,
        },
        "head_offset_stabilization": 0.50,
    }

    required_joints = [
        "pelvis", "chest", "neck", "head",
        "left_shoulder", "left_elbow", "left_wrist",
        "right_shoulder", "right_elbow", "right_wrist",
        "left_hip", "left_knee", "left_ankle", "left_toe",
        "right_hip", "right_knee", "right_ankle", "right_toe",
    ]
    for i, frame in enumerate(frames):
        missing = [name for name in required_joints if name not in frame.get("joints", {})]
        if missing:
            fail(f"frame {i} missing required joints: {missing}")

    pelvis_ys = [float(frame["joints"]["pelvis"]["y"]) for frame in frames]
    median_pelvis_y = median(pelvis_ys)

    head_offsets_x = [
        float(frame["joints"]["head"]["x"]) - float(frame["joints"]["neck"]["x"])
        for frame in frames
    ]
    head_offsets_y = [
        float(frame["joints"]["head"]["y"]) - float(frame["joints"]["neck"]["y"])
        for frame in frames
    ]
    median_head_dx = median(head_offsets_x)
    median_head_dy = median(head_offsets_y)

    out = copy.deepcopy(source)
    out["purpose"] = "C1C gameplay-authored walk overlay V1 on approved 72-degree facing; real gait timing retained"
    out["status"] = "REVIEW_REQUIRED"
    out["c1c_gameplay_overlay"] = {
        "revision": "GAMEPLAY_WALK_OVERLAY_V1",
        "source_guide": str(input_path),
        "facing_azimuth_deg": 72.0,
        "screen_left_forward": True,
        "parameters": params,
        "design_intent": [
            "compact the projected stride for belt-scroller combat readability",
            "reduce casual-walk vertical bob without flattening the gait",
            "give the upper body a mild forward intent",
            "reduce large civilian arm pendulum motion",
            "stabilize the head while preserving real gait phase timing",
        ],
        "not_changed": [
            "source CMU phase timing",
            "left/right support-foot order",
            "eight canonical gait events",
            "camera pitch/native raster/body scale",
            "depth ordering metadata",
        ],
    }

    transformed_metrics = []

    for index, frame in enumerate(out["frames"]):
        joints = frame["joints"]
        original = source["frames"][index]["joints"]

        pelvis_x = float(original["pelvis"]["x"])
        pelvis_y = float(original["pelvis"]["y"])

        # 1) Reduce global vertical bob while preserving the internal body pose.
        desired_pelvis_y = median_pelvis_y + (pelvis_y - median_pelvis_y) * params["pelvis_bob_scale"]
        bob_shift_y = desired_pelvis_y - pelvis_y
        for rec in joints.values():
            rec["y"] = float(rec["y"]) + bob_shift_y

        # 2) Compact stride in the gameplay screen axis.  Hips remain almost
        # unchanged while knees/feet are progressively compressed toward pelvis.
        for side in ("left", "right"):
            for part, scale in params["leg_x_scale"].items():
                name = f"{side}_{part}"
                ox = float(original[name]["x"])
                joints[name]["x"] = pelvis_x + (ox - pelvis_x) * float(scale)

        # 3) Mild screen-left upper-body intent.  This is a shear, not a rigid
        # body translation: pelvis stays planted, head receives the full amount.
        # Use projected vertical distance from pelvis so the effect follows body
        # proportions without hardcoding bone lengths.
        head_y_after_bob = float(joints["head"]["y"])
        pelvis_y_after_bob = float(joints["pelvis"]["y"])
        torso_height = max(1.0, pelvis_y_after_bob - head_y_after_bob)
        torso_names = [
            "chest", "neck", "head",
            "left_shoulder", "right_shoulder",
            "left_elbow", "right_elbow",
            "left_wrist", "right_wrist",
        ]
        for name in torso_names:
            y = float(joints[name]["y"])
            fraction_up = max(0.0, min(1.0, (pelvis_y_after_bob - y) / torso_height))
            joints[name]["x"] = float(joints[name]["x"]) - params["torso_forward_shear_px_at_head"] * fraction_up

        # 4) Reduce arm pendulum amplitude around each shoulder.  This retains
        # the CMU timing but moves the silhouette toward a combat-ready walk.
        for side in ("left", "right"):
            shoulder = joints[f"{side}_shoulder"]
            sx, sy = float(shoulder["x"]), float(shoulder["y"])
            for part in ("elbow", "wrist"):
                name = f"{side}_{part}"
                x = float(joints[name]["x"])
                y = float(joints[name]["y"])
                joints[name]["x"] = sx + (x - sx) * params["arm_swing_x_scale"][part]
                joints[name]["y"] = sy + (y - sy) * params["arm_swing_y_scale"][part]

        # 5) Stabilize head orientation relative to neck by blending the current
        # projected head offset toward the median cycle offset.
        neck_x, neck_y = float(joints["neck"]["x"]), float(joints["neck"]["y"])
        current_dx = float(joints["head"]["x"]) - neck_x
        current_dy = float(joints["head"]["y"]) - neck_y
        t = params["head_offset_stabilization"]
        joints["head"]["x"] = neck_x + lerp(current_dx, median_head_dx, t)
        joints["head"]["y"] = neck_y + lerp(current_dy, median_head_dy, t)

        # Preserve structural metadata but update optional chain screen metrics
        # when present so downstream diagnostics do not retain stale 2D values.
        for chain in frame.get("chains", []):
            a = joints[chain["a"]]
            b = joints[chain["b"]]
            dx = float(b["x"]) - float(a["x"])
            dy = float(b["y"]) - float(a["y"])
            if "screen_dx" in chain:
                chain["screen_dx"] = dx
            if "screen_dy" in chain:
                chain["screen_dy"] = dy
            if "screen_length_px" in chain:
                chain["screen_length_px"] = (dx * dx + dy * dy) ** 0.5

        transformed_metrics.append({
            "index": index,
            "event": str(frame["event"]),
            "support_foot": str(frame["support_foot"]),
            "original_pelvis_y": pelvis_y,
            "authored_pelvis_y": float(joints["pelvis"]["y"]),
            "bob_shift_y": bob_shift_y,
            "left_ankle_x_delta": float(joints["left_ankle"]["x"]) - float(original["left_ankle"]["x"]),
            "right_ankle_x_delta": float(joints["right_ankle"]["x"]) - float(original["right_ankle"]["x"]),
        })

    # Hard invariants: gait semantics and projection family must remain intact.
    expected_events = [
        "left_contact", "left_down", "left_passing", "left_up",
        "right_contact", "right_down", "right_passing", "right_up",
    ]
    if [str(f["event"]) for f in out["frames"]] != expected_events:
        fail("overlay altered canonical gait event order")
    if [str(f["support_foot"]) for f in out["frames"]] != [
        "left", "left", "left", "left", "right", "right", "right", "right"
    ]:
        fail("overlay altered canonical support-foot order")
    if float(out.get("root_travel_total_dx_px", 0.0)) >= 0:
        fail("source guide no longer projects forward travel screen-left")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    marker_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")

    marker = {
        "gate": "G3S-C1C_GAMEPLAY_WALK_OVERLAY",
        "status": "PASS_OUTPUT_READY_FOR_SKELETON_VISUAL_QA",
        "revision": "GAMEPLAY_WALK_OVERLAY_V1",
        "source_guide": str(input_path),
        "output_guide": str(output_path),
        "facing_azimuth_deg": 72.0,
        "parameters": params,
        "transformed_metrics": transformed_metrics,
        "visual_qa_required": True,
    }
    marker_path.write_text(json.dumps(marker, indent=2) + "\n", encoding="utf-8")

    print("G3S-C1C-OVERLAY: PASS_OUTPUT_READY_FOR_SKELETON_VISUAL_QA")
    print(f"SOURCE: {input_path}")
    print(f"GUIDE:  {output_path}")
    print(f"MARKER: {marker_path}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"G3S-C1C-OVERLAY: FAIL - {exc}")
        raise SystemExit(1)
