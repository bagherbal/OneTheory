"""Reconstruct source-labelled relative pushdowns of two Serre constituents.

Owns:
    Exact projection of the I3/I6 schemes to the common projective line,
    the duality-forced W1 contraction, the W2 elementary transformation,
    and finite checks on the source-assigned derived pushdown objects.

Depends on:
    Frozen cubic pencils, exact monomial point schemes, selected mixed
    constituent Cech classes, local dualizing units, and linearisations.

Must not:
    Present assigned line degrees or characters as independently derived,
    identify the current ambient Cech cone with a constituent before
    comparison, or infer physical Higgs states from relative sheaf data alone.

Phase 0:
    Research-only source-bound relative-pushdown reconstruction.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from itertools import product
from pathlib import Path
from typing import cast

from onetheory.math.numbers import OMEGA, OMEGA2, Eisenstein
from onetheory.math.polynomials import Polynomial
from onetheory.models.heterotic_schoen.geometry import schoen_geometry
from onetheory.models.heterotic_schoen.visible import PointScheme, point_schemes
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.computable_carrier.schoen_sparse_actions import (
    schoen_sparse_deck_actions,
)

from .published_constituent_full_cech import published_constituent_full_cech

Monomial = tuple[int, ...]
Character = tuple[Eisenstein, Eisenstein]

ONE_CHARACTER: Character = (Eisenstein(1), Eisenstein(1))
CHI1: Character = (OMEGA, Eisenstein(1))
CHI1_SQUARED: Character = (OMEGA2, Eisenstein(1))
CHI2: Character = (Eisenstein(1), OMEGA)
CHI2_SQUARED: Character = (Eisenstein(1), OMEGA2)

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/relative_constituent_pushdowns.json"


def _variables(count: int) -> tuple[Polynomial, ...]:
    """Return exact coordinate variables in one Eisenstein polynomial ring."""

    return tuple(
        Polynomial.monomial(
            tuple(int(index == position) for index in range(count)),
            scalar_type=Eisenstein,
        )
        for position in range(count)
    )


def _constant_value(polynomial: Polynomial) -> Eisenstein:
    """Extract an exact constant after a complete substitution."""

    if polynomial.variable_count != 0:
        raise ValueError("a completely evaluated polynomial must have no variables")
    return cast(Eisenstein, polynomial.coefficient(()))


def _normalize_linear_form(polynomial: Polynomial) -> Polynomial:
    """Normalize a nonzero homogeneous linear form by its leading coefficient."""

    if polynomial.variable_count != 2 or polynomial.degree != 1:
        raise ValueError("base support equations must be binary linear forms")
    return polynomial.scale(Eisenstein(1) / cast(Eisenstein, polynomial.terms[0][1]))


def _divides(left: Monomial, right: Monomial) -> bool:
    """Return whether one monomial divides another."""

    return all(first <= second for first, second in zip(left, right, strict=True))


def _binary_transform(
    polynomial: Polynomial,
    images: tuple[tuple[Eisenstein, Monomial], ...],
) -> Polynomial:
    """Apply one exact monomial deck action to a binary form."""

    return polynomial.substitute(
        tuple(
            Polynomial.monomial(exponents, scalar, scalar_type=Eisenstein)
            for scalar, exponents in images
        )
    )


def _minimal_monomials(generators: tuple[Polynomial, ...]) -> tuple[Monomial, ...]:
    """Return the divisibility-minimal generators of a monomial ideal."""

    monomials = []
    for generator in generators:
        if generator.is_zero():
            continue
        if len(generator.terms) != 1:
            raise ValueError("the local point ideals must remain monomial")
        monomials.append(generator.terms[0][0])
    unique = tuple(sorted(set(monomials)))
    return tuple(
        monomial
        for monomial in unique
        if not any(
            candidate != monomial and _divides(candidate, monomial)
            for candidate in unique
        )
    )


def _standard_monomials(generators: tuple[Monomial, ...]) -> tuple[Monomial, ...]:
    """Enumerate the finite standard basis of a zero-dimensional monomial ideal."""

    if not generators:
        raise ValueError("a local point ideal needs monomial generators")
    variable_count = len(generators[0])
    bounds = []
    for variable in range(variable_count):
        pure_powers = [
            monomial[variable]
            for monomial in generators
            if monomial[variable] > 0
            and all(
                exponent == 0
                for index, exponent in enumerate(monomial)
                if index != variable
            )
        ]
        if not pure_powers:
            raise ValueError("the local monomial ideal is not zero-dimensional")
        bounds.append(min(pure_powers))
    return tuple(
        monomial
        for monomial in product(*(range(bound) for bound in bounds))
        if not any(_divides(generator, monomial) for generator in generators)
    )


@dataclass(frozen=True, slots=True)
class AffinePointAlgebra:
    """One exact affine local algebra of a coordinate-supported point scheme."""

    pivot: int
    generators: tuple[Monomial, ...]
    standard_monomials: tuple[Monomial, ...]
    projection_constant_to_first_order: bool

    @property
    def length(self) -> int:
        """Return the exact local scheme length."""

        return len(self.standard_monomials)

    @property
    def is_local_complete_intersection(self) -> bool:
        """Return whether two pure powers generate the local codimension-two ideal."""

        return len(self.generators) == 2 and all(
            sum(exponent > 0 for exponent in generator) == 1
            for generator in self.generators
        )


@dataclass(frozen=True, slots=True)
class ProjectedPointScheme:
    """Exact finite projection data for one I3 or I6 scheme."""

    name: str
    surface_factor: int
    support_forms: tuple[Polynomial, ...]
    support_equation: Polynomial
    local_algebras: tuple[AffinePointAlgebra, ...]

    @property
    def support_is_reduced(self) -> bool:
        """Return whether the three base linear forms are pairwise distinct."""

        coefficient_pairs = tuple(
            (
                cast(Eisenstein, form.coefficient((1, 0))),
                cast(Eisenstein, form.coefficient((0, 1))),
            )
            for form in self.support_forms
        )
        return all(
            left[0] * right[1] - left[1] * right[0] != Eisenstein(0)
            for index, left in enumerate(coefficient_pairs)
            for right in coefficient_pairs[index + 1 :]
        )

    @property
    def scheme_length(self) -> int:
        """Return the sum of the exact local lengths."""

        return sum(algebra.length for algebra in self.local_algebras)

    @property
    def support_deck_invariant(self) -> bool:
        """Return whether both exact deck generators preserve the support divisor."""

        return all(
            _binary_transform(self.support_equation, action.p_images)
            == self.support_equation
            for action in schoen_sparse_deck_actions()
        )

    @property
    def exact(self) -> bool:
        """Return all finite projection and local-algebra gates."""

        return (
            len(self.support_forms) == 3
            and self.support_equation.degree == 3
            and self.support_is_reduced
            and self.support_deck_invariant
            and all(item.is_local_complete_intersection for item in self.local_algebras)
            and all(
                item.projection_constant_to_first_order
                for item in self.local_algebras
            )
        )

    def as_record(self) -> dict[str, object]:
        """Serialize exact support and affine-local projection data."""

        def polynomial_record(polynomial: Polynomial) -> list[dict[str, object]]:
            return [
                {"monomial": list(monomial), "coefficient": str(coefficient)}
                for monomial, coefficient in polynomial.terms
            ]

        return {
            "scheme": self.name,
            "surface_factor": self.surface_factor,
            "support_forms": [polynomial_record(form) for form in self.support_forms],
            "support_equation": polynomial_record(self.support_equation),
            "support_is_reduced": self.support_is_reduced,
            "support_deck_invariant": self.support_deck_invariant,
            "scheme_length": self.scheme_length,
            "local_algebras": [
                {
                    "pivot": algebra.pivot,
                    "generators": [list(item) for item in algebra.generators],
                    "standard_monomials": [
                        list(item) for item in algebra.standard_monomials
                    ],
                    "length": algebra.length,
                    "local_complete_intersection": (
                        algebra.is_local_complete_intersection
                    ),
                    "projection_constant_to_first_order": (
                        algebra.projection_constant_to_first_order
                    ),
                }
                for algebra in self.local_algebras
            ],
            "exact": self.exact,
        }


def _affine_point_algebra(
    scheme: PointScheme,
    pivot: int,
    surface_factor: int,
) -> AffinePointAlgebra:
    """Restrict one homogeneous monomial ideal to a coordinate affine chart."""

    local_variables = _variables(2)
    images: list[object] = []
    local_index = 0
    for coordinate in range(3):
        if coordinate == pivot:
            images.append(Eisenstein(1))
        else:
            images.append(local_variables[local_index])
            local_index += 1
    localized = tuple(
        generator.substitute(images) for generator in scheme.ideal_generators
    )
    minimal = _minimal_monomials(localized)
    standard = _standard_monomials(minimal)

    cox = schoen_geometry().cover.cox
    point = tuple(int(index == pivot) for index in range(3))
    tangent_indices = tuple(index for index in range(3) if index != pivot)
    projection_constant = all(
        _constant_value(polynomial.derivative(index).substitute(point)).is_zero()
        for polynomial in (cox.cubic_f, cox.cubic_g)
        for index in tangent_indices
    )
    if surface_factor not in (1, 2):
        raise ValueError("dP9 factors are indexed by one and two")
    return AffinePointAlgebra(pivot, minimal, standard, projection_constant)


def projected_point_scheme(
    scheme: PointScheme,
    surface_factor: int,
) -> ProjectedPointScheme:
    """Project a coordinate-supported scheme through its exact cubic pencil."""

    p0, p1 = _variables(2)
    cox = schoen_geometry().cover.cox
    points = tuple(
        tuple(int(index == pivot) for index in range(3))
        for pivot in range(3)
    )
    forms = []
    for point in points:
        f_value = _constant_value(cox.cubic_f.substitute(point))
        g_value = _constant_value(cox.cubic_g.substitute(point))
        equation = (
            p0.scale(f_value) + p1.scale(g_value)
            if surface_factor == 1
            else p0.scale(g_value) + p1.scale(2 * f_value)
        )
        forms.append(_normalize_linear_form(equation))
    support_equation = Polynomial.one(2, scalar_type=Eisenstein)
    for form in forms:
        support_equation *= form
    result = ProjectedPointScheme(
        scheme.name,
        surface_factor,
        tuple(forms),
        support_equation,
        tuple(
            _affine_point_algebra(scheme, pivot, surface_factor)
            for pivot in range(3)
        ),
    )
    if not result.exact or result.scheme_length != int(scheme.length):
        raise ValueError("the finite point scheme failed exact relative projection")
    return result


@dataclass(frozen=True, slots=True)
class EquivariantP1Line:
    """One exactly graded and character-labelled line bundle on P1."""

    label: str
    degree: int
    character: Character

    def cohomology_dimension(self, degree: int, twist: int = 0) -> int:
        """Return exact line-bundle cohomology after an integral twist."""

        total_degree = self.degree + twist
        if degree == 0:
            return max(total_degree + 1, 0)
        if degree == 1:
            return max(-total_degree - 1, 0)
        raise ValueError("P1 line bundles have cohomology only in degrees zero and one")


@dataclass(frozen=True, slots=True)
class P1LineMap:
    """One homogeneous exact map between explicitly normalized P1 lines."""

    source: EquivariantP1Line
    target: EquivariantP1Line
    polynomial: Polynomial
    normalization: str

    def __post_init__(self) -> None:
        if self.polynomial.variable_count != 2 or self.polynomial.is_zero():
            raise ValueError("a P1 line map requires a nonzero binary form")
        if self.source.degree + self.polynomial.degree != self.target.degree:
            raise ValueError("the binary-form degree does not match the line map")
        if not self.normalization.strip():
            raise ValueError("line-map normalization must be explicit")

    @property
    def is_isomorphism(self) -> bool:
        """Return whether this map is multiplication by a nonzero constant."""

        return self.polynomial.degree == 0


@dataclass(frozen=True, slots=True)
class ElementaryTransformation:
    """The exact line extension across a reduced effective divisor on P1."""

    line_map: P1LineMap
    support: ProjectedPointScheme
    local_extension_units: tuple[bool, ...]

    @property
    def exact(self) -> bool:
        """Return whether the cokernel is one unit skyscraper at each support point."""

        return (
            self.support.support_is_reduced
            and self.line_map.polynomial == self.support.support_equation
            and self.line_map.target.degree - self.line_map.source.degree == 3
            and self.line_map.source.character == self.line_map.target.character
            and self.local_extension_units == (True, True, True)
        )


@dataclass(frozen=True, slots=True)
class RelativeConstituentPushdown:
    """A source-labelled derived pushdown with exact local consistency gates."""

    name: str
    support: ProjectedPointScheme
    direct_terms: tuple[EquivariantP1Line, ...]
    higher_terms: tuple[EquivariantP1Line, ...]
    connecting_map: P1LineMap | None
    connecting_zero_by_character: bool
    elementary_transformation: ElementaryTransformation | None
    selected_mixed_cocycle: bool
    local_extension_units: tuple[bool, ...]
    relative_duality_used: bool

    @property
    def quasi_isomorphism_exact(self) -> bool:
        """Check reductions conditional on the assigned line data and map."""

        connecting_exact = (
            self.connecting_map is not None
            and self.connecting_map.is_isomorphism
            and self.relative_duality_used
        ) or (
            self.connecting_map is None
            and self.connecting_zero_by_character
        )
        elementary_exact = (
            self.elementary_transformation is None
            or self.elementary_transformation.exact
        )
        return (
            self.support.exact
            and self.selected_mixed_cocycle
            and self.local_extension_units == (True, True, True)
            and connecting_exact
            and elementary_exact
        )

    def hypercohomology_dimensions(self, twist: int) -> tuple[int, int, int]:
        """Return exact total cohomology of the derived pushdown after twisting."""

        return (
            sum(term.cohomology_dimension(0, twist) for term in self.direct_terms),
            sum(term.cohomology_dimension(1, twist) for term in self.direct_terms)
            + sum(term.cohomology_dimension(0, twist) for term in self.higher_terms),
            sum(term.cohomology_dimension(1, twist) for term in self.higher_terms),
        )

    def signature(
        self,
    ) -> tuple[
        tuple[tuple[int, Character], ...],
        tuple[tuple[int, Character], ...],
    ]:
        """Return the exact line-degree and character signature."""

        return (
            tuple((term.degree, term.character) for term in self.direct_terms),
            tuple((term.degree, term.character) for term in self.higher_terms),
        )

    def as_record(self) -> dict[str, object]:
        """Serialize the reduction without importing its published target formula."""

        def line_record(line: EquivariantP1Line) -> dict[str, object]:
            return {
                "label": line.label,
                "degree": line.degree,
                "character": [str(value) for value in line.character],
            }

        connecting = None
        if self.connecting_map is not None:
            connecting = {
                "source": line_record(self.connecting_map.source),
                "target": line_record(self.connecting_map.target),
                "isomorphism": self.connecting_map.is_isomorphism,
                "normalization": self.connecting_map.normalization,
            }
        return {
            "name": self.name,
            "support": self.support.as_record(),
            "direct_terms": [line_record(item) for item in self.direct_terms],
            "higher_terms": [line_record(item) for item in self.higher_terms],
            "connecting_map": connecting,
            "connecting_zero_by_character": self.connecting_zero_by_character,
            "elementary_transformation_exact": (
                self.elementary_transformation.exact
                if self.elementary_transformation is not None
                else None
            ),
            "selected_mixed_cocycle": self.selected_mixed_cocycle,
            "local_extension_units": list(self.local_extension_units),
            "relative_duality_used": self.relative_duality_used,
            "twist_profiles_minus_two_through_two": [
                [twist, list(self.hypercohomology_dimensions(twist))]
                for twist in range(-2, 3)
            ],
            "quasi_isomorphism_exact": self.quasi_isomorphism_exact,
            "quasi_isomorphism_conditional_on_assigned_lines": True,
        }


def _selected_mixed_unit_data(
) -> tuple[tuple[bool, tuple[bool, ...]], tuple[bool, tuple[bool, ...]]]:
    """Bind each selected full Cech ray to its three evaluated local units."""

    from .published_constituent_local_units import (  # noqa: PLC0415
        published_constituent_local_units,
    )

    full = published_constituent_full_cech()
    units = published_constituent_local_units()
    records = []
    for result in full:
        scheme = result.alignment.action.derived.extension.scheme.name
        selected = tuple(
            sorted(
                (unit for unit in units if unit.constituent == scheme),
                key=lambda unit: unit.frame.pivot,
            )
        )
        if len(selected) != 3:
            raise ValueError("each selected constituent requires three local units")
        records.append(
            (
                result.exact
                and result.alignment.has_syzygy_koszul_component
                and result.alignment.old_trivial_character_is_different,
                tuple(unit.unit_in_local_dualizing_algebra for unit in selected),
            )
        )
    return cast(
        tuple[tuple[bool, tuple[bool, ...]], tuple[bool, tuple[bool, ...]]],
        tuple(records),
    )


def relative_constituent_pushdowns(
) -> tuple[RelativeConstituentPushdown, RelativeConstituentPushdown]:
    """Check W1 and W2 reductions using source-assigned line signatures."""

    scheme_one, scheme_two = point_schemes()
    support_one = projected_point_scheme(scheme_one, 1)
    support_two = projected_point_scheme(scheme_two, 2)
    (selected_one, units_one), (selected_two, units_two) = _selected_mixed_unit_data()

    w1_cancel_source = EquivariantP1Line(
        "chi1^2 O(-2) quotient image",
        -2,
        CHI1_SQUARED,
    )
    w1_cancel_target = EquivariantP1Line(
        "chi1^2 O(-2) line higher image",
        -2,
        CHI1_SQUARED,
    )
    w1_connecting = P1LineMap(
        w1_cancel_source,
        w1_cancel_target,
        Polynomial.one(2, scalar_type=Eisenstein),
        (
            "relative duality forces the unique nonzero scalar map; source and "
            "target bases normalize it to one"
        ),
    )
    w1 = RelativeConstituentPushdown(
        "W1",
        support_one,
        (EquivariantP1Line("chi1 O(-1)", -1, CHI1),),
        (EquivariantP1Line("O", 0, ONE_CHARACTER),),
        w1_connecting,
        False,
        None,
        selected_one,
        units_one,
        selected_one
        and all(units_one)
        and w1_connecting.source.degree == w1_connecting.target.degree,
    )

    w2_elementary = ElementaryTransformation(
        P1LineMap(
            EquivariantP1Line("chi2^2 O(-2)", -2, CHI2_SQUARED),
            EquivariantP1Line("chi2^2 O(1)", 1, CHI2_SQUARED),
            support_two.support_equation,
            "the monic product of the three exact support equations",
        ),
        support_two,
        units_two,
    )
    w2 = RelativeConstituentPushdown(
        "W2",
        support_two,
        (
            EquivariantP1Line("chi2^2 O(-1)", -1, CHI2_SQUARED),
            EquivariantP1Line("chi2 O(-2)", -2, CHI2),
        ),
        (
            w2_elementary.line_map.target,
            EquivariantP1Line("chi2 O", 0, CHI2),
        ),
        None,
        CHI2 != CHI2_SQUARED,
        w2_elementary,
        selected_two,
        units_two,
        False,
    )
    if not w1.quasi_isomorphism_exact or not w2.quasi_isomorphism_exact:
        raise ValueError("a relative constituent pushdown gate failed")
    return w1, w2


def relative_tensor_dimensions(
    first: RelativeConstituentPushdown,
    second: RelativeConstituentPushdown,
) -> tuple[int, int, int, int]:
    """Compute total P1 cohomology of two split derived pushdown objects."""

    first_terms = tuple((0, term) for term in first.direct_terms) + tuple(
        (1, term) for term in first.higher_terms
    )
    second_terms = tuple((0, term) for term in second.direct_terms) + tuple(
        (1, term) for term in second.higher_terms
    )
    return cast(
        tuple[int, int, int, int],
        tuple(
            sum(
                max(first_line.degree + second_line.degree + 1, 0)
                if total == first_degree + second_degree
                else max(-first_line.degree - second_line.degree - 1, 0)
                if total == first_degree + second_degree + 1
                else 0
                for (first_degree, first_line), (second_degree, second_line) in product(
                    first_terms,
                    second_terms,
                )
            )
            for total in range(4)
        ),
    )


def write_relative_constituent_pushdowns(path: Path = OUTPUT) -> dict[str, object]:
    """Write the source-bound relative-pushdown consistency record."""

    from research.experiments.computable_carrier.pushdown import (  # noqa: PLC0415
        tier_a_pushdown_constraints,
    )

    results = relative_constituent_pushdowns()
    source = tier_a_pushdown_constraints()
    source_signatures = tuple(
        (
            tuple((term.degree, term.character) for term in item.direct_terms),
            tuple((term.degree, term.character) for term in item.higher_terms),
        )
        for item in source
    )
    payload: dict[str, object] = {
        "schema": "relative-constituent-pushdowns-v3",
        "selected_source_inputs": [
            "hep-th/0602073 source labels eq:W1def and eq:W2def",
            "hep-th/0602073 source section sec:CB: W1/W2 local freeness",
            "hep-th/0602073 relative-duality argument after source label eq:W1les",
        ],
        "comparison_targets": [
            "hep-th/0602073 source label eq:W1pushdown",
            "hep-th/0602073 source label eq:W2pushdown",
        ],
        "constituents": [item.as_record() for item in results],
        "all_local_reductions_exact_given_assigned_lines": all(
            item.quasi_isomorphism_exact for item in results
        ),
        "selected_mixed_constituent_cocycles_used": True,
        "retired_maximal_minor_cones_used": False,
        "source_line_degrees_and_characters_used_as_input": True,
        "independent_equivariant_pushdown_derived": False,
        "atlas_to_relative_equivariant_chain_map_constructed": False,
        "source_signature_comparison_is_independent": False,
        "derived_signatures_match_source": (
            tuple(item.signature() for item in results) == source_signatures
        ),
        "derived_tensor_dimensions": list(relative_tensor_dimensions(*results)),
        "full_schoen_cech_representatives_constructed": False,
        "next_required_object": (
            "an atlas-to-relative equivariant chain map deriving both line "
            "signatures before lifting Higgs classes to the full Schoen complex"
        ),
    }
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
    """Regenerate the exact relative constituent pushdown artifact."""

    payload = write_relative_constituent_pushdowns()
    print(f"artifact_digest: {payload['artifact_digest']}")
    print(f"derived_tensor_dimensions: {payload['derived_tensor_dimensions']}")
    print(f"next_required_object: {payload['next_required_object']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "AffinePointAlgebra",
    "ElementaryTransformation",
    "EquivariantP1Line",
    "P1LineMap",
    "ProjectedPointScheme",
    "RelativeConstituentPushdown",
    "OUTPUT",
    "projected_point_scheme",
    "relative_constituent_pushdowns",
    "relative_tensor_dimensions",
    "write_relative_constituent_pushdowns",
]
