from __future__ import annotations

from xml.etree import ElementTree as ET

from .semantic_checks import UNIT_SIGNATURES, require_valid_semantic_model
from .semantic_model import QuantityKind, SemanticModel


SBML_NS = "http://www.sbml.org/sbml/level3/version2/core"
BIOIR_NS = "https://stoicsatvik.github.io/BioIR/ns/semantic/v1"

ET.register_namespace("", SBML_NS)
ET.register_namespace("bioir", BIOIR_NS)


def _tag(name: str) -> str:
    return f"{{{SBML_NS}}}{name}"


def _bioir_tag(name: str) -> str:
    return f"{{{BIOIR_NS}}}{name}"


def _custom_unit_definition(
    parent: ET.Element,
    unit_id: str,
    signature: tuple[int, int, int],
) -> None:
    unit_def = ET.SubElement(parent, _tag("unitDefinition"), {"id": unit_id})
    units = ET.SubElement(unit_def, _tag("listOfUnits"))
    substance, volume, time = signature
    if substance:
        ET.SubElement(
            units,
            _tag("unit"),
            {
                "kind": "mole",
                "exponent": str(substance),
                "scale": "0",
                "multiplier": "1",
            },
        )
    if volume:
        ET.SubElement(
            units,
            _tag("unit"),
            {
                "kind": "litre",
                "exponent": str(volume),
                "scale": "0",
                "multiplier": "1",
            },
        )
    if time:
        ET.SubElement(
            units,
            _tag("unit"),
            {
                "kind": "second",
                "exponent": str(time),
                "scale": "0",
                "multiplier": "1",
            },
        )


def _species_substance_unit(model_unit: str) -> str:
    if model_unit.startswith("mole"):
        return "mole"
    if model_unit.startswith("item"):
        return "item"
    return "dimensionless"


def to_sbml_xml(model: SemanticModel) -> str:
    """Lower the user-facing semantic model to structural SBML Level 3 Version 2.

    This backend intentionally emits no KineticLaw by default. It preserves
    entities, compartments, parameters and interaction topology while deferring
    mathematical kinetics to a later compile-time profile.
    """

    require_valid_semantic_model(model)

    root = ET.Element(
        _tag("sbml"),
        {
            "level": "3",
            "version": "2",
        },
    )
    sbml_model = ET.SubElement(root, _tag("model"), {"id": model.name})

    annotation = ET.SubElement(sbml_model, _tag("annotation"))
    metadata = ET.SubElement(
        annotation,
        _bioir_tag("semanticModel"),
        {"version": model.version},
    )
    if model.provenance.source:
        metadata.set("source", model.provenance.source)
    if model.provenance.citation:
        metadata.set("citation", model.provenance.citation)

    builtin = {"dimensionless", "mole", "item", "litre", "second"}
    parameter_units = {p.unit for p in model.parameters}
    custom_units = sorted(unit for unit in parameter_units if unit not in builtin)
    if custom_units:
        definitions = ET.SubElement(sbml_model, _tag("listOfUnitDefinitions"))
        for unit in custom_units:
            _custom_unit_definition(definitions, unit, UNIT_SIGNATURES[unit])

    compartments = ET.SubElement(sbml_model, _tag("listOfCompartments"))
    for compartment in sorted(model.compartments, key=lambda x: x.id):
        attrs = {
            "id": compartment.id,
            "constant": "true",
            "size": f"{compartment.size:.17g}",
            "units": compartment.unit,
        }
        if compartment.name:
            attrs["name"] = compartment.name
        ET.SubElement(compartments, _tag("compartment"), attrs)

    species_list = ET.SubElement(sbml_model, _tag("listOfSpecies"))
    for entity in sorted(model.entities, key=lambda x: x.id):
        attrs = {
            "id": entity.id,
            "compartment": entity.compartment,
            "substanceUnits": _species_substance_unit(entity.unit),
            "boundaryCondition": "false",
            "constant": "false",
            "hasOnlySubstanceUnits": (
                "true" if entity.quantity_kind != QuantityKind.CONCENTRATION else "false"
            ),
        }
        if entity.quantity_kind == QuantityKind.CONCENTRATION:
            attrs["initialConcentration"] = f"{entity.initial_value:.17g}"
        else:
            attrs["initialAmount"] = f"{entity.initial_value:.17g}"
        if entity.name:
            attrs["name"] = entity.name
        ET.SubElement(species_list, _tag("species"), attrs)

    if model.parameters:
        parameter_list = ET.SubElement(sbml_model, _tag("listOfParameters"))
        for parameter in sorted(model.parameters, key=lambda x: x.id):
            attrs = {
                "id": parameter.id,
                "value": f"{parameter.value:.17g}",
                "units": parameter.unit,
                "constant": "true" if parameter.constant else "false",
            }
            if parameter.name:
                attrs["name"] = parameter.name
            ET.SubElement(parameter_list, _tag("parameter"), attrs)

    if model.interactions:
        reaction_list = ET.SubElement(sbml_model, _tag("listOfReactions"))
        for interaction in sorted(model.interactions, key=lambda x: x.id):
            attrs = {
                "id": interaction.id,
                "reversible": "true" if interaction.reversible else "false",
            }
            if interaction.name:
                attrs["name"] = interaction.name
            reaction = ET.SubElement(reaction_list, _tag("reaction"), attrs)

            if interaction.inputs:
                reactants = ET.SubElement(reaction, _tag("listOfReactants"))
                for participant in interaction.inputs:
                    ET.SubElement(
                        reactants,
                        _tag("speciesReference"),
                        {
                            "species": participant.entity,
                            "stoichiometry": f"{participant.stoichiometry:.17g}",
                            "constant": "true",
                        },
                    )

            if interaction.outputs:
                products = ET.SubElement(reaction, _tag("listOfProducts"))
                for participant in interaction.outputs:
                    ET.SubElement(
                        products,
                        _tag("speciesReference"),
                        {
                            "species": participant.entity,
                            "stoichiometry": f"{participant.stoichiometry:.17g}",
                            "constant": "true",
                        },
                    )

            if interaction.modifiers:
                modifiers = ET.SubElement(reaction, _tag("listOfModifiers"))
                for entity_id in interaction.modifiers:
                    ET.SubElement(
                        modifiers,
                        _tag("modifierSpeciesReference"),
                        {"species": entity_id},
                    )

            reaction_annotation = ET.SubElement(reaction, _tag("annotation"))
            semantic = ET.SubElement(
                reaction_annotation,
                _bioir_tag("interaction"),
                {
                    "kind": interaction.kind.value,
                    "mathematicalRepresentationCommitted": "false",
                },
            )
            if interaction.parameter_refs:
                semantic.set("parameterRefs", " ".join(interaction.parameter_refs))

    ET.indent(root, space="  ")
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(
        root, encoding="unicode"
    ) + "\n"
