# E486 | Equilibrium-only kinetics cannot identify a common rate scale (2 November 2026)

## Falsification question and provenance
Does excellent late-time fit to a published SBML simulator reference identify the actual kinetic rates? Official SBML Test Suite case 00004 pinned at `sbmlteam/sbml-test-suite@d6dcd2cc6408d5eb881638ac6ce7a05fd7d2e4d1`, with reactions S1 -> 2 S2 at k1*S1 and 2 S2 -> S1 at k2*S2^2, k1=0.35, k2=180, initial (0.15,0). These are **simulator reference outputs, not biological observations**. E466 independently validated the conventional closed-form solution.

Scaling both rates by c preserves equilibrium and invariant S1+S2/2=0.15, but rescales time: x_c(t)=x_1(c*t). Frozen c={0.25,0.5,1,2,4}; early times {0.2,0.4}; late times {5,10}; max absolute component error against unchanged published values, tolerance 1e-10. No fitted parameters.

| c | Maximum early error | Maximum late error | Late pass? |
|---:|---:|---:|:---:|
| 0.25 | 0.00900012668120553 | 6.775391254987273e-09 | No |
| 0.5 | 0.004841593594925342 | 1.4328815911568427e-15 | Yes |
| 1 | 2.758734386765216e-11 | 8.326672684688674e-17 | Yes |
| 2 | 0.0023173571699251234 | 8.326672684688674e-17 | Yes |
| 4 | 0.002549516676163663 | 8.326672684688674e-17 | Yes |

Four of five rate pairs pass the late-only numerical check, only the pinned pair passes early; all preserve weighted conservation. Seven offline unittest contracts passed, including independent RK4 for three alternative scales at two early times, frozen published values, negative controls, invariants and deterministic receipt. Python compilation passed. Exact-head CI, full suite and native libSBML/Antimony comparisons not run.

**SUPPORTED on this synthetic standards case:** equilibrium-only fit cannot identify common absolute kinetic scale; early transient observations distinguish these alternatives. **NOT YET PROVEN:** unique BioIR utility, broad standards equivalence, biological validity, real-world control or model provenance. Next: compare independent libSBML/Antimony semantic diagnostics and assumption receipts against BioIR on frozen partially specified models; collapse to thin standards tooling if equivalent. No wet lab, deployment, paid APIs, outreach or main merge.
