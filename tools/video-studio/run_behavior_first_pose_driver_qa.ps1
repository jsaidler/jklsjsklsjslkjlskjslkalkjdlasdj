param(
    [string]$WanGpRoot = 'Z:\AI\WanGP',
    [string]$DriverDir = 'Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\unified\first_driver'
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version 2.0

$Python = Join-Path $WanGpRoot 'env_uv\Scripts\python.exe'
$Inspector = Join-Path $PSScriptRoot 'inspect_behavioral_pose_driver.py'
$Plan = Join-Path $DriverDir 'driver_plan.json'
$Track = Join-Path $DriverDir 'behavioral_driver_coco133.jsonl'
$Preview = Join-Path $DriverDir 'behavioral_driver_pose_preview.mp4'
$Qa = Join-Path $DriverDir 'driver_qa.json'

foreach ($item in @(
    @{ Name='WanGP Python'; Path=$Python },
    @{ Name='Driver inspector'; Path=$Inspector },
    @{ Name='Driver plan'; Path=$Plan },
    @{ Name='Driver pose track'; Path=$Track },
    @{ Name='Driver preview'; Path=$Preview }
)) {
    if (-not (Test-Path -LiteralPath $item.Path -PathType Leaf)) {
        throw ('Missing ' + $item.Name + ': ' + $item.Path)
    }
}

Write-Host 'FIRST BEHAVIORAL POSE DRIVER QA'
Write-Host '================================'
Write-Host ('Plan: ' + $Plan)
Write-Host ('Track: ' + $Track)
Write-Host ('Preview: ' + $Preview)
Write-Host ''
Write-Host 'No DWPose and no Wan-Animate-2 are invoked.'
Write-Host 'Numeric QA has no automatic pass/fail threshold; visual preview remains required.'
Write-Host ''

$Saved = $ErrorActionPreference
try {
    $ErrorActionPreference = 'Continue'
    & $Python $Inspector '--track' $Track '--plan' $Plan '--output' $Qa
    $Exit = $LASTEXITCODE
} finally {
    $ErrorActionPreference = $Saved
}
if ($Exit -ne 0) { throw ('Behavioral driver QA failed with exit code ' + $Exit) }
if (-not (Test-Path -LiteralPath $Qa -PathType Leaf)) { throw 'Driver QA JSON was not produced.' }

Write-Host ''
Write-Host 'FIRST DRIVER NUMERIC QA: COMPLETE'
Write-Host ('QA JSON: ' + $Qa)
Write-Host ('Upload this preview for visual QA: ' + $Preview)
Write-Host 'Do not run Wan-Animate-2 before visual + numeric QA are reviewed.'
