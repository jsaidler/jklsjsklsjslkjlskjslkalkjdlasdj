import bpy
import importlib
import importlib.util
import runpy
import sys
from pathlib import Path


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


def bootstrap_mpfb(mpfb_root: Path, user_root: Path):
    init_py = mpfb_root / "__init__.py"
    services_dir = mpfb_root / "services"
    data_dir = mpfb_root / "data"
    if not init_py.exists() or not services_dir.is_dir() or not data_dir.is_dir():
        raise RuntimeError(f"Invalid MPFB package root: {mpfb_root}")

    user_root.mkdir(parents=True, exist_ok=True)

    # LocationService normally asks Blender for a writable directory associated with
    # an installed extension. G3V intentionally loads the pinned package directly,
    # so provide a deterministic project-local path instead of depending on Blender
    # extension repository state/preferences.
    original_extension_path_user = bpy.utils.extension_path_user

    def project_extension_path_user(package, *, path="", create=False):
        if package == "mpfb":
            p = user_root / path if path else user_root
            if create:
                p.mkdir(parents=True, exist_ok=True)
            return str(p)
        return original_extension_path_user(package, path=path, create=create)

    bpy.utils.extension_path_user = project_extension_path_user

    spec = importlib.util.spec_from_file_location(
        "mpfb",
        str(init_py),
        submodule_search_locations=[str(mpfb_root)],
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not construct MPFB module spec from {init_py}")

    module = importlib.util.module_from_spec(spec)
    sys.modules["mpfb"] = module
    spec.loader.exec_module(module)

    # We only need MPFB's service layer for headless character construction/rigging.
    # Avoid registering the GUI extension entirely. Preferences are therefore replaced
    # by neutral defaults and contextual package information is initialized explicitly.
    module.get_preference = lambda _name: None
    module.MPFB_CONTEXTUAL_INFORMATION = {
        "__package__": "mpfb",
        "__package_short__": "mpfb",
        "__file__": str(init_py),
    }

    services = importlib.import_module("mpfb.services")
    module.MPFB_CONTEXTUAL_INFORMATION["SERVICES"] = services.SERVICES

    required = ("HumanService", "TargetService", "RigService", "ObjectService")
    missing = [name for name in required if name not in services.SERVICES]
    if missing:
        raise RuntimeError("MPFB service bootstrap missing: " + ", ".join(missing))

    print("G3V_MPFB_BOOTSTRAP=PASS")
    print(f"G3V_MPFB_ROOT={mpfb_root}")
    print(f"G3V_MPFB_USER_ROOT={user_root}")


def install_g3v_runtime_fixes(namespace):
    """Patch fragile diagnostic behavior without changing the production hypothesis.

    PNG color management can move emission RGB values significantly. The original
    classifier required an arbitrary absolute distance threshold after already deciding
    that a pixel was closer to a semantic color than to the background. That caused
    valid rendered skin/hair/metal pixels to be discarded while some cloth pixels
    survived. For an ID pass the correct decision is categorical: choose the closest
    semantic only when it beats the background.

    The ID render also uses Raw view transform so the encoded diagnostic colors stay as
    close as possible to their linear emission values. The neutral-light pass restores
    Standard transform for the visual shading measurement.
    """
    required = ("BACKGROUND", "ID_COLORS", "d2", "render_pass", "id_foreground_stats", "main")
    missing = [name for name in required if name not in namespace]
    if missing:
        raise RuntimeError("G3V target missing runtime-patch symbols: " + ", ".join(missing))

    background = namespace["BACKGROUND"]
    id_colors = namespace["ID_COLORS"]
    d2 = namespace["d2"]

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

    namespace["classify_id"] = robust_classify_id

    original_render_pass = namespace["render_pass"]

    def robust_render_pass(scene, path, semantic_objects, mode, id_materials, neutral_material):
        previous_transform = None
        try:
            previous_transform = scene.view_settings.view_transform
        except Exception:
            pass
        try:
            try:
                scene.view_settings.view_transform = "Raw" if mode == "id" else "Standard"
            except Exception:
                pass
            return original_render_pass(scene, path, semantic_objects, mode, id_materials, neutral_material)
        finally:
            if previous_transform is not None:
                try:
                    scene.view_settings.view_transform = previous_transform
                except Exception:
                    pass

    namespace["render_pass"] = robust_render_pass

    original_stats = namespace["id_foreground_stats"]

    def strict_semantic_stats(path):
        stats = original_stats(path)
        counts = stats.get("semantic_pixels", {})
        missing_semantics = [name for name in ("skin", "hair", "cloth", "metal") if int(counts.get(name, 0)) <= 0]
        if missing_semantics:
            raise RuntimeError(
                "G3V semantic ID pass is missing visible representative layers "
                + ", ".join(missing_semantics)
                + f"; stats={stats}"
            )
        return stats

    namespace["id_foreground_stats"] = strict_semantic_stats

    print("G3V_SEMANTIC_CLASSIFIER=NEAREST_VS_BACKGROUND")
    print("G3V_ID_COLOR_TRANSFORM=RAW")
    print("G3V_REQUIRED_SEMANTICS=skin,hair,cloth,metal")


def main():
    mpfb_root = Path(get_arg("--mpfb-root", "")).resolve()
    user_root = Path(get_arg("--mpfb-user-root", "")).resolve()
    target_script = Path(get_arg("--target-script", "")).resolve()

    if not target_script.exists():
        raise RuntimeError(f"G3V target script not found: {target_script}")

    bootstrap_mpfb(mpfb_root, user_root)

    # Load the target without triggering its __main__ block, install diagnostic fixes,
    # then call main explicitly. Functions created by runpy retain this namespace as
    # their globals, so the patched classifier/render_pass are used throughout G3V.
    namespace = runpy.run_path(str(target_script), run_name="g3v_target")
    install_g3v_runtime_fixes(namespace)
    namespace["main"]()


if __name__ == "__main__":
    main()
