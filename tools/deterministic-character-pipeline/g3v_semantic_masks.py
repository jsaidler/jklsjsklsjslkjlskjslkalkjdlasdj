import re
from pathlib import Path

import bpy

SEMANTICS = ("skin", "hair", "cloth", "metal")


def install_binary_semantic_masks(target_globals):
    """Replace the fragile multi-color semantic pass with binary occlusion-aware masks.

    Each semantic is rendered as white while every other representative layer renders
    black. Black geometry remains present, so normal depth/occlusion is preserved. The
    four masks are then composited into the canonical semantic-ID PNG in Python.

    If a semantic has zero visible pixels in a frame, an additional unoccluded mask is
    rendered with all non-target semantic objects hidden. This distinguishes:
      - visible=0, unoccluded>0: target exists but is fully occluded by proxy geometry;
      - visible=0, unoccluded=0: target itself is not renderable/onscreen.
    Sequence-level validation occurs before visible-output construction.
    """
    required = (
        "BACKGROUND", "ID_COLORS", "d2", "render_pass", "build_visible_outputs",
        "id_foreground_stats", "assign_single_material", "make_emission_material",
        "set_world_background", "load_rgba", "save_rgba", "put", "main",
    )
    missing = [name for name in required if name not in target_globals]
    if missing:
        raise RuntimeError("G3V binary-mask patch missing target symbols: " + ", ".join(missing))

    background = target_globals["BACKGROUND"]
    id_colors = target_globals["ID_COLORS"]
    d2 = target_globals["d2"]
    assign_single_material = target_globals["assign_single_material"]
    make_emission_material = target_globals["make_emission_material"]
    set_world_background = target_globals["set_world_background"]
    load_rgba = target_globals["load_rgba"]
    save_rgba = target_globals["save_rgba"]
    put = target_globals["put"]
    original_render_pass = target_globals["render_pass"]
    original_build_visible_outputs = target_globals["build_visible_outputs"]

    diagnostics = {}
    target_globals["G3V_MASK_DIAGNOSTICS"] = diagnostics

    def robust_classify_id(color):
        background_distance = d2(color, background)
        best_semantic = None
        best_distance = background_distance
        for semantic, reference in id_colors.items():
            distance = d2(color, reference)
            if distance < best_distance:
                best_semantic = semantic
                best_distance = distance
        return best_semantic

    target_globals["classify_id"] = robust_classify_id

    def set_object_renderable(obj, renderable):
        obj.hide_render = not renderable
        try:
            obj.hide_viewport = False
        except Exception:
            pass
        try:
            obj.hide_set(False)
        except Exception:
            pass

    white_material = None
    black_material = None

    def ensure_mask_materials():
        nonlocal white_material, black_material
        if white_material is None:
            white_material = make_emission_material("G3V_MASK_WHITE", (1.0, 1.0, 1.0))
        if black_material is None:
            black_material = make_emission_material("G3V_MASK_BLACK", (0.0, 0.0, 0.0))
        return white_material, black_material

    def mask_pixel_count(px):
        count = 0
        for i in range(len(px) // 4):
            j = i * 4
            # Raw white target vs black occluder/background. A low threshold retains
            # antialiased edge pixels while remaining completely color-independent.
            if max(px[j], px[j + 1], px[j + 2]) > 0.20:
                count += 1
        return count

    def render_mask(scene, path, semantic_objects, semantic, unoccluded=False):
        white, black = ensure_mask_materials()
        set_world_background(scene, (0.0, 0.0, 0.0), 0.0)
        for obj in semantic_objects:
            is_target = obj.get("g3v_semantic") == semantic
            set_object_renderable(obj, is_target if unoccluded else True)
            assign_single_material(obj, white if is_target else black)

        previous_transform = None
        try:
            previous_transform = scene.view_settings.view_transform
            scene.view_settings.view_transform = "Raw"
        except Exception:
            pass
        try:
            scene.render.filepath = str(path)
            bpy.context.view_layer.update()
            bpy.ops.render.render(write_still=True)
        finally:
            if previous_transform is not None:
                try:
                    scene.view_settings.view_transform = previous_transform
                except Exception:
                    pass
            for obj in semantic_objects:
                set_object_renderable(obj, True)

        if not path.exists() or path.stat().st_size == 0:
            raise RuntimeError("G3V binary mask render missing: " + str(path))
        w, h, px = load_rgba(path)
        return w, h, px, mask_pixel_count(px)

    def object_diagnostics(semantic_objects, semantic):
        rows = []
        for obj in semantic_objects:
            if obj.get("g3v_semantic") != semantic:
                continue
            row = {
                "name": obj.name,
                "type": obj.type,
                "hide_render": bool(obj.hide_render),
                "scale": [float(v) for v in obj.scale],
            }
            if obj.type == "MESH":
                row["vertices"] = len(obj.data.vertices)
                row["polygons"] = len(obj.data.polygons)
                row["modifiers"] = [m.type for m in obj.modifiers]
            rows.append(row)
        return rows

    def compose_id(path, masks):
        first = masks[SEMANTICS[0]]
        w, h = first[0], first[1]
        for semantic in SEMANTICS[1:]:
            if masks[semantic][0:2] != (w, h):
                raise RuntimeError("G3V binary semantic masks have mismatched dimensions")

        out = [0.0] * (w * h * 4)
        for i in range(w * h):
            best_semantic = None
            best_value = 0.20
            for semantic in SEMANTICS:
                px = masks[semantic][2]
                j = i * 4
                value = max(px[j], px[j + 1], px[j + 2])
                if value > best_value:
                    best_value = value
                    best_semantic = semantic
            put(out, i, id_colors[best_semantic] if best_semantic else background)
        save_rgba(path, w, h, out)

    def binary_render_pass(scene, path, semantic_objects, mode, id_materials, neutral_material):
        if mode != "id":
            previous_transform = None
            try:
                previous_transform = scene.view_settings.view_transform
                scene.view_settings.view_transform = "Standard"
            except Exception:
                pass
            try:
                return original_render_pass(scene, path, semantic_objects, mode, id_materials, neutral_material)
            finally:
                if previous_transform is not None:
                    try:
                        scene.view_settings.view_transform = previous_transform
                    except Exception:
                        pass

        frame = int(scene.frame_current)
        output_path = Path(path)
        masks = {}
        frame_diag = {}
        for semantic in SEMANTICS:
            visible_path = output_path.with_name(f"g3v_mask_{semantic}_f{frame:04d}.png")
            w, h, px, visible_count = render_mask(
                scene, visible_path, semantic_objects, semantic, unoccluded=False
            )
            masks[semantic] = (w, h, px)
            entry = {
                "visible_pixels": int(visible_count),
                "visible_mask": str(visible_path),
                "unoccluded_pixels": None,
                "unoccluded_mask": None,
                "objects": object_diagnostics(semantic_objects, semantic),
            }
            if visible_count == 0:
                unoccluded_path = output_path.with_name(
                    f"g3v_mask_{semantic}_unoccluded_f{frame:04d}.png"
                )
                _, _, _, unoccluded_count = render_mask(
                    scene, unoccluded_path, semantic_objects, semantic, unoccluded=True
                )
                entry["unoccluded_pixels"] = int(unoccluded_count)
                entry["unoccluded_mask"] = str(unoccluded_path)
                print(
                    f"G3V_MASK_{semantic.upper()}_FRAME_{frame}_VISIBLE=0 "
                    f"UNOCCLUDED={unoccluded_count}"
                )
            else:
                print(f"G3V_MASK_{semantic.upper()}_FRAME_{frame}_VISIBLE={visible_count}")
            frame_diag[semantic] = entry

        diagnostics[frame] = frame_diag
        compose_id(output_path, masks)
        print(f"G3V_BINARY_ID_COMPOSITE_FRAME_{frame}=PASS")

    target_globals["render_pass"] = binary_render_pass

    # Per-frame foreground/height validation remains useful, but semantic completeness is
    # validated only across the sampled sequence. A tiny shackle may legitimately vanish
    # in one phase without invalidating the whole representative test.
    original_stats = target_globals["id_foreground_stats"]

    def binary_stats(path):
        return original_stats(path)

    target_globals["id_foreground_stats"] = binary_stats

    def validated_build_visible_outputs(frame_records, output_dir):
        sequence_totals = {semantic: 0 for semantic in SEMANTICS}
        sequence_unoccluded = {semantic: 0 for semantic in SEMANTICS}
        for rec in frame_records:
            frame = int(rec["frame"])
            frame_diag = diagnostics.get(frame, {})
            for semantic in SEMANTICS:
                entry = frame_diag.get(semantic)
                if not entry:
                    raise RuntimeError(
                        f"G3V missing binary-mask diagnostics for frame {frame} semantic {semantic}"
                    )
                sequence_totals[semantic] += int(entry["visible_pixels"])
                if entry["unoccluded_pixels"] is not None:
                    sequence_unoccluded[semantic] += int(entry["unoccluded_pixels"])

        print(
            "G3V_MASK_SEQUENCE_TOTALS="
            + ",".join(f"{s}:{sequence_totals[s]}" for s in SEMANTICS)
        )

        failures = []
        for semantic in SEMANTICS:
            if sequence_totals[semantic] > 0:
                continue
            if sequence_unoccluded[semantic] > 0:
                failures.append(
                    f"{semantic}: visible=0 across sampled sequence but unoccluded="
                    f"{sequence_unoccluded[semantic]} -> fully occluded by representative geometry"
                )
            else:
                objects = []
                for frame_diag in diagnostics.values():
                    if semantic in frame_diag:
                        objects = frame_diag[semantic].get("objects", [])
                        if objects:
                            break
                failures.append(
                    f"{semantic}: visible=0 and unoccluded=0 -> target does not render/onscreen; "
                    f"objects={objects}"
                )
        if failures:
            raise RuntimeError("G3V binary semantic diagnosis: " + " | ".join(failures))

        return original_build_visible_outputs(frame_records, output_dir)

    target_globals["build_visible_outputs"] = validated_build_visible_outputs

    if target_globals["render_pass"] is not binary_render_pass:
        raise RuntimeError("G3V binary-mask render patch did not bind")
    if target_globals["build_visible_outputs"] is not validated_build_visible_outputs:
        raise RuntimeError("G3V binary-mask sequence validator did not bind")

    print("G3V_SEMANTIC_MODE=BINARY_OCCLUSION_MASKS")
    print("G3V_MASK_DIAGNOSTICS=VISIBLE_PLUS_UNOCCLUDED_ON_ZERO")
