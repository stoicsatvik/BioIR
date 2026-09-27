# BioIR architecture

BioIR's primary abstraction is now the **model the user works with**, not a hidden compiler-only IR.

The design rule is:

```text
user-facing biological semantics
        ↓
static checks and metadata validation
        ↓
compile-time lowering boundary
        ↓
SBML / simulator representation / future backend
```

The semantic layer should preserve biological meaning while delaying commitment to a particular mathematical representation until a backend actually needs one.

## User-facing semantic model

`bioir/semantic/v1` represents:

- compartments;
- biological entities;
- initial quantities;
- amount/concentration semantics;
- explicit units;
- parameters as named metadata;
- interaction topology;
- stoichiometry;
- modifiers;
- constraints implied by typed references;
- provenance.

The semantic model deliberately does **not** contain an ODE, MathML expression, rate law or backend-specific solver choice. In v1, trying to place fields such as `rate_law`, `kinetic_law`, `ode` or `math` inside an interaction is rejected.

This is intentional. The user authors the biology-level representation; a later lowering profile chooses the mathematics.

## Static model checks

Before any simulation or backend lowering, BioIR checks:

1. identifier portability and collisions;
2. compartment existence;
3. reference integrity;
4. finite/non-negative initial quantities;
5. finite parameter values;
6. positive stoichiometry;
7. quantity-kind/unit dimensional compatibility;
8. parameter references;
9. provenance presence as a warning.

The current unit system is deliberately small and explicit. It is a compiler contract, not an attempt to replace a real ontology.

## Compile-time lowering

A backend receives a validated semantic model and chooses how to represent it.

The first interoperability backend emits a structural **SBML Level 3 Version 2 Core** document containing compartments, species, parameters and reactions.

Crucially, the default SBML backend emits **no kinetic law**. Interaction topology and parameter references are preserved, while mathematical kinetics remain uncommitted. A future compilation profile can choose a mathematical realization explicitly and audibly.

## Relationship to existing BioIR controller work

The earlier v0 controller path remains preserved:

```text
objective/state model
  ↓
SENSE / INCREASE / DECREASE / MAINTAIN / WAIT
  ↓
synthetic closed-loop runtime
```

That work is still useful for uncertainty and controller falsification experiments, but it is no longer the whole definition of BioIR.

Architecturally, it becomes one possible downstream research path rather than the user-facing abstraction itself.

## Backend contract

Backends must:

- consume a statically valid semantic model;
- declare what mathematical assumptions they introduce;
- preserve provenance;
- fail closed when required semantics cannot be represented;
- never silently change units or identifiers;
- keep real-world actuation outside this repository.

## Safety boundary

BioIR remains simulation/modeling-only. It does not emit wet-lab procedures, biological sequences for synthesis, pathogen optimization, patient-specific treatment instructions, or autonomous physical actuation.

## Next technical milestones

1. compile-time kinetics profiles with explicit assumption receipts;
2. round-trip checks against established SBML tooling;
3. richer unit definitions and ontology references;
4. semantic equivalence tests across multiple backends;
5. provenance receipts for every lowering decision;
6. explicit model uncertainty that survives lowering;
7. a compact textual syntax over the same semantic model, rather than a second hidden representation.
