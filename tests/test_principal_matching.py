"""Independent ODE and connection checks for the principal matching analysis."""
import mpmath as mp
import pytest
from scripts.analyze_principal_matching_20261013 import near_data


@pytest.mark.parametrize('m', [2, 3, 4])
@pytest.mark.parametrize('y', [-0.5, 0.5, 1.0])
def test_near_hypergeometric_solution_and_current(m, y):
    data = near_data(m, m, y)
    assert max(data['ode_residuals']) < 1e-20
    beta = data['h'].imag
    determinant = abs(data['cp'])**2-abs(data['cm'])**2
    assert abs(determinant+y/(2*beta)) < 1e-12


@pytest.mark.parametrize('m', [2, 3, 4])
def test_critical_whittaker_solutions(m):
    data = near_data(m, m, 0.5)
    h = mp.mpc(data['h'])
    lam = mp.mpf(data['eigenvalue'])-3*m*m/4
    for index in (h,1-h):
        def R(u):
            return (-1j*m)**(-index)*mp.whitm(1j*m,index-mp.mpf('0.5'),-1j*m*u)/u
        for u in (mp.mpf('0.3'),mp.mpf('1'),mp.mpf('4')):
            terms = (u*u*mp.diff(R,u,2),2*u*mp.diff(R,u),
                     (m*m*(1+u/2)**2-lam)*R(u))
            assert abs(sum(terms))/sum(abs(t) for t in terms) < mp.mpf('1e-13')
