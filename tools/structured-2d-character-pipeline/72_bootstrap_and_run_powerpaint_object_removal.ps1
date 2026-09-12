param(
    [string]$ProjectRepoRoot = 'D:\GOOGLE DRIVE\DEV\Roguelite',
    [string]$RuntimeWorkspace = 'Z:\AI\QwenImageEdit',
    [string]$PowerPaintWorkspace = 'Z:\AI\PowerPaint',
    [string]$LaMaWorkspace = 'Z:\AI\LaMaInpaint',
    [int]$Port = 8194,
    [int]$TimeoutMinutes = 180
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$ComfyCommit = '6eba895f7d3615284da81e95bf49eaed4a5f7309'
$BrushNetCommit = '505d8ef917ddf3896afd1926770ecc9b099704e2'
$BrushNetRepo = 'https://github.com/nullquant/ComfyUI-BrushNet.git'

$SD15Name = 'v1-5-pruned-emaonly.safetensors'
$SD15Url = 'https://huggingface.co/stable-diffusion-v1-5/stable-diffusion-v1-5/resolve/main/v1-5-pruned-emaonly.safetensors?download=true'
$SD15Sha = '6ce0161689b3853acaa03779ec93eafe75a02f4ced659bee03f50797806fa2fa'
$SD15Bytes = [int64]4265146304

$BrushName = 'diffusion_pytorch_model.safetensors'
$BrushUrl = 'https://huggingface.co/JunhaoZhuang/PowerPaint-v2-1/resolve/main/PowerPaint_Brushnet/diffusion_pytorch_model.safetensors?download=true'
$BrushSha = '530f2886ef5bcdf199269ec344155a517639ba64219b85eeb23fd86aab93147f'
$BrushBytes = [int64]3544366408

$PPTextName = 'pytorch_model.bin'
$PPTextUrl = 'https://huggingface.co/JunhaoZhuang/PowerPaint-v2-1/resolve/main/PowerPaint_Brushnet/pytorch_model.bin?download=true'
$PPTextSha = '73709b4360ca06ef990a67d090e8d81a4310943d67a88845653fc4e9f7f26b65'
$PPTextBytes = [int64]492401329

$BaseClipName = 'model.fp16.safetensors'
$BaseClipUrl = 'https://huggingface.co/stable-diffusion-v1-5/stable-diffusion-v1-5/resolve/main/text_encoder/model.fp16.safetensors?download=true'
$BaseClipSha = '77795e2023adcf39bc29a884661950380bd093cf0750a966d473d1718dc9ef4e'
$BaseClipBytes = [int64]246144864

$LaMaName = 'big-lama.pt'
$LaMaSha = '7ba7aa7ac37a4d41fdbbeba3a2af7ead18058552997e3a3cd1a3b2210c9e6b4c'

function Fail([string]$Message) {
    Write-Host "RUNNER72-POWERPAINT: FAIL - $Message" -ForegroundColor Red
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
        Fail "refusing to delete unexpected $Label. Expected $Expected got $actual at $Path"
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
    Write-Host "Downloading $Label..." -ForegroundColor Cyan
    Write-Host "  $Url" -ForegroundColor DarkGray
    & $curl.Source '--fail' '--location' '--retry' '12' '--retry-delay' '5' '--retry-all-errors' '--continue-at' '-' '--output' $partial $Url
    if ($LASTEXITCODE -ne 0) { Fail "$Label download failed. Partial retained: $partial" }
    $downloadBytes = (Get-Item -LiteralPath $partial).Length
    if ($downloadBytes -ne $ExpectedBytes) { Fail "$Label size mismatch. Expected $ExpectedBytes got $downloadBytes. Partial retained: $partial" }
    $downloadSha = Get-Sha256 $partial
    if ($downloadSha -ne $Expected.ToLowerInvariant()) { Fail "$Label SHA256 mismatch. Expected $Expected got $downloadSha. Partial retained: $partial" }
    Move-Item -LiteralPath $partial -Destination $Destination -Force
    Write-Host "  $Label downloaded and verified." -ForegroundColor Green
}
function Invoke-Git([string]$WorkingDirectory,[string[]]$GitArgs,[string]$Label) {
    & git.exe -C $WorkingDirectory @GitArgs
    if ($LASTEXITCODE -ne 0) { Fail "$Label failed (git exit $LASTEXITCODE)" }
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
function Stop-Managed([string]$PidFile) {
    if (-not (Test-Path $PidFile -PathType Leaf)) { return }
    $raw = Get-Content -LiteralPath $PidFile -Raw
    if ($null -ne $raw) {
        $managedPid = 0
        if ([int]::TryParse(([string]$raw).Trim(), [ref]$managedPid) -and $managedPid -gt 0) {
            $p = Get-Process -Id $managedPid -ErrorAction SilentlyContinue
            if ($p) { Stop-Process -Id $managedPid -Force; Start-Sleep -Seconds 2 }
        }
    }
    Remove-Item -LiteralPath $PidFile -Force -ErrorAction SilentlyContinue
}

$PortableRoot = Join-Path $RuntimeWorkspace 'ComfyUI_windows_portable'
$BasePython = Join-Path $PortableRoot 'python_embeded\python.exe'
$ComfyRoot = Join-Path $PortableRoot 'ComfyUI'
$MainPy = Join-Path $ComfyRoot 'main.py'
$Runner71Dir = Join-Path $LaMaWorkspace 'runner71_object_removal_gate'
$Runner71Manifest = Join-Path $Runner71Dir 'runner71_lama_object_removal_manifest.json'
$Runner71Contact = Join-Path $Runner71Dir 'runner71_lama_object_removal_contact_sheet.png'
$LaMaModel = Join-Path $LaMaWorkspace "models\$LaMaName"
$CustomNodeRoot = Join-Path $ComfyRoot 'custom_nodes\ComfyUI-BrushNet'
$VenvRoot = Join-Path $PowerPaintWorkspace 'venv'
$VenvPython = Join-Path $VenvRoot 'Scripts\python.exe'
$Output = Join-Path $PowerPaintWorkspace 'runner72_object_removal_gate'
$Adapter = Join-Path $ProjectRepoRoot 'tools\roguelite-asset-studio\powerpaint_brushnet_adapter.py'
$Executor = Join-Path $ProjectRepoRoot 'tools\roguelite-asset-studio\powerpaint_object_removal_gate.py'
$Protocol = Join-Path $ProjectRepoRoot 'tools\roguelite-asset-studio\adapter_protocol.py'
$SharedAdapter = Join-Path $ProjectRepoRoot 'tools\roguelite-asset-studio\flux2_klein_adapter.py'

$SD15Path = Join-Path $ComfyRoot "models\checkpoints\$SD15Name"
$BrushPath = Join-Path $ComfyRoot "models\inpaint\powerpaint\$BrushName"
$PPTextPath = Join-Path $ComfyRoot "models\inpaint\powerpaint\$PPTextName"
$BaseClipPath = Join-Path $ComfyRoot "models\clip\$BaseClipName"

foreach ($required in @($BasePython,$MainPy,$Runner71Manifest,$Runner71Contact,$Adapter,$Executor,$Protocol,$SharedAdapter)) {
    if (-not (Test-Path $required -PathType Leaf)) { Fail "required prerequisite missing: $required" }
}

$m71 = Get-Content -LiteralPath $Runner71Manifest -Raw | ConvertFrom-Json
if ([string]$m71.technical_status -ne 'COMPLETE') { Fail 'Runner71 evidence is not technically complete' }
if (-not (Test-Path ([string]$m71.contact_sheet) -PathType Leaf)) { Fail 'Runner71 contact-sheet evidence missing' }
$contactSha = Get-Sha256 ([string]$m71.contact_sheet)
if ($contactSha -ne ([string]$m71.contact_sheet_sha256).ToLowerInvariant()) { Fail 'Runner71 contact-sheet SHA256 mismatch' }

$currentCommit = (& git.exe -C $ComfyRoot rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0 -or $currentCommit -ne $ComfyCommit) { Fail "shared ComfyUI commit mismatch. Expected $ComfyCommit got $currentCommit" }
Write-Host "  Shared ComfyUI commit verified: $currentCommit" -ForegroundColor Green

Write-Host ''
Write-Host 'Roguelite Runner 72 - POWERPAINT V2.1 / TASK-CONDITIONED OBJECT REMOVAL' -ForegroundColor Cyan
Write-Host '[WHY] Big-LaMa was extremely fast but reconstructed local continuity instead of executing the requested removal.' -ForegroundColor Yellow
Write-Host '[ONE BACKEND CHANGE] Runner66/71 masks, source contexts, operation semantics and deterministic compositor remain authoritative.' -ForegroundColor Green
Write-Host '[TASK CONDITIONING] PowerPaint object-removal mode uses learned P_ctxt/P_obj task tokens rather than blind context completion.' -ForegroundColor Green
Write-Host '[RUNTIME ISOLATION] A dedicated venv inherits the proven Torch/ComfyUI install but pins BrushNet dependencies without changing Qwen runtime packages.' -ForegroundColor Green
Write-Host '[MATRIX] plank/strap x tight/expanded masks, exactly matching Runner71 boundary variants.' -ForegroundColor Green
Write-Host '[NO MANUAL MASKS] Uses Runner71 masks derived from accepted Runner66 geometry.' -ForegroundColor Green
Write-Host ''

Write-Host 'Runner71 evidence verified. Cleaning rejected Big-LaMa payload...' -ForegroundColor Cyan
Remove-VerifiedPayload $LaMaModel $LaMaSha 'Big-LaMa TorchScript'

New-Item -ItemType Directory -Force -Path $PowerPaintWorkspace | Out-Null
if (-not (Test-Path $CustomNodeRoot -PathType Container)) {
    $customParent = Split-Path -Parent $CustomNodeRoot
    New-Item -ItemType Directory -Force -Path $customParent | Out-Null
    Write-Host 'Cloning pinned ComfyUI-BrushNet custom node...' -ForegroundColor Cyan
    & git.exe clone $BrushNetRepo $CustomNodeRoot
    if ($LASTEXITCODE -ne 0) { Fail 'ComfyUI-BrushNet clone failed' }
}
if (-not (Test-Path (Join-Path $CustomNodeRoot '.git') -PathType Container)) { Fail "custom node path exists but is not a git checkout: $CustomNodeRoot" }
Invoke-Git $CustomNodeRoot @('fetch','--depth','1','origin',$BrushNetCommit) 'ComfyUI-BrushNet fetch'
Invoke-Git $CustomNodeRoot @('checkout','--detach',$BrushNetCommit) 'ComfyUI-BrushNet checkout'
$actualBrushCommit = (& git.exe -C $CustomNodeRoot rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0 -or $actualBrushCommit -ne $BrushNetCommit) { Fail "ComfyUI-BrushNet commit mismatch: $actualBrushCommit" }
Write-Host "  ComfyUI-BrushNet commit verified: $actualBrushCommit" -ForegroundColor Green

if (-not (Test-Path $VenvPython -PathType Leaf)) {
    Write-Host 'Creating isolated PowerPaint venv with access to proven portable Torch packages...' -ForegroundColor Cyan
    & $BasePython -m venv --system-site-packages $VenvRoot
    if ($LASTEXITCODE -ne 0 -or -not (Test-Path $VenvPython -PathType Leaf)) {
        Write-Host 'stdlib venv failed; installing virtualenv helper into portable Python and retrying...' -ForegroundColor Yellow
        & $BasePython -m pip install --disable-pip-version-check --retries 12 --timeout 120 virtualenv
        if ($LASTEXITCODE -ne 0) { Fail 'could not install virtualenv fallback' }
        & $BasePython -m virtualenv --system-site-packages $VenvRoot
        if ($LASTEXITCODE -ne 0 -or -not (Test-Path $VenvPython -PathType Leaf)) { Fail 'could not create isolated PowerPaint venv' }
    }
}

$DepsMarker = Join-Path $VenvRoot '.powerpaint_deps_0.29.2_0.31.0_0.11.1.ok'
if (-not (Test-Path $DepsMarker -PathType Leaf)) {
    $depsInstalled = $false
    for ($attempt=1; $attempt -le 5; $attempt++) {
        Write-Host "Installing isolated PowerPaint dependencies (attempt $attempt/5)..." -ForegroundColor Cyan
        & $VenvPython -m pip install --disable-pip-version-check --retries 12 --timeout 120 --no-deps 'diffusers==0.29.2' 'accelerate==0.31.0' 'peft==0.11.1'
        if ($LASTEXITCODE -eq 0) { $depsInstalled=$true; break }
        if ($attempt -lt 5) { $delay=10*$attempt; Write-Host "pip failed; retrying in $delay seconds..." -ForegroundColor Yellow; Start-Sleep -Seconds $delay }
    }
    if (-not $depsInstalled) { Fail 'PowerPaint dependency installation failed after retries' }
    Set-Content -LiteralPath $DepsMarker -Value 'diffusers=0.29.2 accelerate=0.31.0 peft=0.11.1' -Encoding ASCII
}
& $VenvPython -c "import torch, diffusers, accelerate, peft; print('PowerPaint venv imports OK', torch.__version__, diffusers.__version__, accelerate.__version__, peft.__version__)"
if ($LASTEXITCODE -ne 0) { Fail 'isolated PowerPaint dependency import check failed' }

$driveRoot = [System.IO.Path]::GetPathRoot($PowerPaintWorkspace)
$driveInfo = [System.IO.DriveInfo]::new($driveRoot)
$freeBytes = [int64]$driveInfo.AvailableFreeSpace
$requiredFree = [int64](12GB)
Write-Host ("Disk preflight: free={0:N2} GiB; required margin={1:N2} GiB." -f ($freeBytes/1GB),($requiredFree/1GB)) -ForegroundColor Cyan
if ($freeBytes -lt $requiredFree) { Fail 'insufficient free space for PowerPaint gate' }

Download-Verified $SD15Url $SD15Path $SD15Sha $SD15Bytes 'SD1.5 base checkpoint'
Download-Verified $BrushUrl $BrushPath $BrushSha $BrushBytes 'PowerPaint v2.1 BrushNet'
Download-Verified $PPTextUrl $PPTextPath $PPTextSha $PPTextBytes 'PowerPaint v2.1 learned text encoder'
Download-Verified $BaseClipUrl $BaseClipPath $BaseClipSha $BaseClipBytes 'SD1.5 FP16 CLIP text encoder'
Require-Hash $SD15Path $SD15Sha 'SD1.5 base checkpoint'
Require-Hash $BrushPath $BrushSha 'PowerPaint v2.1 BrushNet'
Require-Hash $PPTextPath $PPTextSha 'PowerPaint v2.1 learned text encoder'
Require-Hash $BaseClipPath $BaseClipSha 'SD1.5 FP16 CLIP text encoder'

New-Item -ItemType Directory -Force -Path $Output | Out-Null
$Base = "http://127.0.0.1:$Port"
$PidFile = Join-Path $PowerPaintWorkspace '.runner72_comfy.pid'
$ComfyStdout = Join-Path $Output "comfyui_runner72_${Port}_stdout.log"
$ComfyStderr = Join-Path $Output "comfyui_runner72_${Port}_stderr.log"
Stop-Managed $PidFile
$portBusy=$false
try { $null=Invoke-RestMethod -Uri "$Base/system_stats" -TimeoutSec 2; $portBusy=$true } catch { }
if ($portBusy) { Fail "port $Port already serves an unmanaged process" }

$env:PYTORCH_CUDA_ALLOC_CONF='expandable_segments:True'
$launchArgs=@('-s',$MainPy,'--windows-standalone-build','--listen','127.0.0.1','--port',"$Port",'--disable-auto-launch','--lowvram','--reserve-vram','1.0')
$process=Start-Process -FilePath $VenvPython -ArgumentList $launchArgs -WorkingDirectory $ComfyRoot -RedirectStandardOutput $ComfyStdout -RedirectStandardError $ComfyStderr -WindowStyle Hidden -PassThru
Set-Content -LiteralPath $PidFile -Value $process.Id -Encoding ASCII
Write-Host "Started isolated-dependency ComfyUI PID $($process.Id) for PowerPaint on port $Port" -ForegroundColor Green

$ready=$false
for ($i=0; $i -lt 420; $i++) {
    try { $null=Invoke-RestMethod -Uri "$Base/system_stats" -TimeoutSec 2; $ready=$true; break }
    catch {
        if ($process.HasExited) { Print-TextFile $ComfyStderr '--- COMFYUI STDERR ---' 400; Stop-Managed $PidFile; Fail "ComfyUI exited before readiness: $($process.ExitCode)" }
        Start-Sleep -Seconds 1
    }
}
if (-not $ready) { Print-TextFile $ComfyStderr '--- COMFYUI STDERR ---' 400; Stop-Managed $PidFile; Fail 'ComfyUI did not become ready' }

foreach ($node in @('BrushNetLoader','PowerPaintCLIPLoader','PowerPaint')) {
    try { $info=Invoke-RestMethod -Uri "$Base/object_info/$node" -TimeoutSec 20 } catch { Print-TextFile $ComfyStderr '--- COMFYUI STDERR TAIL ---' 400; Stop-Managed $PidFile; Fail "could not query PowerPaint node $node" }
    if ($null -eq $info.$node) { Print-TextFile $ComfyStderr '--- COMFYUI STDERR TAIL ---' 400; Stop-Managed $PidFile; Fail "PowerPaint custom node unavailable: $node" }
}
Write-Host '  PowerPaint custom nodes loaded successfully.' -ForegroundColor Green

$ExecStdout=Join-Path $Output 'runner72_python_stdout.log'
$ExecStderr=Join-Path $Output 'runner72_python_stderr.log'
$ExecLog=Join-Path $Output 'runner72_executor.log'
foreach ($p in @($ExecStdout,$ExecStderr,$ExecLog)) { if (Test-Path $p) { Remove-Item -LiteralPath $p -Force } }
$execArgs=@(
    '-s',(Quote-ProcessArg $Executor),
    '--comfy-root',(Quote-ProcessArg $ComfyRoot),
    '--workspace',(Quote-ProcessArg $PowerPaintWorkspace),
    '--runner71-dir',(Quote-ProcessArg $Runner71Dir),
    '--port',"$Port",
    '--timeout-minutes',"$TimeoutMinutes",
    '--comfy-commit',$ComfyCommit,
    '--brushnet-commit',$BrushNetCommit
)
$executorExit=1
try {
    Write-Host 'RUNNER72: launching PowerPaint task-conditioned object-removal executor...' -ForegroundColor Cyan
    $ep=Start-Process -FilePath $VenvPython -ArgumentList $execArgs -WorkingDirectory $ProjectRepoRoot -RedirectStandardOutput $ExecStdout -RedirectStandardError $ExecStderr -WindowStyle Hidden -PassThru -Wait
    $executorExit=$ep.ExitCode
} finally { Stop-Managed $PidFile }

$stdoutText=Read-TextFileOrEmpty $ExecStdout
$stderrText=Read-TextFileOrEmpty $ExecStderr
Set-Content -LiteralPath $ExecLog -Value (@('=== PYTHON STDOUT ===',$stdoutText,'=== PYTHON STDERR ===',$stderrText) -join [Environment]::NewLine) -Encoding UTF8
Print-TextFile $ExecStdout '--- RUNNER72 PYTHON STDOUT ---'
if (-not [string]::IsNullOrWhiteSpace($stderrText)) { Print-TextFile $ExecStderr '--- RUNNER72 PYTHON STDERR ---' 300 }
if ($executorExit -ne 0) { Print-TextFile $ComfyStderr '--- COMFYUI STDERR TAIL ---' 450; Fail "PowerPaint executor exited with code $executorExit" }

foreach ($name in @(
    'plank_source_context.png','plank_approved_target_overlay.png','plank_powerpaint_tight_raw.png','plank_powerpaint_tight_final.png','plank_powerpaint_expanded_raw.png','plank_powerpaint_expanded_final.png',
    'strap_source_context.png','strap_approved_target_overlay.png','strap_powerpaint_tight_raw.png','strap_powerpaint_tight_final.png','strap_powerpaint_expanded_raw.png','strap_powerpaint_expanded_final.png',
    'runner72_powerpaint_object_removal_contact_sheet.png','runner72_powerpaint_object_removal_manifest.json','runner72_executor.log'
)) {
    if (-not (Test-Path (Join-Path $Output $name) -PathType Leaf)) { Fail "expected Runner72 output missing: $name" }
}

Write-Host ''
Write-Host 'RUNNER72-POWERPAINT: PASS - TECHNICAL TASK-CONDITIONED REMOVAL MATRIX COMPLETE / VISUAL VERDICT PENDING' -ForegroundColor Green
Write-Host "Contact sheet: $(Join-Path $Output 'runner72_powerpaint_object_removal_contact_sheet.png')" -ForegroundColor Cyan
Write-Host "Manifest: $(Join-Path $Output 'runner72_powerpaint_object_removal_manifest.json')" -ForegroundColor Cyan
Write-Host "Executor log: $ExecLog" -ForegroundColor Cyan
Write-Host 'Visual gate: PowerPaint must remove one actual plank and the strap center in at least one boundary variant, not merely reconstruct local continuity.' -ForegroundColor Yellow
