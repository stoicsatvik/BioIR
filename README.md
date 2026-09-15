# BioIR

**BioIR is an experimental intermediate representation for programmable biology.**

The long-term idea is simple: software became powerful when humans stopped reasoning about individual transistor state changes and started programming against stable abstraction layers. BioIR explores what the corresponding abstraction boundary could look like for biological systems.

```text
intent
  ↓
BioIR program
  ↓
state model + constraints
  ↓
planner/controller
  ↓
simulation backend
  ↓
observations
  ↺
```

## What this repository is today

BioIR v0 is a **safe, simulation-only prototype**. It provides:

- a typed representation for biological state, objectives, constraints, and abstract operations;
- a compiler that lowers high-level goals into a small biological instruction set;
- a validator that rejects malformed or non-simulation operations;
- a closed-loop toy runtime that repeatedly senses, plans, acts, and re-observes;
- a CLI and tests so the core abstraction can evolve like a real compiler project instead of remaining a philosophical README.

BioIR deliberately does **not** generate nucleotide sequences, laboratory protocols, patient-specific treatment plans, dosing instructions, or real-world wet-lab actuation. Backends in this repository are synthetic state machines only.

## Core model

A biological system is treated as a partially observed dynamical system:

\[
S_{t+1} \sim P(S_{t+1}\mid S_t, A_t)
\]

with observations:

\[
O_t \sim P(O_t\mid S_t)
\]

and a controller selecting an abstract action under constraints:

\[
A_t = \pi(\hat S_t, G, C)
\]

where `G` is the objective and `C` is the constraint set.

## Tiny example

```json
{
  "name": "toy_homeostasis",
  "state": {
    "signal_a": 0.2,
    "signal_b": 0.8
  },
  "objectives": [
    {"variable": "signal_a", "target": 0.7, "tolerance": 0.05},
    {"variable": "signal_b", "target": 0.4, "tolerance": 0.05}
  ],
  "constraints": {
    "max_steps": 25,
    "max_action_magnitude": 0.15
  }
}
```

Run it with:

```bash
python -m bioir compile examples/toy_homeostasis.json
python -m bioir simulate examples/toy_homeostasis.json
```

## Biological ISA v0

The first instruction set is intentionally small and substrate-independent:

```text
SENSE(variable)
INCREASE(variable, magnitude)
DECREASE(variable, magnitude)
MAINTAIN(variable, target, tolerance)
WAIT(steps)
```

These are **semantic operations**, not wet-lab instructions. A future backend may map them to models of pathways, cell states, tissues, or synthetic environments, but the IR itself stays independent of implementation technology.

## Repository direction

The next milestones are:

1. formal schema/versioning for BioIR programs;
2. richer state estimation and uncertainty;
3. graph-based dependency models;
4. optimization over competing objectives and constraints;
5. pluggable simulation backends;
6. provenance for every lowering decision;
7. benchmark tasks for controllability, robustness, and compression quality.

The metric that matters is not how impressive the vocabulary sounds. It is whether a high-level biological objective can be represented, validated, lowered, simulated, inspected, and reproduced with fewer assumptions leaking across abstraction layers.

## License

Apache-2.0. See `LICENSE`.
