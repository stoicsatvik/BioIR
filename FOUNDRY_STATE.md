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
