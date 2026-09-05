param(
    [string]$RepoRoot = 'D:\GOOGLE DRIVE\DEV\Roguelite',
    [string]$Workspace = 'Z:\AI\RogueliteCharacterPipeline'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Fail([string]$Message) {
    Write-Host "G3: FAIL - $Message" -ForegroundColor Red
    exit 1
}

function Find-BlenderExe {
    $candidates = @()
    if ($env:BLENDER_EXE) { $candidates += $env:BLENDER_EXE }
    $cmd = Get-Command blender.exe -ErrorAction SilentlyContinue
    if ($cmd) { $candidates += $cmd.Source }
    foreach ($root in @('C:\Program Files\Blender Foundation','C:\Program Files (x86)\Blender Foundation')) {
        if (Test-Path $root) {
            $candidates += Get-ChildItem -Path $root -Filter blender.exe -Recurse -ErrorAction SilentlyContinue | Select-Object -ExpandProperty FullName
        }
    }
    $found = @($candidates | Where-Object { $_ -and (Test-Path $_ -PathType Leaf) } | Select-Object -Unique)
    if ($found.Count -eq 0) { return $null }
    return ($found | Sort-Object -Descending | Select-Object -First 1)
}

Write-Host ''
Write-Host 'Roguelite deterministic character pipeline - G3 PIXEL TRANSLATION' -ForegroundColor Cyan
Write-Host 'This gate is the early visual kill switch: can deterministic 3D motion/topology become intentional native-grid pixel art?' 
Write-Host 'It uses a generic stylized semantic proxy. It does NOT build the Exilada production model.'
Write-Host ''

if (-not (Test-Path $RepoRoot -PathType Container)) { Fail "Repository root not found: $RepoRoot" }

$approvalPath = Join-Path $RepoRoot 'tools\deterministic-character-pipeline\g2_approval.json'
if (-not (Test-Path $approvalPath -PathType Leaf)) { Fail "G2 approval missing: $approvalPath. Run git pull --ff-only first." }
$approval = Get-Content $approvalPath -Raw | ConvertFrom-Json
if ($approval.gate -ne 'G2' -or $approval.status -ne 'PASS') { Fail 'Canonical G2 approval is not PASS.' }

$g2Dir = Join-Path $Workspace 'g2'
$g2Blend = Join-Path $g2Dir 'g2_motion_topology.blend'
$g2Manifest = Join-Path $g2Dir 'g2_manifest.json'
foreach ($required in @($g2Blend,$g2Manifest)) {
    if (-not (Test-Path $required -PathType Leaf)) { Fail "Required G2 artifact missing: $required" }
}

$baselinePath = Join-Path $RepoRoot 'tools\deterministic-character-pipeline\g1_baseline.json'
if (-not (Test-Path $baselinePath -PathType Leaf)) { Fail "G1 baseline missing: $baselinePath" }
$baseline = Get-Content $baselinePath -Raw | ConvertFrom-Json
if ($baseline.gate -ne 'G1' -or $baseline.status -ne 'PASS') { Fail 'Canonical G1 baseline is not PASS.' }

$script = Join-Path $RepoRoot 'tools\deterministic-character-pipeline\g3_pixel_translation.py'
if (-not (Test-Path $script -PathType Leaf)) { Fail "G3 Python script missing: $script. Run git pull --ff-only first." }

$blender = Find-BlenderExe
if (-not $blender) { Fail 'Blender could not be located.' }
Write-Host "[OK] Blender: $blender" -ForegroundColor Green

$g3Dir = Join-Path $Workspace 'g3'
$logDir = Join-Path $g3Dir 'logs'
New-Item -ItemType Directory -Force -Path $g3Dir, $logDir | Out-Null
Get-ChildItem $g3Dir -Filter 'g3_*.png' -ErrorAction SilentlyContinue | Remove-Item -Force
@('g3_manifest.json','g3_result.json','g3_pixel_translation.blend','g3_contact_sheet.png') | ForEach-Object {
    $p = Join-Path $g3Dir $_
    if (Test-Path $p) { Remove-Item $p -Force }
}
$stdout = Join-Path $logDir 'blender_stdout.log'
$stderr = Join-Path $logDir 'blender_stderr.log'
Remove-Item $stdout, $stderr -Force -ErrorAction SilentlyContinue

$pitch = [int]$baseline.camera_pitch_deg
$heroPx = [int]$baseline.protagonist_reference_height_px
Write-Host "[RUN] Blender headless | G3 generic proxy | 640x360 / pitch ${pitch}deg / hero ${heroPx}px..." -ForegroundColor Cyan

$argumentString = '--background --factory-startup --python-exit-code 1 --python "{0}" -- --g2-blend "{1}" --g2-manifest "{2}" --output-dir "{3}" --pitch {4} --hero-px {5}' -f $script, $g2Blend, $g2Manifest, $g3Dir, $pitch, $heroPx
$proc = Start-Process -FilePath $blender -ArgumentList $argumentString -Wait -PassThru -NoNewWindow -RedirectStandardOutput $stdout -RedirectStandardError $stderr

Get-Content $stdout -ErrorAction SilentlyContinue | Out-Host
if (Test-Path $stderr) {
    $errText = Get-Content $stderr -Raw -ErrorAction SilentlyContinue
    if ($errText) { Write-Host $errText -ForegroundColor DarkYellow }
}
if ($proc.ExitCode -ne 0) { Fail "Blender exited with code $($proc.ExitCode). See $stdout and $stderr" }

$manifestPath = Join-Path $g3Dir 'g3_manifest.json'
if (-not (Test-Path $manifestPath -PathType Leaf)) { Fail 'G3 manifest was not created.' }
$manifest = Get-Content $manifestPath -Raw | ConvertFrom-Json
if ($manifest.gate -ne 'G3' -or $manifest.status -ne 'REVIEW_REQUIRED') { Fail 'Unexpected G3 manifest status.' }
if ($manifest.methods.Count -ne 3) { Fail "Expected 3 G3 methods, got $($manifest.methods.Count)." }
if ($manifest.outputs.Count -ne 12) { Fail "Expected 12 G3 renders, got $($manifest.outputs.Count)." }

foreach ($output in $manifest.outputs) {
    if (-not (Test-Path $output.file -PathType Leaf)) { Fail "G3 output missing: $($output.file)" }
    $actual = (Get-FileHash -Algorithm SHA256 $output.file).Hash.ToLowerInvariant()
    if ($actual -ne $output.sha256.ToString().ToLowerInvariant()) { Fail "G3 hash mismatch: $($output.file)" }
}

# 4 columns (motion frames) x 3 rows (translation methods).
# Low-resolution method C is displayed with nearest-neighbor scaling, never bilinear filtering.
Add-Type -AssemblyName System.Drawing
$cellW = 640
$cellH = 360
$cols = 4
$rows = 3
$sheet = New-Object System.Drawing.Bitmap ($cellW * $cols), ($cellH * $rows)
$graphics = [System.Drawing.Graphics]::FromImage($sheet)
$graphics.Clear([System.Drawing.Color]::Black)
$graphics.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::NearestNeighbor
$graphics.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::Half
$font = New-Object System.Drawing.Font('Arial', 13, [System.Drawing.FontStyle]::Bold)
$labelBrush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::White)
$bgBrush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(205,0,0,0))

try {
    for ($row = 0; $row -lt $manifest.methods.Count; $row++) {
        $method = $manifest.methods[$row]
        for ($col = 0; $col -lt $manifest.source_frames.Count; $col++) {
            $frame = [int]$manifest.source_frames[$col]
            $output = $manifest.outputs | Where-Object { $_.method -eq $method.id -and [int]$_.frame -eq $frame } | Select-Object -First 1
            if (-not $output) { Fail "Missing contact-sheet source for method=$($method.id), frame=$frame" }
            $img = [System.Drawing.Image]::FromFile($output.file)
            try {
                $x = $col * $cellW
                $y = $row * $cellH
                $dest = New-Object System.Drawing.Rectangle($x,$y,$cellW,$cellH)
                $graphics.DrawImage($img, $dest)
                $graphics.FillRectangle($bgBrush, $x + 8, $y + 8, 390, 29)
                $label = ('{0} | frame {1}' -f $method.label,$frame)
                $graphics.DrawString($label, $font, $labelBrush, $x + 14, $y + 11)
            }
            finally { $img.Dispose() }
        }
    }
    $sheetPath = Join-Path $g3Dir 'g3_contact_sheet.png'
    $sheet.Save($sheetPath, [System.Drawing.Imaging.ImageFormat]::Png)
}
finally {
    $graphics.Dispose(); $sheet.Dispose(); $font.Dispose(); $labelBrush.Dispose(); $bgBrush.Dispose()
}

if (-not (Test-Path $sheetPath -PathType Leaf)) { Fail 'G3 contact sheet was not created.' }
$sheetHash = (Get-FileHash -Algorithm SHA256 $sheetPath).Hash.ToLowerInvariant()

$result = [ordered]@{
    gate = 'G3'
    status = 'REVIEW_REQUIRED'
    timestamp = (Get-Date).ToString('o')
    source_gate = 'G2'
    g2_approval = $approvalPath
    baseline = $baseline
    methods = $manifest.methods
    source_frames = $manifest.source_frames
    semantic_materials = $manifest.semantic_materials
    contact_sheet = $sheetPath
    contact_sheet_sha256 = $sheetHash
    manifest = $manifestPath
    blend = $manifest.blend
    stdout_log = $stdout
    stderr_log = $stderr
}
$resultPath = Join-Path $g3Dir 'g3_result.json'
$result | ConvertTo-Json -Depth 10 | Set-Content -Path $resultPath -Encoding UTF8

Write-Host ''
Write-Host 'G3: REVIEW REQUIRED' -ForegroundColor Yellow
Write-Host "CONTACT SHEET: $sheetPath"
Write-Host "RESULT:        $resultPath"
Write-Host "SHA256:        $sheetHash"
Write-Host ''
Write-Host 'STOP. Do not build Exilada geometry and do not start G4. Share g3_contact_sheet.png for visual kill-switch review.' -ForegroundColor Yellow
