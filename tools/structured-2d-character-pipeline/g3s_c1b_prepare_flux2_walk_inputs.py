#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageDraw

EXPECTED_BODY_SIZE = (37, 128)
EXPECTED_BODY_SHA256 = "702e2d95325049b5d99ea66db4fbbb9b41d6d24813efb0b1c3a37e112b1c2858"
LOGICAL = (96, 160)
UPSCALE = 6
MODEL = (LOGICAL[0] * UPSCALE, LOGICAL[1] * UPSCALE)
GROUND_Y = 152
BG = (228, 226, 222)
INK = (22, 24, 29)
JOINT = (70, 72, 78)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--guide", required=True)
    ap.add_argument("--approval", required=True)
    ap.add_argument("--spec", required=True)
    ap.add_argument("--body", required=True)
    ap.add_argument("--input-dir", required=True)
    ap.add_argument("--workspace", required=True)
    args = ap.parse_args()

    guide_path = Path(args.guide)
    approval_path = Path(args.approval)
    spec_path = Path(args.spec)
    body_path = Path(args.body)
    input_dir = Path(args.input_dir)
    workspace = Path(args.workspace)
    for p in (guide_path, approval_path, spec_path, body_path):
        if not p.is_file():
            raise FileNotFoundError(p)

    approval = json.loads(approval_path.read_text(encoding="utf-8-sig"))
    if approval.get("gate") != "G3S-C1A" or approval.get("status") != "PASS":
        raise RuntimeError("C1A skeleton walk is not approved PASS")
    guide = json.loads(guide_path.read_text(encoding="utf-8-sig"))
    if guide.get("gate") != "G3S-C1A" or guide.get("revision") != "SKELETON_ONLY_WALK_CYCLE_V1":
        raise RuntimeError("unexpected local C1A guide")
    spec = json.loads(spec_path.read_text(encoding="utf-8-sig"))
    if spec.get("gate") != "G3S-C1B" or spec.get("revision") != "FLUX2_EIGHT_POSE_VISUAL_PROOF_V1":
        raise RuntimeError("unexpected C1B spec")
    if len(guide.get("frames", [])) != 8:
        raise RuntimeError("C1A guide does not contain eight frames")

    body = Image.open(body_path).convert("RGBA")
    if body.size != EXPECTED_BODY_SIZE:
        raise RuntimeError(f"canonical body size changed: {body.size}")
    if sha256_file(body_path) != EXPECTED_BODY_SHA256:
        raise RuntimeError("canonical B3B body hash changed")

    input_dir.mkdir(parents=True, exist_ok=True)
    workspace.mkdir(parents=True, exist_ok=True)

    # Body reference: exact canonical pixels on the logical neutral field, integer enlarged.
    logical_body = Image.new("RGBA", LOGICAL, BG + (255,))
    bx = (LOGICAL[0] - body.width) // 2
    by = GROUND_Y - body.height
    logical_body.alpha_composite(body, (bx, by))
    body_model = logical_body.convert("RGB").resize(MODEL, Image.Resampling.NEAREST)
    body_ref = input_dir / "g3s_c1b_body_identity_reference.png"
    body_model.save(body_ref)
    logical_body.convert("RGB").save(workspace / "g3s_c1b_body_identity_reference_logical.png")

    chain_pairs = [
        ("head", "neck"), ("neck", "chest"), ("chest", "pelvis"),
        ("neck", "left_shoulder"), ("left_shoulder", "left_elbow"), ("left_elbow", "left_wrist"),
        ("neck", "right_shoulder"), ("right_shoulder", "right_elbow"), ("right_elbow", "right_wrist"),
        ("pelvis", "left_hip"), ("left_hip", "left_knee"), ("left_knee", "left_ankle"), ("left_ankle", "left_toe"),
        ("pelvis", "right_hip"), ("right_hip", "right_knee"), ("right_knee", "right_ankle"), ("right_ankle", "right_toe"),
    ]

    pose_refs = []
    for i, frame in enumerate(guide["frames"]):
        joints = frame["joints"]
        required = {name for pair in chain_pairs for name in pair}
        missing = sorted(required.difference(joints))
        if missing:
            raise RuntimeError(f"frame {i} missing joints: {missing}")

        foot_y = max(float(joints[k]["y"]) for k in ("left_ankle", "left_toe", "right_ankle", "right_toe"))
        head_y = float(joints["head"]["y"])
        height = foot_y - head_y
        if height <= 1.0:
            raise RuntimeError(f"frame {i} invalid projected skeleton height: {height}")
        scale = 128.0 / height
        pelvis_x = float(joints["pelvis"]["x"])

        def xy(name: str):
            x = 48.0 + (float(joints[name]["x"]) - pelvis_x) * scale
            y = float(GROUND_Y) + (float(joints[name]["y"]) - foot_y) * scale
            return (x, y)

        logical = Image.new("RGB", LOGICAL, BG)
        d = ImageDraw.Draw(logical)
        # Ground cue is deliberately minimal and not appearance information.
        d.line((8, GROUND_Y, LOGICAL[0]-8, GROUND_Y), fill=(176, 172, 166), width=1)
        for a, b in chain_pairs:
            d.line((xy(a), xy(b)), fill=INK, width=3)
        for name in required:
            x, y = xy(name)
            r = 2 if name not in ("head", "pelvis") else 3
            d.ellipse((x-r, y-r, x+r, y+r), fill=JOINT)
        # Explicit head volume cue, still skeletal/control-only.
        hx, hy = xy("head")
        d.ellipse((hx-4, hy-5, hx+4, hy+5), outline=INK, width=2)

        event = str(frame["event"])
        logical_path = workspace / f"g3s_c1b_pose_{i:02d}_{event}_logical.png"
        model_path = input_dir / f"g3s_c1b_pose_{i:02d}_{event}.png"
        logical.save(logical_path)
        logical.resize(MODEL, Image.Resampling.NEAREST).save(model_path)
        pose_refs.append({
            "index": i,
            "frame": int(frame["frame"]),
            "event": event,
            "support_foot": str(frame["support_foot"]),
            "logical": str(logical_path),
            "model_input": str(model_path),
            "model_input_name": model_path.name,
            "near_side": str(frame["near_anatomical_side"]),
            "far_side": str(frame["far_anatomical_side"]),
        })

    manifest = {
        "gate": "G3S-C1B",
        "revision": "FLUX2_EIGHT_POSE_INPUTS_V1",
        "status": "PREPARED",
        "body_reference": str(body_ref),
        "body_reference_name": body_ref.name,
        "canonical_body_sha256": EXPECTED_BODY_SHA256,
        "logical_canvas": list(LOGICAL),
        "model_canvas": list(MODEL),
        "integer_scale": UPSCALE,
        "ground_y": GROUND_Y,
        "pose_refs": pose_refs,
        "note": "Pose images are skeleton-derived control references only. Body reference is exact B3B identity/style conditioning. Neither is a production walk sprite."
    }
    manifest_path = workspace / "g3s_c1b_input_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print("G3S-C1B INPUT PREP: PASS")
    print(f"BODY_REF={body_ref}")
    print(f"POSE_COUNT={len(pose_refs)}")
    print(f"MANIFEST={manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
