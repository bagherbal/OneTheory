"""Exact structural quantum states, operators, and evolution contracts.

Owns:
    Hilbert-space declarations, immutable states, operators and adjoints,
    commutators and anticommutators, canonical bosonic and fermionic relations,
    Hamiltonians, unitary evolution contracts, action phases, and expectation
    records.

Depends on:
    Core policy and no concrete model, carrier, observation, or measured data.

Must not:
    Implement collapse, measurement interpretation, speculative quantum gravity, or
    a numerical claim about interacting quantum field theory.

Phase 0:
    The established structural quantum layer is implemented; interacting dynamics
    remain explicit contracts rather than numerical claims.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from onetheory.core.errors import IncompatibleConvention


@dataclass(frozen=True, slots=True)
class HilbertSpace:
    """A named complex Hilbert-space declaration with optional finite dimension."""

    name: str
    dimension: int | None

    def __init__(self, name: str, dimension: int | None = None) -> None:
        if not name.strip() or dimension == 0 or (dimension is not None and dimension < 0):
            raise ValueError("Hilbert spaces require a name and nonzero dimension")
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "dimension", dimension)


@dataclass(frozen=True, slots=True)
class QuantumState:
    """An immutable state declaration with a normalization contract."""

    space: HilbertSpace
    label: str
    normalized: bool
    amplitudes: tuple[Any, ...] | None

    def __init__(
        self,
        space: HilbertSpace,
        label: str,
        normalized: bool = False,
        amplitudes: Iterable[Any] | None = None,
    ) -> None:
        values = None if amplitudes is None else tuple(amplitudes)
        if not label.strip() or (
            values is not None and space.dimension is not None and len(values) != space.dimension
        ):
            raise ValueError("quantum states require a label and matching amplitudes")
        object.__setattr__(self, "space", space)
        object.__setattr__(self, "label", label)
        object.__setattr__(self, "normalized", normalized)
        object.__setattr__(self, "amplitudes", values)

    def require_normalized(self) -> None:
        if not self.normalized:
            raise ValueError("the requested observable requires a normalized state")


@dataclass(frozen=True, slots=True)
class Operator:
    """A typed linear operator with an explicit adjoint relation."""

    name: str
    domain: HilbertSpace
    codomain: HilbertSpace
    fermionic: bool
    adjoint_label: str

    def __init__(
        self,
        name: str,
        domain: HilbertSpace,
        codomain: HilbertSpace | None = None,
        fermionic: bool = False,
        adjoint_label: str | None = None,
    ) -> None:
        if not name.strip():
            raise ValueError("operators require a name")
        target = codomain or domain
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "domain", domain)
        object.__setattr__(self, "codomain", target)
        object.__setattr__(self, "fermionic", fermionic)
        object.__setattr__(self, "adjoint_label", adjoint_label or f"{name}†")

    def adjoint(self) -> Operator:
        """Return the typed adjoint operator."""

        return Operator(self.adjoint_label, self.codomain, self.domain, self.fermionic, self.name)

    def compose(self, other: Operator) -> Operator:
        """Compose operators only when their intermediate spaces agree."""

        if other.codomain != self.domain:
            raise IncompatibleConvention("operator domains do not compose")
        return Operator(
            f"{self.name}∘{other.name}",
            other.domain,
            self.codomain,
            self.fermionic or other.fermionic,
        )


class Bracket(StrEnum):
    """The graded bracket used by an operator relation."""

    COMMUTATOR = "commutator"
    ANTICOMMUTATOR = "anticommutator"


@dataclass(frozen=True, slots=True)
class OperatorRelation:
    """A symbolic commutator or anticommutator record."""

    left: Operator
    right: Operator
    bracket: Bracket
    result: Any


def commutator(left: Operator, right: Operator) -> OperatorRelation:
    """Record [A,B]=AB-BA with domain validation."""

    left.compose(right)
    right.compose(left)
    return OperatorRelation(left, right, Bracket.COMMUTATOR, (left, right, "AB-BA"))


def anticommutator(left: Operator, right: Operator) -> OperatorRelation:
    """Record {A,B}=AB+BA with domain validation."""

    left.compose(right)
    right.compose(left)
    return OperatorRelation(left, right, Bracket.ANTICOMMUTATOR, (left, right, "AB+BA"))


@dataclass(frozen=True, slots=True)
class CanonicalRelation:
    """A canonical bosonic or fermionic equal-time relation."""

    creation: Operator
    annihilation: Operator
    bracket: Bracket
    right_hand_side: Any

    @classmethod
    def bosonic(cls, creation: Operator, annihilation: Operator) -> CanonicalRelation:
        if creation.fermionic or annihilation.fermionic:
            raise ValueError("bosonic relations require bosonic operators")
        return cls(creation, annihilation, Bracket.COMMUTATOR, "δ")

    @classmethod
    def fermionic(cls, creation: Operator, annihilation: Operator) -> CanonicalRelation:
        if not creation.fermionic or not annihilation.fermionic:
            raise ValueError("fermionic relations require fermionic operators")
        return cls(creation, annihilation, Bracket.ANTICOMMUTATOR, "δ")


@dataclass(frozen=True, slots=True)
class Hamiltonian:
    """A self-adjoint Hamiltonian record on one Hilbert space."""

    name: str
    space: HilbertSpace
    terms: tuple[Any, ...]
    self_adjoint: bool

    def __init__(
        self, name: str, space: HilbertSpace, terms: Iterable[Any], self_adjoint: bool = True
    ) -> None:
        if not name.strip():
            raise ValueError("Hamiltonians require a name")
        if not self_adjoint:
            raise ValueError("Hamiltonian records must declare self-adjointness")
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "space", space)
        object.__setattr__(self, "terms", tuple(terms))
        object.__setattr__(self, "self_adjoint", self_adjoint)


@dataclass(frozen=True, slots=True)
class UnitaryEvolution:
    """A unitary evolution contract generated by a self-adjoint Hamiltonian."""

    hamiltonian: Hamiltonian
    parameter: str
    unitary: bool

    def __init__(self, hamiltonian: Hamiltonian, parameter: str = "t") -> None:
        if not parameter.strip():
            raise ValueError("unitary evolution requires an evolution parameter")
        if not hamiltonian.self_adjoint:
            raise ValueError("unitary evolution requires a self-adjoint Hamiltonian")
        object.__setattr__(self, "hamiltonian", hamiltonian)
        object.__setattr__(self, "parameter", parameter)
        object.__setattr__(self, "unitary", True)


@dataclass(frozen=True, slots=True)
class ActionPhase:
    """The symbolic phase exp(iS/hbar) retaining its action and constant."""

    action: Any
    reduced_planck_name: str
    phase_expression: str

    def __init__(self, action: Any, reduced_planck_name: str = "hbar") -> None:
        if not reduced_planck_name.strip():
            raise ValueError("action phases require an explicit hbar symbol")
        object.__setattr__(self, "action", action)
        object.__setattr__(self, "reduced_planck_name", reduced_planck_name)
        object.__setattr__(self, "phase_expression", f"exp(i*{action}/{reduced_planck_name})")


@dataclass(frozen=True, slots=True)
class ExpectationValue:
    """A normalized-state expectation-value contract."""

    state: QuantumState
    observable: Operator
    expression: str

    def __init__(self, state: QuantumState, observable: Operator) -> None:
        if observable.domain != state.space or observable.codomain != state.space:
            raise IncompatibleConvention("observable and state use different Hilbert spaces")
        state.require_normalized()
        object.__setattr__(self, "state", state)
        object.__setattr__(self, "observable", observable)
        object.__setattr__(self, "expression", f"<{state.label}|{observable.name}|{state.label}>")


__all__ = [
    "ActionPhase",
    "Bracket",
    "CanonicalRelation",
    "ExpectationValue",
    "Hamiltonian",
    "HilbertSpace",
    "Operator",
    "OperatorRelation",
    "QuantumState",
    "UnitaryEvolution",
    "anticommutator",
    "commutator",
]
