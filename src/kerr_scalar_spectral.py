"""Two-domain Chebyshev spectral solver for scalar Teukolsky in modes.

This module follows the same numerical route as the Schwarzschild
Green-function code in :mod:`src.gf_adaptive_match`: peel off the known
oscillatory factors, keep the degenerate endpoint ODE rows as regularity
conditions, solve smooth amplitudes on Chebyshev subdomains, then match value
and radial derivative at an intermediate radius.
"""

from dataclasses import dataclass

import numpy as np

from .cheb import cheb
from .teukolsky_scalar import (
    KerrParams,
    delta,
    drstar_dr,
    rstar,
    teukolsky_lambda_s0,
)


@dataclass(frozen=True)
class ScalarSpectralResult:
    """Container for scalar Kerr spectral scattering data."""

    M: float
    a: float
    l: int
    m: int
    omega: float
    radial_lambda: float
    r_plus: float
    r_minus: float
    omega_h: float
    p_horizon: float
    r_match: float
    z_match: float
    N_outer: int
    N_inner: int
    mapping: str
    kappa_outer: float
    kappa_inner: float
    B_inc: complex
    B_ref: complex
    reflection_amplitude: complex
    transmission: float
    reflection: float
    flux_balance_error: float
    match_condition: float
    outer_down_condition: float
    outer_up_condition: float
    inner_condition: float
    status: str


def _cheb_interval(N, z_left, z_right, mapping="linear", kappa=0.0):
    """Return Chebyshev nodes and z-derivative matrices on [z_left, z_right]."""
    Dy, y = cheb(N)
    length = z_right - z_left
    if length <= 0:
        raise ValueError("Require z_right > z_left.")

    if mapping == "linear" or kappa <= 0.0:
        z = z_left + 0.5 * length * (1.0 - y)
        dzdy = np.full_like(y, -0.5 * length)
    elif mapping == "sinh-left":
        arg = 0.5 * kappa * (1.0 - y)
        z = z_left + length * np.sinh(arg) / np.sinh(kappa)
        dzdy = -0.5 * length * kappa * np.cosh(arg) / np.sinh(kappa)
    else:
        raise ValueError(f"Unknown Chebyshev mapping: {mapping}")

    Dz = Dy / dzdy[:, None]
    D2z = Dz @ Dz
    return z, Dz, D2z


def _default_r_match(M, omega):
    """Heuristic matching radius following the Schwarzschild spectral scale."""
    wM = abs(omega) * M
    if wM <= 0.0:
        raise ValueError("omega must be nonzero.")
    if wM >= 0.5:
        return 12.0 * M
    if wM >= 0.05:
        return 30.0 * M
    return max(30.0 * M, M * (3.0 + 1.0 / np.sqrt(wM)))


def _d2rstar_dr2(r, M, a):
    d = delta(r, M=M, a=a)
    dp = 2.0 * r - 2.0 * M
    num = 2.0 * r * d - (r**2 + a**2) * dp
    return num / d**2


def _phase_log_derivatives(r, branch, params, omega, m):
    """Return q=F'/F and q'=dq/dr for the peeled radial factor F."""
    fp = drstar_dr(r, M=params.M, a=params.a)
    fpp = _d2rstar_dr2(r, params.M, params.a)
    p_h = omega - m * params.omega_h

    if branch == "in":
        q = -1j * p_h * fp
        qp = -1j * p_h * fpp
    elif branch == "down":
        q = -1.0 / r - 1j * omega * fp
        qp = 1.0 / r**2 - 1j * omega * fpp
    elif branch == "up":
        q = -1.0 / r + 1j * omega * fp
        qp = 1.0 / r**2 + 1j * omega * fpp
    else:
        raise ValueError(f"Unknown branch: {branch}")
    return q, qp


def _basis_factor(r, branch, params, omega, m):
    x = rstar(r, M=params.M, a=params.a)
    p_h = omega - m * params.omega_h
    if branch == "in":
        return np.exp(-1j * p_h * x)
    if branch == "down":
        return np.exp(-1j * omega * x) / r
    if branch == "up":
        return np.exp(1j * omega * x) / r
    raise ValueError(f"Unknown branch: {branch}")


def _transformed_coefficients(z, branch, params, l, m, omega, radial_lambda):
    """Coefficients of the amplitude equation in z = r_+ / r."""
    rp = params.rp
    z = np.asarray(z, dtype=float)
    scalar = z.ndim == 0
    z = np.atleast_1d(z)
    B2 = np.zeros_like(z, dtype=complex)
    B1 = np.zeros_like(z, dtype=complex)
    B0 = np.zeros_like(z, dtype=complex)

    regular = (z > 0.0) & (z < 1.0)
    if np.any(regular):
        zr = z[regular]
        r = rp / zr
        d = delta(r, M=params.M, a=params.a)
        dp = 2.0 * r - 2.0 * params.M
        K = (r**2 + params.a**2) * omega - params.a * m
        a0 = K**2 / d - radial_lambda

        q, qp = _phase_log_derivatives(r, branch, params, omega, m)
        z_r = -zr**2 / rp
        z_rr = 2.0 * zr**3 / rp**2

        B2[regular] = d * z_r**2
        B1[regular] = d * (z_rr + 2.0 * q * z_r) + dp * z_r
        B0[regular] = d * (qp + q**2) + dp * q + a0

    at_infinity = z == 0.0
    if np.any(at_infinity):
        if branch not in {"down", "up"}:
            raise ValueError("Only down/up branches are regular at z=0.")
        sigma = -1.0 if branch == "down" else 1.0
        B2[at_infinity] = 0.0
        B1[at_infinity] = -2j * sigma * rp * omega
        B0[at_infinity] = -radial_lambda

    at_horizon = z == 1.0
    if np.any(at_horizon):
        if branch != "in":
            raise ValueError("Only the in branch is regular at z=1.")
        rm = params.rm
        p_h = omega - m * params.omega_h
        B2[at_horizon] = 0.0
        B1[at_horizon] = (rm / rp - 1.0) + 2j * p_h * (rp + rm)
        B0[at_horizon] = (
            4.0 * rp**2 * (rp + rm) * p_h * (omega - p_h) / (rp - rm)
            - 2j * rp * p_h
            - radial_lambda
        )

    if scalar:
        return B2[0], B1[0], B0[0]
    return B2, B1, B0


def _solve_branch(N, z_left, z_right, branch, boundary_side, params,
                  mapping, kappa,
                  l, m, omega, radial_lambda):
    z, Dz, D2z = _cheb_interval(N, z_left, z_right, mapping=mapping, kappa=kappa)
    B2, B1, B0 = _transformed_coefficients(
        z, branch, params, l, m, omega, radial_lambda
    )
    mat = B2[:, None] * D2z + B1[:, None] * Dz + np.diag(B0)
    rhs = np.zeros(N + 1, dtype=complex)

    if boundary_side == "left":
        mat[1, :] = 0.0
        mat[1, 0] = 1.0
        rhs[1] = 1.0
    elif boundary_side == "right":
        mat[-2, :] = 0.0
        mat[-2, -1] = 1.0
        rhs[-2] = 1.0
    else:
        raise ValueError("boundary_side must be 'left' or 'right'.")

    values = np.linalg.solve(mat, rhs)
    derivs = Dz @ values
    condition = float(np.linalg.cond(mat))
    return {
        "z": z,
        "u": values,
        "uz": derivs,
        "condition": condition,
    }


def _field_and_radial_derivative(z, u, uz, branch, params, omega, m):
    rp = params.rp
    r = rp / z
    F = _basis_factor(r, branch, params, omega, m)
    q, _ = _phase_log_derivatives(r, branch, params, omega, m)
    dz_dr = -z**2 / rp
    R = F * u
    Rr = F * (q * u + uz * dz_dr)
    return R, Rr


def solve_scalar_in_mode_spectral(
    l,
    m,
    omega,
    M=1.0,
    a=0.0,
    N_outer=96,
    N_inner=96,
    r_match=None,
    z_infinity=0.0,
    z_horizon=1.0,
    mapping="auto",
    lmax_extra=16,
    radial_lambda=None,
):
    """Compute scalar Kerr in-mode amplitudes by two-domain spectral matching.

    The solution is normalized so that the horizon ``in`` factor has unit
    amplitude. At infinity

        R_in = B_inc exp(-i omega r*)/r + B_ref exp(+i omega r*)/r.
    """
    if abs(omega) <= 0:
        raise ValueError("omega must be nonzero.")
    if abs(a) >= M:
        raise ValueError("Require subextremal Kerr, |a| < M.")

    params = KerrParams(M=M, a=a)
    rp = params.rp
    if r_match is None:
        r_match = _default_r_match(M, omega)
    z_match = rp / r_match

    if z_infinity != 0.0 or z_horizon != 1.0:
        raise NotImplementedError("The endpoint formulation currently uses z=0 and z=1.")
    if not (z_infinity < z_match < z_horizon):
        raise ValueError("Invalid z-domain endpoints.")

    if mapping == "auto":
        use_sinh = abs(omega) * M < 0.1
    elif mapping == "linear":
        use_sinh = False
    elif mapping == "sinh":
        use_sinh = True
    else:
        raise ValueError("mapping must be 'auto', 'linear', or 'sinh'.")

    if use_sinh:
        active_mapping = "sinh-left"
        kappa_outer = abs(np.log(max(abs(omega) * 2.0 * M, 1e-300)))
        kappa_inner = 0.5 * kappa_outer
    else:
        active_mapping = "linear"
        kappa_outer = 0.0
        kappa_inner = 0.0

    lam = radial_lambda
    if lam is None:
        lam = teukolsky_lambda_s0(l, m, a, omega, lmax_extra=lmax_extra)

    down = _solve_branch(
        N_outer, z_infinity, z_match, "down", "left",
        params, active_mapping, kappa_outer,
        l, m, omega, lam
    )
    up = _solve_branch(
        N_outer, z_infinity, z_match, "up", "left",
        params, active_mapping, kappa_outer,
        l, m, omega, lam
    )
    inner = _solve_branch(
        N_inner, z_match, z_horizon, "in", "right",
        params, active_mapping, kappa_inner,
        l, m, omega, lam
    )

    R_down, Rr_down = _field_and_radial_derivative(
        z_match, down["u"][-1], down["uz"][-1], "down", params, omega, m
    )
    R_up, Rr_up = _field_and_radial_derivative(
        z_match, up["u"][-1], up["uz"][-1], "up", params, omega, m
    )
    R_in, Rr_in = _field_and_radial_derivative(
        z_match, inner["u"][0], inner["uz"][0], "in", params, omega, m
    )

    match_matrix = np.array([[R_down, R_up], [Rr_down, Rr_up]], dtype=complex)
    rhs = np.array([R_in, Rr_in], dtype=complex)
    B_inc, B_ref = np.linalg.solve(match_matrix, rhs)

    p_h = omega - m * params.omega_h
    reflection_amp = B_ref / B_inc
    horizon_area_factor = params.rp**2 + params.a**2
    transmission = float((p_h * horizon_area_factor / omega) / abs(B_inc) ** 2)
    reflection = float(abs(reflection_amp) ** 2)
    flux_balance_error = float(abs(transmission + reflection - 1.0))

    return ScalarSpectralResult(
        M=M,
        a=a,
        l=l,
        m=m,
        omega=omega,
        radial_lambda=float(lam),
        r_plus=float(params.rp),
        r_minus=float(params.rm),
        omega_h=float(params.omega_h),
        p_horizon=float(p_h),
        r_match=float(r_match),
        z_match=float(z_match),
        N_outer=int(N_outer),
        N_inner=int(N_inner),
        mapping="sinh" if use_sinh else "linear",
        kappa_outer=float(kappa_outer),
        kappa_inner=float(kappa_inner),
        B_inc=B_inc,
        B_ref=B_ref,
        reflection_amplitude=reflection_amp,
        transmission=transmission,
        reflection=reflection,
        flux_balance_error=flux_balance_error,
        match_condition=float(np.linalg.cond(match_matrix)),
        outer_down_condition=down["condition"],
        outer_up_condition=up["condition"],
        inner_condition=inner["condition"],
        status="ok",
    )
