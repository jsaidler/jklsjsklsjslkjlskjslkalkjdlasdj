#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import deque
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

EXPECTED_BODY_SIZE = (37, 128)
EXPECTED_BODY_RAW_RGBA_SHA256 = "818f0538a145917eac921ad708b3cdf30f87b2c76bc1413aa59305556af7f25c"
EXPECTED_BODY_PNG_SHA256 = "702e2d95325049b5d99ea66db4fbbb9b41d6d24813efb0b1c3a37e112b1c2858"
WORKING_CANVAS = (96, 160)
BODY_GROUND_Y = 152
BODY_X = (WORKING_CANVAS[0] - EXPECTED_BODY_SIZE[0]) // 2
BODY_Y = BODY_GROUND_Y - EXPECTED_BODY_SIZE[1]


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def raw_rgba_sha256(im: Image.Image) -> str:
    return hashlib.sha256(im.convert("RGBA").tobytes()).hexdigest()


def median(values: list[float]) -> float:
    vals = sorted(values)
    if not vals:
        raise RuntimeError("median of empty list")
    n = len(vals)
    if n & 1:
        return vals[n // 2]
    return (vals[n // 2 - 1] + vals[n // 2]) / 2.0


def percentile(values: list[float], p: float) -> float:
    vals = sorted(values)
    if not vals:
        raise RuntimeError("percentile of empty list")
    i = max(0, min(len(vals) - 1, round((len(vals) - 1) * p)))
    return vals[i]


def rgb_distance(a: tuple[int, int, int], b: tuple[float, float, float]) -> float:
    return math.sqrt(sum((float(a[i]) - b[i]) ** 2 for i in range(3)))


def luma(rgb: tuple[int, int, int]) -> float:
    r, g, b = rgb
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def checkerboard(size: tuple[int, int], tile: int = 8) -> Image.Image:
    out = Image.new("RGBA", size, (30, 30, 34, 255))
    draw = ImageDraw.Draw(out)
    for y in range(0, size[1], tile):
        for x in range(0, size[0], tile):
            c = (38, 38, 42, 255) if ((x // tile + y // tile) & 1) == 0 else (55, 55, 60, 255)
            draw.rectangle((x, y, x + tile - 1, y + tile - 1), fill=c)
    return out


def foreground_mask(im: Image.Image) -> Image.Image:
    rgb = im.convert("RGB")
    w, h = rgb.size
    px = rgb.load()
    k = max(4, min(w, h) // 40)
    samples: list[tuple[int, int, int]] = []
    for yy in list(range(k)) + list(range(max(0, h - k), h)):
        for xx in list(range(k)) + list(range(max(0, w - k), w)):
            samples.append(px[xx, yy])
    bg = tuple(median([s[i] for s in samples]) for i in range(3))
    mask = Image.new("L", (w, h), 0)
    mp = mask.load()
    for y in range(h):
        for x in range(w):
            if rgb_distance(px[x, y], bg) > 22.0:
                mp[x, y] = 255
    return mask


def mask_bbox(mask: Image.Image) -> tuple[int, int, int, int]:
    bbox = mask.getbbox()
    if bbox is None:
        raise RuntimeError("empty mask")
    return bbox


def skin_mask(master: Image.Image, fg: Image.Image) -> Image.Image:
    rgb = master.convert("RGB")
    w, h = rgb.size
    rp = rgb.load()
    fp = fg.load()
    out = Image.new("L", (w, h), 0)
    op = out.load()
    for y in range(h):
        for x in range(w):
            if not fp[x, y]:
                continue
            r, g, b = rp[x, y]
            lum = luma((r, g, b))
            # Warm olive/brown skin; intentionally rejects near-neutral gray bg and beige cloth.
            if lum >= 34 and r >= g + 10 and g >= b + 2 and r >= b + 24:
                op[x, y] = 255
    return out


def connected_components(mask: Image.Image) -> list[list[tuple[int, int]]]:
    w, h = mask.size
    mp = mask.load()
    seen = bytearray(w * h)
    comps: list[list[tuple[int, int]]] = []
    nbrs = [(-1,-1),(0,-1),(1,-1),(-1,0),(1,0),(-1,1),(0,1),(1,1)]
    for y in range(h):
        for x in range(w):
            idx = y * w + x
            if seen[idx] or not mp[x, y]:
                continue
            q = deque([(x, y)])
            seen[idx] = 1
            comp: list[tuple[int, int]] = []
            while q:
                cx, cy = q.popleft()
                comp.append((cx, cy))
                for dx, dy in nbrs:
                    nx, ny = cx + dx, cy + dy
                    if nx < 0 or ny < 0 or nx >= w or ny >= h:
                        continue
                    ni = ny * w + nx
                    if seen[ni] or not mp[nx, ny]:
                        continue
                    seen[ni] = 1
                    q.append((nx, ny))
            comps.append(comp)
    return comps


def derive_hair_mask(master: Image.Image, fg: Image.Image, skin: Image.Image) -> tuple[Image.Image, dict[str, float]]:
    skin_bbox = skin.getbbox()
    if skin_bbox is None:
        raise RuntimeError("could not isolate enough warm skin pixels from canonical master")
    sx0, sy0, sx1, sy1 = skin_bbox
    skin_h = sy1 - sy0
    if skin_h < max(40, master.height * 0.25):
        raise RuntimeError(f"skin anchor height too small: {skin_h}")

    sp = skin.load()
    skin_xs: list[int] = []
    for y in range(master.height):
        for x in range(master.width):
            if sp[x, y]:
                skin_xs.append(x)
    skin_cx = median([float(x) for x in skin_xs])

    rgb = master.convert("RGB")
    rp = rgb.load()
    fp = fg.load()
    upper_limit = min(master.height, round(sy0 + skin_h * 0.68))
    upper_lumas: list[float] = []
    for y in range(max(0, sy0 - round(0.12 * skin_h)), upper_limit):
        for x in range(master.width):
            if fp[x, y]:
                upper_lumas.append(luma(rp[x, y]))
    if len(upper_lumas) < 100:
        raise RuntimeError("not enough upper-body foreground pixels to derive hair threshold")
    dark_threshold = min(96.0, percentile(upper_lumas, 0.34) + 10.0)

    cand = Image.new("L", master.size, 0)
    cp = cand.load()
    xmin = max(0, round(skin_cx - 0.62 * skin_h))
    xmax = min(master.width - 1, round(skin_cx + 0.62 * skin_h))
    ymin = max(0, round(sy0 - 0.18 * skin_h))
    ymax = min(master.height - 1, round(sy0 + 0.72 * skin_h))

    for y in range(ymin, ymax + 1):
        for x in range(xmin, xmax + 1):
            if not fp[x, y]:
                continue
            r, g, b = rp[x, y]
            lum = luma((r, g, b))
            warm_skin_shadow = (r >= g + 24 and r >= b + 38 and lum > 42)
            if lum <= dark_threshold and not warm_skin_shadow:
                cp[x, y] = 255

    comps = connected_components(cand)
    if not comps:
        raise RuntimeError("no dark components found for hair candidate")

    seed_y0 = max(ymin, round(sy0 - 0.12 * skin_h))
    seed_y1 = min(ymax, round(sy0 + 0.30 * skin_h))
    seed_x0 = max(xmin, round(skin_cx - 0.34 * skin_h))
    seed_x1 = min(xmax, round(skin_cx + 0.34 * skin_h))

    selected = Image.new("L", master.size, 0)
    selp = selected.load()
    selected_ids: set[int] = set()
    for i, comp in enumerate(comps):
        if len(comp) < 4:
            continue
        touches_seed = any(seed_x0 <= x <= seed_x1 and seed_y0 <= y <= seed_y1 for x, y in comp)
        if touches_seed:
            selected_ids.add(i)
            for x, y in comp:
                selp[x, y] = 255

    if not selected_ids:
        # deterministic fallback: choose the largest candidate component whose centroid is near the head.
        ranked = []
        for i, comp in enumerate(comps):
            cx = sum(x for x, _ in comp) / len(comp)
            cy = sum(y for _, y in comp) / len(comp)
            dist = abs(cx - skin_cx) / max(1.0, skin_h) + abs(cy - sy0) / max(1.0, skin_h)
            ranked.append((dist, -len(comp), i))
        _, _, i = sorted(ranked)[0]
        selected_ids.add(i)
        for x, y in comps[i]:
            selp[x, y] = 255

    # Pull in nearby dark pieces so separated locks/curls survive, but only within the bounded upper-body ROI.
    gap = max(1, round(skin_h * 0.014))
    filter_size = max(3, gap * 2 + 1)
    if filter_size % 2 == 0:
        filter_size += 1
    for _ in range(2):
        dil = selected.filter(ImageFilter.MaxFilter(filter_size))
        dp = dil.load()
        changed = False
        for i, comp in enumerate(comps):
            if i in selected_ids or len(comp) < 3:
                continue
            if any(dp[x, y] for x, y in comp):
                selected_ids.add(i)
                for x, y in comp:
                    selp[x, y] = 255
                changed = True
        if not changed:
            break

    if sum(1 for v in selected.getdata() if v) < 80:
        raise RuntimeError("derived hair mask is implausibly small")

    return selected, {
        "skin_y_top": float(sy0),
        "skin_y_bottom": float(sy1 - 1),
        "skin_center_x": float(skin_cx),
        "skin_height": float(skin_h),
        "dark_threshold_luma": float(dark_threshold),
    }


def transform_hair_to_working(master: Image.Image, hair_mask: Image.Image, anchors: dict[str, float]) -> Image.Image:
    hb = hair_mask.getbbox()
    if hb is None:
        raise RuntimeError("empty derived hair mask")
    x0, y0, x1, y1 = hb
    source = master.convert("RGBA").crop(hb)
    alpha = hair_mask.crop(hb)
    source.putalpha(alpha)

    target_body_top = BODY_Y
    target_body_bottom = BODY_GROUND_Y - 1
    target_h = target_body_bottom - target_body_top
    source_skin_h = max(1.0, anchors["skin_y_bottom"] - anchors["skin_y_top"])
    scale = target_h / source_skin_h

    nw = max(1, round(source.width * scale))
    nh = max(1, round(source.height * scale))
    source = source.resize((nw, nh), Image.Resampling.NEAREST)

    target_cx = WORKING_CANVAS[0] / 2.0
    tx = round((x0 - anchors["skin_center_x"]) * scale + target_cx)
    ty = round((y0 - anchors["skin_y_top"]) * scale + target_body_top)

    out = Image.new("RGBA", WORKING_CANVAS, (0, 0, 0, 0))
    out.alpha_composite(source, (tx, ty))
    return out


def split_front_rear(hair: Image.Image, body_work: Image.Image) -> tuple[Image.Image, Image.Image]:
    hair = hair.convert("RGBA")
    body_alpha = body_work.getchannel("A")
    body_dilated = body_alpha.filter(ImageFilter.MaxFilter(3))
    hp = hair.load()
    bp = body_alpha.load()
    dp = body_dilated.load()
    rear = Image.new("RGBA", hair.size, (0, 0, 0, 0))
    front = Image.new("RGBA", hair.size, (0, 0, 0, 0))
    rp = rear.load()
    fp = front.load()

    for y in range(hair.height):
        for x in range(hair.width):
            rgba = hp[x, y]
            if rgba[3] == 0:
                continue
            # Pixels overlapping the immutable body are visible front hair by definition in the source composite.
            # A 1px dilation keeps strands that cross the immediate face/shoulder contour with the front mass.
            if bp[x, y] or (dp[x, y] and y < BODY_Y + 82):
                fp[x, y] = rgba
            else:
                rp[x, y] = rgba

    return rear, front


def opaque_count(im: Image.Image) -> int:
    return sum(1 for a in im.getchannel("A").getdata() if a)


def make_review_sheet(master: Image.Image, body_work: Image.Image, rear: Image.Image, front: Image.Image, composite: Image.Image, gameplay: Image.Image, out: Path) -> None:
    sheet = Image.new("RGBA", (1600, 900), (16, 16, 19, 255))
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()
    draw.text((24, 18), "G3S-B4B TWO-LAYER HAIR REVIEW — SOURCE-PIXEL EXTRACTION / NO BODY MODIFICATION", fill=(238,238,242), font=font)
    draw.text((24, 42), "REVIEW ONLY — rear_hair -> immutable body -> front_hair", fill=(220,180,90), font=font)

    draw.text((24, 78), "A  CANONICAL MASTER / HAIR IDENTITY", fill=(220,220,225), font=font)
    mp = master.copy()
    mp.thumbnail((430, 700), Image.Resampling.LANCZOS)
    sheet.alpha_composite(mp, (30 + (430-mp.width)//2, 110 + (700-mp.height)//2))

    def panel(layer: Image.Image, title: str, x: int, y: int, scale: int = 4):
        draw.text((x, y-28), title, fill=(220,220,225), font=font)
        bg = checkerboard(layer.size)
        bg.alpha_composite(layer)
        big = bg.resize((layer.width*scale, layer.height*scale), Image.Resampling.NEAREST)
        sheet.alpha_composite(big, (x, y))

    panel(rear, "B  rear_hair", 500, 130)
    panel(body_work, "C  immutable body", 900, 130)
    panel(front, "D  front_hair", 500, 520, scale=2)
    panel(composite, "E  composite", 760, 520, scale=2)

    draw.text((1100, 500), "F  640x360 gameplay preview", fill=(220,220,225), font=font)
    gp = gameplay.resize((480, 270), Image.Resampling.NEAREST)
    sheet.alpha_composite(gp, (1090, 540))
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
        raise RuntimeError(f"body size mismatch: {body.size}")
    if file_sha256(body_path) != EXPECTED_BODY_PNG_SHA256:
        raise RuntimeError("canonical body PNG hash changed")
    if raw_rgba_sha256(body) != EXPECTED_BODY_RAW_RGBA_SHA256:
        raise RuntimeError("canonical body raw RGBA changed")

    preflight = json.loads(preflight_meta_path.read_text(encoding="utf-8"))
    expected_master_sha = str(preflight.get("master_sha256") or "")
    if not expected_master_sha:
        raise RuntimeError("preflight metadata lacks master_sha256")
    actual_master_sha = file_sha256(master_path)
    if actual_master_sha != expected_master_sha:
        raise RuntimeError(f"master SHA changed since B4A preflight: got={actual_master_sha} expected={expected_master_sha}")

    master = Image.open(master_path).convert("RGBA")
    fg = foreground_mask(master)
    skin = skin_mask(master, fg)
    hair_mask, anchors = derive_hair_mask(master, fg, skin)
    hair_work = transform_hair_to_working(master, hair_mask, anchors)

    body_work = Image.new("RGBA", WORKING_CANVAS, (0,0,0,0))
    body_work.alpha_composite(body, (BODY_X, BODY_Y))
    rear, front = split_front_rear(hair_work, body_work)

    rear_count = opaque_count(rear)
    front_count = opaque_count(front)
    if rear_count < 45:
        raise RuntimeError(f"rear_hair too small for meaningful review: {rear_count} opaque px")
    if front_count < 20:
        raise RuntimeError(f"front_hair too small for meaningful review: {front_count} opaque px")

    composite = Image.new("RGBA", WORKING_CANVAS, (0,0,0,0))
    composite.alpha_composite(rear)
    composite.alpha_composite(body_work)
    composite.alpha_composite(front)

    rear_path = workspace / "g3s_b4b_rear_hair_candidate.png"
    front_path = workspace / "g3s_b4b_front_hair_candidate.png"
    composite_path = workspace / "g3s_b4b_body_hair_composite.png"
    rear.save(rear_path)
    front.save(front_path)
    composite.save(composite_path)

    gameplay = Image.new("RGBA", (640,360), (18,18,22,255))
    floor_y = 286
    gdraw = ImageDraw.Draw(gameplay)
    gdraw.rectangle((0,floor_y,639,359), fill=(42,34,30,255))
    bbox = composite.getchannel("A").getbbox()
    if bbox is None:
        raise RuntimeError("empty body+hair composite")
    crop = composite.crop(bbox)
    gx = (640 - crop.width) // 2
    gy = floor_y - crop.height
    gameplay.alpha_composite(crop, (gx, gy))
    gameplay_path = workspace / "g3s_b4b_gameplay_preview.png"
    gameplay.save(gameplay_path)

    sheet_path = workspace / "g3s_b4b_contact_sheet.png"
    make_review_sheet(master, body_work, rear, front, composite, gameplay, sheet_path)

    meta = {
        "gate": "G3S-B4",
        "revision": "B4B_TWO_LAYER_HAIR_CANDIDATE_V1",
        "status": "REVIEW_REQUIRED",
        "method": "bounded extraction of already-authored black hair pixels from canonical Exilada pixel-art master, aligned to immutable B3B body; source colors retained; front/back ownership split by immutable body overlap",
        "master": str(master_path),
        "master_sha256": actual_master_sha,
        "body": str(body_path),
        "body_png_sha256": EXPECTED_BODY_PNG_SHA256,
        "body_raw_rgba_sha256": EXPECTED_BODY_RAW_RGBA_SHA256,
        "working_canvas": list(WORKING_CANVAS),
        "composition_order_back_to_front": ["rear_hair", "body", "front_hair"],
        "rear_hair": str(rear_path),
        "rear_hair_opaque_px": rear_count,
        "front_hair": str(front_path),
        "front_hair_opaque_px": front_count,
        "composite": str(composite_path),
        "contact_sheet": str(sheet_path),
        "contact_sheet_sha256": file_sha256(sheet_path),
        "anchors": anchors,
        "automatic_promotion": False,
        "body_modified": False,
        "limitations": [
            "static review candidate only",
            "rear hidden coverage behind the body is not yet inferred beyond source-visible hair pixels",
            "secondary-motion segmentation is not yet authored",
            "no B5 clothing/accessory work may start before B4 visual/structural approval"
        ]
    }
    meta_path = workspace / "g3s_b4b_two_layer_hair_candidate.json"
    meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"MASTER SHA:  {actual_master_sha}")
    print(f"REAR HAIR:   {rear_path} ({rear_count} opaque px)")
    print(f"FRONT HAIR:  {front_path} ({front_count} opaque px)")
    print(f"COMPOSITE:   {composite_path}")
    print(f"CONTACT:     {sheet_path}")
    print(f"META:        {meta_path}")
    print("STATUS: REVIEW REQUIRED — NO HAIR ASSET PROMOTED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
