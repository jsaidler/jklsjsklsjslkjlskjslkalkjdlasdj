param(
    [switch]$NoOpen,
    [switch]$PreflightOnly
)

$ErrorActionPreference = "Stop"

$ToolRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$Config = Join-Path $ToolRoot "config.json"
$Example = Join-Path $ToolRoot "config.example.json"
$Python = "Z:\AI\MiniMaxH3\ComfyUI_windows_portable\python_embeded\python.exe"
$App = Join-Path $ToolRoot "video_studio.py"

if (-not (Test-Path $Python)) {
    throw "Python portátil do MiniMaxH3 não encontrado: $Python"
}

if (-not (Test-Path $App)) {
    throw "Backend do Video Studio não encontrado: $App"
}

if (-not (Test-Path $Config)) {
    if (-not (Test-Path $Example)) {
        throw "Nem config.json nem config.example.json foram encontrados."
    }
    Copy-Item $Example $Config
    Write-Host "Criado config.json a partir do exemplo."
    Write-Host "As referências atuais já apontam para Z:\AI\MiniMaxH3."
}

if ($PreflightOnly) {
    & $Python $App --config $Config preflight
    exit $LASTEXITCODE
}

$argsList = @($App, "--config", $Config, "serve")
if ($NoOpen) {
    $argsList += "--no-open"
}

Write-Host ""
Write-Host "Local Video Studio — PROTÓTIPO"
Write-Host "==============================="
Write-Host "ATENÇÃO: a arquitetura foi validada, mas a qualidade visual de produção ainda NÃO foi aprovada."
Write-Host "Use tools\video-studio\run_quality_gate.ps1 para o benchmark controlado."
Write-Host ""
Write-Host "Config: $Config"
Write-Host "Interface: http://127.0.0.1:8765/"
Write-Host "Feche esta janela ou pressione Ctrl+C para encerrar o Studio."
Write-Host ""

& $Python @argsList
exit $LASTEXITCODE
