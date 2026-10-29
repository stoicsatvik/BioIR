# E379 | Independent libSBML serialization falsifies receipt portability

**29 October 2026.** Two hypothetical mathematical completion profiles (k1=0.1 and 0.2) were generated from the frozen under-specified SBML Core example. No biological measurements or wet-lab operations were involved.

## Frozen discriminator

1. Verify the original two-assumption SBML Core + sidecar receipt.
2. Independently read/write the completed Core using **libSBML 5.21.2**, rehash the receipt and check against the original baseline.
3. Independently read/write both baseline and completed Core, rehash both and verify again.
4. Mutate an undeclared species initial concentration in the reserialized completed Core, rehash and require rejection.

## Measured result

| Profile | Independent completed reparse | Completed-only receipt accepted | Both-rewritten receipt accepted | Undeclared species mutation rejected |
|---|---|---|---|---|
| k1=0.1 | Yes | **No** | **No** | Yes |
| k1=0.2 | Yes | **No** | **No** | Yes |

Both libSBML outputs reparsed, but the E303/E354 receipt verifier rejected **4/4** legitimate reserialized cases even after correctly recomputing SHA-256 digests. This is a reproducible **portability false rejection** under an independent serializer, not proof of altered biological semantics. The two deliberate species mutations were still rejected.

**Claim:** Independent libSBML serializer compatibility is REJECTED FOR THESE TWO SYNTHETIC PROFILES. The verifier is fail-closed on the tested mutation but is overstrict under standards serialization. No biological correctness, authenticated origin or general semantic equivalence has been demonstrated.

## Evidence

- [Exact-head Actions #40801216458 SUCCESS](https://github.com/stoicsatvik/BioIR/actions/runs/40801216458), both unit and semantic-model jobs, plus one explicit E379 dependency-backed test.
- [E379 numerical receipt #12866251550](https://github.com/stoicsatvik/BioIR/actions/runs/40801216458/artifacts/12866251550), independently downloaded, parsed and SHA-256 verified: `08cf1bcd455a6f54267598cc5d00358e9592e936fd16eb1da56b75805d3a71c6`.
- Source code: `research/e379_libsbml_serializer.py`. Synthetic-only, with no autonomous biological actuation.

**Next discriminating experiment:** Compare structural canonical forms before/after libSBML and isolate the exact formatting/default-attribute/MathML change responsible. Only relax a verifier rule when it can be proved semantically irrelevant and an undeclared-mutation adversarial control still rejects. Compare against a standards-based thin-sidecar alternative before claiming a distinct BioIR language is necessary.
