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

import hashlib
import json
from dataclasses import dataclass
from fractions import Fraction

from onetheory.math.homological import VectorSpace
from onetheory.math.numbers import Eisenstein, Rational

from .schoen_sparse_outer import SparseMap, _freeze_rows, sparse_outer_hom
from .schoen_sparse_outer_actions import (
    _basis_coordinate_record,
    _total_basis_coordinates,
    sparse_outer_invariant_audit,
    sparse_outer_invariant_cocycles,
)
from .schoen_sparse_outer_automorphisms import (
    SparseEndomorphismAlgebraAudit,
    _polynomial_record,
    classify_sparse_outer_automorphism_orbits,
    classify_sparse_square_zero_orbits,
    sparse_constituent_endomorphism_algebra,
    sparse_outer_automorphism_action,
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


def constituent_presentation_identity(
    ray,
    factor: int,
    twist: tuple[int, int, int],
) -> dict[str, object]:
    """Return the complete exact identity of one constituent presentation."""

    return {
        "scheme": ray.cokernel.scheme.name,
        "target_line_shift": ray.cokernel.target_line_shift,
        "character_pair": [str(value) for value in ray.character_pair],
        "extension_map": [
            _polynomial_record(polynomial) for polynomial in ray.extension_map
        ],
        "factor": factor,
        "twist": list(twist),
    }


def constituent_presentation_key(identity: dict[str, object]) -> str:
    """Return the SHA-256 content address of one presentation identity."""

    canonical = json.dumps(
        identity,
        sort_keys=True,
        separators=(",", ":"),
    )
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return f"schoen-constituent-sha256:{digest}"


def _constituent_identity(
    algebra: SparseEndomorphismAlgebraAudit,
) -> dict[str, object]:
    """Return the complete identity carried by one computed algebra."""

    presentation = algebra.invariant.outer.left
    return constituent_presentation_identity(
        presentation.ray,
        presentation.factor,
        presentation.twist,
    )


def _constituent_record(
    algebra: SparseEndomorphismAlgebraAudit,
) -> dict[str, object]:
    """Serialize the exact algebra facts needed by every pair action."""

    identity = _constituent_identity(algebra)
    return {
        "key": constituent_presentation_key(identity),
        "presentation_identity": identity,
        "invariant_h0_dimension": algebra.cocycles.representatives.domain.dimension,
        "identity_coordinates": [str(value) for value in algebra.identity_coordinates],
        "unit_locus_determinant": _polynomial_record(algebra.unit_polynomial),
        "ordinary_chain_maps": algebra.ordinary_chain_maps,
        "associative": algebra.associative,
        "identity_exact": algebra.identity_exact,
        "exact": algebra.exact,
    }


def _compact_projective_record(record: dict[str, object]) -> dict[str, object]:
    """Replace expanded projective charts by one exact normalization rule."""

    compact = dict(record)
    charts = compact.pop("canonical_normal_form_charts", None)
    dimension = compact.get("extension_dimension")
    if isinstance(dimension, bool) or not isinstance(dimension, int) or dimension < 1:
        raise ValueError("projective orbit records require positive dimension")
    if not isinstance(charts, list) or len(charts) != dimension:
        raise ValueError("expanded projective charts do not span the Ext basis")
    compact["canonical_normal_form"] = {
        "rule": "normalize the first nonzero coordinate to one",
        "pivot_index_range": [0, dimension - 1],
        "coordinates_before_pivot": "zero",
        "coordinates_after_pivot": "free",
        "chart_count": dimension,
    }
    return compact


def _quotient_scalar_action_record(
    outer,
    representatives: SparseMap,
    left: SparseEndomorphismAlgebraAudit,
    right: SparseEndomorphismAlgebraAudit,
    cover_dimension: int,
) -> dict[str, object]:
    """Reduce a nonscalar cover action and certify its quotient representation."""

    invariant = sparse_outer_invariant_audit(outer, cover_dimension)
    cocycles = sparse_outer_invariant_cocycles(invariant)
    if (
        cocycles.cover_representatives.codomain != representatives.codomain
        or cocycles.cover_representatives.domain.basis
        != representatives.domain.basis
        or cocycles.cover_representatives.rows != representatives.rows
    ):
        raise ValueError("recomputed invariant cocycles disagree with frozen artifact")
    action = sparse_outer_automorphism_action(cocycles, left, right)
    classification = classify_sparse_outer_automorphism_orbits(action)
    if classification.exact:
        record = _compact_projective_record(classification.as_record())
    else:
        square_zero = classify_sparse_square_zero_orbits(action)
        if not square_zero.exact:
            raise ValueError(
                "quotient action is neither scalar nor square-zero unipotent"
            )
        record = square_zero.as_record()
    record.update(
        {
            "action_proof": "exact quotient reduction modulo coboundaries",
            "left_cover_equalities": False,
            "right_cover_equalities": False,
            "quotient_action_exact": action.exact,
            "module_laws_exact": action.module_laws_exact,
            "actions_commute": action.actions_commute,
        }
    )
    return record


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

    (
        global_index,
        pair_index,
        candidate_index,
        candidate,
        left_ray,
        right_ray,
        cover_dimension,
    ) = task
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
        if action.exact:
            action_record = _compact_projective_record(action.as_record())
            action_record["action_proof"] = "exact equality on cover cocycles"
            action_record["quotient_action_exact"] = True
        else:
            action_record = _quotient_scalar_action_record(
                outer,
                representatives,
                left,
                right,
                cover_dimension,
            )
        return SchoenOuterAutomorphismPairAudit(
            global_index,
            pair_index,
            candidate_index,
            digest,
            dimension,
            _constituent_record(left),
            _constituent_record(right),
            action_record,
        )
    finally:
        _clear_worker_caches()


__all__ = [
    "SchoenOuterAutomorphismPairAudit",
    "audit_schoen_outer_automorphism_pair",
    "constituent_presentation_identity",
    "constituent_presentation_key",
]
