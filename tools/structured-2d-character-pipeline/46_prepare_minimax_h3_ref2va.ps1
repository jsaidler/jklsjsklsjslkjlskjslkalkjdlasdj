param(
    [string]$ProjectRepoRoot = 'D:\GOOGLE DRIVE\DEV\Roguelite',
    [string]$Workspace = 'Z:\AI\MiniMaxH3',
    [string]$WanWorkspace = 'Z:\AI\WanAnimate2',
    [int]$Port = 8190,
    [int]$MinFreeGB = 48
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$ComfyVersion = 'v0.34.0'
$ComfyArchiveName = 'ComfyUI_windows_portable_nvidia.7z'
$ComfyArchiveUrl = 'https://github.com/Comfy-Org/ComfyUI/releases/download/v0.34.0/ComfyUI_windows_portable_nvidia.7z'
$ComfyArchiveSha256 = 'ed57cc6b19ae3d83add1ecebfdd56b25e04e0008cf0fe9af43a4ad8797e2a24c'
$WorkflowTemplateCommit = '7c25a3c586484601f94b7e8f8b14c23b2c95a096'
$WorkflowTemplateUrl = "https://raw.githubusercontent.com/Comfy-Org/workflow_templates/$WorkflowTemplateCommit/templates/video_minimax_h3_r2v.json"

$ModelSpecs = @(
    [pscustomobject]@{
        RelativePath = 'models\diffusion_models\minimax_h3_ref2va_pruned_int8_convrot.safetensors'
        Url = 'https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/main/diffusion_models/minimax_h3_ref2va_pruned_int8_convrot.safetensors'
        Sha256 = '9255f52b6677845ad238f20dfaafa94727053694127ab7f255c048f0f9365779'
        ApproxGB = 21.0
    },
    [pscustomobject]@{
        RelativePath = 'models\text_encoders\qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors'
        Url = 'https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/main/text_encoders/qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors'
        Sha256 = '35a88d51044231fe332301d7a62aa81e3f2cba62febeb446e2c1e3e0ef76f2c6'
        ApproxGB = 15.7
    },
    [pscustomobject]@{
        RelativePath = 'models\vae\minimax_h3_video_vae_fp16.safetensors'
        Url = 'https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/main/vae/minimax_h3_video_vae_fp16.safetensors'
        Sha256 = '7c1f131492e7eddacaac9069a61b81bdd39de5cc96561e677c5eab1cdce5e522'
        ApproxGB = 5.21
    },
    [pscustomobject]@{
        RelativePath = 'models\vae\minimax_h3_audio_vae_fp32.safetensors'
        Url = 'https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/main/vae/minimax_h3_audio_vae_fp32.safetensors'
        Sha256 = '8e505d95dd1561d47abd43d4238fd40d9bb1ae9e147ed0a4cba778d76ae4db48'
        ApproxGB = 0.605
    }
)

function Fail([string]$Message) {
    Write-Host "RUNNER46-H3-PREP: FAIL - $Message" -ForegroundColor Red
    exit 1
}

function Get-Sha256([string]$Path) {
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Download-Verified([string]$Url, [string]$Destination, [string]$ExpectedSha) {
    $parent = Split-Path -Parent $Destination
    New-Item -ItemType Directory -Force -Path $parent | Out-Null

    if (Test-Path $Destination -PathType Leaf) {
        Write-Host "Hash-checking existing: $Destination" -ForegroundColor DarkCyan
        $existingHash = Get-Sha256 $Destination
        if ($existingHash -eq $ExpectedSha.ToLowerInvariant()) {
            Write-Host '  already present and verified.' -ForegroundColor Green
            return
        }
        Write-Host '  existing file hash is wrong; deleting it rather than accumulating a bad checkpoint.' -ForegroundColor Yellow
        Remove-Item -LiteralPath $Destination -Force
    }

    $partial = "$Destination.part"
    $curl = Get-Command curl.exe -ErrorAction SilentlyContinue
    if (-not $curl) { Fail 'curl.exe is required for resumable verified downloads.' }

    Write-Host "Downloading: $Url" -ForegroundColor Cyan
    $curlArgs = @('--fail','--location','--retry','5','--retry-delay','5','--retry-all-errors','--continue-at','-','--output',$partial,$Url)
    & $curl.Source @curlArgs
    if ($LASTEXITCODE -ne 0) { Fail "download failed with curl exit code $LASTEXITCODE : $Url" }

    Move-Item -LiteralPath $partial -Destination $Destination -Force
    Write-Host "Verifying SHA256: $Destination" -ForegroundColor DarkCyan
    $actual = Get-Sha256 $Destination
    if ($actual -ne $ExpectedSha.ToLowerInvariant()) {
        Remove-Item -LiteralPath $Destination -Force -ErrorAction SilentlyContinue
        Fail "SHA256 mismatch for $Destination. Expected $ExpectedSha, got $actual. Corrupt file was deleted."
    }
    Write-Host '  verified.' -ForegroundColor Green
}

function Download-SmallFile([string]$Url, [string]$Destination) {
    $parent = Split-Path -Parent $Destination
    New-Item -ItemType Directory -Force -Path $parent | Out-Null
    $curl = Get-Command curl.exe -ErrorAction SilentlyContinue
    if (-not $curl) { Fail 'curl.exe is required.' }
    & $curl.Source '--fail' '--location' '--retry' '4' '--output' $Destination $Url
    if ($LASTEXITCODE -ne 0) { Fail "small-file download failed: $Url" }
}

function Find-Extractor {
    foreach ($candidate in @(
        (Get-Command 7z.exe -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source -ErrorAction SilentlyContinue),
        (Get-Command 7zz.exe -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source -ErrorAction SilentlyContinue),
        "$env:ProgramFiles\7-Zip\7z.exe",
        "${env:ProgramFiles(x86)}\7-Zip\7z.exe"
    ) | Where-Object { $_ }) {
        if (Test-Path $candidate -PathType Leaf) { return [pscustomobject]@{ Kind='7z'; Path=$candidate } }
    }
    $tar = Get-Command tar.exe -ErrorAction SilentlyContinue
    if ($tar) { return [pscustomobject]@{ Kind='tar'; Path=$tar.Source } }
    return $null
}

function Find-ComfyRoot([string]$Base) {
    foreach ($candidate in @($Base, (Join-Path $Base 'ComfyUI'), (Join-Path $Base 'ComfyUI_windows_portable\ComfyUI'))) {
        if (Test-Path (Join-Path $candidate 'main.py') -PathType Leaf) { return $candidate }
    }
    return $null
}

function Stop-ManagedProcess([string]$PidFile, [string]$Label) {
    if (-not (Test-Path $PidFile -PathType Leaf)) { return }
    $pidText = (Get-Content -LiteralPath $PidFile -Raw).Trim()
    $managedPid = 0
    if (-not [int]::TryParse($pidText, [ref]$managedPid) -or $managedPid -le 0) {
        Write-Host "[$Label] ignoring invalid PID file: $PidFile" -ForegroundColor Yellow
        Remove-Item -LiteralPath $PidFile -Force -ErrorAction SilentlyContinue
        return
    }
    $p = Get-Process -Id $managedPid -ErrorAction SilentlyContinue
    if ($p) {
        Write-Host "[$Label] stopping managed PID $managedPid to free RAM/VRAM." -ForegroundColor Yellow
        Stop-Process -Id $managedPid -Force
        Start-Sleep -Seconds 2
    }
    Remove-Item -LiteralPath $PidFile -Force -ErrorAction SilentlyContinue
}

Write-Host ''
Write-Host 'Roguelite Runner 46 - MiniMax H3 Base Ref2VA / bootstrap + exact H0 preflight' -ForegroundColor Cyan
Write-Host "[WORKSPACE] $Workspace" -ForegroundColor Green
Write-Host '[MODEL] MiniMax H3 Base Ref2VA, pruned INT8 ConvRot diffusion model.' -ForegroundColor Green
Write-Host '[COMFY] pinned stable v0.34.0 NVIDIA portable / CUDA 13.0 route.' -ForegroundColor Green
Write-Host '[H0] 448x800, 124 frames, 24 fps, ref_image_size=match, Base 50-step, res_multistep + beta, seed0.' -ForegroundColor Green
Write-Host '[DOWNLOAD POLICY] Ref2VA only. Includes schema-required audio VAE; no FL2VA, no Turbo LoRA, no style embeddings.' -ForegroundColor Yellow
Write-Host '[AUDIO] H0 uses no audio reference/decode, but pinned MiniMaxH3ReferenceToVideo requires audio_vae as an input.' -ForegroundColor Yellow
Write-Host '[WAN] W1L evidence must exist before the transition. Wan inference server is stopped only if its managed PID is known.' -ForegroundColor Yellow
Write-Host ''

$ReferenceSource = Join-Path $ProjectRepoRoot 'assets\source\characters\exilada\reference\exilada_master.png'
$DriverNormalizer = Join-Path $ProjectRepoRoot 'tools\minimax-h3-spike\prepare_h0_driver.py'
$H0Executor = Join-Path $ProjectRepoRoot 'tools\minimax-h3-spike\run_h0_ref2va_audio_vae_required.py'
foreach ($f in @($ReferenceSource,$DriverNormalizer,$H0Executor)) {
    if (-not (Test-Path $f -PathType Leaf)) { Fail "required repository file missing: $f" }
}

$W1LVideo = Join-Path $WanWorkspace 'w1l_exilada_aspectmatched_ref10_pose80_steps30.mp4'
$W1LManifestPath = Join-Path $WanWorkspace 'w1l_run_manifest.json'
$W1LPrompt = Join-Path $WanWorkspace 'w1l_api_prompt.json'
foreach ($f in @($W1LVideo,$W1LManifestPath,$W1LPrompt)) {
    if (-not (Test-Path $f -PathType Leaf)) {
        Fail "W1L was reported complete but required evidence is missing: $f. Preserve/resolve W1L evidence before H3 bootstrap."
    }
}
$W1LManifest = Get-Content -LiteralPath $W1LManifestPath -Raw | ConvertFrom-Json
if ([string]$W1LManifest.status -ne 'INFERENCE_COMPLETE') {
    Fail "W1L manifest status is '$($W1LManifest.status)', not INFERENCE_COMPLETE."
}
Write-Host "[W1L] completion verified locally. prompt_id=$($W1LManifest.prompt_id)" -ForegroundColor Green

New-Item -ItemType Directory -Force -Path $Workspace | Out-Null
$driveRoot = [System.IO.Path]::GetPathRoot($Workspace)
if ($driveRoot -and $driveRoot.Length -ge 1) {
    $driveName = $driveRoot.Substring(0,1)
    $psDrive = Get-PSDrive -Name $driveName -ErrorAction SilentlyContinue
    if ($psDrive) {
        $freeGB = [math]::Round($psDrive.Free / 1GB, 2)
        Write-Host "[DISK] free on $driveName`: $freeGB GB" -ForegroundColor Cyan
        $portableExpected = Join-Path $Workspace 'ComfyUI_windows_portable\ComfyUI\main.py'
        if (-not (Test-Path $portableExpected -PathType Leaf) -and $freeGB -lt $MinFreeGB) {
            Fail "first H3 bootstrap requires at least about $MinFreeGB GB free. Current free space is $freeGB GB. Do not accumulate partial model families."
        }
    }
}

$systemRamGB = $null
try { $systemRamGB = [math]::Round((Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1GB, 1) } catch {}
if ($systemRamGB) { Write-Host "[RAM] detected physical RAM: $systemRamGB GB" -ForegroundColor Cyan }
try {
    $pagefiles = @(Get-CimInstance Win32_PageFileUsage -ErrorAction Stop)
    if ($pagefiles.Count -eq 0) {
        Write-Host '[PAGEFILE WARNING] No active pagefile reported. H3 + DynamicVRAM can exceed physical RAM; keep a Windows pagefile enabled.' -ForegroundColor Yellow
    } else {
        $pagefileMB = ($pagefiles | Measure-Object -Property AllocatedBaseSize -Sum).Sum
        Write-Host "[PAGEFILE] active allocation: $pagefileMB MB" -ForegroundColor Cyan
    }
} catch {
    Write-Host '[PAGEFILE] could not query pagefile state; bootstrap continues.' -ForegroundColor DarkYellow
}

Stop-ManagedProcess (Join-Path $WanWorkspace '.wan_animate2_spike.pid') 'WAN'

$Archive = Join-Path $Workspace $ComfyArchiveName
$PortableRoot = Join-Path $Workspace 'ComfyUI_windows_portable'
$ComfyRoot = Join-Path $PortableRoot 'ComfyUI'
$Python = Join-Path $PortableRoot 'python_embeded\python.exe'
$InstallManifestPath = Join-Path $Workspace 'h3_comfy_install_manifest.json'

if (-not (Test-Path (Join-Path $ComfyRoot 'main.py') -PathType Leaf) -or -not (Test-Path $Python -PathType Leaf)) {
    Download-Verified $ComfyArchiveUrl $Archive $ComfyArchiveSha256
    $extractor = Find-Extractor
    if (-not $extractor) { Fail 'No 7z.exe/7zz.exe/tar.exe extractor is available for the official .7z portable archive.' }
    Write-Host "Extracting official ComfyUI $ComfyVersion portable with $($extractor.Path)..." -ForegroundColor Cyan
    if ($extractor.Kind -eq '7z') {
        & $extractor.Path 'x' '-y' "-o$Workspace" $Archive
    } else {
        & $extractor.Path '-xf' $Archive '-C' $Workspace
    }
    if ($LASTEXITCODE -ne 0) { Fail "portable extraction failed with exit code $LASTEXITCODE" }
    if (-not (Test-Path (Join-Path $ComfyRoot 'main.py') -PathType Leaf) -or -not (Test-Path $Python -PathType Leaf)) {
        Fail "archive extracted but expected portable layout is missing under $PortableRoot"
    }
    Remove-Item -LiteralPath $Archive -Force -ErrorAction SilentlyContinue
} else {
    Write-Host '[COMFY] pinned workspace already exists; keeping it.' -ForegroundColor Green
}

$installManifest = [ordered]@{
    status = 'INSTALLED'
    comfy_version = $ComfyVersion
    official_archive = $ComfyArchiveName
    official_archive_url = $ComfyArchiveUrl
    official_archive_sha256 = $ComfyArchiveSha256
    comfy_root = $ComfyRoot
    python = $Python
    policy = 'dedicated pinned H3 workspace; no custom nodes for H0'
}
$installManifest | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $InstallManifestPath -Encoding UTF8

foreach ($spec in $ModelSpecs) {
    $dest = Join-Path $ComfyRoot $spec.RelativePath
    Download-Verified $spec.Url $dest $spec.Sha256
}

$OfficialWorkflow = Join-Path $Workspace 'official_video_minimax_h3_r2v_pinned.json'
Download-SmallFile $WorkflowTemplateUrl $OfficialWorkflow
$workflowText = Get-Content -LiteralPath $OfficialWorkflow -Raw
foreach ($token in @('MiniMaxH3ReferenceToVideo','minimax_h3_ref2va_pruned_int8_convrot.safetensors','minimax_h3_audio_vae_fp32.safetensors','res_multistep')) {
    if ($workflowText -notmatch [regex]::Escape($token)) { Fail "pinned official R2V template does not contain expected token: $token" }
}

$InputSubdir = Join-Path $ComfyRoot 'input\roguelite_h3'
New-Item -ItemType Directory -Force -Path $InputSubdir | Out-Null
$ReferenceInput = Join-Path $InputSubdir 'exilada_master.png'
Copy-Item -LiteralPath $ReferenceSource -Destination $ReferenceInput -Force

$WanComfyRoot = Find-ComfyRoot $WanWorkspace
if (-not $WanComfyRoot) { Fail "could not resolve the paused Wan ComfyUI root under $WanWorkspace" }
$W1HManifestPath = Join-Path $WanWorkspace 'w1h_run_manifest.json'
if (-not (Test-Path $W1HManifestPath -PathType Leaf)) { Fail "W1H manifest missing: $W1HManifestPath" }
$W1HManifest = Get-Content -LiteralPath $W1HManifestPath -Raw | ConvertFrom-Json
$driverRel = [string]$W1HManifest.driver
if ([string]::IsNullOrWhiteSpace($driverRel)) { Fail 'W1H manifest does not identify its raw source driver.' }
$driverNativeRel = $driverRel.Replace('/','\')
$DriverSource = Join-Path (Join-Path $WanComfyRoot 'input') $driverNativeRel
if (-not (Test-Path $DriverSource -PathType Leaf)) { Fail "raw W1H source driver missing: $DriverSource" }

$DriverInput = Join-Path $InputSubdir 'h0_driver_24fps_124f.mp4'
$DriverManifest = Join-Path $Workspace 'h0_driver_manifest.json'
Write-Host '[DRIVER] normalizing the same raw Wan driver to H3 timing only: 24 fps / 124 frames / no crop / no resize.' -ForegroundColor Cyan
& $Python $DriverNormalizer --source $DriverSource --output $DriverInput --manifest $DriverManifest --fps 24 --frames 124
if ($LASTEXITCODE -ne 0) { Fail "H0 driver normalization exited with code $LASTEXITCODE" }
foreach ($f in @($ReferenceInput,$DriverInput,$DriverManifest)) {
    if (-not (Test-Path $f -PathType Leaf)) { Fail "prepared H3 input missing: $f" }
}

$Base = "http://127.0.0.1:$Port"
$PidFile = Join-Path $Workspace '.minimax_h3_spike.pid'
Stop-ManagedProcess $PidFile 'H3'
$UserDir = Join-Path $ComfyRoot 'user'
New-Item -ItemType Directory -Force -Path $UserDir | Out-Null
$StdoutLog = Join-Path $UserDir "comfyui_h3_${Port}_stdout.log"
$StderrLog = Join-Path $UserDir "comfyui_h3_${Port}_stderr.log"
$MainPy = Join-Path $ComfyRoot 'main.py'

try {
    $null = Invoke-RestMethod -Uri "$Base/system_stats" -TimeoutSec 2
    Fail "port $Port is already serving an unmanaged ComfyUI instance. Stop it or use another port; runner will not kill an unknown process."
} catch {
    if ($_.Exception.Message -like 'RUNNER46-H3-PREP:*') { throw }
}

$launchArgs = @('-s',$MainPy,'--windows-standalone-build','--listen','127.0.0.1','--port',"$Port",'--disable-auto-launch')
Write-Host '[COMFY] starting clean pinned H3 server with default DynamicVRAM behavior; no Wan-specific memory workaround is carried over.' -ForegroundColor Cyan
$process = Start-Process -FilePath $Python -ArgumentList $launchArgs -WorkingDirectory $ComfyRoot `
    -RedirectStandardOutput $StdoutLog -RedirectStandardError $StderrLog -WindowStyle Hidden -PassThru
Set-Content -LiteralPath $PidFile -Value $process.Id -Encoding ASCII

$ready = $false
for ($i=0; $i -lt 240; $i++) {
    try {
        $null = Invoke-RestMethod -Uri "$Base/system_stats" -TimeoutSec 2
        $ready = $true
        break
    } catch {
        if ($process.HasExited) {
            if (Test-Path $StderrLog) { Get-Content $StderrLog -Tail 160 }
            Fail "pinned ComfyUI exited during H3 bootstrap with code $($process.ExitCode)"
        }
        Start-Sleep -Seconds 1
    }
}
if (-not $ready) {
    if (Test-Path $StderrLog) { Get-Content $StderrLog -Tail 160 }
    Fail "ComfyUI did not become ready at $Base"
}

$RequiredNodes = @(
    'UNETLoader','CLIPLoader','VAELoader','LoadImage','LoadVideo','GetVideoComponents',
    'MiniMaxH3ReferenceToVideo','RandomNoise','KSamplerSelect','BasicScheduler','BasicGuider',
    'SamplerCustomAdvanced','VAEDecode','CreateVideo','SaveVideo'
)
$ObjectInfoSubset = [ordered]@{}
foreach ($nodeName in $RequiredNodes) {
    try {
        $info = Invoke-RestMethod -Uri "$Base/object_info/$nodeName" -TimeoutSec 60
    } catch {
        Fail "could not query required node '$nodeName': $($_.Exception.Message)"
    }
    $prop = $info.PSObject.Properties[$nodeName]
    if (-not $prop) { Fail "required H3/core node is unavailable in pinned ComfyUI: $nodeName" }
    $ObjectInfoSubset[$nodeName] = $prop.Value
}
$ObjectInfoPath = Join-Path $Workspace 'h3_required_object_info.json'
$ObjectInfoSubset | ConvertTo-Json -Depth 100 | Set-Content -LiteralPath $ObjectInfoPath -Encoding UTF8

$SystemStats = Invoke-RestMethod -Uri "$Base/system_stats" -TimeoutSec 30
$SystemStatsPath = Join-Path $Workspace 'h3_system_stats.json'
$SystemStats | ConvertTo-Json -Depth 30 | Set-Content -LiteralPath $SystemStatsPath -Encoding UTF8

Stop-ManagedProcess $PidFile 'H3-PREFLIGHT'

$ModelsManifest = @()
foreach ($spec in $ModelSpecs) {
    $dest = Join-Path $ComfyRoot $spec.RelativePath
    $ModelsManifest += [ordered]@{
        relative_path = $spec.RelativePath
        path = $dest
        approx_gb = $spec.ApproxGB
        sha256 = Get-Sha256 $dest
        source = $spec.Url
    }
}

$BootstrapManifestPath = Join-Path $Workspace 'h3_bootstrap_manifest.json'
$BootstrapManifest = [ordered]@{
    gate = 'MINIMAX_H3_REF2VA_H0_BOOTSTRAP'
    status = 'PREPARED'
    created_utc = [DateTime]::UtcNow.ToString('o')
    project_repo_root = $ProjectRepoRoot
    workspace = $Workspace
    hardware_target = 'Windows 11 / RTX 3060 12 GB / 48 GB RAM'
    comfy_version = $ComfyVersion
    comfy_archive_sha256 = $ComfyArchiveSha256
    comfy_root = $ComfyRoot
    port = $Port
    dynamic_vram_policy = 'ComfyUI default; no --disable-dynamic-vram and no inherited Wan --disable-pinned-memory for H0 baseline'
    w1l_transition = [ordered]@{
        status = 'OPERATOR_REPORTED_AND_MANIFEST_VERIFIED_COMPLETE'
        prompt_id = $W1LManifest.prompt_id
        manifest = $W1LManifestPath
        video = $W1LVideo
        visual_verdict = 'NOT_INGESTED_BY_RUNNER46'
        wan_state = 'PAUSED_AFTER_W1L'
    }
    model_family = 'MiniMax H3 Base Ref2VA'
    model_files = $ModelsManifest
    explicitly_not_downloaded = @('MiniMax H3 FL2VA diffusion weights','Ref2V Turbo LoRA','style embeddings','alternate Ref2VA quantizations')
    audio_policy = 'audio VAE is schema-required by MiniMaxH3ReferenceToVideo; H0 uses no audio reference and no audio decode/output'
    reference_image = 'roguelite_h3/exilada_master.png'
    reference_image_sha256 = Get-Sha256 $ReferenceInput
    raw_driver_source = $DriverSource
    normalized_driver = 'roguelite_h3/h0_driver_24fps_124f.mp4'
    normalized_driver_manifest = $DriverManifest
    official_r2v_template = $OfficialWorkflow
    official_r2v_template_commit = $WorkflowTemplateCommit
    required_object_info = $ObjectInfoPath
    system_stats = $SystemStatsPath
    h0 = [ordered]@{
        task = 'ref2va'
        width = 448
        height = 800
        frames = 124
        fps = 24
        ref_image_size = 'match'
        steps = 50
        sampler = 'res_multistep'
        scheduler = 'beta'
        seed = 0
        video_sigma_shift = 12
        audio_sigma_shift = 3
        turbo_lora = $false
    }
    next_runner = 'tools/structured-2d-character-pipeline/48_run_minimax_h3_ref2va_h0_audio_vae_fix.ps1'
}
$BootstrapManifest | ConvertTo-Json -Depth 30 | Set-Content -LiteralPath $BootstrapManifestPath -Encoding UTF8

Write-Host ''
Write-Host 'RUNNER46-H3-PREP: PASS - H3 REF2VA H0 BOOTSTRAP READY' -ForegroundColor Green
Write-Host "Comfy root:       $ComfyRoot" -ForegroundColor Cyan
Write-Host "Bootstrap:        $BootstrapManifestPath" -ForegroundColor Cyan
Write-Host "Driver manifest:  $DriverManifest" -ForegroundColor Cyan
Write-Host "Object info:      $ObjectInfoPath" -ForegroundColor Cyan
Write-Host 'Downloaded model payload: Ref2VA diffusion + NVFP4 Qwen3-VL encoder + video VAE + schema-required audio VAE (~42.5 GB).' -ForegroundColor Yellow
Write-Host 'NEXT: run Runner48. Do not download FL2VA/Turbo variants before H0 evidence exists.' -ForegroundColor Yellow
