# PRD-style manuscripts

This directory contains English REVTeX/PRD-style manuscripts.  The active
Kerr scalar nonlinear-scattering draft is
`kerr_scalar_nonlinear_GF_baseframe.tex`.

The older files `kerr_scalar_nonlinear_GF.tex` and
`kerr_scalar_nonlinear_GF.pdf` are retained as July 6 archival drafts and are
not submission inputs.  The `baseframe` TeX/PDF pair is the only active
manuscript and is the version copied into the draft package.

Build locally with TeX Live through the submission-prep wrapper:

```powershell
cd ..\..
python scripts\build_prd_manuscript.py
```

The wrapper checks required figure/CSV artifacts, checks manuscript numbers
against the tracked CSV files, verifies the frozen artifact manifest, runs
`pdflatex` three times, fails on unresolved references/citations or overfull boxes,
copies the PDF to the repository root, and removes LaTeX auxiliary files.  It
sets `SOURCE_DATE_EPOCH=1704067200` by default so repeated builds have the
same PDF metadata and SHA-256; callers may override that variable deliberately.

For manual debugging, run LaTeX directly:

```powershell
cd docs\prd
pdflatex -interaction=nonstopmode -halt-on-error kerr_scalar_nonlinear_GF_baseframe.tex
pdflatex -interaction=nonstopmode -halt-on-error kerr_scalar_nonlinear_GF_baseframe.tex
```

The source includes figures from `../../figures/`; they are embedded into the
generated PDF.

The local software versions used for the current draft are recorded in
`environment_snapshot.txt`, including the `qnm` version used for the Kerr
quasinormal-mode reference values.

## Reproducing The Current Kerr Nonlinear Figures

The active draft uses the following tracked inputs:

- `../../figures/kerr_scalar_low_frequency_axisymmetric.png`
- `../../figures/kerr_scalar_nonlinear_axisymmetric_fig2.png`
- `../../figures/kerr_scalar_axisymmetric_accuracy.png`
- `../../figures/kerr_scalar_nonlinear_superradiant_m2.png`
- `../../results/kerr_scalar_nonlinear_axisymmetric_hires_l0.csv`
- `../../results/kerr_scalar_nonlinear_axisymmetric_hires_l1.csv`
- `../../results/kerr_scalar_nonlinear_axisymmetric_hires_l2.csv`
- `../../results/kerr_scalar_nonlinear_axisymmetric_refine_l0.csv`
- `../../results/kerr_scalar_nonlinear_axisymmetric_refine_l1.csv`
- `../../results/kerr_scalar_nonlinear_axisymmetric_refine_l2.csv`
- `../../results/kerr_scalar_nonlinear_axisymmetric_fit_table.csv`
- `../../results/kerr_scalar_low_frequency_axisymmetric_slopes.csv`
- `../../results/kerr_scalar_axisymmetric_spectral_coefficients.csv`
- `../../results/kerr_scalar_axisymmetric_spectral_residuals.csv`
- `../../results/kerr_scalar_axisymmetric_spectral_quality_summary.csv`
- `../../results/kerr_scalar_nonlinear_convergence_summary.csv`
- `../../results/kerr_scalar_axisymmetric_production_convergence.csv`
- `../../results/kerr_scalar_nonlinear_channels.csv`
- `../../results/kerr_scalar_nonlinear_channel_convergence.csv`
- `../../results/kerr_scalar_nonlinear_m2_superradiant.csv`

To rebuild the plotted quantities after the numerical sweeps already exist:

```powershell
cd ..\..
python scripts\plot_kerr_scalar_low_frequency_axisymmetric.py
python scripts\plot_kerr_scalar_nonlinear_axisymmetric_base_like.py
python scripts\plot_kerr_scalar_axisymmetric_accuracy.py
python scripts\build_prd_convergence_summary.py
```

To only check that the rounded numbers in Tables I--VI and the low-frequency
slopes still agree with the tracked CSV data, and that the frozen figure/CSV
artifacts have not drifted:

```powershell
python scripts\check_prd_artifacts.py
python scripts\check_prd_citations.py
python scripts\check_prd_manuscript_numbers.py
```

After intentionally regenerating one of the listed figures or CSV files, update
the manifest before rebuilding:

```powershell
python scripts\write_prd_artifact_manifest.py
python scripts\build_prd_manuscript.py
```

To write a human-readable snapshot of the current manuscript files, frozen
artifacts, and check outputs:

```powershell
python scripts\write_prd_reproducibility_report.py
```

To assemble a self-contained package after the readiness audit passes:

```powershell
python scripts\build_prd_submission_package.py
```

While the final author metadata and submission files are still pending,
an internal-review package can be built explicitly with:

```powershell
python scripts\build_prd_submission_package.py --allow-draft
```

The draft package records the readiness blockers in
`docs\prd\submission_package_draft\package_manifest.json`, copies the
PRD-specific checking and plotting scripts, and writes
`docs\prd\submission_package_draft.zip`.  It must not be used as the final
submission package.

To audit whether the draft has no remaining submission placeholders:

```powershell
python scripts\check_prd_submission_ready.py
```

This stricter audit is expected to fail until the final author metadata and
submission files are available and written into
`docs\prd\submission_metadata.json`.  It also checks that the PDF is fresh,
that the root PDF copy matches the `docs/prd` build, that the metadata template
exists, that the final metadata and generated cover letter are present and
consistent, that the manuscript is still a REVTeX PRD draft, that the Data and
code availability section and submission support files are present, and that
off-scope benchmark or spin-minus-two notes have not leaked into the
manuscript.

For a human-readable PRD submission checklist that records the current local
evidence, official submission-guidance links, and remaining blockers, see
`docs\prd\PRD_SUBMISSION_CHECKLIST.md`.  The checklist is copied into both the
draft review package and the final package.

When those external details are available, copy
`docs\prd\submission_metadata.template.json` to
`docs\prd\submission_metadata.json`, fill in the real author/affiliation/email
metadata, update
`docs\prd\cover_letter.template.md` if the cover-letter wording itself should
change, and apply the manuscript metadata with:

```powershell
python scripts\apply_prd_submission_metadata.py docs\prd\submission_metadata.json
python scripts\build_prd_manuscript.py
python scripts\check_prd_submission_ready.py
```

To render a final cover letter from the same metadata:

```powershell
python scripts\render_prd_cover_letter.py docs\prd\submission_metadata.json
```

By default this writes the path configured by
`submission.cover_letter_output` in the metadata file.  When
`docs\prd\submission_metadata.json` and the generated cover letter exist, the
package builder copies them into the draft or final package alongside the
template files.

The metadata application script rejects template placeholder values by default.
Use `--allow-placeholders` only for dry-run testing of the template, not for the
final manuscript.

To regenerate the representative spectral-accuracy CSV files used in Fig. 3:

```powershell
python scripts\run_kerr_scalar_spectral_quality.py `
  --label kerr_a05_l2m0_peak --l 2 --m 0 --a 0.5 --omega 0.52 `
  --N-outer 240 --N-inner 240 --quad-order 192 --r-match 40 `
  --coeff-output results\kerr_scalar_axisymmetric_spectral_coefficients.csv `
  --residual-output results\kerr_scalar_axisymmetric_spectral_residuals.csv `
  --summary-output results\kerr_scalar_axisymmetric_spectral_quality_summary.csv `
  --skip-flux-convergence
```

Full frequency sweeps are more expensive and are run by
`scripts/run_kerr_scalar_nonlinear_frequency_sweep.py`; the tracked CSV files
record the production data used in the manuscript.

The active axisymmetric PRD curves use the refined sweeps generated by
`scripts/run_prd_axisymmetric_high_order_sweeps.py` with $N=240$ and
quadrature order $q=192$.  The older lower-order sweeps remain in `results/`
as an audit trail but are not used by the active manuscript figures.

The production-resolution audit is generated by
`scripts/run_prd_axisymmetric_production_convergence.py`; it records RSS and
the relative changes in the Green amplitudes and flux coefficients for each
representative peak point.

The representative non-axisymmetric target-channel table and its order audit
are generated with bounded jobs:

```powershell
python scripts\run_kerr_scalar_nonlinear_channels.py `
  --case-label kerr_a05_l2m2_super --N-outer 288 --N-inner 288 `
  --quad-order 224 --tail-epsrel 1e-11 --max-rss-mb 1500
python scripts\run_kerr_scalar_nonlinear_channel_convergence.py `
  --case-label kerr_a05_l2m2_super --l-targets 2,4,6 `
  --configs 224:224,256:224,288:224 --max-rss-mb 1500
```

The bounded non-axisymmetric superradiant check used in the active draft is
reproduced with:

```powershell
python scripts\run_kerr_scalar_nonlinear_frequency_sweep.py `
  --output results\kerr_scalar_nonlinear_m2_superradiant.csv `
  --a 0.5 --l 2 --m 2 `
  --omegas 0.18,0.20,0.22,0.24,0.255,0.265,0.28,0.30,0.35,0.45 `
  --N 320 --quad-order 320 --tail-epsrel 1e-11 `
  --r-match 40 --max-rss-mb 1500
python scripts\plot_kerr_scalar_nonlinear_superradiant.py
```

The channel CSV includes the flux-normalization condition indicator
`(|B_inc|^2+|B_ref|^2)/||B_inc|^2-|B_ref|^2|`.  A large value flags cancellation
in the horizon-normalized continuation; it is not evidence that the physical
channel is absent or that increasing the Chebyshev order alone will restore
double-precision accuracy.

As an external regression, the same endpoint-inclusive Kerr solver can be run
at `a=0` with `m=0` for `l=0,1,2`.  The resulting files
`results/kerr_scalar_schwarzschild_limit_l0.csv`,
`results/kerr_scalar_schwarzschild_limit_l1.csv`, and
`results/kerr_scalar_schwarzschild_limit_l2.csv` are audit data rather than
manuscript inputs.  They test the linear and first-order flux balances and the
normalization conversion in Appendix A against the legacy reduced-field route;
they are intentionally not used as external benchmark claims in the paper and
are not copied into the submission archive.
