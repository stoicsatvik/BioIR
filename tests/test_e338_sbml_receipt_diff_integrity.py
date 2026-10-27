"""E338: synthetic SBML sidecar completeness counterexamples, no wet-lab content."""
from copy import deepcopy
from hashlib import sha256
from xml.etree import ElementTree as ET

from research.e303_sbml_assumption_sidecar import (
    SBML, complete_with_explicit_profile, verify_receipt,
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


def _retarget_digest(receipt, xml):
    forged = deepcopy(receipt)
    forged["completed_core_sha256"] = sha256(xml.encode("utf-8")).hexdigest()
    return forged


def test_legitimate_declared_changes_still_verify():
    baseline = _baseline()
    for value in [0.1, 0.2]:
        completed, receipt = complete_with_explicit_profile(
            baseline, k1=value, origin="hypothetical_user_choice"
        )
        assert verify_receipt(baseline, completed, receipt)


def test_unreported_core_edits_rejected_even_with_matching_forged_digest():
    baseline = _baseline()
    completed, receipt = complete_with_explicit_profile(
        baseline, k1=0.1, origin="hypothetical_user_choice"
    )
    cases = [
        ("species", "initialConcentration", "0.25"),
        ("compartment", "size", "2"),
        ("reaction", "reversible", "true"),
        ("model", "id", "different_toy"),
    ]
    for tag, attribute, replacement in cases:
        root = ET.fromstring(completed)
        node = next(root.iter(f"{{{SBML}}}{tag}"))
        node.set(attribute, replacement)
        tampered = ET.tostring(root, encoding="unicode")
        forged = _retarget_digest(receipt, tampered)
        # The legacy verifier accepted a new self-declared digest, provided
        # k1 and the kinetic law matched the assumption list.
        assert forged["completed_core_sha256"] == sha256(tampered.encode()).hexdigest()
        assert forged["introduced_assumptions"] == receipt["introduced_assumptions"]
        assert not verify_receipt(baseline, tampered, forged), (tag, attribute)


def test_unreported_extra_parameter_rejected_with_matching_digest():
    baseline = _baseline()
    completed, receipt = complete_with_explicit_profile(
        baseline, k1=0.1, origin="hypothetical_profile_choice"
    )
    root = ET.fromstring(completed)
    parameters = next(root.iter(f"{{{SBML}}}listOfParameters"))
    ET.SubElement(parameters, f"{{{SBML}}}parameter", {
        "id": "unreported", "value": "9", "constant": "true"
    })
    tampered = ET.tostring(root, encoding="unicode")
    assert not verify_receipt(baseline, tampered, _retarget_digest(receipt, tampered))


def test_origin_authenticity_remains_unproven():
    baseline = _baseline()
    completed, receipt = complete_with_explicit_profile(
        baseline, k1=0.1, origin="hypothetical_user_choice"
    )
    forged = deepcopy(receipt)
    for assumption in forged["introduced_assumptions"]:
        assumption["origin"] = "hypothetical_profile_choice"
    assert verify_receipt(baseline, completed, forged)
