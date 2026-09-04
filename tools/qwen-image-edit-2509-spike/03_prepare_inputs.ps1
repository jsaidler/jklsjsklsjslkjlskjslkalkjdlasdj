param(
    [string]$Workspace = 'Z:\AI\QwenImageEditSpike',
    [string]$Master = 'D:\GOOGLE DRIVE\DEV\Roguelite\assets\source\characters\exilada\reference\exilada_master.png',
    [int]$Width = 768,
    [int]$Height = 1024,
    [long]$Seed = 20260904
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$PortableRoot = Join-Path $Workspace 'ComfyUI_windows_portable'
$ComfyRoot = Join-Path $PortableRoot 'ComfyUI'
$EmbeddedPython = Join-Path $PortableRoot 'python_embeded\python.exe'
$InputDir = Join-Path $ComfyRoot 'input'
$MasterDest = Join-Path $InputDir 'exilada_master.png'
$PoseDest = Join-Path $InputDir 'qwen_hard_passing_L_keypoints.png'
$SpecPath = Join-Path $Workspace 'qwen_hard_passing_L_spec.json'
$GeneratorPath = Join-Path $Workspace '_make_qwen_hard_pose.py'

$Prompt = @'
Use image 1 as the exact Exilada character identity/reference and image 2 as the keypoint pose map. Repose the woman from image 1 to match the full-body walking passing pose in image 2. Keep exactly one normal adult human body: one head, one torso, two arms, two hands, two legs, and two feet. Do not add, duplicate, fuse, or omit limbs. Preserve the same face, lean adult body proportions, very long heavy black hair, torn beige cloth, scars, wrist shackles, ankle shackles, and barefoot state. Keep the complete body visible from head to both feet. Maintain a three-quarter side view facing screen-right. The lifted leg must be clearly a single swing leg and the planted leg must be clearly a single support leg.
'@

Write-Host ''
Write-Host 'Qwen-Image-Edit-2509 keypoint spike - STEP 4: PREPARE ONE HARD POSE INPUT' -ForegroundColor Cyan
Write-Host 'No model load. No inference.' -ForegroundColor Yellow
Write-Host ''

if (-not (Test-Path $EmbeddedPython -PathType Leaf)) { throw "Embedded Python missing: $EmbeddedPython" }
if (-not (Test-Path $Master -PathType Leaf)) { throw "Canonical master missing: $Master" }
if ($Width -ne 768 -or $Height -ne 1024) { throw "Topology gate is fixed at 768x1024; got ${Width}x${Height}." }
if ($Seed -ne 20260904) { throw "Topology gate seed must remain 20260904; got $Seed." }

New-Item -ItemType Directory -Force -Path $InputDir | Out-Null
Copy-Item -LiteralPath $Master -Destination $MasterDest -Force
$MasterHash = (Get-FileHash -LiteralPath $Master -Algorithm SHA256).Hash.ToLowerInvariant()
$MasterCopyHash = (Get-FileHash -LiteralPath $MasterDest -Algorithm SHA256).Hash.ToLowerInvariant()
if ($MasterHash -ne $MasterCopyHash) { throw 'Copied master hash mismatch.' }

$py = @'
import argparse, hashlib, json
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

# Same difficult structural case as V3 passing_L: one planted support leg and one lifted swing leg.
# This was the FLUX/RefControl case that produced an extra third leg, making it a deliberate topology stress test.
PTS = [
    (0.530, 0.100), (0.515, 0.180),
    (0.460, 0.200), (0.445, 0.300), (0.495, 0.390),
    (0.565, 0.200), (0.600, 0.305), (0.645, 0.395),
    (0.475, 0.450), (0.490, 0.650), (0.475, 0.880),
    (0.540, 0.445), (0.620, 0.600), (0.585, 0.745),
    (0.510, 0.090), (0.550, 0.090), (0.490, 0.100), (0.570, 0.100),
]

def sha(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for b in iter(lambda:f.read(1024*1024), b''):
            h.update(b)
    return h.hexdigest()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    ap.add_argument('--spec', required=True)
    ap.add_argument('--width', type=int, required=True)
    ap.add_argument('--height', type=int, required=True)
    ap.add_argument('--master-sha256', required=True)
    ap.add_argument('--seed', type=int, required=True)
    ap.add_argument('--prompt-file', required=True)
    args=ap.parse_args()

    points=[(round(x*args.width), round(y*args.height)) for x,y in PTS]
    im=Image.new('RGB',(args.width,args.height),(0,0,0))
    d=ImageDraw.Draw(im)
    lw=max(5,round(min(args.width,args.height)*0.012))
    r=max(4,round(min(args.width,args.height)*0.010))
    for a,b in LIMBS:
        d.line([points[a],points[b]], fill=COLORS[a], width=lw)
    for i,(x,y) in enumerate(points):
        c=COLORS[i]
        d.ellipse((x-r,y-r,x+r,y+r), fill=c)
    out=Path(args.out)
    out.parent.mkdir(parents=True,exist_ok=True)
    im.save(out,'PNG',optimize=False)
    prompt=Path(args.prompt_file).read_text(encoding='utf-8')
    spec={
        'spike':'Qwen-Image-Edit-2509 native keypoint topology gate',
        'pose_name':'hard_passing_L',
        'pose_source':'same structural V3 passing_L case that triggered extra-leg failure in RefControl',
        'format':'OpenPose-style COCO-18 keypoint map',
        'canvas':[args.width,args.height],
        'seed':args.seed,
        'master_sha256':args.master_sha256,
        'pose_png':str(out),
        'pose_png_sha256':sha(out),
        'prompt':prompt.strip(),
        'qa_order':[
            'topology count: 1 head/torso, 2 arms/hands, 2 legs/feet',
            'pose adherence',
            'identity continuity',
            'prop continuity',
            'visual quality'
        ],
        'pass_rule':'Any extra/missing/fused major limb is immediate FAIL; no retry or prompt iteration.'
    }
    Path(args.spec).write_text(json.dumps(spec,indent=2),encoding='utf-8')
    print('pose_sha256='+spec['pose_png_sha256'])

if __name__=='__main__': main()
'@

[System.IO.File]::WriteAllText($GeneratorPath, $py, [System.Text.UTF8Encoding]::new($false))
$PromptPath = Join-Path $Workspace '_qwen_prompt.txt'
[System.IO.File]::WriteAllText($PromptPath, $Prompt.Trim(), [System.Text.UTF8Encoding]::new($false))
try {
    & $EmbeddedPython $GeneratorPath --out $PoseDest --spec $SpecPath --width $Width --height $Height --master-sha256 $MasterHash --seed $Seed --prompt-file $PromptPath
    if ($LASTEXITCODE -ne 0) { throw 'Hard-pose generator failed.' }
} finally {
    Remove-Item $GeneratorPath,$PromptPath -Force -ErrorAction SilentlyContinue
}

if (-not (Test-Path $PoseDest -PathType Leaf)) { throw "Missing generated keypoint map: $PoseDest" }
if (-not (Test-Path $SpecPath -PathType Leaf)) { throw "Missing input spec: $SpecPath" }

Write-Host ''
Write-Host 'STEP 4: PASS' -ForegroundColor Green
Write-Host "Identity input: $MasterDest"
Write-Host "Keypoint input: $PoseDest"
Write-Host "Spec/prompt:    $SpecPath"
Write-Host 'No model was loaded and no inference was performed.' -ForegroundColor Green
