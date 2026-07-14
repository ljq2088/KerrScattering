# Results Directory

This directory stores numerical CSV inputs for the Kerr scalar scattering and
weak nonlinear Green-function calculations.

The PRD-style Kerr `s=0`, `a=0.5`, `m=0` nonlinear manuscript uses these
tracked result files:

- `kerr_scalar_nonlinear_axisymmetric_hires_l0.csv`
- `kerr_scalar_nonlinear_axisymmetric_hires_l1.csv`
- `kerr_scalar_nonlinear_axisymmetric_hires_l2.csv`
- `kerr_scalar_nonlinear_axisymmetric_refine_l0.csv`
- `kerr_scalar_nonlinear_axisymmetric_refine_l1.csv`
- `kerr_scalar_nonlinear_axisymmetric_refine_l2.csv`
- `kerr_scalar_nonlinear_axisymmetric_fit_table.csv`
- `kerr_scalar_low_frequency_axisymmetric_slopes.csv`
- `kerr_scalar_axisymmetric_spectral_coefficients.csv`
- `kerr_scalar_axisymmetric_spectral_residuals.csv`
- `kerr_scalar_axisymmetric_spectral_quality_summary.csv`
- `kerr_scalar_nonlinear_convergence_summary.csv`
- `kerr_scalar_axisymmetric_production_convergence.csv`

Most exploratory CSV files are intentionally ignored by git.  The files above
are unignored because they are direct inputs to
`docs/prd/kerr_scalar_nonlinear_GF_baseframe.tex`.  The older lower-order
axisymmetric sweeps remain as an audit trail; the active PRD figures use the
`hires` files at $N=240$ and quadrature order $q=192$.
