"""Independently replay actual invariant ambient resolution sections.

Owns:
    Integer-pair arithmetic in Z[omega], independent block orbit construction,
    complete stream hashes, deck invariance, and the ambient/restricted boundary.

Depends on:
    Frozen deck substitutions and constituent frames, generated artifacts,
    standard-library hashing, and pytest.

Must not:
    Reuse the research sparse action implementation as its own verifier or
    identify these ambient vectors with restricted carrier sections or metrics.

Phase 0:
    Independent exact verification of research inputs for the section quotient.
"""

import hashlib
import json
from collections import Counter
from itertools import product
from pathlib import Path

import pytest

from research.experiments.scientific_genesis import (
    alternate_metric_first_resolution_ambient_sections as ambient,
)

ROOT = Path(__file__).resolve().parents[2]
ARTIFACT = ROOT / (
    "data/generated/scientific_genesis/alternate_metric_first_resolution_ambient_sections.json"
)
ROOTS = ((1, 0), (0, 1), (-1, -1))
TEXT = {
    (1, 0): "1", (-1, 0): "-1", (0, 1): "omega", (0, -1): "-omega",
    (-1, -1): "-1-omega", (1, 1): "1+omega",
}
P_FRAMES = {
    "F0": ((0, 1, 0), (0, 0, 2), (4, 0, 0)),
    "F1": ((0, 4), (3, 3)),
}
# Entries above are evaluations in F7 at omega=2; the six nonzero residues
# distinguish every signed cubic root used by these integral block frames.
RESIDUE_PAIRS = {1: ROOTS[0], 2: ROOTS[1], 4: ROOTS[2], 3: (1, 1)}


def _multiply(left, right):
    a, b = left
    c, d = right
    return (a * c - b * d, a * d + b * c - b * d)


def _add(left, right):
    return tuple(a + b for a, b in zip(left, right, strict=True))


def _p_monomial(monomial):
    x0, x1, x2, u0, u1, u2, mu, nu = monomial
    return (
        ROOTS[(x0 + 2 * x1 + 2 * u1 + u2 + 2 * nu) % 3],
        (x2, x0, x1, u1, u2, u0, mu, nu),
    )


def _t_weight(monomial):
    return (monomial[1] + 2 * monomial[2] + 2 * monomial[4] + monomial[5]) % 3


def _p_section(section, role):
    result = {}
    for (block, monomial), value in section.items():
        coordinate_scalar, image = _p_monomial(monomial)
        for target, row in enumerate(P_FRAMES[role]):
            if not row[block]:
                continue
            label = target, image
            coefficient = _multiply(
                _multiply(value, coordinate_scalar), RESIDUE_PAIRS[row[block]],
            )
            result[label] = _add(result.get(label, (0, 0)), coefficient)
    return {label: value for label, value in result.items() if value != (0, 0)}


def _t_section(section, role):
    return {
        (block, monomial): _multiply(
            value, ROOTS[(_t_weight(monomial) + (block if role == "F0" else 2)) % 3],
        )
        for (block, monomial), value in section.items()
    }


def _orbit_sum(label, role):
    section = {label: (1, 0)}
    result = {}
    for _ in range(3):
        for term, value in section.items():
            result[term] = _add(result.get(term, (0, 0)), value)
        section = _p_section(section, role)
    assert section == {label: (1, 0)}
    return {term: value for term, value in result.items() if value != (0, 0)}


def _monomials(x_degree, u_degree):
    for x0 in range(x_degree + 1):
        for x1 in range(x_degree - x0 + 1):
            for u0 in range(u_degree + 1):
                for u1 in range(u_degree - u0 + 1):
                    for mu in range(3):
                        yield (x0, x1, x_degree - x0 - x1,
                               u0, u1, u_degree - u0 - u1, mu, 2 - mu)


def _generators(role):
    seen = set()
    degree, rank = (11, 3) if role == "F0" else (10, 2)
    for monomial in _monomials(degree, 17):
        if role == "F0":
            for block in range(rank):
                label = block, monomial
                if label in seen or (_t_weight(monomial) + block) % 3:
                    continue
                orbit = []
                current = label
                for _ in range(3):
                    orbit.append(current)
                    _scalar, image = _p_monomial(current[1])
                    current = (current[0] - 1) % 3, image
                assert current == label and len(set(orbit)) == 3
                seen.update(orbit)
                canonical = min(orbit)
                yield canonical, _orbit_sum(canonical, role)
        else:
            if monomial in seen:
                continue
            orbit = []
            current = monomial
            for _ in range(3):
                orbit.append(current)
                _scalar, current = _p_monomial(current)
            assert current == monomial and len(set(orbit)) == 3
            seen.update(orbit)
            if (_t_weight(monomial) + 2) % 3:
                continue
            for block in range(rank):
                label = block, min(orbit)
                section = _orbit_sum(label, role)
                assert section[label] == (1, 0)
                assert section.get((1 - block, label[1]), (0, 0)) == (0, 0)
                yield label, section


def test_actual_frames_and_coordinate_lifts_match_the_independent_replay() -> None:
    """The verifier's explicit substitutions are checked against frozen sources."""

    p, t, f0, f1 = ambient._first_blocks()
    expected_p = (
        (("omega", (0, 1, 0)), ("-1-omega", (0, 0, 1)), ("1", (1, 0, 0))),
        (("1", (0, 0, 1)), ("-1-omega", (1, 0, 0)), ("omega", (0, 1, 0))),
        (("1", (1, 0)), ("-1-omega", (0, 1))),
    )
    expected_t = (
        (("1", (1, 0, 0)), ("omega", (0, 1, 0)), ("-1-omega", (0, 0, 1))),
        (("1", (1, 0, 0)), ("-1-omega", (0, 1, 0)), ("omega", (0, 0, 1))),
        (("1", (1, 0)), ("1", (0, 1))),
    )
    for action, expected in ((p, expected_p), (t, expected_t)):
        assert tuple(
            tuple((str(value), monomial) for value, monomial in images)
            for images in (action.x_images, action.u_images, action.p_images)
        ) == expected
    artifact = json.loads(ARTIFACT.read_text())
    for role, frames, record in zip(("F0", "F1"), (f0, f1), artifact["blocks"], strict=True):
        assert record["role"] == role
        assert record["p_frame"] == [[str(value) for value in row] for row in frames[0].rows]
        assert record["t_frame"] == [[str(value) for value in row] for row in frames[1].rows]
        for row in frames[0].rows + frames[1].rows:
            assert all(value.a.denominator == value.b.denominator == 1 for value in row)
        assert tuple(tuple((value.a.numerator, value.b.numerator) for value in row)
                     for row in frames[0].rows) == tuple(
            tuple(RESIDUE_PAIRS.get(value, (0, 0)) for value in row)
            for row in P_FRAMES[role]
        )
        assert tuple(tuple((value.a.numerator, value.b.numerator) for value in row)
                     for row in frames[1].rows) == tuple(
            tuple(ROOTS[row if role == "F0" else 2] if row == column else (0, 0)
                  for column in range(len(P_FRAMES[role])))
            for row in range(len(P_FRAMES[role]))
        )


@pytest.mark.parametrize("role,expected", (("F0", 13338), ("F1", 7524)))
def test_complete_stream_matches_independent_integer_ring_replay(role, expected) -> None:
    """Every exact section, not just its count or a sample, is independently replayed."""

    artifact = json.loads(ARTIFACT.read_text())
    claimed_digest = artifact.pop("artifact_digest")
    assert claimed_digest == hashlib.sha256(json.dumps(
        artifact, sort_keys=True, separators=(",", ":"),
    ).encode()).hexdigest()
    record = next(item for item in artifact["blocks"] if item["role"] == role)
    digest = hashlib.sha256()
    count = 0
    for label, section in _generators(role):
        assert _p_section(section, role) == _t_section(section, role) == section
        item = {
            "label": [label[0], list(label[1])],
            "terms": [[block, list(monomial), TEXT[value]]
                      for (block, monomial), value in sorted(section.items())],
        }
        if not count:
            assert item == record["first_generator"]
        digest.update(json.dumps(item, sort_keys=True, separators=(",", ":")).encode())
        digest.update(b"\n")
        count += 1
    assert count == expected == record["ambient_invariant_generator_count"]
    assert digest.hexdigest() == record["ordered_generator_stream_sha256"]
    for name, filename in (
        ("generation", "alternate_metric_quotient_generation.json"),
        ("alternate_cone", "alternate_constituent_outer_universal_cone.json"),
    ):
        source = json.loads((ARTIFACT.parent / filename).read_text())
        assert artifact["prerequisite_artifact_digests"][name] == source["artifact_digest"]
    assert artifact["common_flat_character_twist"] == [1, 2]
    assert artifact["twist_cover_degree"] == [14, 16, 1]
    assert all(artifact[flag] is False for flag in (
        "individual_f0_lines_descended", "restricted_hilbert_burch_quotient_basis_available",
        "first_constituent_section_basis_available", "numerical_metrics_available",
        "observational_inputs_used",
    ))


def test_integer_pair_ring_has_an_independent_finite_field_check() -> None:
    """Both embeddings omega=2,4 of Z[omega] into F7 respect multiplication."""

    for left, right, omega in product(TEXT, TEXT, (2, 4)):
        result = _multiply(left, right)
        assert (result[0] + omega * result[1]) % 7 == (
            (left[0] + omega * left[1]) * (right[0] + omega * right[1]) % 7
        )


@pytest.mark.parametrize("role,x_degree,expected", (
    ("F0", 11, (13338, 5130, 6240, 1800, 3768)),
    ("F1", 10, (7524, 2736, 3520, 960, 2228)),
))
def test_actual_koszul_dimension_targets_follow_from_character_counts(
    role, x_degree, expected,
) -> None:
    """Independent character counting fixes the restriction target, not its basis."""

    def weights(degree, sign):
        return Counter(
            sign * (b + 2 * (degree - a - b)) % 3
            for a in range(degree + 1) for b in range(degree - a + 1)
        )

    dimensions = []
    for x, u, p in ((x_degree, 17, 2), (x_degree - 3, 17, 1),
                    (x_degree, 14, 1), (x_degree - 3, 14, 0)):
        x_weights, u_weights = weights(x, 1), weights(u, -1)
        frames = (0, 1, 2) if role == "F0" else (2, 2)
        t_fixed = (p + 1) * sum(
            x_count * u_count
            for (x_weight, x_count), (u_weight, u_count), frame in product(
                x_weights.items(), u_weights.items(), frames,
            )
            if (x_weight + u_weight + frame) % 3 == 0
        )
        assert t_fixed % 3 == 0
        dimensions.append(t_fixed // 3)
    restricted = dimensions[0] - dimensions[1] - dimensions[2] + dimensions[3]
    assert (*dimensions, restricted) == expected
