param(
    [string]$UnifiedRoot = 'Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\unified',
    [int]$Width = 512,
    [int]$Height = 912,
    [double]$Fps = 24.0,
    [int]$Frames = 65
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version 2.0

$Python = 'python'
$Builder = Join-Path $PSScriptRoot 'build_wan_animate2_real_rgb_driver_spike.py'
$Library = Join-Path $UnifiedRoot 'joao_motion_library_v1.json'
$Plan = Join-Path $UnifiedRoot 'first_driver_v3\driver_plan.json'
$OutputDir = Join-Path $UnifiedRoot 'first_driver_v3\wan_real_rgb_spike'

foreach ($item in @(
    @{ Name='Builder'; Path=$Builder },
    @{ Name='Unified library'; Path=$Library },
    @{ Name='Driver v3 plan'; Path=$Plan }
)) {
    if (-not (Test-Path -LiteralPath $item.Path -PathType Leaf)) {
        throw ('Missing ' + $item.Name + ': ' + $item.Path)
    }
}

$Ffmpeg = Get-Command ffmpeg -ErrorAction SilentlyContinue
$Ffprobe = Get-Command ffprobe -ErrorAction SilentlyContinue
if ($null -eq $Ffmpeg) { throw 'ffmpeg is not available in PATH.' }
if ($null -eq $Ffprobe) { throw 'ffprobe is not available in PATH.' }

Write-Host 'WAN-ANIMATE-2 REAL RGB DRIVER SPIKE'
Write-Host '=================================='
Write-Host ('Library: ' + $Library)
Write-Host ('Driver plan: ' + $Plan)
Write-Host ('Output: ' + $OutputDir)
Write-Host ('Canvas: ' + $Width + 'x' + $Height + ' @ ' + $Fps + ' fps')
Write-Host ('Frames: ' + $Frames)
Write-Host ''
Write-Host 'Uses real RGB spans from the two validated v3 base units.'
Write-Host 'No still-image warp, no DWPose, no Wan-Animate-2 inference.'
Write-Host ''

& $Python $Builder `
    '--library' $Library `
    '--plan' $Plan `
    '--output-dir' $OutputDir `
    '--width' $Width `
    '--height' $Height `
    '--fps' $Fps `
    '--frames' $Frames `
    '--ffmpeg' $Ffmpeg.Source `
    '--ffprobe' $Ffprobe.Source

if ($LASTEXITCODE -ne 0) {
    throw ('Real RGB driver spike failed with exit code ' + $LASTEXITCODE)
}

$PoseVideo = Join-Path $OutputDir ('pose_video_real_spike' + $Frames + '.mp4')
$Reference = Join-Path $OutputDir 'reference_image_real.png'
$Contact = Join-Path $OutputDir 'pose_video_real_contact.jpg'
$Manifest = Join-Path $OutputDir 'real_rgb_spike_manifest.json'
foreach ($path in @($PoseVideo,$Reference,$Contact,$Manifest)) {
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        throw ('Expected output missing: ' + $path)
    }
}

Write-Host ''
Write-Host 'REAL RGB DRIVER SPIKE: COMPLETE'
Write-Host ('Pose video: ' + $PoseVideo)
Write-Host ('Reference: ' + $Reference)
Write-Host ('Contact sheet: ' + $Contact)
Write-Host ('Manifest: ' + $Manifest)
Write-Host 'Wan-Animate-2 remains NOT INVOKED until visual QA.'
