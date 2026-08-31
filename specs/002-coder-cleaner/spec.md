# Feature Specification: Coder → Cleaner Agent Pipeline

**Feature Branch**: `004-coder-cleaner`

**Created**: 2026-08-31

**Status**: Draft

**Input**: User description: "quero criar um agent coder -> cleaner" — a two-stage
swarm handoff where an agent that writes code hands its output to an agent that
cleans it before it is considered done.

## Clarifications

### Session 2026-08-31

- Q: O cleaner deve fazer formatação ou só clean code semântico? → A: **só clean
  code semântico** (nomeação, funções pequenas, remover comentários
  redundantes); formatação é delegada a um formatter determinístico (Black, ruff,
  prettier…), fora do cleaner (FR-005).
- Q: Precisa de CLI para rodar o pipeline? → A: sim, um comando **`agentcrew-code`**
  é parte do escopo planejado, mas pode ser entregue depois da biblioteca/tests.
- Q: Onde fica o plano? → A: persistido em `specs/002-coder-cleaner/` (este pacote).
- Q: O coder/cleaner devem gerar/limpar só Python ou qualquer linguagem pedida pela
  tarefa? → A: **language-agnostic** — a tarefa pode pedir qualquer linguagem; o
  coder gera na linguagem pedida e o cleaner aplica heurísticas de clean code
  genéricas (nomeação, funções pequenas, comentários redundantes), sem formatação/
  regras por linguagem.

## User Scenarios & Testing

### User Story 1 - Run the coder→cleaner pipeline and see both handoffs (Priority: P1)

A developer wants to see two agents collaborating: given a natural-language task
("write a Python function that ..."), the **coder** agent produces code, then the
**cleaner** agent refines that code (predictable, readable, well-formed) and
hands back a finished result. The whole handoff is observable — each agent's
output is visible and traceable.

**Why this priority**: This is the first **multi-node orchestration** in the
project and the first real instance of the swarm vision (an agent passing work to
another agent). It must establish the graph plumbing, the LLM-backed agent seam,
and the observable handoff before more agents are added.

**Independent Test**: The graph can be exercised with **mocked node outputs** (no
network) to prove ordering and shape; LLM-backed behavior (coder + semantic
cleaner) is covered by integration tests marked `integration`/`live` (opt-in).

**Acceptance Scenarios**:

1. **Given** the project is installed, **When** a user invokes the coder→cleaner
   pipeline with a task, **Then** the pipeline returns both the raw coder output
   and the cleaned output, in that order.
2. **Given** the graph plumbing, **When** a run executes, **Then** the coder node
   runs before the cleaner node (verified with mocked outputs, offline).
3. **Given** the graph plumbing, **When** a run executes offline with mocked
   nodes, **Then** the handoff completes deterministically (no network, no
   credentials).
4. **Given** LangSmith tracing enabled, **When** a real run executes, **Then** the
   graph and both nodes (`coder`, `cleaner`) appear as a trace in the project.

### Edge Cases

- **Given** an empty or whitespace-only task, **When** the pipeline runs, **Then**
  the system rejects it with a clear usage error (no nodes run) — aligned with the
  CLI contract (exit code `1`).
- **Given** no API key configured for the chosen provider, **When** an LLM-backed
  run is attempted, **Then** it fails fast with a clear hint (exit code `4`),
  mirroring `agentcrew-llm`.
- **Given** an unexpected run-time failure in a node, **When** the pipeline runs,
  **Then** the error is surfaced (exit code `4`) rather than silently masked.

---

## Requirements

### Functional Requirements

- **FR-001**: The system MUST provide a coder capability that, given a
  natural-language task, produces candidate code as text output.
- **FR-002**: The system MUST provide a cleaner capability that accepts code text
  and applies **semantic clean code standards** to it (descriptive naming, small
  single-purpose functions, removing redundant comments), returning cleaner code
  text (the `cleaner_output`).
- **FR-003**: The system MUST orchestrate the two capabilities as a pipeline in
  which the coder runs before the cleaner, passing its output to the cleaner.
- **FR-004**: The pipeline MUST expose the result of each stage (coder output,
  cleaner output) so the handoff is observable.
- **FR-005**: The cleaner MUST NOT be responsible for formatting. Formatting is
  delegated to a deterministic formatter (e.g. Black, ruff, prettier, gofmt) run
  outside the cleaner node, so output is consistent and not LLM-invented.
- **FR-006**: LLM-backed behavior MUST be opt-in (require an API key for the
  chosen provider, like `agentcrew-llm`); the graph plumbing MUST be testable
  offline (verified with stubbed node outputs, no credentials).
- **FR-007**: The pipeline MUST support LangSmith tracing so a real run surfaces
  the graph and node names (observability).
- **FR-008**: The system MUST include an automated test (offline, with mocks)
  verifying the coder→cleaner handoff ordering and shape.
- **FR-009**: The project MUST declare the orchestration dependency needed to
  build a multi-node graph (LangGraph) as an explicit dependency.

### Key Entities

- **CoderAgent**: The "builder" role — given a task, produces candidate code.
  Emits `coder_output`.
- **CleanerAgent**: The "cleaner" role — applies **semantic clean code standards**
  to the code the coder generated: descriptive naming, small single-purpose
  functions, removing redundant comments. It is **LLM-backed** (opt-in) and is
  deliberately **not** responsible for formatting — formatting is delegated to a
  deterministic formatter (Black/ruff, prettier, …) outside the cleaner node. Emits
  `cleaner_output`.
- **CoderCleanerGraph**: The orchestration unit — a LangGraph `StateGraph`
  (START → coder → cleaner → END) binding the two agents and their shared state.
- **TaskState**: The shared data structure between nodes (task input, coder
  output, cleaner output, optional error). Documented in `data-model.md`.

## Success Criteria

### Measurable Outcomes

- **SC-001**: The pipeline runs the coder before the cleaner on every invocation
  (verified by an offline contract test with mocked node outputs).
- **SC-002**: The formatting path used by agent-crew stays deterministic —
  identical input always formats identically — satisfied by the existing
  Black/ruff tooling; the LLM never touches formatting (FR-005).
- **SC-003**: The graph plumbing and the coder→cleaner handoff pass the offline
  test suite (stubbed node outputs) with no network access and no credentials.
- **SC-004**: With LangSmith enabled, a real run produces a trace showing the
  graph and the `coder` and `cleaner` nodes.

## Assumptions

- The pipeline is built on **LangGraph** (1.x, `StateGraph`/`START`/`END`) for
  multi-node orchestration, matching the constitution's swarm vision. LangGraph
  becomes an explicit dependency.
- **Coder** is LLM-backed and **language-agnostic**: it generates code in whatever
  language the task asks for (the user story's "write a Python function…" is just
  an example). It reuses the existing provider infrastructure
  (`agentcrew.nodes.llm`: OpenRouter / OpenCode Go), reading keys from the local
  `.env`. It is opt-in (needs an API key).
- **Cleaner** is **LLM-backed, semantic-only, and language-agnostic**: it applies
  generic clean-code standards (descriptive naming, small single-purpose
  functions, removing redundant comments) in whatever language the code is. It is
  explicitly **not** responsible for formatting — formatting is delegated to a
  deterministic formatter (e.g. Black/ruff, prettier) where the project already
  runs it (CI/editor tooling), which remains Python-scoped unless a formatter is
  configured for it; the LLM never touches formatting (FR-005), and no
  per-language rules/formatting run inside the pipeline for non-Python output.
- Removing dead code / unused imports is a future "lint" step, out of v1 (it
  requires interpreting the language).
- A console script **`agentcrew-code`** exposes the pipeline (same exit-code
  protocol `0`/`1`/`4`, text/JSON output) following constitution Principle II.
- The pipeline does not ship its own formatter and the cleaner never invokes
  formatting (FR-005) — a deterministic formatter (Black/ruff, prettier, …) is
  the single formatting path, identical to the repo's CI/editor tooling.
- LangSmith tracing is opt-in via the existing `LANGSMITH_*` env vars.

## Out of Scope (v1)

- More than two agents (planner/tester/reviewer/security) — the graph is a fixed
  linear pipeline for this slice.
- Conditional routing, loops, human-in-the-loop approval, or time-travel.
- Persistence/checkpointing across processes (InMemorySaver only for dev/tests).
- Actual execution/lint of the produced code (cleaner only normalizes text; it
  does not import or run the generated code).
- A marketplace or multi-language codegen *beyond* the prompt-driven coder: the
  coder is language-agnostic, but only via LLM prompting — there is no
  per-language engine, formatter, or linter inside the pipeline. Formatting stays
  only with the deterministic formatter configured for the language (e.g.
  Black/ruff for Python, prettier for JS/TS); "lint" (dead code / unused imports)
  remains a future step.
---

## Planned Extension: Repo & Branch Mode

**Status:** planned (post-v1); not yet implemented. Extends the text pipeline so a
user can point the pipeline at a real repository and have `coder`/`cleaner` work
on it, with a **commit→merge handoff between branches** (pattern from
SwarmForge's `two-pack` — see `research.md`).

### Inputs

- `repo`: a **local path** to an existing git working tree (remote URLs are out of
  scope for now — no clone).
- `branch`: the base branch the work is derived from.
- `task`: what the coder should change.

### Flow (commit→merge between branches)

1. **Coder** creates a **worktree A** (attached to its own dedicated branch,
   e.g. `agent/coder-<ts>`), reads context, writes files, and **commits** → state
   carries `commit_c` (the SHA), `worktree_a`, `branch_a`, `file_paths`.
2. **Cleaner** creates its **own worktree B** (attached to branch B), **merges
   `commit_c` into B** (same mechanism as SwarmForge `ready_for_next`/`git merge`),
   applies the semantic clean-code policy to the declared files **in B**, and
   **commits** the cleaned result → `commit_b`, `branch_b`.
3. **Local for now:** everything stays **local** — no remote push or PR in the
   current scope. (A remote draft-PR flow is deferred; see Out of Scope additions
   below.)

These changes live on **branches** (via commits in the worktrees); they propagate
between agents by **merging the sender's commit**, not as loose files.

### Data model (repo mode)

`TaskState` is extended with: `repo`, `branch`, `commit_c`, `commit_b`,
`worktree_a`, `worktree_b`, `branch_a`, `branch_b`, `file_paths`,
`cleaned_files`. See `data-model.md`.

### Scope & guardrails

- Worktrees isolate each agent; the main checkout is untouched until a deliberate
  merge/PR.
- No auto-commit on protected/default branches (`main`/`master`) without `--force`;
  dedicated branches by default.
- No remote push/PR in the current scope (deferred) — everything stays local;
  auto-merge is never performed.
- Coder reads context only from declared files (prompt-injection guard); generated
  code is **not executed**; secrets stay out of generated files/logs (`.env*`).
