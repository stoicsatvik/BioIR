"""BioIR: user-facing biological semantics with explicit lowering boundaries."""

from .compiler import compile_program
from .model import Constraints, Objective, OpCode, Operation, Program
from .runtime import SimulationResult, ToyRuntime
from .sbml_backend import to_sbml_xml
from .semantic_checks import (
    ModelCheckReport,
    ModelIssue,
    SemanticValidationError,
    check_semantic_model,
    require_valid_semantic_model,
)
from .semantic_model import (
    Compartment,
    Entity,
    Interaction,
    InteractionKind,
    Parameter,
    Participant,
    Provenance,
    QuantityKind,
    SemanticModel,
)
from .validator import ValidationError, validate_program

__all__ = [
    "Compartment",
    "Constraints",
    "Entity",
    "Interaction",
    "InteractionKind",
    "ModelCheckReport",
    "ModelIssue",
    "Objective",
    "OpCode",
    "Operation",
    "Parameter",
    "Participant",
    "Program",
    "Provenance",
    "QuantityKind",
    "SemanticModel",
    "SemanticValidationError",
    "SimulationResult",
    "ToyRuntime",
    "ValidationError",
    "check_semantic_model",
    "compile_program",
    "require_valid_semantic_model",
    "to_sbml_xml",
    "validate_program",
]

__version__ = "0.2.0"
