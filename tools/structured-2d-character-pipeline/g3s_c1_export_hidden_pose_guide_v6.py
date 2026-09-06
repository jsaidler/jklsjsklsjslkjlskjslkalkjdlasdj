import json
import math
import runpy
import sys
from pathlib import Path

import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

import g3s_c1_export_hidden_pose_guide_v5 as v5


BASE = Path(__file__).with_name("g3s_c1_export_hidden_pose_guide.py")


def matrix_max_delta(a, b):
    return max(abs(float(a[r][c]) - float(b[r][c])) for r in range(4) for c in range(4))


def configure_front_three_quarter_camera(camera, target, travel_world, pitch_deg, azimuth_deg=45.0):
    """Place camera in front-three-quarter view without transforming rig/body.

    The hidden locomotion heading itself defines the horizontal view basis. The camera is
    placed ahead of the character and on the +90-degree lateral side. With a positive
    azimuth this makes forward travel project to screen-left while preserving the original
    MPFB rig/body bind and parent state.
    """
    heading = Vector((travel_world.x, travel_world.y, 0.0))
    if heading.length <= 1e-8:
        heading = Vector((1.0, 0.0, 0.0))
    heading.normalize()
    lateral = Vector((-heading.y, heading.x, 0.0))
    lateral.normalize()

    az = math.radians(azimuth_deg)
    horizontal_dir = heading * math.cos(az) + lateral * math.sin(az)
    horizontal_dir.normalize()

    pitch = math.radians(pitch_deg)
    distance = 12.0
    horizontal_distance = distance * math.cos(pitch)
    vertical_distance = distance * math.sin(pitch)

    camera.location = Vector(target) + horizontal_dir * horizontal_distance + Vector((0.0, 0.0, vertical_distance))
    camera.rotation_euler = (Vector(target) - camera.location).to_track_quat("-Z", "Y").to_euler()
    return heading, lateral, horizontal_dir


def main():
    namespace_copy = runpy.run_path(str(BASE), run_name="g3s_c1_hidden_pose_base_v6")
    base_main = namespace_copy.get("main")
    if base_main is None or not callable(base_main):
        raise RuntimeError("C1A base exporter did not expose callable main()")
    g = base_main.__globals__

    # Retain the V5 topology-free depth shader. V6 changes pose presentation/facing only.
    v5.install_v5(g)
    assign_depth_materials = g["assign_depth_materials"]

    arg = g["arg"]
    bone_world = g["bone_world"]
    source_contact_metrics = g["source_contact_metrics"]
    bbox_world = g["bbox_world"]
    bbox_px = g["bbox_px"]
    calibrate_camera = g["calibrate_camera"]
    set_world = g["set_world"]
    set_single_material = g["set_single_material"]
    render = g["render"]
    assign_region_materials = g["assign_region_materials"]
    emission_material = g["emission_material"]
    diffuse_material = g["diffuse_material"]
    screen_record = g["screen_record"]

    g3v_blend = Path(arg("--g3v-blend", "")).resolve()
    approval_path = Path(arg("--approval", "")).resolve()
    output_dir = Path(arg("--output-dir", "")).resolve()
    pitch = float(arg("--pitch", "26"))
    hero_px = int(arg("--hero-px", "128"))

    if not g3v_blend.is_file():
        raise RuntimeError(f"G3V hidden-guide blend missing: {g3v_blend}")
    if not approval_path.is_file():
        raise RuntimeError(f"retarget approval missing: {approval_path}")
    output_dir.mkdir(parents=True, exist_ok=True)

    approval = json.loads(approval_path.read_text(encoding="utf-8-sig"))
    if approval.get("gate") != "G3V-R" or approval.get("status") != "PASS" or approval.get("method") != "DIRECTION_SPACE_FK":
        raise RuntimeError("validated DIRECTION_SPACE_FK approval is not PASS")
    candidate_frames = [int(x) for x in approval.get("source_frames", [])]
    if len(candidate_frames) != 4:
        raise RuntimeError(f"expected four validated gait phase frames, got {candidate_frames}")

    bpy.ops.wm.open_mainfile(filepath=str(g3v_blend))
    scene = bpy.context.scene
    source = bpy.data.objects.get("G2_CANONICAL_RIG")
    target = bpy.data.objects.get("G3V_CMU_RIG")
    body = bpy.data.objects.get("G3V_BODY")
    if source is None or source.type != "ARMATURE":
        raise RuntimeError("G2_CANONICAL_RIG missing from hidden-guide blend")
    if target is None or target.type != "ARMATURE":
        raise RuntimeError("G3V_CMU_RIG missing from hidden-guide blend")
    if body is None or body.type != "MESH":
        raise RuntimeError("G3V_BODY missing from hidden-guide blend")

    helper_dir = Path(__file__).resolve().parent.parent / "deterministic-character-pipeline"
    if str(helper_dir) not in sys.path:
        sys.path.insert(0, str(helper_dir))
    import g3v_motion_binding_patch as motion_patch

    chosen_frame, contact_metrics, source_ground = source_contact_metrics(scene, source, candidate_frames)

    scene.frame_set(chosen_frame)
    bpy.context.view_layer.update()
    root0 = bone_world(source, "Hips")
    scene.frame_set(chosen_frame + 1)
    bpy.context.view_layer.update()
    root1 = bone_world(source, "Hips")
    source_travel = root1 - root0
    source_travel.z = 0.0
    if source_travel.length <= 1e-8:
        source_travel = Vector((1.0, 0.0, 0.0))
    else:
        source_travel.normalize()

    scene.frame_set(chosen_frame)
    bpy.context.view_layer.update()
    motion_patch._apply_direction_space_fk(source, target)
    bpy.context.view_layer.update()

    # V6 lock: never rotate/translate/parent-edit either the rig or skinned body to choose
    # directional family. Direction is a camera/view decision only.
    target_matrix_after_retarget = target.matrix_world.copy()
    body_matrix_after_retarget = body.matrix_world.copy()
    target_parent_after_retarget = target.parent
    body_parent_after_retarget = body.parent

    for obj in scene.objects:
        if obj.type == "MESH":
            obj.hide_render = (obj != body)
    source.hide_render = True
    target.hide_render = True
    body.hide_render = False

    lo, hi = bbox_world(body)
    target_point = (lo + hi) * 0.5

    for obj in list(scene.objects):
        if obj.type == "CAMERA":
            obj.hide_render = True
    bpy.ops.object.camera_add()
    camera = bpy.context.object
    camera.name = "G3S_C1_GUIDE_CAMERA"
    camera.data.type = "ORTHO"
    camera.data.clip_start = 0.01
    camera.data.clip_end = 1000.0
    scene.camera = camera

    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 640
    scene.render.resolution_y = 360
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.film_transparent = False
    try:
        scene.view_settings.view_transform = "Standard"
        scene.view_settings.look = "None"
        scene.view_settings.exposure = 0.0
        scene.view_settings.gamma = 1.0
    except Exception:
        pass

    heading, lateral, camera_horizontal_dir = configure_front_three_quarter_camera(
        camera, target_point, source_travel, pitch, 45.0
    )
    calibrate_camera(scene, camera, body, hero_px)

    hips_world = bone_world(target, "Hips")
    c0 = world_to_camera_view(scene, camera, hips_world)
    c1 = world_to_camera_view(scene, camera, hips_world + source_travel)
    travel_dx_px = float((c1.x - c0.x) * scene.render.resolution_x)
    if travel_dx_px >= 0:
        raise RuntimeError(
            f"C1 V6 camera-facing contract failed: unmodified forward travel must project screen-left, dx={travel_dx_px:.4f}px"
        )

    # Object/bind state must remain exactly what the validated retarget produced.
    transform_delta_before_render = max(
        matrix_max_delta(target.matrix_world, target_matrix_after_retarget),
        matrix_max_delta(body.matrix_world, body_matrix_after_retarget),
    )
    if transform_delta_before_render > 1e-8 or target.parent is not target_parent_after_retarget or body.parent is not body_parent_after_retarget:
        raise RuntimeError(
            f"C1 V6 changed rig/body object state before rendering: matrix_delta={transform_delta_before_render:.10f}"
        )

    for obj in list(scene.objects):
        if obj.type == "LIGHT":
            bpy.data.objects.remove(obj, do_unlink=True)
    bpy.ops.object.light_add(type="SUN", location=tuple(camera.location))
    sun = bpy.context.object
    sun.rotation_euler = (math.radians(35), 0.0, math.radians(-35))
    sun.data.energy = 2.5

    neutral = diffuse_material("C1_NEUTRAL", (0.48, 0.48, 0.50))
    white = emission_material("C1_SILHOUETTE", (1.0, 1.0, 1.0))
    region_colors = {
        "head": (0.80, 0.72, 0.22),
        "torso": (0.32, 0.74, 0.36),
        "left_arm": (0.20, 0.52, 0.95),
        "right_arm": (0.95, 0.30, 0.22),
        "left_leg": (0.18, 0.80, 0.88),
        "right_leg": (0.95, 0.58, 0.16),
    }
    region_order = ["head", "torso", "left_arm", "right_arm", "left_leg", "right_leg"]
    region_mats = {k: emission_material("C1_REGION_" + k.upper(), v) for k, v in region_colors.items()}
    depth_mats = []

    neutral_path = output_dir / "g3s_c1_contact_left_hidden3d_neutral.png"
    silhouette_path = output_dir / "g3s_c1_contact_left_silhouette_guide.png"
    regions_path = output_dir / "g3s_c1_contact_left_regions_guide.png"
    depth_path = output_dir / "g3s_c1_contact_left_depth_guide.png"

    set_world(scene, (0.055, 0.055, 0.065))
    set_single_material(body, neutral)
    render(scene, neutral_path)

    set_world(scene, (0.0, 0.0, 0.0))
    set_single_material(body, white)
    render(scene, silhouette_path)

    region_counts = assign_region_materials(body, region_mats, region_order)
    render(scene, regions_path)

    depth_stats = assign_depth_materials(body, camera, depth_mats)
    render(scene, depth_path)

    transform_delta_after_render = max(
        matrix_max_delta(target.matrix_world, target_matrix_after_retarget),
        matrix_max_delta(body.matrix_world, body_matrix_after_retarget),
    )
    if transform_delta_after_render > 1e-8 or target.parent is not target_parent_after_retarget or body.parent is not body_parent_after_retarget:
        raise RuntimeError(
            f"C1 V6 changed rig/body object state during guide rendering: matrix_delta={transform_delta_after_render:.10f}"
        )

    joint_defs = {
        "pelvis": ("Hips", False, "center"),
        "chest": ("Spine1", False, "center"),
        "neck": ("Neck1", False, "center"),
        "head": ("Head", True, "center"),
        "left_shoulder": ("LeftArm", False, "left"),
        "left_elbow": ("LeftForeArm", False, "left"),
        "left_wrist": ("LeftHand", False, "left"),
        "right_shoulder": ("RightArm", False, "right"),
        "right_elbow": ("RightForeArm", False, "right"),
        "right_wrist": ("RightHand", False, "right"),
        "left_hip": ("LeftUpLeg", False, "left"),
        "left_knee": ("LeftLeg", False, "left"),
        "left_ankle": ("LeftFoot", False, "left"),
        "left_toe": ("LeftToeBase", False, "left"),
        "right_hip": ("RightUpLeg", False, "right"),
        "right_knee": ("RightLeg", False, "right"),
        "right_ankle": ("RightFoot", False, "right"),
        "right_toe": ("RightToeBase", False, "right"),
    }
    joints = {}
    for key, (bone, tail, side) in joint_defs.items():
        if target.pose.bones.get(bone) is None:
            continue
        rec = screen_record(scene, camera, bone_world(target, bone, tail))
        rec["anatomical_side"] = side
        rec["bone"] = bone
        joints[key] = rec

    left_keys = [k for k in joints if k.startswith("left_")]
    right_keys = [k for k in joints if k.startswith("right_")]
    left_depth = sum(joints[k]["depth"] for k in left_keys) / max(1, len(left_keys))
    right_depth = sum(joints[k]["depth"] for k in right_keys) / max(1, len(right_keys))
    near_side = "left" if left_depth < right_depth else "right"
    far_side = "right" if near_side == "left" else "left"

    body_bbox = bbox_px(scene, camera, body)
    visible_height = body_bbox[3] - body_bbox[1]

    pose_data = {
        "gate": "G3S-C1A",
        "revision": "HIDDEN_3D_FULL_POSE_GUIDE_V6_CAMERA_DIRECTIONAL_FAMILY",
        "status": "REVIEW_REQUIRED",
        "guide_only": True,
        "hidden_3d_visible_art_owner": False,
        "selected_event": "left_contact",
        "selected_source_frame": chosen_frame,
        "candidate_phase_metrics": contact_metrics,
        "source_ground_reference_z": source_ground,
        "source_motion": "CMU 105_34 NormalWalk via G2_CANONICAL_RIG",
        "retarget_method": "DIRECTION_SPACE_FK",
        "direction_family": "screen-left",
        "direction_family_method": "camera_relative_to_motion_no_rig_or_body_transform",
        "travel_vector_screen_dx_px": travel_dx_px,
        "contact_foot": "left",
        "near_anatomical_side": near_side,
        "far_anatomical_side": far_side,
        "left_mean_camera_depth": left_depth,
        "right_mean_camera_depth": right_depth,
        "camera": {
            "raster": [640, 360],
            "type": "ORTHO",
            "pitch_deg": pitch,
            "horizontal_view": "front_three_quarter",
            "azimuth_from_motion_heading_deg": 45.0,
            "ortho_scale": float(camera.data.ortho_scale),
            "target_body_height_px": hero_px,
            "measured_body_height_px": visible_height,
            "heading_world": [float(heading.x), float(heading.y), float(heading.z)],
            "lateral_world": [float(lateral.x), float(lateral.y), float(lateral.z)],
            "horizontal_camera_offset_direction_world": [
                float(camera_horizontal_dir.x), float(camera_horizontal_dir.y), float(camera_horizontal_dir.z)
            ],
        },
        "body_bbox_px": body_bbox,
        "region_polygon_counts": region_counts,
        "depth_guide": depth_stats,
        "joints": joints,
        "root_pelvis_world": joints.get("pelvis", {}).get("world"),
        "transform_safeguard": {
            "rig_or_body_directional_transform_applied": False,
            "grounding_transform_applied": False,
            "target_parent_preserved": target.parent is target_parent_after_retarget,
            "body_parent_preserved": body.parent is body_parent_after_retarget,
            "max_object_matrix_delta_before_render": transform_delta_before_render,
            "max_object_matrix_delta_after_render": transform_delta_after_render,
        },
        "outputs": {
            "neutral": str(neutral_path),
            "silhouette": str(silhouette_path),
            "regions": str(regions_path),
            "depth": str(depth_path),
        },
        "production_rule": "all rendered 3D passes are guide/control evidence only; none may be promoted, quantized or repurposed as final sprite RGB/alpha/silhouette",
    }
    pose_path = output_dir / "g3s_c1_contact_left_pose_guide.json"
    pose_path.write_text(json.dumps(pose_data, indent=2) + "\n", encoding="utf-8")

    print("G3S_C1A_EXPORTER_REVISION=V6_CAMERA_DIRECTIONAL_FAMILY")
    print("C1_DIRECTION_METHOD=CAMERA_ONLY_NO_RIG_BODY_TRANSFORM")
    print(f"C1_OBJECT_TRANSFORM_DELTA={transform_delta_after_render:.10f}")
    print("G3S_C1A=REVIEW_REQUIRED")
    print("C1_SELECTED_EVENT=left_contact")
    print(f"C1_SELECTED_FRAME={chosen_frame}")
    print(f"C1_NEAR_SIDE={near_side}")
    print(f"C1_FAR_SIDE={far_side}")
    print(f"C1_TRAVEL_DX_PX={travel_dx_px:.4f}")
    print(f"C1_BODY_HEIGHT_PX={visible_height:.3f}")
    print(f"C1_POSE_JSON={pose_path}")


if __name__ == "__main__":
    main()
