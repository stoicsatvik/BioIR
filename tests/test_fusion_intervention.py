from bioir.fusion_intervention import fixed_1000_fusion_verdict


def test_temporal_fusion_is_matched_and_falsifiable():
    verdict = fixed_1000_fusion_verdict()
    assert verdict.baseline_converged == 963
    assert verdict.baseline_unsupported == 0
    assert verdict.fusion_unsupported == 0
    # Preserve the frozen negative result. The promotion rule is unchanged;
    # a rejected intervention is not a failing test suite.
    assert verdict.fusion_converged == 876
    assert verdict.fusion_converged < verdict.baseline_converged
    assert verdict.regressed_seeds
    from bioir.fusion_intervention import verdict_artifact
    assert verdict_artifact(verdict)["claim_state"] == "REJECTED"


def test_seed_outcomes_are_preserved():
    first = fixed_1000_fusion_verdict()
    second = fixed_1000_fusion_verdict()
    assert first == second
    assert set(first.regressed_seeds).isdisjoint(first.recovered_seeds)
