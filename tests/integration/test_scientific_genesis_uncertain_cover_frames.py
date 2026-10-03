"""Attack original universal frame bounds on actual uncertain-input domains.

Owns:
    Every declared branch, independent raw-arrow Gaussian elimination, full
    corrected-cochain functionals, original support reuse, and scope rejection.

Depends on:
    Actual native root families, original full section data, and the existing
    independent affine polynomial and raw-arrow test validators.

Must not:
    Treat off-cover arithmetic functionals as geometric samples, choose
    extension moduli, or promote two probe columns into a metric calculation.

Phase 0:
    Research domain regressions; controlled physical integration remains open.
"""

import json
from copy import deepcopy
from functools import cache

import pytest

from onetheory.math.linear import Matrix
from onetheory.math.numbers import OMEGA, Eisenstein, Rational
from research.experiments.scientific_genesis import uncertain_cover_frames as module
from research.experiments.scientific_genesis.alternate_metric_bounded_support import (
    BoundedSupportEvaluator,
)
from research.experiments.scientific_genesis.projective_uniform_input_cells import (
    InputPolicy,
    projective_input_cell,
)
from tests.integration.test_scientific_genesis_alternate_metric_bounded_fibers import (
    _contains,
    _dehomogenized_coefficients,
    _raw_presentation,
)

bounded, roots = module.bounded, module.roots


def _functional(frame, offset=0):
    directions = (Eisenstein(1), OMEGA, OMEGA**2)
    return tuple(c.center + Eisenstein(c.radius) * directions[(i + offset) % 3]
                 for i, c in enumerate((*frame.point.x, *frame.point.u, *frame.point.p)))


def _full_boundary(values, frame, a0, a1):
    """Use original raw arrows and the entire five-row Gaussian quotient."""

    b1, b2, outer = _raw_presentation(values, frame.point)
    extension = outer[0].scale(a0) + outer[1].scale(a1)
    matrix = Matrix(tuple((*b1[i], *extension[i]) for i in range(4))
                    + tuple((0, 0, *b2[i]) for i in range(5)), scalar_type=Eisenstein)
    return matrix, bounded.fiber._quotient(matrix, (0, 2, 4, 5, 6))[0]


def _specialize(coefficients, a0, a1):
    return bounded._add(coefficients[0], bounded._add(
        tuple(tuple(c * a0 for c in row) for row in coefficients[1]),
        tuple(tuple(c * a1 for c in row) for row in coefficients[2]),
    ))


@pytest.mark.parametrize("index", range(15))
def test_every_actual_uncertain_branch_contains_independent_five_relation_gaussian_solves(index):
    name, branch, frame = module.declared_frames()[index]
    assert name in ("A", "Bx", "Bu")
    assert frame.point.root_pair == branch
    assert frame.relation_minor.center.norm() > frame.relation_minor.radius**2
    assert frame.basis_labels == ("V1:F0:0", "V1:F0:2", "V2:F0:2", "V2:F0:3")
    values = _functional(frame)
    for a0, a1 in ((Eisenstein(1), OMEGA), (OMEGA, Eisenstein(2, -1))):
        # These exact arithmetic functionals are not extension-point choices
        # or exact cover coordinates. Membership remains the native certificate.
        boundary, quotient = _full_boundary(values, frame, a0, a1)
        _contains(_specialize(frame.relations, a0, a1), boundary)
        _contains(_specialize(frame.projections, a0, a1), quotient)
        assert quotient.matmul(boundary).is_zero()


@pytest.mark.parametrize("index", (0, 9, 12))
def test_original_support_and_full_corrected_cochains_on_each_mixture_component(index):
    _, _, frame = module.declared_frames()[index]
    section = module.original_section(2655)
    coefficients = module.section_columns(frame, 2655)
    compressed = BoundedSupportEvaluator(frame).evaluate_basis(2655)
    assert [len(c.terms) for c in section.first_coefficients] == [3663, 3663]
    assert any(not c.center.is_zero() for m in coefficients[1:] for row in m for c in row)
    # Different outward arithmetic orders can give different rounded centers.
    # Overlap is a consistency check only; independent Gaussian values below
    # must separately lie in both bounds.
    assert all((a.center-b.center).norm() <= (a.radius+b.radius)**2
               for m, n in zip(coefficients, compressed, strict=True)
               for row, other in zip(m, n, strict=True)
               for a, b in zip(row, other, strict=True))
    contexts = bounded.fiber.lifts.first._context()[0], bounded.fiber.lifts.second._context()[0]
    for offset in (0, 1):
        values = _functional(frame, offset)
        constants = (_dehomogenized_coefficients(section.first_constant, values,
                                                  frame.point, contexts[0])
                     + _dehomogenized_coefficients(section.second_constant, values,
                                                   frame.point, contexts[1]))
        corrections = tuple(_dehomogenized_coefficients(c, values, frame.point, contexts[0])
                            + (Eisenstein(0),) * 5 for c in section.first_coefficients)
        a0, a1 = Eisenstein(1), OMEGA
        _, quotient = _full_boundary(values, frame, a0, a1)
        column = Matrix(tuple((c + a0 * x + a1 * y,) for c, x, y in zip(
            constants, *corrections, strict=True,
        )), scalar_type=Eisenstein)
        expected = quotient.matmul(column)
        _contains(_specialize(coefficients, a0, a1), expected)
        _contains(_specialize(compressed, a0, a1), expected)


def test_refining_the_same_input_prefix_and_roots_contracts_actual_outer_section_bounds():
    coarse = module.declared_frames()[9][2]
    x, u, _ = roots.declared_probes()[0]
    policy = InputPolicy(44, 100, 40, 56)
    refined = tuple(projective_input_cell(tuple(k * 16 + 7 for k in cell.spacing_indices),
        tuple(k * 16 + 7 for k in cell.phase_indices), policy=policy) for cell in (x, u))
    line = roots.BoundedLine(refined[1].coordinates, 0, (1, 2))
    _, partner = roots.point_line(refined[0].coordinates, line, source_side=1, parameter_pivot=0,
        policy=roots.roots.RootPolicy(Rational(1, 2**16), 72, 100, 128))
    configuration = roots.PointLineConfiguration(refined[0].coordinates, 1, line, partner)
    fine = bounded.BoundedFiberFrame(
        roots.UncertainCoverPoint(configuration, ("fixed", 0), (0, 0, 0), 100, center_bits=100),
        (0, 2), (0, 1, 2),
    )
    checked = 0
    for cm, fm in zip(module.section_columns(coarse, 2655), module.section_columns(fine, 2655),
                      strict=True):
        for cr, fr in zip(cm, fm, strict=True):
            for c, f in zip(cr, fr, strict=True):
                if c.radius:
                    assert f.radius < c.radius / 8
                    assert (c.center - f.center).norm() <= (c.radius - f.radius)**2
                    checked += 1
                else:
                    assert f == c
    assert checked == 6


def test_declared_pivot_order_changes_only_signed_minor_not_the_original_quotient():
    frame = module.declared_frames()[9][2]
    reordered = bounded.BoundedFiberFrame(frame.point, (2, 0), (0, 1, 2))
    for original, changed in zip(frame.projections, reordered.projections, strict=True):
        assert all((a.center-b.center).norm() <= (a.radius+b.radius)**2
                   for row, other in zip(original, changed, strict=True)
                   for a, b in zip(row, other, strict=True))
    assert (reordered.relation_minor.center + frame.relation_minor.center).norm() <= (
        reordered.relation_minor.radius + frame.relation_minor.radius
    )**2
    assert reordered.relation_minor.center.norm() > reordered.relation_minor.radius**2


@cache
def _actual_record():
    return module.frame_record()


def test_executed_domains_and_original_sections_reproduce_the_saved_output():
    assert module.read_frames() == _actual_record()
    packet = _actual_record()
    assert len(packet["actual_domain_probes"]) == 15
    assert [sum(p["component"] == name for p in packet["actual_domain_probes"])
            for name in ("A", "Bx", "Bu")] == [9, 3, 3]
    _, parent = bounded.fiber._verified_payload(bounded.fiber.lifts.OUTPUT)
    assert packet["original_section_probes"][1]["correction_cochain_digests"] == (
        parent["actual_coefficient_probes"][0]["coefficient_digests"]
    )
    for domain in packet["actual_domain_probes"]:
        assert [p["basis_index"] for p in domain["actual_universal_section_probes"]] == [0, 2655]
        injection = domain["actual_universal_section_probes"][0]
        assert all(c["center"] == ["0", "0"] and c["radius"] == "0"
                   for m in injection["coefficient_columns_constant_a0_a1"][1:]
                   for row in m for c in row)
    for flag in ("centers_are_exact_cover_points",
                 "complete_5345_column_matrix_on_new_domains_available",
                 "global_input_coverage_available", "independent_sampling_cloud_available",
                 "controlled_integral_available", "ricci_flat_metric_available",
                 "hym_metric_available",
                 "physical_yukawas_available", "common_stabilized_vacuum_available",
                 "extension_point_selected", "observations_used"):
        assert packet[flag] is False


@pytest.mark.parametrize("attack", (
    "branch", "basis", "minor", "correction", "omission", "scope", "typing",
))
def test_rehashed_actual_domain_output_cannot_change_original_bounds_or_scope(tmp_path, attack):
    packet = deepcopy(_actual_record())
    domain = packet["actual_domain_probes"][0]
    if attack == "branch":
        domain["root_pair"] = [1, 1]
    elif attack == "basis":
        domain["fiber_basis_labels"].reverse()
    elif attack == "minor":
        domain["relation_minor"]["radius"] = "0"
    elif attack == "correction":
        domain["actual_universal_section_probes"][1][
            "coefficient_columns_constant_a0_a1"
        ][1][0][0]["center"] = ["0", "0"]
    elif attack == "omission":
        packet["actual_domain_probes"].pop()
    elif attack == "typing":
        domain["root_pair"] = [False, 0]
    else:
        packet["controlled_integral_available"] = True
    packet["artifact_digest"] = roots._digest(packet)
    path = tmp_path / "altered.json"
    path.write_text(json.dumps(packet))
    with pytest.raises(ValueError, match="domains, sections, or scope"):
        module.read_frames(path)


def test_a_changed_complete_archive_is_not_hidden_by_cached_domain_objects(monkeypatch):
    module.declared_frames()
    original = module.Path.read_bytes
    path = next(iter(_actual_record()["original_section_archive_sha256"]))

    def altered_bytes(file):
        data = original(file)
        return data + b"invalid" if file == module.ROOT / path else data

    monkeypatch.setattr(module.Path, "read_bytes", altered_bytes)
    with pytest.raises(ValueError, match="complete section archive changed"):
        module.read_frames()
