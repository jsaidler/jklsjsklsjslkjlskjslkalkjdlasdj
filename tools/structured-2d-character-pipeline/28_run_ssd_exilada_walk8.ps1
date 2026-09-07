param(
    [string]$ProjectRepoRoot = 'D:\GOOGLE DRIVE\DEV\Roguelite'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Write-Host ''
Write-Host 'Roguelite - runner 28 exact upstream SSD walk8' -ForegroundColor Cyan
Write-Host 'SSD-WALK8: BLOCKED/CLOSED' -ForegroundColor Yellow
Write-Host ''
Write-Host 'Reason:' -ForegroundColor Yellow
Write-Host 'The public Sprite-Sheet-Diffusion release does not contain the trained custom multi-scale pose_guider.pth required by its current inference.py/unet_3d.py graph.'
Write-Host 'The available patrolli/AnimateAnyone pose_guider.pth is the original Moore conv_in/blocks/conv_out architecture and is not a drop-in checkpoint for SSD custom conv_layers/cross_attn/final_proj architecture.'
Write-Host ''
Write-Host 'Do not bypass this with strict=False. That would leave the custom SSD pose guider substantially uninitialized and would not be a valid SSD test.' -ForegroundColor Yellow
Write-Host ''
Write-Host 'Current documented route:' -ForegroundColor Green
Write-Host 'tools\structured-2d-character-pipeline\29_run_ssd_moore_compat_exilada_walk8.ps1' -ForegroundColor Green
Write-Host ''
Write-Host 'No reinstall or heavyweight model redownload is required.' -ForegroundColor Green
exit 2
