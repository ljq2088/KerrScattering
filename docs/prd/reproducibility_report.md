# Kerr Scalar PRD Reproducibility Report

Generated from build epoch: `2024-01-01T00:00:00+00:00`
Build `SOURCE_DATE_EPOCH`: `1704067200`

This report records the local artifacts used by the active PRD-style draft `docs/prd/kerr_scalar_nonlinear_GF_baseframe.tex`.

## Manuscript Files

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| docs/prd/kerr_scalar_nonlinear_GF_baseframe.tex | 66856 | `390f63bff4119a7590965a754a6639bcfb613835ba14fb04f89f9efcc5fa323c` |
| docs/prd/kerr_scalar_nonlinear_GF_baseframe.pdf | 908589 | `40a110b88043d1a7b45855ab8b09d989fa0909d5d36324fcb7095deedbb83dda` |
| kerr_scalar_nonlinear_GF_baseframe.pdf | 908589 | `40a110b88043d1a7b45855ab8b09d989fa0909d5d36324fcb7095deedbb83dda` |
| docs/prd/artifact_manifest.json | 11341 | `2c791c2a5379b6609a2af963aedf03c033dfd6576cf8bf82f298c5c2dc8ca392` |

## Frozen Figure And CSV Inputs

| Path | Kind | Rows/size | Bytes | SHA-256 |
| --- | --- | ---: | ---: | --- |
| figures/kerr_scalar_low_frequency_axisymmetric.png | figure | 2016x780 px | 98629 | `e80025cc25b633aa` |
| figures/kerr_scalar_nonlinear_axisymmetric_fig2.png | figure | 2016x780 px | 169154 | `e09c0dcc1ccabb15` |
| figures/kerr_scalar_axisymmetric_accuracy.png | figure | 2064x648 px | 197352 | `dd442939630be16f` |
| figures/kerr_scalar_nonlinear_superradiant_m2.png | figure | 1700x718 px | 87486 | `79f208721a1439ea` |
| figures/kerr_scalar_spin_limit.png | figure | 2034x747 px | 111671 | `b25da671217485bf` |
| results/kerr_scalar_nonlinear_axisymmetric_hires_l0.csv | csv | 12 rows | 8878 | `80f8ee263ec4b51b` |
| results/kerr_scalar_nonlinear_axisymmetric_hires_l1.csv | csv | 13 rows | 9616 | `68acae26d7f0f092` |
| results/kerr_scalar_nonlinear_axisymmetric_hires_l2.csv | csv | 13 rows | 9599 | `255497f8267fb41c` |
| results/kerr_scalar_nonlinear_axisymmetric_refine_l0.csv | csv | 4 rows | 3153 | `8ce315828307fa20` |
| results/kerr_scalar_nonlinear_axisymmetric_refine_l1.csv | csv | 3 rows | 2454 | `5c4203c1f3fbbe15` |
| results/kerr_scalar_nonlinear_axisymmetric_refine_l2.csv | csv | 2 rows | 1744 | `8bf89e24b207d34d` |
| results/kerr_scalar_nonlinear_control_scan.csv | csv | 24 rows | 8970 | `de9ae6a3b1716795` |
| results/kerr_scalar_nonlinear_diagnostics.csv | csv | 16 rows | 9831 | `4481c891a4b40fb5` |
| results/kerr_scalar_nonlinear_axisymmetric_fit_table.csv | csv | 3 rows | 1080 | `069685f48edb0f68` |
| results/kerr_scalar_nonlinear_tail_window_sensitivity.csv | csv | 12 rows | 1376 | `7310eeb06cc9e294` |
| results/kerr_scalar_low_frequency_axisymmetric_slopes.csv | csv | 3 rows | 272 | `f7be0dfd358c9f50` |
| results/kerr_scalar_low_frequency_axisymmetric_window_sensitivity.csv | csv | 9 rows | 779 | `cdf48c17abb14b59` |
| results/kerr_scalar_axisymmetric_spectral_coefficients.csv | csv | 723 rows | 77593 | `c16c276517f1511c` |
| results/kerr_scalar_axisymmetric_spectral_residuals.csv | csv | 720 rows | 159937 | `ea06533b4f44ccea` |
| results/kerr_scalar_axisymmetric_spectral_quality_summary.csv | csv | 3 rows | 1132 | `0114d2e345631ba2` |
| results/kerr_scalar_nonlinear_convergence_summary.csv | csv | 3 rows | 800 | `227e6e4f0195e882` |
| results/kerr_scalar_axisymmetric_production_convergence.csv | csv | 15 rows | 9155 | `1a6ef6a975a211f8` |
| results/kerr_scalar_nonlinear_channels.csv | csv | 5 rows | 3570 | `bb913a4ce431312a` |
| results/kerr_scalar_nonlinear_channel_convergence.csv | csv | 9 rows | 7501 | `f5b1cb3f3b03fbcb` |
| results/kerr_scalar_nonlinear_m2_superradiant.csv | csv | 10 rows | 7412 | `ab6ba593e7734dbb` |
| results/kerr_scalar_spin_limit.csv | csv | 6 rows | 3693 | `e8c25732b3aa49c7` |

## Checks

### Artifact manifest/schema check

Status: **PASS**

```text
PRD artifact checks passed.
```

### Manuscript numeric consistency check

Status: **PASS**

```text
PRD manuscript numeric checks passed.
```

### Citation integrity check

Status: **PASS**

```text
PRD citation integrity passed (35 cited keys, 35 bibliography entries)
```

### PRD style and structure audit

Status: **PASS**

```text
PRD style and structure audit passed.
```

### Submission readiness audit

Status: **EXPECTED BLOCKERS**

```text
PRD submission readiness audit: NOT READY
- author-placeholder: Replace \author{KerrScattering Collaboration} with the final author list.
- affiliation-placeholder: Replace \affiliation{KerrScattering Project} with final institutional affiliations.
- missing-email: Add at least one corresponding-author \email{...} entry if required by the submission.
- missing-final-metadata: Create docs/prd/submission_metadata.json from the template and fill in final submission details.
```

## Rebuild Commands

```powershell
python scripts\write_prd_artifact_manifest.py
python scripts\build_prd_manuscript.py
python scripts\check_prd_citations.py
python scripts\check_prd_style.py
python scripts\check_prd_submission_ready.py
```

The readiness audit is expected to report blockers until the final author metadata, submission metadata, and cover letter are available.
