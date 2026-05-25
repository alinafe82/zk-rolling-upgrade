# Architecture

## Problem

Rolling upgrades are operationally simple until a bad node order, weak health check, or
unclear rollback boundary causes avoidable downtime. This project models the upgrade control
loop in a small, testable CLI.

## Intended User

The intended user is a platform or SRE engineer reviewing an upgrade plan before applying it
to a coordination-service cluster.

## Components

- `Plan` and `Node`: typed representation of the cluster and target version.
- CLI: parses user input and prints the plan or execution log.
- Orchestrator: orders nodes, runs the upgrade action, and checks health.
- Health adapter: currently local and deterministic; intended to be replaced by a real
  Zookeeper health implementation.

## Data Flow

CLI arguments are parsed into a `Plan`. The orchestrator separates followers and leaders,
upgrades followers first, validates health after each step, and raises an `UpgradeError` when
a node is unhealthy after the attempted upgrade.

## Design Choices

I kept the upgrade action behind a small function because the real implementation would be
environment-specific: system packages, containers, Kubernetes, or a host orchestration tool.
The stable part is the ordering and validation logic.

I chose leader-last ordering because it is a conservative default for coordination systems.
The tradeoff is that this does not yet account for all quorum states or multi-leader systems.

## What Is Not Built

This is not a real cluster manager. It does not SSH to hosts, call Kubernetes, or mutate a
Zookeeper ensemble. It is a control-flow model that can be extended safely.

## Extension Points

- Replace `check_health` with a real `mntr` or admin API adapter.
- Replace `upgrade_node` with an executor that can run package, container, or Kubernetes
  operations.
- Persist step status so a failed run can resume safely.

## Operational Considerations

A production version would need quorum checks before each step, explicit rollback behavior,
timeouts, audit logs, and operator approval for leader changes.

## Testing Strategy

Tests cover plan creation, leader-last order, CLI input validation, and unhealthy-node failure.
The next useful layer would verify a real Zookeeper health adapter against a disposable
ensemble or recorded health responses.
