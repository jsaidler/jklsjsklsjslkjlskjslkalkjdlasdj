param(
    [string]$WanRoot = 'Z:\AI\WanAnimate2',
    [string]$WanGpRoot = 'Z:\AI\WanGP',
    [string]$Output = 'Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\unified\wan_animate2_conditioning_preflight.json'
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version 2.0

$Python = Join-Path $WanGpRoot 'env_uv\Scripts\python.exe'
$Inspector = Join-Path $PSScriptRoot 'inspect_wan_animate2_conditioning.py'

foreach ($item in @(
    @{ Name='WanGP Python'; Path=$Python },
    @{ Name='Wan Animate2 install'; Path=$WanRoot },
    @{ Name='Conditioning inspector'; Path=$Inspector }
)) {
    if ($item.Name -eq 'Wan Animate2 install') {
        if (-not (Test-Path -LiteralPath $item.Path -PathType Container)) { throw ('Missing ' + $item.Name + ': ' + $item.Path) }
    } elseif (-not (Test-Path -LiteralPath $item.Path -PathType Leaf)) {
        throw ('Missing ' + $item.Name + ': ' + $item.Path)
    }
}

Write-Host 'WAN-ANIMATE-2 LOCAL CONDITIONING PREFLIGHT'
Write-Host '=========================================='
Write-Host ('Wan root: ' + $WanRoot)
Write-Host ('Inspector: ' + $Inspector)
Write-Host ('Output: ' + $Output)
Write-Host ''
Write-Host 'Static source/config inspection only.'
Write-Host 'No ComfyUI launch, no torch/model import, no DWPose, no Wan inference.'
Write-Host ''

$Saved = $ErrorActionPreference
try {
    $ErrorActionPreference = 'Continue'
    & $Python $Inspector '--root' $WanRoot '--output' $Output
    $Exit = $LASTEXITCODE
} finally {
    $ErrorActionPreference = $Saved
}
if ($Exit -ne 0) { throw ('Wan Animate2 conditioning preflight failed with exit code ' + $Exit) }
if (-not (Test-Path -LiteralPath $Output -PathType Leaf)) { throw 'Preflight JSON was not produced.' }

Write-Host ''
Write-Host 'WAN-ANIMATE-2 CONDITIONING PREFLIGHT: COMPLETE'
Write-Host ('JSON: ' + $Output)
Write-Host 'Paste the complete terminal output into ChatGPT before any render spike.'
