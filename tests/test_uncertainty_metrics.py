from bioir.uncertainty_metrics import fixed_1000_seed_verdict, summarize_matched_suite


def test_metrics_reject_empty_seed_mixture():
    try:
        summarize_matched_suite(())
    except ValueError:
        pass
    else:
        raise AssertionError("empty mixtures must be rejected")


def test_fixed_1000_seed_mixture_preserves_failures_and_budget_cost():
    metrics = fixed_1000_seed_verdict()

    # Exact observations are the matched baseline and converge without waits.
    assert metrics.seeds == 1000
    assert metrics.exact_convergence_rate == 1.0
    assert metrics.exact_unsupported_directions == 0
    assert metrics.mean_exact_steps == 6.0

    # Conservative noisy control avoids unsupported direction changes on this
    # fixed synthetic mixture, but robustness is NOT perfect: some seeds fail
    # to converge within the same 30-step budget and WAIT imposes a cost.
    assert metrics.noisy_unsupported_directions == 0
    assert metrics.noisy_convergence_rate < 1.0
    assert metrics.failing_noisy_seeds
    assert metrics.mean_noisy_waits > 0.0


def test_fixed_1000_seed_verdict_is_deterministic():
    assert fixed_1000_seed_verdict() == fixed_1000_seed_verdict()
