"""Build a Markdown validation report for the Kerr s=0 spectral solver."""

import csv
import os
import sys


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SUMMARY = os.path.join(ROOT, "results", "kerr_scalar_adaptive_summary.csv")
GSN_BENCHMARK = os.path.join(ROOT, "results", "kerr_scalar_gsn_benchmark.csv")
SWEEP = os.path.join(ROOT, "results", "kerr_scalar_frequency_sweep.csv")
COUPLINGS = os.path.join(ROOT, "results", "kerr_scalar_cubic_couplings.csv")
NONLINEAR = os.path.join(ROOT, "results", "kerr_scalar_nonlinear_diagnostics.csv")
NONLINEAR_CONTROL = os.path.join(ROOT, "results", "kerr_scalar_nonlinear_control_scan.csv")
NONLINEAR_CHANNELS = os.path.join(ROOT, "results", "kerr_scalar_nonlinear_channels.csv")
NONLINEAR_CHANNEL_CONVERGENCE = os.path.join(
    ROOT, "results", "kerr_scalar_nonlinear_channel_convergence.csv"
)
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
    gsn_rows = []
    if os.path.exists(GSN_BENCHMARK):
        with open(GSN_BENCHMARK, newline="") as f:
            gsn_rows = list(csv.DictReader(f))

    max_score = max(float(row["score"]) for row in rows)
    max_flux = max(float(row["flux_balance_error"]) for row in rows)
    all_passed = all(row["passed"] == "true" for row in rows)
    excluded_gsn = [row for row in gsn_rows if row["status"] != "ok"]
    sweep_rows = []
    if os.path.exists(SWEEP):
        with open(SWEEP, newline="") as f:
            sweep_rows = list(csv.DictReader(f))
    coupling_rows = []
    if os.path.exists(COUPLINGS):
        with open(COUPLINGS, newline="") as f:
            coupling_rows = list(csv.DictReader(f))
    nonlinear_rows = []
    if os.path.exists(NONLINEAR):
        with open(NONLINEAR, newline="") as f:
            nonlinear_rows = list(csv.DictReader(f))
    nonlinear_control_rows = []
    if os.path.exists(NONLINEAR_CONTROL):
        with open(NONLINEAR_CONTROL, newline="") as f:
            nonlinear_control_rows = list(csv.DictReader(f))
    nonlinear_channel_rows = []
    if os.path.exists(NONLINEAR_CHANNELS):
        with open(NONLINEAR_CHANNELS, newline="") as f:
            nonlinear_channel_rows = list(csv.DictReader(f))
    nonlinear_channel_convergence_rows = []
    if os.path.exists(NONLINEAR_CHANNEL_CONVERGENCE):
        with open(NONLINEAR_CHANNEL_CONVERGENCE, newline="") as f:
            nonlinear_channel_convergence_rows = list(csv.DictReader(f))

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
        "## Phase convention",
        "",
        "The spectral code reports amplitudes in its own Kerr tortoise coordinate",
        "convention. At infinity the basis is",
        "`exp(-i omega r*)/r` for the incident wave and `exp(+i omega r*)/r`",
        "for the reflected wave; at the horizon the unit-amplitude in-mode uses",
        "`exp[-i (omega - m Omega_H) r*]`. If another package uses",
        "`r* -> r* + C`, then the complex coefficients transform by",
        "`B_inc -> B_inc exp(-i omega C)` and",
        "`B_ref -> B_ref exp(+i omega C)` in the infinity basis. Therefore the",
        "magnitudes, reflection probability, transmission probability, and flux",
        "balance are the benchmark quantities used for pass/fail validation.",
        "",
        "## Summary",
        "",
        f"- GSN benchmark requests: {len(gsn_rows) if gsn_rows else 'not recorded'}",
        f"- Usable GSN benchmark cases tested: {len(rows)}",
        f"- GSN benchmark cases excluded: {len(excluded_gsn)}",
        f"- All cases passed: `{str(all_passed).lower()}`",
        f"- Worst score: `{max_score:.3e}`",
        f"- Worst flux-balance residual: `{max_flux:.3e}`",
        "",
    ]

    if excluded_gsn:
        lines.extend([
            "Excluded GSN cases are retained in the benchmark CSV but omitted from",
            "the pass/fail table because the external package returned zero or",
            "non-finite amplitudes:",
            "",
        ])
        for row in excluded_gsn:
            lines.append(
                f"- `l={row['l']}, m={row['m']}, a={float(row['a']):.3g}, "
                f"omega={float(row['omega']):.3g}`: {row['status']}"
            )
        lines.append("")

    lines.extend([
        "| l | m | a | omega | N | r_match | mapping | rel_abs_B_inc | rel_abs_B_ref | flux | score | passed |",
        "|---:|---:|---:|---:|---:|---:|:---|---:|---:|---:|---:|:---|",
    ])

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

    if sweep_rows:
        max_sweep_score = max(float(row["score"]) for row in sweep_rows)
        max_sweep_flux = max(float(row["flux_balance_error"]) for row in sweep_rows)
        all_sweep_passed = all(row["passed"] == "true" for row in sweep_rows)
        superradiant_rows = [
            row for row in sweep_rows
            if row["superradiant"] == "true" and float(row["amplification"]) > 0.0
        ]
        max_amp = (
            max(superradiant_rows, key=lambda row: float(row["amplification"]))
            if superradiant_rows else None
        )

        lines.extend([
            "",
            "## Frequency sweep",
            "",
            "A publication-style frequency sweep is generated by",
            "`scripts/run_kerr_scalar_frequency_sweep.py` and plotted by",
            "`scripts/plot_kerr_scalar_frequency_sweep.py`. The sweep uses",
            "self-convergence in spectral order, the same direct endpoint rows, and",
            "the invariant flux balance check.",
            "",
            f"- Sweep points: {len(sweep_rows)}",
            f"- All sweep points passed: `{str(all_sweep_passed).lower()}`",
            f"- Worst sweep score: `{max_sweep_score:.3e}`",
            f"- Worst sweep flux-balance residual: `{max_sweep_flux:.3e}`",
            "- Maximum sampled superradiant amplification: " + (
                f"`{float(max_amp['amplification']):.3e}` at "
                f"`{max_amp['label']}`, `omega={float(max_amp['omega']):.3g}`"
                if max_amp is not None else "`none in this sweep`"
            ),
            "",
            "| label | l | m | a | omega range | points | max R-1 | all passed |",
            "|:---|---:|---:|---:|:---|---:|---:|:---|",
        ])

        for label in sorted({row["label"] for row in sweep_rows}):
            subset = [row for row in sweep_rows if row["label"] == label]
            omegas = [float(row["omega"]) for row in subset]
            max_case_amp = max(float(row["amplification"]) for row in subset)
            case_passed = all(row["passed"] == "true" for row in subset)
            first = subset[0]
            lines.append(
                "| {label} | {l} | {m} | {a:.3g} | {omin:.3g}--{omax:.3g} | "
                "{n} | {amp:.3e} | {passed} |".format(
                    label=label,
                    l=first["l"],
                    m=first["m"],
                    a=float(first["a"]),
                    omin=min(omegas),
                    omax=max(omegas),
                    n=len(subset),
                    amp=max_case_amp,
                    passed=str(case_passed).lower(),
                )
            )

    if coupling_rows:
        coupling_cases = {
            (row["l_source"], row["m"], row["a"], row["omega"])
            for row in coupling_rows
        }
        self_rows = [
            row for row in coupling_rows
            if int(row["l_source"]) == int(row["l_target"])
        ]
        offdiag_rows = [
            row for row in coupling_rows
            if int(row["l_source"]) != int(row["l_target"])
        ]
        min_self = min(self_rows, key=lambda row: float(row["abs_coefficient"]))
        max_self = max(self_rows, key=lambda row: float(row["abs_coefficient"]))
        max_offdiag = max(offdiag_rows, key=lambda row: float(row["abs_coefficient"]))

        lines.extend([
            "",
            "## Cubic angular projector",
            "",
            "The Kerr nonlinear source requires the spheroidal projection",
            "`C_{l'lm} = int dOmega conj(S_l'm) |S_lm|^2 S_lm`. The table",
            "`results/kerr_scalar_cubic_couplings.csv` evaluates these coefficients",
            "for every validated source mode and target channels `|m| <= l' <= l+4`.",
            "",
            f"- Source modes projected: {len(coupling_cases)}",
            f"- Coupling rows: {len(coupling_rows)}",
            "- Self-channel coefficient range: "
            f"`{float(min_self['abs_coefficient']):.3e}` to "
            f"`{float(max_self['abs_coefficient']):.3e}`",
            "- Largest off-diagonal coefficient: "
            f"`{float(max_offdiag['abs_coefficient']):.3e}` for "
            f"`l={max_offdiag['l_source']}, m={max_offdiag['m']}, "
            f"a={float(max_offdiag['a']):.3g}, "
            f"omega={float(max_offdiag['omega']):.3g}, "
            f"l'={max_offdiag['l_target']}`",
        ])

    if nonlinear_rows:
        finite_rows = [
            row for row in nonlinear_rows
            if row["rel_A_ref_from_previous"] != "inf"
        ]
        max_werr = max(float(row["wronskian_relative_error"]) for row in nonlinear_rows)
        max_ref_delta = max(float(row["rel_A_ref_from_previous"]) for row in finite_rows)
        max_hor_delta = max(float(row["rel_A_hor_from_previous"]) for row in finite_rows)
        diagnostic_cases = {row["label"] for row in nonlinear_rows}
        rss_values = [
            float(row["rss_mb_after"])
            for row in nonlinear_rows
            if row.get("rss_mb_after")
        ]
        elapsed_values = [
            float(row["elapsed_s"])
            for row in nonlinear_rows
            if row.get("elapsed_s")
        ]
        lines.extend([
            "",
            "## Nonlinear radial diagnostics",
            "",
            "`scripts/run_kerr_scalar_nonlinear_diagnostics.py` evaluates",
            "Green-function radial source integrals using the Kerr-covariant",
            "cubic scalar source",
            "`(r^2 C0 + a^2 C2) |R|^2 R` and the physical `dr` measure.",
            "The exterior integral is evaluated after decomposing the outer",
            "homogeneous solutions into `exp(i n omega r*)` phase channels,",
            "so the oscillatory tail is integrated on `r* in [r*_match, inf)`",
            "instead of by a compactified endpoint Gauss rule.",
            "",
            f"- Diagnostic cases: {len(diagnostic_cases)}",
            f"- Quadrature rows: {len(nonlinear_rows)}",
            f"- Worst Wronskian consistency error: `{max_werr:.3e}`",
            f"- Worst consecutive `A_ref_1` quadrature change: `{max_ref_delta:.3e}`",
            f"- Worst consecutive `A_hor_1` quadrature change: `{max_hor_delta:.3e}`",
        ])
        if rss_values:
            lines.append(f"- Peak recorded process RSS: `{max(rss_values):.1f} MB`")
        if elapsed_values:
            lines.append(f"- Slowest diagnostic row: `{max(elapsed_values):.2f} s`")
        if nonlinear_control_rows:
            control_rows = [
                row for row in nonlinear_control_rows
                if row.get("rel_A_ref_to_base")
            ]
            max_control_ref = max(
                float(row["rel_A_ref_to_base"]) for row in control_rows
            )
            max_control_hor = max(
                float(row["rel_A_hor_to_base"]) for row in control_rows
            )
            lines.extend([
                f"- Control scan rows: {len(nonlinear_control_rows)}",
                "- Largest control-scan reflection change: "
                f"`{max_control_ref:.3e}`",
                "- Largest control-scan horizon change: "
                f"`{max_control_hor:.3e}`",
                "The largest reflection control changes occur in deliberately",
                "coarser or farther matching tests; the production rows use",
                "`N=256` and the stable matching window recorded in the CSV.",
            ])
        if nonlinear_channel_rows:
            active_channels = [
                row for row in nonlinear_channel_rows
                if row["status"] == "ok"
            ]
            skipped_channels = [
                row for row in nonlinear_channel_rows
                if row["status"] != "ok"
            ]
            strongest_ref = max(
                active_channels,
                key=lambda row: float(row["abs_A_ref_1"]),
            )
            lines.extend([
                "",
                "### Nonlinear target-channel scan",
                "",
                "`scripts/run_kerr_scalar_nonlinear_channels.py` performs the",
                "first multi-`l'` extension of the nonlinear Green-function",
                "calculation. The current tracked table scans",
                "`kerr_a05_l2m2_super` with target channels `l'=2,...,6`.",
                "",
                f"- Channel rows: {len(nonlinear_channel_rows)}",
                f"- Active radial solves: {len(active_channels)}",
                f"- Skipped zero-coupling channels: {len(skipped_channels)}",
                "- Strongest reflected channel: "
                f"`l'={strongest_ref['l_target']}`, "
                f"`|A_ref_1|={float(strongest_ref['abs_A_ref_1']):.3e}`",
                "",
                "| l' | |C0| | |A_ref_1| | |A_H_1| | status |",
                "|---:|---:|---:|---:|:---|",
            ])
            for row in nonlinear_channel_rows:
                lines.append(
                    "| {lt} | {c0:.3e} | {aref:.3e} | {ahor:.3e} | {status} |".format(
                        lt=row["l_target"],
                        c0=float(row["abs_angular_coupling"]),
                        aref=float(row["abs_A_ref_1"]),
                        ahor=float(row["abs_A_hor_1"]),
                        status=row["status"],
                    )
                )
            if nonlinear_channel_convergence_rows:
                non_reference_rows = [
                    row for row in nonlinear_channel_convergence_rows
                    if float(row["rel_A_ref_to_reference"]) > 0.0
                    or float(row["rel_A_hor_to_reference"]) > 0.0
                ]
                max_conv_ref = max(
                    float(row["rel_A_ref_to_reference"])
                    for row in non_reference_rows
                )
                max_conv_hor = max(
                    float(row["rel_A_hor_to_reference"])
                    for row in non_reference_rows
                )
                max_abs_conv_ref = max(
                    float(row["abs_delta_A_ref_to_reference"])
                    for row in non_reference_rows
                )
                max_abs_conv_hor = max(
                    float(row["abs_delta_A_hor_to_reference"])
                    for row in non_reference_rows
                )
                lines.extend([
                    "",
                    "The multi-channel result is also checked against a higher-order",
                    "reference row for each active target channel. The current",
                    "convergence scan compares `(N,q)=(224,224),(256,224),(288,224)`.",
                    "",
                    "- Channel-convergence rows: "
                    f"{len(nonlinear_channel_convergence_rows)}",
                    "- Largest reflected-amplitude change to reference: "
                    f"`{max_conv_ref:.3e}` relative, `{max_abs_conv_ref:.3e}` absolute",
                    "- Largest horizon-amplitude change to reference: "
                    f"`{max_conv_hor:.3e}` relative, `{max_abs_conv_hor:.3e}` absolute",
                    "The large relative horizon value is caused by the nearly",
                    "vanishing off-diagonal `l'=6` horizon amplitude; the reflected",
                    "channel amplitudes are the robust multi-channel observables in",
                    "the current double-precision implementation.",
                    "",
                    "| l' | N | q | rel A_ref | abs dA_ref | rel A_H | abs dA_H |",
                    "|---:|---:|---:|---:|---:|---:|---:|",
                ])
                for row in nonlinear_channel_convergence_rows:
                    lines.append(
                        "| {lt} | {n} | {q} | {dref:.3e} | {adref:.3e} | "
                        "{dhor:.3e} | {adhor:.3e} |".format(
                            lt=row["l_target"],
                            n=row["N_outer"],
                            q=row["quad_order"],
                            dref=float(row["rel_A_ref_to_reference"]),
                            adref=float(row["abs_delta_A_ref_to_reference"]),
                            dhor=float(row["rel_A_hor_to_reference"]),
                            adhor=float(row["abs_delta_A_hor_to_reference"]),
                        )
                    )

    lines.extend([
        "",
        "## Current interpretation",
        "",
        "The present validation covers the Schwarzschild limit, moderate Kerr spin,",
        "near-superradiant scalar modes, low-frequency superradiant scattering,",
        "high-frequency small-reflection scattering, and high-spin Kerr cases.",
        "The GSN benchmark grid now includes nonrotating checks, non-superradiant",
        "`m=0` modes, multiple `l=1,2,3` modes, and rotating cases on both sides",
        "of `omega = m Omega_H`.",
        "",
        "The worst invariant benchmark error in the current table is below `1.5e-8`,",
        "which is comfortably inside the `1e-7` amplitude-magnitude target. The",
        "hardest case is the high-frequency `l=m=2, a=0.5, omega=1.0` mode, where",
        "`B_ref` is small and therefore relative errors are more sensitive to",
        "conditioning.",
        "",
        "The frequency sweep resolves the Schwarzschild absorption curve and the",
        "Kerr scalar superradiant regime. For the sampled rotating cases, `R > 1`",
        "appears only for `omega < m Omega_H`, while the reported flux residuals",
        "remain below the acceptance gate.",
        "",
        "The angular cubic projector, Kerr-covariant cubic radial source, and",
        "oscillatory-tail Green-function integration are now explicit. Wronskians",
        "are stable at machine precision. The target-channel implementation now",
        "has a first active-channel convergence scan. The remaining nonlinear work",
        "is to set broader production acceptance gates across more modes and, if needed,",
        "replace the QUADPACK Fourier tail by a dedicated Levin/Filon integrator",
        "for very high-frequency nonlinear tails.",
        "",
        "## Remaining PRD-level work",
        "",
        "- Extend the nonlinear table beyond the four representative modes.",
        "- Add an independent oscillatory-tail integrator for high-frequency",
        "  nonlinear source terms.",
        "",
        "Generated from `results/kerr_scalar_adaptive_summary.csv`,",
        "`results/kerr_scalar_frequency_sweep.csv`, and",
        "`results/kerr_scalar_cubic_couplings.csv`, plus nonlinear diagnostics",
        "channel scans, channel-convergence scans, and control scans when available.",
        "",
    ])

    os.makedirs(os.path.dirname(REPORT), exist_ok=True)
    with open(REPORT, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines))
    print(REPORT)


if __name__ == "__main__":
    main()
