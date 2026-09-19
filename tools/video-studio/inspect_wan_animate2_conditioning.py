#!/usr/bin/env python3
"""Inspect the installed local Wan-Animate-2 code path without running inference.

Goal: identify the real loader/model_type and the concrete conditioning interfaces present
in the user's installation before adapting the validated behavioral pose driver.

This script intentionally does not import ComfyUI, torch, Wan, or model weights. It only
reads source/config text and file metadata.
"""
from __future__ import annotations

import argparse
import ast
import json
import os
import re
from pathlib import Path

SKIP_PARTS = {
    ".git", ".venv", "venv", "env", "env_uv", "site-packages", "models", "output",
    "outputs", "input", "inputs", "temp", "cache", "__pycache__", "node_modules"
}
TEXT_EXTS = {".py", ".json", ".yaml", ".yml", ".toml", ".md", ".txt"}
TOKENS = [
    "animate2", "model_type", "pose", "driving", "reference", "ref_image", "ref_video",
    "control", "condition", "conditioning", "mask", "face", "motion", "clip_fea",
    "image_emb", "video", "NODE_CLASS_MAPPINGS", "INPUT_TYPES", "WanAnimate"
]


def fmt_bytes(n: int) -> str:
    units = ["B", "KiB", "MiB", "GiB", "TiB"]
    v = float(n)
    for u in units:
        if v < 1024 or u == units[-1]:
            return f"{v:.3f} {u}"
        v /= 1024.0
    return f"{n} B"


def should_skip(path: Path) -> bool:
    return any(part.lower() in SKIP_PARTS for part in path.parts)


def iter_text_files(root: Path):
    for p in root.rglob("*"):
        if not p.is_file() or should_skip(p):
            continue
        if p.suffix.lower() not in TEXT_EXTS:
            continue
        try:
            if p.stat().st_size > 3 * 1024 * 1024:
                continue
        except OSError:
            continue
        yield p


def read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8-sig", errors="replace")
    except OSError:
        return None


def rel(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def signature_from_node(node) -> str:
    args = []
    a = node.args
    pos = list(a.posonlyargs) + list(a.args)
    defaults = [None] * (len(pos) - len(a.defaults)) + list(a.defaults)
    for arg, default in zip(pos, defaults):
        s = arg.arg
        if default is not None:
            try:
                s += "=" + ast.unparse(default)
            except Exception:
                s += "=..."
        args.append(s)
    if a.vararg:
        args.append("*" + a.vararg.arg)
    for arg, default in zip(a.kwonlyargs, a.kw_defaults):
        s = arg.arg
        if default is not None:
            try:
                s += "=" + ast.unparse(default)
            except Exception:
                s += "=..."
        args.append(s)
    if a.kwarg:
        args.append("**" + a.kwarg.arg)
    return f"{node.name}({', '.join(args)})"


def python_symbols(text: str):
    out = []
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return out
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            out.append({"kind": "function", "name": node.name, "signature": signature_from_node(node), "line": node.lineno})
        elif isinstance(node, ast.ClassDef):
            out.append({"kind": "class", "name": node.name, "line": node.lineno})
            for sub in node.body:
                if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)) and sub.name in {"forward", "__call__", "INPUT_TYPES", "load_model", "encode", "decode", "process", "execute", "sample"}:
                    out.append({"kind": "method", "class": node.name, "name": sub.name, "signature": signature_from_node(sub), "line": sub.lineno})
    return out


def relevant_lines(text: str, max_lines=35):
    lines = text.splitlines()
    scored = []
    for i, line in enumerate(lines, 1):
        low = line.lower()
        hits = [t for t in TOKENS if t.lower() in low]
        if hits:
            score = len(hits)
            if "animate2" in low or "model_type" in low:
                score += 4
            if "input_types" in low or "node_class_mappings" in low:
                score += 3
            scored.append((score, i, line.rstrip()))
    scored.sort(key=lambda x: (-x[0], x[1]))
    return [{"line": i, "text": s} for _, i, s in scored[:max_lines]]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, default=Path(r"Z:\AI\WanAnimate2"))
    ap.add_argument("--output", type=Path, default=Path(r"Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\unified\wan_animate2_conditioning_preflight.json"))
    args = ap.parse_args()
    root = args.root
    if not root.is_dir():
        raise SystemExit(f"Wan root missing: {root}")

    known = [
        root / "models" / "diffusion_models" / "wan_animate_2_bf16.safetensors",
        root / "comfy" / "ldm" / "wan" / "model_animate2.py",
    ]
    model_files = []
    models = root / "models"
    if models.is_dir():
        for p in models.rglob("*"):
            if p.is_file():
                try:
                    model_files.append({"path": rel(p, root), "bytes": p.stat().st_size, "size": fmt_bytes(p.stat().st_size)})
                except OSError:
                    pass
        model_files.sort(key=lambda x: x["bytes"], reverse=True)

    matches = []
    total_files = 0
    for p in iter_text_files(root):
        total_files += 1
        text = read_text(p)
        if text is None:
            continue
        low = text.lower()
        hit_tokens = sorted({t for t in TOKENS if t.lower() in low})
        if not hit_tokens:
            continue
        score = len(hit_tokens)
        if "animate2" in low:
            score += 8
        if "model_type" in low:
            score += 5
        if "node_class_mappings" in low or "input_types" in low:
            score += 4
        item = {
            "path": rel(p, root),
            "score": score,
            "tokens": hit_tokens,
            "relevant_lines": relevant_lines(text),
        }
        if p.suffix.lower() == ".py":
            item["symbols"] = python_symbols(text)
        matches.append(item)

    matches.sort(key=lambda x: (-x["score"], x["path"].lower()))
    top = matches[:35]

    direct_animate2_refs = []
    for m in matches:
        if "animate2" in {x.lower() for x in m["tokens"]} or any("animate2" in r["text"].lower() for r in m["relevant_lines"]):
            direct_animate2_refs.append(m["path"])

    result = {
        "schema": "wan-animate2-conditioning-preflight/v1",
        "root": str(root.resolve()),
        "known_paths": [{"path": str(p), "exists": p.exists()} for p in known],
        "model_files_largest": model_files[:30],
        "text_files_scanned": total_files,
        "matching_files": len(matches),
        "direct_animate2_reference_files": direct_animate2_refs[:50],
        "top_code_matches": top,
        "note": "Static source/config inspection only. No ComfyUI import and no model inference executed."
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    print("WAN-ANIMATE-2 CONDITIONING PREFLIGHT")
    print("====================================")
    print(f"Root: {root}")
    for kp in result["known_paths"]:
        print(f"Known path: {'OK' if kp['exists'] else 'MISSING'}  {kp['path']}")
    print(f"Text/config files scanned: {total_files}")
    print(f"Relevant files: {len(matches)}")
    print("Largest model files:")
    for x in model_files[:12]:
        print(f"  {x['size']:>12}  {x['path']}")
    print("Direct Animate2 references:")
    for p in direct_animate2_refs[:20]:
        print(f"  {p}")
    print("Top conditioning/interface matches:")
    for m in top[:15]:
        print(f"\n[{m['score']}] {m['path']}")
        if m.get("symbols"):
            for s in m["symbols"][:10]:
                sig = s.get("signature") or s.get("name")
                owner = (s.get("class") + ".") if s.get("class") else ""
                print(f"  symbol L{s['line']}: {owner}{sig}")
        for r in m["relevant_lines"][:8]:
            print(f"  L{r['line']}: {r['text'][:220]}")
    print(f"\nJSON: {args.output}")
    print("No inference executed.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
