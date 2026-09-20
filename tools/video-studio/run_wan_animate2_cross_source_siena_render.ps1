param(
    [int]$Port = 8192,
    [int]$TimeoutMinutes = 180
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version 2.0

$Python = 'python'
$Runner = Join-Path $PSScriptRoot 'run_wan_animate2_cross_source_siena_render.py'
if (-not (Test-Path -LiteralPath $Runner -PathType Leaf)) {
    throw ('Missing runner: ' + $Runner)
}

Write-Host 'WAN-ANIMATE-2 CROSS-SOURCE SIENA GATE'
Write-Host '======================================'
Write-Host 'PRIMARY reference + real SIENA driving video.'
Write-Host 'This WILL run the installed Wan-Animate-2 BF16 model.'
Write-Host 'Expected runtime on RTX 3060 12 GB: similar to the prior ~80 minute baseline.'
Write-Host 'No downloads, no DWPose, no new model.'
Write-Host ''

& $Python $Runner '--port' $Port '--timeout-minutes' $TimeoutMinutes
if ($LASTEXITCODE -ne 0) {
    throw ('Cross-source SIENA render gate failed with exit code ' + $LASTEXITCODE)
}
