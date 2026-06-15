# KerrScattering

Chebyshev spectral solvers for scalar scattering and weak nonlinear
Green-function amplitudes.  The current active branch focuses on the scalar
Teukolsky equation on Kerr, `s=0`.

## Current Scope

The active physics target is the scalar field on Kerr:

```text
s = 0
Box Phi + epsilon |Phi|^2 Phi = 0
```

Previous non-scalar benchmark utilities are not part of the current scalar
nonlinear scattering conclusion or documentation flow.

## Main Results

- Endpoint-collocation Kerr scalar spectral solver using `z = r_+/r`.
- Direct inclusion of infinity (`z=0`) and the horizon (`z=1`) as collocation
  endpoints.
- Linear amplitude extraction for `B_inc` and `B_ref` by matching in/down/up
  homogeneous solutions.
- GSN benchmark validation on 37 usable scalar cases:
  - worst amplitude-magnitude error: `1.485e-8`;
  - worst flux residual: `3.714e-9`.
- 51-point scalar frequency sweep resolving superradiance only for
  `omega < m Omega_H`.
- Kerr-covariant cubic scalar source

  ```text
  Q = (r^2 C0 + a^2 C2) |R|^2 R
  ```

  for weak nonlinear Green-function amplitudes.
- Exterior nonlinear tail integration by explicit phase-channel Fourier
  quadrature.

## Important Files

- `src/kerr_scalar_spectral.py`
  Two-domain Chebyshev spectral solver for scalar Kerr in modes.

- `src/teukolsky_scalar.py`
  Scalar spheroidal harmonics, angular eigenvalues, Teukolsky lambda, and
  cubic angular projectors.

- `src/kerr_scalar_nonlinear.py`
  Kerr-covariant weak nonlinear source and Green-function amplitudes.

- `scripts/adaptive_kerr_scalar_gsn_validation.py`
  Adaptive validation against GeneralizedSasakiNakamura.jl scalar benchmarks.

- `scripts/run_kerr_scalar_frequency_sweep.py`
  Scalar frequency sweep and superradiance data.

- `scripts/run_kerr_scalar_nonlinear_diagnostics.py`
  Self-channel weak nonlinear amplitude diagnostics.

- `scripts/run_kerr_scalar_nonlinear_channels.py`
  Multi-`l'` weak nonlinear target-channel amplitudes.

- `scripts/run_kerr_scalar_nonlinear_channel_convergence.py`
  Multi-`l'` spectral-order and quadrature convergence checks.

- `scripts/run_kerr_scalar_nonlinear_control_scan.py`
  Spectral-order and matching-radius control scan for nonlinear amplitudes.

- `docs/kerr_scalar_current_work_zh.pdf`
  Current Chinese derivation and status report for the scalar `s=0` project.

- `docs/prd/kerr_scalar_scattering_prd.pdf`
  Current PRD-style English manuscript draft.

## Quick Start

```bash
python scripts/adaptive_kerr_scalar_gsn_validation.py
python scripts/run_kerr_scalar_frequency_sweep.py
python scripts/run_kerr_scalar_cubic_projector.py
python scripts/run_kerr_scalar_nonlinear_diagnostics.py
python scripts/run_kerr_scalar_nonlinear_channels.py
python scripts/run_kerr_scalar_nonlinear_channel_convergence.py
python scripts/run_kerr_scalar_nonlinear_control_scan.py
python scripts/build_kerr_scalar_validation_report.py
```

Plotting:

```bash
python scripts/plot_kerr_scalar_validation.py
python scripts/plot_kerr_scalar_frequency_sweep.py
```

Minimal smoke checks:

```bash
python -m compileall src scripts tests
python -m pytest tests/test_basic_run.py tests/test_teukolsky_scalar.py
```

If `pytest` is not installed in the active Python environment, use direct
script smoke checks or install it into the local environment first.

## Nonlinear Interpretation

The nonlinear amplitudes currently reported are first-order response
coefficients.  The physical correction is

```text
epsilon A^(1)
```

and weak perturbation theory requires

```text
epsilon |A^(1)| << |A^(0)|.
```

Large `A_ref_1` values in near-superradiant or low-frequency Kerr cases arise
from the unit-horizon-transmission normalization and the cubic source
`|R|^2 R`; they should not be interpreted without specifying the physical
incident normalization and coupling strength.

## Next Work

- Add fixed-incident-amplitude normalization.
- Broaden the multi-channel nonlinear scan beyond the current representative
  `kerr_a05_l2m2_super` case.
- Add independent Levin/Filon-style oscillatory-tail integration for
  cross-checks.

## License

MIT
