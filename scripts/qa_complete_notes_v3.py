"""Render and audit every page of the recomposed notebook."""
from pathlib import Path
import json
import re
import sys
import fitz
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
version = 'v4' if '--reference-layout' in sys.argv else 'v3'
out = ROOT / f'tmp/pdfs/notes_{version}'
out.mkdir(exist_ok=True)
pdf = ROOT / f'output/pdf/kerr_scalar_nonlinear_complete_notes_zh_20261005_{version}.pdf'
doc = fitz.open(pdf)
report = {'pages': len(doc), 'outside_page_text': [], 'blank_pages': [],
          'missing_glyphs': [], 'figure_instances': 0, 'table_numbers': []}
for i,page in enumerate(doc):
    text = page.get_text()
    if len(text.strip()) < 40:
        report['blank_pages'].append(i+1)
    if '\ufffd' in text:
        report['missing_glyphs'].append(i+1)
    report['figure_instances'] += len(page.get_images())
    report['table_numbers'].extend(re.findall(r'表\s*(?:[A-Z]\.)?\d+', text))
    for block in page.get_text('dict')['blocks']:
        for line in block.get('lines', []):
            for span in line['spans']:
                x0,y0,x1,y1 = span['bbox']
                if x0<0 or y0<0 or x1>page.rect.width or y1>page.rect.height:
                    report['outside_page_text'].append([i+1,span['text']])
    page.get_pixmap(matrix=fitz.Matrix(0.5,0.5)).save(str(out/f'page_{i+1}.png'))
for group in range((len(doc)+11)//12):
    sheet = Image.new('RGB',(1080,1260),'#e6e6e6')
    draw = ImageDraw.Draw(sheet)
    for j in range(12):
        i = group*12+j
        if i >= len(doc):
            break
        im = Image.open(out/f'page_{i+1}.png')
        im.thumbnail((250,380))
        x,y = (j%4)*270+10, (j//4)*420+25
        sheet.paste(im,(x,y))
        draw.text((x,y-17),f'PDF {i+1}',fill='black')
    sheet.save(out/f'montage_{group+1}.png')
selected = {0,3,4,19,30,36,37,38,39,40,41,42,43,44,45,46,47}
for i in selected:
    if i<len(doc):
        doc[i].get_pixmap(matrix=fitz.Matrix(1.25,1.25)).save(str(out/f'detail_{i+1}.png'))
assert not report['blank_pages']
assert not report['missing_glyphs']
assert not report['outside_page_text']
assert report['figure_instances'] == 11
source = (ROOT/'docs/notes/kerr_scalar_nonlinear_complete_notes_zh_20261005_v2.tex').read_text(encoding='utf8')
new = (ROOT/f'docs/notes/kerr_scalar_nonlinear_complete_notes_zh_20261005_{version}.tex').read_text(encoding='utf8')
old_bib = source[source.index(r'\begin{thebibliography}'):source.index(r'\end{thebibliography}')]
new_bib = new[new.index(r'\begin{thebibliography}'):new.index(r'\end{thebibliography}')]
assert old_bib == new_bib
assert set(re.findall(r'\\label\{([^}]+)\}',source)) <= set(re.findall(r'\\label\{([^}]+)\}',new))
report['labels_preserved'] = True
report['bibliography_preserved'] = True
report['table_groups'] = len(json.loads((ROOT/'tmp/pdfs/notes_v3_table_layout.json').read_text(encoding='utf8')))
(out/'qa.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(report,ensure_ascii=False))
