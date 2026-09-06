param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Write-Host ''
Write-Host 'G3S-C0 V2 IS CLOSED.' -ForegroundColor Red
Write-Host 'Reason: a single monolithic 3/4 sprite cannot be turned into a valid walk by cutout/chain warping.' -ForegroundColor Yellow
Write-Host 'The reviewed V2 produced anatomically impossible limb arcs because sprite facing/laterality/rest-basis/occlusion were not representable by this method.' -ForegroundColor Yellow
Write-Host 'Do not rerun or patch this route with more pivots, overlaps, anchors or continuous-warp tuning.' -ForegroundColor Yellow
Write-Host 'See: tools/structured-2d-character-pipeline/g3s_c0_v2_visual_failure.json' -ForegroundColor Cyan
Write-Host 'Next architecture must use animation-ready persistent native-2D pose-specific source art.' -ForegroundColor Cyan
exit 1
