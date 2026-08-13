# ADR 0002: Put Node Operations Behind One Adapter Seam

## Status

Accepted

## Context

ADR 0001 separated upgrade ordering from execution by naming a local `upgrade_node` function.
That function did not create a seam: the runner still imported upgrade and health behavior
directly, and failure tests reached the simulated retry loop.

## Decision

The runner accepts a `NodeOperator` adapter with `upgrade` and `wait_until_healthy` operations.
Leader-last ordering, stop-on-failure behavior, and structured upgrade events remain in the
runner. The CLI uses a simulated adapter; tests use an in-memory recording adapter.

This supersedes the `upgrade_node` implementation detail in ADR 0001. It preserves ADR 0001's
larger decision to keep ordering separate from environment-specific execution.

## Consequences

- Failure-path tests do not wait on real polling or patch runner internals.
- Upgrade and health behavior vary together at one seam.
- A production host or Kubernetes adapter can replace the simulator without changing runner
  ordering or event semantics.
- Real cluster execution, quorum checks, persistence, and rollback remain out of scope.
