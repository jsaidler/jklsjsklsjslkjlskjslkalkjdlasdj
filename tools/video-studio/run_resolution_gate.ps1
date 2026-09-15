param(
    [string]$Preset = "quality",
    [int]$Seed = 0,
    [double]$Crf = 14
)

$ErrorActionPreference = "Stop"

$ToolRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$Config = Join-Path $ToolRoot "config.json"
$Example = Join-Path $ToolRoot "config.example.json"
$Python = "Z:\AI\MiniMaxH3\ComfyUI_windows_portable\python_embeded\python.exe"
$Runner = Join-Path $ToolRoot "run_resolution_gate.py"

if (-not (Test-Path $Python)) {
    throw "Python portatil do MiniMaxH3 nao encontrado: $Python"
}

if (-not (Test-Path $Runner)) {
    throw "Resolution gate runner nao encontrado: $Runner"
}

if (-not (Test-Path $Config)) {
    if (-not (Test-Path $Example)) {
        throw "Nem config.json nem config.example.json foram encontrados."
    }
    Copy-Item $Example $Config
    Write-Host "Criado config.json a partir do exemplo atual."
}

Write-Host ""
Write-Host "VIDEO-STUDIO-RESOLUTION-01"
Write-Host "=========================="
Write-Host "Preset: $Preset"
Write-Host "Seed: $Seed"
Write-Host "CRF de comparacao: $Crf"
Write-Host ""
Write-Host "Uma unica inferencia H3 sera salva duas vezes a partir dos mesmos frames."
Write-Host "Isso isola perda do encoder de falta de detalhe do modelo/VAE."
Write-Host ""

& $Python $Runner `
    --config $Config `
    --preset $Preset `
    --seed $Seed `
    --crf $Crf

exit $LASTEXITCODE
