# E423 | Independent SBML Test Suite stoichiometry baseline (30 October 2026)

## Decision question
Can a naive species-sum conservation check substitute for a stoichiometry-aware invariant when assessing a valid, independently authored SBML model?

**No.** Three unchanged SBML Level 3 Version 2 semantic models and all 51 published reference timepoints per model were retrieved from the [official SBML Test Suite](https://github.com/sbmlteam/sbml-test-suite), pinned to commit `d6dcd2cc6408d5eb881638ac6ce7a05fd7d2e4d1`. Cases 00001 and 00002 have one S1-to-S2 product per reactant; case 00003 produces **two S2 units per S1**. The three published models use unit compartment volume and k1=1; case 00002 has a second reaction with k2=0. No parameter was fitted to the reference trajectories.

For this **specific** frozen model family, the analytical conventional baseline is:
- S1(t) = S1(0) exp(-t)
- S2(t) = nu S1(0) [1-exp(-t)]
- conserved invariant = S1 + S2/nu

| Published case | Product coefficient nu | Reference points | Max analytic absolute error | Max weighted-invariant error | Relative naive S1+S2 drift |
|---|---:|---:|---:|---:|---:|
| 00001 | 1 | 51 | 8.14e-20 | 8.14e-20 | 5.42e-16 |
| 00002 | 1 | 51 | 4.34e-19 | 4.34e-19 | 2.89e-16 |
| 00003 | 2 | 51 | 6.94e-18 | 3.47e-18 | **0.9932620530** |

The ordinary species sum increases by approximately **99.326% of initial S1** by t=5 in case 00003, *without* violating the stoichiometrically weighted invariant. These are reference simulation values, not experimental biological observations. They are not evidence of BioIR executing the model.

## Method, validation and provenance
- External files: `cases/semantic/{00001,00002,00003}/{id}-sbml-l3v2.xml` and `{id}-results.csv` at the pinned upstream commit.
- Source retrieval and 153-point arithmetic were performed through the GitHub connector. A second independent analytical expression reproduced the trajectories to floating-point rounding.
- Reproduction script: `python -m research.e423_sbml_stoichiometric_baseline`. It fails closed if the frozen model shape, stoichiometry, rate law, volume or grid changes; it is not a general SBML parser.
- **Six offline pytest tests passed locally** against a source-equivalent copy, including published t=5 checkpoints, stoichiometry extraction and fail-closed controls. The actual committed-source full suite and GitHub Actions are **NOT YET VERIFIED**; no paid CI was requested.
- No independent libSBML execution in this run; no Antimony round-trip, source-origin authentication or clinical/biological validity claim.

## Interpretation
**SUPPORTED FOR THE THREE PUBLISHED MODELS:** a plain species-sum conservation assertion can reject a valid model; an appropriate stoichiometric invariant is essential. This is established chemistry/linear algebra, not a novel BioIR discovery. E401's content-integrity-versus-semantic-validity distinction remains intact. The central standalone BioIR novelty thesis is **NOT YET PROVEN**.

**Next decisive experiment:** use a larger independently authored SBML/Antimony corpus with a pinned valid/invalid oracle, explicit units, rules/events and incomplete parameters; compare libSBML/Antimony plus a thin receipt against BioIR's incremental diagnostic information and round-trip loss. If no advantage survives, collapse the project into standards tooling.

No wet-lab, biological actuation, pathogen work, clinical decisions, main merge, deployment, spending, outreach or competition submission.
