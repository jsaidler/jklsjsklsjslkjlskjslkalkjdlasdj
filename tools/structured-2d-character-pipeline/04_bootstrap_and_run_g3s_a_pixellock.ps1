param(
    [string]$RepoRoot = 'D:\GOOGLE DRIVE\DEV\Roguelite',
    [string]$PipelineWorkspace = 'Z:\AI\RogueliteCharacterPipeline',
    [string]$DependencyRoot = 'Z:\AI\PixelLockSpike',
    [int]$Port = 8221
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$PixelLockCommit = 'bb682f9919fcd302eaa5226b7e6965dfdf151beb'
$ModelRevision = 'd35e3bcc3c8651603393042df4dbf2a1d37173ea'
$LlamaBuild = 'b10516'
$LlamaZipSha = '96d64faeb5b8e655341f32b26ad3e51fbea8bff0bc8120ad3dbffdc0b05b8ad3'
$CudaZipSha = '8c79a9b226de4b3cacfd1f83d24f962d0773be79f1e7b75c6af4ded7e32ae1d6'

function Fail([string]$Message) {
    Write-Host "G3S-A PIXELLOCK: FAIL - $Message" -ForegroundColor Red
    exit 1
}

function Ensure-VerifiedDownload([string]$Url, [string]$Path, [string]$ExpectedSha) {
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $Path) | Out-Null
    if (Test-Path $Path -PathType Leaf) {
        $got = (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
        if ($got -eq $ExpectedSha.ToLowerInvariant()) {
            Write-Host "[OK] Reusing verified $(Split-Path -Leaf $Path)" -ForegroundColor Green
            return
        }
        Fail "Existing file has wrong SHA256: $Path | got=$got expected=$ExpectedSha"
    }

    $part = "$Path.part"
    Write-Host "[DOWNLOAD] $(Split-Path -Leaf $Path)" -ForegroundColor Cyan
    $curlArgs = @('-L','--fail','--retry','4','--retry-delay','4','-C','-','-o',$part,$Url)
    & curl.exe @curlArgs
    if ($LASTEXITCODE -ne 0) { Fail "curl failed downloading $Url" }
    $got = (Get-FileHash -LiteralPath $part -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($got -ne $ExpectedSha.ToLowerInvariant()) {
        Fail "SHA256 mismatch for $(Split-Path -Leaf $Path): got=$got expected=$ExpectedSha"
    }
    Move-Item -LiteralPath $part -Destination $Path -Force
    Write-Host "[OK] Verified $got" -ForegroundColor Green
}

function Ensure-PinnedModel([string]$Url, [string]$Path, [string]$ReceiptPath) {
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $Path) | Out-Null
    if (Test-Path $Path -PathType Leaf) {
        Write-Host '[CHECK] Verifying existing PixelLock GGUF...' -ForegroundColor Cyan
        $got = (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
        if (Test-Path $ReceiptPath -PathType Leaf) {
            $receipt = Get-Content $ReceiptPath -Raw | ConvertFrom-Json
            if ($receipt.revision -ne $ModelRevision) { Fail "PixelLock model receipt revision mismatch: $($receipt.revision)" }
            if ($receipt.sha256 -ne $got) { Fail "PixelLock model SHA256 differs from receipt: got=$got expected=$($receipt.sha256)" }
        } else {
            [pscustomobject]@{
                source = $Url
                revision = $ModelRevision
                file = (Split-Path -Leaf $Path)
                sha256 = $got
                bytes = (Get-Item -LiteralPath $Path).Length
            } | ConvertTo-Json | Set-Content -LiteralPath $ReceiptPath -Encoding UTF8
        }
        Write-Host "[OK] PixelLock GGUF SHA256 $got" -ForegroundColor Green
        return
    }

    $part = "$Path.part"
    Write-Host '[DOWNLOAD] PixelLock Gemma-4 12B Q4_K_M (~7.4 GB)...' -ForegroundColor Cyan
    & curl.exe -L --fail --retry 4 --retry-delay 5 -C - -o $part $Url
    if ($LASTEXITCODE -ne 0) { Fail 'PixelLock GGUF download failed.' }
    Move-Item -LiteralPath $part -Destination $Path -Force
    Write-Host '[CHECK] Hashing downloaded PixelLock GGUF...' -ForegroundColor Cyan
    $got = (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
    [pscustomobject]@{
        source = $Url
        revision = $ModelRevision
        file = (Split-Path -Leaf $Path)
        sha256 = $got
        bytes = (Get-Item -LiteralPath $Path).Length
    } | ConvertTo-Json | Set-Content -LiteralPath $ReceiptPath -Encoding UTF8
    Write-Host "[OK] PixelLock GGUF pinned revision=$ModelRevision SHA256=$got" -ForegroundColor Green
}

function Test-Api([string]$BaseUrl) {
    try {
        $r = Invoke-WebRequest -Uri "$BaseUrl/v1/models" -Method Get -TimeoutSec 8 -UseBasicParsing
        return ($r.StatusCode -eq 200)
    } catch {
        return $false
    }
}

function Start-PixelLockServer([string]$ServerExe, [string]$ModelPath, [string]$LogDir) {
    $attempts = @(99, 45, 20)
    foreach ($layers in $attempts) {
        $stdout = Join-Path $LogDir "llama_ngl_${layers}_stdout.log"
        $stderr = Join-Path $LogDir "llama_ngl_${layers}_stderr.log"
        Remove-Item $stdout,$stderr -Force -ErrorAction SilentlyContinue
        Write-Host "[START] llama.cpp $LlamaBuild | context 32768 | GPU layers $layers..." -ForegroundColor Cyan
        $serverArgs = @(
            '-m', $ModelPath,
            '--alias', 'gemma-4-12b',
            '--host', '127.0.0.1',
            '--port', [string]$Port,
            '-c', '32768',
            '-ngl', [string]$layers,
            '--cache-type-k', 'q4_0',
            '--cache-type-v', 'q4_0',
            '--flash-attn', 'on'
        )
        $proc = Start-Process -FilePath $ServerExe -ArgumentList $serverArgs -WorkingDirectory (Split-Path -Parent $ServerExe) -PassThru -RedirectStandardOutput $stdout -RedirectStandardError $stderr
        $deadline = (Get-Date).AddSeconds(240)
        while ((Get-Date) -lt $deadline) {
            if ($proc.HasExited) { break }
            if (Test-Api "http://127.0.0.1:$Port") {
                Write-Host "[OK] PixelLock model server ready with -ngl $layers" -ForegroundColor Green
                return [pscustomobject]@{ Process=$proc; Layers=$layers; Stdout=$stdout; Stderr=$stderr }
            }
            Start-Sleep -Seconds 2
        }
        if (-not $proc.HasExited) {
            Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
            try { $proc.WaitForExit(5000) | Out-Null } catch {}
        }
        Write-Host "[WARN] llama.cpp did not become ready with -ngl $layers; trying lower GPU offload." -ForegroundColor Yellow
        if (Test-Path $stderr) { Get-Content $stderr -Tail 12 -ErrorAction SilentlyContinue | Out-Host }
    }
    Fail 'llama.cpp could not start PixelLock at -ngl 99, 45, or 20. See dependency logs.'
}

Write-Host ''
Write-Host 'Roguelite - G3S-A PIXELLOCK NATIVE GRID' -ForegroundColor Cyan
Write-Host 'No latent diffusion. PixelLock authors a grammar-constrained palette-indexed grid.'
Write-Host '64x64 conditioning scaffold -> model-generated 128x128 grid; no post-generation resize.' -ForegroundColor Yellow
Write-Host ''

if (-not (Test-Path $RepoRoot -PathType Container)) { Fail "Repository root not found: $RepoRoot" }
$FailureMarker = Join-Path $RepoRoot 'tools\structured-2d-character-pipeline\g3s_a_sd15_failure.json'
$Helper = Join-Path $RepoRoot 'tools\structured-2d-character-pipeline\g3s_a_pixellock_native.py'
$Control = Join-Path $PipelineWorkspace 'g3s_a_control\g3s_a_control_official_raw.png'
foreach ($p in @($FailureMarker,$Helper,$Control)) {
    if (-not (Test-Path $p -PathType Leaf)) { Fail "Required file missing: $p. Run git pull --ff-only first." }
}
$failure = Get-Content $FailureMarker -Raw | ConvertFrom-Json
if ($failure.gate -ne 'G3S-A-SD15' -or $failure.status -ne 'FAIL') { Fail 'SD1.5 native route is not canonically closed FAIL.' }

$Python = 'Z:\AI\QwenImageEditSpike\ComfyUI_windows_portable\python_embeded\python.exe'
if (-not (Test-Path $Python -PathType Leaf)) { Fail "Existing embedded Python not found: $Python" }

New-Item -ItemType Directory -Force -Path $DependencyRoot | Out-Null
$ModelDir = Join-Path $DependencyRoot 'models'
$ModelPath = Join-Path $ModelDir 'pixellock-gemma-12b-q4_k_m.gguf'
$ModelReceipt = Join-Path $ModelDir 'pixellock-gemma-12b-q4_k_m.receipt.json'
if (-not (Test-Path $ModelPath -PathType Leaf)) {
    $driveName = ([System.IO.Path]::GetPathRoot($DependencyRoot)).TrimEnd('\').TrimEnd(':')
    $drive = Get-PSDrive -Name $driveName -ErrorAction SilentlyContinue
    if ($null -ne $drive) {
        $freeGB = [math]::Round($drive.Free / 1GB, 1)
        Write-Host "[CHECK] Free disk on ${driveName}: $freeGB GB" -ForegroundColor Cyan
        if ($drive.Free -lt 10GB) { Fail "At least 10 GB free is required for first PixelLock provisioning; found $freeGB GB." }
    }
}

$DownloadDir = Join-Path $DependencyRoot 'downloads'
$LlamaZip = Join-Path $DownloadDir "llama-$LlamaBuild-bin-win-cuda-12.4-x64.zip"
$CudaZip = Join-Path $DownloadDir 'cudart-llama-bin-win-cuda-12.4-x64.zip'
Ensure-VerifiedDownload "https://github.com/ggml-org/llama.cpp/releases/download/$LlamaBuild/llama-$LlamaBuild-bin-win-cuda-12.4-x64.zip" $LlamaZip $LlamaZipSha
Ensure-VerifiedDownload "https://github.com/ggml-org/llama.cpp/releases/download/$LlamaBuild/cudart-llama-bin-win-cuda-12.4-x64.zip" $CudaZip $CudaZipSha

$LlamaRoot = Join-Path $DependencyRoot "llama-$LlamaBuild-cuda12.4"
$ServerExe = $null
if (Test-Path $LlamaRoot -PathType Container) {
    $found = @(Get-ChildItem $LlamaRoot -Filter 'llama-server.exe' -File -Recurse -ErrorAction SilentlyContinue)
    if ($found.Count -gt 0) { $ServerExe = $found[0].FullName }
}
if ($null -eq $ServerExe) {
    Remove-Item $LlamaRoot -Recurse -Force -ErrorAction SilentlyContinue
    New-Item -ItemType Directory -Force -Path $LlamaRoot | Out-Null
    Write-Host "[INSTALL] Extracting llama.cpp $LlamaBuild CUDA 12.4 runtime..." -ForegroundColor Cyan
    Expand-Archive -LiteralPath $LlamaZip -DestinationPath $LlamaRoot -Force
    Expand-Archive -LiteralPath $CudaZip -DestinationPath $LlamaRoot -Force
    $found = @(Get-ChildItem $LlamaRoot -Filter 'llama-server.exe' -File -Recurse -ErrorAction SilentlyContinue)
    if ($found.Count -eq 0) { Fail "llama-server.exe not found after extraction: $LlamaRoot" }
    $ServerExe = $found[0].FullName
}
Write-Host "[OK] llama-server: $ServerExe" -ForegroundColor Green

$PixelLockRoot = Join-Path $DependencyRoot 'pixellock'
if (-not (Test-Path (Join-Path $PixelLockRoot '.git') -PathType Container)) {
    Remove-Item $PixelLockRoot -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host '[INSTALL] Cloning PixelLock code...' -ForegroundColor Cyan
    & git.exe clone --no-checkout 'https://github.com/solarkyle/pixellock.git' $PixelLockRoot
    if ($LASTEXITCODE -ne 0) { Fail 'git clone PixelLock failed.' }
}
& git.exe -C $PixelLockRoot fetch --depth 1 origin $PixelLockCommit
if ($LASTEXITCODE -ne 0) { Fail "Could not fetch pinned PixelLock commit $PixelLockCommit" }
& git.exe -C $PixelLockRoot checkout --detach --force $PixelLockCommit
if ($LASTEXITCODE -ne 0) { Fail "Could not checkout PixelLock commit $PixelLockCommit" }
$head = (& git.exe -C $PixelLockRoot rev-parse HEAD).Trim()
if ($head -ne $PixelLockCommit) { Fail "PixelLock checkout mismatch: got=$head expected=$PixelLockCommit" }
Write-Host "[OK] PixelLock code pinned: $head" -ForegroundColor Green

$ModelUrl = "https://huggingface.co/solarkyle/pixellock-gemma-12b-pixelart-gguf/resolve/$ModelRevision/pixellock-gemma-12b-q4_k_m.gguf?download=true"
Ensure-PinnedModel $ModelUrl $ModelPath $ModelReceipt

& $Python -c 'import PIL, numpy, httpx' *> $null
if ($LASTEXITCODE -ne 0) {
    Write-Host '[INSTALL] Python dependency httpx 0.28.1...' -ForegroundColor Cyan
    & $Python -m pip install --disable-pip-version-check --no-warn-script-location 'httpx==0.28.1'
    if ($LASTEXITCODE -ne 0) { Fail 'Could not install httpx into existing embedded Python.' }
    & $Python -c 'import PIL, numpy, httpx'
    if ($LASTEXITCODE -ne 0) { Fail 'Python preflight failed: PIL/numpy/httpx unavailable.' }
}
Write-Host '[OK] Python PIL/numpy/httpx ready.' -ForegroundColor Green

$OutDir = Join-Path $PipelineWorkspace 'g3s_a_pixellock'
$LogDir = Join-Path $OutDir 'logs'
Remove-Item $OutDir -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force -Path $OutDir,$LogDir | Out-Null

if (Test-Api "http://127.0.0.1:$Port") { Fail "Port $Port already serves an API. Refusing to attach to an unknown process." }
$server = $null
try {
    $server = Start-PixelLockServer $ServerExe $ModelPath $LogDir
    Write-Host '[RUN] one PixelLock 64->128 footprint-locked Exilada source candidate...' -ForegroundColor Cyan
    & $Python $Helper `
        --api "http://127.0.0.1:$Port" `
        --pixellock-root $PixelLockRoot `
        --control $Control `
        --output-dir $OutDir `
        --model-path $ModelPath `
        --model-revision $ModelRevision `
        --pixellock-commit $PixelLockCommit `
        --llama-build "$LlamaBuild / ngl=$($server.Layers) / ctx=32768 / KV=q4_0"
    $code = $LASTEXITCODE
    if ($code -ne 0) {
        Write-Host ''
        Write-Host '[LLAMA STDERR TAIL]' -ForegroundColor DarkYellow
        if (Test-Path $server.Stderr) { Get-Content $server.Stderr -Tail 60 -ErrorAction SilentlyContinue | Out-Host }
        Fail "PixelLock helper exited with code $code"
    }
}
finally {
    if ($null -ne $server -and $null -ne $server.Process -and -not $server.Process.HasExited) {
        Stop-Process -Id $server.Process.Id -Force -ErrorAction SilentlyContinue
        try { $server.Process.WaitForExit(5000) | Out-Null } catch {}
    }
}

$Contact = Join-Path $OutDir 'g3s_a_pixellock_contact_sheet.png'
$Raw = Join-Path $OutDir 'g3s_a_pixellock_raw128.png'
$Result = Join-Path $OutDir 'g3s_a_pixellock_result.json'
foreach ($p in @($Contact,$Raw,$Result)) {
    if (-not (Test-Path $p -PathType Leaf)) { Fail "Expected output missing: $p" }
}

Write-Host ''
Write-Host 'G3S-A PIXELLOCK: REVIEW REQUIRED' -ForegroundColor Yellow
Write-Host "CONTACT SHEET: $Contact"
Write-Host "RAW 128x128:   $Raw"
Write-Host "RESULT:        $Result"
Write-Host ''
Write-Host 'STOP. Review topology first, then Exilada identity and native pixel-cluster language. Do not run G3S-B or G4.' -ForegroundColor Yellow
