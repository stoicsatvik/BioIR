from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
import re

from .semantic_model import QuantityKind, SemanticModel


class SemanticValidationError(ValueError):
    pass


@dataclass(frozen=True)
class ModelIssue:
    severity: str
    code: str
    path: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return {
            "severity": self.severity,
            "code": self.code,
            "path": self.path,
            "message": self.message,
        }


@dataclass(frozen=True)
class ModelCheckReport:
    issues: tuple[ModelIssue, ...]

    @property
    def errors(self) -> tuple[ModelIssue, ...]:
        return tuple(x for x in self.issues if x.severity == "error")

    @property
    def warnings(self) -> tuple[ModelIssue, ...]:
        return tuple(x for x in self.issues if x.severity == "warning")

    @property
    def ok(self) -> bool:
        return not self.errors

    def to_dict(self) -> dict[str, object]:
        return {
            "ok": self.ok,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "issues": [x.to_dict() for x in self.issues],
        }


# Signature = (substance, volume, time). This deliberately small table is a
# compiler contract, not a universal biological unit ontology.
UNIT_SIGNATURES: dict[str, tuple[int, int, int]] = {
    "dimensionless": (0, 0, 0),
    "mole": (1, 0, 0),
    "item": (1, 0, 0),
    "litre": (0, 1, 0),
    "second": (0, 0, 1),
    "mole_per_litre": (1, -1, 0),
    "item_per_litre": (1, -1, 0),
    "per_second": (0, 0, -1),
}

SID_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _issue(
    issues: list[ModelIssue],
    severity: str,
    code: str,
    path: str,
    message: str,
) -> None:
    issues.append(ModelIssue(severity, code, path, message))


def check_semantic_model(model: SemanticModel) -> ModelCheckReport:
    issues: list[ModelIssue] = []

    if model.version != "bioir/semantic/v1":
        _issue(issues, "error", "version.unsupported", "version", model.version)

    symbol_paths: dict[str, str] = {}

    def register(symbol: str, path: str) -> None:
        if not SID_RE.fullmatch(symbol):
            _issue(
                issues,
                "error",
                "id.not_portable",
                path,
                "identifier must be portable to SBML SId syntax",
            )
        if symbol in symbol_paths:
            _issue(
                issues,
                "error",
                "id.duplicate",
                path,
                f"identifier duplicates {symbol_paths[symbol]}",
            )
        else:
            symbol_paths[symbol] = path

    if not model.compartments:
        _issue(
            issues,
            "error",
            "compartment.missing",
            "compartments",
            "at least one compartment is required",
        )
    for index, compartment in enumerate(model.compartments):
        path = f"compartments[{index}]"
        register(compartment.id, f"{path}.id")
        signature = UNIT_SIGNATURES.get(compartment.unit)
        if signature is None:
            _issue(
                issues,
                "error",
                "unit.unknown",
                f"{path}.unit",
                f"unknown unit: {compartment.unit}",
            )
        elif signature != (0, 1, 0):
            _issue(
                issues,
                "error",
                "unit.compartment_not_volume",
                f"{path}.unit",
                "compartment size must use a volume unit",
            )
        if not isfinite(compartment.size) or compartment.size <= 0:
            _issue(
                issues,
                "error",
                "compartment.size",
                f"{path}.size",
                "compartment size must be finite and positive",
            )

    compartments = {x.id for x in model.compartments}
    if not model.entities:
        _issue(
            issues,
            "error",
            "entity.missing",
            "entities",
            "at least one biological entity is required",
        )

    expected_signatures = {
        QuantityKind.AMOUNT: (1, 0, 0),
        QuantityKind.CONCENTRATION: (1, -1, 0),
        QuantityKind.DIMENSIONLESS: (0, 0, 0),
    }

    for index, entity in enumerate(model.entities):
        path = f"entities[{index}]"
        register(entity.id, f"{path}.id")
        if entity.compartment not in compartments:
            _issue(
                issues,
                "error",
                "entity.unknown_compartment",
                f"{path}.compartment",
                f"unknown compartment: {entity.compartment}",
            )
        signature = UNIT_SIGNATURES.get(entity.unit)
        if signature is None:
            _issue(
                issues,
                "error",
                "unit.unknown",
                f"{path}.unit",
                f"unknown unit: {entity.unit}",
            )
        elif signature != expected_signatures[entity.quantity_kind]:
            _issue(
                issues,
                "error",
                "unit.quantity_mismatch",
                f"{path}.unit",
                f"{entity.quantity_kind.value} requires signature "
                f"{expected_signatures[entity.quantity_kind]}, got {signature}",
            )
        if not isfinite(entity.initial_value) or entity.initial_value < 0:
            _issue(
                issues,
                "error",
                "entity.initial_value",
                f"{path}.initial_value",
                "initial value must be finite and non-negative",
            )

    parameters = {x.id for x in model.parameters}
    for index, parameter in enumerate(model.parameters):
        path = f"parameters[{index}]"
        register(parameter.id, f"{path}.id")
        if parameter.unit not in UNIT_SIGNATURES:
            _issue(
                issues,
                "error",
                "unit.unknown",
                f"{path}.unit",
                f"unknown unit: {parameter.unit}",
            )
        if not isfinite(parameter.value):
            _issue(
                issues,
                "error",
                "parameter.value",
                f"{path}.value",
                "parameter value must be finite",
            )

    entities = {x.id for x in model.entities}
    for index, interaction in enumerate(model.interactions):
        path = f"interactions[{index}]"
        register(interaction.id, f"{path}.id")
        participants = list(interaction.inputs) + list(interaction.outputs)
        if not participants and not interaction.modifiers:
            _issue(
                issues,
                "error",
                "interaction.empty",
                path,
                "interaction must reference at least one entity",
            )
        for p_index, participant in enumerate(participants):
            if participant.entity not in entities:
                _issue(
                    issues,
                    "error",
                    "interaction.unknown_entity",
                    f"{path}.participants[{p_index}]",
                    f"unknown entity: {participant.entity}",
                )
            if (
                not isfinite(participant.stoichiometry)
                or participant.stoichiometry <= 0
            ):
                _issue(
                    issues,
                    "error",
                    "interaction.stoichiometry",
                    f"{path}.participants[{p_index}].stoichiometry",
                    "stoichiometry must be finite and positive",
                )
        for modifier in interaction.modifiers:
            if modifier not in entities:
                _issue(
                    issues,
                    "error",
                    "interaction.unknown_modifier",
                    f"{path}.modifiers",
                    f"unknown entity: {modifier}",
                )
        for parameter in interaction.parameter_refs:
            if parameter not in parameters:
                _issue(
                    issues,
                    "error",
                    "interaction.unknown_parameter",
                    f"{path}.parameter_refs",
                    f"unknown parameter: {parameter}",
                )

    if model.provenance.source is None and model.provenance.citation is None:
        _issue(
            issues,
            "warning",
            "provenance.missing",
            "provenance",
            "model has no source or citation metadata",
        )

    return ModelCheckReport(tuple(issues))


def require_valid_semantic_model(model: SemanticModel) -> ModelCheckReport:
    report = check_semantic_model(model)
    if report.errors:
        detail = "; ".join(
            f"{issue.path}: {issue.message}" for issue in report.errors
        )
        raise SemanticValidationError(detail)
    return report
