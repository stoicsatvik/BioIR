# Unified Foundry State — BioIR

## Mission
Build a safe, executable biological abstraction layer that maps high-level biological objectives into typed, inspectable, reproducible intermediate representations and simulation policies, without pretending simulation is equivalent to wet-lab or clinical validation.

## Claim status
NOT YET PROVEN as a biologically valid control layer. The repository currently supports only software/simulation research.

CI INTEGRITY ALERT (2026-09-16): historical GitHub Actions used `python -m unittest discover -v`, while the repository's falsification tests are pytest-style free functions. A green workflow therefore did not establish that those test functions executed. Historical claims previously promoted from green CI are downgraded to NOT YET PROVEN until rerun under the corrected pytest workflow. The implementation and deterministic benchmark artifacts remain research evidence, but CI success alone is not accepted as validation.

REJECTED from deterministic benchmark reproduction: universal robustness of the current conservative noisy controller on the frozen synthetic mixture.

NOT YET PROVEN pending corrected CI: belief-state contracts; uncertainty compiler contracts; matched closed-loop contracts; frozen 1,000-seed assertions; failure reconstruction; failure-mechanism assertions; temporal-fusion promotion hypothesis; biological sensing accuracy; causal validity; organism-level behavior; intervention efficacy; wet-lab validity; clinical validity.

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
- Experimental temporal belief-fusion controller.

## CI integrity repair
Branch `foundry/v02-ci-falsification-integrity` changes CI to install an explicit pytest test extra and execute `python -m pytest -q`. This branch intentionally inherits the temporal-fusion promotion test unchanged. If the intervention fails its frozen gate, corrected CI must fail and the negative result must be preserved rather than weakening the gate.

## Historical evidence audit
Historical workflows #2-#14 may still be useful for package installation and CLI smoke-test evidence, but they are not accepted as proof that pytest-style falsification functions executed. Their green status must not be cited as test-suite validation without corrected reruns.

## Frozen quantitative result
The deterministic 1,000-seed synthetic benchmark code preserves baseline/fusion seed identities and matched budgets. Previous independent reproduction reported the conservative baseline at 963/1000 convergence with zero unsupported-direction decisions. Exact canonical values for the temporal-fusion candidate must be persisted after corrected pytest execution; no promotion is allowed from the old green workflow.

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
Every substantial change should answer a falsifiable question and preserve a baseline. Primary software metrics include deterministic replay, target attainment, unsupported-direction decisions, WAIT/deferral cost, convergence time, oscillation, budget use, failure identities, and regression seeds. Test discovery itself is part of the evidence chain: a green CI job is insufficient unless the intended tests are demonstrably collected and executed.

## Current blocker
Corrected pytest CI has not yet executed on the integrity-repair branch. Until it does, the repository's pytest-style research contracts are NOT YET PROVEN by CI.

## Current next move
Run corrected pytest CI unchanged. If temporal fusion fails its preregistered promotion gate, preserve the failing test and mark that intervention REJECTED. Then persist exact baseline/fusion convergence, unsupported-direction totals, recovered seeds, and regressed seeds as a deterministic artifact before designing another intervention. Biological validity remains NOT YET PROVEN regardless of simulator outcome.
