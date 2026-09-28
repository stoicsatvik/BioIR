from __future__ import annotations

from bioir.completion import plan_executable_completion
from bioir.render import render_model_human, render_receipt_human
from bioir.semantic_model import SemanticModel


def payload() -> dict:
    return {
        "version": "bioir/semantic/v1",
        "name": "readable_partial_model",
        "compartments": [
            {"id": "cell", "size": 1.0, "unit": "litre"},
        ],
        "entities": [
            {
                "id": "A",
                "compartment": "cell",
                "initial_value": 1.0,
                "quantity_kind": "concentration",
                "unit": "mole_per_litre",
            },
            {
                "id": "B",
                "compartment": "cell",
                "initial_value": 0.0,
                "quantity_kind": "concentration",
                "unit": "mole_per_litre",
            },
        ],
        "parameters": [
            {"id": "k1", "unit": "per_second"},
        ],
        "interactions": [
            {
                "id": "A_to_B",
                "kind": "conversion",
                "inputs": [{"entity": "A"}],
                "outputs": [{"entity": "B"}],
                "parameter_refs": ["k1"],
            }
        ],
        "provenance": {"source": "synthetic readable fixture"},
    }


def test_model_render_is_deterministic_and_exposes_unknowns():
    model = SemanticModel.from_dict(payload())
    first = render_model_human(model)
    second = render_model_human(model)

    assert first == second
    assert "Model: readable_partial_model" in first
    assert "value=unresolved" in first
    assert "mathematical rate law: unresolved" in first
    assert "synthetic readable fixture" in first


def test_receipt_render_is_deterministic_and_auditable():
    model = SemanticModel.from_dict(payload())
    receipt = plan_executable_completion(model)

    text = render_receipt_human(receipt)
    assert text == render_receipt_human(receipt)
    assert "parameter_value:k1" in text
    assert "kinetic_law:A_to_B" in text
    assert "Compiler assumptions introduced:" in text
    assert "- none" in text
    assert receipt.model_fingerprint in text


def test_readable_view_does_not_replace_canonical_model():
    model = SemanticModel.from_dict(payload())
    text = render_model_human(model)

    assert isinstance(text, str)
    assert model.parameters[0].value is None
    assert model.interactions[0].id == "A_to_B"
