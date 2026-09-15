param(
    [string]$AiRoot = "Z:\AI",
    [string]$WanRoot = "Z:\AI\WanAnimate2",
    [string]$OutputDir = ".\tools\video-studio\reports"
)

$ErrorActionPreference = "Stop"

function Write-Section {
    param([string]$Title)

    Write-Host ""
    Write-Host $Title
    Write-Host ("=" * $Title.Length)
}

function Add-Line {
    param(
        [System.Collections.Generic.List[string]]$Lines,
        [string]$Text
    )

    $Lines.Add($Text) | Out-Null
}

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$ResolvedOutputDir = Join-Path $RepoRoot ($OutputDir -replace '^\.\\','')
New-Item -ItemType Directory -Force -Path $ResolvedOutputDir | Out-Null

$Stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$Report = Join-Path $ResolvedOutputDir "wan_s2v_preflight_$Stamp.txt"
$Lines = New-Object 'System.Collections.Generic.List[string]'

Add-Line $Lines "WAN-S2V-PREFLIGHT-01"
Add-Line $Lines "Status date: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Add-Line $Lines "Repo root: $RepoRoot"
Add-Line $Lines "AI root: $AiRoot"
Add-Line $Lines "Wan root: $WanRoot"
Add-Line $Lines ""

Write-Section "SYSTEM"
$Nvidia = ""
try {
    $Nvidia = (& nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader) -join "`n"
} catch {
    $Nvidia = "nvidia-smi unavailable"
}
Write-Host $Nvidia
Add-Line $Lines "SYSTEM"
Add-Line $Lines $Nvidia
Add-Line $Lines "RAM GB: $([math]::Round((Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1GB, 1))"
Add-Line $Lines ""

Write-Section "RUNTIME CHECKS"
$Checks = @(
    @{ Name = 'Wan root'; Path = $WanRoot },
    @{ Name = 'MiniMaxH3 root'; Path = (Join-Path $AiRoot 'MiniMaxH3') },
    @{ Name = 'QwenImageEdit root'; Path = (Join-Path $AiRoot 'QwenImageEdit') },
    @{ Name = 'Flux2Klein root'; Path = (Join-Path $AiRoot 'Flux2Klein') }
)
foreach ($Check in $Checks) {
    $Ok = Test-Path $Check.Path
    $Msg = "{0}: {1}" -f $Check.Name, ($(if ($Ok) { 'FOUND' } else { 'MISSING' }))
    Write-Host $Msg
    Add-Line $Lines $Msg
    if ($Ok) {
        Add-Line $Lines "  $($Check.Path)"
    }
}
Add-Line $Lines ""

Write-Section "FFMPEG / PYTHON"
$Ffmpeg = Get-Command ffmpeg -ErrorAction SilentlyContinue
$PythonEmbedded = Join-Path $AiRoot 'MiniMaxH3\ComfyUI_windows_portable\python_embeded\python.exe'
$FfmpegMsg = if ($Ffmpeg) { "ffmpeg: FOUND -> $($Ffmpeg.Source)" } else { 'ffmpeg: MISSING' }
$PythonMsg = if (Test-Path $PythonEmbedded) { "embedded python: FOUND -> $PythonEmbedded" } else { "embedded python: MISSING -> $PythonEmbedded" }
Write-Host $FfmpegMsg
Write-Host $PythonMsg
Add-Line $Lines $FfmpegMsg
Add-Line $Lines $PythonMsg
Add-Line $Lines ""

Write-Section "WAN MODEL INVENTORY"
Add-Line $Lines "WAN MODEL INVENTORY"

$HasAnimate = $false
$HasS2V = $false
$HasCosy = $false

if (Test-Path $WanRoot) {
    $Weights = @(
        Get-ChildItem $WanRoot -Recurse -File -ErrorAction SilentlyContinue |
            Where-Object { $_.Extension -in '.safetensors','.gguf','.pth','.pt','.bin','.ckpt','.onnx' } |
            Sort-Object Length -Descending
    )

    if ($Weights.Count -eq 0) {
        Write-Host 'No weights found.'
        Add-Line $Lines 'No weights found.'
    } else {
        foreach ($Weight in $Weights) {
            $Line = ('{0,8:N2} GB  {1}' -f ($Weight.Length / 1GB), $Weight.FullName)
            Write-Host $Line
            Add-Line $Lines $Line
        }
    }

    Add-Line $Lines ""

    $WanS2V = @(
        $Weights | Where-Object { $_.Name -match 's2v|speech' -or $_.FullName -match 's2v|speech' }
    )
    $Cosy = @(
        Get-ChildItem $WanRoot -Recurse -File -ErrorAction SilentlyContinue |
            Where-Object { $_.Name -match 'cosy|cosyvoice' }
    )

    $HasAnimate = @($Weights | Where-Object { $_.Name -match 'animate' }).Count -gt 0
    $HasS2V = $WanS2V.Count -gt 0
    $HasCosy = $Cosy.Count -gt 0

    $AnimateMsg = if ($HasAnimate) { 'Wan Animate payload: PRESENT' } else { 'Wan Animate payload: NOT FOUND' }
    $S2VMsg = if ($HasS2V) { 'Wan S2V payload: PRESENT' } else { 'Wan S2V payload: NOT FOUND' }
    $CosyMsg = if ($HasCosy) { 'CosyVoice payload/scripts: PRESENT' } else { 'CosyVoice payload/scripts: NOT FOUND' }

    Write-Host ""
    Write-Host $AnimateMsg
    Write-Host $S2VMsg
    Write-Host $CosyMsg
    Add-Line $Lines $AnimateMsg
    Add-Line $Lines $S2VMsg
    Add-Line $Lines $CosyMsg
} else {
    Write-Host 'Wan root missing.'
    Add-Line $Lines 'Wan root missing.'
}
Add-Line $Lines ""

Write-Section "COMFY / WORKFLOW DISCOVERY"
$WorkflowFiles = @()
$SearchRoots = @(
    $WanRoot,
    (Join-Path $AiRoot 'MiniMaxH3'),
    (Join-Path $AiRoot 'QwenImageEdit'),
    (Join-Path $AiRoot 'Flux2Klein')
) | Where-Object { Test-Path $_ }

foreach ($Root in $SearchRoots) {
    $WorkflowFiles += @(
        Get-ChildItem $Root -Recurse -File -ErrorAction SilentlyContinue |
            Where-Object { $_.Extension -eq '.json' -and $_.FullName -match 'workflow|wan|s2v|speech|avatar|hunyuan|echomimic' }
    )
}

$WorkflowFiles = @($WorkflowFiles | Sort-Object FullName -Unique)
if ($WorkflowFiles.Count -eq 0) {
    $WorkflowMsg = 'No obvious workflow JSONs found for Wan/Hunyuan/EchoMimic.'
    Write-Host $WorkflowMsg
    Add-Line $Lines $WorkflowMsg
} else {
    foreach ($Workflow in $WorkflowFiles) {
        Write-Host $Workflow.FullName
        Add-Line $Lines $Workflow.FullName
    }
}
Add-Line $Lines ""

Write-Section "ASSESSMENT"
$Assessment = @()
if (-not (Test-Path $WanRoot)) {
    $Assessment += 'WAN ROOT MISSING: cannot benchmark Wan2.2-S2V until runtime folder exists.'
}
if (Test-Path $WanRoot) {
    if (-not $HasS2V) {
        $Assessment += 'S2V CHECKPOINT NOT FOUND: current Wan folder appears not to contain the speech-to-video model.'
    }
    if (-not $HasCosy) {
        $Assessment += 'COSYVOICE COMPONENTS NOT FOUND in Wan root.'
    }
    if ($HasAnimate -and -not $HasS2V) {
        $Assessment += 'Current Wan installation appears Animate-oriented, not S2V-oriented.'
    }
}
if (-not $Ffmpeg) {
    $Assessment += 'FFMPEG MISSING from PATH.'
}
if (-not (Test-Path $PythonEmbedded)) {
    $Assessment += 'Embedded python missing from MiniMaxH3 runtime.'
}
if ($Assessment.Count -eq 0) {
    $Assessment += 'Preflight did not detect a blocking filesystem issue for the next Wan2.2-S2V benchmark.'
}
foreach ($Item in $Assessment) {
    Write-Host $Item
    Add-Line $Lines $Item
}
Add-Line $Lines ""

Write-Section "NEXT STEP"
$Next = 'Send this report back into chat. Do not download new models before reviewing which S2V/CosyVoice components are already missing.'
Write-Host $Next
Add-Line $Lines $Next

Set-Content -Path $Report -Value $Lines -Encoding UTF8

Write-Host ""
Write-Host "REPORT WRITTEN:"
Write-Host $Report
