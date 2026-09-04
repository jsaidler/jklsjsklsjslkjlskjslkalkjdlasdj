param(
    [string]$Source = '',
    [switch]$UseOfficialDemo,
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

if ($UseOfficialDemo -and $Source) {
    throw 'Choose either -Source <video> OR -UseOfficialDemo, not both.'
}

if ($UseOfficialDemo) {
    $Source = Join-Path $OutDir 'wan_official_demo_template.mp4'
    $OfficialUrl = 'https://raw.githubusercontent.com/Wan-Video/Wan-Animate-2/main/examples/demo1/template.mp4'
    $needsDownload = -not (Test-Path $Source)
    if (-not $needsDownload) {
        $needsDownload = (Get-Item $Source).Length -lt 1MB
    }
    if ($needsDownload) {
        Write-Host 'Downloading the official Wan-Animate-2 demo driving video...' -ForegroundColor Cyan
        & curl.exe -L --fail --retry 3 --output $Source $OfficialUrl
        if ($LASTEXITCODE -ne 0) { throw 'Failed to download the official Wan-Animate-2 demo driving video.' }
    } else {
        Write-Host "Official demo source already present: $Source" -ForegroundColor Green
    }
} elseif (-not $Source) {
    throw @"
No driving-video source was supplied.

Either use your own local video:
  .\make_driver.ps1 -Source "D:\path\to\video.mp4" -StartSeconds 0

Or use the official Wan-Animate-2 demo video for the first infrastructure spike:
  .\make_driver.ps1 -UseOfficialDemo -StartSeconds 0
"@
}

if (-not (Test-Path $Source)) { throw "Source video not found: $Source" }

$Out = Join-Path $OutDir 'exilada_driver_17f.mp4'
$FirstFrame = Join-Path $OutDir 'exilada_driver_first_frame.png'
$ContactSheet = Join-Path $OutDir 'exilada_driver_contact_sheet.png'

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

& ffmpeg.exe -hide_banner -loglevel error -y -i $Out -frames:v 1 $FirstFrame
if ($LASTEXITCODE -ne 0) { throw 'Failed to extract the first driver frame.' }

# 17 frames arranged in a 5x4 contact sheet. This is only for visual validation;
# the actual model input remains the 384x576 MP4 above.
& ffmpeg.exe -hide_banner -loglevel error -y -i $Out `
    -vf 'scale=192:288,tile=5x4:padding=2:margin=2:color=gray' `
    -frames:v 1 $ContactSheet
if ($LASTEXITCODE -ne 0) { throw 'Failed to create the driver contact sheet.' }

if (Get-Command ffprobe.exe -ErrorAction SilentlyContinue) {
    Write-Host ''
    Write-Host 'Driver metadata:' -ForegroundColor Cyan
    & ffprobe.exe -v error -select_streams v:0 -count_frames `
        -show_entries stream=width,height,r_frame_rate,nb_read_frames `
        -of default=noprint_wrappers=1 $Out
}

Write-Host ''
Write-Host "First frame:  $FirstFrame" -ForegroundColor Green
Write-Host "Contact sheet: $ContactSheet" -ForegroundColor Green
Write-Host ''
Write-Host 'Driver acceptance check:'
Write-Host '- exactly 17 frames'
Write-Host '- 384x576'
Write-Host '- 16 fps'
Write-Host '- first frame roughly matches the Exilada master opening pose'
Write-Host '- body remains visible and camera framing is usable'
Write-Host '- motion is coherent enough to judge transfer'
if ($UseOfficialDemo) {
    Write-Host ''
    Write-Host 'NOTE: the official demo is acceptable for an infrastructure/motion-transfer spike.' -ForegroundColor Yellow
    Write-Host 'If its opening pose differs strongly from the Exilada master, a bad artistic result cannot by itself reject Wan-Animate-2.' -ForegroundColor Yellow
    Write-Host 'Use the generated first-frame/contact-sheet images to check pose compatibility before the final artistic gate.' -ForegroundColor Yellow
}
