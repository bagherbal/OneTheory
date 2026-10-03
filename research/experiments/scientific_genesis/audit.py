"""Generate and validate the machine-readable Scientific Genesis state.

Owns:
    Evidence-backed claim nodes, dependency edges, reusable-engine inventory,
    scoped results, structural questions, and a research-value scheduler.

Depends on:
    Standard-library inspection of repository sources and generated artifacts,
    plus research-only read-only consumers of completed bounded output and
    the source-pinned full neutrino witness packet.

Must not:
    Infer scientific truth from file presence, choose an extension coordinate,
    complete a missing physical edge, or import observations as source inputs.

Phase 0:
    Deterministic state reconstruction is available; all scientific statuses
    remain bounded by the evidence serialized here.
"""

from __future__ import annotations

import gzip
import hashlib
import json
from fractions import Fraction
from itertools import combinations
from pathlib import Path
from typing import Final, cast

ROOT: Final = Path(__file__).resolve().parents[3]
OUTPUT: Final = ROOT / "data/generated/scientific_genesis/scientific_genesis_state.json"
SCHEMA: Final = "scientific-genesis-state-v1"
STATUSES: Final = {
    "ASSUMED",
    "SELECTED",
    "DERIVED",
    "COMPUTED",
    "PROVED",
    "MEASURED",
    "FITTED",
    "CONJECTURED",
    "BLOCKED",
    "REFUTED",
}


def _sha256(path: Path) -> str:
    """Return one file's SHA-256 digest without interpreting its contents."""

    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _canonical_digest(payload: object) -> str:
    """Digest canonical compact JSON."""

    text = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _node(
    identifier: str,
    label: str,
    layer: str,
    status: str,
    statement: str,
    evidence: tuple[str, ...],
    assumptions: tuple[str, ...] = (),
    missing: tuple[str, ...] = (),
) -> dict[str, object]:
    """Create one explicit epistemic claim node."""

    return {
        "id": identifier,
        "label": label,
        "layer": layer,
        "status": status,
        "statement": statement,
        "evidence": list(evidence),
        "assumptions": list(assumptions),
        "missing_prerequisites": list(missing),
    }


def _edge(
    source: str,
    target: str,
    reason: str,
    implementation: tuple[str, ...],
    assumptions: tuple[str, ...],
    exact: bool,
    failure_modes: tuple[str, ...],
) -> dict[str, object]:
    """Create one evidence-bearing dependency implication."""

    return {
        "source": source,
        "target": target,
        "mathematical_reason": reason,
        "implementation_or_artifact": list(implementation),
        "assumptions_required": list(assumptions),
        "implication": "exact" if exact else "conditional_or_conjectural",
        "known_failure_modes": list(failure_modes),
    }


def _nodes() -> list[dict[str, object]]:
    """Return the audited claim set with exactly one status per node."""

    return [
        _node(
            "quantum_phase_structure",
            "quantum phase and Hilbert-space structure",
            "Genesis",
            "ASSUMED",
            "Quantum state, operator, and unitary-evolution laws are executable, "
            "but their deeper origin is not derived.",
            ("src/onetheory/physics/quantum.py", "tests/integration/test_established_laws.py"),
            ("standard quantum postulates",),
        ),
        _node(
            "lorentzian_causal_structure",
            "Lorentzian causal structure",
            "Genesis",
            "ASSUMED",
            "Spacetime and causal records implement established geometry; no "
            "pre-geometric derivation of Lorentzian signature exists.",
            ("src/onetheory/physics/spacetime.py",),
            ("Lorentzian manifold structure",),
        ),
        _node(
            "einstein_gravity",
            "Einstein gravity",
            "Genesis",
            "ASSUMED",
            "Einstein-Hilbert and matter-coupling laws are executable established "
            "inputs rather than consequences of a deeper OneTheory principle.",
            ("src/onetheory/physics/gravity.py", "tests/integration/test_established_laws.py"),
            ("general relativity",),
        ),
        _node(
            "dimensional_constant_contract",
            "c, hbar, and G foundational contract",
            "Genesis",
            "ASSUMED",
            "Dimensional constants are explicit symbolic primitives; only "
            "dimensionless consequences may later count as predictions.",
            ("src/onetheory/core/units.py", "src/onetheory/physics/compactification.py"),
            ("unit conventions and measured dimensional normalizations",),
        ),
        _node(
            "genesis_to_uv_bridge",
            "Genesis to quantum-gravitational UV implication",
            "Genesis",
            "BLOCKED",
            "No lawful derivation currently maps a deeper Genesis structure to "
            "the quantum, causal, gravitational, and heterotic structures used below.",
            ("README.md",),
            missing=(
                "primitive Genesis structure",
                "derivation of quantum phase",
                "derivation of causal geometry",
                "derivation of gravitational coupling",
                "derivation of the selected UV theory",
            ),
        ),
        _node(
            "heterotic_uv",
            "ten-dimensional E8 x E8 heterotic structure",
            "Heterotic realization",
            "SELECTED",
            "Heterotic theory is the explicit conditional UV realization; its "
            "selection is not a Genesis derivation.",
            ("src/onetheory/physics/strings.py", "src/onetheory/physics/compactification.py"),
            ("heterotic UV realization",),
        ),
        _node(
            "schoen_geometry",
            "Schoen fiber product and free Z3 x Z3 quotient",
            "Heterotic realization",
            "COMPUTED",
            "Published Schoen geometry, quotient normalization, Cox equations, "
            "and deck actions are represented exactly.",
            (
                "src/onetheory/models/heterotic_schoen/geometry.py",
                "data/published/visible_carrier/source_manifest.json",
                "tests/integration/test_computable_carrier_dp9_hypersurface.py",
            ),
            ("published one-Higgs Schoen geometry",),
        ),
        _node(
            "standard_model_laws",
            "parameterized Standard Model laws",
            "Low-energy laws",
            "ASSUMED",
            "Gauge representations, charges, interactions, and anomaly checks "
            "implement established low-energy law input without measured parameters.",
            ("src/onetheory/models/standard_model.py", "tests/unit/test_standard_model.py"),
            ("established Standard Model",),
        ),
        _node(
            "published_visible_carrier",
            "published one-Higgs visible SU(4) carrier",
            "Reference realization",
            "SELECTED",
            "The published carrier's sheaf definitions, topology, abstract Ext "
            "dimension, spectrum metadata, and stability result are selected reference inputs.",
            (
                "src/onetheory/models/heterotic_schoen/visible.py",
                "data/published/visible_carrier/source_manifest.json",
                "data/generated/visible_carrier/visible_carrier_artifact.json",
            ),
            ("published source claims and conventions",),
        ),
        _node(
            "published_projective_pushout_adapter",
            "projective-pushout published-carrier adapter",
            "Reference realization",
            "REFUTED",
            "Applying the exact I3/I6 base pushouts with the published twists "
            "gives cover Ext-one dimensions 0 and 63, not the source-bound 36 "
            "and 72. The adapter is not a W1/W2 chain model.",
            (
                "data/generated/scientific_genesis/"
                "published_pushout_mismatch.json",
                "research/experiments/scientific_genesis/"
                "published_pushout_mismatch.py",
            ),
        ),
        _node(
            "published_constituent_ext_spaces",
            "published constituent Serre extension spaces",
            "Reference realization",
            "COMPUTED",
            "Fiber-sensitive dP9 Hilbert--Burch/Koszul total complexes derive "
            "the W1 and W2 constituent Ext-one dimensions 2 and 5 exactly, "
            "without importing the published action matrices.",
            (
                "data/generated/scientific_genesis/"
                "published_constituent_ext_spaces.json",
                "research/experiments/computable_carrier/dp9_serre_ext.py",
                "tests/integration/"
                "test_scientific_genesis_published_constituent_ext_spaces.py",
            ),
        ),
        _node(
            "published_constituent_deck_actions",
            "published constituent Ext representation alignment",
            "Reference realization",
            "COMPUTED",
            "Natural dP9 chain actions and an exact simultaneous intertwiner "
            "recover the source representations. The fixed line of the aligned "
            "representation is not the selected physical extension ray.",
            (
                "data/generated/scientific_genesis/"
                "published_constituent_deck_actions.json",
                "research/experiments/computable_carrier/dp9_serre_actions.py",
                "tests/integration/"
                "test_scientific_genesis_published_constituent_deck_actions.py",
            ),
            ("published constituent equivariant representations",),
        ),
        _node(
            "published_constituent_ray_alignment",
            "source-selected mixed constituent rays",
            "Reference realization",
            "COMPUTED",
            "Pulling the selected W1/W2 rays through the exact intertwiners "
            "gives nontrivial-character mixed Ext cocycles with necessary "
            "syzygy/Koszul edge components.",
            (
                "data/generated/scientific_genesis/"
                "published_constituent_ray_alignment.json",
                "research/experiments/scientific_genesis/"
                "published_constituent_ray_alignment.py",
                "tests/integration/"
                "test_scientific_genesis_published_constituent_ray_alignment.py",
            ),
            ("source-selected Serre ray coordinates",),
        ),
        _node(
            "published_constituent_full_cech",
            "selected mixed constituent full-Cech cocycles",
            "Reference realization",
            "COMPUTED",
            "Finite homological perturbation lifts both selected mixed rays to "
            "the complete P2 x P1 standard cover, where their raw total "
            "differentials vanish exactly.",
            (
                "data/generated/scientific_genesis/"
                "published_constituent_full_cech.json",
                "research/experiments/scientific_genesis/"
                "published_constituent_full_cech.py",
                "tests/integration/"
                "test_scientific_genesis_published_constituent_full_cech.py",
            ),
        ),
        _node(
            "published_constituent_local_units",
            "selected constituent local dualizing units",
            "Reference realization",
            "PROVED",
            "At every I3/I6 support point, the selected parent-one map spans "
            "the one-dimensional local Ext residue. Both fiber charts give "
            "the same nonzero unit modulo Hilbert--Burch boundaries.",
            (
                "data/generated/scientific_genesis/"
                "published_constituent_local_units.json",
                "research/experiments/scientific_genesis/"
                "published_constituent_local_units.py",
                "tests/integration/"
                "test_scientific_genesis_published_constituent_local_units.py",
            ),
            ("finite lci Gorenstein support algebra",),
        ),
        _node(
            "published_constituent_overlap_atlases",
            "selected constituent global cover atlases",
            "Reference realization",
            "COMPUTED",
            "Twelve affine rank-two pushouts are locally free on support and "
            "complement. Sixty ordered overlap maps preserve the relations "
            "modulo the dP9 equation and obey every cocycle law.",
            (
                "data/generated/scientific_genesis/"
                "published_constituent_chart_presentations.json",
                "data/generated/scientific_genesis/"
                "published_constituent_overlap_transitions.json",
                "research/experiments/scientific_genesis/"
                "published_constituent_overlap_transitions.py",
                "tests/integration/"
                "test_scientific_genesis_published_constituent_overlap_transitions.py",
            ),
        ),
        _node(
            "published_constituent_deck_atlases",
            "selected constituent deck-linearized atlases",
            "Reference realization",
            "COMPUTED",
            "Local line-frame factors turn semilinear P/T resolution maps into "
            "exact W1/W2 comparisons. Relation, overlap, order-three, and "
            "commutation gates all close.",
            (
                "data/generated/scientific_genesis/"
                "published_constituent_deck_atlases.json",
                "research/experiments/scientific_genesis/"
                "published_constituent_deck_atlases.py",
                "tests/integration/"
                "test_scientific_genesis_published_constituent_deck_atlases.py",
            ),
            ("source-bound constituent equivariant structures",),
        ),
        _node(
            "mixed_constituent_schoen_arrows",
            "selected mixed arrows in the common Schoen cover",
            "Reference realization",
            "COMPUTED",
            "The complete V1/V2 extension cocycles occupy the synchronized "
            "Schoen grading with 216 and 351 sparse terms after exact pullback "
            "over the unused factor. Degree, multidegree, "
            "regularity, closure, and deck-character gates all close.",
            (
                "data/generated/scientific_genesis/"
                "mixed_constituent_schoen_arrows.json",
                "research/experiments/scientific_genesis/"
                "mixed_constituent_schoen_arrows.py",
                "tests/integration/"
                "test_scientific_genesis_mixed_constituent_schoen_arrows.py",
            ),
        ),
        _node(
            "mixed_schoen_outer_transfer",
            "selected mixed outer-Hom cover transfer",
            "Reference realization",
            "COMPUTED",
            "Alexander--Whitney and Koszul convolution gives square-zero "
            "cover cohomology 18/54 forward and 54/18 reverse without using "
            "source outer dimensions as rank inputs.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_outer_transfer.json",
                "research/experiments/scientific_genesis/"
                "mixed_schoen_outer_transfer.py",
                "tests/integration/"
                "test_scientific_genesis_mixed_schoen_outer_transfer.py",
            ),
        ),
        _node(
            "mixed_schoen_outer_actions",
            "selected mixed outer quotient actions",
            "Reference realization",
            "COMPUTED",
            "Exact perturbed P/T transfer gives commuting order-three actions "
            "with fixed dimensions 2 forward and 6 reverse. Reynolds "
            "averaging produces strict full-Cech representatives without "
            "selecting an extension coordinate.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_outer_actions.json",
                "research/experiments/scientific_genesis/"
                "mixed_schoen_outer_actions.py",
                "tests/integration/"
                "test_scientific_genesis_mixed_schoen_outer_actions.py",
            ),
        ),
        _node(
            "mixed_schoen_outer_universal_cone",
            "lawful mixed universal outer cone",
            "Reference realization",
            "COMPUTED",
            "The two strict forward invariant classes form an exact universal "
            "rank-four cone over P1(Q(omega)). Its split locus is the affine "
            "origin; local freeness, topology, and descent are parameter "
            "independent, with no projective point selected.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_outer_universal_cone.json",
                "research/experiments/scientific_genesis/"
                "mixed_schoen_outer_universal_cone.py",
                "tests/integration/"
                "test_scientific_genesis_mixed_schoen_outer_universal_cone.py",
            ),
        ),
        _node(
            "mixed_schoen_reverse_outer_universal_cone",
            "lawful reverse mixed universal outer cone",
            "Reference realization",
            "COMPUTED",
            "The six strict reverse invariant classes form an exact universal "
            "rank-four cone over P5(Q(omega)). Its split locus is the affine "
            "origin; local freeness, topology, and descent are parameter "
            "independent. No projective point or stable locus is selected.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_reverse_outer_universal_cone.json",
                "research/experiments/scientific_genesis/"
                "mixed_schoen_reverse_outer_universal_cone.py",
                "tests/integration/"
                "test_scientific_genesis_mixed_schoen_reverse_outer_universal_cone.py",
            ),
            missing=(
                "exact reverse stable locus",
                "exclusion of accidental proper structure-group reductions",
            ),
        ),
        _node(
            "mixed_schoen_reverse_outer_stability_locus",
            "lawful reverse equivariant stability locus",
            "Reference realization",
            "PROVED",
            "The extension lower bound preserves all eight proper-subsheaf "
            "inequalities under reversal and replaces only the forced full "
            "subobject V1 by V2. All nine exact slopes are negative on a "
            "rational open box around (3,2,2), so every reverse P5 point is "
            "equivariantly stable there; nonzero cover c3 excludes proper "
            "connected irreducible rank-four reduction. Ordinary stability "
            "of the underlying cover bundle is not inferred.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_reverse_outer_stability_locus.json",
                "research/experiments/scientific_genesis/"
                "mixed_schoen_reverse_outer_stability_locus.py",
                "tests/integration/"
                "test_scientific_genesis_mixed_schoen_reverse_outer_stability_locus.py",
            ),
        ),
        _node(
            "selected_atlas_common_frame_comparison",
            "selected atlas-to-common chain-frame comparison",
            "Computable carrier",
            "COMPUTED",
            "The first constituent's native fiber lift differs by a uniform "
            "homogeneous scalar. After Koszul correction, its mixed action "
            "equals the atlas-bound action times character (2,0) on every "
            "full summand. The second constituent uses inverse-generator "
            "atlas actions with no extra character. This is a constituent "
            "frame relation, not a descended rank-four determinant repair.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_atlas_frame_comparison.json",
                "research/experiments/scientific_genesis/"
                "mixed_schoen_atlas_frame_comparison.py",
                "tests/integration/"
                "test_scientific_genesis_mixed_schoen_atlas_frame_comparison.py",
            ),
        ),
        _node(
            "selected_mixed_determinant_descent",
            "selected mixed quotient determinant descent",
            "Computable carrier",
            "REFUTED",
            "The selected constituent frames have cancelling cover line degrees "
            "but total equivariant determinant character (2,1). The scalar "
            "top class has the same nontrivial framed character. Exact cross-Hom "
            "vanishing and constituent simplicity make every nonsplit selected "
            "extension simple, so the unique determinant-cancelling twist "
            "exhausts same-bundle relinearizations. It fails the fixed Wilson "
            "spectrum. The atlas/common-frame discrepancy is a uniform "
            "constituent character after homogeneous-lift conversion, not a "
            "one-entry repair. A distinct published carrier is not refuted.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_determinant_descent.json",
                "research/experiments/scientific_genesis/"
                "mixed_schoen_determinant_descent.py",
                "tests/integration/"
                "test_scientific_genesis_mixed_schoen_determinant_descent.py",
            ),
        ),
        _node(
            "published_constituent_mapping_cones",
            "trivial-character constituent mapping cones",
            "Reference realization",
            "REFUTED",
            "The pure maximal-minor Cech cones select the trivial kernel "
            "character. The source-selected rays have different characters "
            "and nonzero edge components, so these are not W1/W2 chain models.",
            (
                "data/generated/scientific_genesis/"
                "published_constituent_mapping_cones.json",
                "data/generated/scientific_genesis/"
                "published_constituent_ray_alignment.json",
            ),
        ),
        _node(
            "published_outer_reduced_model",
            "retired trivial-ray outer reduced diagnostic",
            "Reference realization",
            "COMPUTED",
            "The retired cones give exact square-zero reduced dimensions "
            "126/162 and 162/126. This diagnostic is not the selected W1/W2 "
            "outer complex.",
            (
                "data/generated/scientific_genesis/"
                "published_outer_reduced_mismatch.json",
                "research/experiments/computable_carrier/schoen_serre_outer.py",
            ),
        ),
        _node(
            "published_outer_cech_transfer",
            "retired trivial-ray full-Cech outer diagnostic",
            "Reference realization",
            "COMPUTED",
            "Full-Cech transfer gives dimensions 36/72 and 72/36 for the "
            "retired cones. Matching source dimensions does not identify "
            "wrong-character chain objects with W1/W2.",
            (
                "data/generated/scientific_genesis/"
                "published_outer_cech_transfer.json",
                "research/experiments/computable_carrier/"
                "schoen_serre_outer_transfer.py",
            ),
        ),
        _node(
            "published_outer_cech_invariants",
            "retired trivial-ray outer invariant diagnostic",
            "Reference realization",
            "COMPUTED",
            "Transferred deck actions give fixed dimensions four and eight for "
            "the retired cones. Their strict representatives are not published "
            "outer classes.",
            (
                "data/generated/scientific_genesis/"
                "published_outer_cech_invariants.json",
                "research/experiments/computable_carrier/"
                "schoen_serre_outer_transfer_actions.py",
            ),
        ),
        _node(
            "published_outer_universal_cone",
            "retired trivial-ray universal outer cone",
            "Reference realization",
            "COMPUTED",
            "Four strict retired classes form an internally exact universal "
            "rank-four cone. Its algebraic gates do not make it the published "
            "carrier family.",
            (
                "data/generated/scientific_genesis/"
                "published_outer_universal_cone.json",
                "research/experiments/scientific_genesis/"
                "published_outer_universal_cone.py",
            ),
        ),
        _node(
            "published_outer_stability_locus",
            "lawful mixed equivariant stability locus",
            "Reference realization",
            "COMPUTED",
            "The published sufficient slope bounds depend only on constituent "
            "subsheaves and nonsplitting. Every lawful P1 point is nonsplit, so "
            "all are equivariantly stable in the exact chamber; nonzero cover "
            "c3 excludes proper connected irreducible structure-group "
            "reductions. Cover-bundle simplicity is established separately.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_outer_stability_locus.json",
                "research/experiments/scientific_genesis/"
                "mixed_schoen_outer_stability_locus.py",
                "tests/integration/"
                "test_scientific_genesis_mixed_schoen_outer_stability_locus.py",
                "data/published/visible_carrier/source_manifest.json",
            ),
            (
                "published nontrivial-extension stability theorem",
                "Donaldson--Uhlenbeck--Yau correspondence",
            ),
        ),
        _node(
            "published_matter_cohomology",
            "published universal-family matter cohomology",
            "Reference realization",
            "BLOCKED",
            "The source ledger expects three regular representations and no "
            "anti-families, but generated representatives used retired cones. "
            "They must be recomputed from the mixed atlases.",
            (
                "data/generated/scientific_genesis/"
                "published_matter_cohomology.json",
                "research/experiments/scientific_genesis/"
                "published_matter_cohomology.py",
            ),
            ("published Wilson-line embedding", "Calabi--Yau Serre duality"),
            missing=(
                "mixed-constituent synchronized matter transfer",
                "strict deck-equivariant matter representatives",
            ),
        ),
        _node(
            "published_higgs_cohomology",
            "published universal-family Higgs cohomology",
            "Reference realization",
            "BLOCKED",
            "Relative signatures now bind the selected mixed local units and "
            "recover the source tuple (0,4,4,0). Four lawful P1 classes still "
            "require explicit mixed diagonal Schoen lifts.",
            (
                "data/generated/scientific_genesis/"
                "published_higgs_cohomology.json",
                "data/generated/scientific_genesis/"
                "relative_constituent_pushdowns.json",
                "data/generated/scientific_genesis/diagonal_higgs_actions.json",
            ),
            ("relative duality", "published Wilson-line embedding"),
            missing=(
                "mixed constituent relative chain quasi-isomorphisms",
                "four full diagonal Schoen Cech representatives",
                "strict deck action on the lifted Higgs classes",
            ),
        ),
        _node(
            "distinct_constituent_ray_screen",
            "unused locally free Serre Ext rays",
            "Computable carrier",
            "COMPUTED",
            "The fixed I3/I6 presentations have seven one-dimensional joint "
            "Ext-character sectors. Full Cech lifts and exact local residue "
            "tests leave two unused I6 rays with local dualizing units. Their "
            "second deck characters cannot alone repair the selected quotient "
            "determinant. Their relinearized descent and Higgs data are open.",
            (
                "data/generated/scientific_genesis/"
                "distinct_constituent_ray_screen.json",
                "research/experiments/scientific_genesis/"
                "distinct_constituent_ray_screen.py",
                "tests/integration/"
                "test_scientific_genesis_distinct_constituent_ray_screen.py",
            ),
            ("fixed I3/I6 schemes", "source-aligned exact Ext action"),
            ("alternate common-Schoen outer action and quotient determinants",),
        ),
        _node(
            "alternate_constituent_cover_h1",
            "cover Higgs cohomology for unused I6 rays",
            "Computable carrier",
            "COMPUTED",
            "Each of the two unused locally free I6 Ext rays has exact cover "
            "H1 dimension four in Hom(V2 tensor det(V1), V1). This "
            "does not supply alternate descent, deck characters, or Wilson "
            "projection.",
            (
                "data/generated/scientific_genesis/"
                "alternate_constituent_higgs_dimensions.json",
                "research/experiments/scientific_genesis/"
                "alternate_constituent_higgs_dimensions.py",
                "tests/integration/"
                "test_scientific_genesis_alternate_constituent_higgs_dimensions.py",
            ),
            ("fixed I3/I6 presentations", "exact mixed Schoen transfer"),
            ("determinant-trivial carrier", "physical tensor comparison"),
        ),
        _node(
            "alternate_constituent_deck_atlases",
            "deck atlases for unused I6 rays",
            "Computable carrier",
            "COMPUTED",
            "Both unused locally free I6 rays have exact overlap cocycles "
            "and P/T deck comparisons. Neither selected mixed P-frame "
            "formula is uniformly related to its alternate atlas frame; "
            "the old P-determinant shortcut is not a quotient certificate.",
            (
                "data/generated/scientific_genesis/"
                "alternate_constituent_deck_atlases.json",
                "research/experiments/scientific_genesis/"
                "alternate_constituent_deck_atlases.py",
                "tests/integration/"
                "test_scientific_genesis_alternate_constituent_deck_atlases.py",
            ),
            ("fixed I3/I6 presentations", "exact homogeneous chart actions"),
            ("outer extension equivariance", "other constituent linearisations"),
        ),
        _node(
            "alternate_constituent_determinant_obstruction",
            "fixed-atlas determinant obstruction for unused I6 rays",
            "Computable carrier",
            "COMPUTED",
            "Both unused I6 rays have cover-trivial total determinant degree, "
            "but the exact common-frame and scalar-H3 characters are (2,1) "
            "and (0,1). Any equivariant outer extension preserving either "
            "fixed atlas pair therefore fails quotient SU(4).",
            (
                "data/generated/scientific_genesis/"
                "alternate_constituent_determinant_descent.json",
                "research/experiments/scientific_genesis/"
                "alternate_constituent_determinant_descent.py",
                "tests/integration/"
                "test_scientific_genesis_alternate_constituent_determinant_descent.py",
            ),
            ("fixed exact atlas linearisations", "equivariant determinant multiplicativity"),
            ("other linearisations", "distinct underlying constituent bundles"),
        ),
        _node(
            "alternate_constituent_hom_cycle_actions",
            "cover Hom cohomology actions for unused I6 rays",
            "Computable carrier",
            "COMPUTED",
            "Atlas-derived frames preserve all 129 independent cover Hom "
            "boundaries for each generator and ray. The resulting H1 matrices "
            "satisfy the P/T group laws. Raw characters still require the "
            "total determinant shift and do not supply Higgs cocycles.",
            (
                "data/generated/scientific_genesis/"
                "alternate_constituent_hom_actions.json",
                "research/experiments/scientific_genesis/"
                "alternate_constituent_hom_actions.py",
                "tests/integration/"
                "test_scientific_genesis_alternate_constituent_hom_actions.py",
            ),
            ("fixed alternate ray atlases", "declared determinant-twist line action"),
            ("explicit tensor cocycle map", "determinant-trivial carrier"),
        ),
        _node(
            "alternate_constituent_character_screen",
            "conditional determinant-repaired Higgs character screen",
            "Computable carrier",
            "COMPUTED",
            "The rank-two equivariant Hom identity and acyclic determinant "
            "filtration show that, if an equivariant outer extension exists, "
            "the unique common determinant repair gives ray (0,1) one Higgs "
            "pair without triplets. Ray (1,1) retains both triplet sectors. "
            "No outer cone or physical Higgs cocycle is constructed.",
            (
                "data/generated/scientific_genesis/"
                "alternate_constituent_character_screen.json",
                "research/experiments/scientific_genesis/"
                "alternate_constituent_character_screen.py",
                "tests/integration/"
                "test_scientific_genesis_alternate_constituent_character_screen.py",
            ),
            ("exact alternate Hom action", "fixed Wilson weights", "acyclic determinant lines"),
            ("universal cone", "stability", "Higgs cocycles"),
        ),
        _node(
            "alternate_constituent_outer_cover_ext",
            "cover outer Ext for the surviving I6 ray",
            "Computable carrier",
            "COMPUTED",
            "For ray (0,1), the exact outer Hom(V2,V1) transfer has reduced "
            "dimensions (1512,4536,4824), differential ranks (1512,3006), "
            "square-zero differential, H0 dimension zero, and cover Ext1 "
            "dimension 18. No invariant Ext class or cone is claimed.",
            (
                "data/generated/scientific_genesis/"
                "alternate_constituent_outer_ext.json",
                "research/experiments/scientific_genesis/"
                "alternate_constituent_outer_ext.py",
                "tests/integration/"
                "test_scientific_genesis_alternate_constituent_outer_ext.py",
            ),
            ("ray (0,1) exact constituent", "mixed Schoen outer transfer"),
            ("deck-invariant Ext basis", "equivariant universal cone"),
        ),
        _node(
            "alternate_constituent_outer_invariants",
            "strict invariant outer Ext for the surviving I6 ray",
            "Computable carrier",
            "COMPUTED",
            "Exact full-Cech Reynolds averaging of all 18 cover classes "
            "gives a two-dimensional invariant Ext1(V2,V1) space for ray "
            "(0,1). Two independent full representatives are closed and "
            "strictly P/T fixed. No extension point, universal cone, or "
            "stability chamber is claimed.",
            (
                "data/generated/scientific_genesis/"
                "alternate_constituent_outer_invariants.json",
                "research/experiments/scientific_genesis/"
                "alternate_constituent_outer_invariants.py",
                "tests/integration/"
                "test_scientific_genesis_alternate_constituent_outer_invariants.py",
            ),
            ("exact cover Ext basis", "fixed ray (0,1) deck atlas"),
            ("universal equivariant outer cone", "lawful stable locus"),
        ),
        _node(
            "alternate_constituent_outer_universal_cone",
            "determinant-repaired universal outer cone for ray (0,1)",
            "Computable carrier",
            "COMPUTED",
            "The two strict invariant cocycles assemble parameter-linearly "
            "over A2 with split origin and non-split P1. Exact local units "
            "give local freeness; the fixed atlas gives descent; the unique "
            "common flat-character twist cancels the quotient determinant. "
            "The alternate graded K-class matches the selected constituent "
            "pair, so rational Chern data agree. Stability, genuine SU(4), "
            "and physical Higgs cocycles remain unresolved.",
            (
                "data/generated/scientific_genesis/"
                "alternate_constituent_outer_universal_cone.json",
                "research/experiments/scientific_genesis/"
                "alternate_constituent_outer_universal_cone.py",
                "tests/integration/"
                "test_scientific_genesis_alternate_constituent_outer_universal_cone.py",
            ),
            ("strict invariant Ext basis", "alternate local units", "fixed deck atlas"),
            ("parameterwise stable locus", "genuine SU(4)", "physical Higgs cocycles"),
        ),
        _node(
            "alternate_constituent_outer_stability_locus",
            "source-scoped stable SU(4) chamber for the alternate P1",
            "Computable carrier",
            "COMPUTED",
            "The alternate Serre ray has the same subline and I3/I6 ideal "
            "quotients as the published presentation. The published "
            "non-split extension bound therefore supplies the same nine "
            "sufficient slope inequalities for every nonzero P1 class. "
            "An exact rational open box satisfies them; nonzero cover c3 "
            "excludes proper connected irreducible reductions. The complete "
            "Kahler stable cone remains unresolved; spectrum is a separate gate.",
            (
                "data/generated/scientific_genesis/"
                "alternate_constituent_outer_stability_locus.json",
                "research/experiments/scientific_genesis/"
                "alternate_constituent_outer_stability_locus.py",
                "research/experiments/scientific_genesis/"
                "ALTERNATE_STABILITY_NOTE.md",
                "tests/integration/"
                "test_scientific_genesis_alternate_constituent_outer_stability_locus.py",
            ),
            ("non-split alternate P1", "fixed Serre ideals", "published sufficient bound"),
            ("matter/Higgs cocycles",),
        ),
        _node(
            "alternate_constituent_matter_profile",
            "exact cover matter profile of the stable alternate P1",
            "Computable carrier",
            "COMPUTED",
            "The alternate I6 mixed transfer has exact differential ranks "
            "189 and 81, giving pure H1 of dimension 18. The unchanged first "
            "constituent contributes pure H1 of dimension 9, so every "
            "nonzero outer class has cover profile (0,27,0,0). Free-action "
            "Lefschetz then gives three regular deck modules, independently "
            "of the common flat determinant repair. Explicit cone matter "
            "and Higgs cocycles remain absent.",
            (
                "data/generated/scientific_genesis/"
                "alternate_constituent_matter_profile.json",
                "research/experiments/scientific_genesis/"
                "alternate_constituent_matter_profile.py",
                "tests/integration/"
                "test_scientific_genesis_alternate_constituent_matter_profile.py",
            ),
            ("exact alternate cone", "free Schoen quotient"),
            ("explicit matter/Higgs cocycles",),
        ),
        _node(
            "alternate_constituent_structural_spectrum",
            "all-parameter charged spectrum of the alternate carrier",
            "Computable carrier",
            "COMPUTED",
            "The natural rank-two Hom-to-tensor identity plus the acyclic "
            "determinant filtration transports the exact four-character "
            "Hom action to Higgs H1 for every alternate P1 class. After "
            "the unique flat determinant repair, the fixed published "
            "Wilson line retains one Higgs pair and no color triplets. "
            "Three regular matter modules give three families and no "
            "anti-families. Explicit chain cocycles remain uncomputed.",
            (
                "data/generated/scientific_genesis/"
                "alternate_constituent_structural_spectrum.json",
                "research/experiments/scientific_genesis/"
                "alternate_constituent_structural_spectrum.py",
                "research/experiments/scientific_genesis/"
                "ALTERNATE_SPECTRUM_NOTE.md",
                "tests/integration/"
                "test_scientific_genesis_alternate_constituent_structural_spectrum.py",
            ),
            ("published Wilson embedding", "selected heterotic realization"),
            ("strict matter/Higgs cocycles", "Yukawa matrix", "bundle moduli"),
        ),
        _node(
            "alternate_constituent_carrier_state",
            "frozen alternate computable carrier component",
            "Computable carrier",
            "COMPUTED",
            "The entire nonzero alternate P1 component is bound to exact "
            "cone, stable-chamber, Hom-action, and charged-spectrum "
            "certificates. No projective coordinate is selected and the "
            "published P3 reference is kept distinct. The freeze is for "
            "chain-level physics, not a completed vacuum.",
            (
                "data/generated/scientific_genesis/"
                "alternate_constituent_carrier_state.json",
                "research/experiments/scientific_genesis/"
                "alternate_constituent_carrier_state.py",
                "tests/integration/"
                "test_scientific_genesis_alternate_constituent_carrier_state.py",
            ),
            ("source-scoped stability chamber", "published Wilson embedding"),
            ("strict same-cone cocycles", "holomorphic Yukawa matrix"),
        ),
        _node(
            "alternate_constituent_up_matter_representatives",
            "strict I6 matter representatives for the alternate up-type slice",
            "Computable carrier",
            "COMPUTED",
            "Exact full Cech cycles in the alternate I6 atlas give two "
            "independent H1 classes in each constituent character (0,0) "
            "and (1,0). The common flat twist maps these to the fixed "
            "Wilson up-spinor sectors (1,2) and (2,2). These are not yet "
            "classes of the outer rank-four cone.",
            (
                "data/generated/scientific_genesis/"
                "alternate_constituent_up_matter_representatives.json",
                "research/experiments/scientific_genesis/"
                "alternate_constituent_up_matter_representatives.py",
                "tests/integration/"
                "test_scientific_genesis_alternate_constituent_up_matter_representatives.py",
            ),
            ("published Wilson weights", "certified alternate atlas frames"),
            ("outer-cone correction cocycles", "physical Higgs class"),
        ),
        _node(
            "alternate_constituent_up_cone_matter_lifts",
            "universal up-sector matter classes on the alternate cone",
            "Computable carrier",
            "COMPUTED",
            "The alternate atlas yields one strict I3 class in each needed "
            "sector. Eight exact parameter-linear I3 corrections lift the "
            "four strict I6 classes through both invariant outer basis "
            "directions, giving three up-sector matter classes per "
            "character throughout the frozen non-split P1. The physical "
            "Higgs chain class and Yukawa pairing remain uncomputed.",
            (
                "data/generated/scientific_genesis/"
                "alternate_constituent_up_cone_matter_lifts.json",
                "research/experiments/scientific_genesis/"
                "alternate_constituent_up_cone_matter_lifts.py",
                "tests/integration/"
                "test_scientific_genesis_alternate_up_cone_matter_lifts.py",
            ),
            ("certified alternate atlas", "fixed published Wilson sectors"),
            ("same-cone Higgs cocycle", "holomorphic Yukawa matrix"),
        ),
        _node(
            "alternate_up_higgs_hom_representative",
            "strict alternate Hom class for the up-Higgs sector",
            "Computable carrier",
            "COMPUTED",
            "A 324-term exact full-Cech Hom cycle has nonzero H1 class and "
            "strict atlas character (2,0). Its complete terms are saved "
            "with a checked round trip. All six right singleton restrictions "
            "are closed and supported only in syzygy-dual objects; middle "
            "terms occur on overlaps. The certified determinant and "
            "common flat frames send this character to the selected "
            "up-Higgs forward sector (0,2). No tensor chain map or "
            "exterior-cone Higgs cocycle is asserted.",
            (
                "data/generated/scientific_genesis/"
                "alternate_up_higgs_hom_representative.json",
                "data/generated/scientific_genesis/"
                "alternate_up_higgs_hom_full_cochain.json",
                "data/generated/scientific_genesis/"
                "alternate_up_higgs_chart_restriction.json",
                "research/experiments/scientific_genesis/"
                "alternate_up_higgs_hom_representative.py",
                "research/experiments/scientific_genesis/"
                "alternate_up_higgs_chart_restriction.py",
                "tests/integration/"
                "test_scientific_genesis_alternate_up_higgs_hom_representative.py",
                "tests/integration/"
                "test_scientific_genesis_alternate_up_higgs_hom_full_cochain.py",
                "tests/integration/"
                "test_scientific_genesis_alternate_up_higgs_chart_restriction.py",
            ),
            ("certified Hom action", "selected published Wilson sector"),
            ("rank-two determinant chain map", "exterior-cone Higgs lift"),
        ),
        _node(
            "alternate_up_yoneda_evaluation",
            "nonzero alternate mixed-family Yoneda evaluations",
            "Flavor",
            "COMPUTED",
            "The actual strict 324-term Hom class composes with each of four "
            "strict I6 classes to a 207-term full degree-two cycle. Exact "
            "reduced projections are nonboundaries. Within each fixed "
            "matter character, the two images are exactly proportional "
            "with basis-dependent ratios (2-omega)/7 and (-3-2omega)/7. "
            "No scalar Yukawa entry or exterior-cone Higgs cocycle is claimed.",
            (
                "data/generated/scientific_genesis/"
                "alternate_up_yoneda_evaluation.json",
                "research/experiments/scientific_genesis/"
                "alternate_up_yoneda_evaluation.py",
                "research/experiments/scientific_genesis/"
                "mixed_outer_yoneda.py",
                "research/experiments/scientific_genesis/"
                "ALTERNATE_UP_YONEDA_ROUTE_NOTE.md",
                "tests/integration/"
                "test_scientific_genesis_mixed_outer_yoneda.py",
            ),
            (
                "strict alternate Hom and I6 matter cochains",
                "acyclic determinant endpoints",
                "declared common flat frame",
            ),
            (
                "determinant contraction with strict I3 matter",
                "exact scalar residue",
                "same-cone Higgs representative for the F-F block",
            ),
        ),
        _node(
            "alternate_up_mixed_scalar_trace",
            "exact alternate mixed up-sector cover residues",
            "Flavor",
            "COMPUTED",
            "The actual first-constituent Pluecker form contracts four "
            "strict I3/degree-two Yoneda pairs to 2,257-term full scalar "
            "cycles. Their ordered cover residues are 3omega/2, "
            "(3+9omega)/14, 3/2, and (-9-6omega)/14. Reverse cup order "
            "gives the negative residue and both Yoneda ratios agree. "
            "This is the earlier cover-frame certificate, not the final "
            "Higgs-first quotient normalization.",
            (
                "data/generated/scientific_genesis/"
                "alternate_up_mixed_scalar_trace.json",
                "research/experiments/scientific_genesis/"
                "alternate_up_mixed_scalar_trace.py",
                "research/experiments/scientific_genesis/"
                "ALTERNATE_UP_MIXED_TRACE_NOTE.md",
                "tests/integration/"
                "test_scientific_genesis_alternate_up_mixed_scalar_trace.py",
            ),
            (
                "frozen alternate carrier",
                "saved unnormalized cochain bases",
                "ordered cover Laurent residue generator has trace one",
            ),
        ),
        _node(
            "alternate_up_rank_floor",
            "rank-two floor of the alternate holomorphic up matrix",
            "Flavor",
            "DERIVED",
            "Exterior degree forces the E-E slot to zero. The four exact "
            "mixed cover residues give four nonzero two-by-two minors "
            "independent of the F-F block and outer coordinates. "
            "Every nonsplit point has holomorphic up rank at least two. "
            "The later complete matrix sharpens this bound.",
            (
                "data/generated/scientific_genesis/alternate_up_rank_floor.json",
                "research/experiments/scientific_genesis/alternate_up_rank_floor.py",
                "research/experiments/scientific_genesis/ALTERNATE_UP_RANK_FLOOR_NOTE.md",
                "tests/integration/"
                "test_scientific_genesis_alternate_up_rank_floor.py",
            ),
            (
                "frozen nonsplit alternate P1 family",
                "ordered unnormalized cover bases",
                "acyclic determinant filtration",
            ),
        ),
        _node(
            "alternate_up_null_channel",
            "exact alternate up null-channel homotopies",
            "Flavor",
            "COMPUTED",
            "The two exact mixed blocks select one null F combination per "
            "Wilson sector. Their 144-term full Yoneda evaluations are "
            "boundaries with 90-term exact primitives. A formal determinant "
            "identity reduces the rank-three decision to two extension-linear "
            "null-to-null F-F coefficients. Separate complete ordered scalar "
            "screens now evaluate those directions; their physical tensor "
            "identification remains a distinct gate.",
            (
                "data/generated/scientific_genesis/alternate_up_null_channel.json",
                "research/experiments/scientific_genesis/alternate_up_null_channel.py",
                "research/experiments/scientific_genesis/ALTERNATE_UP_NULL_CHANNEL_NOTE.md",
                "tests/integration/"
                "test_scientific_genesis_alternate_up_null_channel.py",
            ),
            ("declared ordered cover convention", "frozen nonsplit P1"),
            ("physical identification of the ordered null scalars",),
        ),
        _node(
            "alternate_up_dual_higgs_inputs",
            "reciprocal covectors for the first-order alternate Higgs action",
            "Flavor",
            "COMPUTED",
            "The global Hilbert-Burch A-line pairing kills syzygies exactly. "
            "Its quotient sends both outer basis classes to independent "
            "nonboundary covectors F to B1. The saved A-supported Higgs "
            "retargets to F to B1 inverse with unchanged full grading. "
            "A separate exterior calculation now checks the ordered products "
            "and their full primitives; these input records alone do not "
            "supply the complete first-order scalar.",
            (
                "data/generated/scientific_genesis/alternate_up_dual_higgs_inputs.json",
                "research/experiments/scientific_genesis/alternate_up_dual_higgs_inputs.py",
                "research/experiments/scientific_genesis/ALTERNATE_UP_DUAL_HIGGS_INPUTS_NOTE.md",
                "data/generated/scientific_genesis/alternate_up_null_shortcut_screen.json",
                "tests/integration/test_scientific_genesis_alternate_up_dual_higgs_inputs.py",
            ),
            ("actual frozen alternate resolutions", "declared determinant orientation"),
            ("physical quotient-cone comparison", "complete F-F block"),
        ),
        _node(
            "alternate_up_exterior_higgs_action",
            "checked reciprocal exterior primitives for the alternate up sector",
            "Flavor",
            "COMPUTED",
            "The actual F resolution has a 31-object graded exterior square "
            "with ordinary odd monomials. All 124 full square-zero witnesses "
            "pass. Both ordered h-wedge-q(e) products are full cycles with "
            "independently checked degree-one primitives. A selectively "
            "transferred candidate aids the solve but is not itself a global "
            "operator certificate. Both signed slot compositions and a "
            "natural ideal-quotient cone now reproduce these identities. "
            "Identification with the physical exterior pairing is separate.",
            (
                "data/generated/scientific_genesis/alternate_up_exterior_higgs_action.json",
                "research/experiments/scientific_genesis/alternate_up_exterior_higgs_action.py",
                "research/experiments/scientific_genesis/mixed_schoen_exterior_square.py",
                "research/experiments/scientific_genesis/ALTERNATE_UP_EXTERIOR_HIGGS_ACTION_NOTE.md",
                "tests/integration/test_scientific_genesis_alternate_up_exterior_higgs_action.py",
                "tests/integration/test_scientific_genesis_mixed_exterior_square.py",
            ),
            ("frozen alternate F", "ordered full-cover cup", "ordinary odd-square basis"),
            ("physical exterior pairing and quotient trace",),
        ),
        _node(
            "alternate_up_higgs_quotient_cone",
            "natural coherent quotient cone for the alternate Higgs",
            "Flavor",
            "COMPUTED",
            "The actual A-section quotient gives K=B1 tensor I6 B2 with "
            "seven objects and six arrows, not an additional vector bundle. "
            "Both full connecting arrows are closed; their signed Higgs "
            "actions match the pinned exterior primitive differentials. "
            "The raw null tensor differences lie entirely in the actual "
            "A target, so their projections vanish before applying h. "
            "This certifies the triangular quotient cone, not an arbitrary "
            "exterior-V cochain map or a normalized physical coupling.",
            (
                "data/generated/scientific_genesis/alternate_up_higgs_quotient_cone.json",
                "research/experiments/scientific_genesis/alternate_up_higgs_quotient_cone.py",
                "research/experiments/scientific_genesis/alternate_up_higgs_covector_comparison.py",
                "research/experiments/scientific_genesis/ALTERNATE_UP_FIRST_ORDER_SCALAR_NOTE.md",
                "tests/integration/test_scientific_genesis_alternate_up_higgs_quotient_cone.py",
            ),
            ("global first quotient", "full pinned primitive identities", "actual Serre quotient"),
            ("physical exterior-V cochain comparison", "equivariant Higgs normalization"),
        ),
        _node(
            "alternate_up_first_order_scalar",
            "complete ordered alternate null-channel scalar screens",
            "Flavor",
            "COMPUTED",
            "Both parameter coefficients include both matter-leg terms "
            "and the positive signed Higgs primitive. Each complete scalar "
            "is checked under the full differential before its exact "
            "ordered cover residue is evaluated. A primitive-free tensor "
            "calculation independently accounts for its zero defect. "
            "The ordered residues are 0 and (2673-486 omega)/49; the a1 "
            "coefficient is nonzero in the exact field. "
            "Closed screens are not assigned as physical null coefficients "
            "or as a permanent physical rank bound.",
            (
                "data/generated/scientific_genesis/alternate_up_first_order_scalar.json",
                "research/experiments/scientific_genesis/alternate_up_first_order_scalar.py",
                "research/experiments/scientific_genesis/ALTERNATE_UP_FIRST_ORDER_SCALAR_NOTE.md",
                "tests/integration/test_scientific_genesis_alternate_up_first_order_scalar.py",
                "tests/integration/test_scientific_genesis_alternate_up_higgs_covector_comparison.py",
            ),
            ("fixed null matter basis", "literal ordered cover cup", "checked positive k sign"),
            ("physical pairing identification", "quotient trace convention", "complete up matrix"),
        ),
        _node(
            "alternate_up_quotient_equivariance",
            "inherited quotient linearization and up-Higgs character",
            "Flavor",
            "COMPUTED",
            "The full 54-term global minor row forces B1 frames omega and 1. "
            "The inherited quotient Higgs retains its native (2,0) character; "
            "both complete connecting arrows are strictly P/T fixed. The "
            "common flat determinant repair gives covector character (0,2), "
            "also the forward Higgs character. No line phase is fitted.",
            (
                "data/generated/scientific_genesis/alternate_up_quotient_equivariance.json",
                "research/experiments/scientific_genesis/alternate_up_quotient_equivariance.py",
                "research/experiments/scientific_genesis/mixed_schoen_exterior_square.py",
                "research/experiments/scientific_genesis/ALTERNATE_UP_QUOTIENT_PAIRING_NOTE.md",
                "tests/integration/test_scientific_genesis_alternate_up_quotient_equivariance.py",
            ),
            ("actual constituent frames", "inherited B1 frame", "common flat twist (1,2)"),
            ("natural exterior-V matter-product comparison", "explicit quotient trace"),
        ),
        _node(
            "alternate_up_pairing_exchange",
            "actual ordered matter exchange and independent Laurent trace",
            "Flavor",
            "COMPUTED",
            "Reverse the actual null matter inputs with unchanged h and k. "
            "Record the full closure defect and ordered residue; when it "
            "agrees with the forward residue, require a full exact primitive "
            "of reverse minus forward. A literal top-Laurent coefficient "
            "checks the scalar trace independently of HPL projection. "
            "Full content-addressed cochains permit direct witness checks. "
            "No symmetrizing average or physical coefficient is assigned.",
            (
                "data/generated/scientific_genesis/alternate_up_pairing_exchange.json",
                "data/generated/scientific_genesis/alternate_up_pairing_exchange.cochains.json.gz",
                "research/experiments/scientific_genesis/alternate_up_pairing_exchange.py",
                "research/experiments/scientific_genesis/ALTERNATE_UP_QUOTIENT_PAIRING_NOTE.md",
                "tests/integration/test_scientific_genesis_alternate_up_pairing_exchange.py",
            ),
            ("same actual Higgs primitive", "declared ordered cover residue generator"),
            ("all-input derived tensor comparison", "quotient trace", "complete up matrix"),
        ),
        _node(
            "alternate_up_null_line_homotopies",
            "actual line-supported null homotopies and comparison ambiguity groups",
            "Flavor",
            "COMPUTED",
            "Both saved 90-term null Yoneda primitives have only line support. "
            "Their full B1-inverse differentials equal the actual h cup b-null "
            "products. The line has complete cohomology (0,0,9,0), so its "
            "primitive is unique modulo boundaries. Hom(det F,K) is zero "
            "before and after exact transfer, making a fixed-endpoint "
            "sheaf-extension morphism unique if it exists. The matter-product "
            "H2(K) ambiguity is five-dimensional on the cover, so it is not "
            "thereby eliminated.",
            (
                "data/generated/scientific_genesis/alternate_up_null_line_homotopies.json",
                "research/experiments/scientific_genesis/alternate_up_null_line_homotopies.py",
                "research/experiments/scientific_genesis/ALTERNATE_UP_QUOTIENT_PAIRING_NOTE.md",
                "tests/integration/test_scientific_genesis_alternate_up_null_line_homotopies.py",
            ),
            ("actual primitive support", "fixed Serre ideal quotient", "complete cover groups"),
            ("natural matter-product comparison", "complete comparison indeterminacy"),
        ),
        _node(
            "alternate_up_exterior_boundary_attack",
            "raw ordered exterior cup as an all-input cohomological product",
            "Flavor",
            "REFUTED",
            "A three-term strict native (0,0) primitive gives a 15-term exact "
            "boundary. Adding it to the actual left null matter class "
            "preserves the class and character but the raw exterior cup "
            "develops a 124-term full closure defect. Its 48-term Leibniz "
            "defect is explicit. This refutes the raw operation, not the "
            "carrier or the original closed scalar screens.",
            (
                "data/generated/scientific_genesis/alternate_up_exterior_boundary_attack.json",
                "research/experiments/scientific_genesis/alternate_up_exterior_boundary_attack.py",
                "tests/integration/test_scientific_genesis_exterior_boundary_attack.py",
            ),
            (
                "actual strict null classes", "full constituent differential",
                "unchanged exterior basis",
            ),
            ("natural product requires a cover tensor comparison",),
        ),
        _node(
            "mixed_even_rank_one_tensor_homotopy",
            "derived coefficient homotopy for the even-object rank-one tensor sector",
            "Flavor",
            "DERIVED",
            "The product-cover diagonal homotopy satisfies its chain identity "
            "on all 147 cells. With closed scalar arrows into one nilpotent "
            "even target, subtracting the coefficient homotopy cancels the "
            "raw wedge Leibniz defect; quadratic terms land in A wedge A. "
            "The actual corrected 302-term boundary wedge is the full "
            "primitive differential and the original null wedge is unchanged.",
            (
                "data/generated/scientific_genesis/alternate_up_exterior_boundary_attack.json",
                "research/experiments/scientific_genesis/mixed_schoen_cup_homotopy.py",
                "research/experiments/scientific_genesis/mixed_schoen_exterior_square.py",
                "research/experiments/scientific_genesis/ALTERNATE_UP_QUOTIENT_PAIRING_NOTE.md",
                "tests/integration/test_scientific_genesis_cup_homotopy.py",
                "tests/integration/test_scientific_genesis_even_tensor_homotopy.py",
            ),
            ("even-object inputs", "closed scalar twisting arrows", "one nilpotent even target"),
            ("syzygy comparison", "outer-cone comparison", "natural exterior-V-to-Q product"),
        ),
        _node(
            "mixed_graded_rank_one_tensor_comparison",
            "full graded tensor identity for an isolated even rank-one mixed image",
            "Flavor",
            "DERIVED",
            "The structural-first differential requires coefficient-before-second-object "
            "braiding. The derived cover homotopy then cancels mixed commutators "
            "in every internal degree. Full Hom-row closure cancels syzygy terms; "
            "quadratic corrections land in A wedge A. The actual strict odd-object "
            "boundary produces a corrected 294-term wedge equal to the differential "
            "of a 47-term primitive, rather than the raw 489-term closure defect. "
            "The original null wedge is unchanged. The coupled outer cone is not certified.",
            (
                "data/generated/scientific_genesis/alternate_up_syzygy_tensor_comparison.json",
                "research/experiments/scientific_genesis/mixed_schoen_rank_one_tensor.py",
                "research/experiments/scientific_genesis/alternate_up_syzygy_tensor_comparison.py",
                "research/experiments/scientific_genesis/ALTERNATE_UP_QUOTIENT_PAIRING_NOTE.md",
                "tests/integration/test_scientific_genesis_rank_one_tensor.py",
                "tests/integration/test_scientific_genesis_syzygy_tensor_comparison.py",
            ),
            (
                "two-term polynomial skeleton", "closed full mixed Hom row",
                "one isolated even nilpotent target", "explicit ordered cover homotopy",
            ),
            ("coupled outer-cone comparison", "physical pairing identification"),
        ),
        _node(
            "product_cover_homotopy_strict_hirsch",
            "strict first-slot Hirsch rule for the product-cover coefficient homotopy",
            "Flavor",
            "REFUTED",
            "Three explicit scalar degree-one edge cochains give a one-term "
            "defect in H(ab,c)-(-1)^|a| a H(b,c)-(-1)^(|b||c|) H(a,c)b. "
            "The telescoping product-cover homotopy is therefore not a strict "
            "first-slot derivation, although its commutator chain identity remains exact. "
            "Coupled outer rows need a compatible higher homotopy or a scoped quotient proof.",
            (
                "tests/integration/test_scientific_genesis_cup_homotopy.py",
                "research/experiments/scientific_genesis/ALTERNATE_UP_QUOTIENT_PAIRING_NOTE.md",
            ),
            ("fixed product-cover ordering", "scalar degree-one mathematical cochains"),
            ("actual outer defect not evaluated", "no carrier or Yukawa refutation"),
        ),
        _node(
            "mixed_schoen_hirsch_coherence",
            "acyclic-carrier filler of the first-slot cover homotopy defect",
            "Flavor",
            "DERIVED",
            "The nonzero chain Hirsch defect is a positive-degree cycle in "
            "each contractible cell carrier. Recursive first-vertex contraction "
            "gives boundary K-K boundary=J without coefficient fitting. Minus "
            "its dual gives a degree-minus-two scalar operation T, with the "
            "full Koszul differential. Independent product-chain boundaries "
            "check all 147 cells; the failed strict rule remains refuted.",
            (
                "research/experiments/scientific_genesis/mixed_schoen_cup_coherence.py",
                "research/experiments/scientific_genesis/ALTERNATE_UP_COUPLED_TENSOR_NOTE.md",
                "tests/integration/test_scientific_genesis_cup_coherence.py",
            ),
            ("fixed ordered cover", "scalar coefficients", "first-vertex contraction"),
            ("not a physical pairing or matrix",),
        ),
        _node(
            "mixed_coupled_quotient_tensor_identity",
            "derived triangular two-row product in the A wedge B quotient",
            "Flavor",
            "DERIVED",
            "For declared even targets A and B, validate the complete inner "
            "Hom row and the outer row against the inner complex. The "
            "differential-invariant A wedge B relation defines a legitimate "
            "quotient. Structural-first braiding, two coefficient homotopies "
            "and T cancel the complete Leibniz defect. Global polynomial terms "
            "cancel by row closure; remaining quadratic outputs vanish in "
            "the quotient. The additive shortcut has an explicit counterexample.",
            (
                "research/experiments/scientific_genesis/mixed_schoen_coupled_tensor.py",
                "research/experiments/scientific_genesis/ALTERNATE_UP_COUPLED_TENSOR_NOTE.md",
                "tests/integration/test_scientific_genesis_coupled_tensor.py",
            ),
            (
                "two-term polynomial skeleton", "triangular A-to-B graph",
                "full closed Hom rows", "declared ordered cover",
            ),
            ("other arrow graphs excluded", "actual cone comparison and scalar evaluation"),
        ),
        _node(
            "mixed_coupled_vertex_comparison",
            "literal vertex-local comparison with the ordinary quotient exterior map",
            "Flavor",
            "DERIVED",
            "The full differential preserves or raises cover degree. H and T "
            "have input-cell union carriers and vanish on vertex outputs. "
            "Consequently vertex restriction keeps all local syzygy and "
            "Koszul arrows and sends the corrected product to the ordinary "
            "local graded exterior quotient. Independent signs and all "
            "eighteen vertex differential projections are checked. The local "
            "identity supports a sheaf comparison only with faithful "
            "resolutions and a sheaf-natural chain map.",
            (
                "research/experiments/scientific_genesis/mixed_schoen_coupled_tensor.py",
                "research/experiments/scientific_genesis/ALTERNATE_UP_VERTEX_COMPARISON_NOTE.md",
                "tests/integration/test_scientific_genesis_coupled_tensor.py",
            ),
            ("declared triangular source", "union-supported H/T kernels", "ordered cover"),
            ("faithful sheaf resolutions", "complete scalar and quotient trace"),
        ),
        _node(
            "alternate_up_canonical_quotient_product",
            "canonical quotient sheaf product on the frozen alternate presentation",
            "Flavor",
            "DERIVED",
            "The actual q_E pushout is locally free; killing the injective "
            "B1 tensor A_F sheaf relation gives coherent Q. Vertex restriction "
            "identifies the ordinary local wedge. Union-supported Laurent "
            "operations make the complete chain map sheaf-natural. For a "
            "nonpositive derived tensor and a degree-zero sheaf target, Hom0 "
            "is exactly Hom from H0. An independent injective-resolution "
            "proof shows that negative ambient Tor adds no map ambiguity. "
            "The resulting comparison represents the canonical quotient "
            "morphism, not an arbitrary H2(K) product lift.",
            (
                "research/experiments/scientific_genesis/ALTERNATE_UP_VERTEX_COMPARISON_NOTE.md",
                "data/generated/scientific_genesis/alternate_constituent_carrier_state.json",
                "data/generated/scientific_genesis/alternate_up_coupled_tensor_comparison.json",
                "tests/integration/test_scientific_genesis_derived_zero_rigidity.py",
            ),
            (
                "frozen locally free Serre presentations", "nonzero injective A_F section",
                "regular Schoen complete intersection", "full sheaf-natural Leibniz identity",
            ),
            ("complete closed Higgs evaluation", "equivariant quotient trace", "full matrix"),
        ),
        _node(
            "alternate_up_same_higgs_class",
            "selected Higgs class identified by the natural exterior filtration",
            "Flavor",
            "DERIVED",
            "The actual determinant endpoints and their duals are acyclic. "
            "The two dual bundle sequences canonically identify exterior "
            "H1 with the middle mixed functional. Pullback through the natural "
            "exterior-V-to-Q map restricts to h_K(q_E(e),q_F(f)). The source "
            "Hom has pure A_E output, kills A_F, and uses the fixed Pluecker "
            "column for e wedge A_E. Thus its class is the selected Higgs, "
            "without a fitted phase or a fabricated strict chain map.",
            (
                "research/experiments/scientific_genesis/ALTERNATE_UP_MIXED_PAIRING_NOTE.md",
                "research/experiments/scientific_genesis/ALTERNATE_UP_VERTEX_COMPARISON_NOTE.md",
                "tests/integration/test_scientific_genesis_alternate_up_quotient_equivariance.py",
                "research/experiments/scientific_genesis/alternate_up_higgs_quotient_cone.py",
            ),
            (
                "frozen locally free carrier", "acyclic determinant endpoints",
                "closed quotient Higgs",
            ),
            ("full matrix entries", "canonical metrics and stabilized common vacuum"),
        ),
        _node(
            "alternate_up_mixed_quotient_pairing",
            "four actual constant mixed entries in the common Higgs-first order",
            "Flavor",
            "COMPUTED",
            "Push the actual E classes through the fixed q_E row. On a "
            "B-supported input every coupled correction vanishes in B wedge B "
            "or the legitimate B wedge A_F relation. All four full scalar "
            "cycles have 2257 terms and unchanged exchanged-input cochains. "
            "Independent Hom composition checks the scalar-order sign: only "
            "the earlier determinant screen's mixed row changes. Quotient "
            "traces use the declared descended volume frame; the F-F block "
            "is not filled with zeros or called a complete matrix.",
            (
                "data/generated/scientific_genesis/alternate_up_mixed_quotient_pairing.json",
                "research/experiments/scientific_genesis/alternate_up_mixed_quotient_pairing.py",
                "research/experiments/scientific_genesis/ALTERNATE_UP_MIXED_PAIRING_NOTE.md",
                "tests/integration/test_scientific_genesis_alternate_up_mixed_quotient_pairing.py",
            ),
            ("fixed family seed bases", "canonical quotient product", "explicit holomorphic trace"),
            ("four F-F entries with both formal coefficients", "canonical matter normalization"),
        ),
        _node(
            "alternate_up_coupled_null_pairing",
            "complete natural carrier null contraction for both formal coefficients",
            "Flavor",
            "COMPUTED",
            "Complete pushed matter and Higgs lifts, the corrected quotient "
            "product, and the scalar are checked coefficientwise by full "
            "differentials. The products have 142815 and 136570 terms; "
            "their scalars have 42302 and 41454 terms. Literal Laurent and "
            "transferred cover traces agree: 0 and (2673-486 omega)/49. "
            "Both scalar cochains equal the old screen literally. The "
            "explicit archive verifier rechecks saved identities and uses "
            "independent inverse convolution. This is one contraction, "
            "not all four F-F entries or a canonically normalized matrix.",
            (
                "data/generated/scientific_genesis/alternate_up_coupled_null_scalar.json",
                "data/generated/scientific_genesis/alternate_up_coupled_null_scalar.cochains.json.gz",
                "research/experiments/scientific_genesis/alternate_up_coupled_null_scalar.py",
                "research/experiments/scientific_genesis/ALTERNATE_UP_NATURAL_NULL_SCALAR_NOTE.md",
            ),
            (
                "complete actual carrier matter lifts", "same closed Higgs",
                "fixed cover residue frame",
            ),
            ("all four F-F entries", "canonical metrics", "stabilized common vacuum"),
        ),
        _node(
            "alternate_up_ff_block",
            "four actual F-F entries for both universal coefficients",
            "Flavor",
            "COMPUTED",
            "All eight F-F entries have complete source-lift, product and "
            "scalar archives. Fresh replay checks both four-entry blocks, "
            "their literal natural-null cochain identities, and the fixed "
            "Higgs-first quotient trace. This gives one exact formal "
            "holomorphic 3x3 up matrix, not a canonically normalized one.",
            (
                "research/experiments/scientific_genesis/alternate_up_ff_entries.py",
                "research/experiments/scientific_genesis/alternate_up_full_matrix.py",
                "data/generated/scientific_genesis/alternate_up_ff_lift_a0_side0_family1.json",
                "data/generated/scientific_genesis/alternate_up_ff_lift_a0_side0_family1.cochains.json.gz",
                "data/generated/scientific_genesis/alternate_up_ff_lift_a0_side0_family2.json",
                "data/generated/scientific_genesis/alternate_up_ff_lift_a0_side0_family2.cochains.json.gz",
                "data/generated/scientific_genesis/alternate_up_ff_lift_a0_side1_family1.json",
                "data/generated/scientific_genesis/alternate_up_ff_lift_a0_side1_family1.cochains.json.gz",
                "data/generated/scientific_genesis/alternate_up_ff_lift_a0_side1_family2.json",
                "data/generated/scientific_genesis/alternate_up_ff_lift_a0_side1_family2.cochains.json.gz",
                "data/generated/scientific_genesis/alternate_up_ff_a0_r1_c1.json",
                "data/generated/scientific_genesis/alternate_up_ff_a0_r1_c1.cochains.json.gz",
                "data/generated/scientific_genesis/alternate_up_ff_a0_r1_c2.json",
                "data/generated/scientific_genesis/alternate_up_ff_a0_r1_c2.cochains.json.gz",
                "data/generated/scientific_genesis/alternate_up_ff_a0_r2_c1.json",
                "data/generated/scientific_genesis/alternate_up_ff_a0_r2_c1.cochains.json.gz",
                "data/generated/scientific_genesis/alternate_up_ff_a0_r2_c2.json",
                "data/generated/scientific_genesis/alternate_up_ff_a0_r2_c2.cochains.json.gz",
                "data/generated/scientific_genesis/alternate_up_ff_coefficient_a0.json",
                "data/generated/scientific_genesis/alternate_up_ff_lift_a1_side0_family1.json",
                "data/generated/scientific_genesis/alternate_up_ff_lift_a1_side0_family1.cochains.json.gz",
                "data/generated/scientific_genesis/alternate_up_ff_lift_a1_side0_family2.json",
                "data/generated/scientific_genesis/alternate_up_ff_lift_a1_side0_family2.cochains.json.gz",
                "data/generated/scientific_genesis/alternate_up_ff_lift_a1_side1_family1.json",
                "data/generated/scientific_genesis/alternate_up_ff_lift_a1_side1_family1.cochains.json.gz",
                "data/generated/scientific_genesis/alternate_up_ff_lift_a1_side1_family2.json",
                "data/generated/scientific_genesis/alternate_up_ff_lift_a1_side1_family2.cochains.json.gz",
                "data/generated/scientific_genesis/alternate_up_ff_a1_r1_c1.json",
                "data/generated/scientific_genesis/alternate_up_ff_a1_r1_c1.cochains.json.gz",
                "data/generated/scientific_genesis/alternate_up_ff_a1_r1_c2.json",
                "data/generated/scientific_genesis/alternate_up_ff_a1_r1_c2.cochains.json.gz",
                "data/generated/scientific_genesis/alternate_up_ff_a1_r2_c1.json",
                "data/generated/scientific_genesis/alternate_up_ff_a1_r2_c1.cochains.json.gz",
                "data/generated/scientific_genesis/alternate_up_ff_a1_r2_c2.json",
                "data/generated/scientific_genesis/alternate_up_ff_a1_r2_c2.cochains.json.gz",
                "data/generated/scientific_genesis/alternate_up_ff_coefficient_a1.json",
                "data/generated/scientific_genesis/alternate_up_full_holomorphic_matrix.json",
                "tests/integration/test_scientific_genesis_alternate_up_ff_entries.py",
                "tests/integration/test_scientific_genesis_alternate_up_full_matrix.py",
            ),
            ("frozen actual family bases", "same Higgs class", "canonical quotient product"),
        ),
        _node(
            "alternate_up_quotient_trace",
            "actual scalar descent and explicit finite-cover trace frame",
            "Flavor",
            "COMPUTED",
            "The 55-term full cover H3(O) generator is closed with direct "
            "and transferred residue one. P changes it by a 30-term "
            "difference with a full checked 16-term primitive; T fixes it "
            "strictly. Thus H3(O) is deck trivial and the dual holomorphic "
            "volume form descends. In the stated pullback-compatible volume "
            "frame finite-etale Serre trace gives the factor 1/9. No matrix "
            "coefficient or canonical matter normalization is assigned.",
            (
                "data/generated/scientific_genesis/alternate_up_quotient_trace.json",
                "research/experiments/scientific_genesis/alternate_up_quotient_trace.py",
                "research/experiments/scientific_genesis/ALTERNATE_UP_QUOTIENT_TRACE_NOTE.md",
                "tests/integration/test_scientific_genesis_alternate_up_quotient_trace.py",
            ),
            (
                "published free ninefold quotient", "fixed ordered cover residue",
                "pi*Omega_quotient=Omega_cover", "finite-etale Serre trace compatibility",
            ),
            ("complete closed carrier products", "same-Higgs identification", "full matrix"),
        ),
        _node(
            "alternate_up_coupled_tensor_presentation",
            "actual two-coefficient pushout and full quotient-product comparison",
            "Flavor",
            "COMPUTED",
            "The actual rank-three pushout has nine resolution objects, "
            "including two-equation Koszul arrows. Its 38-object quotient "
            "matches every object, polynomial and inner mixed arrow of the "
            "existing K/exterior-F cone. Both complete connecting arrows agree "
            "exactly. Full Leibniz checks use an actual odd syzygy primitive "
            "and null matter with nonzero outer differential; neither input "
            "is silently treated as closed in R. No scalar is evaluated.",
            (
                "data/generated/scientific_genesis/alternate_up_coupled_tensor_comparison.json",
                "research/experiments/scientific_genesis/alternate_up_coupled_tensor_comparison.py",
                "research/experiments/scientific_genesis/ALTERNATE_UP_COUPLED_TENSOR_NOTE.md",
                "tests/integration/test_scientific_genesis_actual_coupled_tensor.py",
            ),
            ("frozen alternate component", "actual universal coefficients a0 and a1"),
            (
                "complete cone matter pairing not evaluated", "trace conventions",
                "complete up matrix and physical normalization absent",
            ),
        ),
        _node(
            "alternate_constituent_determinant_pairing",
            "local pairing for the frozen alternate I6 ray",
            "Computable carrier",
            "COMPUTED",
            "Complementary minors of the actual alternate rank-two quotient "
            "annihilate its relations on all six charts. Hypersurface "
            "factorization gives thirty corrected overlap identities; all "
            "six chart pairings differ from the selected I6 ray. The "
            "Hom-to-tensor chain map remains unavailable.",
            (
                "data/generated/scientific_genesis/"
                "alternate_constituent_determinant_pairing.json",
                "research/experiments/scientific_genesis/"
                "alternate_constituent_determinant_pairing.py",
                "tests/integration/"
                "test_scientific_genesis_alternate_determinant_pairing.py",
            ),
            ("frozen alternate ray", "certified six-chart atlas"),
            ("rank-two Hom-to-tensor chain map", "exterior-cone Higgs lift"),
        ),
        _node(
            "alternate_constituent_duality_local_inverse",
            "minor-open inverse of alternate rank-two duality",
            "Computable carrier",
            "COMPUTED",
            "On each of six alternate charts, ten nonzero determinant minors "
            "define principal opens. Sparse numerators satisfy J S J = "
            "Delta J, while adjugate syzygy contractions satisfy A^t T = "
            "D id and J S P = Delta P on all sixty opens. Certified local "
            "freeness makes the combined map a quotient inverse. Full "
            "Cech--Koszul Hom transport remains unavailable.",
            (
                "data/generated/scientific_genesis/"
                "alternate_constituent_duality_local_inverse.json",
                "research/experiments/scientific_genesis/"
                "alternate_constituent_duality_local_inverse.py",
                "research/experiments/scientific_genesis/"
                "ALTERNATE_DUALITY_LOCAL_INVERSE_NOTE.md",
                "tests/integration/"
                "test_scientific_genesis_alternate_duality_local_inverse.py",
            ),
            ("frozen alternate local-freeness", "exact alternate Pluecker form"),
            ("full Hom-to-tensor Cech--Koszul map", "exterior-cone Higgs lift"),
        ),
        _node(
            "alternate_up_higgs_local_syzygy_section",
            "localized actual up-Higgs Hom syzygy sections",
            "Computable carrier",
            "COMPUTED",
            "The saved strict Hom class has eighteen nonzero right-chart "
            "syzygy blocks. On the selected minor principal open, exact "
            "adjugate middle numerators map to denominator times each "
            "block under the independently assembled right mixed arrows. "
            "Fiber-overlap transport is recorded separately; this local "
            "section alone is not a full Cech--Koszul tensor map.",
            (
                "data/generated/scientific_genesis/"
                "alternate_up_higgs_local_syzygy_section.json",
                "research/experiments/scientific_genesis/"
                "alternate_up_higgs_local_syzygy_section.py",
                "research/experiments/scientific_genesis/"
                "ALTERNATE_UP_HIGGS_LOCAL_SECTION_NOTE.md",
                "tests/integration/"
                "test_scientific_genesis_alternate_up_higgs_local_syzygy_section.py",
            ),
            ("strict alternate Hom cochain", "minor-open inverse"),
            ("full Cech--Koszul tensor map", "exterior-cone Higgs lift"),
        ),
        _node(
            "alternate_up_higgs_fiber_overlap_transport",
            "Koszul-corrected fiber transport of the strict alternate Hom class",
            "Computable carrier",
            "COMPUTED",
            "The actual vertex syzygies, fiber-overlap middle terms, and "
            "k1_u syzygies satisfy an exact three-part closure identity. "
            "After the certified unipotent gauge transports the local "
            "minor-open sections, one exact homogeneous formula "
            "satisfies B N = F K across all nine cover blocks. "
            "Minor and base-cover compatibility is established separately; "
            "this identity alone is not a full tensor chain map.",
            (
                "data/generated/scientific_genesis/"
                "alternate_up_higgs_fiber_overlap_transport.json",
                "research/experiments/scientific_genesis/"
                "alternate_up_higgs_fiber_overlap_transport.py",
                "research/experiments/scientific_genesis/"
                "ALTERNATE_UP_HIGGS_FIBER_OVERLAP_NOTE.md",
                "tests/integration/"
                "test_scientific_genesis_alternate_up_higgs_fiber_overlap_transport.py",
            ),
            ("strict Hom cochain", "localized syzygy sections", "alternate atlas"),
            ("global Hom-to-tensor map", "exterior-cone Higgs lift"),
        ),
        _node(
            "alternate_up_higgs_quotient_overlap_image",
            "minor-open quotient image of the alternate Hom overlap",
            "Computable carrier",
            "COMPUTED",
            "The corrected actual Hom overlap maps through the alternate "
            "rank-two Pluecker inverse on the selected principal open. "
            "Its two-coordinate quotient numerator obeys an exact "
            "cross-multiplied hypersurface identity on three target "
            "charts. Subsequent exact comparisons close its minor and "
            "base-cover transition checks, not the full tensor map.",
            (
                "data/generated/scientific_genesis/"
                "alternate_up_higgs_quotient_overlap_image.json",
                "research/experiments/scientific_genesis/"
                "alternate_up_higgs_quotient_overlap_image.py",
                "research/experiments/scientific_genesis/"
                "ALTERNATE_UP_HIGGS_QUOTIENT_OVERLAP_NOTE.md",
                "tests/integration/"
                "test_scientific_genesis_alternate_up_higgs_quotient_overlap_image.py",
            ),
            ("actual corrected Hom overlap", "certified rank-two duality inverse"),
            ("global tensor chain map", "exterior-cone Higgs lift"),
        ),
        _node(
            "alternate_up_higgs_minor_overlap_gluing",
            "principal-open compatibility of the actual alternate Hom quotient",
            "Computable carrier",
            "COMPUTED",
            "The ten sparse Pluecker inverse images of the corrected Hom "
            "overlap agree modulo the actual rank-three relation on their "
            "common principal opens of the Schoen hypersurface. Nine exact "
            "relation witnesses and hypersurface corrections regenerate "
            "from content-pinned formulas. "
            "The fiber-edge formula matches through twelve identity "
            "base-only atlas transitions; a global tensor map remains open.",
            (
                "data/generated/scientific_genesis/"
                "alternate_up_higgs_minor_overlap_gluing.json",
                "research/experiments/scientific_genesis/"
                "alternate_up_higgs_minor_overlap_gluing.py",
                "research/experiments/scientific_genesis/"
                "ALTERNATE_UP_HIGGS_MINOR_OVERLAP_NOTE.md",
                "tests/integration/"
                "test_scientific_genesis_alternate_up_higgs_minor_overlap_gluing.py",
            ),
            ("actual quotient overlap image", "certified minor-open inverse"),
            ("full Cech--Koszul tensor map", "exterior-cone Higgs lift"),
        ),
        _node(
            "alternate_up_yukawa_support",
            "universal up-matrix filtration support",
            "Flavor",
            "DERIVED",
            "The one-plus-two constituent matter bases and acyclic "
            "determinant filtration force the E-E slot to vanish, the "
            "E-F slots to be parameter-independent, and the F-F block "
            "to be linear in the two outer parameters. Consequently the "
            "three-by-three determinant is linear. Both coefficients are "
            "now computed in the separately audited complete matrix.",
            (
                "data/generated/scientific_genesis/"
                "alternate_up_yukawa_support.json",
                "research/experiments/scientific_genesis/"
                "alternate_up_yukawa_support.py",
                "research/experiments/scientific_genesis/"
                "ALTERNATE_UP_YUKAWA_SUPPORT_NOTE.md",
                "tests/integration/"
                "test_scientific_genesis_alternate_up_yukawa_support.py",
            ),
            ("frozen alternate P1", "acyclic determinant endpoints"),
        ),
        _node(
            "relative_constituent_pushdowns",
            "source-labelled constituent relative pushdowns",
            "Computable carrier",
            "SELECTED",
            "Exact point-support and local-unit checks are conditional on "
            "source-assigned W1/W2 line degrees and characters. The derived "
            "tensor has dimension profile (0,4,4,0), but its equivariant "
            "signature is not independently reconstructed from the atlas.",
            (
                "data/generated/scientific_genesis/"
                "relative_constituent_pushdowns.json",
                "research/experiments/scientific_genesis/"
                "relative_constituent_pushdowns.py",
                "tests/integration/"
                "test_scientific_genesis_relative_constituent_pushdowns.py",
            ),
            (
                "relative duality",
                "selected mixed constituent local units",
                "published line signatures",
            ),
            ("atlas-to-relative equivariant chain map",),
        ),
        _node(
            "selected_constituent_determinant_acyclicity",
            "acyclic determinant endpoints for the selected pair",
            "Computable carrier",
            "COMPUTED",
            "Exact full-Cech line transfer gives zero cohomology in every "
            "degree for both constituent determinant lines. Character "
            "relinearizations preserve this acyclicity, so exterior-square "
            "cohomology of either rank-four extension is represented by the "
            "middle constituent tensor cohomology, irrespective of its "
            "nonsplit parameter.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_observable_spectrum.json",
                "research/experiments/scientific_genesis/"
                "mixed_schoen_observable_spectrum.py",
                "tests/integration/"
                "test_scientific_genesis_mixed_schoen_observable_spectrum.py",
            ),
            assumptions=("same selected underlying V1/V2 pair",),
        ),
        _node(
            "mixed_schoen_observable_spectrum",
            "superseded mixed-family Wilson spectrum",
            "Computable carrier",
            "REFUTED",
            "Pure constituent H1 dimensions 9 and 18, the regular matter "
            "multiplicity, and acyclic determinant endpoints remain exact. "
            "Its relative-pushdown Higgs characters predicted one Wilson pair, "
            "but the later full-chain tensor audit gives only the down doublet "
            "under the fixed Wilson embedding. The one-pair claim is superseded.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_observable_spectrum.json",
                "research/experiments/scientific_genesis/"
                "mixed_schoen_observable_spectrum.py",
                "tests/integration/"
                "test_scientific_genesis_mixed_schoen_observable_spectrum.py",
            ),
            (
                "free ninefold Schoen deck action",
                "published Wilson-line embedding",
                "Calabi--Yau Serre duality",
            ),
        ),
        _node(
            "published_chain_reconstruction",
            "published carrier chain reconstruction",
            "Reference realization",
            "BLOCKED",
            "The lawful mixed rank-two constituents and universal P1 outer cone "
            "are exact. The source carrier's former P3 parameter ledger does "
            "not yet have an exact comparison with this smaller lawful family.",
            (
                "data/generated/visible_carrier/visible_carrier_artifact.json",
                "data/generated/scientific_genesis/"
                "mixed_schoen_outer_universal_cone.json",
            ),
            missing=(
                "comparison of the lawful P1 family with the source P3 ledger",
            ),
        ),
        _node(
            "computable_constituent_category",
            "computable Schoen Serre constituent category",
            "Computable carrier",
            "COMPUTED",
            "Forty determinant-compatible topology candidates and their declared "
            "ray pairs have exact constituent presentations and deck actions.",
            (
                "data/generated/computable_carrier/computable_carrier_artifact.json",
                "research/experiments/computable_carrier/tier_b_schoen_outer_full.py",
            ),
        ),
        _node(
            "cover_ext_screen",
            "complete cover Ext screen",
            "Computable carrier",
            "COMPUTED",
            "All 1,440 declared pairs have exact cover Hom totalizations and Ext-one dimensions.",
            ("data/generated/computable_carrier/tier_b_schoen_outer_full.json",),
        ),
        _node(
            "invariant_ext_cocycles",
            "complete invariant Ext cocycle screen",
            "Computable carrier",
            "COMPUTED",
            "All 1,440 pairs have exact invariant subcomplexes; 1,080 positive "
            "spaces have explicit cocycle representatives and 360 vanish exactly.",
            ("data/generated/computable_carrier/tier_b_schoen_outer_invariants.json",),
        ),
        _node(
            "automorphism_orbits",
            "partial exact automorphism quotient classification",
            "Computable carrier",
            "COMPUTED",
            "Exactly 1,296 of 1,440 pair actions are certified; the sweep is "
            "suspended because larger remaining spaces cannot simplify pair 73.",
            (
                "data/generated/computable_carrier/tier_b_schoen_outer_automorphisms.partial.json",
                "research/experiments/computable_carrier/README.md",
            ),
        ),
        _node(
            "automorphism_compression_theorem",
            "structural automorphism trichotomy",
            "Computable carrier",
            "CONJECTURED",
            "Observed actions divide into direct scalar, quotient-reduced scalar, "
            "and square-zero-unipotent exceptional families; a family-level proof is absent.",
            (
                "research/experiments/computable_carrier/schoen_sparse_outer_automorphisms.py",
                "data/generated/computable_carrier/tier_b_schoen_outer_automorphisms.partial.json",
            ),
            missing=(
                "family-level representation-theoretic proof",
                "deliberate exceptional-locus attack",
            ),
        ),
        _node(
            "smallest_certified_ext_family",
            "pair 73 universal P3 extension parameter space",
            "Computable carrier",
            "COMPUTED",
            "Pair 73 has four exact invariant cocycles and scalar constituent "
            "automorphisms, so its nonzero orbit parameter space is P3 over Q(omega).",
            (
                "data/generated/computable_carrier/tier_b_schoen_outer_invariants.json",
                "data/generated/computable_carrier/tier_b_schoen_outer_automorphisms.partial.json",
            ),
        ),
        _node(
            "universal_ext_family",
            "pair 73 universal invariant Ext family",
            "Computable carrier",
            "COMPUTED",
            "The four exact pair-73 cocycles assemble linearly over "
            "Q(omega)[a0,a1,a2,a3]; only the affine origin splits and the "
            "nonzero automorphism quotient is P3.",
            (
                "data/generated/scientific_genesis/pair_73_universal_ext.json",
                "research/experiments/scientific_genesis/pair_73_universal.py",
            ),
        ),
        _node(
            "universal_rank_four_family",
            "universal rank-four mapping-cone family",
            "Computable carrier",
            "COMPUTED",
            "All four pair-73 classes lift through exact projective-product "
            "Cech descent into degree-one morphisms of the full resolution; "
            "their universal linear combination has an exact derived cone.",
            (
                "data/generated/scientific_genesis/pair_73_cech_lift.json",
                "research/experiments/scientific_genesis/pair_73_cech_lift.py",
            ),
        ),
        _node(
            "algebraic_lawful_locus",
            "rank-four algebraic lawful locus",
            "Computable carrier",
            "COMPUTED",
            "Every nonzero pair-73 class is a locally free descended rank-four "
            "extension with trivial determinant and fixed Chern data; local "
            "freeness and descent exclude no additional parameter.",
            (
                "data/generated/scientific_genesis/pair_73_algebraic_locus.json",
                "research/experiments/scientific_genesis/pair_73_lawful_locus.py",
            ),
        ),
        _node(
            "necessary_stability_walls",
            "pair-73 unavoidable stability walls",
            "Computable carrier",
            "COMPUTED",
            "The rank-two extension subbundle, its Serre line, and the "
            "rank-three preimage give exact necessary slope inequalities; "
            "their region intersects the published Kahler cone, while the full "
            "family is unstable at the published carrier anchor.",
            (
                "data/generated/scientific_genesis/pair_73_stability_wall.json",
                "research/experiments/scientific_genesis/pair_73_stability_wall.py",
            ),
        ),
        _node(
            "stability_chamber",
            "pair-73 slope-stable locus",
            "Computable carrier",
            "REFUTED",
            "The right Serre line lifts through every pair-73 outer extension "
            "and has slope opposite to the left rank-two subbundle, so strict "
            "stability fails at every polarization and parameter.",
            (
                "data/generated/scientific_genesis/pair_73_stability_no_go.json",
                "research/experiments/scientific_genesis/pair_73_stability_no_go.py",
            ),
        ),
        _node(
            "minimum_dimensional_stability_block",
            "minimum-dimensional computable stability block",
            "Computable carrier",
            "REFUTED",
            "All 72 four-dimensional invariant-Ext families in candidates 3 "
            "and 23 share the lifted right-Serre-line opposite-slope obstruction.",
            (
                "data/generated/scientific_genesis/minimal_block_stability_no_go.json",
                "research/experiments/scientific_genesis/minimal_block_stability_no_go.py",
            ),
        ),
        _node(
            "next_topology_stability_block",
            "six/eight-dimensional computable stability block",
            "Computable carrier",
            "REFUTED",
            "All 72 families in candidates 14 and 34 lift a right Serre line "
            "whose exact slope is strictly positive throughout the Kahler cone.",
            (
                "data/generated/scientific_genesis/next_block_stability_no_go.json",
                "research/experiments/scientific_genesis/next_block_stability_no_go.py",
            ),
        ),
        _node(
            "current_minimum_stability_block",
            "eight/ten-dimensional computable stability block",
            "Computable carrier",
            "REFUTED",
            "All 72 families in candidates 8 and 28 contain a descended left "
            "Serre line whose exact slope is strictly positive throughout the "
            "published Kahler cone.",
            (
                "data/generated/scientific_genesis/current_minimum_stability_no_go.json",
                "research/experiments/scientific_genesis/"
                "current_minimum_stability_no_go.py",
            ),
        ),
        _node(
            "forced_subobject_stability_class",
            "coefficient-positive forced-subobject topology class",
            "Computable carrier",
            "REFUTED",
            "A structural screen of all 40 declared topology blocks finds 18 "
            "blocks, containing 648 families, with an unavoidable subbundle "
            "of strictly positive slope throughout the Kahler cone.",
            (
                "data/generated/scientific_genesis/"
                "forced_subobject_stability_screen.json",
                "research/experiments/scientific_genesis/"
                "forced_subobject_stability_screen.py",
            ),
        ),
        _node(
            "mixed_sign_minimum_forced_chamber",
            "mixed-sign minimum necessary stability chamber",
            "Computable carrier",
            "COMPUTED",
            "Candidates 15 and 35 have an exact nonempty common chamber for "
            "their three extension-independent subobjects; the rational families "
            "(2,1,t) and (1,2,t), with t greater than 7/2, certify nonemptiness.",
            (
                "data/generated/scientific_genesis/mixed_sign_minimum_chamber.json",
                "research/experiments/scientific_genesis/mixed_sign_minimum_chamber.py",
            ),
            missing=("classification of every additional saturated subsheaf",),
        ),
        _node(
            "mixed_sign_minimum_stability_block",
            "mixed-sign minimum full stability block",
            "Computable carrier",
            "REFUTED",
            "Every invariant class in candidates 15 and 35 restricts trivially "
            "to the right Serre line, which therefore lifts with strictly "
            "positive slope throughout the Kahler cone.",
            (
                "data/generated/scientific_genesis/"
                "mixed_sign_minimum_stability_no_go.json",
                "research/experiments/scientific_genesis/"
                "mixed_sign_minimum_stability_no_go.py",
            ),
        ),
        _node(
            "lifted_line_slope_identity_block",
            "dimension-42/48 lifted-line slope-identity block",
            "Computable carrier",
            "REFUTED",
            "All 72 families in candidates 16 and 36 lift the right Serre line; "
            "a strictly positive linear combination of its slope and the "
            "rank-three preimage slope makes their common chamber empty.",
            (
                "data/generated/scientific_genesis/"
                "lifted_line_slope_identity_no_go.json",
                "research/experiments/scientific_genesis/"
                "lifted_line_slope_identity_no_go.py",
            ),
        ),
        _node(
            "next_survivor_lifting_kernel",
            "dimension-50/52 right-line lifting kernel",
            "Computable carrier",
            "COMPUTED",
            "All 72 families in candidates 4 and 24 have exact rank-20 "
            "restriction maps. Their projective lifting kernels are unstable, "
            "while stability on the nonlifting open complements remains unresolved.",
            (
                "data/generated/scientific_genesis/"
                "next_survivor_restriction.json",
                "research/experiments/scientific_genesis/"
                "next_survivor_restriction.py",
            ),
            missing=(
                "stability classification on the nonlifting open complements",
            ),
        ),
        _node(
            "next_survivor_forced_chamber",
            "dimension-50/52 necessary stability chamber",
            "Computable carrier",
            "COMPUTED",
            "Candidates 4 and 24 have a nonempty exact chamber for every "
            "extension-independent proper subbundle. Rational factor-exchanged "
            "witnesses certify necessity without proving full stability.",
            (
                "data/generated/scientific_genesis/"
                "next_survivor_forced_chamber.json",
                "research/experiments/scientific_genesis/"
                "next_survivor_forced_chamber.py",
            ),
            missing=(
                "classification of additional saturated subsheaves on the "
                "nonlifting open complements",
            ),
        ),
        _node(
            "next_survivor_generator_strata",
            "dimension-50/52 generator-line lifting strata",
            "Computable carrier",
            "COMPUTED",
            "All 288 equivariant quotient-generator line restrictions have "
            "exact positive rank and proper kernels. Their finite unstable "
            "union leaves a nonempty generic complement.",
            (
                "data/generated/scientific_genesis/"
                "next_survivor_generator_restrictions.json",
                "research/experiments/scientific_genesis/"
                "next_survivor_generator_restrictions.py",
            ),
            missing=(
                "restriction maps for lower proper constituent sublines",
            ),
        ),
        _node(
            "next_survivor_lower_line_block",
            "dimension-50/52 lower-line stability block",
            "Computable carrier",
            "REFUTED",
            "Every candidate-4/24 extension lifts a descended lower line. Its "
            "slope plus the unavoidable left-line slope is the strictly "
            "positive fiber-class slope, so their common chamber is empty.",
            (
                "data/generated/scientific_genesis/"
                "next_survivor_lower_line_no_go.json",
                "research/experiments/scientific_genesis/"
                "next_survivor_lower_line_no_go.py",
            ),
        ),
        _node(
            "declared_carrier_category",
            "declared monomial carrier category",
            "Computable carrier",
            "REFUTED",
            "The final 72 families in candidates 5 and 25 universally lift a "
            "descended lower line whose slope has an incompatible positive "
            "sum with the forced left-line slope.",
            (
                "data/generated/scientific_genesis/"
                "remaining_lower_line_no_go.json",
                "research/experiments/scientific_genesis/"
                "remaining_lower_line_no_go.py",
            ),
        ),
        _node(
            "physical_spectrum",
            "physical Wilson-projected carrier spectrum",
            "Reference realization",
            "BLOCKED",
            "The selected cover cohomology and Wilson-character arithmetic "
            "give the target counts throughout P1 x K^s, but a physical "
            "quotient spectrum needs an equivariantly trivial determinant.",
            (
                "src/onetheory/physics/compactification.py",
                "data/generated/scientific_genesis/"
                "mixed_schoen_observable_spectrum.json",
                "research/experiments/scientific_genesis/"
                "mixed_schoen_observable_spectrum.py",
            ),
            assumptions=(
                "published Wilson-line embedding",
                "three families and one Higgs pair are selection constraints",
            ),
            missing=("trivial quotient determinant with compatible Wilson spectrum",),
        ),
        _node(
            "computable_carrier_state",
            "proposed forward computable carrier",
            "Computable carrier",
            "BLOCKED",
            "The selected P1 cover family remains exact, but its proposed "
            "physical quotient freeze requires a trivial equivariant "
            "determinant; rational c1 does not certify it.",
            (
                "data/generated/scientific_genesis/"
                "computable_one_theory_carrier_state.json",
                "research/experiments/scientific_genesis/"
                "computable_one_theory_carrier_state.py",
                "tests/integration/"
                "test_scientific_genesis_computable_one_theory_carrier_state.py",
            ),
            missing=("trivial quotient determinant with compatible Wilson spectrum",),
        ),
        _node(
            "mixed_schoen_reverse_observable_spectrum",
            "superseded reverse-family Wilson spectrum",
            "Reference realization",
            "REFUTED",
            "Pure-H1 constituent cohomology makes reverse matter independent "
            "of all P5 parameters. Acyclic determinant endpoints make the "
            "exterior-square filtration orientation-independent. The older "
            "derived-pushdown one-Higgs character assignment is contradicted "
            "by the full-chain tensor audit; the fixed-Wilson one-pair claim "
            "does not hold for this selected constituent pair.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_reverse_observable_spectrum.json",
                "research/experiments/scientific_genesis/"
                "mixed_schoen_reverse_observable_spectrum.py",
                "tests/integration/"
                "test_scientific_genesis_mixed_schoen_reverse_observable_spectrum.py",
            ),
            assumptions=(
                "published Wilson-line embedding",
                "three families and one Higgs pair are selection constraints",
            ),
        ),
        _node(
            "computable_reverse_carrier_state",
            "proposed reverse computable carrier",
            "Computable carrier",
            "BLOCKED",
            "The selected reverse P5 cover family remains exact, but its "
            "physical quotient freeze fails the current determinant gate. "
            "The source P3 ledger remains a distinct reference.",
            (
                "data/generated/scientific_genesis/"
                "computable_one_theory_reverse_carrier_state.json",
                "research/experiments/scientific_genesis/"
                "computable_one_theory_reverse_carrier_state.py",
                "tests/integration/"
                "test_scientific_genesis_computable_one_theory_reverse_carrier_state.py",
            ),
            missing=("trivial quotient determinant with compatible Wilson spectrum",),
        ),
        _node(
            "reverse_universal_down_matter_lifts",
            "reverse universal down-matter representatives",
            "Computable carrier",
            "COMPUTED",
            "Exact source-to-forward character inversion selects two physical "
            "matter sectors. Four V2 subobject classes remain constant, while "
            "two V1 quotient classes acquire twelve independently certified "
            "V2 correction coefficients over the full reverse P5 without "
            "selecting an extension point.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_reverse_down_matter_lifts.json",
                "research/experiments/scientific_genesis/"
                "mixed_schoen_reverse_down_matter_lifts.py",
                "tests/integration/"
                "test_scientific_genesis_mixed_schoen_reverse_down_matter_lifts.py",
            ),
            assumptions=(
                "published Wilson character assignment for the down sector",
            ),
        ),
        _node(
            "reverse_universal_down_higgs_lift",
            "reverse universal down-Higgs representative",
            "Computable carrier",
            "COMPUTED",
            "The strict 27-term middle tensor Higgs cocycle has six exact "
            "parameter-linear determinant-two corrections over the full "
            "reverse P5. Each extension action is a closed boundary in the "
            "explicit line complex, and the inverse fiber-twist chain map "
            "places every correction in the canonical determinant frame "
            "with exact forward (0,1) deck character.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_reverse_higgs_lifts.json",
                "research/experiments/scientific_genesis/"
                "mixed_schoen_reverse_higgs_lifts.py",
                "tests/integration/"
                "test_scientific_genesis_mixed_schoen_reverse_higgs_lifts.py",
            ),
            assumptions=(
                "published Wilson character assignment for the down sector",
            ),
            missing=(
                "reverse same-chain determinant contraction for the down matrix",
            ),
        ),
        _node(
            "reverse_down_matrix_support",
            "reverse down-matrix exterior support",
            "Computable carrier",
            "COMPUTED",
            "The reverse matter and Higgs lifts have exact rank-two exterior "
            "support. Four V2-V2 entries vanish structurally, four mixed "
            "entries reuse independent exact tree-boundary zero witnesses, "
            "and only the parameter-linear V1-V1 coefficient remains. This "
            "bounds the full matrix rank by one without computing its value.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_reverse_down_support.json",
                "research/experiments/scientific_genesis/"
                "mixed_schoen_reverse_down_support.py",
                "tests/integration/"
                "test_scientific_genesis_mixed_schoen_reverse_down_support.py",
            ),
            assumptions=(
                "published Wilson character assignment for the down sector",
            ),
            missing=(
                "six exact central determinant contractions and comparison homotopies",
            ),
        ),
        _node(
            "reverse_physical_v1_pluecker_pairing",
            "reverse physical V1 determinant pairing",
            "Computable carrier",
            "COMPUTED",
            "The two strict physical-character V1 matter classes pair into "
            "det(V1) through the certified local Pluecker matrices and an "
            "explicit hypersurface-overlap homotopy. Both cup orders are "
            "closed, their exchange difference has an exact primitive, and "
            "the projected pairing has strict forward character (0,2). Its "
            "reduced line coordinates vanish; no Yukawa value follows yet.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_v1_pluecker_chain_map.json",
                "research/experiments/scientific_genesis/"
                "mixed_schoen_v1_pluecker_chain_map.py",
                "tests/integration/"
                "test_scientific_genesis_mixed_schoen_v1_pluecker_chain_map.py",
            ),
            assumptions=(
                "published Wilson character assignment for the down sector",
            ),
            missing=(
                "common-chain comparison with the reverse central Higgs correction",
            ),
        ),
        _node(
            "strict_mixed_matter_representatives",
            "strict synchronized constituent matter classes",
            "Computable carrier",
            "COMPUTED",
            "Exact transferred P/T actions decompose V1 and V2 H1 into one "
            "and two copies of every deck character. Character projectors lift "
            "all 27 classes to strict full Schoen Cech--Koszul cocycles.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_matter_representatives.json",
                "research/experiments/scientific_genesis/"
                "mixed_schoen_matter_representatives.py",
                "tests/integration/"
                "test_scientific_genesis_mixed_schoen_matter_representatives.py",
            ),
            missing=(
                "parameter-dependent V2 corrections in the universal cone",
            ),
        ),
        _node(
            "universal_matter_sector_lifts",
            "minimum universal visible matter sectors",
            "Computable carrier",
            "COMPUTED",
            "For the two characters required by the first up-type matrix, all "
            "V2 matter classes have exact parameter-linear V1 corrections. "
            "Every coefficientwise cone identity and strict deck character "
            "holds over the full frozen P1 without selecting a point.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_universal_matter_lifts.json",
                "research/experiments/scientific_genesis/"
                "mixed_schoen_universal_matter_lifts.py",
                "research/experiments/scientific_genesis/"
                "mixed_schoen_common_dga.py",
                "tests/integration/"
                "test_scientific_genesis_mixed_schoen_universal_matter_lifts.py",
            ),
            assumptions=(
                "published Wilson character assignment for the up-type sector",
            ),
        ),
        _node(
            "higgs_determinant_twist_route",
            "determinant-twist Higgs comparison route",
            "Flavor",
            "REFUTED",
            "Both determinant-Hom orientations have exact cohomology "
            "(0,4,4,0) and exact Z3 x Z3 actions, but neither four-character "
            "representation matches the physical tensor characters under any "
            "uniform scalar shift.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_higgs_twist_audit.json",
                "research/experiments/scientific_genesis/"
                "mixed_schoen_higgs_twist_audit.py",
                "tests/integration/"
                "test_scientific_genesis_mixed_schoen_higgs_twist_audit.py",
            ),
            assumptions=(
                "rank-two determinant identity",
                "det(V2) = det(V1)^-1",
            ),
        ),
        _node(
            "higgs_direct_tensor_diagonal",
            "lawful mixed Higgs tensor diagonal",
            "Flavor",
            "COMPUTED",
            "The canonical four-factor independent-cover tensor and its "
            "three-equation fiber-diagonal Koszul complex are constructed "
            "without shared-cover flattening. Exhaustive exact evaluation "
            "proves D-squared zero on all 4,896 ambient transfer seeds.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_chain_diagonal.json",
                "research/experiments/scientific_genesis/"
                "mixed_schoen_chain_diagonal.py",
                "tests/integration/"
                "test_scientific_genesis_mixed_schoen_chain_diagonal.py",
                "data/generated/scientific_genesis/"
                "mixed_schoen_direct_tensor.json",
            ),
        ),
        _node(
            "strict_mixed_higgs_representative",
            "strict lawful tensor Higgs representative",
            "Flavor",
            "COMPUTED",
            "Exact Reynolds projectors reduce the lawful chain diagonal to "
            "forward P/T character (0,1), routed to physical H_d source "
            "character (0,2) by inverse pullback. Its 100-to-243-to-170 "
            "transfer has ranks 100 and 142, exact square zero, and a unique "
            "H1 class lifted to a strict 27-term full Cech--Koszul cocycle.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_chain_actions.json",
                "research/experiments/scientific_genesis/"
                "mixed_schoen_chain_transfer.py",
                "research/experiments/scientific_genesis/"
                "mixed_schoen_chain_actions.py",
                "tests/integration/"
                "test_scientific_genesis_mixed_schoen_chain_transfer.py",
            ),
            assumptions=("published Wilson character assignment",),
        ),
        _node(
            "mixed_matter_tensor_comparison",
            "direct matter-to-Higgs chain comparison",
            "Flavor",
            "COMPUTED",
            "Finite homological-perturbation projection and strict re-inclusion, "
            "followed by the normalized joint-character Reynolds projector, "
            "turn all four split matter products into distinct exact cycles of "
            "the grouped Higgs complex with character (0,2).",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_matter_comparison.json",
                "research/experiments/scientific_genesis/"
                "mixed_schoen_matter_comparison.py",
                "tests/integration/"
                "test_scientific_genesis_mixed_schoen_matter_comparison.py",
            ),
        ),
        _node(
            "mixed_scalar_trace_target",
            "mixed-Schoen scalar residue target",
            "Flavor",
            "COMPUTED",
            "The constituent virtual determinants have degrees (-2,2,0) and "
            "(2,-2,0), hence cancel exactly. Adjunction identifies the unique "
            "degree-three scalar target with the ordered ambient canonical "
            "Laurent residue generator.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_scalar_trace.json",
                "research/experiments/scientific_genesis/"
                "mixed_schoen_scalar_trace.py",
                "tests/integration/"
                "test_scientific_genesis_mixed_schoen_scalar_trace.py",
            ),
        ),
        _node(
            "mixed_local_determinant_pairings",
            "mixed-Schoen local determinant pairings",
            "Flavor",
            "COMPUTED",
            "Signed complementary maximal minors define the alternating forms "
            "on all twelve rank-two constituent quotient presentations. They "
            "annihilate every relation, factor their overlap differences by the "
            "appropriate hypersurface, and satisfy all sixty corrected "
            "covariance identities.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_determinant_pairing.json",
                "research/experiments/scientific_genesis/"
                "mixed_schoen_determinant_pairing.py",
                "tests/integration/"
                "test_scientific_genesis_mixed_schoen_determinant_pairing.py",
            ),
        ),
        _node(
            "mixed_tree_up_matrix",
            "lawful mixed-carrier tree-level up matrix",
            "Flavor",
            "COMPUTED",
            "The unique relative determinant-totalization orientation makes "
            "all four character-allowed products exact scalar cycles. Each "
            "has zero residue and an explicit depth-four primitive; the other "
            "five entries are character-forbidden, so the complete exact "
            "three-by-three tree-level matrix has rank zero.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_yukawa_trace.json",
                "research/experiments/scientific_genesis/"
                "mixed_schoen_yukawa_trace.py",
                "tests/integration/"
                "test_scientific_genesis_mixed_schoen_yukawa_trace.py",
            ),
        ),
        _node(
            "mixed_diagonal_local_comparison",
            "local common-to-diagonal pencil comparison",
            "Flavor",
            "COMPUTED",
            "The common-Schoen second pencil has exact lifts on the two "
            "independent-fiber q charts. Their difference is the Koszul "
            "syzygy of the independent pencil and diagonal equation. Required "
            "coefficient multidegrees contain negative q degree, proving that "
            "no global homogeneous polynomial lift can replace this Cech data.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_diagonal_comparison.json",
                "research/experiments/scientific_genesis/"
                "mixed_schoen_diagonal_comparison.py",
                "tests/integration/"
                "test_scientific_genesis_mixed_schoen_diagonal_comparison.py",
            ),
        ),
        _node(
            "mixed_diagonal_chain_map",
            "common-to-diagonal Cech chain map",
            "Flavor",
            "COMPUTED",
            "The two local pencil maps and their signed overlap homotopies "
            "extend to a basis-aware Cech chain map. Exact generator checks "
            "intertwine the full raw differential in all four Koszul "
            "summands, while the canonical diagonal tensor carries each "
            "constituent extension once rather than six times.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_chain_diagonal.json",
                "research/experiments/scientific_genesis/"
                "mixed_schoen_diagonal_chain_map.py",
                "tests/integration/"
                "test_scientific_genesis_mixed_schoen_diagonal_chain_map.py",
            ),
        ),
        _node(
            "mixed_matter_leg_deformation",
            "first universal matter-leg deformation term",
            "Flavor",
            "COMPUTED",
            "The family-symmetric a0 matter-leg product is transferred and "
            "projected exactly. Its character-(0,2) representative is not a "
            "cycle, and contraction with the strict Higgs remains nonclosed; "
            "the resulting partial scalar residue is exactly zero and is not "
            "a higher product or Yukawa entry.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_matter_leg_deformation.json",
                "research/experiments/scientific_genesis/"
                "mixed_schoen_matter_leg_deformation.py",
                "tests/integration/"
                "test_scientific_genesis_mixed_schoen_matter_leg_deformation.py",
            ),
            missing=(
                "exact Wilson character support for the next flavor sector",
            ),
        ),
        _node(
            "mixed_higgs_leg_deformation",
            "first universal Higgs-leg deformation lift",
            "Flavor",
            "COMPUTED",
            "The a0 extension action on the strict Higgs is an exact "
            "determinant-line cycle. A deterministic 1,431-term primitive "
            "supplies its parameter-linear correction. The exact local "
            "q-over-p identity and overlap homotopy map them to canonical "
            "2,124-term and 1,908-term determinant-line cochains.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_higgs_leg_deformation.json",
                "research/experiments/scientific_genesis/"
                "mixed_schoen_higgs_leg_deformation.py",
                "tests/integration/"
                "test_scientific_genesis_mixed_schoen_higgs_leg_deformation.py",
            ),
            missing=(
                "exact Wilson character support for the next flavor sector",
            ),
        ),
        _node(
            "mixed_v2_pluecker_chain_map",
            "equivariant V2 determinant pairing",
            "Flavor",
            "COMPUTED",
            "Full local Pluecker matrices and the exact hypersurface overlap "
            "homotopy pair the first source-derived V2 matter classes. Both "
            "cup orders close and differ by an explicit boundary; alternating "
            "determinant frames and Reynolds projection give a strict closed "
            "11,340-term representative of character (0,2).",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_v2_pluecker_chain_map.json",
                "research/experiments/scientific_genesis/"
                "mixed_schoen_v2_pluecker_chain_map.py",
                "tests/integration/"
                "test_scientific_genesis_mixed_schoen_v2_pluecker_chain_map.py",
            ),
            missing=(
                "exact Wilson character support for the next flavor sector",
            ),
        ),
        _node(
            "mixed_first_higher_product_coefficient",
            "first complete higher-product coefficient",
            "Flavor",
            "COMPUTED",
            "The fixed diagonal contraction gives a depth-three primitive for "
            "the grouped-to-Pluecker mismatch, and exact Reynolds averaging "
            "makes it descend. The resulting a0 lower-(1,1) scalar cochain is "
            "closed with 268,905 terms and has exact residue zero.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_first_higher_product.json",
                "research/experiments/scientific_genesis/"
                "mixed_schoen_first_higher_product.py",
                "tests/integration/"
                "test_scientific_genesis_mixed_schoen_first_higher_product.py",
            ),
            missing=(
                "exact Wilson character support for the next flavor sector",
            ),
        ),
        _node(
            "mixed_first_order_up_matrix",
            "complete universal first-order up matrix",
            "Flavor",
            "COMPUTED",
            "All four local-family pairs in both carrier directions have "
            "distinct exact complete-cochain certificates and zero residues. "
            "The two three-family coefficient matrices therefore vanish over "
            "Q(omega)[a0,a1], giving generic first-order rank zero without a "
            "selected projective parameter.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_first_order_matrix.json",
                "research/experiments/scientific_genesis/"
                "mixed_schoen_first_order_matrix.py",
                "tests/integration/"
                "test_scientific_genesis_mixed_schoen_first_order_matrix.py",
            ),
            missing=(
                "exact Wilson character support for the next flavor sector",
            ),
        ),
        _node(
            "mixed_up_yukawa_no_go",
            "universal holomorphic up-type branch theorem",
            "Flavor",
            "PROVED",
            "Exact parameter-linear matter and Higgs cocycles plus finite "
            "exterior-bidegree enumeration exclude every parameter order above "
            "one. The complete tree and first-order matrices both vanish, so "
            "the full universal up matrix has rank zero throughout the frozen "
            "P1 branch.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_up_yukawa_no_go.json",
                "research/experiments/scientific_genesis/"
                "mixed_schoen_up_yukawa_no_go.py",
                "tests/integration/"
                "test_scientific_genesis_mixed_schoen_up_yukawa_no_go.py",
            ),
            missing=(
                "exact Wilson character support for the next flavor sector",
            ),
        ),
        _node(
            "mixed_flavor_character_support",
            "source-pinned Yukawa character support",
            "Flavor",
            "COMPUTED",
            "The published matter and Higgs Wilson assignments give four "
            "exact invariant character triples. Reusing certified up-sector "
            "inputs leaves a minimum workload of seven new chain objects for "
            "the down sector, versus eight for Dirac neutrinos and eleven for "
            "charged leptons, without observational or carrier-point input.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_flavor_character_support.json",
                "research/experiments/scientific_genesis/"
                "mixed_schoen_flavor_character_support.py",
                "tests/integration/"
                "test_scientific_genesis_mixed_schoen_flavor_character_support.py",
                "data/published/visible_carrier/source_manifest.json",
            ),
            missing=(
                "universal matter lifts in character (1,0)",
                "strict Higgs representative in character (0,2)",
            ),
        ),
        _node(
            "mixed_down_higgs_chain_obstruction",
            "down-Higgs chain-character route",
            "Flavor",
            "REFUTED",
            "The exact current-chain character-(0,2) spaces have dimensions "
            "100, 243, and 176 with differential ranks 100 and 143, hence "
            "H1 dimension zero. The published multiplicity-one requirement is "
            "used only afterward, so no strict down-Higgs class is fabricated.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_down_higgs_action.json",
                "research/experiments/scientific_genesis/"
                "mixed_schoen_down_higgs_action.py",
                "tests/integration/"
                "test_scientific_genesis_mixed_schoen_down_higgs_action.py",
            ),
            missing=(
                "full local-semilinear constituent deck action on the "
                "synchronized chain, including overlap gauges",
            ),
        ),
        _node(
            "mixed_higgs_equivariant_comparison_obstruction",
            "current Higgs equivariant comparison route",
            "Flavor",
            "REFUTED",
            "An equivariant quasi-isomorphism must preserve every isotypic "
            "cohomology dimension. The source-derived P1 tensor has one "
            "character-(0,2) H1 class while the current synchronized chain has "
            "none. Both determinant-Hom orientations also fail. After accounting "
            "for the inverse generator on the second synchronized base, only the "
            "W1/P extension-line frame differs from its exact constituent atlas.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_higgs_equivariant_obstruction.json",
                "research/experiments/scientific_genesis/"
                "mixed_schoen_higgs_equivariant_obstruction.py",
                "tests/integration/"
                "test_scientific_genesis_mixed_schoen_higgs_equivariant_obstruction.py",
            ),
            missing=(
                "full local-semilinear constituent deck action on the synchronized chain",
                "overlap-gauge terms in the transferred action",
            ),
        ),
        _node(
            "mixed_higgs_scalar_action_no_go",
            "scalar Higgs-action repair routes",
            "Flavor",
            "REFUTED",
            "Replacing only the W1/P extension-line frame by its atlas value "
            "produces a nonzero 14-term chain commutator. Connectivity forces "
            "a scalar-only repair to rescale the full W1 complex by omega^2; "
            "that exact action shifts the target to legacy character (1,2), "
            "whose exact H1 dimension is still zero.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_higgs_scalar_action_no_go.json",
                "research/experiments/scientific_genesis/"
                "mixed_schoen_higgs_scalar_action_no_go.py",
                "tests/integration/"
                "test_scientific_genesis_mixed_schoen_higgs_scalar_action_no_go.py",
            ),
            missing=(
                "non-scalar local-semilinear W1/P chain comparison",
                "overlap-gauge-derived off-diagonal correction terms",
            ),
        ),
        _node(
            "mixed_higgs_full_character_audit",
            "complete synchronized Higgs character representation",
            "Flavor",
            "COMPUTED",
            "A single shared ambient transfer derives all nine exact character "
            "subcomplexes. Current H1 has characters (0,0), (0,1), (2,0), "
            "and (2,1). No uniform Z3 x Z3 character shift maps this multiset "
            "to the selected source Higgs representation.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_higgs_character_audit.json",
                "research/experiments/scientific_genesis/"
                "mixed_schoen_higgs_character_audit.py",
                "tests/integration/"
                "test_scientific_genesis_mixed_schoen_higgs_character_audit.py",
            ),
            assumptions=(
                "selected source Higgs characters used only after exact ranks",
            ),
            missing=(
                "atlas-derived non-scalar chain action",
                "or a proof that the source action is unrealizable on this complex",
            ),
        ),
        _node(
            "mixed_higgs_linearization_no_go",
            "same-constituent Higgs relinearization routes",
            "Flavor",
            "REFUTED",
            "Exact synchronized self-Hom differentials have ranks 53 of 54 "
            "for V1 and 123 of 124 for V2, so both selected constituents are "
            "simple over Q(omega). Two linearizations of a simple object differ "
            "by a character. Since all nine uniform tensor-character shifts "
            "already fail, no factorwise relinearization of these same objects "
            "can realize the selected source Higgs representation.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_higgs_linearization_no_go.json",
                "research/experiments/scientific_genesis/"
                "mixed_schoen_higgs_linearization_no_go.py",
                "tests/integration/"
                "test_scientific_genesis_mixed_schoen_higgs_linearization_no_go.py",
            ),
            assumptions=(
                "the repair keeps the same selected V1 and V2 objects",
                "the tensor action is induced from constituent linearizations",
            ),
            missing=(
                "direct atlas cohomology derivation of Higgs characters",
                "or a different exact constituent realization",
            ),
        ),
        _node(
            "mixed_atlas_higgs_character_incompatibility",
            "atlas-induced Higgs character representation",
            "Flavor",
            "REFUTED",
            "After homogeneous-lift normalization, the atlas-over-common "
            "ratios are (1,0) for W1 and (0,0) for W2. Simplicity therefore "
            "forces forward atlas Higgs characters (0,0), (0,1), (1,0), "
            "and (1,1). Inverse-pullback section conversion gives (0,0), "
            "(0,2), (2,0), and (2,2), incompatible with the selected source "
            "multiset. Raw line-entry ratios are not full-chain characters.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_atlas_higgs_characters.json",
                "research/experiments/scientific_genesis/"
                "mixed_schoen_atlas_higgs_characters.py",
                "tests/integration/"
                "test_scientific_genesis_mixed_schoen_atlas_higgs_characters.py",
            ),
            assumptions=(
                "the certified local atlases induce the factorwise tensor action",
            ),
            missing=(
                "atlas-derived characters for each relative-pushdown line",
                "the first exact source-convention mismatch",
            ),
        ),
        _node(
            "same_constituent_wilson_shift_no_go",
            "fixed-Wilson selection for all same-constituent shifts",
            "Computable carrier",
            "REFUTED",
            "The source-action tensor H1 support is {0,1} x {0,2}. Acyclic endpoint "
            "determinants identify it with exterior-square H1 for either "
            "nonsplit orientation. Simplicity makes every factorwise "
            "relinearization a character shift. Both Higgs doublets force "
            "shift (0,2) or (2,2); each retains one color triplet under the "
            "fixed Wilson embedding. The atlas-bound source-action shift "
            "(2,0) has no up doublet, one down doublet, and one antitriplet.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_wilson_shift_no_go.json",
                "research/experiments/scientific_genesis/"
                "mixed_schoen_wilson_shift_no_go.py",
                "tests/integration/"
                "test_scientific_genesis_mixed_schoen_wilson_shift_no_go.py",
            ),
            assumptions=(
                "the same selected simple V1 and V2 cover objects",
                "the fixed published Wilson embedding",
            ),
            missing=(
                "a distinct constituent realization or an independent "
                "correction of the full-chain H1 character premise",
            ),
        ),
        _node(
            "mixed_character_convention_correction",
            "source-action deck-character routing",
            "Flavor",
            "PROVED",
            "The synchronized chain labels forward pullback, while the source "
            "section representation uses inverse pullback. Exact factorwise "
            "inversion routes the certified 27-term forward-(0,1) cycle to "
            "physical H_d character (0,2); physical H_u character (0,1) has "
            "H1 dimension zero. The prior up, neutrino, and down-obstruction "
            "physical assignments are therefore invalid without changing a "
            "chain map or fitting a character.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_character_convention.json",
                "research/experiments/scientific_genesis/"
                "mixed_schoen_character_convention.py",
                "tests/integration/"
                "test_scientific_genesis_mixed_schoen_character_convention.py",
            ),
            missing=(
                "recomputed down holomorphic Yukawa matrix",
            ),
        ),
        _node(
            "universal_down_matter_lifts",
            "convention-corrected universal down-matter lifts",
            "Flavor",
            "COMPUTED",
            "Exact character inversion routes the physical source sectors "
            "(2,1) and (1,0) to forward-chain sectors (1,2) and (2,0). "
            "Those sectors contain two constant V1 classes and four V2 "
            "classes with eight independently solved parameter corrections; "
            "every cone identity and forward-character gate closes.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_down_matter_lifts.json",
                "research/experiments/scientific_genesis/"
                "mixed_schoen_down_matter_lifts.py",
                "tests/integration/"
                "test_scientific_genesis_mixed_schoen_down_matter_lifts.py",
            ),
        ),
        _node(
            "mixed_down_tree_matrix",
            "convention-corrected down tree matrix",
            "Flavor",
            "COMPUTED",
            "All four source/forward-corrected character-allowed determinant "
            "contractions have exact zero residue with independently "
            "reconstructed depth-four primitives. The complete associated-"
            "graded tree matrix therefore has exact rank zero; this result is "
            "scoped to tree order and does not erase universal corrections.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_down_tree_matrix.json",
                "research/experiments/scientific_genesis/"
                "mixed_schoen_down_tree_matrix.py",
                "tests/integration/"
                "test_scientific_genesis_mixed_schoen_down_tree_matrix.py",
            ),
        ),
        _node(
            "mixed_down_first_order_matrix",
            "complete universal convention-corrected down matrix",
            "Flavor",
            "PROVED",
            "All eight parameter and local-family coefficients are exact "
            "closed scalar cochains with distinct digests and zero residue. "
            "Both parameter coefficient matrices vanish. Exterior filtration "
            "allows no order above one, so the complete universal physical "
            "down matrix has exact rank zero on the frozen P1.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_down_first_order_matrix.json",
                "research/experiments/scientific_genesis/"
                "mixed_schoen_down_first_order_matrix.py",
                "tests/integration/"
                "test_scientific_genesis_mixed_schoen_down_first_order_matrix.py",
            ),
            missing=(
                "first nontrivial carrier-derived holomorphic Yukawa matrix",
            ),
        ),
        _node(
            "mixed_flavor_frontier",
            "superseded post-obstruction flavor frontier",
            "Flavor",
            "REFUTED",
            "Before source-action inversion was recognized, this scheduler "
            "selected a Dirac-neutrino interpretation of the forward sectors. "
            "The object count and no-observation gate remain exact, but the "
            "physical label is withdrawn by the convention certificate.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_flavor_frontier.json",
                "research/experiments/scientific_genesis/"
                "mixed_schoen_flavor_frontier.py",
                "tests/integration/"
                "test_scientific_genesis_mixed_schoen_flavor_frontier.py",
            ),
        ),
        _node(
            "universal_neutrino_matter_lifts",
            "forward-sector matter lifts with legacy neutrino label",
            "Flavor",
            "COMPUTED",
            "Characters (0,0) and (0,2) each have one exact constant V1 class "
            "and two exact parameter-linear V2 lifts. All eight independently "
            "computed carrier-parameter corrections satisfy the cone identity "
            "and strict deck-character gates over the full frozen P1. Their "
            "former Dirac-neutrino interpretation is withdrawn.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_neutrino_matter_lifts.json",
                "research/experiments/scientific_genesis/"
                "mixed_schoen_neutrino_matter_lifts.py",
                "tests/integration/"
                "test_scientific_genesis_mixed_schoen_neutrino_matter_lifts.py",
            ),
        ),
        _node(
            "mixed_neutrino_tree_matrix",
            "forward-sector tree matrix with legacy neutrino label",
            "Flavor",
            "COMPUTED",
            "All four character-allowed split-family determinant traces are "
            "exact scalar cycles with zero residue and explicit global "
            "primitives. The complete associated-graded three-family matrix "
            "therefore has exact rank zero. The physical neutrino label is "
            "withdrawn; this chain result is retained as exact input to the "
            "charged-lepton convention certificate.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_neutrino_tree_matrix.json",
                "research/experiments/scientific_genesis/"
                "mixed_schoen_neutrino_tree_matrix.py",
                "tests/integration/"
                "test_scientific_genesis_mixed_schoen_neutrino_tree_matrix.py",
            ),
        ),
        _node(
            "mixed_neutrino_first_order_matrix",
            "complete forward matrix with legacy neutrino label",
            "Flavor",
            "COMPUTED",
            "All eight parameter and local-family coefficients are exact "
            "closed scalar cochains with distinct digests and zero residue. "
            "Both parameter coefficient matrices vanish. Exterior filtration "
            "allows no order above one, so the complete forward-sector matrix "
            "has exact rank zero on the frozen P1. Its former Dirac-neutrino "
            "physical assignment is withdrawn.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_neutrino_first_order_matrix.json",
                "research/experiments/scientific_genesis/"
                "mixed_schoen_neutrino_first_order_matrix.py",
                "tests/integration/"
                "test_scientific_genesis_mixed_schoen_neutrino_first_order_matrix.py",
            ),
        ),
        _node(
            "mixed_charged_lepton_convention",
            "convention-corrected charged-lepton matrix",
            "Flavor",
            "PROVED",
            "Exact inverse-pullback routing identifies physical source matter "
            "characters (0,0) and (0,1) with the already-certified forward "
            "sectors (0,0) and (0,2), while physical H_d maps to forward "
            "character (0,1). The tree and both first-order coefficient "
            "matrices vanish, and exterior filtration excludes higher orders. "
            "The complete charged-lepton matrix therefore has exact rank zero.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_charged_lepton_convention.json",
                "research/experiments/scientific_genesis/"
                "mixed_schoen_charged_lepton_convention.py",
                "tests/integration/"
                "test_scientific_genesis_mixed_schoen_charged_lepton_convention.py",
            ),
            missing=(
                "exact replacement constituent or carrier realization with a "
                "nontrivial holomorphic Yukawa matrix",
            ),
        ),
        _node(
            "curvilinear_topology_route",
            "current curvilinear Chern-type route",
            "Scoped exclusions",
            "REFUTED",
            "The declared curvilinear rank-four topology has quotient index zero "
            "and cannot meet the required carrier target.",
            ("research/experiments/computable_carrier/tier_b_curvilinear_topology.py",),
        ),
        _node(
            "projective_tier_a_route",
            "declared projective Tier A outer route",
            "Scoped exclusions",
            "REFUTED",
            "All six declared projective ray pairs have zero invariant Ext-one "
            "classes in that finite presentation category.",
            ("research/experiments/computable_carrier/projective_outer_frontier.py",),
        ),
        _node(
            "common_dga_package",
            "carrier-specific common DGA package",
            "Flavor",
            "COMPUTED",
            "Generic DGA, module, contraction, and HPL engines exist; the lawful "
            "carrier, minimum universal matter sectors, and strict required "
            "Higgs cocycle are fixed. Exact equivariant comparison now supplies "
            "the four restricted matter-product cycles, while adjunction fixes "
            "their one-dimensional scalar residue target. The grouped "
            "determinant totalization is now exact and proves that every "
            "tree-level entry vanishes. The exact common-to-diagonal Cech "
            "chain map supplies the comparison required by the parameter-linear "
            "matter corrections. The first matter leg is exactly nonclosed with "
            "zero partial residue, while its complementary Higgs determinant-line "
            "correction is exact. The equivariant bottom V2 determinant pairing "
            "is also exact. Fixed-contraction comparison primitives close all "
            "eight parameter-linear coefficients with zero residue. Exterior "
            "filtration proves the complete up, down, and charged-lepton "
            "matrices vanish on the current carrier realization.",
            (
                "src/onetheory/math/homological.py",
                "data/generated/scientific_genesis/"
                "mixed_schoen_diagonal_comparison.json",
                "research/experiments/scientific_genesis/"
                "mixed_schoen_diagonal_chain_map.py",
                "data/generated/scientific_genesis/"
                "mixed_schoen_matter_leg_deformation.json",
                "data/generated/scientific_genesis/"
                "mixed_schoen_higgs_leg_deformation.json",
                "data/generated/scientific_genesis/"
                "mixed_schoen_v2_pluecker_chain_map.json",
                "data/generated/scientific_genesis/"
                "mixed_schoen_first_higher_product.json",
                "data/generated/scientific_genesis/"
                "mixed_schoen_first_order_matrix.json",
                "data/generated/scientific_genesis/"
                "mixed_schoen_up_yukawa_no_go.json",
                "data/generated/scientific_genesis/"
                "mixed_schoen_down_first_order_matrix.json",
                "data/generated/scientific_genesis/"
                "mixed_schoen_charged_lepton_convention.json",
                "research/experiments/visible_common_dga/audit.py",
            ),
        ),
        _node(
            "tree_holomorphic_flavor",
            "published tree-level holomorphic flavor structure",
            "Flavor",
            "PROVED",
            "The exact published one-Higgs tree texture and its rank-two/null "
            "structure are represented, conditional on the selected reference carrier.",
            ("src/onetheory/models/heterotic_schoen/flavor.py", "tests/unit/test_visible.py"),
            ("published reference carrier and conventions",),
        ),
        _node(
            "first_exact_yukawa",
            "first carrier-derived 3x3 holomorphic Yukawa matrix",
            "Flavor",
            "COMPUTED",
            "The selected published-reference carrier remains a scoped zero-"
            "matrix no-go. On the distinct stable descended alternate P1 "
            "carrier, complete actual chain witnesses produce an exact "
            "3x3 formal holomorphic up matrix. Its determinant is "
            "(-3/98-39*omega/196)*a1, so rank three holds precisely on "
            "a1 nonzero. No extension point, canonical metrics, or common "
            "vacuum has been selected; this is not a physical mass matrix.",
            (
                "data/generated/scientific_genesis/alternate_up_full_holomorphic_matrix.json",
                "research/experiments/scientific_genesis/alternate_up_full_matrix.py",
                "tests/integration/test_scientific_genesis_alternate_up_full_matrix.py",
                "data/generated/scientific_genesis/"
                "mixed_schoen_matter_leg_deformation.json",
                "data/generated/scientific_genesis/"
                "mixed_schoen_higgs_leg_deformation.json",
                "data/generated/scientific_genesis/"
                "mixed_schoen_v2_pluecker_chain_map.json",
                "data/generated/scientific_genesis/"
                "mixed_schoen_first_higher_product.json",
                "data/generated/scientific_genesis/"
                "mixed_schoen_first_order_matrix.json",
                "data/generated/scientific_genesis/"
                "mixed_schoen_up_yukawa_no_go.json",
                "data/generated/scientific_genesis/"
                "mixed_schoen_flavor_character_support.json",
                "data/generated/scientific_genesis/"
                "mixed_schoen_down_higgs_action.json",
                "data/generated/scientific_genesis/"
                "mixed_schoen_flavor_frontier.json",
                "data/generated/scientific_genesis/"
                "mixed_schoen_neutrino_first_order_matrix.json",
                "data/generated/scientific_genesis/"
                "mixed_schoen_down_first_order_matrix.json",
                "data/generated/scientific_genesis/"
                "mixed_schoen_charged_lepton_convention.json",
            ),
            ("selected heterotic UV realization", "fixed quotient volume frame"),
        ),
        _node(
            "alternate_metric_generation_reduction",
            "quotient-level extension global-generation criterion",
            "Normalization",
            "PROVED",
            "For an exact quotient bundle sequence 0 to A to E to B to 0, "
            "global generation of A and B plus H1(X,A)=0 imply global "
            "generation of E, uniformly in the extension parameter. "
            "The alternate carrier has not yet satisfied these premises.",
            (
                "research/experiments/scientific_genesis/"
                "ALTERNATE_METRIC_GENERATION_REDUCTION_NOTE.md",
                "data/generated/scientific_genesis/alternate_constituent_carrier_state.json",
            ),
            ("descended locally free extension", "descending positive twist"),
        ),
        _node(
            "alternate_metric_subbundle_vanishing",
            "first alternate constituent H1 vanishing at a descending twist",
            "Normalization",
            "COMPUTED",
            "At the declared mathematical twist (5,7,1), exact ambient "
            "Kunneth profiles and the genuine Serre/Hilbert--Burch sequences "
            "give cover H0(V1(H))=1728 and H1(V1(H))=0. The commuting "
            "deck lift and free-action character theorem give quotient "
            "H0=192 and H1=0. A rank-63 higher Koszul transgression is "
            "essential; the sparse first page alone is not final cohomology. "
            "The actual V1(H) is generated on the cover by the Serre "
            "extension criterion. Quotient constituent generation is unproved.",
            (
                "data/generated/scientific_genesis/alternate_metric_subbundle_vanishing.json",
                "research/experiments/scientific_genesis/alternate_metric_subbundle_vanishing.py",
                "research/experiments/scientific_genesis/"
                "ALTERNATE_METRIC_SUBBUNDLE_VANISHING_NOTE.md",
                "tests/integration/"
                "test_scientific_genesis_alternate_metric_subbundle_vanishing.py",
            ),
            ("published free Schoen quotient", "unchanged actual first constituent"),
        ),
        _node(
            "alternate_metric_quotient_generation",
            "alternate carrier quotient generation at an enlarged twist",
            "Normalization",
            "PROVED",
            "At the declared mathematical twist (14,16,1), both actual "
            "alternate constituents are globally generated on the quotient: "
            "Serre cover generation, a descending projected-orbit separator, "
            "and exact finite-group averaging prove invariant evaluation. "
            "The first constituent has H1=0 there, so the rank-four P1 "
            "family is globally generated with 5345 quotient sections. "
            "No complete rank-four invariant section "
            "basis or numerical metric is supplied.",
            (
                "data/generated/scientific_genesis/alternate_metric_quotient_generation.json",
                "research/experiments/scientific_genesis/"
                "alternate_metric_quotient_generation.py",
                "research/experiments/scientific_genesis/"
                "ALTERNATE_METRIC_QUOTIENT_GENERATION_NOTE.md",
                "tests/integration/"
                "test_scientific_genesis_alternate_metric_quotient_generation.py",
            ),
            ("published free Schoen quotient", "actual alternate constituent rays"),
        ),
        _node(
            "alternate_metric_first_subline_sections",
            "actual first Serre subline invariant section basis",
            "Normalization",
            "COMPUTED",
            "At H=(14,16,1), the frozen determinant-repaired first "
            "Serre subline has an explicit 1115-vector quotient basis. "
            "The projected Schoen eliminant is deck invariant; exact "
            "orbit sums and an 880-rank ideal quotient construct the basis. "
            "The full constituent and rank-four section bases remain open.",
            (
                "data/generated/scientific_genesis/"
                "alternate_metric_first_subline_sections.json",
                "research/experiments/scientific_genesis/"
                "alternate_metric_first_subline_sections.py",
                "research/experiments/scientific_genesis/"
                "ALTERNATE_METRIC_FIRST_SUBLINE_SECTIONS_NOTE.md",
                "tests/integration/"
                "test_scientific_genesis_alternate_metric_first_subline_sections.py",
            ),
            ("frozen alternate common flat character", "published Schoen cubics"),
        ),
        _node(
            "alternate_metric_first_resolution_ambient_sections",
            "actual first resolution ambient invariant section bases",
            "Normalization",
            "COMPUTED",
            "At H=(14,16,1), exact determinant-repaired block orbit sums "
            "give 13338 F0 and 7524 F1 ambient invariant sections. An "
            "independent integer-ring replay reproduces both complete "
            "stream hashes. Schoen restriction, the Hilbert-Burch quotient, "
            "and Serre lifts remain necessary for a constituent basis.",
            (
                "data/generated/scientific_genesis/"
                "alternate_metric_first_resolution_ambient_sections.json",
                "research/experiments/scientific_genesis/"
                "alternate_metric_first_resolution_ambient_sections.py",
                "research/experiments/scientific_genesis/"
                "ALTERNATE_METRIC_FIRST_RESOLUTION_AMBIENT_SECTIONS_NOTE.md",
                "tests/integration/"
                "test_scientific_genesis_alternate_metric_first_resolution_ambient_sections.py",
            ),
            ("frozen alternate common flat character", "declared metric twist"),
        ),
        _node(
            "alternate_metric_first_quotient_sections",
            "actual first Serre quotient invariant section basis",
            "Normalization",
            "COMPUTED",
            "The equivariant Hilbert-Burch cokernel is the coordinate-point "
            "ideal at degree (13,17,2) with frame (omega^2,omega^2). "
            "Its exact ideal Koszul presentation has 5814 target vectors, "
            "5114 relations, and an 840-dimensional syzygy space. An "
            "independently replayed nonzero integral minor gives an explicit "
            "1540-vector Q(omega) quotient section basis. This quotient "
            "artifact alone contains no nonsplit Serre or outer lifts.",
            (
                "data/generated/scientific_genesis/alternate_metric_first_quotient_sections.json",
                "data/generated/scientific_genesis/"
                "alternate_metric_first_quotient_sections.relations.json.gz",
                "research/experiments/scientific_genesis/alternate_metric_first_quotient_sections.py",
                "research/experiments/scientific_genesis/"
                "ALTERNATE_METRIC_FIRST_QUOTIENT_SECTIONS_NOTE.md",
                "tests/integration/"
                "test_scientific_genesis_alternate_metric_first_quotient_sections.py",
            ),
            ("actual coordinate-point ideal", "source-checked ideal Koszul regularity"),
        ),
        _node(
            "alternate_metric_first_serre_lifts",
            "actual first constituent complete invariant section basis",
            "Normalization",
            "COMPUTED",
            "At H=(14,16,1), nine actual full-differential lift templates "
            "transport by polynomial plane factors to all 1540 first "
            "Serre-quotient sections. Together with the 1115 subline "
            "sections they give a complete 2655-vector V1 basis. Every "
            "archived cochain has independent exact closure, repaired "
            "deck-invariance, and quotient-image replay. The separately "
            "certified universal outer constructor consumes this basis; "
            "local rank-four evaluation and numerical metrics remain missing.",
            (
                "data/generated/scientific_genesis/alternate_metric_first_serre_lifts.json",
                "data/generated/scientific_genesis/"
                "alternate_metric_first_serre_lifts.sections.json.gz",
                "research/experiments/scientific_genesis/alternate_metric_first_serre_lifts.py",
                "research/experiments/scientific_genesis/"
                "ALTERNATE_METRIC_FIRST_SERRE_LIFTS_NOTE.md",
                "tests/integration/"
                "test_scientific_genesis_alternate_metric_first_serre_lifts.py",
            ),
            ("actual non-split first Serre extension", "certified H0 quotient and subline bases"),
        ),
        _node(
            "alternate_metric_second_sections",
            "actual alternate second constituent complete invariant section basis",
            "Normalization",
            "COMPUTED",
            "The actual I6 ray (0,1) at H=(14,16,1) has a complete "
            "2690-vector V2 basis: 1135 subline sections plus 1555 "
            "nonsplit quotient lifts. Stabilizer-normalized orbits include "
            "fixed monomials; the fat-axis ideal Koszul presentation has "
            "an independently verified exact 4337-rank minor. Twelve "
            "full-differential templates transport the lifts. Every "
            "section and relation has independent coefficient replay. "
            "The separately certified universal outer constructor consumes "
            "this basis; local evaluation and metric convergence remain open.",
            (
                "data/generated/scientific_genesis/alternate_metric_second_sections.json",
                "data/generated/scientific_genesis/"
                "alternate_metric_second_sections.sections.json.gz",
                "data/generated/scientific_genesis/"
                "alternate_metric_second_sections.relations.json.gz",
                "research/experiments/scientific_genesis/alternate_metric_second_sections.py",
                "research/experiments/scientific_genesis/"
                "ALTERNATE_METRIC_SECOND_SECTIONS_NOTE.md",
                "tests/integration/"
                "test_scientific_genesis_alternate_metric_second_sections.py",
            ),
            ("actual alternate I6 ray (0,1)", "common determinant-repair character [1,2]"),
        ),
        _node(
            "alternate_metric_outer_lift_formula",
            "finite universal metric-section lift constructor",
            "Normalization",
            "DERIVED",
            "Every actual V1(H) ambient component has reduced degree at "
            "most zero. The full mixed-arrow filtration makes (h Delta)^5 "
            "zero, yielding a finite primitive for every degree-one outer "
            "residual. An exact constructor covers all 5345 basis indices "
            "without an extension-point choice. Four actual coefficient "
            "probes are checked; full independent rank-four replay and "
            "numerical metrics remain unavailable.",
            (
                "data/generated/scientific_genesis/alternate_metric_outer_lifts.json",
                "research/experiments/scientific_genesis/alternate_metric_outer_lifts.py",
                "research/experiments/scientific_genesis/ALTERNATE_METRIC_OUTER_LIFTS_NOTE.md",
                "tests/integration/test_scientific_genesis_alternate_metric_outer_lifts.py",
            ),
            ("actual target differential", "standard cover contraction identities"),
        ),
        _node(
            "alternate_metric_lift_operator_certificate",
            "independently certified universal metric-section lift operators",
            "Normalization",
            "DERIVED",
            "All 256 Laurent support patterns in both grading parities "
            "pass independent integer incidence and raw contraction checks. "
            "Twenty actual source-module columns certify both outer "
            "composition identities, agreeing with the constructor's cup. "
            "The actual repaired target arrows and equation units certify "
            "averaging. A finite residual-iteration proof establishes the "
            "5345-vector universal invariant section construction without "
            "expanded coefficient replay or an extension-point choice. "
            "Local fiber evaluation is supplied by a separate artifact; "
            "controlled numerical metrics remain open.",
            (
                "data/generated/scientific_genesis/"
                "alternate_metric_lift_operator_certificate.json",
                "research/experiments/scientific_genesis/"
                "alternate_metric_lift_operator_certificate.py",
                "research/experiments/scientific_genesis/"
                "ALTERNATE_METRIC_LIFT_OPERATOR_CERTIFICATE_NOTE.md",
                "tests/integration/"
                "test_scientific_genesis_alternate_metric_lift_operator_certificate.py",
            ),
            ("established actual constituent differentials square to zero",
             "complete independently certified constituent section bases"),
        ),
        _node(
            "alternate_metric_fiber_evaluation",
            "actual symbolic rank-four local fiber evaluation",
            "Normalization",
            "COMPUTED",
            "The actual nine generators and five local relations yield an "
            "explicitly based rank-four quotient over Q(omega)[a0,a1]. "
            "All boundary identities and its nonzero triangular minor hold "
            "for every parameter. Four actual basis sections span an exact "
            "cover-point fiber without a parameter choice. On-demand section "
            "evaluation is available; full metric sampling and convergence "
            "remain unresolved.",
            (
                "data/generated/scientific_genesis/alternate_metric_fiber_evaluation.json",
                "research/experiments/scientific_genesis/alternate_metric_fiber_evaluation.py",
                "research/experiments/scientific_genesis/ALTERNATE_METRIC_FIBER_EVALUATION_NOTE.md",
                "tests/integration/test_scientific_genesis_alternate_metric_fiber_evaluation.py",
            ),
            ("both actual cover equations", "explicit chart line frames and quotient pivot rows",
             "independently certified actual universal section constructor"),
        ),
        _node(
            "alternate_metric_specialized_evaluation",
            "complete exact point evaluation of the universal section basis",
            "Normalization",
            "COMPUTED",
            "Regular second-plane coefficient specialization commutes with "
            "the actual raw homotopy and specialized object/equation arrows. "
            "Three separate deck channels retain all geometric phases. "
            "The complete 5345-column point matrix keeps both parameters "
            "symbolic and reproduces four independent full-cochain probes. "
            "It is not controlled numerical sampling or a metric certificate.",
            (
                "data/generated/scientific_genesis/alternate_metric_specialized_evaluation.json",
                "data/generated/scientific_genesis/"
                "alternate_metric_specialized_evaluation.matrix.json.gz",
                "research/experiments/scientific_genesis/"
                "alternate_metric_specialized_evaluation.py",
                "research/experiments/scientific_genesis/"
                "ALTERNATE_METRIC_SPECIALIZED_EVALUATION_NOTE.md",
                "tests/integration/"
                "test_scientific_genesis_alternate_metric_specialized_evaluation.py",
            ),
            ("all actual target second-plane support stays nonnegative",
             "actual deck coordinate phases and explicit chart line frames"),
        ),
        _node(
            "alternate_metric_measure",
            "actual-cover residue and normalized auxiliary integration measure",
            "Normalization",
            "COMPUTED",
            "The actual cubic pencils give an explicitly oriented double residue "
            "and exact affine tangent frames. The normalized FS auxiliary form "
            "has cover mass nine; quotient importance weights divide separately "
            "by the declared free covering degree. Both actual deck generators "
            "preserve the residue and FS forms. Independent mixed-wedge and "
            "chart-transition checks support this integration prerequisite, "
            "not a numerical sampler or a converged metric.",
            (
                "data/generated/scientific_genesis/alternate_metric_measure.json",
                "research/experiments/scientific_genesis/alternate_metric_measure.py",
                "research/experiments/scientific_genesis/ALTERNATE_METRIC_MEASURE_NOTE.md",
                "tests/integration/test_scientific_genesis_alternate_metric_measure.py",
            ),
            ("actual frozen Schoen equations", "explicit chart and volume-form conventions",
             "independent SU-uniform projective intersection sampling law",
             "free ninefold quotient for descended invariant integrands"),
        ),
        _node(
            "alternate_metric_weight_moments",
            "actual auxiliary-law importance-weight integrability",
            "Normalization",
            "DERIVED",
            "The two actual pencils have square-free degree-six critical "
            "supports with gcd one and no critical infinity fiber. Each has "
            "three axis-node fibers and three triangular fibers. The local "
            "density proof gives A comparable to squared transverse radius "
            "along the critical curves: the importance weight has finite "
            "q-moment exactly for nonnegative q below three. Its variance is "
            "finite but its third moment diverges. This is an integrability "
            "theorem for the ideal A/9 law, not a quantitative variance bound, "
            "implemented sampler, metric, or physical normalization.",
            (
                "data/generated/scientific_genesis/alternate_metric_weight_moments.json",
                "research/experiments/scientific_genesis/alternate_metric_weight_moments.py",
                "research/experiments/scientific_genesis/ALTERNATE_METRIC_WEIGHT_MOMENTS_NOTE.md",
                "tests/integration/test_scientific_genesis_alternate_metric_weight_moments.py",
            ),
            ("actual frozen cubic pencils", "auxiliary probability law A/9",
             "nonzero residue volume-form convention"),
        ),
        _node(
            "alternate_metric_positive_measure",
            "positive auxiliary mixture with globally bounded importance weights",
            "Normalization",
            "DERIVED",
            "The positive ambient FS sum has cube mass 72 on the unchanged "
            "actual cover. Its normalized law is the exact 3/4,1/8,1/8 "
            "mixture of nine-root and two three-root projective intersection "
            "laws. Strict positivity and compactness bound its ideal importance "
            "weight globally, so all nonnegative moments are finite. Actual "
            "three-root branches and 18 regular-chart density enclosures are "
            "verified. No numerical global bound, critical-fiber chart engine, "
            "controlled sampler, physical Kahler class, or metric is supplied.",
            (
                "data/generated/scientific_genesis/alternate_metric_positive_measure.json",
                "research/experiments/scientific_genesis/alternate_metric_positive_measure.py",
                "research/experiments/scientific_genesis/ALTERNATE_METRIC_POSITIVE_MEASURE_NOTE.md",
                "tests/integration/test_scientific_genesis_alternate_metric_positive_measure.py",
            ),
            ("actual smooth compact cover", "explicit auxiliary FS convention"),
        ),
        _node(
            "alternate_metric_critical_charts",
            "certified point-line roots and critical-fiber projection densities",
            "Normalization",
            "COMPUTED",
            "Base-eliminating charts enclose signed residues and the unchanged "
            "positive FS-cube density on all three partner roots of each of "
            "the six actual axis-critical fibers. Complete point-line root "
            "certificates preserve exact source membership. Independent full "
            "wedge determinants, regular-chart overlap Jacobians, and base "
            "pivot transitions verify the coordinate conventions. These 18 "
            "declared domains are not all triangle-node input certificates, "
            "global atlas coverage, a quantitative global bound, or a sampler.",
            (
                "data/generated/scientific_genesis/alternate_metric_critical_charts.json",
                "research/experiments/scientific_genesis/alternate_metric_critical_charts.py",
                "research/experiments/scientific_genesis/ALTERNATE_METRIC_CRITICAL_CHARTS_NOTE.md",
                "tests/integration/test_scientific_genesis_alternate_metric_critical_charts.py",
            ),
            ("same actual pencils", "nonzero declared eliminated-coordinate Jacobians"),
        ),
        _node(
            "projective_uniform_input_cells",
            "controlled coupled input cells for the auxiliary projective law",
            "Normalization",
            "DERIVED",
            "Uniform simplex spacings and independent phases give normalized FS "
            "point and dual-hyperplane laws on CP1 and CP2. Exact rational "
            "analytic remainders enclose each complete supplied dyadic input "
            "cell in coupled homogeneous-coordinate disks, including tied bins "
            "and zero weights. Independent simplex moments and Chudnovsky "
            "endpoint checks attack the construction. This is conditional "
            "on independent uniform input bits: this input packet alone supplies "
            "no RNG, intersection roots, cover cloud, or numerical metric.",
            ("research/experiments/scientific_genesis/projective_uniform_input_cells.py",
             "research/experiments/scientific_genesis/PROJECTIVE_UNIFORM_INPUT_CELLS_NOTE.md",
             "tests/integration/test_scientific_genesis_projective_uniform_input_cells.py",
             "data/generated/scientific_genesis/projective_uniform_input_cells.json"),
            ("explicit auxiliary FS convention", "independent uniform input cell indices"),
            ("branch-complete roots for uncertain inputs", "independent cover draws",
             "integrand error control", "Ricci-flat/HYM convergence"),
        ),
        _node(
            "projective_uncertain_intersections",
            "uniform actual-cover root inclusions on admitted input cells",
            "Normalization",
            "COMPUTED",
            "The unchanged actual Schoen pencils have all nine, three, and "
            "three projective roots enclosed for the three declared auxiliary "
            "mixture input cells. A fourth actual leading-zero coefficient cell "
            "retains a moving infinity root in a positive reciprocal-chart disk. "
            "Coefficient-error Rouche margins and projective disjointness "
            "certify completeness uniformly over each admitted cell. Independent "
            "Fraction-pair Taylor reconstruction and original exact substitutions "
            "verify critical arithmetic. Coupled cover-coordinate bounds retain "
            "input and root errors; this is not global input coverage, an "
            "independent sampling cloud, an integral, or a physical metric.",
            ("research/experiments/scientific_genesis/projective_uncertain_intersections.py",
             "research/experiments/scientific_genesis/PROJECTIVE_UNCERTAIN_INTERSECTIONS_NOTE.md",
             "tests/integration/test_scientific_genesis_projective_uncertain_intersections.py",
             "data/generated/scientific_genesis/projective_uncertain_intersections.json"),
            ("explicit line and parameter frames", "certified nonzero pivots",
             "strict uniform root margins", "actual unchanged cubic pencils"),
            ("law-preserving independent bit-stream workflow", "new-domain integrand bounds",
             "integration error control", "Ricci-flat/HYM convergence"),
        ),
        _node(
            "uncertain_cover_weights",
            "unchanged auxiliary weights on actual coupled uncertain cover families",
            "Normalization",
            "COMPUTED",
            "Actual same-base or source-derived root restrictions certify coupled "
            "cover families on the admitted input cells. The established homogeneous "
            "conormal identity encloses all 9/3/3 auxiliary weights, retaining source "
            "and root error with positive full denominators. Independent full FS "
            "determinants at exact cover points and Fraction-pair coordinate "
            "functionals check the arithmetic. Raw coordinate balls are not "
            "membership certificates. These bounds are not an independent cloud, "
            "a section integrand, an integral, a metric or a stabilized prediction.",
            ("research/experiments/scientific_genesis/uncertain_cover_weights.py",
             "research/experiments/scientific_genesis/UNCERTAIN_COVER_WEIGHTS_NOTE.md",
             "tests/integration/test_scientific_genesis_uncertain_cover_weights.py",
             "data/generated/scientific_genesis/uncertain_cover_weights.json"),
            ("actual coupled root certificates", "positive norm and conormal bounds",
             "declared residue scale and covering degree"),
            ("independent law-preserving draws", "complete original section integrands",
             "controlled integration errors", "Ricci-flat/HYM convergence", "common vacuum"),
        ),
        _node(
            "auxiliary_cover_draws",
            "law-preserving prefix refinement for auxiliary cover draws",
            "Normalization",
            "DERIVED",
            "Independent fair bit streams conditionally realize the exact "
            "3/4,1/8,1/8 auxiliary mixture and uniform complete-root choices. "
            "Whole projective input cells feed the native coupled restrictions. "
            "Prefix exhaustion or numerical failure retains the same request; "
            "admitted root refinement requires bijective projective disk "
            "containment, not the order of sorted centers. This conditional "
            "workflow does not prove its input independence, global numerical "
            "coverage, complete section integrands or a controlled integral.",
            ("research/experiments/scientific_genesis/auxiliary_cover_draws.py",
             "research/experiments/scientific_genesis/AUXILIARY_COVER_DRAWS_NOTE.md",
             "tests/integration/test_scientific_genesis_auxiliary_cover_draws.py",
             "data/generated/scientific_genesis/auxiliary_cover_draws.json"),
            ("mutually independent infinite fair named bit streams",
             "actual coupled root certificates", "explicit unchanged line frames"),
            ("externally justified independent draws", "global numerical input coverage",
             "complete section integrands", "controlled integration errors",
             "Ricci-flat/HYM convergence", "common stabilized vacuum"),
        ),
        _node(
            "uncertain_cover_frames",
            "original universal bundle frames on uncertain-input cover domains",
            "Normalization",
            "COMPUTED",
            "All fifteen declared coupled input families admit the original "
            "nine-generator/five-relation quotient with named free basis and "
            "nonzero determinant enclosures. The original full cochain sections "
            "0 and 2655 are bounded on each domain, retaining both 3663-term "
            "outer corrections and formal a0/a1. Explicit 100-bit uncertain "
            "center rounding adds a certified displacement error; exact singleton "
            "inputs remain exact and the old default is unchanged. Independent "
            "raw-arrow Gaussian quotients check every branch; full corrected "
            "affine-polynomial functionals check each mixture component and "
            "the existing finite-support evaluator. Input/root refinement "
            "contracts actual outer-section error. These declared probe domains "
            "are not independent samples or complete section integrands.",
            ("research/experiments/scientific_genesis/UNCERTAIN_COVER_FRAMES_NOTE.md",
             "research/experiments/scientific_genesis/projective_uncertain_intersections.py",
             "research/experiments/scientific_genesis/alternate_metric_bounded_fibers.py",
             "research/experiments/scientific_genesis/uncertain_cover_frames.py",
             "tests/integration/test_scientific_genesis_uncertain_cover_frames.py",
             "tests/integration/test_scientific_genesis_rounded_centers.py",
             "data/generated/scientific_genesis/uncertain_cover_frames.json"),
            ("actual coupled root family", "explicit homogeneous and relation pivots",
             "explicit radius and uncertain-center precisions"),
        ),
        _node(
            "alternate_metric_projection_free_weights",
            "projection-free positive-law weights from the ambient conormal Gram",
            "Normalization",
            "DERIVED",
            "The Hermitian Schur-complement identity cancels the tangent-chart "
            "Jacobian from the residue-to-FS-cube ratio. The original sparse "
            "equation Jacobian gives a positive three-term conormal determinant "
            "with no individual fiber-gradient inverse. Full ambient inverse "
            "and determinant checks, original exact points, and all 36 declared "
            "regular/axis-critical domain enclosures agree. The formula is valid "
            "on smooth cover charts, including critical fibers; no global input "
            "atlas, quantitative bound, controlled sampler, or metric is supplied.",
            (
                "data/generated/scientific_genesis/alternate_metric_projection_free_weights.json",
                "research/experiments/scientific_genesis/alternate_metric_projection_free_weights.py",
                "research/experiments/scientific_genesis/"
                "ALTERNATE_METRIC_PROJECTION_FREE_WEIGHTS_NOTE.md",
                "tests/integration/"
                "test_scientific_genesis_alternate_metric_projection_free_weights.py",
            ),
            ("same actual smooth cover", "unchanged positive auxiliary law"),
        ),
        _node(
            "alternate_metric_global_weight_bound",
            "quantitative global positive-law weight bound from polynomial identities",
            "Normalization",
            "DERIVED",
            "Full homogeneous polynomial certificates for the original surface "
            "gradients and disjoint critical supports give an explicit positive "
            "global conormal lower bound. Independent Fraction-pair convolution "
            "checks every saved identity. The auxiliary positive-law weight and "
            "its ideal variance have conservative quantitative bounds, not "
            "practical sampling costs, matrix integrand bounds, or physical metrics.",
            ("data/generated/scientific_genesis/alternate_metric_global_weight_bound.json",
             "research/experiments/scientific_genesis/alternate_metric_global_weight_bound.py",
             "research/experiments/scientific_genesis/ALTERNATE_METRIC_GLOBAL_WEIGHT_BOUND_NOTE.md",
             "tests/integration/test_scientific_genesis_alternate_metric_global_weight_bound.py"),
            ("same actual pencils", "unit homogeneous representatives for auxiliary FS norms"),
        ),
        _node(
            "alternate_metric_projective_roots",
            "certified complete projective intersections for exact sampling inputs",
            "Normalization",
            "COMPUTED",
            "Declared Q(omega) line/point/line configurations restrict the actual "
            "pencils to homogeneous cubics. Exact Taylor/Rouche inequalities "
            "give one-root disks; disjointness and degree prove completeness. "
            "Simple infinity roots are retained explicitly, so each accepted "
            "configuration has all nine algebraic intersection points. "
            "Proposal centers are not exact cover points. The SU-uniform "
            "sampling law and complete bounded section evaluation remain open.",
            (
                "data/generated/scientific_genesis/alternate_metric_projective_roots.json",
                "research/experiments/scientific_genesis/alternate_metric_projective_roots.py",
                "research/experiments/scientific_genesis/ALTERNATE_METRIC_PROJECTIVE_ROOTS_NOTE.md",
                "tests/integration/test_scientific_genesis_alternate_metric_projective_roots.py",
            ),
            ("exact Q(omega) configuration inputs", "explicit line bases and parameter charts",
             "transverse cubic intersections", "declared precision and work-cap policy"),
        ),
        _node(
            "alternate_metric_enclosures",
            "certified actual chart, coefficient, and geometric density enclosures",
            "Normalization",
            "COMPUTED",
            "Exact rational circular bounds propagate actual root certificates "
            "through declared homogeneous pivots, projection derivatives, residue, "
            "and FS densities. Both complete nine-root probes have positive "
            "importance bounds, including infinity. Actual local Laurent "
            "constituent coefficients have independent archive checks. These "
            "are ambient generator bounds, not the universal rank-four quotient "
            "or a complete bounded section matrix. No sampling law or metric "
            "convergence has been supplied.",
            (
                "data/generated/scientific_genesis/alternate_metric_enclosures.json",
                "research/experiments/scientific_genesis/alternate_metric_enclosures.py",
                "research/experiments/scientific_genesis/ALTERNATE_METRIC_ENCLOSURES_NOTE.md",
                "tests/integration/test_scientific_genesis_alternate_metric_enclosures.py",
            ),
            ("certified actual-pencil roots", "explicit nonzero pivots and projection Jacobians",
             "declared outward bound precision", "unchanged residue/FS conventions"),
        ),
        _node(
            "alternate_metric_bounded_fibers",
            "determinant-certified universal rank-four quotient enclosures",
            "Normalization",
            "COMPUTED",
            "The original differential and outer cup supply all actual local "
            "relations. Explicit constituent pivot minors exclude zero and "
            "exact block elimination proves the universal quotient identities "
            "for symbolic a0,a1. Finite and infinity probes have named frame "
            "bounds and an actual outer-corrected section, independently checked "
            "against full five-row symbolic/Gaussian elimination and the original "
            "point archive. Original-cochain bounds are available on demand; "
            "compressed complete-matrix throughput and controlled integration "
            "remain unestablished.",
            (
                "data/generated/scientific_genesis/alternate_metric_bounded_fibers.json",
                "research/experiments/scientific_genesis/alternate_metric_bounded_fibers.py",
                "research/experiments/scientific_genesis/ALTERNATE_METRIC_BOUNDED_FIBERS_NOTE.md",
                "tests/integration/test_scientific_genesis_alternate_metric_bounded_fibers.py",
            ),
            ("certified actual cover-point enclosures", "explicit relation pivot rows",
             "original nonsplit Serre and outer coefficients", "nonzero determinant enclosures"),
        ),
        _node(
            "alternate_metric_bounded_support",
            "bounded original section evaluation through finite pole sectors",
            "Normalization",
            "COMPUTED",
            "The certified finite-pole representation now carries circular "
            "coefficient bounds on original labels. Original exact homotopy, "
            "perturbation, and deck unit columns extend linearly; uncertain "
            "zeros remain present and the actual finite filtration controls "
            "termination. Every original basis index is accepted. Three "
            "indices are saved on finite and infinity domains, with independent "
            "full-cochain and exact archive checks. This predecessor packet "
            "does not materialize the complete matrix; the separate complete-output "
            "certificate supplies that gate. Multi-point throughput remains open.",
            (
                "data/generated/scientific_genesis/alternate_metric_bounded_support.json",
                "research/experiments/scientific_genesis/alternate_metric_bounded_support.py",
                "research/experiments/scientific_genesis/ALTERNATE_METRIC_BOUNDED_SUPPORT_NOTE.md",
                "tests/integration/test_scientific_genesis_alternate_metric_bounded_support.py",
            ),
            ("certified determinant-invertible local frames", "same original finite-pole encoding",
             "original finite filtration", "explicit outward coefficient precision"),
        ),
        _node(
            "alternate_metric_bounded_matrix",
            "complete bounded original section output on a certified local domain",
            "Normalization",
            "COMPUTED",
            "All 5345 original bounded columns are stored on the declared "
            "finite-chart domain at the original 80-bit radius mesh. The "
            "read-only consumer independently parses every column, verifies "
            "compressed and raw stream hashes, original parents and frame labels, "
            "and exact agreement with predecessor probes 0,1273,2655. "
            "Single-domain completion does not certify practical multi-point "
            "throughput, requested relative accuracy, sampling, or metrics.",
            (
                "data/generated/scientific_genesis/alternate_metric_bounded_matrix.json",
                "data/generated/scientific_genesis/"
                "alternate_metric_bounded_matrix.columns.jsonl.gz",
                "research/experiments/scientific_genesis/alternate_metric_bounded_matrix.py",
                "research/experiments/scientific_genesis/ALTERNATE_METRIC_BOUNDED_MATRIX_NOTE.md",
                "tests/integration/test_scientific_genesis_alternate_metric_bounded_matrix.py",
            ),
            ("actual original basis ordering", "certified determinant-invertible local domain",
             "same bounded evaluator", "independent complete stream validation"),
        ),
        _node(
            "visible_metrics",
            "Ricci-flat, HYM, and matter metric package",
            "Normalization",
            "BLOCKED",
            "The alternate carrier is globally generated at a declared "
            "ample twist. Both actual constituents have complete invariant "
            "section bases of sizes 2655 and 2690. Its universal rank-four "
            "lifting formula is independently certified and exact local "
            "rank-four evaluation is available with a complete exact point "
            "matrix. The actual residue and normalized auxiliary integration "
            "measure are explicit. Complete projective roots have exact "
            "inclusion certificates for declared Q(omega) configurations. "
            "Actual chart, Laurent-coefficient, and density errors are bounded, "
            "and universal quotient frames now have certified bounds on declared "
            "pivot domains. Full original-cochain section evaluation is bounded "
            "on demand. The original finite-pole engine also carries certified "
            "coefficient bounds for every archived index. The complete bounded "
            "matrix is certified on one declared domain, and exact polynomial "
            "identities give a conservative global auxiliary weight bound. "
            "Practical multi-point throughput, controlled sampling "
            "and converged Ricci-flat/HYM matter metrics are not yet available. The "
            "published reference still lacks complete carrier cocycles.",
            ("src/onetheory/math/sections.py", "research/experiments/visible_metrics/audit.py"),
            missing=(
                "controlled numerical full-basis evaluation and metric sampling",
                "converged Ricci-flat and HYM metrics",
            ),
        ),
        _node(
            "physical_yukawas",
            "canonically normalized physical Yukawas",
            "Normalization",
            "BLOCKED",
            "Canonical-normalization laws and complete alternate holomorphic "
            "up/down/lepton/neutrino matrices exist in the same frozen carrier, "
            "but positive carrier metrics and a common stabilized context do not.",
            ("src/onetheory/physics/observables.py", "src/onetheory/physics/matter.py"),
            missing=(
                "positive matter and Higgs metrics",
                "stabilized common vacuum",
            ),
        ),
        _node(
            "alternate_neutrino_mixed_pairing",
            "constant Dirac-neutrino pairings on the frozen alternate carrier",
            "Flavor",
            "COMPUTED",
            "The source Wilson weights for L and nu^c require pre-twist "
            "characters (2,1) and (2,2). Their sum matches the up-sector "
            "matter-pair character, so the already certified up-Higgs covector "
            "can be reused without choosing a new Higgs or carrier. Six actual "
            "strict constituent cycles and four constant mixed scalars are "
            "archived. Independent Hom composition reproduces each literal "
            "scalar; direct and transferred traces agree in the fixed volume "
            "frame. This is not the missing F-F block or physical mass data.",
            ("research/experiments/scientific_genesis/alternate_neutrino_mixed_pairing.py",
             "research/experiments/scientific_genesis/ALTERNATE_NEUTRINO_MIXED_PAIRING_NOTE.md",
             "data/generated/scientific_genesis/alternate_neutrino_mixed_pairing.json",
             "data/generated/scientific_genesis/alternate_neutrino_mixed_pairing.cochains.json.gz",
             "tests/integration/test_scientific_genesis_alternate_neutrino_mixed_pairing.py"),
            ("source-pinned Wilson embedding", "frozen alternate determinant repair",
             "same actual canonical quotient pairing and trace"),
        ),
        _node(
            "alternate_neutrino_matter_lifts",
            "actual formal Dirac-neutrino matter corrections",
            "Flavor",
            "COMPUTED",
            "All eight actual parameter, side, and family corrections are "
            "archived with full constituent and quotient witnesses. Independent "
            "read-only replay verifies each original differential equation, "
            "strict full atlas character, literal quotient pushout, and "
            "coefficientwise matter identity. These are actual matter inputs, "
            "not the remaining complete scalar evaluations or a neutrino matrix.",
            ("research/experiments/scientific_genesis/alternate_neutrino_ff_entries.py",
             "research/experiments/scientific_genesis/alternate_neutrino_full_matrix.py",
             "tests/integration/test_scientific_genesis_alternate_neutrino_ff_entries.py"),
            ("fixed actual neutrino seeds and frame conventions",
             "same frozen universal two-parameter carrier", "no extension point selected"),
        ),
        _node(
            "alternate_neutrino_matrix",
            "complete alternate holomorphic Dirac-neutrino matrix",
            "Flavor",
            "COMPUTED",
            "All eight actual F-F coefficients pass full independent scalar "
            "replay with literal constant-product, linear-product, and scalar "
            "witness equality. The fixed quotient matrix has determinant "
            "(3/2+3*omega/4)*a0 and a nonzero constant rank-two minor. Its "
            "rank-three locus D(a0) meets the up locus D(a1) on the same P1. "
            "No family bases are identified; no point, metrics, Majorana "
            "mechanism, stabilized vacuum, or physical mass is inferred.",
            ("research/experiments/scientific_genesis/alternate_neutrino_mixed_pairing.py",
             "research/experiments/scientific_genesis/alternate_neutrino_ff_entries.py",
             "research/experiments/scientific_genesis/alternate_neutrino_full_matrix.py",
             "data/generated/scientific_genesis/alternate_neutrino_full_holomorphic_matrix.json",
             "research/experiments/scientific_genesis/ALTERNATE_NEUTRINO_FULL_MATRIX_NOTE.md",
             "tests/integration/test_scientific_genesis_alternate_neutrino_full_matrix.py"),
            ("conditional heterotic realization", "unchanged frozen carrier"),
        ),
        _node(
            "alternate_down_higgs_hom_representative",
            "source-routed down-Higgs Hom class on the frozen alternate carrier",
            "Flavor",
            "COMPUTED",
            "The fixed common twist routes native Hom character (2,2) to "
            "the published down-Higgs forward weight (0,1). Its actual "
            "351-term strict class is archived in the original reduced basis. "
            "Independent replay verifies full closure, both atlas characters, "
            "and exact nonboundary coordinates. This is not an exterior Higgs "
            "lift or a down-quark or charged-lepton Yukawa coefficient.",
            ("research/experiments/scientific_genesis/alternate_down_higgs_hom_representative.py",
             "research/experiments/scientific_genesis/ALTERNATE_DOWN_HIGGS_HOM_NOTE.md",
             "data/generated/scientific_genesis/alternate_down_higgs_hom_representative.json",
             "data/generated/scientific_genesis/"
             "alternate_down_higgs_hom_representative.cochains.json.gz",
             "tests/integration/test_scientific_genesis_"
             "alternate_down_higgs_hom_representative.py"),
            ("same frozen carrier and determinant repair", "source-pinned Wilson weights"),
        ),
        _node(
            "alternate_down_higgs_quotient_cone",
            "actual down-Higgs universal quotient cocycle",
            "Flavor",
            "COMPUTED",
            "The 351-term actual down-Higgs covector factors through the "
            "natural coherent ideal quotient. Both signed quotient actions "
            "equal independently formed reciprocal wedges. Independent full "
            "differential replay verifies both archived exterior primitives, "
            "and the coupled scalar-input checker confirms the constant and "
            "linear equations with zero quadratic action. No up value, complete "
            "full-exterior-square Higgs, or flavor matrix is inferred.",
            ("research/experiments/scientific_genesis/alternate_down_higgs_quotient_cone.py",
             "research/experiments/scientific_genesis/ALTERNATE_DOWN_HIGGS_QUOTIENT_CONE_NOTE.md",
             "data/generated/scientific_genesis/alternate_down_higgs_quotient_cone.json",
             "data/generated/scientific_genesis/alternate_down_higgs_quotient_cone.cochains.json.gz",
             "tests/integration/test_scientific_genesis_alternate_down_higgs_quotient_cone.py",
             "research/experiments/scientific_genesis/alternate_up_higgs_quotient_cone.py",
             "research/experiments/scientific_genesis/alternate_up_exterior_higgs_action.py"),
            ("fixed frozen carrier", "actual native down-Higgs Hom input"),
        ),
        _node(
            "alternate_down_lepton_matter",
            "actual remaining down and charged-lepton constituent classes",
            "Flavor",
            "COMPUTED",
            "The published d^c and e^c Wilson weights require native matter "
            "characters (1,1) and (2,0) after the fixed common twist. Existing "
            "Q and L classes remain distinct. The two E and four F classes "
            "are now archived in the original exact bases. Independent replay "
            "checks full closure, both atlas actions, nonboundary coordinates, "
            "character-subspace rank, and literal producer reproduction. These "
            "are constituent inputs, not corrected matter states or matrices.",
            ("research/experiments/scientific_genesis/"
             "alternate_remaining_flavor_matter.py",
             "research/experiments/scientific_genesis/ALTERNATE_REMAINING_FLAVOR_MATTER_NOTE.md",
             "data/generated/scientific_genesis/alternate_remaining_flavor_matter.json",
             "data/generated/scientific_genesis/alternate_remaining_flavor_matter.cochains.json.gz",
             "tests/integration/test_scientific_genesis_alternate_remaining_flavor_matter.py",
             "research/experiments/scientific_genesis/"
             "alternate_constituent_up_cone_matter_lifts.py"),
            ("same frozen carrier and source-pinned Wilson action",),
        ),
        _node(
            "alternate_remaining_flavor_matter_lifts",
            "actual formal down and charged-lepton matter corrections",
            "Flavor",
            "COMPUTED",
            "All eight actual d^c and e^c outer-parameter corrections are "
            "archived with literal quotient pushouts. Independent replay "
            "checks each full constituent equation, both original atlas "
            "actions, literal quotient maps, and the complete coupled matter "
            "identity. Original seeds and outer bases are unchanged; existing "
            "Q/L corrections are not recomputed. No scalar matrix is inferred.",
            ("research/experiments/scientific_genesis/alternate_remaining_flavor_matter.py",
             "research/experiments/scientific_genesis/alternate_remaining_flavor_matter_lifts.py",
             "research/experiments/scientific_genesis/ALTERNATE_REMAINING_FLAVOR_MATTER_LIFTS_NOTE.md",
             "tests/integration/test_scientific_genesis_alternate_remaining_flavor_matter_lifts.py",
             *(f"data/generated/scientific_genesis/"
               f"alternate_remaining_flavor_lift_a{parameter}_sector{sector}_family{family}.{suffix}"
               for parameter in (0, 1) for sector in (0, 1) for family in (1, 2)
               for suffix in ("json", "cochains.json.gz")),
             "research/experiments/scientific_genesis/"
             "alternate_constituent_up_cone_matter_lifts.py",
             "research/experiments/scientific_genesis/alternate_up_ff_entries.py"),
            ("same frozen two-parameter carrier", "original matter bases"),
        ),
        _node(
            "alternate_down_lepton_mixed_pairing",
            "actual down and charged-lepton constant mixed scalar blocks",
            "Flavor",
            "COMPUTED",
            "All eight actual Q/d and L/e constant mixed scalars are archived "
            "with literal matter, Hom, quotient, scalar, and exchange witnesses. "
            "Each entire scalar equals the separate full Hom-composition "
            "and E-contraction result; strict original atlas characters, "
            "direct/transferred traces, quotient normalization, and byte-for-byte "
            "reproduction pass nineteen regressions. No F-F block is inferred.",
            ("research/experiments/scientific_genesis/alternate_down_lepton_mixed_pairing.py",
             "research/experiments/scientific_genesis/ALTERNATE_DOWN_LEPTON_MIXED_PAIRING_NOTE.md",
             "data/generated/scientific_genesis/alternate_down_lepton_mixed_pairing.json",
             "data/generated/scientific_genesis/alternate_down_lepton_mixed_pairing.cochains.json.gz",
             "tests/integration/test_scientific_genesis_alternate_down_lepton_mixed_pairing.py",
             "research/experiments/scientific_genesis/alternate_up_mixed_quotient_pairing.py"),
            ("same frozen carrier", "unchanged original quotient volume frame"),
        ),
        _node(
            "alternate_down_lepton_matrices",
            "complete actual down and charged-lepton holomorphic matrices",
            "Flavor",
            "COMPUTED",
            "The corrected complete invocation terminated successfully after "
            "replaying all sixteen actual matter lifts and all sixteen F-F "
            "scalar products, with literal constant/linear/scalar witnesses, "
            "original atlas and coupled equations, direct/transferred/inverse "
            "traces, and unchanged thirty-four-source archive snapshots. Both "
            "complete 3x3 matrices retain distinct original family bases and "
            "the quotient volume factor 1/9. Independent Fraction-pair arithmetic "
            "checks all eighteen entries, both linear determinants, the nonzero "
            "rank-two minors and the common four-sector quartic. Its nonempty "
            "open complement requires no extension-point selection. Read-only "
            "consumption rechecks actual source positions and matrix arithmetic. "
            "These are holomorphic matrices only; canonical metrics and a common "
            "stabilized vacuum remain missing.",
            ("research/experiments/scientific_genesis/alternate_up_ff_entries.py",
             "research/experiments/scientific_genesis/alternate_down_lepton_ff_entries.py",
             "research/experiments/scientific_genesis/ALTERNATE_DOWN_LEPTON_FF_NOTE.md",
             "tests/integration/test_scientific_genesis_alternate_down_lepton_ff_entries.py",
             "research/experiments/scientific_genesis/alternate_down_lepton_full_matrices.py",
             "research/experiments/scientific_genesis/ALTERNATE_DOWN_LEPTON_FULL_MATRICES_NOTE.md",
             "tests/integration/test_scientific_genesis_alternate_down_lepton_full_matrices.py",
             "data/generated/scientific_genesis/alternate_down_lepton_full_holomorphic_matrices.json",
             "research/experiments/scientific_genesis/alternate_neutrino_full_matrix.py",
             *(f"data/generated/scientific_genesis/"
               f"alternate_down_lepton_ff_a{p}_s{s}_r{r}_c{c}{suffix}"
               for p in (0, 1) for s in (0, 1) for r in (1, 2) for c in (1, 2)
               for suffix in (".json", ".cochains.json.gz")),
             "research/experiments/scientific_genesis/alternate_remaining_flavor_matter_lifts.py",
             "research/experiments/scientific_genesis/alternate_down_lepton_mixed_pairing.py"),
            ("conditional heterotic realization", "original formal outer basis"),
        ),
        _node(
            "physical_pfaffians",
            "physical worldsheet Pfaffians",
            "Vacuum",
            "BLOCKED",
            "Seed conic embeddings, restrictions, determinant-line maps, and "
            "normalization are absent.",
            ("research/experiments/conic_pfaffians/audit.py",),
            missing=(
                "seed embeddings",
                "restricted resolutions",
                "relative-duality maps",
                "Quillen normalization",
            ),
        ),
        _node(
            "alternate_necessary_hidden_chamber",
            "necessary hidden HYM wall for the frozen alternate carrier",
            "Vacuum",
            "DERIVED",
            "The published Bogomolov wall applies to the alternate carrier's "
            "identical rational Chern target in the no-five-brane, c1=0 "
            "Kahler HYM branch. An exact open box survives; a whole symbolic "
            "visible-stable subfamily is excluded. This is necessary only, "
            "not a hidden bundle, integral anomaly certificate, or vacuum.",
            ("research/experiments/scientific_genesis/alternate_necessary_hidden_chamber.py",
             "research/experiments/scientific_genesis/ALTERNATE_NECESSARY_HIDDEN_CHAMBER_NOTE.md",
             "data/generated/scientific_genesis/alternate_necessary_hidden_chamber.json",
             "tests/integration/test_scientific_genesis_alternate_necessary_hidden_chamber.py"),
            ("conditional heterotic realization", "no additional Bianchi sources",
             "trace-free unitary hidden HYM connection on a compact Kahler threefold"),
        ),
        _node(
            "hidden_bundle",
            "descended stable hidden bundle",
            "Vacuum",
            "BLOCKED",
            "The exact hidden target is known, but polynomial maps, descent, "
            "local freeness, stability, restrictions, and spectrum are absent.",
            (
                "research/experiments/hidden_bundle/audit.py",
                "src/onetheory/models/heterotic_schoen/consistency.py",
            ),
            missing=(
                "exact hidden maps",
                "equivariant descent",
                "global local freeness",
                "common stability chamber",
                "hidden spectrum",
            ),
        ),
        _node(
            "controlled_vacuum",
            "controlled stabilized common vacuum",
            "Vacuum",
            "BLOCKED",
            "The symbolic vacuum engine exists, but the complete physical K, W, "
            "f, D package and compatible hidden sector do not.",
            ("src/onetheory/physics/vacuum.py", "src/onetheory/models/heterotic_schoen/vacuum.py"),
            missing=(
                "visible carrier",
                "physical Pfaffians",
                "hidden bundle",
                "threshold functions",
                "complete effective action",
            ),
        ),
        _node(
            "measured_observables",
            "measured low-energy observables",
            "Comparison",
            "MEASURED",
            "Measurements are terminal comparison data and are not admitted as "
            "geometry, carrier, rank-lifting, or vacuum selectors.",
            ("data/observations/README.md", "src/onetheory/physics/observables.py"),
        ),
        _node(
            "low_energy_predictions",
            "held-out low-energy predictions",
            "Comparison",
            "BLOCKED",
            "No parameter-free low-energy masses, mixings, or CP invariants have "
            "been derived from a common stabilized carrier state.",
            ("src/onetheory/reality.py", "research/experiments/low_energy_closure/README.md"),
            missing=(
                "physical Yukawas",
                "controlled vacuum",
                "threshold matching",
                "RGE evolution",
                "frozen prediction protocol",
            ),
        ),
    ]


def _edges() -> list[dict[str, object]]:
    """Return the governing scientific dependency DAG edges."""

    exact_law = ("established law used conditionally",)
    return [
        _edge(
            "quantum_phase_structure",
            "genesis_to_uv_bridge",
            "A Genesis theory must recover quantum phase.",
            ("src/onetheory/physics/quantum.py",),
            (),
            False,
            ("no derivation from a primitive structure",),
        ),
        _edge(
            "lorentzian_causal_structure",
            "genesis_to_uv_bridge",
            "A Genesis theory must recover causal spacetime.",
            ("src/onetheory/physics/spacetime.py",),
            (),
            False,
            ("signature remains assumed",),
        ),
        _edge(
            "einstein_gravity",
            "genesis_to_uv_bridge",
            "A Genesis theory must recover universal geometric coupling.",
            ("src/onetheory/physics/gravity.py",),
            (),
            False,
            ("gravity remains an input law",),
        ),
        _edge(
            "dimensional_constant_contract",
            "genesis_to_uv_bridge",
            "The bridge must explain invariant dimensionless content rather than SI decimals.",
            ("src/onetheory/core/units.py",),
            (),
            False,
            ("dimensional constants remain primitive",),
        ),
        _edge(
            "genesis_to_uv_bridge",
            "heterotic_uv",
            "A complete Genesis theory would have to derive or uniquely select the UV realization.",
            (),
            (),
            False,
            ("no bridge exists", "other UV realizations may be possible"),
        ),
        _edge(
            "heterotic_uv",
            "schoen_geometry",
            "Compactification selects an internal Calabi-Yau realization.",
            ("src/onetheory/physics/compactification.py",),
            ("heterotic UV realization",),
            True,
            ("selected compactification may not be unique",),
        ),
        _edge(
            "schoen_geometry",
            "published_visible_carrier",
            "The published sheaf extension is defined on the Schoen quotient.",
            ("src/onetheory/models/heterotic_schoen/visible.py",),
            ("published source transcription",),
            True,
            ("chain representatives are not published",),
        ),
        _edge(
            "published_visible_carrier",
            "published_projective_pushout_adapter",
            "Any claimed chain reconstruction must reproduce the published "
            "cover Ext dimensions before quotient invariants are meaningful.",
            (
                "research/experiments/scientific_genesis/"
                "published_pushout_mismatch.py",
            ),
            (),
            True,
            ("the tested adapter omits fiber-sensitive constituent maps",),
        ),
        _edge(
            "published_projective_pushout_adapter",
            "published_constituent_ext_spaces",
            "Replacing the invalid projective pushouts with fiber-sensitive "
            "dP9 Serre complexes recovers both constituent Ext dimensions.",
            (
                "research/experiments/computable_carrier/dp9_serre_ext.py",
            ),
            (),
            True,
            ("deck-linearized representatives are not yet derived",),
        ),
        _edge(
            "published_constituent_ext_spaces",
            "published_constituent_deck_actions",
            "The explicit total complexes support geometric deck pullbacks; "
            "published equivariant data fixes their remaining character choice.",
            (
                "research/experiments/computable_carrier/"
                "dp9_serre_actions.py",
            ),
            ("published constituent equivariant representations",),
            True,
            ("the common character is source-selected, not fundamentally derived",),
        ),
        _edge(
            "published_constituent_deck_actions",
            "distinct_constituent_ray_screen",
            "The complete joint Ext decomposition permits a finite ray screen; "
            "full Cech lifts and local residue evaluations test each sector.",
            (
                "data/generated/scientific_genesis/"
                "distinct_constituent_ray_screen.json",
            ),
            ("fixed I3/I6 presentations", "exact local lci frames"),
            True,
            ("local units alone do not certify quotient descent or Higgs data",),
        ),
        _edge(
            "distinct_constituent_ray_screen",
            "alternate_constituent_cover_h1",
            "The two local-unit rays admit full mixed-complex lifts; the "
            "rank-two identity converts the twisted Hom into their tensor.",
            (
                "data/generated/scientific_genesis/"
                "alternate_constituent_higgs_dimensions.json",
            ),
            ("fixed constituent line degrees", "exact mixed transfer"),
            True,
            ("cover dimension alone does not determine invariant characters",),
        ),
        _edge(
            "distinct_constituent_ray_screen",
            "alternate_constituent_deck_atlases",
            "The unused local-unit rays have exact full Cech lifts, allowing "
            "their overlap and deck comparisons to be tested chartwise.",
            (
                "data/generated/scientific_genesis/"
                "alternate_constituent_deck_atlases.json",
            ),
            ("fixed I3/I6 presentations", "published chart deck lifts"),
            True,
            ("constituent equivariance does not construct an outer extension",),
        ),
        _edge(
            "alternate_constituent_deck_atlases",
            "alternate_constituent_determinant_obstruction",
            "The graded determinant of each exact common-coordinate deck frame "
            "acts on the cover-trivial product determinant line; scalar H3 "
            "reads the same nontrivial character. Determinants multiply in "
            "every equivariant short exact sequence.",
            (
                "data/generated/scientific_genesis/"
                "alternate_constituent_determinant_descent.json",
            ),
            ("fixed atlas linearisations", "equivariant outer extension if any"),
            True,
            ("another linearisation or underlying bundle is not excluded",),
        ),
        _edge(
            "alternate_constituent_deck_atlases",
            "alternate_constituent_hom_cycle_actions",
            "Exact native atlas frames transport to the common Schoen coordinates "
            "and preserve the full boundary basis of the determinant-twisted "
            "outer Hom complex.",
            (
                "data/generated/scientific_genesis/"
                "alternate_constituent_hom_actions.json",
            ),
            ("declared common-coordinate lifts", "rank-two determinant degree"),
            True,
            ("an explicit tensor cocycle map remains open",),
        ),
        _edge(
            "alternate_constituent_cover_h1",
            "alternate_constituent_hom_cycle_actions",
            "The exact rank-four cover Hom H1 selects four independent classes "
            "for the atlas-derived cohomology action.",
            (
                "data/generated/scientific_genesis/"
                "alternate_constituent_hom_actions.json",
            ),
            ("exact transferred degree-zero and degree-one maps",),
            True,
            ("the cover Hom representation is not the physical Higgs sector",),
        ),
        _edge(
            "alternate_constituent_hom_cycle_actions",
            "alternate_constituent_character_screen",
            "For rank-two F, exterior contraction identifies F* tensor det(F) "
            "with F equivariantly. Hence the certified determinant-twisted "
            "Hom characters differ from constituent-tensor characters by "
            "the total determinant character.",
            (
                "data/generated/scientific_genesis/"
                "alternate_constituent_character_screen.json",
            ),
            ("first determinant has trivial atlas character", "canonical homogeneous line action"),
            True,
            ("an explicit tensor chain map is still needed for Higgs cocycles",),
        ),
        _edge(
            "alternate_constituent_determinant_obstruction",
            "alternate_constituent_character_screen",
            "The unique common rank-four character twist cancels each exact "
            "total determinant. Acyclic determinant endpoints then identify "
            "H1 of a hypothetical exterior-square extension with tensor H1; "
            "the fixed Wilson weights distinguish the two rays.",
            (
                "data/generated/scientific_genesis/"
                "alternate_constituent_character_screen.json",
            ),
            ("an equivariant outer extension must exist", "published Wilson embedding"),
            True,
            ("conditional character selection does not construct a carrier",),
        ),
        _edge(
            "alternate_constituent_character_screen",
            "alternate_constituent_outer_cover_ext",
            "The only ray surviving the determinant-repaired conditional Higgs "
            "screen selects a concrete pair of exact mixed constituents. "
            "The existing outer-Hom transfer then computes cover Ext1(V2,V1).",
            (
                "data/generated/scientific_genesis/"
                "alternate_constituent_outer_ext.json",
            ),
            ("fixed ray (0,1) atlas", "exact reduced Schoen transfer"),
            True,
            ("positive cover Ext does not imply invariant Ext",),
        ),
        _edge(
            "alternate_constituent_outer_cover_ext",
            "alternate_constituent_outer_invariants",
            "The exact ray (0,1) deck atlas acts on full outer-Hom Cech "
            "cochains. Reynolds averaging all cover Ext1 classes yields two "
            "independent strictly fixed full cocycles.",
            (
                "data/generated/scientific_genesis/"
                "alternate_constituent_outer_invariants.json",
            ),
            ("exact cover Ext representatives", "certified P/T constituent frames"),
            True,
            ("invariant Ext alone does not construct the outer cone",),
        ),
        _edge(
            "alternate_constituent_outer_invariants",
            "alternate_constituent_outer_universal_cone",
            "The two independent strict cocycles define one universal linear "
            "outer arrow. The alternate local-unit and atlas certificates "
            "give a descended locally free extension; a common character "
            "twist repairs its determinant without changing outer Hom.",
            (
                "data/generated/scientific_genesis/"
                "alternate_constituent_outer_universal_cone.json",
            ),
            ("exact invariant basis", "fixed ray (0,1) atlas", "flat character twist"),
            True,
            ("local freeness and determinant repair do not imply stability",),
        ),
        _edge(
            "alternate_constituent_outer_universal_cone",
            "alternate_constituent_outer_stability_locus",
            "The source's destabilizing-line bound depends on Serre sublines, "
            "fixed I3/I6 ideals, and outer nonsplitting; these premises "
            "survive the alternate ray and common flat twist. Exact slope "
            "arithmetic gives a nonempty sufficient chamber.",
            (
                "data/generated/scientific_genesis/"
                "alternate_constituent_outer_stability_locus.json",
                "research/experiments/scientific_genesis/"
                "ALTERNATE_STABILITY_NOTE.md",
            ),
            ("published stability theorem", "same Serre sequence type", "non-split P1"),
            True,
            ("different ideal supports or a split ray would defeat the transfer",),
        ),
        _edge(
            "alternate_constituent_outer_stability_locus",
            "alternate_constituent_matter_profile",
            "Exact mixed transfer gives pure H1 for both constituents. The "
            "outer long exact sequence therefore collapses for every "
            "extension parameter; free-action Lefschetz fixes its deck "
            "character multiplicities without enumerating actions.",
            (
                "data/generated/scientific_genesis/"
                "alternate_constituent_matter_profile.json",
            ),
            ("unchanged first constituent", "free quotient action"),
            True,
            ("non-pure constituent cohomology would permit jumping",),
        ),
        _edge(
            "alternate_constituent_matter_profile",
            "alternate_constituent_structural_spectrum",
            "Pure H1 gives three regular matter modules. Equivariant "
            "exterior contraction and acyclic determinant endpoints "
            "identify Higgs H1 with the certified alternate Hom H1; "
            "the fixed Wilson weights then count surviving charged states.",
            (
                "data/generated/scientific_genesis/"
                "alternate_constituent_structural_spectrum.json",
                "research/experiments/scientific_genesis/"
                "ALTERNATE_SPECTRUM_NOTE.md",
            ),
            ("published Wilson weights", "exact Hom deck action", "acyclic endpoints"),
            True,
            ("a noncanonical determinant frame would change the characters",),
        ),
        _edge(
            "alternate_constituent_structural_spectrum",
            "alternate_constituent_carrier_state",
            "The only currently certified stable determinant-trivial component "
            "passing the charged structural selection constraints is frozen "
            "as a whole rather than by a fitted extension coordinate.",
            (
                "data/generated/scientific_genesis/"
                "alternate_constituent_carrier_state.json",
            ),
            ("certified alternate cone", "sufficient stable chamber"),
            True,
            ("chain cocycles and Yukawas remain unavailable after the freeze",),
        ),
        _edge(
            "alternate_constituent_carrier_state",
            "alternate_constituent_up_matter_representatives",
            "The frozen carrier fixes the alternate I6 atlas and its unique "
            "determinant-repair twist. Exact mixed transfer, full-cycle "
            "Reynolds projection, and independent reduced H1 rank recover "
            "the two required up-type constituent sectors.",
            (
                "data/generated/scientific_genesis/"
                "alternate_constituent_up_matter_representatives.json",
            ),
            ("exact atlas deck actions", "published Wilson weights"),
            True,
            ("cone lifting and Higgs cocycles are separate prerequisites",),
        ),
        _edge(
            "alternate_constituent_up_matter_representatives",
            "alternate_constituent_up_cone_matter_lifts",
            "The fixed I3 constituent has no H2 matter obstruction. Each "
            "outer-matter cup therefore admits an exact I3 primitive; "
            "eight explicit Reynolds-projected corrections satisfy the "
            "full block-cone differential identity coefficientwise.",
            (
                "data/generated/scientific_genesis/"
                "alternate_constituent_up_cone_matter_lifts.json",
            ),
            ("strict invariant outer basis", "certified atlas deck actions"),
            True,
            ("a Higgs lift is still needed for any physical Yukawa entry",),
        ),
        _edge(
            "alternate_constituent_carrier_state",
            "alternate_up_higgs_hom_representative",
            "The alternate atlas Hom transfer has a one-dimensional "
            "character-(2,0) H1 summand. Exact full-Cech projection gives "
            "a strict nonboundary representative; determinant-frame "
            "arithmetic identifies its required Higgs sector without "
            "constructing a tensor chain map.",
            (
                "data/generated/scientific_genesis/"
                "alternate_up_higgs_hom_representative.json",
            ),
            ("certified alternate Hom action", "fixed Wilson assignment"),
            True,
            ("character matching alone is not a Higgs chain cocycle",),
        ),
        _edge(
            "alternate_up_higgs_hom_representative",
            "alternate_up_yoneda_evaluation",
            "Acyclic determinant endpoints identify Higgs cohomology with "
            "H1(Hom(F tensor det E,E)). The exact signed Yoneda product "
            "with each strict F class survives in H2(Hom(det E,E)); the "
            "two same-character images have checked exact ratios.",
            (
                "data/generated/scientific_genesis/"
                "alternate_up_yoneda_evaluation.json",
                "research/experiments/scientific_genesis/"
                "ALTERNATE_UP_YONEDA_ROUTE_NOTE.md",
            ),
            ("frozen alternate carrier", "strict matter cocycles"),
            True,
            ("the final determinant trace is not yet an exact scalar entry",),
        ),
        _edge(
            "alternate_constituent_up_matter_representatives",
            "alternate_up_yoneda_evaluation",
            "The four exact I6 classes are the right factors in the "
            "common-cover Hom composition; each evaluated degree-two "
            "class lies outside the transferred boundary span.",
            (
                "data/generated/scientific_genesis/"
                "alternate_up_yoneda_evaluation.json",
            ),
            ("certified determinant twist", "exact transferred differential"),
            True,
            ("cohomological nonvanishing does not fix scalar normalization",),
        ),
        _edge(
            "alternate_up_yoneda_evaluation",
            "alternate_up_mixed_scalar_trace",
            "The evaluated Hom classes occupy only the A-line object. "
            "Their alternating product with strict first-constituent "
            "matter therefore uses exactly the F0-A Pluecker entries; "
            "full scalar closure and the ordered residue are checked.",
            (
                "data/generated/scientific_genesis/"
                "alternate_up_mixed_scalar_trace.json",
                "research/experiments/scientific_genesis/"
                "ALTERNATE_UP_MIXED_TRACE_NOTE.md",
            ),
            ("certified first-constituent determinant form",),
            True,
            ("the cover trace is not yet a quotient-normalized full matrix",),
        ),
        _edge(
            "alternate_constituent_up_cone_matter_lifts",
            "alternate_up_mixed_scalar_trace",
            "The two strict I3 classes are the first factors in the "
            "mixed scalar cups. Their unchanged cone lifts make the "
            "constant slots independent of the outer parameters.",
            (
                "data/generated/scientific_genesis/"
                "alternate_up_mixed_scalar_trace.json",
            ),
            ("acyclic determinant filtration", "strict first-constituent classes"),
            True,
            ("the parameter-linear second/second block remains unknown",),
        ),
        _edge(
            "alternate_up_mixed_scalar_trace",
            "alternate_up_rank_floor",
            "Nonzero mixed rows and columns give nonzero E/F two-by-two "
            "minors because the E-E entry vanishes. No F-F entry can "
            "alter these minors.",
            (
                "data/generated/scientific_genesis/alternate_up_rank_floor.json",
                "research/experiments/scientific_genesis/ALTERNATE_UP_RANK_FLOOR_NOTE.md",
            ),
            ("same ordered cover trace", "nonsplit frozen carrier"),
            True,
            ("this lower bound alone cannot establish rank three",),
        ),
        _edge(
            "alternate_up_yukawa_support",
            "alternate_up_rank_floor",
            "The exterior filtration fixes the E-E zero and the "
            "parameter independence of both mixed blocks, so their "
            "nonzero minors hold over the entire nonsplit P1 family.",
            ("data/generated/scientific_genesis/alternate_up_rank_floor.json",),
            ("acyclic determinant endpoints",),
            True,
            ("the full same-cone Higgs representative is still open",),
        ),
        _edge(
            "alternate_up_rank_floor",
            "alternate_up_null_channel",
            "Nonzero mixed reference pivots define exact left and right "
            "kernel vectors. Expanding the three-by-three determinant "
            "over four formal F-F entries leaves only their null pairing.",
            (
                "data/generated/scientific_genesis/alternate_up_null_channel.json",
                "research/experiments/scientific_genesis/ALTERNATE_UP_NULL_CHANNEL_NOTE.md",
            ),
            ("ordered mixed cover residues",),
            True,
            ("the projected F-F coefficient is not yet evaluated",),
        ),
        _edge(
            "alternate_up_yoneda_evaluation",
            "alternate_up_null_channel",
            "The two exact within-character Yoneda ratios cancel the "
            "reduced classes. The full 144-term combinations admit exact "
            "90-term primitives under the synchronized differential.",
            ("data/generated/scientific_genesis/alternate_up_null_channel.json",),
            ("certified full Hom cochains",),
            True,
            ("a null Yoneda homotopy is not an F-F Yukawa value",),
        ),
        _edge(
            "alternate_constituent_outer_invariants",
            "alternate_up_dual_higgs_inputs",
            "The global quotient row annihilates the Hilbert-Burch columns "
            "and all A-targeted extension arrows. It therefore maps both "
            "actual outer cochains to closed reciprocal-Hom inputs without "
            "inverting a local minor.",
            ("data/generated/scientific_genesis/alternate_up_dual_higgs_inputs.json",),
            ("fixed first-constituent quotient orientation",),
            True,
            ("the images are not themselves Higgs corrections",),
        ),
        _edge(
            "alternate_up_higgs_hom_representative",
            "alternate_up_dual_higgs_inputs",
            "Pure A output retargets Hom(F tensor det E,E) to "
            "Hom(F,A tensor det E inverse)=Hom(F,B1 inverse) with "
            "identical object, ambient, and full differential data.",
            ("data/generated/scientific_genesis/alternate_up_dual_higgs_inputs.json",),
            ("saved strict A-supported Hom class",),
            True,
            ("retargeting alone does not supply the complete first-order scalar",),
        ),
        _edge(
            "alternate_up_dual_higgs_inputs",
            "alternate_up_exterior_higgs_action",
            "The actual reciprocal covectors evaluate on every graded "
            "exterior monomial with declared totalization signs. The saved "
            "Higgs kills A, allowing the ordered full products to close. "
            "Each proposed primitive is checked by its full differential.",
            ("data/generated/scientific_genesis/alternate_up_exterior_higgs_action.json",),
            ("single even A target for constituent extension arrows",),
            True,
            ("no complete Higgs-cone representative is assigned",),
        ),
        _edge(
            "alternate_up_exterior_higgs_action",
            "alternate_up_higgs_quotient_cone",
            "Compose both signed slots and project the actual A target. "
            "The full connecting maps close, and their Higgs actions are "
            "exactly minus the pinned exterior products; D k plus action "
            "vanishes coefficientwise in the triangular quotient cone.",
            (
                "data/generated/scientific_genesis/alternate_up_higgs_quotient_cone.json",
            ),
            ("ordinary odd monomials", "global first quotient", "pinned full D k identities"),
            True,
            ("a closed quotient cone does not certify every exterior-V comparison",),
        ),
        _edge(
            "alternate_up_null_channel",
            "alternate_up_higgs_quotient_cone",
            "The actual null matter wedges are full cycles. Before the "
            "Higgs annihilator, both ordered tensor differences have only "
            "A-section support and vanish on the legitimate ideal quotient.",
            ("data/generated/scientific_genesis/alternate_up_higgs_quotient_cone.json",),
            ("actual even null-matter support", "F/A is a coherent ideal quotient"),
            True,
            ("the all-input tensor comparison is not certified",),
        ),
        _edge(
            "alternate_up_exterior_higgs_action",
            "alternate_up_first_order_scalar",
            "The exact signed slot identity fixes the positive k term; "
            "both exact matter corrections must be included before tracing.",
            ("data/generated/scientific_genesis/alternate_up_first_order_scalar.json",),
            ("D x equals minus e b", "literal three-term order"),
            True,
            ("a single primitive term is not a closed Yukawa scalar",),
        ),
        _edge(
            "alternate_up_null_channel",
            "alternate_up_first_order_scalar",
            "The determinant null combinations specify the actual matter "
            "inputs without fitting coefficients or choosing an extension point.",
            ("data/generated/scientific_genesis/alternate_up_first_order_scalar.json",),
            ("declared seed0/seed5 basis and exact within-sector ratios",),
            True,
            ("full F-F matrix entries are not reconstructed from null scalars",),
        ),
        _edge(
            "alternate_up_higgs_quotient_cone",
            "alternate_up_first_order_scalar",
            "The projected ordered tensor comparison vanishes before h. "
            "Its primitive-free scalar defect agrees with the independently "
            "evaluated full scalar differential.",
            (
                "data/generated/scientific_genesis/alternate_up_higgs_quotient_cone.json",
                "data/generated/scientific_genesis/alternate_up_first_order_scalar.json",
            ),
            ("actual null channel only",),
            True,
            ("this does not identify the complete physical exterior pairing",),
        ),
        _edge(
            "alternate_up_higgs_quotient_cone",
            "alternate_up_quotient_equivariance",
            "The actual global minor row induces the unique quotient line "
            "frame. Tensoring it with the F/A frame and expanding the "
            "ordinary graded exterior frame checks h and both delta arrows.",
            ("data/generated/scientific_genesis/alternate_up_quotient_equivariance.json",),
            ("declared common constituent frames", "determinant repair"),
            True,
            ("equivariance alone does not identify a matter-product map",),
        ),
        _edge(
            "mixed_even_rank_one_tensor_homotopy",
            "mixed_graded_rank_one_tensor_comparison",
            "Correct internal braiding and the complete mixed Hom row extend "
            "the coefficient homotopy to odd syzygies without fitting a scalar.",
            ("data/generated/scientific_genesis/alternate_up_syzygy_tensor_comparison.json",),
            ("isolated even image", "global polynomial arrows", "full row closure"),
            True,
            ("odd coefficients are not individually closed",),
        ),
        _edge(
            "mixed_graded_rank_one_tensor_comparison",
            "first_exact_yukawa",
            "The F tensor comparison must be extended through the coupled "
            "outer arrows and the legitimate B tensor A quotient before "
            "identifying the physical pairing and declaring its trace.",
            ("research/experiments/scientific_genesis/ALTERNATE_UP_QUOTIENT_PAIRING_NOTE.md",),
            ("natural outer-cone product", "determinant and quotient trace conventions"),
            False,
            ("the outer coefficient acts nontrivially on the inner target",),
        ),
        _edge(
            "mixed_graded_rank_one_tensor_comparison",
            "product_cover_homotopy_strict_hirsch",
            "A coupled outer-row extension would need a product compatibility "
            "not supplied by the rank-one homotopy identity; an exact edge-cell "
            "counterexample disproves the proposed strict Hirsch shortcut.",
            ("tests/integration/test_scientific_genesis_cup_homotopy.py",),
            ("full product-cover homotopy", "three degree-one scalar cochains"),
            True,
            ("a strict rule on one simplex does not imply it on a product cover",),
        ),
        _edge(
            "product_cover_homotopy_strict_hirsch",
            "first_exact_yukawa",
            "Use a derived higher coefficient compatibility or prove that "
            "the actual outer comparison defect vanishes in the legitimate "
            "quotient; the failed strict rule cannot identify the physical product.",
            ("research/experiments/scientific_genesis/ALTERNATE_UP_QUOTIENT_PAIRING_NOTE.md",),
            ("actual coupled cochain comparison", "unchanged carrier inputs"),
            False,
            ("the generic defect is not a computed physical coupling",),
        ),
        _edge(
            "product_cover_homotopy_strict_hirsch",
            "mixed_schoen_hirsch_coherence",
            "Fill the actual nonzero chain defect recursively in its "
            "contractible carrier rather than asserting a strict derivation rule.",
            ("research/experiments/scientific_genesis/mixed_schoen_cup_coherence.py",),
            ("positive-degree carrier cycles", "explicit first-vertex contraction"),
            True,
            ("a higher homotopy does not make the strict rule true",),
        ),
        _edge(
            "mixed_schoen_hirsch_coherence",
            "mixed_coupled_quotient_tensor_identity",
            "The T correction cancels the first-slot Hirsch defect left "
            "by the two additive row corrections in the declared quotient.",
            ("research/experiments/scientific_genesis/ALTERNATE_UP_COUPLED_TENSOR_NOTE.md",),
            ("closed coupled rows", "A wedge B killed by the legitimate quotient"),
            True,
            ("the theorem is not asserted for arbitrary twisting graphs",),
        ),
        _edge(
            "mixed_graded_rank_one_tensor_comparison",
            "mixed_coupled_quotient_tensor_identity",
            "Retain structural-first braiding and full Hom-row closure while "
            "adding the higher compatibility required when beta acts on A.",
            ("research/experiments/scientific_genesis/mixed_schoen_coupled_tensor.py",),
            ("explicit even A and B", "two-term polynomial skeleton"),
            True,
            ("applying the isolated-target theorem twice is insufficient",),
        ),
        _edge(
            "mixed_coupled_quotient_tensor_identity",
            "mixed_coupled_vertex_comparison",
            "The union-supported homotopies vanish on vertex outputs, leaving "
            "the ordinary graded local wedge with the complete vertex differential.",
            ("research/experiments/scientific_genesis/ALTERNATE_UP_VERTEX_COMPARISON_NOTE.md",),
            ("no differential lowers cover degree", "graded Koszul signs retained"),
            True,
            ("this is not a global augmentation or a physical scalar",),
        ),
        _edge(
            "mixed_coupled_vertex_comparison",
            "alternate_up_canonical_quotient_product",
            "For faithful flat ambient resolutions the degree-zero rigidity "
            "lemma identifies a sheaf-natural product with its H0 local wedge. "
            "Negative ambient Tor cannot supply an additional degree-zero map.",
            ("research/experiments/scientific_genesis/ALTERNATE_UP_VERTEX_COMPARISON_NOTE.md",),
            ("faithful ambient resolutions", "coherent Q", "sheaf-natural chain map"),
            True,
            ("positive source cohomology would invalidate the rigidity lemma",),
        ),
        _edge(
            "alternate_up_coupled_tensor_presentation",
            "alternate_up_canonical_quotient_product",
            "The actual q_E row and all quotient arrows match the declared "
            "pushout and coherent quotient. The frozen local-freeness and "
            "Serre section establish the faithful local presentations.",
            ("research/experiments/scientific_genesis/ALTERNATE_UP_VERTEX_COMPARISON_NOTE.md",),
            ("frozen lawful locus", "fixed signed-minor orientation"),
            True,
            ("a fibrewise subbundle at section zeros is not assumed",),
        ),
        _edge(
            "alternate_up_canonical_quotient_product",
            "first_exact_yukawa",
            "Evaluate the identified natural product with complete matter and "
            "Higgs lifts, then establish determinant orientation, equivariant "
            "descent and the explicitly normalized quotient trace for every entry.",
            ("research/experiments/scientific_genesis/ALTERNATE_UP_VERTEX_COMPARISON_NOTE.md",),
            ("complete actual lifts", "declared trace convention", "all matrix entries"),
            False,
            ("one null coefficient is not a complete or physical matrix",),
        ),
        _edge(
            "mixed_coupled_quotient_tensor_identity",
            "alternate_up_coupled_tensor_presentation",
            "The actual pushout row is q_E(e); complete arrow comparison "
            "identifies its quotient with the existing Higgs cone presentation.",
            ("data/generated/scientific_genesis/alternate_up_coupled_tensor_comparison.json",),
            ("fixed global minor quotient", "retained full Koszul subsets"),
            True,
            ("the coherent quotient is not a fibrewise vector bundle",),
        ),
        _edge(
            "alternate_up_higgs_quotient_cone",
            "alternate_up_coupled_tensor_presentation",
            "Both connecting arrows must agree as full cochains, not only "
            "as transferred classes or selected null-channel evaluations.",
            ("data/generated/scientific_genesis/alternate_up_coupled_tensor_comparison.json",),
            ("all polynomial and inner mixed blocks", "both universal coefficients"),
            True,
            ("dimensional agreement alone does not identify presentations",),
        ),
        _edge(
            "alternate_up_canonical_quotient_product",
            "alternate_up_same_higgs_class",
            "The natural sheaf quotient fixes the middle mixed functional; "
            "acyclic determinant endpoints identify its exterior Higgs class uniquely.",
            ("research/experiments/scientific_genesis/ALTERNATE_UP_MIXED_PAIRING_NOTE.md",),
            ("natural exterior-V-to-Q morphism", "fixed e wedge A_E orientation"),
            True,
            ("matching dimensions alone would not identify the selected class",),
        ),
        _edge(
            "alternate_up_higgs_quotient_cone",
            "alternate_up_same_higgs_class",
            "Both coefficientwise full Higgs primitive identities supply "
            "a closed quotient class, not just its leading character table.",
            ("research/experiments/scientific_genesis/alternate_up_higgs_quotient_cone.py",),
            ("unchanged full primitives", "acyclic dual determinant endpoint"),
            True,
            ("a changed primitive sign would fail full closure",),
        ),
        _edge(
            "alternate_up_same_higgs_class",
            "alternate_up_mixed_quotient_pairing",
            "The actual quotient functional represents the selected class; "
            "its evaluation uses fixed carrier matter bases rather than fitted coefficients.",
            ("research/experiments/scientific_genesis/alternate_up_mixed_quotient_pairing.py",),
            ("actual closed E and F inputs", "fixed Higgs-first scalar order"),
            True,
            ("ordered scalar signs cannot be hidden in a Higgs phase",),
        ),
        _edge(
            "alternate_up_quotient_trace",
            "alternate_up_mixed_quotient_pairing",
            "Trace complete closed scalar classes with the explicit finite-cover "
            "volume frame; do not infer canonical matter metrics from this normalization.",
            ("data/generated/scientific_genesis/alternate_up_mixed_quotient_pairing.json",),
            ("verified scalar closure", "unchanged descended volume frame"),
            True,
            ("a different volume scale rescales the holomorphic trace",),
        ),
        _edge(
            "alternate_up_coupled_tensor_presentation",
            "alternate_up_coupled_null_pairing",
            "Evaluate the actual corrected product with complete pushed matter "
            "and Higgs lifts, then verify all coefficientwise differential identities.",
            ("data/generated/scientific_genesis/alternate_up_coupled_null_scalar.json",),
            ("both formal coefficients", "full Koszul arrows", "explicit primitive archive"),
            True,
            ("constituent matter alone is not closed in the outer cone",),
        ),
        _edge(
            "alternate_up_same_higgs_class",
            "alternate_up_coupled_null_pairing",
            "The closed quotient Higgs evaluates the identified natural class, "
            "not an independently chosen functional with a matching character.",
            ("research/experiments/scientific_genesis/ALTERNATE_UP_MIXED_PAIRING_NOTE.md",),
            ("natural quotient product", "complete closed Higgs lift"),
            True,
            ("no complete matrix follows from one null contraction",),
        ),
        _edge(
            "alternate_up_mixed_quotient_pairing",
            "first_exact_yukawa",
            "Retain the verified constant mixed row and column in the same "
            "Higgs-first order while evaluating the missing F-F block.",
            ("data/generated/scientific_genesis/alternate_up_mixed_quotient_pairing.json",),
            ("all four a1 F-F entries", "freshly verified parameter blocks"),
            False,
            ("partial entries must not be returned as a complete matrix",),
        ),
        _edge(
            "alternate_up_coupled_null_pairing",
            "first_exact_yukawa",
            "The full F-F block must reproduce this null contraction in the "
            "fixed bases; one determinant-sensitive coefficient is not the whole matrix.",
            ("data/generated/scientific_genesis/alternate_up_coupled_null_scalar.json",),
            ("every F-F entry derived", "unchanged Higgs-first convention"),
            False,
            ("rank information alone does not supply complete flavor data",),
        ),
        _edge(
            "alternate_up_coupled_tensor_presentation",
            "alternate_up_ff_block",
            "Each actual F class needs its certified E correction before the "
            "fixed quotient product can evaluate an F-F entry.",
            ("research/experiments/scientific_genesis/alternate_up_ff_entries.py",),
            ("both formal coefficients", "four fixed F-family seed pairs"),
            False,
            ("a free quotient-line primitive is not an actual carrier matter lift",),
        ),
        _edge(
            "alternate_up_ff_block",
            "first_exact_yukawa",
            "All eight coefficientwise scalar witnesses must close, reproduce "
            "the natural null contraction, and enter the verified 3x3 matrix.",
            ("research/experiments/scientific_genesis/alternate_up_full_matrix.py",),
            ("fixed Higgs-first trace", "both complete F-F coefficient blocks"),
            True,
            ("source files or partial archives alone cannot supply matrix entries",),
        ),
        _edge(
            "schoen_geometry",
            "alternate_up_quotient_trace",
            "The stated free ninefold map supports finite-etale descent "
            "and Tr_pi(pi*alpha)=degree*alpha in the explicitly descended volume frame.",
            ("research/experiments/scientific_genesis/ALTERNATE_UP_QUOTIENT_TRACE_NOTE.md",),
            ("free quotient", "exact scalar deck-boundary witnesses", "stated volume scale"),
            True,
            ("a changed cover degree or a ramified map needs a different proof",),
        ),
        _edge(
            "alternate_up_quotient_trace",
            "first_exact_yukawa",
            "Use the fixed quotient trace only after the canonical product, "
            "complete closed inputs and Higgs identification have been checked "
            "for every required matrix entry.",
            ("data/generated/scientific_genesis/alternate_up_quotient_trace.json",),
            ("natural product", "complete matrix entries", "unchanged volume frame"),
            False,
            ("a holomorphic trace does not supply matter metrics or a vacuum",),
        ),
        _edge(
            "alternate_up_coupled_tensor_presentation",
            "first_exact_yukawa",
            "Evaluate the corrected product on complete cone matter lifts "
            "with the existing quotient Higgs cocycle, then check determinant "
            "orientation, equivariance and explicitly declared quotient trace.",
            ("research/experiments/scientific_genesis/ALTERNATE_UP_COUPLED_TENSOR_NOTE.md",),
            ("natural V-to-R pushout", "complete matter lifts", "fixed Higgs lift"),
            False,
            ("previous ordered scalar screens are not assigned to the new product",),
        ),
        _edge(
            "alternate_up_first_order_scalar",
            "alternate_up_pairing_exchange",
            "Exchange the full actual inputs without changing the primitive "
            "or averaging. Compare literal top-Laurent coefficients with "
            "transferred residues only after checking the full differential.",
            ("data/generated/scientific_genesis/alternate_up_pairing_exchange.json",),
            ("both actual matter legs", "unchanged ordered cup convention"),
            True,
            ("a failed exchange refutes this candidate, not the entire carrier",),
        ),
        _edge(
            "alternate_up_exterior_higgs_action",
            "alternate_up_pairing_exchange",
            "The same full primitive enters both orders. Its archived "
            "differential is checked against the pinned full exterior product.",
            ("data/generated/scientific_genesis/alternate_up_pairing_exchange.cochains.json.gz",),
            ("ordinary odd monomials", "checked positive correction sign"),
            True,
            ("a primitive sign cannot be changed to repair the exchanged residue",),
        ),
        _edge(
            "alternate_up_quotient_equivariance",
            "first_exact_yukawa",
            "The quotient class has the required repaired Higgs character. "
            "Its natural exterior-V matter product must still be realized "
            "on actual cochains before assigning any physical matrix entry.",
            ("research/experiments/scientific_genesis/ALTERNATE_UP_QUOTIENT_PAIRING_NOTE.md",),
            ("natural sheaf exterior map", "explicit trace normalization"),
            False,
            ("matching characters do not prove a tensor comparison",),
        ),
        _edge(
            "alternate_up_pairing_exchange",
            "first_exact_yukawa",
            "Exchange symmetry and an independent cover trace are necessary "
            "checks, not sufficient identification of the derived product.",
            ("research/experiments/scientific_genesis/ALTERNATE_UP_QUOTIENT_PAIRING_NOTE.md",),
            ("natural matter-product comparison", "representative independence"),
            False,
            ("even a passing closed exchange screen is not a complete Yukawa matrix",),
        ),
        _edge(
            "alternate_up_null_channel",
            "alternate_up_null_line_homotopies",
            "Inspect all actual primitive components, retarget the unchanged "
            "line grading, and check the complete line differential identity.",
            ("data/generated/scientific_genesis/alternate_up_null_line_homotopies.json",),
            ("the 90-term primitives have only actual line-subobject support",),
            True,
            ("an E-valued boundary need not be a line boundary in another case",),
        ),
        _edge(
            "alternate_up_higgs_quotient_cone",
            "alternate_up_null_line_homotopies",
            "The actual K resolution and determinant endpoint compute the "
            "degree-zero extension-map ambiguity without replacing K by a bundle.",
            ("data/generated/scientific_genesis/alternate_up_null_line_homotopies.json",),
            ("K is the concrete coherent Serre ideal quotient",),
            True,
            ("Hom(det F,K) is not the matter-product H2(K) ambiguity",),
        ),
        _edge(
            "alternate_up_null_line_homotopies",
            "first_exact_yukawa",
            "The actual short line homotopies and fixed-endpoint uniqueness "
            "may shorten the natural product comparison; agreement must "
            "still be proved or checked by reachable tensor homotopies.",
            ("research/experiments/scientific_genesis/ALTERNATE_UP_QUOTIENT_PAIRING_NOTE.md",),
            ("natural exterior product", "complete comparison-indeterminacy analysis"),
            False,
            ("a closed partial product can still differ by an H2(K) class",),
        ),
        _edge(
            "alternate_up_exterior_higgs_action",
            "alternate_up_exterior_boundary_attack",
            "The same actual exterior differential and raw vector cup test "
            "an exact boundary in a physical native character sector.",
            ("data/generated/scientific_genesis/alternate_up_exterior_boundary_attack.json",),
            ("unchanged actual null classes", "full strict-character boundary"),
            True,
            ("raw scalar-screen closure does not imply a cohomological product",),
        ),
        _edge(
            "alternate_up_exterior_boundary_attack",
            "mixed_even_rank_one_tensor_homotopy",
            "An explicit cover coefficient homotopy cancels the exhibited "
            "Leibniz defect, with its actual source differential sign.",
            ("data/generated/scientific_genesis/alternate_up_exterior_boundary_attack.json",),
            ("even-object sector", "rank-one nilpotent twisting target"),
            True,
            ("the correction rejects odd objects and is not an outer-cone comparison",),
        ),
        _edge(
            "mixed_even_rank_one_tensor_homotopy",
            "first_exact_yukawa",
            "The even-sector correction restores the actual boundary identity. "
            "Its graded extension is derived under rank-one hypotheses; "
            "the coupled outer quotient comparison is still required.",
            ("research/experiments/scientific_genesis/ALTERNATE_UP_QUOTIENT_PAIRING_NOTE.md",),
            ("complete natural tensor comparison", "declared trace normalization"),
            False,
            ("a scoped even-sector chain map is not the full physical product",),
        ),
        _edge(
            "alternate_up_first_order_scalar",
            "first_exact_yukawa",
            "A natural sheaf quotient and closed ordered scalars must be "
            "identified with the equivariant physical Higgs pairing, with "
            "explicit determinant and quotient trace conventions, before "
            "the nonzero a1 scalar certifies generic physical holomorphic rank.",
            ("research/experiments/scientific_genesis/ALTERNATE_UP_FIRST_ORDER_SCALAR_NOTE.md",),
            ("physical cochain comparison", "equivariant Higgs and trace normalization"),
            False,
            ("a closed ordered residue alone is not a physical rank theorem",),
        ),
        _edge(
            "alternate_constituent_carrier_state",
            "alternate_constituent_determinant_pairing",
            "The frozen ray fixes a distinct affine Serre presentation. "
            "Its complementary minors satisfy exact relation and "
            "hypersurface-corrected overlap identities on the certified atlas.",
            (
                "data/generated/scientific_genesis/"
                "alternate_constituent_determinant_pairing.json",
            ),
            ("certified alternate atlas",),
            True,
            ("local pairings are not yet a grouped Hom-to-tensor map",),
        ),
        _edge(
            "alternate_constituent_determinant_pairing",
            "alternate_constituent_duality_local_inverse",
            "The complementary-minor form J annihilates the relations. "
            "On each minor open, J S J = Delta J and the adjugate dual "
            "retract satisfies A^t T = D id and J S P = Delta P. Certified "
            "rank-three relations make this a local quotient inverse.",
            (
                "data/generated/scientific_genesis/"
                "alternate_constituent_duality_local_inverse.json",
                "research/experiments/scientific_genesis/"
                "ALTERNATE_DUALITY_LOCAL_INVERSE_NOTE.md",
            ),
            ("rank-two local freeness", "minor principal-open localization"),
            True,
            ("the 324-term Hom cocycle has not been transported globally",),
        ),
        _edge(
            "alternate_up_higgs_hom_representative",
            "alternate_up_higgs_local_syzygy_section",
            "The persisted strict Hom cochain supplies eighteen nonzero "
            "syzygy blocks on the six right chart vertices. The actual "
            "mixed-resolution arrows map the localized middle numerators "
            "back to those blocks after multiplication by the minor.",
            (
                "data/generated/scientific_genesis/"
                "alternate_up_higgs_local_syzygy_section.json",
            ),
            ("certified full Hom representative", "minor principal-open localization"),
            True,
            ("local sections alone do not compare fiber-overlap terms",),
        ),
        _edge(
            "alternate_constituent_duality_local_inverse",
            "alternate_up_higgs_local_syzygy_section",
            "The exact adjugate section of the alternate rank-three "
            "relation is applied to each actual syzygy vector; the "
            "right-arrow matrix independently fixes its object ordering "
            "and sign.",
            (
                "data/generated/scientific_genesis/"
                "alternate_up_higgs_local_syzygy_section.json",
            ),
            ("certified minor-open dual contraction",),
            True,
            ("a local section is not a global tensor chain map",),
        ),
        _edge(
            "alternate_up_higgs_local_syzygy_section",
            "alternate_up_higgs_fiber_overlap_transport",
            "The strict Hom fiber-edge terms obey s_mu-s_nu+B g-F h=0. "
            "Transporting each actual local primitive by the alternate "
            "unipotent gauge and clearing both minor denominators gives "
            "B N=F K with an explicit Koszul numerator on every block.",
            (
                "data/generated/scientific_genesis/"
                "alternate_up_higgs_fiber_overlap_transport.json",
                "research/experiments/scientific_genesis/"
                "ALTERNATE_UP_HIGGS_FIBER_OVERLAP_NOTE.md",
            ),
            ("certified alternate overlap gauge", "minor-open localization"),
            True,
            ("fiber transport alone does not compare minor-open images",),
        ),
        _edge(
            "alternate_up_higgs_fiber_overlap_transport",
            "alternate_up_higgs_quotient_overlap_image",
            "The actual corrected middle numerator has R^t v=F K. "
            "The sparse Pluecker inverse q=S v satisfies "
            "D(J q-Delta v)=F(J S T K-Delta T K) on the selected minor "
            "open, providing a local quotient image on the hypersurface.",
            (
                "data/generated/scientific_genesis/"
                "alternate_up_higgs_quotient_overlap_image.json",
                "research/experiments/scientific_genesis/"
                "ALTERNATE_UP_HIGGS_QUOTIENT_OVERLAP_NOTE.md",
            ),
            ("certified alternate local inverse", "nonzero minor localization"),
            True,
            ("local quotient images do not imply global tensor gluing",),
        ),
        _edge(
            "alternate_constituent_duality_local_inverse",
            "alternate_up_higgs_quotient_overlap_image",
            "The certified identities J S J=Delta J and J S P=Delta P "
            "supply the exact principal-open inverse used on the actual "
            "corrected Hom overlap, without assuming the ambient residual "
            "vanishes off the Schoen hypersurface.",
            (
                "data/generated/scientific_genesis/"
                "alternate_up_higgs_quotient_overlap_image.json",
            ),
            ("rank-two quotient local freeness", "selected nonzero minor"),
            True,
            ("one local inverse alone does not prove minor compatibility",),
        ),
        _edge(
            "alternate_up_higgs_quotient_overlap_image",
            "alternate_up_higgs_minor_overlap_gluing",
            "For every other Pluecker minor, the cross-denominator "
            "difference of its local quotient image and the reference "
            "image is a relation modulo the Schoen equation. The "
            "adjugate relation witness and hypersurface correction are "
            "exactly computed from the actual corrected Hom vector.",
            (
                "data/generated/scientific_genesis/"
                "alternate_up_higgs_minor_overlap_gluing.json",
                "research/experiments/scientific_genesis/"
                "ALTERNATE_UP_HIGGS_MINOR_OVERLAP_NOTE.md",
            ),
            ("selected nonzero minor opens", "rank-two local freeness"),
            True,
            ("minor and base compatibility do not close the full tensor differential",),
        ),
        _edge(
            "alternate_constituent_up_cone_matter_lifts",
            "alternate_up_yukawa_support",
            "Constant E classes, parameter-linear F corrections, and the "
            "acyclic determinant filtration leave only exterior degree "
            "E2 F2. All nonzero determinant permutations have outer "
            "parameter degree one.",
            (
                "data/generated/scientific_genesis/"
                "alternate_up_yukawa_support.json",
                "research/experiments/scientific_genesis/"
                "ALTERNATE_UP_YUKAWA_SUPPORT_NOTE.md",
            ),
            ("rank-two exterior algebra", "acyclic determinant endpoints"),
            True,
            ("support does not establish a nonzero Yukawa coefficient",),
        ),
        _edge(
            "published_constituent_deck_actions",
            "published_constituent_ray_alignment",
            "The simultaneous intertwiner pulls the source-selected rays back "
            "to exact derived coordinates without changing their characters.",
            (
                "data/generated/scientific_genesis/"
                "published_constituent_ray_alignment.json",
            ),
            ("source-selected Serre ray coordinates",),
            True,
            ("choosing the fixed line selects a different extension class",),
        ),
        _edge(
            "published_constituent_ray_alignment",
            "published_constituent_full_cech",
            "The corrected perturbation inclusion lifts each mixed cocycle to "
            "the complete standard-cover total complex.",
            (
                "data/generated/scientific_genesis/"
                "published_constituent_full_cech.json",
            ),
            (),
            True,
            ("dropping the Koszul edge component changes the class",),
        ),
        _edge(
            "published_constituent_full_cech",
            "published_constituent_local_units",
            "Localizing parent-one components in the lci residue algebras tests "
            "the Cayley--Bacharach unit condition directly.",
            (
                "data/generated/scientific_genesis/"
                "published_constituent_local_units.json",
            ),
            ("finite lci Gorenstein support algebra",),
            True,
            ("a zero residue would make the middle term nonfree at support",),
        ),
        _edge(
            "published_constituent_local_units",
            "published_constituent_overlap_atlases",
            "Local units make the affine pushouts free at support; parent-zero "
            "Cech terms supply their exact overlap gauges.",
            (
                "data/generated/scientific_genesis/"
                "published_constituent_overlap_transitions.json",
            ),
            (),
            True,
            ("omitting hypersurface homotopies breaks relation comparison",),
        ),
        _edge(
            "published_constituent_overlap_atlases",
            "published_constituent_deck_atlases",
            "Local line frames convert homogeneous semilinear maps into "
            "comparisons satisfying the quotient deck group laws.",
            (
                "data/generated/scientific_genesis/"
                "published_constituent_deck_atlases.json",
            ),
            ("source-bound constituent equivariant structures",),
            True,
            ("projective commutators omit local frame factors",),
        ),
        _edge(
            "published_constituent_deck_atlases",
            "mixed_constituent_schoen_arrows",
            "Embedding the selected full cocycles in the synchronized grading "
            "retains the local maps and hypersurface homotopies.",
            (
                "data/generated/scientific_genesis/"
                "mixed_constituent_schoen_arrows.json",
            ),
            (),
            True,
            ("flattening the mixed arrow recovers the retired wrong-ray type",),
        ),
        _edge(
            "mixed_constituent_schoen_arrows",
            "mixed_schoen_outer_transfer",
            "Alexander--Whitney Cech multiplication and Koszul exterior "
            "multiplication convolve the selected arrows with synchronized "
            "outer Hom cochains through the exact cover contraction.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_outer_transfer.json",
            ),
            (),
            True,
            ("dropping totalization signs destroys square-zero",),
        ),
        _edge(
            "mixed_schoen_outer_transfer",
            "mixed_schoen_outer_actions",
            "Perturbed inclusion and projection transfer the synchronized "
            "deck action to lawful cover cohomology; exact Reynolds averaging "
            "then selects strict fixed representatives.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_outer_actions.json",
            ),
            (),
            True,
            ("fixed representatives do not select an extension coordinate",),
        ),
        _edge(
            "mixed_schoen_outer_actions",
            "mixed_schoen_outer_universal_cone",
            "The strict forward fixed basis defines a parameter-linear outer "
            "arrow whose closed coefficients give an exact universal block "
            "mapping cone.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_outer_universal_cone.json",
            ),
            (),
            True,
            ("the affine origin is the split extension",),
        ),
        _edge(
            "mixed_schoen_outer_actions",
            "mixed_schoen_reverse_outer_universal_cone",
            "The six strict reverse fixed classes define a parameter-linear "
            "RHom(V1,V2) arrow whose closed coefficients give an exact "
            "universal block mapping cone.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_reverse_outer_universal_cone.json",
            ),
            (),
            True,
            ("the affine origin is the split reverse extension",),
        ),
        _edge(
            "mixed_schoen_reverse_outer_universal_cone",
            "mixed_schoen_reverse_outer_stability_locus",
            "The orientation-independent extension lower bound retains all "
            "proper-subsheaf pairs and changes only the injected full "
            "constituent; exact reverse slopes then certify an open chamber.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_reverse_outer_stability_locus.json",
            ),
            ("published extension lower-bound theorem",),
            True,
            ("the split affine origin is excluded before projectivization",),
        ),
        _edge(
            "published_constituent_deck_actions",
            "published_constituent_mapping_cones",
            "Comparing the fixed-line cone with the selected ray proves that "
            "the former chooses the wrong joint character.",
            (
                "data/generated/scientific_genesis/"
                "published_constituent_ray_alignment.json",
            ),
            (),
            True,
            ("the pure cone remains a diagnostic complex",),
        ),
        _edge(
            "published_constituent_mapping_cones",
            "published_outer_reduced_model",
            "Embedding both derived cones in the common Schoen grading gives "
            "an exact reduced twisted Hom model and exposes the missing transfer.",
            (
                "research/experiments/computable_carrier/"
                "schoen_serre_outer.py",
            ),
            (),
            True,
            ("ambient cohomology reduction is not full Cech hypercohomology",),
        ),
        _edge(
            "published_outer_reduced_model",
            "published_outer_cech_transfer",
            "The equal 90-dimensional H1/H2 excess identifies the exact net "
            "effect tested by full Cech homotopy transfer without fitting.",
            (
                "research/experiments/computable_carrier/"
                "schoen_serre_outer_transfer.py",
            ),
            (),
            True,
            ("quotient deck invariants are not part of cover hypercohomology",),
        ),
        _edge(
            "published_outer_cech_transfer",
            "published_outer_cech_invariants",
            "Perturbed inclusion and projection transfer the synchronized "
            "Schoen deck action to cover cohomology without fitting a relative "
            "character or importing the expected fixed dimensions.",
            (
                "data/generated/scientific_genesis/"
                "published_outer_cech_invariants.json",
            ),
            (),
            True,
            ("fixed cover classes do not select an outer extension coordinate",),
        ),
        _edge(
            "published_outer_cech_invariants",
            "published_outer_universal_cone",
            "The four strict retired representatives form the exact basis of "
            "their scoped diagnostic universal cone.",
            (
                "data/generated/scientific_genesis/"
                "published_outer_cech_invariants.json",
            ),
            (),
            True,
            ("the diagnostic cone is not the selected published family",),
        ),
        _edge(
            "mixed_schoen_outer_universal_cone",
            "published_chain_reconstruction",
            "The lawful universal P1 cone must be related to the source P3 "
            "parameter ledger before it can be identified with the published "
            "generic carrier family.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_outer_universal_cone.json",
            ),
            (),
            False,
            (
                "the lawful and retired parameter spaces have different dimensions",
                "no exact comparison with the source generic locus exists",
            ),
        ),
        _edge(
            "mixed_schoen_outer_universal_cone",
            "published_outer_stability_locus",
            "The source sufficient lower bound is uniform over nontrivial "
            "extensions. The universal split ideal proves every P1 point is "
            "nontrivial, while exact source slopes certify a common chamber.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_outer_stability_locus.json",
            ),
            ("published nontrivial-extension stability theorem",),
            True,
            ("the affine split origin is excluded before projectivization",),
        ),
        _edge(
            "published_outer_stability_locus",
            "published_matter_cohomology",
            "The stable lawful family supplies the exact carrier chain on which "
            "parameter-dependent matter cohomology must be transferred.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_outer_stability_locus.json",
                "data/generated/scientific_genesis/"
                "published_matter_cohomology.json",
            ),
            ("published Wilson-line embedding",),
            False,
            ("lawful mixed matter representatives have not been transferred",),
        ),
        _edge(
            "published_constituent_deck_atlases",
            "published_higgs_cohomology",
            "The lawful constituent maps must lift the four relative P1 classes "
            "through the synchronized diagonal Schoen contraction.",
            (
                "data/generated/scientific_genesis/"
                "relative_constituent_pushdowns.json",
            ),
            ("derived relative signatures over the common P1",),
            False,
            (
                "mixed relative chain maps are absent",
                "full diagonal representatives are absent",
            ),
        ),
        _edge(
            "published_constituent_deck_atlases",
            "relative_constituent_pushdowns",
            "The selected deck-linearized mixed cocycles and exact local units "
            "constrain the source-labelled relative W1/W2 reductions; they "
            "do not derive the assigned equivariant line signatures.",
            (
                "data/generated/scientific_genesis/"
                "relative_constituent_pushdowns.json",
            ),
            ("relative duality", "published line signatures"),
            False,
            (
                "atlas-to-relative equivariant chain map is absent",
                "full Schoen lifts are not part of the relative record",
            ),
        ),
        _edge(
            "published_outer_stability_locus",
            "mixed_schoen_observable_spectrum",
            "Direct synchronized mixed transfers compute constituent matter "
            "cohomology on the lawful stable family; pure H1 makes it independent "
            "of the outer parameter.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_observable_spectrum.json",
            ),
            ("free ninefold Schoen deck action",),
            True,
            ("full matter Schoen representatives remain to be lifted",),
        ),
        _edge(
            "relative_constituent_pushdowns",
            "selected_constituent_determinant_acyclicity",
            "Acyclic determinant lines identify exterior-square cohomology "
            "with the middle constituent tensor for every outer parameter.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_observable_spectrum.json",
            ),
            ("same selected underlying constituent pair",),
            True,
            ("derived-P1 Higgs character labels were later superseded",),
        ),
        _edge(
            "mixed_schoen_observable_spectrum",
            "physical_spectrum",
            "The older derived-pushdown one-Higgs claim cannot establish a "
            "physical spectrum because the full-chain Higgs characters disagree.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_observable_spectrum.json",
            ),
            ("three families and one Higgs pair are selection constraints",),
            False,
            ("the fixed-Wilson one-Higgs gate fails on full-chain H1",),
        ),
        _edge(
            "mixed_schoen_observable_spectrum",
            "strict_mixed_matter_representatives",
            "The synchronized constituent complexes admit exact transferred "
            "deck actions and character projectors on the same full Schoen "
            "Cech--Koszul grading used by the frozen carrier.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_matter_representatives.json",
            ),
            (),
            True,
            (
                "constituent representatives are not yet universal-cone classes",
            ),
        ),
        _edge(
            "published_matter_cohomology",
            "physical_spectrum",
            "Strict mixed matter characters and the Wilson embedding would "
            "determine the family and anti-family blocks.",
            (
                "data/generated/scientific_genesis/"
                "published_matter_cohomology.json",
            ),
            (),
            False,
            ("the mixed matter calculation remains blocked",),
        ),
        _edge(
            "published_higgs_cohomology",
            "physical_spectrum",
            "Strict lifted Higgs characters and the Wilson embedding would "
            "determine doublet and color-triplet multiplicities.",
            (
                "data/generated/scientific_genesis/"
                "published_higgs_cohomology.json",
            ),
            (
                "derived W1/W2 equivariant pushdowns",
                "published Wilson-line embedding",
            ),
            False,
            ("the mixed Higgs calculation remains blocked",),
        ),
        _edge(
            "published_visible_carrier",
            "published_chain_reconstruction",
            "Downstream products require explicit representatives, not dimensions alone.",
            ("research/experiments/visible_bundle_reconstruction/reconstruct.py",),
            (),
            True,
            ("source data are insufficient",),
        ),
        _edge(
            "schoen_geometry",
            "computable_constituent_category",
            "Exact Cox/Koszul geometry supports generated Serre constituents.",
            ("research/experiments/computable_carrier/schoen_outer.py",),
            ("declared finite topology category",),
            True,
            ("category is scoped, not exhaustive over all sheaves",),
        ),
        _edge(
            "computable_constituent_category",
            "cover_ext_screen",
            "Derived Hom totalization computes cover Ext in the declared category.",
            ("research/experiments/computable_carrier/schoen_sparse_outer.py",),
            (),
            True,
            ("outside-category presentations are not covered",),
        ),
        _edge(
            "cover_ext_screen",
            "invariant_ext_cocycles",
            "Exact commuting deck actions define the invariant subcomplex and cocycles.",
            ("research/experiments/computable_carrier/schoen_sparse_outer_actions.py",),
            (),
            True,
            ("action or restriction failure would invalidate quotient classes",),
        ),
        _edge(
            "invariant_ext_cocycles",
            "automorphism_orbits",
            "Constituent unit actions quotient nonzero extension classes.",
            ("research/experiments/computable_carrier/schoen_sparse_outer_automorphisms.py",),
            (),
            True,
            ("non-scalar residual actions require a different orbit normal form",),
        ),
        _edge(
            "automorphism_orbits",
            "automorphism_compression_theorem",
            "Repeated exact action forms motivate a family-level classification.",
            ("data/generated/computable_carrier/tier_b_schoen_outer_automorphisms.partial.json",),
            (),
            False,
            ("remaining strata or singular families may be exceptional",),
        ),
        _edge(
            "invariant_ext_cocycles",
            "smallest_certified_ext_family",
            "Pair 73 supplies four exact invariant cocycles.",
            ("data/generated/computable_carrier/tier_b_schoen_outer_invariants.json",),
            (),
            True,
            ("basis conventions must be preserved",),
        ),
        _edge(
            "automorphism_orbits",
            "smallest_certified_ext_family",
            "Pair 73's unit action identifies only nonzero scalar multiples.",
            ("data/generated/computable_carrier/tier_b_schoen_outer_automorphisms.partial.json",),
            (),
            True,
            ("zero is the split extension",),
        ),
        _edge(
            "smallest_certified_ext_family",
            "universal_ext_family",
            "Exact linearity assembles the four cocycles over the affine "
            "parameter ring, with the origin as the split class.",
            ("research/experiments/scientific_genesis/pair_73_universal.py",),
            (),
            True,
            ("artifact basis or certificate mismatch",),
        ),
        _edge(
            "universal_ext_family",
            "universal_rank_four_family",
            "Exact projective-product contractions solve the three Cech descent "
            "equations and turn each Ext class into a degree-one resolution morphism.",
            (
                "data/generated/scientific_genesis/pair_73_cech_lift.json",
                "research/experiments/scientific_genesis/pair_73_cech_lift.py",
            ),
            (),
            True,
            ("source digest, basis, or totalization-sign mismatch",),
        ),
        _edge(
            "universal_rank_four_family",
            "algebraic_lawful_locus",
            "Fitting, determinant, Chern, equivariance, and reduction loci "
            "are properties of the universal family.",
            (
                "src/onetheory/math/polynomials.py",
                "research/experiments/computable_carrier/downstream.py",
            ),
            (),
            True,
            ("lawful locus may be empty",),
        ),
        _edge(
            "algebraic_lawful_locus",
            "necessary_stability_walls",
            "Exact extension and Serre sequences expose subobjects whose slopes "
            "must be negative at every stable polarization.",
            (
                "src/onetheory/math/geometry.py",
                "research/experiments/scientific_genesis/pair_73_stability_wall.py",
            ),
            (),
            True,
            ("the necessary region may still contain no stable bundle",),
        ),
        _edge(
            "necessary_stability_walls",
            "stability_chamber",
            "A sufficient chamber must satisfy every forced wall and exclude all "
            "additional saturated destabilizing subsheaves.",
            (
                "research/experiments/scientific_genesis/pair_73_stability_wall.py",
                "research/experiments/scientific_genesis/pair_73_stability_no_go.py",
            ),
            (),
            True,
            ("the stable chamber is empty for pair 73",),
        ),
        _edge(
            "stability_chamber",
            "minimum_dimensional_stability_block",
            "The pair-73 restriction theorem depends only on the shared topology "
            "and Hom-support profile, which are checked for every block member.",
            (
                "research/experiments/scientific_genesis/minimal_block_stability_no_go.py",
            ),
            (),
            True,
            ("the theorem is scoped to candidates 3 and 23",),
        ),
        _edge(
            "minimum_dimensional_stability_block",
            "next_topology_stability_block",
            "The same typed restriction test is recomputed in Hom degree minus "
            "one, then exact coefficient positivity excludes the lifted line.",
            (
                "research/experiments/scientific_genesis/next_block_stability_no_go.py",
            ),
            (),
            True,
            ("the theorem is scoped to candidates 14 and 34",),
        ),
        _edge(
            "next_topology_stability_block",
            "current_minimum_stability_block",
            "The next minimum topology is tested through its forced left Serre "
            "line; exact coefficient positivity excludes the full parameter space.",
            (
                "research/experiments/scientific_genesis/"
                "current_minimum_stability_no_go.py",
            ),
            (),
            True,
            ("the theorem is scoped to candidates 8 and 28",),
        ),
        _edge(
            "current_minimum_stability_block",
            "forced_subobject_stability_class",
            "The repeated positive-line obstruction compresses to three "
            "extension-independent subobjects whose slopes are classified "
            "across every declared topology block.",
            (
                "research/experiments/scientific_genesis/"
                "forced_subobject_stability_screen.py",
            ),
            (),
            True,
            ("mixed-sign slope polynomials remain unresolved by this criterion",),
        ),
        _edge(
            "forced_subobject_stability_class",
            "mixed_sign_minimum_forced_chamber",
            "The first unresolved mixed-sign topology is solved by reducing its "
            "two independent homogeneous quadratic walls to exact rational bounds.",
            (
                "research/experiments/scientific_genesis/mixed_sign_minimum_chamber.py",
            ),
            (),
            True,
            ("a nonempty necessary chamber need not contain a stable bundle",),
        ),
        _edge(
            "mixed_sign_minimum_forced_chamber",
            "mixed_sign_minimum_stability_block",
            "The first additional saturated subbundle is obtained by pulling "
            "back the outer extension to the right Serre line; its exact "
            "restriction class vanishes throughout both topology blocks.",
            (
                "research/experiments/scientific_genesis/"
                "mixed_sign_minimum_stability_no_go.py",
            ),
            (),
            True,
            ("the theorem is scoped to candidates 15 and 35",),
        ),
        _edge(
            "mixed_sign_minimum_stability_block",
            "lifted_line_slope_identity_block",
            "The next topology retains universal right-line lifting, while an "
            "exact positive combination of two unavoidable slopes replaces "
            "polarization sampling with a chamber-emptiness proof.",
            (
                "research/experiments/scientific_genesis/"
                "lifted_line_slope_identity_no_go.py",
            ),
            (),
            True,
            ("the theorem is scoped to candidates 16 and 36",),
        ),
        _edge(
            "lifted_line_slope_identity_block",
            "next_survivor_lifting_kernel",
            "The next topology has a nonzero right-line restriction; exact "
            "chain-level quotient reduction identifies its lifting kernel and "
            "the slope identity excludes precisely that closed stratum.",
            (
                "research/experiments/scientific_genesis/"
                "next_survivor_restriction.py",
            ),
            (),
            True,
            (
                "the nonlifting projective complement may still be unstable",
                "the theorem is scoped to candidates 4 and 24",
            ),
        ),
        _edge(
            "next_survivor_lifting_kernel",
            "next_survivor_forced_chamber",
            "After removing the unstable right-line lifting kernel, exact "
            "Schoen intersections reduce the remaining extension-independent "
            "stability conditions to two homogeneous quadratic inequalities.",
            (
                "research/experiments/scientific_genesis/"
                "next_survivor_forced_chamber.py",
            ),
            (),
            True,
            (
                "a nonempty necessary chamber need not contain a stable bundle",
            ),
        ),
        _edge(
            "next_survivor_forced_chamber",
            "next_survivor_generator_strata",
            "The forced chamber makes each maximal right generator line have "
            "slope opposite to the unavoidable left line; exact restriction "
            "maps isolate every locus where such a generator lifts.",
            (
                "research/experiments/scientific_genesis/"
                "next_survivor_generator_restrictions.py",
            ),
            (),
            True,
            (
                "lower proper sublines may lift on larger loci",
                "rank-two and dual rank-three conditions remain open",
            ),
        ),
        _edge(
            "next_survivor_generator_strata",
            "next_survivor_lower_line_block",
            "The unique section of O(3*tau1-phi), or its factor exchange, "
            "induces the zero map on every outer Hom complex. The resulting "
            "universal lift has an incompatible exact slope identity.",
            (
                "research/experiments/scientific_genesis/"
                "lower_line_sections.py",
                "research/experiments/scientific_genesis/"
                "next_survivor_lower_line_no_go.py",
            ),
            (),
            True,
            ("the theorem is scoped to candidates 4 and 24",),
        ),
        _edge(
            "next_survivor_lower_line_block",
            "declared_carrier_category",
            "The same exact lower-line chain map applies to the only remaining "
            "blocks 5 and 25. Exhaustive evaluation gives zero pullback in all "
            "72 frozen projective families and the same positive fiber slope.",
            (
                "research/experiments/scientific_genesis/"
                "remaining_lower_line_no_go.py",
            ),
            (),
            True,
            (
                "the no-go is limited to the declared finite monomial category",
                "general Schoen bundles are not excluded",
            ),
        ),
        _edge(
            "stability_chamber",
            "physical_spectrum",
            "A stable descended replacement bundle is required before the physical "
            "sheaf cohomology problem can proceed; pair 73 cannot supply it.",
            ("src/onetheory/physics/compactification.py",),
            exact_law,
            False,
            (
                "pair 73 has empty stable locus",
                "replacement cohomology may jump",
                "spectrum constraints may fail",
            ),
        ),
        _edge(
            "physical_spectrum",
            "computable_carrier_state",
            "Spectrum selection alone cannot freeze a physical quotient "
            "component without a trivial equivariant determinant.",
            (
                "data/generated/scientific_genesis/"
                "computable_one_theory_carrier_state.json",
            ),
            ("selection constraints are not predictions",),
            False,
            ("the selected determinant has character (2,1)",),
        ),
        _edge(
            "published_constituent_deck_atlases",
            "selected_atlas_common_frame_comparison",
            "Native atlas line actions determine the source-bound frames; "
            "exact coordinate-lift ratios determine their common-Schoen form.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_atlas_frame_comparison.json",
            ),
            ("declared common homogeneous lifts",),
            True,
            ("a constituent frame relation does not select an outer extension",),
        ),
        _edge(
            "mixed_schoen_outer_actions",
            "selected_atlas_common_frame_comparison",
            "The synchronized object frames identify the exact relative "
            "characters after all Koszul-degree corrections.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_atlas_frame_comparison.json",
            ),
            (),
            True,
            ("a different carrier can have a different frame relation",),
        ),
        _edge(
            "selected_atlas_common_frame_comparison",
            "selected_mixed_determinant_descent",
            "The raw first-constituent line scalar is not an independent "
            "determinant correction; its full-chain conversion is a uniform "
            "character twist.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_atlas_frame_comparison.json",
            ),
            (),
            True,
            ("the selected rank-four determinant remains nontrivial",),
        ),
        _edge(
            "published_constituent_deck_actions",
            "selected_mixed_determinant_descent",
            "Alternating exact frame determinants and scalar top-cohomology "
            "actions independently detect the selected quotient character.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_determinant_descent.json",
            ),
            (),
            True,
            ("a distinct lawful relinearization has not been audited",),
        ),
        _edge(
            "selected_mixed_determinant_descent",
            "computable_carrier_state",
            "A physical SU(4) quotient freeze requires trivial equivariant "
            "determinant as well as stable cover geometry.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_determinant_descent.json",
            ),
            (),
            False,
            ("the selected character is (2,1)",),
        ),
        _edge(
            "selected_mixed_determinant_descent",
            "computable_reverse_carrier_state",
            "Reversing the extension preserves the constituent determinant "
            "character, so the same missing quotient trivialization applies.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_determinant_descent.json",
            ),
            (),
            False,
            ("the selected character is (2,1)",),
        ),
        _edge(
            "mixed_schoen_reverse_outer_stability_locus",
            "mixed_schoen_reverse_observable_spectrum",
            "Pure-H1 constituent cohomology kills every matter connecting-rank "
            "dependence, while acyclic determinant endpoints reduce either "
            "exterior-square filtration to the same tensor middle term.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_reverse_observable_spectrum.json",
            ),
            ("published Wilson-line embedding",),
            True,
            ("full common-DGA representatives are not supplied by dimensions",),
        ),
        _edge(
            "mixed_schoen_reverse_observable_spectrum",
            "computable_reverse_carrier_state",
            "Spectrum selection remains conditional on quotient determinant "
            "descent before the reverse component can be frozen physically.",
            (
                "data/generated/scientific_genesis/"
                "computable_one_theory_reverse_carrier_state.json",
            ),
            ("selection constraints are not predictions",),
            False,
            ("the selected determinant has character (2,1)",),
        ),
        _edge(
            "computable_reverse_carrier_state",
            "reverse_universal_down_matter_lifts",
            "The frozen reverse sequence fixes six invariant extension "
            "directions, so exact common-DGA contraction determines each "
            "parameter-linear quotient-class correction.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_reverse_down_matter_lifts.json",
            ),
            (
                "physical source characters are routed by exact pullback inversion",
            ),
            True,
            ("the reverse universal Higgs class is not yet constructed",),
        ),
        _edge(
            "strict_mixed_matter_representatives",
            "reverse_universal_down_matter_lifts",
            "Strict constituent matter cocycles provide the constant V2 "
            "classes and the V1 quotient classes corrected in the reverse cone.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_reverse_down_matter_lifts.json",
            ),
            (),
            True,
            (),
        ),
        _edge(
            "computable_reverse_carrier_state",
            "reverse_universal_down_higgs_lift",
            "The six invariant reverse extension directions act on the "
            "middle tensor Higgs class through the determinant-two filtration.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_reverse_higgs_lifts.json",
            ),
            (),
            True,
            ("the complete down Yukawa contraction remains unresolved",),
        ),
        _edge(
            "strict_mixed_higgs_representative",
            "reverse_universal_down_higgs_lift",
            "The exact 27-term middle tensor cocycle supplies the class "
            "whose six determinant-two boundaries are solved in the reverse cone.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_reverse_higgs_lifts.json",
            ),
            ("source characters are obtained by inverse pullback",),
            True,
            (),
        ),
        _edge(
            "reverse_universal_down_matter_lifts",
            "reverse_down_matrix_support",
            "The quotient family has one V1 term and a linear V2 correction, "
            "whereas both subobject families are constant V2 terms.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_reverse_down_support.json",
            ),
            (),
            True,
            ("the central coefficient remains unresolved",),
        ),
        _edge(
            "reverse_universal_down_higgs_lift",
            "reverse_down_matrix_support",
            "The Higgs has a strict V1-V2 term and a linear determinant-V2 "
            "correction, allowing exact exterior-degree selection.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_reverse_down_support.json",
            ),
            (),
            True,
            (),
        ),
        _edge(
            "mixed_down_tree_matrix",
            "reverse_down_matrix_support",
            "The four strict mixed slots have exact zero-boundary witnesses "
            "in the same constituent basis independently of extension order.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_reverse_down_support.json",
            ),
            (),
            True,
            (),
        ),
        _edge(
            "reverse_down_matrix_support",
            "reverse_physical_v1_pluecker_pairing",
            "Exterior selection isolates the V1-V1 slot, making its "
            "determinant pairing a required input to the central trace.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_v1_pluecker_chain_map.json",
            ),
            (),
            True,
            ("the complete central trace is not yet computed",),
        ),
        _edge(
            "strict_mixed_matter_representatives",
            "reverse_physical_v1_pluecker_pairing",
            "The two exact V1 character cocycles supply the ordered matter "
            "inputs for the determinant pairing.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_v1_pluecker_chain_map.json",
            ),
            (),
            True,
            (),
        ),
        _edge(
            "mixed_local_determinant_pairings",
            "reverse_physical_v1_pluecker_pairing",
            "First-constituent local minors and hypersurface overlap "
            "quotients define the global cochain contraction.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_v1_pluecker_chain_map.json",
            ),
            (),
            True,
            (),
        ),
        _edge(
            "alternate_metric_quotient_generation",
            "visible_metrics",
            "Serre cover generation, orbit interpolation, averaging, and "
            "large-twist acyclicity prove the carrier's exact global-"
            "generation prerequisite on the quotient.",
            (
                "data/generated/scientific_genesis/alternate_metric_quotient_generation.json",
                "research/experiments/scientific_genesis/"
                "ALTERNATE_METRIC_QUOTIENT_GENERATION_NOTE.md",
            ),
            ("selected heterotic UV realization", "declared mathematical twist"),
            True,
            ("generation does not provide invariant bases or converged metrics",),
        ),
        _edge(
            "alternate_metric_first_subline_sections",
            "visible_metrics",
            "The actual-frame invariant subline basis supplies one direct "
            "component of the exact carrier section construction.",
            (
                "data/generated/scientific_genesis/"
                "alternate_metric_first_subline_sections.json",
                "research/experiments/scientific_genesis/"
                "ALTERNATE_METRIC_FIRST_SUBLINE_SECTIONS_NOTE.md",
            ),
            ("determinant-repaired alternate carrier",),
            True,
            ("Serre quotient lifts and complete carrier sections remain missing",),
        ),
        _edge(
            "alternate_metric_quotient_generation",
            "alternate_metric_first_resolution_ambient_sections",
            "The declared generating twist and actual repaired carrier "
            "frame fix both invariant ambient block section spaces.",
            (
                "data/generated/scientific_genesis/"
                "alternate_metric_first_resolution_ambient_sections.json",
            ),
            ("natural ambient twist linearization",),
            True,
            ("individual F0 lines do not descend",),
        ),
        _edge(
            "alternate_metric_first_resolution_ambient_sections",
            "visible_metrics",
            "The actual ambient block vectors supply explicit inputs for "
            "the invariant Koszul and Hilbert-Burch section quotient.",
            (
                "data/generated/scientific_genesis/"
                "alternate_metric_first_resolution_ambient_sections.json",
                "research/experiments/scientific_genesis/"
                "ALTERNATE_METRIC_FIRST_RESOLUTION_AMBIENT_SECTIONS_NOTE.md",
            ),
            ("determinant-repaired alternate carrier",),
            True,
            ("ambient vectors alone are not restricted sections or Serre lifts",),
        ),
        _edge(
            "alternate_metric_first_resolution_ambient_sections",
            "alternate_metric_first_quotient_sections",
            "The actual block frame determines the equivariant monomial "
            "ideal image; its two-equation ideal Koszul quotient and a "
            "nonzero integral minor supply the exact quotient basis.",
            (
                "data/generated/scientific_genesis/alternate_metric_first_quotient_sections.json",
                "research/experiments/scientific_genesis/"
                "ALTERNATE_METRIC_FIRST_QUOTIENT_SECTIONS_NOTE.md",
            ),
            ("source-checked regularity on the coordinate-axis quotient",),
            True,
            ("wrong ideal image character selects a different invariant space",),
        ),
        _edge(
            "alternate_metric_first_quotient_sections",
            "visible_metrics",
            "The actual quotient section basis supplies all 1540 "
            "quotient inputs for the first constituent's Serre lifts.",
            (
                "data/generated/scientific_genesis/alternate_metric_first_quotient_sections.json",
            ),
            ("determinant-repaired alternate carrier",),
            True,
            ("a quotient basis is not a lifted constituent or rank-four basis",),
        ),
        _edge(
            "alternate_metric_first_subline_sections",
            "alternate_metric_first_serre_lifts",
            "The certified 1115-vector subline basis injects into the "
            "first constituent and supplies the kernel of its H0 quotient map.",
            ("data/generated/scientific_genesis/alternate_metric_first_serre_lifts.json",),
            ("exact first Serre sequence",),
            True,
            ("subline sections alone do not span the constituent",),
        ),
        _edge(
            "alternate_metric_first_quotient_sections",
            "alternate_metric_first_serre_lifts",
            "Nine actual full-complex P1 lift templates transport by "
            "global plane polynomials, producing exact invariant lifts of "
            "every certified quotient basis vector.",
            ("data/generated/scientific_genesis/alternate_metric_first_serre_lifts.json",),
            ("actual repaired first constituent", "source-checked polynomial residual shape"),
            True,
            ("discarding the nonsplit correction destroys full closure",),
        ),
        _edge(
            "alternate_metric_first_serre_lifts",
            "visible_metrics",
            "The complete V1 section basis supplies one genuine constituent "
            "input for the eventual rank-four metric construction.",
            ("data/generated/scientific_genesis/alternate_metric_first_serre_lifts.json",),
            ("selected heterotic UV realization",),
            True,
            ("universal rank-four lifts and metric convergence remain necessary",),
        ),
        _edge(
            "alternate_metric_quotient_generation",
            "alternate_metric_second_sections",
            "The actual alternate ray and declared twist fix the second "
            "subline, ideal Koszul presentation, and nonsplit section lifts.",
            ("data/generated/scientific_genesis/alternate_metric_second_sections.json",),
            ("source-checked actual second ideal frame", "fat-axis regular sequence"),
            True,
            ("reference-ray sections are not alternate-ray sections",),
        ),
        _edge(
            "alternate_metric_second_sections",
            "visible_metrics",
            "The complete actual V2 basis supplies all quotient inputs "
            "for universal rank-four section lifting at the generating twist.",
            ("data/generated/scientific_genesis/alternate_metric_second_sections.json",),
            ("actual parameter-dependent outer extension",),
            True,
            ("the direct sum of constituent bases is not the nonsplit rank-four basis",),
        ),
        _edge(
            "alternate_metric_first_serre_lifts",
            "alternate_metric_outer_lift_formula",
            "The complete V1 basis supplies the injected half of the "
            "universal section construction in the actual target complex.",
            ("data/generated/scientific_genesis/alternate_metric_outer_lifts.json",),
            ("actual first-constituent target contraction",),
            True,
            ("an injected constituent basis alone does not give outer lifts",),
        ),
        _edge(
            "alternate_metric_second_sections",
            "alternate_metric_outer_lift_formula",
            "Every actual V2 section enters the same finite outer "
            "homotopy formula with both frozen universal coefficients.",
            ("data/generated/scientific_genesis/alternate_metric_outer_lifts.json",),
            ("standard contraction identity", "strict invariant outer cocycles"),
            True,
            ("full independent formula or coefficient replay is still required",),
        ),
        _edge(
            "alternate_metric_outer_lift_formula",
            "visible_metrics",
            "The universal section constructor provides the nonsplit "
            "cochains needed for later rank-four evaluation and metric work.",
            ("data/generated/scientific_genesis/alternate_metric_outer_lifts.json",),
            ("independent full formula certification",),
            True,
            ("a formal section basis is not a converged Ricci-flat or HYM metric",),
        ),
        _edge(
            "alternate_metric_outer_lift_formula",
            "alternate_metric_lift_operator_certificate",
            "Independent support incidence, actual module operators, and "
            "repaired arrow equivariance certify the complete finite "
            "universal lifting formula rather than only its coefficient probes.",
            ("data/generated/scientific_genesis/"
             "alternate_metric_lift_operator_certificate.json",),
            ("actual target D squared equals zero", "complete constituent H0 bases"),
            True,
            ("raw contraction alone does not certify outer composition or averaging",),
        ),
        _edge(
            "alternate_metric_lift_operator_certificate",
            "visible_metrics",
            "The certified universal invariant section constructor supplies "
            "the actual nonsplit rank-four basis for subsequent fiber evaluation.",
            ("data/generated/scientific_genesis/"
             "alternate_metric_lift_operator_certificate.json",),
            ("explicit local fiber evaluation", "controlled metric convergence"),
            True,
            ("a certified section constructor is not a numerical metric",),
        ),
        _edge(
            "alternate_metric_lift_operator_certificate",
            "alternate_metric_fiber_evaluation",
            "Restricting actual universal section cochains to a declared chart "
            "and quotienting the actual local relations gives their fiber values.",
            ("data/generated/scientific_genesis/alternate_metric_fiber_evaluation.json",),
            ("point satisfies both cover equations", "explicit nonzero relation minors"),
            True,
            ("an implicit fiber basis or dropped Serre/outer terms changes the evaluated object",),
        ),
        _edge(
            "alternate_metric_fiber_evaluation",
            "visible_metrics",
            "Actual framed section values provide algebraic inputs to controlled "
            "metric evaluation; four spanning probe columns alone are not metrics.",
            ("data/generated/scientific_genesis/alternate_metric_fiber_evaluation.json",),
            ("controlled full-basis sampling", "declared moduli and measure", "metric convergence"),
            True,
            ("local algebraic evaluation supplies neither a measure nor a Hermitian metric",),
        ),
        _edge(
            "alternate_metric_fiber_evaluation",
            "alternate_metric_specialized_evaluation",
            "Polynomial coefficient naturality and explicit deck channels "
            "evaluate the same certified basis without repeated full-cover expansion.",
            ("data/generated/scientific_genesis/alternate_metric_specialized_evaluation.json",),
            ("nonnegative second-plane support", "certified finite primitive series"),
            True,
            ("Laurent poles cannot be evaluated by the regular-factor specialization",),
        ),
        _edge(
            "alternate_metric_specialized_evaluation",
            "visible_metrics",
            "The complete exact point matrix supplies an actual section-data "
            "checkpoint for subsequent controlled geometric sampling.",
            ("data/generated/scientific_genesis/alternate_metric_specialized_evaluation.json",),
            ("controlled numerical roots and sampling", "declared measure", "metric convergence"),
            True,
            ("a complete matrix at one point is not an integral or a Hermitian metric",),
        ),
        _edge(
            "schoen_geometry",
            "alternate_metric_measure",
            "The actual complete-intersection equations determine the double "
            "residue and the FS auxiliary topological mass; deck determinants "
            "and equation units certify their descent.",
            ("data/generated/scientific_genesis/alternate_metric_measure.json",),
            ("explicit affine chart and form scale", "normalized ambient FS forms"),
            True,
            ("ramified projections require another explicit chart",
             "omitting equation units changes the residue character"),
        ),
        _edge(
            "alternate_metric_measure",
            "visible_metrics",
            "Explicit residue densities and normalized auxiliary weights give "
            "geometric integration inputs without changing the carrier or "
            "selecting physical moduli.",
            ("data/generated/scientific_genesis/alternate_metric_measure.json",),
            ("controlled projective roots and branch-complete sampling",
             "independent integration-error control", "Ricci-flat/HYM convergence"),
            True,
            ("a correct measure alone is not a converged metric",
             "uniform affine-coordinate sampling has the wrong point law"),
        ),
        _edge(
            "alternate_metric_measure",
            "alternate_metric_projective_roots",
            "The declared projective intersection scheme requires both actual "
            "restricted cubics to be solved completely, including the excluded "
            "point in each parameter chart.",
            ("data/generated/scientific_genesis/alternate_metric_projective_roots.json",),
            ("exact Q(omega) line bases and shared P1 input", "transverse restrictions"),
            True,
            ("a small residual proves neither root existence nor completeness",
             "discarding infinity or repeated roots changes the geometric sample law"),
        ),
        _edge(
            "alternate_metric_projective_roots",
            "visible_metrics",
            "Complete algebraic root descriptions supply geometric integration "
            "inputs only after their uncertainty is propagated into chart, "
            "section, and measure evaluations.",
            ("data/generated/scientific_genesis/alternate_metric_projective_roots.json",),
            ("bounded section and density evaluation", "controlled SU-uniform proposal law",
             "independent integration-error control", "Ricci-flat/HYM convergence"),
            True,
            ("disk centers do not exactly satisfy the cover equations",
             "regression configurations are not SU-uniform samples"),
        ),
        _edge(
            "alternate_metric_projective_roots",
            "alternate_metric_enclosures",
            "Certified roots of the actual line restrictions determine geometric "
            "points; outward bounds propagate their uncertainty without replacing "
            "them by centers that do not satisfy the equations.",
            ("data/generated/scientific_genesis/alternate_metric_enclosures.json",),
            ("explicit invertible homogeneous pivots", "unramified projection enclosure",
             "declared rational error precision"),
            True,
            ("a possible zero denominator must reject this enclosure",
             "a residual containing zero is not a membership proof"),
        ),
        _edge(
            "alternate_metric_first_serre_lifts",
            "alternate_metric_enclosures",
            "The actual invariant constituent section cochains supply exact "
            "Laurent coefficients for bounded local-generator evaluation.",
            ("data/generated/scientific_genesis/alternate_metric_enclosures.json",),
            ("compatible component and chart bases", "declared local line frames"),
            True,
            ("ambient generators are not a rank-four bundle quotient",),
        ),
        _edge(
            "alternate_metric_second_sections",
            "alternate_metric_enclosures",
            "The second constituent's actual archived sections provide "
            "coefficient data, without replacing their universal outer lifts.",
            ("data/generated/scientific_genesis/alternate_metric_enclosures.json",),
            ("same actual constituent archive", "compatible local generator basis"),
            True,
            ("V2 constituent coefficients alone do not evaluate the universal bundle",),
        ),
        _edge(
            "alternate_metric_enclosures",
            "visible_metrics",
            "Bounded densities and local coefficients are integration inputs "
            "once the actual universal fiber quotients, complete section "
            "evaluation, and proposal/integration errors are also controlled.",
            ("data/generated/scientific_genesis/alternate_metric_enclosures.json",),
            ("bounded universal quotient frames and complete section matrix",
             "controlled SU-uniform proposal law", "independent integration-error control",
             "Ricci-flat/HYM convergence"),
            True,
            ("certified local densities do not give a sampling law or Hermitian metric",),
        ),
        _edge(
            "alternate_metric_enclosures",
            "alternate_metric_bounded_fibers",
            "Certified geometric and Laurent coefficient bounds enclose the "
            "actual universal relation matrices and their selected quotient frames.",
            ("data/generated/scientific_genesis/alternate_metric_bounded_fibers.json",),
            ("declared compatible generator bases", "determinant balls exclude zero"),
            True,
            ("an accepted local frame is not global atlas coverage",
             "a zero-containing residual does not prove a quotient identity"),
        ),
        _edge(
            "alternate_metric_fiber_evaluation",
            "alternate_metric_bounded_fibers",
            "The original nine-generator/five-relation construction supplies "
            "the same local frame semantics without substituting uncertified centers.",
            ("data/generated/scientific_genesis/alternate_metric_bounded_fibers.json",),
            ("same original differential and outer cup", "explicit row and line-frame choices"),
            True,
            ("discarding the outer relation would replace the bundle by a direct sum",),
        ),
        _edge(
            "alternate_metric_lift_operator_certificate",
            "alternate_metric_bounded_fibers",
            "The certified universal section constructor gives actual constant "
            "and extension-linear cochains for coefficientwise bounded evaluation.",
            ("data/generated/scientific_genesis/alternate_metric_bounded_fibers.json",),
            ("original full outer lift", "declared local quotient domain"),
            True,
            ("on-demand construction does not establish practical full-matrix throughput",),
        ),
        _edge(
            "alternate_metric_bounded_fibers",
            "visible_metrics",
            "Actual universal frame and section enclosures supply bundle-valued "
            "integration inputs after complete bounded evaluation, proposal "
            "precision, integration error, and metric convergence are established.",
            ("data/generated/scientific_genesis/alternate_metric_bounded_fibers.json",),
            ("controlled complete section evaluation", "SU-uniform proposal law",
             "independent integration errors", "Ricci-flat/HYM convergence"),
            True,
            ("two corrected section probes are not a complete bounded matrix or metric",),
        ),
        _edge(
            "alternate_metric_bounded_fibers",
            "alternate_metric_bounded_support",
            "Determinant-certified actual nonsplit quotient frames map bounded "
            "original section coefficients to the same named universal fibers.",
            ("data/generated/scientific_genesis/alternate_metric_bounded_support.json",),
            ("same original generator basis and declared chart", "invertible pivot enclosures"),
            True,
            ("a failed determinant cannot be replaced by a guessed frame",),
        ),
        _edge(
            "alternate_metric_specialized_evaluation",
            "alternate_metric_bounded_support",
            "The original ordered complete section streams and finite-pole "
            "operator identities admit coefficient-enclosure evaluation without "
            "changing sections or discarding Laurent phases.",
            ("data/generated/scientific_genesis/alternate_metric_bounded_support.json",),
            ("same 2655+2690 index ordering", "exact original unit operators",
             "discard only exact zeros"),
            True,
            ("center-zero pruning would discard potentially nonzero section values",),
        ),
        _edge(
            "alternate_metric_lift_operator_certificate",
            "alternate_metric_bounded_support",
            "The exact operator identities and strictly increasing finite "
            "filtration justify the identical lifting series over enclosed "
            "coefficients even when arithmetic cancellation is unresolved.",
            ("data/generated/scientific_genesis/alternate_metric_bounded_support.json",),
            ("same original component/cell labels", "same five-term filtration bound"),
            True,
            ("an unexpected sixth term is a failure, not a truncation rule",),
        ),
        _edge(
            "alternate_metric_bounded_support",
            "visible_metrics",
            "The bounded all-index evaluator supplies actual section integration "
            "inputs once complete output, practical throughput, proposal precision, "
            "integration error, and Ricci-flat/HYM convergence are certified.",
            ("data/generated/scientific_genesis/alternate_metric_bounded_support.json",),
            ("complete bounded matrix and measured multi-point cost", "SU-uniform proposal law",
             "independent integration errors", "Ricci-flat/HYM convergence"),
            True,
            ("three-index packets are not a complete matrix, probability law, or metric",),
        ),
        _edge(
            "alternate_metric_measure",
            "alternate_metric_weight_moments",
            "The actual residue and auxiliary form determine the importance "
            "weight whose singular-set moments must be established analytically.",
            ("data/generated/scientific_genesis/alternate_metric_weight_moments.json",),
            ("actual critical-fiber algebra", "local density comparability proof"),
            True,
            ("a finite weight at sampled probes does not establish finite moments",),
        ),
        _edge(
            "alternate_metric_weight_moments",
            "visible_metrics",
            "Moment integrability constrains admissible statistical error "
            "methods once the correct probability law, bounded integrands, "
            "quantitative bounds, and metric convergence are also established.",
            ("research/experiments/scientific_genesis/ALTERNATE_METRIC_WEIGHT_MOMENTS_NOTE.md",),
            ("controlled independent draws from A/9", "bounded tested integrands",
             "quantitative error control", "Ricci-flat/HYM convergence"),
            True,
            ("finite variance is not a numerical variance bound or a sampler",),
        ),
        _edge(
            "alternate_metric_measure",
            "alternate_metric_positive_measure",
            "The same residue, ambient FS forms, and actual complete-intersection "
            "class determine a positive auxiliary law once its mass is computed.",
            ("data/generated/scientific_genesis/alternate_metric_positive_measure.json",),
            ("explicit positive FS sum", "exact mixed intersection masses"),
            True,
            ("an auxiliary FS form is not the physical Ricci-flat metric",),
        ),
        _edge(
            "alternate_metric_weight_moments",
            "alternate_metric_positive_measure",
            "The actual nodal-fiber proof supplies smoothness and identifies "
            "the degeneracy to remove by a strictly positive auxiliary law.",
            ("research/experiments/scientific_genesis/ALTERNATE_METRIC_POSITIVE_MEASURE_NOTE.md",),
            ("same actual frozen compact cover", "separate positivity proof"),
            True,
            ("changing the proposal cannot change the target residue volume",),
        ),
        _edge(
            "alternate_metric_positive_measure",
            "visible_metrics",
            "A positive auxiliary law can supply bounded-weight integration "
            "only after controlled proposals, quantitative bounds, section "
            "throughput, and Ricci-flat/HYM convergence are established.",
            ("research/experiments/scientific_genesis/ALTERNATE_METRIC_POSITIVE_MEASURE_NOTE.md",),
            ("correct independent projective draws", "quantitative error bounds",
             "complete section evaluation", "Ricci-flat/HYM convergence"),
            True,
            ("existence of a finite global bound does not compute that bound",),
        ),
        _edge(
            "alternate_metric_positive_measure",
            "alternate_metric_critical_charts",
            "The positive proposal gives actual point-line component equations "
            "and a density that remains positive at critical fibers.",
            ("research/experiments/scientific_genesis/alternate_metric_positive_measure.py",),
            ("certified actual partner roots", "explicit nonzero base-coordinate derivative"),
            True,
            ("uniform sampling cannot be inferred from exact regression inputs",),
        ),
        _edge(
            "alternate_metric_positive_measure",
            "projective_uniform_input_cells",
            "Each auxiliary mixture component requires uniform projective "
            "point or dual-hyperplane inputs; simplex spacings and phase cells "
            "retain the precision error of that same probability law.",
            ("research/experiments/scientific_genesis/PROJECTIVE_UNIFORM_INPUT_CELLS_NOTE.md",),
            ("normalized FS convention", "independent uniform input bits"),
            True,
            ("rounded centers alone are not continuous uniform draws",),
        ),
        _edge(
            "projective_uniform_input_cells",
            "auxiliary_cover_draws",
            "Nested bit prefixes enclose the same continuous projective inputs; "
            "independent discrete selectors realize the derived auxiliary mixture.",
            ("research/experiments/scientific_genesis/AUXILIARY_COVER_DRAWS_NOTE.md",),
            ("mutually independent infinite fair named bit streams",),
            True,
            ("deterministic finite addresses do not establish IID",),
        ),
        _edge(
            "projective_uncertain_intersections",
            "auxiliary_cover_draws",
            "Existing complete uniform root certificates and strict projective "
            "containment identify the same actual branch under input refinement.",
            ("research/experiments/scientific_genesis/auxiliary_cover_draws.py",),
            ("whole-cell restrictions", "complete disjoint roots",
             "same input prefixes and explicitly declared frames"),
            True,
            ("resampling a numerical failure biases the proposed law",
             "sorted root-center positions need not persist under refinement"),
        ),
        _edge(
            "alternate_metric_positive_measure",
            "auxiliary_cover_draws",
            "The intersection-derived FS cube fixes mixture probabilities and "
            "complete-root multiplicities, without choosing physical moduli.",
            ("research/experiments/scientific_genesis/AUXILIARY_COVER_DRAWS_NOTE.md",),
            ("same actual smooth cover", "normalized auxiliary FS convention"),
            True,
            ("an auxiliary proposal is not a Ricci-flat metric",),
        ),
        _edge(
            "auxiliary_cover_draws",
            "visible_metrics",
            "Admitted same-draw refinements can supply native point and weight "
            "bounds to original metric integrands once independent inputs, "
            "complete sections and controlled integral errors are available.",
            ("research/experiments/scientific_genesis/auxiliary_cover_draws.py",),
            ("externally justified independent inputs", "complete original integrands",
             "controlled integration errors", "Ricci-flat/HYM convergence"),
            True,
            ("selecting only successfully admitted numerical draws biases an integral",),
        ),
        _edge(
            "projective_uniform_input_cells",
            "visible_metrics",
            "Coupled projective input bounds can feed the unchanged intersection "
            "law only after uncertain coefficient root completeness, chart and "
            "section bounds, independent integration errors, and metric convergence.",
            ("research/experiments/scientific_genesis/projective_uniform_input_cells.py",),
            ("independent uniform inputs", "branch-complete roots for uncertain inputs",
             "actual integrand bounds", "Ricci-flat/HYM convergence"),
            True,
            ("input-space chordal error is not an intersection integrand error",
             "rejecting difficult configurations can bias the probability law"),
        ),
        _edge(
            "projective_uniform_input_cells",
            "projective_uncertain_intersections",
            "Explicit line frames and original cubic monomial substitution "
            "enclose the full input-cell coefficient family; strict uniform "
            "Rouche bounds retain every projective intersection branch.",
            ("research/experiments/scientific_genesis/PROJECTIVE_UNCERTAIN_INTERSECTIONS_NOTE.md",),
            ("nonzero explicit pivots", "strict admitted-cell margins"),
            True,
            ("a cell-center polynomial alone does not retain proposal error",),
        ),
        _edge(
            "alternate_metric_projective_roots",
            "projective_uncertain_intersections",
            "Existing exact proposals and Taylor witnesses supply center disks; "
            "coefficient perturbation bounds certify all actual cell members, "
            "including a moving reciprocal-chart infinity branch.",
            ("research/experiments/scientific_genesis/projective_uncertain_intersections.py",),
            ("simple center roots", "uniform coefficient-error margin", "projective disjointness"),
            True,
            ("a failed work cap is not a geometric no-go",),
        ),
        _edge(
            "projective_uncertain_intersections",
            "visible_metrics",
            "Coupled cover-coordinate bounds can feed the same metric integrals "
            "only after law-preserving independent draws, actual density/frame "
            "and section bounds, integration errors, and Ricci-flat/HYM convergence.",
            ("research/experiments/scientific_genesis/PROJECTIVE_UNCERTAIN_INTERSECTIONS_NOTE.md",),
            ("independent uniform inputs", "actual integrand bounds",
             "controlled integration error", "Ricci-flat/HYM convergence"),
            True,
            ("admitted regression cells are not an independent cover cloud",),
        ),
        _edge(
            "projective_uncertain_intersections",
            "uncertain_cover_weights",
            "Complete actual root families with their same bounded base or "
            "source-derived base supply coupled cover-coordinate enclosures.",
            ("research/experiments/scientific_genesis/uncertain_cover_weights.py",),
            ("actual original pencil restrictions", "complete uniform root certificates"),
            True,
            ("an arbitrary tuple of coordinate balls does not certify cover membership",),
        ),
        _edge(
            "alternate_metric_projection_free_weights",
            "uncertain_cover_weights",
            "The existing positive-law weight has a homogeneous conormal "
            "identity; outward arithmetic propagates source and root errors "
            "without tangent-chart or individual fiber-gradient inversion.",
            ("research/experiments/scientific_genesis/UNCERTAIN_COVER_WEIGHTS_NOTE.md",),
            ("positive homogeneous norms", "positive full conormal denominator",
             "explicit unchanged normalization convention"),
            True,
            ("off-cover coordinate functionals test arithmetic, not membership",),
        ),
        _edge(
            "uncertain_cover_weights",
            "visible_metrics",
            "Admitted-family auxiliary weights can feed the same physical "
            "metric computation only with law-preserving independent inputs, "
            "section/frame bounds, integration errors and metric convergence.",
            ("research/experiments/scientific_genesis/UNCERTAIN_COVER_WEIGHTS_NOTE.md",),
            ("independent cover draws", "actual complete section integrands",
             "controlled integration errors", "Ricci-flat/HYM convergence"),
            True,
            ("positive auxiliary weight intervals are not a physical Hermitian metric",),
        ),
        _edge(
            "projective_uncertain_intersections",
            "uncertain_cover_frames",
            "The native actual root-family certificate admits each branch into "
            "the same bounded homogeneous chart representation with input error intact.",
            ("research/experiments/scientific_genesis/UNCERTAIN_COVER_FRAMES_NOTE.md",),
            ("explicit root branch", "nonzero declared homogeneous pivots"),
            True,
            ("raw coordinate balls and root centers are not membership certificates",),
        ),
        _edge(
            "alternate_metric_bounded_fibers",
            "uncertain_cover_frames",
            "The original relation cochains and determinant-certified block "
            "elimination apply unchanged to these actual coordinate enclosures.",
            ("research/experiments/scientific_genesis/alternate_metric_bounded_fibers.py",),
            ("nonzero declared relation minors", "same original constituent and outer data"),
            True,
            ("admitting a point type alone does not verify a new domain or section",),
        ),
        _edge(
            "uncertain_cover_frames",
            "visible_metrics",
            "Original section bounds on uncertain-input domains can feed metrics "
            "only after complete integrand, independent law-preserving input and "
            "integration convergence checks.",
            ("research/experiments/scientific_genesis/UNCERTAIN_COVER_FRAMES_NOTE.md",),
            ("complete actual section integrands", "controlled independent integration",
             "Ricci-flat/HYM convergence"),
            True,
            ("a few section probes are not a full section matrix or a metric",),
        ),
        _edge(
            "alternate_metric_global_weight_bound",
            "uncertain_cover_weights",
            "The unit-homogeneous conormal proof gives explicit normalization "
            "factors for arbitrary nonzero homogeneous representatives.",
            ("research/experiments/scientific_genesis/"
             "ALTERNATE_METRIC_GLOBAL_WEIGHT_BOUND_NOTE.md",),
            ("actual cover Euler identities", "unchanged cubic multidegrees"),
            True,
            ("off-cover Euler cancellation cannot be used as a membership proof",),
        ),
        _edge(
            "alternate_metric_weight_moments",
            "alternate_metric_critical_charts",
            "The nodal-fiber proof establishes a nonzero base derivative on the "
            "critical factor and a regular partner factor for the actual cover.",
            ("research/experiments/scientific_genesis/ALTERNATE_METRIC_WEIGHT_MOMENTS_NOTE.md",),
            ("actual nodal critical loci", "declared compatible projection pivots"),
            True,
            ("a critical triangle may require algebraic input beyond Q(omega)",),
        ),
        _edge(
            "alternate_metric_critical_charts",
            "visible_metrics",
            "Certified critical-factor coordinates extend positive-law integration "
            "only after global coverage, controlled proposals, quantitative "
            "bounds, and Ricci-flat/HYM convergence are also established.",
            ("research/experiments/scientific_genesis/ALTERNATE_METRIC_CRITICAL_CHARTS_NOTE.md",),
            ("global atlas coverage", "controlled proposals and numerical error",
             "actual complete section evaluation", "Ricci-flat/HYM convergence"),
            True,
            ("axis-node probes do not certify all triangle-node input domains",),
        ),
        _edge(
            "alternate_metric_positive_measure",
            "alternate_metric_projection_free_weights",
            "The positive FS-cube law determines the ambient Hermitian form "
            "and normalization for a residue-to-volume ratio.",
            ("research/experiments/scientific_genesis/alternate_metric_positive_measure.py",),
            ("full-rank equation Jacobian", "independent determinant identity"),
            True,
            ("a tangent-chart cancellation must be proved before using it",),
        ),
        _edge(
            "alternate_metric_weight_moments",
            "alternate_metric_projection_free_weights",
            "Disjoint critical supports establish smoothness of the actual "
            "cover, so the full two-equation conormal Gram is positive there.",
            ("research/experiments/scientific_genesis/ALTERNATE_METRIC_WEIGHT_MOMENTS_NOTE.md",),
            ("actual unchanged cubic pencils", "positive ambient FS form"),
            True,
            ("pointwise positivity is not a computed global lower bound",),
        ),
        _edge(
            "alternate_metric_projection_free_weights",
            "visible_metrics",
            "Projection-free weights can remove critical-fiber tangent "
            "inversions from integration only after certified inputs, "
            "quantitative errors, section throughput, and metric convergence.",
            ("research/experiments/scientific_genesis/"
             "ALTERNATE_METRIC_PROJECTION_FREE_WEIGHTS_NOTE.md",),
            ("controlled independent proposals", "quantitative error bounds",
             "actual section evaluations", "Ricci-flat/HYM convergence"),
            True,
            ("an auxiliary integration weight is not a physical metric",),
        ),
        _edge(
            "alternate_metric_projection_free_weights",
            "alternate_metric_global_weight_bound",
            "The intrinsic positive conormal denominator reduces the global "
            "weight bound to exact lower bounds for homogeneous gradient norms.",
            ("research/experiments/scientific_genesis/"
             "ALTERNATE_METRIC_GLOBAL_WEIGHT_BOUND_NOTE.md",),
            ("quantitative polynomial certificates", "unchanged residue normalization"),
            True,
            ("a loose certified bound may be impractical for integration",),
        ),
        _edge(
            "alternate_metric_weight_moments",
            "alternate_metric_global_weight_bound",
            "The two coprime exact critical supports admit homogeneous Bezout "
            "identities which quantitatively separate small fiber gradients.",
            ("research/experiments/scientific_genesis/alternate_metric_global_weight_bound.py",),
            ("actual homogeneous gradient identities", "exact coefficient norm estimates"),
            True,
            ("coprimality alone supplies no numerical lower bound",),
        ),
        _edge(
            "alternate_metric_global_weight_bound",
            "visible_metrics",
            "An explicit global weight bound can support integration error "
            "control only after independent proposals, certified numeric inputs, "
            "integrand bounds, section throughput, and metric convergence.",
            ("research/experiments/scientific_genesis/"
             "ALTERNATE_METRIC_GLOBAL_WEIGHT_BOUND_NOTE.md",),
            ("correct proposal law", "controlled numeric error", "actual integrand bounds",
             "Ricci-flat/HYM convergence"),
            True,
            ("bounded weights alone do not certify matrix integrands or a metric",),
        ),
        _edge(
            "alternate_metric_bounded_support",
            "alternate_metric_bounded_matrix",
            "Complete ordered execution materializes each original section's "
            "three coefficient enclosures without introducing new physical data.",
            ("research/experiments/scientific_genesis/alternate_metric_bounded_matrix.py",),
            ("all 5345 columns must finish", "complete independent stream validation"),
            True,
            ("a live process, partial stream, or format test does not prove completion",),
        ),
        _edge(
            "alternate_metric_bounded_matrix",
            "visible_metrics",
            "Complete bounded columns supply a local bundle-evaluation input "
            "only after practical multi-point cost, controlled proposals, "
            "integration errors, and Ricci-flat/HYM convergence are established.",
            ("research/experiments/scientific_genesis/alternate_metric_bounded_matrix.py",),
            ("certified complete output", "measured multi-point cost", "SU-uniform proposal law",
             "independent integration errors", "Ricci-flat/HYM convergence"),
            True,
            ("one certified local domain is not global sampling or a Hermitian metric",),
        ),
        _edge(
            "alternate_constituent_carrier_state", "alternate_neutrino_mixed_pairing",
            "The frozen carrier and flat determinant repair determine the "
            "actual matter-character sectors for source-pinned Wilson weights.",
            ("research/experiments/scientific_genesis/alternate_neutrino_mixed_pairing.py",),
            ("unchanged constituent atlases", "actual exact character projections"), True,
            ("character support alone gives no coupling value",),
        ),
        _edge(
            "alternate_up_mixed_quotient_pairing", "alternate_neutrino_mixed_pairing",
            "The same canonical quotient product and up-Higgs trace evaluate "
            "different matter characters without transferring up-sector values.",
            ("research/experiments/scientific_genesis/alternate_neutrino_mixed_pairing.py",),
            ("same Higgs covector", "fresh actual neutrino matter representatives"), True,
            ("gauge unification does not supply a family-basis identification",),
        ),
        _edge(
            "alternate_neutrino_mixed_pairing", "alternate_neutrino_matrix",
            "Four constant mixed entries provide only the off-block input "
            "to the full parameter-linear matrix.",
            ("research/experiments/scientific_genesis/alternate_neutrino_mixed_pairing.py",),
            ("actual F-F matter corrections", "complete eight coefficient scalars"), True,
            ("absent entries must not be filled with zero or up-sector values",),
        ),
        _edge(
            "alternate_neutrino_matrix", "physical_yukawas",
            "A derived holomorphic neutrino matrix is one required sector "
            "before physical normalization in a common stabilized vacuum.",
            ("research/experiments/scientific_genesis/alternate_neutrino_mixed_pairing.py",),
            ("other flavor sectors", "canonical metrics", "stabilized common vacuum"), True,
            ("a Dirac coupling is not a Majorana mechanism or physical mass",),
        ),
        _edge(
            "alternate_neutrino_mixed_pairing", "alternate_neutrino_matter_lifts",
            "The actual sector-specific constituent representatives admit "
            "full corrections for both universal outer coefficients.",
            ("research/experiments/scientific_genesis/alternate_neutrino_ff_entries.py",
             "research/experiments/scientific_genesis/alternate_neutrino_full_matrix.py"),
            ("original full differentials", "same literal quotient pushout"), True,
            ("a reduced preimage without a verified full equation is insufficient",),
        ),
        _edge(
            "alternate_neutrino_matter_lifts", "alternate_neutrino_matrix",
            "Eight verified actual matter lifts supply the inputs to the "
            "remaining complete coupled F-F product and scalar calculations.",
            ("research/experiments/scientific_genesis/alternate_neutrino_full_matrix.py",),
            ("actual full Higgs cocycle", "complete direct and transferred scalar traces"), True,
            ("a matter lift alone does not determine a Yukawa coefficient",),
        ),
        _edge(
            "alternate_constituent_carrier_state", "alternate_down_higgs_hom_representative",
            "The repaired Hom representation and unchanged common twist route "
            "the published down-Higgs weight to its unique native character.",
            ("research/experiments/scientific_genesis/alternate_up_higgs_hom_representative.py",),
            ("actual alternate I6 ray (0,1)", "fixed common flat twist (1,2)"), True,
            ("a character in a spectrum is not a generated chain representative",),
        ),
        _edge(
            "alternate_down_higgs_hom_representative", "physical_yukawas",
            "A strict down-Higgs class is one prerequisite for both remaining "
            "holomorphic down-quark and charged-lepton matrices on this carrier.",
            ("research/experiments/scientific_genesis/alternate_up_higgs_hom_representative.py",),
            ("actual exterior Higgs realization", "same-carrier matter classes",
             "all entries", "canonical metrics", "common vacuum"), True,
            ("a Hom class alone cannot supply either matrix or a physical mass",),
        ),
        _edge(
            "alternate_down_higgs_hom_representative", "alternate_down_higgs_quotient_cone",
            "A-supported Hom data factors through the actual ideal quotient; "
            "full exterior primitives solve its two coefficientwise cone equations.",
            ("research/experiments/scientific_genesis/alternate_up_higgs_quotient_cone.py",
             "research/experiments/scientific_genesis/alternate_up_exterior_higgs_action.py"),
            ("actual down-Higgs witness", "same signed quotient maps and outer basis"), True,
            ("the actual down action may be nonboundary even when the up action is exact",),
        ),
        _edge(
            "alternate_down_higgs_quotient_cone", "physical_yukawas",
            "One actual down-Higgs cocycle is shared by the remaining down and "
            "charged-lepton scalar calculations, not by their matter bases.",
            ("research/experiments/scientific_genesis/alternate_up_higgs_quotient_cone.py",),
            ("actual sector-specific matter products", "all entries", "metrics", "common vacuum"),
            True, ("a Higgs cocycle alone does not determine any Yukawa scalar",),
        ),
        _edge(
            "alternate_constituent_carrier_state", "alternate_down_lepton_matter",
            "Source Wilson weights and the fixed twist determine two new "
            "constituent character sectors in the original carrier complexes.",
            ("research/experiments/scientific_genesis/"
             "alternate_constituent_up_matter_representatives.py",),
            ("original reduced bases", "full strict deck projections"), True,
            ("character support does not construct a representative",),
        ),
        _edge(
            "alternate_down_lepton_matter", "physical_yukawas",
            "Actual d^c and e^c classes complement the already archived Q "
            "and L inputs for the remaining down-Higgs flavor products.",
            ("research/experiments/scientific_genesis/"
             "alternate_constituent_up_matter_representatives.py",),
            ("full cone matter lifts", "actual down-Higgs cocycle", "all scalar entries",
             "canonical metrics", "common vacuum"), True,
            ("neither a constituent class nor a gauge weight supplies a coupling",),
        ),
        _edge(
            "alternate_down_lepton_matter", "alternate_remaining_flavor_matter_lifts",
            "The actual universal outer class composes with each new d^c/e^c "
            "cycle; a strict full primitive gives its coefficient correction.",
            ("research/experiments/scientific_genesis/"
             "alternate_constituent_up_cone_matter_lifts.py",),
            ("full original differential", "fixed universal outer basis"), True,
            ("uncorrected constituent cycles are not full carrier states",),
        ),
        _edge(
            "alternate_remaining_flavor_matter_lifts", "physical_yukawas",
            "The actual new d^c/e^c corrections supply only the missing sides "
            "of down and charged-lepton products with the archived Q/L states.",
            ("research/experiments/scientific_genesis/alternate_up_ff_entries.py",),
            ("existing Q/L lifts", "verified down-Higgs cocycle", "complete scalar entries",
             "canonical metrics", "common stabilized vacuum"), True,
            ("corrected matter alone does not supply a scalar or a physical Yukawa",),
        ),
        *tuple(_edge(
            source, "alternate_down_lepton_mixed_pairing",
            reason,
            ("research/experiments/scientific_genesis/alternate_down_lepton_mixed_pairing.py",),
            ("actual original E/F witnesses", "fixed quotient and Higgs-first order"), True,
            ("character routing or a shared Higgs object does not supply a scalar value",),
        ) for source, reason in (
            ("alternate_down_lepton_matter", "Actual d/e classes pair with distinct archived Q/L "
             "classes; their B-F quotient products are computed, not relabelled."),
            ("alternate_down_higgs_quotient_cone", "The actual down covector evaluates the "
             "constant mixed products in both sectors with the fixed volume frame."),
        )),
        *tuple(_edge(
            source, "alternate_down_lepton_matrices",
            reason,
            ("research/experiments/scientific_genesis/alternate_up_ff_entries.py",
             "research/experiments/scientific_genesis/alternate_down_lepton_ff_entries.py"),
            ("actual full matter/Higgs inputs", "all entries and independent full scalar replay"),
            True, ("partial blocks cannot be presented as a complete matrix",),
        ) for source, reason in (
            ("alternate_down_lepton_mixed_pairing", "Eight verified constant mixed entries "
             "supply the non-F-F parts of the two actual matrices."),
            ("alternate_remaining_flavor_matter_lifts", "Eight actual d/e corrections combine "
             "with existing Q/L lifts for sixteen formal F-F scalar coefficients."),
            ("alternate_down_higgs_quotient_cone", "The actual down-Higgs constant and linear "
             "coefficients evaluate complete coupled products, without up primitives."),
        )),
        _edge(
            "alternate_down_lepton_matrices", "physical_yukawas",
            "Complete holomorphic down and charged-lepton matrices supply two "
            "missing sectors, but do not replace their metrics or stabilized parameters.",
            ("src/onetheory/physics/observables.py",),
            ("controlled matter/Higgs metrics", "one stabilized common vacuum"), True,
            ("holomorphic scalar ranks alone do not predict physical masses or mixing",),
        ),
        _edge(
            "computable_carrier_state",
            "common_dga_package",
            "The frozen P1 component determines a universal parameter-dependent "
            "carrier complex on which common products must be constructed.",
            (
                "data/generated/scientific_genesis/"
                "computable_one_theory_carrier_state.json",
                "src/onetheory/math/homological.py",
            ),
            (),
            True,
            ("full matter/Higgs lifts or required pairings may be unavailable",),
        ),
        _edge(
            "strict_mixed_matter_representatives",
            "universal_matter_sector_lifts",
            "Signed full-Schoen composition and exact boundary contraction turn "
            "the strict V2 character classes into parameter-linear cocycles of "
            "the universal visible cone.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_universal_matter_lifts.json",
            ),
            (
                "published Wilson character assignment for the up-type sector",
            ),
            True,
            ("only the minimum two physical matter sectors are lifted",),
        ),
        _edge(
            "computable_carrier_state",
            "higgs_determinant_twist_route",
            "The frozen lawful constituent complexes and exact determinant "
            "degrees determine a synchronized outer-Hom transfer whose "
            "cohomology and deck action can be derived independently.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_higgs_twist_audit.json",
            ),
            (
                "rank-two determinant identity",
                "det(V2) = det(V1)^-1",
            ),
            True,
            (
                "the Hom realization lacks an equivariant chain comparison "
                "with the physical tensor",
            ),
        ),
        _edge(
            "universal_matter_sector_lifts",
            "common_dga_package",
            "The universal matter cocycles provide both three-dimensional "
            "external matter bases required by the first up-type product.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_universal_matter_lifts.json",
            ),
            (),
            False,
            (
                "the product hull and cyclic trace are not yet certified",
            ),
        ),
        _edge(
            "higgs_determinant_twist_route",
            "common_dga_package",
            "A lawful equivariant tensor comparison would turn one transferred "
            "class into the required full-Schoen Higgs input.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_higgs_twist_audit.json",
            ),
            (),
            False,
            (
                "no raw Hom character may be selected as a physical tensor class",
                "no uniform scalar character repairs the exact mismatch",
            ),
        ),
        _edge(
            "computable_carrier_state",
            "higgs_direct_tensor_diagonal",
            "The two frozen lawful constituent complexes tensor on independent "
            "covers, after which the fiber diagonal is imposed by its exact "
            "Koszul equation.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_chain_diagonal.json",
            ),
            (),
            True,
            (
                "shared-cover flattening before tensoring destroys strict closure",
                "the transferred Higgs cohomology remains uncomputed",
            ),
        ),
        _edge(
            "higgs_direct_tensor_diagonal",
            "strict_mixed_higgs_representative",
            "Exact P/T projectors select the source-required character sector; "
            "homological perturbation transfers its two maps and lifts the "
            "unique H1 class to the full square-zero chain diagonal.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_chain_actions.json",
            ),
            (
                "published Wilson character assignment for the up-type sector",
            ),
            True,
            (
                "only the source-required character sector is transferred",
            ),
        ),
        _edge(
            "strict_mixed_higgs_representative",
            "common_dga_package",
            "The strict full-Schoen Higgs cocycle supplies the third chain input "
            "required beside the two universal matter sectors.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_chain_actions.json",
            ),
            (),
            True,
            (
                "the first nontrivial higher product remains unresolved",
            ),
        ),
        _edge(
            "strict_mixed_higgs_representative",
            "mixed_matter_tensor_comparison",
            "The strict Higgs cocycle fixes the grouped four-factor target in "
            "which candidate matter products must be exact cycles.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_matter_tensor_audit.json",
            ),
            (),
            True,
            (
                "the canonical signed direct tensor is not closed",
            ),
        ),
        _edge(
            "mixed_matter_tensor_comparison",
            "common_dga_package",
            "Finite HPL comparison and exact character projection place all four "
            "matter products in the grouped Higgs chain model before determinant "
            "pairing and tracing.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_matter_comparison.json",
            ),
            (),
            True,
            (
                "the tree products are exact boundaries",
                "the first nontrivial higher product remains unresolved",
            ),
        ),
        _edge(
            "mixed_scalar_trace_target",
            "common_dga_package",
            "Virtual determinant cancellation and complete-intersection "
            "adjunction identify the unique reduced scalar residue coordinate "
            "used by the alternating chain contraction.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_scalar_trace.json",
            ),
            (),
            True,
            (),
        ),
        _edge(
            "mixed_local_determinant_pairings",
            "common_dga_package",
            "Complementary-minor forms give exact constituent determinant "
            "pairings compatible with every hypersurface-corrected overlap and "
            "supply the local inputs to the grouped chain totalization.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_determinant_pairing.json",
            ),
            (),
            True,
            (),
        ),
        _edge(
            "mixed_matter_tensor_comparison",
            "mixed_tree_up_matrix",
            "The four exact equivariant matter products are the only "
            "character-allowed matrix entries presented for scalar contraction.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_matter_comparison.json",
            ),
            (),
            True,
            (),
        ),
        _edge(
            "mixed_scalar_trace_target",
            "mixed_tree_up_matrix",
            "Adjunction fixes the normalized one-dimensional scalar residue "
            "coordinate used to evaluate every allowed entry.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_scalar_trace.json",
            ),
            (),
            True,
            (),
        ),
        _edge(
            "mixed_local_determinant_pairings",
            "mixed_tree_up_matrix",
            "The certified complementary-minor forms determine the alternating "
            "constituent contraction in the grouped total complex.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_determinant_pairing.json",
            ),
            (),
            True,
            (),
        ),
        _edge(
            "mixed_tree_up_matrix",
            "first_exact_yukawa",
            "The exact rank-zero tree matrix fixes the baseline that a lawful "
            "deformation or higher product must escape.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_yukawa_trace.json",
            ),
            (),
            False,
            (
                "no nonzero deformation or higher-product contribution exists",
            ),
        ),
        _edge(
            "mixed_tree_up_matrix",
            "mixed_diagonal_local_comparison",
            "The exact rank-zero tree result requires the first lawful "
            "parameter-linear matter correction to be evaluated.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_yukawa_trace.json",
            ),
            (),
            True,
            (),
        ),
        _edge(
            "universal_matter_sector_lifts",
            "mixed_diagonal_local_comparison",
            "The universal V2 lifts supply common-Schoen V1 correction "
            "cochains that must be compared with the independent-fiber tensor.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_universal_matter_lifts.json",
            ),
            (),
            True,
            (),
        ),
        _edge(
            "mixed_diagonal_local_comparison",
            "mixed_diagonal_chain_map",
            "The two chartwise pencil identities and their overlap syzygy "
            "supply the exact local coefficients for the Cech chain map.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_diagonal_comparison.json",
            ),
            (),
            True,
            (),
        ),
        _edge(
            "universal_matter_sector_lifts",
            "mixed_diagonal_chain_map",
            "The full universal correction cochains fix the source grading "
            "and support on which the local comparison must act.",
            (
                "research/experiments/scientific_genesis/"
                "mixed_schoen_diagonal_chain_map.py",
            ),
            (),
            True,
            (),
        ),
        _edge(
            "mixed_diagonal_chain_map",
            "mixed_matter_leg_deformation",
            "Exact totalization signs and overlap homotopies carry common "
            "matter corrections into the grouped four-factor complex where "
            "the first ordered deformation terms can be multiplied.",
            (
                "research/experiments/scientific_genesis/"
                "mixed_schoen_diagonal_chain_map.py",
                "data/generated/scientific_genesis/"
                "mixed_schoen_matter_leg_deformation.json",
            ),
            (),
            True,
            (
                "the transferred matter leg is not closed by itself",
            ),
        ),
        _edge(
            "strict_mixed_higgs_representative",
            "mixed_higgs_leg_deformation",
            "The strict A1-tensor-A2 Higgs and universal a0 extension determine "
            "an exact determinant-line action and its boundary correction.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_higgs_leg_deformation.json",
            ),
            (),
            True,
            (
                "the determinant line retains an explicit diagonal p-minus-q twist",
            ),
        ),
        _edge(
            "mixed_matter_leg_deformation",
            "common_dga_package",
            "The exact noncycle residual identifies the terms that a complete "
            "first-order higher product must cancel rather than hiding them in "
            "a scalar residue.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_matter_leg_deformation.json",
            ),
            (),
            True,
            (
                "the scoped zero residue is not a Yukawa coefficient",
            ),
        ),
        _edge(
            "mixed_higgs_leg_deformation",
            "common_dga_package",
            "The exact Higgs correction supplies the complementary extension "
            "leg required by the first-order higher-product identity.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_higgs_leg_deformation.json",
            ),
            (),
            True,
            (
                "direct cochain equality fails and requires the certified "
                "fixed-contraction comparison primitive",
            ),
        ),
        _edge(
            "strict_mixed_matter_representatives",
            "mixed_v2_pluecker_chain_map",
            "The strict V2 character classes provide the actual source support "
            "for the full local determinant pairing and exchange certificate.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_v2_pluecker_chain_map.json",
            ),
            (),
            True,
            (),
        ),
        _edge(
            "mixed_v2_pluecker_chain_map",
            "common_dga_package",
            "The strict bottom determinant pairing supplies the complementary "
            "line-valued factor required by the Higgs correction.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_v2_pluecker_chain_map.json",
            ),
            (),
            True,
            (
                "its direct Higgs-action product is not cochain-equal to the "
                "grouped matter-leg residual; the fixed contraction supplies "
                "the required input-level primitive",
            ),
        ),
        _edge(
            "mixed_matter_leg_deformation",
            "mixed_first_higher_product_coefficient",
            "The exact nonclosed matter scalar fixes one side of the uniquely "
            "signed grouped-to-Pluecker comparison residual.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_first_higher_product.json",
            ),
            (),
            True,
            (),
        ),
        _edge(
            "mixed_higgs_leg_deformation",
            "mixed_first_higher_product_coefficient",
            "The strict determinant-line correction supplies the complementary "
            "first-order Higgs leg and its exact boundary identity.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_first_higher_product.json",
            ),
            (),
            True,
            (),
        ),
        _edge(
            "mixed_v2_pluecker_chain_map",
            "mixed_first_higher_product_coefficient",
            "The equivariant V2 determinant class pairs with the Higgs "
            "correction in the common scalar target.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_first_higher_product.json",
            ),
            (),
            True,
            (),
        ),
        _edge(
            "mixed_first_higher_product_coefficient",
            "mixed_first_order_up_matrix",
            "The complete a0 lower-(1,1) residue anchors the indexed exact "
            "pipeline used for every first-order coefficient.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_first_order_matrix.json",
            ),
            (),
            True,
            (),
        ),
        _edge(
            "mixed_first_order_up_matrix",
            "mixed_up_yukawa_no_go",
            "The complete first-order zero supplies the last coefficient set "
            "allowed by the finite exterior-filtration ledger.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_up_yukawa_no_go.json",
            ),
            (),
            True,
            (),
        ),
        _edge(
            "mixed_up_yukawa_no_go",
            "mixed_flavor_character_support",
            "The branch theorem excludes the up-type sector before exact "
            "published characters rank the remaining flavor workloads.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_flavor_character_support.json",
            ),
            (),
            True,
            (
                "the theorem is scoped to the selected up-type characters",
            ),
        ),
        _edge(
            "mixed_flavor_character_support",
            "mixed_down_higgs_chain_obstruction",
            "The minimum down workload requires character (0,2), whose exact "
            "current-chain cohomology must exist before any matrix calculation.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_down_higgs_action.json",
            ),
            (),
            True,
            (
                "an exact alternative equivariant chain action could reopen down",
            ),
        ),
        _edge(
            "mixed_down_higgs_chain_obstruction",
            "mixed_flavor_frontier",
            "The unavailable down prerequisite removes that sector from the "
            "current exact chain frontier.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_flavor_frontier.json",
            ),
            (),
            True,
            (),
        ),
        _edge(
            "mixed_down_higgs_chain_obstruction",
            "mixed_higgs_equivariant_comparison_obstruction",
            "The zero current-chain H_d sector is compared with the exact "
            "source-derived P1 isotypic multiplicity to test whether an "
            "equivariant quasi-isomorphism can exist.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_higgs_equivariant_obstruction.json",
            ),
            (),
            True,
            (),
        ),
        _edge(
            "mixed_flavor_frontier",
            "universal_neutrino_matter_lifts",
            "The selected Dirac-neutrino sector requires exact universal "
            "matter classes in characters (0,0) and (0,2).",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_neutrino_matter_lifts.json",
            ),
            (),
            True,
            (),
        ),
        _edge(
            "universal_neutrino_matter_lifts",
            "mixed_neutrino_tree_matrix",
            "The two complete matter bases pair with the reused strict Higgs "
            "class through the exact determinant trace.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_neutrino_tree_matrix.json",
            ),
            (),
            True,
            (
                "the associated-graded trace need not include universal corrections",
            ),
        ),
        _edge(
            "mixed_neutrino_tree_matrix",
            "mixed_neutrino_first_order_matrix",
            "The exact tree-level zero fixes the baseline for all eight "
            "independent universal parameter corrections.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_neutrino_first_order_matrix.json",
            ),
            (),
            True,
            (),
        ),
        _edge(
            "mixed_neutrino_first_order_matrix",
            "mixed_charged_lepton_convention",
            "The complete exact forward-sector matrix is relabelled only after "
            "source-action inversion withdraws its Dirac-neutrino assignment.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_charged_lepton_convention.json",
            ),
            (),
            True,
            (),
        ),
        _edge(
            "mixed_character_convention_correction",
            "mixed_charged_lepton_convention",
            "Inverse forward pullback sends physical charged-lepton source "
            "characters to the certified forward matter and H_d sectors.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_charged_lepton_convention.json",
            ),
            (),
            True,
            (),
        ),
        _edge(
            "mixed_higgs_equivariant_comparison_obstruction",
            "mixed_higgs_scalar_action_no_go",
            "The unique remaining frame discrepancy is tested first by the "
            "isolated line replacement and then by its connected uniform "
            "scalar propagation.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_higgs_scalar_action_no_go.json",
            ),
            (),
            True,
            (),
        ),
        _edge(
            "mixed_higgs_scalar_action_no_go",
            "mixed_higgs_full_character_audit",
            "Both scalar trials motivate deriving the complete current H1 "
            "representation before attempting a larger local comparison.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_higgs_character_audit.json",
            ),
            (),
            True,
            (),
        ),
        _edge(
            "mixed_higgs_full_character_audit",
            "mixed_higgs_linearization_no_go",
            "The exhausted uniform character shifts become a no-go for all "
            "same-constituent relinearizations once exact self-Hom ranks prove "
            "that both factors are simple.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_higgs_linearization_no_go.json",
            ),
            (),
            True,
            (),
        ),
        _edge(
            "mixed_higgs_linearization_no_go",
            "mixed_atlas_higgs_character_incompatibility",
            "The normalized full-chain frame ratios identify atlas characters on "
            "both simple factors, so their product acts as a forced shift on "
            "the complete synchronized Higgs representation.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_atlas_higgs_characters.json",
            ),
            (),
            True,
            (),
        ),
        _edge(
            "selected_atlas_common_frame_comparison",
            "mixed_atlas_higgs_character_incompatibility",
            "The homogeneous-lift-normalized constituent ratios, not raw "
            "line entries, determine the tensor cohomology character shift.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_atlas_higgs_characters.json",
            ),
            (),
            True,
            ("the selected source pushdown labels are a separate claim",),
        ),
        _edge(
            "mixed_higgs_linearization_no_go",
            "same_constituent_wilson_shift_no_go",
            "Simplicity restricts every factorwise linearization to a "
            "character shift of the exact tensor-Higgs representation.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_wilson_shift_no_go.json",
            ),
            ("fixed published Wilson embedding",),
            True,
            ("distinct underlying constituents are outside this theorem",),
        ),
        _edge(
            "mixed_atlas_higgs_character_incompatibility",
            "same_constituent_wilson_shift_no_go",
            "The corrected atlas shift is one of the nine factorwise tensor "
            "characters screened by the two-doublet support proof.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_wilson_shift_no_go.json",
            ),
            (),
            True,
            ("changing the underlying pair changes the tensor support",),
        ),
        _edge(
            "selected_constituent_determinant_acyclicity",
            "same_constituent_wilson_shift_no_go",
            "Acyclic determinant endpoints make exterior-square H1 equal "
            "tensor H1 in either nonsplit extension orientation, independent "
            "of extension coordinates.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_wilson_shift_no_go.json",
            ),
            ("same selected underlying constituent pair",),
            True,
            ("its older source-derived Higgs characters are not used",),
        ),
        _edge(
            "mixed_atlas_higgs_character_incompatibility",
            "mixed_character_convention_correction",
            "The apparent atlas/source mismatch requires both actions to be "
            "placed in the same pullback convention before any line character "
            "or physical sector can be compared.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_character_convention.json",
            ),
            (),
            True,
            (),
        ),
        _edge(
            "mixed_character_convention_correction",
            "universal_down_matter_lifts",
            "Exact source-to-forward inversion selects the only admissible "
            "chain sectors for the physical down-matter representatives.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_down_matter_lifts.json",
            ),
            (),
            True,
            (),
        ),
        _edge(
            "universal_down_matter_lifts",
            "mixed_down_tree_matrix",
            "The convention-corrected H_d and down-matter bases determine all "
            "four character-allowed associated-graded contractions.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_down_tree_matrix.json",
            ),
            (),
            True,
            (),
        ),
        _edge(
            "mixed_down_tree_matrix",
            "mixed_down_first_order_matrix",
            "The exact rank-zero tree matrix and all eight exterior-allowed "
            "universal coefficients determine the complete down matrix.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_down_first_order_matrix.json",
            ),
            (),
            True,
            (),
        ),
        _edge(
            "mixed_down_first_order_matrix",
            "first_exact_yukawa",
            "The physical down matrix vanishes at every exterior-allowed "
            "order, so a first nontrivial matrix must use another lawful "
            "physical sector or an exact replacement carrier realization.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_down_first_order_matrix.json",
            ),
            (),
            False,
            ("the reference-carrier branch alone cannot provide it",),
        ),
        _edge(
            "mixed_charged_lepton_convention",
            "first_exact_yukawa",
            "The last available physical flavor matrix on the frozen carrier "
            "vanishes through every exterior-allowed order, so a nontrivial "
            "matrix requires an exact replacement realization.",
            (
                "data/generated/scientific_genesis/"
                "mixed_schoen_charged_lepton_convention.json",
            ),
            (),
            False,
            ("the reference-carrier branch alone cannot provide it",),
        ),
        _edge(
            "common_dga_package",
            "first_exact_yukawa",
            "A nontrivial lawful deformation or higher product followed by the "
            "exact trace would yield a carrier-derived holomorphic matrix.",
            ("src/onetheory/models/heterotic_schoen/flavor.py",),
            (),
            False,
            ("the required nonzero higher product is not yet derived",),
        ),
        _edge(
            "tree_holomorphic_flavor",
            "first_exact_yukawa",
            "The published texture constrains the expected tree-level "
            "structure but is not chain input.",
            ("src/onetheory/models/heterotic_schoen/flavor.py",),
            ("reference-carrier comparison only",),
            False,
            ("computable carrier may realize a different texture",),
        ),
        _edge(
            "alternate_constituent_carrier_state",
            "alternate_metric_generation_reduction",
            "The frozen alternate cone supplies the descended locally free "
            "short exact extension sequence to which the criterion applies.",
            (
                "data/generated/scientific_genesis/alternate_constituent_carrier_state.json",
                "research/experiments/scientific_genesis/"
                "ALTERNATE_METRIC_GENERATION_REDUCTION_NOTE.md",
            ),
            ("selected heterotic realization", "non-split alternate P1"),
            True,
            ("the published reference extension is not this alternate cone",),
        ),
        _edge(
            "alternate_metric_generation_reduction",
            "visible_metrics",
            "Surjective section lifts and fiberwise exactness reduce rank-four "
            "global generation to two constituent evaluations and one H1 vanishing.",
            (
                "research/experiments/scientific_genesis/"
                "ALTERNATE_METRIC_GENERATION_REDUCTION_NOTE.md",
            ),
            ("declared descending positive twist", "quotient-level section certificates"),
            True,
            ("a failed premise leaves direct evaluation or another twist necessary",),
        ),
        _edge(
            "alternate_metric_subbundle_vanishing",
            "visible_metrics",
            "The quotient H1 obstruction to lifting V2(H) sections through "
            "the rank-four extension vanishes at the declared twist.",
            (
                "data/generated/scientific_genesis/alternate_metric_subbundle_vanishing.json",
                "research/experiments/scientific_genesis/"
                "ALTERNATE_METRIC_SUBBUNDLE_VANISHING_NOTE.md",
            ),
            ("same descended twist on both constituents",),
            True,
            ("quotient generation at the smaller trial twist is unproved",),
        ),
        _edge(
            "computable_carrier_state",
            "visible_metrics",
            "Metric construction needs the explicit carrier and extension cocycles.",
            ("research/experiments/visible_metrics/audit.py",),
            (),
            True,
            ("explicit invariant bases or numerical convergence may fail",),
        ),
        _edge(
            "first_exact_yukawa",
            "physical_yukawas",
            "Canonical normalization acts on holomorphic matrices.",
            ("src/onetheory/physics/observables.py",),
            (),
            True,
            ("free moduli prevent prediction",),
        ),
        _edge(
            "visible_metrics",
            "physical_yukawas",
            "Positive matter and Higgs metrics are required for canonical normalization.",
            ("src/onetheory/physics/observables.py",),
            (),
            True,
            ("metric approximation may not converge",),
        ),
        _edge(
            "computable_carrier_state",
            "physical_pfaffians",
            "The visible restriction determines physical instanton maps.",
            ("research/experiments/conic_pfaffians/audit.py",),
            (),
            True,
            ("Pfaffians may cancel or vanish",),
        ),
        _edge(
            "computable_carrier_state",
            "hidden_bundle",
            "Visible Chern data fixes the hidden anomaly target.",
            ("src/onetheory/models/heterotic_schoen/consistency.py",),
            (),
            True,
            ("compatible hidden bundle may not exist",),
        ),
        *[
            _edge(
                source,
                "alternate_necessary_hidden_chamber",
                reason,
                ("research/experiments/scientific_genesis/"
                 "ALTERNATE_NECESSARY_HIDDEN_CHAMBER_NOTE.md",),
                ("no-five-brane c1=0 Kahler HYM branch",),
                True,
                ("changed rational Chern target or extra Bianchi sources",),
            )
            for source, reason in (
                ("alternate_constituent_outer_universal_cone",
                 "The actual cone fixes the parameter-independent rational residual c2."),
                ("alternate_constituent_outer_stability_locus",
                 "The nine sufficient slope bounds define the visible stable chamber."),
            )
        ],
        *[
            _edge(
                "alternate_necessary_hidden_chamber",
                target,
                "A compatible hidden HYM bundle and common vacuum must lie "
                "inside the necessary wall; positivity is not an existence proof.",
                ("research/experiments/scientific_genesis/"
                 "alternate_necessary_hidden_chamber.py",),
                ("same frozen alternate carrier", "no additional Bianchi sources"),
                True,
                ("hidden maps, descent, full stability, or stabilization may fail",),
            )
            for target in ("hidden_bundle", "controlled_vacuum")
        ],
        _edge(
            "physical_pfaffians",
            "controlled_vacuum",
            "Worldsheet terms contribute to the carrier-specific superpotential.",
            ("src/onetheory/models/heterotic_schoen/vacuum.py",),
            (),
            True,
            ("normalization or cancellation may obstruct stabilization",),
        ),
        _edge(
            "hidden_bundle",
            "controlled_vacuum",
            "Hidden dynamics and anomaly cancellation constrain the common vacuum.",
            ("src/onetheory/models/heterotic_schoen/vacuum.py",),
            (),
            True,
            ("no shared stable chamber", "no supersymmetric critical point"),
        ),
        _edge(
            "controlled_vacuum",
            "physical_yukawas",
            "A numerical physical Yukawa requires fixed moduli and one compatible context.",
            ("src/onetheory/reality.py",),
            (),
            True,
            ("vacuum may leave flat directions",),
        ),
        _edge(
            "physical_yukawas",
            "low_energy_predictions",
            "Threshold matching and RGE evolution map high-scale matrices to observables.",
            ("src/onetheory/physics/observables.py",),
            (),
            True,
            ("missing thresholds", "uncontrolled uncertainty"),
        ),
        _edge(
            "controlled_vacuum",
            "low_energy_predictions",
            "All high-scale parameters must belong to the same stabilized state.",
            ("src/onetheory/reality.py",),
            (),
            True,
            ("incompatible contexts",),
        ),
        _edge(
            "measured_observables",
            "low_energy_predictions",
            "Held-out data test predictions only after the protocol is frozen.",
            ("src/onetheory/physics/observables.py",),
            ("no data leakage",),
            True,
            ("selection or fitting would invalidate prediction status",),
        ),
    ]


def _engines() -> list[dict[str, object]]:
    """Inventory reusable machinery and its actual maturity."""

    entries = (
        ("Schoen geometry", "established", ("src/onetheory/models/heterotic_schoen/geometry.py",)),
        (
            "Cox and affine-chart algebra",
            "established",
            ("src/onetheory/math/sections.py", "src/onetheory/math/sheaves.py"),
        ),
        (
            "Hilbert-Burch resolutions",
            "established and carrier prototypes",
            (
                "src/onetheory/models/heterotic_schoen/visible.py",
                "research/experiments/computable_carrier/serre_pushout.py",
            ),
        ),
        (
            "Serre constructions",
            "research prototype",
            (
                "research/experiments/computable_carrier/global_serre.py",
                "research/experiments/computable_carrier/serre_pushout.py",
                "research/experiments/scientific_genesis/"
                "local_constituent_frames.py",
            ),
        ),
        ("Cech complexes", "established generic engine", ("src/onetheory/math/cech.py",)),
        (
            "Koszul totalizations",
            "research exact engine",
            ("research/experiments/computable_carrier/schoen_outer.py",),
        ),
        (
            "hypercohomology",
            "research exact engine",
            ("research/experiments/computable_carrier/projective_hyperhom.py",),
        ),
        (
            "derived Hom and Ext",
            "research exact engine",
            ("research/experiments/computable_carrier/schoen_sparse_outer.py",),
        ),
        (
            "exact group actions",
            "established generic plus research specialization",
            (
                "src/onetheory/math/homological.py",
                "research/experiments/computable_carrier/schoen_sparse_actions.py",
            ),
        ),
        (
            "invariant projectors and quotient representatives",
            "established generic plus research specialization",
            (
                "src/onetheory/math/homological.py",
                "research/experiments/computable_carrier/schoen_sparse_outer_actions.py",
            ),
        ),
        (
            "mapping cones and horseshoes",
            "established generic plus research prototype",
            (
                "src/onetheory/math/homological.py",
                "src/onetheory/math/polynomials.py",
                "research/experiments/computable_carrier/horseshoe.py",
            ),
        ),
        (
            "Fitting and determinantal ideals",
            "established exact engine",
            ("src/onetheory/math/polynomials.py",),
        ),
        (
            "Chern arithmetic",
            "established generic plus research specialization",
            (
                "src/onetheory/math/geometry.py",
                "research/experiments/computable_carrier/tier_b_monomial_topology.py",
            ),
        ),
        (
            "stability",
            "published reference implementation; computable-family chamber absent",
            (
                "src/onetheory/models/heterotic_schoen/visible.py",
                "src/onetheory/physics/compactification.py",
            ),
        ),
        (
            "Wilson projection",
            "established generic and reference metadata",
            (
                "src/onetheory/physics/compactification.py",
                "src/onetheory/models/heterotic_schoen/visible.py",
            ),
        ),
        (
            "matter and Higgs cohomology",
            "exact dimensions and relative representatives; full Schoen lifts absent",
            (
                "src/onetheory/models/heterotic_schoen/visible.py",
                "research/experiments/scientific_genesis/"
                "relative_constituent_pushdowns.py",
                "research/experiments/scientific_genesis/"
                "published_higgs_cohomology.py",
            ),
        ),
        (
            "common DGA",
            "established generic engine; physical package blocked",
            (
                "src/onetheory/math/homological.py",
                "research/experiments/visible_common_dga/audit.py",
            ),
        ),
        (
            "deformation theory",
            "established reference formal frontier",
            (
                "src/onetheory/models/heterotic_schoen/visible.py",
                "src/onetheory/models/heterotic_schoen/flavor.py",
            ),
        ),
        (
            "higher products and HPL",
            "established generic engine; carrier inputs blocked",
            (
                "src/onetheory/math/homological.py",
                "src/onetheory/models/heterotic_schoen/flavor.py",
            ),
        ),
        (
            "mixed graded exterior squares and reciprocal covector products",
            "research-only; coupled quotient product derived and actual presentation checked",
            (
                "research/experiments/scientific_genesis/mixed_schoen_exterior_square.py",
                "research/experiments/scientific_genesis/alternate_up_exterior_higgs_action.py",
                "research/experiments/scientific_genesis/mixed_schoen_cup_homotopy.py",
                "research/experiments/scientific_genesis/alternate_up_exterior_boundary_attack.py",
                "research/experiments/scientific_genesis/mixed_schoen_rank_one_tensor.py",
                "research/experiments/scientific_genesis/alternate_up_syzygy_tensor_comparison.py",
                "research/experiments/scientific_genesis/mixed_schoen_cup_coherence.py",
                "research/experiments/scientific_genesis/mixed_schoen_coupled_tensor.py",
                "research/experiments/scientific_genesis/alternate_up_coupled_tensor_comparison.py",
            ),
        ),
        (
            "alternate coherent Higgs quotient cone and ordered null scalars",
            "research-only; actual quotient maps and scalar closure, not physical normalization",
            (
                "research/experiments/scientific_genesis/alternate_up_higgs_quotient_cone.py",
                "research/experiments/scientific_genesis/alternate_up_first_order_scalar.py",
                "research/experiments/scientific_genesis/alternate_up_higgs_covector_comparison.py",
                "research/experiments/scientific_genesis/alternate_up_quotient_equivariance.py",
                "research/experiments/scientific_genesis/alternate_up_pairing_exchange.py",
                "research/experiments/scientific_genesis/alternate_up_null_line_homotopies.py",
                "research/experiments/scientific_genesis/mixed_schoen_common_dga.py",
            ),
        ),
        (
            "natural quotient null-channel scalar evaluation",
            "research-only evaluator; complete actual coefficient execution pending",
            (
                "research/experiments/scientific_genesis/alternate_up_coupled_null_scalar.py",
                "research/experiments/scientific_genesis/ALTERNATE_UP_NATURAL_NULL_SCALAR_NOTE.md",
                "tests/integration/test_scientific_genesis_quotient_evaluation.py",
            ),
        ),
        (
            "metrics",
            "generic numerical laws and carrier boundary only",
            (
                "src/onetheory/models/heterotic_schoen/metrics.py",
                "research/experiments/visible_metrics/audit.py",
            ),
        ),
        (
            "certified metric integration input enclosures",
            "research-only; actual roots/charts/densities/universal frames, "
            "not sampling or metrics",
            (
                "research/experiments/scientific_genesis/alternate_metric_projective_roots.py",
                "research/experiments/scientific_genesis/alternate_metric_enclosures.py",
                "research/experiments/scientific_genesis/alternate_metric_bounded_fibers.py",
                "research/experiments/scientific_genesis/alternate_metric_bounded_support.py",
                "research/experiments/scientific_genesis/projective_uniform_input_cells.py",
                "research/experiments/scientific_genesis/projective_uncertain_intersections.py",
                "research/experiments/scientific_genesis/uncertain_cover_weights.py",
                "research/experiments/scientific_genesis/auxiliary_cover_draws.py",
            ),
        ),
        (
            "same-carrier strict character projection and remaining flavor execution",
            "research-only; all four complete holomorphic matrices checked; "
            "physical normalization still requires controlled metrics and a common vacuum",
            (
                "research/experiments/scientific_genesis/"
                "alternate_constituent_up_matter_representatives.py",
                "research/experiments/scientific_genesis/"
                "alternate_constituent_up_cone_matter_lifts.py",
                "research/experiments/scientific_genesis/alternate_neutrino_mixed_pairing.py",
                "research/experiments/scientific_genesis/alternate_neutrino_ff_entries.py",
                "research/experiments/scientific_genesis/alternate_neutrino_full_matrix.py",
                "research/experiments/scientific_genesis/alternate_down_lepton_mixed_pairing.py",
                "research/experiments/scientific_genesis/alternate_down_lepton_ff_entries.py",
                "research/experiments/scientific_genesis/alternate_down_lepton_full_matrices.py",
            ),
        ),
        (
            "instantons",
            "carrier boundary and input audit only",
            (
                "src/onetheory/models/heterotic_schoen/instantons.py",
                "research/experiments/conic_pfaffians/audit.py",
            ),
        ),
        (
            "hidden sector",
            "topological target and input audit only",
            (
                "src/onetheory/models/heterotic_schoen/hidden.py",
                "research/experiments/hidden_bundle/audit.py",
            ),
        ),
        (
            "constants and Genesis identities",
            "units and established laws only; no origin theory",
            ("src/onetheory/core/units.py", "src/onetheory/reality.py"),
        ),
    )
    return [
        {"capability": name, "maturity": maturity, "locations": list(paths)}
        for name, maturity, paths in entries
    ]


def _scheduler() -> list[dict[str, object]]:
    """Return value-ranked tasks under the Scientific Genesis criterion."""

    tasks = [
        (
            "alternate_metric_convergence",
            5,
            4,
            5,
            5,
            5,
            2,
            "Use the actual residue and normalized FS measure with the bounded "
            "all-index evaluator and certified complete single-domain output; "
            "measure multi-point cost, then implement the positive auxiliary "
            "SU-uniform mixture using the quantitative global weight bound and "
            "admitted-cell root/weight bounds. Use the same-prefix draw workflow "
            "without dropping pending draws; justify external independence and "
            "complete section/frame integrands on those domains with integral errors; "
            "require Ricci-flat/HYM convergence before normalization.",
        ),
        (
            "shared_hidden_vacuum",
            4,
            5,
            5,
            4,
            5,
            2,
            "Close anomaly, instanton, hidden-sector, and shared stabilization "
            "dependencies without selecting a fitted vacuum.",
        ),
        (
            "full_independent_section_replay",
            5,
            3,
            3,
            2,
            5,
            5,
            "Backup independent certificate if full operator review fails; "
            "do not default to expanding every section separately.",
        ),
        (
            "automorphism_trichotomy_theorem",
            1,
            4,
            2,
            5,
            4,
            4,
            "Secondary structural work; cannot block the already frozen "
            "alternate carrier-to-observable path.",
        ),
        (
            "finish_automorphism_sweep",
            1,
            2,
            2,
            3,
            5,
            5,
            "Adds classification coverage but cannot simplify pair 73.",
        ),
        (
            "genesis_foundational_contract",
            2,
            5,
            5,
            5,
            4,
            4,
            "Clarifies assumptions and falsifiable targets without inventing a bridge.",
        ),
    ]
    records = []
    for name, distance, foundation, discrimination, reuse, cost, rabbit, rationale in tasks:
        score = round((distance * discrimination * reuse + foundation) / (cost * rabbit), 3)
        records.append(
            {
                "task": name,
                "scores": {
                    "distance_to_observable": distance,
                    "foundational_importance": foundation,
                    "probability_of_discriminating_theory": discrimination,
                    "structural_reuse": reuse,
                    "computational_cost": cost,
                    "risk_of_local_rabbit_hole": rabbit,
                },
                "priority_score": score,
                "rationale": rationale,
            }
        )
    return sorted(records, key=lambda item: (
        -float(cast(float, item["priority_score"])), str(item["task"]),
    ))


def build_state() -> dict[str, object]:
    """Inspect authoritative artifacts and assemble the deterministic state."""

    from .alternate_down_lepton_full_matrices import load_full_matrices
    from .alternate_necessary_hidden_chamber import read_hidden_chamber
    from .auxiliary_cover_draws import read_draws
    from .projective_uncertain_intersections import read_uncertain_intersections
    from .projective_uniform_input_cells import read_input_cells
    from .uncertain_cover_frames import read_frames
    from .uncertain_cover_weights import read_weights

    auxiliary_draws = read_draws()
    if _canonical_digest(auxiliary_draws) != (
        "bd942525f05b8d94696bf76b7cec146f52ca437d218f3c55fdbfa80a6411b33b"
    ):
        raise ValueError("the conditional same-prefix draw workflow changed its trusted digest")

    uncertain_weights = read_weights()
    if _canonical_digest(uncertain_weights) != (
        "5be593ab1bfa8d1200b72a944d127cde33343158f1be79236ed5bcef51934429"
    ):
        raise ValueError("the actual coupled uncertain weight bounds changed their trusted digest")
    uncertain_intersections = read_uncertain_intersections()
    if _canonical_digest(uncertain_intersections) != (
        "97981cfe6a6d67fd40287c8902a99f4ce3a73729fea6a64b4f133fdce82c0d26"
    ):
        raise ValueError("the admitted-cell uncertain intersections changed their trusted digest")
    uniform_input_cells = read_input_cells()
    if _canonical_digest(uniform_input_cells) != (
        "b8db32fa76846ebbc8fba44ff5fcb67b1a92f9961d05f8b61355141d8fd7cade"
    ):
        raise ValueError("the coupled projective input cells changed their trusted digest")

    hidden_chamber = read_hidden_chamber()
    if _canonical_digest(hidden_chamber) != (
        "997326fc92fc908d2781268b8c438795e3d19548b8d4c65fb560a9f18acb98c6"
    ):
        raise ValueError("the conditional necessary hidden chamber changed its trusted digest")
    ray_path = (
        ROOT
        / "data/generated/scientific_genesis/"
        "distinct_constituent_ray_screen.json"
    )
    ray_screen = json.loads(ray_path.read_text(encoding="utf-8"))
    ray_digest = ray_screen.pop("artifact_digest", None)
    if (
        ray_digest != _canonical_digest(ray_screen)
        or ray_screen.get("schema") != "distinct-constituent-ray-screen-v1"
        or ray_screen.get("unused_i6_local_unit_rays") != [[0, 1], [1, 1]]
        or ray_screen.get("ray_only_quotient_determinant_t_characters") != [1, 1]
        or ray_screen.get("ray_only_trivial_determinant_possible") is not False
        or ray_screen.get("alternate_deck_atlases_constructed") is not False
        or ray_screen.get("alternate_quotient_determinants_certified") is not False
        or ray_screen.get("alternate_higgs_characters_computed") is not False
    ):
        raise ValueError("the unused constituent-ray screen is not certified")
    cover_path = (
        ROOT / "data/generated/scientific_genesis/"
        "alternate_constituent_higgs_dimensions.json"
    )
    cover = json.loads(cover_path.read_text(encoding="utf-8"))
    cover_digest = cover.pop("artifact_digest", None)
    cases = cover.get("cases", [])
    if (
        cover_digest != _canonical_digest(cover)
        or cover.get("schema") != "alternate-constituent-higgs-dimensions-v2"
        or cover.get("hom_orientation")
        != "Hom(right=V2 tensor det(V1), left=V1)"
        or [case.get("ray_character_exponents") for case in cases]
        != [[0, 1], [1, 1]]
        or any(case.get("h1_dimension") != 4 for case in cases)
        or cover.get("alternate_quotient_determinants_certified") is not False
        or cover.get("alternate_higgs_characters_computed") is not False
        or cover.get("physical_higgs_spectrum_established") is not False
    ):
        raise ValueError("the alternate cover H1 result is not certified")
    alternate_atlas_path = (
        ROOT / "data/generated/scientific_genesis/"
        "alternate_constituent_deck_atlases.json"
    )
    alternate_atlas = json.loads(alternate_atlas_path.read_text(encoding="utf-8"))
    alternate_atlas_digest = alternate_atlas.pop("artifact_digest", None)
    atlas_cases = alternate_atlas.get("cases", [])
    if (
        alternate_atlas_digest != _canonical_digest(alternate_atlas)
        or alternate_atlas.get("schema") != "alternate-constituent-deck-atlases-v1"
        or alternate_atlas.get("alternate_constituent_atlases_exact") is not True
        or [case.get("ray_character_exponents") for case in atlas_cases]
        != [[0, 1], [1, 1]]
        or any(
            [item.get("legacy_frame_uniformly_related")
             for item in case.get("frame_comparisons", [])] != [False, True]
            for case in atlas_cases
        )
        or alternate_atlas.get("alternate_outer_extension_equivariance_certified")
        is not False
        or alternate_atlas.get("alternate_quotient_determinants_certified")
        is not False
    ):
        raise ValueError("the alternate constituent atlas result is not certified")
    alternate_det_path = (
        ROOT / "data/generated/scientific_genesis/"
        "alternate_constituent_determinant_descent.json"
    )
    alternate_det = json.loads(alternate_det_path.read_text(encoding="utf-8"))
    alternate_det_digest = alternate_det.pop("artifact_digest", None)
    alternate_det_cases = alternate_det.get("cases", [])
    if (
        alternate_det_digest != _canonical_digest(alternate_det)
        or alternate_det.get("schema")
        != "alternate-constituent-determinant-descent-v1"
        or alternate_det.get("atlas_artifact_digest") != alternate_atlas_digest
        or [case.get("total_determinant_character")
            for case in alternate_det_cases] != [[2, 1], [0, 1]]
        or any(case.get("total_cover_line_degree") != [0, 0, 0]
               for case in alternate_det_cases)
        or any(case.get("geometric_scalar_h3_character") != [0, 0]
               for case in alternate_det_cases)
        or any(case.get("scalar_h3_character")
               != case.get("total_determinant_character")
               for case in alternate_det_cases)
        or any(case.get("equivariantly_trivial_determinant") is not False
               for case in alternate_det_cases)
        or alternate_det.get("fixed_linearization_su4_excluded_for_both_rays")
        is not True
        or alternate_det.get("conditional_on_equivariant_outer_extension")
        is not True
        or alternate_det.get("outer_extension_constructed") is not False
        or alternate_det.get("other_linearizations_or_bundles_excluded")
        is not False
        or alternate_det.get("physical_higgs_spectrum_computed") is not False
    ):
        raise ValueError("the alternate determinant obstruction is not certified")
    hom_path = (
        ROOT / "data/generated/scientific_genesis/"
        "alternate_constituent_hom_actions.json"
    )
    hom = json.loads(hom_path.read_text(encoding="utf-8"))
    hom_digest = hom.pop("artifact_digest", None)
    hom_cases = hom.get("cases", [])
    if (
        hom_digest != _canonical_digest(hom)
        or hom.get("schema") != "alternate-constituent-hom-actions-v2"
        or [case.get("ray_character_exponents") for case in hom_cases]
        != [[0, 1], [1, 1]]
        or any(case.get("h1_dimension") != 4 for case in hom_cases)
        or any(case.get("boundary_basis_checked") != {"P": 129, "T": 129}
               for case in hom_cases)
        or any(case.get("boundary_preservation_certified") is not True
               for case in hom_cases)
        or hom.get("cohomology_action_certified") is not True
        or hom.get("equivariant_tensor_identification_available") is not False
        or hom.get("wilson_projection_performed") is not False
    ):
        raise ValueError("the alternate cover Hom action record is invalid")
    screen_path = (
        ROOT / "data/generated/scientific_genesis/"
        "alternate_constituent_character_screen.json"
    )
    screen = json.loads(screen_path.read_text(encoding="utf-8"))
    screen_digest = screen.pop("artifact_digest", None)
    screen_cases = screen.get("cases", [])
    screen_prerequisites = screen.get("prerequisite_artifact_digests", {})
    if (
        screen_digest != _canonical_digest(screen)
        or screen.get("schema") != "alternate-constituent-character-screen-v1"
        or screen_prerequisites.get("hom_actions") != hom_digest
        or screen_prerequisites.get("determinant") != alternate_det_digest
        or [case.get("ray_character_exponents") for case in screen_cases]
        != [[0, 1], [1, 1]]
        or [case.get("passes_conditional_one_higgs_zero_triplet_screen")
            for case in screen_cases] != [True, False]
        or any(case.get("hom_twist_uses_canonical_frame") is not True
               for case in screen_cases)
        or screen.get("determinant_line_cohomology_h0_to_h3") != {
            "det_v1": [0, 0, 0, 0],
            "det_v2": [0, 0, 0, 0],
        }
        or screen.get("ray_0_1_passes_conditional_higgs_screen") is not True
        or screen.get("ray_1_1_fails_conditional_triplet_screen") is not True
        or screen.get("outer_extension_constructed") is not False
        or screen.get("outer_extension_equivariance_certified") is not False
        or screen.get("stability_chamber_certified") is not False
        or screen.get("equivariant_chain_map_to_tensor_constructed") is not False
        or screen.get("physical_higgs_cocycles_available") is not False
        or screen.get("physical_carrier_frozen") is not False
    ):
        raise ValueError("the conditional alternate character screen is invalid")
    alternate_outer_path = (
        ROOT / "data/generated/scientific_genesis/"
        "alternate_constituent_outer_ext.json"
    )
    alternate_outer = json.loads(alternate_outer_path.read_text(encoding="utf-8"))
    alternate_outer_digest = alternate_outer.pop("artifact_digest", None)
    if (
        alternate_outer_digest != _canonical_digest(alternate_outer)
        or alternate_outer.get("schema") != "alternate-constituent-outer-ext-v1"
        or alternate_outer.get("screen_artifact_digest") != screen_digest
        or alternate_outer.get("ray_character_exponents") != [0, 1]
        or alternate_outer.get("outer_orientation") != "Hom(V2,V1)"
        or alternate_outer.get("reduced_dimensions_degree_0_to_2")
        != [1512, 4536, 4824]
        or alternate_outer.get("differential_ranks_degree_0_to_1")
        != [1512, 3006]
        or alternate_outer.get("d_squared_zero") is not True
        or alternate_outer.get("cover_h0_dimension") != 0
        or alternate_outer.get("cover_ext1_dimension") != 18
        or alternate_outer.get("invariant_ext1_dimension_computed") is not False
        or alternate_outer.get("outer_extension_constructed") is not False
        or alternate_outer.get("determinant_repaired_universal_cone_constructed")
        is not False
    ):
        raise ValueError("the alternate outer cover Ext is not certified")
    alternate_invariants_path = (
        ROOT / "data/generated/scientific_genesis/"
        "alternate_constituent_outer_invariants.json"
    )
    alternate_invariants = json.loads(
        alternate_invariants_path.read_text(encoding="utf-8")
    )
    alternate_invariants_digest = alternate_invariants.pop("artifact_digest", None)
    invariant_representatives = alternate_invariants.get(
        "strict_full_cech_representatives", []
    )
    invariant_coordinates = alternate_invariants.get(
        "reduced_invariant_coordinates", []
    )
    if (
        alternate_invariants_digest != _canonical_digest(alternate_invariants)
        or alternate_invariants.get("schema")
        != "alternate-constituent-outer-invariants-v1"
        or alternate_invariants.get("cover_artifact_digest") != alternate_outer_digest
        or alternate_invariants.get("ray_character_exponents") != [0, 1]
        or alternate_invariants.get("cover_ext1_dimension") != 18
        or alternate_invariants.get("cover_basis_averaged") != 18
        or alternate_invariants.get("invariant_ext1_dimension") != 2
        or alternate_invariants.get("strict_full_cech_representative_count") != 2
        or len(invariant_representatives) != 2
        or len(invariant_coordinates) != 2
        or any(item.get("term_count") != len(item.get("terms", []))
               for item in invariant_representatives)
        or any(not item.get("terms") for item in invariant_representatives)
        or any(not column for column in invariant_coordinates)
        or alternate_invariants.get("all_representatives_closed") is not True
        or alternate_invariants.get("all_representatives_strictly_deck_fixed")
        is not True
        or alternate_invariants.get("all_representatives_nonboundary_and_independent")
        is not True
        or alternate_invariants.get("common_character_twist_preserves_outer_hom_action")
        is not True
        or alternate_invariants.get("extension_point_selected") is not False
        or alternate_invariants.get("universal_rank_four_cone_constructed") is not False
        or alternate_invariants.get("stability_chamber_certified") is not False
    ):
        raise ValueError("the alternate outer invariants are not certified")
    alternate_cone_path = (
        ROOT / "data/generated/scientific_genesis/"
        "alternate_constituent_outer_universal_cone.json"
    )
    alternate_cone = json.loads(alternate_cone_path.read_text(encoding="utf-8"))
    alternate_cone_digest = alternate_cone.pop("artifact_digest", None)
    cone_prerequisites = alternate_cone.get("prerequisite_artifact_digests", {})
    cone_complex = alternate_cone.get("generated_complex", {})
    cone_chern = alternate_cone.get("chern_classes", {})
    if (
        alternate_cone_digest != _canonical_digest(alternate_cone)
        or alternate_cone.get("schema")
        != "alternate-constituent-outer-universal-cone-v1"
        or alternate_cone.get("invariant_artifact_digest")
        != alternate_invariants_digest
        or cone_prerequisites.get("alternate_constituent_deck_atlases")
        != alternate_atlas_digest
        or cone_prerequisites.get("alternate_constituent_determinant_descent")
        != alternate_det_digest
        or cone_prerequisites.get("alternate_constituent_character_screen")
        != screen_digest
        or cone_prerequisites.get("distinct_constituent_ray_screen")
        != ray_digest
        or alternate_cone.get("ray_character_exponents") != [0, 1]
        or alternate_cone.get("cover_ext1_dimension") != 18
        or alternate_cone.get("invariant_ext1_dimension") != 2
        or alternate_cone.get("projective_non_split_space") != "P^1(Q(omega))"
        or alternate_cone.get("split_locus", {}).get("ideal_generators")
        != ["a0", "a1"]
        or cone_complex.get("orientation") != "RHom(V2,V1)"
        or cone_complex.get("squared_zero") is not True
        or alternate_cone.get("strict_basis_rechecked_from_saved_terms")
        is not True
        or alternate_cone.get("constituent_graded_line_objects_match_published_selected_ray")
        is not True
        or alternate_cone.get("rank") != 4
        or cone_chern.get("c1") != ["0", "0", "0"]
        or cone_chern.get("c2") != ["8/3", "5/3", "4"]
        or cone_chern.get("c3") != "-6"
        or alternate_cone.get("rational_chern_data_only") is not True
        or alternate_cone.get("equivariant_descent_exact") is not True
        or alternate_cone.get("determinant_character_before_common_twist")
        != [2, 1]
        or alternate_cone.get("common_flat_character_twist") != [1, 2]
        or alternate_cone.get("determinant_character_after_common_twist")
        != [0, 0]
        or alternate_cone.get("common_twist_cancels_in_outer_hom") is not True
        or alternate_cone.get("quotient_determinant_trivial_exact") is not True
        or alternate_cone.get("local_freeness_locus") != "all A^2(Q(omega))"
        or alternate_cone.get("arbitrary_extension_point_selected") is not False
        or alternate_cone.get("stability_chamber_certified") is not False
        or alternate_cone.get("genuine_su4_locus_computed") is not False
        or alternate_cone.get("physical_higgs_cocycles_available") is not False
    ):
        raise ValueError("the alternate universal cone is not certified")
    alternate_stability_path = (
        ROOT / "data/generated/scientific_genesis/"
        "alternate_constituent_outer_stability_locus.json"
    )
    alternate_stability = json.loads(
        alternate_stability_path.read_text(encoding="utf-8")
    )
    alternate_stability_digest = alternate_stability.pop("artifact_digest", None)
    stable_chamber = alternate_stability.get("kahler_chamber", {})
    stable_box = stable_chamber.get("rational_open_box", {})
    stable_group = alternate_stability.get("structure_group", {})
    stable_quantifier = alternate_stability.get("parameter_quantifier", {})
    if (
        alternate_stability_digest != _canonical_digest(alternate_stability)
        or alternate_stability.get("schema")
        != "alternate-constituent-outer-stability-locus-v1"
        or alternate_stability.get("universal_cone_digest") != alternate_cone_digest
        or alternate_stability.get("serre_ray_artifact_digest") != ray_digest
        or alternate_stability.get("ray_character_exponents") != [0, 1]
        or alternate_stability.get("alternate_invariant_ext_dimension") != 2
        or alternate_stability.get("serre_quotient_ideals_unchanged")
        != ["I3", "I6"]
        or alternate_stability.get("serre_line_and_ideal_presentation_type_unchanged")
        is not True
        or alternate_stability.get("alternate_serre_ray_nontrivial_and_locally_free")
        is not True
        or alternate_stability.get("common_flat_twist_preserves_slopes")
        is not True
        or alternate_stability.get(
            "source_stability_bound_uses_serre_sequences_not_ray_coordinates"
        ) is not True
        or alternate_stability.get("extension_parameter_space")
        != "P^1(Q(omega))"
        or stable_quantifier.get("every_nonzero_parameter") is not True
        or stable_quantifier.get("genericity_assumed") is not False
        or alternate_stability.get("all_nonzero_parameters_stable_in_chamber")
        is not True
        or alternate_stability.get("certified_stable_locus")
        != "P^1(Q(omega)) x K^s"
        or len(stable_chamber.get("inequalities", [])) != 9
        or stable_chamber.get("anchor") != ["6", "9", "3"]
        or stable_box.get("all_slopes_negative") is not True
        or stable_box.get("inside_positive_cone") is not True
        or stable_group.get("cover_c3") != "-54"
        or stable_group.get("determinant_trivial") is not True
        or stable_group.get("proper_connected_irreducible_reduction_excluded")
        is not True
        or stable_group.get("genuine_su4_on_certified_locus") is not True
        or alternate_stability.get("full_kahler_stability_chamber_computed")
        is not False
        or alternate_stability.get("physical_spectrum_computed") is not False
        or alternate_stability.get("arbitrary_extension_point_selected")
        is not False
    ):
        raise ValueError("the alternate stable locus is not certified")
    alternate_matter_path = (
        ROOT / "data/generated/scientific_genesis/"
        "alternate_constituent_matter_profile.json"
    )
    alternate_matter = json.loads(alternate_matter_path.read_text(encoding="utf-8"))
    alternate_matter_digest = alternate_matter.pop("artifact_digest", None)
    matter_prerequisites = alternate_matter.get("prerequisite_artifact_digests", {})
    second_matter = alternate_matter.get("second_constituent", {})
    deck_matter = alternate_matter.get("deck_representation", {})
    if (
        alternate_matter_digest != _canonical_digest(alternate_matter)
        or alternate_matter.get("schema") != "alternate-constituent-matter-profile-v1"
        or matter_prerequisites.get("alternate_cone") != alternate_cone_digest
        or matter_prerequisites.get("alternate_stability") != alternate_stability_digest
        or alternate_matter.get("ray_character_exponents") != [0, 1]
        or second_matter.get("differential_ranks") != [[0, 189], [1, 81]]
        or second_matter.get("squared_zero") is not True
        or second_matter.get("cover_h0_to_h3") != [0, 18, 0, 0]
        or alternate_matter.get("visible_cover_h0_to_h3") != [0, 27, 0, 0]
        or deck_matter.get("regular_multiplicity") != 3
        or len(deck_matter.get("joint_character_multiplicities", [])) != 9
        or alternate_matter.get("published_matter_dimensions_used_as_rank_inputs")
        is not False
        or alternate_matter.get("physical_spectrum_established") is not False
    ):
        raise ValueError("the alternate matter profile is not certified")
    alternate_spectrum_path = (
        ROOT / "data/generated/scientific_genesis/"
        "alternate_constituent_structural_spectrum.json"
    )
    alternate_spectrum = json.loads(
        alternate_spectrum_path.read_text(encoding="utf-8")
    )
    alternate_spectrum_digest = alternate_spectrum.pop("artifact_digest", None)
    spectrum_inputs = alternate_spectrum.get("prerequisite_artifact_digests", {})
    alternate_projection = alternate_spectrum.get("observable_wilson_projection", {})
    if (
        alternate_spectrum_digest != _canonical_digest(alternate_spectrum)
        or alternate_spectrum.get("schema")
        != "alternate-constituent-structural-spectrum-v1"
        or spectrum_inputs.get("alternate_cone") != alternate_cone_digest
        or spectrum_inputs.get("alternate_stability") != alternate_stability_digest
        or spectrum_inputs.get("alternate_matter") != alternate_matter_digest
        or alternate_spectrum.get("parameter_locus") != "P^1(Q(omega)) x K^s"
        or alternate_spectrum.get("cover_higgs_h0_to_h3") != [0, 4, 4, 0]
        or alternate_spectrum.get("higgs_source_characters")
        != [[0, 1], [0, 2], [1, 2], [2, 1]]
        or alternate_spectrum.get(
            "hom_characters_independently_recovered_by_fourier_traces"
        ) is not True
        or alternate_spectrum.get("hom_fourier_characters")
        != [[0, 0], [1, 2], [2, 0], [2, 2]]
        or alternate_projection.get("families") != 3
        or alternate_projection.get("right_handed_neutrinos") != 3
        or alternate_projection.get("anti_families") != 0
        or alternate_projection.get("higgs_pairs") != 1
        or alternate_projection.get("massless_color_triplets") != 0
        or alternate_spectrum.get("observable_charged_structural_spectrum_passes")
        is not True
        or alternate_spectrum.get("explicit_cone_higgs_cocycles_computed")
        is not False
    ):
        raise ValueError("the alternate charged spectrum is not certified")
    alternate_carrier_path = (
        ROOT / "data/generated/scientific_genesis/"
        "alternate_constituent_carrier_state.json"
    )
    alternate_carrier = json.loads(
        alternate_carrier_path.read_text(encoding="utf-8")
    )
    alternate_carrier_digest = alternate_carrier.pop("artifact_digest", None)
    alternate_carrier_state = alternate_carrier.get("computable_one_theory_carrier_state", {})
    carrier_digests = alternate_carrier_state.get("certificate_digests", {})
    if (
        alternate_carrier_digest != _canonical_digest(alternate_carrier)
        or alternate_carrier.get("schema") != "alternate-constituent-carrier-state-v1"
        or carrier_digests.get("observable_spectrum") != alternate_spectrum_digest
        or carrier_digests.get("universal_cone") != alternate_cone_digest
        or carrier_digests.get("stable_su4_locus") != alternate_stability_digest
        or "relative_pushdowns" in carrier_digests
        or alternate_carrier_state.get("component_id") != "alternate-i6-ray-0-1-P1"
        or alternate_carrier_state.get("frozen") is not True
        or alternate_carrier_state.get("representative_selected") is not False
        or alternate_carrier.get("states_are_distinct") is not True
        or alternate_carrier.get("physical_yukawas_available") is not False
    ):
        raise ValueError("the alternate component freeze is not certified")
    up_matter_path = (
        ROOT / "data/generated/scientific_genesis/"
        "alternate_constituent_up_matter_representatives.json"
    )
    up_matter = json.loads(up_matter_path.read_text(encoding="utf-8"))
    up_matter_digest = up_matter.pop("artifact_digest", None)
    up_inputs = up_matter.get("prerequisite_artifact_digests", {})
    up_classes = up_matter.get("classes", [])
    if (
        up_matter_digest != _canonical_digest(up_matter)
        or up_matter.get("schema")
        != "alternate-constituent-up-matter-representatives-v1"
        or up_inputs.get("frozen_carrier") != alternate_carrier_digest
        or up_inputs.get("structural_spectrum") != alternate_spectrum_digest
        or up_inputs.get("cover_matter_profile") != alternate_matter_digest
        or up_inputs.get("published_wilson_source")
        != spectrum_inputs.get("published_wilson_source")
        or up_matter.get("common_flat_twist") != alternate_spectrum.get(
            "common_flat_twist"
        )
        or up_matter.get("up_spinor_wilson_weights") != [[1, 2], [2, 2]]
        or up_matter.get("up_higgs_wilson_weight") != [0, 2]
        or up_matter.get("constituent_character_sectors") != [[0, 0], [1, 0]]
        or up_matter.get("reduced_h1_dimension") != 18
        or up_matter.get("independent_boundary_dimension") != 189
        or [item.get("constituent_character") for item in up_classes]
        != [[0, 0], [0, 0], [1, 0], [1, 0]]
        or [item.get("repaired_carrier_character") for item in up_classes]
        != [[1, 2], [1, 2], [2, 2], [2, 2]]
        or any(item.get("full_cycle_exact") is not True for item in up_classes)
        or any(
            item.get("strict_alternate_character_exact") is not True
            for item in up_classes
        )
        or up_matter.get("outer_cone_lifts_computed") is not False
        or up_matter.get("higgs_cocycles_computed") is not False
        or up_matter.get("yukawa_matrix_computed") is not False
    ):
        raise ValueError("the alternate up-matter constituent slice is not certified")
    cone_matter_path = (
        ROOT / "data/generated/scientific_genesis/"
        "alternate_constituent_up_cone_matter_lifts.json"
    )
    cone_matter = json.loads(cone_matter_path.read_text(encoding="utf-8"))
    cone_matter_digest = cone_matter.pop("artifact_digest", None)
    cone_matter_inputs = cone_matter.get("prerequisite_artifact_digests", {})
    first_classes = cone_matter.get("first_constituent_constant_classes", [])
    second_lifts = cone_matter.get("second_constituent_parameter_linear_lifts", [])
    if (
        cone_matter_digest != _canonical_digest(cone_matter)
        or cone_matter.get("schema")
        != "alternate-constituent-up-cone-matter-lifts-v1"
        or cone_matter_inputs.get("frozen_carrier") != alternate_carrier_digest
        or cone_matter_inputs.get("strict_i6_matter") != up_matter_digest
        or cone_matter_inputs.get("universal_cone") != alternate_cone_digest
        or cone_matter_inputs.get("invariant_outer_basis")
        != alternate_cone.get("invariant_artifact_digest")
        or cone_matter.get("carrier_parameter_basis") != ["a0", "a1"]
        or cone_matter.get("common_flat_twist") != [1, 2]
        or [item.get("character") for item in first_classes]
        != [[0, 0], [1, 0]]
        or any(
            item.get("full_cycle_exact") is not True
            or item.get("strict_alternate_character_exact") is not True
            for item in first_classes
        )
        or [item.get("character") for item in second_lifts]
        != [[0, 0], [0, 0], [1, 0], [1, 0]]
        or any(
            [coefficient.get("parameter") for coefficient in item.get(
                "parameter_coefficients", []
            )] != ["a0", "a1"]
            for item in second_lifts
        )
        or any(
            coefficient.get("product_cycle_exact") is not True
            or coefficient.get("coefficientwise_cone_identity_exact") is not True
            or coefficient.get("strict_alternate_character_exact") is not True
            for item in second_lifts
            for coefficient in item.get("parameter_coefficients", [])
        )
        or cone_matter.get("all_coefficientwise_cone_identities_exact") is not True
        or cone_matter.get("all_lifts_strict_in_declared_characters") is not True
        or cone_matter.get("arbitrary_extension_point_selected") is not False
        or cone_matter.get("higgs_cocycle_computed") is not False
        or cone_matter.get("holomorphic_yukawa_matrix_computed") is not False
    ):
        raise ValueError("the alternate universal up-matter lifts are not certified")
    up_hom_path = (
        ROOT / "data/generated/scientific_genesis/"
        "alternate_up_higgs_hom_representative.json"
    )
    up_hom = json.loads(up_hom_path.read_text(encoding="utf-8"))
    up_hom_digest = up_hom.pop("artifact_digest", None)
    up_hom_inputs = up_hom.get("prerequisite_artifact_digests", {})
    if (
        up_hom_digest != _canonical_digest(up_hom)
        or up_hom.get("schema") != "alternate-up-higgs-hom-representative-v1"
        or up_hom_inputs.get("frozen_carrier") != alternate_carrier_digest
        or up_hom_inputs.get("universal_cone") != alternate_cone_digest
        or up_hom_inputs.get("structural_spectrum") != alternate_spectrum_digest
        or up_hom_inputs.get("alternate_hom_action")
        != spectrum_inputs.get("alternate_hom_actions")
        or up_hom.get("hom_character") != [2, 0]
        or up_hom.get("repaired_higgs_forward_character") != [0, 2]
        or up_hom.get("repaired_higgs_source_character") != [0, 1]
        or up_hom.get("full_term_count") != 324
        or up_hom.get("full_cycle_exact") is not True
        or up_hom.get("strict_hom_character_exact") is not True
        or up_hom.get("nonboundary_exact") is not True
        or up_hom.get("higgs_tensor_chain_map_constructed") is not False
        or up_hom.get("exterior_cone_higgs_cocycle_constructed") is not False
        or up_hom.get("yukawa_matrix_computed") is not False
    ):
        raise ValueError("the alternate up-Higgs Hom input is not certified")
    full_hom_path = (
        ROOT / "data/generated/scientific_genesis/"
        "alternate_up_higgs_hom_full_cochain.json"
    )
    full_hom = json.loads(full_hom_path.read_text(encoding="utf-8"))
    full_hom_digest = full_hom.pop("artifact_digest", None)
    if (
        full_hom_digest != _canonical_digest(full_hom)
        or full_hom.get("schema") != "alternate-up-higgs-hom-full-cochain-v1"
        or full_hom.get("hom_summary_digest") != up_hom_digest
        or full_hom.get("term_count") != up_hom.get("full_term_count")
        or len(full_hom.get("terms", [])) != up_hom.get("full_term_count")
        or full_hom.get("full_digest") != up_hom.get("full_digest")
        or full_hom.get("higgs_tensor_chain_map_constructed") is not False
        or full_hom.get("exterior_cone_higgs_cocycle_constructed") is not False
    ):
        raise ValueError("the persisted alternate Hom cochain is not certified")
    chart_restriction_path = (
        ROOT / "data/generated/scientific_genesis/"
        "alternate_up_higgs_chart_restriction.json"
    )
    chart_restriction = json.loads(chart_restriction_path.read_text(encoding="utf-8"))
    chart_restriction_digest = chart_restriction.pop("artifact_digest", None)
    chart_records = chart_restriction.get("right_chart_records", [])
    if (
        chart_restriction_digest != _canonical_digest(chart_restriction)
        or chart_restriction.get("schema") != "alternate-up-higgs-chart-restriction-v1"
        or chart_restriction.get("full_hom_cochain_artifact_digest") != full_hom_digest
        or chart_restriction.get("full_hom_term_digest") != full_hom.get("full_digest")
        or len(chart_records) != 6
        or [record.get("term_count") for record in chart_records]
        != [27, 36, 27, 36, 27, 36]
        or any(record.get("middle_term_count") != 0 for record in chart_records)
        or any(
            record.get("syzygy_dual_term_count") != record.get("term_count")
            for record in chart_records
        )
        or chart_restriction.get("right_fiber_overlap_term_count") != 135
        or chart_restriction.get("right_fiber_overlap_middle_term_count") != 81
        or chart_restriction.get("right_fiber_overlap_syzygy_term_count") != 54
        or chart_restriction.get("all_right_restrictions_closed") is not True
        or chart_restriction.get("hom_to_tensor_transport_constructed") is not False
        or chart_restriction.get("exterior_cone_higgs_cocycle_constructed") is not False
    ):
        raise ValueError("the alternate Hom chart restrictions are not certified")
    alternate_pairing_path = (
        ROOT / "data/generated/scientific_genesis/"
        "alternate_constituent_determinant_pairing.json"
    )
    alternate_pairing = json.loads(
        alternate_pairing_path.read_text(encoding="utf-8")
    )
    alternate_pairing_digest = alternate_pairing.pop("artifact_digest", None)
    pairing_inputs = alternate_pairing.get("prerequisite_artifact_digests", {})
    if (
        alternate_pairing_digest != _canonical_digest(alternate_pairing)
        or alternate_pairing.get("schema")
        != "alternate-constituent-determinant-pairing-v1"
        or pairing_inputs.get("frozen_carrier") != alternate_carrier_digest
        or pairing_inputs.get("universal_cone") != alternate_cone_digest
        or pairing_inputs.get("alternate_atlas") != alternate_atlas_digest
        or alternate_pairing.get("ray_character_exponents") != [0, 1]
        or alternate_pairing.get("chart_count") != 6
        or alternate_pairing.get("overlap_count") != 30
        or alternate_pairing.get("charts_different_from_selected_ray") != 6
        or len(alternate_pairing.get("chart_pairing_digests", {})) != 6
        or alternate_pairing.get("relation_annihilation_exact") is not True
        or alternate_pairing.get("alternating_exact") is not True
        or alternate_pairing.get("hypersurface_factorization_exact") is not True
        or alternate_pairing.get("corrected_overlap_covariance_exact") is not True
        or alternate_pairing.get("hom_to_tensor_chain_map_constructed") is not False
        or alternate_pairing.get("exterior_cone_higgs_cocycle_constructed") is not False
    ):
        raise ValueError("the alternate local pairing is not certified")
    local_inverse_path = (
        ROOT / "data/generated/scientific_genesis/"
        "alternate_constituent_duality_local_inverse.json"
    )
    local_inverse = json.loads(local_inverse_path.read_text(encoding="utf-8"))
    local_inverse_digest = local_inverse.pop("artifact_digest", None)
    inverse_inputs = local_inverse.get("prerequisite_artifact_digests", {})
    principal_opens = local_inverse.get("principal_open_row_pairs", {})
    if (
        local_inverse_digest != _canonical_digest(local_inverse)
        or local_inverse.get("schema")
        != "alternate-constituent-duality-local-inverse-v1"
        or inverse_inputs.get("frozen_carrier") != alternate_carrier_digest
        or inverse_inputs.get("alternate_pairing") != alternate_pairing_digest
        or inverse_inputs.get("local_unit_screen") != ray_digest
        or inverse_inputs.get("strict_up_higgs_hom_class") != up_hom_digest
        or local_inverse.get("ray_character_exponents") != [0, 1]
        or local_inverse.get("principal_open_count") != 60
        or local_inverse.get("dual_syzygy_contraction_count") != 60
        or len(principal_opens) != 6
        or any(len(pairs) != 10 for pairs in principal_opens.values())
        or local_inverse.get("inverse_identity_exact") is not True
        or local_inverse.get("two_term_chain_map_exact") is not True
        or local_inverse.get("dual_syzygy_contraction_exact") is not True
        or local_inverse.get("combined_local_hom_to_quotient_identity_exact")
        is not True
        or local_inverse.get("common_hypersurface_witness_base") != ["1", "2", "3"]
        or local_inverse.get("all_principal_opens_nonempty_at_witness") is not True
        or local_inverse.get("quotient_local_freeness_prerequisite_verified")
        is not True
        or local_inverse.get("corrected_overlap_covariance_prerequisite_verified")
        is not True
        or local_inverse.get("hom_to_tensor_cech_koszul_map_constructed")
        is not False
        or local_inverse.get("exterior_cone_higgs_cocycle_constructed")
        is not False
        or local_inverse.get("yukawa_matrix_computed") is not False
    ):
        raise ValueError("the alternate local duality inverse is not certified")
    local_section_path = (
        ROOT / "data/generated/scientific_genesis/"
        "alternate_up_higgs_local_syzygy_section.json"
    )
    local_section = json.loads(local_section_path.read_text(encoding="utf-8"))
    local_section_digest = local_section.pop("artifact_digest", None)
    local_section_inputs = local_section.get("prerequisite_artifact_digests", {})
    section_charts = local_section.get("charts", [])
    if (
        local_section_digest != _canonical_digest(local_section)
        or local_section.get("schema") != "alternate-up-higgs-local-syzygy-section-v1"
        or local_section_inputs.get("full_hom_cochain") != full_hom_digest
        or local_section_inputs.get("right_chart_restriction")
        != chart_restriction_digest
        or local_section_inputs.get("minor_open_inverse") != local_inverse_digest
        or len(section_charts) != 6
        or any(chart.get("block_count") != 3 for chart in section_charts)
        or any(len(chart.get("blocks", [])) != 3 for chart in section_charts)
        or local_section.get("all_actual_syzygy_blocks_contracted_exactly") is not True
        or local_section.get("minor_denominators_inverted_only_on_principal_opens")
        is not True
        or local_section.get("fiber_overlap_gluing_constructed") is not False
        or local_section.get("hom_to_tensor_chain_map_constructed") is not False
        or local_section.get("exterior_cone_higgs_cocycle_constructed") is not False
    ):
        raise ValueError("the actual alternate Hom syzygy sections are not certified")
    fiber_transport_path = (
        ROOT / "data/generated/scientific_genesis/"
        "alternate_up_higgs_fiber_overlap_transport.json"
    )
    fiber_transport = json.loads(fiber_transport_path.read_text(encoding="utf-8"))
    fiber_transport_digest = fiber_transport.pop("artifact_digest", None)
    fiber_inputs = fiber_transport.get("prerequisite_artifact_digests", {})
    fiber_record = fiber_transport.get("fiber_overlap_representative", {})
    if (
        fiber_transport_digest != _canonical_digest(fiber_transport)
        or fiber_transport.get("schema") != "alternate-up-higgs-fiber-overlap-transport-v1"
        or fiber_inputs.get("full_hom_cochain") != full_hom_digest
        or fiber_inputs.get("local_syzygy_section") != local_section_digest
        or fiber_transport.get("fiber_overlap_blocks_checked") != 9
        or fiber_record.get("base_pivots_checked") != [0, 1, 2]
        or fiber_record.get("first_factor_x_cells_checked") != [[0], [1], [2]]
        or fiber_record.get("middle_source_term_count_per_x_cell") != 9
        or fiber_record.get("koszul_source_term_count_per_x_cell") != 6
        or fiber_record.get("koszul_term_necessary_exact") is not True
        or fiber_record.get("corrected_koszul_divisibility_exact") is not True
        or fiber_transport.get("all_original_overlap_equations_exact") is not True
        or fiber_transport.get("all_corrected_koszul_divisibility_exact") is not True
        or fiber_transport.get("first_factor_x_cell_independence_exact") is not True
        or fiber_transport.get("base_chart_formula_independence_exact") is not True
        or fiber_transport.get("base_overlap_gluing_constructed") is not False
        or fiber_transport.get("global_hom_to_tensor_chain_map_constructed") is not False
        or fiber_transport.get("exterior_cone_higgs_cocycle_constructed") is not False
    ):
        raise ValueError("the alternate Hom fiber-overlap transport is not certified")
    quotient_image_path = (
        ROOT / "data/generated/scientific_genesis/"
        "alternate_up_higgs_quotient_overlap_image.json"
    )
    quotient_image = json.loads(quotient_image_path.read_text(encoding="utf-8"))
    quotient_image_digest = quotient_image.pop("artifact_digest", None)
    quotient_inputs = quotient_image.get("prerequisite_artifact_digests", {})
    quotient_rows = quotient_image.get("quotient_numerator_relation_order", [])
    if (
        quotient_image_digest != _canonical_digest(quotient_image)
        or quotient_image.get("schema") != "alternate-up-higgs-quotient-overlap-image-v1"
        or quotient_inputs.get("fiber_overlap_transport") != fiber_transport_digest
        or quotient_inputs.get("minor_open_inverse") != local_inverse_digest
        or quotient_image.get("target_charts_checked")
        != ["U_0_nu", "U_1_nu", "U_2_nu"]
        or quotient_image.get("minor_rows") != [0, 1]
        or [len(row) for row in quotient_rows] != [24, 24, 0, 0, 0]
        or quotient_image.get("quotient_nonzero_exact") is not True
        or quotient_image.get("three_chart_formula_independence_exact") is not True
        or quotient_image.get("cross_multiplied_quotient_identity_exact") is not True
        or quotient_image.get("minor_open_gluing_constructed") is not False
        or quotient_image.get("global_hom_to_tensor_chain_map_constructed")
        is not False
        or quotient_image.get("exterior_cone_higgs_cocycle_constructed") is not False
    ):
        raise ValueError("the alternate Hom quotient overlap is not certified")
    minor_gluing_path = (
        ROOT / "data/generated/scientific_genesis/"
        "alternate_up_higgs_minor_overlap_gluing.json"
    )
    minor_gluing = json.loads(minor_gluing_path.read_text(encoding="utf-8"))
    minor_gluing_digest = minor_gluing.pop("artifact_digest", None)
    minor_inputs = minor_gluing.get("prerequisite_artifact_digests", {})
    minor_records = minor_gluing.get("other_minor_records", [])
    expected_minor_pairs = [
        list(pair) for pair in combinations(range(5), 2) if pair != (0, 1)
    ]
    if (
        minor_gluing_digest != _canonical_digest(minor_gluing)
        or minor_gluing.get("schema") != "alternate-up-higgs-minor-overlap-gluing-v1"
        or minor_inputs.get("fiber_overlap_transport") != fiber_transport_digest
        or minor_inputs.get("reference_quotient_image") != quotient_image_digest
        or minor_inputs.get("minor_open_inverse") != local_inverse_digest
        or minor_gluing.get("reference_minor_rows") != [0, 1]
        or minor_gluing.get("target_charts_checked")
        != ["U_0_nu", "U_1_nu", "U_2_nu"]
        or [record.get("other_minor_rows") for record in minor_records]
        != expected_minor_pairs
        or any(
            record.get("projector_identity_exact") is not True
            or record.get("common_kernel_inverse_identity_exact") is not True
            or record.get("cross_multiplied_gluing_exact") is not True
            or any(
                not isinstance(record.get(key), str)
                or len(record[key]) != 64
                for key in (
                    "other_minor_digest",
                    "other_quotient_digest",
                    "relation_witness_digest",
                    "hypersurface_correction_digest",
                )
            )
            or len(record.get("other_quotient_term_counts", [])) != 5
            or len(record.get("relation_witness_term_counts", [])) != 3
            or len(record.get("hypersurface_correction_term_counts", [])) != 5
            for record in minor_records
        )
        or minor_gluing.get("homogeneous_relation_equal_on_target_charts") is not True
        or minor_gluing.get("base_chart_transitions_checked") != 12
        or minor_gluing.get("base_chart_transitions_identity_exact") is not True
        or minor_gluing.get("fiber_overlap_base_cover_compatibility_exact")
        is not True
        or minor_gluing.get("all_ten_minor_images_compatible_on_common_opens")
        is not True
        or minor_gluing.get("global_hom_to_tensor_chain_map_constructed")
        is not False
        or minor_gluing.get("exterior_cone_higgs_cocycle_constructed") is not False
    ):
        raise ValueError("the actual alternate Hom minor overlaps are not certified")
    yoneda_path = (
        ROOT / "data/generated/scientific_genesis/"
        "alternate_up_yoneda_evaluation.json"
    )
    yoneda = json.loads(yoneda_path.read_text(encoding="utf-8"))
    yoneda_digest = yoneda.pop("artifact_digest", None)
    yoneda_inputs = yoneda.get("prerequisite_artifact_digests", {})
    yoneda_records = yoneda.get("evaluations", [])
    yoneda_ratios = yoneda.get("basis_dependent_mixed_entry_ratios", [])
    if (
        yoneda_digest != _canonical_digest(yoneda)
        or yoneda.get("schema") != "alternate-up-yoneda-evaluation-v1"
        or yoneda_inputs.get("strict_hom_full_cochain") != full_hom_digest
        or yoneda_inputs.get("strict_i6_matter") != up_matter_digest
        or yoneda_inputs.get("determinant_line") != alternate_det_digest
        or yoneda.get("source_hom_orientation")
        != "Hom(V2 tensor det(V1), V1)"
        or yoneda.get("target_hom_orientation") != "Hom(det(V1), V1)"
        or [item.get("matter_character") for item in yoneda_records]
        != [[0, 0], [0, 0], [1, 0], [1, 0]]
        or [item.get("matter_seed_index") for item in yoneda_records]
        != [0, 5, 0, 5]
        or any(
            item.get("evaluated_term_count") != 207
            or len(item.get("reduced_coordinates", [])) != 3
            or item.get("reduced_nonboundary_exact") is not True
            for item in yoneda_records
        )
        or [item.get("candidate_over_reference") for item in yoneda_ratios]
        != ["2/7-1/7*omega", "-3/7-2/7*omega"]
        or yoneda.get("all_full_cycles_exact") is not True
        or yoneda.get("all_nonboundary_exact") is not True
        or yoneda.get("cohomological_ratios_exact") is not True
        or yoneda.get("same_cone_higgs_cocycle_constructed") is not False
        or yoneda.get("holomorphic_yukawa_entries_computed") is not False
    ):
        raise ValueError("the alternate direct Yoneda evaluation is not certified")
    first_pairing_path = (
        ROOT / "data/generated/scientific_genesis/"
        "mixed_schoen_determinant_pairing.json"
    )
    first_pairing = json.loads(first_pairing_path.read_text(encoding="utf-8"))
    first_pairing_digest = first_pairing.pop("artifact_digest", None)
    if (
        first_pairing_digest != _canonical_digest(first_pairing)
        or first_pairing.get("schema") != "mixed-schoen-determinant-pairing-v1"
        or first_pairing.get("pairing", {}).get("corrected_overlap_covariance_exact")
        is not True
    ):
        raise ValueError("the first constituent Pluecker input is not certified")
    mixed_trace_path = (
        ROOT / "data/generated/scientific_genesis/"
        "alternate_up_mixed_scalar_trace.json"
    )
    mixed_trace = json.loads(mixed_trace_path.read_text(encoding="utf-8"))
    mixed_trace_digest = mixed_trace.pop("artifact_digest", None)
    mixed_trace_inputs = mixed_trace.get("prerequisite_artifact_digests", {})
    mixed_trace_entries = mixed_trace.get("mixed_entries", [])
    if (
        mixed_trace_digest != _canonical_digest(mixed_trace)
        or mixed_trace.get("schema") != "alternate-up-mixed-scalar-trace-v1"
        or mixed_trace_inputs.get("nonboundary_yoneda_images") != yoneda_digest
        or mixed_trace_inputs.get("same_cone_matter_lifts") != cone_matter_digest
        or mixed_trace_inputs.get("first_constituent_pluecker_pairing")
        != first_pairing_digest
        or mixed_trace.get("ray_character_exponents") != [0, 1]
        or [item.get("first_matter_character") for item in mixed_trace_entries]
        != [[1, 0], [1, 0], [0, 0], [0, 0]]
        or [item.get("second_matter_character") for item in mixed_trace_entries]
        != [[0, 0], [0, 0], [1, 0], [1, 0]]
        or [item.get("ordered_cover_residue") for item in mixed_trace_entries]
        != ["3/2*omega", "3/14+9/14*omega", "3/2", "-9/14-3/7*omega"]
        or any(
            item.get("scalar_cochain_term_count") != 2257
            or item.get("projection_depth") != 3
            or item.get("reverse_projection_depth") != 3
            or item.get("full_scalar_cycle_exact") is not True
            or item.get("reverse_exchange_exact") is not True
            for item in mixed_trace_entries
        )
        or mixed_trace.get("all_four_cover_scalar_cycles_exact") is not True
        or mixed_trace.get("all_four_cover_residues_nonzero") is not True
        or mixed_trace.get("reverse_exchange_sign_exact") is not True
        or mixed_trace.get("yoneda_ratios_reproduced_exact") is not True
        or mixed_trace.get("quotient_trace_normalization_constructed") is not False
        or mixed_trace.get("same_cone_higgs_cocycle_constructed") is not False
        or mixed_trace.get("complete_holomorphic_up_matrix_available") is not False
        or mixed_trace.get("physical_yukawa_matrix_available") is not False
        or mixed_trace.get("observational_inputs_used") is not False
    ):
        raise ValueError("the alternate mixed cover scalar trace is not certified")
    up_support_path = (
        ROOT / "data/generated/scientific_genesis/"
        "alternate_up_yukawa_support.json"
    )
    up_support = json.loads(up_support_path.read_text(encoding="utf-8"))
    up_support_digest = up_support.pop("artifact_digest", None)
    support_inputs = up_support.get("prerequisite_artifact_digests", {})
    if (
        up_support_digest != _canonical_digest(up_support)
        or up_support.get("schema") != "alternate-up-yukawa-support-v1"
        or support_inputs.get("universal_cone") != alternate_cone_digest
        or support_inputs.get("strict_matter_lifts") != cone_matter_digest
        or support_inputs.get("structural_spectrum") != alternate_spectrum_digest
        or up_support.get("carrier_parameter_basis") != ["a0", "a1"]
        or up_support.get("entry_parameter_degrees")
        != [[[], [0], [0]], [[0], [1], [1]], [[0], [1], [1]]]
        or up_support.get("determinant_parameter_degrees_if_nonzero") != [1]
        or up_support.get("exact_exterior_support") is not True
        or up_support.get("lambda_coefficients_computed") is not False
        or up_support.get("rank_three_established") is not False
        or up_support.get("higgs_chain_cocycle_constructed") is not False
        or up_support.get("yukawa_matrix_computed") is not False
    ):
        raise ValueError("the alternate universal up support is not certified")
    rank_floor_path = (
        ROOT / "data/generated/scientific_genesis/alternate_up_rank_floor.json"
    )
    rank_floor = json.loads(rank_floor_path.read_text(encoding="utf-8"))
    rank_floor_digest = rank_floor.pop("artifact_digest", None)
    rank_inputs = rank_floor.get("prerequisite_artifact_digests", {})
    if (
        rank_floor_digest != _canonical_digest(rank_floor)
        or rank_floor.get("schema") != "alternate-up-rank-floor-v1"
        or rank_inputs.get("mixed_cover_traces") != mixed_trace_digest
        or rank_inputs.get("exterior_filtration_support") != up_support_digest
        or rank_floor.get("zero_first_first_entry") is not True
        or rank_floor.get("mixed_row_cover_residues")
        != ["3/2", "-9/14-3/7*omega"]
        or rank_floor.get("mixed_column_reverse_cover_residues")
        != ["-3/2*omega", "-3/14-9/14*omega"]
        or rank_floor.get("two_by_two_minors_rows_F_columns_F")
        != [
            ["9/4*omega", "9/28+27/28*omega"],
            ["9/14-9/28*omega", "27/196-45/196*omega"],
        ]
        or rank_floor.get("holomorphic_rank_lower_bound") != 2
        or rank_floor.get("all_four_minors_nonzero_exact") is not True
        or rank_floor.get("rank_floor_valid_for_every_nonsplit_extension") is not True
        or rank_floor.get("rank_three_established") is not False
        or rank_floor.get("complete_holomorphic_up_matrix_available") is not False
        or rank_floor.get("physical_yukawa_matrix_available") is not False
        or rank_floor.get("observational_inputs_used") is not False
    ):
        raise ValueError("the alternate up rank floor is not certified")
    null_path = (
        ROOT / "data/generated/scientific_genesis/alternate_up_null_channel.json"
    )
    null_channel = json.loads(null_path.read_text(encoding="utf-8"))
    null_digest = null_channel.pop("artifact_digest", None)
    null_inputs = null_channel.get("prerequisite_artifact_digests", {})
    channels = null_channel.get("null_channels", [])
    if (
        null_digest != _canonical_digest(null_channel)
        or null_channel.get("schema") != "alternate-up-null-channel-v1"
        or null_inputs.get("rank_floor") != rank_floor_digest
        or null_inputs.get("strict_yoneda_evaluations") != yoneda_digest
        or null_channel.get("determinant_prefactor") != "9/4*omega"
        or null_channel.get("formal_four_entry_identity_exact") is not True
        or null_channel.get("determinant_sensitive_unknown_coefficients") != 2
        or [item.get("matter_character") for item in channels]
        != [[0, 0], [1, 0]]
        or [item.get("seed5_over_seed0") for item in channels]
        != ["2/7-1/7*omega", "-3/7-2/7*omega"]
        or any(
            item.get("null_evaluation_term_count") != 144
            or item.get("primitive_term_count") != 90
            or item.get("full_yoneda_boundary_identity_exact") is not True
            for item in channels
        )
        or null_channel.get("null_to_null_coefficients_computed") is not False
        or null_channel.get("rank_three_established") is not False
        or null_channel.get("complete_holomorphic_up_matrix_available") is not False
        or null_channel.get("observational_inputs_used") is not False
    ):
        raise ValueError("the alternate up null-channel homotopies are not certified")
    dual_inputs = json.loads((
        ROOT / "data/generated/scientific_genesis/alternate_up_dual_higgs_inputs.json"
    ).read_text(encoding="utf-8"))
    dual_digest = dual_inputs.pop("artifact_digest", None)
    dual_prerequisites = dual_inputs.get("prerequisite_artifact_digests", {})
    if (
        dual_digest != _canonical_digest(dual_inputs)
        or dual_inputs.get("schema") != "alternate-up-dual-higgs-inputs-v1"
        or dual_prerequisites.get("outer_invariants") != alternate_invariants_digest
        or dual_prerequisites.get("strict_higgs_hom") != full_hom_digest
        or dual_inputs.get("outer_parameter_basis") != ["a0", "a1"]
        or dual_inputs.get("quotient_b_line_degree") != [-1, 1, 1]
        or dual_inputs.get("higgs_target_line_degree") != [1, -1, -1]
        or dual_inputs.get("outer_images_independent_mod_boundaries") is not True
        or dual_inputs.get("hom_to_tensor_inverse_used") is not False
        or dual_inputs.get("determinant_line_higgs_action_computed") is not False
        or dual_inputs.get("determinant_line_higgs_primitive_computed") is not False
        or dual_inputs.get("null_to_null_yukawa_computed") is not False
    ):
        raise ValueError("the reciprocal alternate Higgs-action inputs are not certified")
    exterior_action = json.loads((
        ROOT / "data/generated/scientific_genesis/alternate_up_exterior_higgs_action.json"
    ).read_text(encoding="utf-8"))
    exterior_digest = exterior_action.pop("artifact_digest", None)
    exterior_witnesses = exterior_action.get("witnesses", [])
    if (
        exterior_digest != _canonical_digest(exterior_action)
        or exterior_action.get("schema") != "alternate-up-exterior-higgs-action-v1"
        or exterior_action.get("prerequisite_artifact_digests", {}).get("reciprocal_covectors")
        != dual_digest
        or exterior_action.get("outer_parameter_basis") != ["a0", "a1"]
        or exterior_action.get("ordered_product") != "h wedge q(e)"
        or exterior_action.get("exterior_object_count") != 31
        or exterior_action.get("exterior_resolution_arrow_count") != 42
        or exterior_action.get("exterior_extension_term_count") != 2349
        or [exterior_action.get(field) for field in (
            "even_even_object_count", "even_odd_object_count", "odd_odd_object_count"
        )] != [10, 15, 6]
        or exterior_action.get("full_differential_square_witness_count") != 124
        or exterior_action.get("determinant_target_degree") != [-2, 2, 0]
        or [item.get("parameter") for item in exterior_witnesses] != ["a0", "a1"]
        or [item.get("product_term_count") for item in exterior_witnesses] != [191628, 169983]
        or any(
            item.get("full_product_cycle_exact") is not True
            or item.get("full_primitive_identity_exact") is not True
            or item.get("primitive_term_count", 0) <= 0
            or item.get("directly_transferred_candidate_columns") != 144
            or item.get("candidate_operator_globally_certified") is not False
            for item in exterior_witnesses
        )
        or any(exterior_action.get(field) is not False for field in (
            "minor_inversion_used", "complete_exterior_cone_higgs_cocycle_constructed",
            "null_to_null_coefficients_computed", "rank_three_established",
            "complete_holomorphic_up_matrix_available", "physical_yukawa_matrix_available",
            "extension_point_selected", "observational_inputs_used",
        ))
    ):
        raise ValueError("the full reciprocal exterior primitive identities are not certified")
    quotient_cone = json.loads((
        ROOT / "data/generated/scientific_genesis/alternate_up_higgs_quotient_cone.json"
    ).read_text(encoding="utf-8"))
    quotient_cone_digest = quotient_cone.pop("artifact_digest", None)
    quotient_coefficients = quotient_cone.get("parameter_coefficients", [])
    if (
        quotient_cone_digest != _canonical_digest(quotient_cone)
        or quotient_cone.get("schema") != "alternate-up-higgs-quotient-cone-v1"
        or quotient_cone.get("prerequisite_artifact_digests", {}).get("full_exterior_primitives")
        != exterior_digest
        or quotient_cone.get("outer_parameter_basis") != ["a0", "a1"]
        or quotient_cone.get("quotient_ideal_resolution_object_count") != 7
        or quotient_cone.get("quotient_ideal_resolution_arrow_count") != 6
        or quotient_cone.get("quotient_ideal_resolution_twist") != [0, 0, 1]
        or quotient_cone.get("quotient_is_a_vector_bundle") is not False
        or quotient_cone.get("quotient_covector_term_count") != 324
        or any(quotient_cone.get(field) is not True for field in (
            "full_quotient_covector_closed_exact",
            "universal_triangular_quotient_cone_squared_zero_exact",
            "higgs_lift_exists_by_full_pinned_primitive_identities",
            "null_matter_quotient_tensor_comparison_exact",
        ))
        or [item.get("parameter") for item in quotient_coefficients] != ["a0", "a1"]
        or [item.get("connecting_arrow_term_count") for item in quotient_coefficients]
        != [103986, 87354]
        or [item.get("higgs_action_term_count") for item in quotient_coefficients]
        != [191628, 169983]
        or [item.get("raw_null_tensor_difference_term_count") for item in quotient_coefficients]
        != [31668, 30234]
        or any(
            item.get("full_connecting_arrow_closed_exact") is not True
            or item.get("negative_action_equals_pinned_primitive_differential") is not True
            or item.get("primitive_solver_reexecuted_by_this_writer") is not False
            or item.get("raw_difference_has_only_actual_A_support") is not True
            or item.get("projected_null_tensor_difference_zero_exact") is not True
            or item.get("primitive_digest") != primitive.get("primitive_digest")
            or item.get("primitive_term_count") != primitive.get("primitive_term_count")
            for item, primitive in zip(quotient_coefficients, exterior_witnesses, strict=True)
        )
        or any(quotient_cone.get(field) is not False for field in (
            "extension_point_selected", "observational_inputs_used",
            "complete_holomorphic_up_matrix_available", "physical_yukawa_matrix_available",
        ))
    ):
        raise ValueError("the actual alternate Higgs quotient cone is not certified")
    ordered_scalar = json.loads((
        ROOT / "data/generated/scientific_genesis/alternate_up_first_order_scalar.json"
    ).read_text(encoding="utf-8"))
    ordered_scalar_digest = ordered_scalar.pop("artifact_digest", None)
    ordered_coefficients = ordered_scalar.get("parameter_coefficients", [])
    if (
        ordered_scalar_digest != _canonical_digest(ordered_scalar)
        or ordered_scalar.get("schema") != "alternate-up-first-order-scalar-screen-v1"
        or ordered_scalar.get("prerequisite_artifact_digests", {}).get("null_channels")
        != null_digest
        or ordered_scalar.get("prerequisite_artifact_digests", {}).get("exterior_primitives")
        != exterior_digest
        or ordered_scalar.get("outer_parameter_basis") != ["a0", "a1"]
        or ordered_scalar.get("scalar_order") != (
            "h cup (q(xL) tensor bR - bL tensor q(xR)) + k cup (bL wedge bR)"
        )
        or ordered_scalar.get("signed_two_slot_cone_actions_exact") is not True
        or ordered_scalar.get("higgs_primitive_sign") != (
            "positive, because the dual cone action is minus h wedge q(e)"
        )
        or [item.get("parameter") for item in ordered_coefficients] != ["a0", "a1"]
        or [item.get("ordered_cover_residue") for item in ordered_coefficients]
        != ["0", "2673/49-486/49*omega"]
        or any(
            item.get("null_wedge_term_count") != 2997
            or item.get("null_wedge_digest") != (
                "d8bc1e32e654bcf3eda60b77472e59b5d5d0f01bfc4fdc16c9efc6f9e8b8e6da"
            )
            or item.get("scalar_term_count", 0) <= 0
            or item.get("scalar_defect_term_count") != 0
            or item.get("ordered_scalar_closed_exact") is not True
            or not isinstance(item.get("ordered_cover_residue"), str)
            or item.get("projection_depth") != 3
            or item.get("physical_null_coefficient_assigned") is not False
            for item in ordered_coefficients
        )
        or any(ordered_scalar.get(field) is not False for field in (
            "derived_tensor_comparison_certified", "physical_null_coefficients_computed",
            "rank_three_established", "complete_holomorphic_up_matrix_available",
            "physical_yukawa_matrix_available", "extension_point_selected",
            "observational_inputs_used",
        ))
    ):
        raise ValueError("the complete ordered alternate null scalar screens are not certified")
    quotient_equivariance = json.loads((
        ROOT / "data/generated/scientific_genesis/alternate_up_quotient_equivariance.json"
    ).read_text(encoding="utf-8"))
    quotient_equivariance_digest = quotient_equivariance.pop("artifact_digest", None)
    quotient_generators = quotient_equivariance.get("generator_checks", [])
    if (
        quotient_equivariance_digest != _canonical_digest(quotient_equivariance)
        or quotient_equivariance.get("schema") != "alternate-up-quotient-equivariance-v1"
        or quotient_equivariance.get("prerequisite_artifact_digests") != {
            "quotient_cone": quotient_cone_digest, "outer_cone": alternate_cone_digest,
            "native_higgs": up_hom_digest,
        }
        or quotient_equivariance.get("global_first_quotient_term_count") != 54
        or quotient_equivariance.get("global_first_quotient_digest") != (
            "f43b04eea3480df907cbc3480a1c40c7506c6636522da3634a69d6e3fb45985e"
        )
        or quotient_equivariance.get("native_quotient_covector_character") != [2, 0]
        or quotient_equivariance.get("common_flat_twist") != [1, 2]
        or quotient_equivariance.get("covector_common_twist_weight") != -2
        or quotient_equivariance.get("repaired_up_higgs_character") != [0, 2]
        or quotient_equivariance.get(
            "determinant_repair_makes_covector_and_forward_higgs_characters_equal"
        ) is not True
        or [item.get("generator") for item in quotient_generators] != ["P", "T"]
        or [item.get("inherited_B1_line_frame") for item in quotient_generators] != ["omega", "1"]
        or [item.get("native_higgs_eigenvalue") for item in quotient_generators]
        != ["-1-omega", "1"]
        or any(
            item.get("full_global_quotient_strictly_equivariant_exact") is not True
            or item.get("full_quotient_higgs_character_exact") is not True
            or item.get("connecting_arrows") != [
                {
                    "parameter": arrow["parameter"],
                    "full_connecting_arrow_digest": arrow["connecting_arrow_digest"],
                    "full_connecting_arrow_strictly_fixed_exact": True,
                } for arrow in quotient_coefficients
            ] for item in quotient_generators
        )
        or any(quotient_equivariance.get(field) is not False for field in (
            "line_frame_selected_to_fit_spectrum", "physical_pairing_chain_map_constructed",
            "complete_holomorphic_up_matrix_available", "physical_yukawa_matrix_available",
            "extension_point_selected", "observational_inputs_used",
        ))
    ):
        raise ValueError("the inherited alternate quotient equivariance is not certified")
    pairing_exchange = json.loads((
        ROOT / "data/generated/scientific_genesis/alternate_up_pairing_exchange.json"
    ).read_text(encoding="utf-8"))
    pairing_exchange_digest = pairing_exchange.pop("artifact_digest", None)
    exchange_coefficients = pairing_exchange.get("parameter_coefficients", [])
    exchange_archive = ROOT / (
        "data/generated/scientific_genesis/alternate_up_pairing_exchange.cochains.json.gz"
    )
    if (
        pairing_exchange_digest != _canonical_digest(pairing_exchange)
        or pairing_exchange.get("schema") != "alternate-up-pairing-exchange-v1"
        or pairing_exchange.get("prerequisite_artifact_digests") != {
            "forward_scalars": ordered_scalar_digest, "full_exterior_primitives": exterior_digest,
        }
        or pairing_exchange.get("outer_parameter_basis") != ["a0", "a1"]
        or pairing_exchange.get("full_cochain_archive_name") != exchange_archive.name
        or pairing_exchange.get("full_cochain_archive_sha256") != _sha256(exchange_archive)
        or [item.get("parameter") for item in exchange_coefficients] != ["a0", "a1"]
        or any(
            item.get("forward_scalar_digest") != forward["scalar_digest"]
            or item.get("forward_direct_laurent_residue") != forward["ordered_cover_residue"]
            or item.get("forward_direct_and_transferred_residues_equal") is not True
            or item.get("physical_higgs_identification_certified") is not False
            or not isinstance(item.get("reverse_scalar_closed_exact"), bool)
            or not isinstance(item.get("exchange_difference_boundary_exact"), bool)
            or (item["reverse_scalar_closed_exact"] and (
                item.get("reverse_defect_term_count") != 0
                or item.get("reverse_direct_and_transferred_residues_equal") is not True
                or not isinstance(item.get("reverse_cover_residue"), str)
            ))
            or (not item["reverse_scalar_closed_exact"] and (
                item.get("reverse_defect_term_count", 0) <= 0
                or item.get("reverse_cover_residue") is not None
                or item.get("exchange_difference_boundary_exact") is not False
            ))
            or (item["exchange_difference_boundary_exact"] and (
                item.get("reverse_cover_residue") != forward["ordered_cover_residue"]
                or item.get("exchange_primitive_term_count") is None
                or item.get("exchange_homotopy_depth") is None
            ))
            for item, forward in zip(exchange_coefficients, ordered_coefficients, strict=True)
        )
        or any(pairing_exchange.get(field) is not False for field in (
            "primitive_sign_changed", "symmetrizing_average_used",
            "physical_higgs_identification_certified", "complete_holomorphic_up_matrix_available",
            "physical_yukawa_matrix_available", "extension_point_selected",
            "observational_inputs_used",
        ))
    ):
        raise ValueError("the actual alternate pairing exchange screen is not certified")
    null_line = json.loads((
        ROOT / "data/generated/scientific_genesis/alternate_up_null_line_homotopies.json"
    ).read_text(encoding="utf-8"))
    null_line_digest = null_line.pop("artifact_digest", None)
    null_line_witnesses = null_line.get("null_line_witnesses", [])
    if (
        null_line_digest != _canonical_digest(null_line)
        or null_line.get("schema") != "alternate-up-null-line-homotopies-v1"
        or null_line.get("prerequisite_artifact_digests") != {
            "null_channels": null_digest, "strict_higgs": full_hom_digest,
            "actual_matter": up_matter_digest, "natural_quotient": quotient_cone_digest,
        }
        or null_line.get("line_degree") != [1, -1, -1]
        or null_line.get("line_h0_to_h3") != [0, 0, 9, 0]
        or null_line.get("hom_detF_to_K_ambient_space_dimensions") != [
            [-3, 0], [-2, 0], [-1, 0], [0, 0], [1, 108], [2, 72], [3, 0], [4, 0], [5, 0],
        ]
        or null_line.get("hom_detF_to_K_dimension") != 0
        or null_line.get("K_ambient_space_dimensions") != [
            [-3, 0], [-2, 0], [-1, 0], [0, 90], [1, 152], [2, 70], [3, 8], [4, 0], [5, 0],
        ]
        or null_line.get("K_h0_to_h3") != [0, 5, 5, 0]
        or null_line.get("remaining_matter_product_H2K_dimension") != 5
        or [item.get("matter_character") for item in null_line_witnesses] != [[0, 0], [1, 0]]
        or any(
            item.get("primitive_term_count") != 90
            or item.get("primitive_digest") != reference["primitive_digest"]
            or item.get("null_evaluation_digest") != reference["null_evaluation_digest"]
            or len(item.get("full_primitive_terms", [])) != 90
            or item.get("primitive_has_only_line_support") is not True
            or item.get("full_line_primitive_identity_exact") is not True
            or item.get("ordered_higgs_null_matter_evaluation_exact") is not True
            for item, reference in zip(null_line_witnesses, channels, strict=True)
        )
        or null_line.get("line_primitive_unique_modulo_boundaries") is not True
        or null_line.get("identity_endpoint_extension_map_unique_if_it_exists") is not True
        or any(null_line.get(field) is not False for field in (
            "natural_matter_product_comparison_certified",
            "complete_comparison_indeterminacy_eliminated", "physical_null_coefficients_computed",
            "complete_holomorphic_up_matrix_available", "physical_yukawa_matrix_available",
            "extension_point_selected", "observational_inputs_used",
        ))
    ):
        raise ValueError("the actual null line homotopies and ambiguity groups are not certified")
    boundary_attack = json.loads((
        ROOT / "data/generated/scientific_genesis/alternate_up_exterior_boundary_attack.json"
    ).read_text(encoding="utf-8"))
    boundary_attack_digest = boundary_attack.pop("artifact_digest", None)
    boundary_witness = boundary_attack.get("attack", {})
    if (
        boundary_attack_digest != _canonical_digest(boundary_attack)
        or boundary_attack.get("schema") != "alternate-up-exterior-boundary-attack-v1"
        or boundary_attack.get("prerequisite_artifact_digests") != {
            "actual_matter": up_matter_digest, "null_channels": null_digest,
            "exterior_construction": exterior_digest,
        }
        or boundary_witness.get("matter_character") != [0, 0]
        or boundary_witness.get("other_matter_character") != [1, 0]
        or any(boundary_witness.get(name, {}).get("term_count") != count for name, count in (
            ("boundary_primitive", 3), ("exact_boundary", 15), ("boundary_wedge", 284),
            ("closure_defect", 124), ("primitive_wedge", 78), ("leibniz_defect", 48),
            ("corrected_boundary_wedge", 302),
        ))
        or boundary_witness.get("closure_defect", {}).get("cochain_digest") != (
            "4782ee9be7cb90ee6c6b370f3d6b22ae6b8bc3550bfa7cbfa0666de4454224e4"
        )
        or boundary_witness.get("original_null_wedge_digest") != ordered_coefficients[0][
            "null_wedge_digest"
        ]
        or boundary_witness.get("corrected_null_wedge_digest") != ordered_coefficients[0][
            "null_wedge_digest"
        ]
        or boundary_witness.get("closure_defect_exterior_pairs") != [[0, 1], [0, 2]]
        or any(boundary_witness.get(field) is not True for field in (
            "strict_boundary_primitive_character_exact", "strict_boundary_character_exact",
            "full_boundary_cycle_exact", "original_null_wedge_closed_exact",
            "modified_matter_class_unchanged_exact", "modified_matter_representative_closed_exact",
            "modified_matter_character_exact",
            "full_leibniz_defect_differential_is_negative_closure_defect",
            "corrected_even_boundary_wedge_is_full_primitive_differential",
            "corrected_even_boundary_wedge_closed_exact",
            "original_null_wedge_unchanged_by_even_correction",
        ))
        or any(boundary_witness.get(field) is not False for field in (
            "modified_exterior_wedge_closed_exact", "raw_exterior_cup_is_all_input_chain_map",
            "complete_tensor_comparison_certified", "original_ordered_scalar_screens_refuted",
            "carrier_refuted", "physical_null_coefficient_assigned",
        ))
        or any(boundary_attack.get(field) is not False for field in (
            "natural_product_comparison_certified", "complete_holomorphic_up_matrix_available",
            "physical_yukawa_matrix_available", "extension_point_selected",
            "observational_inputs_used",
        ))
    ):
        raise ValueError("the scoped exterior boundary counterexample and repair are not certified")
    syzygy_tensor = json.loads((
        ROOT / "data/generated/scientific_genesis/alternate_up_syzygy_tensor_comparison.json"
    ).read_text(encoding="utf-8"))
    syzygy_tensor_digest = syzygy_tensor.pop("artifact_digest", None)
    syzygy_witness = syzygy_tensor.get("comparison", {})
    if (
        syzygy_tensor_digest != _canonical_digest(syzygy_tensor)
        or syzygy_tensor.get("schema") != "alternate-up-syzygy-tensor-comparison-v1"
        or syzygy_tensor.get("prerequisite_artifact_digests") != {
            "actual_matter": up_matter_digest, "null_channels": null_digest,
            "even_boundary_attack": boundary_attack_digest,
        }
        or syzygy_witness.get("matter_character") != [0, 0]
        or syzygy_witness.get("other_matter_character") != [1, 0]
        or syzygy_witness.get("primitive_internal_support") != [-1]
        or any(syzygy_witness.get(name, {}).get("term_count") != count for name, count in (
            ("primitive", 3), ("boundary", 27), ("raw_boundary_wedge", 289),
            ("raw_closure_defect", 489), ("corrected_primitive_wedge", 47),
            ("corrected_boundary_wedge", 294),
        ))
        or syzygy_witness.get("raw_closure_defect", {}).get("cochain_digest") != (
            "c5c42dca8e6e36c6865a69b58c28882e12c9a0049d5bc593a86db3bffd50d916"
        )
        or syzygy_witness.get("corrected_boundary_wedge", {}).get("cochain_digest") != (
            "c6438a448029c367075e6ce298c9167eb8b0859edf6c50b81581e11fa2978999"
        )
        or syzygy_witness.get("original_null_wedge_digest") != ordered_coefficients[0][
            "null_wedge_digest"
        ]
        or any(syzygy_witness.get(field) is not True for field in (
            "full_rank_one_row_closed_exact", "primitive_and_boundary_strict_character_exact",
            "boundary_is_nonzero_exact_cycle",
            "corrected_boundary_wedge_is_full_primitive_differential",
            "corrected_boundary_wedge_closed_exact", "original_null_wedge_unchanged_exact",
            "all_input_F_tensor_identity_derived_under_rank_one_hypotheses",
        ))
        or any(syzygy_witness.get(field) is not False for field in (
            "raw_boundary_wedge_closed_exact", "outer_cone_comparison_certified",
            "natural_physical_pairing_certified",
        ))
        or any(syzygy_tensor.get(field) is not False for field in (
            "complete_tensor_comparison_certified", "complete_holomorphic_up_matrix_available",
            "physical_yukawa_matrix_available", "extension_point_selected",
            "observational_inputs_used",
        ))
    ):
        raise ValueError("the actual syzygy tensor comparison and scope are not certified")
    coupled_tensor = json.loads((
        ROOT / "data/generated/scientific_genesis/alternate_up_coupled_tensor_comparison.json"
    ).read_text(encoding="utf-8"))
    coupled_tensor_digest = coupled_tensor.pop("artifact_digest", None)
    coupled_presentations = coupled_tensor.get("presentations", [])
    coupled_witnesses = coupled_tensor.get("actual_leibniz_checks", [])
    if (
        coupled_tensor_digest != _canonical_digest(coupled_tensor)
        or coupled_tensor.get("schema") != "alternate-up-coupled-tensor-comparison-v1"
        or coupled_tensor.get("coefficient_field") != "Q(omega)"
        or coupled_tensor.get("outer_parameter_basis") != ["a0", "a1"]
        or coupled_tensor.get("prerequisite_artifact_digests") != {
            "existing_quotient_cone": quotient_cone_digest,
            "actual_syzygy_comparison": syzygy_tensor_digest,
        }
        or coupled_tensor.get("derived_coupled_R_to_Q_tensor_identity") is not True
        or [item.get("parameter") for item in coupled_presentations] != ["a0", "a1"]
        or [item.get("parameter") for item in coupled_witnesses] != ["a0", "a1"]
        or [item.get("source_k2_arrow_term_count") for item in coupled_presentations] != [540, 432]
        or [item.get("source_right_matter_image_term_count") for item in coupled_witnesses]
        != [21756, 20301]
        or [item.get("full_product_differential_term_count") for item in coupled_witnesses]
        != [1479, 1307]
        or [item.get("full_product_differential_digest") for item in coupled_witnesses] != [
            "c37003d46a719c805a27a22f50e3df9eda929865cb93155e87aa16a6f1b989d1",
            "01b9d8d5403f0fc5bc7f5b603c5e838eeb3ffd5ba5f2729792dee4930f97e670",
        ]
        or any(
            item.get("source_object_count") != 9 or item.get("quotient_object_count") != 38
            or item.get("source_k2_arrow_term_count", 0) <= 0
            or item.get("quotient_mixed_arrow_term_count") != (
                2349 + reference["connecting_arrow_term_count"]
            )
            or item.get("connecting_arrow_term_count") != reference["connecting_arrow_term_count"]
            or item.get("connecting_arrow_digest") != reference["connecting_arrow_digest"]
            or item.get("quotient_is_a_vector_bundle") is not False
            or any(item.get(field) is not True for field in (
                "complete_outer_row_closed_against_inner_complex",
                "all_objects_and_polynomial_blocks_equal_exact",
                "complete_inner_mixed_block_equal_exact", "complete_connecting_arrow_equal_exact",
                "legitimate_A_wedge_B_relation_differential_invariant",
            ))
            for item, reference in zip(coupled_presentations, quotient_coefficients, strict=True)
        )
        or any(
            item.get("syzygy_primitive_term_count") != 3
            or item.get("right_null_matter_term_count") != 522
            or item.get("source_right_matter_image_term_count", 0) <= 0
            or item.get("product_term_count") != 47
            or item.get("product_digest") != (
                "dc03b2274292318343bdc56d12743573d01f0cab49025f9da5d723071c68bb53"
            )
            or item.get("second_differentiated_slot_term_count", 0) <= 0
            or item.get("full_signed_leibniz_identity_exact") is not True
            or item.get("source_differential_squares_checked_exact") is not True
            or item.get("constituent_null_matter_assumed_closed_in_R") is not False
            or item.get("physical_scalar_evaluated") is not False
            for item in coupled_witnesses
        )
        or any(coupled_tensor.get(field) is not False for field in (
            "full_carrier_scalar_pairing_evaluated", "complete_holomorphic_up_matrix_available",
            "physical_yukawa_matrix_available", "extension_point_selected",
            "observational_inputs_used",
        ))
    ):
        raise ValueError(
            "the actual coupled quotient tensor comparison and scope are not certified"
        )
    quotient_trace = json.loads((
        ROOT / "data/generated/scientific_genesis/alternate_up_quotient_trace.json"
    ).read_text(encoding="utf-8"))
    quotient_trace_digest = quotient_trace.pop("artifact_digest", None)
    trace_deck_checks = quotient_trace.get("deck_checks", [])
    if (
        quotient_trace_digest != _canonical_digest(quotient_trace)
        or quotient_trace.get("schema") != "alternate-up-quotient-trace-v1"
        or quotient_trace.get("coefficient_field") != "Q(omega)"
        or quotient_trace.get("cover_scalar_h0_to_h3") != [1, 0, 0, 1]
        or quotient_trace.get("full_generator_term_count") != 55
        or quotient_trace.get("full_generator_digest") != (
            "1e8720583364e1030c691c9bbb476734d17b3c6732a858cbd792da32c8a696b5"
        )
        or quotient_trace.get("full_generator_closed_exact") is not True
        or quotient_trace.get("cover_trace_of_generator") != "1"
        or quotient_trace.get("cover_h3_deck_character") != [0, 0]
        or quotient_trace.get("scalar_class_descent_certified") is not True
        or quotient_trace.get("free_quotient_group") != "Z3 x Z3"
        or quotient_trace.get("covering_degree") != 9
        or quotient_trace.get("geometry_input_identifier") != "schoen_quotient_2004"
        or quotient_trace.get("published_input_sha256") != _sha256(
            ROOT / "data/published/visible_carrier/source_manifest.json"
        )
        or quotient_trace.get("volume_form_convention") != {
            "cover": "dual to the fixed cover H3(O) generator with trace one",
            "quotient": "the unique form whose pullback is that cover form",
            "relation": "pi*Omega_quotient=Omega_cover",
        }
        or quotient_trace.get("finite_etale_trace_identity") != (
            "trace_cover(pi*alpha)=degree*trace_quotient(alpha)"
        )
        or quotient_trace.get("cover_to_quotient_trace_factor") != "1/9"
        or quotient_trace.get("quotient_trace_of_pullback_generator_class") != "1/9"
        or quotient_trace.get("quotient_trace_normalization_constructed") is not True
        or quotient_trace.get("holomorphic_trace_not_canonical_matter_normalization") is not True
        or len(trace_deck_checks) != 2
        or [item.get("generator") for item in trace_deck_checks] != ["P", "T"]
        or [item.get("difference_term_count") for item in trace_deck_checks] != [30, 0]
        or [item.get("primitive_term_count") for item in trace_deck_checks] != [16, 0]
        or [item.get("strictly_fixed") for item in trace_deck_checks] != [False, True]
        or any(
            item.get("cohomology_eigenvalue") != "1"
            or item.get("full_image_closed_exact") is not True
            or item.get("difference_boundary_exact") is not True
            for item in trace_deck_checks
        )
        or any(quotient_trace.get(field) is not False for field in (
            "physical_null_coefficient_assigned", "complete_holomorphic_up_matrix_available",
            "physical_yukawa_matrix_available", "extension_point_selected",
            "observational_inputs_used",
        ))
    ):
        raise ValueError("the actual scalar descent and explicit quotient trace are not certified")
    mixed_quotient = json.loads((
        ROOT / "data/generated/scientific_genesis/alternate_up_mixed_quotient_pairing.json"
    ).read_text(encoding="utf-8"))
    mixed_quotient_digest = mixed_quotient.pop("artifact_digest", None)
    mixed_quotient_entries = mixed_quotient.get("evaluated_entries", [])
    if (
        mixed_quotient_digest != _canonical_digest(mixed_quotient)
        or mixed_quotient.get("schema") != "alternate-up-mixed-quotient-pairing-v1"
        or mixed_quotient.get("prerequisite_artifact_digests") != {
            "explicit_trace_frame": quotient_trace_digest,
            "old_ordered_mixed_comparison": mixed_trace_digest,
            "frozen_carrier": alternate_carrier_digest, "actual_matter": up_matter_digest,
            "quotient_higgs_cone": quotient_cone_digest,
            "coupled_product_presentation": coupled_tensor_digest,
        }
        or mixed_quotient.get("basis_order") != {
            "rows": ["E(0,0)", "F(0,0):seed0", "F(0,0):seed5"],
            "columns": ["E(1,0)", "F(1,0):seed0", "F(1,0):seed5"],
        }
        or mixed_quotient.get("constant_mixed_entries_evaluated") is not True
        or mixed_quotient.get("first_first_entry_zero_by_B_wedge_B") is not True
        or mixed_quotient.get("exterior_filtration_parameter_degree") != 0
        or [(item.get("row"), item.get("column")) for item in mixed_quotient_entries]
        != [(0, 1), (0, 2), (1, 0), (2, 0)]
        or [item.get("cover_residue") for item in mixed_quotient_entries] != [
            "-3/2", "9/14+3/7*omega", "-3/2*omega", "-3/14-9/14*omega",
        ]
        or [item.get("quotient_residue") for item in mixed_quotient_entries] != [
            "-1/6", "1/14+1/21*omega", "-1/6*omega", "-1/42-1/14*omega",
        ]
        or any(
            item.get("full_scalar_closed_exact") is not True
            or item.get("exchanged_scalar_closed_exact") is not True
            or item.get("exchange_difference_boundary_exact") is not True
            or item.get("scalar_term_count") != 2257
            or item.get("reverse_scalar_digest") != item.get("scalar_digest")
            or item.get("exchange_primitive_term_count") != 0
            for item in mixed_quotient_entries
        )
        or any(mixed_quotient.get(field) is not False for field in (
            "second_second_entries_assigned", "complete_holomorphic_up_matrix_available",
            "physical_yukawa_matrix_available", "higgs_phase_adjusted",
            "extension_point_selected", "observational_inputs_used",
        ))
    ):
        raise ValueError("the actual Higgs-first mixed quotient entries are not certified")
    natural_null = json.loads((
        ROOT / "data/generated/scientific_genesis/alternate_up_coupled_null_scalar.json"
    ).read_text(encoding="utf-8"))
    natural_null_digest = natural_null.pop("artifact_digest", None)
    natural_coefficients = natural_null.get("parameter_coefficients", [])
    if (
        natural_null_digest != _canonical_digest(natural_null)
        or natural_null.get("schema") != "alternate-up-coupled-null-scalar-v1"
        or natural_null.get("prerequisite_artifact_digests") != {
            "coupled_tensor_comparison": coupled_tensor_digest,
            "explicit_higgs_primitive_archive": pairing_exchange_digest,
        }
        or natural_null.get("full_carrier_null_pairing_evaluated") is not True
        or natural_null.get("outer_parameter_basis") != ["a0", "a1"]
        or natural_null.get("scalar_order") != "h_K cup P1 + kappa cup P0"
        or natural_null.get("full_cochain_archive_name")
        != "alternate_up_coupled_null_scalar.cochains.json.gz"
        or natural_null.get("full_cochain_archive_sha256") != _sha256(
            ROOT / "data/generated/scientific_genesis/"
            "alternate_up_coupled_null_scalar.cochains.json.gz"
        )
        or [item.get("parameter") for item in natural_coefficients] != ["a0", "a1"]
        or [item.get("ordered_cover_residue") for item in natural_coefficients]
        != ["0", "2673/49-486/49*omega"]
        or [item.get("product_linear_term_count") for item in natural_coefficients]
        != [139818, 133573]
        or [item.get("scalar_term_count") for item in natural_coefficients] != [42302, 41454]
        or any(
            any(item.get(field) is not True for field in (
                "full_pushout_matter_lifts_closed_coefficientwise",
                "full_quotient_higgs_lift_closed_coefficientwise",
                "full_quotient_product_closed_coefficientwise", "scalar_closed_exact",
                "direct_and_transferred_cover_residues_equal", "earlier_screen_literal_equal",
            ))
            or item.get("product_constant_term_count") != 2997
            or item.get("earlier_screen_difference_term_count") != 0
            or item.get("scalar_digest") != old.get("scalar_digest")
            or item.get("quotient_normalization_assigned") is not False
            or item.get("physical_null_coefficient_assigned") is not False
            for item, old in zip(natural_coefficients, ordered_coefficients, strict=True)
        )
        or any(natural_null.get(field) is not False for field in (
            "complete_holomorphic_up_matrix_available", "physical_yukawa_matrix_available",
            "extension_point_selected", "quotient_normalization_assigned",
            "observational_inputs_used",
        ))
    ):
        raise ValueError("the complete natural null contraction and its scope are not certified")
    ff_inputs = {
        "frozen_carrier": alternate_carrier_digest,
        "actual_matter": up_matter_digest,
        "constituent_lift_certificate": cone_matter_digest,
        "coupled_product_presentation": coupled_tensor_digest,
        "higgs_primitive_archive": pairing_exchange_digest,
        "scalar_trace_frame": quotient_trace_digest,
        "constant_mixed_entries": mixed_quotient_digest,
        "complete_null_contraction": natural_null_digest,
    }
    ff_lift_specs = (
        (0, 1, [0, 0], 0, "b2fd30e6b26c8140ff52c41604e161d7fe39e83fd5edbafd63a224e0489094ea",
         (378, 27640, 13326)),
        (0, 2, [0, 0], 5, "d76441a381f99bee8419ce380a06e1786c7d8eb4347543b2535b96f35df7673d",
         (378, 26779, 12708)),
        (1, 1, [1, 0], 0, "d6ca93a2ffb79b652a709fe17cb275b1a9032b85d394a816b5348e23b51ef303",
         (378, 27564, 13278)),
        (1, 2, [1, 0], 5, "08871357a32bcfef583b2ebdb897817a9ce2cb4a49873444039a936e5cb69a69",
         (378, 26779, 12708)),
    )
    for index, (side, family, character, seed, expected_digest, counts) in enumerate(
        ff_lift_specs
    ):
        ff_path = ROOT / (
            f"data/generated/scientific_genesis/alternate_up_ff_lift_a0_"
            f"side{side}_family{family}.json"
        )
        ff_record = json.loads(ff_path.read_text(encoding="utf-8"))
        ff_digest = ff_record.pop("artifact_digest", None)
        ff_archive = ff_path.with_suffix(".cochains.json.gz")
        ff_full = json.loads(gzip.decompress(ff_archive.read_bytes()))
        ff_payload_digest = ff_full.pop("artifact_digest", None)
        ff_witnesses = ff_record.get("witnesses", {})
        ff_cochains = ff_full.get("cochains", {})
        if (
            ff_digest != _canonical_digest(ff_record)
            or ff_digest != expected_digest
            or ff_record.get("schema") != "alternate-up-ff-matter-lift-v1"
            or ff_record.get("parameter") != "a0"
            or ff_record.get("side") != side
            or ff_record.get("family") != family
            or ff_record.get("character") != character
            or ff_record.get("seed_index") != seed
            or ff_record.get("actual_constituent_coefficient")
            != second_lifts[index]["parameter_coefficients"][0]
            or ff_record.get("prerequisite_artifact_digests") != ff_inputs
            or ff_record.get("full_constituent_identity_exact") is not True
            or ff_record.get("full_pushout_identity_exact") is not True
            or ff_record.get("extension_point_selected") is not False
            or any(ff_record.get(flag, False) is not False for flag in (
                "complete_holomorphic_up_matrix_available", "physical_yukawa_matrix_available",
                "observational_inputs_used",
            ))
            or ff_record.get("full_cochain_archive_name") != ff_archive.name
            or ff_record.get("full_cochain_archive_sha256") != _sha256(ff_archive)
            or ff_payload_digest != _canonical_digest(ff_full)
            or ff_payload_digest != ff_record.get("full_cochain_payload_digest")
            or ff_full.get("schema") != "alternate-up-ff-matter-lift-v1-cochains"
            or set(ff_witnesses) != {
                "constant", "constituent_correction", "line_correction",
            }
            or set(ff_cochains) != set(ff_witnesses)
            or any(
                ff_witnesses[name] != {
                    "term_count": ff_cochains[name].get("term_count"),
                    "cochain_digest": ff_cochains[name].get("cochain_digest"),
                }
                or len(ff_cochains[name].get("terms", []))
                != ff_witnesses[name]["term_count"]
                for name in ff_witnesses
            )
            or tuple(ff_witnesses[name]["term_count"] for name in (
                "constant", "constituent_correction", "line_correction",
            )) != counts
        ):
            raise ValueError("an actual a0 F-F matter lift or full archive is not certified")
    ff_entry_specs = (
        (1, 1, "fa4c2645ce34db9df7f852f1ba629b7574406dec134aad019fe31989495d5b73",
         "181/2+45/2*omega", "181/18+5/2*omega", (2169, 106920, 43934)),
        (1, 2, "bd79511e73f4ad749cef740b860e8a83c3a6d55ef08031ca2c4e5b06c3e6f8e9",
         "33/7-1223/14*omega", "11/21-1223/126*omega", (2322, 116110, 50211)),
        (2, 1, "e3a7379c1a0e4d4c3e9418b4c7f6b6c9dff4b5468f8d7d6625d405945ef1b2e9",
         "-347/7-1249/14*omega", "-347/63-1249/126*omega", (2349, 115796, 50172)),
        (2, 2, "752244de9c48f512319a6a987455e895ebc24d1edab00ccd749440110aa2dcd9",
         "-97/49-165/49*omega", "-97/441-55/147*omega", (2211, 104693, 42815)),
    )
    ff_entry_digests = []
    for row, column, expected_digest, cover_residue, quotient_residue, counts in ff_entry_specs:
        ff_entry_path = ROOT / (
            f"data/generated/scientific_genesis/alternate_up_ff_a0_r{row}_c{column}.json"
        )
        ff_entry = json.loads(ff_entry_path.read_text(encoding="utf-8"))
        ff_entry_digest = ff_entry.pop("artifact_digest", None)
        ff_entry_archive = ff_entry_path.with_suffix(".cochains.json.gz")
        ff_entry_digests.append(ff_entry_digest)
        lift_digests = [
            next(spec[4] for spec in ff_lift_specs if spec[:2] == (side, family))
            for side, family in ((0, row), (1, column))
        ]
        witnesses = ff_entry.get("witnesses", {})
        if (
            ff_entry_digest != _canonical_digest(ff_entry)
            or ff_entry_digest != expected_digest
            or ff_entry.get("schema") != "alternate-up-ff-entry-v1"
            or ff_entry.get("parameter") != "a0"
            or (ff_entry.get("row"), ff_entry.get("column")) != (row, column)
            or (ff_entry.get("row_seed_index"), ff_entry.get("column_seed_index"))
            != (0 if row == 1 else 5, 0 if column == 1 else 5)
            or ff_entry.get("actual_matter_lift_digests") != lift_digests
            or ff_entry.get("prerequisite_artifact_digests") != ff_inputs
            or ff_entry.get("scalar_order") != "h_K cup P1 + kappa cup P0"
            or ff_entry.get("exterior_filtration_parameter_degree") != 1
            or ff_entry.get("cover_residue") != cover_residue
            or ff_entry.get("quotient_residue") != quotient_residue
            or any(ff_entry.get(flag) is not True for flag in (
                "full_coefficientwise_product_identity_exact",
                "full_scalar_closed_exact",
                "direct_transferred_and_inverse_convolution_traces_equal",
            ))
            or any(ff_entry.get(flag) is not False for flag in (
                "extension_point_selected", "physical_yukawa_matrix_available",
                "complete_holomorphic_up_matrix_available",
            ))
            or ff_entry.get("full_cochain_archive_name") != ff_entry_archive.name
            or ff_entry.get("full_cochain_archive_sha256") != _sha256(ff_entry_archive)
            or set(witnesses) != {"product_constant", "product_linear", "scalar"}
            or tuple(witnesses[name].get("term_count") for name in (
                "product_constant", "product_linear", "scalar",
            )) != counts
        ):
            raise ValueError("an exact a0 F-F scalar entry or archive is not certified")
    ff_block_path = ROOT / "data/generated/scientific_genesis/alternate_up_ff_coefficient_a0.json"
    ff_block = json.loads(ff_block_path.read_text(encoding="utf-8"))
    ff_block_digest = ff_block.pop("artifact_digest", None)
    if (
        ff_block_digest != _canonical_digest(ff_block)
        or ff_block_digest != "5b624f9a52f3e5397d0ea114e8beff753897238503a58dcfd7c398041a54dbff"
        or ff_block.get("schema") != "alternate-up-ff-coefficient-v1"
        or ff_block.get("parameter") != "a0"
        or ff_block.get("prerequisite_artifact_digests") != ff_inputs
        or ff_block.get("entry_artifact_digests") != ff_entry_digests
        or ff_block.get("cover_block") != [
            [spec[3] for spec in ff_entry_specs[:2]],
            [spec[3] for spec in ff_entry_specs[2:]],
        ]
        or ff_block.get("complete_null_scalar_digest")
        != natural_coefficients[0]["scalar_digest"]
        or ff_block.get("complete_null_cover_residue") != "0"
        or ff_block.get("complete_null_scalar_literal_equal") is not True
        or ff_block.get("all_four_entries_evaluated") is not True
        or any(ff_block.get(flag) is not False for flag in (
            "extension_point_selected", "physical_yukawa_matrix_available",
            "complete_holomorphic_up_matrix_available", "observational_inputs_used",
        ))
    ):
        raise ValueError("the complete exact a0 F-F block and natural null check are not certified")
    ff_a1_lift_specs = (
        (0, 1, [0, 0], 0, "77f04729847dc58ec78314fc1c6fb92017c5a999475dd7047e6f50ee2b837526",
         (378, 25244, 11961)),
        (0, 2, [0, 0], 5, "b32e6cc80c8492e01ffd896c2d77edb5e74a0967a4c962daf0263e64a84c5d03",
         (378, 23868, 11310)),
        (1, 1, [1, 0], 0, "fe0abbfd3110e15dfc6a8bd02ae5c8e54aabc881c5dfc33668cc3080d5481bd4",
         (378, 25220, 11973)),
        (1, 2, [1, 0], 5, "76c8051802c5be7be5a56edbba44ac62978a2501391bb734ee14348d4936e7df",
         (378, 23868, 11310)),
    )
    for index, (side, family, character, seed, expected_digest, counts) in enumerate(
        ff_a1_lift_specs
    ):
        lift_path = ROOT / (
            f"data/generated/scientific_genesis/alternate_up_ff_lift_a1_"
            f"side{side}_family{family}.json"
        )
        lift_record = json.loads(lift_path.read_text(encoding="utf-8"))
        lift_digest = lift_record.pop("artifact_digest", None)
        lift_archive = lift_path.with_suffix(".cochains.json.gz")
        lift_full = json.loads(gzip.decompress(lift_archive.read_bytes()))
        lift_payload_digest = lift_full.pop("artifact_digest", None)
        lift_witnesses = lift_record.get("witnesses", {})
        lift_cochains = lift_full.get("cochains", {})
        if (
            lift_digest != _canonical_digest(lift_record)
            or lift_digest != expected_digest
            or lift_record.get("schema") != "alternate-up-ff-matter-lift-v1"
            or lift_record.get("parameter") != "a1"
            or lift_record.get("side") != side
            or lift_record.get("family") != family
            or lift_record.get("character") != character
            or lift_record.get("seed_index") != seed
            or lift_record.get("actual_constituent_coefficient")
            != second_lifts[index]["parameter_coefficients"][1]
            or lift_record.get("prerequisite_artifact_digests") != ff_inputs
            or lift_record.get("full_constituent_identity_exact") is not True
            or lift_record.get("full_pushout_identity_exact") is not True
            or lift_record.get("extension_point_selected") is not False
            or any(lift_record.get(flag, False) is not False for flag in (
                "complete_holomorphic_up_matrix_available", "physical_yukawa_matrix_available",
                "observational_inputs_used",
            ))
            or lift_record.get("full_cochain_archive_name") != lift_archive.name
            or lift_record.get("full_cochain_archive_sha256") != _sha256(lift_archive)
            or lift_payload_digest != _canonical_digest(lift_full)
            or lift_payload_digest != lift_record.get("full_cochain_payload_digest")
            or lift_full.get("schema") != "alternate-up-ff-matter-lift-v1-cochains"
            or set(lift_witnesses) != {
                "constant", "constituent_correction", "line_correction",
            }
            or set(lift_cochains) != set(lift_witnesses)
            or any(
                lift_witnesses[name] != {
                    "term_count": lift_cochains[name].get("term_count"),
                    "cochain_digest": lift_cochains[name].get("cochain_digest"),
                }
                or len(lift_cochains[name].get("terms", []))
                != lift_witnesses[name]["term_count"]
                for name in lift_witnesses
            )
            or tuple(lift_witnesses[name]["term_count"] for name in (
                "constant", "constituent_correction", "line_correction",
            )) != counts
        ):
            raise ValueError("an actual a1 F-F matter lift or full archive is not certified")
    ff_a1_entry_specs = (
        (1, 1, "505e715da88acd1a0a2e91d811f6f45659f92b5ec629c845eae8f81b4a93780f",
         "617/2+93/2*omega", "617/18+31/6*omega", (2169, 101853, 43425)),
        (1, 2, "62298b039af54250cb7b4c305f21d811789cd3ddf6bb305890f046078a16f50b",
         "-1399/14-95/14*omega", "-1399/126-95/126*omega", (2322, 108444, 49706)),
        (2, 1, "9ddb9885fbe50b6ade521611abd8ee372333c3b397f6830961e126fb4573044a",
         "1235/14-55/7*omega", "1235/126-55/63*omega", (2349, 108380, 49719)),
        (2, 2, "94cfd013941bd9894a8b2e59eb46dad2ead6577a804e406db9fe82e57c165ffc",
         "65/2+omega", "65/18+1/9*omega", (2211, 97929, 42334)),
    )
    ff_a1_entry_digests = []
    for row, column, expected_digest, cover_residue, quotient_residue, counts in (
        ff_a1_entry_specs
    ):
        entry_path = ROOT / (
            f"data/generated/scientific_genesis/alternate_up_ff_a1_r{row}_c{column}.json"
        )
        entry_record = json.loads(entry_path.read_text(encoding="utf-8"))
        entry_digest = entry_record.pop("artifact_digest", None)
        entry_archive = entry_path.with_suffix(".cochains.json.gz")
        ff_a1_entry_digests.append(entry_digest)
        lift_digests = [
            next(spec[4] for spec in ff_a1_lift_specs if spec[:2] == (side, family))
            for side, family in ((0, row), (1, column))
        ]
        witnesses = entry_record.get("witnesses", {})
        if (
            entry_digest != _canonical_digest(entry_record)
            or entry_digest != expected_digest
            or entry_record.get("schema") != "alternate-up-ff-entry-v1"
            or entry_record.get("parameter") != "a1"
            or (entry_record.get("row"), entry_record.get("column")) != (row, column)
            or (entry_record.get("row_seed_index"), entry_record.get("column_seed_index"))
            != (0 if row == 1 else 5, 0 if column == 1 else 5)
            or entry_record.get("actual_matter_lift_digests") != lift_digests
            or entry_record.get("prerequisite_artifact_digests") != ff_inputs
            or entry_record.get("scalar_order") != "h_K cup P1 + kappa cup P0"
            or entry_record.get("exterior_filtration_parameter_degree") != 1
            or entry_record.get("cover_residue") != cover_residue
            or entry_record.get("quotient_residue") != quotient_residue
            or any(entry_record.get(flag) is not True for flag in (
                "full_coefficientwise_product_identity_exact",
                "full_scalar_closed_exact",
                "direct_transferred_and_inverse_convolution_traces_equal",
            ))
            or any(entry_record.get(flag) is not False for flag in (
                "extension_point_selected", "physical_yukawa_matrix_available",
                "complete_holomorphic_up_matrix_available",
            ))
            or entry_record.get("full_cochain_archive_name") != entry_archive.name
            or entry_record.get("full_cochain_archive_sha256") != _sha256(entry_archive)
            or set(witnesses) != {"product_constant", "product_linear", "scalar"}
            or tuple(witnesses[name].get("term_count") for name in (
                "product_constant", "product_linear", "scalar",
            )) != counts
        ):
            raise ValueError("an exact a1 F-F scalar entry or archive is not certified")
    ff_a1_block_path = ROOT / (
        "data/generated/scientific_genesis/alternate_up_ff_coefficient_a1.json"
    )
    ff_a1_block = json.loads(ff_a1_block_path.read_text(encoding="utf-8"))
    ff_a1_block_digest = ff_a1_block.pop("artifact_digest", None)
    if (
        ff_a1_block_digest != _canonical_digest(ff_a1_block)
        or ff_a1_block_digest != "49dae41f452f925a4165c0bed7baeaaaead0990e81b7cd54d11adf4fefe3445f"
        or ff_a1_block.get("schema") != "alternate-up-ff-coefficient-v1"
        or ff_a1_block.get("parameter") != "a1"
        or ff_a1_block.get("prerequisite_artifact_digests") != ff_inputs
        or ff_a1_block.get("entry_artifact_digests") != ff_a1_entry_digests
        or ff_a1_block.get("cover_block") != [
            [spec[3] for spec in ff_a1_entry_specs[:2]],
            [spec[3] for spec in ff_a1_entry_specs[2:]],
        ]
        or ff_a1_block.get("complete_null_scalar_digest")
        != natural_coefficients[1]["scalar_digest"]
        or ff_a1_block.get("complete_null_cover_residue") != "2673/49-486/49*omega"
        or ff_a1_block.get("complete_null_scalar_literal_equal") is not True
        or ff_a1_block.get("all_four_entries_evaluated") is not True
        or any(ff_a1_block.get(flag) is not False for flag in (
            "extension_point_selected", "physical_yukawa_matrix_available",
            "complete_holomorphic_up_matrix_available", "observational_inputs_used",
        ))
    ):
        raise ValueError("the complete exact a1 F-F block and natural null check are not certified")
    full_up_path = ROOT / (
        "data/generated/scientific_genesis/alternate_up_full_holomorphic_matrix.json"
    )
    full_up = json.loads(full_up_path.read_text(encoding="utf-8"))
    full_up_digest = full_up.pop("artifact_digest", None)
    if (
        full_up_digest != _canonical_digest(full_up)
        or full_up_digest != "5dca3368f127ddf90eb8e263b403e6ca74f8857a3e505930194c51a67120884f"
        or full_up.get("schema") != "alternate-up-full-holomorphic-matrix-v1"
        or full_up.get("carrier_status") != "conditional on the selected heterotic UV realization"
        or full_up.get("coefficient_field") != "Q(omega)"
        or full_up.get("outer_parameter_basis") != ["a0", "a1"]
        or full_up.get("basis_order") != mixed_quotient.get("basis_order")
        or full_up.get("scalar_order") != "Higgs first in the fixed quotient volume frame"
        or full_up.get("cover_to_quotient_trace_factor") != "1/9"
        or full_up.get("prerequisite_artifact_digests") != {
            "ff_coefficient_a0": ff_block_digest,
            "ff_coefficient_a1": ff_a1_block_digest,
            "mixed_pairing": mixed_quotient_digest,
        }
        or full_up.get("determinant") != [{
            "powers": [0, 1], "coefficient": "-3/98-39/196*omega",
        }]
        or full_up.get("rank_two_minor") != [{
            "powers": [0, 0], "coefficient": "-1/36*omega",
        }]
        or full_up.get("null_contraction") != [{
            "powers": [0, 1], "coefficient": "297/49-54/49*omega",
        }]
        or len(full_up.get("matrix_entries", [])) != 3
        or any(len(row) != 3 for row in full_up["matrix_entries"])
        or full_up.get("all_nine_entries_derived_from_actual_carrier") is not True
        or full_up.get("holomorphic_matrix_available") is not True
        or any(full_up.get(flag) is not False for flag in (
            "physical_yukawa_matrix_available", "canonical_matter_metrics_available",
            "common_vacuum_stabilized", "extension_point_selected",
            "observational_inputs_used",
        ))
    ):
        raise ValueError("the complete alternate holomorphic matrix or its scope is not certified")
    metric_path = ROOT / (
        "data/generated/scientific_genesis/alternate_metric_subbundle_vanishing.json"
    )
    metric = json.loads(metric_path.read_text(encoding="utf-8"))
    metric_digest = metric.pop("artifact_digest", None)
    first_arrows = json.loads((ROOT / (
        "data/generated/scientific_genesis/mixed_constituent_schoen_arrows.json"
    )).read_text(encoding="utf-8"))
    first_arrows_digest = first_arrows.pop("artifact_digest", None)
    metric_lines = metric.get("line_objects", [])
    if (
        metric_digest != _canonical_digest(metric)
        or metric_digest != "97e390edc44ba0d89b32ebb48d0409b5c7f1e2f53ece5bb96011d5093be585bc"
        or first_arrows_digest != _canonical_digest(first_arrows)
        or metric.get("schema") != "alternate-metric-subbundle-vanishing-v1"
        or metric.get("carrier_status") != "conditional on the selected heterotic UV realization"
        or metric.get("twist_cover_degree") != [5, 7, 1]
        or metric.get("twist_status") != (
            "declared mathematical candidate; no metric modulus selected"
        )
        or metric.get("equation_degrees_x_u_base") != [[3, 0, 1], [0, 3, 1]]
        or metric.get("deck_coordinate_commutators") != ["-1-omega", "-1-omega", "1"]
        or metric.get("twist_descends_by_commuting_lifts") is not True
        or metric.get("prerequisite_artifact_digests") != {
            "alternate_cone": alternate_cone_digest,
            "alternate_carrier": alternate_carrier_digest,
            "first_constituent_arrows": first_arrows_digest,
        }
        or [(item.get("role"), item.get("twisted_degree"), item.get("cover_h0"))
            for item in metric_lines] != [
                ("A", [4, 8, 0], 612),
                *( ("F0", [2, 8, 2], 558) for _ in range(3) ),
                *( ("F1", [1, 8, 2], 279) for _ in range(2) ),
            ]
        or metric.get("cover_h0_first_constituent") != 1728
        or metric.get("cover_h1_to_h3_first_constituent") != [0, 0, 0]
        or metric.get("quotient_h0_first_constituent") != 192
        or metric.get("quotient_h1_first_constituent") != 0
        or metric.get("subline_koszul_higher_transgression_rank") != 63
        or metric.get("ambient_first_page_alone_incomplete_for_subline") is not True
        or metric.get("cover_global_generation_first_constituent") is not True
        or metric.get("quotient_global_generation_first_constituent_certified") is not False
        or metric.get("individual_f0_ambient_lifts_commute") is not False
        or [item.get("ambient_line_deck_commutator") for item in metric_lines]
        != ["1", "-1-omega", "-1-omega", "-1-omega", "1", "1"]
        or [item.get("ambient_nonnegative_and_cover_generated") for item in metric_lines[:4]]
        != [True, True, True, True]
        or metric.get("result_independent_of_outer_extension_parameter") is not True
        or any(metric.get(flag) is not False for flag in (
            "global_generation_of_constituents_certified",
            "rank_four_global_generation_certified", "numerical_metrics_available",
            "physical_yukawas_available", "observational_inputs_used",
        ))
    ):
        raise ValueError("the alternate metric subbundle vanishing or its scope is not certified")
    generation_path = ROOT / (
        "data/generated/scientific_genesis/alternate_metric_quotient_generation.json"
    )
    generation = json.loads(generation_path.read_text(encoding="utf-8"))
    generation_digest = generation.pop("artifact_digest", None)
    if (
        generation_digest != _canonical_digest(generation)
        or generation_digest != "3ca16bfa116c6b5530d73e74486eb196d37dbf9c0f7e75d445e84c41176fe063"
        or generation.get("schema") != "alternate-metric-quotient-generation-v2"
        or generation.get("base_twist_cover_degree") != [5, 7, 1]
        or generation.get("orbit_separator_cover_degree") != [9, 9, 0]
        or generation.get("generating_twist_cover_degree") != [14, 16, 1]
        or generation.get("free_deck_orbit_size") != 9
        or generation.get("projected_orbit_action_free") is not True
        or generation.get("projected_fiber_type") != "empty, point, or the full projective line"
        or generation.get("ambient_multihomogeneous_separation_bound_per_p2_factor") != 8
        or generation.get("right_serre_subline_base_degree") != [6, 6, 0]
        or generation.get("right_serre_subline_base_h0") != 684
        or generation.get("right_hilbert_burch_source_base_degrees") != [[6, 3, 2]] * 4
        or generation.get("cover_h0_constituents_at_generating_twist") != [23895, 24210]
        or generation.get("quotient_h0_constituents_at_generating_twist") != [2655, 2690]
        or generation.get("quotient_h0_rank_four_at_generating_twist") != 5345
        or generation.get("prerequisite_artifact_digests") != {
            "first_constituent": metric_digest,
            "alternate_cone": alternate_cone_digest,
            "alternate_carrier": alternate_carrier_digest,
        }
        or any(generation.get(flag) is not True for flag in (
            "first_constituent_cover_generated_at_base_twist",
            "right_constituent_cover_generated_at_base_twist",
            "orbit_separator_descends",
            "first_constituent_h1_vanishes_at_generating_twist",
            "both_constituents_quotient_generated_at_generating_twist",
            "rank_four_quotient_generated_for_all_alternate_p1",
        ))
        or any(generation.get(flag) is not False for flag in (
            "generation_at_base_twist_certified",
            "explicit_invariant_section_basis_constructed",
            "numerical_metrics_available", "physical_yukawas_available",
            "observational_inputs_used",
        ))
    ):
        raise ValueError("the alternate quotient-generation theorem or scope is not certified")
    subline_path = ROOT / (
        "data/generated/scientific_genesis/alternate_metric_first_subline_sections.json"
    )
    subline = json.loads(subline_path.read_text(encoding="utf-8"))
    subline_digest = subline.pop("artifact_digest", None)
    if (
        subline_digest != _canonical_digest(subline)
        or subline_digest != "73b91e7f16496bc32f5bd03903edd6d06fb0e6dc9dd8b13811ccd62f4fff5a73"
        or subline.get("schema") != "alternate-metric-first-subline-sections-v1"
        or subline.get("twisted_subline_cover_degree") != [13, 17, 0]
        or subline.get("metric_twist_linearization")
        != "natural commuting ambient P/T coordinate lifts"
        or subline.get("actual_subline_frame_p_t") != ["1", "-1-omega"]
        or subline.get("projected_eliminant_bidegree") != [3, 3]
        or subline.get("projected_eliminant_deck_invariant") is not True
        or subline.get("ambient_invariant_orbit_count") != 1995
        or subline.get("ideal_invariant_orbit_count") != 880
        or subline.get("ideal_inclusion_rank") != 880
        or subline.get("quotient_subline_section_count") != 1115
        or len(subline.get("quotient_basis_monomials_x_u", [])) != 1115
        or subline.get("prerequisite_artifact_digests") != {
            "generation": generation_digest,
            "alternate_cone": alternate_cone_digest,
        }
        or any(subline.get(flag) is not False for flag in (
            "full_constituent_section_basis_available",
            "rank_four_section_basis_available", "numerical_metrics_available",
            "observational_inputs_used",
        ))
    ):
        raise ValueError("the actual first-subline section basis or scope is not certified")
    ambient_path = ROOT / (
        "data/generated/scientific_genesis/alternate_metric_first_resolution_ambient_sections.json"
    )
    ambient_sections = json.loads(ambient_path.read_text(encoding="utf-8"))
    ambient_digest = ambient_sections.pop("artifact_digest", None)
    ambient_blocks = ambient_sections.get("blocks", [])
    if (
        ambient_digest != _canonical_digest(ambient_sections)
        or ambient_digest != "c2c097a2e7a32f9fa44ba1e665756cb6cf5fb7856c57b0774039faec313511ff"
        or ambient_sections.get("schema")
        != "alternate-metric-first-resolution-ambient-sections-v1"
        or ambient_sections.get("twist_cover_degree") != [14, 16, 1]
        or ambient_sections.get("common_flat_character_twist") != [1, 2]
        or ambient_sections.get("twist_linearization")
        != "natural commuting ambient P/T coordinate lifts"
        or [item.get("role") for item in ambient_blocks] != ["F0", "F1"]
        or [item.get("ambient_invariant_generator_count") for item in ambient_blocks]
        != [13338, 7524]
        or any(item.get("both_generators_fix_every_section") is not True
               for item in ambient_blocks)
        or ambient_sections.get("prerequisite_artifact_digests") != {
            "generation": generation_digest,
            "alternate_cone": alternate_cone_digest,
        }
        or any(ambient_sections.get(flag) is not False for flag in (
            "individual_f0_lines_descended",
            "restricted_hilbert_burch_quotient_basis_available",
            "first_constituent_section_basis_available",
            "numerical_metrics_available", "observational_inputs_used",
        ))
    ):
        raise ValueError("the actual ambient resolution sections or scope are not certified")
    first_quotient_path = ROOT / (
        "data/generated/scientific_genesis/alternate_metric_first_quotient_sections.json"
    )
    first_quotient = json.loads(first_quotient_path.read_text(encoding="utf-8"))
    first_quotient_digest = first_quotient.pop("artifact_digest", None)
    if (
        first_quotient_digest != _canonical_digest(first_quotient)
        or first_quotient_digest
        != "d6d1473742b89707284f86ad65a52deac89d5d15e26fbb9f94887f679c448824"
        or first_quotient.get("schema") != "alternate-metric-first-quotient-sections-v1"
        or first_quotient.get("twist_cover_degree") != [14, 16, 1]
        or first_quotient.get("ideal_image_degree") != [13, 17, 2]
        or first_quotient.get("actual_ideal_image_frame_p_t_exponents") != [2, 2]
        or first_quotient.get("ambient_ideal_invariant_dimension") != 5814
        or first_quotient.get("ideal_koszul_source_dimensions") != [2394, 2720]
        or first_quotient.get("ideal_koszul_syzygy_dimension") != 840
        or first_quotient.get("structural_relation_rank_upper_bound") != 4274
        or first_quotient.get("certified_relation_minor_rank") != 4274
        or first_quotient.get("certificate_prime") != 7
        or first_quotient.get("certificate_omega_residue") != 2
        or first_quotient.get("quotient_section_dimension") != 1540
        or len(first_quotient.get("quotient_basis_canonical_monomials", [])) != 1540
        or first_quotient.get("relation_archive") != (
            "data/generated/scientific_genesis/"
            "alternate_metric_first_quotient_sections.relations.json.gz"
        )
        or _sha256(ROOT / first_quotient["relation_archive"])
        != first_quotient.get("relation_archive_sha256")
        or first_quotient.get("prerequisite_artifact_digests") != {
            "ambient": ambient_digest, "generation": generation_digest,
        }
        or any(first_quotient.get(flag) is not True for flag in (
            "hilbert_burch_ideal_identification_equivariant",
            "exact_equation_images_in_invariant_span",
            "schoen_sequence_regular_on_coordinate_axis_quotient",
        ))
        or any(first_quotient.get(flag) is not False for flag in (
            "serre_lifts_constructed", "full_constituent_section_basis_available",
            "rank_four_section_basis_available", "numerical_metrics_available",
            "physical_yukawas_available", "observational_inputs_used",
        ))
    ):
        raise ValueError("the actual first Serre quotient basis or scope is not certified")
    first_lifts_path = ROOT / (
        "data/generated/scientific_genesis/alternate_metric_first_serre_lifts.json"
    )
    first_lifts = json.loads(first_lifts_path.read_text(encoding="utf-8"))
    first_lifts_digest = first_lifts.pop("artifact_digest", None)
    if (
        first_lifts_digest != _canonical_digest(first_lifts)
        or first_lifts_digest
        != "1a41b4cff18fb878b800f8f55609535d619186a55ae0861f101e6dcfe9667b0d"
        or first_lifts.get("schema") != "alternate-metric-first-serre-lifts-v1"
        or first_lifts.get("twist_cover_degree") != [14, 16, 1]
        or first_lifts.get("common_flat_character_twist") != [1, 2]
        or first_lifts.get("section_dimension") != 2655
        or first_lifts.get("subline_section_count") != 1115
        or first_lifts.get("quotient_lift_count") != 1540
        or first_lifts.get("full_differential_template_count") != 9
        or first_lifts.get("expanded_full_cover_term_count") != 226530
        or first_lifts.get("coefficient_ring") != "Z[omega], omega^2+omega+1=0"
        or first_lifts.get("section_archive") != (
            "data/generated/scientific_genesis/"
            "alternate_metric_first_serre_lifts.sections.json.gz"
        )
        or _sha256(ROOT / first_lifts["section_archive"])
        != first_lifts.get("section_archive_sha256")
        or first_lifts.get("prerequisite_artifact_digests") != {
            "subline": subline_digest, "quotient": first_quotient_digest,
            "generation": generation_digest,
        }
        or any(first_lifts.get(flag) is not True for flag in (
            "all_sections_full_differential_closed", "all_sections_strictly_p_t_invariant",
            "first_constituent_section_basis_available",
        ))
        or any(first_lifts.get(flag) is not False for flag in (
            "second_constituent_section_basis_available", "rank_four_section_basis_available",
            "numerical_metrics_available", "physical_yukawas_available",
            "observational_inputs_used",
        ))
    ):
        raise ValueError("the actual complete first-constituent section basis is not certified")
    second_sections_path = ROOT / (
        "data/generated/scientific_genesis/alternate_metric_second_sections.json"
    )
    second_sections = json.loads(second_sections_path.read_text(encoding="utf-8"))
    second_digest = second_sections.pop("artifact_digest", None)
    second_a = second_sections.get("subline_certificate", {})
    second_q = second_sections.get("quotient_certificate", {})
    if (
        second_digest != _canonical_digest(second_sections)
        or second_digest
        != "82fc3dfec203d767ab0741b26befec46d076178c06323e1f7c8bf70643317348"
        or second_sections.get("schema") != "alternate-metric-second-sections-v1"
        or second_sections.get("ray_character_exponents") != [0, 1]
        or second_sections.get("common_flat_character_twist") != [1, 2]
        or second_sections.get("twist_cover_degree") != [14, 16, 1]
        or second_sections.get("subline_degree") != [15, 15, 0]
        or second_sections.get("ideal_degree") != [15, 15, 2]
        or second_sections.get("subline_frame_exponents") != [0, 0]
        or second_sections.get("ideal_frame_exponents") != [1, 2]
        or second_sections.get("section_dimension") != 2690
        or second_sections.get("subline_section_count") != 1135
        or second_sections.get("quotient_lift_count") != 1555
        or second_sections.get("subline_fixed_orbit_counts") != [1, 1]
        or second_sections.get("full_differential_template_count") != 12
        or second_sections.get("expanded_full_cover_term_count") != 271035
        or second_a.get("target_dimension") != 2056
        or second_a.get("source_dimensions") != [921]
        or second_a.get("certified_rank") != 921
        or len(second_a.get("basis_labels", [])) != 1135
        or second_q.get("target_dimension") != 5892
        or second_q.get("source_dimensions") != [2628, 2568]
        or second_q.get("syzygy_dimension") != 859
        or second_q.get("certified_rank") != 4337
        or second_q.get("structural_relation_rank_upper_bound") != 4337
        or second_q.get("source_frame_exponents") != [[0, 2], [1, 2]]
        or second_q.get("syzygy_frame_exponents") != [0, 2]
        or len(second_q.get("basis_labels", [])) != 1555
        or second_sections.get("prerequisite_artifact_digests") != {
            "generation": generation_digest, "alternate_cone": alternate_cone_digest,
        }
        or any(second_sections.get(f"{name}_archive") != (
            "data/generated/scientific_genesis/"
            f"alternate_metric_second_sections.{suffix}.json.gz"
        ) or _sha256(ROOT / second_sections[f"{name}_archive"])
            != second_sections.get(f"{name}_archive_sha256")
               for name, suffix in (("section", "sections"), ("relation", "relations")))
        or any(second_sections.get(flag) is not True for flag in (
            "ideal_koszul_regular_sequence_on_fat_axis_quotient",
            "actual_ideal_frame_source_checked",
            "all_sections_full_differential_closed", "all_sections_strictly_p_t_invariant",
            "second_constituent_section_basis_available",
        ))
        or any(second_sections.get(flag) is not False for flag in (
            "rank_four_section_basis_available", "numerical_metrics_available",
            "physical_yukawas_available", "observational_inputs_used",
        ))
    ):
        raise ValueError("the actual complete second-constituent section basis is not certified")
    outer_lifts = json.loads((ROOT / (
        "data/generated/scientific_genesis/alternate_metric_outer_lifts.json"
    )).read_text(encoding="utf-8"))
    outer_lifts_digest = outer_lifts.pop("artifact_digest", None)
    outer_structure = outer_lifts.get("structural_certificate", {})
    if (
        outer_lifts_digest != _canonical_digest(outer_lifts)
        or outer_lifts_digest
        != "3708b3f7757ec12080daa98d09315ed53a2c7d0e0ead61ff3a55777bb00aaa4c"
        or outer_lifts.get("schema") != "alternate-metric-outer-lift-formula-v1"
        or outer_lifts.get("parameter_basis") != ["a0", "a1"]
        or outer_lifts.get("basis_dimension") != 5345
        or outer_lifts.get("universal_section_constructor_available") is not True
        or outer_lifts.get("prerequisite_artifact_digests") != {
            "first": first_lifts_digest, "second": second_digest,
            "invariants": alternate_invariants_digest, "cone": alternate_cone_digest,
        }
        or outer_structure.get("raw_reduced_degree_one_dimension") != 0
        or outer_structure.get("h_delta_nilpotence_bound") != 5
        or outer_structure.get("raw_reduced_dimensions") != [
            [-3, 8640], [-2, 72504], [-1, 177966], [0, 137997],
        ]
        or len(outer_structure.get("component_profiles", [])) != 24
        or len(outer_lifts.get("actual_coefficient_probes", [])) != 2
        or [p.get("second_basis_index") for p in outer_lifts.get("actual_coefficient_probes", [])]
        != [0, 1135]
        or any(
            p.get("all_coefficientwise_cone_identities_exact") is not True
            or p.get("all_corrections_strictly_invariant") is not True
            or len(p.get("coefficient_digests", [])) != 2
            or len(p.get("coefficient_term_counts", [])) != 2
            for p in outer_lifts.get("actual_coefficient_probes", [])
        )
        or any(outer_lifts.get(flag) is not False for flag in (
            "complete_independent_rank_four_basis_replay", "rank_four_section_basis_available",
            "numerical_metrics_available", "physical_yukawas_available",
            "extension_point_selected", "observational_inputs_used",
        ))
    ):
        raise ValueError("the finite universal outer lifting formula or scope is not certified")
    lift_operator = json.loads((ROOT / (
        "data/generated/scientific_genesis/alternate_metric_lift_operator_certificate.json"
    )).read_text(encoding="utf-8"))
    lift_operator_digest = lift_operator.pop("artifact_digest", None)
    raw_operator = lift_operator.get("raw_contraction", {})
    module_operator = lift_operator.get("outer_composition", {})
    averaging = lift_operator.get("repaired_averaging", {})
    if (
        lift_operator_digest != _canonical_digest(lift_operator)
        or lift_operator_digest
        != "6870cdf9bc875777e8ded58e6b434d865204b8aa9aa69c6194e5b5463d55eb82"
        or lift_operator.get("schema") != "alternate-metric-lift-operator-certificate-v1"
        or lift_operator.get("outer_lift_artifact_digest") != outer_lifts_digest
        or raw_operator.get("support_pattern_count") != 256
        or raw_operator.get("verified_basis_column_count") != 10816
        or raw_operator.get("structural_parities") != [0, 1]
        or any(raw_operator.get(flag) is not True for flag in (
            "d_h_plus_h_d_equals_identity_minus_Q", "h_squared_zero", "Q_h_and_h_Q_zero",
            "Q_squared_equals_Q", "d_Q_and_Q_d_zero",
            "observed_raw_d_matches_independent_incidence",
        ))
        or module_operator.get("verified_module_column_count") != 20
        or module_operator.get("source_basis_count") != 2690
        or module_operator.get("all_saved_V2_sections_in_declared_module") is not True
        or module_operator.get("D1_E_plus_E_D2_zero_on_entire_section_module") is not True
        or [
            (c.get("source_object"), c.get("p1_chart"), c.get("parameter"))
            for c in module_operator.get("columns", [])
        ] != [(i, c, p) for i in range(5) for c in range(2) for p in range(2)]
        or any(c.get("D1_E_plus_E_D2_zero") is not True
               or c.get("constructor_product_matches_independent_suffix_operator") is not True
               for c in module_operator.get("columns", []))
        or averaging.get("all_24_homogeneous_components_satisfy_group_relations") is not True
        or averaging.get("Schoen_equation_units_independently_reconstructed") is not True
        or averaging.get("independent_coordinate_relations", {}).get(
            "commutation_phase_depends_only_on_multidegree"
        ) is not True
        or averaging.get("actual_target_operator", {}).get(
            "all_resolution_and_extension_arrows_P_and_T_fixed"
        ) is not True
        or any(lift_operator.get(flag) is not True for flag in (
            "closed_degree_one_residual_primitive_rule_certified",
            "all_outer_section_products_independently_certified",
            "full_universal_lift_formula_certified", "rank_four_section_basis_available",
        ))
        or any(lift_operator.get(flag) is not False for flag in (
            "complete_expanded_coefficient_replay", "numerical_metrics_available",
            "physical_yukawas_available", "extension_point_selected", "observational_inputs_used",
        ))
    ):
        raise ValueError("the independent universal lift operator certificate is not certified")
    fiber_evaluation = json.loads((ROOT / (
        "data/generated/scientific_genesis/alternate_metric_fiber_evaluation.json"
    )).read_text(encoding="utf-8"))
    fiber_digest = fiber_evaluation.pop("artifact_digest", None)
    if (
        fiber_digest != _canonical_digest(fiber_evaluation)
        or fiber_digest != "8b603ad5bcd0c9ecf557521036c5636e35d9c8ec214f2a26750d44bd32588c86"
        or fiber_evaluation.get("schema") != "alternate-metric-fiber-evaluation-v1"
        or fiber_evaluation.get("prerequisite_artifact_digests", {}).get("lift_certificate")
        != lift_operator_digest
        or fiber_evaluation.get("parameter_basis") != ["a0", "a1"]
        or fiber_evaluation.get("generating_twist_cover_degree") != [14, 16, 1]
        or fiber_evaluation.get("point") != {
            "x": ["1", "-1", "0"], "u": ["1", "1", "1"],
            "p": ["0", "1"], "chart": [0, 0, 1],
        }
        or fiber_evaluation.get("first_pivot_rows") != [0, 2]
        or fiber_evaluation.get("second_pivot_rows") != [0, 1, 2]
        or len(fiber_evaluation.get("fiber_basis_labels", [])) != 4
        or fiber_evaluation.get("actual_basis_indices") != [0, 1273, 2670, 3973]
        or fiber_evaluation.get("actual_section_determinant_all_parameters") != "1/81"
        or any(fiber_evaluation.get(field) in (None, "0") for field in (
            "relation_minor_all_parameters", "actual_section_determinant_all_parameters",
        ))
        or any(fiber_evaluation.get(flag) is not True for flag in (
            "local_rank_four_evaluator_available",
            "all_parameter_boundary_quotient_identities_exact",
            "actual_four_section_spanning_probe_exact",
        ))
        or any(fiber_evaluation.get(flag) is not False for flag in (
            "complete_5345_column_point_matrix_materialized", "numerical_metrics_available",
            "physical_yukawas_available", "extension_point_selected", "observational_inputs_used",
        ))
    ):
        raise ValueError("the actual local rank-four fiber evaluation or scope is not certified")
    specialized = json.loads((ROOT / (
        "data/generated/scientific_genesis/alternate_metric_specialized_evaluation.json"
    )).read_text(encoding="utf-8"))
    specialized_digest = specialized.pop("artifact_digest", None)
    if (
        specialized_digest != _canonical_digest(specialized)
        or specialized_digest != "3c08c1e994c3815f27800ebced9cec2dd6ee9262118d559f5e91d4950dfeb72f"
        or specialized.get("schema") != "alternate-metric-specialized-evaluation-v1"
        or specialized.get("fiber_evaluation_artifact_digest") != fiber_digest
        or specialized.get("parameter_basis") != ["a0", "a1"]
        or specialized.get("point") != fiber_evaluation.get("point")
        or specialized.get("fiber_basis_labels") != fiber_evaluation.get("fiber_basis_labels")
        or specialized.get("first_pivot_rows") != fiber_evaluation.get("first_pivot_rows")
        or specialized.get("second_pivot_rows") != fiber_evaluation.get("second_pivot_rows")
        or specialized.get("prerequisite_artifact_digests") != {
            key: value for key, value in fiber_evaluation["prerequisite_artifact_digests"].items()
            if key != "lift_certificate"
        }
        or specialized.get("section_count") != 5345
        or specialized.get("fiber_dimension") != 4
        or specialized.get("independent_full_cochain_probe_indices") != [0, 1273, 2670, 3973]
        or specialized.get("actual_spanning_minor_all_parameters") != "1/81"
        or specialized.get("all_probe_coefficients_match_full_cochain_evaluation") is not True
        or specialized.get("complete_5345_column_point_matrix_materialized") is not True
        or specialized.get("regularity_premises") != {
            "target_components_checked": 24,
            "all_target_second_plane_ambient_degrees_nonnegative": True,
            "all_actual_object_arrows_polynomial_in_both_planes": True,
            "both_outer_coefficients_second_plane_regular": True,
            "Koszul_equations_polynomial_in_both_planes": True,
            "series_length_bound": 5,
        }
        or any(specialized.get(flag) is not False for flag in (
            "controlled_numerical_sampling_available", "numerical_metrics_available",
            "physical_yukawas_available", "extension_point_selected", "observational_inputs_used",
        ))
    ):
        raise ValueError("the complete exact section evaluation or scope is not certified")
    matrix_path = ROOT / (
        "data/generated/scientific_genesis/alternate_metric_specialized_evaluation.matrix.json.gz"
    )
    matrix_archive = matrix_path.read_bytes()
    matrix_raw = gzip.decompress(matrix_archive)
    matrix_columns = json.loads(matrix_raw)
    if (
        specialized.get("matrix_archive") != str(matrix_path.relative_to(ROOT))
        or specialized.get("matrix_archive_sha256") != hashlib.sha256(matrix_archive).hexdigest()
        or specialized.get("exact_column_stream_sha256") != hashlib.sha256(matrix_raw).hexdigest()
        or len(matrix_columns) != 5345
        or any(len(c) != 3 or any(len(m) != 4 or any(len(row) != 1 for row in m)
                                 for m in c) for c in matrix_columns)
        or any(matrix_columns[index][p] != [
            [fiber_evaluation["actual_section_coefficients_constant_a0_a1"][p][r][col]]
            for r in range(4)
        ] for col, index in enumerate([0, 1273, 2670, 3973]) for p in range(3))
    ):
        raise ValueError("the complete section column stream is not certified")
    measure_record = json.loads((ROOT / (
        "data/generated/scientific_genesis/alternate_metric_measure.json"
    )).read_text(encoding="utf-8"))
    measure_digest = measure_record.pop("artifact_digest", None)
    if (
        measure_digest != _canonical_digest(measure_record)
        or measure_digest != "eefa94d3f7b368cc13f4bad2659393129063345ef97097a9e7e0db32ad1ac488"
        or measure_record.get("schema") != "alternate-metric-measure-v1"
        or measure_record.get("actual_equations")
        != ["mu*F(x)+nu*G(x)", "2*nu*F(u)+mu*G(u)"]
        or measure_record.get("auxiliary_cover_mass") != "9"
        or measure_record.get("covering_degree") != 9
        or measure_record.get("deck_residue_characters") != {"P": "1", "T": "1"}
        or measure_record.get("exact_residue_and_auxiliary_measure_available") is not True
        or any(measure_record.get(flag) is not False for flag in (
            "controlled_numerical_sampling_available", "numerical_metrics_available",
            "physical_yukawas_available", "extension_point_selected", "vacuum_selected",
            "observational_inputs_used",
        ))
    ):
        raise ValueError("the exact geometric measure or its scientific scope is not certified")
    moment_record = json.loads((ROOT / (
        "data/generated/scientific_genesis/alternate_metric_weight_moments.json"
    )).read_text(encoding="utf-8"))
    moment_digest = moment_record.pop("artifact_digest", None)
    if (
        moment_digest != _canonical_digest(moment_record)
        or moment_digest != "bae6172a3208f92f6bd954c8a4124bfce84da09cf08a2d66dc44e7305165ee41"
        or moment_record.get("schema") != "alternate-metric-weight-moments-v1"
        or moment_record.get("measure_artifact_digest") != measure_digest
        or moment_record.get("actual_equations") != measure_record.get("actual_equations")
        or moment_record.get("proof") != (
            "research/experiments/scientific_genesis/ALTERNATE_METRIC_WEIGHT_MOMENTS_NOTE.md"
        )
        or moment_record.get("proof_sha256") != _sha256(ROOT / (
            "research/experiments/scientific_genesis/ALTERNATE_METRIC_WEIGHT_MOMENTS_NOTE.md"
        ))
        or moment_record.get("two_critical_supports_gcd_degree") != 0
        or moment_record.get("critical_infinity_fibers") is not False
        or len(moment_record.get("pencils", [])) != 2
        or any(p.get("critical_support_degree") != 6
               or p.get("squarefree_gcd_degree") != 0
               or p.get("axis_nodal_fiber_count") != 3
               or p.get("triangle_fiber_count") != 3
               or p.get("nodal_critical_point_count") != 12
               for p in moment_record.get("pencils", []))
        or moment_record.get("weight_second_moment_finite") is not True
        or moment_record.get("weight_third_moment_finite") is not False
        or moment_record.get("nonnegative_moment_integrability")
        != "finite exactly for 0 <= q < 3"
        or any(moment_record.get(flag) is not False for flag in (
            "quantitative_variance_bound_available",
            "standard_finite_third_absolute_moment_error_bound_applicable_to_weight",
            "controlled_numerical_sampling_available", "numerical_metrics_available",
            "physical_yukawas_available", "extension_point_selected", "vacuum_selected",
            "observational_inputs_used",
        ))
    ):
        raise ValueError("the actual weight integrability or its scientific scope is not certified")
    positive_record = json.loads((ROOT / (
        "data/generated/scientific_genesis/alternate_metric_positive_measure.json"
    )).read_text(encoding="utf-8"))
    positive_digest = positive_record.pop("artifact_digest", None)
    if (
        positive_digest != _canonical_digest(positive_record)
        or positive_digest != "c95486f83301f30fe55906ae773981d3a18d5662b56587de769f9744638cd66e"
        or positive_record.get("schema") != "alternate-metric-positive-measure-v1"
        or positive_record.get("measure_artifact_digest") != measure_digest
        or positive_record.get("moment_artifact_digest") != moment_digest
        or positive_record.get("root_artifact_digest")
        != "cc160262ba3ca6d389c28b1ea2b42c49372d5e47ce90af93ab00ab60cab6ebdf"
        or positive_record.get("proof") != (
            "research/experiments/scientific_genesis/ALTERNATE_METRIC_POSITIVE_MEASURE_NOTE.md"
        )
        or positive_record.get("proof_sha256") != _sha256(ROOT / (
            "research/experiments/scientific_genesis/ALTERNATE_METRIC_POSITIVE_MEASURE_NOTE.md"
        ))
        or positive_record.get("positive_cover_mass") != "72"
        or positive_record.get("component_masses") != ["9", "3", "3"]
        or positive_record.get("component_probabilities") != ["3/4", "1/8", "1/8"]
        or positive_record.get("component_root_counts") != [9, 3, 3]
        or positive_record.get("bound_bits") != 80
        or positive_record.get("covering_degree") != 9
        or [p.get("side") for p in positive_record.get("actual_three_root_branch_probes", [])]
        != [1, 2]
        or any(p.get("partner_root_certificate", {}).get("total_root_count") != 3
               for p in positive_record.get("actual_three_root_branch_probes", []))
        or [c.get("name") for c in positive_record.get("actual_configurations", [])]
        != ["finite_chart", "infinity_branch"]
        or any(len(c.get("all_nine_positive_densities", [])) != 9
               or any(Fraction(p["positive_density_times_pi_cubed"][0]) <= 0
                      for p in c.get("all_nine_positive_densities", []))
               for c in positive_record.get("actual_configurations", []))
        or any(positive_record.get(flag) is not True for flag in (
            "positive_auxiliary_law_derived", "ideal_weight_globally_bounded",
            "all_nonnegative_weight_moments_finite",
            "regular_chart_positive_density_enclosures_available",
        ))
        or any(positive_record.get(flag) is not False for flag in (
            "quantitative_global_weight_bound_available",
            "critical_fiber_chart_enclosures_available",
            "controlled_numerical_sampling_available", "numerical_metrics_available",
            "physical_yukawas_available", "extension_point_selected", "vacuum_selected",
            "physical_kahler_class_selected", "observational_inputs_used",
        ))
    ):
        raise ValueError("the positive auxiliary law or its scientific scope is not certified")
    critical_record = json.loads((ROOT / (
        "data/generated/scientific_genesis/alternate_metric_critical_charts.json"
    )).read_text(encoding="utf-8"))
    critical_digest = critical_record.pop("artifact_digest", None)
    if (
        critical_digest != _canonical_digest(critical_record)
        or critical_digest != "b40ff532135437c7e0ff1bb041a1cd26696303ea721e3ed108c6a04c029a7504"
        or critical_record.get("schema") != "alternate-metric-critical-charts-v1"
        or critical_record.get("positive_measure_artifact_digest") != positive_digest
        or critical_record.get("moment_artifact_digest") != moment_digest
        or critical_record.get("proof") != (
            "research/experiments/scientific_genesis/ALTERNATE_METRIC_CRITICAL_CHARTS_NOTE.md"
        )
        or critical_record.get("proof_sha256") != _sha256(ROOT / (
            "research/experiments/scientific_genesis/ALTERNATE_METRIC_CRITICAL_CHARTS_NOTE.md"
        ))
        or critical_record.get("ambient_coordinate_order") != ["s", "z", "r", "w", "t"]
        or critical_record.get("free_coordinate_orders")
        != {"1": ["s", "z", "r"], "2": ["r", "w", "s"]}
        or critical_record.get("wedge_jacobian_rules") != {"1": "-f_t*g_w", "2": "f_z*g_t"}
        or critical_record.get("partner_line") != [[1, 0, 0], [0, 1, 1]]
        or critical_record.get("root_policy") != {
            "requested_radius": "1/1073741824", "coefficient_bits": 60,
            "modulus_bound_bits": 80, "max_iterations": 128, "parameter_pivot": 0,
        }
        or critical_record.get("bound_bits") != 80
        or critical_record.get("covering_degree") != 9
        or [(p.get("source_side"), p.get("source_axis"))
            for p in critical_record.get("actual_axis_fiber_probes", [])]
        != [(s, a) for s in (1, 2) for a in range(3)]
        or any(p.get("partner_root_certificate", {}).get("total_root_count") != 3
               or len(p.get("all_three_critical_chart_records", [])) != 3
               or any(Fraction(r["positive_density_times_pi_cubed"][0]) <= 0
                      or Fraction(r["omega_density"][0]) <= 0
                      or r.get("free_coordinate_indices")
                      != ([0, 1, 2] if p["source_side"] == 1 else [2, 3, 0])
                      for r in p.get("all_three_critical_chart_records", []))
               for p in critical_record.get("actual_axis_fiber_probes", []))
        or any(critical_record.get(flag) is not True for flag in (
            "point_line_cover_membership_certified",
            "declared_critical_fiber_chart_enclosures_available",
        ))
        or any(critical_record.get(flag) is not False for flag in (
            "all_triangle_node_inputs_certified", "complete_global_atlas_coverage_certified",
            "quantitative_global_weight_bound_available", "controlled_numerical_sampling_available",
            "numerical_metrics_available", "physical_yukawas_available", "extension_point_selected",
            "vacuum_selected", "physical_kahler_class_selected", "observational_inputs_used",
        ))
    ):
        raise ValueError("the declared critical charts or their scientific scope is not certified")
    weight_record = json.loads((ROOT / (
        "data/generated/scientific_genesis/alternate_metric_projection_free_weights.json"
    )).read_text(encoding="utf-8"))
    weight_digest = weight_record.pop("artifact_digest", None)
    if (
        weight_digest != _canonical_digest(weight_record)
        or weight_digest != "cb4eb886edf94ab72b737bc8e3c23a25d2355243557fee40dfe62d24c7cf1e97"
        or weight_record.get("schema") != "alternate-metric-projection-free-weights-v1"
        or weight_record.get("positive_measure_artifact_digest") != positive_digest
        or weight_record.get("critical_chart_artifact_digest") != critical_digest
        or weight_record.get("moment_artifact_digest") != moment_digest
        or weight_record.get("proof") != (
            "research/experiments/scientific_genesis/ALTERNATE_METRIC_PROJECTION_FREE_WEIGHTS_NOTE.md"
        )
        or weight_record.get("proof_sha256") != _sha256(ROOT / (
            "research/experiments/scientific_genesis/ALTERNATE_METRIC_PROJECTION_FREE_WEIGHTS_NOTE.md"
        ))
        or weight_record.get("ambient_coordinate_order") != ["s", "z", "r", "w", "t"]
        or weight_record.get("denominator_rule") != "D=det(G)*det(J*inverse(G)*adjoint(J))"
        or weight_record.get("positive_conormal_rule") != "Ax*Au+Ax*Bp+Au*Ap"
        or weight_record.get("cover_weight_rule") != "72*norm(scale)/(6*D); pi^3 factored out"
        or weight_record.get("bound_bits") != 80
        or weight_record.get("covering_degree") != 9
        or weight_record.get("actual_domain_count") != 36
        or [(p.get("kind"), len(p.get("records", [])))
            for p in weight_record.get("actual_domain_probes", [])]
        != [("finite_chart", 9), ("infinity_branch", 9)] + [("axis_critical", 3)] * 6
        or [(p.get("source_side"), p.get("source_axis"))
            for p in weight_record.get("actual_domain_probes", [])[2:]]
        != [(s, a) for s in (1, 2) for a in range(3)]
        or any(Fraction(r["positive_denominator"][0]) <= 0
               or Fraction(r["cover_weight_without_pi_cubed"][0]) <= 0
               for p in weight_record.get("actual_domain_probes", []) for r in p.get("records", []))
        or any(weight_record.get(flag) is not True for flag in (
            "projection_free_weight_identity_derived",
            "weight_formula_valid_on_all_smooth_cover_charts",
            "declared_projection_free_weight_enclosures_available",
        ))
        or any(weight_record.get(flag) is not False for flag in (
            "individual_projection_inverses_required", "all_triangle_node_inputs_certified",
            "complete_global_input_coverage_certified",
            "quantitative_global_weight_bound_available",
            "controlled_numerical_sampling_available", "numerical_metrics_available",
            "physical_yukawas_available", "extension_point_selected", "vacuum_selected",
            "physical_kahler_class_selected", "observational_inputs_used",
        ))
    ):
        raise ValueError("the projection-free weights or their scientific scope are not certified")
    global_record = json.loads((ROOT / (
        "data/generated/scientific_genesis/alternate_metric_global_weight_bound.json"
    )).read_text(encoding="utf-8"))
    global_digest = global_record.pop("artifact_digest", None)
    if (
        global_digest != _canonical_digest(global_record)
        or global_digest != "96e3d216aa6157dab686069b095e304de5f7e9600348f42c00fff0691986c0f4"
        or global_record.get("schema") != "alternate-metric-global-weight-bound-v1"
        or global_record.get("projection_free_weight_artifact_digest") != weight_digest
        or global_record.get("moment_artifact_digest") != moment_digest
        or global_record.get("surface_coordinate_order") != ["x0", "x1", "x2", "mu", "nu"]
        or global_record.get("base_coordinate_order") != ["mu", "nu"]
        or global_record.get("normalized_volume_scale") != ["1", "0"]
        or global_record.get("covering_degree") != 9
        or global_record.get("conormal_lower_bound")
        != "12141615721/955235133932696537923584"
        or global_record.get("cover_weight_upper_without_pi_cubed")
        != "11462821607192358455083008/12141615721"
        or [(c.get("rows"), c.get("columns"), c.get("rank"), len(c.get("identities", [])))
            for c in global_record.get("surface_certificates", [])]
        != [(45, 54, 45, 6)] * 2
        or [len(c.get("identities", []))
            for c in global_record.get("fiber_gradient_certificates", [])] != [3, 3]
        or global_record.get("base_separation_certificate", {}).get("rank") != 12
        or global_record.get("proof") != (
            "research/experiments/scientific_genesis/ALTERNATE_METRIC_GLOBAL_WEIGHT_BOUND_NOTE.md"
        )
        or global_record.get("proof_sha256") != _sha256(ROOT / global_record["proof"])
        or any(global_record.get(flag) is not True for flag in (
            "full_polynomial_identities_verified", "quantitative_global_weight_bound_available",
            "quantitative_ideal_weight_variance_bound_available",
        ))
        or any(global_record.get(flag) is not False for flag in (
            "point_grid_used_as_proof", "practical_sampling_cost_certified",
            "controlled_numerical_sampling_available", "complete_global_input_coverage_certified",
            "matrix_integrand_bounds_available", "numerical_metrics_available",
            "physical_yukawas_available", "extension_point_selected",
            "physical_kahler_class_selected",
            "vacuum_selected", "observational_inputs_used",
        ))
    ):
        raise ValueError("the global auxiliary weight bound or its scope is not certified")
    root_record = json.loads((ROOT / (
        "data/generated/scientific_genesis/alternate_metric_projective_roots.json"
    )).read_text(encoding="utf-8"))
    root_digest = root_record.pop("artifact_digest", None)
    if (
        root_digest != _canonical_digest(root_record)
        or root_digest != "cc160262ba3ca6d389c28b1ea2b42c49372d5e47ce90af93ab00ab60cab6ebdf"
        or root_record.get("schema") != "alternate-metric-projective-roots-v1"
        or root_record.get("measure_artifact_digest") != measure_digest
        or root_record.get("coefficient_field") != "Q(omega), omega^2+omega+1=0"
        or root_record.get("exact_Qomega_input_intersection_roots_certified") is not True
        or [item.get("name") for item in root_record.get("actual_configurations", [])]
        != ["finite_chart", "infinity_branch"]
        or any(len(item.get("all_nine_root_pairs", [])) != 9
               or any(item[side].get("total_root_count") != 3 for side in ("first", "second"))
               for item in root_record.get("actual_configurations", []))
        or any(root_record.get(flag) is not False for flag in (
            "centers_are_exact_cover_points", "projective_uniform_sampling_law_implemented",
            "controlled_numerical_sampling_available",
            "bounded_section_and_density_evaluation_available",
            "numerical_metrics_available", "physical_yukawas_available",
            "extension_point_selected", "vacuum_selected", "observational_inputs_used",
        ))
    ):
        raise ValueError(
            "the certified projective roots or their scientific scope is not certified"
        )
    enclosures = json.loads((ROOT / (
        "data/generated/scientific_genesis/alternate_metric_enclosures.json"
    )).read_text(encoding="utf-8"))
    enclosure_digest = enclosures.pop("artifact_digest", None)
    if (
        enclosure_digest != _canonical_digest(enclosures)
        or enclosure_digest != "1c01dfa26f84061180030c386b2307a9cf7cb8566e77512a051b9c2d774e261d"
        or enclosures.get("schema") != "alternate-metric-enclosures-v1"
        or enclosures.get("root_artifact_digest") != root_digest
        or enclosures.get("section_prerequisite_artifact_digests")
        != specialized.get("prerequisite_artifact_digests")
        or enclosures.get("bound_bits") != 80
        or enclosures.get("covering_degree") != 9
        or enclosures.get("certified_chart_and_density_enclosures_available") is not True
        or enclosures.get("laurent_coefficient_enclosure_engine_available") is not True
        or [item.get("name") for item in enclosures.get("actual_configurations", [])]
        != ["finite_chart", "infinity_branch"]
        or any([row.get("root_pair") for row in item.get("all_nine_bounded_densities", [])]
               != root_record["actual_configurations"][i]["all_nine_root_pairs"]
               for i, item in enumerate(enclosures.get("actual_configurations", [])))
        or any(not 0 < Fraction(row[key][0]) <= Fraction(row[key][1])
               for item in enclosures.get("actual_configurations", [])
               for row in item.get("all_nine_bounded_densities", [])
               for key in ("omega_density", "auxiliary_density_times_pi_cubed",
                           "quotient_weight_without_pi_cubed"))
        or any([row.get("constituent_basis_index") for row in item.get(
            "constituent_coefficient_probe", {},
        ).get("actual_constituent_coefficients", [])] != [0, 1273, 15, 1318]
               for item in enclosures.get("actual_configurations", []))
        or any(enclosures.get(flag) is not False for flag in (
            "bounded_universal_fiber_frame_available", "centers_are_exact_cover_points",
            "bounded_section_and_density_evaluation_available",
            "controlled_numerical_sampling_available", "numerical_metrics_available",
            "physical_yukawas_available", "extension_point_selected", "vacuum_selected",
            "observational_inputs_used",
        ))
    ):
        raise ValueError("local enclosure inputs or their scientific scope are not certified")
    bounded_fibers = json.loads((ROOT / (
        "data/generated/scientific_genesis/alternate_metric_bounded_fibers.json"
    )).read_text(encoding="utf-8"))
    bounded_fiber_digest = bounded_fibers.pop("artifact_digest", None)
    if (
        bounded_fiber_digest != _canonical_digest(bounded_fibers)
        or bounded_fiber_digest
        != "d9e320a952cc6d5fc843ea2f9c0254823d8d9a49b8d6dbd1d2dda0dd2d61f01c"
        or bounded_fibers.get("schema") != "alternate-metric-bounded-fibers-v1"
        or bounded_fibers.get("enclosure_artifact_digest") != enclosure_digest
        or bounded_fibers.get("root_artifact_digest") != root_digest
        or bounded_fibers.get("original_fiber_evaluation_artifact_digest") != fiber_digest
        or bounded_fibers.get("parameter_basis") != ["a0", "a1"]
        or bounded_fibers.get("bound_bits") != 80
        or bounded_fibers.get("bounded_universal_fiber_frame_available") is not True
        or bounded_fibers.get("on_demand_original_cochain_section_bounds_available") is not True
        or [item.get("name") for item in bounded_fibers.get("actual_frame_probes", [])]
        != ["finite_chart", "infinity_branch"]
        or any(item.get("first_pivot_rows") != [0, 2]
               or item.get("second_pivot_rows") != [0, 1, 2]
               or item.get("fiber_basis_labels") != fiber_evaluation.get("fiber_basis_labels")
               or [p.get("basis_index") for p in item.get("actual_universal_section_probes", [])]
               != [0, 2655] for item in bounded_fibers.get("actual_frame_probes", []))
        or any(Fraction(item["relation_minor"]["center"][0])**2
               - Fraction(item["relation_minor"]["center"][0])
               * Fraction(item["relation_minor"]["center"][1])
               + Fraction(item["relation_minor"]["center"][1])**2
               <= Fraction(item["relation_minor"]["radius"])**2
               for item in bounded_fibers.get("actual_frame_probes", []))
        or any(bounded_fibers.get(flag) is not False for flag in (
            "complete_bounded_5345_column_matrix_materialized",
            "compressed_complete_section_enclosure_engine_available",
            "bounded_section_and_density_evaluation_available",
            "controlled_numerical_sampling_available", "numerical_metrics_available",
            "physical_yukawas_available", "extension_point_selected", "vacuum_selected",
            "observational_inputs_used",
        ))
    ):
        raise ValueError("bounded universal fibers or their scientific scope are not certified")
    bounded_support = json.loads((ROOT / (
        "data/generated/scientific_genesis/alternate_metric_bounded_support.json"
    )).read_text(encoding="utf-8"))
    bounded_support_digest = bounded_support.pop("artifact_digest", None)
    if (
        bounded_support_digest != _canonical_digest(bounded_support)
        or bounded_support_digest
        != "648135531c44d0790e19b42093b11786d8e5f387926e0dc0c261aea34f9940a8"
        or bounded_support.get("schema") != "alternate-metric-bounded-support-v1"
        or bounded_support.get("bounded_fiber_artifact_digest") != bounded_fiber_digest
        or bounded_support.get("root_artifact_digest") != root_digest
        or bounded_support.get("independent_exact_matrix_artifact_digest") != specialized_digest
        or bounded_support.get("independent_exact_matrix_archive_sha256")
        != specialized.get("matrix_archive_sha256")
        or bounded_support.get("parameter_basis") != ["a0", "a1"]
        or bounded_support.get("bound_bits") != 80
        or bounded_support.get("original_basis_count") != 5345
        or bounded_support.get("original_constituent_counts") != [2655, 2690]
        or bounded_support.get("filtration_length_bound") != 5
        or bounded_support.get("zero_policy")
        != "discard only exact center-zero radius-zero coefficients"
        or bounded_support.get("compressed_complete_section_enclosure_engine_available") is not True
        or [p.get("name") for p in bounded_support.get("actual_frame_probes", [])]
        != ["finite_chart", "infinity_branch"]
        or any(p.get("first_pivot_rows") != [0, 2]
               or p.get("second_pivot_rows") != [0, 1, 2]
               or p.get("fiber_basis_labels") != fiber_evaluation.get("fiber_basis_labels")
               or [s.get("basis_index") for s in p.get("actual_universal_section_probes", [])]
               != [0, 1273, 2655]
               or not p.get("observed_series_depths")
               or not all(type(d) is int and 0 <= d <= 5 for d in p["observed_series_depths"])
               for p in bounded_support.get("actual_frame_probes", []))
        or any(bounded_support.get(flag) is not False for flag in (
            "complete_bounded_5345_column_matrix_materialized",
            "practical_multi_point_integration_throughput_certified",
            "bounded_section_and_density_evaluation_available",
            "controlled_numerical_sampling_available", "numerical_metrics_available",
            "physical_yukawas_available", "extension_point_selected", "vacuum_selected",
            "observational_inputs_used",
        ))
    ):
        raise ValueError("bounded original support evaluation or its scope is not certified")
    # The completed execution is evidence only after consuming the actual archive.
    # This imports research from research, never into production.
    from . import alternate_metric_bounded_matrix as completed_matrix

    complete_matrix = completed_matrix.verify_completed_output(
        expected_digest="88cc1d553baa2a00a8f9c105d1ecab52d18d9c9a3e73042b617161253e09688a",
    )
    if (
        complete_matrix["matrix_archive_sha256"]
        != "3f0b600967c9b61d060c2c5d13f51d8b6e5e549bf50600ca6cd813d387e9afce"
        or complete_matrix["exact_column_stream_sha256"]
        != "88bc48fda6bdaed2368ece1f8394920a68bed0e04d318a0a5cbd7e0a6d57b53d"
        or complete_matrix["original_probe_indices_checked"] != [0, 1273, 2655]
    ):
        raise ValueError("completed bounded matrix execution is not independently certified")
    from . import alternate_neutrino_full_matrix as full_neutrino
    from . import alternate_neutrino_mixed_pairing as neutrino_mixed

    neutrino_matrix = full_neutrino.load_full_neutrino_matrix(
        expected_digest="40e5e45b6be980d49c432dbc707c496be56728731cd9b6f9d71d4cf08d8909eb",
    )
    if (neutrino_matrix.get("determinant")
        != [{"powers": [1, 0], "coefficient": "3/2+3/4*omega"}]
        or neutrino_matrix.get("rank_two_minor")
        != [{"powers": [0, 0], "coefficient": "-1/42-1/63*omega"}]):
        raise ValueError(
            "the independently replayed complete neutrino matrix changed its rank data",
        )

    neutrino_packet, _neutrino_witnesses = neutrino_mixed.load_mixed_pairing(
        expected_digest="1bc8020db27e9f7a3c7ee7a7abf4ab0c456903c993eab27b0038cad5e12e6049",
    )
    if (
        neutrino_packet["full_cochain_archive_sha256"]
        != "49bf7e7066fdfc46a87107f4e0a369bcffc1476d084490fcccffe552ae5a3cfd"
        or [item["cover_residue"] for item in neutrino_packet["evaluated_entries"]]
        != ["3*omega", "-3/2", "-3/14-9/14*omega", "3*omega"]
        or [item["seed_index"] for item in neutrino_packet["first_constituent_classes"]]
        != [0, 1]
        or [item["seed_index"] for item in neutrino_packet["second_constituent_classes"]]
        != [2, 4, 1, 3]
    ):
        raise ValueError("the actual neutrino mixed entries are not independently certified")
    from . import alternate_neutrino_ff_entries as neutrino_lifts
    from .mixed_schoen_outer_universal_cone import _verified_payload

    verified_lifts = (
        (0, 0, 1, 27001, 13071,
         "ffc2ff3bdab420bfc9b16ffd1892aa4b84c2896808f976a09ffbca604d6a1379"),
        (0, 0, 2, 26689, 12855,
         "7da302ec452f693ced8a436b29bed9402257428ce85576e2f36c9b0e3cbeab62"),
        (0, 1, 1, 27198, 12966,
         "ce0af7244b5be8a5d8786243f3378518826294cbb7ffabda2df5e7befe84037c"),
        (0, 1, 2, 27369, 13158,
         "fbde476e5e4e892988e9408ff454603da4afb1bc8f8396cbec9d8313921171be"),
        (1, 0, 1, 24016, 11397,
         "d20d9d68689a66e769a4c637efc8abb365fcb4021990dc021126302e8824004d"),
        (1, 0, 2, 23795, 11163,
         "4002b844a63e4a3de0d909f6b232bc4ad645ce7c835fdf4cbb733ef665ee8245"),
        (1, 1, 1, 23916, 11844,
         "ce3f70ba89af4e70b315a490401a734ecb2ce405b33eeb2d85167d545fdb27c8"),
        (1, 1, 2, 25441, 12294,
         "e26c664effe33ed3ca157b0d357062b119b24c3bbc08a3b74cde43cb15691bde"),
    )
    lift_parents = neutrino_lifts._inputs()[1]
    for parameter, side, family, e_terms, b_terms, expected_digest in verified_lifts:
        path = neutrino_lifts.lift_path(parameter, side, family)
        lift_digest, lift = _verified_payload(path)
        archive = path.with_suffix(".cochains.json.gz")
        witnesses = lift.get("witnesses", {})
        # The independent full-equation replay pins these literal packets.
        # A fresh ledger audit checks the exact metadata and archive bytes;
        # it does not redundantly rebuild every sparse cochain object.
        if (lift_digest != expected_digest
            or lift.get("schema") != "alternate-neutrino-ff-matter-lift-v1"
            or lift.get("prerequisite_artifact_digests") != lift_parents
            or (lift.get("parameter"), lift.get("side"), lift.get("family"))
            != (f"a{parameter}", side, family)
            or set(witnesses) != {"constant", "constituent_correction", "line_correction"}
            or witnesses.get("constituent_correction", {}).get("term_count") != e_terms
            or witnesses.get("line_correction", {}).get("term_count") != b_terms
            or lift.get("full_cochain_archive_name") != archive.name
            or _sha256(archive) != lift.get("full_cochain_archive_sha256")
            or lift.get("full_constituent_identity_exact") is not True
            or lift.get("full_pushout_identity_exact") is not True
            or lift.get("extension_point_selected") is not False):
            raise ValueError("the independently replayed actual neutrino matter lift changed")
    from . import alternate_down_higgs_hom_representative as down_hom

    down_packet, down_witness = down_hom.load_down_higgs_hom(
        expected_digest="476e48e981ab66382b43d2510d7a271b2fa3f82468f885b7050edb9af3cd9276",
    )
    if (down_packet.get("seed_index") != 1 or len(down_witness.terms) != 351
        or down_packet.get("cohomology_coordinates")
        != ["0", "1/3-1/3*omega", "0", "2/3+1/3*omega"]
        or down_packet.get("full_cochain_archive_sha256")
        != "7f03d8421c911ce0ad124b29a50ecc7e620f0e9df9f443c1b0a1d8a6a4ead1a2"):
        raise ValueError("the independently verified down-Higgs Hom input changed")
    from . import alternate_remaining_flavor_matter as remaining_flavor

    remaining_packet, remaining_witnesses = remaining_flavor.load_remaining_flavor_matter(
        expected_digest="363c8bc51e58fd6177943b89fdac08b760c5059bf09b1ba7e64b84414a53a8dc",
    )
    if (remaining_packet.get("full_cochain_archive_sha256")
        != "f51ad2e1ddfb1b9942af4104a5ed386fde0d1b67cff1abaf5d4812339d40f870"
        or [len(value.terms) for value in remaining_witnesses.values()]
        != [360, 360, 378, 378, 378, 378]):
        raise ValueError("the independently verified remaining flavor constituent inputs changed")
    from . import alternate_remaining_flavor_matter_lifts as remaining_lifts

    remaining_checkpoints = (
        (0, 0, 1, 27001, 13071,
         "1d4a931761d341544ee256e0d1550be434bde41ac3d0a51588b02540d02b6d29"),
        (0, 0, 2, 26682, 12855,
         "3b508c5e6b9c24d5eb433b9cf187d06c767fe13d5ec7d5afd977a9b8d4afb1c4"),
        (0, 1, 1, 27616, 13302,
         "8b7644c50e4ea0e2d4ff89ba35c111d0c5611599f63e289fac506c58b76202a7"),
        (0, 1, 2, 26779, 12708,
         "1683484cb1a51168f7c3506adf38a831fad65e87485906fa2873501544e3c631"),
        (1, 0, 1, 24016, 11397,
         "eb3f71dec8372883e3b132fc877e2870c271a5d58628f2941c59b059e2a983da"),
        (1, 0, 2, 23782, 11163,
         "09aaa371e465124fd344fb3a4fc421d51d1164fbf7e8330a45fcbffd31df9b52"),
        (1, 1, 1, 25216, 11973,
         "572637f5986124caece4159531611e592e6177f9166b1d2806f048ed65e91c86"),
        (1, 1, 2, 23868, 11310,
         "064e7fd324f2ba23dff2a51dddd7969397b083de6061ba338dc2301218c5ad44"),
    )
    remaining_parents = remaining_lifts._inputs()[1]
    remaining_proof = _sha256(remaining_lifts.PROOF)
    for parameter, sector, family, e_terms, b_terms, expected_digest in remaining_checkpoints:
        path = remaining_lifts.lift_path(parameter, sector, family)
        lift_digest, lift = _verified_payload(path)
        archive = path.with_suffix(".cochains.json.gz")
        witnesses = lift.get("witnesses", {})
        # Independent full-equation tests establish the mathematics. This
        # ledger binds their actual metadata and complete archive bytes.
        if (lift_digest != expected_digest
            or lift.get("schema") != remaining_lifts.SCHEMA
            or lift.get("prerequisite_artifact_digests") != remaining_parents
            or lift.get("proof_sha256") != remaining_proof
            or lift.get("outer_parameter_basis") != ["a0", "a1"]
            or (lift.get("parameter"), lift.get("sector"), lift.get("family"))
            != (f"a{parameter}", sector, family)
            or lift.get("character") != [[1, 1], [2, 0]][sector]
            or lift.get("seed_index") != ((2, 4), (0, 5))[sector][family - 1]
            or set(witnesses) != {"constant", "constituent_correction", "line_correction"}
            or witnesses.get("constant", {}).get("term_count") != 378
            or witnesses.get("constituent_correction", {}).get("term_count") != e_terms
            or witnesses.get("line_correction", {}).get("term_count") != b_terms
            or lift.get("full_cochain_archive_name") != archive.name
            or _sha256(archive) != lift.get("full_cochain_archive_sha256")
            or any(lift.get(flag) is not True for flag in (
                "full_constituent_identity_exact", "full_pushout_identity_exact",
            ))
            or any(lift.get(flag) is not False for flag in (
                "existing_Q_and_L_recomputed", "extension_point_selected",
                "yukawa_entries_assigned", "physical_yukawas_available",
                "observational_inputs_used",
            ))):
            raise ValueError("the independently replayed actual remaining matter lift changed")
    from . import alternate_down_higgs_quotient_cone as down_cone

    # Full independent equations are encoded by the thirteen critical tests.
    # This ledger binds their exact packet and archive bytes, as for the
    # neutrino matter certificates above; it does not rerun a calculation.
    down_cone_digest, down_cone_packet = _verified_payload(down_cone.OUTPUT)
    down_cone_archive = down_cone.OUTPUT.with_suffix(".cochains.json.gz")
    down_cone_parents = {
        "actual_down_higgs_hom": down_packet["artifact_digest"],
        "frozen_carrier": down_packet["prerequisite_artifact_digests"]["frozen_carrier"],
        "outer_invariants": _verified_payload(ROOT / (
            "data/generated/scientific_genesis/alternate_constituent_outer_invariants.json"
        ))[0],
    }
    if (down_cone_digest != "50d0a3f0f2547f5c1eb05444765b2322075dc03fd56b2b65cf7874534044274f"
        or down_cone_packet.get("prerequisite_artifact_digests") != down_cone_parents
        or down_cone_packet.get("source") != down_packet["source"]
        or down_cone_packet.get("higgs_input_proof_sha256") != down_packet["proof_sha256"]
        or down_cone_packet.get("full_cochain_archive_name") != down_cone_archive.name
        or _sha256(down_cone_archive) != down_cone_packet.get("full_cochain_archive_sha256")
        or down_cone_packet.get("full_cochain_archive_sha256")
        != "b8d5f6ceefe1582ea3c168a3e3e48d762cfa912aa3ada0aff0a43bc7772381e0"
        or [down_cone_packet.get("witnesses", {}).get(f"correction_a{parameter}", {}).get(
            "term_count",
        ) for parameter in (0, 1)]
        != [88650, 76014]):
        raise ValueError("the independently replayed actual down-Higgs quotient cone changed")
    from . import alternate_down_lepton_mixed_pairing as down_lepton_mixed

    actual_mixed, _ = down_lepton_mixed.load_mixed_pairing(
        expected_digest="ae7f62edaf3621af9b8dc8142f597218cd5426b8b922fd9b6b1e8ae2cb1ed1b1",
    )
    if (actual_mixed["full_cochain_archive_sha256"]
        != "473ba7c6b1d4a04f9b61f4d459232dfd688178d9f4cb8ae411bf5073d45517a6"
        or [[entry["cover_residue"] for entry in sector["evaluated_entries"]]
            for sector in actual_mixed["sectors"]] != [
                ["5/14+1/14*omega", "-1/2+2*omega", "-1/2-omega", "-1/14+2/7*omega"],
                ["1+1/2*omega", "5/14+1/14*omega", "-2/7-5/14*omega", "-2-5/2*omega"],
            ]):
        raise ValueError("the independently checked actual down/lepton mixed scalars changed")
    from . import alternate_down_lepton_ff_entries as down_ff

    down_a0_pins = (
        "ab590cef3f36b64d7636c200f163a69cedaba3e878e8493f95d8695286b5ca6b",
        "c570612d6c3246000c70e03439a54ab8a950b2f9d6fa0ed29805e602316c0246",
        "abd2e360c41591ed88a24c08c43d0d385ab544e5377a80fda2914aa9cd56cca2",
        "471aaa5ce5c3b9e7b5e3d694b895711a2f3679f0919833ff6f5936b6c4a318bd",
    )
    initial_down_sources, down_a0 = [], {}
    down_source_snapshot = down_ff._snapshot(0)
    for index, (row, column) in enumerate((r, c) for r in (1, 2) for c in (1, 2)):
        source = down_ff.entry_path(0, 0, row, column)
        digest, entry = _verified_payload(source)
        archive = source.with_suffix(".cochains.json.gz")
        if (digest != down_a0_pins[index] or entry.get("schema") != down_ff.SCHEMA
            or entry.get("source_snapshot") != down_source_snapshot
            or entry.get("proof_sha256") != _sha256(down_ff.PROOF)
            or _sha256(archive) != entry.get("full_cochain_archive_sha256")
            or any(entry.get(flag) is not False for flag in (
                "complete_down_matrix_available", "complete_charged_lepton_matrix_available",
                "physical_yukawas_available", "extension_point_selected",
                "observational_inputs_used",
                "up_Higgs_primitives_used", "Q_and_L_matter_corrections_recomputed",
            ))):
            raise ValueError("an independently trace-checked actual down a0 checkpoint changed")
        value = down_ff._parse_eisenstein_text(entry["cover_residue"])/9
        if entry.get("quotient_residue") != str(value):
            raise ValueError("an actual down a0 trace changed its certified quotient normalization")
        down_a0[row, column] = value
        initial_down_sources.append(source)
    mixed_down = {(item["row"], item["column"]): down_ff._parse_eisenstein_text(
        item["quotient_residue"],
    ) for item in actual_mixed["sectors"][0]["evaluated_entries"]}
    r1, r2, c1, c2 = (mixed_down[key] for key in ((0, 1), (0, 2), (1, 0), (2, 0)))
    down_a0_det = (-r1*c1*down_a0[2, 2] + r1*c2*down_a0[1, 2]
                   + r2*c1*down_a0[2, 1] - r2*c2*down_a0[1, 1])
    if str(down_a0_det) != "1/42-2/21*omega":
        raise ValueError(
            "the independently expanded actual down a0 determinant coefficient changed",
        )
    remaining_scalar_pins = (
        (0, 1, (
            "cc169decddb441780b5558a46cfc08873b0877063ba073c134bfcf152e36a4a2",
            "483a57dc975323f2a689eda4a9d0eca564c277c9c412e5c9255d3375197c1eff",
            "8ae36d456eb8622f4621f6b334f701f780fbbe16bdf1ab3cb278951140bdc6a6",
            "5173a49b0460c88c35582b1194803e8d30f02cad850151737bb05ce090ddba58",
        )),
        (1, 0, (
            "8ee8676a63a43fa0ac6c33a2647c2b5fd1355b3fafe0b5b1b57b1010af0c5ed9",
            "53aeb4763a0102ac808fdeb7b26ca0852b5e7a8fa9bb8dcb87b0e8595bc481ab",
            "ee64ef1b5529fec7f6fc578fc19fdd769bf7471aeaff743b4bc084b4b682d31c",
            "be715b5bc83368be3394e10c911dd618d7fccdc99c183962629b74115624b9e7",
        )),
        (1, 1, (
            "0cb4a84f02e31ebefffbc0b69a64a78ef18c71a1609772ccf316f3ef96041882",
            "93d7e4037fa1b3f37f26d5d230b6c9ae9cf35c786092a85e3d1635057fdc41d4",
            "fb89c73981feb1696fb0583eee3aa51c581ee17f69cbe6cc1463b6db573d128c",
            "c302473b42759452ebac5001ccd8dca24fbb958d7162e07b768ed579c9a9280a",
        )),
    )
    flavor_scalar_sources = list(initial_down_sources)
    scalar_values = {(0, 0, r, c): value for (r, c), value in down_a0.items()}
    for parameter, sector, pins in remaining_scalar_pins:
        snapshot = down_ff._snapshot(parameter)
        for index, (row, column) in enumerate((r, c) for r in (1, 2) for c in (1, 2)):
            source = down_ff.entry_path(parameter, sector, row, column)
            digest, entry = _verified_payload(source)
            archive = source.with_suffix(".cochains.json.gz")
            if (digest != pins[index] or entry.get("schema") != down_ff.SCHEMA
                or entry.get("source_snapshot") != snapshot
                or entry.get("proof_sha256") != _sha256(down_ff.PROOF)
                or _sha256(archive) != entry.get("full_cochain_archive_sha256")
                or any(entry.get(flag) is not False for flag in (
                    "complete_down_matrix_available", "complete_charged_lepton_matrix_available",
                    "physical_yukawas_available", "extension_point_selected",
                    "observational_inputs_used", "up_Higgs_primitives_used",
                    "Q_and_L_matter_corrections_recomputed",
                ))):
                raise ValueError(
                    "a completed remaining scalar checkpoint changed its source or scope",
                )
            value = down_ff._parse_eisenstein_text(entry["cover_residue"])/9
            if entry.get("quotient_residue") != str(value):
                raise ValueError("a completed remaining scalar changed its quotient normalization")
            scalar_values[parameter, sector, row, column] = value
            flavor_scalar_sources.append(source)
    arithmetic_rank_coefficients = []
    for sector in (0, 1):
        mixed = {(item["row"], item["column"]): down_ff._parse_eisenstein_text(
            item["quotient_residue"],
        ) for item in actual_mixed["sectors"][sector]["evaluated_entries"]}
        r1, r2, c1, c2 = (mixed[key] for key in ((0, 1), (0, 2), (1, 0), (2, 0)))
        arithmetic_rank_coefficients.append([
            str(-r1*c1*scalar_values[p, sector, 2, 2] + r1*c2*scalar_values[p, sector, 1, 2]
                + r2*c1*scalar_values[p, sector, 2, 1] - r2*c2*scalar_values[p, sector, 1, 1])
            for p in (0, 1)
        ])
    if arithmetic_rank_coefficients != [
        ["1/42-2/21*omega", "-1/21-5/84*omega"],
        ["-1/84+1/21*omega", "-1/21-5/84*omega"],
    ]:
        raise ValueError("the independently expanded remaining scalar rank coefficients changed")
    completed_flavor = load_full_matrices(
        expected_digest="c7892263e1429ff614c121f991c6fc9fe863c96236bca03422779f1f4291381a",
    )
    uncertain_frames = read_frames()
    if _canonical_digest(uncertain_frames) != (
        "84cae656206db888478fef6988e43e8f4228f69f225915bd3e6c8bf45b281b58"
    ):
        raise ValueError("the original uncertain-domain frames changed their trusted digest")
    shortcut = json.loads((
        ROOT / "data/generated/scientific_genesis/alternate_up_null_shortcut_screen.json"
    ).read_text(encoding="utf-8"))
    shortcut_digest = shortcut.pop("artifact_digest", None)
    if (
        shortcut_digest != _canonical_digest(shortcut)
        or shortcut.get("schema") != "alternate-up-null-shortcut-screen-v2"
        or shortcut.get("prerequisite_artifact_digests", {}).get("null_channels")
        != null_digest
        or shortcut.get("actual_full_leibniz_identity_exact") is not True
        or shortcut.get("primitive_differential_accounts_for_entire_defect") is not True
        or shortcut.get("primitive_only_scalar_closed") is not False
        or shortcut.get("null_to_null_coefficient_computed") is not False
    ):
        raise ValueError("the actual null-primitive Leibniz defect is not certified")
    action_path = (
        ROOT / "data/generated/computable_carrier/tier_b_schoen_outer_automorphisms.partial.json"
    )
    action = json.loads(action_path.read_text(encoding="utf-8"))
    pair_73 = action["completed_pairs"]["73"]
    if pair_73["invariant_ext_one_dimension"] != 4 or pair_73["exact"] is not True:
        raise ValueError("pair 73 is no longer the exact four-dimensional family")
    if pair_73["automorphism_action"]["nonzero_orbit_space"] != "P^3(Q(omega))":
        raise ValueError("pair 73 no longer has the certified projective quotient")
    determinant_path = (
        ROOT / "data/generated/scientific_genesis/mixed_schoen_determinant_descent.json"
    )
    determinant = json.loads(determinant_path.read_text(encoding="utf-8"))
    determinant_digest = determinant.pop("artifact_digest", None)
    if (
        determinant_digest != _canonical_digest(determinant)
        or determinant.get("schema") != "mixed-schoen-determinant-descent-audit-v3"
        or determinant.get("total_determinant_character") != [2, 1]
        or determinant.get("equivariantly_trivial_determinant_certified") is not False
        or determinant.get("uniform_twist_screen", {}).get(
            "one_higgs_zero_triplet_spectrum_preserved"
        ) is not False
        or determinant.get("same_cover_bundle_relinearization", {}).get(
            "same_underlying_bundle_su4_one_higgs_repair_available"
        ) is not False
    ):
        raise ValueError("the selected determinant obstruction is not certified")
    frame_path = (
        ROOT
        / "data/generated/scientific_genesis/"
        "mixed_schoen_atlas_frame_comparison.json"
    )
    frame = json.loads(frame_path.read_text(encoding="utf-8"))
    frame_digest = frame.pop("artifact_digest", None)
    if (
        frame_digest != _canonical_digest(frame)
        or frame.get("schema") != "mixed-schoen-atlas-frame-comparison-v1"
        or frame.get("first_constituent_uniform_twist") != [2, 0]
        or frame.get("second_constituent_uniform_twist") != [0, 0]
        or frame.get("source_atlas_total_determinant_certified") is not False
    ):
        raise ValueError("the atlas/common-frame comparison is not certified")
    wilson_path = (
        ROOT
        / "data/generated/scientific_genesis/mixed_schoen_wilson_shift_no_go.json"
    )
    wilson = json.loads(wilson_path.read_text(encoding="utf-8"))
    wilson_digest = wilson.pop("artifact_digest", None)
    if (
        wilson_digest != _canonical_digest(wilson)
        or wilson.get("schema") != "mixed-schoen-wilson-shift-no-go-v1"
        or wilson.get("both_doublets_without_triplets_possible") is not False
        or wilson.get("source_action_convention_applied") is not True
        or wilson.get("distinct_underlying_constituents_excluded") is not False
    ):
        raise ValueError("the same-constituent Wilson obstruction is not certified")

    artifact_paths = (
        "data/generated/scientific_genesis/alternate_necessary_hidden_chamber.json",
        "research/experiments/scientific_genesis/alternate_necessary_hidden_chamber.py",
        "research/experiments/scientific_genesis/ALTERNATE_NECESSARY_HIDDEN_CHAMBER_NOTE.md",
        "tests/integration/test_scientific_genesis_alternate_necessary_hidden_chamber.py",
        *(str(source.relative_to(ROOT)) for source in flavor_scalar_sources),
        *(str(source.with_suffix(".cochains.json.gz").relative_to(ROOT))
          for source in flavor_scalar_sources),
        "data/generated/scientific_genesis/alternate_down_lepton_mixed_pairing.json",
        "data/generated/scientific_genesis/alternate_down_lepton_mixed_pairing.cochains.json.gz",
        *(str(remaining_lifts.lift_path(parameter, sector, family).relative_to(ROOT))
          for parameter in (0, 1) for sector in (0, 1) for family in (1, 2)),
        *(str(remaining_lifts.lift_path(parameter, sector, family).with_suffix(
            ".cochains.json.gz",
        ).relative_to(ROOT))
          for parameter in (0, 1) for sector in (0, 1) for family in (1, 2)),
        "data/generated/computable_carrier/computable_carrier_artifact.json",
        "data/generated/computable_carrier/tier_b_schoen_outer_full.json",
        "data/generated/computable_carrier/tier_b_schoen_outer_invariants.json",
        "data/generated/computable_carrier/tier_b_schoen_outer_automorphisms.partial.json",
        "data/generated/scientific_genesis/pair_73_universal_ext.json",
        "data/generated/scientific_genesis/pair_73_source.json",
        "data/generated/scientific_genesis/pair_73_cech_lift.json",
        "data/generated/scientific_genesis/pair_73_algebraic_locus.json",
        "data/generated/scientific_genesis/pair_73_stability_wall.json",
        "data/generated/scientific_genesis/pair_73_stability_no_go.json",
        "data/generated/scientific_genesis/minimal_block_stability_no_go.json",
        "data/generated/scientific_genesis/next_block_stability_no_go.json",
        "data/generated/scientific_genesis/current_minimum_stability_no_go.json",
        "data/generated/scientific_genesis/forced_subobject_stability_screen.json",
        "data/generated/scientific_genesis/mixed_sign_minimum_chamber.json",
        "data/generated/scientific_genesis/mixed_sign_minimum_stability_no_go.json",
        "data/generated/scientific_genesis/lifted_line_slope_identity_no_go.json",
        "data/generated/scientific_genesis/next_survivor_restriction.json",
        "data/generated/scientific_genesis/next_survivor_forced_chamber.json",
        "data/generated/scientific_genesis/next_survivor_generator_restrictions.json",
        "data/generated/scientific_genesis/next_survivor_lower_line_no_go.json",
        "data/generated/scientific_genesis/remaining_lower_line_no_go.json",
        "data/generated/scientific_genesis/published_pushout_mismatch.json",
        "data/generated/scientific_genesis/published_constituent_ext_spaces.json",
        "data/generated/scientific_genesis/published_constituent_deck_actions.json",
        "data/generated/scientific_genesis/published_constituent_ray_alignment.json",
        "data/generated/scientific_genesis/published_constituent_full_cech.json",
        "data/generated/scientific_genesis/published_constituent_local_units.json",
        "data/generated/scientific_genesis/published_constituent_chart_presentations.json",
        "data/generated/scientific_genesis/published_constituent_overlap_transitions.json",
        "data/generated/scientific_genesis/published_constituent_deck_atlases.json",
        "data/generated/scientific_genesis/"
        "mixed_schoen_atlas_frame_comparison.json",
        "data/generated/scientific_genesis/"
        "mixed_schoen_wilson_shift_no_go.json",
        "data/generated/scientific_genesis/mixed_constituent_schoen_arrows.json",
        "data/generated/scientific_genesis/mixed_schoen_outer_transfer.json",
        "data/generated/scientific_genesis/mixed_schoen_outer_actions.json",
        "data/generated/scientific_genesis/mixed_schoen_outer_universal_cone.json",
        "data/generated/scientific_genesis/"
        "mixed_schoen_reverse_outer_universal_cone.json",
        "data/generated/scientific_genesis/"
        "mixed_schoen_reverse_outer_stability_locus.json",
        "data/generated/scientific_genesis/mixed_schoen_determinant_descent.json",
        "data/generated/scientific_genesis/mixed_schoen_outer_stability_locus.json",
        "data/generated/scientific_genesis/mixed_schoen_observable_spectrum.json",
        "data/generated/scientific_genesis/"
        "mixed_schoen_reverse_observable_spectrum.json",
        "data/generated/scientific_genesis/computable_one_theory_carrier_state.json",
        "data/generated/scientific_genesis/"
        "computable_one_theory_reverse_carrier_state.json",
        "data/generated/scientific_genesis/"
        "mixed_schoen_reverse_down_matter_lifts.json",
        "data/generated/scientific_genesis/"
        "mixed_schoen_reverse_higgs_lifts.json",
        "data/generated/scientific_genesis/"
        "mixed_schoen_reverse_down_support.json",
        "data/generated/scientific_genesis/"
        "mixed_schoen_v1_pluecker_chain_map.json",
        "data/generated/scientific_genesis/mixed_schoen_matter_representatives.json",
        "data/generated/scientific_genesis/mixed_schoen_universal_matter_lifts.json",
        "data/generated/scientific_genesis/mixed_schoen_higgs_twist_audit.json",
        "data/generated/scientific_genesis/mixed_schoen_direct_tensor.json",
        "data/generated/scientific_genesis/mixed_schoen_chain_diagonal.json",
        "data/generated/scientific_genesis/mixed_schoen_chain_actions.json",
        "data/generated/scientific_genesis/mixed_schoen_matter_tensor_audit.json",
        "data/generated/scientific_genesis/mixed_schoen_matter_comparison.json",
        "data/generated/scientific_genesis/mixed_schoen_scalar_trace.json",
        "data/generated/scientific_genesis/mixed_schoen_determinant_pairing.json",
        "data/generated/scientific_genesis/mixed_schoen_yukawa_trace.json",
        "data/generated/scientific_genesis/mixed_schoen_diagonal_comparison.json",
        "data/generated/scientific_genesis/mixed_schoen_matter_leg_deformation.json",
        "data/generated/scientific_genesis/mixed_schoen_higgs_leg_deformation.json",
        "data/generated/scientific_genesis/mixed_schoen_v2_pluecker_chain_map.json",
        "data/generated/scientific_genesis/mixed_schoen_first_higher_product.json",
        "data/generated/scientific_genesis/mixed_schoen_first_order_matrix.json",
        "data/generated/scientific_genesis/mixed_schoen_up_yukawa_no_go.json",
        "data/generated/scientific_genesis/"
        "mixed_schoen_flavor_character_support.json",
        "data/generated/scientific_genesis/mixed_schoen_down_higgs_action.json",
        "data/generated/scientific_genesis/"
        "mixed_schoen_higgs_equivariant_obstruction.json",
        "data/generated/scientific_genesis/"
        "mixed_schoen_higgs_scalar_action_no_go.json",
        "data/generated/scientific_genesis/"
        "mixed_schoen_higgs_character_audit.json",
        "data/generated/scientific_genesis/"
        "mixed_schoen_higgs_linearization_no_go.json",
        "data/generated/scientific_genesis/"
        "mixed_schoen_atlas_higgs_characters.json",
        "data/generated/scientific_genesis/"
        "mixed_schoen_character_convention.json",
        "data/generated/scientific_genesis/"
        "mixed_schoen_down_matter_lifts.json",
        "data/generated/scientific_genesis/"
        "mixed_schoen_down_tree_matrix.json",
        "data/generated/scientific_genesis/"
        "mixed_schoen_down_first_order_matrix.json",
        "data/generated/scientific_genesis/mixed_schoen_flavor_frontier.json",
        "data/generated/scientific_genesis/"
        "mixed_schoen_neutrino_matter_lifts.json",
        "data/generated/scientific_genesis/"
        "mixed_schoen_neutrino_tree_matrix.json",
        "data/generated/scientific_genesis/"
        "mixed_schoen_neutrino_first_order_matrix.json",
        "data/generated/scientific_genesis/"
        "mixed_schoen_charged_lepton_convention.json",
        "data/generated/scientific_genesis/published_constituent_mapping_cones.json",
        "data/generated/scientific_genesis/published_outer_reduced_mismatch.json",
        "data/generated/scientific_genesis/published_outer_cech_transfer.json",
        "data/generated/scientific_genesis/published_outer_cech_invariants.json",
        "data/generated/scientific_genesis/published_outer_universal_cone.json",
        "data/generated/scientific_genesis/published_outer_stability_locus.json",
        "data/generated/scientific_genesis/published_matter_cohomology.json",
        "data/generated/scientific_genesis/published_higgs_cohomology.json",
        "data/generated/scientific_genesis/relative_constituent_pushdowns.json",
        "data/generated/scientific_genesis/"
        "distinct_constituent_ray_screen.json",
        "data/generated/scientific_genesis/"
        "alternate_constituent_higgs_dimensions.json",
        "data/generated/scientific_genesis/"
        "alternate_constituent_deck_atlases.json",
        "data/generated/scientific_genesis/"
        "alternate_constituent_determinant_descent.json",
        "data/generated/scientific_genesis/"
        "alternate_constituent_hom_actions.json",
        "data/generated/scientific_genesis/"
        "alternate_constituent_character_screen.json",
        "data/generated/scientific_genesis/"
        "alternate_constituent_outer_ext.json",
        "data/generated/scientific_genesis/"
        "alternate_constituent_outer_invariants.json",
        "data/generated/scientific_genesis/"
        "alternate_constituent_outer_universal_cone.json",
        "data/generated/scientific_genesis/"
        "alternate_constituent_outer_stability_locus.json",
        "data/generated/scientific_genesis/"
        "alternate_constituent_matter_profile.json",
        "data/generated/scientific_genesis/"
        "alternate_constituent_structural_spectrum.json",
        "data/generated/scientific_genesis/"
        "alternate_constituent_carrier_state.json",
        "data/generated/scientific_genesis/"
        "alternate_constituent_up_matter_representatives.json",
        "data/generated/scientific_genesis/"
        "alternate_constituent_up_cone_matter_lifts.json",
        "data/generated/scientific_genesis/"
        "alternate_up_higgs_hom_representative.json",
        "data/generated/scientific_genesis/"
        "alternate_up_higgs_hom_full_cochain.json",
        "data/generated/scientific_genesis/"
        "alternate_up_higgs_chart_restriction.json",
        "data/generated/scientific_genesis/"
        "alternate_constituent_determinant_pairing.json",
        "data/generated/scientific_genesis/"
        "alternate_constituent_duality_local_inverse.json",
        "data/generated/scientific_genesis/"
        "alternate_up_higgs_local_syzygy_section.json",
        "data/generated/scientific_genesis/"
        "alternate_up_higgs_fiber_overlap_transport.json",
        "data/generated/scientific_genesis/"
        "alternate_up_higgs_quotient_overlap_image.json",
        "data/generated/scientific_genesis/"
        "alternate_up_higgs_minor_overlap_gluing.json",
        "data/generated/scientific_genesis/"
        "alternate_up_yoneda_evaluation.json",
        "data/generated/scientific_genesis/"
        "alternate_up_mixed_scalar_trace.json",
        "data/generated/scientific_genesis/alternate_up_rank_floor.json",
        "data/generated/scientific_genesis/alternate_up_null_channel.json",
        "data/generated/scientific_genesis/alternate_up_dual_higgs_inputs.json",
        "data/generated/scientific_genesis/alternate_up_exterior_higgs_action.json",
        "data/generated/scientific_genesis/alternate_up_higgs_quotient_cone.json",
        "data/generated/scientific_genesis/alternate_up_first_order_scalar.json",
        "data/generated/scientific_genesis/alternate_up_quotient_equivariance.json",
        "data/generated/scientific_genesis/alternate_up_pairing_exchange.json",
        "data/generated/scientific_genesis/alternate_up_pairing_exchange.cochains.json.gz",
        "data/generated/scientific_genesis/alternate_up_null_line_homotopies.json",
        "data/generated/scientific_genesis/alternate_up_exterior_boundary_attack.json",
        "data/generated/scientific_genesis/alternate_up_syzygy_tensor_comparison.json",
        "data/generated/scientific_genesis/alternate_up_coupled_tensor_comparison.json",
        "data/generated/scientific_genesis/alternate_up_quotient_trace.json",
        "data/generated/scientific_genesis/alternate_up_mixed_quotient_pairing.json",
        "data/generated/scientific_genesis/alternate_up_coupled_null_scalar.json",
        "data/generated/scientific_genesis/alternate_up_coupled_null_scalar.cochains.json.gz",
        "data/generated/scientific_genesis/alternate_up_ff_lift_a0_side0_family1.json",
        "data/generated/scientific_genesis/alternate_up_ff_lift_a0_side0_family1.cochains.json.gz",
        "data/generated/scientific_genesis/alternate_up_ff_lift_a0_side0_family2.json",
        "data/generated/scientific_genesis/alternate_up_ff_lift_a0_side0_family2.cochains.json.gz",
        "data/generated/scientific_genesis/alternate_up_ff_lift_a0_side1_family1.json",
        "data/generated/scientific_genesis/alternate_up_ff_lift_a0_side1_family1.cochains.json.gz",
        "data/generated/scientific_genesis/alternate_up_ff_lift_a0_side1_family2.json",
        "data/generated/scientific_genesis/alternate_up_ff_lift_a0_side1_family2.cochains.json.gz",
        "data/generated/scientific_genesis/alternate_up_ff_a0_r1_c1.json",
        "data/generated/scientific_genesis/alternate_up_ff_a0_r1_c1.cochains.json.gz",
        "data/generated/scientific_genesis/alternate_up_ff_a0_r1_c2.json",
        "data/generated/scientific_genesis/alternate_up_ff_a0_r1_c2.cochains.json.gz",
        "data/generated/scientific_genesis/alternate_up_ff_a0_r2_c1.json",
        "data/generated/scientific_genesis/alternate_up_ff_a0_r2_c1.cochains.json.gz",
        "data/generated/scientific_genesis/alternate_up_ff_a0_r2_c2.json",
        "data/generated/scientific_genesis/alternate_up_ff_a0_r2_c2.cochains.json.gz",
        "data/generated/scientific_genesis/alternate_up_ff_coefficient_a0.json",
        "data/generated/scientific_genesis/alternate_up_ff_lift_a1_side0_family1.json",
        "data/generated/scientific_genesis/alternate_up_ff_lift_a1_side0_family1.cochains.json.gz",
        "data/generated/scientific_genesis/alternate_up_ff_lift_a1_side0_family2.json",
        "data/generated/scientific_genesis/alternate_up_ff_lift_a1_side0_family2.cochains.json.gz",
        "data/generated/scientific_genesis/alternate_up_ff_lift_a1_side1_family1.json",
        "data/generated/scientific_genesis/alternate_up_ff_lift_a1_side1_family1.cochains.json.gz",
        "data/generated/scientific_genesis/alternate_up_ff_lift_a1_side1_family2.json",
        "data/generated/scientific_genesis/alternate_up_ff_lift_a1_side1_family2.cochains.json.gz",
        "data/generated/scientific_genesis/alternate_up_ff_a1_r1_c1.json",
        "data/generated/scientific_genesis/alternate_up_ff_a1_r1_c1.cochains.json.gz",
        "data/generated/scientific_genesis/alternate_up_ff_a1_r1_c2.json",
        "data/generated/scientific_genesis/alternate_up_ff_a1_r1_c2.cochains.json.gz",
        "data/generated/scientific_genesis/alternate_up_ff_a1_r2_c1.json",
        "data/generated/scientific_genesis/alternate_up_ff_a1_r2_c1.cochains.json.gz",
        "data/generated/scientific_genesis/alternate_up_ff_a1_r2_c2.json",
        "data/generated/scientific_genesis/alternate_up_ff_a1_r2_c2.cochains.json.gz",
        "data/generated/scientific_genesis/alternate_up_ff_coefficient_a1.json",
        "data/generated/scientific_genesis/alternate_up_full_holomorphic_matrix.json",
        "data/generated/scientific_genesis/alternate_metric_subbundle_vanishing.json",
        "data/generated/scientific_genesis/alternate_metric_quotient_generation.json",
        "data/generated/scientific_genesis/alternate_metric_first_subline_sections.json",
        "data/generated/scientific_genesis/alternate_metric_first_resolution_ambient_sections.json",
        "data/generated/scientific_genesis/alternate_metric_first_quotient_sections.json",
        "data/generated/scientific_genesis/"
        "alternate_metric_first_quotient_sections.relations.json.gz",
        "data/generated/scientific_genesis/alternate_metric_first_serre_lifts.json",
        "data/generated/scientific_genesis/alternate_metric_first_serre_lifts.sections.json.gz",
        "data/generated/scientific_genesis/alternate_metric_second_sections.json",
        "data/generated/scientific_genesis/alternate_metric_second_sections.sections.json.gz",
        "data/generated/scientific_genesis/alternate_metric_second_sections.relations.json.gz",
        "data/generated/scientific_genesis/alternate_metric_outer_lifts.json",
        "data/generated/scientific_genesis/alternate_metric_lift_operator_certificate.json",
        "data/generated/scientific_genesis/alternate_metric_fiber_evaluation.json",
        "data/generated/scientific_genesis/alternate_metric_specialized_evaluation.json",
        "data/generated/scientific_genesis/alternate_metric_specialized_evaluation.matrix.json.gz",
        "data/generated/scientific_genesis/alternate_metric_measure.json",
        "data/generated/scientific_genesis/alternate_metric_weight_moments.json",
        "data/generated/scientific_genesis/alternate_metric_positive_measure.json",
        "data/generated/scientific_genesis/projective_uniform_input_cells.json",
        "data/generated/scientific_genesis/projective_uncertain_intersections.json",
        "data/generated/scientific_genesis/uncertain_cover_weights.json",
        "data/generated/scientific_genesis/auxiliary_cover_draws.json",
        "research/experiments/scientific_genesis/auxiliary_cover_draws.py",
        "research/experiments/scientific_genesis/AUXILIARY_COVER_DRAWS_NOTE.md",
        "tests/integration/test_scientific_genesis_auxiliary_cover_draws.py",
        "research/experiments/scientific_genesis/uncertain_cover_weights.py",
        "research/experiments/scientific_genesis/UNCERTAIN_COVER_WEIGHTS_NOTE.md",
        "tests/integration/test_scientific_genesis_uncertain_cover_weights.py",
        "research/experiments/scientific_genesis/projective_uncertain_intersections.py",
        "research/experiments/scientific_genesis/PROJECTIVE_UNCERTAIN_INTERSECTIONS_NOTE.md",
        "tests/integration/test_scientific_genesis_projective_uncertain_intersections.py",
        "research/experiments/scientific_genesis/projective_uniform_input_cells.py",
        "research/experiments/scientific_genesis/PROJECTIVE_UNIFORM_INPUT_CELLS_NOTE.md",
        "tests/integration/test_scientific_genesis_projective_uniform_input_cells.py",
        "data/generated/scientific_genesis/alternate_metric_critical_charts.json",
        "data/generated/scientific_genesis/alternate_metric_projection_free_weights.json",
        "data/generated/scientific_genesis/alternate_metric_global_weight_bound.json",
        "data/generated/scientific_genesis/alternate_metric_projective_roots.json",
        "data/generated/scientific_genesis/alternate_metric_enclosures.json",
        "data/generated/scientific_genesis/alternate_metric_bounded_fibers.json",
        "data/generated/scientific_genesis/alternate_metric_bounded_support.json",
        "data/generated/scientific_genesis/alternate_metric_bounded_matrix.json",
        "data/generated/scientific_genesis/alternate_metric_bounded_matrix.columns.jsonl.gz",
        "data/generated/scientific_genesis/alternate_neutrino_mixed_pairing.json",
        "data/generated/scientific_genesis/alternate_neutrino_mixed_pairing.cochains.json.gz",
        "data/generated/scientific_genesis/alternate_neutrino_full_holomorphic_matrix.json",
        "data/generated/scientific_genesis/alternate_down_lepton_full_holomorphic_matrices.json",
        "research/experiments/scientific_genesis/alternate_down_lepton_full_matrices.py",
        "tests/integration/test_scientific_genesis_alternate_down_lepton_full_matrices.py",
        "research/experiments/scientific_genesis/UNCERTAIN_COVER_FRAMES_NOTE.md",
        "research/experiments/scientific_genesis/alternate_metric_enclosures.py",
        "tests/integration/test_scientific_genesis_uncertain_cover_points.py",
        "data/generated/scientific_genesis/uncertain_cover_frames.json",
        "research/experiments/scientific_genesis/uncertain_cover_frames.py",
        "tests/integration/test_scientific_genesis_uncertain_cover_frames.py",
        "tests/integration/test_scientific_genesis_rounded_centers.py",
        "data/generated/scientific_genesis/alternate_down_higgs_hom_representative.json",
        "data/generated/scientific_genesis/"
        "alternate_down_higgs_hom_representative.cochains.json.gz",
        "data/generated/scientific_genesis/alternate_remaining_flavor_matter.json",
        "data/generated/scientific_genesis/alternate_remaining_flavor_matter.cochains.json.gz",
        "data/generated/scientific_genesis/alternate_down_higgs_quotient_cone.json",
        "data/generated/scientific_genesis/alternate_down_higgs_quotient_cone.cochains.json.gz",
        *(f"data/generated/scientific_genesis/alternate_neutrino_ff_a{parameter}_r{row}_c{column}.json"
          for parameter in (0, 1) for row in (1, 2) for column in (1, 2)),
        *("data/generated/scientific_genesis/"
          f"alternate_neutrino_ff_a{parameter}_r{row}_c{column}.cochains.json.gz"
          for parameter in (0, 1) for row in (1, 2) for column in (1, 2)),
        *(str(neutrino_lifts.lift_path(parameter, side, family).relative_to(ROOT))
          for parameter in (0, 1) for side in (0, 1) for family in (1, 2)),
        *(str(neutrino_lifts.lift_path(parameter, side, family).with_suffix(
            ".cochains.json.gz",
        ).relative_to(ROOT))
          for parameter in (0, 1) for side in (0, 1) for family in (1, 2)),
        "data/generated/scientific_genesis/alternate_up_null_shortcut_screen.json",
        "data/generated/scientific_genesis/"
        "alternate_up_yukawa_support.json",
        "data/generated/scientific_genesis/diagonal_higgs_actions.json",
        "data/generated/visible_carrier/visible_carrier_artifact.json",
        "data/published/visible_carrier/source_manifest.json",
        "Experimental_Draft_OneTheory.py",
        "Experimental_Draft_OneTheory.docx",
    )
    payload: dict[str, object] = {
        "schema": SCHEMA,
        "objective": {
            "name": "Scientific Genesis: Vertical Closure and Fundamental Derivation",
            "governing_criterion": "minimize distance to the next genuine derived physical result",
            "near_term_milestone": (
                "one stable descended genuine SU(4) bundle and one complete "
                "3x3 Yukawa matrix from generated chain data"
            ),
            "directive_sha256": "c03f5b3713625bc4430559137414e4f7778539fb3a79d29483196d4e33725768",
        },
        "audit_scope": {
            "production_python_files": len(tuple((ROOT / "src/onetheory").rglob("*.py"))),
            "research_python_files": len(tuple((ROOT / "research/experiments").rglob("*.py"))),
            "test_python_files": len(tuple((ROOT / "tests").rglob("test_*.py"))),
            "collected_tests_at_audit": 3129,
            "original_sources_unchanged": True,
        },
        "artifacts": [
            {"path": path, "sha256": _sha256(ROOT / path), "bytes": (ROOT / path).stat().st_size}
            for path in artifact_paths
        ],
        "automorphism_checkpoint": {
            "completed_pairs": action["completed_pair_count"],
            "declared_pairs": action["declared_pair_count"],
            "completion_fraction": "9/10",
            "constituent_certificates": action["constituent_count"],
            "suspended": True,
            "remaining_dimensions": {"110": 36, "116": 36, "126": 72},
            "suspension_reason": (
                "remaining larger Ext spaces cannot improve the simplest "
                "already-certified pair-73 family"
            ),
        },
        "recommended_vertical_path": {
            "candidate_pair": None,
            "selection_status": (
                "the selected P1 and reverse P5 physical quotient freezes are "
                "refuted; the distinct determinant-repaired alternate P1 "
                "component passes the charged structural spectrum and is "
                "frozen only for chain-level physics"
            ),
            "criteria": {
                "retired_invariant_ext_dimension": 4,
                "coefficient_field": "Q(omega)",
                "retired_candidate_blocks": [3, 23],
                "retired_pair_ranges": [[73, 108], [793, 828]],
                "retired_family_count": 72,
                "additional_retired_candidate_blocks": [14, 34],
                "additional_retired_family_count": 72,
                "current_minimum_retired_candidate_blocks": [8, 28],
                "current_minimum_retired_pair_ranges": [[253, 288], [973, 1008]],
                "current_minimum_retired_family_count": 72,
                "forced_subobject_retired_candidate_blocks": [
                    6,
                    7,
                    8,
                    9,
                    10,
                    17,
                    18,
                    19,
                    20,
                    26,
                    27,
                    28,
                    29,
                    30,
                    37,
                    38,
                    39,
                    40,
                ],
                "forced_subobject_retired_family_count": 648,
                "remaining_nonzero_candidate_blocks": [],
                "remaining_nonzero_family_count": 0,
                "mixed_sign_minimum_retired_candidate_blocks": [15, 35],
                "mixed_sign_minimum_retired_family_count": 72,
                "slope_identity_retired_candidate_blocks": [16, 36],
                "slope_identity_retired_family_count": 72,
                "next_survivor_restriction_rank": 20,
                "next_survivor_target_ext_dimension": 216,
                "next_survivor_projective_lifting_loci": {
                    "P^49(Q(omega))": "P^29(Q(omega))",
                    "P^51(Q(omega))": "P^31(Q(omega))",
                },
                "next_survivor_lifting_kernels_unstable": True,
                "next_survivor_complements_stability_proved": False,
                "next_survivor_forced_chamber_nonempty": True,
                "next_survivor_forced_chamber_witnesses": [
                    "(5,1,7)",
                    "(1,5,7)",
                ],
                "next_survivor_generator_restriction_count": 288,
                "next_survivor_generator_rank_counts": {
                    "36": 36,
                    "38": 36,
                    "40": 216,
                },
                "next_survivor_generator_kernels_proper": True,
                "next_survivor_generator_complement_nonempty": True,
                "next_survivor_lower_line_retired_candidate_blocks": [4, 24],
                "next_survivor_lower_line_retired_family_count": 72,
                "next_survivor_lower_line_lifts_universally": True,
                "next_survivor_lower_line_positive_slope_identity": True,
                "final_lower_line_retired_candidate_blocks": [5, 25],
                "final_lower_line_retired_family_count": 72,
                "final_lower_line_lifts_universally": True,
                "declared_computable_carrier_category_exhausted": True,
                "global_schoen_bundle_no_go": False,
                "next_candidate_blocks": [],
                "minimum_forced_chamber_nonempty": True,
                "minimum_forced_chamber_certificate": ["(2,1,t)", "t>7/2"],
                "minimum_projective_orbit_spaces": {
                    "P^17(Q(omega))": 36,
                    "P^23(Q(omega))": 36,
                },
                "arbitrary_point_selected": False,
                "mixed_cover_h1_dimensions": [18, 54],
                "mixed_invariant_h1_dimensions": [2, 6],
                "mixed_strict_invariant_representatives": [2, 6],
                "lawful_mixed_projective_outer_space": "P^1(Q(omega))",
                "lawful_reverse_projective_outer_space": "P^5(Q(omega))",
                "lawful_reverse_split_locus": "affine origin only",
                "lawful_reverse_local_freeness_all_parameters": True,
                "lawful_reverse_equivariant_descent_all_parameters": True,
                "lawful_reverse_extension_point_selected": False,
                "lawful_reverse_exact_stability_locus_computed": True,
                "lawful_reverse_stability_anchor": [3, 2, 2],
                "lawful_reverse_stability_box_radius": "1/4",
                "lawful_reverse_all_P5_stable_in_chamber": True,
                "lawful_reverse_genuine_su4_on_stable_chamber": False,
                "lawful_reverse_factor_exchange_assumed": False,
                "retired_source_scoped_outer_space": "P^3(Q(omega))",
                "outer_parameter_dimension_mismatch_unresolved": True,
                "lawful_P1_all_nonzero_parameters_stable_in_chamber": True,
                "lawful_P1_genuine_su4_on_stable_chamber": False,
                "retired_P3_embedding_used_for_stability": False,
                "lawful_matter_h0_to_h3": [0, 27, 0, 0],
                "lawful_dual_matter_h0_to_h3": [0, 0, 27, 0],
                "lawful_matter_deck_representation": "3 Reg(Z3 x Z3)",
                "lawful_higgs_h0_to_h3": [0, 4, 4, 0],
                "lawful_wilson_projected_families": 3,
                "lawful_wilson_projected_higgs_pairs": 0,
                "lawful_massless_color_triplets": 0,
                "lawful_structural_spectrum_all_P1": False,
                "prior_forward_computable_carrier_component": (
                    "lawful-mixed-schoen-P1"
                ),
                "prior_forward_computable_carrier_component_frozen": False,
                "computable_carrier_component": "alternate-i6-ray-0-1-P1",
                "computable_carrier_component_frozen": True,
                "selected_quotient_determinant_character": [2, 1],
                "selected_quotient_su4_certified": False,
                "alternate_fixed_atlas_determinant_characters": [
                    case["total_determinant_character"]
                    for case in alternate_det_cases
                ],
                "alternate_fixed_atlas_su4_excluded": True,
                "alternate_other_linearisations_excluded": False,
                "alternate_repaired_higgs_screen_survivor": [0, 1],
                "alternate_repaired_higgs_screen_conditional": True,
                "alternate_repaired_higgs_outer_extension_constructed": True,
                "alternate_ray_0_1_cover_ext1_dimension": 18,
                "alternate_ray_0_1_invariant_ext1_dimension": 2,
                "alternate_ray_0_1_strict_invariant_representatives": 2,
                "alternate_ray_0_1_invariant_ext_unresolved": False,
                "alternate_ray_0_1_universal_cone_constructed": True,
                "alternate_ray_0_1_determinant_repaired": True,
                "alternate_ray_0_1_stability_unresolved": False,
                "alternate_ray_0_1_all_nonzero_p1_stable_in_sufficient_chamber": True,
                "alternate_ray_0_1_genuine_su4_on_sufficient_chamber": True,
                "alternate_ray_0_1_physical_spectrum_unresolved": True,
                "alternate_ray_0_1_charged_structural_spectrum_passes": True,
                "alternate_ray_0_1_higgs_h0_to_h3": [0, 4, 4, 0],
                "alternate_ray_0_1_wilson_higgs_pairs": 1,
                "alternate_up_ordered_exterior_products_closed": True,
                "alternate_up_reciprocal_exterior_primitives_verified": True,
                "alternate_up_natural_quotient_cone_available": True,
                "alternate_up_null_tensor_projection_exact": True,
                "alternate_up_complete_ordered_null_screens_computed": True,
                "alternate_up_ordered_null_cover_residues": [
                    item["ordered_cover_residue"] for item in ordered_coefficients
                ],
                "alternate_up_ordered_null_a1_coefficient_nonzero": True,
                "alternate_up_inherited_quotient_equivariance_certified": True,
                "alternate_up_repaired_quotient_higgs_character": [0, 2],
                "alternate_up_ordered_null_direct_trace_independently_verified": True,
                "alternate_up_ordered_exchange_screen_computed": True,
                "alternate_up_null_yoneda_line_homotopies_verified": True,
                "alternate_up_null_line_h0_to_h3": [0, 0, 9, 0],
                "alternate_up_quotient_fixed_endpoint_map_ambiguity_dimension": 0,
                "alternate_up_quotient_K_h0_to_h3": [0, 5, 5, 0],
                "alternate_up_quotient_matter_product_ambiguity_dimension": 5,
                "alternate_up_raw_exterior_cup_all_input_chain_map_refuted": True,
                "alternate_up_raw_exterior_boundary_closure_defect_term_count": 124,
                "alternate_up_even_tensor_boundary_repair_verified": True,
                "alternate_up_null_wedge_unchanged_by_even_tensor_repair": True,
                "alternate_up_graded_rank_one_F_tensor_identity_derived": True,
                "alternate_up_actual_syzygy_boundary_comparison_verified": True,
                "alternate_up_raw_syzygy_boundary_closure_defect_term_count": 489,
                "alternate_up_first_slot_cover_coherence_derived": True,
                "alternate_up_coupled_outer_tensor_comparison_available": True,
                "alternate_up_local_vertex_tensor_comparison_available": True,
                "alternate_up_canonical_quotient_sheaf_product_identified": True,
                "alternate_up_scalar_class_descent_certified": True,
                "alternate_up_explicit_quotient_trace_constructed": True,
                "alternate_up_cover_to_quotient_trace_factor": "1/9",
                "alternate_up_same_higgs_class_identified": True,
                "alternate_up_higgs_first_constant_mixed_entries_computed": True,
                "alternate_up_complete_carrier_scalar_pairing_evaluated": True,
                "alternate_up_natural_null_cover_residues": [
                    item["ordered_cover_residue"] for item in natural_coefficients
                ],
                "alternate_up_holomorphic_matrix_available": True,
                "alternate_up_holomorphic_matrix_determinant": full_up["determinant"],
                "alternate_up_holomorphic_rank_three_locus": "a1 != 0",
                "alternate_up_physical_yukawa_matrix_available": False,
                "alternate_neutrino_actual_constituent_classes_available": True,
                "alternate_neutrino_constant_mixed_entry_count": 4,
                "alternate_neutrino_shared_up_higgs_used": True,
                "alternate_neutrino_complete_holomorphic_matrix_available": True,
                "alternate_neutrino_holomorphic_matrix_determinant": neutrino_matrix["determinant"],
                "alternate_neutrino_holomorphic_rank_three_locus": "a0 != 0",
                "alternate_up_neutrino_common_rank_three_locus": "a0*a1 != 0",
                "alternate_neutrino_physical_yukawa_matrix_available": False,
                "alternate_down_lepton_constant_mixed_entry_count": sum(
                    len(sector["evaluated_entries"]) for sector in actual_mixed["sectors"]
                ),
                "alternate_down_lepton_mixed_blocks_available": True,
                "alternate_down_a0_archived_coefficient_count": len(down_a0),
                "alternate_down_a0_determinant_coefficient": str(down_a0_det),
                "alternate_down_lepton_scalar_archive_count": len(scalar_values),
                "alternate_down_lepton_complete_scalar_source_set_available": True,
                "alternate_down_lepton_arithmetic_rank_coefficients": arithmetic_rank_coefficients,
                "alternate_down_lepton_all_sixteen_fresh_entry_replays_complete":
                completed_flavor["all_sixteen_formal_coefficient_scalars_replayed"],
                "alternate_down_lepton_complete_holomorphic_matrices_available":
                completed_flavor["complete_holomorphic_matrices_available"],
                "alternate_all_four_holomorphic_sectors_available": True,
                "alternate_four_sector_common_rank_three_locus":
                completed_flavor["four_sector_common_rank_three_locus_polynomial"],
                "alternate_four_sector_common_rank_three_locus_nonempty":
                completed_flavor["four_sector_common_rank_three_locus_nonempty"],
                "alternate_down_lepton_physical_yukawa_matrices_available": False,
                "alternate_neutrino_majorana_mechanism_derived": False,
                "alternate_metric_trial_twist": metric["twist_cover_degree"],
                "alternate_metric_subbundle_h1_vanishing": True,
                "alternate_metric_first_constituent_cover_generated": True,
                "alternate_metric_large_generating_twist": generation[
                    "generating_twist_cover_degree"
                ],
                "alternate_metric_quotient_section_count": generation[
                    "quotient_h0_rank_four_at_generating_twist"
                ],
                "alternate_metric_first_subline_basis_count": subline[
                    "quotient_subline_section_count"
                ],
                "alternate_metric_first_serre_quotient_basis_count": first_quotient[
                    "quotient_section_dimension"
                ],
                "alternate_metric_first_serre_lifts_remaining_count": 0,
                "alternate_metric_first_constituent_section_basis_count": first_lifts[
                    "section_dimension"
                ],
                "alternate_metric_first_constituent_section_basis_available": True,
                "alternate_metric_second_constituent_section_basis_count": second_sections[
                    "section_dimension"
                ],
                "alternate_metric_second_constituent_section_basis_available": True,
                "alternate_metric_constituent_section_bases_available": True,
                "alternate_metric_rank_four_quotient_lifts_remaining_count": 0,
                "alternate_metric_universal_section_constructor_available": True,
                "alternate_metric_full_lift_formula_independently_certified": True,
                "alternate_metric_full_independent_rank_four_replay_completed": False,
                "alternate_metric_first_resolution_ambient_generator_counts": [
                    item["ambient_invariant_generator_count"] for item in ambient_blocks
                ],
                "alternate_metric_constituents_globally_generated": True,
                "alternate_metric_rank_four_globally_generated": True,
                "alternate_metric_explicit_invariant_basis_available": True,
                "alternate_metric_local_rank_four_evaluation_available": True,
                "alternate_metric_complete_point_evaluation_matrix_materialized": True,
                "alternate_metric_exact_residue_and_auxiliary_measure_available": True,
                "alternate_metric_weight_second_moment_finite": True,
                "alternate_metric_weight_third_moment_finite": False,
                "alternate_metric_quantitative_variance_bound_available": False,
                "alternate_metric_positive_auxiliary_law_derived": True,
                "alternate_metric_positive_law_ideal_weight_globally_bounded": True,
                "alternate_metric_positive_law_quantitative_global_bound_available": True,
                "alternate_metric_positive_law_"
                "quantitative_ideal_weight_variance_bound_available": True,
                "alternate_metric_critical_fiber_chart_enclosures_available": False,
                "alternate_metric_declared_critical_fiber_chart_enclosures_available": True,
                "alternate_metric_complete_global_atlas_coverage_certified": False,
                "alternate_metric_projection_free_positive_weight_engine_available": True,
                "alternate_metric_weight_individual_projection_inverses_required": False,
                "alternate_metric_complete_global_weight_input_coverage_certified": False,
                "alternate_metric_certified_Qomega_intersection_roots_available": True,
                "alternate_metric_certified_chart_and_density_enclosures_available": True,
                "alternate_metric_laurent_coefficient_enclosure_engine_available": True,
                "alternate_metric_bounded_universal_fiber_frame_available": True,
                "alternate_metric_on_demand_original_cochain_section_bounds_available": True,
                "alternate_metric_compressed_complete_section_enclosure_engine_available": True,
                "alternate_metric_complete_bounded_5345_column_matrix_materialized": True,
                "alternate_metric_practical_multi_point_integration_throughput_certified": False,
                "alternate_metric_bounded_section_and_density_evaluation_available": False,
                "alternate_metric_controlled_numerical_sampling_available": False,
                "alternate_up_complete_tensor_comparison_available": False,
                "alternate_up_complete_comparison_indeterminacy_eliminated": False,
                "alternate_up_ordered_exchange_consistent": all(
                    item["reverse_scalar_closed_exact"]
                    and item["exchange_difference_boundary_exact"]
                    for item in exchange_coefficients
                ),
                "alternate_up_ordered_reverse_null_cover_residues": [
                    item["reverse_cover_residue"] for item in exchange_coefficients
                ],
                "alternate_up_full_higgs_cone_comparison_available": False,
                "alternate_up_null_to_null_coefficients_computed": False,
                "alternate_ray_0_1_explicit_cocycles_available": False,
                "first_constituent_atlas_to_mixed_character": frame[
                    "first_constituent_uniform_twist"
                ],
                "second_constituent_atlas_to_mixed_character": frame[
                    "second_constituent_uniform_twist"
                ],
                "atlas_frame_comparison_exact": True,
                "same_constituent_wilson_repair_available": wilson[
                    "both_doublets_without_triplets_possible"
                ],
                "current_full_chain_wilson_multiplicities": wilson[
                    "current_wilson_multiplicities"
                ],
                "same_cover_bundle_relinearization_repair_available": False,
                "lawful_reverse_matter_h0_to_h3": [0, 27, 0, 0],
                "lawful_reverse_dual_matter_h0_to_h3": [0, 0, 27, 0],
                "lawful_reverse_higgs_h0_to_h3": [0, 4, 4, 0],
                "lawful_reverse_wilson_projected_families": 3,
                "lawful_reverse_wilson_projected_higgs_pairs": 0,
                "lawful_reverse_massless_color_triplets": 0,
                "lawful_reverse_structural_spectrum_all_P5": False,
                "lawful_reverse_spectrum_source_assertion_used_as_rank_input": False,
                "reverse_down_universal_matter_character_count": 2,
                "reverse_down_constant_v2_class_count": 4,
                "reverse_down_universal_v1_lift_count": 2,
                "reverse_down_matter_parameter_correction_count": 12,
                "all_reverse_down_matter_lifts_exact": True,
                "reverse_down_extension_point_selected": False,
                "reverse_down_higgs_lift_available": True,
                "reverse_down_higgs_parameter_correction_count": 6,
                "reverse_down_higgs_character_exact": True,
                "reverse_down_higgs_canonical_frame_exact": True,
                "reverse_down_support_exact": True,
                "reverse_down_exterior_zero_slot_count": 4,
                "reverse_down_tree_boundary_zero_slot_count": 4,
                "reverse_down_matrix_rank_upper_bound": 1,
                "reverse_down_central_coefficient_computed": False,
                "reverse_down_v1_pairing_available": True,
                "reverse_down_v1_pairing_term_count": 8892,
                "reverse_down_v1_pairing_exchange_exact": True,
                "reverse_down_v1_pairing_character_exact": True,
                "reverse_down_v1_pairing_reduced_coordinate_count": 0,
                "lawful_chain_diagonal_transfer_seed_count": 4896,
                "lawful_chain_diagonal_squared_zero": True,
                "required_higgs_character": [0, 1],
                "required_higgs_character_space_dimensions": [100, 243, 170],
                "required_higgs_character_differential_ranks": [100, 142],
                "required_higgs_character_h1_dimension": 1,
                "physical_higgs_representative_available": True,
                "physical_higgs_representative_term_count": 27,
                "direct_matter_product_character": [0, 2],
                "direct_matter_product_hull_available": True,
                "equivariant_matter_product_cycle_count": 4,
                "equivariant_matter_product_character": [0, 2],
                "determinant_trace_available": True,
                "scalar_residue_target_available": True,
                "local_determinant_pairings_available": True,
                "complete_tree_level_up_matrix_available": True,
                "tree_level_up_matrix_rank": 0,
                "tree_level_up_scalar_primitives_exact": True,
                "nontrivial_holomorphic_up_matrix_available": False,
                "deformation_diagonal_local_comparison_available": True,
                "global_polynomial_diagonal_comparison_available": False,
                "cech_local_diagonal_comparison_required": True,
                "cech_local_diagonal_chain_map_available": True,
                "canonical_chain_extension_term_count": 1278,
                "first_matter_leg_raw_term_count": 1715173,
                "first_matter_leg_projected_term_count": 866,
                "first_matter_leg_equivariant_term_count": 72099,
                "first_matter_leg_residual_term_count": 7797,
                "first_matter_leg_is_cycle": False,
                "first_matter_leg_partial_scalar_residue": "0",
                "first_higgs_leg_action_term_count": 1593,
                "first_higgs_leg_correction_term_count": 1431,
                "first_higgs_leg_action_is_cycle": True,
                "first_higgs_leg_correction_exact": True,
                "canonical_higgs_leg_action_term_count": 2124,
                "canonical_higgs_leg_correction_term_count": 1908,
                "canonical_higgs_leg_action_is_cycle": True,
                "canonical_higgs_leg_correction_exact": True,
                "bottom_v2_plucker_chain_map_available": True,
                "bottom_v2_plucker_pairing_term_count": 8592,
                "bottom_v2_plucker_exchange_primitive_term_count": 3900,
                "bottom_v2_plucker_equivariant_term_count": 11340,
                "bottom_v2_plucker_character": [0, 2],
                "bottom_v2_plucker_character_exact": True,
                "first_input_level_comparison_primitive_available": True,
                "first_input_level_comparison_primitive_term_count": 105348,
                "first_complete_higher_product_coefficient_available": True,
                "first_complete_higher_product_coefficient": "0",
                "first_complete_higher_product_cochain_term_count": 268905,
                "complete_first_order_coefficient_count": 8,
                "complete_first_order_matrix_available": True,
                "complete_first_order_matrix_rank": 0,
                "complete_first_order_matrix_parameter_basis": ["a0", "a1"],
                "complete_first_order_matrix_extension_point_selected": False,
                "up_maximum_exterior_allowed_parameter_order": 1,
                "up_f5_and_higher_structurally_zero": True,
                "complete_universal_holomorphic_up_matrix_available": True,
                "complete_universal_holomorphic_up_matrix_rank": 0,
                "declared_up_branch_can_reach_rank_three": False,
                "all_published_yukawa_character_products_invariant": True,
                "selected_next_flavor_sector": "down",
                "selected_next_flavor_chain_object_count": 7,
                "selected_next_matter_character": [1, 0],
                "selected_next_higgs_character": [0, 2],
                "flavor_sector_selected_from_observations": False,
                "down_higgs_character_space_dimensions": [100, 243, 176],
                "down_higgs_character_differential_ranks": [100, 143],
                "down_higgs_character_h1_dimension": 0,
                "strict_down_higgs_representative_available": False,
                "down_higgs_character_twist_guessed": False,
                "source_derived_h_d_character_h1_dimension": 1,
                "current_h_d_comparison_route_refuted": True,
                "both_determinant_hom_orientations_blocked": True,
                "legacy_frame_matches_constituent_atlases": False,
                "factor_action_orientations_exact": True,
                "legacy_frame_atlas_mismatch_count": 1,
                "isolated_atlas_line_commutator_term_count": 14,
                "forced_uniform_w1_p_scalar": "-1-omega",
                "uniform_scalar_shifted_character": [1, 2],
                "uniform_scalar_character_space_dimensions": [100, 243, 176],
                "uniform_scalar_differential_ranks": [100, 143],
                "uniform_scalar_shifted_h1_dimension": 0,
                "scalar_higgs_action_repairs_refuted": True,
                "complete_current_higgs_characters": [
                    [0, 0],
                    [0, 1],
                    [2, 0],
                    [2, 1],
                ],
                "selected_source_higgs_characters": [
                    [0, 1],
                    [0, 2],
                    [1, 2],
                    [2, 1],
                ],
                "uniform_higgs_character_shift_matches": [],
                "complete_higgs_character_audit_exact": True,
                "selected_constituent_self_hom_h0_dimensions": [1, 1],
                "selected_constituents_simple_over_q_omega": True,
                "same_constituent_higgs_relinearization_available": False,
                "constituent_atlas_over_synchronized_characters": [
                    [2, 0],
                    [0, 0],
                ],
                "atlas_induced_higgs_characters": [
                    [1, 0],
                    [1, 1],
                    [2, 0],
                    [2, 1],
                ],
                "atlas_higgs_characters_match_selected_source": False,
                "source_action_is_inverse_forward_pullback": True,
                "source_action_higgs_characters": [
                    [0, 0],
                    [0, 2],
                    [1, 0],
                    [1, 2],
                ],
                "source_action_up_higgs_h1_dimension": 0,
                "source_action_down_higgs_h1_dimension": 1,
                "strict_forward_higgs_character": [0, 1],
                "strict_source_higgs_character": [0, 2],
                "strict_source_down_higgs_representative_available": True,
                "prior_physical_flavor_routing_valid": False,
                "selected_available_flavor_sector": "down",
                "selected_available_flavor_chain_object_count": None,
                "selected_available_matter_characters": [[2, 1], [1, 0]],
                "selected_available_forward_matter_characters": [[1, 2], [2, 0]],
                "selected_available_reused_higgs_character": [0, 2],
                "down_universal_matter_character_count": 2,
                "down_universal_v1_class_count": 2,
                "down_universal_v2_lift_count": 4,
                "down_matter_parameter_correction_count": 8,
                "all_down_matter_lifts_exact": True,
                "down_extension_point_selected": False,
                "complete_down_tree_matrix_available": True,
                "complete_down_tree_matrix_rank": 0,
                "down_tree_zero_entries_have_exact_primitives": True,
                "down_tree_extension_point_selected": False,
                "complete_down_first_order_coefficient_count": 8,
                "complete_universal_holomorphic_down_matrix_available": True,
                "complete_universal_holomorphic_down_matrix_rank": 0,
                "down_maximum_exterior_allowed_parameter_order": 1,
                "down_higher_orders_structurally_zero": True,
                "neutrino_universal_matter_character_count": 2,
                "neutrino_universal_v1_class_count": 2,
                "neutrino_universal_v2_lift_count": 4,
                "neutrino_matter_parameter_correction_count": 8,
                "all_neutrino_matter_lifts_exact": True,
                "complete_neutrino_tree_matrix_available": True,
                "complete_neutrino_tree_matrix_rank": 0,
                "neutrino_tree_zero_entries_have_exact_primitives": True,
                "neutrino_tree_extension_point_selected": False,
                "complete_neutrino_first_order_coefficient_count": 8,
                "complete_universal_holomorphic_neutrino_matrix_available": True,
                "complete_universal_holomorphic_neutrino_matrix_rank": 0,
                "neutrino_maximum_exterior_allowed_parameter_order": 1,
                "neutrino_higher_orders_structurally_zero": True,
                "neutrino_extension_point_selected": False,
                "prior_up_matrix_physical_assignment_valid": False,
                "prior_neutrino_matrix_physical_assignment_valid": False,
                "charged_lepton_source_matter_characters": [[0, 0], [0, 1]],
                "charged_lepton_forward_matter_characters": [[0, 0], [0, 2]],
                "charged_lepton_source_higgs_character": [0, 2],
                "charged_lepton_forward_higgs_character": [0, 1],
                "complete_universal_holomorphic_charged_lepton_matrix_available": True,
                "complete_universal_holomorphic_charged_lepton_matrix_rank": 0,
                "charged_lepton_maximum_exterior_allowed_parameter_order": 1,
                "charged_lepton_higher_orders_structurally_zero": True,
                "remaining_current_chain_flavor_sector_available": False,
                "current_carrier_nontrivial_holomorphic_yukawa_available": False,
                "shared_missing_higgs_character": [0, 1],
                "next_exact_frontier_uses_observations": False,
            },
            "invariant_certificate_digest": pair_73["invariant_certificate_digest"],
            "automorphism_certificate_digest": pair_73["certificate_digest"],
            "next_required_object": (
                "close controlled independent metric integration with original complete "
                "section data, verify Ricci-flat/HYM convergence and stabilize one common "
                "vacuum before physical Yukawa normalization; Genesis-to-UV remains unresolved"
            ),
        },
        "necessary_hidden_chamber": hidden_chamber,
        "projective_uniform_input_cells": uniform_input_cells,
        "projective_uncertain_intersections": uncertain_intersections,
        "uncertain_cover_weights": uncertain_weights,
        "uncertain_cover_frames": uncertain_frames,
        "auxiliary_cover_draws": auxiliary_draws,
        "completed_down_lepton_holomorphic_matrices": completed_flavor,
        "claims": _nodes(),
        "dependencies": _edges(),
        "reusable_engines": _engines(),
        "established_results": [
            "the auxiliary mixture has a conditional same-prefix draw workflow "
            "with unbiased exact selectors, native actual roots and weights, "
            "certified branch continuation and retained unresolved requests; "
            "deterministic probes are not an IID cloud or a controlled integral",
            "all fifteen declared uncertain cover domains admit the original "
            "universal quotient and full cochain section probes 0/2655; explicit "
            "center rounding bounds coefficient growth without approximating "
            "exact singleton inputs; no independent cloud, full integrand, "
            "physical metric or stabilized vacuum is supplied",
            "all four complete actual holomorphic matrices have a nonempty common "
            "rank-three open locus without parameter selection; successful down/lepton "
            "all-witness replay and independent scalar/rank arithmetic do not supply "
            "canonical metrics, a common stabilized vacuum or physical masses/mixing",
            "all 9/3/3 admitted uncertain cover branches have positive unchanged "
            "auxiliary weight intervals with native actual coupling, full source/root "
            "error and independent coefficient/determinant checks; no independent "
            "cloud, section integrand, metric or physical normalization is supplied",
            "all eight actual down/lepton mixed scalars equal independent full "
            "Hom composition in the original bases and Higgs-first quotient "
            "volume frame; no Q/L correction solve or F-F scalar is substituted",
            "all eight actual d^c/e^c parameter corrections pass independent "
            "original full differential, atlas, literal quotient-pushout, and "
            "coupled-identity replay; Q/L inputs and original bases are unchanged, "
            "with no import of up/neutrino coupling values into those scalar matrices",
            "the complete actual neutrino matrix has full all-entry scalar "
            "replay and fixed quotient trace; its determinant is "
            "(3/2+3*omega/4)*a0, and its rank-three locus meets the certified "
            "up locus on D(a0*a1) without parameter selection or physical normalization",
            "both actual down-Higgs quotient actions equal independent signed "
            "reciprocal wedges; full archived primitive equations and both "
            "coupled-input constant/linear/quadratic checks pass in the original "
            "differential, without relabelled up data or a complete flavor matrix",
            "two actual E and four actual F classes for d^c and e^c are archived "
            "in the original bases; independent full closure, atlas characters, "
            "nonboundary coordinates, character ranks, and exact producer "
            "reproduction pass without recalculating existing Q or L inputs",
            "six strict alternate neutrino constituent classes and four actual "
            "constant mixed scalars have complete archived witnesses; independent "
            "Hom composition gives literal scalar equality, with fixed quotient "
            "traces and no up-family value or basis identification",
            "exact homogeneous surface-gradient and critical-support identities "
            "give a quantitative global positive-law conormal lower bound and "
            "ideal auxiliary weight variance bound without sampling or physical moduli selection",
            "all 5345 original bounded columns are materialized on one declared "
            "local domain; compressed/raw hashes, complete stream parsing, and "
            "three predecessor probes are independently checked",
            "a Hermitian Schur-complement identity yields projection-free "
            "positive-law weights from the full ambient conormal Gram; the "
            "original sparse Jacobian has a positive three-term determinant "
            "and all 36 declared domain enclosures agree with the old charts",
            "base-eliminating signed residue and positive-density bounds cover "
            "all three partner roots of the six actual axis-critical fibers; "
            "these 18 declared domains do not certify all triangle-node inputs "
            "or a complete global numerical atlas",
            "the positive ambient FS-cube auxiliary law has mass 72 and exact "
            "projective mixture probabilities 3/4,1/8,1/8; its ideal weights "
            "are bounded on the unchanged compact cover; a separate full "
            "polynomial certificate now gives a conservative exact bound "
            "without selecting physical Kahler moduli",
            "the actual A/9 importance weight has finite nonnegative moments "
            "exactly below order three; its finite variance has no numerical "
            "upper bound yet, so quantitative sampling-error control remains open",
            "exact reusable arithmetic, polynomial, homological, Cech, Cox, "
            "sheaf, and geometry engines",
            "published Schoen geometry and selected one-Higgs reference carrier metadata",
            "exact fiber-sensitive dP9 Serre complexes deriving the published "
            "constituent Ext-one dimensions 2 and 5",
            "exact natural dP9 deck actions and simultaneous source-representation "
            "intertwiners for both constituent Ext spaces",
            "source-selected W1/W2 rays recovered as mixed Cech/Koszul cocycles "
            "with exact full-standard-cover lifts",
            "the fixed I3/I6 Ext category has two unused I6 rays passing exact "
            "full-Cech closure and all local dualizing-unit tests",
            "the atlas/common-frame relation is a uniform (2,0) character "
            "on V1 and the identity on V2 after coordinate-lift normalization",
            "the synchronized tensor H1 source-action support is a 2-by-2 "
            "character rectangle, independent of outer extension parameters",
            "local dualizing-unit proofs at all six I3/I6 support points and "
            "twelve locally free affine rank-two pushout presentations",
            "sixty exact ordered overlap gauges forming global constituent "
            "atlases, including hypersurface homotopies and cocycle laws",
            "twenty-four exact localized P/T constituent comparisons preserving "
            "relations and overlaps while satisfying the quotient group laws",
            "selected V1/V2 arrows embedded in the common Schoen grading with "
            "all 567 pulled-back Cech, local-map, and hypersurface-homotopy terms",
            "exact selected mixed outer-Hom transfer deriving cover cohomology "
            "18/54 and 54/18 with square-zero differentials",
            "exact mixed outer P/T transfer deriving fixed dimensions 2/6 and "
            "strict full-Cech invariant representatives",
            "exact lawful universal rank-four cone over P1(Q(omega)) with "
            "affine-origin split locus and no selected extension point",
            "exact lawful reverse universal rank-four cone over P5(Q(omega)) "
            "with affine-origin split locus and no selected extension point",
            "every lawful reverse P5 extension stable on a rational open "
            "Kahler box; nonzero cover c3 excludes a proper connected reduction",
            "orientation-independent exact reverse matter and Higgs cohomology "
            "with three-family one-Higgs Wilson projection over all P5",
            "the proposed reverse P5 physical freeze is blocked by its "
            "nontrivial selected quotient determinant character",
            "both unused I6 atlas rays have exact common-coordinate total "
            "determinant characters (2,1) and (0,1), confirmed on scalar H3",
            "the unique common determinant repairs have conditional Higgs "
            "characters: ray (0,1) passes the fixed Wilson doublet/triplet "
            "screen, while ray (1,1) retains both triplet sectors",
            "the surviving alternate ray (0,1) has exact cover Ext1(V2,V1) "
            "dimension 18 and a two-dimensional strictly deck-invariant "
            "subspace with two closed full-Cech representatives",
            "the ray (0,1) invariant basis assembles an exact non-split "
            "P1 universal rank-four derived cone; the common flat-character "
            "twist cancels its quotient determinant while preserving outer Hom",
            "the published Serre-sequence stability bound applies to every "
            "nonzero alternate P1 extension; exact nine-slope arithmetic "
            "gives a nonempty sufficient chamber with genuine SU(4)",
            "the alternate I6 mixed transfer gives pure H1 of dimension 18; "
            "the unchanged I3 constituent gives 9, so every nonzero P1 "
            "outer class has cover matter H1=27 and three regular deck modules",
            "the alternate P1 determinant filtration and exact Hom action give "
            "Higgs H1 characters leaving one pair and no triplets under the "
            "selected Wilson line, so the whole structural component is frozen",
            "the frozen alternate P1 cone has six strict up-sector matter "
            "classes from two exact I3 constants and eight coefficientwise "
            "I6-to-I3 corrections, without a selected extension point",
            "the alternate Hom H1 has a strict full-Cech character-(2,0) "
            "representative required by the up-Higgs Wilson sector; its "
            "tensor and exterior-cone chain maps remain unavailable",
            "four exact strict-Hom/I6 Yoneda evaluations survive in "
            "H2(Hom(det V1,V1)); their two fixed-basis mixed-entry ratios "
            "are (2-omega)/7 and (-3-2omega)/7, while scalar entries "
            "were subsequently composed with the same-cone Higgs class",
            "four actual constant mixed up-sector entries have exact "
            "Higgs-first quotient residues in the fixed declared bases",
            "four exact mixed up-sector minors force holomorphic rank at "
            "least two for every nonsplit alternate P1 point",
            "two strict null Yoneda combinations are full boundaries "
            "with 90-term primitives; the determinant reduction needs "
            "only two extension-linear null-to-null coefficients, now computed",
            "the natural coherent Higgs quotient has two full closed "
            "connecting arrows; its signed actions reproduce the pinned "
            "primitive identities without pretending the ideal is a vector bundle",
            "both complete ordered null scalars are full cycles with exact "
            "cover residues; the raw tensor differences vanish on the actual "
            "A quotient, with final pairing identification certified later",
            "the nonzero product-cover Hirsch defect has an exact acyclic-carrier "
            "filler; its negative dual supplies the scalar higher compatibility "
            "without asserting the refuted strict rule",
            "the corrected triangular two-row tensor product obeys full Leibniz "
            "in the legitimate A wedge B quotient; both actual 38-object "
            "presentations match the existing Higgs cone and pass full "
            "syzygy/null-matter attacks; the scalar pairing was computed later",
            "the frozen alternate I6 quotient has six distinct local "
            "determinant pairings satisfying all thirty corrected overlap "
            "identities; no Hom-to-tensor chain map follows yet",
            "all sixty minor opens of the alternate I6 quotient carry exact "
            "rank-two duality inverses and syzygy-dual contractions, but "
            "the strict Hom class has not reached a common Higgs complex",
            "the alternate universal holomorphic up matrix has all nine "
            "actual-carrier entries and determinant "
            "(-3/98-39omega/196)a1 in the fixed quotient frame",
            "global generation of a descended vector-bundle extension "
            "follows from quotient-level constituent generation and "
            "vanishing H1 of its subbundle; the actual alternate premises "
            "are certified at H=(14,16,1)",
            "the actual alternate first constituent at descending twist "
            "(5,7,1) has cover H0=1728 and higher cohomology zero; "
            "quotient H0=192 and H1=0; this count alone is not a "
            "quotient-generation proof at that smaller twist",
            "both actual alternate constituents now have complete invariant "
            "section bases at H=(14,16,1), of sizes 2655 and 2690, with "
            "independent exact closure, repaired deck actions, and quotient "
            "image checks; their universal rank-four lift formula is certified",
            "the actual universal rank-four bundle admits explicit local fiber "
            "evaluation with both extension parameters symbolic; four actual "
            "basis columns at an exact cover probe have determinant 1/81",
            "regular-factor coefficient naturality and three actual deck channels "
            "evaluate all 5345 universal sections at the exact probe without "
            "selecting extension parameters; independent full-cochain comparisons "
            "also pass on a distinct complementary chart, but controlled "
            "sampling and numerical metrics remain unavailable",
            "the two physical reverse down-matter sectors lifted exactly over "
            "all six P5 directions without selecting an extension point",
            "the strict physical down-Higgs cocycle lifted over all six "
            "reverse directions through exact determinant-two corrections",
            "rank-two exterior support and exact tree boundaries restrict the "
            "reverse down matrix to one unresolved parameter-linear entry",
            "the physical V1-V1 determinant pairing closes in both cup orders, "
            "has an exact exchange primitive, and descends in character (0,2)",
            "every lawful P1 extension stable in the exact source chamber; "
            "nonzero cover c3 excludes a proper connected reduction",
            "synchronized mixed constituent transfers derive matter cohomology "
            "(0,27,0,0), with free-action Lefschetz compression proving three "
            "regular deck representations",
            "acyclic determinant filtration and lawful relative pushdowns derive "
            "Higgs cohomology (0,4,4,0), one Wilson-projected Higgs pair, and "
            "zero massless color triplets throughout the lawful P1",
            "the proposed P1 physical freeze is blocked by its nontrivial "
            "selected quotient determinant character",
            "all 27 synchronized constituent matter classes have strict full "
            "Schoen Cech--Koszul representatives with exact joint deck characters",
            "the two matter sectors for the first up-type matrix have exact "
            "parameter-linear universal-cone lifts over the full frozen P1",
            "both determinant-twist Hom orientations derive Higgs cohomology "
            "(0,4,4,0), but neither exact deck action matches the physical tensor "
            "characters under a uniform scalar shift",
            "the lawful 48-object direct tensor resolution skeleton is square-zero",
            "retired trivial-character outer complexes retained only as scoped "
            "dimension and transfer diagnostics",
            "relative signatures recover the source Higgs dimension tuple "
            "(0,4,4,0) from selected mixed constituent cocycles",
            "complete 1,440-pair cover Ext and invariant-cocycle screens in "
            "the declared computable category",
            "1,296 exact automorphism quotients including one "
            "square-zero-unipotent exceptional family",
            "exact four-parameter pair-73 Ext family with split origin and "
            "projective nonzero quotient",
            "exact chain-level lifts of all four pair-73 classes and their "
            "universal derived mapping cone",
            "full nonzero pair-73 parameter space is locally free and descended "
            "with trivial determinant and fixed Chern classes",
            "three forced pair-73 subobjects give exact necessary stability walls "
            "with a nonempty Kahler-cone intersection and exclude the full family "
            "at the published polarization anchor",
            "the current minimum blocks 8 and 28 have a universal descended "
            "left-line slope obstruction independent of extension parameters",
            "all 40 declared topology blocks are partitioned by exact forced "
            "subobject slope signs without completing automorphism quotients",
            "candidates 15 and 35 have an exact nonempty common necessary "
            "forced-subobject chamber with rational one-parameter certificates",
            "the dimension-42/48 block has an exact positive slope identity "
            "between two unavoidable subbundles, making its chamber empty",
            "all candidate-4/24 right-line restriction maps have exact rank 20; "
            "their unstable lifting loci are projective linear subspaces of "
            "codimension 20",
            "the candidate-4/24 nonlifting complements admit an exact nonempty "
            "necessary forced-subobject chamber with rational witnesses",
            "all 288 maximal quotient-generator restrictions have proper "
            "unstable kernels, leaving nonempty generic complements",
            "the unique lower-line section has identically zero outer-Hom "
            "pullback in every candidate-4/24 family",
            "the same exact lower-line screen exhausts all 72 candidate-5/25 "
            "families in the declared monomial category",
            "the sparse Schoen engine accepts exact base pushouts directly and "
            "checks both published-carrier Hom orientations",
            "finite HPL projection, strict re-inclusion, and exact Reynolds "
            "projection close all four split matter products as distinct cycles "
            "of character (0,2) in the grouped Higgs complex",
            "virtual determinant cancellation and adjunction identify the unique "
            "ordered degree-three scalar residue target",
            "complementary maximal minors give exact local determinant pairings "
            "with hypersurface-corrected covariance on all sixty overlaps",
            "the unique grouped determinant orientation gives a complete exact "
            "rank-zero tree-level up matrix, with four explicit scalar primitives",
            "the common-Schoen second pencil has exact two-chart diagonal lifts "
            "whose overlap difference is its Koszul syzygy; negative required "
            "q degrees exclude a global homogeneous polynomial replacement",
            "the signed two-chart comparison extends to an exact Cech chain "
            "map in all four Koszul summands, with each tensor extension term "
            "carried once under the identity on unused cover factors",
            "the first a0 matter leg transfers exactly to 72,099 character "
            "terms with a 7,797-term noncycle residual and zero partial scalar "
            "residue, so it is not promoted to a higher product",
            "the complementary a0 Higgs action is an exact 1,593-term "
            "determinant-line cycle with an explicit 1,431-term correction; "
            "an exact Cech-Koszul line isomorphism maps these to canonical "
            "2,124-term and 1,908-term cochains",
            "published Wilson characters make all four Yukawa triples invariant "
            "and select the down sector as the seven-object minimum next workload",
            "the exact current-chain down-Higgs character complex has H1 zero, "
            "so fail-closed reranking selects the eight-object neutrino sector",
            "both neutrino matter characters have exact universal lifts with "
            "all eight parameter corrections certified over the frozen P1",
            "the complete Dirac-neutrino tree matrix has four independent "
            "exact zero residues with explicit depth-four primitives",
            "the source-derived H_d character-(0,2) H1 has dimension one while "
            "the current synchronized action has dimension zero, refuting an "
            "equivariant quasi-isomorphism for that action",
            "the inverse deck orientation on the second synchronized base makes "
            "both W2 extension-line frames agree with their exact atlas; only "
            "the W1/P frame remains discrepant",
            "the isolated W1/P atlas line substitution has a nonzero 14-term "
            "commutator, while its forced uniform omega^2 propagation is an "
            "exact action whose shifted character-(1,2) H1 remains zero",
            "one shared ambient transfer derives current synchronized Higgs H1 "
            "characters (0,0), (0,1), (2,0), and (2,1)",
        ],
        "scoped_no_go_results": [
            "conditional on an equivariant outer extension and the certified "
            "rank-two character identity, the determinant-repaired ray (1,1) "
            "cannot meet the fixed-Wilson zero-triplet requirement",
            "any equivariant outer extension preserving either unused I6 "
            "atlas pair fails quotient SU(4); other linearisations and "
            "underlying bundles remain untested",
            "the selected mixed constituent frames have total determinant "
            "character (2,1), so this quotient SU(4) claim is uncertified; "
            "a distinct published carrier is not refuted",
            "the unique common rank-four character twist that cancels the "
            "selected determinant removes both Higgs doublet sectors and "
            "introduces a color-antitriplet under the fixed Wilson line",
            "both cross-Hom H0 spaces vanish and both constituents are simple; "
            "every nonsplit selected P1/P5 extension is simple, so no other "
            "same-bundle linearization can repair the fixed Wilson spectrum",
            "the W1 atlas P extension-line scalar is 1 but the mixed frame "
            "uses omega; replacing only that scalar creates a 72-term "
            "outer-Hom chain commutator, so a one-entry repair is invalid",
            "the same simple constituent pair cannot yield both fixed-Wilson "
            "Higgs doublets without a color triplet under any factorwise "
            "character shift; the atlas-bound shift leaves one antitriplet",
            "declared projective Tier A ray pairs have zero invariant Ext-one classes",
            "current curvilinear rank-four Chern type has the wrong quotient index",
            "declared monomial and transported finite linearization categories "
            "have no complete commuting lift pairs where recorded",
            "pair 73 has empty slope-stable locus because the right Serre line "
            "lifts universally with slope opposite to the left rank-two subbundle",
            "all 72 four-dimensional invariant-Ext families in candidates 3 and "
            "23 have the same exact lifted-line stability obstruction",
            "all 72 six/eight-dimensional invariant-Ext families in candidates "
            "14 and 34 lift a line with strictly positive Kahler-cone slope",
            "all 72 eight/ten-dimensional invariant-Ext families in candidates "
            "8 and 28 contain a descended line with strictly positive Kahler-cone slope",
            "18 topology blocks containing 648 families have a coefficient-positive "
            "forced subbundle and therefore no slope-stable extension",
            "all 72 families in candidates 15 and 35 lift a right Serre line "
            "with strictly positive slope despite their nonempty necessary chamber",
            "all 72 families in candidates 16 and 36 have incompatible negative-slope "
            "requirements for the right-line preimage and universally lifted line",
            "all 72 families in candidates 4 and 24 lift a descended lower line "
            "whose slope and the forced left-line slope sum to a strictly "
            "positive fiber-class slope",
            "the final 72 families in candidates 5 and 25 have the same exact "
            "positive fiber-slope contradiction, exhausting only the declared "
            "finite monomial category",
            "the available projective I3/I6 pushouts give cover Ext-one "
            "dimensions 0/63 rather than the published 36/72, so they cannot "
            "stand in for fiber-sensitive W1/W2 presentations",
            "the fixed constituent kernel line is not the source-selected "
            "W1/W2 ray; its pure-Cech mapping cones and downstream outer "
            "objects are scoped diagnostics rather than carrier reconstructions",
            "the current 14-dimensional diagonal Higgs cone has exact character "
            "multiplicities 3,2,3,2,2,2; missing and repeated lawful sectors "
            "rule out character projection as a four-class selector",
            "the two lawful determinant-twist Hom orientations have raw "
            "characters (1,0), (1,1), (2,0), (2,1) and (1,0), (1,2), "
            "(2,0), (2,2); neither admits a uniform scalar shift to the physical "
            "tensor characters",
            "naively merging the two lawful full Koszul--Cech arrow sets gives "
            "an exact three-term differential-square witness, so a genuine "
            "chain diagonal is required; three witnesses eliminate all 4,096 "
            "declared static-plus-live linear parity repairs",
            "the canonical independent-cover tensor followed by the exact fiber "
            "diagonal closes on all 4,896 ambient transfer seeds",
            "the source-required P/T character (0,1) has exact transferred "
            "dimensions 100-to-243-to-170, differential ranks 100/142, and a "
            "unique H1 class represented by a strict 27-term full cocycle",
            "the complete lawful tree-level up matrix is exactly zero: all four "
            "character-allowed scalar cycles have explicit depth-four primitives",
            "the first source-derived V2 Pluecker pairing closes in both cup "
            "orders, has an explicit exchange primitive, and projects exactly "
            "to character (0,2)",
            "the first complete a0 lower-(1,1) higher-product coefficient has "
            "an invariant comparison primitive and exact zero residue",
            "all eight first-order higher-product coefficients close exactly "
            "with zero residue, so the universal first-order up matrix has rank zero",
            "finite exterior-filtration typing excludes f5 and every higher "
            "up-type contribution, proving the full universal up matrix has rank zero",
            "the current chain action has exact H1 dimension zero in the "
            "source-required down-Higgs character (0,2)",
            "all eight universal Dirac-neutrino coefficients have distinct "
            "exact closed cochains but zero residue; exterior filtration "
            "excludes higher orders, proving rank zero on the frozen P1",
            "isotypic H1 dimensions one and zero refute the current source-to-"
            "synchronized-chain equivariant comparison for H_d character (0,2)",
            "neither the isolated W1/P atlas line replacement nor its unique "
            "connected uniform scalar propagation recovers the missing H_d class",
            "none of the nine uniform Z3 x Z3 character shifts maps the complete "
            "current Higgs H1 representation to the selected source multiset",
            "both selected mixed constituents are simple over Q(omega), so every "
            "same-object factorwise relinearization reduces to an exhausted shift",
            "the certified constituent atlases force Higgs characters (1,0), "
            "(1,1), (2,0), and (2,1), incompatible with the source-bound multiset",
        ],
        "open_assumptions": [
            "quantum postulates, Lorentzian causality, Einstein gravity, and dimensional constants",
            "heterotic E8 x E8 as the conditional UV realization",
            "Schoen compactification and published one-Higgs model as selected realization data",
            "three families and one Higgs pair as selection constraints rather than predictions",
        ],
        "experimental_prototypes": [
            "rank-four transition and horseshoe constructors",
            "common-DGA and HPL machinery",
            "complete natural quotient null-scalar evaluator with both "
            "exact coefficient residues certified",
            "metric, conic-Pfaffian, hidden-bundle, and low-energy sufficiency audits",
            "finite-pole point evaluation agrees with all 5345 archived exact columns; "
            "practical multi-point throughput and numerical sampling remain uncertified",
            "original finite-pole evaluation carries certified coefficient bounds "
            "for every archived index; finite/infinity three-index packets are "
            "not a sampling law; complete single-domain output is now separately certified",
        ],
        "blocked_physical_calculations": [
            "equivariantly trivial quotient determinant with preserved Wilson spectrum",
            "atlas-derived relative-pushdown line characters resolving the "
            "unavailable down-Higgs representation",
            "the first nontrivial deformation or higher-product Yukawa contribution",
            "alternate-carrier matter metrics and remaining flavor matrices",
            "physical normalization, hidden sector, vacuum, and low-energy predictions",
        ],
        "duplicated_calculations": [
            {
                "areas": ["published visible carrier metadata", "computable carrier search"],
                "disposition": (
                    "keep separate: one is a selected reference and the other "
                    "must be generated independently"
                ),
            },
            {
                "areas": [
                    "generic production homological engines",
                    "research-specific Schoen totalizations",
                ],
                "disposition": (
                    "reuse production primitives; retain geometry-specific "
                    "orchestration in research until promotion"
                ),
            },
            {
                "areas": ["partial automorphism enumeration", "candidate structural trichotomy"],
                "disposition": (
                    "suspend remaining enumeration and seek a family-level "
                    "theorem unless an exception becomes decision-relevant"
                ),
            },
        ],
        "structural_compression_questions": [
            {
                "question": (
                    "Can H2(E)=0 and the one-way outer row replace separate "
                    "matter-lift existence searches by one character-equivariant "
                    "universal theorem, leaving only needed literal coefficients?"
                ),
                "evidence": (
                    "twenty-four archived up/neutrino/d/e coefficient corrections use "
                    "the same full equation, strict atlas projection, and "
                    "parameter-linear quotient pushout in the same frozen carrier"
                ),
                "attack": (
                    "check exact H2(E) vanishing, full row nilpotence, and "
                    "commutation with both atlas generators before quantifying "
                    "over all classes; this would certify existence and "
                    "truncation, not assign any uncomputed primitive, scalar, "
                    "physical normalization, or moduli value"
                ),
            },
            {
                "question": (
                    "Can the ambient conormal Gram eliminate individual "
                    "projection inverses from all positive-law weights?"
                ),
                "evidence": (
                    "18 regular and 18 axis-critical domains use the same "
                    "residue-to-FS-cube ratio in different free frames"
                ),
                "attack": (
                    "closed by the Hermitian Schur-complement proof, independent "
                    "full ambient inverse/determinant checks, exact source points, "
                    "and all 36 declared domains. The separate full polynomial "
                    "certificate now supplies a conservative global lower bound; "
                    "global input coverage and sampling error remain open gates"
                ),
            },
            {
                "question": (
                    "Can common regular monomials make all bounded section "
                    "corrections reuse a small set of finite-pole responses?"
                ),
                "evidence": (
                    "the first outer column took about 72 seconds after setup; "
                    "the next nine reused 36 correction units and 4707 original "
                    "operator columns at roughly 0.1 seconds each. Actual V2 "
                    "source keys number 1972; common-monomial normalization "
                    "would reduce that static count to 1477 per parameter"
                ),
                "attack": (
                    "normalization is not implemented or certified. Its modest "
                    "key-count reduction does not justify replacing the verified "
                    "engine for controlled integration without a certified "
                    "cost/accuracy improvement. Complete single-domain output "
                    "is now verified; practical multi-point throughput remains open"
                ),
            },
            {
                "question": (
                    "Can regular polynomial coefficients be specialized before "
                    "the certified lifting series rather than expanding full "
                    "cover cochains for every metric section value?"
                ),
                "evidence": (
                    "all actual target second-plane exponents are nonnegative; "
                    "raw incidence and homotopy depend only on Laurent support "
                    "and structural parity, while object and equation arrows "
                    "preserve regularity"
                ),
                "attack": (
                    "closed for exact point evaluation by polynomial coefficient "
                    "naturality, operator commutation, independent full-cochain "
                    "probes on two charts, projective rescaling, and a deliberate "
                    "deck-phase mutation; reusable controlled numerical sampling "
                    "is not established by a point matrix"
                ),
            },
            {
                "question": (
                    "Can one degree-support and nilpotent-filtration theorem "
                    "replace 5380 independent outer coefficient solves?"
                ),
                "evidence": (
                    "all 24 actual ambient target components have no positive "
                    "reduced degree; all mixed arrows raise a weight in [0,4]"
                ),
                "attack": (
                    "closed by 10816 independent signed support columns, twenty "
                    "actual source-module composition columns, repaired target "
                    "arrow equivariance, and a finite residual-iteration proof; "
                    "full expanded coefficient replay is not required or claimed"
                ),
            },
            {
                "question": (
                    "Can the actual constituent Serre lifts be transported "
                    "from finitely many P1 templates rather than solved "
                    "separately for every generating section?"
                ),
                "evidence": (
                    "nine V1 and twelve actual alternate V2 templates lift "
                    "1540 and 1555 quotient sections; all extension arrows "
                    "are plane-polynomial with only P1-overlap poles"
                ),
                "attack": (
                    "check the complete source arrow sets, both Laurent-pole "
                    "directions, repaired actions, and every full residual; "
                    "polynomial-linearity proves the transport for these "
                    "constituents, but does not solve universal outer lifts"
                ),
            },
            {
                "question": (
                    "Do the exact mixed null Yoneda boundaries eliminate the "
                    "indeterminacy of the natural null-to-null product comparison?"
                ),
                "evidence": (
                    "both actual 90-term null primitives are line boundaries; "
                    "H1(B1 inverse) and Hom(det F,K) vanish, while matter-product "
                    "H2(K) indeterminacy is five-dimensional on the cover "
                    "and has not been eliminated"
                ),
                "attack": (
                    "derive the remaining comparison groups and reachable "
                    "tensor homotopies; the line support is checked for these "
                    "actual witnesses, but exchange symmetry does not prove "
                    "agreement with the natural exterior map"
                ),
            },
            {
                "question": (
                    "When do constituent endomorphism radicals act trivially "
                    "on Ext before or only after quotient reduction?"
                ),
                "evidence": (
                    "1,296 exact actions repeatedly show direct scalar, "
                    "quotient-reduced scalar, and one square-zero-unipotent type"
                ),
                "attack": (
                    "derive the action from presentation characters and "
                    "deliberately test singular and factor-exchanged sectors"
                ),
            },
            {
                "question": (
                    "Does either candidate-4/24 nonlifting open complement "
                    "contain a slope-stable extension?"
                ),
                "evidence": (
                    "the exact rank-20 restriction removes the right-line lift "
                    "off P^29 inside P^49 and P^31 inside P^51; the remaining "
                    "forced slopes are negative at (5,1,7) after orientation; "
                    "four generator-line kernels per pair are also proper"
                ),
                "attack": (
                    "construct chain maps for the lower proper sublines, then "
                    "classify rank-two and dual rank-three conditions"
                ),
            },
        ],
        "research_value_scheduler": _scheduler(),
        "fitted_inputs": [],
        "observation_leakage": {
            "observations_used_as_geometry_or_carrier_inputs": False,
            "observations_used_as_vacuum_or_rank_lifting_inputs": False,
            "allowed_role": "terminal comparison and falsification only",
        },
    }
    payload["artifact_digest"] = _canonical_digest(payload)
    return payload


def validate_state(payload: dict[str, object]) -> None:
    """Fail closed on malformed epistemic claims or dependency governance."""

    digest = payload.get("artifact_digest")
    unsigned = dict(payload)
    unsigned.pop("artifact_digest", None)
    if not isinstance(digest, str) or digest != _canonical_digest(unsigned):
        raise ValueError("ScientificGenesisState digest does not verify")
    claims = payload.get("claims")
    edges = payload.get("dependencies")
    if not isinstance(claims, list) or not isinstance(edges, list):
        raise ValueError("claims and dependencies must be arrays")
    identifiers: set[str] = set()
    for claim in claims:
        if not isinstance(claim, dict):
            raise ValueError("claim records must be objects")
        identifier = claim.get("id")
        status = claim.get("status")
        if not isinstance(identifier, str) or identifier in identifiers:
            raise ValueError("claim identifiers must be unique strings")
        if status not in STATUSES:
            raise ValueError(f"claim {identifier} has an invalid status")
        if status == "BLOCKED" and not claim.get("missing_prerequisites"):
            raise ValueError(f"blocked claim {identifier} lacks prerequisites")
        if not claim.get("evidence"):
            raise ValueError(f"claim {identifier} lacks evidence")
        identifiers.add(identifier)

    adjacency: dict[str, set[str]] = {identifier: set() for identifier in identifiers}
    indegree = {identifier: 0 for identifier in identifiers}
    for edge in edges:
        if not isinstance(edge, dict):
            raise ValueError("dependency records must be objects")
        source = edge.get("source")
        target = edge.get("target")
        if source not in identifiers or target not in identifiers or source == target:
            raise ValueError("dependency endpoints must be distinct known claims")
        for key in (
            "mathematical_reason",
            "implementation_or_artifact",
            "assumptions_required",
            "implication",
            "known_failure_modes",
        ):
            if key not in edge:
                raise ValueError(f"dependency {source}->{target} lacks {key}")
        if target not in adjacency[str(source)]:
            adjacency[str(source)].add(str(target))
            indegree[str(target)] += 1

    queue = sorted(node for node, degree in indegree.items() if degree == 0)
    visited = 0
    while queue:
        node = queue.pop(0)
        visited += 1
        for target in sorted(adjacency[node]):
            indegree[target] -= 1
            if indegree[target] == 0:
                queue.append(target)
    if visited != len(identifiers):
        raise ValueError("scientific dependency graph contains a cycle")

    engines = payload.get("reusable_engines", [])
    if not isinstance(engines, list):
        raise ValueError("reusable engines must be an array")
    for engine in engines:
        if not isinstance(engine, dict):
            raise ValueError("engine records must be objects")
        for relative in engine.get("locations", []):
            if not isinstance(relative, str) or not (ROOT / relative).exists():
                raise ValueError(f"reusable engine evidence is missing: {relative}")
    scheduler = payload.get("research_value_scheduler", [])
    if not isinstance(scheduler, list):
        raise ValueError("research scheduler must be an array")
    for item in scheduler:
        if not isinstance(item, dict) or not isinstance(item.get("scores"), dict):
            raise ValueError("scheduler entries require score objects")
        if any(
            not isinstance(value, int) or not 1 <= value <= 5 for value in item["scores"].values()
        ):
            raise ValueError("scheduler scores must be integers from one through five")
    if payload.get("fitted_inputs") != []:
        raise ValueError("the current state must not silently admit fitted inputs")


def write_state(path: Path = OUTPUT) -> dict[str, object]:
    """Build, validate, and atomically write the ScientificGenesisState."""

    payload = build_state()
    validate_state(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)
    return payload


def main() -> int:
    """Regenerate the state and print its governing checkpoint."""

    payload = write_state()
    checkpoint = cast(dict[str, object], payload["automorphism_checkpoint"])
    vertical_path = cast(dict[str, object], payload["recommended_vertical_path"])
    path = OUTPUT.relative_to(ROOT)
    print(f"state: {path}")
    print(f"artifact_digest: {payload['artifact_digest']}")
    print(f"claim_count: {len(cast(list[object], payload['claims']))}")
    print(f"dependency_count: {len(cast(list[object], payload['dependencies']))}")
    print(
        f"automorphism_checkpoint: {checkpoint['completed_pairs']}/{checkpoint['declared_pairs']}"
    )
    print(f"next_required_object: {vertical_path['next_required_object']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
