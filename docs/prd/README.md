# PRD-style manuscript

This directory contains a new English REVTeX/PRD-style manuscript.  It does
not replace the existing Chinese derivation in `docs/teukolsky_scalar_kerr.md`.

Build locally with TeX Live:

```powershell
cd docs\prd
pdflatex -interaction=nonstopmode -halt-on-error kerr_scalar_scattering_prd.tex
pdflatex -interaction=nonstopmode -halt-on-error kerr_scalar_scattering_prd.tex
```

The source includes figures from `../../figures/`; they are embedded into the
generated PDF.
