from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class QuantityKind(str, Enum):
    AMOUNT = "amount"
    CONCENTRATION = "concentration"
    DIMENSIONLESS = "dimensionless"


class InteractionKind(str, Enum):
    CONVERSION = "conversion"
    ASSOCIATION = "association"
    DISSOCIATION = "dissociation"
    TRANSPORT = "transport"
    REGULATION = "regulation"
    GENERIC = "generic"


@dataclass(frozen=True)
class Compartment:
    id: str
    size: float
    unit: str = "litre"
    name: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Compartment":
        return cls(
            id=str(data["id"]),
            size=float(data["size"]),
            unit=str(data.get("unit", "litre")),
            name=str(data["name"]) if data.get("name") is not None else None,
        )


@dataclass(frozen=True)
class Entity:
    id: str
    compartment: str
    initial_value: float
    quantity_kind: QuantityKind
    unit: str
    kind: str = "species"
    name: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Entity":
        return cls(
            id=str(data["id"]),
            compartment=str(data["compartment"]),
            initial_value=float(data["initial_value"]),
            quantity_kind=QuantityKind(str(data["quantity_kind"])),
            unit=str(data["unit"]),
            kind=str(data.get("kind", "species")),
            name=str(data["name"]) if data.get("name") is not None else None,
        )


@dataclass(frozen=True)
class Parameter:
    id: str
    value: float | None = None
    unit: str = "dimensionless"
    constant: bool = True
    name: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Parameter":
        raw_value = data.get("value")
        return cls(
            id=str(data["id"]),
            value=float(raw_value) if raw_value is not None else None,
            unit=str(data.get("unit", "dimensionless")),
            constant=bool(data.get("constant", True)),
            name=str(data["name"]) if data.get("name") is not None else None,
        )


@dataclass(frozen=True)
class Participant:
    entity: str
    stoichiometry: float = 1.0

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Participant":
        return cls(
            entity=str(data["entity"]),
            stoichiometry=float(data.get("stoichiometry", 1.0)),
        )


@dataclass(frozen=True)
class Interaction:
    id: str
    kind: InteractionKind
    inputs: tuple[Participant, ...] = ()
    outputs: tuple[Participant, ...] = ()
    modifiers: tuple[str, ...] = ()
    parameter_refs: tuple[str, ...] = ()
    reversible: bool = False
    name: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Interaction":
        forbidden = {"rate_law", "kinetic_law", "ode", "math", "mathml"}
        present = forbidden.intersection(data)
        if present:
            names = ", ".join(sorted(present))
            raise ValueError(
                "bioir/semantic/v1 does not store mathematical kinetics in the "
                f"user model; move {names} to a compile-time backend profile"
            )
        return cls(
            id=str(data["id"]),
            kind=InteractionKind(str(data.get("kind", "generic"))),
            inputs=tuple(Participant.from_dict(x) for x in data.get("inputs", [])),
            outputs=tuple(Participant.from_dict(x) for x in data.get("outputs", [])),
            modifiers=tuple(str(x) for x in data.get("modifiers", [])),
            parameter_refs=tuple(str(x) for x in data.get("parameter_refs", [])),
            reversible=bool(data.get("reversible", False)),
            name=str(data["name"]) if data.get("name") is not None else None,
        )


@dataclass(frozen=True)
class Provenance:
    source: str | None = None
    citation: str | None = None
    notes: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "Provenance":
        data = data or {}
        return cls(
            source=str(data["source"]) if data.get("source") is not None else None,
            citation=str(data["citation"]) if data.get("citation") is not None else None,
            notes=str(data["notes"]) if data.get("notes") is not None else None,
        )


@dataclass(frozen=True)
class SemanticModel:
    name: str
    compartments: tuple[Compartment, ...]
    entities: tuple[Entity, ...]
    parameters: tuple[Parameter, ...] = ()
    interactions: tuple[Interaction, ...] = ()
    provenance: Provenance = field(default_factory=Provenance)
    version: str = "bioir/semantic/v1"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SemanticModel":
        version = str(data.get("version", "bioir/semantic/v1"))
        if version != "bioir/semantic/v1":
            raise ValueError(f"unsupported semantic model version: {version}")
        return cls(
            name=str(data.get("name", "unnamed_model")),
            compartments=tuple(
                Compartment.from_dict(x) for x in data.get("compartments", [])
            ),
            entities=tuple(Entity.from_dict(x) for x in data.get("entities", [])),
            parameters=tuple(
                Parameter.from_dict(x) for x in data.get("parameters", [])
            ),
            interactions=tuple(
                Interaction.from_dict(x) for x in data.get("interactions", [])
            ),
            provenance=Provenance.from_dict(data.get("provenance")),
            version=version,
        )
