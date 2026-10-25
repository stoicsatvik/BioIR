# E249 | XML 1.0 text-integrity falsification (2026-10-25)

**Scope:** BioIR simulation-only semantic-model-to-SBML export. No biological optimization, real biological measurements, laboratory procedures, or clinical decisions.

## Hypothesis and counterexample

The existing structural checker validates model identifiers, units and finite values, but did not validate free-text names or provenance against XML 1.0 character rules. Python's standard `xml.etree.ElementTree.tostring` can emit a prohibited NUL into an attribute without raising an error:

```python
from xml.etree import ElementTree as ET
text = ET.tostring(ET.Element("model", {"source": "a\\x00b"}), encoding="unicode")
# Serialization returns text containing U+0000.
ET.fromstring(text)  # ParseError: not well-formed (invalid token)
```

This is a **serialization-integrity counterexample**, not evidence of any biological failure. It matters because a semantic model previously accepted as valid could yield invalid SBML XML that downstream tooling cannot parse.

## Adversarial contract

Six synthetic negative fixtures cover forbidden characters in source/citation and compartment/entity/parameter/interaction display names: U+0000, U+000B, U+D800, U+FFFF, U+001F and U+DFFF. They require `check_semantic_model` to emit `text.invalid_xml_char` and `to_sbml_xml` to fail closed with `SemanticValidationError`.

A positive fixture checks valid Greek letters, tab/newline and escaped XML metacharacters; round-tripping through an independent `ElementTree.fromstring` must preserve both metadata and display names.

The rule implements the XML 1.0 Fifth Edition `Char` production: U+0009, U+000A, U+000D, U+0020–U+D7FF, U+E000–U+FFFD, U+10000–U+10FFFF.

## Limits and claim

**SUPPORTED in software tests only** after passing exact-head CI: the tested invalid strings are rejected before XML serialization and valid Unicode/escaping remains accepted. This is not a complete SBML semantic-validity proof; libSBML validation, numerical assumptions, biological truth and downstream interoperability remain independent gates.

**Next:** add a property-based corpus of all XML character boundaries and independently validate generated SBML documents with libSBML across permitted metadata, without adding biological actuation or wet-lab procedures.

No main merge or external action.
