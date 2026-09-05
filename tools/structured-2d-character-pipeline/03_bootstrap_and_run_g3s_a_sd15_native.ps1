param(
    [string]$RepoRoot = 'D:\GOOGLE DRIVE\DEV\Roguelite',
    [string]$QwenWorkspace = 'Z:\AI\QwenImageEditSpike',
    [string]$PipelineWorkspace = 'Z:\AI\RogueliteCharacterPipeline',
    [int]$Port = 8216,
    [long]$Seed = 20260905
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Fail([string]$Message) {
    Write-Host "G3S-A SD15: FAIL - $Message" -ForegroundColor Red
    exit 1
}

function Ensure-Download([string]$Url, [string]$Path, [string]$Sha256) {
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $Path) | Out-Null
    if (Test-Path $Path -PathType Leaf) {
        $got = (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
        if ($got -eq $Sha256.ToLowerInvariant()) {
            Write-Host "[OK] Reusing verified $(Split-Path -Leaf $Path)" -ForegroundColor Green
            return
        }
        Fail "Existing file has wrong SHA256 and will not be overwritten automatically: $Path | got=$got expected=$Sha256"
    }
    $part = "$Path.part"
    Remove-Item $part -Force -ErrorAction SilentlyContinue
    Write-Host "[DOWNLOAD] $(Split-Path -Leaf $Path)" -ForegroundColor Cyan
    & curl.exe -L --fail --retry 3 --retry-delay 3 -o $part $Url
    if ($LASTEXITCODE -ne 0) { Fail "curl failed downloading $Url" }
    $got = (Get-FileHash -LiteralPath $part -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($got -ne $Sha256.ToLowerInvariant()) {
        Remove-Item $part -Force -ErrorAction SilentlyContinue
        Fail "SHA256 mismatch for $(Split-Path -Leaf $Path): got=$got expected=$Sha256"
    }
    Move-Item -LiteralPath $part -Destination $Path -Force
    Write-Host "[OK] Verified $got" -ForegroundColor Green
}

Write-Host ''
Write-Host 'Roguelite - G3S-A NATIVE SD1.5 PIXEL REAUTHOR' -ForegroundColor Cyan
Write-Host 'One static candidate only. Qwen official-resolution output is conditioning/reference only.'
Write-Host 'Final generated pixels are sampled directly at 640x360 and are never post-resized.' -ForegroundColor Yellow
Write-Host ''

if (-not (Test-Path $RepoRoot -PathType Container)) { Fail "Repository root not found: $RepoRoot" }

$PortableRoot = Join-Path $QwenWorkspace 'ComfyUI_windows_portable'
$ComfyRoot = Join-Path $PortableRoot 'ComfyUI'
$Python = Join-Path $PortableRoot 'python_embeded\python.exe'
$MainPy = Join-Path $ComfyRoot 'main.py'
$Helper = Join-Path $RepoRoot 'tools\structured-2d-character-pipeline\g3s_a_sd15_native_reauthor.py'
$Control = Join-Path $PipelineWorkspace 'g3s_a_control\g3s_a_control_official_raw.png'

foreach ($p in @($Python,$MainPy,$Helper,$Control)) {
    if (-not (Test-Path $p -PathType Leaf)) { Fail "Required file missing: $p" }
}

$Checkpoint = Join-Path $ComfyRoot 'models\checkpoints\v1-5-pruned-emaonly.safetensors'
$Lora = Join-Path $ComfyRoot 'models\loras\pixel-art-sd15.safetensors'

# Stable Diffusion 1.5 checkpoint: 4.27 GB, CreativeML OpenRAIL-M.
Ensure-Download `
  'https://huggingface.co/stable-diffusion-v1-5/stable-diffusion-v1-5/resolve/main/v1-5-pruned-emaonly.safetensors' `
  $Checkpoint `
  '6ce0161689b3853acaa03779ec93eafe75a02f4ced659bee03f50797806fa2fa'

# SedatAl pixel-art LoRA for SD1.5: 3.23 MB, CreativeML OpenRAIL-M.
Ensure-Download `
  'https://huggingface.co/SedatAl/pixel-art-LoRa/resolve/main/pytorch_lora_weights.safetensors' `
  $Lora `
  'ad5034703699e910d5f9525ea5db64abcbd8d7396ff8f771c09403f3adb048ad'

$OutDir = Join-Path $PipelineWorkspace 'g3s_a_sd15'
$LogDir = Join-Path $OutDir 'logs'
New-Item -ItemType Directory -Force -Path $OutDir,$LogDir | Out-Null
Get-ChildItem $OutDir -File -ErrorAction SilentlyContinue | Where-Object { $_.Name -like 'g3s_a_sd15_*' } | Remove-Item -Force
$Stdout = Join-Path $LogDir 'comfy_stdout.log'
$Stderr = Join-Path $LogDir 'comfy_stderr.log'
Remove-Item $Stdout,$Stderr -Force -ErrorAction SilentlyContinue

$Api = "http://127.0.0.1:$Port"
try {
    $probe = Invoke-WebRequest -Uri "$Api/object_info" -Method Get -TimeoutSec 2 -UseBasicParsing
    if ($probe.StatusCode -eq 200) { Fail "Port $Port already serves ComfyUI. Refusing to attach to unknown process." }
} catch {}

$proc = $null
try {
    Write-Host "[START] isolated ComfyUI on 127.0.0.1:$Port (low-VRAM)..." -ForegroundColor Cyan
    $serverArgs = @(
        '-s', $MainPy,
        '--windows-standalone-build',
        '--listen', '127.0.0.1',
        '--port', [string]$Port,
        '--disable-auto-launch',
        '--lowvram'
    )
    $proc = Start-Process -FilePath $Python -ArgumentList $serverArgs -WorkingDirectory $ComfyRoot -PassThru -RedirectStandardOutput $Stdout -RedirectStandardError $Stderr

    $deadline = (Get-Date).AddSeconds(180)
    $ready = $false
    while ((Get-Date) -lt $deadline) {
        if ($proc.HasExited) { Fail "ComfyUI exited during startup with code $($proc.ExitCode). See $Stdout and $Stderr" }
        try {
            $r = Invoke-WebRequest -Uri "$Api/object_info" -Method Get -TimeoutSec 10 -UseBasicParsing
            if ($r.StatusCode -eq 200) { $ready = $true; break }
        } catch {}
        Start-Sleep -Milliseconds 750
    }
    if (-not $ready) { Fail "Timed out waiting for ComfyUI. See $Stdout and $Stderr" }
    Write-Host '[OK] Runtime schema ready.' -ForegroundColor Green

    Write-Host '[RUN] native SD1.5 img2img reauthor with pixel-art LoRA...' -ForegroundColor Cyan
    & $Python $Helper `
        --api $Api `
        --comfy-root $ComfyRoot `
        --control $Control `
        --output-dir $OutDir `
        --seed $Seed `
        --timeout-seconds 1800
    $code = $LASTEXITCODE
    if ($code -ne 0) {
        Write-Host ''
        Write-Host '[COMFY STDERR TAIL]' -ForegroundColor DarkYellow
        if (Test-Path $Stderr) { Get-Content $Stderr -Tail 80 -ErrorAction SilentlyContinue | Out-Host }
        Fail "native SD1.5 helper exited with code $code"
    }
}
finally {
    if ($null -ne $proc -and -not $proc.HasExited) {
        Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
        try { $proc.WaitForExit(5000) | Out-Null } catch {}
    }
}

$Contact = Join-Path $OutDir 'g3s_a_sd15_contact_sheet.png'
$Raw = Join-Path $OutDir 'g3s_a_sd15_raw.png'
$Result = Join-Path $OutDir 'g3s_a_sd15_result.json'
foreach ($p in @($Contact,$Raw,$Result)) {
    if (-not (Test-Path $p -PathType Leaf)) { Fail "Expected output missing: $p" }
}

Write-Host ''
Write-Host 'G3S-A SD15: REVIEW REQUIRED' -ForegroundColor Yellow
Write-Host "CONTACT SHEET: $Contact"
Write-Host "RAW:           $Raw"
Write-Host "RESULT:        $Result"
Write-Host ''
Write-Host 'STOP. Review topology first, then Exilada identity and native 1x pixel-cluster language. Do not start G3S-B.' -ForegroundColor Yellow
