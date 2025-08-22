# zk-rolling-upgrade
> Simulated zero-downtime Zookeeper rolling upgrade orchestrator

This project showcases a Python CLI that performs a **rolling upgrade** of Zookeeper nodes with health checks,
dry-run mode, concurrency control, and post-upgrade validation — modeled after enterprise patterns.

## Highlights
- Rolling upgrade strategy with leader awareness
- Health checks via `mntr`-like mock interface
- `--dry-run` and `--concurrency` knobs
- Structured logging and graceful error handling
- Unit tests and typed models (`pydantic`)
- Designed for extension to real clusters

## Quickstart
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest -q
python -m zk_upgrade.cli plan --cluster ds-zk --nodes zk-1,zk-2,zk-3 --target 3.8.2
python -m zk_upgrade.cli run  --cluster ds-zk --nodes zk-1,zk-2,zk-3 --target 3.8.2 --dry-run
```
