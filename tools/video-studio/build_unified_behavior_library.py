#!/usr/bin/env python3
"""Build João's unified source-preserving motion-unit library.

This is a metadata/library construction step only. No pose inference, rendering or
Wan-Animate-2 invocation occurs. Curated per-source policies remain authoritative;
the unified library does not flatten different source roles into one generic score.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path


def load(path: Path):
    if not path.is_file():
        raise SystemExit(f"Missing input: {path}")
    return json.loads(path.read_text(encoding="utf-8-sig"))


def manifest_map(manifest):
    return {str(u["id"]): u for u in (manifest.get("motion_units") or [])}


def role(enabled=False, weight=0.0, priority_tier=None):
    return {
        "enabled": bool(enabled),
        "weight": round(float(weight or 0.0), 6) if enabled else 0.0,
        "priority_tier": int(priority_tier) if enabled and priority_tier is not None else None,
    }


def base_entry(source_key, source_role, manifest_unit, curated_unit, pose_track, roles):
    return {
        "library_unit_id": f"{source_key}:{manifest_unit['id']}",
        "source_key": source_key,
        "source_file": manifest_unit.get("source_file"),
        "source_role": source_role,
        "source_unit_id": manifest_unit["id"],
        "source_start_s": float(manifest_unit["start_s"]),
        "source_end_s": float(manifest_unit["end_s"]),
        "duration_s": float(manifest_unit["duration_s"]),
        "source_video": (manifest_unit.get("rgb_span") or {}).get("source_path"),
        "pose_track": str(pose_track),
        "speech": manifest_unit.get("speech"),
        "prosody": manifest_unit.get("prosody"),
        "transition": manifest_unit.get("transition"),
        "motion_energy": manifest_unit.get("motion_energy"),
        "head_motion": manifest_unit.get("head_motion"),
        "body_activity": manifest_unit.get("body_activity"),
        "hand_activity": manifest_unit.get("hand_activity"),
        "pose_start": manifest_unit.get("pose_start"),
        "pose_end": manifest_unit.get("pose_end"),
        "review_tags": curated_unit.get("review_tags") or [],
        "roles": roles,
    }


def primary_entries(manifest, curated, manifest_path):
    mm = manifest_map(manifest)
    source_key = "primary"
    pose_track = manifest_path.parent / "pose_coco133.jsonl"
    out = []
    for u in curated.get("units") or []:
        if not bool(u.get("eligible")):
            continue
        mu = mm.get(str(u["id"]))
        if mu is None:
            raise SystemExit(f"Primary curated unit missing from manifest: {u['id']}")
        q = u.get("quality_weights") or {}
        roles = {
            "face": role(),
            "head": role(float(q.get("head") or 0) > 0, q.get("head"), 1),
            "posture": role(float(q.get("body") or 0) > 0, q.get("body"), 0),
            "coarse_arm": role(float(q.get("body") or 0) > 0, q.get("body"), 0),
            "left_hand": role(float(q.get("left_hand") or 0) > 0, q.get("left_hand"), 0),
            "right_hand": role(float(q.get("right_hand") or 0) > 0, q.get("right_hand"), 0),
            "both_hands": role(float(q.get("both_hands") or 0) > 0, q.get("both_hands"), 0),
            "generic_whole_upper": role(float(q.get("whole_upper") or 0) > 0, q.get("whole_upper"), 0),
            "body_support": role(float(q.get("body") or 0) > 0, q.get("body"), 0),
        }
        out.append(base_entry(source_key, curated.get("source_role"), mu, u, pose_track, roles))
    return out


def secondary_entries(manifest, curated, manifest_path):
    mm = manifest_map(manifest)
    source_key = "secondary"
    pose_track = manifest_path.parent / "pose_coco133.jsonl"
    out = []
    for u in curated.get("units") or []:
        rr = u.get("retrieval_roles") or {}
        if not any(bool((v or {}).get("enabled")) for v in rr.values()):
            continue
        mu = mm.get(str(u["id"]))
        if mu is None:
            raise SystemExit(f"Secondary curated unit missing from manifest: {u['id']}")
        fq = rr.get("face") or {}
        hq = rr.get("head") or {}
        bq = rr.get("body_support") or {}
        roles = {
            "face": role(fq.get("enabled"), fq.get("weight"), 0),
            "head": role(hq.get("enabled"), hq.get("weight"), 0),
            "posture": role(bq.get("enabled"), bq.get("weight"), 2),
            "coarse_arm": role(),
            "left_hand": role(),
            "right_hand": role(),
            "both_hands": role(),
            "generic_whole_upper": role(),
            "body_support": role(bq.get("enabled"), bq.get("weight"), 0),
        }
        out.append(base_entry(source_key, curated.get("source_role"), mu, u, pose_track, roles))
    return out


def tertiary_entries(manifest, curated, manifest_path):
    mm = manifest_map(manifest)
    source_key = "tertiary"
    pose_track = manifest_path.parent / "pose_coco133.jsonl"
    out = []
    for u in curated.get("units") or []:
        rr = u.get("retrieval_roles") or {}
        if not any(bool((v or {}).get("enabled")) for v in rr.values()):
            continue
        mu = mm.get(str(u["id"]))
        if mu is None:
            raise SystemExit(f"Tertiary curated unit missing from manifest: {u['id']}")
        hq = rr.get("head") or {}
        pq = rr.get("posture") or {}
        aq = rr.get("coarse_arm") or {}
        roles = {
            "face": role(),
            "head": role(hq.get("enabled"), hq.get("weight"), 2),
            "posture": role(pq.get("enabled"), pq.get("weight"), 1),
            "coarse_arm": role(aq.get("enabled"), aq.get("weight"), 1),
            "left_hand": role(),
            "right_hand": role(),
            "both_hands": role(),
            "generic_whole_upper": role(),
            "body_support": role(pq.get("enabled"), pq.get("weight"), 1),
        }
        out.append(base_entry(source_key, curated.get("source_role"), mu, u, pose_track, roles))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--primary-manifest", type=Path, required=True)
    ap.add_argument("--primary-curated", type=Path, required=True)
    ap.add_argument("--secondary-manifest", type=Path, required=True)
    ap.add_argument("--secondary-curated", type=Path, required=True)
    ap.add_argument("--tertiary-manifest", type=Path, required=True)
    ap.add_argument("--tertiary-curated", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    pm, pc = load(args.primary_manifest), load(args.primary_curated)
    sm, sc = load(args.secondary_manifest), load(args.secondary_curated)
    tm, tc = load(args.tertiary_manifest), load(args.tertiary_curated)

    units = []
    units += primary_entries(pm, pc, args.primary_manifest)
    units += secondary_entries(sm, sc, args.secondary_manifest)
    units += tertiary_entries(tm, tc, args.tertiary_manifest)

    role_counts = Counter()
    source_counts = Counter()
    role_source_counts = defaultdict(Counter)
    for u in units:
        source_counts[u["source_key"]] += 1
        for name, r in u["roles"].items():
            if r["enabled"]:
                role_counts[name] += 1
                role_source_counts[name][u["source_key"]] += 1

    out = {
        "schema": "joao-motion-library/v1",
        "subject_id": "joao",
        "source_preserving": True,
        "policy": {
            "face": "secondary source first; facial-behavior sidecar quality is authoritative",
            "head": "secondary tier 0, primary tier 1, SIENA tier 2",
            "posture": "primary tier 0, SIENA tier 1, secondary body-support tier 2",
            "coarse_arm": "primary tier 0, SIENA tier 1",
            "hands": "primary only",
            "generic_whole_upper": "primary only",
            "semantic_exclusions": "already applied per source before library construction",
            "selection": "priority tier constrains preferred source role; continuous quality weight ranks candidates inside compatible tiers; activity/prosody/transition/diversity are matching features, not substitutes for quality",
        },
        "sources": {
            "primary": {"file": pc.get("source_file"), "role": pc.get("source_role"), "curated_units": source_counts["primary"]},
            "secondary": {"file": sc.get("source_file"), "role": sc.get("source_role"), "curated_units": source_counts["secondary"]},
            "tertiary": {"file": tc.get("source_file"), "role": tc.get("source_role"), "curated_units": source_counts["tertiary"]},
        },
        "units_total": len(units),
        "role_counts": dict(role_counts),
        "role_source_counts": {k: dict(v) for k, v in role_source_counts.items()},
        "units": units,
    }

    required = {
        "face": 1,
        "head": 1,
        "posture": 1,
        "coarse_arm": 1,
        "left_hand": 1,
        "right_hand": 1,
        "both_hands": 1,
    }
    missing = [k for k, minimum in required.items() if role_counts[k] < minimum]
    if missing:
        raise SystemExit("Unified library missing required retrieval roles: " + ", ".join(missing))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

    print("UNIFIED JOAO BEHAVIOR LIBRARY")
    print("=============================")
    print(f"Units total: {out['units_total']}")
    print(f"Source units: primary={source_counts['primary']} secondary={source_counts['secondary']} tertiary={source_counts['tertiary']}")
    for name in ("face", "head", "posture", "coarse_arm", "left_hand", "right_hand", "both_hands", "generic_whole_upper", "body_support"):
        print(f"Role {name}: {role_counts[name]} candidates / sources={dict(role_source_counts[name])}")
    print(f"Library: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
