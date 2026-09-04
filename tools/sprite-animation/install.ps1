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
    Require-Command 'nvcc.exe' 'CUDA Toolkit is required for the local CUDA build. Install CUDA 12.x and reopen PowerShell.'

    # Resolve the exact CUDA Toolkit from nvcc instead of relying on CMake auto-detection.
    $Nvcc = (Get-Command 'nvcc.exe').Source
    $CudaBin = Split-Path -Parent $Nvcc
    $CudaPath = Split-Path -Parent $CudaBin
    $CudaVsIntegration = Join-Path $CudaPath 'extras\visual_studio_integration\MSBuildExtensions'

    if (-not (Test-Path $CudaVsIntegration)) {
        throw @"
CUDA was found at:
  $CudaPath

but its Visual Studio integration files were not found at:
  $CudaVsIntegration

This happens when CUDA was installed before Visual Studio Build Tools and the VS integration component was not installed.
Repair/reinstall CUDA 12.9 after Visual Studio 2022 Build Tools is present, then run install.ps1 again.
"@
    }

    # Resolve a VS2022 instance that actually contains the x64/x86 C++ toolchain.
    $VsWhere = Join-Path ${env:ProgramFiles(x86)} 'Microsoft Visual Studio\Installer\vswhere.exe'
    if (-not (Test-Path $VsWhere)) {
        throw 'vswhere.exe was not found. Install Visual Studio 2022 Build Tools with the Desktop development with C++ workload.'
    }

    $VsInstall = (& $VsWhere -latest -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath | Select-Object -First 1)
    if (-not $VsInstall) {
        throw 'Visual Studio 2022 C++ build tools were not detected. Install the Desktop development with C++ workload.'
    }

    $MsBuild = Join-Path $VsInstall 'MSBuild\Current\Bin\MSBuild.exe'
    if (-not (Test-Path $MsBuild)) {
        throw "Visual Studio was detected at $VsInstall, but MSBuild.exe was not found. Repair the Visual Studio 2022 Build Tools installation."
    }

    Write-Host "Visual Studio: $VsInstall"
    Write-Host "CUDA Toolkit:  $CudaPath"
    Write-Host "nvcc:          $Nvcc"

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

    # CMake caches generator/toolset/compiler flags. Reconfigure from a clean build tree.
    if (Test-Path $Build) {
        Write-Host 'Removing stale CMake cache...'
        Remove-Item -Recurse -Force $Build
    }

    Write-Host 'Configuring CUDA build with explicit VS2022 + x64 + CUDA toolset...'
    Write-Host 'MSVC large-object support: /bigobj'
    $Toolset = "host=x64,cuda=$CudaPath"
    & cmake.exe `
        -S $Vendor `
        -B $Build `
        -G 'Visual Studio 17 2022' `
        -A x64 `
        -T $Toolset `
        -DSD_CUDA=ON `
        -DCMAKE_CUDA_ARCHITECTURES=86 `
        '-DCMAKE_CXX_FLAGS=/bigobj'

    if ($LASTEXITCODE -ne 0) {
        throw @"
CMake configure failed even with the toolchain selected explicitly.

Detected Visual Studio:
  $VsInstall
Detected CUDA:
  $CudaPath
CUDA VS integration:
  $CudaVsIntegration
Generator:
  Visual Studio 17 2022 / x64
Toolset:
  $Toolset
C++ flags:
  /bigobj

Do not install anything else yet. Send the CMake output above so the exact integration/compiler failure can be fixed.
"@
    }

    # stable-diffusion.cpp contains very large translation units. On MSVC, unrestricted
    # parallel compilation can trigger D8040/process-spawn failures even with ample RAM.
    Write-Host 'Building sd-cli.exe with bounded parallelism (2 jobs)...'
    & cmake.exe --build $Build --config Release --parallel 2
    if ($LASTEXITCODE -ne 0) { throw 'stable-diffusion.cpp build failed.' }

    $Exe = Get-ChildItem -Path $Build -Recurse -Filter 'sd-cli.exe' | Select-Object -First 1
    if (-not $Exe) { throw "Build completed but sd-cli.exe was not found under $Build" }

    New-Item -ItemType Directory -Path $Bin -Force | Out-Null
    Copy-Item $Exe.FullName (Join-Path $Bin 'sd-cli.exe') -Force

    # Copy the stable-diffusion DLL and local dependency DLLs next to sd-cli when produced by the build.
    $BuiltDlls = Get-ChildItem -Path $Build -Recurse -Filter '*.dll' -ErrorAction SilentlyContinue
    foreach ($Dll in $BuiltDlls) {
        Copy-Item $Dll.FullName (Join-Path $Bin $Dll.Name) -Force
    }

    Write-Host "Installed: $(Join-Path $Bin 'sd-cli.exe')" -ForegroundColor Green
}

# The helper scripts only need Pillow. Use an already-installed supported Python
# instead of forcing an old interpreter. Pillow 12.x supports CPython 3.10-3.14.
$PyLauncher = Get-Command 'py.exe' -ErrorAction SilentlyContinue
$PythonCommand = $null
$PythonArgs = @()

if ($PyLauncher) {
    foreach ($Version in @('3.14', '3.13', '3.12', '3.11', '3.10')) {
        & py.exe "-$Version" -c 'import sys; print(sys.version_info[:2])' *> $null
        if ($LASTEXITCODE -eq 0) {
            $PythonCommand = 'py.exe'
            $PythonArgs = @("-$Version")
            break
        }
    }
}

if (-not $PythonCommand) {
    $Python = Get-Command 'python.exe' -ErrorAction SilentlyContinue
    if ($Python) {
        $DetectedVersion = & $Python.Source -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")'
        if ($LASTEXITCODE -eq 0 -and $DetectedVersion -match '^3\.(10|11|12|13|14)$') {
            $PythonCommand = $Python.Source
        }
    }
}

if (-not $PythonCommand) {
    throw 'No supported Python was found. Install CPython 3.10 through 3.14, then run install.ps1 again.'
}

$BaseVersion = & $PythonCommand @PythonArgs -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")'
Write-Host "Python:        $BaseVersion"

$VenvPython = Join-Path $Venv 'Scripts\python.exe'
if (Test-Path $VenvPython) {
    $VenvVersion = & $VenvPython -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")'
    if ($LASTEXITCODE -ne 0 -or $VenvVersion -notmatch '^3\.(10|11|12|13|14)$') {
        Write-Host "Removing incompatible virtual environment ($VenvVersion)..."
        Remove-Item -Recurse -Force $Venv
    } else {
        Write-Host "Reusing virtual environment (Python $VenvVersion)..."
    }
}

if (-not (Test-Path $VenvPython)) {
    Write-Host "Creating virtual environment with Python $BaseVersion..."
    & $PythonCommand @PythonArgs -m venv $Venv
    if ($LASTEXITCODE -ne 0) { throw 'Failed to create Python virtual environment.' }
}

$VenvPython = Join-Path $Venv 'Scripts\python.exe'
& $VenvPython -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) { throw 'pip upgrade failed.' }
& $VenvPython -m pip install 'Pillow==12.3.0'
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
