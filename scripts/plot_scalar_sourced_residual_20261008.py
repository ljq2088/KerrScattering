"""Plot all local reconstruction degrees, including the differentiation floor."""
import csv
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
with (ROOT / "results/kerr_scalar_sourced_local_residual_20261008.csv").open(newline="", encoding="utf8") as handle:
    rows = list(csv.DictReader(handle))
plt.rcParams.update({"font.size": 10, "font.family": "serif"})
fig, axes = plt.subplots(1, 2, figsize=(7.0, 2.3), constrained_layout=True)
for name, m, n, color in [("A", 0, 1, "#0072b2"), ("B", 0, 2, "#d55e00"), ("C", 2, 1, "#009e73")]:
    selected = [r for r in rows if int(r["m"]) == m and int(r["n"]) == n]
    degree = [int(r["N_reconstruction"]) for r in selected]
    for ax, key in zip(axes, ("relative_residual_max", "coeff_tail")):
        ax.semilogy(degree, [float(r[key]) for r in selected], "o-", color=color, label=f"Case {name}", markersize=4)
        ax.set_xlabel("Reconstruction degree $D$")
        ax.set_xticks([16, 24, 32, 48, 64])
        ax.grid(alpha=0.25)
axes[0].set_ylabel(r"$\max\delta_1$")
axes[1].set_ylabel("Relative coefficient tail")
axes[0].legend(frameon=False)
fig.savefig(ROOT / "figures/kerr_scalar_sourced_local_validation_20261008.png", dpi=220)
plt.close(fig)
