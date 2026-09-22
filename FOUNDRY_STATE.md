# Unified Foundry State — BioIR

## Mission
Build a safe, executable biological abstraction layer that maps high-level biological objectives into typed, inspectable, reproducible intermediate representations and simulation policies, without pretending simulation is equivalent to wet-lab or clinical validation.

## Claim status
NOT YET PROVEN as a biologically valid control layer. The repository currently supports only software/simulation research.

CI INTEGRITY RESULT (2026-09-19): exact PR-head `40be53d8eb76e09e2843f46d80f564b2ee98d9b2` was evaluated by Actions run `35440467009` with corrected pytest discovery. The run collected the intended suite: 34 tests passed and exactly one preregistered temporal-fusion promotion test failed. The failure is the preserved scientific result, not an infrastructure/test-discovery failure: fusion convergence remained 876/1000 versus baseline 963/1000. The new canonical verdict-artifact tests therefore executed and passed in the same run while the rejected promotion gate remained red.

REJECTED by corrected CI on the frozen 1,000-seed matched synthetic experiment: the naïve temporal belief-fusion intervention. Baseline convergence was 963/1000 and fusion convergence was 876/1000. Both baseline and fusion retained zero unsupported-direction decisions, but fusion failed the preregistered strict-improvement gate. The negative result is preserved; do not weaken the gate or tune this intervention against the same frozen seeds.

REJECTED from deterministic benchmark reproduction: universal robustness of the current conservative noisy controller on the frozen synthetic mixture.

SUPPORTED as executed software contracts: the 34 pytest contracts that passed under corrected discovery on PR #9, including deterministic canonical verdict serialization and preservation of the frozen negative result/seed identities. This is software/simulation evidence only, not biological validation.

NOT YET PROVEN: biological sensing accuracy; causal validity; organism-level behavior; intervention efficacy; wet-lab validity; clinical validity.

## Current stack
`intent -> objective/state/constraint model -> BioIR -> uncertainty-aware compiler/controller -> simulation backend -> observation -> feedback`

## Current v0 capabilities
- Typed program/state/objective/constraint representation.
- Small semantic ISA: SENSE, INCREASE, DECREASE, MAINTAIN, WAIT.
- Compiler from high-level goals to abstract operations.
- Closed-loop toy runtime with repeated sensing, planning, action, and re-observation.
- `BeliefValue(mean, uncertainty)` with bounded intervals and conservative directional predicates.
- Matched exact/noisy synthetic benchmark and per-seed failure retention.
- Descriptive failure summaries.
- Experimental temporal belief-fusion controller, now REJECTED under its frozen promotion gate.
- Canonical `bioir/fusion-verdict/v1` machine-readable artifact with deterministic byte serialization, frozen experiment boundary, convergence/unsupported-direction metrics, and recovered/regressed seed identities.

## CI integrity repair
Branch `foundry/v02-ci-falsification-integrity` installs an explicit pytest test extra and executes `python -m pytest -q`. PR #9 run `35440467009` further demonstrates that the corrected pipeline executes both the canonical-artifact contracts and the deliberately failing falsification gate in one suite.

## Historical evidence audit
Historical workflows #2-#14 may still be useful for package installation and CLI smoke-test evidence, but they are not accepted as proof that pytest-style falsification functions executed. Their green status must not be cited as test-suite validation without corrected reruns.

## Frozen quantitative result
Corrected pytest execution preserved the frozen baseline at 963/1000 convergence and measured the temporal-fusion candidate at 876/1000. Baseline unsupported-direction decisions: 0. Fusion unsupported-direction decisions: 0. The intervention therefore preserves the directional-safety property in this toy simulator but materially worsens convergence and is REJECTED by the preregistered promotion rule.

## Hard boundary
BioIR remains simulation-first and safety-constrained.
- No nucleotide-sequence generation for harmful biological engineering.
- No pathogen engineering or optimization.
- No wet-lab procedural protocols.
- No autonomous real-world biological actuation.
- No human/animal experimentation instructions.
- No patient-specific treatment or clinical decision system.
- Toy or computational success must never be promoted as organism-level or clinical evidence.

## Evaluation doctrine
Every substantial change should answer a falsifiable question and preserve a baseline. Primary software metrics include deterministic replay, target attainment, unsupported-direction decisions, WAIT/deferral cost, convergence time, oscillation, budget use, failure identities, and regression seeds. Test discovery itself is part of the evidence chain: a green CI job is insufficient unless the intended tests are demonstrably collected and executed. A failing preregistered promotion test is valid evidence and must not be rewritten merely to restore green CI.

## Current blocker
The naïve temporal-fusion path is empirically rejected on the frozen seed set. Further tuning against those same 1,000 seeds would contaminate the evaluation frontier. The full workflow remains intentionally red because the preserved promotion assertion correctly rejects the candidate; this is evidence, not a request to weaken the test.

## Current next move
Preregister a materially different controller candidate and a sealed seed mixture before implementation/evaluation. Keep the rejected 0..999 temporal-fusion experiment immutable and use its canonical verdict artifact only as historical evidence. Biological validity remains NOT YET PROVEN regardless of simulator outcome.
