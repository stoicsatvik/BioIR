"""E423: independent SBML Test Suite stoichiometric conservation baseline.

Safe mathematical comparison of three published SBML semantic cases. This is
not a BioIR model execution, biological discovery, or wet-lab procedure.
The online run retrieves immutable source files from a pinned public commit.
"""

from __future__ import annotations

import csv
import io
import json
import math
import urllib.request
from xml.etree import ElementTree as ET

SOURCE_COMMIT = "d6dcd2cc6408d5eb881638ac6ce7a05fd7d2e4d1"
SOURCE_ROOT = (
    "https://raw.githubusercontent.com/sbmlteam/sbml-test-suite/"
    f"{SOURCE_COMMIT}/cases/semantic"
)
CASES = ("00001", "00002", "00003")
NS = {"s": "http://www.sbml.org/sbml/level3/version2/core"}


def frozen_model_parameters(xml: str) -> tuple[float, float]:
    """Reject anything outside the predeclared simple S1 -> nu*S2 family."""
    root = ET.fromstring(xml)
    model = root.find("s:model", NS)
    if model is None or root.get("level") != "3" or root.get("version") != "2":
        raise ValueError("not the frozen SBML Level 3 Version 2 model family")
    compartments = model.findall("s:listOfCompartments/s:compartment", NS)
    if len(compartments) != 1 or compartments[0].get("id") != "compartment":
        raise ValueError("unexpected compartment layout")
    if float(compartments[0].get("size", "nan")) != 1:
        raise ValueError("analytic oracle assumes unit compartment volume")
    species = model.findall("s:listOfSpecies/s:species", NS)
    initial = {s.get("id"): float(s.get("initialAmount", "nan")) for s in species}
    if set(initial) != {"S1", "S2"} or initial["S2"] != 0 or not math.isfinite(initial["S1"]):
        raise ValueError("unexpected species or initial conditions")
    parameters = {
        p.get("id"): float(p.get("value", "nan"))
        for p in model.findall("s:listOfParameters/s:parameter", NS)
    }
    if parameters.get("k1") != 1 or any(k != "k1" and v != 0 for k, v in parameters.items()):
        raise ValueError("unexpected kinetic parameter")
    reactions = model.findall("s:listOfReactions/s:reaction", NS)
    if len(reactions) not in (1, 2):
        raise ValueError("unexpected reaction count")
    if len(reactions) == 2:
        secondary = reactions[1]
        sec_r = secondary.findall("s:listOfReactants/s:speciesReference", NS)
        sec_p = secondary.findall("s:listOfProducts/s:speciesReference", NS)
        sec_ci = [n.text.strip() for n in secondary.findall(
            ".//{http://www.w3.org/1998/Math/MathML}ci"
        )]
        if (len(sec_r) != 1 or len(sec_p) != 1
                or sec_r[0].get("species") != "S2"
                or sec_p[0].get("species") != "S1"
                or sec_ci != ["compartment", "k2", "S2"]
                or parameters.get("k2") != 0):
            raise ValueError("unexpected secondary reaction")
    primary = reactions[0]
    reactants = primary.findall("s:listOfReactants/s:speciesReference", NS)
    products = primary.findall("s:listOfProducts/s:speciesReference", NS)
    if len(reactants) != 1 or len(products) != 1:
        raise ValueError("unexpected primary stoichiometry")
    if reactants[0].get("species") != "S1" or products[0].get("species") != "S2":
        raise ValueError("unexpected primary reaction species")
    if float(reactants[0].get("stoichiometry", "nan")) != 1:
        raise ValueError("unexpected primary reactant coefficient")
    coefficient = float(products[0].get("stoichiometry", "nan"))
    if not math.isfinite(coefficient) or coefficient <= 0:
        raise ValueError("invalid product coefficient")
    # Not a general MathML interpreter: the known kinetic-law form is pinned.
    identifiers = [n.text.strip() for n in primary.findall(".//{http://www.w3.org/1998/Math/MathML}ci")]
    if identifiers != ["compartment", "k1", "S1"]:
        raise ValueError("unexpected kinetic law; analytic oracle inapplicable")
    return initial["S1"], coefficient


def evaluate_rows(rows: list[tuple[float, float, float]], initial: float, coefficient: float) -> dict:
    if not rows or initial <= 0 or coefficient <= 0:
        raise ValueError("invalid reference series")
    max_analytic = max_weighted = max_naive = 0.0
    for t, s1, s2 in rows:
        if not all(math.isfinite(x) for x in (t, s1, s2)) or t < 0:
            raise ValueError("invalid time or reference observation")
        expected_s1 = initial * math.exp(-t)
        expected_s2 = coefficient * initial * (-math.expm1(-t))
        max_analytic = max(max_analytic, abs(s1 - expected_s1), abs(s2 - expected_s2))
        max_weighted = max(max_weighted, abs(s1 + s2 / coefficient - initial))
        max_naive = max(max_naive, abs(s1 + s2 - initial))
    return {
        "rows": len(rows),
        "product_stoichiometry": coefficient,
        "initial_s1": initial,
        "max_analytic_absolute_error": max_analytic,
        "max_weighted_invariant_error": max_weighted,
        "max_naive_species_sum_drift": max_naive,
        "relative_naive_species_sum_drift": max_naive / initial,
    }


def analyze_case(xml: str, csv_text: str) -> dict:
    initial, coefficient = frozen_model_parameters(xml)
    reader = csv.DictReader(io.StringIO(csv_text))
    if reader.fieldnames != ["time", "S1", "S2"]:
        raise ValueError("unexpected reference columns")
    rows = [(float(r["time"]), float(r["S1"]), float(r["S2"])) for r in reader]
    if len(rows) != 51 or rows[0][0] != 0 or rows[-1][0] != 5:
        raise ValueError("reference grid differs from frozen 0..5 by 0.1 grid")
    return evaluate_rows(rows, initial, coefficient)


def main() -> None:
    results = {}
    for case in CASES:
        url = f"{SOURCE_ROOT}/{case}/{case}"
        with urllib.request.urlopen(url + "-sbml-l3v2.xml", timeout=20) as response:
            xml = response.read().decode("utf-8")
        with urllib.request.urlopen(url + "-results.csv", timeout=20) as response:
            csv_text = response.read().decode("utf-8")
        results[case] = analyze_case(xml, csv_text)
    print(json.dumps({"source_commit": SOURCE_COMMIT, "cases": results}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
