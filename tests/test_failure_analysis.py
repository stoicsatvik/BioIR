from bioir.failure_analysis import (
    fixed_1000_failure_trajectories,
    summarize_fixed_1000_failures,
    trace_noisy_episode,
)
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


def test_failure_mechanism_summary_is_deterministic_and_exhaustive():
    first = summarize_fixed_1000_failures()
    second = summarize_fixed_1000_failures()
    assert first == second
    assert first.failure_count == len(first.failure_seeds)
    assert first.failure_seeds == fixed_1000_seed_verdict().failing_noisy_seeds
    assert (
        first.wait_dominated_count
        + first.action_dominated_count
        + first.tied_count
        == first.failure_count
    )
    assert 0 <= first.exhausted_budget_count <= first.failure_count
    assert 0 <= first.max_longest_wait_streak <= 30


def test_failure_mechanism_summary_matches_raw_trajectories():
    summary = summarize_fixed_1000_failures()
    trajectories = fixed_1000_failure_trajectories()
    assert summary.wait_dominated_count == sum(t.waits > t.actions for t in trajectories)
    assert summary.action_dominated_count == sum(t.actions > t.waits for t in trajectories)
    assert summary.tied_count == sum(t.actions == t.waits for t in trajectories)
    assert summary.exhausted_budget_count == sum(
        t.waits + t.actions == 30 for t in trajectories
    )
