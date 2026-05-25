# Security Notes

## Threat Assumptions

- This repo is a local simulator and does not connect to a real Zookeeper ensemble.
- CLI inputs are provided by an operator or reviewer, not by an untrusted public user.
- No secrets are required for the default workflow.

## What It Protects Against

- Accidental unsafe ordering in the modeled workflow by upgrading followers before the leader.
- Continuing after a failed health check.
- Empty node names in CLI input.
- Secret commits through repository secret scanning and pre-commit guidance.

## What It Does Not Protect Against

- Real host compromise, SSH misuse, package-manager failure, or Kubernetes rollout failure.
- Split-brain or quorum loss in a real ensemble.
- Malicious operator input beyond basic validation.

## Safe Local Usage

Run the tool in dry-run mode when reviewing behavior:

```bash
uv run python -m zk_upgrade.cli run --cluster ds-zk --nodes zk-1,zk-2,zk-3 --target 3.8.2 --dry-run
```

Do not add real credentials, hostnames, or private cluster data to examples or tests.

## Known Limitations

The current implementation is intentionally non-mutating. A production executor would need
quorum checks, timeouts, audit logs, rollback instructions, and explicit approval before any
node operation.
