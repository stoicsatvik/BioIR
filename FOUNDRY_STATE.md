# Unified Foundry State — BioIR

## Mission
Build a safe, executable biological abstraction layer that maps high-level biological objectives into typed, inspectable, reproducible intermediate representations and simulation policies, without pretending simulation is equivalent to wet-lab or clinical validation.

## Claim status
NOT YET PROVEN as a biologically valid control layer. The repository currently supports only software/simulation claims. The v0.2 uncertainty-aware normalized belief-state primitives are SUPPORTED at exact implementation head `c101ded6d968f87eba4c4ff5fe69071bc327dc2d` by GitHub Actions workflow `35020242830` (`test`, run #4), conclusion SUCCESS. Conservative uncertainty-aware compiler decisions are SUPPORTED at exact implementation head `dff4e36674a5e49232e9f9978aeefeae5406151a` by workflow `35040211614` (`test`, run #6), conclusion SUCCESS.

## Current stack
`intent -> objective/state/constraint model -> BioIR -> uncertainty-aware compiler/controller -> simulation backend -> observation -> feedback`

## Current v0 capabilities
- Typed program/state/objective/constraint representation.
- Small semantic ISA: SENSE, INCREASE, DECREASE, MAINTAIN, WAIT.
- Compiler from high-level goals to abstract operations.
- Validation that rejects malformed/non-simulation operations.
- Closed-loop toy runtime with repeated sensing, planning, action, and re-observation.
- CLI examples and deterministic tests.
- v0.2 `BeliefValue(mean, uncertainty)` primitive with bounded intervals, conservative directional predicates, whole-interval target satisfaction, deterministic synthetic observation fusion, and invalid-state rejection.
- Belief-aware compiler decision path: ambiguous intervals defer direction-changing operations with WAIT; sufficiently precise beliefs preserve INCREASE/DECREASE; whole-interval target satisfaction emits MAINTAIN.
- Apache-2.0 licensed public repository.

## Validated v0.2 belief-state frontier
Branch: `foundry/v02-belief-state`
PR: #2 (draft/open/unmerged)
Validated implementation head: `c101ded6d968f87eba4c4ff5fe69071bc327dc2d`
Validation: workflow `35020242830` SUCCESS.

SUPPORTED: deterministic software contracts for normalized belief intervals, conservative direction decisions, whole-interval target checks, synthetic observation fusion, and invalid-state rejection.

## Validated v0.2 uncertainty-compiler frontier
Branch: `foundry/v02-uncertainty-compiler`
PR: #3 (draft/open/unmerged)
Validated implementation head: `dff4e36674a5e49232e9f9978aeefeae5406151a`
Validation: workflow `35040211614` (`test`, run #6) SUCCESS.

SUPPORTED: deterministic compiler semantics under synthetic normalized beliefs: ambiguity causes WAIT rather than an unsupported direction change; precise beliefs preserve directional baseline behavior; beliefs wholly within tolerance MAINTAIN.

NOT YET PROVEN: closed-loop runtime robustness under repeated noisy observations; biological sensing accuracy; causal validity; organism-level behavior; intervention efficacy; wet-lab validity; clinical validity.

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
1. Benchmark the uncertainty-aware compiler inside a deterministic closed-loop simulation under repeated observation noise.
2. Preserve matched seeds, budgets, initial states, objectives, and simulator dynamics between exact-observation and noisy-observation conditions.
3. Measure unsupported-direction decisions, unnecessary WAIT decisions, target attainment, oscillation, and convergence time; preserve failing seeds.
4. Require uncertainty-aware control to reduce unsupported-direction decisions without silently winning through extra sensing/action budget.
5. Add graph-based causal/dependency state models only after the closed-loop uncertainty gate is validated.
6. Multi-objective constrained control and conflict resolution.
7. Backend capability contracts so the IR can target multiple simulators without leaking implementation details.
8. Provenance for every lowering/planning decision.
9. Deterministic benchmark suite for controllability, robustness, compression quality, and failure preservation.
10. Public ontology/data adapters only where they improve measurable semantics or validation.

## Evaluation doctrine
Every substantial change should answer a falsifiable question and preserve a baseline.

Primary software metrics may include:
- representation completeness on a bounded benchmark;
- invalid-program rejection rate;
- deterministic replay/reproducibility;
- objective satisfaction under explicit simulation assumptions;
- robustness to observation noise/model uncertainty;
- unsupported-direction decision rate;
- unnecessary deferral rate;
- convergence time and oscillation under matched budgets;
- abstraction compression versus backend-specific control logic;
- provenance completeness;
- runtime/compute cost.

No biological-validity claim is allowed without evidence external to the toy simulator.

## Autonomous work policy
BioIR is a first-class Unified Parallel Foundry stream. Hourly Foundry runs may inspect and advance it when it is the highest-value eligible frontier. If 3 Foundry runs pass without substantive BioIR progress and the stream is not BLOCKED, prioritize BioIR on the next run.

Each substantive shift should use a dedicated `foundry/...` branch and draft PR, run available tests/CI, preserve failures, and record the exact branch/commit/PR, result, claim state, blocker, and next move.

## Current blocker
The belief-aware compiler decision path is exact-head CI validated, but the existing closed-loop runtime has not yet been evaluated under repeated noisy observations with matched seeds and budgets. Therefore robust closed-loop behavior under uncertainty remains NOT YET PROVEN.

## Current next move
After exact-head validation of this reconciled ledger commit, create a dedicated closed-loop uncertainty benchmark branch. Compare exact versus noisy observation conditions under matched deterministic seeds/budgets and record unsupported-direction decisions, unnecessary waits, target attainment, oscillation, and convergence time. Preserve failing seeds and do not advance dependency graphs until that gate is supported.
