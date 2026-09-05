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


def install_g3v_runtime_fixes(target_globals):
    """Install diagnostic fixes into the *actual* globals used by target functions.

    runpy.run_path() returns a copied namespace. Mutating that returned dictionary does
    not necessarily alter function.__globals__. Therefore this function must receive
    main.__globals__, not the dictionary returned by runpy.
    """
    required = ("BACKGROUND", "ID_COLORS", "d2", "render_pass", "id_foreground_stats", "main")
    missing = [name for name in required if name not in target_globals]
    if missing:
        raise RuntimeError("G3V target missing runtime-patch symbols: " + ", ".join(missing))

    background = target_globals["BACKGROUND"]
    id_colors = target_globals["ID_COLORS"]
    d2 = target_globals["d2"]

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

    original_render_pass = target_globals["render_pass"]

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

    target_globals["render_pass"] = robust_render_pass

    original_stats = target_globals["id_foreground_stats"]

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

    target_globals["id_foreground_stats"] = strict_semantic_stats

    if target_globals["classify_id"] is not robust_classify_id:
        raise RuntimeError("G3V classifier runtime patch did not bind to target globals")
    if target_globals["render_pass"] is not robust_render_pass:
        raise RuntimeError("G3V render-pass runtime patch did not bind to target globals")
    if target_globals["id_foreground_stats"] is not strict_semantic_stats:
        raise RuntimeError("G3V semantic-stats runtime patch did not bind to target globals")

    print("G3V_RUNTIME_PATCH_GLOBALS=BOUND_TO_MAIN")
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

    namespace_copy = runpy.run_path(str(target_script), run_name="g3v_target")
    target_main = namespace_copy.get("main")
    if target_main is None or not callable(target_main):
        raise RuntimeError("G3V target did not expose callable main()")

    # Critical: runpy returns a copied dictionary. Patch the globals actually referenced
    # by the target functions, then invoke main from that same globals dictionary.
    target_globals = target_main.__globals__
    install_g3v_runtime_fixes(target_globals)
    target_globals["main"]()


if __name__ == "__main__":
    main()
