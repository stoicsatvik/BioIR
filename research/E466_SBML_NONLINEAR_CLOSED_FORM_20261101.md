# E466 | Independent nonlinear SBML closed-form baseline (1 November 2026)

## Falsification question

E444 verified a weighted invariant in official SBML Test Suite semantic case **00004**, but left its nonlinear trajectory untested against an independent conventional solver. Does the unchanged published 51-point reference series agree with the closed-form solution of the *actual* SBML mass-action kinetics, or only with a weak conservation check?

## Frozen source and model

Official independently authored SBML Test Suite, commit \`d6dcd2cc6408d5eb881638ac6ce7a05fd7d2e4d1\`, \`cases/semantic/00004/00004-sbml-l3v2.xml\` and \`00004-results.csv\`. These are simulator reference values, **not biological observations**. The XML has unit compartment, initial S1=0.15, S2=0, forward S1 -> 2 S2 with rate 0.35*S1, reverse 2 S2 -> S1 with rate 180*S2^2. No model parameters were fitted.

The invariant is \`M = S1 + S2/2 = 0.15\`, giving

\`\`\`
dS2/dt = 2*k1*M - k1*S2 - 2*k2*S2^2
lambda = sqrt(k1^2 + 16*k1*k2*M)
r_plus = (-k1 + lambda)/(4*k2)
r_minus = (-k1 - lambda)/(4*k2)
S2(t) = r_plus*(1-exp(-lambda*t))/(1-(r_plus/r_minus)*exp(-lambda*t))
S1(t) = M-S2(t)/2
\`\`\`

## Results

Independent JavaScript evaluated **all 51 pinned published rows**. The exact closed-form baseline has maximum absolute component discrepancy **2.758734386765216e-11**, at t=0.2. Published weighted-invariant drift is at most **2.220446049250313e-16**. This early-time discrepancy is consistent with finite published simulator accuracy; it is not a physical measurement uncertainty.

A deliberately wrong **linear reverse-rate** null (replace 180*S2^2 with 180*S2, leaving the same stoichiometry) has maximum absolute S2 discrepancy **0.016307673660599813** at t=2.6, over **5.9e8 times** the maximum correct-model discrepancy. Thus a conserved weighted sum alone is not enough to certify correct nonlinear kinetics.

A separate locally executed Python closed-form implementation matched seven frozen published checkpoints within 3e-11 and a **separately coded RK4 ODE integrator** at t=0.2/0.4/1.0 within 3e-12. Six offline unittest contracts passed; Python compilation passed. The exact two committed Git blobs were checked against the locally executed files (source \`50498ce95e03a6bdbe1305e37752448c9a831c25\`, tests \`9d538aa38b8a3b6e2525c1628a76531584c23f2d\`). Full inherited suite, libSBML/Antimony round-trip, and exact-head CI were **not executed**; commits intentionally use [skip ci] to avoid paid Actions.

## Claim and next experiment

**SUPPORTED ON THE PINNED SIMULATOR REFERENCE:** independent conventional nonlinear dynamics reproduce all 51 published case-00004 timepoints to the stated numerical tolerance, and the wrong-kinetic-law null is decisively worse. This resolves E444's specific missing nonlinear trajectory baseline.

**NOT YET PROVEN:** any unique BioIR advantage over SBML/libSBML/Antimony with a thin provenance receipt, broad standards equivalence, authenticated model provenance, biological validity or real-world controllability.

**Highest-EV next:** freeze independent standards-authored partial-model cases, compare actual libSBML/Antimony semantic diagnostics and assumption-receipt loss against BioIR on identical inputs; collapse standalone language work if a thin standards-based layer is equivalent.

No biological actuation, wet lab, patient-specific decisions, main merge, spending, deployment or outreach.
