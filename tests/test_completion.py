from __future__ import annotations

from xml.etree import ElementTree as ET

from bioir.completion import model_fingerprint, plan_executable_completion
from bioir.semantic_checks import check_semantic_model
from bioir.semantic_model import SemanticModel
from bioir.sbml_backend import SBML_NS, to_sbml_xml


def incomplete_payload() -> dict:
    return {
        "version": "bioir/semantic/v1",
        "name": "underspecified_conversion",
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
        "provenance": {
            "source": "synthetic partial-model fixture",
        },
    }


def test_partial_parameter_is_valid_but_reported_as_unresolved() -> None:
    model = SemanticModel.from_dict(incomplete_payload())
    report = check_semantic_model(model)

    assert report.ok
    assert any(
        issue.code == "parameter.value_unresolved"
        for issue in report.warnings
    )

    receipt = plan_executable_completion(model)
    keys = {item.key for item in receipt.unresolved_commitments}
    assert keys == {"parameter_value:k1", "kinetic_law:A_to_B"}
    assert receipt.introduced_assumptions == ()
    assert receipt.mathematically_complete is False


def test_structural_sbml_preserves_missing_parameter_value_without_inventing_one() -> None:
    model = SemanticModel.from_dict(incomplete_payload())
    xml = to_sbml_xml(model)
    root = ET.fromstring(xml)
    ns = {"s": SBML_NS}

    parameter = root.find(".//s:parameter[@id='k1']", ns)
    assert parameter is not None
    assert "value" not in parameter.attrib
    assert root.find(".//s:kineticLaw", ns) is None


def test_completion_receipt_is_deterministic() -> None:
    model = SemanticModel.from_dict(incomplete_payload())
    first = plan_executable_completion(model)
    second = plan_executable_completion(model)

    assert first == second
    assert first.model_fingerprint == model_fingerprint(model)
    assert len(first.model_fingerprint) == 64


def test_setting_parameter_value_changes_fingerprint_but_not_hidden_kinetics() -> None:
    payload = incomplete_payload()
    payload["parameters"][0]["value"] = 0.1
    model = SemanticModel.from_dict(payload)

    receipt = plan_executable_completion(model)
    keys = {item.key for item in receipt.unresolved_commitments}
    assert keys == {"kinetic_law:A_to_B"}
