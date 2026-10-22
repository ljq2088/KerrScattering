"""Build a scope-controlled review draft without overwriting the working paper."""
from pathlib import Path
import json
import re
import hashlib
import csv

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'docs/prd/kerr_scalar_nonlinear_GF_baseframe.tex'
TARGET = ROOT / 'docs/prd/kerr_scalar_nonlinear_prd_review_20261007.tex'
text = SOURCE.read_text(encoding='utf8')


def between(first, last):
    start = text.index(first)
    return text[start:text.index(last, start)]


abstract = r'''\begin{abstract}
We derive two asymptotic hierarchies for the first-order scalar energy-flux
response to local interactions $|\Phi|^{2n}\Phi$ on a fixed Kerr background.
At fixed incident amplitude and subextremal spin, cubic axisymmetric
absorption and its first-order correction have the same
$(M\omega)^{2\ell+2}$ power, with a spin-independent limiting ratio.
For the monopole this ratio is $\ln2/\pi$; higher interaction powers give
$M^{2n-2}\chi_{H,00}^{(n)}\sim c_n(M\omega)^{2n-2}$.
Near extremality at fixed $p/\kappa$, principal modes with
$h=1/2+i\beta$ concentrate the incident-normalized field in the throat.
Matching hypergeometric and Whittaker solutions and evaluating the
nonlinear Green integral give
$\widehat\chi_n=\sigma^{-n}{\cal F}_n(p/\kappa,\beta\ln\sigma)
+o(\sigma^{-n})$, where $\sigma=(r_+-r_-)/M$.
The coefficient has logarithmic period $\pi/\beta$ and is specified with
zero fitted parameters.  Spectral calculations test $(\ell,m)=(2,2),(3,3),(4,4)$,
$n=1,2,3$, and both signs of the horizon detuning.  Independent spectral
and quadrature refinements, coefficient tails, field-dependent radial
residuals and flux interference checks quantify numerical accuracy.
The resulting enhancement identifies a shrinking weak-coupling domain
near extremality.  These conclusions describe the stationary first-order
response under the stated normalization and matching conditions.
\end{abstract}
'''

intro = r'''\section{Introduction}

Black-hole scattering relates incident radiation to the flux reaching the
future horizon and the flux returning to infinity.  Linear scalar scattering
in Schwarzschild and Kerr spacetimes is well established
\cite{Sanchez1976,Futterman,GlampedakisAndersson2001}.  Its absorption and
reflection coefficients provide real-frequency observables complementary to
quasinormal-mode (QNM) spectra\cite{Berti2009,Kyutoku2023,Rosato2024}.
Linear axisymmetric absorption vanishes in the infrared, while its
fractional nonlinear response can remain finite.  Near extremality,
incident-normalized principal modes develop enhanced throat amplitudes.
Both effects are determined by the distribution and normalization of the
driving field.  The measurable first-order energy-flux response follows
from interference between the linear and sourced fields at fixed incident
radiation.

Several nonlinear problems must be distinguished.  Numerical evolutions of
incident gravitational radiation measure waveforms and Bondi fluxes
\cite{Zlochower2003,Frauendiener2021}; self-interacting massive scalar clouds
instead describe bound-state growth, level transfer, and collapse
\cite{YoshinoKodama2012,Baryakhtar2021}.  Nonlinear $Q$-clouds are synchronized
bound states with decay at infinity\cite{HerdeiroQCloud2014}.  Here the field
is massless, the driving frequency is real, and radiation is supplied from
infinity.  The calculation treats a stationary driven response on a prescribed
background.  Cloud evolution studies bound-state dynamics and spacetime
evolution includes gravitational backreaction.  Gravitational self-force
theory adds a worldline source, regularization, and gauge control
\cite{BarackPound2019,PoundWardell2021}.

Building on the fixed-background Green-function construction for
Schwarzschild scattering\cite{HeTianZhangManuscript2026}, we determine the
infrared and near-extremal structure of nonlinear scalar scattering on Kerr.
The central results link the interaction power to suppression in the
fixed-spin infrared limit and enhancement in the principal-mode throat.
Explicit connection coefficients and Green projections determine the
response under a common fixed-incident normalization.
Resonance-like peaks and finite-window exponential tails, also present in
the Schwarzschild reference, provide finite-frequency context for the
infrared hierarchy.  The Kerr formulation requires three changes.  The horizon
frequency is $p=\omega-m\Omega_H$, angular functions are spheroidal, and the
covariant source contains the factor $\Sigma=r^2+a^2\cos^2\theta$.  These
changes determine the radial operator, projected source and incident-normalized
flux response.
The exact relation $T^{(1)}+R^{(1)}=0$ then constrains the first-order flux
response, while off-diagonal angular channels first contribute to the
integrated energy flux at second order in the coupling.

Our main results separate the effects of black-hole penetration and local
self-interaction.  First, for cubic axisymmetric self channels, matching
the regular static solution to the far-zone wave gives the same
$\omega^{2\ell+2}$ power for linear absorption and its first-order
correction.  The spin-dependent penetration factor cancels in their ratio,
whose leading coefficient is fixed by a far-zone Bessel integral.
Second, the monopole admits the explicit complex response
$\rho_{H,00}\to\ln2/(2\pi)+i/4$: the absorbed-flux correction and the
horizon-phase correction are distinct parts of the same response.
Third, for $|\Phi|^{2n}\Phi$ the monopole fractional absorption response
scales as $\omega^{2n-2}$ with an analytically computable positive
coefficient.  The cubic case therefore remains unsuppressed relative to
linear absorption, whereas every higher local power is infrared
suppressed.  This hierarchy classifies the specified fixed-incident
scattering observable.

The second asymptotic path holds $y=p/\kappa$ fixed while $a/M\to1$.
For principal modes, $h=1/2+i\beta$ fixes the throat density envelope to
$\kappa^{-1}$ and the nonlinear source produces a $\kappa^{-n}$ relative
response envelope.  Two-branch interference supplies a log-periodic
coefficient.  We derive that coefficient by combining the analytic
near-superradiant connection\cite{BredbergKerrCFT2010} with the covariant
nonlinear Green projection.  A convergent throat integral and matching
denominators bounded away from zero specify the domain of this expansion.
Real-weight modes require the corresponding upper-limit convergence
analysis and full outer matching.

The fixed-spin frequency sweep uses $a/M=0.5$, $m=0$, and $\ell=0,1,2$.
The new principal-response grid contains $81$ physical parameter points:
three principal modes, three interaction orders, three nonzero detunings,
and three near-extremal spins.  Independent spectral and quadrature
refinements test the nonlinear coefficients.  The two sets of experiments
use the same covariant source and incident normalization.

Section~\ref{sec:problem} defines the field equation, source projection, and
flux observables.  Section~\ref{sec:methods} describes the endpoint spectral
solver and the independent accuracy diagnostics.  Section~\ref{sec:results}
derives the infrared and principal-mode responses and compares their
coefficients with numerical data, followed by finite-frequency curves and
the Schwarzschild limit.  The final
section discusses the physical interpretation and remaining limitations.
We use $G=c=\hbar=1$, metric signature $(-,+,+,+)$, and the Fourier convention
$e^{-i\omega t+im\phi}$.  Numerical frequencies are given in units $M=1$
unless stated otherwise.
'''

header = text[:text.index(r'\title{')]
header += r'''\title{Nonlinear scalar scattering on Kerr: infrared hierarchy and principal-mode enhancement}
\author{Jing-Qi Lai}
\email{laijingqi19@mails.ucas.ac.cn}
\affiliation{School of Physical Sciences, University of Chinese Academy of Sciences, Beijing 100049, China}
\author{Yu Tian}
\email[Corresponding author: ]{ytian@ucas.ac.cn}
\affiliation{School of Physical Sciences, University of Chinese Academy of Sciences, Beijing 100049, China}
\affiliation{Institute of Theoretical Physics, Chinese Academy of Sciences, Beijing 100190, China}
''' + '\n' + abstract + r'''
\maketitle
'''
problem = between(r'\section{Nonlinear scattering problem', r'\section{Methods}')
methods = between(r'\section{Methods}', r'\subsubsection{Low-frequency behavior}')
methods = methods.replace(
    'The functions $u_{\\rm in}$, $u_{\\rm down}$, and $u_{\\rm up}$ are regular\n'
    'on their respective subdomains that the degenerate endpoint rows of the\n'
    'transformed ODE can be used directly as boundary regularity conditions.',
    'The functions $u_{\\rm in}$, $u_{\\rm down}$, and $u_{\\rm up}$ are regular\n'
    'on their respective subdomains.  The degenerate endpoint rows of the\n'
    'transformed ODE therefore supply the boundary regularity conditions.')
endpoint = r'''
For the outer branch $f=r^{-1}e^{i\sigma\omega r_*}$, with
$\sigma=-1$ for down and $+1$ for up, the exact limits are
\begin{equation}
B_2(0)=0,\quad B_1(0)=-2i\sigma r_+\omega,
\quad B_0(0)=-(\lambda+2am\omega).
\label{eq:review-infinity-endpoint}
\end{equation}
The last expression is $-(A+a^2\omega^2)$ in the angular convention of
Eq.~\eqref{eq:review-infinity-endpoint}.  It reduces to $-\lambda$ for
the $m=0$ numerical samples in this paper.  Small flux-balance errors
cannot substitute for checking this endpoint relation against the
transformed differential equation.
'''
# The endpoint derivation is explicit; do not imply historical m!=0 data were rerun.
endpoint = endpoint.replace('in the angular convention of\nEq.~\\eqref{eq:review-infinity-endpoint}',
                            'with $\\lambda=A+a^2\\omega^2-2am\\omega$')
key = 'At the exact endpoint of each branch $B_2$ vanishes'
assert key in methods
methods = methods.replace(key, endpoint + '\n' + key)
methods = methods.replace('25 separately recomputed points', '43 points in the three tail-fit windows')
methods = methods.replace('the regular-singular relation', 'the endpoint compatibility relation')
methods = methods.replace(
    'exact collocation endpoint; no horizon truncation is introduced.',
    'exact collocation endpoint; no horizon truncation is introduced.  This\n'
    'algebraic endpoint condition does not classify infinity as a regular\n'
    'singular point: for nonzero frequency the compactified outer equation\n'
    'has an irregular singularity.  Phase peeling removes the leading\n'
    'oscillation, but need not make the amplitude analytic there.  Spectral\n'
    'coefficient decay and mesh-refinement tests therefore remain essential\n'
    '\\cite{HeTianZhangManuscript2026}.')
low = between(r'\subsubsection{Low-frequency behavior}', r'\subsubsection{High-frequency behavior}')
low = low.replace(r'\subsubsection{Low-frequency behavior}', r'\subsection{Infrared response and local-power hierarchy}', 1)
low = low.replace(
    'Thus the cubic interaction is infrared marginal for every axisymmetric\nself channel:',
    'Thus the cubic fractional response is unsuppressed in the infrared for\nevery axisymmetric self channel:')
low = low.replace(
    'Thus $n=1$ is infrared marginal and reproduces $c_1=\\ln2/\\pi$,\n'
    'whereas every $n>1$ operator is infrared irrelevant in this scattering\nobservable.',
    'Thus $n=1$ retains a finite infrared response and reproduces\n'
    '$c_1=\\ln2/\\pi$, whereas every $n>1$ interaction produces a\n'
    'power-suppressed fractional response in this scattering observable.')
low = low.replace(
    'This is qualitatively different from the $1/\\kappa$ growth of\n'
    'the cubic principal $\\ell=m\\ge2$ channels: increasing the local power\n'
    'does not manufacture a monopole throat enhancement.',
    'These paths provide numerical evidence for monopole suppression, not a\n'
    'proof of a uniform asymptotic expansion at extremality.  The fixed-spin\n'
    'matching argument and the fixed-$\\omega/\\kappa$ tests have distinct domains\n'
    'of validity.')
low = re.sub(r'OpenAI Codex \(GPT-5, accessed August 2026\) assisted with implementation.*?frozen data files\.\n', '', low, flags=re.S)
high = between(r'\subsubsection{High-frequency behavior}', r'\section{Results}')
high = high.replace(r'\subsubsection{High-frequency behavior}', r'\subsection{Finite-frequency fit diagnostics}')
finite = between(r'\section{Results}', 'We additionally test the self channel')
finite = finite[finite.index('\n\n') + 2:]
finite = finite.replace('Our main result on the Kerr nonlinear scattering coefficient is shown in',
                        'The finite-frequency cubic response is shown in')
finite = finite.replace('This differs from simply copying the\nSchwarzschild reduced-field statement and is therefore reported as a Kerr\nanalytic result with an independent numerical audit.',
                        'The comparison uses the fixed-incident normalization; the translation to\n'
                        'the reduced Schwarzschild convention is given in Appendix~\\ref{app:flux}.')
angular = between('The angular discretization is inexpensive', r'\subsection{Target-channel structure}')
angular = angular.replace(
    'and the weakest nonzero channel displayed\nin Table~\\ref{tab:channels}, $(2,2,0.30;6)$.',
    'and, as a separate angular-only stress test, the\n'
    'projector $(2,2,0.30;6)$.  The latter does not use a nonaxisymmetric\n'
    'radial solution and is not a nonlinear target-channel flux measurement.')
angular = angular.replace(r'\noindent\parbox[t]{0.96\columnwidth}{\small', '')
angular = angular.replace(r'\textit{Local field diagnostic.}\\',
                          r'\textit{Local field diagnostic.}')
angular = angular.replace('independent samples.  Across', 'independent samples.  Across')
angular = angular.replace('validation points.}\\', 'validation points.')
angular = angular.replace('values\n$2.8\\times10^{-10}$, $1.2\\times10^{-11}$, and $3.2\\times10^{-13}$.\\\\',
                          'values\n$2.8\\times10^{-10}$, $1.2\\times10^{-11}$, and $3.2\\times10^{-13}$.')
angular = angular.replace('global flux-balance residual.}', 'global flux-balance residual.')
spin = between(r'\subsection{Kerr-to-Schwarzschild continuity}', r'\section{Discussion and outlook}')
discussion = r'''\section{Discussion and conclusions}

Two controlled limits organize the nonlinear Kerr response.  At fixed
subextremal spin, the axisymmetric infrared response has an interaction-order
hierarchy.  At fixed nonzero $p/\kappa$, principal-mode scattering near
extremality has an inverse-surface-gravity envelope with logarithmic
modulation.  The matched source integrals and asymptotically flat incident
normalization determine both limits.

The flux formulation separates three quantities that can otherwise be
confused: a unit-horizon Green coefficient, the relative fixed-incident field
response, and the physical correction multiplied by the coupling and incident
amplitude.  The first quantity may grow at low frequency without producing a
divergent fractional absorption correction.  The exact identities
$T^{(0)}+R^{(0)}=1$ and $T^{(1)}+R^{(1)}=0$ express energy conservation;
they provide global checks alongside independent local residual,
spectral-tail, and quadrature-refinement diagnostics.

For the cubic axisymmetric self channels, matched asymptotics give
$T^{(0)},T^{(1)}\propto(M\omega)^{2\ell+2}$ at fixed subextremal spin.
Rotation changes the absolute coefficients, whereas the limiting ratio
is fixed by the far-zone Bessel integral.  In the monopole,
$\rho_{H,00}\to\ln2/(2\pi)+i/4$ and
$\chi_{H,00}\to\ln2/\pi$.  The real part governs the absorption change and
the imaginary part the horizon phase change.  This distinguishes the
nonlinear response from a statement about transmission alone.

The general monopole interaction gives
$M^{2n-2}\chi_{H,00}^{(n)}\sim c_n(M\omega)^{2n-2}$ with $c_n>0$.
The distinction between $n=1$ and $n>1$ is an observable infrared hierarchy:
the cubic fractional response remains finite, while the higher-power
responses vanish.  The $n=2,3$ numerical experiments evaluate the full source
independently of the asymptotic law.  The fitted powers characterize the
finite frequency windows.  At leading order in this fixed-spin infrared
limit, rotation changes the absolute penetration amplitude and the far-zone
integral fixes the fractional-response coefficient independently of spin.

For principal modes, $h=1/2+i\beta$ gives equal real powers for both overlap
branches.  Their matching produces $|B^{\rm inc}|^{-2}\sim\sigma^{-1}
|{\cal D}|^{-2}$.  The unit-horizon nonlinear Green integral converges for
every $n\ge1$, so the fixed-incident response has
$\widehat\chi_n=\sigma^{-n}{\cal F}_n(y,\beta\ln\sigma)+o(\sigma^{-n})$.
The real part of $h$ fixes the envelope; its imaginary part and the two
connection coefficients fix the log-periodic modulation.  The derived
$\Gamma$-function connections and source integrals determine the coefficient
with zero fitted parameters.  Fresh calculations for $(2,2),(3,3),(4,4)$,
$n=1,2,3$, and $y=-0.5,0.5,1$ test that prediction across three spins.
At $a/M=0.999999$, the leading matching differences range from about
$0.03\%$ to $2.42\%$, whereas independent numerical refinements have a
maximum quadrature change of $7.81\times10^{-5}$ and a maximum spectral
change of $6.55\times10^{-9}$.  These comparisons resolve finite-$\sigma$
matching corrections separately from numerical discretization effects.

The real-weight source convergence criterion supplies the corresponding
scope: $1/2<h<1$ gives a convergent throat power, $h=1$ gives a logarithmic
upper integral, and $h>1$ requires the outer-region contribution at leading
order.  The principal envelope thus has a precise modal origin.  It also
identifies a shrinking perturbative domain,
$|g_n||{\cal A}_{\rm in}|^{2n}(M\kappa)^{-n}\ll1$, on intervals with
a bounded nonzero response coefficient.

The finite-frequency curves have positive cubic absorption corrections over
the retained axisymmetric samples in our signed-coupling convention.  A
conventional positive quartic potential corresponds to the opposite sign of
the equation-level coupling and reverses this physical correction.  The
peaks occur near the fundamental scalar QNM frequency scale.  Extracting
QNM poles and residues requires a complex-frequency continuation.
Exponential tails describe the tested windows with fitted slopes; assigning
a thermal spectrum requires a separate test of the temperature relation.

The numerical error budget is resolved by observable and parameter window.
Near the
finite-frequency peak, off-grid residuals, coefficient tails, and paired
resolutions test the radial solution.  In the exponential-tail windows,
inner Green quadrature limits the response accuracy.  At the deepest
infrared points, reflected interference suffers cancellation, so the
horizon response is tested separately.  The localized residual maximum in
the higher-power monopole diagnostic is $1.6\times10^{-5}$, illustrating
the value of a local accuracy test alongside flux conservation and fit
quality.  The principal grid has a maximum homogeneous off-grid radial
residual of $1.37\times10^{-8}$ and a coefficient tail of
$6.82\times10^{-14}$.  A separate
interior reconstruction test is reported in Appendix~\ref{app:validation20261008};
it tests the reconstructed first-order field on the stated interior interval
alongside Green-quadrature refinement and boundary-flux checks.

The principal result extends the linear near-horizon connection framework
\cite{BredbergKerrCFT2010} by including the covariant nonlinear source and
its Green projection.  The numerical study covers the stated self channels
and fixed-detuning paths.  Further tests include higher modal indices,
additional detunings, the complete mode-coupled first-order field, and a
time-domain assessment of the shrinking perturbative domain.  A real
scalar with a $\Phi^3$ source additionally generates harmonics such as
$3\omega$; the present single-frequency closure follows from the complex
field and its $U(1)$-invariant interaction.  Nonlinear saturation and
gravitational backreaction require extensions beyond this first-order
fixed-background calculation.

\section*{Data and code availability}

The figures, numerical tables, and producing scripts are retained in the
local review package described in the accompanying reproducibility record.
The axisymmetric numerical inputs are unchanged by this editorial revision.
A versioned public release and persistent identifier remain to be supplied
before submission.
Completed solver calls and accepted manuscript points are distinguished in
the CSV data.  The fresh principal grid includes its input hashes, analytic
coefficient checks, and separate spectral and quadrature comparisons.

\section*{Acknowledgments}

This research is supported in part by the National Key R\&D Program of
China, grant number 2020YFC2201300, and the National Natural Science
Foundation of China, grant numbers 12035016, 12375058 and 12361141825.

OpenAI Codex assisted with drafting, derivation cross-checks, code review,
and numerical postprocessing.  Responsibility for the scientific content,
references, and conclusions rests with the human authors.
'''
appendix = between(r'\appendix', r'\begin{thebibliography}')
appendix = appendix.replace(r'\subsection{Schwarzschild normalization correspondence}',
    r'''\subsection{Schwarzschild normalization correspondence}

The reference manuscript\cite{HeTianZhangManuscript2026} writes
$\Box\phi=\lambda_{\rm ref}|\phi|^{2N-2}\phi$.  Its interaction index
and equation-level coupling are related to ours by
\begin{equation}
N=n+1,\qquad \epsilon_n=-\lambda_{\rm ref}.
\end{equation}
The amplitude relations below use a common source-sign convention.
When applying them directly to a first-order amplitude quoted per
$\lambda_{\rm ref}$, the opposite source sign must also be included.
The physical flux correction agrees only after both coupling and
normalization have been translated.
''')
validation = r'''
\section{Independent local and endpoint validation}
\label{app:validation20261008}

The main text combines axisymmetric infrared and finite-frequency data with
the freshly computed principal-mode grid in
Sec.~\ref{sec:principal20261014}.  This appendix documents the endpoint
identities and the representative local sourced-field tests that preceded
the expanded principal-mode calculation.

\subsection{Cancellation-free peeled coefficients}

Write $H=r^2+a^2$, $K=\omega H-am$, and
$p=\omega-m\Omega_H$.  If $R=Fu$, the coefficient multiplying $u$ is
\begin{equation}
B_0=\Delta(q'+q^2)+\Delta' q+K^2/\Delta-\lambda,
\qquad q=F'/F.
\end{equation}
For $F=r^{-1}\exp(i\sigma\omega r_*)$, $\sigma=\pm1$, direct substitution
and cancellation before floating-point evaluation give
\begin{equation}
\begin{split}
B_0^{\sigma}={}&\frac{am(am-2\omega H)}{\Delta}-\lambda
-\frac{2i\sigma\omega a^2}{r}\\
&-\frac{2M}{r}+\frac{2a^2}{r^2}.
\end{split}
\label{eq:outerfactored20261008}
\end{equation}
Consequently the exact infinity row is
$B_0(0)=-\lambda-2am\omega=-(A+a^2\omega^2)$, not $-\lambda$.
The difference vanishes for $m=0$ or $a=0$.
For $F=\exp(-ipr_*)$, the identity
$K-pH=(\omega-p)(r-r_+)(r+r_+)$ gives
\begin{equation}
B_0^{\mathrm{in}}=
\frac{(\omega-p)(r+r_+)(K+pH)}{r-r_-}
-2ipr-\lambda.
\label{eq:innerfactored20261008}
\end{equation}
This removes the apparent division by $r-r_+$ without moving the horizon
boundary.  The normalization remains $u(1)=1$ and the degenerate ODE row
remains in the matrix.  Neither expression changes the differential equation.

We tested $a/M=0.99,0.999$, $\ell=m=1,2$, and $n=1,2$ at
$p/\kappa=0.5$.  The spectral degrees were $128,176,224$, with
$r_{\rm match}/M=12$ and Gauss orders $2N$.  A further run at $N=224$
used the erroneous infinity row solely to quantify its effect.  The
corrected maximum homogeneous radial relative residual across these probes
was $3.2\times10^{-9}$; the maximum peeled-amplitude relative residual was
$5.2\times10^{-8}$.  Both denominators contain the corresponding field
terms.  The erroneous row changes the tested responses only at the
$10^{-8}$ level or below, but produces spurious outer spectral tails.
This limited observation neither validates all historical nonaxisymmetric
points nor invalidates their physical trends by itself.

At $a/M=0.999$, $\ell=m=2$, the $N=176\to224$ fractional change in the
cubic response was $1.6\times10^{-6}$ when the quadrature order also changed.
At fixed $N=224$, increasing the Gauss order from $448$ to $1792$ gives a
similar change.  Thus a paired-degree test alone cannot identify the
limiting error.  Matching radii $8M,12M,16M$ were also checked independently.
These are finite-parameter consistency tests, not an asymptotic exponent fit.

\subsection{Local residual of the sourced field}

Let $Q=(r^2C_0+a^2C_2)|R_0|^{2n}R_0$ denote the projected source without
its minus sign, and $V=K^2/\Delta-\lambda$.  With unit-horizon $R_{\rm in}$
and unit-outgoing $R_{\rm up}$, reconstruct
\begin{equation}
R_1(r)=-\frac{R_{\rm up}(r)I_{\rm in}(r)
                    +R_{\rm in}(r)I_{\rm up}(r)}{W},
\end{equation}
where
\begin{align}
I_{\rm in}(r)&=\int_{r_+}^{r}R_{\rm in}(s)Q(s)\,ds,\\
I_{\rm up}(r)&=\int_r^\infty R_{\rm up}(s)Q(s)\,ds,\\
W&=\Delta(R_{\rm in}R_{\rm up}'-R_{\rm up}R_{\rm in}').
\end{align}
To avoid replacing a numerical test by a Green-function identity, we
evaluate these integrals at reconstruction nodes and differentiate their
Chebyshev interpolant, rather than setting $R_1''$ from the ODE.  The
independent local diagnostic is
\begin{equation}
\delta_1(r)=\frac{|\Delta R_1''+\Delta'R_1'+VR_1+Q|}
{|\Delta R_1''|+|\Delta'R_1'|+|VR_1|+|Q|}.
\label{eq:sourcedresidual20261008}
\end{equation}
The field factors in this denominator are essential for invariance under
a common rescaling of the first-order field and its source.

The homogeneous degree is $224$.  The initial horizon-to-$3M$ integrals
use $1024$ open Gauss nodes, the local cumulative increments use $128$
nodes, and the global outgoing-source integral retains the infinite-tail
calculation.  We reconstruct on $3M\le r\le8M$ with degrees
$16,24,32,48,64$ and validate at $600$ Chebyshev--Gauss points different
from the reconstruction nodes.  Cases A and B have $a/M=0.5$,
$\ell=m=0$, $M\omega=0.1$, with $n=1,2$, respectively.  Case C has
$a/M=0.99$, $\ell=m=2$, $p/\kappa=0.5$, and $n=1$.
Table~\ref{tab:sourced20261008} reports all reconstruction degrees;
none was selected by minimizing the residual after the calculation.

The decrease at low degree followed by a nonmonotonic floor is consistent
with spectral truncation giving way to numerical interpolation and
differentiation error.  At degree $32$, maxima are below
$2.3\times10^{-9}$ for all three cases.  This verifies the local sourced
equation on the stated interval, not the accuracy of the accumulated
homogeneous integration constants or the omitted asymptotic intervals.
Global flux/quadrature checks are still needed.  No global
machine-precision accuracy claim follows from this test.
'''
with (ROOT / 'results/kerr_scalar_sourced_local_residual_20261008.csv').open(newline='', encoding='utf8') as handle:
    local_rows = list(csv.DictReader(handle))
validation += r'''
\begin{table*}[t]
\caption{Independent sourced-field residual and coefficient tail on
$[3M,8M]$.  $D$ is the reconstruction degree; the homogeneous degree is
fixed.  The tail is the maximum of the last eight coefficient magnitudes
divided by the maximum coefficient magnitude.}
\label{tab:sourced20261008}
\small
\begin{ruledtabular}
\begin{tabular}{ccccc}
Case & $D$ & $\max\delta_1$ & median $\delta_1$ & tail\\
'''
for row in local_rows:
    case = 'C' if int(row['m']) else ('A' if int(row['n']) == 1 else 'B')
    def scientific_latex(value):
        mantissa, exponent = f"{float(value):.2e}".split('e')
        return '$' + mantissa + r'\times10^{' + str(int(exponent)) + '}$'
    validation += (f"{case} & {row['N_reconstruction']} & "
                   + ' & '.join(scientific_latex(row[key]) for key in
                     ('relative_residual_max', 'relative_residual_median', 'coeff_tail'))
                   + r'\\' + '\n')
validation += r'''\end{tabular}
\end{ruledtabular}
\end{table*}
\begin{figure*}[t]
\includegraphics[width=0.95\textwidth]{../../figures/kerr_scalar_sourced_local_validation_20261008.png}
\caption{Independent local first-order-field validation.  Left: maximum
field-dependent sourced residual on $600$ validation nodes.  Right:
relative coefficient tail.  Cases and degrees are identical to
Table~\ref{tab:sourced20261008}.  The high-degree residual floor is shown
explicitly; a smaller coefficient tail does not guarantee a smaller
second-derivative residual.}
\label{fig:sourced20261008}
\end{figure*}
'''
float_start = validation.index(r'\begin{table*}')
validation_floats = validation[float_start:]
validation = validation[:float_start].replace(
    r'\subsection{Cancellation-free peeled coefficients}',
    validation_floats + r'\subsection{Cancellation-free peeled coefficients}', 1)

principal = (ROOT / 'docs/prd/principal_mode_section_20261014.tex').read_text(encoding='utf8')
principal = principal.replace(r'\input{principal_expanded_tables_20261014.tex}',
    (ROOT / 'docs/prd/principal_expanded_tables_20261014.tex').read_text(encoding='utf8'))

result = (header + intro + problem + methods + angular + high
          + '\n\\section{Results}\n\\label{sec:results}\n' + low
          + '\n' + principal
          + '\n\\subsection{Finite-frequency cubic response}\n' + finite
          + spin + discussion + appendix + validation)
result = result.replace(
    'the $m=0$ numerical samples in this paper.  Small flux-balance errors\n'
    'cannot substitute for checking this endpoint relation against the\n'
    'transformed differential equation.',
    'the axisymmetric numerical samples.  The exact endpoint row is checked\n'
    'directly against the transformed differential equation for all $m$.')
result = result.replace(
    'exact collocation endpoint; no horizon truncation is introduced.  This\n'
    'algebraic endpoint condition does not classify infinity as a regular\n'
    'singular point: for nonzero frequency the compactified outer equation\n'
    'has an irregular singularity.  Phase peeling removes the leading\n'
    'oscillation, but need not make the amplitude analytic there.',
    'exact collocation endpoint.  For nonzero frequency, infinity is an\n'
    'irregular singular point of the compactified outer equation.  Phase\n'
    'peeling removes the leading oscillation; endpoint regularity of the\n'
    'remaining amplitude is tested through its spectral convergence.')
result = result.replace(
    'This limited observation neither validates all historical nonaxisymmetric\n'
    'points nor invalidates their physical trends by itself.',
    'The freshly computed grid in Sec.~\\ref{sec:principal20261014} uses\n'
    'the corrected endpoint coefficients throughout.')
result = result.replace(
    'similar change.  Thus a paired-degree test alone cannot identify the\n'
    'limiting error.  Matching radii $8M,12M,16M$ were also checked independently.\n'
    'These are finite-parameter consistency tests, not an asymptotic exponent fit.',
    'similar change, identifying quadrature as a separate error source.\n'
    'Matching radii $8M,12M,16M$ were also checked independently.\n'
    'These tests quantify consistency at the stated finite parameters.')
# Keep only references actually used by this scoped paper, without inventing metadata.
cited = set()
citation_order = []
for group in re.findall(r'\\cite\w*\{([^}]+)\}', result):
    for key in group.replace('\n', '').split(','):
        key = key.strip()
        if key not in cited:
            citation_order.append(key)
            cited.add(key)
blocks = re.findall(r'\\bibitem\{([^}]+)\}(.*?)(?=\\bibitem|\\end\{thebibliography\})',
                    text[text.index(r'\begin{thebibliography}'):], re.S)
blocks.append(('HeTianZhangManuscript2026', r'''
Z.-T. He, Y. Tian, and H. Zhang,
Nonlinear scattering problem in black hole spacetimes,
supplied manuscript, version dated June 15, 2026.
'''))
assert cited <= {key for key, block in blocks}
result += '\n\\begin{thebibliography}{99}\n'
by_key = dict(blocks)
result += ''.join('\\bibitem{' + key + '}' + by_key[key] for key in citation_order)
result += '\\end{thebibliography}\n\\end{document}\n'
labels = re.findall(r'\\label\{([^}]+)\}', result)
refs = set(re.findall(r'\\(?:ref|eqref)\{([^}]+)\}', result))
assert len(labels) == len(set(labels))
assert not refs - set(labels), sorted(refs - set(labels))
TARGET.write_text(result, encoding='utf8')
record = {
    'source': str(SOURCE.relative_to(ROOT)),
    'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
    'target': str(TARGET.relative_to(ROOT)),
    'retained_labels': labels,
    'retained_citations': sorted(cited),
    'scope': 's=0 axisymmetric infrared and finite-frequency results; analytic near-extremal principal law with 81 freshly verified points for l=m=2,3,4, n=1,2,3, y=-0.5,0.5,1',
    'omitted_from_candidate': 'Historical nonaxisymmetric scans superseded by the fresh principal-mode grid',
    'historical_source_preserved': True,
    'author_and_funding_reference': 'https://cn.overleaf.com/project/69bb9d12f9a917663fb9b9c0; DGF.tex author block and acknowledgments, read 2026-10-08; author selection and funding reuse instructed by user',
    'authors': ['Jing-Qi Lai', 'Yu Tian'],
    'corresponding_author': 'Yu Tian',
    'funding_identifiers': ['2020YFC2201300', '12035016', '12375058', '12361141825'],
    'new_numerical_scans': True,
    'validation_date': '2026-10-14',
    'validation_scope': 'Independent spectral and quadrature refinements for all 81 principal points; homogeneous off-grid residuals; analytic ODE, current, periodicity and integral refinements; representative local sourced residual probes',
    'validation_inputs': {
        str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in [ROOT / 'results/kerr_scalar_endpoint_audit_20261008.csv',
                     ROOT / 'results/kerr_scalar_endpoint_factored_audit_20261008.csv',
                     ROOT / 'results/kerr_scalar_endpoint_quadrature_match_20261008.csv',
                     ROOT / 'results/kerr_scalar_sourced_local_residual_20261008.csv',
                     ROOT / 'src/kerr_scalar_spectral.py',
                     ROOT / 'scripts/audit_scalar_endpoint_20261008.py',
                     ROOT / 'scripts/refine_scalar_endpoint_20261008.py',
                     ROOT / 'scripts/check_scalar_sourced_residual_20261008.py',
                     ROOT / 'scripts/plot_scalar_sourced_residual_20261008.py',
                     ROOT / 'figures/kerr_scalar_sourced_local_validation_20261008.png',
                     ROOT / 'results/kerr_scalar_principal_expanded_comparison_20261014.csv',
                     ROOT / 'results/kerr_scalar_principal_expanded_quality_20261014.csv',
                     ROOT / 'results/kerr_scalar_principal_expanded_analytic_checks_20261014.csv',
                     ROOT / 'results/kerr_scalar_principal_expanded_manifest_20261014.json',
                     ROOT / 'scripts/validate_principal_expanded_20261014.py',
                     ROOT / 'scripts/plot_principal_expanded_20261014.py',
                     ROOT / 'docs/prd/principal_mode_section_20261014.tex',
                     ROOT / 'docs/prd/principal_expanded_tables_20261014.tex',
                     ROOT / 'figures/kerr_scalar_principal_expanded_20261014.png']
    },
}
(ROOT / 'docs/prd/prd_review_20261007_manifest.json').write_text(
    json.dumps(record, ensure_ascii=False, indent=2), encoding='utf8')
print(f'{TARGET.name}: {len(labels)} labels, {len(cited)} cited sources')
