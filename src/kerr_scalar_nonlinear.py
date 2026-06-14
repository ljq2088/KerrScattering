"""Nonlinear Green-function diagnostics for scalar Kerr modes.

The default source model is the Kerr-covariant cubic scalar source obtained
from ``Box Phi + eps |Phi|^2 Phi = 0``.  After multiplying by
``Sigma = r^2 + a^2 cos(theta)^2`` and projecting onto a target spheroidal
harmonic, the self-channel radial source is

    (r^2 C0 + a^2 C2) |R|^2 R,

where C0 and C2 are the angular projections without and with an extra
``cos(theta)^2`` factor.  The radial integral uses the physical ``dr`` measure.
"""

from dataclasses import dataclass
import warnings

import numpy as np
from scipy.integrate import IntegrationWarning, quad

from .cheb import cheb_interpolate, real_to_cheb
from .kerr_scalar_spectral import (
    _basis_factor,
    _default_r_match,
    _field_and_radial_derivative,
    _solve_branch,
)
from .teukolsky_scalar import (
    KerrParams,
    drstar_dr,
    delta,
    rstar,
    scalar_cubic_coupling,
    scalar_cubic_coupling_cos2,
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
    angular_coupling_cos2: complex
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
    radial_integral_method: str
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


def _r_from_rstar(x, params):
    """Invert the Kerr tortoise coordinate on the outer domain."""
    x = np.asarray(x, dtype=float)
    scalar = x.ndim == 0
    x = np.atleast_1d(x)
    r = np.maximum(x, params.rp + 1.0)
    r = np.asarray(r, dtype=float)

    floor = params.rp + 1e-12
    for _ in range(16):
        f = rstar(r, M=params.M, a=params.a) - x
        fp = drstar_dr(r, M=params.M, a=params.a)
        step = f / fp
        trial = r - step
        bad = trial <= floor
        if np.any(bad):
            trial[bad] = 0.5 * (r[bad] + floor)
        r = trial
        if np.max(np.abs(step) / np.maximum(r, 1.0)) < 1e-13:
            break

    if scalar:
        return float(r[0])
    return r


def _quad_complex_infinite(g, x0, phase_frequency, epsrel=1e-9):
    """Integrate ``g(x) exp(i phase_frequency x)`` from x0 to infinity."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", IntegrationWarning)
        if abs(phase_frequency) < 1e-15:
            real = quad(lambda x: np.real(g(x)), x0, np.inf,
                        epsabs=1e-10, epsrel=epsrel, limit=300)[0]
            imag = quad(lambda x: np.imag(g(x)), x0, np.inf,
                        epsabs=1e-10, epsrel=epsrel, limit=300)[0]
            return real + 1j * imag

        k = abs(phase_frequency)
        phase_sign = 1.0 if phase_frequency > 0.0 else -1.0
        a_cos = quad(lambda x: np.real(g(x)), x0, np.inf, weight="cos", wvar=k,
                     epsabs=1e-10, epsrel=epsrel, limit=300, limlst=300)[0]
        a_sin = quad(lambda x: np.real(g(x)), x0, np.inf, weight="sin", wvar=k,
                     epsabs=1e-10, epsrel=epsrel, limit=300, limlst=300)[0]
        b_cos = quad(lambda x: np.imag(g(x)), x0, np.inf, weight="cos", wvar=k,
                     epsabs=1e-10, epsrel=epsrel, limit=300, limlst=300)[0]
        b_sin = quad(lambda x: np.imag(g(x)), x0, np.inf, weight="sin", wvar=k,
                     epsabs=1e-10, epsrel=epsrel, limit=300, limlst=300)[0]
    return (a_cos - phase_sign * b_sin) + 1j * (b_cos + phase_sign * a_sin)


def _outer_phase_projection(
    test_kind,
    x_match,
    params,
    omega,
    a,
    B_inc,
    B_ref,
    down_eval,
    up_eval,
    c_ang,
    c_ang_cos2,
    epsrel=1e-9,
):
    """Outer-domain physical source integral with explicit phase channels."""
    phase_indices = (-4, -2, 0, 2, 4)

    def channel_amplitude(phase_index):
        def amplitude(x):
            r = _r_from_rstar(x, params)
            z = params.rp / r
            down_amp = down_eval.u(z) / r
            up_amp = up_eval.u(z) / r
            radial_weight = r**2 * c_ang + a**2 * c_ang_cos2
            dr_dx = delta(r, M=params.M, a=params.a) / (r**2 + a**2)
            source_prefactor = radial_weight * dr_dx

            field = [
                (-1, B_inc, down_amp),
                (1, B_ref, up_amp),
            ]
            field_conj = [
                (1, np.conj(B_inc), np.conj(down_amp)),
                (-1, np.conj(B_ref), np.conj(up_amp)),
            ]
            if test_kind == "ref":
                tests = field
            elif test_kind == "hor":
                tests = [(1, 1.0 + 0.0j, up_amp)]
            else:
                raise ValueError("test_kind must be 'ref' or 'hor'.")

            total = 0.0 + 0.0j
            for s_test, c_test, a_test in tests:
                for s1, c1, a1 in field:
                    for s2, c2, a2 in field_conj:
                        for s3, c3, a3 in field:
                            if s_test + s1 + s2 + s3 == phase_index:
                                total += c_test * c1 * c2 * c3 * a_test * a1 * a2 * a3
            return source_prefactor * total

        return amplitude

    total = 0.0 + 0.0j
    for phase_index in phase_indices:
        total += _quad_complex_infinite(
            channel_amplitude(phase_index),
            x_match,
            phase_index * omega,
            epsrel=epsrel,
        )
    return total


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
    radial_weight_model="kerr-covariant-sigma-dr",
    angular_coupling_cos2=None,
):
    """Compute nonlinear Green-function radial source integrals.

    The default ``kerr-covariant-sigma-dr`` model projects the cubic scalar
    source from the covariant Kerr equation.  The old
    ``legacy-bondi-dr-over-r2`` model is retained only to reproduce early
    diagnostics.
    """
    if abs(omega) <= 0:
        raise ValueError("omega must be nonzero.")
    if abs(a) >= M:
        raise ValueError("Require subextremal Kerr, |a| < M.")
    if quad_order < 16:
        raise ValueError("quad_order is too small for a stable diagnostic.")
    if radial_weight_model not in {
        "kerr-covariant-sigma-dr",
        "legacy-bondi-dr-over-r2",
    }:
        raise ValueError(
            "radial_weight_model must be 'kerr-covariant-sigma-dr' "
            "or 'legacy-bondi-dr-over-r2'."
        )

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
    c_ang_cos2 = angular_coupling_cos2
    if c_ang_cos2 is None:
        c_ang_cos2 = scalar_cubic_coupling_cos2(
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

    if radial_weight_model == "kerr-covariant-sigma-dr":
        z, z_weights = _gauss_interval(z_match, 1.0, quad_order)
        r = params.rp / z
        weights = z_weights * params.rp / z**2
        R0_values = R0(z)
        cubic_radial = np.abs(R0_values) ** 2 * R0_values
        source = (r**2 * c_ang + a**2 * c_ang_cos2) * cubic_radial
        source_projection_ref = _complex_weighted_sum(Rtest_ref(z) * source, weights)
        source_projection_hor = _complex_weighted_sum(Rtest_hor(z) * source, weights)

        x_match = rstar(r_match, M=M, a=a)
        source_projection_ref += _outer_phase_projection(
            "ref",
            x_match,
            params,
            omega,
            a,
            B_inc,
            B_ref,
            down_eval,
            up_eval,
            c_ang,
            c_ang_cos2,
        )
        source_projection_hor += _outer_phase_projection(
            "hor",
            x_match,
            params,
            omega,
            a,
            B_inc,
            B_ref,
            down_eval,
            up_eval,
            c_ang,
            c_ang_cos2,
        )
    else:
        z0, w0 = _gauss_interval(0.0, z_match, quad_order)
        z1, w1 = _gauss_interval(z_match, 1.0, quad_order)
        z = np.concatenate([z0, z1])
        z_weights = np.concatenate([w0, w1])
        weights = z_weights / params.rp
        R0_values = R0(z)
        cubic_radial = np.abs(R0_values) ** 2 * R0_values
        source = c_ang * cubic_radial
        source_projection_ref = _complex_weighted_sum(Rtest_ref(z) * source, weights)
        source_projection_hor = _complex_weighted_sum(Rtest_hor(z) * source, weights)

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
        angular_coupling_cos2=c_ang_cos2,
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
        radial_weight_model=radial_weight_model,
        radial_integral_method=(
            "phase-channel-fourier-tail"
            if radial_weight_model == "kerr-covariant-sigma-dr"
            else "compact-z-gauss"
        ),
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
