param(
    [string]$RepoRoot = 'D:\GOOGLE DRIVE\DEV\Roguelite',
    [string]$Workspace = 'Z:\AI\RogueliteCharacterPipeline',
    [switch]$SkipInstall
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Find-BlenderExe {
    $candidates = @()

    if ($env:BLENDER_EXE) { $candidates += $env:BLENDER_EXE }

    $cmd = Get-Command blender.exe -ErrorAction SilentlyContinue
    if ($cmd) { $candidates += $cmd.Source }

    $roots = @(
        'C:\Program Files\Blender Foundation',
        'C:\Program Files (x86)\Blender Foundation'
    )

    foreach ($root in $roots) {
        if (Test-Path $root) {
            $candidates += Get-ChildItem -Path $root -Filter blender.exe -Recurse -ErrorAction SilentlyContinue |
                Select-Object -ExpandProperty FullName
        }
    }

    $found = @($candidates | Where-Object { $_ -and (Test-Path $_ -PathType Leaf) } | Select-Object -Unique)
    if ($found.Count -eq 0) { return $null }

    # Prefer the newest installed path lexically/version-wise when more than one exists.
    return ($found | Sort-Object -Descending | Select-Object -First 1)
}

function Fail([string]$Message) {
    Write-Host "G0: FAIL - $Message" -ForegroundColor Red
    exit 1
}

Write-Host ''
Write-Host 'Roguelite deterministic character pipeline - G0 HEADLESS AUTOMATION' -ForegroundColor Cyan
Write-Host 'This gate proves that Blender can be installed/found, driven without GUI, render a known scene and emit a machine-readable manifest.'
Write-Host 'No mocap, Exilada asset, rigging, diffusion or production pixel-art work is performed here.'
Write-Host ''

if (-not (Test-Path $RepoRoot -PathType Container)) {
    Fail "Repository root not found: $RepoRoot"
}

$probeScript = Join-Path $RepoRoot 'tools\deterministic-character-pipeline\g0_headless_probe.py'
if (-not (Test-Path $probeScript -PathType Leaf)) {
    Fail "Probe script not found: $probeScript. Run git pull --ff-only first."
}

# Basic host validation.
$os = Get-CimInstance Win32_OperatingSystem
Write-Host ("[INFO] OS: {0} {1}" -f $os.Caption, $os.Version)
if ($os.Caption -notmatch 'Windows 11') {
    Fail 'Windows 11 was not detected.'
}

$driveName = ([System.IO.Path]::GetPathRoot($Workspace)).TrimEnd('\').TrimEnd(':')
$drive = Get-PSDrive -Name $driveName -ErrorAction SilentlyContinue
if (-not $drive) {
    Fail "Workspace drive not available: $driveName`:"
}
$freeGB = [math]::Round($drive.Free / 1GB, 2)
Write-Host ("[INFO] Free space on {0}: {1} GB" -f $driveName, $freeGB)
if ($freeGB -lt 5) {
    Fail "Less than 5 GB free on $driveName`:"
}

$blender = Find-BlenderExe
if (-not $blender) {
    if ($SkipInstall) {
        Fail 'Blender is not installed/found and -SkipInstall was requested.'
    }

    $winget = Get-Command winget.exe -ErrorAction SilentlyContinue
    if (-not $winget) {
        Fail 'Blender is not installed and winget.exe is unavailable.'
    }

    Write-Host '[INSTALL] Blender not found. Installing Blender Foundation package through winget...' -ForegroundColor Yellow
    & winget.exe install --id BlenderFoundation.Blender -e --accept-package-agreements --accept-source-agreements --silent
    if ($LASTEXITCODE -ne 0) {
        Fail "winget Blender install failed with exit code $LASTEXITCODE"
    }

    $blender = Find-BlenderExe
    if (-not $blender) {
        Fail 'Blender installation completed but blender.exe still could not be located.'
    }
}

Write-Host "[OK] Blender: $blender" -ForegroundColor Green

$versionOutput = & $blender --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Fail 'blender.exe --version failed.'
}
$versionLine = ($versionOutput | Select-Object -First 1).ToString()
Write-Host "[OK] $versionLine" -ForegroundColor Green

$g0Dir = Join-Path $Workspace 'g0'
$logDir = Join-Path $g0Dir 'logs'
New-Item -ItemType Directory -Force -Path $g0Dir, $logDir | Out-Null

# Remove only known G0 outputs so each run proves a fresh headless render.
@('g0_probe.png', 'g0_probe.blend', 'g0_manifest.json', 'g0_result.json') | ForEach-Object {
    $p = Join-Path $g0Dir $_
    if (Test-Path $p) { Remove-Item $p -Force }
}

$stdout = Join-Path $logDir 'blender_stdout.log'
$stderr = Join-Path $logDir 'blender_stderr.log'
Remove-Item $stdout, $stderr -Force -ErrorAction SilentlyContinue

Write-Host '[RUN] Starting Blender in background/factory mode...' -ForegroundColor Cyan
$blenderArgs = @(
    '--background',
    '--factory-startup',
    '--python',
    $probeScript,
    '--',
    '--output-dir',
    $g0Dir
)

# Do NOT use Start-Process -ArgumentList here. Windows PowerShell joins that array
# into one command-line string and can split paths containing spaces. The call
# operator with argument-array splatting preserves each path as one native argument.
& $blender @blenderArgs 1> $stdout 2> $stderr
$blenderExitCode = $LASTEXITCODE

Get-Content $stdout -ErrorAction SilentlyContinue | Out-Host
if (Test-Path $stderr) {
    $errText = Get-Content $stderr -Raw -ErrorAction SilentlyContinue
    if ($errText) { Write-Host $errText -ForegroundColor DarkYellow }
}

if ($blenderExitCode -ne 0) {
    Fail "Blender headless process exited with code $blenderExitCode. See $stdout and $stderr"
}

$png = Join-Path $g0Dir 'g0_probe.png'
$blend = Join-Path $g0Dir 'g0_probe.blend'
$manifestPath = Join-Path $g0Dir 'g0_manifest.json'

foreach ($required in @($png, $blend, $manifestPath)) {
    if (-not (Test-Path $required -PathType Leaf)) {
        Fail "Expected output missing: $required"
    }
}

$manifest = Get-Content $manifestPath -Raw | ConvertFrom-Json
if ($manifest.gate -ne 'G0' -or $manifest.status -ne 'PASS') {
    Fail 'Manifest did not report G0/PASS.'
}

$actualHash = (Get-FileHash -Algorithm SHA256 $png).Hash.ToLowerInvariant()
$manifestHash = $manifest.png_sha256.ToString().ToLowerInvariant()
if ($actualHash -ne $manifestHash) {
    Fail "PNG hash mismatch: manifest=$manifestHash actual=$actualHash"
}

$result = [ordered]@{
    gate = 'G0'
    status = 'PASS'
    timestamp = (Get-Date).ToString('o')
    repo_root = $RepoRoot
    workspace = $Workspace
    blender_exe = $blender
    blender_version = $manifest.blender_version
    render_engine = $manifest.render_engine
    png = $png
    png_sha256 = $actualHash
    blend = $blend
    manifest = $manifestPath
    stdout_log = $stdout
    stderr_log = $stderr
}
$resultPath = Join-Path $g0Dir 'g0_result.json'
$result | ConvertTo-Json -Depth 6 | Set-Content -Path $resultPath -Encoding UTF8

Write-Host ''
Write-Host 'G0: PASS' -ForegroundColor Green
Write-Host "PNG:      $png"
Write-Host "MANIFEST: $manifestPath"
Write-Host "RESULT:   $resultPath"
Write-Host "SHA256:   $actualHash"
Write-Host ''
Write-Host 'STOP. Do not proceed to G1 yet. Share g0_probe.png and g0_result.json for review.' -ForegroundColor Yellow
exit 0
