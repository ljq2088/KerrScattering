"""Basic smoke test for GF adaptive match computation."""
import sys
import os
import warnings
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.gf_adaptive_match import compute

warnings.filterwarnings("ignore")


def test_basic_run():
    """Verify the default-parameter computation runs and produces finite results."""
    result = compute(M=1.0, l=0, omega=1e-3, N=64, Cl=1.0)

    assert result["status"] == "ok"
    assert np.isfinite(result["T"])
    assert np.isfinite(result["R"])
    assert np.isfinite(result["C_id"])
    assert np.isfinite(result["C_iu"])
    assert result["T"] >= 0
    assert result["R"] >= 0


def test_high_frequency():
    """Verify high-frequency regime (no AnMR) runs."""
    result = compute(M=1.0, l=0, omega=0.5, N=64, Cl=1.0)
    assert result["status"] == "ok"
    assert np.isfinite(result["T"])
    assert np.isfinite(result["R"])


def test_matching_quality():
    """Verify matching error is small."""
    result = compute(M=1.0, l=0, omega=0.1, N=64, Cl=1.0)
    assert result["matching_error"] < 1e-4


def test_nonlinear_outputs():
    """Verify nonlinear corrections are finite."""
    result = compute(M=1.0, l=0, omega=0.05, N=64, Cl=1.0)
    assert np.isfinite(result["T1"])
    assert np.isfinite(result["R1"])
    assert np.isfinite(result["A1out"])
    assert np.isfinite(result["A1in"])
