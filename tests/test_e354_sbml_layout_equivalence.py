"""E354: distinguish harmless SBML layout from undeclared semantic edits.

All models are synthetic structural examples; no biological or clinical claims.
"""
from copy import deepcopy
from hashlib import sha256
from xml.etree import ElementTree as ET

from research.e303_sbml_assumption_sidecar import (
    MATH, SBML, complete_with_explicit_profile, verify_receipt,
)


def _baseline():
    return (
        f'<sbml xmlns="{SBML}" level="3" version="2"><model id="toy">'
        '<listOfCompartments><compartment id="cell" size="1" constant="true"/></listOfCompartments>'
        '<listOfSpecies><species id="A" compartment="cell" initialConcentration="1" '
        'hasOnlySubstanceUnits="false" boundaryCondition="false" constant="false"/></listOfSpecies>'
        '<listOfParameters><parameter id="k1" constant="true"/></listOfParameters>'
        '<listOfReactions><reaction id="A_to_B" reversible="false"/></listOfReactions>'
        '</model></sbml>'
    )


def _indented(xml):
    root = ET.fromstring(xml)
    ET.indent(root, space="  ")
    return ET.tostring(root, encoding="unicode")


def _rehashed(receipt, completed):
    updated = deepcopy(receipt)
    updated["completed_core_sha256"] = sha256(completed.encode("utf-8")).hexdigest()
    return updated


def test_indentation_only_roundtrip_keeps_declared_receipt_valid():
    baseline = _baseline()
    completed, receipt = complete_with_explicit_profile(
        baseline, k1=0.1, origin="hypothetical_user_choice"
    )
    pretty = _indented(completed)
    assert pretty != completed
    assert verify_receipt(baseline, pretty, _rehashed(receipt, pretty))


def test_indented_undeclared_species_change_still_rejected():
    baseline = _baseline()
    completed, receipt = complete_with_explicit_profile(
        baseline, k1=0.1, origin="hypothetical_user_choice"
    )
    root = ET.fromstring(completed)
    next(root.iter(f"{{{SBML}}}species")).set("initialConcentration", "9")
    ET.indent(root)
    changed = ET.tostring(root, encoding="unicode")
    assert not verify_receipt(baseline, changed, _rehashed(receipt, changed))


def test_indented_mathml_identifier_change_still_rejected():
    baseline = _baseline()
    completed, receipt = complete_with_explicit_profile(
        baseline, k1=0.1, origin="hypothetical_user_choice"
    )
    root = ET.fromstring(completed)
    next(root.iter(f"{{{MATH}}}ci")).text = "B"
    ET.indent(root)
    changed = ET.tostring(root, encoding="unicode")
    assert not verify_receipt(baseline, changed, _rehashed(receipt, changed))
