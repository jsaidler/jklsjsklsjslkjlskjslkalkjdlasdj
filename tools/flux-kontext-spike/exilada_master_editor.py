#!/usr/bin/env python3
"""Local iterative visual-direction editor for the Exilada canonical master.

This is an authoring tool, not a spritesheet runner. It talks to the already-installed
FLUX.1 Kontext ComfyUI instance and lets the user iteratively revise the character
master while preserving full-resolution renderer output and provenance.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import shutil
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from PIL import Image

try:
    import gradio as gr
except Exception as exc:  # pragma: no cover - launcher installs local dependency
    raise RuntimeError(
        "Gradio is not available. Use 54_run_exilada_master_editor.ps1 so the isolated UI dependencies are prepared."
    ) from exc

MODEL = "flux1-dev-kontext_fp8_scaled.safetensors"
CLIP_L = "clip_l.safetensors"
T5 = "t5xxl_fp16.safetensors"
VAE = "ae.safetensors"

CANONICAL_MASTER_REL = Path("assets/source/characters/exilada/reference/exilada_master.png")
CANONICAL_BODY_REL = Path(
    "assets/source/characters/exilada/reference/exilada_body_turnaround_nude_approved.jpg"
)
HISTORY_REL = Path("assets/source/characters/exilada/reference/history")
WORKING_REL = Path("assets/source/characters/exilada/reference/exilada_master_working.png")

DEFAULT_CLOTHING = (
    "Severely degraded asymmetrical captivity cloth, materially torn rather than designed as a costume. "
    "Use irregular holes, missing edges and displaced remnants; allow substantially more exposed torso and "
    "partial breast exposure where the torn-cloth geometry naturally causes it. The hip cloth is equally "
    "damaged, irregular and precarious. Avoid a neat bandeau, bikini, corset, armor-bikini or decorative fantasy outfit."
)

DEFAULT_BODY = (
    "Preserve the same mature adult woman and her approved natural adult anatomy: approximately 162 cm, lean, "
    "functional and resilient rather than bodybuilder-muscular; long adult torso and limbs; natural adult bust, "
    "hips, pelvis and legs; olive-to-brown skin; severe mature face. Do not enlarge the head, shorten the body, "
    "round the face, soften her into a cute design or otherwise juvenilize her."
)

DEFAULT_MATERIAL = (
    "Her condition must communicate enslavement, abandonment and deprivation: dirty skin, sweat, dust, old abrasions, "
    "frayed exhausted fabric, oxidized or battered restraints, broken chain evidence and no clean heroic equipment. "
    "Bare feet. Materials should feel physical, worn, tactile and causally damaged."
)

DEFAULT_ART = (
    "Push the image away from generic contemporary fantasy concept art. Give it a strong late-1970s/1980s adult "
    "sword-and-sorcery illustration charge: Heavy Metal, Conan and Red Sonja lineage; Frazetta/Julie Bell-like physical "
    "weight, danger, sensuality, pulp excess, dramatic anatomy and tactile skin/hair/cloth/metal, without copying a "
    "specific existing artwork or composition. The result must feel severe, erotic-capable, dangerous and lived-in, "
    "not sanitized, cute, glossy-MMO, cosplay-clean or generic RPG key art."
)

DEFAULT_EXTRA = (
    "Keep the character complete in frame from the top of the hair to both feet, with margin for the entire hair mass "
    "and broken chain fragments. Maintain a simple neutral authoring background. No weapon. No text, border, panel or UI."
)

BASE_LOCK = """Edit Image 1 as the current working master of the Exilada, an unambiguously adult fictional woman. Image 1 is authoritative for identity, overall proportions, pose family, hair identity and character continuity unless the user's explicit edit instruction changes a visible design detail.

If Image 2 is present, it is the approved nude anatomy turnaround of the SAME adult character. Use it only to recover or preserve body anatomy that is hidden by clothing in Image 1. Do not copy its multi-view sheet layout, duplicate the character or change Image 1 into a turnaround.

If later reference images are present, they are visual-direction references only. Borrow high-level pictorial qualities such as physical weight, silhouette severity, material treatment, dramatic adult sword-and-sorcery charge and palette logic. Do not copy a specific composition, character identity or distinctive protected design.

The goal is a revised CHARACTER MASTER, not a runtime sprite and not a tiny proxy. Preserve the renderer's full useful resolution. Do not pixelate, downscale to 128/192/384 pixels, make a spritesheet, add multiple poses, or place the character in a gameplay scene.
"""


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def sha256_file(path: os.PathLike[str] | str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def request_json(url: str, payload: dict[str, Any] | None = None, timeout: int = 60) -> Any:
    data = None
    headers = {"Accept": "application/json"}
    method = "GET"
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
        method = "POST"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code} from {url}: {body[:4000]}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Could not reach {url}: {exc}") from exc


def verify_comfy(base: str) -> None:
    request_json(base + "/system_stats", timeout=10)
    required = [
        "UNETLoader",
        "DualCLIPLoader",
        "VAELoader",
        "LoadImage",
        "FluxKontextImageScale",
        "VAEEncode",
        "CLIPTextEncode",
        "ConditioningZeroOut",
        "ReferenceLatent",
        "FluxGuidance",
        "KSampler",
        "VAEDecode",
        "SaveImage",
    ]
    for name in required:
        info = request_json(base + f"/object_info/{name}", timeout=30)
        if name not in info:
            raise RuntimeError(f"Required ComfyUI node is unavailable: {name}")


def normalize_upload(path: str, destination: Path) -> str:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(path) as im:
        if "A" in im.getbands():
            rgba = im.convert("RGBA")
            # Kontext authoring should not receive transparency as an accidental composition cue.
            bg = Image.new("RGBA", rgba.size, (112, 112, 112, 255))
            bg.alpha_composite(rgba)
            im2 = bg.convert("RGB")
        else:
            im2 = im.convert("RGB")
        im2.save(destination, format="PNG")
    return destination.name


def copy_to_comfy_input(path: str, comfy_root: Path, relative_name: str) -> str:
    target_dir = comfy_root / "input" / "roguelite_master_editor"
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / relative_name
    normalize_upload(path, target)
    return f"roguelite_master_editor/{target.name}"


def build_prompt_text(
    clothing: str,
    body: str,
    material: str,
    art_direction: str,
    extra: str,
    free_edit: str,
    body_ref_present: bool,
    style_ref_count: int,
) -> str:
    reference_note = []
    if body_ref_present:
        reference_note.append("Image 2 is present as the approved nude anatomy reference.")
    else:
        reference_note.append("No separate anatomy image is present; preserve visible adult anatomy from Image 1 conservatively.")
    if style_ref_count:
        first = 3 if body_ref_present else 2
        last = first + style_ref_count - 1
        if first == last:
            reference_note.append(f"Image {first} is a visual-direction reference only.")
        else:
            reference_note.append(f"Images {first} through {last} are visual-direction references only.")

    sections = [
        BASE_LOCK.strip(),
        "REFERENCE MAP:\n" + " ".join(reference_note),
        "BODY / IDENTITY LOCK:\n" + (body.strip() or DEFAULT_BODY),
        "CLOTHING DAMAGE / EXPOSURE:\n" + (clothing.strip() or DEFAULT_CLOTHING),
        "MATERIAL STATE / CAPTIVITY EVIDENCE:\n" + (material.strip() or DEFAULT_MATERIAL),
        "PICTORIAL DIRECTION:\n" + (art_direction.strip() or DEFAULT_ART),
        "COMPOSITION / AUTHORING REQUIREMENTS:\n" + (extra.strip() or DEFAULT_EXTRA),
    ]
    if free_edit.strip():
        sections.append("THIS ITERATION'S SPECIFIC CHANGE:\n" + free_edit.strip())
    sections.append(
        "HARD REJECTIONS: generic clean fantasy heroine; polished leather bikini; symmetric designed costume; modern fashion; "
        "MMO armor language; cute/chibi/adolescent proportions; doll-like face; glamour retouching; censorship garment added only "
        "to hide adult anatomy; accidental extra cloth; duplicated limbs; missing feet/hands; cropped hair; weapon; text; multiple characters."
    )
    return "\n\n".join(sections)


def build_api_prompt(
    master_input: str,
    reference_inputs: list[str],
    prompt_text: str,
    output_prefix: str,
    seed: int,
    steps: int,
    guidance: float,
    denoise: float,
) -> dict[str, Any]:
    prompt: dict[str, Any] = {
        "1": {"inputs": {"unet_name": MODEL, "weight_dtype": "default"}, "class_type": "UNETLoader"},
        "2": {
            "inputs": {
                "clip_name1": CLIP_L,
                "clip_name2": T5,
                "type": "flux",
                "device": "default",
            },
            "class_type": "DualCLIPLoader",
        },
        "3": {"inputs": {"vae_name": VAE}, "class_type": "VAELoader"},
        "4": {"inputs": {"image": master_input}, "class_type": "LoadImage"},
        "5": {"inputs": {"image": ["4", 0]}, "class_type": "FluxKontextImageScale"},
        "6": {"inputs": {"pixels": ["5", 0], "vae": ["3", 0]}, "class_type": "VAEEncode"},
        "10": {"inputs": {"text": prompt_text, "clip": ["2", 0]}, "class_type": "CLIPTextEncode"},
        "11": {"inputs": {"conditioning": ["10", 0]}, "class_type": "ConditioningZeroOut"},
    }

    # Master is the first structural/identity reference and also the init latent.
    cond: list[Any] = ["10", 0]
    next_id = 12
    prompt[str(next_id)] = {
        "inputs": {"conditioning": cond, "latent": ["6", 0]},
        "class_type": "ReferenceLatent",
    }
    cond = [str(next_id), 0]
    next_id += 1

    for idx, ref_name in enumerate(reference_inputs):
        load_id = next_id
        scale_id = next_id + 1
        encode_id = next_id + 2
        ref_id = next_id + 3
        prompt[str(load_id)] = {"inputs": {"image": ref_name}, "class_type": "LoadImage"}
        prompt[str(scale_id)] = {
            "inputs": {"image": [str(load_id), 0]},
            "class_type": "FluxKontextImageScale",
        }
        prompt[str(encode_id)] = {
            "inputs": {"pixels": [str(scale_id), 0], "vae": ["3", 0]},
            "class_type": "VAEEncode",
        }
        prompt[str(ref_id)] = {
            "inputs": {"conditioning": cond, "latent": [str(encode_id), 0]},
            "class_type": "ReferenceLatent",
        }
        cond = [str(ref_id), 0]
        next_id += 4

    guidance_id = next_id
    sampler_id = next_id + 1
    decode_id = next_id + 2
    save_id = next_id + 3
    prompt[str(guidance_id)] = {
        "inputs": {"conditioning": cond, "guidance": float(guidance)},
        "class_type": "FluxGuidance",
    }
    prompt[str(sampler_id)] = {
        "inputs": {
            "seed": int(seed),
            "steps": int(steps),
            "cfg": 1.0,
            "sampler_name": "euler",
            "scheduler": "simple",
            "denoise": float(denoise),
            "model": ["1", 0],
            "positive": [str(guidance_id), 0],
            "negative": ["11", 0],
            "latent_image": ["6", 0],
        },
        "class_type": "KSampler",
    }
    prompt[str(decode_id)] = {
        "inputs": {"samples": [str(sampler_id), 0], "vae": ["3", 0]},
        "class_type": "VAEDecode",
    }
    prompt[str(save_id)] = {
        "inputs": {"filename_prefix": output_prefix, "images": [str(decode_id), 0]},
        "class_type": "SaveImage",
    }
    return prompt


def wait_for_output(base: str, prompt_id: str, comfy_root: Path, timeout_minutes: int) -> tuple[Path, dict[str, Any]]:
    deadline = time.time() + timeout_minutes * 60
    last_status: dict[str, Any] = {}
    while time.time() < deadline:
        history = request_json(base + f"/history/{prompt_id}", timeout=30)
        item = history.get(prompt_id)
        if item:
            last_status = item.get("status") or {}
            outputs = item.get("outputs") or {}
            for node_output in outputs.values():
                for image in node_output.get("images") or []:
                    filename = image.get("filename")
                    if not filename:
                        continue
                    image_type = image.get("type", "output")
                    subfolder = image.get("subfolder") or ""
                    root = comfy_root / ("output" if image_type == "output" else image_type)
                    candidate = root / subfolder / filename
                    if candidate.is_file():
                        return candidate, last_status
            status_text = json.dumps(last_status, ensure_ascii=False).lower()
            if "error" in status_text:
                raise RuntimeError(f"ComfyUI reported an error for prompt {prompt_id}: {last_status}")
        time.sleep(2)
    raise TimeoutError(f"Timed out after {timeout_minutes} minutes waiting for ComfyUI prompt {prompt_id}")


def submit_prompt(base: str, prompt: dict[str, Any], comfy_root: Path, timeout_minutes: int) -> tuple[str, float, Path, dict[str, Any]]:
    started = time.time()
    result = request_json(base + "/prompt", {"prompt": prompt}, timeout=60)
    prompt_id = result.get("prompt_id")
    if not prompt_id:
        raise RuntimeError(f"ComfyUI did not return a prompt_id: {result}")
    output, status = wait_for_output(base, prompt_id, comfy_root, timeout_minutes)
    return prompt_id, time.time() - started, output, status


def copy_result(source: Path, run_dir: Path) -> Path:
    run_dir.mkdir(parents=True, exist_ok=True)
    target = run_dir / "candidate.png"
    shutil.copy2(source, target)
    return target


def ensure_path(path: str | None, label: str) -> str:
    if not path:
        raise ValueError(f"{label} is required")
    if not os.path.isfile(path):
        raise ValueError(f"{label} does not exist: {path}")
    return path


def build_ui(args: argparse.Namespace) -> gr.Blocks:
    project_root = Path(args.project_root).resolve()
    comfy_root = Path(args.comfy_root).resolve()
    workspace = Path(args.workspace).resolve()
    run_root = workspace / "master_editor" / "runs"
    canonical_master = project_root / CANONICAL_MASTER_REL
    canonical_body = project_root / CANONICAL_BODY_REL
    history_dir = project_root / HISTORY_REL
    working_copy = project_root / WORKING_REL
    base = f"http://127.0.0.1:{args.port}"

    verify_comfy(base)
    if not canonical_master.is_file():
        raise FileNotFoundError(f"Canonical Exilada master missing: {canonical_master}")

    def generate(
        working_master: str | None,
        use_body_reference: bool,
        body_reference_upload: str | None,
        style_reference_1: str | None,
        style_reference_2: str | None,
        clothing: str,
        body: str,
        material: str,
        art_direction: str,
        extra: str,
        free_edit: str,
        seed: float,
        steps: float,
        guidance: float,
        denoise: float,
    ):
        try:
            verify_comfy(base)
            source_path = ensure_path(working_master or str(canonical_master), "Working master")
            stamp = utc_stamp()
            run_dir = run_root / stamp
            run_dir.mkdir(parents=True, exist_ok=False)

            master_input = copy_to_comfy_input(source_path, comfy_root, f"{stamp}_master.png")
            refs: list[str] = []
            ref_records: list[dict[str, Any]] = []
            body_ref_present = False

            body_source: str | None = None
            if body_reference_upload:
                body_source = body_reference_upload
            elif use_body_reference and canonical_body.is_file():
                body_source = str(canonical_body)
            if body_source:
                body_source = ensure_path(body_source, "Body/anatomy reference")
                body_ref_present = True
                name = copy_to_comfy_input(body_source, comfy_root, f"{stamp}_body_reference.png")
                refs.append(name)
                ref_records.append(
                    {"role": "body_anatomy", "source": body_source, "sha256": sha256_file(body_source)}
                )

            style_sources = [p for p in [style_reference_1, style_reference_2] if p]
            for idx, style_source in enumerate(style_sources, start=1):
                style_source = ensure_path(style_source, f"Style reference {idx}")
                name = copy_to_comfy_input(style_source, comfy_root, f"{stamp}_style_reference_{idx}.png")
                refs.append(name)
                ref_records.append(
                    {"role": f"visual_direction_{idx}", "source": style_source, "sha256": sha256_file(style_source)}
                )

            final_prompt = build_prompt_text(
                clothing=clothing,
                body=body,
                material=material,
                art_direction=art_direction,
                extra=extra,
                free_edit=free_edit,
                body_ref_present=body_ref_present,
                style_ref_count=len(style_sources),
            )
            seed_i = int(seed)
            steps_i = int(steps)
            output_prefix = f"roguelite_master_editor/{stamp}/exilada_master_candidate"
            api_prompt = build_api_prompt(
                master_input=master_input,
                reference_inputs=refs,
                prompt_text=final_prompt,
                output_prefix=output_prefix,
                seed=seed_i,
                steps=steps_i,
                guidance=float(guidance),
                denoise=float(denoise),
            )
            prompt_json = run_dir / "comfyui_api_prompt.json"
            prompt_json.write_text(json.dumps(api_prompt, ensure_ascii=False, indent=2), encoding="utf-8")

            prompt_id, elapsed, generated, history_status = submit_prompt(
                base, api_prompt, comfy_root, args.timeout_minutes
            )
            candidate = copy_result(generated, run_dir)
            with Image.open(candidate) as im:
                output_size = list(im.size)

            manifest = {
                "gate": "EXILADA_MASTER_LOCAL_VISUAL_REVISION",
                "status": "CANDIDATE_GENERATED",
                "created_utc": datetime.now(timezone.utc).isoformat(),
                "source_master": source_path,
                "source_master_sha256": sha256_file(source_path),
                "references": ref_records,
                "model": MODEL,
                "steps": steps_i,
                "guidance": float(guidance),
                "cfg": 1.0,
                "sampler": "euler",
                "scheduler": "simple",
                "denoise": float(denoise),
                "seed": seed_i,
                "prompt_id": prompt_id,
                "elapsed_seconds": elapsed,
                "prompt": final_prompt,
                "api_prompt": str(prompt_json),
                "candidate": str(candidate),
                "candidate_sha256": sha256_file(candidate),
                "output_size": output_size,
                "resolution_policy": "KEEP_NATIVE_KONTEXT_OUTPUT_NO_128_192_384_DOWNSCALE",
                "history_status": history_status,
                "approval": "PENDING_USER_REVIEW",
            }
            manifest_path = run_dir / "manifest.json"
            manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
            status = (
                f"Candidato gerado em {elapsed:.1f}s | {output_size[0]}×{output_size[1]} | seed {seed_i}\n"
                f"Arquivo: {candidate}\nManifesto: {manifest_path}"
            )
            return str(candidate), str(candidate), str(manifest_path), final_prompt, status
        except Exception as exc:
            return None, None, None, "", f"ERRO: {type(exc).__name__}: {exc}"

    def use_candidate(candidate_path: str | None):
        if not candidate_path or not os.path.isfile(candidate_path):
            return gr.update(), "Nenhum candidato válido para usar como nova entrada."
        working_copy.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(candidate_path, working_copy)
        return str(working_copy), f"Working master atualizado: {working_copy}"

    def approve_candidate(candidate_path: str | None, manifest_path: str | None):
        if not candidate_path or not os.path.isfile(candidate_path):
            return "Nenhum candidato válido para aprovar."
        history_dir.mkdir(parents=True, exist_ok=True)
        stamp = utc_stamp()
        if canonical_master.is_file():
            backup = history_dir / f"exilada_master_before_{stamp}.png"
            shutil.copy2(canonical_master, backup)
        else:
            backup = None
        shutil.copy2(candidate_path, canonical_master)
        approval = {
            "approved_utc": datetime.now(timezone.utc).isoformat(),
            "approved_candidate": candidate_path,
            "approved_candidate_sha256": sha256_file(candidate_path),
            "canonical_master": str(canonical_master),
            "canonical_master_sha256": sha256_file(canonical_master),
            "previous_master_backup": str(backup) if backup else None,
            "source_manifest": manifest_path if manifest_path and os.path.isfile(manifest_path) else None,
        }
        approval_path = history_dir / f"exilada_master_approval_{stamp}.json"
        approval_path.write_text(json.dumps(approval, ensure_ascii=False, indent=2), encoding="utf-8")
        return (
            f"NOVO MASTER APROVADO explicitamente.\n{canonical_master}\n"
            f"SHA256: {approval['canonical_master_sha256']}\nBackup anterior: {backup}\nRegistro: {approval_path}"
        )

    def randomize_seed() -> int:
        return random.SystemRandom().randint(0, 2**31 - 1)

    with gr.Blocks(title="Roguelite — Exilada Master Editor") as demo:
        gr.Markdown(
            "# Exilada — editor local do master\n"
            "Ferramenta de direção visual para revisar **a personagem-base**, antes de continuar animação/sprites. "
            "Nada aqui reduz a personagem para 128/192/384 px. O resultado nativo do Kontext é preservado."
        )
        with gr.Row():
            with gr.Column(scale=1):
                working_master = gr.Image(
                    label="Working master (Image 1)",
                    value=str(canonical_master),
                    type="filepath",
                    sources=["upload"],
                )
                use_body = gr.Checkbox(
                    label="Usar turnaround nu aprovado como referência anatômica, se disponível",
                    value=canonical_body.is_file(),
                )
                body_ref = gr.Image(label="Ou carregar outra referência anatômica (Image 2)", type="filepath")
                style_ref1 = gr.Image(label="Referência visual 1 (opcional)", type="filepath")
                style_ref2 = gr.Image(label="Referência visual 2 (opcional)", type="filepath")
            with gr.Column(scale=2):
                clothing = gr.Textbox(label="Roupa / rasgos / exposição", value=DEFAULT_CLOTHING, lines=5)
                body = gr.Textbox(label="Corpo / identidade", value=DEFAULT_BODY, lines=4)
                material = gr.Textbox(label="Material / sujeira / cativeiro", value=DEFAULT_MATERIAL, lines=4)
                art = gr.Textbox(label="Direção pictórica", value=DEFAULT_ART, lines=5)
                extra = gr.Textbox(label="Composição do master", value=DEFAULT_EXTRA, lines=3)
                free_edit = gr.Textbox(
                    label="Mudança específica desta tentativa",
                    placeholder="Ex.: ampliar o rasgo no lado esquerdo do peito, deslocar o pano para baixo, tornar o rosto mais severo...",
                    lines=4,
                )

        with gr.Row():
            seed = gr.Number(label="Seed", value=0, precision=0)
            random_seed = gr.Button("Seed aleatório")
            steps = gr.Slider(label="Steps", minimum=12, maximum=40, value=20, step=1)
            guidance = gr.Slider(label="Guidance", minimum=1.5, maximum=5.0, value=2.5, step=0.1)
            denoise = gr.Slider(
                label="Denoise / intensidade da revisão",
                minimum=0.15,
                maximum=0.70,
                value=0.38,
                step=0.01,
            )

        generate_btn = gr.Button("Gerar candidato local", variant="primary")
        with gr.Row():
            candidate = gr.Image(label="Candidato", type="filepath")
            with gr.Column():
                status = gr.Textbox(label="Estado", lines=7, interactive=False)
                final_prompt = gr.Textbox(label="Prompt efetivamente enviado", lines=15, interactive=False)
                use_btn = gr.Button("Usar candidato como nova entrada")
                approve_btn = gr.Button("APROVAR candidato como novo exilada_master.png")
                approval_status = gr.Textbox(label="Aprovação / versionamento", lines=7, interactive=False)

        candidate_state = gr.State(value=None)
        manifest_state = gr.State(value=None)

        random_seed.click(randomize_seed, inputs=[], outputs=[seed])
        generate_btn.click(
            generate,
            inputs=[
                working_master,
                use_body,
                body_ref,
                style_ref1,
                style_ref2,
                clothing,
                body,
                material,
                art,
                extra,
                free_edit,
                seed,
                steps,
                guidance,
                denoise,
            ],
            outputs=[candidate, candidate_state, manifest_state, final_prompt, status],
        )
        use_btn.click(use_candidate, inputs=[candidate_state], outputs=[working_master, approval_status])
        approve_btn.click(
            approve_candidate,
            inputs=[candidate_state, manifest_state],
            outputs=[approval_status],
        )

    return demo


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project-root", required=True)
    ap.add_argument("--workspace", required=True)
    ap.add_argument("--comfy-root", required=True)
    ap.add_argument("--port", type=int, default=8191)
    ap.add_argument("--ui-port", type=int, default=7860)
    ap.add_argument("--timeout-minutes", type=int, default=180)
    args = ap.parse_args()

    demo = build_ui(args)
    demo.queue(default_concurrency_limit=1)
    demo.launch(
        server_name="127.0.0.1",
        server_port=args.ui_port,
        share=False,
        inbrowser=True,
        show_error=True,
    )


if __name__ == "__main__":
    main()
