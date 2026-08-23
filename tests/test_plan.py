import pytest
from click.testing import CliRunner
from pydantic import ValidationError

from zk_upgrade.cli import cli
from zk_upgrade.models import Node, Plan
from zk_upgrade.orchestrator import UpgradeError, rolling


class RecordingNodeOperator:
    def __init__(self, unhealthy: set[str] | None = None) -> None:
        self.unhealthy = unhealthy or set()
        self.calls: list[tuple[str, str, str | bool]] = []

    def upgrade(self, node: Node, target_version: str, *, dry_run: bool) -> None:
        self.calls.append(("upgrade", node.name, dry_run))

    def wait_until_healthy(self, node: Node) -> bool:
        self.calls.append(("health", node.name, node.version))
        return node.name not in self.unhealthy


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
    operator = RecordingNodeOperator()

    events = list(rolling(plan, operator, dry_run=True))

    assert [event.node for event in events if event.stage == "draining"] == [
        "zk-2",
        "zk-3",
        "zk-1",
    ]
    assert operator.calls == [
        ("upgrade", "zk-2", True),
        ("health", "zk-2", "3.8.0"),
        ("upgrade", "zk-3", True),
        ("health", "zk-3", "3.8.0"),
        ("upgrade", "zk-1", True),
        ("health", "zk-1", "3.8.0"),
    ]


def test_rolling_stops_on_failed_health_check():
    nodes = [
        Node(name="zk-1", role="leader"),
        Node(name="zk-2", role="follower", healthy=False),
    ]
    plan = Plan(cluster="ds-zk", target_version="3.8.2", nodes=nodes)
    operator = RecordingNodeOperator(unhealthy={"zk-2"})

    with pytest.raises(UpgradeError, match="zk-2 failed health checks"):
        list(rolling(plan, operator, dry_run=True))

    assert operator.calls == [
        ("upgrade", "zk-2", True),
        ("health", "zk-2", "3.8.0"),
    ]


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


def test_cli_run_reports_structured_events_through_the_simulated_operator():
    runner = CliRunner()

    result = runner.invoke(
        cli,
        [
            "run",
            "--cluster",
            "ds-zk",
            "--nodes",
            "zk-1,zk-2,zk-3",
            "--target",
            "3.8.2",
            "--dry-run",
        ],
    )

    assert result.exit_code == 0
    assert "Draining zk-2 (role=follower)" in result.output
    assert "zk-1 health check passed (dry-run, current=3.8.0)" in result.output


def test_dry_run_does_not_mutate_node_versions():
    nodes = [
        Node(name="zk-1", role="leader"),
        Node(name="zk-2", role="follower"),
        Node(name="zk-3", role="follower"),
    ]
    starting_versions = {node.name: node.version for node in nodes}
    plan = Plan(cluster="ds-zk", target_version="3.8.2", nodes=nodes)
    operator = RecordingNodeOperator()

    # Consume the generator under dry_run. No node should have its
    # version field flipped to the target.
    list(rolling(plan, operator, dry_run=True))

    for node in plan.nodes:
        assert node.version == starting_versions[node.name], (
            f"{node.name} version changed under dry_run"
        )


def test_live_success_events_report_target_without_model_mutation():
    nodes = [
        Node(name="zk-1", role="leader"),
        Node(name="zk-2", role="follower"),
    ]
    plan = Plan(cluster="ds-zk", target_version="3.8.2", nodes=nodes)
    operator = RecordingNodeOperator()

    events = list(rolling(plan, operator, dry_run=False))

    healthy_events = [event for event in events if event.stage == "healthy"]
    assert [event.current_version for event in healthy_events] == ["3.8.2", "3.8.2"]
    assert [node.version for node in plan.nodes] == ["3.8.0", "3.8.0"]


def test_plan_requires_single_leader():
    with pytest.raises(ValidationError, match="exactly one leader"):
        Plan(
            cluster="ds-zk",
            target_version="3.8.2",
            nodes=[Node(name="zk-1"), Node(name="zk-2")],
        )

    with pytest.raises(ValidationError, match="exactly one leader"):
        Plan(
            cluster="ds-zk",
            target_version="3.8.2",
            nodes=[
                Node(name="zk-1", role="leader"),
                Node(name="zk-2", role="leader"),
            ],
        )


def test_plan_rejects_duplicate_node_names():
    with pytest.raises(ValidationError, match="duplicate node names: zk-1"):
        Plan(
            cluster="ds-zk",
            target_version="3.8.2",
            nodes=[
                Node(name="zk-1", role="leader"),
                Node(name="zk-1", role="follower"),
            ],
        )


def test_models_normalize_names_and_reject_blank_identifiers():
    plan = Plan(
        cluster="  ds-zk  ",
        target_version="  3.8.2  ",
        nodes=[Node(name="  zk-1  ", version="  3.8.0  ", role="leader")],
    )

    assert plan.cluster == "ds-zk"
    assert plan.target_version == "3.8.2"
    assert plan.nodes[0].name == "zk-1"
    assert plan.nodes[0].version == "3.8.0"

    with pytest.raises(ValidationError, match="must not be blank"):
        Node(name="   ")
