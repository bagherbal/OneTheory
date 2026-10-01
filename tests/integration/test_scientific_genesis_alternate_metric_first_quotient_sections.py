"""Independently verify the actual first Serre-quotient section basis.

Owns:
    Frozen-source equation replay, independent ideal orbit labels, transposed
    minor elimination, archive integrity, and exact epistemic scope checks.

Depends on:
    The published Schoen cubics, actual repaired first frames, integral relation
    archive, standard-library exact modular arithmetic, and pytest.

Must not:
    Import the research relation or elimination algorithms as their own
    verifier, invent Serre lifts, or interpret finite fields as physical data.

Phase 0:
    Independent algebraic certificate for one actual quotient section space.
"""

import gzip
import hashlib
import json
from pathlib import Path

from onetheory.models.heterotic_schoen.geometry import schoen_geometry
from research.experiments.scientific_genesis import (
    alternate_metric_first_quotient_sections as quotient,
)

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "data/generated/scientific_genesis/alternate_metric_first_quotient_sections.json"
PRIME = 7
OMEGA = 2


def _monomials(x, u, p):
    for x0 in range(x + 1):
        for x1 in range(x - x0 + 1):
            x2 = x - x0 - x1
            if sum(value > 0 for value in (x0, x1, x2)) < 2:
                continue
            for u0 in range(u + 1):
                for u1 in range(u - u0 + 1):
                    for mu in range(p + 1):
                        yield (x0, x1, x2, u0, u1, u - u0 - u1, mu, p - mu)


def _rotate(m):
    return m[2], m[0], m[1], m[4], m[5], m[3], m[6], m[7]


def _labels(x, u, p):
    selected = set()
    for monomial in _monomials(x, u, p):
        if (monomial[1] + 2 * monomial[2] + 2 * monomial[4] + monomial[5] + 2) % 3:
            continue
        orbit = (monomial, _rotate(monomial), _rotate(_rotate(monomial)))
        assert len(set(orbit)) == 3
        selected.add(min(orbit))
    return tuple(sorted(selected))


def _orbit(canonical, frame):
    monomial = canonical
    coefficient = 1
    result = []
    for _ in range(3):
        result.append((monomial, coefficient))
        exponent = frame + monomial[0] + 2 * monomial[1] + 2 * monomial[4]
        exponent += monomial[5] + 2 * monomial[7]
        coefficient = coefficient * pow(OMEGA, exponent, PRIME) % PRIME
        monomial = _rotate(monomial)
    assert monomial == canonical and coefficient == 1
    return result


def _equations():
    """Read actual coefficient polynomials; do not assume a Fermat pencil."""

    cox = schoen_geometry().cover.cox
    result = [[], []]
    for equation, block, variable, multiplier, polynomial in (
        (0, 0, 6, 1, cox.cubic_f), (0, 0, 7, 1, cox.cubic_g),
        (1, 3, 7, 2, cox.cubic_f), (1, 3, 6, 1, cox.cubic_g),
    ):
        for monomial, value in polynomial.terms:
            assert value.a.denominator == value.b.denominator == 1
            exponent = [0] * 8
            exponent[block:block + 3] = monomial
            exponent[variable] = 1
            coefficient = multiplier * (value.a.numerator + OMEGA * value.b.numerator) % PRIME
            result[equation].append((tuple(exponent), coefficient))
    return result


def _read():
    payload = json.loads(OUTPUT.read_text())
    digest = payload.pop("artifact_digest")
    assert digest == hashlib.sha256(json.dumps(
        payload, sort_keys=True, separators=(",", ":"),
    ).encode()).hexdigest()
    archive = (ROOT / payload["relation_archive"]).read_bytes()
    assert hashlib.sha256(archive).hexdigest() == payload["relation_archive_sha256"]
    raw = gzip.decompress(archive)
    assert hashlib.sha256(raw).hexdigest() == payload["exact_integral_relation_columns_sha256"]
    return payload, json.loads(raw)


def test_every_integral_relation_column_has_the_actual_equation_image_mod_seven() -> None:
    """Replay every source polynomial independently before trusting its rank."""

    payload, columns = _read()
    target = _labels(13, 17, 2)
    assert len(target) == 5814
    index = {label: row for row, label in enumerate(target)}
    sources = ((_labels(10, 17, 1), 1), (_labels(13, 14, 1), 2))
    assert [len(labels) for labels, _frame in sources] == [2394, 2720]
    assert len(_labels(10, 14, 0)) == 840
    equations = _equations()
    offset = 0
    for equation, (labels, frame) in enumerate(sources):
        for canonical in labels:
            record = columns[offset]
            assert record["equation"] == equation + 1
            assert record["source_canonical_monomial"] == list(canonical)
            image = {}
            for monomial, scalar in _orbit(canonical, frame):
                for equation_monomial, coefficient in equations[equation]:
                    product = tuple(a + b for a, b in zip(
                        monomial, equation_monomial, strict=True,
                    ))
                    image[product] = (image.get(product, 0) + scalar * coefficient) % PRIME
            expected = {index[m]: value for m, value in image.items() if m in index and value}
            actual = {
                row: (pair[0] + OMEGA * pair[1]) % PRIME
                for row, pair in record["coordinates"]
                if (pair[0] + OMEGA * pair[1]) % PRIME
            }
            assert actual == expected
            # Projection to canonical terms reconstructs the entire image.
            full = {
                m: value * coefficient % PRIME
                for row, value in expected.items()
                for m, coefficient in _orbit(target[row], 2)
                if value * coefficient % PRIME
            }
            assert full == {m: value for m, value in image.items() if value}
            offset += 1
    assert offset == len(columns) == 5114
    assert payload["ideal_koszul_syzygy_dimension"] == 840


def test_selected_exact_relation_minor_is_invertible_by_independent_row_elimination() -> None:
    """A transposed sparse minor verifies the same complement without column code."""

    payload, columns = _read()
    rows = payload["relation_minor_pivot_rows"]
    chosen_columns = payload["relation_minor_column_indices"]
    assert len(rows) == len(set(rows)) == len(chosen_columns) == len(set(chosen_columns)) == 4274
    row_index = {row: index for index, row in enumerate(rows)}
    transpose = [{} for _ in rows]
    for column_index, source_index in enumerate(chosen_columns):
        for row, pair in columns[source_index]["coordinates"]:
            if row in row_index:
                value = (pair[0] + OMEGA * pair[1]) % PRIME
                if value:
                    transpose[row_index[row]][column_index] = value
    pivots = {}
    for original in transpose:
        row = dict(original)
        while row:
            lead = min(row)
            previous = pivots.get(lead)
            if previous is None:
                inverse = pow(row[lead], -1, PRIME)
                pivots[lead] = {column: value * inverse % PRIME for column, value in row.items()}
                break
            factor = row[lead]
            for column, value in previous.items():
                updated = (row.get(column, 0) - factor * value) % PRIME
                if updated:
                    row[column] = updated
                else:
                    row.pop(column, None)
        assert row, "the claimed nonzero minor has a dependent row"
    assert len(pivots) == 4274 == payload["certified_relation_minor_rank"]
    target = _labels(13, 17, 2)
    pivot_set = set(rows)
    basis = [list(m) for index, m in enumerate(target) if index not in pivot_set]
    assert basis == payload["quotient_basis_canonical_monomials"]
    assert len(basis) == len({tuple(m) for m in basis}) == 1540
    assert payload["structural_relation_rank_upper_bound"] == 2394 + 2720 - 840 == 4274
    assert payload["quotient_section_dimension"] == 5814 - 4274 == 1540


def test_actual_ideal_frame_regular_sequence_inputs_and_scope_are_explicit() -> None:
    """Keep the genuine quotient space distinct from the still missing Serre lifts."""

    payload, _columns = _read()
    quotient._inputs()  # Source-level exact Hilbert--Burch/frame identities.
    cox = schoen_geometry().cover.cox
    assert {m for m, _c in cox.cubic_f.terms} == {(3, 0, 0), (0, 3, 0), (0, 0, 3)}
    assert not cox.cubic_g.coefficient((1, 1, 1)).is_zero()
    # The actual G has pure-cube terms too; replacing it by xyz is invalid.
    assert all(not cox.cubic_g.coefficient(m).is_zero()
               for m in ((3, 0, 0), (0, 3, 0), (0, 0, 3)))
    assert payload["actual_ideal_image_frame_p_t_exponents"] == [2, 2]
    assert payload["ideal_image_degree"] == [13, 17, 2]
    assert payload["certificate_prime"] == PRIME
    assert payload["certificate_omega_residue"] == OMEGA
    assert (OMEGA * OMEGA + OMEGA + 1) % PRIME == 0
    for key, filename in (
        ("ambient", "alternate_metric_first_resolution_ambient_sections.json"),
        ("generation", "alternate_metric_quotient_generation.json"),
    ):
        source = json.loads((OUTPUT.parent / filename).read_text())
        assert payload["prerequisite_artifact_digests"][key] == source["artifact_digest"]
    assert all(payload[key] is False for key in (
        "serre_lifts_constructed", "full_constituent_section_basis_available",
        "rank_four_section_basis_available", "numerical_metrics_available",
        "physical_yukawas_available", "observational_inputs_used",
    ))
