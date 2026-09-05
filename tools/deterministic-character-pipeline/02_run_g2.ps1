param(
    [string]$RepoRoot = 'D:\GOOGLE DRIVE\DEV\Roguelite',
    [string]$Workspace = 'Z:\AI\RogueliteCharacterPipeline'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Fail([string]$Message) {
    Write-Host "G2: FAIL - $Message" -ForegroundColor Red
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
Write-Host 'Roguelite deterministic character pipeline - G2 REAL MOTION / TOPOLOGY' -ForegroundColor Cyan
Write-Host 'This gate imports a real captured NormalWalk BVH, bakes it onto a persistent diagnostic rig, checks required bones/sockets/contacts and renders 12 sequence samples.'
Write-Host 'No Exilada art and no final pixel renderer are used here.'
Write-Host ''

if (-not (Test-Path $RepoRoot -PathType Container)) { Fail "Repository root not found: $RepoRoot" }

$g0Result = Join-Path $Workspace 'g0\g0_result.json'
if (-not (Test-Path $g0Result -PathType Leaf)) { Fail "G0 result missing: $g0Result" }
$g0 = Get-Content $g0Result -Raw | ConvertFrom-Json
if ($g0.gate -ne 'G0' -or $g0.status -ne 'PASS') { Fail 'G0 is not recorded PASS.' }

$baselinePath = Join-Path $RepoRoot 'tools\deterministic-character-pipeline\g1_baseline.json'
if (-not (Test-Path $baselinePath -PathType Leaf)) { Fail "G1 baseline missing: $baselinePath. Run git pull --ff-only first." }
$baseline = Get-Content $baselinePath -Raw | ConvertFrom-Json
if ($baseline.gate -ne 'G1' -or $baseline.status -ne 'PASS') { Fail 'Canonical G1 baseline is not PASS.' }
if ([int]$baseline.native_raster[0] -ne 640 -or [int]$baseline.native_raster[1] -ne 360) { Fail 'Unexpected G1 native raster.' }

$script = Join-Path $RepoRoot 'tools\deterministic-character-pipeline\g2_motion_topology.py'
if (-not (Test-Path $script -PathType Leaf)) { Fail "G2 Python script missing: $script. Run git pull --ff-only first." }

$blender = Find-BlenderExe
if (-not $blender) { Fail 'Blender could not be located.' }
Write-Host "[OK] Blender: $blender" -ForegroundColor Green

$motionDir = Join-Path $Workspace 'motion_sources\cmu'
New-Item -ItemType Directory -Force -Path $motionDir | Out-Null
$bvh = Join-Path $motionDir '105_34_NormalWalk.bvh'
$sourceCommit = '09a07f54f3bbb58797325f009282d0b2048a2871'
$sourceUrl = "https://raw.githubusercontent.com/una-dinosauria/cmu-mocap/$sourceCommit/data/105/105_34.bvh"

if (-not (Test-Path $bvh -PathType Leaf)) {
    Write-Host '[DOWNLOAD] CMU 105_34 NormalWalk BVH (pinned Git commit)...' -ForegroundColor Cyan
    try {
        Invoke-WebRequest -Uri $sourceUrl -OutFile $bvh -UseBasicParsing
    }
    catch {
        Fail "Could not download pinned BVH source: $($_.Exception.Message)"
    }
}

if (-not (Test-Path $bvh -PathType Leaf)) { Fail "BVH missing after download: $bvh" }
$size = (Get-Item $bvh).Length
if ($size -lt 500000) { Fail "BVH is unexpectedly small ($size bytes)." }
$framesLine = Select-String -Path $bvh -Pattern '^Frames:\s+2209\s*$' -SimpleMatch:$false | Select-Object -First 1
$frameTimeLine = Select-String -Path $bvh -Pattern '^Frame Time:\s+\.0083333\s*$' -SimpleMatch:$false | Select-Object -First 1
if (-not $framesLine -or -not $frameTimeLine) { Fail 'BVH structure does not match pinned 105_34 expectations (2209 frames at 120 fps).' }
$bvhHash = (Get-FileHash -Algorithm SHA256 $bvh).Hash.ToLowerInvariant()
Write-Host "[OK] Motion source: CMU 105_34 NormalWalk | $([math]::Round($size/1MB,2)) MB | SHA256 $bvhHash" -ForegroundColor Green

$g2Dir = Join-Path $Workspace 'g2'
$logDir = Join-Path $g2Dir 'logs'
New-Item -ItemType Directory -Force -Path $g2Dir, $logDir | Out-Null
Get-ChildItem $g2Dir -Filter 'g2_frame_*.png' -ErrorAction SilentlyContinue | Remove-Item -Force
@('g2_manifest.json','g2_result.json','g2_motion_topology.blend','g2_contact_sheet.png') | ForEach-Object {
    $p = Join-Path $g2Dir $_
    if (Test-Path $p) { Remove-Item $p -Force }
}
$stdout = Join-Path $logDir 'blender_stdout.log'
$stderr = Join-Path $logDir 'blender_stderr.log'
Remove-Item $stdout, $stderr -Force -ErrorAction SilentlyContinue

$pitch = [int]$baseline.camera_pitch_deg
$heroPx = [int]$baseline.protagonist_reference_height_px
Write-Host "[RUN] Blender headless | baseline 640x360 / pitch ${pitch}deg / hero ${heroPx}px..." -ForegroundColor Cyan

$argumentString = '--background --factory-startup --python-exit-code 1 --python "{0}" -- --bvh "{1}" --output-dir "{2}" --pitch {3} --hero-px {4}' -f $script, $bvh, $g2Dir, $pitch, $heroPx
$proc = Start-Process -FilePath $blender -ArgumentList $argumentString -Wait -PassThru -NoNewWindow -RedirectStandardOutput $stdout -RedirectStandardError $stderr

Get-Content $stdout -ErrorAction SilentlyContinue | Out-Host
if (Test-Path $stderr) {
    $errText = Get-Content $stderr -Raw -ErrorAction SilentlyContinue
    if ($errText) { Write-Host $errText -ForegroundColor DarkYellow }
}
if ($proc.ExitCode -ne 0) { Fail "Blender exited with code $($proc.ExitCode). See $stdout and $stderr" }

$manifestPath = Join-Path $g2Dir 'g2_manifest.json'
if (-not (Test-Path $manifestPath -PathType Leaf)) { Fail 'G2 manifest was not created.' }
$manifest = Get-Content $manifestPath -Raw | ConvertFrom-Json
if ($manifest.gate -ne 'G2' -or $manifest.status -ne 'REVIEW_REQUIRED') { Fail 'Unexpected G2 manifest status.' }
if ($manifest.canonical_rig.missing_required_bones.Count -ne 0) { Fail 'G2 canonical rig reports missing required bones.' }
if ($manifest.samples.Count -ne 12) { Fail "Expected 12 rendered sequence samples, got $($manifest.samples.Count)." }
if ([double]$manifest.selected_clip.straightness -lt 0.85) { Fail "Automatically selected locomotion window is too curved: straightness=$($manifest.selected_clip.straightness)" }

foreach ($sample in $manifest.samples) {
    if (-not (Test-Path $sample.file -PathType Leaf)) { Fail "Sample frame missing: $($sample.file)" }
    $actual = (Get-FileHash -Algorithm SHA256 $sample.file).Hash.ToLowerInvariant()
    if ($actual -ne $sample.sha256.ToString().ToLowerInvariant()) { Fail "Hash mismatch: $($sample.file)" }
}

# Build 4x3 contact sheet for sequence-level review.
Add-Type -AssemblyName System.Drawing
$cellW = 640
$cellH = 360
$cols = 4
$rows = 3
$sheet = New-Object System.Drawing.Bitmap ($cellW * $cols), ($cellH * $rows)
$graphics = [System.Drawing.Graphics]::FromImage($sheet)
$graphics.Clear([System.Drawing.Color]::Black)
$font = New-Object System.Drawing.Font('Arial', 14, [System.Drawing.FontStyle]::Bold)
$labelBrush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::White)
$bgBrush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(190,0,0,0))

try {
    for ($i = 0; $i -lt $manifest.samples.Count; $i++) {
        $sample = $manifest.samples[$i]
        $row = [math]::Floor($i / $cols)
        $col = $i % $cols
        $x = $col * $cellW
        $y = $row * $cellH
        $img = [System.Drawing.Image]::FromFile($sample.file)
        try {
            $graphics.DrawImage($img, $x, $y, $cellW, $cellH)
            $graphics.FillRectangle($bgBrush, $x + 8, $y + 8, 250, 28)
            $label = ('frame {0} | t+{1:0.00}s' -f [int]$sample.frame, [double]$sample.time_sec_from_clip_start)
            $graphics.DrawString($label, $font, $labelBrush, $x + 14, $y + 11)
        }
        finally { $img.Dispose() }
    }
    $sheetPath = Join-Path $g2Dir 'g2_contact_sheet.png'
    $sheet.Save($sheetPath, [System.Drawing.Imaging.ImageFormat]::Png)
}
finally {
    $graphics.Dispose(); $sheet.Dispose(); $font.Dispose(); $labelBrush.Dispose(); $bgBrush.Dispose()
}

if (-not (Test-Path $sheetPath -PathType Leaf)) { Fail 'G2 contact sheet was not created.' }
$sheetHash = (Get-FileHash -Algorithm SHA256 $sheetPath).Hash.ToLowerInvariant()

$provenance = [ordered]@{
    dataset = 'CMU Graphics Lab Motion Capture Database'
    conversion = 'MotionBuilder-friendly BVH conversion by Bruce Hahne'
    trial = '105_34 NormalWalk'
    source_commit = $sourceCommit
    source_url = $sourceUrl
    local_file = $bvh
    sha256 = $bvhHash
    usage = 'CMU states original data is free for research and commercial projects; Bruce Hahne states no additional restrictions on this BVH conversion.'
}
$provenancePath = Join-Path $g2Dir 'g2_source_provenance.json'
$provenance | ConvertTo-Json -Depth 6 | Set-Content -Path $provenancePath -Encoding UTF8

$result = [ordered]@{
    gate = 'G2'
    status = 'REVIEW_REQUIRED'
    timestamp = (Get-Date).ToString('o')
    baseline = $baseline
    motion_source = $provenance
    selected_clip = $manifest.selected_clip
    canonical_rig = $manifest.canonical_rig
    contacts = $manifest.contacts
    contact_sheet = $sheetPath
    contact_sheet_sha256 = $sheetHash
    manifest = $manifestPath
    blend = $manifest.blend
    stdout_log = $stdout
    stderr_log = $stderr
}
$resultPath = Join-Path $g2Dir 'g2_result.json'
$result | ConvertTo-Json -Depth 12 | Set-Content -Path $resultPath -Encoding UTF8

Write-Host ''
Write-Host 'G2: REVIEW REQUIRED' -ForegroundColor Yellow
Write-Host "CONTACT SHEET: $sheetPath"
Write-Host "RESULT:        $resultPath"
Write-Host "SOURCE SHA256: $bvhHash"
Write-Host "SHEET SHA256:  $sheetHash"
Write-Host ''
Write-Host 'STOP. Do not start G3. Share g2_contact_sheet.png; share console output only if this runner fails.' -ForegroundColor Yellow
