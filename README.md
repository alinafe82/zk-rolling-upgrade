# zk-rolling-upgrade
Simulated Zookeeper rolling upgrade planner and runner.

This repo models the control flow behind a rolling Zookeeper upgrade: plan node order,
upgrade followers before leaders, run health checks after each node, and keep a dry-run mode
for review before changing a cluster.

It is intentionally a simulator. It does not connect to a real Zookeeper ensemble or execute
package-manager commands. The value is in the orchestration shape, failure boundaries, and
testable upgrade plan.

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

## Design Notes
- `zk_upgrade.models` defines the cluster and upgrade plan.
- `zk_upgrade.orchestrator` owns upgrade ordering and post-step health validation.
- `zk_upgrade.health` is the local health-check interface; a real adapter would wrap `mntr`,
  four-letter-word commands, or a service discovery health API.
- `zk_upgrade.cli` keeps command parsing outside the orchestration logic.

## Testing
```bash
uv run --extra dev pytest
uv run --extra dev ruff check .
```

## Limitations
- The upgrade action is simulated.
- There is no quorum math yet beyond leader-last ordering.
- Concurrency is represented in the interface but not wired into parallel execution.

## Future Improvements
- Add a real Zookeeper health adapter.
- Add quorum-aware batch planning.
- Persist upgrade state so a failed run can resume from the last healthy node.

## Interview Notes
See [docs/interview-notes.md](docs/interview-notes.md).
