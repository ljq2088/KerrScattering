"""Providers for Teukolsky angular/radial separation constants."""

from dataclasses import dataclass
import json
import re
import shlex
import subprocess


DEFAULT_WSL_DISTRO = "Ubuntu-22.04-D"
DEFAULT_WSL_HELPER = "/home/ljq/code/PINN/SolvingTeukolskyEq_autoencoder/utils/compute_lambda_usage.py"
DEFAULT_GSN_PROJECT = "/home/ljq/code/GSN/GeneralizedSasakiNakamura.jl"
DEFAULT_JULIA = "/home/ljq/julia-1.10.7/bin/julia"


@dataclass(frozen=True)
class LambdaResult:
    """Separation-constant result with explicit convention metadata."""

    s: int
    l: int
    m: int
    a: float
    omega: float
    value: complex
    provider: str
    convention: str
    status: str = "ok"


def _run_wsl(command, distro=DEFAULT_WSL_DISTRO, timeout=120):
    cmd = ["wsl", "-d", distro, "-e", "bash", "-lc", command]
    proc = subprocess.run(
        cmd,
        text=True,
        capture_output=True,
        timeout=timeout,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or proc.stdout.strip())
    return proc.stdout.strip()


def _parse_complex(text):
    text = text.strip()
    try:
        return complex(text)
    except ValueError:
        pass

    julia = re.fullmatch(
        r"\s*([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)\s*"
        r"([+-])\s*"
        r"((?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)im\s*",
        text,
    )
    if julia:
        real = float(julia.group(1))
        imag = float(julia.group(3))
        if julia.group(2) == "-":
            imag = -imag
        return complex(real, imag)

    raise ValueError(f"Cannot parse complex value: {text!r}")


def local_scalar_lambda(l, m, a, omega, lmax_extra=16):
    """Compute the s=0 radial lambda with the local matrix fallback."""
    from .teukolsky_scalar import teukolsky_lambda_s0

    val = teukolsky_lambda_s0(l=l, m=m, a=a, omega=omega, lmax_extra=lmax_extra)
    return LambdaResult(
        s=0,
        l=l,
        m=m,
        a=a,
        omega=omega,
        value=val,
        provider="local-scalar-matrix",
        convention="lambda = A_lm + a^2 omega^2 - 2 a m omega for s=0",
    )


def wsl_helper_lambda(s, l, m, a, omega, helper=DEFAULT_WSL_HELPER,
                      distro=DEFAULT_WSL_DISTRO):
    """Compute lambda through the user's WSL Python helper."""
    payload = {
        "helper": helper,
        "s": s,
        "l": l,
        "m": m,
        "a": a,
        "omega": omega,
    }
    script = f"""
import importlib.util, json
payload = json.loads({json.dumps(json.dumps(payload))})
spec = importlib.util.spec_from_file_location("compute_lambda_usage", payload["helper"])
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
val = module.compute_lambda(payload["a"], payload["omega"], payload["l"], payload["m"], payload["s"])
print(repr(complex(val)))
"""
    out = _run_wsl("python3 -c " + shlex.quote(script), distro=distro)
    return LambdaResult(
        s=s,
        l=l,
        m=m,
        a=a,
        omega=omega,
        value=_parse_complex(out),
        provider="wsl-helper",
        convention=f"helper={helper}; package returns Teukolsky radial lambda",
    )


def gsn_lambda(s, l, m, a, omega, julia=DEFAULT_JULIA,
               project=DEFAULT_GSN_PROJECT, distro=DEFAULT_WSL_DISTRO):
    """Compute lambda through GeneralizedSasakiNakamura.jl in WSL."""
    code = (
        "using Pkg; "
        f"Pkg.activate({json.dumps(project)}; io=devnull); "
        "using GeneralizedSasakiNakamura; "
        f"val = GeneralizedSasakiNakamura.spin_weighted_spheroidal_eigenvalue({s},{l},{m},{a}*{omega}); "
        "println(repr(complex(val)))"
    )
    out = _run_wsl(shlex.quote(julia) + " -e " + shlex.quote(code),
                   distro=distro, timeout=180)
    return LambdaResult(
        s=s,
        l=l,
        m=m,
        a=a,
        omega=omega,
        value=_parse_complex(out),
        provider="gsn",
        convention="GeneralizedSasakiNakamura.jl Teukolsky radial lambda",
    )


def compute_teukolsky_lambda(s, l, m, a, omega, provider="auto", **kwargs):
    """Compute a Teukolsky separation constant through a named provider.

    provider options:
      - auto: local matrix for s=0, WSL helper otherwise
      - local: local scalar matrix method; only valid for s=0
      - wsl-helper: user's Python helper in WSL
      - gsn: GeneralizedSasakiNakamura.jl
    """
    if provider == "auto":
        provider = "local" if s == 0 else "wsl-helper"

    if provider == "local":
        if s != 0:
            raise ValueError("The local provider currently supports only s=0.")
        return local_scalar_lambda(l, m, a, omega, **kwargs)
    if provider == "wsl-helper":
        return wsl_helper_lambda(s, l, m, a, omega, **kwargs)
    if provider == "gsn":
        return gsn_lambda(s, l, m, a, omega, **kwargs)
    raise ValueError(f"Unknown lambda provider: {provider}")
