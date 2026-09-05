import math
from statistics import median

import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view


SEMANTIC_SKIN = "skin"


def _bone_world(rig, name, tail=False):
    pb = rig.pose.bones.get(name)
    if pb is None:
        raise RuntimeError("G3V geometry patch missing bone: " + name)
    p = pb.tail if tail else pb.head
    return rig.matrix_world @ p


def _skeleton_height(rig):
    head = _bone_world(rig, "Head", True)
    left = _bone_world(rig, "LeftFoot")
    right = _bone_world(rig, "RightFoot")
    vertical = head.z - min(left.z, right.z)
    if vertical <= 1e-5:
        feet = (left + right) * 0.5
        vertical = (head - feet).length
    return max(0.5, float(vertical))


def _cluster_centers(frames):
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


def _derive_gait_period(meta):
    contacts = meta.get("contacts", {})
    source = meta.get("source", {})
    fps = float(source.get("fps", 120.0))
    min_period = max(12, int(round(fps * 0.25)))
    max_period = max(min_period + 1, int(round(fps * 1.20)))

    centers_by_side = {}
    period_candidates = []
    for side in ("LeftFoot", "RightFoot"):
        frames = contacts.get(side, {}).get("contact_frames_sample", [])
        centers = _cluster_centers(frames)
        centers_by_side[side] = centers
        for a, b in zip(centers[:-1], centers[1:]):
            d = b - a
            if min_period <= d <= max_period:
                period_candidates.append(d)

    if period_candidates:
        return float(median(period_candidates)), centers_by_side

    combined = sorted(centers_by_side.get("LeftFoot", []) + centers_by_side.get("RightFoot", []))
    half_candidates = []
    for a, b in zip(combined[:-1], combined[1:]):
        d = b - a
        if max(6, min_period // 3) <= d <= max_period // 2 + 4:
            half_candidates.append(d)
    if half_candidates:
        return float(median(half_candidates) * 2.0), centers_by_side

    raise RuntimeError(
        "G3V could not derive a gait period from G2 contact metadata; refusing fixed-index phase guessing"
    )


def _phase_frames_from_meta(meta):
    clip = meta.get("selected_clip", {})
    clip_start = int(clip.get("start_frame", 0))
    clip_end = int(clip.get("end_frame", 0))
    if clip_end <= clip_start:
        raise RuntimeError("G3V G2 manifest has invalid selected_clip frame range")

    period, centers_by_side = _derive_gait_period(meta)
    if period < 8:
        raise RuntimeError("G3V derived implausibly short gait period: " + str(period))

    possible_bases = centers_by_side.get("LeftFoot", []) + centers_by_side.get("RightFoot", [])
    possible_bases = [f for f in sorted(possible_bases) if clip_start <= f <= clip_end]
    base = None
    for candidate in possible_bases:
        if candidate + period * 0.75 <= clip_end:
            base = float(candidate)
            break
    if base is None:
        base = float(clip_start)
        if base + period * 0.75 > clip_end:
            base = float(clip_end) - period * 0.75

    frames = [int(round(base + period * q)) for q in (0.0, 0.25, 0.50, 0.75)]
    frames = [max(clip_start, min(clip_end, f)) for f in frames]
    if len(set(frames)) != 4:
        raise RuntimeError("G3V contact-derived phase selection did not produce four unique frames: " + repr(frames))

    print("G3V_PHASE_SELECTION=CONTACT_DERIVED_QUARTER_CYCLE")
    print(f"G3V_DERIVED_GAIT_PERIOD_FRAMES={period:.3f}")
    print("G3V_PHASE_FRAMES=" + ",".join(str(f) for f in frames))
    return frames


class _JsonPhaseProxy:
    def __init__(self, original):
        self._original = original
        self._patched_manifest = False

    def loads(self, text, *args, **kwargs):
        data = self._original.loads(text, *args, **kwargs)
        if (
            not self._patched_manifest
            and isinstance(data, dict)
            and data.get("gate") == "G2"
            and isinstance(data.get("samples"), list)
            and len(data["samples"]) >= 10
            and isinstance(data.get("selected_clip"), dict)
        ):
            frames = _phase_frames_from_meta(data)
            samples = [dict(item) for item in data["samples"]]
            for slot, frame in zip((0, 3, 6, 9), frames):
                samples[slot]["frame"] = int(frame)
            data["samples"] = samples
            self._patched_manifest = True
        return data

    def __getattr__(self, name):
        return getattr(self._original, name)


def install_geometry_phase_fixes(target_globals):
    required = (
        "bbox_world", "calibrate_camera", "add_shackle", "add_material", "tag_semantic",
        "parent_bone", "PALETTES", "json", "main",
    )
    missing = [name for name in required if name not in target_globals]
    if missing:
        raise RuntimeError("G3V geometry/phase patch missing target symbols: " + ", ".join(missing))

    original_bbox_world = target_globals["bbox_world"]
    add_material = target_globals["add_material"]
    tag_semantic = target_globals["tag_semantic"]
    parent_bone = target_globals["parent_bone"]
    palettes = target_globals["PALETTES"]

    def stabilized_bbox_world(objects):
        lo, hi = original_bbox_world(objects)
        if len(objects) == 1 and objects[0].get("g3v_semantic") == SEMANTIC_SKIN:
            rig = bpy.data.objects.get("G3V_CMU_RIG")
            if rig is not None and rig.type == "ARMATURE":
                h = _skeleton_height(rig)
                center_z = (lo.z + hi.z) * 0.5
                geometry_h = max(1e-6, hi.z - lo.z)
                print(f"G3V_BODY_GEOMETRY_HEIGHT={geometry_h:.6f}")
                print(f"G3V_SKELETON_HEIGHT={h:.6f}")
                return (
                    Vector((lo.x, lo.y, center_z - h * 0.5)),
                    Vector((hi.x, hi.y, center_z + h * 0.5)),
                )
        return lo, hi

    target_globals["bbox_world"] = stabilized_bbox_world

    def skeleton_calibrate_camera(scene, camera, objects, target_px):
        rig = bpy.data.objects.get("G3V_CMU_RIG")
        if rig is None or rig.type != "ARMATURE":
            raise RuntimeError("G3V skeleton camera calibration could not locate G3V_CMU_RIG")
        camera.data.ortho_scale = 5.0
        for _ in range(7):
            bpy.context.view_layer.update()
            points = [
                _bone_world(rig, "Head", True),
                _bone_world(rig, "LeftFoot"),
                _bone_world(rig, "RightFoot"),
            ]
            ys = [world_to_camera_view(scene, camera, p).y * scene.render.resolution_y for p in points]
            height_px = max(ys) - min(ys)
            if height_px <= 0.01:
                raise RuntimeError("G3V projected skeleton height is zero")
            camera.data.ortho_scale *= height_px / float(target_px)
        bpy.context.view_layer.update()
        print("G3V_CAMERA_CALIBRATION=SKELETON_HEAD_FOOT")

    target_globals["calibrate_camera"] = skeleton_calibrate_camera

    parent_map = {
        "LeftHand": "LeftForeArm",
        "RightHand": "RightForeArm",
        "LeftFoot": "LeftLeg",
        "RightFoot": "RightLeg",
    }

    def oriented_shackle(name, center, radius, semantic, rig, bone):
        parent_name = parent_map.get(bone)
        axis = Vector((0.0, 0.0, 1.0))
        if parent_name and rig.pose.bones.get(parent_name) is not None:
            axis = _bone_world(rig, bone) - _bone_world(rig, parent_name)
            if axis.length <= 1e-6:
                axis = Vector((0.0, 0.0, 1.0))
        axis.normalize()
        major = float(radius) * 1.45
        rotation = Vector((0.0, 0.0, 1.0)).rotation_difference(axis).to_euler()
        bpy.ops.mesh.primitive_torus_add(
            major_radius=major,
            minor_radius=major * 0.22,
            major_segments=12,
            minor_segments=5,
            location=center,
            rotation=rotation,
        )
        obj = bpy.context.object
        obj.name = name
        add_material(obj, palettes[semantic][2], name + "_MAT")
        tag_semantic(obj, semantic)
        parent_bone(obj, rig, bone)
        return obj

    target_globals["add_shackle"] = oriented_shackle

    original_json = target_globals["json"]
    target_globals["json"] = _JsonPhaseProxy(original_json)

    if target_globals["bbox_world"] is not stabilized_bbox_world:
        raise RuntimeError("G3V stabilized bbox patch did not bind")
    if target_globals["calibrate_camera"] is not skeleton_calibrate_camera:
        raise RuntimeError("G3V skeleton camera patch did not bind")
    if target_globals["add_shackle"] is not oriented_shackle:
        raise RuntimeError("G3V shackle geometry patch did not bind")

    print("G3V_GEOMETRY_SCALE=SKELETON_DERIVED")
    print("G3V_SHACKLES=ORIENTED_OVERSURFACE_CUFFS")
