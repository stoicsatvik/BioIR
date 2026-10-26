"""E284: can SBML Core plus a small sidecar represent BioIR's CURRENT receipt?

Safe synthetic structural-model experiment. No kinetics are introduced, and no
real biological measurements, wet-lab actions or treatment decisions occur.
The sidecar is intentionally constructed from the BioIR source model; this is
a representability control, NOT independent scientific validation.
"""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path

from bioir.completion import model_fingerprint, plan_executable_completion
from bioir.semantic_model import SemanticModel
from bioir.sbml_backend import to_sbml_xml
from research.e267_sbml_core_receipts import core_keys, corpus

ROOT = Path(__file__).resolve().parents[1]
TARGET = "antimony-or-sbml-executable"


def annotation_free_core(model: SemanticModel) -> tuple[object, str]:
    import libsbml

    document = libsbml.readSBMLFromString(to_sbml_xml(model))
    if document.getModel() is None:
        raise AssertionError("SBML parse failed")
    sbml_model = document.getModel()
    sbml_model.unsetAnnotation()
    for reaction in sbml_model.getListOfReactions():
        reaction.unsetAnnotation()
    stripped = libsbml.writeSBMLToString(document)
    reparsed = libsbml.readSBMLFromString(stripped)
    if reparsed.getModel() is None:
        raise AssertionError("annotation-free SBML reparse failed")
    return reparsed.getModel(), stripped


def minimal_sidecar(model: SemanticModel, stripped_xml: str) -> dict:
    """Only non-Core intent/provenance, a source fingerprint and pairing hash."""
    return {
        "version": model.version,
        "source_model_fingerprint": model_fingerprint(model),
        "sbml_core_sha256": sha256(stripped_xml.encode("utf-8")).hexdigest(),
        "provenance": {
            "source": model.provenance.source,
            "citation": model.provenance.citation,
            "notes": model.provenance.notes,
        },
        "interaction_intent": {
            x.id: {"kind": x.kind.value, "parameter_refs": list(x.parameter_refs)}
            for x in model.interactions
        },
    }


def reconstruct_current_receipt(sbml_model, sidecar: dict) -> dict:
    """Reconstruct current *unresolved* fields from Core presence bits.

    Reasons are deterministic presentation strings, not a scientific claim.
    The source fingerprint is carried by the sidecar, not inferred from Core.
    No completion profiles or introduced assumptions exist in the current IR.
    """
    commitments = []
    for key in sorted(core_keys(sbml_model)):
        category, identifier = key.split(":", 1)
        if category == "parameter_value":
            path = f"parameters.{identifier}.value"
            reason = (
                f"parameter {identifier!r} has units/identity but no "
                "numerical value"
            )
        elif category == "kinetic_law":
            path = f"interactions.{identifier}"
            reason = (
                f"interaction {identifier!r} defines biological topology "
                "but intentionally does not choose a mathematical rate law"
            )
        else:
            raise AssertionError(f"unexpected category: {category}")
        commitments.append({
            "key": key, "category": category, "path": path,
            "reason": reason, "required_for": TARGET,
        })
    return {
        "model_name": sbml_model.getId(),
        "model_version": sidecar["version"],
        "model_fingerprint": sidecar["source_model_fingerprint"],
        "target": TARGET,
        "mathematically_complete": not commitments,
        "introduced_assumptions": [],
        "unresolved_commitments": commitments,
    }


def current_receipt_projection(receipt: dict) -> dict:
    """Exclude the nonsemantic explanatory policy string."""
    return {k: v for k, v in receipt.items() if k != "policy"}


def variants() -> list[tuple[str, dict, bool]]:
    """True means the annotation-free Core should be unchanged."""
    original = json.loads(
        (ROOT / "examples/underspecified_conversion.json").read_text()
    )
    rows = []
    for label in (
        "provenance_notes", "provenance_source", "interaction_kind",
        "parameter_refs", "reaction_name_control", "parameter_value_control",
    ):
        changed = deepcopy(original)
        if label == "provenance_notes":
            changed["provenance"]["notes"] = "independent synthetic note"
        elif label == "provenance_source":
            changed["provenance"]["source"] = "different synthetic source"
        elif label == "interaction_kind":
            changed["interactions"][0]["kind"] = "generic"
        elif label == "parameter_refs":
            changed["interactions"][0]["parameter_refs"] = []
        elif label == "reaction_name_control":
            changed["interactions"][0]["name"] = "synthetic alternative"
        elif label == "parameter_value_control":
            changed["parameters"][0]["value"] = 0.5
        rows.append((label, changed, not label.endswith("_control")))
    return rows


def run() -> dict:
    import libsbml  # noqa: F401

    receipt_matches = []
    for label, payload in corpus():
        model = SemanticModel.from_dict(payload)
        core, xml = annotation_free_core(model)
        sidecar = minimal_sidecar(model, xml)
        recovered = reconstruct_current_receipt(core, sidecar)
        expected = current_receipt_projection(
            plan_executable_completion(model).to_dict()
        )
        if recovered != expected:
            raise AssertionError(f"{label}: receipt projection mismatch")
        if set(sidecar) != {
            "version", "source_model_fingerprint", "sbml_core_sha256",
            "provenance", "interaction_intent",
        }:
            raise AssertionError("sidecar unexpectedly stores full model")
        receipt_matches.append(label)

    base = json.loads(
        (ROOT / "examples/underspecified_conversion.json").read_text()
    )
    original = SemanticModel.from_dict(base)
    base_core, base_xml = annotation_free_core(original)
    base_sidecar = minimal_sidecar(original, base_xml)
    pairs = []
    for label, payload, expected_same_core in variants():
        model = SemanticModel.from_dict(payload)
        core, xml = annotation_free_core(model)
        same_core = xml == base_xml
        sidecar = minimal_sidecar(model, xml)
        same_sidecar = sidecar == base_sidecar
        if same_core != expected_same_core:
            raise AssertionError(f"{label}: unexpected Core equivalence")
        if same_sidecar:
            raise AssertionError(f"{label}: sidecar lost semantic difference")
        recovered = reconstruct_current_receipt(core, sidecar)
        expected = current_receipt_projection(
            plan_executable_completion(model).to_dict()
        )
        if recovered != expected:
            raise AssertionError(f"{label}: receipt reconstruction failed")
        pairs.append({
            "variant": label,
            "core_equal": same_core,
            "sidecar_equal": same_sidecar,
            "current_receipt_equal": recovered == expected,
        })

    # Detect accidental cross-pairing of an old sidecar with a changed Core.
    changed = SemanticModel.from_dict(variants()[-1][1])
    _, changed_xml = annotation_free_core(changed)
    mismatch_detected = (
        base_sidecar["sbml_core_sha256"]
        != sha256(changed_xml.encode("utf-8")).hexdigest()
    )
    if not mismatch_detected:
        raise AssertionError("Core/sidecar mismatch was not detected")

    return {
        "schema": "bioir-e284-sbml-core-thin-sidecar-v1",
        "synthetic_only": True,
        "libsbml_version": libsbml.getLibSBMLDottedVersion(),
        "receipt_projection_matches": len(receipt_matches),
        "receipt_cases": receipt_matches,
        "variant_pairs": pairs,
        "core_only_collisions": sum(x["core_equal"] for x in pairs),
        "core_changed_controls": sum(not x["core_equal"] for x in pairs),
        "sidecar_distinguished_pairs": sum(not x["sidecar_equal"] for x in pairs),
        "cross_pair_core_digest_mismatch_detected": mismatch_detected,
        "claim": (
            "Core alone loses tested intent/provenance; a thin metadata sidecar "
            "can represent the CURRENT unresolved receipt on this synthetic "
            "corpus. Standalone BioIR novelty NOT YET PROVEN."
        ),
        "limitations": [
            "Sidecar metadata and source fingerprint come from BioIR source, not independently inferred.",
            "All introduced_assumptions are empty; no completion-profile audit is tested.",
            "Six synthetic receipt cases and six controlled variants, not real biology.",
            "Only one libSBML path; no Antimony round-trip or external-tool comparison.",
            "Core digest detects mismatched pairing, not adversarial modification of both files.",
            "No guarantee of broad SBML semantic equivalence or model executability.",
        ],
    }


if __name__ == "__main__":
    result = run()
    out = ROOT / "research/results/e284_sbml_sidecar.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    print(json.dumps({
        "receipt_matches": result["receipt_projection_matches"],
        "core_only_collisions": result["core_only_collisions"],
        "sidecar_distinguished": result["sidecar_distinguished_pairs"],
    }, sort_keys=True))
