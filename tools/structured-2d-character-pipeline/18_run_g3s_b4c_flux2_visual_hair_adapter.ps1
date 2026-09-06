param(
    [string]$RepoRoot = 'D:\GOOGLE DRIVE\DEV\Roguelite',
    [string]$FluxWorkspace = 'Z:\AI\Flux2RefControlSpike',
    [string]$PipelineWorkspace = 'Z:\AI\RogueliteCharacterPipeline',
    [int]$Port = 8214,
    [int]$PromptTimeoutSec = 1800,
    [long]$Seed = 20260906
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Fail([string]$Message) {
    Write-Host "G3S-B4C: FAIL - $Message" -ForegroundColor Red
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

$PortableRoot = Join-Path $FluxWorkspace 'ComfyUI_windows_portable'
$ComfyRoot = Join-Path $PortableRoot 'ComfyUI'
$Python = Join-Path $PortableRoot 'python_embeded\python.exe'
$MainPy = Join-Path $ComfyRoot 'main.py'
$InputDir = Join-Path $ComfyRoot 'input\g3s_b4c'
$OutputRoot = Join-Path $ComfyRoot 'output'
$OutputSubfolder = 'g3s_b4c_flux2'
$OutputDir = Join-Path $OutputRoot $OutputSubfolder

$UnetName = 'flux-2-klein-base-4b-fp8.safetensors'
$ClipName = 'qwen_3_4b.safetensors'
$VaeName = 'flux2-vae.safetensors'
$UnetPath = Join-Path $ComfyRoot "models\diffusion_models\$UnetName"
$ClipPath = Join-Path $ComfyRoot "models\text_encoders\$ClipName"
$VaePath = Join-Path $ComfyRoot "models\vae\$VaeName"

$Body = Join-Path $RepoRoot 'assets\source\characters\exilada\body\exilada_body_base_b3b_v4.png'
$Master = Join-Path $RepoRoot 'assets\source\characters\exilada\reference\exilada_master.png'
$Prepare = Join-Path $RepoRoot 'tools\structured-2d-character-pipeline\g3s_b4c_prepare_flux2_visual_adapter.py'
$Review = Join-Path $RepoRoot 'tools\structured-2d-character-pipeline\g3s_b4c_build_flux2_visual_review.py'
$V4Failure = Join-Path $RepoRoot 'tools\structured-2d-character-pipeline\g3s_b4b_v4_pose_anchor_failure.json'
$Workspace = Join-Path $PipelineWorkspace 'g3s_b4c_flux2_visual_adapter'
$RunDir = Join-Path $Workspace 'run'
$LogDir = Join-Path $Workspace 'logs'
$Manifest = Join-Path $Workspace 'g3s_b4c_input_manifest.json'
$LogicalBody = Join-Path $Workspace 'g3s_b4c_body_reference_logical.png'
$BodyRef = Join-Path $InputDir 'g3s_b4c_body_pose_reference.png'
$MasterRef = Join-Path $InputDir 'g3s_b4c_exilada_master.png'
$ApiRoot = "http://127.0.0.1:$Port"
$StdoutLog = Join-Path $LogDir 'comfy_stdout.log'
$StderrLog = Join-Path $LogDir 'comfy_stderr.log'
$Sentinel = Join-Path $RunDir 'one_shot_started.json'
$RunManifest = Join-Path $RunDir 'one_shot_result.json'

$required = @($Python,$MainPy,$UnetPath,$ClipPath,$VaePath,$Body,$Master,$Prepare,$Review,$V4Failure)
$missing = @($required | Where-Object { -not (Test-Path $_ -PathType Leaf) })
if ($missing.Count -gt 0) {
    Write-Host ''
    Write-Host 'G3S-B4C: EXISTING LOCAL VISUAL STACK IS INCOMPLETE' -ForegroundColor Red
    foreach ($p in $missing) { Write-Host "MISSING: $p" -ForegroundColor Yellow }
    Write-Host 'No download was attempted.' -ForegroundColor Yellow
    exit 1
}

Write-Host ''
Write-Host 'Roguelite - G3S-B4C FLUX2 VISUAL HAIR ADAPTER' -ForegroundColor Cyan
Write-Host '[METHOD] real visual adaptation using the already-retained local FLUX.2 Klein runtime.' -ForegroundColor Green
Write-Host '[LOCK] canonical B3B production body is conditioning/reference only and remains byte/pixel unchanged.' -ForegroundColor Green
Write-Host '[LOCK] canonical master supplies hair identity/material only; clothing/accessories must not transfer.' -ForegroundColor Green
Write-Host '[LOCK] this step generates one visual composite for review; it does NOT promote production hair pixels.' -ForegroundColor Yellow
Write-Host '[LOCK] no download, paid API, Pillow hair geometry, or heuristic pose-anchor authoring occurs.' -ForegroundColor Green
Write-Host ''

New-Item -ItemType Directory -Force -Path $InputDir,$Workspace,$RunDir,$LogDir,$OutputDir | Out-Null

if (Test-Path $Sentinel -PathType Leaf) { Fail "one-shot sentinel already exists: $Sentinel. Do not rerun automatically." }
if (Test-Path $RunManifest -PathType Leaf) { Fail "result manifest already exists: $RunManifest. Do not rerun automatically." }

& $Python $Prepare --body $Body --master $Master --input-dir $InputDir --workspace $Workspace
if ($LASTEXITCODE -ne 0) { Fail "input preparation exited with code $LASTEXITCODE" }
foreach ($p in @($Manifest,$LogicalBody,$BodyRef,$MasterRef)) {
    if (-not (Test-Path $p -PathType Leaf)) { Fail "prepared input missing: $p" }
}

$Prompt = @'
Create a single full-body modern pixel-art adaptation of the adult woman in image 1. IMAGE 1 IS THE AUTHORITATIVE BODY POSE, BODY PROPORTIONS, BODY SCALE, CAMERA ANGLE AND SCREEN PLACEMENT. Preserve that exact three-quarter body pose and the same bald adult female body proportions. IMAGE 2 IS HAIR IDENTITY AND MATERIAL REFERENCE ONLY: transfer only the very long, heavy, voluminous, messy, wild black hair language from image 2 onto the woman from image 1. Do not transfer clothing, wraps, restraints, chains, scars, pose, limb placement, or accessories from image 2. The hair must visibly originate from the scalp of the body in image 1, wrap naturally around that exact head/shoulder/back orientation, with a dominant irregular rear mass behind head/neck/shoulders/back and a smaller sparse front framing mass. Keep the face, neck, clavicle and center torso substantially readable. No curtain shape, no cape shape, no symmetrical wig, no equal-width dreadlocks. Flat neutral background, no scene, no cast shadow. True deliberate pixel art, not painterly illustration and not a pixel filter. Work as if each logical sprite pixel is represented by a uniform 6x6 square block: hard square edges, no antialiasing, no blur, no photographic texture, no smooth gradients. Do not redesign the body. Do not add clothing. Do not add weapons or accessories.
'@.Trim()

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

    Save-Json ([ordered]@{
        revision='B4C_FLUX2_VISUAL_ADAPTER_V1'
        started_at=(Get-Date).ToString('o')
        seed=$Seed
        note='One artistic submission only. Do not rerun automatically after acceptance.'
    }) $Sentinel 16

    $BodyRel = 'g3s_b4c/g3s_b4c_body_pose_reference.png'
    $MasterRel = 'g3s_b4c/g3s_b4c_exilada_master.png'
    $Width = 576
    $Height = 960
    $Steps = 20
    $Cfg = 4.5
    $Prefix = "$OutputSubfolder/g3s_b4c_visual_adapter"

    $workflow = [ordered]@{
        '1' = @{ class_type='UNETLoader'; inputs=@{ unet_name=$UnetName; weight_dtype='default' } }
        '2' = @{ class_type='CLIPLoader'; inputs=@{ clip_name=$ClipName; type='flux2'; device='default' } }
        '3' = @{ class_type='VAELoader'; inputs=@{ vae_name=$VaeName } }
        '4' = @{ class_type='CLIPTextEncode'; inputs=@{ text=$Prompt; clip=@('2',0) } }
        '5' = @{ class_type='CLIPTextEncode'; inputs=@{ text=''; clip=@('2',0) } }
        '6' = @{ class_type='LoadImage'; inputs=@{ image=$BodyRel } }
        '7' = @{ class_type='VAEEncode'; inputs=@{ pixels=@('6',0); vae=@('3',0) } }
        '8' = @{ class_type='LoadImage'; inputs=@{ image=$MasterRel } }
        '9' = @{ class_type='VAEEncode'; inputs=@{ pixels=@('8',0); vae=@('3',0) } }
        '10' = @{ class_type='ReferenceLatent'; inputs=@{ conditioning=@('4',0); latent=@('7',0) } }
        '11' = @{ class_type='ReferenceLatent'; inputs=@{ conditioning=@('10',0); latent=@('9',0) } }
        '12' = @{ class_type='ReferenceLatent'; inputs=@{ conditioning=@('5',0); latent=@('7',0) } }
        '13' = @{ class_type='ReferenceLatent'; inputs=@{ conditioning=@('12',0); latent=@('9',0) } }
        '14' = @{ class_type='EmptyFlux2LatentImage'; inputs=@{ width=$Width; height=$Height; batch_size=1 } }
        '15' = @{ class_type='Flux2Scheduler'; inputs=@{ steps=$Steps; width=$Width; height=$Height } }
        '16' = @{ class_type='RandomNoise'; inputs=@{ noise_seed=$Seed } }
        '17' = @{ class_type='KSamplerSelect'; inputs=@{ sampler_name='euler' } }
        '18' = @{ class_type='CFGGuider'; inputs=@{ model=@('1',0); positive=@('11',0); negative=@('13',0); cfg=$Cfg } }
        '19' = @{ class_type='SamplerCustomAdvanced'; inputs=@{ noise=@('16',0); guider=@('18',0); sampler=@('17',0); sigmas=@('15',0); latent_image=@('14',0) } }
        '20' = @{ class_type='VAEDecode'; inputs=@{ samples=@('19',0); vae=@('3',0) } }
        '21' = @{ class_type='SaveImage'; inputs=@{ images=@('20',0); filename_prefix=$Prefix } }
    }

    $request = [ordered]@{ prompt=$workflow; client_id='g3s-b4c-flux2-visual-adapter' }
    $requestPath = Join-Path $RunDir 'request.json'
    Save-Json $request $requestPath 32
    $bodyJson = $request | ConvertTo-Json -Depth 32 -Compress

    Write-Host '[RUN] submitting one visual-adaptation generation...' -ForegroundColor Cyan
    $submit = Invoke-RestMethod -Uri "$ApiRoot/prompt" -Method Post -ContentType 'application/json' -Body $bodyJson -TimeoutSec 30
    $promptId = [string](Get-Prop $submit 'prompt_id')
    if ([string]::IsNullOrWhiteSpace($promptId)) { throw 'No prompt_id returned. Do not rerun automatically.' }
    Write-Host "[ACCEPTED] prompt_id=$promptId" -ForegroundColor Green

    $deadline = (Get-Date).AddSeconds($PromptTimeoutSec)
    $entry = $null
    while ((Get-Date) -lt $deadline) {
        if ($proc.HasExited) { throw "ComfyUI exited during inference with code $($proc.ExitCode)." }
        try {
            $history = Invoke-RestMethod -Uri "$ApiRoot/history/$promptId" -Method Get -TimeoutSec 10
            $p = $history.PSObject.Properties[$promptId]
            if ($null -ne $p) {
                $entry = $p.Value
                if ((Get-Prop (Get-Prop $entry 'status') 'completed') -eq $true) { break }
            }
        } catch {}
        Start-Sleep -Seconds 1
    }
    if ($null -eq $entry) { throw 'Timed out waiting for history. Do not rerun automatically.' }
    $status = Get-Prop $entry 'status'
    if ((Get-Prop $status 'completed') -ne $true -or [string](Get-Prop $status 'status_str') -ne 'success') {
        throw "generation did not complete successfully; status=$([string](Get-Prop $status 'status_str'))"
    }

    $outputs = Get-Prop $entry 'outputs'
    $save = $outputs.PSObject.Properties['21']
    if ($null -eq $save) { throw 'SaveImage node 21 produced no output.' }
    $images = @(Get-Prop $save.Value 'images')
    if ($images.Count -ne 1) { throw "expected one output image, got $($images.Count)" }
    $filename = [string](Get-Prop $images[0] 'filename')
    $subfolder = [string](Get-Prop $images[0] 'subfolder')
    $generated = if ([string]::IsNullOrWhiteSpace($subfolder)) { Join-Path $OutputRoot $filename } else { Join-Path (Join-Path $OutputRoot $subfolder) $filename }
    if (-not (Test-Path $generated -PathType Leaf)) { throw "generated output missing: $generated" }

    & $Python $Review --master $Master --body-logical $LogicalBody --generated $generated --workspace $Workspace --prompt $Prompt
    if ($LASTEXITCODE -ne 0) { throw "review builder exited with code $LASTEXITCODE" }

    $Contact = Join-Path $Workspace 'g3s_b4c_flux2_contact_sheet.png'
    $ReviewMeta = Join-Path $Workspace 'g3s_b4c_flux2_review.json'
    foreach ($p in @($Contact,$ReviewMeta)) {
        if (-not (Test-Path $p -PathType Leaf)) { throw "review output missing: $p" }
    }

    Save-Json ([ordered]@{
        revision='B4C_FLUX2_VISUAL_ADAPTER_V1'
        completed_at=(Get-Date).ToString('o')
        prompt_id=$promptId
        seed=$Seed
        width=$Width
        height=$Height
        steps=$Steps
        cfg=$Cfg
        generated=$generated
        generated_sha256=(Get-FileHash -LiteralPath $generated -Algorithm SHA256).Hash.ToLowerInvariant()
        contact_sheet=$Contact
        contact_sheet_sha256=(Get-FileHash -LiteralPath $Contact -Algorithm SHA256).Hash.ToLowerInvariant()
        production_approved=$false
    }) $RunManifest 24

    Write-Host ''
    Write-Host 'G3S-B4C: VISUAL ADAPTATION REVIEW PACKAGE READY' -ForegroundColor Green
    Write-Host "CONTACT: $Contact"
    Write-Host "GENERATED: $generated"
    Write-Host 'STOP. Share the contact sheet. This output is visual-guide evidence only; no hair layer was promoted.' -ForegroundColor Yellow
}
catch {
    Write-Host ''
    Write-Host "G3S-B4C: FAIL - $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "STDOUT: $StdoutLog" -ForegroundColor DarkGray
    Write-Host "STDERR: $StderrLog" -ForegroundColor DarkGray
    exit 1
}
finally {
    if ($null -ne $proc -and -not $proc.HasExited) {
        Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
        try { $proc.WaitForExit(5000) | Out-Null } catch {}
    }
}
