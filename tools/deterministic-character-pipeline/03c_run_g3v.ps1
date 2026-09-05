param(
    [string]$RepoRoot = 'D:\GOOGLE DRIVE\DEV\Roguelite',
    [string]$Workspace = 'Z:\AI\RogueliteCharacterPipeline'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Fail([string]$Message) {
    Write-Host "G3V: FAIL - $Message" -ForegroundColor Red
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

function Find-MpfbPackageRoot([string]$Root) {
    if (-not (Test-Path $Root -PathType Container)) { return $null }
    $candidates = Get-ChildItem -Path $Root -Filter '__init__.py' -File -Recurse -ErrorAction SilentlyContinue
    foreach ($init in $candidates) {
        $dir = $init.Directory.FullName
        if ((Test-Path (Join-Path $dir 'services') -PathType Container) -and
            (Test-Path (Join-Path $dir 'data') -PathType Container)) {
            return $dir
        }
    }
    return $null
}

Write-Host ''
Write-Host 'Roguelite deterministic character pipeline - G3V REPRESENTATIVE VISUAL PROXY' -ForegroundColor Cyan
Write-Host 'One Blender background process only. MPFB is loaded directly from the pinned verified archive; Blender extension repository/preferences are not used.'
Write-Host ''

if (-not (Test-Path $RepoRoot -PathType Container)) { Fail "Repository root not found: $RepoRoot" }
$failureMarker = Join-Path $RepoRoot 'tools\deterministic-character-pipeline\g3r_failure.json'
if (-not (Test-Path $failureMarker -PathType Leaf)) { Fail "G3R failure marker missing: $failureMarker. Run git pull --ff-only first." }
$failure = Get-Content $failureMarker -Raw | ConvertFrom-Json
if ($failure.gate -ne 'G3R' -or $failure.status -ne 'FAIL') { Fail 'G3R is not canonically recorded FAIL.' }

$baselinePath = Join-Path $RepoRoot 'tools\deterministic-character-pipeline\g1_baseline.json'
$g2ApprovalPath = Join-Path $RepoRoot 'tools\deterministic-character-pipeline\g2_approval.json'
foreach ($p in @($baselinePath,$g2ApprovalPath)) {
    if (-not (Test-Path $p -PathType Leaf)) { Fail "Required upstream marker missing: $p" }
}
$baseline = Get-Content $baselinePath -Raw | ConvertFrom-Json
$g2Approval = Get-Content $g2ApprovalPath -Raw | ConvertFrom-Json
if ($baseline.status -ne 'PASS' -or $g2Approval.status -ne 'PASS') { Fail 'G1/G2 upstream gates are not PASS.' }

$g2Dir = Join-Path $Workspace 'g2'
$g2Blend = Join-Path $g2Dir 'g2_motion_topology.blend'
$g2Manifest = Join-Path $g2Dir 'g2_manifest.json'
foreach ($p in @($g2Blend,$g2Manifest)) {
    if (-not (Test-Path $p -PathType Leaf)) { Fail "Required local G2 artifact missing: $p" }
}

$targetScript = Join-Path $RepoRoot 'tools\deterministic-character-pipeline\g3v_representative_visual_proxy.py'
$bootstrapScript = Join-Path $RepoRoot 'tools\deterministic-character-pipeline\g3v_mpfb_bootstrap.py'
foreach ($p in @($targetScript,$bootstrapScript)) {
    if (-not (Test-Path $p -PathType Leaf)) { Fail "Required G3V script missing: $p" }
}

$script:BlenderExe = Find-BlenderExe
if (-not $script:BlenderExe) { Fail 'Blender could not be located.' }
Write-Host "[OK] Blender: $script:BlenderExe" -ForegroundColor Green

# Pin exact MPFB package and verify the archive before using it.
$deps = Join-Path $Workspace 'dependencies\g3v'
New-Item -ItemType Directory -Force -Path $deps | Out-Null
$mpfbVersion = '2.0.17'
$mpfbZip = Join-Path $deps "mpfb-$mpfbVersion.zip"
$apiUrls = @(
    'https://extensions.blender.org/api/v1/extensions/?blender_version=5.1.1&platform=windows-x64',
    'https://extensions.blender.org/api/v1/extensions/?blender_version=5.1.1'
)
$pkg = $null
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.SecurityProtocolType]::Tls12
foreach ($api in $apiUrls) {
    try {
        $meta = Invoke-RestMethod -Uri $api -UseBasicParsing
        $pkg = @($meta.data | Where-Object { $_.id -eq 'mpfb' -and $_.version -eq $mpfbVersion }) | Select-Object -First 1
        if ($pkg) { break }
    }
    catch {
        Write-Host "[WARN] MPFB metadata query failed at ${api}: $($_.Exception.Message)" -ForegroundColor DarkYellow
    }
}
if (-not $pkg) { Fail "Official Blender Extensions API did not return pinned MPFB $mpfbVersion for Blender 5.1.1." }

$archiveUrl = [string]$pkg.archive_url
if ($archiveUrl -notmatch '^https?://') { $archiveUrl = 'https://extensions.blender.org' + $archiveUrl }
$expectedHash = ([string]$pkg.archive_hash) -replace '^sha256:',''
if (-not $expectedHash) { Fail 'MPFB metadata did not include archive_hash.' }

$needDownload = $true
if (Test-Path $mpfbZip -PathType Leaf) {
    $existingHash = (Get-FileHash -Algorithm SHA256 $mpfbZip).Hash.ToLowerInvariant()
    if ($existingHash -eq $expectedHash.ToLowerInvariant()) { $needDownload = $false }
}
if ($needDownload) {
    Write-Host "[DOWNLOAD] MPFB $mpfbVersion from official Blender Extensions..." -ForegroundColor Cyan
    try { Invoke-WebRequest -Uri $archiveUrl -OutFile $mpfbZip -UseBasicParsing }
    catch { Fail "Could not download MPFB: $($_.Exception.Message)" }
}
$actualHash = (Get-FileHash -Algorithm SHA256 $mpfbZip).Hash.ToLowerInvariant()
if ($actualHash -ne $expectedHash.ToLowerInvariant()) {
    Fail "MPFB SHA256 mismatch. Expected $expectedHash, got $actualHash"
}
Write-Host "[OK] MPFB $mpfbVersion archive SHA256 $actualHash" -ForegroundColor Green

# Extract once and load MPFB directly as a Python package. This deliberately bypasses
# Blender extension repository state, add-on activation and GUI preferences.
$mpfbExtract = Join-Path $deps "mpfb-$mpfbVersion-unpacked"
$mpfbRoot = Find-MpfbPackageRoot $mpfbExtract
if (-not $mpfbRoot) {
    if (Test-Path $mpfbExtract) { Remove-Item $mpfbExtract -Recurse -Force }
    New-Item -ItemType Directory -Force -Path $mpfbExtract | Out-Null
    Write-Host '[SETUP] Extracting pinned MPFB archive locally...' -ForegroundColor Cyan
    try { Expand-Archive -Path $mpfbZip -DestinationPath $mpfbExtract -Force }
    catch { Fail "Could not extract MPFB archive: $($_.Exception.Message)" }
    $mpfbRoot = Find-MpfbPackageRoot $mpfbExtract
}
if (-not $mpfbRoot) { Fail "Could not locate MPFB package root after extraction: $mpfbExtract" }
$mpfbUserRoot = Join-Path $deps 'mpfb_user'
New-Item -ItemType Directory -Force -Path $mpfbUserRoot | Out-Null
Write-Host "[OK] MPFB direct package root: $mpfbRoot" -ForegroundColor Green

$g3vDir = Join-Path $Workspace 'g3v'
$logDir = Join-Path $g3vDir 'logs'
New-Item -ItemType Directory -Force -Path $g3vDir,$logDir | Out-Null
Get-ChildItem $g3vDir -Filter 'g3v_*.png' -ErrorAction SilentlyContinue | Remove-Item -Force
@('g3v_manifest.json','g3v_result.json','g3v_representative_proxy.blend','g3v_contact_sheet.png') | ForEach-Object {
    $p = Join-Path $g3vDir $_
    if (Test-Path $p) { Remove-Item $p -Force }
}
$stdout = Join-Path $logDir 'blender_stdout.log'
$stderr = Join-Path $logDir 'blender_stderr.log'
Remove-Item $stdout,$stderr -Force -ErrorAction SilentlyContinue

$pitch = [int]$baseline.camera_pitch_deg
$heroPx = [int]$baseline.protagonist_reference_height_px
Write-Host "[RUN] ONE Blender background process | G3V | 640x360 / ${pitch}deg / ${heroPx}px..." -ForegroundColor Cyan

$argumentString = '--background --python-exit-code 1 --python "{0}" -- --mpfb-root "{1}" --mpfb-user-root "{2}" --target-script "{3}" --g2-blend "{4}" --g2-manifest "{5}" --output-dir "{6}" --pitch {7} --hero-px {8}' -f $bootstrapScript,$mpfbRoot,$mpfbUserRoot,$targetScript,$g2Blend,$g2Manifest,$g3vDir,$pitch,$heroPx
$proc = Start-Process -FilePath $script:BlenderExe -ArgumentList $argumentString -Wait -PassThru -NoNewWindow -RedirectStandardOutput $stdout -RedirectStandardError $stderr
Get-Content $stdout -ErrorAction SilentlyContinue | Out-Host
if (Test-Path $stderr) {
    $e = Get-Content $stderr -Raw -ErrorAction SilentlyContinue
    if ($e) { Write-Host $e -ForegroundColor DarkYellow }
}
if ($proc.ExitCode -ne 0) { Fail "Blender exited with code $($proc.ExitCode). See $stdout and $stderr" }

$stdoutText = Get-Content $stdout -Raw -ErrorAction SilentlyContinue
if ($stdoutText -notmatch 'G3V_MPFB_BOOTSTRAP=PASS') {
    Fail 'Blender exited successfully but the direct MPFB service bootstrap did not report PASS.'
}

$manifestPath = Join-Path $g3vDir 'g3v_manifest.json'
if (-not (Test-Path $manifestPath -PathType Leaf)) { Fail 'G3V manifest was not created.' }
$manifest = Get-Content $manifestPath -Raw | ConvertFrom-Json
if ($manifest.gate -ne 'G3V' -or $manifest.status -ne 'REVIEW_REQUIRED') { Fail 'Unexpected G3V manifest status.' }
if ($manifest.outputs.Count -ne 8) { Fail "Expected 8 visible G3V outputs, got $($manifest.outputs.Count)." }
if ([int]$manifest.matching_motion_bones -lt 18) { Fail "Too few CMU-compatible matching bones: $($manifest.matching_motion_bones)" }
foreach ($o in $manifest.outputs) {
    if (-not (Test-Path $o.file -PathType Leaf)) { Fail "G3V output missing: $($o.file)" }
    $h = (Get-FileHash -Algorithm SHA256 $o.file).Hash.ToLowerInvariant()
    if ($h -ne $o.sha256.ToString().ToLowerInvariant()) { Fail "G3V output hash mismatch: $($o.file)" }
}

# 4 real walk phases x 2 rows.
Add-Type -AssemblyName System.Drawing
$cellW=640; $cellH=360; $cols=4; $rows=2
$sheet=New-Object System.Drawing.Bitmap ($cellW*$cols),($cellH*$rows)
$g=[System.Drawing.Graphics]::FromImage($sheet)
$g.InterpolationMode=[System.Drawing.Drawing2D.InterpolationMode]::NearestNeighbor
$font=New-Object System.Drawing.Font('Arial',13,[System.Drawing.FontStyle]::Bold)
$white=New-Object System.Drawing.SolidBrush([System.Drawing.Color]::White)
$black=New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(205,0,0,0))
$variants=@('flat_representative','pixel_4band_semantic')
$labels=@('A representative continuous geometry','B native semantic 4-band pixel')
try {
    for ($r=0;$r -lt 2;$r++) {
        for ($c=0;$c -lt $manifest.source_frames.Count;$c++) {
            $frame=[int]$manifest.source_frames[$c]
            $o=$manifest.outputs | Where-Object { $_.variant -eq $variants[$r] -and [int]$_.frame -eq $frame } | Select-Object -First 1
            if (-not $o) { Fail "Missing contact-sheet source variant=$($variants[$r]) frame=$frame" }
            $img=[System.Drawing.Image]::FromFile($o.file)
            try {
                $x=$c*$cellW; $y=$r*$cellH
                $g.DrawImage($img,$x,$y,$cellW,$cellH)
                $g.FillRectangle($black,$x+8,$y+8,430,29)
                $g.DrawString(('{0} | frame {1}' -f $labels[$r],$frame),$font,$white,$x+14,$y+11)
            } finally { $img.Dispose() }
        }
    }
    $sheetPath=Join-Path $g3vDir 'g3v_contact_sheet.png'
    $sheet.Save($sheetPath,[System.Drawing.Imaging.ImageFormat]::Png)
} finally {
    $g.Dispose(); $sheet.Dispose(); $font.Dispose(); $white.Dispose(); $black.Dispose()
}
if (-not (Test-Path $sheetPath -PathType Leaf)) { Fail 'G3V contact sheet was not created.' }
$sheetHash=(Get-FileHash -Algorithm SHA256 $sheetPath).Hash.ToLowerInvariant()

$result=[ordered]@{
    gate='G3V'; status='REVIEW_REQUIRED'; timestamp=(Get-Date).ToString('o')
    mpfb_version=$mpfbVersion; mpfb_archive_sha256=$actualHash; mpfb_archive_url=$archiveUrl
    mpfb_load_mode='direct_archive_service_bootstrap'; mpfb_package_root=$mpfbRoot
    baseline=$baseline; source_gate='G2'; contact_sheet=$sheetPath; contact_sheet_sha256=$sheetHash
    manifest=$manifestPath; blend=$manifest.blend; stdout_log=$stdout; stderr_log=$stderr
}
$resultPath=Join-Path $g3vDir 'g3v_result.json'
$result | ConvertTo-Json -Depth 10 | Set-Content -Path $resultPath -Encoding UTF8

Write-Host ''
Write-Host 'G3V: REVIEW REQUIRED' -ForegroundColor Yellow
Write-Host "CONTACT SHEET: $sheetPath"
Write-Host "RESULT:        $resultPath"
Write-Host "MPFB:          $mpfbVersion | direct pinned archive | $actualHash"
Write-Host "SHEET SHA256:  $sheetHash"
Write-Host ''
Write-Host 'STOP. Share g3v_contact_sheet.png. Do not start G4 until this representative visual kill switch is reviewed.' -ForegroundColor Yellow
