param(
    [string]$SourceVideo = '',
    [string]$OutputRoot = 'Z:\AI\VideoStudio\profiles\joao\behavior\avatar_v'
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version 2.0

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$ReportDir = Join-Path $PSScriptRoot 'reports'
New-Item -ItemType Directory -Force -Path $ReportDir | Out-Null
$Stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$Report = Join-Path $ReportDir ('avatar_v_reference_prepare_' + $Stamp + '.txt')

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

function Find-SourceVideo {
    param([string]$Explicit)

    if ($Explicit) {
        if (-not (Test-Path -LiteralPath $Explicit -PathType Leaf)) {
            throw "Source video does not exist: $Explicit"
        }
        return (Resolve-Path -LiteralPath $Explicit).Path
    }

    $Candidates = @(
        'Z:\AI\MiniMaxH3\ComfyUI_windows_portable\ComfyUI\input\IA_TEST.mp4',
        'Z:\AI\MiniMaxH3\ComfyUI_windows_portable\ComfyUI\input\IA_TEST.MP4',
        'Z:\AI\WanAnimate2\input\video_studio\IA_TEST.mp4',
        'Z:\AI\WanAnimate2\input\video_studio\IA_TEST.MP4',
        'Z:\AI\IA_TEST.mp4',
        'Z:\AI\IA_TEST.MP4'
    )

    foreach ($candidate in $Candidates) {
        if (Test-Path -LiteralPath $candidate -PathType Leaf) {
            return (Resolve-Path -LiteralPath $candidate).Path
        }
    }

    $SearchRoots = @(
        'Z:\AI\MiniMaxH3',
        'Z:\AI\WanAnimate2',
        'Z:\AI\VideoStudio'
    )
    $Found = @()
    foreach ($root in $SearchRoots) {
        if (Test-Path -LiteralPath $root -PathType Container) {
            $Found += @(Get-ChildItem -LiteralPath $root -Filter 'IA_TEST.mp4' -File -Recurse -ErrorAction SilentlyContinue | Select-Object -ExpandProperty FullName)
            $Found += @(Get-ChildItem -LiteralPath $root -Filter 'IA_TEST.MP4' -File -Recurse -ErrorAction SilentlyContinue | Select-Object -ExpandProperty FullName)
        }
    }
    $Found = @($Found | Sort-Object -Unique)
    if ($Found.Count -eq 1) { return $Found[0] }
    if ($Found.Count -gt 1) {
        throw ("Multiple IA_TEST videos found. Re-run with -SourceVideo and one exact path:`n" + ($Found -join "`n"))
    }

    throw 'IA_TEST.mp4 was not found in the known Video Studio roots. Re-run with -SourceVideo and the exact original file path.'
}

function Invoke-ProbeJson([string]$Path) {
    $json = & $ffprobe -v error -show_streams -show_format -of json -- "$Path"
    if ($LASTEXITCODE -ne 0) { throw "ffprobe failed for $Path" }
    return ($json -join "`n") | ConvertFrom-Json
}

function Get-DurationSeconds($Probe) {
    $d = 0.0
    if ($Probe.format -and $Probe.format.duration) {
        [double]::TryParse([string]$Probe.format.duration, [Globalization.NumberStyles]::Float, [Globalization.CultureInfo]::InvariantCulture, [ref]$d) | Out-Null
    }
    return $d
}

function Get-VideoStream($Probe) {
    return @($Probe.streams | Where-Object { $_.codec_type -eq 'video' } | Select-Object -First 1)[0]
}

function Get-AudioStream($Probe) {
    $a = @($Probe.streams | Where-Object { $_.codec_type -eq 'audio' } | Select-Object -First 1)
    if ($a.Count -eq 0) { return $null }
    return $a[0]
}

function Encode-Clip {
    param(
        [string]$Input,
        [string]$Output,
        [double]$Start,
        [double]$Duration,
        [switch]$FullLength
    )

    $args = @('-hide_banner','-loglevel','error','-y')
    if (-not $FullLength) {
        $args += @('-ss', ('{0:F3}' -f $Start), '-t', ('{0:F3}' -f $Duration))
    }
    $args += @(
        '-i', $Input,
        '-map','0:v:0','-map','0:a:0',
        '-c:v','libx264','-preset','slow','-crf','14','-pix_fmt','yuv420p',
        '-c:a','aac','-b:a','192k','-movflags','+faststart',
        $Output
    )
    & $ffmpeg @args
    if ($LASTEXITCODE -ne 0) { throw "ffmpeg failed creating $Output" }
    if (-not (Test-Path -LiteralPath $Output -PathType Leaf)) { throw "Expected output not created: $Output" }
}

$Source = Find-SourceVideo -Explicit $SourceVideo
$Probe = Invoke-ProbeJson -Path $Source
$Duration = Get-DurationSeconds -Probe $Probe
$Video = Get-VideoStream -Probe $Probe
$Audio = Get-AudioStream -Probe $Probe

if ($null -eq $Video) { throw 'Source has no video stream.' }
if ($null -eq $Audio) { throw 'Source has no audio stream. Avatar V reference footage must contain speech audio.' }
if ($Duration -lt 15.0) { throw ("Source is only {0:F2}s; Avatar V behavioral reference requires at least about 15s." -f $Duration) }

New-Item -ItemType Directory -Force -Path $OutputRoot | Out-Null

$FullOut = Join-Path $OutputRoot 'joao_avatar_v_source_full_h264.mp4'
Encode-Clip -Input $Source -Output $FullOut -Start 0 -Duration $Duration -FullLength

$ClipLength = 15.0
$maxStart = [Math]::Max(0.0, $Duration - $ClipLength)
$startA = [Math]::Min(1.0, $maxStart)
$startB = [Math]::Max(0.0, [Math]::Min($maxStart, ($Duration - $ClipLength) / 2.0))
$startC = [Math]::Max(0.0, $maxStart - [Math]::Min(1.0, $maxStart))

$Starts = @($startA, $startB, $startC)
$Labels = @('A_early','B_middle','C_late')
$Clips = @()
for ($i = 0; $i -lt 3; $i++) {
    $out = Join-Path $OutputRoot ('joao_avatar_v_motion_' + $Labels[$i] + '_15s.mp4')
    Encode-Clip -Input $Source -Output $out -Start $Starts[$i] -Duration $ClipLength
    $hash = (Get-FileHash -LiteralPath $out -Algorithm SHA256).Hash
    $Clips += [ordered]@{
        label = $Labels[$i]
        start_seconds = [Math]::Round($Starts[$i], 3)
        duration_seconds = $ClipLength
        path = $out
        sha256 = $hash
    }
}

$SourceHash = (Get-FileHash -LiteralPath $Source -Algorithm SHA256).Hash
$FullHash = (Get-FileHash -LiteralPath $FullOut -Algorithm SHA256).Hash
$FullProbe = Invoke-ProbeJson -Path $FullOut
$FullVideo = Get-VideoStream -Probe $FullProbe
$FullAudio = Get-AudioStream -Probe $FullProbe

$Manifest = [ordered]@{
    schema = 'AVATAR-V-REFERENCE-PREPARE-01'
    created = (Get-Date -Format 'yyyy-MM-ddTHH:mm:ss')
    source = [ordered]@{
        path = $Source
        sha256 = $SourceHash
        duration_seconds = [Math]::Round($Duration, 3)
        width = [int]$Video.width
        height = [int]$Video.height
        video_codec = [string]$Video.codec_name
        audio_codec = [string]$Audio.codec_name
    }
    canonical_full_reference = [ordered]@{
        path = $FullOut
        sha256 = $FullHash
        duration_seconds = [Math]::Round((Get-DurationSeconds -Probe $FullProbe), 3)
        width = [int]$FullVideo.width
        height = [int]$FullVideo.height
        video_codec = [string]$FullVideo.codec_name
        audio_codec = [string]$FullAudio.codec_name
    }
    motion_candidates = $Clips
    selection_rule = 'Choose the 15-second candidate that most closely represents João normal speaking behavior. Do not choose merely the largest gestures or highest energy. Behavioral identity is the benchmark.'
    provider_target = 'HeyGen Avatar V / Digital Twin'
}

$ManifestPath = Join-Path $OutputRoot 'avatar_v_reference_manifest.json'
$Manifest | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $ManifestPath -Encoding UTF8

$ReportLines = @(
    'AVATAR V REFERENCE PREPARATION',
    '==============================',
    ('Source: ' + $Source),
    ('Source duration: {0:F3} s' -f $Duration),
    ('Source video: {0}x{1} / {2}' -f $Video.width, $Video.height, $Video.codec_name),
    ('Source audio: ' + $Audio.codec_name),
    '',
    'CANONICAL FULL REFERENCE',
    '========================',
    $FullOut,
    '',
    '15-SECOND MOTION CANDIDATES',
    '===========================',
    ('A: {0:F3}s -> {1:F3}s  {2}' -f $startA, ($startA + $ClipLength), $Clips[0].path),
    ('B: {0:F3}s -> {1:F3}s  {2}' -f $startB, ($startB + $ClipLength), $Clips[1].path),
    ('C: {0:F3}s -> {1:F3}s  {2}' -f $startC, ($startC + $ClipLength), $Clips[2].path),
    '',
    'SELECTION RULE',
    '==============',
    'Watch A/B/C and choose the clip that feels most like your normal delivery. Do not select the most theatrical or the one with the biggest gestures.',
    '',
    'MANIFEST',
    '========',
    $ManifestPath
)
Set-Content -LiteralPath $Report -Value $ReportLines -Encoding UTF8

Write-Host ''
Write-Host 'RESULT'
Write-Host '======'
Write-Host 'AVATAR V REFERENCE ASSETS PREPARED'
Write-Host ('Source: ' + $Source)
Write-Host ('Full reference: ' + $FullOut)
Write-Host ('Candidate A: ' + $Clips[0].path)
Write-Host ('Candidate B: ' + $Clips[1].path)
Write-Host ('Candidate C: ' + $Clips[2].path)
Write-Host ('Manifest: ' + $ManifestPath)
Write-Host ''
Write-Host 'REPORT'
Write-Host '======'
Write-Host $Report
