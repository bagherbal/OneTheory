"""Independently replay the actual down-Higgs natural quotient cocycle.

Owns:
    Literal covector retargeting, independently formed full actions and
    ordered products, original differential identities, and scope attacks.

Depends on:
    Pinned down-Higgs witnesses and the unchanged full quotient/exterior engines.

Must not:
    Rerun the primitive search, borrow up-sector values, or infer flavor matrices.

Phase 0:
    Conditional heterotic research verification; physical normalization is absent.
"""

import json

import pytest

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_invariants import (
    _canonical_digest,
)
from research.experiments.scientific_genesis import alternate_down_higgs_quotient_cone as cone
from research.experiments.scientific_genesis.alternate_down_higgs_hom_representative import (
    load_down_higgs_hom,
)
from research.experiments.scientific_genesis.alternate_up_dual_higgs_inputs import _quotient
from research.experiments.scientific_genesis.alternate_up_ff_entries import checked_coupled_higgs
from research.experiments.scientific_genesis.alternate_up_higgs_quotient_cone import (
    alternate_higgs_quotient_connecting_arrow,
    alternate_higgs_quotient_models,
    quotient_higgs_covector,
)
from research.experiments.scientific_genesis.mixed_constituent_schoen_arrows import (
    MixedConstituentObject,
)
from research.experiments.scientific_genesis.mixed_schoen_common_dga import mixed_outer_cup
from research.experiments.scientific_genesis.mixed_schoen_exterior_square import (
    reciprocal_covector_wedge,
)
from research.experiments.scientific_genesis.mixed_schoen_outer_actions import _MixedContraction
from research.experiments.scientific_genesis.mixed_schoen_outer_transfer import (
    MixedSchoenUnit,
    mixed_schoen_unit,
)

DIGEST = "50d0a3f0f2547f5c1eb05444765b2322075dc03fd56b2b65cf7874534044274f"


@pytest.fixture(scope="module")
def actual():
    return cone.load_down_higgs_quotient_cone(expected_digest=DIGEST)


def test_actual_down_higgs_covector_has_the_original_full_quotient_presentation(actual) -> None:
    _, witnesses = actual
    _, hom = load_down_higgs_hom(expected_digest=cone.HOM_DIGEST)
    h = witnesses["quotient_covector"]
    assert h == quotient_higgs_covector(hom)
    assert len(h.terms) == 351
    _, quotient = alternate_higgs_quotient_models()
    assert len(quotient.objects) == 7
    assert len(quotient.resolution_arrows) == 6
    assert _MixedContraction(mixed_schoen_unit(), quotient).differential(h).is_zero()


@pytest.mark.parametrize("index", (0, 1))
def test_both_actual_down_higgs_actions_and_primitives_replay_in_full(actual, index) -> None:
    _, witnesses = actual
    _, full = load_down_higgs_hom(expected_digest=cone.HOM_DIGEST)
    second, _ = alternate_higgs_quotient_models()
    exterior, context = cone.alternate_up_exterior_context()
    b = MixedSchoenUnit("B1", 0, cone.QUOTIENT_LINE, (
        MixedConstituentObject("B1", 0, cone.QUOTIENT_LINE),
    ))
    independently_ordered = reciprocal_covector_wedge(full, _quotient(
        cone.alternate_outer_coefficient(index), _MixedContraction(b, second),
    ), exterior, context, 1, 1)
    product = witnesses[f"ordered_product_a{index}"]
    action = witnesses[f"action_a{index}"]
    correction = witnesses[f"correction_a{index}"]
    assert product == independently_ordered
    assert action == mixed_outer_cup(witnesses["quotient_covector"],
                                    alternate_higgs_quotient_connecting_arrow(index))
    assert action == product.scale(-1)
    assert context.differential(product).is_zero()
    differential = context.differential(correction)
    assert differential == product
    assert (differential + action).is_zero()
    assert len(product.terms) == (183258, 159570)[index]
    assert len(correction.terms) == (88650, 76014)[index]


@pytest.mark.parametrize("index", (0, 1))
def test_actual_down_higgs_passes_the_same_coupled_scalar_input_checker(actual, index) -> None:
    """Its complete Higgs equations must hold without any up input substitution."""

    _, witnesses = actual
    h, kappa, _ = checked_coupled_higgs(
        index, witnesses["quotient_covector"], witnesses[f"correction_a{index}"],
    )
    assert not h.is_zero() and not kappa.is_zero()


@pytest.mark.parametrize("field,value", (
    ("native_hom_character", [2, 1]), ("repaired_higgs_forward_character", [0, 2]),
    ("outer_parameter_basis", ["a1", "a0"]), ("quotient_is_a_vector_bundle", True),
    ("full_exterior_square_higgs_constructed", True), ("extension_point_selected", True),
    ("physical_yukawas_available", True),
))
def test_rehashed_down_higgs_scope_and_routing_changes_are_rejected(tmp_path, field, value) -> None:
    record = json.loads(cone.OUTPUT.read_text())
    record.pop("artifact_digest")
    record[field] = value
    record["artifact_digest"] = _canonical_digest(record)
    path = tmp_path / cone.OUTPUT.name
    path.write_text(json.dumps(record))
    path.with_suffix(".cochains.json.gz").symlink_to(cone.OUTPUT.with_suffix(".cochains.json.gz"))
    with pytest.raises(ValueError, match="basis, parents, or scope"):
        cone.load_down_higgs_quotient_cone(path, expected_digest=record["artifact_digest"])


def test_down_higgs_absent_or_unpinned_witnesses_have_no_search_fallback(tmp_path) -> None:
    path = tmp_path / cone.OUTPUT.name
    path.write_bytes(cone.OUTPUT.read_bytes())
    with pytest.raises(FileNotFoundError):
        cone.load_down_higgs_quotient_cone(path, expected_digest=DIGEST)
    with pytest.raises(ValueError, match="expected content digest"):
        cone.load_down_higgs_quotient_cone(expected_digest="0"*64)
