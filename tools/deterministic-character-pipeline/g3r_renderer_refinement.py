import bpy
import json
import math
import hashlib
import sys
from collections import Counter
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
        (0.22, 0.105, 0.070),
        (0.40, 0.205, 0.125),
        (0.62, 0.385, 0.235),
        (0.82, 0.625, 0.420),
    ],
    "cloth": [
        (0.18, 0.155, 0.115),
        (0.32, 0.285, 0.205),
        (0.52, 0.475, 0.345),
        (0.73, 0.675, 0.505),
    ],
    "hair": [
        (0.018, 0.018, 0.024),
        (0.045, 0.045, 0.058),
        (0.080, 0.080, 0.105),
        (0.135, 0.135, 0.170),
    ],
    "metal": [
        (0.13, 0.145, 0.16),
        (0.27, 0.30, 0.33),
        (0.48, 0.53, 0.57),
        (0.76, 0.80, 0.83),
    ],
}

OUTLINE = (0.028, 0.025, 0.027)
BACKGROUND = (0.055, 0.062, 0.072)


class ProxyPart:
    def __init__(self, obj, semantic):
        self.obj = obj
        self.semantic = semantic
        self.ramp = []
        for i, rgb in enumerate(PALETTES[semantic]):
            mat = make_material(f"G3R_{semantic.upper()}_{i}_{obj.name}", rgb)
            obj.data.materials.append(mat)
            self.ramp.append(mat)
        obj.color = (*PALETTES[semantic][2], 1.0)


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
            parts[name] = add_segment("G3R_" + name, semantic, vertices=8)
        elif kind == "ico2":
            parts[name] = add_ico("G3R_" + name, semantic, subdivisions=2)
        else:
            parts[name] = add_ico("G3R_" + name, semantic, subdivisions=1)
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

    hair_top = bone_world_point(rig, "Head", "tail") + Vector((0.0, 0.035 * h, -0.02 * h))
    hair_bottom = bone_world_point(rig, "Spine") + Vector((0.0, 0.055 * h, -0.05 * h))
    set_ellipsoid_between(parts["HAIR"], hair_top, hair_bottom, h * 0.095, h * 0.055)

    set_marker(parts["WRIST_L"], bone_world_point(rig, "LeftHand"), h * 0.030)
    set_marker(parts["WRIST_R"], bone_world_point(rig, "RightHand"), h * 0.030)
    set_marker(parts["ANKLE_L"], bone_world_point(rig, "LeftFoot"), h * 0.032)
    set_marker(parts["ANKLE_R"], bone_world_point(rig, "RightFoot"), h * 0.032)
    bpy.context.view_layer.update()


def assign_bands(parts):
    light_dir = Vector((-0.45, -0.70, 0.55)).normalized()
    for part in parts.values():
        obj = part.obj
        normal_matrix = obj.matrix_world.to_3x3()
        for poly in obj.data.polygons:
            n = (normal_matrix @ poly.normal).normalized()
            d = n.dot(light_dir)
            if d >= 0.55:
                idx = 3
            elif d >= 0.15:
                idx = 2
            elif d >= -0.28:
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
            raise RuntimeError("G3R projected proxy height is zero")
        camera.data.ortho_scale *= h / float(target_px)
    bpy.context.view_layer.update()


def prepare_scene(scene):
    for obj in list(bpy.data.objects):
        if obj.type == "MESH":
            obj.hide_render = True
        elif obj.type == "CAMERA":
            bpy.data.objects.remove(obj, do_unlink=True)

    try:
        scene.render.engine = "BLENDER_WORKBENCH"
    except Exception as exc:
        raise RuntimeError(f"G3R requires Blender Workbench: {exc}")

    scene.render.resolution_x = 640
    scene.render.resolution_y = 360
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.display.shading.light = "FLAT"
    scene.display.shading.color_type = "MATERIAL"
    scene.display.shading.show_shadows = False
    scene.display.shading.show_cavity = False
    scene.display.shading.show_specular_highlight = False
    scene.display.shading.background_type = "VIEWPORT"
    scene.display.shading.background_color = BACKGROUND
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


def flat_palette():
    entries = []
    for semantic, ramp in PALETTES.items():
        for level, rgb in enumerate(ramp):
            entries.append((semantic, level, rgb))
    return entries


PALETTE_ENTRIES = flat_palette()


def color_dist2(a, b):
    return (a[0]-b[0])**2 + (a[1]-b[1])**2 + (a[2]-b[2])**2


def load_rgba(path):
    img = bpy.data.images.load(str(path), check_existing=False)
    try:
        w, h = int(img.size[0]), int(img.size[1])
        pixels = [0.0] * (w * h * 4)
        img.pixels.foreach_get(pixels)
        return w, h, pixels
    finally:
        bpy.data.images.remove(img)


def save_rgba(path, w, h, pixels):
    img = bpy.data.images.new(path.stem, width=w, height=h, alpha=True, float_buffer=False)
    try:
        img.pixels.foreach_set(pixels)
        img.filepath_raw = str(path)
        img.file_format = "PNG"
        img.save()
    finally:
        bpy.data.images.remove(img)


def pixel_rgb(pixels, idx):
    base = idx * 4
    return (pixels[base], pixels[base+1], pixels[base+2])


def put_rgb(out, idx, rgb, alpha=1.0):
    base = idx * 4
    out[base] = rgb[0]
    out[base+1] = rgb[1]
    out[base+2] = rgb[2]
    out[base+3] = alpha


def nearest_palette(rgb):
    best_i = 0
    best_d = None
    for i, (_, _, p) in enumerate(PALETTE_ENTRIES):
        d = color_dist2(rgb, p)
        if best_d is None or d < best_d:
            best_d = d
            best_i = i
    return best_i


def semantic_of_palette_index(i):
    return PALETTE_ENTRIES[i][0]


def palette_rgb(i):
    return PALETTE_ENTRIES[i][2]


def base_segmentation(w, h, pixels):
    bg = pixel_rgb(pixels, 0)
    mask = [False] * (w*h)
    pal_idx = [-1] * (w*h)
    snapped = list(pixels)
    for i in range(w*h):
        rgb = pixel_rgb(pixels, i)
        is_fg = color_dist2(rgb, bg) > 0.0014
        mask[i] = is_fg
        if is_fg:
            pi = nearest_palette(rgb)
            pal_idx[i] = pi
            put_rgb(snapped, i, palette_rgb(pi), 1.0)
        else:
            put_rgb(snapped, i, bg, 1.0)
    return bg, mask, pal_idx, snapped


def neighbors8(x, y, w, h):
    for yy in range(max(0, y-1), min(h, y+2)):
        for xx in range(max(0, x-1), min(w, x+2)):
            if xx == x and yy == y:
                continue
            yield yy*w + xx


def edge_map(mask, w, h):
    edge = [False] * (w*h)
    for y in range(h):
        for x in range(w):
            i = y*w + x
            if not mask[i]:
                continue
            for n in neighbors8(x, y, w, h):
                if not mask[n]:
                    edge[i] = True
                    break
    return edge


def add_outer_outline(bg, mask, snapped, w, h):
    out = list(snapped)
    for y in range(h):
        for x in range(w):
            i = y*w + x
            if mask[i]:
                continue
            if any(mask[n] for n in neighbors8(x, y, w, h)):
                put_rgb(out, i, OUTLINE, 1.0)
    return out


def cluster_interior(mask, edge, pal_idx, snapped, w, h):
    out = list(snapped)
    new_idx = list(pal_idx)
    for y in range(0, h-1, 2):
        for x in range(0, w-1, 2):
            ids = [y*w+x, y*w+x+1, (y+1)*w+x, (y+1)*w+x+1]
            if not all(mask[i] for i in ids):
                continue
            if any(edge[i] for i in ids):
                continue
            families = [semantic_of_palette_index(pal_idx[i]) for i in ids]
            family = Counter(families).most_common(1)[0][0]
            same_family = [pal_idx[i] for i in ids if semantic_of_palette_index(pal_idx[i]) == family]
            chosen = Counter(same_family).most_common(1)[0][0]
            for i in ids:
                new_idx[i] = chosen
                put_rgb(out, i, palette_rgb(chosen), 1.0)
    return new_idx, out


def selective_contour(bg, mask, edge, pal_idx, clustered, w, h):
    out = add_outer_outline(bg, mask, clustered, w, h)
    # Sprite-like selective contour: darken lower/right external edge pixels,
    # and allow upper/left edge pixels to keep their material color.
    for y in range(h):
        for x in range(w):
            i = y*w + x
            if not mask[i] or not edge[i]:
                continue
            right_bg = (x+1 >= w) or (not mask[y*w + (x+1)])
            lower_bg = (y-1 < 0) or (not mask[(y-1)*w + x])
            if right_bg or lower_bg:
                put_rgb(out, i, OUTLINE, 1.0)
    return out


def tiny_island_count(mask, w, h, threshold=2):
    visited = [False]*(w*h)
    tiny = 0
    for i in range(w*h):
        if visited[i] or not mask[i]:
            continue
        stack = [i]
        visited[i] = True
        count = 0
        while stack:
            cur = stack.pop()
            count += 1
            y, x = divmod(cur, w)
            for n in neighbors8(x, y, w, h):
                if mask[n] and not visited[n]:
                    visited[n] = True
                    stack.append(n)
        if count <= threshold:
            tiny += 1
    return tiny


def process_methods(base_path, output_dir, frame):
    w, h, pixels = load_rgba(base_path)
    bg, mask, pal_idx, snapped = base_segmentation(w, h, pixels)
    edge = edge_map(mask, w, h)

    methods = []

    r1 = add_outer_outline(bg, mask, snapped, w, h)
    path1 = output_dir / f"g3r_d_outlined_f{frame:04d}.png"
    save_rgba(path1, w, h, r1)
    methods.append(("outlined_4band", "D outlined 4-band", path1))

    clustered_idx, clustered = cluster_interior(mask, edge, pal_idx, snapped, w, h)
    r2 = add_outer_outline(bg, mask, clustered, w, h)
    path2 = output_dir / f"g3r_e_cluster_f{frame:04d}.png"
    save_rgba(path2, w, h, r2)
    methods.append(("edge_preserving_cluster", "E edge-preserving cluster", path2))

    r3 = selective_contour(bg, mask, edge, clustered_idx, clustered, w, h)
    path3 = output_dir / f"g3r_f_selective_f{frame:04d}.png"
    save_rgba(path3, w, h, r3)
    methods.append(("selective_contour_cluster", "F selective contour cluster", path3))

    bbox_x = []
    bbox_y = []
    for i, is_fg in enumerate(mask):
        if is_fg:
            y, x = divmod(i, w)
            bbox_x.append(x)
            bbox_y.append(y)
    metrics = {
        "foreground_pixels": int(sum(1 for v in mask if v)),
        "tiny_islands_le_2px": tiny_island_count(mask, w, h),
        "bbox": [min(bbox_x), min(bbox_y), max(bbox_x), max(bbox_y)] if bbox_x else None,
    }
    return methods, metrics


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
        raise RuntimeError("G2 manifest has too few sequence samples for G3R")
    chosen = [samples[i] for i in (0, 3, 6, 9)]
    frames = [int(s["frame"]) for s in chosen]

    bpy.ops.wm.open_mainfile(filepath=str(g2_blend))
    scene = bpy.context.scene
    rig = bpy.data.objects.get("G2_CANONICAL_RIG")
    if rig is None or rig.type != "ARMATURE":
        raise RuntimeError("G2_CANONICAL_RIG is missing from the G2 blend")

    prepare_scene(scene)
    parts = build_proxy()

    bpy.ops.object.camera_add()
    camera = bpy.context.object
    camera.name = "G3R_CAMERA"
    camera.data.type = "ORTHO"
    scene.camera = camera

    ref_frame = frames[0]
    scene.frame_set(ref_frame)
    bpy.context.view_layer.update()
    update_proxy(rig, parts)
    assign_bands(parts)
    root = bone_world_point(rig, "Hips")
    target = Vector((root.x, root.y, root.z + body_height(rig) * 0.43))
    configure_camera(camera, pitch, target)
    calibrate_camera(scene, camera, parts, hero_px)
    locked_ortho_scale = camera.data.ortho_scale

    outputs = []
    metrics = []
    base_paths = []

    for frame in frames:
        scene.frame_set(frame)
        bpy.context.view_layer.update()
        update_proxy(rig, parts)
        assign_bands(parts)
        root = bone_world_point(rig, "Hips")
        target = Vector((root.x, root.y, root.z + body_height(rig) * 0.43))
        configure_camera(camera, pitch, target)
        camera.data.ortho_scale = locked_ortho_scale

        base_path = output_dir / f"g3r_base_f{frame:04d}.png"
        scene.render.filepath = str(base_path)
        bpy.ops.render.render(write_still=True)
        if not base_path.exists() or base_path.stat().st_size == 0:
            raise RuntimeError(f"G3R base render missing: {base_path}")
        base_paths.append(base_path)

        method_outputs, frame_metrics = process_methods(base_path, output_dir, frame)
        metrics.append({"frame": frame, **frame_metrics})
        for method_id, label, path in method_outputs:
            outputs.append({
                "method": method_id,
                "method_label": label,
                "frame": frame,
                "resolution": [640, 360],
                "file": str(path),
                "sha256": sha256_file(path),
            })

    methods = [
        {"id": "outlined_4band", "label": "D outlined 4-band", "rule": "native 4-band material palette plus deterministic one-pixel external outline"},
        {"id": "edge_preserving_cluster", "label": "E edge-preserving cluster", "rule": "D plus 2x2 majority clustering only on fully interior pixels; native silhouette is preserved"},
        {"id": "selective_contour_cluster", "label": "F selective contour cluster", "rule": "E plus directional lower/right silhouette darkening to test less-uniform sprite contour"},
    ]

    blend_path = output_dir / "g3r_renderer_refinement.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))

    manifest = {
        "gate": "G3R",
        "status": "REVIEW_REQUIRED",
        "purpose": "renderer/style refinement after G3 technical viability; still generic proxy",
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
        "metrics": metrics,
        "outputs": outputs,
        "blend": str(blend_path),
        "review_rule": "At least one refined method must read as a credible intentional pixel-art production foundation at 1x gameplay scale, with stable silhouette/material separation and no generic filtered-3D look. Otherwise do not begin G4 Exilada identity geometry.",
    }
    manifest_path = output_dir / "g3r_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print("G3R_RENDERER_REFINEMENT=REVIEW_REQUIRED")
    print(f"G3R_FRAMES={','.join(str(f) for f in frames)}")
    print(f"G3R_OUTPUTS={len(outputs)}")
    print(f"G3R_MANIFEST={manifest_path}")


if __name__ == "__main__":
    main()
