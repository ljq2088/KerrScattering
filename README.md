# Schwarzschild Green-function Spectral Method

Multi-domain Chebyshev spectral method for Schwarzschild frequency-domain radial scattering and Green-function nonlinear amplitude correction.

## Method Overview

This project solves the radial scattering problem for a scalar field on a Schwarzschild background using a multi-domain Chebyshev spectral method. The computation produces:

1. **Linear scattering coefficients**: transmission probability T and reflection probability R
2. **Nonlinear amplitude corrections**: first-order corrections T1, R1 from a cubic (|φ|²φ) self-interaction

### Key Features
- Compactified Bondi coordinate z = 2M/r
- Multi-domain approach with matching at zp
- Adaptive mesh refinement (AnMR) for low frequencies (ω < 0.1)
- Green function matching for connection coefficients
- Quadrature-based nonlinear correction integrals

## Quick Start

```bash
cd KerrScatteringProb
python scripts/run_reproduction.py       # Single frequency reproduction
python scripts/run_parameter_sweep.py     # Multi-frequency sweep
python scripts/run_convergence.py         # N-convergence test
python scripts/run_teukolsky_scalar_demo.py  # Scalar s=0 Kerr/Teukolsky demo
python scripts/run_kerr_scalar_spectral_demo.py  # Kerr s=0 spectral/IVP comparison
python scripts/run_kerr_scalar_spectral_convergence.py  # Kerr s=0 spectral convergence
julia --project=/home/ljq/code/GSN/GeneralizedSasakiNakamura.jl scripts/run_kerr_scalar_gsn_benchmark.jl
python scripts/compare_kerr_scalar_gsn.py  # Kerr s=0 spectral/GSN benchmark comparison
python scripts/adaptive_kerr_scalar_gsn_validation.py  # Scan N/r_match against GSN
python scripts/run_kerr_scalar_frequency_sweep.py  # Kerr s=0 frequency sweep
python scripts/run_kerr_scalar_cubic_projector.py  # Kerr s=0 cubic angular source projection
python scripts/run_kerr_scalar_nonlinear_diagnostics.py  # Prototype nonlinear radial GF diagnostics
python scripts/build_kerr_scalar_validation_report.py
python scripts/plot_kerr_scalar_validation.py
python scripts/plot_kerr_scalar_frequency_sweep.py
python scripts/compute_teukolsky_lambda.py --s 0 --l 2 --m 1 --a 0.5 --omega 0.1
python scripts/run_spin_minus2_rin_comparison.py  # s=-2 R_in Binc/Bref comparison
python -m pytest tests/test_basic_run.py  # Smoke test
```

## Requirements

- Python 3.8+
- numpy, scipy, matplotlib

## Project Structure

```
├── src/                          # Core computation
│   ├── cheb.py                   # Chebyshev spectral tools
│   ├── bondi.py                  # ODE operator construction
│   └── gf_adaptive_match.py     # Main computation function
├── scripts/                      # Runnable scripts
│   ├── run_reproduction.py
│   ├── run_parameter_sweep.py
│   └── run_convergence.py
├── tests/                        # Tests
│   └── test_basic_run.py
├── results/                      # Output data
├── figures/                      # Output plots
└── docs/                         # Documentation
    ├── reproduction_log.md
    └── method_summary.md
```

## Reference

Based on MATLAB code: `GF_adaptive_match.m` and `MatlCheb-main`.

## Kerr / Teukolsky Branch

This branch adds first building blocks for extending the Schwarzschild scalar
Green-function method to scalar (`s=0`) Teukolsky modes on Kerr:

- `src/teukolsky_scalar.py`: scalar spheroidal eigenvalue, Kerr tortoise
  coordinate, scalar radial Teukolsky ODE, and unit-horizon-amplitude in-mode
  integration.
- `src/kerr_scalar_spectral.py`: two-domain Chebyshev spectral matching for
  scalar Kerr in modes. This follows the Schwarzschild spectral route with
  Kerr `s=0` radial coefficients, direct `z=0,1` endpoint regularity rows,
  phase peeling, and value/derivative matching for `B_inc` and `B_ref`.
- `scripts/run_kerr_scalar_spectral_demo.py`: compares the Kerr `s=0` spectral
  amplitudes against the direct radial IVP leading-asymptotic output.
- `scripts/run_kerr_scalar_spectral_convergence.py`: scans spectral order and
  records convergence diagnostics in `results/kerr_scalar_spectral_convergence.csv`.
- `scripts/run_kerr_scalar_gsn_benchmark.jl`: runs external GSN scalar
  Teukolsky benchmarks for selected Kerr modes.
- `scripts/compare_kerr_scalar_gsn.py`: compares spectral amplitudes with GSN.
  Magnitude errors are the convention-invariant benchmark; complex phase
  factors are reported separately because tortoise-coordinate constants differ
  across packages.
- `scripts/adaptive_kerr_scalar_gsn_validation.py`: scans Chebyshev order and
  matching radius for each usable GSN case; the summary table currently
  verifies 37 cases with all amplitude-magnitude errors below `1e-7`.
- `scripts/run_kerr_scalar_frequency_sweep.py`: computes self-converged
  Schwarzschild and Kerr frequency sweeps for `R`, `T`, and superradiant
  amplification using the same endpoint-collocation spectral route.
- `scripts/run_kerr_scalar_cubic_projector.py`: computes scalar spheroidal
  cubic source projection coefficients `C_{l'lm}` for the validated Kerr
  modes; this is the angular input for the nonlinear Green-function extension.
- `scripts/run_kerr_scalar_nonlinear_diagnostics.py`: evaluates prototype
  nonlinear radial Green-function source integrals and quadrature convergence
  diagnostics. These are explicitly marked as diagnostics until the final Kerr
  cubic radial source weight is fixed.
- `scripts/plot_kerr_scalar_frequency_sweep.py`: produces publication-style
  frequency-sweep plots in `figures/kerr_scalar_frequency_rt.png` and
  `figures/kerr_scalar_superradiance_amplification.png`.
- `docs/kerr_scalar_validation_report.md` and `figures/kerr_scalar_*.png`:
  current validation report and plots.
- `docs/teukolsky_scalar_kerr.md` and `docs/teukolsky_scalar_kerr.pdf`:
  derivation notes.
- `scripts/probe_spin_minus2_benchmark.py`: environment probe for the requested
  `s=-2`, `a=0.5`, `l=m=2` benchmark stack.
- `scripts/run_spin_minus2_benchmark_suite.py`: split benchmark runner using
  GSN for high frequency and Windows Mathematica/MST from `F:\mma` for low
  frequency.
- `scripts/run_spin_minus2_rin_comparison.py`: computes the requested
  `s=-2, a=0.5, l=m=2` `R_in` incidence/reflection amplitudes at
  `omega = 10, 0.1, 1e-4` and compares them against the GSN/MST benchmarks.

## Future Work

- Extension to Kerr (Teukolsky equation) with non-zero spin parameter
- Higher angular modes (l > 0)
- Convergence acceleration for the quadrature integrals
- Physical calibration of the nonlinear coupling constant Cl

## License

MIT
