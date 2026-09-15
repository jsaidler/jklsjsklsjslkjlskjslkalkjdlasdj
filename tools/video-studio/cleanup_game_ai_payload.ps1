param(
    [switch]$Execute,
    [string]$AiRoot = "Z:\AI"
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version 2.0

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\.." )).Path
$ReportDir = Join-Path $RepoRoot "tools\video-studio\reports"
New-Item -ItemType Directory -Force -Path $ReportDir | Out-Null

$Stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$Report = Join-Path $ReportDir "game_ai_cleanup_$Stamp.txt"
$Lines = New-Object 'System.Collections.Generic.List[string]'

function Log([string]$Text = "") {
    Write-Host $Text
    $Lines.Add($Text) | Out-Null
}

function Section([string]$Title) {
    Log ""
    Log $Title
    Log ("=" * $Title.Length)
}

function Get-DirectoryBytes([string]$Path) {
    if (-not (Test-Path -LiteralPath $Path -PathType Container)) {
        return [int64]0
    }

    $sum = Get-ChildItem -LiteralPath $Path -Recurse -File -Force -ErrorAction SilentlyContinue |
        Measure-Object -Property Length -Sum

    if ($null -eq $sum.Sum) {
        return [int64]0
    }
    return [int64]$sum.Sum
}

function Format-Bytes([int64]$Bytes) {
    if ($Bytes -ge 1TB) { return ('{0:N2} TB' -f ($Bytes / 1TB)) }
    if ($Bytes -ge 1GB) { return ('{0:N2} GB' -f ($Bytes / 1GB)) }
    if ($Bytes -ge 1MB) { return ('{0:N2} MB' -f ($Bytes / 1MB)) }
    return ('{0:N0} B' -f $Bytes)
}

function Assert-SafeAiPath([string]$Path) {
    $FullAi = [System.IO.Path]::GetFullPath($AiRoot).TrimEnd('\')
    $Full = [System.IO.Path]::GetFullPath($Path).TrimEnd('\')

    if (-not $Full.StartsWith($FullAi + '\', [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing path outside AI root: $Path"
    }

    if ($Full -eq $FullAi) {
        throw "Refusing to delete AI root itself: $Path"
    }
}

Log "VIDEO-STUDIO-GAME-CLEANUP-01"
Log ("Status date: " + (Get-Date -Format "yyyy-MM-dd HH:mm:ss"))
Log "AI root: $AiRoot"
Log "Execute: $Execute"

$DeleteRoots = @(
    [ordered]@{
        path = (Join-Path $AiRoot "RogueliteAssetStudio")
        reason = "Game-only asset-studio runtime; active product is now Video Studio."
    },
    [ordered]@{
        path = (Join-Path $AiRoot "SpriteSheetDiffusionSpike")
        reason = "Game-only sprite-sheet diffusion spike."
    },
    [ordered]@{
        path = (Join-Path $AiRoot "RogueliteCharacterPipeline")
        reason = "Game-only character pipeline."
    },
    [ordered]@{
        path = (Join-Path $AiRoot "QwenImageEditSpike")
        reason = "Retired game-era Qwen image-edit spike; current reusable image runtime is Z:\AI\QwenImageEdit."
    },
    [ordered]@{
        path = (Join-Path $AiRoot "Flux2RefControlSpike")
        reason = "Retired game-era reference-control spike; current reusable look/reference runtimes are Flux2Klein / QwenImageEdit."
    }
)

$ProtectedRoots = @(
    [ordered]@{ path = (Join-Path $AiRoot "WanAnimate2"); reason = "ACTIVE video runtime; being reused for Wan2.2-S2V." },
    [ordered]@{ path = (Join-Path $AiRoot "MiniMaxH3"); reason = "Video baseline/evidence and current profile source assets." },
    [ordered]@{ path = (Join-Path $AiRoot "QwenImageEdit"); reason = "Reusable for high-quality identity/scene still preparation." },
    [ordered]@{ path = (Join-Path $AiRoot "Flux2Klein"); reason = "Reusable for high-quality identity/scene still preparation." },
    [ordered]@{ path = (Join-Path $AiRoot "FluxKontext"); reason = "General image/reference tool; not classified as game-only." },
    [ordered]@{ path = (Join-Path $AiRoot "VideoStudioRuns"); reason = "Current video project outputs/evidence." }
)

Section "PROTECTED VIDEO / REUSABLE ROOTS"
foreach ($Item in $ProtectedRoots) {
    $Exists = Test-Path -LiteralPath $Item.path
    Log ((if ($Exists) { "KEEP" } else { "ABSENT" }) + "  " + $Item.path)
    Log ("      " + $Item.reason)
}

Section "GAME-ONLY DELETE SET"
$Found = New-Object 'System.Collections.Generic.List[object]'
$TotalBytes = [int64]0

foreach ($Item in $DeleteRoots) {
    $Path = [string]$Item.path
    Assert-SafeAiPath $Path

    if (-not (Test-Path -LiteralPath $Path -PathType Container)) {
        Log "ABSENT  $Path"
        continue
    }

    $Info = Get-Item -LiteralPath $Path -Force
    if (($Info.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0) {
        throw "Refusing to delete reparse-point root automatically: $Path"
    }

    Log "Scanning size: $Path"
    $Bytes = Get-DirectoryBytes $Path
    $TotalBytes += $Bytes

    $Entry = [pscustomobject]@{
        path = $Path
        bytes = $Bytes
        reason = [string]$Item.reason
    }
    $Found.Add($Entry) | Out-Null

    Log ("DELETE  {0}  [{1}]" -f $Path, (Format-Bytes $Bytes))
    Log ("        " + $Item.reason)
}

Section "SUMMARY BEFORE DELETE"
Log ("Game-only roots found: {0}" -f $Found.Count)
Log ("Recoverable size: {0}" -f (Format-Bytes $TotalBytes))

if (-not $Execute) {
    Log ""
    Log "DRY RUN ONLY. Nothing deleted."
    Log "Run again with -Execute to remove exactly the roots listed above."
} else {
    Section "DELETE"
    foreach ($Entry in $Found) {
        Log ("Deleting: " + $Entry.path)
        Remove-Item -LiteralPath $Entry.path -Recurse -Force -ErrorAction Stop
        if (Test-Path -LiteralPath $Entry.path) {
            throw "Path still exists after deletion: $($Entry.path)"
        }
        Log ("DELETED: " + $Entry.path)
    }

    Section "RESULT"
    Log ("Deleted roots: {0}" -f $Found.Count)
    Log ("Recovered approximately: {0}" -f (Format-Bytes $TotalBytes))
}

$Manifest = [ordered]@{
    schema = "VIDEO-STUDIO-GAME-CLEANUP-01"
    created = (Get-Date).ToString("o")
    execute = [bool]$Execute
    ai_root = $AiRoot
    deleted_or_planned = @($Found | ForEach-Object {
        [ordered]@{
            path = $_.path
            bytes = $_.bytes
            reason = $_.reason
        }
    })
    protected = @($ProtectedRoots)
    total_bytes = $TotalBytes
}

$ManifestPath = Join-Path $ReportDir "game_ai_cleanup_$Stamp.json"
$Manifest | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $ManifestPath -Encoding UTF8
Set-Content -LiteralPath $Report -Value $Lines -Encoding UTF8

Log ""
Log "REPORT: $Report"
Log "MANIFEST: $ManifestPath"
