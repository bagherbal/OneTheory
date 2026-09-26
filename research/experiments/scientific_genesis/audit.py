"""Generate and validate the machine-readable Scientific Genesis state.

Owns:
    Evidence-backed claim nodes, dependency edges, reusable-engine inventory,
    scoped results, structural questions, and a research-value scheduler.

Depends on:
    Standard-library inspection of repository sources and generated artifacts.

Must not:
    Infer scientific truth from file presence, choose an extension coordinate,
    complete a missing physical edge, or import observations as source inputs.

Phase 0:
    Deterministic state reconstruction is available; all scientific statuses
    remain bounded by the evidence serialized here.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Final

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
            "strict atlas character (2,0). The certified determinant and "
            "common flat frames send this character to the selected "
            "up-Higgs forward sector (0,2). No tensor chain map or "
            "exterior-cone Higgs cocycle is asserted.",
            (
                "data/generated/scientific_genesis/"
                "alternate_up_higgs_hom_representative.json",
                "research/experiments/scientific_genesis/"
                "alternate_up_higgs_hom_representative.py",
                "tests/integration/"
                "test_scientific_genesis_alternate_up_higgs_hom_representative.py",
            ),
            ("certified Hom action", "selected published Wilson sector"),
            ("rank-two determinant chain map", "exterior-cone Higgs lift"),
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
            "alternate_up_yukawa_support",
            "universal up-matrix filtration support",
            "Flavor",
            "DERIVED",
            "The one-plus-two constituent matter bases and acyclic "
            "determinant filtration force the E-E slot to vanish, the "
            "E-F slots to be parameter-independent, and the F-F block "
            "to be linear in the two outer parameters. Consequently the "
            "three-by-three determinant is linear if nonzero; its two "
            "coefficients remain uncomputed.",
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
            ("same-cone Higgs chain class", "two determinant coefficients"),
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
            "BLOCKED",
            "The complete carrier-derived tree-level up matrix is exactly zero. "
            "The first parameter-linear matter leg and complementary Higgs lift "
            "are exact scoped results, and the bottom V2 Pluecker pairing is "
            "closed and equivariant. All eight complete first-order "
            "coefficients vanish exactly. Exterior-filtration truncation proves "
            "that the full universal up matrix has rank zero, so this branch "
            "cannot supply the required nontrivial matrix. Convention-corrected "
            "down and charged-lepton matrices also vanish exactly through every "
            "exterior-allowed order. The prior Dirac-neutrino assignment is "
            "withdrawn. No available flavor sector on this frozen carrier "
            "realization supplies the first nontrivial holomorphic matrix.",
            (
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
            missing=(
                "exact replacement constituent or carrier realization with a "
                "nontrivial holomorphic Yukawa matrix",
            ),
        ),
        _node(
            "visible_metrics",
            "Ricci-flat, HYM, and matter metric package",
            "Normalization",
            "BLOCKED",
            "Generic section machinery exists, but carrier cocycles, section "
            "bases, global-generation proof, and converged metrics are absent.",
            ("src/onetheory/math/sections.py", "research/experiments/visible_metrics/audit.py"),
            missing=(
                "carrier extension cocycles",
                "positive-twist section package",
                "global generation",
                "converged Ricci-flat and HYM metrics",
            ),
        ),
        _node(
            "physical_yukawas",
            "canonically normalized physical Yukawas",
            "Normalization",
            "BLOCKED",
            "Canonical-normalization laws exist, but holomorphic matrices, "
            "positive metrics, and a common stabilized context do not.",
            ("src/onetheory/physics/observables.py", "src/onetheory/physics/matter.py"),
            missing=(
                "all holomorphic Yukawa sectors",
                "positive matter and Higgs metrics",
                "stabilized common vacuum",
            ),
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
            ("the 324-term Hom cocycle has not been transported",),
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
            ("the first nontrivial holomorphic Yukawa remains unresolved",),
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
            ("the first nontrivial holomorphic Yukawa remains unresolved",),
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
            "computable_carrier_state",
            "visible_metrics",
            "Metric construction needs the explicit carrier and extension cocycles.",
            ("research/experiments/visible_metrics/audit.py",),
            (),
            True,
            ("global generation or numerical convergence may fail",),
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
            "metrics",
            "generic numerical laws and carrier boundary only",
            (
                "src/onetheory/models/heterotic_schoen/metrics.py",
                "research/experiments/visible_metrics/audit.py",
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
            "distinct_constituent_realization_screen",
            5,
            5,
            5,
            5,
            2,
            1,
            "Test the two unused locally free I6 rays for descent and Higgs support.",
        ),
        (
            "distinct_su4_carrier_screen",
            5,
            4,
            5,
            5,
            4,
            2,
            "Screen a distinct underlying bundle against exact carrier gates.",
        ),
        (
            "lawful_carrier_common_dga_lifts",
            2,
            4,
            2,
            5,
            5,
            4,
            "Existing lifts remain conditional until a physical carrier is certified.",
        ),
        (
            "minimal_common_dga_yukawa_slice",
            2,
            4,
            2,
            5,
            5,
            4,
            "A physical matrix cannot precede the corrected determinant gate.",
        ),
        (
            "automorphism_trichotomy_theorem",
            3,
            4,
            4,
            5,
            3,
            2,
            "Compresses repeated action data without blocking carrier construction.",
        ),
        (
            "lawful_carrier_global_generation",
            3,
            3,
            4,
            4,
            4,
            3,
            "Screens the later metric route before expensive numerical geometry.",
        ),
        (
            "first_tree_rank_explanation",
            4,
            4,
            5,
            5,
            4,
            2,
            "Determines whether higher products are mathematically required.",
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
    return sorted(records, key=lambda item: (-float(item["priority_score"]), str(item["task"])))


def build_state() -> dict[str, object]:
    """Inspect authoritative artifacts and assemble the deterministic state."""

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
        "alternate_constituent_determinant_pairing.json",
        "data/generated/scientific_genesis/"
        "alternate_constituent_duality_local_inverse.json",
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
            "collected_tests_at_audit": 653,
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
                "construct the strict up-Higgs cocycle on the frozen "
                "alternate P1 cone, then compute one complete exact "
                "holomorphic 3x3 up-type Yukawa matrix"
            ),
        },
        "claims": _nodes(),
        "dependencies": _edges(),
        "reusable_engines": _engines(),
        "established_results": [
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
            "the frozen alternate I6 quotient has six distinct local "
            "determinant pairings satisfying all thirty corrected overlap "
            "identities; no Hom-to-tensor chain map follows yet",
            "all sixty minor opens of the alternate I6 quotient carry exact "
            "rank-two duality inverses and syzygy-dual contractions, but "
            "the strict Hom class has not reached a common Higgs complex",
            "the alternate universal up matrix has an exterior-forced zero "
            "E-E slot, constant mixed slots, and a parameter-linear F-F "
            "block; its determinant coefficients are uncomputed",
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
            "metric, conic-Pfaffian, hidden-bundle, and low-energy sufficiency audits",
        ],
        "blocked_physical_calculations": [
            "equivariantly trivial quotient determinant with preserved Wilson spectrum",
            "atlas-derived relative-pushdown line characters resolving the "
            "unavailable down-Higgs representation",
            "the first nontrivial deformation or higher-product Yukawa contribution",
            "carrier-derived nontrivial holomorphic Yukawa matrix",
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

    for engine in payload.get("reusable_engines", []):
        if not isinstance(engine, dict):
            raise ValueError("engine records must be objects")
        for relative in engine.get("locations", []):
            if not isinstance(relative, str) or not (ROOT / relative).exists():
                raise ValueError(f"reusable engine evidence is missing: {relative}")
    for item in payload.get("research_value_scheduler", []):
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
    checkpoint = payload["automorphism_checkpoint"]
    path = OUTPUT.relative_to(ROOT)
    print(f"state: {path}")
    print(f"artifact_digest: {payload['artifact_digest']}")
    print(f"claim_count: {len(payload['claims'])}")
    print(f"dependency_count: {len(payload['dependencies'])}")
    print(
        f"automorphism_checkpoint: {checkpoint['completed_pairs']}/{checkpoint['declared_pairs']}"
    )
    print(f"next_required_object: {payload['recommended_vertical_path']['next_required_object']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
