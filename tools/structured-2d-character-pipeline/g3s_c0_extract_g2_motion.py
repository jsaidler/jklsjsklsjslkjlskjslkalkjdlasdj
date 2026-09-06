import bpy
import json
import sys
from pathlib import Path
from bpy_extras.object_utils import world_to_camera_view


def args_after_double_dash():
    if '--' not in sys.argv:
        return []
    return sys.argv[sys.argv.index('--') + 1:]


def arg(name, default=None):
    a = args_after_double_dash()
    for i, v in enumerate(a):
        if v == name and i + 1 < len(a):
            return a[i + 1]
    return default


def bone_point(rig, bone_name, which='head'):
    pb = rig.pose.bones.get(bone_name)
    if pb is None:
        raise RuntimeError(f'missing bone: {bone_name}')
    p = pb.head if which == 'head' else pb.tail
    return rig.matrix_world @ p


def screen_record(scene, cam, world):
    co = world_to_camera_view(scene, cam, world)
    cam_local = cam.matrix_world.inverted() @ world
    return {
        'x': float(co.x * scene.render.resolution_x),
        'y': float((1.0 - co.y) * scene.render.resolution_y),
        'depth': float(-cam_local.z),
        'world': [float(world.x), float(world.y), float(world.z)],
    }


def main():
    out_path = Path(arg('--output', '')).resolve()
    approval_path = Path(arg('--approval', '')).resolve()
    if not out_path:
        raise RuntimeError('missing --output')
    if not approval_path.is_file():
        raise RuntimeError(f'missing direction-space approval: {approval_path}')

    approval = json.loads(approval_path.read_text(encoding='utf-8-sig'))
    if approval.get('gate') != 'G3V-R' or approval.get('status') != 'PASS' or approval.get('method') != 'DIRECTION_SPACE_FK':
        raise RuntimeError('G3V-R DIRECTION_SPACE_FK approval is not PASS')
    phases = [int(x) for x in approval.get('source_frames', [])]
    if len(phases) != 4:
        raise RuntimeError('expected four validated source phase frames')
    steps = [phases[i+1] - phases[i] for i in range(3)]
    if len(set(steps)) != 1 or steps[0] <= 0:
        raise RuntimeError(f'validated phase frames are not equally spaced: {phases}')
    phase_step = steps[0]
    cycle_end = phases[0] + phase_step * 4
    sample_step = phase_step // 2
    if sample_step <= 0:
        raise RuntimeError('invalid sample step')
    sample_frames = list(range(phases[0], cycle_end, sample_step))
    if len(sample_frames) != 8:
        raise RuntimeError(f'expected 8 sample frames, got {sample_frames}')

    scene = bpy.context.scene
    rig = bpy.data.objects.get('G2_CANONICAL_RIG')
    cam = bpy.data.objects.get('G2_CAMERA') or scene.camera
    if rig is None or rig.type != 'ARMATURE':
        raise RuntimeError('G2_CANONICAL_RIG missing from G2 blend')
    if cam is None or cam.type != 'CAMERA':
        raise RuntimeError('G2_CAMERA missing from G2 blend')
    scene.camera = cam

    joint_defs = {
        'pelvis': ('Hips', 'head'),
        'neck': ('Neck1', 'head'),
        'head': ('Head', 'tail'),
        'left_shoulder': ('LeftArm', 'head'),
        'left_elbow': ('LeftForeArm', 'head'),
        'left_wrist': ('LeftHand', 'head'),
        'right_shoulder': ('RightArm', 'head'),
        'right_elbow': ('RightForeArm', 'head'),
        'right_wrist': ('RightHand', 'head'),
        'left_hip': ('LeftUpLeg', 'head'),
        'left_knee': ('LeftLeg', 'head'),
        'left_ankle': ('LeftFoot', 'head'),
        'left_toe': ('LeftToeBase', 'head'),
        'right_hip': ('RightUpLeg', 'head'),
        'right_knee': ('RightLeg', 'head'),
        'right_ankle': ('RightFoot', 'head'),
        'right_toe': ('RightToeBase', 'head'),
    }

    frames = []
    for f in sample_frames:
        scene.frame_set(f)
        bpy.context.view_layer.update()
        joints = {}
        for name, (bone, which) in joint_defs.items():
            joints[name] = screen_record(scene, cam, bone_point(rig, bone, which))
        frames.append({'frame': f, 'joints': joints})

    result = {
        'gate': 'G3S-C0',
        'revision': 'G2_PROJECTED_REAL_MOTION_8_FRAME_CYCLE_V1',
        'source_rig': 'G2_CANONICAL_RIG',
        'camera': 'G2_CAMERA',
        'source_motion': 'CMU 105_34 NormalWalk',
        'direction_space_method': 'DIRECTION_SPACE_FK',
        'validated_phase_frames': phases,
        'phase_step_source_frames': phase_step,
        'cycle_start': phases[0],
        'cycle_end_exclusive': cycle_end,
        'sample_frames': sample_frames,
        'native_raster': [int(scene.render.resolution_x), int(scene.render.resolution_y)],
        'frames': frames,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(f'G3S-C0 motion projection ready: {out_path}')
    print(f'frames: {sample_frames}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
