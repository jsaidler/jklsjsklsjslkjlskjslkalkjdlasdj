param(
    [string]$WanGpRoot = 'Z:\AI\WanGP',
    [string]$SystemPython = 'C:\Python314\python.exe',
    [string]$CacheRoot = "$env:LOCALAPPDATA\VideoStudio"
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version 2.0

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$ReportDir = Join-Path $RepoRoot 'tools\video-studio\reports'
New-Item -ItemType Directory -Force -Path $ReportDir | Out-Null
$Stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$Report = Join-Path $ReportDir ('wangp_runtime_bootstrap_' + $Stamp + '.txt')
$Lines = New-Object 'System.Collections.Generic.List[string]'

function Emit([string]$Text) {
    Write-Host $Text
    $Lines.Add($Text) | Out-Null
}

function Section([string]$Title) {
    Emit ''
    Emit $Title
    Emit ('=' * $Title.Length)
}

function Assert-Exit([string]$Message) {
    if ($LASTEXITCODE -ne 0) {
        throw $Message
    }
}

function Find-UvExe {
    $Cmd = Get-Command uv -ErrorAction SilentlyContinue
    if ($null -ne $Cmd -and (Test-Path -LiteralPath $Cmd.Source -PathType Leaf)) {
        return $Cmd.Source
    }

    try {
        $UserScripts = (& $SystemPython -c "import sysconfig; print(sysconfig.get_path('scripts', scheme='nt_user'))").Trim()
        if ($UserScripts) {
            $Candidate = Join-Path $UserScripts 'uv.exe'
            if (Test-Path -LiteralPath $Candidate -PathType Leaf) {
                return $Candidate
            }
        }
    } catch {
    }

    $PythonUserRoot = Join-Path $env:APPDATA 'Python'
    if (Test-Path -LiteralPath $PythonUserRoot -PathType Container) {
        $Found = Get-ChildItem -LiteralPath $PythonUserRoot -Recurse -File -Filter 'uv.exe' -ErrorAction SilentlyContinue |
            Select-Object -First 1
        if ($null -ne $Found) {
            return $Found.FullName
        }
    }

    return $null
}

Emit 'WANGP-RUNTIME-BOOTSTRAP-02'
Emit ('Status date: ' + (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'))
Emit ('Repo root: ' + $RepoRoot)
Emit ('WanGP root: ' + $WanGpRoot)

Section 'PREREQUISITES'
if (-not (Test-Path -LiteralPath $SystemPython -PathType Leaf)) {
    throw ('Bootstrap Python not found: ' + $SystemPython)
}
Emit ('Bootstrap Python: ' + $SystemPython)

$Git = Get-Command git -ErrorAction SilentlyContinue
if ($null -eq $Git) {
    throw 'git not found in PATH.'
}
Emit ('git: ' + $Git.Source)

Section 'WANGP CHECKOUT'
if (Test-Path -LiteralPath (Join-Path $WanGpRoot '.git') -PathType Container) {
    Emit 'Existing WanGP checkout found; updating with fast-forward only.'
    & git -C $WanGpRoot pull --ff-only
    Assert-Exit 'WanGP git pull failed.'
}
if (-not (Test-Path -LiteralPath (Join-Path $WanGpRoot '.git') -PathType Container)) {
    Emit 'WanGP checkout missing; cloning.'
    & git clone --depth 1 'https://github.com/deepbeepmeep/Wan2GP.git' $WanGpRoot
    Assert-Exit 'WanGP git clone failed.'
}
$WanCommit = (& git -C $WanGpRoot rev-parse HEAD).Trim()
Emit ('WanGP commit: ' + $WanCommit)

Section 'CACHE PLACEMENT'
$env:UV_CACHE_DIR = Join-Path $CacheRoot 'uv-cache'
$env:PIP_CACHE_DIR = Join-Path $CacheRoot 'pip-cache'
New-Item -ItemType Directory -Force -Path $env:UV_CACHE_DIR | Out-Null
New-Item -ItemType Directory -Force -Path $env:PIP_CACHE_DIR | Out-Null
Emit ('UV cache: ' + $env:UV_CACHE_DIR)
Emit ('PIP cache: ' + $env:PIP_CACHE_DIR)

Section 'UV DISCOVERY'
$UvExe = Find-UvExe
if ($null -eq $UvExe) {
    Emit 'uv.exe not found; installing/upgrading uv with bootstrap Python.'
    & $SystemPython -m pip install --user --upgrade uv
    Assert-Exit 'uv installation failed.'
    $UvExe = Find-UvExe
}
if ($null -eq $UvExe -or -not (Test-Path -LiteralPath $UvExe -PathType Leaf)) {
    throw 'uv was installed but uv.exe could not be located.'
}
$UvDir = Split-Path -Parent $UvExe
$env:Path = $UvDir + ';' + $env:Path
Emit ('uv.exe: ' + $UvExe)
$UvVersion = (& $UvExe --version).Trim()
Assert-Exit 'uv executable failed.'
Emit ('uv version: ' + $UvVersion)

Section 'PYTHON 3.11 RUNTIME'
& $UvExe python install 3.11.14
Assert-Exit 'uv failed to prepare Python 3.11.14.'
Emit 'Python 3.11.14 managed runtime: READY'

Section 'WANGP ENVIRONMENT'
$WanPython = Join-Path $WanGpRoot 'env_uv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $WanPython -PathType Leaf)) {
    Emit 'WanGP env_uv is not complete; running official automatic installer.'
    Push-Location $WanGpRoot
    try {
        & $SystemPython '.\setup.py' install --env uv --auto
        Assert-Exit 'WanGP automatic installation failed.'
    }
    finally {
        Pop-Location
    }
}
if (-not (Test-Path -LiteralPath $WanPython -PathType Leaf)) {
    throw ('WanGP Python not created: ' + $WanPython)
}
Emit ('WanGP Python: ' + $WanPython)

Section 'WANGP RUNTIME'
$RuntimeInfo = & $WanPython -c "import sys, torch; print('Python:', sys.version.split()[0]); print('Torch:', torch.__version__); print('CUDA runtime:', torch.version.cuda); print('CUDA available:', torch.cuda.is_available()); print('GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'NONE')"
Assert-Exit 'WanGP runtime verification failed.'
foreach ($Line in $RuntimeInfo) { Emit ([string]$Line) }

$CudaOk = (& $WanPython -c "import torch; print('YES' if torch.cuda.is_available() else 'NO')").Trim()
if ($CudaOk -ne 'YES') {
    throw 'WanGP installed, but CUDA is not available inside its environment.'
}

Section 'DISK AFTER RUNTIME'
$Drive = Get-PSDrive -Name 'Z' -ErrorAction Stop
$FreeGb = [math]::Round($Drive.Free / 1GB, 2)
$WanGpBytes = (Get-ChildItem -LiteralPath $WanGpRoot -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
if ($null -eq $WanGpBytes) { $WanGpBytes = 0 }
$WanGpGb = [math]::Round($WanGpBytes / 1GB, 2)
Emit ('WanGP total: ' + $WanGpGb + ' GB')
Emit ('Free Z: ' + $FreeGb + ' GB')

if ($FreeGb -ge 32) {
    Emit 'HUNYUAN PAYLOAD GATE: PASS'
    Emit 'Next step: prepare the minimal Hunyuan Avatar INT8 payload with no duplicate model cache.'
} else {
    Emit 'HUNYUAN PAYLOAD GATE: HOLD'
    Emit 'Do not download model weights yet; free additional space first.'
}

Set-Content -LiteralPath $Report -Value $Lines -Encoding UTF8
Section 'REPORT'
Write-Host $Report
