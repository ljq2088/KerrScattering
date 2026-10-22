"""Read-only checks of inputs and rendered-note checks; writes QA outputs only."""
import csv
import hashlib
import json
from pathlib import Path
import re

import fitz
from PIL import Image, ImageDraw, ImageOps

ROOT = Path(__file__).resolve().parents[2]
STEM = 'kerr_scalar_learning_notes_zh_20261014_v2'
source = ROOT / f'docs/notes/{STEM}.tex'
pdf = ROOT / f'output/pdf/{STEM}.pdf'
original = {
    ROOT/'docs/notes/kerr_scalar_learning_notes_zh_20261013.tex':
        'E54088EBCCD1BCE38F7864D4C98CE8C28242E475857CA5E15625095321C3B8F1',
    ROOT/'output/pdf/kerr_scalar_learning_notes_zh_20261013.pdf':
        '8EA3F781B625E8A78C98EB15633BCD0FD9ECC221AAB8C1E61FB9BA67E1E4C03B',
}
for path, expected in original.items():
    assert hashlib.sha256(path.read_bytes()).hexdigest().upper() == expected, path
tex = source.read_text(encoding='utf8')
combined = tex
for relative in re.findall(r'\\input\{([^}]+)\}', tex):
    combined += '\n' + (source.parent/relative).read_text(encoding='utf8')
labels = re.findall(r'\\label\{([^}]+)\}', combined)
references = set(re.findall(r'\\(?:eqref|ref)\{([^}]+)\}', combined))
assert len(labels) == len(set(labels))
assert references <= set(labels)
cited = {key for group in re.findall(r'\\cite\w*\{([^}]+)\}', combined)
         for key in group.split(',')}
assert cited <= set(re.findall(r'\\bibitem\{([^}]+)\}', combined))
with (ROOT/'results/kerr_scalar_principal_matched_prediction_20261013.csv').open(newline='',encoding='utf8') as handle:
    rows = list(csv.DictReader(handle))
selected = [row for row in rows if row['N']=='320' and float(row['a'])>=0.99999]
assert len(selected) == 4
for row in selected:
    assert row['two_boundary_flux_accepted'] == 'True'
    for key in ('chi','chi_matched'):
        assert f"{float(row[key]):.6f}" in tex
    assert f"{100*float(row['matched_chi_relative_error']):.3f}" in tex
log = (ROOT/f'output/pdf/{STEM}.log').read_text(encoding='utf8',errors='replace')
for pattern in ('Overfull','undefined','Missing character','! LaTeX Error'):
    assert pattern not in log, pattern
doc = fitz.open(pdf)
out = ROOT/f'tmp/pdfs/{STEM}'
out.mkdir(parents=True,exist_ok=True)
outside, blank, principal_pages = [], [], []
for number, page in enumerate(doc,1):
    text = page.get_text()
    if len(text.strip()) < 20:
        blank.append(number)
    if 'Principal' in text or 'principal' in text:
        principal_pages.append(number)
    for block in page.get_text('dict')['blocks']:
        for line in block.get('lines',[]):
            for span in line['spans']:
                x0,y0,x1,y1 = span['bbox']
                if x0 < -1 or y0 < -1 or x1 > page.rect.width+1 or y1 > page.rect.height+1:
                    outside.append([number,span['text']])
    page.get_pixmap(matrix=fitz.Matrix(1.3,1.3)).save(out/f'page_{number:02}.png')
assert not outside and not blank
for start in range(0,len(doc),12):
    canvas = Image.new('RGB',(1240,1260),'#dddddd')
    draw = ImageDraw.Draw(canvas)
    for index in range(start,min(start+12,len(doc))):
        thumb = ImageOps.contain(Image.open(out/f'page_{index+1:02}.png'),(306,396))
        x,y = (index-start)%4*310,(index-start)//4*420
        canvas.paste(thumb,(x,y+20))
        draw.text((x+5,y+3),str(index+1),fill='black')
    canvas.save(out/f'montage_{start//12+1}.png')
report = dict(pages=len(doc),original_files_unchanged=True,
              pdf_sha256=hashlib.sha256(pdf.read_bytes()).hexdigest(),
              principal_pages=principal_pages,checked_new_numeric_rows=len(selected),
              labels=len(labels),cited_sources=len(cited),outside_page_text=outside,
              blank_pages=blank,rendered_pages=len(doc),new_physics_runs=False,
              source=str(source.relative_to(ROOT)))
(ROOT/f'output/pdf/{STEM}_qa.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps(report,indent=2))
