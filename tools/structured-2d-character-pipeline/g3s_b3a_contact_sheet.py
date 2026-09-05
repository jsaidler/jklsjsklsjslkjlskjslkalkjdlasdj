from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

BG = (18, 18, 22)
FG = (238, 238, 238)


def fit_panel(image: Image.Image, label: str, size=(640, 360), nearest=False) -> Image.Image:
    out = Image.new("RGB", size, BG)
    im = image.convert("RGBA")
    max_w, max_h = size[0] - 32, size[1] - 48
    scale = min(max_w / im.width, max_h / im.height)
    nw, nh = max(1, round(im.width * scale)), max(1, round(im.height * scale))
    resample = Image.Resampling.NEAREST if nearest else Image.Resampling.LANCZOS
    im = im.resize((nw, nh), resample)
    tmp = Image.new("RGBA", size, (*BG, 255))
    tmp.alpha_composite(im, ((size[0] - nw) // 2, 28 + (max_h - nh) // 2))
    out = tmp.convert("RGB")
    d = ImageDraw.Draw(out)
    d.rectangle([4, 4, size[0] - 4, 26], fill=(0, 0, 0))
    d.text((10, 9), label, fill=FG, font=ImageFont.load_default())
    return out


def crop_from_bbox(image: Image.Image, bbox, margin=10) -> Image.Image:
    x0, y0, x1, y1 = [int(round(v)) for v in bbox]
    x0 = max(0, x0 - margin)
    y0 = max(0, y0 - margin)
    x1 = min(image.width - 1, x1 + margin)
    y1 = min(image.height - 1, y1 + margin)
    return image.crop((x0, y0, x1 + 1, y1 + 1))


def info_panel(manifest: dict, size=(640, 360)) -> Image.Image:
    out = Image.new("RGB", size, BG)
    d = ImageDraw.Draw(out)
    font = ImageFont.load_default()
    d.rectangle([4, 4, size[0] - 4, 26], fill=(0, 0, 0))
    d.text((10, 9), "D structural + phenotype audit - GUIDE ONLY, NOT FINAL PIXEL ART", fill=FG, font=font)
    audit = manifest["layer_audit"]
    phenotype = manifest["phenotype_audit"]
    cam = manifest["camera"]
    lines = [
        "G3S-B3A establishes adult-female anatomy ownership only.",
        f"revision = {manifest['revision']}",
        f"gender_value = {phenotype['gender_value']} | resolved_gender = {phenotype['resolved_gender']}",
        f"age_value = {phenotype['age_value']} | life_stage = {phenotype['resolved_life_stage']}",
        f"female_targets = {phenotype['female_target_count']} | male_targets = {phenotype['male_target_count']}",
        f"adult_targets = {phenotype['adult_target_count']} | minor_targets = {phenotype['minor_target_count']}",
        "",
        f"complete_body_geometry = {audit['complete_body_geometry']}",
        f"hair_objects = {audit['hair_objects']}",
        f"clothing_objects = {audit['clothing_objects']}",
        f"restraint_objects = {audit['restraint_objects']}",
        f"chains_objects = {audit['chains_objects']}",
        f"visible_height_px = {cam['visible_height_px']}",
        f"pitch = {cam['pitch_deg']} deg | yaw = {cam['yaw_deg']} deg",
        "",
        "Nudity is not a separate runtime variant.",
        "NEXT AFTER REVIEW: author native 128x128 body source (B3-B).",
    ]
    y = 42
    for line in lines:
        d.text((24, y), line, fill=FG if not line.startswith("NEXT") else (255, 215, 90), font=font)
        y += 17
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    manifest_path = Path(args.manifest)
    out_path = Path(args.output)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("gate") != "G3S-B3-A-NUDE-ANATOMY-GUIDE":
        raise RuntimeError("Unexpected G3S-B3A manifest")
    if manifest.get("revision") != "G3S_B3A_NUDE_ANATOMY_GUIDE_V2":
        raise RuntimeError("Contact-sheet helper requires corrected G3S-B3A V2 manifest")
    phenotype = manifest.get("phenotype_audit") or {}
    if phenotype.get("resolved_gender") != "female" or int(phenotype.get("male_target_count", -1)) != 0:
        raise RuntimeError("Contact-sheet helper gender audit is not clean female")
    if phenotype.get("resolved_life_stage") != "adult" or int(phenotype.get("minor_target_count", -1)) != 0:
        raise RuntimeError("Contact-sheet helper life-stage audit is not clean adult")

    lit = Image.open(manifest["outputs"]["lit"]).convert("RGBA")
    mask = Image.open(manifest["outputs"]["mask"]).convert("RGBA")
    bbox = manifest["camera"]["projected_bbox"]
    zoom = crop_from_bbox(lit, bbox, margin=8)

    cells = [
        fit_panel(lit, "A complete adult female nude/hairless anatomy guide - NOT final art", nearest=False),
        fit_panel(mask, "B complete adult female body silhouette - no hair/clothing/restraints", nearest=True),
        fit_panel(zoom, "C adult female anatomy zoom - structural reference only", nearest=True),
        info_panel(manifest),
    ]
    sheet = Image.new("RGB", (1280, 720), BG)
    for cell, pos in zip(cells, [(0, 0), (640, 0), (0, 360), (640, 360)]):
        sheet.paste(cell, pos)
    sheet.save(out_path)
    print(f"G3S_B3A_CONTACT={out_path}")


if __name__ == "__main__":
    main()
