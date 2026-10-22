"""Render all notebook pages and inspect searchable layout metrics."""
from pathlib import Path
import json
import argparse
import fitz
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--revised-layout', action='store_true')
args = parser.parse_args()
suffix = '_v2' if args.revised_layout else ''
pdf = ROOT / ('output/pdf/kerr_scalar_nonlinear_complete_notes_zh_20261005' + suffix + '.pdf')
dest = ROOT / ('tmp/pdfs/complete_notes_20261005' + suffix)
dest.mkdir(parents=True, exist_ok=True)
doc = fitz.open(pdf)
texts = [page.get_text() for page in doc]
for group in range((len(doc) + 11) // 12):
    sheet = Image.new('RGB', (1040, 1440), '#dddddd')
    draw = ImageDraw.Draw(sheet)
    for j in range(12):
        i = 12 * group + j
        if i >= len(doc):
            break
        pix = doc[i].get_pixmap(matrix=fitz.Matrix(0.4, 0.4))
        im = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
        im.thumbnail((242, 332))
        x, y = (j % 4) * 260 + 9, (j // 4) * 480 + 28
        sheet.paste(im, (x, y))
        draw.text((x, y - 20), f'PDF {i+1}', fill='black')
    sheet.save(dest / f'montage_{group+1}.png')
keywords = ['新发现的无穷远', '复 Green', '从径向方程', '因子化：', '七点幂律拟合审计']
selected = {0, 7, 16}
for keyword in keywords:
    selected.update(i for i, text in enumerate(texts) if keyword in text)
for i in sorted(selected):
    if i < len(doc):
        doc[i].get_pixmap(matrix=fitz.Matrix(1.25, 1.25)).save(dest / f'page_{i+1}.png')
report = {'pages': len(doc), 'characters': sum(map(len, texts)),
          'selected_pages': [i+1 for i in sorted(selected)],
          'replacement_characters': sum(t.count('\ufffd') for t in texts),
          'empty_pages': [i+1 for i,t in enumerate(texts) if len(t.strip()) < 40]}
report['outside_page_text'] = []
for i,page in enumerate(doc):
    for block in page.get_text('dict')['blocks']:
        for line in block.get('lines', []):
            for span in line['spans']:
                x0,y0,x1,y1 = span['bbox']
                if x0 < 0 or y0 < 0 or x1 > page.rect.width or y1 > page.rect.height:
                    report['outside_page_text'].append([i+1, span['text']])
(dest / 'qa.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(report, ensure_ascii=False))
