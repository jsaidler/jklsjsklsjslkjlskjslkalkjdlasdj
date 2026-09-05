param(
    [string]$RepoRoot = 'D:\GOOGLE DRIVE\DEV\Roguelite',
    [string]$Workspace = 'Z:\AI\RogueliteCharacterPipeline'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Fail([string]$Message) {
    Write-Host "G3S-B3A: FAIL - $Message" -ForegroundColor Red
    exit 1
}

function Find-BlenderExe {
    $candidates = @()
    if ($env:BLENDER_EXE) { $candidates += $env:BLENDER_EXE }
    $cmd = Get-Command blender.exe -ErrorAction SilentlyContinue
    if ($cmd) { $candidates += $cmd.Source }
    foreach ($root in @('C:\Program Files\Blender Foundation','C:\Program Files (x86)\Blender Foundation')) {
        if (Test-Path $root) {
            $candidates += @(Get-ChildItem -Path $root -Filter blender.exe -Recurse -ErrorAction SilentlyContinue | Select-Object -ExpandProperty FullName)
        }
    }
    $found = @($candidates | Where-Object { $_ -and (Test-Path $_ -PathType Leaf) } | Select-Object -Unique)
    if ($found.Count -eq 0) { return $null }
    return ($found | Sort-Object -Descending | Select-Object -First 1)
}

function Find-MpfbPackageRoot([string]$Root) {
    if (-not (Test-Path $Root -PathType Container)) { return $null }
    $candidates = @(Get-ChildItem -Path $Root -Filter '__init__.py' -File -Recurse -ErrorAction SilentlyContinue)
    foreach ($init in $candidates) {
        $dir = $init.Directory.FullName
        if ((Test-Path (Join-Path $dir 'services') -PathType Container) -and
            (Test-Path (Join-Path $dir 'data') -PathType Container)) {
            return $dir
        }
    }
    return $null
}

function Invoke-NativeSafe {
    param(
        [Parameter(Mandatory=$true)][string]$Exe,
        [Parameter(Mandatory=$true)][string[]]$Arguments
    )
    $saved = $ErrorActionPreference
    try {
        $ErrorActionPreference = 'Continue'
        $captured = @(& $Exe @Arguments 2>&1)
        $code = $LASTEXITCODE
    }
    finally {
        $ErrorActionPreference = $saved
    }
    foreach ($line in $captured) { Write-Host ([string]$line) }
    return [int]$code
}

Write-Host ''
Write-Host 'Roguelite - G3S-B3A V2 COMPLETE ADULT FEMALE NUDE ANATOMY GUIDE' -ForegroundColor Cyan
Write-Host 'Body first. Female phenotype. No hair, no clothing, no cuffs/shackles, no chains.'
Write-Host 'This produces deterministic structural guide data only; it is NOT final visible pixel art.' -ForegroundColor Yellow
Write-Host ''

if (-not (Test-Path $RepoRoot -PathType Container)) { Fail "Repository root not found: $RepoRoot" }

$baselinePath = Join-Path $RepoRoot 'tools\deterministic-character-pipeline\g1_baseline.json'
$b2MarkerPath = Join-Path $RepoRoot 'tools\structured-2d-character-pipeline\g3s_b2_approval.json'
$bootstrapScript = Join-Path $RepoRoot 'tools\structured-2d-character-pipeline\g3s_b3_mpfb_bootstrap.py'
$targetScript = Join-Path $RepoRoot 'tools\structured-2d-character-pipeline\g3s_b3a_nude_anatomy_guide.py'
$contactHelper = Join-Path $RepoRoot 'tools\structured-2d-character-pipeline\g3s_b3a_contact_sheet.py'
$embeddedPython = 'Z:\AI\QwenImageEditSpike\ComfyUI_windows_portable\python_embeded\python.exe'

foreach ($p in @($baselinePath,$b2MarkerPath,$bootstrapScript,$targetScript,$contactHelper,$embeddedPython)) {
    if (-not (Test-Path $p -PathType Leaf)) { Fail "Required file missing: $p. Run git pull --ff-only first." }
}

$baseline = Get-Content -LiteralPath $baselinePath -Raw | ConvertFrom-Json
$b2 = Get-Content -LiteralPath $b2MarkerPath -Raw | ConvertFrom-Json
if ($baseline.status -ne 'PASS') { Fail 'G1 baseline is not PASS.' }
if ($b2.gate -ne 'G3S-B2-LAYER-STACK-PREFLIGHT' -or $b2.status -ne 'PASS_CLOSED_DIAGNOSTIC_ONLY') {
    Fail 'G3S-B2 diagnostic is not canonically closed PASS.'
}
Write-Host '[OK] G3S-B2 diagnostic acknowledged: composite subtraction is not body authoring.' -ForegroundColor Green

$blenderExe = Find-BlenderExe
if (-not $blenderExe) { Fail 'Blender could not be located.' }
Write-Host "[OK] Blender: $blenderExe" -ForegroundColor Green

# Reuse the exact MPFB package already validated in G3V. If it is absent, restore the
# same pinned official package instead of introducing a new dependency/version.
$deps = Join-Path $Workspace 'dependencies\g3v'
New-Item -ItemType Directory -Force -Path $deps | Out-Null
$mpfbVersion = '2.0.17'
$mpfbZip = Join-Path $deps "mpfb-$mpfbVersion.zip"
$mpfbExtract = Join-Path $deps "mpfb-$mpfbVersion-unpacked"
$mpfbRoot = Find-MpfbPackageRoot $mpfbExtract

if (-not $mpfbRoot) {
    $apiUrls = @(
        'https://extensions.blender.org/api/v1/extensions/?blender_version=5.1.1&platform=windows-x64',
        'https://extensions.blender.org/api/v1/extensions/?blender_version=5.1.1'
    )
    $pkg = $null
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.SecurityProtocolType]::Tls12
    foreach ($api in $apiUrls) {
        try {
            $meta = Invoke-RestMethod -Uri $api -UseBasicParsing
            $matches = @($meta.data | Where-Object { $_.id -eq 'mpfb' -and $_.version -eq $mpfbVersion })
            if ($matches.Count -gt 0) { $pkg = $matches[0]; break }
        }
        catch {
            Write-Host "[WARN] MPFB metadata query failed at ${api}: $($_.Exception.Message)" -ForegroundColor DarkYellow
        }
    }
    if (-not $pkg) { Fail "Official Blender Extensions API did not return pinned MPFB $mpfbVersion." }

    $archiveUrl = [string]$pkg.archive_url
    if ($archiveUrl -notmatch '^https?://') { $archiveUrl = 'https://extensions.blender.org' + $archiveUrl }
    $expectedHash = (([string]$pkg.archive_hash) -replace '^sha256:','').ToLowerInvariant()
    if (-not $expectedHash) { Fail 'MPFB metadata did not include archive_hash.' }

    $download = $true
    if (Test-Path $mpfbZip -PathType Leaf) {
        $existingHash = (Get-FileHash -LiteralPath $mpfbZip -Algorithm SHA256).Hash.ToLowerInvariant()
        if ($existingHash -eq $expectedHash) { $download = $false }
    }
    if ($download) {
        Write-Host "[DOWNLOAD] Restoring pinned MPFB $mpfbVersion from official Blender Extensions..." -ForegroundColor Cyan
        Invoke-WebRequest -Uri $archiveUrl -OutFile $mpfbZip -UseBasicParsing
    }
    $actualHash = (Get-FileHash -LiteralPath $mpfbZip -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($actualHash -ne $expectedHash) { Fail "MPFB SHA256 mismatch. expected=$expectedHash got=$actualHash" }

    if (Test-Path $mpfbExtract) { Remove-Item $mpfbExtract -Recurse -Force }
    New-Item -ItemType Directory -Force -Path $mpfbExtract | Out-Null
    Expand-Archive -Path $mpfbZip -DestinationPath $mpfbExtract -Force
    $mpfbRoot = Find-MpfbPackageRoot $mpfbExtract
}
if (-not $mpfbRoot) { Fail "Could not locate MPFB package root: $mpfbExtract" }

$mpfbArchiveHash = $null
if (Test-Path $mpfbZip -PathType Leaf) {
    $mpfbArchiveHash = (Get-FileHash -LiteralPath $mpfbZip -Algorithm SHA256).Hash.ToLowerInvariant()
}
if ($mpfbArchiveHash) { Write-Host "[OK] MPFB $mpfbVersion SHA256 $mpfbArchiveHash" -ForegroundColor Green }
Write-Host "[OK] MPFB package root: $mpfbRoot" -ForegroundColor Green

$mpfbUserRoot = Join-Path $deps 'mpfb_user'
New-Item -ItemType Directory -Force -Path $mpfbUserRoot | Out-Null

$outDir = Join-Path $Workspace 'g3s_b3a_nude_guide'
$logDir = Join-Path $outDir 'logs'
Remove-Item $outDir -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force -Path $outDir,$logDir | Out-Null
$stdout = Join-Path $logDir 'blender_stdout.log'
$stderr = Join-Path $logDir 'blender_stderr.log'

$pitch = [int]$baseline.camera_pitch_deg
$heroPx = [int]$baseline.protagonist_reference_height_px
$yaw = 8
Write-Host "[RUN] one Blender background process | corrected adult female nude/hairless anatomy guide | 640x360 / ${pitch}deg / ${heroPx}px..." -ForegroundColor Cyan

$argumentString = '--background --python-exit-code 1 --python "{0}" -- --mpfb-root "{1}" --mpfb-user-root "{2}" --target-script "{3}" --output-dir "{4}" --pitch {5} --hero-px {6} --yaw {7}' -f $bootstrapScript,$mpfbRoot,$mpfbUserRoot,$targetScript,$outDir,$pitch,$heroPx,$yaw
$proc = Start-Process -FilePath $blenderExe -ArgumentList $argumentString -Wait -PassThru -NoNewWindow -RedirectStandardOutput $stdout -RedirectStandardError $stderr
Get-Content $stdout -ErrorAction SilentlyContinue | Out-Host
if (Test-Path $stderr -PathType Leaf) {
    $errText = Get-Content $stderr -Raw -ErrorAction SilentlyContinue
    if ($errText) { Write-Host $errText -ForegroundColor DarkYellow }
}
if ($proc.ExitCode -ne 0) { Fail "Blender exited with code $($proc.ExitCode). See $stdout and $stderr" }

$stdoutText = Get-Content $stdout -Raw -ErrorAction SilentlyContinue
foreach ($marker in @(
    'G3S_B3_MPFB_BOOTSTRAP=PASS',
    'G3S_B3A_REVISION=G3S_B3A_NUDE_ANATOMY_GUIDE_V2',
    'G3S_B3A_PHENOTYPE_GENDER=FEMALE',
    'G3S_B3A_MALE_TARGETS=0',
    'G3S_B3A_COMPLETE_NUDE_GEOMETRY=PASS',
    'G3S_B3A_HAIR_OBJECTS=0',
    'G3S_B3A_CLOTHING_OBJECTS=0',
    'G3S_B3A_RESTRAINT_OBJECTS=0',
    'G3S_B3A_ART_AUTHORITY=GUIDE_ONLY_NOT_FINAL_PIXEL_ART'
)) {
    if ($stdoutText -notmatch [regex]::Escape($marker)) { Fail "Expected Blender marker missing: $marker" }
}

$manifest = Join-Path $outDir 'g3s_b3a_manifest.json'
if (-not (Test-Path $manifest -PathType Leaf)) { Fail "Manifest missing: $manifest" }
$data = Get-Content $manifest -Raw | ConvertFrom-Json
if ($data.gate -ne 'G3S-B3-A-NUDE-ANATOMY-GUIDE' -or $data.status -ne 'REVIEW_REQUIRED') { Fail 'Unexpected G3S-B3A manifest state.' }
if ($data.revision -ne 'G3S_B3A_NUDE_ANATOMY_GUIDE_V2') { Fail "Unexpected G3S-B3A revision: $($data.revision)" }
if ([double]$data.macro.gender -ne 0.0) { Fail "MPFB gender polarity guard failed: expected 0.0 female, got $($data.macro.gender)" }
if ($data.phenotype_audit.resolved_gender -ne 'female') { Fail "Phenotype audit did not resolve female: $($data.phenotype_audit.resolved_gender)" }
if ([int]$data.phenotype_audit.female_target_count -lt 1) { Fail 'Phenotype audit resolved no female macro targets.' }
if ([int]$data.phenotype_audit.male_target_count -ne 0) { Fail "Phenotype audit resolved male targets: $($data.phenotype_audit.male_target_count)" }
if (-not [bool]$data.layer_audit.complete_body_geometry) { Fail 'Body geometry audit did not pass.' }
if ([int]$data.layer_audit.hair_objects -ne 0 -or [int]$data.layer_audit.clothing_objects -ne 0 -or [int]$data.layer_audit.restraint_objects -ne 0 -or [int]$data.layer_audit.chains_objects -ne 0) {
    Fail 'Forbidden layer objects were present in nude body guide.'
}
Write-Host '[OK] MPFB phenotype audit: female target stack, zero male targets.' -ForegroundColor Green

$contact = Join-Path $outDir 'g3s_b3a_contact_sheet.png'
$code = Invoke-NativeSafe -Exe $embeddedPython -Arguments @($contactHelper,'--manifest',$manifest,'--output',$contact)
if ($code -ne 0) { Fail "Contact-sheet helper exited with code $code" }
if (-not (Test-Path $contact -PathType Leaf)) { Fail "Contact sheet missing: $contact" }

Write-Host ''
Write-Host 'G3S-B3A V2: REVIEW REQUIRED' -ForegroundColor Yellow
Write-Host "CONTACT SHEET: $contact"
Write-Host "MANIFEST:      $manifest"
Write-Host "LIT GUIDE:     $(Join-Path $outDir 'g3s_b3a_nude_anatomy_lit.png')"
Write-Host "MASK:          $(Join-Path $outDir 'g3s_b3a_nude_anatomy_mask.png')"
Write-Host ''
Write-Host 'STOP. This only validates the corrected complete adult female nude/hairless anatomy guide. Do not author hair/clothing and do not start animation yet.' -ForegroundColor Yellow
Write-Host 'After review, B3-B authors the actual native 128x128 body-base pixel asset.' -ForegroundColor Yellow
