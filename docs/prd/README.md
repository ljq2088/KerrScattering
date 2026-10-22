# PRD-style manuscripts

This directory contains English REVTeX/PRD-style manuscripts.  The active
Kerr scalar nonlinear-scattering draft is
`kerr_scalar_nonlinear_prd_review_20261007.tex`, with narrative updates on October 23, 2026.
The verified Overleaf PDF for this revision is
`../../output/overleaf_20261023/prd_narrative_20261023.pdf`.
The complete cross-device entry is [HANDOFF.md](../../HANDOFF.md).
The October 23 numerical work is documented separately in
`../../output/pdf/kerr_precision_flux_phase_20261023.pdf`.
Section IV.A presents the resonance and tail analysis, including the
Schwarzschild-inspired algebraic-prefactor test. Section IV.C derives the
principal response and verifies 81 new parameter
points for three modes, three interaction orders, three detunings and three spins.
The October 14 validation record is `PRINCIPAL_MODE_VALIDATION_20261014.md`.

The open TeX source includes a subsequent in-place frequency-profile
revision. Compile that existing source directly. The historical
`build_prd_review_20261007.py` reproduces the earlier principal-grid revision;
running it overwrites the later in-place editorial changes.

Compile this current source from the repository root:

```powershell
cd docs/prd
pdflatex '-interaction=nonstopmode' '-halt-on-error' '-output-directory=../../output/pdf' kerr_scalar_nonlinear_prd_review_20261007.tex
pdflatex '-interaction=nonstopmode' '-halt-on-error' '-output-directory=../../output/pdf' kerr_scalar_nonlinear_prd_review_20261007.tex
cd ../..
```

## Historical Baseframe Package

The older files `kerr_scalar_nonlinear_GF.tex` and
`kerr_scalar_nonlinear_GF.pdf` are retained as July 6 archival drafts and are
not submission inputs.  The `baseframe` TeX/PDF pair and its submission-prep
wrapper are retained as the historical input for the scoped revision.
The package instructions below refer to that historical build.

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

Create an isolated Python environment and install the frozen numerical stack
from the repository root before regenerating results:

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements-dev.txt
.\.venv\Scripts\python -m pytest -q
```

The production dependencies are pinned in `requirements.txt`; the development
file adds the test runner without changing the numerical package versions.

## Reproducing The Current Kerr Nonlinear Figures

The active draft uses the following tracked inputs:

- `../../figures/kerr_scalar_low_frequency_axisymmetric.png`
- `../../figures/kerr_scalar_nonlinear_axisymmetric_fig2.png`
- `../../figures/kerr_scalar_axisymmetric_accuracy.png`
- `../../figures/kerr_scalar_superradiant_response.png`
- `../../figures/kerr_scalar_near_extremal_scaling.png`
- `../../figures/kerr_scalar_spin_limit.png`
- `../../results/kerr_scalar_nonlinear_axisymmetric_hires_l0.csv`
- `../../results/kerr_scalar_nonlinear_axisymmetric_hires_l1.csv`
- `../../results/kerr_scalar_nonlinear_axisymmetric_hires_l2.csv`
- `../../results/kerr_scalar_nonlinear_axisymmetric_refine_l0.csv`
- `../../results/kerr_scalar_nonlinear_axisymmetric_refine_l1.csv`
- `../../results/kerr_scalar_nonlinear_axisymmetric_refine_l2.csv`
- `../../results/kerr_scalar_nonlinear_axisymmetric_dense_l0.csv`
- `../../results/kerr_scalar_nonlinear_axisymmetric_dense_l1.csv`
- `../../results/kerr_scalar_nonlinear_axisymmetric_dense_l2.csv`
- `../../results/kerr_scalar_nonlinear_axisymmetric_tail_q2048_l0.csv`
- `../../results/kerr_scalar_nonlinear_axisymmetric_tail_q2048_l1.csv`
- `../../results/kerr_scalar_nonlinear_axisymmetric_tail_q2048_l2.csv`
- `../../results/kerr_scalar_nonlinear_control_scan.csv`
- `../../results/kerr_scalar_nonlinear_diagnostics.csv`
- `../../results/kerr_scalar_nonlinear_axisymmetric_fit_table.csv`
- `../../results/kerr_scalar_nonlinear_peak_window_sensitivity.csv`
- `../../results/kerr_scalar_nonlinear_tail_window_sensitivity.csv`
- `../../results/kerr_scalar_nonlinear_tail_model_comparison.csv`
- `../../results/kerr_scalar_low_frequency_axisymmetric_acceptance.csv`
- `../../results/kerr_scalar_axisymmetric_spectral_coefficients.csv`
- `../../results/kerr_scalar_axisymmetric_spectral_residuals.csv`
- `../../results/kerr_scalar_axisymmetric_spectral_quality_summary.csv`
- `../../results/kerr_scalar_nonlinear_convergence_summary.csv`
- `../../results/kerr_scalar_axisymmetric_production_convergence.csv`
- `../../results/kerr_scalar_axisymmetric_low_frequency_convergence.csv`
- `../../results/kerr_scalar_axisymmetric_tail_convergence.csv`
- `../../results/kerr_scalar_angular_convergence.csv`
- `../../results/kerr_scalar_nonlinear_channels.csv`
- `../../results/kerr_scalar_nonlinear_channel_convergence.csv`
- `../../results/kerr_scalar_superradiant_response_N288.csv`
- `../../results/kerr_scalar_superradiant_response_N320.csv`
- `../../results/kerr_scalar_superradiant_near_threshold_N288.csv`
- `../../results/kerr_scalar_superradiant_near_threshold_N320.csv`
- `../../results/kerr_scalar_superradiant_highspin_dense_N288.csv`
- `../../results/kerr_scalar_superradiant_highspin_dense_N320.csv`
- `../../results/kerr_scalar_superradiant_response_accepted.csv`
- `../../results/kerr_scalar_superradiant_threshold_limits.csv`
- `../../results/kerr_scalar_superradiant_highspin_peaks.csv`
- `../../results/kerr_scalar_superradiant_matching_convergence.csv`
- `../../results/kerr_scalar_newphysics_threshold_N144.csv`
- `../../results/kerr_scalar_newphysics_threshold_N176.csv`
- `../../results/kerr_scalar_newphysics_extreme_threshold_N144.csv`
- `../../results/kerr_scalar_newphysics_extreme_threshold_N176.csv`
- `../../results/kerr_scalar_newphysics_highl_threshold_N144.csv`
- `../../results/kerr_scalar_newphysics_highl_threshold_N176.csv`
- `../../results/kerr_scalar_newphysics_subdominant_threshold_N144.csv`
- `../../results/kerr_scalar_newphysics_subdominant_threshold_N176.csv`
- `../../results/kerr_scalar_near_extremal_scaling_N144.csv`
- `../../results/kerr_scalar_near_extremal_scaling_N176.csv`
- `../../results/kerr_scalar_near_extremal_peakdense_N144.csv`
- `../../results/kerr_scalar_near_extremal_peakdense_N176.csv`
- `../../results/kerr_scalar_near_extremal_threshold_summary.csv`
- `../../results/kerr_scalar_near_extremal_scaling_convergence.csv`
- `../../results/kerr_scalar_near_extremal_collapse_summary.csv`
- `../../results/kerr_scalar_near_extremal_subdominant_summary.csv`
- `../../results/kerr_scalar_near_extremal_peak_summary.csv`
- `../../results/kerr_scalar_near_extremal_mode_crossings.csv`
- `../../results/kerr_scalar_near_extremal_l0_N144.csv`
- `../../results/kerr_scalar_near_extremal_l0_N176.csv`
- `../../results/kerr_scalar_near_extremal_l0_highspin_N224.csv`
- `../../results/kerr_scalar_near_extremal_l0_highspin_N256.csv`
- `../../results/kerr_scalar_l0_zero_frequency_summary.csv`
- `../../results/kerr_scalar_axisymmetric_infrared_N144.csv`
- `../../results/kerr_scalar_axisymmetric_infrared_N176.csv`
- `../../results/kerr_scalar_axisymmetric_infrared_fits.csv`
- `../../results/kerr_scalar_spin_limit.csv`

To rebuild the plotted quantities after the numerical sweeps already exist:

```powershell
cd ..\..
python scripts\plot_kerr_scalar_low_frequency_axisymmetric.py
python scripts\plot_kerr_scalar_nonlinear_axisymmetric_base_like.py
python scripts\analyze_kerr_scalar_peak_window_sensitivity.py
python scripts\analyze_kerr_scalar_tail_window_sensitivity.py
python scripts\analyze_kerr_scalar_tail_models.py
python scripts\analyze_kerr_scalar_superradiant_response.py
python scripts\analyze_kerr_scalar_near_extremal_scaling.py
python scripts\analyze_kerr_scalar_modal_powerlaws.py
python scripts\analyze_kerr_scalar_l0_zero_frequency.py
python scripts\run_kerr_scalar_axisymmetric_infrared.py --N 144 --quad-order 144 --output results\kerr_scalar_axisymmetric_infrared_N144.csv
python scripts\run_kerr_scalar_axisymmetric_infrared.py --N 176 --quad-order 176 --output results\kerr_scalar_axisymmetric_infrared_N176.csv
python scripts\plot_kerr_scalar_axisymmetric_accuracy.py
python scripts\plot_kerr_scalar_spin_limit.py
python scripts\build_prd_convergence_summary.py
```

The package is self-contained for the manuscript build, all listed artifact
checks, and regeneration of the figures and compact tables from the included
CSV inputs.  The expensive raw frequency sweeps and channel scans require the
full repository checkout and solver source tree; their commands below are
reproduction recipes for that checkout, not package-local commands.

To only check that the rounded numbers in Tables I--XIII and the low-frequency
slopes still agree with the tracked CSV data, and that the frozen figure/CSV
artifacts have not drifted:

```powershell
python scripts\check_prd_artifacts.py
python scripts\check_prd_citations.py
python scripts\check_prd_manuscript_numbers.py
python -m pytest -q
```

The CSV field `status=ok` means that the solver call completed.  The manuscript
acceptance gate is applied separately to the recorded absolute first-order
flux-balance residual; therefore a completed row can be retained in the audit
trail while being excluded from a high-precision claim.

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

The manuscript's Data and code availability statement describes the frozen
review package accurately: it is available to editors and referees upon
reasonable request while the versioned public release is being prepared.  Do
not replace that wording with a moving development-branch URL.  Before
publication, deposit the accepted frozen package in a public archive, add its
persistent data/software citation to the reference list, and update the
statement with that identifier.

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

To regenerate the representative spectral-accuracy CSV files used in Fig. 3,
including 600 off-grid Chebyshev--Gauss residual samples per homogeneous
branch:

```powershell
python scripts\run_kerr_scalar_spectral_quality.py `
  --label kerr_a05_l2m0_peak --l 2 --m 0 --a 0.5 --omega 0.52 `
  --N-outer 240 --N-inner 240 --quad-order 192 --r-match 40 `
  --coeff-output results\kerr_scalar_axisymmetric_spectral_coefficients.csv `
  --residual-output results\kerr_scalar_axisymmetric_spectral_residuals.csv `
  --summary-output results\kerr_scalar_axisymmetric_spectral_quality_summary.csv `
  --skip-flux-convergence
```

To regenerate the independent spheroidal-basis and angular-quadrature audit:

```powershell
python scripts\run_kerr_scalar_angular_convergence.py
```

Full frequency sweeps are more expensive and are run by
`scripts/run_kerr_scalar_nonlinear_frequency_sweep.py`; the tracked CSV files
record the production data used in the manuscript.

The active axisymmetric PRD curves combine the refined sweeps generated by
`scripts/run_prd_axisymmetric_high_order_sweeps.py` with the denser grids in
`kerr_scalar_nonlinear_axisymmetric_dense_l*.csv`.  Both use $N=240$ and
quadrature order $q=192$.  The dense grids contain 45, 33, and 39 samples for
$\ell=0,1,2$, respectively.  The older lower-order sweeps remain in
`results/` as an audit trail but are not used by the active manuscript
figures.  All 43 points in the fitted high-frequency windows are separately
recomputed at $q=2048$ and override duplicate $q=192$ rows in the
postprocessing scripts.

Regenerate only the dense low-to-peak grids sequentially with the same memory
guard used for the present data:

```powershell
python scripts\run_prd_axisymmetric_high_order_sweeps.py `
  --suite dense --max-rss-mb 800
```

Regenerate the complete $q=2048$ tail-fit grids with the same memory guard:

```powershell
python scripts\run_prd_axisymmetric_high_order_sweeps.py `
  --suite tail --max-rss-mb 800
```

The production-resolution audit is generated by
`scripts/run_prd_axisymmetric_production_convergence.py`; it records RSS and
the relative changes in the Green amplitudes and flux coefficients for each
representative peak point.

The lowest-accepted-point flux audit is generated by
`scripts/run_prd_axisymmetric_low_frequency_convergence.py`.  It runs
sequentially, records RSS, and varies $N$, $q$, and $r_{\rm m}$ for the lowest
displayed point of each multipole.  Those points are selected by the common
$|T^{(1)}+R^{(1)}|\leq10^{-8}$ gate, and both first-order boundary fluxes are
stable in the reported scan.

The high-frequency quadrature audit is generated by
`scripts/run_prd_axisymmetric_tail_convergence.py`.  It compares $q=1792$ and
$q=2048$ at three representative tail points and also lowers the Chebyshev
order from $N=240$ to $N=224$ at fixed $q=2048$.

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

The cross-spin non-axisymmetric superradiant survey used in the active draft is
reproduced sequentially with the bounded-memory commands below.  Repeat the
coarse command with `N=320`, `quad-order=384`, and the corresponding output
name; the near-threshold and high-spin dense grids use the same two resolution
pairs.

```powershell
python scripts\run_kerr_scalar_superradiant_response_scan.py `
  --output results\kerr_scalar_superradiant_response_N288.csv `
  --spins 0.3,0.5,0.7,0.9 --modes 1:1,2:2 `
  --omega-fractions 0.60,0.75,0.90,0.97,1.03,1.10,1.25,1.50 `
  --N 288 --quad-order 320 --linear-solver equilibrated --max-rss-mb 1800
python scripts\run_kerr_scalar_superradiant_response_scan.py `
  --output results\kerr_scalar_superradiant_near_threshold_N288.csv `
  --spins 0.5,0.7,0.9 --modes 1:1,2:2 `
  --omega-fractions 0.99,0.999,1.001,1.01 `
  --N 288 --quad-order 320 --linear-solver equilibrated --max-rss-mb 1800
python scripts\run_kerr_scalar_superradiant_response_scan.py `
  --output results\kerr_scalar_superradiant_highspin_dense_N288.csv `
  --spins 0.9 --modes 1:1,2:2 `
  --omega-fractions 1.10,1.15,1.20,1.25,1.30,1.35,1.40,1.45,1.50,1.60,1.75,2.00 `
  --N 288 --quad-order 320 --linear-solver equilibrated --max-rss-mb 1800
python scripts\analyze_kerr_scalar_superradiant_response.py
```

The near-extremal response is generated in the variables
`y=(omega-m*Omega_H)/kappa` and `Xi=M*kappa*chi_H`.  The production curve scan
is run at two resolutions, followed by the common threshold/collapse analysis:

```powershell
python scripts\run_kerr_scalar_near_extremal_scaling.py `
  --output results\kerr_scalar_near_extremal_scaling_N144.csv `
  --spins 0.98,0.99,0.995 --modes 2:2,3:3 `
  --detunings=-0.5,-0.2,-0.05,0.05,0.2,0.4,0.6,0.8,1.0,1.2 `
  --N 144 --quad-order 144 --max-rss-mb 1000
python scripts\run_kerr_scalar_near_extremal_scaling.py `
  --output results\kerr_scalar_near_extremal_scaling_N176.csv `
  --spins 0.98,0.99,0.995 --modes 2:2,3:3 `
  --detunings=-0.5,-0.2,-0.05,0.05,0.2,0.4,0.6,0.8,1.0,1.2 `
  --N 176 --quad-order 176 --max-rss-mb 1000
python scripts\analyze_kerr_scalar_near_extremal_scaling.py
```

The threshold, dense-peak, high-multipole, and `m<l` control CSV pairs listed
above are analyzed by the same script.  Exact `p=0` is not sampled because the
horizon Frobenius roots coalesce there; the threshold is extrapolated from
symmetric nonzero detunings while the radial grid retains the event-horizon
endpoint.

The scalar-monopole control uses the same endpoint-inclusive route with
`m=0`, so `y=omega/kappa`.  The following pairs cover
`a=0,0.5,0.9,0.98,0.99,0.995,0.997,0.999`; the higher-order pair stabilizes
the `a=0.997` extrapolation.  The analysis script compares the fitted
zero-frequency limit with the exact value `log(2)/pi`.

```powershell
python scripts\run_kerr_scalar_near_extremal_scaling.py `
  --output results\kerr_scalar_near_extremal_l0_N144.csv `
  --spins 0,0.5,0.9,0.98,0.99,0.995,0.997,0.999 --modes 0:0 `
  --detunings 0.0125,0.025,0.05,0.1,0.2,0.5,1,2,4,8 `
  --N 144 --quad-order 144 --max-rss-mb 1000
python scripts\run_kerr_scalar_near_extremal_scaling.py `
  --output results\kerr_scalar_near_extremal_l0_N176.csv `
  --spins 0,0.5,0.9,0.98,0.99,0.995,0.997,0.999 --modes 0:0 `
  --detunings 0.0125,0.025,0.05,0.1,0.2,0.5,1,2,4,8 `
  --N 176 --quad-order 176 --max-rss-mb 1000
python scripts\run_kerr_scalar_near_extremal_scaling.py `
  --output results\kerr_scalar_near_extremal_l0_highspin_N224.csv `
  --spins 0.997,0.999 --modes 0:0 --detunings 0.0125,0.025,0.05 `
  --N 224 --quad-order 224 --max-rss-mb 1000
python scripts\run_kerr_scalar_near_extremal_scaling.py `
  --output results\kerr_scalar_near_extremal_l0_highspin_N256.csv `
  --spins 0.997,0.999 --modes 0:0 --detunings 0.0125,0.025,0.05 `
  --N 256 --quad-order 256 --max-rss-mb 1000
python scripts\analyze_kerr_scalar_l0_zero_frequency.py
```

The higher odd-power monopole control is generated at fixed frequency and at
fixed `omega/kappa`, then paired across two spectral resolutions:

```powershell
python scripts\run_kerr_scalar_power_nonlinearity_l0.py `
  --output results\kerr_scalar_power_nonlinearity_l0_fixed_N144.csv `
  --spins 0,0.5,0.9,0.99,0.999 --orders 2,3 --frequency-mode fixed `
  --frequencies 0.0005,0.00075,0.001,0.0015,0.002,0.003,0.005 `
  --N 144 --quad-order 144 --max-rss-mb 500
python scripts\run_kerr_scalar_power_nonlinearity_l0.py `
  --output results\kerr_scalar_power_nonlinearity_l0_kappa_N144.csv `
  --spins 0.98,0.99,0.995,0.997,0.999 --orders 2,3 --frequency-mode kappa `
  --frequencies 0.025,0.05,0.1 --N 144 --quad-order 144 --max-rss-mb 500
python scripts\analyze_kerr_scalar_power_nonlinearity_l0.py
python scripts\plot_kerr_scalar_power_nonlinearity_l0.py
```

Repeat the two runner commands with `N=176`, `quad-order=176`, and the `N176`
output names before running the analyzer.  The manuscript also freezes a
representative 600-point-per-branch off-grid residual audit produced with
`run_kerr_scalar_spectral_quality.py` at `l=m=0`, `a=0.5`, and
`omega=0.0005`.

The higher-power nonaxisymmetric scan uses the same threshold extrapolation
and paired-resolution gates:

```powershell
python scripts\run_kerr_scalar_power_near_extremal.py `
  --output results\kerr_scalar_power_near_extremal_N144.csv `
  --orders 2,3 --spins 0.98,0.99,0.995,0.997,0.999 `
  --modes 1:1,2:2 --detunings=-0.5,-0.05,-0.025,0.025,0.05,0.5,1 `
  --N 144 --quad-order 144 --max-rss-mb 1000
python scripts\run_kerr_scalar_power_near_extremal.py `
  --output results\kerr_scalar_power_near_extremal_additional_N144.csv `
  --orders 2,3 --spins 0.98,0.99,0.995,0.997,0.999 `
  --modes 2:1,3:3 --detunings=-0.05,-0.025,0.025,0.05,0.5 `
  --N 144 --quad-order 144 --max-rss-mb 1000
python scripts\analyze_kerr_scalar_power_near_extremal.py
python scripts\analyze_kerr_scalar_cft_factorization.py
python scripts\run_kerr_scalar_power_angular_convergence.py
```

Repeat the two base commands at `N=176`.  The extreme files use
`a=0.9995,0.9998,0.9999`, `N=224/256`, and the five-detuning grid of the
additional command.  The dense principal files add
`a=0.99995,0.999975,0.9999875,0.99999375` at `N=256/288`; the ultra pair adds
`a=0.999996875,0.9999984375` at `N=288/320`.  All raw rows are retained; the
analyzer excludes any row that fails paired response, linear balance,
Wronskian constancy, or both the absolute and flux-relative first-order
balance gates.  The manuscript uses seven-point principal fits and records
95% slope intervals plus leave-one-out errors.
The factorization audit uses only accepted rows with directly recorded
`B_inc_abs`; it fits the response, fixed-incident horizon intensity, and
unit-horizon nonlinear kernel separately at fixed nonzero `p/kappa` and in
the iterated threshold limit.

The finite-bandwidth and dense-peak extension is reproduced with paired
spectral orders:

```powershell
python scripts\run_kerr_scalar_power_near_extremal.py `
  --output results\kerr_scalar_power_band_N256.csv `
  --orders 2,3 --spins 0.995,0.9999,0.99999375 --modes 2:2,3:3 `
  --detunings=-0.5,-0.2,-0.05,0.05,0.2,0.4,0.6,0.8,1.0,1.2 `
  --N 256 --quad-order 256 --max-rss-mb 800
python scripts\run_kerr_scalar_power_near_extremal.py `
  --output results\kerr_scalar_power_peakdense_N288.csv `
  --orders 1,2,3 --spins 0.9999 --modes 2:2,3:3 `
  --detunings=0.75,0.8,0.85,0.9,0.95,1.0,1.05,1.1,1.15,1.2 `
  --N 288 --quad-order 288 --max-rss-mb 800
python scripts\analyze_kerr_scalar_bandwidth_hierarchy.py
```

Repeat the first command at `N=288` and the second at `N=320` with the
corresponding output names.  The analyzer requires identical paired grids,
applies the same response, flux, and Wronskian gates, integrates the fixed
throat window, and fits each dense peak only when a five-point local
neighborhood is available.

The internal Kerr-to-Schwarzschild continuity audit used in the active draft
is reproduced with the bounded serial commands:

```powershell
python scripts\run_kerr_scalar_spin_limit.py --max-rss-mb 1500
python scripts\plot_kerr_scalar_spin_limit.py
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
