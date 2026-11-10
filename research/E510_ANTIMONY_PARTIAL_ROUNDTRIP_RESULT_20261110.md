# E510 — Antimony 3 partial-model round-trip result

Date: 10 November 2026  
Workflow: [#42879788450](https://github.com/stoicsatvik/BioIR/actions/runs/42879788450)  
Branch head: `db006c97a1f58603082663b3812521febda0a435`  
Artifact: [e510-antimony-partial-model, 13792979022](https://github.com/stoicsatvik/BioIR/actions/runs/42879788450/artifacts/13792979022), SHA-256 `ffb0cffd3b400c6bb8e98c6079723972ffe9c7196ab116e2ae42cbab3fbd38a9`.

## Question

Does a partial BioIR SBML model survive an Antimony 3 import/export cycle without silently losing BioIR semantic annotations? The fixture intentionally contains an unresolved parameter and no kinetic law; it is not a complete executable biological model.

## Measurement and controls

- Antimony: **3.3.0**.
- python-libSBML: **5.21.2**.
- BioIR source SBML SHA-256: `bbad1b44c9b854beb9c04b1e4a0cfbc1e65beffbc64fa8c6a553331b844cc7d4`.
- libSBML-only parse/write control SHA-256: `2872efd3a3d27f489f685ad91bdcc3d7727da0f21d902c6b9d23d86880233a55`.
- Antimony text SHA-256: `cad7142b9c972ece91ed91d09d97c7ddac996df0f84ae2e43588c53c45d363db`.
- Antimony round-trip SBML SHA-256: `bda0cf79455b3ba3ad5b82d2a3e1687700c8201447cd1efd8e4a0729ab7f4102`.

The signature detector now parses XML expanded namespace names rather than searching serialized annotation text for a namespace URI. A regression test renames the `bioir` XML prefix and confirms that model and interaction annotations are still detected. This avoids confusing a namespace prefix with the namespace URI declaration.

A libSBML-only read/write control was added to isolate whether annotation loss originates in BioIR export, libSBML serialization, or Antimony.

## Result

<badge>Negative interoperability result</badge>

Antimony import and re-export completed with no import or round-trip error. The libSBML-only control preserved both BioIR annotations, while the Antimony round-trip did not.

| Property | Result |
|---|---|
| Core SBML structure preserved | true |
| Unresolved parameter preserved | true |
| Absence of kinetic law preserved | true |
| BioIR model annotation preserved by libSBML control | true |
| BioIR interaction annotation preserved by libSBML control | true |
| BioIR model annotation preserved by Antimony 3.3.0 | false |
| BioIR interaction annotation preserved by Antimony 3.3.0 | false |

This isolates the observed loss to the Antimony 3.3.0 import/export path for this fixture. It is not evidence that BioIR's source exporter omitted the annotations: the source signature detects both, and the libSBML-only control preserves both.

## Validation and workflow correction

- The initial workflow failed because the `pytest` console entry point did not put the repository root on `sys.path`; the test imports the `research` namespace package.
- The workflow now runs `python -m pytest`, which makes the repository root importable.
- Latest exact-head run [#42879788450](https://github.com/stoicsatvik/BioIR/actions/runs/42879788450): **3 tests passed in 0.21 s**.
- The namespace-prefix regression, positive control, libSBML-only control and pinned Antimony negative result all passed.

## Interpretation and next experiment

This is a synthetic partial-model interoperability probe only. It does not validate biological model semantics, executable completion, kinetic behavior or any production workflow.

Next, test whether Antimony supports an explicit annotation-preservation mechanism or whether a separate sidecar/rehydration adapter is required. Compare the same fixture with another SBML tool before changing BioIR's core serializer. Preserve the current negative result; do not label the Antimony round-trip loss as fixed.
