param(
    [Parameter(Mandatory = $true)][string]$Source,
    [string]$Workspace = 'D:\AI\WanAnimate2',
    [double]$StartSeconds = 0.0
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Find-ComfyRoot([string]$Base) {
    foreach ($candidate in @($Base, (Join-Path $Base 'ComfyUI'))) {
        if ((Test-Path (Join-Path $candidate 'main.py')) -and (Test-Path (Join-Path $candidate '.git'))) {
            return $candidate
        }
    }
    return $null
}

if (-not (Test-Path $Source)) { throw "Source video not found: $Source" }

$ComfyRoot = Find-ComfyRoot $Workspace
if (-not $ComfyRoot) {
    throw "ComfyUI not found at $Workspace or $(Join-Path $Workspace 'ComfyUI'). Run bootstrap.ps1 first."
}

if (-not (Get-Command ffmpeg.exe -ErrorAction SilentlyContinue)) {
    Write-Host 'ffmpeg not found; installing with winget...' -ForegroundColor Cyan
    & winget.exe install -e --id Gyan.FFmpeg --accept-package-agreements --accept-source-agreements
    if ($LASTEXITCODE -ne 0) { throw 'ffmpeg installation failed.' }
    $env:Path = [Environment]::GetEnvironmentVariable('Path','Machine') + ';' + [Environment]::GetEnvironmentVariable('Path','User')
}

if (-not (Get-Command ffmpeg.exe -ErrorAction SilentlyContinue)) {
    throw 'ffmpeg was installed but is not visible in this PowerShell session. Reopen PowerShell and run this script again.'
}

$OutDir = Join-Path $ComfyRoot 'input'
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
$Out = Join-Path $OutDir 'exilada_driver_17f.mp4'

$Filter = 'fps=16,scale=384:576:force_original_aspect_ratio=decrease,pad=384:576:(ow-iw)/2:(oh-ih)/2:color=gray'

& ffmpeg.exe -hide_banner -loglevel warning -y `
    -ss $StartSeconds `
    -i $Source `
    -vf $Filter `
    -frames:v 17 `
    -an `
    -c:v libx264 `
    -pix_fmt yuv420p `
    -movflags +faststart `
    $Out

if ($LASTEXITCODE -ne 0) { throw 'ffmpeg failed while creating the 17-frame driver.' }

Write-Host "Driver written: $Out" -ForegroundColor Green

if (Get-Command ffprobe.exe -ErrorAction SilentlyContinue) {
    & ffprobe.exe -v error -select_streams v:0 -count_frames `
        -show_entries stream=width,height,r_frame_rate,nb_read_frames `
        -of default=noprint_wrappers=1 $Out
}

Write-Host ''
Write-Host 'Driver acceptance check:'
Write-Host '- exactly 17 frames'
Write-Host '- 384x576'
Write-Host '- 16 fps'
Write-Host '- first frame roughly matches the Exilada master opening pose'
Write-Host '- one small controlled step only; fixed camera; full body visible'
