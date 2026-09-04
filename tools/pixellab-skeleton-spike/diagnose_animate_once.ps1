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

function Write-Utf8NoBom([string]$Path, [string]$Text) {
    [System.IO.File]::WriteAllText($Path, $Text, [System.Text.UTF8Encoding]::new($false))
}

function Get-WebExceptionBody($Exception) {
    if ($null -eq $Exception.Response) { return ($Exception | Out-String) }
    try {
        $stream = $Exception.Response.GetResponseStream()
        if ($null -eq $stream) { return '' }
        $reader = New-Object System.IO.StreamReader($stream)
        try { return $reader.ReadToEnd() }
        finally { $reader.Dispose(); $stream.Dispose() }
    }
    catch {
        return ($Exception | Out-String)
    }
}

function Get-ResponseHeadersText($Response) {
    if ($null -eq $Response) { return '' }
    $lines = @()
    try {
        foreach ($key in $Response.Headers.AllKeys) {
            $lines += "$key`: $($Response.Headers[$key])"
        }
    } catch {}
    return ($lines -join [Environment]::NewLine)
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

# Reuse ONLY artifacts from the previous spike. No estimator, pose regeneration, retry, or fallback schema.
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
Write-Utf8NoBom $requestPath $json

Write-Host ''
Write-Host 'PixelLab single-call diagnostic' -ForegroundColor Cyan
Write-Host "  endpoint:   $Endpoint"
Write-Host "  workspace:  $Workspace"
Write-Host "  reference:  $Reference"
Write-Host "  palette:    $Palette"
Write-Host '  poses:      target_pose_0.json .. target_pose_3.json'
Write-Host '  API calls:  EXACTLY ONE POST; no balance query, no estimator, no retry'
Write-Host "  request:    $requestPath"
Write-Host ''

$headers = @{
    Authorization = "Bearer $env:PIXELLAB_SECRET"
    Accept = 'application/json'
}

$statusLine = $null
$body = ''
$responseHeaders = ''
$statusCode = $null
$success = $false

try {
    # IMPORTANT: this is the only network/API call in the script.
    $response = Invoke-WebRequest `
        -UseBasicParsing `
        -Uri $Endpoint `
        -Method Post `
        -Headers $headers `
        -ContentType 'application/json' `
        -Body $json `
        -TimeoutSec 600

    $statusCode = [int]$response.StatusCode
    $statusLine = "HTTP $statusCode $($response.StatusDescription)"
    $body = [string]$response.Content
    $responseHeaders = Get-ResponseHeadersText $response
    $success = ($statusCode -ge 200 -and $statusCode -lt 300)
}
catch [System.Net.WebException] {
    $webEx = $_.Exception
    if ($null -ne $webEx.Response) {
        try { $statusCode = [int]$webEx.Response.StatusCode } catch { $statusCode = 0 }
        try { $reason = [string]$webEx.Response.StatusDescription } catch { $reason = '' }
        $statusLine = "HTTP $statusCode $reason".Trim()
        $body = Get-WebExceptionBody $webEx
        $responseHeaders = Get-ResponseHeadersText $webEx.Response
    }
    else {
        $statusCode = 0
        $statusLine = 'NO HTTP RESPONSE'
        $body = ($webEx | Out-String)
    }
}
catch {
    $statusCode = 0
    $statusLine = 'NO HTTP RESPONSE'
    $body = ($_ | Out-String)
}

Write-Utf8NoBom $statusPath ($statusLine + [Environment]::NewLine)
Write-Utf8NoBom $bodyPath $body
Write-Utf8NoBom $headersPath $responseHeaders

Write-Host $statusLine -ForegroundColor Yellow
Write-Host "Full response body saved to: $bodyPath"
Write-Host "Response headers saved to:   $headersPath"

$tierDenied = $body -match '(?i)tier\s*1|requires?\s+(at\s+least\s+)?tier|subscription.*required|upgrade.*tier|plan.*required'
if ($tierDenied) {
    Write-Host ''
    Write-Host 'Tier/subscription restriction detected. STOPPING. No workaround or second call will be attempted.' -ForegroundColor Red
    exit 3
}

if ($success) {
    Write-Host ''
    Write-Host 'The one POST was accepted. Diagnostic ends here; no estimator/QA follow-up is being run.' -ForegroundColor Green
    exit 0
}

Write-Host ''
Write-Host 'The one POST failed for a reason other than an obvious Tier-1 restriction. Diagnostic ends here with no retry.' -ForegroundColor Red
exit 1
