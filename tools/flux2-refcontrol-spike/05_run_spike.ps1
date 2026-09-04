param(
    [string]$Workspace = 'D:\AI\Flux2RefControlSpike',
    [int]$Port = 8199,
    [int]$PromptTimeoutSec = 1800,
    [long]$Seed = 20260904
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$PortableRoot = Join-Path $Workspace 'ComfyUI_windows_portable'
$ComfyRoot = Join-Path $PortableRoot 'ComfyUI'
$Python = Join-Path $PortableRoot 'python_embeded\python.exe'
$MainPy = Join-Path $ComfyRoot 'main.py'
$WorkflowPath = Join-Path $Workspace 'workflows\flux2_refcontrol_api_template.json'
$ContractPath = Join-Path $Workspace 'workflows\workflow_contract.json'
$LogDir = Join-Path $Workspace 'logs'
$RunDir = Join-Path $Workspace 'run'
$RunManifestPath = Join-Path $RunDir 'step6_run_manifest.json'
$StdoutLog = Join-Path $LogDir 'step6_comfy_stdout.log'
$StderrLog = Join-Path $LogDir 'step6_comfy_stderr.log'
$ApiRoot = "http://127.0.0.1:$Port"
$OutputRoot = Join-Path $ComfyRoot 'output'
$SpikeOutputDir = Join-Path $OutputRoot 'flux2_refcontrol_spike'
$ClientId = 'flux2-refcontrol-spike-20260904'

$ExpectedPoses = @(
    'pose_00_contact_L',
    'pose_01_passing_L',
    'pose_02_contact_R',
    'pose_03_passing_R'
)

function Get-PropertyValue([object]$Object, [string]$Name) {
    if ($null -eq $Object) { return $null }
    $p = $Object.PSObject.Properties[$Name]
    if ($null -eq $p) { return $null }
    return $p.Value
}

function Wait-ComfyReady([System.Diagnostics.Process]$Process, [string]$Api, [int]$TimeoutSec) {
    $deadline = (Get-Date).AddSeconds($TimeoutSec)
    while ((Get-Date) -lt $deadline) {
        if ($Process.HasExited) {
            throw "ComfyUI exited during startup with code $($Process.ExitCode). See $StdoutLog and $StderrLog"
        }
        try {
            $result = Invoke-RestMethod -Uri "$Api/object_info" -Method Get -TimeoutSec 5
            if ($result) { return }
        } catch {
            Start-Sleep -Milliseconds 750
        }
    }
    throw "Timed out waiting for ComfyUI on $Api"
}

function Save-Json([object]$Object, [string]$Path, [int]$Depth = 60) {
    $json = $Object | ConvertTo-Json -Depth $Depth
    [System.IO.File]::WriteAllText($Path, $json, [System.Text.UTF8Encoding]::new($false))
}

Write-Host ''
Write-Host 'FLUX.2 Klein + RefControl Pose spike - STEP 6: ONE-SHOT FOUR-POSE INFERENCE' -ForegroundColor Cyan
Write-Host 'This is the first inference stage.' -ForegroundColor Yellow
Write-Host 'Contract: exactly one /prompt submission per pose, sequentially, same seed, no artistic retry, no fallback, no parameter change.' -ForegroundColor Yellow
Write-Host ''

foreach ($p in @($Python, $MainPy, $WorkflowPath, $ContractPath)) {
    if (-not (Test-Path $p -PathType Leaf)) { throw "Missing required file: $p" }
}

New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
New-Item -ItemType Directory -Force -Path $RunDir | Out-Null

# One-shot guard. If any prior Step 6 artifact exists, stop rather than create an artistic retry.
if (Test-Path $RunManifestPath -PathType Leaf) {
    throw "Step 6 run manifest already exists: $RunManifestPath. Refusing to rerun the spike."
}
if (Test-Path $SpikeOutputDir -PathType Container) {
    $existingOutputs = @(Get-ChildItem -LiteralPath $SpikeOutputDir -File -Filter '*.png' -ErrorAction SilentlyContinue)
    if ($existingOutputs.Count -gt 0) {
        throw "Existing spike PNG outputs were found in $SpikeOutputDir. Refusing to rerun or overwrite them."
    }
}

$templateRaw = Get-Content -LiteralPath $WorkflowPath -Raw
$contract = Get-Content -LiteralPath $ContractPath -Raw | ConvertFrom-Json

if ([long]$contract.seed -ne $Seed) {
    throw "Workflow contract seed is $($contract.seed), expected $Seed"
}

# Validate immutable one-shot parameters directly from the template before starting ComfyUI.
$templateCheck = $templateRaw | ConvertFrom-Json
if ([long]$templateCheck.'17'.inputs.noise_seed -ne $Seed) { throw 'Template RandomNoise seed mismatch.' }
if ([double]$templateCheck.'2'.inputs.strength_model -ne 1.0) { throw 'Template RefControl LoRA strength changed from 1.0.' }
if ([string]$templateCheck.'9'.inputs.image -ne 'exilada_master.png') { throw 'Template canonical reference path changed.' }
if ([string]$templateCheck.'18'.inputs.sampler_name -ne 'euler') { throw 'Template sampler changed from Euler.' }

foreach ($name in $ExpectedPoses) {
    $posePath = Join-Path $ComfyRoot ("input\refcontrol_poses\" + $name + '.png')
    if (-not (Test-Path $posePath -PathType Leaf)) { throw "Missing pose input: $posePath" }
}

Remove-Item $StdoutLog, $StderrLog -Force -ErrorAction SilentlyContinue

$portBusy = $false
try {
    Invoke-RestMethod -Uri "$ApiRoot/object_info" -Method Get -TimeoutSec 2 | Out-Null
    $portBusy = $true
} catch {
    $portBusy = $false
}
if ($portBusy) {
    throw "Port $Port already serves a ComfyUI-compatible endpoint. This script will not reuse an unknown process."
}

$args = @(
    '-s',
    $MainPy,
    '--windows-standalone-build',
    '--listen', '127.0.0.1',
    '--port', [string]$Port,
    '--disable-auto-launch'
)

Write-Host "[START] Launching isolated ComfyUI inference server on 127.0.0.1:$Port ..." -ForegroundColor Cyan
$proc = Start-Process -FilePath $Python -ArgumentList $args -WorkingDirectory $ComfyRoot -PassThru -RedirectStandardOutput $StdoutLog -RedirectStandardError $StderrLog

$records = @()
$runStarted = (Get-Date).ToString('o')

try {
    Wait-ComfyReady $proc $ApiRoot 90
    Write-Host '[OK] ComfyUI is ready.' -ForegroundColor Green
    Write-Host '[INFO] No prompt has been submitted yet.' -ForegroundColor DarkGray

    foreach ($name in $ExpectedPoses) {
        $workflow = $templateRaw | ConvertFrom-Json
        $poseRel = 'refcontrol_poses/' + $name + '.png'
        $prefix = 'flux2_refcontrol_spike/' + $name

        # Only the pose image and output filename prefix vary across the four jobs.
        $workflow.'7'.inputs.image = $poseRel
        $workflow.'22'.inputs.filename_prefix = $prefix
        $workflow.'17'.inputs.noise_seed = $Seed

        if ([string]$workflow.'9'.inputs.image -ne 'exilada_master.png') { throw "${name}: canonical reference changed unexpectedly." }
        if ([long]$workflow.'17'.inputs.noise_seed -ne $Seed) { throw "${name}: seed changed unexpectedly." }

        $requestObject = [ordered]@{
            prompt = $workflow
            client_id = $ClientId
        }
        $requestPath = Join-Path $RunDir ($name + '_request.json')
        Save-Json $requestObject $requestPath 80

        Write-Host ''
        Write-Host "[PROMPT] $name" -ForegroundColor Cyan
        Write-Host "         pose=$poseRel"
        Write-Host "         seed=$Seed"
        Write-Host '         submission_attempt=1/1'

        $submittedAt = Get-Date
        $body = $requestObject | ConvertTo-Json -Depth 80 -Compress

        # IMPORTANT: this POST is intentionally not retried. If transport is ambiguous,
        # the spike stops to avoid accidentally submitting the same artistic generation twice.
        try {
            $submit = Invoke-RestMethod -Uri "$ApiRoot/prompt" -Method Post -ContentType 'application/json' -Body $body -TimeoutSec 30
        } catch {
            throw "${name}: /prompt submission failed. It will NOT be retried. $($_.Exception.Message)"
        }

        $promptId = [string](Get-PropertyValue $submit 'prompt_id')
        if ([string]::IsNullOrWhiteSpace($promptId)) {
            throw "${name}: ComfyUI accepted the POST response without a prompt_id. No retry will be attempted."
        }
        Write-Host "[ACCEPTED] prompt_id=$promptId" -ForegroundColor Green

        $deadline = (Get-Date).AddSeconds($PromptTimeoutSec)
        $historyEntry = $null
        while ((Get-Date) -lt $deadline) {
            if ($proc.HasExited) {
                throw "${name}: ComfyUI process exited during inference with code $($proc.ExitCode)."
            }

            try {
                $history = Invoke-RestMethod -Uri "$ApiRoot/history/$promptId" -Method Get -TimeoutSec 10
                $prop = $history.PSObject.Properties[$promptId]
                if ($null -ne $prop) {
                    $historyEntry = $prop.Value
                    $completed = Get-PropertyValue (Get-PropertyValue $historyEntry 'status') 'completed'
                    if ($completed -eq $true) { break }
                }
            } catch {
                # Polling is read-only and is not an inference retry. The /prompt request is never repeated.
            }
            Start-Sleep -Seconds 1
        }

        if ($null -eq $historyEntry) {
            throw "${name}: timed out waiting for ComfyUI history after prompt_id=$promptId. The prompt will NOT be resubmitted."
        }

        $historyPath = Join-Path $RunDir ($name + '_history.json')
        Save-Json $historyEntry $historyPath 100

        $status = Get-PropertyValue $historyEntry 'status'
        $statusStr = [string](Get-PropertyValue $status 'status_str')
        $completedFlag = Get-PropertyValue $status 'completed'
        if ($completedFlag -ne $true -or $statusStr -ne 'success') {
            throw "${name}: ComfyUI completed with status='$statusStr'. No retry and no next pose will be submitted. See $historyPath"
        }

        $outputs = Get-PropertyValue $historyEntry 'outputs'
        $saveNodeProp = $outputs.PSObject.Properties['22']
        if ($null -eq $saveNodeProp) { throw "${name}: history has no SaveImage node 22 output." }
        $images = @(Get-PropertyValue $saveNodeProp.Value 'images')
        if ($images.Count -ne 1) { throw "${name}: expected exactly one saved image, got $($images.Count)." }

        $filename = [string](Get-PropertyValue $images[0] 'filename')
        $subfolder = [string](Get-PropertyValue $images[0] 'subfolder')
        if ([string]::IsNullOrWhiteSpace($filename)) { throw "${name}: saved image filename is empty." }

        $outputPath = if ([string]::IsNullOrWhiteSpace($subfolder)) {
            Join-Path $OutputRoot $filename
        } else {
            Join-Path (Join-Path $OutputRoot $subfolder) $filename
        }
        if (-not (Test-Path $outputPath -PathType Leaf)) { throw "${name}: reported output file is missing: $outputPath" }

        $hash = (Get-FileHash -LiteralPath $outputPath -Algorithm SHA256).Hash.ToLowerInvariant()
        $elapsed = [math]::Round(((Get-Date) - $submittedAt).TotalSeconds, 2)

        $record = [ordered]@{
            pose_name = $name
            pose_input = $poseRel
            prompt_id = $promptId
            seed = $Seed
            submission_attempts = 1
            status = $statusStr
            elapsed_seconds = $elapsed
            output_path = $outputPath
            output_sha256 = $hash
            request_json = $requestPath
            history_json = $historyPath
        }
        $records += [pscustomobject]$record

        Write-Host "[OK] $name completed in $elapsed s" -ForegroundColor Green
        Write-Host "     output=$outputPath"
        Write-Host "     sha256=$hash"
    }

    if ($records.Count -ne 4) { throw "Expected four completed records, got $($records.Count)." }

    $manifest = [ordered]@{
        spike = 'FLUX.2 Klein Base 4B FP8 + RefControl Pose'
        stage = 'four_pose_one_shot_inference_complete_visual_qa_pending'
        started_at = $runStarted
        completed_at = (Get-Date).ToString('o')
        api = $ApiRoot
        seed = $Seed
        reference = 'exilada_master.png'
        prompt_submissions_expected = 4
        prompt_submissions_completed = $records.Count
        retry_policy = 'no artistic retry; exactly one /prompt submission per pose'
        outputs = $records
        visual_qa_performed = $false
        production_approved = $false
    }
    Save-Json $manifest $RunManifestPath 100

    Write-Host ''
    Write-Host 'STEP 6: PASS' -ForegroundColor Green
    Write-Host 'Exactly four one-shot pose generations completed.'
    Write-Host "Run manifest: $RunManifestPath"
    Write-Host "Outputs: $SpikeOutputDir"
    Write-Host 'No visual QA, interpolation, video generation, inpainting, seed fishing, or second attempt was performed.' -ForegroundColor Green
}
finally {
    if ($null -ne $proc -and -not $proc.HasExited) {
        Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
        try { $proc.WaitForExit(5000) | Out-Null } catch {}
    }
}
