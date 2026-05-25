from typing import Literal

from pydantic import BaseModel, Field


class Node(BaseModel):
    name: str
    version: str = "3.8.0"
    role: Literal["leader", "follower"] = "follower"
    healthy: bool = True


class Plan(BaseModel):
    cluster: str
    target_version: str
    nodes: list[Node]
    concurrency: int = Field(1, ge=1, le=3)
