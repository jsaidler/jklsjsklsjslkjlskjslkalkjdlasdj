param(
    [string]$Workspace = 'D:\AI\Flux2RefControlSpike'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$Port = 8188
$HostAddress = '127.0.0.1'
$BaseUrl = "http://${HostAddress}:$Port"

$PortableRoot = Join-Path $Workspace 'ComfyUI_windows_portable'
$ComfyRoot = Join-Path $PortableRoot 'ComfyUI'
$Python = Join-Path $PortableRoot 'python_embeded\python.exe'
$ComfyMain = Join-Path $ComfyRoot 'main.py'
$InputDir = Join-Path $ComfyRoot 'input'

$SchemaDir = Join-Path $Workspace 'runtime_schema'
$FullSchemaPath = Join-Path $SchemaDir 'object_info.full.json'
$ReducedSchemaPath = Join-Path $SchemaDir 'object_info.required.json'
$ReportJsonPath = Join-Path $SchemaDir 'step5_runtime_schema_report.json'
$ReportTextPath = Join-Path $SchemaDir 'step5_runtime_schema_report.txt'
$StdoutLog = Join-Path $SchemaDir 'comfy_step5.stdout.log'
$StderrLog = Join-Path $SchemaDir 'comfy_step5.stderr.log'

$ExpectedModelContracts = @(
    [pscustomobject]@{ role='diffusion_model'; node='UNETLoader'; input='unet_name'; file='flux-2-klein-base-4b-fp8.safetensors' },
    [pscustomobject]@{ role='text_encoder'; node='CLIPLoader'; input='clip_name'; file='qwen_3_4b.safetensors' },
    [pscustomobject]@{ role='vae'; node='VAELoader'; input='vae_name'; file='flux2-vae.safetensors' },
    [pscustomobject]@{ role='refcontrol_pose_lora'; node='LoraLoaderModelOnly'; input='lora_name'; file='refcontrol-pose-klein-4b.safetensors' }
)

$ExpectedInputFiles = @(
    'exilada_master.png',
    'refcontrol_poses/pose_00_contact_L.png',
    'refcontrol_poses/pose_01_passing_L.png',
    'refcontrol_poses/pose_02_contact_R.png',
    'refcontrol_poses/pose_03_passing_R.png'
)

$RequiredCoreNodes = @(
    'UNETLoader',
    'CLIPLoader',
    'VAELoader',
    'LoraLoaderModelOnly',
    'LoadImage',
    'VAEEncode',
    'CLIPTextEncode',
    'EmptyFlux2LatentImage',
    'Flux2Scheduler',
    'RandomNoise',
    'KSamplerSelect',
    'CFGGuider',
    'SamplerCustomAdvanced',
    'VAEDecode',
    'SaveImage'
)

$Checks = @()
$FailureReasons = @()
$Server = $null
$ObjectInfo = $null
$RawObjectInfo = $null
$ReferenceNodeName = $null
$ReferenceConditioningInput = $null
$ReferenceLatentInput = $null
$ReferenceCandidateNames = @()
$ExitCode = 1
$Utf8NoBom = [System.Text.UTF8Encoding]::new($false)

function Add-Check {
    param(
        [string]$Name,
        [bool]$Passed,
        [string]$Detail
    )

    $script:Checks += [pscustomobject]@{
        name = $Name
        passed = $Passed
        detail = $Detail
    }

    if ($Passed) {
        Write-Host "[OK] $Name - $Detail" -ForegroundColor Green
    } else {
        Write-Host "[FAIL] $Name - $Detail" -ForegroundColor Red
        $script:FailureReasons += "${Name}: $Detail"
    }
}

function Get-PropertyValue {
    param(
        $Object,
        [Parameter(Mandatory=$true)][string]$Name
    )

    if ($null -eq $Object) { return $null }
    $property = $Object.PSObject.Properties[$Name]
    if ($null -eq $property) { return $null }
    return $property.Value
}

function Get-NodeInfo {
    param(
        [Parameter(Mandatory=$true)]$Schema,
        [Parameter(Mandatory=$true)][string]$NodeName
    )

    return Get-PropertyValue -Object $Schema -Name $NodeName
}

function Get-InputSpec {
    param(
        [Parameter(Mandatory=$true)]$NodeInfo,
        [Parameter(Mandatory=$true)][string]$InputName
    )

    $input = Get-PropertyValue -Object $NodeInfo -Name 'input'
    if ($null -eq $input) { return $null }

    foreach ($groupName in @('required', 'optional')) {
        $group = Get-PropertyValue -Object $input -Name $groupName
        if ($null -eq $group) { continue }
        $property = $group.PSObject.Properties[$InputName]
        if ($null -ne $property) {
            return [pscustomobject]@{
                group = $groupName
                spec = $property.Value
            }
        }
    }

    return $null
}

function Get-InputType {
    param(
        [Parameter(Mandatory=$true)]$NodeInfo,
        [Parameter(Mandatory=$true)][string]$InputName
    )

    $record = Get-InputSpec -NodeInfo $NodeInfo -InputName $InputName
    if ($null -eq $record) { return $null }

    $spec = $record.spec
    if ($spec -is [System.Array] -and $spec.Count -gt 0) {
        $first = $spec[0]
        if ($first -is [string]) { return [string]$first }
        if ($first -is [System.Collections.IEnumerable] -and -not ($first -is [string])) {
            return 'COMBO'
        }
    }

    return $null
}

function Get-ComboChoices {
    param(
        [Parameter(Mandatory=$true)]$NodeInfo,
        [Parameter(Mandatory=$true)][string]$InputName
    )

    $record = Get-InputSpec -NodeInfo $NodeInfo -InputName $InputName
    if ($null -eq $record) { return @() }

    $spec = $record.spec
    if ($spec -is [System.Array] -and $spec.Count -gt 0) {
        $first = $spec[0]
        if ($first -is [System.Array]) { return @($first) }
        if ($first -is [System.Collections.IEnumerable] -and -not ($first -is [string])) {
            return @($first)
        }
    }

    return @()
}

function Get-OutputTypes {
    param(
        [Parameter(Mandatory=$true)]$NodeInfo
    )

    $output = Get-PropertyValue -Object $NodeInfo -Name 'output'
    if ($null -eq $output) { return @() }
    return @($output)
}

function Get-InputNamesByType {
    param(
        [Parameter(Mandatory=$true)]$NodeInfo,
        [Parameter(Mandatory=$true)][string]$ExpectedType
    )

    $names = @()
    $input = Get-PropertyValue -Object $NodeInfo -Name 'input'
    if ($null -eq $input) { return @() }

    foreach ($groupName in @('required', 'optional')) {
        $group = Get-PropertyValue -Object $input -Name $groupName
        if ($null -eq $group) { continue }

        foreach ($property in @($group.PSObject.Properties)) {
            $inputType = Get-InputType -NodeInfo $NodeInfo -InputName $property.Name
            if ($inputType -eq $ExpectedType) {
                $names += [string]$property.Name
            }
        }
    }

    return @($names | Select-Object -Unique)
}

function Normalize-InputPath {
    param([string]$Value)

    if ($null -eq $Value) { return '' }
    $normalized = ([string]$Value) -replace '\\', '/'
    while ($normalized.StartsWith('./')) {
        $normalized = $normalized.Substring(2)
    }
    return $normalized
}

function Test-ChoicesContainFile {
    param(
        [object[]]$Choices,
        [string]$ExpectedFile
    )

    foreach ($choice in @($Choices)) {
        $value = [string]$choice
        if ($value -eq $ExpectedFile) { return $true }

        try {
            if ([System.IO.Path]::GetFileName($value) -eq $ExpectedFile) {
                return $true
            }
        } catch {}
    }

    return $false
}

function Find-ModelChoiceOccurrences {
    param(
        [Parameter(Mandatory=$true)]$Schema,
        [Parameter(Mandatory=$true)][string]$ExpectedFile
    )

    $matches = @()

    foreach ($nodeProperty in @($Schema.PSObject.Properties)) {
        $nodeName = [string]$nodeProperty.Name
        $nodeInfo = $nodeProperty.Value
        $input = Get-PropertyValue -Object $nodeInfo -Name 'input'
        if ($null -eq $input) { continue }

        foreach ($groupName in @('required', 'optional')) {
            $group = Get-PropertyValue -Object $input -Name $groupName
            if ($null -eq $group) { continue }

            foreach ($inputProperty in @($group.PSObject.Properties)) {
                $choices = @(Get-ComboChoices -NodeInfo $nodeInfo -InputName $inputProperty.Name)
                if ($choices.Count -eq 0) { continue }

                if (Test-ChoicesContainFile -Choices $choices -ExpectedFile $ExpectedFile) {
                    $matches += [pscustomobject]@{
                        node = $nodeName
                        input = [string]$inputProperty.Name
                        group = $groupName
                    }
                }
            }
        }
    }

    return @($matches)
}

function Assert-NodeOutput {
    param(
        [Parameter(Mandatory=$true)]$Schema,
        [Parameter(Mandatory=$true)][string]$NodeName,
        [Parameter(Mandatory=$true)][string]$OutputType
    )

    $nodeInfo = Get-NodeInfo -Schema $Schema -NodeName $NodeName
    if ($null -eq $nodeInfo) {
        Add-Check -Name "node:$NodeName" -Passed $false -Detail 'node not exposed by /object_info'
        return
    }

    $outputs = @(Get-OutputTypes -NodeInfo $nodeInfo)
    $ok = $outputs -contains $OutputType
    Add-Check -Name "contract:$NodeName.output" -Passed $ok -Detail ("expected $OutputType; found [" + ($outputs -join ', ') + "]")
}

function Assert-NodeInputType {
    param(
        [Parameter(Mandatory=$true)]$Schema,
        [Parameter(Mandatory=$true)][string]$NodeName,
        [Parameter(Mandatory=$true)][string]$InputName,
        [Parameter(Mandatory=$true)][string]$ExpectedType
    )

    $nodeInfo = Get-NodeInfo -Schema $Schema -NodeName $NodeName
    if ($null -eq $nodeInfo) {
        Add-Check -Name "node:$NodeName" -Passed $false -Detail 'node not exposed by /object_info'
        return
    }

    $actualType = Get-InputType -NodeInfo $nodeInfo -InputName $InputName
    $ok = $actualType -eq $ExpectedType
    Add-Check -Name "contract:$NodeName.$InputName" -Passed $ok -Detail "expected $ExpectedType; found $actualType"
}

function Resolve-ReferenceMechanism {
    param(
        [Parameter(Mandatory=$true)]$Schema
    )

    $candidateNames = @()

    foreach ($nodeProperty in @($Schema.PSObject.Properties)) {
        $nodeName = [string]$nodeProperty.Name
        $nodeInfo = $nodeProperty.Value

        $conditioningInputs = @(Get-InputNamesByType -NodeInfo $nodeInfo -ExpectedType 'CONDITIONING')
        $latentInputs = @(Get-InputNamesByType -NodeInfo $nodeInfo -ExpectedType 'LATENT')
        $outputs = @(Get-OutputTypes -NodeInfo $nodeInfo)

        if ($conditioningInputs.Count -lt 1 -or $latentInputs.Count -lt 1 -or ($outputs -notcontains 'CONDITIONING')) {
            continue
        }

        $displayName = [string](Get-PropertyValue -Object $nodeInfo -Name 'display_name')
        $description = [string](Get-PropertyValue -Object $nodeInfo -Name 'description')
        $semanticText = ($nodeName + ' ' + $displayName + ' ' + $description)

        if ($semanticText -match '(?i)reference') {
            $candidateNames += $nodeName
        }
    }

    $candidateNames = @($candidateNames | Select-Object -Unique)
    $script:ReferenceCandidateNames = $candidateNames

    if ($candidateNames -contains 'ReferenceLatent') {
        return 'ReferenceLatent'
    }

    if ($candidateNames.Count -eq 1) {
        return [string]$candidateNames[0]
    }

    return $null
}

function Test-PortInUse {
    param(
        [string]$Address,
        [int]$PortNumber
    )

    $client = New-Object System.Net.Sockets.TcpClient
    try {
        $async = $client.BeginConnect($Address, $PortNumber, $null, $null)
        $connected = $async.AsyncWaitHandle.WaitOne(300)
        if (-not $connected) { return $false }
        $client.EndConnect($async)
        return $true
    }
    catch {
        return $false
    }
    finally {
        $client.Close()
    }
}

function Write-JsonFile {
    param(
        [Parameter(Mandatory=$true)]$Value,
        [Parameter(Mandatory=$true)][string]$Path,
        [int]$Depth = 50
    )

    $json = $Value | ConvertTo-Json -Depth $Depth
    [System.IO.File]::WriteAllText($Path, $json, $script:Utf8NoBom)
}

function Write-FinalReports {
    $status = if ($script:FailureReasons.Count -eq 0 -and $null -ne $script:ObjectInfo) { 'PASS' } else { 'FAIL' }

    $modelReport = @()
    if ($null -ne $script:ObjectInfo) {
        foreach ($contract in $script:ExpectedModelContracts) {
            $nodeInfo = Get-NodeInfo -Schema $script:ObjectInfo -NodeName $contract.node
            $choices = @()
            if ($null -ne $nodeInfo) {
                $choices = @(Get-ComboChoices -NodeInfo $nodeInfo -InputName $contract.input)
            }
            $occurrences = @(Find-ModelChoiceOccurrences -Schema $script:ObjectInfo -ExpectedFile $contract.file)

            $modelReport += [pscustomobject]@{
                role = $contract.role
                expected_node = $contract.node
                expected_input = $contract.input
                file = $contract.file
                visible_in_expected_loader = (Test-ChoicesContainFile -Choices $choices -ExpectedFile $contract.file)
                all_schema_occurrences = $occurrences
            }
        }
    }

    $referenceRepresentation = @()
    if ($null -ne $script:ReferenceNodeName) {
        $referenceRepresentation = @(
            "image_1 -> LoadImage -> VAEEncode -> $($script:ReferenceNodeName).$($script:ReferenceLatentInput)",
            "conditioning_0 -> $($script:ReferenceNodeName).$($script:ReferenceConditioningInput) + latent(image_1) -> conditioning_1",
            "conditioning_1 -> $($script:ReferenceNodeName).$($script:ReferenceConditioningInput) + latent(image_2) -> conditioning_2"
        )
    }

    $referenceReport = [ordered]@{
        resolved_node = $script:ReferenceNodeName
        conditioning_input = $script:ReferenceConditioningInput
        latent_input = $script:ReferenceLatentInput
        candidates = @($script:ReferenceCandidateNames)
        supports_chaining = ($null -ne $script:ReferenceNodeName)
        semantic_order = @(
            'image_1 = COCO-18 target skeleton',
            'image_2 = exilada_master.png identity reference'
        )
        representation = $referenceRepresentation
        note = 'Semantic image order comes from the locked RefControl spike contract; the installed /object_info schema is used to validate the actual runtime node and chainable CONDITIONING+LATENT->CONDITIONING mechanism.'
    }

    $httpRequests = @()
    if ($null -ne $script:Server) {
        $httpRequests = @('GET /object_info only; polled until HTTP 200')
    }

    $nextGate = 'Remain in STEP 5. Fix the reported runtime/schema mismatch; do not build or queue an inference workflow.'
    if ($status -eq 'PASS') {
        $nextGate = 'STEP 5 passed locally. Update docs/ANIMATION_PIPELINE.md and docs/PROJECT_STATE.md with the observed report before creating or running STEP 6 tooling.'
    }

    $report = [ordered]@{
        step = 5
        name = 'runtime schema/workflow validation without inference'
        status = $status
        timestamp_utc = (Get-Date).ToUniversalTime().ToString('o')
        workspace = $script:Workspace
        comfy_endpoint = $script:BaseUrl
        http_requests_made = $httpRequests
        prompt_requests_sent = 0
        inference_performed = $false
        model_execution_requested = $false
        full_object_info_path = $script:FullSchemaPath
        reduced_object_info_path = $script:ReducedSchemaPath
        checks = @($script:Checks)
        failures = @($script:FailureReasons)
        models = $modelReport
        reference_mechanism = $referenceReport
        next_gate = $nextGate
    }

    Write-JsonFile -Value $report -Path $script:ReportJsonPath -Depth 100

    $text = @(
        'FLUX.2 Klein + RefControl Pose - STEP 5 runtime schema validation',
        ('status=' + $status),
        ('timestamp_utc=' + $report.timestamp_utc),
        ('endpoint=' + $script:BaseUrl),
        'prompt_requests_sent=0',
        'inference_performed=false',
        'model_execution_requested=false',
        ('full_object_info=' + $script:FullSchemaPath),
        ('reduced_object_info=' + $script:ReducedSchemaPath),
        ('reference_node=' + [string]$script:ReferenceNodeName),
        ('reference_conditioning_input=' + [string]$script:ReferenceConditioningInput),
        ('reference_latent_input=' + [string]$script:ReferenceLatentInput),
        '',
        'CHECKS'
    )

    foreach ($check in @($script:Checks)) {
        $checkStatus = if ($check.passed) { 'PASS' } else { 'FAIL' }
        $text += "[$checkStatus] $($check.name) - $($check.detail)"
    }

    if ($script:FailureReasons.Count -gt 0) {
        $text += ''
        $text += 'FAILURES'
        foreach ($failure in @($script:FailureReasons)) {
            $text += ('- ' + $failure)
        }
    }

    $text += ''
    $text += ('next_gate=' + $report.next_gate)
    [System.IO.File]::WriteAllLines($script:ReportTextPath, $text, $script:Utf8NoBom)

    return $status
}

Write-Host ''
Write-Host 'FLUX.2 Klein + RefControl Pose spike - STEP 5: runtime schema validation only' -ForegroundColor Cyan
Write-Host "Endpoint: $BaseUrl"
Write-Host 'This script performs GET /object_info only. It never POSTs /prompt and never executes a workflow.'
Write-Host ''

New-Item -ItemType Directory -Force -Path $SchemaDir | Out-Null
Remove-Item $FullSchemaPath, $ReducedSchemaPath, $ReportJsonPath, $ReportTextPath, $StdoutLog, $StderrLog -Force -ErrorAction SilentlyContinue

try {
    Add-Check -Name 'runtime:embedded_python' -Passed (Test-Path $Python -PathType Leaf) -Detail $Python
    Add-Check -Name 'runtime:comfy_main' -Passed (Test-Path $ComfyMain -PathType Leaf) -Detail $ComfyMain

    foreach ($relativeInput in $ExpectedInputFiles) {
        $physicalPath = Join-Path $InputDir ($relativeInput -replace '/', '\')
        Add-Check -Name "input_file:$relativeInput" -Passed (Test-Path $physicalPath -PathType Leaf) -Detail $physicalPath
    }

    if ($FailureReasons.Count -gt 0) {
        throw 'Pre-start STEP 5 checks failed.'
    }

    if (Test-PortInUse -Address $HostAddress -PortNumber $Port) {
        Add-Check -Name 'runtime:port_8188_free' -Passed $false -Detail "${HostAddress}:$Port is already accepting TCP connections; validator will not attach to an unknown process."
        throw 'Port 8188 is already in use.'
    }
    Add-Check -Name 'runtime:port_8188_free' -Passed $true -Detail "${HostAddress}:$Port is available."

    $arguments = @(
        '-s',
        $ComfyMain,
        '--windows-standalone-build',
        '--listen', $HostAddress,
        '--port', [string]$Port,
        '--disable-auto-launch'
    )

    Write-Host ''
    Write-Host '[START] Launching temporary ComfyUI schema server...' -ForegroundColor Cyan
    $Server = Start-Process `
        -FilePath $Python `
        -ArgumentList $arguments `
        -WorkingDirectory $ComfyRoot `
        -PassThru `
        -RedirectStandardOutput $StdoutLog `
        -RedirectStandardError $StderrLog

    $deadline = (Get-Date).AddSeconds(120)
    $response = $null

    while ((Get-Date) -lt $deadline) {
        if ($Server.HasExited) {
            $stdoutTail = if (Test-Path $StdoutLog) { (Get-Content $StdoutLog -Tail 60) -join [Environment]::NewLine } else { '' }
            $stderrTail = if (Test-Path $StderrLog) { (Get-Content $StderrLog -Tail 60) -join [Environment]::NewLine } else { '' }
            Add-Check -Name 'runtime:server_start' -Passed $false -Detail "ComfyUI exited with code $($Server.ExitCode). STDOUT tail: $stdoutTail STDERR tail: $stderrTail"
            throw 'ComfyUI exited before /object_info became available.'
        }

        try {
            $response = Invoke-WebRequest -Uri ($BaseUrl + '/object_info') -Method Get -UseBasicParsing -TimeoutSec 5
            if ($null -ne $response -and $response.StatusCode -eq 200 -and $response.Content) {
                break
            }
        }
        catch {
            Start-Sleep -Milliseconds 750
        }
    }

    if ($null -eq $response -or $response.StatusCode -ne 200 -or -not $response.Content) {
        Add-Check -Name 'http:GET_/object_info' -Passed $false -Detail 'No HTTP 200 response within 120 seconds.'
        throw 'Timed out waiting for GET /object_info.'
    }

    Add-Check -Name 'runtime:server_start' -Passed $true -Detail "ComfyUI started as PID $($Server.Id)."
    Add-Check -Name 'http:GET_/object_info' -Passed $true -Detail 'HTTP 200; no /prompt request sent.'

    $RawObjectInfo = [string]$response.Content
    [System.IO.File]::WriteAllText($FullSchemaPath, $RawObjectInfo, $Utf8NoBom)
    Add-Check -Name 'artifact:full_object_info' -Passed (Test-Path $FullSchemaPath -PathType Leaf) -Detail $FullSchemaPath

    $ObjectInfo = $RawObjectInfo | ConvertFrom-Json
    Add-Check -Name 'schema:parse' -Passed ($null -ne $ObjectInfo) -Detail 'Full /object_info JSON parsed successfully.'

    Write-Host ''
    Write-Host '[CHECK] Core FLUX.2 image-edit node contracts...' -ForegroundColor Cyan

    foreach ($nodeName in $RequiredCoreNodes) {
        $nodeInfo = Get-NodeInfo -Schema $ObjectInfo -NodeName $nodeName
        $nodeDetail = if ($null -ne $nodeInfo) { 'exposed by /object_info' } else { 'missing from /object_info' }
        Add-Check -Name "node:$nodeName" -Passed ($null -ne $nodeInfo) -Detail $nodeDetail
    }

    Assert-NodeOutput -Schema $ObjectInfo -NodeName 'UNETLoader' -OutputType 'MODEL'
    Assert-NodeOutput -Schema $ObjectInfo -NodeName 'CLIPLoader' -OutputType 'CLIP'
    Assert-NodeOutput -Schema $ObjectInfo -NodeName 'VAELoader' -OutputType 'VAE'

    Assert-NodeInputType -Schema $ObjectInfo -NodeName 'LoraLoaderModelOnly' -InputName 'model' -ExpectedType 'MODEL'
    Assert-NodeOutput -Schema $ObjectInfo -NodeName 'LoraLoaderModelOnly' -OutputType 'MODEL'

    Assert-NodeOutput -Schema $ObjectInfo -NodeName 'LoadImage' -OutputType 'IMAGE'
    Assert-NodeInputType -Schema $ObjectInfo -NodeName 'VAEEncode' -InputName 'pixels' -ExpectedType 'IMAGE'
    Assert-NodeInputType -Schema $ObjectInfo -NodeName 'VAEEncode' -InputName 'vae' -ExpectedType 'VAE'
    Assert-NodeOutput -Schema $ObjectInfo -NodeName 'VAEEncode' -OutputType 'LATENT'

    Assert-NodeInputType -Schema $ObjectInfo -NodeName 'CLIPTextEncode' -InputName 'clip' -ExpectedType 'CLIP'
    Assert-NodeOutput -Schema $ObjectInfo -NodeName 'CLIPTextEncode' -OutputType 'CONDITIONING'

    Assert-NodeOutput -Schema $ObjectInfo -NodeName 'EmptyFlux2LatentImage' -OutputType 'LATENT'
    Assert-NodeOutput -Schema $ObjectInfo -NodeName 'Flux2Scheduler' -OutputType 'SIGMAS'
    Assert-NodeOutput -Schema $ObjectInfo -NodeName 'RandomNoise' -OutputType 'NOISE'
    Assert-NodeOutput -Schema $ObjectInfo -NodeName 'KSamplerSelect' -OutputType 'SAMPLER'

    Assert-NodeInputType -Schema $ObjectInfo -NodeName 'CFGGuider' -InputName 'model' -ExpectedType 'MODEL'
    Assert-NodeInputType -Schema $ObjectInfo -NodeName 'CFGGuider' -InputName 'positive' -ExpectedType 'CONDITIONING'
    Assert-NodeInputType -Schema $ObjectInfo -NodeName 'CFGGuider' -InputName 'negative' -ExpectedType 'CONDITIONING'
    Assert-NodeOutput -Schema $ObjectInfo -NodeName 'CFGGuider' -OutputType 'GUIDER'

    Assert-NodeInputType -Schema $ObjectInfo -NodeName 'SamplerCustomAdvanced' -InputName 'noise' -ExpectedType 'NOISE'
    Assert-NodeInputType -Schema $ObjectInfo -NodeName 'SamplerCustomAdvanced' -InputName 'guider' -ExpectedType 'GUIDER'
    Assert-NodeInputType -Schema $ObjectInfo -NodeName 'SamplerCustomAdvanced' -InputName 'sampler' -ExpectedType 'SAMPLER'
    Assert-NodeInputType -Schema $ObjectInfo -NodeName 'SamplerCustomAdvanced' -InputName 'sigmas' -ExpectedType 'SIGMAS'
    Assert-NodeInputType -Schema $ObjectInfo -NodeName 'SamplerCustomAdvanced' -InputName 'latent_image' -ExpectedType 'LATENT'
    Assert-NodeOutput -Schema $ObjectInfo -NodeName 'SamplerCustomAdvanced' -OutputType 'LATENT'

    Assert-NodeInputType -Schema $ObjectInfo -NodeName 'VAEDecode' -InputName 'samples' -ExpectedType 'LATENT'
    Assert-NodeInputType -Schema $ObjectInfo -NodeName 'VAEDecode' -InputName 'vae' -ExpectedType 'VAE'
    Assert-NodeOutput -Schema $ObjectInfo -NodeName 'VAEDecode' -OutputType 'IMAGE'
    Assert-NodeInputType -Schema $ObjectInfo -NodeName 'SaveImage' -InputName 'images' -ExpectedType 'IMAGE'

    Write-Host ''
    Write-Host '[CHECK] Installed model filenames and loader choices...' -ForegroundColor Cyan

    foreach ($contract in $ExpectedModelContracts) {
        $nodeInfo = Get-NodeInfo -Schema $ObjectInfo -NodeName $contract.node
        if ($null -eq $nodeInfo) {
            Add-Check -Name "model:$($contract.role)" -Passed $false -Detail "expected loader $($contract.node) is missing"
            continue
        }

        $choices = @(Get-ComboChoices -NodeInfo $nodeInfo -InputName $contract.input)
        $visible = Test-ChoicesContainFile -Choices $choices -ExpectedFile $contract.file
        $occurrences = @(Find-ModelChoiceOccurrences -Schema $ObjectInfo -ExpectedFile $contract.file)
        $occurrenceText = if ($occurrences.Count -gt 0) {
            @($occurrences | ForEach-Object { "$($_.node).$($_.input)" }) -join ', '
        } else {
            'none'
        }

        Add-Check `
            -Name "model:$($contract.role)" `
            -Passed $visible `
            -Detail "expected $($contract.file) in $($contract.node).$($contract.input); schema occurrences: $occurrenceText"
    }

    $clipLoader = Get-NodeInfo -Schema $ObjectInfo -NodeName 'CLIPLoader'
    if ($null -ne $clipLoader) {
        $clipTypes = @(Get-ComboChoices -NodeInfo $clipLoader -InputName 'type')
        Add-Check -Name 'loader:CLIPLoader.type=flux2' -Passed ($clipTypes -contains 'flux2') -Detail ("available types: " + ($clipTypes -join ', '))
    }

    Write-Host ''
    Write-Host '[CHECK] LoadImage sees all prepared reference inputs...' -ForegroundColor Cyan

    $loadImage = Get-NodeInfo -Schema $ObjectInfo -NodeName 'LoadImage'
    if ($null -ne $loadImage) {
        $imageChoices = @(Get-ComboChoices -NodeInfo $loadImage -InputName 'image')
        $normalizedChoices = @($imageChoices | ForEach-Object { Normalize-InputPath -Value ([string]$_) })

        foreach ($expectedInput in $ExpectedInputFiles) {
            $normalizedExpected = Normalize-InputPath -Value $expectedInput
            Add-Check -Name "loader_input:$expectedInput" -Passed ($normalizedChoices -contains $normalizedExpected) -Detail "LoadImage.image must list $normalizedExpected"
        }
    }

    Write-Host ''
    Write-Host '[CHECK] ReferenceLatent / equivalent two-reference mechanism...' -ForegroundColor Cyan

    $ReferenceNodeName = Resolve-ReferenceMechanism -Schema $ObjectInfo
    if ($null -eq $ReferenceNodeName) {
        Add-Check -Name 'reference:mechanism' -Passed $false -Detail ("Could not resolve a unique reference node with CONDITIONING + LATENT -> CONDITIONING. Candidates: " + ($ReferenceCandidateNames -join ', '))
    } else {
        $referenceNode = Get-NodeInfo -Schema $ObjectInfo -NodeName $ReferenceNodeName
        $conditioningInputs = @(Get-InputNamesByType -NodeInfo $referenceNode -ExpectedType 'CONDITIONING')
        $latentInputs = @(Get-InputNamesByType -NodeInfo $referenceNode -ExpectedType 'LATENT')
        $outputs = @(Get-OutputTypes -NodeInfo $referenceNode)

        if ($conditioningInputs.Count -eq 1) {
            $ReferenceConditioningInput = [string]$conditioningInputs[0]
        }
        if ($latentInputs.Count -eq 1) {
            $ReferenceLatentInput = [string]$latentInputs[0]
        }

        $contractPass = (
            $conditioningInputs.Count -eq 1 -and
            $latentInputs.Count -eq 1 -and
            ($outputs -contains 'CONDITIONING')
        )

        Add-Check `
            -Name 'reference:mechanism' `
            -Passed $contractPass `
            -Detail "$ReferenceNodeName inputs CONDITIONING=[$($conditioningInputs -join ', ')] LATENT=[$($latentInputs -join ', ')] outputs=[$($outputs -join ', ')]"

        if ($contractPass) {
            Add-Check `
                -Name 'reference:two_reference_chain' `
                -Passed $true `
                -Detail "The runtime can chain image_1 latent then image_2 latent because $ReferenceNodeName returns CONDITIONING accepted again by its $ReferenceConditioningInput input."
        }
    }

    $selectedNodeNames = @($RequiredCoreNodes)
    if ($null -ne $ReferenceNodeName -and $selectedNodeNames -notcontains $ReferenceNodeName) {
        $selectedNodeNames += $ReferenceNodeName
    }
    foreach ($candidateName in @($ReferenceCandidateNames)) {
        if ($selectedNodeNames -notcontains $candidateName) {
            $selectedNodeNames += $candidateName
        }
    }

    $selectedNodes = [ordered]@{}
    foreach ($nodeName in $selectedNodeNames) {
        $nodeInfo = Get-NodeInfo -Schema $ObjectInfo -NodeName $nodeName
        if ($null -ne $nodeInfo) {
            $selectedNodes[$nodeName] = $nodeInfo
        }
    }

    $reducedSchema = [ordered]@{
        source = 'GET /object_info from installed local ComfyUI runtime'
        endpoint = $BaseUrl
        timestamp_utc = (Get-Date).ToUniversalTime().ToString('o')
        selected_nodes = $selectedNodes
        resolved_reference_node = $ReferenceNodeName
        resolved_reference_conditioning_input = $ReferenceConditioningInput
        resolved_reference_latent_input = $ReferenceLatentInput
        semantic_reference_order = @(
            'image_1 = COCO-18 target skeleton',
            'image_2 = exilada_master.png identity reference'
        )
        prompt_requests_sent = 0
        inference_performed = $false
    }
    Write-JsonFile -Value $reducedSchema -Path $ReducedSchemaPath -Depth 100
    Add-Check -Name 'artifact:reduced_object_info' -Passed (Test-Path $ReducedSchemaPath -PathType Leaf) -Detail $ReducedSchemaPath

    if ($FailureReasons.Count -gt 0) {
        throw "STEP 5 schema validation has $($FailureReasons.Count) failing check(s)."
    }

    $ExitCode = 0
}
catch {
    $message = $_.Exception.Message
    if ($FailureReasons -notcontains $message) {
        $FailureReasons += $message
    }
    $ExitCode = 1
}
finally {
    if ($null -ne $Server -and -not $Server.HasExited) {
        Write-Host ''
        Write-Host '[STOP] Stopping temporary ComfyUI schema server...' -ForegroundColor Cyan
        Stop-Process -Id $Server.Id -Force -ErrorAction SilentlyContinue
        try {
            [void]$Server.WaitForExit(10000)
        } catch {}

        $Server.Refresh()
        if ($Server.HasExited) {
            Add-Check -Name 'runtime:server_stopped' -Passed $true -Detail "PID $($Server.Id) exited."
        } else {
            Add-Check -Name 'runtime:server_stopped' -Passed $false -Detail "PID $($Server.Id) did not exit after Stop-Process."
        }
    }

    $status = Write-FinalReports
    if ($status -eq 'PASS') {
        $ExitCode = 0
    } else {
        $ExitCode = 1
    }

    Write-Host ''
    if ($status -eq 'PASS') {
        Write-Host 'STEP 5: PASS' -ForegroundColor Green
        Write-Host "Full schema:    $FullSchemaPath"
        Write-Host "Reduced schema: $ReducedSchemaPath"
        Write-Host "Report:         $ReportJsonPath"
        Write-Host 'No /prompt POST was sent. No workflow was executed. No image was generated.' -ForegroundColor Green
    } else {
        Write-Host 'STEP 5: FAIL' -ForegroundColor Red
        Write-Host "Report: $ReportJsonPath"
        Write-Host "Logs:   $StdoutLog / $StderrLog"
        Write-Host 'Remain in STEP 5. Do not create or run STEP 6 tooling.' -ForegroundColor Yellow
    }
}

exit $ExitCode
