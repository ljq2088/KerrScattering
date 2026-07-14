# Convention ledger for literature transfer

This ledger is deliberately explicit. Never identify symbols across papers
until each row has been checked.

| Quantity | KerrScattering working convention | Must be checked in external work |
|---|---|---|
| Units | Geometric units, `G=c=1`, usually `M=1` | Whether `M=1`, `2M=1`, or dimensional units are used |
| Fourier sign | Project convention recorded in the active derivation | Whether fields use `exp(-i omega t)` or `exp(+i omega t)` |
| Spin | Active manuscript: scalar `s=0` | Teukolsky `s`, Newman--Penrose scalar, or metric perturbation variable |
| Angular label | Spheroidal mode `(ell,m)` | Spherical versus spheroidal harmonics and eigenvalue shift |
| Separation constant | Local `lambda` convention in `src/teukolsky_scalar.py` | `A_lm`, `E_lm`, `lambda`, and shifts by `a^2 omega^2-2am omega` |
| Radial coordinate | Endpoint-inclusive compactification `z=r_+/r` | Boyer--Lindquist `r`, tortoise `r_*`, hyperboloidal radius, or GSN radius |
| Horizon basis | `R_in` is ingoing at the future horizon | Whether the paper factors out the horizon phase or uses a rescaled Teukolsky variable |
| Infinity basis | `B_inc`, `B_ref` are extracted by asymptotic matching | Incoming/outgoing labels and phase conventions |
| Wronskian | Green-function normalization fixed by the two homogeneous solutions | Sign, radial measure, and whether a source weight is absorbed into `W` |
| Nonlinear coefficient | `A^(1)` is a response coefficient; physical correction is `epsilon A^(1)` | Whether `A^(1)` denotes a field, a metric coefficient, a mode amplitude, or a force |
| Flux | Fluxes are quadratic field observables on fixed Kerr | Gravitational energy flux, horizon area flux, canonical energy, or local self-force power |
| Self-force parameter | Not present in active scalar problem | `eta=mu/M`, regular field, puncture order, and gauge |

## Required comparison record

Every benchmark comparison should store:

- the external code, commit/version, and exact invocation;
- the conversion map for `omega`, `lambda`, `R`, and amplitudes;
- the normalization used before comparing raw complex values;
- the physical invariant compared: amplitude ratio, flux, Wronskian, or
  residual;
- the precision and cancellation diagnostics.

This prevents a normalization mismatch from being misreported as a solver
failure or as a physical discrepancy.
