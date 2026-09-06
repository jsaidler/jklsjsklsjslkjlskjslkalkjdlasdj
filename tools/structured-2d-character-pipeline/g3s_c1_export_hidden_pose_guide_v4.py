import math
import runpy
from pathlib import Path

import bpy
from mathutils import Vector


BASE = Path(__file__).with_name("g3s_c1_export_hidden_pose_guide.py")


def install_v4(target_globals):
    """Render depth from a detached copy of the evaluated MPFB mesh.

    V3 tried to replace the rigged source object's mesh with a world-space baked mesh and
    then neutralize that same object's transform/parent state. On the retained MPFB stack,
    object/parent/bind state made that mutation non-invariant: a calibrated 128 px body
    became 99.0563 px.

    V4 does not mutate G3V_BODY at all. It creates a separate temporary object from the
    already evaluated posed mesh, gives that detached object the exact evaluated
    matrix_world, and renders depth bands on that copy. This isolates the topology-only
    depth pass from all MPFB parenting, constraints, armature modifiers and bind-space
    state while preserving the same evaluated world geometry used by camera calibration.
    """
    required = ("main", "bbox_px")
    missing = [name for name in required if name not in target_globals]
    if missing:
        raise RuntimeError("C1A V4 patch missing base symbols: " + ", ".join(missing))

    bbox_px = target_globals["bbox_px"]

    def assign_depth_materials_v4(body, camera, mats):
        scene = bpy.context.scene
        source_polygon_count = len(body.data.polygons)
        pre_bbox = bbox_px(scene, camera, body)
        pre_height = float(pre_bbox[3] - pre_bbox[1])

        deps = bpy.context.evaluated_depsgraph_get()
        ev = body.evaluated_get(deps)
        eval_world = ev.matrix_world.copy()
        eval_mesh = ev.to_mesh()
        try:
            evaluated_polygon_count = len(eval_mesh.polygons)
            if evaluated_polygon_count <= 0:
                raise RuntimeError("C1A evaluated MPFB body contains zero polygons")
            baked = eval_mesh.copy()
        finally:
            ev.to_mesh_clear()

        depth_obj = bpy.data.objects.new("G3S_C1_DEPTH_EVALUATED_PROXY", baked)
        scene.collection.objects.link(depth_obj)
        depth_obj.matrix_world = eval_world
        depth_obj.hide_render = False

        # Depth proxy is detached: no parent, no armature modifier, no constraints.
        if depth_obj.parent is not None or len(depth_obj.modifiers) != 0 or len(depth_obj.constraints) != 0:
            raise RuntimeError("C1A detached evaluated depth proxy unexpectedly inherited rig state")

        bpy.context.view_layer.update()
        post_bbox = bbox_px(scene, camera, depth_obj)
        post_height = float(post_bbox[3] - post_bbox[1])
        height_delta = abs(post_height - pre_height)
        if height_delta > 0.25:
            raise RuntimeError(
                "C1A detached evaluated depth proxy changed projected geometry: "
                f"pre={pre_height:.4f}px post={post_height:.4f}px delta={height_delta:.4f}px"
            )

        depth_obj.data.materials.clear()
        for mat in mats:
            depth_obj.data.materials.append(mat)

        cam_inv = camera.matrix_world.inverted()
        mw = depth_obj.matrix_world
        depths = []
        for poly in depth_obj.data.polygons:
            center = Vector((0.0, 0.0, 0.0))
            for vi in poly.vertices:
                center += mw @ depth_obj.data.vertices[vi].co
            center /= max(1, len(poly.vertices))
            depths.append(float(-(cam_inv @ center).z))

        lo = min(depths)
        hi = max(depths)
        span = max(1e-8, hi - lo)
        n = len(mats)
        for poly, depth in zip(depth_obj.data.polygons, depths):
            t = (depth - lo) / span
            band = max(0, min(n - 1, int(math.floor(t * n))))
            poly.material_index = band

        # The original rigged body already produced neutral/silhouette/region passes.
        # Hide only for the upcoming depth render so the detached evaluated proxy is the
        # sole visible geometry. G3V_BODY itself remains geometrically untouched and is
        # still used below for joints/bbox/metadata.
        body.hide_render = True
        depth_obj.hide_render = False
        bpy.context.view_layer.update()

        print(
            "C1A_DEPTH_TOPOLOGY=DETACHED_EVALUATED_OBJECT "
            f"source_polygons={source_polygon_count} evaluated_polygons={evaluated_polygon_count} "
            f"pre_height_px={pre_height:.4f} post_height_px={post_height:.4f}"
        )
        return {
            "near": lo,
            "far": hi,
            "bands": n,
            "mode": "detached_evaluated_object",
            "source_polygon_count": source_polygon_count,
            "evaluated_polygon_count": evaluated_polygon_count,
            "projected_height_before_bake_px": pre_height,
            "projected_height_after_bake_px": post_height,
            "projected_height_delta_px": height_delta,
            "source_body_mutated": False,
            "proxy_object": depth_obj.name,
        }

    target_globals["assign_depth_materials"] = assign_depth_materials_v4
    if target_globals["assign_depth_materials"] is not assign_depth_materials_v4:
        raise RuntimeError("C1A V4 detached depth patch did not bind")

    print("G3S_C1A_EXPORTER_REVISION=V4_DETACHED_EVALUATED_DEPTH_PROXY")


def main():
    namespace_copy = runpy.run_path(str(BASE), run_name="g3s_c1_hidden_pose_base_v4")
    target_main = namespace_copy.get("main")
    if target_main is None or not callable(target_main):
        raise RuntimeError("C1A base exporter did not expose callable main()")
    target_globals = target_main.__globals__
    install_v4(target_globals)
    target_globals["main"]()


if __name__ == "__main__":
    main()
