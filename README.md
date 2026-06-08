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
