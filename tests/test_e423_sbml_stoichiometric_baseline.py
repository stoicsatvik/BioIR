"""Offline deterministic contracts for E423's published-data comparison."""

import math

import pytest

from research.e423_sbml_stoichiometric_baseline import evaluate_rows, frozen_model_parameters


BASE_XML = '''<sbml xmlns="http://www.sbml.org/sbml/level3/version2/core" level="3" version="2">
<model><listOfCompartments><compartment id="compartment" size="1"/></listOfCompartments><listOfSpecies><species id="S1" initialAmount="0.015"/><species id="S2" initialAmount="0"/></listOfSpecies>
<listOfParameters><parameter id="k1" value="1"/></listOfParameters>
<listOfReactions><reaction><listOfReactants><speciesReference species="S1" stoichiometry="1"/></listOfReactants>
<listOfProducts><speciesReference species="S2" stoichiometry="2"/></listOfProducts>
<kineticLaw><math xmlns="http://www.w3.org/1998/Math/MathML"><apply><times/><ci> compartment </ci><ci> k1 </ci><ci> S1 </ci></apply></math></kineticLaw>
</reaction></listOfReactions></model></sbml>'''


def test_frozen_stoichiometry_is_read_from_sbml_not_assumed():
    assert frozen_model_parameters(BASE_XML) == (0.015, 2.0)


def test_reference_case_00003_naive_sum_is_not_conserved():
    rows = [(0.0, 0.015, 0.0), (5.0, 0.000101069204986282, 0.02979786159002744)]
    result = evaluate_rows(rows, 0.015, 2.0)
    assert result["max_weighted_invariant_error"] < 1e-15
    assert abs(result["relative_naive_species_sum_drift"] - (1 - math.exp(-5))) < 1e-12
    assert result["max_analytic_absolute_error"] < 1e-15


def test_unity_stoichiometry_recovers_species_sum_conservation():
    rows = [(0.0, 0.00015, 0.0), (5.0, 0.00000101069204986282, 0.0001489893079501372)]
    result = evaluate_rows(rows, 0.00015, 1.0)
    assert result["max_naive_species_sum_drift"] < 1e-15
    assert result["max_weighted_invariant_error"] < 1e-15


def test_unexpected_kinetic_law_fails_closed():
    with pytest.raises(ValueError, match="kinetic law"):
        frozen_model_parameters(BASE_XML.replace("<ci> S1 </ci>", "<ci> missing </ci>"))


def test_nonfinite_reference_fails_closed():
    with pytest.raises(ValueError, match="invalid time"):
        evaluate_rows([(1.0, float("nan"), 0.0)], 0.015, 2.0)


def test_nonunit_compartment_fails_closed():
    with pytest.raises(ValueError, match="unit compartment"):
        frozen_model_parameters(BASE_XML.replace('size="1"', 'size="2"'))
