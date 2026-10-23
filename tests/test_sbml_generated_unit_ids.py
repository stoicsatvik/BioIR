"""Synthetic SBML namespace collision regression; no biological execution."""
from xml.etree import ElementTree as ET

from bioir.semantic_model import SemanticModel
from bioir.sbml_backend import SBML_NS, to_sbml_xml


def test_generated_unit_ids_do_not_alias_species_or_parameters():
    model = SemanticModel.from_dict(
        {
            "name": "synthetic_collision",
            "compartments": [{"id": "cell", "size": 1.0, "unit": "litre"}],
            "entities": [
                {"id": "item_per_litre", "compartment": "cell",
                 "initial_value": 1.0, "quantity_kind": "amount", "unit": "item"},
                {"id": "bioir_unit_item_per_litre", "compartment": "cell",
                 "initial_value": 2.0, "quantity_kind": "amount", "unit": "item"},
            ],
            "parameters": [
                {"id": "p", "unit": "item_per_litre", "value": 1.0},
                {"id": "mole_per_litre", "unit": "mole_per_litre", "value": 2.0},
            ],
            "provenance": {"source": "synthetic regression fixture"},
        }
    )
    xml = to_sbml_xml(model)
    root = ET.fromstring(xml)
    ns = {"s": SBML_NS}
    ids = [element.attrib["id"] for element in root.iter() if "id" in element.attrib]
    assert len(ids) == len(set(ids)), "SBML model-wide identifiers must not collide"

    definitions = {
        element.attrib["id"]: element
        for element in root.findall(".//s:unitDefinition", ns)
    }
    parameters = {
        element.attrib["id"]: element
        for element in root.findall(".//s:parameter", ns)
    }
    item_unit_id = parameters["p"].attrib["units"]
    mole_unit_id = parameters["mole_per_litre"].attrib["units"]
    assert item_unit_id == "bioir_unit_item_per_litre_2"
    assert mole_unit_id == "bioir_unit_mole_per_litre"
    assert definitions[item_unit_id].find("s:listOfUnits/s:unit", ns).attrib["kind"] == "item"
    assert definitions[mole_unit_id].find("s:listOfUnits/s:unit", ns).attrib["kind"] == "mole"
    assert to_sbml_xml(model) == xml


def test_noncolliding_unit_ids_keep_existing_contract():
    model = SemanticModel.from_dict(
        {
            "name": "synthetic_no_collision",
            "compartments": [{"id": "cell", "size": 1.0, "unit": "litre"}],
            "entities": [{"id": "A", "compartment": "cell",
                          "initial_value": 1.0, "quantity_kind": "amount", "unit": "item"}],
            "parameters": [{"id": "p", "unit": "item_per_litre", "value": 1.0}],
            "provenance": {"source": "synthetic regression fixture"},
        }
    )
    root = ET.fromstring(to_sbml_xml(model))
    ns = {"s": SBML_NS}
    assert root.find(".//s:unitDefinition[@id='item_per_litre']", ns) is not None
    assert root.find(".//s:parameter[@id='p']", ns).attrib["units"] == "item_per_litre"
