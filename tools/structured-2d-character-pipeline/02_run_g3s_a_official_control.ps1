param(
    [string]$RepoRoot = 'D:\GOOGLE DRIVE\DEV\Roguelite',
    [string]$QwenWorkspace = 'Z:\AI\QwenImageEditSpike',
    [string]$PipelineWorkspace = 'Z:\AI\RogueliteCharacterPipeline',
    [int]$Port = 8215,
    [long]$Seed = 20260905
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Fail([string]$Message) {
    Write-Host "G3S-A CONTROL: FAIL - $Message" -ForegroundColor Red
    exit 1
}

Write-Host ''
Write-Host 'Roguelite - G3S-A QWEN OFFICIAL-RESOLUTION CONTROL' -ForegroundColor Cyan
Write-Host 'Diagnostic only. This output can NEVER become final sprite art and will not be resized/promoted.' -ForegroundColor Yellow
Write-Host ''

$PortableRoot = Join-Path $QwenWorkspace 'ComfyUI_windows_portable'
$ComfyRoot = Join-Path $PortableRoot 'ComfyUI'
$Python = Join-Path $PortableRoot 'python_embeded\python.exe'
$MainPy = Join-Path $ComfyRoot 'main.py'
$Model = Join-Path $ComfyRoot 'models\unet\Qwen-Image-Edit-2509-Q4_0.gguf'
$Clip = Join-Path $ComfyRoot 'models\text_encoders\qwen_2.5_vl_7b_fp8_scaled.safetensors'
$Vae = Join-Path $ComfyRoot 'models\vae\qwen_image_vae.safetensors'
$Helper = Join-Path $RepoRoot 'tools\structured-2d-character-pipeline\g3s_a_qwen_official_control.py'
$Master = Join-Path $RepoRoot 'assets\source\characters\exilada\reference\exilada_master.png'
$Required = @($Python,$MainPy,$Model,$Clip,$Vae,$Helper,$Master)
$Missing = @($Required | Where-Object { -not (Test-Path $_ -PathType Leaf) })
if ($Missing.Count -gt 0) {
    $Missing | ForEach-Object { Write-Host "  - $_" -ForegroundColor Red }
    Fail 'Required provisioned Qwen/control files are missing.'
}

$OutDir = Join-Path $PipelineWorkspace 'g3s_a_control'
$LogDir = Join-Path $OutDir 'logs'
New-Item -ItemType Directory -Force -Path $OutDir,$LogDir | Out-Null
Get-ChildItem $OutDir -File -ErrorAction SilentlyContinue | Where-Object { $_.Name -like 'g3s_a_control_*' } | Remove-Item -Force
$Stdout = Join-Path $LogDir 'comfy_stdout.log'
$Stderr = Join-Path $LogDir 'comfy_stderr.log'
Remove-Item $Stdout,$Stderr -Force -ErrorAction SilentlyContinue

$Api = "http://127.0.0.1:$Port"
try {
    $probe = Invoke-WebRequest -Uri "$Api/object_info" -Method Get -TimeoutSec 2 -UseBasicParsing
    if ($probe.StatusCode -eq 200) { Fail "Port $Port already serves ComfyUI." }
} catch {}

$proc = $null
try {
    Write-Host "[START] isolated ComfyUI control on 127.0.0.1:$Port..." -ForegroundColor Cyan
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
        if ($proc.HasExited) { Fail "ComfyUI exited during startup with code $($proc.ExitCode)." }
        try {
            $r = Invoke-WebRequest -Uri "$Api/object_info" -Method Get -TimeoutSec 10 -UseBasicParsing
            if ($r.StatusCode -eq 200) { $ready = $true; break }
        } catch {}
        Start-Sleep -Milliseconds 750
    }
    if (-not $ready) { Fail 'Timed out waiting for ComfyUI.' }

    Write-Host '[RUN] official preferred-resolution control; expect roughly the same runtime as V2...' -ForegroundColor Cyan
    & $Python $Helper `
        --api $Api `
        --comfy-root $ComfyRoot `
        --master $Master `
        --output-dir $OutDir `
        --seed $Seed `
        --timeout-seconds 2700
    $code = $LASTEXITCODE
    if ($code -ne 0) {
        Write-Host ''
        Write-Host '[COMFY STDERR TAIL]' -ForegroundColor DarkYellow
        if (Test-Path $Stderr) { Get-Content $Stderr -Tail 60 -ErrorAction SilentlyContinue | Out-Host }
        Fail "control helper exited with code $code"
    }
}
finally {
    if ($null -ne $proc -and -not $proc.HasExited) {
        Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
        try { $proc.WaitForExit(5000) | Out-Null } catch {}
    }
}

$Raw = Join-Path $OutDir 'g3s_a_control_official_raw.png'
$Result = Join-Path $OutDir 'g3s_a_control_result.json'
if (-not (Test-Path $Raw -PathType Leaf)) { Fail "Expected raw control output missing: $Raw" }
if (-not (Test-Path $Result -PathType Leaf)) { Fail "Expected control result missing: $Result" }

Write-Host ''
Write-Host 'G3S-A CONTROL: REVIEW CONTROL' -ForegroundColor Yellow
Write-Host "RAW:    $Raw"
Write-Host "RESULT: $Result"
Write-Host ''
Write-Host 'STOP. Do not resize this image and do not treat it as a sprite candidate.' -ForegroundColor Yellow
