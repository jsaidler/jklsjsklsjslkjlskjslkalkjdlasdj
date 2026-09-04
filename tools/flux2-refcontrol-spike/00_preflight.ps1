param(
    [string]$RepoRoot = 'D:\GOOGLE DRIVE\DEV\Roguelite',
    [string]$Workspace = 'D:\AI\Flux2RefControlSpike',
    [string]$Master = 'D:\GOOGLE DRIVE\DEV\Roguelite\assets\source\characters\exilada\reference\exilada_master.png',
    [double]$MinFreeGB = 25.0
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Write-Check([string]$Name, [bool]$Ok, [string]$Detail) {
    $tag = if ($Ok) { '[OK]' } else { '[FAIL]' }
    $color = if ($Ok) { 'Green' } else { 'Red' }
    Write-Host ("{0} {1}: {2}" -f $tag, $Name, $Detail) -ForegroundColor $color
}

Write-Host ''
Write-Host 'FLUX.2 Klein + RefControl Pose spike — PRE-FLIGHT ONLY' -ForegroundColor Cyan
Write-Host 'No files will be downloaded and no software will be installed by this script.' -ForegroundColor Cyan
Write-Host ''

$failures = @()

# OS
$os = Get-CimInstance Win32_OperatingSystem
$osText = "$($os.Caption) $($os.Version) build $($os.BuildNumber)"
$osOk = $os.Caption -match 'Windows 11'
Write-Check 'Operating system' $osOk $osText
if (-not $osOk) { $failures += 'Windows 11 not detected' }

# RAM
$ramGB = [math]::Round(($os.TotalVisibleMemorySize * 1KB) / 1GB, 1)
$ramOk = $ramGB -ge 32
Write-Check 'System RAM' $ramOk ("{0} GB detected (minimum for this spike: 32 GB)" -f $ramGB)
if (-not $ramOk) { $failures += 'Less than 32 GB system RAM' }

# NVIDIA tool / GPU
$nvidia = Get-Command nvidia-smi.exe -ErrorAction SilentlyContinue
if ($null -eq $nvidia) {
    Write-Check 'nvidia-smi' $false 'nvidia-smi.exe not found on PATH'
    $failures += 'nvidia-smi.exe not found'
} else {
    $query = & nvidia-smi.exe --query-gpu=name,memory.total,driver_version --format=csv,noheader,nounits 2>$null
    if ($LASTEXITCODE -ne 0 -or -not $query) {
        Write-Check 'NVIDIA GPU query' $false 'nvidia-smi could not query the GPU'
        $failures += 'nvidia-smi query failed'
    } else {
        $first = ($query | Select-Object -First 1).ToString().Split(',')
        $gpuName = $first[0].Trim()
        $vramMiB = [double]$first[1].Trim()
        $driver = $first[2].Trim()
        $vramGB = [math]::Round($vramMiB / 1024, 2)
        $gpuOk = $vramMiB -ge 11000
        Write-Check 'NVIDIA GPU' $gpuOk ("{0}; VRAM {1} GB; driver {2}" -f $gpuName, $vramGB, $driver)
        if (-not $gpuOk) { $failures += 'Less than ~11 GB NVIDIA VRAM detected' }
    }
}

# Disk hosting D:\AI workspace
$driveName = ([System.IO.Path]::GetPathRoot($Workspace)).TrimEnd('\').TrimEnd(':')
$drive = Get-PSDrive -Name $driveName -ErrorAction Stop
$freeGB = [math]::Round($drive.Free / 1GB, 2)
$diskOk = $freeGB -ge $MinFreeGB
Write-Check 'Free disk space' $diskOk ("{0}: has {1} GB free; spike requires at least {2} GB free" -f $driveName, $freeGB, $MinFreeGB)
if (-not $diskOk) { $failures += ("Less than {0} GB free on {1}:" -f $MinFreeGB, $driveName) }

# Repository and canonical master
$repoOk = Test-Path $RepoRoot -PathType Container
Write-Check 'Repository root' $repoOk $RepoRoot
if (-not $repoOk) { $failures += 'Repository root not found' }

$masterOk = Test-Path $Master -PathType Leaf
if ($masterOk) {
    $masterInfo = Get-Item $Master
    Write-Check 'Canonical Exilada master' $true ("{0} ({1:N0} bytes)" -f $Master, $masterInfo.Length)
} else {
    Write-Check 'Canonical Exilada master' $false $Master
    $failures += 'Canonical Exilada master not found'
}

# CLI tools used in later steps
$git = Get-Command git.exe -ErrorAction SilentlyContinue
Write-Check 'git' ($null -ne $git) ($(if ($git) { (& git --version) } else { 'not found' }))
if ($null -eq $git) { $failures += 'git not found' }

$winget = Get-Command winget.exe -ErrorAction SilentlyContinue
Write-Check 'winget' ($null -ne $winget) ($(if ($winget) { 'available' } else { 'not found' }))

$sevenZipCandidates = @(
    (Get-Command 7z.exe -ErrorAction SilentlyContinue | ForEach-Object Source),
    'C:\Program Files\7-Zip\7z.exe'
) | Where-Object { $_ -and (Test-Path $_) } | Select-Object -Unique
$sevenZipOk = @($sevenZipCandidates).Count -gt 0
Write-Check '7-Zip' $sevenZipOk ($(if ($sevenZipOk) { $sevenZipCandidates[0] } else { 'not installed/found; next step can install it with winget' }))

# Existing workspace status (informational only)
if (Test-Path $Workspace) {
    $itemCount = @(Get-ChildItem -Force $Workspace -ErrorAction SilentlyContinue).Count
    Write-Host ("[INFO] Workspace already exists: {0} ({1} top-level items)" -f $Workspace, $itemCount) -ForegroundColor Yellow
} else {
    Write-Host ("[INFO] Workspace does not exist yet: {0}" -f $Workspace) -ForegroundColor DarkGray
}

# Existing portable status (informational only)
$portableRoot = Join-Path $Workspace 'ComfyUI_windows_portable'
$portablePython = Join-Path $portableRoot 'python_embeded\python.exe'
$comfyMain = Join-Path $portableRoot 'ComfyUI\main.py'
if ((Test-Path $portablePython) -and (Test-Path $comfyMain)) {
    Write-Host "[INFO] A complete-looking ComfyUI portable already exists at $portableRoot" -ForegroundColor Yellow
} elseif (Test-Path $portableRoot) {
    Write-Host "[INFO] Partial/incomplete ComfyUI portable folder exists at $portableRoot" -ForegroundColor Yellow
} else {
    Write-Host '[INFO] No ComfyUI portable detected in the spike workspace.' -ForegroundColor DarkGray
}

Write-Host ''
if ($failures.Count -gt 0) {
    Write-Host 'PRE-FLIGHT: FAIL' -ForegroundColor Red
    $failures | ForEach-Object { Write-Host "  - $_" -ForegroundColor Red }
    exit 1
}

Write-Host 'PRE-FLIGHT: PASS' -ForegroundColor Green
if (-not $sevenZipOk) {
    Write-Host '7-Zip is the only optional prerequisite missing; it can be installed in Step 2.' -ForegroundColor Yellow
}
Write-Host 'No downloads or installations were performed.' -ForegroundColor Green
exit 0
