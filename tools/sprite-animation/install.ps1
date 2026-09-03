param(
    [switch]$SkipModels,
    [switch]$SkipBuild
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Vendor = Join-Path $Root 'vendor\stable-diffusion.cpp'
$Build = Join-Path $Root 'build\sdcpp'
$Bin = Join-Path $Root 'bin'
$Venv = Join-Path $Root '.venv'

function Require-Command([string]$Name, [string]$Hint) {
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "$Name was not found.`n$Hint"
    }
}

Require-Command 'git.exe' 'Install Git for Windows. Example: winget install --id Git.Git -e'
Require-Command 'cmake.exe' 'Install CMake. Example: winget install --id Kitware.CMake -e'
Require-Command 'nvidia-smi.exe' 'NVIDIA driver tools were not found. Install/update the NVIDIA driver first.'

if (-not $SkipBuild) {
    Require-Command 'nvcc.exe' 'CUDA Toolkit is required for the local CUDA build. Install a current CUDA 12.x toolkit and reopen PowerShell.'

    if (-not (Test-Path $Vendor)) {
        New-Item -ItemType Directory -Path (Split-Path -Parent $Vendor) -Force | Out-Null
        Write-Host 'Cloning stable-diffusion.cpp Sprite-Sheet-Diffusion branch...'
        & git.exe clone --depth 1 --branch feat/sprite-sheet-diffusion `
            https://github.com/fszontagh/stable-diffusion.cpp.git $Vendor
        if ($LASTEXITCODE -ne 0) { throw 'git clone failed.' }
    } else {
        Write-Host 'Updating stable-diffusion.cpp fork...'
        & git.exe -C $Vendor fetch origin feat/sprite-sheet-diffusion
        if ($LASTEXITCODE -ne 0) { throw 'git fetch failed.' }
        & git.exe -C $Vendor checkout feat/sprite-sheet-diffusion
        if ($LASTEXITCODE -ne 0) { throw 'git checkout failed.' }
        & git.exe -C $Vendor pull --ff-only origin feat/sprite-sheet-diffusion
        if ($LASTEXITCODE -ne 0) { throw 'git pull failed.' }
    }

    & git.exe -C $Vendor submodule update --init --recursive
    if ($LASTEXITCODE -ne 0) { throw 'git submodule update failed.' }

    Write-Host 'Configuring CUDA build...'
    & cmake.exe -S $Vendor -B $Build -DSD_CUDA=ON -DCMAKE_BUILD_TYPE=Release
    if ($LASTEXITCODE -ne 0) {
        throw @'
CMake configure failed. On Windows this usually means the Visual Studio 2022 C++ build tools are missing.
Install "Visual Studio 2022 Build Tools" with the "Desktop development with C++" workload, then run install.ps1 again.
'@
    }

    Write-Host 'Building sd-cli.exe...'
    & cmake.exe --build $Build --config Release --parallel
    if ($LASTEXITCODE -ne 0) { throw 'stable-diffusion.cpp build failed.' }

    $Exe = Get-ChildItem -Path $Build -Recurse -Filter 'sd-cli.exe' | Select-Object -First 1
    if (-not $Exe) { throw "Build completed but sd-cli.exe was not found under $Build" }

    New-Item -ItemType Directory -Path $Bin -Force | Out-Null
    Copy-Item $Exe.FullName (Join-Path $Bin 'sd-cli.exe') -Force
    Write-Host "Installed: $(Join-Path $Bin 'sd-cli.exe')" -ForegroundColor Green
}

$PyLauncher = Get-Command 'py.exe' -ErrorAction SilentlyContinue
$Python = Get-Command 'python.exe' -ErrorAction SilentlyContinue
if (-not $PyLauncher -and -not $Python) {
    throw 'Python was not found. Install Python 3.10 or newer. Example: winget install --id Python.Python.3.10 -e'
}

if (-not (Test-Path $Venv)) {
    if ($PyLauncher) {
        & py.exe -3.10 -m venv $Venv
        if ($LASTEXITCODE -ne 0) { & py.exe -3 -m venv $Venv }
    } else {
        & python.exe -m venv $Venv
    }
    if ($LASTEXITCODE -ne 0) { throw 'Failed to create Python virtual environment.' }
}

$VenvPython = Join-Path $Venv 'Scripts\python.exe'
& $VenvPython -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) { throw 'pip upgrade failed.' }
& $VenvPython -m pip install 'Pillow==10.4.0'
if ($LASTEXITCODE -ne 0) { throw 'Pillow install failed.' }

if (-not $SkipModels) {
    & (Join-Path $Root 'download_models.ps1')
    if ($LASTEXITCODE -ne 0) { throw 'Model download step failed.' }
}

& $VenvPython (Join-Path $Root 'prepare_walk_poses.py') `
    --width 512 --height 768 --cycles 3 --output (Join-Path $Root 'poses\walk')
if ($LASTEXITCODE -ne 0) { throw 'Pose generation failed.' }

Write-Host ''
Write-Host 'Sprite animation toolchain is installed.' -ForegroundColor Green
Write-Host 'Next: .\run_walk.ps1 -Reference "C:\path\to\exilada_frame1.png" -Profile quality'
