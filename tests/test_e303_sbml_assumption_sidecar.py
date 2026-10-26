"""E303 safe synthetic standards-based assumption-receipt falsification."""
from xml.etree import ElementTree as ET

from research.e303_sbml_assumption_sidecar import (
    SBML, complete_with_explicit_profile, evaluate, missing_commitments,
    strip_annotations,
)


def minimal_core():
    return (
        f'<sbml xmlns="{SBML}" level="3" version="2"><model id="toy">'
        '<listOfCompartments><compartment id="cell" size="1" constant="true"/></listOfCompartments>'
        '<listOfSpecies><species id="A" compartment="cell" initialConcentration="1" '
        'hasOnlySubstanceUnits="false" boundaryCondition="false" constant="false"/></listOfSpecies>'
        '<listOfParameters><parameter id="k1" constant="true"/></listOfParameters>'
        '<listOfReactions><reaction id="A_to_B" reversible="false"/></listOfReactions>'
        '</model></sbml>'
    )


def test_frozen_campaign():
    result = evaluate(minimal_core())
    assert result["completed_profiles_verified"] == 2
    assert result["distinct_completed_core"]
    assert result["swapped_sidecar_rejected"]
    assert result["parameter_tamper_rejected"]
    assert result["kinetic_law_tamper_rejected"]
    assert result["origin_spoof_accepted"], "negative provenance-authenticity control must remain visible"


def test_fail_closed_nonfinite_profile_and_unknown_commitment():
    for value in [float("nan"), float("inf"), -0.1, 0.0]:
        try:
            complete_with_explicit_profile(
                minimal_core(), k1=value, origin="hypothetical_user_choice"
            )
        except ValueError:
            pass
        else:
            raise AssertionError("invalid hypothetical value accepted")
    changed = minimal_core().replace('id="k1"', 'id="other"')
    try:
        complete_with_explicit_profile(
            changed, k1=0.1, origin="hypothetical_user_choice"
        )
    except ValueError:
        pass
    else:
        raise AssertionError("unexpected commitment accepted")


def test_unrelated_annotation_removed_without_mutating_core():
    source = minimal_core().replace(
        "<listOfCompartments>",
        "<annotation><note>synthetic</note></annotation><listOfCompartments>",
    )
    stripped = strip_annotations(source)
    assert "synthetic" not in stripped
    assert missing_commitments(stripped) == [
        "kinetic_law:A_to_B", "parameter_value:k1"
    ]
    assert ET.fromstring(stripped).find(f"{{{SBML}}}model") is not None


def test_actual_bioir_fixture_and_optional_libsbml():
    from research.e303_sbml_assumption_sidecar import run
    result = run()
    assert result["completed_profiles_verified"] == 2
    assert result["baseline_missing_keys"] == [
        "kinetic_law:A_to_B", "parameter_value:k1"
    ]
    assert result["libsbml_reparse"] in {
        "2/2", "NOT RUN (dependency unavailable)"
    }
