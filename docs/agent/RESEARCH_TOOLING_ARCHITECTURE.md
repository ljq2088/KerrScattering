# Research-agent tooling architecture

This project uses a project-scoped research agent rather than a hidden claim
that the model has been retrained on gravity. Its capability is made explicit
by four layers: instructions, reusable skills, MCP tools, and executable
audits. The design follows the official OpenAI agent and MCP guidance listed
below, while keeping the local implementation independent of the OpenAI
Agents SDK.

## Official design anchors

- [Agents SDK quickstart](https://openai.github.io/openai-agents-python/quickstart/):
  an agent is configured with instructions, tools, and a reproducible runtime.
- [Agents](https://openai.github.io/openai-agents-python/agents/):
  instructions, tools, MCP servers, handoffs, and guardrails are separate
  configuration surfaces.
- [MCP in the Agents SDK](https://openai.github.io/openai-agents-python/mcp/):
  local stdio, Streamable HTTP, and hosted MCP are distinct transports;
  tool filtering, approval, caching, and tracing are explicit choices.
- [Skills in ChatGPT](https://help.openai.com/en/articles/20001066-skills-in-chatgpt):
  skills are reusable workflows containing instructions, examples, and
  supporting resources.
- [Plugins in Codex](https://help.openai.com/en/articles/20001256-plugins-in-codex):
  plugins package skills and approved app/tool dependencies for repeatable
  workflows.

## Local implementation

```text
AGENTS.md
  -> project rules: conventions, scope, numerical standards, memory limits

.agents/skills/gravity-theory-research/SKILL.md
  -> reusable workflow: paper -> derivation -> experiment -> validation

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
