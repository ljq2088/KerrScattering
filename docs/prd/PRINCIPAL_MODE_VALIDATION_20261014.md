# Principal-Mode Validation: October 14, 2026

## Scope

The complex scalar interaction is |Phi|^(2n) Phi on a fixed Kerr background.
The observable is the fixed-incident self-channel horizon response
hat_chi_n = M^(2n-2) T_n^(1)/T^(0). Calculations cover l=m=2,3,4;
n=1,2,3; y=p/kappa=-0.5,0.5,1; and a/M=0.9999,0.99999,0.999999.
The Cartesian grid contains 81 distinct physical points and four resolution
settings give 324 completed calls. Each sampled solver RSS was approximately
80 MB, with one BLAS thread and a 900 MB guard.

## Analytic Chain

1. The near radial indicial equation fixes h=1/2+i beta for principal modes.
2. Hypergeometric continuation supplies both overlap coefficients.
3. Critical-frequency Whittaker solutions connect those branches to
   asymptotically flat incident radiation.
4. B_inc = sigma^(1/2) D(beta log sigma) at leading order, giving a
   fixed-incident throat density proportional to sigma^(-1).
5. The covariant nonlinear Green integral has an X^(-n-1) upper envelope.
   It converges for every positive integer n.
6. Incident normalization gives hat_chi_n = sigma^(-n) F_n(y,beta log sigma)
   + o(sigma^(-n)); F_n has analytic log-period pi/beta.

These are leading near-extremal hypergeometric/Whittaker connections. The
MST references describe the full-frequency series structure. The present
calculation evaluates the leading matching coefficient with zero fitted
parameters. Numerical tests of the analytic ODE, current, integral
refinement and period are retained in the analytic-check CSV.

## Independent Numerical Checks

Production: N=448, q=3072, matching radius 12M.
Spectral refinement: N=384 to 448 at fixed q=3072.
Quadrature refinement: q=1536 to 3072 at fixed N=448.
Additional initial scan: N=384, q=1024.
The horizon and infinity remain exact collocation endpoints.
Residual denominators include all local field-weighted equation terms.

All 81 points pass the uniform principal-grid criteria. Maximum relative
spectral change: 6.55e-9. Maximum quadrature change: 7.81e-5.
Maximum homogeneous off-grid radial residual: 1.37e-8.
Maximum relative Chebyshev coefficient tail: 6.82e-14.
Maximum normalized first-order flux-balance error: 2.47e-9.
The original absolute 1e-8 flux gate passes 60 points, recorded separately.
Absolute flux discrepancies and physical coupling/amplitude factors remain
explicit in the manuscript and CSV rather than combined with relative gates.

At a/M=0.999999 the analytic leading-coefficient differences range from
0.030% to 2.422%. These finite-sigma matching differences are distinct from
the numerical refinement changes. Three spins per series test the predicted
coefficient at finite sigma. The logarithmic period is derived analytically;
a dense full-Kerr numerical measurement of each period remains a further
test. The figure's dense lines are analytic evaluations and its circles are
independent spectral calculations.

## Claim And Perturbative Domain

The principal envelope depends on Re h=1/2, and Im h determines the
two-branch logarithmic phase. Both branches and the nonlinear integral are
included in the coefficient. Real weights have a different source-convergence
classification: 1/2<h<1 gives a convergent throat power; h=1 gives logarithmic
upper behavior; h>1 requires the outer contribution at leading order.
The complex horizon correction controls both amplitude and phase. Its
perturbative parameter has a typical principal envelope
|g_n| |A_in|^(2n) (M kappa)^(-n), on nonresonant compact parameter sets.
Saturation, time-domain dynamics and gravitational backreaction require
extensions beyond the computed first-order response.

## Reproduction

Run `scripts/validate_principal_expanded_20261014.py`, then
`scripts/plot_principal_expanded_20261014.py`, then the current manuscript
builder and local pdflatex commands in README.md. The validation manifest
records input hashes. `scripts/check_prd_review_20261007.py` verifies source
preservation, tables, metadata, numerical manifests and PDF bounds.
`scripts/render_principal_paper_20261014.py` renders every page for visual QA.
The full test suite passed 49 tests, with two pre-existing Schwarzschild
oscillatory-quadrature warnings in `test_basic_run`.
