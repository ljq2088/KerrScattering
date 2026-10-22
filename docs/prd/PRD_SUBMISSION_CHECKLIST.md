# PRD Submission Checklist

Active manuscript:

- `docs/prd/kerr_scalar_nonlinear_GF_baseframe.tex`
- `docs/prd/kerr_scalar_nonlinear_GF_baseframe.pdf`

This checklist records the current submission-level state of the Kerr scalar
nonlinear-scattering manuscript.  It is stricter than a successful local PDF
build: the manuscript can be internally reproducible while still lacking final
author metadata.

## External Guidance Used

- APS web submission guidance identifies author and affiliation entry, open
  science information, data availability, title/abstract, subject
  classification, and final manuscript-file upload as submission steps:
  https://journals.aps.org/authors/web-submission-guidelines-physical-review
- APS data-availability guidance says authors are asked to enter a statement
  describing the availability of relevant data and software:
  https://journals.aps.org/authors/data-availability-statements
- APS style basics also flags the data availability statement as a submission
  item:
  https://journals.aps.org/authors/style-basics
- APS requires substantive AI assistance with derivations, code, simulations,
  data analysis, or scientific drafting to be disclosed with the tool,
  purpose, and author verification:
  https://journals.aps.org/authors/appropriate-use-ai-tools
- The APS Author Guide for REVTeX 4.2 says REVTeX should handle author and
  affiliation grouping, with one `\author` macro per author and optional
  `\email` for an author's email address:
  https://ctan.math.illinois.edu/macros/latex/contrib/revtex/aps/apsguide4-2.pdf
- arXiv reference guidance says arXiv identifiers should be included in the
  standard `arXiv:YYMM.NNNN [category]` form when citing arXiv works:
  https://info.arxiv.org/help/faq/references.html

## Current Local Status

| Item | Status | Evidence |
| --- | --- | --- |
| REVTeX PRD class | PASS | `\documentclass[aps,prd,twocolumn,...]{revtex4-2}` in the active TeX source. |
| Manuscript builds cleanly | PASS | `python scripts/build_prd_manuscript.py` passes. |
| Figure/CSV artifacts are frozen | PASS | `docs/prd/artifact_manifest.json` is checked by `scripts/check_prd_artifacts.py`. |
| Manuscript table numbers match CSVs | PASS | `scripts/check_prd_manuscript_numbers.py` passes. |
| PRD style and structure audit | PASS | `scripts/check_prd_style.py` verifies REVTeX options, required sections, abstract, cross-references, data/code statement, active scope, fixed-frequency complex-field closure, flux normalization, and residual definitions. |
| Data/code availability text | PASS | The manuscript states the current review-stage access route and the planned versioned public archive without presenting the moving development branch as a frozen release. |
| AI-use disclosure | PASS | The Methods and Acknowledgments identify OpenAI Codex, its uses in code/numerics/drafting, and the authors' independent verification and responsibility. |
| Public archive citation | PREPUBLICATION | Deposit the frozen data/software package in a versioned archive and replace the provisional data statement with a persistent data citation before publication.  APS requires publicly shared data and software to be cited in the reference list. |
| Cover letter template | PASS | `docs/prd/cover_letter.template.md` contains a PRD-ready cover-letter draft to finalize with real corresponding-author details. |
| Final metadata file | BLOCKED | `docs/prd/submission_metadata.json` has not yet been created from the template with final author and reference details. |
| Final cover letter | BLOCKED | `docs/prd/cover_letter.md` is generated only after final metadata is available. |
| Visual PDF sanity check | PASS | The latest rendered PDF pages have no overlapping text, clipped figures, or stuck-float warning. |
| Author list | BLOCKED | `\author{Author list to be inserted}` is the only intentionally unfinished manuscript block. |
| Affiliations | BLOCKED | Affiliations will be supplied together with the final author list. |
| Corresponding email | BLOCKED | No `\email{...}` command is present. |
| Schwarzschild companion citation | PASS | The active manuscript does not cite an unpublished local companion; a formal companion reference is optional. |
| Final submission package | BLOCKED | `scripts/check_prd_submission_ready.py` fails only until the external author metadata, final metadata file, and cover letter are supplied. |

## Physics And Numerical Claims

The current draft makes only the claims supported by the tracked data:

- Kerr scalar field, spin weight `s=0`.
- The nonlinear field is complex and the `U(1)`-invariant
  $|\Phi|^2\Phi$ source closes at the incident $(\omega,m)$.  The manuscript
  explicitly distinguishes this from a real-scalar $\Phi^3$ problem, which
  would generate additional temporal harmonics.
- The perturbative coefficient $\epsilon$ is signed.  In the action convention
  used in the paper, a conventional positive quartic potential
  $V=\lambda|\Phi|^4/2$ corresponds to $\epsilon=-\lambda$.
- $T^{(1)}$ and $R^{(1)}$ are quoted per unit incident-amplitude squared.  For
  general incident amplitude ${\cal A}_{\rm in}$, the physical correction is
  $\epsilon|{\cal A}_{\rm in}|^2(T^{(1)},R^{(1)})$ to first order.
- Axisymmetric sample: `a=0.5`, `m=0`, `l=0,1,2`.
- Self-channel first-order flux coefficients, justified because only the
  target channel that matches the zeroth-order angular mode interferes in the
  total flux at order epsilon.
- A representative non-axisymmetric target-channel matrix at
  `(a,l,m,M omega)=(0.5,2,2,0.30)`, with dominant reflected amplitudes
  converged separately from cancellation-limited horizon amplitudes.
- A bounded non-axisymmetric `a=0.5, l=m=2` scan crossing
  `m Omega_H=0.2679491924`, with accepted signed-flux points on both sides of
  the superradiant threshold and explicit rejection of cancellation-limited
  near-threshold points.
- Accuracy is assessed internally by Chebyshev coefficient tails, the radial
  Teukolsky residual with the field-dependent denominator on 1800 off-grid
  validation points, and the linear and first-order flux balances.
- The spheroidal basis and angular Gauss--Legendre quadrature have a separate
  tracked convergence audit; active-setting changes are at or below
  `5.3e-14` relative to a larger angular reference calculation.
- The high-frequency fit is described as a finite-window effective temperature,
  not as a proof of an exact theorem.  A 25-point $q=2048$ tail data set is
  compared against a power law with AICc and leave-one-out diagnostics, and a
  three-point $q=1792$--$2048$ convergence audit bounds the representative
  relative changes in $T^{(1)}$ by $2.5\times10^{-4}$.
- A common first-order balance gate removes cancellation-limited low-frequency
  rows before plotting or fitting.  The lowest displayed frequencies are
  `M omega=0.02,0.12,0.28` for `l=0,1,2`; a separate tracked scan changes either
  first-order flux coefficient there by at most `2.0e-8`.
- The scalar-monopole far-zone calculation is extended analytically to every
  positive integer `n` in the `|Phi|^(2n) Phi` family.  It predicts
  `M^(2n-2) chi_H = c_n (M omega)^(2n-2) + o(...)`, with a positive finite-sum
  coefficient.  The cubic member is infrared marginal and every `n>1` member
  is infrared suppressed.
- Independent `n=2,3` fixed-frequency scans recover the analytic coefficients
  with maximum extrapolation error `2.8e-6`; the largest paired-resolution
  response change is `2.5e-6`.  Fixed `omega/kappa=0.025` high-spin fits give
  powers `2.00734` and `4.01128`, resolving the predicted `kappa^2` and
  `kappa^4` suppression rather than a monopole near-extremal enhancement.
- The higher-power homogeneous audit has Chebyshev tail ratio at most
  `5.2e-14`; across 1800 field-dependent off-grid residual samples, the median,
  95th percentile, and localized maximum are `2.7e-10`, `2.1e-7`, and
  `1.6e-5`.  Cancellation-limited reflected coefficients at the smallest
  responses are not used for physical fits.

## Finalization Steps

1. Copy `docs/prd/submission_metadata.template.json` to
   `docs/prd/submission_metadata.json`.
2. Fill in the final author names, affiliations, and at least one corresponding
   author email.  Also review the `submission` object for the journal,
   manuscript type, corresponding author, cover-letter template/output paths,
   and data availability statement.
3. Apply the metadata:

   ```powershell
   python scripts/apply_prd_submission_metadata.py docs/prd/submission_metadata.json
   ```

4. Rebuild and audit:

   ```powershell
   python scripts/build_prd_manuscript.py
   python scripts/check_prd_style.py
   python scripts/check_prd_submission_ready.py
   ```

5. Render the final cover letter from the same metadata:

   ```powershell
   python scripts/render_prd_cover_letter.py docs/prd/submission_metadata.json
   ```

This writes `docs/prd/cover_letter.md` and checks that the corresponding
author exists in the author list and has an email address.  If
`submission.cover_letter_output` is set in the metadata file, that path is
used as the default output.
6. Re-run the readiness audit.  It now checks the final metadata file and the
   generated cover letter in addition to the manuscript TeX/PDF:

   ```powershell
   python scripts/check_prd_submission_ready.py
   ```

7. Build the final package only after the readiness audit passes:

   ```powershell
   python scripts/build_prd_submission_package.py
   ```

   The package builder includes the final `docs/prd/submission_metadata.json`
   and generated `docs/prd/cover_letter.md` when those files exist, in addition
   to the templates and reproducibility artifacts.

Until those steps pass, use only the draft package:

```powershell
python scripts/build_prd_submission_package.py --allow-draft
```

Before publication, deposit the exact accepted data/software package in a
versioned public archive (for example, Zenodo), add the archive citation to the
reference list, and update the Data and code availability statement with the
persistent identifier.  This is a prepublication data-policy step rather than
a blocker to the initial referee PDF.
