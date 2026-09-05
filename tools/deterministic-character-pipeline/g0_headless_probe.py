import bpy
import json
import math
import hashlib
import sys
from pathlib import Path
from mathutils import Vector


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


def make_material(name, color, metallic=0.0, roughness=0.6):
    mat = bpy.data.materials.new(name=name)
    mat.diffuse_color = (*color, 1.0)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf is not None:
        bsdf.inputs["Base Color"].default_value = (*color, 1.0)
        bsdf.inputs["Metallic"].default_value = metallic
        bsdf.inputs["Roughness"].default_value = roughness
    return mat


def select_eevee_engine(scene):
    """Select the Eevee identifier valid for the running Blender version.

    Blender 4.2 used BLENDER_EEVEE_NEXT; Blender 5.0 changed the identifier
    back to BLENDER_EEVEE. Probe the runtime instead of hard-coding a version
    boundary so the headless gate survives both families.
    """
    errors = []
    for candidate in ("BLENDER_EEVEE", "BLENDER_EEVEE_NEXT"):
        try:
            scene.render.engine = candidate
            return candidate
        except (TypeError, ValueError) as exc:
            errors.append(f"{candidate}: {exc}")
    raise RuntimeError("No supported Eevee render-engine identifier found: " + " | ".join(errors))


def main():
    output_arg = get_arg("--output-dir")
    if not output_arg:
        raise RuntimeError("Missing --output-dir")
    output_dir = Path(output_arg).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    # Factory-clean scene so the result never depends on a user's Blender file/configuration.
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene

    # Use the local real-time renderer only as an automation probe. This is NOT the planned pixel renderer.
    engine = select_eevee_engine(scene)
    scene.render.resolution_x = 320
    scene.render.resolution_y = 180
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.render.filepath = str(output_dir / "g0_probe.png")

    # Stable color-management baseline for diagnostics.
    try:
        scene.view_settings.look = "Medium High Contrast"
    except Exception:
        pass

    world = bpy.data.worlds.new("G0_WORLD")
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    bg.inputs["Color"].default_value = (0.035, 0.045, 0.06, 1.0)
    bg.inputs["Strength"].default_value = 0.35
    scene.world = world

    mat_floor = make_material("MAT_FLOOR", (0.11, 0.13, 0.15), roughness=0.95)
    mat_cube = make_material("MAT_CUBE", (0.34, 0.11, 0.08), roughness=0.55)
    mat_sphere = make_material("MAT_SPHERE", (0.10, 0.23, 0.36), metallic=0.15, roughness=0.4)
    mat_marker = make_material("MAT_SOCKET_MARKER", (0.55, 0.42, 0.08), metallic=0.7, roughness=0.3)

    bpy.ops.mesh.primitive_plane_add(size=14, location=(0, 0, 0))
    floor = bpy.context.object
    floor.name = "G0_FLOOR"
    floor.data.materials.append(mat_floor)

    bpy.ops.mesh.primitive_cube_add(size=2.0, location=(-1.35, 0, 1.0))
    cube = bpy.context.object
    cube.name = "G0_BODY_PROXY"
    cube.data.materials.append(mat_cube)

    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, radius=1.05, location=(1.35, 0.25, 1.05))
    sphere = bpy.context.object
    sphere.name = "G0_PROP_PROXY"
    sphere.data.materials.append(mat_sphere)

    # A named attachment/socket marker proves that semantic scene objects can be created and recorded headlessly.
    bpy.ops.object.empty_add(type="PLAIN_AXES", location=(-0.45, 0.0, 1.5))
    socket = bpy.context.object
    socket.name = "SOCKET_TEST_L"
    socket.empty_display_size = 0.25

    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=0.14, location=socket.location)
    marker = bpy.context.object
    marker.name = "G0_SOCKET_VISIBLE_MARKER"
    marker.data.materials.append(mat_marker)

    bpy.ops.object.light_add(type="AREA", location=(1.5, -3.0, 6.0))
    key = bpy.context.object
    key.name = "G0_KEY_LIGHT"
    key.data.energy = 950
    key.data.shape = "DISK"
    key.data.size = 5.0
    look_at(key, (0, 0, 0.7))

    bpy.ops.object.light_add(type="AREA", location=(-4.0, 2.0, 3.0))
    fill = bpy.context.object
    fill.name = "G0_FILL_LIGHT"
    fill.data.energy = 350
    fill.data.size = 4.0
    look_at(fill, (0, 0, 1.0))

    bpy.ops.object.camera_add(location=(7.2, -10.5, 6.5))
    camera = bpy.context.object
    camera.name = "G0_CAMERA"
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = 7.4
    look_at(camera, (0, 0, 0.8))
    scene.camera = camera

    png_path = output_dir / "g0_probe.png"
    blend_path = output_dir / "g0_probe.blend"
    manifest_path = output_dir / "g0_manifest.json"

    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))
    bpy.ops.render.render(write_still=True)

    if not png_path.exists() or png_path.stat().st_size == 0:
        raise RuntimeError("Blender completed but diagnostic PNG was not created")

    manifest = {
        "gate": "G0",
        "status": "PASS",
        "purpose": "headless Blender automation probe only; not final visual rendering",
        "blender_version": bpy.app.version_string,
        "python_version": sys.version.split()[0],
        "render_engine": engine,
        "resolution": [scene.render.resolution_x, scene.render.resolution_y],
        "camera": {
            "name": camera.name,
            "type": camera.data.type,
            "ortho_scale": camera.data.ortho_scale,
            "location": list(camera.location),
        },
        "semantic_objects": [
            "G0_BODY_PROXY",
            "G0_PROP_PROXY",
            "SOCKET_TEST_L",
            "G0_SOCKET_VISIBLE_MARKER",
        ],
        "outputs": {
            "png": str(png_path),
            "blend": str(blend_path),
        },
        "png_sha256": sha256_file(png_path),
    }

    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print("G0_HEADLESS_PROBE=PASS")
    print(f"G0_ENGINE={engine}")
    print(f"G0_PNG={png_path}")
    print(f"G0_MANIFEST={manifest_path}")
    print(f"G0_SHA256={manifest['png_sha256']}")


if __name__ == "__main__":
    main()
