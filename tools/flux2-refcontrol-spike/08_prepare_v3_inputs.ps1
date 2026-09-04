param(
    [string]$Workspace = 'Z:\AI\Flux2RefControlSpike',
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
$PoseInputDir = Join-Path $InputDir 'refcontrol_poses_v3'
$PoseSpecDir = Join-Path $Workspace 'pose_specs_v3'
$CopiedMaster = Join-Path $InputDir 'exilada_master.png'
$GeneratorPath = Join-Path $Workspace '_make_walk_skeletons_v3.py'
$ManifestPath = Join-Path $Workspace 'input_manifest_v3.json'

Write-Host ''
Write-Host 'FLUX.2 Klein + RefControl Pose - STEP 8A: PREPARE V3 WALK INPUTS' -ForegroundColor Cyan
Write-Host 'Goal: restore real left/right gait alternation using four distinct screen-space skeleton geometries.'
Write-Host 'NO model is loaded. NO inference is performed.' -ForegroundColor Yellow
Write-Host ''

if (-not (Test-Path $EmbeddedPython -PathType Leaf)) { throw "Embedded Python not found: $EmbeddedPython" }
if (-not (Test-Path $Master -PathType Leaf)) { throw "Canonical Exilada master not found: $Master" }
if ($CanvasWidth -ne 768 -or $CanvasHeight -ne 1024) {
    throw "V3 comparison contract requires 768x1024. Got ${CanvasWidth}x${CanvasHeight}."
}
if ($Seed -ne 20260904) { throw "V3 comparison contract requires seed 20260904. Got $Seed." }

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

# V3 fixes the central V2 failure: V2 used nearly identical screen-space
# silhouettes for L/R pairs and relied too heavily on COCO left/right colors.
# RefControl rendered those pairs as nearly repeated poses.
#
# V3 contract:
# - every gait phase has genuinely different screen-space geometry;
# - no leg crossing/X shapes;
# - support vs swing legs are visually distinct;
# - arm opposition also changes geometry between opposite phases;
# - 3/4 side-facing-right bias is encoded with a slight head/torso asymmetry;
# - binary silhouette hashes must be unique across all four controls.
POSES = {
    "pose_00_contact_L_v3": [
        (0.530, 0.105), (0.515, 0.185),
        (0.460, 0.205), (0.435, 0.300), (0.465, 0.395),
        (0.565, 0.205), (0.600, 0.315), (0.635, 0.410),
        (0.475, 0.455), (0.430, 0.650), (0.360, 0.835),
        (0.540, 0.450), (0.615, 0.640), (0.700, 0.890),
        (0.510, 0.095), (0.550, 0.095), (0.490, 0.105), (0.570, 0.105),
    ],
    "pose_01_passing_L_v3": [
        (0.530, 0.100), (0.515, 0.180),
        (0.460, 0.200), (0.445, 0.300), (0.495, 0.390),
        (0.565, 0.200), (0.600, 0.305), (0.645, 0.395),
        (0.475, 0.450), (0.490, 0.650), (0.475, 0.880),
        (0.540, 0.445), (0.620, 0.600), (0.585, 0.745),
        (0.510, 0.090), (0.550, 0.090), (0.490, 0.100), (0.570, 0.100),
    ],
    "pose_02_contact_R_v3": [
        (0.530, 0.105), (0.520, 0.185),
        (0.465, 0.205), (0.425, 0.315), (0.390, 0.420),
        (0.570, 0.205), (0.580, 0.300), (0.545, 0.390),
        (0.535, 0.455), (0.580, 0.650), (0.640, 0.860),
        (0.470, 0.450), (0.445, 0.660), (0.405, 0.905),
        (0.510, 0.095), (0.550, 0.095), (0.490, 0.105), (0.570, 0.105),
    ],
    "pose_03_passing_R_v3": [
        (0.530, 0.100), (0.520, 0.180),
        (0.465, 0.200), (0.425, 0.300), (0.390, 0.390),
        (0.570, 0.200), (0.570, 0.305), (0.545, 0.395),
        (0.535, 0.450), (0.605, 0.590), (0.650, 0.730),
        (0.470, 0.445), (0.460, 0.655), (0.445, 0.895),
        (0.510, 0.090), (0.550, 0.090), (0.490, 0.100), (0.570, 0.100),
    ],
}

POSE_NOTES = {
    "pose_00_contact_L_v3": "contact: anatomical left leg visibly leads toward screen-right; right leg visibly trails; wide near-leg stride",
    "pose_01_passing_L_v3": "passing: right leg is straight support; anatomical left knee is lifted forward with visible swing foot",
    "pose_02_contact_R_v3": "opposite contact: anatomical right leg visibly leads; left leg trails; intentionally different perspective/stride silhouette from contact_L",
    "pose_03_passing_R_v3": "opposite passing: left leg is straight support; anatomical right knee/foot swing forward with a different silhouette from passing_L",
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def to_pixels(points_norm, width, height):
    return [(round(x * width), round(y * height)) for x, y in points_norm]


def draw_pose(points, width, height, colored=True):
    image = Image.new("RGB", (width, height), (0, 0, 0))
    draw = ImageDraw.Draw(image)
    limb_width = max(5, round(min(width, height) * 0.012))
    radius = max(4, round(min(width, height) * 0.010))

    for a, b in LIMBS:
        color = COLORS[a % len(COLORS)] if colored else (255, 255, 255)
        draw.line([points[a], points[b]], fill=color, width=limb_width)
    for i, (x, y) in enumerate(points):
        color = COLORS[i] if colored else (255, 255, 255)
        draw.ellipse((x-radius, y-radius, x+radius, y+radius), fill=color)
    return image


def silhouette_hash(points, width, height):
    image = draw_pose(points, width, height, colored=False).convert("1")
    return sha256_bytes(image.tobytes())


def render_pose(name, points_norm, width, height, pose_dir, spec_dir):
    points = to_pixels(points_norm, width, height)
    if len(points) != 18:
        raise RuntimeError(f"{name}: expected 18 keypoints, got {len(points)}")

    image = draw_pose(points, width, height, colored=True)
    png_path = pose_dir / f"{name}.png"
    image.save(png_path, format="PNG", optimize=False)

    sil_hash = silhouette_hash(points, width, height)
    spec = {
        "format": "openpose_coco18",
        "revision": "v3_walk_distinct_screenspace",
        "pose_name": name,
        "pose_note": POSE_NOTES[name],
        "canvas": [width, height],
        "movement_direction": "screen_right",
        "view": "three-quarter side bias, facing screen-right",
        "renderer_foot_constraint": "both bare feet/toes must orient screen-right; COCO-18 controls ankles but not toe/heel joints",
        "silhouette_contract": "all four V3 skeletons must remain distinct even when COCO colors are removed",
        "continuity_contract": [
            "same adult Exilada identity and body proportions across all frames",
            "same anatomical left/right limbs across all frames",
            "both wrists and both ankles remain shackled",
            "do not swap restraint topology between anatomical sides",
            "same scars, cloth layout and dominant black hair mass as reference",
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
        "png_sha256": sha256_file(png_path),
        "binary_silhouette_sha256": sil_hash,
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
    silhouette_hashes = []
    for name, pts in POSES.items():
        png_path, json_path, spec = render_pose(name, pts, args.width, args.height, pose_dir, spec_dir)
        silhouette_hashes.append(spec["binary_silhouette_sha256"])
        produced.append({
            "pose_name": name,
            "pose_note": POSE_NOTES[name],
            "png": str(png_path),
            "json": str(json_path),
            "png_sha256": spec["png_sha256"],
            "binary_silhouette_sha256": spec["binary_silhouette_sha256"],
        })

    if len(set(silhouette_hashes)) != 4:
        raise RuntimeError("V3 silhouette gate failed: at least two controls become identical when COCO colors are removed")

    manifest = {
        "spike": "FLUX.2 Klein Base 4B FP8 + RefControl Pose",
        "revision": "v3_walk_distinct_screenspace",
        "stage": "v3_inputs_prepared_no_inference",
        "canonical_master": str(Path(args.master)),
        "canonical_master_sha256": args.master_sha256,
        "canvas": [args.width, args.height],
        "seed_reserved_for_generation": args.seed,
        "pose_format": "OpenPose-style COCO-18 PNG on black background",
        "v2_failure_addressed": "left/right pairs collapsed because their screen-space silhouettes were nearly repeated and differed mainly by COCO semantic colors",
        "v3_gate": "four binary silhouettes must be unique without COCO color semantics",
        "controlled_changes_vs_v2": [
            "genuinely different screen-space leg geometry for contact_L vs contact_R",
            "genuinely different screen-space support/swing geometry for passing_L vs passing_R",
            "different arm opposition geometry across opposite phases",
            "slight three-quarter facing-right asymmetry retained",
        ],
        "unchanged_vs_v2": [
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
        "silhouette_uniqueness_pass": True,
        "network_access": False,
        "model_loaded": False,
        "inference_performed": False,
    }
    Path(args.manifest).write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    if len(produced) != 4:
        raise RuntimeError(f"Expected 4 poses, produced {len(produced)}")
    print(f"generated_v3_poses={len(produced)}")
    print("silhouette_uniqueness=PASS")
    for item in produced:
        print(f"{item['pose_name']} sha256={item['png_sha256']} silhouette={item['binary_silhouette_sha256']}")


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
    if ($LASTEXITCODE -ne 0) { throw "V3 skeleton generator failed with exit code $LASTEXITCODE" }
}
finally {
    Remove-Item $GeneratorPath -Force -ErrorAction SilentlyContinue
}

$ExpectedPoses = @(
    'pose_00_contact_L_v3',
    'pose_01_passing_L_v3',
    'pose_02_contact_R_v3',
    'pose_03_passing_R_v3'
)
foreach ($name in $ExpectedPoses) {
    if (-not (Test-Path (Join-Path $PoseInputDir ($name + '.png')) -PathType Leaf)) { throw "Missing V3 pose PNG: $name" }
    if (-not (Test-Path (Join-Path $PoseSpecDir ($name + '.json')) -PathType Leaf)) { throw "Missing V3 pose JSON: $name" }
}
if (-not (Test-Path $ManifestPath -PathType Leaf)) { throw "Missing V3 manifest: $ManifestPath" }

$Manifest = Get-Content -LiteralPath $ManifestPath -Raw | ConvertFrom-Json
if ($Manifest.silhouette_uniqueness_pass -ne $true) { throw 'V3 silhouette uniqueness gate did not pass.' }

Write-Host ''
Write-Host 'STEP 8A: PASS' -ForegroundColor Green
Write-Host 'Four V3 controls were generated and their color-independent silhouettes are unique.'
Write-Host "V3 poses:    $PoseInputDir"
Write-Host "V3 specs:    $PoseSpecDir"
Write-Host "V3 manifest: $ManifestPath"
Write-Host 'No inference was performed. STOP HERE and inspect/share the four V3 skeleton PNGs.' -ForegroundColor Yellow
