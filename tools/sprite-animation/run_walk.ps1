param(
    [Parameter(Mandatory=$true)][string]$Reference,
    [ValidateSet('quality','smoke')][string]$Profile = 'quality',
    [int]$Seed = 42
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Exe = Join-Path $Root 'bin\sd-cli.exe'
$Py = Join-Path $Root '.venv\Scripts\python.exe'
$Models = Join-Path $Root 'models'
$PoseDir = Join-Path $Root 'poses\walk'
$OutputDir = Join-Path $Root 'output'

if (-not (Test-Path $Reference)) { throw "Reference image not found: $Reference" }
if (-not (Test-Path $Exe)) { throw "sd-cli.exe not found. Run .\install.ps1 first." }
if (-not (Test-Path $Py)) { throw "Python environment not found. Run .\install.ps1 first." }

switch ($Profile) {
    'quality' {
        $Width = 512
        $Height = 768
        $Steps = 25
        $UseVaeTiling = $true
    }
    'smoke' {
        $Width = 384
        $Height = 576
        $Steps = 12
        $UseVaeTiling = $false
    }
}

# The motion module's native window is 24 frames. Use the same 8-frame walk cycle
# repeated three times, then keep the middle eight frames in post-processing.
& $Py (Join-Path $Root 'prepare_walk_poses.py') `
    --width $Width --height $Height --cycles 3 --output $PoseDir
if ($LASTEXITCODE -ne 0) { throw 'Pose generation failed.' }

New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
$Stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$Stem = "exilada_walk_${Profile}_${Stamp}"
$Video = Join-Path $OutputDir "$Stem.webp"
$Sheet = Join-Path $OutputDir "${Stem}_spritesheet.png"

$Args = @(
    '-M','vid_gen',
    '--diffusion-model', (Join-Path $Models 'ssd\denoising_unet.pth'),
    '--motion-module', (Join-Path $Models 'animate-anyone\motion_module.pth'),
    '--reference-net', (Join-Path $Models 'ssd\reference_unet.pth'),
    '--pose-guider', (Join-Path $Models 'animate-anyone\pose_guider.pth'),
    '--clip_vision', (Join-Path $Models 'image_encoder\pytorch_model.bin'),
    '--vae', (Join-Path $Models 'sd-vae-ft-mse\diffusion_pytorch_model.safetensors'),
    '--type','f16',
    '--offload-to-cpu',
    '--diffusion-fa',
    '-r', (Resolve-Path $Reference).Path,
    '--pose-dir', $PoseDir,
    '-W', "$Width",
    '-H', "$Height",
    '--steps', "$Steps",
    '--cfg-scale','3.5',
    '-s', "$Seed",
    '--fps','8',
    '-o', $Video
)
if ($UseVaeTiling) { $Args += '--vae-tiling' }

Write-Host "Generating 24-frame walk window ($Width x $Height, $Steps steps)..." -ForegroundColor Cyan
& $Exe @Args
if ($LASTEXITCODE -ne 0) { throw "sd-cli failed with exit code $LASTEXITCODE" }

if (-not (Test-Path $Video)) {
    $Candidate = Get-ChildItem $OutputDir -Filter "$Stem*.webp" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if ($Candidate) { $Video = $Candidate.FullName }
}
if (-not (Test-Path $Video)) { throw 'Generation completed but no animated WebP was found.' }

& $Py (Join-Path $Root 'build_spritesheet.py') $Video --output $Sheet --cycle 1 --frames-per-cycle 8
if ($LASTEXITCODE -ne 0) { throw 'Sprite-sheet extraction failed.' }

Write-Host ''
Write-Host 'Done.' -ForegroundColor Green
Write-Host "Animation:    $Video"
Write-Host "Sprite sheet: $Sheet"
Write-Host "Manifest:     $([IO.Path]::ChangeExtension($Sheet, '.json'))"
