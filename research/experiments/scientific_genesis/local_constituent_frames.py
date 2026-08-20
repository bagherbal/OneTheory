"""Materialize exact local Koszul frames for the two Serre constituents.

Owns:
    Affine localization of the I3/I6 Hilbert--Burch presentations, reduction
    to two-generator local complete intersections, and explicit free rank-two
    Serre middle terms with factored syzygies.

Depends on:
    The exact published point schemes and their certified relative support
    projection.

Must not:
    Glue local frames without transition matrices, infer a global bundle from
    local freeness alone, or identify local sections with Higgs cocycles.

Phase 0:
    Research-only local constituent frame construction.
"""

from __future__ import annotations

from dataclasses import dataclass

from onetheory.math.numbers import Eisenstein
from onetheory.math.polynomials import Polynomial
from onetheory.models.heterotic_schoen.visible import PointScheme, point_schemes
from research.experiments.computable_carrier.serre_atlas import (
    AtlasSerreLocal,
    tier_a_atlas_serre_locals,
)

from .relative_constituent_pushdowns import (
    AffinePointAlgebra,
    _divides,
    _variables,
    projected_point_scheme,
)

Monomial = tuple[int, ...]


def _localization_images(pivot: int) -> tuple[object, ...]:
    """Return the coordinate substitution for one standard P2 affine chart."""

    variables = _variables(2)
    images: list[object] = []
    local_index = 0
    for coordinate in range(3):
        if coordinate == pivot:
            images.append(Eisenstein(1))
        else:
            images.append(variables[local_index])
            local_index += 1
    return tuple(images)


def _monomial_polynomial(monomial: Monomial) -> Polynomial:
    """Return a unit-normalized local monomial."""

    return Polynomial.monomial(monomial, scalar_type=Eisenstein)


def _divide_by_monomial(
    polynomial: Polynomial,
    divisor: Monomial,
) -> Polynomial:
    """Divide every term exactly by one known monomial factor."""

    terms = []
    for monomial, coefficient in polynomial.terms:
        if not _divides(divisor, monomial):
            raise ValueError("the declared monomial does not divide the polynomial")
        terms.append(
            (
                tuple(
                    exponent - divisor_exponent
                    for exponent, divisor_exponent in zip(
                        monomial,
                        divisor,
                        strict=True,
                    )
                ),
                coefficient,
            )
        )
    return Polynomial(terms, variable_count=2, scalar_type=Eisenstein)


def _local_generator_coordinates(
    localized: tuple[Polynomial, ...],
    minimal: tuple[Monomial, Monomial],
) -> tuple[tuple[Polynomial, Polynomial], ...]:
    """Express every global ideal generator in the two local lci generators."""

    zero = Polynomial.zero(2, scalar_type=Eisenstein)
    coordinates = []
    for polynomial in localized:
        if polynomial.is_zero():
            coordinates.append((zero, zero))
            continue
        if len(polynomial.terms) != 1:
            raise ValueError("localized published ideal generators must be monomials")
        monomial = polynomial.terms[0][0]
        selected = next(
            (
                index
                for index, generator in enumerate(minimal)
                if _divides(generator, monomial)
            ),
            None,
        )
        if selected is None:
            raise ValueError("a global generator escaped the local lci ideal")
        quotient = _divide_by_monomial(polynomial, minimal[selected])
        coordinates.append(
            (quotient, zero) if selected == 0 else (zero, quotient)
        )
    return tuple(coordinates)


def _local_syzygy_images(
    scheme: PointScheme,
    images: tuple[object, ...],
    coordinates: tuple[tuple[Polynomial, Polynomial], ...],
) -> tuple[tuple[Polynomial, Polynomial], ...]:
    """Map every Hilbert--Burch column into the local two-generator frame."""

    zero = Polynomial.zero(2, scalar_type=Eisenstein)
    localized_matrix = tuple(
        tuple(entry.substitute(images) for entry in row)
        for row in scheme.resolution.matrix
    )
    return tuple(
        tuple(
            sum(
                (
                    coordinates[row][component] * localized_matrix[row][column]
                    for row in range(len(coordinates))
                ),
                zero,
            )
            for component in range(2)
        )
        for column in range(len(localized_matrix[0]))
    )  # type: ignore[return-value]


@dataclass(frozen=True, slots=True)
class LocalKoszulSerreFrame:
    """One explicit free rank-two local Serre extension frame."""

    scheme: str
    surface_factor: int
    pivot: int
    algebra: AffinePointAlgebra
    localized_global_generators: tuple[Polynomial, ...]
    generator_coordinates: tuple[tuple[Polynomial, Polynomial], ...]
    syzygy_images: tuple[tuple[Polynomial, Polynomial], ...]

    @property
    def local_generators(self) -> tuple[Polynomial, Polynomial]:
        """Return the two monomial generators of the local ideal."""

        return tuple(
            _monomial_polynomial(item) for item in self.algebra.generators
        )  # type: ignore[return-value]

    @property
    def serre_injection(self) -> tuple[Polynomial, Polynomial]:
        """Return the canonical Koszul injection into the free middle term."""

        first, second = self.local_generators
        return (-second, first)

    @property
    def global_generators_reconstructed(self) -> bool:
        """Return whether the local frame exactly recovers every global generator."""

        first, second = self.local_generators
        return all(
            first * first_coordinate + second * second_coordinate == generator
            for generator, (first_coordinate, second_coordinate) in zip(
                self.localized_global_generators,
                self.generator_coordinates,
                strict=True,
            )
        )

    @property
    def koszul_composition_zero(self) -> bool:
        """Return the exact quotient-after-injection identity."""

        first, second = self.local_generators
        injection_first, injection_second = self.serre_injection
        return (first * injection_first + second * injection_second).is_zero()

    @property
    def syzygies_factor_through_koszul(self) -> bool:
        """Return whether every global syzygy is a local Koszul multiple."""

        first, second = self.local_generators
        for image_first, image_second in self.syzygy_images:
            if image_first.is_zero() and image_second.is_zero():
                continue
            multiplier_from_first = -_divide_by_monomial(
                image_first,
                self.algebra.generators[1],
            )
            multiplier_from_second = _divide_by_monomial(
                image_second,
                self.algebra.generators[0],
            )
            if multiplier_from_first != multiplier_from_second:
                return False
            if (
                image_first != -second * multiplier_from_first
                or image_second != first * multiplier_from_first
            ):
                return False
        return True

    @property
    def exact(self) -> bool:
        """Return every local frame and mapping-cone identity."""

        return (
            self.algebra.is_local_complete_intersection
            and self.global_generators_reconstructed
            and self.koszul_composition_zero
            and self.syzygies_factor_through_koszul
        )


@dataclass(frozen=True, slots=True)
class BoundPuncturedSerreFrame:
    """A published local frame bound to its existing punctured atlas cocycle."""

    frame: LocalKoszulSerreFrame
    atlas: AtlasSerreLocal

    @property
    def multiplicity(self) -> int:
        """Return the nilpotent-direction multiplicity of the local scheme."""

        return max(sum(generator) for generator in self.frame.algebra.generators)

    @property
    def exact(self) -> bool:
        """Return every frame, incidence, and punctured-cocycle gate."""

        return (
            self.frame.exact
            and self.atlas.scheme == self.frame.scheme
            and self.atlas.local_model.multiplicity == self.multiplicity
            and self.atlas.local_model.locally_free
            and self.atlas.local_cocycle_exact
            and self.atlas.local_cocycle_nonboundary
            and self.atlas.cocycle_monomial_exponents == (-1, -self.multiplicity)
            and self.atlas.hypersurface_incidence
            and self.atlas.fiber_derivative_nonzero
        )


def _local_frames(
    scheme: PointScheme,
    surface_factor: int,
) -> tuple[LocalKoszulSerreFrame, ...]:
    """Construct all three coordinate-point frames of one constituent."""

    projection = projected_point_scheme(scheme, surface_factor)
    frames = []
    for algebra in projection.local_algebras:
        if len(algebra.generators) != 2:
            raise ValueError("local Serre frames require two lci generators")
        images = _localization_images(algebra.pivot)
        localized = tuple(
            generator.substitute(images) for generator in scheme.ideal_generators
        )
        minimal = (algebra.generators[0], algebra.generators[1])
        coordinates = _local_generator_coordinates(localized, minimal)
        frame = LocalKoszulSerreFrame(
            scheme.name,
            surface_factor,
            algebra.pivot,
            algebra,
            localized,
            coordinates,
            _local_syzygy_images(scheme, images, coordinates),
        )
        if not frame.exact:
            raise ValueError("a local Koszul Serre frame failed exact reconstruction")
        frames.append(frame)
    return tuple(frames)


def published_local_constituent_frames(
) -> tuple[tuple[LocalKoszulSerreFrame, ...], ...]:
    """Return exact local frames for W1 and W2 in factor order."""

    first, second = point_schemes()
    return (_local_frames(first, 1), _local_frames(second, 2))


def published_bound_punctured_frames() -> tuple[BoundPuncturedSerreFrame, ...]:
    """Bind all six published lci frames to the reusable punctured atlas data."""

    frames = {
        (frame.scheme, frame.pivot): frame
        for group in published_local_constituent_frames()
        for frame in group
    }
    point_pivots = {"p_a": 0, "p_b": 1, "p_c": 2}
    results = tuple(
        BoundPuncturedSerreFrame(
            frames[(atlas.scheme, point_pivots[atlas.point])],
            atlas,
        )
        for atlas in tier_a_atlas_serre_locals()
    )
    if not all(result.exact for result in results):
        raise ValueError("a published local frame failed punctured-atlas binding")
    return results


__all__ = [
    "BoundPuncturedSerreFrame",
    "LocalKoszulSerreFrame",
    "published_bound_punctured_frames",
    "published_local_constituent_frames",
]
