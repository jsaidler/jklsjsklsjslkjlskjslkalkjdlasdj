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
$FfmpegCmd = Get-Command ffmpeg.exe -ErrorAction SilentlyContinue
if ($null -eq $FfmpegCmd) { $FfmpegCmd = Get-Command ffmpeg -ErrorAction SilentlyContinue }

Out-Line 'WANGP DWPOSE RUNTIME PROBE'
Out-Line '==========================='
Out-Line ('Timestamp: ' + (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'))
Out-Line 'Mode: LOCAL REUSE / NO DOWNLOAD / NO INSTALL / NO MODEL MUTATION'
Out-Line ('WanGP root: ' + $WanGpRoot)
Out-Line ('Python: ' + $Python)
Out-Line ('Detector: ' + $Det)
Out-Line ('Pose: ' + $Pose)
Out-Line ('Source: ' + $Source)
Out-Line ''

foreach ($item in @(
    @{ Name='WanGP Python'; Path=$Python },
    @{ Name='DWPose code'; Path=$DwCode },
    @{ Name='YOLOX detector'; Path=$Det },
    @{ Name='DWPose whole-body'; Path=$Pose },
    @{ Name='Primary source'; Path=$Source }
)) {
    if (Test-Path -LiteralPath $item.Path -PathType Leaf) {
        $f = Get-Item -LiteralPath $item.Path
        Out-Line ('PASS  {0}: {1} ({2:N1} MB)' -f $item.Name, $f.FullName, ($f.Length / 1MB))
    } else {
        Out-Line ('FAIL  {0}: {1}' -f $item.Name, $item.Path)
        throw ('Required local component missing: ' + $item.Name)
    }
}
if ($null -eq $FfmpegCmd) { throw 'ffmpeg not found in PATH.' }
Out-Line ('PASS  ffmpeg: ' + $FfmpegCmd.Source)
Out-Line ''

$TempFrame = Join-Path $env:TEMP ("video_studio_dwpose_probe_$Stamp.png")
try {
    & $FfmpegCmd.Source -hide_banner -loglevel error -ss $ProbeSecond -i $Source -frames:v 1 -vf 'scale=960:-2' -y $TempFrame
    if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath $TempFrame -PathType Leaf)) {
        throw 'ffmpeg could not extract the DWPose probe frame.'
    }

    $Code = @'
import json, sys
from pathlib import Path
root, det_path, pose_path, frame_path = map(Path, sys.argv[1:5])
sys.path.insert(0, str(root))
result = {
    "python": sys.version.split()[0],
    "executable": sys.executable,
    "imports_ok": False,
    "providers": [],
    "session_provider": None,
    "detected_boxes": 0,
    "keypoint_count": 0,
    "mean_keypoint_score": None,
    "error": None,
}
try:
    import cv2
    import numpy as np
    import onnxruntime as ort
    from preprocessing.dwpose.onnxdet import inference_detector
    from preprocessing.dwpose.onnxpose import inference_pose
    result["imports_ok"] = True
    result["opencv"] = cv2.__version__
    result["numpy"] = np.__version__
    result["onnxruntime"] = ort.__version__
    result["providers"] = ort.get_available_providers()

    candidates = []
    if "CUDAExecutionProvider" in result["providers"]:
        candidates.append("CUDAExecutionProvider")
    candidates.append("CPUExecutionProvider")

    det_sess = pose_sess = None
    errors = []
    for provider in candidates:
        try:
            det_sess = ort.InferenceSession(str(det_path), providers=[provider])
            pose_sess = ort.InferenceSession(str(pose_path), providers=[provider])
            result["session_provider"] = provider
            break
        except Exception as exc:
            errors.append(f"{provider}: {exc}")
    if det_sess is None or pose_sess is None:
        raise RuntimeError("; ".join(errors))

    img = cv2.imread(str(frame_path), cv2.IMREAD_COLOR)
    if img is None:
        raise RuntimeError("cv2.imread failed for probe frame")
    boxes = inference_detector(det_sess, img)
    result["detected_boxes"] = int(len(boxes))
    if len(boxes):
        areas = (boxes[:,2]-boxes[:,0]) * (boxes[:,3]-boxes[:,1])
        box = boxes[int(np.argmax(areas))]
        pose_boxes = np.asarray([box], dtype=np.float32)
    else:
        pose_boxes = np.empty((0,4), dtype=np.float32)
    keypoints, scores = inference_pose(pose_sess, pose_boxes, img)
    if len(keypoints):
        result["keypoint_count"] = int(keypoints.shape[1])
        result["mean_keypoint_score"] = float(np.mean(scores[0]))
except Exception as exc:
    result["error"] = repr(exc)
print(json.dumps(result, ensure_ascii=False))
'@

    $Saved = $ErrorActionPreference
    try {
        $ErrorActionPreference = 'Continue'
        $Raw = & $Python -c $Code $WanGpRoot $Det $Pose $TempFrame 2>&1
        $Exit = $LASTEXITCODE
    } finally {
        $ErrorActionPreference = $Saved
    }

    foreach ($line in @($Raw)) { Out-Line ([string]$line) }
    Out-Line ('Python exit: ' + $Exit)
    if ($Exit -ne 0) { throw 'WanGP Python DWPose probe failed.' }

    $JsonLine = @($Raw | Where-Object { ([string]$_).Trim().StartsWith('{') }) | Select-Object -Last 1
    if (-not $JsonLine) { throw 'DWPose probe did not emit JSON result.' }
    $Result = ([string]$JsonLine) | ConvertFrom-Json

    Out-Line ''
    Out-Line ('Resolved Python: {0} / {1}' -f $Result.executable, $Result.python)
    Out-Line ('ONNX providers: ' + (($Result.providers | ForEach-Object { [string]$_ }) -join ', '))
    Out-Line ('Session provider: ' + $Result.session_provider)
    Out-Line ('Detected boxes: ' + $Result.detected_boxes)
    Out-Line ('Keypoints: ' + $Result.keypoint_count)
    Out-Line ('Mean keypoint score: ' + $Result.mean_keypoint_score)
    if ($Result.error) { throw ('DWPose runtime error: ' + $Result.error) }
    if (-not $Result.imports_ok -or [int]$Result.keypoint_count -lt 133) {
        throw 'DWPose runtime did not produce a valid COCO WholeBody pose result.'
    }
    Out-Line 'DWPose runtime: PASS'
}
finally {
    if (Test-Path -LiteralPath $TempFrame) { Remove-Item -LiteralPath $TempFrame -Force -ErrorAction SilentlyContinue }
    Set-Content -LiteralPath $Report -Value $Lines -Encoding UTF8
    Write-Host ('Report: ' + $Report)
}
