# E267 | SBML Core reconstructs BioIR's current unresolved commitment keys

**Date:** 2026-10-25. **Safe synthetic structural-model research.** No biological experiments, treatment decisions, wet-lab protocols or autonomous actuation.

## Decisive question

Does BioIR's currently implemented `parameter_value:<id>` / `kinetic_law:<id>` unresolved-commitment **key set** contain information that is unavailable from standard SBML Level 3 Core, once all BioIR-specific annotations are removed?

**Result: No, in six frozen synthetic structural cases.** An independent libSBML read → annotation removal → serialize → re-read pipeline reconstructed **every key in all 6/6 cases** solely from `Parameter.isSetValue()` and `Reaction.isSetKineticLaw()`.

## Measured cases

| Synthetic model case | BioIR unresolved keys | Recovered from annotation-free SBML Core |
|---|---:|---:|
| Known parameter, unknown kinetics | 1 | 1 |
| Unknown parameter, unknown kinetics | 2 | 2 |
| Two unknown parameters | 3 | 3 |
| No reactions, unknown parameter | 1 | 1 |
| Unknown kinetics, no parameters | 1 | 1 |
| Two unknown kinetic laws | 3 | 3 |
| **Exact case-level matches** | | **6/6** |

The procedure strips model and reaction annotations. libSBML can retain an **unused namespace declaration** after annotation removal, so the integrity check correctly verifies absence of actual BioIR extension **elements and attributes**, not absence of a harmless `xmlns:bioir` string. The first exact-head CI attempt failed this overly strict test; the corrected test passed without changing any biological data or lowering semantics.

## Evidence

- Code: `research/e267_sbml_core_receipts.py`; tests: `tests/test_e267_sbml_core_receipts.py`.
- Exact-head Actions run: https://github.com/stoicsatvik/BioIR/actions/runs/40212759770 **SUCCESS**; both unit and semantic/libSBML jobs passed.
- Initial expected test-harness failure: https://github.com/stoicsatvik/BioIR/actions/runs/40212713455.
- Immutable artifact: `e267-sbml-core-receipts`, ID **12605943062**.
- Extracted JSON SHA-256: `c6c481ba4ff420cd839ef03b02cff6ac6e4e5153e5aa07b0b9c333ec5e6b8769`.

## Interpretation and stop criterion

**SUPPORTED IN THE SIX TESTED SYNTHETIC CASES:** BioIR's current unresolved **key identities** are derivable from standard SBML Core fields; key enumeration by itself is **not** a defensible novelty claim. This narrows the candidate contribution toward an explicit *assumption introduction and audit workflow*, not another modeling language.

**NOT YET PROVEN:** Full receipt equivalence, preservation of reasons/provenance/parameter-to-interaction intent, Antimony round-trip behavior, actual completion-profile value, or semantic correctness of real biological models.

**Next decisive experiment:** freeze partial models that include provenance, interaction intent and explicit hypothetical mathematical completions; compare an SBML/Antimony-plus-thin-receipt baseline against BioIR on exact assumption provenance, semantic round-trip loss and false assumption insertion. If the thin standards-based baseline is equivalent, consolidate BioIR into interoperability tooling rather than continuing a redundant standalone representation.
