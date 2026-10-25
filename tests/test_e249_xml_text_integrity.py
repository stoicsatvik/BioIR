"""E249: XML 1.0 character-integrity gate for simulation-only SBML export.

Synthetic names and metadata only. This test must fail against E229 because
ElementTree serializes prohibited control/surrogate characters without error.
"""
from copy import deepcopy
from xml.etree import ElementTree as ET

import pytest

from bioir.semantic_checks import SemanticValidationError, check_semantic_model
from bioir.semantic_model import SemanticModel
from bioir.sbml_backend import SBML_NS, BIOIR_NS, to_sbml_xml


def fixture():
    return {
        "name": "synthetic_xml_gate",
        "compartments": [{"id": "cell", "size": 1.0, "unit": "litre"}],
        "entities": [{"id": "A", "compartment": "cell", "initial_value": 1.0,
                      "quantity_kind": "amount", "unit": "item"}],
        "parameters": [{"id": "k", "unit": "per_second", "value": 1.0}],
        "interactions": [{"id": "r", "kind": "generic",
                          "inputs": [{"entity": "A"}],
                          "outputs": [{"entity": "A"}],
                          "parameter_refs": ["k"]}],
        "provenance": {"source": "synthetic fixture", "citation": "fixture only"},
    }


@pytest.mark.parametrize("path,illegal", [
    (("provenance", "source"), "\x00"),
    (("provenance", "citation"), "\x0b"),
    (("compartments", 0, "name"), "\ud800"),
    (("entities", 0, "name"), "\uffff"),
    (("parameters", 0, "name"), "\x1f"),
    (("interactions", 0, "name"), "\udfff"),
])
def test_illegal_xml_character_rejected_before_serialization(path, illegal):
    payload = deepcopy(fixture())
    obj = payload
    for key in path[:-1]:
        obj = obj[key]
    obj[path[-1]] = "valid" + illegal + "text"
    model = SemanticModel.from_dict(payload)
    report = check_semantic_model(model)
    assert not report.ok
    assert any(issue.code == "text.invalid_xml_char" for issue in report.errors)
    with pytest.raises(SemanticValidationError, match="XML"):
        to_sbml_xml(model)


def test_legal_unicode_and_xml_escapes_roundtrip_without_corruption():
    payload = fixture()
    payload["provenance"]["source"] = "Study & validation <audit> \u03a9\t\n"
    payload["provenance"]["citation"] = "synthetic \"quoted\" reference"
    payload["entities"][0]["name"] = "Symbol \u03b1 & <beta>"
    model = SemanticModel.from_dict(payload)
    assert check_semantic_model(model).ok
    xml = to_sbml_xml(model)
    root = ET.fromstring(xml)
    ns = {"s": SBML_NS, "b": BIOIR_NS}
    metadata = root.find(".//b:semanticModel", ns)
    species = root.find(".//s:species", ns)
    assert metadata.attrib["source"] == payload["provenance"]["source"]
    assert metadata.attrib["citation"] == payload["provenance"]["citation"]
    assert species.attrib["name"] == payload["entities"][0]["name"]
    assert to_sbml_xml(model) == xml
