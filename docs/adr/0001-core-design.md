# ADR 0001: Keep The Upgrade Runner A Testable Simulator

## Context

Rolling upgrades need a predictable control loop: pick a safe node order, apply one step,
verify health, and stop on failure. The public repo should demonstrate that logic without
requiring private cluster access or real host credentials.

## Decision

Keep the core implementation as a local simulator with typed models, a small CLI, and an
orchestrator that upgrades followers before leaders and checks health after every node.

## Alternatives Considered

- Build a real SSH or Kubernetes executor.
- Model a complete Zookeeper quorum planner.
- Keep only a README-level design with no runnable code.

## Why This Design Was Selected

I chose this design because the valuable interview signal is the operational control flow, not
access to a private environment. The code is small enough to review, test, and extend.

## Tradeoffs

The tradeoff is that the repo cannot prove real cluster safety. It can only prove the local
planner and failure boundary.

## Consequences

- The demo runs without secrets or infrastructure.
- The adapter boundary is clear.
- Future real execution must add quorum checks, timeouts, state persistence, and rollback notes.

## What Would Change At Larger Scale

At larger scale, I would add a real health adapter, resumable state, an approval gate before
leader changes, and audit logs for each node operation. I would still keep destructive execution
outside the CLI parsing layer.
