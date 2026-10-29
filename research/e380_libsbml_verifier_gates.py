"""E380: localize independent libSBML receipt failures without relaxing any guard.

Only two frozen synthetic mathematical SBML profiles; no biological measurements.
This is a diagnostic, not a proof of SBML semantic equivalence.
"""
from __future__ import annotations

from collections import Counter
from hashlib import sha256
import json
from xml.etree import ElementTree as ET

from research.e303_sbml_assumption_sidecar import (
    SBML, _canonical_layout_xml, _find_single,
    _only_declared_assumptions_changed, _render,
    complete_with_explicit_profile, missing_commitments, strip_annotations,
    verify_receipt,
)
from research.e379_libsbml_serializer import ROOT, _rehashed


def _flatten(xml: str) -> dict[str, tuple[tuple[tuple[str, str], ...], str]]:
    """Indexed element paths make serializer changes inspectable without text diffs."""
    result = {}

    def visit(node: ET.Element, path: str) -> None:
        result[path] = (tuple(sorted(node.attrib.items())), (node.text or "").strip())
        seen: Counter[str] = Counter()
        for child in node:
            seen[child.tag] += 1
            visit(child, f"{path}/{child.tag}[{seen[child.tag]}]")

    root = ET.fromstring(xml)
    visit(root, root.tag)
    return result


def structural_changes(before: str, after: str) -> list[dict]:
    a, b = _flatten(before), _flatten(after)
    return [
        {"path": path, "before": a.get(path), "after": b.get(path)}
        for path in sorted(set(a) | set(b))
        if a.get(path) != b.get(path)
    ]


def gates(baseline: str, completed: str, receipt: dict) -> dict[str, bool]:
    root = ET.fromstring(completed)
    parameter = _find_single(root, "parameter", "k1")
    reaction = _find_single(root, "reaction", "A_to_B")
    law = reaction.find(f"{{{SBML}}}kineticLaw")
    assumptions = receipt["introduced_assumptions"]
    return {
        "baseline_hash": sha256(baseline.encode()).hexdigest() == receipt["baseline_core_sha256"],
        "completed_hash": sha256(completed.encode()).hexdigest() == receipt["completed_core_sha256"],
        "completed_has_no_missing_commitments": not missing_commitments(completed),
        "parameter_value_matches_receipt": parameter.get("value") == assumptions[0]["value"],
        "kinetic_law_shape": law is not None and len(law) == 1,
        "mathml_layout_matches_receipt": (
            law is not None and len(law) == 1 and
            _canonical_layout_xml(_render(law[0])) ==
            _canonical_layout_xml(assumptions[1]["mathml"])
        ),
        "only_declared_edits": _only_declared_assumptions_changed(baseline, completed),
        "receipt_accepted": verify_receipt(baseline, completed, receipt),
    }


def run() -> dict:
    import libsbml
    from bioir.sbml_backend import to_sbml_xml
    from bioir.semantic_model import SemanticModel

    model = SemanticModel.from_dict(json.loads(
        (ROOT / "examples/underspecified_conversion.json").read_text()
    ))
    baseline = strip_annotations(to_sbml_xml(model))

    def roundtrip(xml: str) -> str:
        doc = libsbml.readSBMLFromString(xml)
        if doc.getModel() is None:
            raise AssertionError("libSBML failed to parse frozen input")
        output = libsbml.writeSBMLToString(doc)
        if libsbml.readSBMLFromString(output).getModel() is None:
            raise AssertionError("libSBML output did not reparse")
        return output

    baseline_rt = roundtrip(baseline)
    rows = []
    for k1, origin in ((0.1, "hypothetical_user_choice"),
                       (0.2, "hypothetical_profile_choice")):
        completed, receipt = complete_with_explicit_profile(
            baseline, k1=k1, origin=origin
        )
        completed_rt = roundtrip(completed)
        cases = {}
        for label, b, c in (
            ("original", baseline, completed),
            ("completed_only", baseline, completed_rt),
            ("both_roundtripped", baseline_rt, completed_rt),
        ):
            cases[label] = gates(b, c, _rehashed(receipt, b, c))
        rows.append({
            "k1": k1,
            "gates": cases,
            "baseline_structural_changes": structural_changes(baseline, baseline_rt)[:30],
            "completed_structural_changes": structural_changes(completed, completed_rt)[:30],
            "baseline_change_count": len(structural_changes(baseline, baseline_rt)),
            "completed_change_count": len(structural_changes(completed, completed_rt)),
        })
    return {
        "experiment": "E380_LIBSBML_VERIFIER_GATE_ISOLATION",
        "libsbml_version": libsbml.getLibSBMLDottedVersion(),
        "synthetic_only": True,
        "rows": rows,
        "limits": [
            "XML structural differences do not establish semantic equivalence.",
            "Hashes are correctly recomputed for each candidate; origin is not authenticated.",
            "No verifier gate was relaxed; no wet-lab or biological claims.",
        ],
    }


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True, indent=2, allow_nan=False))
