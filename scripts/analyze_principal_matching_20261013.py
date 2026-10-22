"""Parameter-free near-extremal scalar principal-channel matching test.

M=1, y=p/kappa=0.5. Hypergeometric near solutions and Whittaker far
connection coefficients determine the response including log-phase mixing.
The independent full Kerr datasets use the corrected spectral endpoints.
"""
import csv
import json
import hashlib
import os
from pathlib import Path
import sys

for name in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[name] = "1"
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import mpmath as mp
import numpy as np
from src.teukolsky_scalar import scalar_spheroidal_eigenvalue, scalar_power_coupling
from scripts.run_kerr_scalar_nonlinear_diagnostics import require_memory_room

mp.mp.dps = 32


def near_data(l=2, m=2, y=0.5):
    eigenvalue = scalar_spheroidal_eigenvalue(l, m, m/2)
    h = mp.mpf('0.5') + mp.sqrt(mp.mpf('0.25') + eigenvalue - 7*m*m/4)
    if abs(mp.re(h)-mp.mpf('0.5')) > mp.mpf('1e-20') or mp.im(h) == 0:
        raise ValueError("This test retains both principal branches")
    a, b, c = h-1j*m, 1-h-1j*m, 1-1j*y
    cp = mp.gamma(c)*mp.gamma(2*h-1)/(mp.gamma(a)*mp.gamma(h-1j*(y-m)))
    cm = mp.gamma(c)*mp.gamma(1-2*h)/(mp.gamma(b)*mp.gamma(1-h-1j*(y-m)))

    def f(x):
        x = mp.mpf(x)
        if x <= 2:
            return x**(-1j*y/2)*(1+x)**(1j*(y/2-m))*mp.hyp2f1(a,b,c,-x)
        return (1+1/x)**(1j*(y/2-m))*(
            cm*x**(-h)*mp.hyp2f1(a, a+1j*y, 2*h, -1/x)
            + cp*x**(h-1)*mp.hyp2f1(b, b+1j*y, 2-2*h, -1/x))

    lam = eigenvalue-3*m*m/4
    residuals = []
    for x in (mp.mpf('0.1'), mp.mpf('1'), mp.mpf('10')):
        terms = (x*(x+1)*mp.diff(f,x,2), (2*x+1)*mp.diff(f,x),
                 ((m*x+y/2)**2/(x*(x+1))-lam)*f(x))
        residuals.append(float(abs(sum(terms))/sum(abs(t) for t in terms)))
    assert max(residuals) < 1e-20, residuals
    up = mp.gamma(2*h)/mp.gamma(h-1j*m)*(-1j*m)**(-h-1j*m)
    um = mp.gamma(2-2*h)/mp.gamma(1-h-1j*m)*(-1j*m)**(h-1-1j*m)
    gp = mp.gamma(1-2*h)/mp.gamma(1-h-1j*m)*(-1j*m)**h
    gm = mp.gamma(2*h-1)/mp.gamma(h-1j*m)*(-1j*m)**(1-h)
    return dict(h=complex(h), cp=complex(cp), cm=complex(cm),
                up=complex(up), um=complex(um), gp=complex(gp), gm=complex(gm),
                f=f, ode_residuals=residuals, eigenvalue=eigenvalue)


def source_integrals(data, order):
    gx, gw = np.polynomial.legendre.leggauss(order)
    totals = {n: [0j, 0.0] for n in (1,2)}
    for left in range(-36,36):
        require_memory_room(900, "near-zone analytic quadrature")
        t = left+0.5+0.5*gx
        x = np.exp(t)
        f = np.asarray([complex(data['f'](float(v))) for v in x])
        weight = 0.5*gw*x
        for n in (1,2):
            totals[n][0] += np.sum(weight*f*f*abs(f)**(2*n))
            totals[n][1] += float(np.sum(weight*abs(f)**(2*n+2)))
    return totals


def main():
    data = near_data()
    integrals_low = source_integrals(data, 12)
    integrals = source_integrals(data, 20)
    errors = {str(n): max(abs(v-w)/max(abs(w),1e-300)
                         for v,w in zip(integrals_low[n],integrals[n])) for n in (1,2)}
    assert max(errors.values()) < 1e-8, errors
    print('h=',data['h'],'near integral checks=',errors,flush=True)
    print('ODE residuals=',data['ode_residuals'],flush=True)
    rows = []
    beta = data['h'].imag
    y, m, l = 0.5, 2, 2
    det = abs(data['cp'])**2-abs(data['cm'])**2
    assert abs(det+y/(2*beta)) < 1e-12
    couplings = {n: float(np.real(sum(scalar_power_coupling(l,m,1,m/2,n,cos_power=j)
                                          for j in (0,2)))) for n in (1,2)}
    for degree in (256,320,384,448):
        path = ROOT / f'results/kerr_scalar_principal_relation_20261013_N{degree}.csv'
        with path.open(newline='',encoding='utf8') as handle:
            source_rows = list(csv.DictReader(handle))
        for raw in source_rows:
            if int(raw['l']) != l or int(raw['m']) != m:
                continue
            n = int(raw['nonlinearity_order'])
            spin = float(raw['a'])
            sigma = 2*np.sqrt(1-spin*spin)
            phase = np.exp(1j*beta*np.log(sigma))
            D = data['cp']*data['up']/phase + data['cm']*data['um']*phase
            gamma_p, gamma_m = data['gp']*phase, data['gm']/phase
            aa = (gamma_p*data['cp'].conjugate()-gamma_m*data['cm'].conjugate())/det
            bb = (-gamma_p*data['cm']+gamma_m*data['cp'])/det
            ios, iabs = integrals[n]
            AH = 1j*couplings[n]/y*(aa/bb*ios+iabs)
            predicted_chi = 2*AH.real/(sigma**n*abs(D)**(2*n))
            predicted_T0 = y/(m*abs(D)**2)
            observed = float(raw['horizon_response'])
            row = dict(a=spin, l=l, m=m, n=n, y=y, N=degree, sigma=sigma,
                       kappa=float(raw['surface_gravity']), chi=observed,
                       chi_matched=predicted_chi,
                       matched_chi_relative_error=abs(observed-predicted_chi)/abs(observed),
                       T0=float(raw['T0']), T0_matched=predicted_T0,
                       nonlinear_balance=float(raw['nonlinear_balance']),
                       two_boundary_flux_accepted=abs(float(raw['nonlinear_balance']))<=1e-8,
                       scaled_sigma_response=sigma**n*observed,
                       scaled_sigma_response_matched=2*AH.real/abs(D)**(2*n),
                       green_coefficient_real=AH.real, green_coefficient_imag=AH.imag)
            rows.append(row)
            print(row,flush=True)
    output = ROOT / 'results/kerr_scalar_principal_matched_prediction_20261013.csv'
    with output.open('w',newline='',encoding='utf8') as handle:
        writer = csv.DictWriter(handle,fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    indexed = {(int(r['N']),float(r['a']),int(r['n'])):r for r in rows}
    paired = []
    for coarse,fine in ((256,320),(384,448)):
        for (degree,spin,n), row in indexed.items():
            if degree != fine or (coarse,spin,n) not in indexed:
                continue
            reference = indexed[(coarse,spin,n)]
            paired.append(dict(N_coarse=coarse,N_fine=fine,a=spin,n=n,
                               relative_change=abs(row['chi']-reference['chi'])/abs(row['chi'])))
    report = dict(h_real=data['h'].real,h_imag=data['h'].imag,
                  eigenvalue=data['eigenvalue'],near_ode_relative_residuals=data['ode_residuals'],
                  integral_relative_checks=errors,mp_decimal_digits=mp.mp.dps,
                  log_X_interval=[-36,36],gauss_orders=[12,20],source_couplings=couplings,
                  paired_response_convergence=paired,
                  fitted_parameters=0,
                  source_sha256={str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                                 for path in [ROOT/'src/kerr_scalar_spectral.py',
                                              ROOT/'src/kerr_scalar_nonlinear.py',
                                              ROOT/'src/teukolsky_scalar.py',
                                              Path(__file__).resolve()]},
                  input_sha256={str(path.relative_to(ROOT)):hashlib.sha256(path.read_bytes()).hexdigest()
                                for path in [ROOT/f'results/kerr_scalar_principal_relation_20261013_N{N}.csv'
                                             for N in (256,320,384,448)]},
                  analytic_scope='Leading principal self-channel matching; y=0.5; n=1,2')
    (ROOT/'results/kerr_scalar_principal_matching_checks_20261013.json').write_text(
        json.dumps(report,indent=2),encoding='utf8')


if __name__ == '__main__':
    main()
