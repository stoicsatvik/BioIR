from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
from pathlib import Path
from typing import Any
import xml.etree.ElementTree as ET

import antimony
import libsbml

from bioir.cli import load_semantic_model
from bioir.sbml_backend import BIOIR_NS, SBML_NS, to_sbml_xml


POSITIVE_CONTROL = """model positive_control
  A = 1;
  B = 0;
  k1 = 0.1;
  J0: A -> B; k1*A;
end
"""


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _sbml_signature(xml: str) -> dict[str, Any]:
    document = libsbml.readSBMLFromString(xml)
    if document is None or document.getModel() is None:
        raise ValueError("libSBML could not parse the SBML model")
    model = document.getModel()
    xml_root = ET.fromstring(xml)
    sbml_model = xml_root.find(f".//{{{SBML_NS}}}model")
    if sbml_model is None:
        raise ValueError("SBML XML has no model element")
    model_annotation_element = sbml_model.find(f"{{{SBML_NS}}}annotation")
    bioir_model_annotation = bool(
        model_annotation_element is not None
        and any(
            child.tag == f"{{{BIOIR_NS}}}semanticModel"
            for child in model_annotation_element
        )
    )
    reaction_annotations = {}
    for reaction_element in sbml_model.findall(f".//{{{SBML_NS}}}reaction"):
        annotation_element = reaction_element.find(f"{{{SBML_NS}}}annotation")
        reaction_annotations[reaction_element.get("id", "")] = bool(
            annotation_element is not None
            and any(
                child.tag == f"{{{BIOIR_NS}}}interaction"
                for child in annotation_element
            )
        )
    errors = []
    for index in range(document.getNumErrors()):
        error = document.getError(index)
        errors.append(
            {
                "severity": int(error.getSeverity()),
                "category": str(error.getCategoryAsString()),
                "message": str(error.getMessage()).strip(),
            }
        )

    compartments = []
    for index in range(model.getNumCompartments()):
        item = model.getCompartment(index)
        compartments.append(
            {
                "id": item.getId(),
                "size": float(item.getSize()) if item.isSetSize() else None,
                "units": item.getUnits() if item.isSetUnits() else None,
            }
        )

    species = []
    for index in range(model.getNumSpecies()):
        item = model.getSpecies(index)
        species.append(
            {
                "id": item.getId(),
                "compartment": item.getCompartment(),
                "substance_units": item.getSubstanceUnits() if item.isSetSubstanceUnits() else None,
                "initial_concentration": (
                    float(item.getInitialConcentration())
                    if item.isSetInitialConcentration()
                    else None
                ),
                "initial_amount": (
                    float(item.getInitialAmount()) if item.isSetInitialAmount() else None
                ),
            }
        )

    parameters = []
    for index in range(model.getNumParameters()):
        item = model.getParameter(index)
        parameters.append(
            {
                "id": item.getId(),
                "units": item.getUnits() if item.isSetUnits() else None,
                "value_set": bool(item.isSetValue()),
                "value": float(item.getValue()) if item.isSetValue() else None,
                "constant": bool(item.getConstant()),
            }
        )

    reactions = []
    for index in range(model.getNumReactions()):
        item = model.getReaction(index)
        reactions.append(
            {
                "id": item.getId(),
                "reversible": bool(item.getReversible()),
                "reactants": sorted(
                    (item.getReactant(j).getSpecies(), float(item.getReactant(j).getStoichiometry()))
                    for j in range(item.getNumReactants())
                ),
                "products": sorted(
                    (item.getProduct(j).getSpecies(), float(item.getProduct(j).getStoichiometry()))
                    for j in range(item.getNumProducts())
                ),
                "kinetic_law_present": item.getKineticLaw() is not None,
                "bioir_annotation": reaction_annotations.get(item.getId(), False),
            }
        )

    return {
        "document_error_count": int(document.getNumErrors()),
        "document_diagnostics": errors,
        "model_id": model.getId(),
        "compartments": sorted(compartments, key=lambda row: row["id"]),
        "species": sorted(species, key=lambda row: row["id"]),
        "parameters": sorted(parameters, key=lambda row: row["id"]),
        "reactions": sorted(reactions, key=lambda row: row["id"]),
        "bioir_model_annotation": bioir_model_annotation,
    }


def _load_antimony_sbml(xml: str) -> tuple[str | None, str | None]:
    antimony.clearPreviousLoads()
    handle = antimony.loadSBMLString(xml)
    if handle < 0:
        return None, str(antimony.getLastError())
    module = antimony.getMainModuleName()
    text = antimony.getAntimonyString(module)
    if not text:
        return None, str(antimony.getLastError())
    return text, None


def run_probe(model_path: Path, output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    model = load_semantic_model(model_path)
    source_sbml = to_sbml_xml(model)
    source_signature = _sbml_signature(source_sbml)
    (output_dir / "source_bioir_model.xml").write_text(source_sbml, encoding="utf-8")

    # Control: a libSBML-only parse/write cycle separates annotation loss in
    # Antimony from loss in the BioIR exporter or libSBML serializer itself.
    libsbml_document = libsbml.readSBMLFromString(source_sbml)
    if libsbml_document is None or libsbml_document.getModel() is None:
        raise RuntimeError("libSBML control could not parse the source SBML model")
    libsbml_roundtrip = libsbml.writeSBMLToString(libsbml_document)
    if not libsbml_roundtrip:
        raise RuntimeError("libSBML control produced no round-trip SBML")
    libsbml_signature = _sbml_signature(libsbml_roundtrip)
    (output_dir / "libsbml_roundtrip.xml").write_text(
        libsbml_roundtrip, encoding="utf-8"
    )
    libsbml_control = {
        "status": "PASS",
        "roundtrip_sbml_sha256": _sha256(libsbml_roundtrip),
        "bioir_model_annotation_preserved": (
            source_signature["bioir_model_annotation"]
            and libsbml_signature["bioir_model_annotation"]
        ),
        "bioir_interaction_annotation_preserved": (
            source_signature["reactions"][0]["bioir_annotation"]
            and libsbml_signature["reactions"][0]["bioir_annotation"]
        ),
    }

    # Positive control: prove the pinned Antimony binding can parse and export
    # a fully executable reaction before interpreting a partial-model result.
    antimony.clearPreviousLoads()
    positive_handle = antimony.loadAntimonyString(POSITIVE_CONTROL)
    if positive_handle < 0:
        raise RuntimeError(f"Antimony positive control failed: {antimony.getLastError()}")
    positive_module = antimony.getMainModuleName()
    positive_sbml = antimony.getSBMLString(positive_module)
    if not positive_sbml:
        raise RuntimeError(f"Antimony positive control produced no SBML: {antimony.getLastError()}")
    positive_signature = _sbml_signature(positive_sbml)

    antimony_text, import_error = _load_antimony_sbml(source_sbml)
    result: dict[str, Any] = {
        "status": "REJECTED_BY_ANTIMONY",
        "import_error": import_error,
        "roundtrip_error": None,
        "source_signature": source_signature,
        "positive_control": {
            "status": "PASS",
            "antimony_model": positive_module,
            "sbml_signature": positive_signature,
        },
        "libsbml_control": libsbml_control,
        "antimony_version": importlib.metadata.version("antimony"),
        "libsbml_version": libsbml.getLibSBMLDottedVersion(),
        "source_sbml_sha256": _sha256(source_sbml),
        "antimony_text_sha256": None,
        "roundtrip_sbml_sha256": None,
        "antimony_text": None,
        "roundtrip_signature": None,
        "comparison": {
            "core_structure_preserved": False,
            "unresolved_parameter_preserved": False,
            "kinetic_law_absence_preserved": False,
            "bioir_model_annotation_preserved": False,
            "bioir_interaction_annotation_preserved": False,
        },
        "claim_boundary": (
            "Synthetic partial-model interoperability probe only; no biological "
            "model validation or executable completion is claimed."
        ),
    }

    if antimony_text is not None:
        result["status"] = "IMPORTED_FROM_SBML"
        result["antimony_text"] = antimony_text
        result["antimony_text_sha256"] = _sha256(antimony_text)
        (output_dir / "antimony_partial_model.ant").write_text(antimony_text, encoding="utf-8")

        antimony.clearPreviousLoads()
        roundtrip_handle = antimony.loadAntimonyString(antimony_text)
        if roundtrip_handle < 0:
            result["status"] = "ROUNDTRIP_FAILED"
            result["roundtrip_error"] = str(antimony.getLastError())
        else:
            roundtrip_module = antimony.getMainModuleName()
            roundtrip_sbml = antimony.getSBMLString(roundtrip_module)
            if not roundtrip_sbml:
                result["status"] = "ROUNDTRIP_FAILED"
                result["roundtrip_error"] = str(antimony.getLastError())
            else:
                result["status"] = "ROUNDTRIP_COMPLETED"
                result["roundtrip_sbml_sha256"] = _sha256(roundtrip_sbml)
                result["roundtrip_signature"] = _sbml_signature(roundtrip_sbml)
                (output_dir / "antimony_roundtrip.xml").write_text(
                    roundtrip_sbml, encoding="utf-8"
                )

                source = source_signature
                roundtrip = result["roundtrip_signature"]
                def canonical_core(signature: dict[str, Any]) -> dict[str, Any]:
                    def rounded(value: Any) -> Any:
                        return round(value, 12) if isinstance(value, float) else value

                    compartments = [
                        {key: rounded(value) for key, value in row.items()}
                        for row in signature["compartments"]
                    ]
                    species = [
                        {key: rounded(value) for key, value in row.items()}
                        for row in signature["species"]
                    ]
                    parameters = [
                        {key: rounded(value) for key, value in row.items()}
                        for row in signature["parameters"]
                    ]
                    reactions = []
                    for row in signature["reactions"]:
                        reactions.append({
                            key: (
                                [(item[0], rounded(item[1])) for item in value]
                                if key in {"reactants", "products"}
                                else value
                            )
                            for key, value in row.items()
                            if key != "bioir_annotation"
                        })
                    return {
                        "compartments": compartments,
                        "species": species,
                        "parameters": parameters,
                        "reactions": reactions,
                    }

                source_parameters = {row["id"]: row for row in source["parameters"]}
                roundtrip_parameters = {row["id"]: row for row in roundtrip["parameters"]}
                source_reactions = {row["id"]: row for row in source["reactions"]}
                roundtrip_reactions = {row["id"]: row for row in roundtrip["reactions"]}
                result["comparison"] = {
                    "core_structure_preserved": (
                        canonical_core(source) == canonical_core(roundtrip)
                    ),
                    "unresolved_parameter_preserved": (
                        "k1" in source_parameters
                        and "k1" in roundtrip_parameters
                        and not source_parameters["k1"]["value_set"]
                        and not roundtrip_parameters["k1"]["value_set"]
                    ),
                    "kinetic_law_absence_preserved": (
                        "A_to_B" in source_reactions
                        and "A_to_B" in roundtrip_reactions
                        and not source_reactions["A_to_B"]["kinetic_law_present"]
                        and not roundtrip_reactions["A_to_B"]["kinetic_law_present"]
                    ),
                    "bioir_model_annotation_preserved": (
                        source["bioir_model_annotation"]
                        and roundtrip["bioir_model_annotation"]
                    ),
                    "bioir_interaction_annotation_preserved": (
                        "A_to_B" in source_reactions
                        and "A_to_B" in roundtrip_reactions
                        and source_reactions["A_to_B"]["bioir_annotation"]
                        and roundtrip_reactions["A_to_B"]["bioir_annotation"]
                    ),
                }

    receipt_path = output_dir / "antimony_partial_model_receipt.json"
    receipt_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="examples/underspecified_conversion.json")
    parser.add_argument("--out", default="artifacts/e510-antimony-partial-model")
    args = parser.parse_args()
    result = run_probe(Path(args.model), Path(args.out))
    print(json.dumps({key: value for key, value in result.items() if key != "antimony_text"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
