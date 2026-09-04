param(
    [string]$Workspace = 'D:\AI\WanAnimate2',
    [int]$Port = 8188,
    [int]$Timeout = 7200
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Find-ComfyRoot([string]$Base) {
    foreach ($candidate in @($Base, (Join-Path $Base 'ComfyUI'))) {
        if (Test-Path (Join-Path $candidate 'main.py')) { return $candidate }
    }
    return $null
}

$ComfyRoot = Find-ComfyRoot $Workspace
if (-not $ComfyRoot) { throw "ComfyUI not found under $Workspace" }

$Python = @(
    (Join-Path $ComfyRoot '.venv\Scripts\python.exe'),
    (Join-Path $Workspace '.venv\Scripts\python.exe')
) | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $Python) { throw 'ComfyUI Python not found.' }

$Master = Join-Path $ComfyRoot 'input\exilada_master.png'
$Driver = Join-Path $ComfyRoot 'input\exilada_driver_17f.mp4'
foreach ($f in @($Master, $Driver)) {
    if (-not (Test-Path $f)) { throw "Required input missing: $f" }
}

$BaseUrl = "http://127.0.0.1:$Port"
try {
    $null = Invoke-RestMethod -Uri "$BaseUrl/system_stats" -TimeoutSec 3
} catch {
    throw "ComfyUI API is not running at $BaseUrl. Run .\inspect.ps1 first."
}

# Do not accidentally submit a second expensive job while a previous prompt is
# still active after a client-side WebSocket timeout.
$Queue = Invoke-RestMethod -Uri "$BaseUrl/queue" -TimeoutSec 10
if ($Queue.queue_running -and @($Queue.queue_running).Count -gt 0) {
    Write-Host 'ComfyUI already has a running prompt. Nothing new will be submitted.' -ForegroundColor Yellow
    Write-Host 'Use the existing prompt id with the /queue and /history API, or wait for it to finish.' -ForegroundColor Yellow
    $Queue.queue_running | ConvertTo-Json -Depth 20 | Write-Host
    exit 2
}

$Template = Join-Path $Workspace 'video_wan_animate2_official.json'
$Workflow = Join-Path $Workspace 'wan_animate2_exilada_17f.json'
$TemplateUrl = 'https://raw.githubusercontent.com/Comfy-Org/workflow_templates/main/templates/video_wan_animate2.json'

Write-Host 'Downloading current official Wan Animate 2 workflow template...' -ForegroundColor Cyan
Invoke-WebRequest -UseBasicParsing -Uri $TemplateUrl -OutFile $Template

$Builder = Join-Path $PSScriptRoot 'build_workflow.py'
& $Python $Builder $Template $Workflow
if ($LASTEXITCODE -ne 0) { throw 'Workflow builder failed.' }

Write-Host ''
Write-Host "Submitting headless Base-model validation workflow (timeout=${Timeout}s)..." -ForegroundColor Cyan
Push-Location 'D:\AI'
try {
    & py.exe -3.14 -m pipx run --spec comfy-cli comfy --workspace $Workspace run `
        --workflow $Workflow `
        --where local `
        --host 127.0.0.1 `
        --port $Port `
        --wait `
        --timeout $Timeout `
        --verbose
    if ($LASTEXITCODE -ne 0) { throw 'comfy run failed.' }
} finally {
    Pop-Location
}

Write-Host ''
Write-Host 'Relevant model/runtime log lines:' -ForegroundColor Cyan
$Logs = @(
    (Join-Path $Workspace "user\comfyui_${Port}_stderr.log"),
    (Join-Path $Workspace "user\comfyui_${Port}_stdout.log"),
    (Join-Path $ComfyRoot "user\comfyui_${Port}.log")
) | Select-Object -Unique
foreach ($log in $Logs) {
    if (Test-Path $log) {
        Write-Host "--- $log"
        Select-String -Path $log -Pattern 'Animate2|WanAnimate2|WAN_Animate2|wan_animate_2|loaded|Loading|VRAM|OOM|out of memory|ERROR|Traceback' -CaseSensitive:$false |
            Select-Object -Last 80 | ForEach-Object { $_.Line }
    }
}

$OutputDir = Join-Path $ComfyRoot 'output'
if (Test-Path $OutputDir) {
    $latest = Get-ChildItem -Path $OutputDir -Recurse -File |
        Where-Object { $_.Extension -match '^\.(mp4|webm|gif|webp)$' } |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 5
    if ($latest) {
        Write-Host ''
        Write-Host 'Newest generated media:' -ForegroundColor Green
        $latest | ForEach-Object { Write-Host $_.FullName }
    }
}
