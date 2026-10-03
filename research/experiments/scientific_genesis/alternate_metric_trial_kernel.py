"""Enclose the complete original trial kernel and derive its global projection bounds.

Owns:
    Explicit parameter-domain inverse admission, full-basis factorized kernel
    actions and source-bound global estimates for the declared unit initializer.

Depends on:
    The original covariance and all section columns, exact polynomial determinants,
    existing circular bounds, quotient generation and the global auxiliary weight.

Must not:
    Choose extension or vacuum points, replace sections by probes, infer a balanced
    fixed point, invent independence, untwist a metric or report physical Yukawas.

Phase 0:
    Research trial-integrand prerequisite only; physical normalization is unresolved.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from fractions import Fraction
from functools import cache
from pathlib import Path

from onetheory.math.numbers import Eisenstein, Rational
from onetheory.math.polynomials import Polynomial, determinant

from . import alternate_metric_global_weight_bound as global_weight
from . import alternate_section_covariance as covariance

Ball = covariance.Ball
bounds = covariance.completed.bounds
fiber = covariance.completed.bounded
ROOT = covariance.ROOT
OUTPUT = covariance.OUTPUT.with_name("alternate_metric_trial_kernel.json")
PROOF = Path(__file__).with_name("ALTERNATE_METRIC_TRIAL_KERNEL_NOTE.md")
COVARIANCE_DIGEST = "93cdd93105e5723fe7312c574cbe436333414c1593ba5ff1fe58c85fea448988"
PARENT_DIGESTS = (
    ("alternate_metric_quotient_generation.json",
     "3ca16bfa116c6b5530d73e74486eb196d37dbf9c0f7e75d445e84c41176fe063"),
    ("alternate_metric_lift_operator_certificate.json",
     "6870cdf9bc875777e8ded58e6b434d865204b8aa9aa69c6194e5b5463d55eb82"),
    ("alternate_metric_global_weight_bound.json",
     "96e3d216aa6157dab686069b095e304de5f7e9600348f42c00fff0691986c0f4"),
)
PARENT_PROOFS = (
    ("ALTERNATE_METRIC_QUOTIENT_GENERATION_NOTE.md",
     "f900fbd7433d6f624b13ba8065cd0a6b396b13757428e7fbd551dbabde01f726"),
    ("ALTERNATE_METRIC_LIFT_OPERATOR_CERTIFICATE_NOTE.md",
     "fd34381d477f91bcd912771dbefcc9b39f95c5499850e19b427b5673433e7820"),
)


def _covariance_source_guard():
    digest, record = covariance.completed.fiber._verified_payload(covariance.OUTPUT)
    if (digest != COVARIANCE_DIGEST or record["proof_sha256"]
        != hashlib.sha256(covariance.PROOF.read_bytes()).hexdigest()):
        raise ValueError("the original covariance input or its proof changed")
    return digest


def _global_sources():
    for name, expected in PARENT_PROOFS:
        if hashlib.sha256(PROOF.with_name(name).read_bytes()).hexdigest() != expected:
            raise ValueError("an established generation or lift proof changed")
    records = []
    for name, expected in PARENT_DIGESTS:
        digest, record = covariance.completed.fiber._verified_payload(OUTPUT.with_name(name))
        if digest != expected:
            raise ValueError("an established generation, lift or global weight source changed")
        records.append(record)
    generation, lifts, weight = records
    if (generation["rank_four_quotient_generated_for_all_alternate_p1"] is not True
        or generation["quotient_h0_rank_four_at_generating_twist"] != 5345
        or generation["generating_twist_cover_degree"] != [14, 16, 1]
        or lifts["full_universal_lift_formula_certified"] is not True
        or lifts["rank_four_section_basis_available"] is not True
        or weight["normalized_volume_scale"] != ["1", "0"]
        or type(weight["covering_degree"]) is not int or weight["covering_degree"] != 9
        or weight["proof_sha256"] != hashlib.sha256(
            (ROOT / weight["proof"]).read_bytes()).hexdigest()):
        raise ValueError("global kernel hypotheses or the unchanged auxiliary conventions changed")
    return tuple(records)


@cache
def _four_determinant_formula():
    # The old bounded pivot helper is deliberately capped at size three.
    # Extend that demonstrated deficiency using the SAME exact determinant engine.
    variables = tuple(Polynomial.monomial(tuple(int(i == j) for j in range(16)),
                                          scalar_type=Eisenstein) for i in range(16))
    return determinant(tuple(variables[4*i:4*(i+1)] for i in range(4)))


def _real_enclosure(value):
    """Project a bound for a proved-real target, rejecting an empty real slice."""

    if 3 * value.center.b**2 > 4 * value.radius**2:
        raise ValueError("a claimed Hermitian real target has no real value in its enclosure")
    return Ball(Eisenstein(value.center.a - value.center.b / 2), value.radius,
                value.bits, value.center_bits)


def _hermitian(matrix):
    size = len(matrix)
    return tuple(tuple(_real_enclosure(matrix[i][j]) if i == j else
        matrix[i][j] if i < j else matrix[j][i].conjugate()
        for j in range(size)) for i in range(size))


def gram_on(actual, parameters):
    """Enclose the entire actual covariance on two explicit complex disks."""

    parameters = tuple(parameters)
    if (len(parameters) != 2 or any(not isinstance(p, Ball) or p.bits != actual.bits
        or p.center_bits != actual.center_bits for p in parameters)):
        raise ValueError("explicit compatible complex a0/a1 enclosures are required")
    eta = (parameters[0]._coerce(1), *parameters)
    zero = eta[0]._coerce(0)
    size = len(actual.fiber_labels)
    return _hermitian(tuple(tuple(sum((actual.blocks[m][n][i][j] * eta[m]
        * eta[n].conjugate() for m in range(3) for n in range(3)
        if actual.blocks[m][n][i][j].radius or not actual.blocks[m][n][i][j].center.is_zero()),
        zero) for j in range(size)) for i in range(size)))


def _inverse_with_unit_certificate(actual, parameters):
    certificate = covariance.unit_determinant_certificate(actual)
    structural_lower = Rational(Fraction(certificate[
        "all_complex_parameter_determinant_lower_bound"]))
    gram = gram_on(actual, parameters)
    determinant_ball = _real_enclosure(bounds.polynomial_value(
        _four_determinant_formula(), tuple(c for row in gram for c in row)))
    lower = max(structural_lower, determinant_ball.center.a - determinant_ball.radius)
    upper = determinant_ball.center.a + determinant_ball.radius
    if lower > upper:
        raise ValueError("the structural determinant bound contradicts the arithmetic enclosure")
    denominator = bounds.Interval(lower, upper, actual.bits)
    if denominator.lower <= 0:
        raise ValueError("the declared bound precision cannot retain determinant positivity")
    # An unscaled inverse determinant can be far below the absolute dyadic
    # mesh even though the FINAL inverse entries are resolvable. Declare the
    # exact arithmetic rescaling: adj(G)/M divided by det(G)/M, M=upper(det G).
    # This is not a physical normalization or an increase of precision.
    scale = denominator.upper
    normalized = bounds.Interval(denominator.lower / scale, Rational(1), actual.bits)
    if normalized.lower <= 0:
        raise ValueError("the declared precision cannot retain the scaled determinant positivity")
    reciprocal = covariance._interval_ball(normalized.inverse(), center_bits=actual.center_bits)
    adjugate = tuple(tuple(fiber._determinant(tuple(tuple(gram[r][c]
        for c in range(4) if c != i) for r in range(4) if r != j)) * ((-1)**(i+j))
        for j in range(4)) for i in range(4))
    inverse = _hermitian(tuple(tuple((c * (Rational(1) / scale)) * reciprocal for c in row)
                              for row in adjugate))
    return gram, denominator, inverse, structural_lower


@cache
def _all_columns():
    return tuple(covariance.original_columns(bits=80, center_bits=80))


@dataclass(frozen=True, slots=True)
class TrialKernel:
    """Full original factorization K=S^dagger G^-1 S on a declared region."""

    actual: covariance.Covariance
    parameters: tuple[Ball, Ball]
    columns: tuple
    gram: tuple
    denominator: bounds.Interval
    inverse: tuple
    structural_lower: Rational

    def __post_init__(self):
        parameters = tuple(self.parameters)
        columns = tuple((index, tuple(tuple(row) for row in values))
                        for index, values in self.columns)
        if self.actual != covariance.declared_covariance() or columns != _all_columns():
            raise ValueError("the original complete covariance and actual columns are required")
        covariance.unit_determinant_certificate(self.actual)
        if (len(parameters) != 2 or any(not isinstance(p, Ball)
            or p.bits != self.actual.bits or p.center_bits != self.actual.center_bits
            for p in parameters) or len(columns) != 5345):
            raise ValueError("the full original kernel requires compatible parameters and columns")
        for expected, (index, values) in enumerate(columns):
            if (type(index) is not int or index != expected or len(values) != 3
                or any(len(row) != 4 for row in values)
                or any(not isinstance(c, Ball) or c.bits != self.actual.bits
                       or c.center_bits != self.actual.center_bits for row in values for c in row)):
                raise ValueError("every complete original column and precision must be retained")
        gram = tuple(tuple(row) for row in self.gram)
        inverse = tuple(tuple(row) for row in self.inverse)
        for matrix in (gram, inverse):
            if (len(matrix) != 4 or any(len(row) != 4 for row in matrix)
                or any(not isinstance(c, Ball) or c.bits != self.actual.bits
                       or c.center_bits != self.actual.center_bits for row in matrix for c in row)
                or covariance._adjoint(matrix) != matrix):
                raise ValueError("named rank-four Hermitian bounds must use one declared precision")
        if (not isinstance(self.denominator, bounds.Interval)
            or self.denominator.bits != self.actual.bits or self.denominator.lower <= 0
            or self.structural_lower != Rational(Fraction(covariance.unit_determinant_certificate(
                self.actual)["all_complex_parameter_determinant_lower_bound"]))):
            raise ValueError("the original structural positive determinant certificate is required")
        expected_gram, expected_denominator, expected_inverse, _ = _inverse_with_unit_certificate(
            self.actual, parameters,
        )
        if (gram != expected_gram or self.denominator != expected_denominator
            or inverse != expected_inverse):
            raise ValueError(
                "the admitted inverse must reproduce its complete actual factorization",
            )
        object.__setattr__(self, "parameters", parameters)
        object.__setattr__(self, "columns", columns)
        object.__setattr__(self, "gram", gram)
        object.__setattr__(self, "inverse", inverse)

    def section_columns(self):
        """Evaluate every original constant/a0/a1 column, including uncertain zeros."""

        eta = (self.parameters[0]._coerce(1), *self.parameters)
        zero = eta[0]._coerce(0)
        for index, values in self.columns:
            yield index, tuple(sum((values[m][r] * eta[m] for m in range(3)
                if values[m][r].radius or not values[m][r].center.is_zero()), zero)
                for r in range(4))

    def apply(self, coordinates, *, basis_digest, indices):
        """Consume and return the whole original basis, not a substitute projection."""

        if basis_digest != self.actual.form.basis_digest:
            raise ValueError("the vector and kernel section bases are incompatible")
        indices = tuple(indices)
        if (any(type(i) is not int for i in indices) or indices != self.actual.form.indices):
            raise ValueError("the exact complete ordered original indices are required")
        coordinates = tuple(Eisenstein.coerce(c) for c in coordinates)
        if len(coordinates) != 5345:
            raise ValueError(
                "a complete explicitly supplied exact section-coordinate vector is required",
            )
        before = covariance._parents(), _covariance_source_guard()
        columns = tuple(self.section_columns())
        zero = columns[0][1][0]._coerce(0)
        section_value = tuple(sum((column[r] * coordinates[index] for index, column in columns
            if not coordinates[index].is_zero()), zero) for r in range(4))
        inverse_value = tuple(sum((c * x for c, x in zip(row, section_value, strict=True)), zero)
                              for row in self.inverse)
        result = tuple(sum((c.conjugate() * x for c, x in zip(column, inverse_value, strict=True)),
                           zero) for _, column in columns)
        if (covariance._parents(), _covariance_source_guard()) != before:
            raise ValueError("an original source changed during complete kernel application")
        return result


def build_kernel(parameters):
    """Admit the actual complete unit initializer without selecting parameters."""

    parameters = tuple(parameters)
    if len(parameters) != 2 or any(not isinstance(p, Ball) or p.bits != 80
                                   or p.center_bits != 80 for p in parameters):
        raise ValueError("explicit original-precision complex parameter enclosures are required")
    record = covariance.read_covariance()
    if hashlib.sha256(covariance.completed._canonical(record)).hexdigest() != COVARIANCE_DIGEST:
        raise ValueError("the original complete covariance changed its trusted identity")
    before = covariance._parents(), _global_sources()
    actual = covariance.declared_covariance()
    gram, denominator, inverse, lower = _inverse_with_unit_certificate(actual, parameters)
    result = TrialKernel(actual, parameters, _all_columns(), gram, denominator, inverse, lower)
    if (record["exact_column_stream_sha256"] != actual.form.basis_digest
        or (covariance._parents(), _global_sources()) != before):
        raise ValueError("an original source changed during full kernel admission")
    return result


def global_kernel_bounds():
    """Derive whole-family unit-H bounds, not empirical section extrema or a cloud."""

    before = _global_sources()
    weight = global_weight.bound_artifact()
    if weight["artifact_digest"] != PARENT_DIGESTS[2][1]:
        raise ValueError("the original global weight identities no longer reproduce")
    result = {}
    for name in ("cover", "quotient"):
        b = Rational(Fraction(weight[f"{name}_weight_upper_without_pi_cubed"]))
        result[name] = {
            "operator_norm_upper_without_pi_cubed": str(b),
            "diagonal_upper_without_pi_cubed": str(b),
            "off_diagonal_modulus_upper_without_pi_cubed": str(b / 2),
            "frobenius_squared_upper_without_pi_to_six": str(4 * b**2),
            "conditional_sample_mean_squared_frobenius_error_numerator_without_pi_to_six":
                str(4 * b**2),
            "conditional_real_coordinate_variance_upper_without_pi_to_six": str(b**2 / 4),
        }
    if _global_sources() != before:
        raise ValueError("a global kernel source changed during bound verification")
    return result


@cache
def _unit_region_execution():
    # An explicit computational enclosure region, NOT a selected extension point.
    parameters = (Ball(Eisenstein(0), Rational(1), 80, 80),) * 2
    kernel = build_kernel(parameters)
    coordinates = (Eisenstein(1),) + (Eisenstein(0),) * 5344
    action = kernel.apply(coordinates, basis_digest=kernel.actual.form.basis_digest,
                          indices=kernel.actual.form.indices)
    return kernel, action


def kernel_record():
    """Revalidate sources around a complete immutable whole-region computation."""

    source_record = covariance.read_covariance()
    if (hashlib.sha256(covariance.completed._canonical(source_record)).hexdigest()
        != COVARIANCE_DIGEST):
        raise ValueError("the original complete covariance changed its trusted identity")
    before = covariance._parents(), _global_sources()
    kernel, action = _unit_region_execution()
    parameters = kernel.parameters
    global_estimates = global_kernel_bounds()
    if (covariance._parents(), _global_sources()) != before:
        raise ValueError("an original kernel source changed during packet construction")
    cover_weight = bounds.Interval(*(Rational(Fraction(v)) for v in source_record[
        "cover_weight_without_pi_cubed"]), 80)
    quotient_weight = bounds.Interval(*(Rational(Fraction(v)) for v in source_record[
        "quotient_weight_without_pi_cubed"]), 80)
    # Return every output enclosure. Full actions at other vectors or regions use
    # the same factorization; no 5345-square matrix or small substitute is asserted.
    return {
        "schema": "alternate-metric-trial-kernel-v1",
        "covariance_parent_digest": COVARIANCE_DIGEST,
        "prerequisite_digests": dict(PARENT_DIGESTS),
        "generation_and_lift_proof_sha256": dict(PARENT_PROOFS),
        "source_identity": before[0],
        "proof_sha256": hashlib.sha256(PROOF.read_bytes()).hexdigest(),
        "source_publication": "https://arxiv.org/pdf/1103.3041",
        "source_publication_equations": ["3.18", "3.19"],
        "section_basis_digest": kernel.actual.form.basis_digest,
        "section_count": 5345, "fiber_rank": 4,
        "fiber_basis_labels": list(kernel.actual.fiber_labels),
        "parameter_order": ["a0", "a1"],
        "parameter_regions": [bounds._ball_record(p) for p in parameters],
        "parameter_region_role": "computational full-polydisk enclosure only; no point selection",
        "bound_bits": 80, "uncertain_center_bits": 80,
        "kernel_rule": "Sdagger (S Sdagger)^-1 S; full original invariant section basis",
        "section_form": "explicit unit-H computational initializer; not a physical metric",
        "gram": covariance._matrix_record(kernel.gram),
        "structural_determinant_lower_bound": str(kernel.structural_lower),
        "admitted_real_determinant_interval": bounds._interval_record(kernel.denominator),
        "exact_arithmetic_denominator_scale": str(kernel.denominator.upper),
        "inverse_rule": "(adjugate/M)/(determinant/M); M=certified determinant upper bound",
        "inverse": covariance._matrix_record(kernel.inverse),
        "action_input": {"role": "computational section-coordinate witness only",
                         "nonzero_coordinates": [[0, ["1", "0"]]]},
        "complete_action": [bounds._ball_record(c) for c in action],
        "cover_weighted_complete_action_without_pi_cubed": [bounds._ball_record(
            c * covariance._interval_ball(cover_weight, center_bits=80)) for c in action],
        "quotient_weighted_complete_action_without_pi_cubed": [bounds._ball_record(
            c * covariance._interval_ball(quotient_weight, center_bits=80)) for c in action],
        "global_unit_kernel_bounds": global_estimates,
        "global_scope": "complete original quotient-generating alternate P1 family",
        "projection_rank": 4, "unweighted_operator_norm": "1",
        "unweighted_frobenius_squared": "4",
        "conditional_error_assumptions": ["fixed unit input",
            "fixed extension parameters independent of the sampling cloud", "independent draws",
            "unchanged ideal positive auxiliary law", "certified complete per-draw evaluation"],
        "error_probability_bound_rule": "4 B^2/(n epsilon^2) for each fixed a; pi^3 factored out",
        "all_original_columns_consumed": True, "all_original_action_coordinates_produced": True,
        "full_factorized_trial_kernel_available": True,
        "global_unit_kernel_integrand_bound_available": True,
        "line_metric_required_for_trial_kernel": False,
        "global_fiber_inverse_norm_bound_available": False,
        "nonunit_kernel_execution_available": False,
        "uniform_simultaneous_parameter_family_probability_bound_available": False,
        "extension_point_selected": False, "unit_form_is_physical_or_canonical": False,
        "new_geometric_domain_section_calculation_performed": False,
        "new_all_column_cochain_replay_performed": False,
        "independent_cloud_available": False, "practical_sample_cost_certified": False,
        "controlled_integral_available": False, "balanced_iteration_performed": False,
        "ricci_flat_or_hym_metric_available": False, "line_twist_removed": False,
        "harmonic_matter_or_higgs_metrics_available": False,
        "physical_yukawas_available": False, "common_stabilized_vacuum_available": False,
        "observations_used": False,
    }


def write_kernel(path=OUTPUT):
    record = kernel_record()
    record["artifact_digest"] = hashlib.sha256(covariance.completed._canonical(record)).hexdigest()
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(record, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)
    return record


def read_kernel(path=OUTPUT):
    """Recompute every original-basis action, denominator, global bound and scope."""

    record = json.loads(path.read_text(encoding="utf-8"))
    digest = record.pop("artifact_digest", None)
    if (digest != hashlib.sha256(covariance.completed._canonical(record)).hexdigest()
        or digest != hashlib.sha256(covariance.completed._canonical(kernel_record())).hexdigest()):
        raise ValueError("the complete trial kernel changed its source, action, bounds or scope")
    return record


if __name__ == "__main__":
    print(write_kernel()["artifact_digest"])
