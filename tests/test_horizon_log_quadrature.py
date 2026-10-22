import numpy as np
import pytest
from src.teukolsky_scalar import KerrParams, rstar
from src.kerr_scalar_nonlinear import _rstar_horizon_distance, _horizon_log_rule


@pytest.mark.parametrize('a', [0, 0.5, 0.999999])
def test_stable_tortoise_agrees_with_existing_convention(a):
    params = KerrParams(M=1, a=a)
    s = np.array([0.1, 1, 12])
    np.testing.assert_allclose(_rstar_horizon_distance(s, params), rstar(params.rp+s,a=a),
                               rtol=2e-12, atol=2e-11)
    assert np.all(np.isfinite(_rstar_horizon_distance(np.array([1e-25]),params)))


@pytest.mark.parametrize('y', [-2, -0.5, 0.5, 1, 4])
def test_log_rule_with_analytic_mellin_endpoint(y):
    params = KerrParams(M=1, a=0.999999)
    gap = params.rp-params.rm
    distance, weights, cutoff = _horizon_log_rule(params, 12, 32, -30)
    actual = np.sum(weights*(distance/gap)**(-1j*y))
    actual += cutoff*(cutoff/gap)**(-1j*y)/(1-1j*y)
    upper = 12-params.rp
    expected = upper*(upper/gap)**(-1j*y)/(1-1j*y)
    assert abs(actual-expected)/abs(expected) < 2e-13
