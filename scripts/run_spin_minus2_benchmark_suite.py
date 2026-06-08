"""Run the split s=-2 benchmark suite.

High frequency uses GSN in WSL. Low frequency uses Windows Mathematica/MST.
"""
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WOLFRAMSCRIPT = Path(r"F:\mma\wolframscript.exe")
JULIA = "/home/ljq/julia-1.10.7/bin/julia"
DISTRO = "Ubuntu-22.04-D"


def run(cmd, **kwargs):
    print("+", " ".join(str(x) for x in cmd))
    subprocess.run(cmd, cwd=ROOT, check=True, **kwargs)


def main():
    run([
        "cmd", "/c", "wsl", "-d", DISTRO, "-e", "bash", "-lc",
        f"{JULIA} scripts/run_spin_minus2_gsn_benchmark.jl",
    ])

    if not WOLFRAMSCRIPT.exists():
        raise FileNotFoundError(f"Cannot find {WOLFRAMSCRIPT}")
    run([str(WOLFRAMSCRIPT), "-file", str(ROOT / "scripts" / "run_spin_minus2_mathematica_benchmark.wl")])

    print("outputs:")
    print("  results/spin_minus2_gsn_highfreq.csv")
    print("  results/spin_minus2_mathematica_lowfreq.csv")


if __name__ == "__main__":
    main()
