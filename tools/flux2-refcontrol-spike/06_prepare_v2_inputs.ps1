param(
    [string]$Workspace = 'D:\AI\Flux2RefControlSpike',
    [string]$Master = 'D:\GOOGLE DRIVE\DEV\Roguelite\assets\source\characters\exilada\reference\exilada_master.png',
    [int]$CanvasWidth = 768,
    [int]$CanvasHeight = 1024,
    [long]$Seed = 20260904
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$PortableRoot = Join-Path $Workspace 'ComfyUI_windows_portable'
$ComfyRoot = Join-Path $PortableRoot 'ComfyUI'
$EmbeddedPython = Join-Path $PortableRoot 'python_embeded\python.exe'
$InputDir = Join-Path $ComfyRoot 'input'
$PoseInputDir = Join-Path $InputDir 'refcontrol_poses_v2'
$PoseSpecDir = Join-Path $Workspace 'pose_specs_v2'
$CopiedMaster = Join-Path $InputDir 'exilada_master.png'
$GeneratorPath = Join-Path $Workspace '_make_walk_skeletons_v2.py'
$ManifestPath = Join-Path $Workspace 'input_manifest_v2.json'

Write-Host ''
Write-Host 'FLUX.2 Klein + RefControl Pose - STEP 7A: PREPARE V2 WALK INPUTS' -ForegroundColor Cyan
Write-Host 'Goal: reduce limb ambiguity while keeping the V1 model/seed/render settings unchanged.'
Write-Host 'NO model is loaded. NO inference is performed.' -ForegroundColor Yellow
Write-Host ''

if (-not (Test-Path $EmbeddedPython -PathType Leaf)) { throw "Embedded Python not found: $EmbeddedPython" }
if (-not (Test-Path $Master -PathType Leaf)) { throw "Canonical Exilada master not found: $Master" }
if ($CanvasWidth -ne 768 -or $CanvasHeight -ne 1024) {
    throw "V2 comparison contract requires the same 768x1024 canvas used by V1. Got ${CanvasWidth}x${CanvasHeight}."
}
if ($Seed -ne 20260904) { throw "V2 comparison contract requires seed 20260904. Got $Seed." }

New-Item -ItemType Directory -Force -Path $InputDir | Out-Null
New-Item -ItemType Directory -Force -Path $PoseInputDir | Out-Null
New-Item -ItemType Directory -Force -Path $PoseSpecDir | Out-Null

Copy-Item -LiteralPath $Master -Destination $CopiedMaster -Force
$SourceHash = (Get-FileHash -LiteralPath $Master -Algorithm SHA256).Hash.ToLowerInvariant()
$CopyHash = (Get-FileHash -LiteralPath $CopiedMaster -Algorithm SHA256).Hash.ToLowerInvariant()
if ($SourceHash -ne $CopyHash) { throw 'Copied Exilada master hash does not match canonical source.' }

$generator = @'
import argparse
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageDraw

LABELS = [
    "NOSE", "NECK",
    "RIGHT SHOULDER", "RIGHT ELBOW", "RIGHT WRIST",
    "LEFT SHOULDER", "LEFT ELBOW", "LEFT WRIST",
    "RIGHT HIP", "RIGHT KNEE", "RIGHT ANKLE",
    "LEFT HIP", "LEFT KNEE", "LEFT ANKLE",
    "RIGHT EYE", "LEFT EYE", "RIGHT EAR", "LEFT EAR",
]

LIMBS = [
    (1, 2), (2, 3), (3, 4),
    (1, 5), (5, 6), (6, 7),
    (1, 8), (8, 9), (9, 10),
    (1, 11), (11, 12), (12, 13),
    (1, 0), (0, 14), (14, 16),
    (0, 15), (15, 17),
]

COLORS = [
    (255, 0, 0), (255, 85, 0), (255, 170, 0), (255, 255, 0),
    (170, 255, 0), (85, 255, 0), (0, 255, 0), (0, 255, 85),
    (0, 255, 170), (0, 255, 255), (0, 170, 255), (0, 85, 255),
    (0, 0, 255), (85, 0, 255), (170, 0, 255), (255, 0, 255),
    (255, 0, 170), (255, 0, 85),
]

# V2 principles:
# - same 768x1024 COCO-18 contract as V1;
# - no arm crosses the torso centerline: shoulders/elbows/wrists remain clearly separated;
# - knees and ankles have larger screen-space separation to reduce leg/foot ambiguity;
# - left/right gait phases use the same clean non-crossing screen-space trajectories,
#   with COCO left/right colors assigning which anatomical leg occupies each trajectory;
# - feet are still inferred by the renderer (COCO-18 has ankle but no toe/heel joints),
#   so toe orientation is additionally constrained by the V2 text prompt.
POSES = {
    "pose_00_contact_L_v2": [
        (0.500, 0.105), (0.500, 0.185),
        (0.445, 0.205), (0.420, 0.305), (0.395, 0.380),
        (0.555, 0.205), (0.585, 0.305), (0.615, 0.420),
        (0.475, 0.455), (0.425, 0.650), (0.350, 0.875),
        (0.525, 0.455), (0.575, 0.645), (0.650, 0.875),
        (0.480, 0.095), (0.520, 0.095), (0.458, 0.105), (0.542, 0.105),
    ],
    "pose_01_passing_L_v2": [
        (0.500, 0.100), (0.500, 0.180),
        (0.445, 0.200), (0.415, 0.305), (0.395, 0.395),
        (0.555, 0.200), (0.585, 0.305), (0.615, 0.395),
        (0.475, 0.450), (0.455, 0.650), (0.445, 0.870),
        (0.525, 0.450), (0.575, 0.605), (0.535, 0.735),
        (0.480, 0.090), (0.520, 0.090), (0.458, 0.100), (0.542, 0.100),
    ],
    "pose_02_contact_R_v2": [
        (0.500, 0.105), (0.500, 0.185),
        (0.445, 0.205), (0.420, 0.315), (0.395, 0.420),
        (0.555, 0.205), (0.585, 0.295), (0.615, 0.380),
        (0.525, 0.455), (0.575, 0.645), (0.650, 0.875),
        (0.475, 0.455), (0.425, 0.650), (0.350, 0.875),
        (0.480, 0.095), (0.520, 0.095), (0.458, 0.105), (0.542, 0.105),
    ],
    "pose_03_passing_R_v2": [
        (0.500, 0.100), (0.500, 0.180),
        (0.445, 0.200), (0.415, 0.305), (0.395, 0.395),
        (0.555, 0.200), (0.585, 0.305), (0.605, 0.395),
        (0.525, 0.450), (0.575, 0.605), (0.535, 0.735),
        (0.475, 0.450), (0.455, 0.650), (0.445, 0.870),
        (0.480, 0.090), (0.520, 0.090), (0.458, 0.100), (0.542, 0.100),
    ],
}

POSE_NOTES = {
    "pose_00_contact_L_v2": "contact phase; left leg forward, right leg trailing; both arms kept outside torso centerline",
    "pose_01_passing_L_v2": "passing phase; right leg planted, left leg lifted/passing; left/right arms remain separately readable",
    "pose_02_contact_R_v2": "opposite contact phase; right leg forward, left leg trailing; both arms kept outside torso centerline",
    "pose_03_passing_R_v2": "opposite passing phase; left leg planted, right leg lifted/passing; left/right arms remain separately readable",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def render_pose(name, points_norm, width, height, pose_dir, spec_dir):
    points = [(round(x * width), round(y * height)) for x, y in points_norm]
    if len(points) != 18:
        raise RuntimeError(f"{name}: expected 18 keypoints, got {len(points)}")

    image = Image.new("RGB", (width, height), (0, 0, 0))
    draw = ImageDraw.Draw(image)
    limb_width = max(5, round(min(width, height) * 0.012))
    radius = max(4, round(min(width, height) * 0.010))

    for a, b in LIMBS:
        draw.line([points[a], points[b]], fill=COLORS[a % len(COLORS)], width=limb_width)
    for i, (x, y) in enumerate(points):
        c = COLORS[i]
        draw.ellipse((x-radius, y-radius, x+radius, y+radius), fill=c)

    png_path = pose_dir / f"{name}.png"
    image.save(png_path, format="PNG", optimize=False)

    spec = {
        "format": "openpose_coco18",
        "revision": "v2_walk_anatomy_clarity",
        "pose_name": name,
        "pose_note": POSE_NOTES[name],
        "canvas": [width, height],
        "movement_direction": "screen_right",
        "renderer_foot_constraint": "both bare feet and toes must point toward screen-right; COCO-18 provides ankle only",
        "continuity_contract": [
            "same anatomical left/right limbs across all frames",
            "do not mirror or swap shackle/chain topology from identity reference",
            "same body proportions, scars, cloth layout and hair mass across frames",
        ],
        "keypoint_order": LABELS,
        "keypoints_normalized": [
            {"label": label, "x": x, "y": y}
            for label, (x, y) in zip(LABELS, points_norm)
        ],
        "keypoints_pixels": [
            {"label": label, "x": x, "y": y}
            for label, (x, y) in zip(LABELS, points)
        ],
        "png_sha256": sha256(png_path),
    }
    json_path = spec_dir / f"{name}.json"
    json_path.write_text(json.dumps(spec, indent=2), encoding="utf-8")
    return png_path, json_path, spec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pose-dir", required=True)
    ap.add_argument("--spec-dir", required=True)
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--master", required=True)
    ap.add_argument("--master-sha256", required=True)
    ap.add_argument("--width", type=int, required=True)
    ap.add_argument("--height", type=int, required=True)
    ap.add_argument("--seed", type=int, required=True)
    args = ap.parse_args()

    pose_dir = Path(args.pose_dir)
    spec_dir = Path(args.spec_dir)
    pose_dir.mkdir(parents=True, exist_ok=True)
    spec_dir.mkdir(parents=True, exist_ok=True)

    for name in POSES:
        for p in (pose_dir / f"{name}.png", spec_dir / f"{name}.json"):
            if p.exists():
                p.unlink()

    produced = []
    for name, pts in POSES.items():
        png_path, json_path, spec = render_pose(name, pts, args.width, args.height, pose_dir, spec_dir)
        produced.append({
            "pose_name": name,
            "pose_note": POSE_NOTES[name],
            "png": str(png_path),
            "json": str(json_path),
            "png_sha256": spec["png_sha256"],
        })

    manifest = {
        "spike": "FLUX.2 Klein Base 4B FP8 + RefControl Pose",
        "revision": "v2_walk_anatomy_clarity",
        "stage": "v2_inputs_prepared_no_inference",
        "canonical_master": str(Path(args.master)),
        "canonical_master_sha256": args.master_sha256,
        "canvas": [args.width, args.height],
        "seed_reserved_for_generation": args.seed,
        "pose_format": "OpenPose-style COCO-18 PNG on black background",
        "controlled_changes_vs_v1": [
            "arm geometry avoids torso-centerline crossings",
            "leg/ankle screen-space separation increased",
            "text prompt will explicitly constrain feet/toes and exact shackle-chain topology",
        ],
        "unchanged_vs_v1": [
            "canonical identity master",
            "FLUX.2 Klein Base 4B FP8",
            "RefControl Pose LoRA strength 1.0",
            "seed 20260904",
            "768x1024 output",
            "20 steps",
            "CFG 5.0",
            "Euler sampler",
            "one-shot/no-retry policy",
        ],
        "poses": produced,
        "network_access": False,
        "model_loaded": False,
        "inference_performed": False,
    }
    Path(args.manifest).write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    if len(produced) != 4:
        raise RuntimeError(f"Expected 4 poses, produced {len(produced)}")
    print(f"generated_v2_poses={len(produced)}")
    for item in produced:
        print(f"{item['pose_name']} sha256={item['png_sha256']}")


if __name__ == "__main__":
    main()
'@

[System.IO.File]::WriteAllText($GeneratorPath, $generator, [System.Text.UTF8Encoding]::new($false))
try {
    & $EmbeddedPython $GeneratorPath `
        --pose-dir $PoseInputDir `
        --spec-dir $PoseSpecDir `
        --manifest $ManifestPath `
        --master $Master `
        --master-sha256 $SourceHash `
        --width $CanvasWidth `
        --height $CanvasHeight `
        --seed $Seed
    if ($LASTEXITCODE -ne 0) { throw "V2 skeleton generator failed with exit code $LASTEXITCODE" }
}
finally {
    Remove-Item $GeneratorPath -Force -ErrorAction SilentlyContinue
}

$ExpectedPoses = @(
    'pose_00_contact_L_v2',
    'pose_01_passing_L_v2',
    'pose_02_contact_R_v2',
    'pose_03_passing_R_v2'
)
foreach ($name in $ExpectedPoses) {
    if (-not (Test-Path (Join-Path $PoseInputDir ($name + '.png')) -PathType Leaf)) { throw "Missing V2 pose PNG: $name" }
    if (-not (Test-Path (Join-Path $PoseSpecDir ($name + '.json')) -PathType Leaf)) { throw "Missing V2 pose JSON: $name" }
}
if (-not (Test-Path $ManifestPath -PathType Leaf)) { throw "Missing V2 manifest: $ManifestPath" }

Write-Host ''
Write-Host 'STEP 7A: PASS' -ForegroundColor Green
Write-Host "V2 poses:    $PoseInputDir"
Write-Host "V2 specs:    $PoseSpecDir"
Write-Host "V2 manifest: $ManifestPath"
Write-Host 'No inference was performed.' -ForegroundColor Green
