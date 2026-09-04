param(
    [string]$Workspace = 'D:\AI\Flux2RefControlSpike',
    [int]$Port = 8191
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$PortableRoot = Join-Path $Workspace 'ComfyUI_windows_portable'
$ComfyRoot = Join-Path $PortableRoot 'ComfyUI'
$Python = Join-Path $PortableRoot 'python_embeded\python.exe'
$ComfyMain = Join-Path $ComfyRoot 'main.py'
$PoseDir = Join-Path $ComfyRoot 'input\refcontrol_poses'
$PoseSpecDir = Join-Path $Workspace 'pose_specs'
$ManifestPath = Join-Path $Workspace 'input_manifest.json'
$SchemaDir = Join-Path $Workspace 'schema'
$SchemaPath = Join-Path $SchemaDir 'required_object_info.json'
$SummaryPath = Join-Path $SchemaDir 'runtime_schema_summary.txt'
$StdoutLog = Join-Path $SchemaDir 'comfy_schema_probe.stdout.log'
$StderrLog = Join-Path $SchemaDir 'comfy_schema_probe.stderr.log'

$ExpectedPoses = @(
    'pose_00_contact_L',
    'pose_01_passing_L',
    'pose_02_contact_R',
    'pose_03_passing_R'
)

$RequiredNodes = @(
    'LoadImage',
    'UNETLoader',
    'CLIPLoader',
    'VAELoader',
    'LoraLoaderModelOnly',
    'VAEEncode',
    'ReferenceLatent',
    'CLIPTextEncode',
    'EmptyFlux2LatentImage',
    'Flux2Scheduler',
    'KSamplerSelect',
    'CFGGuider',
    'RandomNoise',
    'SamplerCustomAdvanced',
    'VAEDecode',
    'SaveImage'
)

$ExpectedModels = [ordered]@{
    UNETLoader = [ordered]@{
        input = 'unet_name'
        file = 'flux-2-klein-base-4b-fp8.safetensors'
    }
    CLIPLoader = [ordered]@{
        input = 'clip_name'
        file = 'qwen_3_4b.safetensors'
    }
    VAELoader = [ordered]@{
        input = 'vae_name'
        file = 'flux2-vae.safetensors'
    }
    LoraLoaderModelOnly = [ordered]@{
        input = 'lora_name'
        file = 'refcontrol-pose-klein-4b.safetensors'
    }
}

function Get-DynamicPropertyValue {
    param(
        [Parameter(Mandatory=$true)]$Object,
        [Parameter(Mandatory=$true)][string]$Name
    )
    if ($null -eq $Object) { return $null }
    $p = $Object.PSObject.Properties[$Name]
    if ($null -eq $p) { return $null }
    return $p.Value
}

function Get-ChoiceList {
    param(
        [Parameter(Mandatory=$true)]$ObjectInfo,
        [Parameter(Mandatory=$true)][string]$NodeName,
        [Parameter(Mandatory=$true)][string]$InputName
    )
    $node = Get-DynamicPropertyValue -Object $ObjectInfo -Name $NodeName
    if ($null -eq $node) { return @() }
    $input = Get-DynamicPropertyValue -Object $node -Name 'input'
    $required = Get-DynamicPropertyValue -Object $input -Name 'required'
    $spec = Get-DynamicPropertyValue -Object $required -Name $InputName
    if ($null -eq $spec) { return @() }

    # ComfyUI object_info usually encodes a combo as: [ [choice1, choice2, ...], {options...} ]
    if ($spec -is [System.Array] -and $spec.Count -gt 0) {
        $first = $spec[0]
        if ($first -is [System.Array]) { return @($first) }
        if ($first -is [System.Collections.IEnumerable] -and -not ($first -is [string])) { return @($first) }
    }
    return @()
}

Write-Host ''
Write-Host 'FLUX.2 Klein + RefControl Pose spike - STEP 5: runtime/schema validation only' -ForegroundColor Cyan
Write-Host 'This step validates the four deterministic skeleton specs, starts ComfyUI headless on localhost,'
Write-Host 'queries GET /object_info, validates required core nodes/model filenames, saves the schema subset, and stops.'
Write-Host 'NO /prompt request is sent. NO inference is performed.'
Write-Host ''

if (-not (Test-Path $Python -PathType Leaf)) { throw "Embedded Python not found: $Python" }
if (-not (Test-Path $ComfyMain -PathType Leaf)) { throw "ComfyUI main.py not found: $ComfyMain" }
if (-not (Test-Path $ManifestPath -PathType Leaf)) { throw "Input manifest not found: $ManifestPath" }

New-Item -ItemType Directory -Force -Path $SchemaDir | Out-Null

Write-Host '[CHECK] Deterministic pose specs...' -ForegroundColor Cyan
$poseHashes = @()
foreach ($poseName in $ExpectedPoses) {
    $png = Join-Path $PoseDir ($poseName + '.png')
    $json = Join-Path $PoseSpecDir ($poseName + '.json')
    if (-not (Test-Path $png -PathType Leaf)) { throw "Missing pose PNG: $png" }
    if (-not (Test-Path $json -PathType Leaf)) { throw "Missing pose JSON: $json" }

    $spec = Get-Content -LiteralPath $json -Raw | ConvertFrom-Json
    if ($spec.format -ne 'openpose_coco18') { throw "$poseName has unexpected format: $($spec.format)" }
    if ($spec.pose_name -ne $poseName) { throw "$poseName JSON pose_name mismatch: $($spec.pose_name)" }
    if (@($spec.keypoints_normalized).Count -ne 18) { throw "$poseName must contain exactly 18 normalized keypoints" }
    if (@($spec.keypoints_pixels).Count -ne 18) { throw "$poseName must contain exactly 18 pixel keypoints" }

    foreach ($kp in @($spec.keypoints_normalized)) {
        $x = [double]$kp.x
        $y = [double]$kp.y
        if ($x -lt 0.0 -or $x -gt 1.0 -or $y -lt 0.0 -or $y -gt 1.0) {
            throw "$poseName contains an out-of-range normalized keypoint: $($kp.label) x=$x y=$y"
        }
    }

    $actualHash = (Get-FileHash -LiteralPath $png -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($actualHash -ne ([string]$spec.png_sha256).ToLowerInvariant()) {
        throw "$poseName PNG SHA256 does not match its JSON spec"
    }
    $poseHashes += $actualHash
    Write-Host "[OK] $poseName - 18 keypoints; sha256=$actualHash" -ForegroundColor Green
}

if (@($poseHashes | Select-Object -Unique).Count -ne 4) {
    throw 'The four pose PNGs are not four distinct deterministic renders.'
}
Write-Host '[OK] Four structurally valid and distinct COCO-18 pose renders.' -ForegroundColor Green

# Use a dedicated probe port and fail rather than attaching to an unrelated existing process.
$existing = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
if ($existing) {
    throw "Local port $Port is already in use. Stop the existing listener or rerun with -Port <free_port>."
}

Remove-Item $StdoutLog, $StderrLog -Force -ErrorAction SilentlyContinue

$arguments = @(
    '-s',
    $ComfyMain,
    '--windows-standalone-build',
    '--listen', '127.0.0.1',
    '--port', [string]$Port,
    '--disable-auto-launch'
)

Write-Host ''
Write-Host "[START] ComfyUI headless schema probe on 127.0.0.1:$Port ..." -ForegroundColor Cyan
$server = Start-Process -FilePath $Python -ArgumentList $arguments -PassThru -RedirectStandardOutput $StdoutLog -RedirectStandardError $StderrLog

try {
    $baseUrl = "http://127.0.0.1:$Port"
    $objectInfo = $null
    $deadline = (Get-Date).AddSeconds(120)

    while ((Get-Date) -lt $deadline) {
        if ($server.HasExited) {
            $stdoutTail = if (Test-Path $StdoutLog) { (Get-Content $StdoutLog -Tail 40) -join [Environment]::NewLine } else { '' }
            $stderrTail = if (Test-Path $StderrLog) { (Get-Content $StderrLog -Tail 40) -join [Environment]::NewLine } else { '' }
            throw "ComfyUI exited before /object_info became available.`nSTDOUT:`n$stdoutTail`nSTDERR:`n$stderrTail"
        }

        try {
            $objectInfo = Invoke-RestMethod -Uri ($baseUrl + '/object_info') -Method Get -TimeoutSec 5
            if ($null -ne $objectInfo) { break }
        } catch {
            Start-Sleep -Milliseconds 750
        }
    }

    if ($null -eq $objectInfo) {
        throw 'Timed out waiting for ComfyUI GET /object_info. No inference was attempted.'
    }
    Write-Host '[OK] GET /object_info responded.' -ForegroundColor Green

    Write-Host ''
    Write-Host '[CHECK] Required core nodes...' -ForegroundColor Cyan
    $selectedNodes = [ordered]@{}
    foreach ($nodeName in $RequiredNodes) {
        $node = Get-DynamicPropertyValue -Object $objectInfo -Name $nodeName
        if ($null -eq $node) { throw "Required ComfyUI node is missing: $nodeName" }
        $selectedNodes[$nodeName] = $node
        Write-Host "[OK] node: $nodeName" -ForegroundColor Green
    }

    Write-Host ''
    Write-Host '[CHECK] Required model filenames are visible to their loaders...' -ForegroundColor Cyan
    foreach ($nodeName in $ExpectedModels.Keys) {
        $inputName = [string]$ExpectedModels[$nodeName].input
        $fileName = [string]$ExpectedModels[$nodeName].file
        $choices = @(Get-ChoiceList -ObjectInfo $objectInfo -NodeName $nodeName -InputName $inputName)
        if ($choices.Count -eq 0) {
            throw "Could not read combo choices for $nodeName.$inputName from /object_info"
        }
        if ($choices -notcontains $fileName) {
            throw "$nodeName does not list expected file '$fileName'"
        }
        Write-Host "[OK] $nodeName.$inputName -> $fileName" -ForegroundColor Green
    }

    $clipTypes = @(Get-ChoiceList -ObjectInfo $objectInfo -NodeName 'CLIPLoader' -InputName 'type')
    if ($clipTypes.Count -eq 0 -or $clipTypes -notcontains 'flux2') {
        throw "CLIPLoader does not expose required type 'flux2'. Found: $($clipTypes -join ', ')"
    }
    Write-Host "[OK] CLIPLoader type includes 'flux2'." -ForegroundColor Green

    # Save only the subset needed to construct the workflow; avoid a giant full object_info dump.
    $schemaRecord = [ordered]@{
        stage = 'runtime_schema_validated_no_inference'
        timestamp_utc = (Get-Date).ToUniversalTime().ToString('o')
        comfy_url = $baseUrl
        prompt_requests_sent = 0
        inference_performed = $false
        expected_control_order = @('image_1=skeleton', 'image_2=reference')
        expected_seed = 20260904
        required_nodes = $selectedNodes
        model_files = $ExpectedModels
    }
    $schemaJson = $schemaRecord | ConvertTo-Json -Depth 100
    [System.IO.File]::WriteAllText($SchemaPath, $schemaJson, [System.Text.UTF8Encoding]::new($false))

    $summaryLines = @(
        'FLUX.2 Klein + RefControl Pose runtime schema validation',
        'stage=runtime_schema_validated_no_inference',
        'prompt_requests_sent=0',
        'inference_performed=false',
        'control_order=image_1_skeleton,image_2_reference',
        'seed=20260904',
        ('nodes=' + ($RequiredNodes -join ',')),
        'unet=flux-2-klein-base-4b-fp8.safetensors',
        'clip=qwen_3_4b.safetensors',
        'clip_type=flux2',
        'vae=flux2-vae.safetensors',
        'lora=refcontrol-pose-klein-4b.safetensors'
    )
    [System.IO.File]::WriteAllLines($SummaryPath, $summaryLines, [System.Text.UTF8Encoding]::new($false))

    Write-Host ''
    Write-Host "[OK] Schema subset saved: $SchemaPath" -ForegroundColor Green
    Write-Host "[OK] Summary saved:       $SummaryPath" -ForegroundColor Green
}
finally {
    if ($null -ne $server -and -not $server.HasExited) {
        Write-Host ''
        Write-Host '[STOP] Stopping temporary ComfyUI schema-probe process...' -ForegroundColor Cyan
        Stop-Process -Id $server.Id -Force -ErrorAction SilentlyContinue
        try { Wait-Process -Id $server.Id -Timeout 10 -ErrorAction SilentlyContinue } catch {}
    }
}

Write-Host ''
Write-Host 'STEP 5: PASS' -ForegroundColor Green
Write-Host 'Runtime/schema is sufficient to construct the two-reference FLUX.2 + RefControl workflow.'
Write-Host 'No /prompt POST was made. No generation or inference was performed.' -ForegroundColor Green
