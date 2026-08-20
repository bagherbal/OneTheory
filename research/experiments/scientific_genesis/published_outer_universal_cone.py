"""Build the universal published outer extension from strict Čech representatives.

Owns:
    Parameter-linear assembly of the four forward outer cocycles, the universal
    block-cone differential, and exact split, local-freeness, descent, and Chern gates.

Depends on:
    The content-addressed invariant outer basis, exact polynomial parameters,
    and published constituent/vector-bundle topology with explicit provenance.

Must not:
    Select a projective point, infer stability from local freeness, call the
    full nonzero family genuinely SU(4), or use observables to choose parameters.

Phase 0:
    Research-only universal rank-four derived cone; its stable SU(4) locus is open.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import cache
from pathlib import Path
from typing import cast

from onetheory.math.numbers import Eisenstein
from onetheory.math.polynomials import Polynomial, PolynomialIdeal
from onetheory.models.heterotic_schoen.geometry import schoen_geometry
from onetheory.models.heterotic_schoen.visible import visible_bundle
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.computable_carrier.schoen_serre_outer_transfer import (
    OuterCechBasis,
    OuterCechComponent,
    SparseOuterCechCochain,
)
from research.experiments.computable_carrier.tier_b_schoen_outer_automorphisms import (
    _eisenstein_text,
)

from .published_outer_cech_invariants import OUTPUT as INVARIANT_ARTIFACT

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/published_outer_universal_cone.json"
PARAMETERS = ("a0", "a1", "a2", "a3")


def _parameter(index: int) -> Polynomial:
    """Return one exact coordinate of the four-variable parameter ring."""

    return Polynomial.monomial(
        tuple(int(index == position) for position in range(len(PARAMETERS))),
        scalar_type=Eisenstein,
    )


def _constant(polynomial: Polynomial) -> Eisenstein:
    """Extract one exact scalar after complete specialization."""

    if polynomial.variable_count != 0:
        raise ValueError("universal specialization left an unresolved parameter")
    return cast(Eisenstein, polynomial.coefficient(()))


def _basis(raw: object) -> OuterCechBasis:
    """Decode one typed full Čech basis label from the frozen certificate."""

    if not isinstance(raw, dict):
        raise ValueError("outer Čech basis records must be objects")
    component = OuterCechComponent(
        cast(int, raw["left_object"]),
        cast(int, raw["right_object"]),
        cast(int, raw["object_degree"]),
        cast(tuple[int, int, int], tuple(raw["line_degree"])),
        cast(str, raw["koszul_summand"]),
    )
    return OuterCechBasis(
        component,
        cast(tuple[int, int, int], tuple(raw["x_monomial"])),
        cast(tuple[int, int, int], tuple(raw["u_monomial"])),
        cast(tuple[int, int], tuple(raw["p_monomial"])),
        cast(
            tuple[tuple[int, ...], tuple[int, ...], tuple[int, ...]],
            tuple(tuple(simplex) for simplex in raw["cell"]),
        ),
    )


def _load_invariant_basis(
    path: Path = INVARIANT_ARTIFACT,
) -> tuple[str, tuple[SparseOuterCechCochain, ...]]:
    """Load and validate the exact forward basis from its reproducible artifact."""

    payload = json.loads(path.read_text(encoding="utf-8"))
    digest = payload.pop("artifact_digest", None)
    if not isinstance(digest, str) or digest != _canonical_digest(payload):
        raise ValueError("published invariant outer artifact digest does not verify")
    forward = payload.get("forward")
    if not isinstance(forward, dict):
        raise ValueError("published invariant artifact lacks its forward direction")
    if (
        forward.get("invariant_h1_dimension") != 4
        or forward.get("exact") is not True
        or forward.get("full_representatives_are_cycles") is not True
        or forward.get("full_representatives_are_strictly_invariant") is not True
    ):
        raise ValueError("published forward invariant basis is not exact")
    raw_representatives = forward.get("full_cech_koszul_representatives")
    if not isinstance(raw_representatives, list) or len(raw_representatives) != 4:
        raise ValueError("published forward invariant basis must have four classes")
    representatives = []
    for raw_representative in raw_representatives:
        if not isinstance(raw_representative, dict):
            raise ValueError("published invariant representatives must be objects")
        raw_terms = raw_representative.get("terms")
        if not isinstance(raw_terms, list) or not raw_terms:
            raise ValueError("published invariant representatives require exact terms")
        representatives.append(
            SparseOuterCechCochain(
                tuple(
                    (
                        _basis(term["basis"]),
                        _eisenstein_text(term["coefficient"]),
                    )
                    for term in raw_terms
                    if isinstance(term, dict)
                )
            )
        )
    if any(representative.is_zero() for representative in representatives):
        raise ValueError("an invariant outer basis class vanished while decoding")
    return digest, tuple(representatives)


@dataclass(frozen=True, slots=True)
class ParameterizedOuterCechCochain:
    """An immutable full Čech cochain with linear polynomial coefficients."""

    terms: tuple[tuple[OuterCechBasis, Polynomial], ...]

    def __init__(
        self,
        terms: tuple[tuple[OuterCechBasis, Polynomial], ...] = (),
    ) -> None:
        values: dict[OuterCechBasis, Polynomial] = {}
        for basis, coefficient in terms:
            if coefficient.variable_count != len(PARAMETERS):
                raise ValueError("universal outer coefficients require four parameters")
            if coefficient.scalar_type is not Eisenstein or coefficient.degree > 1:
                raise ValueError("universal outer coefficients must be linear over Q(omega)")
            values[basis] = values.get(
                basis,
                Polynomial.zero(len(PARAMETERS), scalar_type=Eisenstein),
            ) + coefficient
        object.__setattr__(
            self,
            "terms",
            tuple(
                (basis, coefficient)
                for basis, coefficient in sorted(values.items())
                if not coefficient.is_zero()
            ),
        )

    def specialize(self, values: tuple[Eisenstein, ...]) -> SparseOuterCechCochain:
        """Evaluate the universal cochain at one exact affine parameter point."""

        if len(values) != len(PARAMETERS):
            raise ValueError("universal outer specialization requires four values")
        return SparseOuterCechCochain(
            tuple(
                (basis, _constant(coefficient.substitute(values)))
                for basis, coefficient in self.terms
            )
        )


@dataclass(frozen=True, slots=True)
class PublishedUniversalOuterCone:
    """The exact universal rank-four derived cone before stability selection."""

    invariant_artifact_digest: str
    basis_representatives: tuple[SparseOuterCechCochain, ...]
    extension: ParameterizedOuterCechCochain
    basis_cycles_exact: bool
    basis_invariant_exact: bool
    rank: int
    determinant_c1: tuple[str, str, str]
    second_chern: tuple[str, str, str]
    third_chern: str

    def __post_init__(self) -> None:
        if len(self.basis_representatives) != len(PARAMETERS):
            raise ValueError("the published universal cone requires four basis classes")
        if not self.basis_cycles_exact or not self.basis_invariant_exact:
            raise ValueError("the universal cone requires closed invariant basis classes")
        if self.rank != 4 or self.determinant_c1 != ("0", "0", "0"):
            raise ValueError("the universal cone lost rank four or trivial determinant")
        for index, representative in enumerate(self.basis_representatives):
            values = tuple(
                Eisenstein(int(position == index))
                for position in range(len(PARAMETERS))
            )
            if self.extension.specialize(values) != representative:
                raise ValueError("a universal basis specialization failed")

    @property
    def split_locus_ideal(self) -> PolynomialIdeal:
        """Return the exact affine-origin ideal where the Ext class vanishes."""

        return PolynomialIdeal(
            tuple(_parameter(index) for index in range(len(PARAMETERS))),
            variable_count=len(PARAMETERS),
            scalar_type=Eisenstein,
        )

    @property
    def mapping_cone_squared_zero(self) -> bool:
        """Return the universal block-square identity by coefficient linearity."""

        return self.basis_cycles_exact

    @property
    def equivariant_descent_exact(self) -> bool:
        """Return descent of the universal invariant extension family."""

        return self.basis_invariant_exact

    @property
    def local_freeness_exact(self) -> bool:
        """Return the local extension theorem for the published constituents."""

        return True

    def as_record(self) -> dict[str, object]:
        """Serialize algebraic closure without claiming a stable SU(4) locus."""

        return {
            "schema": "published-outer-universal-cone-v1",
            "coefficient_field": "Q(omega)",
            "parameters": list(PARAMETERS),
            "parameter_ring": "Q(omega)[a0,a1,a2,a3]",
            "affine_parameter_space": "A^4(Q(omega))",
            "projective_non_split_space": "P^3(Q(omega))",
            "split_locus": {
                "ideal_generators": list(PARAMETERS),
                "description": "the affine origin only",
            },
            "non_split_locus": "A^4(Q(omega)) minus the origin",
            "basis_names": [f"e_{index}" for index in range(len(PARAMETERS))],
            "basis_term_counts": [
                len(representative.terms)
                for representative in self.basis_representatives
            ],
            "universal_term_count": len(self.extension.terms),
            "invariant_artifact_digest": self.invariant_artifact_digest,
            "generated_complex": {
                "objects": ["V1", "V2"],
                "differential": "D_E(a)=[[D_V1,e(a)],[0,D_V2]]",
                "extension": "e(a)=a0 e_0+a1 e_1+a2 e_2+a3 e_3",
                "squared_zero": self.mapping_cone_squared_zero,
                "parameter_linear": True,
            },
            "rank": self.rank,
            "determinant_c1": list(self.determinant_c1),
            "chern_classes": {
                "c1": list(self.determinant_c1),
                "c2": list(self.second_chern),
                "c3": self.third_chern,
                "parameter_independent": True,
            },
            "local_freeness_locus": "all A^4(Q(omega))",
            "local_freeness_theorem": (
                "an extension of locally free sheaves is locally free because "
                "the quotient is projective on each local stalk"
            ),
            "equivariant_descent_exact": self.equivariant_descent_exact,
            "descent_locus": "all A^4(Q(omega))",
            "arbitrary_extension_point_selected": False,
            "genuine_su4_locus_computed": False,
            "first_missing_input": (
                "the exact stable locus and exclusion of accidental proper "
                "structure-group reductions over P^3(Q(omega))"
            ),
            "status": (
                "exact universal non-split locally free descended rank-four "
                "derived cone; genuine SU(4) remains conditional on stability"
            ),
        }


@cache
def published_universal_outer_cone() -> PublishedUniversalOuterCone:
    """Construct the universal cone without choosing a projective point."""

    digest, representatives = _load_invariant_basis()
    extension = ParameterizedOuterCechCochain(
        tuple(
            (basis, _parameter(index).scale(coefficient))
            for index, representative in enumerate(representatives)
            for basis, coefficient in representative.terms
        )
    )
    published = visible_bundle(schoen_geometry()).bundle
    return PublishedUniversalOuterCone(
        digest,
        representatives,
        extension,
        True,
        True,
        published.rank,
        tuple(str(value) for value in published.c1),
        tuple(str(value) for value in published.c2),
        str(published.c3),
    )


def write_published_universal_outer_cone(
    path: Path = OUTPUT,
) -> dict[str, object]:
    """Write the content-addressed universal outer-cone certificate."""

    payload = published_universal_outer_cone().as_record()
    payload["artifact_digest"] = _canonical_digest(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)
    return payload


def main() -> int:
    """Regenerate the universal outer-cone artifact."""

    payload = write_published_universal_outer_cone()
    print(f"artifact_digest: {payload['artifact_digest']}")
    print(f"projective_non_split_space: {payload['projective_non_split_space']}")
    print(f"mapping_cone_squared_zero: {payload['generated_complex']['squared_zero']}")
    print(f"first_missing_input: {payload['first_missing_input']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "ParameterizedOuterCechCochain",
    "PublishedUniversalOuterCone",
    "published_universal_outer_cone",
]
