#!/usr/bin/env python3
"""Direct Big-LaMa adapter for exact automatic-mask object removal.

This backend is intentionally narrow. It does not interpret text prompts and it
never decides where to edit. The Roguelite Asset Studio supplies an approved
automatic operation mask; LaMa only synthesizes replacement pixels inside that
region. A deterministic final compositor remains authoritative outside the
allowed neighborhood.

The runtime artifact is the TorchScript Big-LaMa model distributed by
simple-lama-inpainting. Because TorchScript is executable/pickle-bearing, the
adapter refuses to load anything except the pinned SHA256.
"""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image
import torch

MODEL_NAME = "big-lama.pt"
MODEL_SHA256 = "344c77bbcb158f17dd143070d1e789f38a66c04202311ae3a258ef66667a9ea9"
MODEL_BYTES = 206_134_115


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _ceil_modulo(value: int, modulo: int = 8) -> int:
    if value % modulo == 0:
        return value
    return ((value // modulo) + 1) * modulo


def _pad_symmetric_chw(array: np.ndarray, modulo: int = 8) -> np.ndarray:
    _, height, width = array.shape
    out_h = _ceil_modulo(height, modulo)
    out_w = _ceil_modulo(width, modulo)
    return np.pad(
        array,
        ((0, 0), (0, out_h - height), (0, out_w - width)),
        mode="symmetric",
    )


@dataclass(frozen=True)
class LaMaResult:
    output_path: Path
    elapsed_seconds: float
    output_sha256: str
    source_sha256: str
    mask_sha256: str
    device: str


class LaMaInpaintAdapter:
    adapter_id = "big_lama_object_removal"

    def __init__(self, model_path: Path, prefer_cuda: bool = True) -> None:
        self.model_path = Path(model_path).resolve()
        self.device = torch.device("cuda" if prefer_cuda and torch.cuda.is_available() else "cpu")
        self._model = None

    def verify_runtime(self) -> None:
        if not self.model_path.is_file():
            raise FileNotFoundError(self.model_path)
        actual_size = self.model_path.stat().st_size
        if actual_size != MODEL_BYTES:
            raise RuntimeError(f"Big-LaMa size mismatch: expected {MODEL_BYTES}, got {actual_size}")
        actual_hash = sha256_file(self.model_path)
        if actual_hash != MODEL_SHA256:
            raise RuntimeError(f"Big-LaMa SHA256 mismatch: expected {MODEL_SHA256}, got {actual_hash}")
        if self.device.type == "cuda" and not torch.cuda.is_available():
            raise RuntimeError("CUDA device requested but unavailable")

    def _load(self) -> None:
        if self._model is not None:
            return
        self.verify_runtime()
        self._model = torch.jit.load(str(self.model_path), map_location=self.device)
        self._model.eval()
        self._model.to(self.device)

    def inpaint(self, source: Path, mask: Path, destination: Path) -> LaMaResult:
        self._load()
        source = Path(source).resolve()
        mask = Path(mask).resolve()
        destination = Path(destination).resolve()
        if not source.is_file():
            raise FileNotFoundError(source)
        if not mask.is_file():
            raise FileNotFoundError(mask)

        with Image.open(source) as opened:
            rgb = opened.convert("RGB")
            original_size = rgb.size
            image_np = np.asarray(rgb, dtype=np.float32) / 255.0
        with Image.open(mask) as opened:
            mask_l = opened.convert("L")
            if mask_l.size != original_size:
                raise ValueError(f"mask/source size mismatch: {mask_l.size} vs {original_size}")
            mask_np = np.asarray(mask_l, dtype=np.float32) / 255.0

        image_chw = np.transpose(image_np, (2, 0, 1))
        mask_chw = mask_np[np.newaxis, ...]
        image_chw = _pad_symmetric_chw(image_chw, 8)
        mask_chw = _pad_symmetric_chw(mask_chw, 8)

        image_t = torch.from_numpy(image_chw).unsqueeze(0).to(self.device)
        mask_t = torch.from_numpy(mask_chw).unsqueeze(0).to(self.device)
        mask_t = (mask_t > 0).to(image_t.dtype)

        if self.device.type == "cuda":
            torch.cuda.synchronize()
        started = time.time()
        with torch.inference_mode():
            out = self._model(image_t, mask_t)
        if self.device.type == "cuda":
            torch.cuda.synchronize()
        elapsed = time.time() - started

        result = out[0].permute(1, 2, 0).detach().float().cpu().numpy()
        result = np.clip(result * 255.0, 0, 255).astype(np.uint8)
        result_image = Image.fromarray(result, mode="RGB").crop((0, 0, original_size[0], original_size[1]))
        destination.parent.mkdir(parents=True, exist_ok=True)
        result_image.save(destination)

        return LaMaResult(
            output_path=destination,
            elapsed_seconds=elapsed,
            output_sha256=sha256_file(destination),
            source_sha256=sha256_file(source),
            mask_sha256=sha256_file(mask),
            device=str(self.device),
        )
