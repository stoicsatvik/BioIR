# Unified Foundry State — BioIR

## Mission
Build a safe, executable biological abstraction layer that maps high-level biological objectives into typed, inspectable, reproducible intermediate representations and simulation policies, without pretending simulation is equivalent to wet-lab or clinical validation.

## Claim status
NOT YET PROVEN as a biologically valid control layer. The repository currently supports only software/simulation claims. The v0.2 uncertainty-aware normalized belief-state primitives are SUPPORTED at exact implementation head `c101ded6d968f87eba4c4ff5fe69071bc327dc2d` by GitHub Actions workflow `35020242830` (`test`, run #4), conclusion SUCCESS.

## Current stack
`intent -> objective/state/constraint model -> BioIR -> compiler/controller -> simulation backend -> observation -> feedback`

## Current v0 capabilities
- Typed program/state/objective/constraint representation.
- Small semantic ISA: SENSE, INCREASE, DECREASE, MAINTAIN, WAIT.
- Compiler from high-level goals to abstract operations.
- Validation that rejects malformed/non-simulation operations.
- Closed-loop toy runtime with repeated sensing, planning, action, and re-observation.
- CLI examples and deterministic tests.
- v0.2 `BeliefValue(mean, uncertainty)` primitive with bounded intervals, conservative directional predicates, whole-interval target satisfaction, deterministic synthetic observation fusion, and invalid-state rejection.
- Apache-2.0 licensed public repository.

## Validated v0.2 belief-state frontier
Branch: `foundry/v02-belief-state`
PR: #2 (draft/open/unmerged)
Validated implementation head: `c101ded6d968f87eba4c4ff5fe69071bc327dc2d`
Validation: workflow `35020242830` SUCCESS.

SUPPORTED: deterministic software contracts for normalized belief intervals, conservative direction decisions, whole-interval target checks, synthetic observation fusion, and invalid-state rejection.

NOT YET PROVEN: compiler/runtime integration of belief states; biological sensing accuracy; causal validity; organism-level behavior; intervention efficacy; clinical validity.

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
1. Integrate uncertainty-aware belief predicates into compiler/runtime decision semantics.
2. Preserve the certain-state baseline and compare identical deterministic simulated tasks under exact versus uncertain observations.
3. Require ambiguous observations to defer direction-changing operations while sufficiently precise observations preserve baseline behavior.
4. Add graph-based causal/dependency state models only after the compiler/runtime uncertainty gate is validated.
5. Multi-objective constrained control and conflict resolution.
6. Backend capability contracts so the IR can target multiple simulators without leaking implementation details.
7. Provenance for every lowering/planning decision.
8. Deterministic benchmark suite for controllability, robustness, compression quality, and failure preservation.
9. Public ontology/data adapters only where they improve measurable semantics or validation.

## Evaluation doctrine
Every substantial change should answer a falsifiable question and preserve a baseline.

Primary software metrics may include:
- representation completeness on a bounded benchmark;
- invalid-program rejection rate;
- deterministic replay/reproducibility;
- objective satisfaction under explicit simulation assumptions;
- robustness to observation noise/model uncertainty;
- abstraction compression versus backend-specific control logic;
- provenance completeness;
- runtime/compute cost.

No biological-validity claim is allowed without evidence external to the toy simulator.

## Autonomous work policy
BioIR is a first-class Unified Parallel Foundry stream. Hourly Foundry runs may inspect and advance it when it is the highest-value eligible frontier. If 3 Foundry runs pass without substantive BioIR progress and the stream is not BLOCKED, prioritize BioIR on the next run.

Each substantive shift should use a dedicated `foundry/...` branch and draft PR, run available tests/CI, preserve failures, and record the exact branch/commit/PR, result, claim state, blocker, and next move.

## Current blocker
Belief-state primitives are validated as standalone software contracts but are not yet wired into compiler lowering/runtime decisions. Therefore uncertainty has not yet been shown to change simulated execution conservatively.

## Current next move
After exact-head validation of this reconciled ledger commit, create a dedicated compiler/runtime integration branch. Benchmark certain-state versus uncertain-state behavior under deterministic synthetic observation noise; preserve failures and do not advance dependency graphs until that gate is supported.
