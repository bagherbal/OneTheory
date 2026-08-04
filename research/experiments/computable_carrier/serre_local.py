"""Construct exact local Serre pushout presentations.

Owns:
    The local ideals ``(x,y)`` and ``(x,y^2)``, their syzygy relations,
    unit and nilpotent extension classes, pushout presentations, and exact
    Fitting-ideal tests for local freeness.

Depends on:
    Generic exact polynomial matrices and determinantal ideals, with no
    assumptions about a global dP9 atlas or a quotient bundle.

Must not:
    Promote a local pushout to a global Serre cocycle, infer transition
    functions between dP9 charts, reuse a reference extension class, or claim
    equivariant descent from local freeness.

Phase 0:
    Local Serre models are executable and exact; global patching, linearization,
    and identification with the Tier A complexes remain unresolved.
"""

from __future__ import annotations

from dataclasses import dataclass

from onetheory.math.polynomials import Polynomial, PolynomialIdeal, PolynomialMatrix


def _variables() -> tuple[Polynomial, Polynomial]:
    """Return exact local coordinates ``x`` and ``y``."""

    return (
        Polynomial.monomial((1, 0)),
        Polynomial.monomial((0, 1)),
    )


def _class_polynomial(label: str, y: Polynomial) -> Polynomial:
    """Return one declared local Ext direction without a fallback."""

    if label == "unit":
        return Polynomial.one(2)
    if label == "nilpotent":
        return y
    raise ValueError("local Serre classes are unit or nilpotent")


@dataclass(frozen=True, slots=True)
class LocalSerreModel:
    """One local Serre pushout with an exact freeness certificate."""

    scheme: str
    multiplicity: int
    class_label: str
    local_coordinates: tuple[str, str]
    ideal_generators: tuple[Polynomial, Polynomial]
    syzygy: tuple[Polynomial, Polynomial]
    extension_class: Polynomial
    pushout_relation: PolynomialMatrix
    quotient_map: PolynomialMatrix
    fitting_ideal: PolynomialIdeal
    relation_composes_to_zero: bool
    locally_free: bool

    def __post_init__(self) -> None:
        if self.scheme not in {"I3", "I6"}:
            raise ValueError("local Serre models require I3 or I6")
        expected_multiplicity = 1 if self.scheme == "I3" else 2
        if self.multiplicity != expected_multiplicity:
            raise ValueError("the local multiplicity does not match the scheme")
        if self.pushout_relation.shape != (1, 3) or self.quotient_map.shape != (1, 3):
            raise ValueError("local Serre presentations require one relation and quotient row")

    def as_record(self) -> dict[str, object]:
        """Serialize the local presentation and its exact status boundary."""

        def polynomial_record(polynomial: Polynomial) -> dict[str, object]:
            return {
                "terms": [
                    {
                        "exponents": list(exponents),
                        "coefficient": str(coefficient),
                    }
                    for exponents, coefficient in polynomial.terms
                ]
            }

        return {
            "scheme": self.scheme,
            "multiplicity": self.multiplicity,
            "class_label": self.class_label,
            "local_coordinates": list(self.local_coordinates),
            "ideal_generators": [polynomial_record(item) for item in self.ideal_generators],
            "syzygy": [polynomial_record(item) for item in self.syzygy],
            "extension_class": polynomial_record(self.extension_class),
            "pushout_relation": [
                [polynomial_record(item) for item in row]
                for row in self.pushout_relation.rows
            ],
            "quotient_map": [
                [polynomial_record(item) for item in row]
                for row in self.quotient_map.rows
            ],
            "fitting_ideal": self.fitting_ideal.as_record(),
            "relation_composes_to_zero": self.relation_composes_to_zero,
            "locally_free": self.locally_free,
            "status": "local Serre presentation only; global patching remains pending",
        }


def local_serre_model(scheme: str, class_label: str = "unit") -> LocalSerreModel:
    """Construct one exact local pushout for I3 or I6."""

    x, y = _variables()
    multiplicity = 1 if scheme == "I3" else 2 if scheme == "I6" else -1
    if multiplicity < 0:
        raise ValueError("local Serre models require I3 or I6")
    y_power = y**multiplicity
    ideal_generators = (x, y_power)
    syzygy = (-y_power, x)
    extension_class = _class_polynomial(class_label, y)
    pushout_relation = PolynomialMatrix(((syzygy[0], syzygy[1], -extension_class),))
    quotient_map = PolynomialMatrix(((x, y_power, Polynomial.zero(2)),))
    relation_composes_to_zero = (
        pushout_relation.compose(
            PolynomialMatrix(((x,), (y_power,), (Polynomial.zero(2),)))
        ).is_zero()
    )
    fitting_generators = (syzygy[0], syzygy[1], extension_class)
    fitting_ideal = PolynomialIdeal(fitting_generators)
    locally_free = any(
        polynomial == Polynomial.one(2)
        or polynomial == Polynomial.one(2).scale(-1)
        for polynomial in fitting_ideal.generators
    )
    return LocalSerreModel(
        scheme,
        multiplicity,
        class_label,
        ("x", "y"),
        ideal_generators,
        syzygy,
        extension_class,
        pushout_relation,
        quotient_map,
        fitting_ideal,
        relation_composes_to_zero,
        locally_free,
    )


def tier_a_local_serre_models() -> tuple[LocalSerreModel, ...]:
    """Return the unit local classes selected by the Tier A local algebra."""

    return (local_serre_model("I3"), local_serre_model("I6"))


__all__ = ["LocalSerreModel", "local_serre_model", "tier_a_local_serre_models"]
