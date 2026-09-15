param(
    [int]$Port = 8192,
    [int]$Seed = 0,
    [int]$TimeoutMinutes = 360,
    [switch]$LowVram
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version 2.0

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\.." )).Path
$Runner = Join-Path $PSScriptRoot "run_wan_s2v_benchmark.py"

$PythonCandidates = @(
    "Z:\AI\Flux2Klein\ComfyUI_windows_portable\python_embeded\python.exe",
    "Z:\AI\MiniMaxH3\ComfyUI_windows_portable\python_embeded\python.exe",
    "Z:\AI\QwenImageEdit\ComfyUI_windows_portable\python_embeded\python.exe"
)

$Python = $PythonCandidates | Where-Object { Test-Path -LiteralPath $_ -PathType Leaf } | Select-Object -First 1
if ($null -eq $Python) {
    throw "No protected ComfyUI embedded Python runtime found."
}
if (-not (Test-Path -LiteralPath $Runner -PathType Leaf)) {
    throw "Wan S2V benchmark runner not found: $Runner"
}

Write-Host "WAN-S2V-BENCHMARK-01"
Write-Host "===================="
Write-Host "Repo: $RepoRoot"
Write-Host "Python: $Python"
Write-Host "Port: $Port"
Write-Host "Seed: $Seed"
Write-Host "Timeout: $TimeoutMinutes min"
Write-Host "LowVram: $LowVram"
Write-Host ""
Write-Host "This is one 77-frame quality benchmark. It does not approve production quality automatically."
Write-Host ""

$Args = @(
    $Runner,
    "--port", $Port,
    "--seed", $Seed,
    "--timeout-minutes", $TimeoutMinutes
)

if ($LowVram) {
    $Args += "--lowvram"
}

& $Python @Args
$ExitCode = $LASTEXITCODE
if ($ExitCode -ne 0) {
    throw "Wan S2V benchmark failed with exit code $ExitCode."
}
