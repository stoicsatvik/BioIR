# BioIR v0.2 controller-candidate preregistration

Status: FROZEN BEFORE IMPLEMENTATION OR EVALUATION

## Question
Can a materially different, simulation-only controller improve target convergence over the current conservative baseline without increasing unsupported-direction decisions under the same sensing, action, and step budgets?

This document freezes the evaluation boundary. It does not claim that a candidate works.

## Historical evidence boundary
The seed population `0..999` belongs to the rejected temporal-belief-fusion experiment and is historical evidence only. It MUST NOT be used to tune, select, promote, or reject the next candidate.

## Sealed evaluation population
- Development seeds: `1000..1499`.
- Sealed evaluation seeds: `1500..2499`.
- The evaluation seeds MUST NOT be inspected for candidate selection or parameter tuning.
- The simulator configuration, objective distribution, noise process, and initial-state generation MUST be identical between baseline and candidate for each seed.
- Seed membership MUST remain fixed even if results are unfavorable.

## Matched resource budget
For every paired baseline/candidate replay:
- observations per step: 1;
- maximum steps: 30;
- maximum action magnitude: 0.1;
- response gain: 0.85;
- observation-noise scale: 0.08;
- no extra hidden state from the simulator;
- no additional sensing calls, retries, or candidate-only information.

If the implementation cannot satisfy this matched boundary, the experiment is BLOCKED rather than silently redefined.

## Candidate admissibility
The next candidate MUST be materially different from the rejected naïve temporal-fusion rule. It may use only current and prior synthetic observations plus deterministic internal state. It MUST NOT:
- tune against seeds `0..999` or sealed seeds `1500..2499`;
- use future observations or simulator internals;
- generate biological sequences, wet-lab procedures, treatment recommendations, or real-world actuation;
- encode organism-specific or pathogen-specific optimization.

Candidate architecture and all tunable constants MUST be frozen in a follow-up commit before sealed evaluation.

## Primary metric
`convergence_rate = converged_seeds / evaluated_seeds`

The primary comparison is paired candidate convergence versus the current conservative baseline on the sealed 1,000-seed population.

## Safety metric
`unsupported_direction_decisions`, using the repository's existing definition.

## Secondary diagnostics
Record, but do not substitute for the primary metric:
- steps to convergence;
- WAIT count;
- action count;
- longest WAIT streak;
- final-state error;
- recovered seed identities;
- regressed seed identities.

## Promotion rule
The candidate is SUPPORTED on this bounded synthetic experiment only if ALL conditions hold on sealed seeds `1500..2499`:
1. candidate convergence count is strictly greater than baseline convergence count;
2. candidate unsupported-direction decisions equal 0;
3. candidate introduces no regression seeds where the baseline converges and the candidate does not.

Otherwise the candidate is REJECTED. No threshold may be weakened after sealed results are observed.

## Claim boundary
Even a promoted candidate establishes only deterministic behavior in the repository's normalized synthetic simulator. It does NOT establish biological sensing accuracy, causal validity, organism-level control, intervention efficacy, wet-lab validity, clinical validity, or safe real-world actuation.

## Required artifact
The eventual sealed run MUST persist a canonical machine-readable verdict containing:
- schema/version;
- exact candidate identifier and constants;
- seed ranges;
- matched-budget parameters;
- baseline and candidate aggregate metrics;
- recovered/regressed seed identities;
- claim state (`SUPPORTED` or `REJECTED`).

Negative evidence is retained. The Foundry does not tune the exam after reading the answer sheet.
