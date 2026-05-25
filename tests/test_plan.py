import pytest
from click.testing import CliRunner

from zk_upgrade.cli import cli
from zk_upgrade.models import Node, Plan
from zk_upgrade.orchestrator import UpgradeError, rolling


def test_plan_builds():
    nodes = [Node(name="zk-1", role="leader"), Node(name="zk-2"), Node(name="zk-3")]
    p = Plan(cluster="ds-zk", target_version="3.8.2", nodes=nodes, concurrency=1)
    assert p.target_version == "3.8.2"
    assert len(p.nodes) == 3


def test_rolling_upgrades_followers_before_leader():
    nodes = [
        Node(name="zk-1", role="leader"),
        Node(name="zk-2", role="follower"),
        Node(name="zk-3", role="follower"),
    ]
    plan = Plan(cluster="ds-zk", target_version="3.8.2", nodes=nodes)

    messages = list(rolling(plan, dry_run=True))

    drain_messages = [message for message in messages if message.startswith("Draining")]
    assert drain_messages == [
        "Draining zk-2 (role=follower)",
        "Draining zk-3 (role=follower)",
        "Draining zk-1 (role=leader)",
    ]
    assert "zk-2 health check passed (dry-run, current=3.8.0)" in messages


def test_rolling_stops_on_failed_health_check():
    nodes = [
        Node(name="zk-1", role="leader"),
        Node(name="zk-2", role="follower", healthy=False),
    ]
    plan = Plan(cluster="ds-zk", target_version="3.8.2", nodes=nodes)

    with pytest.raises(UpgradeError, match="zk-2 failed health checks"):
        list(rolling(plan, dry_run=True))


def test_cli_rejects_empty_node_entries():
    runner = CliRunner()

    result = runner.invoke(
        cli,
        [
            "plan",
            "--cluster",
            "ds-zk",
            "--nodes",
            "zk-1,,zk-3",
            "--target",
            "3.8.2",
        ],
    )

    assert result.exit_code != 0
    assert "empty entries" in result.output
