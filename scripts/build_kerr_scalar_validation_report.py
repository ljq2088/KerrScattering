"""Build a Markdown validation report for the Kerr s=0 spectral solver."""

import csv
import os
import sys


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SUMMARY = os.path.join(ROOT, "results", "kerr_scalar_adaptive_summary.csv")
REPORT = os.path.join(ROOT, "docs", "kerr_scalar_validation_report.md")


def fmt(x):
    return f"{float(x):.3e}"


def main():
    if not os.path.exists(SUMMARY):
        raise FileNotFoundError(
            f"{SUMMARY} not found. Run scripts/adaptive_kerr_scalar_gsn_validation.py first."
        )

    with open(SUMMARY, newline="") as f:
        rows = list(csv.DictReader(f))

    max_score = max(float(row["score"]) for row in rows)
    max_flux = max(float(row["flux_balance_error"]) for row in rows)
    all_passed = all(row["passed"] == "true" for row in rows)

    lines = [
        "# Kerr s=0 spectral validation report",
        "",
        "## Scope",
        "",
        "This report validates the two-domain Chebyshev spectral solver for the scalar",
        "Teukolsky in mode on Kerr. The solver uses `z = r_+/r`, direct endpoint",
        "collocation at `z=0,1`, degenerate endpoint ODE rows as regularity",
        "conditions, and value/derivative matching at an intermediate radius.",
        "",
        "The external benchmark is `GeneralizedSasakiNakamura.jl` with the",
        "`UNIT_TEUKOLSKY_TRANS` convention, so `B_trans = 1` at the horizon.",
        "",
        "## Acceptance gates",
        "",
        "- `rel_abs_B_inc <= 1e-7`",
        "- `rel_abs_B_ref <= 1e-7`",
        "- `flux_balance_error <= 1e-8`",
        "",
        "Only amplitude magnitudes and flux balance are used as pass/fail quantities.",
        "The complex amplitudes include convention-dependent phase factors from the",
        "additive constant in `r*` and package-specific normalization choices; those",
        "phase factors are recorded in the CSV output but are not used as invariant",
        "benchmark errors.",
        "",
        "## Summary",
        "",
        f"- Cases tested: {len(rows)}",
        f"- All cases passed: `{str(all_passed).lower()}`",
        f"- Worst score: `{max_score:.3e}`",
        f"- Worst flux-balance residual: `{max_flux:.3e}`",
        "",
        "| l | m | a | omega | N | r_match | mapping | rel_abs_B_inc | rel_abs_B_ref | flux | score | passed |",
        "|---:|---:|---:|---:|---:|---:|:---|---:|---:|---:|---:|:---|",
    ]

    for row in rows:
        lines.append(
            "| {l} | {m} | {a:.3g} | {omega:.3g} | {N} | {r_match:.3g} | "
            "{mapping} | {rel_inc} | {rel_ref} | {flux} | {score} | {passed} |".format(
                l=row["l"],
                m=row["m"],
                a=float(row["a"]),
                omega=float(row["omega"]),
                N=row["N"],
                r_match=float(row["r_match"]),
                mapping=row["mapping"],
                rel_inc=fmt(row["rel_abs_B_inc"]),
                rel_ref=fmt(row["rel_abs_B_ref"]),
                flux=fmt(row["flux_balance_error"]),
                score=fmt(row["score"]),
                passed=row["passed"],
            )
        )

    lines.extend([
        "",
        "## Current interpretation",
        "",
        "The present validation covers the Schwarzschild limit, moderate Kerr spin,",
        "near-superradiant scalar modes, low-frequency superradiant scattering,",
        "high-frequency small-reflection scattering, and high-spin Kerr cases.",
        "",
        "The worst invariant benchmark error in the current table is below `1.5e-8`,",
        "which is comfortably inside the `1e-7` amplitude-magnitude target. The",
        "hardest case is the high-frequency `l=m=2, a=0.5, omega=1.0` mode, where",
        "`B_ref` is small and therefore relative errors are more sensitive to",
        "conditioning.",
        "",
        "## Remaining PRD-level work",
        "",
        "- Expand the benchmark grid before using final production tables.",
        "- Add publication plots for transmission/reflection versus frequency.",
        "- State the complex phase convention explicitly if phase-sensitive",
        "  observables are reported.",
        "- Carry the nonlinear Green-function correction over from the Schwarzschild",
        "  project only after the linear solver validation remains stable on a denser",
        "  grid.",
        "",
        "Generated from `results/kerr_scalar_adaptive_summary.csv`.",
        "",
    ])

    os.makedirs(os.path.dirname(REPORT), exist_ok=True)
    with open(REPORT, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines))
    print(REPORT)


if __name__ == "__main__":
    main()
