# ADR 0001: Keep Upgrade Ordering Separate From Execution

## Status

Accepted

## Context

The risky part of a rolling upgrade is not only the command used to upgrade a node. It is the
order of operations, the health gate after each step, and the point where the run should stop.

## Decision

The repo keeps ordering and validation in `zk_upgrade.orchestrator`, while the actual node
upgrade is isolated behind `upgrade_node`.

## Consequences

This makes the core logic easy to test without a real cluster. It also means the current repo
is a simulator, not a deployable upgrade service. A production implementation would add a real
executor and stronger quorum checks without changing the public control-flow shape.
