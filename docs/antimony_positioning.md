# BioIR positioning after SBML + Antimony review

## Why this document exists

BioIR must not claim novelty for capabilities that the systems-biology ecosystem
already has.

SBML is an established exchange/model-definition standard with Level 3 Core and
extension packages. Antimony is an established human-readable model language
with bidirectional SBML translation and support for substantial SBML Level 3
functionality.

Therefore BioIR is **not** positioned as:

- "a readable replacement for SBML";
- "biology's LLVM";
- a new syntax for reactions, rules, events, annotations or modular models;
- a replacement for Antimony;
- a replacement for SBML;
- a generic provenance/annotation format.

Those territories already contain serious standards and tooling.

## Current candidate research delta

The remaining BioIR experiment is narrower:

> Can a biologically meaningful but mathematically incomplete model be treated as
> a first-class object, statically checked, and later completed for an
> Antimony/SBML/executable backend with every newly introduced mathematical
> assumption recorded explicitly?

The important distinction is not whether SBML or Antimony can *represent* a
particular element. They often can. The question is whether an explicit
incompleteness-and-assumption workflow is useful enough to justify separate
tooling.

## Overlap matrix

| Capability | SBML / Antimony territory | BioIR position |
| --- | --- | --- |
| Human-readable reaction syntax | Antimony already does this | not novelty |
| SBML serialization/interchange | SBML + Antimony already do this | backend/interoperability only |
| Rules, events, modularity | established modeling functionality | not novelty |
| Annotations / biological context | supported in current ecosystem | not novelty by itself |
| FBC, uncertainty distributions, layout/render | supported by SBML packages / Antimony 3 | not BioIR's target |
| Structural/unit/reference validation | partly available in existing tooling | benchmark, do not assume advantage |
| Mathematically incomplete model as an explicit workflow state | candidate question | test against existing tooling |
| Machine-readable list of unresolved mathematical commitments | candidate question | implemented experimentally |
| Assumption receipt for semantic -> executable completion | candidate question | research frontier, not proven advantage |

## Fail-closed rule

The BioIR compiler must never silently infer a kinetic law, missing parameter
value, solver semantics, or equivalent mathematical commitment.

For a partial model such as:

```text
A -> B
parameter k1 : 1/second
k1 value = unknown
kinetic law = unknown
```

BioIR should be able to validate the known structure, export structural
interoperability data where legal, and emit a completion receipt such as:

```text
unresolved:
  - parameter_value:k1
  - kinetic_law:A_to_B

introduced_assumptions: []
```

A later explicit compilation profile may resolve those items, but every
resolution must appear in the receipt.

## Kill criterion

BioIR should stop being developed as a standalone modeling language if
Antimony/SBML plus a thin validation/provenance layer can provide the same
partial-model workflow, diagnostics and assumption audit with no meaningful loss.

In that case the correct project is a tool or library **on top of** the
established ecosystem, not a competing language.

That outcome counts as successful falsification, not project failure.

## Evidence needed next

1. Encode a small corpus of deliberately incomplete models.
2. Determine exactly which are already representable in SBML and Antimony.
3. Compare diagnostics from established tooling against BioIR static checks.
4. Measure what information is lost during BioIR -> SBML -> established-tool
   round trips.
5. Add explicit completion profiles only after the unresolved commitments are
   frozen.
6. Compare whether assumption receipts add information not already preserved by
   Antimony/SBML annotations and tooling.

No novelty claim survives merely because BioIR uses different JSON keys.
