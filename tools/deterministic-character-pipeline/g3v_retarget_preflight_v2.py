import bpy
import runpy
from pathlib import Path
from mathutils import Matrix, Vector


BASE = Path(__file__).with_name("g3v_retarget_preflight.py")


def _activate_pose_object(rig):
    current = bpy.context.object
    if current is not None and current.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
    for obj in bpy.context.view_layer.objects:
        obj.select_set(False)
    rig.hide_set(False)
    rig.hide_viewport = False
    rig.select_set(True)
    bpy.context.view_layer.objects.active = rig
    bpy.ops.object.mode_set(mode='POSE', toggle=False)


def install_v2(target_globals):
    required = (
        "main", "reset_pose", "armature_height_rest", "_depth", "score_method",
    )
    missing = [name for name in required if name not in target_globals]
    if missing:
        raise RuntimeError("G3V retarget v2 missing base symbols: " + ", ".join(missing))

    reset_pose = target_globals["reset_pose"]
    depth_fn = target_globals["_depth"]
    original_score_method = target_globals["score_method"]

    def apply_mpfb_pose_api_context_correct(source, target, RigService):
        # MPFB's own UI enters Pose Mode before set_pose_from_dict(). Reproduce that
        # contract explicitly in background mode so bpy.ops.pose.select_all has context.
        _activate_pose_object(source)
        pose = RigService.get_pose_as_dict(
            source,
            root_bone_translation=True,
            ik_bone_translation=True,
            fk_bone_translation=False,
            onlyselected=False,
        )
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        reset_pose(target)
        _activate_pose_object(target)
        RigService.set_pose_from_dict(target, pose, from_rest_pose=True)
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        bpy.context.view_layer.update()

    def apply_direction_space_fk(source, target):
        """Retarget articulation by posed bone directions, not source local axes.

        This is intentionally insensitive to source/target rest bone roll and local-axis
        conventions. The target keeps its own rest lengths, hierarchy, weights and bone
        heads. For each matching bone, processed parent-first, rotate the target bone in
        armature space so its +Y/bone direction matches the currently posed source bone
        direction in world space. This preserves anatomical bend directions while leaving
        target proportions owned by the MPFB rig.
        """
        reset_pose(target)
        bpy.context.view_layer.update()

        common = [
            name for name in target.pose.bones.keys()
            if source.pose.bones.get(name) is not None
            and source.data.bones.get(name) is not None
            and target.data.bones.get(name) is not None
        ]
        common.sort(key=lambda n: depth_fn(target.data.bones[n]))

        source_world_rot = source.matrix_world.to_quaternion().to_matrix()
        target_world_inv_rot = target.matrix_world.to_quaternion().inverted().to_matrix()

        for name in common:
            spb = source.pose.bones[name]
            tpb = target.pose.bones[name]

            sdir_local = spb.tail - spb.head
            if sdir_local.length <= 1e-8:
                continue
            sdir_world = source_world_rot @ sdir_local.normalized()
            desired_target_arm = target_world_inv_rot @ sdir_world
            if desired_target_arm.length <= 1e-8:
                continue
            desired_target_arm.normalize()

            # Parent bones have already been posed. Therefore tpb.matrix here contains
            # the target's own rest offset transformed by the posed parent. Swing only
            # the current orientation until its bone direction matches the source. This
            # retains target roll/twist convention instead of importing incompatible axes.
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

        # Root motion is deliberately excluded from fidelity scoring; the preflight
        # compares articulation relative to Hips. Gameplay root translation remains a
        # separate deterministic channel.
        bpy.context.view_layer.update()

    def score_method_v2(method, source, target, frames, RigService):
        if method == "REST_COMPENSATED_FK":
            # The base main() asks for this slot. Replace the failed local-axis method
            # with the rest-axis-independent direction-space solver and report its real name.
            result = original_score_method("REST_COMPENSATED_FK", source, target, frames, RigService)
            result["method"] = "DIRECTION_SPACE_FK"
            return result
        return original_score_method(method, source, target, frames, RigService)

    target_globals["apply_mpfb_pose_api"] = apply_mpfb_pose_api_context_correct
    target_globals["apply_rest_compensated_fk"] = apply_direction_space_fk
    target_globals["score_method"] = score_method_v2

    if target_globals["apply_mpfb_pose_api"] is not apply_mpfb_pose_api_context_correct:
        raise RuntimeError("G3V retarget v2 MPFB API patch did not bind")
    if target_globals["apply_rest_compensated_fk"] is not apply_direction_space_fk:
        raise RuntimeError("G3V retarget v2 direction-space patch did not bind")

    print("G3V_RETARGET_V2=BOUND")
    print("G3V_RETARGET_MPFB_API_CONTEXT=POSE_MODE")
    print("G3V_RETARGET_AXIS_INDEPENDENT_METHOD=DIRECTION_SPACE_FK")


def main():
    namespace_copy = runpy.run_path(str(BASE), run_name="g3v_retarget_base")
    target_main = namespace_copy.get("main")
    if target_main is None or not callable(target_main):
        raise RuntimeError("G3V retarget base did not expose main()")
    target_globals = target_main.__globals__
    install_v2(target_globals)
    target_globals["main"]()


if __name__ == "__main__":
    main()
