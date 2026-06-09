# Linting and Testing Standards

These standards define the checks expected before a pull request is marked ready. Run the sections for the
languages touched by the change.

## Required Gates

- Start from the default branch and keep the PR focused on one reviewable change.
- Run `git diff --check` before committing.
- Run `repowave scan .` when `repowave.toml` is present.
- Run every applicable language command below. If a command needs credentials, a live service, or unavailable
  platform tooling, state that in the PR and run the closest local gate.
- Add or update tests for behavior changes. Documentation-only changes still need the diff and repository gates.

## Python

- Use `uv` with the checked-in lockfile.
- Run Ruff before merging Python changes.
- Run Pytest for upgrade planning, quorum checks, leader handling, and rollback behavior.
- Keep ZooKeeper cluster calls behind fixtures or marked integration tests.

## Current Command Map

- Install: `uv sync`.
- Lint: `uv run ruff check .`.
- Format check: `uv run ruff format --check .`.
- Tests: `uv run pytest -q`.
