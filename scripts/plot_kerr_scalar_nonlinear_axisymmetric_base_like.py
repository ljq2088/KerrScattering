"""Build a Schwarzschild-paper-style Kerr nonlinear result figure and table."""

import csv
import os
import warnings

import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import PchipInterpolator
from scipy.optimize import curve_fit


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_FIG = os.path.join(ROOT, "figures", "kerr_scalar_nonlinear_axisymmetric_fig2.png")
OUT_TABLE = os.path.join(ROOT, "results", "kerr_scalar_nonlinear_axisymmetric_fit_table.csv")

INPUTS = {
    0: [
        "results/kerr_scalar_nonlinear_axisymmetric_hires_l0.csv",
        "results/kerr_scalar_nonlinear_axisymmetric_refine_l0.csv",
    ],
    1: [
        "results/kerr_scalar_nonlinear_axisymmetric_hires_l1.csv",
        "results/kerr_scalar_nonlinear_axisymmetric_refine_l1.csv",
    ],
    2: [
        "results/kerr_scalar_nonlinear_axisymmetric_hires_l2.csv",
        "results/kerr_scalar_nonlinear_axisymmetric_refine_l2.csv",
    ],
}


def read_rows(paths):
    best = {}
    for rel in paths:
        path = os.path.join(ROOT, rel)
        with open(path, newline="") as f:
            for row in csv.DictReader(f):
                omega = round(float(row["omega"]), 14)
                score = abs(float(row["nonlinear_balance"]))
                old = best.get(omega)
                if old is None or score < abs(float(old["nonlinear_balance"])):
                    best[omega] = row
    rows = [best[key] for key in sorted(best)]
    omega = np.array([float(row["omega"]) for row in rows])
    t1 = np.array([float(row["T1"]) for row in rows])
    balance = np.array([abs(float(row["nonlinear_balance"])) for row in rows])
    return rows, omega, t1, balance


def qnm_values(a=0.5):
    import qnm

    values = {}
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        for ell in (0, 1, 2):
            seq = qnm.modes_cache(s=0, l=ell, m=0, n=0, compute_if_not_found=True)
            omega, _, _ = seq(a=a)
            values[ell] = omega
    return values


def lorentzian(w, amp, w0, gamma, offset):
    return offset + amp * gamma**2 / ((w - w0) ** 2 + gamma**2)


def fit_peak(omega, t1):
    interp = PchipInterpolator(omega, t1)
    dense = np.linspace(omega.min(), omega.max(), 4000)
    y_dense = interp(dense)
    idx = int(np.argmax(y_dense))
    w_peak = float(dense[idx])
    y_peak = float(y_dense[idx])

    mask = t1 > 0.2 * y_peak
    x = omega[mask]
    y = t1[mask]
    if len(x) >= 5:
        left = x[x < w_peak]
        right = x[x > w_peak]
        width0 = 0.08
        if len(left) and len(right):
            width0 = 0.5 * (right[0] - left[-1])
        p0 = [max(y_peak, 1e-8), w_peak, max(width0, 0.02), 0.0]
        bounds = ([0.0, omega.min(), 1e-4, -np.inf], [np.inf, omega.max(), 1.0, np.inf])
        try:
            popt, _ = curve_fit(lorentzian, x, y, p0=p0, bounds=bounds, maxfev=20000)
            amp, w0, gamma, offset = popt
            prediction = lorentzian(x, *popt)
            rmse = float(np.sqrt(np.mean((y - prediction) ** 2)))
            peak_scale = max(abs(y_peak), np.finfo(float).tiny)
            r2_denominator = float(np.sum((y - np.mean(y)) ** 2))
            r2 = float(
                1.0 - np.sum((y - prediction) ** 2) / r2_denominator
                if r2_denominator > 0.0
                else np.nan
            )
            return (
                float(w0), float(abs(gamma)), float(lorentzian(w0, *popt)),
                rmse / peak_scale, r2, len(x),
            )
        except Exception:
            pass
    return w_peak, np.nan, y_peak, np.nan, np.nan, len(x)


def fit_tail_temperature(omega, t1, qnm_real, w_peak):
    mask = (omega >= max(qnm_real, w_peak + 0.05)) & (t1 > 0.0)
    x = omega[mask]
    y = t1[mask]
    if len(x) < 3:
        x = omega[-4:]
        y = t1[-4:]
    coeff = np.polyfit(x, np.log(y), 1)
    slope = coeff[0]
    if slope >= 0.0:
        return np.nan, np.nan
    tfit = -1.0 / slope
    intercept = coeff[1]
    y_model = np.exp(intercept + slope * x)
    rms_log = float(np.sqrt(np.mean((np.log(y) - np.log(y_model)) ** 2)))
    return float(tfit), rms_log, float(intercept), float(slope), float(x.min()), float(x.max())


def main():
    data = {}
    for ell, paths in INPUTS.items():
        data[ell] = read_rows(paths)

    qnms = qnm_values(a=0.5)
    M = 1.0
    a = 0.5
    r_plus = M + np.sqrt(M**2 - a**2)
    r_minus = M - np.sqrt(M**2 - a**2)
    T_H = (r_plus - r_minus) / (4.0 * np.pi * (r_plus**2 + a**2))

    table_rows = []
    for ell, (_, omega, t1, balance) in data.items():
        w_peak, gamma, y_peak, peak_rms_over_peak, peak_r2, peak_fit_points = fit_peak(omega, t1)
        q = qnms[ell]
        tfit, rms_log, tail_intercept, tail_slope, tail_min, tail_max = fit_tail_temperature(
            omega, t1, q.real, w_peak
        )
        table_rows.append(
            {
                "l": ell,
                "omega_peak": w_peak,
                "gamma": gamma,
                "peak_rms_over_peak": peak_rms_over_peak,
                "peak_r2": peak_r2,
                "peak_fit_points": peak_fit_points,
                "qnm_real": float(q.real),
                "qnm_imag_abs": float(abs(q.imag)),
                "pi_Tfit": float(np.pi * tfit),
                "Tfit_over_TH_minus_1_abs": float(abs(tfit / T_H - 1.0)),
                "tail_rms_log": rms_log,
                "tail_intercept": tail_intercept,
                "tail_slope": tail_slope,
                "tail_omega_min": tail_min,
                "tail_omega_max": tail_max,
                "max_T1": y_peak,
                "max_balance": float(np.max(balance)),
            }
        )

    os.makedirs(os.path.dirname(OUT_TABLE), exist_ok=True)
    with open(OUT_TABLE, "w", newline="") as f:
        fieldnames = [
            "l", "omega_peak", "gamma", "peak_rms_over_peak", "peak_r2",
            "peak_fit_points", "qnm_real", "qnm_imag_abs",
            "pi_Tfit", "Tfit_over_TH_minus_1_abs", "tail_rms_log",
            "tail_intercept", "tail_slope", "tail_omega_min", "tail_omega_max",
            "max_T1", "max_balance",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in table_rows:
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
        ax.set_xlabel(r"$M\omega$")
        ax.grid(False)
        ax.tick_params(direction="in", top=True, right=True)

    tail_rows = {int(row["l"]): row for row in table_rows}
    for ell, (_, omega, t1, _) in data.items():
        idx = np.argsort(omega)
        omega = omega[idx]
        t1 = t1[idx]
        interp = PchipInterpolator(omega, t1)
        dense = np.linspace(omega.min(), omega.max(), 900)
        smooth = np.clip(interp(dense), 1e-18, None)
        axes[0].plot(dense, smooth, color=colors[ell], lw=1.5, label=rf"$\ell={ell}$")
        axes[1].semilogy(dense, smooth, color=colors[ell], lw=1.5, label=rf"$\ell={ell}$")
        tail = tail_rows[ell]
        fit_x = np.linspace(tail["tail_omega_min"], tail["tail_omega_max"], 120)
        fit_y = np.exp(tail["tail_intercept"] + tail["tail_slope"] * fit_x)
        axes[1].semilogy(fit_x, fit_y, color=colors[ell], ls=":", lw=1.4)

    for ell, q in qnms.items():
        for ax in axes:
            ax.axvline(q.real, color="0.35", ls="--", lw=0.8)
    axes[0].plot([], [], color="0.35", ls="--", lw=0.8, label=r"$\Re\omega_{\ell0}$")
    axes[1].plot([], [], color="0.35", ls="--", lw=0.8, label=r"$\Re\omega_{\ell0}$")
    axes[1].plot([], [], color="0.2", ls=":", lw=1.4, label="tail fit")

    axes[0].set_xlim(0.0, 1.0)
    axes[1].set_xlim(0.0, 1.0)
    axes[0].set_ylim(0.0, 0.14)
    axes[1].set_ylim(1e-8, 2e-1)
    axes[0].set_ylabel(r"$T_{\ell}^{(1)}$")
    axes[1].set_ylabel(r"$T_{\ell}^{(1)}$")
    axes[0].legend(frameon=True, fontsize=9, loc="upper right")
    axes[1].legend(frameon=True, fontsize=9, loc="upper right")

    os.makedirs(os.path.dirname(OUT_FIG), exist_ok=True)
    fig.savefig(OUT_FIG, dpi=240)
    plt.close(fig)

    print(OUT_FIG)
    print(OUT_TABLE)
    for row in table_rows:
        print(
            f"l={row['l']} w_peak={row['omega_peak']:.4f} gamma={row['gamma']:.4f} "
            f"qnm={row['qnm_real']:.4f}-{row['qnm_imag_abs']:.4f}i "
            f"piTfit={row['pi_Tfit']:.4f} rel={row['Tfit_over_TH_minus_1_abs']:.3%}"
        )


if __name__ == "__main__":
    main()
