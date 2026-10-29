# E401 | Undefined MathML identifier survives a self-consistent SBML receipt

**30 October 2026.** Frozen, safe, synthetic mathematical negative control. No biological measurements, wet-lab protocols, sequence design, clinical claims, or physical actuation.

## Question

Does the E303/E381 SBML Core + thin assumption-sidecar receipt establish that its newly declared kinetic-law symbols resolve against the actual model? Or does it establish only content consistency?

## Discriminator and method

1. Load the existing under-specified `examples/underspecified_conversion.json` fixture and export annotation-free SBML Core.
2. Complete exactly the two declared commitments using the frozen hypothetical `k1=0.1` profile. Confirm the legitimate receipt verifies.
3. In the *declared* MathML kinetic law, replace identifier `A` with `e401_undefined_symbol`, which is absent from the model. Update the declared MathML and completed XML SHA-256 in the receipt to match the changed content. Leave the baseline and all undeclared model structure unchanged.
4. Check the unchanged `verify_receipt` contract and independently run libSBML 5.21.2 `checkConsistency` on the exact forged SBML.
5. Preserve inherited E303, E338 and E381 controls. Do not silently promote content integrity into semantic validity.

## Measured result

| Frozen case | Result |
|---|---|
| Original synthetic completed receipt | Accepted by content verifier |
| Rehashed, declared MathML with undefined `ci` identifier | **Accepted** by content verifier |
| Same forged SBML passed to independent libSBML `checkConsistency` | **Undefined identifier reported** |
| E401 focused tests | **2/2 passed** |
| Inherited E303/E338/E381 regression tests | **11/11 passed** |

[Exact-code E401 GitHub Actions run #40958356283](https://github.com/stoicsatvik/BioIR/actions/runs/40958356283) **SUCCESS** on implementation head `b548995e65adc0e6fbd1bf44d756e7d9b7e164c8`. Both E401 assertions and all inherited regressions passed. Test source: `tests/test_e401_semantic_symbol_gap.py`.

## Interpretation and claim states

**SUPPORTED:** E303/E381 verifies declared changes and hash-bound content for the tested synthetic examples. The E401 negative control shows that such content consistency **does not imply MathML symbol resolution or SBML semantic validity**. Independent libSBML identifies an invalid symbol that the receipt deliberately accepts.

This is a **contract-boundary falsification**, not proof of a security exploit or biological invalidity in any real model. The receipt verifier describes itself as a content checker and explicitly does not authenticate origin; therefore its acceptance is not necessarily a regression against its documented scope. However, a downstream system would be wrong to treat `verify_receipt=True` as an executable/semantically valid model certificate.

**NOT YET PROVEN:** Standalone BioIR novelty, general standards interoperability, authenticated assumption provenance, biological correctness or real-world controllability.

## Highest-EV next experiment

Freeze a third-party, independently authored SBML/Antimony model corpus with both valid and invalid MathML, unit and identifier controls. Compare (a) content-only sidecar verification, (b) independent libSBML consistency, and (c) any incremental BioIR semantic checks on untouched examples. Explicitly separate content integrity, model semantics and source authenticity. Prefer integration with established standards over inventing a new language.

No main merge, deployment, outreach, spending, competition submission or irreversible action.
