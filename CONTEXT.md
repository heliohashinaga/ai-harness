# AI Harness

A minimal engineering harness for software development: one agent session per task, verified by evidence, extended only on measured gain.

## Language

**Task**:
A human-written contract with Goal, Acceptance Criteria and Constraints. The only input an Agent Session needs.
_Avoid_: ticket, prompt, request

**Agent Session**:
A single model working with repository tools and task context to produce a change. No fixed roles inside it.
_Avoid_: worker, coder agent, swarm

**Harness**:
The code around the model: task loading, tool access, verification and retry. It provides map and feedback, never orchestration for its own sake.
_Avoid_: framework, orchestrator, swarm

**Evaluator**:
A separate, preferably fresh-context check that turns a change into a Verdict. Deterministic checks first, LLM judge only for what cannot be checked deterministically.
_Avoid_: reviewer agent, tester agent, cleaner agent

**Verdict**:
PASS or FAIL with evidence (build, tests, diff, violated criterion). Never "I think it's done".
_Avoid_: approval, opinion

**Retry**:
A new Agent Session attempt fed with the previous Verdict as feedback. Bounded (max 3), then human.
_Avoid_: loop, self-heal

**Skill**:
An opt-in capability (e.g. security, testing) the agent loads when the task needs it. Not a separate agent.
_Avoid_: specialist agent, subagent

**Complexity Budget**:
The rule that a second agent, planner or memory layer must earn existence via benchmark gain before entering the architecture.
_Avoid_: roadmap, evolution ladder
