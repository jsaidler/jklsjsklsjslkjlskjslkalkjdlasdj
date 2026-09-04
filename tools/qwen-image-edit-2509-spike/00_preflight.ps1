param(
    [string]$RepoRoot = 'D:\GOOGLE DRIVE\DEV\Roguelite',
    [string]$Workspace = 'Z:\AI\QwenImageEditSpike',
    [string]$Master = 'D:\GOOGLE DRIVE\DEV\Roguelite\assets\source\characters\exilada\reference\exilada_master.png',
    [double]$MinFreeGB = 40.0
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Write-Check([string]$Name, [bool]$Ok, [string]$Detail) {
    $tag = if ($Ok) { '[OK]' } else { '[FAIL]' }
    $color = if ($Ok) { 'Green' } else { 'Red' }
    Write-Host ("{0} {1}: {2}" -f $tag, $Name, $Detail) -ForegroundColor $color
}

Write-Host ''
Write-Host 'Qwen-Image-Edit-2509 keypoint spike - STEP 1: PRE-FLIGHT ONLY' -ForegroundColor Cyan
Write-Host 'No downloads, installs, model loads, or inference are performed.' -ForegroundColor Cyan
Write-Host ''

$failures = @()

$os = Get-CimInstance Win32_OperatingSystem
$osText = "$($os.Caption) $($os.Version) build $($os.BuildNumber)"
$osOk = $os.Caption -match 'Windows 11'
Write-Check 'Operating system' $osOk $osText
if (-not $osOk) { $failures += 'Windows 11 not detected' }

$ramGB = [math]::Round(($os.TotalVisibleMemorySize * 1KB) / 1GB, 1)
$ramOk = $ramGB -ge 40
Write-Check 'System RAM' $ramOk ("{0} GB detected; this spike requires >=40 GB to leave room for CPU offload" -f $ramGB)
if (-not $ramOk) { $failures += 'Less than 40 GB system RAM' }

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

$driveName = ([System.IO.Path]::GetPathRoot($Workspace)).TrimEnd('\').TrimEnd(':')
$drive = Get-PSDrive -Name $driveName -ErrorAction Stop
$freeGB = [math]::Round($drive.Free / 1GB, 2)
$diskOk = $freeGB -ge $MinFreeGB
Write-Check 'Free SSD space' $diskOk ("{0}: has {1} GB free; require at least {2} GB before setup" -f $driveName, $freeGB, $MinFreeGB)
if (-not $diskOk) { $failures += ("Less than {0} GB free on {1}:" -f $MinFreeGB, $driveName) }

$repoOk = Test-Path $RepoRoot -PathType Container
Write-Check 'Repository root' $repoOk $RepoRoot
if (-not $repoOk) { $failures += 'Repository root not found' }

$masterOk = Test-Path $Master -PathType Leaf
if ($masterOk) {
    $masterInfo = Get-Item $Master
    $masterHash = (Get-FileHash -LiteralPath $Master -Algorithm SHA256).Hash.ToLowerInvariant()
    Write-Check 'Canonical Exilada master' $true ("{0} ({1:N0} bytes; sha256 {2})" -f $Master, $masterInfo.Length, $masterHash)
} else {
    Write-Check 'Canonical Exilada master' $false $Master
    $failures += 'Canonical Exilada master not found'
}

$git = Get-Command git.exe -ErrorAction SilentlyContinue
Write-Check 'git' ($null -ne $git) ($(if ($git) { (& git --version) } else { 'not found' }))
if ($null -eq $git) { $failures += 'git not found' }

$curl = Get-Command curl.exe -ErrorAction SilentlyContinue
Write-Check 'curl' ($null -ne $curl) ($(if ($curl) { 'available' } else { 'not found' }))
if ($null -eq $curl) { $failures += 'curl.exe not found' }

$winget = Get-Command winget.exe -ErrorAction SilentlyContinue
Write-Check 'winget' ($null -ne $winget) ($(if ($winget) { 'available' } else { 'not found; acceptable only if 7-Zip is already installed' }))

$sevenZipCandidates = @(
    (Get-Command 7z.exe -ErrorAction SilentlyContinue | ForEach-Object Source),
    'C:\Program Files\7-Zip\7z.exe'
) | Where-Object { $_ -and (Test-Path $_) } | Select-Object -Unique
$sevenZipOk = @($sevenZipCandidates).Count -gt 0
Write-Check '7-Zip' $sevenZipOk ($(if ($sevenZipOk) { $sevenZipCandidates[0] } else { 'not found; setup can install it with winget' }))
if (-not $sevenZipOk -and $null -eq $winget) { $failures += 'Neither 7-Zip nor winget is available' }

if (Test-Path $Workspace) {
    $itemCount = @(Get-ChildItem -Force $Workspace -ErrorAction SilentlyContinue).Count
    Write-Host ("[INFO] Workspace already exists: {0} ({1} top-level items)" -f $Workspace, $itemCount) -ForegroundColor Yellow
} else {
    Write-Host ("[INFO] Workspace does not exist yet: {0}" -f $Workspace) -ForegroundColor DarkGray
}

Write-Host ''
Write-Host 'Planned first model set (no download yet):' -ForegroundColor DarkGray
Write-Host '  - Qwen-Image-Edit-2509 Q4_0 GGUF: ~11.9 GB'
Write-Host '  - Qwen 2.5 VL 7B FP8 text encoder: ~9.38 GB'
Write-Host '  - Qwen Image VAE: ~0.25 GB'
Write-Host '  - no Lightning LoRA in the first topology test'
Write-Host ''

if ($failures.Count -gt 0) {
    Write-Host 'STEP 1 PRE-FLIGHT: FAIL' -ForegroundColor Red
    $failures | ForEach-Object { Write-Host "  - $_" -ForegroundColor Red }
    exit 1
}

Write-Host 'STEP 1 PRE-FLIGHT: PASS' -ForegroundColor Green
Write-Host 'No downloads, installations, model loads, or inference were performed.' -ForegroundColor Green
exit 0
