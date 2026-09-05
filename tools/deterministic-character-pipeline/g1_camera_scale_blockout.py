import bpy
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


def look_at(obj, target):
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def set_object_color(obj, rgb):
    obj.color = (*rgb, 1.0)


def add_box(name, location, scale, color, parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    set_object_color(obj, color)
    if parent:
        obj.parent = parent
    return obj


def add_sphere(name, location, radius, color, parent=None):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=radius, location=location)
    obj = bpy.context.object
    obj.name = name
    set_object_color(obj, color)
    if parent:
        obj.parent = parent
    return obj


def add_proxy(name, origin, color, protagonist=False):
    root = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(root)
    root.location = origin

    # Overall world-space height ~2.0 units. Deliberately simple: G1 tests framing, not art.
    add_box(name + "_TORSO", (origin[0], origin[1], 1.25), (0.32, 0.18, 0.48), color, root)
    add_sphere(name + "_HEAD", (origin[0], origin[1], 1.92), 0.23, color, root)
    add_box(name + "_LEG_L", (origin[0]-0.16, origin[1], 0.48), (0.12, 0.12, 0.48), color, root)
    add_box(name + "_LEG_R", (origin[0]+0.16, origin[1], 0.48), (0.12, 0.12, 0.48), color, root)
    add_box(name + "_ARM_L", (origin[0]-0.43, origin[1], 1.25), (0.10, 0.10, 0.48), color, root)
    add_box(name + "_ARM_R", (origin[0]+0.43, origin[1], 1.25), (0.10, 0.10, 0.48), color, root)

    if protagonist:
        # Large dark hair-like mass to make the protagonist silhouette non-generic even in the blockout.
        add_box(name + "_HAIR_MASS", (origin[0], origin[1]+0.06, 1.48), (0.39, 0.13, 0.65), (0.055,0.055,0.07), root)
        # Re-create head in front of the hair mass as a lighter readable face/head marker.
        add_sphere(name + "_FACE_MARKER", (origin[0], origin[1]-0.03, 1.92), 0.19, color, root)
    return root


def add_ground_strip(y_center, depth, color):
    add_box(
        f"GROUND_STRIP_{y_center:+.2f}",
        (0, y_center, -0.055),
        (7.5, depth / 2.0, 0.05),
        color,
    )


def add_reach_overlay(origin):
    # Lateral attack reach bars and depth envelope; diagnostic only.
    c = (0.92, 0.62, 0.08)
    add_box("REACH_FORWARD", (origin[0]+1.15, origin[1], 0.015), (1.15, 0.035, 0.015), c)
    add_box("REACH_BACK", (origin[0]-0.65, origin[1], 0.015), (0.65, 0.035, 0.015), c)
    add_box("DEPTH_FRONT", (origin[0], origin[1]-0.70, 0.014), (1.0, 0.025, 0.014), c)
    add_box("DEPTH_BACK", (origin[0], origin[1]+0.70, 0.014), (1.0, 0.025, 0.014), c)


def descendant_meshes(root):
    return [o for o in root.children_recursive if o.type == "MESH"]


def projected_bbox_px(scene, camera, objects):
    xs, ys = [], []
    for obj in objects:
        for corner in obj.bound_box:
            world = obj.matrix_world @ Vector(corner)
            co = world_to_camera_view(scene, camera, world)
            xs.append(co.x * scene.render.resolution_x)
            ys.append(co.y * scene.render.resolution_y)
    return {
        "min_x": min(xs), "max_x": max(xs), "min_y": min(ys), "max_y": max(ys),
        "width": max(xs)-min(xs), "height": max(ys)-min(ys),
    }


def configure_camera(camera, pitch_deg, target=(0, 0, 0.95)):
    p = math.radians(pitch_deg)
    distance = 12.0
    camera.location = (0.0, target[1] - distance * math.cos(p), target[2] + distance * math.sin(p))
    look_at(camera, target)


def calibrate_ortho_for_height(scene, camera, objects, target_px):
    camera.data.ortho_scale = 5.0
    for _ in range(3):
        bbox = projected_bbox_px(scene, camera, objects)
        if bbox["height"] <= 0:
            raise RuntimeError("Projected protagonist height is zero")
        camera.data.ortho_scale *= bbox["height"] / float(target_px)
    return projected_bbox_px(scene, camera, objects)


def choose_workbench_engine(scene):
    try:
        scene.render.engine = "BLENDER_WORKBENCH"
        return scene.render.engine
    except Exception:
        # Eevee fallback if a future Blender build removes Workbench from background rendering.
        for candidate in ("BLENDER_EEVEE", "BLENDER_EEVEE_NEXT"):
            try:
                scene.render.engine = candidate
                return scene.render.engine
            except Exception:
                pass
    raise RuntimeError("No supported diagnostic render engine found")


def main():
    output_dir = Path(get_arg("--output-dir", "")).resolve()
    if not str(output_dir):
        raise RuntimeError("Missing --output-dir")
    output_dir.mkdir(parents=True, exist_ok=True)

    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    engine = choose_workbench_engine(scene)
    scene.render.resolution_x = 640
    scene.render.resolution_y = 360
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False

    # Workbench configuration when available.
    if engine == "BLENDER_WORKBENCH":
        scene.display.shading.light = "FLAT"
        scene.display.shading.color_type = "OBJECT"
        scene.display.shading.show_shadows = True
        scene.display.shading.show_cavity = True
        scene.display.shading.cavity_type = "BOTH"
        scene.display.shading.background_type = "WORLD"
        scene.display.shading.show_specular_highlight = False

    world = bpy.data.worlds.new("G1_WORLD")
    world.color = (0.055, 0.065, 0.08)
    scene.world = world

    # Walkable band, deliberately subdivided to show depth ordering and usable Y-space.
    strips = [
        (-2.0, 1.0, (0.12,0.13,0.15)),
        (-1.0, 1.0, (0.15,0.16,0.18)),
        ( 0.0, 1.0, (0.18,0.19,0.20)),
        ( 1.0, 1.0, (0.15,0.16,0.18)),
        ( 2.0, 1.0, (0.12,0.13,0.15)),
    ]
    for y, d, c in strips:
        add_ground_strip(y, d, c)

    hero_color = (0.73, 0.43, 0.28)
    enemy_color = (0.23, 0.33, 0.40)
    hero_origin = (0.0, -0.25, 0.0)
    hero = add_proxy("PROTAGONIST_PROXY", hero_origin, hero_color, protagonist=True)
    enemy_positions = [(-4.3,1.3,0),( -2.8,-1.55,0),(2.1,1.55,0),(3.5,-0.75,0),(5.0,0.65,0)]
    for i, pos in enumerate(enemy_positions, start=1):
        add_proxy(f"ENEMY_{i:02d}", pos, enemy_color, protagonist=False)
    add_reach_overlay(hero_origin)

    # Side markers roughly indicating exits/architecture margins.
    add_box("LEFT_BOUNDARY", (-6.7, 0, 0.8), (0.10, 2.5, 0.8), (0.35,0.17,0.16))
    add_box("RIGHT_BOUNDARY", (6.7, 0, 0.8), (0.10, 2.5, 0.8), (0.35,0.17,0.16))

    bpy.ops.object.camera_add()
    camera = bpy.context.object
    camera.name = "G1_CAMERA"
    camera.data.type = "ORTHO"
    scene.camera = camera

    hero_meshes = descendant_meshes(hero)
    pitches = [18, 26, 34]
    target_heights = [112, 128, 144]
    candidates = []

    for pitch in pitches:
        configure_camera(camera, pitch)
        for target_px in target_heights:
            bbox = calibrate_ortho_for_height(scene, camera, hero_meshes, target_px)
            filename = f"g1_pitch{pitch:02d}_h{target_px}.png"
            path = output_dir / filename
            scene.render.filepath = str(path)
            bpy.ops.render.render(write_still=True)
            if not path.exists() or path.stat().st_size == 0:
                raise RuntimeError(f"Missing render: {path}")
            candidates.append({
                "pitch_deg": pitch,
                "target_height_px": target_px,
                "measured_height_px": round(bbox["height"], 2),
                "measured_width_px": round(bbox["width"], 2),
                "ortho_scale": camera.data.ortho_scale,
                "camera_location": [round(v,6) for v in camera.location],
                "file": str(path),
                "sha256": sha256_file(path),
            })

    blend_path = output_dir / "g1_blockout.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))

    manifest = {
        "gate": "G1",
        "status": "REVIEW_REQUIRED",
        "purpose": "camera/native-scale composition comparison; not final art",
        "blender_version": bpy.app.version_string,
        "render_engine": engine,
        "native_raster": [640,360],
        "pitches_deg": pitches,
        "target_protagonist_heights_px": target_heights,
        "walkable_depth_world": 5.0,
        "enemy_count": 5,
        "candidate_count": len(candidates),
        "candidates": candidates,
        "blend": str(blend_path),
    }
    manifest_path = output_dir / "g1_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print("G1_BLOCKOUT=REVIEW_REQUIRED")
    print(f"G1_CANDIDATES={len(candidates)}")
    print(f"G1_MANIFEST={manifest_path}")


if __name__ == "__main__":
    main()
