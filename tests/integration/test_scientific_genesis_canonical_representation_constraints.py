"""Attack the exact scope of foundational canonical-representation constraints.

Owns:
    Independent Fraction-pair products, direct modular counterexamples, boundary
    defects, basis and coefficient checks, and protection against physical overclaims.

Depends on:
    Existing exact based maps, prime-field matrices and the research analytic proof.

Must not:
    Interpret algebraic witnesses as particles, infer quantum emergence from
    declared operators, or exclude controlled approximations or finite CAR systems.

Phase 0:
    Necessary-condition verification only; the fundamental physics remains open.
"""

import json
from fractions import Fraction

import pytest

from onetheory.math.homological import LinearMap, VectorSpace
from onetheory.math.numbers import OMEGA, Eisenstein, Rational
from research.experiments.scientific_genesis import canonical_representation_constraints as module

EXECUTION_DIGEST = "3cb170379b54658324e13d9511f18de939694473790686069c5cc91e3b7f0cbf"


def _pair(value):
    if isinstance(value, Eisenstein):
        return Fraction(str(value.a)), Fraction(str(value.b))
    return Fraction(str(value)), Fraction(0)


def _multiply(left, right):
    a, b = left
    c, d = right
    return a*c - b*d, a*d + b*c - b*d


def _sum(values):
    values = tuple(values)
    return sum((a for a, _ in values), Fraction(0)), sum((b for _, b in values), Fraction(0))


def _product(left, right):
    return tuple(tuple(_sum(_multiply(_pair(left[i][k]), _pair(right[k][j]))
        for k in range(len(right))) for j in range(len(right[0]))) for i in range(len(left)))


@pytest.mark.parametrize("scalar_type", (Rational, Eisenstein))
@pytest.mark.parametrize("dimension", (1, 2, 4, 7))
def test_truncation_has_the_exact_nonzero_boundary_defect(scalar_type, dimension):
    derivative, multiplication = module.truncated_polynomial_pair(
        dimension, scalar_type=scalar_type)
    assert derivative.domain == derivative.codomain == multiplication.domain
    assert derivative.domain.basis == tuple("1" if i == 0 else f"t^{i}"
                                            for i in range(dimension))
    dx, xd = _product(derivative.rows, multiplication.rows), _product(
        multiplication.rows, derivative.rows)
    for i in range(dimension):
        for j in range(dimension):
            actual = tuple(a-b for a, b in zip(dx[i][j], xd[i][j], strict=True))
            expected = int(i == j) - dimension * int(i == j == dimension - 1)
            assert actual == (Fraction(expected), Fraction(0))
    assert module.commutator_trace(derivative, multiplication).is_zero()


@pytest.mark.parametrize("scalar_type", (Rational, Eisenstein))
def test_nonzero_trace_excludes_exact_ccr_but_zero_does_not_certify_existence(scalar_type):
    scalar = Rational(2, 7) if scalar_type is Rational else Eisenstein(1, 2)
    for dimension in (1, 2, 9):
        result = module.trace_obstruction(dimension, scalar, scalar_type=scalar_type)
        assert result["exact_finite_relation_excluded"] is True
        assert _pair(scalar * dimension) != (Fraction(0), Fraction(0))
        assert result["a_representation_constructed"] is False
    result = module.trace_obstruction(3, 0, scalar_type=scalar_type)
    assert result["exact_finite_relation_excluded"] is False
    assert result["a_representation_constructed"] is False


@pytest.mark.parametrize("dimension", (0, -1, True, 2.0))
def test_finite_dimension_must_be_explicit_and_nonzero(dimension):
    with pytest.raises(ValueError, match="positive actual"):
        module.trace_obstruction(dimension, 1, scalar_type=Rational)
    with pytest.raises(ValueError, match="positive actual"):
        module.truncated_polynomial_pair(dimension, scalar_type=Rational)


@pytest.mark.parametrize("scalar_type", (int, float, "complex"))
def test_unknown_coefficients_cannot_be_silently_identified_with_characteristic_zero(scalar_type):
    with pytest.raises(TypeError, match="explicit Rational"):
        module.trace_obstruction(2, 1, scalar_type=scalar_type)
    with pytest.raises(TypeError, match="explicit Rational"):
        module.truncated_polynomial_pair(2, scalar_type=scalar_type)
    with pytest.raises(TypeError, match="explicit Rational"):
        module.one_mode_car_pair(scalar_type=scalar_type)


def test_trace_and_commutators_reject_basis_changes_and_rectangular_maps():
    original = VectorSpace("original", ("x", "y"), Rational)
    reordered = VectorSpace("original", ("y", "x"), Rational)
    first, second = LinearMap.identity(original), LinearMap.identity(reordered)
    with pytest.raises(ValueError, match="same declared basis"):
        module.commutator_trace(first, second)
    with pytest.raises(ValueError, match="endomorphism"):
        module.trace(LinearMap(original, VectorSpace("target", ("z",)), ((1, 0),)))
    with pytest.raises(ValueError, match="endomorphism"):
        module.trace(object())


@pytest.mark.parametrize("scalar_type", (Rational, Eisenstein))
def test_noncommuting_exact_maps_still_have_zero_commutator_trace(scalar_type):
    space = VectorSpace("arithmetic trace witness", ("u", "v"), scalar_type)
    a = Rational(2, 3) if scalar_type is Rational else Eisenstein(1, 2)
    b = Rational(3, 5) if scalar_type is Rational else Eisenstein(2, -1)
    first = LinearMap(space, space, ((a, b), (1, 0)))
    second = LinearMap(space, space, ((0, 1), (b, a)))
    assert not (first.compose(second) - second.compose(first)).is_zero()
    ab, ba = _product(first.rows, second.rows), _product(second.rows, first.rows)
    independent = _sum(tuple(x-y for x, y in zip(ab[i][i], ba[i][i], strict=True))
                       for i in range(2))
    assert independent == (Fraction(0), Fraction(0))
    assert module.commutator_trace(first, second).is_zero()


@pytest.mark.parametrize("prime", (2, 3, 5))
def test_positive_characteristic_really_defeats_the_unqualified_finite_ccr_no_go(prime):
    derivative, multiplication = module.prime_characteristic_pair(prime)
    # Direct integer modular sums are independent of FiniteMatrix.matmul.
    for i in range(prime):
        for j in range(prime):
            commutator = sum(derivative.rows[i][k]*multiplication.rows[k][j]
                - multiplication.rows[i][k]*derivative.rows[k][j] for k in range(prime)) % prime
            assert commutator == int(i == j)
    assert derivative.field.element(prime) == 0
    assert Rational(prime) != 0
    # A unital scalar-ring map would preserve this sum and contradict p != 0.
    assert sum(1 for _ in range(prime)) == prime


@pytest.mark.parametrize("scalar_type", (Rational, Eisenstein))
def test_car_witness_prevents_a_false_exclusion_of_all_finite_quantum_algebras(scalar_type):
    first, second = module.one_mode_car_pair(scalar_type=scalar_type)
    ab, ba = _product(first.rows, second.rows), _product(second.rows, first.rows)
    assert module.trace(first).is_zero() and module.trace(second).is_zero()
    assert first.compose(first).is_zero() and second.compose(second).is_zero()
    for i in range(2):
        for j in range(2):
            assert tuple(a+b for a, b in zip(ab[i][j], ba[i][j], strict=True)) == (
                Fraction(int(i == j)), Fraction(0))


def test_current_symbolic_contract_is_not_a_quantum_representation():
    record = module.constraint_record()
    assert record["actual_symbolic_contract"] == {"finite_dimension": 2,
        "accepted_bracket": "commutator", "accepted_right_hand_side": "δ",
        "matrix_representation_supplied": False}
    assert record["proof_is_universal_not_witness_enumeration"] is True
    assert len(record["finite_truncation_witnesses"]) == 6
    assert [w["prime"] for w in record["positive_characteristic_counterexamples"]] == [2, 3, 5]
    for flag in ("all_finite_quantum_theories_excluded",
                 "controlled_truncation_convergence_certified",
                 "nonlinear_or_continuum_emergence_excluded", "quantum_postulates_derived",
                 "causal_geometry_derived", "gravitational_coupling_derived",
                 "dimensional_constants_derived", "genesis_to_uv_derivation_available",
                 "physical_quantum_state_generated", "observations_used"):
        assert record[flag] is False


def test_missing_representation_evidence_is_not_reconstructed_as_a_physical_fallback(
    tmp_path, monkeypatch,
):
    monkeypatch.setattr(module, "OUTPUT", tmp_path / "unavailable.json")
    with pytest.raises(FileNotFoundError):
        module.read_constraints(expected_digest="0" * 64)
    assert not module.OUTPUT.exists()


def test_different_existing_representation_evidence_is_not_overwritten(tmp_path, monkeypatch):
    output = tmp_path / "existing.json"
    output.write_text(json.dumps({"original": "scientific bytes"}))
    monkeypatch.setattr(module, "OUTPUT", output)
    with pytest.raises(ValueError, match="refusing to overwrite"):
        module.write_constraints()
    assert json.loads(output.read_text()) == {"original": "scientific bytes"}


def test_completed_mathematical_evidence_reproduces_without_deriving_quantum_physics():
    record = module.read_constraints(expected_digest=EXECUTION_DIGEST)
    assert record == module.constraint_record()
    assert record["quantum_postulates_derived"] is False
    assert record["genesis_to_uv_derivation_available"] is False


@pytest.mark.parametrize("field", (
    "quantum_postulates_derived", "genesis_to_uv_derivation_available",
    "all_finite_quantum_theories_excluded",
))
def test_rehashed_physical_or_overbroad_scope_attacks_fail_closed(field, tmp_path, monkeypatch):
    record = json.loads(module.OUTPUT.read_text())
    record[field] = True
    record.pop("artifact_digest")
    record["artifact_digest"] = module.hashlib.sha256(json.dumps(record, sort_keys=True,
        separators=(",", ":")).encode()).hexdigest()
    path = tmp_path / "changed-scope.json"
    path.write_text(json.dumps(record))
    monkeypatch.setattr(module, "OUTPUT", path)
    with pytest.raises(ValueError, match="trusted digest"):
        module.read_constraints(expected_digest=EXECUTION_DIGEST)


@pytest.mark.parametrize("change", ("dimension_alias", "boolean_alias"))
def test_a_self_hash_does_not_override_the_current_exact_scope(change, tmp_path, monkeypatch):
    record = json.loads(module.OUTPUT.read_text())
    if change == "dimension_alias":
        record["actual_symbolic_contract"]["finite_dimension"] = 2.0
    else:
        record["proof_is_universal_not_witness_enumeration"] = 1
    record.pop("artifact_digest")
    digest = module.hashlib.sha256(json.dumps(record, sort_keys=True,
        separators=(",", ":")).encode()).hexdigest()
    record["artifact_digest"] = digest
    path = tmp_path / "self-hashed-scope-attack.json"
    path.write_text(json.dumps(record))
    monkeypatch.setattr(module, "OUTPUT", path)
    with pytest.raises(ValueError, match="proof, source or exact scope"):
        module.read_constraints(expected_digest=digest)


def test_completed_reader_rechecks_the_actual_analytic_proof(tmp_path, monkeypatch):
    path = tmp_path / "changed-proof.md"
    path.write_text(module.PROOF.read_text() + "\nChanged analytic premise.\n")
    monkeypatch.setattr(module, "PROOF", path)
    with pytest.raises(ValueError, match="proof, source or exact scope"):
        module.read_constraints(expected_digest=EXECUTION_DIGEST)


def test_finite_groups_can_still_have_complex_characters_without_a_scalar_ring_embedding():
    # This ordinary exact C3 character is an algebraic counterexample to an
    # overbroad interpretation, not a generated physical quantum phase.
    assert OMEGA**3 == Eisenstein(1)
    assert OMEGA != Eisenstein(1)
    assert OMEGA.norm() == Rational(1)
