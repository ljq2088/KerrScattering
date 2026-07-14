# Reusable paper cards

These cards are compact technical records derived from the verified arXiv
metadata catalog and the primary papers. They are intentionally shorter than a
full literature review; the source paper remains authoritative for equations.

## MST: analytic Teukolsky solutions

- **Source:** Mano, Suzuki, Takasugi, arXiv:gr-qc/9603020,
  https://arxiv.org/abs/gr-qc/9603020
- **Problem/order:** homogeneous Teukolsky equation on Kerr; hypergeometric
  and Coulomb-wave series with a low-frequency parameter `epsilon=2 M omega`.
- **Core idea:** construct two analytic representations and connect them by
  recurrence/continued-fraction data. The connection coefficients give an
  independent route to asymptotic amplitudes and Wronskian identities.
- **Transfer:** use MST/low-frequency formulas to audit the phase and
  normalization of `R_in`, `B_inc`, and `B_ref` when cancellation dominates.
- **Incompatibility:** the active endpoint solver is a direct spectral solve,
  not an MST series; agreement requires the same radial variable and amplitude
  normalization.
- **Experiment:** compare amplitude ratios and fluxes at `omega=1e-4, 0.1`
  after converting the local `lambda` convention.

## GSN: stable Kerr homogeneous solutions

- **Source:** Lo, arXiv:2306.16469,
  https://arxiv.org/abs/2306.16469
- **Problem/order:** homogeneous scalar, electromagnetic, and gravitational
  Teukolsky/GSN equations on Kerr.
- **Core idea:** transform the long-range Teukolsky radial equation to a form
  with better numerical behavior and provide explicit maps between GSN and
  Teukolsky solutions for both horizon and infinity boundary conditions.
- **Transfer:** benchmark complex amplitude ratios and fluxes; compare raw
  solutions only after applying the transformation and normalization map.
- **Incompatibility:** GSN solves a transformed equation and its internal
  amplitude constants are not automatically the local `B_inc` and `B_ref`.
- **Experiment:** use the GSN implementation at high frequency and verify that
  the spectral tail and field-dependent residual converge independently.

## Chebyshev spectral black-hole perturbations

- **Source:** Chung, Wagle, and Yunes, arXiv:2302.11624,
  https://arxiv.org/abs/2302.11624; Phys. Rev. D **107**, 124032 (2023).
- **Problem/order:** spectral treatment of linearized black-hole perturbations
  on a Schwarzschild background, with endpoint asymptotics factored before
  Chebyshev representation.
- **Core idea:** derive the horizon and infinity behavior first, then turn the
  regularized equations into a finite spectral algebraic system and quantify
  accuracy by order refinement and comparison with a trusted method.
- **Transfer:** this supports the present endpoint-inclusive workflow and the
  practice of treating endpoint relations as part of the matrix rather than
  as ordinary interior residual points.
- **Incompatibility:** the cited calculation targets gravitational QNMs in
  Schwarzschild, not Kerr scalar scattering or an inhomogeneous Green source.
- **Experiment:** retain separate coefficient-tail, endpoint, residual,
  Wronskian, and amplitude-convergence diagnostics when extending the route to
  Kerr.

## Barack--Pound: self-force and radiation reaction

- **Source:** Barack and Pound, arXiv:1805.10385,
  https://arxiv.org/abs/1805.10385
- **Problem/order:** small-mass-ratio expansion of the metric, worldline, and
  radiation reaction, including rotating black-hole applications.
- **Core idea:** matched asymptotic expansions, singular/regular field split,
  gauge issues, dissipative versus conservative effects, and the connection to
  waveform phase.
- **Transfer:** use the separation of observables and error budgets. Flux
  balance validates dissipative bookkeeping but does not validate a local
  conservative field or a long-time phase.
- **Incompatibility:** the scalar cubic Green-function response has no small
  body, metric perturbation, singular field, or gauge completion.
- **Experiment:** retain separate checks for radial-field residual,
  amplitude stability, flux balance, and perturbative smallness
  `epsilon |A^(1)| << |A^(0)|`.

## Pound--Wardell: unified BHPT/GSF workflow

- **Source:** Pound and Wardell, arXiv:2101.04592,
  https://arxiv.org/abs/2101.04592
- **Problem/order:** black-hole perturbation theory, Kerr orbital mechanics,
  self-force, and adiabatic/post-adiabatic EMRI waveforms.
- **Core idea:** connect Teukolsky/RWZ equations, metric reconstruction,
  action-angle orbital mechanics, resonances, puncture schemes, and
  multiscale waveform generation.
- **Transfer:** separate the radial solver from source-mode generation and from
  orbit evolution. This gives the correct future interface for EMRI work.
- **Incompatibility:** the current project has no evolving worldline and no
  mass-ratio expansion.
- **Experiment:** define a source-channel API carrying `(l,m,k,n,omega)` and a
  convention-checked radial response API before attempting inspiral evolution.

## Second-order Teukolsky in Kerr

- **Source:** Spiers, Pound, and Moxon, arXiv:2305.19332,
  https://arxiv.org/abs/2305.19332
- **Problem/order:** second-order gravitational perturbations on Kerr and the
  nonlinear source in a second-order Teukolsky formalism.
- **Core idea:** formulate a second-order equation compatible with metric
  reconstruction and discuss infrared behavior and gauge choices.
- **Transfer:** this is the correct reference for a future gravitational,
  rather than scalar, nonlinear source. It motivates keeping the present
  scalar nonlinear article explicit about its fixed-background scope.
- **Incompatibility:** a gravitational second-order source depends on tetrad,
  metric reconstruction, gauge, and regularization structures absent here.
- **Experiment:** no direct implementation until the linear `s=-2` convention
  and reconstruction layer are separately validated.

## Kerr QNM currents and nonlinear projection

- **Source:** Green et al., arXiv:2210.15935,
  https://arxiv.org/abs/2210.15935
- **Problem/order:** conserved bilinear currents and QNM orthogonality for Kerr
  Weyl perturbations.
- **Core idea:** Kerr QNMs require a nonstandard bilinear form and suitable
  contour/renormalization treatment; ordinary Hilbert-space projection is not
  automatic.
- **Transfer:** treat the current manuscript's Lorentzian peak fits as
  descriptive interpolation parameters, not QNM excitation coefficients.
- **Incompatibility:** the active calculation is a real-frequency driven scalar
  response and does not perform analytic continuation to a QNM pole.
- **Experiment:** only after a contour-regularized projection is implemented
  should a mode-coupling coefficient be reported.

## Self-force memory and long-time matching

- **Source:** Cunningham et al., arXiv:2410.23950,
  https://arxiv.org/abs/2410.23950
- **Problem/order:** gravitational-wave memory through first and second order
  in the mass-ratio/self-force expansion, including Kerr inspirals.
- **Core idea:** long-time effects can require matching the near-zone self-force
  expansion to a far-zone post-Minkowskian description.
- **Transfer:** a frequency-domain local response and a conserved flux do not
  by themselves establish long-time waveform accuracy.
- **Incompatibility:** the current scalar scattering problem has no inspiral
  timescale, mass-ratio expansion, or memory observable.
- **Experiment:** if a time-domain extension is attempted, measure accumulated
  phase/error and matching-scale dependence, not only pointwise residuals.

## Kerr geodesic frequencies and action-angle variables

- **Source:** Schmidt, arXiv:gr-qc/0202090,
  https://arxiv.org/abs/gr-qc/0202090
- **Problem/order:** bound geodesic motion in Kerr at zeroth order in the
  mass ratio, organized by action-angle variables.
- **Core idea:** the three fundamental frequencies are geometric invariants
  and provide the natural slow/fast decomposition for an EMRI source.
- **Transfer:** define a future source interface with the orbit constants,
  `Omega_r`, `Omega_theta`, `Omega_phi`, and the mode frequency
  `omega_mkn = m Omega_phi + k Omega_theta + n Omega_r`.
- **Incompatibility:** the active calculation has one prescribed frequency
  and no evolving orbit or source harmonic lattice.
- **Experiment:** before adding an orbit module, verify that a supplied
  `(m,k,n)` tuple maps to the same `omega` convention used by the radial
  solver and flux code.

## Analytic Kerr geodesics in Mino time

- **Source:** Fujita and Hikida, arXiv:0906.1420,
  https://arxiv.org/abs/0906.1420
- **Problem/order:** analytic bound timelike Kerr geodesics at test-particle
  order, using Mino time to decouple radial and polar motion.
- **Core idea:** elliptic-integral expressions make the three frequencies and
  the phase variables numerically accessible without integrating a rapidly
  varying coordinate-time trajectory directly.
- **Transfer:** use Mino-time quadratures as an independent orbit/frequency
  check for any future EMRI source generator.
- **Incompatibility:** no self-force, radiation reaction, or metric response
  is included.
- **Experiment:** compare frequency-domain source generation against a
  direct geodesic integration at fixed `(p,e,theta_minus)` before adding
  slow evolution.

## Teukolsky waveforms from generic Kerr geodesics

- **Source:** Fujita, Hikida, and Tagoshi, arXiv:0904.3810,
  https://arxiv.org/abs/0904.3810
- **Problem/order:** gravitational perturbations sourced by a point particle
  on eccentric and inclined Kerr geodesics at leading order in the mass ratio.
- **Core idea:** the source is a discrete `(l,m,k,n)` harmonic sum; energy,
  angular-momentum, and Carter-constant fluxes are built from the same
  homogeneous Teukolsky amplitudes.
- **Transfer:** the current `R_in/R_up` and flux modules can become the radial
  backend for a source-mode pipeline, provided spin `s=-2`, angular, and
  normalization conventions are implemented separately.
- **Incompatibility:** the active manuscript is scalar `s=0`, has no point
  particle stress-energy source, and does not compute Carter fluxes.
- **Experiment:** validate mode truncation in `l`, `k`, and `n` independently
  of radial spectral convergence; do not hide source truncation in a single
  residual number.

## Scalar self-force in Kerr

- **Source:** Warburton and Barack, arXiv:1103.0287,
  https://arxiv.org/abs/1103.0287
- **Problem/order:** scalar charge on eccentric equatorial Kerr orbits,
  including conservative self-force at first order in the charge/mass-ratio
  expansion.
- **Core idea:** extended homogeneous solutions remove Gibbs behavior from
  frequency-domain reconstruction, while mode-sum regularization removes the
  local singular field mode by mode.
- **Transfer:** retain the distinction between a smooth homogeneous radial
  solution and a regularized local self-force; both require explicit endpoint
  normalization and independent convergence tests.
- **Incompatibility:** the current cubic source is finite and prescribed; it
  has no worldline singularity or Detweiler--Whiting subtraction.
- **Experiment:** a future self-force branch should compare EHS reconstruction
  error, large-`l` regularization tail, and flux balance separately.

## Gravitational self-force on generic Kerr orbits

- **Source:** van de Meent, arXiv:1711.09607,
  https://arxiv.org/abs/1711.09607
- **Problem/order:** first-order gravitational self-force for generic bound
  Kerr geodesics, including dissipative and conservative pieces.
- **Core idea:** reconstruct the local metric from `psi_4`, apply spherical
  `l`-mode regularization, and validate averaged changes in `E`, `L_z`, and
  `Q` against fluxes at infinity and the horizon.
- **Transfer:** this is the model validation chain for a future gravitational
  branch: local field, regularization tail, orbit-averaged force, and global
  flux balance must all be reported.
- **Incompatibility:** it is not a scalar fixed-background response and uses
  metric reconstruction, a gravitational gauge, and a mass-ratio expansion.
- **Experiment:** do not expose a gravitational self-force API until the
  radial solver can carry source harmonics and convention metadata without
  conflating `s=0` and `s=-2`.

## Generic-Kerr regularization parameters

- **Source:** Heffernan, arXiv:2209.05450,
  https://arxiv.org/abs/2209.05450
- **Problem/order:** higher-order Detweiler--Whiting mode-sum regularization
  parameters for electromagnetic and gravitational self-force on generic
  Kerr orbits.
- **Core idea:** the singular-field asymptotics determine the large-`l`
  subtraction terms; more terms accelerate the residual mode sum.
- **Transfer:** use the same principle for numerical diagnostics: a residual
  must retain the field amplitude and the dominant local scale, rather than
  normalizing only by differential-equation coefficients.
- **Incompatibility:** no singular field occurs in the active scalar cubic
  Green-function problem.
- **Experiment:** if a self-force extension is started, measure convergence
  both before and after each regularization parameter is included.

## Frequency-domain self-force workflow and phase targets

- **Source:** Osburn et al., arXiv:1409.4419,
  https://arxiv.org/abs/1409.4419
- **Problem/order:** frequency-domain gravitational self-force for eccentric
  binaries, with extended homogeneous solutions and mode-sum regularization.
- **Core idea:** waveform usefulness imposes a phase-error budget, which is
  stricter than a pointwise field residual and determines precision targets for
  averaged and oscillatory force pieces.
- **Transfer:** future KerrScattering studies should propagate radial-amplitude
  error into flux error and then into an accumulated phase estimate instead of
  stopping at a single-frequency residual.
- **Incompatibility:** the current work has no orbit-time integration and no
  gravitational phase observable.
- **Experiment:** add a bounded synthetic frequency sweep whose output is an
  integrated phase-error estimate, while keeping it clearly separate from the
  scalar scattering manuscript.

## Recent second-order self-force for eccentric EMRIs

- **Source:** Wei, Zhu, Zhang, and Mei, arXiv:2504.09640,
  https://arxiv.org/abs/2504.09640
- **Problem/order:** second-order self-force formulation for eccentric EMRIs
  on Schwarzschild, including a puncture field and a two-timescale expansion.
- **Core idea:** the second-order source is organized by the lower-order field
  and the orbital slow time; the singular local structure must be separated
  before a numerical field can be interpreted as a self-force.
- **Transfer:** the current Green-function hierarchy is useful as a source
  bookkeeping prototype, but an EMRI branch must add a worldline, a slow-time
  expansion, and a regular field prescription.
- **Incompatibility:** this is not a fixed-frequency Kerr scalar response and
  it does not justify relabelling the present `A^(1)` as a gravitational
  second-order field.

## Kerr metric reconstruction from Teukolsky modes

- **Source:** Berens, Gravely, and Lupsasca, arXiv:2403.20311,
  https://arxiv.org/abs/2403.20311
- **Problem/order:** explicit reconstruction of linearized metric perturbations
  on Kerr from separated Teukolsky modes.
- **Core idea:** energy fluxes can be obtained at the Teukolsky-scalar level,
  but nonlinear or local observables require metric reconstruction, gauge
  information, and careful use of Teukolsky--Starobinsky identities.
- **Transfer:** use this as the interface specification for a future
  gravitational branch: `psi4 -> metric -> source/force`, with reconstruction
  metadata kept distinct from radial amplitude metadata.
- **Incompatibility:** the active project has `s=0` and no metric perturbation,
  tetrad reconstruction, or gauge-dependent local observable.

## EMRI tests of Kerr symmetry

- **Source:** Muguruza and Sopuerta, arXiv:2604.06053,
  https://arxiv.org/abs/2604.06053
- **Problem/order:** LISA EMRI waveform sensitivity to multipolar and symmetry-
  breaking deviations from Kerr.
- **Core idea:** the many accumulated orbital cycles turn small changes in
  geodesic frequencies and fluxes into measurable phase information.
- **Transfer:** this fixes the long-term validation target for future work:
  radial amplitude error must be propagated through source harmonics, fluxes,
  orbital evolution, and finally waveform phase.
- **Incompatibility:** a single-frequency scalar scattering curve, even with a
  small residual, is not an EMRI waveform or a test of Kerr symmetry.

## Nonlinear gravity scattering

- **Source:** Cardoso, Redondo-Yuste, Sperhake, and Tuncer,
  arXiv:2603.04501, https://arxiv.org/abs/2603.04501
- **Problem/order:** nonlinear Einstein--Klein--Gordon and vacuum wave
  scattering, including higher-harmonic generation and spectral broadening.
- **Core idea:** nonlinear wave propagation can redistribute spectral content;
  a single real-frequency response is therefore not a complete description of
  a time-dependent nonlinear scattering experiment.
- **Transfer:** this motivates a future scalar time-domain extension that
  measures generated harmonics separately from the fixed-frequency Green
  coefficient reported here.
- **Incompatibility:** the active calculation uses a prescribed cubic scalar
  interaction on a fixed Kerr metric and keeps one Fourier frequency; it does
  not solve the coupled Einstein--Klein--Gordon system.
- **Experiment:** evolve a bounded wave packet on Kerr and compare the
  generated-frequency spectrum with the sum of fixed-frequency perturbative
  responses, while monitoring energy flux at infinity and the horizon.

## Frequency-domain effective-source prototype

- **Source:** Leather and Warburton, arXiv:2306.17221,
  https://arxiv.org/abs/2306.17221
- **Problem/order:** frequency-domain effective-source treatment of eccentric
  self-force calculations, demonstrated with a scalar-field prototype.
- **Core idea:** extended effective sources and extended particular solutions
  can improve Fourier reconstruction while retaining the local singular-field
  subtraction needed by self-force theory.
- **Transfer:** this is a concrete numerical bridge for a future scalar
  self-force branch: distinguish homogeneous radial accuracy, source
  reconstruction, and regularization-tail convergence.
- **Incompatibility:** the current cubic source is smooth and prescribed; it
  has no point-particle singularity, Detweiler--Whiting split, or corrected
  worldline.
- **Experiment:** implement a separate toy effective-source problem and report
  Fourier-mode truncation, reconstruction error, and regularization residuals
  independently of the present nonlinear scattering tables.

## Relativistic EMRI waveforms for LISA inference

- **Source:** Khalvati, Santini, Duque, Speri, Gair, Yang, and Brito,
  arXiv:2410.17310, https://arxiv.org/abs/2410.17310
- **Problem/order:** fully relativistic adiabatic waveforms for circular
  equatorial Kerr EMRIs, including environmental and scalar-cloud examples.
- **Core idea:** relativistic corrections can change inference and
  environmental distinguishability even when the waveform is still only
  adiabatic in mass-ratio order.
- **Transfer:** use waveform phase, parameter bias, and model-selection
  impact as the observable-level endpoint of a future radial error budget.
- **Incompatibility:** adiabatic waveform generation is not a substitute for
  conservative or second-order self-force.
- **Experiment:** inject a fixed radial-amplitude perturbation into a bounded
  circular-orbit waveform and measure phase accumulation separately from the
  radial residual.

## Post-adiabatic EMRI waveforms with environmental corrections

- **Source:** Rahman and Takahashi, arXiv:2507.06923,
  https://arxiv.org/abs/2507.06923
- **Problem/order:** first post-adiabatic EMRI evolution with a perturbative
  environmental correction.
- **Core idea:** the correction must be propagated through the slow orbital
  evolution; an instantaneous flux change is not the final waveform
  observable.
- **Transfer:** add an explicit slow-time and accumulated-phase record to any
  future source/orbit module.
- **Incompatibility:** environmental modeling changes the background/source
  assumptions and is not part of the fixed Kerr scalar manuscript.
- **Experiment:** compare adiabatic and first post-adiabatic phase for a
  controlled toy flux perturbation while holding the radial backend fixed.

## Numerical-relativity methods for self-force in Kerr

- **Source:** Vu, Nishimura, Osburn, Thompson, Kidder, Upton, and Wardell,
  arXiv:2606.04998, https://arxiv.org/abs/2606.04998
- **Problem/order:** a high-order discontinuous-Galerkin, adaptive,
  horizon-penetrating route toward generic second-order self-force in Kerr.
- **Core idea:** time-domain DG/AMR can retain exponential convergence and
  high-spin horizon access when generic or second-order problems make
  frequency-domain separability impractical.
- **Transfer:** use it as a complementary algorithmic benchmark: compare
  endpoint regularity, observable convergence, and memory scaling rather than
  raw matrix sizes.
- **Incompatibility:** the active solver is a separated frequency-domain
  Chebyshev method for a smooth scalar source, not a puncture-based
  second-order self-force code.
- **Experiment:** only after the orbit/source interface exists, compare one
  circular scalar mode against a bounded time-domain evolution.

## Mino--Sasaki--Tanaka radiation reaction

- **Source:** Mino, Sasaki, and Tanaka, arXiv:gr-qc/9712056,
  https://arxiv.org/abs/gr-qc/9712056
- **Problem/order:** leading gravitational radiation reaction for a small body
  obtained from matched asymptotic expansions at first order in the mass ratio.
- **Core idea:** consistency between an external perturbed background and an
  internal tidally perturbed small black hole produces a tail-dependent force.
  The local singular self-field is not inserted directly into the motion.
- **Transfer:** keep the perturbative parameter and slow-time bookkeeping
  explicit when moving from a fixed-frequency field response toward an EMRI
  source model. A flux result is a dissipative projection, not the full local
  force.
- **Incompatibility:** the current scalar calculation has no small body, matched
  zones, worldline, metric perturbation, or radiation-reaction evolution.
- **Experiment:** add an `eta` label to a future source-mode API and verify that
  changing the radial discretization does not alter the declared perturbative
  order.

## Detweiler--Whiting singular/regular split

- **Source:** Detweiler and Whiting, arXiv:gr-qc/0202086,
  https://arxiv.org/abs/gr-qc/0202086
- **Problem/order:** first-order scalar, electromagnetic, and gravitational
  self-force fields generated by a point particle in curved spacetime.
- **Core idea:** decompose the retarded field into a locally determined singular
  field and a homogeneous regular field containing the tail contribution; the
  regular field determines the self-force.
- **Transfer:** this is the conceptual gate that prevents a smooth prescribed
  nonlinear response from being mislabeled as self-force. Any future point-source
  extension needs a singular/regular or equivalent effective-source interface.
- **Incompatibility:** the present cubic source is smooth and fixed-background;
  there is no worldline singularity or gauge-completed metric perturbation.
- **Experiment:** compare a smooth-source residual with a deliberately localized
  point-source prototype and record where mode-sum subtraction becomes necessary.

## Barack--Ori mode-sum regularization

- **Source:** Barack and Ori, arXiv:gr-qc/9912010,
  https://arxiv.org/abs/gr-qc/9912010
- **Problem/order:** scalar self-force on Schwarzschild, with local force modes
  regularized before summing over multipoles.
- **Core idea:** calculate each retarded multipole, subtract its analytically
  known large-`l` singular asymptotics, and only then sum the residual modes.
- **Transfer:** use large-mode asymptotics and tail fits as a model for future
  source-lattice diagnostics, while keeping radial spectral convergence and
  angular/mode regularization as separate error axes.
- **Incompatibility:** no singular point source appears in the active Kerr
  scalar nonlinear Green-function problem, so mode-sum subtraction would be an
  unjustified extra operation there.
- **Experiment:** require a future self-force prototype to report the raw mode,
  subtraction terms, residual mode, and tail error separately.

## Post-Newtonian gravity as an effective field theory

- **Source:** Levi, arXiv:1807.01699,
  https://arxiv.org/abs/1807.01699
- **Problem/order:** organize compact-binary dynamics and gravitational-wave
  observables using scale-separated effective field theories in the PN regime.
- **Core idea:** separate near-zone conservative dynamics from radiation-zone
  propagation and matching, with worldline operators encoding finite-size and
  multipolar effects.
- **Transfer:** use an approximation-order ledger when comparing PN, BHPT, and
  EMRI predictions. The radial Kerr solver supplies strong-field response data,
  but it does not by itself define a PN waveform or a matched observable.
- **Incompatibility:** the current calculation is a single fixed Kerr background
  and not a two-body inspiral expansion; PN gauge and matching choices are not
  present in the manuscript.
- **Experiment:** for a future overlap study, compare one invariant flux or
  phase coefficient in a declared weak-field limit, including the matching
  convention and truncation order.

## Kerr adiabatic inspiral and horizon absorption

- **Source:** Hughes, arXiv:gr-qc/9910091,
  https://arxiv.org/abs/gr-qc/9910091
- **Problem/order:** adiabatic radiation reaction for circular, inclined
  orbits around Kerr at leading order in the mass ratio.
- **Core idea:** energy and angular-momentum fluxes, including horizon
  absorption, constrain the evolution of the orbit and the Carter constant
  for this restricted family.
- **Transfer:** a radial amplitude is useful only after its infinity and
  horizon pieces are converted into fluxes and inserted into an orbit model.
  Horizon absorption can change both inspiral time and waveform phase.
- **Incompatibility:** the current fixed-frequency scalar response has no
  small-body worldline, adiabatic time, or gravitational Carter-flux law.
- **Experiment:** use a convention-tagged pair of horizon/infinity amplitudes
  to build one flux-balance record before attempting an orbit evolution.

## Kerr inspiral trajectories and multi-harmonic waveforms

- **Source:** Hughes, arXiv:gr-qc/0104041,
  https://arxiv.org/abs/gr-qc/0104041
- **Problem/order:** adiabatic inspiral trajectories and waveforms for
  circular, inclined Kerr orbits.
- **Core idea:** the signal is a sum of slowly evolving harmonic voices, and
  rapid spin makes horizon coupling important to the accumulated phase.
- **Transfer:** the future source interface must preserve mode labels and
  phases instead of collapsing a spectrum to a single effective frequency.
  Radial solver errors should be propagated to phase error, not reported only
  as pointwise amplitude errors.
- **Incompatibility:** the current paper solves a fixed real-frequency scalar
  problem and does not evolve orbital constants.
- **Experiment:** inject a controlled fractional perturbation into one mode,
  integrate its phase over a bounded toy inspiral, and report the resulting
  phase budget separately from radial residuals.

## Generic eccentric and inclined EMRI waveform snapshots

- **Source:** Drasco and Hughes, arXiv:gr-qc/0509101,
  https://arxiv.org/abs/gr-qc/0509101
- **Problem/order:** frequency-domain gravitational waves from generic bound
  Kerr geodesics, with simultaneous eccentricity and inclination.
- **Core idea:** radial, polar, and azimuthal orbital motions create distinct
  harmonic voices; infinity and horizon fluxes are computed mode by mode and
  can drive an adiabatic evolution.
- **Transfer:** this supplies the concrete hierarchy
  `(E,L_z,Q) -> (Omega_r,Omega_theta,Omega_phi) -> (l,m,k,n) -> omega`
  that a future KerrScattering source layer must implement.
- **Incompatibility:** a single `(l,m,omega)` scalar response is only the
  radial backend of this hierarchy and cannot be called an EMRI waveform.
- **Experiment:** validate mode-lattice truncation independently of radial
  spectral order, then compare the reconstructed flux with the sum of retained
  source modes.
