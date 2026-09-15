# Unified Foundry State — BioIR

## Mission
Build a safe, executable biological abstraction layer that maps high-level biological objectives into typed, inspectable, reproducible intermediate representations and simulation policies, without pretending simulation is equivalent to wet-lab or clinical validation.

## Claim status
NOT YET PROVEN as a biologically valid control layer. The repository currently proves only that a small software IR/compiler/runtime loop can represent, validate, lower, simulate, and test abstract state-control programs.

## Current stack
`intent -> objective/state/constraint model -> BioIR -> compiler/controller -> simulation backend -> observation -> feedback`

## Current v0 capabilities
- Typed program/state/objective/constraint representation.
- Small semantic ISA: SENSE, INCREASE, DECREASE, MAINTAIN, WAIT.
- Compiler from high-level goals to abstract operations.
- Validation that rejects malformed/non-simulation operations.
- Closed-loop toy runtime with repeated sensing, planning, action, and re-observation.
- CLI examples and deterministic tests.
- Apache-2.0 licensed public repository.

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
1. Versioned schema and formal semantics for BioIR programs.
2. Uncertainty-aware state estimation and belief-state representation.
3. Graph-based causal/dependency state models.
4. Multi-objective constrained control and conflict resolution.
5. Backend capability contracts so the IR can target multiple simulators without leaking implementation details.
6. Provenance for every lowering/planning decision.
7. Deterministic benchmark suite for controllability, robustness, compression quality, and failure preservation.
8. Public ontology/data adapters only where they improve measurable semantics or validation.

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

## Current next move
Implement the v0.2 state-model foundation: explicit uncertainty plus dependency graph semantics, with deterministic tests showing how compiler/runtime behavior changes under partial observation without expanding into real biological actuation.
