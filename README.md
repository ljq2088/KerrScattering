# KerrScattering

## October 23, 2026 Cross-Device Handoff

Start with **[HANDOFF.md](HANDOFF.md)** for the current manuscripts, verified
PDFs, numerical evidence, setup commands, conventions, and next research tasks.
Use branch **`prd-kerr-scalar-submission`** for this complete snapshot.

- Current PRD source: [review manuscript](docs/prd/kerr_scalar_nonlinear_prd_review_20261007.tex).
- Current compiled main paper: [26-page PDF](output/overleaf_20261023/prd_narrative_20261023.pdf).
- New extreme-frequency research: [Chinese note](output/pdf/kerr_precision_flux_phase_20261023.pdf),
  [21 paired results](results/precision_20261023/comparison.csv), and
  [BigFloat scalar solver](src/kerr_scalar_precision.jl).
- New portable run entry: `python scripts/run_scalar_precision.py --help`.
- Verify the downloaded snapshot: `python scripts/verify_handoff.py`.
- Full analysis dependencies: `python -m pip install -r requirements-research.txt`.

The supplied Schwarzschild reference `nonlinear_GF.pdf` stays local and is
excluded from the handoff. Current Kerr manuscripts and their data are included.
The new high-precision results are in the separate review note; the main paper
received narrative-only revisions. The sections below document the established
workflow and historical development.

Chebyshev spectral solvers for scalar scattering and weak nonlinear
Green-function amplitudes.  The current active branch focuses on the scalar
Teukolsky equation on Kerr, `s=0`.

## Current Scope

The active physics target is the scalar field on Kerr:

```text
s = 0
Box Phi + epsilon |Phi|^2 Phi = 0
```

Previous non-scalar benchmark utilities are not part of the current scalar
nonlinear scattering conclusion or documentation flow.

## Main Results

- Endpoint-collocation Kerr scalar spectral solver using `z = r_+/r`.
- Direct inclusion of infinity (`z=0`) and the horizon (`z=1`) as collocation
  endpoints.
- Linear amplitude extraction for `B_inc` and `B_ref` by matching in/down/up
  homogeneous solutions.
- GSN benchmark validation on 37 usable scalar cases:
  - worst amplitude-magnitude error: `1.485e-8`;
  - worst flux residual: `3.714e-9`.
- 51-point scalar frequency sweep resolving superradiance only for
  `omega < m Omega_H`.
- Kerr-covariant cubic scalar source

  ```text
  Q = (r^2 C0 + a^2 C2) |R|^2 R
  ```

  for weak nonlinear Green-function amplitudes.
- Exterior nonlinear tail integration by explicit phase-channel Fourier
  quadrature.
- PRD-style Kerr `s=0` nonlinear scattering draft for the axisymmetric
  `a=0.5`, `m=0`, `ell=0,1,2` frequency sweep:
  `docs/prd/kerr_scalar_nonlinear_GF_baseframe.pdf`.

## Important Files

- `src/kerr_scalar_spectral.py`
  Two-domain Chebyshev spectral solver for scalar Kerr in modes.

- `src/teukolsky_scalar.py`
  Scalar spheroidal harmonics, angular eigenvalues, Teukolsky lambda, and
  cubic angular projectors.

- `src/kerr_scalar_nonlinear.py`
  Kerr-covariant weak nonlinear source and Green-function amplitudes.

- `scripts/adaptive_kerr_scalar_gsn_validation.py`
  Adaptive validation against GeneralizedSasakiNakamura.jl scalar benchmarks.

- `scripts/run_kerr_scalar_frequency_sweep.py`
  Scalar frequency sweep and superradiance data.

- `scripts/run_kerr_scalar_nonlinear_diagnostics.py`
  Self-channel weak nonlinear amplitude diagnostics.

- `scripts/run_kerr_scalar_nonlinear_channels.py`
  Multi-`l'` weak nonlinear target-channel amplitudes.

- `scripts/run_kerr_scalar_nonlinear_channel_convergence.py`
  Multi-`l'` spectral-order and quadrature convergence checks.

- `scripts/run_kerr_scalar_nonlinear_control_scan.py`
  Spectral-order and matching-radius control scan for nonlinear amplitudes.

- `docs/kerr_scalar_current_work_zh.pdf`
  Current Chinese derivation and status report for the scalar `s=0` project.

- `AGENTS.md`
  Persistent project guidance for the gravitational-physics research agent.

- `.agents/skills/gravity-theory-research/SKILL.md`
  Reusable workflow for Kerr perturbation theory, EMRI/self-force literature,
  spectral numerics, and reproducible manuscript work.

- `docs/agent/RESEARCH_AGENT_ARCHITECTURE.md`
  Chinese description of the agent layers and local MCP boundary.

- `docs/literature/gravity_literature_map.md`
  Staged reading map for Teukolsky theory, EMRIs, Green functions, radiation
  reaction, self-force, and second-order perturbation theory.

- `docs/literature/deep_learning_curriculum.md`,
  `docs/literature/convention_ledger.md`, and
  `docs/literature/paper_cards.md`,
  `docs/literature/study_log_2026-07-14.md`
  Technical reading curriculum, cross-paper convention ledger, and reusable
  paper cards for EMRI, gravitational-wave, self-force, and nonlinear Kerr
  work, with the latest verified transfer conclusions.

- `tools/mcp/gravity_research_server.py`
  Local read-only-first MCP bridge for arXiv, Zotero, Mathematica, and the
  project literature cards.

- `docs/prd/kerr_scalar_nonlinear_GF_baseframe.tex`
  Active REVTeX/PRD-style Kerr scalar nonlinear-scattering manuscript.

- `docs/prd/kerr_scalar_nonlinear_GF_baseframe.pdf`
  Compiled PDF of the active manuscript.

## Quick Start

Install the frozen numerical environment and test runner in an isolated
environment:

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements-dev.txt
.venv/Scripts/python -m pytest -q
```

Research-agent smoke checks:

```bash
python scripts/check_mcp_server.py
python scripts/build_literature_manifest.py
python scripts/check_literature_catalog.py
python scripts/check_research_setup.py
```

```bash
python scripts/adaptive_kerr_scalar_gsn_validation.py
python scripts/run_kerr_scalar_frequency_sweep.py
python scripts/run_kerr_scalar_cubic_projector.py
python scripts/run_kerr_scalar_nonlinear_diagnostics.py
python scripts/run_kerr_scalar_nonlinear_channels.py
python scripts/run_kerr_scalar_nonlinear_channel_convergence.py
python scripts/run_kerr_scalar_nonlinear_control_scan.py
python scripts/build_kerr_scalar_validation_report.py
```

Plotting:

```bash
python scripts/plot_kerr_scalar_validation.py
python scripts/plot_kerr_scalar_frequency_sweep.py
python scripts/plot_kerr_scalar_low_frequency_axisymmetric.py
python scripts/plot_kerr_scalar_nonlinear_axisymmetric_base_like.py
python scripts/plot_kerr_scalar_axisymmetric_accuracy.py
python scripts/run_prd_axisymmetric_low_frequency_convergence.py
python scripts/analyze_kerr_scalar_modal_powerlaws.py
```

Near-extremal modal power laws use separate threshold and fixed-detuning
paths.  The production grid can be reproduced with

```bash
python scripts/run_kerr_scalar_near_extremal_scaling.py --output results/kerr_scalar_modal_powerlaw_N144.csv --spins 0.98,0.99,0.995,0.997,0.999 --modes 1:1,2:2,3:3,4:4,5:5,2:1,3:2 --detunings=-0.5,-0.05,-0.025,0.025,0.05,0.5,1.0 --N 144 --quad-order 144
python scripts/run_kerr_scalar_near_extremal_scaling.py --output results/kerr_scalar_modal_powerlaw_N176.csv --spins 0.98,0.99,0.995,0.997,0.999 --modes 1:1,2:2,3:3,4:4,5:5,2:1,3:2 --detunings=-0.5,-0.05,-0.025,0.025,0.05,0.5,1.0 --N 176 --quad-order 176
python scripts/analyze_kerr_scalar_modal_powerlaws.py
```

The analysis labels `y=0` only after symmetrizing `y=+/-0.025,+/-0.05`
and Richardson extrapolating to `p=0`.  The `y=-0.5,0.5,1` fits use the raw
fixed-`p/kappa` rows and are never mixed with that threshold extrapolation.

The `|Phi|^(2n) Phi` near-extremal extension uses the same path definition and
adds the nonlinearity order to every checkpoint key:

```bash
python scripts/run_kerr_scalar_power_near_extremal.py --output results/kerr_scalar_power_near_extremal_N144.csv --orders 2,3 --spins 0.98,0.99,0.995,0.997,0.999 --modes 1:1,2:2 --detunings=-0.5,-0.05,-0.025,0.025,0.05,0.5,1 --N 144 --quad-order 144
python scripts/run_kerr_scalar_power_near_extremal.py --output results/kerr_scalar_power_near_extremal_N176.csv --orders 2,3 --spins 0.98,0.99,0.995,0.997,0.999 --modes 1:1,2:2 --detunings=-0.5,-0.05,-0.025,0.025,0.05,0.5,1 --N 176 --quad-order 176
python scripts/analyze_kerr_scalar_power_near_extremal.py
python scripts/run_kerr_scalar_power_angular_convergence.py
```

The frozen data add `(2,1)` and `(3,3)` controls and repeat the three highest
spins at `N=224/256`; the exact commands and accepted-row policy are recorded
in `docs/prd/README.md` and `results/README.md`.

Build the active manuscript:

```bash
cd docs/prd
pdflatex -interaction=nonstopmode -halt-on-error kerr_scalar_nonlinear_GF_baseframe.tex
pdflatex -interaction=nonstopmode -halt-on-error kerr_scalar_nonlinear_GF_baseframe.tex
```

Minimal smoke checks:

```bash
python -m compileall src scripts tests
python -m pytest tests/test_basic_run.py tests/test_teukolsky_scalar.py
```

If `pytest` is not installed in the active Python environment, use direct
script smoke checks or install it into the local environment first.

## Nonlinear Interpretation

The nonlinear amplitudes currently reported are first-order response
coefficients.  The physical correction is

```text
epsilon A^(1)
```

and weak perturbation theory requires

```text
epsilon |A^(1)| << |A^(0)|.
```

Large `A_ref_1` values in near-superradiant or low-frequency Kerr cases arise
from the unit-horizon-transmission normalization and the cubic source
`|R|^2 R`; they should not be interpreted without specifying the physical
incident normalization and coupling strength.

## Remaining Submission Work

- Replace manuscript author and affiliation placeholders with final submission
  metadata.
- Add a formal companion-paper citation only if it exists and is cited in the
  final manuscript.
- Derive the observed conformal-class split by a matched near-horizon
  expansion if an analytic exponent theorem is needed.

Use `python scripts\build_prd_manuscript.py` for the internally consistent
submission-prep build, and `python scripts\check_prd_submission_ready.py` to
audit whether the remaining external metadata gates have been cleared.
When final metadata are available, fill
`docs\prd\submission_metadata.template.json`, save it as
`docs\prd\submission_metadata.json`, and apply it with
`python scripts\apply_prd_submission_metadata.py docs\prd\submission_metadata.json`.

## License

MIT
