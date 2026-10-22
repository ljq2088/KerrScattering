"""Plot low-frequency Kerr scalar scattering diagnostics."""

import csv
import os

import matplotlib.pyplot as plt
import numpy as np


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_FIG = os.path.join(ROOT, "figures", "kerr_scalar_low_frequency_axisymmetric.png")
OUT_TABLE = os.path.join(ROOT, "results", "kerr_scalar_low_frequency_axisymmetric_acceptance.csv")
OUT_FITS = os.path.join(ROOT, "results", "kerr_scalar_axisymmetric_infrared_fits.csv")
BALANCE_TOL = 1.0e-8
DISPLAY_MAX = {0: 0.09, 1: 0.28, 2: 0.46}
INPUTS = {
    0: [
        "results/kerr_scalar_nonlinear_axisymmetric_hires_l0.csv",
        "results/kerr_scalar_nonlinear_axisymmetric_dense_l0.csv",
    ],
    1: [
        "results/kerr_scalar_nonlinear_axisymmetric_hires_l1.csv",
        "results/kerr_scalar_nonlinear_axisymmetric_dense_l1.csv",
    ],
    2: [
        "results/kerr_scalar_nonlinear_axisymmetric_hires_l2.csv",
        "results/kerr_scalar_nonlinear_axisymmetric_dense_l2.csv",
    ],
}
IR_INPUT = os.path.join(ROOT, "results", "kerr_scalar_axisymmetric_infrared_N176.csv")


def read_rows(paths):
    best = {}
    for rel in paths:
        with open(os.path.join(ROOT, rel), newline="") as f:
            for row in csv.DictReader(f):
                omega = round(float(row["omega"]), 14)
                rank = (
                    int(float(row.get("N", 0))),
                    int(float(row.get("quad_order", 0))),
                    -abs(float(row["nonlinear_balance"])),
                )
                old = best.get(omega)
                old_rank = None if old is None else (
                    int(float(old.get("N", 0))),
                    int(float(old.get("quad_order", 0))),
                    -abs(float(old["nonlinear_balance"])),
                )
                if old is None or rank > old_rank:
                    best[omega] = row
    rows = [best[key] for key in sorted(best)]
    accepted = [
        row for row in rows
        if abs(float(row["nonlinear_balance"])) <= BALANCE_TOL
    ]
    omega = np.array([float(row["omega"]) for row in accepted])
    t0 = np.array([float(row["T0"]) for row in accepted])
    t1 = np.array([float(row["T1"]) for row in accepted])
    balance = np.array([abs(float(row["nonlinear_balance"])) for row in accepted])
    return omega, t0, t1, balance


def read_ir_rows():
    with open(IR_INPUT, newline="") as f:
        rows = list(csv.DictReader(f))
    out = {}
    for ell in (0, 1, 2):
        selected = sorted(
            (row for row in rows if int(row["l"]) == ell),
            key=lambda row: float(row["omega"]),
        )
        out[ell] = {
            "omega": np.array([float(row["omega"]) for row in selected]),
            "T0": np.array([float(row["T0"]) for row in selected]),
            "T1": np.array([float(row["T1"]) for row in selected]),
            "A0": float(selected[0]["analytic_T0_coefficient"]),
            "A1": float(selected[0]["analytic_T1_coefficient"]),
        }
    return out


def log_power_fit(omega, values):
    x = np.log(omega)
    y = np.log(values)
    slope, intercept = np.polyfit(x, y, 1)
    prediction = intercept + slope * x
    denominator = float(np.sum((y - np.mean(y)) ** 2))
    r2 = 1.0 - float(np.sum((y - prediction) ** 2)) / denominator
    return float(slope), float(intercept), float(r2)


def main():
    data = {ell: read_rows(paths) for ell, paths in INPUTS.items()}
    infrared = read_ir_rows()
    summary = []
    for ell, (omega, t0, t1, balance) in data.items():
        take = omega <= DISPLAY_MAX[ell]
        summary.append(
            {
                "l": ell,
                "lowest_accepted_omega": float(omega[0]),
                "highest_displayed_omega": float(omega[take][-1]),
                "displayed_points": int(np.count_nonzero(take)),
                "T0_at_lowest": float(t0[0]),
                "T1_at_lowest": float(t1[0]),
                "abs_balance_at_lowest": float(balance[0]),
            }
        )

    os.makedirs(os.path.dirname(OUT_TABLE), exist_ok=True)
    with open(OUT_TABLE, "w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "l", "lowest_accepted_omega", "highest_displayed_omega",
                "displayed_points", "T0_at_lowest", "T1_at_lowest",
                "abs_balance_at_lowest",
            ],
        )
        writer.writeheader()
        for row in summary:
            writer.writerow({k: (f"{v:.12e}" if isinstance(v, float) else v) for k, v in row.items()})

    fit_rows = []
    for ell, ir in infrared.items():
        expected = 2 * ell + 2
        for quantity in ("T0", "T1"):
            for points in range(len(ir["omega"]), len(ir["omega"]) - 3, -1):
                omega = ir["omega"][:points]
                values = ir[quantity][:points]
                slope, intercept, r2 = log_power_fit(omega, values)
                fit_rows.append(
                    {
                        "l": ell,
                        "quantity": quantity,
                        "points": points,
                        "omega_min": float(omega[0]),
                        "omega_max": float(omega[-1]),
                        "power": slope,
                        "intercept": intercept,
                        "R2": r2,
                        "expected_power": expected,
                    }
                )
    with open(OUT_FITS, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(fit_rows[0]))
        writer.writeheader()
        for row in fit_rows:
            writer.writerow({k: (f"{v:.12e}" if isinstance(v, float) else v) for k, v in row.items()})

    plt.rcParams.update(
        {
            "font.family": "DejaVu Serif",
            "font.size": 10,
            "mathtext.fontset": "dejavuserif",
            "axes.linewidth": 0.8,
        }
    )
    colors = {0: "#0072bd", 1: "#d95319", 2: "#edb120"}
    fig, axes = plt.subplots(1, 2, figsize=(8.4, 3.25), constrained_layout=True)
    for ax in axes:
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlabel(r"$M\omega$")
        ax.tick_params(direction="in", top=True, right=True)
    axes[0].set_ylabel(r"$T_\ell^{(0)}$")
    axes[1].set_ylabel(r"$T_\ell^{(1)}$")

    for ell, (omega, t0, t1, _) in data.items():
        take = omega <= DISPLAY_MAX[ell]
        axes[0].plot(omega[take], t0[take], "o-", color=colors[ell], ms=3, lw=1.2, label=rf"$\ell={ell}$")
        axes[1].plot(omega[take], t1[take], "o-", color=colors[ell], ms=3, lw=1.2, label=rf"$\ell={ell}$")
        ir = infrared[ell]
        axes[0].plot(
            ir["omega"], ir["T0"], "o", color=colors[ell], ms=4,
            markerfacecolor="white", markeredgewidth=0.9,
        )
        axes[1].plot(
            ir["omega"], ir["T1"], "o", color=colors[ell], ms=4,
            markerfacecolor="white", markeredgewidth=0.9,
        )
        guide = np.geomspace(ir["omega"].min(), ir["omega"].max(), 120)
        power = 2 * ell + 2
        axes[0].plot(guide, ir["A0"] * guide**power, "--", color=colors[ell], lw=1.0)
        axes[1].plot(guide, ir["A1"] * guide**power, "--", color=colors[ell], lw=1.0)

    for ax in axes:
        ax.plot([], [], "o", color="0.25", ms=4, markerfacecolor="white", label="horizon-side IR")
        ax.plot([], [], "--", color="0.25", lw=1.0, label="analytic IR")

    axes[0].legend(frameon=True, fontsize=9, loc="best")
    axes[1].legend(frameon=True, fontsize=9, loc="best")

    os.makedirs(os.path.dirname(OUT_FIG), exist_ok=True)
    fig.savefig(OUT_FIG, dpi=360)
    plt.close(fig)

    print(OUT_FIG)
    print(OUT_TABLE)
    print(OUT_FITS)
    for row in summary:
        print(
            f"l={row['l']} accepted Momega>={row['lowest_accepted_omega']:.3f} "
            f"displayed through {row['highest_displayed_omega']:.3f}"
        )


if __name__ == "__main__":
    main()
