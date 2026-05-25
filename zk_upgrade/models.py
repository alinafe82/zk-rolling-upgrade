from typing import Literal

from pydantic import BaseModel, Field, model_validator


class Node(BaseModel):
    name: str = Field(..., min_length=1)
    version: str = Field("3.8.0", min_length=1)
    role: Literal["leader", "follower"] = "follower"
    healthy: bool = True


class Plan(BaseModel):
    cluster: str = Field(..., min_length=1)
    target_version: str = Field(..., min_length=1)
    nodes: list[Node] = Field(..., min_length=1)
    concurrency: int = Field(1, ge=1, le=3)

    @model_validator(mode="after")
    def require_single_leader(self) -> "Plan":
        leaders = [node for node in self.nodes if node.role == "leader"]
        if len(leaders) != 1:
            raise ValueError("plan must contain exactly one leader")
        return self
