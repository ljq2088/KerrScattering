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

## Nonlinear radial diagnostics

`scripts/run_kerr_scalar_nonlinear_diagnostics.py` evaluates
Green-function radial source integrals using the Kerr-covariant
cubic scalar source
`(r^2 C0 + a^2 C2) |R|^2 R` and the physical `dr` measure.
The exterior integral is evaluated after decomposing the outer
homogeneous solutions into `exp(i n omega r*)` phase channels,
so the oscillatory tail is integrated on `r* in [r*_match, inf)`
instead of by a compactified endpoint Gauss rule.

- Diagnostic cases: 4
- Quadrature rows: 16
- Worst Wronskian consistency error: `2.925e-16`
- Worst consecutive `A_ref_1` quadrature change: `1.847e-06`
- Worst consecutive `A_hor_1` quadrature change: `5.398e-06`
- Peak recorded process RSS: `85.4 MB`
- Slowest diagnostic row: `13.35 s`
- Control scan rows: 24
- Largest control-scan reflection change: `3.807e-05`
- Largest control-scan horizon change: `1.067e-07`
The largest reflection control changes occur in deliberately
coarser or farther matching tests; the production rows use
`N=256` and the stable matching window recorded in the CSV.

### Nonlinear target-channel scan

`scripts/run_kerr_scalar_nonlinear_channels.py` performs the
first multi-`l'` extension of the nonlinear Green-function
calculation. The current tracked table scans
`kerr_a05_l2m2_super` with target channels `l'=2,...,6`.

- Channel rows: 5
- Active radial solves: 3
- Skipped zero-coupling channels: 2
- Strongest reflected channel: `l'=2`, `|A_ref_1|=1.137e+06`

| l' | |C0| | |A_ref_1| | |A_H_1| | status |
|---:|---:|---:|---:|:---|
| 2 | 1.136e-01 | 1.137e+06 | 3.804e+03 | ok |
| 3 | 0.000e+00 | 0.000e+00 | 0.000e+00 | skipped-zero-angular-coupling |
| 4 | 3.578e-02 | 1.362e+04 | 1.319e+00 | ok |
| 5 | 0.000e+00 | 0.000e+00 | 0.000e+00 | skipped-zero-angular-coupling |
| 6 | 5.341e-03 | 2.265e+03 | 5.383e-07 | ok |

The multi-channel result is also checked against a higher-order
reference row for each active target channel. The current
convergence scan compares `(N,q)=(224,224),(256,224),(288,224)`.

- Channel-convergence rows: 9
- Largest reflected-amplitude change to reference: `1.140e-04` relative, `4.338e+01` absolute
- Largest horizon-amplitude change to reference: `2.350e+00` relative, `1.017e-01` absolute
The large relative horizon value is caused by the nearly
vanishing off-diagonal `l'=6` horizon amplitude; the reflected
channel amplitudes are the robust multi-channel observables in
the current double-precision implementation.

| l' | N | q | rel A_ref | abs dA_ref | rel A_H | abs dA_H |
|---:|---:|---:|---:|---:|---:|---:|
| 2 | 224 | 224 | 3.814e-05 | 4.338e+01 | 2.407e-08 | 9.158e-05 |
| 2 | 256 | 224 | 2.450e-07 | 2.787e-01 | 1.492e-08 | 5.675e-05 |
| 2 | 288 | 224 | 0.000e+00 | 0.000e+00 | 0.000e+00 | 0.000e+00 |
| 4 | 224 | 224 | 1.140e-04 | 1.552e+00 | 7.706e-02 | 1.017e-01 |
| 4 | 256 | 224 | 6.270e-07 | 8.538e-03 | 7.104e-03 | 9.373e-03 |
| 4 | 288 | 224 | 0.000e+00 | 0.000e+00 | 0.000e+00 | 0.000e+00 |
| 6 | 224 | 224 | 5.811e-07 | 1.316e-03 | 1.168e-01 | 6.289e-08 |
| 6 | 256 | 224 | 2.454e-07 | 5.560e-04 | 2.350e+00 | 1.265e-06 |
| 6 | 288 | 224 | 0.000e+00 | 0.000e+00 | 0.000e+00 | 0.000e+00 |

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

The angular cubic projector, Kerr-covariant cubic radial source, and
oscillatory-tail Green-function integration are now explicit. Wronskians
are stable at machine precision. The target-channel implementation now
has a first active-channel convergence scan. The remaining nonlinear work
is to set broader production acceptance gates across more modes and, if needed,
replace the QUADPACK Fourier tail by a dedicated Levin/Filon integrator
for very high-frequency nonlinear tails.

## Remaining PRD-level work

- Extend the nonlinear table beyond the four representative modes.
- Add an independent oscillatory-tail integrator for high-frequency
  nonlinear source terms.

Generated from `results/kerr_scalar_adaptive_summary.csv`,
`results/kerr_scalar_frequency_sweep.csv`, and
`results/kerr_scalar_cubic_couplings.csv`, plus nonlinear diagnostics
channel scans, channel-convergence scans, and control scans when available.
