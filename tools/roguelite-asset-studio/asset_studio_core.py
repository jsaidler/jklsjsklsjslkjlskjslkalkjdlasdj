#!/usr/bin/env python3
"""Core contracts for the Roguelite Asset Studio.

This module deliberately contains no UI and no model-specific ComfyUI graph.
It owns asset-spec validation and model routing so Gradio/desktop/web surfaces and
individual model adapters can evolve independently.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

HERE = Path(__file__).resolve().parent
DEFAULT_SCHEMA = HERE / "asset_schema.json"
DEFAULT_REGISTRY = HERE / "model_registry.json"

ROUTABLE_STATUSES = {
    "active_proven": 0,
    "active_rnd": 20,
    "available_unvalidated_for_studio": 40,
    "priority_candidate_not_installed": 60,
    "priority_training_candidate_not_installed": 70,
    "quality_control_candidate_not_installed": 80,
    "deferred_hardware_mismatch": 100,
}


class AssetStudioError(RuntimeError):
    pass


@dataclass(frozen=True)
class ModelRoute:
    adapter_id: str
    family: str
    status: str
    license: str
    quality_tier: str
    score: int
    installed: bool
    notes: str


def load_json(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as fh:
            value = json.load(fh)
    except FileNotFoundError as exc:
        raise AssetStudioError(f"Required Asset Studio file is missing: {path}") from exc
    except json.JSONDecodeError as exc:
        raise AssetStudioError(f"Invalid JSON in {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise AssetStudioError(f"Expected JSON object in {path}")
    return value


def validate_spec(spec: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for field in schema.get("required_fields", []):
        if field not in spec or spec[field] in (None, "", []):
            errors.append(f"missing required field: {field}")

    asset_type = spec.get("asset_type")
    if asset_type and asset_type not in schema.get("asset_types", []):
        errors.append(f"unsupported asset_type: {asset_type}")

    output_contract = spec.get("output_contract")
    if output_contract and output_contract not in schema.get("output_contracts", []):
        errors.append(f"unsupported output_contract: {output_contract}")

    allowed_roles = set(schema.get("reference_roles", []))
    refs = spec.get("references", [])
    if refs is not None and not isinstance(refs, list):
        errors.append("references must be a list")
    elif isinstance(refs, list):
        for index, ref in enumerate(refs):
            if not isinstance(ref, dict):
                errors.append(f"references[{index}] must be an object")
                continue
            role = ref.get("role")
            if role not in allowed_roles:
                errors.append(f"references[{index}].role unsupported: {role}")
            if not ref.get("path"):
                errors.append(f"references[{index}].path is required")

    world_scale = spec.get("world_scale")
    if world_scale is not None:
        try:
            if float(world_scale) <= 0:
                errors.append("world_scale must be > 0")
        except (TypeError, ValueError):
            errors.append("world_scale must be numeric")

    return errors


def infer_required_capabilities(spec: dict[str, Any]) -> set[str]:
    contract = spec.get("output_contract")
    refs = spec.get("references") or []
    roles = {ref.get("role") for ref in refs if isinstance(ref, dict)}

    caps: set[str] = set()
    if contract in {"static_master", "static_rgba", "variant_set", "turnaround_reference", "layered_environment_module", "tileable_texture"}:
        if "previous_approved_state" in roles or "identity" in roles or "structure" in roles:
            caps.add("single_reference_edit")
        else:
            caps.add("text_to_image")
        if len(refs) > 1:
            caps.add("multi_reference_edit")

    if contract in {"animated_action", "sprite_row", "sprite_atlas"}:
        if "motion" in roles:
            caps.add("reference_video_motion")
        else:
            caps.add("image_to_video")

    if contract in {"animated_loop", "sequence_rgba"}:
        caps.add("animated_loop_candidate")

    return caps


def _capability_match(model_caps: set[str], required: set[str]) -> tuple[bool, int]:
    if not required:
        return True, 0
    missing = required - model_caps
    if not missing:
        return True, 0

    # A semantic/appearance editor can satisfy the generic single-reference edit
    # contract even when the registry uses more specific capability names.
    edit_aliases = {"semantic_edit", "appearance_edit", "reference_edit"}
    if "single_reference_edit" in missing and model_caps & edit_aliases:
        missing.remove("single_reference_edit")
    if "multi_reference_edit" in missing and "multimodal_reference" in model_caps:
        missing.remove("multi_reference_edit")
    return (not missing), len(missing)


def route_models(
    spec: dict[str, Any],
    registry: dict[str, Any],
    *,
    include_uninstalled: bool = False,
) -> list[ModelRoute]:
    asset_type = spec.get("asset_type")
    required = infer_required_capabilities(spec)
    routes: list[ModelRoute] = []

    for model in registry.get("models", []):
        if not isinstance(model, dict):
            continue
        if asset_type not in set(model.get("asset_types", [])):
            continue
        status = str(model.get("status", "unknown"))
        installed = status in {"active_proven", "active_rnd", "available_unvalidated_for_studio"}
        if not include_uninstalled and not installed:
            continue

        model_caps = set(model.get("capabilities", []))
        matches, missing_count = _capability_match(model_caps, set(required))
        if not matches:
            continue

        score = ROUTABLE_STATUSES.get(status, 90)
        score += missing_count * 100
        if model.get("quality_tier") in {"motion_master", "priority_static_interactive_candidate"}:
            score -= 5
        routes.append(
            ModelRoute(
                adapter_id=str(model.get("adapter_id")),
                family=str(model.get("family")),
                status=status,
                license=str(model.get("license", "unknown")),
                quality_tier=str(model.get("quality_tier", "unknown")),
                score=score,
                installed=installed,
                notes=str(model.get("notes", "")),
            )
        )

    routes.sort(key=lambda route: (route.score, route.family.lower()))
    return routes


def format_routes(routes: Iterable[ModelRoute]) -> str:
    rows = []
    for route in routes:
        rows.append(
            f"{route.adapter_id}: {route.family} | status={route.status} | "
            f"quality={route.quality_tier} | license={route.license} | score={route.score}"
        )
    return "\n".join(rows) if rows else "NO_COMPATIBLE_ROUTE"


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate an Asset Studio spec and show compatible model routes.")
    parser.add_argument("spec", type=Path, help="Path to an asset spec JSON file")
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--include-uninstalled", action="store_true")
    args = parser.parse_args()

    schema = load_json(args.schema)
    registry = load_json(args.registry)
    spec = load_json(args.spec)
    errors = validate_spec(spec, schema)
    if errors:
        for error in errors:
            print(f"SPEC_ERROR: {error}")
        return 2

    required = sorted(infer_required_capabilities(spec))
    print("SPEC_OK")
    print("required_capabilities=" + ",".join(required))
    routes = route_models(spec, registry, include_uninstalled=args.include_uninstalled)
    print(format_routes(routes))
    return 0 if routes else 3


if __name__ == "__main__":
    raise SystemExit(main())
