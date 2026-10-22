"""Separate Green quadrature and matching-radius checks at the hardest audit point."""
import csv
from pathlib import Path
from audit_scalar_endpoint_20261008 import (
    ROOT, compute_kerr_scalar_green_diagnostics, fixed_incident_flux_coefficients,
    KerrParams, require_memory_room,
)
from scripts.run_kerr_scalar_near_extremal_scaling import surface_gravity


def main():
    params = KerrParams(M=1.0, a=0.999)
    omega = 2*params.omega_h + 0.5*surface_gravity(params)
    rows = []
    output = ROOT / "results/kerr_scalar_endpoint_quadrature_match_20261008.csv"
    for rmatch, q in [(12, 448), (12, 896), (12, 1792), (8, 1792), (16, 1792)]:
        for n in (1, 2):
            require_memory_room(900, "before refinement")
            result = compute_kerr_scalar_green_diagnostics(
                2, 2, omega, a=params.a, N_outer=224, N_inner=224,
                r_match=rmatch, quad_order=q, tail_epsrel=1e-11,
                linear_solver="equilibrated", nonlinearity_order=n,
            )
            flux = fixed_incident_flux_coefficients(result)
            row = dict(a=params.a, l=2, m=2, y=0.5, omega=omega, n=n,
                       N=224, quad_order=q, r_match=rmatch, chi=flux.horizon_response,
                       T0=flux.T0, T1=flux.T1, R1=flux.R1,
                       linear_balance=flux.linear_balance,
                       nonlinear_balance=flux.nonlinear_balance,
                       rss_mb=require_memory_room(900, "after refinement"))
            print(row, flush=True)
            rows.append(row)
            with output.open("w", newline="", encoding="utf8") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(row))
                writer.writeheader()
                writer.writerows(rows)


if __name__ == "__main__":
    main()
