from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

GAME_W, GAME_H = 640, 360
BG = (18, 18, 22)
FG = (238, 238, 238)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def bbox(alpha: np.ndarray):
    ys, xs = np.where(alpha > 0)
    if len(xs) == 0:
        return None
    return [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())]


def panel(image: Image.Image, label: str, size=(640, 360), nearest=True) -> Image.Image:
    out = Image.new('RGB', size, BG)
    im = image.convert('RGBA')
    max_w, max_h = size[0] - 32, size[1] - 48
    scale = min(max_w / im.width, max_h / im.height)
    nw, nh = max(1, round(im.width * scale)), max(1, round(im.height * scale))
    resample = Image.Resampling.NEAREST if nearest else Image.Resampling.LANCZOS
    im = im.resize((nw, nh), resample)
    tmp = Image.new('RGBA', size, (*BG, 255))
    tmp.alpha_composite(im, ((size[0] - nw) // 2, 28 + (max_h - nh) // 2))
    out = tmp.convert('RGB')
    d = ImageDraw.Draw(out)
    d.rectangle([4, 4, size[0] - 4, 26], fill=(0, 0, 0))
    d.text((10, 9), label, fill=FG, font=ImageFont.load_default())
    return out


def gameplay_preview(sprite: Image.Image) -> Image.Image:
    out = Image.new('RGBA', (GAME_W, GAME_H), (*BG, 255))
    out.alpha_composite(sprite, ((GAME_W - sprite.width) // 2, (GAME_H - sprite.height) // 2))
    return out.convert('RGB')


def landmark_debug(sprite: Image.Image, landmarks: dict) -> Image.Image:
    dbg = sprite.resize((512, 512), Image.Resampling.NEAREST).convert('RGBA')
    d = ImageDraw.Draw(dbg)
    for name, p in landmarks.items():
        x, y = int(p[0]) * 4, int(p[1]) * 4
        d.line([(x - 5, y), (x + 5, y)], fill=(255, 255, 255, 255), width=1)
        d.line([(x, y - 5), (x, y + 5)], fill=(255, 255, 255, 255), width=1)
        if name in ('head_center', 'sternum', 'pelvis_center', 'left_knee', 'right_knee'):
            d.text((x + 6, y - 5), name, fill=(255, 255, 255, 255), font=ImageFont.load_default())
    return dbg


def info_panel(meta: dict, stats: dict, size=(640, 360)) -> Image.Image:
    out = Image.new('RGB', size, BG)
    d = ImageDraw.Draw(out)
    f = ImageFont.load_default()
    d.rectangle([4, 4, size[0] - 4, 26], fill=(0, 0, 0))
    d.text((10, 9), 'D G3S-B3B V2 audit - authored native 2D source', fill=FG, font=f)
    lines = [
        f"revision = {meta['revision']}",
        f"source authority = {meta['source_authority']}",
        '',
        f"canvas = {stats['size'][0]}x{stats['size'][1]}",
        f"visible bbox = {stats['visible_bbox']}",
        f"visible height = {stats['visible_height']} px",
        f"opaque palette colors = {stats['opaque_palette_colors']}",
        f"partial alpha pixels = {stats['partial_alpha_pixels']}",
        '',
        'Visible RGB / alpha / silhouette are owned by the committed 2D asset.',
        'B3A RGB sampled = False',
        'B3A mask sampled = False',
        'B3A projected silhouette copied = False',
        '',
        'REVIEW AT 1x before hair, clothing or animation.'
    ]
    y = 46
    for line in lines:
        d.text((22, y), line, fill=FG, font=f)
        y += 18
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--source', required=True)
    ap.add_argument('--metadata', required=True)
    ap.add_argument('--output-dir', required=True)
    args = ap.parse_args()

    source = Path(args.source).resolve()
    metadata = Path(args.metadata).resolve()
    out = Path(args.output_dir).resolve()
    out.mkdir(parents=True, exist_ok=True)

    meta = json.loads(metadata.read_text(encoding='utf-8'))
    if meta.get('gate') != 'G3S-B3-B-NATIVE-2D-BODY-SOURCE':
        raise RuntimeError('Unexpected B3B metadata gate')
    if meta.get('revision') != 'G3S_B3B_NATIVE_2D_BODY_SOURCE_V2':
        raise RuntimeError('Unexpected B3B revision')
    if meta.get('source_authority') != 'COMMITTED_NATIVE_2D_PIXEL_ASSET':
        raise RuntimeError('B3B source is not a committed native 2D asset')
    own = meta.get('ownership', {})
    if own.get('final_visible_rgb') != 'native_2d_asset' or own.get('final_alpha') != 'native_2d_asset' or own.get('final_silhouette') != 'native_2d_asset':
        raise RuntimeError('Visible ownership invariant failed')
    if own.get('b3a_rgb_sampled') or own.get('b3a_mask_sampled') or own.get('b3a_silhouette_copied'):
        raise RuntimeError('B3A may not own visible source pixels or silhouette')

    actual_sha = sha256(source)
    if actual_sha != meta.get('source_sha256'):
        raise RuntimeError(f"Source SHA mismatch: {actual_sha}")

    sprite = Image.open(source).convert('RGBA')
    if sprite.size != (128, 128):
        raise RuntimeError(f'Native source must be 128x128, got {sprite.size}')
    arr = np.asarray(sprite, dtype=np.uint8)
    alpha = arr[:, :, 3]
    partial = int(np.logical_and(alpha > 0, alpha < 255).sum())
    if partial != 0:
        raise RuntimeError(f'Partial alpha is forbidden: {partial}')
    bb = bbox(alpha)
    if bb is None:
        raise RuntimeError('Source contains no visible pixels')
    visible_h = bb[3] - bb[1] + 1
    if visible_h != 128:
        raise RuntimeError(f'Expected 128px visible body height, got {visible_h}')
    opaque = arr[alpha > 0][:, :3]
    palette_count = int(len(np.unique(opaque, axis=0)))
    if palette_count != int(meta.get('opaque_palette_colors')):
        raise RuntimeError(f'Palette drift: got {palette_count}')

    source_out = out / 'g3s_b3b_body_base_source_v2.png'
    mask_out = out / 'g3s_b3b_body_base_mask_v2.png'
    preview_out = out / 'g3s_b3b_gameplay_preview_v2.png'
    contact_out = out / 'g3s_b3b_contact_sheet_v2.png'
    manifest_out = out / 'g3s_b3b_manifest_v2.json'

    shutil.copyfile(source, source_out)
    mask_rgba = np.zeros_like(arr)
    mask_rgba[alpha > 0] = (255, 255, 255, 255)
    Image.fromarray(mask_rgba, 'RGBA').save(mask_out)
    preview = gameplay_preview(sprite)
    preview.save(preview_out)

    cells = [
        panel(sprite.resize((512, 512), Image.Resampling.NEAREST), 'A authored native 128x128 body source V2 - 4x nearest', nearest=True),
        panel(preview, 'B gameplay preview 640x360 - source shown at native 1x', nearest=True),
        panel(landmark_debug(sprite, meta.get('landmarks_px', {})), 'C native 2D landmarks - no 3D silhouette ownership', nearest=True),
    ]
    stats = {
        'size': list(sprite.size),
        'visible_bbox': bb,
        'visible_height': visible_h,
        'opaque_palette_colors': palette_count,
        'partial_alpha_pixels': partial,
        'source_sha256': actual_sha,
    }
    cells.append(info_panel(meta, stats))
    sheet = Image.new('RGB', (1280, 720), BG)
    for cell, pos in zip(cells, [(0, 0), (640, 0), (0, 360), (640, 360)]):
        sheet.paste(cell, pos)
    sheet.save(contact_out)

    result = {
        'gate': meta['gate'],
        'status': 'REVIEW_REQUIRED',
        'revision': meta['revision'],
        'source_authority': meta['source_authority'],
        'ownership': own,
        'layer_audit': meta.get('layer_audit', {}),
        'stats': stats,
        'outputs': {
            'source': str(source_out),
            'source_sha256': sha256(source_out),
            'mask': str(mask_out),
            'mask_sha256': sha256(mask_out),
            'gameplay_preview': str(preview_out),
            'gameplay_preview_sha256': sha256(preview_out),
            'contact_sheet': str(contact_out),
            'contact_sheet_sha256': sha256(contact_out),
        },
        'rules': meta.get('rules', {}),
    }
    manifest_out.write_text(json.dumps(result, indent=2), encoding='utf-8')

    print('G3S_B3B_V2_SOURCE_AUTHORITY=COMMITTED_NATIVE_2D_PIXEL_ASSET')
    print('G3S_B3B_V2_B3A_RGB_SAMPLED=FALSE')
    print('G3S_B3B_V2_B3A_MASK_SAMPLED=FALSE')
    print('G3S_B3B_V2_B3A_SILHOUETTE_COPIED=FALSE')
    print(f'G3S_B3B_V2_VISIBLE_HEIGHT={visible_h}')
    print(f'G3S_B3B_V2_CONTACT={contact_out}')


if __name__ == '__main__':
    main()
