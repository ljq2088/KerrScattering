"""Scalar (s=0) Teukolsky building blocks on Kerr.

The module implements the convention

    d/dr (Delta dR/dr) + (K**2 / Delta - lambda) R = 0,

where K = (r**2 + a**2) omega - a m and
lambda = A_lm(a omega) + a**2 omega**2 - 2 a m omega.
"""

from dataclasses import dataclass

import numpy as np
from scipy.integrate import solve_ivp
from scipy.linalg import eigh
from scipy.special import sph_harm_y


@dataclass(frozen=True)
class KerrParams:
    """Kerr background parameters."""

    M: float = 1.0
    a: float = 0.0

    @property
    def rp(self):
        return self.M + np.sqrt(self.M**2 - self.a**2)

    @property
    def rm(self):
        return self.M - np.sqrt(self.M**2 - self.a**2)

    @property
    def omega_h(self):
        return self.a / (self.rp**2 + self.a**2)


@dataclass(frozen=True)
class ScalarSpheroidalMode:
    """Scalar spheroidal harmonic expanded in normalized spherical harmonics."""

    l: int
    m: int
    c: float
    eigenvalue: float
    ells: np.ndarray
    coefficients: np.ndarray


def kerr_horizons(M=1.0, a=0.0):
    """Return outer and inner Kerr horizon radii."""
    params = KerrParams(M=M, a=a)
    return params.rp, params.rm


def delta(r, M=1.0, a=0.0):
    """Kerr horizon function Delta."""
    return r**2 - 2 * M * r + a**2


def drstar_dr(r, M=1.0, a=0.0):
    """Derivative of the Kerr tortoise coordinate."""
    return (r**2 + a**2) / delta(r, M, a)


def rstar(r, M=1.0, a=0.0):
    """Kerr tortoise coordinate, up to an irrelevant additive constant."""
    rp, rm = kerr_horizons(M, a)
    if abs(a) < 1e-14:
        return r + 2 * M * np.log(r / (2 * M) - 1)

    return (r
            + (2 * M * rp / (rp - rm)) * np.log(r - rp)
            - (2 * M * rm / (rp - rm)) * np.log(r - rm))


def _cos_y_ladder_coeff(ell, m):
    """Coefficient of Y_{ell,m} in cos(theta) Y_{ell-1,m}."""
    if ell <= abs(m):
        return 0.0
    return np.sqrt((ell**2 - m**2) / ((2 * ell - 1) * (2 * ell + 1)))


def _cos2_matrix(ells, m):
    """Matrix of cos(theta)^2 in the scalar spherical-harmonic basis."""
    index = {ell: i for i, ell in enumerate(ells)}
    mat = np.zeros((len(ells), len(ells)))
    for ell in ells:
        j = index[ell]

        up = _cos_y_ladder_coeff(ell + 1, m)
        down = _cos_y_ladder_coeff(ell, m)

        for ell_mid, coeff1 in ((ell + 1, up), (ell - 1, down)):
            if coeff1 == 0.0:
                continue

            up2 = _cos_y_ladder_coeff(ell_mid + 1, m)
            down2 = _cos_y_ladder_coeff(ell_mid, m)
            for ell_out, coeff2 in ((ell_mid + 1, up2), (ell_mid - 1, down2)):
                if ell_out in index and coeff2 != 0.0:
                    mat[index[ell_out], j] += coeff1 * coeff2
    return mat


def scalar_spheroidal_mode(l, m, c, lmax_extra=16):
    """Return the scalar spheroidal mode in a spherical-harmonic basis.

    The angular equation convention is

        L_sphere S + c**2 cos(theta)**2 S + A S = 0.

    Therefore A is obtained from the matrix
    diag(ell(ell+1)) - c**2 <ell|cos^2|ell'>.
    """
    if l < abs(m):
        raise ValueError("Require l >= |m|.")

    lmax = l + lmax_extra
    ells = np.arange(abs(m), lmax + 1)
    c2 = _cos2_matrix(ells, m)
    mat = np.diag(ells * (ells + 1.0)) - (c**2) * c2
    vals, vecs = eigh(mat)

    target = np.where(ells == l)[0][0]
    mode = int(np.argmax(np.abs(vecs[target, :])))
    coeffs = vecs[:, mode].astype(float)
    if coeffs[target] < 0.0:
        coeffs = -coeffs
    return ScalarSpheroidalMode(
        l=l,
        m=m,
        c=float(c),
        eigenvalue=float(vals[mode]),
        ells=ells,
        coefficients=coeffs,
    )


def scalar_spheroidal_eigenvalue(l, m, c, lmax_extra=16):
    """Return the scalar spheroidal angular eigenvalue A_lm(c)."""
    return scalar_spheroidal_mode(l, m, c, lmax_extra=lmax_extra).eigenvalue


def evaluate_scalar_spheroidal(mode, theta, phi=0.0):
    """Evaluate a scalar spheroidal harmonic from its spherical expansion."""
    theta = np.asarray(theta)
    value = np.zeros(theta.shape, dtype=complex)
    for ell, coeff in zip(mode.ells, mode.coefficients):
        value = value + coeff * sph_harm_y(int(ell), mode.m, theta, phi)
    if value.ndim == 0:
        return value.item()
    return value


def scalar_cubic_coupling(l_source, m, a, omega, l_target=None,
                          lmax_extra=16, quad_order=256, cos_power=0):
    """Project ``cos(theta)**p |S_lm|^2 S_lm`` onto a spheroidal harmonic.

    The returned coefficient is

        C^{(p)}_{l'lm}
        = int dOmega cos(theta)**p conj(S_{l'm}) |S_lm|^2 S_lm,

    with all spheroidal harmonics normalized to unit integral over the sphere.
    The same spheroidal parameter ``c = a omega`` is used for source and
    target modes.
    """
    if l_target is None:
        l_target = l_source
    if l_source < abs(m) or l_target < abs(m):
        raise ValueError("Require l_source,l_target >= |m|.")
    if cos_power < 0:
        raise ValueError("cos_power must be non-negative.")

    c = a * omega
    source = scalar_spheroidal_mode(l_source, m, c, lmax_extra=lmax_extra)
    target = scalar_spheroidal_mode(l_target, m, c, lmax_extra=lmax_extra)

    x, w = np.polynomial.legendre.leggauss(quad_order)
    theta = np.arccos(x)
    source_vals = evaluate_scalar_spheroidal(source, theta, 0.0)
    target_vals = evaluate_scalar_spheroidal(target, theta, 0.0)
    integrand = np.conj(target_vals) * np.abs(source_vals) ** 2 * source_vals
    if cos_power:
        integrand = (x ** int(cos_power)) * integrand
    return 2.0 * np.pi * np.sum(w * integrand)


def scalar_cubic_coupling_cos2(l_source, m, a, omega, l_target=None,
                               lmax_extra=16, quad_order=256):
    """Return the Kerr ``cos(theta)^2`` cubic angular projection."""
    return scalar_cubic_coupling(
        l_source,
        m,
        a,
        omega,
        l_target=l_target,
        lmax_extra=lmax_extra,
        quad_order=quad_order,
        cos_power=2,
    )


def scalar_cubic_couplings(l_source, m, a, omega, l_targets,
                           lmax_extra=16, quad_order=256, cos_power=0):
    """Return cubic source projection coefficients for several target modes."""
    return {
        int(l_target): scalar_cubic_coupling(
            l_source,
            m,
            a,
            omega,
            l_target=int(l_target),
            lmax_extra=lmax_extra,
            quad_order=quad_order,
            cos_power=cos_power,
        )
        for l_target in l_targets
    }


def teukolsky_lambda_s0(l, m, a, omega, lmax_extra=16):
    """Return the scalar Teukolsky radial separation constant lambda."""
    c = a * omega
    A = scalar_spheroidal_eigenvalue(l, m, c, lmax_extra=lmax_extra)
    return A + a**2 * omega**2 - 2 * a * m * omega


def radial_potential_s0(r, l, m, omega, M=1.0, a=0.0, eigenvalue=None):
    """Return K**2 / Delta - lambda in the s=0 Teukolsky radial equation."""
    lam = teukolsky_lambda_s0(l, m, a, omega) if eigenvalue is None else eigenvalue
    K = (r**2 + a**2) * omega - a * m
    return K**2 / delta(r, M, a) - lam


def radial_rhs_s0(r, y, l, m, omega, M=1.0, a=0.0, eigenvalue=None):
    """First-order system for the scalar Teukolsky radial equation."""
    R, Rp = y
    d = delta(r, M, a)
    dp = 2 * r - 2 * M
    V = radial_potential_s0(r, l, m, omega, M=M, a=a, eigenvalue=eigenvalue)
    Rpp = -(dp * Rp + V * R) / d
    return np.array([Rp, Rpp], dtype=complex)


def solve_scalar_in_mode(l, m, omega, M=1.0, a=0.0, r_out=None,
                         eps=1e-6, rtol=1e-9, atol=1e-11,
                         lmax_extra=16, radial_lambda=None):
    """Integrate the unit-horizon-amplitude scalar in mode.

    The returned amplitudes fit the large-r form

        R ~ Z_in exp(-i omega r*)/r + Z_out exp(+i omega r*)/r.
    """
    if r_out is None:
        r_out = max(200.0, 50.0 / max(abs(omega), 1e-6))

    params = KerrParams(M=M, a=a)
    rp = params.rp
    alpha_p = (rp**2 + a**2) / (rp - params.rm) if abs(a) > 1e-14 else 2 * M
    p_h = omega - m * params.omega_h
    exponent = -1j * alpha_p * p_h

    r0 = rp + eps
    R0 = eps ** exponent
    Rp0 = exponent * eps ** (exponent - 1)

    lam = radial_lambda
    if lam is None:
        lam = teukolsky_lambda_s0(l, m, a, omega, lmax_extra=lmax_extra)
    sol = solve_ivp(
        lambda r, y: radial_rhs_s0(r, y, l, m, omega, M=M, a=a, eigenvalue=lam),
        (r0, r_out),
        np.array([R0, Rp0], dtype=complex),
        rtol=rtol,
        atol=atol,
    )
    if not sol.success:
        raise RuntimeError(sol.message)

    R, Rp = sol.y[0, -1], sol.y[1, -1]
    x = rstar(r_out, M=M, a=a)
    xp = drstar_dr(r_out, M=M, a=a)
    f_in = np.exp(-1j * omega * x) / r_out
    f_out = np.exp(1j * omega * x) / r_out
    df_in = f_in * (-1j * omega * xp - 1.0 / r_out)
    df_out = f_out * (1j * omega * xp - 1.0 / r_out)

    mat = np.array([[f_in, f_out], [df_in, df_out]], dtype=complex)
    Zin, Zout = np.linalg.solve(mat, np.array([R, Rp], dtype=complex))

    return {
        "M": M,
        "a": a,
        "l": l,
        "m": m,
        "omega": omega,
        "lambda": lam,
        "r_plus": rp,
        "r_minus": params.rm,
        "omega_h": params.omega_h,
        "p_horizon": p_h,
        "r_out": r_out,
        "Z_in": Zin,
        "Z_out": Zout,
        "reflection_amplitude": Zout / Zin,
        "incident_amplitude": Zin,
        "status": "ok",
    }
