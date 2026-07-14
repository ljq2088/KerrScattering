# Deep-reading curriculum for Kerr, EMRI, gravitational waves, and self-force

This document is the maintained research map for the project. It is a
technical reading protocol, not a claim that the active scalar calculation is
already a gravitational self-force calculation.

## 1. Conceptual separation

The project contains four related but distinct layers:

1. **Fixed-background black-hole perturbation theory.** Solve a linearized
   field equation on a prescribed Schwarzschild or Kerr geometry. The active
   implementation is the scalar Teukolsky equation with `s=0`.
2. **Prescribed-field nonlinear response.** Insert a weak nonlinear source,
   here schematically `Box Phi + epsilon |Phi|^2 Phi = 0`, and compute the
   first response coefficient with a Green function. This changes the field
   equation but does not change the background metric or the source worldline.
3. **Gravitational self-force.** Expand the metric and the small body's motion
   in the mass ratio `eta = mu/M`, split the retarded field into singular and
   regular pieces, and derive a corrected worldline. Gauge, regularization, and
   second-order consistency are essential.
4. **EMRI waveform modelling.** Combine geodesic orbits, dissipative and
   conservative self-force, resonances, multiscale evolution, and waveform
   generation. A highly accurate single-frequency amplitude is only one input
   to this layer.

The agent must state which layer a statement belongs to before transferring a
formula or a numerical diagnostic between papers.

## 2. Reading tracks

### Track A: Kerr perturbation theory and scattering

Read Sasaki--Tagoshi and the MST papers together with the local scalar
Teukolsky derivation. Extract the spin convention, Fourier sign, angular
eigenvalue convention, radial variable, horizon exponent, infinity basis, and
the normalization of `B_inc`, `B_ref`, and the transmitted amplitude. Then
compare the direct Teukolsky solver against GSN, not by comparing raw solution
normalizations but by comparing invariant amplitude ratios and fluxes.

**Transfer to this repository:** maintain a convention ledger, add endpoint
equations to the matrix, and test the same physical solution under a change of
radial normalization.

### Track B: EMRI orbital mechanics and waveform accuracy

Read the EMRI overview and the Pound--Ward review after the Kerr track. Focus
on action-angle variables, the three fundamental Kerr frequencies, resonances,
adiabatic versus post-adiabatic evolution, and near-identity transformations.
Then read the FastEMRIWaveforms and eccentric/spinning-body papers as
implementation studies.

**Transfer:** the current frequency sweep is a fixed-frequency module. A
future EMRI module must expose orbital frequencies, mode labels, source
Fourier coefficients, and accumulated phase error separately from the local
radial amplitude error.

### Track C: Green functions, radiation reaction, and self-force

Read Poisson--Pound--Vega for the singular/regular field construction,
Barack--Pound for the full self-force workflow, and the Pound papers for
second-order motion and the choice of worldline representation. Read the
Barack--Sago flux-balance paper as a numerical validation pattern: dissipative
quantities can be checked against infinity plus horizon flux, while the local
conservative force requires a separate regularization and gauge analysis.

**Transfer:** the current nonlinear Green-function Wronskian and flux balance
are reusable numerical structures, but the cubic scalar source is not the
gravitational singular source and `A^(1)` is not a self-force vector.

### Track D: second order, nonlinear Teukolsky, and ringdown

Read the second-order Teukolsky formulation and the Kerr conserved-current/QNM
work together. Track the distinction between a driven frequency-domain
response, a second-order metric perturbation, and a QNM projection. Pay
particular attention to outgoing boundary conditions, infrared/memory terms,
non-Hermitian mode normalization, and the order at which a background mass or
spin shift feeds back into the spectrum.

**Transfer:** the present Lorentzian peak fit is descriptive only. It must not
be called a QNM excitation coefficient unless the appropriate Kerr bilinear
projection and analytic continuation are implemented.

### Track E: nonlinear scattering and effective-source numerics

Read the recent nonlinear-gravity scattering work together with the
frequency-domain effective-source prototype. The former is useful for
identifying harmonic generation and spectral broadening; the latter is useful
for understanding how extended particular solutions can control Fourier-mode
reconstruction in an eccentric problem.

**Transfer:** use these papers to design two separate future tests: (i) target
channel generation and frequency mixing in a genuinely time-dependent scalar
calculation, and (ii) an effective-source toy problem with a controlled local
singularity. Neither test changes the interpretation of the present fixed-
background cubic coefficient.

### Track F: EMRI accuracy and the second-order frontier

Read the relativistic-waveform, post-adiabatic-environment, and
numerical-relativity self-force papers after Tracks B and C. The key
distinction is between (i) improving the physical approximation order, (ii)
improving the radial/field discretization, and (iii) accelerating a waveform
model for inference. A fast waveform is not automatically a high-order
self-force waveform.

The central bookkeeping is

```text
eta = mu/M
g = g_Kerr + eta h^(1) + eta^2 h^(2) + ...
T = eta t
dJ/dT = F^(0)(J) + eta F^(1)(J, q) + ...
Phi(t) = eta^(-1) Phi_(-1)(T) + Phi_(0)(T) + ...
```

For a generic bound Kerr orbit, the source frequencies remain
`omega_mkn = m Omega_phi + k Omega_theta + n Omega_r`. The radial solver
therefore sees a discrete mode lattice, while the inspiral module evolves
the actions and phases on the slow time. Near a transient resonance,
`n Omega_r + k Omega_theta = 0`, the ordinary adiabatic averaging is
insufficient and a jump in the actions can feed an order-one phase error
over the remaining inspiral.

The 2024 relativistic-waveform work is the inference-facing benchmark:
compare relativistic and approximate waveform phase, parameter bias, and
environmental distinguishability. The 2025 post-adiabatic work is the
approximation-order benchmark: isolate the first correction to the slow
evolution. The 2026 DG/AMR work is the discretization/algorithm benchmark:
test exponential convergence, horizon regularity, and generic-orbit
scalability in a nonseparable setting.

**Transfer:** add an orbit/source layer only after the present radial API
returns convention-tagged amplitudes and fluxes. Every EMRI run should report
radial spectral error, source-lattice truncation, orbit integrator error, and
accumulated phase error as separate entries.

### Track G: self-force regularization and gauge discipline

Read Poisson--Pound--Vega and Barack--Pound before any gravitational
interpretation of the scalar experiments. The retarded field is decomposed
schematically as

```text
h_ret = h_S + h_R
F_self^mu = functional[h_R, u^mu, curvature]
```

The singular field is locally determined and is not a physical force. In a
mode-sum implementation one subtracts the large-`l` singular asymptotics
before summing the residual modes. The regular field and the force are gauge
dependent, whereas suitably defined fluxes and certain redshift/frequency
invariants can provide cleaner comparisons.

**Transfer:** the current field-dependent radial residual is a sound
discretization diagnostic, but it is not a regularization prescription. The
nonlinear scalar source is smooth and prescribed; it does not require
Detweiler--Whiting subtraction, puncture fields, or a self-consistent
worldline.

## 3. Paper-card protocol

For every paper in `seed_arxiv_ids.txt`, create or update a card containing:

- identifier, version, publication status, and primary link;
- background, small parameter, and perturbative order;
- metric signature, Fourier convention, gauge, tetrad, radial variable, and
  angular eigenvalue convention;
- main differential equation and the exact endpoint conditions;
- Green-function or Wronskian normalization;
- numerical method, precision controls, and independent benchmark;
- which result can be transferred to KerrScattering;
- which assumption is incompatible with the active scalar problem;
- one new experiment that would test the transfer.

The card is considered complete only when the last three items are filled.

## 4. Current high-priority cards

| Module | Primary source | Immediate lesson |
|---|---|---|
| MST | `gr-qc/9603020` | Use analytic connection formulas as a low-frequency normalization audit. |
| GSN | `2306.16469` | Compare Teukolsky and GSN homogeneous solutions through physical amplitudes and fluxes. |
| Self-force review | `1805.10385` | Keep dissipative flux, local conservative force, gauge, and regularization distinct. |
| Unified BHPT/GSF | `2101.04592` | Treat orbit evolution and field solving as separate modules connected by source coefficients. |
| Second-order Teukolsky | `2305.19332` | A gravitational nonlinear source requires metric/tetrad/gauge structure absent from the scalar toy model. |
| Kerr QNM currents | `2210.15935` | Standard `L2` projection is not automatically valid for Kerr QNMs. |
| Self-force memory | `2410.23950` | Long-time observables can require near-zone/far-zone matching beyond a local frequency calculation. |
| Kerr geodesic frequencies | `gr-qc/0202090`, `0906.1420` | Build the orbit-frequency interface before introducing an EMRI source spectrum. |
| Generic-orbit Teukolsky fluxes | `0904.3810` | The source is a discrete `(l,m,k,n)` lattice and flux truncation is a separate error source. |
| Scalar self-force prototype | `1103.0287`, `1408.2885` | Extended homogeneous solutions and mode-sum regularization are distinct from a finite nonlinear Green source. |
| Generic Kerr gravitational self-force | `1711.09607`, `2209.05450` | Local reconstruction, regularization tails, and flux balance form a coupled but auditable validation chain. |
| Frequency-domain phase budget | `1409.4419` | Pointwise field accuracy must eventually be propagated into accumulated waveform phase error. |
| Nonlinear gravity scattering | `2603.04501` | Harmonic generation and spectral broadening must be distinguished from a single-frequency response fit. |
| Frequency-domain effective source | `2306.17221` | Extended particular solutions and regularization are a concrete bridge from scalar prototypes to EMRI self-force. |
| Relativistic EMRI waveform | `2410.17310` | Relativistic corrections can dominate inference systematics even at adiabatic order. |
| Post-adiabatic environmental EMRI | `2507.06923` | First post-adiabatic terms must be tracked through the accumulated phase, not only instantaneous fluxes. |
| Numerical-relativity self-force | `2606.04998` | DG/AMR and horizon-penetrating coordinates offer a complementary route for generic second-order Kerr self-force. |

## 5. Project-specific learning loop

For each new theoretical claim:

1. locate the exact source equation and its convention block;
2. write the conversion to the local `R`, `lambda`, and `B` conventions;
3. design a numerical test with a field-dependent residual denominator;
4. run order, matching-radius, quadrature, and normalization scans;
5. record the result in `results/literature/` and cite the source in the
   manuscript only after the metadata is verified.

The present project is ready for the first two tracks at the fixed-background
level. It is not yet an EMRI inspiral or a gravitational self-force code.

## 6. Knowledge graph and implementation gate

The cross-module dependency graph is maintained in
`docs/literature/research_knowledge_graph.md`. A new module is considered
scientifically ready only when it identifies its perturbative parameter,
convention block, source harmonics, boundary conditions, regularization status,
and an observable-level validation target. This gate prevents a homogeneous
Teukolsky amplitude from being silently promoted to a self-force or waveform
observable.
