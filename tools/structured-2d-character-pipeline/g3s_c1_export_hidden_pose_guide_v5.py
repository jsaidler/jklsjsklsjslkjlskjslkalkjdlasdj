import runpy
from pathlib import Path

import bpy


BASE = Path(__file__).with_name("g3s_c1_export_hidden_pose_guide.py")


def install_v5(target_globals):
    """Render camera-space depth on the original rigged body without topology substitution.

    V1-V4 all tried to derive a separate polygon-indexed/evaluated geometry carrier for
    the depth pass. On the retained MPFB stack, every substitution route changed the
    projected body geometry despite apparently equivalent transforms.

    V5 removes that entire class of failure. It leaves G3V_BODY geometry, parenting,
    armature/bind state and object transform untouched. A guide-only emission shader is
    assigned to the original body and computes grayscale depth continuously from the
    shading point transformed from WORLD to CAMERA space. The same evaluated body that
    calibrated the locked 128 px camera is therefore the body that renders the depth
    pass. No source/evaluated polygon correspondence is needed.
    """
    required = ("main", "bbox_px", "evaluated_points")
    missing = [name for name in required if name not in target_globals]
    if missing:
        raise RuntimeError("C1A V5 patch missing base symbols: " + ", ".join(missing))

    bbox_px = target_globals["bbox_px"]
    evaluated_points = target_globals["evaluated_points"]

    def assign_depth_materials_v5(body, camera, _mats):
        scene = bpy.context.scene
        pre_bbox = bbox_px(scene, camera, body)
        pre_height = float(pre_bbox[3] - pre_bbox[1])

        points = evaluated_points(body)
        if not points:
            raise RuntimeError("C1A original evaluated body has no vertices for depth range")
        cam_inv = camera.matrix_world.inverted()
        depths = [float(-(cam_inv @ p).z) for p in points]
        lo = min(depths)
        hi = max(depths)
        if hi - lo <= 1e-8:
            raise RuntimeError("C1A original evaluated body has zero camera-space depth span")

        deps = bpy.context.evaluated_depsgraph_get()
        ev = body.evaluated_get(deps)
        mesh = ev.to_mesh()
        try:
            evaluated_polygon_count = len(mesh.polygons)
        finally:
            ev.to_mesh_clear()
        source_polygon_count = len(body.data.polygons)

        mat = bpy.data.materials.get("C1_DEPTH_CAMERA_SPACE_SHADER") or bpy.data.materials.new(
            "C1_DEPTH_CAMERA_SPACE_SHADER"
        )
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        nodes.clear()

        out = nodes.new("ShaderNodeOutputMaterial")
        emit = nodes.new("ShaderNodeEmission")
        geom = nodes.new("ShaderNodeNewGeometry")
        xform = nodes.new("ShaderNodeVectorTransform")
        xform.vector_type = "POINT"
        xform.convert_from = "WORLD"
        xform.convert_to = "CAMERA"
        sep = nodes.new("ShaderNodeSeparateXYZ")
        neg = nodes.new("ShaderNodeMath")
        neg.operation = "MULTIPLY"
        neg.inputs[1].default_value = -1.0
        remap = nodes.new("ShaderNodeMapRange")
        remap.clamp = True
        remap.inputs["From Min"].default_value = lo
        remap.inputs["From Max"].default_value = hi
        remap.inputs["To Min"].default_value = 0.95
        remap.inputs["To Max"].default_value = 0.15
        emit.inputs["Strength"].default_value = 1.0

        links.new(geom.outputs["Position"], xform.inputs["Vector"])
        links.new(xform.outputs["Vector"], sep.inputs["Vector"])
        links.new(sep.outputs["Z"], neg.inputs[0])
        links.new(neg.outputs[0], remap.inputs["Value"])
        links.new(remap.outputs["Result"], emit.inputs["Color"])
        links.new(emit.outputs["Emission"], out.inputs["Surface"])

        body.data.materials.clear()
        body.data.materials.append(mat)
        for poly in body.data.polygons:
            poly.material_index = 0
        body.hide_render = False
        bpy.context.view_layer.update()

        post_bbox = bbox_px(scene, camera, body)
        post_height = float(post_bbox[3] - post_bbox[1])
        height_delta = abs(post_height - pre_height)
        if height_delta > 0.01:
            raise RuntimeError(
                "C1A camera-space depth shader changed projected body geometry: "
                f"pre={pre_height:.4f}px post={post_height:.4f}px delta={height_delta:.4f}px"
            )

        print(
            "C1A_DEPTH_MODE=ORIGINAL_BODY_CAMERA_SPACE_SHADER "
            f"source_polygons={source_polygon_count} evaluated_polygons={evaluated_polygon_count} "
            f"pre_height_px={pre_height:.4f} post_height_px={post_height:.4f} "
            f"near={lo:.6f} far={hi:.6f}"
        )
        return {
            "near": lo,
            "far": hi,
            "bands": "continuous_shader",
            "mode": "original_body_camera_space_shader",
            "source_polygon_count": source_polygon_count,
            "evaluated_polygon_count": evaluated_polygon_count,
            "projected_height_before_depth_shader_px": pre_height,
            "projected_height_after_depth_shader_px": post_height,
            "projected_height_delta_px": height_delta,
            "source_geometry_mutated": False,
            "proxy_object_used": False,
            "topology_index_mapping_used": False,
        }

    target_globals["assign_depth_materials"] = assign_depth_materials_v5
    if target_globals["assign_depth_materials"] is not assign_depth_materials_v5:
        raise RuntimeError("C1A V5 camera-space depth shader patch did not bind")

    print("G3S_C1A_EXPORTER_REVISION=V5_ORIGINAL_BODY_CAMERA_SPACE_DEPTH_SHADER")


def main():
    namespace_copy = runpy.run_path(str(BASE), run_name="g3s_c1_hidden_pose_base_v5")
    target_main = namespace_copy.get("main")
    if target_main is None or not callable(target_main):
        raise RuntimeError("C1A base exporter did not expose callable main()")
    target_globals = target_main.__globals__
    install_v5(target_globals)
    target_globals["main"]()


if __name__ == "__main__":
    main()
