"""Record downstream carrier gates without inventing physical outputs.

Owns:
    Deterministic dependency chains from the bounded rank-four transition
    frontier to stability, spectrum, common-DGA, metric, instanton, and hidden
    consistency calculations.

Depends on:
    The exact bounded rank-four frontier and immutable standard-library data
    structures. It does not read observations or select a candidate.

Must not:
    Replace missing sheaf, equivariance, metric, instanton, or hidden-bundle
    calculations with status values, synthetic observables, or copied reference
    results.

Phase 0:
    Downstream gates are explicit and fail closed; no physical downstream
    artifact is promoted until its prerequisite chain is certified.
"""

from __future__ import annotations

from dataclasses import dataclass

from .rank_four import RankFourFrontier, tier_a_rank_four_frontier


@dataclass(frozen=True, slots=True)
class DownstreamGate:
    """One downstream calculation with an explicit unresolved boundary."""

    name: str
    first_missing_prerequisite: str
    prerequisite_chain: tuple[str, ...]
    promotable: bool

    def __post_init__(self) -> None:
        if not self.name.strip() or not self.first_missing_prerequisite.strip():
            raise ValueError("downstream gates require named prerequisites")
        if not self.prerequisite_chain:
            raise ValueError("downstream gates require a nonempty dependency chain")
        if self.first_missing_prerequisite != self.prerequisite_chain[0]:
            raise ValueError("the first missing prerequisite must head the chain")
        if self.promotable:
            raise ValueError("unresolved downstream gates cannot be promotable")

    def as_record(self) -> dict[str, object]:
        """Return the gate without creating a physical result."""

        return {
            "name": self.name,
            "first_missing_prerequisite": self.first_missing_prerequisite,
            "prerequisite_chain": list(self.prerequisite_chain),
            "promotable": self.promotable,
        }


@dataclass(frozen=True, slots=True)
class DownstreamFrontier:
    """The unresolved downstream calculation frontier for the new carrier."""

    rank_four: RankFourFrontier
    gates: tuple[DownstreamGate, ...]

    def __post_init__(self) -> None:
        names = tuple(gate.name for gate in self.gates)
        if len(set(names)) != len(names):
            raise ValueError("downstream gate names must be unique")

    def gate(self, name: str) -> DownstreamGate:
        """Return one named downstream gate."""

        for gate in self.gates:
            if gate.name == name:
                return gate
        raise KeyError(name)

    @property
    def promotable(self) -> bool:
        """Return whether every downstream gate has a certified result."""

        return all(gate.promotable for gate in self.gates)

    def as_record(self) -> dict[str, object]:
        """Return exact gate chains and no fabricated downstream values."""

        return {
            "promotable": self.promotable,
            "gates": [gate.as_record() for gate in self.gates],
            "status": "downstream calculations blocked by explicit prerequisites",
        }


def downstream_frontier(
    rank_four: RankFourFrontier | None = None,
) -> DownstreamFrontier:
    """Build all downstream dependency chains from the rank-four frontier."""

    frontier = tier_a_rank_four_frontier() if rank_four is None else rank_four
    if not frontier.all_cocycles or not frontier.all_locally_free:
        raise ValueError("downstream gates require exact bounded rank-four checks")
    gates = (
        DownstreamGate(
            "stability",
            "global polynomial horseshoe or mapping-cone certificate",
            (
                "global polynomial horseshoe or mapping-cone certificate",
                "global locally free rank-four sheaf",
                "equivariant descent and exact stability chamber",
            ),
            False,
        ),
        DownstreamGate(
            "spectrum",
            "global equivariant sheaf cohomology representatives",
            (
                "global equivariant sheaf cohomology representatives",
                "complete cohomology character decomposition",
                "Wilson-line projection and exact spectrum certificate",
            ),
            False,
        ),
        DownstreamGate(
            "common_dga",
            "common Cech-Koszul hypercohomology representatives",
            (
                "common Cech-Koszul hypercohomology representatives",
                "deck action on every graded component",
                "equivariant cyclic products and trace conventions",
            ),
            False,
        ),
        DownstreamGate(
            "metrics",
            "complete normalized matter and Higgs section bases",
            (
                "complete normalized matter and Higgs section bases",
                "Ricci-flat metric and HYM connection certificate",
                "converged matter metric and canonical normalization",
            ),
            False,
        ),
        DownstreamGate(
            "instantons",
            "explicit bundle restrictions on certified rational curves",
            (
                "explicit bundle restrictions on certified rational curves",
                "Pfaffian determinant-line maps and Quillen normalization",
                "controlled instanton amplitudes and phase conventions",
            ),
            False,
        ),
        DownstreamGate(
            "hidden_consistency",
            "selected visible carrier with certified Chern data",
            (
                "selected visible carrier with certified Chern data",
                "hidden bundle maps, descent, and stability",
                "Bianchi identity, anomaly cancellation, and hidden spectrum",
            ),
            False,
        ),
    )
    return DownstreamFrontier(frontier, gates)


def tier_a_downstream_frontier() -> DownstreamFrontier:
    """Build the downstream gate report for the Tier A frontier."""

    return downstream_frontier()


__all__ = ["DownstreamFrontier", "DownstreamGate", "downstream_frontier",
           "tier_a_downstream_frontier"]
