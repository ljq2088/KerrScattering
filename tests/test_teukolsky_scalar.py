"""Smoke tests for scalar Teukolsky building blocks."""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.teukolsky_scalar import (
    kerr_horizons,
    scalar_spheroidal_eigenvalue,
    solve_scalar_in_mode,
    teukolsky_lambda_s0,
)
from src.kerr_scalar_spectral import solve_scalar_in_mode_spectral
from src.teukolsky_lambda import compute_teukolsky_lambda


def test_kerr_horizons_schwarzschild_limit():
    rp, rm = kerr_horizons(M=1.0, a=0.0)
    assert rp == 2.0
    assert rm == 0.0


def test_scalar_spheroidal_zero_c_limit():
    for l, m in [(0, 0), (1, 0), (2, 1), (3, 2)]:
        A = scalar_spheroidal_eigenvalue(l, m, c=0.0)
        assert abs(A - l * (l + 1)) < 1e-12


def test_teukolsky_lambda_schwarzschild_limit():
    lam = teukolsky_lambda_s0(l=2, m=1, a=0.0, omega=0.3)
    assert abs(lam - 6.0) < 1e-12


def test_lambda_provider_local_scalar():
    result = compute_teukolsky_lambda(s=0, l=2, m=1, a=0.0, omega=0.3)
    assert result.provider == "local-scalar-matrix"
    assert abs(result.value - 6.0) < 1e-12


def test_scalar_in_mode_smoke():
    result = solve_scalar_in_mode(l=0, m=0, omega=0.1, M=1.0, a=0.3, r_out=120.0)
    assert result["status"] == "ok"
    assert np.isfinite(result["lambda"])
    assert np.isfinite(result["Z_in"])
    assert np.isfinite(result["Z_out"])


def test_scalar_spectral_in_mode_smoke():
    result = solve_scalar_in_mode_spectral(
        l=0, m=0, omega=0.1, M=1.0, a=0.3, N_outer=64, N_inner=64
    )
    assert result.status == "ok"
    assert np.isfinite(result.radial_lambda)
    assert np.isfinite(result.B_inc)
    assert np.isfinite(result.B_ref)
    assert result.flux_balance_error < 1e-4
