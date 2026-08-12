"""Audit every declared Tier B outer automorphism action.

Owns:
    Strict reconstruction of frozen invariant cover cocycles, exact constituent
    endomorphism certificates, and pair-level scalar orbit certificates.

Depends on:
    Content-addressed invariant pair records and exact sparse Schoen composition.

Must not:
    Infer actions from dimensions, identify unrelated presentations, select an
    extension point, or construct a rank-four bundle.

Phase 0:
    Research-only pair and constituent action audits are executable; exhaustive
    generation and rank-four construction remain separate gates.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from onetheory.math.homological import VectorSpace
from onetheory.math.numbers import Eisenstein, Rational

from .schoen_sparse_outer import SparseMap, _freeze_rows, sparse_outer_hom
from .schoen_sparse_outer_actions import (
    _basis_coordinate_record,
    _total_basis_coordinates,
)
from .schoen_sparse_outer_automorphisms import (
    SparseEndomorphismAlgebraAudit,
    _polynomial_record,
    sparse_constituent_endomorphism_algebra,
    sparse_outer_cover_scalar_action,
)
from .tier_b_schoen_outer_full import _clear_worker_caches
from .tier_b_schoen_outer_invariants import InvariantPairTask


def _rational_text(text: str) -> Rational:
    """Parse one canonical integer or fraction without evaluating text."""

    try:
        value = Fraction(text)
    except (ValueError, ZeroDivisionError) as error:
        raise ValueError("invalid exact rational artifact coefficient") from error
    return Rational(value)


def _eisenstein_text(text: object) -> Eisenstein:
    """Parse the canonical ``a+b*omega`` format emitted by exact scalars."""

    if not isinstance(text, str) or not text:
        raise ValueError("Eisenstein artifact coefficients must be nonempty text")
    if "omega" not in text:
        return Eisenstein(_rational_text(text))
    suffix = "*omega" if text.endswith("*omega") else "omega"
    if not text.endswith(suffix) or text.count("omega") != 1:
        raise ValueError("invalid Eisenstein artifact coefficient")
    prefix = text[: -len(suffix)]
    separator = max(prefix.rfind("+", 1), prefix.rfind("-", 1))
    if separator < 0:
        omega_text = prefix
        if omega_text in ("", "+"):
            omega_text = "1"
        elif omega_text == "-":
            omega_text = "-1"
        return Eisenstein(0, _rational_text(omega_text))
    rational_text = prefix[:separator]
    omega_text = prefix[separator:]
    if omega_text == "+":
        omega_text = "1"
    elif omega_text == "-":
        omega_text = "-1"
    return Eisenstein(_rational_text(rational_text), _rational_text(omega_text))


def _stored_cover_representatives(
    outer,
    pair_record: dict[str, object],
) -> SparseMap:
    """Reconstruct and structurally verify one frozen invariant cocycle basis."""

    raw_basis = pair_record.get("cocycle_basis")
    if not isinstance(raw_basis, dict) or raw_basis.get("exact") is not True:
        raise ValueError("pair record lacks an exact cocycle basis")
    dimension = raw_basis.get("dimension")
    raw_representatives = raw_basis.get("representatives")
    if (
        isinstance(dimension, bool)
        or not isinstance(dimension, int)
        or not isinstance(raw_representatives, list)
        or len(raw_representatives) != dimension
    ):
        raise ValueError("stored cocycle dimension is inconsistent")
    coordinates = _total_basis_coordinates(outer, 1)
    rows: list[dict[int, Eisenstein]] = [
        {} for _ in range(outer.total[1].dimension)
    ]
    names = []
    for column, raw_representative in enumerate(raw_representatives):
        if not isinstance(raw_representative, dict):
            raise ValueError("stored cocycle representatives must be objects")
        name = raw_representative.get("name")
        terms = raw_representative.get("terms")
        if not isinstance(name, str) or not isinstance(terms, list):
            raise ValueError("stored cocycle name or terms are invalid")
        names.append(name)
        for term in terms:
            if not isinstance(term, dict):
                raise ValueError("stored cocycle terms must be objects")
            index = term.get("basis_index")
            if isinstance(index, bool) or not isinstance(index, int):
                raise ValueError("stored cocycle basis indices must be integers")
            if index < 0 or index >= len(coordinates):
                raise ValueError("stored cocycle basis index is out of range")
            if term.get("basis_coordinate") != _basis_coordinate_record(
                coordinates[index]
            ):
                raise ValueError("stored cocycle coordinate does not match its index")
            coefficient = _eisenstein_text(term.get("coefficient"))
            if coefficient.is_zero() or column in rows[index]:
                raise ValueError("stored cocycle term is zero or duplicated")
            rows[index][column] = coefficient
    domain = VectorSpace("stored-invariant-Ext1", tuple(names), Eisenstein)
    result = SparseMap(domain, outer.total[1], _freeze_rows(rows))
    outgoing = dict(outer.total_differentials).get(1)
    if outgoing is not None and not outgoing.compose(result).is_zero():
        raise ValueError("stored invariant representative is not a cover cocycle")
    return result


def _constituent_key(algebra: SparseEndomorphismAlgebraAudit) -> str:
    """Return a collision-free structural key for one constituent presentation."""

    presentation = algebra.invariant.outer.left
    ray = presentation.ray
    return "|".join(
        (
            ray.cokernel.scheme.name,
            *(str(value) for value in ray.character_pair),
            str(presentation.factor),
            *(str(value) for value in presentation.twist),
        )
    )


def _constituent_record(
    algebra: SparseEndomorphismAlgebraAudit,
) -> dict[str, object]:
    """Serialize the exact algebra facts needed by every pair action."""

    return {
        "key": _constituent_key(algebra),
        "scheme": algebra.invariant.outer.left.candidate.scheme.name,
        "factor": algebra.invariant.outer.left.factor,
        "twist": list(algebra.invariant.outer.left.twist),
        "character_pair": [
            str(value) for value in algebra.invariant.outer.left.ray.character_pair
        ],
        "invariant_h0_dimension": algebra.cocycles.representatives.domain.dimension,
        "identity_coordinates": [str(value) for value in algebra.identity_coordinates],
        "unit_locus_determinant": _polynomial_record(algebra.unit_polynomial),
        "ordinary_chain_maps": algebra.ordinary_chain_maps,
        "associative": algebra.associative,
        "identity_exact": algebra.identity_exact,
        "exact": algebra.exact,
    }


@dataclass(frozen=True, slots=True)
class SchoenOuterAutomorphismPairAudit:
    """One exact zero-space or positive scalar-action pair certificate."""

    global_pair_index: int
    candidate_pair_index: int
    candidate_index: int
    invariant_certificate_digest: str
    invariant_ext_one_dimension: int
    left_constituent: dict[str, object] | None
    right_constituent: dict[str, object] | None
    action: dict[str, object]

    @property
    def exact(self) -> bool:
        """Return whether this pair's complete automorphism quotient is exact."""

        return self.action.get("exact") is True

    def as_record(self) -> dict[str, object]:
        """Serialize this pair while keeping rank-four construction unavailable."""

        record: dict[str, object] = {
            "global_pair_index": self.global_pair_index,
            "candidate_pair_index": self.candidate_pair_index,
            "candidate_index": self.candidate_index,
            "invariant_certificate_digest": self.invariant_certificate_digest,
            "invariant_ext_one_dimension": self.invariant_ext_one_dimension,
            "automorphism_action": self.action,
            "canonical_orbits_computed": self.exact,
            "outer_extension_constructed": False,
            "exact": self.exact,
        }
        if self.left_constituent is not None and self.right_constituent is not None:
            record["left_constituent_key"] = self.left_constituent["key"]
            record["right_constituent_key"] = self.right_constituent["key"]
        return record


def audit_schoen_outer_automorphism_pair(
    task: InvariantPairTask,
    pair_record: dict[str, object],
) -> SchoenOuterAutomorphismPairAudit:
    """Audit one stored pair and release every exact sparse cache afterward."""

    global_index, pair_index, candidate_index, candidate, left_ray, right_ray, _ = task
    digest = pair_record.get("certificate_digest")
    subcomplex = pair_record.get("invariant_subcomplex")
    if not isinstance(digest, str) or not isinstance(subcomplex, dict):
        raise ValueError("invariant pair record is missing its bound certificate")
    dimension = subcomplex.get("invariant_ext_one_dimension")
    if isinstance(dimension, bool) or not isinstance(dimension, int):
        raise ValueError("invariant Ext-one dimension must be an integer")
    if dimension == 0:
        return SchoenOuterAutomorphismPairAudit(
            global_index,
            pair_index,
            candidate_index,
            digest,
            dimension,
            None,
            None,
            {
                "extension_dimension": 0,
                "unique_action": True,
                "orbit_count": 1,
                "zero_orbit": {"representative": [], "split_extension": True},
                "canonical_orbits_computed": True,
                "outer_extension_constructed": False,
                "exact": True,
                "status": "zero Ext space has the unique trivial action and split orbit",
            },
        )
    try:
        outer = sparse_outer_hom(
            left_ray,
            right_ray,
            candidate.left_factor,
            candidate.left_twist,
            candidate.right_factor,
            candidate.right_twist,
        )
        representatives = _stored_cover_representatives(outer, pair_record)
        if representatives.domain.dimension != dimension:
            raise ValueError("stored cocycles disagree with invariant Ext dimension")
        left = sparse_constituent_endomorphism_algebra(
            left_ray,
            candidate.left_factor,
            candidate.left_twist,
        )
        right = sparse_constituent_endomorphism_algebra(
            right_ray,
            candidate.right_factor,
            candidate.right_twist,
        )
        action = sparse_outer_cover_scalar_action(
            outer,
            representatives,
            left,
            right,
        )
        if not action.exact:
            raise ValueError("pair automorphism action is not exactly scalar")
        return SchoenOuterAutomorphismPairAudit(
            global_index,
            pair_index,
            candidate_index,
            digest,
            dimension,
            _constituent_record(left),
            _constituent_record(right),
            action.as_record(),
        )
    finally:
        _clear_worker_caches()


__all__ = [
    "SchoenOuterAutomorphismPairAudit",
    "audit_schoen_outer_automorphism_pair",
]
