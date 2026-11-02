# E509 | Early transient measurements versus late-equilibrium identifiability (2 November 2026)

## Falsifiable question

E486 showed that four of five common kinetic-rate scales fit the late-time published SBML simulator reference, despite distinct transients. Does this ambiguity survive a specified finite-noise observation model, and which time windows actually distinguish the frozen competing scales?

**Provenance:** Official `sbmlteam/sbml-test-suite@d6dcd2cc6408d5eb881638ac6ce7a05fd7d2e4d1`, semantic case `00004`, the E466 independent nonlinear closed-form baseline, and the E486 frozen rate-scale candidates. The case is an **SBML simulator standard**, not biological measurement data. No fitting or experimental actuation.

## Design

- Frozen binary hypotheses `(0.5,1)` and `(1,2)` multiplying both kinetic rates.
- Four two-observation windows: `(.1,.2)`, `(.2,.4)`, `(1,2)`, `(5,10)` in the source model's time units.
- Observe both species with independent Gaussian noise at fixed per-component standard deviation `0.001` or `0.005` concentration units; equal prior hypotheses.
- Compute exact Euclidean separation `d` between the four-dimensional predicted observation vectors and optimal Gaussian binary classification error `Phi(-d/(2*sigma))`.
- Seeded independent Gaussian sufficient-statistic Monte Carlo checks at seed `20261102` and 100,000 draws per design/scale/noise combination.
- Analytic local Fisher information for log-rate scale at `c=1`, with `dS1/dlog(c)=-t*flux`, `dS2/dlog(c)=2*t*flux`.
- Negative control: at exactly identical predictions, the classifier must report 50% expected error, not exploit arbitrary label ordering.

## Measured computational results

At noise SD `0.001`, `(0.5,1)` at `(.1,.2)` has `d=0.0071356872`, expected binary error `0.000179966`, and seeded Monte Carlo error `0.00019`. At `(5,10)`, `d=1.595e-15`, expected error `0.5`, Monte Carlo `0.50128`.

For `(1,2)` at `(.1,.2)`, `d=0.0060011637`, expected error `0.00134732`, Monte Carlo `0.00126`. At `(5,10)` the predictions are numerically indistinguishable and the seeded tie control yields `0.50037`.

The local Fisher information at `t=0.1` is `63.4858`, versus `4.07261e-6` at `t=1`, for SD `0.001`, a ratio of approximately 15.59 million. The deterministic script emits all 16 rows and their exact numerical distances, theoretical Bayes errors, seeded Monte Carlo errors and Fisher information.

**Interpretation:** For this known nonlinear ODE, late-only observations are nearly uninformative about the absolute rate scale under even modest *assumed* observation noise, whereas appropriately timed transients are highly discriminating. This is a conventional identifiability/experimental-design finding, **not** evidence of a unique BioIR capability or actual biological measurement accuracy. It does not compare BioIR to native libSBML/Antimony, which remains the highest-value novelty test.

**Limits:** Gaussian independence, noise levels, equal priors, exact model, time units and frozen candidate scales are assumptions; Monte Carlo is synthetic and cannot be treated as independent empirical validation. Very late predictions are near machine precision. No standards-native comparison, real observations, wet lab, clinical use, deployment, paid APIs or main merge.

## Validation

Seven focused deterministic unittest controls passed locally with the E466 mathematical predictor reproduced in a local fixture. The exact repository-branch source and test files require independent GitHub readback; full native inherited suite and exact-head CI not yet run. Avoid treating this as biological or standards-native empirical evidence.
