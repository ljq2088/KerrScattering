"""Compute spin-weighted spheroidal lambda with the user's WSL helper."""
import csv
import importlib.util
from pathlib import Path


HELPER = Path("/home/ljq/code/PINN/SolvingTeukolskyEq_autoencoder/utils/compute_lambda_usage.py")
OUT = Path("results/spin_minus2_lambda_probe.csv")


def load_helper():
    spec = importlib.util.spec_from_file_location("compute_lambda_usage", HELPER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    module = load_helper()
    rows = []
    for omega in [1.0e-4, 10.0]:
        rows.append({
            "s": -2,
            "a": 0.5,
            "l": 2,
            "m": 2,
            "omega": omega,
            "lambda": module.compute_lambda(0.5, omega, 2, 2, -2),
            "helper": str(HELPER),
            "status": "ok",
        })

    OUT.parent.mkdir(exist_ok=True)
    with OUT.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    for row in rows:
        print(f"omega={row['omega']} lambda={row['lambda']}")
    print(f"saved={OUT}")


if __name__ == "__main__":
    main()
