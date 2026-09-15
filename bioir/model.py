from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class OpCode(str, Enum):
    SENSE = "SENSE"
    INCREASE = "INCREASE"
    DECREASE = "DECREASE"
    MAINTAIN = "MAINTAIN"
    WAIT = "WAIT"


@dataclass(frozen=True)
class Objective:
    variable: str
    target: float
    tolerance: float = 0.05

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Objective":
        return cls(
            variable=str(data["variable"]),
            target=float(data["target"]),
            tolerance=float(data.get("tolerance", 0.05)),
        )


@dataclass(frozen=True)
class Constraints:
    max_steps: int = 25
    max_action_magnitude: float = 0.1

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "Constraints":
        data = data or {}
        return cls(
            max_steps=int(data.get("max_steps", 25)),
            max_action_magnitude=float(data.get("max_action_magnitude", 0.1)),
        )


@dataclass
class Program:
    name: str
    state: dict[str, float]
    objectives: list[Objective]
    constraints: Constraints = field(default_factory=Constraints)
    version: str = "bioir/v0"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Program":
        return cls(
            name=str(data.get("name", "unnamed")),
            state={str(k): float(v) for k, v in data.get("state", {}).items()},
            objectives=[Objective.from_dict(x) for x in data.get("objectives", [])],
            constraints=Constraints.from_dict(data.get("constraints")),
            version=str(data.get("version", "bioir/v0")),
        )


@dataclass(frozen=True)
class Operation:
    opcode: OpCode
    variable: str | None = None
    magnitude: float | None = None
    target: float | None = None
    tolerance: float | None = None
    steps: int | None = None

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {"op": self.opcode.value}
        for key in ("variable", "magnitude", "target", "tolerance", "steps"):
            value = getattr(self, key)
            if value is not None:
                out[key] = value
        return out
