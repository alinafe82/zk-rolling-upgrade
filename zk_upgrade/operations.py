from time import sleep
from typing import Protocol

from .health import check_health
from .models import Node


class NodeOperator(Protocol):
    def upgrade(self, node: Node, target_version: str, *, dry_run: bool) -> None: ...

    def wait_until_healthy(self, node: Node) -> bool: ...


class SimulatedNodeOperator:
    def upgrade(self, node: Node, target_version: str, *, dry_run: bool) -> None:
        if dry_run:
            return
        sleep(0.5)
        node.version = target_version
        node.healthy = True

    def wait_until_healthy(self, node: Node) -> bool:
        return check_health(node)
