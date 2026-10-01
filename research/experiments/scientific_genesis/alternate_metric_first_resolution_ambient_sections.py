"""Generate invariant ambient sections in the first Hilbert--Burch blocks.

Owns:
    Actual determinant-repaired block actions, sparse Reynolds orbit sums,
    and deterministic ambient invariant-generator streams for F0 and F1.

Depends on:
    The frozen first constituent, exact Schoen coordinate lifts, declared
    metric twist, and its common flat-character repair.

Must not:
    Descend individual F0 lines, identify ambient generators with sections
    of the restricted quotient sheaf, or infer a numerical bundle metric.

Phase 0:
    Research-only ambient inputs for exact Koszul and Hilbert--Burch quotients.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterator
from pathlib import Path
from typing import cast

from onetheory.math.linear import Matrix
from onetheory.math.numbers import OMEGA, OMEGA2, Eisenstein
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_invariants import (
    _canonical_digest,
)
from research.experiments.computable_carrier.schoen_sparse_actions import (
    SchoenSparseDeckAction,
    _monomial_action,
    schoen_sparse_deck_actions,
)

from .alternate_constituent_hom_actions import _common_frame
from .alternate_metric_quotient_generation import CONE
from .alternate_metric_quotient_generation import OUTPUT as GENERATION
from .mixed_constituent_schoen_arrows import mixed_schoen_constituents
from .mixed_schoen_outer_universal_cone import _verified_payload

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / (
    "data/generated/scientific_genesis/alternate_metric_first_resolution_ambient_sections.json"
)

type Monomial8 = tuple[int, int, int, int, int, int, int, int]
type Label = tuple[int, Monomial8]
type SparseSection = dict[Label, Eisenstein]


def _ambient_monomials(x_degree: int, u_degree: int, p_degree: int) -> Iterator[Monomial8]:
    for x0 in range(x_degree + 1):
        for x1 in range(x_degree - x0 + 1):
            for u0 in range(u_degree + 1):
                for u1 in range(u_degree - u0 + 1):
                    for mu in range(p_degree + 1):
                        yield (
                            x0, x1, x_degree - x0 - x1,
                            u0, u1, u_degree - u0 - u1,
                            mu, p_degree - mu,
                        )


def _ambient_monomial_action(
    monomial: Monomial8, action: SchoenSparseDeckAction,
) -> tuple[Eisenstein, Monomial8]:
    x_scalar, x_image = _monomial_action(monomial[:3], action.x_images)
    u_scalar, u_image = _monomial_action(monomial[3:6], action.u_images)
    p_scalar, p_image = _monomial_action(monomial[6:], action.p_images)
    return (
        x_scalar * u_scalar * p_scalar,
        cast(Monomial8, x_image + u_image + p_image),
    )


def _block_frame(frame: Matrix, indices: tuple[int, ...]) -> Matrix:
    return Matrix(
        tuple(tuple(frame[row][column] for column in indices) for row in indices),
        scalar_type=Eisenstein,
    )


def _apply(
    section: SparseSection, action: SchoenSparseDeckAction, frame: Matrix,
) -> SparseSection:
    result: SparseSection = {}
    for (source, monomial), coefficient in section.items():
        coordinate_scalar, image = _ambient_monomial_action(monomial, action)
        for target in range(frame.row_count):
            value = frame[target][source]
            if value.is_zero():
                continue
            label = (target, image)
            updated = result.get(label, Eisenstein(0)) + coefficient * value * coordinate_scalar
            if updated.is_zero():
                result.pop(label, None)
            else:
                result[label] = updated
    return result


def _orbit_sum(
    label: Label, p_action: SchoenSparseDeckAction, p_frame: Matrix,
) -> SparseSection:
    current = {label: Eisenstein(1)}
    result: SparseSection = {}
    for _ in range(3):
        for target, value in current.items():
            result[target] = result.get(target, Eisenstein(0)) + value
        current = _apply(current, p_action, p_frame)
    if current != {label: Eisenstein(1)}:
        raise ValueError("the actual Hilbert--Burch P action lost order three")
    return {target: value for target, value in result.items() if not value.is_zero()}


def _first_blocks() -> tuple[
    SchoenSparseDeckAction, SchoenSparseDeckAction,
    tuple[Matrix, Matrix], tuple[Matrix, Matrix],
]:
    first = mixed_schoen_constituents()[0]
    if (
        first.name != "V1"
        or [item.name for item in first.objects]
        != ["A", "F0:0", "F0:1", "F0:2", "F1:0", "F1:1"]
    ):
        raise ValueError("the actual first Hilbert--Burch object order changed")
    p_action, t_action = schoen_sparse_deck_actions()
    p_full = _common_frame(first, p_action).scale(OMEGA)
    t_full = _common_frame(first, t_action).scale(OMEGA2)
    f0 = (_block_frame(p_full, (1, 2, 3)), _block_frame(t_full, (1, 2, 3)))
    f1 = (_block_frame(p_full, (4, 5)), _block_frame(t_full, (4, 5)))
    for (p_frame, t_frame), degree in ((f0, (11, 17, 2)), (f1, (10, 17, 2))):
        identity = Matrix.identity(p_frame.row_count, scalar_type=Eisenstein)
        coordinate_commutator = OMEGA2 ** (degree[0] + degree[1])
        if (
            p_frame**3 != identity
            or t_frame**3 != identity
            or (p_frame @ t_frame).scale(coordinate_commutator)
            != t_frame @ p_frame
        ):
            raise ValueError("the actual block frame fails the exact deck relations")
    if (
        any(f0[0][row][column].is_zero() is False for row in range(3)
            for column in range(3) if column != (row + 1) % 3)
        or any(f0[1][row][column].is_zero() is False for row in range(3)
               for column in range(3) if row != column)
        or any(f1[1][row][column].is_zero() is False for row in range(2)
               for column in range(2) if row != column)
    ):
        raise ValueError("the first ambient block no longer has its sparse form")
    return p_action, t_action, f0, f1


def invariant_first_ambient_generators(
    role: str,
) -> Iterator[tuple[Label, SparseSection]]:
    """Yield actual-frame invariant ambient block sections without quotienting."""

    p_action, t_action, f0, f1 = _first_blocks()
    if role == "F0":
        p_frame, t_frame = f0
        seen: set[Label] = set()
        for monomial in _ambient_monomials(11, 17, 2):
            t_scalar, t_image = _ambient_monomial_action(monomial, t_action)
            if t_image != monomial:
                raise ValueError("the first F0 T action is not monomial-diagonal")
            for block in range(3):
                label = (block, monomial)
                if t_scalar * t_frame[block][block] != Eisenstein(1) or label in seen:
                    continue
                orbit_labels = []
                current = {label: Eisenstein(1)}
                for _ in range(3):
                    if len(current) != 1:
                        raise ValueError("the F0 P action stopped being monomial")
                    orbit_labels.append(next(iter(current)))
                    current = _apply(current, p_action, p_frame)
                if current != {label: Eisenstein(1)} or len(set(orbit_labels)) != 3:
                    raise ValueError("the F0 P orbit did not close in three steps")
                seen.update(orbit_labels)
                canonical = min(orbit_labels)
                section = _orbit_sum(canonical, p_action, p_frame)
                if (
                    _apply(section, p_action, p_frame) != section
                    or _apply(section, t_action, t_frame) != section
                ):
                    raise ValueError("an F0 ambient generator is not invariant")
                yield canonical, section
        return
    if role != "F1":
        raise ValueError("only the actual F0/F1 resolution blocks are supported")
    p_frame, t_frame = f1
    seen_monomials: set[Monomial8] = set()
    for monomial in _ambient_monomials(10, 17, 2):
        if monomial in seen_monomials:
            continue
        t_scalar, t_image = _ambient_monomial_action(monomial, t_action)
        if t_image != monomial:
            raise ValueError("the first F1 T action is not monomial-diagonal")
        current_monomial = monomial
        orbit_monomials = []
        for _ in range(3):
            orbit_monomials.append(current_monomial)
            _factor, current_monomial = _ambient_monomial_action(
                current_monomial, p_action
            )
        if current_monomial != monomial or len(set(orbit_monomials)) != 3:
            raise ValueError("the F1 ambient monomial P orbit changed")
        seen_monomials.update(orbit_monomials)
        canonical = min(orbit_monomials)
        for block in range(2):
            if t_scalar * t_frame[block][block] != Eisenstein(1):
                continue
            label = (block, canonical)
            section = _orbit_sum(label, p_action, p_frame)
            if (
                _apply(section, p_action, p_frame) != section
                or _apply(section, t_action, t_frame) != section
                or section.get(label) != Eisenstein(1)
            ):
                raise ValueError("an F1 ambient generator is not independent and fixed")
            yield label, section


def _generator_digest(role: str) -> tuple[int, str, dict[str, object]]:
    digest = hashlib.sha256()
    count = 0
    first: dict[str, object] | None = None
    for label, section in invariant_first_ambient_generators(role):
        record = {
            "label": [label[0], list(label[1])],
            "terms": [
                [block, list(monomial), str(value)]
                for (block, monomial), value in sorted(section.items())
            ],
        }
        digest.update(json.dumps(record, sort_keys=True, separators=(",", ":")).encode("utf-8"))
        digest.update(b"\n")
        if first is None:
            first = record
        count += 1
    if first is None:
        raise ValueError("no actual invariant ambient generators were produced")
    return count, digest.hexdigest(), first


def alternate_metric_first_resolution_ambient_sections() -> dict[str, object]:
    """Certify both actual first-resolution ambient invariant streams."""

    generation_digest, generation = _verified_payload(GENERATION)
    cone_digest, cone = _verified_payload(CONE)
    if (
        generation.get("schema") != "alternate-metric-quotient-generation-v2"
        or generation.get("generating_twist_cover_degree") != [14, 16, 1]
        or generation.get("prerequisite_artifact_digests", {}).get("alternate_cone")
        != cone_digest
        or cone.get("common_flat_character_twist") != [1, 2]
    ):
        raise ValueError("the actual carrier or metric twist changed")
    p_action, t_action, f0, f1 = _first_blocks()
    records = []
    for role, degree, frames, expected in (
        ("F0", (11, 17, 2), f0, 13338),
        ("F1", (10, 17, 2), f1, 7524),
    ):
        count, digest, example = _generator_digest(role)
        if count != expected:
            raise ValueError("the actual invariant ambient block dimension changed")
        records.append({
            "role": role,
            "twisted_line_degree": list(degree),
            "block_rank": frames[0].row_count,
            "p_frame": [[str(value) for value in row] for row in frames[0].rows],
            "t_frame": [[str(value) for value in row] for row in frames[1].rows],
            "ambient_invariant_generator_count": count,
            "ordered_generator_stream_sha256": digest,
            "first_generator": example,
            "both_generators_fix_every_section": True,
        })
    return {
        "schema": "alternate-metric-first-resolution-ambient-sections-v1",
        "carrier_status": "conditional on the selected heterotic UV realization",
        "twist_cover_degree": [14, 16, 1],
        "twist_linearization": "natural commuting ambient P/T coordinate lifts",
        "common_flat_character_twist": [1, 2],
        "deck_generator_names": [p_action.name, t_action.name],
        "blocks": records,
        "individual_f0_lines_descended": False,
        "restricted_hilbert_burch_quotient_basis_available": False,
        "first_constituent_section_basis_available": False,
        "numerical_metrics_available": False,
        "observational_inputs_used": False,
        "prerequisite_artifact_digests": {
            "generation": generation_digest,
            "alternate_cone": cone_digest,
        },
    }


def write_alternate_metric_first_resolution_ambient_sections(
    path: Path = OUTPUT,
) -> dict[str, object]:
    """Write one content-addressed actual-block ambient generator certificate."""

    payload = alternate_metric_first_resolution_ambient_sections()
    payload["artifact_digest"] = _canonical_digest(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)
    return payload


if __name__ == "__main__":
    report = write_alternate_metric_first_resolution_ambient_sections()
    print(f"artifact_digest: {report['artifact_digest']}")
    print("ambient_counts:", [
        item["ambient_invariant_generator_count"] for item in report["blocks"]
    ])
