# Research capability status: 2026-07-15

This snapshot records what the project-scoped research agent can do and what
has not been implemented. It is an auditable capability contract, not a claim
that a language model has been retrained on gravitational physics.

## Active role

The active role is a theoretical-gravity and scientific-computing collaborator
for Kerr black-hole perturbation theory. The production problem is the scalar
Teukolsky equation (`s=0`) on a prescribed Kerr background, including
endpoint-inclusive Chebyshev solves, homogeneous connection coefficients,
Wronskian-normalized Green functions, weak cubic response, energy fluxes, and
PRD-quality reproducibility.

The present manuscript does not claim a gravitational self-force, a metric
perturbation, or an EMRI waveform. Its nonlinear coefficient is a response of a
prescribed scalar field on a fixed background.

## Capability layers and evidence

| Layer | Current capability | Evidence and acceptance |
| --- | --- | --- |
| Conventions | Kerr geometry, Fourier sign, radial compactification, angular eigenvalue, horizon/infinity bases, and flux orientation are recorded before transfer. | `docs/literature/convention_ledger.md`; endpoint, Wronskian, and flux checks. |
| Fixed-background BHPT | Scalar Teukolsky separation, regular-singular endpoint rows, `R_in`/`R_up`, matching, Green projections, and field-dependent residuals. | `src/`; spectral tails, endpoint relations, order scans, Wronskian constancy, and flux balance. |
| Prescribed nonlinearity | Cubic source projection into target spheroidal channels and first-order reflected/horizon response. | `src/kerr_scalar_nonlinear.py`; channel convergence, quadrature sensitivity, and fixed-incident flux coefficients. |
| Independent literature route | MST/GSN are treated as convention-aware audits or future backends, not silently identified with the direct Teukolsky variable. | `docs/literature/core_reading_notes.md`; `Hughes2000` and `Lo2023` in the manuscript bibliography. |
| EMRI transfer | The radial solver is specified as one backend component for a future source lattice. | `docs/literature/EMRI_TRANSFER_PROTOCOL_ZH.md`; gate `emri-source-lattice`. |
| Self-force | The mass-ratio expansion, singular/regular split, gauge declaration, mode-sum/effective-source route, and long-time phase budget are understood as separate layers. | `docs/literature/deep_learning_report_2026-07-14.md`; gates `singular-regular-self-force` and `gw-waveform-phase`. |
| Agent tooling | Repository rules, a progressively loaded gravity skill, its `agents/openai.yaml` metadata, optional stdio MCP, literature metadata/cards, and deterministic audits are wired together. | `AGENTS.md`, `.agents/skills/gravity-theory-research/SKILL.md`, `.agents/skills/gravity-theory-research/agents/openai.yaml`, `.codex/config.toml`, `scripts/check_research_setup.py`. |

## Literature transfer protocol

For each paper, the maintained record must contain: (i) approximation order
and perturbative parameter, (ii) metric/signature/Fourier/tetrad/gauge
conventions, (iii) central equation and boundary condition, (iv) Green,
Wronskian, flux, regularization, or bilinear normalization, (v) numerical
method and independent validation, (vi) a concrete implementation target, and
(vii) an incompatibility statement relative to the active scalar problem.

The linked reading tracks are deliberately separated:

1. Kerr geometry, Teukolsky separation, MST, and generalized
   Sasaki--Nakamura methods.
2. Kerr geodesics, Mino-time frequencies, the `(l,m,k,n)` EMRI source lattice,
   and infinity/horizon flux reconstruction.
3. Radiation reaction, Detweiler--Whiting regular fields, mode-sum and
   effective-source regularization, and gauge dependence.
4. Adiabatic and post-adiabatic evolution, transient resonances, accumulated
   waveform phase, and detector-level error budgets.
5. Second-order Teukolsky, metric reconstruction, nonlinear ringdown, and the
   distinction between a real-frequency response fit and a QNM excitation
   coefficient.

The machine-readable catalogue and promotion tests are in
`docs/literature/seed_arxiv_ids.txt`, `results/literature/arxiv_catalog.json`,
and `docs/literature/learning_gates.json`. The current audit resolves 46
records and checks 9 modules with 29 acceptance tests.

A focused 2025--2026 frontier update is recorded in
`docs/literature/research_frontier_update_2026-07-15.md`. It transfers four
primary-paper lessons about eccentric second-order self-force, generic
effective sources, second-order puncture structure, and conserved Kerr
bilinear forms. These are explicitly marked as watchlist material until the
corresponding implementation and validation gates exist.

## Agent construction and official anchors

The project follows the official Codex configuration model at the project
level:

- `AGENTS.md` supplies repository-scoped instructions;
- `.agents/skills/gravity-theory-research/SKILL.md` supplies the reusable
  derivation-to-validation workflow;
- `.agents/skills/gravity-theory-research/agents/openai.yaml` supplies the
  skill's display metadata and invocation contract;
- `.codex/config.toml` registers an optional local stdio MCP server;
- `tools/mcp/gravity_research_server.py` exposes read-only arXiv metadata,
  read-only Zotero queries, bounded explicitly supplied Wolfram evaluations,
  and local literature cards/gates;
- `scripts/check_mcp_server.py`, `scripts/check_research_setup.py`, and the
  literature gates provide executable smoke tests.

The official design anchors are the OpenAI documentation for
[Codex customization](https://developers.openai.com/codex/concepts/customization),
[AGENTS.md](https://developers.openai.com/codex/agent-configuration/agents-md),
[skills](https://developers.openai.com/codex/build-skills),
[MCP extension](https://developers.openai.com/codex/extend/mcp), and the
[configuration reference](https://developers.openai.com/codex/config-reference).
The local MCP is explicitly a bridge and is not presented as an official arXiv,
Zotero, or Wolfram connector.

The setup audit also checks the skill front matter and UI metadata. This keeps
the repository aligned with Codex's progressive-disclosure skill model: the
short description participates in discovery, while the full gravity workflow
is loaded only when the task matches it.

## Promotion criteria for future physics

The project may promote the current scalar backend to an EMRI experiment only
after implementing and independently testing
`OrbitConstants -> Frequencies -> ModeLabel -> SourceCoefficients -> FluxRecord`.
It may promote a calculation to gravitational self-force only after adding a
mass-ratio expansion, a singular/regular or effective-source construction,
regularization parameters, a gauge prescription, and a worldline/phase error
budget. A single accurate `B_inc`, `B_ref`, or fixed-frequency flux cannot pass
either promotion gate by itself.

## Verified on this snapshot

The following checks pass in the repository checkout:

```text
literature catalog: 46 resolved records
learning gates: 9 modules, 29 acceptance tests
research setup and MCP smoke test: pass
PRD artifact, numeric, citation, and style checks: pass
package-local plot regeneration and PDF SHA comparison: pass
```

The remaining PRD submission blockers are external author names,
affiliations, corresponding email, and final submission metadata. They are not
invented here.
