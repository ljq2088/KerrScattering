"""Run Kerr s=0 nonlinear Green-function radial diagnostics."""

import argparse
import csv
import ctypes
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.kerr_scalar_nonlinear import compute_kerr_scalar_green_diagnostics


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "kerr_scalar_nonlinear_diagnostics.csv")

CASES = [
    {"label": "schwarzschild_l0", "l": 0, "m": 0, "a": 0.0, "omega": 0.1,
     "r_match": 30.0},
    {"label": "kerr_a05_l2m2_sub", "l": 2, "m": 2, "a": 0.5, "omega": 0.24,
     "r_match": 40.0},
    {"label": "kerr_a05_l2m2_super", "l": 2, "m": 2, "a": 0.5, "omega": 0.3,
     "r_match": 40.0},
    {"label": "kerr_a09_l2m2_peak", "l": 2, "m": 2, "a": 0.9, "omega": 0.58,
     "r_match": 16.0},
]
QUAD_ORDERS = [64, 96, 128, 192]


class _WindowsProcessMemoryCounters(ctypes.Structure):
    _fields_ = [
        ("cb", ctypes.c_ulong),
        ("PageFaultCount", ctypes.c_ulong),
        ("PeakWorkingSetSize", ctypes.c_size_t),
        ("WorkingSetSize", ctypes.c_size_t),
        ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
        ("QuotaPagedPoolUsage", ctypes.c_size_t),
        ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
        ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
        ("PagefileUsage", ctypes.c_size_t),
        ("PeakPagefileUsage", ctypes.c_size_t),
    ]


def current_rss_mb():
    """Return the process resident set size in MB when available."""
    if os.name == "nt":
        counters = _WindowsProcessMemoryCounters()
        counters.cb = ctypes.sizeof(counters)
        psapi = ctypes.WinDLL("psapi.dll", use_last_error=True)
        kernel32 = ctypes.WinDLL("kernel32.dll", use_last_error=True)
        get_current_process = kernel32.GetCurrentProcess
        get_current_process.restype = ctypes.c_void_p
        get_process_memory_info = psapi.GetProcessMemoryInfo
        get_process_memory_info.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(_WindowsProcessMemoryCounters),
            ctypes.c_ulong,
        ]
        get_process_memory_info.restype = ctypes.c_int
        ok = get_process_memory_info(
            get_current_process(), ctypes.byref(counters), counters.cb
        )
        if ok:
            return counters.WorkingSetSize / (1024.0 ** 2)
        return None

    try:
        import resource
    except ImportError:
        return None

    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    if sys.platform == "darwin":
        return rss / (1024.0 ** 2)
    return rss / 1024.0


def require_memory_room(max_rss_mb, context):
    rss = current_rss_mb()
    if max_rss_mb > 0.0 and rss is not None and rss > max_rss_mb:
        raise MemoryError(
            f"{context}: RSS {rss:.1f} MB exceeds limit {max_rss_mb:.1f} MB"
        )
    return rss


def parse_quad_orders(text):
    orders = [int(item) for item in text.split(",") if item.strip()]
    if not orders:
        raise argparse.ArgumentTypeError("at least one quadrature order is required")
    if min(orders) < 16:
        raise argparse.ArgumentTypeError("quadrature orders must be >= 16")
    return orders


def fmt_complex(z):
    return f"{z.real:.16e}{z.imag:+.16e}j"


def rel(a, b):
    return abs(a - b) / max(abs(b), 1e-300)


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--output", default=OUT)
    parser.add_argument("--quad-orders", type=parse_quad_orders,
                        default=QUAD_ORDERS)
    parser.add_argument("--case-label", action="append", default=[],
                        help="case label to run; may be repeated")
    parser.add_argument("--N-outer", type=int, default=256)
    parser.add_argument("--N-inner", type=int, default=256)
    parser.add_argument(
        "--radial-weight-model",
        choices=["kerr-covariant-sigma-dr", "legacy-bondi-dr-over-r2"],
        default="kerr-covariant-sigma-dr",
        help="radial source measure/model to use",
    )
    parser.add_argument(
        "--max-rss-mb",
        type=float,
        default=0.0,
        help="abort before/after each row if process RSS exceeds this limit; 0 disables",
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    output = os.path.abspath(args.output)
    cases = CASES
    if args.case_label:
        labels = set(args.case_label)
        cases = [case for case in CASES if case["label"] in labels]
        missing = labels - {case["label"] for case in cases}
        if missing:
            raise ValueError(f"Unknown case label(s): {', '.join(sorted(missing))}")

    os.makedirs(os.path.dirname(output), exist_ok=True)
    rows = []
    initial_rss = require_memory_room(args.max_rss_mb, "initial")
    if initial_rss is None:
        print("RSS monitor unavailable on this platform; memory cap is inactive.")
    else:
        print(f"Initial RSS = {initial_rss:.1f} MB")

    for case in cases:
        previous = None
        for quad_order in args.quad_orders:
            rss_before = require_memory_room(
                args.max_rss_mb, f"before {case['label']} q={quad_order}"
            )
            start = time.perf_counter()
            print(
                f"Running {case['label']} q={quad_order} "
                f"r_match={case.get('r_match', 'auto')} "
                f"RSS={rss_before:.1f} MB"
                if rss_before is not None
                else (
                    f"Running {case['label']} q={quad_order} "
                    f"r_match={case.get('r_match', 'auto')}"
                )
            )
            result = compute_kerr_scalar_green_diagnostics(
                case["l"],
                case["m"],
                case["omega"],
                a=case["a"],
                N_outer=args.N_outer,
                N_inner=args.N_inner,
                r_match=case.get("r_match"),
                quad_order=quad_order,
                radial_weight_model=args.radial_weight_model,
            )
            elapsed_s = time.perf_counter() - start
            rss_after = require_memory_room(
                args.max_rss_mb, f"after {case['label']} q={quad_order}"
            )
            if previous is None:
                rel_A_ref = float("inf")
                rel_A_hor = float("inf")
            else:
                rel_A_ref = rel(result.A_ref_1, previous.A_ref_1)
                rel_A_hor = rel(result.A_hor_1, previous.A_hor_1)
            rows.append({
                "label": case["label"],
                "l": case["l"],
                "m": case["m"],
                "a": f"{case['a']:.16e}",
                "omega": f"{case['omega']:.16e}",
                "quad_order": quad_order,
                "N_outer": result.N_outer,
                "N_inner": result.N_inner,
                "r_match": f"{result.r_match:.16e}",
                "mapping": result.mapping,
                "radial_weight_model": result.radial_weight_model,
                "radial_integral_method": result.radial_integral_method,
                "angular_coupling": fmt_complex(result.angular_coupling),
                "angular_coupling_cos2": fmt_complex(result.angular_coupling_cos2),
                "wronskian": fmt_complex(result.wronskian),
                "wronskian_relative_error": f"{result.wronskian_relative_error:.16e}",
                "source_projection_ref": fmt_complex(result.source_projection_ref),
                "source_projection_hor": fmt_complex(result.source_projection_hor),
                "A_ref_1": fmt_complex(result.A_ref_1),
                "A_hor_1": fmt_complex(result.A_hor_1),
                "rel_A_ref_from_previous": f"{rel_A_ref:.16e}",
                "rel_A_hor_from_previous": f"{rel_A_hor:.16e}",
                "elapsed_s": f"{elapsed_s:.6e}",
                "rss_mb_before": "" if rss_before is None else f"{rss_before:.6e}",
                "rss_mb_after": "" if rss_after is None else f"{rss_after:.6e}",
                "status": result.status,
            })
            previous = result

    fields = [
        "label", "l", "m", "a", "omega", "quad_order", "N_outer",
        "N_inner", "r_match", "mapping", "radial_weight_model",
        "radial_integral_method", "angular_coupling", "angular_coupling_cos2",
        "wronskian", "wronskian_relative_error",
        "source_projection_ref", "source_projection_hor", "A_ref_1", "A_hor_1",
        "rel_A_ref_from_previous", "rel_A_hor_from_previous", "elapsed_s",
        "rss_mb_before", "rss_mb_after", "status",
    ]
    with open(output, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    print("Kerr scalar nonlinear radial diagnostics")
    for row in rows:
        print(
            f"  {row['label']} q={row['quad_order']}: "
            f"Werr={row['wronskian_relative_error']} "
            f"dAref={row['rel_A_ref_from_previous']} "
            f"dAhor={row['rel_A_hor_from_previous']} "
            f"rss={row['rss_mb_after'] or 'NA'} MB "
            f"elapsed={row['elapsed_s']} s"
        )
    print(f"  saved = {output}")


if __name__ == "__main__":
    main()
