"""Render each manuscript page and four contact sheets for visual review."""
from pathlib import Path
import fitz
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output' / 'review' / 'principal_20261014'
OUT.mkdir(parents=True, exist_ok=True)
doc = fitz.open(ROOT / 'output/pdf/kerr_scalar_nonlinear_prd_review_20261007.pdf')
for index, page in enumerate(doc, 1):
    page.get_pixmap(matrix=fitz.Matrix(1.6, 1.6)).save(OUT / f'page_{index:02d}.png')
for start in range(0, len(doc), 6):
    sheet = Image.new('RGB', (1200, 1620), 'white')
    draw = ImageDraw.Draw(sheet)
    for slot, index in enumerate(range(start, min(start + 6, len(doc)))):
        thumb = Image.open(OUT / f'page_{index+1:02d}.png').convert('RGB')
        thumb.thumbnail((585, 495))
        x, y = (slot % 2)*600, (slot // 2)*540
        sheet.paste(thumb, (x, y+30))
        draw.text((x+12, y+8), f'Page {index+1}', fill='black')
    sheet.save(OUT / f'contact_{start//6+1}.png')
print(f'Rendered {len(doc)} pages to {OUT}')
