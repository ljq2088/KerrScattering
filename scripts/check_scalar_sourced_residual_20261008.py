"""Differentiate a reconstructed Green field, not an algebraic ODE identity.

The finite interior interval excludes both asymptotic ends. This is a local
inhomogeneous residual test, not a global boundary/quadrature error estimate.
"""
import csv
import os
from pathlib import Path
import sys

for name in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[name] = "1"
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import numpy as np
from numpy.polynomial.chebyshev import chebval, chebder
from src.kerr_scalar_spectral import _cheb_interval
from src.kerr_scalar_nonlinear import compute_kerr_scalar_green_diagnostics, _solve_matched_mode
from src.teukolsky_scalar import KerrParams, delta
from scripts.run_kerr_scalar_spectral_quality import _cheb_coeff
from scripts.run_kerr_scalar_nonlinear_diagnostics import require_memory_room
from scripts.run_kerr_scalar_near_extremal_scaling import surface_gravity


def run_case(a, l, m, omega, n):
    params = KerrParams(M=1.0, a=a)
    result = compute_kerr_scalar_green_diagnostics(
        l, m, omega, a=a, N_outer=224, N_inner=224, r_match=12.0,
        quad_order=1024, tail_epsrel=1e-11, linear_solver="equilibrated",
        nonlinearity_order=n,
    )
    mode = _solve_matched_mode(l, m, omega, params, result.radial_lambda,
                              params.rp/12.0, 224, 224, "linear", 0.0, 0.0,
                              "equilibrated")

    def fields(r):
        rin = mode["inner_eval"].R(params.rp / np.asarray(r))
        rup = (-np.conj(mode["B_ref"])*rin + mode["B_inc"]*np.conj(rin)) / mode["flux_norm"]
        source = (np.asarray(r)**2*result.angular_coupling
                  + a*a*result.angular_coupling_cos2)*abs(rin)**(2*n)*rin
        return rin, rup, source

    # Initial cumulative integrals from the actual horizon to r=3, using
    # open quadrature; global infinite-tail information is in the total integral.
    gx, gw = np.polynomial.legendre.leggauss(1024)
    za = params.rp / 3.0
    z = (1-za)*gx/2 + (1+za)/2
    r = params.rp / z
    weights = (1-za)*gw/2 * params.rp/z**2
    rin, rup, source = fields(r)
    Iin_a = np.sum(weights*rin*source)
    Iup_a = np.sum(weights*rup*source)
    lx, lw = np.polynomial.legendre.leggauss(128)
    rows = []
    for degree in (16, 24, 32, 48, 64):
        require_memory_room(900, "sourced residual reconstruction")
        nodes, _, _ = _cheb_interval(degree, 3.0, 8.0)
        vals = []
        for rnode in nodes:
            rquad = (rnode-3)*lx/2 + (rnode+3)/2
            rin_q, rup_q, source_q = fields(rquad)
            Iin = Iin_a + (rnode-3)/2*np.sum(lw*rin_q*source_q)
            Iup = result.source_projection_hor - Iup_a - (rnode-3)/2*np.sum(lw*rup_q*source_q)
            rin_n, rup_n, _ = fields(rnode)
            vals.append(-(rup_n*Iin + rin_n*Iup)/result.wronskian)
        coeff = _cheb_coeff(np.asarray(vals))
        y = np.cos(np.pi*(np.arange(600)+0.5)/600)
        rv = 5.5 - 2.5*y
        R1 = chebval(y, coeff)
        R1r = -chebval(y, chebder(coeff))/2.5
        R1rr = chebval(y, chebder(coeff, 2))/2.5**2
        d = delta(rv, M=1.0, a=a)
        K = (rv*rv+a*a)*omega-a*m
        terms = (d*R1rr, (2*rv-2)*R1r,
                 (K*K/d-result.radial_lambda)*R1, fields(rv)[2])
        residual = abs(sum(terms))
        scale = sum(abs(term) for term in terms)
        row = dict(a=a, l=l, m=m, omega=omega, n=n, N_homogeneous=224,
                   quad_order=1024, N_reconstruction=degree, r_left=3.0,
                   r_right=8.0, samples=600,
                   relative_residual_max=float(np.max(residual/np.maximum(scale, 1e-300))),
                   relative_residual_median=float(np.median(residual/np.maximum(scale, 1e-300))),
                   coeff_tail=float(np.max(abs(coeff[-8:]))/np.max(abs(coeff))),
                   rss_mb=require_memory_room(900, "after sourced residual"))
        print(row, flush=True)
        rows.append(row)
    by_degree = {row["N_reconstruction"]: row for row in rows}
    assert by_degree[32]["relative_residual_max"] < 1e-7
    assert by_degree[16]["relative_residual_max"] > 1000*by_degree[32]["relative_residual_max"]
    return rows


def main():
    rows = []
    params = KerrParams(M=1.0, a=0.99)
    for case in [(0.5, 0, 0, 0.1, 1), (0.5, 0, 0, 0.1, 2),
                 (0.99, 2, 2, 2*params.omega_h + 0.5*surface_gravity(params), 1)]:
        rows.extend(run_case(*case))
    output = ROOT / "results/kerr_scalar_sourced_local_residual_20261008.csv"
    with output.open("w", newline="", encoding="utf8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
