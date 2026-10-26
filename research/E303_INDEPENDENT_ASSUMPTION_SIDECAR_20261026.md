# E303 | Explicit hypothetical completion in SBML Core plus a sidecar

**Date:** 2026-10-26. **Scope:** representation and integrity of synthetic mathematical assumptions only. No biological measurements, wet-lab procedures, clinical advice, pathogen work, or real-world actuation.

## Predeclared falsification

E284 showed that SBML Level 3 Core plus a small metadata sidecar could reproduce all six *currently implemented*, assumption-free BioIR unresolved receipts. The missing comparison was whether a **newly introduced assumption** necessarily requires a standalone BioIR language.

This experiment deliberately does **not** invoke a BioIR completion compiler. It starts from the existing synthetic underspecified_conversion model, strips BioIR annotations, and independently supplies two hypothetical completion profiles:

- Profile A: missing k1 assigned hypothetical value 0.1, with kinetic-law MathML for k1 * A * cell; origin label hypothetical_user_choice.
- Profile B: same mathematical law, hypothetical k1 assigned 0.2; origin label hypothetical_profile_choice.

Both are labelled hypothetical, not fitted parameters, observed kinetics, measured biology, or validated mechanistic models.

A small sidecar binds the original and completed Core byte representations by SHA-256 and records the exact introduced parameter value, kinetic MathML, declared hypothetical origin, and empty unresolved-commitment list. The verifier independently reads the completed Core to check the parameter and kinetic law. This tests **representability and content integrity**, not whether the asserted origin is true.

## Predeclared controls

1. Independently derive the two unresolved keys from annotation-free SBML and compare them with BioIR's original receipt.
2. Verify both independently supplied completions and distinguish their Core content.
3. Reject swapped sidecars, changed numerical values, and changed MathML.
4. Fail closed for nonfinite/nonpositive hypothetical parameters and unexpected unresolved keys.
5. Deliberately rewrite only an origin label to another allowed hypothetical origin and measure whether content verification catches it. **Prediction: it does not.** A digest is not a signature or an independent provenance witness.
6. Reparse both completed documents with libSBML when installed. This is a syntax/interoperability check, not a scientific or full semantic validity certificate.

## Interpretation and claim boundary

- **SUPPORTED if controls pass:** SBML Core plus a thin sidecar can record and content-check these two introduced mathematical assumptions. This weakens the standalone-language novelty hypothesis beyond E284's zero-assumption case.
- **EXPECTED NEGATIVE:** A sidecar can lie about who supplied an assumption while remaining content-consistent. Independent provenance authenticity is **NOT YET PROVEN**.
- **NOT TESTED:** Antimony import/export, independently authored real models, scientific kinetic-law validity, general model completion, round-trip semantic equivalence, signed provenance, or real biological measurements.
- The sidecar is independently specified from a hypothetical profile, **not** independently recovered from biology.
- The exact-byte digest is sensitive to benign XML serialization changes; canonical SBML content addressing is future work.

**Decision:** Do not promote BioIR as a novel standalone modeling language on the basis of an assumption receipt. Compare an established SBML/Antimony toolchain with explicit, independently authenticated assumption provenance on externally authored models. If the thin layer suffices, consolidate into established tooling.

**Reproduction:** python -m research.e303_sbml_assumption_sidecar ; python -m pytest tests/test_e303_sbml_assumption_sidecar.py -q. Preserve negative controls rather than reporting them as validation failures.
