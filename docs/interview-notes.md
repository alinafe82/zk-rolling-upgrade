# Interview Notes

## 60-Second Explanation

This is a small Python CLI that models a safe Zookeeper rolling upgrade. It builds an upgrade
plan, upgrades followers before the leader, validates health after each node, and stops on
failure. I kept it as a simulator so the orchestration logic is reviewable and testable without
requiring a real cluster.

## Decisions I Can Defend

- Leader-last ordering is a conservative default for coordination services.
- The executor is isolated because real environments differ.
- Dry-run output is treated as a first-class path so operators can review the sequence.

## Tradeoffs

The repo does not model every quorum edge case. That keeps the example focused, but a production
tool would need quorum-aware batch planning, timeout handling, rollback policy, and persistent
run state.

## Fixes Made During Portfolio Hardening

- Declared test and lint tooling in `pyproject.toml`.
- Added local pytest import configuration so a fresh clone can run tests with `uv`.
- Added architecture and ADR notes to make the scope explicit.

## Likely Questions

**Why not upgrade nodes concurrently?**
Concurrency is risky for coordination systems unless the planner understands quorum. I would
add concurrency only after the planner can prove the cluster remains healthy after each batch.

**What would make this production-ready?**
A real health adapter, persistent state, audited execution, explicit rollback behavior, and
integration tests against a disposable Zookeeper cluster.

**What does this show for Engineering Productivity?**
It shows how I think about operational automation: dry runs, health gates, small interfaces,
and failure containment before convenience features.
