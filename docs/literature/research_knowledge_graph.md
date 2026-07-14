# Research knowledge graph

This graph is an implementation map, not a claim that every downstream
module already exists.

## Physics dependency graph

```text
Kerr background
  -> geodesic orbit and constants (E, Lz, Q)
  -> fundamental frequencies (Omega_r, Omega_theta, Omega_phi)
  -> source harmonics (l,m,k,n)
  -> separated field equation
  -> homogeneous solutions and connection amplitudes
  -> Green-function response and fluxes
  -> orbit evolution
  -> waveform and detector response
```

Current coverage is the fixed-background scalar radial problem and a weak
cubic Green-function response. The geodesic, source-lattice, regularization,
orbit-evolution, and waveform layers remain future interfaces.

The current frontier has three independent error axes:

```text
physical order:       adiabatic -> post-adiabatic -> second order
field discretization: spectral/DG order -> residual -> observable
model reduction:      mode/source truncation -> orbit phase -> detector response
```

They must not be collapsed into one number. A radial residual can be tiny
while a truncated `(l,m,k,n)` source lattice or an adiabatic approximation
still produces a large accumulated waveform phase error.

## Four small parameters that must not be conflated

| Layer | Parameter | Meaning | Current status |
|---|---|---|---|
| Prescribed field | `epsilon` | Weak scalar self-interaction | Implemented for `s=0` |
| EMRI source | `eta = mu/M` | Small-body mass ratio | Not implemented |
| Self-force order | `h = eta h1 + eta^2 h2 + ...` | Metric/field perturbation | Not implemented |
| Long-time evolution | `T = eta t` | Slow orbital evolution | Not implemented |

Thus `A^(1)` in the active manuscript means a scalar response coefficient.
It must not be renamed as a gravitational self-force or mass-ratio waveform
coefficient.

## Numerical validation graph

1. **Equation:** endpoint relations, field-dependent radial residual, and
   Wronskian identity.
2. **Spectrum:** Chebyshev coefficient tails, order refinement, matching-radius
   changes, and conditioning/scaling diagnostics.
3. **Amplitudes:** `B_inc`, `B_ref`, horizon amplitude, and normalization-invariant
   ratios.
4. **Flux:** infinity plus horizon balance and perturbative order bookkeeping.
5. **Orbit/waveform:** source-lattice truncation, orbital evolution, and
   accumulated phase error. These are not covered by the active manuscript.

## Interfaces to build next

```text
RadialConvention(s, M, a, FourierSign, radialVariable, lambdaConvention)
HomogeneousSolution(Rin, Rup, Binc, Bref, horizonAmplitude, Wronskian)
Response(sourceProjection, A1, fluxes, residuals)
OrbitConstants(E, Lz, Q, p, e, thetaMinus)
Frequencies(OmegaR, OmegaTheta, OmegaPhi, Gamma)
ModeLabel(l, m, k, n, omega_mkn)
RegularField(singularPart, regularPart, gauge, regularizationData)
```

Each interface needs explicit conventions and an observable-level validation
before it can feed the next layer.

## Research readiness gate

Before adding an EMRI or gravitational-self-force module, require:

1. `eta`, slow time, perturbative order, and gauge are declared.
2. The source mode lattice and its truncation error are recorded.
3. Homogeneous amplitudes, Wronskian, and flux normalization pass the
   existing radial checks.
4. If a worldline source is present, a singular/regular split and
   regularization tail are implemented.
5. Orbit, field, and waveform errors are propagated to an accumulated phase
   observable.

The active scalar manuscript passes only the fixed-background radial and
smooth-source portions of this gate.
