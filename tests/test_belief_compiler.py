from bioir.belief import BeliefValue
from bioir.belief_compiler import compile_belief_objective
from bioir.model import Objective, OpCode


def opcodes(ops):
    return [op.opcode for op in ops]


def test_ambiguous_belief_defers_direction_change() -> None:
    objective = Objective(variable="x", target=0.6, tolerance=0.05)
    ops = compile_belief_objective(objective, BeliefValue(0.45, 0.2), 0.1)
    assert opcodes(ops) == [OpCode.SENSE, OpCode.WAIT, OpCode.MAINTAIN]
    assert not any(op.opcode in (OpCode.INCREASE, OpCode.DECREASE) for op in ops)


def test_precise_below_belief_preserves_increase_behavior() -> None:
    objective = Objective(variable="x", target=0.6, tolerance=0.05)
    ops = compile_belief_objective(objective, BeliefValue(0.2, 0.0), 0.1)
    assert opcodes(ops) == [OpCode.SENSE, OpCode.INCREASE, OpCode.MAINTAIN]
    assert ops[1].magnitude == 0.1


def test_precise_above_belief_preserves_decrease_behavior() -> None:
    objective = Objective(variable="x", target=0.4, tolerance=0.05)
    ops = compile_belief_objective(objective, BeliefValue(0.8, 0.0), 0.1)
    assert opcodes(ops) == [OpCode.SENSE, OpCode.DECREASE, OpCode.MAINTAIN]
    assert ops[1].magnitude == 0.1


def test_guaranteed_target_does_not_change_direction() -> None:
    objective = Objective(variable="x", target=0.6, tolerance=0.05)
    ops = compile_belief_objective(objective, BeliefValue(0.6, 0.03), 0.1)
    assert opcodes(ops) == [OpCode.SENSE, OpCode.MAINTAIN]


def test_same_mean_changes_decision_only_due_to_uncertainty() -> None:
    objective = Objective(variable="x", target=0.6, tolerance=0.05)
    precise = compile_belief_objective(objective, BeliefValue(0.45, 0.0), 0.1)
    uncertain = compile_belief_objective(objective, BeliefValue(0.45, 0.2), 0.1)
    assert OpCode.INCREASE in opcodes(precise)
    assert OpCode.WAIT in opcodes(uncertain)
    assert OpCode.INCREASE not in opcodes(uncertain)
