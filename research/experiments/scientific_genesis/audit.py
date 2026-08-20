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
            "published constituent deck-linearized cocycles",
            "Reference realization",
            "COMPUTED",
            "Natural dP9 chain actions are derived exactly. The unique common "
            "character matching the published W1/W2 representations is "
            "source-selected explicitly, yielding one invariant Ext class each.",
            (
                "data/generated/scientific_genesis/"
                "published_constituent_deck_actions.json",
                "research/experiments/computable_carrier/"
                "dp9_serre_actions.py",
                "tests/integration/"
                "test_scientific_genesis_published_constituent_deck_actions.py",
            ),
            ("published constituent equivariant representations",),
        ),
        _node(
            "published_constituent_mapping_cones",
            "published constituent derived mapping cones",
            "Reference realization",
            "COMPUTED",
            "Each invariant W1/W2 class lifts to the exact maximal-minor tuple "
            "divided by mu nu. Cech closure and Hilbert--Burch closure certify "
            "the corresponding derived block differential squares to zero.",
            (
                "data/generated/scientific_genesis/"
                "published_constituent_mapping_cones.json",
                "research/experiments/computable_carrier/"
                "dp9_serre_cech.py",
                "tests/integration/"
                "test_scientific_genesis_published_constituent_mapping_cones.py",
            ),
            ("published Cayley-Bacharach local-freeness theorem",),
        ),
        _node(
            "published_outer_reduced_model",
            "published outer cohomology-reduced model",
            "Reference realization",
            "COMPUTED",
            "The fiber-sensitive twisted constituents give exact square-zero "
            "reduced outer complexes with forward H1/H2 126/162 and reverse "
            "162/126. Both preserve the published Euler characteristic while "
            "exhibiting one common 90-dimensional excess.",
            (
                "data/generated/scientific_genesis/"
                "published_outer_reduced_mismatch.json",
                "research/experiments/computable_carrier/"
                "schoen_serre_outer.py",
                "tests/integration/"
                "test_scientific_genesis_published_outer_reduced_mismatch.py",
            ),
        ),
        _node(
            "published_outer_cech_transfer",
            "published full-Cech outer hypercohomology",
            "Reference realization",
            "COMPUTED",
            "Canonical standard-cover contraction and finite homological "
            "perturbation derive square-zero outer complexes with forward "
            "H1/H2 36/72 and reverse 72/36 without rank fitting.",
            (
                "data/generated/scientific_genesis/"
                "published_outer_cech_transfer.json",
                "research/experiments/computable_carrier/"
                "schoen_serre_outer_transfer.py",
                "tests/integration/"
                "test_scientific_genesis_published_outer_cech_transfer.py",
            ),
        ),
        _node(
            "published_outer_cech_invariants",
            "published invariant outer Cech representatives",
            "Reference realization",
            "COMPUTED",
            "Exact p' g i' transfer derives commuting order-three deck actions "
            "on cover H1. Their common fixed spaces have dimensions four and "
            "eight, with strict Reynolds-averaged representatives in one "
            "full Cech-Koszul complex.",
            (
                "data/generated/scientific_genesis/"
                "published_outer_cech_invariants.json",
                "research/experiments/computable_carrier/"
                "schoen_serre_outer_transfer_actions.py",
                "tests/integration/"
                "test_scientific_genesis_published_outer_cech_invariants.py",
            ),
            ("published constituent equivariant structures",),
        ),
        _node(
            "published_outer_universal_cone",
            "published universal outer mapping cone",
            "Reference realization",
            "COMPUTED",
            "The four strict forward classes assemble over Q(omega)[a0,...,a3] "
            "into a parameter-linear rank-four block cone. Its square-zero, "
            "non-split, local-freeness, determinant, Chern, and descent gates "
            "close without selecting a projective point.",
            (
                "data/generated/scientific_genesis/"
                "published_outer_universal_cone.json",
                "research/experiments/scientific_genesis/"
                "published_outer_universal_cone.py",
                "tests/integration/"
                "test_scientific_genesis_published_outer_universal_cone.py",
            ),
            ("published constituent local-freeness theorem",),
        ),
        _node(
            "published_outer_stability_locus",
            "published generic stable SU(4) outer locus",
            "Reference realization",
            "PROVED",
            "The source-generic extension theorem pulls back to a nonempty "
            "Zariski-open U_pub in the reconstructed P3. Nine exact slope "
            "inequalities define K^s, a rational open box proves it nonempty, "
            "and stable determinant-trivial rank four with nonzero c3 excludes "
            "proper connected irreducible structure-group reductions.",
            (
                "data/generated/scientific_genesis/"
                "published_outer_stability_locus.json",
                "research/experiments/scientific_genesis/"
                "published_outer_stability_locus.py",
                "tests/integration/"
                "test_scientific_genesis_published_outer_stability_locus.py",
                "data/published/visible_carrier/source_manifest.json",
            ),
            (
                "published generic stability theorem",
                "Donaldson--Uhlenbeck--Yau correspondence",
                "classification of connected irreducible subgroups of SU(4)",
            ),
        ),
        _node(
            "published_matter_cohomology",
            "published universal-family matter cohomology",
            "Reference realization",
            "COMPUTED",
            "Full transferred constituent complexes derive H1(V1)=Reg(G) "
            "and H1(V2)=2 Reg(G), with all other constituent cohomology zero. "
            "The outer long exact sequence therefore gives H1(V)=3 Reg(G) "
            "and H1(V dual)=0 for every extension parameter; the Wilson "
            "projection yields three complete families including nu_R.",
            (
                "data/generated/scientific_genesis/"
                "published_matter_cohomology.json",
                "research/experiments/scientific_genesis/"
                "published_matter_cohomology.py",
                "tests/integration/"
                "test_scientific_genesis_published_matter_cohomology.py",
            ),
            (
                "published Wilson-line embedding",
                "Calabi--Yau Serre duality",
                "Maschke semisimplicity in characteristic zero",
            ),
        ),
        _node(
            "published_higgs_cohomology",
            "published universal-family Higgs cohomology",
            "Reference realization",
            "COMPUTED",
            "Full-Cech transfer proves both determinant terms acyclic, while "
            "relative projection, duality contraction, and an elementary "
            "transformation derive the W1/W2 P1 pushdowns. Their tensor gives "
            "H*(wedge^2 V)= (0,4,4,0) for every extension parameter. The "
            "inverse-pullback action on four canonical P1 Cech representatives "
            "generates the published deck-character decomposition exactly.",
            (
                "data/generated/scientific_genesis/"
                "published_higgs_cohomology.json",
                "data/generated/scientific_genesis/"
                "relative_constituent_pushdowns.json",
                "data/generated/scientific_genesis/"
                "diagonal_higgs_actions.json",
                "research/experiments/scientific_genesis/"
                "published_higgs_cohomology.py",
                "research/experiments/scientific_genesis/"
                "relative_constituent_pushdowns.py",
                "research/experiments/scientific_genesis/"
                "diagonal_higgs_actions.py",
                "tests/integration/"
                "test_scientific_genesis_published_higgs_cohomology.py",
                "tests/integration/"
                "test_scientific_genesis_relative_constituent_pushdowns.py",
            ),
            (
                "published constituent linearisations",
                "relative duality for the locally free self-dual W1",
                "published Wilson-line embedding",
            ),
        ),
        _node(
            "published_chain_reconstruction",
            "published carrier chain reconstruction",
            "Reference realization",
            "BLOCKED",
            "The parameter-dependent rank-four cone is exact, locally free, "
            "determinant-trivial, and descended over the full nonzero forward "
            "family, with a certified generic stable genuine-SU(4) locus. An "
            "explicit local transition presentation remains absent.",
            (
                "data/generated/visible_carrier/visible_carrier_artifact.json",
                "data/generated/scientific_genesis/"
                "published_outer_cech_transfer.json",
                "data/generated/scientific_genesis/"
                "published_outer_cech_invariants.json",
                "data/generated/scientific_genesis/"
                "published_outer_universal_cone.json",
                "data/generated/scientific_genesis/"
                "published_outer_stability_locus.json",
            ),
            missing=(
                "local transition data",
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
            "Wilson-projected carrier spectrum",
            "Reference realization",
            "COMPUTED",
            "The stable published family has exact parameter-independent matter "
            "and Higgs dimensions. Inverse P1 Cech pullback generates the Higgs "
            "deck characters, so the Wilson projection gives three families, "
            "one Higgs pair, and no color triplets from selected published "
            "carrier inputs.",
            (
                "src/onetheory/physics/compactification.py",
                "research/experiments/computable_carrier/downstream.py",
                "data/generated/scientific_genesis/"
                "published_matter_cohomology.json",
                "data/generated/scientific_genesis/"
                "published_higgs_cohomology.json",
            ),
            assumptions=(
                "published W1/W2 equivariant pushdowns",
                "published Wilson-line embedding",
            ),
        ),
        _node(
            "computable_carrier_state",
            "first frozen computable carrier",
            "Computable carrier",
            "BLOCKED",
            "No candidate has passed every rank, determinant, topology, "
            "local-freeness, descent, stability, and spectrum gate.",
            ("data/generated/computable_carrier/computable_carrier_artifact.json",),
            missing=(
                "replacement algebraic lawful family",
                "nonempty stability chamber",
                "required structural spectrum",
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
            "BLOCKED",
            "Generic DGA, module, contraction, and HPL engines exist, but no "
            "synchronized carrier complex and physical representatives are available.",
            (
                "src/onetheory/math/homological.py",
                "research/experiments/visible_common_dga/audit.py",
            ),
            missing=(
                "synchronized V1/V2 Cech-Koszul complex",
                "matter and Higgs hypercocycles",
                "restricted actions and contraction",
                "cyclic pairing and trace conventions",
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
            "No complete matrix has been evaluated from generated carrier chain data.",
            ("research/experiments/visible_common_dga/audit.py",),
            missing=(
                "frozen computable carrier",
                "common DGA package",
                "matter and Higgs cocycles",
                "trace evaluation",
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
            "published_constituent_mapping_cones",
            "The chain-fixed invariant classes lift to explicit Cech overlap "
            "maps whose maximal-minor syzygies close the derived cones.",
            (
                "research/experiments/computable_carrier/"
                "dp9_serre_cech.py",
            ),
            ("published Cayley-Bacharach local-freeness theorem",),
            True,
            ("local transition matrices are not yet materialized",),
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
            "The four strict forward representatives provide the exact basis "
            "for the universal nonzero outer extension family.",
            (
                "data/generated/scientific_genesis/"
                "published_outer_cech_invariants.json",
            ),
            (),
            True,
            ("the universal cone does not by itself prove slope stability",),
        ),
        _edge(
            "published_outer_universal_cone",
            "published_outer_stability_locus",
            "The reconstructed P3 identifies the source's generic extension "
            "space, while exact slope inequalities and nonzero c3 certify a "
            "nonempty stable genuine-SU(4) sublocus without choosing a point.",
            (
                "data/generated/scientific_genesis/"
                "published_outer_stability_locus.json",
            ),
            (
                "published generic stability theorem",
                "Donaldson--Uhlenbeck--Yau correspondence",
                "rank-four connected subgroup classification",
            ),
            True,
            (
                "the proper exceptional parameter ideal is not computed",
                "no explicit HYM metric is constructed",
            ),
        ),
        _edge(
            "published_outer_stability_locus",
            "published_matter_cohomology",
            "The stable generic family makes the exact universal cone a lawful "
            "carrier; pure degree-one constituent cohomology collapses its long "
            "exact sequence independently of the extension parameters.",
            (
                "data/generated/scientific_genesis/"
                "published_matter_cohomology.json",
            ),
            (
                "published Wilson-line embedding",
                "Calabi--Yau Serre duality",
                "Maschke semisimplicity",
            ),
            True,
            ("Higgs cohomology is not determined by the matter sequence",),
        ),
        _edge(
            "published_matter_cohomology",
            "published_higgs_cohomology",
            "The lawful stable outer family supplies the same constituent and "
            "source gates used by the determinant filtration; acyclic outer "
            "terms remove all extension-parameter dependence.",
            (
                "data/generated/scientific_genesis/"
                "published_higgs_cohomology.json",
                "data/generated/scientific_genesis/"
                "relative_constituent_pushdowns.json",
            ),
            (
                "derived relative pushdowns over the common P1",
            ),
            True,
            (
                "the current tensor calculation does not generate full Cech "
                "representatives or their deck action",
            ),
        ),
        _edge(
            "published_matter_cohomology",
            "physical_spectrum",
            "Exact deck characters and the Wilson embedding determine the "
            "three-family and anti-family matter blocks.",
            (
                "data/generated/scientific_genesis/"
                "published_matter_cohomology.json",
            ),
            (),
            True,
            ("the matter edge alone does not determine the Higgs block",),
        ),
        _edge(
            "published_higgs_cohomology",
            "physical_spectrum",
            "Inverse pullback on four exact derived-P1 Cech representatives "
            "generates the deck characters, whose Wilson products select one "
            "doublet pair and no color triplets.",
            (
                "data/generated/scientific_genesis/"
                "published_higgs_cohomology.json",
            ),
            (
                "derived W1/W2 equivariant pushdowns",
                "published Wilson-line embedding",
            ),
            True,
            (
                "a changed pushdown linearization changes the generated "
                "character decomposition",
            ),
        ),
        _edge(
            "published_outer_stability_locus",
            "published_chain_reconstruction",
            "The generic stable locus supplies lawful physical parameters for "
            "the exact universal chain family.",
            (
                "data/generated/scientific_genesis/"
                "published_outer_stability_locus.json",
            ),
            (),
            True,
            ("local transition matrices remain absent",),
        ),
        _edge(
            "published_outer_universal_cone",
            "published_chain_reconstruction",
            "The universal block differential supplies the exact descended "
            "rank-four family on which stability and proper-reduction loci act.",
            (
                "data/generated/scientific_genesis/"
                "published_outer_universal_cone.json",
            ),
            (),
            True,
            ("genuine SU(4) requires a stable locus, not Chern data alone",),
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
            "Passing the declared three-family, one-Higgs, no-exotic "
            "constraints freezes a carrier.",
            ("research/experiments/computable_carrier/downstream.py",),
            ("selection constraints are not predictions",),
            True,
            ("no lawful parameter locus may satisfy all constraints",),
        ),
        _edge(
            "computable_carrier_state",
            "common_dga_package",
            "A fixed carrier determines the synchronized complexes and products.",
            ("src/onetheory/math/homological.py",),
            (),
            True,
            ("required contractions or pairings may be unavailable",),
        ),
        _edge(
            "common_dga_package",
            "first_exact_yukawa",
            "Matter/Higgs cocycle products and trace yield a holomorphic matrix.",
            ("src/onetheory/models/heterotic_schoen/flavor.py",),
            (),
            True,
            ("matrix may vanish or have rank below three",),
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
            "universal_pair_73_mapping_cone",
            5,
            4,
            5,
            5,
            3,
            2,
            "Closes the first carrier-construction edge using existing exact cocycles.",
        ),
        (
            "pair_73_algebraic_locus",
            5,
            3,
            5,
            5,
            4,
            2,
            "Can validate or eliminate the entire simplest family symbolically.",
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
            "computable_family_stability_chamber",
            4,
            3,
            5,
            4,
            4,
            3,
            "Decides whether an algebraically lawful family can become physical.",
        ),
        (
            "computable_family_spectrum_loci",
            5,
            3,
            5,
            5,
            5,
            3,
            "Directly tests three-family and one-Higgs selection constraints.",
        ),
        (
            "minimal_common_dga_yukawa_slice",
            5,
            4,
            5,
            5,
            5,
            3,
            "Produces the first matrix once a carrier survives.",
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

    action_path = (
        ROOT / "data/generated/computable_carrier/tier_b_schoen_outer_automorphisms.partial.json"
    )
    action = json.loads(action_path.read_text(encoding="utf-8"))
    pair_73 = action["completed_pairs"]["73"]
    if pair_73["invariant_ext_one_dimension"] != 4 or pair_73["exact"] is not True:
        raise ValueError("pair 73 is no longer the exact four-dimensional family")
    if pair_73["automorphism_action"]["nonzero_orbit_space"] != "P^3(Q(omega))":
        raise ValueError("pair 73 no longer has the certified projective quotient")

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
        "data/generated/scientific_genesis/published_constituent_mapping_cones.json",
        "data/generated/scientific_genesis/published_outer_reduced_mismatch.json",
        "data/generated/scientific_genesis/published_outer_cech_transfer.json",
        "data/generated/scientific_genesis/published_outer_cech_invariants.json",
        "data/generated/scientific_genesis/published_outer_universal_cone.json",
        "data/generated/scientific_genesis/published_outer_stability_locus.json",
        "data/generated/scientific_genesis/published_matter_cohomology.json",
        "data/generated/scientific_genesis/published_higgs_cohomology.json",
        "data/generated/scientific_genesis/relative_constituent_pushdowns.json",
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
            "collected_tests_at_audit": 498,
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
                "published spectrum closed; full Higgs Cech lift"
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
            },
            "invariant_certificate_digest": pair_73["invariant_certificate_digest"],
            "automorphism_certificate_digest": pair_73["certificate_digest"],
            "next_required_object": (
                "exact overlap transitions gluing the six local Serre frames, "
                "followed by a synchronized lift of the four derived-P1 "
                "representatives into the full Schoen Cech complex"
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
            "exact natural dP9 deck chain actions plus source-aligned invariant "
            "constituent Ext representatives",
            "exact invariant Cech maximal-minor cocycles and square-zero derived "
            "mapping-cone certificates for W1 and W2",
            "exact free rank-two local Serre frames at all six I3/I6 support "
            "points with localized Hilbert--Burch-to-Koszul factorization",
            "exact cohomology-reduced outer model preserving the source Euler "
            "characteristic and isolating a common 90-dimensional excess",
            "exact standard-cover Cech contraction and finite transfer deriving "
            "the published forward 36/72 and reverse 72/36 cover outer dimensions",
            "exact transferred deck actions deriving invariant dimensions four "
            "and eight plus strict full-Cech representatives",
            "exact universal rank-four outer cone over P^3(Q(omega)) with "
            "non-split, local-freeness, Chern, and descent gates",
            "nonempty generic stable descended genuine-SU(4) locus U_pub x K^s "
            "with nine exact slope inequalities and a rational open witness",
            "exact all-parameter matter cohomology H1(V)=3 Reg(Z3 x Z3), "
            "H1(V dual)=0, and a three-family Wilson projection",
            "exact all-parameter Higgs cohomology H*(wedge^2 V)=(0,4,4,0) "
            "from derived W1/W2 relative quasi-isomorphisms, with an empty "
            "jumping locus and a generated derived-P1 deck action giving one "
            "Higgs pair with no color triplets",
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
        ],
        "scoped_no_go_results": [
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
            "the current 14-dimensional diagonal Higgs cone has exact character "
            "multiplicities 3,2,3,2,2,2; missing and repeated lawful sectors "
            "rule out character projection as a four-class selector",
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
            "full common-Cech matter and Higgs representatives for Yukawa products",
            "carrier-derived complete holomorphic Yukawa matrix",
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
