"""E303: independent explicit-assumption receipt in SBML Core plus sidecar.

Synthetic mathematical examples only. No biological measurements, experiments,
clinical claims, or autonomous biological actuation. The test evaluates
representability and content integrity, NOT provenance authenticity.
"""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
from math import isfinite
from pathlib import Path
from xml.etree import ElementTree as ET

SBML = "http://www.sbml.org/sbml/level3/version2/core"
MATH = "http://www.w3.org/1998/Math/MathML"
ET.register_namespace("", SBML)
ET.register_namespace("math", MATH)
ROOT = Path(__file__).resolve().parents[1]


def _digest(xml: str) -> str:
    return sha256(xml.encode("utf-8")).hexdigest()


def _render(root: ET.Element) -> str:
    return ET.tostring(root, encoding="unicode")


def strip_annotations(xml: str) -> str:
    root = ET.fromstring(xml)
    for parent in root.iter():
        for child in list(parent):
            if child.tag == f"{{{SBML}}}annotation":
                parent.remove(child)
    return _render(root)


def missing_commitments(xml: str) -> list[str]:
    root = ET.fromstring(xml)
    model = root.find(f"{{{SBML}}}model")
    if model is None:
        raise ValueError("no SBML model")
    keys = []
    for p in model.findall(f".//{{{SBML}}}listOfParameters/{{{SBML}}}parameter"):
        if "value" not in p.attrib:
            keys.append(f"parameter_value:{p.attrib['id']}")
    for r in model.findall(f".//{{{SBML}}}listOfReactions/{{{SBML}}}reaction"):
        if r.find(f"{{{SBML}}}kineticLaw") is None:
            keys.append(f"kinetic_law:{r.attrib['id']}")
    return sorted(keys)


def _find_single(root: ET.Element, kind: str, identifier: str) -> ET.Element:
    matches = [e for e in root.iter(f"{{{SBML}}}{kind}") if e.get("id") == identifier]
    if len(matches) != 1:
        raise ValueError(f"expected exactly one {kind}:{identifier}")
    return matches[0]


def _mathml() -> ET.Element:
    math = ET.Element(f"{{{MATH}}}math")
    apply = ET.SubElement(math, f"{{{MATH}}}apply")
    ET.SubElement(apply, f"{{{MATH}}}times")
    for symbol in ("k1", "A", "cell"):
        ET.SubElement(apply, f"{{{MATH}}}ci").text = symbol
    return math


def complete_with_explicit_profile(
    baseline_xml: str, *, k1: float, origin: str
) -> tuple[str, dict]:
    """An independently specified hypothetical profile, not a BioIR compiler."""
    if not isfinite(k1) or k1 <= 0:
        raise ValueError("hypothetical k1 must be positive and finite")
    if origin not in {"hypothetical_user_choice", "hypothetical_profile_choice"}:
        raise ValueError("only explicitly hypothetical origins are allowed")
    if missing_commitments(baseline_xml) != [
        "kinetic_law:A_to_B", "parameter_value:k1"
    ]:
        raise ValueError("unexpected source commitments; fail closed")
    root = ET.fromstring(baseline_xml)
    _find_single(root, "parameter", "k1").set("value", format(k1, ".17g"))
    kinetic = ET.SubElement(
        _find_single(root, "reaction", "A_to_B"), f"{{{SBML}}}kineticLaw"
    )
    kinetic.append(_mathml())
    completed = _render(root)
    if missing_commitments(completed):
        raise AssertionError("completion failed")
    receipt = {
        "schema": "e303-explicit-sbml-sidecar-v1",
        "baseline_core_sha256": _digest(baseline_xml),
        "completed_core_sha256": _digest(completed),
        "introduced_assumptions": [
            {"key": "parameter_value:k1", "value": format(k1, ".17g"), "origin": origin},
            {"key": "kinetic_law:A_to_B", "mathml": _render(_mathml()), "origin": origin},
        ],
        "unresolved_commitments": [],
        "origin_independently_verified": False,
    }
    if not verify_receipt(baseline_xml, completed, receipt):
        raise AssertionError("sidecar content verification failed")
    return completed, receipt


def _canonical_layout_xml(xml: str) -> str:
    """Ignore XML indentation in element-only SBML/MathML structures.

    Do not strip non-whitespace text, MathML identifier contents, or
    notes/annotation mixed content. This is a deliberately narrow layout
    normalization, not an assertion of general SBML semantic equivalence.
    """
    root = ET.fromstring(xml)
    for parent in root.iter():
        sbml_structure = (
            parent.tag.startswith(f"{{{SBML}}}")
            and parent.tag not in {f"{{{SBML}}}notes", f"{{{SBML}}}annotation"}
        )
        math_structure = parent.tag in {f"{{{MATH}}}math", f"{{{MATH}}}apply"}
        if sbml_structure or math_structure:
            if parent.text is not None and not parent.text.strip():
                parent.text = None
            for child in parent:
                if child.tail is not None and not child.tail.strip():
                    child.tail = None
    return ET.canonicalize(_render(root))


def _only_declared_assumptions_changed(baseline_xml: str, completed_xml: str) -> bool:
    """Prove the completed Core differs only at the two declared commitments.

    A matching digest alone is insufficient: an author can hash an altered
    species, compartment or reaction and leave the sidecar's assumption list
    unchanged. Revert exactly the declared edits, then compare canonical XML.
    """
    baseline = ET.fromstring(baseline_xml)
    completed = ET.fromstring(completed_xml)
    source_parameter = _find_single(baseline, "parameter", "k1")
    source_reaction = _find_single(baseline, "reaction", "A_to_B")
    if "value" in source_parameter.attrib:
        return False
    if source_reaction.find(f"{{{SBML}}}kineticLaw") is not None:
        return False

    parameter = _find_single(completed, "parameter", "k1")
    reaction = _find_single(completed, "reaction", "A_to_B")
    law = reaction.find(f"{{{SBML}}}kineticLaw")
    if law is None:
        return False
    parameter.attrib.pop("value", None)
    reaction.remove(law)
    return _canonical_layout_xml(_render(completed)) == _canonical_layout_xml(_render(baseline))


def verify_receipt(baseline_xml: str, completed_xml: str, receipt: dict) -> bool:
    """Verify claimed SBML content; cannot verify who supplied an assumption."""
    try:
        if receipt["schema"] != "e303-explicit-sbml-sidecar-v1":
            return False
        if receipt["baseline_core_sha256"] != _digest(baseline_xml):
            return False
        if receipt["completed_core_sha256"] != _digest(completed_xml):
            return False
        if receipt["unresolved_commitments"] or receipt["origin_independently_verified"] is not False:
            return False
        if missing_commitments(completed_xml):
            return False
        assumptions = receipt["introduced_assumptions"]
        if [a["key"] for a in assumptions] != ["parameter_value:k1", "kinetic_law:A_to_B"]:
            return False
        root = ET.fromstring(completed_xml)
        parameter = _find_single(root, "parameter", "k1")
        reaction = _find_single(root, "reaction", "A_to_B")
        law = reaction.find(f"{{{SBML}}}kineticLaw")
        if law is None or len(law) != 1:
            return False
        if not _only_declared_assumptions_changed(baseline_xml, completed_xml):
            return False
        return (
            parameter.get("value") == assumptions[0]["value"]
            and _canonical_layout_xml(_render(law[0])) == _canonical_layout_xml(assumptions[1]["mathml"])
            and all(a["origin"] in {
                "hypothetical_user_choice", "hypothetical_profile_choice"
            } for a in assumptions)
        )
    except (ValueError, KeyError, TypeError, IndexError, ET.ParseError):
        return False


def evaluate(baseline_xml: str) -> dict:
    """Two independent profiles, three tamper controls, one spoofed-origin null."""
    profiles = [(0.1, "hypothetical_user_choice"), (0.2, "hypothetical_profile_choice")]
    outputs = [
        complete_with_explicit_profile(baseline_xml, k1=k, origin=o)
        for k, o in profiles
    ]
    matches = [verify_receipt(baseline_xml, core, receipt) for core, receipt in outputs]
    first_core, first_receipt = outputs[0]
    second_core, second_receipt = outputs[1]
    swapped_rejected = not verify_receipt(baseline_xml, first_core, second_receipt)
    altered = ET.fromstring(first_core)
    _find_single(altered, "parameter", "k1").set("value", "0.9")
    parameter_tamper_rejected = not verify_receipt(baseline_xml, _render(altered), first_receipt)
    altered_law = ET.fromstring(first_core)
    law = _find_single(altered_law, "reaction", "A_to_B").find(f"{{{SBML}}}kineticLaw")
    assert law is not None
    law[0].find(f".//{{{MATH}}}ci").text = "B"
    law_tamper_rejected = not verify_receipt(baseline_xml, _render(altered_law), first_receipt)
    forged_origin = deepcopy(first_receipt)
    for assumption in forged_origin["introduced_assumptions"]:
        assumption["origin"] = "hypothetical_profile_choice"
    origin_spoof_accepted = verify_receipt(baseline_xml, first_core, forged_origin)
    return {
        "schema": "bioir-e303-sbml-assumption-representability-v1",
        "synthetic_only": True,
        "baseline_missing_keys": missing_commitments(baseline_xml),
        "completed_profiles_verified": sum(matches),
        "profile_count": len(outputs),
        "distinct_completed_core": first_core != second_core,
        "swapped_sidecar_rejected": swapped_rejected,
        "parameter_tamper_rejected": parameter_tamper_rejected,
        "kinetic_law_tamper_rejected": law_tamper_rejected,
        "origin_spoof_accepted": origin_spoof_accepted,
        "conclusion": (
            "SBML Core plus an independently specified hypothetical assumption "
            "sidecar represents and checks these receipts. Origin authenticity NOT proven."
        ),
    }


def run() -> dict:
    from bioir.completion import plan_executable_completion
    from bioir.semantic_model import SemanticModel
    from bioir.sbml_backend import to_sbml_xml

    model = SemanticModel.from_dict(json.loads(
        (ROOT / "examples/underspecified_conversion.json").read_text()
    ))
    baseline = strip_annotations(to_sbml_xml(model))
    result = evaluate(baseline)
    expected = sorted(x.key for x in plan_executable_completion(model).unresolved_commitments)
    if result["baseline_missing_keys"] != expected:
        raise AssertionError("independent SBML keys disagree with BioIR")
    try:
        import libsbml
    except ImportError:
        result["libsbml_reparse"] = "NOT RUN (dependency unavailable)"
    else:
        for k, origin in [
            (0.1, "hypothetical_user_choice"),
            (0.2, "hypothetical_profile_choice"),
        ]:
            completed, _ = complete_with_explicit_profile(baseline, k1=k, origin=origin)
            parsed = libsbml.readSBMLFromString(completed)
            if (
                parsed.getModel() is None
                or parsed.getModel().getReaction("A_to_B").getKineticLaw() is None
            ):
                raise AssertionError("libSBML failed to reparse hypothetical completion")
        result["libsbml_reparse"] = "2/2"
    if not (
        result["completed_profiles_verified"] == 2
        and result["distinct_completed_core"]
        and result["swapped_sidecar_rejected"]
        and result["parameter_tamper_rejected"]
        and result["kinetic_law_tamper_rejected"]
        and result["origin_spoof_accepted"]
    ):
        raise AssertionError("predeclared E303 checks failed")
    return result


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True, indent=2))
