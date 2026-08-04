"""Freeze the target and finite bounds for Computable Carrier Genesis.

Owns:
    Immutable selection constraints, forbidden-input declarations, ordered
    Tier A/B/C search bounds, and canonical serialization for the new carrier.

Depends on:
    Python standard-library dataclasses and exact scalar-free metadata only.

Must not:
    Select a bundle, predict observables, import the published bundle as an
    answer, or encode measured masses, mixing, CP data, or fitted couplings.

Phase 0:
    The construction contract is executable; no candidate is promoted yet.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TierBound:
    """An explicit finite bound for one ordered construction tier."""

    name: str
    maximum_point_length: int
    twist_radius: int
    maximum_extension_dimension: int
    maximum_complex_rank: int
    permitted_constructions: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.name.strip() or not self.permitted_constructions:
            raise ValueError("a tier bound requires a name and construction category")
        if any(
            isinstance(value, bool) or not isinstance(value, int) or value < 0
            for value in (
                self.maximum_point_length,
                self.twist_radius,
                self.maximum_extension_dimension,
                self.maximum_complex_rank,
            )
        ):
            raise ValueError("tier bounds must be nonnegative integers")

    def as_record(self) -> dict[str, object]:
        """Return deterministic metadata for the declared finite bound."""

        return {
            "name": self.name,
            "maximum_point_length": self.maximum_point_length,
            "twist_radius": self.twist_radius,
            "maximum_extension_dimension": self.maximum_extension_dimension,
            "maximum_complex_rank": self.maximum_complex_rank,
            "permitted_constructions": list(self.permitted_constructions),
        }


@dataclass(frozen=True, slots=True)
class ComputableCarrierSpecification:
    """The immutable target contract for a new Schoen quotient carrier."""

    identifier: str
    reference_carrier_identifier: str
    geometry_identifier: str
    quotient_group: str
    quotient_order: int
    rank: int
    first_chern_class: tuple[int, ...]
    structure_group: str
    honest_equivariant_descent_required: bool
    slope_stability_required: bool
    quotient_chiral_index: int
    observable_commutant: str
    wilson_line_route: str
    chiral_families: int
    right_handed_neutrinos: int
    higgs_pairs: int
    conjugate_families: int
    exotic_massless_character_blocks: int
    anomaly_budget_required: bool
    complete_chain_computability_required: bool
    selection_constraints_are_not_predictions: bool
    forbidden_inputs: tuple[str, ...]
    tiers: tuple[TierBound, ...]

    def __post_init__(self) -> None:
        if not self.identifier.strip() or not self.reference_carrier_identifier.strip():
            raise ValueError("a computable carrier needs distinct named identities")
        if self.identifier == self.reference_carrier_identifier:
            raise ValueError("the new carrier cannot be identified with its reference")
        if self.geometry_identifier != "Schoen quotient":
            raise ValueError("this epic is fixed to the Schoen quotient")
        if self.quotient_group != "Z3 x Z3" or self.quotient_order != 9:
            raise ValueError("the target quotient must be the order-nine Schoen quotient")
        if self.rank != 4 or self.first_chern_class != (0, 0, 0):
            raise ValueError("the target is a rank-four c1-zero bundle")
        if self.structure_group != "SU(4)":
            raise ValueError("the target structure group must be SU(4)")
        if not self.honest_equivariant_descent_required or not self.slope_stability_required:
            raise ValueError("descent and slope stability are mandatory target gates")
        if self.quotient_chiral_index != 3 or self.observable_commutant != "Spin(10)":
            raise ValueError("the target index and observable commutant are fixed")
        if self.chiral_families != 3 or self.right_handed_neutrinos != 3:
            raise ValueError("the target has exactly three families and neutrinos")
        if self.higgs_pairs != 1 or self.conjugate_families != 0:
            raise ValueError("the target has one Higgs pair and no conjugate families")
        if self.exotic_massless_character_blocks != 0:
            raise ValueError("the target forbids exotic massless character blocks")
        if not self.anomaly_budget_required or not self.complete_chain_computability_required:
            raise ValueError("anomaly and chain-computability gates are mandatory")
        if not self.selection_constraints_are_not_predictions:
            raise ValueError("selection constraints must not be treated as predictions")
        if len(self.forbidden_inputs) < 4 or len(self.tiers) != 3:
            raise ValueError("the contract needs forbidden inputs and three ordered tiers")
        if tuple(tier.name for tier in self.tiers) != ("Tier A", "Tier B", "Tier C"):
            raise ValueError("tiers must be ordered A, B, C")

    def as_record(self) -> dict[str, object]:
        """Return a canonical JSON-ready contract record."""

        return {
            "identifier": self.identifier,
            "reference_carrier_identifier": self.reference_carrier_identifier,
            "geometry_identifier": self.geometry_identifier,
            "quotient_group": self.quotient_group,
            "quotient_order": self.quotient_order,
            "rank": self.rank,
            "first_chern_class": list(self.first_chern_class),
            "structure_group": self.structure_group,
            "honest_equivariant_descent_required": self.honest_equivariant_descent_required,
            "slope_stability_required": self.slope_stability_required,
            "quotient_chiral_index": self.quotient_chiral_index,
            "observable_commutant": self.observable_commutant,
            "wilson_line_route": self.wilson_line_route,
            "chiral_families": self.chiral_families,
            "right_handed_neutrinos": self.right_handed_neutrinos,
            "higgs_pairs": self.higgs_pairs,
            "conjugate_families": self.conjugate_families,
            "exotic_massless_character_blocks": self.exotic_massless_character_blocks,
            "anomaly_budget_required": self.anomaly_budget_required,
            "complete_chain_computability_required": self.complete_chain_computability_required,
            "selection_constraints_are_not_predictions": (
                self.selection_constraints_are_not_predictions
            ),
            "forbidden_inputs": list(self.forbidden_inputs),
            "tiers": [tier.as_record() for tier in self.tiers],
        }


def computable_carrier_specification() -> ComputableCarrierSpecification:
    """Construct the frozen new-carrier contract without selecting a candidate."""

    return ComputableCarrierSpecification(
        identifier="OneTheory computable one-Higgs Schoen carrier",
        reference_carrier_identifier="published one-Higgs heterotic Schoen carrier",
        geometry_identifier="Schoen quotient",
        quotient_group="Z3 x Z3",
        quotient_order=9,
        rank=4,
        first_chern_class=(0, 0, 0),
        structure_group="SU(4)",
        honest_equivariant_descent_required=True,
        slope_stability_required=True,
        quotient_chiral_index=3,
        observable_commutant="Spin(10)",
        wilson_line_route="Spin(10) -> SU(3) x SU(2) x U(1) x U(1)",
        chiral_families=3,
        right_handed_neutrinos=3,
        higgs_pairs=1,
        conjugate_families=0,
        exotic_massless_character_blocks=0,
        anomaly_budget_required=True,
        complete_chain_computability_required=True,
        selection_constraints_are_not_predictions=True,
        forbidden_inputs=(
            "measured masses",
            "mixing angles",
            "CP data",
            "gauge couplings",
            "fitted hierarchies",
            "superseded two-Higgs coordinates",
        ),
        tiers=(
            TierBound(
                "Tier A",
                6,
                1,
                4,
                4,
                ("I3/I6 Hilbert-Burch schemes", "rank-two Serre constituents"),
            ),
            TierBound(
                "Tier B",
                9,
                2,
                8,
                8,
                ("invariant zero-dimensional schemes", "bounded Serre pairs"),
            ),
            TierBound(
                "Tier C",
                12,
                3,
                12,
                12,
                ("equivariant monads", "mapping-cone bundles", "multi-step extensions"),
            ),
        ),
    )


__all__ = [
    "ComputableCarrierSpecification",
    "TierBound",
    "computable_carrier_specification",
]
