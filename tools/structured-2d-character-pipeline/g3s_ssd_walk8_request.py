#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from types import SimpleNamespace

import g3s_ssd_prepare_walk8 as impl


def read_request(path: Path) -> dict:
    if not path.is_file():
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8-sig"))


def require(data: dict, *keys: str) -> None:
    missing = [key for key in keys if not isinstance(data.get(key), str) or not data[key]]
    if missing:
        raise RuntimeError("request missing required string fields: " + ", ".join(missing))


def command_probe(request_path: Path, output_path: Path) -> int:
    data = read_request(request_path)
    require(data, "project_repo_root", "master", "model_training", "guide", "marker")
    out = {
        "status": "PASS",
        "project_repo_root": data["project_repo_root"],
        "master": data["master"],
        "model_training": data["model_training"],
        "guide": data["guide"],
        "marker": data["marker"],
    }
    output_path.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print("SSD-WALK8-REQUEST-PROBE: PASS")
    return 0


def command_prepare(request_path: Path) -> int:
    data = read_request(request_path)
    require(data, "master", "model_training", "guide", "marker")
    args = SimpleNamespace(
        master=data["master"],
        model_training=data["model_training"],
        guide=data["guide"],
        marker=data["marker"],
    )
    return impl.prepare(args)


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    probe = sub.add_parser("probe")
    probe.add_argument("request")
    probe.add_argument("output")

    prep = sub.add_parser("prepare")
    prep.add_argument("request")

    args = parser.parse_args()
    if args.command == "probe":
        return command_probe(Path(args.request).resolve(), Path(args.output).resolve())
    return command_prepare(Path(args.request).resolve())


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"SSD-WALK8: FAIL - {exc}")
        raise SystemExit(1)
