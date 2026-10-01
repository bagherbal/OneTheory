"""Independently verify the actual first constituent's complete section basis.

Owns:
    Exact integer-polynomial replay of every archived section, full non-split
    closure, both repaired deck actions, quotient images, and basis provenance.

Depends on:
    Actual constituent arrow data, previously certified section bases,
    archived exact cochains, and the separate full-cover homotopy engine.

Must not:
    Substitute a dimension for constructed sections, reuse the compact
    verification algorithm as its own oracle, or claim metrics or predictions.

Phase 0:
    Independent research certificate for one actual rank-two section basis.
"""

import gzip
import hashlib
import json
from collections import Counter
from functools import cache
from pathlib import Path

import pytest

from onetheory.math.numbers import Eisenstein
from research.experiments.scientific_genesis import alternate_metric_first_serre_lifts as lifts
from research.experiments.scientific_genesis.mixed_constituent_schoen_arrows import (
    mixed_schoen_constituents,
)

ROOT = Path(__file__).resolve().parents[2]


def _digest_payload(path):
    record = json.loads(path.read_text())
    digest = record.pop("artifact_digest")
    assert digest == hashlib.sha256(json.dumps(
        record, sort_keys=True, separators=(",", ":"),
    ).encode()).hexdigest()
    return digest, record


@cache
def _read():
    _digest, payload = _digest_payload(lifts.OUTPUT)
    archive = (ROOT / payload["section_archive"]).read_bytes()
    assert hashlib.sha256(archive).hexdigest() == payload["section_archive_sha256"]
    raw = gzip.decompress(archive)
    assert hashlib.sha256(raw).hexdigest() == payload["exact_section_stream_sha256"]
    return payload, json.loads(raw)


def _product(left, right):
    # Multiply in Z[t], then reduce t^2 = -1-t independently of the engine.
    coefficients = [left[0] * right[0],
                    left[0] * right[1] + left[1] * right[0], left[1] * right[1]]
    return coefficients[0] - coefficients[2], coefficients[1] - coefficients[2]


def _put(values, key, coefficient):
    previous = values.get(key, (0, 0))
    value = (previous[0] + coefficient[0], previous[1] + coefficient[1])
    if value == (0, 0):
        values.pop(key, None)
    else:
        values[key] = value


ROOTS = ((1, 0), (0, 1), (-1, -1))


def _rotate(m):
    return m[2], m[0], m[1], m[4], m[5], m[3], m[6], m[7]


def _orbit(m, frame):
    result = {}
    value = (1, 0)
    seed = m
    for _ in range(3):
        _put(result, m, value)
        phase = frame + m[0] + 2 * m[1] + 2 * m[4] + m[5] + 2 * m[7]
        value = _product(value, ROOTS[phase % 3])
        m = _rotate(m)
    assert m == seed and value == (1, 0)
    return result


def _deck(section, generator):
    result = {}
    for (index, m, chart), value in section.items():
        if generator == "P":
            phase = m[0] + 2 * m[1] + 2 * m[4] + m[5] + 2 * m[7]
            target = (0, 3, 1, 2)[index]
            phase += (0, 2, 0, 1)[index]
            monomial = _rotate(m)
        else:
            phase = m[1] + 2 * m[2] + 2 * m[4] + m[5] + (2, 0, 1, 2)[index]
            target = index
            monomial = m
        _put(result, (target, monomial, chart), _product(value, ROOTS[phase % 3]))
    return result


@cache
def _arrows():
    first = mixed_schoen_constituents()[0]
    result = {}
    for term in first.extension_terms:
        if term.source not in (1, 2, 3):
            continue
        assert term.target == 0 and term.koszul_equation is None
        assert term.p_monomial == (-1, -1) and term.u_monomial == (0, 0, 0)
        assert term.cell[2] == (0, 1) and all(len(s) == 1 for s in term.cell[:2])
        assert term.parent_degree in (0, 1)
        assert all(e >= 0 for e in term.x_monomial)
        assert term.coefficient.a.denominator == term.coefficient.b.denominator == 1
        sign = -1 if term.parent_degree == 0 else 1
        value = (sign * term.coefficient.a.numerator, sign * term.coefficient.b.numerator)
        monomial = term.x_monomial + term.u_monomial + term.p_monomial
        result.setdefault((term.source, monomial), {})[
            term.cell[0][0], term.cell[1][0]
        ] = value
    assert len(result) == 6
    arrows = []
    for (source, monomial), charts in result.items():
        assert set(charts) == {(x, u) for x in range(3) for u in range(3)}
        assert len(set(charts.values())) == 1
        arrows.append((source, monomial, next(iter(charts.values()))))
    return arrows


def _section(record):
    result = {}
    for index, monomial, chart, value in record["terms"]:
        assert index in range(4) and chart in (0, 1)
        assert len(monomial) == 8 and all(type(e) is int for e in monomial)
        assert len(value) == 2 and all(type(c) is int for c in value)
        assert tuple(value) != (0, 0)
        assert all(e >= 0 for e in monomial[:6])
        assert all(e >= 0 or coordinate == chart for coordinate, e in enumerate(monomial[6:]))
        assert (sum(monomial[:3]), sum(monomial[3:6]), sum(monomial[6:])) == (
            (13, 17, 0) if index == 0 else (11, 17, 2)
        )
        key = (index, tuple(monomial), chart)
        assert key not in result
        result[key] = tuple(value)
    return result


def test_every_actual_section_is_closed_in_the_non_split_complex_and_deck_fixed() -> None:
    """Replay every coefficient exactly, not a modular sample or hash-only gate."""

    payload, records = _read()
    arrows = _arrows()
    expanded = 0
    for record in records:
        section = _section(record)
        overlap = {}
        for (index, monomial, chart), value in section.items():
            if index == 0:
                sign = 1 if chart == 1 else -1
                _put(overlap, monomial, (sign * value[0], sign * value[1]))
            else:
                assert section[index, monomial, 1 - chart] == value
                if chart == 1:
                    for source, arrow_monomial, coefficient in arrows:
                        if source == index:
                            image = tuple(a + b for a, b in zip(
                                monomial, arrow_monomial, strict=True,
                            ))
                            _put(overlap, image, _product(value, coefficient))
        assert not overlap
        # All plane restrictions are polynomial and copied to all nine
        # vertices, so their two Cech directions cancel identically.
        # k0 has no Koszul differential; these sections have no F1 terms.
        assert _deck(section, "P") == section
        assert _deck(section, "T") == section
        expanded += 9 * len(section)
    assert expanded == payload["expanded_full_cover_term_count"]


def test_every_lift_has_the_certified_quotient_image_and_subline_injection() -> None:
    """An exact H0 sequence proves independence of the entire 2655-vector basis."""

    payload, records = _read()
    _, subline = _digest_payload(lifts.SUBLINE)
    _, quotient = _digest_payload(lifts.QUOTIENT)
    assert Counter(record["kind"] for record in records) == {"subline": 1115, "quotient_lift": 1540}
    assert [r["canonical_monomial"] for r in records if r["kind"] == "subline"] == (
        subline["quotient_basis_monomials_x_u"]
    )
    assert [r["canonical_monomial"] for r in records if r["kind"] == "quotient_lift"] == (
        quotient["quotient_basis_canonical_monomials"]
    )
    generators = ((1, 1, 0), (1, 0, 1), (0, 1, 1))
    for record in records:
        section = _section(record)
        label = tuple(record["canonical_monomial"])
        if record["kind"] == "subline":
            expected = {(0, m, chart): c for m, c in _orbit((*label, 0, 0), 0).items()
                        for chart in (0, 1)}
            assert section == expected
        else:
            image = {}
            for (index, monomial, chart), value in section.items():
                if index and chart == 0:
                    g = generators[index - 1]
                    target = tuple(a + b for a, b in zip(monomial[:3], g, strict=True))
                    _put(image, (*target, *monomial[3:]), value)
            assert image == _orbit(label, 2)
            assert any(index == 0 for index, _m, _chart in section)
    assert payload["section_dimension"] == 1115 + 1540 == 2655


def test_polynomial_template_transport_matches_the_separate_full_cover_homotopy() -> None:
    """Attack compression at both pole directions and the regular middle case."""

    _, records = _read()
    selected = {}
    for record in records:
        if record["kind"] == "quotient_lift":
            selected.setdefault(tuple(record["canonical_monomial"][6:]), record)
    assert set(selected) == {(2, 0), (1, 1), (0, 2)}
    assert len(lifts.first_lift_templates()) == 9
    for record in selected.values():
        canonical = tuple(record["canonical_monomial"])
        actual = lifts.compressed_first_quotient_section(canonical)
        assert actual == tuple(sorted(_section(record).items()))
        expanded = lifts.expand_section(actual)
        reference = lifts.lift_first_quotient_section(canonical)
        assert expanded == reference.invariant_lift
        assert reference.homotopy_depth == 1
        assert lifts._context()[0].differential(expanded).is_zero()
        for generator in (0, 1):
            assert lifts._action(expanded, generator) == expanded
    # Keep the actual non-split correction indispensable.
    record = next(iter(selected.values()))
    terms = tuple((key, value) for key, value in _section(record).items() if key[0] != 0)
    with pytest.raises(ValueError, match="not closed"):
        lifts.verify_compact_section(terms)


def test_complete_first_basis_does_not_claim_second_basis_metrics_or_physical_yukawas() -> None:
    payload, _records = _read()
    assert payload["first_constituent_section_basis_available"] is True
    assert payload["twist_cover_degree"] == [14, 16, 1]
    assert payload["common_flat_character_twist"] == [1, 2]
    assert payload["full_differential_template_count"] == 9
    assert payload["coefficient_ring"] == "Z[omega], omega^2+omega+1=0"
    for name, path in (("subline", lifts.SUBLINE), ("quotient", lifts.QUOTIENT),
                       ("generation", lifts.GENERATION)):
        digest, _record = _digest_payload(path)
        assert payload["prerequisite_artifact_digests"][name] == digest
    assert all(payload[flag] is False for flag in (
        "second_constituent_section_basis_available", "rank_four_section_basis_available",
        "numerical_metrics_available", "physical_yukawas_available", "observational_inputs_used",
    ))
    # Source-checked repaired homogeneous blocks used by the independent action formula.
    _, _, frames = lifts._context()
    assert [[str(frames[0][row][column]) for column in range(4)] for row in range(4)] == [
        ["1", "0", "0", "0"], ["0", "0", "1", "0"],
        ["0", "0", "0", "omega"], ["0", "-1-omega", "0", "0"],
    ]
    assert [frames[1][i][i] for i in range(4)] == (
        [Eisenstein(0, -1) - 1, Eisenstein(1), Eisenstein(0, 1), Eisenstein(-1, -1)]
    )
