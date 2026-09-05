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
        "mpfb", str(init_py), submodule_search_locations=[str(mpfb_root)]
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

    print("G3V_RETARGET_BOOTSTRAP=PASS")
    print(f"G3V_RETARGET_MPFB_ROOT={mpfb_root}")


def main():
    mpfb_root = Path(get_arg("--mpfb-root", "")).resolve()
    user_root = Path(get_arg("--mpfb-user-root", "")).resolve()
    target_script = Path(get_arg("--target-script", "")).resolve()
    if not target_script.exists():
        raise RuntimeError(f"Retarget preflight target script not found: {target_script}")

    # Route the canonical preflight through the V2 solver when present. This keeps the
    # operator command stable while replacing the failed local-axis retarget assumption.
    v2 = target_script.with_name("g3v_retarget_preflight_v2.py")
    if v2.exists():
        target_script = v2
        print("G3V_RETARGET_BOOTSTRAP_SOLVER=V2")

    bootstrap_mpfb(mpfb_root, user_root)
    namespace = runpy.run_path(str(target_script), run_name="g3v_retarget_preflight")
    target_main = namespace.get("main")
    if target_main is None or not callable(target_main):
        raise RuntimeError("Retarget preflight target did not expose callable main()")
    target_main()


if __name__ == "__main__":
    main()
