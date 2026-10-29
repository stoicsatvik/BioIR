"""E401: semantic identifier negative control for a content-only SBML receipt.

Safe synthetic mathematical model. No biological validity, wet lab or clinical use.
This test deliberately preserves the negative result: content-consistent receipts
can contain an undefined MathML identifier; the receipt is not a semantic oracle.
"""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
from xml.etree import ElementTree as ET

import pytest

from bioir.sbml_backend import to_sbml_xml
from bioir.semantic_model import SemanticModel
from research.e303_sbml_assumption_sidecar import (
    MATH, SBML, complete_with_explicit_profile, strip_annotations, verify_receipt,
)

ROOT = Path(__file__).resolve().parents[1]


def _frozen_pair():
    model = SemanticModel.from_dict(json.loads(
        (ROOT / "examples/underspecified_conversion.json").read_text()
    ))
    baseline = strip_annotations(to_sbml_xml(model))
    completed, receipt = complete_with_explicit_profile(
        baseline, k1=0.1, origin="hypothetical_user_choice"
    )
    assert verify_receipt(baseline, completed, receipt)
    return baseline, completed, receipt


def _forge_undefined_symbol(completed, receipt):
    root = ET.fromstring(completed)
    law = next(root.iter(f"{{{SBML}}}kineticLaw"))
    math = law[0]
    identifiers = [node for node in math.iter(f"{{{MATH}}}ci")]
    assert [node.text for node in identifiers] == ["k1", "A", "cell"]
    identifiers[1].text = "e401_undefined_symbol"
    forged_xml = ET.tostring(root, encoding="unicode")
    forged_receipt = deepcopy(receipt)
    forged_receipt["completed_core_sha256"] = sha256(
        forged_xml.encode("utf-8")
    ).hexdigest()
    forged_receipt["introduced_assumptions"][1]["mathml"] = ET.tostring(
        math, encoding="unicode"
    )
    return forged_xml, forged_receipt


def test_content_receipt_accepts_rehashed_undefined_math_identifier():
    baseline, completed, receipt = _frozen_pair()
    forged_xml, forged_receipt = _forge_undefined_symbol(completed, receipt)
    assert "e401_undefined_symbol" in forged_xml
    assert verify_receipt(baseline, forged_xml, forged_receipt), (
        "Preserve negative control: receipt validates declared content, "
        "not whether a declared kinetic law resolves its MathML symbols."
    )


def test_independent_libsbml_flags_undefined_math_identifier():
    libsbml = pytest.importorskip("libsbml")
    _, completed, receipt = _frozen_pair()
    forged_xml, _ = _forge_undefined_symbol(completed, receipt)

    def errors(xml):
        doc = libsbml.readSBMLFromString(xml)
        assert doc.getModel() is not None
        doc.checkConsistency()
        return [(doc.getError(i).getErrorId(), doc.getError(i).getMessage())
                for i in range(doc.getNumErrors())
                if doc.getError(i).getSeverity() >= libsbml.LIBSBML_SEV_ERROR]

    original = errors(completed)
    forged = errors(forged_xml)
    assert any("e401_undefined_symbol" in message for _, message in forged), (
        "Independent libSBML did not flag the undefined MathML symbol: "
        f"baseline={original!r}, forged={forged!r}"
    )
