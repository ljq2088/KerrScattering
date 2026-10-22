"""Export narrative-only edits; assert display mathematics and figures survive."""
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
old = ROOT/'output/overleaf_20261017/prd_before_narrative_20261023.tex'
current = ROOT/'docs/prd/kerr_scalar_nonlinear_prd_review_20261007.tex'
before = old.read_text(encoding='utf8')
after = current.read_text(encoding='utf8')
pattern = r'\\begin\{(equation\*?|align\*?|gather\*?|table\*?|figure\*?)\}[\s\S]*?\\end\{\1\}'
before_blocks = re.findall(pattern, before)
assert [m.group(0) for m in re.finditer(pattern,before)] == [m.group(0) for m in re.finditer(pattern,after)]
assert before[before.index('\\begin{abstract}'):before.index('\\end{abstract}')] == after[after.index('\\begin{abstract}'):after.index('\\end{abstract}')]
out = ROOT/'output/overleaf_20261023'
out.mkdir(exist_ok=True)
(out/'main.tex').write_text(after.replace('../../figures/','figures/'),encoding='utf8')
record = dict(scope='narrative-only: introduction, asymptotic transition, conclusion opening',
              preserved_display_table_figure_blocks=len(before_blocks),abstract_unchanged=True,
              original_sha256=hashlib.sha256(old.read_bytes()).hexdigest(),
              revised_sha256=hashlib.sha256(current.read_bytes()).hexdigest(),
              new_precision_results_in_manuscript=False)
(out/'editorial_audit.json').write_text(json.dumps(record,indent=2),encoding='utf8')
print(json.dumps(record,indent=2))
