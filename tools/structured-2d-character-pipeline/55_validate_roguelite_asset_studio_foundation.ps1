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
Write-Host '[PROOF] Validate one playable-character spec and one architecture-module spec.' -ForegroundColor Green
Write-Host ''

Write-Host '--- CHARACTER / INSTALLED ROUTES ---' -ForegroundColor Cyan
& $Python -s $Core $CharacterSpec
$characterInstalledExit = $LASTEXITCODE
if ($characterInstalledExit -ne 0) {
    Write-Host "Character installed-route query returned code $characterInstalledExit. This may be expected when no installed static model satisfies the generic contract." -ForegroundColor Yellow
}

Write-Host ''
Write-Host '--- CHARACTER / PLANNING ROUTES INCLUDING UNINSTALLED CANDIDATES ---' -ForegroundColor Cyan
& $Python -s $Core $CharacterSpec --include-uninstalled
if ($LASTEXITCODE -ne 0) { Fail 'character planning-route validation failed' }

Write-Host ''
Write-Host '--- ENVIRONMENT / INSTALLED ROUTES ---' -ForegroundColor Cyan
& $Python -s $Core $EnvironmentSpec
$environmentInstalledExit = $LASTEXITCODE
if ($environmentInstalledExit -ne 0) {
    Write-Host "Environment installed-route query returned code $environmentInstalledExit. This is expected until a generic static generator is installed/accepted." -ForegroundColor Yellow
}

Write-Host ''
Write-Host '--- ENVIRONMENT / PLANNING ROUTES INCLUDING UNINSTALLED CANDIDATES ---' -ForegroundColor Cyan
& $Python -s $Core $EnvironmentSpec --include-uninstalled
if ($LASTEXITCODE -ne 0) { Fail 'environment planning-route validation failed' }

Write-Host ''
Write-Host 'RUNNER55-ASSET-STUDIO-FOUNDATION: PASS - generic schema/router validated for character and environment specs.' -ForegroundColor Green
Write-Host 'No models were downloaded or executed.' -ForegroundColor Green
