"""Generate the immutable source-backed visible-carrier artifact.

Owns:
    Deterministic serialization and content hashing of the retrieved source
    manifest, exact Schoen geometry handoff, Hilbert–Burch schemes, Serre data,
    published extension dimensions, and the first missing chain-level input.

Depends on:
    Standard-library JSON, hashing, pathlib, and platform APIs; production
    Schoen geometry, exact polynomial data, and visible-bundle metadata.

Must not:
    Read observations, select coefficients from measurements, synthesize
    cocycles or matrices, or report unresolved source claims as certified.

Phase 0:
    Reconstruction stops at the published-data boundary and records outcome 3
    when indispensable unpublished chain representatives are unavailable.
"""

from __future__ import annotations

import argparse
import json
from collections.abc import Mapping
from hashlib import sha256
from pathlib import Path

from onetheory.math.linear import Matrix, Vector
from onetheory.math.numbers import Eisenstein, Rational
from onetheory.math.polynomials import Polynomial
from onetheory.models.heterotic_schoen.geometry import schoen_geometry
from onetheory.models.heterotic_schoen.visible import (
    InvariantSerreRay,
    PointScheme,
    SerreData,
    SerreKernelAction,
    SplitWallDeformation,
    point_schemes,
    serre_data,
    split_wall_deformation,
    visible_bundle,
)


def _exact(value: object) -> object:
    """Convert supported exact objects into deterministic JSON values."""

    if isinstance(value, (Rational, Eisenstein)):
        return str(value)
    if isinstance(value, Polynomial):
        return {
            "variable_count": value.variable_count,
            "scalar_type": value.scalar_type.__name__,
            "terms": [
                {"exponents": list(exponents), "coefficient": str(coefficient)}
                for exponents, coefficient in value.terms
            ],
        }
    if isinstance(value, Matrix):
        return {
            "shape": list(value.shape),
            "scalar_type": value.scalar_type.__name__,
            "rows": [[str(entry) for entry in row] for row in value.rows],
        }
    if isinstance(value, Vector):
        return {
            "dimension": value.dimension,
            "scalar_type": value.scalar_type.__name__,
            "values": [str(entry) for entry in value.values],
        }
    if isinstance(value, Mapping):
        return {str(key): _exact(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_exact(item) for item in value]
    return value


def _sha256(path: Path) -> str:
    """Return the content hash of one declared repository artifact."""

    return sha256(path.read_bytes()).hexdigest()


def _polynomial_matrix(matrix: tuple[tuple[Polynomial, ...], ...]) -> object:
    """Serialize a polynomial matrix without losing exact coefficients."""

    return _exact(matrix)


def _scheme_record(scheme: PointScheme) -> dict[str, object]:
    """Serialize one exact Hilbert–Burch point-scheme record."""

    resolution = scheme.resolution
    return {
        "name": scheme.name,
        "ideal_generators": _exact(scheme.ideal_generators),
        "length": str(scheme.length),
        "certified_minors": scheme.is_certified,
        "hilbert_burch": {
            "matrix": _polynomial_matrix(resolution.matrix),
            "generators": _exact(resolution.generators),
            "maximal_minors": _exact(resolution.maximal_minors),
            "hilbert_numerator": list(resolution.hilbert_numerator),
            "free_resolution": {
                "term_ranks": [list(item) for item in resolution.free_resolution.term_ranks],
                "differential_shapes": [
                    [degree, list(differential.shape)]
                    for degree, differential in resolution.free_resolution.differentials
                ],
                "squared_zero": resolution.free_resolution.squared_zero,
            },
        },
    }


def _action_record(action: SerreKernelAction) -> dict[str, object]:
    """Serialize one exact finite-dimensional Serre kernel action."""

    return {
        "name": action.name,
        "dimension": action.dimension,
        "p": _exact(action.p),
        "t": _exact(action.t),
        "commutes": action.commutes,
        "character_multiplicities": [
            {
                "p": str((p_value, t_value)[0]),
                "t": str((p_value, t_value)[1]),
                "multiplicity": multiplicity,
            }
            for (p_value, t_value), multiplicity in action.p_character_multiplicities
        ],
    }


def _ray_record(ray: InvariantSerreRay) -> dict[str, object]:
    """Serialize one exact shifted-action invariant ray."""

    return {
        "name": ray.name,
        "vector": _exact(ray.vector),
        "shifted_p": _exact(ray.shifted_p),
        "shifted_t": _exact(ray.shifted_t),
        "p_fixed": ray.p_fixed,
        "t_fixed": ray.t_fixed,
    }


def _serre_record(data: SerreData) -> dict[str, object]:
    """Serialize the exact kernel, ray, and local-character data."""

    return {
        "coefficient_field": "Q(omega)",
        "actions": [_action_record(action) for action in data.actions],
        "invariant_rays": [_ray_record(ray) for ray in data.rays],
        "local_i6": {
            "unit": str(data.local_i6.unit),
            "nilpotent": str(data.local_i6.nilpotent),
        },
    }


def _wall_record(wall: SplitWallDeformation) -> dict[str, object]:
    """Record abstract deformation dimensions without fabricating cocycles."""

    return {
        "summands": list(wall.summands),
        "forward_dimension": wall.forward.dimension,
        "reverse_dimension": wall.reverse.dimension,
        "coefficient_field": wall.coefficient_field,
        "basis_convention": wall.basis_convention,
        "common_dga_representatives_available": (
            wall.common_dga_representatives_available
        ),
        "basis_status": "abstract Ext labels only",
    }


def _source_provenance(root: Path) -> dict[str, object]:
    """Hash the frozen manifest and the unchanged draft source artifacts."""

    manifest = root / "data/published/visible_carrier/source_manifest.json"
    declared = (
        "Experimental_Draft_OneTheory.py",
        "Experimental_Draft_OneTheory.docx",
    )
    return {
        "source_manifest": {
            "path": str(manifest.relative_to(root)),
            "sha256": _sha256(manifest),
        },
        "draft_artifacts": [
            {"path": name, "sha256": _sha256(root / name)}
            for name in declared
            if (root / name).is_file()
        ],
        "retrieved_primary_source_archives": True,
        "ancillary_computational_files": "none advertised in retrieved records",
    }


def build_artifact(root: Path) -> dict[str, object]:
    """Build the deterministic artifact and preserve every unresolved edge."""

    geometry = schoen_geometry()
    schemes = point_schemes()
    serre = serre_data()
    visible = visible_bundle(geometry)
    wall = split_wall_deformation()
    cox = geometry.cover.cox
    return {
        "schema": {
            "name": "VisibleCarrierArtifact",
            "version": 1,
            "immutable": True,
            "content_addressed": True,
            "digest_algorithm": "sha256",
        },
        "carrier": {
            "name": "published one-Higgs heterotic Schoen carrier",
            "superseded_carriers_excluded": ["two-Higgs carrier"],
            "coefficient_field": "Q(omega)",
        },
        "provenance": _source_provenance(root),
        "conventions": {
            "polynomial_variables": list(cox.variables),
            "eisenstein_relation": cox.coefficient_relation,
            "basis": list(geometry.basis.labels),
            "quotient_normalization": "quotient",
            "cover_normalization": "cover",
            "covering_degree": 9,
            "status": "exact values are serialized as text in declared bases",
        },
        "ambient": {
            "status": "partially reconstructed",
            "cover": {
                "name": geometry.cover.name,
                "base_surfaces": list(geometry.cover.base_surfaces),
                "base_maps": list(geometry.cover.base_maps),
                "fiber_product_equation": geometry.cover.fiber_product_equation,
                "cox": {
                    "variables": list(cox.variables),
                    "multidegrees": _exact(cox.multidegrees),
                    "equations": list(cox.equations),
                    "base_identification": cox.base_identification,
                    "cubic_f": _exact(cox.cubic_f),
                    "cubic_g": _exact(cox.cubic_g),
                },
            },
            "quotient": {
                "group": geometry.quotient.group_name,
                "generators": list(geometry.quotient.generators),
                "order": geometry.quotient.order,
                "acts_freely": geometry.quotient.acts_freely,
                "freeness_certificate": {
                    "status": "declared by production handoff",
                    "independent_pointwise_certificate": False,
                },
            },
            "intersection_tensor": {
                "basis": list(geometry.quotient_intersections.basis.labels),
                "normalization": geometry.quotient_intersections.normalization.name,
                "entries": _exact(geometry.quotient_intersections.entries),
            },
            "heisenberg_lifts": {
                "p": _exact(geometry.heisenberg.p),
                "t": _exact(geometry.heisenberg.t),
                "coefficient": str(geometry.heisenberg.coefficient),
                "order_three_p": geometry.heisenberg.order_three_p,
                "order_three_t": geometry.heisenberg.order_three_t,
                "projective_commutator": geometry.heisenberg.projective_commutator,
                "deck_commutator": geometry.heisenberg.deck_commutator,
            },
            "deck_action": {
                "status": "exact projective lift identities available",
                "global_freeness": "not independently serialized",
            },
        },
        "point_schemes": [_scheme_record(scheme) for scheme in schemes],
        "serre": _serre_record(serre),
        "visible_bundle": {
            "status": "published metadata plus exact constituent point schemes",
            "rank": visible.bundle.rank,
            "group": visible.bundle.structure_group.name,
            "constituents": [
                {
                    "name": visible.constituent_one.name,
                    "rank": visible.constituent_one.rank,
                    "twist": _exact(visible.constituent_one.twist),
                    "scheme": visible.constituent_one.point_scheme.name,
                    "source_definition": "V1 = O(-tau1+tau2) tensor pi1*(W1)",
                },
                {
                    "name": visible.constituent_two.name,
                    "rank": visible.constituent_two.rank,
                    "twist": _exact(visible.constituent_two.twist),
                    "scheme": visible.constituent_two.point_scheme.name,
                    "source_definition": "V2 = O(tau1-tau2) tensor pi2*(W2)",
                },
            ],
            "outer_sequence": visible.outer_extension,
            "outer_extension_class": {
                "status": "not serialized by the retrieved primary sources",
                "representatives": [],
            },
            "determinant_c1": _exact(visible.determinant_c1),
            "equivariant_descent": visible.equivariant_descent,
            "spectrum_metadata": {
                "families": visible.spectrum.families,
                "right_handed_neutrinos": visible.spectrum.right_handed_neutrinos,
                "higgs_pairs": visible.spectrum.higgs_pairs,
                "observable_bundle_moduli": visible.spectrum.observable_bundle_moduli,
            },
        },
        "outer_extension": {
            "cohomology_dimensions_h0_to_h3": [0, 36, 72, 0],
            "regular_representation_dimensions_h0_to_h3": [0, 4, 8, 0],
            "invariant_ext1_dimension": 4,
            "representatives": [],
            "status": "blocked: dimension is published; invariant cocycles are absent",
            "required_for_promotion": [
                "four explicit invariant Ext^1 cocycles",
                "common Cech/Koszul basis and signs",
                "local transition maps and equivariant lifts",
            ],
        },
        "common_chain_model": {
            "status": "blocked",
            "required": [
                "synchronized Cech cover",
                "Koszul ordering and local trivializations",
                "V1/V2 chain representatives",
                "deck action on every graded component",
                "DGA/module/pairing/contracting identities",
            ],
            "representatives": [],
        },
        "flavor": {
            "status": "blocked at missing outer cocycles and common chain model",
            "available": "abstract split-wall Ext dimensions only",
            "abstract_split_wall": _wall_record(wall),
            "target_artifacts": {
                "f3_traces": "unresolved",
                "F3_F5_F7_K5_K7": "unresolved",
                "residues": "unresolved; target count 24",
                "amplitudes_and_hessians": "unresolved; target count 12",
            },
        },
        "positive_twist": {
            "status": "unresolved research claims, not certified inputs",
            "target_kahler_point": [5, 7, 1],
            "target_basis_dimensions": [192, 212],
            "target_decision_split": [136, 76],
            "target_lifts": 848,
            "target_evaluation_matrix": {"rows": 4, "columns": 404},
            "certified": False,
        },
        "conic_seeds": {
            "status": "blocked",
            "required": [
                "explicit seed conic representatives and embeddings",
                "bundle restrictions and extension maps",
                "normal jets and chain maps",
            ],
            "pfaffian_representatives": [],
        },
        "verification": {
            "exact_checks_run": [
                "Hilbert-Burch maximal-minor identities",
                "point-scheme lengths 3 and 6",
                "polynomial free-resolution square-zero",
                "Serre kernel commutation and shifted invariant rays",
                "Heisenberg lift order and projective commutator",
            ],
            "independent_external_cas": "unavailable in the environment",
            "observational_data_used": False,
            "synthetic_physical_values_used": False,
        },
        "outcome": {
            "code": 3,
            "status": "blocked by an indispensable unpublished datum",
            "failed_derivation": [
                "The retrieved primary source archives were inspected and hashed.",
                "They determine the sheaf extensions, twists, ideals, and dimension counts.",
                (
                    "They do not serialize four invariant Ext cocycles, transition "
                    "functions, or the 404-section evaluation matrix."
                ),
                (
                    "A dimension count cannot determine those chain representatives "
                    "without a chosen cover, trivializations, extension class, and coordinates."
                ),
            ],
            "indispensable_missing_datum": (
                "four explicit invariant Ext^1 cocycles in one synchronized "
                "Cech-Koszul convention, together with their local transition data"
            ),
            "next_action": (
                "obtain or independently derive that exact chain-level datum "
                "before promotion"
            ),
        },
    }


def _with_digest(payload: dict[str, object]) -> dict[str, object]:
    """Return a copy of the payload with its canonical content digest."""

    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    result = dict(payload)
    result["artifact_digest"] = sha256(canonical.encode("utf-8")).hexdigest()
    return result


def write_artifact(root: Path, output: Path | None = None) -> dict[str, object]:
    """Build the artifact and optionally write its canonical JSON representation."""

    artifact = _with_digest(build_artifact(root))
    if output is not None:
        target = output if output.is_absolute() else root / output
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            json.dumps(artifact, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    return artifact


def main(argv: list[str] | None = None) -> int:
    """Generate the artifact and print only its immutable identity."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    root = Path(__file__).resolve().parents[3]
    artifact = write_artifact(root, args.output)
    print(f"artifact_digest: {artifact['artifact_digest']}")
    print(f"outcome: {artifact['outcome']['code']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
