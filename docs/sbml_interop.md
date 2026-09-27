# SBML interoperability boundary

BioIR uses SBML as an interoperability target, not as an enemy to replace.

The current backend emits a narrow structural subset of SBML Level 3 Version 2 Core:

- Model
- Compartment
- Species
- Parameter
- Reaction
- SpeciesReference
- ModifierSpeciesReference
- UnitDefinition where a supported derived parameter unit requires one

The exporter intentionally omits `KineticLaw` by default.

That omission is a feature of the experiment: the user-facing semantic model records biological topology and metadata without prematurely selecting a mathematical rate expression. A later compile-time profile must make that commitment explicitly.

## Current evidence boundary

The repository tests XML structure, deterministic serialization, unit/reference checks and the absence of hidden kinetic-law commitment. It does **not** yet claim full conformance against every SBML rule or package.

The next interoperability gate is to validate generated documents with established SBML tooling and preserve all failures rather than teaching the tests to like our XML.
