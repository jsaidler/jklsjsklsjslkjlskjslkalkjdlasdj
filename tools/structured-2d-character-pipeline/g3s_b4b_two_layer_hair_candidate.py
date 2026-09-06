#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

EXPECTED_BODY_SIZE = (37, 128)
EXPECTED_BODY_RAW_RGBA_SHA256 = "818f0538a145917eac921ad708b3cdf30f87b2c76bc1413aa59305556af7f25c"
EXPECTED_BODY_PNG_SHA256 = "702e2d95325049b5d99ea66db4fbbb9b41d6d24813efb0b1c3a37e112b1c2858"

WORKING_CANVAS = (96, 160)
BODY_GROUND_Y = 152
BODY_X = (WORKING_CANVAS[0] - EXPECTED_BODY_SIZE[0]) // 2
BODY_Y = BODY_GROUND_Y - EXPECTED_BODY_SIZE[1]
GAMEPLAY_CANVAS = (640, 360)

# Compact black-hair ramp: warm-neutral black, readable at 1x.
OUTLINE = (3, 4, 6, 255)
DEEP = (7, 8, 11, 255)
BASE = (11, 12, 16, 255)
BASE2 = (16, 17, 21, 255)
MID = (22, 23, 28, 255)
MID2 = (29, 30, 35, 255)
HIGH = (39, 39, 44, 255)
HIGH2 = (50, 49, 53, 255)
PALETTE = [OUTLINE, DEEP, BASE, BASE2, MID, MID2, HIGH, HIGH2]


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def raw_rgba_sha256(im: Image.Image) -> str:
    return hashlib.sha256(im.convert("RGBA").tobytes()).hexdigest()


def checkerboard(size: tuple[int, int], tile: int = 8) -> Image.Image:
    out = Image.new("RGBA", size, (30, 30, 34, 255))
    d = ImageDraw.Draw(out)
    for y in range(0, size[1], tile):
        for x in range(0, size[0], tile):
            c = (38, 38, 42, 255) if ((x // tile + y // tile) & 1) == 0 else (55, 55, 60, 255)
            d.rectangle((x, y, x + tile - 1, y + tile - 1), fill=c)
    return out


def fit_inside(im: Image.Image, box: tuple[int, int]) -> Image.Image:
    bw, bh = box
    scale = min(bw / im.width, bh / im.height)
    return im.resize((max(1, round(im.width * scale)), max(1, round(im.height * scale))), Image.Resampling.LANCZOS)


def paste_center(dst: Image.Image, src: Image.Image, box: tuple[int, int, int, int]) -> None:
    x0, y0, x1, y1 = box
    dst.alpha_composite(src, (x0 + (x1 - x0 - src.width) // 2, y0 + (y1 - y0 - src.height) // 2))


def poly(d: ImageDraw.ImageDraw, pts, fill, outline=OUTLINE) -> None:
    d.polygon(pts, fill=fill, outline=outline)


def stroke(d: ImageDraw.ImageDraw, pts, fill, width: int = 1) -> None:
    d.line(pts, fill=fill, width=width)


def authored_rear_hair_v3() -> Image.Image:
    """New rear geometry. Intentionally asymmetric and dominant."""
    layer = Image.new("RGBA", WORKING_CANVAS, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    # Primary silhouette: left-heavy, irregular, long; not a centered bell/cape.
    outer = [
        (45, 15), (38, 16), (31, 20), (25, 26), (21, 34), (17, 44),
        (15, 55), (12, 68), (14, 80), (13, 92), (16, 104), (20, 118),
        (25, 126), (29, 119), (32, 109), (34, 98), (37, 89), (41, 81),
        (45, 76), (49, 78), (54, 84), (58, 94), (61, 104), (65, 116),
        (69, 110), (71, 99), (69, 88), (72, 76), (70, 64), (73, 53),
        (70, 41), (66, 31), (60, 22), (53, 17)
    ]
    poly(d, outer, DEEP)

    # Broad authored rear masses. They overlap to make a hierarchy rather than equal dreads.
    poly(d, [(34,18),(27,26),(22,38),(19,54),(19,70),(17,85),(20,101),(23,116),
             (28,111),(31,99),(30,85),(33,71),(31,56),(34,40),(39,27)], BASE)
    poly(d, [(43,16),(36,23),(33,34),(34,47),(31,62),(34,76),(32,91),(35,106),
             (39,98),(41,84),(39,69),(43,55),(41,42),(46,29),(49,19)], BASE2)
    poly(d, [(51,17),(47,25),(48,37),(45,50),(48,64),(46,77),(50,90),(49,103),
             (54,96),(56,82),(53,69),(57,55),(54,42),(59,29),(58,21)], BASE)
    poly(d, [(58,20),(61,28),(60,39),(64,50),(62,63),(66,75),(64,88),(68,101),
             (67,112),(63,104),(60,93),(61,80),(57,68),(59,54),(56,43),(60,31)], BASE2)

    # Side/back locks with distinct lengths and directions.
    poly(d, [(26,27),(20,35),(17,47),(16,58),(13,69),(15,78),(18,70),(21,60),(20,49),(24,39),(29,32)], BASE2)
    poly(d, [(29,47),(23,56),(21,68),(18,78),(19,91),(16,101),(19,113),(23,119),
             (24,108),(27,98),(25,86),(28,74),(26,62),(32,52)], BASE)
    poly(d, [(66,31),(70,40),(69,51),(72,61),(69,72),(71,83),(68,93),(70,103),
             (67,111),(64,102),(65,91),(62,81),(64,69),(61,58),(64,47),(61,39)], BASE)

    # Deliberate negative separations in the lower rear silhouette.
    for gap in [
        [(25,79),(28,82),(27,91),(29,97),(27,107),(24,113),(23,105),(25,96),(23,88)],
        [(38,73),(41,77),(40,85),(42,92),(40,101),(37,106),(37,97),(39,89),(37,81)],
        [(55,78),(58,82),(57,91),(60,99),(59,107),(56,111),(55,102),(57,94),(54,86)],
    ]:
        d.polygon(gap, fill=(0,0,0,0))

    # Coarse value accents: short, broken, non-parallel.
    stroke(d, [(25,31),(22,43),(23,55),(20,66)], HIGH, 1)
    stroke(d, [(31,26),(28,39),(30,52),(27,64)], MID2, 1)
    stroke(d, [(38,24),(36,36),(38,48)], HIGH2, 1)
    stroke(d, [(48,24),(46,36),(49,49)], MID2, 1)
    stroke(d, [(57,27),(60,39),(58,51)], HIGH, 1)
    stroke(d, [(65,38),(67,50),(65,61)], MID2, 1)
    stroke(d, [(19,83),(21,94),(19,104)], MID, 1)
    stroke(d, [(64,84),(67,95),(65,104)], MID, 1)

    # Messy edge tufts.
    poly(d, [(22,29),(17,27),(19,34),(14,36),(21,38)], BASE)
    poly(d, [(31,20),(27,16),(28,23),(23,22),(29,27)], BASE2)
    poly(d, [(58,21),(63,18),(61,25),(66,27),(60,29)], BASE)
    poly(d, [(69,46),(76,43),(72,50),(76,54),(69,55)], BASE2)
    return layer


def authored_front_hair_v3() -> Image.Image:
    """Sparse front framing: face, clavicle and torso remain readable."""
    layer = Image.new("RGBA", WORKING_CANVAS, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    # Crown/frame around the head, deliberately open in the center/front.
    poly(d, [(34,22),(38,17),(45,14),(53,16),(59,20),(63,26),(62,32),(58,36),
             (56,31),(53,26),(49,23),(44,24),(41,29),(38,35),(34,34),(31,29)], BASE)
    poly(d, [(37,22),(41,18),(47,17),(53,18),(58,22),(60,26),(59,30),(56,32),
             (54,27),(50,21),(44,21),(41,25),(39,31),(35,31),(34,27)], BASE2)

    # Viewer-left face/shoulder framing lock: broad but kept to side.
    poly(d, [(36,25),(32,34),(31,43),(33,51),(31,61),(33,70),(31,79),(34,86),
             (37,80),(36,70),(38,61),(36,52),(38,43),(39,34)], BASE2)
    stroke(d, [(35,31),(34,41),(35,50)], HIGH, 1)

    # Short inner lock near cheek/neck; stops above chest.
    poly(d, [(41,24),(39,31),(40,38),(39,45),(41,52),(43,47),(42,40),(44,33),(44,27)], BASE)
    stroke(d, [(41,29),(41,37),(41,44)], MID2, 1)

    # Viewer-right dominant side lock, but it stays lateral to the torso.
    poly(d, [(57,23),(61,31),(60,39),(63,47),(61,56),(64,64),(62,74),(65,82),
             (68,76),(66,66),(68,57),(65,48),(67,39),(63,31)], BASE2)
    stroke(d, [(60,29),(62,38),(61,47),(63,56)], HIGH, 1)

    # One long side lock crossing only the shoulder edge, not center chest/abdomen.
    poly(d, [(60,34),(64,41),(63,50),(66,59),(65,69),(68,77),(67,89),(64,96),
             (62,89),(63,79),(60,70),(62,60),(59,51),(61,43)], BASE)
    stroke(d, [(63,44),(64,53),(63,63)], MID2, 1)

    # A few broken tufts for wild silhouette.
    poly(d, [(32,25),(28,24),(30,29),(26,31),(33,32)], DEEP)
    poly(d, [(60,22),(65,20),(63,26),(68,27),(62,30)], BASE)
    poly(d, [(34,39),(30,42),(33,45),(29,49),(35,47)], BASE2)
    return layer


def body_work(body: Image.Image) -> Image.Image:
    out = Image.new("RGBA", WORKING_CANVAS, (0, 0, 0, 0))
    out.alpha_composite(body, (BODY_X, BODY_Y))
    return out


def composite_layers(body_layer: Image.Image, rear: Image.Image, front: Image.Image) -> Image.Image:
    out = Image.new("RGBA", WORKING_CANVAS, (0, 0, 0, 0))
    out.alpha_composite(rear)
    out.alpha_composite(body_layer)
    out.alpha_composite(front)
    return out


def gameplay_preview(composite: Image.Image) -> Image.Image:
    scene = Image.new("RGBA", GAMEPLAY_CANVAS, (18, 18, 21, 255))
    d = ImageDraw.Draw(scene)
    ground_y = 286
    d.rectangle((0, ground_y, GAMEPLAY_CANVAS[0], GAMEPLAY_CANVAS[1]), fill=(38, 31, 27, 255))
    bbox = composite.getchannel("A").getbbox()
    if bbox is None:
        raise RuntimeError("empty body+hair composite")
    crop = composite.crop(bbox)
    x = GAMEPLAY_CANVAS[0] // 2 - crop.width // 2
    y = ground_y - crop.height
    scene.alpha_composite(crop, (x, y))
    return scene


def opaque_count(im: Image.Image) -> int:
    return sum(1 for a in im.getchannel("A").getdata() if a)


def make_contact_sheet(master: Image.Image, rear: Image.Image, body_layer: Image.Image,
                       front: Image.Image, composite: Image.Image,
                       gameplay: Image.Image, out: Path) -> None:
    sheet = Image.new("RGBA", (1600, 900), (16, 16, 19, 255))
    d = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()
    d.text((24, 18), "G3S-B4B V3 AUTHORED TWO-LAYER HAIR REVIEW", fill=(238,238,242), font=font)
    d.text((24, 42), "V2 VISUAL FAIL CORRECTION: REAR-DOMINANT / ASYMMETRIC / SPARSE FRONT", fill=(220,180,90), font=font)
    d.text((24, 64), "COMPOSITION: rear_hair -> immutable body -> front_hair", fill=(220,220,225), font=font)

    d.text((24, 96), "A  MASTER / IDENTITY ONLY", fill=(220,220,225), font=font)
    mp = fit_inside(master, (390, 690))
    paste_center(sheet, mp, (20, 120, 430, 830))

    def panel(layer: Image.Image, title: str, x: int, y: int, scale: int = 3) -> None:
        d.text((x, y-24), title, fill=(220,220,225), font=font)
        bg = checkerboard(layer.size)
        bg.alpha_composite(layer)
        big = bg.resize((layer.width*scale, layer.height*scale), Image.Resampling.NEAREST)
        sheet.alpha_composite(big, (x, y))

    panel(rear, "B  rear_hair / V3 NEW", 470, 140)
    panel(front, "C  front_hair / V3 NEW", 790, 140)
    panel(composite, "D  COMPOSITE 3x", 1110, 140)

    d.text((470, 650), "E  NATIVE 640x360 GAMEPLAY PREVIEW", fill=(220,220,225), font=font)
    gp = gameplay.resize((640,360), Image.Resampling.NEAREST)
    sheet.alpha_composite(gp, (470, 680))

    d.text((1140, 650), "F  V3 STRUCTURAL CONTRACT", fill=(220,220,225), font=font)
    facts = [
        "rear_hair: dominant asymmetric new geometry",
        "body: canonical B3B V4 byte/pixel unchanged",
        "front_hair: sparse framing; center torso intentionally open",
        "master pixels used in hair layers: NO",
        "external paid API/model: NO",
        "automatic promotion: NO",
    ]
    yy = 684
    for fact in facts:
        d.text((1140, yy), fact, fill=(190,190,196), font=font)
        yy += 24

    sheet.convert("RGB").save(out, quality=95)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--master", required=True)
    ap.add_argument("--body", required=True)
    ap.add_argument("--preflight-meta", required=True)
    ap.add_argument("--workspace", required=True)
    args = ap.parse_args()

    master_path = Path(args.master)
    body_path = Path(args.body)
    preflight_meta_path = Path(args.preflight_meta)
    workspace = Path(args.workspace)
    workspace.mkdir(parents=True, exist_ok=True)

    for p in (master_path, body_path, preflight_meta_path):
        if not p.is_file():
            raise FileNotFoundError(p)

    body = Image.open(body_path).convert("RGBA")
    if body.size != EXPECTED_BODY_SIZE:
        raise RuntimeError(f"body size mismatch: got={body.size} expected={EXPECTED_BODY_SIZE}")
    if file_sha256(body_path) != EXPECTED_BODY_PNG_SHA256:
        raise RuntimeError("canonical body PNG SHA mismatch")
    if raw_rgba_sha256(body) != EXPECTED_BODY_RAW_RGBA_SHA256:
        raise RuntimeError("canonical body raw-RGBA SHA mismatch")

    preflight = json.loads(preflight_meta_path.read_text(encoding="utf-8"))
    expected_master_sha = preflight.get("master_sha256")
    if not expected_master_sha:
        raise RuntimeError("preflight metadata has no master_sha256")
    master_sha = file_sha256(master_path)
    if master_sha != expected_master_sha:
        raise RuntimeError(f"canonical master changed since B4A preflight: got={master_sha} expected={expected_master_sha}")
    master = Image.open(master_path).convert("RGBA")

    rear = authored_rear_hair_v3()
    front = authored_front_hair_v3()
    bw = body_work(body)
    comp = composite_layers(bw, rear, front)
    gameplay = gameplay_preview(comp)

    if opaque_count(rear) < 500:
        raise RuntimeError("rear_hair implausibly small")
    if opaque_count(front) < 120:
        raise RuntimeError("front_hair implausibly small")
    if opaque_count(front) >= opaque_count(rear):
        raise RuntimeError("V3 contract violated: front hair must not dominate rear hair")

    rear_path = workspace / "g3s_b4b_rear_hair_candidate.png"
    front_path = workspace / "g3s_b4b_front_hair_candidate.png"
    comp_path = workspace / "g3s_b4b_body_hair_composite.png"
    gameplay_path = workspace / "g3s_b4b_gameplay_preview.png"
    sheet_path = workspace / "g3s_b4b_contact_sheet.png"
    meta_path = workspace / "g3s_b4b_two_layer_hair_candidate.json"

    rear.save(rear_path)
    front.save(front_path)
    comp.save(comp_path)
    gameplay.save(gameplay_path)
    make_contact_sheet(master, rear, bw, front, comp, gameplay, sheet_path)

    meta = {
        "gate": "G3S-B4",
        "revision": "B4B_AUTHORED_TWO_LAYER_HAIR_V3",
        "status": "REVIEW_REQUIRED",
        "method": "new native-pixel authored hair geometry; master used only for identity inspiration",
        "working_canvas": list(WORKING_CANVAS),
        "body_anchor": {"x": BODY_X, "y": BODY_Y, "ground_y": BODY_GROUND_Y},
        "body_png_sha256": EXPECTED_BODY_PNG_SHA256,
        "body_raw_rgba_sha256": EXPECTED_BODY_RAW_RGBA_SHA256,
        "master_sha256": master_sha,
        "composition_order": ["rear_hair", "body", "front_hair"],
        "rear_hair_opaque_pixels": opaque_count(rear),
        "front_hair_opaque_pixels": opaque_count(front),
        "palette": [list(c) for c in PALETTE],
        "v2_visual_correction": [
            "rear mass is dominant and asymmetric",
            "front coverage reduced to lateral framing",
            "face/clavicle/center torso kept substantially open",
            "equal-width curtain/dread rhythm removed",
            "rear silhouette uses hierarchy of broad masses and irregular side locks"
        ],
        "automatic_promotion": False,
        "outputs": {
            "rear_hair": str(rear_path),
            "front_hair": str(front_path),
            "composite": str(comp_path),
            "gameplay_preview": str(gameplay_path),
            "contact_sheet": str(sheet_path)
        },
        "contact_sheet_sha256": file_sha256(sheet_path)
    }
    meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print("G3S-B4B V3: REVIEW PACKAGE READY")
    print(f"REAR:    {rear_path}")
    print(f"FRONT:   {front_path}")
    print(f"CONTACT: {sheet_path}")
    print(f"META:    {meta_path}")
    print("STOP. Share the contact sheet. Do not promote hair and do not start B5/C.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
