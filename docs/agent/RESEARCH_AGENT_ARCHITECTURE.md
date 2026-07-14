# KerrScattering research-agent architecture

This repository contains a project-scoped research workflow for Kerr black-hole
perturbation theory. It is designed to keep analytic derivations, numerical
experiments, literature evidence, and manuscript production auditable.

## Scope layers

| Layer | Current status | Required distinction |
|---|---|---|
| Fixed-background perturbation | Active: scalar Teukolsky, `s=0` | Field amplitudes and fluxes on prescribed Kerr |
| Prescribed nonlinear response | Active: weak cubic scalar Green response | `A^(1)` is a response coefficient, not a self-force |
| Gravitational self-force | Reading and future interface | Mass-ratio expansion, singular/regular split, gauge control |
| EMRI waveform modelling | Future interface | Geodesics, mode lattice, fluxes, orbit evolution, phase error |

The active PRD manuscript must remain in the first two layers. `s=-2` and
gravitational self-force material belongs in separate notes or branches unless
the user explicitly requests a separate manuscript.

## Configuration layers

1. `AGENTS.md` defines repository-wide scientific and engineering rules.
2. `.agents/skills/gravity-theory-research/SKILL.md` defines the workflow for
   derivations, numerical work, literature review, and PRD preparation.
3. `.codex/config.toml` registers the optional local `gravity_research` MCP
   server. Its project path must be valid on the local Windows machine.
4. `src/`, `scripts/`, and `results/` contain the implementation, experiments,
   and generated data. Manuscript and derivation artifacts live under `docs/`.

The local MCP server is a bridge, not an official arXiv, Zotero, or Wolfram
service. It provides read-only arXiv metadata, read-only Zotero queries, an
explicitly requested bounded Mathematica evaluation, environment checks, and
read-only access to the maintained project literature modules and paper cards.
Run `python scripts/check_research_setup.py` to audit the complete local
research setup before a long derivation or numerical scan.

## Research protocol

For every calculation:

1. State units, signature, Fourier convention, radial variable, angular
   eigenvalue convention, and amplitude normalization.
2. Separate analytic identities, numerical observations, and fitted trends.
3. Record the script, parameters, memory guard, output path, and precision
   diagnostic for every reported number.
4. Validate field-dependent residuals, endpoint relations, spectral tails,
   matching/Wronskian identities, amplitude convergence, and flux balance.
5. Build the manuscript twice, inspect rendered pages, and run citation,
   artifact, numerical-consistency, and submission-readiness checks.

## Literature-to-code graph

```text
Kerr geodesics
  -> (Omega_r, Omega_theta, Omega_phi, Gamma)
  -> source lattice (l,m,k,n; omega_mkn)
  -> separated Teukolsky modes (S_lmomega, R_lmomega)
  -> B amplitudes and fluxes
  -> dissipative/conservative self-force
  -> orbit evolution and waveform phase
```

The current project starts at the separated fixed-frequency scalar radial
problem. It does not yet implement geodesic source harmonics, a mass-ratio
expansion, regularization, or accumulated EMRI phase evolution.

## External tools

- MATLAB: `F:\\matlab\\2026a\\bin\\matlab.exe`
- Wolfram Script: `F:\\mma\\wolframscript.exe`
- WSL: `wsl.exe`
- Local research MCP: `tools/mcp/gravity_research_server.py`

Use bounded jobs and memory checks for high-order spectral calculations. Keep
generated logs and intermediate data under the project or a clearly named
external output directory.

## Official documentation anchors

- [Codex customization](https://developers.openai.com/codex/concepts/customization)
- [AGENTS.md configuration](https://developers.openai.com/codex/agent-configuration/agents-md)
- [Build skills](https://developers.openai.com/codex/build-skills)
- [MCP extension](https://developers.openai.com/codex/extend/mcp)
- [Configuration reference](https://developers.openai.com/codex/config-reference)
