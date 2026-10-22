"""Audit current source and numerical evidence without replacing the open PDF."""
import csv
import hashlib
import json
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1]
tex=ROOT/'docs/prd/kerr_scalar_nonlinear_prd_review_20261007.tex'
s=tex.read_text(encoding='utf8')
labels=re.findall(r'\\label\{([^}]+)\}',s)
refs=set(re.findall(r'\\(?:ref|eqref)\{([^}]+)\}',s))
assert len(labels)==len(set(labels)) and refs<=set(labels)
cited={k.strip() for g in re.findall(r'\\cite\w*\{([^}]+)\}',s) for k in g.split(',')}
assert cited==set(re.findall(r'\\bibitem\{([^}]+)\}',s))
abstract=re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}',s,re.S).group(1)
abstract_words=len(re.findall(r'\b[A-Za-z][A-Za-z-]*\b',abstract))
assert abstract_words<250
figures=re.findall(r'\\includegraphics(?:\[[^]]+\])?\{([^}]+)\}',s)
assert all((tex.parent/p).is_file() for p in figures)
record=json.loads((ROOT/'results/kerr_scalar_letter_refinement_20261014.json').read_text(encoding='utf8'))
for p,digest in record['sources'].items():
    assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==digest,p
assert record['principal_points']==81 and record['phase_points']==27
assert record['max_paired_change']<1e-8 and record['max_phase_grid_chi_change']<1e-7
assert record['max_abs_chi_at_root']<1e-7
with (ROOT/'results/kerr_scalar_flux_zero_sourced_20261014.csv').open(newline='',encoding='utf8') as h:
    rows=list(csv.DictReader(h))
assert [int(r['degree']) for r in rows]==[16,24,32,48,64]
assert float(rows[3]['relative_residual_max'])<1e-7
assert 'q_{\n' not in s
report=dict(source_sha256=hashlib.sha256(tex.read_bytes()).hexdigest(),labels=len(labels),
            cited_sources=len(cited),abstract_words=abstract_words,figure_count=len(figures),
            numerical_evidence_checked=True,zero_sourced_residual_interval=[1,8],
            finite_coupling_validation='pending',letter_readiness='requires further physics validation')
(ROOT/'docs/prd/letter_refinement_checks_20261014.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps(report,indent=2))
