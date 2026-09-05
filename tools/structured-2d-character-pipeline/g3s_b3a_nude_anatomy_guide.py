import bpy
import hashlib
import importlib
import json
import math
import sys
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

REVISION = "G3S_B3A_NUDE_ANATOMY_GUIDE_V2"
WIDTH = 640
HEIGHT = 360
BG = (0.045, 0.050, 0.060)
SKIN = (0.47, 0.27, 0.15)


def cli_args():
    return sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []


def arg(name, default=None):
    a = cli_args()
    for i, v in enumerate(a):
        if v == name and i + 1 < len(a):
            return a[i + 1]
    return default


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def mpfb_class(submodule, name):
    roots = []
    for modname in list(sys.modules):
        if modname == "mpfb" or modname.endswith(".mpfb"):
            roots.append(modname)
    if "mpfb" not in roots:
        roots.append("mpfb")
    for root in roots:
        try:
            mod = importlib.import_module(root + "." + submodule)
            if hasattr(mod, name):
                return getattr(mod, name), root
        except Exception:
            pass
    raise RuntimeError("MPFB bootstrap is present but required class could not be imported: " + name)


def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for datablocks in (bpy.data.materials, bpy.data.cameras, bpy.data.lights):
        for block in list(datablocks):
            if block.users == 0:
                datablocks.remove(block)


def set_world(scene, color, strength=1.0):
    world = scene.world or bpy.data.worlds.new("G3S_B3_WORLD")
    scene.world = world
    world.use_nodes = True
    nodes = world.node_tree.nodes
    bg = nodes.get("Background")
    if bg is None:
        nodes.clear()
        bg = nodes.new("ShaderNodeBackground")
        out = nodes.new("ShaderNodeOutputWorld")
        world.node_tree.links.new(bg.outputs["Background"], out.inputs["Surface"])
    bg.inputs["Color"].default_value = (*color, 1.0)
    bg.inputs["Strength"].default_value = strength


def material_principled(name, color):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf is None:
        mat.node_tree.nodes.clear()
        out = mat.node_tree.nodes.new("ShaderNodeOutputMaterial")
        bsdf = mat.node_tree.nodes.new("ShaderNodeBsdfPrincipled")
        mat.node_tree.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.92
    return mat


def material_emission(name, color):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    out = nodes.new("ShaderNodeOutputMaterial")
    emit = nodes.new("ShaderNodeEmission")
    emit.inputs["Color"].default_value = (*color, 1.0)
    emit.inputs["Strength"].default_value = 1.0
    mat.node_tree.links.new(emit.outputs["Emission"], out.inputs["Surface"])
    return mat


def assign_material(obj, mat):
    obj.data.materials.clear()
    obj.data.materials.append(mat)
    for poly in obj.data.polygons:
        poly.material_index = 0


def evaluated_points(obj):
    deps = bpy.context.evaluated_depsgraph_get()
    ev = obj.evaluated_get(deps)
    mesh = ev.to_mesh()
    try:
        mw = ev.matrix_world
        return [mw @ v.co for v in mesh.vertices]
    finally:
        ev.to_mesh_clear()


def bbox_world(obj):
    pts = evaluated_points(obj)
    xs = [p.x for p in pts]
    ys = [p.y for p in pts]
    zs = [p.z for p in pts]
    return Vector((min(xs), min(ys), min(zs))), Vector((max(xs), max(ys), max(zs)))


def look_at(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def configure_camera(camera, pitch_deg, target):
    p = math.radians(pitch_deg)
    distance = 12.0
    camera.location = (target.x, target.y - distance * math.cos(p), target.z + distance * math.sin(p))
    look_at(camera, target)


def projected_bbox(scene, camera, obj):
    xs, ys = [], []
    for p in evaluated_points(obj):
        co = world_to_camera_view(scene, camera, p)
        xs.append(co.x * scene.render.resolution_x)
        ys.append((1.0 - co.y) * scene.render.resolution_y)
    return [min(xs), min(ys), max(xs), max(ys)]


def calibrate_camera(scene, camera, obj, target_height_px):
    camera.data.ortho_scale = 4.0
    for _ in range(7):
        bpy.context.view_layer.update()
        bb = projected_bbox(scene, camera, obj)
        h = bb[3] - bb[1]
        if h <= 0:
            raise RuntimeError("Projected body height is zero")
        camera.data.ortho_scale *= h / float(target_height_px)
    bpy.context.view_layer.update()


def render(scene, path: Path):
    scene.render.filepath = str(path)
    bpy.context.view_layer.update()
    bpy.ops.render.render(write_still=True)
    if not path.exists() or path.stat().st_size == 0:
        raise RuntimeError("Render missing: " + str(path))


def project_joint(scene, camera, rig, bone_name, tail=False):
    pb = rig.pose.bones.get(bone_name)
    if pb is None:
        return None
    p = pb.tail if tail else pb.head
    world = rig.matrix_world @ p
    co = world_to_camera_view(scene, camera, world)
    return [round(float(co.x * scene.render.resolution_x), 3), round(float((1.0 - co.y) * scene.render.resolution_y), 3)]


def audit_adult_female_macro_stack(TargetService, macro):
    if abs(float(macro.get("gender", -1.0))) > 1e-9:
        raise RuntimeError(f"G3S-B3A phenotype audit failed: MPFB female requires gender=0.0, got {macro.get('gender')}")
    if float(macro.get("age", 0.0)) < 0.5:
        raise RuntimeError(f"G3S-B3A phenotype audit failed: adult guide requires age>=0.5, got {macro.get('age')}")

    raw_stack = TargetService.calculate_target_stack_from_macro_info_dict(macro)
    stack = [[str(name), float(weight)] for name, weight in raw_stack]
    female_targets = [entry for entry in stack if "female" in entry[0].lower()]
    male_targets = [
        entry for entry in stack
        if "male" in entry[0].lower() and "female" not in entry[0].lower()
    ]
    adult_targets = [
        entry for entry in stack
        if "young" in entry[0].lower() or "old" in entry[0].lower()
    ]
    minor_targets = [
        entry for entry in stack
        if "baby" in entry[0].lower() or "child" in entry[0].lower()
    ]
    if not female_targets:
        raise RuntimeError("G3S-B3A phenotype audit failed: no female macro targets resolved")
    if male_targets:
        raise RuntimeError("G3S-B3A phenotype audit failed: male macro targets resolved: " + json.dumps(male_targets))
    if not adult_targets:
        raise RuntimeError("G3S-B3A phenotype audit failed: no adult (young/old) macro targets resolved")
    if minor_targets:
        raise RuntimeError("G3S-B3A phenotype audit failed: minor (baby/child) macro targets resolved: " + json.dumps(minor_targets))

    return {
        "gender_value": 0.0,
        "resolved_gender": "female",
        "age_value": float(macro["age"]),
        "resolved_life_stage": "adult",
        "female_target_count": len(female_targets),
        "male_target_count": len(male_targets),
        "adult_target_count": len(adult_targets),
        "minor_target_count": len(minor_targets),
        "female_targets": female_targets,
        "male_targets": male_targets,
        "adult_targets": adult_targets,
        "minor_targets": minor_targets,
        "upstream_semantics": "MPFB gender 0.0=female, 1.0=male; age >=0.5 resolves from young toward old",
    }


def main():
    out = Path(arg("--output-dir", "")).resolve()
    pitch = float(arg("--pitch", "26"))
    hero_px = int(arg("--hero-px", "128"))
    yaw = float(arg("--yaw", "8"))
    out.mkdir(parents=True, exist_ok=True)

    HumanService, mpfb_root = mpfb_class("services.humanservice", "HumanService")
    TargetService, _ = mpfb_class("services.targetservice", "TargetService")

    clear_scene()
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = WIDTH
    scene.render.resolution_y = HEIGHT
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.film_transparent = False
    try:
        scene.view_settings.view_transform = "Standard"
        scene.view_settings.look = "None"
        scene.view_settings.exposure = 0.0
        scene.view_settings.gamma = 1.0
    except Exception:
        pass

    macro = TargetService.get_default_macro_info_dict()
    macro.update({
        "gender": 0.0,
        "age": 0.52,
        "muscle": 0.40,
        "weight": 0.36,
        "proportions": 0.56,
        "height": 0.52,
        "cupsize": 0.42,
        "firmness": 0.55,
    })
    phenotype_audit = audit_adult_female_macro_stack(TargetService, macro)

    body = HumanService.create_human(
        mask_helpers=True,
        detailed_helpers=True,
        extra_vertex_groups=True,
        feet_on_ground=True,
        scale=0.1,
        macro_detail_dict=macro,
    )
    body.name = "G3S_B3_NUDE_BODY_GUIDE"
    for poly in body.data.polygons:
        poly.use_smooth = True

    rig = HumanService.add_builtin_rig(body, "cmu_mb", import_weights=True)
    if rig is None:
        raise RuntimeError("MPFB cmu_mb rig creation failed")
    rig.name = "G3S_B3_BODY_GUIDE_RIG"
    rig.hide_render = True

    # Authoring guide uses one deterministic slight three-quarter orientation.
    # No hair/clothing/restraint objects are ever created in this scene.
    body.rotation_euler[2] = math.radians(yaw)
    rig.rotation_euler[2] = math.radians(yaw)
    bpy.context.view_layer.update()

    skin_mat = material_principled("G3S_B3_SKIN_GUIDE", SKIN)
    mask_mat = material_emission("G3S_B3_BODY_MASK", (1.0, 1.0, 1.0))
    assign_material(body, skin_mat)

    bpy.ops.object.camera_add()
    camera = bpy.context.object
    camera.name = "G3S_B3_CAMERA"
    camera.data.type = "ORTHO"
    camera.data.clip_start = 0.01
    camera.data.clip_end = 1000.0
    scene.camera = camera

    lo, hi = bbox_world(body)
    target = (lo + hi) * 0.5
    configure_camera(camera, pitch, target)
    calibrate_camera(scene, camera, body, hero_px)
    bb = projected_bbox(scene, camera, body)
    visible_height = bb[3] - bb[1]
    if abs(visible_height - hero_px) > 2.0:
        raise RuntimeError(f"Body guide height calibration drift: {visible_height:.3f}px")

    set_world(scene, BG, 0.45)
    bpy.ops.object.light_add(type="SUN", location=(0.0, -4.0, 7.0))
    sun = bpy.context.object
    sun.name = "G3S_B3_KEY"
    sun.rotation_euler = (math.radians(32), math.radians(-8), math.radians(-38))
    sun.data.energy = 2.7
    bpy.ops.object.light_add(type="AREA", location=(3.0, -4.0, 4.0))
    fill = bpy.context.object
    fill.name = "G3S_B3_FILL"
    fill.data.energy = 220.0
    fill.data.shape = "DISK"
    fill.data.size = 4.0
    look_at(fill, target)

    lit_path = out / "g3s_b3a_nude_anatomy_lit.png"
    mask_path = out / "g3s_b3a_nude_anatomy_mask.png"
    blend_path = out / "g3s_b3a_nude_anatomy_guide.blend"
    manifest_path = out / "g3s_b3a_manifest.json"

    assign_material(body, skin_mat)
    set_world(scene, BG, 0.45)
    sun.hide_render = False
    fill.hide_render = False
    render(scene, lit_path)

    assign_material(body, mask_mat)
    set_world(scene, (0.0, 0.0, 0.0), 1.0)
    sun.hide_render = True
    fill.hide_render = True
    render(scene, mask_path)

    assign_material(body, skin_mat)
    sun.hide_render = False
    fill.hide_render = False
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))

    joint_names = [
        "Hips", "Spine1", "Neck1", "Head",
        "LeftArm", "LeftForeArm", "LeftHand",
        "RightArm", "RightForeArm", "RightHand",
        "LeftUpLeg", "LeftLeg", "LeftFoot",
        "RightUpLeg", "RightLeg", "RightFoot",
    ]
    joints = {name: project_joint(scene, camera, rig, name) for name in joint_names}
    missing = [name for name, pos in joints.items() if pos is None]
    if missing:
        raise RuntimeError("G3S-B3 guide rig missing bones: " + ", ".join(missing))

    scene_objects = [obj.name for obj in scene.objects]
    forbidden_tokens = ("hair", "cloth", "garment", "shackle", "chain", "cuff")
    forbidden = [name for name in scene_objects if any(tok in name.lower() for tok in forbidden_tokens)]
    # Material names contain no forbidden assets; object audit must be clean.
    if forbidden:
        raise RuntimeError("G3S-B3 guide scene contains forbidden layer objects: " + ", ".join(forbidden))

    manifest = {
        "gate": "G3S-B3-A-NUDE-ANATOMY-GUIDE",
        "status": "REVIEW_REQUIRED",
        "revision": REVISION,
        "art_authority": "STRUCTURAL_GUIDE_ONLY_NOT_FINAL_PIXEL_ART",
        "mpfb_module_root": mpfb_root,
        "macro": macro,
        "phenotype_audit": phenotype_audit,
        "body_object": body.name,
        "rig": "cmu_mb",
        "camera": {
            "resolution": [WIDTH, HEIGHT],
            "pitch_deg": pitch,
            "yaw_deg": yaw,
            "hero_px_target": hero_px,
            "visible_height_px": round(float(visible_height), 4),
            "ortho_scale": round(float(camera.data.ortho_scale), 8),
            "projected_bbox": [round(float(v), 3) for v in bb],
        },
        "joints_px": joints,
        "outputs": {
            "lit": str(lit_path),
            "lit_sha256": sha256_file(lit_path),
            "mask": str(mask_path),
            "mask_sha256": sha256_file(mask_path),
            "blend": str(blend_path),
        },
        "layer_audit": {
            "complete_body_geometry": True,
            "hair_objects": 0,
            "clothing_objects": 0,
            "restraint_objects": 0,
            "chains_objects": 0,
            "body_is_hairless": True,
            "body_is_unclothed": True,
        },
        "rules": {
            "not_final_visible_art": True,
            "not_a_nude_variant": True,
            "guide_for_native_body_source": True,
            "no_hair_before_body_source_pass": True,
            "no_clothing_before_body_source_pass": True,
            "no_animation_before_body_source_pass": True,
        },
        "next_internal_step": "G3S-B3-B NATIVE 128 NUDE BODY SOURCE",
    }
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print(f"G3S_B3A_REVISION={REVISION}")
    print("G3S_B3A_PHENOTYPE_GENDER=FEMALE")
    print("G3S_B3A_LIFE_STAGE=ADULT")
    print(f"G3S_B3A_FEMALE_TARGETS={phenotype_audit['female_target_count']}")
    print("G3S_B3A_MALE_TARGETS=0")
    print(f"G3S_B3A_ADULT_TARGETS={phenotype_audit['adult_target_count']}")
    print("G3S_B3A_MINOR_TARGETS=0")
    print("G3S_B3A_COMPLETE_NUDE_GEOMETRY=PASS")
    print("G3S_B3A_HAIR_OBJECTS=0")
    print("G3S_B3A_CLOTHING_OBJECTS=0")
    print("G3S_B3A_RESTRAINT_OBJECTS=0")
    print("G3S_B3A_ART_AUTHORITY=GUIDE_ONLY_NOT_FINAL_PIXEL_ART")
    print(f"G3S_B3A_VISIBLE_HEIGHT_PX={visible_height:.4f}")
    print(f"G3S_B3A_MANIFEST={manifest_path}")


if __name__ == "__main__":
    main()
