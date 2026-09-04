param(
    [string]$Workspace = 'D:\AI\Flux2RefControlSpike',
    [int]$Port = 8200,
    [int]$PromptTimeoutSec = 1800,
    [long]$Seed = 20260904,
    [int]$Width = 768,
    [int]$Height = 1024,
    [int]$Steps = 20,
    [double]$Cfg = 5.0
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$PortableRoot = Join-Path $Workspace 'ComfyUI_windows_portable'
$ComfyRoot = Join-Path $PortableRoot 'ComfyUI'
$Python = Join-Path $PortableRoot 'python_embeded\python.exe'
$MainPy = Join-Path $ComfyRoot 'main.py'
$InputDir = Join-Path $ComfyRoot 'input'
$PoseDir = Join-Path $InputDir 'refcontrol_poses_v2'
$SpecDir = Join-Path $Workspace 'pose_specs_v2'
$ManifestInput = Join-Path $Workspace 'input_manifest_v2.json'
$LogDir = Join-Path $Workspace 'logs'
$RunDir = Join-Path $Workspace 'run_v2'
$RunManifestPath = Join-Path $RunDir 'step7_v2_run_manifest.json'
$RunStartedPath = Join-Path $RunDir 'step7_v2_started.json'
$StdoutLog = Join-Path $LogDir 'step7_v2_comfy_stdout.log'
$StderrLog = Join-Path $LogDir 'step7_v2_comfy_stderr.log'
$ApiRoot = "http://127.0.0.1:$Port"
$OutputRoot = Join-Path $ComfyRoot 'output'
$V2OutputDir = Join-Path $OutputRoot 'flux2_refcontrol_v2'
$ClientId = 'flux2-refcontrol-v2-20260904'

$UnetName = 'flux-2-klein-base-4b-fp8.safetensors'
$ClipName = 'qwen_3_4b.safetensors'
$VaeName = 'flux2-vae.safetensors'
$LoraName = 'refcontrol-pose-klein-4b.safetensors'
$MasterRel = 'exilada_master.png'

$ExpectedPoses = @(
    'pose_00_contact_L_v2',
    'pose_01_passing_L_v2',
    'pose_02_contact_R_v2',
    'pose_03_passing_R_v2'
)

$BasePrompt = @'
refcontrol, use image 1 as the exact pose skeleton and image 2 as the exact character reference. Preserve the same adult female character identity, face, long black hair silhouette, clothing, straps, chains, body proportions and modern detailed pixel-art visual language. Full body, side / south-east walking pose, crisp deliberate pixel clusters, no painterly rendering, no anti-aliased illustration. CORRECTION CONTRACT: keep the same exact lean body proportions and limb thickness in every frame. Preserve the exact shackle and chain topology visible in image 2: never swap a chain to the opposite anatomical wrist or ankle, never mirror the accessories, and keep each loose chain attached to the same anatomical side as the reference. Bare feet must be anatomically correct: five toes in correct order, heel behind toes, no reversed foot and no mirrored toes. The character walks toward screen-right; both bare feet and toes point toward screen-right. Keep the anatomical left arm and right arm coherent and visibly separated from the torso: no fused arm, hidden elbow, duplicated hand, impossible shoulder, or limb crossing through the body. Preserve the same scars and torn-cloth layout as closely as possible. Do not redesign the character.
'@

$PoseSuffix = @{
    'pose_00_contact_L_v2' = 'Contact phase: left leg is forward and contacting the ground, right leg trails behind. Keep both legs clearly separated and both feet oriented screen-right.'
    'pose_01_passing_L_v2' = 'Passing phase: right leg is the planted support leg; left leg is lifted and passing beneath the body. Keep the lifted foot readable and oriented screen-right.'
    'pose_02_contact_R_v2' = 'Opposite contact phase: right leg is forward and contacting the ground, left leg trails behind. Keep both legs clearly separated and both feet oriented screen-right.'
    'pose_03_passing_R_v2' = 'Opposite passing phase: left leg is the planted support leg; right leg is lifted and passing beneath the body. Keep the lifted foot readable and oriented screen-right.'
}

function Get-PropertyValue([object]$Object, [string]$Name) {
    if ($null -eq $Object) { return $null }
    $p = $Object.PSObject.Properties[$Name]
    if ($null -eq $p) { return $null }
    return $p.Value
}

function Save-Json([object]$Object, [string]$Path, [int]$Depth = 80) {
    $json = $Object | ConvertTo-Json -Depth $Depth
    [System.IO.File]::WriteAllText($Path, $json, [System.Text.UTF8Encoding]::new($false))
}

function Wait-ComfyReady([System.Diagnostics.Process]$Process, [string]$Api, [int]$TimeoutSec) {
    $deadline = (Get-Date).AddSeconds($TimeoutSec)
    while ((Get-Date) -lt $deadline) {
        if ($Process.HasExited) { throw "ComfyUI exited during startup with code $($Process.ExitCode). See $StdoutLog and $StderrLog" }
        try {
            $result = Invoke-RestMethod -Uri "$Api/object_info" -Method Get -TimeoutSec 5
            if ($result) { return $result }
        } catch { Start-Sleep -Milliseconds 750 }
    }
    throw "Timed out waiting for ComfyUI on $Api"
}

function Assert-Choice([object]$ObjectInfo, [string]$NodeName, [string]$InputName, [string]$Expected) {
    $nodeProp = $ObjectInfo.PSObject.Properties[$NodeName]
    if ($null -eq $nodeProp) { throw "Required ComfyUI node unavailable: $NodeName" }
    $input = Get-PropertyValue $nodeProp.Value 'input'
    $required = Get-PropertyValue $input 'required'
    $optional = Get-PropertyValue $input 'optional'
    $prop = $null
    if ($null -ne $required) { $prop = $required.PSObject.Properties[$InputName] }
    if ($null -eq $prop -and $null -ne $optional) { $prop = $optional.PSObject.Properties[$InputName] }
    if ($null -eq $prop) { throw "$NodeName does not expose input '$InputName'." }
    $definition = $prop.Value
    if ($definition -is [System.Array] -and $definition.Count -gt 0 -and $definition[0] -is [System.Array]) {
        if (@($definition[0]) -notcontains $Expected) { throw "$NodeName.$InputName does not offer expected value '$Expected'." }
    }
}

Write-Host ''
Write-Host 'FLUX.2 Klein + RefControl Pose - STEP 7B: V2 FOUR-POSE CORRECTION RUN' -ForegroundColor Cyan
Write-Host 'Controlled comparison against V1.' -ForegroundColor Yellow
Write-Host 'Unchanged: model, reference, seed, 768x1024, 20 steps, CFG 5.0, LoRA 1.0, Euler, one-shot/no-retry.' -ForegroundColor Yellow
Write-Host 'Changed: V2 skeleton geometry + anatomy/continuity prompt only.' -ForegroundColor Yellow
Write-Host ''

if ($Seed -ne 20260904) { throw "V2 contract requires seed 20260904. Got $Seed." }
if ($Width -ne 768 -or $Height -ne 1024) { throw "V2 contract requires 768x1024. Got ${Width}x${Height}." }
if ($Steps -ne 20) { throw "V2 contract requires 20 steps. Got $Steps." }
if ([math]::Abs($Cfg - 5.0) -gt 0.0001) { throw "V2 contract requires CFG 5.0. Got $Cfg." }

foreach ($p in @($Python, $MainPy, $ManifestInput, (Join-Path $InputDir $MasterRel))) {
    if (-not (Test-Path $p -PathType Leaf)) { throw "Missing required file: $p" }
}

$modelFiles = @(
    (Join-Path $ComfyRoot "models\diffusion_models\$UnetName"),
    (Join-Path $ComfyRoot "models\text_encoders\$ClipName"),
    (Join-Path $ComfyRoot "models\vae\$VaeName"),
    (Join-Path $ComfyRoot "models\loras\$LoraName")
)
foreach ($p in $modelFiles) { if (-not (Test-Path $p -PathType Leaf)) { throw "Missing model file: $p" } }

$inputManifestObject = Get-Content -LiteralPath $ManifestInput -Raw | ConvertFrom-Json
if ([string]$inputManifestObject.revision -ne 'v2_walk_anatomy_clarity') { throw 'Unexpected V2 input manifest revision.' }
if ([long]$inputManifestObject.seed_reserved_for_generation -ne $Seed) { throw 'V2 input manifest seed mismatch.' }

foreach ($name in $ExpectedPoses) {
    $png = Join-Path $PoseDir ($name + '.png')
    $json = Join-Path $SpecDir ($name + '.json')
    if (-not (Test-Path $png -PathType Leaf)) { throw "Missing V2 pose PNG: $png" }
    if (-not (Test-Path $json -PathType Leaf)) { throw "Missing V2 pose spec: $json" }
    $spec = Get-Content -LiteralPath $json -Raw | ConvertFrom-Json
    if ([string]$spec.pose_name -ne $name) { throw "${name}: pose spec name mismatch." }
    $hash = (Get-FileHash -LiteralPath $png -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($hash -ne ([string]$spec.png_sha256).ToLowerInvariant()) { throw "${name}: pose PNG hash mismatch." }
}

New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
New-Item -ItemType Directory -Force -Path $RunDir | Out-Null

if (Test-Path $RunStartedPath -PathType Leaf) { throw "V2 run-start sentinel already exists: $RunStartedPath. Refusing to risk a duplicate artistic submission." }
if (Test-Path $RunManifestPath -PathType Leaf) { throw "V2 run manifest already exists: $RunManifestPath. Refusing to create an artistic retry." }
if (Test-Path $V2OutputDir -PathType Container) {
    $existing = @(Get-ChildItem -LiteralPath $V2OutputDir -File -Filter '*.png' -ErrorAction SilentlyContinue)
    if ($existing.Count -gt 0) { throw "Existing V2 PNG outputs found in $V2OutputDir. Refusing to rerun." }
}

Remove-Item $StdoutLog, $StderrLog -Force -ErrorAction SilentlyContinue
$portBusy = $false
try { Invoke-RestMethod -Uri "$ApiRoot/object_info" -Method Get -TimeoutSec 2 | Out-Null; $portBusy = $true } catch { $portBusy = $false }
if ($portBusy) { throw "Port $Port is already in use by a ComfyUI-compatible endpoint. Refusing to reuse it." }

$args = @('-s', $MainPy, '--windows-standalone-build', '--listen', '127.0.0.1', '--port', [string]$Port, '--disable-auto-launch')
Write-Host "[START] Launching isolated ComfyUI on 127.0.0.1:$Port ..." -ForegroundColor Cyan
$proc = Start-Process -FilePath $Python -ArgumentList $args -WorkingDirectory $ComfyRoot -PassThru -RedirectStandardOutput $StdoutLog -RedirectStandardError $StderrLog

$records = @()
$runStarted = (Get-Date).ToString('o')
try {
    $objectInfo = Wait-ComfyReady $proc $ApiRoot 90
    Write-Host '[OK] ComfyUI ready.' -ForegroundColor Green

    foreach ($node in @('UNETLoader','LoraLoaderModelOnly','CLIPLoader','VAELoader','CLIPTextEncode','LoadImage','VAEEncode','ReferenceLatent','EmptyFlux2LatentImage','Flux2Scheduler','RandomNoise','KSamplerSelect','CFGGuider','SamplerCustomAdvanced','VAEDecode','SaveImage')) {
        if ($null -eq $objectInfo.PSObject.Properties[$node]) { throw "Runtime missing required node: $node" }
    }
    Assert-Choice $objectInfo 'UNETLoader' 'unet_name' $UnetName
    Assert-Choice $objectInfo 'CLIPLoader' 'clip_name' $ClipName
    Assert-Choice $objectInfo 'CLIPLoader' 'type' 'flux2'
    Assert-Choice $objectInfo 'VAELoader' 'vae_name' $VaeName
    Assert-Choice $objectInfo 'LoraLoaderModelOnly' 'lora_name' $LoraName
    Assert-Choice $objectInfo 'KSamplerSelect' 'sampler_name' 'euler'

    $startedRecord = [ordered]@{
        revision='v2_walk_anatomy_clarity'
        started_at=(Get-Date).ToString('o')
        seed=$Seed
        note='Sentinel written after runtime validation and immediately before the first possible /prompt submission. Presence means do not rerun automatically.'
    }
    Save-Json $startedRecord $RunStartedPath 20

    foreach ($name in $ExpectedPoses) {
        $poseRel = 'refcontrol_poses_v2/' + $name + '.png'
        $prefix = 'flux2_refcontrol_v2/' + $name
        $prompt = ($BasePrompt.Trim() + ' ' + [string]$PoseSuffix[$name]).Trim()

        $workflow = [ordered]@{
            '1' = @{ class_type='UNETLoader'; inputs=@{ unet_name=$UnetName; weight_dtype='default' } }
            '2' = @{ class_type='LoraLoaderModelOnly'; inputs=@{ model=@('1',0); lora_name=$LoraName; strength_model=1.0 } }
            '3' = @{ class_type='CLIPLoader'; inputs=@{ clip_name=$ClipName; type='flux2'; device='default' } }
            '4' = @{ class_type='VAELoader'; inputs=@{ vae_name=$VaeName } }
            '5' = @{ class_type='CLIPTextEncode'; inputs=@{ text=$prompt; clip=@('3',0) } }
            '6' = @{ class_type='CLIPTextEncode'; inputs=@{ text=''; clip=@('3',0) } }
            '7' = @{ class_type='LoadImage'; inputs=@{ image=$poseRel } }
            '8' = @{ class_type='VAEEncode'; inputs=@{ pixels=@('7',0); vae=@('4',0) } }
            '9' = @{ class_type='LoadImage'; inputs=@{ image=$MasterRel } }
            '10' = @{ class_type='VAEEncode'; inputs=@{ pixels=@('9',0); vae=@('4',0) } }
            '11' = @{ class_type='ReferenceLatent'; inputs=@{ conditioning=@('5',0); latent=@('8',0) } }
            '12' = @{ class_type='ReferenceLatent'; inputs=@{ conditioning=@('11',0); latent=@('10',0) } }
            '13' = @{ class_type='ReferenceLatent'; inputs=@{ conditioning=@('6',0); latent=@('8',0) } }
            '14' = @{ class_type='ReferenceLatent'; inputs=@{ conditioning=@('13',0); latent=@('10',0) } }
            '15' = @{ class_type='EmptyFlux2LatentImage'; inputs=@{ width=$Width; height=$Height; batch_size=1 } }
            '16' = @{ class_type='Flux2Scheduler'; inputs=@{ steps=$Steps; width=$Width; height=$Height } }
            '17' = @{ class_type='RandomNoise'; inputs=@{ noise_seed=$Seed } }
            '18' = @{ class_type='KSamplerSelect'; inputs=@{ sampler_name='euler' } }
            '19' = @{ class_type='CFGGuider'; inputs=@{ model=@('2',0); positive=@('12',0); negative=@('14',0); cfg=$Cfg } }
            '20' = @{ class_type='SamplerCustomAdvanced'; inputs=@{ noise=@('17',0); guider=@('19',0); sampler=@('18',0); sigmas=@('16',0); latent_image=@('15',0) } }
            '21' = @{ class_type='VAEDecode'; inputs=@{ samples=@('20',0); vae=@('4',0) } }
            '22' = @{ class_type='SaveImage'; inputs=@{ images=@('21',0); filename_prefix=$prefix } }
        }

        $requestObject = [ordered]@{ prompt=$workflow; client_id=$ClientId }
        $requestPath = Join-Path $RunDir ($name + '_request.json')
        Save-Json $requestObject $requestPath 100

        Write-Host ''
        Write-Host "[PROMPT] $name" -ForegroundColor Cyan
        Write-Host "         seed=$Seed"
        Write-Host '         attempt=1/1'
        $submittedAt = Get-Date
        $body = $requestObject | ConvertTo-Json -Depth 100 -Compress
        try {
            $submit = Invoke-RestMethod -Uri "$ApiRoot/prompt" -Method Post -ContentType 'application/json' -Body $body -TimeoutSec 30
        } catch {
            throw "${name}: /prompt submission failed and will NOT be retried. $($_.Exception.Message)"
        }
        $promptId = [string](Get-PropertyValue $submit 'prompt_id')
        if ([string]::IsNullOrWhiteSpace($promptId)) { throw "${name}: no prompt_id returned; no retry will be attempted." }

        $deadline = (Get-Date).AddSeconds($PromptTimeoutSec)
        $historyEntry = $null
        while ((Get-Date) -lt $deadline) {
            if ($proc.HasExited) { throw "${name}: ComfyUI exited during inference with code $($proc.ExitCode)." }
            try {
                $history = Invoke-RestMethod -Uri "$ApiRoot/history/$promptId" -Method Get -TimeoutSec 10
                $prop = $history.PSObject.Properties[$promptId]
                if ($null -ne $prop) {
                    $historyEntry = $prop.Value
                    if ((Get-PropertyValue (Get-PropertyValue $historyEntry 'status') 'completed') -eq $true) { break }
                }
            } catch {}
            Start-Sleep -Seconds 1
        }
        if ($null -eq $historyEntry) { throw "${name}: timed out; prompt will NOT be resubmitted." }

        $historyPath = Join-Path $RunDir ($name + '_history.json')
        Save-Json $historyEntry $historyPath 120
        $status = Get-PropertyValue $historyEntry 'status'
        $statusStr = [string](Get-PropertyValue $status 'status_str')
        if ((Get-PropertyValue $status 'completed') -ne $true -or $statusStr -ne 'success') { throw "${name}: status '$statusStr'; no retry." }

        $outputs = Get-PropertyValue $historyEntry 'outputs'
        $saveNodeProp = $outputs.PSObject.Properties['22']
        if ($null -eq $saveNodeProp) { throw "${name}: no SaveImage node 22 output." }
        $images = @(Get-PropertyValue $saveNodeProp.Value 'images')
        if ($images.Count -ne 1) { throw "${name}: expected one image, got $($images.Count)." }
        $filename = [string](Get-PropertyValue $images[0] 'filename')
        $subfolder = [string](Get-PropertyValue $images[0] 'subfolder')
        $outputPath = if ([string]::IsNullOrWhiteSpace($subfolder)) { Join-Path $OutputRoot $filename } else { Join-Path (Join-Path $OutputRoot $subfolder) $filename }
        if (-not (Test-Path $outputPath -PathType Leaf)) { throw "${name}: output missing: $outputPath" }

        $hash = (Get-FileHash -LiteralPath $outputPath -Algorithm SHA256).Hash.ToLowerInvariant()
        $elapsed = [math]::Round(((Get-Date)-$submittedAt).TotalSeconds, 2)
        $records += [pscustomobject][ordered]@{
            pose_name=$name
            pose_input=$poseRel
            prompt_id=$promptId
            prompt=$prompt
            seed=$Seed
            submission_attempts=1
            status=$statusStr
            elapsed_seconds=$elapsed
            output_path=$outputPath
            output_sha256=$hash
            request_json=$requestPath
            history_json=$historyPath
        }
        Write-Host "[OK] $name completed in $elapsed s" -ForegroundColor Green
        Write-Host "     output=$outputPath"
    }

    if ($records.Count -ne 4) { throw "Expected four completed V2 records, got $($records.Count)." }
    $manifest = [ordered]@{
        spike='FLUX.2 Klein Base 4B FP8 + RefControl Pose'
        revision='v2_walk_anatomy_clarity'
        stage='v2_four_pose_one_shot_complete_visual_qa_pending'
        started_at=$runStarted
        completed_at=(Get-Date).ToString('o')
        api=$ApiRoot
        seed=$Seed
        reference=$MasterRel
        unchanged_settings=@{ width=$Width; height=$Height; steps=$Steps; cfg=$Cfg; lora_strength=1.0; sampler='euler' }
        controlled_changes=@('V2 COCO-18 skeleton geometry','V2 anatomy/foot/chain continuity prompt')
        prompt_submissions_expected=4
        prompt_submissions_completed=$records.Count
        retry_policy='exactly one /prompt submission per pose; no artistic retry'
        outputs=$records
        visual_qa_performed=$false
        production_approved=$false
    }
    Save-Json $manifest $RunManifestPath 120

    Write-Host ''
    Write-Host 'STEP 7B: PASS' -ForegroundColor Green
    Write-Host 'Exactly four V2 one-shot generations completed.'
    Write-Host "Manifest: $RunManifestPath"
    Write-Host "Outputs:  $V2OutputDir"
    Write-Host 'Do not rerun. Next gate is V1-vs-V2 visual QA.' -ForegroundColor Yellow
}
finally {
    if ($null -ne $proc -and -not $proc.HasExited) {
        Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
        try { $proc.WaitForExit(5000) | Out-Null } catch {}
    }
}
