"""E380: frozen synthetic negative controls for the verifier gate diagnostic."""
from copy import deepcopy
from xml.etree import ElementTree as ET

from bioir.sbml_backend import to_sbml_xml
from bioir.semantic_model import SemanticModel
from research.e303_sbml_assumption_sidecar import (
    SBML, complete_with_explicit_profile, strip_annotations,
)
from research.e379_libsbml_serializer import ROOT, _rehashed
from research.e380_libsbml_verifier_gates import gates, structural_changes
import json


def _fixture():
    model = SemanticModel.from_dict(json.loads(
        (ROOT / "examples/underspecified_conversion.json").read_text()
    ))
    baseline = strip_annotations(to_sbml_xml(model))
    completed, receipt = complete_with_explicit_profile(
        baseline, k1=0.1, origin="hypothetical_user_choice"
    )
    return baseline, completed, receipt


def test_original_declared_completion_passes_every_gate():
    baseline, completed, receipt = _fixture()
    assert all(gates(baseline, completed, receipt).values())
    assert structural_changes(completed, completed) == []


def test_rehashed_undeclared_species_change_fails_declared_only_gate():
    baseline, completed, receipt = _fixture()
    root = ET.fromstring(completed)
    next(root.iter(f"{{{SBML}}}species")).set("initialConcentration", "0.5")
    mutated = ET.tostring(root, encoding="unicode")
    checks = gates(baseline, mutated, _rehashed(receipt, baseline, mutated))
    assert checks["baseline_hash"] and checks["completed_hash"]
    assert checks["only_declared_edits"] is False
    assert checks["receipt_accepted"] is False
    assert structural_changes(completed, mutated)


def test_rehashed_wrong_parameter_fails_value_gate():
    baseline, completed, receipt = _fixture()
    root = ET.fromstring(completed)
    next(root.iter(f"{{{SBML}}}parameter")).set("value", "0.9")
    mutated = ET.tostring(root, encoding="unicode")
    checks = gates(baseline, mutated, _rehashed(receipt, baseline, mutated))
    assert checks["parameter_value_matches_receipt"] is False
    assert checks["receipt_accepted"] is False
