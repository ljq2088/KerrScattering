# Kerr s=0 spectral validation report

## Scope

This report validates the two-domain Chebyshev spectral solver for the scalar
Teukolsky in mode on Kerr. The solver uses `z = r_+/r`, direct endpoint
collocation at `z=0,1`, degenerate endpoint ODE rows as regularity
conditions, and value/derivative matching at an intermediate radius.

The external benchmark is `GeneralizedSasakiNakamura.jl` with the
`UNIT_TEUKOLSKY_TRANS` convention, so `B_trans = 1` at the horizon.

## Acceptance gates

- `rel_abs_B_inc <= 1e-7`
- `rel_abs_B_ref <= 1e-7`
- `flux_balance_error <= 1e-8`

Only amplitude magnitudes and flux balance are used as pass/fail quantities.
The complex amplitudes include convention-dependent phase factors from the
additive constant in `r*` and package-specific normalization choices; those
phase factors are recorded in the CSV output but are not used as invariant
benchmark errors.

## Summary

- Cases tested: 12
- All cases passed: `true`
- Worst score: `1.485e-08`
- Worst flux-balance residual: `6.144e-10`

| l | m | a | omega | N | r_match | mapping | rel_abs_B_inc | rel_abs_B_ref | flux | score | passed |
|---:|---:|---:|---:|---:|---:|:---|---:|---:|---:|---:|:---|
| 0 | 0 | 0 | 0.1 | 96 | 10 | linear | 3.407e-12 | 5.774e-13 | 2.837e-12 | 3.407e-12 | true |
| 0 | 0 | 0.5 | 0.1 | 128 | 8 | linear | 2.011e-12 | 1.359e-12 | 1.040e-12 | 2.011e-12 | true |
| 1 | 1 | 0.5 | 0.1 | 224 | 6 | linear | 9.427e-12 | 8.895e-12 | 1.028e-12 | 9.427e-12 | true |
| 2 | 1 | 0.5 | 0.3 | 160 | 30 | linear | 1.825e-10 | 1.823e-10 | 1.523e-13 | 1.825e-10 | true |
| 2 | 2 | 0.5 | 0.01 | 80 | 8 | sinh | 1.571e-09 | 1.571e-09 | 3.331e-16 | 1.571e-09 | true |
| 2 | 2 | 0.5 | 0.1 | 192 | 40 | linear | 5.039e-10 | 5.044e-10 | 1.107e-12 | 5.044e-10 | true |
| 2 | 2 | 0.5 | 0.25 | 160 | 12 | linear | 1.965e-10 | 1.968e-10 | 6.986e-13 | 1.968e-10 | true |
| 2 | 2 | 0.5 | 0.3 | 160 | 30 | linear | 6.524e-10 | 6.522e-10 | 4.885e-13 | 6.524e-10 | true |
| 2 | 2 | 0.5 | 1 | 224 | 20 | linear | 3.072e-10 | 1.485e-08 | 6.144e-10 | 1.485e-08 | true |
| 2 | 2 | 0.9 | 0.05 | 224 | 25 | sinh | 3.800e-11 | 3.796e-11 | 8.860e-14 | 3.800e-11 | true |
| 2 | 2 | 0.9 | 0.5 | 192 | 25 | linear | 1.109e-10 | 1.104e-10 | 5.466e-13 | 1.109e-10 | true |
| 3 | 2 | 0.9 | 0.2 | 224 | 6 | linear | 8.015e-11 | 8.015e-11 | 0.000e+00 | 8.015e-11 | true |

## Current interpretation

The present validation covers the Schwarzschild limit, moderate Kerr spin,
near-superradiant scalar modes, low-frequency superradiant scattering,
high-frequency small-reflection scattering, and high-spin Kerr cases.

The worst invariant benchmark error in the current table is below `1.5e-8`,
which is comfortably inside the `1e-7` amplitude-magnitude target. The
hardest case is the high-frequency `l=m=2, a=0.5, omega=1.0` mode, where
`B_ref` is small and therefore relative errors are more sensitive to
conditioning.

## Remaining PRD-level work

- Expand the benchmark grid before using final production tables.
- Add publication plots for transmission/reflection versus frequency.
- State the complex phase convention explicitly if phase-sensitive
  observables are reported.
- Carry the nonlinear Green-function correction over from the Schwarzschild
  project only after the linear solver validation remains stable on a denser
  grid.

Generated from `results/kerr_scalar_adaptive_summary.csv`.
