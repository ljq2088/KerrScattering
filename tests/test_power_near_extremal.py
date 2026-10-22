import numpy as np

from scripts.analyze_kerr_scalar_power_near_extremal import (
    PairedValue,
    power_fit,
    threshold_extrapolation,
)
from scripts.analyze_kerr_scalar_cft_factorization import (
    power_fit as factorization_power_fit,
)
from scripts.run_kerr_scalar_power_near_extremal import (
    comma_positive_integers,
    row_key,
)


def paired_value(n: int, y: float, response: float) -> PairedValue:
    return PairedValue(
        n=n,
        a=0.999,
        l=2,
        m=2,
        kappa=0.0213983642361842,
        y=y,
        response=response,
        response_low=response,
        resolution_change=0.0,
        linear_balance=0.0,
        nonlinear_balance=0.0,
        nonlinear_relative_balance=0.0,
        wronskian_error=0.0,
        accepted=True,
    )


def test_power_runner_order_parser_and_checkpoint_key():
    assert comma_positive_integers("1,2,5") == [1, 2, 5]
    row = {
        "nonlinearity_order": "3",
        "a": "0.999",
        "l": "2",
        "m": "2",
        "detuning_over_kappa": "0.025",
    }
    assert row_key(row) == (3, 0.999, 2, 2, 0.025)


def test_higher_power_threshold_extrapolation_removes_quadratic_term():
    n = 3
    c0 = 0.73
    c2 = 2.4
    values = {
        (n, 0.999, 2, 2, y): paired_value(n, y, c0 + c2 * y**2)
        for y in (-0.05, -0.025, 0.025, 0.05)
    }
    rows = threshold_extrapolation(values)
    assert len(rows) == 1
    assert rows[0]["accepted"] == "true"
    assert abs(float(rows[0]["horizon_response"]) - c0) < 1.0e-14


def test_higher_power_fit_recovers_order_locked_exponent():
    n = 3
    kappa = np.geomspace(0.007, 0.08, 7)
    rows = [
        {"surface_gravity": value, "horizon_response": 0.013 * value**-n}
        for value in kappa
    ]
    fit = power_fit(rows)
    assert abs(fit["amplitude"] - 0.013) < 1.0e-13
    assert abs(fit["alpha"] - n) < 1.0e-13
    assert fit["r_squared"] > 1.0 - 1.0e-14
    assert fit["alpha_ci95_low"] <= n <= fit["alpha_ci95_high"]
    assert fit["loo_max_relative_prediction_error"] < 1.0e-12


def test_cft_factorization_exponent_closure():
    n = 2
    kappa = np.geomspace(0.007, 0.08, 7)
    intensity = 0.4 * kappa**-0.9
    kernel = 0.2 * kappa**-0.2
    response = intensity**n * kernel
    alpha_response, _ = factorization_power_fit(kappa, response)
    alpha_intensity, _ = factorization_power_fit(kappa, intensity)
    alpha_kernel, _ = factorization_power_fit(kappa, kernel)
    assert abs(alpha_response - n * alpha_intensity - alpha_kernel) < 1.0e-13
