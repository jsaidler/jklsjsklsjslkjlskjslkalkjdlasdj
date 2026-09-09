#!/usr/bin/env python3
"""UI-independent adapter contract for Roguelite Asset Studio model backends."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol, Sequence


@dataclass(frozen=True)
class ReferenceInput:
    role: str
    path: Path


@dataclass(frozen=True)
class StaticGenerationRequest:
    job_id: str
    asset_type: str
    output_contract: str
    prompt: str
    negative: str = ""
    references: Sequence[ReferenceInput] = field(default_factory=tuple)
    width: int = 768
    height: int = 768
    steps: int = 4
    cfg: float = 1.0
    sampler: str = "euler"
    seed: int = 0

    def validate(self) -> None:
        if not self.job_id.strip():
            raise ValueError("job_id must not be empty")
        if not self.asset_type.strip():
            raise ValueError("asset_type must not be empty")
        if not self.output_contract.strip():
            raise ValueError("output_contract must not be empty")
        if not self.prompt.strip():
            raise ValueError("prompt must not be empty")
        if self.width <= 0 or self.height <= 0:
            raise ValueError("width and height must be positive")
        if self.width % 16 or self.height % 16:
            raise ValueError("width and height must be multiples of 16")
        if self.steps <= 0:
            raise ValueError("steps must be positive")
        for reference in self.references:
            if not reference.role.strip():
                raise ValueError("reference role must not be empty")
            if not Path(reference.path).is_file():
                raise FileNotFoundError(f"reference file not found: {reference.path}")


@dataclass(frozen=True)
class GenerationResult:
    adapter_id: str
    prompt_id: str
    output_path: Path
    elapsed_seconds: float
    request: StaticGenerationRequest
    reference_hashes: tuple[str, ...]
    output_sha256: str


class StaticAssetAdapter(Protocol):
    adapter_id: str

    def verify_runtime(self) -> None:
        """Raise if the backend is not installed and executable."""

    def generate(self, request: StaticGenerationRequest, destination: Path) -> GenerationResult:
        """Execute one static-generation/edit job and copy the result to destination."""
