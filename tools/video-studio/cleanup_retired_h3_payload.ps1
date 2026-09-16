param(
    [string]$H3Root = 'Z:\AI\MiniMaxH3',
    [switch]$Execute
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version 2.0

if (-not (Test-Path -LiteralPath $H3Root -PathType Container)) {
    throw "H3 root not found: $H3Root"
}

$ResolvedH3Root = (Resolve-Path -LiteralPath $H3Root).Path.TrimEnd('\')
$ExpectedRoot = 'Z:\AI\MiniMaxH3'
if ($ResolvedH3Root -ne $ExpectedRoot) {
    throw "Safety stop: resolved H3 root is '$ResolvedH3Root', expected '$ExpectedRoot'."
}

$Targets = @(
    'minimax_h3_ref2va_pruned_int8_convrot.safetensors',
    'qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors'
)

Write-Host ''
Write-Host 'RETIRED H3 PAYLOAD CLEANUP'
Write-Host '==========================='
Write-Host ('Root: ' + $ResolvedH3Root)
Write-Host ('Mode: ' + $(if ($Execute) { 'EXECUTE' } else { 'DRY RUN' }))
Write-Host ''

$Found = New-Object 'System.Collections.Generic.List[System.IO.FileInfo]'

foreach ($Name in $Targets) {
    $Matches = @(
        Get-ChildItem -LiteralPath $ResolvedH3Root -Recurse -File -ErrorAction Stop |
            Where-Object { $_.Name -eq $Name }
    )

    if ($Matches.Count -eq 0) {
        Write-Host ('ABSENT  ' + $Name)
        continue
    }

    foreach ($Item in $Matches) {
        if (-not $Item.FullName.StartsWith($ResolvedH3Root + '\', [System.StringComparison]::OrdinalIgnoreCase)) {
            throw ('Safety stop: target escaped H3 root: ' + $Item.FullName)
        }
        $Found.Add($Item) | Out-Null
        $SizeGb = [math]::Round($Item.Length / 1GB, 2)
        Write-Host ('FOUND   ' + $SizeGb + ' GB  ' + $Item.FullName)
    }
}

$TotalBytes = 0
foreach ($Item in $Found) {
    $TotalBytes += $Item.Length
}
$TotalGb = [math]::Round($TotalBytes / 1GB, 2)

Write-Host ''
Write-Host 'SUMMARY'
Write-Host '======='
Write-Host ('Files found: ' + $Found.Count)
Write-Host ('Recoverable: ' + $TotalGb + ' GB')

if (-not $Execute) {
    Write-Host ''
    Write-Host 'DRY RUN ONLY. Nothing deleted.'
    Write-Host 'Run again with -Execute to remove only the exact retired H3 weights listed above.'
    exit 0
}

if ($Found.Count -eq 0) {
    Write-Host ''
    Write-Host 'Nothing to delete.'
    exit 0
}

Write-Host ''
Write-Host 'DELETE'
Write-Host '======'
foreach ($Item in $Found) {
    Write-Host ('Deleting ' + $Item.FullName)
    Remove-Item -LiteralPath $Item.FullName -Force -ErrorAction Stop
    if (Test-Path -LiteralPath $Item.FullName -PathType Leaf) {
        throw ('Delete verification failed: ' + $Item.FullName)
    }
}

$Drive = Get-PSDrive -Name 'Z' -ErrorAction Stop
$FreeGb = [math]::Round($Drive.Free / 1GB, 2)

Write-Host ''
Write-Host 'RESULT'
Write-Host '======'
Write-Host ('Recovered approximately: ' + $TotalGb + ' GB')
Write-Host ('Free Z: ' + $FreeGb + ' GB')

if ($FreeGb -ge 35) {
    Write-Host 'HUNYUAN PAYLOAD GATE: PASS'
} else {
    Write-Host 'HUNYUAN PAYLOAD GATE: HOLD'
}
