param(
    [switch]$ForceLegacySingleSource
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version 2.0

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$InventoryScript = Join-Path $PSScriptRoot 'inventory_avatar_v_sources.ps1'

Write-Host 'AVATAR V SINGLE-SOURCE PREPARER — DEPRECATED'
Write-Host '==========================================='
Write-Host ''
Write-Host 'The project now has multiple good behavioral source videos.'
Write-Host 'Do not auto-select or auto-trim one source before inventorying the full set.'
Write-Host ''
Write-Host ('Use instead: ' + $InventoryScript)
Write-Host ''

if (-not $ForceLegacySingleSource) {
    throw 'Legacy single-source trimming is blocked by design. Run inventory_avatar_v_sources.ps1 first.'
}

throw 'Legacy trimming remains intentionally disabled. If a 15-second trim is required after source review, create it from the selected source and documented time range with a dedicated review-backed step.'
