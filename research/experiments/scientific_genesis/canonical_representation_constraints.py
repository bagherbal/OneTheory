"""Check exact scalar and operator prerequisites of canonical quantum claims.

Owns:
    Finite characteristic-zero commutator obstructions, explicit truncation
    defects, positive-characteristic counterexamples and a finite CAR witness.

Depends on:
    Existing based exact linear maps, rational/Eisenstein arithmetic, prime-field
    matrices and the symbolic quantum contract being inspected.

Must not:
    Derive quantum postulates, equate finite-field arithmetic with complex
    quantum theory, construct a physical particle, or supply a Genesis adapter.

Phase 0:
    Research necessary-condition audit only; no quantum emergence is asserted.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from onetheory.math.finite import FiniteMatrix, PrimeField
from onetheory.math.homological import LinearMap, VectorSpace
from onetheory.math.numbers import Eisenstein, Rational, coerce_rational
from onetheory.physics.quantum import CanonicalRelation, HilbertSpace, Operator

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/canonical_representation_constraints.json"
PROOF = Path(__file__).with_name("CANONICAL_REPRESENTATION_CONSTRAINTS_NOTE.md")
QUANTUM = ROOT / "src/onetheory/physics/quantum.py"


def _dimension(dimension):
    if type(dimension) is not int or dimension < 1:
        raise ValueError("a positive actual finite dimension is required")


def _scalar(value, scalar_type):
    if scalar_type is Rational:
        return coerce_rational(value)
    if scalar_type is Eisenstein:
        return Eisenstein.coerce(value)
    raise TypeError("explicit Rational or Eisenstein coefficients are required")


def trace(map_):
    """Use the declared basis of one exact finite endomorphism, without rebasing."""

    if not isinstance(map_, LinearMap) or map_.domain != map_.codomain:
        raise ValueError("a based exact endomorphism is required")
    return sum((map_.rows[i][i] for i in range(map_.domain.dimension)),
               _scalar(0, map_.domain.scalar_type))


def commutator_trace(left, right):
    """Compute the trace with existing typed composition, not a new matrix engine."""

    if (not isinstance(left, LinearMap) or not isinstance(right, LinearMap)
        or left.domain != left.codomain or right.domain != right.codomain
        or left.domain != right.domain):
        raise ValueError("both endomorphisms must use the same declared basis")
    return trace(left.compose(right) - right.compose(left))


def trace_obstruction(dimension, canonical_scalar, *, scalar_type):
    """Apply the universal characteristic-zero trace proof, not a case search.

    Zero right-hand side does not establish a representation. A nonzero scalar
    excludes the exact finite relation AB-BA=lambda I, not finite quantum theory.
    """

    _dimension(dimension)
    scalar = _scalar(canonical_scalar, scalar_type)
    right_trace = scalar * dimension
    return {"dimension": dimension, "coefficient_field": scalar_type.__name__,
            "canonical_scalar": str(scalar), "commutator_trace": str(_scalar(0, scalar_type)),
            "identity_right_trace": str(right_trace),
            "exact_finite_relation_excluded": not right_trace.is_zero(),
            "a_representation_constructed": False}


def truncated_polynomial_pair(dimension, *, scalar_type):
    """Return derivative and projected multiplication in the stated monomial basis.

    This is a finite VECTOR SPACE of polynomials of degree below n. In
    characteristic zero its derivative is not a derivation of K[t]/(t^n).
    No adjoint, Hilbert norm, physical state or preferred physical basis follows.
    """

    _dimension(dimension)
    _scalar(0, scalar_type)
    basis = tuple("1" if i == 0 else f"t^{i}" for i in range(dimension))
    space = VectorSpace(f"{scalar_type.__name__} polynomial span degree < {dimension}",
                        basis, scalar_type)
    derivative = LinearMap(space, space, tuple(tuple(
        column if column == row + 1 else 0 for column in range(dimension))
        for row in range(dimension)))
    multiplication = LinearMap(space, space, tuple(tuple(
        int(row == column + 1) for column in range(dimension)) for row in range(dimension)))
    return derivative, multiplication


def prime_characteristic_pair(prime):
    """Return the same algebraic operators over F_p[t]/(t^p), not complex physics."""

    field = PrimeField(prime)
    derivative = FiniteMatrix(tuple(tuple(column if column == row + 1 else 0
        for column in range(prime)) for row in range(prime)), field)
    multiplication = FiniteMatrix(tuple(tuple(int(row == column + 1)
        for column in range(prime)) for row in range(prime)), field)
    return derivative, multiplication


def one_mode_car_pair(*, scalar_type):
    """An exact Clifford-algebra witness prevents a false no-go for all finite QM."""

    _scalar(0, scalar_type)
    space = VectorSpace("two-dimensional algebraic CAR witness", ("e0", "e1"), scalar_type)
    return (LinearMap(space, space, ((0, 1), (0, 0))),
            LinearMap(space, space, ((0, 0), (1, 0))))


def constraint_record():
    """Reproduce small arithmetic witnesses of universally proved constraints."""

    truncations = []
    for scalar_type in (Rational, Eisenstein):
        for dimension in (1, 2, 4):
            derivative, multiplication = truncated_polynomial_pair(
                dimension, scalar_type=scalar_type)
            commutator = derivative.compose(multiplication) - multiplication.compose(derivative)
            identity = LinearMap.identity(derivative.domain)
            defect = identity - commutator
            expected = LinearMap(derivative.domain, derivative.domain, tuple(tuple(
                dimension if row == column == dimension - 1 else 0
                for column in range(dimension)) for row in range(dimension)))
            if defect != expected or not commutator_trace(derivative, multiplication).is_zero():
                raise ValueError("the exact finite truncation boundary defect changed")
            truncations.append({"dimension": dimension, "field": scalar_type.__name__,
                "basis": list(derivative.domain.basis),
                "commutator_rows": [[str(c) for c in row] for row in commutator.rows],
                "identity_defect_rows": [[str(c) for c in row] for row in defect.rows],
                "nonzero_boundary_defect": True})
    exceptions = []
    for prime in (2, 3, 5):
        derivative, multiplication = prime_characteristic_pair(prime)
        commutator = derivative.matmul(multiplication) - multiplication.matmul(derivative)
        if commutator != FiniteMatrix.identity(prime, derivative.field):
            raise ValueError("the positive-characteristic counterexample changed")
        exceptions.append({"prime": prime, "dimension": prime,
            "monomial_basis": ["1" if i == 0 else f"t^{i}" for i in range(prime)],
            "commutator_rows": [list(row) for row in commutator.rows],
            "finite_field_p_times_one": derivative.field.element(prime),
            "characteristic_zero_p_times_one": str(Rational(prime)),
            "complex_hilbert_representation_asserted": False})
    car = []
    for scalar_type in (Rational, Eisenstein):
        first, second = one_mode_car_pair(scalar_type=scalar_type)
        if (not first.compose(first).is_zero() or not second.compose(second).is_zero()
            or first.compose(second) + second.compose(first) != LinearMap.identity(first.domain)):
            raise ValueError("the finite CAR counterexample to an overbroad no-go changed")
        car.append({"field": scalar_type.__name__, "basis": list(first.domain.basis),
                    "nilpotence_and_car_identity_exact": True})

    # Inspect a REAL declaration accepted by the existing symbolic API. This is
    # explicitly not an operator representation or a generated quantum state.
    declared = HilbertSpace("finite canonical-contract scope check", 2)
    relation = CanonicalRelation.bosonic(Operator("a-dagger", declared), Operator("a", declared))
    record = {"schema": "canonical-representation-constraints-v1",
        "proof_sha256": hashlib.sha256(PROOF.read_bytes()).hexdigest(),
        "quantum_contract_source_sha256": hashlib.sha256(QUANTUM.read_bytes()).hexdigest(),
        "theorem_scope": [
            "finite endomorphisms over a characteristic-zero commutative field",
            "AB-BA=lambda I with lambda nonzero cannot hold exactly",
            "no unital scalar-ring homomorphism from F_p into a characteristic-zero field"],
        "proof_is_universal_not_witness_enumeration": True,
        "finite_truncation_witnesses": truncations,
        "positive_characteristic_counterexamples": exceptions,
        "finite_car_counterexamples_to_all_finite_quantum_no_go": car,
        "actual_symbolic_contract": {"finite_dimension": declared.dimension,
            "accepted_bracket": relation.bracket.value,
            "accepted_right_hand_side": relation.right_hand_side,
            "matrix_representation_supplied": False},
        "all_finite_quantum_theories_excluded": False,
        "controlled_truncation_convergence_certified": False,
        "nonlinear_or_continuum_emergence_excluded": False,
        "quantum_postulates_derived": False, "causal_geometry_derived": False,
        "gravitational_coupling_derived": False, "dimensional_constants_derived": False,
        "genesis_to_uv_derivation_available": False, "physical_quantum_state_generated": False,
        "observations_used": False}
    record["artifact_digest"] = hashlib.sha256(json.dumps(record, sort_keys=True,
        separators=(",", ":")).encode()).hexdigest()
    return record


def write_constraints():
    """Install deterministic mathematical evidence, never partial physical output."""

    record = constraint_record()
    text = json.dumps(record, sort_keys=True, indent=2) + "\n"
    if OUTPUT.exists() and OUTPUT.read_text(encoding="utf-8") != text:
        raise ValueError("refusing to overwrite different representation evidence")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    temporary = OUTPUT.with_name(f".{OUTPUT.name}.tmp")
    try:
        temporary.write_text(text, encoding="utf-8")
        temporary.replace(OUTPUT)
    finally:
        temporary.unlink(missing_ok=True)
    return record


def read_constraints(*, expected_digest):
    """Bind the saved evidence to trusted execution and fresh proof/source bytes."""

    record = json.loads(OUTPUT.read_text(encoding="utf-8"))
    unsigned = dict(record)
    digest = unsigned.pop("artifact_digest", None)
    actual = hashlib.sha256(json.dumps(unsigned, sort_keys=True,
        separators=(",", ":")).encode()).hexdigest()
    if digest != expected_digest or digest != actual:
        raise ValueError("canonical representation evidence changed its trusted digest")
    if record != constraint_record():
        raise ValueError("canonical representation proof, source or exact scope changed")
    return record


if __name__ == "__main__":
    print(write_constraints()["artifact_digest"])
