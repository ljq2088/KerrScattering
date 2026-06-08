"""Numerical amplitudes for the spin -2 Teukolsky R_in solution.

The conventions here are matched to the GSN/BHPT benchmark used in this
project: M=1, unit Teukolsky transmission at the future horizon, and the
dimensionless Kerr tortoise coordinate used by GeneralizedSasakiNakamura.jl.
"""

from dataclasses import dataclass
from functools import lru_cache

import numpy as np
from scipy.integrate import solve_ivp

from .cheb import cheb
from .teukolsky_scalar import delta, kerr_horizons


S = -2
L = 2
M_AZ = 2
A_KERR = 0.5


@dataclass(frozen=True)
class RInAmplitudeResult:
    omega: float
    radial_lambda: float
    incidence_amplitude: complex
    reflection_amplitude: complex
    method: str
    r_match: float
    status: str = "ok"


def kerr_rstar_gsn(r, a=A_KERR):
    """Kerr tortoise coordinate with the GSN/BHPT logarithm constants."""
    rp, rm = kerr_horizons(1.0, a)
    h = np.asarray(r) - rp
    return (
        rp
        + h
        + (2.0 * rp / (rp - rm)) * np.log(h / 2.0)
        - (2.0 * rm / (rp - rm)) * np.log((h + rp - rm) / 2.0)
    )


def _drstar_dr(r, a=A_KERR):
    return (r * r + a * a) / delta(r, 1.0, a)


def _d2rstar_dr2(r, a=A_KERR):
    d = delta(r, 1.0, a)
    dp = 2.0 * r - 2.0
    q = r * r + a * a
    qp = 2.0 * r
    return (qp * d - q * dp) / (d * d)


def _radial_coefficients(r, omega, radial_lambda, s=S, m=M_AZ, a=A_KERR):
    d = delta(r, 1.0, a)
    dp = 2.0 * r - 2.0
    k = (r * r + a * a) * omega - a * m
    v = (k * k - 2j * s * (r - 1.0) * k) / d + 4j * s * omega * r - radial_lambda
    return d, (s + 1) * dp, v


def _factor_log_derivative(r, kind, omega, s=S, m=M_AZ, a=A_KERR):
    d = delta(r, 1.0, a)
    dp = 2.0 * r - 2.0
    rs1 = _drstar_dr(r, a)
    rs2 = _d2rstar_dr2(r, a)
    rp, _ = kerr_horizons(1.0, a)
    omega_h = a / (rp * rp + a * a)
    p = omega - m * omega_h

    if kind == "horizon":
        logp = -s * dp / d - 1j * p * rs1
        logpp = -s * (2.0 / d - (dp / d) ** 2) - 1j * p * rs2
        return logp, logpp
    if kind == "inc":
        logp = -1.0 / r - 1j * omega * rs1
        logpp = 1.0 / (r * r) - 1j * omega * rs2
        return logp, logpp
    if kind == "ref":
        n = -2 * s - 1
        logp = n / r + 1j * omega * rs1
        logpp = -n / (r * r) + 1j * omega * rs2
        return logp, logpp
    raise ValueError(f"unknown factor kind {kind!r}")


def _factor_value(r, kind, omega, s=S, m=M_AZ, a=A_KERR):
    rp, _ = kerr_horizons(1.0, a)
    omega_h = a / (rp * rp + a * a)
    p = omega - m * omega_h
    x = kerr_rstar_gsn(r, a)
    if kind == "horizon":
        return delta(r, 1.0, a) ** (-s) * np.exp(-1j * p * x)
    if kind == "inc":
        return r ** (-1) * np.exp(-1j * omega * x)
    if kind == "ref":
        return r ** (-2 * s - 1) * np.exp(1j * omega * x)
    raise ValueError(f"unknown factor kind {kind!r}")


def _radial_rhs(r, y, omega, radial_lambda):
    r_val, rp_val = y
    a2, a1, a0 = _radial_coefficients(r, omega, radial_lambda)
    rpp = -(a1 * rp_val + a0 * r_val) / a2
    return np.array([rp_val, rpp], dtype=complex)


def _sympy_module():
    try:
        import sympy as sp
    except ImportError as exc:
        raise RuntimeError("sympy is required for high-order asymptotic coefficients") from exc
    return sp


@lru_cache(maxsize=64)
def _horizon_series_coefficients(omega, radial_lambda, order):
    sp = _sympy_module()
    x = sp.symbols("x")
    coeff_symbols = sp.symbols(f"h0:{order + 1}")
    a = sp.Float(A_KERR, 50)
    s = S
    m = M_AZ
    om = sp.Float(omega, 50)
    lam = sp.Float(radial_lambda, 50)
    rp = 1 + sp.sqrt(1 - a * a)
    r = rp + x
    d = r**2 - 2 * r + a * a
    dp = 2 * r - 2
    k = (r**2 + a * a) * om - a * m
    a2 = d
    a1 = (s + 1) * dp
    a0 = (k**2 - 2 * sp.I * s * (r - 1) * k) / d + 4 * sp.I * s * om * r - lam
    rs1 = (r**2 + a * a) / d
    rs2 = (2 * r * d - (r**2 + a * a) * dp) / d**2
    omega_h = a / (rp**2 + a * a)
    p = om - m * omega_h
    logp = -s * dp / d - sp.I * p * rs1
    logpp = -s * (2 / d - (dp / d) ** 2) - sp.I * p * rs2
    b1 = sp.simplify(a2 * 2 * logp + a1)
    b0 = sp.simplify(a2 * (logpp + logp**2) + a1 * logp + a0)

    coeff = [1.0 + 0j]
    for n in range(1, order + 1):
        y = sum((coeff[k] if k < n else coeff_symbols[k]) * x**k for k in range(n + 1))
        expr = sp.series(a2 * sp.diff(y, x, 2) + b1 * sp.diff(y, x) + b0 * y, x, 0, n).removeO()
        eq = sp.N(sp.expand(expr).coeff(x, n - 1), 60)
        sol = sp.solve(sp.Eq(eq, 0), coeff_symbols[n])
        if not sol:
            raise RuntimeError(f"could not solve horizon coefficient h_{n}")
        coeff.append(complex(sp.N(sol[0], 60)))
    return tuple(coeff)


@lru_cache(maxsize=64)
def _infinity_series_coefficients(kind, omega, radial_lambda, order):
    sp = _sympy_module()
    z = sp.symbols("z")
    coeff_symbols = sp.symbols(f"c0:{order + 1}")
    a = sp.Float(A_KERR, 50)
    s = S
    m = M_AZ
    om = sp.Float(omega, 50)
    lam = sp.Float(radial_lambda, 50)
    r = 1 / z
    d = r**2 - 2 * r + a * a
    dp = 2 * r - 2
    k = (r**2 + a * a) * om - a * m
    a2 = d
    a1 = (s + 1) * dp
    a0 = (k**2 - 2 * sp.I * s * (r - 1) * k) / d + 4 * sp.I * s * om * r - lam
    rs1 = (r**2 + a * a) / d
    rs2 = (2 * r * d - (r**2 + a * a) * dp) / d**2
    z_r = -z**2
    z_rr = 2 * z**3
    if kind == "inc":
        n_power = -1
        sign = -1
    elif kind == "ref":
        n_power = -2 * s - 1
        sign = 1
    else:
        raise ValueError(kind)
    logp = n_power / r + sign * sp.I * om * rs1
    logpp = -n_power / r**2 + sign * sp.I * om * rs2
    b2 = sp.simplify(a2 * z_r**2)
    b1 = sp.simplify(a2 * (2 * logp * z_r + z_rr) + a1 * z_r)
    b0 = sp.simplify(a2 * (logpp + logp**2) + a1 * logp + a0)

    coeff = [1.0 + 0j]
    for n in range(1, order + 1):
        y = sum((coeff[k] if k < n else coeff_symbols[k]) * z**k for k in range(n + 1))
        expr = sp.series(b2 * sp.diff(y, z, 2) + b1 * sp.diff(y, z) + b0 * y, z, 0, n + 1).removeO()
        eq = sp.N(sp.expand(expr).coeff(z, n - 1), 60)
        sol = sp.solve(sp.Eq(eq, 0), coeff_symbols[n])
        if not sol:
            raise RuntimeError(f"could not solve infinity coefficient {kind}_{n}")
        coeff.append(complex(sp.N(sol[0], 60)))
    return tuple(coeff)


def _series_value_and_r_derivative(r, coeff):
    z = 1.0 / r
    val = sum(c * z**i for i, c in enumerate(coeff))
    dz_val = sum(i * c * z ** (i - 1) for i, c in enumerate(coeff[1:], start=1))
    return val, dz_val * (-1.0 / (r * r))


def _infinity_basis(r, kind, omega, radial_lambda, order):
    coeff = _infinity_series_coefficients(kind, float(omega), float(radial_lambda), int(order))
    y, yr = _series_value_and_r_derivative(r, coeff)
    f = _factor_value(r, kind, omega)
    logp, _ = _factor_log_derivative(r, kind, omega)
    return f * y, f * (logp * y + yr)


def solve_rin_asymptotic(
    omega,
    radial_lambda,
    r_match,
    infinity_order=6,
    horizon_order=3,
    eps=1e-4,
    rtol=3e-12,
    atol=1e-14,
):
    """Solve R_in by direct radial integration and asymptotic matching."""
    rp, _ = kerr_horizons(1.0, A_KERR)
    r0 = rp + eps
    hcoeff = _horizon_series_coefficients(float(omega), float(radial_lambda), int(horizon_order))
    h, hp = _eval_power_series(eps, hcoeff)
    f0 = _factor_value(r0, "horizon", omega)
    logp0, _ = _factor_log_derivative(r0, "horizon", omega)
    y0 = np.array([f0 * h, f0 * (logp0 * h + hp)], dtype=complex)
    sol = solve_ivp(
        lambda r, y: _radial_rhs(r, y, omega, radial_lambda),
        (r0, r_match),
        y0,
        method="DOP853",
        rtol=rtol,
        atol=atol,
    )
    if not sol.success:
        raise RuntimeError(sol.message)

    inc, incp = _infinity_basis(r_match, "inc", omega, radial_lambda, infinity_order)
    ref, refp = _infinity_basis(r_match, "ref", omega, radial_lambda, infinity_order)
    b_inc, b_ref = np.linalg.solve(
        np.array([[inc, ref], [incp, refp]], dtype=complex),
        np.array([sol.y[0, -1], sol.y[1, -1]], dtype=complex),
    )
    return RInAmplitudeResult(
        omega=omega,
        radial_lambda=radial_lambda,
        incidence_amplitude=b_inc,
        reflection_amplitude=b_ref,
        method=f"asymptotic-ode:hor{horizon_order}:inf{infinity_order}",
        r_match=r_match,
    )


def _eval_power_series(x, coeff):
    val = sum(c * x**i for i, c in enumerate(coeff))
    der = sum(i * c * x ** (i - 1) for i, c in enumerate(coeff[1:], start=1))
    return val, der


def _transformed_operator(r, du, d2u, u_r, u_rr, kind, omega, radial_lambda):
    a2, a1, a0 = _radial_coefficients(r, omega, radial_lambda)
    logp, logpp = _factor_log_derivative(r, kind, omega)
    b2 = a2 * u_r * u_r
    b1 = a2 * (2.0 * logp * u_r + u_rr) + a1 * u_r
    b0 = a2 * (logpp + logp * logp) + a1 * logp + a0
    return np.diag(b2) @ d2u + np.diag(b1) @ du + np.diag(b0)


def _solve_cheb_branch(kind, omega, radial_lambda, n, r_match):
    rp, _ = kerr_horizons(1.0, A_KERR)
    dy, y = cheb(n)
    if kind == "horizon":
        u = (y + 1.0) / 2.0
        length = r_match - rp
        r = rp + length * u
        u_r = np.full(n + 1, 1.0 / length)
        u_rr = np.zeros(n + 1)
        du = dy / 0.5
        d2u = du @ du
        r_eval = r.astype(complex)
        r_eval[-1] = rp + 1e-8
        mat = _transformed_operator(r_eval, du, d2u, u_r, u_rr, kind, omega, radial_lambda)
        mat[0, :] = 0.0
        mat[0, -1] = 1.0
        rhs = np.zeros(n + 1, dtype=complex)
        rhs[0] = 1.0
        vals = np.linalg.solve(mat, rhs)
        dvals = du @ vals
        idx = 0
        factor = _factor_value(r_match, kind, omega)
        logp, _ = _factor_log_derivative(r_match, kind, omega)
        return factor * vals[idx], factor * (logp * vals[idx] + dvals[idx] * u_r[idx])

    z_match = 1.0 / r_match
    z = z_match * (y + 1.0) / 2.0
    r = np.empty(n + 1)
    mask = z > 0.0
    r[mask] = 1.0 / z[mask]
    r[~mask] = 1e8
    z_r = -z * z
    z_rr = 2.0 * z**3
    z_r[-1] = -1e-16
    z_rr[-1] = 2e-24
    dz = dy / (z_match / 2.0)
    d2z = dz @ dz
    mat = _transformed_operator(r.astype(complex), dz, d2z, z_r, z_rr, kind, omega, radial_lambda)
    mat[0, :] = 0.0
    mat[0, -1] = 1.0
    rhs = np.zeros(n + 1, dtype=complex)
    rhs[0] = 1.0
    vals = np.linalg.solve(mat, rhs)
    dvals = dz @ vals
    idx = 0
    factor = _factor_value(r_match, kind, omega)
    logp, _ = _factor_log_derivative(r_match, kind, omega)
    return factor * vals[idx], factor * (logp * vals[idx] + dvals[idx] * z_r[idx])


def solve_rin_chebyshev(omega, radial_lambda, n=192, r_match=20.0):
    """Two-domain phase-peeled Chebyshev collocation for R_in.

    This is closest to the Schwarzschild spectral construction.  For
    omega=10 it resolves B_inc well and B_ref to order-of-magnitude accuracy;
    the tiny reflected mode is near the double-precision floor of the direct
    Teukolsky variable.
    """
    h, hp = _solve_cheb_branch("horizon", omega, radial_lambda, n, r_match)
    inc, incp = _solve_cheb_branch("inc", omega, radial_lambda, n, r_match)
    ref, refp = _solve_cheb_branch("ref", omega, radial_lambda, n, r_match)
    b_inc, b_ref = np.linalg.solve(
        np.array([[inc, ref], [incp, refp]], dtype=complex),
        np.array([h, hp], dtype=complex),
    )
    return RInAmplitudeResult(
        omega=omega,
        radial_lambda=radial_lambda,
        incidence_amplitude=b_inc,
        reflection_amplitude=b_ref,
        method=f"chebyshev:n{n}",
        r_match=r_match,
    )
