param(
    [switch]$Download,
    [string]$WanRoot = "Z:\AI\WanAnimate2",
    [string]$H3Input = "Z:\AI\MiniMaxH3\ComfyUI_windows_portable\ComfyUI\input",
    [double]$AudioSeconds = 4.5
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version 2.0

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\.." )).Path
$ReportDir = Join-Path $RepoRoot "tools\video-studio\reports"
New-Item -ItemType Directory -Force -Path $ReportDir | Out-Null

$Stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$Report = Join-Path $ReportDir "wan_s2v_prepare_$Stamp.txt"
$Lines = New-Object 'System.Collections.Generic.List[string]'

function Log([string]$Text = "") {
    Write-Host $Text
    $Lines.Add($Text) | Out-Null
}

function Section([string]$Title) {
    Log ""
    Log $Title
    Log ("=" * $Title.Length)
}

function Require-File([string]$Path, [string]$Label) {
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        throw "$Label not found: $Path"
    }
}

function Test-TokenInFiles([string]$Root, [string]$Token) {
    if (-not (Test-Path -LiteralPath $Root)) {
        return $false
    }
    $matches = Get-ChildItem -LiteralPath $Root -Recurse -File -ErrorAction SilentlyContinue |
        Where-Object { $_.Extension -in '.py','.json' } |
        Select-String -SimpleMatch -Pattern $Token -List -ErrorAction SilentlyContinue
    return @($matches).Count -gt 0
}

function Verify-Sha256([string]$Path, [string]$Expected) {
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return $false
    }
    $Actual = (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
    return $Actual -eq $Expected.ToLowerInvariant()
}

function Download-Verified(
    [string]$Url,
    [string]$Destination,
    [string]$Sha256,
    [string]$Label
) {
    if (Test-Path -LiteralPath $Destination -PathType Leaf) {
        if (Verify-Sha256 $Destination $Sha256) {
            Log "$Label already present and SHA256 verified."
            return
        }
        throw "$Label exists but SHA256 does not match: $Destination"
    }

    $Dir = Split-Path -Parent $Destination
    New-Item -ItemType Directory -Force -Path $Dir | Out-Null
    $Partial = "$Destination.partial"

    Log "Downloading $Label"
    Log "  URL: $Url"
    Log "  DST: $Destination"

    & curl.exe -L --fail --retry 5 --retry-delay 5 -C - -o $Partial $Url
    if ($LASTEXITCODE -ne 0) {
        throw "curl failed downloading $Label with exit code $LASTEXITCODE"
    }

    if (-not (Verify-Sha256 $Partial $Sha256)) {
        $Actual = (Get-FileHash -LiteralPath $Partial -Algorithm SHA256).Hash
        throw "$Label SHA256 mismatch. Expected $Sha256, got $Actual"
    }

    Move-Item -LiteralPath $Partial -Destination $Destination -Force
    Log "$Label downloaded and verified."
}

Log "WAN-S2V-PREPARE-01"
Log ("Status date: " + (Get-Date -Format "yyyy-MM-dd HH:mm:ss"))
Log "Repo root: $RepoRoot"
Log "Wan root: $WanRoot"
Log "Download enabled: $Download"

if (-not (Test-Path -LiteralPath $WanRoot -PathType Container)) {
    throw "Wan root not found: $WanRoot"
}

$ModelsRoot = Join-Path $WanRoot "models"
$DiffusionDir = Join-Path $ModelsRoot "diffusion_models"
$TextDir = Join-Path $ModelsRoot "text_encoders"
$VaeDir = Join-Path $ModelsRoot "vae"
$AudioEncoderDir = Join-Path $ModelsRoot "audio_encoders"
$InputDir = Join-Path $WanRoot "input"

$ExistingText = Join-Path $TextDir "umt5_xxl_fp16.safetensors"
$ExistingVae = Join-Path $VaeDir "Wan2_1_VAE_bf16.safetensors"
$S2VModel = Join-Path $DiffusionDir "wan2.2_s2v_14B_fp8_scaled.safetensors"
$AudioEncoder = Join-Path $AudioEncoderDir "wav2vec2_large_english_fp16.safetensors"

$S2VUrl = "https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/diffusion_models/wan2.2_s2v_14B_fp8_scaled.safetensors?download=true"
$S2VSha = "140e75af5534ac3d91e710d9df756f7032addd64b341ba2c1c70e3e6da9aa216"
$AudioEncoderUrl = "https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/audio_encoders/wav2vec2_large_english_fp16.safetensors?download=true"
$AudioEncoderSha = "f0017a43ea57ef6b3d4866be607844bbd8cada6d30966f7d70044ed0d63d3f9e"

Section "RUNTIME SUPPORT"
$ObjectInfoCandidates = @(
    (Join-Path $WanRoot "object_info_wan_bf16.json"),
    (Join-Path $WanRoot "object_info_w0_live.json")
) | Where-Object { Test-Path -LiteralPath $_ -PathType Leaf }

$RequiredTokens = @(
    "WanSoundImageToVideo",
    "AudioEncoderLoader",
    "AudioEncoderEncode"
)

$RuntimeSupportOk = $true
foreach ($Token in $RequiredTokens) {
    $Found = $false
    foreach ($Info in $ObjectInfoCandidates) {
        $Raw = Get-Content -LiteralPath $Info -Raw -Encoding UTF8
        if ($Raw.Contains($Token)) {
            $Found = $true
            break
        }
    }
    if (-not $Found) {
        $Found = Test-TokenInFiles $WanRoot $Token
    }
    Log ("{0}: {1}" -f $Token, $(if ($Found) { "FOUND" } else { "NOT FOUND" }))
    if (-not $Found) {
        $RuntimeSupportOk = $false
    }
}

if (-not $RuntimeSupportOk) {
    throw "Current Wan runtime does not expose all native S2V nodes. Stop before downloading models."
}

Section "REUSE CHECK"
Require-File $ExistingText "Existing UMT5 FP16"
Require-File $ExistingVae "Existing Wan VAE BF16"
Log "Reuse text encoder: $ExistingText"
Log "Reuse VAE: $ExistingVae"

Section "DISK SPACE"
$DriveName = ([System.IO.Path]::GetPathRoot($WanRoot)).Substring(0,1)
$Drive = Get-PSDrive -Name $DriveName -ErrorAction Stop
$FreeGb = [math]::Round($Drive.Free / 1GB, 2)
Log "Free space on $DriveName`: $FreeGb GB"
if ($Download -and $FreeGb -lt 22) {
    throw "Less than 22 GB free on $DriveName`: refusing the ~17 GB model download."
}

Section "MODEL REQUIREMENTS"
Log "S2V FP8: 16.4 GB -> $S2VModel"
Log "Audio encoder: 631 MB -> $AudioEncoder"
Log "Text encoder: REUSE existing UMT5 FP16"
Log "VAE: REUSE existing Wan2.1 VAE BF16"
Log "CosyVoice: DEFERRED until renderer visual-quality pass"

if ($Download) {
    Section "DOWNLOAD"
    Download-Verified $S2VUrl $S2VModel $S2VSha "Wan2.2 S2V 14B FP8 scaled"
    Download-Verified $AudioEncoderUrl $AudioEncoder $AudioEncoderSha "wav2vec2 large English FP16"
} else {
    Section "DOWNLOAD SKIPPED"
    Log "Run again with -Download after reviewing this preflight."
}

Section "BENCHMARK ASSETS"
$SourceImage = Join-Path $H3Input "joao_id_upperbody.png"
$SourceAudio = Join-Path $H3Input "joao_ref_voice.wav"
Require-File $SourceImage "Joao upper-body reference"
Require-File $SourceAudio "Joao voice reference"

$AssetDir = Join-Path $InputDir "video_studio\wan_s2v_benchmark"
New-Item -ItemType Directory -Force -Path $AssetDir | Out-Null

$TargetImage = Join-Path $AssetDir "joao_wan_s2v_ref.png"
$TargetAudio = Join-Path $AssetDir "joao_wan_s2v_test_4p5s.wav"

Copy-Item -LiteralPath $SourceImage -Destination $TargetImage -Force

# Windows PowerShell 5.1 can promote redirected native stderr to NativeCommandError
# when ErrorActionPreference is Stop. Keep ffmpeg stderr native, suppress normal
# banner/progress output with loglevel, and trust the native process exit code.
& ffmpeg.exe -hide_banner -loglevel error -y -i $SourceAudio -t $AudioSeconds -ac 1 -ar 16000 -c:a pcm_s16le $TargetAudio
$FfmpegExitCode = $LASTEXITCODE
if ($FfmpegExitCode -ne 0) {
    throw "ffmpeg failed preparing Wan S2V test audio with exit code $FfmpegExitCode."
}
Require-File $TargetAudio "Prepared Wan S2V test audio"

Log "Reference image: $TargetImage"
Log "Speech audio: $TargetAudio"
Log ("Audio duration target: {0:N2}s" -f $AudioSeconds)

Section "OFFICIAL TEMPLATE"
$TemplateCandidates = @(
    "Z:\AI\Flux2Klein\ComfyUI_windows_portable\python_embeded\Lib\site-packages\comfyui_workflow_templates_json\templates\video_wan2_2_14B_s2v.json",
    "Z:\AI\MiniMaxH3\ComfyUI_windows_portable\python_embeded\Lib\site-packages\comfyui_workflow_templates_json\templates\video_wan2_2_14B_s2v.json",
    "Z:\AI\QwenImageEdit\ComfyUI_windows_portable\python_embeded\Lib\site-packages\comfyui_workflow_templates_json\templates\video_wan2_2_14B_s2v.json"
)
$Template = $TemplateCandidates | Where-Object { Test-Path -LiteralPath $_ -PathType Leaf } | Select-Object -First 1
if ($null -eq $Template) {
    throw "Official local video_wan2_2_14B_s2v.json template not found."
}
$PinnedTemplate = Join-Path $WanRoot "video_wan2_2_14B_s2v_official_pinned.json"
Copy-Item -LiteralPath $Template -Destination $PinnedTemplate -Force
Log "Template source: $Template"
Log "Pinned copy: $PinnedTemplate"

Section "MANIFEST"
$ManifestPath = Join-Path $WanRoot "wan_s2v_benchmark_prepare_manifest.json"
$Manifest = [ordered]@{
    schema = "WAN-S2V-PREPARE-01"
    created = (Get-Date).ToString("o")
    runtime_root = $WanRoot
    runtime_support = "PASS"
    model = [ordered]@{
        diffusion = $S2VModel
        diffusion_sha256 = $S2VSha
        audio_encoder = $AudioEncoder
        audio_encoder_sha256 = $AudioEncoderSha
        reused_text_encoder = $ExistingText
        reused_vae = $ExistingVae
    }
    benchmark = [ordered]@{
        reference_image = $TargetImage
        audio = $TargetAudio
        audio_seconds = $AudioSeconds
        intended_chunk_frames = 77
        fps = 16
        intended_chunk_seconds = 77.0 / 16.0
        cosyvoice = "deferred"
    }
    official_template = $PinnedTemplate
}
$Manifest | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $ManifestPath -Encoding UTF8
Log "Manifest: $ManifestPath"

Section "RESULT"
if ($Download) {
    if (-not (Verify-Sha256 $S2VModel $S2VSha)) {
        throw "S2V model verification failed after preparation."
    }
    if (-not (Verify-Sha256 $AudioEncoder $AudioEncoderSha)) {
        throw "Audio encoder verification failed after preparation."
    }
    Log "WAN S2V BENCHMARK ASSETS PREPARED"
    Log "Next: build a single-chunk workflow pinned to these assets and reused UMT5/VAE."
} else {
    Log "PREFLIGHT PASS. Models not downloaded because -Download was not supplied."
}

Set-Content -LiteralPath $Report -Value $Lines -Encoding UTF8
Log ""
Log "REPORT: $Report"
