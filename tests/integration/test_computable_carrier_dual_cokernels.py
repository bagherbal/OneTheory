"""Test finite dual-resolution cokernels without promoting them to Ext data.

Owns:
    Exact presentation ranks, representative dimensions, relation preservation,
    and the derived P/T commutator boundary for the I3/I6 diagnostics.

Depends on:
    The computable-carrier dual-presentation experiment and exact Eisenstein
    linear algebra.

Must not:
    Identify the finite cokernels with sheaf Ext, reuse published Serre rays,
    or infer honest descent from their action characters.

Phase 0:
    Dual graded cokernels are tested as explicit diagnostics; Serre comparison
    and projective sheafification remain unresolved.
"""

from __future__ import annotations

from onetheory.math.numbers import OMEGA2, Eisenstein
from research.experiments.computable_carrier.dual_cokernels import (
    tier_a_dual_cokernels,
)


def test_tier_a_dual_presentations_have_exact_dimensions() -> None:
    """The lowest dual presentations retain exact I3/I6 quotient sizes."""

    cokernels = tier_a_dual_cokernels()

    assert tuple(cokernel.scheme.name for cokernel in cokernels) == ("I3", "I6")
    assert tuple(cokernel.degree for cokernel in cokernels) == (-2, -3)
    assert tuple(cokernel.presentation.shape for cokernel in cokernels) == ((6, 3), (9, 4))
    assert tuple(cokernel.dimension for cokernel in cokernels) == (3, 5)
    assert all(action.preserves_relations for cokernel in cokernels for action in cokernel.actions)


def test_dual_cokernel_actions_keep_the_serre_boundary_explicit() -> None:
    """I3 remains projective while I6 has a commuting finite diagnostic."""

    i3, i6 = tier_a_dual_cokernels()

    assert not i3.action_commutes
    assert i3.commutator_scalar == OMEGA2
    assert i6.action_commutes
    assert i6.commutator_scalar == Eisenstein(1)
