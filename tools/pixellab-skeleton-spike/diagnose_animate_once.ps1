param(
    [string]$Workspace = 'D:\AI\PixelLabSkeletonSpike',
    [string]$Endpoint = 'https://api.pixellab.ai/v2/animate-with-skeleton',
    [int]$Size = 128,
    [int]$Seed = 20260904,
    [ValidateSet('side','low top-down','high top-down')][string]$View = 'side',
    [ValidateSet('south','south-east','east','north-east','north','north-west','west','south-west')][string]$Direction = 'south-east',
    [double]$ReferenceGuidanceScale = 1.1,
    [double]$PoseGuidanceScale = 3.0
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Get-Base64ImageObject([string]$Path) {
    if (-not (Test-Path $Path)) { throw "Required file missing: $Path" }
    $bytes = [System.IO.File]::ReadAllBytes($Path)
    return [ordered]@{
        type   = 'base64'
        base64 = [Convert]::ToBase64String($bytes)
        format = 'png'
    }
}

function Read-Keypoints([string]$Path) {
    if (-not (Test-Path $Path)) { throw "Required file missing: $Path" }
    $raw = Get-Content -Raw -Path $Path | ConvertFrom-Json
    if ($null -eq $raw) { throw "Empty keypoint file: $Path" }
    return @($raw)
}

$Reference = Join-Path $Workspace 'exilada_reference_128.png'
$Palette = Join-Path $Workspace 'palette.png'
$PoseFiles = 0..3 | ForEach-Object { Join-Path $Workspace "target_pose_$_.json" }

foreach ($path in @($Reference, $Palette) + $PoseFiles) {
    if (-not (Test-Path $path)) { throw "Required existing spike artifact missing: $path" }
}

if (-not $env:PIXELLAB_SECRET) {
    $secure = Read-Host 'PixelLab API token (input hidden)' -AsSecureString
    $ptr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
    try {
        $env:PIXELLAB_SECRET = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr)
    } finally {
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr)
    }
}
if (-not $env:PIXELLAB_SECRET) { throw 'PIXELLAB_SECRET is empty.' }

$frames = @()
foreach ($poseFile in $PoseFiles) {
    $frames += [ordered]@{ keypoints = @(Read-Keypoints $poseFile) }
}

# This payload intentionally reuses ONLY the artifacts already produced by the failed spike.
# No estimate-skeleton call, no pose regeneration, no retries, no fallback schema.
$payload = [ordered]@{
    image_size               = [ordered]@{ width = $Size; height = $Size }
    reference_image          = Get-Base64ImageObject $Reference
    view                     = $View
    direction                = $Direction
    isometric                = $false
    oblique_projection       = $false
    reference_guidance_scale = $ReferenceGuidanceScale
    pose_guidance_scale      = $PoseGuidanceScale
    color_image              = Get-Base64ImageObject $Palette
    skeleton_keypoints       = $frames
    seed                     = $Seed
}

$requestPath = Join-Path $Workspace 'diagnostic_animate_once_request.json'
$statusPath = Join-Path $Workspace 'diagnostic_animate_once_status.txt'
$bodyPath = Join-Path $Workspace 'diagnostic_animate_once_response_body.txt'
$headersPath = Join-Path $Workspace 'diagnostic_animate_once_response_headers.txt'

$json = $payload | ConvertTo-Json -Depth 30 -Compress
[System.IO.File]::WriteAllText($requestPath, $json, [System.Text.UTF8Encoding]::new($false))

Write-Host ''
Write-Host 'PixelLab single-call diagnostic' -ForegroundColor Cyan
Write-Host "  endpoint:   $Endpoint"
Write-Host "  workspace:  $Workspace"
Write-Host "  reference:  $Reference"
Write-Host "  palette:    $Palette"
Write-Host '  poses:      target_pose_0.json .. target_pose_3.json'
Write-Host '  API calls:   EXACTLY ONE POST; no balance query, no estimator, no retry'
Write-Host "  request:    $requestPath"
Write-Host ''

$client = [System.Net.Http.HttpClient]::new()
$client.Timeout = [TimeSpan]::FromMinutes(10)
$client.DefaultRequestHeaders.Authorization = [System.Net.Http.Headers.AuthenticationHeaderValue]::new('Bearer', $env:PIXELLAB_SECRET)
$client.DefaultRequestHeaders.Accept.ParseAdd('application/json')
$content = [System.Net.Http.StringContent]::new($json, [System.Text.Encoding]::UTF8, 'application/json')

try {
    # IMPORTANT: this is the only network/API call in the script. Do not wrap in retry logic.
    $response = $client.PostAsync($Endpoint, $content).GetAwaiter().GetResult()
    $body = $response.Content.ReadAsStringAsync().GetAwaiter().GetResult()
    $statusLine = "HTTP $([int]$response.StatusCode) $($response.ReasonPhrase)"

    [System.IO.File]::WriteAllText($statusPath, $statusLine + [Environment]::NewLine, [System.Text.UTF8Encoding]::new($false))
    [System.IO.File]::WriteAllText($bodyPath, $body, [System.Text.UTF8Encoding]::new($false))

    $headerLines = @()
    foreach ($h in $response.Headers) {
        $headerLines += "$($h.Key): $([string]::Join(', ', $h.Value))"
    }
    foreach ($h in $response.Content.Headers) {
        $headerLines += "$($h.Key): $([string]::Join(', ', $h.Value))"
    }
    [System.IO.File]::WriteAllLines($headersPath, $headerLines, [System.Text.UTF8Encoding]::new($false))

    Write-Host $statusLine -ForegroundColor Yellow
    Write-Host "Full response body saved to: $bodyPath"
    Write-Host "Response headers saved to:   $headersPath"

    $tierDenied = $body -match '(?i)tier\s*1|requires?\s+(at\s+least\s+)?tier|subscription.*required|upgrade.*tier|plan.*required'
    if ($tierDenied) {
        Write-Host ''
        Write-Host 'Tier/subscription restriction detected. STOPPING. No workaround or second call will be attempted.' -ForegroundColor Red
        exit 3
    }

    if ($response.IsSuccessStatusCode) {
        Write-Host ''
        Write-Host 'The one POST was accepted. Diagnostic ends here; no estimator/QA follow-up is being run.' -ForegroundColor Green
        exit 0
    }

    Write-Host ''
    Write-Host 'The one POST failed for a reason other than an obvious Tier-1 restriction. Diagnostic ends here with no retry.' -ForegroundColor Red
    exit 1
}
catch {
    $exceptionText = $_ | Out-String
    [System.IO.File]::WriteAllText($statusPath, "NO HTTP RESPONSE`r`n", [System.Text.UTF8Encoding]::new($false))
    [System.IO.File]::WriteAllText($bodyPath, $exceptionText, [System.Text.UTF8Encoding]::new($false))
    Write-Host 'The single POST attempt raised a transport/client exception. No retry will be attempted.' -ForegroundColor Red
    Write-Host "Exception saved to: $bodyPath"
    exit 1
}
finally {
    $content.Dispose()
    $client.Dispose()
}
