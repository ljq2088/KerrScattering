"""Prototype nonlinear Green-function diagnostics for scalar Kerr modes.

This module does not claim the final physical Kerr self-interaction
normalization.  It provides the radial Green-function data needed to finish
that step: continued homogeneous solutions, a constant radial Wronskian, and
finite cubic source projections using the same compactified spectral solutions
as the validated linear solver.
"""

from dataclasses import dataclass

import numpy as np

from .cheb import cheb_interpolate, real_to_cheb
from .kerr_scalar_spectral import (
    _basis_factor,
    _default_r_match,
    _field_and_radial_derivative,
    _solve_branch,
)
from .teukolsky_scalar import (
    KerrParams,
    delta,
    scalar_cubic_coupling,
    teukolsky_lambda_s0,
)


@dataclass(frozen=True)
class KerrScalarGreenDiagnostics:
    """Radial Green-function source diagnostics for one scalar Kerr mode."""

    M: float
    a: float
    l: int
    m: int
    omega: float
    radial_lambda: float
    angular_coupling: complex
    r_plus: float
    r_minus: float
    omega_h: float
    p_horizon: float
    r_match: float
    z_match: float
    N_outer: int
    N_inner: int
    mapping: str
    quad_order: int
    radial_weight_model: str
    B_inc: complex
    B_ref: complex
    wronskian: complex
    wronskian_outer: complex
    wronskian_relative_error: float
    source_projection_ref: complex
    source_projection_hor: complex
    A_ref_1: complex
    A_hor_1: complex
    Cl: float
    status: str


class _BranchEvaluator:
    def __init__(self, branch_data, z_left, z_right, branch, params,
                 omega, m, mapping, kappa):
        self.z_left = z_left
        self.z_right = z_right
        self.branch = branch
        self.params = params
        self.omega = omega
        self.m = m
        self.mapping = mapping
        self.kappa = kappa
        self.re_coeff = real_to_cheb(np.real(branch_data["u"]))
        self.im_coeff = real_to_cheb(np.imag(branch_data["u"]))

    def _y_from_z(self, z):
        z = np.asarray(z, dtype=float)
        length = self.z_right - self.z_left
        if self.mapping == "linear" or self.kappa <= 0.0:
            return 1.0 - 2.0 * (z - self.z_left) / length
        arg = (z - self.z_left) * np.sinh(self.kappa) / length
        return 1.0 - 2.0 * np.arcsinh(arg) / self.kappa

    def u(self, z):
        y = self._y_from_z(z)
        return (
            cheb_interpolate(self.re_coeff, -1.0, 1.0, y)
            + 1j * cheb_interpolate(self.im_coeff, -1.0, 1.0, y)
        )

    def R(self, z):
        z = np.asarray(z, dtype=float)
        r = self.params.rp / z
        return _basis_factor(r, self.branch, self.params, self.omega, self.m) * self.u(z)


def _gauss_interval(a, b, order):
    x, w = np.polynomial.legendre.leggauss(order)
    z = 0.5 * (b - a) * x + 0.5 * (a + b)
    weights = 0.5 * (b - a) * w
    return z, weights


def _complex_weighted_sum(values, weights):
    return np.sum(weights * values)


def compute_kerr_scalar_green_diagnostics(
    l,
    m,
    omega,
    M=1.0,
    a=0.0,
    N_outer=128,
    N_inner=128,
    r_match=None,
    mapping="auto",
    lmax_extra=16,
    radial_lambda=None,
    angular_coupling=None,
    Cl=1.0,
    quad_order=240,
):
    """Compute prototype nonlinear Green-function radial source integrals.

    The radial source model uses the legacy Schwarzschild/Bondi compact-weight
    convention ``dr/r^2 = dz/r_+``.  The returned ``A_ref_1`` and ``A_hor_1``
    are therefore diagnostic Green-function amplitudes, not final calibrated
    Kerr observables.
    """
    if abs(omega) <= 0:
        raise ValueError("omega must be nonzero.")
    if abs(a) >= M:
        raise ValueError("Require subextremal Kerr, |a| < M.")
    if quad_order < 16:
        raise ValueError("quad_order is too small for a stable diagnostic.")

    params = KerrParams(M=M, a=a)
    if r_match is None:
        r_match = _default_r_match(M, a, omega)
    z_match = params.rp / r_match

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
    c_ang = angular_coupling
    if c_ang is None:
        c_ang = scalar_cubic_coupling(
            l, m, a, omega, l_target=l, lmax_extra=lmax_extra
        )

    down = _solve_branch(
        N_outer, 0.0, z_match, "down", "left",
        params, active_mapping, kappa_outer,
        l, m, omega, lam,
    )
    up = _solve_branch(
        N_outer, 0.0, z_match, "up", "left",
        params, active_mapping, kappa_outer,
        l, m, omega, lam,
    )
    inner = _solve_branch(
        N_inner, z_match, 1.0, "in", "right",
        params, active_mapping, kappa_inner,
        l, m, omega, lam,
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
    B_inc, B_ref = np.linalg.solve(match_matrix, np.array([R_in, Rr_in]))

    flux_norm = abs(B_inc) ** 2 - abs(B_ref) ** 2
    if abs(flux_norm) <= 1e-300:
        raise FloatingPointError("Degenerate in/up continuation normalization.")

    down_eval = _BranchEvaluator(
        down, 0.0, z_match, "down", params, omega, m, active_mapping, kappa_outer
    )
    up_eval = _BranchEvaluator(
        up, 0.0, z_match, "up", params, omega, m, active_mapping, kappa_outer
    )
    inner_eval = _BranchEvaluator(
        inner, z_match, 1.0, "in", params, omega, m, active_mapping, kappa_inner
    )

    def R0(z):
        z = np.asarray(z, dtype=float)
        out = np.empty(z.shape, dtype=complex)
        outer = z < z_match
        if np.any(outer):
            out[outer] = B_inc * down_eval.R(z[outer]) + B_ref * up_eval.R(z[outer])
        if np.any(~outer):
            out[~outer] = inner_eval.R(z[~outer])
        return out

    def Rtest_ref(z):
        return R0(z)

    def Rtest_hor(z):
        z = np.asarray(z, dtype=float)
        out = np.empty(z.shape, dtype=complex)
        outer = z < z_match
        if np.any(outer):
            out[outer] = up_eval.R(z[outer])
        if np.any(~outer):
            rin = inner_eval.R(z[~outer])
            out[~outer] = (-np.conj(B_ref) * rin + B_inc * np.conj(rin)) / flux_norm
        return out

    d_match = delta(params.rp / z_match, M=M, a=a)
    wronskian = d_match * (R_in * Rr_up - R_up * Rr_in)
    wronskian_outer = d_match * (
        (B_inc * R_down + B_ref * R_up) * Rr_up
        - R_up * (B_inc * Rr_down + B_ref * Rr_up)
    )
    wronskian_relative_error = float(
        abs(wronskian - wronskian_outer) / max(abs(wronskian), 1e-300)
    )

    z0, w0 = _gauss_interval(0.0, z_match, quad_order)
    z1, w1 = _gauss_interval(z_match, 1.0, quad_order)
    z = np.concatenate([z0, z1])
    weights = np.concatenate([w0, w1]) / params.rp
    source = np.abs(R0(z)) ** 2 * R0(z)

    source_projection_ref = c_ang * _complex_weighted_sum(Rtest_ref(z) * source, weights)
    source_projection_hor = c_ang * _complex_weighted_sum(Rtest_hor(z) * source, weights)

    A_ref_1 = -Cl * source_projection_ref / wronskian
    A_hor_1 = -Cl * source_projection_hor / wronskian

    return KerrScalarGreenDiagnostics(
        M=M,
        a=a,
        l=l,
        m=m,
        omega=omega,
        radial_lambda=float(lam),
        angular_coupling=c_ang,
        r_plus=float(params.rp),
        r_minus=float(params.rm),
        omega_h=float(params.omega_h),
        p_horizon=float(omega - m * params.omega_h),
        r_match=float(r_match),
        z_match=float(z_match),
        N_outer=int(N_outer),
        N_inner=int(N_inner),
        mapping="sinh" if use_sinh else "linear",
        quad_order=int(quad_order),
        radial_weight_model="legacy-bondi-dr-over-r2",
        B_inc=B_inc,
        B_ref=B_ref,
        wronskian=wronskian,
        wronskian_outer=wronskian_outer,
        wronskian_relative_error=wronskian_relative_error,
        source_projection_ref=source_projection_ref,
        source_projection_hor=source_projection_hor,
        A_ref_1=A_ref_1,
        A_hor_1=A_hor_1,
        Cl=float(Cl),
        status="ok",
    )
