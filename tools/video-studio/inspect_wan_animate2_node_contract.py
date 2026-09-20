#!/usr/bin/env python3
"""Static contract probe for the locally installed WanAnimate2ToVideo node.

No ComfyUI import, no torch import, no model load, no inference.
Reads the local node source plus saved object-info/API-prompt/manifests to answer what
`pose_video` actually is in this installation and how prior validated workflows wired it.
"""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path


def read_text(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8-sig", errors="replace")


def class_block(text: str, class_name: str):
    lines = text.splitlines()
    start = None
    indent = None
    for i, line in enumerate(lines):
        m = re.match(r"^(\s*)class\s+" + re.escape(class_name) + r"\b", line)
        if m:
            start = i
            indent = len(m.group(1))
            break
    if start is None:
        return None
    end = len(lines)
    for i in range(start + 1, len(lines)):
        m = re.match(r"^(\s*)class\s+\w+\b", lines[i])
        if m and len(m.group(1)) <= indent:
            end = i
            break
    return {"start_line": start + 1, "end_line": end, "text": "\n".join(lines[start:end])}


def find_execute_signature(block_text: str):
    for line in block_text.splitlines():
        if re.search(r"\bdef\s+execute\s*\(", line):
            return line.strip()
    return None


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return None


def find_node_info(obj, node_name: str):
    if isinstance(obj, dict):
        if node_name in obj and isinstance(obj[node_name], dict):
            return obj[node_name]
        for v in obj.values():
            r = find_node_info(v, node_name)
            if r is not None:
                return r
    elif isinstance(obj, list):
        for v in obj:
            r = find_node_info(v, node_name)
            if r is not None:
                return r
    return None


def api_nodes(obj):
    if not isinstance(obj, dict):
        return {}
    # Comfy API prompt is normally {node_id:{class_type,inputs,...}}
    if all(isinstance(v, dict) for v in obj.values()):
        return obj
    for key in ("prompt", "workflow", "nodes"):
        v = obj.get(key)
        if isinstance(v, dict):
            return v
    return {}


def resolve_link(nodes, value):
    if isinstance(value, list) and len(value) >= 1:
        nid = str(value[0])
        node = nodes.get(nid)
        if isinstance(node, dict):
            return {"node_id": nid, "class_type": node.get("class_type"), "inputs": node.get("inputs")}
    return None


def inspect_api_prompt(path: Path):
    obj = load_json(path)
    if obj is None:
        return None
    nodes = api_nodes(obj)
    found = []
    for nid, node in nodes.items():
        if not isinstance(node, dict):
            continue
        if node.get("class_type") == "WanAnimate2ToVideo":
            inputs = node.get("inputs") or {}
            rec = {"node_id": str(nid), "inputs": inputs, "linked_inputs": {}}
            for k, v in inputs.items():
                link = resolve_link(nodes, v)
                if link:
                    rec["linked_inputs"][k] = link
            found.append(rec)
    return found


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--wan-root", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    root = args.wan_root

    nodes_wan = root / "comfy_extras" / "nodes_wan.py"
    object_info = root / "object_info_wan_bf16.json"
    if not object_info.is_file():
        alt = root / "object_info_w0_live.json"
        object_info = alt if alt.is_file() else object_info

    source = read_text(nodes_wan)
    block = class_block(source, "WanAnimate2ToVideo")
    info_obj = load_json(object_info) if object_info.is_file() else None
    node_info = find_node_info(info_obj, "WanAnimate2ToVideo") if info_obj is not None else None

    prompt_files = sorted(root.glob("w*_api_prompt.json"))
    prompt_usage = {}
    for p in prompt_files:
        hit = inspect_api_prompt(p)
        if hit:
            prompt_usage[p.name] = hit

    manifest_usage = []
    for p in sorted(root.glob("w*_run_manifest.json")):
        obj = load_json(p)
        if not isinstance(obj, dict):
            continue
        driver = obj.get("driver")
        if driver or "animate" in json.dumps(obj, ensure_ascii=False).lower():
            manifest_usage.append({
                "file": p.name,
                "gate": obj.get("gate"),
                "driver": driver,
                "prompt_file": obj.get("prompt_file"),
                "canonical_output": obj.get("canonical_output"),
                "hypothesis": obj.get("hypothesis"),
            })

    result = {
        "schema": "wan-animate2-node-contract-preflight/v1",
        "wan_root": str(root),
        "nodes_wan": str(nodes_wan),
        "object_info": str(object_info),
        "class_block": block,
        "execute_signature": find_execute_signature(block["text"]) if block else None,
        "node_info": node_info,
        "api_prompt_usage": prompt_usage,
        "manifest_usage": manifest_usage,
        "interpretation_guard": "Do not infer that pose_video accepts COCO-133 or a skeleton render until source/object-info and saved workflow wiring show the expected Comfy IMAGE/video representation.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    print("WAN-ANIMATE-2 NODE CONTRACT PROBE")
    print("=================================")
    print(f"Root: {root}")
    print(f"Node source: {'OK' if nodes_wan.is_file() else 'MISSING'} {nodes_wan}")
    print(f"Object info: {'OK' if object_info.is_file() else 'MISSING'} {object_info}")
    if block:
        print(f"WanAnimate2ToVideo source lines: {block['start_line']}-{block['end_line']}")
        print(f"Execute signature: {result['execute_signature']}")
    else:
        print("WanAnimate2ToVideo class: NOT FOUND")

    print("\nObject-info node contract:")
    if node_info is None:
        print("  NOT FOUND")
    else:
        print(json.dumps(node_info, ensure_ascii=False, indent=2))

    print("\nSaved API prompt wiring:")
    if not prompt_usage:
        print("  No WanAnimate2ToVideo usage found in w*_api_prompt.json")
    else:
        for name, hits in prompt_usage.items():
            print(f"  {name}")
            for hit in hits:
                print(f"    node {hit['node_id']}")
                for k, link in hit['linked_inputs'].items():
                    print(f"      {k} <- {link['class_type']} node {link['node_id']}")
                inputs = hit.get('inputs') or {}
                for key in ("pose_video", "face_video", "reference_image", "pose_video_strength", "face_video_strength", "pose_start_percent", "pose_end_percent", "width", "height", "length"):
                    if key in inputs and key not in hit['linked_inputs']:
                        print(f"      {key} = {inputs[key]}")

    print("\nPrior run manifests with driver:")
    for m in manifest_usage:
        if m.get("driver"):
            print(f"  {m['file']}: driver={m['driver']} gate={m.get('gate')}")

    print("\n--- EXACT WanAnimate2ToVideo SOURCE BLOCK ---")
    if block:
        for n, line in enumerate(block["text"].splitlines(), block["start_line"]):
            print(f"{n:04d}: {line}")
    print("--- END SOURCE BLOCK ---")
    print(f"\nJSON: {args.output}")
    print("No ComfyUI import, model load, DWPose, or inference executed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
