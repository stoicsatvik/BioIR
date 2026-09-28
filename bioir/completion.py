from __future__ import annotations

from dataclasses import dataclass, fields, is_dataclass
from enum import Enum
from hashlib import sha256
import json
from typing import Any

from .semantic_checks import require_valid_semantic_model
from .semantic_model import SemanticModel


@dataclass(frozen=True)
class UnresolvedCommitment:
    key: str
    category: str
    path: str
    reason: str
    required_for: str

    def to_dict(self) -> dict[str, str]:
        return {
            "key": self.key,
            "category": self.category,
            "path": self.path,
            "reason": self.reason,
            "required_for": self.required_for,
        }


@dataclass(frozen=True)
class AssumptionReceipt:
    model_name: str
    model_version: str
    model_fingerprint: str
    target: str
    introduced_assumptions: tuple[dict[str, str], ...]
    unresolved_commitments: tuple[UnresolvedCommitment, ...]

    @property
    def mathematically_complete(self) -> bool:
        return not self.unresolved_commitments

    def to_dict(self) -> dict[str, Any]:
        return {
            "model_name": self.model_name,
            "model_version": self.model_version,
            "model_fingerprint": self.model_fingerprint,
            "target": self.target,
            "mathematically_complete": self.mathematically_complete,
            "introduced_assumptions": list(self.introduced_assumptions),
            "unresolved_commitments": [
                item.to_dict() for item in self.unresolved_commitments
            ],
            "policy": (
                "BioIR does not silently infer missing mathematics. An executable "
                "backend must resolve each commitment through an explicit profile "
                "or user-supplied assumption and record that choice."
            ),
        }


def _canonical(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value):
        return {
            field.name: _canonical(getattr(value, field.name))
            for field in fields(value)
        }
    if isinstance(value, tuple):
        return [_canonical(item) for item in value]
    if isinstance(value, list):
        return [_canonical(item) for item in value]
    if isinstance(value, dict):
        return {
            str(key): _canonical(item)
            for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))
        }
    return value


def model_fingerprint(model: SemanticModel) -> str:
    payload = json.dumps(
        _canonical(model),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")
    return sha256(payload).hexdigest()


def plan_executable_completion(
    model: SemanticModel,
    target: str = "antimony-or-sbml-executable",
) -> AssumptionReceipt:
    """Return what is still missing before the semantic model is executable.

    This planner is deliberately conservative. It does not guess kinetic laws,
    missing parameter values, or solver semantics. The receipt is the audit
    boundary between what the biological model states and what a later compiler
    profile would have to introduce.
    """

    require_valid_semantic_model(model)
    unresolved: list[UnresolvedCommitment] = []

    for parameter in model.parameters:
        if parameter.value is None:
            unresolved.append(
                UnresolvedCommitment(
                    key=f"parameter_value:{parameter.id}",
                    category="parameter_value",
                    path=f"parameters.{parameter.id}.value",
                    reason=(
                        f"parameter {parameter.id!r} has units/identity but no "
                        "numerical value"
                    ),
                    required_for=target,
                )
            )

    for interaction in model.interactions:
        unresolved.append(
            UnresolvedCommitment(
                key=f"kinetic_law:{interaction.id}",
                category="kinetic_law",
                path=f"interactions.{interaction.id}",
                reason=(
                    f"interaction {interaction.id!r} defines biological topology "
                    "but intentionally does not choose a mathematical rate law"
                ),
                required_for=target,
            )
        )

    return AssumptionReceipt(
        model_name=model.name,
        model_version=model.version,
        model_fingerprint=model_fingerprint(model),
        target=target,
        introduced_assumptions=(),
        unresolved_commitments=tuple(unresolved),
    )
