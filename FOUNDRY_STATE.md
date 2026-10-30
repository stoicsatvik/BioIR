# Unified Foundry State — BioIR

## Mission

Test whether mathematically incomplete but biologically meaningful models can be
validated, preserved, and completed into established systems-biology
representations with every newly introduced mathematical assumption explicitly
audited.

## Claim status

**NOT YET PROVEN.**

BioIR no longer claims novelty for human-readable biological modeling, SBML
interchange, annotations, modularity, rules, events, or other territory already
covered by SBML/Antimony tooling.

The current novelty hypothesis is narrower and may still fail.

## External-feedback revision — 2026-09-28

Two systems-biology experts materially changed the project boundary:

1. The user-facing abstraction should not be a hidden IR, and mathematical
   representation should be delayed until needed.
2. Antimony is direct prior art for human-readable SBML-oriented model
   definitions, so BioIR must compare against it rather than reinvent it.

Resulting architecture:

```text
partial biological semantics
        ↓
structural/unit validation
        ↓
unresolved commitment receipt
        ↓
explicit completion profile (future)
        ↓
assumption receipt
        ↓
Antimony / SBML / executable backend
```

## What was removed from the novelty claim

BioIR does not claim novelty for:

- human-readable reaction syntax;
- SBML conversion/interchange;
- model modularity;
- rules/events;
- annotations by themselves;
- FBC support;
- uncertainty/distribution syntax;
- layout/render;
- generic systems-biology model authoring.

See `docs/antimony_positioning.md`.

## Semantic-model frontier

Branch: `foundry/semantic-model-sbml-v1`

Current capabilities:

- typed compartments and biological entities;
- amount/concentration semantics;
- explicit units;
- parameters whose numerical values may remain unresolved;
- interaction topology and stoichiometry;
- modifiers and provenance;
- static reference/unit/model checks;
- structural SBML Level 3 Version 2 lowering;
- omission of unknown parameter values rather than fabrication;
- deliberate omission of kinetic laws;
- deterministic model fingerprinting;
- fail-closed completion planner;
- machine-readable unresolved mathematical commitments.

## Completion receipt invariant

For an under-specified model, the planner records what is missing before a
kinetic/executable backend can exist.

Example:

```text
parameter_value:k1
kinetic_law:A_to_B
```

The current planner introduces **zero assumptions automatically**.

Any future completion profile must record exactly which commitments it resolves
and what assumption supplied the missing mathematics.


## Human / AI readability invariant

The canonical semantic model remains structured data, but every scientifically
important state must also have a deterministic plain-text rendering that a
person or AI system can inspect directly.

Current readable views expose:

- compartments and entities;
- units and initial quantities;
- parameter values or explicit `unresolved` state;
- interaction topology;
- unresolved kinetic laws;
- provenance;
- model fingerprint;
- unresolved commitments;
- introduced assumptions.

The renderer is a view of the canonical model/receipt, **not a new modeling
language**. BioIR must not recreate Antimony merely to satisfy readability.

CLI:

```bash
python -m bioir show-model examples/underspecified_conversion.json
python -m bioir plan-completion examples/underspecified_conversion.json --format text
```

## SBML / Antimony boundary

SBML is an interoperability target.

Antimony is established prior art and a likely downstream/human-facing layer,
not something BioIR should reimplement.

The existing structural SBML example has passed libSBML consistency validation.
This does not establish broad round-trip preservation or unique BioIR value.

## Kill criterion

If Antimony/SBML plus a thin validation/provenance layer can provide equivalent:

- partial-model representation;
- static diagnostics;
- unresolved-commitment tracking;
- assumption auditing;
- round-trip preservation;

then BioIR should stop being developed as a standalone language.

The surviving project would become tooling on top of the established ecosystem.

## Historical controller evidence

The earlier synthetic controller research remains preserved:

- baseline convergence: 963/1000;
- temporal-fusion convergence: 876/1000;
- unsupported-direction decisions: 0 for both;
- temporal-fusion intervention remains REJECTED by its frozen promotion rule.

That negative evidence is unrelated to the Antimony/SBML positioning change and
must remain visible.

## Current evaluation plan

1. Build a frozen corpus of complete, partial, and intentionally invalid models.
2. Test direct representability in SBML and Antimony.
3. Compare diagnostics against established tooling.
4. Round-trip models and measure semantic loss.
5. Measure whether explicit unresolved-commitment receipts add information.
6. Only then implement completion profiles.
7. If the assumption-audit layer provides no meaningful advantage, collapse
   BioIR into an Antimony/SBML tooling layer.

## Hard boundary

BioIR remains modeling/simulation-only.

- No harmful biological sequence generation.
- No pathogen engineering or optimization.
- No wet-lab procedural protocols.
- No autonomous real-world biological actuation.
- No patient-specific treatment or clinical decision system.

## 2026-10-25: E229 nonfinite objective-tolerance false convergence

**Pre-fix falsification:** BioIR v0 accepted an objective with `tolerance=Infinity` and `state.x=0, target.x=1`; the synthetic runtime could mark this maximally wrong state converged at step zero. NaN tolerance was also accepted, leading to non-convergent comparisons. A test-only PR commit `1c9fa2cfde46e860ddc70ccb815410ec2eb7d765` produced expected-red [CI 40121341687](https://github.com/stoicsatvik/BioIR/actions/runs/40121341687): 3 failed, 67 passed, 2 skipped.

**Correction:** `validate_program` now requires finite, strictly positive objective tolerances; compiler and runtime inherit the same fail-closed validation. [Exact-head CI 40121419724](https://github.com/stoicsatvik/BioIR/actions/runs/40121419724) at `e53d35fd599263632da72b4ec703657ddbcbce30`: 70 passed, 2 skipped, semantic-model/SBML job passed.

**Claim:** Numerical validation boundary SUPPORTED IN SOFTWARE TESTS. This is not evidence of biological controllability, SBML round-trip completeness, or unique value over Antimony. The central novelty hypothesis remains NOT YET PROVEN. **Next scientific move:** direct comparison of partial-model assumption receipts against Antimony/SBML on independently frozen model examples, not further generic compiler scaffolding.

## 2026-10-25: E267 SBML Core unresolved-key reconstruction

Six frozen safe synthetic structural models were exported to SBML Level 3 Core, parsed by libSBML, stripped of BioIR-specific annotation elements/attributes, serialized, and reparsed. All six BioIR `parameter_value:<id>` and `kinetic_law:<id>` unresolved-key sets were reconstructed exactly using only standard SBML presence bits. [Exact-head CI 40212759770](https://github.com/stoicsatvik/BioIR/actions/runs/40212759770) passed both jobs; immutable JSON artifact 12605943062. Details: `research/E267_SBML_CORE_RECEIPT_FALSIFICATION.md`.

**Claim update:** Enumeration of missing parameter-value and kinetic-law keys is **not unique** to BioIR for the tested corpus. This is evidence *against* the standalone-language novelty thesis, not proof of full equivalence to Antimony/SBML or the broader assumption-audit workflow. The central BioIR novelty remains **NOT YET PROVEN**.

**Highest-EV next:** Head-to-head standards-based thin receipt vs BioIR on explicit assumption introduction, parameter/reaction intent, provenance, and semantic round-trip loss. If no differential value survives, collapse BioIR into an established SBML/Antimony tooling layer. No biological wet-lab or clinical action.

## 2026-10-26: E284 SBML Core plus thin-sidecar novelty falsification

On six safe synthetic structural models, annotation-free SBML Core plus a small
source-derived metadata sidecar reconstructed **6/6 current unresolved receipts**
(excluding policy prose). Four of six one-field variants (provenance source/notes,
interaction kind/parameter references) were **indistinguishable in Core alone**
but distinguishable by the sidecar; two standard-Core controls changed Core.
An accidental Core/sidecar mismatch was detected by a pairing digest. Exact-head
initial CI run 40270102419 SUCCESS, two jobs; immutable artifact 12627808897.
See `research/E284_SBML_SIDECAR_NOVELTY_FALSIFICATION.md` and draft PR #18.

**Claim:** Core-only semantic-intent loss and current thin-sidecar representability
SUPPORTED IN SYNTHETIC TESTS. Standalone BioIR novelty **NOT YET PROVEN**;
this is further negative evidence against inventing a new language.
**Crucial limitation:** the sidecar is generated from BioIR source and carries
its fingerprint; every introduced-assumption list is empty. No completion
profiles, real biological models, independent Antimony round trip, or verified
assumption-audit advantage were tested.

**Next:** one frozen hypothetical completion-profile assumption-audit comparison
against SBML/Antimony + a thin independent provenance layer; collapse to
standards-based tooling if the latter is equivalent. Remain simulation-only.


## 2026-10-26: E303 explicit-assumption standards-based falsification

E284's zero-assumption result was extended with two independently specified, **hypothetical** parameter/kinetic-law completion profiles (k1=0.1 and 0.2; MathML k1*A*cell). Annotation-free SBML Core plus a thin receipt sidecar represented both, matched BioIR's two unresolved commitment keys, and rejected swapped Core/sidecar, altered parameter values, and altered kinetic MathML. The deliberately spoofed hypothetical origin label **was accepted**: content hashes do not authenticate provenance. All examples are synthetic, with no measured biological kinetics.

E303 [draft PR #19](https://github.com/stoicsatvik/BioIR/pull/19), stacked on E284 #18. [Exact-head Actions 40342916806](https://github.com/stoicsatvik/BioIR/actions/runs/40342916806) SUCCESS at 73df1de19e295d38e5b3bc03cd9cfe853ad8a844: 4 focused tests, 2/2 libSBML reparses, unit suite 83 passed / 4 skipped; [artifact 12659922223](https://github.com/stoicsatvik/BioIR/actions/runs/40342916806/artifacts/12659922223).

**Claim:** Thin-sidecar introduced-assumption *representability and content checking* SUPPORTED FOR TWO SYNTHETIC PROFILES. Independently authenticated assumption provenance NOT YET PROVEN. Standalone BioIR language novelty NOT YET PROVEN. No Antimony parity or scientific validity demonstrated. **Next:** independently authored real-model SBML/Antimony comparison with externally verifiable assumption provenance; collapse into standards tooling if no distinct capability survives.


## 2026-10-28 E354: layout-only SBML receipt false rejection

An ordinary XML pretty-print of the E303 synthetic completed SBML Core, with
a correctly recomputed receipt digest and no changed assumptions, was
incorrectly rejected by the E338 verifier. Test-first CI
[40638397736](https://github.com/stoicsatvik/BioIR/actions/runs/40638397736)
failed at the reindentation control. Narrow element-only SBML/MathML
whitespace normalization fixed the false rejection while retaining
undeclared species and MathML mutation rejection. Exact-head CI
[40638435163](https://github.com/stoicsatvik/BioIR/actions/runs/40638435163)
passed; see `research/E354_SBML_LAYOUT_EQUIVALENCE_20261028.md` and
draft PR #21. **Claim:** narrow XML layout tolerance SUPPORTED IN TESTED
SOFTWARE; independent standards round-trip equivalence, provenance
authenticity, biological validity and standalone BioIR novelty NOT YET PROVEN.
Next: independent libSBML/Antimony round-trip and mixed-content adversarial
tests, with standards integration preferred over duplicating prior art.


## 2026-10-30 E401: content receipt does not certify SBML semantics

On the frozen synthetic under-specified conversion fixture, a hypothetical completed
kinetic law with an undefined MathML identifier was accepted by the unchanged
E303/E381 content receipt after the declared MathML and XML digest were both
updated. Independent libSBML 5.21.2 `checkConsistency` flagged that exact
undefined symbol. This is a measured **content-versus-semantics contract gap**,
not an undocumented regression: `verify_receipt` checks hash-bound declared
changes, not complete SBML semantics. Treating it as an executable-model
certificate would be unjustified.

[E401 exact-code Actions #40958356283](https://github.com/stoicsatvik/BioIR/actions/runs/40958356283)
SUCCESS at `b548995e65adc0e6fbd1bf44d756e7d9b7e164c8`:
2/2 focused tests and 11/11 inherited E303/E338/E381 controls.
Report: `research/E401_SBML_UNDEFINED_SYMBOL_NEGATIVE_CONTROL_20261030.md`.
Draft PR #25 stacked on E381 #24. **Claim:** content/semantic boundary
SUPPORTED IN SYNTHETIC SOFTWARE TESTS; standalone BioIR novelty, authenticated
provenance, general SBML/Antimony equivalence and biological validity
**NOT YET PROVEN**. Next: independently authored standards-model corpus,
with separate content, semantic and origin validation baselines.


## 2026-10-30 E423: independently authored SBML stoichiometric baseline

Official SBML Test Suite commit `d6dcd2cc6408d5eb881638ac6ce7a05fd7d2e4d1`, semantic cases 00001–00003, provided three unchanged Level 3 Version 2 models and 153 published reference timepoints. For cases 00001 and 00002 (one product per reactant), naive S1+S2 is conserved to floating-point precision. In case 00003 (two products per reactant), naive S1+S2 changes by 99.3262053% of initial S1 by t=5, while S1+S2/2 remains conserved within 3.47e-18 absolute error. The conventional analytical trajectory agrees within 6.94e-18 absolute error. Six isolated offline Python tests passed locally; full exact committed-source CI was not executed. See `research/E423_INDEPENDENT_SBML_STOICHIOMETRY_20261030.md`.

**Claim:** naive species-sum conservation as a general SBML semantic invariant REJECTED FOR THESE PUBLISHED MODELS; stoichiometric invariant and analytic baseline SUPPORTED ON THIS FROZEN FAMILY. These are published simulation reference trajectories, not biological measurements. BioIR standalone novelty, broad standards equivalence and biological validity NOT YET PROVEN. Next: larger independent valid/invalid standards corpus, libSBML/Antimony comparisons and assumption-receipt differential value. No live actuation.
