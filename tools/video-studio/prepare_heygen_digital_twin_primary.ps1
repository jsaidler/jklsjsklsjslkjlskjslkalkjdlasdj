param(
    [string]$SourceVideo = 'Z:\AI\VideoStudio\profiles\joao\behavior\avatar_v\sources\VID_20260911_140124885.mp4',
    [string]$OutputRoot = 'Z:\AI\VideoStudio\profiles\joao\behavior\avatar_v\prepared'
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version 2.0

function Resolve-Executable([string]$Name) {
    $cmd = Get-Command $Name -ErrorAction SilentlyContinue
    if ($null -eq $cmd) { return $null }
    return $cmd.Source
}

$ffmpeg = Resolve-Executable 'ffmpeg.exe'
if (-not $ffmpeg) { $ffmpeg = Resolve-Executable 'ffmpeg' }
$ffprobe = Resolve-Executable 'ffprobe.exe'
if (-not $ffprobe) { $ffprobe = Resolve-Executable 'ffprobe' }
if (-not $ffmpeg) { throw 'ffmpeg not found in PATH.' }
if (-not $ffprobe) { throw 'ffprobe not found in PATH.' }

if (-not (Test-Path -LiteralPath $SourceVideo -PathType Leaf)) {
    throw "Primary source not found: $SourceVideo"
}

New-Item -ItemType Directory -Force -Path $OutputRoot | Out-Null

$SourceVideo = (Resolve-Path -LiteralPath $SourceVideo).Path
$OutputVideo = Join-Path $OutputRoot 'joao_heygen_digital_twin_primary_1080p_h264.mp4'
$ManifestPath = Join-Path $OutputRoot 'joao_heygen_digital_twin_primary_manifest.json'

function Probe([string]$Path) {
    $json = & $ffprobe -v error -show_streams -show_format -of json -- "$Path"
    if ($LASTEXITCODE -ne 0) { throw "ffprobe failed for: $Path" }
    return (($json -join "`n") | ConvertFrom-Json)
}

$sourceProbe = Probe $SourceVideo
$sourceVideoStream = @($sourceProbe.streams | Where-Object { $_.codec_type -eq 'video' } | Select-Object -First 1)
$sourceAudioStream = @($sourceProbe.streams | Where-Object { $_.codec_type -eq 'audio' } | Select-Object -First 1)
if ($sourceVideoStream.Count -eq 0) { throw 'Source has no readable video stream.' }
if ($sourceAudioStream.Count -eq 0) { throw 'Source has no readable audio stream.' }

Write-Host 'HEYGEN DIGITAL TWIN PRIMARY PREPARATION'
Write-Host '======================================='
Write-Host ('Source: ' + $SourceVideo)
Write-Host ('Output: ' + $OutputVideo)
Write-Host ''
Write-Host 'Creating a full-duration, continuous 1080p H.264/AAC upload-safe derivative.'
Write-Host 'No trimming, splicing, looping, frame interpolation, stabilization, retiming or content edits are applied.'
Write-Host ''

$ffArgs = @(
    '-hide_banner','-loglevel','error','-y',
    '-i', $SourceVideo,
    '-map','0:v:0','-map','0:a:0',
    '-vf','scale=1920:1080:flags=lanczos',
    '-c:v','libx264','-preset','slow','-crf','14','-pix_fmt','yuv420p',
    '-c:a','aac','-b:a','192k',
    '-movflags','+faststart',
    $OutputVideo
)
& $ffmpeg @ffArgs
if ($LASTEXITCODE -ne 0) { throw 'ffmpeg transcode failed.' }
if (-not (Test-Path -LiteralPath $OutputVideo -PathType Leaf)) { throw 'Expected output video was not created.' }

$outProbe = Probe $OutputVideo
$outVideoStream = @($outProbe.streams | Where-Object { $_.codec_type -eq 'video' } | Select-Object -First 1)[0]
$outAudioStream = @($outProbe.streams | Where-Object { $_.codec_type -eq 'audio' } | Select-Object -First 1)[0]

$sourceDuration = [double]::Parse([string]$sourceProbe.format.duration, [Globalization.CultureInfo]::InvariantCulture)
$outDuration = [double]::Parse([string]$outProbe.format.duration, [Globalization.CultureInfo]::InvariantCulture)
if ([Math]::Abs($sourceDuration - $outDuration) -gt 0.15) {
    throw ("Duration mismatch after transcode. Source={0:F3}s Output={1:F3}s" -f $sourceDuration, $outDuration)
}

$sourceHash = (Get-FileHash -LiteralPath $SourceVideo -Algorithm SHA256).Hash
$outHash = (Get-FileHash -LiteralPath $OutputVideo -Algorithm SHA256).Hash

$manifest = [ordered]@{
    schema = 'HEYGEN-DIGITAL-TWIN-PRIMARY-01'
    created = (Get-Date -Format 'yyyy-MM-ddTHH:mm:ss')
    role = 'primary Digital Twin / Video Look upload candidate'
    provider = 'HeyGen'
    source = [ordered]@{
        path = $SourceVideo
        sha256 = $sourceHash
        duration_seconds = [Math]::Round($sourceDuration, 3)
        width = [int]$sourceVideoStream[0].width
        height = [int]$sourceVideoStream[0].height
        video_codec = [string]$sourceVideoStream[0].codec_name
        audio_codec = [string]$sourceAudioStream[0].codec_name
    }
    prepared = [ordered]@{
        path = $OutputVideo
        sha256 = $outHash
        duration_seconds = [Math]::Round($outDuration, 3)
        width = [int]$outVideoStream.width
        height = [int]$outVideoStream.height
        video_codec = [string]$outVideoStream.codec_name
        audio_codec = [string]$outAudioStream.codec_name
        preservation = 'Full duration, continuous. No cuts/splices/loops/retiming/content edits. Only scale + codec conversion.'
    }
}
$manifest | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $ManifestPath -Encoding UTF8

Write-Host ''
Write-Host 'RESULT'
Write-Host '======'
Write-Host 'HEYGEN PRIMARY SOURCE PREPARED'
Write-Host ('Source duration: {0:F3}s' -f $sourceDuration)
Write-Host ('Output duration: {0:F3}s' -f $outDuration)
Write-Host ('Output: ' + $OutputVideo)
Write-Host ('Manifest: ' + $ManifestPath)
