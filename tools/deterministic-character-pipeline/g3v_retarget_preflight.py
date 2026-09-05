import bpy
import hashlib
import importlib
import json
import math
import sys
from pathlib import Path
from statistics import median

from mathutils import Matrix, Vector
from bpy_extras.object_utils import world_to_camera_view


REQUIRED = (
    "Hips", "Spine1", "Neck1", "Head",
    "LeftArm", "LeftForeArm", "LeftHand",
    "RightArm", "RightForeArm", "RightHand",
    "LeftUpLeg", "LeftLeg", "LeftFoot",
    "RightUpLeg", "RightLeg", "RightFoot",
)

CHAINS = (
    ("Hips", "Spine1"),
    ("Spine1", "Neck1"),
    ("Neck1", "Head"),
    ("Head", "__TAIL__"),
    ("LeftArm", "LeftForeArm"),
    ("LeftForeArm", "LeftHand"),
    ("LeftHand", "__TAIL__"),
    ("RightArm", "RightForeArm"),
    ("RightForeArm", "RightHand"),
    ("RightHand", "__TAIL__"),
    ("LeftUpLeg", "LeftLeg"),
    ("LeftLeg", "LeftFoot"),
    ("LeftFoot", "__TAIL__"),
    ("RightUpLeg", "RightLeg"),
    ("RightLeg", "RightFoot"),
    ("RightFoot", "__TAIL__"),
)

JOINTS = {
    "left_elbow": ("LeftArm", "LeftForeArm", "LeftHand"),
    "right_elbow": ("RightArm", "RightForeArm", "RightHand"),
    "left_knee": ("LeftUpLeg", "LeftLeg", "LeftFoot"),
    "right_knee": ("RightUpLeg", "RightLeg", "RightFoot"),
}

SIGNATURE_BONES = (
    "LeftHand", "RightHand", "LeftLeg", "RightLeg", "LeftFoot", "RightFoot"
)


def cli_args():
    return sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []


def arg(name, default=None):
    args = cli_args()
    for i, value in enumerate(args):
        if value == name and i + 1 < len(args):
            return args[i + 1]
    return default


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def mpfb_class(submodule, name):
    for root in ("mpfb", "bl_ext.blender_org.mpfb"):
        try:
            mod = importlib.import_module(root + "." + submodule)
            if hasattr(mod, name):
                return getattr(mod, name)
        except Exception:
            pass
    raise RuntimeError(f"MPFB class unavailable: {submodule}.{name}")


def cluster_centers(frames):
    vals = sorted({int(v) for v in frames})
    if not vals:
        return []
    groups = [[vals[0]]]
    for value in vals[1:]:
        if value - groups[-1][-1] <= 2:
            groups[-1].append(value)
        else:
            groups.append([value])
    return [int(round((g[0] + g[-1]) * 0.5)) for g in groups]


def derive_phase_frames(meta):
    contacts = meta.get("contacts", {})
    source = meta.get("source", {})
    clip = meta.get("selected_clip", {})
    fps = float(source.get("fps", 120.0))
    clip_start = int(clip.get("start_frame", 0))
    clip_end = int(clip.get("end_frame", 0))
    if clip_end <= clip_start:
        raise RuntimeError("Invalid G2 selected_clip")

    min_period = max(12, int(round(fps * 0.25)))
    max_period = max(min_period + 1, int(round(fps * 1.20)))
    centers_by_side = {}
    periods = []

    for side in ("LeftFoot", "RightFoot"):
        centers = cluster_centers(contacts.get(side, {}).get("contact_frames_sample", []))
        centers_by_side[side] = centers
        for a, b in zip(centers[:-1], centers[1:]):
            d = b - a
            if min_period <= d <= max_period:
                periods.append(d)

    if periods:
        period = float(median(periods))
    else:
        combined = sorted(centers_by_side.get("LeftFoot", []) + centers_by_side.get("RightFoot", []))
        half = []
        for a, b in zip(combined[:-1], combined[1:]):
            d = b - a
            if max(6, min_period // 3) <= d <= max_period // 2 + 4:
                half.append(d)
        if not half:
            raise RuntimeError("Could not derive gait period from G2 contact metadata")
        period = float(median(half) * 2.0)

    bases = [
        f for f in sorted(centers_by_side.get("LeftFoot", []) + centers_by_side.get("RightFoot", []))
        if clip_start <= f <= clip_end
    ]
    base = None
    for candidate in bases:
        if candidate + period * 0.75 <= clip_end:
            base = float(candidate)
            break
    if base is None:
        base = max(float(clip_start), float(clip_end) - period * 0.75)

    frames = [int(round(base + period * q)) for q in (0.0, 0.25, 0.50, 0.75)]
    if len(set(frames)) != 4:
        raise RuntimeError(f"Contact-derived phases not unique: {frames}")
    return period, frames


def reset_pose(rig):
    if rig.animation_data is not None:
        rig.animation_data.action = None
    for pb in rig.pose.bones:
        pb.matrix_basis.identity()
    bpy.context.view_layer.update()


def armature_height_rest(rig):
    head = rig.data.bones["Head"].tail_local
    lf = rig.data.bones["LeftFoot"].head_local
    rf = rig.data.bones["RightFoot"].head_local
    return max(0.5, float(head.z - min(lf.z, rf.z)))


def arm_point(rig, bone, tail=False):
    pb = rig.pose.bones.get(bone)
    if pb is None:
        raise RuntimeError("Missing pose bone: " + bone)
    local = pb.tail if tail else pb.head
    return rig.matrix_world @ local


def rest_point(rig, bone, tail=False):
    db = rig.data.bones.get(bone)
    if db is None:
        raise RuntimeError("Missing rest bone: " + bone)
    local = db.tail_local if tail else db.head_local
    return rig.matrix_world @ local


def angle_deg(a, b, c):
    v1 = Vector(a) - Vector(b)
    v2 = Vector(c) - Vector(b)
    if v1.length <= 1e-8 or v2.length <= 1e-8:
        return 0.0
    return math.degrees(v1.angle(v2))


def joint_angles(rig):
    out = {}
    for key, (a, b, c) in JOINTS.items():
        out[key] = angle_deg(arm_point(rig, a), arm_point(rig, b), arm_point(rig, c))
    return out


def pose_signature(rig):
    hips = arm_point(rig, "Hips")
    h = armature_height_rest(rig)
    values = []
    for name in SIGNATURE_BONES:
        p = (arm_point(rig, name) - hips) / h
        values.extend(round(float(v), 5) for v in p)
    return tuple(values)


def endpoint_motion_signature(rig):
    hips_pose = arm_point(rig, "Hips")
    hips_rest = rest_point(rig, "Hips")
    h = armature_height_rest(rig)
    out = {}
    for name in ("Head", "LeftHand", "RightHand", "LeftFoot", "RightFoot"):
        pose = arm_point(rig, name)
        rest = rest_point(rig, name)
        delta = ((pose - hips_pose) - (rest - hips_rest)) / h
        out[name] = [float(delta.x), float(delta.y), float(delta.z)]
    return out


def endpoint_rms(source_sig, target_sig):
    vals = []
    for name in source_sig:
        a = source_sig[name]
        b = target_sig[name]
        for i in range(3):
            vals.append((a[i] - b[i]) ** 2)
    return math.sqrt(sum(vals) / max(1, len(vals)))


def rest_audit(source, target):
    rows = []
    parent_mismatches = []
    orientation_angles = []
    length_ratios = []

    for name in REQUIRED:
        sb = source.data.bones[name]
        tb = target.data.bones[name]
        sp = sb.parent.name if sb.parent else None
        tp = tb.parent.name if tb.parent else None
        if sp != tp:
            parent_mismatches.append({"bone": name, "source_parent": sp, "target_parent": tp})

        qs = sb.matrix_local.to_quaternion()
        qt = tb.matrix_local.to_quaternion()
        angle = math.degrees(qs.rotation_difference(qt).angle)
        ratio = float(tb.length / sb.length) if sb.length > 1e-8 else 1.0
        orientation_angles.append(angle)
        length_ratios.append(ratio)
        rows.append({
            "bone": name,
            "source_parent": sp,
            "target_parent": tp,
            "rest_orientation_delta_deg": angle,
            "length_ratio_target_over_source": ratio,
        })

    return {
        "bones": rows,
        "parent_mismatches": parent_mismatches,
        "orientation_delta_mean_deg": sum(orientation_angles) / len(orientation_angles),
        "orientation_delta_max_deg": max(orientation_angles),
        "length_ratio_min": min(length_ratios),
        "length_ratio_max": max(length_ratios),
    }


def apply_mpfb_pose_api(source, target, RigService):
    pose = RigService.get_pose_as_dict(
        source,
        root_bone_translation=True,
        ik_bone_translation=True,
        fk_bone_translation=False,
        onlyselected=False,
    )
    reset_pose(target)
    RigService.set_pose_from_dict(target, pose, from_rest_pose=True)
    bpy.context.view_layer.update()


def _depth(bone):
    d = 0
    b = bone
    while b.parent is not None:
        d += 1
        b = b.parent
    return d


def apply_rest_compensated_fk(source, target):
    reset_pose(target)

    common = [
        name for name in target.pose.bones.keys()
        if source.pose.bones.get(name) is not None and source.data.bones.get(name) is not None
    ]
    common.sort(key=lambda n: _depth(target.data.bones[n]))

    source_h = armature_height_rest(source)
    target_h = armature_height_rest(target)
    root_scale = target_h / source_h

    for name in common:
        sb = source.data.bones[name]
        spb = source.pose.bones[name]
        tb = target.data.bones[name]
        tpb = target.pose.bones[name]

        if sb.parent is not None and sb.parent.name in common:
            sr_local = source.data.bones[sb.parent.name].matrix_local.inverted_safe() @ sb.matrix_local
            sp_local = source.pose.bones[sb.parent.name].matrix.inverted_safe() @ spb.matrix
        else:
            sr_local = sb.matrix_local.copy()
            sp_local = spb.matrix.copy()

        if tb.parent is not None and tb.parent.name in common:
            tr_local = target.data.bones[tb.parent.name].matrix_local.inverted_safe() @ tb.matrix_local
        else:
            tr_local = tb.matrix_local.copy()

        qs_rest = sr_local.to_quaternion().normalized()
        qs_pose = sp_local.to_quaternion().normalized()
        qt_rest = tr_local.to_quaternion().normalized()

        delta_source_local = qs_rest.inverted() @ qs_pose
        source_to_target_basis = qs_rest.inverted() @ qt_rest
        delta_target_local = (
            source_to_target_basis.inverted()
            @ delta_source_local
            @ source_to_target_basis
        )
        qt_pose = (qt_rest @ delta_target_local).normalized()

        translation = tr_local.translation.copy()
        if tb.parent is None:
            source_delta = sp_local.translation - sr_local.translation
            translation += source_delta * root_scale

        local_pose = Matrix.Translation(translation) @ qt_pose.to_matrix().to_4x4()
        if tb.parent is not None and tb.parent.name in common:
            global_pose = target.pose.bones[tb.parent.name].matrix @ local_pose
        else:
            global_pose = local_pose
        tpb.matrix = global_pose

    bpy.context.view_layer.update()


def score_method(method, source, target, frames, RigService):
    per_frame = []
    signatures = []
    angle_errors = []
    endpoint_errors = []

    for frame in frames:
        bpy.context.scene.frame_set(frame)
        bpy.context.view_layer.update()
        src_angles = joint_angles(source)
        src_endpoint = endpoint_motion_signature(source)

        if method == "MPFB_POSE_API":
            apply_mpfb_pose_api(source, target, RigService)
        elif method == "REST_COMPENSATED_FK":
            apply_rest_compensated_fk(source, target)
        else:
            raise RuntimeError("Unknown retarget method: " + method)

        tgt_angles = joint_angles(target)
        tgt_endpoint = endpoint_motion_signature(target)
        sig = pose_signature(target)
        signatures.append(sig)

        frame_angle_errors = {
            key: abs(src_angles[key] - tgt_angles[key]) for key in src_angles
        }
        angle_errors.extend(frame_angle_errors.values())
        e_rms = endpoint_rms(src_endpoint, tgt_endpoint)
        endpoint_errors.append(e_rms)

        per_frame.append({
            "frame": frame,
            "source_joint_angles_deg": src_angles,
            "target_joint_angles_deg": tgt_angles,
            "joint_angle_abs_error_deg": frame_angle_errors,
            "endpoint_motion_rms_body_heights": e_rms,
            "target_pose_signature": list(sig),
        })

    unique_poses = len(set(signatures))
    mean_angle = sum(angle_errors) / max(1, len(angle_errors))
    max_angle = max(angle_errors) if angle_errors else 999.0
    mean_endpoint = sum(endpoint_errors) / max(1, len(endpoint_errors))
    score = mean_angle / 10.0 + mean_endpoint * 10.0

    return {
        "method": method,
        "unique_poses": unique_poses,
        "mean_joint_angle_error_deg": mean_angle,
        "max_joint_angle_error_deg": max_angle,
        "mean_endpoint_motion_rms_body_heights": mean_endpoint,
        "score": score,
        "frames": per_frame,
    }


def make_material(name, color):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    return mat


def add_segment(name, material):
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=1.0, depth=2.0)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(material)
    return obj


def add_marker(name, material):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=1.0)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(material)
    return obj


def set_segment(obj, a, b, radius):
    a = Vector(a)
    b = Vector(b)
    d = b - a
    length = max(1e-5, d.length)
    obj.location = (a + b) * 0.5
    obj.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
    obj.scale = (radius, radius, length * 0.5)


def skeleton_points(rig):
    pts = {}
    for name in REQUIRED:
        pts[(name, False)] = arm_point(rig, name)
        pts[(name, True)] = arm_point(rig, name, True)
    return pts


def update_proxy(rig, proxy, body_h):
    pts = skeleton_points(rig)
    radius = body_h * 0.018
    for i, (a, b) in enumerate(CHAINS):
        p1 = pts[(a, False)]
        if b == "__TAIL__":
            p2 = pts[(a, True)]
        else:
            p2 = pts[(b, False)]
        set_segment(proxy["segments"][i], p1, p2, radius)
    for key, obj in proxy["markers"].items():
        obj.location = pts[(key, False)]
        obj.scale = (radius * 1.9,) * 3
    bpy.context.view_layer.update()


def configure_camera(camera, target, pitch_deg):
    p = math.radians(pitch_deg)
    distance = 12.0
    camera.location = (target.x, target.y - distance * math.cos(p), target.z + distance * math.sin(p))
    camera.rotation_euler = (Vector(target) - camera.location).to_track_quat("-Z", "Y").to_euler()


def calibrate_camera(scene, camera, rig, target_px):
    camera.data.ortho_scale = 5.0
    for _ in range(6):
        bpy.context.view_layer.update()
        points = [
            arm_point(rig, "Head", True),
            arm_point(rig, "LeftFoot"),
            arm_point(rig, "RightFoot"),
        ]
        ys = [world_to_camera_view(scene, camera, p).y * scene.render.resolution_y for p in points]
        hpx = max(ys) - min(ys)
        if hpx <= 0.01:
            raise RuntimeError("Projected skeleton height is zero")
        camera.data.ortho_scale *= hpx / float(target_px)


def render_skeleton(scene, camera, rig, proxy, output_path, frame, pitch, hero_px):
    body_h = armature_height_rest(rig)
    update_proxy(rig, proxy, body_h)

    points = [arm_point(rig, "Head", True), arm_point(rig, "Hips"), arm_point(rig, "LeftFoot"), arm_point(rig, "RightFoot")]
    target = sum(points, Vector((0.0, 0.0, 0.0))) / len(points)
    configure_camera(camera, target, pitch)
    calibrate_camera(scene, camera, rig, hero_px)

    scene.render.filepath = str(output_path)
    bpy.ops.render.render(write_still=True)
    if not output_path.exists() or output_path.stat().st_size == 0:
        raise RuntimeError("Missing retarget preflight render: " + str(output_path))


def prepare_render_scene(scene):
    for obj in list(scene.objects):
        if obj.type in {"MESH", "CAMERA", "LIGHT"}:
            obj.hide_render = True

    scene.render.engine = "BLENDER_WORKBENCH"
    scene.render.resolution_x = 640
    scene.render.resolution_y = 360
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.film_transparent = False

    scene.display.shading.light = "FLAT"
    scene.display.shading.color_type = "MATERIAL"
    scene.display.shading.show_shadows = False
    scene.display.shading.show_cavity = False
    scene.display.shading.background_type = "WORLD"
    scene.world.color = (0.035, 0.040, 0.050)

    center_mat = make_material("RT_CENTER", (0.55, 0.55, 0.58))
    left_mat = make_material("RT_LEFT", (0.20, 0.55, 0.85))
    right_mat = make_material("RT_RIGHT", (0.85, 0.40, 0.22))
    marker_mat = make_material("RT_MARKER", (0.92, 0.78, 0.18))

    segments = []
    for i, (a, _b) in enumerate(CHAINS):
        if a.startswith("Left"):
            mat = left_mat
        elif a.startswith("Right"):
            mat = right_mat
        else:
            mat = center_mat
        segments.append(add_segment(f"RT_SEG_{i:02d}", mat))

    markers = {
        "Head": add_marker("RT_HEAD", marker_mat),
        "LeftHand": add_marker("RT_L_HAND", marker_mat),
        "RightHand": add_marker("RT_R_HAND", marker_mat),
        "LeftFoot": add_marker("RT_L_FOOT", marker_mat),
        "RightFoot": add_marker("RT_R_FOOT", marker_mat),
    }
    for obj in segments + list(markers.values()):
        obj.hide_render = False

    bpy.ops.object.camera_add()
    camera = bpy.context.object
    camera.name = "RT_CAMERA"
    camera.data.type = "ORTHO"
    scene.camera = camera
    camera.hide_render = False
    return camera, {"segments": segments, "markers": markers}


def main():
    output_dir = Path(arg("--output-dir", "")).resolve()
    g2_blend = Path(arg("--g2-blend", "")).resolve()
    g2_manifest_path = Path(arg("--g2-manifest", "")).resolve()
    pitch = float(arg("--pitch", "26"))
    hero_px = int(arg("--hero-px", "128"))

    if not g2_blend.exists() or not g2_manifest_path.exists():
        raise RuntimeError("Missing G2 artifacts for retarget preflight")
    output_dir.mkdir(parents=True, exist_ok=True)

    HumanService = mpfb_class("services.humanservice", "HumanService")
    TargetService = mpfb_class("services.targetservice", "TargetService")
    RigService = mpfb_class("services.rigservice", "RigService")

    meta = json.loads(g2_manifest_path.read_text(encoding="utf-8-sig"))
    gait_period, frames = derive_phase_frames(meta)

    bpy.ops.wm.open_mainfile(filepath=str(g2_blend))
    scene = bpy.context.scene
    source = bpy.data.objects.get("G2_CANONICAL_RIG")
    if source is None or source.type != "ARMATURE":
        raise RuntimeError("G2_CANONICAL_RIG missing")

    macro = TargetService.get_default_macro_info_dict()
    macro.update({
        "gender": 1.0,
        "age": 0.48,
        "muscle": 0.40,
        "weight": 0.36,
        "proportions": 0.56,
        "height": 0.52,
        "cupsize": 0.42,
        "firmness": 0.55,
    })
    body = HumanService.create_human(
        mask_helpers=True,
        detailed_helpers=True,
        extra_vertex_groups=True,
        feet_on_ground=True,
        scale=0.1,
        macro_detail_dict=macro,
    )
    body.name = "G3V_RETARGET_BODY"
    target = HumanService.add_builtin_rig(body, "cmu_mb", import_weights=True)
    if target is None:
        raise RuntimeError("MPFB cmu_mb rig creation failed")
    target.name = "G3V_RETARGET_RIG"

    missing_source = [name for name in REQUIRED if source.pose.bones.get(name) is None]
    missing_target = [name for name in REQUIRED if target.pose.bones.get(name) is None]
    if missing_source or missing_target:
        raise RuntimeError(f"Required retarget bones missing source={missing_source} target={missing_target}")

    rest = rest_audit(source, target)
    print(f"G3V_RETARGET_REST_ORIENTATION_MEAN_DEG={rest['orientation_delta_mean_deg']:.4f}")
    print(f"G3V_RETARGET_REST_ORIENTATION_MAX_DEG={rest['orientation_delta_max_deg']:.4f}")
    print(f"G3V_RETARGET_PARENT_MISMATCHES={len(rest['parent_mismatches'])}")
    print(f"G3V_RETARGET_GAIT_PERIOD={gait_period:.3f}")
    print("G3V_RETARGET_FRAMES=" + ",".join(str(f) for f in frames))

    methods = []
    api_error = None
    try:
        source_type = RigService.identify_rig(source)
        target_type = RigService.identify_rig(target)
        print("G3V_RETARGET_SOURCE_RIG_TYPE=" + str(source_type))
        print("G3V_RETARGET_TARGET_RIG_TYPE=" + str(target_type))
        methods.append(score_method("MPFB_POSE_API", source, target, frames, RigService))
    except Exception as exc:
        api_error = repr(exc)
        print("G3V_RETARGET_MPFB_POSE_API=UNAVAILABLE " + api_error)

    methods.append(score_method("REST_COMPENSATED_FK", source, target, frames, RigService))
    methods.sort(key=lambda m: m["score"])
    chosen = methods[0]

    for m in methods:
        print(
            "G3V_RETARGET_METHOD={} score={:.5f} unique={} mean_angle={:.4f} max_angle={:.4f} endpoint_rms={:.5f}".format(
                m["method"], m["score"], m["unique_poses"],
                m["mean_joint_angle_error_deg"], m["max_joint_angle_error_deg"],
                m["mean_endpoint_motion_rms_body_heights"],
            )
        )

    if chosen["unique_poses"] < 3:
        raise RuntimeError("Retarget preflight produced fewer than 3 unique target poses")
    if chosen["mean_joint_angle_error_deg"] > 15.0 or chosen["max_joint_angle_error_deg"] > 35.0:
        raise RuntimeError(
            "Retarget preflight joint-angle fidelity failed: "
            f"method={chosen['method']} mean={chosen['mean_joint_angle_error_deg']:.3f} "
            f"max={chosen['max_joint_angle_error_deg']:.3f}"
        )
    if chosen["mean_endpoint_motion_rms_body_heights"] > 0.18:
        raise RuntimeError(
            "Retarget preflight endpoint-motion fidelity failed: "
            f"method={chosen['method']} rms={chosen['mean_endpoint_motion_rms_body_heights']:.5f}"
        )

    print("G3V_RETARGET_CHOSEN_METHOD=" + chosen["method"])
    print("G3V_RETARGET_NUMERIC_AUDIT=PASS")

    camera, proxy = prepare_render_scene(scene)
    body.hide_render = True
    source.hide_render = True
    target.hide_render = True

    outputs = []

    for frame in frames:
        scene.frame_set(frame)
        bpy.context.view_layer.update()
        path = output_dir / f"retarget_source_f{frame:04d}.png"
        render_skeleton(scene, camera, source, proxy, path, frame, pitch, hero_px)
        outputs.append({
            "variant": "source",
            "frame": frame,
            "file": str(path),
            "sha256": sha256_file(path),
        })

    for frame in frames:
        scene.frame_set(frame)
        bpy.context.view_layer.update()
        if chosen["method"] == "MPFB_POSE_API":
            apply_mpfb_pose_api(source, target, RigService)
        else:
            apply_rest_compensated_fk(source, target)
        path = output_dir / f"retarget_target_f{frame:04d}.png"
        render_skeleton(scene, camera, target, proxy, path, frame, pitch, hero_px)
        outputs.append({
            "variant": "target",
            "frame": frame,
            "file": str(path),
            "sha256": sha256_file(path),
        })

    manifest = {
        "gate": "G3V_RETARGET_PREFLIGHT",
        "status": "REVIEW_REQUIRED",
        "purpose": "prove rest-pose-aware CMU->MPFB motion retarget before returning to representative body rendering",
        "source_frames": frames,
        "gait_period_frames": gait_period,
        "source_rig": "G2_CANONICAL_RIG",
        "target_rig": "G3V_RETARGET_RIG",
        "rest_audit": rest,
        "mpfb_pose_api_error": api_error,
        "methods": methods,
        "chosen_method": chosen["method"],
        "numeric_pass_thresholds": {
            "unique_poses_min": 3,
            "mean_joint_angle_error_deg_max": 15.0,
            "max_joint_angle_error_deg_max": 35.0,
            "mean_endpoint_motion_rms_body_heights_max": 0.18,
        },
        "outputs": outputs,
    }
    manifest_path = output_dir / "g3v_retarget_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print("G3V_RETARGET_PREFLIGHT=REVIEW_REQUIRED")
    print("G3V_RETARGET_MANIFEST=" + str(manifest_path))


if __name__ == "__main__":
    main()
