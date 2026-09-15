# BioIR architecture

BioIR separates **intent**, **representation**, **control**, and **execution** so no single layer needs to know how every lower layer works.

## Layer model

```text
L7  Intent / phenotype specification
L6  Objective + constraint model
L5  BioIR semantic operations
L4  Planner / controller
L3  Backend adapter
L2  State transition model
L1  Observations
L0  underlying biological reality (outside v0)
```

BioIR v0 implements L6-L2 against a synthetic normalized state space. L0-L1 are deliberately mocked. This keeps the compiler architecture testable without pretending a toy model is a real organism.

## Closed-loop execution

The runtime follows five phases:

```text
SENSE → INFER → PLAN → ACT → OBSERVE → repeat
```

For v0, sensing is perfect and state is fully observable. The state estimate is therefore simply the current synthetic state. Later versions can separate latent state `S_t` from observation `O_t` and maintain a belief distribution.

## BioIR semantic ISA

`SENSE(variable)` requests an observation.

`INCREASE(variable, magnitude)` expresses a directional state change.

`DECREASE(variable, magnitude)` expresses the opposite directional state change.

`MAINTAIN(variable, target, tolerance)` declares a feedback objective rather than a one-shot mutation.

`WAIT(steps)` advances a backend without requesting another state change.

The important design rule is that these operations describe **what semantic transition is requested**, not how to perform it in a laboratory.

## Compiler contract

The compiler consumes:

```text
(current state, objectives, constraints)
```

and emits a sequence of semantic operations. Every lowering decision should eventually carry provenance, confidence, assumptions, and backend compatibility metadata.

## Backend contract

A backend should eventually implement a small interface resembling:

```python
observe(variable) -> Observation
apply(operation) -> TransitionReceipt
step() -> None
snapshot() -> StateEstimate
```

Backends may be deterministic simulations, stochastic models, graph simulators, or validated external research simulators. Real-world actuation is intentionally out of scope for v0.

## Safety boundary

BioIR v0 must remain simulation-only. It must not emit:

- nucleotide or protein sequences intended for synthesis;
- wet-lab procedures or experimental protocols;
- pathogen optimization or biological threat design;
- patient-specific treatment, dosing, or clinical instructions;
- automatic physical actuation.

This is not decorative policy text. It is an architectural constraint: the IR and runtime should remain useful even when all physical actuators are absent.

## Next technical milestones

1. JSON Schema for versioned programs.
2. First-class uncertainty on every state variable and observation.
3. Dependency graphs and cross-variable coupling.
4. Multi-objective optimization with hard and soft constraints.
5. Backend capability negotiation.
6. Provenance graph for compiler lowering decisions.
7. Reproducible benchmark suite.
8. A richer textual DSL that lowers to the same canonical IR.
