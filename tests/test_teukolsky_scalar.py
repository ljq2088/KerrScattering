"""Smoke tests for scalar Teukolsky building blocks."""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.teukolsky_scalar import (
    evaluate_scalar_spheroidal,
    kerr_horizons,
    scalar_cubic_coupling,
    scalar_cubic_coupling_cos2,
    scalar_spheroidal_mode,
    scalar_spheroidal_eigenvalue,
    solve_scalar_in_mode,
    teukolsky_lambda_s0,
)
from src.kerr_scalar_spectral import solve_scalar_in_mode_spectral
from src.kerr_scalar_nonlinear import compute_kerr_scalar_green_diagnostics
from src.teukolsky_lambda import compute_teukolsky_lambda


def test_kerr_horizons_schwarzschild_limit():
    rp, rm = kerr_horizons(M=1.0, a=0.0)
    assert rp == 2.0
    assert rm == 0.0


def test_scalar_spheroidal_zero_c_limit():
    for l, m in [(0, 0), (1, 0), (2, 1), (3, 2)]:
        A = scalar_spheroidal_eigenvalue(l, m, c=0.0)
        assert abs(A - l * (l + 1)) < 1e-12


def test_scalar_spheroidal_mode_zero_c_basis_vector():
    mode = scalar_spheroidal_mode(l=2, m=1, c=0.0)
    target = np.where(mode.ells == 2)[0][0]
    assert abs(mode.coefficients[target] - 1.0) < 1e-12
    assert np.linalg.norm(np.delete(mode.coefficients, target)) < 1e-12


def test_scalar_spheroidal_harmonic_normalization():
    mode = scalar_spheroidal_mode(l=2, m=1, c=0.3)
    x, w = np.polynomial.legendre.leggauss(256)
    theta = np.arccos(x)
    vals = evaluate_scalar_spheroidal(mode, theta, 0.0)
    norm = 2.0 * np.pi * np.sum(w * np.abs(vals) ** 2)
    assert abs(norm - 1.0) < 1e-10


def test_scalar_cubic_coupling_spherical_l0():
    coeff = scalar_cubic_coupling(l_source=0, m=0, a=0.0, omega=0.1)
    assert abs(coeff.imag) < 1e-14
    assert abs(coeff.real - 1.0 / (4.0 * np.pi)) < 1e-12


def test_scalar_cubic_coupling_cos2_spherical_l0():
    coeff = scalar_cubic_coupling_cos2(l_source=0, m=0, a=0.0, omega=0.1)
    assert abs(coeff.imag) < 1e-14
    assert abs(coeff.real - 1.0 / (12.0 * np.pi)) < 1e-12


def test_scalar_cubic_coupling_spherical_l1_m0():
    coeff = scalar_cubic_coupling(l_source=1, m=0, a=0.0, omega=0.1)
    assert abs(coeff.imag) < 1e-14
    assert abs(coeff.real - 9.0 / (20.0 * np.pi)) < 1e-12


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


def test_kerr_scalar_green_diagnostics_smoke():
    result = compute_kerr_scalar_green_diagnostics(
        l=2, m=2, omega=0.3, a=0.5, N_outer=64, N_inner=64, quad_order=48
    )
    assert result.status == "ok"
    assert np.isfinite(result.wronskian)
    assert np.isfinite(result.A_ref_1)
    assert np.isfinite(result.A_hor_1)
    assert result.radial_weight_model == "kerr-covariant-sigma-dr"
    assert result.wronskian_relative_error < 1e-10


def test_kerr_scalar_green_diagnostics_zero_coupling():
    result = compute_kerr_scalar_green_diagnostics(
        l=2, m=2, omega=0.3, a=0.5, N_outer=64, N_inner=64,
        quad_order=48, Cl=0.0
    )
    assert result.A_ref_1 == 0.0
    assert result.A_hor_1 == 0.0
