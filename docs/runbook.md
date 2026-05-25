# Runbook

## Run Locally

```bash
uv run python -m zk_upgrade.cli plan --cluster ds-zk --nodes zk-1,zk-2,zk-3 --target 3.8.2
uv run python -m zk_upgrade.cli run --cluster ds-zk --nodes zk-1,zk-2,zk-3 --target 3.8.2 --dry-run
```

## Test

```bash
uv run --extra dev pytest
uv run --extra dev ruff check .
```

## Common Failure Modes

- `nodes must be a comma-separated list without empty entries`: remove empty entries from
  `--nodes`.
- `failed health checks post-upgrade`: the orchestrator stopped after a node was unhealthy.
- `concurrency` validation error: use a value from 1 to 3.

## Troubleshooting

- Start with `plan` to verify the node order.
- Use `--dry-run` until a real executor exists.
- If a health failure is expected in a test, verify the unhealthy node is ordered before any
  node you expect to remain untouched.

## Safe Cleanup

The local simulator does not create files or mutate infrastructure. Remove `.venv`,
`.pytest_cache`, or `__pycache__` directories if you want a clean workspace.

## Known Limitations

This is not a real Zookeeper upgrade runner. It models the workflow and failure boundary that a
real adapter would use.
