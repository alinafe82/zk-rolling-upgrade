# Architecture

## Problem

Rolling upgrades are operationally simple until a bad node order, weak health check, or
unclear rollback boundary causes avoidable downtime. This project models the upgrade control
loop in a small, testable CLI.

## Intended User

The intended user is a platform or SRE engineer reviewing an upgrade plan before applying it
to a coordination-service cluster.

## Modules

- `Plan` and `Node`: typed representation of the cluster and target version.
- CLI: parses user input and prints the plan or execution log.
- Runner: orders nodes, coordinates upgrade and health gates, and emits structured events.
- Node-operations seam: `NodeOperator` combines the upgrade action and post-step health wait.
- Simulated adapter: local implementation used by the CLI; tests supply an in-memory adapter.

## Data Flow

CLI arguments are parsed into a `Plan`. The runner separates followers and leaders, sends
followers to the node-operations adapter first, validates health after each step, and raises an
`UpgradeError` when a node is unhealthy after the attempted upgrade. Structured events cross
the runner interface; the CLI owns their presentation.

## Design Choices

The runner accepts a `NodeOperator` because node operations vary together by environment:
system packages, containers, Kubernetes, or a host orchestration tool. The runner retains the
stable ordering, stop-on-failure, and event semantics behind one interface.

I chose leader-last ordering because it is a conservative default for coordination systems.
The tradeoff is that this does not yet account for all quorum states or multi-leader systems.

## What Is Not Built

This is not a real cluster manager. It does not SSH to hosts, call Kubernetes, or mutate a
Zookeeper ensemble. It is a control-flow model that can be extended safely.

## Extension Points

- Add a production `NodeOperator` adapter for package, container, or Kubernetes operations and
  a real `mntr` or admin-interface health wait.
- Persist step status so a failed run can resume safely.

## Operational Considerations

A production version would need quorum checks before each step, explicit rollback behavior,
timeouts, audit logs, and operator approval for leader changes.

## Testing Strategy

Tests cover plan creation, adapter-observed leader-last order, CLI input validation, and
unhealthy-node failure through an in-memory adapter. The next useful adapter test would verify a
production `NodeOperator` against a disposable ensemble or recorded health responses.
