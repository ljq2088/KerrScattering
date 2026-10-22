"""Compare resolved Kerr tails with the Schwarzschild-inspired prefactor."""
import csv
from pathlib import Path
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.analyze_kerr_scalar_tail_models import load, T_H, aicc

rows = []
for ell in (0, 1, 2):
    x, values, balance = load(ell)
    keep = balance <= 1e-8
    x, values = x[keep], values[keep]
    target = np.log(values)
    for name, alpha, fixed_temperature in (
        ('exponential', 0.0, False),
        ('schwarzschild_prefactor', 0.5, False),
        ('hawking_prefactor', 0.5, True),
    ):
        shifted = target + alpha*np.log(x)
        if fixed_temperature:
            slope = -1/T_H
            intercept = float(np.mean(shifted-slope*x))
            parameters = 1
        else:
            slope, intercept = np.polyfit(x, shifted, 1)
            parameters = 2
        predicted = intercept + slope*x - alpha*np.log(x)
        residual = target-predicted
        loo = []
        for i in range(len(x)):
            mask = np.arange(len(x)) != i
            if fixed_temperature:
                b = float(np.mean(shifted[mask]-slope*x[mask]))
                s = slope
            else:
                s, b = np.polyfit(x[mask], shifted[mask], 1)
            loo.append(target[i]-(b+s*x[i]-alpha*np.log(x[i])))
        rows.append(dict(l=ell, model=name, alpha=alpha, points=len(x),
                         omega_min=min(x), omega_max=max(x),
                         pi_Tfit=-np.pi/slope, slope=slope,
                         rms_log=np.sqrt(np.mean(residual**2)),
                         loo_rms_log=np.sqrt(np.mean(np.asarray(loo)**2)),
                         aicc=aicc(residual, parameters),
                         max_balance=max(balance[keep])))
path = ROOT/'results/kerr_scalar_tail_prefactor_20261014.csv'
with path.open('w', newline='', encoding='utf8') as handle:
    writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
for row in rows:
    print(row)
