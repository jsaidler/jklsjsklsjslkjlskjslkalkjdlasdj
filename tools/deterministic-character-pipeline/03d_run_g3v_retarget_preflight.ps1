param(
    [string]$RepoRoot = 'D:\GOOGLE DRIVE\DEV\Roguelite',
    [string]$Workspace = 'Z:\AI\RogueliteCharacterPipeline'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Fail([string]$Message) {
    Write-Host "G3V RETARGET: FAIL - $Message" -ForegroundColor Red
    exit 1
}

function Find-BlenderExe {
    $candidates = @()
    if ($env:BLENDER_EXE) { $candidates += $env:BLENDER_EXE }
    $cmd = Get-Command blender.exe -ErrorAction SilentlyContinue
    if ($cmd) { $candidates += $cmd.Source }
    foreach ($root in @('C:\Program Files\Blender Foundation','C:\Program Files (x86)\Blender Foundation')) {
        if (Test-Path $root) {
            $candidates += Get-ChildItem -Path $root -Filter blender.exe -Recurse -ErrorAction SilentlyContinue |
                Select-Object -ExpandProperty FullName
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
Write-Host 'Roguelite - G3V RETARGET PREFLIGHT' -ForegroundColor Cyan
Write-Host 'Skeleton-only. No Exilada render. Compares source/target rest rigs and validates retarget numerically before returning to G3V.'
Write-Host ''

if (-not (Test-Path $RepoRoot -PathType Container)) { Fail "Repository root not found: $RepoRoot" }

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
    if (-not (Test-Path $p -PathType Leaf)) { Fail "Required G2 artifact missing: $p" }
}

$targetScript = Join-Path $RepoRoot 'tools\deterministic-character-pipeline\g3v_retarget_preflight.py'
$bootstrapScript = Join-Path $RepoRoot 'tools\deterministic-character-pipeline\g3v_retarget_bootstrap.py'
foreach ($p in @($targetScript,$bootstrapScript)) {
    if (-not (Test-Path $p -PathType Leaf)) { Fail "Retarget preflight script missing: $p. Run git pull --ff-only first." }
}

$BlenderExe = Find-BlenderExe
if (-not $BlenderExe) { Fail 'Blender could not be located.' }
Write-Host "[OK] Blender: $BlenderExe" -ForegroundColor Green

$deps = Join-Path $Workspace 'dependencies\g3v'
New-Item -ItemType Directory -Force -Path $deps | Out-Null
$mpfbVersion = '2.0.17'
$mpfbZip = Join-Path $deps "mpfb-$mpfbVersion.zip"
$expectedHash = '4f0a879d64a39bf646fbf5f53601ac678855da329d650617dca5737548239a87'

if (-not (Test-Path $mpfbZip -PathType Leaf)) {
    Write-Host "[DOWNLOAD] Cached MPFB missing; resolving official $mpfbVersion package..." -ForegroundColor Cyan
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.SecurityProtocolType]::Tls12
    $api = 'https://extensions.blender.org/api/v1/extensions/?blender_version=5.1.1&platform=windows-x64'
    try {
        $meta = Invoke-RestMethod -Uri $api -UseBasicParsing
        $pkg = @($meta.data | Where-Object { $_.id -eq 'mpfb' -and $_.version -eq $mpfbVersion }) | Select-Object -First 1
    } catch {
        Fail "Could not query official MPFB package metadata: $($_.Exception.Message)"
    }
    if (-not $pkg) { Fail "Official Blender Extensions API did not return MPFB $mpfbVersion." }
    $archiveUrl = [string]$pkg.archive_url
    if ($archiveUrl -notmatch '^https?://') { $archiveUrl = 'https://extensions.blender.org' + $archiveUrl }
    try { Invoke-WebRequest -Uri $archiveUrl -OutFile $mpfbZip -UseBasicParsing }
    catch { Fail "Could not download MPFB: $($_.Exception.Message)" }
}

$actualHash = (Get-FileHash -Algorithm SHA256 $mpfbZip).Hash.ToLowerInvariant()
if ($actualHash -ne $expectedHash) {
    Fail "MPFB SHA256 mismatch. Expected $expectedHash, got $actualHash"
}
Write-Host "[OK] MPFB $mpfbVersion SHA256 $actualHash" -ForegroundColor Green

$mpfbExtract = Join-Path $deps "mpfb-$mpfbVersion-unpacked"
$mpfbRoot = Find-MpfbPackageRoot $mpfbExtract
if (-not $mpfbRoot) {
    if (Test-Path $mpfbExtract) { Remove-Item $mpfbExtract -Recurse -Force }
    New-Item -ItemType Directory -Force -Path $mpfbExtract | Out-Null
    Expand-Archive -Path $mpfbZip -DestinationPath $mpfbExtract -Force
    $mpfbRoot = Find-MpfbPackageRoot $mpfbExtract
}
if (-not $mpfbRoot) { Fail "Could not locate MPFB package root: $mpfbExtract" }
$mpfbUserRoot = Join-Path $deps 'mpfb_user'
New-Item -ItemType Directory -Force -Path $mpfbUserRoot | Out-Null

$outDir = Join-Path $Workspace 'g3v_retarget'
$logDir = Join-Path $outDir 'logs'
New-Item -ItemType Directory -Force -Path $outDir,$logDir | Out-Null
Get-ChildItem $outDir -Filter 'retarget_*.png' -ErrorAction SilentlyContinue | Remove-Item -Force
foreach ($name in @('g3v_retarget_manifest.json','g3v_retarget_contact_sheet.png','g3v_retarget_result.json')) {
    $p = Join-Path $outDir $name
    if (Test-Path $p) { Remove-Item $p -Force }
}
$stdout = Join-Path $logDir 'blender_stdout.log'
$stderr = Join-Path $logDir 'blender_stderr.log'
Remove-Item $stdout,$stderr -Force -ErrorAction SilentlyContinue

$pitch = [int]$baseline.camera_pitch_deg
$heroPx = [int]$baseline.protagonist_reference_height_px

Write-Host '[RUN] one Blender process | skeleton-only rest-aware retarget preflight...' -ForegroundColor Cyan
$argumentString = '--background --python-exit-code 1 --python "{0}" -- --mpfb-root "{1}" --mpfb-user-root "{2}" --target-script "{3}" --g2-blend "{4}" --g2-manifest "{5}" --output-dir "{6}" --pitch {7} --hero-px {8}' -f `
    $bootstrapScript,$mpfbRoot,$mpfbUserRoot,$targetScript,$g2Blend,$g2Manifest,$outDir,$pitch,$heroPx

$proc = Start-Process -FilePath $BlenderExe -ArgumentList $argumentString -Wait -PassThru -NoNewWindow `
    -RedirectStandardOutput $stdout -RedirectStandardError $stderr

Get-Content $stdout -ErrorAction SilentlyContinue | Out-Host
if (Test-Path $stderr) {
    $errText = Get-Content $stderr -Raw -ErrorAction SilentlyContinue
    if ($errText) { Write-Host $errText -ForegroundColor DarkYellow }
}
if ($proc.ExitCode -ne 0) {
    Fail "Blender exited with code $($proc.ExitCode). See $stdout and $stderr"
}

$stdoutText = Get-Content $stdout -Raw
if ($stdoutText -notmatch 'G3V_RETARGET_BOOTSTRAP=PASS') { Fail 'MPFB retarget bootstrap did not report PASS.' }
if ($stdoutText -notmatch 'G3V_RETARGET_NUMERIC_AUDIT=PASS') { Fail 'Retarget numeric audit did not report PASS.' }

$manifestPath = Join-Path $outDir 'g3v_retarget_manifest.json'
if (-not (Test-Path $manifestPath -PathType Leaf)) { Fail 'Retarget manifest missing.' }
$manifest = Get-Content $manifestPath -Raw | ConvertFrom-Json
if ($manifest.gate -ne 'G3V_RETARGET_PREFLIGHT' -or $manifest.status -ne 'REVIEW_REQUIRED') {
    Fail 'Unexpected retarget manifest status.'
}
if ($manifest.outputs.Count -ne 8) { Fail "Expected 8 skeleton renders, got $($manifest.outputs.Count)." }

foreach ($o in $manifest.outputs) {
    if (-not (Test-Path $o.file -PathType Leaf)) { Fail "Retarget output missing: $($o.file)" }
    $h = (Get-FileHash -Algorithm SHA256 $o.file).Hash.ToLowerInvariant()
    if ($h -ne $o.sha256.ToString().ToLowerInvariant()) { Fail "Retarget output hash mismatch: $($o.file)" }
}

Add-Type -AssemblyName System.Drawing
$cellW=640; $cellH=360; $cols=4; $rows=2
$sheet=New-Object System.Drawing.Bitmap ($cellW*$cols),($cellH*$rows)
$g=[System.Drawing.Graphics]::FromImage($sheet)
$g.InterpolationMode=[System.Drawing.Drawing2D.InterpolationMode]::NearestNeighbor
$font=New-Object System.Drawing.Font('Arial',13,[System.Drawing.FontStyle]::Bold)
$white=New-Object System.Drawing.SolidBrush([System.Drawing.Color]::White)
$black=New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(205,0,0,0))
$variants=@('source','target')
$labels=@('A G2 source skeleton','B retargeted MPFB cmu_mb skeleton')
try {
    for ($r=0;$r -lt 2;$r++) {
        for ($c=0;$c -lt $manifest.source_frames.Count;$c++) {
            $frame=[int]$manifest.source_frames[$c]
            $o=$manifest.outputs | Where-Object { $_.variant -eq $variants[$r] -and [int]$_.frame -eq $frame } | Select-Object -First 1
            if (-not $o) { Fail "Missing contact-sheet source $($variants[$r]) frame=$frame" }
            $img=[System.Drawing.Image]::FromFile($o.file)
            try {
                $x=$c*$cellW; $y=$r*$cellH
                $g.DrawImage($img,$x,$y,$cellW,$cellH)
                $g.FillRectangle($black,$x+8,$y+8,475,29)
                $g.DrawString(('{0} | frame {1}' -f $labels[$r],$frame),$font,$white,$x+14,$y+11)
            } finally { $img.Dispose() }
        }
    }
    $sheetPath=Join-Path $outDir 'g3v_retarget_contact_sheet.png'
    $sheet.Save($sheetPath,[System.Drawing.Imaging.ImageFormat]::Png)
} finally {
    $g.Dispose(); $sheet.Dispose(); $font.Dispose(); $white.Dispose(); $black.Dispose()
}

$result=[ordered]@{
    gate='G3V_RETARGET_PREFLIGHT'
    status='REVIEW_REQUIRED'
    timestamp=(Get-Date).ToString('o')
    chosen_method=$manifest.chosen_method
    contact_sheet=$sheetPath
    manifest=$manifestPath
    stdout_log=$stdout
    stderr_log=$stderr
}
$resultPath=Join-Path $outDir 'g3v_retarget_result.json'
$result | ConvertTo-Json -Depth 8 | Set-Content -Path $resultPath -Encoding UTF8

Write-Host ''
Write-Host 'G3V RETARGET PREFLIGHT: REVIEW REQUIRED' -ForegroundColor Yellow
Write-Host "METHOD:        $($manifest.chosen_method)"
Write-Host "CONTACT SHEET: $sheetPath"
Write-Host "MANIFEST:      $manifestPath"
Write-Host ''
Write-Host 'STOP. Share g3v_retarget_contact_sheet.png. Do not rerun G3V body rendering and do not start G4 yet.' -ForegroundColor Yellow
