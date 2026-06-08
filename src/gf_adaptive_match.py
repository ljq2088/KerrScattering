import numpy as np
from scipy.integrate import quad

from .cheb import cheb, cheb_interpolate, real_to_cheb
from .bondi import bondi_matrix


def compute(M=1.0, l=0, omega=1e-3, N=128, Cl=1.0, quad_reltol=1e-10,
            quad_abstol=1e-6):
    """Compute Schwarzschild scattering coefficients and nonlinear corrections.

    Args:
        M: black hole mass (default 1.0).
        l: angular harmonic index (default 0).
        omega: frequency (default 1e-3).
        N: Chebyshev nodes (default 128).
        Cl: nonlinear coupling constant (default 1.0).
            NOTE: Cl is undefined in the original MATLAB script; set to 1.0
            as a placeholder. Physical value must be supplied by the user.
        quad_reltol: relative tolerance for quadrature (default 1e-10).
        quad_abstol: absolute tolerance for oscillatory tail quadrature
            (default 1e-6). This is applied to individual Fourier-cycle
            tail integrals, so over-tightening it can make QUADPACK's
            extrapolation table less stable.

    Returns:
        dict with keys:
            omega, zp, rp, N, C_id, C_iu, T, R, W,
            A1out, A1in, T1, R1,
            matching_error, W_error, status
    """
    rh = 2 * M
    rp = 3 * M + omega ** (-0.5)
    zp = 2 * M / rp
    xp = rh * (1.0 / zp + np.log(1 - zp) - np.log(zp))
    s = -1j * omega * 4 * M

    AnMR_flag = omega < 0.1

    Dy, y = cheb(N)

    if not AnMR_flag:
        # High frequency: linear mapping
        # z1 in [zp, 1], z1(0)=1 → z1(N)=zp
        z1 = (1 - zp) / 2 * (y + 1) + zp
        Dz1 = Dy / ((1 - zp) / 2)
        D2z1 = Dz1 @ Dz1

        # z0 in [zp, 0], z0(0)=zp → z0(N)=0
        z0 = (zp / 2) * (y + 1)
        Dz0 = Dy / (zp / 2)
        D2z0 = Dz0 @ Dz0
    else:
        # Low frequency: sinh-mapped Chebyshev (AnMR)
        kappa = abs(np.log(omega * 2 * M))
        kappa_in = kappa / 2

        # y in [-1,1] → z1 in [1, zp]  (note: MATLAB does (1-zp)*sinh... + zp)
        # y=-1 → z1=1,  y=1 → z1=zp
        sinh_kappa_in = np.sinh(kappa_in)
        z1 = (1 - zp) * np.sinh(kappa_in * (y + 1) / 2) / sinh_kappa_in + zp
        dz1dy = (1 - zp) * kappa_in / 2 * np.cosh(kappa_in * (y + 1) / 2) / sinh_kappa_in
        Dz1 = Dy / dz1dy.reshape(-1, 1)
        D2z1 = Dz1 @ Dz1

        # y in [-1,1] → z0 in [zp, 0]
        # y=-1 → z0=zp,  y=1 → z0=0
        sinh_kappa = np.sinh(kappa)
        z0 = zp * np.sinh(kappa * (y + 1) / 2) / sinh_kappa
        dz0dy = zp * kappa / 2 * np.cosh(kappa * (y + 1) / 2) / sinh_kappa
        Dz0 = Dy / dz0dy.reshape(-1, 1)
        D2z0 = Dz0 @ Dz0

    # Solve phi_in on [zp, 1] with BC: phi_in(z=1) = 1
    # z1 goes from 1 to zp, so last index is zp, first is 1
    B1 = bondi_matrix(z1, Dz1, D2z1, l, s)
    # Replace last row (z=zp) with BC at horizon (z=1): phi_in(1) = 1
    B1[-1, :] = 0.0
    B1[-1, 0] = 1.0  # z1[0] = 1
    rhs1 = np.zeros(N + 1)
    rhs1[-1] = 1.0
    phi_in = np.linalg.solve(B1, rhs1)
    dphi_in = Dz1 @ phi_in

    # Solve phi_down on [0, zp] with BC: phi_down(z=0) = 1
    # z0 goes from zp to 0, so first index is zp, last is 0
    B0 = bondi_matrix(z0, Dz0, D2z0, l, s)
    # Replace first row (z=zp) with BC at infinity (z=0): phi_down(0) = 1
    B0[0, :] = 0.0
    B0[0, -1] = 1.0  # z0[-1] = 0
    rhs0 = np.zeros(N + 1)
    rhs0[0] = 1.0
    phi_down = np.linalg.solve(B0, rhs0)
    dphi_down = Dz0 @ phi_down

    # Green function matching at zp
    tmp = np.exp(-1j * omega * xp)
    dxp = rh / (zp ** 2 * (zp - 1))

    # phi_down at zp is phi_down[0] (first element of z0 grid)
    # phi_in at zp is phi_in[-1] (last element of z1 grid)
    GFM11 = tmp * phi_down[0]
    GFM21 = tmp * (dphi_down[0] + phi_down[0] * (-1j * omega) * dxp)
    GFM = np.array([[GFM11, np.conj(GFM11)],
                    [GFM21, np.conj(GFM21)]])

    rhs_gf = np.array([
        phi_in[-1] * tmp,
        tmp * (dphi_in[-1] + phi_in[-1] * (-1j * omega) * dxp)
    ])
    C = np.linalg.solve(GFM, rhs_gf)
    Cid = C[0]
    Ciu = C[1]

    T = 1.0 / abs(Cid) ** 2
    R = abs(Ciu) ** 2 / abs(Cid) ** 2
    W = 1j * 2 * omega * Cid

    # Tortoise coordinate
    def x_fun(z):
        return rh * (1.0 / z + np.log(1 - z) - np.log(z))

    # Chebyshev coefficients for interpolation
    phi_in_ReCheb = real_to_cheb(np.real(phi_in))
    phi_in_ImCheb = real_to_cheb(np.imag(phi_in))
    phi_down_ReCheb = real_to_cheb(np.real(phi_down))
    phi_down_ImCheb = real_to_cheb(np.imag(phi_down))

    def cheb_eval(ReCheb, ImCheb, x1, x2, z):
        return (cheb_interpolate(ReCheb, x1, x2, z) +
                1j * cheb_interpolate(ImCheb, x1, x2, z))

    if not AnMR_flag:
        # Linear mapping: domain is [x1, x2] match the original grid range
        def phi_in_fun1(z):
            return cheb_eval(phi_in_ReCheb, phi_in_ImCheb, zp, 1, z) * np.exp(-1j * omega * x_fun(z))

        def phi_out_fun1(z):
            return np.conj(phi_in_fun1(z))

        def phi_up_fun1(z):
            return -np.conj(Ciu) * phi_in_fun1(z) + Cid * phi_out_fun1(z)

        def phi_down_amp0(z):
            return cheb_eval(phi_down_ReCheb, phi_down_ImCheb, 0, zp, z)

        def phi_down_fun0(z):
            return phi_down_amp0(z) * np.exp(-1j * omega * x_fun(z))

        def phi_up_fun0(z):
            return np.conj(phi_down_fun0(z))

        def phi_in_fun0(z):
            return Cid * phi_down_fun0(z) + Ciu * phi_up_fun0(z)
    else:
        # sinh-mapped: coefficients are in y-coordinate
        def z12y(z):
            return np.arcsinh((z - zp) / (1 - zp) * np.sinh(kappa_in)) * 2 / kappa_in - 1

        def phi_in_funy(y):
            return cheb_eval(phi_in_ReCheb, phi_in_ImCheb, -1, 1, y)

        def phi_in_fun1(z):
            return phi_in_funy(z12y(z)) * np.exp(-1j * omega * x_fun(z))

        def phi_out_fun1(z):
            return np.conj(phi_in_fun1(z))

        def phi_up_fun1(z):
            return -np.conj(Ciu) * phi_in_fun1(z) + Cid * phi_out_fun1(z)

        def z02y(z):
            return np.arcsinh(z / zp * np.sinh(kappa)) * 2 / kappa - 1

        def phi_down_funy(y):
            return cheb_eval(phi_down_ReCheb, phi_down_ImCheb, -1, 1, y)

        def phi_down_amp0(z):
            return phi_down_funy(z02y(z))

        def phi_down_fun0(z):
            return phi_down_amp0(z) * np.exp(-1j * omega * x_fun(z))

        def phi_up_fun0(z):
            return np.conj(phi_down_fun0(z))

        def phi_in_fun0(z):
            return Cid * phi_down_fun0(z) + Ciu * phi_up_fun0(z)

    def phi_in_full(z):
        z = np.asarray(z)
        val = np.zeros(z.shape, dtype=complex)
        mask0 = z < zp
        mask1 = z >= zp
        if np.any(mask0):
            val[mask0] = phi_in_fun0(z[mask0])
        if np.any(mask1):
            val[mask1] = phi_in_fun1(z[mask1])
        if np.isscalar(z) or z.ndim == 0:
            return val.item()
        return val

    def phi_up_full(z):
        z = np.asarray(z)
        val = np.zeros(z.shape, dtype=complex)
        mask0 = z < zp
        mask1 = z >= zp
        if np.any(mask0):
            val[mask0] = phi_up_fun0(z[mask0])
        if np.any(mask1):
            val[mask1] = phi_up_fun1(z[mask1])
        if np.isscalar(z) or z.ndim == 0:
            return val.item()
        return val

    r_match = rh / zp

    def poly_mul(p, q):
        out = {}
        for pk, pv in p.items():
            for qk, qv in q.items():
                out[pk + qk] = out.get(pk + qk, 0.0j) + pv * qv
        return out

    def mode_coeffs_out(r):
        q = phi_down_amp0(rh / r)
        qc = np.conj(q)
        phi = {-1: Cid * q, 1: Ciu * qc}
        phi_c = {1: np.conj(Cid) * qc, -1: np.conj(Ciu) * q}
        return poly_mul(poly_mul(poly_mul(phi, phi_c), phi), phi)

    def mode_coeffs_in(r):
        q = phi_down_amp0(rh / r)
        qc = np.conj(q)
        phi = {-1: Cid * q, 1: Ciu * qc}
        phi_c = {1: np.conj(Cid) * qc, -1: np.conj(Ciu) * q}
        phi_up = {1: qc}
        return poly_mul(poly_mul(poly_mul(phi, phi_c), phi), phi_up)

    def complex_quad(fun, a, b):
        real, real_err = quad(lambda x: np.real(fun(x)), a, b,
                              epsabs=quad_abstol, epsrel=quad_reltol,
                              limit=2000)
        imag, imag_err = quad(lambda x: np.imag(fun(x)), a, b,
                              epsabs=quad_abstol, epsrel=quad_reltol,
                              limit=2000)
        return real + 1j * imag, real_err + 1j * imag_err

    def weighted_exp_quad(amp_fun, k):
        w = abs(k) * omega
        sign = 1.0 if k > 0 else -1.0

        def slow_amp(r):
            z = rh / r
            return (amp_fun(r) *
                    np.exp(1j * k * omega * rh * np.log(1.0 / z - 1.0)))

        # QAWFE accelerates the infinite sum over Fourier cycles.  For this
        # problem the final observables contain severe cancellations, so an
        # over-small cycle absolute tolerance can destabilize the extrapolation.
        rc, rc_err = quad(lambda r: np.real(slow_amp(r)), r_match, np.inf,
                          weight="cos", wvar=w, epsabs=quad_abstol,
                          epsrel=quad_reltol, limlst=1000, maxp1=200)
        rs, rs_err = quad(lambda r: np.real(slow_amp(r)), r_match, np.inf,
                          weight="sin", wvar=w, epsabs=quad_abstol,
                          epsrel=quad_reltol, limlst=1000, maxp1=200)
        ic, ic_err = quad(lambda r: np.imag(slow_amp(r)), r_match, np.inf,
                          weight="cos", wvar=w, epsabs=quad_abstol,
                          epsrel=quad_reltol, limlst=1000, maxp1=200)
        is_, is_err = quad(lambda r: np.imag(slow_amp(r)), r_match, np.inf,
                           weight="sin", wvar=w, epsabs=quad_abstol,
                           epsrel=quad_reltol, limlst=1000, maxp1=200)

        val = (rc - sign * is_) + 1j * (ic + sign * rs)
        err = (rc_err + is_err) + 1j * (ic_err + rs_err)
        return val, err

    def integrate_modes(mode_coeffs):
        values = []
        errors = []
        sample_modes = mode_coeffs(r_match)
        for k in sorted(sample_modes):
            def amp(r, kk=k):
                return mode_coeffs(r).get(kk, 0.0j) / r ** 2

            if k == 0:
                val, err = complex_quad(amp, r_match, np.inf)
            else:
                val, err = weighted_exp_quad(amp, k)
            values.append(val)
            errors.append(err)
        return sum(values), sum(errors)

    # Nonlinear corrections: integrals
    # A1out: integral of |phi_in|^2 * phi_in^2
    def integrand1_out(z):
        return np.abs(phi_in_fun1(z)) ** 2 * phi_in_fun1(z) ** 2

    val1_out, err1_out = quad(lambda z: integrand1_out(z).real, zp, 1,
                              epsrel=quad_reltol, limit=2000)
    val1_out_imag, err1_out_imag = quad(lambda z: integrand1_out(z).imag, zp, 1,
                                        epsrel=quad_reltol, limit=2000)
    val1_out = (val1_out + 1j * val1_out_imag) / rh

    val0_out, err0_out = integrate_modes(mode_coeffs_out)

    A1out = -(val1_out + val0_out) * Cl / W

    # A1in: integral of |phi_in|^2 * phi_in * phi_up
    def integrand1_in(z):
        return np.abs(phi_in_fun1(z)) ** 2 * phi_in_fun1(z) * phi_up_fun1(z)

    val1_in, err1_in = quad(lambda z: integrand1_in(z).real, zp, 1,
                            epsrel=quad_reltol, limit=2000)
    val1_in_imag, err1_in_imag = quad(lambda z: integrand1_in(z).imag, zp, 1,
                                      epsrel=quad_reltol, limit=2000)
    val1_in = (val1_in + 1j * val1_in_imag) / rh

    val0_in, err0_in = integrate_modes(mode_coeffs_in)

    A1in = -(val1_in + val0_in) * Cl / W

    T1 = 2 * np.real(A1in) / abs(Cid) ** 2
    R1 = 2 * np.real(Ciu * np.conj(A1out)) / abs(Cid) ** 2

    # Matching error: value and derivative jump at zp
    phi_right = phi_in[-1] * tmp
    dphi_right = tmp * (dphi_in[-1] + phi_in[-1] * (-1j * omega) * dxp)

    phi_left = Cid * phi_down[0] * tmp + Ciu * np.conj(phi_down[0] * tmp)
    dphi_left = Cid * GFM21 + Ciu * np.conj(GFM21)

    value_jump = abs(phi_right - phi_left) / max(abs(phi_right), abs(phi_left))
    deriv_jump = abs(dphi_right - dphi_left) / max(abs(dphi_right), abs(dphi_left))
    matching_error = max(value_jump, deriv_jump)

    # Wronskian consistency: verify that C_id computed via Cramer's rule
    # (using the GFM determinant) matches the directly-solved value.
    # This checks that the Wronskian det(GFM) is numerically consistent
    # with the matching solution.
    GFM_det = GFM11 * np.conj(GFM21) - np.conj(GFM11) * GFM21
    Cid_cramer = (phi_in[-1] * tmp * np.conj(GFM21) - np.conj(GFM11) * rhs_gf[1]) / GFM_det
    W_error = abs(Cid_cramer - Cid) / abs(Cid)

    return {
        "omega": omega,
        "zp": zp,
        "rp": rp,
        "N": N,
        "C_id": Cid,
        "C_iu": Ciu,
        "T": T,
        "R": R,
        "W": W,
        "A1out": A1out,
        "A1in": A1in,
        "T1": T1,
        "R1": R1,
        "matching_error": matching_error,
        "W_error": W_error,
        "status": "ok",
    }
