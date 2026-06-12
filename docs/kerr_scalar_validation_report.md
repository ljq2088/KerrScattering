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

## Phase convention

The spectral code reports amplitudes in its own Kerr tortoise coordinate
convention. At infinity the basis is
`exp(-i omega r*)/r` for the incident wave and `exp(+i omega r*)/r`
for the reflected wave; at the horizon the unit-amplitude in-mode uses
`exp[-i (omega - m Omega_H) r*]`. If another package uses
`r* -> r* + C`, then the complex coefficients transform by
`B_inc -> B_inc exp(-i omega C)` and
`B_ref -> B_ref exp(+i omega C)` in the infinity basis. Therefore the
magnitudes, reflection probability, transmission probability, and flux
balance are the benchmark quantities used for pass/fail validation.

## Summary

- GSN benchmark requests: 37
- Usable GSN benchmark cases tested: 37
- GSN benchmark cases excluded: 0
- All cases passed: `true`
- Worst score: `1.485e-08`
- Worst flux-balance residual: `3.714e-09`

| l | m | a | omega | N | r_match | mapping | rel_abs_B_inc | rel_abs_B_ref | flux | score | passed |
|---:|---:|---:|---:|---:|---:|:---|---:|---:|---:|---:|:---|
| 0 | 0 | 0 | 0.01 | 64 | 40 | sinh | 1.379e-12 | 1.298e-12 | 3.006e-13 | 1.379e-12 | true |
| 0 | 0 | 0 | 0.1 | 96 | 10 | linear | 3.407e-12 | 5.774e-13 | 2.837e-12 | 3.407e-12 | true |
| 0 | 0 | 0 | 0.5 | 192 | 15 | linear | 9.610e-13 | 2.739e-11 | 1.956e-12 | 2.739e-11 | true |
| 1 | 0 | 0 | 0.1 | 128 | 40 | linear | 3.080e-12 | 3.205e-12 | 7.772e-14 | 3.205e-12 | true |
| 1 | 0 | 0 | 0.5 | 224 | 30 | linear | 3.458e-12 | 6.136e-12 | 6.731e-12 | 6.731e-12 | true |
| 0 | 0 | 0.5 | 0.1 | 128 | 8 | linear | 2.011e-12 | 1.359e-12 | 1.040e-12 | 2.011e-12 | true |
| 1 | 0 | 0.5 | 0.1 | 96 | 15 | linear | 4.929e-12 | 4.894e-12 | 5.140e-14 | 4.929e-12 | true |
| 2 | 0 | 0.5 | 0.1 | 96 | 25 | linear | 4.503e-11 | 4.500e-11 | 5.862e-14 | 4.503e-11 | true |
| 2 | 0 | 0.5 | 0.5 | 96 | 10 | linear | 6.970e-13 | 5.767e-13 | 8.209e-13 | 8.209e-13 | true |
| 1 | 1 | 0.5 | 0.05 | 160 | 40 | sinh | 2.319e-10 | 2.313e-10 | 1.150e-12 | 2.319e-10 | true |
| 1 | 1 | 0.5 | 0.1 | 224 | 6 | linear | 9.427e-12 | 8.895e-12 | 1.028e-12 | 9.427e-12 | true |
| 1 | 1 | 0.5 | 0.2 | 224 | 25 | linear | 3.269e-10 | 3.256e-10 | 3.448e-12 | 3.269e-10 | true |
| 2 | 1 | 0.5 | 0.05 | 112 | 25 | sinh | 5.922e-10 | 5.922e-10 | 8.882e-16 | 5.922e-10 | true |
| 2 | 1 | 0.5 | 0.1 | 192 | 6 | linear | 1.074e-09 | 1.074e-09 | 1.665e-15 | 1.074e-09 | true |
| 2 | 1 | 0.5 | 0.3 | 160 | 30 | linear | 1.825e-10 | 1.823e-10 | 1.523e-13 | 1.825e-10 | true |
| 2 | 1 | 0.5 | 0.8 | 224 | 15 | linear | 2.773e-10 | 4.493e-09 | 5.564e-10 | 4.493e-09 | true |
| 2 | 2 | 0.5 | 0.01 | 128 | 40 | sinh | 1.945e-10 | 1.945e-10 | 3.331e-16 | 1.945e-10 | true |
| 2 | 2 | 0.5 | 0.05 | 192 | 20 | sinh | 1.846e-10 | 1.846e-10 | 1.110e-14 | 1.846e-10 | true |
| 2 | 2 | 0.5 | 0.1 | 192 | 40 | linear | 5.039e-10 | 5.044e-10 | 1.107e-12 | 5.044e-10 | true |
| 2 | 2 | 0.5 | 0.24 | 224 | 40 | linear | 5.147e-10 | 5.148e-10 | 1.985e-13 | 5.148e-10 | true |
| 2 | 2 | 0.5 | 0.25 | 160 | 12 | linear | 1.965e-10 | 1.968e-10 | 6.986e-13 | 1.968e-10 | true |
| 2 | 2 | 0.5 | 0.26 | 128 | 40 | linear | 2.433e-11 | 2.431e-11 | 3.642e-14 | 2.433e-11 | true |
| 2 | 2 | 0.5 | 0.275 | 224 | 40 | linear | 1.121e-10 | 1.122e-10 | 1.443e-13 | 1.122e-10 | true |
| 2 | 2 | 0.5 | 0.3 | 160 | 30 | linear | 6.524e-10 | 6.522e-10 | 4.885e-13 | 6.524e-10 | true |
| 2 | 2 | 0.5 | 0.6 | 224 | 40 | linear | 2.350e-10 | 3.870e-10 | 1.601e-10 | 3.870e-10 | true |
| 2 | 2 | 0.5 | 1 | 224 | 20 | linear | 3.072e-10 | 1.485e-08 | 6.144e-10 | 1.485e-08 | true |
| 2 | 2 | 0.9 | 0.02 | 192 | 30 | sinh | 9.144e-10 | 9.144e-10 | 5.551e-16 | 9.144e-10 | true |
| 2 | 2 | 0.9 | 0.05 | 224 | 25 | sinh | 3.800e-11 | 3.796e-11 | 8.860e-14 | 3.800e-11 | true |
| 2 | 2 | 0.9 | 0.2 | 224 | 8 | linear | 1.552e-11 | 1.563e-11 | 2.092e-13 | 1.563e-11 | true |
| 2 | 2 | 0.9 | 0.5 | 192 | 25 | linear | 1.109e-10 | 1.104e-10 | 5.466e-13 | 1.109e-10 | true |
| 2 | 2 | 0.9 | 0.58 | 224 | 40 | linear | 1.079e-10 | 1.082e-10 | 3.366e-13 | 1.082e-10 | true |
| 2 | 2 | 0.9 | 0.62 | 128 | 12 | linear | 5.958e-10 | 5.980e-10 | 4.145e-12 | 5.980e-10 | true |
| 2 | 2 | 0.9 | 0.65 | 160 | 25 | linear | 2.447e-10 | 2.483e-10 | 4.032e-12 | 2.483e-10 | true |
| 2 | 2 | 0.9 | 0.9 | 224 | 10 | linear | 1.863e-09 | 1.173e-09 | 3.714e-09 | 3.714e-09 | true |
| 3 | 2 | 0.9 | 0.05 | 96 | 20 | sinh | 1.045e-09 | 1.045e-09 | 0.000e+00 | 1.045e-09 | true |
| 3 | 2 | 0.9 | 0.2 | 224 | 6 | linear | 8.015e-11 | 8.015e-11 | 0.000e+00 | 8.015e-11 | true |
| 3 | 2 | 0.9 | 0.6 | 128 | 20 | linear | 2.250e-10 | 2.251e-10 | 1.458e-13 | 2.251e-10 | true |

## Frequency sweep

A publication-style frequency sweep is generated by
`scripts/run_kerr_scalar_frequency_sweep.py` and plotted by
`scripts/plot_kerr_scalar_frequency_sweep.py`. The sweep uses
self-convergence in spectral order, the same direct endpoint rows, and
the invariant flux balance check.

- Sweep points: 51
- All sweep points passed: `true`
- Worst sweep score: `9.467e-08`
- Worst sweep flux-balance residual: `7.351e-09`
- Maximum sampled superradiant amplification: `4.970e-04` at `kerr_a09_l2m2`, `omega=0.58`

| label | l | m | a | omega range | points | max R-1 | all passed |
|:---|---:|---:|---:|:---|---:|---:|:---|
| kerr_a05_l2m2 | 2 | 2 | 0.5 | 0.01--1 | 20 | 2.373e-06 | true |
| kerr_a09_l2m2 | 2 | 2 | 0.9 | 0.02--1.1 | 20 | 4.970e-04 | true |
| schwarzschild_l0 | 0 | 0 | 0 | 0.01--1 | 11 | -1.714e-03 | true |

## Cubic angular projector

The Kerr nonlinear source requires the spheroidal projection
`C_{l'lm} = int dOmega conj(S_l'm) |S_lm|^2 S_lm`. The table
`results/kerr_scalar_cubic_couplings.csv` evaluates these coefficients
for every validated source mode and target channels `|m| <= l' <= l+4`.

- Source modes projected: 37
- Coupling rows: 199
- Self-channel coefficient range: `7.958e-02` to `1.705e-01`
- Largest off-diagonal coefficient: `8.318e-02` for `l=2, m=0, a=0.5, omega=0.1, l'=4`

## Current interpretation

The present validation covers the Schwarzschild limit, moderate Kerr spin,
near-superradiant scalar modes, low-frequency superradiant scattering,
high-frequency small-reflection scattering, and high-spin Kerr cases.
The GSN benchmark grid now includes nonrotating checks, non-superradiant
`m=0` modes, multiple `l=1,2,3` modes, and rotating cases on both sides
of `omega = m Omega_H`.

The worst invariant benchmark error in the current table is below `1.5e-8`,
which is comfortably inside the `1e-7` amplitude-magnitude target. The
hardest case is the high-frequency `l=m=2, a=0.5, omega=1.0` mode, where
`B_ref` is small and therefore relative errors are more sensitive to
conditioning.

The frequency sweep resolves the Schwarzschild absorption curve and the
Kerr scalar superradiant regime. For the sampled rotating cases, `R > 1`
appears only for `omega < m Omega_H`, while the reported flux residuals
remain below the acceptance gate.

The angular cubic projector is now explicit, so the remaining nonlinear
work is reduced to the radial Green-function source integrals and their
convergence validation.

## Remaining PRD-level work

- Carry the nonlinear Green-function correction over from the Schwarzschild
  project only after the linear solver validation remains stable on a denser
  grid.

Generated from `results/kerr_scalar_adaptive_summary.csv`,
`results/kerr_scalar_frequency_sweep.csv`, and
`results/kerr_scalar_cubic_couplings.csv` when available.
