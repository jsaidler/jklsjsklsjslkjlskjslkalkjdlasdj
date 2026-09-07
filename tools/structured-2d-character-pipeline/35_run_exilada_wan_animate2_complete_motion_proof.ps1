param(
    [string]$ProjectRepoRoot = 'D:\GOOGLE DRIVE\DEV\Roguelite',
    [string]$WanWorkspace = 'D:\AI\WanAnimate2',
    [string]$PipelineWorkspace = 'Z:\AI\RogueliteCharacterPipeline',
    [string]$MotionGuide = 'Z:\AI\RogueliteCharacterPipeline\g3s_c1c_gameplay_walk_overlay_v2_feminine\overlay_v2_feminine\g3s_c1c_gameplay_walk_overlay_v2_feminine_guide.json',
    [string]$MasterPath = 'D:\GOOGLE DRIVE\DEV\Roguelite\assets\source\characters\exilada\reference\exilada_master.png',
    [int]$Port = 8188,
    [int]$Timeout = 7200
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Fail([string]$Message) {
    Write-Host "G3S-WAN-COMPLETE-MOTION: FAIL - $Message" -ForegroundColor Red
    exit 1
}

function Find-ComfyRoot([string]$Base) {
    foreach ($candidate in @($Base, (Join-Path $Base 'ComfyUI'))) {
        if (Test-Path (Join-Path $candidate 'main.py') -PathType Leaf) { return $candidate }
    }
    return $null
}

function Find-ComfyPython([string]$Base, [string]$ComfyRoot) {
    foreach ($candidate in @(
        (Join-Path $ComfyRoot '.venv\Scripts\python.exe'),
        (Join-Path $Base '.venv\Scripts\python.exe')
    )) {
        if (Test-Path $candidate -PathType Leaf) { return $candidate }
    }
    return $null
}

Write-Host ''
Write-Host 'Roguelite - Runner 35 / Wan-Animate-2 COMPLETE-MOTION driver proof' -ForegroundColor Cyan
Write-Host '[PURPOSE] Test whether direct driving-video conditioning can animate the COMPLETE initial Exilada better than body-pose-only Moore+SSD.' -ForegroundColor Yellow
Write-Host '[RUNTIME LOCK] Every exported sprite remains one complete precomposed character frame.' -ForegroundColor Green
Write-Host '[REFERENCE] exilada_master.png remains the complete initial-state appearance reference.' -ForegroundColor Green
Write-Host '[DRIVER] 17 frames @ 384x576 / 16fps: 16-frame loop + explicit duplicate closure frame.' -ForegroundColor Green
Write-Host '[DRIVER CONTENT] body + explicit heavy-hair lag + cloth lag + subtle soft-body lag + wrist/ankle broken-chain trajectories.' -ForegroundColor Green
Write-Host '[WAN] Official Wan-Animate-2 BASE INT8 ConvRot; 20 steps; Euler; shift 5; seed 42; no distillation LoRA.' -ForegroundColor Green
Write-Host '[DECISION] This is a discriminant. If complete secondary motion is not materially better, do not rescue it by seed/CFG fishing.' -ForegroundColor Yellow
Write-Host ''

$DriverBuilder = Join-Path $ProjectRepoRoot 'tools\structured-2d-character-pipeline\g3s_build_complete_motion_driver_v1.py'
$WanBuilder = Join-Path $ProjectRepoRoot 'tools\wan-animate2-spike\build_workflow_complete_motion.py'
$WanInspect = Join-Path $ProjectRepoRoot 'tools\wan-animate2-spike\inspect.ps1'
$Packer = Join-Path $ProjectRepoRoot 'tools\structured-2d-character-pipeline\g3s_pack_wan_complete_character_spritesheet.py'
foreach ($f in @($DriverBuilder,$WanBuilder,$WanInspect,$Packer,$MotionGuide,$MasterPath)) {
    if (-not (Test-Path $f -PathType Leaf)) { Fail "required file missing: $f" }
}

$ComfyRoot = Find-ComfyRoot $WanWorkspace
if (-not $ComfyRoot) {
    Fail "Wan workspace not found at $WanWorkspace. Existing spike must be bootstrapped first; no model download is performed by runner 35."
}
$Python = Find-ComfyPython $WanWorkspace $ComfyRoot
if (-not $Python) { Fail "ComfyUI Python not found under $WanWorkspace" }
if (-not (Get-Command ffmpeg.exe -ErrorAction SilentlyContinue)) { Fail 'ffmpeg.exe not found.' }
if (-not (Get-Command ffprobe.exe -ErrorAction SilentlyContinue)) { Fail 'ffprobe.exe not found.' }
if (-not (Get-Command py.exe -ErrorAction SilentlyContinue)) { Fail 'py.exe not found; existing Wan spike uses Python launcher/comfy-cli.' }

$Models = Join-Path $ComfyRoot 'models'
$RequiredWanFiles = @(
    (Join-Path $Models 'diffusion_models\wan_animate_2_int8_convrot.safetensors'),
    (Join-Path $Models 'text_encoders\umt5_xxl_fp8_e4m3fn_scaled.safetensors'),
    (Join-Path $Models 'clip_vision\clip_vision_h.safetensors'),
    (Join-Path $Models 'vae\Wan2_1_VAE_bf16.safetensors')
)
foreach ($f in $RequiredWanFiles) {
    if (-not (Test-Path $f -PathType Leaf)) {
        Fail "Wan Base asset missing: $f. Runner 35 will not silently download models. Use tools\wan-animate2-spike\bootstrap.ps1 -UseOfficialBaseInt8 if required."
    }
}

$InputDir = Join-Path $ComfyRoot 'input'
$OutputDir = Join-Path $ComfyRoot 'output'
New-Item -ItemType Directory -Force -Path $InputDir | Out-Null
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null
Copy-Item -LiteralPath $MasterPath -Destination (Join-Path $InputDir 'exilada_master.png') -Force

$ProofRoot = Join-Path $PipelineWorkspace 'g3s_runner35_wan_complete_motion_proof'
$DriverRoot = Join-Path $ProofRoot 'driver'
$WanRoot = Join-Path $ProofRoot 'wan_output'
$ExtractedFrames = Join-Path $WanRoot 'frames_17'
$SpriteRoot = Join-Path $ProofRoot 'spritesheet'
Remove-Item -LiteralPath $ProofRoot -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force -Path $DriverRoot,$WanRoot,$ExtractedFrames,$SpriteRoot | Out-Null

Write-Host '[1/6] Building deterministic complete-motion driver frames...' -ForegroundColor Yellow
& $Python $DriverBuilder --guide $MotionGuide --output $DriverRoot
if ($LASTEXITCODE -ne 0) { Fail "complete-motion driver builder exited with code $LASTEXITCODE" }
$DriverMarker = Join-Path $DriverRoot 'complete_motion_driver.json'
if (-not (Test-Path $DriverMarker -PathType Leaf)) { Fail 'complete-motion driver marker missing.' }
$DriverData = Get-Content -LiteralPath $DriverMarker -Raw | ConvertFrom-Json
if ($DriverData.status -ne 'PASS_DRIVER_FRAMES_READY' -or [int]$DriverData.frame_count -ne 17) {
    Fail 'complete-motion driver did not produce the expected 17-frame package.'
}

$DriverMp4 = Join-Path $InputDir 'exilada_complete_motion_driver_17f.mp4'
Write-Host '[2/6] Encoding exact 17-frame Wan driving video...' -ForegroundColor Yellow
& ffmpeg.exe -hide_banner -loglevel warning -y `
    -framerate 16 `
    -i (Join-Path $DriverRoot 'frames\frame_%03d.png') `
    -frames:v 17 `
    -an `
    -c:v libx264 `
    -pix_fmt yuv420p `
    -movflags +faststart `
    $DriverMp4
if ($LASTEXITCODE -ne 0) { Fail 'ffmpeg failed while encoding the complete-motion driver.' }

$ProbeText = & ffprobe.exe -v error -select_streams v:0 -count_frames -show_entries stream=width,height,r_frame_rate,nb_read_frames -of default=noprint_wrappers=1 $DriverMp4 2>&1
$ProbeText | Out-Host
if (($ProbeText -join "`n") -notmatch 'width=384' -or ($ProbeText -join "`n") -notmatch 'height=576' -or ($ProbeText -join "`n") -notmatch 'nb_read_frames=17') {
    Fail 'encoded driver contract check failed; expected 384x576 and exactly 17 frames.'
}

Write-Host '[3/6] Starting/validating existing Wan-Animate-2 ComfyUI environment...' -ForegroundColor Yellow
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $WanInspect -Workspace $WanWorkspace -Port $Port
if ($LASTEXITCODE -ne 0) { Fail "Wan inspect/preflight exited with code $LASTEXITCODE" }

$BaseUrl = "http://127.0.0.1:$Port"
try { $Queue = Invoke-RestMethod -Uri "$BaseUrl/queue" -TimeoutSec 10 } catch { Fail "ComfyUI API unavailable after inspect: $BaseUrl" }
if ($Queue.queue_running -and @($Queue.queue_running).Count -gt 0) {
    Fail 'ComfyUI already has a running prompt; refusing to submit a second expensive Wan job.'
}

$Template = Join-Path $ProofRoot 'video_wan_animate2_official.json'
$Workflow = Join-Path $ProofRoot 'wan_animate2_exilada_complete_motion_17f.json'
$TemplateUrl = 'https://raw.githubusercontent.com/Comfy-Org/workflow_templates/main/templates/video_wan_animate2.json'
Write-Host '[4/6] Building current official Wan-Animate-2 workflow...' -ForegroundColor Yellow
Invoke-WebRequest -UseBasicParsing -Uri $TemplateUrl -OutFile $Template
& $Python $WanBuilder $Template $Workflow
if ($LASTEXITCODE -ne 0) { Fail 'complete-motion Wan workflow builder failed.' }

$RunStart = Get-Date
Write-Host '[5/6] Running Wan-Animate-2 Base complete-motion transfer...' -ForegroundColor Yellow
Write-Host "[NOTE] RTX 3060 12 GB target; this can take a long time. Timeout=${Timeout}s." -ForegroundColor DarkYellow
Push-Location 'D:\AI'
try {
    & py.exe -3.14 -m pipx run --spec comfy-cli comfy --workspace $WanWorkspace run `
        --workflow $Workflow `
        --where local `
        --host 127.0.0.1 `
        --port $Port `
        --wait `
        --timeout $Timeout `
        --verbose
    if ($LASTEXITCODE -ne 0) { Fail "comfy-cli Wan run exited with code $LASTEXITCODE" }
} finally {
    Pop-Location
}

$NewMedia = Get-ChildItem -Path $OutputDir -Recurse -File -ErrorAction SilentlyContinue |
    Where-Object { $_.Extension -match '^\.(mp4|webm|gif|webp)$' -and $_.LastWriteTime -ge $RunStart.AddSeconds(-5) } |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1
if (-not $NewMedia) { Fail 'Wan run finished but no new generated media was found.' }
$WanVideo = Join-Path $WanRoot ("wan_complete_motion_output" + $NewMedia.Extension.ToLower())
Copy-Item -LiteralPath $NewMedia.FullName -Destination $WanVideo -Force
Write-Host "WAN OUTPUT: $WanVideo" -ForegroundColor Cyan

Write-Host '[6/6] Extracting 17 output frames and packing the first 16 as a complete-character spritesheet...' -ForegroundColor Yellow
Remove-Item -LiteralPath $ExtractedFrames -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force -Path $ExtractedFrames | Out-Null
& ffmpeg.exe -hide_banner -loglevel warning -y -i $WanVideo `
    -vf 'fps=16,scale=384:576:flags=lanczos' `
    -frames:v 17 `
    (Join-Path $ExtractedFrames 'frame_%03d.png')
if ($LASTEXITCODE -ne 0) { Fail 'ffmpeg failed extracting Wan output frames.' }
$Count = @(Get-ChildItem -LiteralPath $ExtractedFrames -Filter 'frame_*.png').Count
if ($Count -lt 17) { Fail "expected 17 extracted Wan frames, got $Count" }

& $Python $Packer --frames-dir $ExtractedFrames --master $MasterPath --output $SpriteRoot --source-video $WanVideo
if ($LASTEXITCODE -ne 0) { Fail "Wan spritesheet packer exited with code $LASTEXITCODE" }
$Metadata = Join-Path $SpriteRoot 'exilada_initial_walk16_wan_complete_spritesheet.json'
if (-not (Test-Path $Metadata -PathType Leaf)) { Fail 'Wan spritesheet metadata missing.' }
$Meta = Get-Content -LiteralPath $Metadata -Raw | ConvertFrom-Json
if ($Meta.status -ne 'PASS_OUTPUT_READY_FOR_VISUAL_QA') { Fail "unexpected packer status: $($Meta.status)" }

$Result = [ordered]@{
    gate = 'G3S_RUNNER35_WAN_ANIMATE2_COMPLETE_MOTION_PROOF'
    status = 'PASS_OUTPUT_READY_FOR_VISUAL_QA'
    reference_master = $MasterPath
    body_motion_guide = $MotionGuide
    driver_marker = $DriverMarker
    driver_video = $DriverMp4
    wan_workspace = $WanWorkspace
    wan_model = 'wan_animate_2_int8_convrot.safetensors'
    wan_route = 'official_base_int8_convrot'
    output_video = $WanVideo
    spritesheet_metadata = $Metadata
    spritesheet = $Meta.sheet
    preview_gif = $Meta.preview_gif
    gameplay_128px_preview_gif = $Meta.gameplay_128px_preview_gif
    decision_rule = 'Continue only if direct complete-video conditioning materially improves whole-character secondary motion and attachment coherence over runner 34; no seed/CFG fishing.'
}
$ResultPath = Join-Path $ProofRoot 'runner35_result.json'
$Result | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $ResultPath -Encoding UTF8

Write-Host ''
Write-Host 'G3S-WAN-COMPLETE-MOTION: OUTPUT READY FOR VISUAL QA' -ForegroundColor Green
Write-Host "DRIVER SHEET: $($DriverData.contact_sheet)" -ForegroundColor Cyan
Write-Host "DRIVER GIF:   $($DriverData.preview_gif)" -ForegroundColor Cyan
Write-Host "WAN VIDEO:    $WanVideo" -ForegroundColor Cyan
Write-Host "SPRITESHEET:  $($Meta.sheet)" -ForegroundColor Green
Write-Host "FULL PREVIEW: $($Meta.preview_gif)" -ForegroundColor Green
Write-Host "128PX PREVIEW:$($Meta.gameplay_128px_preview_gif)" -ForegroundColor Green
Write-Host "RESULT:       $ResultPath" -ForegroundColor Cyan
Write-Host ''
Write-Host '[QA] Compare against runner 34 specifically on hair inertia, cloth lag, jiggle, chain ownership/trajectory, feet/lower-leg topology, identity and loop coherence.' -ForegroundColor Yellow
Write-Host '[KILL] If those classes are not materially better, Wan complete-video conditioning does not justify further rescue tuning in this branch.' -ForegroundColor Yellow
