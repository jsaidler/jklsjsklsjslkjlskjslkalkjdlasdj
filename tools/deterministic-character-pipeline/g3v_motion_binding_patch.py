import hashlib
from pathlib import Path

import bpy
from mathutils import Matrix


_POSE_SIGNATURES = {}
_REQUIRED_BONES = (
    "Hips", "Spine1", "Neck1", "Head",
    "LeftArm", "LeftForeArm", "LeftHand", "RightArm", "RightForeArm", "RightHand",
    "LeftUpLeg", "LeftLeg", "LeftFoot", "RightUpLeg", "RightLeg", "RightFoot",
)
_SIGNATURE_BONES = (
    "LeftHand", "RightHand", "LeftLeg", "RightLeg", "LeftFoot", "RightFoot",
)


def _bone_world(rig, name, tail=False):
    pb = rig.pose.bones.get(name)
    if pb is None:
        raise RuntimeError("G3V motion binding missing bone: " + name)
    point = pb.tail if tail else pb.head
    return rig.matrix_world @ point


def _pose_signature(rig):
    hips = _bone_world(rig, "Hips")
    values = []
    for name in _SIGNATURE_BONES:
        p = _bone_world(rig, name) - hips
        values.extend((round(float(p.x), 5), round(float(p.y), 5), round(float(p.z), 5)))
    return tuple(values)


def _max_signature_delta(signatures):
    sigs = list(signatures)
    best = 0.0
    for i in range(len(sigs)):
        for j in range(i + 1, len(sigs)):
            a, b = sigs[i], sigs[j]
            total = 0.0
            for k in range(0, len(a), 3):
                dx = a[k] - b[k]
                dy = a[k + 1] - b[k + 1]
                dz = a[k + 2] - b[k + 2]
                total += (dx * dx + dy * dy + dz * dz) ** 0.5
            best = max(best, total)
    return best


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _depth(bone):
    d = 0
    current = bone
    while current.parent is not None:
        d += 1
        current = current.parent
    return d


def _reset_target_pose(target):
    if target.animation_data is not None:
        target.animation_data.action = None
    for pb in target.pose.bones:
        pb.matrix_basis.identity()
    bpy.context.view_layer.update()


def _apply_direction_space_fk(source, target):
    """Apply the G3V-R validated axis-independent CMU -> MPFB retarget.

    G3V-R measured source/target rest orientation differences of ~83 deg mean and
    ~180 deg max, despite matching CMU bone names and parent hierarchy. Therefore raw
    Action/matrix_basis/local-axis copying is invalid. This solver reproduces each posed
    source bone direction in target armature space, parent-first, while preserving MPFB's
    own bone lengths, hierarchy, weights and roll/twist convention.
    """
    _reset_target_pose(target)

    common = [
        name for name in target.pose.bones.keys()
        if source.pose.bones.get(name) is not None
        and source.data.bones.get(name) is not None
        and target.data.bones.get(name) is not None
    ]
    common.sort(key=lambda name: _depth(target.data.bones[name]))

    source_world_rot = source.matrix_world.to_quaternion().to_matrix()
    target_world_inv_rot = target.matrix_world.to_quaternion().inverted().to_matrix()

    for name in common:
        spb = source.pose.bones[name]
        tpb = target.pose.bones[name]

        source_dir = spb.tail - spb.head
        if source_dir.length <= 1e-8:
            continue
        desired_world = source_world_rot @ source_dir.normalized()
        desired_target_arm = target_world_inv_rot @ desired_world
        if desired_target_arm.length <= 1e-8:
            continue
        desired_target_arm.normalize()

        bpy.context.view_layer.update()
        current_dir = tpb.tail - tpb.head
        if current_dir.length <= 1e-8:
            continue
        current_dir.normalize()
        swing = current_dir.rotation_difference(desired_target_arm)

        current_matrix = tpb.matrix.copy()
        location = current_matrix.translation.copy()
        rotation = current_matrix.to_quaternion().normalized()
        new_rotation = (swing @ rotation).normalized()
        tpb.matrix = Matrix.Translation(location) @ new_rotation.to_matrix().to_4x4()
        bpy.context.view_layer.update()

    bpy.context.view_layer.update()


def install_motion_binding(target_globals):
    """Install the G3V-R-approved direction-space retarget into G3V body rendering."""
    required = ("bbox_world", "render_pass", "build_visible_outputs", "main")
    missing = [name for name in required if name not in target_globals]
    if missing:
        raise RuntimeError("G3V motion-binding patch missing target symbols: " + ", ".join(missing))

    original_bbox_world = target_globals["bbox_world"]
    original_render_pass = target_globals["render_pass"]
    original_build_visible_outputs = target_globals["build_visible_outputs"]

    state = {"initialized": False, "last_frame": None}

    def ensure_motion_binding():
        source = bpy.data.objects.get("G2_CANONICAL_RIG")
        target = bpy.data.objects.get("G3V_CMU_RIG")
        body = bpy.data.objects.get("G3V_BODY")
        if source is None or source.type != "ARMATURE":
            raise RuntimeError("G3V direction-space binding could not locate G2_CANONICAL_RIG")
        if target is None or target.type != "ARMATURE":
            return False
        if body is None or body.type != "MESH":
            raise RuntimeError("G3V direction-space binding could not locate G3V_BODY")

        if not state["initialized"]:
            missing_source = [b for b in _REQUIRED_BONES if source.pose.bones.get(b) is None]
            missing_target = [b for b in _REQUIRED_BONES if target.pose.bones.get(b) is None]
            if missing_source or missing_target:
                raise RuntimeError(
                    "G3V direction-space retarget bone mismatch: source=" + repr(missing_source)
                    + " target=" + repr(missing_target)
                )

            armature_modifiers = [
                m for m in body.modifiers
                if m.type == "ARMATURE" and getattr(m, "object", None) == target
            ]
            if not armature_modifiers:
                raise RuntimeError("G3V_BODY has no Armature modifier bound to G3V_CMU_RIG")

            if target.animation_data is not None:
                target.animation_data.action = None
            state["initialized"] = True
            print("G3V_MOTION_BINDING=DIRECTION_SPACE_FK_VALIDATED_G3V_R")
            print("G3V_MOTION_LOCAL_AXIS_COPY=DISABLED")
            print("G3V_TARGET_ACTION=DISABLED")
            print("G3V_BODY_ARMATURE_MODIFIER=PASS")

        frame = int(bpy.context.scene.frame_current)
        if state["last_frame"] == frame:
            return True

        _apply_direction_space_fk(source, target)
        signature = _pose_signature(target)
        _POSE_SIGNATURES[frame] = signature
        state["last_frame"] = frame
        print(
            "G3V_MOTION_POSE_FRAME_{}=RETARGETED sig={}".format(
                frame,
                ",".join(f"{v:.5f}" for v in signature[:9]),
            )
        )
        return True

    def motion_bbox_world(objects):
        ensure_motion_binding()
        return original_bbox_world(objects)

    def motion_render_pass(scene, path, semantic_objects, mode, id_materials, neutral_material):
        ensure_motion_binding()
        return original_render_pass(scene, path, semantic_objects, mode, id_materials, neutral_material)

    def audited_build_visible_outputs(frame_records, output_dir):
        ensure_motion_binding()

        frames = [int(rec["frame"]) for rec in frame_records]
        signatures = [_POSE_SIGNATURES.get(frame) for frame in frames]
        if any(sig is None for sig in signatures):
            raise RuntimeError(
                "G3V motion audit missing retargeted target pose signature for frames " + repr(frames)
            )
        unique_pose_count = len(set(signatures))
        max_pose_delta = _max_signature_delta(signatures)
        print(f"G3V_MOTION_UNIQUE_POSES={unique_pose_count}")
        print(f"G3V_MOTION_MAX_SIGNATURE_DELTA={max_pose_delta:.6f}")
        if unique_pose_count < 3 or max_pose_delta < 0.05:
            raise RuntimeError(
                "G3V target rig remains effectively static after direction-space retarget: "
                f"unique_poses={unique_pose_count}, max_signature_delta={max_pose_delta:.6f}, frames={frames}"
            )

        diagnostics = target_globals.get("G3V_MASK_DIAGNOSTICS", {})
        skin_hashes = []
        for frame in frames:
            entry = diagnostics.get(frame, {}).get("skin")
            if not entry:
                raise RuntimeError(f"G3V motion audit missing skin-mask diagnostics for frame {frame}")
            path = Path(entry["visible_mask"])
            if not path.exists():
                raise RuntimeError("G3V motion audit missing skin mask: " + str(path))
            skin_hashes.append(_sha256(path))

        unique_skin_masks = len(set(skin_hashes))
        print(f"G3V_MOTION_UNIQUE_SKIN_MASKS={unique_skin_masks}")
        if unique_skin_masks < 3:
            raise RuntimeError(
                "G3V rendered body deformation remains effectively static after validated retarget: "
                f"unique_skin_masks={unique_skin_masks}, frames={frames}"
            )

        print("G3V_MOTION_DIVERSITY_AUDIT=PASS")
        return original_build_visible_outputs(frame_records, output_dir)

    target_globals["bbox_world"] = motion_bbox_world
    target_globals["render_pass"] = motion_render_pass
    target_globals["build_visible_outputs"] = audited_build_visible_outputs

    if target_globals["bbox_world"] is not motion_bbox_world:
        raise RuntimeError("G3V direction-space bbox patch did not bind")
    if target_globals["render_pass"] is not motion_render_pass:
        raise RuntimeError("G3V direction-space render patch did not bind")
    if target_globals["build_visible_outputs"] is not audited_build_visible_outputs:
        raise RuntimeError("G3V direction-space diversity audit did not bind")

    print("G3V_MOTION_BINDING_MODE=VALIDATED_DIRECTION_SPACE_PER_FRAME")
    print("G3V_MOTION_REVIEW_REQUIRES=3_UNIQUE_POSES_AND_3_UNIQUE_SKIN_MASKS")
