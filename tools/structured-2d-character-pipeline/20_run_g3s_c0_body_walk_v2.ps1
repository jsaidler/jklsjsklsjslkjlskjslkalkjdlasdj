param(
    [string]$RepoRoot = 'D:\GOOGLE DRIVE\DEV\Roguelite',
    [string]$PipelineWorkspace = 'Z:\AI\RogueliteCharacterPipeline'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Fail([string]$Message) {
    Write-Host "G3S-C0-V2: FAIL - $Message" -ForegroundColor Red
    exit 1
}

function Find-BlenderExe {
    $candidates = @()
    if ($env:BLENDER_EXE) { $candidates += $env:BLENDER_EXE }
    $cmd = Get-Command blender.exe -ErrorAction SilentlyContinue
    if ($cmd) { $candidates += $cmd.Source }
    foreach ($root in @('C:\Program Files\Blender Foundation','C:\Program Files (x86)\Blender Foundation')) {
        if (Test-Path $root) {
            $candidates += Get-ChildItem -Path $root -Filter blender.exe -Recurse -ErrorAction SilentlyContinue | Select-Object -ExpandProperty FullName
        }
    }
    $found = @($candidates | Where-Object { $_ -and (Test-Path $_ -PathType Leaf) } | Select-Object -Unique)
    if ($found.Count -eq 0) { return $null }
    return ($found | Sort-Object -Descending | Select-Object -First 1)
}

$Body = Join-Path $RepoRoot 'assets\source\characters\exilada\body\exilada_body_base_b3b_v4.png'
$G2Blend = Join-Path $PipelineWorkspace 'g2\g2_motion_topology.blend'
$G2Approval = Join-Path $RepoRoot 'tools\deterministic-character-pipeline\g2_approval.json'
$DirectionApproval = Join-Path $RepoRoot 'tools\deterministic-character-pipeline\g3v_retarget_approval.json'
$Spec = Join-Path $RepoRoot 'tools\structured-2d-character-pipeline\g3s_c0_body_motion_spec_v2.json'
$Extract = Join-Path $RepoRoot 'tools\structured-2d-character-pipeline\g3s_c0_extract_g2_motion.py'
$Build = Join-Path $RepoRoot 'tools\structured-2d-character-pipeline\g3s_c0_continuous_warp_v2.py'
$BuildTravel = Join-Path $RepoRoot 'tools\structured-2d-character-pipeline\g3s_c0_build_left_facing_travel.py'
$Python = 'Z:\AI\QwenImageEditSpike\ComfyUI_windows_portable\python_embeded\python.exe'
$Workspace = Join-Path $PipelineWorkspace 'g3s_c0_body_walk_v2'
$MotionJson = Join-Path $Workspace 'g3s_c0_motion_projection.json'

foreach ($p in @($Body,$G2Blend,$G2Approval,$DirectionApproval,$Spec,$Extract,$Build,$BuildTravel,$Python)) {
    if (-not (Test-Path $p -PathType Leaf)) { Fail "Required file missing: $p" }
}

$g2 = Get-Content -LiteralPath $G2Approval -Raw | ConvertFrom-Json
if ($g2.gate -ne 'G2' -or $g2.status -ne 'PASS') { Fail 'G2 approval is not PASS.' }
$dir = Get-Content -LiteralPath $DirectionApproval -Raw | ConvertFrom-Json
if ($dir.gate -ne 'G3V-R' -or $dir.status -ne 'PASS' -or $dir.method -ne 'DIRECTION_SPACE_FK') {
    Fail 'Validated DIRECTION_SPACE_FK evidence is not PASS.'
}

$bodyHash = (Get-FileHash -LiteralPath $Body -Algorithm SHA256).Hash.ToLowerInvariant()
if ($bodyHash -ne '702e2d95325049b5d99ea66db4fbbb9b41d6d24813efb0b1c3a37e112b1c2858') {
    Fail "Canonical B3B body PNG hash mismatch: $bodyHash"
}

$Blender = Find-BlenderExe
if (-not $Blender) { Fail 'Blender could not be located.' }

New-Item -ItemType Directory -Force -Path $Workspace | Out-Null
Get-ChildItem -LiteralPath $Workspace -File -ErrorAction SilentlyContinue | Remove-Item -Force

Write-Host ''
Write-Host 'Roguelite - G3S-C0 V2 CONTINUOUS BODY MOTION PROOF' -ForegroundColor Cyan
Write-Host '[V1 CLOSED] Rigid chopped body-part rotation produced detached/loop-like limb silhouettes.' -ForegroundColor Yellow
Write-Host '[V2] Continuous chain warp keeps each arm/leg as one deforming region across its joints.' -ForegroundColor Green
Write-Host '[FACING LOCK] Canonical B3B source faces screen-left; travel preview must move screen-left.' -ForegroundColor Green
Write-Host '[LOCK] Exact promoted B3B body is still the visible source.' -ForegroundColor Green
Write-Host '[LOCK] Motion is still approved CMU 105_34 / G2 projected real motion.' -ForegroundColor Green
Write-Host '[LOCK] Hidden 3D supplies motion/depth only; no hidden-3D RGB is used.' -ForegroundColor Green
Write-Host '[LOCK] No model/API/diffusion is used.' -ForegroundColor Green
Write-Host '[LOCK] Review only; no automatic production promotion.' -ForegroundColor Yellow
Write-Host "[OK] Blender: $Blender" -ForegroundColor Green
Write-Host ''

$stdout = Join-Path $Workspace 'blender_motion_extract_stdout.log'
$stderr = Join-Path $Workspace 'blender_motion_extract_stderr.log'
$argString = '"{0}" --background --python-exit-code 1 --python "{1}" -- --output "{2}" --approval "{3}"' -f $G2Blend, $Extract, $MotionJson, $DirectionApproval
$proc = Start-Process -FilePath $Blender -ArgumentList $argString -Wait -PassThru -NoNewWindow -RedirectStandardOutput $stdout -RedirectStandardError $stderr
Get-Content $stdout -ErrorAction SilentlyContinue | Out-Host
if ($proc.ExitCode -ne 0) {
    if (Test-Path $stderr) { Get-Content $stderr | Out-Host }
    Fail "Blender motion extraction exited with code $($proc.ExitCode)."
}
if (-not (Test-Path $MotionJson -PathType Leaf)) { Fail "Motion projection missing: $MotionJson" }

& $Python $Build --body $Body --motion $MotionJson --workspace $Workspace
if ($LASTEXITCODE -ne 0) { Fail "Continuous-warp builder exited with code $LASTEXITCODE" }

# The canonical body visibly faces left. Rebuild only the travel presentation so spatial travel agrees
# with the sprite facing. Do not mirror the body and do not reverse gait phase order.
& $Python $BuildTravel --workspace $Workspace
if ($LASTEXITCODE -ne 0) { Fail "Left-facing travel builder exited with code $LASTEXITCODE" }

$InPlace = Join-Path $Workspace 'g3s_c0_v2_body_walk_in_place.gif'
$Travel = Join-Path $Workspace 'g3s_c0_v2_body_walk_travel.gif'
$Contact = Join-Path $Workspace 'g3s_c0_v2_contact_sheet.png'
$Zoom = Join-Path $Workspace 'g3s_c0_v2_zoom_contact_sheet.png'
$Report = Join-Path $Workspace 'g3s_c0_v2_report.json'
foreach ($p in @($InPlace,$Travel,$Contact,$Zoom,$Report)) {
    if (-not (Test-Path $p -PathType Leaf)) { Fail "Expected review output missing: $p" }
}

Write-Host ''
Write-Host 'G3S-C0-V2: REVIEW PACKAGE READY' -ForegroundColor Green
Write-Host "IN-PLACE GIF: $InPlace"
Write-Host "TRAVEL GIF:   $Travel"
Write-Host "CONTACT:      $Contact"
Write-Host "ZOOM CONTACT: $Zoom"
Write-Host "REPORT:       $Report"
Write-Host 'FACING: canonical left-facing source; travel direction = left.' -ForegroundColor Green
Write-Host 'STOP. Share the in-place GIF, travel GIF and zoom contact sheet for visual review.' -ForegroundColor Yellow
