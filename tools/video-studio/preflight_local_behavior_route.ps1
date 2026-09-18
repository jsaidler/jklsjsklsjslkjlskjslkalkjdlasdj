param(
    [string]$AiRoot = 'Z:\AI',
    [string]$WanRoot = 'Z:\AI\WanAnimate2',
    [string]$BehaviorRoot = 'Z:\AI\VideoStudio\profiles\joao\behavior\avatar_v',
    [switch]$VerifyLargeSha
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version 2.0

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$ReportDir = Join-Path $PSScriptRoot 'reports'
New-Item -ItemType Directory -Force -Path $ReportDir | Out-Null
$Stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$Report = Join-Path $ReportDir ('local_behavior_route_preflight_' + $Stamp + '.txt')

$Lines = New-Object System.Collections.Generic.List[string]
function Out-Line([string]$Text = '') {
    $Lines.Add($Text)
    Write-Host $Text
}

function File-Info([string]$Path) {
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { return $null }
    $f = Get-Item -LiteralPath $Path
    return [ordered]@{
        path = $f.FullName
        bytes = [int64]$f.Length
        gib = [Math]::Round($f.Length / 1GB, 3)
    }
}

function Find-FirstFile {
    param(
        [string]$Root,
        [string[]]$Names
    )
    if (-not (Test-Path -LiteralPath $Root -PathType Container)) { return $null }
    foreach ($name in $Names) {
        $hit = Get-ChildItem -LiteralPath $Root -File -Recurse -ErrorAction SilentlyContinue |
            Where-Object { $_.Name -ieq $name } |
            Select-Object -First 1
        if ($null -ne $hit) { return $hit.FullName }
    }
    return $null
}

function Find-FirstDirByName {
    param(
        [string]$Root,
        [string[]]$Names
    )
    if (-not (Test-Path -LiteralPath $Root -PathType Container)) { return $null }
    foreach ($name in $Names) {
        $hit = Get-ChildItem -LiteralPath $Root -Directory -Recurse -ErrorAction SilentlyContinue |
            Where-Object { $_.Name -ieq $name } |
            Select-Object -First 1
        if ($null -ne $hit) { return $hit.FullName }
    }
    return $null
}

function Probe-Video([string]$Path, [string]$Ffprobe) {
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { return $null }
    $json = & $Ffprobe -v error -show_streams -show_format -of json -- "$Path"
    if ($LASTEXITCODE -ne 0) { return $null }
    $p = (($json -join "`n") | ConvertFrom-Json)
    $v = @($p.streams | Where-Object { $_.codec_type -eq 'video' } | Select-Object -First 1)
    $a = @($p.streams | Where-Object { $_.codec_type -eq 'audio' } | Select-Object -First 1)
    $duration = 0.0
    if ($p.format -and $p.format.duration) {
        [double]::TryParse([string]$p.format.duration, [Globalization.NumberStyles]::Float, [Globalization.CultureInfo]::InvariantCulture, [ref]$duration) | Out-Null
    }
    return [ordered]@{
        duration = [Math]::Round($duration, 3)
        width = $(if ($v.Count -gt 0) { [int]$v[0].width } else { 0 })
        height = $(if ($v.Count -gt 0) { [int]$v[0].height } else { 0 })
        video_codec = $(if ($v.Count -gt 0) { [string]$v[0].codec_name } else { '' })
        has_audio = ($a.Count -gt 0)
        audio_codec = $(if ($a.Count -gt 0) { [string]$a[0].codec_name } else { '' })
    }
}

Out-Line 'LOCAL BEHAVIOR ROUTE PREFLIGHT'
Out-Line '=============================='
Out-Line ('Timestamp: ' + (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'))
Out-Line ('Repo: ' + $RepoRoot)
Out-Line ('AI root: ' + $AiRoot)
Out-Line ('Wan root: ' + $WanRoot)
Out-Line 'Mode: NO DOWNLOAD / NO INSTALL / NO MODEL MUTATION'
Out-Line ''

# Basic executables
$ffmpegCmd = Get-Command ffmpeg.exe -ErrorAction SilentlyContinue
if ($null -eq $ffmpegCmd) { $ffmpegCmd = Get-Command ffmpeg -ErrorAction SilentlyContinue }
$ffprobeCmd = Get-Command ffprobe.exe -ErrorAction SilentlyContinue
if ($null -eq $ffprobeCmd) { $ffprobeCmd = Get-Command ffprobe -ErrorAction SilentlyContinue }
$nvidiaCmd = Get-Command nvidia-smi.exe -ErrorAction SilentlyContinue
if ($null -eq $nvidiaCmd) { $nvidiaCmd = Get-Command nvidia-smi -ErrorAction SilentlyContinue }
$pyCmd = Get-Command py.exe -ErrorAction SilentlyContinue
if ($null -eq $pyCmd) { $pyCmd = Get-Command py -ErrorAction SilentlyContinue }

Out-Line 'SYSTEM'
Out-Line '======'
Out-Line ('ffmpeg: ' + $(if ($ffmpegCmd) { $ffmpegCmd.Source } else { 'MISSING' }))
Out-Line ('ffprobe: ' + $(if ($ffprobeCmd) { $ffprobeCmd.Source } else { 'MISSING' }))
Out-Line ('nvidia-smi: ' + $(if ($nvidiaCmd) { $nvidiaCmd.Source } else { 'MISSING' }))

if ($pyCmd) {
    $py311 = & $pyCmd.Source -3.11 -c "import sys; print(sys.executable); print(sys.version.split()[0])" 2>$null
    if ($LASTEXITCODE -eq 0 -and $py311) {
        Out-Line ('Python 3.11: PASS / ' + (($py311 | ForEach-Object { [string]$_ }) -join ' / '))
    } else {
        Out-Line 'Python 3.11: NOT RESOLVED THROUGH py launcher'
    }
} else {
    Out-Line 'Python launcher: MISSING'
}

if ($nvidiaCmd) {
    try {
        $gpu = & $nvidiaCmd.Source --query-gpu=name,driver_version,memory.total,memory.free --format=csv,noheader,nounits 2>$null
        if ($LASTEXITCODE -eq 0 -and $gpu) { Out-Line ('GPU: ' + (($gpu | Select-Object -First 1).Trim())) }
    } catch {
        Out-Line ('GPU query failed: ' + $_.Exception.Message)
    }
}

try {
    $drive = Get-PSDrive -Name Z -ErrorAction Stop
    Out-Line ('Z: free: {0:N2} GB' -f ($drive.Free / 1GB))
    Out-Line ('Z: used: {0:N2} GB' -f ($drive.Used / 1GB))
} catch {
    Out-Line 'Z: drive status unavailable'
}
Out-Line ''

# Behavioral source library
Out-Line 'BEHAVIORAL SOURCE LIBRARY'
Out-Line '========================='
$SourceRoot = Join-Path $BehaviorRoot 'sources'
$ExpectedSources = @(
    'SIENA_BRUTO.mp4',
    'VID_20260819_124008056.mp4',
    'VID_20260911_140124885.mp4'
)
$sourcePass = $true
foreach ($name in $ExpectedSources) {
    $path = Join-Path $SourceRoot $name
    if (Test-Path -LiteralPath $path -PathType Leaf) {
        $f = Get-Item -LiteralPath $path
        if ($ffprobeCmd) {
            $p = Probe-Video -Path $path -Ffprobe $ffprobeCmd.Source
            if ($p) {
                Out-Line ('PASS  {0} | {1:N1}s | {2}x{3} | {4} | audio={5}' -f $name, $p.duration, $p.width, $p.height, $p.video_codec, $p.has_audio)
            } else {
                Out-Line ('WARN  {0} | exists ({1:N2} GB) but probe failed' -f $name, ($f.Length / 1GB))
            }
        } else {
            Out-Line ('PASS  {0} | exists ({1:N2} GB)' -f $name, ($f.Length / 1GB))
        }
    } else {
        Out-Line ('FAIL  ' + $name + ' | missing')
        $sourcePass = $false
    }
}
$PreparedLocal = Join-Path $BehaviorRoot 'prepared\joao_heygen_digital_twin_primary_1080p_h264.mp4'
if (Test-Path -LiteralPath $PreparedLocal -PathType Leaf) {
    $f = Get-Item -LiteralPath $PreparedLocal
    Out-Line ('PASS  generic 1080p local derivative | {0:N2} GB | historical filename only' -f ($f.Length / 1GB))
} else {
    Out-Line 'INFO  generic 1080p derivative not found; originals remain canonical'
}
Out-Line ''

# Installed Wan-Animate-2 payload
Out-Line 'WAN-ANIMATE-2 REUSE AUDIT'
Out-Line '========================='
$AnimateModel = Join-Path $WanRoot 'models\diffusion_models\wan_animate_2_bf16.safetensors'
$AnimateInfo = File-Info $AnimateModel
if ($AnimateInfo) {
    Out-Line ('PASS  Animate-2 transformer: {0} ({1:N3} GiB)' -f $AnimateInfo.path, $AnimateInfo.gib)
    if ($VerifyLargeSha) {
        Out-Line 'Hashing ~30.5 GiB Animate-2 transformer...'
        $sha = (Get-FileHash -LiteralPath $AnimateModel -Algorithm SHA256).Hash.ToLowerInvariant()
        $expected = '48abc389b8d9bba17a7f54a1cd7f1286fd3e3e0e292ddf756721aee324aede09'
        Out-Line ('SHA256: ' + $sha)
        Out-Line ('Official match: ' + ($sha -eq $expected))
    } else {
        Out-Line 'SHA256: SKIPPED (use -VerifyLargeSha only if integrity verification is needed)'
    }
} else {
    Out-Line ('FAIL  Animate-2 transformer missing at canonical path: ' + $AnimateModel)
}

$TextEncoderCandidates = @(
    (Join-Path $WanRoot 'models\text_encoders\umt5_xxl_fp16.safetensors'),
    (Join-Path $WanRoot 'models\text_encoders\umt5_xxl_fp8_e4m3fn_scaled.safetensors')
)
$foundTE = $false
foreach ($p in $TextEncoderCandidates) {
    $info = File-Info $p
    if ($info) {
        Out-Line ('PASS  text encoder: {0} ({1:N3} GiB)' -f $info.path, $info.gib)
        $foundTE = $true
    }
}
if (-not $foundTE) { Out-Line 'WARN  no expected UMT5 text encoder found at canonical Wan paths' }

$VaeCandidates = @(
    (Join-Path $WanRoot 'models\vae\Wan2_1_VAE_bf16.safetensors'),
    (Join-Path $WanRoot 'models\vae\wan_2.1_vae.safetensors')
)
$foundVae = $false
foreach ($p in $VaeCandidates) {
    $info = File-Info $p
    if ($info) {
        Out-Line ('PASS  VAE: {0} ({1:N3} GiB)' -f $info.path, $info.gib)
        $foundVae = $true
    }
}
if (-not $foundVae) { Out-Line 'WARN  no expected Wan VAE found at canonical Wan paths' }

$NativeAnimateNode = Find-FirstFile -Root $WanRoot -Names @('model_animate2.py')
if ($NativeAnimateNode) {
    Out-Line ('PASS  native Animate-2 model code: ' + $NativeAnimateNode)
} else {
    Out-Line 'WARN  model_animate2.py not found under Wan root; ComfyUI may predate native Animate-2 support'
}

$ControlAuxDir = Find-FirstDirByName -Root $WanRoot -Names @('comfyui_controlnet_aux','ComfyUI-ControlNet-Aux')
if ($ControlAuxDir) {
    Out-Line ('PASS  controlnet auxiliary nodes present: ' + $ControlAuxDir)
} else {
    Out-Line 'INFO  comfyui_controlnet_aux not found under Wan root'
}
$KJDir = Find-FirstDirByName -Root $WanRoot -Names @('ComfyUI-KJNodes','comfyui-kjnodes')
if ($KJDir) {
    Out-Line ('PASS  KJNodes present: ' + $KJDir)
} else {
    Out-Line 'INFO  KJNodes not found under Wan root'
}
Out-Line ''

# Pose tooling scan: only the active Wan root, avoiding an expensive full Z: crawl.
Out-Line 'POSE / BEHAVIOR TOOLING'
Out-Line '======================='
$DWPose = Find-FirstFile -Root $WanRoot -Names @('dw-ll_ucoco_384.onnx','dw-ll_ucoco_384_bs5.torchscript.pt','dwpose-l.onnx')
if ($DWPose) {
    Out-Line ('REUSE DWPose-like model found: ' + $DWPose)
} else {
    Out-Line 'MISSING-SMALL-COMPONENT: no DWPose whole-body model found under Wan root'
    Out-Line 'If needed later, DWPose-L is ~350 MB; DO NOT DOWNLOAD IT FROM THIS PREFLIGHT.'
}

$MotionMirrorRoots = @(
    (Join-Path $AiRoot 'MotionMirror'),
    (Join-Path $AiRoot 'motion-mirror')
)
$mmFound = $false
foreach ($r in $MotionMirrorRoots) {
    if (Test-Path -LiteralPath $r -PathType Container) {
        Out-Line ('INFO  Motion Mirror checkout already exists: ' + $r)
        $mmFound = $true
    }
}
if (-not $mmFound) { Out-Line 'INFO  Motion Mirror not installed. This is expected; it is a fallback, not the next download.' }

foreach ($name in @('MuseTalk','LatentSync')) {
    $p = Join-Path $AiRoot $name
    if (Test-Path -LiteralPath $p -PathType Container) {
        Out-Line ('INFO  ' + $name + ' already exists: ' + $p)
    } else {
        Out-Line ('INFO  ' + $name + ' not installed; lip-sync stage remains deferred')
    }
}
Out-Line ''

# Retired payload awareness - report only, never delete.
Out-Line 'RETIRED / RECLAIMABLE PAYLOAD AWARENESS'
Out-Line '========================================'
$WanGp = Join-Path $AiRoot 'WanGP'
if (Test-Path -LiteralPath $WanGp -PathType Container) {
    $HunyuanCandidates = @(
        (Join-Path $WanGp 'models\hunyuan_video_avatar_720_quanto_bf16_int8.safetensors'),
        (Join-Path $WanGp 'ckpts\hunyuan_video_avatar_720_quanto_bf16_int8.safetensors')
    )
    $hFound = $false
    foreach ($p in $HunyuanCandidates) {
        $info = File-Info $p
        if ($info) {
            Out-Line ('INFO  retired Hunyuan transformer still present: {0} ({1:N3} GiB)' -f $info.path, $info.gib)
            $hFound = $true
        }
    }
    if (-not $hFound) { Out-Line 'INFO  no Hunyuan transformer found at the two canonical candidate paths' }
} else {
    Out-Line 'INFO  WanGP root not present'
}
Out-Line 'No files are deleted by this preflight.'
Out-Line ''

$animatePass = ($null -ne $AnimateInfo -and $null -ne $NativeAnimateNode)
Out-Line 'RESULT'
Out-Line '======'
Out-Line ('BEHAVIOR SOURCES: ' + $(if ($sourcePass) { 'PASS' } else { 'FAIL' }))
Out-Line ('WAN-ANIMATE-2 PAYLOAD: ' + $(if ($AnimateInfo) { 'PASS' } else { 'FAIL' }))
Out-Line ('WAN-ANIMATE-2 NATIVE CODE: ' + $(if ($NativeAnimateNode) { 'PASS' } else { 'MISSING/STALE' }))
Out-Line ('POSE TOOLING: ' + $(if ($DWPose) { 'REUSE AVAILABLE' } else { 'NOT FOUND UNDER WAN ROOT' }))
Out-Line ('NEXT ROUTE GATE: ' + $(if ($animatePass -and $sourcePass) { 'BUILD BEHAVIOR PROFILE WITHOUT NEW LARGE RENDERER DOWNLOAD' } else { 'FIX LOCAL RUNTIME/PAYLOAD BEFORE ANY LARGE DOWNLOAD' }))
Out-Line ('Report: ' + $Report)

Set-Content -LiteralPath $Report -Value $Lines -Encoding UTF8
