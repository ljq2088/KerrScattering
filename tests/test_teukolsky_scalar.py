"""Smoke tests for scalar Teukolsky building blocks."""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.teukolsky_scalar import (
    KerrParams,
    evaluate_scalar_spheroidal,
    kerr_horizons,
    scalar_cubic_coupling,
    scalar_cubic_coupling_cos2,
    scalar_power_coupling,
    scalar_spheroidal_mode,
    scalar_spheroidal_eigenvalue,
    solve_scalar_in_mode,
    teukolsky_lambda_s0,
)
from src.kerr_scalar_spectral import (
    _cheb_interval,
    _phase_log_derivatives,
    _solve_branch,
    _transformed_coefficients,
    solve_scalar_in_mode_spectral,
)
from src.kerr_scalar_nonlinear import (
    compute_kerr_scalar_green_diagnostics,
    fixed_incident_flux_coefficients,
    scalar_axisymmetric_cubic_low_frequency_coupling,
    scalar_axisymmetric_cubic_low_frequency_horizon_coefficient,
    scalar_axisymmetric_cubic_low_frequency_integral,
    scalar_axisymmetric_cubic_low_frequency_phase_integral,
    scalar_axisymmetric_cubic_low_frequency_relative_horizon_amplitude,
    scalar_axisymmetric_cubic_low_frequency_response,
    scalar_axisymmetric_linear_low_frequency_coefficient,
    scalar_monopole_low_frequency_coefficient,
    scalar_monopole_low_frequency_integral,
)
from src.teukolsky_lambda import compute_teukolsky_lambda
from scripts.run_kerr_scalar_near_extremal_scaling import comma_scalar_modes


def test_kerr_horizons_schwarzschild_limit():
    rp, rm = kerr_horizons(M=1.0, a=0.0)
    assert rp == 2.0
    assert rm == 0.0


def test_infinity_rows_include_rotational_cross_term():
    for a, m in [(0.5, 2), (0.5, -2), (0.5, 0), (0.0, 2)]:
        params = KerrParams(M=1.0, a=a)
        omega = 0.3
        radial_lambda = teukolsky_lambda_s0(2, m, a, omega)
        angular_eigenvalue = scalar_spheroidal_eigenvalue(2, m, a * omega)
        for branch, sigma in [("down", -1.0), ("up", 1.0)]:
            B2, B1, B0 = _transformed_coefficients(
                0.0, branch, params, 2, m, omega, radial_lambda
            )
            assert B2 == 0.0
            np.testing.assert_allclose(B1, -2j * sigma * params.rp * omega)
            np.testing.assert_allclose(B0, -angular_eigenvalue - a**2 * omega**2)


def test_factored_coefficients_agree_with_unfactored_radial_operator():
    params = KerrParams(M=1.0, a=0.99)
    omega, m = 0.7, 2
    lam = teukolsky_lambda_s0(2, m, params.a, omega)
    z = np.asarray([0.02, 0.1, 0.4, 0.8])
    r = params.rp / z
    d = r*r - 2*r + params.a**2
    dp = 2*r - 2
    K = (r*r + params.a**2)*omega - params.a*m
    zr, zrr = -z*z/params.rp, 2*z**3/params.rp**2
    for branch in ("in", "down", "up"):
        q, qp = _phase_log_derivatives(r, branch, params, omega, m)
        got = _transformed_coefficients(z, branch, params, 2, m, omega, lam)
        expected = (d*zr*zr, d*(zrr+2*q*zr)+dp*zr,
                    d*(qp+q*q)+dp*q+K*K/d-lam)
        for actual, reference in zip(got, expected):
            np.testing.assert_allclose(actual, reference, rtol=2e-11, atol=2e-11)


def test_factored_coefficients_approach_both_endpoint_rows():
    params = KerrParams(M=1.0, a=0.99)
    omega, m = 0.7, 2
    lam = teukolsky_lambda_s0(2, m, params.a, omega)
    for branch, end, nearby in [("up", 0.0, 1e-10), ("down", 0.0, 1e-10),
                                ("in", 1.0, 1.0-1e-10)]:
        endpoint = _transformed_coefficients(end, branch, params, 2, m, omega, lam)
        interior = _transformed_coefficients(nearby, branch, params, 2, m, omega, lam)
        for actual, reference in zip(interior, endpoint):
            np.testing.assert_allclose(actual, reference, rtol=1e-7, atol=1e-7)


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


def test_scalar_power_coupling_spherical_l0():
    for n in (1, 2, 3):
        coefficient = scalar_power_coupling(
            l_source=0,
            m=0,
            a=0.0,
            omega=0.1,
            nonlinearity_order=n,
        )
        coefficient_cos2 = scalar_power_coupling(
            l_source=0,
            m=0,
            a=0.0,
            omega=0.1,
            nonlinearity_order=n,
            cos_power=2,
        )
        expected = (4.0 * np.pi) ** (-n)
        assert abs(coefficient.imag) < 1e-14
        assert abs(coefficient.real - expected) < 1e-12
        assert abs(coefficient_cos2.real - expected / 3.0) < 1e-12


def test_scalar_monopole_power_nonlinearity_coefficients():
    assert np.allclose(
        scalar_monopole_low_frequency_integral(1),
        0.5 * np.log(2.0),
        rtol=1e-14,
        atol=0.0,
    )
    expected_n2 = (81.0 * np.log(3.0) - 96.0 * np.log(2.0)) / (
        36.0 * np.pi**2
    )
    expected_n3 = (416.0 * np.log(2.0) - 243.0 * np.log(3.0)) / (
        40.0 * np.pi**3
    )
    assert np.allclose(
        scalar_monopole_low_frequency_coefficient(1),
        np.log(2.0) / np.pi,
        rtol=1e-14,
        atol=0.0,
    )
    assert np.allclose(
        scalar_monopole_low_frequency_coefficient(2),
        expected_n2,
        rtol=1e-14,
        atol=0.0,
    )
    assert np.allclose(
        scalar_monopole_low_frequency_coefficient(3),
        expected_n3,
        rtol=1e-14,
        atol=0.0,
    )


def test_axisymmetric_cubic_low_frequency_coefficients():
    assert np.allclose(
        scalar_axisymmetric_cubic_low_frequency_integral(0),
        0.5 * np.log(2.0),
        rtol=2e-13,
        atol=0.0,
    )
    assert np.allclose(
        scalar_axisymmetric_cubic_low_frequency_phase_integral(0),
        0.25 * np.pi,
        rtol=2e-11,
        atol=0.0,
    )
    assert np.allclose(
        scalar_axisymmetric_cubic_low_frequency_horizon_coefficient(0, 0.5),
        np.log(2.0) / (8.0 * np.pi) + 0.0625j,
        rtol=2e-11,
        atol=0.0,
    )
    assert np.allclose(
        scalar_axisymmetric_cubic_low_frequency_relative_horizon_amplitude(0),
        np.log(2.0) / (2.0 * np.pi) + 0.25j,
        rtol=2e-11,
        atol=0.0,
    )
    assert np.allclose(
        scalar_axisymmetric_cubic_low_frequency_coupling(1),
        9.0 / (20.0 * np.pi),
        rtol=2e-13,
        atol=0.0,
    )
    assert np.allclose(
        scalar_axisymmetric_cubic_low_frequency_response(0),
        np.log(2.0) / np.pi,
        rtol=2e-13,
        atol=0.0,
    )
    assert np.allclose(
        scalar_axisymmetric_cubic_low_frequency_response(1),
        0.14713671778617247,
        rtol=2e-13,
        atol=0.0,
    )
    assert np.allclose(
        scalar_axisymmetric_linear_low_frequency_coefficient(0, a=0.5),
        4.0 * (2.0 + np.sqrt(3.0)),
        rtol=2e-14,
        atol=0.0,
    )


def test_near_extremal_mode_parser_accepts_scalar_monopole():
    assert comma_scalar_modes("0:0,2:2") == [(0, 0), (2, 2)]


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


def test_endpoint_inclusive_sinh_mapping_and_regular_rows():
    params = KerrParams(M=1.0, a=0.5)
    omega = 0.02
    radial_lambda = teukolsky_lambda_s0(l=0, m=0, a=params.a, omega=omega)
    z_match = params.rp / 40.0
    kappa = abs(np.log(2.0 * params.M * omega))

    z_outer, _, _ = _cheb_interval(
        48, 0.0, z_match, mapping="sinh-left", kappa=kappa
    )
    z_inner, _, _ = _cheb_interval(
        48, z_match, 1.0, mapping="sinh-left", kappa=0.5 * kappa
    )
    assert z_outer[0] == 0.0
    assert z_outer[-1] == z_match
    assert z_inner[0] == z_match
    assert z_inner[-1] == 1.0

    for z, branch in ((0.0, "down"), (1.0, "in")):
        B2, B1, B0 = _transformed_coefficients(
            z, branch, params, 0, 0, omega, radial_lambda
        )
        assert B2 == 0.0
        assert np.isfinite(B1)
        assert np.isfinite(B0)
        assert abs(B1) > 0.0


def test_equilibrated_branch_solve_reduces_conditioning_without_changing_solution():
    params = KerrParams(M=1.0, a=0.5)
    omega = 0.3
    radial_lambda = teukolsky_lambda_s0(
        l=2, m=2, a=params.a, omega=omega
    )
    z_match = params.rp / 30.0
    args = (
        64, 0.0, z_match, "down", "left", params,
        "linear", 0.0, 2, 2, omega, radial_lambda,
    )

    direct = _solve_branch(*args, linear_solver="direct")
    equilibrated = _solve_branch(*args, linear_solver="equilibrated")

    assert equilibrated["scaled_condition"] < direct["condition"] / 1.0e3
    assert np.allclose(equilibrated["u"], direct["u"], rtol=1e-10, atol=1e-11)


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


def test_fixed_incident_flux_normalization_and_balance():
    result = compute_kerr_scalar_green_diagnostics(
        l=2, m=0, omega=0.52, a=0.5,
        N_outer=96, N_inner=96, quad_order=96, tail_epsrel=1e-10,
    )
    flux = fixed_incident_flux_coefficients(result)
    expected_scale = abs(result.B_inc) ** 2 * result.B_inc

    assert np.allclose(
        flux.A_ref_fixed_incident, result.A_ref_1 / expected_scale,
        rtol=1e-14, atol=0.0,
    )
    assert np.allclose(
        flux.A_hor_fixed_incident, result.A_hor_1 / expected_scale,
        rtol=1e-14, atol=0.0,
    )
    assert abs(flux.linear_balance) < 1e-8
    assert abs(flux.nonlinear_balance) < 1e-8
    assert flux.T1 > 0.0
    assert flux.R1 < 0.0
    assert np.allclose(
        flux.horizon_response,
        2.0 * result.A_hor_1.real / abs(result.B_inc) ** 2,
        rtol=1e-14,
        atol=0.0,
    )
    assert np.allclose(
        flux.horizon_response,
        flux.T1 / flux.T0,
        rtol=1e-14,
        atol=0.0,
    )


def test_power_nonlinearity_fixed_incident_normalization_and_balance():
    result = compute_kerr_scalar_green_diagnostics(
        l=0,
        m=0,
        omega=0.08,
        a=0.3,
        N_outer=72,
        N_inner=72,
        quad_order=72,
        tail_epsrel=1e-10,
        nonlinearity_order=2,
        linear_solver="equilibrated",
    )
    flux = fixed_incident_flux_coefficients(result)
    expected_scale = abs(result.B_inc) ** 4 * result.B_inc

    assert result.nonlinearity_order == 2
    assert np.allclose(
        flux.A_hor_fixed_incident,
        result.A_hor_1 / expected_scale,
        rtol=1e-14,
        atol=0.0,
    )
    assert abs(flux.linear_balance) < 1e-8
    assert abs(flux.nonlinear_balance) < 1e-8
    assert flux.horizon_response > 0.0
    assert np.allclose(
        flux.horizon_response,
        2.0 * result.A_hor_1.real / abs(result.B_inc) ** 4,
        rtol=1e-14,
        atol=0.0,
    )


def test_kerr_scalar_green_diagnostics_target_channel_smoke():
    result = compute_kerr_scalar_green_diagnostics(
        l=2, m=2, omega=0.3, a=0.5, l_target=4,
        N_outer=64, N_inner=64, quad_order=48
    )
    assert result.status == "ok"
    assert result.l == 2
    assert result.l_target == 4
    assert np.isfinite(result.A_ref_1)
    assert np.isfinite(result.A_hor_1)
    assert result.wronskian_relative_error < 1e-10


def test_kerr_scalar_green_diagnostics_zero_coupling():
    result = compute_kerr_scalar_green_diagnostics(
        l=2, m=2, omega=0.3, a=0.5, N_outer=64, N_inner=64,
        quad_order=48, Cl=0.0
    )
    assert result.A_ref_1 == 0.0
    assert result.A_hor_1 == 0.0
