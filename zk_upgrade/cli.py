import click
from rich.console import Console
from rich.table import Table
from .models import Node, Plan
from .orchestrator import rolling

console = Console()

@click.group()
def cli():
    "ZK rolling upgrade orchestrator (simulated)"
    pass

@cli.command()
@click.option("--cluster", required=True)
@click.option("--nodes", required=True, help="Comma-separated (e.g., zk-1,zk-2,zk-3)")
@click.option("--target", "target_version", required=True)
@click.option("--concurrency", default=1, type=int)
def plan(cluster, nodes, target_version, concurrency):
    node_list = []
    for i, n in enumerate(nodes.split(",")):
        role = "leader" if i == 0 else "follower"
        node_list.append(Node(name=n, role=role))
    p = Plan(cluster=cluster, target_version=target_version, nodes=node_list, concurrency=concurrency)

    table = Table(title=f"Plan for {cluster}")
    table.add_column("Node"); table.add_column("Role"); table.add_column("Current"); table.add_column("Target")
    for n in p.nodes:
        table.add_row(n.name, n.role, n.version, target_version)
    console.print(table)

@cli.command()
@click.option("--cluster", required=True)
@click.option("--nodes", required=True)
@click.option("--target", "target_version", required=True)
@click.option("--dry-run", is_flag=True, default=False)
def run(cluster, nodes, target_version, dry_run):
    node_list = []
    for i, n in enumerate(nodes.split(",")):
        role = "leader" if i == 0 else "follower"
        node_list.append(Node(name=n, role=role))
    p = Plan(cluster=cluster, target_version=target_version, nodes=node_list)
    for msg in rolling(p, dry_run=dry_run):
        console.log(msg)

if __name__ == "__main__":
    cli()
