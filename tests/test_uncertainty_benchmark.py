from bioir.uncertainty_benchmark import matched_suite, run_closed_loop


def test_closed_loop_replay_is_deterministic():
    first = run_closed_loop(seed=17, noisy=True)
    second = run_closed_loop(seed=17, noisy=True)
    assert first == second


def test_exact_baseline_converges_without_unsupported_direction():
    result = run_closed_loop(seed=3, noisy=False)
    assert result.converged
    assert result.unsupported_directions == 0
    assert result.waits == 0


def test_matched_suite_preserves_equal_step_budget_and_seed_identity():
    pairs = matched_suite((1, 2, 3, 5, 8, 13))
    assert len(pairs) == 6
    for exact, noisy in pairs:
        assert exact.seed == noisy.seed
        assert exact.steps <= 30
        assert noisy.steps <= 30


def test_noisy_controller_never_acts_in_unsupported_direction_on_fixed_seeds():
    pairs = matched_suite((1, 2, 3, 5, 8, 13, 21, 34))
    assert all(noisy.unsupported_directions == 0 for _, noisy in pairs)


def test_noisy_failures_are_observable_not_hidden():
    pairs = matched_suite(tuple(range(20)))
    # The benchmark returns every seed result, including non-convergence and
    # waits, so future regressions cannot disappear behind aggregate means.
    assert [noisy.seed for _, noisy in pairs] == list(range(20))
    assert all(noisy.waits >= 0 for _, noisy in pairs)
