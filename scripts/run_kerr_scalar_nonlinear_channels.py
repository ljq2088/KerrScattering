"""Run Kerr s=0 weak nonlinear l' channel scan."""

import argparse
import csv
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.run_kerr_scalar_nonlinear_diagnostics import (
    CASES,
    current_rss_mb,
    fmt_complex,
    require_memory_room,
)
from src.kerr_scalar_nonlinear import compute_kerr_scalar_green_diagnostics
from src.teukolsky_scalar import scalar_cubic_coupling, scalar_cubic_coupling_cos2


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "kerr_scalar_nonlinear_channels.csv")


def parse_int_list(text):
    values = [int(item) for item in text.split(",") if item.strip()]
    if not values:
        raise argparse.ArgumentTypeError("at least one integer is required")
    return values


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--output", default=OUT)
    parser.add_argument("--case-label", default="kerr_a05_l2m2_super")
    parser.add_argument("--l-targets", type=parse_int_list, default=None)
    parser.add_argument("--N-outer", type=int, default=288)
    parser.add_argument("--N-inner", type=int, default=288)
    parser.add_argument("--quad-order", type=int, default=224)
    parser.add_argument("--tail-epsrel", type=float, default=1e-11)
    parser.add_argument("--max-rss-mb", type=float, default=0.0)
    parser.add_argument(
        "--coupling-zero-tol",
        type=float,
        default=1e-14,
        help="skip radial solve when |C0|+a^2|C2| is below this threshold",
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    case_map = {case["label"]: case for case in CASES}
    if args.case_label not in case_map:
        raise ValueError(f"Unknown case label: {args.case_label}")
    case = case_map[args.case_label]
    l_targets = args.l_targets
    if l_targets is None:
        l_targets = list(range(abs(case["m"]), case["l"] + 5))

    output = os.path.abspath(args.output)
    os.makedirs(os.path.dirname(output), exist_ok=True)
    initial_rss = require_memory_room(args.max_rss_mb, "initial")
    if initial_rss is not None:
        print(f"Initial RSS = {initial_rss:.1f} MB")

    rows = []
    for l_target in l_targets:
        rss_before = require_memory_room(
            args.max_rss_mb, f"before {case['label']} l_target={l_target}"
        )
        c0 = scalar_cubic_coupling(
            case["l"], case["m"], case["a"], case["omega"], l_target=l_target
        )
        c2 = scalar_cubic_coupling_cos2(
            case["l"], case["m"], case["a"], case["omega"], l_target=l_target
        )
        effective_coupling = abs(c0) + case["a"] ** 2 * abs(c2)
        if effective_coupling < args.coupling_zero_tol:
            rows.append({
                "label": case["label"],
                "l_source": case["l"],
                "l_target": l_target,
                "m": case["m"],
                "a": f"{case['a']:.16e}",
                "omega": f"{case['omega']:.16e}",
                "N_outer": args.N_outer,
                "N_inner": args.N_inner,
                "r_match": f"{case.get('r_match'):.16e}",
                "quad_order": args.quad_order,
                "tail_epsrel": f"{args.tail_epsrel:.16e}",
                "radial_integral_method": "skipped-zero-angular-coupling",
                "angular_coupling": fmt_complex(c0),
                "angular_coupling_cos2": fmt_complex(c2),
                "abs_angular_coupling": f"{abs(c0):.16e}",
                "abs_angular_coupling_cos2": f"{abs(c2):.16e}",
                "B_inc_source": "",
                "B_ref_source": "",
                "B_inc_target": "",
                "B_ref_target": "",
                "flux_normalization_condition_number": "",
                "wronskian_relative_error": "",
                "A_ref_1": fmt_complex(0.0 + 0.0j),
                "A_hor_1": fmt_complex(0.0 + 0.0j),
                "abs_A_ref_1": "0.0000000000000000e+00",
                "abs_A_hor_1": "0.0000000000000000e+00",
                "elapsed_s": "0.000000e+00",
                "rss_mb_before": "" if rss_before is None else f"{rss_before:.6e}",
                "rss_mb_after": "" if current_rss_mb() is None else f"{current_rss_mb():.6e}",
                "status": "skipped-zero-angular-coupling",
            })
            print(
                f"Skipping {case['label']} l_target={l_target}: "
                f"effective angular coupling {effective_coupling:.3e}"
            )
            continue
        start = time.perf_counter()
        print(
            f"Running {case['label']} l_target={l_target} "
            f"N={args.N_outer} q={args.quad_order}"
        )
        result = compute_kerr_scalar_green_diagnostics(
            case["l"],
            case["m"],
            case["omega"],
            a=case["a"],
            l_target=l_target,
            N_outer=args.N_outer,
            N_inner=args.N_inner,
            r_match=case.get("r_match"),
            quad_order=args.quad_order,
            tail_epsrel=args.tail_epsrel,
            radial_weight_model="kerr-covariant-sigma-dr",
        )
        elapsed_s = time.perf_counter() - start
        rss_after = current_rss_mb()
        rows.append({
            "label": case["label"],
            "l_source": case["l"],
            "l_target": result.l_target,
            "m": case["m"],
            "a": f"{case['a']:.16e}",
            "omega": f"{case['omega']:.16e}",
            "N_outer": result.N_outer,
            "N_inner": result.N_inner,
            "r_match": f"{result.r_match:.16e}",
            "quad_order": result.quad_order,
            "tail_epsrel": f"{result.tail_epsrel:.16e}",
            "radial_integral_method": result.radial_integral_method,
            "angular_coupling": fmt_complex(result.angular_coupling),
            "angular_coupling_cos2": fmt_complex(result.angular_coupling_cos2),
            "abs_angular_coupling": f"{abs(result.angular_coupling):.16e}",
            "abs_angular_coupling_cos2": f"{abs(result.angular_coupling_cos2):.16e}",
            "B_inc_source": fmt_complex(result.B_inc),
            "B_ref_source": fmt_complex(result.B_ref),
            "B_inc_target": fmt_complex(result.B_inc_target),
            "B_ref_target": fmt_complex(result.B_ref_target),
            "flux_normalization_condition_number": (
                f"{result.flux_normalization_condition_number:.16e}"
            ),
            "wronskian_relative_error": f"{result.wronskian_relative_error:.16e}",
            "A_ref_1": fmt_complex(result.A_ref_1),
            "A_hor_1": fmt_complex(result.A_hor_1),
            "abs_A_ref_1": f"{abs(result.A_ref_1):.16e}",
            "abs_A_hor_1": f"{abs(result.A_hor_1):.16e}",
            "elapsed_s": f"{elapsed_s:.6e}",
            "rss_mb_before": "" if rss_before is None else f"{rss_before:.6e}",
            "rss_mb_after": "" if rss_after is None else f"{rss_after:.6e}",
            "status": result.status,
        })

    fields = [
        "label", "l_source", "l_target", "m", "a", "omega", "N_outer",
        "N_inner", "r_match", "quad_order", "tail_epsrel",
        "radial_integral_method", "angular_coupling", "angular_coupling_cos2",
        "abs_angular_coupling", "abs_angular_coupling_cos2", "B_inc_source",
        "B_ref_source", "B_inc_target", "B_ref_target",
        "flux_normalization_condition_number",
        "wronskian_relative_error", "A_ref_1", "A_hor_1", "abs_A_ref_1",
        "abs_A_hor_1", "elapsed_s", "rss_mb_before", "rss_mb_after", "status",
    ]
    with open(output, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    print("Kerr scalar nonlinear l' channel scan")
    for row in rows:
        print(
            f"  l'={row['l_target']}: |C0|={row['abs_angular_coupling']} "
            f"|Aref|={row['abs_A_ref_1']} |Ahor|={row['abs_A_hor_1']} "
            f"Werr={row['wronskian_relative_error']}"
        )
    print(f"  saved = {output}")


if __name__ == "__main__":
    main()
