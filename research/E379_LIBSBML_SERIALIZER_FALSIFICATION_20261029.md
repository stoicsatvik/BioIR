# E379 | Independent libSBML serializer versus explicit-assumption receipts

**29 October 2026.** BioIR's E303/E354 synthetic SBML Core + thin-sidecar receipt verifier is tested against a *real independent SBML serializer*, rather than a same-library XML pretty-printer.

## Predeclared test

Two hypothetical mathematical completion profiles (k1=0.1, 0.2) are generated from the frozen under-specified structural model. For each:

1. Verify the original two-assumption receipt.
2. Round-trip completed SBML through the installed libSBML parser and serializer.
3. Rehash the receipt and test whether the completed-only round trip is accepted against the unchanged baseline.
4. Independently round-trip the baseline, rehash both, and test receipt acceptance.
5. Change a species initial concentration in the reserialized completed Core, rehash again, and require rejection.

The last step tests a genuine undeclared content mutation, not digest mismatch. A false rejection after pure serialization is useful negative evidence about portability; acceptance would only support this narrow example.

## Evidence status

**PENDING exact-head CI and real libSBML receipt.** Do not report a success rate until the independent serializer experiment actually runs.

The work is simulation-only. No biological optimization, wet-lab instructions, harmful sequence design, or clinical decisions. The standalone BioIR novelty thesis remains **NOT YET PROVEN**; standards-based integration is preferred if it provides equivalent capability.
