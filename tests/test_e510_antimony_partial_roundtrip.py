from __future__ import annotations

import json
from pathlib import Path

import pytest

pytest.importorskip("antimony")
pytest.importorskip("libsbml")

from research.e510_antimony_partial_roundtrip import run_probe


def test_bioir_fixture_is_deliberately_partial_and_non_executable(tmp_path):
    result = run_probe(
        Path("examples/underspecified_conversion.json"),
        tmp_path,
    )
    source = result["source_signature"]

    assert result["positive_control"]["status"] == "PASS"
    assert result["antimony_version"] == "3.3.0"
    assert result["libsbml_version"]
    assert result["status"] in {
        "REJECTED_BY_ANTIMONY",
        "ROUNDTRIP_FAILED",
        "ROUNDTRIP_COMPLETED",
    }
    assert source["model_id"] == "underspecified_conversion"
    assert [row["id"] for row in source["species"]] == ["A", "B"]
    assert source["parameters"] == [
        {
            "id": "k1",
            "units": "per_second",
            "value_set": False,
            "value": None,
            "constant": True,
        }
    ]
    assert source["reactions"][0]["id"] == "A_to_B"
    assert source["reactions"][0]["kinetic_law_present"] is False
    assert source["bioir_model_annotation"] is True
    assert source["reactions"][0]["bioir_annotation"] is True

    assert (tmp_path / "source_bioir_model.xml").exists()
    receipt_path = tmp_path / "antimony_partial_model_receipt.json"
    assert receipt_path.exists()
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert receipt["status"] == result["status"]

    if result["status"] == "REJECTED_BY_ANTIMONY":
        assert result["import_error"]
        assert result["antimony_text_sha256"] is None
    elif result["status"] == "ROUNDTRIP_FAILED":
        assert result["antimony_text_sha256"]
        assert result["roundtrip_error"]
    else:
        assert result["antimony_text_sha256"]
        assert result["roundtrip_sbml_sha256"]
        assert (tmp_path / "antimony_partial_model.ant").exists()
        assert (tmp_path / "antimony_roundtrip.xml").exists()
        assert set(result["comparison"]) == {
            "core_structure_preserved",
            "unresolved_parameter_preserved",
            "kinetic_law_absence_preserved",
            "bioir_model_annotation_preserved",
            "bioir_interaction_annotation_preserved",
        }


def test_antimony_positive_control_is_executable():
    import antimony
    import libsbml

    from research.e510_antimony_partial_roundtrip import POSITIVE_CONTROL

    antimony.clearPreviousLoads()
    handle = antimony.loadAntimonyString(POSITIVE_CONTROL)
    assert handle >= 0, antimony.getLastError()
    module = antimony.getMainModuleName()
    sbml = antimony.getSBMLString(module)
    assert sbml
    document = libsbml.readSBMLFromString(sbml)
    assert document is not None
    model = document.getModel()
    assert model is not None
    assert model.getNumReactions() == 1
    assert model.getReaction(0).getKineticLaw() is not None
