param(
    [string]$ProjectRepoRoot = 'D:\GOOGLE DRIVE\DEV\Roguelite',
    [string]$Python = 'Z:\AI\FluxKontext\ComfyUI_windows_portable\python_embeded\python.exe'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Fail([string]$Message) {
    Write-Host "RUNNER55-ASSET-STUDIO-FOUNDATION: FAIL - $Message" -ForegroundColor Red
    exit 1
}

function Run-InstalledRouteCheck([string]$Label, [string]$Core, [string]$Spec, [string]$Python) {
    Write-Host "--- $Label / INSTALLED ROUTES ---" -ForegroundColor Cyan
    & $Python -s $Core $Spec
    $exitCode = $LASTEXITCODE
    if ($exitCode -eq 0) {
        return
    }
    if ($exitCode -eq 3) {
        Write-Host "$Label has no compatible installed route yet. This is an expected routing result, not a spec error." -ForegroundColor Yellow
        return
    }
    if ($exitCode -eq 2) {
        Fail "$Label spec/schema validation failed. SPEC_ERROR must never be treated as a missing-model condition."
    }
    Fail "$Label installed-route query failed with unexpected exit code $exitCode"
}

function Run-PlanningRouteCheck([string]$Label, [string]$Core, [string]$Spec, [string]$Python) {
    Write-Host "--- $Label / PLANNING ROUTES INCLUDING UNINSTALLED CANDIDATES ---" -ForegroundColor Cyan
    & $Python -s $Core $Spec --include-uninstalled
    $exitCode = $LASTEXITCODE
    if ($exitCode -eq 0) {
        return
    }
    if ($exitCode -eq 2) {
        Fail "$Label planning spec/schema validation failed"
    }
    if ($exitCode -eq 3) {
        Fail "$Label has no compatible planning route; registry/capability coverage is incomplete"
    }
    Fail "$Label planning-route query failed with unexpected exit code $exitCode"
}

$Core = Join-Path $ProjectRepoRoot 'tools\roguelite-asset-studio\asset_studio_core.py'
$CharacterSpec = Join-Path $ProjectRepoRoot 'tools\roguelite-asset-studio\examples\exilada_master.json'
$EnvironmentSpec = Join-Path $ProjectRepoRoot 'tools\roguelite-asset-studio\examples\ruined_gate.json'
$Registry = Join-Path $ProjectRepoRoot 'tools\roguelite-asset-studio\model_registry.json'
$Schema = Join-Path $ProjectRepoRoot 'tools\roguelite-asset-studio\asset_schema.json'

foreach ($f in @($Python,$Core,$CharacterSpec,$EnvironmentSpec,$Registry,$Schema)) {
    if (-not (Test-Path $f -PathType Leaf)) { Fail "required file missing: $f" }
}

Write-Host ''
Write-Host 'Roguelite Runner 55 - ASSET STUDIO FOUNDATION VALIDATION' -ForegroundColor Cyan
Write-Host '[SCOPE] Generic schema + model router. No image generation and no model download.' -ForegroundColor Green
Write-Host '[PROOF] Validate one playable-character spec with references and one reference-free architecture-module spec.' -ForegroundColor Green
Write-Host '[REGRESSION] Empty references[] is valid; SPEC_ERROR exit code 2 is fatal and can no longer be masked as a missing model.' -ForegroundColor Green
Write-Host ''

Run-InstalledRouteCheck 'CHARACTER' $Core $CharacterSpec $Python
Write-Host ''
Run-PlanningRouteCheck 'CHARACTER' $Core $CharacterSpec $Python
Write-Host ''
Run-InstalledRouteCheck 'ENVIRONMENT' $Core $EnvironmentSpec $Python
Write-Host ''
Run-PlanningRouteCheck 'ENVIRONMENT' $Core $EnvironmentSpec $Python

Write-Host ''
Write-Host 'RUNNER55-ASSET-STUDIO-FOUNDATION: PASS - generic schema/router validated for referenced character and reference-free environment specs.' -ForegroundColor Green
Write-Host 'No models were downloaded or executed.' -ForegroundColor Green
