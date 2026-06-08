"""Probe availability of external s=-2 benchmark tools in WSL."""
import json
import os
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "spin_minus2_benchmark_probe.json"
DISTRO = "Ubuntu-22.04-D"


def wsl(cmd):
    proc = subprocess.run(
        ["wsl", "-d", DISTRO, "-e", "bash", "-lc", cmd],
        text=True,
        capture_output=True,
        timeout=120,
    )
    return {
        "returncode": proc.returncode,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
    }


def main():
    checks = {
        "distro": {"returncode": 0, "stdout": DISTRO, "stderr": ""},
        "wsl_uname": wsl("uname -a"),
        "julia": wsl("command -v julia || test -x /home/ljq/julia-1.10.7/bin/julia && echo /home/ljq/julia-1.10.7/bin/julia || true"),
        "wolframscript": wsl("command -v wolframscript || true"),
        "math": wsl("command -v math || true"),
        "lambda_script": wsl(
            "test -f /home/ljq/code/PINN/SolvingTeukolskyEq_autoencoder/utils/compute_lambda_usage.py "
            "&& echo found || echo missing"
        ),
        "gsn_dir": wsl("test -d /home/ljq/code/GSN/GeneralizedSasakiNakamura.jl && echo found || echo missing"),
        "repo_search": wsl(
            "find /home -maxdepth 6 "
            "\\( -path '*compute_lambda_usage.py' -o -path '*GeneralizedSasakiNakamura*' -o -path '*/GSN' \\) "
            "2>/dev/null | head -50"
        ),
    }

    os.makedirs(OUT.parent, exist_ok=True)
    OUT.write_text(json.dumps(checks, indent=2), encoding="utf-8")
    print(OUT)
    for name, result in checks.items():
        print(f"{name}: {result['stdout'] or '<empty>'}")


if __name__ == "__main__":
    main()
