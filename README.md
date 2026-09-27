# BioIR

**BioIR is an experimental, user-facing semantic model for biological systems with explicit compile-time lowering into simulation and interoperability backends.**

The central design has changed:

```text
user works with BioIR semantic model
              ↓
      static model checks
              ↓
     compile-time lowering
              ↓
   SBML / simulator / backend
```

The BioIR abstraction is not supposed to be hidden behind another modeling language. It is the representation the user directly authors and inspects.

## Why this boundary

A biological model should be able to carry compartments, entities, units, parameters, interaction topology, stoichiometry and provenance **before** committing to one mathematical realization.

That enables checks such as:

- does every entity live in a real compartment?
- are identifiers unique and portable?
- do concentration variables actually use concentration units?
- do interactions reference existing entities and parameters?
- is stoichiometry positive?
- is provenance present?

Only after those checks does a backend choose how to lower the model.

## Semantic model v1

A small example:

```json
{
  "version": "bioir/semantic/v1",
  "name": "toy_conversion",
  "compartments": [
    {"id": "cell", "size": 1.0, "unit": "litre"}
  ],
  "entities": [
    {
      "id": "substrate",
      "compartment": "cell",
      "initial_value": 1.0,
      "quantity_kind": "concentration",
      "unit": "mole_per_litre"
    },
    {
      "id": "product",
      "compartment": "cell",
      "initial_value": 0.0,
      "quantity_kind": "concentration",
      "unit": "mole_per_litre"
    }
  ],
  "parameters": [
    {"id": "k1", "value": 0.1, "unit": "per_second"}
  ],
  "interactions": [
    {
      "id": "conversion_1",
      "kind": "conversion",
      "inputs": [{"entity": "substrate"}],
      "outputs": [{"entity": "product"}],
      "parameter_refs": ["k1"]
    }
  ]
}
```

Notice what is missing: there is no ODE and no rate-law expression.

In `bioir/semantic/v1`, embedding fields such as `rate_law`, `kinetic_law`, `ode`, `math` or `mathml` in the user model is rejected. Mathematical commitment belongs at the lowering boundary.

## Check before simulation

```bash
python -m bioir check-model examples/toy_semantic_model.json
```

BioIR runs static structural and dimensional checks without needing a simulator.

## SBML interoperability

The first lowering backend exports a structural SBML Level 3 Version 2 Core document:

```bash
python -m bioir export-sbml examples/toy_semantic_model.json --out model.xml
```

The current exporter preserves:

- compartments;
- species;
- initial amount/concentration semantics;
- parameters and supported units;
- reactions and stoichiometry;
- modifiers;
- BioIR interaction metadata and parameter references.

It intentionally emits **no kinetic law by default**. That is how the current experiment tests delayed commitment to mathematical representation.

This exporter is a bounded interoperability prototype. Full conformance against established SBML validation tooling is the next gate, not something this README gets to declare by confidence.

## Existing controller research

The earlier BioIR v0 synthetic controller is preserved.

```text
objective/state/constraint model
              ↓
SENSE / INCREASE / DECREASE / MAINTAIN / WAIT
              ↓
synthetic closed-loop runtime
```

The old CLI remains available:

```bash
python -m bioir compile examples/toy_homeostasis.json
python -m bioir simulate examples/toy_homeostasis.json
```

Those controller experiments are now treated as one downstream research path, not the definition of the entire abstraction.

The rejected temporal-fusion result is also preserved. BioIR does not rewrite failed experiments because a newer architecture is more attractive.

## Safety boundary

BioIR remains modeling/simulation-only. It does not generate wet-lab protocols, synthesis-ready biological sequences, pathogen optimization, patient-specific treatment instructions, or autonomous physical actuation.

## Current research question

The next falsifiable question is:

> Can a typed, user-facing biological abstraction catch useful errors before simulation and lower reproducibly into established representations such as SBML without forcing the user to commit prematurely to one mathematical form?

That is a much narrower claim than “a universal programming language for biology,” which is convenient because reality tends to punish slogans eventually.

## License

Apache-2.0. See `LICENSE`.
