param(
    [string]$ProjectRepoRoot = 'D:\GOOGLE DRIVE\DEV\Roguelite',
    [string]$SsdRoot = 'Z:\AI\SpriteSheetDiffusionSpike'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Fail([string]$Message) {
    Write-Host "SSD-SUPPORT: FAIL - $Message" -ForegroundColor Red
    exit 1
}

$EnvMarker = Join-Path $SsdRoot 'ssd_environment_bootstrap.json'
$DependencyMarker = Join-Path $SsdRoot 'ssd_dependencies_bootstrap.json'
$ModelMarker = Join-Path $SsdRoot 'ssd_models_bootstrap.json'
$UpstreamRepo = Join-Path $SsdRoot 'repo'
$ModelTraining = Join-Path $UpstreamRepo 'ModelTraining'
$Manifest = Join-Path $ProjectRepoRoot 'tools\structured-2d-character-pipeline\ssd_authoring_support_manifest.json'
$Downloader = Join-Path $SsdRoot 'ssd_download_authoring_support.py'
$Result = Join-Path $SsdRoot 'ssd_authoring_support_bootstrap.json'
$ProbeResult = Join-Path $SsdRoot 'ssd_authoring_support_probe.json'

Write-Host ''
Write-Host 'Roguelite - Sprite Sheet Diffusion production-authoring support bootstrap' -ForegroundColor Cyan
Write-Host '[SCOPE] DWPose action-pose extraction + optional FILM interpolation + bundled MediaPipe asset verification.' -ForegroundColor Green
Write-Host '[LOCK] Core SSD model gate must already be PASS.' -ForegroundColor Green
Write-Host '[LOCK] Legacy CMU OpenPose weights are NOT downloaded.' -ForegroundColor Green
Write-Host '[LOCK] No wav2vec/audio portrait models are downloaded.' -ForegroundColor Green
Write-Host '[LOCK] No inference is executed in this gate.' -ForegroundColor Green
Write-Host ''

foreach ($required in @($EnvMarker, $DependencyMarker, $ModelMarker, $ModelTraining, $Manifest)) {
    if (-not (Test-Path -LiteralPath $required)) {
        Fail "required path missing: $required"
    }
}

try {
    $envState = Get-Content -LiteralPath $EnvMarker -Raw | ConvertFrom-Json
    $depState = Get-Content -LiteralPath $DependencyMarker -Raw | ConvertFrom-Json
    $modelState = Get-Content -LiteralPath $ModelMarker -Raw | ConvertFrom-Json
} catch {
    Fail 'cannot parse required PASS markers.'
}

if ($envState.status -ne 'PASS') { Fail 'environment marker is not PASS.' }
if ($depState.status -ne 'PASS') { Fail 'dependency marker is not PASS.' }
if ($modelState.status -ne 'PASS') { Fail 'core model marker is not PASS.' }

$CondaExe = [string]$envState.conda_exe
if (-not (Test-Path -LiteralPath $CondaExe -PathType Leaf)) {
    Fail "conda.exe from environment marker is missing: $CondaExe"
}
$CondaRoot = Split-Path -Parent (Split-Path -Parent $CondaExe)
$Python = Join-Path $CondaRoot 'envs\ssd\python.exe'
if (-not (Test-Path -LiteralPath $Python -PathType Leaf)) {
    Fail "ssd environment python.exe missing: $Python"
}

Write-Host "[OK] Python:        $Python" -ForegroundColor Green
Write-Host "[OK] ModelTraining: $ModelTraining" -ForegroundColor Green
Write-Host "[OK] Manifest:      $Manifest" -ForegroundColor Green
Write-Host ''

$pythonSource = @'
import hashlib
import json
import os
import shutil
import sys
import time
from pathlib import Path

import requests

manifest_path = Path(os.environ["SSD_SUPPORT_MANIFEST"])
root = Path(os.environ["SSD_MODELTRAINING_ROOT"])
result_path = Path(os.environ["SSD_SUPPORT_RESULT"])
probe_path = Path(os.environ["SSD_SUPPORT_PROBE"])


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def human_mb(n: int) -> str:
    return f"{n / 1_000_000:.1f} MB"


def valid_existing(path: Path, item: dict):
    if not path.is_file():
        return False, None
    if path.stat().st_size < int(item.get("expected_min_bytes") or 1):
        return False, None
    actual = sha256_file(path)
    expected = item.get("expected_sha256")
    if expected and actual.lower() != expected.lower():
        return False, actual
    return True, actual


def download_one(session: requests.Session, item: dict):
    dest = root / Path(item["destination"])
    dest.parent.mkdir(parents=True, exist_ok=True)

    ok, existing_hash = valid_existing(dest, item)
    if ok:
        print(f"[SKIP] {item['id']}: verified existing {dest}")
        return {
            "id": item["id"], "path": str(dest), "size": dest.stat().st_size,
            "sha256": existing_hash, "source": item["source"], "downloaded": False,
            "license_family": item.get("license_family")
        }

    if dest.exists():
        print(f"[REPAIR] {item['id']}: removing invalid existing file")
        dest.unlink()

    part = Path(str(dest) + ".part")
    start = part.stat().st_size if part.exists() else 0
    headers = {"User-Agent": "Roguelite-SSD-Support/1.0"}
    if start:
        headers["Range"] = f"bytes={start}-"
        print(f"[RESUME] {item['id']}: {human_mb(start)} already present")
    else:
        print(f"[DOWNLOAD] {item['id']}")

    response = session.get(item["source"], headers=headers, stream=True, allow_redirects=True, timeout=(30, 300))

    if response.status_code == 416 and start:
        response.close()
        actual = sha256_file(part)
        expected = item.get("expected_sha256")
        if expected and actual.lower() == expected.lower():
            part.replace(dest)
        else:
            part.unlink(missing_ok=True)
            raise RuntimeError(f"invalid resume state for {item['id']}; removed partial file")
    else:
        if start and response.status_code == 206:
            mode = "ab"
            written = start
        elif response.status_code == 200:
            mode = "wb"
            written = 0
            start = 0
        else:
            body = ""
            try:
                body = response.text[:500]
            except Exception:
                pass
            response.close()
            raise RuntimeError(f"HTTP {response.status_code} for {item['id']}: {body}")

        with part.open(mode) as f:
            for chunk in response.iter_content(chunk_size=8 * 1024 * 1024):
                if not chunk:
                    continue
                f.write(chunk)
                written += len(chunk)
        response.close()
        part.replace(dest)

    size = dest.stat().st_size
    if size < int(item.get("expected_min_bytes") or 1):
        dest.unlink(missing_ok=True)
        raise RuntimeError(f"{item['id']} too small after download: {size}")

    actual = sha256_file(dest)
    expected = item.get("expected_sha256")
    if expected and actual.lower() != expected.lower():
        dest.unlink(missing_ok=True)
        raise RuntimeError(f"SHA256 mismatch for {item['id']}: expected {expected}, got {actual}")

    print(f"[OK] {item['id']}: {human_mb(size)} sha256={actual}")
    return {
        "id": item["id"], "path": str(dest), "size": size,
        "sha256": actual, "source": item["source"], "downloaded": True,
        "license_family": item.get("license_family")
    }


try:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    root.mkdir(parents=True, exist_ok=True)

    remaining_min = 0
    for item in manifest["files"]:
        dest = root / Path(item["destination"])
        ok, _ = valid_existing(dest, item)
        if ok:
            continue
        part = Path(str(dest) + ".part")
        partial = part.stat().st_size if part.exists() else 0
        remaining_min += max(0, int(item.get("expected_min_bytes") or 0) - partial)

    free = shutil.disk_usage(root).free
    required = int(remaining_min * 1.15 + 500_000_000)
    print(f"[SPACE] free={human_mb(free)} estimated-minimum-needed={human_mb(required)}")
    if free < required:
        raise RuntimeError(f"insufficient free space: {human_mb(free)} free, {human_mb(required)} required")

    session = requests.Session()
    records = [download_one(session, item) for item in manifest["files"]]

    bundled = []
    for relative in manifest.get("repo_bundled_assets_to_verify", []):
        path = root / relative
        if not path.is_file() or path.stat().st_size <= 0:
            raise RuntimeError(f"required bundled repo asset missing: {path}")
        bundled.append({"path": str(path), "size": path.stat().st_size, "sha256": sha256_file(path)})
        print(f"[OK] bundled asset: {relative}")

    probe = {"status": "PASS", "dwpose": {}, "film": {}, "bundled_assets": bundled}

    import cv2
    det_path = root / "models/openpose/yolox_l.onnx"
    pose_path = root / "models/openpose/dw-ll_ucoco_384.onnx"
    det = cv2.dnn.readNetFromONNX(str(det_path))
    pose = cv2.dnn.readNetFromONNX(str(pose_path))
    probe["dwpose"] = {
        "status": "PASS",
        "detector": str(det_path),
        "pose": str(pose_path),
        "opencv": cv2.__version__
    }
    del det, pose
    print("[PROBE] DWPose ONNX load: PASS")

    import torch
    film_path = root / "pretrained_model/film_net_fp16.pt"
    film = torch.jit.load(str(film_path), map_location="cpu")
    film.eval()
    probe["film"] = {"status": "PASS", "path": str(film_path), "torch": torch.__version__}
    del film
    print("[PROBE] FILM TorchScript load: PASS")

    probe_path.write_text(json.dumps(probe, indent=2), encoding="utf-8")

    total = sum(r["size"] for r in records)
    result = {
        "gate": "SSD_AUTHORING_SUPPORT",
        "status": "PASS",
        "date_epoch": time.time(),
        "manifest_revision": manifest.get("revision"),
        "modeltraining_root": str(root),
        "total_downloaded_asset_bytes": total,
        "total_downloaded_asset_gb_decimal": round(total / 1_000_000_000, 3),
        "files": records,
        "bundled_assets": bundled,
        "dwpose_available": True,
        "film_interpolation_available": True,
        "legacy_cmu_openpose_weights_downloaded": False,
        "wav2vec2_downloaded": False,
        "audio_portrait_models_downloaded": False,
        "inference_executed_by_this_gate": False,
        "probe": str(probe_path)
    }
    result_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"SSD-SUPPORT-DOWNLOADER: PASS - {result['total_downloaded_asset_gb_decimal']} GB verified")
except Exception as exc:
    failure = {"gate": "SSD_AUTHORING_SUPPORT", "status": "FAIL", "error": str(exc), "date_epoch": time.time()}
    try:
        result_path.write_text(json.dumps(failure, indent=2), encoding="utf-8")
    except Exception:
        pass
    print(f"SSD-SUPPORT: FAIL - {exc}")
    sys.exit(1)
'@

Set-Content -LiteralPath $Downloader -Value $pythonSource -Encoding UTF8

$env:SSD_SUPPORT_MANIFEST = $Manifest
$env:SSD_MODELTRAINING_ROOT = $ModelTraining
$env:SSD_SUPPORT_RESULT = $Result
$env:SSD_SUPPORT_PROBE = $ProbeResult
$env:PYTHONUNBUFFERED = '1'

Write-Host '[RUN] Downloading/verifying SSD production-authoring support assets...' -ForegroundColor Yellow
$proc = Start-Process -FilePath $Python -ArgumentList $Downloader -NoNewWindow -Wait -PassThru
if ($proc.ExitCode -ne 0) {
    if (Test-Path -LiteralPath $Result -PathType Leaf) {
        try {
            $failure = Get-Content -LiteralPath $Result -Raw | ConvertFrom-Json
            Fail "support downloader exited with code $($proc.ExitCode): $($failure.error)"
        } catch {
            Fail "support downloader exited with code $($proc.ExitCode); inspect $Result"
        }
    }
    Fail "support downloader exited with code $($proc.ExitCode)"
}

if (-not (Test-Path -LiteralPath $Result -PathType Leaf)) {
    Fail "support downloader did not write result marker: $Result"
}
try {
    $state = Get-Content -LiteralPath $Result -Raw | ConvertFrom-Json
} catch {
    Fail "cannot parse support result marker: $Result"
}
if ($state.status -ne 'PASS') {
    Fail 'support result marker is not PASS.'
}

Write-Host ''
Write-Host 'SSD-SUPPORT: PASS' -ForegroundColor Green
Write-Host "DWPose:  available" -ForegroundColor Green
Write-Host "FILM:    available (optional, not default)" -ForegroundColor Green
Write-Host "MARKER:  $Result" -ForegroundColor Cyan
Write-Host "PROBE:   $ProbeResult" -ForegroundColor Cyan
Write-Host ''
Write-Host '[NEXT] Production support is complete. Prepare Exilada master + pose sequence + first real SSD inference.' -ForegroundColor Yellow
