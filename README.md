# zk-rolling-upgrade

Rolling-upgrade planner and runner for a Zookeeper ensemble. The control flow models the part that matters: order the nodes, drain each one in turn, run a post-step health check, and stop the rollout the moment a node fails its check.

The default health-check adapter is local, so the repo can be reviewed end-to-end without a real Zookeeper cluster. A production adapter would wrap `mntr`, `ruok`, `stat`, or a service-discovery health API. The orchestrator and the adapter interface stay the same.

## Why leader-last matters

Zookeeper writes go to the leader and replicate to followers. Upgrading the leader first does two avoidable things: it forces a leader election while followers are still on the old version (mixed-version election windows are where upgrade incidents come from), and it concentrates the riskiest restart at the start of the rollout instead of the end. Followers-first means each follower gets a clean upgrade against a stable leader, and the final restart happens once the rest of the ensemble has already proved itself on the new version.

Plans must contain exactly one leader. An ensemble in an undefined or split-brain state should fail at plan-construction time, not partway through a rollout.

## Quickstart

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest -q
python -m zk_upgrade.cli plan --cluster ds-zk --nodes zk-1,zk-2,zk-3 --target 3.8.2
python -m zk_upgrade.cli run  --cluster ds-zk --nodes zk-1,zk-2,zk-3 --target 3.8.2 --dry-run
```

With `uv`:

```bash
uv run --extra dev pytest
uv run python -m zk_upgrade.cli plan --cluster ds-zk --nodes zk-1,zk-2,zk-3 --target 3.8.2
```

## Control flow

- `zk_upgrade.models.Node` and `Plan` carry the schema. `Plan.require_single_leader` rejects a plan with zero or two-plus leaders before any upgrade step runs.
- `zk_upgrade.orchestrator.rolling` orders followers first, then the leader. Between nodes it calls `health.check_health`. The first failed check raises `UpgradeError` and stops the generator.
- `zk_upgrade.health.check_health` is the local adapter. The interface is what a real adapter would replace.
- `zk_upgrade.cli` handles input parsing, including rejecting empty node entries.

Design notes: [docs/architecture.md](docs/architecture.md). Operator flow: [docs/runbook.md](docs/runbook.md).

## What the tests prove

- followers run before the leader, in order.
- a failed health check raises `UpgradeError` and the rollout stops at that node.
- empty entries in the CLI node list (`zk-1,,zk-3`) are rejected up front.
- a plan with zero or multiple leaders fails at construction time.
- `dry_run=True` does not mutate node versions (added in this pass).

## Adapter work left before this could touch a real cluster

- A `mntr`/`ruok`/`stat` health adapter implementing the `check_health` interface.
- A real upgrade action: stop the service, install the target package, start the service, wait for the four-letter-word response to return `imok`.
- Quorum-aware batch planning when the ensemble has five or more nodes. Today the orchestrator upgrades one node at a time. Anything larger than three nodes needs explicit batch math (`floor((n-1)/2)` per batch keeps quorum during the rollout).
- Persistent state so a partial run can resume from the last healthy node.

## Operational notes

- [docs/runbook.md](docs/runbook.md)
- [docs/security-notes.md](docs/security-notes.md)
- [docs/production-readiness.md](docs/production-readiness.md)
- [docs/interview-notes.md](docs/interview-notes.md)
