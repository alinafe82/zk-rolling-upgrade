from time import sleep
from .models import Node

def check_health(node: Node, timeout: int = 30) -> bool:
    # Simulated 'mntr' health — in reality, call zk_mntr and parse response.
    for _ in range(timeout // 2):
        if node.healthy:
            return True
        sleep(2)
    return False
