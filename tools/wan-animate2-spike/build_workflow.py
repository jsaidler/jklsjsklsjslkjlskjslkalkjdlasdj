import json
import sys
from pathlib import Path

MASTER = "exilada_master.png"
DRIVER = "exilada_driver_17f.mp4"
MODEL = "wan_animate_2_int8_convrot.safetensors"
TEXT = "umt5_xxl_fp8_e4m3fn_scaled.safetensors"
CLIPV = "clip_vision_h.safetensors"
VAE = "Wan2_1_VAE_bf16.safetensors"
PROMPT = (
    "Character appearance description: An adult brown-olive skinned woman with a hard mature face, "
    "long extremely voluminous messy black hair, lean natural athletic anatomy, visible scars and bruises. "
    "She wears a worn beige cloth bandage across the chest and a deteriorated asymmetrical beige cloth wrap "
    "around the hips and thighs. Iron captivity shackles and broken chain segments are visible on the wrist "
    "and ankle. She is barefoot. Background description: plain neutral gray studio background, static, with even lighting."
)
POSE_PROMPT = (
    "A person performs one controlled small forward half-step with a smooth weight transfer and subtle natural "
    "arm swing. Full body remains visible. Camera and background are completely stationary."
)


def iter_nodes(obj):
    if isinstance(obj, dict):
        nodes = obj.get("nodes")
        if isinstance(nodes, list):
            for node in nodes:
                if isinstance(node, dict):
                    yield node
                yield from iter_nodes(node)
        for k, v in obj.items():
            if k != "nodes":
                yield from iter_nodes(v)
    elif isinstance(obj, list):
        for item in obj:
            yield from iter_nodes(item)


def node_name(node):
    props = node.get("properties") or {}
    return props.get("Node name for S&R") or node.get("type")


def patch_top_level_motion_transfer(node):
    vals = node.get("widgets_values")
    inputs = node.get("inputs") or []
    if not isinstance(vals, list) or len(vals) < 20:
        return False
    labels = {str(i.get("name", "")) for i in inputs if isinstance(i, dict)}
    if "reference_image_strength_1" not in labels or "pose_strength_1" not in labels:
        return False
    # Current official Wan Animate 2 template subgraph widget order.
    vals[0] = 0
    vals[1] = PROMPT
    vals[2] = 1.0
    vals[3] = POSE_PROMPT
    vals[4] = 1.0
    vals[5] = 0.0
    vals[6] = 1.0
    vals[7] = False
    vals[8] = "cpu"  # cache on system RAM for 12 GB VRAM target
    vals[9] = "int8"
    vals[10] = False
    vals[11] = 384
    vals[12] = 576
    vals[13] = 42
    vals[14] = 17
    vals[15] = MODEL
    # vals[16] is the distillation LoRA selector. The actual LoRA loader is bypassed below.
    vals[17] = TEXT
    vals[18] = CLIPV
    vals[19] = VAE
    return True


def patch_node(node):
    name = node_name(node)
    vals = node.get("widgets_values")

    if name == "LoadImage" and isinstance(vals, list) and vals:
        vals[0] = MASTER
    elif name == "LoadVideo" and isinstance(vals, list) and vals:
        vals[0] = DRIVER
    elif name == "UNETLoader" and isinstance(vals, list) and vals:
        vals[0] = MODEL
    elif name == "CLIPLoader" and isinstance(vals, list) and vals:
        vals[0] = TEXT
    elif name == "CLIPVisionLoader" and isinstance(vals, list) and vals:
        vals[0] = CLIPV
    elif name == "VAELoader" and isinstance(vals, list) and vals:
        vals[0] = VAE
    elif name == "LoraLoaderModelOnly":
        # Bypass the step-distillation LoRA so this remains a Base-model validation.
        node["mode"] = 4
    elif name == "ModelSamplingSD3" and isinstance(vals, list) and vals:
        vals[0] = 5.0
    elif name == "BasicScheduler" and isinstance(vals, list) and len(vals) >= 3:
        vals[0] = "simple"
        vals[1] = 20
        vals[2] = 1.0
    elif name == "KSamplerSelect" and isinstance(vals, list) and vals:
        vals[0] = "euler"

    patch_top_level_motion_transfer(node)


def main():
    if len(sys.argv) != 3:
        raise SystemExit("usage: build_workflow.py <official_template.json> <output.json>")
    src = Path(sys.argv[1])
    dst = Path(sys.argv[2])
    data = json.loads(src.read_text(encoding="utf-8"))

    counts = {}
    for node in iter_nodes(data):
        name = str(node_name(node))
        counts[name] = counts.get(name, 0) + 1
        patch_node(node)

    required = ["LoadImage", "LoadVideo", "UNETLoader", "WanAnimate2ToVideo", "BasicScheduler", "KSamplerSelect"]
    missing = [n for n in required if counts.get(n, 0) == 0]
    if missing:
        raise SystemExit("official template structure changed; missing nodes: " + ", ".join(missing))

    dst.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote patched headless workflow: {dst}")
    print("Base settings: 384x576, 17 frames, seed 42, Euler, shift 5, 20 steps, no distillation LoRA.")


if __name__ == "__main__":
    main()
