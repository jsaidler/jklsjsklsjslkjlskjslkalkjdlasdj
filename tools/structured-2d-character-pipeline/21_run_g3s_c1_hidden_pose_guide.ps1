param(
    [string]$RepoRoot = 'D:\GOOGLE DRIVE\DEV\Roguelite',
    [string]$PipelineWorkspace = 'Z:\AI\RogueliteCharacterPipeline'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Write-Host ''
Write-Host 'Roguelite - G3S-C1A' -ForegroundColor Cyan
Write-Host 'RUNNER DISABLED: the V6 skinned-body guide path is superseded.' -ForegroundColor Yellow
Write-Host 'Canonical architecture now uses a hidden skeleton/rig only for pose/laterality/depth/contact control.' -ForegroundColor Yellow
Write-Host 'Do not repair or rerun the MPFB skinned-body guide. A skeleton-only C1A runner must replace this file.' -ForegroundColor Yellow
Write-Host ''
exit 1
