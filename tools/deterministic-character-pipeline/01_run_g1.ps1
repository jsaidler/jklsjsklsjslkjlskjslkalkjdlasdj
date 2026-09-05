param(
    [string]$RepoRoot = 'D:\GOOGLE DRIVE\DEV\Roguelite',
    [string]$Workspace = 'Z:\AI\RogueliteCharacterPipeline'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Fail([string]$Message) {
    Write-Host "G1: FAIL - $Message" -ForegroundColor Red
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
Write-Host 'Roguelite deterministic character pipeline - G1 CAMERA / NATIVE SCALE' -ForegroundColor Cyan
Write-Host 'This gate renders a 3x3 comparison matrix at native 640x360.'
Write-Host 'Rows vary camera pitch (18/26/34 deg); columns vary protagonist height (112/128/144 px).'
Write-Host 'No Exilada model, mocap or final pixel renderer is used yet.'
Write-Host ''

$g0Result = Join-Path $Workspace 'g0\g0_result.json'
if (-not (Test-Path $g0Result -PathType Leaf)) { Fail "G0 result missing: $g0Result" }
$g0 = Get-Content $g0Result -Raw | ConvertFrom-Json
if ($g0.gate -ne 'G0' -or $g0.status -ne 'PASS') { Fail 'G0 is not recorded as PASS.' }

$script = Join-Path $RepoRoot 'tools\deterministic-character-pipeline\g1_camera_scale_blockout.py'
if (-not (Test-Path $script -PathType Leaf)) { Fail "G1 Python script missing: $script. Run git pull --ff-only first." }
$blender = Find-BlenderExe
if (-not $blender) { Fail 'Blender could not be located. G0 previously passed, so installation should exist.' }
Write-Host "[OK] Blender: $blender" -ForegroundColor Green

$g1Dir = Join-Path $Workspace 'g1'
$logDir = Join-Path $g1Dir 'logs'
New-Item -ItemType Directory -Force -Path $g1Dir, $logDir | Out-Null
Get-ChildItem $g1Dir -Filter 'g1_*.png' -ErrorAction SilentlyContinue | Remove-Item -Force
@('g1_manifest.json','g1_result.json','g1_blockout.blend','g1_contact_sheet.png') | ForEach-Object {
    $p = Join-Path $g1Dir $_
    if (Test-Path $p) { Remove-Item $p -Force }
}
$stdout = Join-Path $logDir 'blender_stdout.log'
$stderr = Join-Path $logDir 'blender_stderr.log'
Remove-Item $stdout, $stderr -Force -ErrorAction SilentlyContinue

Write-Host '[RUN] Rendering nine diagnostic composition candidates...' -ForegroundColor Cyan
$argumentString = '--background --factory-startup --python-exit-code 1 --python "{0}" -- --output-dir "{1}"' -f $script, $g1Dir
$proc = Start-Process -FilePath $blender -ArgumentList $argumentString -Wait -PassThru -NoNewWindow -RedirectStandardOutput $stdout -RedirectStandardError $stderr
Get-Content $stdout -ErrorAction SilentlyContinue | Out-Host
if (Test-Path $stderr) {
    $errText = Get-Content $stderr -Raw -ErrorAction SilentlyContinue
    if ($errText) { Write-Host $errText -ForegroundColor DarkYellow }
}
if ($proc.ExitCode -ne 0) { Fail "Blender exited with code $($proc.ExitCode). See $stdout and $stderr" }

$manifestPath = Join-Path $g1Dir 'g1_manifest.json'
if (-not (Test-Path $manifestPath -PathType Leaf)) { Fail 'G1 manifest was not created.' }
$manifest = Get-Content $manifestPath -Raw | ConvertFrom-Json
if ($manifest.gate -ne 'G1' -or $manifest.status -ne 'REVIEW_REQUIRED') { Fail 'Unexpected G1 manifest status.' }
if ([int]$manifest.candidate_count -ne 9) { Fail "Expected 9 candidates, got $($manifest.candidate_count)." }

foreach ($candidate in $manifest.candidates) {
    if (-not (Test-Path $candidate.file -PathType Leaf)) { Fail "Candidate missing: $($candidate.file)" }
    $actual = (Get-FileHash -Algorithm SHA256 $candidate.file).Hash.ToLowerInvariant()
    if ($actual -ne $candidate.sha256.ToString().ToLowerInvariant()) { Fail "Hash mismatch: $($candidate.file)" }
    if ([math]::Abs([double]$candidate.measured_height_px - [double]$candidate.target_height_px) -gt 1.5) {
        Fail "Height calibration outside tolerance for $($candidate.file): target=$($candidate.target_height_px) measured=$($candidate.measured_height_px)"
    }
}

# Build a single review sheet so the user does not need to open nine files manually.
Add-Type -AssemblyName System.Drawing
$cellW = 640
$cellH = 360
$sheet = New-Object System.Drawing.Bitmap ($cellW * 3), ($cellH * 3)
$graphics = [System.Drawing.Graphics]::FromImage($sheet)
$graphics.Clear([System.Drawing.Color]::Black)
$font = New-Object System.Drawing.Font('Arial', 16, [System.Drawing.FontStyle]::Bold)
$labelBrush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::White)
$bgBrush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(190,0,0,0))

try {
    $pitches = @(18,26,34)
    $heights = @(112,128,144)
    for ($row = 0; $row -lt 3; $row++) {
        for ($col = 0; $col -lt 3; $col++) {
            $pitch = $pitches[$row]
            $height = $heights[$col]
            $candidate = $manifest.candidates | Where-Object { [int]$_.pitch_deg -eq $pitch -and [int]$_.target_height_px -eq $height } | Select-Object -First 1
            if (-not $candidate) { Fail "Candidate not found for pitch=$pitch height=$height" }
            $img = [System.Drawing.Image]::FromFile($candidate.file)
            try {
                $x = $col * $cellW
                $y = $row * $cellH
                $graphics.DrawImage($img, $x, $y, $cellW, $cellH)
                $graphics.FillRectangle($bgBrush, $x + 8, $y + 8, 260, 32)
                $graphics.DrawString(("pitch {0}deg | hero {1}px" -f $pitch,$height), $font, $labelBrush, $x + 14, $y + 12)
            }
            finally { $img.Dispose() }
        }
    }

    $sheetPath = Join-Path $g1Dir 'g1_contact_sheet.png'
    $sheet.Save($sheetPath, [System.Drawing.Imaging.ImageFormat]::Png)
}
finally {
    $graphics.Dispose(); $sheet.Dispose(); $font.Dispose(); $labelBrush.Dispose(); $bgBrush.Dispose()
}

if (-not (Test-Path $sheetPath -PathType Leaf)) { Fail 'Contact sheet was not created.' }
$sheetHash = (Get-FileHash -Algorithm SHA256 $sheetPath).Hash.ToLowerInvariant()

$result = [ordered]@{
    gate = 'G1'
    status = 'REVIEW_REQUIRED'
    timestamp = (Get-Date).ToString('o')
    g0_png_sha256 = $g0.png_sha256
    blender_version = $manifest.blender_version
    native_raster = $manifest.native_raster
    pitches_deg = $manifest.pitches_deg
    target_protagonist_heights_px = $manifest.target_protagonist_heights_px
    candidate_count = $manifest.candidate_count
    contact_sheet = $sheetPath
    contact_sheet_sha256 = $sheetHash
    manifest = $manifestPath
    blend = $manifest.blend
    stdout_log = $stdout
    stderr_log = $stderr
}
$resultPath = Join-Path $g1Dir 'g1_result.json'
$result | ConvertTo-Json -Depth 8 | Set-Content -Path $resultPath -Encoding UTF8

Write-Host ''
Write-Host 'G1: REVIEW REQUIRED' -ForegroundColor Yellow
Write-Host "CONTACT SHEET: $sheetPath"
Write-Host "RESULT:        $resultPath"
Write-Host "SHA256:        $sheetHash"
Write-Host ''
Write-Host 'STOP. Do not start G2. Share g1_contact_sheet.png for camera/scale review.' -ForegroundColor Yellow
