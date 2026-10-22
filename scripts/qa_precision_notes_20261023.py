"""Check rendered notes and prepare a contact sheet for visual review."""
from pathlib import Path
import json
import fitz
from PIL import Image, ImageOps, ImageDraw

ROOT=Path(__file__).resolve().parents[1]
PDF=ROOT/'output/pdf/kerr_precision_flux_phase_20261023.pdf'
OUT=ROOT/'output/pdf/precision_notes_20261023_qa'
OUT.mkdir(exist_ok=True)
doc=fitz.open(PDF)
texts=[p.get_text() for p in doc]
assert len(doc)>=6 and all(len(t.strip())>60 for t in texts)
assert '??' not in '\n'.join(texts)
outside=[]
tiles=[]
for index,page in enumerate(doc):
    for b in page.get_text('blocks'):
        if b[0]<-1 or b[1]<-1 or b[2]>page.rect.width+1 or b[3]>page.rect.height+1:
            outside.append(index+1)
    pix=page.get_pixmap(matrix=fitz.Matrix(1.1,1.1))
    file=OUT/f'page_{index+1:02}.png'
    pix.save(file)
    thumb=Image.open(file).convert('RGB');thumb.thumbnail((260,380))
    tile=Image.new('RGB',(280,410),'#eeeeee');tile.paste(thumb,((280-thumb.width)//2,10))
    ImageDraw.Draw(tile).text((10,390),f'Page {index+1}',fill='black')
    tiles.append(tile)
sheet=Image.new('RGB',(280*3,410*((len(tiles)+2)//3)),'white')
for i,tile in enumerate(tiles):sheet.paste(tile,((i%3)*280,(i//3)*410))
sheet.save(OUT/'contact_sheet.png')
log=PDF.with_suffix('.log').read_text(encoding='utf8',errors='replace')
record=dict(pages=len(doc),characters=[len(t) for t in texts],outside_page_blocks=outside,
            undefined_reference_warning='There were undefined references' in log,
            overfull_boxes=log.count('Overfull \\hbox'))
(OUT/'qa.json').write_text(json.dumps(record,indent=2),encoding='utf8')
print(json.dumps(record,indent=2))
