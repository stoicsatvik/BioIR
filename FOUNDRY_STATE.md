# Unified Foundry State — BioIR

## Mission

Build a safe, user-facing biological abstraction that preserves biological structure, units, metadata and provenance, performs useful checks before simulation, and lowers explicitly into established modeling/simulation backends without silently committing the user to one mathematical representation.

## Claim status

NOT YET PROVEN as a biologically valid abstraction or control layer. The repository supports software/modeling experiments only.

The historical controller research remains part of the evidence record:

- corrected CI preserved the frozen 1,000-seed temporal-fusion result;
- baseline convergence: 963/1000;
- temporal fusion convergence: 876/1000;
- unsupported-direction decisions: 0 for both;
- the temporal-fusion intervention remains REJECTED by its frozen promotion rule;
- the rejected 0..999 seed population must not be reused for tuning.

Negative evidence is retained.

## Architecture revision — 2026-09-27

BioIR is being re-centered around a stronger abstraction boundary:

```text
user-facing semantic model
        ↓
static checks
        ↓
compile-time lowering
        ↓
SBML / simulator / future backend
```

The abstraction itself is what the user should work with. A hidden internal IR sitting beneath another user model is no longer the architectural goal.

The semantic layer should preserve biological meaning while delaying commitment to a particular mathematical realization until compilation.

## Semantic model v1 — current branch

Branch: `foundry/semantic-model-sbml-v1`

Added:

- typed compartments;
- biological entities;
- amount/concentration semantics;
- explicit units;
- parameters;
- interaction topology;
- stoichiometry;
- modifiers;
- provenance;
- static reference/unit/model checks;
- structural SBML Level 3 Version 2 lowering;
- deliberate omission of kinetic laws by default;
- CLI model checking and SBML export;
- deterministic tests for delayed mathematical commitment.

Status: UNDER VALIDATION until exact-head CI executes.

## Mathematical commitment boundary

`bioir/semantic/v1` rejects embedded `rate_law`, `kinetic_law`, `ode`, `math` and `mathml` fields in interactions.

A later backend profile may introduce mathematics, but that assumption must be explicit at compile time and must not be confused with biology-level semantics.

## SBML boundary

SBML is treated as an interoperability/lowering target, not something BioIR needs to replace.

The current exporter covers a narrow structural subset: model, compartments, species, parameters, reactions, species references, modifier references and supported unit definitions.

Full SBML conformance has NOT YET BEEN VALIDATED against established external tooling.

## Existing controller stack

The legacy synthetic controller path remains preserved:

```text
objective/state/constraint model
  ↓
uncertainty-aware compiler/controller
  ↓
SENSE / INCREASE / DECREASE / MAINTAIN / WAIT
  ↓
synthetic closed-loop runtime
```

It is now treated as one downstream research path rather than the entire definition of BioIR.

## Hard boundary

BioIR remains simulation/modeling-first and safety-constrained.

- No nucleotide-sequence generation for harmful biological engineering.
- No pathogen engineering or optimization.
- No wet-lab procedural protocols.
- No autonomous real-world biological actuation.
- No human/animal experimentation instructions.
- No patient-specific treatment or clinical decision system.
- Computational success must never be promoted as organism-level or clinical evidence.

## Evaluation doctrine

Every substantive change should answer a falsifiable question and preserve failures.

For the semantic-model frontier, primary software questions are:

1. Can malformed references and unit mismatches be caught before simulation?
2. Can one user-facing semantic model lower deterministically?
3. Does lowering preserve compartments, entities, quantities, interactions and metadata?
4. Can mathematical assumptions remain absent until an explicit compilation profile introduces them?
5. Can generated SBML pass established external validation without weakening the semantic contract?

## Current blocker

The semantic/SBML architecture is not externally validated yet. Repository tests can prove our own structural contract, not full SBML interoperability.

## Current next move

Validate the new semantic-model tests in CI. Then run generated documents through established SBML tooling and use any failures to tighten the exporter. After that, add explicit compile-time kinetics profiles with assumption/provenance receipts rather than embedding mathematics back into the user model.
