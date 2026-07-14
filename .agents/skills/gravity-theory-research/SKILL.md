---
name: gravity-theory-research
description: Use for gravitational-physics research tasks involving Kerr or Schwarzschild black holes, gravitational waves, Teukolsky equations, scattering amplitudes, Green functions, spectral methods, Mathematica/MATLAB/WSL computations, literature review, or PRD-quality manuscript preparation. Do not use for unrelated software work.
---

# Gravity theory research

Work as a careful collaborator in mathematical relativity and scientific computing. The default active problem is the scalar Teukolsky equation on Kerr (`s=0`) and its weak nonlinear scattering extension.

## First pass

Read, in this order when relevant:

1. The repository `AGENTS.md`.
2. The active derivation and manuscript in `docs/`.
3. The solver and source modules in `src/`.
4. The producing scripts and matching CSV/JSON outputs in `scripts/` and `results/`.
5. The local Schwarzschild reference workflow if the user asks for a route comparison.

Use `rg` to locate definitions and equation labels before making claims. Preserve unrelated user edits.

## Analytic derivations

For a derivation, make the logical chain explicit:

- geometric and field conventions;
- separation ansatz and angular eigenvalue convention;
- radial Teukolsky equation and singular endpoints;
- horizon and infinity asymptotics;
- normalization of `R_in`, `B_inc`, `B_ref`, and transmitted amplitude;
- Green-function construction and Wronskian;
- perturbative source and projected target channels;
- energy fluxes and the order-by-order balance law.

Keep algebraic equalities separate from numerical definitions. If two papers use different radial variables or lambda conventions, write the conversion instead of silently identifying symbols.

## Numerical workflow

Start from the endpoint-inclusive Chebyshev formulation used by the Schwarzschild solver. Record:

- domain map and collocation order;
- endpoint equations replacing the vanishing second-derivative coefficient;
- normalization row and boundary derivative relation;
- linear solver and scaling;
- matching points and asymptotic basis;
- precision, condition estimates, coefficient tails, and residual denominators.

For nonlinear calculations, state whether a number is `A^(1)` or the physical `epsilon A^(1)`. Check weak-perturbation validity before interpreting large response coefficients.

## Literature and citations

Use primary sources and store stable identifiers (DOI, arXiv ID, or publisher URL). Use the local research MCP for arXiv metadata and Zotero for the local bibliography. Never manufacture authors, dates, or journal information. If a citation is only a local manuscript, label it as such and keep it out of final submission metadata until an arXiv or journal record exists.

For deep learning of the literature, use the staged map in `docs/literature/gravity_literature_map.md`, the English and Chinese curricula in `docs/literature/deep_learning_curriculum.md` and `docs/literature/deep_learning_curriculum_zh.md`, the capability matrix in `docs/agent/RESEARCH_CAPABILITY_MATRIX.md`, the convention ledger in `docs/literature/convention_ledger.md`, and the paper cards in `docs/literature/paper_cards.md`. Refresh `results/literature/arxiv_catalog.json` with `python scripts/build_literature_manifest.py` and run `python scripts/check_research_setup.py` before relying on the local agent configuration. The MCP exposes `list_literature_modules` and `get_literature_card` for read-only project evidence. For every paper, make a compact evidence record with:

- the problem and approximation hierarchy;
- exact field/orbit/gauge conventions;
- the central equations and boundary conditions;
- the regularization, flux, or Green-function construction;
- the numerical method and convergence evidence;
- the result that can be reused in this repository;
- differences from the present fixed-background scalar `s=0` problem.

Maintain the following conceptual separation: black-hole perturbation theory computes fields on a background; gravitational self-force computes the small body's motion and metric perturbation with singular-field subtraction; EMRI waveform modelling combines geodesic orbits, dissipative fluxes, conservative self-force, resonances, and multiscale evolution. Similar symbols such as `R`, `lambda`, `B_inc`, or `A^(1)` must not be identified across these layers without a convention check.

## External computations

- arXiv tools are read-only metadata/abstract access unless the user explicitly requests a download.
- Zotero tools are read-only by default. Writes/imports require a separate explicit user request and exact destination.
- Mathematica evaluation is local code execution. Use it only when requested, pass a finite timeout, and return stdout/stderr plus the exact kernel path. Do not use it as a hidden file-editing mechanism.
- MATLAB and WSL runs must write logs and bounded outputs. Monitor memory for high-order spectral matrices and stop before the machine becomes unresponsive.

## Verification and reporting

Run the narrowest relevant tests first. For manuscript work, build twice, inspect the PDF visually, and run the project readiness checks. Report:

- files changed;
- commands run;
- numerical diagnostics and their denominators;
- failures or unavailable external references;
- the next scientific decision that remains.

Do not call a result high precision merely because one observable agrees. Require convergence of the field, residual, endpoint conditions, and extracted amplitudes.
