# Research-agent tooling architecture

This project uses a project-scoped research agent rather than a hidden claim
that the model has been retrained on gravity. Its capability is made explicit
by four layers: instructions, reusable skills, MCP tools, and executable
audits. The design follows the current Codex skill and MCP guidance listed
below, while keeping the local implementation independent of the OpenAI
Agents SDK.

## Official design anchors

- [Build skills](https://developers.openai.com/codex/build-skills): a skill is
  a directory with a required `SKILL.md`; Codex loads full instructions only
  after selecting the skill, so descriptions must be concise and specific.
- [Codex MCP extension](https://developers.openai.com/codex/extend/mcp): MCP
  transports, server configuration, and tool exposure are explicit rather
  than hidden inside the research prompt.
- [AGENTS.md configuration](https://developers.openai.com/codex/agent-configuration/agents-md):
  project instructions are scoped by repository location and remain separate
  from reusable skills.
- [Codex configuration reference](https://developers.openai.com/codex/config-reference):
  project-local configuration is checked as configuration, not treated as
  prose documentation.
- [Plugins](https://developers.openai.com/codex/plugins): plugins are the
  distribution boundary when multiple skills and tool dependencies should be
  shared beyond one repository.

## Local implementation

```text
AGENTS.md
  -> project rules: conventions, scope, numerical standards, memory limits

.agents/skills/gravity-theory-research/SKILL.md
  -> reusable workflow: paper -> derivation -> experiment -> validation

.agents/skills/gravity-theory-research/agents/openai.yaml
  -> optional UI metadata and the skill invocation contract

tools/mcp/gravity_research_server.py
  -> stdio MCP bridge
     arXiv metadata/abstracts (read-only)
     local Zotero HTTP API (read-only)
     explicitly supplied Wolfram Language evaluation (bounded timeout)
     local literature cards and learning gates

scripts/check_mcp_server.py
scripts/check_research_setup.py
scripts/check_literature_learning_gates.py
  -> executable smoke tests and promotion gates
```

The local bridge is deliberately described as a bridge, not as an official
arXiv, Mathematica, or Zotero connector. It does not write bibliography files,
does not mutate the repository through MCP, and does not execute Mathematica
unless the caller supplies the expression and a timeout. Wolfram paths,
MATLAB, WSL, and Zotero endpoints are reported by `research_environment()`;
their availability is an environment fact that must be checked at runtime.

The skill follows progressive disclosure: the front matter is short enough for
skill discovery, while the detailed gravity workflow stays in `SKILL.md` and
the literature files. The project audit checks both the front matter and the
optional `openai.yaml` contract so a broken skill cannot silently become the
research agent's default workflow. MCP registration remains in
`.codex/config.toml`, where the local stdio command and its approval policy are
visible and independently testable.

## Research call policy

1. **Literature:** query metadata first, then inspect the primary paper. A
   catalog entry is not evidence for an equation.
2. **Derivation:** record signature, Fourier sign, tetrad/gauge, radial and
   angular conventions, perturbative order, and boundary normalization before
   transferring a formula.
3. **Numerics:** preserve the distinction between a residual, an amplitude,
   a flux, and an accumulated waveform phase. Use independent validation when
   a result is promoted to a manuscript.
4. **Mathematica:** use only for a declared finite evaluation. Keep code
   evaluation time-bounded and record stdout, stderr, kernel path, and return
   code.
5. **Zotero:** read item metadata or export BibTeX on request; never treat an
   empty or unavailable local library as proof that a citation does not exist.
6. **EMRI/self-force:** never infer a gravitational self-force or EMRI
   waveform from the present fixed-background scalar nonlinear calculation.
   Those layers require a mass-ratio expansion, worldline, source lattice,
   regularization/gauge data, and slow-time phase evolution.

## Promotion gate

A new literature conclusion enters the maintained knowledge graph only when
its record contains: (i) convention extraction, (ii) an equation or algorithm
reproduced in project notation, (iii) a concrete implementation target, (iv)
an independent validation, and (v) an explicit incompatibility/scope
statement. The machine-readable implementation is
`docs/literature/learning_gates.json`; the runtime checks are listed above.

This architecture improves reliability by making the agent's capabilities
inspectable. It does not replace reading the original papers or running the
underlying numerical experiments.
