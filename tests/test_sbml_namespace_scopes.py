"""E208: SBML Level 3 V2 SId and UnitSId are separate namespaces.

Research regression only; synthetic model symbols and no biological execution.
Specification: https://sbml.org/specifications/sbml-level-3/version-2/core/release-1/sbml-level-3-version-2-core.pdf
"""
from copy import deepcopy
from xml.etree import ElementTree as ET

import pytest

from bioir.semantic_checks import SemanticValidationError, check_semantic_model
from bioir.semantic_model import SemanticModel
from bioir.sbml_backend import SBML_NS, to_sbml_xml


def _payload():
    return {
        "name": "synthetic_namespace",
        "compartments": [{"id": "cell", "size": 1.0, "unit": "litre"}],
        "entities": [{"id": "A", "compartment": "cell", "initial_value": 1.0,
                      "quantity_kind": "amount", "unit": "item"}],
        "parameters": [{"id": "k", "unit": "per_second", "value": 1.0}],
        "interactions": [{"id": "r", "kind": "conversion",
                          "inputs": [{"entity": "A"}],
                          "outputs": [{"entity": "A"}],
                          "parameter_refs": ["k"]}],
        "provenance": {"source": "synthetic E208 namespace fixture"},
    }


@pytest.mark.parametrize("duplicate", ["cell", "A", "k", "r"])
def test_model_id_cannot_alias_any_component_sid(duplicate):
    payload = _payload()
    payload["name"] = duplicate
    model = SemanticModel.from_dict(payload)
    report = check_semantic_model(model)
    assert not report.ok, f"model id {duplicate} illegally aliases a component SId"
    assert any(issue.code == "id.duplicate" for issue in report.errors)
    with pytest.raises(SemanticValidationError):
        to_sbml_xml(model)


def test_unit_sids_are_separate_from_model_species_and_parameter_sids():
    payload = _payload()
    payload["name"] = "item_per_litre"  # same as a UnitDefinition
    payload["entities"][0]["id"] = "mole_per_litre"  # same as a UnitDefinition
    payload["interactions"][0]["inputs"][0]["entity"] = "mole_per_litre"
    payload["interactions"][0]["outputs"][0]["entity"] = "mole_per_litre"
    payload["parameters"] = [
        {"id": "per_second", "unit": "per_second", "value": 1.0},
        {"id": "p_item", "unit": "item_per_litre", "value": 2.0},
        {"id": "p_mole", "unit": "mole_per_litre", "value": 3.0},
    ]
    payload["interactions"][0]["parameter_refs"] = ["per_second"]
    model = SemanticModel.from_dict(payload)
    assert check_semantic_model(model).ok
    xml = to_sbml_xml(model)
    root = ET.fromstring(xml)
    ns = {"s": SBML_NS}
    unit_ids = {node.attrib["id"] for node in root.findall(".//s:unitDefinition", ns)}
    assert unit_ids == {"item_per_litre", "mole_per_litre", "per_second"}
    parameters = {node.attrib["id"]: node for node in root.findall(".//s:parameter", ns)}
    assert parameters["p_item"].attrib["units"] == "item_per_litre"
    assert parameters["p_mole"].attrib["units"] == "mole_per_litre"
    assert parameters["per_second"].attrib["units"] == "per_second"
    assert to_sbml_xml(model) == xml

    # An independent standards implementation, when available, must not
    # report a duplicate-SId error for cross-namespace reuse.
    libsbml = pytest.importorskip("libsbml")
    document = libsbml.readSBMLFromString(xml)
    assert document.getModel() is not None
    document.checkConsistency()
    sid_collisions = [
        str(document.getError(i).getMessage())
        for i in range(document.getNumErrors())
        if document.getError(i).getErrorId() == 10301
    ]
    assert not sid_collisions
