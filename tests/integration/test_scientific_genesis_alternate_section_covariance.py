"""Independently reconstruct complete original trial section covariance bounds.

Owns:
    Full-archive Fraction-pair contraction, non-diagonal exact LDL identities,
    complex conjugate routing, immutable bases, zero-error policy and scope attacks.

Depends on:
    Actual completed section columns, the research streaming covariance owner,
    independent standard-library rational arithmetic and explicit test inputs.

Must not:
    Replace the full executed basis by probes, call unit H physical, infer an
    integral or HYM convergence, or select a vacuum from trial parameters.

Phase 0:
    Mathematical covariance checks only; physical normalization remains open.
"""

import gzip
import json
from dataclasses import FrozenInstanceError, replace
from fractions import Fraction
from functools import cache
from itertools import permutations

import pytest

from onetheory.math.numbers import Eisenstein, Rational
from research.experiments.scientific_genesis import alternate_section_covariance as covariance

ZERO = Fraction(0), Fraction(0)


def _pair(value):
    return Fraction(value.a.numerator, value.a.denominator), Fraction(
        value.b.numerator, value.b.denominator)


def _add(a, b):
    return a[0] + b[0], a[1] + b[1]


def _multiply(a, b):
    return a[0]*b[0] - a[1]*b[1], a[0]*b[1] + a[1]*b[0] - a[1]*b[1]


def _conjugate(a):
    return a[0] - a[1], -a[1]


def _sum(values):
    result = ZERO
    for value in values:
        result = _add(result, value)
    return result


def _contains(ball, value):
    center = _pair(ball.center)
    a, b = value[0] - center[0], value[1] - center[1]
    radius = Fraction(ball.radius.numerator, ball.radius.denominator)
    return a*a - a*b + b*b <= radius*radius


@cache
def _records():
    targets = {0, 1273, 2655}
    with gzip.open(covariance.completed.MATRIX, "rb") as stream:
        return tuple(json.loads(line) for line in stream
                     if json.loads(line)["basis_index"] in targets)


def _exact_probe_columns():
    # Same actual coefficients, exact scalar singletons ONLY as algebraic
    # arithmetic witnesses. Their centers are NOT cover points or physical data.
    return tuple((r["basis_index"], tuple(tuple(covariance.Ball(
        Eisenstein(*(Fraction(v) for v in row[0]["center"])), 0, 80, 80,
    ) for row in matrix) for matrix in r["coefficient_columns_constant_a0_a1"]))
                 for r in _records())


@cache
def _basis_digest():
    return covariance.completed.verify_completed_output(
        expected_digest=covariance.COMPLETED_DIGEST,
    )["exact_column_stream_sha256"]


def _form(diagonal=(1, 2, 3), lower=()):
    return covariance.SectionForm(_basis_digest(), (0, 1273, 2655), diagonal, lower)


def _contract(columns, form):
    return covariance.contract_columns(columns, form, basis_digest=form.basis_digest,
        fiber_labels=("V1:F0:0", "V1:F0:2", "V2:F0:2", "V2:F0:3"), bits=80, center_bits=80)


def test_non_diagonal_ldl_matches_independent_dense_h_contraction_of_actual_columns():
    form = _form(lower=((1, 0, Eisenstein(1, 1)), (2, 0, Eisenstein(1, -1)),
                        (2, 1, Eisenstein(-1, 2))))
    columns = _exact_probe_columns()
    result = _contract(columns, form)
    # Build full H directly, unlike the producer's streaming S L columns.
    lower = [[ZERO for _ in range(3)] for _ in range(3)]
    for i in range(3):
        lower[i][i] = Fraction(1), Fraction(0)
    for i, j, scalar in form.lower:
        lower[i][j] = _pair(scalar)
    h = [[_sum(_multiply(_multiply(lower[i][k], (Fraction(form.diagonal[k].numerator,
        form.diagonal[k].denominator), Fraction(0))), _conjugate(lower[j][k]))
        for k in range(3)) for j in range(3)] for i in range(3)]
    for m in range(3):
        for n in range(3):
            for r in range(4):
                for c in range(4):
                    value = _sum(_multiply(_multiply(_pair(columns[i][1][m][r].center), h[i][j]),
                        _conjugate(_pair(columns[j][1][n][c].center)))
                        for i in range(3) for j in range(3))
                    assert _contains(result.blocks[m][n][r][c], value)


def test_complex_parameters_use_actual_conjugates_not_holomorphic_squares():
    columns, form = _exact_probe_columns(), _form(lower=((2, 0, Eisenstein(0, 1)),))
    result = _contract(columns, form)
    parameters = Eisenstein(1, 1), Eisenstein(-2, 1)
    actual = result.at(parameters)
    eta = ((Fraction(1), Fraction(0)), *(_pair(a) for a in parameters))
    reconstructed = [[_sum(_multiply(_multiply(_pair(result.blocks[m][n][r][c].center),
        eta[m]), _conjugate(eta[n])) for m in range(3) for n in range(3))
        for c in range(4)] for r in range(4)]
    assert all(_contains(actual[r][c], reconstructed[r][c]) for r in range(4) for c in range(4))
    assert all(value[1] == 0 for i, row in enumerate(reconstructed) for value in (row[i],))
    assert any(not c.center.is_zero() for row in result.blocks[1][0] for c in row)


@cache
def _full_fraction_reference():
    accum = {(m, n): [[ZERO for _ in range(4)] for _ in range(4)]
             for m in range(3) for n in range(3)}
    count = 0
    mesh = 1 << 80
    with gzip.open(covariance.completed.MATRIX, "rb") as stream:
        for line in stream:
            raw = json.loads(line)
            assert raw["basis_index"] == count
            values = []
            for matrix in raw["coefficient_columns_constant_a0_a1"]:
                column = []
                for row in matrix:
                    r = row[0]
                    center = tuple(Fraction(v) for v in r["center"])
                    # Independently implement the explicitly declared dyadic
                    # recentering. Exact singleton arithmetic stays exact.
                    if Fraction(r["radius"]) != 0:
                        center = tuple(Fraction(round(c * mesh), mesh) for c in center)
                    column.append(center)
                values.append(column)
            forbidden = ((*values[0][2:], *values[1], *values[2]) if count < 2655 else
                         (*values[0][:2], *values[1][2:], *values[2][2:]))
            assert all(value == ZERO for value in forbidden)
            for (m, n), block in accum.items():
                for r in range(4):
                    for c in range(4):
                        block[r][c] = _add(block[r][c], _multiply(
                            values[m][r], _conjugate(values[n][c])))
            count += 1
    assert count == 5345
    return accum


def test_full_5345_archive_contraction_with_independent_fraction_pairs():
    actual = covariance.declared_covariance()
    accum = _full_fraction_reference()
    assert actual.consumed_indices == tuple(range(5345))
    for (m, n), block in accum.items():
        for r in range(4):
            for c in range(4):
                assert _contains(actual.blocks[m][n][r][c], block[r][c])
    assert all(actual.blocks[n][m] == covariance._adjoint(actual.blocks[m][n])
               for m in range(3) for n in range(3))


def _determinant(matrix):
    size = len(matrix)
    result = ZERO
    for permutation in permutations(range(size)):
        sign = (-1)**sum(permutation[i] > permutation[j]
                        for i in range(size) for j in range(i + 1, size))
        value = Fraction(sign), Fraction(0)
        for i, j in enumerate(permutation):
            value = _multiply(value, matrix[i][j])
        result = _add(result, value)
    return result


def test_family_lower_bound_has_independent_positive_principal_minor_witnesses():
    actual = covariance.declared_covariance()
    certificate = covariance.unit_determinant_certificate(actual)
    reference = _full_fraction_reference()[0, 0]
    independent_minors = []
    for start, record in zip((0, 2), certificate["constituent_positive_minor_bounds"], strict=True):
        matrix = tuple(tuple(reference[i][j] for j in range(start, start + 2))
                       for i in range(start, start + 2))
        determinant = _determinant(matrix)
        assert determinant[1] == 0
        lower, upper = map(Fraction, record["determinant"])
        assert 0 < lower <= determinant[0] <= upper
        assert 0 < Fraction(record["first_principal_minor"][0]) <= matrix[0][0][0]
        independent_minors.append(determinant[0])
    bound = Fraction(certificate["all_complex_parameter_determinant_lower_bound"])
    assert 0 < bound <= independent_minors[0] * independent_minors[1]
    assert certificate["extension_parameter_choice_used"] is False
    # These complex inputs attack the general proof; they are NOT selected
    # physical extension/vacuum points or substitutes for the Schur argument.
    for params in (((1, 1), (-2, 1)), ((-3, 2), (0, 1)), ((0, 0), (0, 0))):
        eta = ((Fraction(1), Fraction(0)), *tuple(tuple(map(Fraction, p)) for p in params))
        gram = [[_sum(_multiply(_multiply(_full_fraction_reference()[m, n][i][j], eta[m]),
            _conjugate(eta[n])) for m in range(3) for n in range(3))
            for j in range(4)] for i in range(4)]
        determinant = _determinant(gram)
        assert determinant[1] == 0
        assert determinant[0] >= independent_minors[0] * independent_minors[1]


def test_uniform_unit_bound_cannot_be_applied_to_a_partial_or_nonunit_input():
    partial = _contract(_exact_probe_columns(), _form())
    with pytest.raises(ValueError, match="complete original unit-H"):
        covariance.unit_determinant_certificate(partial)
    actual = covariance.declared_covariance()
    nonunit = replace(actual, form=replace(actual.form,
        diagonal=(Rational(2), *actual.form.diagonal[1:])))
    with pytest.raises(ValueError, match="complete original unit-H"):
        covariance.unit_determinant_certificate(nonunit)


def test_actual_uncertain_columns_retain_input_radius_and_uncertain_zero_centers():
    records = _records()
    columns = tuple(covariance.decode_column(r, bits=80, center_bits=80) for r in records)
    form = _form()
    result = _contract(columns, form)
    for exact_row, bounded_row in zip(_contract(_exact_probe_columns(), form).blocks,
                                    result.blocks, strict=True):
        for exact_matrix, bounded_matrix in zip(exact_row, bounded_row, strict=True):
            for exact_entries, bounded_entries in zip(exact_matrix, bounded_matrix, strict=True):
                for exact, bounded in zip(exact_entries, bounded_entries, strict=True):
                    assert bounded.contains(exact.center)
    # Arithmetic-only perturbation of a real original zero coefficient, NOT a
    # invented physical section. Its entire uncertainty must contribute.
    changed = [list(row) for row in columns[0][1]]
    changed[1][0] = covariance.Ball(Eisenstein(0), Rational(1, 2**20), 80, 80)
    first = (columns[0][0], tuple(tuple(row) for row in changed))
    with_error = _contract((first, *columns[1:]), form)
    assert with_error.blocks[1][1][0][0].radius > result.blocks[1][1][0][0].radius


def test_explicit_weight_retains_width_and_all_hermitian_blocks():
    actual = covariance.declared_covariance()
    weight = covariance.completed.bounds.Interval(Rational(1, 2), Rational(3, 2), 80)
    blocks = covariance.weighted_blocks(actual, weight)
    for m in range(3):
        for n in range(3):
            assert blocks[n][m] == covariance._adjoint(blocks[m][n])
            for r in range(4):
                for c in range(4):
                    assert blocks[m][n][r][c].contains(actual.blocks[m][n][r][c].center)


def test_form_and_covariance_are_deeply_immutable_and_exact():
    form = _form(lower=((2, 1, Eisenstein(1, 1)), (1, 0, 0)))
    assert form.lower == ((2, 1, Eisenstein(1, 1)),)
    with pytest.raises(FrozenInstanceError):
        form.diagonal = (Rational(2),) * 3
    result = _contract(_exact_probe_columns(), form)
    mutable = [[[[c for c in row] for row in matrix] for matrix in matrices]
               for matrices in result.blocks]
    copied = replace(result, blocks=mutable)
    mutable[0][0][0][0] = None
    assert copied.blocks == result.blocks


@pytest.mark.parametrize("diagonal,lower", (
    ((1, 0, 1), ()), ((1, -1, 1), ()), ((1, 1), ()),
    ((1, 1, 1), ((0, 0, 1),)), ((1, 1, 1), ((0, 1, 1),)),
    ((1, 1, 1), ((3, 0, 1),)), ((1, 1, 1), ((True, 0, 1),)),
    ((1, 1, 1), ((2, 0, 1), (2, 0, 2))),
))
def test_invalid_or_indefinite_section_inputs_rejected(diagonal, lower):
    with pytest.raises(ValueError):
        _form(diagonal, lower)


@pytest.mark.parametrize("change", ("missing", "reordered", "duplicate", "foreign", "precision"))
def test_incompatible_column_streams_fail_closed(change):
    columns, form = _exact_probe_columns(), _form()
    if change == "missing":
        columns = columns[:-1]
    elif change == "reordered":
        columns = tuple(reversed(columns))
    elif change == "duplicate":
        columns = (columns[0], columns[0], columns[2])
    elif change == "foreign":
        with pytest.raises(ValueError, match="incompatible"):
            covariance.contract_columns(columns, form, basis_digest="0" * 64,
                fiber_labels=("f0", "f1", "f2", "f3"), bits=80, center_bits=80)
        return
    else:
        index, raw = columns[0]
        changed = [list(row) for row in raw]
        changed[0][0] = replace(changed[0][0], bits=81)
        columns = ((index, tuple(tuple(row) for row in changed)), *columns[1:])
    with pytest.raises(ValueError, match="column|incomplete"):
        _contract(columns, form)


@cache
def _record():
    return covariance.covariance_record()


def test_executed_full_packet_and_scope_reproduce():
    record = covariance.read_covariance()
    assert record == _record()
    assert record["section_count"] == 5345
    assert len(record["unweighted_blocks"]) == 3
    assert record["all_original_columns_consumed"] is True
    assert record["unit_form_is_physical_or_canonical"] is False
    assert record["hym_inverse_kernel_available"] is False
    assert record["controlled_integral_available"] is False


def test_source_archive_changes_cannot_hide_behind_cached_covariance(monkeypatch):
    covariance.declared_covariance()
    _, source = covariance.completed.fiber._verified_payload(
        covariance.completed.fiber.lifts.first.OUTPUT)
    path = covariance.ROOT / source["section_archive"]
    original = covariance.Path.read_bytes

    def altered(self):
        value = original(self)
        return value + b"changed" if self == path else value

    monkeypatch.setattr(covariance.Path, "read_bytes", altered)
    with pytest.raises(ValueError, match="original complete section archive changed"):
        covariance.covariance_record()


def test_boolean_alias_cannot_replace_an_original_index(tmp_path, monkeypatch):
    original = _record()
    changed = json.loads(json.dumps(original))
    changed["consumed_indices"][0] = False
    changed["artifact_digest"] = covariance.hashlib.sha256(
        covariance.completed._canonical(changed)).hexdigest()
    path = tmp_path / "changed.json"
    path.write_text(json.dumps(changed), encoding="utf-8")
    monkeypatch.setattr(covariance, "covariance_record", lambda: original)
    with pytest.raises(ValueError):
        covariance.read_covariance(path)


@pytest.mark.parametrize("field", ("unweighted_blocks", "weighted_cover_blocks_without_pi_cubed",
    "weighted_quotient_blocks_without_pi_cubed", "section_form", "consumed_indices",
    "proof_sha256", "complete_matrix_archive_sha256", "fiber_basis_labels",
    "unit_family_determinant_certificate",
    "coefficient_rule", "cover_weight_without_pi_cubed", "uncertain_center_bits",
    "unit_form_is_physical_or_canonical", "extension_parameters_specialized",
    "uncertain_zeros_pruned", "hym_inverse_kernel_available", "line_twist_removed",
    "independent_sampling_cloud_available", "global_integrand_bounds_available",
    "controlled_integral_available", "ricci_flat_or_hym_metric_available",
    "harmonic_matter_or_higgs_metrics_available", "physical_yukawas_available",
    "common_stabilized_vacuum_available", "observations_used"))
def test_rehashed_coefficient_input_and_scope_changes_rejected(field, tmp_path, monkeypatch):
    original = _record()
    changed = json.loads(json.dumps(original))
    value = changed[field]
    changed[field] = (not value if type(value) is bool else
                      ("changed" if isinstance(value, str) else 0))
    changed["artifact_digest"] = covariance.hashlib.sha256(
        covariance.completed._canonical(changed)).hexdigest()
    path = tmp_path / "changed.json"
    path.write_text(json.dumps(changed), encoding="utf-8")
    monkeypatch.setattr(covariance, "covariance_record", lambda: original)
    with pytest.raises(ValueError, match="source, basis, bounds or scope"):
        covariance.read_covariance(path)
