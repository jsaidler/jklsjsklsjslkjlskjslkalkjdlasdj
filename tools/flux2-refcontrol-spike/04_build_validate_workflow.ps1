param(
    [string]$Workspace = 'D:\AI\Flux2RefControlSpike',
    [int]$Port = 8199,
    [int]$Width = 768,
    [int]$Height = 1024,
    [int]$Steps = 20,
    [double]$Cfg = 5.0,
    [long]$Seed = 20260904
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$PortableRoot = Join-Path $Workspace 'ComfyUI_windows_portable'
$ComfyRoot = Join-Path $PortableRoot 'ComfyUI'
$Python = Join-Path $PortableRoot 'python_embeded\python.exe'
$MainPy = Join-Path $ComfyRoot 'main.py'
$InputDir = Join-Path $ComfyRoot 'input'
$PoseDir = Join-Path $InputDir 'refcontrol_poses'
$SpecDir = Join-Path $Workspace 'pose_specs'
$WorkflowDir = Join-Path $Workspace 'workflows'
$LogDir = Join-Path $Workspace 'logs'
$WorkflowPath = Join-Path $WorkflowDir 'flux2_refcontrol_api_template.json'
$ContractPath = Join-Path $WorkflowDir 'workflow_contract.json'
$StdoutLog = Join-Path $LogDir 'step5_comfy_stdout.log'
$StderrLog = Join-Path $LogDir 'step5_comfy_stderr.log'
$ApiRoot = "http://127.0.0.1:$Port"

$UnetName = 'flux-2-klein-base-4b-fp8.safetensors'
$ClipName = 'qwen_3_4b.safetensors'
$VaeName = 'flux2-vae.safetensors'
$LoraName = 'refcontrol-pose-klein-4b.safetensors'
$MasterRel = 'exilada_master.png'
$PoseRel = 'refcontrol_poses/pose_00_contact_L.png'

$Prompt = 'refcontrol, use image 1 as the exact pose skeleton and image 2 as the exact character reference. Preserve the same adult female character identity, face, long black hair silhouette, clothing, straps, chains, body proportions and modern detailed pixel-art visual language. Full body, side / south-east walking pose, crisp deliberate pixel clusters, no painterly rendering, no anti-aliased illustration.'
$NegativePrompt = ''

$ExpectedPoses = @(
    'pose_00_contact_L',
    'pose_01_passing_L',
    'pose_02_contact_R',
    'pose_03_passing_R'
)

function Get-Node([object]$ObjectInfo, [string]$Name) {
    $p = $ObjectInfo.PSObject.Properties[$Name]
    if ($null -eq $p) { throw "Required ComfyUI node is unavailable: $Name" }
    return $p.Value
}

function Get-InputNames([object]$NodeInfo) {
    $names = @()
    if ($NodeInfo.input -and $NodeInfo.input.required) {
        $names += @($NodeInfo.input.required.PSObject.Properties.Name)
    }
    if ($NodeInfo.input -and $NodeInfo.input.optional) {
        $names += @($NodeInfo.input.optional.PSObject.Properties.Name)
    }
    return @($names | Select-Object -Unique)
}

function Get-RequiredInputNames([object]$NodeInfo) {
    if ($NodeInfo.input -and $NodeInfo.input.required) {
        return @($NodeInfo.input.required.PSObject.Properties.Name)
    }
    return @()
}

function Assert-Choice([object]$ObjectInfo, [string]$NodeName, [string]$InputName, [string]$Expected) {
    $node = Get-Node $ObjectInfo $NodeName
    $prop = $node.input.required.PSObject.Properties[$InputName]
    if ($null -eq $prop -and $node.input.optional) {
        $prop = $node.input.optional.PSObject.Properties[$InputName]
    }
    if ($null -eq $prop) { throw "$NodeName does not expose input '$InputName'." }

    $definition = $prop.Value
    if ($definition -is [System.Array] -and $definition.Count -gt 0 -and $definition[0] -is [System.Array]) {
        $choices = @($definition[0])
        if ($choices -notcontains $Expected) {
            throw "$NodeName.$InputName does not offer expected value '$Expected'."
        }
    }
}

function Assert-WorkflowSchema([object]$ObjectInfo, [hashtable]$Workflow) {
    foreach ($entry in $Workflow.GetEnumerator()) {
        $id = [string]$entry.Key
        $nodeDef = $entry.Value
        $classType = [string]$nodeDef.class_type
        $nodeInfo = Get-Node $ObjectInfo $classType
        $allowed = @(Get-InputNames $nodeInfo)
        $required = @(Get-RequiredInputNames $nodeInfo)
        $actual = @($nodeDef.inputs.Keys)

        foreach ($name in $actual) {
            if ($allowed -notcontains $name) {
                throw "Workflow node $id ($classType) uses unknown input '$name'."
            }
        }
        foreach ($name in $required) {
            if ($actual -notcontains $name) {
                throw "Workflow node $id ($classType) is missing required input '$name'."
            }
        }
    }
}

Write-Host ''
Write-Host 'FLUX.2 Klein + RefControl Pose spike - STEP 5: build + validate workflow only' -ForegroundColor Cyan
Write-Host 'This step validates inputs, starts ComfyUI locally, queries /object_info, builds an API workflow, and validates it against the live node schemas.'
Write-Host 'NO /prompt request is sent. NO model is loaded for inference. NO image is generated.'
Write-Host ''

foreach ($p in @($Python, $MainPy)) {
    if (-not (Test-Path $p -PathType Leaf)) { throw "Missing runtime file: $p" }
}

$modelFiles = @(
    (Join-Path $ComfyRoot "models\diffusion_models\$UnetName"),
    (Join-Path $ComfyRoot "models\text_encoders\$ClipName"),
    (Join-Path $ComfyRoot "models\vae\$VaeName"),
    (Join-Path $ComfyRoot "models\loras\$LoraName")
)
foreach ($p in $modelFiles) {
    if (-not (Test-Path $p -PathType Leaf)) { throw "Missing required model file: $p" }
}
Write-Host '[OK] Four required model files are present.' -ForegroundColor Green

$MasterPath = Join-Path $InputDir $MasterRel
if (-not (Test-Path $MasterPath -PathType Leaf)) { throw "Missing copied Exilada master: $MasterPath" }

foreach ($name in $ExpectedPoses) {
    $png = Join-Path $PoseDir ($name + '.png')
    $json = Join-Path $SpecDir ($name + '.json')
    if (-not (Test-Path $png -PathType Leaf)) { throw "Missing pose PNG: $png" }
    if (-not (Test-Path $json -PathType Leaf)) { throw "Missing pose spec: $json" }

    $spec = Get-Content -LiteralPath $json -Raw | ConvertFrom-Json
    if ($spec.format -ne 'openpose_coco18') { throw "$name: unexpected pose format '$($spec.format)'" }
    if ($spec.pose_name -ne $name) { throw "$name: pose_name mismatch in JSON" }
    if (@($spec.keypoints_normalized).Count -ne 18) { throw "$name: expected 18 normalized keypoints" }
    if (@($spec.keypoints_pixels).Count -ne 18) { throw "$name: expected 18 pixel keypoints" }
    if ([int]$spec.canvas[0] -ne $Width -or [int]$spec.canvas[1] -ne $Height) {
        throw "$name: expected canvas ${Width}x${Height}, got $($spec.canvas[0])x$($spec.canvas[1])"
    }
    foreach ($kp in @($spec.keypoints_normalized)) {
        if ([double]$kp.x -lt 0.0 -or [double]$kp.x -gt 1.0 -or [double]$kp.y -lt 0.0 -or [double]$kp.y -gt 1.0) {
            throw "$name: keypoint '$($kp.label)' is outside normalized canvas"
        }
    }
    $actualHash = (Get-FileHash -LiteralPath $png -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($actualHash -ne ([string]$spec.png_sha256).ToLowerInvariant()) {
        throw "$name: PNG hash no longer matches its pose spec"
    }
}
Write-Host '[OK] Four deterministic COCO-18 skeletons validate structurally and by SHA-256.' -ForegroundColor Green

New-Item -ItemType Directory -Force -Path $WorkflowDir | Out-Null
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
Remove-Item $StdoutLog, $StderrLog -Force -ErrorAction SilentlyContinue

# Refuse to reuse an unknown service already bound to the dedicated validation port.
$portBusy = $false
try {
    Invoke-RestMethod -Uri "$ApiRoot/object_info" -Method Get -TimeoutSec 2 | Out-Null
    $portBusy = $true
} catch {
    $portBusy = $false
}
if ($portBusy) { throw "Port $Port already serves a ComfyUI-compatible endpoint. Stop it or choose another port; this script will not reuse an unknown process." }

$args = @(
    '-s',
    $MainPy,
    '--windows-standalone-build',
    '--listen', '127.0.0.1',
    '--port', [string]$Port,
    '--disable-auto-launch'
)

Write-Host "[START] Launching isolated ComfyUI validation server on 127.0.0.1:$Port ..." -ForegroundColor Cyan
$proc = Start-Process -FilePath $Python -ArgumentList $args -WorkingDirectory $ComfyRoot -PassThru -RedirectStandardOutput $StdoutLog -RedirectStandardError $StderrLog

try {
    $objectInfo = $null
    $deadline = (Get-Date).AddSeconds(90)
    while ((Get-Date) -lt $deadline) {
        if ($proc.HasExited) {
            throw "ComfyUI exited during startup with code $($proc.ExitCode). See $StdoutLog and $StderrLog"
        }
        try {
            $objectInfo = Invoke-RestMethod -Uri "$ApiRoot/object_info" -Method Get -TimeoutSec 5
            if ($objectInfo) { break }
        } catch {
            Start-Sleep -Milliseconds 750
        }
    }
    if (-not $objectInfo) { throw "Timed out waiting for ComfyUI /object_info. See logs in $LogDir" }
    Write-Host '[OK] ComfyUI /object_info is reachable.' -ForegroundColor Green

    $requiredNodes = @(
        'UNETLoader','LoraLoaderModelOnly','CLIPLoader','VAELoader',
        'CLIPTextEncode','LoadImage','VAEEncode','ReferenceLatent',
        'EmptyFlux2LatentImage','Flux2Scheduler','RandomNoise','KSamplerSelect',
        'CFGGuider','SamplerCustomAdvanced','VAEDecode','SaveImage'
    )
    foreach ($name in $requiredNodes) { Get-Node $objectInfo $name | Out-Null }
    Write-Host "[OK] Required core node set is present ($($requiredNodes.Count) nodes)." -ForegroundColor Green

    Assert-Choice $objectInfo 'UNETLoader' 'unet_name' $UnetName
    Assert-Choice $objectInfo 'CLIPLoader' 'clip_name' $ClipName
    Assert-Choice $objectInfo 'CLIPLoader' 'type' 'flux2'
    Assert-Choice $objectInfo 'VAELoader' 'vae_name' $VaeName
    Assert-Choice $objectInfo 'LoraLoaderModelOnly' 'lora_name' $LoraName
    Assert-Choice $objectInfo 'KSamplerSelect' 'sampler_name' 'euler'
    Write-Host '[OK] Live ComfyUI schemas expose the exact FLUX.2/Klein files, flux2 text-encoder type, RefControl LoRA and Euler sampler.' -ForegroundColor Green

    # API-format graph. Reference order is intentionally fixed:
    #   image 1 = pose skeleton
    #   image 2 = canonical Exilada reference
    # The same ordered reference latents are attached to positive and negative conditioning.
    $workflow = [ordered]@{
        '1' = @{ class_type='UNETLoader'; inputs=@{ unet_name=$UnetName; weight_dtype='default' } }
        '2' = @{ class_type='LoraLoaderModelOnly'; inputs=@{ model=@('1',0); lora_name=$LoraName; strength_model=1.0 } }
        '3' = @{ class_type='CLIPLoader'; inputs=@{ clip_name=$ClipName; type='flux2'; device='default' } }
        '4' = @{ class_type='VAELoader'; inputs=@{ vae_name=$VaeName } }
        '5' = @{ class_type='CLIPTextEncode'; inputs=@{ text=$Prompt; clip=@('3',0) } }
        '6' = @{ class_type='CLIPTextEncode'; inputs=@{ text=$NegativePrompt; clip=@('3',0) } }
        '7' = @{ class_type='LoadImage'; inputs=@{ image=$PoseRel } }
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
        '22' = @{ class_type='SaveImage'; inputs=@{ images=@('21',0); filename_prefix='flux2_refcontrol_spike/pose_00_contact_L' } }
    }

    Assert-WorkflowSchema $objectInfo $workflow
    Write-Host '[OK] API workflow inputs match the live ComfyUI node schemas.' -ForegroundColor Green

    $workflowJson = $workflow | ConvertTo-Json -Depth 30
    [System.IO.File]::WriteAllText($WorkflowPath, $workflowJson, [System.Text.UTF8Encoding]::new($false))

    $contract = [ordered]@{
        spike = 'FLUX.2 Klein Base 4B FP8 + RefControl Pose'
        stage = 'workflow_built_and_schema_validated_no_inference'
        comfy_api = $ApiRoot
        reference_order = @('image1: OpenPose COCO-18 skeleton', 'image2: canonical exilada_master.png')
        seed = $Seed
        width = $Width
        height = $Height
        steps = $Steps
        cfg = $Cfg
        sampler = 'euler'
        lora_strength_model = 1.0
        prompt = $Prompt
        negative_prompt = $NegativePrompt
        generation_policy = 'one render per each of four predetermined poses; same seed and settings; zero artistic retries'
        queued_to_prompt_endpoint = $false
        inference_performed = $false
        video = $false
        interpolation = $false
        pixel_art_lora = $false
    }
    [System.IO.File]::WriteAllText($ContractPath, ($contract | ConvertTo-Json -Depth 10), [System.Text.UTF8Encoding]::new($false))

    Write-Host '[OK] Workflow template written:' -ForegroundColor Green
    Write-Host "     $WorkflowPath"
    Write-Host '[OK] Workflow contract written:' -ForegroundColor Green
    Write-Host "     $ContractPath"
    Write-Host ''
    Write-Host 'STEP 5: PASS' -ForegroundColor Green
    Write-Host 'No /prompt request was sent. No inference was performed.' -ForegroundColor Green
}
finally {
    if ($proc -and -not $proc.HasExited) {
        Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
        Start-Sleep -Milliseconds 300
    }
}
