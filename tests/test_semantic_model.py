from __future__ import annotations

from xml.etree import ElementTree as ET

import pytest

from bioir.semantic_checks import (
    SemanticValidationError,
    check_semantic_model,
    require_valid_semantic_model,
)
from bioir.semantic_model import SemanticModel
from bioir.sbml_backend import BIOIR_NS, SBML_NS, to_sbml_xml


def valid_payload() -> dict:
    return {
        "version": "bioir/semantic/v1",
        "name": "toy_conversion",
        "compartments": [
            {"id": "cell", "size": 1.0, "unit": "litre"},
        ],
        "entities": [
            {
                "id": "substrate",
                "compartment": "cell",
                "initial_value": 1.0,
                "quantity_kind": "concentration",
                "unit": "mole_per_litre",
            },
            {
                "id": "product",
                "compartment": "cell",
                "initial_value": 0.0,
                "quantity_kind": "concentration",
                "unit": "mole_per_litre",
            },
        ],
        "parameters": [
            {"id": "k1", "value": 0.1, "unit": "per_second"},
        ],
        "interactions": [
            {
                "id": "conversion_1",
                "kind": "conversion",
                "inputs": [{"entity": "substrate", "stoichiometry": 1}],
                "outputs": [{"entity": "product", "stoichiometry": 1}],
                "parameter_refs": ["k1"],
            }
        ],
        "provenance": {"source": "synthetic test fixture"},
    }


def test_user_model_rejects_embedded_mathematical_kinetics() -> None:
    payload = valid_payload()
    payload["interactions"][0]["rate_law"] = "k1 * substrate"
    with pytest.raises(ValueError, match="compile-time backend profile"):
        SemanticModel.from_dict(payload)


def test_static_checks_accept_typed_semantic_model() -> None:
    report = check_semantic_model(SemanticModel.from_dict(valid_payload()))
    assert report.ok
    assert not report.errors


def test_static_checks_reject_unit_mismatch_before_lowering() -> None:
    payload = valid_payload()
    payload["entities"][0]["unit"] = "second"
    model = SemanticModel.from_dict(payload)
    report = check_semantic_model(model)
    assert not report.ok
    assert any(x.code == "unit.quantity_mismatch" for x in report.errors)
    with pytest.raises(SemanticValidationError):
        to_sbml_xml(model)


def test_static_checks_reject_unknown_references() -> None:
    payload = valid_payload()
    payload["interactions"][0]["outputs"][0]["entity"] = "missing_species"
    report = check_semantic_model(SemanticModel.from_dict(payload))
    assert any(x.code == "interaction.unknown_entity" for x in report.errors)


def test_sbml_lowering_preserves_structure_without_kinetic_law() -> None:
    model = SemanticModel.from_dict(valid_payload())
    xml = to_sbml_xml(model)
    root = ET.fromstring(xml)

    ns = {"s": SBML_NS, "b": BIOIR_NS}
    assert root.attrib["level"] == "3"
    assert root.attrib["version"] == "2"
    assert root.find(".//s:compartment[@id='cell']", ns) is not None
    assert root.find(".//s:species[@id='substrate']", ns) is not None
    assert root.find(".//s:species[@id='product']", ns) is not None
    assert root.find(".//s:reaction[@id='conversion_1']", ns) is not None
    assert root.find(".//s:kineticLaw", ns) is None

    semantic = root.find(
        ".//s:reaction[@id='conversion_1']/s:annotation/b:interaction",
        ns,
    )
    assert semantic is not None
    assert semantic.attrib["mathematicalRepresentationCommitted"] == "false"


def test_sbml_lowering_is_deterministic() -> None:
    model = SemanticModel.from_dict(valid_payload())
    assert to_sbml_xml(model) == to_sbml_xml(model)


def test_unknown_unit_is_rejected() -> None:
    payload = valid_payload()
    payload["parameters"][0]["unit"] = "mystery_flux_unit"
    model = SemanticModel.from_dict(payload)
    with pytest.raises(SemanticValidationError):
        require_valid_semantic_model(model)
