import click
from rich.console import Console
from rich.table import Table

from .models import Node, Plan
from .operations import SimulatedNodeOperator
from .orchestrator import UpgradeEvent, rolling

console = Console()


def format_event(event: UpgradeEvent) -> str:
    if event.stage == "draining":
        return f"Draining {event.node} (role={event.role})"
    if event.stage == "upgrading":
        return f"Upgrading {event.node} -> {event.target_version}"
    if event.dry_run:
        return f"{event.node} health check passed (dry-run, current={event.current_version})"
    return f"{event.node} healthy on {event.current_version}"


def parse_nodes(value: str) -> list[Node]:
    names = [name.strip() for name in value.split(",")]
    if not names or any(not name for name in names):
        raise click.BadParameter("nodes must be a comma-separated list without empty entries")

    return [
        Node(name=name, role="leader" if index == 0 else "follower")
        for index, name in enumerate(names)
    ]


@click.group()
def cli():
    "ZK rolling upgrade orchestrator (simulated)"
    pass


@cli.command()
@click.option("--cluster", required=True)
@click.option("--nodes", required=True, help="Comma-separated (e.g., zk-1,zk-2,zk-3)")
@click.option("--target", "target_version", required=True)
@click.option("--concurrency", default=1, type=click.IntRange(1, 3), show_default=True)
def plan(cluster, nodes, target_version, concurrency):
    node_list = parse_nodes(nodes)
    p = Plan(
        cluster=cluster,
        target_version=target_version,
        nodes=node_list,
        concurrency=concurrency,
    )

    table = Table(title=f"Plan for {cluster}")
    table.add_column("Node")
    table.add_column("Role")
    table.add_column("Current")
    table.add_column("Target")
    for n in p.nodes:
        table.add_row(n.name, n.role, n.version, target_version)
    console.print(table)


@cli.command()
@click.option("--cluster", required=True)
@click.option("--nodes", required=True)
@click.option("--target", "target_version", required=True)
@click.option("--dry-run", is_flag=True, default=False)
def run(cluster, nodes, target_version, dry_run):
    node_list = parse_nodes(nodes)
    p = Plan(cluster=cluster, target_version=target_version, nodes=node_list)
    operator = SimulatedNodeOperator()
    for event in rolling(p, operator, dry_run=dry_run):
        console.log(format_event(event))


if __name__ == "__main__":
    cli()
