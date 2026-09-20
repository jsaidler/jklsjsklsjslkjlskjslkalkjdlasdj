param(
    [string]$WanRoot = 'Z:\AI\WanAnimate2',
    [string]$Output = 'Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\unified\wan_animate2_node_contract_preflight.json'
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version 2.0

$Python = 'python'
$Inspector = Join-Path $PSScriptRoot 'inspect_wan_animate2_node_contract.py'

if (-not (Test-Path -LiteralPath $Inspector -PathType Leaf)) {
    throw ('Missing inspector: ' + $Inspector)
}
if (-not (Test-Path -LiteralPath $WanRoot -PathType Container)) {
    throw ('Missing Wan root: ' + $WanRoot)
}

Write-Host 'WAN-ANIMATE-2 NODE CONTRACT PREFLIGHT'
Write-Host '====================================='
Write-Host ('Wan root: ' + $WanRoot)
Write-Host ('Inspector: ' + $Inspector)
Write-Host ('Output: ' + $Output)
Write-Host ''
Write-Host 'Static source/config/workflow inspection only.'
Write-Host 'No ComfyUI import, no torch/model load, no DWPose, no Wan inference.'
Write-Host ''

& $Python $Inspector '--wan-root' $WanRoot '--output' $Output
if ($LASTEXITCODE -ne 0) {
    throw ('Wan Animate2 node-contract preflight failed with exit code ' + $LASTEXITCODE)
}
if (-not (Test-Path -LiteralPath $Output -PathType Leaf)) {
    throw ('Expected preflight JSON missing: ' + $Output)
}

Write-Host ''
Write-Host 'WAN-ANIMATE-2 NODE CONTRACT PREFLIGHT: COMPLETE'
Write-Host ('JSON: ' + $Output)
Write-Host 'Paste the complete terminal output into ChatGPT before building the conditioning adapter.'
