import bpy
import addon_utils
import json
import math
import hashlib
import sys
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view


def args_after_double_dash():
    if "--" not in sys.argv:
        return []
    return sys.argv[sys.argv.index("--") + 1 :]


def get_arg(name, default=None):
    args = args_after_double_dash()
    for i, value in enumerate(args):
        if value == name and i + 1 < len(args):
            return args[i + 1]
    return default


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def ensure_bvh_importer():
    if hasattr(bpy.types, "IMPORT_ANIM_OT_bvh"):
        return "already_registered"

    modules = addon_utils.modules(refresh=True)
    candidates = []
    for mod in modules:
        info = getattr(mod, "bl_info", {}) or {}
        name = str(info.get("name", ""))
        module_name = getattr(mod, "__name__", "")
        if module_name.endswith("io_anim_bvh") or "BioVision Motion Capture" in name or "BVH" in name:
            candidates.append(module_name)

    for module_name in candidates:
        try:
            addon_utils.enable(module_name, default_set=False, persistent=False)
        except Exception:
            continue
        if hasattr(bpy.types, "IMPORT_ANIM_OT_bvh"):
            return module_name

    # Legacy core-addon name fallback used by Blender 5.1 installations.
    try:
        addon_utils.enable("io_anim_bvh", default_set=False, persistent=False)
    except Exception:
        pass
    if hasattr(bpy.types, "IMPORT_ANIM_OT_bvh"):
        return "io_anim_bvh"

    raise RuntimeError("Blender BVH importer could not be registered in factory/headless mode")


def look_at(obj, target):
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def choose_workbench_engine(scene):
    try:
        scene.render.engine = "BLENDER_WORKBENCH"
        return scene.render.engine
    except Exception:
        for candidate in ("BLENDER_EEVEE", "BLENDER_EEVEE_NEXT"):
            try:
                scene.render.engine = candidate
                return scene.render.engine
            except Exception:
                pass
    raise RuntimeError("No supported diagnostic render engine found")


def bone_world_point(rig, bone_name, which="head"):
    pb = rig.pose.bones.get(bone_name)
    if pb is None:
        raise RuntimeError(f"Required bone missing: {bone_name}")
    p = pb.head if which == "head" else pb.tail
    return rig.matrix_world @ p


def find_straight_window(scene, rig, start_frame, end_frame, fps):
    # Find a short real-motion window with strong, straight root travel instead of guessing frame numbers.
    window = max(90, int(round(fps * 1.5)))
    window = min(window, max(30, end_frame - start_frame - 2))
    step = max(1, int(round(fps / 24.0)))
    start_step = max(15, int(round(fps * 0.25)))
    best = None

    for s in range(start_frame + 2, end_frame - window, start_step):
        points = []
        for f in range(s, s + window + 1, step):
            scene.frame_set(f)
            bpy.context.view_layer.update()
            p = bone_world_point(rig, "Hips")
            points.append(Vector((p.x, p.y, p.z)))
        if len(points) < 3:
            continue
        net_vec = points[-1] - points[0]
        net_xy = Vector((net_vec.x, net_vec.y))
        net = net_xy.length
        path = 0.0
        zmin = min(p.z for p in points)
        zmax = max(p.z for p in points)
        for a, b in zip(points[:-1], points[1:]):
            path += Vector((b.x - a.x, b.y - a.y)).length
        if path <= 1e-6:
            continue
        straightness = net / path
        score = net * (straightness ** 3) - 0.15 * (zmax - zmin)
        item = {
            "start": s,
            "end": s + window,
            "net": net,
            "path": path,
            "straightness": straightness,
            "score": score,
            "delta_xy": [net_vec.x, net_vec.y],
        }
        if best is None or item["score"] > best["score"]:
            best = item

    if best is None:
        raise RuntimeError("Could not find a usable locomotion window in the BVH")
    return best


def duplicate_and_bake_same_skeleton(scene, source, start_frame, end_frame):
    target = source.copy()
    target.data = source.data.copy()
    target.animation_data_clear()
    bpy.context.collection.objects.link(target)
    target.name = "G2_CANONICAL_RIG"
    target.data.name = "G2_CANONICAL_ARMATURE"

    action = bpy.data.actions.new("G2_CANONICAL_BAKED_ACTION")
    target.animation_data_create()
    target.animation_data.action = action

    # This first G2 spike proves deterministic source->persistent-rig baking on an identical
    # skeleton. Cross-skeleton library normalization is a later explicit validation, not implied here.
    for tpb in target.pose.bones:
        spb = source.pose.bones.get(tpb.name)
        if spb is not None:
            tpb.rotation_mode = spb.rotation_mode

    for frame in range(start_frame, end_frame + 1):
        scene.frame_set(frame)
        bpy.context.view_layer.update()
        for tpb in target.pose.bones:
            spb = source.pose.bones.get(tpb.name)
            if spb is None:
                continue
            tpb.matrix_basis = spb.matrix_basis.copy()
            tpb.keyframe_insert(data_path="location", frame=frame, group=tpb.name)
            if tpb.rotation_mode == "QUATERNION":
                tpb.keyframe_insert(data_path="rotation_quaternion", frame=frame, group=tpb.name)
            elif tpb.rotation_mode == "AXIS_ANGLE":
                tpb.keyframe_insert(data_path="rotation_axis_angle", frame=frame, group=tpb.name)
            else:
                tpb.keyframe_insert(data_path="rotation_euler", frame=frame, group=tpb.name)
            tpb.keyframe_insert(data_path="scale", frame=frame, group=tpb.name)

    scene.frame_set(start_frame)
    bpy.context.view_layer.update()
    return target, action


def add_cylinder(name, color):
    bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=1.0, depth=2.0)
    obj = bpy.context.object
    obj.name = name
    obj.color = (*color, 1.0)
    return obj


def add_sphere(name, color):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=1.0)
    obj = bpy.context.object
    obj.name = name
    obj.color = (*color, 1.0)
    return obj


def set_segment(obj, a, b, radius):
    a = Vector(a); b = Vector(b)
    d = b - a
    length = max(d.length, 1e-4)
    obj.location = (a + b) * 0.5
    obj.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
    obj.scale = (radius, radius, length * 0.5)


def set_marker(obj, p, radius):
    obj.location = p
    obj.scale = (radius, radius, radius)


def make_proxy_objects():
    center = (0.72, 0.55, 0.39)
    left = (0.20, 0.58, 0.82)
    right = (0.88, 0.38, 0.20)
    socket = (0.92, 0.78, 0.12)
    segs = {}
    definitions = {
        "TORSO": ("Hips", "Neck1", center),
        "L_UPPER_ARM": ("LeftArm", "LeftForeArm", left),
        "L_FOREARM": ("LeftForeArm", "LeftHand", left),
        "R_UPPER_ARM": ("RightArm", "RightForeArm", right),
        "R_FOREARM": ("RightForeArm", "RightHand", right),
        "L_THIGH": ("LeftUpLeg", "LeftLeg", left),
        "L_SHIN": ("LeftLeg", "LeftFoot", left),
        "R_THIGH": ("RightUpLeg", "RightLeg", right),
        "R_SHIN": ("RightLeg", "RightFoot", right),
        "L_FOOT": ("LeftFoot", "LeftToeBase", left),
        "R_FOOT": ("RightFoot", "RightToeBase", right),
    }
    for name, (a, b, color) in definitions.items():
        segs[name] = {"obj": add_cylinder("G2_" + name, color), "a": a, "b": b}
    markers = {
        "HEAD": {"obj": add_sphere("G2_HEAD", center), "bone": "Head"},
        "SOCKET_HAND_L": {"obj": add_sphere("G2_SOCKET_HAND_L", socket), "bone": "LeftHand"},
        "SOCKET_HAND_R": {"obj": add_sphere("G2_SOCKET_HAND_R", socket), "bone": "RightHand"},
        "SOCKET_FOOT_L": {"obj": add_sphere("G2_SOCKET_FOOT_L", socket), "bone": "LeftFoot"},
        "SOCKET_FOOT_R": {"obj": add_sphere("G2_SOCKET_FOOT_R", socket), "bone": "RightFoot"},
    }
    return segs, markers


def update_proxy(rig, segs, markers, body_height):
    radius = body_height * 0.032
    for item in segs.values():
        set_segment(item["obj"], bone_world_point(rig, item["a"]), bone_world_point(rig, item["b"]), radius)
    set_marker(markers["HEAD"]["obj"], bone_world_point(rig, "Head", "tail"), body_height * 0.075)
    for key in ("SOCKET_HAND_L", "SOCKET_HAND_R", "SOCKET_FOOT_L", "SOCKET_FOOT_R"):
        set_marker(markers[key]["obj"], bone_world_point(rig, markers[key]["bone"]), body_height * 0.028)
    bpy.context.view_layer.update()


def body_height(rig):
    feet = [bone_world_point(rig, "LeftFoot"), bone_world_point(rig, "RightFoot")]
    top = bone_world_point(rig, "Head", "tail")
    return max(0.5, top.z - min(p.z for p in feet))


def proxy_bbox_px(scene, camera, objects):
    xs, ys = [], []
    for obj in objects:
        for corner in obj.bound_box:
            p = obj.matrix_world @ Vector(corner)
            co = world_to_camera_view(scene, camera, p)
            xs.append(co.x * scene.render.resolution_x)
            ys.append(co.y * scene.render.resolution_y)
    return min(xs), max(xs), min(ys), max(ys)


def configure_camera(camera, pitch_deg, target):
    p = math.radians(pitch_deg)
    distance = 12.0
    camera.location = (target.x, target.y - distance * math.cos(p), target.z + distance * math.sin(p))
    look_at(camera, target)


def calibrate_camera(scene, camera, proxy_objects, target_height_px):
    camera.data.ortho_scale = 5.0
    for _ in range(5):
        bpy.context.view_layer.update()
        _, _, min_y, max_y = proxy_bbox_px(scene, camera, proxy_objects)
        h = max_y - min_y
        if h <= 0:
            raise RuntimeError("Proxy projected height is zero")
        camera.data.ortho_scale *= h / float(target_height_px)
    bpy.context.view_layer.update()


def compute_contacts(scene, rig, start_frame, end_frame):
    data = {"LeftFoot": [], "RightFoot": []}
    for f in range(start_frame, end_frame + 1):
        scene.frame_set(f)
        bpy.context.view_layer.update()
        for bone in data:
            p = bone_world_point(rig, bone)
            data[bone].append((f, p.x, p.y, p.z))

    global_ground = min(row[3] for rows in data.values() for row in rows)
    result = {}
    for bone, rows in data.items():
        contacts = []
        for i in range(1, len(rows) - 1):
            f, x, y, z = rows[i]
            _, x0, y0, z0 = rows[i - 1]
            _, x1, y1, z1 = rows[i + 1]
            speed = math.sqrt((x1-x0)**2 + (y1-y0)**2 + (z1-z0)**2) * 0.5
            if z <= global_ground + 0.08 and speed <= 0.08:
                contacts.append(f)
        result[bone] = {
            "min_z": min(r[3] for r in rows),
            "max_z": max(r[3] for r in rows),
            "contact_frame_count": len(contacts),
            "contact_frames_sample": contacts[:30],
        }
    result["ground_reference_z"] = global_ground
    return result


def main():
    output_dir = Path(get_arg("--output-dir", "")).resolve()
    bvh_path = Path(get_arg("--bvh", "")).resolve()
    pitch = float(get_arg("--pitch", "26"))
    hero_px = int(get_arg("--hero-px", "128"))
    if not output_dir:
        raise RuntimeError("Missing --output-dir")
    if not bvh_path.exists():
        raise RuntimeError(f"BVH not found: {bvh_path}")
    output_dir.mkdir(parents=True, exist_ok=True)

    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    engine = choose_workbench_engine(scene)
    scene.render.resolution_x = 640
    scene.render.resolution_y = 360
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    if engine == "BLENDER_WORKBENCH":
        scene.display.shading.light = "FLAT"
        scene.display.shading.color_type = "OBJECT"
        scene.display.shading.show_shadows = True
        scene.display.shading.show_cavity = True
        scene.display.shading.cavity_type = "BOTH"
        scene.display.shading.background_type = "WORLD"
        scene.display.shading.show_specular_highlight = False

    world = bpy.data.worlds.new("G2_WORLD")
    world.color = (0.045, 0.055, 0.07)
    scene.world = world

    importer_module = ensure_bvh_importer()
    before = set(bpy.data.objects)
    result = bpy.ops.import_anim.bvh(
        filepath=str(bvh_path),
        target="ARMATURE",
        global_scale=0.1,
        frame_start=1,
        use_fps_scale=False,
        update_scene_fps=True,
        update_scene_duration=True,
        use_cyclic=False,
        rotate_mode="NATIVE",
        axis_forward="-Z",
        axis_up="Y",
    )
    if "FINISHED" not in result:
        raise RuntimeError(f"BVH import failed: {result}")

    new_armatures = [o for o in set(bpy.data.objects) - before if o.type == "ARMATURE"]
    source = new_armatures[0] if new_armatures else bpy.context.object
    if source is None or source.type != "ARMATURE":
        raise RuntimeError("Imported BVH armature was not found")
    source.name = "G2_SOURCE_BVH"

    required_bones = [
        "Hips", "Spine1", "Neck1", "Head",
        "LeftArm", "LeftForeArm", "LeftHand", "RightArm", "RightForeArm", "RightHand",
        "LeftUpLeg", "LeftLeg", "LeftFoot", "LeftToeBase",
        "RightUpLeg", "RightLeg", "RightFoot", "RightToeBase",
    ]
    missing = [b for b in required_bones if source.pose.bones.get(b) is None]
    if missing:
        raise RuntimeError("Required BVH bones missing: " + ", ".join(missing))

    action = source.animation_data.action if source.animation_data else None
    if action is None:
        raise RuntimeError("Imported BVH has no action")
    full_start = int(math.floor(action.frame_range[0]))
    full_end = int(math.ceil(action.frame_range[1]))
    fps = float(scene.render.fps) / float(scene.render.fps_base)
    window = find_straight_window(scene, source, full_start, full_end, fps)
    clip_start, clip_end = int(window["start"]), int(window["end"])

    target, baked_action = duplicate_and_bake_same_skeleton(scene, source, clip_start, clip_end)
    source.hide_set(True)
    source.hide_render = True

    # Align selected root travel to +X so the accepted belt-scroller camera sees lateral locomotion.
    scene.frame_set(clip_start); bpy.context.view_layer.update()
    start_local = target.pose.bones["Hips"].head.copy()
    scene.frame_set(clip_end); bpy.context.view_layer.update()
    end_local = target.pose.bones["Hips"].head.copy()
    d = end_local - start_local
    target.rotation_euler[2] = -math.atan2(d.y, d.x)
    bpy.context.view_layer.update()

    # Put lowest foot contact on z=0 for diagnostics.
    min_foot_z = 1e9
    scan_step = max(1, int(round(fps / 30.0)))
    for f in range(clip_start, clip_end + 1, scan_step):
        scene.frame_set(f); bpy.context.view_layer.update()
        min_foot_z = min(min_foot_z, bone_world_point(target, "LeftFoot").z, bone_world_point(target, "RightFoot").z)
    target.location.z -= min_foot_z
    bpy.context.view_layer.update()

    segs, markers = make_proxy_objects()
    proxy_objects = [v["obj"] for v in segs.values()] + [v["obj"] for v in markers.values()]

    # Ground band/grid.
    bpy.ops.mesh.primitive_plane_add(size=24, location=(0, 0, -0.02))
    ground = bpy.context.object
    ground.name = "G2_GROUND"
    ground.color = (0.10, 0.11, 0.13, 1.0)
    for y in (-2, -1, 0, 1, 2):
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, y, 0.0))
        line = bpy.context.object
        line.name = f"G2_DEPTH_LINE_{y:+d}"
        line.scale = (8.0, 0.025, 0.012)
        line.color = (0.22, 0.23, 0.25, 1.0)

    bpy.ops.object.camera_add()
    camera = bpy.context.object
    camera.name = "G2_CAMERA"
    camera.data.type = "ORTHO"
    scene.camera = camera

    mid = (clip_start + clip_end) // 2
    scene.frame_set(mid); bpy.context.view_layer.update()
    h = body_height(target)
    update_proxy(target, segs, markers, h)
    hips = bone_world_point(target, "Hips")
    configure_camera(camera, pitch, Vector((hips.x, hips.y, hips.z + h * 0.35)))
    calibrate_camera(scene, camera, proxy_objects, hero_px)

    # Render 12 samples across the automatically selected real-motion window.
    sample_count = 12
    sample_frames = []
    for i in range(sample_count):
        t = i / float(sample_count - 1)
        f = int(round(clip_start + (clip_end - clip_start) * t))
        scene.frame_set(f); bpy.context.view_layer.update()
        h_now = body_height(target)
        update_proxy(target, segs, markers, h_now)
        hips_now = bone_world_point(target, "Hips")
        configure_camera(camera, pitch, Vector((hips_now.x, hips_now.y, hips_now.z + h_now * 0.35)))
        path = output_dir / f"g2_frame_{i:02d}_f{f:04d}.png"
        scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        if not path.exists() or path.stat().st_size == 0:
            raise RuntimeError(f"Missing G2 frame: {path}")
        sample_frames.append({
            "index": i,
            "frame": f,
            "time_sec_from_clip_start": round((f - clip_start) / fps, 4),
            "file": str(path),
            "sha256": sha256_file(path),
        })

    contacts = compute_contacts(scene, target, clip_start, clip_end)

    scene.frame_set(clip_start); bpy.context.view_layer.update()
    root_start = bone_world_point(target, "Hips")
    scene.frame_set(clip_end); bpy.context.view_layer.update()
    root_end = bone_world_point(target, "Hips")
    root_delta = root_end - root_start

    blend_path = output_dir / "g2_motion_topology.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))

    manifest = {
        "gate": "G2",
        "status": "REVIEW_REQUIRED",
        "purpose": "real captured locomotion + persistent rig/topology/socket validation",
        "blender_version": bpy.app.version_string,
        "render_engine": engine,
        "bvh_importer_module": importer_module,
        "source": {
            "dataset": "CMU Graphics Lab Motion Capture Database - BVH conversion by Bruce Hahne",
            "trial": "105_34 NormalWalk",
            "file": str(bvh_path),
            "sha256": sha256_file(bvh_path),
            "full_frame_range": [full_start, full_end],
            "fps": fps,
        },
        "baseline": {
            "native_raster": [640, 360],
            "camera_pitch_deg": pitch,
            "protagonist_reference_height_px": hero_px,
        },
        "selected_clip": {
            "start_frame": clip_start,
            "end_frame": clip_end,
            "duration_sec": round((clip_end - clip_start) / fps, 4),
            "straightness": round(window["straightness"], 6),
            "source_root_net_distance": round(window["net"], 6),
            "source_root_path_distance": round(window["path"], 6),
            "baked_root_delta_world": [round(root_delta.x, 6), round(root_delta.y, 6), round(root_delta.z, 6)],
        },
        "canonical_rig": {
            "name": target.name,
            "bone_count": len(target.pose.bones),
            "required_bones": required_bones,
            "missing_required_bones": [],
            "baked_action": baked_action.name,
            "retarget_scope": "identical-skeleton persistent baked clone for G2 motion/topology validation; cross-skeleton library normalization remains a separate explicit validation before production scaling",
        },
        "stable_sockets": ["LeftHand", "RightHand", "LeftFoot", "RightFoot"],
        "contacts": contacts,
        "samples": sample_frames,
        "blend": str(blend_path),
    }
    manifest_path = output_dir / "g2_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print("G2_MOTION_TOPOLOGY=REVIEW_REQUIRED")
    print(f"G2_CLIP={clip_start}:{clip_end}")
    print(f"G2_FPS={fps}")
    print(f"G2_STRAIGHTNESS={window['straightness']:.6f}")
    print(f"G2_MANIFEST={manifest_path}")


if __name__ == "__main__":
    main()
