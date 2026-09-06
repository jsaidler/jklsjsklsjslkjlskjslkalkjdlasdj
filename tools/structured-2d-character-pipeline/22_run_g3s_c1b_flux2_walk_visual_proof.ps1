param(
    [string]$RepoRoot = 'D:\GOOGLE DRIVE\DEV\Roguelite',
    [string]$FluxWorkspace = 'Z:\AI\Flux2RefControlSpike',
    [string]$PipelineWorkspace = 'Z:\AI\RogueliteCharacterPipeline',
    [int]$Port = 8215,
    [int]$PromptTimeoutSec = 1800
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Fail([string]$Message) {
    Write-Host "G3S-C1B: FAIL - $Message" -ForegroundColor Red
    exit 1
}

function Get-Prop([object]$Object, [string]$Name) {
    if ($null -eq $Object) { return $null }
    $p = $Object.PSObject.Properties[$Name]
    if ($null -eq $p) { return $null }
    return $p.Value
}

function Save-Json([object]$Object, [string]$Path, [int]$Depth = 32) {
    $d = [math]::Max(4, [math]::Min($Depth, 64))
    $json = $Object | ConvertTo-Json -Depth $d
    [System.IO.File]::WriteAllText($Path, $json, [System.Text.UTF8Encoding]::new($false))
}

function Wait-ComfyReady([System.Diagnostics.Process]$Process, [string]$Api, [int]$TimeoutSec) {
    $deadline = (Get-Date).AddSeconds($TimeoutSec)
    while ((Get-Date) -lt $deadline) {
        if ($Process.HasExited) { throw "ComfyUI exited during startup with code $($Process.ExitCode)." }
        try {
            $info = Invoke-RestMethod -Uri "$Api/object_info" -Method Get -TimeoutSec 5
            if ($info) { return $info }
        } catch {}
        Start-Sleep -Milliseconds 750
    }
    throw "Timed out waiting for ComfyUI at $Api"
}

function Wait-Prompt([System.Diagnostics.Process]$Process, [string]$Api, [string]$PromptId, [int]$TimeoutSec) {
    $deadline = (Get-Date).AddSeconds($TimeoutSec)
    $entry = $null
    while ((Get-Date) -lt $deadline) {
        if ($Process.HasExited) { throw "ComfyUI exited during inference with code $($Process.ExitCode)." }
        try {
            $history = Invoke-RestMethod -Uri "$Api/history/$PromptId" -Method Get -TimeoutSec 10
            $p = $history.PSObject.Properties[$PromptId]
            if ($null -ne $p) {
                $entry = $p.Value
                $status = Get-Prop $entry 'status'
                if ((Get-Prop $status 'completed') -eq $true) { break }
            }
        } catch {}
        Start-Sleep -Seconds 1
    }
    if ($null -eq $entry) { throw "Timed out waiting for prompt $PromptId" }
    $status = Get-Prop $entry 'status'
    if ((Get-Prop $status 'completed') -ne $true -or [string](Get-Prop $status 'status_str') -ne 'success') {
        throw "Prompt $PromptId did not complete successfully; status=$([string](Get-Prop $status 'status_str'))"
    }
    return $entry
}

$PortableRoot = Join-Path $FluxWorkspace 'ComfyUI_windows_portable'
$ComfyRoot = Join-Path $PortableRoot 'ComfyUI'
$Python = Join-Path $PortableRoot 'python_embeded\python.exe'
$MainPy = Join-Path $ComfyRoot 'main.py'
$InputDir = Join-Path $ComfyRoot 'input\g3s_c1b'
$OutputRoot = Join-Path $ComfyRoot 'output'
$OutputSubfolder = 'g3s_c1b_flux2'
$OutputDir = Join-Path $OutputRoot $OutputSubfolder
$ApiRoot = "http://127.0.0.1:$Port"

$UnetName = 'flux-2-klein-base-4b-fp8.safetensors'
$ClipName = 'qwen_3_4b.safetensors'
$VaeName = 'flux2-vae.safetensors'
$UnetPath = Join-Path $ComfyRoot "models\diffusion_models\$UnetName"
$ClipPath = Join-Path $ComfyRoot "models\text_encoders\$ClipName"
$VaePath = Join-Path $ComfyRoot "models\vae\$VaeName"

$Spec = Join-Path $RepoRoot 'tools\structured-2d-character-pipeline\g3s_c1b_flux2_walk_spec.json'
$Approval = Join-Path $RepoRoot 'tools\structured-2d-character-pipeline\g3s_c1a_skeleton_walk_approval.json'
$Guide = Join-Path $PipelineWorkspace 'g3s_c1_skeleton_walk\g3s_c1_skeleton_walk_guide.json'
$Body = Join-Path $RepoRoot 'assets\source\characters\exilada\body\exilada_body_base_b3b_v4.png'
$Prepare = Join-Path $RepoRoot 'tools\structured-2d-character-pipeline\g3s_c1b_prepare_flux2_walk_inputs.py'
$Review = Join-Path $RepoRoot 'tools\structured-2d-character-pipeline\g3s_c1b_build_flux2_walk_review.py'
$Workspace = Join-Path $PipelineWorkspace 'g3s_c1b_flux2_walk_visual_proof'
$RunDir = Join-Path $Workspace 'run'
$LogDir = Join-Path $Workspace 'logs'
$InputManifest = Join-Path $Workspace 'g3s_c1b_input_manifest.json'
$RunManifest = Join-Path $RunDir 'g3s_c1b_run_manifest.json'
$StdoutLog = Join-Path $LogDir 'comfy_stdout.log'
$StderrLog = Join-Path $LogDir 'comfy_stderr.log'

$required = @($Python,$MainPy,$UnetPath,$ClipPath,$VaePath,$Spec,$Approval,$Guide,$Body,$Prepare,$Review)
$missing = @($required | Where-Object { -not (Test-Path $_ -PathType Leaf) })
if ($missing.Count -gt 0) {
    Write-Host ''
    Write-Host 'G3S-C1B: REQUIRED EXISTING LOCAL COMPONENT MISSING' -ForegroundColor Red
    foreach ($p in $missing) { Write-Host "MISSING: $p" -ForegroundColor Yellow }
    Write-Host 'No download was attempted.' -ForegroundColor Yellow
    exit 1
}

$approvalData = Get-Content -LiteralPath $Approval -Raw | ConvertFrom-Json
if ($approvalData.gate -ne 'G3S-C1A' -or $approvalData.status -ne 'PASS') { Fail 'C1A skeleton walk is not approved PASS.' }
$specData = Get-Content -LiteralPath $Spec -Raw | ConvertFrom-Json
if ($specData.gate -ne 'G3S-C1B' -or $specData.revision -ne 'FLUX2_EIGHT_POSE_VISUAL_PROOF_V1' -or $specData.status -ne 'RUNNER_READY_REVIEW_REQUIRED') {
    Fail 'C1B spec is not runner-ready.'
}
$bodyHash = (Get-FileHash -LiteralPath $Body -Algorithm SHA256).Hash.ToLowerInvariant()
if ($bodyHash -ne '702e2d95325049b5d99ea66db4fbbb9b41d6d24813efb0b1c3a37e112b1c2858') { Fail "Canonical B3B body hash changed: $bodyHash" }

Write-Host ''
Write-Host 'Roguelite - G3S-C1B EXILADA EIGHT-POSE WALK VISUAL PROOF' -ForegroundColor Cyan
Write-Host '[LOCK] C1A skeleton cycle is PASS and owns pose/laterality/depth/contact only.' -ForegroundColor Green
Write-Host '[LOCK] B3B V4 owns visible identity/body-style reference.' -ForegroundColor Green
Write-Host '[LOCK] No static sprite warp/cutout/cage. Each gait state is redrawn as a complete body.' -ForegroundColor Green
Write-Host '[LOCK] Hair, clothing, restraints, accessories and weapons remain absent.' -ForegroundColor Green
Write-Host '[LOCK] Uses the already-retained local FLUX.2 Klein stack only; NO DOWNLOAD and NO PAID API.' -ForegroundColor Green
Write-Host '[LOCK] Generated frames are REVIEW CANDIDATES only and are NOT promoted automatically.' -ForegroundColor Yellow
Write-Host '[OUTPUT] One visible eight-frame Exilada walk GIF + contact sheet.' -ForegroundColor Cyan
Write-Host ''

New-Item -ItemType Directory -Force -Path $InputDir,$OutputDir,$Workspace,$RunDir,$LogDir | Out-Null
Get-ChildItem -LiteralPath $InputDir -File -ErrorAction SilentlyContinue | Remove-Item -Force
Get-ChildItem -LiteralPath $OutputDir -File -Filter 'g3s_c1b_*' -ErrorAction SilentlyContinue | Remove-Item -Force
Get-ChildItem -LiteralPath $RunDir -File -ErrorAction SilentlyContinue | Remove-Item -Force

& $Python $Prepare --guide $Guide --approval $Approval --spec $Spec --body $Body --input-dir $InputDir --workspace $Workspace
if ($LASTEXITCODE -ne 0) { Fail "Input preparation exited with code $LASTEXITCODE" }
if (-not (Test-Path $InputManifest -PathType Leaf)) { Fail "Input manifest missing: $InputManifest" }
$inputs = Get-Content -LiteralPath $InputManifest -Raw | ConvertFrom-Json
if ($inputs.pose_refs.Count -ne 8) { Fail "Expected 8 prepared pose controls, got $($inputs.pose_refs.Count)." }

$portBusy = $false
try {
    Invoke-RestMethod -Uri "$ApiRoot/object_info" -Method Get -TimeoutSec 2 | Out-Null
    $portBusy = $true
} catch { $portBusy = $false }
if ($portBusy) { Fail "port $Port is already in use by a ComfyUI-compatible endpoint" }

Remove-Item $StdoutLog,$StderrLog -Force -ErrorAction SilentlyContinue
$args = @('-s',$MainPy,'--windows-standalone-build','--listen','127.0.0.1','--port',[string]$Port,'--disable-auto-launch')
$proc = Start-Process -FilePath $Python -ArgumentList $args -WorkingDirectory $ComfyRoot -PassThru -RedirectStandardOutput $StdoutLog -RedirectStandardError $StderrLog

try {
    $info = Wait-ComfyReady $proc $ApiRoot 90
    foreach ($node in @('UNETLoader','CLIPLoader','VAELoader','CLIPTextEncode','LoadImage','VAEEncode','ReferenceLatent','EmptyFlux2LatentImage','Flux2Scheduler','RandomNoise','KSamplerSelect','CFGGuider','SamplerCustomAdvanced','VAEDecode','SaveImage')) {
        if ($null -eq $info.PSObject.Properties[$node]) { throw "runtime missing required node: $node" }
    }

    $Width = [int]$specData.authoring_canvas.model[0]
    $Height = [int]$specData.authoring_canvas.model[1]
    $Steps = [int]$specData.generation.steps
    $Cfg = [double]$specData.generation.cfg
    $BaseSeed = [long]$specData.generation.base_seed
    $Duration = [int]$specData.generation.frame_duration_ms
    $BodyRel = 'g3s_c1b/' + [string]$inputs.body_reference_name

    $outputs = @()
    foreach ($pose in $inputs.pose_refs) {
        $i = [int]$pose.index
        $event = [string]$pose.event
        $support = [string]$pose.support_foot
        $poseRel = 'g3s_c1b/' + [string]$pose.model_input_name
        $seed = $BaseSeed + $i
        $prefix = "$OutputSubfolder/g3s_c1b_$('{0:d2}' -f $i)_$event"

        $Prompt = @"
Create ONE full-body modern pixel-art animation frame of the SAME ADULT WOMAN shown in IMAGE 1.
IMAGE 1 is the AUTHORITATIVE IDENTITY, BODY PROPORTIONS, SKIN TONE, BALD HEAD, CAMERA FAMILY AND PIXEL-ART LANGUAGE. Preserve her adult feminine anatomy, lean functional build, relatively long legs, defined waist, natural breasts, shoulders and barefoot body. Do not redesign her.
IMAGE 2 is POSE CONTROL ONLY. Redraw the complete woman from scratch so her pelvis, torso, head, shoulders, elbows, wrists, hips, knees, ankles and feet follow that skeleton pose and its foreshortening. Do NOT draw the skeleton or copy its colors/lines.
This gait state is $event; support foot is anatomical $support. The character remains in the elevated front-three-quarter belt-scroller family and faces/travels SCREEN-LEFT.
She is an adult bald nude woman, barefoot, with no hair, no clothing, no wraps, no chains, no restraints, no accessories, no weapons. Neutral flat light background, no environment, no cast shadow.
Anatomy must be coherent: exactly two arms, two legs, two hands and two feet; connected shoulders/hips; no detached limbs, duplicate limbs, melted joints or twisted impossible pelvis.
True deliberate modern pixel art, not painterly illustration and not a pixel filter. Work as if every logical sprite pixel is represented by a uniform 6x6 square block: hard square edges, no antialiasing, no blur, no photographic texture and no smooth gradients. Keep the whole body fully inside frame with both feet visible.
"@.Trim()

        $workflow = [ordered]@{
            '1' = @{ class_type='UNETLoader'; inputs=@{ unet_name=$UnetName; weight_dtype='default' } }
            '2' = @{ class_type='CLIPLoader'; inputs=@{ clip_name=$ClipName; type='flux2'; device='default' } }
            '3' = @{ class_type='VAELoader'; inputs=@{ vae_name=$VaeName } }
            '4' = @{ class_type='CLIPTextEncode'; inputs=@{ text=$Prompt; clip=@('2',0) } }
            '5' = @{ class_type='CLIPTextEncode'; inputs=@{ text=''; clip=@('2',0) } }
            '6' = @{ class_type='LoadImage'; inputs=@{ image=$BodyRel } }
            '7' = @{ class_type='VAEEncode'; inputs=@{ pixels=@('6',0); vae=@('3',0) } }
            '8' = @{ class_type='LoadImage'; inputs=@{ image=$poseRel } }
            '9' = @{ class_type='VAEEncode'; inputs=@{ pixels=@('8',0); vae=@('3',0) } }
            '10' = @{ class_type='ReferenceLatent'; inputs=@{ conditioning=@('4',0); latent=@('7',0) } }
            '11' = @{ class_type='ReferenceLatent'; inputs=@{ conditioning=@('10',0); latent=@('9',0) } }
            '12' = @{ class_type='ReferenceLatent'; inputs=@{ conditioning=@('5',0); latent=@('7',0) } }
            '13' = @{ class_type='ReferenceLatent'; inputs=@{ conditioning=@('12',0); latent=@('9',0) } }
            '14' = @{ class_type='EmptyFlux2LatentImage'; inputs=@{ width=$Width; height=$Height; batch_size=1 } }
            '15' = @{ class_type='Flux2Scheduler'; inputs=@{ steps=$Steps; width=$Width; height=$Height } }
            '16' = @{ class_type='RandomNoise'; inputs=@{ noise_seed=$seed } }
            '17' = @{ class_type='KSamplerSelect'; inputs=@{ sampler_name='euler' } }
            '18' = @{ class_type='CFGGuider'; inputs=@{ model=@('1',0); positive=@('11',0); negative=@('13',0); cfg=$Cfg } }
            '19' = @{ class_type='SamplerCustomAdvanced'; inputs=@{ noise=@('16',0); guider=@('18',0); sampler=@('17',0); sigmas=@('15',0); latent_image=@('14',0) } }
            '20' = @{ class_type='VAEDecode'; inputs=@{ samples=@('19',0); vae=@('3',0) } }
            '21' = @{ class_type='SaveImage'; inputs=@{ images=@('20',0); filename_prefix=$prefix } }
        }

        $request = [ordered]@{ prompt=$workflow; client_id="g3s-c1b-$i" }
        $requestPath = Join-Path $RunDir ("request_{0:d2}_{1}.json" -f $i,$event)
        Save-Json $request $requestPath 32
        $bodyJson = $request | ConvertTo-Json -Depth 32 -Compress

        Write-Host "[GENERATE $($i+1)/8] $event | support=$support | seed=$seed" -ForegroundColor Cyan
        $submit = Invoke-RestMethod -Uri "$ApiRoot/prompt" -Method Post -ContentType 'application/json' -Body $bodyJson -TimeoutSec 30
        $promptId = [string](Get-Prop $submit 'prompt_id')
        if ([string]::IsNullOrWhiteSpace($promptId)) { throw "No prompt_id returned for frame $i" }
        $entry = Wait-Prompt $proc $ApiRoot $promptId $PromptTimeoutSec

        $save = (Get-Prop $entry 'outputs').PSObject.Properties['21']
        if ($null -eq $save) { throw "SaveImage node produced no output for frame $i" }
        $images = @(Get-Prop $save.Value 'images')
        if ($images.Count -ne 1) { throw "expected one output for frame $i, got $($images.Count)" }
        $filename = [string](Get-Prop $images[0] 'filename')
        $subfolder = [string](Get-Prop $images[0] 'subfolder')
        $generated = if ([string]::IsNullOrWhiteSpace($subfolder)) { Join-Path $OutputRoot $filename } else { Join-Path (Join-Path $OutputRoot $subfolder) $filename }
        if (-not (Test-Path $generated -PathType Leaf)) { throw "generated frame missing: $generated" }

        $outputs += [ordered]@{
            index=$i
            frame=[int]$pose.frame
            event=$event
            support_foot=$support
            near_side=[string]$pose.near_side
            far_side=[string]$pose.far_side
            seed=$seed
            prompt_id=$promptId
            generated=$generated
            generated_sha256=(Get-FileHash -LiteralPath $generated -Algorithm SHA256).Hash.ToLowerInvariant()
            pose_control=[string]$pose.model_input
        }
        Write-Host "[OK] $event -> $generated" -ForegroundColor Green
    }

    $run = [ordered]@{
        gate='G3S-C1B'
        revision='FLUX2_EIGHT_POSE_VISUAL_PROOF_V1'
        status='REVIEW_REQUIRED'
        created_at=(Get-Date).ToString('o')
        visual_stack='existing retained FLUX.2 Klein Base 4B FP8 + qwen_3_4b + flux2-vae'
        downloads=0
        paid_api=$false
        production_promotion=$false
        frame_duration_ms=$Duration
        body_reference=$Body
        skeleton_guide=$Guide
        outputs=$outputs
    }
    Save-Json $run $RunManifest 32

    & $Python $Review --run-manifest $RunManifest --body $Body --workspace $Workspace
    if ($LASTEXITCODE -ne 0) { throw "Review builder exited with code $LASTEXITCODE" }

    $Gif = Join-Path $Workspace 'g3s_c1b_exilada_walk_visual_proof.gif'
    $Sheet = Join-Path $Workspace 'g3s_c1b_exilada_walk_contact_sheet.png'
    $ReviewJson = Join-Path $Workspace 'g3s_c1b_review.json'
    foreach ($p in @($Gif,$Sheet,$ReviewJson)) {
        if (-not (Test-Path $p -PathType Leaf)) { throw "Expected C1B review output missing: $p" }
    }

    Write-Host ''
    Write-Host 'G3S-C1B: VISIBLE WALK REVIEW PACKAGE READY' -ForegroundColor Green
    Write-Host "GIF:   $Gif"
    Write-Host "SHEET: $Sheet"
    Write-Host "REVIEW:$ReviewJson"
    Write-Host ''
    Write-Host 'STOP. Share the GIF and contact sheet. Nothing has been promoted into production assets.' -ForegroundColor Yellow
}
catch {
    Write-Host $_.Exception.Message -ForegroundColor Red
    if (Test-Path $StdoutLog) { Write-Host '--- Comfy stdout tail ---'; Get-Content $StdoutLog -Tail 80 | Out-Host }
    if (Test-Path $StderrLog) { Write-Host '--- Comfy stderr tail ---'; Get-Content $StderrLog -Tail 80 | Out-Host }
    exit 1
}
finally {
    if ($null -ne $proc -and -not $proc.HasExited) {
        Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
        $proc.WaitForExit(5000) | Out-Null
    }
}
