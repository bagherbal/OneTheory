"""Transfer outer Hom using the selected mixed constituent arrows.

Owns:
    Alexander--Whitney Cech convolution, Koszul exterior multiplication,
    mixed outer perturbations, finite contraction, and exact cohomology ranks.

Depends on:
    Common-Schoen mixed arrows, the reusable full-cover outer contraction, and
    exact sparse maps over the Eisenstein field.

Must not:
    Import retired pure-Cech extension arrows, fit ranks to source dimensions,
    select an outer extension ray, or infer stability and physical spectrum.

Phase 0:
    Research-only mixed constituent outer transfer in both Hom orientations.
"""

from __future__ import annotations

import json
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from functools import cache
from pathlib import Path
from typing import Protocol, cast

from onetheory.math.homological import VectorSpace
from onetheory.math.numbers import Eisenstein
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.computable_carrier.schoen_serre_outer import (
    SchoenSerreConstituent,
    SerreArrow,
    SerreObject,
    schoen_serre_outer_hom,
)
from research.experiments.computable_carrier.schoen_serre_outer_transfer import (
    KOSZUL_DEGREES,
    OuterCechBasis,
    OuterCechComponent,
    SparseOuterCechCochain,
    _components,
    _homotopy,
    _include,
    _projection_index,
    _reduced_basis,
    _target_component,
)
from research.experiments.computable_carrier.schoen_serre_outer_transfer import (
    _perturbation as _structural_perturbation,
)
from research.experiments.computable_carrier.schoen_sparse_outer import (
    SparseMap,
    _freeze_rows,
)

from .mixed_constituent_schoen_arrows import (
    Cell,
    MixedConstituentObject,
    MixedExtensionTerm,
    MixedResolutionArrow,
    mixed_schoen_constituents,
)

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/mixed_schoen_outer_transfer.json"

KOSZUL_SUBSETS = {
    "k0": (),
    "k1_x": (1,),
    "k1_u": (2,),
    "k2": (1, 2),
}
SUBSET_KOSZUL = {subset: name for name, subset in KOSZUL_SUBSETS.items()}


class MixedSchoenComplex(Protocol):
    """Structural interface consumed by the synchronized transfer."""

    @property
    def name(self) -> str: ...

    @property
    def factor(self) -> int: ...

    @property
    def twist(self) -> tuple[int, int, int]: ...

    @property
    def objects(self) -> tuple[MixedConstituentObject, ...]: ...

    @property
    def resolution_arrows(self) -> tuple[MixedResolutionArrow, ...]: ...

    @property
    def extension_terms(self) -> tuple[MixedExtensionTerm, ...]: ...


@dataclass(frozen=True, slots=True)
class MixedSchoenUnit:
    """The structure sheaf in the synchronized mixed-complex grading."""

    name: str = "O_X"
    factor: int = 0
    twist: tuple[int, int, int] = (0, 0, 0)
    objects: tuple[MixedConstituentObject, ...] = (
        MixedConstituentObject("O_X", 0, (0, 0, 0)),
    )
    resolution_arrows: tuple[MixedResolutionArrow, ...] = ()
    extension_terms: tuple[MixedExtensionTerm, ...] = ()


def mixed_schoen_unit() -> MixedSchoenUnit:
    """Return the exact one-object unit for mixed derived-Hom calculations."""

    return MixedSchoenUnit()


def _skeleton(constituent: MixedSchoenComplex) -> SchoenSerreConstituent:
    """Return the object and resolution part without any extension shortcut."""

    return SchoenSerreConstituent(
        constituent.name,
        constituent.factor,
        constituent.twist,
        None,
        tuple(
            SerreObject(item.name, item.position, item.line_degree)
            for item in constituent.objects
        ),
        tuple(
            SerreArrow(
                arrow.source,
                arrow.target,
                arrow.polynomial,
                "x" if arrow.factor == 1 else "u",
                0,
            )
            for arrow in constituent.resolution_arrows
        ),
    )


def _simplex_cup(
    left: tuple[int, ...],
    right: tuple[int, ...],
) -> tuple[int, ...] | None:
    """Return one ordered Alexander--Whitney simplex product."""

    left_degree = len(left) - 1
    right_degree = len(right) - 1
    combined = tuple(sorted(set((*left, *right))))
    if len(combined) != left_degree + right_degree + 1:
        return None
    if left != combined[: left_degree + 1]:
        return None
    if right != combined[left_degree:]:
        return None
    return combined


def _cell_cup(
    arrow: Cell,
    basis: Cell,
    composition: str,
) -> tuple[int, Cell] | None:
    """Cup one arrow cell with one outer cell in declared composition order."""

    if composition not in {"left", "right"}:
        raise ValueError("mixed outer composition is left or right")
    products = []
    for arrow_simplex, basis_simplex in zip(arrow, basis, strict=True):
        product = (
            _simplex_cup(arrow_simplex, basis_simplex)
            if composition == "left"
            else _simplex_cup(basis_simplex, arrow_simplex)
        )
        if product is None:
            return None
        products.append(product)
    arrow_degrees = tuple(len(simplex) - 1 for simplex in arrow)
    basis_degrees = tuple(len(simplex) - 1 for simplex in basis)
    crossings = (
        sum(
            arrow_degrees[right] * basis_degrees[left]
            for left in range(3)
            for right in range(left + 1, 3)
        )
        if composition == "left"
        else sum(
            basis_degrees[right] * arrow_degrees[left]
            for left in range(3)
            for right in range(left + 1, 3)
        )
    )
    return (-1 if crossings % 2 else 1), cast(Cell, tuple(products))


def _koszul_product(
    equation: int | None,
    summand: str,
    composition: str,
) -> tuple[int, str] | None:
    """Exterior-multiply one selected equation with an outer Koszul summand."""

    if equation is None:
        return 1, summand
    subset = KOSZUL_SUBSETS[summand]
    if equation in subset:
        return None
    raw = (
        (equation, *subset)
        if composition == "left"
        else (*subset, equation)
    )
    inversions = sum(
        raw[left] > raw[right]
        for left in range(len(raw))
        for right in range(left + 1, len(raw))
    )
    return (-1 if inversions % 2 else 1), SUBSET_KOSZUL[tuple(sorted(raw))]


def _term_image(
    basis: OuterCechBasis,
    coefficient: Eisenstein,
    term: MixedExtensionTerm,
    target: OuterCechComponent,
    target_cell: Cell,
    sign: int,
) -> tuple[OuterCechBasis, Eisenstein] | None:
    """Convolve one mixed arrow term with one full outer basis term."""

    return (
        OuterCechBasis(
            target,
            cast(
                tuple[int, int, int],
                tuple(
                    left + right
                    for left, right in zip(
                        basis.x_monomial,
                        term.x_monomial,
                        strict=True,
                    )
                ),
            ),
            cast(
                tuple[int, int, int],
                tuple(
                    left + right
                    for left, right in zip(
                        basis.u_monomial,
                        term.u_monomial,
                        strict=True,
                    )
                ),
            ),
            cast(
                tuple[int, int],
                tuple(
                    left + right
                    for left, right in zip(
                        basis.p_monomial,
                        term.p_monomial,
                        strict=True,
                    )
                ),
            ),
            target_cell,
        ),
        coefficient * term.coefficient * sign,
    )


class _CompatibleTermIndex:
    """Memoize compatible mixed terms without hashing full constituents."""

    def __init__(self, constituent: MixedSchoenComplex) -> None:
        self._left: dict[int, tuple[MixedExtensionTerm, ...]] = {}
        self._right: dict[int, tuple[MixedExtensionTerm, ...]] = {}
        for object_index in range(len(constituent.objects)):
            self._left[object_index] = tuple(
                term
                for term in constituent.extension_terms
                if term.source == object_index
            )
            self._right[object_index] = tuple(
                term
                for term in constituent.extension_terms
                if term.target == object_index
            )
        self._cache: dict[
            tuple[int, Cell, str, str],
            tuple[tuple[MixedExtensionTerm, str, Cell, int], ...],
        ] = {}

    def compatible(
        self,
        object_index: int,
        basis_cell: Cell,
        koszul_summand: str,
        composition: str,
    ) -> tuple[tuple[MixedExtensionTerm, str, Cell, int], ...]:
        """Return only terms with nonzero Cech and Koszul products."""

        key = object_index, basis_cell, koszul_summand, composition
        cached = self._cache.get(key)
        if cached is not None:
            return cached
        selected = (
            self._left[object_index]
            if composition == "left"
            else self._right[object_index]
        )
        result = []
        for term in selected:
            cell = _cell_cup(term.cell, basis_cell, composition)
            koszul = _koszul_product(
                term.koszul_equation,
                koszul_summand,
                composition,
            )
            if cell is None or koszul is None:
                continue
            cell_sign, target_cell = cell
            koszul_sign, target_koszul = koszul
            result.append(
                (
                    term,
                    target_koszul,
                    target_cell,
                    cell_sign * koszul_sign,
                )
            )
        frozen = tuple(result)
        self._cache[key] = frozen
        return frozen


def _mixed_extension_perturbation(
    cochain: SparseOuterCechCochain,
    left: MixedSchoenComplex,
    right: MixedSchoenComplex,
    components: dict[tuple[int, int, str], OuterCechComponent],
    left_index: _CompatibleTermIndex,
    right_index: _CompatibleTermIndex,
) -> SparseOuterCechCochain:
    """Apply both selected mixed extension arrows to outer cochains."""

    result = []
    for basis, coefficient in cochain.terms:
        component = basis.component
        object_sign = -1 if component.object_degree % 2 else 1
        koszul_sign = -1 if KOSZUL_DEGREES[component.koszul_summand] % 2 else 1
        for term, target_koszul, target_cell, product_sign in left_index.compatible(
            component.left_index,
            basis.cell,
            component.koszul_summand,
            "left",
        ):
            target = _target_component(
                components,
                term.target,
                component.right_index,
                target_koszul,
            )
            internal_degree = term.cech_degree - term.koszul_degree
            sign = product_sign
            if internal_degree % 2:
                sign *= koszul_sign * object_sign
            if term.koszul_degree % 2 and KOSZUL_DEGREES[
                component.koszul_summand
            ] % 2:
                sign *= -1
            if term.parent_degree == 0:
                sign *= -1
            image = _term_image(
                basis,
                coefficient,
                term,
                target,
                target_cell,
                sign,
            )
            if image is not None:
                result.append(image)
        for term, target_koszul, target_cell, product_sign in right_index.compatible(
            component.right_index,
            basis.cell,
            component.koszul_summand,
            "right",
        ):
            target = _target_component(
                components,
                component.left_index,
                term.source,
                target_koszul,
            )
            internal_degree = term.cech_degree - term.koszul_degree
            sign = product_sign * -object_sign
            if internal_degree % 2:
                sign *= koszul_sign
            if term.cech_degree % 2 and basis.cech_degree % 2:
                sign *= -1
            if term.parent_degree == 0:
                sign *= -1
            image = _term_image(
                basis,
                coefficient,
                term,
                target,
                target_cell,
                sign,
            )
            if image is not None:
                result.append(image)
    return SparseOuterCechCochain(tuple(result))


def _mixed_perturbation(
    cochain: SparseOuterCechCochain,
    left: MixedSchoenComplex,
    right: MixedSchoenComplex,
    left_skeleton: SchoenSerreConstituent,
    right_skeleton: SchoenSerreConstituent,
    components: dict[tuple[int, int, str], OuterCechComponent],
    left_index: _CompatibleTermIndex,
    right_index: _CompatibleTermIndex,
) -> SparseOuterCechCochain:
    """Apply equations, resolutions, and selected mixed extension arrows."""

    return _structural_perturbation(
        cochain,
        left_skeleton,
        right_skeleton,
        components,
    ) + _mixed_extension_perturbation(
        cochain,
        left,
        right,
        components,
        left_index,
        right_index,
    )


@dataclass(frozen=True, slots=True)
class MixedTransferredOuterHom:
    """One exact synchronized outer Hom after selected mixed-arrow transfer."""

    left: str
    right: str
    spaces: tuple[tuple[int, VectorSpace], ...]
    differentials: tuple[tuple[int, SparseMap], ...]
    path_depths: tuple[tuple[int, int], ...]

    @property
    def squared_zero(self) -> bool:
        """Return whether consecutive transferred maps compose to zero."""

        maps = dict(self.differentials)
        return all(
            maps[degree + 1].compose(map_).is_zero()
            for degree, map_ in self.differentials
            if degree + 1 in maps
        )

    def cohomology_dimension(self, degree: int) -> int:
        """Return one exact transferred cohomology dimension."""

        spaces = dict(self.spaces)
        maps = dict(self.differentials)
        outgoing = maps.get(degree)
        incoming = maps.get(degree - 1)
        return spaces[degree].dimension - (
            0 if outgoing is None else outgoing.rank()
        ) - (0 if incoming is None else incoming.rank())

    def as_record(self) -> dict[str, object]:
        """Serialize exact dimensions without importing a source target."""

        ranks = {degree: map_.rank() for degree, map_ in self.differentials}
        return {
            "left": self.left,
            "right": self.right,
            "space_dimensions": [
                [degree, space.dimension] for degree, space in self.spaces
            ],
            "differential_ranks": [
                [degree, ranks[degree]] for degree, _map in self.differentials
            ],
            "cohomology_dimensions": [
                [
                    degree,
                    space.dimension
                    - ranks.get(degree, 0)
                    - ranks.get(degree - 1, 0),
                ]
                for degree, space in self.spaces
            ],
            "path_depths": [list(item) for item in self.path_depths],
            "squared_zero": self.squared_zero,
        }


def _transfer_map(
    left: MixedSchoenComplex,
    right: MixedSchoenComplex,
    degree: int,
) -> tuple[SparseMap, int]:
    """Transfer one mixed full differential through the standard contraction."""

    left_skeleton = _skeleton(left)
    right_skeleton = _skeleton(right)
    reduced = schoen_serre_outer_hom(left_skeleton, right_skeleton)
    spaces = dict(reduced.total_spaces)
    source_entries = _reduced_basis(left_skeleton, right_skeleton, degree)
    target_entries = _reduced_basis(left_skeleton, right_skeleton, degree + 1)
    target_indices = {
        (
            entry.component,
            entry.x_monomial,
            entry.u_monomial,
            entry.p_monomial,
        ): entry.index
        for entry in target_entries
    }
    components = {
        (component.left_index, component.right_index, component.koszul_summand): component
        for component in _components(left_skeleton, right_skeleton)
    }
    left_index = _CompatibleTermIndex(left)
    right_index = _CompatibleTermIndex(right)
    rows: list[dict[int, Eisenstein]] = [dict() for _ in target_entries]
    maximum_depth = 0
    for source in source_entries:
        current = _include(source)
        depth = 0
        while not current.is_zero():
            image = _mixed_perturbation(
                current,
                left,
                right,
                left_skeleton,
                right_skeleton,
                components,
                left_index,
                right_index,
            )
            for basis, coefficient in image.terms:
                target_index = _projection_index(basis, target_indices)
                if target_index is not None:
                    rows[target_index][source.index] = rows[target_index].get(
                        source.index,
                        Eisenstein(0),
                    ) + coefficient
            current = _homotopy(image).scale(-1)
            depth += 1
            if depth > 16:
                raise ValueError("mixed outer Cech perturbation did not terminate")
        maximum_depth = max(maximum_depth, depth)
    return (
        SparseMap(spaces[degree], spaces[degree + 1], _freeze_rows(rows)),
        maximum_depth,
    )


@cache
def mixed_transferred_outer_hom(
    left: MixedSchoenComplex,
    right: MixedSchoenComplex,
) -> MixedTransferredOuterHom:
    """Transfer one selected mixed outer Hom exactly."""

    reduced = schoen_serre_outer_hom(_skeleton(left), _skeleton(right))
    spaces = dict(reduced.total_spaces)
    maps = []
    depths = []
    for degree, space in reduced.total_spaces:
        target = spaces.get(degree + 1)
        if space.dimension == 0 or target is None or target.dimension == 0:
            maps.append(
                (
                    degree,
                    SparseMap.zero(
                        space,
                        target or VectorSpace("zero", (), Eisenstein),
                    ),
                )
            )
            depths.append((degree, 0))
            continue
        map_, depth = _transfer_map(left, right, degree)
        maps.append((degree, map_))
        depths.append((degree, depth))
    result = MixedTransferredOuterHom(
        left.name,
        right.name,
        reduced.total_spaces,
        tuple(maps),
        tuple(depths),
    )
    if not result.squared_zero:
        raise ValueError("mixed transferred outer differential is not square zero")
    return result


def _transfer_job(
    job: tuple[int, int, int],
) -> tuple[int, int, int, SparseMap, int]:
    """Compute one independent orientation/degree map in a worker process."""

    left_index, right_index, degree = job
    constituents = mixed_schoen_constituents()
    map_, depth = _transfer_map(
        constituents[left_index],
        constituents[right_index],
        degree,
    )
    return left_index, right_index, degree, map_, depth


def _assembled_transfer(
    left_index: int,
    right_index: int,
    computed: dict[tuple[int, int, int], tuple[SparseMap, int]],
) -> MixedTransferredOuterHom:
    """Assemble one orientation from independently transferred degree maps."""

    constituents = mixed_schoen_constituents()
    left = constituents[left_index]
    right = constituents[right_index]
    reduced = schoen_serre_outer_hom(_skeleton(left), _skeleton(right))
    spaces = dict(reduced.total_spaces)
    maps = []
    depths = []
    for degree, space in reduced.total_spaces:
        item = computed.get((left_index, right_index, degree))
        if item is None:
            map_ = SparseMap.zero(
                space,
                spaces.get(
                    degree + 1,
                    VectorSpace("zero", (), Eisenstein),
                ),
            )
            depth = 0
        else:
            map_, depth = item
        maps.append((degree, map_))
        depths.append((degree, depth))
    result = MixedTransferredOuterHom(
        left.name,
        right.name,
        reduced.total_spaces,
        tuple(maps),
        tuple(depths),
    )
    if not result.squared_zero:
        raise ValueError("parallel mixed outer differential is not square zero")
    return result


@cache
def mixed_outer_transfers(
) -> tuple[MixedTransferredOuterHom, MixedTransferredOuterHom]:
    """Return both orientations using independent deterministic degree jobs."""

    constituents = mixed_schoen_constituents()
    orientations = ((0, 1), (1, 0))
    jobs = []
    for left_index, right_index in orientations:
        reduced = schoen_serre_outer_hom(
            _skeleton(constituents[left_index]),
            _skeleton(constituents[right_index]),
        )
        spaces = dict(reduced.total_spaces)
        jobs.extend(
            (left_index, right_index, degree)
            for degree, space in reduced.total_spaces
            if space.dimension > 0
            and degree + 1 in spaces
            and spaces[degree + 1].dimension > 0
        )
    with ProcessPoolExecutor(max_workers=len(jobs)) as executor:
        completed = tuple(executor.map(_transfer_job, jobs))
    computed = {
        (left, right, degree): (map_, depth)
        for left, right, degree, map_, depth in completed
    }
    return tuple(
        _assembled_transfer(left, right, computed)
        for left, right in orientations
    )  # type: ignore[return-value]


def write_mixed_outer_transfers(path: Path = OUTPUT) -> dict[str, object]:
    """Write the content-addressed selected mixed outer transfer."""

    transfers = mixed_outer_transfers()
    payload: dict[str, object] = {
        "schema": "mixed-schoen-outer-transfer-v1",
        "orientations": [item.as_record() for item in transfers],
        "all_transferred_differentials_square_zero": all(
            item.squared_zero for item in transfers
        ),
        "source_outer_dimensions_imported": False,
        "retired_pure_cech_arrows_used": False,
        "deck_actions_transferred": False,
        "next_required_object": (
            "strict P/T transfer on the mixed outer cohomology, followed by "
            "invariant representative extraction"
        ),
    }
    payload["artifact_digest"] = _canonical_digest(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)
    return payload


def main() -> int:
    """Regenerate both exact selected mixed outer transfers."""

    payload = write_mixed_outer_transfers()
    print(f"artifact_digest: {payload['artifact_digest']}")
    print(
        "all_transferred_differentials_square_zero: "
        f"{payload['all_transferred_differentials_square_zero']}"
    )
    print(f"next_required_object: {payload['next_required_object']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "MixedSchoenComplex",
    "MixedSchoenUnit",
    "MixedTransferredOuterHom",
    "mixed_outer_transfers",
    "mixed_schoen_unit",
    "mixed_transferred_outer_hom",
]
