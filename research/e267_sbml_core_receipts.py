"""E267: can ordinary SBML Core reconstruct BioIR's current unresolved keys?

Uses only safe, synthetic A/B conversion models and the established libSBML
parser. It deliberately strips BioIR annotations before reconstructing the
*keys*, not the richer provenance, intent, or assumption-audit workflow.
"""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path

from bioir.completion import plan_executable_completion
from bioir.semantic_model import SemanticModel
from bioir.sbml_backend import to_sbml_xml

ROOT = Path(__file__).resolve().parents[1]


def corpus() -> list[tuple[str, dict]]:
    complete = json.loads((ROOT / "examples/toy_semantic_model.json").read_text())
    incomplete = json.loads((ROOT / "examples/underspecified_conversion.json").read_text())
    cases = [("known_parameter_unknown_kinetics", complete),
             ("unknown_parameter_unknown_kinetics", incomplete)]
    double_missing = deepcopy(incomplete)
    double_missing["parameters"].append({"id": "k2", "unit": "per_second"})
    cases.append(("two_unknown_parameters", double_missing))
    no_reactions = deepcopy(incomplete)
    no_reactions["interactions"] = []
    cases.append(("no_reactions_unknown_parameter", no_reactions))
    no_parameters = deepcopy(incomplete)
    no_parameters["parameters"] = []
    no_parameters["interactions"][0]["parameter_refs"] = []
    cases.append(("unknown_kinetics_no_parameters", no_parameters))
    two_reactions = deepcopy(incomplete)
    second = deepcopy(two_reactions["interactions"][0])
    second["id"] = "B_to_A"
    second["inputs"], second["outputs"] = second["outputs"], second["inputs"]
    two_reactions["interactions"].append(second)
    cases.append(("two_unknown_kinetics", two_reactions))
    return cases


def core_keys(sbml_model) -> set[str]:
    """Read *standard SBML Core* presence bits, without any BioIR extension."""
    return {
        *(f"parameter_value:{p.getId()}" for p in sbml_model.getListOfParameters()
          if not p.isSetValue()),
        *(f"kinetic_law:{r.getId()}" for r in sbml_model.getListOfReactions()
          if not r.isSetKineticLaw()),
    }


def run() -> dict:
    import libsbml  # optional dependency installed in the semantic CI job

    rows = []
    for name, payload in corpus():
        model = SemanticModel.from_dict(payload)
        receipt = plan_executable_completion(model)
        expected = {c.key for c in receipt.unresolved_commitments}
        document = libsbml.readSBMLFromString(to_sbml_xml(model))
        if document.getModel() is None:
            raise AssertionError(f"{name}: libSBML failed to parse exported model")
        original = core_keys(document.getModel())
        # Deliberately discard *all* BioIR-specific annotations. Any surviving
        # keys therefore come from standard SBML parameter/reaction fields.
        sbml_model = document.getModel()
        sbml_model.unsetAnnotation()
        for reaction in sbml_model.getListOfReactions():
            reaction.unsetAnnotation()
        stripped_xml = libsbml.writeSBMLToString(document)
        reread = libsbml.readSBMLFromString(stripped_xml)
        if reread.getModel() is None:
            raise AssertionError(f"{name}: stripped document not readable")
        reconstructed = core_keys(reread.getModel())
        if expected != original or expected != reconstructed:
            raise AssertionError(f"{name}: unresolved-key reconstruction mismatch")
        if "bioir:" in stripped_xml or "stoicsatvik.github.io/BioIR" in stripped_xml:
            raise AssertionError(f"{name}: BioIR extension not actually stripped")
        rows.append({
            "case": name,
            "expected_receipt_keys": sorted(expected),
            "sbml_core_keys_before_stripping": sorted(original),
            "sbml_core_keys_after_annotation_stripping": sorted(reconstructed),
            "keys_reconstructed": len(expected),
            "exact_key_match": True,
            "bioir_annotations_removed": True,
        })
    return {
        "schema": "bioir-e267-sbml-core-receipt-reconstruction-v1",
        "synthetic_only": True,
        "corpus_size": len(rows),
        "exact_core_key_reconstruction": sum(r["exact_key_match"] for r in rows),
        "rows": rows,
        "claim": "Current missing-value/missing-kinetics receipt keys are recoverable from standard SBML Core on this corpus; BioIR workflow novelty NOT YET PROVEN",
        "limitations": [
            "Only six synthetic structural model variants; not real biology.",
            "Reconstructs key identities only, not rationale, provenance, or introduced assumptions.",
            "No Antimony parser or cross-tool semantic equivalence evaluated.",
            "SBML Core missing fields are not proof a model is executable or scientifically valid.",
        ],
    }


if __name__ == "__main__":
    result = run()
    out = ROOT / "research/results/e267_sbml_core_receipts.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "cases": result["corpus_size"],
        "exact_key_matches": result["exact_core_key_reconstruction"],
        "claim": result["claim"],
    }, sort_keys=True))
