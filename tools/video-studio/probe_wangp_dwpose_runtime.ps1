param(
    [string]$WanGpRoot = 'Z:\AI\WanGP',
    [string]$Source = 'Z:\AI\VideoStudio\profiles\joao\behavior\avatar_v\sources\VID_20260911_140124885.mp4',
    [double]$ProbeSecond = 30.0
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version 2.0

$ReportDir = Join-Path $PSScriptRoot 'reports'
New-Item -ItemType Directory -Force -Path $ReportDir | Out-Null
$Stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$Report = Join-Path $ReportDir ("wangp_dwpose_runtime_$Stamp.txt")
$Lines = New-Object System.Collections.Generic.List[string]
function Out-Line([string]$Text = '') { $Lines.Add($Text) | Out-Null; Write-Host $Text }

$Python = Join-Path $WanGpRoot 'env_uv\Scripts\python.exe'
$DwCode = Join-Path $WanGpRoot 'preprocessing\dwpose\wholebody.py'
$Det = Join-Path $WanGpRoot 'ckpts\pose\yolox_l.onnx'
$Pose = Join-Path $WanGpRoot 'ckpts\pose\dw-ll_ucoco_384.onnx'
$Runner = Join-Path $PSScriptRoot 'extract_dwpose_track.py'
$TempOut = Join-Path $env:TEMP ("video_studio_dwpose_probe_$Stamp.jsonl")
$TempSummary = $TempOut + '.summary.json'

Out-Line 'WANGP DWPOSE RUNTIME PROBE'
Out-Line '==========================='
Out-Line ('Timestamp: ' + (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'))
Out-Line 'Mode: LOCAL REUSE / NO DOWNLOAD / NO INSTALL / NO MODEL MUTATION'
Out-Line ('WanGP root: ' + $WanGpRoot)
Out-Line ('Python: ' + $Python)
Out-Line ('Detector: ' + $Det)
Out-Line ('Pose: ' + $Pose)
Out-Line ('Source: ' + $Source)
Out-Line ('Probe runner: ' + $Runner)
Out-Line ''

foreach ($item in @(
    @{ Name='WanGP Python'; Path=$Python },
    @{ Name='DWPose code'; Path=$DwCode },
    @{ Name='YOLOX detector'; Path=$Det },
    @{ Name='DWPose whole-body'; Path=$Pose },
    @{ Name='Primary source'; Path=$Source },
    @{ Name='Pose extractor'; Path=$Runner }
)) {
    if (Test-Path -LiteralPath $item.Path -PathType Leaf) {
        $f = Get-Item -LiteralPath $item.Path
        Out-Line ('PASS  {0}: {1} ({2:N1} MB)' -f $item.Name, $f.FullName, ($f.Length / 1MB))
    } else {
        Out-Line ('FAIL  {0}: {1}' -f $item.Name, $item.Path)
        throw ('Required local component missing: ' + $item.Name)
    }
}
Out-Line ''

try {
    $PythonVersion = (& $Python --version 2>&1 | Select-Object -Last 1)
    if ($LASTEXITCODE -ne 0) { throw 'WanGP Python --version failed.' }
    Out-Line ('Resolved Python: ' + $Python + ' / ' + [string]$PythonVersion)

    $ProbeSecondText = $ProbeSecond.ToString([System.Globalization.CultureInfo]::InvariantCulture)
    $Args = @(
        $Runner,
        '--source', $Source,
        '--wangp-root', $WanGpRoot,
        '--det-model', $Det,
        '--pose-model', $Pose,
        '--output', $TempOut,
        '--start', $ProbeSecondText,
        '--fps', '6',
        '--long-side', '960',
        '--provider', 'auto',
        '--max-frames', '1'
    )

    $Saved = $ErrorActionPreference
    try {
        $ErrorActionPreference = 'Continue'
        $Raw = & $Python @Args 2>&1
        $Exit = $LASTEXITCODE
    } finally {
        $ErrorActionPreference = $Saved
    }

    foreach ($line in @($Raw)) { Out-Line ([string]$line) }
    Out-Line ('Python exit: ' + $Exit)
    if ($Exit -ne 0) { throw 'WanGP Python DWPose probe failed.' }
    if (-not (Test-Path -LiteralPath $TempSummary -PathType Leaf)) {
        throw 'DWPose probe did not produce its summary JSON.'
    }

    $Result = Get-Content -LiteralPath $TempSummary -Raw -Encoding UTF8 | ConvertFrom-Json
    Out-Line ''
    Out-Line ('ONNX providers: ' + (($Result.available_onnx_providers | ForEach-Object { [string]$_ }) -join ', '))
    Out-Line ('Session provider: ' + $Result.onnx_provider)
    Out-Line ('Frames: ' + $Result.frames)
    Out-Line ('Schema: ' + $Result.schema)
    Out-Line ('Mean keypoint score: ' + $Result.mean_keypoint_score)
    Out-Line ('Detector fallback frames: ' + $Result.detector_fallback_frames)

    if ([int]$Result.frames -lt 1) { throw 'DWPose runtime produced no pose frames.' }
    if ([string]$Result.schema -ne 'coco_wholebody_133') { throw 'DWPose runtime returned an unexpected pose schema.' }
    if ([string]::IsNullOrWhiteSpace([string]$Result.onnx_provider)) { throw 'DWPose runtime did not select an ONNX provider.' }

    Out-Line 'DWPose runtime: PASS'
}
finally {
    if (Test-Path -LiteralPath $TempOut) { Remove-Item -LiteralPath $TempOut -Force -ErrorAction SilentlyContinue }
    if (Test-Path -LiteralPath $TempSummary) { Remove-Item -LiteralPath $TempSummary -Force -ErrorAction SilentlyContinue }
    Set-Content -LiteralPath $Report -Value $Lines -Encoding UTF8
    Write-Host ('Report: ' + $Report)
}
