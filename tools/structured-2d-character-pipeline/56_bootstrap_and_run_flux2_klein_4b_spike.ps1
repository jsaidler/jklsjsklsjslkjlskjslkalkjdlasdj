param(
    [string]$ProjectRepoRoot = 'D:\GOOGLE DRIVE\DEV\Roguelite',
    [string]$SourcePortable = 'Z:\AI\FluxKontext\ComfyUI_windows_portable',
    [string]$Workspace = 'Z:\AI\Flux2Klein',
    [int]$Port = 8192,
    [int]$TimeoutMinutes = 180
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$ComfyCommit = '672ba9e5e388bd6bfac5ceef61f89ffdd9467200'
$ComfyRepo = 'https://github.com/Comfy-Org/ComfyUI.git'

$ModelName = 'flux-2-klein-4b-fp8.safetensors'
$ModelUrl = 'https://huggingface.co/black-forest-labs/FLUX.2-klein-4b-fp8/resolve/main/flux-2-klein-4b-fp8.safetensors'
$ModelSha256 = '97ed34fe0567e436200f2faee3939b88f2b5d99f8af2a4dc16532c4245c0ccb6'
$ModelBytes = [int64]4070624520

$TextEncoderName = 'qwen_3_4b.safetensors'
$TextEncoderUrl = 'https://huggingface.co/Comfy-Org/vae-text-encorder-for-flux-klein-4b/resolve/main/split_files/text_encoders/qwen_3_4b.safetensors'
$TextEncoderSha256 = '6c671498573ac2f7a5501502ccce8d2b08ea6ca2f661c458e708f36b36edfc5a'
$TextEncoderBytes = [int64]8044982048

$VaeName = 'flux2-vae.safetensors'
$VaeUrl = 'https://huggingface.co/Comfy-Org/vae-text-encorder-for-flux-klein-4b/resolve/main/split_files/vae/flux2-vae.safetensors'
$VaeSha256 = '868fe7b343cc8f3a19dbcfcafbc3d5f888802be3f89bd81b65b3621a066ce8f3'
$VaeBytes = [int64]336211292

function Fail([string]$Message) {
    Write-Host "RUNNER56-FLUX2-KLEIN: FAIL - $Message" -ForegroundColor Red
    exit 1
}

function Get-Sha256([string]$Path) {
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Test-Verified([string]$Path, [string]$ExpectedSha) {
    if (-not (Test-Path $Path -PathType Leaf)) { return $false }
    return ((Get-Sha256 $Path) -eq $ExpectedSha.ToLowerInvariant())
}

function Require-Hash([string]$Path, [string]$ExpectedSha, [string]$Label) {
    if (-not (Test-Path $Path -PathType Leaf)) { Fail "required $Label missing: $Path" }
    $actual = Get-Sha256 $Path
    if ($actual -ne $ExpectedSha.ToLowerInvariant()) {
        Fail "$Label SHA256 mismatch. Expected $ExpectedSha, got $actual"
    }
    Write-Host "  $Label verified." -ForegroundColor Green
}

function Download-Verified([string]$Url, [string]$Destination, [string]$ExpectedSha, [string]$Label) {
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $Destination) | Out-Null
    if (Test-Path $Destination -PathType Leaf) {
        $actual = Get-Sha256 $Destination
        if ($actual -eq $ExpectedSha.ToLowerInvariant()) {
            Write-Host "  $Label already present and verified." -ForegroundColor Green
            return
        }
        Write-Host "  Existing $Label failed hash verification; removing it." -ForegroundColor Yellow
        Remove-Item -LiteralPath $Destination -Force
    }

    $partial = "$Destination.part"
    $curl = Get-Command curl.exe -ErrorAction SilentlyContinue
    if (-not $curl) { Fail 'curl.exe is required for resumable verified model downloads.' }

    Write-Host "Downloading $Label" -ForegroundColor Cyan
    Write-Host "  $Url" -ForegroundColor DarkGray
    & $curl.Source '--fail' '--location' '--retry' '8' '--retry-delay' '5' '--retry-all-errors' '--continue-at' '-' '--output' $partial $Url
    if ($LASTEXITCODE -ne 0) {
        Fail "$Label download failed with curl exit code $LASTEXITCODE. Partial file was retained for resume: $partial"
    }
    Move-Item -LiteralPath $partial -Destination $Destination -Force
    Require-Hash $Destination $ExpectedSha $Label
}

function Stop-Managed([string]$PidFile) {
    if (-not (Test-Path $PidFile -PathType Leaf)) { return }
    $pidText = (Get-Content -LiteralPath $PidFile -Raw).Trim()
    $managedPid = 0
    if ([int]::TryParse($pidText, [ref]$managedPid) -and $managedPid -gt 0) {
        $p = Get-Process -Id $managedPid -ErrorAction SilentlyContinue
        if ($p) {
            Stop-Process -Id $managedPid -Force
            Start-Sleep -Seconds 2
        }
    }
    Remove-Item -LiteralPath $PidFile -Force -ErrorAction SilentlyContinue
}

function Invoke-Git([string[]]$GitArgs, [string]$FailureMessage) {
    & git.exe @GitArgs
    if ($LASTEXITCODE -ne 0) { Fail "$FailureMessage (git exit code $LASTEXITCODE)" }
}

$SourcePythonDir = Join-Path $SourcePortable 'python_embeded'
$SourcePython = Join-Path $SourcePythonDir 'python.exe'
$Executor = Join-Path $ProjectRepoRoot 'tools\roguelite-asset-studio\flux2_klein_t2i_probe.py'
foreach ($required in @($SourcePython,$Executor)) {
    if (-not (Test-Path $required -PathType Leaf)) { Fail "required source file missing: $required" }
}
if (-not (Get-Command git.exe -ErrorAction SilentlyContinue)) { Fail 'git.exe is required.' }
if (-not (Get-Command robocopy.exe -ErrorAction SilentlyContinue)) { Fail 'robocopy.exe is required.' }

$PortableRoot = Join-Path $Workspace 'ComfyUI_windows_portable'
$PythonDir = Join-Path $PortableRoot 'python_embeded'
$Python = Join-Path $PythonDir 'python.exe'
$ComfyRoot = Join-Path $PortableRoot 'ComfyUI'
$MainPy = Join-Path $ComfyRoot 'main.py'
$ModelPath = Join-Path $ComfyRoot "models\diffusion_models\$ModelName"
$TextEncoderPath = Join-Path $ComfyRoot "models\text_encoders\$TextEncoderName"
$VaePath = Join-Path $ComfyRoot "models\vae\$VaeName"
$SpikeDir = Join-Path $Workspace 'spike'
$PidFile = Join-Path $Workspace '.flux2_klein.pid'
$DepsMarker = Join-Path $PortableRoot ".deps_$ComfyCommit.ok"

New-Item -ItemType Directory -Force -Path $Workspace,$PortableRoot,$SpikeDir | Out-Null

Write-Host ''
Write-Host 'Roguelite Runner 56 - FLUX.2 KLEIN 4B DISTILLED / GENERIC STATIC ASSET SPIKE' -ForegroundColor Cyan
Write-Host '[SCOPE] First real static-generation backend test for the Roguelite Asset Studio.' -ForegroundColor Yellow
Write-Host '[GENERIC PROOF] Generates an architecture_module, not the Exilada.' -ForegroundColor Green
Write-Host '[ISOLATION] Uses Z:\AI\Flux2Klein and does not modify H3/Kontext runtimes.' -ForegroundColor Green
Write-Host "[COMFY PIN] $ComfyCommit" -ForegroundColor Green
Write-Host '[WEIGHTS] FLUX.2 Klein 4B distilled FP8 4.07 GB + full Qwen3-4B 8.04 GB + VAE 0.336 GB = ~12.45 GB.' -ForegroundColor Green
Write-Host '[MODEL LICENSE] FLUX.2 Klein 4B / supporting Comfy repack path: Apache-2.0.' -ForegroundColor Green
Write-Host '[PROBE] 768x768, 4 distilled steps, CFG 1.0, Euler, seed 0.' -ForegroundColor Green
Write-Host ''

# Calculate only the space that is still needed, plus an isolation/runtime reserve.
$missingBytes = [int64]0
if (-not (Test-Verified $ModelPath $ModelSha256)) { $missingBytes += $ModelBytes }
if (-not (Test-Verified $TextEncoderPath $TextEncoderSha256)) { $missingBytes += $TextEncoderBytes }
if (-not (Test-Verified $VaePath $VaeSha256)) { $missingBytes += $VaeBytes }
$runtimeReserve = if (Test-Path $Python -PathType Leaf) { [int64](2GB) } else { [int64](7GB) }
$requiredFree = $missingBytes + $runtimeReserve + [int64](2GB)
$driveRoot = [System.IO.Path]::GetPathRoot($Workspace)
$driveInfo = New-Object System.IO.DriveInfo($driveRoot)
$freeBytes = [int64]$driveInfo.AvailableFreeSpace
$requiredGiB = [math]::Round($requiredFree / 1GB, 2)
$freeGiB = [math]::Round($freeBytes / 1GB, 2)
Write-Host "Disk preflight: free=${freeGiB} GiB; conservative additional requirement=${requiredGiB} GiB." -ForegroundColor Cyan
if ($freeBytes -lt $requiredFree) {
    Fail "insufficient free space on $driveRoot. Need about ${requiredGiB} GiB additional free space; found ${freeGiB} GiB."
}

# Copy the already-proven portable Python once, but never mutate the source runtime.
if (-not (Test-Path $Python -PathType Leaf)) {
    Write-Host 'Creating isolated Python runtime from the proven Kontext portable Python...' -ForegroundColor Cyan
    New-Item -ItemType Directory -Force -Path $PythonDir | Out-Null
    & robocopy.exe $SourcePythonDir $PythonDir /E /COPY:DAT /DCOPY:DAT /R:2 /W:2 /NFL /NDL /NJH /NJS /NP
    $rc = $LASTEXITCODE
    if ($rc -gt 7) { Fail "robocopy of isolated Python runtime failed with code $rc" }
}
if (-not (Test-Path $Python -PathType Leaf)) { Fail "isolated python executable was not created: $Python" }

# Pin an isolated current ComfyUI codebase; never update the existing Kontext checkout.
if (-not (Test-Path (Join-Path $ComfyRoot '.git') -PathType Container)) {
    if (Test-Path $ComfyRoot) { Remove-Item -LiteralPath $ComfyRoot -Recurse -Force }
    Write-Host 'Cloning isolated ComfyUI codebase...' -ForegroundColor Cyan
    Invoke-Git @('clone','--filter=blob:none','--no-checkout',$ComfyRepo,$ComfyRoot) 'ComfyUI clone failed'
}
Write-Host "Pinning ComfyUI to $ComfyCommit" -ForegroundColor Cyan
Invoke-Git @('-C',$ComfyRoot,'fetch','--depth','1','origin',$ComfyCommit) 'ComfyUI pinned commit fetch failed'
Invoke-Git @('-C',$ComfyRoot,'checkout','--detach','--force',$ComfyCommit) 'ComfyUI pinned checkout failed'
$currentCommit = (& git.exe -C $ComfyRoot rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0 -or $currentCommit -ne $ComfyCommit) {
    Fail "ComfyUI checkout mismatch. Expected $ComfyCommit, got $currentCommit"
}

# Install only into the copied Python runtime. A marker makes repeat runs cheap.
if (-not (Test-Path $DepsMarker -PathType Leaf)) {
    Write-Host 'Installing pinned ComfyUI dependencies into the isolated Python runtime...' -ForegroundColor Cyan
    & $Python -s -m pip install --disable-pip-version-check -r (Join-Path $ComfyRoot 'requirements.txt')
    if ($LASTEXITCODE -ne 0) { Fail 'isolated ComfyUI dependency installation failed' }
    Set-Content -LiteralPath $DepsMarker -Value $ComfyCommit -Encoding ASCII
} else {
    Write-Host '  Pinned ComfyUI dependency marker already present.' -ForegroundColor Green
}

Download-Verified $ModelUrl $ModelPath $ModelSha256 'FLUX.2 Klein 4B distilled FP8 (4.07 GB)'
Download-Verified $TextEncoderUrl $TextEncoderPath $TextEncoderSha256 'Qwen3-4B text encoder (8.04 GB)'
Download-Verified $VaeUrl $VaePath $VaeSha256 'FLUX.2 VAE (336 MB)'

$Base = "http://127.0.0.1:$Port"
$UserDir = Join-Path $ComfyRoot 'user'
New-Item -ItemType Directory -Force -Path $UserDir | Out-Null
$StdoutLog = Join-Path $SpikeDir "comfyui_flux2_klein_${Port}_stdout.log"
$StderrLog = Join-Path $SpikeDir "comfyui_flux2_klein_${Port}_stderr.log"
$ExecutorLog = Join-Path $SpikeDir 'flux2_klein_4b_t2i_executor.log'

Stop-Managed $PidFile
try {
    $null = Invoke-RestMethod -Uri "$Base/system_stats" -TimeoutSec 2
    Fail "port $Port is already serving an unmanaged process; stop it or rerun with a different -Port"
} catch {
    if ($_.Exception.Message -like '*unmanaged process*') { throw }
}

$launchArgs = @('-s',$MainPy,'--windows-standalone-build','--listen','127.0.0.1','--port',"$Port",'--disable-auto-launch')
$process = Start-Process -FilePath $Python -ArgumentList $launchArgs -WorkingDirectory $ComfyRoot `
    -RedirectStandardOutput $StdoutLog -RedirectStandardError $StderrLog -WindowStyle Hidden -PassThru
Set-Content -LiteralPath $PidFile -Value $process.Id -Encoding ASCII
Write-Host "Started isolated FLUX.2 ComfyUI PID $($process.Id) on port $Port" -ForegroundColor Green

$ready = $false
for ($i=0; $i -lt 300; $i++) {
    try {
        $null = Invoke-RestMethod -Uri "$Base/system_stats" -TimeoutSec 2
        $ready = $true
        break
    } catch {
        if ($process.HasExited) {
            if (Test-Path $StderrLog) { Get-Content -LiteralPath $StderrLog -Tail 220 }
            Stop-Managed $PidFile
            Fail "isolated ComfyUI exited before readiness with code $($process.ExitCode)"
        }
        Start-Sleep -Seconds 1
    }
}
if (-not $ready) {
    Stop-Managed $PidFile
    if (Test-Path $StderrLog) { Get-Content -LiteralPath $StderrLog -Tail 220 }
    Fail "isolated ComfyUI did not become ready at $Base"
}

if (Test-Path $ExecutorLog) { Remove-Item -LiteralPath $ExecutorLog -Force }
try {
    & $Python -s $Executor `
        --comfy-root $ComfyRoot `
        --workspace $Workspace `
        --port $Port `
        --timeout-minutes $TimeoutMinutes `
        --comfy-commit $ComfyCommit 2>&1 | Tee-Object -FilePath $ExecutorLog | ForEach-Object { Write-Host $_ }
    $executorExit = $LASTEXITCODE
} finally {
    Stop-Managed $PidFile
}

if ($executorExit -ne 0) {
    if (Test-Path $ExecutorLog) { Get-Content -LiteralPath $ExecutorLog -Tail 260 }
    if (Test-Path $StderrLog) { Get-Content -LiteralPath $StderrLog -Tail 260 }
    Fail "FLUX.2 Klein probe executor exited with code $executorExit"
}

$Output = Join-Path $SpikeDir 'flux2_klein_4b_t2i_probe.png'
$Manifest = Join-Path $SpikeDir 'flux2_klein_4b_t2i_manifest.json'
$PromptJson = Join-Path $SpikeDir 'flux2_klein_4b_t2i_prompt.json'
foreach ($f in @($Output,$Manifest,$PromptJson,$ExecutorLog)) {
    if (-not (Test-Path $f -PathType Leaf)) { Fail "expected probe output missing: $f" }
}

Write-Host ''
Write-Host 'RUNNER56-FLUX2-KLEIN: PASS - TECHNICAL T2I INFERENCE COMPLETE / VISUAL VERDICT PENDING' -ForegroundColor Green
Write-Host "Generated architecture-module candidate: $Output" -ForegroundColor Cyan
Write-Host "Manifest: $Manifest" -ForegroundColor Cyan
Write-Host "Executor log: $ExecutorLog" -ForegroundColor Cyan
Write-Host 'Next gate after visual review: promote Klein to an installed Asset Studio adapter and test single/multi-reference editing.' -ForegroundColor Yellow
