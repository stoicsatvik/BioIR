# E284 | Annotation-free SBML Core versus a minimal provenance/intent sidecar

**Date:** 2026-10-26. **Synthetic structural-model research only.** No biological observations, wet-lab procedures, pathogen work, clinical treatment or autonomous actuation.

## Question

Does the *currently implemented* BioIR unresolved-commitment receipt require a standalone modeling language, or can established SBML Level 3 Version 2 Core plus a small explicit metadata sidecar represent the same fields?

The comparison uses libSBML, removes all BioIR-specific model/reaction annotations, serializes and reparses the result, and reconstructs missing parameter values and kinetic laws from standard Core presence bits. A sidecar contains only non-Core provenance, interaction intent, a source fingerprint, and a hash binding it to the stripped Core. The sidecar is derived from the original BioIR source, **not** independently recovered.

## Predeclared cases and results

Six inherited E267 synthetic partial models were evaluated. The thin-Core-plus-sidecar baseline reconstructed the current receipt fields (excluding an explanatory policy string) exactly in **6/6** cases.

Six one-field variants of a frozen partial model tested what Core loses:

| Perturbation | Annotation-free Core identical? | Sidecar distinguishes? |
|---|---|---|
| Provenance notes | **Yes** | Yes |
| Provenance source | **Yes** | Yes |
| Interaction kind | **Yes** | Yes |
| Interaction parameter references | **Yes** | Yes |
| Reaction name (positive control) | No | Yes |
| Parameter numerical value (positive control) | No | Yes |

**Four of six distinct source-model pairs collapse to identical annotation-free SBML Core.** The sidecar distinguishes all six. A deliberately mismatched Core/sidecar pair was rejected by a deterministic SHA-256 pairing check.

These are software/representation results, not evidence that either model is biologically correct. Core-only loss is expected for annotations; it is not a defect in the SBML standard.

## Interpretation

- **SUPPORTED FOR THIS SYNTHETIC CORPUS:** BioIR's current unresolved receipt and basic provenance/intent fields can be represented by standard SBML Core plus a thin metadata sidecar. The standalone-language novelty claim is weakened.
- **SUPPORTED:** Annotation-free Core alone does not preserve the four tested non-Core fields.
- **NOT YET PROVEN:** The same thin layer can audit **newly introduced mathematical assumptions**, because the current planner introduces zero assumptions in every case. No completion profiles exist.
- **NOT TESTED:** Antimony interoperability, full semantic round-trip of real models, independent source provenance, scientific validity, or broad SBML ecosystem compatibility.
- **SECURITY BOUNDARY:** The Core digest catches accidental mismatched pairing. It is not a signature and does not protect against coordinated modification of both files.

The source fingerprint is copied into the sidecar. Matching it is not an independent reconstruction of the BioIR model.

## Evidence and next decision

- Script: `research/e284_sbml_sidecar.py`; tests: `tests/test_e284_sbml_sidecar.py`.
- Exact-head initial Actions run [40270102419](https://github.com/stoicsatvik/BioIR/actions/runs/40270102419): **SUCCESS**, unit and semantic/libSBML jobs.
- Job logs: **6 receipt matches, 4 Core-only collisions, 6 sidecar distinctions**.
- Immutable artifact: `e284-sbml-sidecar`, ID **12627808897**.
- Draft PR: [#18](https://github.com/stoicsatvik/BioIR/pull/18), stacked on E267 #17.

**Highest-EV next:** implement one *explicit hypothetical* completion profile with an assumption-introduction receipt and test it head-to-head against SBML/Antimony plus a thin, independently generated provenance layer. Freeze independent examples and tampering controls. If no additional validated capability survives, collapse BioIR into standards-based tooling rather than continuing a redundant language.
