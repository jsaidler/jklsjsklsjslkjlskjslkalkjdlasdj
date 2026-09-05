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
    return sys.argv[sys.argv.index("--") + 1:]


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


def bone_world_point(rig, bone_name, which="head"):
    pb = rig.pose.bones.get(bone_name)
    if pb is None:
        raise RuntimeError(f"Required bone missing: {bone_name}")
    p = pb.head if which == "head" else pb.tail
    return rig.matrix_world @ p


def look_at(obj, target):
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def configure_camera(camera, pitch_deg, target):
    p = math.radians(pitch_deg)
    distance = 12.0
    camera.location = (
        target.x,
        target.y - distance * math.cos(p),
        target.z + distance * math.sin(p),
    )
    look_at(camera, target)


def make_material(name, rgb):
    mat = bpy.data.materials.new(name=name)
    mat.diffuse_color = (*rgb, 1.0)
    return mat


PALETTES = {
    "skin": [
        (0.29, 0.15, 0.10),
        (0.55, 0.31, 0.20),
        (0.78, 0.54, 0.36),
    ],
    "cloth": [
        (0.25, 0.22, 0.17),
        (0.48, 0.42, 0.31),
        (0.69, 0.62, 0.47),
    ],
    "hair": [
        (0.025, 0.025, 0.032),
        (0.070, 0.070, 0.090),
        (0.135, 0.135, 0.165),
    ],
    "metal": [
        (0.18, 0.20, 0.22),
        (0.40, 0.44, 0.48),
        (0.68, 0.72, 0.76),
    ],
}


class ProxyPart:
    def __init__(self, obj, semantic):
        self.obj = obj
        self.semantic = semantic
        self.ramp = []
        for i, rgb in enumerate(PALETTES[semantic]):
            mat = make_material(f"G3_{semantic.upper()}_{i}_{obj.name}", rgb)
            obj.data.materials.append(mat)
            self.ramp.append(mat)
        obj.color = (*PALETTES[semantic][1], 1.0)


def add_segment(name, semantic, vertices=8):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=1.0, depth=2.0)
    obj = bpy.context.object
    obj.name = name
    return ProxyPart(obj, semantic)


def add_ico(name, semantic, subdivisions=1):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=subdivisions, radius=1.0)
    obj = bpy.context.object
    obj.name = name
    return ProxyPart(obj, semantic)


def set_segment(part, a, b, radius):
    obj = part.obj
    a = Vector(a)
    b = Vector(b)
    d = b - a
    length = max(d.length, 1e-5)
    obj.location = (a + b) * 0.5
    obj.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
    obj.scale = (radius, radius, length * 0.5)


def set_ellipsoid_between(part, a, b, width, depth):
    obj = part.obj
    a = Vector(a)
    b = Vector(b)
    d = b - a
    length = max(d.length, 1e-5)
    obj.location = (a + b) * 0.5
    obj.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
    obj.scale = (width, depth, length * 0.55)


def set_marker(part, p, radius):
    obj = part.obj
    obj.location = Vector(p)
    obj.rotation_euler = (0.0, 0.0, 0.0)
    obj.scale = (radius, radius, radius)


def build_proxy():
    parts = {}
    definitions = {
        "TORSO": ("segment", "cloth"),
        "L_UPPER_ARM": ("segment", "skin"),
        "L_FOREARM": ("segment", "skin"),
        "R_UPPER_ARM": ("segment", "skin"),
        "R_FOREARM": ("segment", "skin"),
        "L_THIGH": ("segment", "skin"),
        "L_SHIN": ("segment", "skin"),
        "R_THIGH": ("segment", "skin"),
        "R_SHIN": ("segment", "skin"),
        "L_FOOT": ("segment", "skin"),
        "R_FOOT": ("segment", "skin"),
        "HEAD": ("ico", "skin"),
        "HAIR": ("ico2", "hair"),
        "WRIST_L": ("ico", "metal"),
        "WRIST_R": ("ico", "metal"),
        "ANKLE_L": ("ico", "metal"),
        "ANKLE_R": ("ico", "metal"),
    }
    for name, (kind, semantic) in definitions.items():
        if kind == "segment":
            parts[name] = add_segment("G3_" + name, semantic, vertices=8)
        elif kind == "ico2":
            parts[name] = add_ico("G3_" + name, semantic, subdivisions=2)
        else:
            parts[name] = add_ico("G3_" + name, semantic, subdivisions=1)
    return parts


def body_height(rig):
    feet = [bone_world_point(rig, "LeftFoot"), bone_world_point(rig, "RightFoot")]
    top = bone_world_point(rig, "Head", "tail")
    return max(0.5, top.z - min(p.z for p in feet))


def update_proxy(rig, parts):
    h = body_height(rig)
    r_limb = h * 0.035
    r_torso = h * 0.085

    set_segment(parts["TORSO"], bone_world_point(rig, "Hips"), bone_world_point(rig, "Neck1"), r_torso)
    set_segment(parts["L_UPPER_ARM"], bone_world_point(rig, "LeftArm"), bone_world_point(rig, "LeftForeArm"), r_limb)
    set_segment(parts["L_FOREARM"], bone_world_point(rig, "LeftForeArm"), bone_world_point(rig, "LeftHand"), r_limb * 0.90)
    set_segment(parts["R_UPPER_ARM"], bone_world_point(rig, "RightArm"), bone_world_point(rig, "RightForeArm"), r_limb)
    set_segment(parts["R_FOREARM"], bone_world_point(rig, "RightForeArm"), bone_world_point(rig, "RightHand"), r_limb * 0.90)
    set_segment(parts["L_THIGH"], bone_world_point(rig, "LeftUpLeg"), bone_world_point(rig, "LeftLeg"), r_limb * 1.15)
    set_segment(parts["L_SHIN"], bone_world_point(rig, "LeftLeg"), bone_world_point(rig, "LeftFoot"), r_limb * 0.93)
    set_segment(parts["R_THIGH"], bone_world_point(rig, "RightUpLeg"), bone_world_point(rig, "RightLeg"), r_limb * 1.15)
    set_segment(parts["R_SHIN"], bone_world_point(rig, "RightLeg"), bone_world_point(rig, "RightFoot"), r_limb * 0.93)
    set_segment(parts["L_FOOT"], bone_world_point(rig, "LeftFoot"), bone_world_point(rig, "LeftToeBase"), r_limb * 0.88)
    set_segment(parts["R_FOOT"], bone_world_point(rig, "RightFoot"), bone_world_point(rig, "RightToeBase"), r_limb * 0.88)

    head_center = (bone_world_point(rig, "Head") + bone_world_point(rig, "Head", "tail")) * 0.5
    set_marker(parts["HEAD"], head_center, h * 0.075)

    # Large persistent dark mass: intentionally crude, only to test semantic hair translation.
    hair_top = bone_world_point(rig, "Head", "tail") + Vector((0.0, 0.035 * h, -0.02 * h))
    hair_bottom = bone_world_point(rig, "Spine") + Vector((0.0, 0.055 * h, -0.05 * h))
    set_ellipsoid_between(parts["HAIR"], hair_top, hair_bottom, h * 0.095, h * 0.055)

    set_marker(parts["WRIST_L"], bone_world_point(rig, "LeftHand"), h * 0.030)
    set_marker(parts["WRIST_R"], bone_world_point(rig, "RightHand"), h * 0.030)
    set_marker(parts["ANKLE_L"], bone_world_point(rig, "LeftFoot"), h * 0.032)
    set_marker(parts["ANKLE_R"], bone_world_point(rig, "RightFoot"), h * 0.032)
    bpy.context.view_layer.update()


def assign_bands(parts):
    # Fixed world-space key light. Face colors become discrete material/value decisions;
    # Workbench itself is kept flat, so no smooth lighting gradient is introduced.
    light_dir = Vector((-0.45, -0.70, 0.55)).normalized()
    for part in parts.values():
        obj = part.obj
        normal_matrix = obj.matrix_world.to_3x3()
        for poly in obj.data.polygons:
            n = (normal_matrix @ poly.normal).normalized()
            d = n.dot(light_dir)
            if d >= 0.38:
                idx = 2
            elif d >= -0.20:
                idx = 1
            else:
                idx = 0
            poly.material_index = idx


def proxy_bbox_px(scene, camera, parts):
    xs, ys = [], []
    for part in parts.values():
        obj = part.obj
        for corner in obj.bound_box:
            p = obj.matrix_world @ Vector(corner)
            co = world_to_camera_view(scene, camera, p)
            xs.append(co.x * scene.render.resolution_x)
            ys.append(co.y * scene.render.resolution_y)
    return min(xs), max(xs), min(ys), max(ys)


def calibrate_camera(scene, camera, parts, target_px):
    camera.data.ortho_scale = 5.0
    for _ in range(6):
        bpy.context.view_layer.update()
        _, _, min_y, max_y = proxy_bbox_px(scene, camera, parts)
        h = max_y - min_y
        if h <= 0:
            raise RuntimeError("G3 projected proxy height is zero")
        camera.data.ortho_scale *= h / float(target_px)
    bpy.context.view_layer.update()


def prepare_scene(scene):
    # Hide G2 diagnostic meshes but retain the baked rig/action.
    for obj in list(bpy.data.objects):
        if obj.type == "MESH":
            obj.hide_render = True

    # Remove old cameras. G3 owns its own fixed camera family.
    for obj in list(bpy.data.objects):
        if obj.type == "CAMERA":
            bpy.data.objects.remove(obj, do_unlink=True)

    try:
        scene.render.engine = "BLENDER_WORKBENCH"
    except Exception as exc:
        raise RuntimeError(f"G3 requires Blender Workbench diagnostic renderer: {exc}")

    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.display.shading.light = "FLAT"
    scene.display.shading.show_shadows = False
    scene.display.shading.show_cavity = False
    scene.display.shading.show_specular_highlight = False
    scene.display.shading.background_type = "VIEWPORT"
    scene.display.shading.background_color = (0.055, 0.062, 0.072)
    try:
        scene.display.render_aa = "OFF"
    except Exception:
        pass
    try:
        scene.view_settings.view_transform = "Standard"
        scene.view_settings.look = "None"
        scene.view_settings.exposure = 0.0
        scene.view_settings.gamma = 1.0
    except Exception:
        pass


def add_ground():
    # Simple neutral floor marker; G3 judges character translation, not environment art.
    bpy.ops.mesh.primitive_plane_add(size=20, location=(0.0, 0.0, -0.03))
    floor = bpy.context.object
    floor.name = "G3_GROUND"
    floor.color = (0.09, 0.10, 0.12, 1.0)
    mat = make_material("G3_GROUND_MAT", (0.09, 0.10, 0.12))
    floor.data.materials.append(mat)
    return floor


def main():
    output_dir = Path(get_arg("--output-dir", "")).resolve()
    g2_blend = Path(get_arg("--g2-blend", "")).resolve()
    g2_manifest_path = Path(get_arg("--g2-manifest", "")).resolve()
    pitch = float(get_arg("--pitch", "26"))
    hero_px = int(get_arg("--hero-px", "128"))

    if not g2_blend.exists():
        raise RuntimeError(f"G2 blend not found: {g2_blend}")
    if not g2_manifest_path.exists():
        raise RuntimeError(f"G2 manifest not found: {g2_manifest_path}")
    output_dir.mkdir(parents=True, exist_ok=True)

    g2_manifest = json.loads(g2_manifest_path.read_text(encoding="utf-8-sig"))
    samples = g2_manifest.get("samples", [])
    if len(samples) < 10:
        raise RuntimeError("G2 manifest has too few sequence samples for G3")
    chosen = [samples[i] for i in (0, 3, 6, 9)]
    frames = [int(s["frame"]) for s in chosen]

    bpy.ops.wm.open_mainfile(filepath=str(g2_blend))
    scene = bpy.context.scene
    rig = bpy.data.objects.get("G2_CANONICAL_RIG")
    if rig is None or rig.type != "ARMATURE":
        raise RuntimeError("G2_CANONICAL_RIG is missing from the G2 blend")

    prepare_scene(scene)
    parts = build_proxy()
    add_ground()

    bpy.ops.object.camera_add()
    camera = bpy.context.object
    camera.name = "G3_CAMERA"
    camera.data.type = "ORTHO"
    scene.camera = camera

    # Calibrate at the first approved G2 frame, then keep one fixed ortho scale for all methods/frames.
    ref_frame = frames[0]
    scene.frame_set(ref_frame)
    bpy.context.view_layer.update()
    update_proxy(rig, parts)
    root = bone_world_point(rig, "Hips")
    target = Vector((root.x, root.y, root.z + body_height(rig) * 0.43))
    scene.render.resolution_x = 640
    scene.render.resolution_y = 360
    scene.render.resolution_percentage = 100
    configure_camera(camera, pitch, target)
    calibrate_camera(scene, camera, parts, hero_px)
    locked_ortho_scale = camera.data.ortho_scale

    methods = [
        {"id": "native_flat", "label": "A native flat semantic", "resolution": [640, 360], "color_type": "OBJECT", "banded": False},
        {"id": "palette_banded", "label": "B palette-banded semantic", "resolution": [640, 360], "color_type": "MATERIAL", "banded": True},
        {"id": "palette_banded_2x", "label": "C palette-banded 2x cluster", "resolution": [320, 180], "color_type": "MATERIAL", "banded": True},
    ]

    outputs = []
    for method in methods:
        scene.render.resolution_x = method["resolution"][0]
        scene.render.resolution_y = method["resolution"][1]
        scene.render.resolution_percentage = 100
        scene.display.shading.color_type = method["color_type"]
        camera.data.ortho_scale = locked_ortho_scale

        for frame in frames:
            scene.frame_set(frame)
            bpy.context.view_layer.update()
            update_proxy(rig, parts)
            root = bone_world_point(rig, "Hips")
            target = Vector((root.x, root.y, root.z + body_height(rig) * 0.43))
            configure_camera(camera, pitch, target)
            camera.data.ortho_scale = locked_ortho_scale
            if method["banded"]:
                assign_bands(parts)

            path = output_dir / f"g3_{method['id']}_f{frame:04d}.png"
            scene.render.filepath = str(path)
            bpy.ops.render.render(write_still=True)
            if not path.exists() or path.stat().st_size == 0:
                raise RuntimeError(f"G3 render missing: {path}")
            outputs.append({
                "method": method["id"],
                "method_label": method["label"],
                "frame": frame,
                "resolution": method["resolution"],
                "file": str(path),
                "sha256": sha256_file(path),
            })

    blend_path = output_dir / "g3_pixel_translation.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))

    manifest = {
        "gate": "G3",
        "status": "REVIEW_REQUIRED",
        "purpose": "early native-grid visual-translation kill switch; generic proxy only",
        "blender_version": bpy.app.version_string,
        "source_gate": "G2",
        "source_frames": frames,
        "baseline": {
            "native_raster": [640, 360],
            "camera_pitch_deg": pitch,
            "protagonist_reference_height_px": hero_px,
            "locked_ortho_scale": locked_ortho_scale,
        },
        "semantic_materials": list(PALETTES.keys()),
        "methods": methods,
        "outputs": outputs,
        "blend": str(blend_path),
        "review_rule": "At least one non-control method must read as intentional pixel art rather than merely low-resolution 3D. Otherwise reject the visible hidden-3D translation route before Exilada production geometry.",
    }
    manifest_path = output_dir / "g3_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print("G3_PIXEL_TRANSLATION=REVIEW_REQUIRED")
    print(f"G3_FRAMES={','.join(str(f) for f in frames)}")
    print(f"G3_OUTPUTS={len(outputs)}")
    print(f"G3_MANIFEST={manifest_path}")


if __name__ == "__main__":
    main()
