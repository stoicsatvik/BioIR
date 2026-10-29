"""E379 real libSBML dependency test, skipped when the dependency is absent."""
import pytest

pytest.importorskip("libsbml")

from research.e379_libsbml_serializer import run


def test_two_independent_serializer_roundtrips_and_undeclared_tamper():
    result = run()
    assert result["profiles"] == 2
    assert all(row["libsbml_completed_reparsed"] for row in result["rows"])
    assert all(row["undeclared_species_change_rejected"] for row in result["rows"])
    assert all(isinstance(row["both_reserialized_receipt_accepted"], bool)
               for row in result["rows"])
