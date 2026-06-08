"""CLI for Teukolsky separation constants."""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.teukolsky_lambda import compute_teukolsky_lambda


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--s", type=int, default=0)
    parser.add_argument("--l", type=int, required=True)
    parser.add_argument("--m", type=int, required=True)
    parser.add_argument("--a", type=float, required=True)
    parser.add_argument("--omega", type=float, required=True)
    parser.add_argument(
        "--provider",
        choices=["auto", "local", "wsl-helper", "gsn"],
        default="auto",
    )
    args = parser.parse_args()

    result = compute_teukolsky_lambda(
        s=args.s,
        l=args.l,
        m=args.m,
        a=args.a,
        omega=args.omega,
        provider=args.provider,
    )
    print(f"value={result.value}")
    print(f"provider={result.provider}")
    print(f"convention={result.convention}")


if __name__ == "__main__":
    main()
