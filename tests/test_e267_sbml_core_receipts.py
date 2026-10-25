"""E267: independent SBML Core receipt-key reconstruction checks."""
import pytest

from research.e267_sbml_core_receipts import corpus, run


def test_frozen_safe_corpus():
    cases = corpus()
    assert len(cases) == 6
    assert len({name for name, _ in cases}) == 6
    assert all(len(payload["entities"]) == 2 for _, payload in cases)
    assert all(len(payload["interactions"]) <= 2 for _, payload in cases)


def test_libsbml_reconstructs_keys_without_bioir_annotations():
    pytest.importorskip("libsbml")
    result = run()
    assert result["corpus_size"] == 6
    assert result["exact_core_key_reconstruction"] == 6
    for row in result["rows"]:
        assert row["exact_key_match"]
        assert row["bioir_annotations_removed"]
        assert row["expected_receipt_keys"] == row["sbml_core_keys_after_annotation_stripping"]
    assert any(row["keys_reconstructed"] == 0 for row in result["rows"]) is False
    assert any(row["keys_reconstructed"] >= 2 for row in result["rows"])
