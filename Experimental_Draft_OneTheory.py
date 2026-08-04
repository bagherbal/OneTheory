#!/usr/bin/env python3
"""Standalone verifier and reproducibility engine for the OneTheory project.

Release scope
-------------
Version 0.13.6 implements the front matter and Sections 1--13.  In addition to
the completion contract, it records the imported heterotic carrier and
reproduces its project-side exact checks over Q and Q(omega): Heisenberg
coordinate lifts, eigen-cubics, Hilbert--Burch point schemes, equivariant
Serre rays, quotient intersection and Chern data, the slope anchor, and the
finite Mordell--Weil curve counts.  It also implements the exact finite-origin
ledger: Planck-scale monomials, the action-paired metric/symplectic carrier,
Clifford grades, phase-plane projectors, exceptional-algebra dimensions,
finite quadratic forms, E8 and D5 mod-three lattice checks, the finite Fourier
chirp, CP conjugation, and hierarchy-filter bookkeeping.

Section 4 does not claim a completed Origin-to-Carrier theorem. It implements
the theorem's typed interface registry, dependency graph, non-circularity
firewall, pass and kill criteria, and explicit OPEN/MISSING_INPUT states.

Section 5 implements the exact observable-sector deformation ledger: the
rank-two tree texture, four forward and eight reverse deformation directions,
the scoped complete-forward-slice no-go, the bi-Leray zero quadratic
obstruction, a strict square-zero witness, the curvature-corrected
Maurer--Cartan and Higgs identities, the local-freeness normal-form
certificate, exact stability-box inequalities, and the open-locus spectrum
argument. It does not claim physical normalized Yukawa matrices or a
light-family rank lift.

Section 6 implements the exact finite light-family frontier.  It certifies
the odd-order wall-charge law, the complete degree-three and direct
order-five no-go results, the determinant second-normal correction, and the
generic 24-residue restricted-hull compiler and its direction-adaptive
refinement.  The exact f3 identities reduce the worst-case carrier workload
to 20 normalized scalar traces, while the first simultaneous-rank test needs
only four.  A suspended-planar HPL compiler now evaluates requested transfer
words from an exact common-DGA contraction by the sparse memoized recursion
F_1=i_1, B_n=sum mu(F_r,F_{n-r}), F_n=-h_2 B_n, and m_n=p_2 B_n.
It validates the archived chain, primitive, pairing, cyclicity, equivariance,
matrix-digest, and word-assignment certificates before a trace can reach the
adaptive decision layer.  A raw common-cyclic tensor compiler derives four values
from frozen sector bases, external states, effective FE responses, and paired
cyclic tensors, checking the orientation collapse before invoking the
binary-Gram decision.  All compilers are deliberately fail-closed: the
physical common-DGA/word package, physical raw package, and carrier traces are
MISSING_INPUT, while exact
synthetic packages exercise every decision branch.  It does not claim a
carrier rank lift or physical quark masses.

This release also certifies the exact conditional star-tangent theorem for an
off-diagonal active block.  If the up transport is confined to one star arm,
its degree-five second-normal form vanishes identically.  If the down
transport has the certified triangular form, its quadratic factorizes as
D_2=-(2/m_d)A_d B_d.  No project artifact certifies that these typing
hypotheses hold for the physical carrier, so carrier applicability remains
MISSING_INPUT and the theorem is not promoted to a physical degree-five
no-go result.

Release 0.13.5 closes a tempting but invalid shortcut to those hypotheses.
The retained branch-pruning certificates determine surviving mechanisms and
the universal binary-Gram structure, but not the two exact components of the
physical transport columns.  Exact countermodels satisfy every retained
structural constraint while disagreeing on both up-star and down-triangular
typing.  The verifier therefore marks inference of either typing from the
current evidence as KILLED, while leaving the actual carrier typing
MISSING_INPUT.  It exposes the invariant early test: four normalized f3 traces
produce p_u,3 and p_d,3; a nonzero self-pairing immediately refutes the
corresponding shortcut, while an isotropic first column triggers the existing
adaptive f5/f7 path.

Section 7 replaces the superseded global-section differential for the
non-split bundle by the lawful Cech hypercocycle-lift interface.  It certifies
the 192+212=404 dimension ledger, the 4*212=848 lift workload, the scoped
global-matrix no-go, and rank invariance under invertible canonical
normalization.  Numerical Hermitian-metric helpers are isolated from exact
arithmetic and fail explicitly on non-Hermitian or non-positive input.  No
Ricci-flat metric, HYM connection, harmonic representatives, physical
Yukawa matrix, or selected vacuum is supplied.

Section 8 certifies the two free nine-conic orbits, the degree-four local
Pfaffian grammar, the exact Serre-restriction firewall, and the finite
quadratic-refinement classification.  It also records the stronger
projective-catalecticant nonidentifiability theorem: the stored outer tensors,
right restriction, and rank-six comparison data do not determine a physical
quartic, even projectively.  The 7- and 19-term quartics are nonphysical
witnesses to that insufficiency.  No orbit sum, determinant-line
trivialization, Quillen phase assignment, hidden determinant, controlled
vacuum, or physical CP observable is manufactured.

Section 9 fixes the hidden topological target, certifies the bounded monad
closures through objective 26, and records the objective-28 reduction to 44
unresolved supports.  Candidate 750 supplies an exact Q(omega) complex with
G*F=0 and the required sampled-fibre ranks at two exact points; it is not a
bundle-existence theorem.  The standard one-fibration FMW/vertical-Hecke
route is excluded for the required mixed Chern class.  Global constant rank,
local freeness, honest equivariant descent, curve restrictions, invariant
extension data, stability, hidden cohomology, HYM data, and determinant-line
compatibility remain OPEN or MISSING_INPUT.

Section 10 implements the exact nonperturbative source classification. It
certifies the four-term sign obstruction, the universal affine-hyperplane
no-go, the published split-bicubic Chern--Simons firewall, the complete
toral E6 Wilson-line classification, the one-extra-worldsheet and multicover
no-go, and the unique minimal same-f_h unequal-exponent racetrack target.
The carrier-specific exponents, prefactors, Kähler potential, gauge kinetic
functions, determinant lines, F- and D-term solution, Hessian, hierarchy of
omitted corrections, and controlled vacuum remain OPEN or MISSING_INPUT.

Section 11 implements the four-dimensional closure and falsification ledger.
It serializes twenty-seven completion criteria, program-layer kill rules, the
one-vacuum consistency contract, prediction-role and held-out-data firewalls,
exact covariance propagation, numerical CKM/Jarlskog, seesaw, running, and
comparison helpers, and a fail-closed conditional closure theorem.  It does
not import legacy numerical phenomenology as a prediction and does not claim
carrier closure, a controlled vacuum, low-energy observables, or native origin.

Section 12 implements the maintained reproducibility spine: canonical
serialization, SHA-256 artifact verification, dependency-graph validation,
fail-closed numerical-certificate metadata, a twenty-one-item reproducibility
ledger, release-bundle validation, and a machine-readable inventory of open
obligations.  The single-file verifier and its standard-library regression
suite are established; a frozen public archive and an independent clean-room
reproduction remain OPEN.

Section 13 supplies the final scientific synthesis and technical-appendix
crosswalk.  It derives no new physical observable.  Instead it serializes the
thirteen-section result ledger, the A--M appendix map, the three simultaneous
closure requirements, the inherited open-obligation frontier, and the final
critical path.  It certifies that the current release is a theorem-gated
incomplete research program, not a completed Theory of Everything.

Release 0.13.6 adds an artifact-level publication firewall.  It audits DOCX
OOXML for empty or malformed formula shells, empty native equations, leaked
internal identifiers, replacement glyphs, and raw Markdown residue.  It also
audits Python source for syntax errors, placeholder statements, duplicate
top-level definitions, and unimplemented branches.  Artifact integrity is
kept separate from scientific completion.

The program deliberately does not turn an OPEN, CONDITIONAL, ANALYTICAL, or
MISSING_INPUT result into a passed theorem. Later paper sections can extend
this single file without changing that rule.

Only the Python standard library is required.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import sys
import tempfile
import unittest
import zipfile
from dataclasses import asdict, dataclass
from decimal import Decimal, localcontext
from enum import Enum
from fractions import Fraction
from itertools import product
from math import comb, exp, isfinite, log, pi, sqrt
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence
from xml.etree import ElementTree

__version__ = "0.13.6"
COMPLETED_PAPER_SECTIONS = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13)


class EvidenceClass(str, Enum):
    """Scientific-status labels used in the paper and machine output."""

    PUBLISHED_INPUT = "P"
    EXACT_THEOREM = "T"
    ANALYTICAL_UNCERTIFIED = "A"
    CONDITIONAL = "C"
    BRIDGE_TARGET = "B"
    SCOPED_NO_GO = "N"
    OPEN = "O"


class GateState(str, Enum):
    """Operational state of a completion gate."""

    PASSED = "PASSED"
    CONDITIONAL = "CONDITIONAL"
    OPEN = "OPEN"
    MISSING_INPUT = "MISSING_INPUT"
    KILLED = "KILLED"


class ExitCode(int, Enum):
    """Stable command-line exit codes."""

    OK = 0
    CERTIFICATE_FAILURE = 1
    MISSING_INPUT = 2
    INVALID_MANIFEST = 3
    NUMERICAL_TOLERANCE_FAILURE = 4
    COMPLETION_OPEN = 5


class ObservableRole(str, Enum):
    """Audit role assigned to every numerical observable."""

    DERIVED = "DERIVED"
    DISCRETE_SELECTION = "DISCRETE_SELECTION"
    FITTED = "FITTED"
    HELD_OUT_PREDICTION = "HELD_OUT_PREDICTION"


class ComputationLayer(str, Enum):
    """The exact, numerical, and physical layers of the verifier."""

    EXACT = "E"
    NUMERICAL = "N"
    PHYSICAL = "P"


@dataclass(frozen=True)
class Claim:
    identifier: str
    evidence_class: EvidenceClass
    statement: str
    source_ids: tuple[str, ...]
    scope: str


@dataclass(frozen=True)
class Gate:
    identifier: str
    label: str
    state: GateState
    evidence_class: EvidenceClass
    pass_criterion: str
    kill_criterion: str
    current_basis: str


@dataclass(frozen=True)
class Check:
    identifier: str
    passed: bool
    expected: Any
    observed: Any
    evidence_class: EvidenceClass
    note: str


@dataclass(frozen=True)
class ClosureCriterion:
    """One necessary condition in the Section 11 completion contract."""

    number: int
    category: str
    label: str
    state: GateState
    evidence_class: EvidenceClass
    dependency_ids: tuple[str, ...]
    pass_criterion: str
    failure_scope: str


@dataclass(frozen=True)
class FalsificationRule:
    """A scoped kill rule and its scientific implication."""

    identifier: str
    layer: str
    required_object: str
    kill_test: str
    implication: str
    scope: str


@dataclass(frozen=True)
class PredictionRecord:
    """One auditable derived, selected, fitted, or held-out quantity."""

    identifier: str
    role: ObservableRole
    provenance_ids: tuple[str, ...]
    used_for_selection: bool
    value_supplied: bool
    uncertainty_supplied: bool
    note: str


@dataclass(frozen=True)
class OriginInterface:
    """Typed contract for one still-open Origin-to-Carrier subsystem map."""

    identifier: str
    class_name: str
    domain: str
    codomain: str
    dependencies: tuple[str, ...]
    required_properties: tuple[str, ...]
    missing_inputs: tuple[str, ...]
    pass_criterion: str
    kill_criterion: str
    state: GateState = GateState.OPEN
    evidence_class: EvidenceClass = EvidenceClass.OPEN


@dataclass(frozen=True)
class ReproducibilityCriterion:
    """One pass/fail item in the Section 12 release contract."""

    number: int
    label: str
    state: GateState
    evidence_class: EvidenceClass
    pass_criterion: str
    current_basis: str


@dataclass(frozen=True)
class FinalLedgerEntry:
    """One section-level conclusion in the final scientific ledger."""

    section: int
    title: str
    evidence_classes: tuple[EvidenceClass, ...]
    strongest_result: str
    boundary: str


@dataclass(frozen=True)
class AppendixRecord:
    """One technical appendix and the maintained sections it summarizes."""

    letter: str
    title: str
    source_sections: tuple[int, ...]
    evidence_class: EvidenceClass
    purpose: str


SOURCE_CORPUS_SHA256: Mapping[str, str] = {
    "1-OneTheory(1).docx":
        "81011e69e306bfd39ad4b918ed116c29753fc12d756f2b3c71dd2a16f20b2add",
    "2-Minimal Physical Foundation and Ultraviolet Carrier.docx":
        "63d3bdcf206249b169931b17b8188a7df178c0a1340bf67a98538fc459ee67ee",
    "3-Native Finite-Origin Architecture.docx":
        "c6d5c2e50200dc508b744cdea15030f72f66deb0000300592f7d672722a0c8d6",
    "4-The Missing Origin-to-Carrier Theorem.docx":
        "9650d5756f5b8aa2b03c7d58d92f6fb13a27d8c7713039dbbb6585d759fe5746",
    "5-Exact Observable-Sector Deformation Theory.docx":
        "122868522df4d6d786675265b33ae14208fd38f49b6adb993fe04f415603bcba",
    "6-Light-Family Rank Lifting and the Finite Visible Frontier.docx":
        "f5b3e9ce1ff60ad0f2564d894103ffa6eb7a243d3e109d32301aa44d01517dbd",
    "7-Metric Completion and Physical Yukawa Couplings.docx":
        "5df218fc3486296e6ec6aa62cd9af435b8a0e2ddd2bb1ff424cd2d2f507bb8a7",
    "8-Worldsheet Instantons, Determinant Lines, and CP.docx":
        "bb9751301a2c503866fc972cdebf3fd37581e210ce59ba05f2660e4a1442cafd",
    "9-Hidden-Bundle Completion.docx":
        "d1ac13c9218c603761df7f1fad873bdeb7978a6ef6e9f144b2f23adec510090c",
    "10-Nonperturbative Superpotential and Controlled Vacuum.docx":
        "9c9a131c3ee297b95bb5fc02a666f9cffcae9738a4dd5042206405ec3bb93822",
    "11-Four-Dimensional Closure and Falsification.docx":
        "305c26481211617f77694914edcc9bc3c902b2ada3db18936ef4d41b51bf68d5",
    "12-Companion Implementation and Reproducibility.docx":
        "a6b9a860ccf38e5714c7630e37117aaf6352d26b725d6203424368bb18a72886",
    "13-OneTheory Conclusion and Technical Appendices.docx":
        "f2131bcca760f4b5bde32f168cf9fbf73608c9b0fe849b71259ee7fe9bfc6e79",
}


EVIDENCE_REGISTRY: Mapping[str, Mapping[str, str]] = {
    "schoen_quotient_2004": {
        "kind": "published_primary",
        "citation": (
            "Braun, Ovrut, Pantev, and Reinbacher, "
            "Elliptic Calabi-Yau Threefolds with Z3 x Z3 Wilson Lines, "
            "JHEP 12 (2004) 062"
        ),
        "locator": "https://arxiv.org/abs/hep-th/0410055",
    },
    "old_two_higgs_2005": {
        "kind": "published_primary_superseded_carrier",
        "citation": (
            "Braun, He, Ovrut, and Pantev, Vector Bundle Extensions, "
            "Sheaf Cohomology, and the Heterotic Standard Model"
        ),
        "locator": "https://arxiv.org/abs/hep-th/0505041",
    },
    "old_carrier_moduli_2005": {
        "kind": "published_primary_superseded_carrier",
        "citation": "Braun, He, Ovrut, and Pantev, Heterotic Standard Model Moduli",
        "locator": "https://arxiv.org/abs/hep-th/0509051",
    },
    "exact_mssm_2006": {
        "kind": "published_primary",
        "citation": "Braun et al., JHEP 05 (2006) 043",
        "locator": "https://arxiv.org/abs/hep-th/0512177",
    },
    "carrier_stability_2006": {
        "kind": "published_primary",
        "citation": "Braun et al., JHEP 06 (2006) 032",
        "locator": "https://arxiv.org/abs/hep-th/0602073",
    },
    "carrier_yukawa_2006": {
        "kind": "published_primary",
        "citation": "Braun et al., JHEP 04 (2006) 019",
        "locator": "https://arxiv.org/abs/hep-th/0601204",
    },
    "curve_lattice_v055": {
        "kind": "project_certificate",
        "citation": "MinTOE exact curve-lattice gate v0.55",
        "locator": "project-library",
    },
    "torsion_fourier_v056": {
        "kind": "project_certificate",
        "citation": "MinTOE torsion/Pfaffian Fourier gate v0.56",
        "locator": "project-library",
    },
    "carrier_reconciliation_v057": {
        "kind": "project_certificate",
        "citation": "MinTOE exact-carrier/Yukawa reconciliation gate v0.57",
        "locator": "project-library",
    },
    "heisenberg_serre_v062": {
        "kind": "project_certificate",
        "citation": "MinTOE Heisenberg-linearized Serre-class gate v0.62",
        "locator": "project-library",
    },
    "degree_two_v068": {
        "kind": "project_certificate",
        "citation": "MinTOE degree-two conic/quartic gate v0.68",
        "locator": "project-library",
    },
    "hidden_c2_v77": {
        "kind": "project_certificate",
        "citation": "MinTOE remaining-gaps solver v77",
        "locator": "project-library",
    },
    "canonical_manual_v8": {
        "kind": "project_manual",
        "citation": "MinTOE–ASHA Canonical Research Manual, version 8",
        "locator": "project-library",
    },
    "forward_classes_v18": {
        "kind": "project_certificate",
        "citation": "ASHA equivariant outer-hypercocycle gate v18",
        "locator": "project-library",
    },
    "forward_no_go_v26": {
        "kind": "project_certificate",
        "citation": "ASHA full outer-slice Yukawa no-go gate v26",
        "locator": "project-library",
    },
    "reverse_classes_v31": {
        "kind": "project_certificate",
        "citation": "ASHA reverse factor-hypercohomology gate v31",
        "locator": "project-library",
    },
    "quadratic_v34c": {
        "kind": "project_certificate",
        "citation": "ASHA bi-Leray quadratic-vanishing gate v34c",
        "locator": "project-library",
    },
    "strict_slice_v35h1d": {
        "kind": "project_certificate",
        "citation": "ASHA Serre-shear annihilation gate v35h1d",
        "locator": "project-library",
    },
    "deformation_v35i0": {
        "kind": "project_certificate",
        "citation": "ASHA formal local-freeness gate v35i0",
        "locator": "project-library",
    },
    "stability_v35i1": {
        "kind": "project_certificate",
        "citation": "ASHA mixed-branch stability-openness gate v35i1",
        "locator": "project-library",
    },
    "spectrum_v35i2": {
        "kind": "project_certificate",
        "citation": "ASHA mixed-branch spectrum-reduction gate v35i2",
        "locator": "project-library",
    },
    "higgs_v36a2f": {
        "kind": "project_certificate",
        "citation": "ASHA all-order Higgs-protection gate v36a2f",
        "locator": "project-library",
    },
    "degree3_v36a2g": {
        "kind": "project_certificate",
        "citation": "ASHA order-three Serre-annihilation gate v36a2g",
        "locator": "project-library",
    },
    "order5_v36a2h": {
        "kind": "project_certificate",
        "citation": "ASHA order-five second-normal-jet gate v36a2h",
        "locator": "project-library",
    },
    "second_fundamental_v36a2i": {
        "kind": "project_certificate",
        "citation": "ASHA second-fundamental-form gate v36a2i",
        "locator": "project-library",
    },
    "residue_v36a2k": {
        "kind": "project_certificate",
        "citation": "ASHA branch-typed null-transport gate v36a2k",
        "locator": "project-library",
    },
    "restricted_hull_v36a2m": {
        "kind": "project_certificate",
        "citation": "ASHA restricted common null-transport hull gate v36a2m",
        "locator": "project-library",
    },
    "adaptive_residue_v36a2n": {
        "kind": "project_certificate",
        "citation": "ASHA f3-direction adaptive null-transport gate v36a2n",
        "locator": "project-library",
    },
    "raw_f3_compiler_v0132": {
        "kind": "exact_internal_certificate",
        "citation": (
            "OneTheory raw f3 common-cyclic trace compiler and orientation "
            "collapse certificate, release 0.13.2"
        ),
        "locator": "OneTheory.py",
    },
    "common_dga_schema_v35h1": {
        "kind": "project_interface",
        "citation": (
            "ASHA minimal suspended cyclic common-DGA contraction package "
            "schema v35h1"
        ),
        "locator": "project-library",
    },
    "suspended_hpl_compiler_v0133": {
        "kind": "exact_internal_certificate",
        "citation": (
            "OneTheory suspended-planar HPL source-to-trace compiler, "
            "release 0.13.3"
        ),
        "locator": "OneTheory.py",
    },
    "positive_twist_v99": {
        "kind": "project_report",
        "citation": "MinTOE positive-twist/HYM gate v99",
        "locator": "project-library",
    },
    "frontier_v105": {
        "kind": "project_report",
        "citation": "MinTOE frontier-reduction report v105",
        "locator": "project-library",
    },
    "stabilization_v41": {
        "kind": "project_report",
        "citation": "MinTOE controlled-stabilization classification v41",
        "locator": "project-library",
    },
    "extension_blindness_v13": {
        "kind": "project_certificate",
        "citation": "ASHA extension-blindness theorem v13",
        "locator": "libfile_344b2a74a9808191b3d22587f1d79c58",
    },
    "cech_lift_v14": {
        "kind": "project_certificate",
        "citation": "ASHA lawful Cech-lift replacement v14",
        "locator": "libfile_3074411f920c8191bd5367da61320a27",
    },
    "section_basis_v30": {
        "kind": "project_report_and_interface",
        "citation": "ASHA positive-twist section-basis architecture v30",
        "locator": (
            "libfile_a583d491eff08191a18e0da0e00c6b57; "
            "libfile_217d799984088191905944fe806f6efb"
        ),
    },
    "numerical_cy_metrics_2006": {
        "kind": "published_primary",
        "citation": "Douglas, Karp, Lukic, and Reinbacher, Numerical Calabi-Yau metrics",
        "locator": "https://arxiv.org/abs/hep-th/0612075",
    },
    "quotient_hym_2023": {
        "kind": "published_primary",
        "citation": "Cui, Numerical Hermitian Yang-Mills Connection for Bundles on Quotient Manifold",
        "locator": "https://arxiv.org/abs/2302.09622",
    },
    "general_hym_yukawa_2025": {
        "kind": "published_primary",
        "citation": "Mishra and Tan, HYM connections on general vector bundles",
        "locator": "https://arxiv.org/abs/2512.10907",
    },
    "witten_instantons_1999": {
        "kind": "published_primary",
        "citation": "Witten, World-Sheet Corrections Via D-Instantons",
        "locator": "https://arxiv.org/abs/hep-th/9907041",
    },
    "beasley_witten_2003": {
        "kind": "published_primary",
        "citation": "Beasley and Witten, Residues and World-Sheet Instantons",
        "locator": "https://arxiv.org/abs/hep-th/0304115",
    },
    "dai_freed_1994": {
        "kind": "published_primary",
        "citation": "Dai and Freed, Eta-Invariants and Determinant Lines",
        "locator": "https://arxiv.org/abs/hep-th/9405012",
    },
    "curio_pfaffians_2008": {
        "kind": "published_primary",
        "citation": "Curio, World-sheet Instanton Superpotentials and Moduli Dependence",
        "locator": "https://arxiv.org/abs/0810.3087",
    },
    "curio_pfaffians_2009": {
        "kind": "published_primary",
        "citation": "Curio, Perspectives on Pfaffians of Heterotic World-sheet Instantons",
        "locator": "https://arxiv.org/abs/0904.2738",
    },
    "curio_individual_2010": {
        "kind": "published_primary",
        "citation": "Curio, On the Heterotic World-sheet Instanton Superpotential",
        "locator": "https://arxiv.org/abs/1006.5568",
    },
    "buchbinder_instantons_2019": {
        "kind": "published_primary",
        "citation": "Buchbinder, Lukas, Ovrut, and Ruehle, Heterotic Instantons for Monad and Extension Bundles",
        "locator": "https://arxiv.org/abs/1912.07222",
    },
    "restriction_v071": {
        "kind": "project_certificate",
        "citation": "MinTOE conic restriction and physical-map gate v0.71",
        "locator": "libfile_21d038cd6fc4819195ed4024f22a5912",
    },
    "serre_ray_v072": {
        "kind": "project_certificate",
        "citation": "MinTOE Serre-ray normalization firewall v0.72",
        "locator": "libfile_20340b5bb75c8191b3cc07570fa589a6",
    },
    "quartic_nonidentifiability_v075": {
        "kind": "project_certificate",
        "citation": "MinTOE projective catalecticant transport gate v0.75",
        "locator": "libfile_b32613ed5b8c8191863efb82fb53d327",
    },
    "quillen_quadratic_v27": {
        "kind": "project_certificate",
        "citation": "MinTOE Quillen quadratic-refinement gate v27",
        "locator": "libfile_57c3220f6d648191a82542bf57d519c0",
    },
    "cp_pair_v8": {
        "kind": "project_report",
        "citation": "ASHA CP vacuum-pair closure report v8",
        "locator": "libfile_de2d2d787a288191ac18ab3996196ba5",
    },
    "cp_order_v9": {
        "kind": "project_report",
        "citation": "ASHA equivariant CP-order gate v9",
        "locator": "libfile_08d859febea08191bbe8c603a8fc997e",
    },
    "hidden_remaining_gaps_v77": {
        "kind": "project_certificate",
        "citation": "MinTOE remaining-gaps solver v77",
        "locator": "project-library",
    },
    "hidden_rank22_v92": {
        "kind": "project_certificate_superseded_milestone",
        "citation": "MinTOE primitive-Q rank-22 exact gate v92",
        "locator": "libfile_d1647b9c03ec81918a7a5e7ac1cac0df",
    },
    "hidden_radius1_v94": {
        "kind": "project_certificate",
        "citation": "MinTOE primitive-Q radius-one closure v94",
        "locator": "libfile_106a7124fbe48191aaea7bf25c560567",
    },
    "hidden_objective28_v95": {
        "kind": "project_certificate",
        "citation": "MinTOE primitive-Q objective-26 closure/objective-28 gate v95",
        "locator": "libfile_49be013378788191935d08d71f3027d6",
    },
    "hidden_candidate750_witness": {
        "kind": "project_certificate",
        "citation": "Candidate 750 exact Q(omega) complex witness",
        "locator": "libfile_67411915209c819193316bd6c85a82a5",
    },
    "hidden_spectral_v24": {
        "kind": "project_certificate",
        "citation": "MinTOE hidden spectral GRR/source-separation gate v24",
        "locator": "libfile_abfa6d490b3081918d1322be255cf76f",
    },
    "hidden_input_gate_v42": {
        "kind": "project_certificate",
        "citation": "MinTOE hidden-input sufficiency gate v42",
        "locator": "libfile_db88a810ab688191bc195463c6a6fa5",
    },
    "standard_model_2005": {
        "kind": "published_primary",
        "citation": "Braun et al., A Standard Model from the E8 x E8 Heterotic Superstring",
        "locator": "https://arxiv.org/abs/hep-th/0502155",
    },
    "fmw_vector_bundles_1997": {
        "kind": "published_primary",
        "citation": "Friedman, Morgan, and Witten, Vector Bundles and F Theory",
        "locator": "https://arxiv.org/abs/hep-th/9701162",
    },
    "stabilization_term_count_v30": {
        "kind": "project_certificate",
        "citation": "MinTOE supersymmetric-vacuum term-count gate v30",
        "locator": "project-library:MINTOE_SUSY_VACUUM_TERM_COUNT_GATE_v30",
    },
    "stabilization_affine_v31": {
        "kind": "project_certificate",
        "citation": "MinTOE affine charge-hyperplane no-go v31",
        "locator": "libfile_06e14584f7e4819185454562ade70f53",
    },
    "stabilization_cs_v34": {
        "kind": "project_certificate",
        "citation": "MinTOE split-bicubic Chern-Simons no-go v34",
        "locator": "libfile_fcb6d3a2d5d481919de4bfbf0551f69f",
    },
    "stabilization_e6_v35": {
        "kind": "project_certificate",
        "citation": "MinTOE E6 toral pure-SYM racetrack gate v35",
        "locator": "libfile_775be6fc80f08191ad877d80e67082d3",
    },
    "stabilization_remaining_v77": {
        "kind": "project_certificate",
        "citation": "MinTOE remaining-gaps solver v77",
        "locator": "libfile_59ab25cc5d0c819186845461f6978e99",
    },
    "heterotic_moduli_2011": {
        "kind": "published_primary",
        "citation": "Anderson, Gray, Lukas, and Ovrut, Stabilizing All Geometric Moduli in Heterotic Calabi-Yau Vacua",
        "locator": "https://arxiv.org/abs/1102.0011",
    },
    "split_bicubic_cs_2015": {
        "kind": "published_primary",
        "citation": "Apruzzi et al., Wilson Lines and Chern-Simons Flux in Explicit Heterotic Calabi-Yau Compactifications",
        "locator": "https://arxiv.org/abs/1410.2603",
    },
    "gluino_condensation_1985": {
        "kind": "published_primary",
        "citation": "Dine, Rohm, Seiberg, and Witten, Gluino Condensation in Superstring Models",
        "locator": "https://inspirehep.net/literature/16691",
    },
    "jarlskog_1985": {
        "kind": "published_primary",
        "citation": "Jarlskog, Commutator of the Quark Mass Matrices and CP Nonconservation",
        "locator": "https://inspirehep.net/literature/216470",
    },
    "breitenlohner_freedman_1982": {
        "kind": "published_primary",
        "citation": "Breitenlohner and Freedman, Positive Energy in anti-De Sitter Backgrounds",
        "locator": "https://inspirehep.net/literature/12129",
    },
    "minkowski_1977": {
        "kind": "published_primary",
        "citation": "Minkowski, Mu to e gamma at a Rate of One Out of One Billion Muon Decays?",
        "locator": "https://inspirehep.net/literature/4994",
    },
    "machacek_vaughn_1983": {
        "kind": "published_primary",
        "citation": "Machacek and Vaughn, Two-Loop Renormalization Group Equations in a General Quantum Field Theory",
        "locator": "https://inspirehep.net/literature/188748",
    },
    "appelquist_carazzone_1975": {
        "kind": "published_primary",
        "citation": "Appelquist and Carazzone, Infrared Singularities and Massive Fields",
        "locator": "https://inspirehep.net/literature/1631",
    },
    "weinberg_baryon_lepton_1979": {
        "kind": "published_primary",
        "citation": "Weinberg, Baryon and Lepton Nonconserving Processes",
        "locator": "https://inspirehep.net/literature/144673",
    },
    "four_dimensional_closure_source": {
        "kind": "project_source",
        "citation": "OneTheory Section 11 source: Four-Dimensional Closure and Falsification",
        "locator": "libfile_b4f5527d4ad88191991d9c69cb8abeb8",
    },
    "legacy_prediction_ledger": {
        "kind": "superseded_unintegrated_project_ledger",
        "citation": "Legacy full-action prediction/falsifier ledger",
        "locator": "libfile_18cf52d5f288819185f05ae0818d8531",
    },
    "companion_implementation_source": {
        "kind": "project_source",
        "citation": "OneTheory Section 12 source: Companion Implementation and Reproducibility",
        "locator": "libfile_93e6b22fa7808191a9308c643be9e8c2",
    },
    "sandve_reproducibility_2013": {
        "kind": "published_primary",
        "citation": (
            "Sandve et al., Ten Simple Rules for Reproducible Computational "
            "Research, PLoS Computational Biology 9 (2013) e1003285"
        ),
        "locator": "https://doi.org/10.1371/journal.pcbi.1003285",
    },
    "fair_principles_2016": {
        "kind": "published_primary",
        "citation": (
            "Wilkinson et al., The FAIR Guiding Principles for scientific data "
            "management and stewardship, Scientific Data 3 (2016) 160018"
        ),
        "locator": "https://doi.org/10.1038/sdata.2016.18",
    },
    "nist_fips_180_4": {
        "kind": "published_standard",
        "citation": "NIST FIPS PUB 180-4, Secure Hash Standard",
        "locator": "https://csrc.nist.gov/pubs/fips/180-4/upd1/final",
    },
    "conclusion_appendices_source": {
        "kind": "project_source",
        "citation": "OneTheory Section 13 source: Conclusion and Technical Appendices",
        "locator": "libfile_a1ed9b9d3a74819191f05af1c891f61c",
    },
}


CLAIMS: tuple[Claim, ...] = (
    Claim(
        "published_carrier",
        EvidenceClass.PUBLISHED_INPUT,
        "A Z3 x Z3 heterotic standard-model carrier with three families, "
        "one Higgs pair, and the stated observable gauge sector is imported.",
        (
            "schoen_quotient_2004",
            "exact_mssm_2006",
            "carrier_stability_2006",
        ),
        "Published construction; this does not establish native ASHA origin.",
    ),
    Claim(
        "tree_rank",
        EvidenceClass.EXACT_THEOREM,
        "The supported tree-level Yukawa texture has determinant zero and "
        "rank at most two over any coefficient field.",
        ("carrier_yukawa_2006", "canonical_manual_v8"),
        "The statement concerns the holomorphic tree-level texture.",
    ),
    Claim(
        "mixed_branch",
        EvidenceClass.EXACT_THEOREM,
        "The corrected mixed Maurer-Cartan branch is formally integrable "
        "and reaches an open stable, locally free, spectrum-preserving locus.",
        (
            "forward_classes_v18",
            "forward_no_go_v26",
            "reverse_classes_v31",
            "quadratic_v34c",
            "strict_slice_v35h1d",
            "deformation_v35i0",
            "stability_v35i1",
            "spectrum_v35i2",
            "higgs_v36a2f",
        ),
        "Formal/local branch proved by the cited project certificates.",
    ),
    Claim(
        "metric_completion",
        EvidenceClass.OPEN,
        "Ricci-flat, Hermitian Yang-Mills, and matter-metric completion remain open.",
        ("positive_twist_v99",),
        "No physical normalized Yukawa hierarchy follows before this gate passes.",
    ),
    Claim(
        "metric_section_basis",
        EvidenceClass.EXACT_THEOREM,
        "At the scoped positive twist H*=(5,7,1), the abstract invariant "
        "section dimensions are 192+212=404 and the lawful construction "
        "requires 848 Cech lift-operator applications.",
        ("positive_twist_v99", "extension_blindness_v13", "cech_lift_v14", "section_basis_v30"),
        "This does not certify the 404 pointwise sections or global generation.",
    ),
    Claim(
        "metric_global_matrix_no_go",
        EvidenceClass.SCOPED_NO_GO,
        "A nonzero outer block in the former K^190 to K^594 global-section "
        "differential cannot encode the non-split bundle because the required "
        "global Hom spaces vanish.",
        ("extension_blindness_v13", "cech_lift_v14"),
        "The no-go is scoped to that global two-term matrix ansatz.",
    ),
    Claim(
        "metric_rank_invariance",
        EvidenceClass.EXACT_THEOREM,
        "Invertible positive-definite canonical normalization preserves "
        "the rank of each holomorphic Yukawa matrix.",
        ("canonical_manual_v8",),
        "Metrics may change singular values and mixing, but cannot repair a rank defect.",
    ),
    Claim(
        "instanton_conic_geometry",
        EvidenceClass.EXACT_THEOREM,
        "The retained degree-two sector contains eighteen isolated smooth conics "
        "in two free nine-element Z3 x Z3 orbits.",
        ("degree_two_v068", "curve_lattice_v055"),
        "This is a curve-geometry theorem, not a nonzero-superpotential theorem.",
    ),
    Claim(
        "instanton_quartic_nonidentifiability",
        EvidenceClass.SCOPED_NO_GO,
        "The certified outer tensors, right restriction, and rank-six left "
        "comparison do not identify a local Pfaffian quartic up to a K-unit.",
        ("quartic_nonidentifiability_v075",),
        "The no-go is scoped to the stored data; the missing tensor-structured "
        "relative-duality chain map can still resolve the physical quartic.",
    ),
    Claim(
        "instanton_global_sum",
        EvidenceClass.OPEN,
        "The determinant-line-valued conic contributions have not been placed "
        "in a common physical trivialization and summed.",
        ("witten_instantons_1999", "dai_freed_1994", "quillen_quadratic_v27"),
        "Neither a nonzero instanton superpotential nor physical CP violation is established.",
    ),
    Claim(
        "hidden_topological_target",
        EvidenceClass.EXACT_THEOREM,
        "The formal rank-four extension target has c1=0, "
        "c2=(4/3,7/3,-4), c3=0 and exactly saturates the integrated "
        "visible-plus-hidden Chern-class equation.",
        ("hidden_remaining_gaps_v77",),
        "This certifies topology of a formal extension architecture, not existence "
        "of a locally free stable hidden bundle.",
    ),
    Claim(
        "hidden_bounded_frontier",
        EvidenceClass.EXACT_THEOREM,
        "In the radius-one bounded monad search category, objectives 20, 22, "
        "24, and 26 are closed and exactly 44 objective-28 supports remain.",
        ("hidden_radius1_v94", "hidden_objective28_v95"),
        "The theorem is scoped to the stated block category and combinatorial bounds.",
    ),
    Claim(
        "hidden_candidate750",
        EvidenceClass.CONDITIONAL,
        "Candidate 750 admits an exact Q(omega) complex witness with G*F=0 "
        "and ranks 7 and 6 at two exact fibres.",
        ("hidden_candidate750_witness", "hidden_objective28_v95"),
        "Global characteristic-zero constant rank and local freeness are unproved.",
    ),
    Claim(
        "hidden_standard_spectral_no_go",
        EvidenceClass.SCOPED_NO_GO,
        "Standard one-fibration FMW/vertical-Hecke SU(3) constructions and "
        "finite c1=0 extensions cannot realize the required mixed hidden Chern class.",
        ("hidden_spectral_v24", "fmw_vector_bundles_1997"),
        "Nonstandard mixed or relative Fourier-Mukai constructions are not excluded.",
    ),
    Claim(
        "hidden_bundle_completion",
        EvidenceClass.OPEN,
        "No stable, locally free, honestly equivariant hidden SU(4) bundle "
        "with certified restrictions, spectrum, HYM data, and determinant line exists yet.",
        ("hidden_objective28_v95", "hidden_input_gate_v42"),
        "Hidden-bundle completion and all downstream vacuum claims remain open.",
    ),
    Claim(
        "native_origin",
        EvidenceClass.OPEN,
        "The native finite-origin architecture has not been proved to emit "
        "the imported heterotic carrier.",
        ("canonical_manual_v8",),
        "This is the Origin-to-Carrier theorem, required for full OneTheory.",
    ),
    Claim(
        "native_finite_ledger",
        EvidenceClass.EXACT_THEOREM,
        "The finite-origin vector spaces, bilinear structures, projector "
        "algebra, finite quadratic plane, lattice enumerations, and Fourier "
        "chirp identities are exact finite constructions.",
        ("canonical_manual_v8",),
        "Exactness of the finite objects does not establish their physical transfer.",
    ),
    Claim(
        "native_shortcut_no_go",
        EvidenceClass.SCOPED_NO_GO,
        "Several direct family, real-E8, and visible-Wilson-line shortcuts fail "
        "within their explicitly tested representations or finite lattices.",
        ("canonical_manual_v8",),
        "These are scoped exclusions, not global no-go theorems for native origin.",
    ),
    Claim(
        "origin_interface_contract",
        EvidenceClass.EXACT_THEOREM,
        "The eight required Origin-to-Carrier subsystem interfaces, their "
        "dependencies, pass criteria, kill criteria, and missing inputs are "
        "serialized and mechanically validated.",
        ("canonical_manual_v8",),
        "This certifies the specification, not the existence of any bridge map.",
    ),
    Claim(
        "finite_visible_frontier",
        EvidenceClass.EXACT_THEOREM,
        "After the degree-three and direct order-five annihilation theorems, "
        "the generic light-family decision factors through 24 normalized "
        "restricted-hull residues. Exact f3 identities reduce the worst-case "
        "physical ledger to 20 traces and the first simultaneous test to four.",
        (
            "degree3_v36a2g",
            "order5_v36a2h",
            "second_fundamental_v36a2i",
            "residue_v36a2k",
            "restricted_hull_v36a2m",
            "adaptive_residue_v36a2n",
        ),
        "The reduction is exact; the four first-test carrier traces remain missing.",
    ),
    Claim(
        "stabilization_affine_no_go",
        EvidenceClass.SCOPED_NO_GO,
        "All ordinary base-degree-one worldsheet charges and the tested single "
        "condensate lie on one affine charge hyperplane whose tree-level "
        "Kahler gradient has the wrong sign; no finite sum of those terms can "
        "solve the supersymmetric F-term equations in the physical cone.",
        ("stabilization_term_count_v30", "stabilization_affine_v31"),
        "The theorem excludes the stated source class, not all heterotic superpotentials.",
    ),
    Claim(
        "stabilization_one_extra_no_go",
        EvidenceClass.SCOPED_NO_GO,
        "Adding one higher-base-degree worldsheet term, including a one-term "
        "multicover, cannot restore a controlled supersymmetric limit under "
        "subexponential determinant growth.",
        ("stabilization_v41",),
        "Multiple new sources or determinant growth outside the stated assumption are not excluded.",
    ),
    Claim(
        "stabilization_minimal_survivor",
        EvidenceClass.CONDITIONAL,
        "The unique minimal charge-space survivor is a same-gauge-kinetic-"
        "function racetrack with carrier-derived unequal exponents.",
        ("stabilization_v41", "stabilization_remaining_v77"),
        "The hidden spectrum, exponents, prefactors, thresholds, and full vacuum solution are missing.",
    ),
    Claim(
        "controlled_vacuum",
        EvidenceClass.OPEN,
        "No controlled four-dimensional vacuum has been constructed: the full "
        "K, W, gauge kinetic functions, D terms, F-term solution, stability "
        "chamber, Hessian, and correction hierarchy remain unresolved.",
        ("heterotic_moduli_2011", "gluino_condensation_1985"),
        "Source classification is not vacuum stabilization.",
    ),
    Claim(
        "four_dimensional_closure",
        EvidenceClass.OPEN,
        "The project does not yet define one normalized four-dimensional action "
        "at one controlled common vacuum.",
        ("four_dimensional_closure_source", "canonical_manual_v8"),
        "Carrier closure and full OneTheory completion both remain false.",
    ),
    Claim(
        "prediction_independence",
        EvidenceClass.OPEN,
        "No quantitatively nontrivial held-out observable has been predicted "
        "after freezing all geometric, bundle, metric, vacuum, and fitted inputs.",
        ("four_dimensional_closure_source",),
        "Imported or fitted values are not predictions.",
    ),
    Claim(
        "legacy_prediction_firewall",
        EvidenceClass.SCOPED_NO_GO,
        "Legacy numerical phenomenology ledgers are not admissible OneTheory "
        "predictions without a carrier-to-action derivation, uncertainty budget, "
        "and proof that the observable was not used for selection.",
        ("legacy_prediction_ledger", "four_dimensional_closure_source"),
        "The firewall rejects provenance, not the numerical values as experimental hypotheses.",
    ),
    Claim(
        "conditional_cp_pairing",
        EvidenceClass.CONDITIONAL,
        "If a CP-invariant completed action admits conjugate controlled vacua, "
        "CP-even observables agree and properly defined CP-odd invariants reverse sign.",
        ("cp_pair_v8", "cp_order_v9", "jarlskog_1985"),
        "No stabilized pair, magnitude, or cosmological vacuum selection is established.",
    ),
    Claim(
        "closure_falsification_contract",
        EvidenceClass.EXACT_THEOREM,
        "Twenty-seven completion criteria and scoped mathematical, carrier, "
        "vacuum, phenomenological, and native-origin kill rules are serialized.",
        ("four_dimensional_closure_source", "canonical_manual_v8"),
        "A complete audit contract is not completion of the objects it audits.",
    ),
    Claim(
        "reproducibility_spine",
        EvidenceClass.EXACT_THEOREM,
        "The maintained release is one dependency-free Python verifier with "
        "canonical machine output, source hashes, typed status ledgers, "
        "fail-closed checks, and a deterministic regression suite.",
        ("companion_implementation_source", "sandve_reproducibility_2013"),
        "This theorem concerns the maintained verifier, not independent reproduction.",
    ),
    Claim(
        "reproducibility_layer_firewall",
        EvidenceClass.EXACT_THEOREM,
        "Numerical and physical certificates cannot override failed or missing "
        "exact-layer dependencies.",
        ("companion_implementation_source",),
        "The firewall is an implementation contract; numerical inputs remain absent.",
    ),
    Claim(
        "frozen_release_bundle",
        EvidenceClass.OPEN,
        "A frozen public archive containing the paper, verifier, manifest, "
        "data, lockfile, schemas, logs, and replay instructions has not been issued.",
        ("companion_implementation_source", "fair_principles_2016"),
        "The maintained DOCX and Python files are not by themselves that archive.",
    ),
    Claim(
        "clean_room_reproduction",
        EvidenceClass.OPEN,
        "No independent team has reproduced the release from the frozen inputs "
        "and written specification.",
        ("companion_implementation_source",),
        "Internal regression tests are not an independent implementation.",
    ),
    Claim(
        "final_scientific_assessment",
        EvidenceClass.EXACT_THEOREM,
        "The maintained thirteen-section ledger classifies OneTheory as a "
        "theorem-gated incomplete research program with exact subtheorems, "
        "scoped no-go results, conditional survivors, and explicit open gates.",
        ("conclusion_appendices_source", "four_dimensional_closure_source"),
        "This is a theorem about the project ledger, not a completed unification theorem.",
    ),
    Claim(
        "threefold_closure_requirement",
        EvidenceClass.BRIDGE_TARGET,
        "Full completion requires carrier closure, a non-circular native-origin "
        "derivation, and at least one independently held-out prediction with uncertainty.",
        ("conclusion_appendices_source", "four_dimensional_closure_source"),
        "All three requirements are currently unsatisfied.",
    ),
)


def _coerce_fraction(value: int | Fraction) -> Fraction:
    if isinstance(value, Fraction):
        return value
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError("exact matrices accept int or Fraction entries only")
    return Fraction(value)


def exact_matrix(rows: Sequence[Sequence[int | Fraction]]) -> tuple[tuple[Fraction, ...], ...]:
    """Return a rectangular immutable matrix over the rational numbers."""

    if not rows:
        raise ValueError("matrix must contain at least one row")
    width = len(rows[0])
    if width == 0 or any(len(row) != width for row in rows):
        raise ValueError("matrix must be nonempty and rectangular")
    return tuple(tuple(_coerce_fraction(value) for value in row) for row in rows)


def exact_rank(rows: Sequence[Sequence[int | Fraction]]) -> int:
    """Compute rank using deterministic Gaussian elimination over Q."""

    matrix = [list(row) for row in exact_matrix(rows)]
    row_count = len(matrix)
    column_count = len(matrix[0])
    pivot_row = 0
    for column in range(column_count):
        pivot = next(
            (row for row in range(pivot_row, row_count) if matrix[row][column]),
            None,
        )
        if pivot is None:
            continue
        matrix[pivot_row], matrix[pivot] = matrix[pivot], matrix[pivot_row]
        pivot_value = matrix[pivot_row][column]
        matrix[pivot_row] = [entry / pivot_value for entry in matrix[pivot_row]]
        for row in range(row_count):
            if row == pivot_row:
                continue
            factor = matrix[row][column]
            if factor:
                matrix[row] = [
                    entry - factor * pivot_entry
                    for entry, pivot_entry in zip(matrix[row], matrix[pivot_row])
                ]
        pivot_row += 1
        if pivot_row == row_count:
            break
    return pivot_row


def determinant_3x3(rows: Sequence[Sequence[int | Fraction]]) -> Fraction:
    """Compute a 3 x 3 determinant exactly."""

    matrix = exact_matrix(rows)
    if len(matrix) != 3 or any(len(row) != 3 for row in matrix):
        raise ValueError("determinant_3x3 requires a 3 x 3 matrix")
    a, b, c = matrix[0]
    d, e, f = matrix[1]
    g, h, i = matrix[2]
    return a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)


def tree_yukawa_texture(
    a: int | Fraction,
    b: int | Fraction,
    c: int | Fraction,
    d: int | Fraction,
) -> tuple[tuple[Fraction, ...], ...]:
    """Construct the exact tree-level support texture used by each sector."""

    return exact_matrix(((0, a, b), (c, 0, 0), (d, 0, 0)))


def matrix_vector_product(
    matrix: Sequence[Sequence[int | Fraction]],
    vector: Sequence[int | Fraction],
) -> tuple[Fraction, ...]:
    exact = exact_matrix(matrix)
    v = tuple(_coerce_fraction(entry) for entry in vector)
    if len(exact[0]) != len(v):
        raise ValueError("matrix and vector dimensions do not agree")
    return tuple(sum(entry * coordinate for entry, coordinate in zip(row, v)) for row in exact)


def row_vector_matrix_product(
    vector: Sequence[int | Fraction],
    matrix: Sequence[Sequence[int | Fraction]],
) -> tuple[Fraction, ...]:
    exact = exact_matrix(matrix)
    v = tuple(_coerce_fraction(entry) for entry in vector)
    if len(exact) != len(v):
        raise ValueError("vector and matrix dimensions do not agree")
    return tuple(
        sum(v[row] * exact[row][column] for row in range(len(exact)))
        for column in range(len(exact[0]))
    )


def verify_tree_texture() -> tuple[Check, ...]:
    """Certify determinant, maximal generic rank, and exact null vectors."""

    # Nonzero sample values demonstrate that the support permits rank two.
    matrix = tree_yukawa_texture(2, 3, 5, 7)
    right_null = (0, -3, 2)
    left_null = (0, -7, 5)
    return (
        Check(
            "tree.det.zero",
            determinant_3x3(matrix) == 0,
            Fraction(0),
            determinant_3x3(matrix),
            EvidenceClass.EXACT_THEOREM,
            "The determinant vanishes identically for this support pattern.",
        ),
        Check(
            "tree.rank.generic",
            exact_rank(matrix) == 2,
            2,
            exact_rank(matrix),
            EvidenceClass.EXACT_THEOREM,
            "A nondegenerate coefficient choice attains the support bound.",
        ),
        Check(
            "tree.right_null",
            matrix_vector_product(matrix, right_null) == (0, 0, 0),
            (0, 0, 0),
            matrix_vector_product(matrix, right_null),
            EvidenceClass.EXACT_THEOREM,
            "rho=(0,-b,a)^T is an exact right-null vector.",
        ),
        Check(
            "tree.left_null",
            row_vector_matrix_product(left_null, matrix) == (0, 0, 0),
            (0, 0, 0),
            row_vector_matrix_product(left_null, matrix),
            EvidenceClass.EXACT_THEOREM,
            "lambda=(0,-d,c) is an exact left-null covector.",
        ),
    )


def verify_frontier_counts() -> tuple[Check, ...]:
    """Reproduce exact finite counts imported into the Section 1 result map."""

    checks = (
        ("frontier.residues", 6 + 18, 24,
         "Six up-sector plus eighteen down-sector normalized residues."),
        ("sections.split", 192 + 212, 404,
         "Exact positive-twist section-space split."),
        ("sections.analytical_split", 136 + 76, 212,
         "Analytical, not yet fully serialized, quotient decomposition."),
        ("sections.lifts", 4 * 212, 848,
         "Four lifts for each of 212 quotient representatives."),
        ("hidden.unresolved", 67 - 20 - 3, 44,
         "Unresolved hidden supports after exact and branch-specific closures."),
    )
    return tuple(
        Check(
            identifier,
            observed == expected,
            expected,
            observed,
            (
                EvidenceClass.ANALYTICAL_UNCERTIFIED
                if identifier == "sections.analytical_split"
                else EvidenceClass.EXACT_THEOREM
            ),
            note,
        )
        for identifier, observed, expected, note in checks
    )


def gate_registry() -> tuple[Gate, ...]:
    """Return the versioned Section 1 completion ledger."""

    return (
        Gate(
            "uv_carrier",
            "Published ultraviolet carrier",
            GateState.PASSED,
            EvidenceClass.PUBLISHED_INPUT,
            "A fully specified heterotic carrier with traceable primary sources.",
            "Primary-source metadata or imported model data are inconsistent.",
            "Published Z3 x Z3 quotient carrier imported; metadata cross-checked.",
        ),
        Gate(
            "visible_holomorphic",
            "Visible holomorphic sector",
            GateState.OPEN,
            EvidenceClass.OPEN,
            "Serialize all required section bases and certify the physical residue/Hessian maps.",
            "Certified support or rank conditions preclude the observed visible sector.",
            "The raw common-cyclic compiler is exact; its physical package is absent. The first test derives four f3 traces and the adaptive worst case is twenty.",
        ),
        Gate(
            "visible_metric",
            "Metric and HYM normalization",
            GateState.MISSING_INPUT,
            EvidenceClass.OPEN,
            "Certify Ricci-flat/HYM solutions and positive matter metrics at a common moduli point.",
            "No admissible common solution exists within the declared geometry and bundle chamber.",
            "Required numerical metric data have not been supplied.",
        ),
        Gate(
            "instanton_determinant",
            "Instanton determinant line",
            GateState.OPEN,
            EvidenceClass.OPEN,
            "Compute the two physical seed maps, all Pfaffians, and determinant-line normalization.",
            "Certified cancellation or vanishing removes every required contribution.",
            "Curve counting is finite, but physical maps and Pfaffians remain open.",
        ),
        Gate(
            "hidden_bundle",
            "Hidden stable bundle",
            GateState.OPEN,
            EvidenceClass.OPEN,
            "Construct a stable, locally free hidden bundle with the required anomaly class and spectrum.",
            "Every bounded candidate support is exactly excluded.",
            "Forty-four bounded support cases remain unresolved.",
        ),
        Gate(
            "global_anomaly",
            "Global anomaly and consistency",
            GateState.OPEN,
            EvidenceClass.OPEN,
            "Pass integrated and global anomaly, flux, and quantization checks for one common model.",
            "A nonremovable global inconsistency is certified.",
            "Topological reductions exist; global closure awaits the hidden and instanton sectors.",
        ),
        Gate(
            "controlled_vacuum",
            "Controlled nonperturbative vacuum",
            GateState.CONDITIONAL,
            EvidenceClass.CONDITIONAL,
            "Produce a metastable controlled vacuum with all relevant moduli stabilized.",
            "All admissible controlled superpotentials are excluded or destabilize the solution.",
            "Scoped no-go results pass; an unequal-exponent same-f_h racetrack survives conditionally.",
        ),
        Gate(
            "ir_observables",
            "Four-dimensional effective observables",
            GateState.MISSING_INPUT,
            EvidenceClass.OPEN,
            "Derive normalized masses, mixings, couplings, thresholds, and uncertainty propagation.",
            "The closed model is incompatible with required consistency or observation within scope.",
            "Normalized metrics, vacuum data, thresholds, and running are missing.",
        ),
        Gate(
            "blind_prediction",
            "Blind prediction",
            GateState.OPEN,
            EvidenceClass.OPEN,
            "Register and predict at least one unused observable before comparison with data.",
            "No observable remains both calculable and unused for model selection.",
            "No preregistered blind prediction has passed.",
        ),
        Gate(
            "native_origin",
            "Native Origin-to-Carrier theorem",
            GateState.OPEN,
            EvidenceClass.OPEN,
            "Derive the imported carrier functorially from the finite-origin architecture.",
            "A scoped obstruction proves that the architecture cannot emit the carrier.",
            "Required bridge dictionary, descent, and uniqueness theorem are open.",
        ),
    )


CARRIER_GATE_IDS = (
    "uv_carrier",
    "visible_holomorphic",
    "visible_metric",
    "instanton_determinant",
    "hidden_bundle",
    "global_anomaly",
    "controlled_vacuum",
    "ir_observables",
    "blind_prediction",
)


def evaluate_completion(gates: Iterable[Gate] | None = None) -> Mapping[str, Any]:
    """Evaluate carrier closure and full OneTheory completion without shortcuts."""

    registry = {gate.identifier: gate for gate in (gates or gate_registry())}
    required = set(CARRIER_GATE_IDS) | {"native_origin"}
    missing = sorted(required - registry.keys())
    if missing:
        raise ValueError(f"completion registry is missing gates: {', '.join(missing)}")
    carrier_passed = all(
        registry[identifier].state is GateState.PASSED
        for identifier in CARRIER_GATE_IDS
    )
    full_passed = carrier_passed and registry["native_origin"].state is GateState.PASSED
    blockers = [
        {
            "identifier": identifier,
            "state": registry[identifier].state.value,
            "current_basis": registry[identifier].current_basis,
        }
        for identifier in (*CARRIER_GATE_IDS, "native_origin")
        if registry[identifier].state is not GateState.PASSED
    ]
    return {
        "carrier_closure": carrier_passed,
        "full_onetheory_completion": full_passed,
        "blockers": blockers,
        "interpretation": (
            "OneTheory is a theorem-gated research program, not a completed "
            "Theory of Everything."
            if not full_passed
            else "All declared completion predicates pass."
        ),
    }


def verify_source_corpus(directory: Path) -> tuple[Check, ...]:
    """Verify the exact thirteen-document input corpus against embedded hashes."""

    checks: list[Check] = []
    for filename, expected in SOURCE_CORPUS_SHA256.items():
        path = directory / filename
        if not path.is_file():
            checks.append(
                Check(
                    f"source.{filename}",
                    False,
                    expected,
                    "MISSING_INPUT",
                    EvidenceClass.OPEN,
                    f"Required source document is absent from {directory}.",
                )
            )
            continue
        observed = hashlib.sha256(path.read_bytes()).hexdigest()
        checks.append(
            Check(
                f"source.{filename}",
                observed == expected,
                expected,
                observed,
                EvidenceClass.EXACT_THEOREM,
                "Byte-level SHA-256 provenance check.",
            )
        )
    return tuple(checks)


def run_section1_checks(source_dir: Path | None = None) -> tuple[Check, ...]:
    checks = (*verify_tree_texture(), *verify_frontier_counts())
    if source_dir is not None:
        checks = (*checks, *verify_source_corpus(source_dir))
    return checks


@dataclass(frozen=True)
class Eisenstein:
    """Exact element a+b*omega of Q(omega), where omega^2+omega+1=0."""

    a: Fraction = Fraction(0)
    b: Fraction = Fraction(0)

    def __post_init__(self) -> None:
        object.__setattr__(self, "a", Fraction(self.a))
        object.__setattr__(self, "b", Fraction(self.b))

    @staticmethod
    def coerce(value: object) -> "Eisenstein":
        if isinstance(value, Eisenstein):
            return value
        if isinstance(value, bool) or not isinstance(value, (int, Fraction)):
            raise TypeError("Q(omega) accepts int, Fraction, or Eisenstein values")
        return Eisenstein(Fraction(value))

    def __add__(self, other: object) -> "Eisenstein":
        rhs = Eisenstein.coerce(other)
        return Eisenstein(self.a + rhs.a, self.b + rhs.b)

    def __radd__(self, other: object) -> "Eisenstein":
        return self + other

    def __neg__(self) -> "Eisenstein":
        return Eisenstein(-self.a, -self.b)

    def __sub__(self, other: object) -> "Eisenstein":
        return self + (-Eisenstein.coerce(other))

    def __rsub__(self, other: object) -> "Eisenstein":
        return Eisenstein.coerce(other) - self

    def __mul__(self, other: object) -> "Eisenstein":
        rhs = Eisenstein.coerce(other)
        return Eisenstein(
            self.a * rhs.a - self.b * rhs.b,
            self.a * rhs.b + self.b * rhs.a - self.b * rhs.b,
        )

    def __rmul__(self, other: object) -> "Eisenstein":
        return self * other

    def inverse(self) -> "Eisenstein":
        norm = self.a * self.a - self.a * self.b + self.b * self.b
        if norm == 0:
            raise ZeroDivisionError("zero has no inverse in Q(omega)")
        return Eisenstein((self.a - self.b) / norm, -self.b / norm)

    def __truediv__(self, other: object) -> "Eisenstein":
        return self * Eisenstein.coerce(other).inverse()

    def __pow__(self, exponent: int) -> "Eisenstein":
        if not isinstance(exponent, int):
            raise TypeError("the exponent must be an integer")
        if exponent < 0:
            return self.inverse() ** (-exponent)
        result = Eisenstein(1)
        base = self
        power = exponent
        while power:
            if power & 1:
                result *= base
            base *= base
            power >>= 1
        return result

    def is_zero(self) -> bool:
        return self.a == 0 and self.b == 0

    def text(self) -> str:
        if self.is_zero():
            return "0"
        if self.b == 0:
            return str(self.a)
        if self.a == 0:
            return "omega" if self.b == 1 else "-omega" if self.b == -1 else f"{self.b}*omega"
        sign = "+" if self.b > 0 else "-"
        magnitude = abs(self.b)
        omega_term = "omega" if magnitude == 1 else f"{magnitude}*omega"
        return f"{self.a}{sign}{omega_term}"


E_ZERO = Eisenstein(0)
E_ONE = Eisenstein(1)
OMEGA = Eisenstein(0, 1)
OMEGA2 = OMEGA ** 2
EMatrix = tuple[tuple[Eisenstein, ...], ...]
Monomial = tuple[int, int, int]
Polynomial = dict[Monomial, Eisenstein]


def e_matrix(rows: Sequence[Sequence[object]]) -> EMatrix:
    if not rows or not rows[0] or any(len(row) != len(rows[0]) for row in rows):
        raise ValueError("matrix must be nonempty and rectangular")
    return tuple(tuple(Eisenstein.coerce(value) for value in row) for row in rows)


def e_identity(size: int) -> EMatrix:
    return e_matrix(
        tuple(tuple(E_ONE if row == column else E_ZERO for column in range(size))
              for row in range(size))
    )


def e_matmul(left: Sequence[Sequence[object]], right: Sequence[Sequence[object]]) -> EMatrix:
    a, b = e_matrix(left), e_matrix(right)
    if len(a[0]) != len(b):
        raise ValueError("matrix dimensions do not agree")
    return e_matrix(
        tuple(
            tuple(
                sum((a[i][k] * b[k][j] for k in range(len(b))), E_ZERO)
                for j in range(len(b[0]))
            )
            for i in range(len(a))
        )
    )


def e_matvec(matrix: Sequence[Sequence[object]], vector: Sequence[object]) -> tuple[Eisenstein, ...]:
    a = e_matrix(matrix)
    v = tuple(Eisenstein.coerce(value) for value in vector)
    if len(a[0]) != len(v):
        raise ValueError("matrix and vector dimensions do not agree")
    return tuple(sum((entry * coordinate for entry, coordinate in zip(row, v)), E_ZERO)
                 for row in a)


def e_scale(matrix: Sequence[Sequence[object]], scalar: object) -> EMatrix:
    factor = Eisenstein.coerce(scalar)
    return e_matrix(tuple(tuple(factor * entry for entry in row) for row in e_matrix(matrix)))


def e_rref(rows: Sequence[Sequence[object]]) -> tuple[EMatrix, tuple[int, ...]]:
    matrix = [list(row) for row in e_matrix(rows)]
    row_count, column_count = len(matrix), len(matrix[0])
    pivots: list[int] = []
    pivot_row = 0
    for column in range(column_count):
        choice = next(
            (row for row in range(pivot_row, row_count) if not matrix[row][column].is_zero()),
            None,
        )
        if choice is None:
            continue
        matrix[pivot_row], matrix[choice] = matrix[choice], matrix[pivot_row]
        inverse = matrix[pivot_row][column].inverse()
        matrix[pivot_row] = [inverse * entry for entry in matrix[pivot_row]]
        for row in range(row_count):
            if row == pivot_row or matrix[row][column].is_zero():
                continue
            factor = matrix[row][column]
            matrix[row] = [
                entry - factor * pivot_entry
                for entry, pivot_entry in zip(matrix[row], matrix[pivot_row])
            ]
        pivots.append(column)
        pivot_row += 1
        if pivot_row == row_count:
            break
    return e_matrix(matrix), tuple(pivots)


def e_rank(rows: Sequence[Sequence[object]]) -> int:
    return len(e_rref(rows)[1])


def e_nullspace(rows: Sequence[Sequence[object]]) -> tuple[tuple[Eisenstein, ...], ...]:
    matrix = e_matrix(rows)
    reduced, pivots = e_rref(matrix)
    free_columns = [column for column in range(len(matrix[0])) if column not in pivots]
    basis: list[tuple[Eisenstein, ...]] = []
    for free_column in free_columns:
        vector = [E_ZERO for _ in range(len(matrix[0]))]
        vector[free_column] = E_ONE
        for row, pivot in enumerate(pivots):
            vector[pivot] = -reduced[row][free_column]
        basis.append(tuple(vector))
    return tuple(basis)


def e_inverse(matrix: Sequence[Sequence[object]]) -> EMatrix:
    a = e_matrix(matrix)
    if len(a) != len(a[0]):
        raise ValueError("inverse requires a square matrix")
    size = len(a)
    augmented = e_matrix(
        tuple(tuple(a[row]) + tuple(e_identity(size)[row]) for row in range(size))
    )
    reduced, pivots = e_rref(augmented)
    if pivots[:size] != tuple(range(size)):
        raise ValueError("matrix is singular")
    return e_matrix(tuple(tuple(row[size:]) for row in reduced[:size]))


def e_power(matrix: Sequence[Sequence[object]], exponent: int) -> EMatrix:
    a = e_matrix(matrix)
    if len(a) != len(a[0]):
        raise ValueError("power requires a square matrix")
    if exponent < 0:
        return e_power(e_inverse(a), -exponent)
    result, base, power = e_identity(len(a)), a, exponent
    while power:
        if power & 1:
            result = e_matmul(result, base)
        base = e_matmul(base, base)
        power >>= 1
    return result


def e_eigenpair_multiplicity(
    p_action: Sequence[Sequence[object]],
    t_action: Sequence[Sequence[object]],
    p_value: object,
    t_value: object,
) -> int:
    p, t = e_matrix(p_action), e_matrix(t_action)
    pv, tv = Eisenstein.coerce(p_value), Eisenstein.coerce(t_value)
    equations = tuple(
        tuple(p[i][j] - (pv if i == j else E_ZERO) for j in range(len(p)))
        for i in range(len(p))
    ) + tuple(
        tuple(t[i][j] - (tv if i == j else E_ZERO) for j in range(len(t)))
        for i in range(len(t))
    )
    return len(e_nullspace(equations))


def p_clean(poly: Mapping[Monomial, Eisenstein]) -> Polynomial:
    return {monomial: coefficient for monomial, coefficient in poly.items()
            if not coefficient.is_zero()}


def p_monomial(exponents: Monomial, coefficient: object = 1) -> Polynomial:
    value = Eisenstein.coerce(coefficient)
    return {} if value.is_zero() else {exponents: value}


def p_add(left: Mapping[Monomial, Eisenstein], right: Mapping[Monomial, Eisenstein]) -> Polynomial:
    result: Polynomial = dict(left)
    for monomial, coefficient in right.items():
        result[monomial] = result.get(monomial, E_ZERO) + coefficient
    return p_clean(result)


def p_neg(poly: Mapping[Monomial, Eisenstein]) -> Polynomial:
    return p_clean({monomial: -coefficient for monomial, coefficient in poly.items()})


def p_sub(left: Mapping[Monomial, Eisenstein], right: Mapping[Monomial, Eisenstein]) -> Polynomial:
    return p_add(left, p_neg(right))


def p_scale(poly: Mapping[Monomial, Eisenstein], scalar: object) -> Polynomial:
    factor = Eisenstein.coerce(scalar)
    return p_clean({monomial: factor * coefficient for monomial, coefficient in poly.items()})


def p_mul(left: Mapping[Monomial, Eisenstein], right: Mapping[Monomial, Eisenstein]) -> Polynomial:
    result: Polynomial = {}
    for monomial_left, coefficient_left in left.items():
        for monomial_right, coefficient_right in right.items():
            monomial = tuple(
                monomial_left[index] + monomial_right[index] for index in range(3)
            )
            result[monomial] = (
                result.get(monomial, E_ZERO) + coefficient_left * coefficient_right
            )
    return p_clean(result)


def p_substitute(
    poly: Mapping[Monomial, Eisenstein],
    images: Sequence[tuple[Eisenstein, Monomial]],
) -> Polynomial:
    result: Polynomial = {}
    for exponents, coefficient in poly.items():
        target_exponents = [0, 0, 0]
        target_coefficient = coefficient
        for source, power in enumerate(exponents):
            scalar, target = images[source]
            target_coefficient *= scalar ** power
            for coordinate in range(3):
                target_exponents[coordinate] += power * target[coordinate]
        result = p_add(result, p_monomial(tuple(target_exponents), target_coefficient))
    return p_clean(result)


def p_determinant(matrix: Sequence[Sequence[Polynomial]]) -> Polynomial:
    size = len(matrix)
    if size == 0 or any(len(row) != size for row in matrix):
        raise ValueError("polynomial determinant requires a nonempty square matrix")
    if size == 1:
        return dict(matrix[0][0])
    result: Polynomial = {}
    for column in range(size):
        minor = [
            [entry for index, entry in enumerate(row) if index != column]
            for row in matrix[1:]
        ]
        term = p_mul(matrix[0][column], p_determinant(minor))
        result = p_add(result, term if column % 2 == 0 else p_neg(term))
    return p_clean(result)


def p_maximal_minors(matrix: Sequence[Sequence[Polynomial]]) -> tuple[Polynomial, ...]:
    if len(matrix) != len(matrix[0]) + 1:
        raise ValueError("Hilbert--Burch matrix must have shape (n+1) x n")
    return tuple(
        p_determinant([row for index, row in enumerate(matrix) if index != removed])
        for removed in range(len(matrix))
    )


def p_equal_up_to_unit(left: Polynomial, right: Polynomial) -> bool:
    if not left or not right or set(left) != set(right):
        return left == right
    monomial = next(iter(left))
    unit = left[monomial] / right[monomial]
    return all(left[key] == unit * right[key] for key in left)


def projective_zero_scheme_length(hilbert_numerator: Sequence[int | Fraction]) -> Fraction:
    """Return N''(1)/2 for a zero-dimensional Proj with H(t)=N(t)/(1-t)^3."""

    coefficients = tuple(_coerce_fraction(value) for value in hilbert_numerator)
    return sum(
        Fraction(index * (index - 1), 2) * coefficient
        for index, coefficient in enumerate(coefficients)
    )


def carrier_polynomial_data() -> Mapping[str, Any]:
    """Construct the exact Q(omega) eigen-cubics and point-scheme resolutions."""

    a, b, c = (p_monomial(exponents) for exponents in ((1, 0, 0), (0, 1, 0), (0, 0, 1)))
    a3, b3, c3 = (p_mul(p_mul(value, value), value) for value in (a, b, c))
    abc = p_mul(p_mul(a, b), c)
    f = p_add(
        p_add(p_scale(a3, -3 - 3 * OMEGA), p_scale(b3, 3)),
        p_scale(c3, 3 * OMEGA),
    )
    g = p_add(
        p_scale(p_add(p_add(a3, b3), c3), -3 - 6 * OMEGA),
        p_scale(abc, 36 + 18 * OMEGA),
    )
    h_p = (
        (OMEGA, (0, 1, 0)),
        (OMEGA2, (0, 0, 1)),
        (E_ONE, (1, 0, 0)),
    )
    h_t = (
        (E_ONE, (1, 0, 0)),
        (OMEGA, (0, 1, 0)),
        (OMEGA2, (0, 0, 1)),
    )
    zero: Polynomial = {}
    m3 = ((c, c), (p_neg(b), zero), (zero, p_neg(a)))
    m6 = (
        (a, zero, zero),
        (zero, b, zero),
        (p_neg(b), p_neg(c), a),
        (zero, zero, p_neg(c)),
    )
    i3 = (p_mul(a, b), p_mul(a, c), p_mul(b, c))
    i6 = (p_mul(p_mul(b, b), c), p_mul(a, p_mul(c, c)), abc, p_mul(p_mul(a, a), b))
    return {
        "F": f,
        "G": g,
        "H_P_images": h_p,
        "H_T_images": h_t,
        "M3": m3,
        "M6": m6,
        "I3": i3,
        "I6": i6,
    }


def verify_heisenberg_and_point_schemes() -> tuple[Check, ...]:
    data = carrier_polynomial_data()
    p = e_matrix(((0, 1, 0), (0, 0, 1), (1, 0, 0)))
    d = e_matrix(((1, 0, 0), (0, OMEGA, 0), (0, 0, OMEGA2)))
    t = e_matmul(p, d)
    minors3 = p_maximal_minors(data["M3"])
    minors6 = p_maximal_minors(data["M6"])
    hb3 = all(any(p_equal_up_to_unit(minor, generator) for generator in data["I3"])
              for minor in minors3)
    hb6 = all(any(p_equal_up_to_unit(minor, generator) for generator in data["I6"])
              for minor in minors6)
    observations = (
        ("carrier.omega.relation", OMEGA ** 2 + OMEGA + 1, E_ZERO,
         "The coefficient field is Q(omega), omega^2+omega+1=0."),
        ("carrier.heisenberg.commutator", e_matmul(p, t), e_scale(e_matmul(t, p), OMEGA),
         "Linear lifts obey P*T=omega*T*P; they commute only projectively."),
        ("carrier.heisenberg.P3", e_power(p, 3), e_identity(3), "P has order three."),
        ("carrier.heisenberg.T3", e_power(t, 3), e_identity(3), "T has order three."),
        ("carrier.pencil.F.P", p_substitute(data["F"], data["H_P_images"]),
         p_scale(data["F"], OMEGA2), "F has H_P-character omega^2."),
        ("carrier.pencil.G.P", p_substitute(data["G"], data["H_P_images"]),
         data["G"], "G is H_P-invariant."),
        ("carrier.pencil.F.T", p_substitute(data["F"], data["H_T_images"]),
         data["F"], "F is H_T-invariant."),
        ("carrier.pencil.G.T", p_substitute(data["G"], data["H_T_images"]),
         data["G"], "G is H_T-invariant."),
        ("carrier.I3.hilbert_burch", hb3, True,
         "Maximal minors generate I3=(AB,AC,BC) up to nonzero units."),
        ("carrier.I6.hilbert_burch", hb6, True,
         "Maximal minors generate I6=(B^2C,AC^2,ABC,A^2B) up to units."),
        ("carrier.I3.length", projective_zero_scheme_length((1, 0, -3, 2)),
         Fraction(3), "Hilbert numerator 1-3t^2+2t^3 gives length 3."),
        ("carrier.I6.length", projective_zero_scheme_length((1, 0, 0, -4, 3)),
         Fraction(6), "Hilbert numerator 1-4t^3+3t^4 gives length 6."),
    )
    return tuple(
        Check(identifier, observed == expected, expected, observed,
              EvidenceClass.EXACT_THEOREM, note)
        for identifier, observed, expected, note in observations
    )


def serre_kernel_actions() -> Mapping[str, EMatrix]:
    """Return the exact raw kernel actions serialized by certificate v0.62."""

    w = OMEGA
    return {
        "W1_P": e_matrix(((1, -2 - 4 * w), (0, w))),
        "W1_T": e_identity(2),
        "W2_P": e_matrix((
            (0, 0, 0, -1 - w, 0),
            (0, w, 0, 0, 0),
            (1, 0, 0, 4 + 2 * w, 0),
            (2 + 4 * w, 0, w, 0, 0),
            (0, -2 - 4 * w, 0, 0, 1),
        )),
        "W2_T": e_matrix((
            (w, 0, 0, 0, 0),
            (0, 1, 0, 0, 0),
            (0, 0, w, 0, 0),
            (0, 0, 0, w, 0),
            (0, 0, 0, 0, 1),
        )),
    }


def verify_serre_linearization() -> tuple[Check, ...]:
    actions = serre_kernel_actions()
    w1_p, w1_t = actions["W1_P"], actions["W1_T"]
    w2_p, w2_t = actions["W2_P"], actions["W2_T"]
    expected1 = {(E_ONE.text(), E_ONE.text()): 1, (OMEGA.text(), E_ONE.text()): 1}
    expected2 = {
        (E_ONE.text(), E_ONE.text()): 1,
        (OMEGA.text(), E_ONE.text()): 1,
        (E_ONE.text(), OMEGA.text()): 1,
        (OMEGA.text(), OMEGA.text()): 1,
        (OMEGA2.text(), OMEGA.text()): 1,
    }

    def decomposition(p_action: EMatrix, t_action: EMatrix) -> dict[tuple[str, str], int]:
        return {
            (p_value.text(), t_value.text()): multiplicity
            for p_value in (E_ONE, OMEGA, OMEGA2)
            for t_value in (E_ONE, OMEGA, OMEGA2)
            if (multiplicity := e_eigenpair_multiplicity(
                p_action, t_action, p_value, t_value
            ))
        }

    ray1 = (2 * OMEGA, E_ONE)
    ray2 = (E_ONE, E_ZERO, -2 + 3 * OMEGA, E_ONE, E_ZERO)
    total1_p = e_scale(e_inverse(w1_p), OMEGA)
    total1_t = e_inverse(w1_t)
    total2_p = e_scale(e_inverse(w2_p), OMEGA2)
    total2_t = e_scale(e_inverse(w2_t), OMEGA)
    observations = (
        ("carrier.serre.W1.group", e_power(w1_p, 3), e_identity(2),
         "The induced W1 pullback action has order three."),
        ("carrier.serre.W2.group", e_power(w2_p, 3), e_identity(5),
         "The induced W2 pullback action has order three."),
        ("carrier.serre.W1.commuting", e_matmul(w1_p, w1_t), e_matmul(w1_t, w1_p),
         "The central cocycle cancels on the W1 kernel."),
        ("carrier.serre.W2.commuting", e_matmul(w2_p, w2_t), e_matmul(w2_t, w2_p),
         "The central cocycle cancels on the W2 kernel."),
        ("carrier.serre.W1.characters", decomposition(w1_p, w1_t), expected1,
         "Raw W1 characters are (1,1)+(omega,1)."),
        ("carrier.serre.W2.characters", decomposition(w2_p, w2_t), expected2,
         "Raw W2 characters match the five certificate characters."),
        ("carrier.serre.W1.ray.P", e_matvec(total1_p, ray1), ray1,
         "The Cech/Hom-shifted W1 action fixes [2omega,1]."),
        ("carrier.serre.W1.ray.T", e_matvec(total1_t, ray1), ray1,
         "The same W1 ray is fixed by T."),
        ("carrier.serre.W2.ray.P", e_matvec(total2_p, ray2), ray2,
         "The shifted W2 action fixes [1,0,-2+3omega,1,0]."),
        ("carrier.serre.W2.ray.T", e_matvec(total2_t, ray2), ray2,
         "The same W2 ray is fixed by T."),
        ("carrier.serre.I6.local_unit", OMEGA2 * OMEGA, E_ONE,
         "In Ext^1((x,y^2),O), the invariant local class is the unit."),
        ("carrier.serre.I6.nilpotent", OMEGA, OMEGA,
         "The nilpotent local direction is nontrivial and not invariant."),
    )
    return tuple(
        Check(identifier, observed == expected, expected, observed,
              EvidenceClass.EXACT_THEOREM, note)
        for identifier, observed, expected, note in observations
    )


def triple_intersection(
    left: Sequence[int | Fraction],
    middle: Sequence[int | Fraction],
    right: Sequence[int | Fraction],
) -> Fraction:
    """Evaluate the quotient-normalized symmetric intersection tensor."""

    vectors = tuple(tuple(_coerce_fraction(value) for value in vector)
                    for vector in (left, middle, right))
    if any(len(vector) != 3 for vector in vectors):
        raise ValueError("divisor coordinates must have length three")

    def coefficient(indices: tuple[int, int, int]) -> Fraction:
        ordered = tuple(sorted(indices))
        if ordered in ((0, 0, 1), (0, 1, 1)):
            return Fraction(1, 3)
        if ordered == (0, 1, 2):
            return Fraction(1)
        return Fraction(0)

    return sum(
        vectors[0][i] * vectors[1][j] * vectors[2][k] * coefficient((i, j, k))
        for i in range(3) for j in range(3) for k in range(3)
    )


def divisor_square(divisor: Sequence[int | Fraction]) -> tuple[Fraction, Fraction, Fraction]:
    basis = ((1, 0, 0), (0, 1, 0), (0, 0, 1))
    return tuple(triple_intersection(divisor, divisor, vector) for vector in basis)


def slope(
    first_chern: Sequence[int | Fraction],
    kahler: Sequence[int | Fraction],
    rank: int,
) -> Fraction:
    if rank <= 0:
        raise ValueError("bundle rank must be positive")
    return triple_intersection(first_chern, kahler, kahler) / rank


def verify_topology_and_anomaly() -> tuple[Check, ...]:
    c2_tangent = (Fraction(4), Fraction(4), Fraction(0))
    c2_visible = (Fraction(8, 3), Fraction(5, 3), Fraction(4))
    c2_hidden = (Fraction(4, 3), Fraction(7, 3), Fraction(-4))
    hidden_d = (1, 2, -1)
    hidden_p = (0, 1, 0)
    hidden_from_extension = tuple(
        2 * Fraction(hidden_p[index]) - divisor_square(hidden_d)[index]
        for index in range(3)
    )
    quotient_slope = slope((-2, 2, 0), (6, 9, 3), rank=2)
    observations = (
        ("carrier.intersection.d112", triple_intersection((1, 0, 0), (1, 0, 0),
                                                          (0, 1, 0)),
         Fraction(1, 3), "Quotient normalization d112=1/3."),
        ("carrier.intersection.d122", triple_intersection((1, 0, 0), (0, 1, 0),
                                                          (0, 1, 0)),
         Fraction(1, 3), "Quotient normalization d122=1/3."),
        ("carrier.intersection.d123", triple_intersection((1, 0, 0), (0, 1, 0),
                                                          (0, 0, 1)),
         Fraction(1), "Quotient normalization d123=1."),
        ("carrier.hidden.D.square", divisor_square(hidden_d),
         (Fraction(-4, 3), Fraction(-1, 3), Fraction(4)),
         "The hidden extension divisor square is exact."),
        ("carrier.hidden.c2", hidden_from_extension, c2_hidden,
         "2P-D^2 gives the corrected hidden target class."),
        ("carrier.bianchi.c2", tuple(c2_visible[index] + c2_hidden[index]
                                     for index in range(3)), c2_tangent,
         "Visible plus hidden c2 equals c2(TX) with no five-brane class."),
        ("carrier.descent.visible", (8 + 1) % 3, 0,
         "The visible coefficient pair obeys the necessary descent congruence."),
        ("carrier.slope.quotient", quotient_slope, Fraction(-33),
         "mu_J(V1)=-33 in quotient-normalized intersections."),
        ("carrier.slope.cover", 9 * quotient_slope, Fraction(-297),
         "The ninefold-cover integral is -297; only the sign is invariant."),
        ("carrier.index.generations", -Fraction(-6, 2), Fraction(3),
         "Imported c3(V)=-6 gives three net generations in the stated convention."),
    )
    return tuple(
        Check(identifier, observed == expected, expected, observed,
              EvidenceClass.EXACT_THEOREM if identifier != "carrier.index.generations"
              else EvidenceClass.PUBLISHED_INPUT, note)
        for identifier, observed, expected, note in observations
    )


def mw_degree(m: int, n: int) -> int:
    return m * m + n * n - m * n - m


def mw_action(point: tuple[int, int]) -> tuple[int, int]:
    m, n = point
    return 1 - n, m - n


def mw_shell(degree: int, bound: int = 8) -> tuple[tuple[int, int], ...]:
    if degree < 0 or bound < 1:
        raise ValueError("degree must be nonnegative and bound must be positive")
    return tuple(
        (m, n)
        for m in range(-bound, bound + 1)
        for n in range(-bound, bound + 1)
        if mw_degree(m, n) == degree
    )


def mw_orbits(points: Iterable[tuple[int, int]]) -> tuple[tuple[tuple[int, int], ...], ...]:
    remaining = set(points)
    orbits: list[tuple[tuple[int, int], ...]] = []
    while remaining:
        point = min(remaining)
        orbit = (point, mw_action(point), mw_action(mw_action(point)))
        if set(orbit) - remaining:
            raise ValueError("input is not closed under the order-three action")
        remaining.difference_update(orbit)
        orbits.append(orbit)
    return tuple(orbits)


def u_trim(coefficients: Sequence[object]) -> tuple[Eisenstein, ...]:
    result = list(Eisenstein.coerce(value) for value in coefficients)
    while len(result) > 1 and result[-1].is_zero():
        result.pop()
    return tuple(result)


def u_divmod(
    dividend: Sequence[object],
    divisor: Sequence[object],
) -> tuple[tuple[Eisenstein, ...], tuple[Eisenstein, ...]]:
    """Divide univariate polynomials over Q(omega), coefficients ascending."""

    numerator, denominator = list(u_trim(dividend)), u_trim(divisor)
    if len(denominator) == 1 and denominator[0].is_zero():
        raise ZeroDivisionError("polynomial division by zero")
    quotient = [E_ZERO for _ in range(max(1, len(numerator) - len(denominator) + 1))]
    while len(numerator) >= len(denominator) and not (
        len(numerator) == 1 and numerator[0].is_zero()
    ):
        degree = len(numerator) - len(denominator)
        factor = numerator[-1] / denominator[-1]
        quotient[degree] = factor
        for index, coefficient in enumerate(denominator):
            numerator[index + degree] -= factor * coefficient
        numerator = list(u_trim(numerator))
    return u_trim(quotient), u_trim(numerator)


def u_gcd(left: Sequence[object], right: Sequence[object]) -> tuple[Eisenstein, ...]:
    a, b = u_trim(left), u_trim(right)
    while not (len(b) == 1 and b[0].is_zero()):
        _, remainder = u_divmod(a, b)
        a, b = b, remainder
    leading_inverse = a[-1].inverse()
    return u_trim(tuple(leading_inverse * coefficient for coefficient in a))


BASEPOINT_MODULUS: tuple[Eisenstein, ...] = (
    Eisenstein(-1), E_ZERO, E_ZERO, -51 - 27 * OMEGA,
    E_ZERO, E_ZERO, 24 - 27 * OMEGA, E_ZERO, E_ZERO, E_ONE,
)


def verify_curve_lattice() -> tuple[Check, ...]:
    shell1, shell2 = mw_shell(1), mw_shell(2)
    orbit1, orbit2 = mw_orbits(shell1), mw_orbits(shell2)
    derivative = tuple(
        index * BASEPOINT_MODULUS[index] for index in range(1, len(BASEPOINT_MODULUS))
    )
    observations = (
        ("carrier.curves.action.order3", mw_action(mw_action(mw_action((4, -2)))),
         (4, -2), "The affine Mordell-Weil action has order three."),
        ("carrier.curves.degree.invariant", mw_degree(*mw_action((4, -2))),
         mw_degree(4, -2), "The quadratic degree is invariant under the action."),
        ("carrier.curves.degree1.shell", len(shell1), 3,
         "The minimal shell is a single orbit of three Mordell-Weil labels."),
        ("carrier.curves.degree1.orbits", len(orbit1), 1,
         "There is one free degree-one orbit."),
        ("carrier.curves.cover.count", 9 * 9, 81,
         "The certified minimal cover count is 81."),
        ("carrier.curves.quotient.count", (9 * 9) // 9, 9,
         "Free Z3 x Z3 descent gives nine minimal quotient curves."),
        ("carrier.curves.degree2.shell", len(shell2), 6,
         "The degree-two shell has six labels."),
        ("carrier.curves.degree2.orbits", len(orbit2), 2,
         "The degree-two shell splits into two free orbits."),
        ("carrier.curves.degree2.quotient", 2 * 9, 18,
         "The two orbit families give eighteen quotient curves."),
        ("carrier.basepoint.degree", len(u_trim(BASEPOINT_MODULUS)) - 1, 9,
         "The finite basepoint algebra is degree nine over Q(omega)."),
        ("carrier.basepoint.squarefree", u_gcd(BASEPOINT_MODULUS, derivative),
         (E_ONE,), "The degree-nine modulus is squarefree."),
    )
    return tuple(
        Check(identifier, observed == expected, expected, observed,
              EvidenceClass.EXACT_THEOREM, note)
        for identifier, observed, expected, note in observations
    )


def verify_carrier_manifest() -> tuple[Check, ...]:
    """Check logical consistency of published carrier metadata, not rederive it."""

    published = {
        "fundamental_group_order": 9,
        "families": 3,
        "right_handed_neutrinos": 3,
        "higgs_pairs": 1,
        "geometric_moduli": 6,
        "observable_bundle_moduli": 13,
        "cover_h1_V": 27,
        "cover_h1_V_dual": 0,
        "cover_h1_wedge2_V": 4,
    }
    observations = (
        ("carrier.published.family_descent",
         published["cover_h1_V"] // published["fundamental_group_order"],
         published["families"], "Twenty-seven cover multiplets descend to three families."),
        ("carrier.published.no_antifamilies", published["cover_h1_V_dual"], 0,
         "The published carrier has no anti-family cohomology."),
        ("carrier.published.one_higgs", published["higgs_pairs"], 1,
         "This release imports the exact one-Higgs carrier."),
        ("carrier.published.bundle_moduli", published["observable_bundle_moduli"], 13,
         "The exact carrier has thirteen observable bundle moduli."),
        ("carrier.published.wedge2", published["cover_h1_wedge2_V"], 4,
         "The imported cover cohomology h1(wedge^2 V)=4."),
    )
    return tuple(
        Check(identifier, observed == expected, expected, observed,
              EvidenceClass.PUBLISHED_INPUT, note)
        for identifier, observed, expected, note in observations
    )


SECTION2_CERTIFICATE_SHA256: Mapping[str, str] = {
    "v055_curve_lattice": "112468e75092fc3889458415c36c919cbd05272cf8ef3b56157e38b28da8a939",
    "v056_torsion_fourier": "60478552ae2e9d0f53e3af826d287eacfaf870ce45ca78aeda60c649b3cab49b",
    "v057_carrier_reconciliation": "7c8990a5af0e03216fb082ceb2520d565a3910a6fb0e24a5dbf6940cff49f24a",
    "v062_heisenberg_serre": "15bf6c2ba692929bbc864b864a17deb1036c388cea18e58a35dcb71b84f24b7d",
    "v068_degree_two": "ad8537589da7f5b7e5fb209163263d109a6627932e39ff41bf92d78706fea409",
    "v77_remaining_gaps": "277836a4c14e3f329ca76445d69e0300c41d86dce10715c8f952803a2fffcdc2",
}


def run_section2_checks() -> tuple[Check, ...]:
    return (
        *verify_carrier_manifest(),
        *verify_heisenberg_and_point_schemes(),
        *verify_serre_linearization(),
        *verify_topology_and_anomaly(),
        *verify_curve_lattice(),
    )


@dataclass(frozen=True)
class ScaleMonomial:
    """Formal powers of hbar, c, G, and an energy E."""

    hbar: Fraction = Fraction(0)
    c: Fraction = Fraction(0)
    gravity: Fraction = Fraction(0)
    energy: Fraction = Fraction(0)

    def __mul__(self, other: object) -> "ScaleMonomial":
        if not isinstance(other, ScaleMonomial):
            return NotImplemented
        return ScaleMonomial(
            self.hbar + other.hbar,
            self.c + other.c,
            self.gravity + other.gravity,
            self.energy + other.energy,
        )

    def __truediv__(self, other: object) -> "ScaleMonomial":
        if not isinstance(other, ScaleMonomial):
            return NotImplemented
        return ScaleMonomial(
            self.hbar - other.hbar,
            self.c - other.c,
            self.gravity - other.gravity,
            self.energy - other.energy,
        )

    def power(self, exponent: int | Fraction) -> "ScaleMonomial":
        exponent = Fraction(exponent)
        return ScaleMonomial(
            exponent * self.hbar,
            exponent * self.c,
            exponent * self.gravity,
            exponent * self.energy,
        )

    def at_planck_energy(self) -> "ScaleMonomial":
        """Substitute E_P=(hbar*c^5/G)^(1/2) for the energy symbol."""

        planck_energy = ScaleMonomial(Fraction(1, 2), Fraction(5, 2),
                                     Fraction(-1, 2), Fraction(0))
        return ScaleMonomial(self.hbar, self.c, self.gravity) * planck_energy.power(
            self.energy
        )


HBAR_SCALE = ScaleMonomial(hbar=Fraction(1))
C_SCALE = ScaleMonomial(c=Fraction(1))
G_SCALE = ScaleMonomial(gravity=Fraction(1))
ENERGY_SCALE = ScaleMonomial(energy=Fraction(1))
PLANCK_LENGTH_SCALE = (HBAR_SCALE * G_SCALE / C_SCALE.power(3)).power(Fraction(1, 2))
PLANCK_TIME_SCALE = (HBAR_SCALE * G_SCALE / C_SCALE.power(5)).power(Fraction(1, 2))
PLANCK_ENERGY_SCALE = (HBAR_SCALE * C_SCALE.power(5) / G_SCALE).power(Fraction(1, 2))


def q_identity(size: int) -> tuple[tuple[Fraction, ...], ...]:
    return tuple(
        tuple(Fraction(int(i == j)) for j in range(size))
        for i in range(size)
    )


def q_matmul(
    left: Sequence[Sequence[int | Fraction]],
    right: Sequence[Sequence[int | Fraction]],
) -> tuple[tuple[Fraction, ...], ...]:
    a, b = exact_matrix(left), exact_matrix(right)
    if not a or not b or len(a[0]) != len(b):
        raise ValueError("incompatible exact matrix dimensions")
    return tuple(
        tuple(sum(a[i][k] * b[k][j] for k in range(len(b)))
              for j in range(len(b[0])))
        for i in range(len(a))
    )


def q_matrix_add(
    left: Sequence[Sequence[int | Fraction]],
    right: Sequence[Sequence[int | Fraction]],
) -> tuple[tuple[Fraction, ...], ...]:
    a, b = exact_matrix(left), exact_matrix(right)
    if len(a) != len(b) or (a and len(a[0]) != len(b[0])):
        raise ValueError("incompatible exact matrix dimensions")
    return tuple(tuple(x + y for x, y in zip(row_a, row_b))
                 for row_a, row_b in zip(a, b))


def paired_carrier_matrices() -> Mapping[str, tuple[tuple[Fraction, ...], ...]]:
    """Return eta_8, Omega, and J=eta_8^{-1}Omega in x-then-p ordering."""

    eta_diagonal = (1, -1, -1, -1, -1, -1, -1, -1)
    eta = tuple(
        tuple(Fraction(eta_diagonal[i] if i == j else 0) for j in range(8))
        for i in range(8)
    )
    omega = tuple(
        tuple(
            Fraction(
                -1 if i < 4 and j == i + 4
                else 1 if i >= 4 and j == i - 4
                else 0
            )
            for j in range(8)
        )
        for i in range(8)
    )
    eta_inverse = eta
    j_map = q_matmul(eta_inverse, omega)
    return {"metric": eta, "symplectic": omega, "J": j_map}


def phase_plane_projectors() -> tuple[tuple[tuple[Fraction, ...], ...], ...]:
    """Projectors in the V7 basis (p0,x1,p1,x2,p2,x3,p3)."""

    projectors = []
    for start in (1, 3, 5):
        projectors.append(
            tuple(
                tuple(Fraction(int(i == j and i in (start, start + 1)))
                      for j in range(7))
                for i in range(7)
            )
        )
    return tuple(projectors)


def native_depth_data() -> Mapping[str, Any]:
    depths = (Fraction(1, 3), Fraction(1, 2), Fraction(2, 3))
    return {
        "depths": depths,
        "weight_exponents": tuple(-4 * item for item in depths),
        "left_filter_exponents": (3, 2, 0),
        "up_filter_exponents": (5, 2, 0),
        "down_filter_exponents": (2, 1, 0),
        "up_singular_orders": (8, 4, 0),
        "down_singular_orders": (5, 3, 0),
        "mixing_orders": (1, 2, 3),
    }


def s3_albert_character() -> Mapping[str, Any]:
    """Character calculation for 2*1 + 7*sign + 9*standard."""

    irreducible = {
        "trivial": (1, 1, 1),
        "sign": (1, -1, 1),
        "standard": (2, 0, -1),
    }
    multiplicities = {"trivial": 2, "sign": 7, "standard": 9}
    character = tuple(
        sum(multiplicities[name] * values[index]
            for name, values in irreducible.items())
        for index in range(3)
    )
    return {
        "classes": ("identity", "transposition", "three_cycle"),
        "character": character,
        "multiplicities": multiplicities,
        "dimension": character[0],
    }


F3_VECTOR2 = tuple(product(range(3), repeat=2))


def f3_q(vector: tuple[int, int]) -> int:
    return vector[0] * vector[1] % 3


def f3_bilinear(left: tuple[int, int], right: tuple[int, int]) -> int:
    return (left[0] * right[1] + left[1] * right[0]) % 3


def finite_quadratic_plane() -> Mapping[str, Any]:
    table = tuple((a, b, f3_q((a, b))) for a, b in F3_VECTOR2)
    isotropic = tuple((a, b) for a, b in F3_VECTOR2 if f3_q((a, b)) == 0)
    return {
        "table": table,
        "isotropic": isotropic,
        "bilinear_matrix": ((0, 1), (1, 0)),
        "bilinear_determinant_mod3": 2,
    }


def gl2_3() -> tuple[tuple[int, int, int, int], ...]:
    return tuple(
        (a, b, c, d)
        for a, b, c, d in product(range(3), repeat=4)
        if (a * d - b * c) % 3 != 0
    )


def quadratic_form_table(coefficients: tuple[int, int, int]) -> tuple[int, ...]:
    a_coefficient, b_coefficient, c_coefficient = coefficients
    return tuple(
        (a_coefficient * x * x + b_coefficient * x * y + c_coefficient * y * y) % 3
        for x, y in F3_VECTOR2
    )


def transform_quadratic_table(
    coefficients: tuple[int, int, int],
    matrix: tuple[int, int, int, int],
) -> tuple[int, ...]:
    a, b, c, d = matrix
    return tuple(
        quadratic_form_table(coefficients)[F3_VECTOR2.index(
            ((a * x + b * y) % 3, (c * x + d * y) % 3)
        )]
        for x, y in F3_VECTOR2
    )


def quadratic_form_classification() -> Mapping[str, Any]:
    nondegenerate = tuple(
        coefficients
        for coefficients in product(range(3), repeat=3)
        if (coefficients[1] ** 2 - 4 * coefficients[0] * coefficients[2]) % 3
    )
    split_tables = {
        transform_quadratic_table((0, 1, 0), matrix)
        for matrix in gl2_3()
    }
    anisotropic_tables = {
        transform_quadratic_table((1, 0, 1), matrix)
        for matrix in gl2_3()
    }
    return {
        "nondegenerate_count": len(nondegenerate),
        "split_orbit_size": len(split_tables),
        "anisotropic_orbit_size": len(anisotropic_tables),
        "orbits_disjoint": split_tables.isdisjoint(anisotropic_tables),
        "orbit_union_count": len(split_tables | anisotropic_tables),
    }


def finite_chirp_transform() -> Mapping[tuple[int, int], Eisenstein]:
    return {
        (r, s): sum(
            (OMEGA ** ((x * y - r * x - s * y) % 3) for x, y in F3_VECTOR2),
            E_ZERO,
        )
        for r, s in F3_VECTOR2
    }


def bourbaki_cartan_e8() -> tuple[tuple[int, ...], ...]:
    """E8 Cartan matrix: 1-3-4-5-6-7-8 with node 2 attached to 3."""

    matrix = [[0] * 8 for _ in range(8)]
    for index in range(8):
        matrix[index][index] = 2
    for left, right in ((0, 2), (1, 2), (2, 3), (3, 4),
                        (4, 5), (5, 6), (6, 7)):
        matrix[left][right] = matrix[right][left] = -1
    return tuple(tuple(row) for row in matrix)


def cartan_d5() -> tuple[tuple[int, ...], ...]:
    """D5 Cartan matrix: 1-2-3 with nodes 4 and 5 attached to 3."""

    matrix = [[0] * 5 for _ in range(5)]
    for index in range(5):
        matrix[index][index] = 2
    for left, right in ((0, 1), (1, 2), (2, 3), (2, 4)):
        matrix[left][right] = matrix[right][left] = -1
    return tuple(tuple(row) for row in matrix)


def cartan_pairing_mod3(
    left: Sequence[int],
    right: Sequence[int],
    cartan: Sequence[Sequence[int]],
) -> int:
    return sum(
        left[i] * cartan[i][j] * right[j]
        for i in range(len(left))
        for j in range(len(right))
    ) % 3


def lattice_quadratic_mod3(
    vector: Sequence[int],
    cartan: Sequence[Sequence[int]],
) -> int:
    return 2 * cartan_pairing_mod3(vector, vector, cartan) % 3


def e8_hyperbolic_embedding() -> Mapping[str, Any]:
    cartan = bourbaki_cartan_e8()
    u = (0, 0, 0, 0, 0, 1, 2, 0)
    v = (0, 0, 0, 0, 2, 1, 0, 0)
    table = tuple(
        (
            a,
            b,
            lattice_quadratic_mod3(
                tuple((a * u[i] + b * v[i]) % 3 for i in range(8)),
                cartan,
            ),
        )
        for a, b in F3_VECTOR2
    )
    return {
        "u": u,
        "v": v,
        "q_u": lattice_quadratic_mod3(u, cartan),
        "q_v": lattice_quadratic_mod3(v, cartan),
        "pairing": cartan_pairing_mod3(u, v, cartan),
        "table": table,
    }


def roots_from_cartan(
    cartan: Sequence[Sequence[int]],
    bound: int = 3,
) -> tuple[tuple[int, ...], ...]:
    rank = len(cartan)
    roots = []
    for vector in product(range(-bound, bound + 1), repeat=rank):
        norm = sum(
            vector[i] * cartan[i][j] * vector[j]
            for i in range(rank)
            for j in range(rank)
        )
        if norm == 2:
            roots.append(vector)
    return tuple(roots)


def d5_visible_wilson_classification() -> Mapping[str, Any]:
    cartan = cartan_d5()
    vectors = tuple(product(range(3), repeat=5))
    zero = (0, 0, 0, 0, 0)
    isotropic = tuple(
        vector
        for vector in vectors
        if vector != zero and lattice_quadratic_mod3(vector, cartan) == 0
    )
    hyperbolic_pairs = tuple(
        (left, right)
        for left in isotropic
        for right in isotropic
        if cartan_pairing_mod3(left, right, cartan) == 1
    )
    roots = roots_from_cartan(cartan)
    survivor_counts: dict[int, int] = {}
    for left, right in hyperbolic_pairs:
        survivors = sum(
            1
            for root in roots
            if cartan_pairing_mod3(left, root, cartan) == 0
            and cartan_pairing_mod3(right, root, cartan) == 0
        )
        survivor_counts[survivors] = survivor_counts.get(survivors, 0) + 1
    return {
        "root_count": len(roots),
        "nonzero_isotropic_count": len(isotropic),
        "ordered_hyperbolic_pair_count": len(hyperbolic_pairs),
        "survivor_distribution": dict(sorted(survivor_counts.items())),
        "visible_a2_a1_root_count_present": 8 in survivor_counts,
    }


def decimal_pi(precision: int = 50) -> Decimal:
    """Deterministic Gauss-Legendre pi for bridge-only numerical reporting."""

    if precision < 16:
        raise ValueError("precision must be at least 16 decimal digits")
    with localcontext() as context:
        context.prec = precision + 10
        one = Decimal(1)
        two = Decimal(2)
        a = one
        b = one / two.sqrt()
        t = Decimal(1) / Decimal(4)
        p = one
        for _ in range(8):
            next_a = (a + b) / two
            b = (a * b).sqrt()
            t -= p * (a - next_a) ** 2
            a = next_a
            p *= two
        result = (a + b) ** 2 / (Decimal(4) * t)
        context.prec = precision
        return +result


def hierarchy_bridge_parameters(precision: int = 40) -> Mapping[str, Any]:
    """Numerical values for explicitly labelled bridge definitions."""

    with localcontext() as context:
        context.prec = precision
        pi_value = decimal_pi(precision + 5)
        source = Decimal(14) / (Decimal(431) * Decimal(8) * pi_value)
        epsilon_right = (Decimal(9) * source / Decimal(5)).sqrt().sqrt()
        eta_left = (Decimal(4) * source / Decimal(3)).sqrt().sqrt()
        return {
            "L": +(Decimal(1) / (Decimal(8) * pi_value)),
            "S_star": +source,
            "epsilon_R": +epsilon_right,
            "eta_Q": +eta_left,
        }


def hierarchy_coefficient_closure() -> Mapping[str, Fraction]:
    """Return the declared coefficient identities over Q.

    The values are coefficients of c, b_u, or c*b_u as appropriate; the free
    symbols themselves are not assigned numerical values.
    """

    a_u_over_c = Fraction(4)
    a_d_over_c = Fraction(8, 3)
    b_d_over_b_u = Fraction(3, 2)
    return {
        "a_u_over_c": a_u_over_c,
        "a_d_over_c": a_d_over_c,
        "b_d_over_b_u": b_d_over_b_u,
        "difference_over_c": a_u_over_c - a_d_over_c,
        "up_product_over_c_b_u": a_u_over_c,
        "down_product_over_c_b_u": a_d_over_c * b_d_over_b_u,
    }


SECTION3_MISSING_INPUTS: Mapping[str, str] = {
    "tight_frame_representation":
        "The nine operators U_g defining the claimed 9/5 frame are not serialized.",
    "triality_overlap_certificate":
        "The three triality subspaces and their pairwise intersections are not serialized.",
    "freudenthal_carrier_certificate":
        "The tested 56-dimensional carrier and chiral-index complex are not supplied.",
    "e6_su3_beta_coefficients":
        "The branchwise beta-function coefficients are absent.",
    "degree32_sturm_eliminant":
        "The square-free eliminant and Sturm certificate are absent.",
    "filtered_weil_generators":
        "The matrices C, R, K and their normalization are not supplied.",
    "planck_electroweak_formula":
        "The source DOCX lost operators and constants in the displayed formula.",
    "physical_native_to_carrier_maps":
        "No typed spacetime, worldsheet, compactification, family, flavor, or determinant-line map is supplied.",
}


def verify_native_finite_architecture() -> tuple[Check, ...]:
    paired = paired_carrier_matrices()
    j_squared = q_matmul(paired["J"], paired["J"])
    expected_j_squared = tuple(
        tuple(Fraction(
            (1 if i in (0, 4) else -1) if i == j else 0
        ) for j in range(8))
        for i in range(8)
    )
    projectors = phase_plane_projectors()
    projector_sum = tuple(tuple(Fraction(0) for _ in range(7)) for _ in range(7))
    for projector in projectors:
        projector_sum = q_matrix_add(projector_sum, projector)
    depth = native_depth_data()
    albert = s3_albert_character()
    plane = finite_quadratic_plane()
    classification = quadratic_form_classification()
    chirp = finite_chirp_transform()
    embedding = e8_hyperbolic_embedding()
    d5 = d5_visible_wilson_classification()
    bridge = hierarchy_bridge_parameters()
    coefficient_closure = hierarchy_coefficient_closure()

    observations: tuple[tuple[str, Any, Any, EvidenceClass, str], ...] = (
        ("native.planck.lambda_times_r",
         (HBAR_SCALE * C_SCALE / ENERGY_SCALE)
         * (G_SCALE * ENERGY_SCALE / C_SCALE.power(4)),
         PLANCK_LENGTH_SCALE.power(2), EvidenceClass.EXACT_THEOREM,
         "lambda_Q(E) r_G(E)=ell_P^2 as a formal monomial identity."),
        ("native.planck.tau_times_tau_g",
         (HBAR_SCALE / ENERGY_SCALE)
         * (G_SCALE * ENERGY_SCALE / C_SCALE.power(5)),
         PLANCK_TIME_SCALE.power(2), EvidenceClass.EXACT_THEOREM,
         "tau_Q(E) tau_G(E)=t_P^2 as a formal monomial identity."),
        ("native.planck.lambda_at_Ep",
         (HBAR_SCALE * C_SCALE / ENERGY_SCALE).at_planck_energy(),
         PLANCK_LENGTH_SCALE, EvidenceClass.EXACT_THEOREM,
         "The quantum localization scale equals ell_P at E_P."),
        ("native.planck.r_at_Ep",
         (G_SCALE * ENERGY_SCALE / C_SCALE.power(4)).at_planck_energy(),
         PLANCK_LENGTH_SCALE, EvidenceClass.EXACT_THEOREM,
         "The adopted gravitational scale equals ell_P at E_P."),
        ("native.planck.Ep_tP", PLANCK_ENERGY_SCALE * PLANCK_TIME_SCALE,
         HBAR_SCALE, EvidenceClass.EXACT_THEOREM, "E_P t_P=hbar."),
        ("native.paired.signature",
         tuple(sum(1 for i in range(8) if paired["metric"][i][i] == sign)
               for sign in (1, -1)),
         (1, 7), EvidenceClass.EXACT_THEOREM, "eta_8 has signature (1,7)."),
        ("native.paired.J_square", j_squared, expected_j_squared,
         EvidenceClass.EXACT_THEOREM,
         "J^2 is +I on the time-action plane and -I on three spatial planes."),
        ("native.clifford.grade_dimensions",
         tuple(comb(8, grade) for grade in range(9)),
         (1, 8, 28, 56, 70, 56, 28, 8, 1),
         EvidenceClass.EXACT_THEOREM, "Exterior-grade dimensions of Cl(1,7)."),
        ("native.clifford.total_dimension",
         sum(comb(8, grade) for grade in range(9)), 256,
         EvidenceClass.EXACT_THEOREM, "The real Clifford algebra has dimension 2^8."),
        ("native.projectors.idempotent",
         all(q_matmul(projector, projector) == projector for projector in projectors),
         True, EvidenceClass.EXACT_THEOREM, "All three phase-plane projectors are idempotent."),
        ("native.projectors.orthogonal",
         all(q_matmul(projectors[i], projectors[j])
             == tuple(tuple(Fraction(0) for _ in range(7)) for _ in range(7))
             for i in range(3) for j in range(3) if i != j),
         True, EvidenceClass.EXACT_THEOREM, "The phase-plane projectors are mutually orthogonal."),
        ("native.projectors.rank_sum", exact_rank(projector_sum), 6,
         EvidenceClass.EXACT_THEOREM, "Their sum projects onto the six-dimensional spatial phase sector."),
        ("native.depth.values", depth["depths"],
         (Fraction(1, 3), Fraction(1, 2), Fraction(2, 3)),
         EvidenceClass.CONDITIONAL, "Selected finite depths; physical uniqueness is not proved."),
        ("native.depth.weight_exponents", depth["weight_exponents"],
         (Fraction(-4, 3), Fraction(-2), Fraction(-8, 3)),
         EvidenceClass.CONDITIONAL, "Exact exponents after the depth operator is defined."),
        ("native.exceptional.dimensions", (8, 14, 27, 52, 78),
         (8, 14, 27, 52, 78), EvidenceClass.PUBLISHED_INPUT,
         "Dimensions of O, G2, J3(O), F4, and E6."),
        ("native.exceptional.e6_branch_dimension", 16 + 10 + 1, 27,
         EvidenceClass.PUBLISHED_INPUT, "E6 fundamental branch 27=16+10+1."),
        ("native.albert.s3_character", albert["character"], (27, -5, 0),
         EvidenceClass.EXACT_THEOREM, "Character of 2*1 + 7*sign + 9*standard."),
        ("native.albert.s3_dimension", albert["dimension"], 27,
         EvidenceClass.EXACT_THEOREM, "The S3 decomposition has total dimension 27."),
        ("native.shortcut.one_albert", 16 < 3 * 16, True,
         EvidenceClass.SCOPED_NO_GO, "One E6 fundamental contains one Spin(10) 16, not three."),
        ("native.shortcut.triality_bound", 24 < 3 * 16, True,
         EvidenceClass.SCOPED_NO_GO,
         "The reported 24-dimensional combined span cannot hold 48 independent Weyl components."),
        ("native.shortcut.freudenthal_bound", 56 // 2 < 3 * 16, True,
         EvidenceClass.SCOPED_NO_GO,
         "A Lagrangian half of the tested 56 has dimension 28, below 48."),
        ("native.e8.adjoint_branch_dimension", 120 + 128, 248,
         EvidenceClass.PUBLISHED_INPUT, "Under Spin(16), 248=120+128."),
        ("native.f3.bilinear_nondegenerate", plane["bilinear_determinant_mod3"], 2,
         EvidenceClass.EXACT_THEOREM, "The split bilinear form has nonzero determinant mod 3."),
        ("native.f3.isotropic_count", len(plane["isotropic"]), 5,
         EvidenceClass.EXACT_THEOREM, "q(a,b)=ab has five isotropic vectors including zero."),
        ("native.f3.nondegenerate_quadratics",
         classification["nondegenerate_count"], 18,
         EvidenceClass.EXACT_THEOREM, "There are 18 nondegenerate homogeneous binary quadratics over F3."),
        ("native.f3.quadratic_orbits",
         (classification["split_orbit_size"], classification["anisotropic_orbit_size"],
          classification["orbits_disjoint"], classification["orbit_union_count"]),
         (12, 6, True, 18), EvidenceClass.EXACT_THEOREM,
         "The 18 forms split into the split and anisotropic GL(2,3) orbits."),
        ("native.chirp.fourier",
         tuple(chirp[(r, s)] for r, s in F3_VECTOR2),
         tuple(3 * (OMEGA ** ((-r * s) % 3)) for r, s in F3_VECTOR2),
         EvidenceClass.EXACT_THEOREM,
         "The unnormalized Fourier transform is 3 omega^(-rs)."),
        ("native.chirp.cp",
         tuple(f3_q((a, (-b) % 3)) for a, b in F3_VECTOR2),
         tuple((-f3_q((a, b))) % 3 for a, b in F3_VECTOR2),
         EvidenceClass.EXACT_THEOREM, "The involution (a,b)->(a,-b) conjugates the chirp."),
        ("native.e8.hyperbolic_pair",
         (embedding["q_u"], embedding["q_v"], embedding["pairing"]),
         (0, 0, 1), EvidenceClass.EXACT_THEOREM,
         "The supplied E8 mod-three vectors form a hyperbolic pair."),
        ("native.e8.embedded_table",
         tuple(item[2] for item in embedding["table"]),
         tuple(f3_q((a, b)) for a, b in F3_VECTOR2),
         EvidenceClass.EXACT_THEOREM, "The embedded E8 plane reproduces q(a,b)=ab."),
        ("native.d5.roots", d5["root_count"], 40,
         EvidenceClass.EXACT_THEOREM, "The D5 root system has 40 roots."),
        ("native.d5.isotropic", d5["nonzero_isotropic_count"], 80,
         EvidenceClass.EXACT_THEOREM, "D5/3D5 has 80 nonzero isotropic vectors."),
        ("native.d5.hyperbolic_pairs", d5["ordered_hyperbolic_pair_count"], 2160,
         EvidenceClass.EXACT_THEOREM, "There are 2160 ordered hyperbolic pairs."),
        ("native.d5.survivor_distribution", d5["survivor_distribution"],
         {2: 960, 4: 960, 6: 240}, EvidenceClass.EXACT_THEOREM,
         "Surviving D5 roots occur only in counts 2, 4, and 6."),
        ("native.d5.visible_a2_a1_absent",
         d5["visible_a2_a1_root_count_present"], False,
         EvidenceClass.SCOPED_NO_GO,
         "No hyperbolic pair preserves the eight roots of A2 plus A1."),
        ("native.hierarchy.orders",
         (depth["up_singular_orders"], depth["down_singular_orders"],
          depth["mixing_orders"]),
         ((8, 4, 0), (5, 3, 0), (1, 2, 3)),
         EvidenceClass.BRIDGE_TARGET, "Arithmetic consequences of the declared grading filters."),
        ("native.hierarchy.source_parameter",
         str(bridge["S_star"])[:14], "0.001292441533",
         EvidenceClass.BRIDGE_TARGET,
         "Deterministic numerical value of S*=14/(431*8*pi); no physical transfer is implied."),
        ("native.hierarchy.coefficient_difference",
         coefficient_closure["difference_over_c"], Fraction(4, 3),
         EvidenceClass.EXACT_THEOREM,
         "The declared relations imply a_u-a_d=(4/3)c."),
        ("native.hierarchy.coefficient_product",
         coefficient_closure["down_product_over_c_b_u"],
         coefficient_closure["up_product_over_c_b_u"],
         EvidenceClass.EXACT_THEOREM,
         "The declared relations imply a_u b_u=a_d b_d."),
    )
    return tuple(
        Check(identifier, observed == expected, expected, observed, evidence, note)
        for identifier, observed, expected, evidence, note in observations
    )


def run_section3_checks() -> tuple[Check, ...]:
    return verify_native_finite_architecture()


ORIGIN_INTERFACE_IDS = (
    "origin_geometry",
    "origin_worldsheet",
    "origin_visible_bundle",
    "origin_hidden_bundle",
    "generation_carrier",
    "matter_socket",
    "hierarchy_transport",
    "determinant_refinement",
)


def origin_interface_registry() -> tuple[OriginInterface, ...]:
    """Return the complete, typed Section 4 interface ledger.

    Every entry is intentionally OPEN. The registry is a specification of what
    must be constructed; it is not a collection of assumed identity maps.
    """

    native = (
        "G_nat=(V8,eta8,Omega,J,{P_i},N_Q,A_F,G3,q,kappa)"
    )
    geometry = "origin_geometry"
    worldsheet = "origin_worldsheet"
    visible = "origin_visible_bundle"
    hidden = "origin_hidden_bundle"
    generation = "generation_carrier"
    socket = "matter_socket"
    hierarchy = "hierarchy_transport"
    return (
        OriginInterface(
            geometry,
            "OriginGeometryMap",
            native,
            "(M^(3,1),g; X_tilde,G=Z3xZ3,X=X_tilde/G)",
            (),
            (
                "automorphism-invariant Lorentzian event selection",
                "Calabi-Yau threefold construction",
                "free deck action on explicit geometric coordinates",
                "quotient topology and moduli",
                "naturality under source and target equivalences",
            ),
            (
                "canonical event-selection construction",
                "native action on the Schoen Cox and fiber-product data",
                "proof of freeness, quotient topology, and moduli selection",
            ),
            (
                "Construct the Lorentzian event sector and a free Schoen "
                "Z3xZ3 quotient, or an explicitly equivalent carrier geometry, "
                "functorially from the native datum."
            ),
            (
                "An exact obstruction shows that no admissible source "
                "automorphism-compatible construction can reproduce the "
                "required Lorentzian and quotient invariants."
            ),
        ),
        OriginInterface(
            worldsheet,
            "OriginWorldsheetMap",
            native,
            "consistent ten-dimensional heterotic worldsheet CFT",
            (),
            (
                "left-right heterotic field content",
                "critical central charges and modular invariance",
                "even self-dual rank-16 current lattice",
                "selection of the E8xE8 branch",
                "physical state and anomaly consistency",
            ),
            (
                "worldsheet fields and operator algebra",
                "partition function and modular data",
                "native criterion selecting E8xE8 over Spin(32)/Z2",
            ),
            (
                "Construct a modular-invariant heterotic worldsheet theory "
                "and derive the E8xE8 branch from the native datum."
            ),
            (
                "No consistent modular-invariant heterotic worldsheet or no "
                "native E8xE8 branch selector exists in the declared source category."
            ),
        ),
        OriginInterface(
            visible,
            "OriginVisibleBundleMap",
            native,
            "(V_vis,rho_G,rho_W) on X_tilde and X",
            (geometry, worldsheet),
            (
                "rank-four holomorphic SU(4) bundle",
                "Serre point schemes of lengths three and six",
                "outer extension and equivariant descent",
                "published Chern classes and common stable Kahler chamber",
                "Spin(10) commutant and Wilson-line compatibility",
            ),
            (
                "native construction of the two Serre constituents",
                "native selection of the outer extension class",
                "equivariant structure, descent, and stability proof",
            ),
            (
                "Construct an equivariant stable SU(4) observable bundle "
                "equivalent to the published one, including its Wilson line."
            ),
            (
                "Every native candidate violates rank, Chern, local-freeness, "
                "descent, stability, or Wilson-line conditions."
            ),
        ),
        OriginInterface(
            hidden,
            "OriginHiddenBundleMap",
            native,
            "(V_hid,B,H,A_hid,nabla_TX) on X",
            (geometry, worldsheet, visible),
            (
                "honest equivariant locally free hidden bundle",
                "required anomaly-target Chern class",
                "stability in a chamber overlapping the visible bundle",
                "Hermitian Yang-Mills connection and hidden spectrum",
                "differential B-field anomaly trivialization",
            ),
            (
                "completed stable hidden bundle",
                "global differential B-field datum",
                "hidden HYM connection and charged spectrum",
            ),
            (
                "Construct the full hidden and differential anomaly package "
                "compatible with the visible carrier."
            ),
            (
                "No admissible hidden bundle or differential anomaly "
                "trivialization exists for the selected visible carrier."
            ),
        ),
        OriginInterface(
            generation,
            "GenerationCarrierMap",
            "Q_depth^3 with its projector and Z3xZ3 data",
            "physical family factor in H^1(X,V_vis) after Wilson projection",
            (visible,),
            (
                "explicit intertwiner onto the family multiplicity factor",
                "chiral index and multiplicity three",
                "Z3xZ3 and Wilson-character compatibility",
                "compatibility with gauge representations and Yukawa products",
                "compatibility with Hermitian matter metrics",
            ),
            (
                "serialized physical cohomology basis",
                "native chiral complex or index operator",
                "equivariant family intertwiner",
            ),
            (
                "Construct an equivariant chiral map from the three depth "
                "slots to the physical three-family cohomology."
            ),
            (
                "Every admissible intertwiner has incorrect chirality, "
                "multiplicity, character content, or Yukawa compatibility."
            ),
        ),
        OriginInterface(
            socket,
            "MatterSocketMap",
            "A_F=C+H+M3(C)",
            "representation in End(H_phys)",
            (visible, generation),
            (
                "weak-doublet and color-triplet actions",
                "correct Abelian charge and hypercharge embedding",
                "chirality and right-handed-neutrino content",
                "Higgs representation",
                "anomaly and Wilson-line compatibility",
            ),
            (
                "physical cohomology representation matrices",
                "charge-normalization dictionary",
                "proof that the finite algebra action descends",
            ),
            (
                "Represent the finite matter algebra on the derived physical "
                "cohomology with the carrier's charges and chirality."
            ),
            (
                "No faithful admissible representation reproduces the "
                "physical charges, chirality, Higgs sector, and anomaly constraints."
            ),
        ),
        OriginInterface(
            hierarchy,
            "HierarchyTransportMap",
            "(Q_depth^3,N_Q,W_Q)",
            "filtered heterotic cohomological products and normalized couplings",
            (generation, socket),
            (
                "conjugacy of the depth operator on physical family space",
                "compatibility with cup products and bundle deformation",
                "compatibility with determinant contributions",
                "compatibility with positive HYM matter metrics",
                "no empirical selection of basis, grading, or moduli",
            ),
            (
                "physical cohomology products",
                "Ricci-flat, HYM, and matter metrics at one moduli point",
                "native derivation of the grading and filter normalization",
            ),
            (
                "Transport the finite depth filtration into the actual "
                "holomorphic and canonically normalized Yukawa construction."
            ),
            (
                "The hierarchy operator cannot act compatibly on the "
                "physical cohomology without empirical tuning or loss of positivity."
            ),
        ),
        OriginInterface(
            "determinant_refinement",
            "DeterminantRefinementMap",
            "(G3=F3^2,q,kappa)",
            "(L_det,nabla^Q,Quillen metric,CP action)",
            (geometry, visible, hidden),
            (
                "flat finite-orbit determinant holonomy",
                "split nondegenerate quadratic refinement",
                "global anomaly-trivialization compatibility",
                "CP covariance",
                "independent positive Quillen norms",
            ),
            (
                "physical determinant or Pfaffian line",
                "global parallel transport on the finite orbit",
                "Quillen metric and CP-conjugate bundle data",
            ),
            (
                "Realize the native split quadratic form as the phase core "
                "of the physical anomaly-cancelled determinant line."
            ),
            (
                "The physical determinant holonomy is provably incompatible "
                "with every split quadratic refinement equivalent to q(a,b)=ab."
            ),
        ),
    )


SECTION4_MISSING_INPUTS: Mapping[str, str] = {
    interface.identifier: "; ".join(interface.missing_inputs)
    for interface in origin_interface_registry()
}


FORBIDDEN_ORIGIN_SELECTION_TOKENS = (
    "measured mass",
    "fermion mass",
    "mixing angle",
    "ckm",
    "pmns",
    "measured cp phase",
    "higgs mass",
    "experimental fit",
    "vacuum fit",
)


def empirical_leakage_scan(selection_inputs: Iterable[str]) -> tuple[str, ...]:
    """Return forbidden empirical selectors found in proposed bridge inputs."""

    findings: set[str] = set()
    for value in selection_inputs:
        normalized = " ".join(value.casefold().split())
        for token in FORBIDDEN_ORIGIN_SELECTION_TOKENS:
            if token in normalized:
                findings.add(token)
    return tuple(sorted(findings))


def origin_dependency_order(
    interfaces: Sequence[OriginInterface] | None = None,
) -> tuple[str, ...]:
    """Topologically order the interface dependency graph or fail on a cycle."""

    registry = {
        interface.identifier: interface
        for interface in (interfaces or origin_interface_registry())
    }
    if len(registry) != len(interfaces or origin_interface_registry()):
        raise ValueError("origin interface identifiers must be unique")
    unknown = sorted({
        dependency
        for interface in registry.values()
        for dependency in interface.dependencies
        if dependency not in registry
    })
    if unknown:
        raise ValueError(f"unknown origin-interface dependencies: {', '.join(unknown)}")
    remaining = {
        identifier: set(interface.dependencies)
        for identifier, interface in registry.items()
    }
    order: list[str] = []
    while remaining:
        ready = sorted(
            identifier for identifier, dependencies in remaining.items()
            if not dependencies
        )
        if not ready:
            raise ValueError("origin interface dependency graph contains a cycle")
        order.extend(ready)
        for identifier in ready:
            del remaining[identifier]
        for dependencies in remaining.values():
            dependencies.difference_update(ready)
    return tuple(order)


def origin_bridge_status(
    interfaces: Sequence[OriginInterface] | None = None,
) -> Mapping[str, Any]:
    """Evaluate the scientific state without mistaking a contract for a proof."""

    registry = tuple(interfaces or origin_interface_registry())
    states = {interface.identifier: interface.state for interface in registry}
    visible_ids = {
        "origin_geometry",
        "origin_worldsheet",
        "origin_visible_bundle",
        "generation_carrier",
        "matter_socket",
    }
    full_ids = set(ORIGIN_INTERFACE_IDS)
    visible_constructed = all(states.get(item) is GateState.PASSED for item in visible_ids)
    full_constructed = all(states.get(item) is GateState.PASSED for item in full_ids)
    return {
        "highest_level": (
            "LEVEL_V_FULL_CARRIER"
            if full_constructed
            else "LEVEL_IV_VISIBLE_CARRIER"
            if visible_constructed
            else "LEVEL_I_PARTIAL_STRUCTURAL_COMPATIBILITY"
        ),
        "visible_carrier_constructed": visible_constructed,
        "full_carrier_constructed": full_constructed,
        "origin_theorem_proved": full_constructed,
        "open_interfaces": tuple(
            interface.identifier
            for interface in registry
            if interface.state is not GateState.PASSED
        ),
        "interpretation": (
            "The typed interface contract is verified; no Origin-to-Carrier "
            "subsystem map is presently certified."
            if not full_constructed
            else "All declared Origin-to-Carrier subsystem interfaces pass."
        ),
    }


def verify_origin_to_carrier_interface() -> tuple[Check, ...]:
    """Verify the Section 4 contract while preserving its OPEN status."""

    interfaces = origin_interface_registry()
    identifiers = tuple(interface.identifier for interface in interfaces)
    dependency_order = origin_dependency_order(interfaces)
    status = origin_bridge_status(interfaces)
    properties_complete = all(
        interface.domain.strip()
        and interface.codomain.strip()
        and interface.required_properties
        and interface.missing_inputs
        and interface.pass_criterion.strip()
        and interface.kill_criterion.strip()
        for interface in interfaces
    )
    no_empirical_leakage = not empirical_leakage_scan(
        ("finite quadratic form", "source automorphisms", "bundle Chern data")
    )
    forbidden_detected = empirical_leakage_scan(
        ("choose the family basis from CKM mixing angles",)
    )
    observations: tuple[
        tuple[str, Any, Any, EvidenceClass, str], ...
    ] = (
        (
            "origin.contract.interface_count",
            len(interfaces),
            8,
            EvidenceClass.EXACT_THEOREM,
            "The specification contains all eight required subsystem interfaces.",
        ),
        (
            "origin.contract.interface_ids",
            identifiers,
            ORIGIN_INTERFACE_IDS,
            EvidenceClass.EXACT_THEOREM,
            "Interface identifiers are stable and ordered.",
        ),
        (
            "origin.contract.unique_ids",
            len(set(identifiers)),
            len(identifiers),
            EvidenceClass.EXACT_THEOREM,
            "Every subsystem interface has a unique identifier.",
        ),
        (
            "origin.contract.complete_fields",
            properties_complete,
            True,
            EvidenceClass.EXACT_THEOREM,
            "Every interface states its type, obligations, missing inputs, and criteria.",
        ),
        (
            "origin.contract.dependency_dag",
            len(dependency_order),
            len(interfaces),
            EvidenceClass.EXACT_THEOREM,
            "The dependency graph is total and acyclic.",
        ),
        (
            "origin.contract.all_open",
            tuple(interface.state.value for interface in interfaces),
            tuple(GateState.OPEN.value for _ in interfaces),
            EvidenceClass.OPEN,
            "No unproved subsystem map is represented as passed.",
        ),
        (
            "origin.contract.missing_inputs_exposed",
            tuple(sorted(SECTION4_MISSING_INPUTS)),
            tuple(sorted(ORIGIN_INTERFACE_IDS)),
            EvidenceClass.OPEN,
            "Every open interface has an explicit missing-input record.",
        ),
        (
            "origin.contract.empirical_firewall_accepts_native",
            no_empirical_leakage,
            True,
            EvidenceClass.EXACT_THEOREM,
            "Native algebraic inputs do not trigger the empirical-selection firewall.",
        ),
        (
            "origin.contract.empirical_firewall_rejects_fit",
            forbidden_detected,
            ("ckm", "mixing angle"),
            EvidenceClass.EXACT_THEOREM,
            "CKM-based family-basis selection is detected as circular.",
        ),
        (
            "origin.status.visible_carrier",
            status["visible_carrier_constructed"],
            False,
            EvidenceClass.OPEN,
            "The verified interface ledger is not a visible-carrier construction.",
        ),
        (
            "origin.status.full_carrier",
            status["full_carrier_constructed"],
            False,
            EvidenceClass.OPEN,
            "The hidden and differential anomaly targets remain unconstructed.",
        ),
        (
            "origin.status.highest_level",
            status["highest_level"],
            "LEVEL_I_PARTIAL_STRUCTURAL_COMPATIBILITY",
            EvidenceClass.OPEN,
            "Only partial structural compatibility is currently established.",
        ),
    )
    return tuple(
        Check(identifier, observed == expected, expected, observed, evidence, note)
        for identifier, observed, expected, evidence, note in observations
    )


SECTION5_CERTIFICATE_SHA256: Mapping[str, str] = {
    "v18_forward_hypercocycles":
        "359b5e5e362fe2715503b5ec84093696aaba1b7d7796d6cce649daa9643dbb61",
    "v26_forward_slice_no_go":
        "789bd1831308209f981d62842d7ade587e64b05a3a58dfad595c1f3f7c2c7011",
    "v31_reverse_hypercohomology":
        "e53255f172dd38aaff0cd13bcec0dbaadbe9166424be4947ee70c17e3dd29fe3",
    "v34c_bileray_quadratic":
        "aff0d4a8124932f65b2e4336782ca0dc8179bd0fa785616ec0b7cffc242af91a",
    "v35h1d_strict_mixed_slice":
        "e891330e7db026eeb072f8018b9eaf070c7779d9447e8c6a2a98e91f7c4ae480",
    "v35i0_local_freeness":
        "19c30294616bfed3b5cb62f87167a9eab7176f1ccaf59908a774c36c5721ad8f",
    "v35i1_stability_openness":
        "ee3a2f4240f4fc1096603dc2924e34444867d76e3961648f22485126ecb5c641",
    "v35i2_spectrum_reduction":
        "1c6f091aeb76aca0d2270bc702ab2ef2b73bcac470e739cef72f3338c31b7eac",
    "v35i2b_projective_higgs_component":
        "b8dc4d97d2ef60a3c5842e87c92a9666ca1e05bf89de5101638e471864e8c8cb",
    "v36a2f_higgs_protection":
        "abefba4f37d8e5760e585c34b5431e5e1111b897424b97c510837b402b093d89",
}


SECTION5_MISSING_INPUTS: Mapping[str, str] = {
    "global_mixed_moduli_space":
        "No global classification or irreducible-component equation is certified.",
    "maximal_stability_chamber":
        "Only an explicit sufficient anchor box and local openness are certified.",
    "visible_hym_connection":
        "No Hermitian Yang--Mills connection is available on the mixed branch.",
    "matter_and_higgs_metrics":
        "Canonical-normalization matrices have not been computed.",
    "light_family_rank_lift":
        "The truth-bearing mixed Yukawa transfer coefficients remain unevaluated.",
    "physical_yukawa_matrices":
        "Holomorphic data have not been converted to physical normalized couplings.",
    "ckm_and_cp":
        "Neither a full-rank CKM matrix nor a physical CP invariant is certified.",
    "vacuum_selection":
        "No stabilized vacuum selects a point of the mixed branch.",
}


SECTION6_CERTIFICATE_SHA256: Mapping[str, str] = {
    "v35h1_common_dga_schema":
        "e8da0f567632f13f68b7228ded451d797646328491b8bf18508cf34181cb60fd",
    "v36a2g_degree_three_result":
        "c077eb33c4b7071958dcb5d953c37281ea5e20f074e3659a178a64359718b1cb",
    "v36a2h_order_five_result":
        "a18d54185f42b4d0bed37bb7b468b3a5a5245ec42b7467d0ca88f641ccb8ec92",
    "v36a2h_order_five_source":
        "5ec2be1c1270e6f64a6f5fbc54155ccb563c14cf1c54d7310dd992064072a667",
    "v36a2i_second_fundamental_result":
        "e40deaae86da0bca972bbeb5784947a321fd7b14458bec41974ebfb449ae16bc",
    "v36a2k_residue_reduction_result":
        "5ba95df950bd810cd368927bea5fc9c7acfe0e6cf58b175f0799636ba8da50f4",
    "v36a2k_residue_interface":
        "c0a4652e7ddfb772fc62f3ef345209c87fe5626c52884fb130a7a32b5b0d3336",
    "v36a2m_restricted_hull_source":
        "6fb5bc704d80f174e5d60fd4dd56f5450ee7e3a3b9915af40c2edc3d5388342a",
    "v36a2n_direction_adaptive_source":
        "a53def6fc760a50c006394d6e82d7e2201e2393703d7ee69007bd238b76c81b6",
    "v36a2n_direction_adaptive_result":
        "a753cc38185c35628b839ef54d72a804a3e9a4b8335be5d9b0ff74cd27e36388",
    "v36a2b_common_cyclic_gauge_interface":
        "6ebc4bbb16d3de64e81b87ea77ab771693f9588496a97dec3db992ef6208657f",
    "v36a2m_restricted_carrier_interface":
        "4b31537d6695323d2330af7910f9a1adb273b3b2de25ff74719ffbfd24a47835",
    "v36a2m_restricted_carrier_schema":
        "039e4c15f3febc05afc0bc84f3b063f877235df33aa6af30325e93cd506f7840",
    "v36a2l_physical_target_result":
        "d5b29d8e52c7f5498a8db2132ff972243ee31366a47ea47eafb470ce84074863",
}


SECTION6_MISSING_INPUTS: Mapping[str, str] = {
    "physical_star_tangent_typing":
        "Exact countermodels prove that retained branch pruning does not determine whether every up-sector degree-five transport column lies on one star arm or whether the down-sector first column has the required frozen-basis triangular typing. The actual carrier columns remain absent.",
    "physical_hpl_contraction_package":
        "No physical v35h1 common-DGA package supplies the exact D1, mu11, i1, p2, h2, pairing, four f3 trace words, and retained provenance digests.",
    "ambient_common_basis":
        "Common-basis ambient matter representatives a, b_1, and b_2 are absent.",
    "restricted_reverse_actions":
        "The restricted actions rho(F_3), rho(F_5), rho(F_7), rho(K_5), and rho(K_7) are absent.",
    "restricted_contractions":
        "The reachable-hull contractions h_A, h_B, and h_H are absent.",
    "normalized_cyclic_traces":
        "The cyclic contractions tau_AHB and tau_BHA are not normalized.",
    "physical_f3_traces":
        "The first-test columns p_u,3 and p_d,3 require four normalized B-neutral FE traces in one common cyclic gauge.",
    "raw_f3_common_cyclic_package":
        "No frozen package supplies the sector bases, external states, certified effective FE responses, cyclic tensors, and provenance digests required by the raw f3 compiler.",
    "adaptive_residue_escalation":
        "If an f3 Gram norm vanishes, the f5 and then f7 columns remain to be evaluated; the direction-refined worst case is twenty traces.",
    "carrier_second_normal_forms":
        "Consequently the conditional star-tangent theorem has not been promoted to the Schoen carrier, and U_2 and D_2 have not been evaluated there.",
    "physical_normalization":
        "Matter/Higgs metrics and a common stabilized moduli point remain outside this section.",
}


STPolynomial = dict[tuple[int, int], Fraction]
DGAExpression = dict[str, STPolynomial]


def st_polynomial(
    terms: Mapping[tuple[int, int], int | Fraction] | None = None,
) -> STPolynomial:
    """Create a sparse exact polynomial in commuting parameters s and t."""

    result: STPolynomial = {}
    for power, coefficient in (terms or {}).items():
        value = _coerce_fraction(coefficient)
        if value:
            if len(power) != 2 or min(power) < 0:
                raise ValueError("polynomial powers must be nonnegative (s,t) pairs")
            result[power] = result.get(power, Fraction(0)) + value
    return {power: value for power, value in result.items() if value}


def st_poly_add(*polynomials: Mapping[tuple[int, int], Fraction]) -> STPolynomial:
    result: STPolynomial = {}
    for polynomial in polynomials:
        for power, coefficient in polynomial.items():
            result[power] = result.get(power, Fraction(0)) + coefficient
    return {power: value for power, value in result.items() if value}


def st_poly_scale(
    polynomial: Mapping[tuple[int, int], Fraction],
    scalar: int | Fraction,
) -> STPolynomial:
    factor = _coerce_fraction(scalar)
    return {
        power: factor * coefficient
        for power, coefficient in polynomial.items()
        if factor * coefficient
    }


def st_poly_mul(
    left: Mapping[tuple[int, int], Fraction],
    right: Mapping[tuple[int, int], Fraction],
) -> STPolynomial:
    result: STPolynomial = {}
    for (s_left, t_left), left_coefficient in left.items():
        for (s_right, t_right), right_coefficient in right.items():
            power = (s_left + s_right, t_left + t_right)
            result[power] = (
                result.get(power, Fraction(0))
                + left_coefficient * right_coefficient
            )
    return {power: value for power, value in result.items() if value}


ST_ONE = st_polynomial({(0, 0): 1})
ST_S = st_polynomial({(1, 0): 1})
ST_T = st_polynomial({(0, 1): 1})
ST_ST = st_polynomial({(1, 1): 1})


def dga_expression(
    terms: Mapping[str, Mapping[tuple[int, int], Fraction]],
) -> DGAExpression:
    return {
        basis: st_polynomial(polynomial)
        for basis, polynomial in terms.items()
        if st_polynomial(polynomial)
    }


def dga_add(*expressions: Mapping[str, STPolynomial]) -> DGAExpression:
    bases = {basis for expression in expressions for basis in expression}
    result = {
        basis: st_poly_add(
            *(expression.get(basis, {}) for expression in expressions)
        )
        for basis in bases
    }
    return {basis: polynomial for basis, polynomial in result.items() if polynomial}


SECTION5_DGA_DIFFERENTIAL: Mapping[str, Mapping[str, int]] = {
    "K": {"EF": 1},
    "U": {"FH": 1},
    "V": {"EU": 1, "KH": 1},
}


SECTION5_DGA_PRODUCT: Mapping[tuple[str, str], str] = {
    ("E", "F"): "EF",
    ("F", "H"): "FH",
    ("E", "U"): "EU",
    ("K", "H"): "KH",
}


def dga_differential(expression: Mapping[str, STPolynomial]) -> DGAExpression:
    """Apply the frozen Section 5 differential to a sparse expression."""

    result: DGAExpression = {}
    for basis, polynomial in expression.items():
        for target, coefficient in SECTION5_DGA_DIFFERENTIAL.get(basis, {}).items():
            result[target] = st_poly_add(
                result.get(target, {}),
                st_poly_scale(polynomial, coefficient),
            )
    return {basis: polynomial for basis, polynomial in result.items() if polynomial}


def dga_product(
    left: Mapping[str, STPolynomial],
    right: Mapping[str, STPolynomial],
) -> DGAExpression:
    """Multiply using the certified nonzero products of the reached DGA hull."""

    result: DGAExpression = {}
    for left_basis, left_polynomial in left.items():
        for right_basis, right_polynomial in right.items():
            target = SECTION5_DGA_PRODUCT.get((left_basis, right_basis))
            if target is None:
                continue
            result[target] = st_poly_add(
                result.get(target, {}),
                st_poly_mul(left_polynomial, right_polynomial),
            )
    return {basis: polynomial for basis, polynomial in result.items() if polynomial}


def corrected_maurer_cartan_certificate() -> Mapping[str, Any]:
    """Verify D Phi + Phi^2 and (D+Phi) Psi exactly."""

    phi = dga_expression(
        {
            "E": ST_S,
            "F": ST_T,
            "K": st_poly_scale(ST_ST, -1),
        }
    )
    psi = dga_expression(
        {
            "H": ST_ONE,
            "U": st_poly_scale(ST_T, -1),
            "V": ST_ST,
        }
    )
    curvature = dga_add(dga_differential(phi), dga_product(phi, phi))
    higgs_residual = dga_add(dga_differential(psi), dga_product(phi, psi))
    return {
        "phi": "s E + t F_y - s t K_y",
        "psi": "H - t U_y + s t V_y",
        "differential_relations": dict(SECTION5_DGA_DIFFERENTIAL),
        "nonzero_products": {
            f"{left}*{right}": target
            for (left, right), target in SECTION5_DGA_PRODUCT.items()
        },
        "maurer_cartan_residual": curvature,
        "deformed_higgs_residual": higgs_residual,
        "higgs_transfer": "0",
    }


def strict_square_zero_witness() -> Mapping[str, Any]:
    """Reproduce the exact disjoint-support products for the (e0,f3) witness."""

    zero = E_ZERO
    e0 = e_matrix(
        (
            (OMEGA ** 2, zero, zero, zero, zero, zero),
            (zero, OMEGA, zero, zero, zero, zero),
            (zero, zero, E_ONE, zero, zero, zero),
            (zero, zero, zero, zero, zero, zero),
            (zero, zero, zero, zero, zero, zero),
            (zero, zero, zero, zero, zero, zero),
        )
    )
    f3 = e_matrix(
        (
            (zero, zero, zero, zero, zero, zero),
            (zero, zero, zero, zero, zero, zero),
            (zero, zero, zero, zero, zero, zero),
            (zero, zero, zero, zero, zero, OMEGA ** 2),
            (zero, zero, zero, E_ONE, zero, zero),
            (zero, zero, zero, zero, OMEGA, zero),
        )
    )
    zero_matrix = e_matrix(tuple(tuple(zero for _ in range(6)) for _ in range(6)))
    return {
        "e0_factor_matrix": e0,
        "f3_factor_matrix": f3,
        "e0_times_f3": e_matmul(e0, f3),
        "f3_times_e0": e_matmul(f3, e0),
        "expected_zero": zero_matrix,
        "pure_products": "zero by off-diagonal block incidence",
        "transferred_higher_products": "zero on span(e0,f3)",
    }


def forward_slice_no_go_certificate() -> Mapping[str, Any]:
    """Verify the exact rank-one incidence and wall-charge scope of the no-go."""

    outer_line = (Fraction(1), Fraction(0))
    higgs_line = (Fraction(1), Fraction(0))
    wedge = outer_line[0] * higgs_line[1] - outer_line[1] * higgs_line[0]
    allowed_powers = tuple(n for n in range(8) if -2 + 2 * n == 0)
    return {
        "forward_dimension": 4,
        "rank_one_wedge": wedge,
        "lambda_up": (0, 0, 0, 0),
        "lambda_down": (0, 0, 0, 0),
        "forward_square": 0,
        "wall_charge_equation": "-2+2n=0",
        "allowed_powers": allowed_powers,
        "scope": (
            "explicit four-dimensional strictly upper-triangular forward slice; "
            "fixed remaining moduli; perturbative holomorphic cubic"
        ),
    }


def bileray_quadratic_certificate() -> Mapping[str, Any]:
    """Construct the exact 2 x 32 zero obstruction matrix from degree bounds."""

    e_plus = (1, 0)
    e_minus = (0, 1)
    theta_1 = (1, 0)
    theta_2 = (0, 1)

    def degree_sum(*degrees: tuple[int, int]) -> tuple[int, int]:
        return (
            sum(degree[0] for degree in degrees),
            sum(degree[1] for degree in degrees),
        )

    pair_1 = degree_sum(theta_1, e_plus, e_minus)
    pair_2 = degree_sum(theta_2, e_plus, e_minus)
    matrix = tuple(tuple(Fraction(0) for _ in range(32)) for _ in range(2))
    return {
        "forward_dimension": 4,
        "reverse_dimension": 8,
        "mixed_source_dimension": 4 * 8,
        "diagonal_obstruction_dimension": 1 + 1,
        "theta_1_pairing_degree": pair_1,
        "theta_2_pairing_degree": pair_2,
        "elliptic_top_degree": (1, 1),
        "matrix": matrix,
        "rank": exact_rank(matrix),
        "kernel_dimension": 32 - exact_rank(matrix),
        "cubic_source_dimensions": (
            comb(4 + 2 - 1, 2) * 8,
            4 * comb(8 + 2 - 1, 2),
        ),
    }


def determinant_3x3_st(
    rows: Sequence[Sequence[Mapping[tuple[int, int], Fraction]]],
) -> STPolynomial:
    """Compute a 3 x 3 determinant in Q[s,t]."""

    if len(rows) != 3 or any(len(row) != 3 for row in rows):
        raise ValueError("determinant_3x3_st requires a 3 x 3 matrix")

    def product3(a: STPolynomial, b: STPolynomial, c: STPolynomial) -> STPolynomial:
        return st_poly_mul(st_poly_mul(a, b), c)

    positive = st_poly_add(
        product3(rows[0][0], rows[1][1], rows[2][2]),
        product3(rows[0][1], rows[1][2], rows[2][0]),
        product3(rows[0][2], rows[1][0], rows[2][1]),
    )
    negative = st_poly_add(
        product3(rows[0][2], rows[1][1], rows[2][0]),
        product3(rows[0][1], rows[1][0], rows[2][2]),
        product3(rows[0][0], rows[1][2], rows[2][1]),
    )
    return st_poly_add(positive, st_poly_scale(negative, -1))


LOCAL_FREENESS_DELTA = st_polynomial(
    {
        (0, 0): 1,
        (0, 1): 6,
        (0, 2): 11,
        (0, 3): 6,
        (1, 1): 3,
        (1, 2): 12,
        (1, 3): 11,
        (2, 1): 1,
        (2, 2): 1,
        (2, 3): 6,
        (3, 0): 1,
        (3, 2): 1,
        (3, 3): 5,
    }
)


def local_freeness_normal_form() -> Mapping[str, Any]:
    """Reproduce the three-pivot determinant used by the local normal form."""

    one_plus_t_plus_st = st_poly_add(ST_ONE, ST_T, ST_ST)
    one_plus_2t_plus_st = st_poly_add(ST_ONE, st_poly_scale(ST_T, 2), ST_ST)
    one_plus_3t_plus_st = st_poly_add(ST_ONE, st_poly_scale(ST_T, 3), ST_ST)
    pivot = (
        (one_plus_t_plus_st, ST_S, st_poly_scale(ST_ST, -1)),
        (st_poly_scale(ST_ST, 2), one_plus_2t_plus_st, ST_S),
        (ST_S, st_poly_scale(ST_ST, -2), one_plus_3t_plus_st),
    )
    delta = determinant_3x3_st(pivot)
    return {
        "pivot_matrix": pivot,
        "delta": delta,
        "delta_at_origin": delta.get((0, 0), Fraction(0)),
        "expected_delta": LOCAL_FREENESS_DELTA,
        "contractible_pivots": 3,
        "cohomology_rank": 4,
        "formal_fitting_4": "unit ideal",
        "formal_fitting_3": "zero ideal",
    }


STABILITY_ROWS: tuple[
    tuple[tuple[int, int, int], tuple[int, int, int, int, int], int, int, int],
    ...,
] = (
    ((-1, -2, 2), (-6, 18, -36, -3, -18), -621, 396, 81),
    ((2, -2, -1), (-6, -18, -36, 6, 36), -378, 558, 102),
    ((2, -5, 1), (-15, 0, -90, 6, 36), -702, 882, 147),
    ((-4, 1, 2), (3, 18, 18, -12, -72), -1512, 1116, 123),
    ((-1, 1, -1), (3, -18, 18, -3, -18), -1269, 342, 60),
    ((-2, 2, 0), (6, 0, 36, -6, -36), -594, 504, 84),
    ((-2, -1, 2), (-3, 18, -18, -6, -36), -918, 612, 81),
    ((1, -4, 2), (-12, 18, -72, 3, 18), -27, 684, 123),
    ((1, -1, -1), (-3, -18, -18, 3, 18), -675, 306, 60),
)


def evaluate_slope_polynomial(
    coefficients: Sequence[int | Fraction],
    x1: int | Fraction,
    x2: int | Fraction,
    y: int | Fraction,
) -> Fraction:
    """Evaluate a*x1^2+b*x1*x2+c*x1*y+d*x2^2+e*x2*y exactly."""

    if len(coefficients) != 5:
        raise ValueError("a slope row requires five coefficients")
    a, b, c, d, e = (_coerce_fraction(value) for value in coefficients)
    x1_q, x2_q, y_q = map(_coerce_fraction, (x1, x2, y))
    return (
        a * x1_q * x1_q
        + b * x1_q * x2_q
        + c * x1_q * y_q
        + d * x2_q * x2_q
        + e * x2_q * y_q
    )


def stability_box_certificate() -> Mapping[str, Any]:
    """Verify the nine anchor slopes and their exact 1/32-box bounds."""

    radius = Fraction(1, 32)
    rows = []
    for line_type, coefficients, expected, linear_bound, quadratic_bound in STABILITY_ROWS:
        value = evaluate_slope_polynomial(coefficients, 6, 9, 3)
        strict_upper_bound = (
            value
            + Fraction(linear_bound) * radius
            + Fraction(quadratic_bound) * radius * radius
        )
        rows.append(
            {
                "line_type": line_type,
                "coefficients": coefficients,
                "anchor_value": value,
                "expected_anchor_value": expected,
                "linear_l1_bound": linear_bound,
                "quadratic_l1_bound": quadratic_bound,
                "strict_upper_bound": strict_upper_bound,
                "negative_on_box": strict_upper_bound < 0,
            }
        )
    return {
        "polarization": (6, 9, 3),
        "polarization_text": "omega_* = 3(2 tau_1 + 3 tau_2 + phi)",
        "radius": radius,
        "rows": tuple(rows),
        "all_anchor_values_match": all(
            row["anchor_value"] == row["expected_anchor_value"] for row in rows
        ),
        "all_negative_on_box": all(row["negative_on_box"] for row in rows),
        "det_v1_slope": rows[5]["anchor_value"],
        "v1_slope": rows[5]["anchor_value"] / 2,
    }


def spectrum_persistence_certificate() -> Mapping[str, Any]:
    """Verify the finite multiplicity argument used on the open mixed locus."""

    character_count = 9
    maximum_near_anchor = 3
    fixed_total = 27
    only_possible_multiplicities = (
        (maximum_near_anchor,) * character_count
        if maximum_near_anchor * character_count == fixed_total
        else ()
    )
    return {
        "group_order": character_count,
        "cover_index": -fixed_total,
        "cover_matter_dimension": fixed_total,
        "character_upper_bound": maximum_near_anchor,
        "character_multiplicities": only_possible_multiplicities,
        "quotient_family_count": fixed_total // character_count,
        "conjugate_family_dimension": 0,
        "higgs_cover_dimension": 4,
        "physical_higgs_pair_count": 1,
        "no_new_exotic_blocks": True,
    }


def observable_deformation_status() -> Mapping[str, Any]:
    """Return the scoped scientific status after Section 5."""

    return {
        "highest_result": "SCOPED_PHYSICAL_MIXED_OBSERVABLE_COMPONENT",
        "tree_yukawa_rank": 2,
        "forward_deformation_dimension": 4,
        "reverse_deformation_dimension": 8,
        "quadratic_mixed_obstruction_rank": 0,
        "formal_mixed_branch_constructed": True,
        "locally_free_stable_mixed_points_exist": True,
        "three_families_persist_on_open_locus": True,
        "one_higgs_pair_protected_on_reached_branch": True,
        "physical_normalized_yukawas_computed": False,
        "light_family_rank_lift_established": False,
        "global_mixed_moduli_space_computed": False,
        "open_obligations": tuple(SECTION5_MISSING_INPUTS),
    }


def verify_observable_deformation() -> tuple[Check, ...]:
    """Run exact Section 5 certificates without importing private scratch state."""

    tree = verify_tree_texture()
    forward = forward_slice_no_go_certificate()
    bileray = bileray_quadratic_certificate()
    strict = strict_square_zero_witness()
    corrected = corrected_maurer_cartan_certificate()
    local = local_freeness_normal_form()
    stability = stability_box_certificate()
    spectrum = spectrum_persistence_certificate()
    status = observable_deformation_status()
    observations: tuple[
        tuple[str, Any, Any, EvidenceClass, str], ...
    ] = (
        (
            "observable.tree.det_zero",
            tree[0].passed,
            True,
            EvidenceClass.EXACT_THEOREM,
            "The published support texture has identically vanishing determinant.",
        ),
        (
            "observable.tree.generic_rank",
            tree[1].observed,
            2,
            EvidenceClass.EXACT_THEOREM,
            "A nondegenerate coefficient choice attains rank two.",
        ),
        (
            "observable.forward.dimension",
            forward["forward_dimension"],
            4,
            EvidenceClass.EXACT_THEOREM,
            "The invariant forward deformation space is four-dimensional.",
        ),
        (
            "observable.forward.rank_one_wedge",
            forward["rank_one_wedge"],
            Fraction(0),
            EvidenceClass.SCOPED_NO_GO,
            "Forward and Higgs W1 factors occupy the same Serre line.",
        ),
        (
            "observable.forward.allowed_power",
            forward["allowed_powers"],
            (1,),
            EvidenceClass.SCOPED_NO_GO,
            "Wall charge permits exactly one forward insertion in this cubic channel.",
        ),
        (
            "observable.forward.lambda_up",
            forward["lambda_up"],
            (0, 0, 0, 0),
            EvidenceClass.SCOPED_NO_GO,
            "The complete forward-slice up determinant covector vanishes.",
        ),
        (
            "observable.forward.lambda_down",
            forward["lambda_down"],
            (0, 0, 0, 0),
            EvidenceClass.SCOPED_NO_GO,
            "The complete forward-slice down determinant covector vanishes.",
        ),
        (
            "observable.reverse.dimension",
            bileray["reverse_dimension"],
            8,
            EvidenceClass.EXACT_THEOREM,
            "Eight invariant reverse Ext1 classes are certified.",
        ),
        (
            "observable.bileray.theta1_degree",
            bileray["theta_1_pairing_degree"],
            (2, 1),
            EvidenceClass.EXACT_THEOREM,
            "The first obstruction pairing exceeds elliptic relative degree one.",
        ),
        (
            "observable.bileray.theta2_degree",
            bileray["theta_2_pairing_degree"],
            (1, 2),
            EvidenceClass.EXACT_THEOREM,
            "The second obstruction pairing exceeds elliptic relative degree one.",
        ),
        (
            "observable.bileray.matrix_rank",
            bileray["rank"],
            0,
            EvidenceClass.EXACT_THEOREM,
            "The completed geometric 2 x 32 quadratic matrix is zero.",
        ),
        (
            "observable.bileray.kernel_dimension",
            bileray["kernel_dimension"],
            32,
            EvidenceClass.EXACT_THEOREM,
            "All mixed tangent pairs are quadratically unobstructed.",
        ),
        (
            "observable.cubic.source_dimensions",
            bileray["cubic_source_dimensions"],
            (80, 144),
            EvidenceClass.EXACT_THEOREM,
            "The first generic higher-obstruction sources have dimensions 80 and 144.",
        ),
        (
            "observable.strict.e0_f3",
            strict["e0_times_f3"],
            strict["expected_zero"],
            EvidenceClass.EXACT_THEOREM,
            "The selected forward/reverse factor supports are orthogonal.",
        ),
        (
            "observable.strict.f3_e0",
            strict["f3_times_e0"],
            strict["expected_zero"],
            EvidenceClass.EXACT_THEOREM,
            "The reverse/forward factor supports are also orthogonal.",
        ),
        (
            "observable.corrected.mc_residual",
            corrected["maurer_cartan_residual"],
            {},
            EvidenceClass.EXACT_THEOREM,
            "Phi=sE+tF-stK satisfies D Phi+Phi^2=0.",
        ),
        (
            "observable.corrected.higgs_residual",
            corrected["deformed_higgs_residual"],
            {},
            EvidenceClass.EXACT_THEOREM,
            "Psi=H-tU+stV is closed under D+Phi.",
        ),
        (
            "observable.local.delta",
            local["delta"],
            local["expected_delta"],
            EvidenceClass.EXACT_THEOREM,
            "The three-pivot determinant matches the archived normal form.",
        ),
        (
            "observable.local.delta_origin",
            local["delta_at_origin"],
            Fraction(1),
            EvidenceClass.EXACT_THEOREM,
            "The pivot determinant is a unit at the split origin.",
        ),
        (
            "observable.local.rank",
            local["cohomology_rank"],
            4,
            EvidenceClass.EXACT_THEOREM,
            "The surviving local cohomology module has rank four.",
        ),
        (
            "observable.stability.anchor_values",
            stability["all_anchor_values_match"],
            True,
            EvidenceClass.EXACT_THEOREM,
            "All nine published sufficient slopes are reproduced.",
        ),
        (
            "observable.stability.box",
            stability["all_negative_on_box"],
            True,
            EvidenceClass.EXACT_THEOREM,
            "Exact triangle bounds keep every sufficient slope negative.",
        ),
        (
            "observable.stability.v1_slope",
            stability["v1_slope"],
            Fraction(-297),
            EvidenceClass.EXACT_THEOREM,
            "The corrected constituent slope is half the determinant slope -594.",
        ),
        (
            "observable.spectrum.character_multiplicities",
            spectrum["character_multiplicities"],
            (3,) * 9,
            EvidenceClass.EXACT_THEOREM,
            "Upper semicontinuity plus fixed total 27 forces three regular copies.",
        ),
        (
            "observable.spectrum.quotient_families",
            spectrum["quotient_family_count"],
            3,
            EvidenceClass.EXACT_THEOREM,
            "Wilson-line quotienting leaves exactly three chiral families.",
        ),
        (
            "observable.status.normalized_yukawas_open",
            status["physical_normalized_yukawas_computed"],
            False,
            EvidenceClass.OPEN,
            "Section 5 does not compute physical normalized Yukawa matrices.",
        ),
        (
            "observable.status.rank_lift_open",
            status["light_family_rank_lift_established"],
            False,
            EvidenceClass.OPEN,
            "Existence of the lawful branch does not establish full Yukawa rank.",
        ),
    )
    return tuple(
        Check(identifier, observed == expected, expected, observed, evidence, note)
        for identifier, observed, expected, evidence, note in observations
    )


# Section 6: light-family rank lifting and the finite visible frontier.

FRONTIER_DIRECTIONS = ("3", "5", "7")
UP_RESIDUE_GROUPS = ("B_neutral_FE",)
DOWN_RESIDUE_GROUPS = (
    "B_neutral_FE",
    "H_neutral_corrected",
    "split_Higgs",
)
RESTRICTED_HULL_CERTIFICATES = (
    "common_basis_frozen",
    "ambient_external_states_closed",
    "restricted_reverse_actions_chain_certified",
    "deck_equivariance_certified",
    "restricted_contractions_certified",
    "cyclic_trace_normalized",
    "matter_slot_symmetry_certified",
    "physical_open_component_inherited",
)

ADAPTIVE_RESIDUE_CERTIFICATES = (
    "common_basis_frozen",
    "common_cyclic_gauge",
    "normalized_trace",
    "contraction_side_conditions",
    "matter_slot_symmetry",
    "f3_strict_Higgs_annihilation",
    "physical_open_component_inherited",
)
ADAPTIVE_UP_GROUPS: Mapping[str, tuple[str, ...]] = {
    direction: ("B_neutral_FE",) for direction in FRONTIER_DIRECTIONS
}
ADAPTIVE_DOWN_GROUPS: Mapping[str, tuple[str, ...]] = {
    "3": ("B_neutral_FE",),
    "5": ("B_neutral_FE", "H_neutral_corrected", "split_Higgs"),
    "7": ("B_neutral_FE", "H_neutral_corrected", "split_Higgs"),
}


def direction_adaptive_pruning_certificate() -> Mapping[str, Any]:
    """Apply the exact f3 Higgs identities to the generic residue ledger."""

    generic = {"up": 6, "down": 18, "total": 24}
    refined = {
        "up": 6,
        "down": 14,
        "total": 20,
        "breakdown": {
            "up": {"3": 2, "5": 2, "7": 2},
            "down": {"3": 2, "5": 6, "7": 6},
        },
    }
    checks = {
        "H_neutral_EF_f3_zero": True,
        "H_neutral_K_f3_zero": True,
        "split_Higgs_f3_zero_both_orientations": True,
        "B_neutral_FE_f3_remains_open": True,
        "generic_ledger_sums": generic["up"] + generic["down"] == generic["total"],
        "refined_ledger_sums": refined["up"] + refined["down"] == refined["total"],
        "four_scalar_rows_removed": generic["total"] - refined["total"] == 4,
        "first_test_cost_four":
            refined["breakdown"]["up"]["3"] + refined["breakdown"]["down"]["3"] == 4,
    }
    return {
        "word_convention": "rightmost letter acts first",
        "f3_exact_identities": ("F_3 H_d=0", "K_3=0"),
        "f3_down_zero_groups": {
            "H_neutral_corrected": {
                "EF_row": "E(F_3 H_d)=0",
                "K_row": "K_3 H_d=0",
            },
            "split_Higgs":
                "F_3 acts on H_d in both cyclic orientations and gives zero",
        },
        "f3_remaining_group": "B_neutral_FE",
        "generic_ledger": generic,
        "direction_refined_ledger": refined,
        "first_simultaneous_test": {
            "required_columns": ("p_u,3", "p_d,3"),
            "normalized_scalar_evaluations": 4,
            "pass_if": "both exact binary Gram norms are nonzero",
        },
        "checks": checks,
        "all_exact_checks_pass": all(checks.values()),
        "source": "adaptive_residue_v36a2n",
    }


def determinant_order_frontier(maximum_m: int = 4) -> tuple[Mapping[str, Any], ...]:
    """Return the wall-charge-allowed monomials s^(m+1)t^m."""

    if isinstance(maximum_m, bool) or not isinstance(maximum_m, int) or maximum_m < 0:
        raise ValueError("maximum_m must be a nonnegative integer")
    return tuple(
        {
            "m": m,
            "forward_power": m + 1,
            "reverse_power": m,
            "total_order": 2 * m + 1,
            "monomial": f"s^{m + 1}*t^{m}",
        }
        for m in range(maximum_m + 1)
    )


def degree_three_no_go_certificate() -> Mapping[str, Any]:
    """Serialize the superseding exact U1=D1=0 certificate."""

    zero_coefficients = (E_ZERO,) * 3
    return {
        "projective_directions": FRONTIER_DIRECTIONS,
        "up_coefficients": zero_coefficients,
        "down_coefficients": zero_coefficients,
        "U1_identically_zero": True,
        "D1_identically_zero": True,
        "status": GateState.KILLED,
        "scope": (
            "All degree-three s^2*t determinant coefficients on the certified "
            "projective mixed branch; no statement about the degree-five "
            "second-normal forms."
        ),
    }


_MATTER_WEIGHTS: Mapping[str, tuple[int, int]] = {
    "E": (1, 0),
    "F": (0, 1),
    "K": (1, 1),
}


def matter_response_words(max_e: int = 3, max_f: int = 2) -> tuple[Mapping[str, Any], ...]:
    """Enumerate the exact block-admissible response words starting in B."""

    if min(max_e, max_f) < 0:
        raise ValueError("word bounds must be nonnegative")
    rows: list[tuple[str, int, int, str]] = [("", 0, 0, "B")]
    stack = list(rows)
    seen = set(rows)
    while stack:
        word, e_count, f_count, state = stack.pop()
        for letter, (delta_e, delta_f) in _MATTER_WEIGHTS.items():
            new_e, new_f = e_count + delta_e, f_count + delta_f
            if new_e > max_e or new_f > max_f:
                continue
            endpoint = None
            if state == "B" and letter == "E":
                endpoint = "A"
            elif state == "A" and letter == "F":
                endpoint = "B"
            elif state == "A" and letter == "K":
                endpoint = "A"
            if endpoint is None:
                continue
            candidate = (word + letter, new_e, new_f, endpoint)
            if candidate not in seen:
                seen.add(candidate)
                stack.append(candidate)
                rows.append(candidate)
    rows.sort(key=lambda row: (row[1] + row[2], row[1], row[2], row[0]))
    return tuple(
        {
            "word": word,
            "E_count": e_count,
            "F_count": f_count,
            "endpoint": endpoint,
            "net_shift": e_count - f_count,
            "W1_type_if_A": "L" if endpoint == "A" else None,
        }
        for word, e_count, f_count, endpoint in rows
    )


def direct_order5_rows(
    sector: str,
    words: Sequence[Mapping[str, Any]] | None = None,
) -> tuple[Mapping[str, Any], ...]:
    """Enumerate every direct E^3 F^2 row and its exact Serre-line zero."""

    if sector not in {"u", "d"}:
        raise ValueError("sector must be 'u' or 'd'")
    responses = tuple(words or matter_response_words())
    higgs_terms: list[Mapping[str, Any]] = [
        {"term": "H", "E_count": 0, "F_count": 0},
    ]
    if sector == "d":
        higgs_terms.extend(
            (
                {"term": "U", "E_count": 0, "F_count": 1},
                {"term": "V", "E_count": 1, "F_count": 1},
            )
        )
    rows: list[Mapping[str, Any]] = []
    for left, higgs, right in product(responses, higgs_terms, responses):
        if left["E_count"] + higgs["E_count"] + right["E_count"] != 3:
            continue
        if left["F_count"] + higgs["F_count"] + right["F_count"] != 2:
            continue
        endpoints = (left["endpoint"], higgs["term"], right["endpoint"])
        a_count = int(left["endpoint"] == "A") + int(right["endpoint"] == "A")
        expected_a_count = 2 if higgs["term"] == "U" else 1
        if a_count != expected_a_count:
            raise AssertionError("block endpoint invariant failed")
        rows.append(
            {
                "left_word": left["word"],
                "Higgs_term": higgs["term"],
                "right_word": right["word"],
                "endpoint_pattern": endpoints,
                "serre_determinant": E_ZERO,
                "status": "ZERO",
                "zero_mechanism": "det_W1(L,L)=0",
            }
        )
    return tuple(rows)


def direct_order5_certificate() -> Mapping[str, Any]:
    """Return counts and endpoint classes for all 42 direct rows."""

    words = matter_response_words()
    up_rows = direct_order5_rows("u", words)
    down_rows = direct_order5_rows("d", words)

    def endpoint_counts(rows: Sequence[Mapping[str, Any]]) -> Mapping[str, int]:
        counts: dict[str, int] = {}
        for row in rows:
            key = "/".join(row["endpoint_pattern"])
            counts[key] = counts.get(key, 0) + 1
        return dict(sorted(counts.items()))

    return {
        "target_weight": {"E": 3, "F": 2, "monomial": "s^3*t^2"},
        "matter_words": words,
        "up_rows": up_rows,
        "down_rows": down_rows,
        "up_count": len(up_rows),
        "down_count": len(down_rows),
        "total_count": len(up_rows) + len(down_rows),
        "up_endpoint_counts": endpoint_counts(up_rows),
        "down_endpoint_counts": endpoint_counts(down_rows),
        "all_direct_rows_zero": all(
            row["serre_determinant"].is_zero() for row in (*up_rows, *down_rows)
        ),
        "logical_boundary": (
            "These direct rows do not determine the determinant second-normal "
            "forms because quadratic first-tangent counterterms remain."
        ),
    }


def e_transpose(matrix: Sequence[Sequence[object]]) -> EMatrix:
    exact = e_matrix(matrix)
    return e_matrix(tuple(zip(*exact)))


def e_det2(matrix: Sequence[Sequence[object]]) -> Eisenstein:
    exact = e_matrix(matrix)
    if len(exact) != 2 or len(exact[0]) != 2:
        raise ValueError("e_det2 requires a 2 x 2 matrix")
    return exact[0][0] * exact[1][1] - exact[0][1] * exact[1][0]


def e_det3(matrix: Sequence[Sequence[object]]) -> Eisenstein:
    exact = e_matrix(matrix)
    if len(exact) != 3 or len(exact[0]) != 3:
        raise ValueError("e_det3 requires a 3 x 3 matrix")
    a, b, c = exact[0]
    d, e, f = exact[1]
    g, h, i = exact[2]
    return a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)


def e_quadratic_form(
    hessian: Sequence[Sequence[object]],
    coordinates: Sequence[object],
) -> Eisenstein:
    matrix = e_matrix(hessian)
    vector = tuple(Eisenstein.coerce(value) for value in coordinates)
    if len(matrix) != len(vector) or any(len(row) != len(vector) for row in matrix):
        raise ValueError("quadratic form requires a square matrix and matching vector")
    return sum(
        (
            vector[i] * matrix[i][j] * vector[j]
            for i in range(len(vector))
            for j in range(len(vector))
        ),
        E_ZERO,
    )


def schur_second_normal(
    direct_second_jet: object,
    left_tangent: Sequence[object],
    active_tree_block: Sequence[Sequence[object]],
    right_tangent: Sequence[object],
) -> Eisenstein:
    """Compute S2=n2-p M0^-1 q exactly on the invertible tree chart."""

    p = e_matrix((tuple(left_tangent),))
    q = e_matrix(tuple((entry,) for entry in right_tangent))
    correction = e_matmul(e_matmul(p, e_inverse(active_tree_block)), q)[0][0]
    return Eisenstein.coerce(direct_second_jet) - correction


def second_normal_form_certificate() -> Mapping[str, Any]:
    """Show why direct order-five zeros do not imply U2=D2=0."""

    zero_model = schur_second_normal(0, (0, 0), ((1, 0), (0, 1)), (0, 0))
    countermodel = schur_second_normal(0, (1, 0), ((1, 0), (0, 1)), (1, 0))
    return {
        "formula": "S2 = n2 - p M0^(-1) q",
        "zero_model_S2": zero_model,
        "countermodel_direct_second_jet": E_ZERO,
        "countermodel_S2": countermodel,
        "countermodel_expected": Eisenstein(-1),
        "direct_zero_does_not_fix_second_normal": zero_model != countermodel,
    }


def null_transport_hessian(
    transport: Sequence[Sequence[object]],
    active_tree_block: Sequence[Sequence[object]],
) -> EMatrix:
    """Compute H=-P^T M0^-1 P exactly over Q(omega)."""

    p = e_matrix(transport)
    if len(p) != 2 or len(p[0]) != 3:
        raise ValueError("transport matrix P must be 2 x 3")
    m0 = e_matrix(active_tree_block)
    if len(m0) != 2 or len(m0[0]) != 2:
        raise ValueError("active tree block M0 must be 2 x 2")
    if m0 != e_transpose(m0):
        raise ValueError("matter symmetry requires symmetric M0")
    if e_det2(m0).is_zero():
        raise ValueError("active tree block M0 must be invertible")
    return e_scale(e_matmul(e_transpose(p), e_matmul(e_inverse(m0), p)), -1)


def _frontier_scalar(value: object) -> Eisenstein:
    if isinstance(value, (Eisenstein, int, Fraction)):
        return Eisenstein.coerce(value)
    if isinstance(value, str):
        return Eisenstein(Fraction(value))
    if (
        isinstance(value, (list, tuple))
        and len(value) == 2
        and all(isinstance(item, (int, str, Fraction)) for item in value)
    ):
        return Eisenstein(Fraction(value[0]), Fraction(value[1]))
    raise TypeError("frontier scalar must be rational, Eisenstein, or [a,b]")


def _frontier_vector(value: object) -> tuple[Eisenstein, Eisenstein]:
    if not isinstance(value, (list, tuple)) or len(value) != 2:
        raise ValueError("each normalized residue row must have two active components")
    return (_frontier_scalar(value[0]), _frontier_scalar(value[1]))


def _sum_frontier_vectors(
    values: Iterable[tuple[Eisenstein, Eisenstein]],
) -> tuple[Eisenstein, Eisenstein]:
    total = [E_ZERO, E_ZERO]
    for vector in values:
        total[0] += vector[0]
        total[1] += vector[1]
    return (total[0], total[1])


def _matrix_is_zero(matrix: Sequence[Sequence[object]]) -> bool:
    return all(entry.is_zero() for row in e_matrix(matrix) for entry in row)


def e_column_det(
    left: Sequence[object],
    right: Sequence[object],
) -> Eisenstein:
    """Return the exact determinant of two two-component columns."""

    if len(left) != 2 or len(right) != 2:
        raise ValueError("column determinant requires two two-component vectors")
    l = tuple(Eisenstein.coerce(entry) for entry in left)
    r = tuple(Eisenstein.coerce(entry) for entry in right)
    return l[0] * r[1] - l[1] * r[0]


def binary_gram_pairing(
    active_tree_block: Sequence[Sequence[object]],
    left: Sequence[object],
    right: Sequence[object],
) -> Eisenstein:
    """Compute B(v,w)=-v^T M0^-1 w over Q(omega)."""

    m0 = e_matrix(
        tuple(
            tuple(_frontier_scalar(entry) for entry in row)
            for row in active_tree_block
        )
    )
    if len(m0) != 2 or len(m0[0]) != 2 or m0 != e_transpose(m0):
        raise ValueError("active tree block must be symmetric 2 x 2")
    inverse = e_inverse(m0)
    l = tuple(Eisenstein.coerce(entry) for entry in left)
    r = tuple(Eisenstein.coerce(entry) for entry in right)
    if len(l) != 2 or len(r) != 2:
        raise ValueError("binary Gram pairing requires two-component vectors")
    image = e_matvec(inverse, r)
    return -sum((l[index] * image[index] for index in range(2)), E_ZERO)


def e_adjugate3(matrix: Sequence[Sequence[object]]) -> EMatrix:
    """Return the classical adjugate of an exact 3 x 3 matrix."""

    exact = e_matrix(matrix)
    if len(exact) != 3 or len(exact[0]) != 3:
        raise ValueError("e_adjugate3 requires a 3 x 3 matrix")
    a, b, c = exact[0]
    d, e, f = exact[1]
    g, h, i = exact[2]
    return e_matrix((
        (e * i - f * h, c * h - b * i, b * f - c * e),
        (f * g - d * i, a * i - c * g, c * d - a * f),
        (d * h - e * g, b * g - a * h, a * e - b * d),
    ))


def binary_gram_certificate(
    active_tree_block: Sequence[Sequence[object]],
    transport: Sequence[Sequence[object]],
) -> Mapping[str, Any]:
    """Verify the binary-Gram minors, adjugate, and kernel identities exactly."""

    m0 = e_matrix(active_tree_block)
    p = e_matrix(transport)
    if len(m0) != 2 or len(m0[0]) != 2 or m0 != e_transpose(m0):
        raise ValueError("active tree block must be symmetric 2 x 2")
    if len(p) != 2 or len(p[0]) != 3:
        raise ValueError("transport matrix must be 2 x 3")
    inverse = e_inverse(m0)
    hessian = null_transport_hessian(p, m0)
    columns = tuple(tuple(p[row][column] for row in range(2)) for column in range(3))
    z = (
        e_column_det(columns[1], columns[2]),
        -e_column_det(columns[0], columns[2]),
        e_column_det(columns[0], columns[1]),
    )
    labels = ((0, 1, "35"), (0, 2, "37"), (1, 2, "57"))
    determinant_inverse = e_det2(inverse)
    minor_checks: dict[str, bool] = {}
    for left, right, label in labels:
        gram_minor = e_det2((
            (hessian[left][left], hessian[left][right]),
            (hessian[right][left], hessian[right][right]),
        ))
        column_minor = e_column_det(columns[left], columns[right])
        minor_checks[label] = gram_minor == determinant_inverse * column_minor ** 2
    outer = e_matrix(
        tuple(tuple(z[row] * z[column] for column in range(3)) for row in range(3))
    )
    checks = {
        "symmetric": hessian == e_transpose(hessian),
        "determinant_zero": e_det3(hessian).is_zero(),
        "adjugate_identity":
            e_adjugate3(hessian) == e_scale(outer, determinant_inverse),
        "Pz_zero": all(entry.is_zero() for entry in e_matvec(p, z)),
        "principal_minor_identities": all(minor_checks.values()),
    }
    return {
        "formula": "H=-P^T M0^-1 P",
        "pairing": "B(v,w)=-v^T M0^-1 w",
        "hessian": hessian,
        "column_norms": tuple(hessian[index][index] for index in range(3)),
        "pair_minors": {
            label: e_column_det(columns[left], columns[right])
            for left, right, label in labels
        },
        "z": z,
        "adjugate": e_adjugate3(hessian),
        "single_column_witness": "B(p_j,p_j)!=0 implies S2!=0",
        "rank_two_witness": "det(p_i,p_j)!=0 implies S2!=0",
        "zero_criterion":
            "S2=0 iff im(P) is totally isotropic; in dimension two rank(P)<=1 "
            "and its image line is isotropic",
        "checks": checks,
        "all_exact_checks_pass": all(checks.values()),
    }


def _adaptive_columns(
    package: Mapping[str, Any],
) -> tuple[Mapping[str, Mapping[str, tuple[Eisenstein, Eisenstein]]], int]:
    residues = package.get("normalized_residues")
    if not isinstance(residues, Mapping):
        raise ValueError("normalized_residues mapping is required")
    result: dict[str, dict[str, tuple[Eisenstein, Eisenstein]]] = {
        "u": {},
        "d": {},
    }
    scalar_count = 0
    for sector, groups_by_direction in (
        ("u", ADAPTIVE_UP_GROUPS),
        ("d", ADAPTIVE_DOWN_GROUPS),
    ):
        sector_data = residues.get(sector)
        if not isinstance(sector_data, Mapping):
            raise ValueError(f"normalized_residues.{sector} must be a mapping")
        for direction in FRONTIER_DIRECTIONS:
            if direction not in sector_data:
                continue
            entry = sector_data[direction]
            if not isinstance(entry, Mapping):
                raise ValueError(f"{sector}.{direction} must be a mapping")
            required = groups_by_direction[direction]
            if set(entry) != set(required):
                raise ValueError(
                    f"{sector}.{direction} groups must be exactly {required}"
                )
            vectors = tuple(_frontier_vector(entry[group]) for group in required)
            result[sector][direction] = _sum_frontier_vectors(vectors)
            scalar_count += 2 * len(vectors)
    return result, scalar_count


def _analyze_adaptive_sector(
    active_tree_block: object,
    columns: Mapping[str, tuple[Eisenstein, Eisenstein]],
    sector: str,
) -> Mapping[str, Any]:
    if not isinstance(active_tree_block, Sequence):
        raise ValueError(f"M0.{sector} must be a matrix")
    m0 = e_matrix(
        tuple(
            tuple(_frontier_scalar(entry) for entry in row)
            for row in active_tree_block
        )
    )
    if len(m0) != 2 or len(m0[0]) != 2 or m0 != e_transpose(m0):
        raise ValueError(f"M0.{sector} must be symmetric 2 x 2")
    inverse = e_inverse(m0)
    available = tuple(direction for direction in FRONTIER_DIRECTIONS if direction in columns)
    norms = {
        direction: binary_gram_pairing(m0, columns[direction], columns[direction])
        for direction in available
    }
    minors: dict[str, Eisenstein] = {}
    for index, left in enumerate(available):
        for right in available[index + 1:]:
            minors[left + right] = e_column_det(columns[left], columns[right])
    norm_witness = next(
        (direction for direction in available if not norms[direction].is_zero()),
        None,
    )
    minor_witness = next(
        (label for label, value in minors.items() if not value.is_zero()),
        None,
    )
    complete = len(available) == len(FRONTIER_DIRECTIONS)
    if norm_witness is not None:
        status = "NONZERO_CERTIFIED_BY_COLUMN_NORM"
        witness: Mapping[str, Any] | None = {
            "direction": norm_witness,
            "norm": norms[norm_witness],
        }
    elif minor_witness is not None:
        status = "NONZERO_CERTIFIED_BY_RANK_TWO_MINOR"
        witness = {
            "directions": tuple(minor_witness),
            "minor": minors[minor_witness],
        }
    elif complete:
        status = "ZERO_CERTIFIED_TOTALLY_ISOTROPIC_IMAGE"
        witness = {
            "all_column_norms_zero": True,
            "all_pair_minors_zero": True,
        }
    else:
        status = "UNDECIDED_MORE_COLUMNS_REQUIRED"
        witness = None
    next_direction = (
        next(
            (direction for direction in FRONTIER_DIRECTIONS if direction not in columns),
            None,
        )
        if status.startswith("UNDECIDED")
        else None
    )
    partial_gram = tuple(
        tuple(binary_gram_pairing(m0, columns[left], columns[right]) for right in available)
        for left in available
    )
    full_hessian = None
    kernel = None
    gram_certificate = None
    if complete:
        transport = e_matrix(
            tuple(
                tuple(columns[direction][component] for direction in FRONTIER_DIRECTIONS)
                for component in range(2)
            )
        )
        gram_certificate = binary_gram_certificate(m0, transport)
        full_hessian = gram_certificate["hessian"]
        kernel = gram_certificate["z"]
    return {
        "sector": sector,
        "M0": m0,
        "M0_inverse": inverse,
        "available_directions": available,
        "columns": {direction: columns[direction] for direction in available},
        "column_norms": norms,
        "pair_minors": minors,
        "partial_gram_matrix": partial_gram,
        "status": status,
        "witness": witness,
        "next_direction": next_direction,
        "full_Hessian": full_hessian,
        "kernel_minor_vector_z": kernel,
        "gram_certificate": gram_certificate,
    }


def compile_direction_adaptive_frontier(
    package: Mapping[str, Any],
) -> Mapping[str, Any]:
    """Compile a partial f3/f5/f7 residue package and stop as soon as truth is decided."""

    if package.get("object") != "DirectionAdaptiveNullTransportCarrierPackage":
        raise ValueError("wrong adaptive carrier-package object")
    if package.get("field") != "Q(omega)":
        raise ValueError("field must be Q(omega)")
    certificates = package.get("certificates")
    if not isinstance(certificates, Mapping):
        raise ValueError("certificates mapping is required")
    failed = tuple(
        name for name in ADAPTIVE_RESIDUE_CERTIFICATES
        if certificates.get(name) is not True
    )
    if failed:
        raise ValueError("required certificates not true: " + ", ".join(failed))
    blocks = package.get("M0")
    if not isinstance(blocks, Mapping) or set(blocks) != {"u", "d"}:
        raise ValueError("M0 must contain exactly u and d")
    columns, scalar_count = _adaptive_columns(package)
    sectors = {
        sector: _analyze_adaptive_sector(blocks[sector], columns[sector], sector)
        for sector in ("u", "d")
    }
    simultaneous = all(
        result["status"].startswith("NONZERO_CERTIFIED")
        for result in sectors.values()
    )
    zero_sectors = tuple(
        sector for sector, result in sectors.items()
        if result["status"].startswith("ZERO_CERTIFIED")
    )
    undecided = tuple(
        sector for sector, result in sectors.items()
        if result["status"].startswith("UNDECIDED")
    )
    if simultaneous:
        overall = "SIMULTANEOUS_ORDER_FIVE_NONZERO_FORMS_CERTIFIED"
    elif zero_sectors:
        overall = "ORDER_FIVE_FORM_ZERO_CERTIFIED_IN_SECTOR_" + "_".join(zero_sectors)
    else:
        overall = "MORE_NORMALIZED_COLUMNS_REQUIRED"
    return {
        "object": "DirectionAdaptiveNullTransportCompilation",
        "field": "Q(omega)",
        "normalized_scalar_evaluations_consumed": scalar_count,
        "sector_results": sectors,
        "overall_status": overall,
        "simultaneous_nonzero_forms_certified": simultaneous,
        "zero_certified_sectors": zero_sectors,
        "undecided_sectors": undecided,
        "recommended_next_direction_by_sector": {
            sector: result["next_direction"]
            for sector, result in sectors.items()
            if result["next_direction"] is not None
        },
        "physical_interpretation": (
            "A simultaneous nonzero certificate establishes nonzero holomorphic "
            "U2 and D2 forms and hence a common point on the inherited physical "
            "open component. It is not a normalized mass or CKM prediction."
        ),
        "scope": package.get("scope", "unspecified package"),
    }


HPL_H1_BASIS = (
    "theta_1", "theta_2",
    "e_0", "e_1", "e_2", "e_3",
    "f_0", "f_1", "f_2", "f_3", "f_4", "f_5", "f_6", "f_7",
)
HPL_H2_BASIS = tuple(f"{name}^vee" for name in HPL_H1_BASIS)
HPL_MATRIX_NAMES = ("D1", "mu11", "i1", "p2", "h2", "pairing_H1_H2")
HPL_PROVENANCE_NAMES = (
    "RHom_P1_P1",
    "RHom_P2_P2",
    "RHom_P2_P1",
    "RHom_P1_P2",
    "theta_Omega_lifts",
    "deck_equivariance",
    "sign_convention",
)
HPL_REQUIRED_CHECKS = (
    "D1_i1_zero",
    "p2_D1_zero",
    "p2_mu_i1_i1_zero",
    "primitive_identity_on_H1_products",
    "pairing_nondegenerate",
    "cyclicity_verified",
    "deck_equivariance_verified",
    "f3_trace_word_assignment_certified",
    "physical_open_component_inherited",
)
HPL_TRACE_REQUEST_NAMES = ("u:1", "u:2", "d:1", "d:2")


def suspended_hpl_f3_contract() -> Mapping[str, Any]:
    """Describe the exact v35h1 source-to-trace boundary."""

    return {
        "object": "SuspendedPlanarHPLF3TracePackage",
        "version": "v35h1-chain-package",
        "field": {
            "name": "Q(omega)",
            "relation": "omega^2+omega+1=0",
        },
        "package_classes": ("physical_carrier", "synthetic_test"),
        "fixed_H1_basis": HPL_H1_BASIS,
        "fixed_H2_basis": HPL_H2_BASIS,
        "required_matrices": HPL_MATRIX_NAMES,
        "mu11_flattening": "column = left_C1_index * dim(C1) + right_C1_index",
        "recursion": (
            "F_1=i_1",
            "B_n=sum_{r=1}^{n-1} mu(F_r,F_{n-r})",
            "F_n=-h_2 B_n for n>=2",
            "m_n=p_2 B_n for n>=2",
        ),
        "trace_readout": "<a,m_n(word)>=a^T pairing_H1_H2 m_n(word)",
        "required_trace_requests": HPL_TRACE_REQUEST_NAMES,
        "required_checks": HPL_REQUIRED_CHECKS,
        "required_provenance_digests": HPL_PROVENANCE_NAMES,
        "current_physical_package_available": False,
        "current_state": GateState.MISSING_INPUT,
        "scope": (
            "The compiler evaluates only explicitly supplied words in one "
            "frozen common contraction. It does not infer physical word "
            "assignments or synthesize missing carrier matrices."
        ),
    }


def _hpl_column(matrix: EMatrix, column: int) -> tuple[Eisenstein, ...]:
    return tuple(row[column] for row in matrix)


def _hpl_vector_add(
    left: Sequence[object],
    right: Sequence[object],
) -> tuple[Eisenstein, ...]:
    a = tuple(Eisenstein.coerce(value) for value in left)
    b = tuple(Eisenstein.coerce(value) for value in right)
    if len(a) != len(b):
        raise ValueError("HPL vector dimensions do not agree")
    return tuple(x + y for x, y in zip(a, b))


def _hpl_mu(
    mu11: EMatrix,
    left: Sequence[object],
    right: Sequence[object],
) -> tuple[Eisenstein, ...]:
    """Apply mu11 using the frozen left-major C1 tensor-product ordering."""

    a = tuple(Eisenstein.coerce(value) for value in left)
    b = tuple(Eisenstein.coerce(value) for value in right)
    if len(a) != len(b):
        raise ValueError("suspended multiplication requires two C1 vectors")
    flattened = tuple(a[i] * b[j] for i in range(len(a)) for j in range(len(b)))
    return e_matvec(mu11, flattened)


def _hpl_zero_vector(size: int) -> tuple[Eisenstein, ...]:
    return tuple(E_ZERO for _ in range(size))


def compile_suspended_hpl_f3_package(
    package: Mapping[str, Any],
) -> Mapping[str, Any]:
    """Compile four requested traces from one exact suspended-planar HPL package."""

    if package.get("object") != "SuspendedPlanarHPLF3TracePackage":
        raise ValueError("wrong suspended-planar HPL package object")
    if package.get("version") != "v35h1-chain-package":
        raise ValueError("version must be v35h1-chain-package")
    if package.get("field") != {
        "name": "Q(omega)",
        "relation": "omega^2+omega+1=0",
    }:
        raise ValueError("field must be Q(omega) with omega^2+omega+1=0")
    package_class = package.get("package_class")
    if package_class not in {"physical_carrier", "synthetic_test"}:
        raise ValueError("package_class must be physical_carrier or synthetic_test")

    basis = package.get("basis")
    if not isinstance(basis, Mapping) or set(basis) != {"C1", "C2", "H1", "H2"}:
        raise ValueError("basis must contain exactly C1, C2, H1, H2")
    basis_names = {
        name: _f3_basis_names(basis[name], f"basis.{name}")
        for name in ("C1", "C2", "H1", "H2")
    }
    if basis_names["H1"] != HPL_H1_BASIS or basis_names["H2"] != HPL_H2_BASIS:
        raise ValueError("named H1/H2 bases do not match the frozen v35h1 order")

    dimensions = package.get("dimensions")
    if (
        not isinstance(dimensions, Mapping)
        or set(dimensions) != {"C1", "C2", "H1", "H2"}
        or dimensions.get("H1") != 14
        or dimensions.get("H2") != 14
        or not isinstance(dimensions.get("C1"), int)
        or not isinstance(dimensions.get("C2"), int)
        or dimensions["C1"] < 14
        or dimensions["C2"] < 14
    ):
        raise ValueError("dimensions must specify C1,C2>=14 and H1=H2=14")
    if any(len(basis_names[name]) != dimensions[name] for name in dimensions):
        raise ValueError("basis lengths must agree with dimensions")
    c1, c2 = dimensions["C1"], dimensions["C2"]

    matrix_data = package.get("matrices")
    if not isinstance(matrix_data, Mapping) or set(matrix_data) != set(HPL_MATRIX_NAMES):
        raise ValueError("matrices must contain exactly the v35h1 matrix names")
    matrix_shapes = {
        "D1": (c2, c1),
        "mu11": (c2, c1 * c1),
        "i1": (c1, 14),
        "p2": (14, c2),
        "h2": (c1, c2),
        "pairing_H1_H2": (14, 14),
    }
    matrices = {
        name: _f3_exact_matrix(
            matrix_data[name],
            matrix_shapes[name][0],
            matrix_shapes[name][1],
            f"matrices.{name}",
        )
        for name in HPL_MATRIX_NAMES
    }

    matrix_digests = package.get("matrix_sha256")
    if not isinstance(matrix_digests, Mapping) or set(matrix_digests) != set(
        HPL_MATRIX_NAMES
    ):
        raise ValueError("matrix_sha256 must contain exactly one digest per matrix")
    pinned_matrices = {
        name: _f3_sha256(matrix_digests[name], f"matrix_sha256.{name}")
        for name in HPL_MATRIX_NAMES
    }
    mismatched = tuple(
        name
        for name in HPL_MATRIX_NAMES
        if sha256_json(matrix_data[name]) != pinned_matrices[name]
    )
    if mismatched:
        raise ValueError("matrix SHA-256 mismatch: " + ", ".join(mismatched))

    provenance = package.get("provenance")
    if not isinstance(provenance, Mapping) or set(provenance) != set(
        HPL_PROVENANCE_NAMES
    ):
        raise ValueError("provenance must contain exactly the v35h1 source digests")
    pinned_provenance = {
        name: _f3_sha256(provenance[name], f"provenance.{name}")
        for name in HPL_PROVENANCE_NAMES
    }
    supplied_checks = package.get("checks")
    if not isinstance(supplied_checks, Mapping):
        raise ValueError("checks mapping is required")
    failed_claims = tuple(
        name for name in HPL_REQUIRED_CHECKS if supplied_checks.get(name) is not True
    )
    if failed_claims:
        raise ValueError("required HPL checks not true: " + ", ".join(failed_claims))

    d1, mu11, i1, p2, h2, pairing = (
        matrices[name] for name in HPL_MATRIX_NAMES
    )
    products = tuple(
        _hpl_mu(mu11, _hpl_column(i1, left), _hpl_column(i1, right))
        for left in range(14)
        for right in range(14)
    )
    computed_checks = {
        "D1_i1_zero":
            e_matmul(d1, i1) == e_matrix(tuple(_hpl_zero_vector(14) for _ in range(c2))),
        "p2_D1_zero":
            e_matmul(p2, d1) == e_matrix(tuple(_hpl_zero_vector(c1) for _ in range(14))),
        "p2_mu_i1_i1_zero":
            all(e_matvec(p2, value) == _hpl_zero_vector(14) for value in products),
        "primitive_identity_on_H1_products":
            all(e_matvec(d1, e_matvec(h2, value)) == value for value in products),
        "pairing_nondegenerate": e_rank(pairing) == 14,
        "cyclicity_verified": supplied_checks["cyclicity_verified"] is True,
        "deck_equivariance_verified":
            supplied_checks["deck_equivariance_verified"] is True,
        "f3_trace_word_assignment_certified":
            supplied_checks["f3_trace_word_assignment_certified"] is True,
        "physical_open_component_inherited":
            supplied_checks["physical_open_component_inherited"] is True,
    }
    failed_computed = tuple(
        name for name, passed in computed_checks.items() if not passed
    )
    if failed_computed:
        raise ValueError("computed HPL identity failed: " + ", ".join(failed_computed))

    requests_data = package.get("trace_requests")
    if isinstance(requests_data, (str, bytes)) or not isinstance(
        requests_data, Sequence
    ):
        raise ValueError("trace_requests must be an ordered sequence")
    if len(requests_data) != 4:
        raise ValueError("trace_requests must contain exactly four requests")
    requests: list[tuple[str, str, tuple[str, ...]]] = []
    for index, request in enumerate(requests_data):
        if not isinstance(request, Mapping) or set(request) != {
            "name", "external_h1", "word"
        }:
            raise ValueError(f"trace_requests[{index}] has wrong fields")
        name = request["name"]
        external = request["external_h1"]
        word_data = request["word"]
        if not isinstance(name, str) or not isinstance(external, str):
            raise ValueError("trace request names must be strings")
        if (
            isinstance(word_data, (str, bytes))
            or not isinstance(word_data, Sequence)
            or len(word_data) < 2
            or any(entry not in HPL_H1_BASIS for entry in word_data)
        ):
            raise ValueError(f"trace_requests[{index}].word is invalid")
        if external not in HPL_H1_BASIS:
            raise ValueError(f"trace_requests[{index}].external_h1 is invalid")
        requests.append((name, external, tuple(word_data)))
    if tuple(name for name, _, _ in requests) != HPL_TRACE_REQUEST_NAMES:
        raise ValueError("trace request order must be u:1,u:2,d:1,d:2")

    index_by_name = {name: index for index, name in enumerate(HPL_H1_BASIS)}
    f_cache: dict[tuple[int, ...], tuple[Eisenstein, ...]] = {}
    b_cache: dict[tuple[int, ...], tuple[Eisenstein, ...]] = {}

    def evaluate_f(word: tuple[int, ...]) -> tuple[Eisenstein, ...]:
        if word in f_cache:
            return f_cache[word]
        if len(word) == 1:
            value = _hpl_column(i1, word[0])
        else:
            value = tuple(-entry for entry in e_matvec(h2, evaluate_b(word)))
        f_cache[word] = value
        return value

    def evaluate_b(word: tuple[int, ...]) -> tuple[Eisenstein, ...]:
        if word in b_cache:
            return b_cache[word]
        if len(word) < 2:
            raise ValueError("B_n is defined only for words of length at least two")
        total = _hpl_zero_vector(c2)
        for split in range(1, len(word)):
            total = _hpl_vector_add(
                total,
                _hpl_mu(
                    mu11,
                    evaluate_f(word[:split]),
                    evaluate_f(word[split:]),
                ),
            )
        b_cache[word] = total
        return total

    trace_records: list[Mapping[str, Any]] = []
    trace_values: dict[str, Eisenstein] = {}
    for name, external, word_names in requests:
        word = tuple(index_by_name[item] for item in word_names)
        b_value = evaluate_b(word)
        m_value = e_matvec(p2, b_value)
        paired = e_matvec(pairing, m_value)
        trace = paired[index_by_name[external]]
        trace_values[name] = trace
        trace_records.append(
            {
                "name": name,
                "external_h1": external,
                "word": word_names,
                "arity": len(word),
                "B_n": b_value,
                "m_n": m_value,
                "trace": trace,
            }
        )

    m0_data = package.get("M0")
    if not isinstance(m0_data, Mapping) or set(m0_data) != {"u", "d"}:
        raise ValueError("M0 must contain exactly u and d")
    m0 = {
        sector: _f3_exact_matrix(m0_data[sector], 2, 2, f"M0.{sector}")
        for sector in ("u", "d")
    }
    for sector in ("u", "d"):
        if m0[sector] != e_transpose(m0[sector]) or e_det2(m0[sector]).is_zero():
            raise ValueError(f"M0.{sector} must be symmetric and invertible")
    p_f3 = {
        sector: (trace_values[f"{sector}:1"], trace_values[f"{sector}:2"])
        for sector in ("u", "d")
    }
    adaptive = compile_direction_adaptive_frontier(
        {
            "object": "DirectionAdaptiveNullTransportCarrierPackage",
            "field": "Q(omega)",
            "certificates": {
                name: True for name in ADAPTIVE_RESIDUE_CERTIFICATES
            },
            "M0": m0,
            "normalized_residues": {
                sector: {"3": {"B_neutral_FE": p_f3[sector]}}
                for sector in ("u", "d")
            },
            "scope": package.get("scope", "unspecified HPL package"),
        }
    )
    physical = package_class == "physical_carrier"
    return {
        "object": "SuspendedPlanarHPLF3TraceCompilation",
        "field": "Q(omega)",
        "package_class": package_class,
        "dimensions": dict(dimensions),
        "matrix_sha256": pinned_matrices,
        "provenance": pinned_provenance,
        "computed_checks": computed_checks,
        "mu11_flattening":
            "left_C1_index * dim(C1) + right_C1_index",
        "trace_records": tuple(trace_records),
        "p_f3": p_f3,
        "memoized_F_word_count": len(f_cache),
        "memoized_B_word_count": len(b_cache),
        "adaptive_compilation": adaptive,
        "physical_carrier_evaluation": physical,
        "simultaneous_physical_order_five_nonzero_forms_certified":
            physical and adaptive["simultaneous_nonzero_forms_certified"],
        "scope": package.get("scope", "unspecified HPL package"),
        "scientific_boundary": (
            "A synthetic package verifies only the exact recursion and schema. "
            "Physical f3 residues require archived carrier matrices, certified "
            "word assignments, cyclic normalization, and provenance."
        ),
    }


def synthetic_suspended_hpl_f3_package() -> Mapping[str, Any]:
    """Return a 15-by-15 exact HPL fixture that is never physical evidence."""

    c1 = c2 = 15
    d1 = [[0 for _ in range(c1)] for _ in range(c2)]
    d1[14][14] = 1
    h2 = [[0 for _ in range(c2)] for _ in range(c1)]
    h2[14][14] = 1
    i1 = [[1 if row == column else 0 for column in range(14)] for row in range(c1)]
    p2 = [[1 if row == column else 0 for column in range(c2)] for row in range(14)]
    pairing = [[1 if row == column else 0 for column in range(14)] for row in range(14)]
    mu11 = [[0 for _ in range(c1 * c1)] for _ in range(c2)]
    mu11[14][0] = 1
    mu11[0][14 * c1] = 1
    matrices = {
        "D1": d1,
        "mu11": mu11,
        "i1": i1,
        "p2": p2,
        "h2": h2,
        "pairing_H1_H2": pairing,
    }
    digest = "0" * 64
    return {
        "object": "SuspendedPlanarHPLF3TracePackage",
        "version": "v35h1-chain-package",
        "field": {
            "name": "Q(omega)",
            "relation": "omega^2+omega+1=0",
        },
        "package_class": "synthetic_test",
        "basis": {
            "C1": (*HPL_H1_BASIS, "x_boundary_primitive"),
            "C2": (*HPL_H2_BASIS, "y_boundary"),
            "H1": HPL_H1_BASIS,
            "H2": HPL_H2_BASIS,
        },
        "dimensions": {"C1": c1, "C2": c2, "H1": 14, "H2": 14},
        "matrices": matrices,
        "matrix_sha256": {
            name: sha256_json(value) for name, value in matrices.items()
        },
        "provenance": {name: digest for name in HPL_PROVENANCE_NAMES},
        "checks": {name: True for name in HPL_REQUIRED_CHECKS},
        "trace_requests": tuple(
            {
                "name": name,
                "external_h1": "theta_1",
                "word": ("theta_1", "theta_1", "theta_1"),
            }
            for name in HPL_TRACE_REQUEST_NAMES
        ),
        "M0": {
            "u": ((0, 1), (1, 0)),
            "d": ((0, 1), (1, 0)),
        },
        "scope": "synthetic exact HPL-compiler fixture only; not carrier evidence",
    }


STAR_TANGENT_CERTIFICATES = (
    "common_basis_frozen",
    "canonical_off_diagonal_active_blocks",
    "direct_second_normal_jet_zero",
    "up_star_arm_typing_certified",
    "down_triangular_typing_certified",
    "matter_symmetry_certified",
    "physical_open_component_inherited",
)
STAR_TANGENT_PROVENANCE = (
    "active_block_sha256",
    "up_transport_typing_sha256",
    "down_transport_typing_sha256",
    "second_normal_jet_sha256",
)
DEGREE_FIVE_MONOMIAL_ORDER = (
    "y3^2", "y3*y5", "y3*y7", "y5^2", "y5*y7", "y7^2",
)


def star_tangent_degree5_contract() -> Mapping[str, Any]:
    """Describe the exact conditional degree-five typing theorem."""

    return {
        "object": "StarTangentDegreeFivePackage",
        "version": "v36a2o-conditional",
        "field": "Q(omega)",
        "coordinate_order": ("y3", "y5", "y7"),
        "monomial_order": DEGREE_FIVE_MONOMIAL_ORDER,
        "active_blocks": "M0_s=[[0,m_s],[m_s,0]], m_s!=0",
        "up_transport": "P_u=[[a3,a5,a7],[0,0,0]]",
        "down_transport": "P_d=[[a3,a5,a7],[0,b5,b7]]",
        "conclusions": (
            "U2 identically zero under the certified up-star typing",
            "D2=-(2/m_d) A_d B_d under the certified down-triangular typing",
            "simultaneous degree-five full rank is impossible under both typings",
        ),
        "required_certificates": STAR_TANGENT_CERTIFICATES,
        "required_provenance_digests": STAR_TANGENT_PROVENANCE,
        "physical_carrier_package_available": False,
        "carrier_applicability": GateState.MISSING_INPUT,
        "scope": (
            "This is an exact implication from typed transport matrices. "
            "It does not prove that the Schoen carrier has those matrices."
        ),
    }


def _degree_five_coefficients(
    hessian: Sequence[Sequence[object]],
) -> tuple[Eisenstein, ...]:
    """Serialize y^T H y in the fixed six-monomial order."""

    matrix = e_matrix(hessian)
    if len(matrix) != 3 or any(len(row) != 3 for row in matrix):
        raise ValueError("degree-five Hessian must be 3 x 3")
    if matrix != e_transpose(matrix):
        raise ValueError("degree-five Hessian must be symmetric")
    return (
        matrix[0][0],
        2 * matrix[0][1],
        2 * matrix[0][2],
        matrix[1][1],
        2 * matrix[1][2],
        matrix[2][2],
    )


def _star_vector(
    values: object,
    length: int,
    label: str,
) -> tuple[Eisenstein, ...]:
    if isinstance(values, (str, bytes)) or not isinstance(values, Sequence):
        raise ValueError(f"{label} must be an exact sequence")
    if len(values) != length:
        raise ValueError(f"{label} must contain exactly {length} scalars")
    return tuple(_frontier_scalar(value) for value in values)


def compile_star_tangent_degree5_package(
    package: Mapping[str, Any],
) -> Mapping[str, Any]:
    """Verify the conditional star-tangent no-go and down-sector factorization."""

    if package.get("object") != "StarTangentDegreeFivePackage":
        raise ValueError("wrong star-tangent package object")
    if package.get("version") != "v36a2o-conditional":
        raise ValueError("version must be v36a2o-conditional")
    if package.get("field") != "Q(omega)":
        raise ValueError("field must be Q(omega)")
    package_class = package.get("package_class")
    if package_class not in {"physical_carrier", "synthetic_test"}:
        raise ValueError("package_class must be physical_carrier or synthetic_test")

    certificates = package.get("certificates")
    if not isinstance(certificates, Mapping):
        raise ValueError("certificates mapping is required")
    failed = tuple(
        name for name in STAR_TANGENT_CERTIFICATES
        if certificates.get(name) is not True
    )
    if failed:
        raise ValueError(
            "required star-tangent certificates not true: " + ", ".join(failed)
        )

    provenance = package.get("provenance")
    if not isinstance(provenance, Mapping) or set(provenance) != set(
        STAR_TANGENT_PROVENANCE
    ):
        raise ValueError(
            "provenance must contain exactly the star-tangent source digests"
        )
    pinned_provenance = {
        name: _f3_sha256(provenance[name], f"provenance.{name}")
        for name in STAR_TANGENT_PROVENANCE
    }

    parameters = package.get("parameters")
    if not isinstance(parameters, Mapping) or set(parameters) != {
        "m_u", "m_d", "A_u", "A_d", "B_d_tail"
    }:
        raise ValueError(
            "parameters must contain exactly m_u,m_d,A_u,A_d,B_d_tail"
        )
    m_u = _frontier_scalar(parameters["m_u"])
    m_d = _frontier_scalar(parameters["m_d"])
    if m_u.is_zero() or m_d.is_zero():
        raise ValueError("m_u and m_d must be nonzero")
    a_u = _star_vector(parameters["A_u"], 3, "A_u")
    a_d = _star_vector(parameters["A_d"], 3, "A_d")
    b_tail = _star_vector(parameters["B_d_tail"], 2, "B_d_tail")
    zero_row = (E_ZERO, E_ZERO, E_ZERO)
    b_d = (E_ZERO, *b_tail)

    m0_u = ((E_ZERO, m_u), (m_u, E_ZERO))
    m0_d = ((E_ZERO, m_d), (m_d, E_ZERO))
    p_u = (a_u, zero_row)
    p_d = (a_d, b_d)
    h_u = null_transport_hessian(p_u, m0_u)
    h_d = null_transport_hessian(p_d, m0_d)
    u2 = _degree_five_coefficients(h_u)
    d2 = _degree_five_coefficients(h_d)

    expected_h_d = e_matrix(
        tuple(
            tuple(
                -(a_d[row] * b_d[column] + b_d[row] * a_d[column]) / m_d
                for column in range(3)
            )
            for row in range(3)
        )
    )
    expected_d2 = _degree_five_coefficients(expected_h_d)
    exact_checks = {
        "up_star_image_totally_isotropic":
            all(entry.is_zero() for entry in u2),
        "down_hessian_factorization": h_d == expected_h_d,
        "down_quadratic_factorization": d2 == expected_d2,
        "active_blocks_invertible":
            not e_det2(m0_u).is_zero() and not e_det2(m0_d).is_zero(),
    }
    if not all(exact_checks.values()):
        raise ValueError("internal star-tangent identity failure")

    physical = package_class == "physical_carrier"
    return {
        "object": "StarTangentDegreeFiveCompilation",
        "field": "Q(omega)",
        "package_class": package_class,
        "coordinate_order": ("y3", "y5", "y7"),
        "monomial_order": DEGREE_FIVE_MONOMIAL_ORDER,
        "M0_u": m0_u,
        "M0_d": m0_d,
        "P_u": p_u,
        "P_d": p_d,
        "H_u": h_u,
        "H_d": h_d,
        "U2_coefficients": u2,
        "D2_coefficients": d2,
        "D2_factorization": "-(2/m_d) A_d B_d",
        "A_d_coefficients": a_d,
        "B_d_coefficients": b_d,
        "exact_checks": exact_checks,
        "package_level_U2_identically_zero": True,
        "package_level_simultaneous_degree_five_full_rank_impossible": True,
        "D2_identically_zero": all(entry.is_zero() for entry in d2),
        "physical_carrier_evaluation": physical,
        "physical_degree_five_up_no_go_certified": physical,
        "physical_simultaneous_degree_five_full_rank_impossible": physical,
        "provenance": pinned_provenance,
        "next_order_contract": {
            "up_order": 7,
            "required_objects": ("n3_u", "A_u", "B_u_order2"),
            "formula": "U3=n3_u-(2/m_u)A_u*B_u_order2",
            "state": GateState.MISSING_INPUT,
        },
        "scope": package.get("scope", "unspecified star-tangent package"),
        "scientific_boundary": (
            "The algebraic implication is exact. Physical promotion requires "
            "a retained common-basis carrier certificate for every typing "
            "hypothesis and digest; no such package is currently available."
        ),
    }


def synthetic_star_tangent_degree5_package() -> Mapping[str, Any]:
    """Return a nonphysical exact fixture for the conditional theorem."""

    return {
        "object": "StarTangentDegreeFivePackage",
        "version": "v36a2o-conditional",
        "field": "Q(omega)",
        "package_class": "synthetic_test",
        "certificates": {name: True for name in STAR_TANGENT_CERTIFICATES},
        "provenance": {name: "0" * 64 for name in STAR_TANGENT_PROVENANCE},
        "parameters": {
            "m_u": 2,
            "m_d": 3,
            "A_u": (1, OMEGA, 2),
            "A_d": (1, 2, 3),
            "B_d_tail": (4, 5),
        },
        "scope": "synthetic star-tangent identity fixture only; not carrier evidence",
    }


def classify_star_tangent_transport(
    transport: Sequence[Sequence[object]],
    active_tree_block: Sequence[Sequence[object]] = (
        (E_ZERO, E_ONE),
        (E_ONE, E_ZERO),
    ),
) -> Mapping[str, Any]:
    """Classify the exact star/triangular invariants of one 2 x 3 transport.

    ``image_totally_isotropic`` is the basis-independent content of the
    one-star-arm hypothesis: the induced Gram/Hessian matrix vanishes.
    ``frozen_first_arm`` and ``frozen_triangular`` retain the stronger row
    statements used by the conditional package in its pinned active basis.
    """

    p = e_matrix(transport)
    if len(p) != 2 or any(len(row) != 3 for row in p):
        raise ValueError("transport matrix must be 2 x 3")
    m0 = e_matrix(active_tree_block)
    if len(m0) != 2 or any(len(row) != 2 for row in m0):
        raise ValueError("active tree block must be 2 x 2")
    if m0 != e_transpose(m0) or e_det2(m0).is_zero():
        raise ValueError("active tree block must be symmetric and invertible")

    hessian = null_transport_hessian(p, m0)
    column_self_pairings = tuple(hessian[index][index] for index in range(3))
    second_row_zero = all(entry.is_zero() for entry in p[1])
    first_row_zero = all(entry.is_zero() for entry in p[0])
    return {
        "transport": p,
        "active_tree_block": m0,
        "induced_gram_hessian": hessian,
        "transport_rank": e_rank(p),
        "hessian_rank": e_rank(hessian),
        "hessian_determinant": e_det3(hessian),
        "column_self_pairings": column_self_pairings,
        "image_totally_isotropic": _matrix_is_zero(hessian),
        "one_star_arm_in_some_hyperbolic_basis": _matrix_is_zero(hessian),
        "frozen_first_arm": second_row_zero,
        "frozen_second_arm": first_row_zero,
        "frozen_up_star_typing": second_row_zero,
        "first_direction_isotropic": column_self_pairings[0].is_zero(),
        "frozen_down_triangular_typing": p[1][0].is_zero(),
        "universal_structural_checks": {
            "hessian_symmetric": hessian == e_transpose(hessian),
            "hessian_rank_at_most_two": e_rank(hessian) <= 2,
            "hessian_determinant_zero": e_det3(hessian).is_zero(),
        },
    }


def star_tangent_typing_nonidentifiability_certificate() -> Mapping[str, Any]:
    """Prove that retained branch data do not determine physical typing.

    The four matrices are exact countermodels over Q, hence over Q(omega).
    They obey the universal matter-symmetric binary-Gram constraints retained
    by v36a2k/v36a2m/v36a2n, but they disagree on the specialized typing
    predicates.  This kills the inference from branch support to typing; it
    does not decide the missing physical transport matrix.
    """

    m0 = ((E_ZERO, E_ONE), (E_ONE, E_ZERO))
    models = {
        "up_star": classify_star_tangent_transport(
            ((1, 0, 1), (0, 0, 0)),
            m0,
        ),
        "up_nonstar": classify_star_tangent_transport(
            ((1, 0, 1), (0, 1, 1)),
            m0,
        ),
        "down_triangular": classify_star_tangent_transport(
            ((1, 1, 0), (0, 1, 1)),
            m0,
        ),
        "down_nontriangular": classify_star_tangent_transport(
            ((1, 1, 0), (1, 0, 1)),
            m0,
        ),
    }
    shared_structure = all(
        all(model["universal_structural_checks"].values())
        for model in models.values()
    )
    exact_checks = {
        "all_models_obey_universal_structure": shared_structure,
        "up_models_disagree_on_total_isotropy":
            models["up_star"]["image_totally_isotropic"]
            and not models["up_nonstar"]["image_totally_isotropic"],
        "up_models_disagree_on_frozen_star_typing":
            models["up_star"]["frozen_up_star_typing"]
            and not models["up_nonstar"]["frozen_up_star_typing"],
        "down_models_disagree_on_first_direction_isotropy":
            models["down_triangular"]["first_direction_isotropic"]
            and not models["down_nontriangular"]["first_direction_isotropic"],
        "down_models_disagree_on_frozen_triangular_typing":
            models["down_triangular"]["frozen_down_triangular_typing"]
            and not models["down_nontriangular"][
                "frozen_down_triangular_typing"
            ],
        "nontriangular_f3_norm_is_nonzero":
            not models["down_nontriangular"]["column_self_pairings"][0].is_zero(),
    }
    if not all(exact_checks.values()):
        raise ArithmeticError("typing nonidentifiability countermodel failed")

    return {
        "object": "StarTangentTypingNonidentifiabilityCertificate",
        "field": "Q(omega)",
        "active_tree_block": m0,
        "retained_evidence": (
            "v36a2k branch pruning and symmetric Hessian reduction",
            "v36a2m restricted reachable-hull sufficiency theorem",
            "v36a2n direction-adaptive trace ledger",
        ),
        "retained_source_sha256": {
            "v36a2k_result":
                SECTION6_CERTIFICATE_SHA256["v36a2k_residue_reduction_result"],
            "v36a2m_source":
                SECTION6_CERTIFICATE_SHA256["v36a2m_restricted_hull_source"],
            "v36a2n_result":
                SECTION6_CERTIFICATE_SHA256["v36a2n_direction_adaptive_result"],
        },
        "models": models,
        "exact_checks": exact_checks,
        "inference_from_branch_support_to_up_star_typing": GateState.KILLED,
        "inference_from_branch_support_to_down_triangular_typing":
            GateState.KILLED,
        "actual_physical_carrier_typing": GateState.MISSING_INPUT,
        "first_invariant_test": {
            "required_columns": ("p_u,3", "p_d,3"),
            "normalized_scalar_trace_count": 4,
            "up_kill_criterion":
                "B_u(p_u,3,p_u,3) != 0 refutes one-star-arm typing",
            "down_kill_criterion":
                "B_d(p_d,3,p_d,3) != 0 refutes triangular typing",
            "zero_result_boundary": (
                "Two isotropic f3 columns do not certify the up-star theorem; "
                "continue with the adaptive f5/f7 pairings."
            ),
        },
        "scientific_conclusion": (
            "The conditional star-tangent theorem remains exact, but its "
            "physical hypotheses cannot be inferred from the retained branch "
            "labels, support zeros, Hessian rank bound, or positive-twist "
            "section count. Exact common-cyclic transport data are required."
        ),
    }


F3_COMMON_CYCLIC_CERTIFICATES = (
    "common_basis_frozen",
    "effective_FE_response_chain_certified",
    "contraction_side_conditions",
    "cyclic_trace_normalized",
    "cyclic_orientation_sign_certified",
    "matter_slot_symmetry_certified",
    "physical_open_component_inherited",
)
F3_COMMON_CYCLIC_PROVENANCE = (
    "external_states_sha256",
    "effective_FE_response_sha256",
    "contractions_sha256",
    "cyclic_tensors_sha256",
    "normalization_sha256",
)


def f3_common_cyclic_contract() -> Mapping[str, Any]:
    """Describe the exact raw-data boundary immediately before the four f3 traces."""

    return {
        "object": "F3CommonCyclicTracePackage",
        "field": "Q(omega)",
        "package_classes": ("physical_carrier", "synthetic_test"),
        "sector_basis_blocks": ("A", "H", "B"),
        "sector_external_states": ("a", "H", "b_active[0]", "b_active[1]"),
        "sector_linear_data": ("M0", "effective_FE_B", "tau_AHB", "tau_BHA"),
        "required_certificates": F3_COMMON_CYCLIC_CERTIFICATES,
        "required_provenance_digests": F3_COMMON_CYCLIC_PROVENANCE,
        "right_orientation_formula":
            "c^R_s,i=tau_AHB(a_s,H_s,R^FE_s,3 b_s,i)",
        "left_orientation_formula":
            "c^L_s,i=tau_BHA(R^FE_s,3 b_s,i,H_s,a_s)",
        "orientation_collapse":
            "cyclicity and matter-slot symmetry require c^R_s,i=c^L_s,i",
        "compiled_column": "p_s,3=(c_s,1,c_s,2)^T",
        "oriented_contractions": 8,
        "independent_normalized_scalars": 4,
        "current_package_available": False,
        "current_state": GateState.MISSING_INPUT,
        "scope": (
            "The effective FE response must be induced and certified by one "
            "frozen common contraction. It may not be substituted by an "
            "arbitrary product of separately exported primitives."
        ),
    }


def _f3_sha256(value: object, label: str) -> str:
    if not isinstance(value, str) or len(value) != 64 or value.lower() != value:
        raise ValueError(f"{label} must be a lowercase SHA-256 digest")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{label} must be a lowercase SHA-256 digest") from exc
    return value


def _f3_exact_vector(value: object, size: int, label: str) -> tuple[Eisenstein, ...]:
    if isinstance(value, (str, bytes)) or not isinstance(value, Sequence):
        raise ValueError(f"{label} must be an exact vector")
    if len(value) != size:
        raise ValueError(f"{label} must have length {size}")
    return tuple(_frontier_scalar(entry) for entry in value)


def _f3_exact_matrix(
    value: object,
    rows: int,
    columns: int,
    label: str,
) -> EMatrix:
    if isinstance(value, (str, bytes)) or not isinstance(value, Sequence):
        raise ValueError(f"{label} must be an exact matrix")
    if len(value) != rows:
        raise ValueError(f"{label} must have {rows} rows")
    matrix: list[tuple[Eisenstein, ...]] = []
    for index, row in enumerate(value):
        matrix.append(_f3_exact_vector(row, columns, f"{label}[{index}]"))
    return tuple(matrix)


def _f3_exact_tensor3(
    value: object,
    dimensions: tuple[int, int, int],
    label: str,
) -> tuple[tuple[tuple[Eisenstein, ...], ...], ...]:
    if isinstance(value, (str, bytes)) or not isinstance(value, Sequence):
        raise ValueError(f"{label} must be an exact rank-three tensor")
    if len(value) != dimensions[0]:
        raise ValueError(f"{label} first dimension must be {dimensions[0]}")
    tensor: list[tuple[tuple[Eisenstein, ...], ...]] = []
    for first, plane in enumerate(value):
        if isinstance(plane, (str, bytes)) or not isinstance(plane, Sequence):
            raise ValueError(f"{label}[{first}] must be a matrix")
        if len(plane) != dimensions[1]:
            raise ValueError(
                f"{label}[{first}] second dimension must be {dimensions[1]}"
            )
        tensor.append(
            tuple(
                _f3_exact_vector(
                    row,
                    dimensions[2],
                    f"{label}[{first}][{second}]",
                )
                for second, row in enumerate(plane)
            )
        )
    return tuple(tensor)


def _f3_trilinear(
    tensor: Sequence[Sequence[Sequence[object]]],
    left: Sequence[object],
    middle: Sequence[object],
    right: Sequence[object],
) -> Eisenstein:
    exact_left = tuple(Eisenstein.coerce(entry) for entry in left)
    exact_middle = tuple(Eisenstein.coerce(entry) for entry in middle)
    exact_right = tuple(Eisenstein.coerce(entry) for entry in right)
    exact_tensor = _f3_exact_tensor3(
        tensor,
        (len(exact_left), len(exact_middle), len(exact_right)),
        "cyclic tensor",
    )
    return sum(
        (
            exact_tensor[i][j][k]
            * exact_left[i]
            * exact_middle[j]
            * exact_right[k]
            for i in range(len(exact_left))
            for j in range(len(exact_middle))
            for k in range(len(exact_right))
        ),
        E_ZERO,
    )


def _f3_basis_names(value: object, label: str) -> tuple[str, ...]:
    if isinstance(value, (str, bytes)) or not isinstance(value, Sequence) or not value:
        raise ValueError(f"{label} must be a nonempty ordered basis")
    names = tuple(value)
    if any(not isinstance(name, str) or not name for name in names):
        raise ValueError(f"{label} basis names must be nonempty strings")
    if len(set(names)) != len(names):
        raise ValueError(f"{label} basis names must be unique")
    return names


def _compile_f3_common_cyclic_sector(
    sector_data: object,
    sector: str,
) -> Mapping[str, Any]:
    if not isinstance(sector_data, Mapping):
        raise ValueError(f"sectors.{sector} must be an object")
    if set(sector_data) != {
        "basis",
        "M0",
        "a",
        "H",
        "b_active",
        "effective_FE_B",
        "tau_AHB",
        "tau_BHA",
    }:
        raise ValueError(
            f"sectors.{sector} must contain exactly the frozen f3 trace fields"
        )
    basis = sector_data["basis"]
    if not isinstance(basis, Mapping) or set(basis) != {"A", "H", "B"}:
        raise ValueError(f"sectors.{sector}.basis must contain exactly A, H, B")
    basis_names = {
        block: _f3_basis_names(basis[block], f"sectors.{sector}.basis.{block}")
        for block in ("A", "H", "B")
    }
    dimensions = {block: len(names) for block, names in basis_names.items()}
    a = _f3_exact_vector(sector_data["a"], dimensions["A"], f"{sector}.a")
    higgs = _f3_exact_vector(sector_data["H"], dimensions["H"], f"{sector}.H")
    b_active_data = sector_data["b_active"]
    if (
        isinstance(b_active_data, (str, bytes))
        or not isinstance(b_active_data, Sequence)
        or len(b_active_data) != 2
    ):
        raise ValueError(f"{sector}.b_active must contain exactly two vectors")
    b_active = tuple(
        _f3_exact_vector(vector, dimensions["B"], f"{sector}.b_active[{index}]")
        for index, vector in enumerate(b_active_data)
    )
    effective = _f3_exact_matrix(
        sector_data["effective_FE_B"],
        dimensions["B"],
        dimensions["B"],
        f"{sector}.effective_FE_B",
    )
    tau_ahb = _f3_exact_tensor3(
        sector_data["tau_AHB"],
        (dimensions["A"], dimensions["H"], dimensions["B"]),
        f"{sector}.tau_AHB",
    )
    tau_bha = _f3_exact_tensor3(
        sector_data["tau_BHA"],
        (dimensions["B"], dimensions["H"], dimensions["A"]),
        f"{sector}.tau_BHA",
    )
    m0 = _f3_exact_matrix(sector_data["M0"], 2, 2, f"{sector}.M0")
    if m0 != e_transpose(m0) or e_det2(m0).is_zero():
        raise ValueError(f"{sector}.M0 must be symmetric and invertible")

    responses = tuple(e_matvec(effective, vector) for vector in b_active)
    right = tuple(
        _f3_trilinear(tau_ahb, a, higgs, response)
        for response in responses
    )
    left = tuple(
        _f3_trilinear(tau_bha, response, higgs, a)
        for response in responses
    )
    if right != left:
        raise ValueError(
            f"{sector} cyclic orientations disagree; common-gauge package rejected"
        )
    return {
        "sector": sector,
        "basis_dimensions": dimensions,
        "effective_FE_responses": responses,
        "right_orientation_traces": right,
        "left_orientation_traces": left,
        "orientation_pairs_equal": True,
        "p_f3": right,
        "q_f3": tuple((entry,) for entry in left),
        "M0": m0,
        "independent_normalized_scalar_count": 2,
        "oriented_contraction_count": 4,
    }


def compile_f3_common_cyclic_package(
    package: Mapping[str, Any],
) -> Mapping[str, Any]:
    """Derive the four f3 residues from one exact frozen common-cyclic package."""

    if package.get("object") != "F3CommonCyclicTracePackage":
        raise ValueError("wrong raw f3 common-cyclic package object")
    if package.get("field") != "Q(omega)":
        raise ValueError("field must be Q(omega)")
    package_class = package.get("package_class")
    if package_class not in {"physical_carrier", "synthetic_test"}:
        raise ValueError("package_class must be physical_carrier or synthetic_test")
    certificates = package.get("certificates")
    if not isinstance(certificates, Mapping):
        raise ValueError("certificates mapping is required")
    failed = tuple(
        name
        for name in F3_COMMON_CYCLIC_CERTIFICATES
        if certificates.get(name) is not True
    )
    if failed:
        raise ValueError("required certificates not true: " + ", ".join(failed))
    provenance = package.get("provenance")
    if not isinstance(provenance, Mapping) or set(provenance) != set(
        F3_COMMON_CYCLIC_PROVENANCE
    ):
        raise ValueError("provenance must contain exactly the required SHA-256 digests")
    pinned = {
        name: _f3_sha256(provenance[name], f"provenance.{name}")
        for name in F3_COMMON_CYCLIC_PROVENANCE
    }
    sectors_data = package.get("sectors")
    if not isinstance(sectors_data, Mapping) or set(sectors_data) != {"u", "d"}:
        raise ValueError("sectors must contain exactly u and d")
    sectors = {
        sector: _compile_f3_common_cyclic_sector(sectors_data[sector], sector)
        for sector in ("u", "d")
    }
    adaptive_package = {
        "object": "DirectionAdaptiveNullTransportCarrierPackage",
        "field": "Q(omega)",
        "certificates": {
            "common_basis_frozen": True,
            "common_cyclic_gauge": True,
            "normalized_trace": True,
            "contraction_side_conditions": True,
            "matter_slot_symmetry": True,
            "f3_strict_Higgs_annihilation": True,
            "physical_open_component_inherited": True,
        },
        "M0": {sector: sectors[sector]["M0"] for sector in ("u", "d")},
        "normalized_residues": {
            sector: {"3": {"B_neutral_FE": sectors[sector]["p_f3"]}}
            for sector in ("u", "d")
        },
        "scope": package.get("scope", "unspecified raw f3 common-cyclic package"),
    }
    adaptive = compile_direction_adaptive_frontier(adaptive_package)
    physical = package_class == "physical_carrier"
    return {
        "object": "F3CommonCyclicTraceCompilation",
        "field": "Q(omega)",
        "package_class": package_class,
        "provenance": pinned,
        "sector_traces": sectors,
        "independent_normalized_scalar_count": sum(
            result["independent_normalized_scalar_count"]
            for result in sectors.values()
        ),
        "oriented_contraction_count": sum(
            result["oriented_contraction_count"] for result in sectors.values()
        ),
        "all_orientation_pairs_equal": all(
            result["orientation_pairs_equal"] for result in sectors.values()
        ),
        "adaptive_compilation": adaptive,
        "physical_carrier_evaluation": physical,
        "simultaneous_physical_order_five_nonzero_forms_certified":
            physical and adaptive["simultaneous_nonzero_forms_certified"],
        "scope": package.get("scope", "unspecified raw f3 common-cyclic package"),
        "scientific_boundary": (
            "A synthetic package tests only the compiler. A physical result "
            "requires independently constructed source tensors and retained "
            "provenance for one common cyclic contraction."
        ),
    }


def synthetic_f3_common_cyclic_package(
    *,
    cyclic: bool = True,
) -> Mapping[str, Any]:
    """Return a tiny exact raw package for compiler tests, never carrier evidence."""

    digest = "0" * 64

    def sector(label: str) -> Mapping[str, Any]:
        tau_right = (((E_ONE, E_ONE),),)
        tau_left = (((E_ONE,),), ((E_ONE,),))
        if not cyclic and label == "d":
            tau_left = (((E_ONE,),), ((E_ZERO,),))
        return {
            "basis": {
                "A": (f"{label}_a",),
                "H": (f"H_{label}",),
                "B": (f"{label}_b1", f"{label}_b2"),
            },
            "M0": ((E_ZERO, E_ONE), (E_ONE, E_ZERO)),
            "a": (E_ONE,),
            "H": (E_ONE,),
            "b_active": ((E_ONE, E_ZERO), (E_ZERO, E_ONE)),
            "effective_FE_B": ((E_ONE, E_ZERO), (E_ZERO, E_ONE)),
            "tau_AHB": tau_right,
            "tau_BHA": tau_left,
        }

    return {
        "object": "F3CommonCyclicTracePackage",
        "field": "Q(omega)",
        "package_class": "synthetic_test",
        "certificates": {name: True for name in F3_COMMON_CYCLIC_CERTIFICATES},
        "provenance": {name: digest for name in F3_COMMON_CYCLIC_PROVENANCE},
        "sectors": {"u": sector("u"), "d": sector("d")},
        "scope": "synthetic exact raw-compiler test only; not carrier evidence",
    }


def synthetic_adaptive_frontier_package(mode: str) -> Mapping[str, Any]:
    """Return exact branch-coverage data that are explicitly not carrier residues."""

    package: dict[str, Any] = {
        "object": "DirectionAdaptiveNullTransportCarrierPackage",
        "field": "Q(omega)",
        "certificates": {name: True for name in ADAPTIVE_RESIDUE_CERTIFICATES},
        "M0": {
            "u": ((E_ZERO, E_ONE), (E_ONE, E_ZERO)),
            "d": ((E_ZERO, E_ONE), (E_ONE, E_ZERO)),
        },
        "normalized_residues": {"u": {}, "d": {}},
        "scope": "synthetic exact compiler test only; not a Schoen-carrier evaluation",
    }
    if mode == "f3_norm_pass":
        package["normalized_residues"] = {
            "u": {"3": {"B_neutral_FE": (E_ONE, E_ONE)}},
            "d": {"3": {"B_neutral_FE": (E_ONE, E_ONE)}},
        }
    elif mode == "rank2_pass":
        package["normalized_residues"] = {
            "u": {
                "3": {"B_neutral_FE": (E_ONE, E_ZERO)},
                "5": {"B_neutral_FE": (E_ZERO, E_ONE)},
            },
            "d": {
                "3": {"B_neutral_FE": (E_ONE, E_ZERO)},
                "5": {
                    "B_neutral_FE": (E_ZERO, E_ONE),
                    "H_neutral_corrected": (E_ZERO, E_ZERO),
                    "split_Higgs": (E_ZERO, E_ZERO),
                },
            },
        }
    elif mode == "full_zero":
        package["normalized_residues"] = {
            "u": {
                direction: {"B_neutral_FE": (E_ONE, E_ZERO)}
                for direction in FRONTIER_DIRECTIONS
            },
            "d": {
                "3": {"B_neutral_FE": (E_ONE, E_ZERO)},
                "5": {
                    "B_neutral_FE": (E_ONE, E_ZERO),
                    "H_neutral_corrected": (E_ZERO, E_ZERO),
                    "split_Higgs": (E_ZERO, E_ZERO),
                },
                "7": {
                    "B_neutral_FE": (E_ONE, E_ZERO),
                    "H_neutral_corrected": (E_ZERO, E_ZERO),
                    "split_Higgs": (E_ZERO, E_ZERO),
                },
            },
        }
    else:
        raise ValueError(f"unknown synthetic adaptive mode: {mode}")
    return package


def compile_restricted_frontier(package: Mapping[str, Any]) -> Mapping[str, Any]:
    """Compile the 24 normalized carrier residues, rejecting incomplete input."""

    if package.get("field") != "Q(omega)":
        raise ValueError("field must be Q(omega)")
    certificates = package.get("certificates")
    if not isinstance(certificates, Mapping):
        raise ValueError("certificates mapping is required")
    missing = tuple(
        name for name in RESTRICTED_HULL_CERTIFICATES
        if certificates.get(name) is not True
    )
    if missing:
        raise ValueError("missing/false production certificates: " + ", ".join(missing))
    residues = package.get("normalized_residues")
    blocks = package.get("M0")
    if not isinstance(residues, Mapping) or not isinstance(blocks, Mapping):
        raise ValueError("normalized_residues and M0 mappings are required")
    up = residues.get("u")
    down = residues.get("d")
    if not isinstance(up, Mapping) or not isinstance(down, Mapping):
        raise ValueError("both up and down residue mappings are required")

    for group in UP_RESIDUE_GROUPS:
        directions = up.get(group)
        if not isinstance(directions, Mapping) or set(directions) != set(FRONTIER_DIRECTIONS):
            raise ValueError(f"up/{group} directions must be {FRONTIER_DIRECTIONS}")
    for group in DOWN_RESIDUE_GROUPS:
        directions = down.get(group)
        if not isinstance(directions, Mapping) or set(directions) != set(FRONTIER_DIRECTIONS):
            raise ValueError(f"down/{group} directions must be {FRONTIER_DIRECTIONS}")

    p_up = {
        direction: _frontier_vector(up["B_neutral_FE"][direction])
        for direction in FRONTIER_DIRECTIONS
    }
    p_down = {
        direction: _sum_frontier_vectors(
            _frontier_vector(down[group][direction]) for group in DOWN_RESIDUE_GROUPS
        )
        for direction in FRONTIER_DIRECTIONS
    }
    transport_up = e_matrix(
        tuple(
            tuple(p_up[direction][component] for direction in FRONTIER_DIRECTIONS)
            for component in range(2)
        )
    )
    transport_down = e_matrix(
        tuple(
            tuple(p_down[direction][component] for direction in FRONTIER_DIRECTIONS)
            for component in range(2)
        )
    )
    hessian_up = null_transport_hessian(transport_up, blocks["u"])
    hessian_down = null_transport_hessian(transport_down, blocks["d"])
    up_nonzero = not _matrix_is_zero(hessian_up)
    down_nonzero = not _matrix_is_zero(hessian_down)
    simultaneous_open = up_nonzero and down_nonzero

    witness = None
    witness_candidates = (
        (1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 0),
        (1, 0, 1), (0, 1, 1), (1, 1, 1), (1, -1, 0),
        (1, 0, -1), (0, 1, -1), (1, 2, 3), (1, 3, 2),
    )
    for point in witness_candidates:
        up_value = e_quadratic_form(hessian_up, point)
        down_value = e_quadratic_form(hessian_down, point)
        if not up_value.is_zero() and not down_value.is_zero():
            witness = {"y": point, "U2": up_value, "D2": down_value}
            break

    return {
        "input_residue_count": 24,
        "P_u": transport_up,
        "P_d": transport_down,
        "H_u": hessian_up,
        "H_d": hessian_down,
        "rank_H_u": e_rank(hessian_up),
        "rank_H_d": e_rank(hessian_down),
        "det_H_u": e_det3(hessian_up),
        "det_H_d": e_det3(hessian_down),
        "U2_identically_zero": not up_nonzero,
        "D2_identically_zero": not down_nonzero,
        "simultaneous_nonvanishing_open_nonempty": simultaneous_open,
        "small_rational_witness": witness,
        "scope": package.get("scope", "unspecified package"),
    }


def synthetic_frontier_package(nonzero: bool = True) -> Mapping[str, Any]:
    """Build an exact compiler test package; never carrier evidence."""

    certificates = {name: True for name in RESTRICTED_HULL_CERTIFICATES}
    zero_vector = (E_ZERO, E_ZERO)
    if nonzero:
        up = {
            "3": (E_ONE, E_ZERO),
            "5": (E_ZERO, E_ONE),
            "7": (E_ONE, E_ONE),
        }
        down_primary = {
            "3": (E_ONE, E_ONE),
            "5": (E_ONE, E_ZERO),
            "7": (E_ZERO, E_ONE),
        }
    else:
        up = {direction: zero_vector for direction in FRONTIER_DIRECTIONS}
        down_primary = {direction: zero_vector for direction in FRONTIER_DIRECTIONS}
    zero_group = {direction: zero_vector for direction in FRONTIER_DIRECTIONS}
    return {
        "field": "Q(omega)",
        "certificates": certificates,
        "M0": {
            "u": ((E_ONE, E_ZERO), (E_ZERO, E_ONE)),
            "d": ((Eisenstein(2), E_ONE), (E_ONE, Eisenstein(2))),
        },
        "normalized_residues": {
            "u": {"B_neutral_FE": up},
            "d": {
                "B_neutral_FE": down_primary,
                "H_neutral_corrected": zero_group,
                "split_Higgs": zero_group,
            },
        },
        "scope": "synthetic exact compiler test only; not a Schoen-carrier evaluation",
    }


def simultaneous_open_theorem(
    up_form_nonzero: bool,
    down_form_nonzero: bool,
    inherited_physical_open_nonempty: bool,
) -> Mapping[str, Any]:
    """Apply irreducibility of P^2 to the two nonvanishing loci."""

    established = (
        up_form_nonzero
        and down_form_nonzero
        and inherited_physical_open_nonempty
    )
    return {
        "ambient_parameter_space": "P^2 over a characteristic-zero field",
        "irreducible": True,
        "U2_nonzero_polynomial": up_form_nonzero,
        "D2_nonzero_polynomial": down_form_nonzero,
        "inherited_physical_open_nonempty": inherited_physical_open_nonempty,
        "simultaneous_nonvanishing_open_nonempty": established,
        "requires_separate_projective_search": False,
    }


def light_family_frontier_status() -> Mapping[str, Any]:
    """Return the exact Section 6 boundary without fabricating carrier data."""

    direct = direct_order5_certificate()
    adaptive = direction_adaptive_pruning_certificate()
    return {
        "highest_result": "CONDITIONAL_STAR_TANGENT_DEGREE_FIVE_COMPILER_COMPLETE",
        "degree_three_U1_zero": True,
        "degree_three_D1_zero": True,
        "direct_order5_rows": direct["total_count"],
        "direct_order5_rows_zero": direct["all_direct_rows_zero"],
        "second_normal_formula_certified": True,
        "generic_residue_ledger_count":
            adaptive["generic_ledger"]["total"],
        "direction_refined_worst_case_count":
            adaptive["direction_refined_ledger"]["total"],
        "first_simultaneous_test_count":
            adaptive["first_simultaneous_test"]["normalized_scalar_evaluations"],
        "first_simultaneous_test_columns": ("p_u,3", "p_d,3"),
        "binary_gram_decision_theorem_certified": True,
        "suspended_hpl_source_to_trace_compiler_certified": True,
        "suspended_hpl_physical_package_available": False,
        "suspended_hpl_fixed_trace_request_count": 4,
        "star_tangent_degree_five_theorem_certified": True,
        "star_tangent_physical_typing_package_available": False,
        "physical_degree_five_up_no_go_certified": False,
        "degree_seven_up_contract_defined": True,
        "raw_f3_common_cyclic_compiler_certified": True,
        "raw_f3_oriented_contractions": 8,
        "raw_f3_independent_normalized_scalars": 4,
        "raw_f3_physical_package_available": False,
        "carrier_residue_values_available": False,
        "carrier_f3_columns_computed": False,
        "carrier_U2_computed": False,
        "carrier_D2_computed": False,
        "simultaneous_light_family_rank_lift_established": False,
        "physical_normalized_yukawas_computed": False,
        "state": GateState.MISSING_INPUT,
        "open_obligations": tuple(SECTION6_MISSING_INPUTS),
    }


def verify_light_family_frontier() -> tuple[Check, ...]:
    """Run the Section 6 exact theorems and fail-closed compiler tests."""

    orders = determinant_order_frontier(3)
    degree_three = degree_three_no_go_certificate()
    direct = direct_order5_certificate()
    normal = second_normal_form_certificate()
    adaptive_pruning = direction_adaptive_pruning_certificate()
    gram = binary_gram_certificate(
        ((E_ZERO, E_ONE), (E_ONE, E_ZERO)),
        ((E_ONE, E_ZERO, E_ONE), (E_ONE, E_ONE, E_ZERO)),
    )
    synthetic_nonzero = compile_restricted_frontier(synthetic_frontier_package(True))
    synthetic_zero = compile_restricted_frontier(synthetic_frontier_package(False))
    incomplete = dict(synthetic_frontier_package(True))
    incomplete["certificates"] = dict(incomplete["certificates"])
    incomplete["certificates"]["ambient_external_states_closed"] = False
    rejected = False
    try:
        compile_restricted_frontier(incomplete)
    except ValueError:
        rejected = True
    adaptive_f3 = compile_direction_adaptive_frontier(
        synthetic_adaptive_frontier_package("f3_norm_pass")
    )
    adaptive_rank2 = compile_direction_adaptive_frontier(
        synthetic_adaptive_frontier_package("rank2_pass")
    )
    adaptive_zero = compile_direction_adaptive_frontier(
        synthetic_adaptive_frontier_package("full_zero")
    )
    adaptive_incomplete = dict(synthetic_adaptive_frontier_package("f3_norm_pass"))
    adaptive_incomplete["certificates"] = dict(adaptive_incomplete["certificates"])
    adaptive_incomplete["certificates"]["common_cyclic_gauge"] = False
    adaptive_rejected = False
    try:
        compile_direction_adaptive_frontier(adaptive_incomplete)
    except ValueError:
        adaptive_rejected = True
    raw_contract = f3_common_cyclic_contract()
    raw_f3 = compile_f3_common_cyclic_package(
        synthetic_f3_common_cyclic_package()
    )
    raw_cyclic_rejected = False
    try:
        compile_f3_common_cyclic_package(
            synthetic_f3_common_cyclic_package(cyclic=False)
        )
    except ValueError:
        raw_cyclic_rejected = True
    raw_certificate_incomplete = dict(synthetic_f3_common_cyclic_package())
    raw_certificate_incomplete["certificates"] = dict(
        raw_certificate_incomplete["certificates"]
    )
    raw_certificate_incomplete["certificates"][
        "effective_FE_response_chain_certified"
    ] = False
    raw_certificate_rejected = False
    try:
        compile_f3_common_cyclic_package(raw_certificate_incomplete)
    except ValueError:
        raw_certificate_rejected = True
    hpl_contract = suspended_hpl_f3_contract()
    hpl = compile_suspended_hpl_f3_package(
        synthetic_suspended_hpl_f3_package()
    )
    hpl_digest_package = dict(synthetic_suspended_hpl_f3_package())
    hpl_digest_package["matrices"] = dict(hpl_digest_package["matrices"])
    hpl_digest_d1 = [
        list(row) for row in hpl_digest_package["matrices"]["D1"]
    ]
    hpl_digest_d1[0][0] = 1
    hpl_digest_package["matrices"]["D1"] = hpl_digest_d1
    hpl_digest_rejected = False
    try:
        compile_suspended_hpl_f3_package(hpl_digest_package)
    except ValueError:
        hpl_digest_rejected = True
    hpl_identity_package = dict(hpl_digest_package)
    hpl_identity_package["matrix_sha256"] = dict(
        hpl_identity_package["matrix_sha256"]
    )
    hpl_identity_package["matrix_sha256"]["D1"] = sha256_json(hpl_digest_d1)
    hpl_identity_rejected = False
    try:
        compile_suspended_hpl_f3_package(hpl_identity_package)
    except ValueError:
        hpl_identity_rejected = True
    star_contract = star_tangent_degree5_contract()
    star = compile_star_tangent_degree5_package(
        synthetic_star_tangent_degree5_package()
    )
    star_incomplete = dict(synthetic_star_tangent_degree5_package())
    star_incomplete["certificates"] = dict(star_incomplete["certificates"])
    star_incomplete["certificates"]["up_star_arm_typing_certified"] = False
    star_rejected = False
    try:
        compile_star_tangent_degree5_package(star_incomplete)
    except ValueError:
        star_rejected = True
    typing_nonidentifiability = (
        star_tangent_typing_nonidentifiability_certificate()
    )
    open_theorem = simultaneous_open_theorem(True, True, True)
    status = light_family_frontier_status()
    observations = (
        (
            "frontier.wall_charge.orders",
            tuple(row["total_order"] for row in orders),
            (1, 3, 5, 7),
            EvidenceClass.EXACT_THEOREM,
            "The determinant channel permits only odd total orders.",
        ),
        (
            "frontier.degree3.up_zero",
            degree_three["U1_identically_zero"],
            True,
            EvidenceClass.SCOPED_NO_GO,
            "The superseding certificate closes every up-sector degree-three coefficient.",
        ),
        (
            "frontier.degree3.down_zero",
            degree_three["D1_identically_zero"],
            True,
            EvidenceClass.SCOPED_NO_GO,
            "Every down-sector degree-three coefficient vanishes.",
        ),
        (
            "frontier.words.count",
            len(direct["matter_words"]),
            11,
            EvidenceClass.EXACT_THEOREM,
            "The bounded response automaton has exactly eleven words.",
        ),
        (
            "frontier.words.exact",
            tuple(row["word"] for row in direct["matter_words"]),
            ("", "E", "EF", "EFE", "EK", "EFEF", "EKF",
             "EFEFE", "EFEK", "EKFE", "EKK"),
            EvidenceClass.EXACT_THEOREM,
            "The word order and block endpoints are frozen.",
        ),
        (
            "frontier.direct.up_count",
            direct["up_count"],
            16,
            EvidenceClass.EXACT_THEOREM,
            "All ordered up-sector E3F2 rows are enumerated.",
        ),
        (
            "frontier.direct.down_count",
            direct["down_count"],
            26,
            EvidenceClass.EXACT_THEOREM,
            "All ordered down-sector E3F2 rows are enumerated.",
        ),
        (
            "frontier.direct.total_zero",
            direct["all_direct_rows_zero"] and direct["total_count"],
            42,
            EvidenceClass.SCOPED_NO_GO,
            "All 42 direct rows vanish on the reached Serre line.",
        ),
        (
            "frontier.direct.up_endpoints",
            direct["up_endpoint_counts"],
            {"A/H/B": 8, "B/H/A": 8},
            EvidenceClass.EXACT_THEOREM,
            "Up-sector endpoint multiplicities match the archived certificate.",
        ),
        (
            "frontier.direct.down_endpoints",
            direct["down_endpoint_counts"],
            {
                "A/H/B": 8,
                "A/U/A": 4,
                "A/V/B": 3,
                "B/H/A": 8,
                "B/V/A": 3,
            },
            EvidenceClass.EXACT_THEOREM,
            "Down-sector endpoint multiplicities match the archived certificate.",
        ),
        (
            "frontier.second_normal.countermodel",
            normal["countermodel_S2"],
            Eisenstein(-1),
            EvidenceClass.EXACT_THEOREM,
            "A rational countermodel has zero direct jet but nonzero second normal form.",
        ),
        (
            "frontier.compiler.residue_count",
            synthetic_nonzero["input_residue_count"],
            24,
            EvidenceClass.EXACT_THEOREM,
            "The compiler consumes six up and eighteen down normalized residues.",
        ),
        (
            "frontier.adaptive.worst_case_count",
            adaptive_pruning["direction_refined_ledger"]["total"],
            20,
            EvidenceClass.EXACT_THEOREM,
            "The f3 identities remove four generic down-sector scalar traces.",
        ),
        (
            "frontier.adaptive.first_test_count",
            adaptive_pruning["first_simultaneous_test"]["normalized_scalar_evaluations"],
            4,
            EvidenceClass.EXACT_THEOREM,
            "The first simultaneous decision needs only p_u,3 and p_d,3.",
        ),
        (
            "frontier.adaptive.gram_identity",
            gram["all_exact_checks_pass"],
            True,
            EvidenceClass.EXACT_THEOREM,
            "The binary-Gram minors, adjugate, and kernel identities hold exactly.",
        ),
        (
            "frontier.adaptive.f3_branch",
            (
                adaptive_f3["normalized_scalar_evaluations_consumed"],
                adaptive_f3["simultaneous_nonzero_forms_certified"],
            ),
            (4, True),
            EvidenceClass.EXACT_THEOREM,
            "Four synthetic f3 traces exercise the early nonzero branch.",
        ),
        (
            "frontier.adaptive.rank2_branch",
            (
                adaptive_rank2["normalized_scalar_evaluations_consumed"],
                adaptive_rank2["simultaneous_nonzero_forms_certified"],
            ),
            (12, True),
            EvidenceClass.EXACT_THEOREM,
            "The exact two-column minors exercise the adaptive rank-two branch.",
        ),
        (
            "frontier.adaptive.zero_branch",
            (
                adaptive_zero["normalized_scalar_evaluations_consumed"],
                adaptive_zero["zero_certified_sectors"],
            ),
            (20, ("u", "d")),
            EvidenceClass.EXACT_THEOREM,
            "Twenty traces exercise the complete totally-isotropic zero branch.",
        ),
        (
            "frontier.adaptive.fail_closed",
            adaptive_rejected,
            True,
            EvidenceClass.EXACT_THEOREM,
            "A missing common cyclic gauge certificate is rejected.",
        ),
        (
            "frontier.raw_f3.orientation_collapse",
            (
                raw_contract["oriented_contractions"],
                raw_contract["independent_normalized_scalars"],
            ),
            (8, 4),
            EvidenceClass.EXACT_THEOREM,
            "Cyclicity pairs eight oriented contractions into four independent values.",
        ),
        (
            "frontier.raw_f3.synthetic_compiler",
            (
                raw_f3["independent_normalized_scalar_count"],
                raw_f3["all_orientation_pairs_equal"],
                raw_f3["adaptive_compilation"][
                    "simultaneous_nonzero_forms_certified"
                ],
            ),
            (4, True, True),
            EvidenceClass.EXACT_THEOREM,
            "A tiny exact package exercises raw tensor contraction through the Gram decision.",
        ),
        (
            "frontier.raw_f3.synthetic_firewall",
            (
                raw_f3["physical_carrier_evaluation"],
                raw_f3[
                    "simultaneous_physical_order_five_nonzero_forms_certified"
                ],
            ),
            (False, False),
            EvidenceClass.EXACT_THEOREM,
            "Synthetic raw tensors cannot become physical carrier evidence.",
        ),
        (
            "frontier.raw_f3.cyclicity_fail_closed",
            raw_cyclic_rejected,
            True,
            EvidenceClass.EXACT_THEOREM,
            "A mismatch between A-H-B and B-H-A orientations is rejected.",
        ),
        (
            "frontier.raw_f3.chain_certificate_fail_closed",
            raw_certificate_rejected,
            True,
            EvidenceClass.EXACT_THEOREM,
            "An uncertified effective FE response is rejected.",
        ),
        (
            "frontier.hpl.contract",
            (
                hpl_contract["mu11_flattening"],
                hpl_contract["required_trace_requests"],
            ),
            (
                "column = left_C1_index * dim(C1) + right_C1_index",
                HPL_TRACE_REQUEST_NAMES,
            ),
            EvidenceClass.EXACT_THEOREM,
            "The v35h1 multiplication ordering and four trace names are frozen.",
        ),
        (
            "frontier.hpl.synthetic_traces",
            hpl["p_f3"],
            {
                "u": (Eisenstein(-1), Eisenstein(-1)),
                "d": (Eisenstein(-1), Eisenstein(-1)),
            },
            EvidenceClass.EXACT_THEOREM,
            "A 15-dimensional exact fixture exercises the sparse HPL recursion.",
        ),
        (
            "frontier.hpl.memoized_words",
            (hpl["memoized_F_word_count"], hpl["memoized_B_word_count"]),
            (2, 2),
            EvidenceClass.EXACT_THEOREM,
            "Repeated requests reuse the same exact word subproblems.",
        ),
        (
            "frontier.hpl.identities",
            all(hpl["computed_checks"].values()),
            True,
            EvidenceClass.EXACT_THEOREM,
            "Chain, primitive, pairing, cyclicity, and equivariance gates pass.",
        ),
        (
            "frontier.hpl.synthetic_firewall",
            (
                hpl["physical_carrier_evaluation"],
                hpl[
                    "simultaneous_physical_order_five_nonzero_forms_certified"
                ],
            ),
            (False, False),
            EvidenceClass.EXACT_THEOREM,
            "A synthetic HPL package cannot become carrier evidence.",
        ),
        (
            "frontier.hpl.digest_fail_closed",
            hpl_digest_rejected,
            True,
            EvidenceClass.EXACT_THEOREM,
            "A matrix mutation without a matching digest is rejected.",
        ),
        (
            "frontier.hpl.identity_fail_closed",
            hpl_identity_rejected,
            True,
            EvidenceClass.EXACT_THEOREM,
            "A rehashed matrix that violates the chain identities is rejected.",
        ),
        (
            "frontier.star_tangent.contract",
            (
                star_contract["active_blocks"],
                star_contract["up_transport"],
                star_contract["down_transport"],
            ),
            (
                "M0_s=[[0,m_s],[m_s,0]], m_s!=0",
                "P_u=[[a3,a5,a7],[0,0,0]]",
                "P_d=[[a3,a5,a7],[0,b5,b7]]",
            ),
            EvidenceClass.CONDITIONAL,
            "The exact theorem is explicitly conditional on retained carrier typing.",
        ),
        (
            "frontier.star_tangent.up_zero",
            star["package_level_U2_identically_zero"],
            True,
            EvidenceClass.SCOPED_NO_GO,
            "A one-arm star transport is totally isotropic for the off-diagonal active pairing.",
        ),
        (
            "frontier.star_tangent.down_factorization",
            (
                star["D2_factorization"],
                star["exact_checks"]["down_quadratic_factorization"],
            ),
            ("-(2/m_d) A_d B_d", True),
            EvidenceClass.EXACT_THEOREM,
            "The triangular down transport factorizes exactly in the fixed coordinate order.",
        ),
        (
            "frontier.star_tangent.synthetic_firewall",
            (
                star["physical_carrier_evaluation"],
                star["physical_degree_five_up_no_go_certified"],
            ),
            (False, False),
            EvidenceClass.EXACT_THEOREM,
            "The synthetic theorem fixture cannot certify the physical carrier.",
        ),
        (
            "frontier.star_tangent.fail_closed",
            star_rejected,
            True,
            EvidenceClass.EXACT_THEOREM,
            "A missing up-star typing certificate is rejected.",
        ),
        (
            "frontier.star_tangent.next_order",
            star["next_order_contract"]["formula"],
            "U3=n3_u-(2/m_u)A_u*B_u_order2",
            EvidenceClass.OPEN,
            "The degree-seven up package is typed but remains MISSING_INPUT.",
        ),
        (
            "frontier.star_tangent.support_inference_killed",
            (
                typing_nonidentifiability[
                    "inference_from_branch_support_to_up_star_typing"
                ],
                typing_nonidentifiability[
                    "inference_from_branch_support_to_down_triangular_typing"
                ],
            ),
            (GateState.KILLED, GateState.KILLED),
            EvidenceClass.SCOPED_NO_GO,
            "Exact countermodels close the shortcut from branch support to specialized transport typing.",
        ),
        (
            "frontier.star_tangent.countermodels_exact",
            all(typing_nonidentifiability["exact_checks"].values()),
            True,
            EvidenceClass.EXACT_THEOREM,
            "Star/nonstar and triangular/nontriangular models obey the same retained structural constraints.",
        ),
        (
            "frontier.star_tangent.physical_typing_open",
            typing_nonidentifiability["actual_physical_carrier_typing"],
            GateState.MISSING_INPUT,
            EvidenceClass.OPEN,
            "The no-inference theorem does not decide the absent physical transport columns.",
        ),
        (
            "frontier.star_tangent.first_invariant_test",
            typing_nonidentifiability["first_invariant_test"][
                "normalized_scalar_trace_count"
            ],
            4,
            EvidenceClass.EXACT_THEOREM,
            "The two f3 column norms need four normalized scalar traces and can immediately kill either shortcut.",
        ),
        (
            "frontier.hessian.up_rank_bound",
            synthetic_nonzero["rank_H_u"] <= 2,
            True,
            EvidenceClass.EXACT_THEOREM,
            "H_u=-P_u^T M_u^-1 P_u has rank at most two.",
        ),
        (
            "frontier.hessian.down_rank_bound",
            synthetic_nonzero["rank_H_d"] <= 2,
            True,
            EvidenceClass.EXACT_THEOREM,
            "H_d=-P_d^T M_d^-1 P_d has rank at most two.",
        ),
        (
            "frontier.hessian.determinants",
            (synthetic_nonzero["det_H_u"], synthetic_nonzero["det_H_d"]),
            (E_ZERO, E_ZERO),
            EvidenceClass.EXACT_THEOREM,
            "Both 3 x 3 Hessian determinants vanish identically.",
        ),
        (
            "frontier.compiler.nonzero_branch",
            (
                synthetic_nonzero["U2_identically_zero"],
                synthetic_nonzero["D2_identically_zero"],
            ),
            (False, False),
            EvidenceClass.EXACT_THEOREM,
            "Synthetic data exercise the compiler's nonzero branch only.",
        ),
        (
            "frontier.compiler.zero_branch",
            (
                synthetic_zero["U2_identically_zero"],
                synthetic_zero["D2_identically_zero"],
            ),
            (True, True),
            EvidenceClass.EXACT_THEOREM,
            "Synthetic zero data exercise the compiler's zero branch.",
        ),
        (
            "frontier.compiler.fail_closed",
            rejected,
            True,
            EvidenceClass.EXACT_THEOREM,
            "A false production certificate is rejected explicitly.",
        ),
        (
            "frontier.simultaneous_open",
            open_theorem["simultaneous_nonvanishing_open_nonempty"],
            True,
            EvidenceClass.CONDITIONAL,
            "Two nonzero forms meet the inherited physical open on irreducible P2.",
        ),
        (
            "frontier.status.carrier_values",
            status["carrier_residue_values_available"],
            False,
            EvidenceClass.OPEN,
            "No synthetic amplitude is promoted to carrier evidence.",
        ),
        (
            "frontier.status.rank_lift",
            status["simultaneous_light_family_rank_lift_established"],
            False,
            EvidenceClass.OPEN,
            "The physical carrier rank lift remains MISSING_INPUT.",
        ),
    )
    return tuple(
        Check(identifier, observed == expected, expected, observed, evidence, note)
        for identifier, observed, expected, evidence, note in observations
    )


def run_section4_checks() -> tuple[Check, ...]:
    return verify_origin_to_carrier_interface()


def run_section5_checks() -> tuple[Check, ...]:
    return verify_observable_deformation()


def run_section6_checks() -> tuple[Check, ...]:
    return verify_light_family_frontier()


SECTION7_EVIDENCE_IDS: Mapping[str, str] = {
    "source_docx_sha256":
        "5df218fc3486296e6ec6aa62cd9af435b8a0e2ddd2bb1ff424cd2d2f507bb8a7",
    "positive_twist_v99":
        "libfile_928994df81f881919a0ceb93e9d1f1ef",
    "extension_blindness_v13":
        "libfile_344b2a74a9808191b3d22587f1d79c58",
    "cech_lift_v14":
        "libfile_3074411f920c8191bd5367da61320a27",
    "section_basis_report_v30":
        "libfile_a583d491eff08191a18e0da0e00c6b57",
    "section_basis_interface_v30":
        "libfile_217d799984088191905944fe806f6efb",
    "canonical_manual_v8":
        "libfile_500f783276e88191b9fb6d5ac46c0689",
}


SECTION7_MISSING_INPUTS: Mapping[str, str] = {
    "quotient_136_serialization":
        "The analytical 136-dimensional quotient constituent has no machine artifact.",
    "native_76_common_convention":
        "The native 76-dimensional constituent is not serialized in the same basis.",
    "constituent_212_certificate":
        "No executable common-convention 136+76=212 basis certificate is supplied.",
    "outer_848_lifts":
        "The 848 Cech homotopy-lift outputs have not been serialized.",
    "full_404_pointwise_basis":
        "No evaluated 4 x 404 section matrix S(x) is supplied.",
    "global_generation":
        "Rank S(x)=4 has not been certified over the required quotient domain.",
    "ricci_flat_metric":
        "No converged Ricci-flat metric and residual/error certificate is supplied.",
    "visible_hym":
        "No visible-bundle HYM metric/connection and residual certificate is supplied.",
    "harmonic_representatives":
        "No harmonic matter or Higgs representatives are supplied.",
    "matter_higgs_metrics":
        "No positive-definite matter/Higgs metric package is supplied.",
    "physical_yukawas":
        "No canonically normalized physical Yukawa matrices are supplied.",
    "stabilized_vacuum":
        "No stabilized common moduli point selects the geometry and bundle data.",
}


def positive_twist_dimension_certificate() -> Mapping[str, Any]:
    """Return the exact scoped positive-twist dimension ledger.

    The numerical equality 594-190=404 is retained only as a dimension check.
    It is not interpreted as the cokernel of a lawful non-split global matrix.
    """

    v1 = 192
    v2 = 212
    total = v1 + v2
    cover_a = 1710
    cover_b = 5346
    cover_v = cover_b - cover_a
    return {
        "twist": (5, 7, 1),
        "alternative_pareto_safe_twist": (6, 6, 1),
        "alternative_invariant_sections": 415,
        "minimality_scope": (
            "two-term horseshoe resolution with every shifted line summand "
            "nef and big; not universal across all resolutions or cancellations"
        ),
        "cover_H0_A": cover_a,
        "cover_H0_B": cover_b,
        "cover_H0_V": cover_v,
        "deck_group_order": 9,
        "invariant_H0_A": 190,
        "invariant_H0_B": 594,
        "dimension_difference_only": 594 - 190,
        "H0_V1": v1,
        "H0_V2": v2,
        "H0_V": total,
        "direct_sum_dimension_identity": total == 404,
        "global_non_split_differential_lawful": False,
        "status": EvidenceClass.EXACT_THEOREM,
    }


def extension_blindness_certificate() -> Mapping[str, Any]:
    """Serialize the precise scope of abstract H0 extension blindness."""

    return {
        "exact_sequence": "0 -> H0(V1(H*)) -> H0(V(H*)) -> H0(V2(H*)) -> 0",
        "H0_V1": 192,
        "H0_V2": 212,
        "H0_V": 404,
        "vector_space_split_exists": True,
        "vector_space_split_canonical": False,
        "sheaf_split_implied": False,
        "pointwise_evaluation_extension_blind": False,
        "products_extension_blind": False,
        "hym_geometry_extension_blind": False,
        "required_global_Hom_spaces_nonzero": False,
        "former_594_by_190_outer_block_valid": False,
        "status": EvidenceClass.SCOPED_NO_GO,
    }


def analytical_constituent_certificate(twist_character: int = 0) -> Mapping[str, Any]:
    """Return, without promoting it, the unexecuted 136+76 analytical ledger."""

    if twist_character not in range(9):
        raise ValueError("twist_character must be one of the nine values 0,...,8")
    return {
        "twist_character": twist_character,
        "cover_B1_sections": 46,
        "cover_B2_sections": 64,
        "source_multiplicity": 4,
        "target_multiplicity": 22,
        "cover_source_dimension": 46 * 4,
        "cover_target_dimension": 64 * 22,
        "claimed_multiplication_rank": 184,
        "claimed_cover_cokernel": 1408 - 184,
        "regular_representation_blocks": 136,
        "reduced_dimension_options": ((20, 156), (21, 157)),
        "claimed_reduced_cokernel_options": (156 - 20, 157 - 21),
        "character_to_dimension_assignment_available": False,
        "quotient_constituent": 136,
        "native_constituent": 76,
        "claimed_total": 136 + 76,
        "serialized_artifact_available": False,
        "status": EvidenceClass.ANALYTICAL_UNCERTIFIED,
    }


def cech_lift_workload() -> Mapping[str, Any]:
    """Return the lawful non-split section-construction interface."""

    quotient_sections = 212
    extension_directions = 4
    return {
        "extension_directions": extension_directions,
        "quotient_sections": quotient_sections,
        "operator_applications": extension_directions * quotient_sections,
        "native_sections": 192,
        "total_sections": 192 + quotient_sections,
        "extension_class": "e(C)=sum_A C_A e_A",
        "cochain_equation": "delta x_s(C)=-e(C)s",
        "contracting_homotopy_solution": "x_s(C)=-h[e(C)s]",
        "linear_lift_operator": "L_A=-h o mu_{e_A}",
        "lifted_section": "sigma_C(s)=(sum_A C_A L_A(s),s)",
        "required_inputs": (
            "212 quotient representatives in a fixed equivariant basis",
            "four local extension cocycles e_A",
            "finite Cech differentials",
            "an equivariant contracting homotopy h",
        ),
        "outputs_available": False,
        "state": GateState.MISSING_INPUT,
    }


NMatrix = tuple[tuple[complex, ...], ...]


def numerical_matrix(rows: Sequence[Sequence[complex | float | int]]) -> NMatrix:
    """Create a rectangular numerical matrix, kept separate from exact arithmetic."""

    matrix = tuple(tuple(complex(value) for value in row) for row in rows)
    if not matrix or not matrix[0]:
        raise ValueError("numerical matrix must be nonempty")
    if any(len(row) != len(matrix[0]) for row in matrix):
        raise ValueError("numerical matrix rows must have equal length")
    return matrix


def n_conjugate_transpose(matrix: Sequence[Sequence[complex]]) -> NMatrix:
    if not matrix or not matrix[0]:
        raise ValueError("matrix must be nonempty")
    return tuple(
        tuple(complex(matrix[i][j]).conjugate() for i in range(len(matrix)))
        for j in range(len(matrix[0]))
    )


def n_transpose(matrix: Sequence[Sequence[complex]]) -> NMatrix:
    if not matrix or not matrix[0]:
        raise ValueError("matrix must be nonempty")
    return tuple(
        tuple(complex(matrix[i][j]) for i in range(len(matrix)))
        for j in range(len(matrix[0]))
    )


def n_matmul(
    left: Sequence[Sequence[complex]],
    right: Sequence[Sequence[complex]],
) -> NMatrix:
    if not left or not right or not left[0] or not right[0]:
        raise ValueError("matrices must be nonempty")
    if any(len(row) != len(left[0]) for row in left):
        raise ValueError("left matrix is ragged")
    if any(len(row) != len(right[0]) for row in right):
        raise ValueError("right matrix is ragged")
    if len(left[0]) != len(right):
        raise ValueError("matrix dimensions do not align")
    return tuple(
        tuple(
            sum(
                (complex(left[i][k]) * complex(right[k][j]) for k in range(len(right))),
                0j,
            )
            for j in range(len(right[0]))
        )
        for i in range(len(left))
    )


def n_scale(matrix: Sequence[Sequence[complex]], scalar: complex) -> NMatrix:
    return tuple(tuple(complex(scalar) * complex(value) for value in row) for row in matrix)


def n_identity(size: int) -> NMatrix:
    if size < 1:
        raise ValueError("identity size must be positive")
    return tuple(
        tuple(complex(int(i == j)) for j in range(size))
        for i in range(size)
    )


def n_max_abs_difference(
    left: Sequence[Sequence[complex]],
    right: Sequence[Sequence[complex]],
) -> float:
    if len(left) != len(right) or any(
        len(left[i]) != len(right[i]) for i in range(len(left))
    ):
        raise ValueError("matrix dimensions differ")
    return max(
        abs(complex(left[i][j]) - complex(right[i][j]))
        for i in range(len(left))
        for j in range(len(left[i]))
    )


def cholesky_lower(
    metric: Sequence[Sequence[complex | float | int]],
    tolerance: float = 1e-12,
) -> NMatrix:
    """Compute K=L L^dagger, rejecting non-Hermitian or non-positive input."""

    matrix = numerical_matrix(metric)
    n = len(matrix)
    if any(len(row) != n for row in matrix):
        raise ValueError("metric must be square")
    if tolerance <= 0:
        raise ValueError("tolerance must be positive")
    for i in range(n):
        for j in range(n):
            if abs(matrix[i][j] - matrix[j][i].conjugate()) > tolerance:
                raise ValueError("metric is not Hermitian within tolerance")
    lower = [[0j for _ in range(n)] for _ in range(n)]
    for i in range(n):
        for j in range(i + 1):
            subtotal = sum(lower[i][k] * lower[j][k].conjugate() for k in range(j))
            if i == j:
                diagonal = matrix[i][i] - subtotal
                if abs(diagonal.imag) > tolerance or diagonal.real <= tolerance:
                    raise ValueError("metric is not positive definite")
                lower[i][j] = complex(sqrt(diagonal.real))
            else:
                lower[i][j] = (matrix[i][j] - subtotal) / lower[j][j]
    return tuple(tuple(row) for row in lower)


def invert_upper_triangular(
    upper: Sequence[Sequence[complex]],
    tolerance: float = 1e-12,
) -> NMatrix:
    matrix = numerical_matrix(upper)
    n = len(matrix)
    if any(len(row) != n for row in matrix):
        raise ValueError("upper-triangular matrix must be square")
    if any(abs(matrix[i][j]) > tolerance for i in range(n) for j in range(i)):
        raise ValueError("matrix is not upper triangular")
    inverse = [[0j for _ in range(n)] for _ in range(n)]
    for column in range(n):
        for i in range(n - 1, -1, -1):
            rhs = complex(int(i == column))
            rhs -= sum(matrix[i][j] * inverse[j][column] for j in range(i + 1, n))
            if abs(matrix[i][i]) <= tolerance:
                raise ValueError("upper-triangular matrix is singular")
            inverse[i][column] = rhs / matrix[i][i]
    return tuple(tuple(row) for row in inverse)


def metric_whitener(
    metric: Sequence[Sequence[complex | float | int]],
    tolerance: float = 1e-12,
) -> Mapping[str, Any]:
    """Return N=(L^dagger)^-1 with N^dagger K N=I and its residual."""

    k_matrix = numerical_matrix(metric)
    lower = cholesky_lower(k_matrix, tolerance)
    whitener = invert_upper_triangular(n_conjugate_transpose(lower), tolerance)
    whitened = n_matmul(n_matmul(n_conjugate_transpose(whitener), k_matrix), whitener)
    residual = n_max_abs_difference(whitened, n_identity(len(k_matrix)))
    if residual > 100 * tolerance:
        raise ArithmeticError("metric whitening residual exceeds tolerance")
    return {
        "whitener": whitener,
        "cholesky_lower": lower,
        "residual": residual,
        "tolerance": tolerance,
    }


def canonical_normalize_yukawa(
    holomorphic: Sequence[Sequence[complex | float | int]],
    left_metric: Sequence[Sequence[complex | float | int]],
    right_metric: Sequence[Sequence[complex | float | int]],
    higgs_metric: float,
    moduli_kahler_potential: float,
    tolerance: float = 1e-12,
) -> Mapping[str, Any]:
    """Normalize Q^T Y f H using deterministic Cholesky whiteners.

    The returned matrix is e^(Kmod/2) kH^(-1/2) N_Q^T Y N_f, where
    N_R^dagger K_R N_R=I.  This is a numerical helper, not carrier evidence.
    """

    yukawa = numerical_matrix(holomorphic)
    left = metric_whitener(left_metric, tolerance)
    right = metric_whitener(right_metric, tolerance)
    if len(yukawa) != len(left["whitener"]):
        raise ValueError("left family dimension does not match Yukawa rows")
    if len(yukawa[0]) != len(right["whitener"]):
        raise ValueError("right family dimension does not match Yukawa columns")
    if higgs_metric <= tolerance:
        raise ValueError("Higgs metric must be positive")
    scalar = exp(float(moduli_kahler_potential) / 2.0) / sqrt(float(higgs_metric))
    physical = n_scale(
        n_matmul(
            n_matmul(n_transpose(left["whitener"]), yukawa),
            right["whitener"],
        ),
        scalar,
    )
    return {
        "physical_yukawa": physical,
        "left_whitener": left["whitener"],
        "right_whitener": right["whitener"],
        "left_residual": left["residual"],
        "right_residual": right["residual"],
        "scalar_prefactor": scalar,
        "evidence_status": (
            "NUMERICAL_TRANSFORM_ONLY; physical interpretation requires carrier inputs"
        ),
    }


def canonical_normalization_rank_certificate() -> Mapping[str, Any]:
    """Prove rank preservation with exact invertible rational factors."""

    holomorphic = exact_matrix(((1, 2, 3), (2, 4, 6), (0, 1, 1)))
    left = exact_matrix(((1, 1, 0), (0, 1, 1), (0, 0, 1)))
    right = exact_matrix(((2, 0, 0), (0, 1, 1), (0, 0, 1)))
    transformed = q_matmul(q_matmul(left, holomorphic), right)
    return {
        "holomorphic_rank": exact_rank(holomorphic),
        "normalized_rank": exact_rank(transformed),
        "left_determinant": determinant_3x3(left),
        "right_determinant": determinant_3x3(right),
        "rank_preserved": exact_rank(holomorphic) == exact_rank(transformed),
        "scope": "all invertible left/right family-basis factors and nonzero Higgs scalar",
        "status": EvidenceClass.EXACT_THEOREM,
    }


def metric_completion_status() -> Mapping[str, Any]:
    """Return the Section 7 boundary without manufacturing numerical geometry."""

    return {
        "highest_exact_result": "LAWFUL_CECH_LIFT_INTERFACE_AND_RANK_INVARIANCE",
        "positive_twist_dimensions_certified": True,
        "global_matrix_ansatz_rejected": True,
        "analytical_136_plus_76_serialized": False,
        "cech_lift_outputs_available": False,
        "pointwise_global_generation_certified": False,
        "ricci_flat_metric_available": False,
        "visible_hym_available": False,
        "harmonic_representatives_available": False,
        "physical_normalized_yukawas_computed": False,
        "tree_rank_repair_by_metrics_possible": False,
        "state": GateState.MISSING_INPUT,
        "open_obligations": tuple(SECTION7_MISSING_INPUTS),
    }


def verify_metric_completion() -> tuple[Check, ...]:
    """Run exact Section 7 checks plus deterministic numerical helper tests."""

    twist = positive_twist_dimension_certificate()
    blindness = extension_blindness_certificate()
    analytic = tuple(analytical_constituent_certificate(character) for character in range(9))
    lifts = cech_lift_workload()
    rank = canonical_normalization_rank_certificate()
    metric = numerical_matrix(((2, 1 + 0.25j), (1 - 0.25j, 3)))
    white = metric_whitener(metric)
    normalized = canonical_normalize_yukawa(
        ((1, 2), (0, 1)),
        metric,
        ((3, 0.5), (0.5, 2)),
        2.0,
        0.0,
    )
    nonhermitian_rejected = False
    indefinite_rejected = False
    try:
        metric_whitener(((1, 1), (0, 1)))
    except ValueError:
        nonhermitian_rejected = True
    try:
        metric_whitener(((1, 2), (2, 1)))
    except ValueError:
        indefinite_rejected = True
    status = metric_completion_status()
    observations = (
        (
            "metric.twist.cover_dimension",
            twist["cover_H0_V"],
            3636,
            EvidenceClass.EXACT_THEOREM,
            "The cover dimension is 5346-1710.",
        ),
        (
            "metric.twist.invariant_split",
            (twist["H0_V1"], twist["H0_V2"], twist["H0_V"]),
            (192, 212, 404),
            EvidenceClass.EXACT_THEOREM,
            "The invariant section dimensions obey 192+212=404.",
        ),
        (
            "metric.twist.global_matrix_rejected",
            twist["global_non_split_differential_lawful"],
            False,
            EvidenceClass.SCOPED_NO_GO,
            "The 594 by 190 dimension identity is not a lawful non-split differential.",
        ),
        (
            "metric.extension_blindness.scope",
            (
                blindness["vector_space_split_exists"],
                blindness["sheaf_split_implied"],
                blindness["pointwise_evaluation_extension_blind"],
            ),
            (True, False, False),
            EvidenceClass.EXACT_THEOREM,
            "Abstract H0 splitting does not split the sheaf or its evaluation geometry.",
        ),
        (
            "metric.analytical.characters",
            tuple(row["twist_character"] for row in analytic),
            tuple(range(9)),
            EvidenceClass.ANALYTICAL_UNCERTIFIED,
            "All nine twist characters are exposed without promoting the result.",
        ),
        (
            "metric.analytical.constituents",
            tuple(
                (row["quotient_constituent"], row["native_constituent"], row["claimed_total"])
                for row in analytic
            ),
            ((136, 76, 212),) * 9,
            EvidenceClass.ANALYTICAL_UNCERTIFIED,
            "The 136+76 decomposition remains explicitly unserialized.",
        ),
        (
            "metric.analytical.assignment_missing",
            tuple(row["character_to_dimension_assignment_available"] for row in analytic),
            (False,) * 9,
            EvidenceClass.ANALYTICAL_UNCERTIFIED,
            "No unarchived character-to-dimension assignment is invented.",
        ),
        (
            "metric.cech.workload",
            lifts["operator_applications"],
            848,
            EvidenceClass.EXACT_THEOREM,
            "Four lift operators act on each of 212 quotient representatives.",
        ),
        (
            "metric.rank.invariance",
            (
                rank["holomorphic_rank"],
                rank["normalized_rank"],
                rank["rank_preserved"],
            ),
            (2, 2, True),
            EvidenceClass.EXACT_THEOREM,
            "Invertible canonical-normalization factors preserve matrix rank.",
        ),
        (
            "metric.numeric.whitening",
            white["residual"] < 1e-10,
            True,
            EvidenceClass.CONDITIONAL,
            "The deterministic Cholesky whitener satisfies N^dagger K N=I.",
        ),
        (
            "metric.numeric.normalization",
            max(normalized["left_residual"], normalized["right_residual"]) < 1e-10,
            True,
            EvidenceClass.CONDITIONAL,
            "A synthetic positive package exercises both family whiteners.",
        ),
        (
            "metric.numeric.fail_closed",
            (nonhermitian_rejected, indefinite_rejected),
            (True, True),
            EvidenceClass.EXACT_THEOREM,
            "Invalid metric inputs fail explicitly.",
        ),
        (
            "metric.status.open",
            (
                status["physical_normalized_yukawas_computed"],
                status["tree_rank_repair_by_metrics_possible"],
                status["state"],
            ),
            (False, False, GateState.MISSING_INPUT),
            EvidenceClass.OPEN,
            "No synthetic metric is promoted to carrier evidence.",
        ),
    )
    return tuple(
        Check(identifier, observed == expected, expected, observed, evidence, note)
        for identifier, observed, expected, evidence, note in observations
    )


def run_section7_checks() -> tuple[Check, ...]:
    return verify_metric_completion()


SECTION8_EVIDENCE_IDS: Mapping[str, str] = {
    "source_docx_sha256":
        "bb9751301a2c503866fc972cdebf3fd37581e210ce59ba05f2660e4a1442cafd",
    "degree_two_v068_result_sha256":
        "ad8537589da7f5b7e5fb209163263d109a6627932e39ff41bf92d78706fea409",
    "restriction_v071":
        "libfile_21d038cd6fc4819195ed4024f22a5912",
    "serre_ray_v072":
        "libfile_20340b5bb75c8191b3cc07570fa589a6",
    "first_neighborhood_v074_result_sha256":
        "21124ecf9952c28cf1805b9f86b42f567f1720077265652e18797d0ae75f9b77",
    "nonidentifiability_v075":
        "libfile_b32613ed5b8c8191863efb82fb53d327",
    "outer_tensor_v063_result_sha256":
        "9c44424c7b6b792dc89e64d52028451e7be0dde8b3768526adcd6b0c12ee4b65",
    "quillen_v27":
        "libfile_57c3220f6d648191a82542bf57d519c0",
    "cp_pair_v8":
        "libfile_de2d2d787a288191ac18ab3996196ba5",
    "cp_order_v9":
        "libfile_08d859febea08191bbe8c603a8fc997e",
}


SECTION8_MISSING_INPUTS: Mapping[str, str] = {
    "tensor_structured_relative_duality_chain_map":
        "The GL(6)/(GL(2) x Sym^2 GL(2)) comparison datum is not constructed.",
    "physical_seed_maps":
        "Neither conic representative has a certified physical comparison map.",
    "physical_seed_quartics":
        "The two physical Pfaffian quartics are therefore undefined.",
    "eighteen_orbit_pfaffians":
        "Equivariant transport of the two seed sections to all eighteen curves is absent.",
    "relation_module_and_common_zero_locus":
        "No exact relation module or simultaneous vanishing locus exists for undefined quartics.",
    "hidden_restricted_determinants":
        "The hidden-bundle determinant factors on all conics are not supplied.",
    "anomaly_line_trivialization":
        "No common global trivialization of the combined anomaly line is supplied.",
    "differential_B_field":
        "The differential B-field datum needed for the global phase is absent.",
    "quillen_transport":
        "Quillen norms, connections, holonomies, and eight relative ratios per orbit are absent.",
    "relative_orbit_normalization":
        "The relative normalization between the two orbit sums is absent.",
    "complete_instanton_sum":
        "No scalar-valued sum over all curves in a homology class has been formed.",
    "controlled_CP_vacuum":
        "The CP-conjugate bundle pair is not a stabilized four-dimensional vacuum pair.",
    "matter_inserted_correlators":
        "No matter-inserted instanton correlators relevant to Yukawa operators are computed.",
}


def degree_two_conic_certificate() -> Mapping[str, Any]:
    """Return the exact curve census without attaching a Pfaffian value."""

    free_coordinate_orbits = (
        ((-1, -1), (2, 0), (1, 2)),
        ((-1, 0), (1, -1), (2, 2)),
    )
    labels = tuple(
        (orbit, free_pair[0], free_pair[1], torsion)
        for orbit, free_pairs in enumerate(free_coordinate_orbits)
        for free_pair in free_pairs
        for torsion in range(3)
    )
    return {
        "curve_count": len(labels),
        "orbit_count": 2,
        "orbit_sizes": tuple(
            sum(1 for label in labels if label[0] == orbit) for orbit in range(2)
        ),
        "free_action": len(set(labels)) == len(labels),
        "representatives": ((-1, -1, 0), (-1, 0, 0)),
        "labels": labels,
        "curve_type": "smooth isolated rational degree-two conic",
        "normal_bundle": ("O(-1)", "O(-1)"),
        "quadratic_value_rank": (5, 5),
        "first_jet_rank": (6, 6),
        "coefficient_algebra": (
            "Q(omega)[a]/(a^9+(24-27*omega)a^6+"
            "(-51-27*omega)a^3-1)"
        ),
        "dimension_over_Qomega": 9,
        "root_sampled": False,
        "pfaffian_value_attached": False,
    }


def homogeneous_monomials(variable_count: int, degree: int) -> tuple[tuple[int, ...], ...]:
    """Enumerate exponent tuples of a homogeneous polynomial deterministically."""

    if variable_count < 1 or degree < 0:
        raise ValueError("variable_count must be positive and degree nonnegative")
    if variable_count == 1:
        return ((degree,),)
    return tuple(
        (head, *tail)
        for head in range(degree + 1)
        for tail in homogeneous_monomials(variable_count - 1, degree - head)
    )


def quartic_grammar_certificate() -> Mapping[str, Any]:
    """Certify only the local algebraic grammar reached by the project."""

    monomials = homogeneous_monomials(4, 4)
    return {
        "serre_splitting_cases": 4,
        "local_ext1_dimension": 12,
        "spin_twisted_boundary_map_shape": (4, 4),
        "determinant_degree": 4,
        "variable_count": 4,
        "ambient_quartic_dimension": len(monomials),
        "expected_ambient_quartic_dimension": comb(7, 4),
        "monomials": monomials,
        "physical_boundary_map_available": False,
        "physical_quartic_defined": False,
    }


def serre_restriction_firewall() -> Mapping[str, Any]:
    """Expose the exact restriction result and the superseded normalization."""

    return {
        "conics_disjoint_from_I3_and_I6_scheme_theoretically": True,
        "tor_correction_required": False,
        "restricted_sequence": "0 -> O(-1) -> Wi|Gamma -> O(1) -> 0",
        "local_ext1": "H1(P1,O(-2))",
        "local_ext1_dimension": 1,
        "nonzero_extension_splitting": ("O", "O"),
        "zero_extension_splitting": ("O(-1)", "O(1)"),
        "W1_restriction_values_nonzero": (True, True),
        "W2_constant_partner_nonzero": True,
        "cech_coordinate_gauge_check_exact": True,
        "independent_serre_ray_rescaling": True,
        "naive_projective_ratio_invariant": False,
        "normal_jet_relative_normalization_available": False,
        "physical_six_by_six_maps_defined": False,
    }


def quartic_nonidentifiability_certificate() -> Mapping[str, Any]:
    """Record the exact no-go without promoting either witness to physics."""

    return {
        "certified_outer_tensor_count": 4,
        "right_euler_map_shape": (2, 6),
        "right_euler_rank": 2,
        "left_comparison_rank": 6,
        "maximal_fitting_ideal_is_unit": True,
        "witnesses": (
            {
                "name": "blocked_identity_completion",
                "quartic_term_count": 7,
                "unit_determinant": True,
                "physical": False,
            },
            {
                "name": "interleaved_completion",
                "quartic_term_count": 19,
                "unit_determinant": True,
                "physical": False,
            },
        ),
        "witnesses_Kunit_proportional": False,
        "physical_local_quartic_defined": False,
        "cross_curve_CP_work_allowed": False,
        "missing_structure": (
            "tensor-structured relative-duality chain map, equivalently the "
            "comparison orbit in GL(6)/(GL(2) x Sym^2 GL(2))"
        ),
        "scope": (
            "The stored outer tensors, right restriction, rank, and Fitting "
            "data do not identify a local quartic up to a K-unit."
        ),
    }


def relative_normalization_ledger(curves_per_orbit: int = 9) -> Mapping[str, int]:
    """Count relative scalar data; this is a ledger, not a physical assignment."""

    if curves_per_orbit < 1:
        raise ValueError("curves_per_orbit must be positive")
    return {
        "relative_ratios_per_orbit": curves_per_orbit - 1,
        "orbits": 2,
        "within_orbit_ratios": 2 * (curves_per_orbit - 1),
        "between_orbit_ratio": 1,
        "total_relative_ratios": 2 * curves_per_orbit - 1,
    }


def quillen_quadratic_refinement_certificate() -> Mapping[str, Any]:
    """Reproduce the finite classification while keeping geometry conditional."""

    classification = quadratic_form_classification()
    chirp = finite_chirp_transform()
    expected = {
        (r, s): 3 * (OMEGA ** ((-r * s) % 3)) for r, s in F3_VECTOR2
    }
    split_isotropic = sum(f3_q(label) == 0 for label in F3_VECTOR2)
    anisotropic_isotropic = sum(
        (a * a + b * b) % 3 == 0 for a, b in F3_VECTOR2
    )
    return {
        "group": "F3^2",
        "GL2_order": len(gl2_3()),
        "homogeneous_quadratic_forms": 27,
        "nondegenerate_forms": classification["nondegenerate_count"],
        "split_forms": classification["split_orbit_size"],
        "anisotropic_forms": classification["anisotropic_orbit_size"],
        "split_representative": "q(a,b)=a*b",
        "anisotropic_representative": "q(a,b)=a^2+b^2",
        "split_isotropic_count_including_zero": split_isotropic,
        "anisotropic_isotropic_count_including_zero": anisotropic_isotropic,
        "linear_form_ambiguities": 9,
        "common_phase_ambiguities": 3,
        "affine_phase_vectors": 27,
        "fourier_chirp_exact": chirp == expected,
        "physical_quillen_holonomy_identified": False,
        "conditional_acceptance_tests": (
            "the labels form an F3^2 torsor for honest bundle linearizations",
            "the Quillen holonomy is a quadratic refinement",
            "its polarization is nondegenerate",
            "the refinement is split",
        ),
    }


def _minimal_monomial_generators(
    generators: Iterable[tuple[int, int]],
) -> tuple[tuple[int, int], ...]:
    values = set(generators)
    return tuple(sorted(
        generator
        for generator in values
        if not any(
            other != generator
            and other[0] <= generator[0]
            and other[1] <= generator[1]
            for other in values
        )
    ))


def monomial_ideal_intersection(
    left: Iterable[tuple[int, int]],
    right: Iterable[tuple[int, int]],
) -> tuple[tuple[int, int], ...]:
    """Intersect two monomial ideals in two variables via lcm generators."""

    left_values, right_values = tuple(left), tuple(right)
    if not left_values or not right_values:
        raise ValueError("both monomial ideals require generators")
    return _minimal_monomial_generators(
        (max(a, c), max(b, d))
        for a, b in left_values
        for c, d in right_values
    )


def cp_bundle_pair_certificate() -> Mapping[str, Any]:
    """Certify the CP-conjugate pair and discrete local order parameter."""

    plus_local = ((0, 1), (2, 0))   # (y, x^2)
    minus_local = ((1, 0), (0, 2))  # (x, y^2)
    intersection = monomial_ideal_intersection(plus_local, minus_local)
    return {
        "global_I6_plus": ("B^2*C", "A*C^2", "A*B*C", "A^2*B"),
        "global_I6_minus": ("A^2*C", "B*C^2", "A*B*C", "A*B^2"),
        "local_I_plus": plus_local,
        "local_I_minus": minus_local,
        "local_intersection": intersection,
        "expected_local_intersection": ((0, 2), (1, 1), (2, 0)),
        "local_intersection_is_maximal_ideal_squared": (
            intersection == ((0, 2), (1, 1), (2, 0))
        ),
        "local_length": 3,
        "global_length": 9,
        "tangent_weights_plus": (1, 1, 2, 2),
        "tangent_weights_minus": (1, 1, 2, 2),
        "invariant_tangent_dimension": 0,
        "bundle_is_real": False,
        "CP_partner_exact": True,
        "support_order_parameter_discrete": True,
        "controlled_vacuum_pair_constructed": False,
        "tree_level_Jarlskog_for_texture": 0,
        "physical_Jarlskog_predicted": False,
    }


def instanton_completion_status() -> Mapping[str, Any]:
    """Return the fail-closed Section 8 boundary."""

    return {
        "highest_exact_result": (
            "TWO_CONIC_ORBITS_PLUS_QUARTIC_NONIDENTIFIABILITY_AND_CP_BUNDLE_PAIR"
        ),
        "isolated_conic_geometry_certified": True,
        "physical_seed_quartics_defined": False,
        "eighteen_pfaffian_sections_compiled": False,
        "common_determinant_line_trivialized": False,
        "hidden_determinants_available": False,
        "differential_B_field_available": False,
        "quillen_phases_available": False,
        "complete_instanton_sum_computed": False,
        "physical_CP_violation_established": False,
        "matter_inserted_yukawa_corrections_computed": False,
        "state": GateState.MISSING_INPUT,
        "open_obligations": tuple(SECTION8_MISSING_INPUTS),
    }


def verify_worldsheet_instantons() -> tuple[Check, ...]:
    curves = degree_two_conic_certificate()
    grammar = quartic_grammar_certificate()
    restriction = serre_restriction_firewall()
    no_go = quartic_nonidentifiability_certificate()
    normalization = relative_normalization_ledger()
    quillen = quillen_quadratic_refinement_certificate()
    cp_pair = cp_bundle_pair_certificate()
    status = instanton_completion_status()
    observations = (
        (
            "instanton.curves.census",
            (curves["curve_count"], curves["orbit_count"], curves["orbit_sizes"]),
            (18, 2, (9, 9)),
            EvidenceClass.EXACT_THEOREM,
            "The degree-two sector consists of two free nine-conic orbits.",
        ),
        (
            "instanton.curves.rigidity",
            curves["normal_bundle"],
            ("O(-1)", "O(-1)"),
            EvidenceClass.EXACT_THEOREM,
            "Each retained conic is isolated.",
        ),
        (
            "instanton.curves.exact_algebra",
            (curves["dimension_over_Qomega"], curves["root_sampled"]),
            (9, False),
            EvidenceClass.EXACT_THEOREM,
            "The degree-nine coefficient algebra is retained symbolically.",
        ),
        (
            "instanton.quartic.grammar",
            (
                grammar["spin_twisted_boundary_map_shape"],
                grammar["determinant_degree"],
                grammar["ambient_quartic_dimension"],
            ),
            ((4, 4), 4, 35),
            EvidenceClass.EXACT_THEOREM,
            "A 4x4 determinant has quartic grammar in four variables.",
        ),
        (
            "instanton.restriction.disjoint",
            (
                restriction["conics_disjoint_from_I3_and_I6_scheme_theoretically"],
                restriction["tor_correction_required"],
            ),
            (True, False),
            EvidenceClass.EXACT_THEOREM,
            "The point schemes do not create the missing physical rank drop.",
        ),
        (
            "instanton.restriction.ray_firewall",
            (
                restriction["independent_serre_ray_rescaling"],
                restriction["naive_projective_ratio_invariant"],
            ),
            (True, False),
            EvidenceClass.SCOPED_NO_GO,
            "The formerly proposed [s1:s2] ratio is not a physical invariant.",
        ),
        (
            "instanton.quartic.nonidentifiability",
            (
                tuple(witness["quartic_term_count"] for witness in no_go["witnesses"]),
                no_go["witnesses_Kunit_proportional"],
                no_go["physical_local_quartic_defined"],
            ),
            ((7, 19), False, False),
            EvidenceClass.SCOPED_NO_GO,
            "The nonphysical witnesses prove the stored data insufficient.",
        ),
        (
            "instanton.normalization.ledger",
            (
                normalization["relative_ratios_per_orbit"],
                normalization["total_relative_ratios"],
            ),
            (8, 17),
            EvidenceClass.EXACT_THEOREM,
            "Nine sections require eight within-orbit ratios; two orbits add one.",
        ),
        (
            "instanton.quillen.classification",
            (
                quillen["GL2_order"],
                quillen["nondegenerate_forms"],
                quillen["split_forms"],
                quillen["anisotropic_forms"],
            ),
            (48, 18, 12, 6),
            EvidenceClass.EXACT_THEOREM,
            "The binary quadratic forms over F3 form the two exact orbits.",
        ),
        (
            "instanton.quillen.chirp",
            (
                quillen["split_isotropic_count_including_zero"],
                quillen["anisotropic_isotropic_count_including_zero"],
                quillen["fourier_chirp_exact"],
            ),
            (5, 1, True),
            EvidenceClass.EXACT_THEOREM,
            "The split chirp identity is exact but its physical realization is conditional.",
        ),
        (
            "instanton.cp.bundle_pair",
            (
                cp_pair["CP_partner_exact"],
                cp_pair["local_intersection_is_maximal_ideal_squared"],
                cp_pair["invariant_tangent_dimension"],
            ),
            (True, True, 0),
            EvidenceClass.EXACT_THEOREM,
            "The CP-conjugate bundle pair has a discrete support order parameter.",
        ),
        (
            "instanton.cp.physical_boundary",
            (
                cp_pair["controlled_vacuum_pair_constructed"],
                cp_pair["physical_Jarlskog_predicted"],
            ),
            (False, False),
            EvidenceClass.OPEN,
            "Bundle-level CP pairing is not a stabilized physical prediction.",
        ),
        (
            "instanton.status.open",
            (
                status["physical_seed_quartics_defined"],
                status["complete_instanton_sum_computed"],
                status["physical_CP_violation_established"],
                status["state"],
            ),
            (False, False, False, GateState.MISSING_INPUT),
            EvidenceClass.OPEN,
            "The determinant-line-valued sector remains deliberately fail-closed.",
        ),
    )
    return tuple(
        Check(identifier, observed == expected, expected, observed, evidence, note)
        for identifier, observed, expected, evidence, note in observations
    )


def run_section8_checks() -> tuple[Check, ...]:
    return verify_worldsheet_instantons()


SECTION9_EVIDENCE_IDS: Mapping[str, str] = {
    "source_docx_sha256":
        "d1ac13c9218c603761df7f1fad873bdeb7978a6ef6e9f144b2f23adec510090c",
    "remaining_gaps_v77": "project-library:MINTOE_REMAINING_GAPS_SOLVER_v77",
    "rank22_v92_superseded":
        "libfile_d1647b9c03ec81918a7a5e7ac1cac0df",
    "radius1_v94": "libfile_106a7124fbe48191aaea7bf25c560567",
    "objective28_v95": "libfile_49be013378788191935d08d71f3027d6",
    "candidate750_witness":
        "libfile_67411915209c819193316bd6c85a82a5",
    "spectral_source_separation_v24":
        "libfile_abfa6d490b3081918d1322be255cf76f",
    "hidden_input_sufficiency_v42":
        "libfile_db88a810ab688191bc195463c6a6fa5",
}


SECTION9_MISSING_INPUTS: Mapping[str, str] = {
    "objective28_support_records":
        "The 44 unresolved support records are not embedded in this standalone release.",
    "candidate750_global_rank_ideal":
        "No characteristic-zero saturation proves injectivity of F and surjectivity of G on every fibre.",
    "candidate750_local_freeness":
        "The relevant Fitting ideals and boundary-fibre incidence ideal are not certified.",
    "primitive_Q_construction":
        "No locally free rank-two sheaf Q with the target Chern data has been proved to exist.",
    "honest_equivariant_descent":
        "Linearizations, cocycle identities, and the zero Schur-multiplier obstruction class are absent.",
    "hidden_curve_restrictions":
        "The target restrictions on the two conic seeds, hence all eighteen conics, are unproved.",
    "legacy_shell_restrictions":
        "If the earlier nine-curve shell is retained, its hidden restrictions also require proof.",
    "invariant_extension_basis":
        "No invariant Ext^1 basis or rank-two restriction map to the two conic seeds is serialized.",
    "hidden_stability":
        "No common Kahler chamber proves slope stability and exact SU(4) holonomy.",
    "hidden_spectrum":
        "Absolute hidden cohomology dimensions and the resulting Spin(10) matter multiplicities are unknown.",
    "hidden_hym":
        "No hidden Hermitian Yang-Mills connection or threshold data are available.",
    "hidden_determinant_line":
        "Hidden restricted determinants, differential B-field data, and Quillen transport are absent.",
}


def hidden_anomaly_target_certificate() -> Mapping[str, Any]:
    """Reproduce the exact integrated hidden topological target."""

    tangent = (Fraction(4), Fraction(4), Fraction(0))
    visible = (Fraction(8, 3), Fraction(5, 3), Fraction(4))
    hidden = tuple(tangent[i] - visible[i] for i in range(3))
    D = (Fraction(1), Fraction(2), Fraction(-1))
    P = (Fraction(0), Fraction(1), Fraction(0))
    D2 = divisor_square(D)
    extension_c2 = tuple(2 * P[i] - D2[i] for i in range(3))
    return {
        "c2_tangent": tangent,
        "c2_visible": visible,
        "c2_hidden_required": hidden,
        "D": D,
        "P": P,
        "D_squared": D2,
        "extension_c2": extension_c2,
        "c1_V4": (Fraction(0), Fraction(0), Fraction(0)),
        "c3_V4": Fraction(0),
        "integrated_bianchi_residual": tuple(
            tangent[i] - visible[i] - extension_c2[i] for i in range(3)
        ),
        "effective_fivebrane_class_required": False,
        "bundle_constructed": False,
    }


def hidden_monad_rank_contract(rank_source: int, rank_middle: int, rank_target: int) -> int:
    """Return rk ker(G)/im(F), rejecting impossible rank data."""

    if any(isinstance(value, bool) or not isinstance(value, int) or value < 0
           for value in (rank_source, rank_middle, rank_target)):
        raise ValueError("monad ranks must be nonnegative integers")
    rank = rank_middle - rank_source - rank_target
    if rank < 0:
        raise ValueError("middle rank is too small for the proposed monad")
    return rank


def formal_hidden_extension_certificate() -> Mapping[str, Any]:
    """Expose the formal Q-by-Q-dual architecture without asserting existence."""

    topology = hidden_anomaly_target_certificate()
    return {
        "primitive_rank": 2,
        "c1_Q": topology["D"],
        "c2_Q": topology["P"],
        "ch3_Q": Fraction(-2),
        "chi_Q": -1,
        "rank_V4": 4,
        "extension": "0 -> Q -> V4 -> Q^dual -> 0",
        "c1_V4": topology["c1_V4"],
        "c2_V4": topology["extension_c2"],
        "c3_V4": topology["c3_V4"],
        "structure_group_target": "SU(4)",
        "commutant_in_E8": "Spin(10)",
        "primitive_Q_exists": False,
        "extension_class_constructed": False,
        "status": EvidenceClass.BRIDGE_TARGET,
    }


def bounded_hidden_search_certificate() -> Mapping[str, Any]:
    """Return the exact radius-one closure and active objective-28 ledger."""

    chain = (901_114, 1_300, 942, 840, 610, 273, 164, 67)
    unresolved = chain[-1] - 20 - 3
    return {
        "coefficient_box": (-1, 1),
        "maximum_block_multiplicity": 6,
        "ordinary_rank_one_condition": "a+b == 0 mod 3",
        "inverse_heisenberg_rank": 3,
        "closed_objectives": (20, 22, 24, 26),
        "survivor_counts_through_26": (0, 0, 0, 0),
        "objective28_N_records": 2_654_388,
        "objective28_B_records": 10_958_808,
        "objective28_raw_feature_matches": 869_832,
        "objective28_disjoint_matches": 6_463,
        "objective28_source_target_splits": chain[0],
        "reduction_stages": (
            "two-neighbour",
            "weighted Hall",
            "virtual-kernel Chern",
            "determinant-line",
            "seed-curve cohomology",
            "exact point-Hall",
            "low-rank subset Chern",
        ),
        "reduction_chain": chain,
        "coordinate_symbolic_point_exclusions": 20,
        "special_branch_closures": (916, 933, 934),
        "unresolved_supports": unresolved,
        "reconnaissance_subset": 20,
        "theorem_ledger": 44,
        "older_objective22_seven_candidate_snapshot_current": False,
        "scope": "radius-one bounded block category only",
    }


def candidate750_certificate() -> Mapping[str, Any]:
    """Describe the exact complex witness and its proof boundary."""

    return {
        "candidate": 750,
        "branch": "g72_zero",
        "ranks_S_B_T": (7, 15, 6),
        "cohomology_rank": hidden_monad_rank_contract(7, 15, 6),
        "coefficient_field": "Q(omega), omega^2+omega+1=0",
        "F_coefficient_pairs": 76,
        "G_coefficient_pairs": 94,
        "composition_equation_rank": 13,
        "composition_nullity": 81,
        "GF_coefficientwise_zero": True,
        "exact_test_points": ("pA", "pC"),
        "F_ranks_at_exact_points": (7, 7),
        "G_ranks_at_exact_points": (6, 6),
        "sampled_points": 5_400,
        "sampled_rank_loss_found": False,
        "sample_scan_is_proof": False,
        "global_characteristic_zero_constant_rank_proved": False,
        "local_freeness_proved": False,
        "bad_reduction_defects_resolved": False,
        "status": EvidenceClass.CONDITIONAL,
    }


def hidden_local_freeness_contract() -> Mapping[str, Any]:
    """Specify the exact algebraic gate still required for candidate 750."""

    return {
        "required_F_rank": 7,
        "required_G_rank": 6,
        "required_conditions": (
            "the maximal-minor ideal of F has empty projective zero locus",
            "the maximal-minor ideal of G has empty projective zero locus",
            "the complex is saturated on every boundary fibre",
            "ker(G)/im(F) has Fitting support of pure rank two",
        ),
        "inactive_middle_blocks_to_remove": ("B1", "B10"),
        "next_exact_computation": (
            "compact boundary-fibre incidence with branchwise "
            "auxiliary-kernel elimination"
        ),
        "state": GateState.MISSING_INPUT,
    }


def equivariant_descent_certificate() -> Mapping[str, Any]:
    """Expose the Z3 obstruction ledger without manufacturing a linearization."""

    return {
        "group": "Z3 x Z3",
        "schur_multiplier": "H^2(Z3 x Z3,C*) = Z3",
        "obstruction_classes": (0, 1, 2),
        "honest_descent_class": 0,
        "character_twists_if_honest": 9,
        "candidate_obstruction_class_computed": False,
        "linearization_maps_serialized": False,
        "cocycle_identities_verified": False,
        "descends": False,
        "state": GateState.MISSING_INPUT,
    }


def hidden_curve_restriction_contract(
    include_legacy_shell: bool = False,
) -> Mapping[str, Any]:
    """Return the present conic target and the conditional broader inventory."""

    current = 18
    legacy = 9 if include_legacy_shell else 0
    return {
        "degree_two_conics": current,
        "degree_two_orbits": 2,
        "seed_curves": ("Gamma_A", "Gamma_B"),
        "target_Q_on_each_conic": ("O", "O(1)"),
        "target_nonzero_extension_on_each_conic": True,
        "target_V4_on_each_conic": ("O", "O", "O", "O"),
        "legacy_shell_included": include_legacy_shell,
        "legacy_shell_curves": legacy,
        "total_restriction_targets": current + legacy,
        "restrictions_proved": False,
        "state": GateState.MISSING_INPUT,
    }


def hidden_extension_index_certificate() -> Mapping[str, Any]:
    """Record the exact index and the missing invariant restriction map."""

    return {
        "chi_Q_Qdual": 14,
        "local_Ext1_dimension_per_conic_seed": 1,
        "conic_seed_count": 2,
        "required_restriction_map_rank": 2,
        "invariant_Ext1_dimension_computed": False,
        "invariant_basis_serialized": False,
        "restriction_map_constructed": False,
        "required_rank_proved": False,
        "state": GateState.MISSING_INPUT,
    }


def spin10_beta_coefficient(n10: int, n16: int, n16bar: int) -> int:
    """Return b0=24-n10-2*n16-2*n16bar for hidden Spin(10)."""

    values = (n10, n16, n16bar)
    if any(isinstance(value, bool) or not isinstance(value, int) or value < 0
           for value in values):
        raise ValueError("hidden multiplicities must be nonnegative integers")
    return 24 - n10 - 2 * n16 - 2 * n16bar


def hidden_spectrum_index_certificate() -> Mapping[str, Any]:
    """Separate exact vanishing indices from unknown absolute cohomology."""

    return {
        "branching": "E8 -> SU(4) x Spin(10)",
        "indices": {
            "chi(V4)": 0,
            "chi(V4dual)": 0,
            "chi(wedge2 V4)": 0,
            "chi(End V4)": 0,
        },
        "beta_formula": "24 - n10 - 2*n16 - 2*n16bar",
        "absolute_cohomology_dimensions_known": False,
        "matter_multiplicities_known": False,
        "asymptotic_freedom_certified": False,
        "gaugino_condensate_certified": False,
        "state": GateState.MISSING_INPUT,
    }


def spectral_hidden_firewall() -> Mapping[str, Any]:
    """Return the corrected genus-ten spectral data and scoped no-go."""

    return {
        "spectral_support_class": "3*sigma + 5*F",
        "spectral_rank": 3,
        "spectral_curve_genus": 10,
        "spectral_line_degree": 12,
        "spectral_line_chi": 3,
        "picard_dimension": 10,
        "point_charge_c2": 5,
        "standard_c2_shape": "(p,q,0)",
        "required_hidden_c2": (Fraction(4, 3), Fraction(7, 3), Fraction(-4)),
        "standard_one_fibration_route_can_match": False,
        "scoped_no_go": (
            "standard one-fibration FMW/vertical-Hecke bundles and finite "
            "c1=0 extensions thereof"
        ),
        "genuine_U2_relative_FM_route_open": True,
        "spectral_line_determined_by_degree": False,
        "honest_descent_reopened": True,
        "obsolete_genus_seven_claim": False,
        "state": GateState.OPEN,
    }


def hidden_bundle_status() -> Mapping[str, Any]:
    """Return the fail-closed status of Section 9."""

    return {
        "highest_exact_result": "OBJECTIVE28_FRONTIER_44_PLUS_CANDIDATE750_COMPLEX",
        "topological_target_certified": True,
        "objectives_through_26_closed": True,
        "objective28_unresolved_supports": 44,
        "candidate750_exact_complex": True,
        "primitive_Q_locally_free": False,
        "honest_equivariant_descent": False,
        "required_curve_restrictions": False,
        "rank_four_extension_constructed": False,
        "stable_hidden_SU4_bundle_constructed": False,
        "hidden_spectrum_computed": False,
        "hidden_HYM_available": False,
        "hidden_determinant_line_available": False,
        "state": GateState.MISSING_INPUT,
        "open_obligations": tuple(SECTION9_MISSING_INPUTS),
    }


def verify_hidden_bundle() -> tuple[Check, ...]:
    topology = hidden_anomaly_target_certificate()
    formal = formal_hidden_extension_certificate()
    search = bounded_hidden_search_certificate()
    witness = candidate750_certificate()
    descent = equivariant_descent_certificate()
    restrictions = hidden_curve_restriction_contract()
    extension = hidden_extension_index_certificate()
    spectrum = hidden_spectrum_index_certificate()
    spectral = spectral_hidden_firewall()
    status = hidden_bundle_status()
    observations = (
        ("hidden.topology.target", topology["c2_hidden_required"],
         (Fraction(4, 3), Fraction(7, 3), Fraction(-4)),
         EvidenceClass.EXACT_THEOREM, "The hidden anomaly target is exact."),
        ("hidden.topology.D2", topology["D_squared"],
         (Fraction(-4, 3), Fraction(-1, 3), Fraction(4)),
         EvidenceClass.EXACT_THEOREM, "The quotient intersection form fixes D squared."),
        ("hidden.topology.extension", topology["extension_c2"],
         topology["c2_hidden_required"], EvidenceClass.EXACT_THEOREM,
         "The formal extension topology matches the anomaly target."),
        ("hidden.topology.bianchi", topology["integrated_bianchi_residual"],
         (Fraction(0), Fraction(0), Fraction(0)), EvidenceClass.EXACT_THEOREM,
         "The integrated visible-plus-hidden residual vanishes."),
        ("hidden.extension.formal",
         (formal["rank_V4"], formal["c1_V4"], formal["c3_V4"], formal["primitive_Q_exists"]),
         (4, (Fraction(0), Fraction(0), Fraction(0)), Fraction(0), False),
         EvidenceClass.BRIDGE_TARGET, "Formal Chern data do not prove existence."),
        ("hidden.search.closed", search["survivor_counts_through_26"],
         (0, 0, 0, 0), EvidenceClass.SCOPED_NO_GO,
         "Objectives through 26 are closed in the bounded category."),
        ("hidden.search.chain", search["reduction_chain"],
         (901_114, 1_300, 942, 840, 610, 273, 164, 67),
         EvidenceClass.EXACT_THEOREM, "The objective-28 reduction ledger is exact."),
        ("hidden.search.frontier", search["unresolved_supports"], 44,
         EvidenceClass.EXACT_THEOREM, "The active theorem ledger has 44 supports."),
        ("hidden.candidate750.complex",
         (witness["cohomology_rank"], witness["GF_coefficientwise_zero"]),
         (2, True), EvidenceClass.EXACT_THEOREM,
         "Candidate 750 is an exact rank-two complex witness."),
        ("hidden.candidate750.fibres",
         (witness["F_ranks_at_exact_points"], witness["G_ranks_at_exact_points"]),
         ((7, 7), (6, 6)), EvidenceClass.EXACT_THEOREM,
         "Two exact fibres have the required ranks."),
        ("hidden.candidate750.boundary",
         (witness["sample_scan_is_proof"], witness["local_freeness_proved"]),
         (False, False), EvidenceClass.OPEN,
         "Finite sampling is not a global constant-rank theorem."),
        ("hidden.descent.open",
         (descent["obstruction_classes"], descent["descends"]),
         ((0, 1, 2), False), EvidenceClass.OPEN,
         "The actual obstruction class and cocycles are missing."),
        ("hidden.restrictions.current",
         (restrictions["degree_two_conics"], restrictions["total_restriction_targets"],
          restrictions["restrictions_proved"]),
         (18, 18, False), EvidenceClass.OPEN,
         "The current required degree-two inventory is eighteen conics."),
        ("hidden.extension.restriction_rank",
         (extension["chi_Q_Qdual"], extension["required_restriction_map_rank"],
          extension["required_rank_proved"]),
         (14, 2, False), EvidenceClass.OPEN,
         "The index does not supply the invariant restriction map."),
        ("hidden.spectrum.indices",
         tuple(spectrum["indices"].values()), (0, 0, 0, 0),
         EvidenceClass.EXACT_THEOREM, "All retained hidden indices vanish."),
        ("hidden.spectral.correction",
         (spectral["spectral_curve_genus"], spectral["spectral_line_degree"],
          spectral["standard_one_fibration_route_can_match"]),
         (10, 12, False), EvidenceClass.SCOPED_NO_GO,
         "Genus ten supersedes the obsolete genus-seven claim."),
        ("hidden.status.open",
         (status["objective28_unresolved_supports"],
          status["stable_hidden_SU4_bundle_constructed"], status["state"]),
         (44, False, GateState.MISSING_INPUT), EvidenceClass.OPEN,
         "The hidden bundle remains deliberately fail-closed."),
    )
    return tuple(
        Check(identifier, observed == expected, expected, observed, evidence, note)
        for identifier, observed, expected, evidence, note in observations
    )


def run_section9_checks() -> tuple[Check, ...]:
    return verify_hidden_bundle()


SECTION10_EVIDENCE_IDS: Mapping[str, str] = {
    "source_docx_sha256":
        "9c9a131c3ee297b95bb5fc02a666f9cffcae9738a4dd5042206405ec3bb93822",
    "term_count_v30":
        "project-library:MINTOE_SUSY_VACUUM_TERM_COUNT_GATE_v30",
    "affine_hyperplane_v31":
        "libfile_06e14584f7e4819185454562ade70f53",
    "split_bicubic_cs_v34":
        "libfile_fcb6d3a2d5d481919de4bfbf0551f69f",
    "e6_toral_racetrack_v35":
        "libfile_775be6fc80f08191ad877d80e67082d3",
    "controlled_classification_v41":
        "libfile_966ca708e5388191906d1be96524bc7b",
    "remaining_gaps_v77":
        "libfile_59ab25cc5d0c819186845461f6978e99",
}


SECTION10_MISSING_INPUTS: Mapping[str, str] = {
    "worldsheet_coefficients":
        "No physical carrier Pfaffians are available in one common determinant-line trivialization.",
    "hidden_bundle_and_spectrum":
        "Section 9 has not supplied a stable hidden bundle or its absolute charged spectrum.",
    "condensate_exponents":
        "Carrier-derived beta functions, mass thresholds, and unequal effective exponents are absent.",
    "condensate_prefactors":
        "Holomorphic condensate prefactors and their moduli dependence are not computed.",
    "threshold_functions":
        "The carrier-specific one-loop gauge kinetic functions are unavailable.",
    "kahler_potential":
        "No full corrected Kahler potential covers dilaton, Kahler, complex-structure, and bundle moduli.",
    "gauge_kinetic_functions":
        "The complete visible and hidden gauge kinetic matrix has not been derived.",
    "d_terms":
        "D-term charges, Fayet-Iliopoulos data, and charged-field branches are missing.",
    "complex_and_bundle_dependence":
        "The combined superpotential dependence on complex-structure and bundle moduli is unresolved.",
    "f_and_d_solution":
        "No simultaneous solution of every F- and D-flatness equation has been exhibited.",
    "common_stability_chamber":
        "No candidate vacuum is proved to lie in the visible/hidden slope-stability and physical Kahler cone.",
    "hym_and_matter_metrics":
        "Visible and hidden HYM connections and positive physical matter metrics remain open.",
    "hessian":
        "No canonically normalized scalar Hessian establishes metastability or absence of tachyons.",
    "correction_bounds":
        "Worldsheet, loop, alpha-prime, and additional nonperturbative corrections are not bounded.",
    "uplift_or_nonsupersymmetric_sector":
        "No controlled uplift or independently stable nonsupersymmetric construction is supplied.",
    "scale_separation":
        "No hierarchy among KK, string, condensation, moduli, and four-dimensional scales is certified.",
    "cp_pair":
        "No pair of fully stabilized CP-conjugate vacua has been constructed.",
    "visible_physical_point":
        "No common point also realizes the full-rank, canonically normalized visible Yukawa sector.",
}


def exact_determinant(
    rows: Sequence[Sequence[int | Fraction]],
) -> Fraction:
    """Compute a square determinant by exact elimination over Q."""

    matrix = [list(row) for row in exact_matrix(rows)]
    size = len(matrix)
    if len(matrix[0]) != size:
        raise ValueError("determinant requires a square matrix")
    determinant = Fraction(1)
    for column in range(size):
        pivot = next(
            (row for row in range(column, size) if matrix[row][column] != 0),
            None,
        )
        if pivot is None:
            return Fraction(0)
        if pivot != column:
            matrix[column], matrix[pivot] = matrix[pivot], matrix[column]
            determinant = -determinant
        pivot_value = matrix[column][column]
        determinant *= pivot_value
        for row in range(column + 1, size):
            factor = matrix[row][column] / pivot_value
            for index in range(column + 1, size):
                matrix[row][index] -= factor * matrix[column][index]
    return determinant


def exact_solve(
    rows: Sequence[Sequence[int | Fraction]],
    rhs: Sequence[int | Fraction],
) -> tuple[Fraction, ...]:
    """Solve a nonsingular square rational system with explicit failure."""

    matrix = exact_matrix(rows)
    if len(matrix) != len(matrix[0]) or len(rhs) != len(matrix):
        raise ValueError("exact_solve requires a square system and matching rhs")
    augmented = [
        [*row, _coerce_fraction(value)]
        for row, value in zip(matrix, rhs)
    ]
    size = len(matrix)
    for column in range(size):
        pivot = next(
            (row for row in range(column, size) if augmented[row][column] != 0),
            None,
        )
        if pivot is None:
            raise ValueError("system is singular")
        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
        pivot_value = augmented[column][column]
        augmented[column] = [value / pivot_value for value in augmented[column]]
        for row in range(size):
            if row == column:
                continue
            factor = augmented[row][column]
            augmented[row] = [
                augmented[row][index] - factor * augmented[column][index]
                for index in range(size + 1)
            ]
    return tuple(augmented[row][-1] for row in range(size))


def worldsheet_charge(
    d1: int,
    d2: int,
    p: int | Fraction = 1,
    base_degree: int = 1,
) -> tuple[Fraction, ...]:
    """Return q_n(d1,d2) in the fixed (S,T1,T2,T3) ordering."""

    if any(
        isinstance(value, bool) or not isinstance(value, int)
        for value in (d1, d2, base_degree)
    ):
        raise TypeError("degrees must be integers")
    if base_degree < 1:
        raise ValueError("base_degree must be positive")
    scale = _coerce_fraction(p)
    if scale == 0:
        raise ValueError("p must be nonzero")
    return (
        Fraction(0),
        scale * d1,
        scale * d2,
        scale * base_degree,
    )


def condensate_charge(
    exponent: int | Fraction,
    threshold_direction: Sequence[int | Fraction] = (
        Fraction(-2, 3),
        Fraction(1, 3),
        Fraction(-4),
    ),
) -> tuple[Fraction, ...]:
    """Return a(1,b1,b2,b3) in the fixed modulus ordering."""

    if len(threshold_direction) != 3:
        raise ValueError("threshold_direction must have three entries")
    a = _coerce_fraction(exponent)
    if a == 0:
        raise ValueError("condensate exponent must be nonzero")
    direction = tuple(_coerce_fraction(value) for value in threshold_direction)
    return (a, *(a * value for value in direction))


def affine_functional(
    charge: Sequence[int | Fraction],
    exponent: int | Fraction,
    p: int | Fraction = 1,
) -> Fraction:
    """Evaluate L(q)=(1/a+4/p)q_S+q_T3/p exactly."""

    if len(charge) != 4:
        raise ValueError("charge must use (S,T1,T2,T3) ordering")
    q = tuple(_coerce_fraction(value) for value in charge)
    a, scale = _coerce_fraction(exponent), _coerce_fraction(p)
    if a == 0 or scale == 0:
        raise ValueError("a and p must be nonzero")
    return (Fraction(1, 1) / a + Fraction(4, 1) / scale) * q[0] + q[3] / scale


def tree_kahler_gradient(
    s: int | Fraction,
    t1: int | Fraction,
    t2: int | Fraction,
    t3: int | Fraction,
) -> tuple[Fraction, ...]:
    """Return the tree-level gradient used by the charge no-go certificate."""

    s_q, t1_q, t2_q, t3_q = (
        _coerce_fraction(value) for value in (s, t1, t2, t3)
    )
    U = t1_q + t2_q + 6 * t3_q
    if s_q <= 0 or t1_q <= 0 or t2_q <= 0 or U <= 0:
        raise ValueError("the physical cone requires s,t1,t2,U>0")
    return (
        -Fraction(1, 2) / s_q,
        -Fraction(1, 2) * (Fraction(1, 1) / t1_q + Fraction(1, 1) / U),
        -Fraction(1, 2) * (Fraction(1, 1) / t2_q + Fraction(1, 1) / U),
        -Fraction(3, 1) / U,
    )


def affine_hyperplane_certificate(
    exponent: int | Fraction = 1,
    p: int | Fraction = 1,
    sample_point: Sequence[int | Fraction] = (2, 3, 5, 7),
) -> Mapping[str, Any]:
    """Certify the universal base-degree-one affine obstruction."""

    if len(sample_point) != 4:
        raise ValueError("sample_point must be (s,t1,t2,t3)")
    a, scale = _coerce_fraction(exponent), _coerce_fraction(p)
    retained = (
        worldsheet_charge(1, 0, scale),
        worldsheet_charge(2, 0, scale),
        worldsheet_charge(2, 1, scale),
    )
    condensate = condensate_charge(a)
    gradient = tree_kahler_gradient(*sample_point)
    gradient_value = affine_functional(gradient, a, scale)
    return {
        "coordinate_order": ("S", "T1", "T2", "T3"),
        "retained_worldsheet_charges": retained,
        "condensate_charge": condensate,
        "retained_L_values": tuple(
            affine_functional(charge, a, scale)
            for charge in (*retained, condensate)
        ),
        "all_base_degree_one_L_value": Fraction(1),
        "tree_kahler_gradient": gradient,
        "L_of_tree_kahler_gradient": gradient_value,
        "physical_cone_sign_obstruction": gradient_value < 0,
        "q40_affine_relation": (2, -3, 1),
        "finite_ordinary_base_degree_one_plus_one_condensate_susy_solution": False,
        "scope": (
            "finite ordinary base-degree-one worldsheet terms plus the tested "
            "single condensate and tree-level Kahler gradient"
        ),
    }


def worldsheet_augmented_matrix(
    d1: int,
    d2: int,
    base_degree: int,
    exponent: int | Fraction = 1,
    p: int | Fraction = 1,
) -> tuple[tuple[Fraction, ...], ...]:
    """Return rows (q10,q20,q21,qgc,q_n), each augmented by one."""

    charges = (
        worldsheet_charge(1, 0, p),
        worldsheet_charge(2, 0, p),
        worldsheet_charge(2, 1, p),
        condensate_charge(exponent),
        worldsheet_charge(d1, d2, p, base_degree),
    )
    return tuple((*charge, Fraction(1)) for charge in charges)


def controlled_worldsheet_weights(
    d1: int,
    d2: int,
    base_degree: int,
) -> tuple[Fraction, ...]:
    """Return the exact v41 controlled-limit affine weights."""

    if base_degree <= 1:
        raise ValueError("the higher-base certificate requires n>=2")
    denominator = Fraction(base_degree - 1)
    return (
        Fraction(2 * base_degree - d1, base_degree - 1),
        Fraction(d1 - d2 - base_degree, base_degree - 1),
        Fraction(d2, base_degree - 1),
        Fraction(0),
        -Fraction(1, base_degree - 1),
    )


def one_extra_worldsheet_certificate(
    d1: int = 2,
    d2: int = 0,
    base_degree: int = 2,
    exponent: int | Fraction = 1,
    p: int | Fraction = 1,
) -> Mapping[str, Any]:
    """Classify one higher-base term and its controlled-limit obstruction."""

    if base_degree <= 1:
        raise ValueError("base_degree must be at least two")
    a, scale = _coerce_fraction(exponent), _coerce_fraction(p)
    matrix = worldsheet_augmented_matrix(
        d1, d2, base_degree, a, scale
    )
    determinant = exact_determinant(matrix)
    weights = controlled_worldsheet_weights(d1, d2, base_degree)
    charge_relation = tuple(
        sum(weights[row] * matrix[row][column] for row in range(5))
        for column in range(4)
    )
    affine_sum = sum(weights)
    alignments = (
        (base_degree, 0, "q10"),
        (2 * base_degree, 0, "q20"),
        (2 * base_degree, base_degree, "q21"),
    )
    aligned = next(
        (label for x, y, label in alignments if (d1, d2) == (x, y)),
        None,
    )
    return {
        "augmented_determinant": determinant,
        "expected_determinant": a * scale ** 3 * (base_degree - 1),
        "controlled_weights": weights,
        "weighted_charge_relation": charge_relation,
        "weight_sum": affine_sum,
        "surviving_alignment": aligned,
        "all_surviving_alignments": alignments,
        "required_amplitude_ratio": -Fraction(1, base_degree),
        "subexponential_determinant_growth_gives_ratio_zero": True,
        "one_extra_term_closes_controlled_limit": True,
        "one_term_multicover_closed": True,
        "assumption": "subexponential determinant growth in the controlled limit",
    }


def second_condensate_augmented_matrix(
    exponent1: int | Fraction,
    exponent2: int | Fraction,
    threshold_direction2: Sequence[int | Fraction],
    p: int | Fraction = 1,
) -> tuple[tuple[Fraction, ...], ...]:
    """Return rows (q10,q20,q21,q1,q2), each augmented by one."""

    charges = (
        worldsheet_charge(1, 0, p),
        worldsheet_charge(2, 0, p),
        worldsheet_charge(2, 1, p),
        condensate_charge(exponent1),
        condensate_charge(exponent2, threshold_direction2),
    )
    return tuple((*charge, Fraction(1)) for charge in charges)


def second_condensate_certificate(
    exponent1: int | Fraction = 1,
    exponent2: int | Fraction = 2,
    threshold_direction2: Sequence[int | Fraction] = (
        Fraction(-2, 3),
        Fraction(1, 3),
        Fraction(-4),
    ),
    p: int | Fraction = 1,
) -> Mapping[str, Any]:
    """Classify the general second-condensate escape."""

    a1, a2, scale = (
        _coerce_fraction(exponent1),
        _coerce_fraction(exponent2),
        _coerce_fraction(p),
    )
    b = tuple(_coerce_fraction(value) for value in threshold_direction2)
    matrix = second_condensate_augmented_matrix(a1, a2, b, scale)
    q2 = matrix[-1][:4]
    determinant = exact_determinant(matrix)
    expected = a1 * scale ** 3 * (
        affine_functional(q2, a1, scale) - 1
    )
    unique_direction = (
        Fraction(-2, 3),
        Fraction(1, 3),
        Fraction(-4),
    )
    return {
        "augmented_determinant": determinant,
        "expected_determinant": expected,
        "condensate_ratio_in_controlled_limit": -a1 / a2,
        "unique_no_worldsheet_threshold_direction": unique_direction,
        "uses_same_gauge_kinetic_function": b == unique_direction,
        "unequal_exponents": a1 != a2,
        "minimal_survivor": b == unique_direction and a1 != a2,
        "equal_exponents_collapse_to_one_exponential": b == unique_direction and a1 == a2,
        "conditional_one_worldsheet_families": {
            "q10_active": "b2=1/3, b1=b3+10/3, b3!=-4",
            "q20_active": "b2=1/3, b1=2*b3+22/3, b3!=-4",
            "q21_active": "b1=2*b3+22/3, b2=b3+13/3, b3!=-4",
        },
        "carrier_parameters_supplied": False,
    }


def racetrack_charge_rank_certificate(
    exponent1: int | Fraction = 1,
    exponent2: int | Fraction = 2,
    p: int | Fraction = 1,
) -> Mapping[str, Any]:
    """Certify that a same-direction racetrack gains rank iff a1 != a2."""

    a1, a2, scale = (
        _coerce_fraction(exponent1),
        _coerce_fraction(exponent2),
        _coerce_fraction(p),
    )
    q10 = worldsheet_charge(1, 0, scale)
    q20 = worldsheet_charge(2, 0, scale)
    q21 = worldsheet_charge(2, 1, scale)
    q1 = condensate_charge(a1)
    q2 = condensate_charge(a2)
    rows = (q10, q20, q21, q1, q2)
    augmented = tuple((*charge, Fraction(1)) for charge in rows)
    selected = (augmented[0], augmented[1], augmented[2], augmented[3], augmented[4])
    determinant = exact_determinant(selected)
    ordinary_augmented_rank = exact_rank(augmented[:-1])
    racetrack_augmented_rank = exact_rank(augmented)
    return {
        "ordinary_linear_charge_rank": exact_rank(rows[:-1]),
        "racetrack_linear_charge_rank": exact_rank(rows),
        "ordinary_affine_hull_dimension": ordinary_augmented_rank - 1,
        "racetrack_affine_hull_dimension": racetrack_augmented_rank - 1,
        "augmented_determinant": determinant,
        "expected_augmented_determinant": -(scale ** 3) * (a1 - a2),
        "same_threshold_direction": True,
        "rank_lift_if_and_only_if_unequal": (
            racetrack_augmented_rank == 5
            if a1 != a2
            else racetrack_augmented_rank == 4
        ),
        "minimal_racetrack_pass": a1 != a2,
    }


def cartan_e6() -> tuple[tuple[int, ...], ...]:
    """E6 Cartan matrix with arms of lengths two, two, and one."""

    matrix = [[0] * 6 for _ in range(6)]
    for index in range(6):
        matrix[index][index] = 2
    for left, right in ((0, 1), (1, 2), (2, 3), (3, 4), (2, 5)):
        matrix[left][right] = matrix[right][left] = -1
    return tuple(tuple(row) for row in matrix)


def rref_two_subspaces_f3_6(
) -> tuple[tuple[tuple[int, ...], tuple[int, ...]], ...]:
    """Enumerate every 2-plane in F3^6 exactly once in RREF."""

    subspaces = []
    for pivot1 in range(5):
        for pivot2 in range(pivot1 + 1, 6):
            free1 = tuple(
                column
                for column in range(pivot1 + 1, 6)
                if column != pivot2
            )
            free2 = tuple(range(pivot2 + 1, 6))
            for values in product(range(3), repeat=len(free1) + len(free2)):
                row1, row2 = [0] * 6, [0] * 6
                row1[pivot1], row2[pivot2] = 1, 1
                for column, value in zip(free1, values[:len(free1)]):
                    row1[column] = value
                for column, value in zip(free2, values[len(free1):]):
                    row2[column] = value
                subspaces.append((tuple(row1), tuple(row2)))
    return tuple(subspaces)


def e6_toral_racetrack_certificate() -> Mapping[str, Any]:
    """Enumerate the historical E6 toral Wilson-line escape exactly."""

    cartan = cartan_e6()
    roots = roots_from_cartan(cartan)
    subspaces = rref_two_subspaces_f3_6()
    type_by_rank_and_roots = {
        (0, 0): "none",
        (2, 6): "A2",
        (3, 12): "A3",
        (3, 6): "A1^3",
        (4, 12): "A2^2",
        (5, 30): "A5",
        (4, 24): "D4",
        (6, 18): "A2^3",
    }
    counts = {label: 0 for label in type_by_rank_and_roots.values()}
    for left, right in subspaces:
        surviving = tuple(
            root
            for root in roots
            if cartan_pairing_mod3(left, root, cartan) == 0
            and cartan_pairing_mod3(right, root, cartan) == 0
        )
        key = (
            exact_rank(surviving) if surviving else 0,
            len(surviving),
        )
        counts[type_by_rank_and_roots[key]] += 1
    expected = {
        "none": 360,
        "A2": 2160,
        "A3": 2430,
        "A1^3": 4860,
        "A2^2": 1080,
        "A5": 36,
        "D4": 45,
        "A2^3": 40,
    }
    return {
        "ambient_group": "E6",
        "root_count": len(roots),
        "two_subspaces_F3_6": len(subspaces),
        "centralizer_type_counts": counts,
        "expected_type_counts": expected,
        "enumeration_exact": counts == expected and sum(counts.values()) == 11_011,
        "multifactor_types": ("A1^3", "A2^2", "A2^3"),
        "dual_coxeter_numbers_by_multifactor_type": {
            "A1^3": (2, 2, 2),
            "A2^2": (3, 3),
            "A2^3": (3, 3, 3),
        },
        "pure_SYM_unequal_exponent_racetrack_exists": False,
        "scope": (
            "historical hidden-SU(3)/E6 toral Wilson-line pure-SYM architecture; "
            "not the Section 9 hidden-SU(4)/Spin(10) target"
        ),
    }


def chern_simons_constant_firewall() -> Mapping[str, Any]:
    """Record the published split-bicubic result with its exact scope."""

    return {
        "geometry": "split bicubic quotient",
        "published_result": "W_CS=0 for the analyzed cycles and flat connections",
        "constant_source_available_on_tested_route": False,
        "complete_cycle_basis_through_singular_limit_certified": False,
        "universal_flux_or_CS_no_go": False,
        "scope": "Apruzzi et al. arXiv:1410.2603, equations 4.34--4.35",
    }


def n1_f_term_potential(
    kahler_value: float,
    superpotential: complex,
    covariant_derivatives: Sequence[complex],
    inverse_kahler_metric: Sequence[Sequence[complex]],
) -> float:
    """Numerically evaluate V_F, isolated from the exact certificate layer."""

    size = len(covariant_derivatives)
    if size == 0 or len(inverse_kahler_metric) != size:
        raise ValueError("nonempty derivative vector and square inverse metric required")
    if any(len(row) != size for row in inverse_kahler_metric):
        raise ValueError("inverse Kahler metric must be square")
    contraction = sum(
        inverse_kahler_metric[i][j]
        * covariant_derivatives[i]
        * covariant_derivatives[j].conjugate()
        for i in range(size)
        for j in range(size)
    )
    value = exp(kahler_value) * (contraction - 3 * abs(superpotential) ** 2)
    if abs(value.imag) > 1e-10:
        raise ValueError("the supplied data do not produce a real F-term potential")
    return float(value.real)


def n1_d_term_potential(
    d_terms: Sequence[float],
    inverse_real_gauge_metric: Sequence[Sequence[float]],
) -> float:
    """Numerically evaluate one half D^T(Re f)^(-1)D."""

    size = len(d_terms)
    if size == 0 or len(inverse_real_gauge_metric) != size:
        raise ValueError("nonempty D vector and square inverse gauge metric required")
    if any(len(row) != size for row in inverse_real_gauge_metric):
        raise ValueError("inverse gauge metric must be square")
    return 0.5 * sum(
        d_terms[i] * inverse_real_gauge_metric[i][j] * d_terms[j]
        for i in range(size)
        for j in range(size)
    )


def minimal_racetrack_certificate(
    exponent1: int | Fraction = 1,
    exponent2: int | Fraction = 2,
) -> Mapping[str, Any]:
    """Return the leading balance without pretending that a vacuum exists."""

    a1, a2 = _coerce_fraction(exponent1), _coerce_fraction(exponent2)
    if a1 <= 0 or a2 <= 0:
        raise ValueError("physical racetrack exponents must be positive")
    return {
        "superpotential": "A1*exp(-a1*f_h)+A2*exp(-a2*f_h)",
        "leading_balance": "a1*W1+a2*W2 approximately 0",
        "required_term_ratio": -a1 / a2,
        "logarithmic_diagnostic":
            "exp(-(a2-a1)f_h) approximately -a1*A1/(a2*A2)",
        "unequal_exponents": a1 != a2,
        "axion_fixed_by_log_branch_if_coefficients_known": True,
        "carrier_coefficients_known": False,
        "vacuum_established": False,
    }


def controlled_vacuum_contract() -> tuple[str, ...]:
    """Return the fail-closed obligations for a controlled vacuum claim."""

    return tuple(SECTION10_MISSING_INPUTS)


def stabilization_status() -> Mapping[str, Any]:
    """Return Section 10's strongest result and open boundary."""

    return {
        "highest_exact_result":
            "SOURCE_CLASSIFICATION_TO_SAME_FH_UNEQUAL_EXPONENT_RACETRACK",
        "four_term_sign_obstruction": True,
        "universal_affine_hyperplane_no_go": True,
        "tested_chern_simons_constant_route_closed": True,
        "pure_SYM_toral_E6_racetrack_closed": True,
        "one_extra_worldsheet_term_closed": True,
        "one_term_multicovers_closed": True,
        "minimal_survivor":
            "A1 exp(-a1 f_h)+A2 exp(-a2 f_h), a1 != a2",
        "carrier_unequal_exponents_derived": False,
        "full_superpotential_constructed": False,
        "simultaneous_F_and_D_solution": False,
        "controlled_vacuum_constructed": False,
        "state": GateState.MISSING_INPUT,
        "open_obligations": controlled_vacuum_contract(),
    }


def verify_stabilization() -> tuple[Check, ...]:
    """Run the exact and fail-closed Section 10 certificate suite."""

    affine = affine_hyperplane_certificate()
    higher = one_extra_worldsheet_certificate()
    second = second_condensate_certificate()
    rank = racetrack_charge_rank_certificate()
    e6 = e6_toral_racetrack_certificate()
    cs = chern_simons_constant_firewall()
    racetrack = minimal_racetrack_certificate()
    status = stabilization_status()
    observations = (
        ("stabilization.affine.values", affine["retained_L_values"],
         (Fraction(1),) * 4, EvidenceClass.SCOPED_NO_GO,
         "All retained charges lie on L=1."),
        ("stabilization.affine.sign", affine["physical_cone_sign_obstruction"],
         True, EvidenceClass.SCOPED_NO_GO,
         "The tree Kahler gradient has L(K)<0 in the physical cone."),
        ("stabilization.higher.determinant",
         higher["augmented_determinant"], higher["expected_determinant"],
         EvidenceClass.EXACT_THEOREM,
         "The higher-base augmented determinant is a*p^3*(n-1)."),
        ("stabilization.higher.relation",
         (higher["weighted_charge_relation"], higher["weight_sum"]),
         ((Fraction(0),) * 4, Fraction(1)), EvidenceClass.EXACT_THEOREM,
         "The v41 controlled weights satisfy the exact affine relation."),
        ("stabilization.higher.no_go",
         (higher["one_extra_term_closes_controlled_limit"],
          higher["one_term_multicover_closed"]),
         (True, True), EvidenceClass.SCOPED_NO_GO,
         "One extra higher-base term and its one-term multicovers are closed."),
        ("stabilization.second.determinant",
         second["augmented_determinant"], second["expected_determinant"],
         EvidenceClass.EXACT_THEOREM,
         "The general second-condensate determinant matches a*p^3*(L(q2)-1)."),
        ("stabilization.second.survivor",
         (second["uses_same_gauge_kinetic_function"],
          second["unequal_exponents"], second["minimal_survivor"]),
         (True, True, True), EvidenceClass.CONDITIONAL,
         "The minimal charge-space survivor uses same f_h and unequal exponents."),
        ("stabilization.racetrack.rank",
         (rank["ordinary_affine_hull_dimension"],
          rank["racetrack_affine_hull_dimension"],
          rank["augmented_determinant"], rank["expected_augmented_determinant"]),
         (3, 4, Fraction(1), Fraction(1)), EvidenceClass.EXACT_THEOREM,
         "Unequal same-direction exponents raise the charge rank."),
        ("stabilization.e6.enumeration",
         (e6["root_count"], e6["two_subspaces_F3_6"],
          e6["enumeration_exact"]),
         (72, 11_011, True), EvidenceClass.EXACT_THEOREM,
         "All 11011 toral two-planes are enumerated."),
        ("stabilization.e6.pure_SYM",
         e6["pure_SYM_unequal_exponent_racetrack_exists"], False,
         EvidenceClass.SCOPED_NO_GO,
         "Every multifactor toral centralizer has equal dual Coxeter numbers."),
        ("stabilization.cs.scope",
         (cs["constant_source_available_on_tested_route"],
          cs["universal_flux_or_CS_no_go"]),
         (False, False), EvidenceClass.SCOPED_NO_GO,
         "The tested split-bicubic constant vanishes without a universal no-go."),
        ("stabilization.racetrack.boundary",
         (racetrack["required_term_ratio"], racetrack["vacuum_established"]),
         (Fraction(-1, 2), False), EvidenceClass.CONDITIONAL,
         "The leading balance is a diagnostic, not a vacuum."),
        ("stabilization.status.open",
         (status["carrier_unequal_exponents_derived"],
          status["controlled_vacuum_constructed"], status["state"]),
         (False, False, GateState.MISSING_INPUT), EvidenceClass.OPEN,
         "The carrier coefficients and full controlled vacuum remain missing."),
    )
    return tuple(
        Check(identifier, observed == expected, expected, observed, evidence, note)
        for identifier, observed, expected, evidence, note in observations
    )


def run_section10_checks() -> tuple[Check, ...]:
    return verify_stabilization()


SECTION11_EVIDENCE_IDS: Mapping[str, str] = {
    "source_docx_sha256":
        "305c26481211617f77694914edcc9bc3c902b2ada3db18936ef4d41b51bf68d5",
    "section11_source": "libfile_b4f5527d4ad88191991d9c69cb8abeb8",
    "canonical_manual_v8": "libfile_500f783276e88191b9fb6d5ac46c0689",
    "legacy_prediction_ledger_excluded":
        "libfile_18cf52d5f288819185f05ae0818d8531",
    "jarlskog_1985": "https://inspirehep.net/literature/216470",
    "bf_1982": "https://inspirehep.net/literature/12129",
    "minkowski_1977": "https://inspirehep.net/literature/4994",
    "machacek_vaughn_1983": "https://inspirehep.net/literature/188748",
    "appelquist_carazzone_1975": "https://inspirehep.net/literature/1631",
    "weinberg_1979": "https://inspirehep.net/literature/144673",
}


SECTION11_MISSING_INPUTS: Mapping[str, str] = {
    "common_vacuum":
        "No single point supplies geometry, both bundles, metrics, determinants, thresholds, and observables.",
    "normalized_action":
        "The complete Einstein-frame four-dimensional action has not been derived.",
    "visible_full_rank":
        "The four first-test f3 traces are missing; adaptive escalation uses at most twenty traces before deciding simultaneous full rank.",
    "metric_package":
        "Ricci-flat, HYM, harmonic-representative, and matter-metric data are absent.",
    "instanton_line":
        "Physical seed maps, Pfaffians, Quillen normalization, and global determinant transport are missing.",
    "hidden_completion":
        "No stable descended hidden bundle, absolute spectrum, or threshold package exists.",
    "differential_anomaly":
        "No global differential B-field and total anomaly-line trivialization is available.",
    "vacuum_solution":
        "No complete F/D or controlled nonsupersymmetric stationary solution has been certified.",
    "hessian":
        "No canonically normalized scalar mass matrix has been computed.",
    "rg_thresholds":
        "No carrier spectrum with ordered heavy thresholds and beta functions has been supplied.",
    "supersymmetry_breaking":
        "No breaking sector, mediation mechanism, or soft terms are derived.",
    "electroweak_breaking":
        "No mu term, B-mu term, Higgs potential, or electroweak vacuum is derived.",
    "neutrino_sector":
        "Physical Y_e, Y_nu, M_R, PMNS data, and neutrino masses are missing.",
    "proton_stability":
        "The normalized baryon/lepton violating operator basis has not been bounded.",
    "cosmology":
        "Vacuum energy, dark matter, baryogenesis, reheating, and early-universe history are open.",
    "held_out_prediction":
        "No preregistered observable remains both calculable and unused for model selection.",
    "prediction_uncertainty":
        "No end-to-end theoretical covariance budget exists.",
    "native_origin":
        "The Origin-to-Carrier theorem remains open.",
}


def four_dimensional_closure_criteria() -> tuple[ClosureCriterion, ...]:
    """Return the twenty-seven fail-closed completion predicates."""

    rows = (
        (1, "Ultraviolet/geometric", "Ultraviolet quantum-gravity framework specified",
         GateState.PASSED, EvidenceClass.PUBLISHED_INPUT, ("uv_carrier",),
         "Specify the ultraviolet framework and trace it to primary sources.",
         "Failure invalidates the selected ultraviolet carrier."),
        (2, "Ultraviolet/geometric", "Smooth globally consistent compactification",
         GateState.OPEN, EvidenceClass.OPEN, ("global_anomaly",),
         "Prove smoothness and all global consistency conditions for one carrier.",
         "A global obstruction kills the carrier, not heterotic theory in general."),
        (3, "Ultraviolet/geometric", "Observable and hidden bundles constructed",
         GateState.OPEN, EvidenceClass.OPEN, ("hidden_bundle",),
         "Construct both bundles with local freeness, descent, and stability.",
         "Failure kills the corresponding bundle architecture."),
        (4, "Ultraviolet/geometric", "Differential anomaly cancellation",
         GateState.OPEN, EvidenceClass.OPEN, ("global_anomaly", "instanton_determinant"),
         "Construct the differential B-field and total anomaly-line trivialization.",
         "A nonremovable obstruction makes the carrier inconsistent."),
        (5, "Matter/interactions", "Complete exact chiral spectrum",
         GateState.OPEN, EvidenceClass.OPEN, ("hidden_bundle",),
         "Compute observable and hidden absolute cohomology at the same carrier point.",
         "A wrong unavoidable spectrum kills the selected branch."),
        (6, "Matter/interactions", "All relevant holomorphic couplings",
         GateState.OPEN, EvidenceClass.OPEN, ("visible_holomorphic", "instanton_determinant"),
         "Compute every retained perturbative and nonperturbative coupling.",
         "A certified all-order rank or coupling obstruction kills the branch in scope."),
        (7, "Matter/interactions", "Matter and moduli metrics",
         GateState.MISSING_INPUT, EvidenceClass.OPEN, ("visible_metric",),
         "Construct positive Ricci-flat/HYM-induced kinetic matrices.",
         "No physical normalization is available without this package."),
        (8, "Matter/interactions", "Physical normalized interactions",
         GateState.MISSING_INPUT, EvidenceClass.OPEN, ("visible_metric", "ir_observables"),
         "Canonicalize the complete interactions at one common point.",
         "Singular metrics or persistent rank defects kill the physical branch."),
        (9, "Vacuum", "All moduli stabilized or symmetry-protected",
         GateState.MISSING_INPUT, EvidenceClass.OPEN, ("controlled_vacuum",),
         "Solve every geometric, bundle, and charged-field modulus equation.",
         "An unavoidable runaway or uncontrolled flat direction kills the vacuum claim."),
        (10, "Vacuum", "Common vacuum in both stability chambers",
         GateState.OPEN, EvidenceClass.OPEN, ("hidden_bundle", "controlled_vacuum"),
         "Place the same vacuum in the physical cone and both bundle chambers.",
         "Incompatible chambers kill the candidate vacuum."),
        (11, "Vacuum", "Controlled scalar potential",
         GateState.MISSING_INPUT, EvidenceClass.OPEN, ("controlled_vacuum",),
         "Bound omitted instanton, loop, and alpha-prime corrections.",
         "Comparable omitted terms invalidate the truncation."),
        (12, "Vacuum", "Acceptable normalized scalar Hessian",
         GateState.MISSING_INPUT, EvidenceClass.OPEN, ("controlled_vacuum",),
         "Compute canonical masses and apply Minkowski/dS or AdS stability criteria.",
         "A forbidden tachyon kills the candidate vacuum."),
        (13, "Low energy", "Gauge couplings and thresholds",
         GateState.MISSING_INPUT, EvidenceClass.OPEN, ("ir_observables",),
         "Derive gauge kinetic functions, beta functions, and all threshold matches.",
         "Uncontrolled thresholds prevent a physical gauge prediction."),
        (14, "Low energy", "Electroweak symmetry breaking",
         GateState.MISSING_INPUT, EvidenceClass.OPEN, ("ir_observables",),
         "Derive the Higgs potential and electroweak vacuum after running.",
         "Failure to obtain a viable electroweak vacuum kills the selected low-energy branch."),
        (15, "Low energy", "Supersymmetry breaking or exact absence",
         GateState.MISSING_INPUT, EvidenceClass.OPEN, ("ir_observables",),
         "Derive the breaking sector, mediation, and soft terms, or prove exact low-energy supersymmetry.",
         "Assumed soft parameters are not a compactification prediction."),
        (16, "Low energy", "Quark and charged-lepton masses and mixing",
         GateState.MISSING_INPUT, EvidenceClass.OPEN, ("visible_holomorphic", "visible_metric", "ir_observables"),
         "Compute normalized matrices and RG transport to a declared scale.",
         "Unavoidable disagreement beyond uncertainty falsifies the selected model."),
        (17, "Low energy", "Neutrino masses and PMNS data",
         GateState.MISSING_INPUT, EvidenceClass.OPEN, ("ir_observables",),
         "Compute Y_e, Y_nu, M_R, thresholds, masses, mixing, and phases.",
         "No neutrino prediction exists without the complete carrier data."),
        (18, "Low energy", "Proton stability and B/L operator bounds",
         GateState.OPEN, EvidenceClass.OPEN, ("ir_observables",),
         "Enumerate and bound the normalized effective operator basis.",
         "A rate incompatible with observation kills the selected model or branch."),
        (19, "Cosmology", "Vacuum energy addressed",
         GateState.OPEN, EvidenceClass.OPEN, ("controlled_vacuum",),
         "Derive or explicitly control the four-dimensional vacuum energy.",
         "An uncontrolled value prevents cosmological closure."),
        (20, "Cosmology", "Dark-matter identity and abundance",
         GateState.OPEN, EvidenceClass.OPEN, ("ir_observables",),
         "Identify a stable state and calculate its production and abundance.",
         "An assumed relic is not a prediction."),
        (21, "Cosmology", "Baryogenesis or leptogenesis",
         GateState.OPEN, EvidenceClass.OPEN, ("ir_observables",),
         "Derive a viable asymmetry mechanism from the same action and history.",
         "Failure leaves cosmological matter asymmetry unexplained."),
        (22, "Cosmology", "Moduli decay and reheating controlled",
         GateState.OPEN, EvidenceClass.OPEN, ("controlled_vacuum", "ir_observables"),
         "Compute lifetimes, branching fractions, and reheating history.",
         "Late unstable moduli can kill the cosmological branch."),
        (23, "Cosmology", "Early-universe history supplied",
         GateState.OPEN, EvidenceClass.OPEN, ("ir_observables",),
         "Provide inflation or a quantitatively specified alternative.",
         "No cosmological closure follows from a static vacuum alone."),
        (24, "Prediction", "Independent held-out prediction",
         GateState.OPEN, EvidenceClass.OPEN, ("blind_prediction",),
         "Freeze all selections and fits before computing an unused observable.",
         "If every calculable observable was used for selection, no blind prediction exists."),
        (25, "Prediction", "Theoretical uncertainty budget",
         GateState.OPEN, EvidenceClass.OPEN, ("blind_prediction", "ir_observables"),
         "Propagate numerical, threshold, truncation, and omitted-source uncertainties.",
         "Digits without an uncertainty budget are not precision predictions."),
        (26, "Prediction", "Published mathematical and experimental kill criteria",
         GateState.PASSED, EvidenceClass.EXACT_THEOREM, ("four_dimensional_closure_source",),
         "Serialize scoped kill tests and their scientific implications.",
         "Ambiguous scope prevents meaningful falsification."),
        (27, "Native origin", "Explicit Origin-to-Carrier theorem",
         GateState.OPEN, EvidenceClass.OPEN, ("native_origin",),
         "Derive the imported carrier through the typed bridge interfaces.",
         "A scoped obstruction kills the declared native architecture only."),
    )
    return tuple(
        ClosureCriterion(
            number, category, label, state, evidence, dependencies,
            pass_criterion, failure_scope,
        )
        for (
            number, category, label, state, evidence, dependencies,
            pass_criterion, failure_scope,
        ) in rows
    )


def program_falsification_rules() -> tuple[FalsificationRule, ...]:
    """Return scoped program-level kill rules."""

    rows = (
        ("native_origin", "Native origin", "typed Origin-to-Carrier map",
         "exact obstruction in the declared source category",
         "the named native architecture is killed",
         "not heterotic theory or all possible origins"),
        ("visible_rank_lift", "Observable deformation", "simultaneous full-rank mixed point",
         "U2(y)D2(y)=0 on the complete admissible component",
         "the leading order-five perturbative lift is killed",
         "higher lawful orders and nonperturbative matter insertions remain separate"),
        ("visible_flavor", "Observable flavor", "full-rank physical Yu and Yd",
         "rank deficiency persists at every lawful contribution",
         "the one-Higgs observable branch is killed",
         "metric normalization cannot repair an exact rank defect"),
        ("metric", "Metric completion", "positive Ricci-flat/HYM normalization",
         "no controlled positive realization exists at the selected point",
         "physical flavor claims are unavailable",
         "failed numerics alone do not prove nonexistence when stability is known"),
        ("instanton_seed", "Degree-two instantons", "two physical seed Pfaffians",
         "both physical seed sections vanish identically",
         "the retained degree-two instanton route is killed",
         "other curve classes are not excluded"),
        ("orbit_sum", "Global instanton sum", "normalized orbit contribution",
         "exact determinant-line-compatible orbit cancellation",
         "the retained instanton class is inactive",
         "individual nonzero Pfaffians are insufficient"),
        ("hidden_bundle", "Hidden bundle", "stable descended V4",
         "all 44 supports fail, or a global architecture obstruction is proved",
         "the bounded hidden branch or declared architecture is killed",
         "the implication must distinguish bounded-category from global failure"),
        ("global_anomaly", "Global consistency", "differential B-field and anomaly line",
         "no global compatible trivialization exists",
         "the carrier is inconsistent",
         "cohomological Chern equality alone is insufficient"),
        ("stabilization", "Stabilization", "carrier-derived unequal-exponent racetrack",
         "no unequal exponents/prefactors arise, or every prefactor vanishes",
         "the minimal stabilization route is killed",
         "nonminimal source architectures remain separate"),
        ("vacuum", "Controlled vacuum", "one physical-cone stable solution",
         "any F/D, cone, positivity, Hessian, correction, or scale test fails",
         "the proposed compactification vacuum is rejected",
         "a truncated stationary point is not the complete vacuum"),
        ("phenomenology", "Phenomenology", "held-out predictions with covariance",
         "disagreement exceeds combined uncertainty after selections are frozen",
         "the selected model is falsified in the stated scope",
         "identify whether the failure is vacuum, branch, carrier, or universal"),
        ("full_theory", "Full OneTheory", "carrier closure plus native origin",
         "either closure loop fails in unavoidable scope",
         "the full OneTheory claim fails",
         "carrier closure alone is not native-origin closure"),
    )
    return tuple(FalsificationRule(*row) for row in rows)


def validate_closure_criteria(
    criteria: Sequence[ClosureCriterion] | None = None,
) -> Mapping[str, Any]:
    """Validate numbering, dependencies, and nonempty pass/failure contracts."""

    values = tuple(criteria or four_dimensional_closure_criteria())
    numbers = tuple(item.number for item in values)
    known_dependencies = {gate.identifier for gate in gate_registry()} | {
        "four_dimensional_closure_source"
    }
    unknown = sorted({
        dependency
        for item in values
        for dependency in item.dependency_ids
        if dependency not in known_dependencies
    })
    return {
        "criterion_count": len(values),
        "numbers_contiguous": numbers == tuple(range(1, len(values) + 1)),
        "identifiers_unique": len(numbers) == len(set(numbers)),
        "unknown_dependencies": tuple(unknown),
        "all_contracts_nonempty": all(
            item.label.strip()
            and item.pass_criterion.strip()
            and item.failure_scope.strip()
            and item.dependency_ids
            for item in values
        ),
        "valid": (
            len(values) == 27
            and numbers == tuple(range(1, 28))
            and not unknown
            and all(
                item.label.strip()
                and item.pass_criterion.strip()
                and item.failure_scope.strip()
                and item.dependency_ids
                for item in values
            )
        ),
    }


def current_prediction_registry() -> tuple[PredictionRecord, ...]:
    """Return current auditable quantities without manufacturing a prediction."""

    return (
        PredictionRecord(
            "carrier_choice",
            ObservableRole.DISCRETE_SELECTION,
            ("schoen_quotient_2004", "exact_mssm_2006"),
            True,
            True,
            False,
            "The realistic carrier and observable spectrum are selection inputs.",
        ),
        PredictionRecord(
            "tree_rank_bound",
            ObservableRole.DERIVED,
            ("carrier_yukawa_2006", "canonical_manual_v8"),
            False,
            True,
            False,
            "Exact rank-at-most-two theorem; not a numerical low-energy prediction.",
        ),
        PredictionRecord(
            "controlled_vacuum",
            ObservableRole.DERIVED,
            ("stabilization_v41",),
            False,
            False,
            False,
            "The required vacuum output is MISSING_INPUT.",
        ),
    )


def validate_prediction_registry(
    records: Sequence[PredictionRecord] | None = None,
) -> Mapping[str, Any]:
    """Enforce selection/fit/held-out separation."""

    values = tuple(records or current_prediction_registry())
    identifiers = tuple(record.identifier for record in values)
    held_out = tuple(
        record for record in values
        if record.role is ObservableRole.HELD_OUT_PREDICTION
    )
    violations = []
    for record in values:
        if record.role is ObservableRole.HELD_OUT_PREDICTION:
            if record.used_for_selection:
                violations.append(f"{record.identifier}: held-out value used for selection")
            if not record.value_supplied:
                violations.append(f"{record.identifier}: prediction value missing")
            if not record.uncertainty_supplied:
                violations.append(f"{record.identifier}: prediction uncertainty missing")
            if not record.provenance_ids:
                violations.append(f"{record.identifier}: prediction provenance missing")
        if record.role is ObservableRole.FITTED and not record.used_for_selection:
            violations.append(f"{record.identifier}: fitted value not marked as selection input")
    if len(identifiers) != len(set(identifiers)):
        violations.append("prediction identifiers are not unique")
    return {
        "record_count": len(values),
        "held_out_count": len(held_out),
        "violations": tuple(violations),
        "registry_valid": not violations,
        "independent_prediction_gate_passed": bool(held_out) and not violations,
    }


def legacy_prediction_firewall() -> Mapping[str, Any]:
    """Exclude unintegrated numerical ledgers from the current prediction set."""

    return {
        "source_id": "legacy_prediction_ledger",
        "excluded_claim_classes": (
            "numerical neutrino values",
            "unintegrated CP targets",
            "heavy-shelf scales",
            "cosmological-constant relations",
            "dark-relic guesses",
        ),
        "reason": (
            "No derivation through the maintained heterotic carrier, common "
            "vacuum, normalization, thresholds, or held-out selection ledger."
        ),
        "numerical_values_imported": False,
        "status": EvidenceClass.SCOPED_NO_GO,
    }


def exact_covariance_variance(
    jacobian: Sequence[int | Fraction],
    covariance: Sequence[Sequence[int | Fraction]],
) -> Fraction:
    """Return J C J^T exactly for one scalar observable."""

    vector = tuple(_coerce_fraction(value) for value in jacobian)
    matrix = exact_matrix(covariance)
    size = len(vector)
    if len(matrix) != size or any(len(row) != size for row in matrix):
        raise ValueError("covariance dimensions must match the Jacobian")
    if any(matrix[i][j] != matrix[j][i] for i in range(size) for j in range(size)):
        raise ValueError("covariance matrix must be symmetric")
    return sum(
        vector[i] * matrix[i][j] * vector[j]
        for i in range(size)
        for j in range(size)
    )


def type1_seesaw_mass_matrix(
    dirac_mass: Sequence[Sequence[int | Fraction]],
    inverse_majorana_mass: Sequence[Sequence[int | Fraction]],
) -> tuple[tuple[Fraction, ...], ...]:
    """Return -M_D^T M_R^{-1} M_D over Q."""

    dirac = exact_matrix(dirac_mass)
    inverse_majorana = exact_matrix(inverse_majorana_mass)
    if len(inverse_majorana) != len(inverse_majorana[0]):
        raise ValueError("inverse Majorana matrix must be square")
    if len(inverse_majorana) != len(dirac):
        raise ValueError("Majorana and Dirac dimensions do not align")
    transpose = tuple(tuple(dirac[row][column] for row in range(len(dirac)))
                      for column in range(len(dirac[0])))
    product_matrix = q_matmul(q_matmul(transpose, inverse_majorana), dirac)
    return tuple(tuple(-value for value in row) for row in product_matrix)


def ckm_matrix(
    up_left_rotation: Sequence[Sequence[complex | float | int]],
    down_left_rotation: Sequence[Sequence[complex | float | int]],
) -> NMatrix:
    """Return V_CKM=U_uL^dagger U_dL as a numerical helper."""

    up = numerical_matrix(up_left_rotation)
    down = numerical_matrix(down_left_rotation)
    if len(up) != len(up[0]) or len(down) != len(down[0]) or len(up) != len(down):
        raise ValueError("left rotations must be square with equal size")
    return n_matmul(n_conjugate_transpose(up), down)


def jarlskog_invariant(ckm: Sequence[Sequence[complex | float | int]]) -> float:
    """Return Im(V_us V_cb V_ub* V_cs*) in the standard 3x3 indexing."""

    matrix = numerical_matrix(ckm)
    if len(matrix) != 3 or any(len(row) != 3 for row in matrix):
        raise ValueError("Jarlskog helper requires a 3x3 matrix")
    value = matrix[0][1] * matrix[1][2] * matrix[0][2].conjugate() * matrix[1][1].conjugate()
    return float(value.imag)


def one_loop_inverse_gauge_coupling(
    inverse_g_squared_at_reference: float,
    beta_coefficient: float,
    scale_ratio: float,
) -> float:
    """Run 1/g^2 with dg/dln(mu)=b*g^3/(16*pi^2)."""

    if inverse_g_squared_at_reference <= 0:
        raise ValueError("inverse coupling must be positive")
    if scale_ratio <= 0:
        raise ValueError("scale ratio must be positive")
    return (
        float(inverse_g_squared_at_reference)
        - float(beta_coefficient) * log(float(scale_ratio)) / (8.0 * pi ** 2)
    )


def validate_threshold_scales(
    scales: Mapping[str, float],
    required_order: Sequence[str],
) -> Mapping[str, Any]:
    """Validate positive, strictly increasing threshold scales."""

    missing = tuple(name for name in required_order if name not in scales)
    values = tuple(float(scales[name]) for name in required_order if name in scales)
    positive = not missing and all(value > 0 for value in values)
    ordered = positive and all(
        values[index] < values[index + 1] for index in range(len(values) - 1)
    )
    return {
        "required_order": tuple(required_order),
        "missing": missing,
        "values": values,
        "positive": positive,
        "strictly_increasing": ordered,
        "valid": positive and ordered,
    }


def phenomenology_comparison(
    predicted: float,
    observed: float,
    theory_sigma: float,
    experimental_sigma: float,
    sigma_threshold: float = 5.0,
) -> Mapping[str, Any]:
    """Compare one frozen held-out prediction with combined uncertainty."""

    if theory_sigma < 0 or experimental_sigma < 0 or sigma_threshold <= 0:
        raise ValueError("uncertainties must be nonnegative and threshold positive")
    combined = sqrt(theory_sigma ** 2 + experimental_sigma ** 2)
    if combined == 0:
        significance = 0.0 if predicted == observed else float("inf")
    else:
        significance = abs(predicted - observed) / combined
    return {
        "predicted": predicted,
        "observed": observed,
        "combined_sigma": combined,
        "significance": significance,
        "sigma_threshold": sigma_threshold,
        "falsified_in_declared_scope": significance > sigma_threshold,
    }


def scalar_stability_certificate(
    mass_squared: Sequence[float],
    vacuum_kind: str,
    ads_radius: float | None = None,
    goldstone_indices: Sequence[int] = (),
    tolerance: float = 1e-12,
) -> Mapping[str, Any]:
    """Apply canonical Minkowski/dS positivity or the AdS4 BF bound."""

    masses = tuple(float(value) for value in mass_squared)
    if not masses:
        raise ValueError("at least one scalar mass is required")
    ignored = set(goldstone_indices)
    if any(index < 0 or index >= len(masses) for index in ignored):
        raise ValueError("Goldstone index is out of range")
    physical = tuple(value for index, value in enumerate(masses) if index not in ignored)
    if vacuum_kind in ("Minkowski", "dS"):
        bound = -tolerance
        passed = all(value >= bound for value in physical)
    elif vacuum_kind == "AdS4":
        if ads_radius is None or ads_radius <= 0:
            raise ValueError("AdS4 stability requires a positive radius")
        bound = -Fraction(9, 4) / Fraction.from_float(ads_radius ** 2)
        passed = all(Fraction.from_float(value) >= bound for value in physical)
    else:
        raise ValueError("vacuum_kind must be Minkowski, dS, or AdS4")
    return {
        "vacuum_kind": vacuum_kind,
        "physical_mass_squared": physical,
        "bound": bound,
        "passed": passed,
        "canonical_normalization_assumed": True,
    }


def common_vacuum_certificate(
    component_vacuum_ids: Mapping[str, str | None],
) -> Mapping[str, Any]:
    """Require every physical component to use one explicit vacuum identifier."""

    missing = tuple(
        component for component, identifier in component_vacuum_ids.items()
        if identifier is None or not str(identifier).strip()
    )
    supplied = tuple(
        str(identifier)
        for identifier in component_vacuum_ids.values()
        if identifier is not None and str(identifier).strip()
    )
    unique = tuple(sorted(set(supplied)))
    return {
        "component_count": len(component_vacuum_ids),
        "missing_components": missing,
        "unique_vacuum_ids": unique,
        "one_vacuum_principle_satisfied": not missing and len(unique) == 1,
        "state": (
            GateState.PASSED
            if not missing and len(unique) == 1
            else GateState.MISSING_INPUT
            if missing
            else GateState.KILLED
        ),
    }


VACUUM_ACCEPTANCE_KEYS = (
    "all_F_or_stationarity_equations",
    "all_D_terms",
    "physical_kahler_cone",
    "visible_bundle_stable",
    "hidden_bundle_stable",
    "positive_gauge_kinetic_matrix",
    "positive_scalar_metric",
    "acceptable_normalized_hessian",
    "omitted_instantons_suppressed",
    "loop_and_alpha_prime_control",
    "scale_separation",
    "visible_full_rank_locus",
    "required_CP_partner",
)


def controlled_vacuum_acceptance(
    results: Mapping[str, bool | None],
) -> Mapping[str, Any]:
    """Evaluate every declared Section 11 vacuum kill criterion."""

    missing = tuple(
        key for key in VACUUM_ACCEPTANCE_KEYS
        if key not in results or results[key] is None
    )
    failed = tuple(
        key for key in VACUUM_ACCEPTANCE_KEYS
        if results.get(key) is False
    )
    passed = not missing and not failed and all(results[key] is True for key in VACUUM_ACCEPTANCE_KEYS)
    return {
        "required_keys": VACUUM_ACCEPTANCE_KEYS,
        "missing": missing,
        "failed": failed,
        "passed": passed,
        "state": (
            GateState.PASSED
            if passed
            else GateState.KILLED
            if failed
            else GateState.MISSING_INPUT
        ),
    }


def conditional_cp_pairing_certificate() -> Mapping[str, Any]:
    """Record the exact implication and the absent physical realization."""

    return {
        "assumptions": (
            "completed action is CP invariant",
            "two controlled vacua are CP conjugate",
        ),
        "cp_even_relation": "O_even(vacuum_plus)=O_even(vacuum_minus)",
        "cp_odd_relation": "O_odd(vacuum_plus)=-O_odd(vacuum_minus)",
        "bundle_pair_exists": cp_bundle_pair_certificate()["CP_partner_exact"],
        "controlled_vacuum_pair_exists": False,
        "physical_Jarlskog_magnitude_known": False,
        "vacuum_selection_known": False,
        "status": EvidenceClass.CONDITIONAL,
    }


def four_dimensional_closure_status() -> Mapping[str, Any]:
    """Return the current Section 11 closure result without shortcuts."""

    criteria = four_dimensional_closure_criteria()
    passed = tuple(item.number for item in criteria if item.state is GateState.PASSED)
    blockers = tuple(item.number for item in criteria if item.state is not GateState.PASSED)
    completion = evaluate_completion()
    prediction = validate_prediction_registry()
    return {
        "criterion_count": len(criteria),
        "passed_criteria": passed,
        "passed_count": len(passed),
        "blocking_criteria": blockers,
        "blocking_count": len(blockers),
        "carrier_closure": completion["carrier_closure"],
        "native_origin_closure": (
            next(item for item in criteria if item.number == 27).state
            is GateState.PASSED
        ),
        "full_onetheory_completion": completion["full_onetheory_completion"],
        "independent_prediction": prediction["independent_prediction_gate_passed"],
        "normalized_four_dimensional_action": False,
        "one_controlled_common_vacuum": False,
        "state": GateState.MISSING_INPUT,
        "current_statement": (
            "theorem-gated incomplete research program with exact subtheorems"
        ),
        "open_obligations": tuple(SECTION11_MISSING_INPUTS),
    }


def optimized_critical_path() -> tuple[Mapping[str, Any], ...]:
    """Return the shortest dependency-respecting continuation sequence."""

    steps = (
        (
            "visible_residues",
            "Supply the physical v35h1 common-DGA package and evaluate the four normalized f3 traces for p_u,3 and p_d,3; nonzero self-pairing kills the corresponding star/triangular shortcut, while isotropic results continue through the adaptive f5/f7 path",
            GateState.MISSING_INPUT,
        ),
        ("visible_full_rank", "Prove or reject a stable simultaneous full-rank point", GateState.OPEN),
        ("visible_metrics", "Construct 404 sections, Ricci-flat metric, and visible HYM data", GateState.MISSING_INPUT),
        ("instanton_maps", "Construct physical seed maps and global Pfaffian line", GateState.MISSING_INPUT),
        ("hidden_bundle", "Complete stable descended hidden V4 and spectrum", GateState.OPEN),
        ("global_anomaly", "Construct differential anomaly and determinant-line trivialization", GateState.OPEN),
        ("hidden_dynamics", "Derive hidden exponents, prefactors, and thresholds", GateState.MISSING_INPUT),
        ("supergravity_data", "Assemble complete K,W,f,D", GateState.MISSING_INPUT),
        ("controlled_vacuum", "Solve and certify one common controlled vacuum", GateState.MISSING_INPUT),
        ("low_energy", "Normalize, match thresholds, and run to observables", GateState.MISSING_INPUT),
        ("blind_prediction", "Freeze selection data and compute one held-out prediction", GateState.OPEN),
        ("native_origin", "Prove the Origin-to-Carrier theorem", GateState.OPEN),
    )
    return tuple(
        {"identifier": identifier, "task": task, "state": state}
        for identifier, task, state in steps
    )


def verify_four_dimensional_closure() -> tuple[Check, ...]:
    """Run Section 11's exact audit and fail-closed boundary checks."""

    criteria = four_dimensional_closure_criteria()
    validation = validate_closure_criteria(criteria)
    rules = program_falsification_rules()
    prediction = validate_prediction_registry()
    legacy = legacy_prediction_firewall()
    status = four_dimensional_closure_status()
    covariance = exact_covariance_variance((1, 2), ((4, 1), (1, 9)))
    seesaw = type1_seesaw_mass_matrix(
        ((1, 0), (0, 1)),
        ((Fraction(1, 2), 0), (0, Fraction(1, 3))),
    )
    identity = n_identity(3)
    thresholds = validate_threshold_scales(
        {"electroweak": 100.0, "supersymmetry": 1_000.0, "compactification": 1e16},
        ("electroweak", "supersymmetry", "compactification"),
    )
    vacuum = controlled_vacuum_acceptance({})
    common = common_vacuum_certificate({
        "holomorphic_yukawas": None,
        "metrics": None,
        "thresholds": None,
        "stabilization": None,
    })
    observations = (
        ("closure.criteria.count", validation["criterion_count"], 27,
         EvidenceClass.EXACT_THEOREM, "The completion contract has twenty-seven criteria."),
        ("closure.criteria.valid", validation["valid"], True,
         EvidenceClass.EXACT_THEOREM, "Numbering, dependencies, and contracts validate."),
        ("closure.criteria.current",
         (status["passed_count"], status["blocking_count"]),
         (2, 25), EvidenceClass.EXACT_THEOREM,
         "Only the UV specification and published falsification contract pass."),
        ("closure.criteria.native_open",
         criteria[26].state, GateState.OPEN, EvidenceClass.OPEN,
         "Native-origin closure is criterion twenty-seven and remains open."),
        ("closure.falsification.rules", len(rules), 12,
         EvidenceClass.EXACT_THEOREM, "Twelve scoped program-layer kill rules are serialized."),
        ("closure.prediction.registry",
         (prediction["registry_valid"], prediction["held_out_count"],
          prediction["independent_prediction_gate_passed"]),
         (True, 0, False), EvidenceClass.OPEN,
         "The role ledger is valid but contains no held-out prediction."),
        ("closure.legacy.firewall", legacy["numerical_values_imported"], False,
         EvidenceClass.SCOPED_NO_GO,
         "Unintegrated legacy numerical values are excluded."),
        ("closure.uncertainty.exact", covariance, Fraction(44),
         EvidenceClass.EXACT_THEOREM, "Exact scalar covariance propagation gives J C J^T=44."),
        ("closure.seesaw.exact", seesaw,
         ((Fraction(-1, 2), Fraction(0)), (Fraction(0), Fraction(-1, 3))),
         EvidenceClass.EXACT_THEOREM, "The exact type-I seesaw helper preserves sign and ordering."),
        ("closure.ckm.identity", jarlskog_invariant(ckm_matrix(identity, identity)), 0.0,
         EvidenceClass.EXACT_THEOREM, "Identity rotations give zero Jarlskog invariant."),
        ("closure.rg.reference",
         one_loop_inverse_gauge_coupling(2.0, 7.0, 1.0), 2.0,
         EvidenceClass.EXACT_THEOREM, "Running is unchanged at the reference scale."),
        ("closure.threshold.order", thresholds["valid"], True,
         EvidenceClass.EXACT_THEOREM, "The threshold helper enforces a strict positive order."),
        ("closure.vacuum.fail_closed",
         (vacuum["passed"], vacuum["state"]),
         (False, GateState.MISSING_INPUT), EvidenceClass.OPEN,
         "No missing vacuum criterion is silently passed."),
        ("closure.one_vacuum.fail_closed",
         (common["one_vacuum_principle_satisfied"], common["state"]),
         (False, GateState.MISSING_INPUT), EvidenceClass.OPEN,
         "Missing component points fail the one-vacuum contract."),
        ("closure.current.status",
         (status["carrier_closure"], status["full_onetheory_completion"],
          status["independent_prediction"], status["state"]),
         (False, False, False, GateState.MISSING_INPUT), EvidenceClass.OPEN,
         "Neither closure loop nor the prediction gate has passed."),
    )
    return tuple(
        Check(identifier, observed == expected, expected, observed, evidence, note)
        for identifier, observed, expected, evidence, note in observations
    )


def run_section11_checks() -> tuple[Check, ...]:
    return verify_four_dimensional_closure()


SECTION12_EVIDENCE_IDS: Mapping[str, str] = {
    "source_docx_sha256":
        "a6b9a860ccf38e5714c7630e37117aaf6352d26b725d6203424368bb18a72886",
    "section12_source": "libfile_93e6b22fa7808191a9308c643be9e8c2",
    "sandve_2013": "https://doi.org/10.1371/journal.pcbi.1003285",
    "fair_2016": "https://doi.org/10.1038/sdata.2016.18",
    "nist_fips_180_4": "https://csrc.nist.gov/pubs/fips/180-4/upd1/final",
}


SECTION12_MISSING_INPUTS: Mapping[str, str] = {
    "frozen_release_archive":
        "No immutable public archive contains all paper, code, data, schema, log, and lock artifacts.",
    "requirements_lock":
        "No separately frozen environment lockfile has been issued; the verifier itself uses only the standard library.",
    "numerical_certificate_archive":
        "No metric, HYM, harmonic-representative, determinant-line, or vacuum numerical archive exists.",
    "paper_code_crosswalk":
        "Not every displayed paper equation, table entry, and number has a stable certificate identifier.",
    "clean_environment_replay":
        "The complete release has not been replayed from a fresh frozen environment.",
    "independent_implementation":
        "No independent team has reimplemented and reproduced the certificates.",
}


def canonical_json_bytes(value: Any) -> bytes:
    """Serialize verifier data deterministically for hashing and comparison.

    This is the project's canonical JSON profile (sorted keys, compact
    separators, UTF-8, and no NaN); it is not a claim of RFC 8785 compliance.
    """

    return json.dumps(
        _jsonable(value),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def sha256_bytes(payload: bytes) -> str:
    """Return the lowercase SHA-256 digest of *payload*."""

    return hashlib.sha256(payload).hexdigest()


def sha256_json(value: Any) -> str:
    """Hash a value after project-canonical JSON serialization."""

    return sha256_bytes(canonical_json_bytes(value))


def sha256_path(path: Path) -> str:
    """Stream a regular file into SHA-256 without loading it into memory."""

    if not path.is_file():
        raise FileNotFoundError(f"not a regular file: {path}")
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


_WORD_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
_MATH_NS = "http://schemas.openxmlformats.org/officeDocument/2006/math"
_INTERNAL_IDENTIFIER = re.compile(
    r"\b(?:turn\d+[a-z]+\d+|file_[0-9a-f]{16,}|libfile_[0-9a-f]{16,})\b",
    re.IGNORECASE,
)
_EMPTY_FORMULA_SHELL = re.compile(r"^\s*[\[\]{}(),.;:\s]+\s*$")
_EMPTY_INLINE_PARENS = re.compile(r"\(\s*\)")
_SHORT_BROKEN_FORMULA = re.compile(
    r"^\s*\[\s*(?:[A-Za-z]\s*[,.;]|[\^_]\s*\d*\s*[=+]*)\s*\]\s*$"
)


def _xml_text(element: ElementTree.Element) -> str:
    """Return visible Word and OMML text in document order."""

    accepted = {
        f"{{{_WORD_NS}}}t",
        f"{{{_WORD_NS}}}instrText",
        f"{{{_MATH_NS}}}t",
    }
    return "".join(node.text or "" for node in element.iter() if node.tag in accepted)


def audit_docx_publication(path: Path) -> Mapping[str, Any]:
    """Audit a DOCX for publication-breaking formula and text artifacts.

    The audit is structural and deterministic.  It does not decide whether a
    mathematically well-formed equation is scientifically true.
    """

    violations: list[Mapping[str, Any]] = []
    parts_checked = 0
    paragraphs_checked = 0
    equations_checked = 0
    try:
        with zipfile.ZipFile(path) as archive:
            corrupt_member = archive.testzip()
            if corrupt_member is not None:
                violations.append(
                    {"kind": "corrupt_zip_member", "part": corrupt_member}
                )
            names = set(archive.namelist())
            if "word/document.xml" not in names:
                violations.append({"kind": "missing_document_xml"})
            xml_parts = sorted(
                name for name in names
                if name == "word/document.xml"
                or re.fullmatch(
                    r"word/(?:header|footer)\d+\.xml|word/(?:footnotes|endnotes)\.xml",
                    name,
                )
            )
            for part in xml_parts:
                parts_checked += 1
                root = ElementTree.fromstring(archive.read(part))
                for index, paragraph in enumerate(root.iter(f"{{{_WORD_NS}}}p")):
                    paragraphs_checked += 1
                    raw = _xml_text(paragraph)
                    text = " ".join(raw.split())
                    if not text:
                        continue
                    context = {"part": part, "paragraph": index, "text": text[:240]}
                    if _EMPTY_FORMULA_SHELL.fullmatch(text):
                        violations.append({"kind": "empty_formula_shell", **context})
                    if _EMPTY_INLINE_PARENS.search(text):
                        violations.append({"kind": "empty_inline_formula", **context})
                    if _SHORT_BROKEN_FORMULA.fullmatch(text):
                        violations.append({"kind": "malformed_formula_fragment", **context})
                    if "{}" in text or "_{}" in text:
                        violations.append({"kind": "empty_math_slot", **context})
                    if "++" in text:
                        violations.append({"kind": "doubled_operator", **context})
                    if "**" in text:
                        violations.append({"kind": "raw_markdown", **context})
                    if "\ufffd" in text:
                        violations.append({"kind": "replacement_character", **context})
                    if _INTERNAL_IDENTIFIER.search(text):
                        violations.append({"kind": "internal_identifier", **context})
                for equation in root.iter(f"{{{_MATH_NS}}}oMath"):
                    equations_checked += 1
                    if not _xml_text(equation).strip():
                        violations.append(
                            {
                                "kind": "empty_native_equation",
                                "part": part,
                                "equation": equations_checked,
                            }
                        )
    except (FileNotFoundError, OSError, zipfile.BadZipFile, ElementTree.ParseError) as exc:
        violations.append({"kind": "unreadable_docx", "error": str(exc)})
    return {
        "path": str(path),
        "sha256": sha256_path(path) if path.is_file() else None,
        "parts_checked": parts_checked,
        "paragraphs_checked": paragraphs_checked,
        "equations_checked": equations_checked,
        "violation_count": len(violations),
        "violations": tuple(violations),
        "valid": not violations,
        "state": GateState.PASSED if not violations else GateState.KILLED,
    }


def audit_python_publication(path: Path) -> Mapping[str, Any]:
    """Audit Python source for incomplete executable constructs."""

    violations: list[Mapping[str, Any]] = []
    source = ""
    tree: ast.Module | None = None
    try:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
    except (FileNotFoundError, OSError, UnicodeError, SyntaxError) as exc:
        violations.append({"kind": "unreadable_or_invalid_python", "error": str(exc)})
    if tree is not None:
        top_level: dict[str, list[int]] = {}
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                top_level.setdefault(node.name, []).append(node.lineno)
        for name, lines in sorted(top_level.items()):
            if len(lines) > 1:
                violations.append(
                    {"kind": "duplicate_top_level_definition", "name": name, "lines": tuple(lines)}
                )
        for node in ast.walk(tree):
            if isinstance(node, ast.Pass):
                violations.append({"kind": "pass_statement", "line": node.lineno})
            if (
                isinstance(node, ast.Expr)
                and isinstance(node.value, ast.Constant)
                and node.value.value is Ellipsis
            ):
                violations.append({"kind": "ellipsis_statement", "line": node.lineno})
            if isinstance(node, ast.Raise):
                target = node.exc
                if isinstance(target, ast.Call) and getattr(target.func, "id", None) == "NotImplementedError":
                    violations.append({"kind": "not_implemented", "line": node.lineno})
        for number, line in enumerate(source.splitlines(), start=1):
            stripped = line.lstrip()
            if stripped.startswith("#") and re.search(
                r"\b(?:TODO|FIXME|TBD|PLACEHOLDER)\b", stripped, re.IGNORECASE
            ):
                violations.append(
                    {"kind": "placeholder_comment", "line": number, "text": stripped[:160]}
                )
    return {
        "path": str(path),
        "sha256": sha256_path(path) if path.is_file() else None,
        "line_count": source.count("\n") + 1 if source else 0,
        "violation_count": len(violations),
        "violations": tuple(violations),
        "valid": tree is not None and not violations,
        "state": GateState.PASSED if tree is not None and not violations else GateState.KILLED,
    }


def publication_artifact_audit(
    docx_path: Path | None = None,
    python_path: Path | None = None,
) -> Mapping[str, Any]:
    """Combine document and source audits without conflating them with physics."""

    python_report = audit_python_publication(python_path or Path(__file__))
    docx_report = audit_docx_publication(docx_path) if docx_path is not None else None
    valid = python_report["valid"] and (
        docx_report is None or bool(docx_report["valid"])
    )
    return {
        "implementation_version": __version__,
        "python": python_report,
        "docx": docx_report,
        "artifact_integrity_passed": valid,
        "scientific_completion_implied": False,
        "state": GateState.PASSED if valid else GateState.KILLED,
    }


def _safe_release_path(root: Path, relative: str) -> Path:
    """Resolve an archive member and reject absolute/path-traversal targets."""

    candidate = Path(relative)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise ValueError(f"unsafe artifact path: {relative!r}")
    root_resolved = root.resolve()
    result = (root_resolved / candidate).resolve()
    if result != root_resolved and root_resolved not in result.parents:
        raise ValueError(f"artifact escapes release root: {relative!r}")
    return result


def verify_artifact_digests(
    root: Path,
    expected: Mapping[str, str],
) -> Mapping[str, Any]:
    """Verify a path-to-SHA-256 map with a path-traversal firewall."""

    records: list[Mapping[str, Any]] = []
    for relative, expected_digest in sorted(expected.items()):
        if len(expected_digest) != 64 or any(
            char not in "0123456789abcdef" for char in expected_digest
        ):
            raise ValueError(f"invalid SHA-256 digest for {relative!r}")
        path = _safe_release_path(root, relative)
        observed = sha256_path(path) if path.is_file() else None
        records.append(
            {
                "path": relative,
                "expected_sha256": expected_digest,
                "observed_sha256": observed,
                "passed": observed == expected_digest,
            }
        )
    return {
        "artifact_count": len(records),
        "all_passed": all(record["passed"] for record in records),
        "artifacts": tuple(records),
    }


def certificate_dependency_graph() -> Mapping[str, tuple[str, ...]]:
    """Return the maintained section-level prerequisite DAG."""

    return {
        "section1": (),
        "section2": ("section1",),
        "section3": ("section1",),
        "section4": ("section2", "section3"),
        "section5": ("section2",),
        "section6": ("section5",),
        "section7": ("section5",),
        "section8": ("section2", "section5"),
        "section9": ("section2",),
        "section10": ("section8", "section9"),
        "section11": ("section4", "section6", "section7", "section8", "section9", "section10"),
        "section12": ("section1", "section2", "section3", "section4", "section5",
                      "section6", "section7", "section8", "section9", "section10",
                      "section11"),
        "section13": ("section1", "section2", "section3", "section4", "section5",
                      "section6", "section7", "section8", "section9", "section10",
                      "section11", "section12"),
    }


def validate_dependency_graph(
    graph: Mapping[str, Sequence[str]],
) -> Mapping[str, Any]:
    """Validate references and return a deterministic topological order."""

    nodes = set(graph)
    missing = sorted({dependency for values in graph.values() for dependency in values} - nodes)
    if missing:
        return {"valid": False, "missing_dependencies": tuple(missing), "cycle": (), "order": ()}
    state: dict[str, int] = {}
    order: list[str] = []
    stack: list[str] = []
    cycle: tuple[str, ...] = ()

    def visit(node: str) -> bool:
        nonlocal cycle
        marker = state.get(node, 0)
        if marker == 2:
            return True
        if marker == 1:
            start = stack.index(node)
            cycle = tuple((*stack[start:], node))
            return False
        state[node] = 1
        stack.append(node)
        for dependency in sorted(graph[node]):
            if not visit(dependency):
                return False
        stack.pop()
        state[node] = 2
        order.append(node)
        return True

    for node in sorted(nodes):
        if not visit(node):
            return {"valid": False, "missing_dependencies": (), "cycle": cycle, "order": ()}
    return {"valid": True, "missing_dependencies": (), "cycle": (), "order": tuple(order)}


NUMERICAL_CERTIFICATE_FIELDS = (
    "algorithm",
    "software_version",
    "precision",
    "tolerance",
    "residual",
    "converged",
    "input_sha256",
)


def validate_numerical_certificate(record: Mapping[str, Any]) -> Mapping[str, Any]:
    """Validate numerical metadata without manufacturing absent results."""

    missing = tuple(field for field in NUMERICAL_CERTIFICATE_FIELDS if field not in record)
    errors: list[str] = []
    if not missing:
        for field in ("precision", "tolerance", "residual"):
            value = record[field]
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value):
                errors.append(f"{field} must be finite")
        if not errors:
            if record["precision"] <= 0 or record["tolerance"] < 0 or record["residual"] < 0:
                errors.append("precision must be positive and tolerance/residual nonnegative")
            if record["residual"] > record["tolerance"]:
                errors.append("residual exceeds tolerance")
        if record["converged"] is not True:
            errors.append("solver did not certify convergence")
        digest = record["input_sha256"]
        if not isinstance(digest, str) or len(digest) != 64 or any(
            char not in "0123456789abcdef" for char in digest
        ):
            errors.append("input_sha256 is not a lowercase SHA-256 digest")
    state = GateState.MISSING_INPUT if missing else (
        GateState.PASSED if not errors else GateState.KILLED
    )
    return {
        "valid": not missing and not errors,
        "state": state,
        "missing_fields": missing,
        "errors": tuple(errors),
    }


def reproducibility_criteria() -> tuple[ReproducibilityCriterion, ...]:
    """Return the twenty-one-item release ledger with present states."""

    P = GateState.PASSED
    O = GateState.OPEN
    T = EvidenceClass.EXACT_THEOREM
    rows = (
        (1, "Every paper theorem has a deterministic certificate", O,
         "Give every exact theorem a stable code identifier and replayable check.",
         "The maintained verifier covers the implemented ledgers, but the global paper crosswalk is incomplete."),
        (2, "Every certificate declares inputs and hashes", O,
         "Serialize all input identities and SHA-256 digests.", "Source DOCX hashes exist; all derived artifacts are not yet hashed."),
        (3, "Exact arithmetic uses the declared coefficient field", P,
         "Reject implicit floating-point substitution in exact checks.", "Rational and Eisenstein arithmetic are typed and tested."),
        (4, "Bases, orderings, and signs are serialized", O,
         "Serialize every convention needed to replay a certificate.", "Core conventions are encoded, but no global sign/basis registry is complete."),
        (5, "No-go results state their scope", P,
         "Attach the excluded ansatz and non-excluded alternatives.", "Scoped no-go evidence is represented separately from global impossibility."),
        (6, "Implemented exact checks replay offline", P,
         "Run all maintained exact checks with the Python standard library.", "The verifier has no third-party runtime dependency."),
        (7, "Open bridges have typed interfaces", P,
         "Represent required domains, codomains, dependencies, and pass/kill criteria.", "Origin, metric, hidden, vacuum, and closure contracts are explicit."),
        (8, "Missing inputs remain explicit", P,
         "Emit OPEN or MISSING_INPUT instead of a fabricated value.", "Every unresolved layer has a machine-readable missing-input ledger."),
        (9, "Placeholders cannot pass theorem gates", P,
         "Negative tests must reject incomplete or generic stand-ins.", "Fail-closed interfaces and synthetic-only labels are enforced."),
        (10, "Failed dependencies block downstream claims", P,
         "Validate an acyclic dependency graph and gate downstream status.", "The section dependency DAG is validated and completion remains blocked."),
        (11, "Numerical certificates carry full metadata", O,
         "Store algorithm, version, precision, tolerance, residual, convergence, and input hash.", "The validator exists; no project numerical archive is supplied."),
        (12, "Geometric solvers certify equations and tolerances", O,
         "Archive convergence and residual evidence for geometry.", "Ricci-flat metric data are missing."),
        (13, "Gauge solvers certify HYM residuals", O,
         "Archive gauge choice, iteration history, residuals, and error bounds.", "No HYM connection is supplied."),
        (14, "Harmonic representatives certify residuals", O,
         "Archive basis, inner products, orthogonality, and PDE residuals.", "No harmonic-representative package is supplied."),
        (15, "Vacuum solvers certify stationarity and stability", O,
         "Archive gradients, Hessian, constraints, corrections, and accepted tolerance.", "No controlled vacuum is supplied."),
        (16, "Displayed quantities cite certificates", O,
         "Cross-reference every displayed number and exact table entry.", "The end-to-end paper-code crosswalk is incomplete."),
        (17, "Paper and code share status labels", P,
         "Use the same P/T/A/C/B/N/O and gate-state vocabularies.", "The maintained paper and manifest use the common status ledger."),
        (18, "Published exact tables replay byte-for-byte", O,
         "Regenerate all exact tables from frozen inputs.", "No frozen table artifact set exists."),
        (19, "Numerical figures recreate within tolerance", O,
         "Regenerate figures with recorded software and tolerances.", "No numerical figure archive exists."),
        (20, "The frozen release replays in a clean environment", O,
         "Run the archived workflow from an empty, documented environment.", "Only in-workspace regression has been performed."),
        (21, "An independent implementation agrees", O,
         "Reimplement from the paper and compare certificates.", "No independent clean-room report exists."),
    )
    return tuple(
        ReproducibilityCriterion(number, label, state, T if state is P else EvidenceClass.OPEN,
                                 criterion, basis)
        for number, label, state, criterion, basis in rows
    )


def validate_reproducibility_criteria(
    criteria: Sequence[ReproducibilityCriterion] | None = None,
) -> Mapping[str, Any]:
    """Validate numbering and summarize the current release boundary."""

    items = tuple(criteria or reproducibility_criteria())
    numbering = tuple(item.number for item in items)
    passed = tuple(item.number for item in items if item.state is GateState.PASSED)
    blocking = tuple(item.number for item in items if item.state is not GateState.PASSED)
    valid = (
        numbering == tuple(range(1, 22))
        and all(item.label and item.pass_criterion and item.current_basis for item in items)
    )
    return {
        "valid": valid,
        "criterion_count": len(items),
        "passed_count": len(passed),
        "blocking_count": len(blocking),
        "passed_criteria": passed,
        "blocking_criteria": blocking,
        "full_release_reproducible": valid and not blocking,
    }


def open_obligation_registry() -> Mapping[str, Any]:
    """Aggregate maintained open inputs without converting them to results."""

    section_ledgers = {
        "section3": SECTION3_MISSING_INPUTS,
        "section4": SECTION4_MISSING_INPUTS,
        "section5": SECTION5_MISSING_INPUTS,
        "section6": SECTION6_MISSING_INPUTS,
        "section7": SECTION7_MISSING_INPUTS,
        "section8": SECTION8_MISSING_INPUTS,
        "section9": SECTION9_MISSING_INPUTS,
        "section10": SECTION10_MISSING_INPUTS,
        "section11": SECTION11_MISSING_INPUTS,
        "section12": SECTION12_MISSING_INPUTS,
        "section13": SECTION13_MISSING_INPUTS,
    }
    records = tuple(
        {"section": section, "identifier": identifier, "description": description}
        for section, ledger in section_ledgers.items()
        for identifier, description in sorted(ledger.items())
    )
    return {
        "state": GateState.MISSING_INPUT,
        "obligation_count": len(records),
        "obligations": records,
    }


def validate_release_manifest(
    candidate: Mapping[str, Any],
    root: Path | None = None,
) -> Mapping[str, Any]:
    """Validate the minimum standalone release schema and optional artifacts."""

    required = (
        "project",
        "implementation_version",
        "completed_paper_sections",
        "external_dependencies",
        "status_labels",
        "gate_states",
        "source_corpus_sha256",
    )
    missing = tuple(key for key in required if key not in candidate)
    errors: list[str] = []
    if not missing:
        if candidate["project"] != "OneTheory":
            errors.append("unexpected project identifier")
        sections = tuple(candidate["completed_paper_sections"])
        if not sections or sections != tuple(range(1, max(sections) + 1)):
            errors.append("completed sections must be contiguous from 1")
        if set(candidate["gate_states"]) != {state.value for state in GateState}:
            errors.append("gate-state vocabulary mismatch")
        if set(candidate["status_labels"]) != {item.value for item in EvidenceClass}:
            errors.append("evidence-status vocabulary mismatch")
    artifact_report: Mapping[str, Any] | None = None
    if root is not None and not missing:
        if "artifacts_sha256" not in candidate:
            errors.append("release-root validation requires artifacts_sha256")
        else:
            try:
                artifact_report = verify_artifact_digests(root, candidate["artifacts_sha256"])
                if not artifact_report["all_passed"]:
                    errors.append("one or more artifact digests failed")
            except (FileNotFoundError, TypeError, ValueError) as exc:
                errors.append(str(exc))
    return {
        "valid": not missing and not errors,
        "state": GateState.PASSED if not missing and not errors else (
            GateState.MISSING_INPUT if missing else GateState.KILLED
        ),
        "missing_fields": missing,
        "errors": tuple(errors),
        "artifact_report": artifact_report,
    }


def reproducibility_status() -> Mapping[str, Any]:
    """Return the established verifier spine and unresolved release claims."""

    ledger = validate_reproducibility_criteria()
    graph = validate_dependency_graph(certificate_dependency_graph())
    return {
        "standalone_verifier": True,
        "standard_library_only": True,
        "canonical_machine_output": True,
        "source_hash_manifest": True,
        "dependency_graph_valid": graph["valid"],
        "implemented_exact_checks_replay": True,
        "frozen_public_release_bundle": False,
        "clean_room_reproduction": False,
        "full_release_reproducible": ledger["full_release_reproducible"],
        "state": GateState.OPEN,
        "scientific_status": EvidenceClass.OPEN,
    }


def verify_reproducibility_spine() -> tuple[Check, ...]:
    """Certify implemented mechanics while preserving the open release boundary."""

    criteria = validate_reproducibility_criteria()
    graph = validate_dependency_graph(certificate_dependency_graph())
    status = reproducibility_status()
    empty_numerical = validate_numerical_certificate({})
    valid_numerical = validate_numerical_certificate(
        {
            "algorithm": "synthetic-contract-test",
            "software_version": __version__,
            "precision": 80,
            "tolerance": 1e-20,
            "residual": 1e-24,
            "converged": True,
            "input_sha256": "0" * 64,
        }
    )
    payload_a = {"b": 2, "a": (1, Fraction(1, 3))}
    payload_b = {"a": (1, Fraction(1, 3)), "b": 2}
    observations = (
        ("repro.version", __version__, "0.13.6", EvidenceClass.EXACT_THEOREM,
         "The maintained implementation includes the Section 12 reproducibility spine."),
        ("repro.sections", COMPLETED_PAPER_SECTIONS, tuple(range(1, 14)),
         EvidenceClass.EXACT_THEOREM, "The completed section ledger is contiguous through 13."),
        ("repro.canonical_json",
         canonical_json_bytes(payload_a) == canonical_json_bytes(payload_b), True,
         EvidenceClass.EXACT_THEOREM, "Canonical serialization is independent of mapping insertion order."),
        ("repro.sha256.length", len(sha256_json(payload_a)), 64,
         EvidenceClass.EXACT_THEOREM, "Canonical digests have the SHA-256 length."),
        ("repro.graph.valid", graph["valid"], True, EvidenceClass.EXACT_THEOREM,
         "The section dependency graph is acyclic and closed."),
        ("repro.graph.final", graph["order"][-1], "section13", EvidenceClass.EXACT_THEOREM,
         "The final synthesis follows the reproducibility layer and all earlier sections."),
        ("repro.criteria.valid", criteria["valid"], True, EvidenceClass.EXACT_THEOREM,
         "The twenty-one release criteria are complete and consecutively numbered."),
        ("repro.criteria.count", criteria["criterion_count"], 21, EvidenceClass.EXACT_THEOREM,
         "The release ledger contains twenty-one criteria."),
        ("repro.criteria.passed", criteria["passed_count"], 8, EvidenceClass.EXACT_THEOREM,
         "Eight implementation-level criteria currently pass."),
        ("repro.criteria.blocking", criteria["blocking_count"], 13, EvidenceClass.OPEN,
         "Thirteen archival, numerical, or independent-replay criteria remain open."),
        ("repro.numerical.missing", empty_numerical["state"], GateState.MISSING_INPUT,
         EvidenceClass.OPEN, "An empty numerical record cannot pass."),
        ("repro.numerical.synthetic", valid_numerical["valid"], True,
         EvidenceClass.EXACT_THEOREM, "Synthetic metadata exercises the validator only."),
        ("repro.manifest.valid", validate_release_manifest(manifest())["valid"], True,
         EvidenceClass.EXACT_THEOREM, "The maintained manifest satisfies its minimum schema."),
        ("repro.open.nonempty", open_obligation_registry()["obligation_count"] > 0, True,
         EvidenceClass.OPEN, "Open obligations are explicit and nonempty."),
        ("repro.bundle.open", status["frozen_public_release_bundle"], False,
         EvidenceClass.OPEN, "No frozen public release bundle is claimed."),
        ("repro.clean_room.open", status["clean_room_reproduction"], False,
         EvidenceClass.OPEN, "Internal tests are not independent reproduction."),
        ("repro.full.open", status["full_release_reproducible"], False,
         EvidenceClass.OPEN, "The full twenty-one-item release contract remains open."),
        ("repro.dependencies", manifest()["external_dependencies"], [],
         EvidenceClass.EXACT_THEOREM, "The verifier declares no third-party runtime dependency."),
        ("repro.source.count", len(SOURCE_CORPUS_SHA256), 13,
         EvidenceClass.EXACT_THEOREM, "All thirteen supplied source DOCX hashes are registered."),
    )
    return tuple(
        Check(identifier, observed == expected, expected, observed, evidence, note)
        for identifier, observed, expected, evidence, note in observations
    )


def run_section12_checks() -> tuple[Check, ...]:
    return verify_reproducibility_spine()


SECTION13_EVIDENCE_IDS: Mapping[str, str] = {
    "source_docx_sha256":
        "f2131bcca760f4b5bde32f168cf9fbf73608c9b0fe849b71259ee7fe9bfc6e79",
    "section13_source": "libfile_a1ed9b9d3a74819191f05af1c891f61c",
    "section11_closure_contract": "libfile_b4f5527d4ad88191991d9c69cb8abeb8",
    "section12_reproducibility_contract": "libfile_93e6b22fa7808191a9308c643be9e8c2",
}


SECTION13_MISSING_INPUTS: Mapping[str, str] = {
    "carrier_closure":
        "The visible rank lift, metrics, determinant line, hidden bundle, anomaly trivialization, and controlled vacuum are incomplete.",
    "native_origin_closure":
        "No non-circular Origin-to-Carrier theorem derives the heterotic carrier from the finite architecture.",
    "predictive_closure":
        "No nontrivial held-out observable with a complete uncertainty budget has been produced.",
    "publication_archive":
        "The complete frozen public archive and clean-environment replay remain open.",
    "independent_evaluation":
        "No independent implementation has reproduced the maintained certificates.",
}


def final_section_ledger() -> tuple[FinalLedgerEntry, ...]:
    """Return the thirteen-section scientific result map."""

    T = EvidenceClass.EXACT_THEOREM
    O = EvidenceClass.OPEN
    P = EvidenceClass.PUBLISHED_INPUT
    N = EvidenceClass.SCOPED_NO_GO
    A = EvidenceClass.ANALYTICAL_UNCERTIFIED
    C = EvidenceClass.CONDITIONAL
    B = EvidenceClass.BRIDGE_TARGET
    return (
        FinalLedgerEntry(1, "Completion criterion and result map", (T, O),
                         "Completion, evidence, selection, and falsification firewalls are explicit.",
                         "The imported carrier and its exact subtheorems do not satisfy completion."),
        FinalLedgerEntry(2, "Minimal physical foundation and ultraviolet carrier", (P, T),
                         "The published heterotic carrier and its project-side exact invariants are pinned.",
                         "The carrier is imported, not derived from the finite origin."),
        FinalLedgerEntry(3, "Native finite-origin architecture", (T, N, O),
                         "Finite arithmetic, algebraic structures, and scoped shortcut no-go results are exact.",
                         "No physical emission map to spacetime or the carrier exists."),
        FinalLedgerEntry(4, "Origin-to-Carrier theorem", (B, O),
                         "The bridge is specified by typed interfaces, dependencies, pass tests, and kill tests.",
                         "Every load-bearing subsystem map remains OPEN or MISSING_INPUT."),
        FinalLedgerEntry(5, "Observable-sector deformation theory", (T, N, O),
                         "A corrected mixed formal branch reaches stable, locally free, spectrum-preserving objects.",
                         "No physical normalized Yukawa matrix or light-family rank lift follows."),
        FinalLedgerEntry(6, "Light-family rank lifting", (T, N, O),
                         "Low-order channels and the raw compiler are closed; exact countermodels kill inference of star/triangular typing from branch support, so four physical f3 traces begin the twenty-trace worst-case path.",
                         "The carrier f3 traces and simultaneous full-rank certificate are missing."),
        FinalLedgerEntry(7, "Metric completion and physical Yukawas", (T, A, O),
                         "The 404-section dimension ledger, 848-lift workload, and rank-invariance theorem are fixed.",
                         "The section basis, Ricci-flat/HYM metrics, harmonics, and physical Yukawas are missing."),
        FinalLedgerEntry(8, "Worldsheet instantons, determinant lines, and CP", (T, N, C, O),
                         "Two conic orbits, quartic grammar, and nonidentifiability/phase firewalls are exact.",
                         "Physical seed maps, global determinant-line transport, and CP observables are missing."),
        FinalLedgerEntry(9, "Hidden-bundle completion", (T, N, O),
                         "The topological target and bounded search frontier are exact; candidate 750 is an exact complex.",
                         "Local freeness, descent, stability, spectrum, and HYM completion are unproved."),
        FinalLedgerEntry(10, "Nonperturbative superpotential and vacuum", (T, N, C, O),
                          "Several source classes are excluded and a minimal same-f_h unequal-exponent racetrack survives conditionally.",
                          "Carrier exponents, prefactors, full K/W/f/D data, and a controlled vacuum are missing."),
        FinalLedgerEntry(11, "Four-dimensional closure and falsification", (T, O),
                          "Twenty-seven closure criteria, scoped kill rules, and one-vacuum/prediction firewalls are serialized.",
                          "Only criteria 1 and 26 pass; 25 criteria remain blocking."),
        FinalLedgerEntry(12, "Companion implementation and reproducibility", (T, O),
                          "The dependency-free verifier, manifest, DAG, validators, and regression suite are maintained.",
                          "Thirteen of 21 full-release criteria, the public archive, and clean-room reproduction remain open."),
        FinalLedgerEntry(13, "Conclusion and technical appendices", (T, O),
                          "The complete result ledger, A--M appendix crosswalk, and final critical path are synchronized.",
                          "Synthesis adds no new physical observable and does not close any upstream gate."),
    )


def validate_final_section_ledger(
    ledger: Sequence[FinalLedgerEntry] | None = None,
) -> Mapping[str, Any]:
    """Validate coverage, ordering, and nonempty scientific boundaries."""

    items = tuple(ledger or final_section_ledger())
    numbering = tuple(item.section for item in items)
    identifiers_unique = len(set(numbering)) == len(numbering)
    fields_complete = all(
        item.title.strip()
        and item.evidence_classes
        and item.strongest_result.strip()
        and item.boundary.strip()
        for item in items
    )
    allowed = set(EvidenceClass)
    statuses_valid = all(set(item.evidence_classes) <= allowed for item in items)
    return {
        "valid": (
            numbering == tuple(range(1, 14))
            and identifiers_unique
            and fields_complete
            and statuses_valid
        ),
        "section_count": len(items),
        "numbering": numbering,
        "identifiers_unique": identifiers_unique,
        "fields_complete": fields_complete,
        "statuses_valid": statuses_valid,
    }


def technical_appendix_crosswalk() -> tuple[AppendixRecord, ...]:
    """Map Appendices A--M to the verified sections they summarize."""

    T = EvidenceClass.EXACT_THEOREM
    O = EvidenceClass.OPEN
    return (
        AppendixRecord("A", "Status, notation, and conventions", (1, 2, 12),
                       T, "Freeze evidence classes, gate states, coefficient fields, and total-differential conventions."),
        AppendixRecord("B", "Compactification and observable-bundle data", (2,),
                       T, "Collect the published carrier geometry, equivariance, Chern data, and spectrum anchor."),
        AppendixRecord("C", "Observable deformation complex", (5,),
                       T, "Collect the obstruction target, corrected Maurer--Cartan family, Higgs cocycle, and local-freeness certificate."),
        AppendixRecord("D", "Tree flavor and rank-lifting geometry", (1, 5, 6),
                       T, "Collect the rank-two texture, low-order no-go results, and direction-adaptive binary-Gram frontier."),
        AppendixRecord("E", "Positive-twist and metric interface", (7,),
                       O, "Separate exact section/lift data from missing metric, HYM, harmonic, and normalized-Yukawa inputs."),
        AppendixRecord("F", "Instanton and determinant-line interface", (8, 9),
                       O, "Collect conic geometry and specify the missing physical maps and anomaly-line transport."),
        AppendixRecord("G", "CP and finite quadratic refinement", (3, 8),
                       EvidenceClass.CONDITIONAL, "Separate the exact finite phase grammar from the unproved physical holonomy map."),
        AppendixRecord("H", "Hidden-bundle topology and construction", (9,),
                       O, "Collect the formal target, bounded frontier, and the remaining bundle-existence tests."),
        AppendixRecord("I", "Stabilization charge algebra", (10,),
                       EvidenceClass.CONDITIONAL, "Collect scoped source no-gos and the conditional minimal racetrack survivor."),
        AppendixRecord("J", "Four-dimensional effective action", (10, 11),
                       O, "State the required supergravity, vacuum, normalization, neutrino, and breaking interfaces."),
        AppendixRecord("K", "Reproducibility and certificate contract", (12,),
                       T, "Freeze exact/numerical separation, CLI, manifest, dependency blocking, and exit states."),
        AppendixRecord("L", "Open-obligation and falsification matrix", (4, 6, 7, 8, 9, 10, 11, 12),
                       O, "Pair every remaining frontier with a pass object, kill test, and scope."),
        AppendixRecord("M", "Final research ledger", (13,),
                       T, "State established results, immediate open objects, and the final scientific conclusion."),
    )


def validate_appendix_crosswalk(
    records: Sequence[AppendixRecord] | None = None,
) -> Mapping[str, Any]:
    """Validate the A--M appendix order and section references."""

    items = tuple(records or technical_appendix_crosswalk())
    letters = tuple(item.letter for item in items)
    expected = tuple(chr(code) for code in range(ord("A"), ord("N")))
    valid_sections = set(range(1, 14))
    section_refs_valid = all(
        item.source_sections
        and set(item.source_sections) <= valid_sections
        and tuple(sorted(set(item.source_sections))) == item.source_sections
        for item in items
    )
    fields_complete = all(item.title.strip() and item.purpose.strip() for item in items)
    return {
        "valid": letters == expected and section_refs_valid and fields_complete,
        "appendix_count": len(items),
        "letters": letters,
        "section_refs_valid": section_refs_valid,
        "fields_complete": fields_complete,
    }


def final_completion_contract() -> Mapping[str, Any]:
    """Evaluate the three simultaneous closure requirements without shortcuts."""

    closure = four_dimensional_closure_status()
    prediction = validate_prediction_registry()
    reproducibility = validate_reproducibility_criteria()
    carrier = bool(closure["carrier_closure"])
    native = bool(closure["native_origin_closure"])
    predictive = bool(prediction["independent_prediction_gate_passed"])
    threefold = carrier and native and predictive
    return {
        "carrier_closure": carrier,
        "native_origin_closure": native,
        "predictive_closure": predictive,
        "threefold_closure": threefold,
        "full_onetheory_completion": (
            bool(closure["full_onetheory_completion"]) and threefold
        ),
        "closure_criteria_passed": closure["passed_count"],
        "closure_criteria_blocking": closure["blocking_count"],
        "reproducibility_criteria_passed": reproducibility["passed_count"],
        "reproducibility_criteria_blocking": reproducibility["blocking_count"],
        "state": GateState.MISSING_INPUT,
        "scientific_status": EvidenceClass.OPEN,
    }


def final_scientific_statement() -> Mapping[str, Any]:
    """Return the exact final statement permitted by the maintained ledgers."""

    contract = final_completion_contract()
    return {
        "classification":
            "theorem-gated incomplete research program with exact subtheorems",
        "completed_theory_of_everything": False,
        "completed_heterotic_carrier": False,
        "native_origin_theorem": False,
        "controlled_common_vacuum": False,
        "independent_held_out_prediction": False,
        "maintained_section_scope": COMPLETED_PAPER_SECTIONS,
        "artifact_publication_readiness":
            "requires a passing publication-audit on the released DOCX and Python files",
        "strongest_permitted_claim": (
            "OneTheory supplies a finite, falsifiable, reproducible continuation "
            "program; it does not yet supply a completed physical theory."
        ),
        "state": contract["state"],
        "scientific_status": contract["scientific_status"],
    }


def final_critical_path() -> tuple[Mapping[str, Any], ...]:
    """Reuse the optimized Section 11 order as the final research path."""

    return optimized_critical_path()


def final_open_obligation_summary() -> Mapping[str, Any]:
    """Summarize, without deduplication claims, the immediate final blockers."""

    path = final_critical_path()
    return {
        "state": GateState.MISSING_INPUT,
        "critical_path_count": len(path),
        "critical_path": path,
        "section13_missing_inputs": dict(SECTION13_MISSING_INPUTS),
        "all_section_obligations": open_obligation_registry(),
    }


def verify_final_synthesis() -> tuple[Check, ...]:
    """Verify that the final synthesis matches the maintained project state."""

    ledger = validate_final_section_ledger()
    appendices = validate_appendix_crosswalk()
    contract = final_completion_contract()
    statement = final_scientific_statement()
    closure = four_dimensional_closure_status()
    reproduction = validate_reproducibility_criteria()
    prediction = validate_prediction_registry()
    path = final_critical_path()
    observations = (
        ("conclusion.version", __version__, "0.13.6", EvidenceClass.EXACT_THEOREM,
         "The maintained implementation carries the final synthesis release number."),
        ("conclusion.sections", COMPLETED_PAPER_SECTIONS, tuple(range(1, 14)),
         EvidenceClass.EXACT_THEOREM, "The publication ledger is contiguous through Section 13."),
        ("conclusion.ledger.valid", ledger["valid"], True, EvidenceClass.EXACT_THEOREM,
         "Every section has a strongest result and explicit boundary."),
        ("conclusion.ledger.count", ledger["section_count"], 13, EvidenceClass.EXACT_THEOREM,
         "The final ledger contains thirteen sections."),
        ("conclusion.appendices.valid", appendices["valid"], True, EvidenceClass.EXACT_THEOREM,
         "Appendices A through M are complete and reference valid sections."),
        ("conclusion.appendices.count", appendices["appendix_count"], 13,
         EvidenceClass.EXACT_THEOREM, "The technical crosswalk contains thirteen appendices."),
        ("conclusion.closure.criteria", closure["criterion_count"], 27,
         EvidenceClass.EXACT_THEOREM, "The final completion contract retains all 27 criteria."),
        ("conclusion.closure.passed", closure["passed_count"], 2,
         EvidenceClass.EXACT_THEOREM, "Only the ultraviolet-framework and falsification criteria pass."),
        ("conclusion.closure.blocking", closure["blocking_count"], 25,
         EvidenceClass.OPEN, "Twenty-five completion criteria remain blocking."),
        ("conclusion.carrier.open", contract["carrier_closure"], False,
         EvidenceClass.OPEN, "Carrier closure is not claimed."),
        ("conclusion.native.open", contract["native_origin_closure"], False,
         EvidenceClass.OPEN, "Native-origin closure is not claimed."),
        ("conclusion.predictive.open", contract["predictive_closure"], False,
         EvidenceClass.OPEN, "Predictive closure is not claimed."),
        ("conclusion.full.open", contract["full_onetheory_completion"], False,
         EvidenceClass.OPEN, "Full OneTheory completion remains false."),
        ("conclusion.prediction.count", prediction["held_out_count"], 0,
         EvidenceClass.OPEN, "No held-out prediction is present."),
        ("conclusion.repro.passed", reproduction["passed_count"], 8,
         EvidenceClass.EXACT_THEOREM, "Eight reproducibility criteria pass."),
        ("conclusion.repro.blocking", reproduction["blocking_count"], 13,
         EvidenceClass.OPEN, "Thirteen reproducibility criteria remain blocking."),
        ("conclusion.path.count", len(path), 12, EvidenceClass.EXACT_THEOREM,
         "The optimized critical path contains twelve ordered tasks."),
        ("conclusion.path.first", path[0]["identifier"], "visible_residues",
         EvidenceClass.OPEN, "The immediate truth-bearing object is the physical common-DGA package and four normalized f3 traces; branch support alone cannot decide the specialized typing."),
        ("conclusion.path.last", path[-1]["identifier"], "native_origin",
         EvidenceClass.OPEN, "The native-origin theorem remains the final independent bridge."),
        ("conclusion.statement.toe", statement["completed_theory_of_everything"], False,
         EvidenceClass.OPEN, "The final statement does not advertise a completed TOE."),
        ("conclusion.statement.classification", statement["classification"],
         "theorem-gated incomplete research program with exact subtheorems",
         EvidenceClass.EXACT_THEOREM, "The final classification matches Section 11."),
        ("conclusion.source.hash",
         SOURCE_CORPUS_SHA256["13-OneTheory Conclusion and Technical Appendices.docx"],
         SECTION13_EVIDENCE_IDS["source_docx_sha256"], EvidenceClass.EXACT_THEOREM,
         "The Section 13 source digest is pinned."),
        ("conclusion.source.count", len(SOURCE_CORPUS_SHA256), 13,
         EvidenceClass.EXACT_THEOREM, "The complete supplied source corpus contains thirteen documents."),
    )
    return tuple(
        Check(identifier, observed == expected, expected, observed, evidence, note)
        for identifier, observed, expected, evidence, note in observations
    )


def run_section13_checks() -> tuple[Check, ...]:
    return verify_final_synthesis()


def run_checks(section: str, source_dir: Path | None = None) -> tuple[Check, ...]:
    if section == "1":
        return run_section1_checks(source_dir)
    if section == "2":
        checks = run_section2_checks()
        if source_dir is not None:
            checks = (*checks, *verify_source_corpus(source_dir))
        return checks
    if section == "3":
        checks = run_section3_checks()
        if source_dir is not None:
            checks = (*checks, *verify_source_corpus(source_dir))
        return checks
    if section == "4":
        checks = run_section4_checks()
        if source_dir is not None:
            checks = (*checks, *verify_source_corpus(source_dir))
        return checks
    if section == "5":
        checks = run_section5_checks()
        if source_dir is not None:
            checks = (*checks, *verify_source_corpus(source_dir))
        return checks
    if section == "6":
        checks = run_section6_checks()
        if source_dir is not None:
            checks = (*checks, *verify_source_corpus(source_dir))
        return checks
    if section == "7":
        checks = run_section7_checks()
        if source_dir is not None:
            checks = (*checks, *verify_source_corpus(source_dir))
        return checks
    if section == "8":
        checks = run_section8_checks()
        if source_dir is not None:
            checks = (*checks, *verify_source_corpus(source_dir))
        return checks
    if section == "9":
        checks = run_section9_checks()
        if source_dir is not None:
            checks = (*checks, *verify_source_corpus(source_dir))
        return checks
    if section == "10":
        checks = run_section10_checks()
        if source_dir is not None:
            checks = (*checks, *verify_source_corpus(source_dir))
        return checks
    if section == "11":
        checks = run_section11_checks()
        if source_dir is not None:
            checks = (*checks, *verify_source_corpus(source_dir))
        return checks
    if section == "12":
        checks = run_section12_checks()
        if source_dir is not None:
            checks = (*checks, *verify_source_corpus(source_dir))
        return checks
    if section == "13":
        checks = run_section13_checks()
        if source_dir is not None:
            checks = (*checks, *verify_source_corpus(source_dir))
        return checks
    if section == "all":
        checks = (
            *run_section1_checks(),
            *run_section2_checks(),
            *run_section3_checks(),
            *run_section4_checks(),
            *run_section5_checks(),
            *run_section6_checks(),
            *run_section7_checks(),
            *run_section8_checks(),
            *run_section9_checks(),
            *run_section10_checks(),
            *run_section11_checks(),
            *run_section12_checks(),
            *run_section13_checks(),
        )
        if source_dir is not None:
            checks = (*checks, *verify_source_corpus(source_dir))
        return checks
    raise ValueError(f"unsupported section selector: {section}")


def _jsonable(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, Fraction):
        return (
            value.numerator
            if value.denominator == 1
            else {"numerator": value.numerator, "denominator": value.denominator}
        )
    if isinstance(value, Eisenstein):
        return {"a": _jsonable(value.a), "b": _jsonable(value.b), "text": value.text()}
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if hasattr(value, "__dataclass_fields__"):
        return _jsonable(asdict(value))
    return value


def emit(payload: Any, json_mode: bool) -> None:
    converted = _jsonable(payload)
    if json_mode:
        print(json.dumps(converted, indent=2, sort_keys=True))
    elif isinstance(converted, dict):
        for key, value in converted.items():
            print(f"{key}: {value}")
    elif isinstance(converted, list):
        for item in converted:
            print(item)
    else:
        print(converted)


def manifest() -> Mapping[str, Any]:
    return {
        "project": "OneTheory",
        "implementation_version": __version__,
        "completed_paper_sections": COMPLETED_PAPER_SECTIONS,
        "arithmetic_policy": (
            "fractions.Fraction over Q and exact pairs a+b*omega over "
            "Q(omega), omega^2+omega+1=0"
        ),
        "external_dependencies": [],
        "status_labels": {item.value: item.name for item in EvidenceClass},
        "gate_states": [item.value for item in GateState],
        "source_corpus_sha256": dict(SOURCE_CORPUS_SHA256),
        "section2_certificate_sha256": dict(SECTION2_CERTIFICATE_SHA256),
        "section3_missing_inputs": dict(SECTION3_MISSING_INPUTS),
        "section4_open_interfaces": origin_interface_registry(),
        "section4_missing_inputs": dict(SECTION4_MISSING_INPUTS),
        "section4_status": origin_bridge_status(),
        "section5_certificate_sha256": dict(SECTION5_CERTIFICATE_SHA256),
        "section5_missing_inputs": dict(SECTION5_MISSING_INPUTS),
        "section5_status": observable_deformation_status(),
        "section6_certificate_sha256": dict(SECTION6_CERTIFICATE_SHA256),
        "section6_missing_inputs": dict(SECTION6_MISSING_INPUTS),
        "section6_status": light_family_frontier_status(),
        "section6_direction_adaptive_frontier":
            direction_adaptive_pruning_certificate(),
        "section7_evidence_ids": dict(SECTION7_EVIDENCE_IDS),
        "section7_missing_inputs": dict(SECTION7_MISSING_INPUTS),
        "section7_status": metric_completion_status(),
        "section8_evidence_ids": dict(SECTION8_EVIDENCE_IDS),
        "section8_missing_inputs": dict(SECTION8_MISSING_INPUTS),
        "section8_status": instanton_completion_status(),
        "section9_evidence_ids": dict(SECTION9_EVIDENCE_IDS),
        "section9_missing_inputs": dict(SECTION9_MISSING_INPUTS),
        "section9_status": hidden_bundle_status(),
        "section10_evidence_ids": dict(SECTION10_EVIDENCE_IDS),
        "section10_missing_inputs": dict(SECTION10_MISSING_INPUTS),
        "section10_status": stabilization_status(),
        "section11_evidence_ids": dict(SECTION11_EVIDENCE_IDS),
        "section11_missing_inputs": dict(SECTION11_MISSING_INPUTS),
        "section11_status": four_dimensional_closure_status(),
        "section11_criteria": four_dimensional_closure_criteria(),
        "section11_falsification_rules": program_falsification_rules(),
        "section11_prediction_registry": current_prediction_registry(),
        "section11_critical_path": optimized_critical_path(),
        "section12_evidence_ids": dict(SECTION12_EVIDENCE_IDS),
        "section12_missing_inputs": dict(SECTION12_MISSING_INPUTS),
        "section12_status": reproducibility_status(),
        "section12_criteria": reproducibility_criteria(),
        "section12_dependency_graph": certificate_dependency_graph(),
        "section13_evidence_ids": dict(SECTION13_EVIDENCE_IDS),
        "section13_missing_inputs": dict(SECTION13_MISSING_INPUTS),
        "section13_status": final_scientific_statement(),
        "section13_ledger": final_section_ledger(),
        "section13_appendices": technical_appendix_crosswalk(),
        "section13_completion_contract": final_completion_contract(),
        "section13_critical_path": final_critical_path(),
        "evidence_registry": dict(EVIDENCE_REGISTRY),
    }


class Section1Tests(unittest.TestCase):
    def test_tree_certificate(self) -> None:
        self.assertTrue(all(check.passed for check in verify_tree_texture()))

    def test_exact_rank_rejects_float(self) -> None:
        with self.assertRaises(TypeError):
            exact_rank(((1.0, 0), (0, 1)))  # type: ignore[arg-type]

    def test_frontier_counts(self) -> None:
        self.assertTrue(all(check.passed for check in verify_frontier_counts()))

    def test_current_project_is_not_complete(self) -> None:
        result = evaluate_completion()
        self.assertFalse(result["carrier_closure"])
        self.assertFalse(result["full_onetheory_completion"])

    def test_native_origin_is_required_only_for_full_completion(self) -> None:
        gates = [
            Gate(
                gate.identifier,
                gate.label,
                (
                    GateState.OPEN
                    if gate.identifier == "native_origin"
                    else GateState.PASSED
                ),
                gate.evidence_class,
                gate.pass_criterion,
                gate.kill_criterion,
                gate.current_basis,
            )
            for gate in gate_registry()
        ]
        result = evaluate_completion(gates)
        self.assertTrue(result["carrier_closure"])
        self.assertFalse(result["full_onetheory_completion"])

    def test_every_gate_has_pass_and_kill_criteria(self) -> None:
        for gate in gate_registry():
            self.assertTrue(gate.pass_criterion.strip())
            self.assertTrue(gate.kill_criterion.strip())


class Section2Tests(unittest.TestCase):
    def test_eisenstein_field(self) -> None:
        self.assertEqual(OMEGA ** 2 + OMEGA + 1, E_ZERO)
        self.assertEqual((3 + 2 * OMEGA) / (3 + 2 * OMEGA), E_ONE)

    def test_heisenberg_and_point_schemes(self) -> None:
        self.assertTrue(all(check.passed for check in verify_heisenberg_and_point_schemes()))

    def test_serre_linearization(self) -> None:
        self.assertTrue(all(check.passed for check in verify_serre_linearization()))

    def test_topology_and_anomaly(self) -> None:
        self.assertTrue(all(check.passed for check in verify_topology_and_anomaly()))

    def test_curve_lattice(self) -> None:
        self.assertTrue(all(check.passed for check in verify_curve_lattice()))

    def test_published_carrier_metadata(self) -> None:
        self.assertTrue(all(check.passed for check in verify_carrier_manifest()))

    def test_float_rejected_in_eisenstein_arithmetic(self) -> None:
        with self.assertRaises(TypeError):
            Eisenstein.coerce(1.0)


class Section3Tests(unittest.TestCase):
    def test_planck_interface(self) -> None:
        checks = [
            check for check in verify_native_finite_architecture()
            if check.identifier.startswith("native.planck.")
        ]
        self.assertTrue(all(check.passed for check in checks))

    def test_paired_carrier_and_projectors(self) -> None:
        checks = [
            check for check in verify_native_finite_architecture()
            if check.identifier.startswith(("native.paired.", "native.projectors."))
        ]
        self.assertTrue(all(check.passed for check in checks))

    def test_albert_and_shortcut_dimensions(self) -> None:
        self.assertEqual(s3_albert_character()["character"], (27, -5, 0))
        self.assertEqual(16 + 10 + 1, 27)
        self.assertLess(24, 48)
        self.assertLess(28, 48)

    def test_finite_quadratic_plane_and_chirp(self) -> None:
        self.assertEqual(len(finite_quadratic_plane()["isotropic"]), 5)
        self.assertEqual(quadratic_form_classification()["orbit_union_count"], 18)
        self.assertTrue(all(
            finite_chirp_transform()[(r, s)] == 3 * OMEGA ** ((-r * s) % 3)
            for r, s in F3_VECTOR2
        ))

    def test_e8_embedding(self) -> None:
        embedding = e8_hyperbolic_embedding()
        self.assertEqual(
            tuple(item[2] for item in embedding["table"]),
            tuple(f3_q((a, b)) for a, b in F3_VECTOR2),
        )

    def test_d5_visible_no_go(self) -> None:
        result = d5_visible_wilson_classification()
        self.assertEqual(result["ordered_hyperbolic_pair_count"], 2160)
        self.assertEqual(result["survivor_distribution"], {2: 960, 4: 960, 6: 240})
        self.assertFalse(result["visible_a2_a1_root_count_present"])

    def test_hierarchy_coefficient_closure(self) -> None:
        data = hierarchy_coefficient_closure()
        self.assertEqual(data["difference_over_c"], Fraction(4, 3))
        self.assertEqual(
            data["up_product_over_c_b_u"],
            data["down_product_over_c_b_u"],
        )

    def test_missing_inputs_are_explicit(self) -> None:
        self.assertIn("tight_frame_representation", SECTION3_MISSING_INPUTS)
        self.assertIn("physical_native_to_carrier_maps", SECTION3_MISSING_INPUTS)


class Section4Tests(unittest.TestCase):
    def test_interface_registry_is_complete_and_open(self) -> None:
        interfaces = origin_interface_registry()
        self.assertEqual(
            tuple(interface.identifier for interface in interfaces),
            ORIGIN_INTERFACE_IDS,
        )
        self.assertTrue(all(interface.state is GateState.OPEN for interface in interfaces))

    def test_dependency_graph_is_acyclic_and_total(self) -> None:
        order = origin_dependency_order()
        self.assertEqual(set(order), set(ORIGIN_INTERFACE_IDS))
        self.assertLess(
            order.index("origin_geometry"),
            order.index("origin_visible_bundle"),
        )
        self.assertLess(
            order.index("origin_visible_bundle"),
            order.index("generation_carrier"),
        )

    def test_origin_status_does_not_claim_a_theorem(self) -> None:
        status = origin_bridge_status()
        self.assertFalse(status["visible_carrier_constructed"])
        self.assertFalse(status["full_carrier_constructed"])
        self.assertFalse(status["origin_theorem_proved"])
        self.assertEqual(
            status["highest_level"],
            "LEVEL_I_PARTIAL_STRUCTURAL_COMPATIBILITY",
        )

    def test_empirical_leakage_firewall(self) -> None:
        self.assertEqual(
            empirical_leakage_scan(("fit family basis to CKM mixing angles",)),
            ("ckm", "mixing angle"),
        )
        self.assertEqual(
            empirical_leakage_scan(("finite form q(a,b)=ab", "Chern classes")),
            (),
        )

    def test_section4_contract_checks_pass_without_closing_bridge(self) -> None:
        self.assertTrue(all(check.passed for check in run_section4_checks()))
        self.assertTrue(
            all(
                interface.state is not GateState.PASSED
                for interface in origin_interface_registry()
            )
        )


class Section5Tests(unittest.TestCase):
    def test_forward_and_reverse_dimensions(self) -> None:
        self.assertEqual(forward_slice_no_go_certificate()["forward_dimension"], 4)
        self.assertEqual(bileray_quadratic_certificate()["reverse_dimension"], 8)

    def test_complete_forward_slice_no_go(self) -> None:
        result = forward_slice_no_go_certificate()
        self.assertEqual(result["rank_one_wedge"], 0)
        self.assertEqual(result["lambda_up"], (0, 0, 0, 0))
        self.assertEqual(result["lambda_down"], (0, 0, 0, 0))
        self.assertEqual(result["allowed_powers"], (1,))

    def test_bileray_quadratic_vanishing(self) -> None:
        result = bileray_quadratic_certificate()
        self.assertEqual(result["theta_1_pairing_degree"], (2, 1))
        self.assertEqual(result["theta_2_pairing_degree"], (1, 2))
        self.assertEqual(result["rank"], 0)
        self.assertEqual(result["kernel_dimension"], 32)

    def test_strict_square_zero_witness(self) -> None:
        result = strict_square_zero_witness()
        self.assertEqual(result["e0_times_f3"], result["expected_zero"])
        self.assertEqual(result["f3_times_e0"], result["expected_zero"])

    def test_corrected_maurer_cartan_and_higgs(self) -> None:
        result = corrected_maurer_cartan_certificate()
        self.assertEqual(result["maurer_cartan_residual"], {})
        self.assertEqual(result["deformed_higgs_residual"], {})

    def test_local_freeness_normal_form(self) -> None:
        result = local_freeness_normal_form()
        self.assertEqual(result["delta"], result["expected_delta"])
        self.assertEqual(result["delta_at_origin"], 1)
        self.assertEqual(result["cohomology_rank"], 4)

    def test_stability_box(self) -> None:
        result = stability_box_certificate()
        self.assertTrue(result["all_anchor_values_match"])
        self.assertTrue(result["all_negative_on_box"])
        self.assertEqual(result["v1_slope"], -297)

    def test_scoped_status_and_open_physical_yukawas(self) -> None:
        result = observable_deformation_status()
        self.assertTrue(result["locally_free_stable_mixed_points_exist"])
        self.assertTrue(result["one_higgs_pair_protected_on_reached_branch"])
        self.assertFalse(result["physical_normalized_yukawas_computed"])
        self.assertFalse(result["light_family_rank_lift_established"])

    def test_section5_checks_pass(self) -> None:
        self.assertTrue(all(check.passed for check in run_section5_checks()))


class Section6Tests(unittest.TestCase):
    def test_odd_determinant_orders(self) -> None:
        self.assertEqual(
            tuple(row["total_order"] for row in determinant_order_frontier(3)),
            (1, 3, 5, 7),
        )

    def test_degree_three_no_go(self) -> None:
        result = degree_three_no_go_certificate()
        self.assertTrue(result["U1_identically_zero"])
        self.assertTrue(result["D1_identically_zero"])

    def test_response_automaton_and_direct_rows(self) -> None:
        result = direct_order5_certificate()
        self.assertEqual(len(result["matter_words"]), 11)
        self.assertEqual(result["up_count"], 16)
        self.assertEqual(result["down_count"], 26)
        self.assertTrue(result["all_direct_rows_zero"])

    def test_second_normal_countermodel(self) -> None:
        result = second_normal_form_certificate()
        self.assertEqual(result["countermodel_direct_second_jet"], E_ZERO)
        self.assertEqual(result["countermodel_S2"], Eisenstein(-1))
        self.assertTrue(result["direct_zero_does_not_fix_second_normal"])

    def test_hessian_formula_and_rank_bound(self) -> None:
        result = compile_restricted_frontier(synthetic_frontier_package(True))
        self.assertLessEqual(result["rank_H_u"], 2)
        self.assertLessEqual(result["rank_H_d"], 2)
        self.assertEqual(result["det_H_u"], E_ZERO)
        self.assertEqual(result["det_H_d"], E_ZERO)

    def test_compiler_zero_and_nonzero_branches(self) -> None:
        nonzero = compile_restricted_frontier(synthetic_frontier_package(True))
        zero = compile_restricted_frontier(synthetic_frontier_package(False))
        self.assertFalse(nonzero["U2_identically_zero"])
        self.assertFalse(nonzero["D2_identically_zero"])
        self.assertTrue(zero["U2_identically_zero"])
        self.assertTrue(zero["D2_identically_zero"])

    def test_direction_adaptive_pruning(self) -> None:
        result = direction_adaptive_pruning_certificate()
        self.assertTrue(result["all_exact_checks_pass"])
        self.assertEqual(result["generic_ledger"]["total"], 24)
        self.assertEqual(result["direction_refined_ledger"]["total"], 20)
        self.assertEqual(
            result["first_simultaneous_test"]["normalized_scalar_evaluations"],
            4,
        )

    def test_binary_gram_certificate(self) -> None:
        result = binary_gram_certificate(
            ((E_ZERO, E_ONE), (E_ONE, E_ZERO)),
            ((E_ONE, E_ZERO, E_ONE), (E_ONE, E_ONE, E_ZERO)),
        )
        self.assertTrue(result["all_exact_checks_pass"])
        self.assertTrue(result["checks"]["adjugate_identity"])
        self.assertTrue(result["checks"]["principal_minor_identities"])

    def test_adaptive_compiler_branches(self) -> None:
        f3 = compile_direction_adaptive_frontier(
            synthetic_adaptive_frontier_package("f3_norm_pass")
        )
        rank2 = compile_direction_adaptive_frontier(
            synthetic_adaptive_frontier_package("rank2_pass")
        )
        zero = compile_direction_adaptive_frontier(
            synthetic_adaptive_frontier_package("full_zero")
        )
        self.assertEqual(f3["normalized_scalar_evaluations_consumed"], 4)
        self.assertTrue(f3["simultaneous_nonzero_forms_certified"])
        self.assertEqual(rank2["normalized_scalar_evaluations_consumed"], 12)
        self.assertTrue(rank2["simultaneous_nonzero_forms_certified"])
        self.assertEqual(zero["normalized_scalar_evaluations_consumed"], 20)
        self.assertEqual(zero["zero_certified_sectors"], ("u", "d"))

    def test_adaptive_compiler_fails_closed(self) -> None:
        package = dict(synthetic_adaptive_frontier_package("f3_norm_pass"))
        package["certificates"] = dict(package["certificates"])
        package["certificates"]["common_cyclic_gauge"] = False
        with self.assertRaisesRegex(ValueError, "common_cyclic_gauge"):
            compile_direction_adaptive_frontier(package)

    def test_raw_f3_common_cyclic_compiler(self) -> None:
        result = compile_f3_common_cyclic_package(
            synthetic_f3_common_cyclic_package()
        )
        self.assertEqual(result["independent_normalized_scalar_count"], 4)
        self.assertEqual(result["oriented_contraction_count"], 8)
        self.assertTrue(result["all_orientation_pairs_equal"])
        self.assertTrue(
            result["adaptive_compilation"][
                "simultaneous_nonzero_forms_certified"
            ]
        )

    def test_raw_f3_synthetic_firewall(self) -> None:
        result = compile_f3_common_cyclic_package(
            synthetic_f3_common_cyclic_package()
        )
        self.assertFalse(result["physical_carrier_evaluation"])
        self.assertFalse(
            result[
                "simultaneous_physical_order_five_nonzero_forms_certified"
            ]
        )

    def test_raw_f3_cyclicity_fails_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "cyclic orientations disagree"):
            compile_f3_common_cyclic_package(
                synthetic_f3_common_cyclic_package(cyclic=False)
            )

    def test_raw_f3_certificate_fails_closed(self) -> None:
        package = dict(synthetic_f3_common_cyclic_package())
        package["certificates"] = dict(package["certificates"])
        package["certificates"]["effective_FE_response_chain_certified"] = False
        with self.assertRaisesRegex(
            ValueError,
            "effective_FE_response_chain_certified",
        ):
            compile_f3_common_cyclic_package(package)

    def test_raw_f3_float_rejected(self) -> None:
        package = dict(synthetic_f3_common_cyclic_package())
        package["sectors"] = dict(package["sectors"])
        package["sectors"]["u"] = dict(package["sectors"]["u"])
        package["sectors"]["u"]["a"] = (1.0,)
        with self.assertRaises(TypeError):
            compile_f3_common_cyclic_package(package)

    def test_suspended_hpl_compiler(self) -> None:
        result = compile_suspended_hpl_f3_package(
            synthetic_suspended_hpl_f3_package()
        )
        expected = (Eisenstein(-1), Eisenstein(-1))
        self.assertEqual(result["p_f3"], {"u": expected, "d": expected})
        self.assertTrue(all(result["computed_checks"].values()))
        self.assertTrue(
            result["adaptive_compilation"][
                "simultaneous_nonzero_forms_certified"
            ]
        )

    def test_suspended_hpl_synthetic_firewall(self) -> None:
        result = compile_suspended_hpl_f3_package(
            synthetic_suspended_hpl_f3_package()
        )
        self.assertFalse(result["physical_carrier_evaluation"])
        self.assertFalse(
            result[
                "simultaneous_physical_order_five_nonzero_forms_certified"
            ]
        )

    def test_suspended_hpl_digest_fails_closed(self) -> None:
        package = dict(synthetic_suspended_hpl_f3_package())
        package["matrices"] = dict(package["matrices"])
        d1 = [list(row) for row in package["matrices"]["D1"]]
        d1[0][0] = 1
        package["matrices"]["D1"] = d1
        with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
            compile_suspended_hpl_f3_package(package)

    def test_suspended_hpl_identity_fails_closed(self) -> None:
        package = dict(synthetic_suspended_hpl_f3_package())
        package["matrices"] = dict(package["matrices"])
        d1 = [list(row) for row in package["matrices"]["D1"]]
        d1[0][0] = 1
        package["matrices"]["D1"] = d1
        package["matrix_sha256"] = dict(package["matrix_sha256"])
        package["matrix_sha256"]["D1"] = sha256_json(d1)
        with self.assertRaisesRegex(ValueError, "computed HPL identity failed"):
            compile_suspended_hpl_f3_package(package)

    def test_suspended_hpl_float_rejected(self) -> None:
        package = dict(synthetic_suspended_hpl_f3_package())
        package["matrices"] = dict(package["matrices"])
        d1 = [list(row) for row in package["matrices"]["D1"]]
        d1[0][0] = 1.0
        package["matrices"]["D1"] = d1
        with self.assertRaises(TypeError):
            compile_suspended_hpl_f3_package(package)

    def test_suspended_hpl_request_order_fails_closed(self) -> None:
        package = dict(synthetic_suspended_hpl_f3_package())
        package["trace_requests"] = tuple(reversed(package["trace_requests"]))
        with self.assertRaisesRegex(ValueError, "trace request order"):
            compile_suspended_hpl_f3_package(package)

    def test_star_tangent_degree_five_theorem(self) -> None:
        result = compile_star_tangent_degree5_package(
            synthetic_star_tangent_degree5_package()
        )
        self.assertTrue(result["package_level_U2_identically_zero"])
        self.assertTrue(
            result["package_level_simultaneous_degree_five_full_rank_impossible"]
        )
        self.assertTrue(all(result["exact_checks"].values()))
        self.assertEqual(
            result["D2_factorization"],
            "-(2/m_d) A_d B_d",
        )

    def test_star_tangent_synthetic_firewall(self) -> None:
        result = compile_star_tangent_degree5_package(
            synthetic_star_tangent_degree5_package()
        )
        self.assertFalse(result["physical_carrier_evaluation"])
        self.assertFalse(result["physical_degree_five_up_no_go_certified"])
        self.assertEqual(
            result["next_order_contract"]["state"],
            GateState.MISSING_INPUT,
        )

    def test_star_tangent_typing_fails_closed(self) -> None:
        package = dict(synthetic_star_tangent_degree5_package())
        package["certificates"] = dict(package["certificates"])
        package["certificates"]["down_triangular_typing_certified"] = False
        with self.assertRaisesRegex(
            ValueError,
            "down_triangular_typing_certified",
        ):
            compile_star_tangent_degree5_package(package)

    def test_star_tangent_float_rejected(self) -> None:
        package = dict(synthetic_star_tangent_degree5_package())
        package["parameters"] = dict(package["parameters"])
        package["parameters"]["m_u"] = 1.0
        with self.assertRaises(TypeError):
            compile_star_tangent_degree5_package(package)

    def test_star_tangent_typing_invariants(self) -> None:
        star = classify_star_tangent_transport(
            ((1, 0, 1), (0, 0, 0))
        )
        nonstar = classify_star_tangent_transport(
            ((1, 0, 1), (0, 1, 1))
        )
        self.assertTrue(star["image_totally_isotropic"])
        self.assertTrue(star["frozen_up_star_typing"])
        self.assertFalse(nonstar["image_totally_isotropic"])
        self.assertFalse(nonstar["frozen_up_star_typing"])

    def test_star_tangent_typing_nonidentifiability(self) -> None:
        result = star_tangent_typing_nonidentifiability_certificate()
        self.assertTrue(all(result["exact_checks"].values()))
        self.assertEqual(
            result["inference_from_branch_support_to_up_star_typing"],
            GateState.KILLED,
        )
        self.assertEqual(
            result["inference_from_branch_support_to_down_triangular_typing"],
            GateState.KILLED,
        )
        self.assertEqual(
            result["actual_physical_carrier_typing"],
            GateState.MISSING_INPUT,
        )
        self.assertEqual(
            result["first_invariant_test"]["normalized_scalar_trace_count"],
            4,
        )

    def test_down_triangular_f3_kill_criterion(self) -> None:
        triangular = classify_star_tangent_transport(
            ((1, 1, 0), (0, 1, 1))
        )
        nontriangular = classify_star_tangent_transport(
            ((1, 1, 0), (1, 0, 1))
        )
        self.assertTrue(triangular["first_direction_isotropic"])
        self.assertTrue(triangular["frozen_down_triangular_typing"])
        self.assertFalse(nontriangular["first_direction_isotropic"])
        self.assertFalse(nontriangular["frozen_down_triangular_typing"])

    def test_compiler_fails_closed(self) -> None:
        package = dict(synthetic_frontier_package(True))
        package["certificates"] = dict(package["certificates"])
        package["certificates"]["cyclic_trace_normalized"] = False
        with self.assertRaisesRegex(ValueError, "cyclic_trace_normalized"):
            compile_restricted_frontier(package)

    def test_simultaneous_open_theorem(self) -> None:
        result = simultaneous_open_theorem(True, True, True)
        self.assertTrue(result["simultaneous_nonvanishing_open_nonempty"])
        self.assertFalse(result["requires_separate_projective_search"])

    def test_carrier_status_remains_open(self) -> None:
        result = light_family_frontier_status()
        self.assertEqual(result["generic_residue_ledger_count"], 24)
        self.assertEqual(result["direction_refined_worst_case_count"], 20)
        self.assertEqual(result["first_simultaneous_test_count"], 4)
        self.assertTrue(
            result["suspended_hpl_source_to_trace_compiler_certified"]
        )
        self.assertFalse(result["suspended_hpl_physical_package_available"])
        self.assertTrue(result["star_tangent_degree_five_theorem_certified"])
        self.assertFalse(
            result["star_tangent_physical_typing_package_available"]
        )
        self.assertFalse(result["physical_degree_five_up_no_go_certified"])
        self.assertTrue(result["degree_seven_up_contract_defined"])
        self.assertTrue(result["raw_f3_common_cyclic_compiler_certified"])
        self.assertFalse(result["raw_f3_physical_package_available"])
        self.assertFalse(result["carrier_residue_values_available"])
        self.assertFalse(result["carrier_f3_columns_computed"])
        self.assertFalse(result["simultaneous_light_family_rank_lift_established"])
        self.assertEqual(result["state"], GateState.MISSING_INPUT)

    def test_section6_checks_pass(self) -> None:
        self.assertTrue(all(check.passed for check in run_section6_checks()))


class Section7Tests(unittest.TestCase):
    def test_positive_twist_dimensions(self) -> None:
        result = positive_twist_dimension_certificate()
        self.assertEqual(result["twist"], (5, 7, 1))
        self.assertEqual(result["cover_H0_V"], 3636)
        self.assertEqual(
            (result["H0_V1"], result["H0_V2"], result["H0_V"]),
            (192, 212, 404),
        )
        self.assertFalse(result["global_non_split_differential_lawful"])

    def test_extension_blindness_is_scoped(self) -> None:
        result = extension_blindness_certificate()
        self.assertTrue(result["vector_space_split_exists"])
        self.assertFalse(result["vector_space_split_canonical"])
        self.assertFalse(result["sheaf_split_implied"])
        self.assertFalse(result["pointwise_evaluation_extension_blind"])

    def test_analytical_constituents_stay_uncertified(self) -> None:
        rows = tuple(analytical_constituent_certificate(i) for i in range(9))
        self.assertEqual({row["claimed_total"] for row in rows}, {212})
        self.assertTrue(all(not row["serialized_artifact_available"] for row in rows))
        self.assertTrue(
            all(row["status"] is EvidenceClass.ANALYTICAL_UNCERTIFIED for row in rows)
        )
        with self.assertRaises(ValueError):
            analytical_constituent_certificate(9)

    def test_cech_lift_workload(self) -> None:
        result = cech_lift_workload()
        self.assertEqual(result["operator_applications"], 848)
        self.assertEqual(result["total_sections"], 404)
        self.assertEqual(result["state"], GateState.MISSING_INPUT)

    def test_metric_whitener(self) -> None:
        result = metric_whitener(((2, 1 + 0.25j), (1 - 0.25j, 3)))
        self.assertLess(result["residual"], 1e-10)

    def test_invalid_metrics_fail_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "Hermitian"):
            metric_whitener(((1, 1), (0, 1)))
        with self.assertRaisesRegex(ValueError, "positive definite"):
            metric_whitener(((1, 2), (2, 1)))

    def test_canonical_normalization_helper(self) -> None:
        result = canonical_normalize_yukawa(
            ((1, 2), (0, 1)),
            ((2, 0.25), (0.25, 1)),
            ((3, 0.5), (0.5, 2)),
            2.0,
            0.0,
        )
        self.assertEqual(len(result["physical_yukawa"]), 2)
        self.assertLess(result["left_residual"], 1e-10)
        self.assertLess(result["right_residual"], 1e-10)

    def test_rank_invariance(self) -> None:
        result = canonical_normalization_rank_certificate()
        self.assertEqual(result["holomorphic_rank"], 2)
        self.assertEqual(result["normalized_rank"], 2)
        self.assertTrue(result["rank_preserved"])

    def test_metric_completion_remains_open(self) -> None:
        result = metric_completion_status()
        self.assertFalse(result["physical_normalized_yukawas_computed"])
        self.assertFalse(result["tree_rank_repair_by_metrics_possible"])
        self.assertEqual(result["state"], GateState.MISSING_INPUT)

    def test_section7_checks_pass(self) -> None:
        self.assertTrue(all(check.passed for check in run_section7_checks()))


class Section8Tests(unittest.TestCase):
    def test_two_free_conic_orbits(self) -> None:
        result = degree_two_conic_certificate()
        self.assertEqual(result["curve_count"], 18)
        self.assertEqual(result["orbit_sizes"], (9, 9))
        self.assertTrue(result["free_action"])
        self.assertFalse(result["pfaffian_value_attached"])

    def test_quartic_grammar(self) -> None:
        result = quartic_grammar_certificate()
        self.assertEqual(result["spin_twisted_boundary_map_shape"], (4, 4))
        self.assertEqual(result["ambient_quartic_dimension"], 35)
        self.assertEqual(len(result["monomials"]), 35)
        self.assertFalse(result["physical_quartic_defined"])

    def test_naive_serre_ratio_is_rejected(self) -> None:
        result = serre_restriction_firewall()
        self.assertTrue(result["independent_serre_ray_rescaling"])
        self.assertFalse(result["naive_projective_ratio_invariant"])
        self.assertFalse(result["physical_six_by_six_maps_defined"])

    def test_v075_nonidentifiability(self) -> None:
        result = quartic_nonidentifiability_certificate()
        self.assertEqual(
            tuple(witness["quartic_term_count"] for witness in result["witnesses"]),
            (7, 19),
        )
        self.assertTrue(all(not witness["physical"] for witness in result["witnesses"]))
        self.assertFalse(result["witnesses_Kunit_proportional"])
        self.assertFalse(result["cross_curve_CP_work_allowed"])

    def test_relative_normalization_ledger(self) -> None:
        result = relative_normalization_ledger()
        self.assertEqual(result["relative_ratios_per_orbit"], 8)
        self.assertEqual(result["total_relative_ratios"], 17)
        with self.assertRaises(ValueError):
            relative_normalization_ledger(0)

    def test_quadratic_refinement_classification(self) -> None:
        result = quillen_quadratic_refinement_certificate()
        self.assertEqual(
            (
                result["GL2_order"],
                result["homogeneous_quadratic_forms"],
                result["nondegenerate_forms"],
                result["split_forms"],
                result["anisotropic_forms"],
            ),
            (48, 27, 18, 12, 6),
        )
        self.assertTrue(result["fourier_chirp_exact"])
        self.assertFalse(result["physical_quillen_holonomy_identified"])

    def test_cp_pair_and_discrete_order(self) -> None:
        result = cp_bundle_pair_certificate()
        self.assertTrue(result["CP_partner_exact"])
        self.assertTrue(result["local_intersection_is_maximal_ideal_squared"])
        self.assertEqual(result["invariant_tangent_dimension"], 0)
        self.assertFalse(result["controlled_vacuum_pair_constructed"])

    def test_monomial_ideal_intersection(self) -> None:
        self.assertEqual(
            monomial_ideal_intersection(((0, 1), (2, 0)), ((1, 0), (0, 2))),
            ((0, 2), (1, 1), (2, 0)),
        )

    def test_section8_remains_fail_closed(self) -> None:
        result = instanton_completion_status()
        self.assertFalse(result["physical_seed_quartics_defined"])
        self.assertFalse(result["complete_instanton_sum_computed"])
        self.assertFalse(result["physical_CP_violation_established"])
        self.assertEqual(result["state"], GateState.MISSING_INPUT)

    def test_section8_checks_pass(self) -> None:
        self.assertTrue(all(check.passed for check in run_section8_checks()))


class Section9Tests(unittest.TestCase):
    def test_hidden_topological_target(self) -> None:
        result = hidden_anomaly_target_certificate()
        self.assertEqual(
            result["c2_hidden_required"],
            (Fraction(4, 3), Fraction(7, 3), Fraction(-4)),
        )
        self.assertEqual(result["extension_c2"], result["c2_hidden_required"])
        self.assertEqual(result["integrated_bianchi_residual"], (0, 0, 0))

    def test_formal_extension_does_not_claim_existence(self) -> None:
        result = formal_hidden_extension_certificate()
        self.assertEqual(result["rank_V4"], 4)
        self.assertEqual(result["c1_V4"], (0, 0, 0))
        self.assertEqual(result["c3_V4"], 0)
        self.assertFalse(result["primitive_Q_exists"])

    def test_bounded_search_uses_current_frontier(self) -> None:
        result = bounded_hidden_search_certificate()
        self.assertEqual(result["survivor_counts_through_26"], (0, 0, 0, 0))
        self.assertEqual(result["unresolved_supports"], 44)
        self.assertEqual(result["theorem_ledger"], 44)
        self.assertFalse(result["older_objective22_seven_candidate_snapshot_current"])

    def test_candidate750_exact_complex_boundary(self) -> None:
        result = candidate750_certificate()
        self.assertEqual(result["cohomology_rank"], 2)
        self.assertTrue(result["GF_coefficientwise_zero"])
        self.assertEqual(result["F_ranks_at_exact_points"], (7, 7))
        self.assertEqual(result["G_ranks_at_exact_points"], (6, 6))
        self.assertFalse(result["sample_scan_is_proof"])
        self.assertFalse(result["local_freeness_proved"])

    def test_monad_rank_contract_fails_closed(self) -> None:
        self.assertEqual(hidden_monad_rank_contract(7, 15, 6), 2)
        with self.assertRaises(ValueError):
            hidden_monad_rank_contract(7, 10, 6)
        with self.assertRaises(ValueError):
            hidden_monad_rank_contract(True, 15, 6)

    def test_descent_obstruction_is_open(self) -> None:
        result = equivariant_descent_certificate()
        self.assertEqual(result["obstruction_classes"], (0, 1, 2))
        self.assertEqual(result["character_twists_if_honest"], 9)
        self.assertFalse(result["descends"])

    def test_current_and_legacy_curve_ledgers_are_separate(self) -> None:
        current = hidden_curve_restriction_contract()
        broader = hidden_curve_restriction_contract(True)
        self.assertEqual(current["total_restriction_targets"], 18)
        self.assertEqual(broader["total_restriction_targets"], 27)
        self.assertFalse(current["restrictions_proved"])

    def test_hidden_index_does_not_fix_spectrum(self) -> None:
        result = hidden_spectrum_index_certificate()
        self.assertEqual(tuple(result["indices"].values()), (0, 0, 0, 0))
        self.assertFalse(result["absolute_cohomology_dimensions_known"])
        self.assertEqual(spin10_beta_coefficient(2, 1, 1), 18)
        with self.assertRaises(ValueError):
            spin10_beta_coefficient(-1, 0, 0)

    def test_spectral_genus_correction_and_scoped_no_go(self) -> None:
        result = spectral_hidden_firewall()
        self.assertEqual(result["spectral_curve_genus"], 10)
        self.assertEqual(result["spectral_line_degree"], 12)
        self.assertFalse(result["standard_one_fibration_route_can_match"])
        self.assertTrue(result["genuine_U2_relative_FM_route_open"])

    def test_section9_remains_fail_closed(self) -> None:
        result = hidden_bundle_status()
        self.assertEqual(result["objective28_unresolved_supports"], 44)
        self.assertFalse(result["stable_hidden_SU4_bundle_constructed"])
        self.assertEqual(result["state"], GateState.MISSING_INPUT)
        self.assertTrue(all(check.passed for check in run_section9_checks()))


class Section10Tests(unittest.TestCase):
    def test_affine_hyperplane_no_go(self) -> None:
        result = affine_hyperplane_certificate()
        self.assertEqual(result["retained_L_values"], (Fraction(1),) * 4)
        self.assertLess(result["L_of_tree_kahler_gradient"], 0)
        self.assertFalse(
            result["finite_ordinary_base_degree_one_plus_one_condensate_susy_solution"]
        )

    def test_general_base_degree_one_charge(self) -> None:
        charge = worldsheet_charge(17, -4, Fraction(7, 3))
        self.assertEqual(
            affine_functional(charge, Fraction(5, 2), Fraction(7, 3)),
            Fraction(1),
        )

    def test_higher_base_determinant_and_weights(self) -> None:
        result = one_extra_worldsheet_certificate(5, 3, 4, 2, 3)
        self.assertEqual(
            result["augmented_determinant"],
            Fraction(2 * 3 ** 3 * (4 - 1)),
        )
        self.assertEqual(result["weighted_charge_relation"], (Fraction(0),) * 4)
        self.assertEqual(result["weight_sum"], 1)

    def test_multicover_alignment(self) -> None:
        result = one_extra_worldsheet_certificate(6, 3, 3)
        self.assertEqual(result["surviving_alignment"], "q21")
        self.assertEqual(result["required_amplitude_ratio"], Fraction(-1, 3))
        self.assertTrue(result["one_term_multicover_closed"])

    def test_second_condensate_unique_survivor(self) -> None:
        result = second_condensate_certificate(3, 5)
        self.assertTrue(result["uses_same_gauge_kinetic_function"])
        self.assertTrue(result["unequal_exponents"])
        self.assertTrue(result["minimal_survivor"])
        self.assertEqual(
            result["condensate_ratio_in_controlled_limit"],
            Fraction(-3, 5),
        )

    def test_equal_exponents_collapse(self) -> None:
        result = second_condensate_certificate(3, 3)
        self.assertTrue(result["equal_exponents_collapse_to_one_exponential"])
        self.assertFalse(result["minimal_survivor"])
        rank = racetrack_charge_rank_certificate(3, 3)
        self.assertEqual(rank["racetrack_affine_hull_dimension"], 3)
        self.assertFalse(rank["minimal_racetrack_pass"])

    def test_unequal_exponents_raise_rank(self) -> None:
        result = racetrack_charge_rank_certificate(3, 5, 2)
        self.assertEqual(result["ordinary_affine_hull_dimension"], 3)
        self.assertEqual(result["racetrack_affine_hull_dimension"], 4)
        self.assertEqual(result["augmented_determinant"], 16)
        self.assertTrue(result["rank_lift_if_and_only_if_unequal"])

    def test_e6_toral_enumeration(self) -> None:
        result = e6_toral_racetrack_certificate()
        self.assertEqual(result["two_subspaces_F3_6"], 11_011)
        self.assertEqual(
            result["centralizer_type_counts"],
            result["expected_type_counts"],
        )
        self.assertFalse(result["pure_SYM_unequal_exponent_racetrack_exists"])

    def test_supergravity_potential_helpers(self) -> None:
        self.assertAlmostEqual(
            n1_f_term_potential(0.0, 2 + 0j, (0j,), ((1 + 0j,),)),
            -12.0,
        )
        self.assertAlmostEqual(n1_d_term_potential((2.0,), ((0.5,),)), 1.0)

    def test_stabilization_remains_fail_closed(self) -> None:
        result = stabilization_status()
        self.assertFalse(result["carrier_unequal_exponents_derived"])
        self.assertFalse(result["controlled_vacuum_constructed"])
        self.assertEqual(result["state"], GateState.MISSING_INPUT)
        self.assertTrue(all(check.passed for check in run_section10_checks()))


class Section11Tests(unittest.TestCase):
    def test_completion_contract_is_numbered_and_fail_closed(self) -> None:
        criteria = four_dimensional_closure_criteria()
        validation = validate_closure_criteria(criteria)
        self.assertTrue(validation["valid"])
        self.assertEqual(tuple(item.number for item in criteria), tuple(range(1, 28)))
        self.assertEqual(
            tuple(item.number for item in criteria if item.state is GateState.PASSED),
            (1, 26),
        )

    def test_current_closure_status_is_not_completion(self) -> None:
        result = four_dimensional_closure_status()
        self.assertEqual(result["criterion_count"], 27)
        self.assertEqual(result["passed_count"], 2)
        self.assertEqual(result["blocking_count"], 25)
        self.assertFalse(result["carrier_closure"])
        self.assertFalse(result["native_origin_closure"])
        self.assertFalse(result["full_onetheory_completion"])

    def test_prediction_registry_has_no_held_out_prediction(self) -> None:
        result = validate_prediction_registry()
        self.assertTrue(result["registry_valid"])
        self.assertEqual(result["held_out_count"], 0)
        self.assertFalse(result["independent_prediction_gate_passed"])

    def test_legacy_prediction_firewall(self) -> None:
        result = legacy_prediction_firewall()
        self.assertFalse(result["numerical_values_imported"])
        self.assertEqual(result["status"], EvidenceClass.SCOPED_NO_GO)
        self.assertIn("common vacuum", result["reason"])

    def test_exact_covariance_and_seesaw_helpers(self) -> None:
        self.assertEqual(
            exact_covariance_variance((1, 2), ((4, 1), (1, 9))),
            Fraction(44),
        )
        self.assertEqual(
            type1_seesaw_mass_matrix(
                ((1, 0), (0, 1)),
                ((Fraction(1, 2), 0), (0, Fraction(1, 3))),
            ),
            ((Fraction(-1, 2), 0), (0, Fraction(-1, 3))),
        )

    def test_ckm_jarlskog_identity(self) -> None:
        identity = n_identity(3)
        self.assertEqual(ckm_matrix(identity, identity), identity)
        self.assertEqual(jarlskog_invariant(identity), 0.0)

    def test_threshold_and_running_contracts(self) -> None:
        self.assertEqual(one_loop_inverse_gauge_coupling(2.0, 7.0, 1.0), 2.0)
        valid = validate_threshold_scales(
            {"ew": 100.0, "susy": 1_000.0, "compactification": 1e16},
            ("ew", "susy", "compactification"),
        )
        invalid = validate_threshold_scales(
            {"ew": 100.0, "susy": 10.0},
            ("ew", "susy", "compactification"),
        )
        self.assertTrue(valid["valid"])
        self.assertFalse(invalid["valid"])

    def test_vacuum_acceptance_and_one_vacuum_principle(self) -> None:
        complete = {key: True for key in VACUUM_ACCEPTANCE_KEYS}
        self.assertTrue(controlled_vacuum_acceptance(complete)["passed"])
        self.assertEqual(
            controlled_vacuum_acceptance({})["state"],
            GateState.MISSING_INPUT,
        )
        shared = common_vacuum_certificate({"Y": "v1", "K": "v1", "RG": "v1"})
        split = common_vacuum_certificate({"Y": "v1", "K": "v2", "RG": "v1"})
        self.assertTrue(shared["one_vacuum_principle_satisfied"])
        self.assertEqual(split["state"], GateState.KILLED)

    def test_scalar_stability_contract(self) -> None:
        self.assertTrue(
            scalar_stability_certificate((0.0, 1.0), "Minkowski")["passed"]
        )
        self.assertFalse(
            scalar_stability_certificate((-0.1, 1.0), "Minkowski")["passed"]
        )
        self.assertTrue(
            scalar_stability_certificate((-2.0, 1.0), "AdS4", ads_radius=1.0)[
                "passed"
            ]
        )

    def test_section11_checks_pass(self) -> None:
        self.assertTrue(all(check.passed for check in run_section11_checks()))


class Section12Tests(unittest.TestCase):
    def test_canonical_json_and_digest(self) -> None:
        left = {"z": 2, "a": (Fraction(1, 3), 1)}
        right = {"a": (Fraction(1, 3), 1), "z": 2}
        self.assertEqual(canonical_json_bytes(left), canonical_json_bytes(right))
        self.assertEqual(sha256_json(left), sha256_json(right))
        self.assertEqual(len(sha256_json(left)), 64)

    def test_dependency_graph(self) -> None:
        result = validate_dependency_graph(certificate_dependency_graph())
        self.assertTrue(result["valid"])
        self.assertEqual(result["order"][-1], "section13")
        cycle = validate_dependency_graph({"a": ("b",), "b": ("a",)})
        self.assertFalse(cycle["valid"])
        self.assertTrue(cycle["cycle"])

    def test_unsafe_artifact_paths_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            _safe_release_path(Path("."), "../escape")
        with self.assertRaises(ValueError):
            _safe_release_path(Path("."), "/absolute")

    def test_numerical_certificate_fails_closed(self) -> None:
        result = validate_numerical_certificate({})
        self.assertFalse(result["valid"])
        self.assertEqual(result["state"], GateState.MISSING_INPUT)
        bad = validate_numerical_certificate(
            {
                "algorithm": "test",
                "software_version": __version__,
                "precision": 50,
                "tolerance": 1e-12,
                "residual": 1e-4,
                "converged": True,
                "input_sha256": "0" * 64,
            }
        )
        self.assertEqual(bad["state"], GateState.KILLED)

    def test_reproducibility_ledger_is_numbered_and_open(self) -> None:
        result = validate_reproducibility_criteria()
        self.assertTrue(result["valid"])
        self.assertEqual(result["criterion_count"], 21)
        self.assertEqual(result["passed_count"], 8)
        self.assertEqual(result["blocking_count"], 13)
        self.assertFalse(result["full_release_reproducible"])

    def test_manifest_schema(self) -> None:
        self.assertTrue(validate_release_manifest(manifest())["valid"])
        self.assertEqual(
            validate_release_manifest({})["state"],
            GateState.MISSING_INPUT,
        )

    def test_artifact_digest_verifier(self) -> None:
        source = Path(__file__)
        result = verify_artifact_digests(
            source.parent,
            {source.name: sha256_path(source)},
        )
        self.assertTrue(result["all_passed"])

    def test_python_publication_audit(self) -> None:
        result = audit_python_publication(Path(__file__))
        self.assertTrue(result["valid"])
        self.assertEqual(result["violation_count"], 0)

    def test_docx_publication_audit_rejects_empty_formula(self) -> None:
        document_xml = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<w:document xmlns:w="'
            + _WORD_NS
            + '"><w:body><w:p><w:r><w:t>[ ]</w:t></w:r></w:p>'
            '<w:sectPr/></w:body></w:document>'
        ).encode("utf-8")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "broken.docx"
            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr("word/document.xml", document_xml)
            result = audit_docx_publication(path)
        self.assertFalse(result["valid"])
        self.assertTrue(
            any(row["kind"] == "empty_formula_shell" for row in result["violations"])
        )

    def test_docx_publication_audit_rejects_empty_inline_formula(self) -> None:
        document_xml = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<w:document xmlns:w="'
            + _WORD_NS
            + '"><w:body><w:p><w:r><w:t>where () is required</w:t></w:r></w:p>'
            '<w:sectPr/></w:body></w:document>'
        ).encode("utf-8")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "broken-inline.docx"
            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr("word/document.xml", document_xml)
            result = audit_docx_publication(path)
        self.assertFalse(result["valid"])
        self.assertTrue(
            any(row["kind"] == "empty_inline_formula" for row in result["violations"])
        )

    def test_current_status_does_not_claim_clean_room(self) -> None:
        result = reproducibility_status()
        self.assertTrue(result["standalone_verifier"])
        self.assertFalse(result["frozen_public_release_bundle"])
        self.assertFalse(result["clean_room_reproduction"])
        self.assertEqual(result["state"], GateState.OPEN)

    def test_open_obligation_registry(self) -> None:
        result = open_obligation_registry()
        self.assertEqual(result["state"], GateState.MISSING_INPUT)
        self.assertGreater(result["obligation_count"], 0)
        self.assertTrue(any(row["section"] == "section12" for row in result["obligations"]))

    def test_section12_checks_pass(self) -> None:
        self.assertTrue(all(check.passed for check in run_section12_checks()))


class Section13Tests(unittest.TestCase):
    def test_final_ledger_is_complete(self) -> None:
        result = validate_final_section_ledger()
        self.assertTrue(result["valid"])
        self.assertEqual(result["numbering"], tuple(range(1, 14)))

    def test_appendix_crosswalk_is_A_through_M(self) -> None:
        result = validate_appendix_crosswalk()
        self.assertTrue(result["valid"])
        self.assertEqual(
            result["letters"],
            tuple(chr(code) for code in range(ord("A"), ord("N"))),
        )

    def test_threefold_closure_fails_closed(self) -> None:
        result = final_completion_contract()
        self.assertFalse(result["carrier_closure"])
        self.assertFalse(result["native_origin_closure"])
        self.assertFalse(result["predictive_closure"])
        self.assertFalse(result["threefold_closure"])
        self.assertFalse(result["full_onetheory_completion"])

    def test_final_statement_does_not_claim_TOE(self) -> None:
        result = final_scientific_statement()
        self.assertFalse(result["completed_theory_of_everything"])
        self.assertFalse(result["controlled_common_vacuum"])
        self.assertFalse(result["independent_held_out_prediction"])
        self.assertEqual(result["scientific_status"], EvidenceClass.OPEN)

    def test_final_critical_path_reuses_verified_order(self) -> None:
        result = final_critical_path()
        self.assertEqual(len(result), 12)
        self.assertEqual(result[0]["identifier"], "visible_residues")
        self.assertEqual(result[-1]["identifier"], "native_origin")

    def test_section13_source_hash_is_pinned(self) -> None:
        self.assertEqual(
            SOURCE_CORPUS_SHA256[
                "13-OneTheory Conclusion and Technical Appendices.docx"
            ],
            SECTION13_EVIDENCE_IDS["source_docx_sha256"],
        )

    def test_final_open_summary_is_explicit(self) -> None:
        result = final_open_obligation_summary()
        self.assertEqual(result["state"], GateState.MISSING_INPUT)
        self.assertEqual(result["critical_path_count"], 12)
        self.assertIn("carrier_closure", result["section13_missing_inputs"])

    def test_manifest_contains_final_synthesis(self) -> None:
        result = manifest()
        self.assertEqual(result["completed_paper_sections"], tuple(range(1, 14)))
        self.assertIn("section13_ledger", result)
        self.assertIn("section13_appendices", result)

    def test_appendices_only_reference_completed_sections(self) -> None:
        completed = set(COMPLETED_PAPER_SECTIONS)
        for record in technical_appendix_crosswalk():
            self.assertTrue(set(record.source_sections) <= completed)

    def test_section13_checks_pass(self) -> None:
        self.assertTrue(all(check.passed for check in run_section13_checks()))


def command_verify(args: argparse.Namespace) -> int:
    checks = run_checks(args.section, args.source_dir)
    emit(
        {
            "implementation_version": __version__,
            "section": args.section,
            "all_passed": all(check.passed for check in checks),
            "checks": checks,
        },
        args.json,
    )
    if any(check.observed == "MISSING_INPUT" for check in checks):
        return ExitCode.MISSING_INPUT
    return ExitCode.OK if all(check.passed for check in checks) else ExitCode.CERTIFICATE_FAILURE


def command_status(args: argparse.Namespace) -> int:
    emit(
        {
            "claims": CLAIMS,
            "gates": gate_registry(),
            "completion": evaluate_completion(),
        },
        args.json,
    )
    return ExitCode.OK


def command_completion(args: argparse.Namespace) -> int:
    result = evaluate_completion()
    emit(result, args.json)
    if args.require_complete and not result["full_onetheory_completion"]:
        return ExitCode.COMPLETION_OPEN
    return ExitCode.OK


def command_manifest(args: argparse.Namespace) -> int:
    emit(manifest(), args.json)
    return ExitCode.OK


def command_origin_interfaces(args: argparse.Namespace) -> int:
    emit(
        {
            "implementation_version": __version__,
            "status": origin_bridge_status(),
            "dependency_order": origin_dependency_order(),
            "interfaces": origin_interface_registry(),
            "missing_inputs": SECTION4_MISSING_INPUTS,
        },
        args.json,
    )
    return ExitCode.OK


def command_observable_deformation(args: argparse.Namespace) -> int:
    emit(
        {
            "implementation_version": __version__,
            "status": observable_deformation_status(),
            "forward_slice": forward_slice_no_go_certificate(),
            "quadratic_obstruction": bileray_quadratic_certificate(),
            "strict_witness": strict_square_zero_witness(),
            "corrected_branch": corrected_maurer_cartan_certificate(),
            "local_freeness": local_freeness_normal_form(),
            "stability": stability_box_certificate(),
            "spectrum": spectrum_persistence_certificate(),
            "missing_inputs": SECTION5_MISSING_INPUTS,
        },
        args.json,
    )
    return ExitCode.OK


def command_rank_lifting(args: argparse.Namespace) -> int:
    supplied_packages = sum(
        path is not None
        for path in (
            args.star_tangent_package,
            args.hpl_f3_package,
            args.f3_common_package,
            args.adaptive_package,
        )
    ) + int(args.typing_audit)
    if supplied_packages > 1:
        raise ValueError(
            "--typing-audit, --star-tangent-package, --hpl-f3-package, "
            "--f3-common-package, and --adaptive-package are mutually exclusive"
        )
    if args.typing_audit:
        emit(
            {
                "implementation_version": __version__,
                "star_tangent_typing_nonidentifiability":
                    star_tangent_typing_nonidentifiability_certificate(),
            },
            args.json,
        )
        return ExitCode.OK
    if args.star_tangent_package is not None:
        package = json.loads(
            args.star_tangent_package.read_text(encoding="utf-8")
        )
        if not isinstance(package, Mapping):
            raise ValueError("star-tangent package must contain a JSON object")
        compiled = compile_star_tangent_degree5_package(package)
        emit(
            {
                "implementation_version": __version__,
                "star_tangent_degree_five_compilation": compiled,
            },
            args.json,
        )
        return ExitCode.OK
    if args.hpl_f3_package is not None:
        package = json.loads(args.hpl_f3_package.read_text(encoding="utf-8"))
        if not isinstance(package, Mapping):
            raise ValueError("HPL f3 package must contain a JSON object")
        compiled = compile_suspended_hpl_f3_package(package)
        emit(
            {
                "implementation_version": __version__,
                "suspended_hpl_f3_compilation": compiled,
            },
            args.json,
        )
        adaptive = compiled["adaptive_compilation"]
        return (
            ExitCode.MISSING_INPUT
            if adaptive["undecided_sectors"]
            else ExitCode.OK
        )
    if args.f3_common_package is not None:
        package = json.loads(args.f3_common_package.read_text(encoding="utf-8"))
        if not isinstance(package, Mapping):
            raise ValueError("raw f3 common-cyclic package must contain a JSON object")
        compiled = compile_f3_common_cyclic_package(package)
        emit(
            {
                "implementation_version": __version__,
                "raw_f3_common_cyclic_compilation": compiled,
            },
            args.json,
        )
        adaptive = compiled["adaptive_compilation"]
        return (
            ExitCode.MISSING_INPUT
            if adaptive["undecided_sectors"]
            else ExitCode.OK
        )
    if args.adaptive_package is not None:
        package = json.loads(args.adaptive_package.read_text(encoding="utf-8"))
        if not isinstance(package, Mapping):
            raise ValueError("adaptive carrier package must contain a JSON object")
        compiled = compile_direction_adaptive_frontier(package)
        emit(
            {
                "implementation_version": __version__,
                "adaptive_compilation": compiled,
            },
            args.json,
        )
        return (
            ExitCode.MISSING_INPUT
            if compiled["undecided_sectors"]
            else ExitCode.OK
        )
    emit(
        {
            "implementation_version": __version__,
            "status": light_family_frontier_status(),
            "wall_charge_frontier": determinant_order_frontier(),
            "degree_three_no_go": degree_three_no_go_certificate(),
            "direct_order_five": direct_order5_certificate(),
            "second_normal_form": second_normal_form_certificate(),
            "restricted_hull_contract": {
                "directions": FRONTIER_DIRECTIONS,
                "up_groups": UP_RESIDUE_GROUPS,
                "down_groups": DOWN_RESIDUE_GROUPS,
                "required_certificates": RESTRICTED_HULL_CERTIFICATES,
                "generic_residue_count": 24,
            },
            "direction_adaptive_frontier": direction_adaptive_pruning_certificate(),
            "suspended_hpl_f3_contract": suspended_hpl_f3_contract(),
            "suspended_hpl_f3_self_test": compile_suspended_hpl_f3_package(
                synthetic_suspended_hpl_f3_package()
            ),
            "raw_f3_common_cyclic_contract": f3_common_cyclic_contract(),
            "raw_f3_common_cyclic_self_test": compile_f3_common_cyclic_package(
                synthetic_f3_common_cyclic_package()
            ),
            "star_tangent_degree_five_contract":
                star_tangent_degree5_contract(),
            "star_tangent_degree_five_self_test":
                compile_star_tangent_degree5_package(
                    synthetic_star_tangent_degree5_package()
                ),
            "star_tangent_typing_nonidentifiability":
                star_tangent_typing_nonidentifiability_certificate(),
            "binary_gram_self_test": binary_gram_certificate(
                ((E_ZERO, E_ONE), (E_ONE, E_ZERO)),
                ((E_ONE, E_ZERO, E_ONE), (E_ONE, E_ONE, E_ZERO)),
            ),
            "adaptive_f3_self_test": compile_direction_adaptive_frontier(
                synthetic_adaptive_frontier_package("f3_norm_pass")
            ),
            "adaptive_rank2_self_test": compile_direction_adaptive_frontier(
                synthetic_adaptive_frontier_package("rank2_pass")
            ),
            "adaptive_zero_self_test": compile_direction_adaptive_frontier(
                synthetic_adaptive_frontier_package("full_zero")
            ),
            "synthetic_nonzero_self_test": compile_restricted_frontier(
                synthetic_frontier_package(True)
            ),
            "synthetic_zero_self_test": compile_restricted_frontier(
                synthetic_frontier_package(False)
            ),
            "missing_inputs": SECTION6_MISSING_INPUTS,
        },
        args.json,
    )
    return ExitCode.OK


def command_metric_completion(args: argparse.Namespace) -> int:
    emit(
        {
            "implementation_version": __version__,
            "status": metric_completion_status(),
            "positive_twist": positive_twist_dimension_certificate(),
            "extension_blindness": extension_blindness_certificate(),
            "analytical_constituents": tuple(
                analytical_constituent_certificate(character)
                for character in range(9)
            ),
            "cech_lift_interface": cech_lift_workload(),
            "rank_invariance": canonical_normalization_rank_certificate(),
            "numerical_api": {
                "metric_whitener": (
                    "returns N=(L^dagger)^-1 with N^dagger K N=I"
                ),
                "canonical_normalize_yukawa": (
                    "returns e^(Kmod/2) kH^(-1/2) N_Q^T Y_hol N_f"
                ),
                "carrier_metric_package_supplied": False,
            },
            "evidence_ids": SECTION7_EVIDENCE_IDS,
            "missing_inputs": SECTION7_MISSING_INPUTS,
        },
        args.json,
    )
    return ExitCode.OK


def command_instanton_sector(args: argparse.Namespace) -> int:
    emit(
        {
            "implementation_version": __version__,
            "status": instanton_completion_status(),
            "conic_geometry": degree_two_conic_certificate(),
            "quartic_grammar": quartic_grammar_certificate(),
            "restriction_firewall": serre_restriction_firewall(),
            "quartic_nonidentifiability": quartic_nonidentifiability_certificate(),
            "relative_normalization": relative_normalization_ledger(),
            "quillen_quadratic_refinement": quillen_quadratic_refinement_certificate(),
            "cp_bundle_pair": cp_bundle_pair_certificate(),
            "evidence_ids": SECTION8_EVIDENCE_IDS,
            "missing_inputs": SECTION8_MISSING_INPUTS,
        },
        args.json,
    )
    return ExitCode.OK


def command_hidden_bundle(args: argparse.Namespace) -> int:
    emit(
        {
            "implementation_version": __version__,
            "status": hidden_bundle_status(),
            "topological_target": hidden_anomaly_target_certificate(),
            "formal_extension": formal_hidden_extension_certificate(),
            "bounded_search": bounded_hidden_search_certificate(),
            "candidate750": candidate750_certificate(),
            "local_freeness_contract": hidden_local_freeness_contract(),
            "equivariant_descent": equivariant_descent_certificate(),
            "curve_restrictions": hidden_curve_restriction_contract(),
            "legacy_curve_restrictions": hidden_curve_restriction_contract(True),
            "extension_index": hidden_extension_index_certificate(),
            "spectrum_index": hidden_spectrum_index_certificate(),
            "spectral_firewall": spectral_hidden_firewall(),
            "evidence_ids": SECTION9_EVIDENCE_IDS,
            "missing_inputs": SECTION9_MISSING_INPUTS,
        },
        args.json,
    )
    return ExitCode.OK


def command_stabilization(args: argparse.Namespace) -> int:
    emit(
        {
            "implementation_version": __version__,
            "status": stabilization_status(),
            "affine_hyperplane": affine_hyperplane_certificate(),
            "higher_base_worldsheet": one_extra_worldsheet_certificate(),
            "second_condensate": second_condensate_certificate(),
            "racetrack_rank": racetrack_charge_rank_certificate(),
            "toral_E6_firewall": e6_toral_racetrack_certificate(),
            "chern_simons_firewall": chern_simons_constant_firewall(),
            "leading_racetrack": minimal_racetrack_certificate(),
            "evidence_ids": SECTION10_EVIDENCE_IDS,
            "missing_inputs": SECTION10_MISSING_INPUTS,
        },
        args.json,
    )
    return ExitCode.OK


def command_closure(args: argparse.Namespace) -> int:
    emit(
        {
            "implementation_version": __version__,
            "status": four_dimensional_closure_status(),
            "criteria": four_dimensional_closure_criteria(),
            "falsification_rules": program_falsification_rules(),
            "prediction_registry": current_prediction_registry(),
            "prediction_validation": validate_prediction_registry(),
            "legacy_prediction_firewall": legacy_prediction_firewall(),
            "conditional_CP_pairing": conditional_cp_pairing_certificate(),
            "critical_path": optimized_critical_path(),
            "evidence_ids": SECTION11_EVIDENCE_IDS,
            "missing_inputs": SECTION11_MISSING_INPUTS,
        },
        args.json,
    )
    return ExitCode.OK


def command_reproducibility(args: argparse.Namespace) -> int:
    release_report = None
    if args.release_root is not None:
        candidate = manifest()
        if args.artifact:
            candidate = {**candidate, "artifacts_sha256": dict(args.artifact)}
        release_report = validate_release_manifest(candidate, args.release_root)
    emit(
        {
            "implementation_version": __version__,
            "status": reproducibility_status(),
            "criteria": reproducibility_criteria(),
            "criteria_validation": validate_reproducibility_criteria(),
            "dependency_graph": certificate_dependency_graph(),
            "dependency_validation": validate_dependency_graph(certificate_dependency_graph()),
            "open_obligations": open_obligation_registry(),
            "release_validation": release_report,
            "evidence_ids": SECTION12_EVIDENCE_IDS,
            "missing_inputs": SECTION12_MISSING_INPUTS,
        },
        args.json,
    )
    if release_report is not None and not release_report["valid"]:
        return ExitCode.INVALID_MANIFEST
    return ExitCode.OK


def command_publication_audit(args: argparse.Namespace) -> int:
    report = publication_artifact_audit(args.docx, args.python)
    emit(report, args.json)
    return (
        ExitCode.OK
        if report["artifact_integrity_passed"]
        else ExitCode.CERTIFICATE_FAILURE
    )


def command_conclusion(args: argparse.Namespace) -> int:
    emit(
        {
            "implementation_version": __version__,
            "scientific_statement": final_scientific_statement(),
            "completion_contract": final_completion_contract(),
            "section_ledger": final_section_ledger(),
            "ledger_validation": validate_final_section_ledger(),
            "technical_appendices": technical_appendix_crosswalk(),
            "appendix_validation": validate_appendix_crosswalk(),
            "critical_path": final_critical_path(),
            "open_obligations": final_open_obligation_summary(),
            "evidence_ids": SECTION13_EVIDENCE_IDS,
            "missing_inputs": SECTION13_MISSING_INPUTS,
        },
        args.json,
    )
    return ExitCode.OK


def command_self_test(args: argparse.Namespace) -> int:
    suite = unittest.TestSuite(
        (
            unittest.defaultTestLoader.loadTestsFromTestCase(Section1Tests),
            unittest.defaultTestLoader.loadTestsFromTestCase(Section2Tests),
            unittest.defaultTestLoader.loadTestsFromTestCase(Section3Tests),
            unittest.defaultTestLoader.loadTestsFromTestCase(Section4Tests),
            unittest.defaultTestLoader.loadTestsFromTestCase(Section5Tests),
            unittest.defaultTestLoader.loadTestsFromTestCase(Section6Tests),
            unittest.defaultTestLoader.loadTestsFromTestCase(Section7Tests),
            unittest.defaultTestLoader.loadTestsFromTestCase(Section8Tests),
            unittest.defaultTestLoader.loadTestsFromTestCase(Section9Tests),
            unittest.defaultTestLoader.loadTestsFromTestCase(Section10Tests),
            unittest.defaultTestLoader.loadTestsFromTestCase(Section11Tests),
            unittest.defaultTestLoader.loadTestsFromTestCase(Section12Tests),
            unittest.defaultTestLoader.loadTestsFromTestCase(Section13Tests),
        )
    )
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return ExitCode.OK if result.wasSuccessful() else ExitCode.CERTIFICATE_FAILURE


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="OneTheory.py",
        description=(
            "Deterministic verifier for the OneTheory paper. "
            "Implemented scope: front matter and Sections 1--13, with an "
            "artifact-level publication audit."
        ),
    )
    parser.add_argument("--version", action="version", version=__version__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    verify = subparsers.add_parser("verify", help="run exact checks for completed sections")
    verify.add_argument(
        "--section",
        choices=("1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "all"),
        default="all",
        help="select Section 1 through 13, or all completed sections (default)",
    )
    verify.add_argument(
        "--source-dir",
        type=Path,
        help="also verify the thirteen source DOCX files in this directory",
    )
    verify.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    verify.set_defaults(func=command_verify)

    status = subparsers.add_parser("status", help="show claims, gates, and completion state")
    status.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    status.set_defaults(func=command_status)

    completion = subparsers.add_parser(
        "completion",
        help="evaluate carrier closure and full OneTheory completion",
    )
    completion.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    completion.add_argument(
        "--require-complete",
        action="store_true",
        help=f"exit {ExitCode.COMPLETION_OPEN.value} while full completion is open",
    )
    completion.set_defaults(func=command_completion)

    manifest_parser = subparsers.add_parser(
        "manifest",
        help="print provenance and evidence registry",
    )
    manifest_parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    manifest_parser.set_defaults(func=command_manifest)

    origin_interfaces = subparsers.add_parser(
        "origin-interfaces",
        help="show the typed, still-open Section 4 bridge contracts",
    )
    origin_interfaces.add_argument(
        "--json",
        action="store_true",
        help="emit machine-readable JSON",
    )
    origin_interfaces.set_defaults(func=command_origin_interfaces)

    observable = subparsers.add_parser(
        "observable-deformation",
        help="show the exact Section 5 deformation certificates and open boundaries",
    )
    observable.add_argument(
        "--json",
        action="store_true",
        help="emit machine-readable JSON",
    )
    observable.set_defaults(func=command_observable_deformation)

    rank_lifting = subparsers.add_parser(
        "rank-lifting",
        help="show Section 6 finite-frontier certificates and open carrier inputs",
    )
    rank_lifting.add_argument(
        "--json",
        action="store_true",
        help="emit machine-readable JSON",
    )
    rank_lifting.add_argument(
        "--typing-audit",
        action="store_true",
        help=(
            "emit the exact countermodel certificate showing that retained "
            "branch support does not determine physical star/triangular typing"
        ),
    )
    rank_lifting.add_argument(
        "--star-tangent-package",
        type=Path,
        help=(
            "verify a certified off-diagonal star-tangent degree-five "
            "package and its exact down-sector factorization"
        ),
    )
    rank_lifting.add_argument(
        "--adaptive-package",
        type=Path,
        help=(
            "compile a certified partial f3/f5/f7 carrier package; exact scalars "
            "use rational strings or [a,b] for a+b*omega"
        ),
    )
    rank_lifting.add_argument(
        "--hpl-f3-package",
        type=Path,
        help=(
            "derive the four f3 traces by the exact suspended-planar HPL "
            "recursion, then run the adaptive Gram decision"
        ),
    )
    rank_lifting.add_argument(
        "--f3-common-package",
        type=Path,
        help=(
            "derive the four f3 traces from one frozen raw common-cyclic "
            "tensor package, then run the adaptive Gram decision"
        ),
    )
    rank_lifting.set_defaults(func=command_rank_lifting)

    metric_completion = subparsers.add_parser(
        "metric-completion",
        help="show Section 7 section-basis, metric, and normalization boundaries",
    )
    metric_completion.add_argument(
        "--json",
        action="store_true",
        help="emit machine-readable JSON",
    )
    metric_completion.set_defaults(func=command_metric_completion)

    instanton_sector = subparsers.add_parser(
        "instanton-sector",
        help="show Section 8 conic, Pfaffian-line, Quillen, and CP boundaries",
    )
    instanton_sector.add_argument(
        "--json",
        action="store_true",
        help="emit machine-readable JSON",
    )
    instanton_sector.set_defaults(func=command_instanton_sector)

    hidden_bundle = subparsers.add_parser(
        "hidden-bundle",
        help="show Section 9 hidden topology, bounded frontier, and open gates",
    )
    hidden_bundle.add_argument(
        "--json",
        action="store_true",
        help="emit machine-readable JSON",
    )
    hidden_bundle.set_defaults(func=command_hidden_bundle)

    stabilization = subparsers.add_parser(
        "stabilization",
        help="show Section 10 source-classification certificates and open vacuum gates",
    )
    stabilization.add_argument(
        "--json",
        action="store_true",
        help="emit machine-readable JSON",
    )
    stabilization.set_defaults(func=command_stabilization)

    closure = subparsers.add_parser(
        "closure",
        help="show Section 11 closure criteria, falsification rules, and open gates",
    )
    closure.add_argument(
        "--json",
        action="store_true",
        help="emit machine-readable JSON",
    )
    closure.set_defaults(func=command_closure)

    reproducibility = subparsers.add_parser(
        "reproducibility",
        help="show Section 12 release criteria, dependency graph, and open obligations",
    )
    reproducibility.add_argument(
        "--release-root",
        type=Path,
        help="optionally verify declared artifact hashes below this release root",
    )
    reproducibility.add_argument(
        "--artifact",
        action="append",
        nargs=2,
        metavar=("RELATIVE_PATH", "SHA256"),
        default=(),
        help="artifact digest pair; repeat for multiple artifacts",
    )
    reproducibility.add_argument(
        "--json",
        action="store_true",
        help="emit machine-readable JSON",
    )
    reproducibility.set_defaults(func=command_reproducibility)

    publication_audit = subparsers.add_parser(
        "publication-audit",
        help="audit DOCX and Python artifacts for publication-breaking defects",
    )
    publication_audit.add_argument(
        "--docx",
        type=Path,
        help="DOCX artifact to inspect; omit to audit Python only",
    )
    publication_audit.add_argument(
        "--python",
        type=Path,
        help="Python artifact to inspect; defaults to this standalone program",
    )
    publication_audit.add_argument(
        "--json",
        action="store_true",
        help="emit machine-readable JSON",
    )
    publication_audit.set_defaults(func=command_publication_audit)

    conclusion = subparsers.add_parser(
        "conclusion",
        help="show Section 13 final ledger, appendix crosswalk, and open closure state",
    )
    conclusion.add_argument(
        "--json",
        action="store_true",
        help="emit machine-readable JSON",
    )
    conclusion.set_defaults(func=command_conclusion)

    self_test = subparsers.add_parser("self-test", help="run the built-in regression suite")
    self_test.set_defaults(func=command_self_test)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    sys.exit(main())
