"""Verify the byte-preserving research handoff using only the Python standard library."""
import argparse
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path, PureWindowsPath
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT/'docs/handoff/file_manifest_20261023.json'
DOCUMENTS = [
    'docs/prd/kerr_scalar_nonlinear_prd_review_20261007.tex',
    'docs/prd/kerr_phase_flux_research_draft_20261017.tex',
    'docs/notes/kerr_precision_flux_phase_20261023.tex',
    'docs/notes/kerr_scalar_learning_notes_zh_20261014_v3.tex',
]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative_path(raw):
    value = PureWindowsPath(raw)
    if value.is_absolute() or value.drive or value.root or '..' in value.parts:
        raise ValueError(f'expected repository-relative path: {raw}')
    return Path(*value.parts)


def excluded(path):
    return path.name.lower().startswith('nonlinear_gf')


def verify_dependencies():
    seen = set()
    def visit(path):
        path = path.resolve()
        assert path.is_relative_to(ROOT), path
        assert path.is_file(), path
        if path in seen:
            return
        seen.add(path)
        source = path.read_text(encoding='utf8')
        pattern = r'\\(input|include|includegraphics)(?:\[[^]]*\])?\{([^}]+)\}'
        for command, name in re.findall(pattern, source):
            target = path.parent/name
            if command in ('input', 'include'):
                if not target.suffix:
                    target = target.with_suffix('.tex')
                visit(target)
            else:
                assert target.is_file(), target
    for document in DOCUMENTS:
        visit(ROOT/document)
    return len(seen)


def verify_precision():
    base = ROOT/'results/precision_20261023'
    counts = Counter()
    for path in sorted(base.glob('*/manifest.json')):
        record = json.loads(path.read_text(encoding='utf8'))
        counts[record['status']] += 1
        for name, expected in record['outputs'].items():
            assert digest(path.parent/relative_path(name)) == expected, (path,name)
        if record['status'] == 'completed':
            assert record['source_hashes_before'] == record['source_hashes_after'], path
            for name, expected in record['source_hashes_before'].items():
                relative = relative_path(name)
                candidates = [ROOT/relative, *base.glob('source_*/'+relative.name)]
                assert any(p.is_file() and digest(p)==expected for p in candidates), (path,name)
    with (base/'comparison.csv').open(newline='',encoding='utf8') as handle:
        rows=list(csv.DictReader(handle))
    assert len(rows)==21 and all(r['accepted']=='True' for r in rows)
    return dict(counts)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-manifest', action='store_true',
                        help='Record the reviewed Git index file list before commit')
    args = parser.parse_args()
    if args.write_manifest:
        paths = subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode('utf8').split('\0')
        paths = sorted(p for p in paths if p and p!=MANIFEST.relative_to(ROOT).as_posix())
        forbidden = ROOT/'nonlinear_GF.pdf'
        excluded_hashes = [digest(forbidden)] if forbidden.exists() else []
        files = {}
        for name in paths:
            path = ROOT/name
            assert path.is_file() and not excluded(path), name
            value=digest(path)
            assert value not in excluded_hashes, name
            assert path.stat().st_size < 80*1024**2, name
            files[name]={'sha256':value,'bytes':path.stat().st_size}
        record=dict(schema=1,scope='Kerr scalar manuscripts, numerical evidence, source and handoff',
                    excludes='Supplied nonlinear_GF reference and local temporary bundles',
                    excluded_content_sha256=excluded_hashes,files=files)
        MANIFEST.parent.mkdir(parents=True,exist_ok=True)
        MANIFEST.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    record=json.loads(MANIFEST.read_text(encoding='utf8'))
    for name, item in record['files'].items():
        path=ROOT/relative_path(name)
        assert not excluded(path), name
        assert digest(path)==item['sha256'], name
        assert item['sha256'] not in record['excluded_content_sha256'], name
    report=dict(files_verified=len(record['files']),
                document_dependencies_verified=verify_dependencies(),
                historical_precision_runs=verify_precision(),paired_points=21,
                supplied_reference_in_manifest=False)
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    main()
