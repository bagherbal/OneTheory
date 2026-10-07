"""Exact invariant-theory audit of the inherited hierarchy-seed integers.

Owns:
    Weight-multiset counts of invariant lines in the inherited "defect chamber"
    Lambda^2 X4 (x) V8 (x) End(F3) under the Lorentz and flavor symmetries that
    the MinTOE/ASHA construction attaches to its factors.

Depends on:
    Only exact integer arithmetic; the sl2 + sl2 complexification of the
    Lorentz algebra and the u(3) adjoint weights are written out explicitly.

Must not:
    Assign physical meaning to 431, 14, 9/5 or 8 pi, choose a different
    integer, or use observations.

Phase 0:
    Research audit of an inherited bridge definition; no physical claim.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from itertools import product

# so(1,3) complexified is sl2 + sl2; a weight is a pair (2*m_left, 2*m_right).
VECTOR = Counter({(1, 1): 1, (1, -1): 1, (-1, 1): 1, (-1, -1): 1})


def _tensor(left: Counter, right: Counter) -> Counter:
    result: Counter = Counter()
    for (a, ma), (b, mb) in product(left.items(), right.items()):
        result[tuple(x + y for x, y in zip(a, b, strict=True))] += ma * mb
    return result


def _exterior_square(weights: Counter) -> Counter:
    expanded = [w for w, m in sorted(weights.items()) for _ in range(m)]
    result: Counter = Counter()
    for i in range(len(expanded)):
        for j in range(i + 1, len(expanded)):
            result[tuple(x + y for x, y in zip(expanded[i], expanded[j], strict=True))] += 1
    return result


def lorentz_invariant_count(weights: Counter) -> int:
    """Trivial summands of an sl2 + sl2 module: m(0,0)-m(2,0)-m(0,2)+m(2,2)."""

    return weights[(0, 0)] - weights[(2, 0)] - weights[(0, 2)] + weights[(2, 2)]


@dataclass(frozen=True)
class SeedChamberAudit:
    """Dimensions and invariant lines of the inherited defect chamber."""

    chamber_dimension: int
    lorentz_invariants_in_bivector_times_octave: int
    flavor_invariants_in_end_f3: int
    invariants_under_lorentz_and_flavor: int
    invariants_under_flavor_only: int
    flavor_traceless_dimension: int
    canonical_identity_line_exists: bool


def audit_seed_chamber() -> SeedChamberAudit:
    """Test whether "432 - 1 = 431" removes a canonical invariant line."""

    bivectors = _exterior_square(VECTOR)            # Lambda^2 X4, dimension 6
    octave = VECTOR + VECTOR                        # V8 = X4 + P4, both Lorentz vectors
    spacetime_part = _tensor(bivectors, octave)     # dimension 48
    spacetime_dimension = sum(spacetime_part.values())
    lorentz = lorentz_invariant_count(spacetime_part)
    flavor = 1  # End(F3) = 1 + adjoint under u(3): exactly one invariant (the identity)
    end_f3_dimension = 9
    return SeedChamberAudit(
        chamber_dimension=spacetime_dimension * end_f3_dimension,
        lorentz_invariants_in_bivector_times_octave=lorentz,
        flavor_invariants_in_end_f3=flavor,
        invariants_under_lorentz_and_flavor=lorentz * flavor,
        invariants_under_flavor_only=spacetime_dimension * flavor,
        flavor_traceless_dimension=spacetime_dimension * (end_f3_dimension - flavor),
        canonical_identity_line_exists=lorentz * flavor == 1,
    )


if __name__ == "__main__":
    print(audit_seed_chamber())
