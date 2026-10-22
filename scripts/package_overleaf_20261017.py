"""Package the existing manuscript and a separate exploratory Overleaf draft."""
from pathlib import Path
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output' / 'overleaf_20261017'


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    sources = {
        'Kerr_scalar_scattering_PRD_20261017':
            'docs/prd/kerr_scalar_nonlinear_prd_review_20261007.tex',
        'Kerr_phase_flux_research_draft_20261017':
            'docs/prd/kerr_phase_flux_research_draft_20261017.tex',
    }
    for name, relative in sources.items():
        source = ROOT / relative
        tex = source.read_text(encoding='utf-8')
        figures = re.findall(r'\\includegraphics(?:\[[^]]*\])?\{([^}]+)\}', tex)
        assert all((source.parent / path).resolve().is_file() for path in figures)
        archive = OUT / (name + '.zip')
        with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as bundle:
            bundle.writestr('main.tex', tex.replace('../../figures/', 'figures/'))
            for path in figures:
                bundle.write((source.parent / path).resolve(), 'figures/' + Path(path).name)
            if 'research_draft' in name:
                for pattern in ('kerr_scalar_letter_refinement_20261014.json',
                                'kerr_scalar_phase_dominance*_20261014.csv',
                                'kerr_scalar_flux_zero*_20261014.csv'):
                    for path in (ROOT / 'results').glob(pattern):
                        bundle.write(path, 'evidence/' + path.name)
        with zipfile.ZipFile(archive) as bundle:
            assert bundle.testzip() is None
        print(f'{archive}: {len(figures)} figures, {archive.stat().st_size} bytes')


if __name__ == '__main__':
    main()
