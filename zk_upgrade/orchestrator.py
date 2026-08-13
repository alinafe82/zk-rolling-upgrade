from collections.abc import Iterable
from dataclasses import dataclass
from typing import Literal

from .models import Node, Plan
from .operations import NodeOperator


class UpgradeError(Exception):
    pass


UpgradeStage = Literal["draining", "upgrading", "healthy"]


@dataclass(frozen=True)
class UpgradeEvent:
    stage: UpgradeStage
    node: str
    role: Literal["leader", "follower"]
    current_version: str
    target_version: str
    dry_run: bool


def _event(stage: UpgradeStage, node: Node, plan: Plan, dry_run: bool) -> UpgradeEvent:
    return UpgradeEvent(
        stage=stage,
        node=node.name,
        role=node.role,
        current_version=node.version,
        target_version=plan.target_version,
        dry_run=dry_run,
    )


def rolling(
    plan: Plan,
    operator: NodeOperator,
    dry_run: bool = True,
) -> Iterable[UpgradeEvent]:
    # leader last
    followers = [n for n in plan.nodes if n.role == "follower"]
    leaders = [n for n in plan.nodes if n.role == "leader"]
    order = followers + leaders
    for node in order:
        yield _event("draining", node, plan, dry_run)
        yield _event("upgrading", node, plan, dry_run)
        operator.upgrade(node, plan.target_version, dry_run=dry_run)
        if not operator.wait_until_healthy(node):
            raise UpgradeError(f"{node.name} failed health checks post-upgrade")
        yield _event("healthy", node, plan, dry_run)
