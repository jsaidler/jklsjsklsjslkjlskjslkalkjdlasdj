param(
    [string]$ProjectRepoRoot = 'D:\GOOGLE DRIVE\DEV\Roguelite',
    [string]$SsdRoot = 'Z:\AI\SpriteSheetDiffusionSpike',
    [switch]$AcceptAnacondaTos
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Fail([string]$Message) {
    Write-Host "SSD-ENV: FAIL - $Message" -ForegroundColor Red
    exit 1
}

function Find-Conda {
    $cmd = Get-Command conda.exe -ErrorAction SilentlyContinue
    if ($null -ne $cmd) { return $cmd.Source }

    $candidates = @(
        (Join-Path $env:USERPROFILE 'miniconda3\Scripts\conda.exe'),
        (Join-Path $env:LOCALAPPDATA 'miniconda3\Scripts\conda.exe'),
        (Join-Path $env:LOCALAPPDATA 'Programs\Miniconda3\Scripts\conda.exe'),
        'C:\ProgramData\miniconda3\Scripts\conda.exe'
    )
    foreach ($candidate in $candidates) {
        if (Test-Path -LiteralPath $candidate -PathType Leaf) { return $candidate }
    }
    return $null
}

$UpstreamRepo = Join-Path $SsdRoot 'repo'
$Inference = Join-Path $UpstreamRepo 'ModelTraining\inference.py'
$InferenceConfig = Join-Path $UpstreamRepo 'ModelTraining\configs\prompts\inference.yaml'
$Marker = Join-Path $SsdRoot 'ssd_environment_bootstrap.json'
$AnacondaChannels = @(
    'https://repo.anaconda.com/pkgs/main',
    'https://repo.anaconda.com/pkgs/r',
    'https://repo.anaconda.com/pkgs/msys2'
)

Write-Host ''
Write-Host 'Roguelite - Sprite Sheet Diffusion environment bootstrap' -ForegroundColor Cyan
Write-Host '[SCOPE] Miniconda + isolated Python 3.10 environment only.' -ForegroundColor Green
Write-Host '[LOCK] No model downloads in this gate.' -ForegroundColor Green
Write-Host '[LOCK] No large SSD dependency install in this gate.' -ForegroundColor Green
Write-Host '[INFO] PowerShell is used natively; no CMD-only cd /d syntax.' -ForegroundColor DarkGray
Write-Host ''

if (-not (Test-Path -LiteralPath $UpstreamRepo -PathType Container)) {
    Fail "SSD upstream clone missing: $UpstreamRepo"
}
if (-not (Test-Path -LiteralPath $Inference -PathType Leaf)) {
    Fail "SSD inference entry point missing: $Inference"
}
if (-not (Test-Path -LiteralPath $InferenceConfig -PathType Leaf)) {
    Fail "SSD inference config missing: $InferenceConfig"
}

Write-Host "[OK] Upstream clone: $UpstreamRepo" -ForegroundColor Green
Write-Host "[OK] Inference:      $Inference" -ForegroundColor Green
Write-Host "[OK] Config:         $InferenceConfig" -ForegroundColor Green

$Conda = Find-Conda
if ($null -eq $Conda) {
    $winget = Get-Command winget.exe -ErrorAction SilentlyContinue
    if ($null -eq $winget) {
        Fail 'conda is absent and winget.exe is unavailable; cannot bootstrap Miniconda automatically.'
    }

    Write-Host '[INSTALL] Miniconda not found. Installing Anaconda.Miniconda3 with WinGet...' -ForegroundColor Yellow
    & $winget.Source install --id Anaconda.Miniconda3 --exact --scope user --accept-package-agreements --accept-source-agreements --silent
    if ($LASTEXITCODE -ne 0) {
        Fail "WinGet Miniconda install exited with code $LASTEXITCODE"
    }

    $Conda = Find-Conda
    if ($null -eq $Conda) {
        Fail 'Miniconda installation completed but conda.exe could not be located in known user/system locations.'
    }
}

Write-Host "[OK] conda.exe: $Conda" -ForegroundColor Green

$envExists = $false
try {
    $probe = & $Conda run -n ssd python --version 2>&1
    if ($LASTEXITCODE -eq 0 -and (($probe | Out-String) -match 'Python\s+3\.10\.')) {
        $envExists = $true
    }
} catch {
    $envExists = $false
}

$tosAcceptedThisRun = $false
if (-not $envExists) {
    if (-not $AcceptAnacondaTos) {
        Write-Host ''
        Write-Host '[ACTION REQUIRED] Miniconda is installed, but Anaconda now requires Terms of Service acceptance for its default channels before package creation.' -ForegroundColor Yellow
        Write-Host '[LEGAL] The runner will not accept these terms silently.' -ForegroundColor Yellow
        Write-Host '[LEGAL] If you agree to Anaconda Terms of Service for the following channels, rerun this runner with -AcceptAnacondaTos:' -ForegroundColor Yellow
        foreach ($channel in $AnacondaChannels) {
            Write-Host "  $channel" -ForegroundColor DarkYellow
        }
        Write-Host ''
        Write-Host 'Example:' -ForegroundColor Cyan
        Write-Host 'powershell.exe -NoProfile -ExecutionPolicy Bypass -File "D:\GOOGLE DRIVE\DEV\Roguelite\tools\structured-2d-character-pipeline\24_bootstrap_ssd_environment.ps1" -AcceptAnacondaTos' -ForegroundColor Cyan
        Fail 'Anaconda Terms of Service acceptance is required before conda create; explicit user opt-in was not supplied.'
    }

    Write-Host '[TOS] Explicit -AcceptAnacondaTos supplied. Accepting Anaconda Terms of Service for required default channels...' -ForegroundColor Yellow
    foreach ($channel in $AnacondaChannels) {
        & $Conda tos accept --override-channels --channel $channel
        if ($LASTEXITCODE -ne 0) {
            Fail "Anaconda ToS acceptance failed for channel $channel with code $LASTEXITCODE"
        }
    }
    $tosAcceptedThisRun = $true

    Write-Host '[CREATE] Creating isolated conda env ssd with Python 3.10 + pip...' -ForegroundColor Yellow
    & $Conda create -n ssd python=3.10 pip -y
    if ($LASTEXITCODE -ne 0) {
        Fail "conda create exited with code $LASTEXITCODE"
    }
}

$pythonVersionOutput = & $Conda run -n ssd python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Fail 'conda env ssd exists but Python probe failed.'
}
$pythonVersion = ($pythonVersionOutput | Out-String).Trim()
if ($pythonVersion -notmatch '^Python\s+3\.10\.') {
    Fail "expected Python 3.10.x in env ssd, got: $pythonVersion"
}

$pipVersionOutput = & $Conda run -n ssd python -m pip --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Fail 'pip probe failed inside env ssd.'
}
$pipVersion = ($pipVersionOutput | Out-String).Trim()

$markerData = [ordered]@{
    gate = 'SSD_ENV_BOOTSTRAP'
    status = 'PASS'
    date = (Get-Date).ToString('o')
    ssd_root = $SsdRoot
    upstream_repo = $UpstreamRepo
    inference = $Inference
    inference_config = $InferenceConfig
    conda_exe = $Conda
    environment = 'ssd'
    python = $pythonVersion
    pip = $pipVersion
    anaconda_tos_explicit_opt_in_switch = [bool]$AcceptAnacondaTos
    anaconda_tos_accepted_by_runner_this_run = $tosAcceptedThisRun
    anaconda_channels = $AnacondaChannels
    models_downloaded_by_this_gate = $false
    large_dependencies_installed_by_this_gate = $false
}
$markerData | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $Marker -Encoding UTF8

Write-Host ''
Write-Host 'SSD-ENV: PASS' -ForegroundColor Green
Write-Host "PYTHON: $pythonVersion" -ForegroundColor Green
Write-Host "PIP:    $pipVersion" -ForegroundColor Green
Write-Host "MARKER: $Marker" -ForegroundColor Cyan
Write-Host ''
Write-Host '[NEXT] Stop here. Dependency/model bootstrap is a separate documented gate.' -ForegroundColor Yellow
