"""E284: standards-based thin-sidecar versus current BioIR receipt controls."""
import pytest

from research.e284_sbml_sidecar import run, variants


def test_frozen_variants_cover_core_and_noncore_fields():
    rows = variants()
    assert len(rows) == 6
    assert len({label for label, _, _ in rows}) == 6
    assert sum(expected for _, _, expected in rows) == 4
    assert all(len(payload["entities"]) == 2 for _, payload, _ in rows)


def test_libsbml_core_collisions_and_sidecar_receipt_reconstruction():
    pytest.importorskip("libsbml")
    result = run()
    assert result["receipt_projection_matches"] == 6
    assert result["core_only_collisions"] == 4
    assert result["core_changed_controls"] == 2
    assert result["sidecar_distinguished_pairs"] == 6
    assert result["cross_pair_core_digest_mismatch_detected"]
    assert all(row["current_receipt_equal"] for row in result["variant_pairs"])
    assert all(not row["sidecar_equal"] for row in result["variant_pairs"])
    assert all(row["core_equal"] for row in result["variant_pairs"][:4])
    assert all(not row["core_equal"] for row in result["variant_pairs"][4:])
    assert result["synthetic_only"]
    assert any("introduced_assumptions" in x for x in result["limitations"])
