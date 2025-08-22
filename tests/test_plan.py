from zk_upgrade.models import Node, Plan

def test_plan_builds():
    nodes = [Node(name="zk-1", role="leader"), Node(name="zk-2"), Node(name="zk-3")]
    p = Plan(cluster="ds-zk", target_version="3.8.2", nodes=nodes, concurrency=1)
    assert p.target_version == "3.8.2"
    assert len(p.nodes) == 3
