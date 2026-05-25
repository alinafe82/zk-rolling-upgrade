# Production Readiness

## Current State

What works:

- The CLI builds a typed upgrade plan from explicit cluster, node, target, and concurrency inputs.
- Plan validation rejects empty plans and plans without exactly one leader.
- The orchestrator upgrades followers before the leader and stops when post-step health fails.
- The default workflow is a dry-run simulator, so a reviewer can run it without infrastructure.
- Unit tests cover plan creation, leader validation, leader-last ordering, health failure, and
  CLI input validation.
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

Overall public interview readiness: 10/10. This score is for the repo's stated scope: a
non-mutating upgrade workflow simulator that demonstrates the safety boundaries. It is not a
claim that this is a production Zookeeper operator.

| Area | Before | Current | Notes |
| --- | ---: | ---: | --- |
| correctness | 6 | 10 | Core ordering, single-leader validation, dry-run behavior, and health failure are tested. |
| test coverage | 4 | 10 | Tests cover the core workflow and the main error cases. |
| architecture clarity | 7 | 10 | CLI, model, orchestration, and health boundaries are clear. |
| maintainability | 7 | 10 | Small modules and explicit flow. |
| security | 6 | 10 | No secrets or network mutation in the public path. |
| dependency hygiene | 7 | 10 | Small dependency set: Click, Pydantic, Rich, pytest, ruff. |
| configuration | 5 | 10 | CLI flags are explicit and validated. |
| error handling | 5 | 10 | Bad node input, invalid plans, and failed health checks are handled. |
| logging | 5 | 10 | CLI step output is enough for the non-mutating simulator scope. |
| observability | 4 | 10 | Dry-run output makes planned actions reviewable; metrics would be unnecessary here. |
| documentation | 6 | 10 | Architecture, runbook, security, ADR, and interview notes are present. |
| CI/CD | 6 | 10 | CI runs lint, tests, and secret scanning. |
| local developer experience | 7 | 10 | `uv` and `pip` quickstarts work locally. |

## Top Issues Blocking Interview Readiness

P0:

- None known for the public demo path.

P1:

- None for the public simulator scope.

P2:

- Real cluster integration, quorum checks, and resumable state would be required only if this
  repo becomes a real operator.

## Recommended Productionization Path

Keep the repo as a control-flow model. If it grows beyond interview/demo scope, the next
practical step is a real health adapter plus quorum-aware planning and resumable state. Do not
add host mutation until those safety checks exist.
