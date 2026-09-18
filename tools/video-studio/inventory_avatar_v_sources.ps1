param(
    [string]$SourceRoot = 'Z:\AI\VideoStudio\profiles\joao\behavior\avatar_v\sources',
    [string]$OutputRoot = 'Z:\AI\VideoStudio\profiles\joao\behavior\avatar_v\review'
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version 2.0

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$ReportDir = Join-Path $PSScriptRoot 'reports'
New-Item -ItemType Directory -Force -Path $ReportDir | Out-Null
$Stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$Report = Join-Path $ReportDir ('avatar_v_source_inventory_' + $Stamp + '.txt')

function Resolve-Executable([string]$Name) {
    $cmd = Get-Command $Name -ErrorAction SilentlyContinue
    if ($null -eq $cmd) { return $null }
    return $cmd.Source
}

$ffprobe = Resolve-Executable 'ffprobe.exe'
if (-not $ffprobe) { $ffprobe = Resolve-Executable 'ffprobe' }
$ffmpeg = Resolve-Executable 'ffmpeg.exe'
if (-not $ffmpeg) { $ffmpeg = Resolve-Executable 'ffmpeg' }
if (-not $ffprobe) { throw 'ffprobe not found in PATH.' }
if (-not $ffmpeg) { throw 'ffmpeg not found in PATH.' }

if (-not (Test-Path -LiteralPath $SourceRoot -PathType Container)) {
    throw "Source folder not found: $SourceRoot"
}

New-Item -ItemType Directory -Force -Path $OutputRoot | Out-Null
$ContactRoot = Join-Path $OutputRoot 'contact_sheets'
New-Item -ItemType Directory -Force -Path $ContactRoot | Out-Null

$Allowed = @('.mp4','.mov','.m4v','.mkv','.avi','.webm')
$Files = @(Get-ChildItem -LiteralPath $SourceRoot -File | Where-Object { $Allowed -contains $_.Extension.ToLowerInvariant() } | Sort-Object Name)
if ($Files.Count -eq 0) {
    throw "No supported video files found in: $SourceRoot"
}

function Invoke-ProbeJson([string]$Path) {
    $json = & $ffprobe -v error -show_streams -show_format -of json -- "$Path"
    if ($LASTEXITCODE -ne 0) { throw "ffprobe failed for $Path" }
    return ($json -join "`n") | ConvertFrom-Json
}

function Parse-Double([object]$Value) {
    $d = 0.0
    if ($null -eq $Value) { return $d }
    [double]::TryParse([string]$Value, [Globalization.NumberStyles]::Float, [Globalization.CultureInfo]::InvariantCulture, [ref]$d) | Out-Null
    return $d
}

function Parse-Fps([string]$Rate) {
    if ([string]::IsNullOrWhiteSpace($Rate)) { return 0.0 }
    if ($Rate -match '^([0-9.]+)\/([0-9.]+)$') {
        $num = Parse-Double $Matches[1]
        $den = Parse-Double $Matches[2]
        if ($den -ne 0) { return $num / $den }
    }
    return Parse-Double $Rate
}

function Safe-BaseName([string]$Name) {
    $s = [IO.Path]::GetFileNameWithoutExtension($Name)
    return ($s -replace '[^A-Za-z0-9._-]', '_')
}

function Make-ContactSheet {
    param(
        [string]$Input,
        [double]$Duration,
        [string]$Output
    )
    if ($Duration -le 0) { return $false }
    $sampleFps = 12.0 / $Duration
    if ($sampleFps -le 0) { return $false }
    $fpsText = $sampleFps.ToString('0.########', [Globalization.CultureInfo]::InvariantCulture)
    $filter = "fps=$fpsText,scale=320:-2,tile=4x3:padding=4:margin=4"
    & $ffmpeg -hide_banner -loglevel error -y -i "$Input" -vf $filter -frames:v 1 -q:v 2 "$Output"
    if ($LASTEXITCODE -ne 0) { return $false }
    return (Test-Path -LiteralPath $Output -PathType Leaf)
}

$Items = @()
foreach ($file in $Files) {
    Write-Host ('Inspecting: ' + $file.Name)
    $probe = Invoke-ProbeJson -Path $file.FullName
    $video = @($probe.streams | Where-Object { $_.codec_type -eq 'video' } | Select-Object -First 1)
    $audio = @($probe.streams | Where-Object { $_.codec_type -eq 'audio' } | Select-Object -First 1)
    if ($video.Count -eq 0) { continue }

    $v = $video[0]
    $a = $null
    if ($audio.Count -gt 0) { $a = $audio[0] }

    $duration = 0.0
    if ($probe.format -and $probe.format.duration) { $duration = Parse-Double $probe.format.duration }
    if ($duration -le 0 -and $v.duration) { $duration = Parse-Double $v.duration }

    $fps = 0.0
    if ($v.avg_frame_rate) { $fps = Parse-Fps ([string]$v.avg_frame_rate) }
    if ($fps -le 0 -and $v.r_frame_rate) { $fps = Parse-Fps ([string]$v.r_frame_rate) }

    $sizeBytes = [int64]$file.Length
    $hash = (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash
    $base = Safe-BaseName $file.Name
    $sheet = Join-Path $ContactRoot ($base + '_contact.jpg')
    $sheetOk = Make-ContactSheet -Input $file.FullName -Duration $duration -Output $sheet

    $hasAudio = $null -ne $a
    $motionReady = ($duration -ge 15.0 -and $hasAudio)
    $digitalTwinReady = ($duration -ge 120.0 -and $hasAudio)
    $minDim = [Math]::Min([int]$v.width, [int]$v.height)

    $Items += [ordered]@{
        file = $file.Name
        path = $file.FullName
        sha256 = $hash
        size_bytes = $sizeBytes
        size_mb = [Math]::Round($sizeBytes / 1MB, 2)
        duration_seconds = [Math]::Round($duration, 3)
        width = [int]$v.width
        height = [int]$v.height
        fps = [Math]::Round($fps, 3)
        video_codec = [string]$v.codec_name
        has_audio = $hasAudio
        audio_codec = $(if ($hasAudio) { [string]$a.codec_name } else { '' })
        audio_sample_rate = $(if ($hasAudio -and $a.sample_rate) { [int]$a.sample_rate } else { 0 })
        avatar_v_motion_reference_15s_candidate = $motionReady
        digital_twin_video_look_2min_candidate = $digitalTwinReady
        at_least_1080_short_dimension = ($minDim -ge 1080)
        contact_sheet = $(if ($sheetOk) { $sheet } else { '' })
    }
}

if ($Items.Count -eq 0) {
    throw 'No readable video streams were found in the source folder.'
}

$Manifest = [ordered]@{
    schema = 'AVATAR-V-SOURCE-INVENTORY-01'
    created = (Get-Date -Format 'yyyy-MM-ddTHH:mm:ss')
    source_root = $SourceRoot
    review_root = $OutputRoot
    provider_target = 'HeyGen Digital Twin / Avatar V'
    interpretation = [ordered]@{
        digital_twin_video_look = 'Current HeyGen guidance recommends at least 2 minutes of uninterrupted source footage for a high-quality Digital Twin / Video Look.'
        avatar_v_motion_reference = 'Current Avatar V guidance emphasizes about 15 seconds of representative motion reference.'
        rule = 'Do not trim or choose a source automatically. Inventory first, then assign source roles after technical and behavioral review.'
    }
    sources = $Items
}

$ManifestPath = Join-Path $OutputRoot 'avatar_v_source_inventory.json'
$Manifest | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $ManifestPath -Encoding UTF8

$Lines = @(
    'AVATAR V SOURCE INVENTORY',
    '=========================',
    ('Source root: ' + $SourceRoot),
    ('Files found: ' + $Items.Count),
    '',
    'INTERPRETATION',
    '==============',
    'DT>=2m : candidate for Digital Twin / Video Look source under current HeyGen guidance.',
    'AVV>=15s: candidate for Avatar V motion-reference material.',
    'No source is trimmed or selected by this script.',
    ''
)

foreach ($item in $Items) {
    $Lines += ('FILE: ' + $item.file)
    $Lines += ('  Duration: {0:F3} s' -f $item.duration_seconds)
    $Lines += ('  Resolution: {0}x{1}' -f $item.width, $item.height)
    $Lines += ('  FPS: {0:F3}' -f $item.fps)
    $Lines += ('  Video codec: ' + $item.video_codec)
    $Lines += ('  Audio: ' + $(if ($item.has_audio) { 'YES / ' + $item.audio_codec } else { 'NO' }))
    $Lines += ('  Size: {0:F2} MB' -f $item.size_mb)
    $Lines += ('  DT>=2m: ' + $(if ($item.digital_twin_video_look_2min_candidate) { 'YES' } else { 'NO' }))
    $Lines += ('  AVV>=15s: ' + $(if ($item.avatar_v_motion_reference_15s_candidate) { 'YES' } else { 'NO' }))
    $Lines += ('  1080 short dimension: ' + $(if ($item.at_least_1080_short_dimension) { 'YES' } else { 'NO' }))
    $Lines += ('  SHA256: ' + $item.sha256)
    $Lines += ('  Contact sheet: ' + $item.contact_sheet)
    $Lines += ''
}
$Lines += 'MANIFEST'
$Lines += '========'
$Lines += $ManifestPath
Set-Content -LiteralPath $Report -Value $Lines -Encoding UTF8

Write-Host ''
Write-Host 'RESULT'
Write-Host '======'
Write-Host ('VIDEO SOURCES INVENTORIED: ' + $Items.Count)
foreach ($item in $Items) {
    Write-Host ('- {0} | {1:F1}s | {2}x{3} | DT>=2m={4} | AVV>=15s={5}' -f $item.file, $item.duration_seconds, $item.width, $item.height, $item.digital_twin_video_look_2min_candidate, $item.avatar_v_motion_reference_15s_candidate)
}
Write-Host ('Manifest: ' + $ManifestPath)
Write-Host ('Contact sheets: ' + $ContactRoot)
Write-Host ''
Write-Host 'REPORT'
Write-Host '======'
Write-Host $Report
