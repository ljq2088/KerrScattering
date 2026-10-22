"""Bounded endpoint audit; historical rows are never overwritten."""
import csv
import argparse
import gc
import os
from pathlib import Path
import sys
import threading
import time
from contextlib import contextmanager

for name in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[name] = "1"
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import numpy as np
from src import kerr_scalar_spectral as spectral
from src.kerr_scalar_nonlinear import (
    compute_kerr_scalar_green_diagnostics, fixed_incident_flux_coefficients,
)
from src.teukolsky_scalar import KerrParams, teukolsky_lambda_s0
from scripts.run_kerr_scalar_spectral_quality import _offgrid_residuals, _cheb_coeff
from scripts.run_kerr_scalar_nonlinear_diagnostics import current_rss_mb, require_memory_room


@contextmanager
def endpoint_version(legacy):
    original = spectral._transformed_coefficients

    def old_row(z, branch, params, l, m, omega, lam):
        B2, B1, B0 = original(z, branch, params, l, m, omega, lam)
        mask = np.isclose(z, 0.0, rtol=0.0, atol=1e-14)
        return B2, B1, np.where(mask, -lam, B0)

    if legacy:
        spectral._transformed_coefficients = old_row
    try:
        yield
    finally:
        spectral._transformed_coefficients = original


def radial_quality(a, l, m, omega, N, r_match):
    params = KerrParams(M=1.0, a=a)
    lam = teukolsky_lambda_s0(l, m, a, omega)
    zm = params.rp / r_match
    out = {}
    for branch, left, right in [("down", 0.0, zm), ("up", 0.0, zm), ("in", zm, 1.0)]:
        # Evaluators preserve the solved nodal amplitudes in their data dict.
        data = spectral._solve_branch(
            N, left, right, branch, "right" if branch == "in" else "left",
            params, "linear", 0.0, l, m, omega, lam, "equilibrated",
        )
        residual = _offgrid_residuals(
            data, left, right, branch, params, "linear", 0.0,
            l, m, omega, lam, 600,
        )
        coeff = np.abs(_cheb_coeff(data["u"]))
        out[f"{branch}_radial_residual_max"] = float(np.max(residual[5]))
        out[f"{branch}_amplitude_residual_max"] = float(np.max(residual[2]))
        out[f"{branch}_coeff_tail"] = float(np.max(coeff[-16:]) / np.max(coeff))
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "results/kerr_scalar_endpoint_factored_audit_20261008.csv")
    args = parser.parse_args()
    output = args.output
    rows = []
    peak = [0.0]
    stop = threading.Event()

    def monitor():
        while not stop.wait(0.05):
            peak[0] = max(peak[0], current_rss_mb() or 0.0)

    worker = threading.Thread(target=monitor, daemon=True)
    worker.start()
    try:
        for a in (0.99, 0.999):
            params = KerrParams(M=1.0, a=a)
            kappa = (params.rp - params.rm) / (2 * (params.rp**2 + a*a))
            for l in (1, 2):
                omega = l * params.omega_h + 0.5 * kappa
                for legacy, N in [(False, 128), (False, 176), (False, 224), (True, 224)]:
                    quality = None
                    for n in (1, 2):
                        require_memory_room(900, "before endpoint audit sample")
                        start = time.perf_counter()
                        print(f"a={a} l=m={l} n={n} N={N} legacy={legacy}", flush=True)
                        with endpoint_version(legacy):
                            result = compute_kerr_scalar_green_diagnostics(
                                l, l, omega, a=a, N_outer=N, N_inner=N,
                                r_match=12.0, quad_order=2*N, tail_epsrel=1e-11,
                                linear_solver="equilibrated", nonlinearity_order=n,
                            )
                            flux = fixed_incident_flux_coefficients(result)
                            if quality is None:
                                # The residual evaluator always uses the correct interior ODE.
                                quality = radial_quality(a, l, l, omega, N, 12.0)
                        row = dict(a=a, l=l, m=l, n=n, y=0.5, omega=omega,
                                   kappa=kappa, N=N, quad_order=2*N, r_match=12.0,
                                   legacy=legacy, T0=flux.T0, T1=flux.T1, R1=flux.R1,
                                   chi=flux.horizon_response,
                                   linear_balance=flux.linear_balance,
                                   nonlinear_balance=flux.nonlinear_balance,
                                   wronskian_error=result.wronskian_relative_error,
                                   peak_rss_mb=peak[0], elapsed_s=time.perf_counter()-start,
                                   **quality)
                        rows.append(row)
                        temporary = output.with_suffix(".csv.tmp")
                        with temporary.open("w", newline="", encoding="utf8") as handle:
                            writer = csv.DictWriter(handle, fieldnames=list(row))
                            writer.writeheader()
                            writer.writerows(rows)
                        temporary.replace(output)
                        print(f"  chi={flux.horizon_response:.12g} T0={flux.T0:.9g} "
                              f"peak RSS={peak[0]:.1f} MB", flush=True)
                        gc.collect()
    finally:
        stop.set()
        worker.join()
    print(f"Saved {len(rows)} rows to {output}")


if __name__ == "__main__":
    main()
