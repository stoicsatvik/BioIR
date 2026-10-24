# E208 | SBML namespace premise falsification (2026-10-24)

## Question and prior belief
E189 assumed that an SBML UnitDefinition identifier must be different from every model, species, compartment, reaction and parameter identifier. Its generated-name allocator renamed units when unrelated model symbols had the same spelling.

**That premise is REJECTED.** SBML Level 3 Version 2 Core §3.3.1 distinguishes the **SId** namespace (Model, Compartment, Species, Parameter, Reaction, etc.) from the **UnitSId** namespace (UnitDefinition). A UnitDefinition may legally reuse a species or parameter identifier. By contrast, the model's own SId must be unique among model components.

Primary specification: https://sbml.org/specifications/sbml-level-3/version-2/core/release-1/sbml-level-3-version-2-core.pdf

## Discriminating tests and preserved negative evidence
- Four synthetic counterexamples set the model ID equal to, respectively, a compartment, species, parameter and reaction ID. The previous semantic validator accepted all four even though the shared SId namespace forbids them.
- A fifth synthetic model uses the same string in UnitSId and SId roles. The old exporter renamed valid UnitDefinition IDs despite no actual namespace conflict.
- The pre-fix test-only commit `2b27ec6fa86946d0c8db1a4d13f2352602bd2c55` failed **5 tests** in Actions run 40071109685: four missing model-ID duplicate checks and one needless unit renaming assertion. This is the preserved falsification, not an implementation win.
- Independent `libsbml` consistency checking is exercised when the optional dependency is available; the new test specifically rejects a duplicate-SId rule violation rather than treating warnings as equivalent to errors.

## Correction
1. Register the model ID in the semantic validator's shared SId symbol table.
2. Emit canonical UnitDefinition IDs without renaming them merely because an unrelated SId matches.
3. Preserve the original unit meaning and parameter unit references; maintain deterministic export.
4. Replace E189's incorrect model-wide ID uniqueness assertion with **separate** SId and UnitSId uniqueness checks.

Exact-head CI run 40071139164 passed at `794b71dfef542a1bb3fb98ad6f25e0ce6c88bd03`, including the revised namespace regressions. Subsequent documentation commits require their own final-head validation.

## Claim boundaries
- **SUPPORTED:** model/component SId collision detection and legal UnitSId/SId reuse on the synthetic cases and CI implementation.
- **REJECTED:** E189's claim that cross-namespace spelling collisions themselves make SBML invalid.
- **NOT YET PROVEN:** broad SBML/Antimony round-trip equivalence, interoperability on an independent model corpus, biological fidelity or a novel BioIR abstraction advantage.
- The current BioIR research direction remains incomplete-model semantics with explicit assumptions; conventional SBML/Antimony is prior art.

No biological wet lab, patient data, clinical treatment or autonomous actuation.
