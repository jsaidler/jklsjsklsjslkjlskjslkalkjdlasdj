param(
    [string]$Workspace = 'Z:\AI\QwenImageEditSpike'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$Port = 8210
$PortableRoot = Join-Path $Workspace 'ComfyUI_windows_portable'
$ComfyRoot = Join-Path $PortableRoot 'ComfyUI'
$Python = Join-Path $PortableRoot 'python_embeded\python.exe'
$MainPy = Join-Path $ComfyRoot 'main.py'
$SchemaDir = Join-Path $Workspace 'runtime_schema'
$FullSchemaPath = Join-Path $SchemaDir 'object_info.full.json'
$RequiredSchemaPath = Join-Path $SchemaDir 'object_info.required.json'
$ReportJson = Join-Path $SchemaDir 'step5_runtime_schema_report.json'
$ReportTxt = Join-Path $SchemaDir 'step5_runtime_schema_report.txt'
$StdoutLog = Join-Path $SchemaDir 'comfy_step5.stdout.log'
$StderrLog = Join-Path $SchemaDir 'comfy_step5.stderr.log'
$Api = "http://127.0.0.1:$Port"

$QwenModel = 'Qwen-Image-Edit-2509-Q4_0.gguf'
$ClipModel = 'qwen_2.5_vl_7b_fp8_scaled.safetensors'
$VaeModel = 'qwen_image_vae.safetensors'
$IdentityInput = 'exilada_master.png'
$PoseInput = 'qwen_hard_passing_L_keypoints.png'

function Get-Prop([object]$Object, [string]$Name) {
    if ($null -eq $Object) { return $null }
    $p = $Object.PSObject.Properties[$Name]
    if ($null -eq $p) { return $null }
    return $p.Value
}

function Save-Json([object]$Object, [string]$Path, [int]$Depth=32) {
    $safe=[math]::Max(4,[math]::Min($Depth,64))
    $json=$Object | ConvertTo-Json -Depth $safe
    [System.IO.File]::WriteAllText($Path,$json,[System.Text.UTF8Encoding]::new($false))
}

function Add-Check([System.Collections.ArrayList]$Checks, [System.Collections.ArrayList]$Failures, [string]$Name, [bool]$Ok, [string]$Detail) {
    [void]$Checks.Add([ordered]@{ name=$Name; pass=$Ok; detail=$Detail })
    if (-not $Ok) { [void]$Failures.Add("${Name}: $Detail") }
    $tag = if ($Ok) { '[OK]' } else { '[FAIL]' }
    $color = if ($Ok) { 'Green' } else { 'Red' }
    Write-Host "$tag $Name - $Detail" -ForegroundColor $color
}

function Get-ChoiceValues([object]$Node, [string]$InputName) {
    $input = Get-Prop $Node 'input'
    foreach ($bucketName in @('required','optional')) {
        $bucket = Get-Prop $input $bucketName
        if ($null -eq $bucket) { continue }
        $p = $bucket.PSObject.Properties[$InputName]
        if ($null -eq $p) { continue }
        $def = $p.Value
        if ($def -is [System.Array] -and $def.Count -gt 0 -and $def[0] -is [System.Array]) {
            return @($def[0])
        }
    }
    return @()
}

function Has-Input([object]$Node,[string]$InputName) {
    $input=Get-Prop $Node 'input'
    foreach($bucketName in @('required','optional')) {
        $bucket=Get-Prop $input $bucketName
        if($null -ne $bucket -and $null -ne $bucket.PSObject.Properties[$InputName]) { return $true }
    }
    return $false
}

Write-Host ''
Write-Host 'Qwen-Image-Edit-2509 keypoint spike - STEP 5: RUNTIME SCHEMA GATE' -ForegroundColor Cyan
Write-Host 'GET /object_info only. No /prompt. No model execution. No inference.' -ForegroundColor Yellow
Write-Host ''

foreach($p in @($Python,$MainPy)) {
    if(-not(Test-Path $p -PathType Leaf)) { throw "Missing runtime file: $p" }
}
foreach($p in @(
    (Join-Path $ComfyRoot "models\unet\$QwenModel"),
    (Join-Path $ComfyRoot "models\text_encoders\$ClipModel"),
    (Join-Path $ComfyRoot "models\vae\$VaeModel"),
    (Join-Path $ComfyRoot "input\$IdentityInput"),
    (Join-Path $ComfyRoot "input\$PoseInput")
)) {
    if(-not(Test-Path $p -PathType Leaf)) { throw "Missing required prepared file: $p" }
}

New-Item -ItemType Directory -Force -Path $SchemaDir | Out-Null
Remove-Item $StdoutLog,$StderrLog -Force -ErrorAction SilentlyContinue

try {
    Invoke-RestMethod -Uri "$Api/object_info" -Method Get -TimeoutSec 2 | Out-Null
    throw "Port $Port already serves a ComfyUI-compatible endpoint. Refusing to attach to an unknown process."
} catch {
    if($_.Exception.Message -like 'Port * already serves*') { throw }
}

$proc=$null
$checks=New-Object System.Collections.ArrayList
$failures=New-Object System.Collections.ArrayList
$rawBody=$null
try {
    Write-Host "[START] ComfyUI low-VRAM schema server on 127.0.0.1:$Port ..." -ForegroundColor Cyan
    $args=@('-s',$MainPy,'--windows-standalone-build','--listen','127.0.0.1','--port',[string]$Port,'--disable-auto-launch','--lowvram')
    $proc=Start-Process -FilePath $Python -ArgumentList $args -WorkingDirectory $ComfyRoot -PassThru -RedirectStandardOutput $StdoutLog -RedirectStandardError $StderrLog

    $deadline=(Get-Date).AddSeconds(120)
    $response=$null
    while((Get-Date)-lt $deadline) {
        if($proc.HasExited) { throw "ComfyUI exited during startup with code $($proc.ExitCode)." }
        try {
            $r=Invoke-WebRequest -Uri "$Api/object_info" -Method Get -TimeoutSec 10 -UseBasicParsing
            if($r.StatusCode -eq 200) { $response=$r; break }
        } catch {}
        Start-Sleep -Milliseconds 750
    }
    if($null -eq $response) { throw 'Timed out waiting for GET /object_info.' }

    $rawBody=[string]$response.Content
    [System.IO.File]::WriteAllText($FullSchemaPath,$rawBody,[System.Text.UTF8Encoding]::new($false))
    $schema=$rawBody | ConvertFrom-Json

    $requiredNodes=@('UnetLoaderGGUF','CLIPLoader','VAELoader','TextEncodeQwenImageEditPlus','ModelSamplingAuraFlow','LoadImage','VAEEncode','RandomNoise','KSamplerSelect','SamplerCustomAdvanced','VAEDecode','SaveImage')
    $subset=[ordered]@{}
    foreach($name in $requiredNodes) {
        $prop=$schema.PSObject.Properties[$name]
        $ok=$null -ne $prop
        Add-Check $checks $failures "node:$name" $ok $(if($ok){'available'}else{'missing'})
        if($ok) { $subset[$name]=$prop.Value }
    }

    if($null -ne $schema.PSObject.Properties['UnetLoaderGGUF']) {
        $node=$schema.UnetLoaderGGUF
        $choices=Get-ChoiceValues $node 'unet_name'
        Add-Check $checks $failures 'GGUF model loader choice' ($choices -contains $QwenModel) $(if($choices -contains $QwenModel){$QwenModel}else{"not listed; choices="+($choices -join ', ')})
    }

    if($null -ne $schema.PSObject.Properties['CLIPLoader']) {
        $node=$schema.CLIPLoader
        $clipChoices=Get-ChoiceValues $node 'clip_name'
        $typeChoices=Get-ChoiceValues $node 'type'
        Add-Check $checks $failures 'Qwen text encoder loader choice' ($clipChoices -contains $ClipModel) $(if($clipChoices -contains $ClipModel){$ClipModel}else{'not listed'})
        Add-Check $checks $failures 'CLIPLoader qwen_image type' ($typeChoices -contains 'qwen_image') $(if($typeChoices -contains 'qwen_image'){'qwen_image available'}else{"types="+($typeChoices -join ', ')})
    }

    if($null -ne $schema.PSObject.Properties['VAELoader']) {
        $choices=Get-ChoiceValues $schema.VAELoader 'vae_name'
        Add-Check $checks $failures 'Qwen VAE loader choice' ($choices -contains $VaeModel) $(if($choices -contains $VaeModel){$VaeModel}else{'not listed'})
    }

    if($null -ne $schema.PSObject.Properties['TextEncodeQwenImageEditPlus']) {
        $node=$schema.TextEncodeQwenImageEditPlus
        foreach($inputName in @('clip','vae','image1','image2','prompt')) {
            Add-Check $checks $failures "TextEncode input:$inputName" (Has-Input $node $inputName) $(if(Has-Input $node $inputName){'available'}else{'missing'})
        }
        $out=Get-Prop $node 'output'
        $hasConditioning=@($out) -contains 'CONDITIONING'
        Add-Check $checks $failures 'TextEncode output CONDITIONING' $hasConditioning $(if($hasConditioning){'available'}else{'missing'})
    }

    $loadChoices=Get-ChoiceValues $schema.LoadImage 'image'
    $norm=@($loadChoices | ForEach-Object { ([string]$_).Replace('\','/') })
    foreach($inputFile in @($IdentityInput,$PoseInput)) {
        Add-Check $checks $failures "LoadImage sees:$inputFile" ($norm -contains $inputFile) $(if($norm -contains $inputFile){'listed'}else{'not listed'})
    }

    Save-Json $subset $RequiredSchemaPath 64

    $pass=$failures.Count -eq 0
    $report=[ordered]@{
        spike='Qwen-Image-Edit-2509 native keypoint topology gate'
        stage='runtime_schema_validation'
        pass=$pass
        workspace=$Workspace
        api=$Api
        object_info_full=$FullSchemaPath
        object_info_required=$RequiredSchemaPath
        checks=$checks
        failures=$failures
        prompt_requests_sent=0
        inference_performed=$false
        model_execution_requested=$false
        next_gate=$(if($pass){'Build one-pose executable workflow from observed runtime schema; do not run until tooling is reviewed.'}else{'Fix runtime/schema only. Do not build or run inference.'})
        completed_at=(Get-Date).ToString('o')
    }
    Save-Json $report $ReportJson 32

    $lines=@()
    $lines += "STEP 5: " + $(if($pass){'PASS'}else{'FAIL'})
    $lines += "prompt_requests_sent=0"
    $lines += "inference_performed=false"
    foreach($c in $checks){ $lines += ((if($c.pass){'[PASS] '}else{'[FAIL] '}) + $c.name + ' - ' + $c.detail) }
    if($failures.Count -gt 0){ $lines += 'Failures:'; $lines += @($failures | ForEach-Object { ' - ' + $_ }) }
    [System.IO.File]::WriteAllLines($ReportTxt,$lines,[System.Text.UTF8Encoding]::new($false))

    Write-Host ''
    if($pass){
        Write-Host 'STEP 5: PASS' -ForegroundColor Green
        Write-Host 'Runtime exposes the required Qwen 2509 edit + GGUF contracts.'
    } else {
        Write-Host 'STEP 5: FAIL' -ForegroundColor Red
        $failures | ForEach-Object { Write-Host "  - $_" -ForegroundColor Red }
    }
    Write-Host "Report: $ReportJson"
    Write-Host 'No /prompt request was sent and no inference was performed.' -ForegroundColor Yellow
    if(-not $pass){ exit 1 }
}
finally {
    if($null -ne $proc -and -not $proc.HasExited) {
        Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
        try { $proc.WaitForExit(5000) | Out-Null } catch {}
    }
}
