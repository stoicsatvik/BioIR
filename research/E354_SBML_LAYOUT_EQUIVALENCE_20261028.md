# E354: XML layout-only SBML receipt false rejection (2026-10-28)

## Falsifiable question

Does the E338 independent SBML Core + sidecar verifier reject an otherwise
identical declared completion solely because an XML serializer indents its
element-only content?

## Test-first result

At commit `7d892314a5ac26c99575b4cab30bc9fbb3e05b3d`,
[Actions run 40638397736](https://github.com/stoicsatvik/BioIR/actions/runs/40638397736)
failed precisely
`test_indentation_only_roundtrip_keeps_declared_receipt_valid`.
The completed SBML was parsed and indented with Python's `ElementTree.indent`;
its SHA-256 was recomputed correctly in the receipt, and the original two
declared assumptions were unchanged. The E338 verifier returned `False`.
This was a **false rejection**, not an unauthorized-model-change acceptance.

## Narrow correction and controls

Commit `83de6404973b7d14590647f63d9da2fef2ed544b` removes only
whitespace-only text/tail nodes in SBML structural elements and the MathML
`math`/`apply` element-only containers before canonical comparison.
Non-whitespace text, MathML identifier content and SBML notes/annotation
mixed content are not stripped.

- Indentation-only reserialization: ACCEPTED.
- Indented undeclared species initial-concentration change: REJECTED.
- Indented MathML identifier mutation: REJECTED.
- E338 original unrelated Core mutation and added-parameter controls: retained.
- E303 origin spoofing: still possible, not falsely called authenticated.

[Exact-head Actions run 40638435163](https://github.com/stoicsatvik/BioIR/actions/runs/40638435163)
**SUCCESS**, both unit-test and semantic-model workflows.

## Claim boundary

Layout normalization is **SUPPORTED IN TESTED SOFTWARE** for these synthetic
SBML examples. This does **not** prove general SBML semantic equivalence,
round-trip fidelity across independent tools, authenticity of the stated
assumption origin, biological correctness, or standalone BioIR novelty.

## Next discriminating experiment

Use independently generated libSBML/Antimony round-trips and adversarial
annotation/MathML mixed-content cases. If a thin standards-based sidecar
satisfies the same requirements, integrate it rather than claiming a new
representation is necessary. No biological optimization, wet-lab protocols,
clinical use or autonomous actuation.
