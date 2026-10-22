"""Audit the scoped editorial draft; a structural pass is not submission readiness."""
from pathlib import Path
import hashlib
import json
import re
import csv

import fitz
import sympy as sp

ROOT = Path(__file__).resolve().parents[1]
STEM = 'kerr_scalar_nonlinear_prd_review_20261007'
source = (ROOT / 'docs/prd/kerr_scalar_nonlinear_GF_baseframe.tex').read_text(encoding='utf8')
draft = (ROOT / f'docs/prd/{STEM}.tex').read_text(encoding='utf8')
manifest = json.loads((ROOT / 'docs/prd/prd_review_20261007_manifest.json').read_text(encoding='utf8'))
assert hashlib.sha256((ROOT / manifest['source']).read_bytes()).hexdigest() == manifest['source_sha256']
labels = re.findall(r'\\label\{([^}]+)\}', draft)
refs = set(re.findall(r'\\(?:eqref|ref)\{([^}]+)\}', draft))
assert len(labels) == len(set(labels))
assert refs <= set(labels)
assert re.findall(r'\\author\{([^}]+)\}', draft) == ['Jing-Qi Lai', 'Yu Tian']
assert r'\email[Corresponding author: ]{ytian@ucas.ac.cn}' in draft
for identifier in ('2020YFC2201300', '12035016', '12375058', '12361141825'):
    assert identifier in draft


def tables(tex):
    result = {}
    for block in re.findall(r'\\begin\{table\*?\}.*?\\end\{table\*?\}', tex, re.S):
        label = re.search(r'\\label\{([^}]+)\}', block).group(1)
        result[label] = re.search(r'\\begin\{tabular\}.*?\\end\{tabular\}', block, re.S).group(0)
    return result


old_tables, new_tables = tables(source), tables(draft)
for label, content in new_tables.items():
    if label not in {'tab:sourced20261008', 'tab:principal-weights20261014',
                     'tab:principal-verification20261014'}:
        assert content == old_tables[label], label
for path, expected in manifest.get('validation_inputs', {}).items():
    assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == expected, path
principal_manifest = json.loads((ROOT / 'results/kerr_scalar_principal_expanded_manifest_20261014.json').read_text(encoding='utf8'))
for path, expected in principal_manifest['files'].items():
    assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == expected, path
with (ROOT / 'results/kerr_scalar_principal_expanded_comparison_20261014.csv').open(newline='', encoding='utf8') as handle:
    principal_rows = list(csv.DictReader(handle))
assert len(principal_rows) == 81 and principal_manifest['accepted'] == 81
assert principal_manifest['analytic_fitted_parameters'] == 0
assert {int(row['n']) for row in principal_rows} == {1, 2, 3}
assert {int(row['m']) for row in principal_rows} == {2, 3, 4}
assert r'\sigma^{-n}{\cal F}_n' in draft
assert (ROOT / 'docs/prd/principal_expanded_tables_20261014.tex').read_text(encoding='utf8') in draft
with (ROOT / 'results/kerr_scalar_sourced_local_residual_20261008.csv').open(newline='', encoding='utf8') as handle:
    local_rows = list(csv.DictReader(handle))
assert len(local_rows) == 15
for row in local_rows:
    case = 'C' if int(row['m']) else ('A' if int(row['n']) == 1 else 'B')
    cells = []
    for key in ('relative_residual_max', 'relative_residual_median', 'coeff_tail'):
        mantissa, exponent = f"{float(row[key]):.2e}".split('e')
        cells.append('$' + mantissa + r'\times10^{' + str(int(exponent)) + '}$')
    expected_row = f"{case} & {row['N_reconstruction']} & " + ' & '.join(cells)
    assert expected_row in new_tables['tab:sourced20261008'], expected_row
figures = re.findall(r'\\includegraphics(?:\[[^]]+\])?\{([^}]+)\}', draft)
for path in figures:
    assert (ROOT / 'docs/prd' / path).is_file(), path
assert not any('near_extremal' in path or 'superradiant' in path for path in figures)
abstract = re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}', draft, re.S).group(1)
abstract_words = len(re.findall(r'\b[A-Za-z][A-Za-z-]*\b', abstract))
assert abstract_words < 250, abstract_words

# Derive the peeled infinity row independently of the production endpoint branch.
r, M, a, w, m, lam = sp.symbols('r M a w m lam', real=True)
D = r*r - 2*M*r + a*a
H = r*r + a*a
for sigma in (-1, 1):
    q = sp.I*sigma*w*H/D - 1/r
    B0 = D*(sp.diff(q, r) + q*q) + sp.diff(D, r)*q + (w*H - a*m)**2/D - lam
    limit = sp.simplify(sp.limit(sp.cancel(B0), r, sp.oo))
    assert sp.simplify(limit + lam + 2*a*m*w) == 0
coefficients = {}
for n in (1, 2, 3):
    integral = ((-1)**n / (4*sp.Integer(n+1)*sp.factorial(2*n-1))
                * sum((-1)**(j+1)*j**(2*n)*sp.binomial(2*n+2, n+1-j)*sp.log(j)
                      for j in range(1, n+2)))
    coefficients[str(n)] = str(sp.N(2*integral/sp.pi**n, 16))

doc = fitz.open(ROOT / f'output/pdf/{STEM}.pdf')
outside, blank, missing = [], [], []
for i, page in enumerate(doc, 1):
    text = page.get_text()
    if len(text.strip()) < 20:
        blank.append(i)
    if '\ufffd' in text:
        missing.append(i)
    for block in page.get_text('dict')['blocks']:
        for line in block.get('lines', []):
            for span in line['spans']:
                x0, y0, x1, y1 = span['bbox']
                if x0 < -1 or y0 < -1 or x1 > page.rect.width+1 or y1 > page.rect.height+1:
                    outside.append([i, span['text']])
assert not outside and not blank and not missing
log = (ROOT / f'output/pdf/{STEM}.log').read_text(encoding='utf8', errors='replace')
for pattern in ['Overfull', 'undefined references', 'undefined citations', 'Missing character', '! LaTeX Error', 'float is stuck', 'Deferred float stuck']:
    assert pattern not in log, pattern
report = {
    'date': '2026-10-14', 'editorial_structure_passed': True,
    'source_unchanged': True, 'retained_numeric_tables_unchanged': len(new_tables)-3,
    'principal_parameter_points': 81, 'principal_fitted_parameters': 0,
    'new_local_sourced_residual_table': 'tab:sourced20261008',
    'figure_count': len(figures), 'pages': len(doc), 'abstract_words': abstract_words,
    'outside_page_text': outside, 'blank_pages': blank, 'missing_glyphs': missing,
    'symbolic_infinity_B0': '-lambda - 2*a*m*omega',
    'independently_checked_c_n': coefficients,
    'new_parameter_scans': True, 'submission_ready': False,
    'author_metadata_present': True,
    'corresponding_author': 'Yu Tian',
    'funding_metadata_present': True,
    'blockers': [
        'Principal grid covers l=m=2,3,4 and three spins; wider modal and detuning coverage remains an extension',
        'Local sourced residual verified only on [3M,8M]; global endpoint and accumulated integration-error validation remain incomplete',
        'Public bibliographic status of the supplied Schwarzschild reference not verified',
        'Novelty comparison and human scientific review not completed',
        'A verified archived data-access statement and persistent release identifier remain to be supplied',
    ],
    'nonfatal_tex_notices': re.findall(r'(?:Package|Class) [^\n]*Warning:[^\n]*', log),
}
(ROOT / 'docs/prd/prd_review_20261007_checks.json').write_text(
    json.dumps(report, ensure_ascii=False, indent=2), encoding='utf8')
print(json.dumps(report, ensure_ascii=False, indent=2))
