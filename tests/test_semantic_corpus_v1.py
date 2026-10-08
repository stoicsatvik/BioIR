"""Frozen synthetic BioIR v1 structural/partial-model regression cases.

This corpus does not establish biological validity or Antimony equivalence.
"""
from xml.etree import ElementTree as ET

import pytest

from bioir.completion import plan_executable_completion
from bioir.semantic_checks import SemanticValidationError, check_semantic_model
from bioir.semantic_model import SemanticModel
from bioir.sbml_backend import SBML_NS, to_sbml_xml


def base():
    return {
        "name": "toy",
        "compartments": [{"id": "cell", "size": 1, "unit": "litre"}],
        "entities": [
            {"id": "A", "compartment": "cell", "initial_value": 1,
             "quantity_kind": "concentration", "unit": "mole_per_litre"},
            {"id": "B", "compartment": "cell", "initial_value": 0,
             "quantity_kind": "concentration", "unit": "mole_per_litre"},
        ],
        "parameters": [{"id": "k", "value": 0.1, "unit": "per_second"}],
        "interactions": [{
            "id": "convert", "kind": "conversion",
            "inputs": [{"entity": "A"}], "outputs": [{"entity": "B"}],
            "parameter_refs": ["k"],
        }],
        "provenance": {"source": "synthetic regression fixture"},
    }


CASES = [
    ("complete", (), None, (), ("kinetic_law:convert",)),
    ("unresolved", ("parameters", 0, "value"), None, (),
     ("parameter_value:k", "kinetic_law:convert")),
    ("missing_species", ("interactions", 0, "outputs", 0, "entity"),
     "ghost", ("interaction.unknown_entity",), ()),
    ("wrong_units", ("entities", 0, "unit"),
     "second", ("unit.quantity_mismatch",), ()),
    ("missing_parameter", ("interactions", 0, "parameter_refs", 0),
     "ghost", ("interaction.unknown_parameter",), ()),
    ("duplicate_symbol", ("entities", 1, "id"),
     "A", ("id.duplicate", "interaction.unknown_entity"), ()),
    ("invalid_stoichiometry", ("interactions", 0, "inputs", 0, "stoichiometry"),
     -1, ("interaction.stoichiometry",), ()),
    ("zero_volume", ("compartments", 0, "size"),
     0, ("compartment.size",), ()),
]


@pytest.mark.parametrize(
    "case,path,value,errors,unresolved", CASES, ids=[row[0] for row in CASES]
)
def test_frozen_corpus(case, path, value, errors, unresolved):
    payload = base()
    if path:
        obj = payload
        for key in path[:-1]:
            obj = obj[key]
        obj[path[-1]] = value
    model = SemanticModel.from_dict(payload)
    report = check_semantic_model(model)
    assert tuple(sorted(issue.code for issue in report.errors)) == tuple(sorted(errors))
    if errors:
        with pytest.raises(SemanticValidationError):
            to_sbml_xml(model)
        return
    receipt = plan_executable_completion(model)
    assert receipt.introduced_assumptions == ()
    assert {x.key for x in receipt.unresolved_commitments} == set(unresolved)
    xml = to_sbml_xml(model)
    root = ET.fromstring(xml)
    ns = {"s": SBML_NS}
    assert root.find(".//s:kineticLaw", ns) is None
    param = root.find(".//s:parameter[@id='k']", ns)
    assert ("value" in param.attrib) is (case == "complete")
    assert to_sbml_xml(model) == xml
