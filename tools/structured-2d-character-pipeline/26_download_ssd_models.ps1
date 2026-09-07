param(
    [string]$ProjectRepoRoot = 'D:\GOOGLE DRIVE\DEV\Roguelite',
    [string]$SsdRoot = 'Z:\AI\SpriteSheetDiffusionSpike'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Fail([string]$Message) {
    Write-Host "SSD-MODELS: FAIL - $Message" -ForegroundColor Red
    exit 1
}

$EnvMarker = Join-Path $SsdRoot 'ssd_environment_bootstrap.json'
$DependencyMarker = Join-Path $SsdRoot 'ssd_dependencies_bootstrap.json'
$UpstreamRepo = Join-Path $SsdRoot 'repo'
$ModelTraining = Join-Path $UpstreamRepo 'ModelTraining'
$PretrainedRoot = Join-Path $ModelTraining 'pretrained_model'
$Manifest = Join-Path $ProjectRepoRoot 'tools\structured-2d-character-pipeline\ssd_model_manifest.json'
$Downloader = Join-Path $SsdRoot 'ssd_download_models.py'
$Result = Join-Path $SsdRoot 'ssd_models_bootstrap.json'

Write-Host ''
Write-Host 'Roguelite - Sprite Sheet Diffusion model bootstrap' -ForegroundColor Cyan
Write-Host '[SCOPE] Minimal model set required by ModelTraining/inference.py.' -ForegroundColor Green
Write-Host '[LOCK] Direct resumable HTTP downloads; no duplicate Hugging Face cache.' -ForegroundColor Green
Write-Host '[LOCK] Known large-file SHA256 values are verified before PASS.' -ForegroundColor Green
Write-Host '[LOCK] No inference/model loading in this gate.' -ForegroundColor Green
Write-Host '[LOCK] No wav2vec2, DWPose or FILM interpolation model in this gate.' -ForegroundColor Green
Write-Host ''

foreach ($required in @($EnvMarker, $DependencyMarker, $ModelTraining, $Manifest)) {
    if (-not (Test-Path -LiteralPath $required)) {
        Fail "required path missing: $required"
    }
}

try {
    $envState = Get-Content -LiteralPath $EnvMarker -Raw | ConvertFrom-Json
    $depState = Get-Content -LiteralPath $DependencyMarker -Raw | ConvertFrom-Json
} catch {
    Fail 'cannot parse environment/dependency PASS markers.'
}
if ($envState.status -ne 'PASS') { Fail 'environment marker is not PASS.' }
if ($depState.status -ne 'PASS') { Fail 'dependency marker is not PASS.' }
if ($depState.ssd_inference_import -ne 'PASS') { Fail 'dependency marker does not report SSD inference import PASS.' }

$CondaExe = [string]$envState.conda_exe
if (-not (Test-Path -LiteralPath $CondaExe -PathType Leaf)) {
    Fail "conda.exe from environment marker is missing: $CondaExe"
}
$CondaRoot = Split-Path -Parent (Split-Path -Parent $CondaExe)
$Python = Join-Path $CondaRoot 'envs\ssd\python.exe'
if (-not (Test-Path -LiteralPath $Python -PathType Leaf)) {
    Fail "ssd environment python.exe missing: $Python"
}

New-Item -ItemType Directory -Force -Path $PretrainedRoot | Out-Null
Write-Host "[OK] Python:          $Python" -ForegroundColor Green
Write-Host "[OK] ModelTraining:   $ModelTraining" -ForegroundColor Green
Write-Host "[OK] Destination:     $PretrainedRoot" -ForegroundColor Green
Write-Host "[OK] Manifest:        $Manifest" -ForegroundColor Green
Write-Host ''

$pythonSource = @'
import hashlib
import json
import os
import shutil
import sys
import time
from pathlib import Path

try:
    import requests
except Exception as exc:
    print(f"SSD-MODELS: FAIL - requests import failed: {exc}")
    sys.exit(2)

manifest_path = Path(os.environ["SSD_MODEL_MANIFEST"])
root = Path(os.environ["SSD_PRETRAINED_ROOT"])
result_path = Path(os.environ["SSD_MODEL_RESULT"])


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def valid_existing(path: Path, item: dict) -> tuple[bool, str | None]:
    if not path.is_file():
        return False, None
    min_bytes = int(item.get("expected_min_bytes") or 1)
    if path.stat().st_size < min_bytes:
        return False, None
    expected = item.get("expected_sha256")
    if expected:
        actual = sha256_file(path)
        return actual.lower() == expected.lower(), actual
    if path.suffix.lower() == ".json":
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return False, None
    return True, sha256_file(path)


def human_gb(n: int) -> str:
    return f"{n / 1_000_000_000:.2f} GB"


def download_one(session: requests.Session, item: dict) -> dict:
    dest = root / Path(item["destination"])
    dest.parent.mkdir(parents=True, exist_ok=True)
    ok, existing_hash = valid_existing(dest, item)
    if ok:
        print(f"[SKIP] {item['id']}: verified existing {dest}")
        return {
            "id": item["id"], "path": str(dest), "size": dest.stat().st_size,
            "sha256": existing_hash, "source": item["source"], "downloaded": False,
        }

    if dest.exists():
        print(f"[REPAIR] {item['id']}: removing invalid existing file before redownload")
        dest.unlink()

    part = Path(str(dest) + ".part")
    start = part.stat().st_size if part.exists() else 0
    headers = {"User-Agent": "Roguelite-SSD-Spike/1.0"}
    if start > 0:
        headers["Range"] = f"bytes={start}-"
        print(f"[RESUME] {item['id']}: {human_gb(start)} already present")
    else:
        print(f"[DOWNLOAD] {item['id']}")

    try:
        response = session.get(
            item["source"], headers=headers, stream=True, allow_redirects=True,
            timeout=(30, 300)
        )
    except Exception as exc:
        raise RuntimeError(f"network request failed for {item['id']}: {exc}") from exc

    if response.status_code == 416 and start > 0:
        # A fully downloaded .part can produce Range Not Satisfiable. Verify it directly.
        response.close()
        expected = item.get("expected_sha256")
        actual = sha256_file(part)
        if expected and actual.lower() == expected.lower():
            part.replace(dest)
        else:
            part.unlink(missing_ok=True)
            raise RuntimeError(f"resume state invalid for {item['id']}; partial file removed, rerun runner")
    else:
        if start > 0 and response.status_code == 206:
            mode = "ab"
            base = start
        elif response.status_code == 200:
            mode = "wb"
            base = 0
            start = 0
        else:
            body = ""
            try:
                body = response.text[:500]
            except Exception:
                pass
            response.close()
            raise RuntimeError(f"HTTP {response.status_code} for {item['id']}: {body}")

        remaining = int(response.headers.get("Content-Length") or 0)
        total = base + remaining if remaining else 0
        written = base
        next_report = written + 256 * 1024 * 1024
        with part.open(mode) as f:
            for chunk in response.iter_content(chunk_size=8 * 1024 * 1024):
                if not chunk:
                    continue
                f.write(chunk)
                written += len(chunk)
                if written >= next_report:
                    if total:
                        pct = written * 100.0 / total
                        print(f"  {item['id']}: {human_gb(written)} / {human_gb(total)} ({pct:.1f}%)")
                    else:
                        print(f"  {item['id']}: {human_gb(written)}")
                    next_report = written + 256 * 1024 * 1024
        response.close()
        part.replace(dest)

    min_bytes = int(item.get("expected_min_bytes") or 1)
    size = dest.stat().st_size
    if size < min_bytes:
        dest.unlink(missing_ok=True)
        raise RuntimeError(f"{item['id']} is too small after download: {size} bytes")

    actual_hash = sha256_file(dest)
    expected_hash = item.get("expected_sha256")
    if expected_hash and actual_hash.lower() != expected_hash.lower():
        dest.unlink(missing_ok=True)
        raise RuntimeError(
            f"SHA256 mismatch for {item['id']}: expected {expected_hash}, got {actual_hash}; file removed"
        )

    if dest.suffix.lower() == ".json":
        json.loads(dest.read_text(encoding="utf-8"))

    print(f"[OK] {item['id']}: {human_gb(size)} sha256={actual_hash}")
    return {
        "id": item["id"], "path": str(dest), "size": size,
        "sha256": actual_hash, "source": item["source"], "downloaded": True,
    }


try:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    root.mkdir(parents=True, exist_ok=True)

    # Estimate remaining space from manifest minima and already verified files/partials.
    remaining_min = 0
    for item in manifest["files"]:
        dest = root / Path(item["destination"])
        ok, _ = valid_existing(dest, item)
        if ok:
            continue
        min_bytes = int(item.get("expected_min_bytes") or 0)
        part = Path(str(dest) + ".part")
        partial = part.stat().st_size if part.exists() else 0
        remaining_min += max(0, min_bytes - partial)

    free = shutil.disk_usage(root).free
    required = int(remaining_min * 1.10 + 1_000_000_000)
    print(f"[SPACE] free={human_gb(free)} estimated-minimum-needed={human_gb(required)}")
    if free < required:
        raise RuntimeError(
            f"insufficient free space: {human_gb(free)} free, at least {human_gb(required)} required for remaining files"
        )

    session = requests.Session()
    records = []
    for item in manifest["files"]:
        records.append(download_one(session, item))

    total = sum(r["size"] for r in records)
    result = {
        "gate": "SSD_MODEL_BOOTSTRAP",
        "status": "PASS",
        "date_epoch": time.time(),
        "manifest_revision": manifest.get("revision"),
        "pretrained_root": str(root),
        "total_bytes": total,
        "total_gb_decimal": round(total / 1_000_000_000, 3),
        "files": records,
        "wav2vec2_downloaded": False,
        "dwpose_downloaded": False,
        "film_interpolation_downloaded": False,
        "models_loaded_by_this_gate": False,
    }
    result_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"SSD-MODELS-DOWNLOADER: PASS - {result['total_gb_decimal']} GB verified")
except Exception as exc:
    failure = {
        "gate": "SSD_MODEL_BOOTSTRAP",
        "status": "FAIL",
        "error": str(exc),
        "date_epoch": time.time(),
    }
    try:
        result_path.write_text(json.dumps(failure, indent=2), encoding="utf-8")
    except Exception:
        pass
    print(f"SSD-MODELS: FAIL - {exc}")
    sys.exit(1)
'@
Set-Content -LiteralPath $Downloader -Value $pythonSource -Encoding UTF8

$env:SSD_MODEL_MANIFEST = $Manifest
$env:SSD_PRETRAINED_ROOT = $PretrainedRoot
$env:SSD_MODEL_RESULT = $Result
$env:PYTHONUNBUFFERED = '1'

Write-Host '[RUN] Downloading/verifying minimal SSD model set. Large files resume from .part files.' -ForegroundColor Yellow
$proc = Start-Process -FilePath $Python -ArgumentList $Downloader -NoNewWindow -Wait -PassThru
if ($proc.ExitCode -ne 0) {
    if (Test-Path -LiteralPath $Result -PathType Leaf) {
        try {
            $failure = Get-Content -LiteralPath $Result -Raw | ConvertFrom-Json
            Fail "model downloader exited with code $($proc.ExitCode): $($failure.error)"
        } catch {
            Fail "model downloader exited with code $($proc.ExitCode); see console output and $Result"
        }
    }
    Fail "model downloader exited with code $($proc.ExitCode)"
}

if (-not (Test-Path -LiteralPath $Result -PathType Leaf)) {
    Fail "model downloader did not write result marker: $Result"
}
try {
    $state = Get-Content -LiteralPath $Result -Raw | ConvertFrom-Json
} catch {
    Fail "cannot parse model result marker: $Result"
}
if ($state.status -ne 'PASS') {
    Fail "model result marker is not PASS"
}

Write-Host ''
Write-Host 'SSD-MODELS: PASS' -ForegroundColor Green
Write-Host "TOTAL:   $($state.total_gb_decimal) GB verified" -ForegroundColor Green
Write-Host "ROOT:    $PretrainedRoot" -ForegroundColor Green
Write-Host "MARKER:  $Result" -ForegroundColor Cyan
Write-Host ''
Write-Host '[NEXT] Stop here. Input/config + first 8-frame Exilada inference is the next documented gate.' -ForegroundColor Yellow
