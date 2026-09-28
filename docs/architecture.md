# BioIR architecture

## Architecture after SBML / Antimony review

BioIR is no longer framed as a new high-level biological modeling language.

Antimony and SBML already cover substantial territory around human-readable model specification, model exchange, annotations, modularity, events, rules, and multiple SBML Level 3 modeling features.

The current architecture therefore focuses only on the boundary that still needs to be tested:

```text
biologically meaningful partial model
        ↓
static validity checks
        ↓
explicit unresolved commitments
        ↓
completion profile (future)
        ↓
assumption receipt
        ↓
Antimony / SBML / simulator
```

## Two kinds of failure

BioIR now distinguishes:

### 1. Invalid structure

Examples:

- reference to a missing species;
- invalid compartment;
- incompatible units;
- duplicate identifiers;
- invalid stoichiometry.

These are hard errors.

### 2. Valid but incomplete mathematics

Examples:

- a parameter has identity and units but no numerical value;
- an interaction is known biologically but no kinetic law has been chosen.

These can remain valid semantic-model states.

They block an executable kinetic backend, but they should not be disguised as structural corruption.

## Completion planner

`bioir.completion.plan_executable_completion` produces an `AssumptionReceipt`.

The first version is deliberately conservative:

- it fingerprints the exact semantic model;
- lists missing parameter values;
- lists interactions whose kinetic laws remain unresolved;
- records **zero introduced assumptions**;
- never guesses a mathematical law.

This is intentionally less impressive than an auto-model generator. It is also considerably harder to lie with.


## Human / AI readability invariant

The canonical representation may be structured, but no scientifically important
state should be visible only through internal object graphs or opaque compiler
metadata.

BioIR therefore requires deterministic plain-text views for:

- the biological model;
- unresolved mathematical commitments;
- introduced assumptions;
- provenance and model fingerprint.

The renderer is deliberately a **view**, not another language. This avoids
recreating Antimony while still making the model and compiler decisions legible
to humans and AI systems.

A change is incomplete if structured output changes but the readable audit no
longer exposes the same scientific meaning.

## Future completion profiles

A future profile may choose mathematics, for example a particular kinetic form.

Such a profile must record:

- which model fingerprint it acted on;
- which commitment it resolved;
- the exact assumption introduced;
- the source of that assumption;
- any new parameter/value required;
- the downstream target.

A completed model without that receipt violates the architecture.

## Interoperability

SBML and Antimony are established ecosystem components, not competitors to defeat.

BioIR's current structural SBML exporter exists to test preservation and interoperability.

Antimony should be evaluated as a likely human-facing/downstream representation rather than reimplemented.

## Kill criterion

If existing Antimony/SBML tooling plus a thin validation/provenance library can:

- represent the same partial models;
- surface equivalent diagnostics;
- preserve unresolved commitments;
- record completion assumptions;

with no meaningful disadvantage, BioIR should stop existing as a standalone language.

The useful artifact would then be the validation/assumption-audit layer itself.

## Historical controller work

The v0 synthetic controller experiments remain preserved as a separate research line. Their positive and negative results must not be rewritten to fit the new modeling architecture.
