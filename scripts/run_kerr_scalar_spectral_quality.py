"""Self-convergence and residual diagnostics for the Kerr s=0 spectral method."""

import argparse
import csv
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.run_kerr_scalar_nonlinear_diagnostics import CASES, fmt_complex
from src.cheb import real_to_cheb
from src.kerr_scalar_nonlinear import compute_kerr_scalar_green_diagnostics
from src.kerr_scalar_spectral import (
    _cheb_interval,
    _default_r_match,
    _phase_log_derivatives,
    _solve_branch,
    _transformed_coefficients,
)
from src.teukolsky_scalar import KerrParams, delta, teukolsky_lambda_s0


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COEFF_OUT = os.path.join(ROOT, "results", "kerr_scalar_spectral_coefficients.csv")
RESIDUAL_OUT = os.path.join(ROOT, "results", "kerr_scalar_spectral_residuals.csv")
SUMMARY_OUT = os.path.join(ROOT, "results", "kerr_scalar_spectral_quality_summary.csv")
FLUX_OUT = os.path.join(ROOT, "results", "kerr_scalar_nonlinear_flux_convergence.csv")


def _cheb_coeff(values):
    return real_to_cheb(np.real(values)) + 1j * real_to_cheb(np.imag(values))


def _mapping_y_to_z(y, z_left, z_right, mapping, kappa):
    length = z_right - z_left
    if mapping == "linear" or kappa <= 0.0:
        z = z_left + 0.5 * length * (1.0 - y)
        z_y = np.full_like(y, -0.5 * length)
        z_yy = np.zeros_like(y)
        return z, z_y, z_yy

    arg = 0.5 * kappa * (1.0 - y)
    sinh_k = np.sinh(kappa)
    z = z_left + length * np.sinh(arg) / sinh_k
    z_y = -0.5 * length * kappa * np.cosh(arg) / sinh_k
    z_yy = 0.25 * length * kappa**2 * np.sinh(arg) / sinh_k
    return z, z_y, z_yy


def _collocation_residuals(data, N, z_left, z_right, branch, boundary,
                           params, mapping, kappa, l, m, omega, lam):
    z, Dz, D2z = _cheb_interval(N, z_left, z_right, mapping=mapping, kappa=kappa)
    B2, B1, B0 = _transformed_coefficients(z, branch, params, l, m, omega, lam)
    u = data["u"]
    u_z = Dz @ u
    u_zz = D2z @ u
    residual = B2 * u_zz + B1 * u_z + B0 * u
    term_scale = np.maximum(
        np.abs(B2 * u_zz) + np.abs(B1 * u_z) + np.abs(B0 * u),
        1e-300,
    )
    rel = np.abs(residual) / term_scale

    radial_residual = np.full(N + 1, np.nan, dtype=float)
    radial_rel = np.full(N + 1, np.nan, dtype=float)
    radial_scale = np.full(N + 1, np.nan, dtype=float)
    interior = (z > 0.0) & (z < 1.0)
    if np.any(interior):
        zi = z[interior]
        r = params.rp / zi
        d = delta(r, M=params.M, a=params.a)
        dp = 2.0 * r - 2.0 * params.M
        K = (r**2 + params.a**2) * omega - params.a * m
        potential = K**2 / d - lam
        z_r = -zi**2 / params.rp
        z_rr = 2.0 * zi**3 / params.rp**2
        q, qp = _phase_log_derivatives(r, branch, params, omega, m)
        ui = u[interior]
        uzi = u_z[interior]
        uzzi = u_zz[interior]

        R = ui
        R_r_over_phase = q * ui + uzi * z_r
        R_rr_over_phase = (
            (qp + q**2) * ui
            + 2.0 * q * uzi * z_r
            + uzzi * z_r**2
            + uzi * z_rr
        )
        term2 = d * R_rr_over_phase
        term1 = dp * R_r_over_phase
        term0 = potential * R
        raw_radial = term2 + term1 + term0
        raw_scale = np.maximum(np.abs(term2) + np.abs(term1) + np.abs(term0), 1e-300)
        radial_residual[interior] = np.abs(raw_radial)
        radial_scale[interior] = raw_scale
        radial_rel[interior] = np.abs(raw_radial) / raw_scale

    keep = np.ones(N + 1, dtype=bool)
    if boundary == "left":
        keep[1] = False
    elif boundary == "right":
        keep[-2] = False
    else:
        raise ValueError("boundary must be left or right")
    return (
        z[keep],
        residual[keep],
        rel[keep],
        term_scale[keep],
        radial_residual[keep],
        radial_rel[keep],
        radial_scale[keep],
        np.nonzero(keep)[0],
    )


def _active_mapping(omega, M, mapping):
    if mapping == "auto":
        use_sinh = abs(omega) * M < 0.1
    elif mapping == "linear":
        use_sinh = False
    elif mapping == "sinh":
        use_sinh = True
    else:
        raise ValueError("mapping must be auto, linear, or sinh")

    if use_sinh:
        kappa_outer = abs(np.log(max(abs(omega) * 2.0 * M, 1e-300)))
        return "sinh-left", kappa_outer, 0.5 * kappa_outer
    return "linear", 0.0, 0.0


def run_spectral_quality(args):
    params = KerrParams(M=args.M, a=args.a)
    r_match = args.r_match or _default_r_match(args.M, args.a, args.omega)
    z_match = params.rp / r_match
    active_mapping, kappa_outer, kappa_inner = _active_mapping(args.omega, args.M, args.mapping)
    lam = teukolsky_lambda_s0(args.l, args.m, args.a, args.omega)

    branch_configs = [
        ("down", "outer", 0.0, z_match, "left", args.N_outer, kappa_outer),
        ("up", "outer", 0.0, z_match, "left", args.N_outer, kappa_outer),
        ("in", "inner", z_match, 1.0, "right", args.N_inner, kappa_inner),
    ]

    coeff_rows = []
    residual_rows = []
    summary_rows = []
    for branch, subdomain, z_left, z_right, boundary, N, kappa in branch_configs:
        data = _solve_branch(
            N,
            z_left,
            z_right,
            branch,
            boundary,
            params,
            active_mapping,
            kappa,
            args.l,
            args.m,
            args.omega,
            lam,
        )
        coeff = _cheb_coeff(data["u"])
        max_coeff = max(float(np.max(np.abs(coeff))), 1e-300)
        tail = coeff[-args.tail_terms:]
        tail_ratio = float(np.max(np.abs(tail)) / max_coeff)

        for k, value in enumerate(coeff):
            coeff_rows.append({
                "branch": branch,
                "subdomain": subdomain,
                "k": k,
                "abs_coeff": f"{abs(value):.16e}",
                "normalized_abs_coeff": f"{abs(value) / max_coeff:.16e}",
                "real_coeff": f"{value.real:.16e}",
                "imag_coeff": f"{value.imag:.16e}",
            })

        (
            z,
            residual,
            rel,
            term_scale,
            radial_residual,
            radial_rel,
            radial_scale,
            residual_index,
        ) = _collocation_residuals(
            data,
            N,
            z_left,
            z_right,
            branch,
            boundary,
            params,
            active_mapping,
            kappa,
            args.l,
            args.m,
            args.omega,
            lam,
        )
        radial_rel_finite = radial_rel[np.isfinite(radial_rel)]
        radial_res_finite = radial_residual[np.isfinite(radial_residual)]
        for idx, zi, ri, rrel, scale, rri, rrrel, rrscale in zip(
            residual_index,
            z,
            residual,
            rel,
            term_scale,
            radial_residual,
            radial_rel,
            radial_scale,
        ):
            residual_rows.append({
                "branch": branch,
                "subdomain": subdomain,
                "node_index": int(idx),
                "z": f"{zi:.16e}",
                "abs_residual": f"{abs(ri):.16e}",
                "relative_residual": f"{rrel:.16e}",
                "term_scale": f"{scale:.16e}",
                "radial_abs_residual": "" if not np.isfinite(rri) else f"{rri:.16e}",
                "radial_relative_residual": "" if not np.isfinite(rrrel) else f"{rrrel:.16e}",
                "radial_term_scale": "" if not np.isfinite(rrscale) else f"{rrscale:.16e}",
                "real_residual": f"{ri.real:.16e}",
                "imag_residual": f"{ri.imag:.16e}",
            })
        summary_rows.append({
            "case": args.label,
            "l": args.l,
            "m": args.m,
            "a": f"{args.a:.16e}",
            "omega": f"{args.omega:.16e}",
            "N": N,
            "branch": branch,
            "subdomain": subdomain,
            "mapping": "sinh" if active_mapping == "sinh-left" else "linear",
            "r_match": f"{r_match:.16e}",
            "tail_terms": args.tail_terms,
            "coeff_tail_ratio": f"{tail_ratio:.16e}",
            "max_abs_residual": f"{float(np.max(np.abs(residual))):.16e}",
            "max_relative_residual": f"{float(np.max(rel)):.16e}",
            "p95_relative_residual": f"{float(np.quantile(rel, 0.95)):.16e}",
            "median_relative_residual": f"{float(np.median(rel)):.16e}",
            "max_radial_abs_residual": (
                "" if radial_res_finite.size == 0
                else f"{float(np.max(radial_res_finite)):.16e}"
            ),
            "max_radial_relative_residual": (
                "" if radial_rel_finite.size == 0
                else f"{float(np.max(radial_rel_finite)):.16e}"
            ),
            "condition": f"{float(data['condition']):.16e}",
        })

    return coeff_rows, residual_rows, summary_rows


def _fixed_incident_flux_row(case, N, quad_order, tail_epsrel):
    result = compute_kerr_scalar_green_diagnostics(
        case["l"],
        case["m"],
        case["omega"],
        M=case.get("M", 1.0),
        a=case["a"],
        N_outer=N,
        N_inner=N,
        r_match=case.get("r_match"),
        quad_order=quad_order,
        tail_epsrel=tail_epsrel,
        radial_weight_model="kerr-covariant-sigma-dr",
    )
    horizon_factor = result.p_horizon * (result.r_plus**2 + result.a**2) / result.omega
    bnorm4 = abs(result.B_inc) ** 4
    T0 = horizon_factor / abs(result.B_inc) ** 2
    R0 = abs(result.B_ref / result.B_inc) ** 2
    T1 = 2.0 * horizon_factor * float(np.real(result.A_hor_1)) / bnorm4
    R1 = 2.0 * float(np.real(np.conj(result.B_ref) * result.A_ref_1)) / bnorm4
    return {
        "label": case["label"],
        "l": case["l"],
        "m": case["m"],
        "a": f"{case['a']:.16e}",
        "omega": f"{case['omega']:.16e}",
        "N": int(N),
        "quad_order": int(quad_order),
        "tail_epsrel": f"{tail_epsrel:.16e}",
        "B_inc": fmt_complex(result.B_inc),
        "B_ref": fmt_complex(result.B_ref),
        "A_ref_1": fmt_complex(result.A_ref_1),
        "A_hor_1": fmt_complex(result.A_hor_1),
        "T0": f"{T0:.16e}",
        "R0": f"{R0:.16e}",
        "linear_balance": f"{T0 + R0:.16e}",
        "T1": f"{T1:.16e}",
        "R1": f"{R1:.16e}",
        "nonlinear_balance": f"{T1 + R1:.16e}",
        "wronskian_relative_error": f"{result.wronskian_relative_error:.16e}",
        "_T1": T1,
        "_R1": R1,
    }


def run_flux_convergence(args):
    case_map = {case["label"]: case for case in CASES}
    rows = []
    for label in args.flux_cases:
        if label not in case_map:
            raise ValueError(f"Unknown nonlinear case label: {label}")
        case = case_map[label]
        print(f"Flux convergence for {label}")
        case_rows = []
        for N in args.flux_orders:
            print(f"  N={N}, q={args.quad_order}")
            row = _fixed_incident_flux_row(case, N, args.quad_order, args.tail_epsrel)
            case_rows.append(row)
        reference = max(case_rows, key=lambda row: int(row["N"]))
        for row in case_rows:
            row["rel_T1_to_reference"] = (
                f"{abs(row['_T1'] - reference['_T1']) / max(abs(reference['_T1']), 1e-300):.16e}"
            )
            row["rel_R1_to_reference"] = (
                f"{abs(row['_R1'] - reference['_R1']) / max(abs(reference['_R1']), 1e-300):.16e}"
            )
            del row["_T1"]
            del row["_R1"]
            rows.append(row)
    return rows


def _write_csv(path, rows, fields):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--label", default="kerr_a05_l2m2_super")
    parser.add_argument("--l", type=int, default=2)
    parser.add_argument("--m", type=int, default=2)
    parser.add_argument("--a", type=float, default=0.5)
    parser.add_argument("--omega", type=float, default=0.30)
    parser.add_argument("--M", type=float, default=1.0)
    parser.add_argument("--N-outer", type=int, default=288)
    parser.add_argument("--N-inner", type=int, default=288)
    parser.add_argument("--r-match", type=float, default=40.0)
    parser.add_argument("--mapping", choices=["auto", "linear", "sinh"], default="auto")
    parser.add_argument("--tail-terms", type=int, default=16)
    parser.add_argument("--residual-samples", type=int, default=600)
    parser.add_argument("--quad-order", type=int, default=224)
    parser.add_argument("--tail-epsrel", type=float, default=1e-11)
    parser.add_argument(
        "--flux-orders",
        type=lambda text: [int(item) for item in text.split(",") if item],
        default=[192, 224, 256, 288],
    )
    parser.add_argument(
        "--flux-cases",
        type=lambda text: [item.strip() for item in text.split(",") if item.strip()],
        default=["kerr_a05_l2m2_sub", "kerr_a05_l2m2_super", "kerr_a09_l2m2_peak"],
    )
    parser.add_argument("--coeff-output", default=COEFF_OUT)
    parser.add_argument("--residual-output", default=RESIDUAL_OUT)
    parser.add_argument("--summary-output", default=SUMMARY_OUT)
    parser.add_argument("--flux-output", default=FLUX_OUT)
    parser.add_argument("--skip-flux-convergence", action="store_true")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    coeff_rows, residual_rows, summary_rows = run_spectral_quality(args)
    _write_csv(
        args.coeff_output,
        coeff_rows,
        ["branch", "subdomain", "k", "abs_coeff", "normalized_abs_coeff",
         "real_coeff", "imag_coeff"],
    )
    _write_csv(
        args.residual_output,
        residual_rows,
        ["branch", "subdomain", "node_index", "z", "abs_residual",
         "relative_residual", "term_scale", "radial_abs_residual",
         "radial_relative_residual", "radial_term_scale",
         "real_residual", "imag_residual"],
    )
    _write_csv(
        args.summary_output,
        summary_rows,
        ["case", "l", "m", "a", "omega", "N", "branch", "subdomain",
         "mapping", "r_match", "tail_terms", "coeff_tail_ratio",
         "max_abs_residual", "max_relative_residual",
         "p95_relative_residual", "median_relative_residual",
         "max_radial_abs_residual", "max_radial_relative_residual",
         "condition"],
    )
    print(f"Saved spectral coefficients: {args.coeff_output}")
    print(f"Saved spectral residuals: {args.residual_output}")
    print(f"Saved spectral summary: {args.summary_output}")
    for row in summary_rows:
        print(
            f"  {row['branch']:>4s} {row['subdomain']}: "
            f"tail={row['coeff_tail_ratio']} "
            f"max_rel_res={row['max_relative_residual']}"
        )

    if not args.skip_flux_convergence:
        flux_rows = run_flux_convergence(args)
        _write_csv(
            args.flux_output,
            flux_rows,
            ["label", "l", "m", "a", "omega", "N", "quad_order", "tail_epsrel",
             "B_inc", "B_ref", "A_ref_1", "A_hor_1", "T0", "R0",
             "linear_balance", "T1", "R1", "nonlinear_balance",
             "wronskian_relative_error", "rel_T1_to_reference",
             "rel_R1_to_reference"],
        )
        print(f"Saved nonlinear flux convergence: {args.flux_output}")


if __name__ == "__main__":
    main()
