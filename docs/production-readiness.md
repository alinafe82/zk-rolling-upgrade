# Production Readiness

## Current State

What works:

- The CLI builds a typed upgrade plan from explicit cluster, node, target, and concurrency inputs.
- The orchestrator upgrades followers before the leader and stops when post-step health fails.
- The default workflow is a dry-run simulator, so a reviewer can run it without infrastructure.
- Unit tests cover plan creation, leader-last ordering, health failure, and CLI input validation.
- CI runs tests, linting, and secret scanning.

What is broken:

- Nothing known in the local quickstart path.

What is unclear:

- The simulator does not model quorum math or real Zookeeper health responses.
- `concurrency` is validated but not used for parallel execution.

What is missing:

- A real Zookeeper adapter.
- Persistent upgrade state for resume after failure.
- Explicit rollback behavior.

What is risky:

- A real executor would be unsafe without quorum checks, timeout handling, and operator approval.

## Readiness Scores

| Area | Before | Current | Notes |
| --- | ---: | ---: | --- |
| correctness | 6 | 7 | Core ordering is tested; real cluster behavior is still out of scope. |
| test coverage | 4 | 7 | Tests now cover order, failure, and CLI validation. |
| architecture clarity | 7 | 8 | CLI, model, orchestration, and health boundaries are clear. |
| maintainability | 7 | 8 | Small modules and explicit flow. |
| security | 6 | 7 | No secrets or network mutation; real executor would need stronger controls. |
| dependency hygiene | 7 | 7 | Small dependency set: Click, Pydantic, Rich, pytest, ruff. |
| configuration | 5 | 6 | CLI flags are explicit; no config file yet. |
| error handling | 5 | 7 | Bad node input and failed health checks are handled. |
| logging | 5 | 6 | CLI logs steps, but there is no structured audit log. |
| observability | 4 | 5 | Step output exists; metrics/tracing would be overbuilt here. |
| documentation | 6 | 8 | Architecture, runbook, security, ADR, and interview notes are present. |
| CI/CD | 6 | 8 | CI runs lint, tests, and secret scanning. |
| local developer experience | 7 | 8 | `uv` and `pip` quickstarts work locally. |

## Top Issues Blocking Interview Readiness

P0:

- None known for the public demo path.

P1:

- Real cluster integration is not implemented. This is acceptable if described as a simulator.
- Quorum safety is not modeled yet.

P2:

- Persisting step state would make the design more realistic.
- A fake health adapter fixture could make extension behavior clearer.

## Recommended Productionization Path

Keep the repo as a control-flow model. The next practical step is not Kubernetes or a full host
executor; it is a real health adapter interface plus tests that prove failed health prevents
later nodes from being touched. After that, add quorum-aware planning and resumable state.
