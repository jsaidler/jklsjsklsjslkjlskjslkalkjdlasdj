param(
    [string]$WanGpRoot = 'Z:\AI\WanGP',
    [string]$UnifiedRoot = 'Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\unified',
    [int]$Width = 256,
    [int]$Height = 456,
    [double]$Fps = 24.0,
    [int]$SpikeFrames = 65
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version 2.0

$Python = Join-Path $WanGpRoot 'env_uv\Scripts\python.exe'
$Builder = Join-Path $PSScriptRoot 'build_wan_animate2_rgb_driver_proxy_idw.py'
$Library = Join-Path $UnifiedRoot 'joao_motion_library_v1.json'
$PoseDriver = Join-Path $UnifiedRoot 'first_driver_v3\behavioral_driver_coco133.jsonl'
$OutputDir = Join-Path $UnifiedRoot 'first_driver_v3\wan_rgb_proxy'

foreach ($item in @(
    @{ Name='WanGP Python'; Path=$Python },
    @{ Name='IDW RGB proxy builder'; Path=$Builder },
    @{ Name='Unified library'; Path=$Library },
    @{ Name='Validated v3 pose driver'; Path=$PoseDriver }
)) {
    if (-not (Test-Path -LiteralPath $item.Path -PathType Leaf)) {
        throw ('Missing ' + $item.Name + ': ' + $item.Path)
    }
}

$FfmpegCmd = Get-Command ffmpeg -ErrorAction SilentlyContinue
if ($null -eq $FfmpegCmd) {
    throw 'ffmpeg is not available in PATH.'
}

Write-Host 'WAN-ANIMATE-2 RGB DRIVER PROXY SPIKE / IDW'
Write-Host '==========================================='
Write-Host ('Library: ' + $Library)
Write-Host ('Pose driver: ' + $PoseDriver)
Write-Host ('Output: ' + $OutputDir)
Write-Host ('Proxy canvas: ' + $Width + 'x' + $Height + ' @ ' + $Fps + ' fps')
Write-Host ('Spike: first ' + $SpikeFrames + ' frames only')
Write-Host ''
Write-Host 'Triangle-by-triangle Delaunay rendering is retired after local runtime stalls.'
Write-Host 'This version uses a coarse IDW inverse deformation field and exactly one cv2.remap per frame.'
Write-Host 'Stage markers and per-frame timing are printed. No DWPose and no Wan-Animate-2 inference are invoked.'
Write-Host ''

& $Python $Builder `
    '--library' $Library `
    '--pose-driver' $PoseDriver `
    '--output-dir' $OutputDir `
    '--width' $Width `
    '--height' $Height `
    '--fps' $Fps `
    '--spike-frames' $SpikeFrames `
    '--ffmpeg' $FfmpegCmd.Source

if ($LASTEXITCODE -ne 0) {
    throw ('RGB driver IDW proxy spike failed with exit code ' + $LASTEXITCODE)
}

$Manifest = Join-Path $OutputDir 'rgb_driver_proxy_manifest.json'
$Contact = Join-Path $OutputDir 'behavioral_driver_rgb_proxy_contact.jpg'
$Spike = Join-Path $OutputDir ('behavioral_driver_rgb_proxy_spike' + $SpikeFrames + '.mp4')
$Reference = Join-Path $OutputDir 'rgb_proxy_anchor_reference.png'
$NeutralReference = Join-Path $OutputDir 'rgb_proxy_anchor_neutral.png'
foreach ($path in @($Manifest,$Contact,$Spike,$Reference,$NeutralReference)) {
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        throw ('Expected output missing: ' + $path)
    }
}

Write-Host ''
Write-Host 'WAN RGB DRIVER IDW PROXY SPIKE: COMPLETE'
Write-Host ('Manifest: ' + $Manifest)
Write-Host ('Reference: ' + $Reference)
Write-Host ('Neutral reference: ' + $NeutralReference)
Write-Host ('Spike driver: ' + $Spike)
Write-Host ('Upload this contact sheet: ' + $Contact)
Write-Host ('Upload this driver video: ' + $Spike)
Write-Host 'Do not run Wan-Animate-2 until the RGB proxy is visually reviewed.'
