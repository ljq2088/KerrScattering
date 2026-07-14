"""Select best nonlinear frequency-sweep rows from repeated Kerr runs."""

import csv
import os


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUTS = [
    os.path.join(ROOT, "results", "kerr_scalar_nonlinear_frequency_sweep.csv"),
    os.path.join(ROOT, "results", "tmp_kerr_scalar_nonlinear_frequency_sweep_highcheck.csv"),
    os.path.join(ROOT, "results", "tmp_kerr_scalar_nonlinear_frequency_sweep_threshold_highcheck.csv"),
]
OUT = os.path.join(ROOT, "results", "kerr_scalar_nonlinear_frequency_sweep_best.csv")
BALANCE_ACCEPT = 1e-8


def read_rows(path):
    if not os.path.exists(path):
        return []
    with open(path, newline="") as f:
        rows = list(csv.DictReader(f))
    for row in rows:
        row["_source_file"] = os.path.basename(path)
    return rows


def main():
    best = {}
    for path in INPUTS:
        for row in read_rows(path):
            key = (row["label"], row["omega"])
            score = abs(float(row["nonlinear_balance"]))
            old = best.get(key)
            if old is None or score < abs(float(old["nonlinear_balance"])):
                best[key] = row

    rows = sorted(best.values(), key=lambda r: (r["label"], float(r["omega"])))
    for row in rows:
        residual = abs(float(row["nonlinear_balance"]))
        row["abs_nonlinear_balance"] = f"{residual:.16e}"
        row["accepted_balance"] = "true" if residual <= BALANCE_ACCEPT else "false"
        row["source_file"] = row.pop("_source_file")

    if not rows:
        raise RuntimeError("No input rows found.")

    fields = [field for field in rows[0].keys() if not field.startswith("_")]
    if "source_file" not in fields:
        fields.append("source_file")
    if "accepted_balance" not in fields:
        fields.append("accepted_balance")

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print(OUT)
    for row in rows:
        print(
            f"omega={float(row['omega']):.3f} T1={float(row['T1']):+.3e} "
            f"R1={float(row['R1']):+.3e} residual={float(row['abs_nonlinear_balance']):.3e} "
            f"accepted={row['accepted_balance']} source={row['source_file']}"
        )


if __name__ == "__main__":
    main()
