"""E381: independent serializer recovery must preserve all negative controls.

Two synthetic mathematical completion profiles only; no biological validation.
"""
import pytest
from research.e303_sbml_assumption_sidecar import (
    _same_sbml_binary64, _canonical_mathml_token_xml,
)


def test_binary64_roundtrip_lexemes_and_negative_controls():
    assert _same_sbml_binary64("0.1", "0.10000000000000001")
    assert _same_sbml_binary64("0.2", "0.20000000000000001")
    assert _same_sbml_binary64("1e-1", "0.1")
    assert not _same_sbml_binary64("0.10000000000000002", "0.1")
    assert not _same_sbml_binary64("-0", "0")
    assert not _same_sbml_binary64("NaN", "NaN")
    assert not _same_sbml_binary64("1e999", "1e999")
    assert not _same_sbml_binary64(" 0.1", "0.1")
    assert not _same_sbml_binary64("0.1", "0.1 ")
    assert not _same_sbml_binary64(None, "0.1")


def test_mathml_only_outer_token_padding_is_ignored():
    prefix = '<math xmlns="http://www.w3.org/1998/Math/MathML"><apply><times/>'
    suffix = '</apply></math>'
    a = prefix + '<ci>k1</ci><ci>A</ci>' + suffix
    b = prefix + '<ci> k1 </ci><ci> A </ci>' + suffix
    bad = prefix + '<ci>k2</ci><ci>A</ci>' + suffix
    assert _canonical_mathml_token_xml(a) == _canonical_mathml_token_xml(b)
    assert _canonical_mathml_token_xml(a) != _canonical_mathml_token_xml(bad)


def test_independent_libsbml_roundtrips_now_accept_only_declared_changes():
    pytest.importorskip("libsbml")
    from research.e379_libsbml_serializer import run
    result = run()
    assert result["profiles"] == 2
    for row in result["rows"]:
        assert row["completed_only_receipt_accepted"]
        assert row["both_reserialized_receipt_accepted"]
        assert row["undeclared_species_change_rejected"]
