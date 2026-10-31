"""E444: pinned SBML Test Suite semantic cases 00004-00008, no BioIR execution.

Read-only standard-library reproduction. Published trajectories are simulator
references, NOT empirical biological measurements. No real-world actuation.
"""
import csv
import io
import json
import math
import urllib.request
import xml.etree.ElementTree as ET

COMMIT = "d6dcd2cc6408d5eb881638ac6ce7a05fd7d2e4d1"
ROOT = f"https://raw.githubusercontent.com/sbmlteam/sbml-test-suite/{COMMIT}/cases/semantic"
NS = {"s": "http://www.sbml.org/sbml/level3/version2/core"}
# Frozen structural expectations: initial S1/S2, k1/k2, boundary flags,
# reactant/product stoichiometries for each reaction, end time.
CASES = {
    "00004": ((.15, 0), (.35, 180), (False, False), ((1, 2), (2, 1)), 10),
    "00005": ((.00015, .00015), (1, None), (False, False), ((1, 1),), 5),
    "00006": ((.0015, .0015), (.5, .5), (False, False), ((1, 1), (1, 1)), 5),
    "00007": ((.015, .015), (.5, .25), (True, False), ((1, 1), (1, 1)), 15),
    "00008": ((.15, .15), (.5, .25), (False, True), ((1, 1), (1, 1)), 10),
}


def check_model(xml, case):
    root = ET.fromstring(xml)
    if root.get("level") != "3" or root.get("version") != "2":
        raise ValueError("unexpected SBML version")
    model = root.find("s:model", NS)
    if model is None or model.get("id") != "case" + case:
        raise ValueError("unexpected model identity")
    compartments = model.findall("s:listOfCompartments/s:compartment", NS)
    if len(compartments) != 1 or float(compartments[0].get("size", "nan")) != 1:
        raise ValueError("nonunit compartment")
    species = model.findall("s:listOfSpecies/s:species", NS)
    if [s.get("id") for s in species] != ["S1", "S2"]:
        raise ValueError("unexpected species")
    initial = tuple(float(s.get("initialAmount", "nan")) for s in species)
    boundary = tuple(s.get("boundaryCondition") == "true" for s in species)
    parameters = {p.get("id"): float(p.get("value", "nan"))
                  for p in model.findall("s:listOfParameters/s:parameter", NS)}
    rates = (parameters.get("k1"), parameters.get("k2"))
    reactions = model.findall("s:listOfReactions/s:reaction", NS)
    pairs = []
    for index, reaction in enumerate(reactions):
        react = reaction.findall("s:listOfReactants/s:speciesReference", NS)
        prod = reaction.findall("s:listOfProducts/s:speciesReference", NS)
        if len(react) != 1 or len(prod) != 1:
            raise ValueError("unexpected reaction arity")
        expected_species = ("S1", "S2") if index == 0 else ("S2", "S1")
        if (react[0].get("species"), prod[0].get("species")) != expected_species:
            raise ValueError("unexpected reaction species")
        pairs.append((float(react[0].get("stoichiometry", "nan")),
                      float(prod[0].get("stoichiometry", "nan"))))
    expected = CASES[case]
    if (initial, rates, boundary, tuple(pairs)) != expected[:4]:
        raise ValueError("frozen model structure changed")
    # Explicitly restrict to the pinned MathML law family.
    mathml = "{http://www.w3.org/1998/Math/MathML}"
    laws = [[n.text.strip() for n in rx.findall(f".//{mathml}ci")]
            for rx in reactions]
    expected_laws = (["compartment", "k1", "S1"],)
    if len(reactions) == 2:
        expected_laws += (["compartment", "k2", "S2"],)
    if tuple(laws) != expected_laws:
        raise ValueError("unexpected kinetic identifiers")
    if case == "00004":
        powers = reactions[1].findall(f".//{mathml}power")
        exponents = [n.text.strip() for n in reactions[1].findall(f".//{mathml}cn")]
        if len(powers) != 1 or exponents != ["2"]:
            raise ValueError("unexpected nonlinear reverse law")
    return initial, rates, boundary


def oracle(case, t):
    (a, b), (k1, k2), _, _, _ = CASES[case]
    if case == "00005":
        return a * math.exp(-k1*t), b + a * (-math.expm1(-k1*t))
    if case == "00006":
        return a, b  # symmetric rates and equal initial amounts
    if case == "00007":
        target = k1*a/k2  # S1 is a fixed boundary reservoir
        return a, target + (b-target)*math.exp(-k2*t)
    if case == "00008":
        target = k2*b/k1  # S2 is a fixed boundary reservoir
        return target + (a-target)*math.exp(-k1*t), b
    return None  # 00004 is nonlinear; conservation only


def evaluate(case, xml, csv_text):
    initial, _, boundary = check_model(xml, case)
    rows = list(csv.DictReader(io.StringIO(csv_text)))
    if len(rows) != 51 or not rows or set(rows[0]) != {"time", "S1", "S2"}:
        raise ValueError("unexpected reference series")
    weight = .5 if case == "00004" else 1.
    initial_sum = sum(initial)
    initial_weighted = initial[0] + weight*initial[1]
    max_sum = max_weighted = max_oracle = 0.
    for i, row in enumerate(rows):
        t, s1, s2 = (float(row[k]) for k in ("time", "S1", "S2"))
        if not all(math.isfinite(v) for v in (t, s1, s2)):
            raise ValueError("nonfinite published result")
        if abs(t - i*CASES[case][4]/50) > 1e-10:
            raise ValueError("reference time grid changed")
        max_sum = max(max_sum, abs(s1+s2-initial_sum))
        max_weighted = max(max_weighted, abs(s1+weight*s2-initial_weighted))
        predicted = oracle(case, t)
        if predicted is not None:
            max_oracle = max(max_oracle, abs(s1-predicted[0]), abs(s2-predicted[1]))
    return {"rows": len(rows), "boundary": boundary,
            "max_naive_sum_drift": max_sum,
            "max_stoichiometric_weighted_drift": max_weighted,
            "max_analytic_error": None if case == "00004" else max_oracle}


def main():
    out = {}
    for case in CASES:
        url = f"{ROOT}/{case}/{case}"
        with urllib.request.urlopen(url + "-sbml-l3v2.xml", timeout=20) as f:
            xml = f.read().decode("utf-8")
        with urllib.request.urlopen(url + "-results.csv", timeout=20) as f:
            csv_text = f.read().decode("utf-8")
        out[case] = evaluate(case, xml, csv_text)
    print(json.dumps({"source_commit": COMMIT, "cases": out}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
