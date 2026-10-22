import numpy as np

from scripts.analyze_kerr_scalar_modal_powerlaws import (
    PairedValue,
    conformal_data,
    power_fit,
    threshold_extrapolation,
)


def paired_value(y: float, response: float) -> PairedValue:
    return PairedValue(
        a=0.99,
        l=2,
        m=2,
        kappa=0.06181377400094834,
        y=y,
        response=response,
        response_low=response,
        resolution_change=0.0,
        linear_balance=0.0,
        nonlinear_balance=0.0,
        wronskian_error=0.0,
        accepted=True,
    )


def test_threshold_extrapolation_removes_even_quadratic_term():
    c0 = 0.47
    c2 = 1.9
    values = {
        (0.99, 2, 2, y): paired_value(y, c0 + c2 * y**2)
        for y in (-0.05, -0.025, 0.025, 0.05)
    }
    rows = threshold_extrapolation(values)
    assert len(rows) == 1
    assert rows[0]["accepted"] == "true"
    assert abs(float(rows[0]["horizon_response"]) - c0) < 1.0e-14


def test_power_fit_recovers_known_exponent():
    kappa = np.geomspace(0.007, 0.08, 7)
    response = 0.029 * kappa**-1.0
    fit = power_fit(kappa, response)
    assert abs(fit["amplitude"] - 0.029) < 1.0e-14
    assert abs(fit["alpha"] - 1.0) < 1.0e-14
    assert fit["r_squared"] > 1.0 - 1.0e-14


def test_extremal_conformal_classes_separate_modal_families():
    assert conformal_data(2, 2)[3] == "principal_complex_h"
    assert conformal_data(3, 3)[3] == "principal_complex_h"
    assert conformal_data(1, 1)[3] == "supplementary_real_h"
    assert conformal_data(2, 1)[3] == "supplementary_real_h"
