from bioir.failure_analysis import fixed_1000_failure_trajectories, trace_noisy_episode
from bioir.uncertainty_metrics import fixed_1000_seed_verdict


def test_failure_set_matches_frozen_quantitative_verdict():
    verdict = fixed_1000_seed_verdict()
    trajectories = fixed_1000_failure_trajectories()
    assert tuple(item.seed for item in trajectories) == verdict.failing_noisy_seeds
    assert all(not item.converged for item in trajectories)


def test_failure_traces_are_deterministic_and_budget_bounded():
    first = fixed_1000_failure_trajectories()
    second = fixed_1000_failure_trajectories()
    assert first == second
    assert first
    assert all(item.waits + item.actions <= 30 for item in first)
    assert all(item.longest_wait_streak <= item.waits for item in first)


def test_trace_agrees_with_known_failure_membership():
    failures = fixed_1000_seed_verdict().failing_noisy_seeds
    assert failures
    replay = trace_noisy_episode(failures[0])
    assert replay.seed == failures[0]
    assert not replay.converged
    assert replay.waits > 0
