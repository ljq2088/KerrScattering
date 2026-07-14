# Deep-learning report: gravitation, EMRIs, waves, and self-force

This report is the technical synthesis for the research agent. It is
organized around equations, approximation layers, and numerical validation
rather than around a list of names. The active KerrScattering calculation
remains a fixed-background scalar (`s=0`) problem.

## 1. The hierarchy of problems

Let `M` be the large black-hole mass, `mu` the small-body mass, and
`eta = mu/M << 1`. The four layers are:

1. **Background field theory:** a field propagates on a prescribed Kerr
   metric `g^(0)_{mu nu}(M,a)`.
2. **Black-hole perturbation theory:** a linear field or metric perturbation
   is solved on `g^(0)`, often after separation into `(l,m,omega)` modes.
3. **Gravitational self-force:** the small body changes both the metric and
   its own worldline,
   `g = g^(0) + eta h^(1) + eta^2 h^(2) + ...`,
   `z = z_0 + eta z_1 + ...`.
4. **EMRI waveform:** the orbital actions and phases evolve on slow time
   `T = eta t`; local self-force information is integrated over
   `O(eta^(-1))` orbital cycles.

The active equation,

`Box_g Phi + epsilon |Phi|^2 Phi = 0`,

belongs to layer 1 with a prescribed nonlinear field response. Its
first-order coefficient `A^(1)` is not a coefficient of `h^(1)`, not a
worldline force, and not an EMRI waveform correction.

## 2. Kerr separation and the EMRI source lattice

For a Fourier convention `exp(-i omega t + i m phi)`, a separated mode has

`Phi = R_lm(r) S_lm(theta) exp(-i omega t + i m phi)`.

For a point particle on a generic bound Kerr geodesic, the orbit has three
fundamental frequencies. The source is therefore a discrete lattice

`omega_mkn = m Omega_phi + k Omega_theta + n Omega_r`,

with integers `(m,k,n)`. The radial equation is solved separately for every
mode, and the waveform is reconstructed only after summing the source
coefficients and phase factors. This is the central reason an accurate
single-frequency radial amplitude is necessary but insufficient for an EMRI.

The implementation contract for the future source layer is:

`(E,Lz,Q,p,e,theta_minus) -> (Omega_r,Omega_theta,Omega_phi,Gamma)`

followed by

`(l,m,k,n) -> omega_mkn, Z_inf, Z_H, flux contribution`.

The orbit module must validate frequencies independently, for example with
Mino-time quadratures and a direct geodesic integration.

## 3. Green functions, amplitudes, and fluxes

For a separated radial operator `L_omega`, let `R_in` be ingoing at the
horizon and `R_up` be outgoing at infinity. Their Wronskian is

`W = Delta^(s+1) (R_in dR_up/dr - R_up dR_in/dr)`,

up to the exact spin/radial convention used by the implementation. A source
projection gives

`R_part(r) = R_up(r) int_{r_+}^r R_in(r') S(r')/W(r') dr'
             + R_in(r) int_r^infinity R_up(r') S(r')/W(r') dr'`.

The amplitude at infinity and the horizon is therefore a source projection
divided by the same Wronskian. The physical flux is quadratic in the
appropriate asymptotic amplitude. This is the reusable numerical core shared
by the scalar project and frequency-domain EMRI calculations.

The transfer rule is strict: compare fluxes or convention-converted ratios,
not raw radial arrays with different normalizations.

## 4. Adiabatic and post-adiabatic evolution

For actions `J_A` and orbital phases `q_alpha`, the two-timescale
expansion has the schematic form

`dJ_A/dT = F_A^(0)(J) + eta F_A^(1)(J, q) + O(eta^2)`,

`dq_alpha/dT = Omega_alpha(J)/eta + f_alpha^(0)(J,q) + O(eta)`.

At leading adiabatic order, one averages the dissipative force over the
fast phases. Post-adiabatic order adds oscillatory and conservative pieces.
The accumulated phase is more sensitive than an instantaneous field:

`delta Phi(T) = int delta Omega(J(T)) dt + phase corrections`.

Consequently, a `10^-10` radial residual is not a `10^-10` waveform error.
The complete budget must include radial discretization, angular eigenvalue,
source-lattice truncation, orbit integration, and approximation order.

## 5. Resonances

Transient resonances occur when

`n Omega_r + k Omega_theta = 0`

for nonzero integers `(k,n)`. The averaging used away from resonance then
fails because a normally oscillatory phase combination becomes slow. The
actions can receive a resonance jump, which changes the subsequent phase.

A future EMRI test should therefore report:

- distance from resonance;
- resonance crossing time and phase combination;
- action jump at the chosen perturbative order;
- post-crossing accumulated phase difference.

This physics is absent from the present fixed-frequency scattering paper and
must not be inferred from a frequency sweep alone.

## 6. Self-force and regularization

The retarded gravitational perturbation is decomposed schematically as

`h_ret = h_S + h_R`.

The singular piece `h_S` reproduces the local Coulomb-like structure of the
small body and is not itself the physical force. The regular field `h_R`
enters the self-force after specifying the gauge and the worldline
prescription. In a mode-sum implementation, one subtracts the large-`l`
singular asymptotics from the retarded modes before summing the residual.

At second order, the source contains products of first-order fields and
worldline corrections. A puncture/effective-source formulation makes the
residual field numerically regular, while an extended-homogeneous-solution
formulation controls Gibbs behavior in frequency-domain reconstruction.
These are different tools for different singular and reconstruction
problems.

The present cubic scalar source is smooth and externally prescribed. It needs
a field-dependent residual and perturbative-smallness test, but it does not
need Detweiler--Whiting subtraction or a gravitational gauge choice.

## 7. What the latest numerical frontier changes

Fully relativistic adiabatic EMRI waveforms show that waveform and inference
systematics can be important before second-order self-force terms are added.
Post-adiabatic environmental models make the accumulated phase the natural
observable for deciding whether a correction matters. A 2026
horizon-penetrating DG/AMR approach demonstrates a complementary route toward
generic second-order self-force in Kerr, where frequency-domain separability
is no longer sufficient by itself.

The project consequence is a solver portfolio, not a solver replacement:

- endpoint-inclusive Chebyshev for the present separated scalar radial problem;
- MST/GSN for independent amplitude audits and difficult frequency regimes;
- EHS plus mode-sum/effective-source machinery for worldline self-force;
- DG/AMR time-domain methods for generic second-order nonseparable problems.

## 8. Study questions and experiments

The agent should answer these before promoting any result:

1. Which convention maps the local `lambda` to the source paper's angular
   separation constant?
2. Does the extracted amplitude converge under order, matching radius, and
   quadrature refinement?
3. Is the source smooth, extended, or singular?
4. Which flux balance is an identity, and which is a numerical diagnostic?
5. What is the perturbative parameter, and is the reported coefficient
   physical only after multiplying by it?
6. How does a local field error propagate into the target observable?
7. Is the result gauge invariant, gauge dependent, or only a convention-fixed
   amplitude?

The next concrete code milestone is an orbit/source interface that feeds a
single convention-tagged `(l,m,k,n,omega)` mode into the existing radial
backend without changing the scalar manuscript's scope.

## Primary reading anchors

- [Sasaki--Tagoshi, gr-qc/0306120](https://arxiv.org/abs/gr-qc/0306120)
- [Pound--Wardell, 2101.04592](https://arxiv.org/abs/2101.04592)
- [Barack--Pound, 1805.10385](https://arxiv.org/abs/1805.10385)
- [Fujita--Hikida, 0906.1420](https://arxiv.org/abs/0906.1420)
- [Fujita--Tagoshi, 0904.3810](https://arxiv.org/abs/0904.3810)
- [Khalvati et al., 2410.17310](https://arxiv.org/abs/2410.17310)
- [Rahman--Takahashi, 2507.06923](https://arxiv.org/abs/2507.06923)
- [Vu et al., 2606.04998](https://arxiv.org/abs/2606.04998)
