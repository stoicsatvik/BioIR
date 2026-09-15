"""BioIR: a simulation-only intermediate representation for programmable biology."""

from .compiler import compile_program
from .model import Constraints, Objective, OpCode, Operation, Program
from .runtime import SimulationResult, ToyRuntime
from .validator import ValidationError, validate_program

__all__ = [
    "Constraints",
    "Objective",
    "OpCode",
    "Operation",
    "Program",
    "SimulationResult",
    "ToyRuntime",
    "ValidationError",
    "compile_program",
    "validate_program",
]

__version__ = "0.1.0"
