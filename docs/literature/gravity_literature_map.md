# Gravity literature map

This map separates neighbouring research areas before transferring equations
or numerical diagnostics into KerrScattering. The active implementation is a
fixed-background scalar Teukolsky calculation on Kerr, with a prescribed weak
cubic field nonlinearity.

## 1. Fixed-background black-hole perturbation theory

Read Teukolsky, Sasaki--Tagoshi, MST, and GSN together. Extract the spin
weight, Fourier sign, angular eigenvalue, radial variable, horizon exponent,
infinity basis, and normalization of `B_inc`, `B_ref`, and the horizon
amplitude. The reusable numerical lesson is to compare invariant ratios and
fluxes after convention conversion, rather than raw radial arrays.

Primary anchors: `gr-qc/0306120`, `gr-qc/9603020`, `2306.16469`.

## 2. Kerr geodesics and EMRI source structure

The EMRI source is a discrete mode lattice, not a single arbitrary frequency:

```text
OrbitConstants(E, Lz, Q, p, e, theta_minus)
 -> (Omega_r, Omega_theta, Omega_phi, Gamma)
 -> omega_mkn = m Omega_phi + k Omega_theta + n Omega_r
 -> source coefficients and Teukolsky modes
```

The current fixed-frequency module can become the radial backend for this
interface, but it does not provide orbital evolution or a waveform phase.

Primary anchors: `gr-qc/0202090`, `0906.1420`, `0904.3810`, `2101.04592`.

## 3. Green functions, fluxes, and radiation reaction

Green-function amplitudes are source projections divided by a Wronskian.
Flux balance is a global dissipative check. Neither one by itself proves local
field accuracy, conservative-force accuracy, or long-time waveform accuracy.

Primary anchors: `1102.0529`, `1805.10385`, `1711.09607`.

## 4. Gravitational self-force

Gravitational self-force expands in the small-body mass ratio and requires a
singular/regular field split, gauge specification, regularization parameters,
and a corrected worldline. A scalar prescribed source such as
`Box Phi + epsilon |Phi|^2 Phi = 0` is not a gravitational self-force model.

Primary anchors: `1103.0287`, `1408.2885`, `1805.10385`, `2209.05450`.

## 5. Second-order perturbation theory and ringdown

Second-order gravitational Teukolsky work adds metric/tetrad reconstruction,
gauge and infrared structure, and a nonlinear source with gravitational
couplings. A real-frequency Lorentzian fit is a diagnostic, not automatically
a Kerr QNM excitation coefficient; Kerr QNM projections require the relevant
bilinear form and analytic continuation.

Primary anchors: `2305.19332`, `2210.15935`, `2410.23950`.

## 6. Nonlinear wave scattering and effective-source prototypes

Nonlinear Einstein--Klein--Gordon and vacuum scattering provide a useful
comparison for harmonic generation and spectral broadening, but they are not
the same as a prescribed cubic scalar response on a fixed Kerr background.
Conversely, frequency-domain effective-source calculations for eccentric
orbits show how a scalar toy model can test extended particular solutions and
regularization machinery without being promoted to a gravitational
self-force result.

Primary anchors: `2603.04501`, `2306.17221`.

## 7. Waveform and detector layer

EMRI waveform work must propagate radial amplitude and source truncation errors
through orbit evolution and accumulated phase. A high-accuracy single-mode
amplitude is only one module in that error budget.

Primary anchors: `1409.4419`, `1703.09722`, `2310.08438`, `2604.06053`.

## 8. Current numerical frontier

Recent work makes the practical hierarchy sharper. Fully relativistic
adiabatic EMRI waveforms are already important for inference, even before
post-adiabatic self-force terms are included (`2410.17310`). A first
post-adiabatic environmental model makes the phase budget explicit
(`2507.06923`). In parallel, a 2026 numerical-relativity route targets
generic second-order self-force in Kerr with horizon-penetrating coordinates,
high-order discontinuous Galerkin discretization, adaptive refinement, and
iterative preconditioning (`2606.04998`).

The transferable lesson is not to choose one universal solver. Frequency-
domain spectral methods are natural for separated fixed-frequency radial
problems; extended homogeneous solutions and mode-sum methods address
worldline singularities; time-domain DG/AMR methods are attractive when
generic orbits and second-order sources defeat separability. These are
complementary layers with different error norms.

Primary anchors: `2410.17310`, `2507.06923`, `2606.04998`.

## 9. Foundations of self-force and waveform approximations

The conceptual chain is now explicit rather than implicit:

```text
matched asymptotics -> radiation-reaction tail
                    -> singular/regular field split
                    -> mode-sum or effective-source regularization
                    -> orbit actions and EMRI source lattice
                    -> waveform phase and detector observable
```

Mino--Sasaki--Tanaka supplies the first arrow, Detweiler--Whiting supplies the
singular/regular distinction, and Barack--Ori supplies a concrete mode-sum
implementation. The post-Newtonian EFT literature supplies a complementary
weak-field organization and makes the near-zone/far-zone matching question
explicit. None of these changes the scope of the active fixed-background
scalar manuscript; they define the prerequisites for a future self-force or
waveform branch.

Primary anchors: `gr-qc/9712056`, `gr-qc/0202086`, `gr-qc/9912010`, `1807.01699`.

## Transfer gate

Before importing a result, record:

1. perturbative parameter and order;
2. metric, signature, gauge, tetrad, Fourier, and radial conventions;
3. angular eigenvalue and boundary conditions;
4. Green-function/Wronskian or regularization normalization;
5. numerical method and independent validation;
6. what is transferable to the scalar fixed-background problem;
7. what assumption is incompatible with the current model.

The maintained evidence records are in `paper_cards.md`,
`core_reading_notes.md`, `deep_learning_curriculum.md`, and
`results/literature/arxiv_catalog.json`.
