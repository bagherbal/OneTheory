"""Test exact visible-bundle and point-scheme carrier invariants.

Owns:
    Hilbert–Burch identities, scheme lengths, Serre kernel characters and rays,
    determinant cancellation, equivariant descent, spectrum counts, and the
    one-Higgs carrier identity firewall.

Depends on:
    `onetheory.models.heterotic_schoen.visible`, concrete Schoen geometry, exact
    Rational and Eisenstein arithmetic, and pytest.

Must not:
    Create metrics, instanton amplitudes, hidden bundles, physical Yukawas, or
    normalized observables.

Phase 0:
    Exact published visible-sector tests only; unresolved downstream physics stays
    fail-closed.
"""

from __future__ import annotations

from onetheory.math.numbers import OMEGA, Eisenstein
from onetheory.models.heterotic_schoen.geometry import schoen_geometry
from onetheory.models.heterotic_schoen.visible import (
    mixed_maurer_cartan_branch,
    observable_admissibility,
    point_schemes,
    serre_data,
    split_wall_deformation,
    visible_bundle,
)


def test_point_schemes_reproduce_exact_hilbert_burch_lengths() -> None:
    length_three, length_six = point_schemes()

    assert length_three.resolution.verifies_generators()
    assert length_six.resolution.verifies_generators()
    assert length_three.resolution.basis_shape.space(0).dimension == 3
    assert length_three.resolution.basis_shape.space(1).dimension == 2
    assert length_six.resolution.basis_shape.space(0).dimension == 4
    assert length_six.resolution.basis_shape.space(1).dimension == 3
    assert length_three.length == 3
    assert length_six.length == 6


def test_serre_kernel_actions_and_invariant_rays_are_exact() -> None:
    data = serre_data()

    assert data.action("W1").commutes
    assert data.action("W2").commutes
    assert data.action("W1").character_multiplicity(Eisenstein(1), Eisenstein(1)) == 1
    assert data.action("W1").character_multiplicity(OMEGA, Eisenstein(1)) == 1
    assert all(ray.p_fixed and ray.t_fixed for ray in data.rays)
    assert data.local_i6.unit == Eisenstein(1)
    assert data.local_i6.nilpotent == OMEGA


def test_visible_bundle_is_the_published_one_higgs_extension() -> None:
    visible = visible_bundle(schoen_geometry())

    assert visible.bundle.rank == 4
    assert visible.bundle.status.value == "published"
    assert visible.bundle.c1 == (0, 0, 0)
    assert visible.constituent_one.twist == tuple(-value for value in visible.constituent_two.twist)
    assert visible.determinant_c1 == (0, 0, 0)
    assert visible.equivariant_descent
    assert visible.commutant.name == "Spin(10)"
    assert visible.spectrum.families == 3
    assert visible.spectrum.right_handed_neutrinos == 3
    assert visible.spectrum.higgs_pairs == 1
    assert visible.spectrum.anti_families == 0
    assert visible.spectrum.exotic_zero_modes == 0
    assert visible.spectrum.geometric_moduli == 6
    assert visible.spectrum.observable_bundle_moduli == 13


def test_split_wall_branch_recomputes_the_formal_local_certificates() -> None:
    wall = split_wall_deformation()
    branch = mixed_maurer_cartan_branch(wall)
    admissibility = observable_admissibility(branch)

    assert wall.forward.dimension == 4
    assert wall.reverse.dimension == 8
    assert not wall.common_dga_representatives_available
    assert branch.formally_integrable
    assert branch.curvature_correction == "-s*t*K_y is required to cancel the E*F curvature term"
    assert admissibility.certified
    assert admissibility.local_freeness.determinant_at_origin == 1
    assert admissibility.spectrum.multiplicities == (3,) * 9
