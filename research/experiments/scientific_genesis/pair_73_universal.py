"""Certify the universal exact Ext family for computable-carrier pair 73.

Owns:
    Parameter-linear assembly of the four certified invariant cocycles,
    specialization identities, split/non-split loci, and projective quotient data.

Depends on:
    Content-addressed invariant-cocycle and automorphism-action artifacts plus
    reusable exact Eisenstein polynomial arithmetic.

Must not:
    Select a projective point, call a cohomology family a rank-four bundle,
    invent transition lifts, or claim local freeness, descent, or stability.

Phase 0:
    The universal Ext class is exact; its chain-level mapping-cone lift remains
    the first missing carrier construction input.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import cache
from pathlib import Path
from typing import cast

from onetheory.math.numbers import Eisenstein
from onetheory.math.polynomials import Polynomial, PolynomialIdeal
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    DEFAULT_INVARIANT_ARTIFACT,
    DEFAULT_PARTIAL,
    _canonical_digest,
    _read_partial,
    _validated_invariant_records,
)
from research.experiments.computable_carrier.tier_b_schoen_outer_automorphisms import (
    _eisenstein_text,
)

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/pair_73_universal_ext.json"
PAIR_INDEX = 73
PARAMETERS = ("a0", "a1", "a2", "a3")
FIRST_MISSING_INPUT = (
    "chain-level lift of the universal Cech-Koszul Ext cocycle into compatible "
    "constituent transition or resolution maps"
)


def _coefficient(polynomial: Polynomial) -> Eisenstein:
    """Extract one exact constant after a complete specialization."""

    if polynomial.variable_count != 0:
        raise ValueError("specialization did not eliminate every parameter")
    return cast(Eisenstein, polynomial.coefficient(()))


def _parameter(index: int) -> Polynomial:
    """Return one exact coordinate variable in the universal parameter ring."""

    exponents = tuple(int(position == index) for position in range(len(PARAMETERS)))
    return Polynomial.monomial(exponents, scalar_type=Eisenstein)


@dataclass(frozen=True, slots=True)
class UniversalExtFamily:
    """The universal pair-73 cohomology class before a mapping-cone lift."""

    ambient_dimension: int
    basis_names: tuple[str, ...]
    basis_columns: tuple[tuple[Eisenstein, ...], ...]
    universal_coordinates: tuple[Polynomial, ...]
    invariant_certificate_digest: str
    automorphism_certificate_digest: str
    source_cocycles_exact: bool
    quotient_action_exact: bool

    def __post_init__(self) -> None:
        if self.ambient_dimension <= 0:
            raise ValueError("a universal Ext family requires a positive ambient space")
        if len(self.basis_names) != len(PARAMETERS):
            raise ValueError("pair 73 requires exactly four named Ext basis classes")
        if len(self.basis_columns) != len(PARAMETERS):
            raise ValueError("pair 73 requires exactly four Ext coordinate columns")
        if any(len(column) != self.ambient_dimension for column in self.basis_columns):
            raise ValueError("Ext columns do not span the declared ambient basis")
        if len(self.universal_coordinates) != self.ambient_dimension:
            raise ValueError("universal coordinates do not span the ambient basis")
        if any(
            polynomial.variable_count != len(PARAMETERS)
            or polynomial.scalar_type is not Eisenstein
            or polynomial.degree > 1
            for polynomial in self.universal_coordinates
        ):
            raise ValueError("universal coordinates must be linear over Q(omega)")
        if not self.source_cocycles_exact or not self.quotient_action_exact:
            raise ValueError("universal assembly requires exact source certificates")
        for index in range(len(PARAMETERS)):
            values = tuple(Eisenstein(int(position == index)) for position in range(4))
            if self.specialize(values) != self.basis_columns[index]:
                raise ValueError("universal specialization does not recover its Ext basis")

    @property
    def parameter_dimension(self) -> int:
        """Return the affine parameter-space dimension."""

        return len(PARAMETERS)

    @property
    def nonzero_coordinate_count(self) -> int:
        """Return the number of occupied ambient cocycle coordinates."""

        return sum(not polynomial.is_zero() for polynomial in self.universal_coordinates)

    @property
    def split_locus_ideal(self) -> PolynomialIdeal:
        """Return the exact origin ideal where the cohomology class vanishes."""

        return PolynomialIdeal(
            tuple(_parameter(index) for index in range(len(PARAMETERS))),
            variable_count=len(PARAMETERS),
            scalar_type=Eisenstein,
        )

    @property
    def universal_class_exact(self) -> bool:
        """Return exactness by linearity from the certified cocycle basis."""

        return self.source_cocycles_exact and all(
            self.specialize(tuple(Eisenstein(int(position == index)) for position in range(4)))
            == self.basis_columns[index]
            for index in range(4)
        )

    def specialize(self, values: tuple[Eisenstein, ...]) -> tuple[Eisenstein, ...]:
        """Evaluate the universal class at one exact affine parameter tuple."""

        if len(values) != len(PARAMETERS):
            raise ValueError("pair 73 specialization requires four parameters")
        return tuple(
            _coefficient(polynomial.substitute(values)) for polynomial in self.universal_coordinates
        )

    def as_record(self) -> dict[str, object]:
        """Serialize the universal class and preserve its first missing lift."""

        terms = []
        for ambient_index, polynomial in enumerate(self.universal_coordinates):
            if polynomial.is_zero():
                continue
            terms.append(
                {
                    "ambient_index": ambient_index,
                    "coefficients": [
                        {
                            "parameter": PARAMETERS[exponents.index(1)],
                            "coefficient": str(coefficient),
                        }
                        for exponents, coefficient in polynomial.terms
                    ],
                }
            )
        return {
            "schema": "pair-73-universal-ext-v1",
            "global_pair_index": PAIR_INDEX,
            "coefficient_field": "Q(omega)",
            "parameters": list(PARAMETERS),
            "affine_parameter_space": "A^4(Q(omega))",
            "basis_names": list(self.basis_names),
            "ambient_cocycle_dimension": self.ambient_dimension,
            "nonzero_ambient_coordinate_count": self.nonzero_coordinate_count,
            "universal_class_terms": terms,
            "source_cocycles_exact": self.source_cocycles_exact,
            "universal_class_exact": self.universal_class_exact,
            "basis_specializations_exact": True,
            "split_locus": {
                "ideal_generators": list(PARAMETERS),
                "description": "the affine origin only",
            },
            "non_split_locus": "A^4(Q(omega)) minus the origin",
            "automorphism_quotient": "P^3(Q(omega))",
            "quotient_action_exact": self.quotient_action_exact,
            "arbitrary_extension_point_selected": False,
            "invariant_certificate_digest": self.invariant_certificate_digest,
            "automorphism_certificate_digest": self.automorphism_certificate_digest,
            "mapping_cone_constructed": False,
            "first_missing_input": FIRST_MISSING_INPUT,
            "status": (
                "exact universal invariant Ext family; chain-level mapping cone, "
                "local freeness, descent, Chern gates, and stability remain unresolved"
            ),
        }


@cache
def pair_73_universal_ext_family() -> UniversalExtFamily:
    """Reconstruct the exact universal class from verified pair certificates."""

    invariant_digest, invariant_records = _validated_invariant_records(DEFAULT_INVARIANT_ARTIFACT)
    actions, _ = _read_partial(DEFAULT_PARTIAL, invariant_digest)
    invariant = invariant_records[PAIR_INDEX - 1]
    action = actions[PAIR_INDEX]
    if invariant.get("exact") is not True or action.get("exact") is not True:
        raise ValueError("pair 73 certificates must both be exact")
    if action.get("invariant_certificate_digest") != invariant.get("certificate_digest"):
        raise ValueError("pair 73 action is not bound to its invariant certificate")
    raw_basis = invariant.get("cocycle_basis")
    raw_action = action.get("automorphism_action")
    if not isinstance(raw_basis, dict) or not isinstance(raw_action, dict):
        raise ValueError("pair 73 lacks cocycle or action records")
    if raw_basis.get("dimension") != 4 or raw_action.get("extension_dimension") != 4:
        raise ValueError("pair 73 is no longer four-dimensional")
    if raw_action.get("nonzero_orbit_space") != "P^3(Q(omega))":
        raise ValueError("pair 73 no longer has the scalar projective quotient")
    raw_ambient = raw_basis.get("ambient_basis")
    raw_representatives = raw_basis.get("representatives")
    if not isinstance(raw_ambient, dict) or not isinstance(raw_representatives, list):
        raise ValueError("pair 73 cocycle basis has an invalid shape")
    ambient_dimension = raw_ambient.get("dimension")
    if isinstance(ambient_dimension, bool) or not isinstance(ambient_dimension, int):
        raise ValueError("pair 73 ambient dimension must be an integer")

    columns: list[list[Eisenstein]] = [
        [Eisenstein(0) for _ in range(ambient_dimension)] for _ in range(4)
    ]
    names = []
    for column_index, raw_representative in enumerate(raw_representatives):
        if not isinstance(raw_representative, dict):
            raise ValueError("pair 73 representatives must be objects")
        name = raw_representative.get("name")
        raw_terms = raw_representative.get("terms")
        if not isinstance(name, str) or not isinstance(raw_terms, list):
            raise ValueError("pair 73 representative names or terms are invalid")
        names.append(name)
        for raw_term in raw_terms:
            if not isinstance(raw_term, dict):
                raise ValueError("pair 73 representative terms must be objects")
            index = raw_term.get("basis_index")
            if isinstance(index, bool) or not isinstance(index, int):
                raise ValueError("pair 73 basis indices must be integers")
            if not 0 <= index < ambient_dimension:
                raise ValueError("pair 73 basis index is out of range")
            coefficient = _eisenstein_text(raw_term.get("coefficient"))
            if coefficient.is_zero() or not columns[column_index][index].is_zero():
                raise ValueError("pair 73 has a zero or duplicate cocycle term")
            columns[column_index][index] = coefficient

    parameters = tuple(_parameter(index) for index in range(4))
    universal = tuple(
        sum(
            (parameters[column].scale(columns[column][row]) for column in range(4)),
            Polynomial.zero(4, scalar_type=Eisenstein),
        )
        for row in range(ambient_dimension)
    )
    return UniversalExtFamily(
        ambient_dimension,
        tuple(names),
        tuple(tuple(column) for column in columns),
        universal,
        cast(str, invariant["certificate_digest"]),
        cast(str, action["certificate_digest"]),
        raw_basis.get("cover_cycles_exact") is True and raw_basis.get("quotient_exact") is True,
        raw_action.get("quotient_action_exact") is True,
    )


def write_pair_73_universal_ext(path: Path = OUTPUT) -> dict[str, object]:
    """Write one content-addressed universal-family certificate atomically."""

    payload = pair_73_universal_ext_family().as_record()
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
    """Regenerate the universal-family artifact and report its open boundary."""

    payload = write_pair_73_universal_ext()
    print(f"artifact_digest: {payload['artifact_digest']}")
    print(f"parameter_space: {payload['affine_parameter_space']}")
    print(f"non_split_quotient: {payload['automorphism_quotient']}")
    print(f"mapping_cone_constructed: {payload['mapping_cone_constructed']}")
    print(f"first_missing_input: {payload['first_missing_input']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
