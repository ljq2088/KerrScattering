"""Run convergence checks for Kerr s=0 nonlinear target-channel amplitudes."""

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
from scripts.run_kerr_scalar_nonlinear_channels import parse_int_list
from src.kerr_scalar_nonlinear import compute_kerr_scalar_green_diagnostics
from src.teukolsky_scalar import scalar_cubic_coupling, scalar_cubic_coupling_cos2


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "kerr_scalar_nonlinear_channel_convergence.csv")


def parse_config_list(text):
    configs = []
    for item in text.split(","):
        if not item.strip():
            continue
        parts = item.split(":")
        if len(parts) != 2:
            raise argparse.ArgumentTypeError("configs must have form N:q,N:q")
        n, q = (int(part) for part in parts)
        configs.append((n, q))
    if not configs:
        raise argparse.ArgumentTypeError("at least one N:q config is required")
    return configs


def rel(a, b):
    return abs(a - b) / max(abs(b), 1e-300)


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--output", default=OUT)
    parser.add_argument("--case-label", default="kerr_a05_l2m2_super")
    parser.add_argument("--l-targets", type=parse_int_list, default=parse_int_list("2,4,6"))
    parser.add_argument(
        "--configs",
        type=parse_config_list,
        default=parse_config_list("224:224,256:224,288:224"),
    )
    parser.add_argument("--tail-epsrel", type=float, default=1e-11)
    parser.add_argument("--max-rss-mb", type=float, default=0.0)
    parser.add_argument("--coupling-zero-tol", type=float, default=1e-14)
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    case_map = {case["label"]: case for case in CASES}
    if args.case_label not in case_map:
        raise ValueError(f"Unknown case label: {args.case_label}")
    case = case_map[args.case_label]

    output = os.path.abspath(args.output)
    os.makedirs(os.path.dirname(output), exist_ok=True)
    initial_rss = require_memory_room(args.max_rss_mb, "initial")
    if initial_rss is not None:
        print(f"Initial RSS = {initial_rss:.1f} MB")

    rows = []
    by_target = {}
    for l_target in args.l_targets:
        c0 = scalar_cubic_coupling(
            case["l"], case["m"], case["a"], case["omega"], l_target=l_target
        )
        c2 = scalar_cubic_coupling_cos2(
            case["l"], case["m"], case["a"], case["omega"], l_target=l_target
        )
        effective_coupling = abs(c0) + case["a"] ** 2 * abs(c2)
        if effective_coupling < args.coupling_zero_tol:
            print(f"Skipping l_target={l_target}: angular coupling is zero")
            continue

        target_rows = []
        for n, q in args.configs:
            rss_before = require_memory_room(
                args.max_rss_mb, f"before {case['label']} l_target={l_target} N={n} q={q}"
            )
            start = time.perf_counter()
            print(f"Running {case['label']} l_target={l_target} N={n} q={q}")
            result = compute_kerr_scalar_green_diagnostics(
                case["l"],
                case["m"],
                case["omega"],
                a=case["a"],
                l_target=l_target,
                N_outer=n,
                N_inner=n,
                r_match=case.get("r_match"),
                quad_order=q,
                tail_epsrel=args.tail_epsrel,
                radial_weight_model="kerr-covariant-sigma-dr",
            )
            elapsed_s = time.perf_counter() - start
            rss_after = current_rss_mb()
            row = {
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
                "angular_coupling": fmt_complex(result.angular_coupling),
                "angular_coupling_cos2": fmt_complex(result.angular_coupling_cos2),
                "abs_angular_coupling": f"{abs(result.angular_coupling):.16e}",
                "abs_angular_coupling_cos2": f"{abs(result.angular_coupling_cos2):.16e}",
                "B_inc_source": fmt_complex(result.B_inc),
                "B_ref_source": fmt_complex(result.B_ref),
                "B_inc_target": fmt_complex(result.B_inc_target),
                "B_ref_target": fmt_complex(result.B_ref_target),
                "wronskian_relative_error": f"{result.wronskian_relative_error:.16e}",
                "A_ref_1": fmt_complex(result.A_ref_1),
                "A_hor_1": fmt_complex(result.A_hor_1),
                "abs_A_ref_1": f"{abs(result.A_ref_1):.16e}",
                "abs_A_hor_1": f"{abs(result.A_hor_1):.16e}",
                "abs_delta_A_ref_to_reference": "",
                "abs_delta_A_hor_to_reference": "",
                "rel_A_ref_to_reference": "",
                "rel_A_hor_to_reference": "",
                "elapsed_s": f"{elapsed_s:.6e}",
                "rss_mb_before": "" if rss_before is None else f"{rss_before:.6e}",
                "rss_mb_after": "" if rss_after is None else f"{rss_after:.6e}",
                "status": result.status,
                "_A_ref_complex": result.A_ref_1,
                "_A_hor_complex": result.A_hor_1,
            }
            target_rows.append(row)

        reference = max(
            target_rows,
            key=lambda row: (int(row["N_outer"]), int(row["quad_order"])),
        )
        by_target[l_target] = reference
        for row in target_rows:
            row["abs_delta_A_ref_to_reference"] = (
                f"{abs(row['_A_ref_complex'] - reference['_A_ref_complex']):.16e}"
            )
            row["abs_delta_A_hor_to_reference"] = (
                f"{abs(row['_A_hor_complex'] - reference['_A_hor_complex']):.16e}"
            )
            row["rel_A_ref_to_reference"] = (
                f"{rel(row['_A_ref_complex'], reference['_A_ref_complex']):.16e}"
            )
            row["rel_A_hor_to_reference"] = (
                f"{rel(row['_A_hor_complex'], reference['_A_hor_complex']):.16e}"
            )
            del row["_A_ref_complex"]
            del row["_A_hor_complex"]
            rows.append(row)

    fields = [
        "label", "l_source", "l_target", "m", "a", "omega", "N_outer",
        "N_inner", "r_match", "quad_order", "tail_epsrel",
        "angular_coupling", "angular_coupling_cos2", "abs_angular_coupling",
        "abs_angular_coupling_cos2", "B_inc_source", "B_ref_source",
        "B_inc_target", "B_ref_target", "wronskian_relative_error",
        "A_ref_1", "A_hor_1", "abs_A_ref_1", "abs_A_hor_1",
        "abs_delta_A_ref_to_reference", "abs_delta_A_hor_to_reference",
        "rel_A_ref_to_reference", "rel_A_hor_to_reference", "elapsed_s",
        "rss_mb_before", "rss_mb_after", "status",
    ]
    with open(output, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    print("Kerr scalar nonlinear l' channel convergence")
    for row in rows:
        print(
            f"  l'={row['l_target']} N={row['N_outer']} q={row['quad_order']}: "
            f"dref={row['rel_A_ref_to_reference']} "
            f"dhor={row['rel_A_hor_to_reference']}"
        )
    print(f"  saved = {output}")


if __name__ == "__main__":
    main()
