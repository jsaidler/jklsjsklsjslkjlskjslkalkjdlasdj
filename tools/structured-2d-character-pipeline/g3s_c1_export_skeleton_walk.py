import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view


def args_after_double_dash():
    if "--" not in sys.argv:
        return []
    return sys.argv[sys.argv.index("--") + 1:]


def arg(name, default=None):
    a = args_after_double_dash()
    for i, value in enumerate(a):
        if value == name and i + 1 < len(a):
            return a[i + 1]
    return default


def bone_world_point(rig, bone_name, which="head"):
    pb = rig.pose.bones.get(bone_name)
    if pb is None:
        raise RuntimeError(f"missing required bone: {bone_name}")
    p = pb.head if which == "head" else pb.tail
    return rig.matrix_world @ p


def bone_world_matrix(rig, bone_name):
    pb = rig.pose.bones.get(bone_name)
    if pb is None:
        raise RuntimeError(f"missing required bone: {bone_name}")
    m = rig.matrix_world @ pb.matrix
    return [[float(m[r][c]) for c in range(4)] for r in range(4)]


def look_at(camera, target):
    camera.rotation_euler = (Vector(target) - camera.location).to_track_quat("-Z", "Y").to_euler()


def configure_camera(camera, target, heading, pitch_deg, side_sign, azimuth_deg):
    lateral = Vector((-heading.y, heading.x, 0.0))
    if lateral.length <= 1e-8:
        lateral = Vector((0.0, 1.0, 0.0))
    lateral.normalize()
    az = math.radians(azimuth_deg)
    horizontal = heading * math.cos(az) + lateral * (float(side_sign) * math.sin(az))
    horizontal.normalize()
    pitch = math.radians(pitch_deg)
    distance = 12.0
    camera.location = Vector(target) + horizontal * (distance * math.cos(pitch)) + Vector((0.0, 0.0, distance * math.sin(pitch)))
    look_at(camera, target)
    # Blender 5.1 can otherwise expose the previous evaluated camera transform to
    # world_to_camera_view inside the same headless Python evaluation step.
    bpy.context.view_layer.update()
    return horizontal


def normalize_screen_x(raw_x, width, screen_x_multiplier):
    if screen_x_multiplier < 0.0:
        return float(width) - float(raw_x)
    return float(raw_x)


def projected_screen_x(scene, camera, world, screen_x_multiplier=1.0):
    co = world_to_camera_view(scene, camera, world)
    raw_x = float(co.x * scene.render.resolution_x)
    return normalize_screen_x(raw_x, scene.render.resolution_x, screen_x_multiplier)


def screen_record(scene, camera, world, screen_x_multiplier=1.0):
    co = world_to_camera_view(scene, camera, world)
    local = camera.matrix_world.inverted() @ world
    raw_x = float(co.x * scene.render.resolution_x)
    return {
        "x": normalize_screen_x(raw_x, scene.render.resolution_x, screen_x_multiplier),
        "y": float((1.0 - co.y) * scene.render.resolution_y),
        "depth": float(-local.z),
        "world": [float(world.x), float(world.y), float(world.z)],
    }


def flat_xy(v):
    return Vector((v.x, v.y, 0.0))


def main():
    spec_path = Path(arg("--spec", "")).resolve()
    manifest_path = Path(arg("--manifest", "")).resolve()
    output_path = Path(arg("--output", "")).resolve()
    if not spec_path.is_file():
        raise RuntimeError(f"C1 skeleton spec missing: {spec_path}")
    if not manifest_path.is_file():
        raise RuntimeError(f"G2 manifest missing: {manifest_path}")

    spec = json.loads(spec_path.read_text(encoding="utf-8-sig"))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    if spec.get("gate") != "G3S-C1A" or spec.get("revision") != "SKELETON_ONLY_WALK_CYCLE_V1":
        raise RuntimeError("unexpected C1 skeleton spec")
    if manifest.get("gate") != "G2":
        raise RuntimeError("unexpected G2 manifest")

    cycle = spec.get("cycle", [])
    if len(cycle) != 8:
        raise RuntimeError(f"expected 8 walk states, got {len(cycle)}")
    frames = [int(row["frame"]) for row in cycle]
    clip = manifest.get("selected_clip", {})
    clip_start = int(clip.get("start_frame", -1))
    clip_end = int(clip.get("end_frame", -1))
    outside = [f for f in frames if f < clip_start or f > clip_end]
    if outside:
        raise RuntimeError(f"C1 cycle frames outside retained G2 clip {clip_start}:{clip_end}: {outside}")

    scene = bpy.context.scene
    rig = bpy.data.objects.get("G2_CANONICAL_RIG")
    if rig is None or rig.type != "ARMATURE":
        raise RuntimeError("G2_CANONICAL_RIG missing from loaded G2 blend")

    joint_defs = {
        "pelvis": ("Hips", "head", "center"),
        "chest": ("Spine1", "head", "center"),
        "neck": ("Neck1", "head", "center"),
        "head": ("Head", "tail", "center"),
        "left_shoulder": ("LeftArm", "head", "left"),
        "left_elbow": ("LeftForeArm", "head", "left"),
        "left_wrist": ("LeftHand", "head", "left"),
        "right_shoulder": ("RightArm", "head", "right"),
        "right_elbow": ("RightForeArm", "head", "right"),
        "right_wrist": ("RightHand", "head", "right"),
        "left_hip": ("LeftUpLeg", "head", "left"),
        "left_knee": ("LeftLeg", "head", "left"),
        "left_ankle": ("LeftFoot", "head", "left"),
        "left_toe": ("LeftToeBase", "head", "left"),
        "right_hip": ("RightUpLeg", "head", "right"),
        "right_knee": ("RightLeg", "head", "right"),
        "right_ankle": ("RightFoot", "head", "right"),
        "right_toe": ("RightToeBase", "head", "right"),
    }
    required_bones = sorted({v[0] for v in joint_defs.values()})
    missing = [name for name in required_bones if rig.pose.bones.get(name) is None]
    if missing:
        raise RuntimeError("G2 rig missing C1 bones: " + ", ".join(missing))

    chains = [
        ("head_neck", "head", "neck", "center"),
        ("neck_chest", "neck", "chest", "center"),
        ("chest_pelvis", "chest", "pelvis", "center"),
        ("left_clavicle", "neck", "left_shoulder", "left"),
        ("left_upper_arm", "left_shoulder", "left_elbow", "left"),
        ("left_forearm", "left_elbow", "left_wrist", "left"),
        ("right_clavicle", "neck", "right_shoulder", "right"),
        ("right_upper_arm", "right_shoulder", "right_elbow", "right"),
        ("right_forearm", "right_elbow", "right_wrist", "right"),
        ("left_pelvis", "pelvis", "left_hip", "left"),
        ("left_thigh", "left_hip", "left_knee", "left"),
        ("left_shin", "left_knee", "left_ankle", "left"),
        ("left_foot", "left_ankle", "left_toe", "left"),
        ("right_pelvis", "pelvis", "right_hip", "right"),
        ("right_thigh", "right_hip", "right_knee", "right"),
        ("right_shin", "right_knee", "right_ankle", "right"),
        ("right_foot", "right_ankle", "right_toe", "right"),
    ]

    scene.render.resolution_x = int(spec["camera"]["native_raster"][0])
    scene.render.resolution_y = int(spec["camera"]["native_raster"][1])
    scene.render.resolution_percentage = 100

    raw = []
    for row in cycle:
        f = int(row["frame"])
        scene.frame_set(f)
        bpy.context.view_layer.update()
        joints = {}
        for key, (bone, which, side) in joint_defs.items():
            p = bone_world_point(rig, bone, which)
            joints[key] = {"world": p.copy(), "side": side, "bone": bone}
        raw.append({"frame": f, "event": row["event"], "support_foot": row["support_foot"], "joints": joints})

    root_first = raw[0]["joints"]["pelvis"]["world"]
    root_last = raw[-1]["joints"]["pelvis"]["world"]
    heading = flat_xy(root_last - root_first)
    if heading.length <= 1e-8:
        raise RuntimeError("C1 retained G2 cycle has zero root travel")
    heading.normalize()

    centers_z = []
    for rec in raw:
        top = rec["joints"]["head"]["world"].z
        foot = min(
            rec["joints"]["left_ankle"]["world"].z,
            rec["joints"]["left_toe"]["world"].z,
            rec["joints"]["right_ankle"]["world"].z,
            rec["joints"]["right_toe"]["world"].z,
        )
        centers_z.append((top + foot) * 0.5)
    baseline_center_z = sorted(centers_z)[len(centers_z) // 2]

    old = bpy.data.objects.get("G3S_C1_SKELETON_CAMERA")
    if old is not None:
        bpy.data.objects.remove(old, do_unlink=True)
    bpy.ops.object.camera_add()
    camera = bpy.context.object
    camera.name = "G3S_C1_SKELETON_CAMERA"
    camera.data.type = "ORTHO"
    camera.data.clip_start = 0.01
    camera.data.clip_end = 1000.0
    scene.camera = camera

    pitch = float(spec["camera"]["pitch_deg"])
    azimuth = float(spec["camera"]["azimuth_from_motion_heading_deg"])
    target0 = Vector((root_first.x, root_first.y, baseline_center_z))

    # Evaluate both front-three-quarter lateral sides after forcing a depsgraph
    # update. Prefer a camera whose raw Blender projection already sends forward
    # travel screen-left. If Blender's camera basis still reports the opposite
    # screen handedness, keep the physical camera and normalize only the guide's
    # screen-X coordinate system. This does not transform the rig or alter depth.
    camera_candidates = []
    for side_sign in (1, -1):
        camera.data.ortho_scale = 5.0
        horizontal = configure_camera(camera, target0, heading, pitch, side_sign, azimuth)
        a = world_to_camera_view(scene, camera, target0)
        b = world_to_camera_view(scene, camera, target0 + heading)
        dx = float((b.x - a.x) * scene.render.resolution_x)
        camera_candidates.append({
            "side_sign": int(side_sign),
            "horizontal": horizontal.copy(),
            "raw_heading_dx_px_at_ortho_5": dx,
        })
        print(f"C1_CAMERA_CANDIDATE side={side_sign:+d} raw_heading_dx_px={dx:.6f}")

    negative = [c for c in camera_candidates if c["raw_heading_dx_px_at_ortho_5"] < -1e-6]
    if negative:
        chosen = max(negative, key=lambda c: abs(c["raw_heading_dx_px_at_ortho_5"]))
        screen_x_multiplier = 1.0
    else:
        chosen = max(camera_candidates, key=lambda c: abs(c["raw_heading_dx_px_at_ortho_5"]))
        if abs(chosen["raw_heading_dx_px_at_ortho_5"]) <= 1e-6:
            raise RuntimeError(
                "front-three-quarter camera projects the motion heading with effectively zero horizontal component"
            )
        screen_x_multiplier = -1.0 if chosen["raw_heading_dx_px_at_ortho_5"] > 0.0 else 1.0

    selected_side = int(chosen["side_sign"])
    selected_horizontal = chosen["horizontal"].copy()
    normalized_heading_dx = chosen["raw_heading_dx_px_at_ortho_5"] * screen_x_multiplier
    if normalized_heading_dx >= -1e-6:
        raise RuntimeError(
            f"screen-left guide normalization failed: normalized heading dx={normalized_heading_dx:.6f}px"
        )
    print(f"C1_CAMERA_SELECTED side={selected_side:+d}")
    print(f"C1_SCREEN_X_MULTIPLIER={screen_x_multiplier:+.1f}")
    print(f"C1_NORMALIZED_HEADING_DX_PX_AT_ORTHO_5={normalized_heading_dx:.6f}")

    def frame_target(rec):
        root = rec["joints"]["pelvis"]["world"]
        forward = flat_xy(root - root_first).dot(heading)
        xy = flat_xy(root_first) + heading * forward
        return Vector((xy.x, xy.y, baseline_center_z))

    camera.data.ortho_scale = 5.0
    max_height_at_5 = 0.0
    for rec in raw:
        configure_camera(camera, frame_target(rec), heading, pitch, selected_side, azimuth)
        ys = []
        for item in rec["joints"].values():
            co = world_to_camera_view(scene, camera, item["world"])
            ys.append(float((1.0 - co.y) * scene.render.resolution_y))
        max_height_at_5 = max(max_height_at_5, max(ys) - min(ys))
    target_height = float(spec["camera"]["target_skeleton_height_px"])
    if max_height_at_5 <= 1e-6:
        raise RuntimeError("projected skeleton height is zero")
    camera.data.ortho_scale *= max_height_at_5 / target_height
    locked_ortho = float(camera.data.ortho_scale)

    configure_camera(camera, target0, heading, pitch, selected_side, azimuth)
    fixed_camera_matrix = camera.matrix_world.copy()
    fixed_root_x = projected_screen_x(scene, camera, root_first, screen_x_multiplier)

    all_ground_z = min(
        rec["joints"][key]["world"].z
        for rec in raw
        for key in ("left_ankle", "left_toe", "right_ankle", "right_toe")
    )

    output_frames = []
    for rec in raw:
        target = frame_target(rec)
        configure_camera(camera, target, heading, pitch, selected_side, azimuth)
        camera.data.ortho_scale = locked_ortho
        bpy.context.view_layer.update()
        joints = {}
        for key, item in rec["joints"].items():
            sr = screen_record(scene, camera, item["world"], screen_x_multiplier)
            sr["anatomical_side"] = item["side"]
            sr["bone"] = item["bone"]
            joints[key] = sr

        chain_rows = []
        for name, a, b, side in chains:
            ja, jb = joints[a], joints[b]
            dx = jb["x"] - ja["x"]
            dy = jb["y"] - ja["y"]
            wa = Vector(rec["joints"][a]["world"])
            wb = Vector(rec["joints"][b]["world"])
            chain_rows.append({
                "name": name,
                "a": a,
                "b": b,
                "anatomical_side": side,
                "mean_depth": float((ja["depth"] + jb["depth"]) * 0.5),
                "screen_length_px": float(math.sqrt(dx * dx + dy * dy)),
                "world_length": float((wb - wa).length),
            })

        left_depth = sum(joints[k]["depth"] for k in joints if k.startswith("left_")) / 7.0
        right_depth = sum(joints[k]["depth"] for k in joints if k.startswith("right_")) / 7.0
        near_side = "left" if left_depth < right_depth else "right"
        far_side = "right" if near_side == "left" else "left"

        camera.matrix_world = fixed_camera_matrix
        camera.data.ortho_scale = locked_ortho
        bpy.context.view_layer.update()
        root_fixed_x = projected_screen_x(
            scene, camera, rec["joints"]["pelvis"]["world"], screen_x_multiplier
        )
        root_dx = root_fixed_x - fixed_root_x

        left_low = min(rec["joints"]["left_ankle"]["world"].z, rec["joints"]["left_toe"]["world"].z)
        right_low = min(rec["joints"]["right_ankle"]["world"].z, rec["joints"]["right_toe"]["world"].z)

        scene.frame_set(rec["frame"])
        bpy.context.view_layer.update()
        bone_transforms = {}
        for bone in required_bones:
            bone_transforms[bone] = {
                "matrix_world": bone_world_matrix(rig, bone),
                "head_world": [float(v) for v in bone_world_point(rig, bone, "head")],
                "tail_world": [float(v) for v in bone_world_point(rig, bone, "tail")],
            }

        output_frames.append({
            "frame": rec["frame"],
            "event": rec["event"],
            "support_foot": rec["support_foot"],
            "root_travel_dx_px": float(root_dx),
            "near_anatomical_side": near_side,
            "far_anatomical_side": far_side,
            "left_mean_camera_depth": float(left_depth),
            "right_mean_camera_depth": float(right_depth),
            "foot_ground_distance_world": {
                "left": float(left_low - all_ground_z),
                "right": float(right_low - all_ground_z),
            },
            "joints": joints,
            "chains": chain_rows,
            "bone_transforms": bone_transforms,
        })

    total_dx = float(output_frames[-1]["root_travel_dx_px"])
    if total_dx >= 0:
        raise RuntimeError(f"C1 skeleton travel contract failed: total root dx={total_dx:.4f}px")

    heights = []
    for rec in output_frames:
        ys = [float(v["y"]) for v in rec["joints"].values()]
        heights.append(max(ys) - min(ys))

    result = {
        "gate": "G3S-C1A",
        "revision": "SKELETON_ONLY_WALK_CYCLE_V1",
        "status": "REVIEW_REQUIRED",
        "source_motion": "CMU 105_34 NormalWalk",
        "source_rig": "G2_CANONICAL_RIG",
        "skinned_human_mesh_used": False,
        "mpfb_body_used": False,
        "hidden_3d_visible_art_owner": False,
        "cycle_frames": frames,
        "frame_duration_ms": int(spec.get("frame_duration_ms", 83)),
        "camera": {
            "raster": [int(scene.render.resolution_x), int(scene.render.resolution_y)],
            "type": "ORTHO",
            "pitch_deg": pitch,
            "azimuth_from_motion_heading_deg": azimuth,
            "selected_lateral_side_sign": selected_side,
            "heading_world": [float(heading.x), float(heading.y), float(heading.z)],
            "horizontal_camera_offset_direction_world": [float(selected_horizontal.x), float(selected_horizontal.y), float(selected_horizontal.z)],
            "ortho_scale": locked_ortho,
            "target_skeleton_height_px": target_height,
            "max_measured_skeleton_height_px": float(max(heights)),
            "tracking": "follow forward root component only; preserve lateral sway and vertical gait motion",
            "screen_x_multiplier": screen_x_multiplier,
            "screen_x_normalization": (
                "none" if screen_x_multiplier > 0.0
                else "horizontal guide-coordinate normalization only; rig/world/depth remain unchanged"
            ),
            "selection_candidates": [
                {
                    "side_sign": int(c["side_sign"]),
                    "raw_heading_dx_px_at_ortho_5": float(c["raw_heading_dx_px_at_ortho_5"]),
                }
                for c in camera_candidates
            ],
        },
        "root_travel_total_dx_px": total_dx,
        "ground_reference_z": float(all_ground_z),
        "frames": output_frames,
        "production_rule": "skeleton guide is control data only; visible anatomy/RGB/alpha/silhouette belong to persistent native-2D pose assets"
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print("G3S_C1A_SKELETON_WALK=REVIEW_REQUIRED")
    print("C1_SOURCE_RIG=G2_CANONICAL_RIG")
    print("C1_SKINNED_MESH_USED=false")
    print("C1_CYCLE=" + ",".join(str(x) for x in frames))
    print(f"C1_TRAVEL_TOTAL_DX_PX={total_dx:.4f}")
    print(f"C1_MAX_SKELETON_HEIGHT_PX={max(heights):.3f}")
    print(f"C1_GUIDE_JSON={output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
