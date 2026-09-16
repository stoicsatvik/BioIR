# Unified Foundry State — BioIR

## Mission
Build a safe, executable biological abstraction layer that maps high-level biological objectives into typed, inspectable, reproducible intermediate representations and simulation policies, without pretending simulation is equivalent to wet-lab or clinical validation.

## Claim status
NOT YET PROVEN as a biologically valid control layer. The repository currently supports only software/simulation claims.

SUPPORTED software frontiers:
- normalized uncertainty-aware belief-state primitives;
- conservative belief-aware compiler semantics;
- matched deterministic closed-loop uncertainty contracts;
- frozen 1,000-seed quantitative uncertainty verdict;
- deterministic per-seed failure reconstruction;
- deterministic descriptive failure-mechanism summarization.

REJECTED: universal robustness of the current conservative noisy controller on the frozen synthetic mixture. The controller preserves the tested unsupported-direction safety property but does not converge on every frozen seed under the same budget.

NOT YET PROVEN: any controller intervention that improves same-budget convergence while preserving the unsupported-direction property; biological sensing accuracy; causal validity; organism-level behavior; intervention efficacy; wet-lab validity; clinical validity.

## Current stack
`intent -> objective/state/constraint model -> BioIR -> uncertainty-aware compiler/controller -> simulation backend -> observation -> feedback`

## Current v0 capabilities
- Typed program/state/objective/constraint representation.
- Small semantic ISA: SENSE, INCREASE, DECREASE, MAINTAIN, WAIT.
- Compiler from high-level goals to abstract operations.
- Validation that rejects malformed/non-simulation operations.
- Closed-loop toy runtime with repeated sensing, planning, action, and re-observation.
- `BeliefValue(mean, uncertainty)` with bounded intervals and conservative directional predicates.
- Belief-aware compilation: ambiguous intervals WAIT; sufficiently precise beliefs preserve INCREASE/DECREASE; whole-interval target satisfaction MAINTAINs.
- Matched exact/noisy closed-loop benchmark with frozen seeds and budgets.
- Per-seed failure retention and deterministic failure replay.
- Descriptive failure summaries over WAIT/action balance, WAIT streaks, and budget exhaustion.

## Validated evidence chain
1. Belief-state primitives: branch `foundry/v02-belief-state`, PR #2, head `c101ded6d968f87eba4c4ff5fe69071bc327dc2d`, workflow `35020242830` SUCCESS.
2. Uncertainty compiler: branch `foundry/v02-uncertainty-compiler`, PR #3, implementation head `dff4e36674a5e49232e9f9978aeefeae5406151a`, workflow `35040211614` SUCCESS. Reconciled ledger head `6ffd297519fc1d1f6ef8654e807ce7230e405228` also received exact-head CI success.
3. Closed-loop uncertainty contracts: branch `foundry/v02-closed-loop-uncertainty`, PR #4. Exact-head benchmark contracts at `abdd1d5ee12d72699c1b5035f083224ea69a6806` passed workflow `35056114383`. The later frozen 1,000-seed quantitative head `beb986db0850d02fd010cb65f1c5c5a5f0118bff` passed workflow `35064233442`.
4. Failure stratification: branch `foundry/v02-failure-stratification`, PR #5, head `a08b528f9e8b3881e76b25ea9438f59d83125386`, workflow `35079729784` SUCCESS.
5. Failure-mechanism summary: branch `foundry/v02-failure-mechanism`, PR #6, head `de86838df55e29e91f26fb903df5aa11b9000e18`, workflow `35091005800` (`test`, run #12) SUCCESS.

## Frozen quantitative result
The deterministic 1,000-seed synthetic mixture preserves the safety-versus-convergence tradeoff rather than hiding it behind a single aggregate. The current controller achieved zero unsupported noisy-direction decisions on that frozen mixture but failed to converge on a non-empty subset under the same step/action budget. Therefore conservative directional safety is SUPPORTED on this benchmark while universal robustness is REJECTED.

Failure identities are frozen by the quantitative verdict and reconstructed deterministically by the failure-analysis layer. The mechanism partition (WAIT-dominated/action-dominated/tied) is descriptive only and must not be interpreted as causal evidence.

## Hard boundary
BioIR remains simulation-first and safety-constrained.
- No nucleotide-sequence generation for harmful biological engineering.
- No pathogen engineering or optimization.
- No wet-lab procedural protocols.
- No autonomous real-world biological actuation.
- No human/animal experimentation instructions.
- No patient-specific treatment or clinical decision system.
- Toy or computational success must never be promoted as organism-level or clinical evidence.

## Highest-EV research frontier
1. Freeze the validated failure-mechanism distribution before modifying the controller.
2. Preregister the smallest intervention justified by the observed failure mechanism rather than selecting a method after seeing intervention results.
3. Compare candidate versus frozen controller on identical seeds, sensing budget, action budget, initial state, objective, observation model, and simulator dynamics.
4. Promotion gate: improve convergence while producing zero increase in unsupported-direction decisions. Preserve all regressed and failing seeds.
5. Reject interventions that win by extra observations, actions, steps, seed selection, or altered dynamics.
6. Only after this gate, consider graph-based causal/dependency state models, multi-objective constrained control, backend capability contracts, and provenance expansion.

## Evaluation doctrine
Every substantial change should answer a falsifiable question and preserve a baseline. Primary software metrics include deterministic replay, target attainment, unsupported-direction decisions, WAIT/deferral cost, convergence time, oscillation, budget use, failure identities, and regression seeds. No biological-validity claim is allowed without evidence external to the toy simulator.

## Autonomous work policy
BioIR is a first-class Unified Parallel Foundry stream. Hourly Foundry runs may inspect and advance it when it is the highest-value eligible frontier. If 3 Foundry runs pass without substantive BioIR progress and the stream is not BLOCKED, prioritize BioIR on the next run.

Each substantive shift should use a dedicated `foundry/...` branch and draft PR, run available tests/CI, preserve failures, and record the exact branch/commit/PR, result, claim state, blocker, and next move.

## Current blocker
No CI blocker remains through failure-mechanism head `de86838df55e29e91f26fb903df5aa11b9000e18`. The research blocker is intervention selection: the validated mechanism summary is descriptive, not causal, so a controller change must be preregistered and tested against the frozen baseline rather than assumed to fix the failures.

## Current next move
Record the concrete validated mechanism distribution, then preregister one minimal controller intervention and its rejection/promotion thresholds. Run it against the frozen 1,000-seed mixture with identical budgets and dynamics. Require improved convergence with no increase in unsupported-direction decisions, and preserve every regression seed. Biological validity remains NOT YET PROVEN regardless of simulator outcome.
