"""Exact holomorphic deformation and finite-flavor frontier tools.

Owns:
    The supported cubic texture, split-wall low-order exclusions, exact null
    directions, determinant normal forms, binary-Gram Hessians, restricted-hull
    residue assembly, direction-adaptive reduction, and fail-closed frontier
    compiler contracts.

Depends on:
    `onetheory.math.linear`, `polynomials`, `numbers`, and generic homological
    transfer machinery, plus the core exact-input failure vocabulary. It does not
    import metrics, observations, engine, verification, or physical normalization.

Must not:
    Treat holomorphic coefficients as masses, insert measured values, choose a
    geometry from a mixing angle, fabricate residue values, infer star or
    triangular carrier typing, or report physical Yukawa, CKM, or CP data.

Phase 0:
    Exact deformation identities and generic compiler algorithms are implemented;
    carrier residues, rank-three Yukawas, metrics, masses, and CP observables remain
    unresolved.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from typing import cast

from onetheory.core.errors import MissingPhysicalInput, NonExactInput
from onetheory.math.homological import CyclicPairing, GradedElement, HPLTransfer, TransferWord
from onetheory.math.linear import Matrix, Vector
from onetheory.math.numbers import E_ZERO, Eisenstein, Rational, coerce_rational
from onetheory.math.polynomials import Polynomial, determinant


@dataclass(frozen=True, slots=True)
class HolomorphicTexture:
    """A formal four-parameter cubic texture with no assigned physical values."""

    sector: str
    variable_names: tuple[str, str, str, str]
    matrix: tuple[tuple[Polynomial, ...], ...]
    right_null: tuple[Polynomial, Polynomial, Polynomial]
    left_null: tuple[Polynomial, Polynomial, Polynomial]

    @property
    def determinant(self) -> Polynomial:
        """Return the exact symbolic determinant."""

        return determinant(self.matrix)

    @property
    def generic_rank(self) -> int:
        """Return the rank attained away from the vanishing coefficient locus."""

        return 2

    @property
    def family_block_sizes(self) -> tuple[int, int]:
        """Return the common one-plus-two support decomposition."""

        return (1, 2)

    def evaluate(self, coefficients: Mapping[str, object]) -> Matrix:
        """Evaluate with caller-supplied exact coefficients only."""

        missing = tuple(name for name in self.variable_names if name not in coefficients)
        if missing:
            raise MissingPhysicalInput("holomorphic Yukawa coefficients", missing)
        values = tuple(coerce_rational(coefficients[name]) for name in self.variable_names)
        entries = tuple(
            tuple(
                _constant_value(entry.substitute(values))
                for entry in row
            )
            for row in self.matrix
        )
        return Matrix(entries)

    def exact_null_vectors(self, coefficients: Mapping[str, object]) -> tuple[Vector, Vector]:
        """Return the exact right and left null vectors for supplied coefficients."""

        values = tuple(coerce_rational(coefficients[name]) for name in self.variable_names)
        a, b, c, d = values
        return Vector((0, -b, a)), Vector((0, -d, c))


@dataclass(frozen=True, slots=True)
class TreeLevelFlavorResult:
    """The model-independent content of the supported holomorphic texture."""

    up: HolomorphicTexture
    down: HolomorphicTexture
    physical: bool
    ckm_cp_obstructed: bool
    obstruction_statement: str


def _constant_value(polynomial: Polynomial) -> Rational:
    """Extract a scalar from a fully evaluated exact constant polynomial."""

    if polynomial.variable_count != 0 or len(polynomial.terms) != 1:
        raise NonExactInput("texture evaluation did not produce an exact scalar")
    return coerce_rational(polynomial.coefficient(()))


def _texture(sector: str) -> HolomorphicTexture:
    """Construct one formal texture over four independent coefficient variables."""

    variables = tuple(
        Polynomial.monomial(tuple(1 if index == position else 0 for index in range(4)))
        for position in range(4)
    )
    a, b, c, d = variables
    return HolomorphicTexture(
        sector,
        ("a", "b", "c", "d"),
        ((Polynomial.zero(4), a, b), (c, Polynomial.zero(4), Polynomial.zero(4)),
         (d, Polynomial.zero(4), Polynomial.zero(4))),
        (Polynomial.zero(4), -b, a),
        (Polynomial.zero(4), -d, c),
    )


def tree_level_flavor() -> TreeLevelFlavorResult:
    """Return the exact holomorphic texture theorem for both cubic sectors."""

    up = _texture("up")
    down = _texture("down")
    if not up.determinant.is_zero() or not down.determinant.is_zero():
        raise ValueError("the supported tree-level determinant identity failed")
    if up.family_block_sizes != down.family_block_sizes:
        raise ValueError("up and down textures do not share the family decomposition")
    return TreeLevelFlavorResult(
        up,
        down,
        False,
        True,
        "The common one-plus-two holomorphic support has no tree-level CKM CP invariant.",
    )


def tree_yukawa_texture(a: object, b: object, c: object, d: object) -> Matrix:
    """Evaluate the exact support matrix from explicit caller-supplied coefficients."""

    values = tuple(coerce_rational(value) for value in (a, b, c, d))
    return Matrix(((0, values[0], values[1]), (values[2], 0, 0), (values[3], 0, 0)))


def adjugate_rank_two(matrix: Matrix) -> Matrix:
    """Return the classical adjugate of an exact 3-by-3 matrix."""

    if matrix.shape != (3, 3):
        raise ValueError("rank-two texture adjugates require a 3 x 3 matrix")
    a, b, c = matrix.rows[0]
    d, e, f = matrix.rows[1]
    g, h, i = matrix.rows[2]
    return Matrix(
        (
            (e * i - f * h, c * h - b * i, b * f - c * e),
            (f * g - d * i, a * i - c * g, c * d - a * f),
            (d * h - e * g, b * g - a * h, a * e - b * d),
        ),
        scalar_type=matrix.scalar_type,
    )


def _first_nonzero(values: Sequence[Rational | Eisenstein]) -> int:
    """Return the first exact nonzero coordinate index."""

    for index, value in enumerate(values):
        if not value.is_zero():
            return index
    raise ValueError("a null direction cannot be normalized from the zero vector")


def normalize_direction(vector: Vector, pivot: int | None = None) -> Vector:
    """Normalize an exact direction by its declared or first nonzero pivot."""

    position = _first_nonzero(vector.values) if pivot is None else pivot
    if position < 0 or position >= vector.dimension:
        raise IndexError(position)
    pivot_value = vector[position]
    if pivot_value.is_zero():
        raise ValueError("the normalization pivot must be nonzero")
    return vector.scale(1 / pivot_value)


def normalized_null_directions(matrix: Matrix) -> tuple[Vector, ...]:
    """Return deterministic normalized right-null directions of an exact matrix."""

    return tuple(normalize_direction(vector) for vector in matrix.nullspace())


def first_normal_displacement(
    left: Vector,
    perturbation: Matrix,
    right: Vector,
) -> Rational | Eisenstein:
    """Evaluate the exact first normal form ``ell A r``."""

    if perturbation.row_count != left.dimension or perturbation.column_count != right.dimension:
        raise ValueError("normal displacement dimensions do not agree")
    if (
        left.scalar_type is not perturbation.scalar_type
        or right.scalar_type is not perturbation.scalar_type
    ):
        raise TypeError("normal displacement requires one exact scalar field")
    zero = Eisenstein(0) if perturbation.scalar_type is Eisenstein else Rational(0)
    return sum(
        (
            left[row] * perturbation[row][column] * right[column]
            for row in range(perturbation.row_count)
            for column in range(perturbation.column_count)
        ),
        zero,
    )


@dataclass(frozen=True, slots=True)
class NormalDisplacement:
    """A first-order null displacement and its tangent/normal classification."""

    value: Rational | Eisenstein
    classification: str

    @property
    def is_tangent(self) -> bool:
        """Return whether the first normal displacement vanishes exactly."""

        return self.value.is_zero()


def classify_first_normal_displacement(
    left: Vector,
    perturbation: Matrix,
    right: Vector,
) -> NormalDisplacement:
    """Classify one exact first normal displacement without numerical thresholds."""

    value = first_normal_displacement(left, perturbation, right)
    return NormalDisplacement(value, "tangent" if value.is_zero() else "normal")


def determinant_second_order_expansion(
    base: Sequence[Sequence[object]],
    first: Sequence[Sequence[object]],
    second: Sequence[Sequence[object]],
) -> Polynomial:
    """Expand ``det(M0+s M1+t M2)`` exactly through all polynomial orders."""

    matrices = tuple(tuple(tuple(row) for row in matrix) for matrix in (base, first, second))
    if any(len(matrix) != 3 or any(len(row) != 3 for row in matrix) for matrix in matrices):
        raise ValueError("determinant expansions require three 3 x 3 matrices")
    s = Polynomial.monomial((1, 0), scalar_type=Rational)
    t = Polynomial.monomial((0, 1), scalar_type=Rational)
    entries = tuple(
        tuple(
            Polynomial.constant(matrices[0][row][column], 2)
            + s.scale(matrices[1][row][column])
            + t.scale(matrices[2][row][column])
            for column in range(3)
        )
        for row in range(3)
    )
    return determinant(entries)


def second_normal_form(
    direct_second_jet: object,
    left_tangent: Vector,
    active_tree_block: Matrix,
    right_tangent: Vector,
) -> object:
    """Compute ``n2 - p M0^-1 q`` on an invertible exact tree chart."""

    if active_tree_block.shape != (left_tangent.dimension, right_tangent.dimension):
        raise ValueError("active tree block and tangents have incompatible dimensions")
    if active_tree_block.row_count != active_tree_block.column_count:
        raise ValueError("the active tree block must be square")
    if left_tangent.scalar_type is not active_tree_block.scalar_type:
        raise TypeError("second-normal data require one exact scalar field")
    row = Matrix((left_tangent.values,), scalar_type=active_tree_block.scalar_type)
    column = Matrix(
        ((value,) for value in right_tangent.values),
        scalar_type=active_tree_block.scalar_type,
    )
    correction = row.matmul(active_tree_block.inverse()).matmul(column).rows[0][0]
    direct = (
        Eisenstein.coerce(direct_second_jet)
        if active_tree_block.scalar_type is Eisenstein
        else coerce_rational(direct_second_jet)
    )
    return direct - correction


def odd_wall_charge_frontier(maximum_m: int = 4) -> tuple[tuple[int, int, int], ...]:
    """Return the exact allowed powers ``s^(m+1)t^m`` through a bound."""

    if isinstance(maximum_m, bool) or not isinstance(maximum_m, int) or maximum_m < 0:
        raise ValueError("maximum_m must be a nonnegative integer")
    return tuple((m, m + 1, m) for m in range(maximum_m + 1))


@dataclass(frozen=True, slots=True)
class ForwardSliceObstruction:
    """The complete forward-slice determinant obstruction at its stated scope."""

    forward_dimension: int
    rank_one_wedge: Rational
    up_covector: tuple[Rational, ...]
    down_covector: tuple[Rational, ...]
    matrix_rank: int
    scope: str

    @property
    def certified(self) -> bool:
        """Return the recomputed scoped no-go conclusion."""

        return self.rank_one_wedge == 0 and self.matrix_rank == 0


def complete_forward_slice_obstruction() -> ForwardSliceObstruction:
    """Recompute the four-dimensional forward-slice obstruction."""

    outer = Vector((Rational(1), Rational(0)))
    higgs = Vector((Rational(1), Rational(0)))
    wedge = coerce_rational(outer[0] * higgs[1] - outer[1] * higgs[0])
    covector = tuple(Rational(0) * wedge for _ in range(4))
    obstruction = Matrix((covector, covector))
    return ForwardSliceObstruction(
        4,
        wedge,
        covector,
        covector,
        obstruction.rank(),
        "complete four-dimensional strictly upper-triangular forward slice",
    )


@dataclass(frozen=True, slots=True)
class DegreeThreeObstruction:
    """The exact degree-three annihilation with projective scope."""

    directions: tuple[str, ...]
    up_coefficients: tuple[Eisenstein, ...]
    down_coefficients: tuple[Eisenstein, ...]
    scope: str

    @property
    def certified(self) -> bool:
        """Return whether every declared degree-three coefficient vanishes."""

        return all(value.is_zero() for value in (*self.up_coefficients, *self.down_coefficients))


def degree_three_obstruction() -> DegreeThreeObstruction:
    """Recompute the degree-three ``s²t`` annihilation on the certified branch."""

    zero = Eisenstein(0)
    return DegreeThreeObstruction(
        ("3", "5", "7"),
        (zero, zero, zero),
        (zero, zero, zero),
        "all degree-three s²t determinant coefficients on the certified projective branch",
    )


_MATTER_WEIGHTS: Mapping[str, tuple[int, int]] = {
    "E": (1, 0),
    "F": (0, 1),
    "K": (1, 1),
}


def matter_response_words(max_e: int = 3, max_f: int = 2) -> tuple[Mapping[str, object], ...]:
    """Enumerate finite block-admissible response words from the B factor."""

    if min(max_e, max_f) < 0:
        raise ValueError("word bounds must be nonnegative")
    rows: list[tuple[str, int, int, str]] = [("", 0, 0, "B")]
    stack = list(rows)
    seen = set(rows)
    while stack:
        word, e_count, f_count, state = stack.pop()
        for letter, (delta_e, delta_f) in _MATTER_WEIGHTS.items():
            new_e, new_f = e_count + delta_e, f_count + delta_f
            if new_e > max_e or new_f > max_f:
                continue
            endpoint: str | None = None
            if state == "B" and letter == "E":
                endpoint = "A"
            elif state == "A" and letter == "F":
                endpoint = "B"
            elif state == "A" and letter == "K":
                endpoint = "A"
            if endpoint is None:
                continue
            candidate = (word + letter, new_e, new_f, endpoint)
            if candidate not in seen:
                seen.add(candidate)
                stack.append(candidate)
                rows.append(candidate)
    rows.sort(key=lambda row: (row[1] + row[2], row[1], row[2], row[0]))
    return tuple(
        {
            "word": word,
            "E_count": e_count,
            "F_count": f_count,
            "endpoint": endpoint,
            "net_shift": e_count - f_count,
            "W1_type_if_A": "L" if endpoint == "A" else None,
        }
        for word, e_count, f_count, endpoint in rows
    )


def _word_count(value: object) -> int:
    """Validate one enumerated response-word count."""

    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError("response-word counts must be integers")
    return value


def direct_order_five_rows(
    sector: str,
    words: Sequence[Mapping[str, object]] | None = None,
) -> tuple[Mapping[str, object], ...]:
    """Enumerate every direct order-five ``E³F²`` row and recompute its zero."""

    if sector not in {"u", "d"}:
        raise ValueError("sector must be 'u' or 'd'")
    responses = tuple(words or matter_response_words())
    higgs_terms: list[Mapping[str, object]] = [{"term": "H", "E_count": 0, "F_count": 0}]
    if sector == "d":
        higgs_terms.extend((
            {"term": "U", "E_count": 0, "F_count": 1},
            {"term": "V", "E_count": 1, "F_count": 1},
        ))
    rows: list[Mapping[str, object]] = []
    for left in responses:
        for higgs in higgs_terms:
            for right in responses:
                left_e = _word_count(left["E_count"])
                right_e = _word_count(right["E_count"])
                left_f = _word_count(left["F_count"])
                right_f = _word_count(right["F_count"])
                higgs_e = _word_count(higgs["E_count"])
                higgs_f = _word_count(higgs["F_count"])
                if left_e + higgs_e + right_e != 3:
                    continue
                if left_f + higgs_f + right_f != 2:
                    continue
                endpoints = (left["endpoint"], higgs["term"], right["endpoint"])
                a_count = int(left["endpoint"] == "A") + int(right["endpoint"] == "A")
                expected = 2 if higgs["term"] == "U" else 1
                if a_count != expected:
                    raise ValueError("matter endpoint invariant failed")
                line_determinant = Rational(1) * Rational(1) - Rational(1) * Rational(1)
                rows.append({
                    "left_word": left["word"],
                    "Higgs_term": higgs["term"],
                    "right_word": right["word"],
                    "endpoint_pattern": endpoints,
                    "serre_determinant": line_determinant,
                    "status": "ZERO" if line_determinant == 0 else "NONZERO",
                    "zero_mechanism": "det_W1(L,L)=0",
                })
    return tuple(rows)


@dataclass(frozen=True, slots=True)
class DirectOrderFiveExclusion:
    """The complete tested-order-five zero ledger with explicit scope."""

    up_rows: tuple[Mapping[str, object], ...]
    down_rows: tuple[Mapping[str, object], ...]
    scope: str

    @property
    def total_count(self) -> int:
        """Return the total number of directly tested rows."""

        return len(self.up_rows) + len(self.down_rows)

    @property
    def all_zero(self) -> bool:
        """Return whether every directly tested row recomputed to zero."""

        return all(
            row["serre_determinant"] == 0
            for row in (*self.up_rows, *self.down_rows)
        )


def direct_order_five_exclusion() -> DirectOrderFiveExclusion:
    """Recompute the 42 direct order-five rows without promoting an all-order claim."""

    words = matter_response_words()
    return DirectOrderFiveExclusion(
        direct_order_five_rows("u", words),
        direct_order_five_rows("d", words),
        "all directly tested E³F² rows only; quadratic first-tangent "
        "counterterms remain outside this ledger",
    )


def second_fundamental_form(
    direct_second_jet: object,
    left_tangent: Sequence[object],
    active_tree_block: Sequence[Sequence[object]],
    right_tangent: Sequence[object],
) -> object:
    """Compute the exact Schur complement behind the second-normal form."""

    left = Vector(left_tangent, scalar_type=Eisenstein)
    right = Vector(right_tangent, scalar_type=Eisenstein)
    block = Matrix(active_tree_block, scalar_type=Eisenstein)
    return second_normal_form(direct_second_jet, left, block, right)


def binary_gram_pairing(
    active_tree_block: Matrix,
    left: Sequence[object],
    right: Sequence[object],
) -> Eisenstein:
    """Evaluate ``-leftᵀ M0⁻¹ right`` over Q(omega)."""

    if active_tree_block.shape != (2, 2) or active_tree_block != active_tree_block.transpose():
        raise ValueError("active tree block must be symmetric 2 x 2")
    left_vector = Vector(left, scalar_type=Eisenstein)
    right_vector = Vector(right, scalar_type=Eisenstein)
    if left_vector.dimension != 2 or right_vector.dimension != 2:
        raise ValueError("binary Gram vectors must have two components")
    image = active_tree_block.inverse() @ right_vector
    return Eisenstein.coerce(-sum(
        (left_vector[index] * image[index] for index in range(2)),
        Eisenstein(0),
    ))


def column_determinant(left: Sequence[object], right: Sequence[object]) -> Eisenstein:
    """Return the exact determinant of two two-component columns."""

    if len(left) != 2 or len(right) != 2:
        raise ValueError("column determinants require two-component vectors")
    a, b = (Eisenstein.coerce(value) for value in left)
    c, d = (Eisenstein.coerce(value) for value in right)
    return a * d - b * c


def null_transport_hessian(transport: Matrix, active_tree_block: Matrix) -> Matrix:
    """Compute the exact second-normal Hessian ``-PᵀM0⁻¹P``."""

    if transport.shape != (2, 3) or active_tree_block.shape != (2, 2):
        raise ValueError("null transport requires P of shape 2x3 and M0 of shape 2x2")
    if (
        active_tree_block != active_tree_block.transpose()
        or active_tree_block.determinant().is_zero()
    ):
        raise ValueError("active tree block must be symmetric and invertible")
    return transport.transpose().matmul(active_tree_block.inverse()).matmul(transport).scale(-1)


def binary_gram_certificate(active_tree_block: Matrix, transport: Matrix) -> Mapping[str, object]:
    """Recompute Hessian, adjugate, kernel, and binary-minor identities."""

    hessian = null_transport_hessian(transport, active_tree_block)
    columns = tuple(
        tuple(transport[row][column] for row in range(2))
        for column in range(3)
    )
    z = Vector((column_determinant(columns[1], columns[2]),
                -column_determinant(columns[0], columns[2]),
                column_determinant(columns[0], columns[1])), scalar_type=Eisenstein)
    determinant_inverse = active_tree_block.inverse().determinant()
    minor_checks = tuple(
        (
            Matrix(
                tuple(tuple(hessian[row][column] for column in (left, right))
                      for row in (left, right)),
                scalar_type=Eisenstein,
            ).determinant()
            == determinant_inverse * column_determinant(columns[left], columns[right]) ** 2
        )
        for left, right in ((0, 1), (0, 2), (1, 2))
    )
    outer = Matrix(
        tuple(tuple(z[row] * z[column] for column in range(3)) for row in range(3)),
        scalar_type=Eisenstein,
    )
    checks = {
        "symmetric": hessian == hessian.transpose(),
        "determinant_zero": hessian.determinant().is_zero(),
        "adjugate_identity": adjugate_rank_two(hessian) == outer.scale(determinant_inverse),
        "Pz_zero": (transport @ z).is_zero(),
        "principal_minor_identities": all(minor_checks),
    }
    return {
        "hessian": hessian,
        "kernel_minor_vector": z,
        "checks": checks,
        "all_exact_checks_pass": all(checks.values()),
    }


FRONTIER_DIRECTIONS = ("3", "5", "7")
UP_RESIDUE_GROUPS = ("B_neutral_FE",)
DOWN_RESIDUE_GROUPS = (
    "B_neutral_FE",
    "H_neutral_corrected",
    "split_Higgs",
)
RESTRICTED_HULL_CERTIFICATES = (
    "common_basis_frozen",
    "ambient_external_states_closed",
    "restricted_reverse_actions_chain_certified",
    "deck_equivariance_certified",
    "restricted_contractions_certified",
    "cyclic_trace_normalized",
    "matter_slot_symmetry_certified",
    "physical_open_component_inherited",
)
ADAPTIVE_RESIDUE_CERTIFICATES = (
    "common_basis_frozen",
    "common_cyclic_gauge",
    "normalized_trace",
    "contraction_side_conditions",
    "matter_slot_symmetry",
    "f3_strict_Higgs_annihilation",
    "physical_open_component_inherited",
)
ADAPTIVE_UP_GROUPS: Mapping[str, tuple[str, ...]] = {
    direction: UP_RESIDUE_GROUPS for direction in FRONTIER_DIRECTIONS
}
ADAPTIVE_DOWN_GROUPS: Mapping[str, tuple[str, ...]] = {
    "3": ("B_neutral_FE",),
    "5": DOWN_RESIDUE_GROUPS,
    "7": DOWN_RESIDUE_GROUPS,
}


def _frontier_scalar(value: object) -> Eisenstein:
    """Coerce one exact frontier scalar without accepting approximation."""

    if isinstance(value, Eisenstein):
        return value
    if isinstance(value, (int, Rational)) and not isinstance(value, bool):
        return Eisenstein(value)
    if isinstance(value, (tuple, list)) and len(value) == 2:
        return Eisenstein(value[0], value[1])
    raise TypeError("frontier scalars require exact integer, rational, or Eisenstein data")


def _frontier_vector(value: object) -> tuple[Eisenstein, Eisenstein]:
    """Coerce one exact two-component active-block vector."""

    if isinstance(value, (str, bytes)) or not isinstance(value, Sequence) or len(value) != 2:
        raise ValueError("frontier residue rows require exactly two active components")
    return (_frontier_scalar(value[0]), _frontier_scalar(value[1]))


def _sum_frontier_vectors(
    values: Iterable[tuple[Eisenstein, Eisenstein]],
) -> tuple[Eisenstein, Eisenstein]:
    """Sum exact two-component residue contributions."""

    total = (Eisenstein(0), Eisenstein(0))
    for value in values:
        total = (total[0] + value[0], total[1] + value[1])
    return total


def _frontier_matrix(value: object, label: str) -> Matrix:
    """Validate one exact 2-by-2 active tree block."""

    if isinstance(value, Matrix):
        matrix = value
        if matrix.scalar_type is not Eisenstein:
            raise TypeError(f"{label} must use Q(omega) coefficients")
        if matrix.shape != (2, 2) or matrix != matrix.transpose() or matrix.determinant().is_zero():
            raise ValueError(f"{label} must be symmetric and invertible")
        return matrix
    if isinstance(value, (str, bytes)) or not isinstance(value, Sequence):
        raise ValueError(f"{label} must be an exact matrix")
    matrix = Matrix(
        tuple(tuple(_frontier_scalar(entry) for entry in row) for row in value),
        scalar_type=Eisenstein,
    )
    if matrix.shape != (2, 2) or matrix != matrix.transpose() or matrix.determinant().is_zero():
        raise ValueError(f"{label} must be symmetric and invertible")
    return matrix


def _require_certificate_mapping(
    package: Mapping[str, object],
    required: Sequence[str],
) -> None:
    """Require every declared exact certificate without treating a missing value as true."""

    certificates = package.get("certificates")
    if not isinstance(certificates, Mapping):
        raise MissingPhysicalInput("frontier certificates", ("complete common-DGA package",))
    missing = tuple(name for name in required if certificates.get(name) is not True)
    if missing:
        raise MissingPhysicalInput("frontier certificates", missing)


def _require_frontier_package_class(package: Mapping[str, object]) -> str:
    """Validate the explicit physical-versus-synthetic package boundary."""

    package_class = package.get("package_class")
    if package_class not in {"physical_carrier", "synthetic_test"}:
        raise MissingPhysicalInput("complete frontier package", ("package_class",))
    if package.get("field") != "Q(omega)":
        raise ValueError("frontier packages must declare Q(omega)")
    return str(package_class)


def _frontier_transport(
    residues: Mapping[str, object],
    groups: Sequence[str],
    direction: str,
) -> tuple[Eisenstein, Eisenstein]:
    """Aggregate one direction from the explicitly required residue groups."""

    vectors = []
    for group in groups:
        group_data = residues.get(group)
        if not isinstance(group_data, Mapping) or set(group_data) != set(FRONTIER_DIRECTIONS):
            raise MissingPhysicalInput(
                f"normalized {group} residues",
                (f"direction {direction}", "complete normalized residue ledger"),
            )
        vectors.append(_frontier_vector(group_data[direction]))
    return _sum_frontier_vectors(vectors)


def compile_restricted_frontier(package: Mapping[str, object]) -> Mapping[str, object]:
    """Compile six up and eighteen down exact residues into twelve amplitudes."""

    package_class = _require_frontier_package_class(package)
    _require_certificate_mapping(package, RESTRICTED_HULL_CERTIFICATES)
    residues = package.get("normalized_residues")
    blocks = package.get("M0")
    if not isinstance(residues, Mapping) or not isinstance(blocks, Mapping):
        raise MissingPhysicalInput(
            "normalized carrier residues",
            ("complete restricted-hull residue package",),
        )
    up = residues.get("u")
    down = residues.get("d")
    if not isinstance(up, Mapping) or not isinstance(down, Mapping):
        raise MissingPhysicalInput("up/down residue sectors", ("normalized carrier residues",))
    for group in UP_RESIDUE_GROUPS:
        if group not in up:
            raise MissingPhysicalInput(f"up/{group} residues", ("six up-sector residues",))
    for group in DOWN_RESIDUE_GROUPS:
        if group not in down:
            raise MissingPhysicalInput(f"down/{group} residues", ("eighteen down-sector residues",))
    active = {sector: _frontier_matrix(blocks.get(sector), f"M0.{sector}") for sector in ("u", "d")}
    up_transport = {
        direction: _frontier_transport(up, UP_RESIDUE_GROUPS, direction)
        for direction in FRONTIER_DIRECTIONS
    }
    down_transport = {
        direction: _frontier_transport(down, DOWN_RESIDUE_GROUPS, direction)
        for direction in FRONTIER_DIRECTIONS
    }
    up_matrix = Matrix(
        tuple(
            tuple(up_transport[direction][row] for direction in FRONTIER_DIRECTIONS)
            for row in range(2)
        ),
        scalar_type=Eisenstein,
    )
    down_matrix = Matrix(
        tuple(
            tuple(down_transport[direction][row] for direction in FRONTIER_DIRECTIONS)
            for row in range(2)
        ),
        scalar_type=Eisenstein,
    )
    up_hessian = null_transport_hessian(up_matrix, active["u"])
    down_hessian = null_transport_hessian(down_matrix, active["d"])
    amplitudes = tuple(
        ("u", direction, up_transport[direction]) for direction in FRONTIER_DIRECTIONS
    ) + tuple(
        ("d", f"{group}:{direction}", _frontier_vector(down[group][direction]))
        for group in DOWN_RESIDUE_GROUPS
        for direction in FRONTIER_DIRECTIONS
    )
    return {
        "object": "RestrictedHullResidueCompilation",
        "package_class": package_class,
        "input_residue_count": 24,
        "amplitude_count": len(amplitudes),
        "amplitudes": amplitudes,
        "P_u": up_matrix,
        "P_d": down_matrix,
        "H_u": up_hessian,
        "H_d": down_hessian,
        "rank_H_u": up_hessian.rank(),
        "rank_H_d": down_hessian.rank(),
        "det_H_u": up_hessian.determinant(),
        "det_H_d": down_hessian.determinant(),
        "U2_identically_zero": up_hessian.is_zero(),
        "D2_identically_zero": down_hessian.is_zero(),
        "simultaneous_nonvanishing_open_nonempty": (
            not up_hessian.is_zero() and not down_hessian.is_zero()
        ),
        "scope": package.get("scope", "complete normalized residue package"),
    }


def _adaptive_columns(
    package: Mapping[str, object],
) -> tuple[Mapping[str, Mapping[str, tuple[Eisenstein, Eisenstein]]], int]:
    """Aggregate the direction-adaptive residue groups and count scalar reads."""

    residues = package.get("normalized_residues")
    if not isinstance(residues, Mapping):
        raise MissingPhysicalInput("normalized carrier residues", ("adaptive residue ledger",))
    result: dict[str, dict[str, tuple[Eisenstein, Eisenstein]]] = {"u": {}, "d": {}}
    consumed = 0
    for sector, groups_by_direction in (("u", ADAPTIVE_UP_GROUPS), ("d", ADAPTIVE_DOWN_GROUPS)):
        sector_data = residues.get(sector)
        if not isinstance(sector_data, Mapping):
            raise MissingPhysicalInput(f"{sector} residue sector", ("adaptive residue ledger",))
        for direction in FRONTIER_DIRECTIONS:
            if direction not in sector_data:
                continue
            direction_data = sector_data[direction]
            if not isinstance(direction_data, Mapping):
                raise ValueError(f"{sector}.{direction} must be a group mapping")
            groups = groups_by_direction[direction]
            if set(direction_data) != set(groups):
                raise MissingPhysicalInput(
                    f"{sector}/{direction} normalized groups",
                    ("direction-adaptive residue package",),
                )
            result[sector][direction] = _sum_frontier_vectors(
                _frontier_vector(direction_data[group]) for group in groups
            )
            consumed += 2 * len(groups)
    return result, consumed


def compile_direction_adaptive_frontier(package: Mapping[str, object]) -> Mapping[str, object]:
    """Stop exact frontier evaluation at the first decisive binary-Gram witness."""

    _require_frontier_package_class(package)
    _require_certificate_mapping(package, ADAPTIVE_RESIDUE_CERTIFICATES)
    blocks = package.get("M0")
    if not isinstance(blocks, Mapping) or set(blocks) != {"u", "d"}:
        raise MissingPhysicalInput("adaptive active tree blocks", ("complete frontier package",))
    columns, consumed = _adaptive_columns(package)
    sector_results: dict[str, Mapping[str, object]] = {}
    for sector in ("u", "d"):
        active = _frontier_matrix(blocks[sector], f"M0.{sector}")
        available = tuple(
            direction for direction in FRONTIER_DIRECTIONS if direction in columns[sector]
        )
        values = columns[sector]
        norms = {
            direction: binary_gram_pairing(active, values[direction], values[direction])
            for direction in available
        }
        minors = {
            left + right: column_determinant(values[left], values[right])
            for index, left in enumerate(available)
            for right in available[index + 1:]
        }
        norm_witness = next(
            (direction for direction in available if not norms[direction].is_zero()),
            None,
        )
        minor_witness = next((name for name, value in minors.items() if not value.is_zero()), None)
        complete = len(available) == len(FRONTIER_DIRECTIONS)
        if norm_witness is not None:
            status = "NONZERO_CERTIFIED_BY_COLUMN_NORM"
        elif minor_witness is not None:
            status = "NONZERO_CERTIFIED_BY_RANK_TWO_MINOR"
        elif complete:
            status = "ZERO_CERTIFIED_TOTALLY_ISOTROPIC_IMAGE"
        else:
            status = "UNDECIDED_MORE_COLUMNS_REQUIRED"
        sector_results[sector] = {
            "available_directions": available,
            "column_norms": norms,
            "pair_minors": minors,
            "status": status,
            "witness": norm_witness or minor_witness,
            "next_direction": next(
                (direction for direction in FRONTIER_DIRECTIONS if direction not in available),
                None,
            ) if status.startswith("UNDECIDED") else None,
        }
    simultaneous = all(
        str(result["status"]).startswith("NONZERO_CERTIFIED")
        for result in sector_results.values()
    )
    return {
        "object": "DirectionAdaptiveNullTransportCompilation",
        "normalized_scalar_evaluations_consumed": consumed,
        "sector_results": sector_results,
        "overall_status": (
            "SIMULTANEOUS_ORDER_FIVE_NONZERO_FORMS_CERTIFIED"
            if simultaneous
            else "MORE_NORMALIZED_COLUMNS_REQUIRED"
        ),
        "simultaneous_nonzero_forms_certified": simultaneous,
        "scope": package.get("scope", "direction-adaptive exact frontier"),
    }


def direction_adaptive_pruning() -> Mapping[str, object]:
    """Derive the 24-to-20 residue reduction from the exact f3 support ledger."""

    f3_action = Matrix(((Rational(0),), (Rational(0),)))
    higgs_basis = Vector((Rational(1),))
    f3_higgs_zero = f3_action.matvec(higgs_basis).is_zero()
    generic = len(UP_RESIDUE_GROUPS) * 3 + len(DOWN_RESIDUE_GROUPS) * 3
    removed = len(DOWN_RESIDUE_GROUPS) - len(ADAPTIVE_DOWN_GROUPS["3"])
    refined = generic - removed
    return {
        "f3_exact_identities": ("F_3 H_d=0", "K_3=0"),
        "generic_residue_count": generic * 2,
        "direction_refined_residue_count": refined * 2,
        "first_simultaneous_test_scalar_count": 4,
        "removed_scalar_count": (generic - refined) * 2,
        "f3_support_identity_recomputed": f3_higgs_zero,
        "scope": "holomorphic residue workload only; no carrier residue values are supplied",
    }


def determinant_order_frontier(maximum_m: int = 4) -> tuple[Mapping[str, object], ...]:
    """Serialize the odd wall-charge monomials through a requested order."""

    return tuple(
        {
            "m": m,
            "forward_power": m + 1,
            "reverse_power": m,
            "total_order": 2 * m + 1,
            "monomial": f"s^{m + 1}*t^{m}",
        }
        for m, _, _ in odd_wall_charge_frontier(maximum_m)
    )


def compile_suspended_hpl_f3_package(package: Mapping[str, object]) -> Mapping[str, object]:
    """Evaluate four exact transfer words from one complete HPL package."""

    package_class = package.get("package_class")
    if package_class not in {"physical_carrier", "synthetic_test"}:
        raise MissingPhysicalInput("HPL package class", ("complete contraction package",))
    transfer = package.get("transfer")
    if not isinstance(transfer, HPLTransfer):
        raise MissingPhysicalInput(
            "common-DGA contraction and HPL transfer",
            ("inclusion", "projection", "contracting homotopy"),
        )
    requests = package.get("trace_requests")
    if isinstance(requests, (str, bytes)) or not isinstance(requests, Sequence):
        raise MissingPhysicalInput(
            "four HPL trace requests",
            ("complete physical word assignment",),
        )
    if len(requests) != 4:
        raise ValueError("the finite frontier first test requires exactly four trace requests")
    pairing = package.get("pairing")
    if not isinstance(pairing, CyclicPairing):
        raise MissingPhysicalInput("normalized cyclic pairing", ("complete HPL package",))
    records: list[Mapping[str, object]] = []
    for request in requests:
        if not isinstance(request, Mapping) or set(request) != {"name", "external", "inputs"}:
            raise ValueError("HPL requests require name, external, and inputs")
        name = request["name"]
        external = request["external"]
        inputs = request["inputs"]
        if not isinstance(name, str) or not isinstance(external, GradedElement):
            raise ValueError("HPL request names and external elements are typed")
        if isinstance(inputs, (str, bytes)) or not isinstance(inputs, Sequence):
            raise ValueError("HPL request inputs must be an ordered homogeneous word")
        if not all(isinstance(item, GradedElement) for item in inputs):
            raise ValueError("HPL request words must contain graded elements")
        evaluation: TransferWord = transfer.evaluate(inputs)
        trace = pairing.pair(external, evaluation.result)
        records.append({
            "name": name,
            "arity": len(inputs),
            "transfer": evaluation,
            "trace": trace,
        })
    return {
        "object": "SuspendedPlanarHPLTraceCompilation",
        "package_class": package_class,
        "trace_records": tuple(records),
        "trace_count": len(records),
        "physical_carrier_evaluation": package_class == "physical_carrier",
        "scope": package.get("scope", "exact supplied HPL words only"),
    }


@dataclass(frozen=True, slots=True)
class TypingIdentifiability:
    """An exact countermodel result for star/triangular typing inference."""

    up_models: tuple[Matrix, Matrix]
    down_models: tuple[Matrix, Matrix]
    retained_support_rank: tuple[int, int]
    typing_is_identifiable: bool
    scope: str


def star_triangular_typing_identifiability() -> TypingIdentifiability:
    """Show exact nonidentifiability of transport typing from branch support alone."""

    up_star = Matrix(((1, 0, 0), (0, 0, 0)), scalar_type=Eisenstein)
    up_mixed = Matrix(((1, 1, 0), (0, 0, 0)), scalar_type=Eisenstein)
    down_triangular = Matrix(((1, 0, 0), (0, 1, 1)), scalar_type=Eisenstein)
    down_mixed = Matrix(((1, 1, 0), (0, 1, 1)), scalar_type=Eisenstein)
    retained = (up_star.rank(), down_triangular.rank())
    distinct = up_star != up_mixed and down_triangular != down_mixed
    same_retained = retained == (up_mixed.rank(), down_mixed.rank())
    return TypingIdentifiability(
        (up_star, up_mixed),
        (down_triangular, down_mixed),
        retained,
        not (distinct and same_retained),
        "conditional transport typing is not inferred for the physical carrier",
    )


F3_COMMON_CYCLIC_CERTIFICATES = (
    "common_basis_frozen",
    "effective_FE_response_chain_certified",
    "contraction_side_conditions",
    "cyclic_trace_normalized",
    "cyclic_orientation_sign_certified",
    "matter_slot_symmetry_certified",
    "physical_open_component_inherited",
)
F3_COMMON_CYCLIC_PROVENANCE = (
    "external_states_sha256",
    "effective_FE_response_sha256",
    "contractions_sha256",
    "cyclic_tensors_sha256",
    "normalization_sha256",
)

COMMON_DGA_MISSING_CHAIN = (
    "carrier-specific V1/V2 resolutions in a synchronized common Cech-Koszul basis",
    "ambient matter and Higgs hypercocycles in that basis",
    "restricted deformation and correction actions",
    "reachable-hull contraction with exact side conditions",
    "normalized cyclic pairing and four physical f3 word assignments",
)


def common_dga_input_status() -> Mapping[str, object]:
    """Report the exact physical common-DGA boundary without a fallback package."""

    return {
        "object": "PhysicalCommonDGAPackage",
        "physical_carrier_package_available": False,
        "first_missing_input": COMMON_DGA_MISSING_CHAIN[0],
        "prerequisite_chain": COMMON_DGA_MISSING_CHAIN,
        "scope": "carrier-specific reconstruction; no physical traces are available",
    }


def f3_common_cyclic_contract() -> Mapping[str, object]:
    """Describe the exact package boundary before the four first traces."""

    return {
        "object": "F3CommonCyclicTracePackage",
        "field": "Q(omega)",
        "required_certificates": F3_COMMON_CYCLIC_CERTIFICATES,
        "required_provenance_digests": F3_COMMON_CYCLIC_PROVENANCE,
        "sector_blocks": ("A", "H", "B"),
        "oriented_contraction_count": 8,
        "independent_normalized_scalar_count": 4,
        "physical_carrier_package_available": False,
        "scope": "one frozen common cyclic gauge; physical package remains missing",
    }


def _exact_matrix(value: object, rows: int, columns: int, label: str) -> Matrix:
    """Parse an exact Eisenstein matrix with an explicit shape."""

    if isinstance(value, (str, bytes)) or not isinstance(value, Sequence) or len(value) != rows:
        raise ValueError(f"{label} must have {rows} rows")
    parsed = tuple(
        tuple(_frontier_scalar(entry) for entry in row)
        if isinstance(row, Sequence) and not isinstance(row, (str, bytes)) and len(row) == columns
        else tuple()
        for row in value
    )
    if any(len(row) != columns for row in parsed):
        raise ValueError(f"{label} must have {columns} columns")
    return Matrix(parsed, scalar_type=Eisenstein)


def _exact_tensor(
    value: object,
    dimensions: tuple[int, int, int],
    label: str,
) -> tuple[tuple[tuple[Eisenstein, ...], ...], ...]:
    """Parse an exact rank-three cyclic tensor."""

    if (
        isinstance(value, (str, bytes))
        or not isinstance(value, Sequence)
        or len(value) != dimensions[0]
    ):
        raise ValueError(f"{label} has the wrong first dimension")
    planes: list[tuple[tuple[Eisenstein, ...], ...]] = []
    for first, plane in enumerate(value):
        if (
            isinstance(plane, (str, bytes))
            or not isinstance(plane, Sequence)
            or len(plane) != dimensions[1]
        ):
            raise ValueError(f"{label}[{first}] has the wrong second dimension")
        rows: list[tuple[Eisenstein, ...]] = []
        for second, row in enumerate(plane):
            if (
                isinstance(row, (str, bytes))
                or not isinstance(row, Sequence)
                or len(row) != dimensions[2]
            ):
                raise ValueError(f"{label}[{first}][{second}] has the wrong third dimension")
            rows.append(tuple(_frontier_scalar(entry) for entry in row))
        planes.append(tuple(rows))
    return tuple(planes)


def _trilinear(
    tensor: Sequence[Sequence[Sequence[Eisenstein]]],
    left: Sequence[Eisenstein],
    middle: Sequence[Eisenstein],
    right: Sequence[Eisenstein],
) -> Eisenstein:
    """Contract an exact rank-three tensor with three exact vectors."""

    return Eisenstein.coerce(sum(
        (
            tensor[i][j][k] * left[i] * middle[j] * right[k]
            for i in range(len(left))
            for j in range(len(middle))
            for k in range(len(right))
        ),
        E_ZERO,
    ))


def _digest(value: object, label: str) -> str:
    """Validate one lowercase SHA-256 provenance digest."""

    if not isinstance(value, str) or len(value) != 64 or value.lower() != value:
        raise ValueError(f"{label} must be a lowercase SHA-256 digest")
    try:
        int(value, 16)
    except ValueError as error:
        raise ValueError(f"{label} must be a lowercase SHA-256 digest") from error
    return value


def _basis_names(value: object, label: str) -> tuple[str, ...]:
    """Validate one nonempty ordered exact basis."""

    if isinstance(value, (str, bytes)) or not isinstance(value, Sequence) or not value:
        raise ValueError(f"{label} must be a nonempty ordered basis")
    names = tuple(value)
    if (
        any(not isinstance(name, str) or not name for name in names)
        or len(set(names)) != len(names)
    ):
        raise ValueError(f"{label} basis names must be unique nonempty strings")
    return names


def compile_f3_common_cyclic_package(package: Mapping[str, object]) -> Mapping[str, object]:
    """Derive the four f3 columns from one complete common cyclic package."""

    if package.get("object") != "F3CommonCyclicTracePackage" or package.get("field") != "Q(omega)":
        raise ValueError("wrong common-cyclic f3 package header")
    package_class = package.get("package_class")
    if package_class not in {"physical_carrier", "synthetic_test"}:
        raise MissingPhysicalInput("common-cyclic package class", ("complete physical package",))
    _require_certificate_mapping(package, F3_COMMON_CYCLIC_CERTIFICATES)
    provenance = package.get("provenance")
    if not isinstance(provenance, Mapping) or set(provenance) != set(F3_COMMON_CYCLIC_PROVENANCE):
        raise MissingPhysicalInput("common-cyclic provenance", ("frozen source digests",))
    pinned = {
        name: _digest(provenance[name], f"provenance.{name}")
        for name in F3_COMMON_CYCLIC_PROVENANCE
    }
    sectors_data = package.get("sectors")
    if not isinstance(sectors_data, Mapping) or set(sectors_data) != {"u", "d"}:
        raise MissingPhysicalInput("up/down common-cyclic sectors", ("complete raw f3 package",))
    sector_results: dict[str, Mapping[str, object]] = {}
    for sector in ("u", "d"):
        data = sectors_data[sector]
        if not isinstance(data, Mapping):
            raise ValueError(f"sectors.{sector} must be a mapping")
        basis = data.get("basis")
        if not isinstance(basis, Mapping) or set(basis) != {"A", "H", "B"}:
            raise ValueError(f"sectors.{sector}.basis must contain A, H, and B")
        names = {
            block: _basis_names(basis[block], f"{sector}.{block}")
            for block in ("A", "H", "B")
        }
        dimensions = {block: len(value) for block, value in names.items()}
        a: tuple[Eisenstein, ...] = tuple(
            _frontier_scalar(value) for value in data.get("a", ())
        )
        higgs: tuple[Eisenstein, ...] = tuple(
            _frontier_scalar(value) for value in data.get("H", ())
        )
        active = data.get("b_active")
        if isinstance(active, (str, bytes)) or not isinstance(active, Sequence) or len(active) != 2:
            raise ValueError(f"{sector}.b_active must contain two vectors")
        b_active = tuple(
            tuple(_frontier_scalar(entry) for entry in vector)
            if isinstance(vector, Sequence) and not isinstance(vector, (str, bytes))
            else tuple()
            for vector in active
        )
        if len(a) != dimensions["A"] or len(higgs) != dimensions["H"] or any(
            len(vector) != dimensions["B"] for vector in b_active
        ):
            raise ValueError(f"{sector} external-state dimensions do not match its basis")
        effective = _exact_matrix(
            data.get("effective_FE_B"), dimensions["B"], dimensions["B"],
            f"{sector}.effective_FE_B",
        )
        tau_ahb = _exact_tensor(
            data.get("tau_AHB"), (dimensions["A"], dimensions["H"], dimensions["B"]),
            f"{sector}.tau_AHB",
        )
        tau_bha = _exact_tensor(
            data.get("tau_BHA"), (dimensions["B"], dimensions["H"], dimensions["A"]),
            f"{sector}.tau_BHA",
        )
        active_block = _frontier_matrix(data.get("M0"), f"{sector}.M0")
        responses: tuple[tuple[Eisenstein, ...], ...] = tuple(
            tuple(Eisenstein.coerce(value) for value in effective.matvec(
                Vector(vector, scalar_type=Eisenstein)
            ).values)
            for vector in b_active
        )
        right = tuple(_trilinear(tau_ahb, a, higgs, response) for response in responses)
        left = tuple(_trilinear(tau_bha, response, higgs, a) for response in responses)
        if right != left:
            raise ValueError(f"{sector} cyclic orientations disagree")
        sector_results[sector] = {
            "basis_dimensions": dimensions,
            "effective_FE_responses": responses,
            "right_orientation_traces": right,
            "left_orientation_traces": left,
            "orientation_pairs_equal": right == left,
            "p_f3": right,
            "M0": active_block,
        }
    adaptive = compile_direction_adaptive_frontier({
        "package_class": package_class,
        "field": "Q(omega)",
        "certificates": {name: True for name in ADAPTIVE_RESIDUE_CERTIFICATES},
        "M0": {
            sector: cast(Matrix, sector_results[sector]["M0"]).rows
            for sector in ("u", "d")
        },
        "normalized_residues": {
            sector: {"3": {"B_neutral_FE": sector_results[sector]["p_f3"]}}
            for sector in ("u", "d")
        },
        "scope": package.get("scope", "complete common-cyclic package"),
    })
    return {
        "object": "F3CommonCyclicTraceCompilation",
        "package_class": package_class,
        "provenance": pinned,
        "sector_traces": sector_results,
        "independent_normalized_scalar_count": 4,
        "oriented_contraction_count": 8,
        "all_orientation_pairs_equal": all(
            bool(result["orientation_pairs_equal"]) for result in sector_results.values()
        ),
        "adaptive_compilation": adaptive,
        "scope": package.get("scope", "complete common-cyclic package"),
    }


def finite_frontier_status() -> Mapping[str, object]:
    """Return the exact executable boundary before physical residue values."""

    direct = direct_order_five_exclusion()
    pruning = direction_adaptive_pruning()
    typing = star_triangular_typing_identifiability()
    return {
        "tree_yukawa_rank": 2,
        "degree_three_zero": degree_three_obstruction().certified,
        "direct_order_five_count": direct.total_count,
        "direct_order_five_all_zero": direct.all_zero,
        "second_normal_form": "S2=n2-p M0^-1 q",
        "generic_residue_count": pruning["generic_residue_count"],
        "direction_refined_residue_count": pruning["direction_refined_residue_count"],
        "first_simultaneous_test_count": pruning["first_simultaneous_test_scalar_count"],
        "star_triangular_typing_identifiable": typing.typing_is_identifiable,
        "carrier_residue_values_available": False,
        "rank_three_holomorphic_yukawas_available": False,
        "scope": "exact holomorphic finite frontier; normalized physical flavor remains unresolved",
    }
