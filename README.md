# BioIR

**BioIR is an experiment in representing biologically meaningful but mathematically incomplete models without silently inventing the missing mathematics.**

After comparing the project against SBML and Antimony, BioIR is **not** positioned as a new human-readable modeling language or as a replacement for either standard.

The current research boundary is:

```text
partial biological semantics
        ↓
static structural / unit checks
        ↓
completion plan
        ↓
explicit assumption receipt
        ↓
Antimony / SBML / executable backend
```

## What BioIR is not trying to reinvent

Antimony already provides a human-readable systems-biology language with bidirectional SBML translation and substantial SBML Level 3 support. SBML already provides the core exchange/model representation plus packages for additional modeling formalisms.

BioIR therefore does **not** claim novelty for:

- human-readable reaction syntax;
- SBML interchange;
- rules or events;
- model modularity;
- biological annotations by themselves;
- uncertainty/distribution syntax;
- layout/render support;
- flux-balance modeling.

See `docs/antimony_positioning.md` for the explicit overlap and kill criteria.

## Current hypothesis

The narrower question is:

> Can a partial biological model remain useful before it is mathematically complete, and can every assumption introduced while making it executable be exposed and audited?

A model can therefore state:

- compartments and entities;
- interaction topology;
- units;
- stoichiometry;
- parameter identity and units;
- provenance;

while intentionally leaving a parameter value or kinetic law unresolved.

For example:

```json
{
  "version": "bioir/semantic/v1",
  "name": "underspecified_conversion",
  "compartments": [
    {"id": "cell", "size": 1.0, "unit": "litre"}
  ],
  "entities": [
    {
      "id": "A",
      "compartment": "cell",
      "initial_value": 1.0,
      "quantity_kind": "concentration",
      "unit": "mole_per_litre"
    },
    {
      "id": "B",
      "compartment": "cell",
      "initial_value": 0.0,
      "quantity_kind": "concentration",
      "unit": "mole_per_litre"
    }
  ],
  "parameters": [
    {"id": "k1", "unit": "per_second"}
  ],
  "interactions": [
    {
      "id": "A_to_B",
      "kind": "conversion",
      "inputs": [{"entity": "A"}],
      "outputs": [{"entity": "B"}],
      "parameter_refs": ["k1"]
    }
  ]
}
```

The missing `k1` value is not automatically filled in. A kinetic law is not inferred.

## Static validation

```bash
python -m bioir check-model examples/underspecified_conversion.json
```

Structural invalidity remains an error. Mathematical incompleteness is reported separately when it can legally remain unresolved.

Examples of structural checks include:

- invalid or duplicate identifiers;
- unknown compartments;
- broken entity/parameter references;
- incompatible quantity units;
- invalid stoichiometry;
- non-finite supplied values.

## Completion receipt

```bash
python -m bioir plan-completion examples/underspecified_conversion.json
```

The planner emits a deterministic receipt containing the model fingerprint and unresolved commitments, for example:

```text
unresolved:
  parameter_value:k1
  kinetic_law:A_to_B

introduced_assumptions: []
```

The important invariant is that **BioIR does not silently convert missing biological knowledge into mathematical certainty**.

A future explicit compilation profile may resolve those commitments, but each added assumption must be recorded.


## Human / AI readable views

The canonical model remains structured data, but important semantics must not be
hidden inside compiler internals.

Render a deterministic plain-text view with:

```bash
python -m bioir show-model examples/underspecified_conversion.json
```

The output exposes compartments, entities, units, parameters, interactions,
provenance, and unresolved mathematics in ordinary text.

The same rule applies to completion receipts:

```bash
python -m bioir plan-completion examples/underspecified_conversion.json --format text
```

This produces a human/AI-readable audit such as:

```text
Still unresolved:
- parameter_value:k1
- kinetic_law:A_to_B

Compiler assumptions introduced:
- none
```

These renderings are **views of the canonical structured model and receipt**,
not a second modeling language. The JSON remains the machine-stable source of
truth; the text view exists so a person or AI system can inspect the same
semantics without reverse-engineering internal objects.

## Structural SBML export

```bash
python -m bioir export-sbml examples/underspecified_conversion.json --out model.xml
```

The current exporter preserves compatible structure without inventing missing parameter values or a `KineticLaw`.

This makes SBML an interoperability target, not an adversary.

The existing exporter has already been checked with libSBML on the current toy model. Broader round-trip equivalence is still an open experiment.

## Antimony relationship

Antimony is treated as established prior art and a likely downstream/interoperability layer.

BioIR must earn its existence by demonstrating value around explicit incompleteness, diagnostics, and assumption auditing that is not already handled adequately by Antimony/SBML tooling.

If a thin Antimony/SBML-based layer can provide the same workflow, BioIR should collapse into that layer rather than become another language.

## Existing controller research

The historical BioIR v0 controller experiments are preserved, including the rejected temporal-fusion result. They are evidence, not the current definition of the project.

```bash
python -m bioir compile examples/toy_homeostasis.json
python -m bioir simulate examples/toy_homeostasis.json
```

## Current falsifiable questions

1. Which incomplete BioIR models are already representable directly in Antimony/SBML?
2. Which diagnostics are genuinely missing from established tooling?
3. Does a machine-readable unresolved-commitment receipt add useful information?
4. Can partial models round-trip through established tooling without semantic loss?
5. Can explicit completion profiles make models executable while preserving an auditable assumption trail?

Until those tests are answered, BioIR has **no novelty claim** beyond being an experimental hypothesis.

## Safety boundary

BioIR remains modeling/simulation-only. It does not generate wet-lab protocols, synthesis-ready biological sequences, pathogen optimization, patient-specific treatment instructions, or autonomous physical actuation.

## License

Apache-2.0. See `LICENSE`.
