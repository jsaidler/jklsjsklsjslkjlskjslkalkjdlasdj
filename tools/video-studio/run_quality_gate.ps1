param(
    [string]$Presets = "production,quality",
    [int]$Seed = 0
)

$ErrorActionPreference = "Stop"

$ToolRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$Config = Join-Path $ToolRoot "config.json"
$Example = Join-Path $ToolRoot "config.example.json"
$Python = "Z:\AI\MiniMaxH3\ComfyUI_windows_portable\python_embeded\python.exe"
$Runner = Join-Path $ToolRoot "run_quality_gate.py"

if (-not (Test-Path $Python)) {
    throw "Python portátil do MiniMaxH3 não encontrado: $Python"
}

if (-not (Test-Path $Runner)) {
    throw "Quality gate runner não encontrado: $Runner"
}

if (-not (Test-Path $Config)) {
    if (-not (Test-Path $Example)) {
        throw "Nem config.json nem config.example.json foram encontrados."
    }
    Copy-Item $Example $Config
    Write-Host "Criado config.json a partir do exemplo atual."
}

Write-Host ""
Write-Host "VIDEO-STUDIO-QUALITY-01"
Write-Host "======================="
Write-Host "Presets: $Presets"
Write-Host "Seed: $Seed"
Write-Host ""
Write-Host "ATENÇÃO: conclusão da inferência NÃO significa aprovação de qualidade."
Write-Host "Os MP4s precisam de revisão visual humana antes de qualquer promoção."
Write-Host ""

& $Python $Runner `
    --config $Config `
    --presets $Presets `
    --seed $Seed

exit $LASTEXITCODE
