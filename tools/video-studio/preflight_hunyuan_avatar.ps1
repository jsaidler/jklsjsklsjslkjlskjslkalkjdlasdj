param(
    [string]$AiRoot = 'Z:\AI',
    [string]$WanGpRoot = 'Z:\AI\WanGP'
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version 2.0

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$ReportDir = Join-Path $RepoRoot 'tools\video-studio\reports'
New-Item -ItemType Directory -Force -Path $ReportDir | Out-Null
$Stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$Report = Join-Path $ReportDir ('hunyuan_avatar_preflight_' + $Stamp + '.txt')
$Lines = New-Object 'System.Collections.Generic.List[string]'

function Add-Line([string]$Text) {
    $Lines.Add($Text) | Out-Null
}

function Section([string]$Title) {
    Write-Host ''
    Write-Host $Title
    Write-Host ('=' * $Title.Length)
    Add-Line ''
    Add-Line $Title
    Add-Line ('=' * $Title.Length)
}

function Emit([string]$Text) {
    Write-Host $Text
    Add-Line $Text
}

Add-Line 'HUNYUAN-AVATAR-PREFLIGHT-01'
Add-Line ('Status date: ' + (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'))
Add-Line ('Repo root: ' + $RepoRoot)
Add-Line ('AI root: ' + $AiRoot)
Add-Line ('WanGP root: ' + $WanGpRoot)

Section 'SYSTEM'
try {
    $Gpu = (& nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader) -join "`n"
} catch {
    $Gpu = 'nvidia-smi unavailable'
}
Emit $Gpu
$RamGb = [math]::Round((Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1GB, 1)
Emit ('RAM GB: ' + $RamGb)

$DriveName = ([System.IO.Path]::GetPathRoot($AiRoot)).TrimEnd('\')
$Drive = Get-PSDrive -Name $DriveName.TrimEnd(':') -ErrorAction Stop
$FreeGb = [math]::Round($Drive.Free / 1GB, 2)
Emit ('Free space on ' + $DriveName + ': ' + $FreeGb + ' GB')
if ($FreeGb -ge 35) {
    Emit 'Disk reserve >= 35 GB: PASS'
} else {
    Emit 'Disk reserve >= 35 GB: FAIL/WARN - cleanup required before model install.'
}

Section 'COMMANDS'
$CommandNames = @('git','ffmpeg','conda','py','python')
foreach ($Name in $CommandNames) {
    $Cmd = Get-Command $Name -ErrorAction SilentlyContinue
    if ($null -ne $Cmd) {
        Emit ($Name + ': FOUND -> ' + $Cmd.Source)
    } else {
        Emit ($Name + ': MISSING')
    }
}

Section 'BENCHMARK INPUTS'
$RefImage = 'Z:\AI\WanAnimate2\input\video_studio\wan_s2v_benchmark\joao_wan_s2v_ref.png'
$Audio = 'Z:\AI\WanAnimate2\input\video_studio\wan_s2v_benchmark\joao_wan_s2v_test_4p5s.wav'
foreach ($Path in @($RefImage,$Audio)) {
    if (Test-Path -LiteralPath $Path -PathType Leaf) {
        $SizeMb = [math]::Round((Get-Item -LiteralPath $Path).Length / 1MB, 2)
        Emit ('FOUND  ' + $Path + '  (' + $SizeMb + ' MB)')
    } else {
        Emit ('MISSING  ' + $Path)
    }
}

Section 'WANGP INSTALLATION'
if (Test-Path -LiteralPath $WanGpRoot -PathType Container) {
    Emit ('WanGP root: FOUND -> ' + $WanGpRoot)
    $GitDir = Join-Path $WanGpRoot '.git'
    if (Test-Path -LiteralPath $GitDir -PathType Container) {
        Emit 'WanGP git checkout: FOUND'
        try {
            $Branch = (& git -C $WanGpRoot rev-parse --abbrev-ref HEAD).Trim()
            $Commit = (& git -C $WanGpRoot rev-parse HEAD).Trim()
            Emit ('WanGP branch: ' + $Branch)
            Emit ('WanGP commit: ' + $Commit)
        } catch {
            Emit ('WanGP git metadata read failed: ' + $_.Exception.Message)
        }
    } else {
        Emit 'WanGP git checkout: NOT FOUND'
    }
} else {
    Emit ('WanGP root: MISSING -> ' + $WanGpRoot)
}

Section 'HUNYUAN PAYLOAD INVENTORY'
$ExpectedNames = @(
    'hunyuan_video_avatar_720_quanto_bf16_int8.safetensors',
    'llava-llama-3-8b-v1_1_vlm_quanto_int8.safetensors',
    'hunyuan_video_VAE_fp32.safetensors',
    'detface.pt'
)

foreach ($Name in $ExpectedNames) {
    $Found = Get-ChildItem -LiteralPath $AiRoot -Recurse -File -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -eq $Name } |
        Select-Object -First 1
    if ($null -ne $Found) {
        $SizeGb = [math]::Round($Found.Length / 1GB, 3)
        Emit ('FOUND  ' + $Name + '  ' + $SizeGb + ' GB  -> ' + $Found.FullName)
    } else {
        Emit ('MISSING  ' + $Name)
    }
}

$ClipFound = Get-ChildItem -LiteralPath $AiRoot -Recurse -File -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -eq 'model.safetensors' -and $_.FullName -match 'clip_vit_large_patch14' } |
    Select-Object -First 1
if ($null -ne $ClipFound) {
    Emit ('FOUND  CLIP ViT-L/14 -> ' + $ClipFound.FullName)
} else {
    Emit 'MISSING  CLIP ViT-L/14 model.safetensors'
}

$WhisperFound = Get-ChildItem -LiteralPath $AiRoot -Recurse -File -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -eq 'model.safetensors' -and $_.FullName -match 'whisper-tiny' } |
    Select-Object -First 1
if ($null -ne $WhisperFound) {
    Emit ('FOUND  Whisper Tiny -> ' + $WhisperFound.FullName)
} else {
    Emit 'MISSING  Whisper Tiny model.safetensors'
}

Section 'PLANNED DIRECT GATE'
Emit 'Renderer: Hunyuan Video Avatar 720p 13B via WanGP'
Emit 'Checkpoint target: quantized INT8 (~13.4 GB)'
Emit 'Reference: reuse exact Wan benchmark identity image'
Emit 'Audio: reuse exact 4.5 s recorded speech'
Emit 'Native WanGP Hunyuan Avatar FPS: 25'
Emit 'Default segment: 129 frames (~5.16 s)'
Emit 'Wan 20-step A/B: PAUSED until Hunyuan comparison'

Section 'ASSESSMENT'
$Blocking = New-Object 'System.Collections.Generic.List[string]'
if (-not (Test-Path -LiteralPath $RefImage -PathType Leaf)) { $Blocking.Add('reference image missing') | Out-Null }
if (-not (Test-Path -LiteralPath $Audio -PathType Leaf)) { $Blocking.Add('benchmark audio missing') | Out-Null }
if ($FreeGb -lt 35) { $Blocking.Add('less than 35 GB free on AI drive') | Out-Null }
if ($null -eq (Get-Command git -ErrorAction SilentlyContinue)) { $Blocking.Add('git missing') | Out-Null }
if ($null -eq (Get-Command ffmpeg -ErrorAction SilentlyContinue)) { $Blocking.Add('ffmpeg missing') | Out-Null }

if ($Blocking.Count -eq 0) {
    Emit 'PRECHECK PASS: no basic blocker detected for WanGP/Hunyuan setup.'
    if (-not (Test-Path -LiteralPath $WanGpRoot -PathType Container)) {
        Emit 'NEXT: bootstrap WanGP in Z:\AI\WanGP, then download only the Hunyuan Avatar INT8 dependency set.'
    } else {
        Emit 'NEXT: inspect/update existing WanGP and prepare Hunyuan Avatar model through its native model manager/API.'
    }
} else {
    Emit ('BLOCKERS: ' + ($Blocking -join '; '))
}

Set-Content -LiteralPath $Report -Value $Lines -Encoding UTF8
Write-Host ''
Write-Host 'REPORT:'
Write-Host $Report
