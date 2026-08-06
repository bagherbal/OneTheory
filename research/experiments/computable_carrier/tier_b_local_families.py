"""Classify bounded local invariant-scheme normal forms.

Owns:
    Exact weighted local Artin normal forms of length at most three at the
    special reduced Tier B orbit types, including the two curvilinear
    parameter families absent from the coordinate-monomial search.

Depends on:
    The exact special-orbit classification and the Eisenstein coefficient
    field. The records describe completed local ideals; no global polynomial
    intersection or affine-chart sheafification is assumed.

Must not:
    Treat a local normal form as a global invariant point scheme, choose a
    parameter as a physical coefficient, claim a Serre constituent, or infer
    quotient descent, stability, spectrum, or carrier promotion.

Phase 0:
    The bounded local stabilizer classification is exact as a normal-form
    diagnostic; global parameterized ideals and their equivariant Serre
    constructions remain unresolved.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import cache

from .tier_b_orbits import tier_b_reduced_orbit_classification

LocalMonomial = tuple[int, int]


@dataclass(frozen=True, slots=True)
class LocalRelation:
    """One weighted homogeneous relation in completed local coordinates."""

    monomials: tuple[LocalMonomial, ...]
    coefficients: tuple[str, ...]
    weight: int

    def __post_init__(self) -> None:
        if not self.monomials or len(self.monomials) != len(self.coefficients):
            raise ValueError("local relations require matching nonempty terms")
        if self.weight not in (0, 1, 2):
            raise ValueError("local stabilizer weights are residues modulo three")
        if any(
            len(monomial) != 2
            or any(
                isinstance(exponent, bool)
                or not isinstance(exponent, int)
                or exponent < 0
                for exponent in monomial
            )
            for monomial in self.monomials
        ):
            raise ValueError("local relation monomials require nonnegative pairs")
        if any(not coefficient.strip() for coefficient in self.coefficients):
            raise ValueError("local relation coefficients require expressions")

    @property
    def weighted(self) -> bool:
        """Return whether every displayed monomial has the declared weight."""

        return all(
            (monomial[0] + 2 * monomial[1]) % 3 == self.weight
            for monomial in self.monomials
        )

    def as_record(self) -> dict[str, object]:
        """Serialize the weighted relation without evaluating parameters."""

        return {
            "monomials": [list(monomial) for monomial in self.monomials],
            "coefficients": list(self.coefficients),
            "weight_mod_3": self.weight,
            "weighted": self.weighted,
        }


@dataclass(frozen=True, slots=True)
class LocalInvariantNormalForm:
    """One bounded stabilizer-invariant local Artin normal form."""

    orbit_identifier: str
    name: str
    length: int
    standard_monomials: tuple[LocalMonomial, ...]
    relations: tuple[LocalRelation, ...]
    parameter_symbol: str | None
    parameter_domain: str | None
    tangent_weights: tuple[int, int] = (1, 2)

    def __post_init__(self) -> None:
        if self.length not in (1, 2, 3):
            raise ValueError("the local Tier B bound has lengths one through three")
        if self.tangent_weights != (1, 2):
            raise ValueError("the special-orbit tangent weights must be (1, 2)")
        if len(self.standard_monomials) != self.length:
            raise ValueError("standard monomial count must equal local length")
        if len(set(self.standard_monomials)) != self.length:
            raise ValueError("standard monomials must be distinct")
        if not self.relations or not all(relation.weighted for relation in self.relations):
            raise ValueError("local normal forms require weighted relations")
        if self.parameter_symbol is None and self.parameter_domain is not None:
            raise ValueError("a parameter domain requires a parameter symbol")
        if self.parameter_symbol is not None and not self.parameter_domain:
            raise ValueError("parameterized normal forms require a declared domain")

    @property
    def parameterized(self) -> bool:
        """Return whether the normal form represents a nontrivial family."""

        return self.parameter_symbol is not None

    @property
    def exact(self) -> bool:
        """Return the exact local normal-form certificate."""

        return (
            len(self.standard_monomials) == self.length
            and all(relation.weighted for relation in self.relations)
        )

    def as_record(self) -> dict[str, object]:
        """Serialize the local form and its explicit global-scope boundary."""

        return {
            "orbit": self.orbit_identifier,
            "name": self.name,
            "length": self.length,
            "standard_monomials": [list(item) for item in self.standard_monomials],
            "relations": [relation.as_record() for relation in self.relations],
            "parameterized": self.parameterized,
            "parameter_symbol": self.parameter_symbol,
            "parameter_domain": self.parameter_domain,
            "tangent_weights": list(self.tangent_weights),
            "exact": self.exact,
            "status": (
                "exact completed-local stabilizer normal form only; global ideal "
                "construction and quotient Serre descent remain unresolved"
            ),
        }


@dataclass(frozen=True, slots=True)
class TierBLocalInvariantNormalForms:
    """Complete local normal-form report within the declared special-orbit bound."""

    group_order: int
    special_orbit_count: int
    local_length_bound: int
    tangent_weights: tuple[int, int]
    normal_forms: tuple[LocalInvariantNormalForm, ...]

    @property
    def finite_normal_form_count(self) -> int:
        """Return the total number of parameter-free local strata."""

        return sum(not item.parameterized for item in self.normal_forms)

    @property
    def parameterized_family_count(self) -> int:
        """Return the total number of parameterized local strata."""

        return sum(item.parameterized for item in self.normal_forms)

    @property
    def exact(self) -> bool:
        """Return whether every declared local form passes its exact checks."""

        return (
            self.group_order == 9
            and self.special_orbit_count == 4
            and self.local_length_bound == 3
            and self.tangent_weights == (1, 2)
            and len(self.normal_forms) == 32
            and all(item.exact for item in self.normal_forms)
        )

    def as_record(self) -> dict[str, object]:
        """Serialize the local category without promoting it globally."""

        return {
            "category": "special-orbit completed-local invariant normal forms",
            "group_order": self.group_order,
            "special_orbit_count": self.special_orbit_count,
            "local_length_bound": self.local_length_bound,
            "tangent_weights": list(self.tangent_weights),
            "normal_form_count": len(self.normal_forms),
            "parameter_free_count": self.finite_normal_form_count,
            "parameterized_family_count": self.parameterized_family_count,
            "exact": self.exact,
            "normal_forms": [item.as_record() for item in self.normal_forms],
            "global_parameterized_ideal_search": "unresolved",
            "global_serre_constituents": "unresolved",
            "status": (
                "exact local stabilizer normal-form category; global polynomial "
                "ideals, Serre extensions, and quotient descent remain unresolved"
            ),
        }


def _relation(
    monomials: tuple[LocalMonomial, ...],
    coefficients: tuple[str, ...],
) -> LocalRelation:
    """Build one relation and derive its common tangent weight."""

    weights = {(u + 2 * v) % 3 for u, v in monomials}
    if len(weights) != 1:
        raise ValueError("relation terms must share one tangent character")
    return LocalRelation(monomials, coefficients, next(iter(weights)))


def _local_forms(orbit_identifier: str) -> tuple[LocalInvariantNormalForm, ...]:
    """Return the six discrete strata and two curvilinear family strata."""

    forms = (
        LocalInvariantNormalForm(
            orbit_identifier,
            "length-one",
            1,
            ((0, 0),),
            (_relation(((1, 0),), (("1",))), _relation(((0, 1),), (("1",)))),
            None,
            None,
        ),
        LocalInvariantNormalForm(
            orbit_identifier,
            "length-two-u-axis",
            2,
            ((0, 0), (1, 0)),
            (_relation(((0, 1),), (("1",))), _relation(((2, 0),), (("1",)))),
            None,
            None,
        ),
        LocalInvariantNormalForm(
            orbit_identifier,
            "length-two-v-axis",
            2,
            ((0, 0), (0, 1)),
            (_relation(((1, 0),), (("1",))), _relation(((0, 2),), (("1",)))),
            None,
            None,
        ),
        LocalInvariantNormalForm(
            orbit_identifier,
            "length-three-double-point",
            3,
            ((0, 0), (1, 0), (0, 1)),
            (
                _relation(((2, 0),), (("1",))),
                _relation(((1, 1),), (("1",))),
                _relation(((0, 2),), (("1",))),
            ),
            None,
            None,
        ),
        LocalInvariantNormalForm(
            orbit_identifier,
            "length-three-u-curve-family",
            3,
            ((0, 0), (1, 0), (2, 0)),
            (
                _relation(((0, 1), (2, 0)), (("1", "-alpha"))),
                _relation(((3, 0),), (("1",))),
            ),
            "alpha",
            "Eisenstein coefficients excluding alpha=0 specialization",
        ),
        LocalInvariantNormalForm(
            orbit_identifier,
            "length-three-v-curve-family",
            3,
            ((0, 0), (0, 1), (0, 2)),
            (
                _relation(((1, 0), (0, 2)), (("1", "-beta"))),
                _relation(((0, 3),), (("1",))),
            ),
            "beta",
            "Eisenstein coefficients excluding beta=0 specialization",
        ),
        LocalInvariantNormalForm(
            orbit_identifier,
            "length-three-u-curve-zero-specialization",
            3,
            ((0, 0), (1, 0), (2, 0)),
            (_relation(((0, 1),), (("1",))), _relation(((3, 0),), (("1",)))),
            None,
            None,
        ),
        LocalInvariantNormalForm(
            orbit_identifier,
            "length-three-v-curve-zero-specialization",
            3,
            ((0, 0), (0, 1), (0, 2)),
            (_relation(((1, 0),), (("1",))), _relation(((0, 3),), (("1",)))),
            None,
            None,
        ),
    )
    if not all(item.exact for item in forms):
        raise ValueError("local invariant normal forms failed exact checks")
    return forms


@cache
def tier_b_local_invariant_normal_forms() -> TierBLocalInvariantNormalForms:
    """Construct local normal forms over all four special projective orbits."""

    classification = tier_b_reduced_orbit_classification()
    forms = tuple(
        item
        for orbit in classification.special_orbits
        for item in _local_forms(orbit.identifier)
    )
    result = TierBLocalInvariantNormalForms(
        classification.group_order,
        len(classification.special_orbits),
        3,
        (1, 2),
        forms,
    )
    if not result.exact:
        raise ValueError("Tier B local normal-form category failed exact checks")
    return result


__all__ = [
    "LocalInvariantNormalForm",
    "LocalRelation",
    "TierBLocalInvariantNormalForms",
    "tier_b_local_invariant_normal_forms",
]
