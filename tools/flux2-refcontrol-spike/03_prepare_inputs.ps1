param(
    [string]$RepoRoot = 'D:\GOOGLE DRIVE\DEV\Roguelite',
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
$PoseInputDir = Join-Path $InputDir 'refcontrol_poses'
$PoseSpecDir = Join-Path $Workspace 'pose_specs'
$CopiedMaster = Join-Path $InputDir 'exilada_master.png'
$GeneratorPath = Join-Path $Workspace '_make_walk_skeletons.py'
$ManifestPath = Join-Path $Workspace 'input_manifest.json'

Write-Host ''
Write-Host 'FLUX.2 Klein + RefControl Pose spike - STEP 4: prepare inputs only' -ForegroundColor Cyan
Write-Host 'This step copies the canonical Exilada master byte-for-byte and generates four deterministic COCO-18 skeleton PNGs.'
Write-Host 'NO model is loaded. NO inference is performed. NO network access is used.'
Write-Host ''

if (-not (Test-Path $EmbeddedPython -PathType Leaf)) {
    throw "Embedded Python not found: $EmbeddedPython"
}
if (-not (Test-Path $Master -PathType Leaf)) {
    throw "Canonical Exilada master not found: $Master"
}
if ($CanvasWidth -lt 256 -or $CanvasHeight -lt 256) {
    throw 'Canvas is unexpectedly small.'
}

New-Item -ItemType Directory -Force -Path $InputDir | Out-Null
New-Item -ItemType Directory -Force -Path $PoseInputDir | Out-Null
New-Item -ItemType Directory -Force -Path $PoseSpecDir | Out-Null

# Copy the canonical master without resampling, compositing, conversion, or metadata editing.
Copy-Item -LiteralPath $Master -Destination $CopiedMaster -Force
$SourceHash = (Get-FileHash -LiteralPath $Master -Algorithm SHA256).Hash.ToLowerInvariant()
$CopyHash = (Get-FileHash -LiteralPath $CopiedMaster -Algorithm SHA256).Hash.ToLowerInvariant()
if ($SourceHash -ne $CopyHash) {
    throw 'Copied Exilada master hash does not match canonical source.'
}
Write-Host "[OK] Canonical master copied byte-for-byte: $CopiedMaster" -ForegroundColor Green
Write-Host "[OK] master_sha256=$SourceHash" -ForegroundColor Green

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

# OpenPose/COCO-18-style limb topology.
LIMBS = [
    (1, 2), (2, 3), (3, 4),
    (1, 5), (5, 6), (6, 7),
    (1, 8), (8, 9), (9, 10),
    (1, 11), (11, 12), (12, 13),
    (1, 0), (0, 14), (14, 16),
    (0, 15), (15, 17),
]

# Common OpenPose-style rainbow palette, one color per COCO-18 joint.
COLORS = [
    (255, 0, 0), (255, 85, 0), (255, 170, 0), (255, 255, 0),
    (170, 255, 0), (85, 255, 0), (0, 255, 0), (0, 255, 85),
    (0, 255, 170), (0, 255, 255), (0, 170, 255), (0, 85, 255),
    (0, 0, 255), (85, 0, 255), (170, 0, 255), (255, 0, 255),
    (255, 0, 170), (255, 0, 85),
]

# Normalized keypoints in the exact COCO-18 label order above.
# Four deterministic fundamental walk poses: contact L, passing L, contact R, passing R.
# No random numbers are used to build the geometry.
POSES = {
    "pose_00_contact_L": [
        (0.500, 0.105), (0.500, 0.185),
        (0.445, 0.205), (0.420, 0.310), (0.595, 0.395),
        (0.555, 0.205), (0.585, 0.300), (0.360, 0.390),
        (0.468, 0.455), (0.430, 0.650), (0.365, 0.875),
        (0.532, 0.455), (0.565, 0.650), (0.635, 0.875),
        (0.480, 0.095), (0.520, 0.095), (0.458, 0.105), (0.542, 0.105),
    ],
    "pose_01_passing_L": [
        (0.500, 0.098), (0.500, 0.178),
        (0.445, 0.198), (0.405, 0.300), (0.555, 0.370),
        (0.555, 0.198), (0.595, 0.300), (0.445, 0.370),
        (0.468, 0.448), (0.470, 0.650), (0.468, 0.865),
        (0.532, 0.448), (0.575, 0.610), (0.535, 0.735),
        (0.480, 0.088), (0.520, 0.088), (0.458, 0.098), (0.542, 0.098),
    ],
    "pose_02_contact_R": [
        (0.500, 0.105), (0.500, 0.185),
        (0.445, 0.205), (0.415, 0.300), (0.640, 0.390),
        (0.555, 0.205), (0.580, 0.310), (0.405, 0.395),
        (0.468, 0.455), (0.435, 0.650), (0.635, 0.875),
        (0.532, 0.455), (0.570, 0.650), (0.365, 0.875),
        (0.480, 0.095), (0.520, 0.095), (0.458, 0.105), (0.542, 0.105),
    ],
    "pose_03_passing_R": [
        (0.500, 0.098), (0.500, 0.178),
        (0.445, 0.198), (0.405, 0.300), (0.445, 0.370),
        (0.555, 0.198), (0.595, 0.300), (0.555, 0.370),
        (0.468, 0.448), (0.425, 0.610), (0.465, 0.735),
        (0.532, 0.448), (0.530, 0.650), (0.532, 0.865),
        (0.480, 0.088), (0.520, 0.088), (0.458, 0.098), (0.542, 0.098),
    ],
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def render_pose(name: str, points_norm, width: int, height: int, pose_dir: Path, spec_dir: Path):
    points = [(round(x * width), round(y * height)) for x, y in points_norm]
    if len(points) != 18:
        raise RuntimeError(f"{name}: expected 18 keypoints, got {len(points)}")

    image = Image.new("RGB", (width, height), (0, 0, 0))
    draw = ImageDraw.Draw(image)
    limb_width = max(5, round(min(width, height) * 0.012))
    radius = max(4, round(min(width, height) * 0.010))

    for limb_index, (a, b) in enumerate(LIMBS):
        draw.line([points[a], points[b]], fill=COLORS[a % len(COLORS)], width=limb_width)

    for i, (x, y) in enumerate(points):
        c = COLORS[i]
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=c)

    png_path = pose_dir / f"{name}.png"
    image.save(png_path, format="PNG", optimize=False)

    spec = {
        "format": "openpose_coco18",
        "pose_name": name,
        "canvas": [width, height],
        "background_rgb": [0, 0, 0],
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

    # Remove only prior deterministic spike outputs, never arbitrary files.
    for name in POSES:
        for p in (pose_dir / f"{name}.png", spec_dir / f"{name}.json"):
            if p.exists():
                p.unlink()

    produced = []
    for name, pts in POSES.items():
        png_path, json_path, spec = render_pose(name, pts, args.width, args.height, pose_dir, spec_dir)
        produced.append({
            "pose_name": name,
            "png": str(png_path),
            "json": str(json_path),
            "png_sha256": spec["png_sha256"],
        })

    manifest = {
        "spike": "FLUX.2 Klein Base 4B FP8 + RefControl Pose",
        "stage": "inputs_prepared_no_inference",
        "canonical_master": str(Path(args.master)),
        "canonical_master_sha256": args.master_sha256,
        "reference_policy": "byte-for-byte copy only; no resize, crop, repaint, palette change, or regeneration",
        "canvas": [args.width, args.height],
        "seed_reserved_for_generation": args.seed,
        "pose_format": "OpenPose-style COCO-18 PNG on black background",
        "poses": produced,
        "network_access": False,
        "model_loaded": False,
        "inference_performed": False,
        "retry_policy_for_future_generation": "one render per pose; no artistic retry",
    }
    Path(args.manifest).write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    # Final structural validation.
    if len(produced) != 4:
        raise RuntimeError(f"Expected 4 poses, produced {len(produced)}")
    for item in produced:
        img = Image.open(item["png"])
        if img.size != (args.width, args.height):
            raise RuntimeError(f"Wrong image size for {item['pose_name']}: {img.size}")
        if img.mode != "RGB":
            raise RuntimeError(f"Wrong image mode for {item['pose_name']}: {img.mode}")

    print(f"generated_poses={len(produced)}")
    print(f"canvas={args.width}x{args.height}")
    print(f"seed_reserved={args.seed}")
    for item in produced:
        print(f"{item['pose_name']} sha256={item['png_sha256']}")


if __name__ == "__main__":
    main()
'@

[System.IO.File]::WriteAllText($GeneratorPath, $generator, [System.Text.UTF8Encoding]::new($false))
try {
    Write-Host ''
    Write-Host '[GENERATE] Creating four deterministic COCO-18 pose images...' -ForegroundColor Cyan
    & $EmbeddedPython $GeneratorPath `
        --pose-dir $PoseInputDir `
        --spec-dir $PoseSpecDir `
        --manifest $ManifestPath `
        --master $Master `
        --master-sha256 $SourceHash `
        --width $CanvasWidth `
        --height $CanvasHeight `
        --seed $Seed
    if ($LASTEXITCODE -ne 0) {
        throw "Skeleton generator failed with exit code $LASTEXITCODE"
    }
}
finally {
    Remove-Item $GeneratorPath -Force -ErrorAction SilentlyContinue
}

$ExpectedPoses = @(
    'pose_00_contact_L',
    'pose_01_passing_L',
    'pose_02_contact_R',
    'pose_03_passing_R'
)

foreach ($name in $ExpectedPoses) {
    $png = Join-Path $PoseInputDir ($name + '.png')
    $json = Join-Path $PoseSpecDir ($name + '.json')
    if (-not (Test-Path $png -PathType Leaf)) { throw "Missing pose PNG: $png" }
    if (-not (Test-Path $json -PathType Leaf)) { throw "Missing pose JSON: $json" }
}
if (-not (Test-Path $ManifestPath -PathType Leaf)) { throw "Missing manifest: $ManifestPath" }

Write-Host ''
Write-Host 'STEP 4: PASS' -ForegroundColor Green
Write-Host 'Prepared inputs:'
Write-Host "  reference: $CopiedMaster"
foreach ($name in $ExpectedPoses) {
    Write-Host "  pose:      $(Join-Path $PoseInputDir ($name + '.png'))"
}
Write-Host "  specs:     $PoseSpecDir"
Write-Host "  manifest:  $ManifestPath"
Write-Host ''
Write-Host 'No model was loaded and no inference was performed.' -ForegroundColor Green
