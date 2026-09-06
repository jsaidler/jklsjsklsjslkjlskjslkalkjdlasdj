import math
import runpy
from pathlib import Path

import bpy
from mathutils import Vector


BASE = Path(__file__).with_name("g3s_c1_export_hidden_pose_guide.py")


def install_v2(target_globals):
    """Fix C1A depth rendering when MPFB modifiers change evaluated topology.

    The V1 exporter assumed a 1:1 polygon mapping between G3V_BODY source mesh and
    its evaluated/deformed render mesh. On the retained MPFB body this is false
    (observed locally: source 18486 polygons, evaluated 13378 polygons), so mapping
    evaluated polygon depth back by source polygon index is invalid.

    C1A only needs one frozen guide pose. For the depth pass, bake the already posed
    evaluated mesh into a temporary-in-process body data block, remove its modifiers,
    and assign depth bands directly on that evaluated topology. This does NOT make 3D
    visible art authoritative; it remains guide/control evidence only.
    """
    required = ("main", "assign_depth_materials")
    missing = [name for name in required if name not in target_globals]
    if missing:
        raise RuntimeError("C1A V2 patch missing base symbols: " + ", ".join(missing))

    def assign_depth_materials_v2(body, camera, mats):
        source_polygon_count = len(body.data.polygons)
        deps = bpy.context.evaluated_depsgraph_get()
        ev = body.evaluated_get(deps)
        eval_mesh = ev.to_mesh()
        try:
            baked = eval_mesh.copy()
            evaluated_polygon_count = len(baked.polygons)
        finally:
            ev.to_mesh_clear()

        if evaluated_polygon_count <= 0:
            raise RuntimeError("C1A evaluated MPFB body contains zero polygons")

        # Freeze exactly the already-retargeted guide pose. The original source mesh is
        # untouched on disk; this mutation exists only inside this headless Blender run.
        body.data = baked
        for modifier in list(body.modifiers):
            body.modifiers.remove(modifier)
        bpy.context.view_layer.update()

        body.data.materials.clear()
        for mat in mats:
            body.data.materials.append(mat)

        cam_inv = camera.matrix_world.inverted()
        mw = body.matrix_world
        depths = []
        for poly in body.data.polygons:
            center = Vector((0.0, 0.0, 0.0))
            for vi in poly.vertices:
                center += mw @ body.data.vertices[vi].co
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
            "C1A_DEPTH_TOPOLOGY=EVALUATED_BAKE "
            f"source_polygons={source_polygon_count} evaluated_polygons={evaluated_polygon_count}"
        )
        return {
            "near": lo,
            "far": hi,
            "bands": n,
            "mode": "evaluated_mesh_bake",
            "source_polygon_count": source_polygon_count,
            "evaluated_polygon_count": evaluated_polygon_count,
        }

    target_globals["assign_depth_materials"] = assign_depth_materials_v2
    if target_globals["assign_depth_materials"] is not assign_depth_materials_v2:
        raise RuntimeError("C1A V2 depth-topology patch did not bind")

    print("G3S_C1A_EXPORTER_REVISION=V2_EVALUATED_DEPTH_TOPOLOGY")


def main():
    namespace_copy = runpy.run_path(str(BASE), run_name="g3s_c1_hidden_pose_base_v2")
    target_main = namespace_copy.get("main")
    if target_main is None or not callable(target_main):
        raise RuntimeError("C1A base exporter did not expose callable main()")
    target_globals = target_main.__globals__
    install_v2(target_globals)
    target_globals["main"]()


if __name__ == "__main__":
    main()
