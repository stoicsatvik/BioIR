from bioir.fusion_intervention import fixed_1000_fusion_verdict


def test_temporal_fusion_is_matched_and_falsifiable():
    verdict = fixed_1000_fusion_verdict()
    assert verdict.baseline_converged == 963
    assert verdict.baseline_unsupported == 0
    assert verdict.fusion_unsupported == 0
    # Promotion requires strictly better convergence at identical budget.
    # Preserve a negative result instead of weakening the gate.
    assert verdict.fusion_converged > verdict.baseline_converged
    assert not verdict.regressed_seeds


def test_seed_outcomes_are_preserved():
    first = fixed_1000_fusion_verdict()
    second = fixed_1000_fusion_verdict()
    assert first == second
    assert set(first.regressed_seeds).isdisjoint(first.recovered_seeds)
