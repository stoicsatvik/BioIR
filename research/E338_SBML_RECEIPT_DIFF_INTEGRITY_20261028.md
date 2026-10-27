# E338: An SBML digest is not an exhaustive assumption receipt

## Question

Does a self-consistent completed-model SHA-256 digest plus the two declared
assumptions prove that no other SBML Core fields were changed?

## Falsifying construction

Start from the repository's deliberately synthetic, non-executable toy SBML
Core model. Complete only the missing `k1` value and `A_to_B` kinetic law.
Then silently alter one unrelated field (species initial concentration,
compartment size, reaction reversibility, model ID, or an extra parameter).
Recompute the completed-model digest and leave the two assumption entries
unchanged.

The E303 verifier checked that the digest matched the supplied completed
document and that the two declared commitments matched. It did **not**
compare all other Core content to the original. Thus a newly computed digest
could authenticate the *wrong* model relative to the declared change set.
This is a logical content-integrity gap, not a SHA-256 collision or an
assertion about biological truth.

## E338 acceptance gate

- Revert exactly the two declared edits from the completed XML.
- Compare canonicalized reconstructed SBML Core to canonicalized baseline.
- Accept both legitimate synthetic completion profiles.
- Reject the four unrelated field edits and the added parameter, even when
  the attacker recomputes the completed digest.
- Preserve E303's separate negative control: the `origin` string can still
  be spoofed, because there is no independent signer or authenticated source.

## Claim boundary

This is a deterministic, synthetic software-integrity experiment.
It does not verify who supplied the assumptions, biological validity,
SBML semantics beyond this narrow toy subset, or independent provenance.
No wet-lab instructions, biological optimization, or clinical actions.

## Next uncertainty

Test independent standards-based SBML/Antimony examples and validate
canonicalization/annotation policy against independent tools. If a thin
standards-based sidecar suffices, BioIR should integrate rather than claim
unique representational novelty.
