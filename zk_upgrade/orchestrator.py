from typing import List, Iterable
from time import sleep
from .models import Node, Plan
from .health import check_health

class UpgradeError(Exception): pass

def upgrade_node(node: Node, target: str, dry_run: bool = True) -> None:
    if dry_run:
        return
    # pretend to stop, upgrade, start
    sleep(0.5)
    node.version = target
    node.healthy = True

def rolling(plan: Plan, dry_run: bool = True) -> Iterable[str]:
    # leader last
    followers = [n for n in plan.nodes if n.role == "follower"]
    leaders = [n for n in plan.nodes if n.role == "leader"]
    order = followers + leaders
    for node in order:
        yield f"Draining {node.name} (role={node.role})"
        yield f"Upgrading {node.name} -> {plan.target_version}"
        upgrade_node(node, plan.target_version, dry_run=dry_run)
        if not check_health(node):
            raise UpgradeError(f"{node.name} failed health checks post-upgrade")
        yield f"{node.name} healthy on {node.version}"
