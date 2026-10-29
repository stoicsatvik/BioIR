"""E379: independent libSBML serializer stress of synthetic SBML sidecar receipts.

No biological measurements, parameter estimation, sequence design, clinical
inference or wet-lab operations. Tests XML content integrity and whether a
standards serializer preserves the E303/E354 declared-assumption receipt.
"""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
from xml.etree import ElementTree as ET

from research.e303_sbml_assumption_sidecar import (
    SBML, complete_with_explicit_profile, missing_commitments,
    strip_annotations, verify_receipt,
)

ROOT = Path(__file__).resolve().parents[1]


def _hash(xml: str) -> str:
    return sha256(xml.encode("utf-8")).hexdigest()


def _rehashed(receipt: dict, baseline: str, completed: str) -> dict:
    copy = deepcopy(receipt)
    copy["baseline_core_sha256"] = _hash(baseline)
    copy["completed_core_sha256"] = _hash(completed)
    return copy


def run() -> dict:
    import libsbml

    from bioir.sbml_backend import to_sbml_xml
    from bioir.semantic_model import SemanticModel

    model = SemanticModel.from_dict(json.loads(
        (ROOT / "examples/underspecified_conversion.json").read_text()
    ))
    baseline = strip_annotations(to_sbml_xml(model))
    if missing_commitments(baseline) != ["kinetic_law:A_to_B", "parameter_value:k1"]:
        raise AssertionError("source commitments drifted")

    def roundtrip(xml: str) -> str:
        document = libsbml.readSBMLFromString(xml)
        if document.getModel() is None:
            raise AssertionError("libSBML cannot parse source SBML")
        result = libsbml.writeSBMLToString(document)
        if not result or libsbml.readSBMLFromString(result).getModel() is None:
            raise AssertionError("libSBML output cannot be reparsed")
        return result

    baseline_roundtrip = roundtrip(baseline)
    rows = []
    for k1, origin in (
        (0.1, "hypothetical_user_choice"),
        (0.2, "hypothetical_profile_choice"),
    ):
        completed, receipt = complete_with_explicit_profile(
            baseline, k1=k1, origin=origin
        )
        if not verify_receipt(baseline, completed, receipt):
            raise AssertionError("original receipt unexpectedly invalid")
        completed_roundtrip = roundtrip(completed)
        completed_only = verify_receipt(
            baseline, completed_roundtrip,
            _rehashed(receipt, baseline, completed_roundtrip),
        )
        both_roundtrip = verify_receipt(
            baseline_roundtrip, completed_roundtrip,
            _rehashed(receipt, baseline_roundtrip, completed_roundtrip),
        )
        altered = ET.fromstring(completed_roundtrip)
        species = next(altered.iter(f"{{{SBML}}}species"))
        species.set("initialConcentration", "0.5")
        changed = ET.tostring(altered, encoding="unicode")
        tamper_rejected = not verify_receipt(
            baseline_roundtrip, changed,
            _rehashed(receipt, baseline_roundtrip, changed),
        )
        rows.append({
            "k1": k1,
            "libsbml_completed_reparsed": True,
            "baseline_xml_changed": baseline_roundtrip != baseline,
            "completed_xml_changed": completed_roundtrip != completed,
            "completed_only_receipt_accepted": completed_only,
            "both_reserialized_receipt_accepted": both_roundtrip,
            "undeclared_species_change_rejected": tamper_rejected,
            "baseline_roundtrip_sha256": _hash(baseline_roundtrip),
            "completed_roundtrip_sha256": _hash(completed_roundtrip),
        })
    return {
        "schema": "bioir/e379/independent-libsbml-serializer/v1",
        "profiles": len(rows),
        "rows": rows,
        "libsbml_version": libsbml.getLibSBMLDottedVersion(),
        "synthetic_only": True,
        "claim": "independent serializer receipt compatibility measured; biological validity NOT YET PROVEN",
        "limitations": [
            "Two synthetic completion profiles, not biological kinetic measurements.",
            "libSBML read/write is not an independent biological semantics oracle.",
            "Rehashing receipt proves only content consistency, never assumption-origin authenticity.",
            "Serializer acceptance does not prove universal SBML/Antimony equivalence.",
        ],
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True, allow_nan=False))
