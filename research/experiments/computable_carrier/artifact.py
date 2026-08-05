"""Serialize the current new-carrier construction frontier.

Owns:
    Deterministic content-addressed serialization of the new-carrier contract,
    finite search report, reference separation, and promotion-gate statuses.

Depends on:
    Standard-library JSON and hashing plus the local specification and search
    experiment. It does not read observations or import generated results.

Must not:
    Mark an unresolved descriptor as a selected carrier, copy reference
    cocycles, or emit physical spectrum, metric, flavor, or instanton results.

Phase 0:
    The artifact records construction progress and remains unpromotable until
    all chain-level gates are independently certified.
"""

from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path

from onetheory.models.heterotic_schoen.visible import point_schemes

from .cech_sections import bounded_cech_sections
from .constituents import tier_a_constituents
from .downstream import downstream_frontier
from .dp9_actions import dp9_deck_action_audit
from .dp9_homology import tier_a_dp9_derived_homs
from .dp9_hypersurface import tier_a_dp9_hypersurface_comparisons
from .dual_cokernels import tier_a_dual_cokernels
from .equivariance import tier_a_equivariance, tier_a_split_equivariance
from .equivariant_extensions import cached_tier_a_bounded_extension_equivariance
from .global_serre import tier_a_global_serre_pushout_audits
from .global_serre_search import tier_a_global_serre_ray_audits
from .hom_cech import cached_tier_a_hom_cech, tier_a_hom_cech
from .ideal_atlas import tier_a_atlas_ideal_resolutions
from .local_equivariance import tier_a_local_cech_deck_actions
from .outer import split_rank_four_baseline
from .outer_actions import bounded_outer_action
from .pencil import tier_a_pencil_model
from .polynomial_hom import polynomial_hom_degree_slice, tier_a_polynomial_hom_complex
from .projective_hom_action import projective_hom_deck_audit
from .projective_hom_search import tier_a_projective_hom_pair_audits
from .projective_hyperhom import tier_a_projective_hom_hypercohomology
from .projective_outer_frontier import tier_a_projective_outer_frontier
from .pushdown import tier_a_pushdown_constraints
from .pushout_linearization import tier_a_pushout_relation_linearizations
from .rank_four import rank_four_frontier
from .resolution_actions import tier_a_resolution_actions
from .search import finite_tier_search
from .serre_atlas import tier_a_atlas_serre_locals, tier_a_serre_pushout_atlases
from .serre_local import local_serre_model, tier_a_local_serre_models
from .serre_pushout import tier_a_serre_pushouts
from .serre_rays import tier_a_serre_eigenclass_variants
from .specification import computable_carrier_specification
from .tier_b_dp9_ideals import tier_b_dp9_monomial_ideal_resolutions
from .tier_b_local_serre import tier_b_local_monomial_serre_audits
from .tier_b_monomial import (
    tier_b_invariant_monomial_schemes,
    tier_b_monomial_resolution_actions,
)
from .tier_b_search import tier_b_known_scheme_search
from .tier_b_serre_sections import tier_b_projective_serre_section_audits
from .tier_b_twists import tier_b_twist_descent_screen


def _sha256(path: Path) -> str:
    """Hash one local benchmark artifact without interpreting its contents."""

    return sha256(path.read_bytes()).hexdigest()


def _bounded_hom_window_record(hom) -> dict[str, object]:
    """Serialize finite-window dimensions without recomputing representatives."""

    return {
        "bound": hom.bound,
        "basis_sizes": [
            [degree, len(hom.basis(degree))]
            for degree in hom.complex.degrees
        ],
        "h1_dimension": hom.h1_dimension,
        "squared_zero": all(
            hom.complex.differential(degree + 1).compose(
                hom.complex.differential(degree)
            ).is_zero()
            for degree in (0, 1)
        ),
        "status": hom.status,
    }


def build_artifact(root: Path) -> dict[str, object]:
    """Build a deterministic frontier artifact for the new carrier."""

    specification = computable_carrier_specification()
    search = finite_tier_search(specification)
    hom = tier_a_hom_cech()
    hom_bound_one = cached_tier_a_hom_cech(1)
    outer_actions = bounded_outer_action(hom)
    outer_actions_bound_one = bounded_outer_action(hom_bound_one)
    rank_four = rank_four_frontier(hom)
    downstream = downstream_frontier(rank_four)
    bounded_equivariance = cached_tier_a_bounded_extension_equivariance(2)
    resolution_actions = tier_a_resolution_actions()
    dual_cokernels = tier_a_dual_cokernels()
    local_serre_models = tier_a_local_serre_models()
    pencil_model = tier_a_pencil_model()
    atlas_ideal_resolutions = tier_a_atlas_ideal_resolutions(pencil_model)
    atlas_serre_locals = tier_a_atlas_serre_locals(pencil_model)
    serre_pushout_atlases = tier_a_serre_pushout_atlases(pencil_model)
    explicit_serre_pushouts = tier_a_serre_pushouts(pencil_model)
    pushout_relation_linearizations = tier_a_pushout_relation_linearizations(
        explicit_serre_pushouts
    )
    global_serre_pushouts = tier_a_global_serre_pushout_audits(
        pencil_model,
        explicit_serre_pushouts,
    )
    polynomial_hom = tier_a_polynomial_hom_complex()
    projective_hypercohomology = tier_a_projective_hom_hypercohomology()
    projective_deck_audit = projective_hom_deck_audit(projective_hypercohomology)
    serre_eigenclass_variants = tier_a_serre_eigenclass_variants(
        explicit_serre_pushouts,
        resolution_actions,
    )
    projective_hom_pair_audits = tier_a_projective_hom_pair_audits(
        explicit_serre_pushouts,
        resolution_actions,
        serre_eigenclass_variants,
    )
    projective_outer_frontier = tier_a_projective_outer_frontier(
        projective_hom_pair_audits,
    )
    dp9_hypersurface_comparisons = tier_a_dp9_hypersurface_comparisons(
        projective_hom_pair_audits,
    )
    dp9_derived_homs = tier_a_dp9_derived_homs(projective_hom_pair_audits)
    dp9_deck_actions = tuple(
        dp9_deck_action_audit(item) for item in dp9_derived_homs
    )
    tier_b_known_schemes = tier_b_known_scheme_search(
        projective_hom_pair_audits,
        dp9_deck_actions,
    )
    tier_b_monomial_schemes = tier_b_invariant_monomial_schemes(
        tier_b_known_schemes.maximum_point_length,
    )
    tier_b_monomial_actions = tier_b_monomial_resolution_actions(
        tier_b_monomial_schemes,
    )
    tier_b_twist_screen = tier_b_twist_descent_screen(
        tier_b_known_schemes.twist_radius,
    )
    tier_b_projective_sections = tier_b_projective_serre_section_audits(
        tier_b_monomial_schemes,
    )
    tier_b_dp9_ideals = tier_b_dp9_monomial_ideal_resolutions(
        tier_b_monomial_schemes,
    )
    tier_b_local_serre = tier_b_local_monomial_serre_audits(
        tier_b_monomial_schemes,
    )
    global_serre_ray_audits = tier_a_global_serre_ray_audits(
        pencil_model,
        explicit_serre_pushouts,
        resolution_actions,
        serre_eigenclass_variants,
    )
    local_cech_actions = tier_a_local_cech_deck_actions(
        pencil_model,
        atlas_serre_locals,
    )
    pushdown_constraints = tier_a_pushdown_constraints()
    reference_artifact = root / "data/generated/visible_carrier/visible_carrier_artifact.json"
    return {
        "schema": {
            "name": "ComputableVisibleCarrierArtifact",
            "version": 1,
            "immutable": True,
            "content_addressed": True,
            "digest_algorithm": "sha256",
        },
        "identity": {
            "candidate": specification.identifier,
            "reference_benchmark": specification.reference_carrier_identifier,
            "identity_or_isomorphism_proved": False,
            "silent_reference_replacement_forbidden": True,
        },
        "specification": specification.as_record(),
        "finite_search": search.as_record(),
        "construction": {
            "selected_candidate": None,
            "status": "contract frozen; chain construction in progress",
            "required_artifacts": [
                "Cox charts and localization records",
                "rank-two Serre cocycles and transition matrices",
                "outer Ext complex and invariant cocycle basis",
                "rank-four mapping-cone complex",
                "stability chamber and exact spectrum representatives",
                "common DGA, metric, and instanton artifacts",
            ],
        },
        "tier_a_chain_inputs": {
            "status": (
                "exact complexes and local candidate transitions available; "
                "Serre gate pending"
            ),
            "point_schemes": [
                {
                    "name": scheme.name,
                    "polynomial_complex": {
                        "degrees": list(scheme.resolution.polynomial_complex.degrees),
                        "modules": [
                            {
                                "degree": degree,
                                "name": module.name,
                                "basis": list(module.basis),
                                "shifts": [list(shift) for shift in module.shifts],
                            }
                            for degree, module in scheme.resolution.polynomial_complex.modules
                        ],
                        "differential_shapes": [
                            [degree, list(differential.matrix.shape)]
                            for degree, differential
                            in scheme.resolution.polynomial_complex.differentials
                        ],
                        "squared_zero": scheme.resolution.polynomial_complex.squared_zero,
                    },
                }
                for scheme in point_schemes()
            ],
            "constituent_candidates": [
                candidate.as_record() for candidate in tier_a_constituents()
            ],
            "resolution_actions": [
                action_pair.as_record() for action_pair in resolution_actions
            ],
            "dual_cokernels": [
                cokernel.as_record() for cokernel in dual_cokernels
            ],
            "local_serre_models": [
                model.as_record() for model in local_serre_models
            ],
            "dP9_pencil": pencil_model.as_record(),
            "atlas_ideal_resolutions": [
                item.as_record() for item in atlas_ideal_resolutions
            ],
            "atlas_serre_locals": [item.as_record() for item in atlas_serre_locals],
            "serre_pushout_atlases": [
                item.as_record() for item in serre_pushout_atlases
            ],
            "explicit_serre_pushouts": [
                item.as_record() for item in explicit_serre_pushouts
            ],
            "pushout_relation_linearizations": [
                item.as_record() for item in pushout_relation_linearizations
            ],
            "global_serre_pushout_audits": [
                item.as_record() for item in global_serre_pushouts
            ],
            "global_serre_ray_audits": [
                item.as_record() for item in global_serre_ray_audits
            ],
            "serre_eigenclass_variants": [
                item.as_record() for item in serre_eigenclass_variants
            ],
            "polynomial_hom_presentation": polynomial_hom.as_record(),
            "polynomial_hom_degree_slices": [
                polynomial_hom_degree_slice(polynomial_hom, degree).as_record()
                for degree in (-2, -1, 0)
            ],
            "projective_hom_hypercohomology": projective_hypercohomology.as_record(),
            "projective_hom_deck_audit": projective_deck_audit.as_record(),
            "projective_hom_ray_pair_audits": [
                item.as_record() for item in projective_hom_pair_audits
            ],
            "projective_outer_frontier": projective_outer_frontier.as_record(),
            "dp9_hypersurface_comparisons": [
                item.as_record() for item in dp9_hypersurface_comparisons
            ],
            "dp9_derived_homs": [item.as_record() for item in dp9_derived_homs],
            "dp9_deck_actions": [item.as_record() for item in dp9_deck_actions],
            "tier_b_known_scheme_search": tier_b_known_schemes.as_record(),
            "tier_b_invariant_monomial_schemes": [
                item.as_record() for item in tier_b_monomial_schemes
            ],
            "tier_b_monomial_resolution_actions": [
                item.as_record() for item in tier_b_monomial_actions
            ],
            "tier_b_twist_descent_screen": tier_b_twist_screen.as_record(),
            "tier_b_projective_serre_sections": [
                item.as_record() for item in tier_b_projective_sections
            ],
            "tier_b_dp9_ideal_resolutions": [
                item.as_record() for item in tier_b_dp9_ideals
            ],
            "tier_b_local_serre_audits": [
                item.as_record() for item in tier_b_local_serre
            ],
            "local_cech_deck_actions": [item.as_record() for item in local_cech_actions],
            "local_class_boundary": {
                "I3": [local_serre_model("I3", "unit").as_record()],
                "I6": [
                    local_serre_model("I6", "unit").as_record(),
                    local_serre_model("I6", "nilpotent").as_record(),
                ],
                "status": (
                    "local pushout freeness only; global Serre patching and "
                    "linearization remain unresolved"
                ),
            },
            "pushdown_constraints": [
                constraint.as_record() for constraint in pushdown_constraints
            ],
            "bounded_cech_windows": [
                {
                    "scheme": candidate.scheme.name,
                    "windows": [
                        {
                            "bound": bound,
                            "cohomology_data": [list(item)
                                                 for item in bounded_cech_sections(
                                                     candidate.cover, bound
                                                 ).cohomology_data()],
                        }
                        for bound in (0, 1)
                    ],
                    "status": "finite localization diagnostic; not full sheaf cohomology",
                }
                for candidate in tier_a_constituents()
            ],
            "rank_four_baseline": split_rank_four_baseline().as_record(),
            "bounded_hom_cech": hom.as_record(),
            "bounded_hom_windows": [
                _bounded_hom_window_record(hom),
                _bounded_hom_window_record(hom_bound_one),
            ],
            "bounded_outer_action": outer_actions.as_record(),
            "bounded_outer_action_bound_one": outer_actions_bound_one.as_record(),
            "rank_four_frontier": rank_four.as_record(),
            "bounded_equivariant_extensions": {
                "bound": 2,
                "candidate_count": len(bounded_equivariance),
                "candidates": [item.as_record() for item in bounded_equivariance],
                "status": (
                    "finite affine gauge search; completeness beyond the declared "
                    "monomial window remains unproved"
                ),
            },
            "downstream_frontier": downstream.as_record(),
            "equivariance": tier_a_equivariance().as_record(),
            "split_equivariance": tier_a_split_equivariance().as_record(),
        },
        "promotion": {
            "production_import_allowed": False,
            "gates": {
                "chain_level": "unresolved",
                "equivariance": "unresolved",
                "local_freeness": "unresolved",
                "stability": "unresolved",
                "spectrum": "unresolved",
                "independent_external_algebra": "unresolved",
            },
        },
        "provenance": {
            "reference_artifact": {
                "path": str(reference_artifact.relative_to(root)),
                "sha256": _sha256(reference_artifact),
            },
            "observations_used": False,
            "measured_parameters_used": False,
            "superseded_two_higgs_data_used": False,
        },
        "external_algebra": {
            "status": "not available in current environment",
            "required_independent_path": "pinned SageMath, Singular, or Macaulay2 reproduction",
            "promotion_blocked": True,
        },
    }


def with_digest(payload: dict[str, object]) -> dict[str, object]:
    """Attach a digest over canonical JSON excluding the digest field."""

    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    result = dict(payload)
    result["artifact_digest"] = sha256(canonical.encode("utf-8")).hexdigest()
    return result


def write_artifact(root: Path, output: Path | None = None) -> dict[str, object]:
    """Build and optionally write the deterministic frontier artifact."""

    artifact = with_digest(build_artifact(root))
    if output is not None:
        target = output if output.is_absolute() else root / output
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            json.dumps(artifact, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    return artifact


def main() -> int:
    """Generate the frontier artifact at its declared repository location."""

    root = Path(__file__).resolve().parents[3]
    artifact = write_artifact(
        root,
        Path("data/generated/computable_carrier/computable_carrier_artifact.json"),
    )
    print(f"artifact_digest: {artifact['artifact_digest']}")
    print(f"candidate_count: {artifact['finite_search']['candidate_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
