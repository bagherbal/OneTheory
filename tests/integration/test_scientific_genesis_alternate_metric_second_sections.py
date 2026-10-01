"""Independently verify the alternate V2 generating section basis.

Owns:
    Stabilizer-normalized orbit replay, exact equation columns, independently
    transposed relation minors, actual Serre closure, and basis-image checks.

Depends on:
    Actual Schoen polynomials, frozen alternate arrow data, exact integer
    arithmetic, archived section and relation streams, and pytest.

Must not:
    Import the research elimination as its own verifier, discard fixed
    monomials, use the reference I6 ray, or infer physical normalization.

Phase 0:
    Independent mathematical certificate for one actual constituent basis.
"""

import gzip
import hashlib
import json
from collections import Counter
from functools import cache

import pytest

from onetheory.math.numbers import OMEGA, Eisenstein
from onetheory.models.heterotic_schoen.geometry import schoen_geometry
from research.experiments.scientific_genesis import alternate_metric_second_sections as second
from research.experiments.scientific_genesis.mixed_schoen_common_dga import perturbed_homotopy

ROOTS = ((1, 0), (0, 1), (-1, -1))
GENERATORS = ((0, 2, 1), (1, 0, 2), (1, 1, 1), (2, 1, 0))


@cache
def _read():
    payload = json.loads(second.OUTPUT.read_text())
    digest = payload.pop("artifact_digest")
    assert hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode(
    )).hexdigest() == digest
    streams = []
    for name in ("section", "relation"):
        archive = (second.ROOT / payload[f"{name}_archive"]).read_bytes()
        assert hashlib.sha256(archive).hexdigest() == payload[f"{name}_archive_sha256"]
        raw = gzip.decompress(archive)
        assert hashlib.sha256(raw).hexdigest() == payload[f"exact_{name}_stream_sha256"]
        streams.append(json.loads(raw))
    return payload, *streams


def _product(left, right):
    c0, c1, c2 = (left[0] * right[0], left[0] * right[1] + left[1] * right[0],
                  left[1] * right[1])
    return c0 - c2, c1 - c2


def _put(values, key, value):
    old = values.get(key, (0, 0))
    new = (old[0] + value[0], old[1] + value[1])
    if new == (0, 0):
        values.pop(key, None)
    else:
        values[key] = new


def _rotate(m):
    return m[2], m[0], m[1], m[4], m[5], m[3], m[6], m[7]


def _p_phase(m, frame):
    return (frame + m[0] + 2 * m[1] + 2 * m[4] + m[5] + 2 * m[7]) % 3


def _orbit(canonical, frame):
    result = {}
    m, value = canonical, (1, 0)
    for _ in range(3):
        result[m] = value
        value = _product(value, ROOTS[_p_phase(m, frame)])
        m = _rotate(m)
        if m == canonical:
            assert value == (1, 0)
            break
    assert m == canonical
    return result


@cache
def _labels(degree, p_frame, t_frame, ideal):
    labels = set()
    x, u, base = degree
    for x0 in range(x + 1):
        for x1 in range(x - x0 + 1):
            for u0 in range(u + 1):
                for u1 in range(u - u0 + 1):
                    native = (u0, u1, u - u0 - u1)
                    if ideal and not any(all(a >= b for a, b in zip(native, g, strict=True))
                                         for g in GENERATORS):
                        continue
                    for mu in range(base + 1):
                        m = (x0, x1, x - x0 - x1, *native, mu, base - mu)
                        if (m[1] + 2 * m[2] + 2 * m[4] + m[5] + t_frame) % 3:
                            continue
                        canonical = min(m, _rotate(m), _rotate(_rotate(m)))
                        if _rotate(canonical) == canonical and _p_phase(canonical, p_frame):
                            continue
                        labels.add(canonical)
    return tuple(sorted(labels))


def _pair(value):
    assert value.a.denominator == value.b.denominator == 1
    return value.a.numerator, value.b.numerator


def _equations():
    cox = schoen_geometry().cover.cox
    polynomials = [{}, {}]
    for equation, offset, variable, scale, cubic in (
        (0, 0, 6, 1, cox.cubic_f), (0, 0, 7, 1, cox.cubic_g),
        (1, 3, 7, 2, cox.cubic_f), (1, 3, 6, 1, cox.cubic_g),
    ):
        for monomial, value in cubic.terms:
            m = [0] * 8
            m[offset:offset + 3] = monomial
            m[variable] = 1
            a, b = _pair(value)
            polynomials[equation][tuple(m)] = (scale * a, scale * b)
    return polynomials


def _eliminant():
    cox = schoen_geometry().cover.cox
    result = {}
    for sign, cubic in ((2, cox.cubic_f), (-1, cox.cubic_g)):
        for x, a in cubic.terms:
            for u, b in cubic.terms:
                coefficient = _product(_pair(a), _pair(b))
                _put(result, (*x, *u, 0, 0), (sign * coefficient[0], sign * coefficient[1]))
    return result


def test_every_exact_relation_column_replays_in_the_correct_equation_character() -> None:
    payload, _sections, relations = _read()
    cases = (
        ("subline", _labels((15, 15, 0), 0, 0, False),
         (("eliminant", _labels((12, 12, 0), 0, 0, False), 0, _eliminant()),)),
        ("quotient", _labels((15, 15, 2), 1, 2, True), (
            ("equation1", _labels((12, 15, 1), 0, 2, True), 0, _equations()[0]),
            ("equation2", _labels((15, 12, 1), 1, 2, True), 1, _equations()[1]),
        )),
    )
    assert [len(case[1]) for case in cases] == [2056, 5892]
    assert len(_labels((12, 12, 0), 0, 2, True)) == 859
    for name, target, sources in cases:
        target_index = {m: i for i, m in enumerate(target)}
        offset = 0
        for source_name, labels, frame, polynomial in sources:
            for canonical in labels:
                record = relations[name][offset]
                assert record["source"] == source_name
                assert record["source_canonical_monomial"] == list(canonical)
                full = {}
                for monomial, value in _orbit(canonical, frame).items():
                    for m, coefficient in polynomial.items():
                        image = tuple(a + b for a, b in zip(monomial, m, strict=True))
                        _put(full, image, _product(value, coefficient))
                expected = {target_index[m]: c for m, c in full.items() if m in target_index}
                actual = {row: tuple(value) for row, value in record["coordinates"]}
                assert actual == expected
                reconstructed = {}
                target_frame = 0 if name == "subline" else 1
                for row, value in expected.items():
                    for m, coefficient in _orbit(target[row], target_frame).items():
                        _put(reconstructed, m, _product(value, coefficient))
                assert reconstructed == full
                offset += 1
        assert offset == len(relations[name])
    assert payload["quotient_certificate"]["source_frame_exponents"] == [[0, 2], [1, 2]]
    assert payload["quotient_certificate"]["syzygy_frame_exponents"] == [0, 2]


def test_both_relation_minors_are_independently_invertible_by_row_elimination() -> None:
    payload, _sections, relations = _read()
    for name, expected_rank, dimension, labels in (
        ("subline", 921, 1135, _labels((15, 15, 0), 0, 0, False)),
        ("quotient", 4337, 1555, _labels((15, 15, 2), 1, 2, True)),
    ):
        cert = payload[f"{name}_certificate"]
        rows, columns = cert["pivot_rows"], cert["minor_columns"]
        assert len(rows) == len(set(rows)) == len(columns) == len(set(columns)) == expected_rank
        position = {row: i for i, row in enumerate(rows)}
        transpose = [{} for _ in rows]
        for col, source in enumerate(columns):
            for row, pair in relations[name][source]["coordinates"]:
                value = (pair[0] + 2 * pair[1]) % 7
                if row in position and value:
                    transpose[position[row]][col] = value
        pivots = {}
        for original in transpose:
            row = dict(original)
            while row:
                lead = min(row)
                previous = pivots.get(lead)
                if previous is None:
                    inverse = pow(row[lead], -1, 7)
                    pivots[lead] = {col: value * inverse % 7 for col, value in row.items()}
                    break
                coefficient = row[lead]
                for col, value in previous.items():
                    updated = (row.get(col, 0) - coefficient * value) % 7
                    if updated:
                        row[col] = updated
                    else:
                        row.pop(col, None)
            assert row
        assert len(pivots) == expected_rank
        complement = [list(m) for i, m in enumerate(labels) if i not in position]
        assert cert["basis_labels"] == complement and len(complement) == dimension
    q = payload["quotient_certificate"]
    assert q["source_dimensions"] == [2628, 2568]
    assert q["syzygy_dimension"] == 859
    assert q["structural_relation_rank_upper_bound"] == 2628 + 2568 - 859 == 4337


def _terms(record):
    section = {}
    for index, m, chart, value in record["terms"]:
        assert index in range(5) and chart in (0, 1)
        assert len(m) == 8 and all(type(e) is int for e in m)
        assert len(value) == 2 and all(type(c) is int for c in value) and any(value)
        assert all(e >= 0 for e in m[:6])
        assert all(e >= 0 or j == chart for j, e in enumerate(m[6:]))
        assert (sum(m[:3]), sum(m[3:6]), sum(m[6:])) == (
            (15, 15, 0) if index == 0 else (15, 12, 2)
        )
        key = (index, tuple(m), chart)
        assert key not in section
        section[key] = tuple(value)
    return section


def _deck(section, generator):
    output = {}
    for (index, m, chart), value in section.items():
        if generator == "P":
            phase = _p_phase(m, (0, 0, 0, 1, 0)[index])
            target, monomial = (0, 4, 1, 3, 2)[index], _rotate(m)
        else:
            phase = (m[1] + 2 * m[2] + 2 * m[4] + m[5] + (0, 1, 1, 2, 1)[index]) % 3
            target, monomial = index, m
        _put(output, (target, monomial, chart), _product(value, ROOTS[phase]))
    return output


def test_all_2690_actual_sections_are_closed_invariant_and_have_the_certified_images() -> None:
    payload, records, _relations = _read()
    constituent = second._context()[0].left
    arrows = {}
    for term in constituent.extension_terms:
        if term.source in range(1, 5):
            assert term.target == 0 and term.koszul_equation is None
            assert term.cell[2] == (0, 1) and all(len(s) == 1 for s in term.cell[:2])
            assert term.x_monomial == (0, 0, 0) and term.p_monomial == (-1, -1)
            sign = -1 if term.parent_degree == 0 else 1
            a, b = _pair(term.coefficient)
            arrows.setdefault((term.source, (*term.x_monomial, *term.u_monomial,
                                             *term.p_monomial)), {})[
                term.cell[0][0], term.cell[1][0]
            ] = (sign * a, sign * b)
    assert len(arrows) == 12
    flat = []
    for key, charts in arrows.items():
        assert set(charts) == {(x, u) for x in range(3) for u in range(3)}
        assert len(set(charts.values())) == 1
        flat.append((*key, next(iter(charts.values()))))
    assert Counter(r["kind"] for r in records) == {"subline": 1135, "quotient_lift": 1555}
    for kind, cert in (("subline", payload["subline_certificate"]),
                       ("quotient_lift", payload["quotient_certificate"])):
        assert [r["canonical_monomial"] for r in records if r["kind"] == kind] == (
            cert["basis_labels"]
        )
    expanded = 0
    for record in records:
        section = _terms(record)
        residual, image = {}, {}
        for (index, monomial, chart), value in section.items():
            if index == 0:
                sign = 1 if chart else -1
                _put(residual, monomial, (sign * value[0], sign * value[1]))
            else:
                assert section[index, monomial, 1 - chart] == value
                if chart == 1:
                    for source, m, coefficient in flat:
                        if source == index:
                            target = tuple(a + b for a, b in zip(monomial, m, strict=True))
                            _put(residual, target, _product(value, coefficient))
                else:
                    g = GENERATORS[index - 1]
                    native = tuple(a + b for a, b in zip(monomial[3:6], g, strict=True))
                    _put(image, (*monomial[:3], *native, *monomial[6:]), value)
        assert not residual
        # Plane-polynomial restrictions repeat on every vertex, and k0 has
        # no Koszul differential. No F1 component is present.
        assert _deck(section, "P") == section and _deck(section, "T") == section
        label = tuple(record["canonical_monomial"])
        if record["kind"] == "subline":
            assert section == {(0, m, chart): c for m, c in _orbit(label, 0).items()
                               for chart in (0, 1)}
        else:
            assert image == _orbit(label, 1)
            assert any(index == 0 for index, _m, _chart in section)
        expanded += 9 * len(section)
    assert len(records) == payload["section_dimension"] == 2690
    assert expanded == payload["expanded_full_cover_term_count"]


def test_fixed_orbits_fat_axis_regularity_and_actual_frame_inputs_are_not_assumed() -> None:
    payload, _sections, _relations = _read()
    assert payload["subline_fixed_orbit_counts"] == [1, 1]
    for d in (12, 15):
        fixed = (d // 3,) * 6 + (0, 0)
        assert _orbit(fixed, 0) == {fixed: (1, 0)}
        own = dict(second._orbits((d, d, 0), 0, 0, False))
        assert own[fixed] == ((fixed, 0),)
        assert fixed not in dict(second._orbits((d, d, 0), 1, 0, False))
    # Independently reconstruct the primary monomial intersection by lcms.
    primary = (((0, 1, 0), (0, 0, 2)), ((0, 0, 1), (2, 0, 0)),
               ((1, 0, 0), (0, 2, 0)))
    intersection = {tuple(max(a[i], b[i], c[i]) for i in range(3))
                    for a in primary[0] for b in primary[1] for c in primary[2]}
    minimal = {m for m in intersection if not any(
        n != m and all(a <= b for a, b in zip(n, m, strict=True)) for n in intersection
    )}
    assert minimal == set(GENERATORS)
    cox = schoen_geometry().cover.cox
    assert {m for m, _c in cox.cubic_f.terms} == {(3, 0, 0), (0, 3, 0), (0, 0, 3)}
    assert not cox.cubic_g.coefficient((1, 1, 1)).is_zero()
    assert {m for m, _c in cox.cubic_g.terms} <= {
        (3, 0, 0), (0, 3, 0), (0, 0, 3), (1, 1, 1),
    }
    _contraction, _actions, frames = second._context()
    assert [frames[1][i][i] for i in range(5)] == [
        Eisenstein(1), OMEGA, OMEGA, Eisenstein(-1, -1), OMEGA,
    ]
    assert [[str(frames[0][r][c]) for c in range(5)] for r in range(5)] == [
        ["1", "0", "0", "0", "0"], ["0", "0", "1", "0", "0"],
        ["0", "0", "0", "0", "1"], ["0", "0", "0", "omega", "0"],
        ["0", "1", "0", "0", "0"],
    ]
    assert payload["ray_character_exponents"] == [0, 1]
    assert payload["common_flat_character_twist"] == [1, 2]
    assert payload["quotient_certificate"]["source_frame_exponents"] == [[0, 2], [1, 2]]


def test_both_pole_directions_and_middle_lift_match_the_full_cover_homotopy() -> None:
    _payload, records, _relations = _read()
    selected = {}
    for r in records:
        if r["kind"] == "quotient_lift":
            selected.setdefault(tuple(r["canonical_monomial"][6:]), r)
    assert set(selected) == {(2, 0), (1, 1), (0, 2)}
    assert len(second._templates()) == 12
    contraction = second._context()[0]
    for record in selected.values():
        section = tuple(sorted(_terms(record).items()))
        expanded = second.expand_section(section)
        assert contraction.differential(expanded).is_zero()
        preimage = type(expanded)(tuple(
            (b, c) for b, c in expanded.terms if b.component.left_index
        ))
        residual = contraction.differential(preimage)
        primitive, depth = perturbed_homotopy(residual, contraction)
        assert depth == 1 and contraction.differential(primitive) == residual
        assert preimage + primitive.scale(-1) == expanded
        assert all(second.full_action(expanded, g) == expanded for g in (0, 1))
        with pytest.raises(ValueError, match="not closed"):
            second.verify_section(tuple((key, c) for key, c in section if key[0]))


def test_second_basis_closes_no_rank_four_metric_or_physical_prediction_gate() -> None:
    payload, _sections, _relations = _read()
    assert payload["second_constituent_section_basis_available"] is True
    assert payload["full_differential_template_count"] == 12
    assert all(payload[key] is False for key in (
        "rank_four_section_basis_available", "numerical_metrics_available",
        "physical_yukawas_available", "observational_inputs_used",
    ))
    for key, path in (("generation", second.GENERATION), ("alternate_cone", second.CONE)):
        parent = json.loads(path.read_text())
        assert parent["artifact_digest"] == payload["prerequisite_artifact_digests"][key]
