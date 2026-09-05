param(
    [string]$RepoRoot = 'D:\GOOGLE DRIVE\DEV\Roguelite',
    [string]$QwenWorkspace = 'Z:\AI\QwenImageEditSpike',
    [string]$PipelineWorkspace = 'Z:\AI\RogueliteCharacterPipeline',
    [int]$Port = 8214,
    [long]$Seed = 20260905
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Fail([string]$Message) {
    Write-Host "G3S-A: FAIL - $Message" -ForegroundColor Red
    exit 1
}

Write-Host ''
Write-Host 'Roguelite - G3S-A STATIC PRODUCTION PIXEL SOURCE' -ForegroundColor Cyan
Write-Host 'One static Exilada source-art candidate only. No animation frames are generated.'
Write-Host 'Uses the existing isolated Qwen-Image-Edit-2509 runtime; this runner downloads nothing.' -ForegroundColor Yellow
Write-Host ''

if (-not (Test-Path $RepoRoot -PathType Container)) { Fail "Repository root not found: $RepoRoot" }

$FailureMarker = Join-Path $RepoRoot 'tools\deterministic-character-pipeline\g3v_failure.json'
if (-not (Test-Path $FailureMarker -PathType Leaf)) { Fail "G3V failure marker missing: $FailureMarker. Run git pull --ff-only first." }
$Failure = Get-Content $FailureMarker -Raw | ConvertFrom-Json
if ($Failure.gate -ne 'G3V' -or $Failure.status -ne 'FAIL') { Fail 'G3V is not canonically recorded FAIL.' }

$Master = Join-Path $RepoRoot 'assets\source\characters\exilada\reference\exilada_master.png'
$Helper = Join-Path $RepoRoot 'tools\structured-2d-character-pipeline\g3s_a_static_source.py'
foreach ($p in @($Master,$Helper)) {
    if (-not (Test-Path $p -PathType Leaf)) { Fail "Required file missing: $p" }
}

$PortableRoot = Join-Path $QwenWorkspace 'ComfyUI_windows_portable'
$ComfyRoot = Join-Path $PortableRoot 'ComfyUI'
$Python = Join-Path $PortableRoot 'python_embeded\python.exe'
$MainPy = Join-Path $ComfyRoot 'main.py'
$Model = Join-Path $ComfyRoot 'models\unet\Qwen-Image-Edit-2509-Q4_0.gguf'
$Clip = Join-Path $ComfyRoot 'models\text_encoders\qwen_2.5_vl_7b_fp8_scaled.safetensors'
$Vae = Join-Path $ComfyRoot 'models\vae\qwen_image_vae.safetensors'

$Missing = @(@($Python,$MainPy,$Model,$Clip,$Vae) | Where-Object { -not (Test-Path $_ -PathType Leaf) })
if ($Missing.Count -gt 0) {
    Write-Host 'G3S-A will not download large dependencies implicitly. Missing:' -ForegroundColor Red
    $Missing | ForEach-Object { Write-Host "  - $_" -ForegroundColor Red }
    Write-Host ''
    Write-Host 'The preserved Qwen setup scripts are under tools\qwen-image-edit-2509-spike\.' -ForegroundColor Yellow
    exit 1
}

$MasterHash = (Get-FileHash -LiteralPath $Master -Algorithm SHA256).Hash.ToLowerInvariant()
Write-Host "[OK] Canonical Exilada master: $MasterHash" -ForegroundColor Green
Write-Host '[OK] Existing Qwen 2509 Q4_0 + Qwen VL encoder + VAE found.' -ForegroundColor Green
Write-Host '[LOCK] 640x360 native canvas | target character ~128 px | seed fixed | no post-inference resize.' -ForegroundColor Cyan

$OutDir = Join-Path $PipelineWorkspace 'g3s_a'
$LogDir = Join-Path $OutDir 'logs'
New-Item -ItemType Directory -Force -Path $OutDir,$LogDir | Out-Null
Get-ChildItem $OutDir -File -ErrorAction SilentlyContinue | Where-Object { $_.Name -like 'g3s_a_*' } | Remove-Item -Force
$Stdout = Join-Path $LogDir 'comfy_stdout.log'
$Stderr = Join-Path $LogDir 'comfy_stderr.log'
Remove-Item $Stdout,$Stderr -Force -ErrorAction SilentlyContinue

$Api = "http://127.0.0.1:$Port"
try {
    $probe = Invoke-WebRequest -Uri "$Api/object_info" -Method Get -TimeoutSec 2 -UseBasicParsing
    if ($probe.StatusCode -eq 200) { Fail "Port $Port already serves ComfyUI. Refusing to attach to an unknown process." }
} catch {
    if ($_.Exception.Message -like 'G3S-A: FAIL*') { throw }
}

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
    if (-not $ready) { Fail "Timed out waiting for ComfyUI /object_info. See $Stdout and $Stderr" }
    Write-Host '[OK] Runtime schema endpoint ready.' -ForegroundColor Green

    Write-Host '[RUN] Qwen-Image-Edit-2509 one-shot static source candidate...' -ForegroundColor Cyan
    & $Python $Helper `
        --api $Api `
        --comfy-root $ComfyRoot `
        --master $Master `
        --output-dir $OutDir `
        --seed $Seed `
        --timeout-seconds 2700
    $HelperExit = $LASTEXITCODE
    if ($HelperExit -ne 0) {
        Write-Host ''
        Write-Host '[COMFY STDERR TAIL]' -ForegroundColor DarkYellow
        if (Test-Path $Stderr) { Get-Content $Stderr -Tail 80 -ErrorAction SilentlyContinue | Out-Host }
        Fail "G3S-A helper exited with code $HelperExit. See $Stdout and $Stderr"
    }
}
finally {
    if ($null -ne $proc -and -not $proc.HasExited) {
        Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
        try { $proc.WaitForExit(5000) | Out-Null } catch {}
    }
}

$ResultPath = Join-Path $OutDir 'g3s_a_result.json'
$Contact = Join-Path $OutDir 'g3s_a_contact_sheet.png'
$Raw = Join-Path $OutDir 'g3s_a_qwen_raw.png'
$Quant = Join-Path $OutDir 'g3s_a_same_raster_32color.png'
foreach ($p in @($ResultPath,$Contact,$Raw,$Quant)) {
    if (-not (Test-Path $p -PathType Leaf)) { Fail "Expected output missing: $p" }
}
$Result = Get-Content $ResultPath -Raw | ConvertFrom-Json
if ($Result.gate -ne 'G3S-A' -or $Result.status -ne 'REVIEW_REQUIRED') { Fail 'Unexpected G3S-A result status.' }
if ([int]$Result.canvas[0] -ne 640 -or [int]$Result.canvas[1] -ne 360) { Fail 'G3S-A output canvas contract changed unexpectedly.' }
if ([bool]$Result.rules.post_inference_resize) { Fail 'G3S-A illegally resized the generated image.' }

Write-Host ''
Write-Host 'G3S-A: REVIEW REQUIRED' -ForegroundColor Yellow
Write-Host "CONTACT SHEET: $Contact"
Write-Host "RAW:           $Raw"
Write-Host "32-COLOR VIEW: $Quant"
Write-Host "RESULT:        $ResultPath"
Write-Host ''
Write-Host 'STOP. Review topology first, then Exilada identity, native 1x pixel language, scale, hair/cloth/restraints. Do not decompose or animate yet.' -ForegroundColor Yellow
