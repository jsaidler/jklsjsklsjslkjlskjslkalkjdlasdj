param(
    [int]$Port = 8192,
    [int]$TimeoutMinutes = 180
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version 2.0

$Python = 'python'
$Runner = Join-Path $PSScriptRoot 'run_wan_animate2_primary_baseline_render.py'
if (-not (Test-Path -LiteralPath $Runner -PathType Leaf)) {
    throw ('Missing runner: ' + $Runner)
}

Write-Host 'WAN-ANIMATE-2 PRIMARY BASELINE RENDER GATE'
Write-Host '========================================'
Write-Host 'This is the first actual Wan-Animate-2 inference in the behavioral route.'
Write-Host 'It deliberately uses one clean PRIMARY RGB motion span only.'
Write-Host 'The multi-source xfade driver is NOT used in this gate.'
Write-Host 'No downloads and no new model installation occur.'
Write-Host ('Comfy API port: ' + $Port)
Write-Host ('Timeout: ' + $TimeoutMinutes + ' min')
Write-Host ''

& $Python $Runner '--port' $Port '--timeout-minutes' $TimeoutMinutes
if ($LASTEXITCODE -ne 0) {
    throw ('Wan Animate2 primary baseline gate failed with exit code ' + $LASTEXITCODE)
}

Write-Host ''
Write-Host 'WAN-ANIMATE-2 PRIMARY BASELINE GATE: COMPLETE'
Write-Host 'Paste the complete terminal output and upload the final MP4 reported by the runner.'
