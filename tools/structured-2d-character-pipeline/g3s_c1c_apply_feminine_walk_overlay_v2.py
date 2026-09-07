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


def update_chain_metrics(frame: dict) -> None:
    joints = frame["joints"]
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


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input-guide", required=True)
    ap.add_argument("--spec", required=True)
    ap.add_argument("--output-guide", required=True)
    ap.add_argument("--marker", required=True)
    args = ap.parse_args()

    input_path = Path(args.input_guide).resolve()
    spec_path = Path(args.spec).resolve()
    output_path = Path(args.output_guide).resolve()
    marker_path = Path(args.marker).resolve()

    if not input_path.is_file():
        fail(f"input guide missing: {input_path}")
    if not spec_path.is_file():
        fail(f"overlay spec missing: {spec_path}")

    spec = read_json(spec_path)
    if spec.get("gate") != "G3S-C1C_GAMEPLAY_WALK_OVERLAY" or spec.get("revision") != "GAMEPLAY_WALK_OVERLAY_V2_FEMININE":
        fail("unexpected overlay spec")
    if spec.get("status") != "RUNNER_READY_REVIEW_REQUIRED":
        fail("overlay spec is not runner-ready")
    if abs(float(spec.get("facing_azimuth_deg", -1)) - 72.0) > 0.01:
        fail("overlay spec facing is not the approved 72-degree baseline")

    source = read_json(input_path)
    if source.get("gate") != "G3S-C1A" or source.get("revision") != "SKELETON_ONLY_WALK_CYCLE_V1":
        fail("unexpected source guide; expected canonical C1A skeleton schema")
    frames = source.get("frames", [])
    if len(frames) != 8:
        fail(f"expected 8 gait frames, got {len(frames)}")

    azimuth = float(source.get("camera", {}).get("azimuth_from_motion_heading_deg", -1))
    if abs(azimuth - 72.0) > 0.01:
        fail(f"feminine gameplay overlay requires the approved 72-degree facing baseline, got {azimuth}")

    expected_events = [
        "left_contact", "left_down", "left_passing", "left_up",
        "right_contact", "right_down", "right_passing", "right_up",
    ]
    if [str(f.get("event")) for f in frames] != expected_events:
        fail("source guide does not contain the canonical eight gait events")
    expected_support = ["left", "left", "left", "left", "right", "right", "right", "right"]
    if [str(f.get("support_foot")) for f in frames] != expected_support:
        fail("source guide support-foot order changed")

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

    params = spec.get("parameters")
    if not isinstance(params, dict):
        fail("overlay spec parameters missing")
    required_param_keys = [
        "pelvis_bob_scale", "stride_x_scale", "phase_weight",
        "pelvic_obliquity_total_px", "pelvic_yaw_split_px",
        "torso_counterlean_total_px", "shoulder_counteryaw_split_px",
        "torso_forward_shear_px_at_head", "arm_swing_x_scale",
        "arm_swing_y_scale", "swing_leg_lift_px",
        "head_offset_stabilization",
    ]
    missing_params = [key for key in required_param_keys if key not in params]
    if missing_params:
        fail(f"overlay spec missing parameters: {missing_params}")

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
    out["purpose"] = (
        "C1C gameplay walk overlay V2: subtle feminine locomotion art direction "
        "on approved 72-degree facing; real gait timing/support retained"
    )
    out["status"] = "REVIEW_REQUIRED"
    out["c1c_gameplay_overlay"] = {
        "revision": "GAMEPLAY_WALK_OVERLAY_V2_FEMININE",
        "source_guide": str(input_path),
        "facing_azimuth_deg": 72.0,
        "screen_left_forward": True,
        "parameters": params,
        "design_intent": spec.get("design_intent", []),
        "guardrails": spec.get("guardrails", []),
    }

    transformed_metrics: list[dict] = []

    for index, frame in enumerate(out["frames"]):
        joints = frame["joints"]
        original = source["frames"][index]["joints"]
        event = str(frame["event"])
        support = str(frame["support_foot"])
        swing = "right" if support == "left" else "left"
        phase = event.split("_", 1)[1]
        if phase not in params["phase_weight"]:
            fail(f"unknown gait phase in event: {event}")
        phase_weight = float(params["phase_weight"][phase])

        pelvis_x = float(original["pelvis"]["x"])
        pelvis_y = float(original["pelvis"]["y"])

        desired_pelvis_y = median_pelvis_y + (pelvis_y - median_pelvis_y) * params["pelvis_bob_scale"]
        bob_shift_y = desired_pelvis_y - pelvis_y
        for rec in joints.values():
            rec["y"] = float(rec["y"]) + bob_shift_y

        for side in ("left", "right"):
            for part, scale in params["stride_x_scale"].items():
                name = f"{side}_{part}"
                ox = float(original[name]["x"])
                joints[name]["x"] = pelvis_x + (ox - pelvis_x) * float(scale)

        oblique = float(params["pelvic_obliquity_total_px"]) * phase_weight
        support_hip = joints[f"{support}_hip"]
        swing_hip = joints[f"{swing}_hip"]
        support_hip["y"] = float(support_hip["y"]) - oblique * 0.5
        swing_hip["y"] = float(swing_hip["y"]) + oblique * 0.5

        for side in (support, swing):
            hip = joints[f"{side}_hip"]
            hip_orig_y_after_bob = float(original[f"{side}_hip"]["y"]) + bob_shift_y
            dy = float(hip["y"]) - hip_orig_y_after_bob
            for part, weight in (("knee", 0.58), ("ankle", 0.18), ("toe", 0.12)):
                joints[f"{side}_{part}"]["y"] = float(joints[f"{side}_{part}"]["y"]) + dy * weight

        yaw_split = float(params["pelvic_yaw_split_px"]) * phase_weight
        joints[f"{swing}_hip"]["x"] = float(joints[f"{swing}_hip"]["x"]) - yaw_split * 0.5
        joints[f"{support}_hip"]["x"] = float(joints[f"{support}_hip"]["x"]) + yaw_split * 0.5
        for side in (support, swing):
            dx = (
                float(joints[f"{side}_hip"]["x"])
                - (pelvis_x + (float(original[f"{side}_hip"]["x"]) - pelvis_x) * params["stride_x_scale"]["hip"])
            )
            for part, weight in (("knee", 0.52), ("ankle", 0.16), ("toe", 0.10)):
                joints[f"{side}_{part}"]["x"] = float(joints[f"{side}_{part}"]["x"]) + dx * weight

        shoulder_oblique = float(params["torso_counterlean_total_px"]) * phase_weight
        shoulder_yaw = float(params["shoulder_counteryaw_split_px"]) * phase_weight
        for side in (support, swing):
            sh = joints[f"{side}_shoulder"]
            old_x, old_y = float(sh["x"]), float(sh["y"])
            if side == support:
                sh["y"] = old_y + shoulder_oblique * 0.5
                sh["x"] = old_x - shoulder_yaw * 0.5
            else:
                sh["y"] = old_y - shoulder_oblique * 0.5
                sh["x"] = old_x + shoulder_yaw * 0.5
            dx_sh = float(sh["x"]) - old_x
            dy_sh = float(sh["y"]) - old_y
            for part in ("elbow", "wrist"):
                rec = joints[f"{side}_{part}"]
                rec["x"] = float(rec["x"]) + dx_sh
                rec["y"] = float(rec["y"]) + dy_sh

        head_y = float(joints["head"]["y"])
        pelvis_y_after_bob = float(joints["pelvis"]["y"])
        torso_height = max(1.0, pelvis_y_after_bob - head_y)
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

        for side in ("left", "right"):
            shoulder = joints[f"{side}_shoulder"]
            sx, sy = float(shoulder["x"]), float(shoulder["y"])
            for part in ("elbow", "wrist"):
                name = f"{side}_{part}"
                x = float(joints[name]["x"])
                y = float(joints[name]["y"])
                joints[name]["x"] = sx + (x - sx) * params["arm_swing_x_scale"][part]
                joints[name]["y"] = sy + (y - sy) * params["arm_swing_y_scale"][part]

        lift = params["swing_leg_lift_px"][phase]
        for part in ("knee", "ankle", "toe"):
            joints[f"{swing}_{part}"]["y"] = float(joints[f"{swing}_{part}"]["y"]) - float(lift[part])

        neck_x, neck_y = float(joints["neck"]["x"]), float(joints["neck"]["y"])
        current_dx = float(joints["head"]["x"]) - neck_x
        current_dy = float(joints["head"]["y"]) - neck_y
        t = float(params["head_offset_stabilization"])
        joints["head"]["x"] = neck_x + lerp(current_dx, median_head_dx, t)
        joints["head"]["y"] = neck_y + lerp(current_dy, median_head_dy, t)

        update_chain_metrics(frame)

        transformed_metrics.append({
            "index": index,
            "event": event,
            "support_foot": support,
            "swing_foot": swing,
            "phase_weight": phase_weight,
            "bob_shift_y": bob_shift_y,
            "pelvic_obliquity_total_px": oblique,
            "pelvic_yaw_split_px": yaw_split,
            "support_hip_y": float(joints[f"{support}_hip"]["y"]),
            "swing_hip_y": float(joints[f"{swing}_hip"]["y"]),
        })

    if [str(f["event"]) for f in out["frames"]] != expected_events:
        fail("V2 altered canonical gait event order")
    if [str(f["support_foot"]) for f in out["frames"]] != expected_support:
        fail("V2 altered canonical support-foot order")
    if float(out.get("root_travel_total_dx_px", 0.0)) >= 0:
        fail("source guide no longer projects forward travel screen-left")

    hip_diffs = [
        abs(float(f["joints"]["left_hip"]["y"]) - float(f["joints"]["right_hip"]["y"]))
        for f in out["frames"]
    ]
    if max(hip_diffs) > 8.0:
        fail(f"V2 pelvic obliquity exceeded safety limit: {max(hip_diffs):.2f}px")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    marker_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")

    marker = {
        "gate": "G3S-C1C_GAMEPLAY_WALK_OVERLAY",
        "status": "PASS_OUTPUT_READY_FOR_SKELETON_VISUAL_QA",
        "revision": "GAMEPLAY_WALK_OVERLAY_V2_FEMININE",
        "source_guide": str(input_path),
        "spec": str(spec_path),
        "output_guide": str(output_path),
        "facing_azimuth_deg": 72.0,
        "parameters": params,
        "max_projected_hip_y_difference_px": max(hip_diffs),
        "transformed_metrics": transformed_metrics,
        "visual_qa_required": True,
    }
    marker_path.write_text(json.dumps(marker, indent=2) + "\n", encoding="utf-8")

    print("G3S-C1C-FEMININE-V2: PASS_OUTPUT_READY_FOR_SKELETON_VISUAL_QA")
    print(f"SOURCE: {input_path}")
    print(f"GUIDE:  {output_path}")
    print(f"MARKER: {marker_path}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"G3S-C1C-FEMININE-V2: FAIL - {exc}")
        raise SystemExit(1)
