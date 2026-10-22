"""Nonlinear Green-function diagnostics for scalar Kerr modes.

The default source model is the Kerr-covariant scalar-power source obtained
from ``Box Phi + eps_n |Phi|^(2n) Phi = 0``.  After multiplying by
``Sigma = r^2 + a^2 cos(theta)^2`` and projecting onto a target spheroidal
harmonic, the self-channel radial source is

    (r^2 C0 + a^2 C2) |R|^(2n) R,

where C0 and C2 are the angular projections without and with an extra
``cos(theta)^2`` factor.  The radial integral uses the physical ``dr`` measure.
"""

from dataclasses import dataclass
from functools import lru_cache
import math
import warnings

import numpy as np
from scipy.integrate import IntegrationWarning, quad
from scipy.special import spherical_jn, spherical_yn

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
    scalar_power_coupling,
    teukolsky_lambda_s0,
)


@dataclass(frozen=True)
class KerrScalarGreenDiagnostics:
    """Radial Green-function source diagnostics for one scalar Kerr mode."""

    M: float
    a: float
    l: int
    l_target: int
    m: int
    omega: float
    radial_lambda: float
    radial_lambda_source: float
    angular_coupling: complex
    angular_coupling_cos2: complex
    nonlinearity_order: int
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
    tail_epsrel: float
    radial_weight_model: str
    radial_integral_method: str
    linear_solver: str
    B_inc: complex
    B_ref: complex
    B_inc_target: complex
    B_ref_target: complex
    flux_normalization_condition_number: float
    wronskian: complex
    wronskian_outer: complex
    wronskian_relative_error: float
    source_projection_ref: complex
    source_projection_hor: complex
    A_ref_1: complex
    A_hor_1: complex
    Cl: float
    status: str


@dataclass(frozen=True)
class KerrScalarFluxCoefficients:
    """Boundary amplitudes and flux coefficients at unit incident amplitude."""

    A_ref_fixed_incident: complex
    A_hor_fixed_incident: complex
    horizon_factor: float
    T0: float
    R0: float
    linear_balance: float
    T1: float
    R1: float
    nonlinear_balance: float
    horizon_response: float


def scalar_monopole_low_frequency_integral(nonlinearity_order):
    """Return the analytic far-zone integral for the scalar monopole."""
    n = nonlinearity_order
    if not isinstance(n, (int, np.integer)) or n < 1:
        raise ValueError("nonlinearity_order must be a positive integer.")
    weighted_logs = sum(
        (-1) ** (j + 1)
        * j ** (2 * n)
        * math.comb(2 * n + 2, n + 1 - j)
        * math.log(j)
        for j in range(1, n + 2)
    )
    return (
        (-1) ** n
        * weighted_logs
        / (4.0 * (n + 1) * math.factorial(2 * n - 1))
    )


def scalar_monopole_low_frequency_coefficient(nonlinearity_order):
    """Return the coefficient of omega**(2n-2) in the monopole response."""
    n = int(nonlinearity_order)
    integral = scalar_monopole_low_frequency_integral(n)
    return 2.0 * integral / math.pi**n


def _validate_axisymmetric_multipole(l):
    if not isinstance(l, (int, np.integer)) or l < 0:
        raise ValueError("l must be a nonnegative integer.")
    return int(l)


@lru_cache(maxsize=None)
def scalar_axisymmetric_cubic_low_frequency_integral(l, max_cycles=800):
    r"""Return ``-int x^2 y_l(x) j_l(x)^3 dx`` on ``[0, infinity)``.

    Partial integrals ending at integer multiples of pi have an inverse-power
    tail.  Four nested cutoffs and an extrapolation in ``N^-2, N^-3, N^-4``
    remove that tail without introducing an oscillatory regulator.
    """
    l = _validate_axisymmetric_multipole(l)
    if not isinstance(max_cycles, (int, np.integer)) or max_cycles < 80:
        raise ValueError("max_cycles must be an integer >= 80.")
    max_cycles = int(max_cycles)
    checkpoints = np.asarray(
        [max_cycles // 8, max_cycles // 4, max_cycles // 2, max_cycles],
        dtype=int,
    )
    if len(set(checkpoints)) != 4:
        raise ValueError("max_cycles is too small for four nested cutoffs.")

    def integrand(x):
        return (
            -x**2
            * spherical_yn(l, x)
            * spherical_jn(l, x) ** 3
        )

    partials = []
    running = 0.0
    for cycle in range(1, max_cycles + 1):
        left = 1.0e-8 if cycle == 1 else (cycle - 1) * math.pi
        right = cycle * math.pi
        value, _ = quad(
            integrand,
            left,
            right,
            epsabs=2.0e-14,
            epsrel=2.0e-13,
            limit=100,
        )
        running += value
        if cycle in checkpoints:
            partials.append(running)

    inverse_cycles = checkpoints.astype(float) ** -1
    design = np.column_stack(
        [
            np.ones(4),
            inverse_cycles**2,
            inverse_cycles**3,
            inverse_cycles**4,
        ]
    )
    return float(np.linalg.solve(design, np.asarray(partials))[0])


@lru_cache(maxsize=None)
def scalar_axisymmetric_cubic_low_frequency_phase_integral(l, max_cycles=800):
    r"""Return ``int x^2 j_l(x)^4 dx`` on ``[0, infinity)``.

    This positive integral is the imaginary, phase-shifting part of the
    leading unit-horizon Green amplitude.  Partial integrals ending at
    integer multiples of pi have a leading ``N^-1`` tail, which is removed
    together with the next two inverse powers.
    """
    l = _validate_axisymmetric_multipole(l)
    if not isinstance(max_cycles, (int, np.integer)) or max_cycles < 80:
        raise ValueError("max_cycles must be an integer >= 80.")
    max_cycles = int(max_cycles)
    checkpoints = np.asarray(
        [max_cycles // 8, max_cycles // 4, max_cycles // 2, max_cycles],
        dtype=int,
    )
    if len(set(checkpoints)) != 4:
        raise ValueError("max_cycles is too small for four nested cutoffs.")

    def integrand(x):
        return x**2 * spherical_jn(l, x) ** 4

    partials = []
    running = 0.0
    for cycle in range(1, max_cycles + 1):
        left = 0.0 if cycle == 1 else (cycle - 1) * math.pi
        right = cycle * math.pi
        value, _ = quad(
            integrand,
            left,
            right,
            epsabs=2.0e-14,
            epsrel=2.0e-13,
            limit=100,
        )
        running += value
        if cycle in checkpoints:
            partials.append(running)

    inverse_cycles = checkpoints.astype(float) ** -1
    design = np.column_stack(
        [
            np.ones(4),
            inverse_cycles,
            inverse_cycles**2,
            inverse_cycles**3,
        ]
    )
    return float(np.linalg.solve(design, np.asarray(partials))[0])


def scalar_axisymmetric_cubic_low_frequency_coupling(l):
    r"""Return ``int |Y_l0|^4 dOmega`` in the spherical limit."""
    l = _validate_axisymmetric_multipole(l)
    order = max(64, 2 * l + 4)
    x, weights = np.polynomial.legendre.leggauss(order)
    coefficients = np.zeros(l + 1)
    coefficients[l] = 1.0
    legendre = np.polynomial.legendre.legval(x, coefficients)
    return float(
        (2 * l + 1) ** 2
        * np.sum(weights * legendre**4)
        / (8.0 * math.pi)
    )


def scalar_axisymmetric_cubic_low_frequency_response(l, max_cycles=800):
    r"""Return ``lim_(omega->0) T1/T0`` for the ``(l,0)`` self channel."""
    coupling = scalar_axisymmetric_cubic_low_frequency_coupling(l)
    integral = scalar_axisymmetric_cubic_low_frequency_integral(l, max_cycles)
    return 8.0 * coupling * integral


def _scalar_axisymmetric_low_frequency_matching(l, a, M=1.0):
    l = _validate_axisymmetric_multipole(l)
    M = float(M)
    a = float(a)
    if M <= 0.0 or abs(a) >= M:
        raise ValueError("Require M > 0 and subextremal |a| < M.")
    gap = math.sqrt(M**2 - a**2)
    legendre_leading = math.comb(2 * l, l) / 2.0**l
    odd_double_factorial = math.factorial(2 * l + 1) / (
        2.0**l * math.factorial(l)
    )
    return (
        legendre_leading
        * odd_double_factorial
        * (M / gap) ** l
    )


def scalar_axisymmetric_cubic_low_frequency_horizon_coefficient(
    l, a, M=1.0, max_cycles=800
):
    r"""Return the leading complex coefficient of the unit-horizon amplitude.

    The convention is
    ``A_H^(1) / M^2 = coefficient * (M omega)^(-2l-2) * (1 + o(1))``.
    Its real part changes the horizon flux, while its imaginary part is the
    first-order horizon-wave phase response.
    """
    matching = _scalar_axisymmetric_low_frequency_matching(l, a, M)
    coupling = scalar_axisymmetric_cubic_low_frequency_coupling(l)
    dissipative = scalar_axisymmetric_cubic_low_frequency_integral(
        l, max_cycles
    )
    reactive = scalar_axisymmetric_cubic_low_frequency_phase_integral(
        l, max_cycles
    )
    return coupling * matching**2 * (dissipative + 1j * reactive)


def scalar_axisymmetric_cubic_low_frequency_relative_horizon_amplitude(
    l, max_cycles=800
):
    r"""Return the fixed-incident relative horizon-amplitude limit.

    This is ``lim A_H^(1)/|B_inc|^2`` for the cubic axisymmetric self channel.
    It is independent of spin at fixed subextremality.
    """
    coupling = scalar_axisymmetric_cubic_low_frequency_coupling(l)
    dissipative = scalar_axisymmetric_cubic_low_frequency_integral(
        l, max_cycles
    )
    reactive = scalar_axisymmetric_cubic_low_frequency_phase_integral(
        l, max_cycles
    )
    return 4.0 * coupling * (dissipative + 1j * reactive)


def scalar_axisymmetric_linear_low_frequency_coefficient(l, a, M=1.0):
    r"""Return the coefficient of ``(M omega)^(2l+2)`` in ``T0``.

    The horizon-normalized static solution is
    ``P_l((r-M)/sqrt(M^2-a^2))``.  Matching its growing branch to
    ``j_l(omega r)`` fixes the incident amplitude and hence the coefficient.
    """
    M = float(M)
    a = float(a)
    matching = _scalar_axisymmetric_low_frequency_matching(l, a, M)
    gap = math.sqrt(M**2 - a**2)
    r_plus = M + gap
    horizon_area_factor = (r_plus**2 + a**2) / M**2
    return 4.0 * horizon_area_factor / matching**2


def fixed_incident_flux_coefficients(result):
    """Convert a unit-horizon self-channel solve to fixed-incident fluxes.

    The source scales as ``|alpha|^(2n) alpha`` under
    ``R^(0) -> alpha R^(0)``.  Setting ``alpha = 1/B_inc`` therefore gives
    fixed-incident first-order amplitudes with the corresponding nonlinear
    normalization factor.
    """
    if result.l_target != result.l:
        raise ValueError("Flux coefficients require the self channel l_target == l.")
    if result.omega == 0.0:
        raise ValueError("Flux coefficients require nonzero omega.")

    b_inc = result.B_inc
    norm2 = abs(b_inc) ** 2
    nonlinearity_order = result.nonlinearity_order
    if norm2 == 0.0:
        raise ZeroDivisionError("B_inc vanishes; fixed-incident normalization is undefined.")

    horizon_factor = (
        result.p_horizon * (result.r_plus**2 + result.a**2) / result.omega
    )
    nonlinear_norm = norm2**nonlinearity_order
    interference_norm = norm2 ** (nonlinearity_order + 1)
    A_ref_fixed = result.A_ref_1 / (nonlinear_norm * b_inc)
    A_hor_fixed = result.A_hor_1 / (nonlinear_norm * b_inc)
    T0 = horizon_factor / norm2
    R0 = abs(result.B_ref / b_inc) ** 2
    T1 = 2.0 * horizon_factor * result.A_hor_1.real / interference_norm
    R1 = (
        2.0
        * (result.B_ref.conjugate() * result.A_ref_1).real
        / interference_norm
    )
    horizon_response = 2.0 * result.A_hor_1.real / nonlinear_norm

    return KerrScalarFluxCoefficients(
        A_ref_fixed_incident=A_ref_fixed,
        A_hor_fixed_incident=A_hor_fixed,
        horizon_factor=float(horizon_factor),
        T0=float(T0),
        R0=float(R0),
        linear_balance=float(T0 + R0 - 1.0),
        T1=float(T1),
        R1=float(R1),
        nonlinear_balance=float(T1 + R1),
        horizon_response=float(horizon_response),
    )


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


def _rstar_horizon_distance(distance, params):
    """Evaluate the existing tortoise convention without subtracting radii."""
    distance = np.asarray(distance, dtype=float)
    if np.any(distance <= 0):
        raise ValueError("Horizon distance must be positive.")
    gap = params.rp - params.rm
    if abs(params.a) < 1e-14:
        return params.rp + distance + 2*params.M*np.log(distance/(2*params.M))
    return (params.rp + distance + 2*params.M*np.log(distance+gap)
            - 2*params.M*params.rp/gap*np.log1p(gap/distance))


def _horizon_log_rule(params, r_match, order, min_log):
    """Panel rule in log((r-r_plus)/(r_plus-r_minus)); dr is preserved."""
    gap = params.rp - params.rm
    upper = np.log((r_match-params.rp)/gap)
    if not np.isfinite(min_log) or min_log >= upper:
        raise ValueError("inner_log_min must be finite and below the matching point.")
    edges = np.linspace(min_log, upper, int(np.ceil(upper-min_log))+1)
    x, w = np.polynomial.legendre.leggauss(order)
    middle = (edges[1:]+edges[:-1])/2
    half = np.diff(edges)/2
    t = (middle[:, None]+half[:, None]*x).ravel()
    distance = gap*np.exp(t)
    weights = (half[:, None]*w).ravel()*distance
    return distance, weights, gap*np.exp(min_log)


def _complex_weighted_sum(values, weights):
    return np.sum(weights * values)


def _solve_matched_mode(
    l,
    m,
    omega,
    params,
    lam,
    z_match,
    N_outer,
    N_inner,
    active_mapping,
    kappa_outer,
    kappa_inner,
    linear_solver,
):
    """Solve down/up/in branches and match the in solution at z_match."""
    down = _solve_branch(
        N_outer, 0.0, z_match, "down", "left",
        params, active_mapping, kappa_outer,
        l, m, omega, lam, linear_solver,
    )
    up = _solve_branch(
        N_outer, 0.0, z_match, "up", "left",
        params, active_mapping, kappa_outer,
        l, m, omega, lam, linear_solver,
    )
    inner = _solve_branch(
        N_inner, z_match, 1.0, "in", "right",
        params, active_mapping, kappa_inner,
        l, m, omega, lam, linear_solver,
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
    flux_normalization_condition_number = float(
        (abs(B_inc) ** 2 + abs(B_ref) ** 2) / abs(flux_norm)
    )

    down_eval = _BranchEvaluator(
        down, 0.0, z_match, "down", params, omega, m, active_mapping, kappa_outer
    )
    up_eval = _BranchEvaluator(
        up, 0.0, z_match, "up", params, omega, m, active_mapping, kappa_outer
    )
    inner_eval = _BranchEvaluator(
        inner, z_match, 1.0, "in", params, omega, m, active_mapping, kappa_inner
    )

    return {
        "lambda": lam,
        "B_inc": B_inc,
        "B_ref": B_ref,
        "flux_norm": flux_norm,
        "flux_normalization_condition_number": flux_normalization_condition_number,
        "R_down": R_down,
        "Rr_down": Rr_down,
        "R_up": R_up,
        "Rr_up": Rr_up,
        "R_in": R_in,
        "Rr_in": Rr_in,
        "down_eval": down_eval,
        "up_eval": up_eval,
        "inner_eval": inner_eval,
    }


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
    source_mode,
    target_mode,
    c_ang,
    c_ang_cos2,
    nonlinearity_order,
    epsrel=1e-9,
):
    """Outer-domain physical source integral with explicit phase channels."""
    n = int(nonlinearity_order)
    phase_indices = range(-2 * n - 2, 2 * n + 3, 2)

    def channel_amplitude(phase_index):
        def amplitude(x):
            r = _r_from_rstar(x, params)
            z = params.rp / r
            source_down_amp = source_mode["down_eval"].u(z) / r
            source_up_amp = source_mode["up_eval"].u(z) / r
            target_down_amp = target_mode["down_eval"].u(z) / r
            target_up_amp = target_mode["up_eval"].u(z) / r
            radial_weight = r**2 * c_ang + a**2 * c_ang_cos2
            dr_dx = delta(r, M=params.M, a=params.a) / (r**2 + a**2)
            source_prefactor = radial_weight * dr_dx

            down_term = source_mode["B_inc"] * source_down_amp
            up_term = source_mode["B_ref"] * source_up_amp
            down_conj_term = np.conj(down_term)
            up_conj_term = np.conj(up_term)
            if test_kind == "ref":
                tests = [
                    (-1, target_mode["B_inc"], target_down_amp),
                    (1, target_mode["B_ref"], target_up_amp),
                ]
            elif test_kind == "hor":
                tests = [(1, 1.0 + 0.0j, target_up_amp)]
            else:
                raise ValueError("test_kind must be 'ref' or 'hor'.")

            total = 0.0 + 0.0j
            for test_phase, test_coeff, test_amp in tests:
                test_term = test_coeff * test_amp
                for up_count in range(n + 2):
                    field_phase = -(n + 1) + 2 * up_count
                    field_term = (
                        math.comb(n + 1, up_count)
                        * down_term ** (n + 1 - up_count)
                        * up_term**up_count
                    )
                    for down_conj_count in range(n + 1):
                        conj_phase = -n + 2 * down_conj_count
                        conj_term = (
                            math.comb(n, down_conj_count)
                            * down_conj_term**down_conj_count
                            * up_conj_term ** (n - down_conj_count)
                        )
                        if (
                            test_phase + field_phase + conj_phase
                            == phase_index
                        ):
                            total += test_term * field_term * conj_term
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
    radial_lambda_target=None,
    l_target=None,
    angular_coupling=None,
    Cl=1.0,
    quad_order=240,
    tail_epsrel=1e-9,
    radial_weight_model="kerr-covariant-sigma-dr",
    angular_coupling_cos2=None,
    linear_solver="direct",
    nonlinearity_order=1,
    inner_quadrature="legendre",
    inner_log_min=-30.0,
):
    """Compute nonlinear Green-function radial source integrals.

    The default ``kerr-covariant-sigma-dr`` model projects the scalar-power
    source from the covariant Kerr equation.  The old
    ``legacy-bondi-dr-over-r2`` model is retained only to reproduce early
    diagnostics.
    """
    if abs(omega) <= 0:
        raise ValueError("omega must be nonzero.")
    if abs(a) >= M:
        raise ValueError("Require subextremal Kerr, |a| < M.")
    if l < abs(m):
        raise ValueError("Require l >= |m|.")
    if l_target is None:
        l_target = l
    if l_target < abs(m):
        raise ValueError("Require l_target >= |m|.")
    if (
        not isinstance(nonlinearity_order, (int, np.integer))
        or nonlinearity_order < 1
    ):
        raise ValueError("nonlinearity_order must be a positive integer.")
    if quad_order < 16:
        raise ValueError("quad_order is too small for a stable diagnostic.")
    if inner_quadrature not in {"legendre", "log-horizon"}:
        raise ValueError("inner_quadrature must be 'legendre' or 'log-horizon'.")
    if inner_quadrature == "log-horizon" and radial_weight_model != "kerr-covariant-sigma-dr":
        raise ValueError("log-horizon quadrature requires the covariant source.")
    if radial_weight_model not in {
        "kerr-covariant-sigma-dr",
        "legacy-bondi-dr-over-r2",
    }:
        raise ValueError(
            "radial_weight_model must be 'kerr-covariant-sigma-dr' "
            "or 'legacy-bondi-dr-over-r2'."
        )
    if linear_solver not in {"direct", "equilibrated"}:
        raise ValueError("linear_solver must be 'direct' or 'equilibrated'.")

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

    lam_source = radial_lambda
    if lam_source is None:
        lam_source = teukolsky_lambda_s0(l, m, a, omega, lmax_extra=lmax_extra)
    lam_target = radial_lambda_target
    if lam_target is None:
        if l_target == l and radial_lambda is not None:
            lam_target = radial_lambda
        else:
            lam_target = teukolsky_lambda_s0(
                l_target, m, a, omega, lmax_extra=lmax_extra
            )
    c_ang = angular_coupling
    if c_ang is None:
        c_ang = scalar_power_coupling(
            l,
            m,
            a,
            omega,
            nonlinearity_order,
            l_target=l_target,
            lmax_extra=lmax_extra,
        )
    c_ang_cos2 = angular_coupling_cos2
    if c_ang_cos2 is None:
        c_ang_cos2 = scalar_power_coupling(
            l,
            m,
            a,
            omega,
            nonlinearity_order,
            l_target=l_target,
            lmax_extra=lmax_extra,
            cos_power=2,
        )

    source_mode = _solve_matched_mode(
        l, m, omega, params, lam_source, z_match,
        N_outer, N_inner, active_mapping, kappa_outer, kappa_inner,
        linear_solver,
    )
    if l_target == l and abs(lam_target - lam_source) <= 1e-13:
        target_mode = source_mode
    else:
        target_mode = _solve_matched_mode(
            l_target, m, omega, params, lam_target, z_match,
            N_outer, N_inner, active_mapping, kappa_outer, kappa_inner,
            linear_solver,
        )

    def R_source(z):
        z = np.asarray(z, dtype=float)
        out = np.empty(z.shape, dtype=complex)
        outer = z < z_match
        if np.any(outer):
            out[outer] = (
                source_mode["B_inc"] * source_mode["down_eval"].R(z[outer])
                + source_mode["B_ref"] * source_mode["up_eval"].R(z[outer])
            )
        if np.any(~outer):
            out[~outer] = source_mode["inner_eval"].R(z[~outer])
        return out

    def Rtest_ref(z):
        z = np.asarray(z, dtype=float)
        out = np.empty(z.shape, dtype=complex)
        outer = z < z_match
        if np.any(outer):
            out[outer] = (
                target_mode["B_inc"] * target_mode["down_eval"].R(z[outer])
                + target_mode["B_ref"] * target_mode["up_eval"].R(z[outer])
            )
        if np.any(~outer):
            out[~outer] = target_mode["inner_eval"].R(z[~outer])
        return out

    def Rtest_hor(z):
        z = np.asarray(z, dtype=float)
        out = np.empty(z.shape, dtype=complex)
        outer = z < z_match
        if np.any(outer):
            out[outer] = target_mode["up_eval"].R(z[outer])
        if np.any(~outer):
            rin = target_mode["inner_eval"].R(z[~outer])
            out[~outer] = (
                -np.conj(target_mode["B_ref"]) * rin
                + target_mode["B_inc"] * np.conj(rin)
            ) / target_mode["flux_norm"]
        return out

    d_match = delta(params.rp / z_match, M=M, a=a)
    wronskian = d_match * (
        target_mode["R_in"] * target_mode["Rr_up"]
        - target_mode["R_up"] * target_mode["Rr_in"]
    )
    wronskian_outer = d_match * (
        (
            target_mode["B_inc"] * target_mode["R_down"]
            + target_mode["B_ref"] * target_mode["R_up"]
        )
        * target_mode["Rr_up"]
        - target_mode["R_up"]
        * (
            target_mode["B_inc"] * target_mode["Rr_down"]
            + target_mode["B_ref"] * target_mode["Rr_up"]
        )
    )
    wronskian_relative_error = float(
        abs(wronskian - wronskian_outer) / max(abs(wronskian), 1e-300)
    )

    if radial_weight_model == "kerr-covariant-sigma-dr":
        if inner_quadrature == "log-horizon":
            distance, weights, cutoff = _horizon_log_rule(
                params, r_match, quad_order, inner_log_min)
            r = params.rp + distance
            z = params.rp/r
            p = omega-m*params.omega_h
            phase = np.exp(-1j*p*_rstar_horizon_distance(distance, params))
            R0_values = phase*source_mode["inner_eval"].u(z)
            target_in = phase*target_mode["inner_eval"].u(z)
            target_up = (-np.conj(target_mode["B_ref"])*target_in
                         + target_mode["B_inc"]*np.conj(target_in))/target_mode["flux_norm"]
        else:
            z, z_weights = _gauss_interval(z_match, 1.0, quad_order)
            r = params.rp / z
            weights = z_weights * params.rp / z**2
            R0_values = R_source(z)
            target_in, target_up = Rtest_ref(z), Rtest_hor(z)
        power_radial = (
            np.abs(R0_values) ** (2 * nonlinearity_order) * R0_values
        )
        source = (r**2 * c_ang + a**2 * c_ang_cos2) * power_radial
        source_projection_ref = _complex_weighted_sum(target_in * source, weights)
        source_projection_hor = _complex_weighted_sum(target_up * source, weights)
        if inner_quadrature == "log-horizon":
            # Integrate the leading horizon power over [0, cutoff] analytically.
            phase_cut = np.exp(-1j*p*_rstar_horizon_distance(cutoff, params))
            exponent = 4*params.M*params.rp*p/(params.rp-params.rm)
            oscillatory = cutoff*phase_cut**2/(1-1j*exponent)
            horizon_weight = params.rp**2*c_ang+a**2*c_ang_cos2
            source_projection_ref += horizon_weight*oscillatory
            source_projection_hor += horizon_weight*(
                -np.conj(target_mode["B_ref"])*oscillatory
                + target_mode["B_inc"]*cutoff)/target_mode["flux_norm"]

        x_match = rstar(r_match, M=M, a=a)
        source_projection_ref += _outer_phase_projection(
            "ref",
            x_match,
            params,
            omega,
            a,
            source_mode,
            target_mode,
            c_ang,
            c_ang_cos2,
            nonlinearity_order,
            epsrel=tail_epsrel,
        )
        source_projection_hor += _outer_phase_projection(
            "hor",
            x_match,
            params,
            omega,
            a,
            source_mode,
            target_mode,
            c_ang,
            c_ang_cos2,
            nonlinearity_order,
            epsrel=tail_epsrel,
        )
    else:
        z0, w0 = _gauss_interval(0.0, z_match, quad_order)
        z1, w1 = _gauss_interval(z_match, 1.0, quad_order)
        z = np.concatenate([z0, z1])
        z_weights = np.concatenate([w0, w1])
        weights = z_weights / params.rp
        R0_values = R_source(z)
        power_radial = (
            np.abs(R0_values) ** (2 * nonlinearity_order) * R0_values
        )
        source = c_ang * power_radial
        source_projection_ref = _complex_weighted_sum(Rtest_ref(z) * source, weights)
        source_projection_hor = _complex_weighted_sum(Rtest_hor(z) * source, weights)

    A_ref_1 = -Cl * source_projection_ref / wronskian
    A_hor_1 = -Cl * source_projection_hor / wronskian

    return KerrScalarGreenDiagnostics(
        M=M,
        a=a,
        l=l,
        l_target=int(l_target),
        m=m,
        omega=omega,
        radial_lambda=float(lam_target),
        radial_lambda_source=float(lam_source),
        angular_coupling=c_ang,
        angular_coupling_cos2=c_ang_cos2,
        nonlinearity_order=int(nonlinearity_order),
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
        tail_epsrel=float(tail_epsrel),
        radial_weight_model=radial_weight_model,
        radial_integral_method=(
            "phase-channel-fourier-tail"
            if radial_weight_model == "kerr-covariant-sigma-dr"
            else "compact-z-gauss"
        ),
        linear_solver=linear_solver,
        B_inc=source_mode["B_inc"],
        B_ref=source_mode["B_ref"],
        B_inc_target=target_mode["B_inc"],
        B_ref_target=target_mode["B_ref"],
        flux_normalization_condition_number=(
            target_mode["flux_normalization_condition_number"]
        ),
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
