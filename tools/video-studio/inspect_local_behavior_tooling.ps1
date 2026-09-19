param(
    [string]$AiRoot = 'Z:\AI',
    [string]$BehaviorRoot = 'Z:\AI\VideoStudio\profiles\joao\behavior\avatar_v'
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version 2.0

$ReportDir = Join-Path $PSScriptRoot 'reports'
New-Item -ItemType Directory -Force -Path $ReportDir | Out-Null
$Stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$TxtReport = Join-Path $ReportDir ("local_behavior_tooling_$Stamp.txt")
$JsonReport = Join-Path $ReportDir ("local_behavior_tooling_$Stamp.json")

$Lines = New-Object System.Collections.Generic.List[string]
function Out-Line([string]$Text = '') {
    $Lines.Add($Text)
    Write-Host $Text
}

function Add-UniquePath {
    param(
        [System.Collections.Generic.List[string]]$List,
        [string]$Path
    )
    if ([string]::IsNullOrWhiteSpace($Path)) { return }
    if (-not (Test-Path -LiteralPath $Path)) { return }
    $resolved = (Resolve-Path -LiteralPath $Path).Path
    if (-not $List.Contains($resolved)) { $List.Add($resolved) }
}

function Get-PythonIdentity {
    param(
        [string]$Executable,
        [string[]]$PrefixArgs = @()
    )
    try {
        $args = @()
        $args += $PrefixArgs
        $args += @('-c', 'import json,sys,importlib.util; print(json.dumps({"exe":sys.executable,"version":sys.version.split()[0],"major":sys.version_info.major,"minor":sys.version_info.minor,"packages":{n:(importlib.util.find_spec(n) is not None) for n in ["numpy","cv2","onnxruntime","torch","mediapipe","controlnet_aux"]}}))')
        $raw = & $Executable @args 2>$null
        if ($LASTEXITCODE -ne 0 -or -not $raw) { return $null }
        return (($raw | Select-Object -Last 1) | ConvertFrom-Json)
    } catch {
        return $null
    }
}

function Find-Limited {
    param(
        [string]$Root,
        [string[]]$FilePatterns,
        [string[]]$DirectoryNames,
        [int]$MaxDepth = 5,
        [int]$MaxHits = 50
    )
    $hits = New-Object System.Collections.Generic.List[object]
    if (-not (Test-Path -LiteralPath $Root -PathType Container)) { return @() }

    $queue = New-Object System.Collections.Queue
    $queue.Enqueue([pscustomobject]@{ Path = (Resolve-Path -LiteralPath $Root).Path; Depth = 0 })

    while ($queue.Count -gt 0 -and $hits.Count -lt $MaxHits) {
        $node = $queue.Dequeue()
        try {
            $dirs = @(Get-ChildItem -LiteralPath $node.Path -Directory -Force -ErrorAction SilentlyContinue)
            $files = @(Get-ChildItem -LiteralPath $node.Path -File -Force -ErrorAction SilentlyContinue)
        } catch {
            continue
        }

        foreach ($d in $dirs) {
            foreach ($name in $DirectoryNames) {
                if ($d.Name -ieq $name) {
                    $hits.Add([pscustomobject]@{ kind='directory'; path=$d.FullName; matched=$name })
                    break
                }
            }
            if ($hits.Count -ge $MaxHits) { break }
        }
        if ($hits.Count -ge $MaxHits) { break }

        foreach ($f in $files) {
            foreach ($pattern in $FilePatterns) {
                if ($f.Name -like $pattern) {
                    $hits.Add([pscustomobject]@{ kind='file'; path=$f.FullName; matched=$pattern; bytes=[int64]$f.Length })
                    break
                }
            }
            if ($hits.Count -ge $MaxHits) { break }
        }

        if ($node.Depth -lt $MaxDepth) {
            foreach ($d in $dirs) {
                if ($d.Name -in @('.git','node_modules','outputs','output','runs','cache','__pycache__')) { continue }
                $queue.Enqueue([pscustomobject]@{ Path=$d.FullName; Depth=($node.Depth + 1) })
            }
        }
    }
    return @($hits)
}

Out-Line 'LOCAL BEHAVIOR TOOLING INSPECTION'
Out-Line '================================='
Out-Line ('Timestamp: ' + (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'))
Out-Line 'Mode: READ ONLY / NO DOWNLOAD / NO INSTALL / NO DELETE'
Out-Line ('AI root: ' + $AiRoot)
Out-Line ''

# Python resolution: never trust the requested launcher label without checking
# sys.version_info from the resolved interpreter.
Out-Line 'PYTHON RESOLUTION'
Out-Line '================='
$PythonCandidates = New-Object System.Collections.Generic.List[object]
$pyCmd = Get-Command py.exe -ErrorAction SilentlyContinue
if ($null -eq $pyCmd) { $pyCmd = Get-Command py -ErrorAction SilentlyContinue }

if ($pyCmd) {
    Out-Line ('py launcher: ' + $pyCmd.Source)
    try {
        $launcherList = & $pyCmd.Source -0p 2>$null
        Out-Line 'py -0p:'
        foreach ($line in @($launcherList)) { Out-Line ('  ' + [string]$line) }
    } catch {
        Out-Line ('py -0p failed: ' + $_.Exception.Message)
    }

    $id311 = Get-PythonIdentity -Executable $pyCmd.Source -PrefixArgs @('-3.11')
    if ($id311) {
        $exact311 = ([int]$id311.major -eq 3 -and [int]$id311.minor -eq 11)
        $PythonCandidates.Add([pscustomobject]@{
            source='py -3.11'; executable=[string]$id311.exe; version=[string]$id311.version;
            exact311=$exact311; packages=$id311.packages
        })
        if ($exact311) {
            Out-Line ("py -3.11: PASS / {0} / {1}" -f $id311.exe, $id311.version)
        } else {
            Out-Line ("py -3.11: MISMATCH / requested 3.11 but resolved {0} / {1}" -f $id311.exe, $id311.version)
        }
    } else {
        Out-Line 'py -3.11: NOT RESOLVED'
    }
} else {
    Out-Line 'py launcher: MISSING'
}

$KnownPythonPaths = @(
    'C:\Python311\python.exe',
    'C:\Program Files\Python311\python.exe',
    (Join-Path $env:LOCALAPPDATA 'Programs\Python\Python311\python.exe'),
    (Join-Path $env:USERPROFILE 'AppData\Local\Programs\Python\Python311\python.exe')
)

foreach ($p in $KnownPythonPaths) {
    if (-not (Test-Path -LiteralPath $p -PathType Leaf)) { continue }
    $id = Get-PythonIdentity -Executable $p
    if (-not $id) { continue }
    $exact311 = ([int]$id.major -eq 3 -and [int]$id.minor -eq 11)
    $PythonCandidates.Add([pscustomobject]@{
        source='known path'; executable=[string]$id.exe; version=[string]$id.version;
        exact311=$exact311; packages=$id.packages
    })
    Out-Line ("candidate: {0} / {1} / exact311={2}" -f $id.exe, $id.version, $exact311)
}

# Target only likely local AI runtimes; do not crawl all Z:\ recursively.
$LikelyRoots = New-Object System.Collections.Generic.List[string]
foreach ($p in @(
    (Join-Path $AiRoot 'WanAnimate2'),
    (Join-Path $AiRoot 'WanGP'),
    (Join-Path $AiRoot 'MiniMaxH3'),
    (Join-Path $AiRoot 'ComfyUI'),
    (Join-Path $AiRoot 'ComfyUI_windows_portable'),
    (Join-Path $AiRoot 'VideoStudio')
)) {
    Add-UniquePath -List $LikelyRoots -Path $p
}

if (Test-Path -LiteralPath $AiRoot -PathType Container) {
    foreach ($d in @(Get-ChildItem -LiteralPath $AiRoot -Directory -ErrorAction SilentlyContinue)) {
        if ($d.Name -match '(?i)(wan|comfy|pose|control|video|minimax|h3|annotator|aux|python)') {
            Add-UniquePath -List $LikelyRoots -Path $d.FullName
        }
    }
}

$PythonPathHits = New-Object System.Collections.Generic.List[string]
foreach ($root in $LikelyRoots) {
    $hits = Find-Limited -Root $root -FilePatterns @('python.exe') -DirectoryNames @() -MaxDepth 3 -MaxHits 20
    foreach ($hit in $hits) {
        if ($hit.kind -eq 'file' -and -not $PythonPathHits.Contains([string]$hit.path)) {
            $PythonPathHits.Add([string]$hit.path)
        }
    }
}

foreach ($p in $PythonPathHits) {
    $id = Get-PythonIdentity -Executable $p
    if (-not $id) { continue }
    $exact311 = ([int]$id.major -eq 3 -and [int]$id.minor -eq 11)
    $already = @($PythonCandidates | Where-Object { $_.executable -ieq [string]$id.exe }).Count -gt 0
    if (-not $already) {
        $PythonCandidates.Add([pscustomobject]@{
            source='AI runtime'; executable=[string]$id.exe; version=[string]$id.version;
            exact311=$exact311; packages=$id.packages
        })
        Out-Line ("AI python: {0} / {1} / exact311={2}" -f $id.exe, $id.version, $exact311)
    }
}

$Exact311 = @($PythonCandidates | Where-Object { $_.exact311 })
$SelectedPython = $null
if ($Exact311.Count -gt 0) {
    $withOnnx = @($Exact311 | Where-Object { $_.packages.onnxruntime -eq $true })
    $SelectedPython = if ($withOnnx.Count -gt 0) { $withOnnx[0] } else { $Exact311[0] }
    Out-Line ("SELECTED PYTHON CANDIDATE: {0} / {1}" -f $SelectedPython.executable, $SelectedPython.version)
} else {
    Out-Line 'SELECTED PYTHON CANDIDATE: NONE (no interpreter verified as exactly Python 3.11)'
}
Out-Line ''

# Pose tooling search: targeted existing roots only, with bounded depth.
Out-Line 'POSE TOOLING SEARCH'
Out-Line '==================='
$PosePatterns = @(
    'dw-ll_ucoco_384.onnx',
    'dw-ll_ucoco_384_bs5.torchscript.pt',
    'dwpose*.onnx',
    'yolox*.onnx',
    'yolox*.torchscript.pt',
    'pose_landmarker*.task',
    'hand_landmarker*.task',
    'body_pose_model.pth',
    'hand_pose_model.pth'
)
$PoseDirNames = @(
    'comfyui_controlnet_aux',
    'ComfyUI-ControlNet-Aux',
    'DWPose',
    'dwpose',
    'annotator'
)

$PoseHits = New-Object System.Collections.Generic.List[object]
foreach ($root in $LikelyRoots) {
    Out-Line ('scan root: ' + $root)
    $hits = Find-Limited -Root $root -FilePatterns $PosePatterns -DirectoryNames $PoseDirNames -MaxDepth 6 -MaxHits 50
    foreach ($hit in $hits) {
        $exists = @($PoseHits | Where-Object { $_.path -ieq $hit.path }).Count -gt 0
        if (-not $exists) {
            $PoseHits.Add($hit)
            if ($hit.kind -eq 'file') {
                Out-Line ("  FILE {0} ({1:N1} MB) pattern={2}" -f $hit.path, ([int64]$hit.bytes / 1MB), $hit.matched)
            } else {
                Out-Line ("  DIR  {0} name={1}" -f $hit.path, $hit.matched)
            }
        }
    }
}

if ($PoseHits.Count -eq 0) {
    Out-Line 'POSE TOOLING RESULT: NONE FOUND IN TARGETED LOCAL ROOTS'
} else {
    Out-Line ('POSE TOOLING RESULT: REUSE CANDIDATES FOUND = ' + $PoseHits.Count)
}
Out-Line ''

# Canonical source check, because the next extractor is intentionally primary-source only.
$PrimarySource = Join-Path $BehaviorRoot 'sources\VID_20260911_140124885.mp4'
Out-Line 'PRIMARY SOURCE'
Out-Line '=============='
if (Test-Path -LiteralPath $PrimarySource -PathType Leaf) {
    $f = Get-Item -LiteralPath $PrimarySource
    Out-Line ("PASS {0} ({1:N2} GB)" -f $f.FullName, ($f.Length / 1GB))
} else {
    Out-Line ('FAIL missing: ' + $PrimarySource)
}
Out-Line ''

$Result = [ordered]@{
    timestamp = (Get-Date).ToString('o')
    mode = 'read-only'
    ai_root = $AiRoot
    python_candidates = @($PythonCandidates)
    selected_python_candidate = $SelectedPython
    likely_roots = @($LikelyRoots)
    pose_hits = @($PoseHits)
    primary_source = $PrimarySource
}

$Result | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $JsonReport -Encoding UTF8
Set-Content -LiteralPath $TxtReport -Value $Lines -Encoding UTF8

Out-Line ('Text report: ' + $TxtReport)
Out-Line ('JSON report: ' + $JsonReport)
