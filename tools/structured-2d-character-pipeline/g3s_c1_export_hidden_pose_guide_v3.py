import math
import runpy
from pathlib import Path

import bpy
from mathutils import Matrix, Vector


BASE = Path(__file__).with_name("g3s_c1_export_hidden_pose_guide.py")


def install_v3(target_globals):
    """Preserve the calibrated world-space guide exactly while baking evaluated MPFB topology.

    C1A V2 correctly stopped assuming source/evaluated polygon identity, but it copied
    the evaluated mesh back into the source object's local space while retaining the
    source object transform. On the retained MPFB object this changed the projected
    guide height after the depth bake (128 px calibration became ~102.43 px).

    V3 freezes the evaluated mesh in WORLD coordinates, detaches the temporary guide
    object from parenting/modifiers, and gives it an identity object matrix. Therefore
    the frozen depth-pass geometry is numerically the same world-space geometry used by
    camera calibration. This mutation exists only in the headless C1A guide process.
    """
    required = ("main", "bbox_px")
    missing = [name for name in required if name not in target_globals]
    if missing:
        raise RuntimeError("C1A V3 patch missing base symbols: " + ", ".join(missing))

    bbox_px = target_globals["bbox_px"]

    def assign_depth_materials_v3(body, camera, mats):
        scene = bpy.context.scene
        source_polygon_count = len(body.data.polygons)
        pre_bbox = bbox_px(scene, camera, body)
        pre_height = float(pre_bbox[3] - pre_bbox[1])

        deps = bpy.context.evaluated_depsgraph_get()
        ev = body.evaluated_get(deps)
        eval_mesh = ev.to_mesh()
        try:
            evaluated_polygon_count = len(eval_mesh.polygons)
            if evaluated_polygon_count <= 0:
                raise RuntimeError("C1A evaluated MPFB body contains zero polygons")
            baked = eval_mesh.copy()
            # Convert evaluated local coordinates to exact evaluated WORLD coordinates
            # before discarding the dependency graph / armature modifiers.
            baked.transform(ev.matrix_world.copy())
        finally:
            ev.to_mesh_clear()

        body.data = baked
        for modifier in list(body.modifiers):
            body.modifiers.remove(modifier)
        body.parent = None
        body.matrix_world = Matrix.Identity(4)
        bpy.context.view_layer.update()

        post_bbox = bbox_px(scene, camera, body)
        post_height = float(post_bbox[3] - post_bbox[1])
        height_delta = abs(post_height - pre_height)
        if height_delta > 0.25:
            raise RuntimeError(
                "C1A world-space evaluated bake changed projected geometry: "
                f"pre={pre_height:.4f}px post={post_height:.4f}px delta={height_delta:.4f}px"
            )

        body.data.materials.clear()
        for mat in mats:
            body.data.materials.append(mat)

        cam_inv = camera.matrix_world.inverted()
        depths = []
        for poly in body.data.polygons:
            center = Vector((0.0, 0.0, 0.0))
            for vi in poly.vertices:
                center += body.data.vertices[vi].co
            center /= max(1, len(poly.vertices))
            depths.append(float(-(cam_inv @ center).z))

        lo = min(depths)
        hi = max(depths)
        span = max(1e-8, hi - lo)
        n = len(mats)
        for poly, depth in zip(body.data.polygons, depths):
            t = (depth - lo) / span
            band = max(0, min(n - 1, int(math.floor(t * n))))
            poly.material_index = band

        print(
            "C1A_DEPTH_TOPOLOGY=EVALUATED_WORLDSPACE_BAKE "
            f"source_polygons={source_polygon_count} evaluated_polygons={evaluated_polygon_count} "
            f"pre_height_px={pre_height:.4f} post_height_px={post_height:.4f}"
        )
        return {
            "near": lo,
            "far": hi,
            "bands": n,
            "mode": "evaluated_worldspace_bake",
            "source_polygon_count": source_polygon_count,
            "evaluated_polygon_count": evaluated_polygon_count,
            "projected_height_before_bake_px": pre_height,
            "projected_height_after_bake_px": post_height,
            "projected_height_delta_px": height_delta,
        }

    target_globals["assign_depth_materials"] = assign_depth_materials_v3
    if target_globals["assign_depth_materials"] is not assign_depth_materials_v3:
        raise RuntimeError("C1A V3 world-space depth patch did not bind")

    print("G3S_C1A_EXPORTER_REVISION=V3_WORLDSPACE_EVALUATED_BAKE")


def main():
    namespace_copy = runpy.run_path(str(BASE), run_name="g3s_c1_hidden_pose_base_v3")
    target_main = namespace_copy.get("main")
    if target_main is None or not callable(target_main):
        raise RuntimeError("C1A base exporter did not expose callable main()")
    target_globals = target_main.__globals__
    install_v3(target_globals)
    target_globals["main"]()


if __name__ == "__main__":
    main()
