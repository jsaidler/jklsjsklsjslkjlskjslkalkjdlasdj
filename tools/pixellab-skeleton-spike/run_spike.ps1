param(
    [string]$Master = 'D:\GOOGLE DRIVE\DEV\Roguelite\assets\source\characters\exilada\reference\exilada_master.png',
    [string]$Workspace = 'D:\AI\PixelLabSkeletonSpike',
    [int]$Size = 128,
    [int]$Seed = 20260904,
    [int]$PaletteColors = 24,
    [ValidateSet('side','low top-down','high top-down')][string]$View = 'side',
    [ValidateSet('south','south-east','east','north-east','north','north-west','west','south-west')][string]$Direction = 'south-east'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if (-not (Test-Path $Master)) {
    throw "Canonical Exilada master not found: $Master"
}
if (-not (Get-Command py.exe -ErrorAction SilentlyContinue)) {
    throw 'py.exe is required.'
}

New-Item -ItemType Directory -Force -Path $Workspace | Out-Null
$Venv = Join-Path $Workspace '.venv'
$Python = Join-Path $Venv 'Scripts\python.exe'

if (-not (Test-Path $Python)) {
    Write-Host "Creating lightweight PixelLab spike venv: $Venv" -ForegroundColor Cyan
    & py.exe -3.14 -m venv $Venv
    if ($LASTEXITCODE -ne 0) { throw 'Failed to create Python venv.' }
}

$Requirements = Join-Path $PSScriptRoot 'requirements.txt'
Write-Host 'Installing/verifying lightweight dependencies...' -ForegroundColor Cyan
& $Python -m pip install -q --disable-pip-version-check -r $Requirements
if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed.' }

if (-not $env:PIXELLAB_SECRET) {
    $secure = Read-Host 'PixelLab API token (input hidden)' -AsSecureString
    $ptr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
    try {
        $env:PIXELLAB_SECRET = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr)
    } finally {
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr)
    }
}
if (-not $env:PIXELLAB_SECRET) { throw 'PIXELLAB_SECRET is empty.' }

Write-Host ''
Write-Host 'PixelLab skeleton spike contract:' -ForegroundColor Cyan
Write-Host "  master:     $Master"
Write-Host "  workspace:  $Workspace"
Write-Host "  canvas:     ${Size}x${Size}"
Write-Host "  seed:       $Seed"
Write-Host "  palette:    $PaletteColors colors, extracted deterministically from canonical master"
Write-Host "  view:       $View"
Write-Host "  direction:  $Direction"
Write-Host '  generation: ONE 4-frame animate-with-skeleton request'
Write-Host '  corrections: none; no retries, inpainting, manual skeleton edits, or seed fishing'
Write-Host '  Pixel Engine: FORBIDDEN unless this spike passes'
Write-Host ''

$Script = Join-Path $PSScriptRoot 'pixellab_spike.py'
& $Python $Script `
    --master $Master `
    --workspace $Workspace `
    --size $Size `
    --seed $Seed `
    --palette-colors $PaletteColors `
    --view $View `
    --direction $Direction
$Code = $LASTEXITCODE

Write-Host ''
Write-Host "Spike process exit code: $Code"
if ($Code -eq 2) {
    Write-Host 'Automatic QA rejected the key poses. Pixel Engine must NOT be used.' -ForegroundColor Red
    exit 2
}
if ($Code -ne 0) {
    throw "PixelLab skeleton spike failed with exit code $Code"
}
Write-Host 'Automatic pre-gate passed. Inspect contact_sheet.png before any Pixel Engine work.' -ForegroundColor Green
