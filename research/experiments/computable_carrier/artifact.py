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
from .dual_cokernels import tier_a_dual_cokernels
from .equivariance import tier_a_equivariance, tier_a_split_equivariance
from .equivariant_extensions import cached_tier_a_bounded_extension_equivariance
from .hom_cech import tier_a_hom_cech
from .outer import split_rank_four_baseline
from .pencil import tier_a_pencil_model
from .pushdown import tier_a_pushdown_constraints
from .rank_four import rank_four_frontier
from .resolution_actions import tier_a_resolution_actions
from .search import finite_tier_search
from .serre_local import local_serre_model, tier_a_local_serre_models
from .specification import computable_carrier_specification


def _sha256(path: Path) -> str:
    """Hash one local benchmark artifact without interpreting its contents."""

    return sha256(path.read_bytes()).hexdigest()


def build_artifact(root: Path) -> dict[str, object]:
    """Build a deterministic frontier artifact for the new carrier."""

    specification = computable_carrier_specification()
    search = finite_tier_search(specification)
    hom = tier_a_hom_cech()
    rank_four = rank_four_frontier(hom)
    downstream = downstream_frontier(rank_four)
    bounded_equivariance = cached_tier_a_bounded_extension_equivariance(2)
    resolution_actions = tier_a_resolution_actions()
    dual_cokernels = tier_a_dual_cokernels()
    local_serre_models = tier_a_local_serre_models()
    pencil_model = tier_a_pencil_model()
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
