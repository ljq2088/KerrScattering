# Research frontier update: EMRI and self-force

This note records a focused literature transfer completed on 2026-07-15.
The sources are primary research papers.  They are a watchlist for the next
implementation layer; they are not silently promoted into the fixed-background
scalar Kerr manuscript.

## 1. Eccentric second-order self-force

**Source:** Yi-Xiang Wei, Xian-Long Zhu, Jian-dong Zhang, and Jianwei Mei,
"Toward Second-Order Self-Force for Eccentric Extreme-Mass-Ratio Inspirals in
Schwarzschild Spacetime," arXiv:2504.09640v2,
[arXiv record](https://arxiv.org/abs/2504.09640), Phys. Rev. D 112, 064048
(2025).

**Transferred structure.**  The calculation separates the mass-ratio
expansion from the fast orbital phases and constructs a puncture field for
eccentric motion.  The source is therefore organized by perturbative order
and by multiple time scales, rather than by a single stationary real
frequency.

**Implementation target.**  The future interface must carry
`eta_order`, orbital phase labels, and a puncture/effective-source tag next to
each radial mode.  A frequency-domain radial solve can be reused only after
the source lattice and slow-time bookkeeping are explicit.

**Boundary of transfer.**  The current cubic scalar source is smooth and
prescribed on a fixed Kerr background.  It has no point-particle singularity,
worldline correction, or second-order metric source, so this paper does not
change the present manuscript's interpretation of `T^(1)` and `R^(1)`.

## 2. Generic first-order effective sources

**Source:** Chao Zhang, Rong-gen Cai, Guoyang Fu, Yungui Gong, Xuchen Lu, and
Wenting Zhou, "Generic effective sources for first-order in mass-ratio
gravitational self-force calculations in Schwarzschild spacetime,"
arXiv:2505.19732v2,
[arXiv record](https://arxiv.org/abs/2505.19732), Phys. Rev. D 112, 104069
(2025).

**Transferred structure.**  The effective-source method replaces a singular
point-particle equation by a finite residual equation.  The paper gives an
analytic construction for generic Schwarzschild geodesics and emphasizes a
continuous effective source suitable for numerical evolution.

**Implementation target.**  Add an explicit source contract
`S_ret = S_puncture + S_eff` and tests for continuity across the worldline,
large-mode scaling, and gauge declaration.  The present radial residual test
is a useful template for the residual equation, but it is not a
regularization test.

**Boundary of transfer.**  A smooth scalar self-interaction does not require a
Detweiler--Whiting split.  Importing an effective-source label into the
current Kerr scalar calculation would therefore be physically misleading.

## 3. Second-order effective source and post-adiabatic structure

**Source:** Samuel D. Upton, Barry Wardell, Adam Pound, Niels Warburton, and
Leor Barack, "Effective source for second-order self-force calculations:
quasicircular orbits in Schwarzschild spacetime," arXiv:2508.00087v2,
[arXiv record](https://arxiv.org/abs/2508.00087), Phys. Rev. D 113, 064013
(2026).

**Transferred structure.**  The second-order source contains quadratic
first-order modes, slow evolution of those modes, quadratic puncture-field
terms, and a second-order puncture.  This is the correct warning against
identifying an arbitrary nonlinear source with a second-order gravitational
Teukolsky source.

**Implementation target.**  A future nonlinear-gravity branch needs separate
source provenance fields for quadratic regular-field terms, slow-time terms,
and puncture terms.  Its validation must test each contribution before their
sum, then test waveform phase and flux observables.

**Boundary of transfer.**  The active project computes a first derivative with
respect to a scalar coupling at `epsilon=0`; it does not solve the
second-order Einstein equation and does not include a puncture field.

## 4. Conserved Kerr bilinear forms

**Source:** Stephen R. Green, Stefan Hollands, Laura Sberna, Vahid Toomani,
and Peter Zimmerman, "Conserved currents for Kerr and orthogonality of
quasinormal modes," arXiv:2210.15935v3,
[arXiv record](https://arxiv.org/abs/2210.15935).

**Transferred structure.**  The paper constructs conserved bilinear forms for
Kerr Weyl perturbations and uses them to define QNM projections.  It also
separates local conserved-current statements from the special analytic
continuation required for QNM normalization.

**Implementation target.**  Keep the present real-frequency Wronskian and
energy-flux checks separate from any future QNM projection.  If a ringdown
module is added, it must carry a `qnm_projection` observable label and a
complex-frequency contour/renormalization record.

**Boundary of transfer.**  The current local identity is for a scalar radial
equation with a real potential and a smooth cubic self-channel.  It is not a
Weyl-scalar bilinear QNM excitation coefficient.

## Promotion decision

These records strengthen the research workflow but do not change the active
physics claim.  Promotion to an EMRI waveform requires the tested chain

`OrbitConstants -> Frequencies -> ModeLabel -> SourceCoefficients -> FluxRecord`

and promotion to gravitational self-force additionally requires a
singular/regular or effective-source construction, a gauge prescription,
regularization data, and a phase-error budget.  The current manuscript passes
none of those new promotion gates by analogy alone.
