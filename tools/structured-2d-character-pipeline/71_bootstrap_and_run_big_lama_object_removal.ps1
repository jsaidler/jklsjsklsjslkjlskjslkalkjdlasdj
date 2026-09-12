param(
    [string]$ProjectRepoRoot = 'D:\GOOGLE DRIVE\DEV\Roguelite',
    [string]$PythonRuntimeRoot = 'Z:\AI\QwenImageEdit\ComfyUI_windows_portable',
    [string]$KleinWorkspace = 'Z:\AI\Flux2Klein',
    [string]$StudioRoot = 'Z:\AI\RogueliteAssetStudio',
    [string]$SDXLWorkspace = 'Z:\AI\SDXLInpaint',
    [string]$LaMaWorkspace = 'Z:\AI\LaMaInpaint'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$LaMaUrl = 'https://github.com/enesmsahin/simple-lama-inpainting/releases/download/v0.1.0/big-lama.pt'
$LaMaName = 'big-lama.pt'
$LaMaSha = '7ba7aa7ac37a4d41fdbbeba3a2af7ead18058552997e3a3cd1a3b2210c9e6b4c'
$LaMaBytes = [int64]205803670

$SDXLInpaintName = 'sdxl_inpaint_0.1_fp16.safetensors'
$SDXLInpaintSha = '6470840731e98cc16713ddf3ac7ee458c9fdbcb881a98c6727cd4a938f227d3f'
$SDXLBaseName = 'sd_xl_base_1.0.safetensors'
$SDXLBaseSha = '31e35c80fc4829d14f90153f4c74cd59c90b779f6afe05a74cd6120b893f7e5b'

function Fail([string]$Message) {
    Write-Host "RUNNER71-BIG-LAMA: FAIL - $Message" -ForegroundColor Red
    exit 1
}
function Get-Sha256([string]$Path) {
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}
function Require-Hash([string]$Path,[string]$Expected,[string]$Label) {
    if (-not (Test-Path $Path -PathType Leaf)) { Fail "required $Label missing: $Path" }
    $actual = Get-Sha256 $Path
    if ($actual -ne $Expected.ToLowerInvariant()) { Fail "$Label SHA256 mismatch. Expected $Expected got $actual" }
    Write-Host "  $Label verified." -ForegroundColor Green
}
function Remove-VerifiedPayload([string]$Path,[string]$Expected,[string]$Label) {
    if (-not (Test-Path $Path -PathType Leaf)) {
        Write-Host "  $Label already absent." -ForegroundColor DarkGray
        return
    }
    $actual = Get-Sha256 $Path
    if ($actual -ne $Expected.ToLowerInvariant()) {
        Fail "refusing to delete unexpected $Label payload. Expected $Expected got $actual at $Path"
    }
    $bytes = (Get-Item -LiteralPath $Path).Length
    Remove-Item -LiteralPath $Path -Force
    Write-Host ("  Removed retired {0}: {1:N2} GiB" -f $Label,($bytes/1GB)) -ForegroundColor Yellow
}
function Download-Verified([string]$Url,[string]$Destination,[string]$Expected,[int64]$ExpectedBytes,[string]$Label) {
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $Destination) | Out-Null
    if (Test-Path $Destination -PathType Leaf) {
        $actual = Get-Sha256 $Destination
        $actualBytes = (Get-Item -LiteralPath $Destination).Length
        if ($actual -eq $Expected.ToLowerInvariant() -and $actualBytes -eq $ExpectedBytes) {
            Write-Host "  $Label already present and verified." -ForegroundColor Green
            return
        }
        Fail "existing $Label does not match pinned artifact; refusing to overwrite: $Destination"
    }
    $partial = "$Destination.part"
    $curl = Get-Command curl.exe -ErrorAction SilentlyContinue
    if (-not $curl) { Fail 'curl.exe is required.' }
    Write-Host "Downloading $Label (~196 MiB)..." -ForegroundColor Cyan
    Write-Host "  $Url" -ForegroundColor DarkGray
    & $curl.Source '--fail' '--location' '--retry' '10' '--retry-delay' '5' '--retry-all-errors' '--continue-at' '-' '--output' $partial $Url
    if ($LASTEXITCODE -ne 0) { Fail "$Label download failed. Partial retained: $partial" }
    $downloadBytes = (Get-Item -LiteralPath $partial).Length
    if ($downloadBytes -ne $ExpectedBytes) { Fail "$Label size mismatch after download. Expected $ExpectedBytes got $downloadBytes. Partial retained: $partial" }
    $downloadSha = Get-Sha256 $partial
    if ($downloadSha -ne $Expected.ToLowerInvariant()) { Fail "$Label SHA256 mismatch after download. Expected $Expected got $downloadSha. Partial retained: $partial" }
    Move-Item -LiteralPath $partial -Destination $Destination -Force
    Write-Host "  $Label downloaded and verified." -ForegroundColor Green
}
function Quote-ProcessArg([string]$Value) {
    if ($Value -match '[\s"]') { return '"' + ($Value -replace '"','\"') + '"' }
    return $Value
}
function Read-TextFileOrEmpty([string]$Path) {
    if (-not (Test-Path $Path -PathType Leaf)) { return '' }
    $v = Get-Content -LiteralPath $Path -Raw
    if ($null -eq $v) { return '' }
    return [string]$v
}
function Print-TextFile([string]$Path,[string]$Header,[int]$Tail=0) {
    Write-Host $Header -ForegroundColor Yellow
    if (-not (Test-Path $Path -PathType Leaf)) { Write-Host "  <missing: $Path>"; return }
    if ($Tail -gt 0) { Get-Content -LiteralPath $Path -Tail $Tail } else { Get-Content -LiteralPath $Path }
}

$Python = Join-Path $PythonRuntimeRoot 'python_embeded\python.exe'
$ComfyRoot = Join-Path $PythonRuntimeRoot 'ComfyUI'
$Original = Join-Path $KleinWorkspace 'spike\flux2_klein_4b_t2i_probe.png'
$Runner66Dir = Join-Path $StudioRoot 'localization\runner66_gate'
$Runner66Manifest = Join-Path $Runner66Dir 'runner66_repeated_element_manifest.json'
$Runner70Dir = Join-Path $SDXLWorkspace 'runner70_1024_parity_gate'
$Runner70Manifest = Join-Path $Runner70Dir 'runner70_sdxl_1024_manifest.json'
$Runner70Contact = Join-Path $Runner70Dir 'runner70_sdxl_1024_contact_sheet.png'
$Adapter = Join-Path $ProjectRepoRoot 'tools\roguelite-asset-studio\lama_inpaint_adapter.py'
$Executor = Join-Path $ProjectRepoRoot 'tools\roguelite-asset-studio\lama_object_removal_gate.py'
$Output = Join-Path $LaMaWorkspace 'runner71_object_removal_gate'
$Model = Join-Path $LaMaWorkspace "models\$LaMaName"

$SDXLInpaintPath = Join-Path $ComfyRoot "models\diffusion_models\$SDXLInpaintName"
$SDXLBasePath = Join-Path $ComfyRoot "models\checkpoints\$SDXLBaseName"

foreach ($required in @($Python,$Original,$Runner66Manifest,$Runner70Manifest,$Runner70Contact,$Adapter,$Executor)) {
    if (-not (Test-Path $required -PathType Leaf)) { Fail "required prerequisite missing: $required" }
}

$m66 = Get-Content -LiteralPath $Runner66Manifest -Raw | ConvertFrom-Json
if (-not [bool]$m66.auto_geometry_gate_pass) { Fail 'Runner66 automatic geometry gate did not pass' }
$m70 = Get-Content -LiteralPath $Runner70Manifest -Raw | ConvertFrom-Json
if ([string]$m70.technical_status -ne 'COMPLETE') { Fail 'Runner70 evidence is not technically complete' }

Write-Host ''
Write-Host 'Roguelite Runner 71 - BIG-LAMA / AUTOMATIC MASK OBJECT REMOVAL' -ForegroundColor Cyan
Write-Host '[WHY] Runner70 exhausted SDXL Inpainting fairly: 1024 parity still preserved the plank and strap instead of executing the physical removal/break.' -ForegroundColor Yellow
Write-Host '[EDITOR CHANGE ONLY] Runner66 masks, operation semantics and deterministic full-resolution compositor remain authoritative.' -ForegroundColor Green
Write-Host '[SPECIALIST] Big-LaMa is a lightweight resolution-robust object-removal/inpainting model; no text prompt is used.' -ForegroundColor Green
Write-Host '[LICENSE] Apache-2.0 upstream LaMa lineage.' -ForegroundColor Green
Write-Host '[SECURITY] TorchScript is executable; the runner loads only the exact pinned SHA256 artifact.' -ForegroundColor Yellow
Write-Host '[MATRIX] one-plank and one-strap object-removal edits using tight and expanded automatic boundary masks.' -ForegroundColor Green
Write-Host '[NO MANUAL MASKS] Uses accepted Runner66 masks only.' -ForegroundColor Green
Write-Host ''

Write-Host 'Preserved Runner69/70 evidence verified. Cleaning retired SDXL payload...' -ForegroundColor Cyan
Remove-VerifiedPayload $SDXLInpaintPath $SDXLInpaintSha 'SDXL Inpainting 0.1 UNet'
Remove-VerifiedPayload $SDXLBasePath $SDXLBaseSha 'SDXL Base 1.0 checkpoint'

$driveRoot = [System.IO.Path]::GetPathRoot($LaMaWorkspace)
$driveInfo = [System.IO.DriveInfo]::new($driveRoot)
$freeBytes = [int64]$driveInfo.AvailableFreeSpace
$requiredFree = [int64](2GB)
Write-Host ("Disk preflight after cleanup: free={0:N2} GiB; required margin={1:N2} GiB." -f ($freeBytes/1GB),($requiredFree/1GB)) -ForegroundColor Cyan
if ($freeBytes -lt $requiredFree) { Fail 'insufficient free space for Big-LaMa gate.' }

Download-Verified $LaMaUrl $Model $LaMaSha $LaMaBytes 'Big-LaMa TorchScript'
Require-Hash $Model $LaMaSha 'Big-LaMa TorchScript'

New-Item -ItemType Directory -Force -Path $Output | Out-Null
$ExecStdout = Join-Path $Output 'runner71_python_stdout.log'
$ExecStderr = Join-Path $Output 'runner71_python_stderr.log'
$ExecLog = Join-Path $Output 'runner71_executor.log'
foreach ($p in @($ExecStdout,$ExecStderr,$ExecLog)) { if (Test-Path $p) { Remove-Item -LiteralPath $p -Force } }

$execArgs = @(
    '-s',(Quote-ProcessArg $Executor),
    '--model',(Quote-ProcessArg $Model),
    '--workspace',(Quote-ProcessArg $LaMaWorkspace),
    '--klein-workspace',(Quote-ProcessArg $KleinWorkspace),
    '--runner66-dir',(Quote-ProcessArg $Runner66Dir),
    '--runner70-dir',(Quote-ProcessArg $Runner70Dir)
)

Write-Host 'RUNNER71: launching direct Big-LaMa executor (no ComfyUI server)...' -ForegroundColor Cyan
$ep = Start-Process -FilePath $Python -ArgumentList $execArgs -WorkingDirectory $ProjectRepoRoot -RedirectStandardOutput $ExecStdout -RedirectStandardError $ExecStderr -WindowStyle Hidden -PassThru -Wait
$executorExit = $ep.ExitCode
$stdoutText = Read-TextFileOrEmpty $ExecStdout
$stderrText = Read-TextFileOrEmpty $ExecStderr
Set-Content -LiteralPath $ExecLog -Value (@('=== PYTHON STDOUT ===',$stdoutText,'=== PYTHON STDERR ===',$stderrText) -join [Environment]::NewLine) -Encoding UTF8
Print-TextFile $ExecStdout '--- RUNNER71 PYTHON STDOUT ---'
if (-not [string]::IsNullOrWhiteSpace($stderrText)) { Print-TextFile $ExecStderr '--- RUNNER71 PYTHON STDERR ---' 250 }
if ($executorExit -ne 0) { Fail "Big-LaMa executor exited with code $executorExit" }

foreach ($name in @(
    'plank_lama_tight_mask.png','plank_lama_tight_raw.png','plank_lama_tight_final.png','plank_lama_expanded_mask.png','plank_lama_expanded_raw.png','plank_lama_expanded_final.png',
    'strap_lama_tight_mask.png','strap_lama_tight_raw.png','strap_lama_tight_final.png','strap_lama_expanded_mask.png','strap_lama_expanded_raw.png','strap_lama_expanded_final.png',
    'runner71_lama_object_removal_contact_sheet.png','runner71_lama_object_removal_manifest.json','runner71_executor.log'
)) {
    if (-not (Test-Path (Join-Path $Output $name) -PathType Leaf)) { Fail "expected Runner71 output missing: $name" }
}

Write-Host ''
Write-Host 'RUNNER71-BIG-LAMA: PASS - TECHNICAL OBJECT-REMOVAL MATRIX COMPLETE / VISUAL VERDICT PENDING' -ForegroundColor Green
Write-Host "Contact sheet: $(Join-Path $Output 'runner71_lama_object_removal_contact_sheet.png')" -ForegroundColor Cyan
Write-Host "Manifest: $(Join-Path $Output 'runner71_lama_object_removal_manifest.json')" -ForegroundColor Cyan
Write-Host "Executor log: $ExecLog" -ForegroundColor Cyan
Write-Host 'Visual gate: at least one variant per task must execute the actual removal/break while the deterministic compositor preserves unrelated geometry.' -ForegroundColor Yellow
