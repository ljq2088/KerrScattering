# Core reading notes

These notes are a compact technical orientation. They are not a replacement
for the cited papers; equations used in a manuscript must still be checked
against the source version and the local convention ledger.

## Teukolsky, MST, and GSN

Primary sources: [Sasaki--Tagoshi, gr-qc/0306120](https://arxiv.org/abs/gr-qc/0306120),
[MST, gr-qc/9603020](https://arxiv.org/abs/gr-qc/9603020), and
[GSN, 2306.16469](https://arxiv.org/abs/2306.16469).

The transferable chain is:

1. fix spin weight, Fourier sign, angular eigenvalue, and radial variable;
2. define horizon and infinity bases before quoting connection coefficients;
3. compare normalized amplitudes, fluxes, and Wronskians rather than raw
   values of differently rescaled radial functions;
4. use MST as an analytic low-frequency audit and GSN as a transformed-
   equation numerical audit.

For KerrScattering this means that `lambda`, `R_in`, `B_inc`, and `B_ref` must
always be accompanied by the convention block in `docs/literature/convention_ledger.md`.

## Green functions and self-force

Primary sources: [Poisson--Pound--Vega, 1102.0529](https://arxiv.org/abs/1102.0529),
[Barack--Pound, 1805.10385](https://arxiv.org/abs/1805.10385), and
[Pound--Wardell, 2101.04592](https://arxiv.org/abs/2101.04592).

A Green-function projection divided by a Wronskian is reusable as a numerical
structure. A gravitational self-force calculation additionally needs a small
mass-ratio expansion, a singular/regular field split, gauge information,
regularization, and a worldline prescription. The active scalar equation
`Box Phi + epsilon |Phi|^2 Phi = 0` has none of those gravitational ingredients.

Therefore the current `A^(1)` is a prescribed nonlinear response coefficient,
not a self-force or a metric perturbation coefficient.

## EMRI orbital and waveform layers

Primary sources: [Schmidt, gr-qc/0202090](https://arxiv.org/abs/gr-qc/0202090),
[Fujita--Hikida, 0906.1420](https://arxiv.org/abs/0906.1420),
[Fujita--Tagoshi, 0904.3810](https://arxiv.org/abs/0904.3810), and
[Babak et al., 1703.09722](https://arxiv.org/abs/1703.09722).

An EMRI source is a mode lattice,
`omega_mkn = m Omega_phi + k Omega_theta + n Omega_r`, built from Kerr
geodesic constants and fundamental frequencies. A single fixed-frequency
radial amplitude is one backend component, not an inspiral waveform. Before
adding orbit evolution, define APIs for orbit constants, frequencies, source
coefficients, mode labels, radial conventions, fluxes, and accumulated phase
error.

## Second order and ringdown

Primary sources: [Spiers--Pound--Moxon, 2305.19332](https://arxiv.org/abs/2305.19332)
and [Green et al., 2210.15935](https://arxiv.org/abs/2210.15935).

Second-order gravitational Teukolsky work introduces metric/tetrad
reconstruction, gauge completion, nonlinear gravitational sources, and
infrared structure. A real-frequency response peak can be a useful diagnostic,
but it is not automatically a Kerr QNM excitation coefficient. QNM projection
requires the correct Kerr bilinear form and boundary/analytic-continuation
prescription.

## Validation hierarchy

For every transfer from the literature, record:

- the exact convention conversion;
- endpoint and source conditions;
- the numerical method and precision controls;
- field-dependent residual and spectral-tail diagnostics;
- amplitude, Wronskian, and flux checks;
- the distinction between a local fixed-frequency result and a long-time
  EMRI observable.

The current project has evidence through the fixed-background response and
flux layers. Orbit evolution, regularization, conservative self-force, and
waveform phase error remain future modules.
