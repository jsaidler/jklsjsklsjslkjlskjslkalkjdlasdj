param(
    [switch]$Execute,
    [switch]$Push
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version 2.0

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\.." )).Path
Push-Location $RepoRoot
try {
    $Top = (& git rev-parse --show-toplevel).Trim()
    if ($LASTEXITCODE -ne 0) {
        throw "Not inside a Git repository."
    }

    if ([System.IO.Path]::GetFullPath($Top).TrimEnd('\') -ne [System.IO.Path]::GetFullPath($RepoRoot).TrimEnd('\')) {
        throw "Unexpected repository root: $Top"
    }

    $Branch = (& git rev-parse --abbrev-ref HEAD).Trim()
    if ($LASTEXITCODE -ne 0) {
        throw "Unable to resolve current branch."
    }

    if ($Branch -ne "main") {
        throw "Repository cleanup is locked to branch main. Current branch: $Branch"
    }

    $TrackedChanges = @(& git status --porcelain --untracked-files=no)
    if ($LASTEXITCODE -ne 0) {
        throw "git status failed."
    }
    if ($TrackedChanges.Count -gt 0) {
        throw "Tracked local changes exist. Commit/stash them before repository cleanup."
    }

    $Tracked = @(& git ls-files)
    if ($LASTEXITCODE -ne 0) {
        throw "git ls-files failed."
    }

    function Test-KeepPath([string]$Path) {
        if ($Path -eq ".gitignore") { return $true }
        if ($Path -eq "README.md") { return $true }
        if ($Path -eq "docs/PROJECT_STATE.md") { return $true }
        if ($Path -like "docs/VIDEO_STUDIO*.md") { return $true }
        if ($Path -like "tools/video-studio/*") { return $true }
        return $false
    }

    $Keep = New-Object 'System.Collections.Generic.List[string]'
    $Remove = New-Object 'System.Collections.Generic.List[string]'

    foreach ($Path in $Tracked) {
        if (Test-KeepPath $Path) {
            $Keep.Add($Path) | Out-Null
        } else {
            $Remove.Add($Path) | Out-Null
        }
    }

    $RemoveBytes = [int64]0
    foreach ($Path in $Remove) {
        $Full = Join-Path $RepoRoot $Path
        if (Test-Path -LiteralPath $Full -PathType Leaf) {
            $RemoveBytes += (Get-Item -LiteralPath $Full).Length
        }
    }

    Write-Host "VIDEO-STUDIO-REPO-CLEANUP-01"
    Write-Host "============================"
    Write-Host ("Branch: " + $Branch)
    Write-Host ("Tracked files kept: " + $Keep.Count)
    Write-Host ("Tracked files removed from working tree: " + $Remove.Count)
    Write-Host ("Current checkout bytes removed: {0:N2} MB" -f ($RemoveBytes / 1MB))
    Write-Host ""
    Write-Host "KEEP POLICY"
    Write-Host "-----------"
    Write-Host ".gitignore"
    Write-Host "README.md"
    Write-Host "docs/PROJECT_STATE.md"
    Write-Host "docs/VIDEO_STUDIO*.md"
    Write-Host "tools/video-studio/**"
    Write-Host ""
    Write-Host "REMOVE SET"
    Write-Host "----------"
    foreach ($Path in $Remove) {
        Write-Host $Path
    }

    if (-not $Execute) {
        Write-Host ""
        Write-Host "DRY RUN ONLY. Nothing removed."
        Write-Host "Run with -Execute to git-rm the remove set. Add -Push to commit and push main."
        return
    }

    if ($Remove.Count -eq 0) {
        Write-Host ""
        Write-Host "Repository already matches Video Studio-only policy."
        return
    }

    Write-Host ""
    Write-Host "REMOVING GAME-ERA TRACKED FILES"
    Write-Host "-------------------------------"

    $BatchSize = 40
    for ($i = 0; $i -lt $Remove.Count; $i += $BatchSize) {
        $End = [Math]::Min($i + $BatchSize - 1, $Remove.Count - 1)
        $Batch = @()
        for ($j = $i; $j -le $End; $j++) {
            $Batch += $Remove[$j]
        }
        & git rm -f -- $Batch
        if ($LASTEXITCODE -ne 0) {
            throw "git rm failed for batch starting at index $i."
        }
    }

    $StatusAfterRm = @(& git status --short)
    if ($LASTEXITCODE -ne 0) {
        throw "git status failed after cleanup."
    }

    Write-Host ""
    Write-Host "STAGED CLEANUP SUMMARY"
    Write-Host "----------------------"
    $StatusAfterRm | ForEach-Object { Write-Host $_ }

    if (-not $Push) {
        Write-Host ""
        Write-Host "Files are staged for deletion but not committed/pushed."
        Write-Host "Re-run with -Execute -Push from a clean checkout if you want the script to publish the cleanup automatically."
        return
    }

    & git commit -m "Remove retired Roguelite working-tree content"
    if ($LASTEXITCODE -ne 0) {
        throw "git commit failed."
    }

    & git push origin main
    if ($LASTEXITCODE -ne 0) {
        throw "git push origin main failed."
    }

    Write-Host ""
    Write-Host "REPOSITORY CLEANUP COMPLETE"
    Write-Host "---------------------------"
    Write-Host "main now contains only the active Video Studio working tree."
    Write-Host "Old Roguelite material remains recoverable from Git history."
}
finally {
    Pop-Location
}
