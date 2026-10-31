# E444 | SBML boundary species invalidate naive closed-system conservation (31 October 2026)

## Falsification question
Can a generic conservation checker infer a conserved total from a reaction network's stoichiometric nullspace **without** respecting SBML `boundaryCondition` semantics?

**No.** Five additional independently authored official [SBML Test Suite](https://github.com/sbmlteam/sbml-test-suite) Level 3 Version 2 semantic cases, `00004`–`00008`, were inspected at pinned upstream commit `d6dcd2cc6408d5eb881638ac6ce7a05fd7d2e4d1`. Their 255 published reference timepoints were evaluated. These are published **simulation reference trajectories**, not laboratory measurements.

| Official case | Physical/semantic distinction | Reference rows | Max absolute naive S1+S2 drift | Max appropriate invariant drift | Max independent analytic error |
|---|---|---:|---:|---:|---:|
| 00004 | S1 ↔ 2 S2; nonlinear reverse law; both dynamic | 51 | 0.008299528518936006 | 2.22e-16 for S1+S2/2 | Not computed; nonlinear |
| 00005 | S1 → S2; nonzero initial S2; both dynamic | 51 | 1.08e-19 | 1.08e-19 | 1.08e-19 |
| 00006 | Equal forward/reverse rates at equilibrium | 51 | 0 | 0 | 0 |
| 00007 | S1 boundaryCondition=true, S2 dynamic | 51 | **0.014647233812159863** | No closed S1+S2 invariant | 1.04e-17 |
| 00008 | S2 boundaryCondition=true, S1 dynamic | 51 | **0.0744946539750686** | No closed S1+S2 invariant | 8.33e-17 |

The "max appropriate invariant" column for boundary cases intentionally does **not** imply a conserved total: the boundary reservoir can supply/remove species, so a closed-system conservation check is inapplicable.

## Independent conventional baseline
- 00004: each reaction changes S1 and S2 in ratio 1:2; `S1+S2/2` is conserved, despite nonzero `S1+S2` drift.
- 00005: `S1(t)=a exp(-t)`; `S2(t)=b+a(1-exp(-t))`, with `a=b=0.00015`.
- 00006: `S1=S2=0.0015` for all times under symmetric rates.
- 00007: `S1=0.015` is externally fixed. `S2(t)=0.03-0.015 exp(-0.25t)`. The naive sum increases by about 0.014647 at t=15.
- 00008: `S2=0.15` is externally fixed. `S1(t)=0.075+0.075 exp(-0.5t)`. The naive sum decreases by about 0.074495 at t=10.

The four closed-form baselines agree with all 204 published reference points within 8.33e-17 absolute error. The 00004 weighted invariant was checked against all 51 points, but no independent nonlinear trajectory solver was run. This is a **semantic counterexample**, not a new scientific discovery.

## Source, method, reproducibility and limits
- Official immutable sources: `https://raw.githubusercontent.com/sbmlteam/sbml-test-suite/d6dcd2cc6408d5eb881638ac6ce7a05fd7d2e4d1/cases/semantic/{CASE}/{CASE}-sbml-l3v2.xml` and `{CASE}-results.csv`, for CASE=00004 through 00008.
- Pinned source files and all 255 published CSV rows were read through the GitHub connector. An independent JavaScript analysis parsed model initial values, boundary flags, rates, and published results and computed the table above. No parameters were fitted.
- Reproduction code: `python -m research.e444_sbml_boundary_audit`. It retrieves only the pinned public corpus, fails closed on frozen model shape and 51-point grid changes, and reports maximum deviations.
- Six offline tests passed on a local byte-identical source/test copy; Python compilation passed. Remote Git blob identities were verified for both files. **The exact committed Python downloader has NOT been executed against the external corpus in this environment** (network access unavailable in local Python); the published-row calculation was independently executed in JavaScript. No full repository suite or exact-head GitHub Actions was run.
- This restricted reader is not a general SBML interpreter or libSBML replacement. Its MathML checks cover the pinned family only; it cannot certify semantic validity, biological realism, authenticated source origin, or broad round-trip preservation.

## Claim discipline and next experiment
**REJECTED FOR THESE OFFICIAL CASES:** assuming every stoichiometrically balanced reaction network has a conserved dynamic-species total, without checking `boundaryCondition` and reservoir semantics.

**SUPPORTED:** conventional boundary-aware analytical baselines and appropriate weighted invariants reproduce the published standard reference trajectories within stated numerical limits.

**NOT YET PROVEN:** standalone BioIR novelty, independent biological validation, general SBML/Antimony equivalence, provenance authentication, and any advantage over a thin SBML/libSBML receipt layer.

**Next:** compare independent libSBML/Antimony handling of boundary species, nonlinear kinetic laws, and unresolved assumptions against BioIR receipts. If a standards-based thin layer preserves the same information and diagnostics, collapse BioIR into that layer rather than duplicate it.

No biological actuation, hazardous optimization, wet lab, clinical advice, paid API, deployment, outreach, or main merge.
