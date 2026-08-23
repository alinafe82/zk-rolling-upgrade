from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator


def _normalized_identifier(value: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValueError("must not be blank")
    return normalized


class Node(BaseModel):
    name: str = Field(..., min_length=1)
    version: str = Field("3.8.0", min_length=1)
    role: Literal["leader", "follower"] = "follower"
    healthy: bool = True

    _normalize_name = field_validator("name", mode="before")(_normalized_identifier)
    _normalize_version = field_validator("version", mode="before")(_normalized_identifier)


class Plan(BaseModel):
    cluster: str = Field(..., min_length=1)
    target_version: str = Field(..., min_length=1)
    nodes: list[Node] = Field(..., min_length=1)
    concurrency: int = Field(1, ge=1, le=3)

    _normalize_cluster = field_validator("cluster", mode="before")(_normalized_identifier)
    _normalize_target_version = field_validator("target_version", mode="before")(
        _normalized_identifier
    )

    @model_validator(mode="after")
    def require_single_leader(self) -> "Plan":
        leaders = [node for node in self.nodes if node.role == "leader"]
        if len(leaders) != 1:
            raise ValueError("plan must contain exactly one leader")

        names = [node.name for node in self.nodes]
        duplicates = sorted({name for name in names if names.count(name) > 1})
        if duplicates:
            raise ValueError(f"duplicate node names: {', '.join(duplicates)}")
        return self
