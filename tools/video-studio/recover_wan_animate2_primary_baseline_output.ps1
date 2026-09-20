param(
    [string]$RunRoot = 'Z:\AI\VideoStudioRuns\wan-animate2-behavior'
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version 2.0

$run = Get-ChildItem -LiteralPath $RunRoot -Directory -Filter 'primary-baseline-*' |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1
if ($null -eq $run) { throw ('No primary-baseline run found under ' + $RunRoot) }

$manifestPath = Join-Path $run.FullName 'run_manifest.json'
if (-not (Test-Path -LiteralPath $manifestPath -PathType Leaf)) {
    throw ('Missing manifest: ' + $manifestPath)
}
$manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json

$driverLeaf = [IO.Path]::GetFileName([string]$manifest.driver)
$candidates = @()
foreach ($p in @($manifest.copied_outputs)) {
    $s = [string]$p
    if (-not (Test-Path -LiteralPath $s -PathType Leaf)) { continue }
    $leaf = [IO.Path]::GetFileName($s)
    $ext = [IO.Path]::GetExtension($leaf).ToLowerInvariant()
    if ($ext -notin @('.mp4','.mov','.mkv','.webm','.avi')) { continue }
    if ($leaf -eq $driverLeaf) { continue }
    if ($leaf -like 'pose_video_primary_baseline*') { continue }
    $candidates += Get-Item -LiteralPath $s
}

if ($candidates.Count -eq 0) {
    throw 'No generated Wan video distinct from the driving-video passthrough was found in copied_outputs.'
}

$generated = $candidates |
    Sort-Object @{Expression={ if ($_.Name -like '*wan_animate2*') { 1 } else { 0 } }; Descending=$true}, Length -Descending |
    Select-Object -First 1

$out = Join-Path $run.FullName 'wan_animate2_primary_baseline65_GENERATED.mp4'
Copy-Item -LiteralPath $generated.FullName -Destination $out -Force

$ffmpeg = Get-Command ffmpeg -ErrorAction SilentlyContinue
if ($null -eq $ffmpeg) { throw 'ffmpeg is not available in PATH.' }
$contact = Join-Path $run.FullName 'wan_animate2_primary_baseline65_GENERATED_contact.jpg'
$vf = "select='eq(n\,0)+eq(n\,8)+eq(n\,16)+eq(n\,24)+eq(n\,32)+eq(n\,40)+eq(n\,48)+eq(n\,56)+eq(n\,64)',scale=256:456:flags=lanczos,tile=3x3:padding=4:margin=4"
& $ffmpeg.Source -y -hide_banner -loglevel error -i $out -vf $vf -frames:v 1 $contact
if ($LASTEXITCODE -ne 0) { throw ('Contact-sheet generation failed with exit code ' + $LASTEXITCODE) }

Write-Host 'WAN-ANIMATE-2 BASELINE OUTPUT RECOVERY: COMPLETE'
Write-Host ('Run: ' + $run.FullName)
Write-Host ('Driver passthrough excluded: ' + $driverLeaf)
Write-Host ('Actual generated source: ' + $generated.FullName)
Write-Host ('Recovered generated video: ' + $out)
Write-Host ('Contact sheet: ' + $contact)
Write-Host ''
Write-Host 'Upload BOTH recovered generated video and contact sheet. No inference was rerun.'
