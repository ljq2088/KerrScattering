# Kerr Scalar PRD Reproducibility Report

Generated: 2026-07-14T21:24:33

This report records the local artifacts used by the active PRD-style draft `docs/prd/kerr_scalar_nonlinear_GF_baseframe.tex`.

## Manuscript Files

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| docs/prd/kerr_scalar_nonlinear_GF_baseframe.tex | 57750 | `afd53e74d5b19c100c9f4adb16ee7202876c9692c97100a4990bc8a7aefd3738` |
| docs/prd/kerr_scalar_nonlinear_GF_baseframe.pdf | 795193 | `a64c365ee86f14eebf6674499658ff4363bfe29b6be5bf8320eab62d28f67b7b` |
| kerr_scalar_nonlinear_GF_baseframe.pdf | 795193 | `a64c365ee86f14eebf6674499658ff4363bfe29b6be5bf8320eab62d28f67b7b` |
| docs/prd/artifact_manifest.json | 8339 | `1b13d7e14b0766ef9c80a10833557d47f198491f1db909245b053593ece8f997` |

## Frozen Figure And CSV Inputs

| Path | Kind | Rows/size | Bytes | SHA-256 |
| --- | --- | ---: | ---: | --- |
| figures/kerr_scalar_low_frequency_axisymmetric.png | figure | 2016x780 px | 98629 | `e80025cc25b633aa` |
| figures/kerr_scalar_nonlinear_axisymmetric_fig2.png | figure | 2016x780 px | 169154 | `e09c0dcc1ccabb15` |
| figures/kerr_scalar_axisymmetric_accuracy.png | figure | 2064x648 px | 197352 | `dd442939630be16f` |
| figures/kerr_scalar_nonlinear_superradiant_m2.png | figure | 1700x718 px | 87486 | `79f208721a1439ea` |
| results/kerr_scalar_nonlinear_axisymmetric_hires_l0.csv | csv | 12 rows | 8878 | `80f8ee263ec4b51b` |
| results/kerr_scalar_nonlinear_axisymmetric_hires_l1.csv | csv | 13 rows | 9616 | `68acae26d7f0f092` |
| results/kerr_scalar_nonlinear_axisymmetric_hires_l2.csv | csv | 13 rows | 9599 | `255497f8267fb41c` |
| results/tmp_kerr_axisymmetric_refine_l0.csv | csv | 4 rows | 3153 | `8ce315828307fa20` |
| results/tmp_kerr_axisymmetric_refine_l1.csv | csv | 3 rows | 2454 | `5c4203c1f3fbbe15` |
| results/tmp_kerr_axisymmetric_refine_l2.csv | csv | 2 rows | 1744 | `8bf89e24b207d34d` |
| results/kerr_scalar_nonlinear_axisymmetric_fit_table.csv | csv | 3 rows | 916 | `fb941582e78ba557` |
| results/kerr_scalar_low_frequency_axisymmetric_slopes.csv | csv | 3 rows | 272 | `f7be0dfd358c9f50` |
| results/kerr_scalar_axisymmetric_spectral_coefficients.csv | csv | 723 rows | 77593 | `c16c276517f1511c` |
| results/kerr_scalar_axisymmetric_spectral_residuals.csv | csv | 720 rows | 159937 | `ea06533b4f44ccea` |
| results/kerr_scalar_axisymmetric_spectral_quality_summary.csv | csv | 3 rows | 1132 | `0114d2e345631ba2` |
| results/kerr_scalar_nonlinear_convergence_summary.csv | csv | 3 rows | 800 | `227e6e4f0195e882` |
| results/kerr_scalar_axisymmetric_production_convergence.csv | csv | 15 rows | 9155 | `1a6ef6a975a211f8` |
| results/kerr_scalar_nonlinear_channels.csv | csv | 5 rows | 3570 | `bb913a4ce431312a` |
| results/kerr_scalar_nonlinear_channel_convergence.csv | csv | 9 rows | 7501 | `f5b1cb3f3b03fbcb` |
| results/kerr_scalar_nonlinear_m2_superradiant.csv | csv | 10 rows | 7412 | `ab6ba593e7734dbb` |

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
PRD citation integrity passed (34 cited keys, 34 bibliography entries)
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
python scripts\check_prd_submission_ready.py
```

The readiness audit is expected to report blockers until the final author metadata, submission metadata, and cover letter are available.
