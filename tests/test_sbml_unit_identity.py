"""Regression: item counts must never silently become moles in SBML.

Synthetic model only; this checks unit semantics, not biological validity.
"""
from xml.etree import ElementTree as ET

import pytest

from bioir.semantic_model import SemanticModel
from bioir.sbml_backend import SBML_NS, to_sbml_xml


@pytest.mark.parametrize(
    ("parameter_unit", "expected_kinds"),
    [
        ("item_per_litre", {"item": 1, "litre": -1}),
        ("mole_per_litre", {"mole": 1, "litre": -1}),
        ("per_second", {"second": -1}),
    ],
)
def test_parameter_unit_identity_is_preserved(parameter_unit, expected_kinds):
    model = SemanticModel.from_dict(
        {
            "name": "synthetic_unit_identity",
            "compartments": [{"id": "cell", "size": 1.0, "unit": "litre"}],
            "entities": [
                {
                    "id": "A",
                    "compartment": "cell",
                    "initial_value": 1.0,
                    "quantity_kind": "amount",
                    "unit": "item",
                }
            ],
            "parameters": [{"id": "p", "unit": parameter_unit, "value": 1.0}],
            "provenance": {"source": "synthetic regression fixture"},
        }
    )
    xml = to_sbml_xml(model)
    root = ET.fromstring(xml)
    ns = {"s": SBML_NS}
    definition = root.find(f".//s:unitDefinition[@id='{parameter_unit}']", ns)
    assert definition is not None
    observed = {
        item.attrib["kind"]: int(item.attrib["exponent"])
        for item in definition.findall("s:listOfUnits/s:unit", ns)
    }
    assert observed == expected_kinds
    assert root.find(".//s:species[@id='A']", ns).attrib["substanceUnits"] == "item"
    assert to_sbml_xml(model) == xml


def test_libsbml_preserves_item_kind_when_available():
    libsbml = pytest.importorskip("libsbml")
    model = SemanticModel.from_dict(
        {
            "name": "synthetic_item_parameter",
            "compartments": [{"id": "cell", "size": 1.0, "unit": "litre"}],
            "entities": [
                {
                    "id": "A",
                    "compartment": "cell",
                    "initial_value": 1.0,
                    "quantity_kind": "amount",
                    "unit": "item",
                }
            ],
            "parameters": [{"id": "p", "unit": "item_per_litre", "value": 1.0}],
            "provenance": {"source": "synthetic regression fixture"},
        }
    )
    doc = libsbml.readSBMLFromString(to_sbml_xml(model))
    assert doc.getModel() is not None
    definition = doc.getModel().getUnitDefinition("item_per_litre")
    assert definition is not None
    kinds = {definition.getUnit(i).getKind() for i in range(definition.getNumUnits())}
    assert libsbml.UNIT_KIND_ITEM in kinds
    assert libsbml.UNIT_KIND_MOLE not in kinds
