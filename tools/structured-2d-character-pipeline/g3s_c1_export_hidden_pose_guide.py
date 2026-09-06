import bpy
import json
import math
import sys
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view


def args_after_double_dash():
    if "--" not in sys.argv:
        return []
    return sys.argv[sys.argv.index("--") + 1:]


def arg(name, default=None):
    a = args_after_double_dash()
    for i, v in enumerate(a):
        if v == name and i + 1 < len(a):
            return a[i + 1]
    return default


def bone_world(rig, name, tail=False):
    pb = rig.pose.bones.get(name)
    if pb is None:
        raise RuntimeError(f"missing required bone: {name}")
    p = pb.tail if tail else pb.head
    return rig.matrix_world @ p


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
    if not pts:
        raise RuntimeError("hidden guide body has no evaluated vertices")
    xs = [p.x for p in pts]
    ys = [p.y for p in pts]
    zs = [p.z for p in pts]
    return Vector((min(xs), min(ys), min(zs))), Vector((max(xs), max(ys), max(zs)))


def look_at(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def configure_camera(camera, pitch_deg, target):
    p = math.radians(pitch_deg)
    distance = 12.0
    camera.location = (
        target.x,
        target.y - distance * math.cos(p),
        target.z + distance * math.sin(p),
    )
    look_at(camera, target)


def bbox_px(scene, camera, obj):
    xs, ys = [], []
    for p in evaluated_points(obj):
        co = world_to_camera_view(scene, camera, p)
        xs.append(float(co.x * scene.render.resolution_x))
        ys.append(float((1.0 - co.y) * scene.render.resolution_y))
    return [min(xs), min(ys), max(xs), max(ys)]


def calibrate_camera(scene, camera, obj, target_px):
    camera.data.ortho_scale = 5.0
    for _ in range(7):
        bpy.context.view_layer.update()
        b = bbox_px(scene, camera, obj)
        h = b[3] - b[1]
        if h <= 0.01:
            raise RuntimeError("projected hidden-guide body height is zero")
        camera.data.ortho_scale *= h / float(target_px)
    bpy.context.view_layer.update()


def set_world(scene, color):
    world = scene.world or bpy.data.worlds.new("C1_GUIDE_WORLD")
    scene.world = world
    world.use_nodes = True
    nodes = world.node_tree.nodes
    links = world.node_tree.links
    bg = nodes.get("Background")
    if bg is None:
        nodes.clear()
        bg = nodes.new("ShaderNodeBackground")
        out = nodes.new("ShaderNodeOutputWorld")
        links.new(bg.outputs["Background"], out.inputs["Surface"])
    bg.inputs["Color"].default_value = (*color, 1.0)
    bg.inputs["Strength"].default_value = 1.0


def emission_material(name, color):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    out = nodes.new("ShaderNodeOutputMaterial")
    emit = nodes.new("ShaderNodeEmission")
    emit.inputs["Color"].default_value = (*color, 1.0)
    emit.inputs["Strength"].default_value = 1.0
    links.new(emit.outputs["Emission"], out.inputs["Surface"])
    return mat


def diffuse_material(name, color):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    out = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.9
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat


def set_single_material(obj, mat):
    obj.data.materials.clear()
    obj.data.materials.append(mat)
    for p in obj.data.polygons:
        p.material_index = 0


def render(scene, path):
    scene.render.filepath = str(path)
    bpy.context.view_layer.update()
    bpy.ops.render.render(write_still=True)
    if not path.exists() or path.stat().st_size == 0:
        raise RuntimeError(f"missing guide render: {path}")


def category_for_group(name):
    n = name.lower()
    if n.startswith("left"):
        if any(k in n for k in ("arm", "forearm", "hand")):
            return "left_arm"
        if any(k in n for k in ("upleg", "leg", "foot", "toe")):
            return "left_leg"
    if n.startswith("right"):
        if any(k in n for k in ("arm", "forearm", "hand")):
            return "right_arm"
        if any(k in n for k in ("upleg", "leg", "foot", "toe")):
            return "right_leg"
    if "head" in n:
        return "head"
    if any(k in n for k in ("hips", "spine", "neck", "chest")):
        return "torso"
    return None


def assign_region_materials(body, mats, order):
    body.data.materials.clear()
    for key in order:
        body.data.materials.append(mats[key])
    index = {key: i for i, key in enumerate(order)}
    group_region = {}
    for vg in body.vertex_groups:
        region = category_for_group(vg.name)
        if region:
            group_region[vg.index] = region

    if not group_region:
        raise RuntimeError("MPFB body exposes no recognizable rig-weight vertex groups")

    vertices = body.data.vertices
    counts = {key: 0 for key in order}
    for poly in body.data.polygons:
        score = {key: 0.0 for key in order}
        for vi in poly.vertices:
            for item in vertices[vi].groups:
                region = group_region.get(item.group)
                if region:
                    score[region] += float(item.weight)
        region = max(order, key=lambda k: score[k])
        if max(score.values()) <= 1e-8:
            region = "torso"
        poly.material_index = index[region]
        counts[region] += 1
    return counts


def assign_depth_materials(body, camera, mats):
    body.data.materials.clear()
    for mat in mats:
        body.data.materials.append(mat)

    deps = bpy.context.evaluated_depsgraph_get()
    ev = body.evaluated_get(deps)
    mesh = ev.to_mesh()
    try:
        if len(mesh.polygons) != len(body.data.polygons):
            raise RuntimeError(
                f"evaluated body topology changed: eval={len(mesh.polygons)} source={len(body.data.polygons)}"
            )
        cam_inv = camera.matrix_world.inverted()
        mw = ev.matrix_world
        depths = []
        for poly in mesh.polygons:
            center = Vector((0.0, 0.0, 0.0))
            for vi in poly.vertices:
                center += mw @ mesh.vertices[vi].co
            center /= max(1, len(poly.vertices))
            depths.append(float(-(cam_inv @ center).z))
        lo = min(depths)
        hi = max(depths)
        span = max(1e-8, hi - lo)
        n = len(mats)
        for i, d in enumerate(depths):
            t = (d - lo) / span
            band = max(0, min(n - 1, int(math.floor(t * n))))
            body.data.polygons[i].material_index = band
        return {"near": lo, "far": hi, "bands": n}
    finally:
        ev.to_mesh_clear()


def screen_record(scene, camera, world):
    co = world_to_camera_view(scene, camera, world)
    cam_local = camera.matrix_world.inverted() @ world
    return {
        "x": float(co.x * scene.render.resolution_x),
        "y": float((1.0 - co.y) * scene.render.resolution_y),
        "depth": float(-cam_local.z),
        "world": [float(world.x), float(world.y), float(world.z)],
    }


def source_contact_metrics(scene, source, frames):
    rows = []
    all_z = []
    for f in frames:
        scene.frame_set(f)
        bpy.context.view_layer.update()
        left = bone_world(source, "LeftFoot")
        right = bone_world(source, "RightFoot")
        ltoe = bone_world(source, "LeftToeBase") if source.pose.bones.get("LeftToeBase") else left
        rtoe = bone_world(source, "RightToeBase") if source.pose.bones.get("RightToeBase") else right
        all_z.extend([left.z, right.z, ltoe.z, rtoe.z])
        sep = math.hypot(left.x - right.x, left.y - right.y)
        rows.append({
            "frame": int(f),
            "left": left.copy(),
            "right": right.copy(),
            "left_toe": ltoe.copy(),
            "right_toe": rtoe.copy(),
            "separation": float(sep),
            "left_lead_delta_x": float(left.x - right.x),
        })
    ground = min(all_z)
    for row in rows:
        left_low = min(row["left"].z, row["left_toe"].z) - ground
        right_low = min(row["right"].z, row["right_toe"].z) - ground
        row["left_ground_distance"] = float(left_low)
        row["right_ground_distance"] = float(right_low)
        row["score_left_contact"] = float(
            row["separation"]
            + max(0.0, row["left_lead_delta_x"]) * 0.5
            - left_low * 2.0
        )
    left_lead = [r for r in rows if r["left_lead_delta_x"] > 0.0]
    pool = left_lead if left_lead else rows
    chosen = max(pool, key=lambda r: r["score_left_contact"])
    serial = []
    for row in rows:
        serial.append({
            "frame": row["frame"],
            "foot_separation_xy": row["separation"],
            "left_lead_delta_x": row["left_lead_delta_x"],
            "left_ground_distance": row["left_ground_distance"],
            "right_ground_distance": row["right_ground_distance"],
            "score_left_contact": row["score_left_contact"],
        })
    return int(chosen["frame"]), serial, float(ground)


def ensure_left_facing(scene, camera, target, travel_world):
    # The validated G2 clip travels +X before directional-family conversion.
    # Flip the already-retargeted target in world space, then verify its travel vector projects left.
    target.rotation_euler[2] += math.pi
    bpy.context.view_layer.update()
    hips = bone_world(target, "Hips")
    rotated_travel = target.matrix_world.to_3x3() @ travel_world
    p0 = world_to_camera_view(scene, camera, hips)
    p1 = world_to_camera_view(scene, camera, hips + rotated_travel)
    dx = float((p1.x - p0.x) * scene.render.resolution_x)
    return dx


def main():
    g3v_blend = Path(arg("--g3v-blend", "")).resolve()
    approval_path = Path(arg("--approval", "")).resolve()
    output_dir = Path(arg("--output-dir", "")).resolve()
    pitch = float(arg("--pitch", "26"))
    hero_px = int(arg("--hero-px", "128"))

    if not g3v_blend.is_file():
        raise RuntimeError(f"G3V hidden-guide blend missing: {g3v_blend}")
    if not approval_path.is_file():
        raise RuntimeError(f"retarget approval missing: {approval_path}")
    output_dir.mkdir(parents=True, exist_ok=True)

    approval = json.loads(approval_path.read_text(encoding="utf-8-sig"))
    if approval.get("gate") != "G3V-R" or approval.get("status") != "PASS" or approval.get("method") != "DIRECTION_SPACE_FK":
        raise RuntimeError("validated DIRECTION_SPACE_FK approval is not PASS")
    candidate_frames = [int(x) for x in approval.get("source_frames", [])]
    if len(candidate_frames) != 4:
        raise RuntimeError(f"expected four validated gait phase frames, got {candidate_frames}")

    bpy.ops.wm.open_mainfile(filepath=str(g3v_blend))
    scene = bpy.context.scene
    source = bpy.data.objects.get("G2_CANONICAL_RIG")
    target = bpy.data.objects.get("G3V_CMU_RIG")
    body = bpy.data.objects.get("G3V_BODY")
    if source is None or source.type != "ARMATURE":
        raise RuntimeError("G2_CANONICAL_RIG missing from hidden-guide blend")
    if target is None or target.type != "ARMATURE":
        raise RuntimeError("G3V_CMU_RIG missing from hidden-guide blend")
    if body is None or body.type != "MESH":
        raise RuntimeError("G3V_BODY missing from hidden-guide blend")

    helper_dir = Path(__file__).resolve().parent.parent / "deterministic-character-pipeline"
    if str(helper_dir) not in sys.path:
        sys.path.insert(0, str(helper_dir))
    import g3v_motion_binding_patch as motion_patch

    chosen_frame, contact_metrics, source_ground = source_contact_metrics(scene, source, candidate_frames)

    # Measure source travel direction before posing target. G2 canonical clip is real captured motion.
    scene.frame_set(chosen_frame)
    bpy.context.view_layer.update()
    root0 = bone_world(source, "Hips")
    scene.frame_set(chosen_frame + 1)
    bpy.context.view_layer.update()
    root1 = bone_world(source, "Hips")
    travel_world = root1 - root0
    travel_world.z = 0.0
    if travel_world.length <= 1e-8:
        travel_world = Vector((1.0, 0.0, 0.0))
    else:
        travel_world.normalize()

    scene.frame_set(chosen_frame)
    bpy.context.view_layer.update()
    motion_patch._apply_direction_space_fk(source, target)

    # Hide everything except the continuous hidden adult body. No hair/cloth/metal/ground is part of C1A.
    for obj in scene.objects:
        if obj.type == "MESH":
            obj.hide_render = (obj != body)
    source.hide_render = True
    target.hide_render = True
    body.hide_render = False

    # Neutralize target object orientation first; the blend already stores the G2-aligned basis.
    # The full pose has already been solved in target armature space, so directional-family flip happens after solve.
    target.rotation_euler[2] += math.pi
    bpy.context.view_layer.update()

    # Put evaluated body on z=0; this is only guide framing, while contact metadata remains explicit in JSON.
    lo, hi = bbox_world(body)
    target.location.z -= lo.z
    bpy.context.view_layer.update()
    lo, hi = bbox_world(body)

    for obj in list(scene.objects):
        if obj.type == "CAMERA":
            obj.hide_render = True
    bpy.ops.object.camera_add()
    camera = bpy.context.object
    camera.name = "G3S_C1_GUIDE_CAMERA"
    camera.data.type = "ORTHO"
    camera.data.clip_start = 0.01
    camera.data.clip_end = 1000.0
    scene.camera = camera

    scene.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in {item.identifier for item in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items} else "BLENDER_EEVEE"
    scene.render.resolution_x = 640
    scene.render.resolution_y = 360
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

    target_point = (lo + hi) * 0.5
    configure_camera(camera, pitch, target_point)
    calibrate_camera(scene, camera, body, hero_px)

    # Verify the chosen directional family projects travel to screen-left.
    hips_world = bone_world(target, "Hips")
    rotated_travel = target.matrix_world.to_3x3() @ travel_world
    c0 = world_to_camera_view(scene, camera, hips_world)
    c1 = world_to_camera_view(scene, camera, hips_world + rotated_travel)
    travel_dx_px = float((c1.x - c0.x) * scene.render.resolution_x)
    if travel_dx_px >= 0:
        raise RuntimeError(f"C1 facing contract failed: expected screen-left travel vector, dx={travel_dx_px:.4f}px")

    # Ensure one deterministic key light for the neutral anatomy guide.
    for obj in list(scene.objects):
        if obj.type == "LIGHT":
            bpy.data.objects.remove(obj, do_unlink=True)
    bpy.ops.object.light_add(type="SUN", location=(0.0, -4.0, 6.0))
    sun = bpy.context.object
    sun.rotation_euler = (math.radians(35), 0.0, math.radians(-35))
    sun.data.energy = 2.5

    neutral = diffuse_material("C1_NEUTRAL", (0.48, 0.48, 0.50))
    white = emission_material("C1_SILHOUETTE", (1.0, 1.0, 1.0))
    region_colors = {
        "head": (0.80, 0.72, 0.22),
        "torso": (0.32, 0.74, 0.36),
        "left_arm": (0.20, 0.52, 0.95),
        "right_arm": (0.95, 0.30, 0.22),
        "left_leg": (0.18, 0.80, 0.88),
        "right_leg": (0.95, 0.58, 0.16),
    }
    region_order = ["head", "torso", "left_arm", "right_arm", "left_leg", "right_leg"]
    region_mats = {k: emission_material("C1_REGION_" + k.upper(), v) for k, v in region_colors.items()}
    depth_mats = []
    for i in range(8):
        # Near is bright, far is dark after assignment order is known from camera-space depth.
        v = 0.92 - i * (0.72 / 7.0)
        depth_mats.append(emission_material(f"C1_DEPTH_{i}", (v, v, v)))

    neutral_path = output_dir / "g3s_c1_contact_left_hidden3d_neutral.png"
    silhouette_path = output_dir / "g3s_c1_contact_left_silhouette_guide.png"
    regions_path = output_dir / "g3s_c1_contact_left_regions_guide.png"
    depth_path = output_dir / "g3s_c1_contact_left_depth_guide.png"

    set_world(scene, (0.055, 0.055, 0.065))
    set_single_material(body, neutral)
    render(scene, neutral_path)

    set_world(scene, (0.0, 0.0, 0.0))
    set_single_material(body, white)
    render(scene, silhouette_path)

    region_counts = assign_region_materials(body, region_mats, region_order)
    render(scene, regions_path)

    depth_stats = assign_depth_materials(body, camera, depth_mats)
    render(scene, depth_path)

    joint_defs = {
        "pelvis": ("Hips", False, "center"),
        "chest": ("Spine1", False, "center"),
        "neck": ("Neck1", False, "center"),
        "head": ("Head", True, "center"),
        "left_shoulder": ("LeftArm", False, "left"),
        "left_elbow": ("LeftForeArm", False, "left"),
        "left_wrist": ("LeftHand", False, "left"),
        "right_shoulder": ("RightArm", False, "right"),
        "right_elbow": ("RightForeArm", False, "right"),
        "right_wrist": ("RightHand", False, "right"),
        "left_hip": ("LeftUpLeg", False, "left"),
        "left_knee": ("LeftLeg", False, "left"),
        "left_ankle": ("LeftFoot", False, "left"),
        "left_toe": ("LeftToeBase", False, "left"),
        "right_hip": ("RightUpLeg", False, "right"),
        "right_knee": ("RightLeg", False, "right"),
        "right_ankle": ("RightFoot", False, "right"),
        "right_toe": ("RightToeBase", False, "right"),
    }
    joints = {}
    for key, (bone, tail, side) in joint_defs.items():
        if target.pose.bones.get(bone) is None:
            continue
        rec = screen_record(scene, camera, bone_world(target, bone, tail))
        rec["anatomical_side"] = side
        rec["bone"] = bone
        joints[key] = rec

    left_depth = sum(joints[k]["depth"] for k in joints if k.startswith("left_")) / max(1, sum(1 for k in joints if k.startswith("left_")))
    right_depth = sum(joints[k]["depth"] for k in joints if k.startswith("right_")) / max(1, sum(1 for k in joints if k.startswith("right_")))
    near_side = "left" if left_depth < right_depth else "right"
    far_side = "right" if near_side == "left" else "left"

    body_bbox = bbox_px(scene, camera, body)
    visible_height = body_bbox[3] - body_bbox[1]
    contact_side = "left"

    pose_data = {
        "gate": "G3S-C1A",
        "revision": "HIDDEN_3D_FULL_POSE_GUIDE_V1",
        "status": "REVIEW_REQUIRED",
        "guide_only": True,
        "hidden_3d_visible_art_owner": False,
        "selected_event": "left_contact",
        "selected_source_frame": chosen_frame,
        "candidate_phase_metrics": contact_metrics,
        "source_ground_reference_z": source_ground,
        "source_motion": "CMU 105_34 NormalWalk via G2_CANONICAL_RIG",
        "retarget_method": "DIRECTION_SPACE_FK",
        "direction_family": "screen-left",
        "travel_vector_screen_dx_px": travel_dx_px,
        "contact_foot": contact_side,
        "near_anatomical_side": near_side,
        "far_anatomical_side": far_side,
        "left_mean_camera_depth": left_depth,
        "right_mean_camera_depth": right_depth,
        "camera": {
            "raster": [640, 360],
            "type": "ORTHO",
            "pitch_deg": pitch,
            "ortho_scale": float(camera.data.ortho_scale),
            "target_body_height_px": hero_px,
            "measured_body_height_px": visible_height,
        },
        "body_bbox_px": body_bbox,
        "region_polygon_counts": region_counts,
        "depth_guide": depth_stats,
        "joints": joints,
        "root_pelvis_world": joints.get("pelvis", {}).get("world"),
        "outputs": {
            "neutral": str(neutral_path),
            "silhouette": str(silhouette_path),
            "regions": str(regions_path),
            "depth": str(depth_path),
        },
        "production_rule": "all rendered 3D passes are guide/control evidence only; none may be promoted, quantized or repurposed as final sprite RGB/alpha/silhouette",
    }
    joints_path = output_dir / "g3s_c1_contact_left_pose_guide.json"
    joints_path.write_text(json.dumps(pose_data, indent=2) + "\n", encoding="utf-8")

    print("G3S_C1A=REVIEW_REQUIRED")
    print(f"C1_SELECTED_EVENT=left_contact")
    print(f"C1_SELECTED_FRAME={chosen_frame}")
    print(f"C1_NEAR_SIDE={near_side}")
    print(f"C1_FAR_SIDE={far_side}")
    print(f"C1_TRAVEL_DX_PX={travel_dx_px:.4f}")
    print(f"C1_BODY_HEIGHT_PX={visible_height:.3f}")
    print(f"C1_POSE_JSON={joints_path}")


if __name__ == "__main__":
    main()
