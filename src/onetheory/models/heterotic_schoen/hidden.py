"""Hidden-bundle construction and spectrum for the Schoen carrier.

Owns:
    Hidden-bundle construction, descent, stability, restrictions, hidden spectrum, and
    the model-specific data required by anomaly and vacuum calculations.

Depends on:
    Core policy, reusable geometry, finite, homological, and linear mathematics,
    general gauge, matter, and string physics, and established Schoen geometry.

Must not:
    Treat bounded candidate searches as bundle existence, use observations to select a
    support, or encode the excluded one-fibration route as a solution.

Phase 0:
    The exact topological target remains separate from the missing hidden-bundle
    input package; no candidate is promoted to a bundle.
"""

from __future__ import annotations

from dataclasses import dataclass

HIDDEN_BUNDLE_MISSING_CHAIN = (
    "all 44 objective-(28) support-pattern records with exact map data",
    "candidate 750 exact F and G polynomial matrices",
    "multigraded bases, irrelevant ideals, and affine-chart presentations",
    "Z3^2 pullback actions and honest linearizations",
    "global constant-rank and Fitting-ideal certificates",
    "equivariant Ext1 basis and non-split rank-four extension class",
    "all 27 curve restrictions and a common stable Kähler chamber",
    "hidden cohomology, gauge group, and charged-spectrum computation",
)


@dataclass(frozen=True, slots=True)
class HiddenBundleInputStatus:
    """Fail-closed status of the hidden-bundle construction boundary."""

    first_missing_input: str
    prerequisite_chain: tuple[str, ...]
    objective28_supports_available: bool
    candidate750_matrices_available: bool
    global_local_freeness_available: bool
    honest_descent_available: bool
    extension_available: bool
    curve_restrictions_available: bool
    stable_bundle_available: bool
    spectrum_available: bool


def hidden_bundle_input_status() -> HiddenBundleInputStatus:
    """Return the exact hidden-bundle boundary without a candidate fallback."""

    return HiddenBundleInputStatus(
        HIDDEN_BUNDLE_MISSING_CHAIN[0],
        HIDDEN_BUNDLE_MISSING_CHAIN,
        False,
        False,
        False,
        False,
        False,
        False,
        False,
        False,
    )
