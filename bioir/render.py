from __future__ import annotations

from .completion import AssumptionReceipt
from .semantic_model import SemanticModel


def _participant_text(items) -> str:
    if not items:
        return "none"
    return ", ".join(
        f"{item.entity} x {item.stoichiometry:g}" for item in items
    )


def render_model_human(model: SemanticModel) -> str:
    """Deterministic plain-text rendering of the canonical semantic model.

    The rendering is intentionally simple enough for a person, a diff tool, or
    an AI system to inspect without reverse-engineering internal Python objects.
    It is a view of the canonical structured model, not a second source language.
    """

    lines: list[str] = [
        f"Model: {model.name}",
        f"BioIR version: {model.version}",
        "",
        "Compartments:",
    ]

    for compartment in sorted(model.compartments, key=lambda x: x.id):
        name = f" ({compartment.name})" if compartment.name else ""
        lines.append(
            f"- {compartment.id}{name}: size={compartment.size:g} {compartment.unit}"
        )

    lines.extend(["", "Biological entities:"])
    for entity in sorted(model.entities, key=lambda x: x.id):
        name = f" ({entity.name})" if entity.name else ""
        lines.append(
            f"- {entity.id}{name}: {entity.kind}; compartment={entity.compartment}; "
            f"initial={entity.initial_value:g} {entity.unit}; "
            f"quantity={entity.quantity_kind.value}"
        )

    lines.extend(["", "Parameters:"])
    if model.parameters:
        for parameter in sorted(model.parameters, key=lambda x: x.id):
            value = "unresolved" if parameter.value is None else f"{parameter.value:g}"
            name = f" ({parameter.name})" if parameter.name else ""
            lines.append(
                f"- {parameter.id}{name}: value={value}; unit={parameter.unit}; "
                f"constant={str(parameter.constant).lower()}"
            )
    else:
        lines.append("- none")

    lines.extend(["", "Interactions:"])
    if model.interactions:
        for interaction in sorted(model.interactions, key=lambda x: x.id):
            lines.append(
                f"- {interaction.id}: kind={interaction.kind.value}; "
                f"inputs=[{_participant_text(interaction.inputs)}]; "
                f"outputs=[{_participant_text(interaction.outputs)}]; "
                f"modifiers=[{', '.join(interaction.modifiers) or 'none'}]; "
                f"parameters=[{', '.join(interaction.parameter_refs) or 'none'}]; "
                f"reversible={str(interaction.reversible).lower()}"
            )
            lines.append("  mathematical rate law: unresolved")
    else:
        lines.append("- none")

    lines.extend(["", "Provenance:"])
    lines.append(f"- source: {model.provenance.source or 'not supplied'}")
    lines.append(f"- citation: {model.provenance.citation or 'not supplied'}")
    if model.provenance.notes:
        lines.append(f"- notes: {model.provenance.notes}")

    lines.extend(
        [
            "",
            "Interpretation:",
            "- This rendering is a human/AI-readable view of the canonical structured model.",
            "- Missing mathematics is shown explicitly rather than guessed.",
        ]
    )
    return "\n".join(lines) + "\n"


def render_receipt_human(receipt: AssumptionReceipt) -> str:
    """Render an assumption receipt as deterministic, audit-friendly text."""

    lines = [
        f"Completion receipt for: {receipt.model_name}",
        f"Model version: {receipt.model_version}",
        f"Model fingerprint: {receipt.model_fingerprint}",
        f"Target: {receipt.target}",
        (
            "Mathematically complete: yes"
            if receipt.mathematically_complete
            else "Mathematically complete: no"
        ),
        "",
        "Still unresolved:",
    ]

    if receipt.unresolved_commitments:
        for item in receipt.unresolved_commitments:
            lines.append(f"- {item.key}")
            lines.append(f"  category: {item.category}")
            lines.append(f"  location: {item.path}")
            lines.append(f"  reason: {item.reason}")
    else:
        lines.append("- none")

    lines.extend(["", "Compiler assumptions introduced:"])
    if receipt.introduced_assumptions:
        for assumption in receipt.introduced_assumptions:
            ordered = ", ".join(
                f"{key}={assumption[key]}"
                for key in sorted(assumption)
            )
            lines.append(f"- {ordered}")
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "Policy:",
            "- BioIR does not silently infer missing mathematics.",
            "- Any future completion profile must record every introduced assumption.",
        ]
    )
    return "\n".join(lines) + "\n"
