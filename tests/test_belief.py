import pytest

from bioir.belief import BeliefValue, fuse_observation


def test_interval_is_bounded() -> None:
    assert BeliefValue(0.05, 0.2).interval() == (0.0, 0.25)
    assert BeliefValue(0.95, 0.2).interval() == (0.75, 1.0)


def test_uncertainty_prevents_false_direction_claim() -> None:
    belief = BeliefValue(0.45, 0.2)
    assert not belief.definitely_below(0.6, 0.05)
    assert not belief.definitely_above(0.6, 0.05)
    assert not belief.target_guaranteed(0.6, 0.05)


def test_precise_belief_can_support_direction() -> None:
    belief = BeliefValue(0.2, 0.02)
    assert belief.definitely_below(0.6, 0.05)
    assert not belief.definitely_above(0.6, 0.05)


def test_target_requires_whole_interval_inside_tolerance() -> None:
    assert BeliefValue(0.6, 0.03).target_guaranteed(0.6, 0.05)
    assert not BeliefValue(0.6, 0.08).target_guaranteed(0.6, 0.05)


def test_observation_fusion_is_deterministic_and_reduces_bound() -> None:
    prior = BeliefValue(0.2, 0.3)
    first = fuse_observation(prior, 0.5, 0.1)
    second = fuse_observation(prior, 0.5, 0.1)
    assert first == second
    assert first.uncertainty == 0.1
    assert prior.mean < first.mean < 0.5


@pytest.mark.parametrize(
    "mean, uncertainty",
    [(-0.1, 0.1), (1.1, 0.1), (0.5, -0.1), (0.5, 1.1)],
)
def test_invalid_beliefs_are_rejected(mean: float, uncertainty: float) -> None:
    with pytest.raises(ValueError):
        BeliefValue(mean, uncertainty)
