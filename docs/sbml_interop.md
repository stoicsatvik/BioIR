# SBML and Antimony interoperability boundary

BioIR uses the existing systems-biology ecosystem rather than pretending it began yesterday.

## SBML

The current backend emits a narrow structural subset of SBML Level 3 Version 2 Core:

- Model
- Compartment
- Species
- Parameter
- Reaction
- SpeciesReference
- ModifierSpeciesReference
- supported UnitDefinition entries

It intentionally omits a `KineticLaw` unless a future explicit completion profile introduces one.

If a BioIR parameter has no numerical value, structural export does not fabricate one.

## Antimony

Antimony already provides human-readable systems-biology model definitions and bidirectional translation with SBML. Current Antimony work also covers substantial SBML Level 3 functionality.

Therefore BioIR will not build a competing text syntax merely to make SBML easier to type.

The relevant comparison is instead:

```text
Can Antimony/SBML already support the same partial-model workflow,
diagnostics, and assumption audit?
```

If yes, BioIR should become a thin layer over that ecosystem.

## Current evidence

The existing toy structural SBML export has passed a libSBML consistency check with no error-severity findings.

That does not prove:

- broad SBML conformance;
- Antimony round-trip equivalence;
- preservation of every under-specified semantic;
- unique value from BioIR.

Those are now explicit benchmark targets.

## Next interoperability experiment

Build a corpus containing:

1. complete ordinary kinetic models;
2. missing parameter values;
3. known interaction topology with unknown kinetics;
4. provenance-rich models;
5. intentionally invalid unit/reference cases.

For each case compare:

- BioIR static diagnostics;
- SBML representability;
- Antimony representability;
- round-trip preservation;
- unresolved information;
- assumption/provenance retention.

The comparison decides whether BioIR remains a standalone abstraction or collapses into tooling on top of Antimony/SBML.
