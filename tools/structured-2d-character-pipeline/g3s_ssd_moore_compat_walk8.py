#!/usr/bin/env python3
from __future__ import annotations

import gc
import json
import sys
from pathlib import Path

import numpy as np
import torch
from diffusers import AutoencoderKL, DDIMScheduler
from omegaconf import OmegaConf
from PIL import Image
from transformers import CLIPVisionModelWithProjection


def fail(message: str) -> None:
    raise RuntimeError(message)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def save_review(frames: list[Image.Image], output_root: Path) -> tuple[Path, Path]:
    if len(frames) != 8:
        fail(f"expected 8 frames for review, got {len(frames)}")
    output_root.mkdir(parents=True, exist_ok=True)
    w, h = frames[0].size
    sheet = Image.new("RGB", (w * 4, h * 2))
    for i, frame in enumerate(frames):
        sheet.paste(frame, ((i % 4) * w, (i // 4) * h))
    sheet_path = output_root / "exilada_walk8_moore_compat_contact_sheet.png"
    sheet.save(sheet_path)

    gif_path = output_root / "exilada_walk8_moore_compat.gif"
    frames[0].save(
        gif_path,
        save_all=True,
        append_images=frames[1:],
        duration=125,
        loop=0,
        disposal=2,
        optimize=False,
    )
    return sheet_path, gif_path


def main() -> int:
    if len(sys.argv) != 2:
        fail("usage: g3s_ssd_moore_compat_walk8.py <request.json>")

    request_path = Path(sys.argv[1]).resolve()
    req = load_json(request_path)

    moore_root = Path(req["moore_root"]).resolve()
    model_training = Path(req["model_training"]).resolve()
    input_marker = Path(req["input_marker"]).resolve()
    output_root = Path(req["output_root"]).resolve()
    result_marker = Path(req["result_marker"]).resolve()

    if not moore_root.is_dir():
        fail(f"Moore-AnimateAnyone source missing: {moore_root}")
    if not model_training.is_dir():
        fail(f"SSD ModelTraining missing: {model_training}")
    if not input_marker.is_file():
        fail(f"prepared walk8 input marker missing: {input_marker}")

    prepared = load_json(input_marker)
    if prepared.get("status") != "PASS":
        fail("walk8 input marker is not PASS")
    if int(prepared.get("target_pose_count", 0)) != 8:
        fail("walk8 input marker does not contain exactly 8 target poses")

    master = Path(prepared["master"]).resolve()
    pose_paths = [Path(row["path"]).resolve() for row in prepared["poses"]]
    if not master.is_file():
        fail(f"Exilada master missing: {master}")
    if len(pose_paths) != 8 or any(not p.is_file() for p in pose_paths):
        fail("one or more prepared target pose maps are missing")

    pretrained = model_training / "pretrained_model"
    base_model = pretrained / "stable-diffusion-v1-5"
    vae_path = pretrained / "sd-vae-ft-mse"
    image_encoder_path = pretrained / "image_encoder"
    denoising_path = pretrained / "denoising_unet.pth"
    reference_path = pretrained / "reference_unet.pth"
    pose_guider_path = pretrained / "pose_guider.pth"
    motion_module_path = pretrained / "motion_module.pth"
    inference_config_path = moore_root / "configs" / "inference" / "inference_v2.yaml"

    for required in (
        base_model / "unet" / "config.json",
        vae_path / "config.json",
        image_encoder_path / "config.json",
        denoising_path,
        reference_path,
        pose_guider_path,
        motion_module_path,
        inference_config_path,
    ):
        if not required.exists():
            fail(f"required model/source asset missing: {required}")

    # The exact upstream SSD Python graph expects a custom multi-scale PoseGuider
    # checkpoint that the authors never released. This fallback deliberately uses
    # Moore-AnimateAnyone's original PoseGuider graph with the released SSD
    # fine-tuned denoising/reference UNets. Keep the distinction explicit.
    pose_state = torch.load(pose_guider_path, map_location="cpu")
    pose_keys = set(pose_state.keys())
    if not {"conv_in.weight", "conv_in.bias", "conv_out.weight", "conv_out.bias"}.issubset(pose_keys):
        fail("pose_guider.pth is not the expected Moore/AnimateAnyone baseline checkpoint")
    if any(k.startswith("conv_layers.") for k in pose_keys):
        fail("pose_guider.pth looks like the unreleased SSD custom architecture; fallback route should be reviewed")
    del pose_state
    gc.collect()

    sys.path.insert(0, str(moore_root))
    from src.models.pose_guider import PoseGuider  # noqa: E402
    from src.models.unet_2d_condition import UNet2DConditionModel  # noqa: E402
    from src.models.unet_3d import UNet3DConditionModel  # noqa: E402
    from src.pipelines.pipeline_pose2vid import Pose2VideoPipeline  # noqa: E402

    if not torch.cuda.is_available():
        fail("CUDA is not available in the ssd environment")

    torch.cuda.empty_cache()
    weight_dtype = torch.float16

    print("SSD-MOORE-COMPAT: loading models...")
    vae = AutoencoderKL.from_pretrained(str(vae_path)).to("cuda", dtype=weight_dtype)
    reference_unet = UNet2DConditionModel.from_pretrained(
        str(base_model), subfolder="unet"
    ).to(dtype=weight_dtype, device="cuda")

    infer_cfg = OmegaConf.load(str(inference_config_path))
    denoising_unet = UNet3DConditionModel.from_pretrained_2d(
        str(base_model),
        str(motion_module_path),
        subfolder="unet",
        unet_additional_kwargs=OmegaConf.to_container(infer_cfg.unet_additional_kwargs),
    ).to(dtype=weight_dtype, device="cuda")

    pose_guider = PoseGuider(
        320, block_out_channels=(16, 32, 96, 256)
    ).to(dtype=weight_dtype, device="cuda")

    image_enc = CLIPVisionModelWithProjection.from_pretrained(
        str(image_encoder_path)
    ).to(dtype=weight_dtype, device="cuda")

    scheduler = DDIMScheduler(**OmegaConf.to_container(infer_cfg.noise_scheduler_kwargs))

    print("SSD-MOORE-COMPAT: verifying released SSD UNets against Moore graph...")
    den_state = torch.load(denoising_path, map_location="cpu")
    missing, unexpected = denoising_unet.load_state_dict(den_state, strict=False)
    # Moore's own inference loads denoising with strict=False. Unexpected keys
    # indicate a graph incompatibility and are not acceptable for this fallback.
    if unexpected:
        fail(f"SSD denoising UNet has unexpected Moore keys: {unexpected[:12]}")
    del den_state

    ref_state = torch.load(reference_path, map_location="cpu")
    reference_unet.load_state_dict(ref_state, strict=True)
    del ref_state

    pose_state = torch.load(pose_guider_path, map_location="cpu")
    pose_guider.load_state_dict(pose_state, strict=True)
    del pose_state
    gc.collect()

    print(f"SSD-MOORE-COMPAT: denoising missing keys accepted by Moore strict=False: {len(missing)}")

    pipe = Pose2VideoPipeline(
        vae=vae,
        image_encoder=image_enc,
        reference_unet=reference_unet,
        denoising_unet=denoising_unet,
        pose_guider=pose_guider,
        scheduler=scheduler,
    ).to("cuda", dtype=weight_dtype)

    ref_image = Image.open(master).convert("RGB")
    pose_images = [Image.open(p).convert("RGB") for p in pose_paths]
    generator = torch.manual_seed(42)

    print("SSD-MOORE-COMPAT: generating 8 frames at 512x512 / 25 steps / CFG 3.5...")
    try:
        video = pipe(
            ref_image,
            pose_images,
            512,
            512,
            8,
            25,
            3.5,
            generator=generator,
        ).videos
    except RuntimeError as exc:
        if "out of memory" in str(exc).lower():
            torch.cuda.empty_cache()
            fail("CUDA OOM during Moore-compatible 8x512 inference on RTX 3060 12 GB")
        raise

    if not isinstance(video, torch.Tensor):
        video = torch.from_numpy(video)
    if tuple(video.shape[:3]) != (1, 3, 8):
        fail(f"unexpected generated tensor shape: {tuple(video.shape)}")

    frames_dir = output_root / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)
    frames: list[Image.Image] = []
    frame_paths: list[str] = []
    for i in range(8):
        arr = video[0, :, i].permute(1, 2, 0).clamp(0, 1).cpu().numpy()
        arr = np.rint(arr * 255.0).astype(np.uint8)
        im = Image.fromarray(arr, mode="RGB")
        path = frames_dir / f"frame_{i+1:03d}.png"
        im.save(path)
        frames.append(im)
        frame_paths.append(str(path))

    sheet_path, gif_path = save_review(frames, output_root)

    result = {
        "gate": "SSD_EXILADA_WALK8_MOORE_COMPAT",
        "status": "PASS_OUTPUT_READY_FOR_VISUAL_QA",
        "route": "MOORE_ANIMATEANYONE_GRAPH_WITH_RELEASED_SSD_DENOISING_REFERENCE_UNETS",
        "exact_upstream_ssd": False,
        "reason": "upstream SSD custom multi-scale pose_guider.pth was not publicly released",
        "moore_commit": req.get("moore_commit"),
        "master": str(master),
        "pose_count": 8,
        "frames": frame_paths,
        "contact_sheet": str(sheet_path),
        "gif": str(gif_path),
        "resolution": [512, 512],
        "steps": 25,
        "cfg": 3.5,
        "seed": 42,
        "visual_qa_required": True,
    }
    result_marker.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    print("SSD-MOORE-COMPAT: OUTPUT READY FOR VISUAL QA")
    print(f"FRAMES: {frames_dir}")
    print(f"SHEET:  {sheet_path}")
    print(f"GIF:    {gif_path}")
    print(f"MARKER: {result_marker}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"SSD-MOORE-COMPAT: FAIL - {exc}")
        raise SystemExit(1)
