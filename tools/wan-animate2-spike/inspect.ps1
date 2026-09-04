param(
    [string]$Workspace = 'D:\AI\WanAnimate2',
    [int]$Port = 8188
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Find-ComfyRoot([string]$Base) {
    $candidates = @($Base, (Join-Path $Base 'ComfyUI'))
    foreach ($candidate in $candidates) {
        if (Test-Path (Join-Path $candidate 'main.py')) { return $candidate }
    }
    return $null
}

function Find-WorkspacePython([string]$Base, [string]$ComfyRoot) {
    $candidates = @(
        (Join-Path $ComfyRoot '.venv\Scripts\python.exe'),
        (Join-Path $Base '.venv\Scripts\python.exe')
    ) | Select-Object -Unique
    foreach ($candidate in $candidates) {
        if (Test-Path $candidate) { return $candidate }
    }
    return $null
}

$ComfyRoot = Find-ComfyRoot $Workspace
if (-not $ComfyRoot) {
    throw "ComfyUI not found under $Workspace. Run bootstrap.ps1 first."
}

$WorkspacePython = Find-WorkspacePython $Workspace $ComfyRoot
if (-not $WorkspacePython) {
    throw "ComfyUI Python environment not found under $Workspace or $ComfyRoot"
}

Write-Host "ComfyUI root: $ComfyRoot" -ForegroundColor Green
Write-Host "ComfyUI Python: $WorkspacePython" -ForegroundColor Green

$Base = "http://127.0.0.1:$Port"
$serverAlreadyRunning = $false
try {
    $null = Invoke-RestMethod -Uri "$Base/system_stats" -TimeoutSec 2
    $serverAlreadyRunning = $true
} catch {}

$UserDir = Join-Path $ComfyRoot 'user'
New-Item -ItemType Directory -Force -Path $UserDir | Out-Null
$StdoutLog = Join-Path $UserDir "comfyui_${Port}_stdout.log"
$StderrLog = Join-Path $UserDir "comfyui_${Port}_stderr.log"
$PidFile = Join-Path $Workspace '.wan_animate2_spike.pid'
$process = $null

if ($serverAlreadyRunning) {
    Write-Host "ComfyUI API is already running at $Base" -ForegroundColor Green
} else {
    Write-Host 'Starting ComfyUI directly with the workspace Python (headless)...' -ForegroundColor Cyan
    $MainPy = Join-Path $ComfyRoot 'main.py'
    $launchArgs = @(
        $MainPy,
        '--listen', '127.0.0.1',
        '--port', "$Port",
        '--disable-auto-launch'
    )

    $process = Start-Process `
        -FilePath $WorkspacePython `
        -ArgumentList $launchArgs `
        -WorkingDirectory $ComfyRoot `
        -RedirectStandardOutput $StdoutLog `
        -RedirectStandardError $StderrLog `
        -WindowStyle Hidden `
        -PassThru

    Set-Content -Path $PidFile -Value $process.Id -Encoding ascii
    Write-Host "Started PID $($process.Id)" -ForegroundColor Green
    Write-Host "stdout: $StdoutLog"
    Write-Host "stderr: $StderrLog"
}

$ok = $false
for ($i = 0; $i -lt 120; $i++) {
    try {
        $null = Invoke-RestMethod -Uri "$Base/system_stats" -TimeoutSec 2
        $ok = $true
        break
    } catch {
        if ($process -and $process.HasExited) {
            Write-Host "ComfyUI exited early with code $($process.ExitCode)." -ForegroundColor Red
            if (Test-Path $StderrLog) {
                Write-Host '--- stderr tail ---' -ForegroundColor Yellow
                Get-Content $StderrLog -Tail 80
            }
            if (Test-Path $StdoutLog) {
                Write-Host '--- stdout tail ---' -ForegroundColor Yellow
                Get-Content $StdoutLog -Tail 40
            }
            throw 'ComfyUI failed during startup.'
        }
        Start-Sleep -Seconds 1
    }
}
if (-not $ok) {
    if (Test-Path $StderrLog) {
        Write-Host '--- stderr tail ---' -ForegroundColor Yellow
        Get-Content $StderrLog -Tail 80
    }
    throw "ComfyUI API did not become available at $Base"
}

Write-Host "ComfyUI API ready: $Base" -ForegroundColor Green
$ObjectInfo = Invoke-RestMethod -Uri "$Base/object_info" -TimeoutSec 120

$OfficialBaseInt8 = Test-Path (Join-Path $ComfyRoot 'models\diffusion_models\wan_animate_2_int8_convrot.safetensors')
$BaseQ4 = Test-Path (Join-Path $ComfyRoot 'models\diffusion_models\Wan-Animate-2-14B-Q4_K_M.gguf')

if ($OfficialBaseInt8) {
    $Route = 'official_base_int8_convrot'
    $Required = @(
        'WanAnimate2ToVideo',
        'LoadImage',
        'LoadVideo',
        'UNETLoader',
        'CLIPLoader',
        'CLIPVisionLoader',
        'CLIPVisionEncode',
        'VAELoader'
    )
} elseif ($BaseQ4) {
    $Route = 'base_q4_gguf'
    $Required = @(
        'RebelsGGUFUnetLoaderMeta',
        'WanAnimate2ToVideo',
        'LoadImage',
        'LoadVideo',
        'CLIPLoader',
        'CLIPVisionLoader',
        'CLIPVisionEncode',
        'VAELoader'
    )
} else {
    throw 'No supported Base model file was found. Do not continue with the workflow.'
}

Write-Host "Detected model route: $Route" -ForegroundColor Cyan
Write-Host ''
Write-Host 'Required node classes:' -ForegroundColor Cyan
$failed = $false
foreach ($name in $Required) {
    $present = $ObjectInfo.PSObject.Properties.Name -contains $name
    if ($present) {
        Write-Host "[OK]   $name" -ForegroundColor Green
    } else {
        Write-Host "[MISS] $name" -ForegroundColor Red
        $failed = $true
    }
}

$Models = Join-Path $ComfyRoot 'models'
$MainModel = if ($Route -eq 'official_base_int8_convrot') {
    Join-Path $Models 'diffusion_models\wan_animate_2_int8_convrot.safetensors'
} else {
    Join-Path $Models 'diffusion_models\Wan-Animate-2-14B-Q4_K_M.gguf'
}

$Files = @(
    $MainModel,
    (Join-Path $Models 'text_encoders\umt5_xxl_fp8_e4m3fn_scaled.safetensors'),
    (Join-Path $Models 'clip_vision\clip_vision_h.safetensors'),
    (Join-Path $Models 'vae\Wan2_1_VAE_bf16.safetensors'),
    (Join-Path $ComfyRoot 'input\exilada_master.png')
)

Write-Host ''
Write-Host 'Required files:' -ForegroundColor Cyan
foreach ($f in $Files) {
    if (Test-Path $f) {
        $size = [math]::Round((Get-Item $f).Length / 1GB, 3)
        Write-Host "[OK]   $f ($size GB)" -ForegroundColor Green
    } else {
        Write-Host "[MISS] $f" -ForegroundColor Red
        $failed = $true
    }
}

$Probe = [ordered]@{ route = $Route }
foreach ($name in @('RebelsGGUFUnetLoaderMeta','UNETLoader','WanAnimate2ToVideo','LoadVideo','CLIPLoader','CLIPVisionLoader','CLIPVisionEncode','VAELoader')) {
    if ($ObjectInfo.PSObject.Properties.Name -contains $name) {
        $Probe[$name] = $ObjectInfo.$name
    }
}
$ProbePath = Join-Path $Workspace 'object_info_spike.json'
$Probe | ConvertTo-Json -Depth 40 | Set-Content -Path $ProbePath -Encoding utf8
Write-Host ''
Write-Host "Saved exact installed node schemas to: $ProbePath" -ForegroundColor Green

foreach ($Log in @($StderrLog, $StdoutLog)) {
    if (Test-Path $Log) {
        $imports = Select-String -Path $Log -Pattern 'IMPORT FAILED|Rebels|GGUF|WanAnimate2|Animate2' -SimpleMatch:$false
        if ($imports) {
            Write-Host ''
            Write-Host "Relevant startup log lines from $Log"
            $imports | Select-Object -Last 40 | ForEach-Object { $_.Line }
        }
    }
}

if ($failed) {
    throw 'Wan-Animate-2 CLI preflight FAILED. Do not build or run the workflow yet.'
}

Write-Host ''
Write-Host 'CLI preflight PASSED.' -ForegroundColor Green
if ($Route -eq 'base_q4_gguf') {
    Write-Host 'GGUF route: model class=WAN_Animate2 must be proven at actual model load.' -ForegroundColor Yellow
} else {
    Write-Host 'Official Base INT8 route: actual Animate-2 model loading will be checked during the workflow run.' -ForegroundColor Yellow
}
Write-Host 'Next: prepare the 17-frame driver, then build the headless API workflow from these installed schemas.'
