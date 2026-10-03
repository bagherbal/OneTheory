"""Contract the complete original sections with explicitly supplied trial forms.

Owns:
    Positive exact LDL section inputs, complete streaming Hermitian coefficient
    contractions and unchanged weighted trial covariance on the original domain.

Depends on:
    The certified original bounded matrix, existing circular/norm arithmetic,
    positive auxiliary weights and explicit source, section and fiber bases.

Must not:
    Invent sections, hide a unit form, specialize complex parameters as real,
    drop uncertain zeros, infer a HYM kernel or report physical matter metrics.

Phase 0:
    Research trial covariance only; physical normalization remains unresolved.
"""

from __future__ import annotations

import gzip
import hashlib
import json
from dataclasses import dataclass
from fractions import Fraction
from functools import cache
from pathlib import Path

from onetheory.math.numbers import Eisenstein, Rational, coerce_rational

from . import alternate_metric_bounded_matrix as completed
from . import alternate_metric_positive_measure as positive
from . import uncertain_cover_frames as original_sources

Ball = completed.bounds.Ball
ROOT = completed.fiber.lifts.first.ROOT
OUTPUT = completed.OUTPUT.with_name("alternate_section_covariance.json")
PROOF = Path(__file__).with_name("ALTERNATE_SECTION_COVARIANCE_NOTE.md")
COMPLETED_DIGEST = "88cc1d553baa2a00a8f9c105d1ecab52d18d9c9a3e73042b617161253e09688a"


@dataclass(frozen=True, slots=True)
class SectionForm:
    """Caller-supplied H=L D L^dagger in an explicitly ordered original basis."""

    basis_digest: str
    indices: tuple[int, ...]
    diagonal: tuple[Rational, ...]
    lower: tuple[tuple[int, int, Eisenstein], ...]

    def __post_init__(self):
        indices = tuple(self.indices)
        diagonal = tuple(coerce_rational(d) for d in self.diagonal)
        if (not isinstance(self.basis_digest, str) or len(self.basis_digest) != 64
            or any(c not in "0123456789abcdef" for c in self.basis_digest)
            or not indices or any(type(i) is not int or i < 0 for i in indices)
            or len(set(indices)) != len(indices) or len(diagonal) != len(indices)
            or any(d <= 0 for d in diagonal)):
            raise ValueError(
                "an explicit source basis and strictly positive exact diagonal are required",
            )
        lower = []
        seen = set()
        for entry in self.lower:
            if len(entry) != 3:
                raise ValueError(
                    "each supplied lower entry needs two positions and one exact scalar",
                )
            i, j, scalar = entry
            if (type(i) is not int or type(j) is not int or not 0 <= j < i < len(indices)
                or (i, j) in seen):
                raise ValueError("distinct strict lower-triangular positional entries are required")
            seen.add((i, j))
            value = Eisenstein.coerce(scalar)
            if not value.is_zero():
                lower.append((i, j, value))
        object.__setattr__(self, "indices", indices)
        object.__setattr__(self, "diagonal", diagonal)
        object.__setattr__(self, "lower", tuple(sorted(lower)))


def _ball(record, *, bits, center_bits):
    return Ball(Eisenstein(*(Fraction(v) for v in record["center"])),
                Fraction(record["radius"]), bits, center_bits)


def decode_column(record, *, bits, center_bits):
    """Keep all twelve original coefficient bounds, including uncertain zeros."""

    completed._validate_column(record, record["basis_index"], bits)
    return record["basis_index"], tuple(tuple(_ball(row[0], bits=bits, center_bits=center_bits)
        for row in matrix) for matrix in record["coefficient_columns_constant_a0_a1"])


def _adjoint(matrix):
    return tuple(tuple(c.conjugate() for c in column) for column in zip(*matrix, strict=True))


def _interval_ball(interval, *, center_bits):
    return Ball(Eisenstein((interval.lower + interval.upper) / 2),
                (interval.upper - interval.lower) / 2, interval.bits, center_bits)


@dataclass(frozen=True, slots=True)
class Covariance:
    """All nine bounded coefficients of a complete trial covariance, not a metric."""

    form: SectionForm
    fiber_labels: tuple[str, ...]
    blocks: tuple
    bits: int
    center_bits: int
    consumed_indices: tuple[int, ...]

    def __post_init__(self):
        completed.bounds._bits(self.bits)
        completed.bounds._bits(self.center_bits)
        labels = tuple(self.fiber_labels)
        blocks = tuple(tuple(tuple(tuple(r) for r in matrix) for matrix in row)
                       for row in self.blocks)
        consumed = tuple(self.consumed_indices)
        if (not isinstance(self.form, SectionForm) or not labels
            or len(set(labels)) != len(labels)
            or any(not isinstance(s, str) or not s for s in labels)
            or any(type(i) is not int for i in consumed) or consumed != self.form.indices
            or len(blocks) != 3 or any(len(row) != 3 for row in blocks)):
            raise ValueError("all consumed original indices and explicit fiber labels are required")
        size = len(labels)
        for row in blocks:
            for matrix in row:
                if (len(matrix) != size or any(len(r) != size for r in matrix)
                    or any(not isinstance(c, Ball) or c.bits != self.bits
                           or c.center_bits != self.center_bits for r in matrix for c in r)):
                    raise ValueError(
                        "all nine bounded coefficient matrices must use the same basis",
                    )
        if any(blocks[n][m] != _adjoint(blocks[m][n])
               for m in range(3) for n in range(3)):
            raise ValueError("coefficient blocks must obey the exact Hermitian adjoint identities")
        object.__setattr__(self, "fiber_labels", labels)
        object.__setattr__(self, "blocks", blocks)
        object.__setattr__(self, "consumed_indices", consumed)

    def at(self, parameters):
        """Exact caller-supplied specialization for algebra checks, not vacuum selection."""

        parameters = tuple(Eisenstein.coerce(a) for a in parameters)
        if len(parameters) != 2:
            raise ValueError("explicit ordered complex a0 and a1 are required")
        eta = (Eisenstein(1), *parameters)
        zero = self.blocks[0][0][0][0]._coerce(0)
        size = len(self.fiber_labels)
        return tuple(tuple(sum((self.blocks[m][n][i][j] * eta[m] * eta[n].conjugate()
                               for m in range(3) for n in range(3)), zero)
                           for j in range(size)) for i in range(size))


def contract_columns(columns, form, *, basis_digest, fiber_labels, bits, center_bits):
    """Consume every declared column and every supplied LDL entry without defaults."""

    if not isinstance(form, SectionForm):
        raise TypeError("an explicit positive section input is required")
    if basis_digest != form.basis_digest:
        raise ValueError("the source column basis and supplied Hermitian input are incompatible")
    completed.bounds._bits(bits)
    completed.bounds._bits(center_bits)
    labels = tuple(fiber_labels)
    size = len(labels)
    if not size or len(set(labels)) != size or any(not isinstance(s, str) or not s for s in labels):
        raise ValueError("a nonempty ordered named fiber basis is required")
    zero = Ball(Eisenstein(0), Rational(0), bits, center_bits)
    accum = {(m, n): [[zero for _ in labels] for _ in labels]
             for m in range(3) for n in range(m, 3)}
    rows = {}
    release = list(range(len(form.indices)))
    for i, j, scalar in form.lower:
        rows.setdefault(i, []).append((j, scalar))
        release[j] = max(release[j], i)
    releases = {}
    for j, i in enumerate(release):
        releases.setdefault(i, []).append(j)
    active = {}
    consumed = []
    for position, (index, column) in enumerate(columns):
        if (position >= len(form.indices) or type(index) is not int
            or index != form.indices[position] or len(column) != 3
            or any(len(row) != size for row in column)
            or any(not isinstance(c, Ball) or c.bits != bits or c.center_bits != center_bits
                   for row in column for c in row)):
            raise ValueError("complete column ordering, precision and original basis must agree")
        consumed.append(index)
        active[position] = column
        for j, scalar in rows.get(position, ()):
            active[j] = tuple(tuple(a + b * scalar for a, b in zip(x, y, strict=True))
                              for x, y in zip(active[j], column, strict=True))
        for j in releases.get(position, ()):
            transformed = active.pop(j)
            d = form.diagonal[j]
            for (m, n), matrix in accum.items():
                for r in range(size):
                    for c in range(r if m == n else 0, size):
                        a, b = transformed[m][r], transformed[n][c]
                        if (a.radius == 0 and a.center.is_zero()) or (
                            b.radius == 0 and b.center.is_zero()
                        ):
                            continue
                        product = (_interval_ball(a.norm_interval(), center_bits=center_bits)
                                   if m == n and r == c else a * b.conjugate())
                        matrix[r][c] = matrix[r][c] + product * d
    if tuple(consumed) != form.indices or active:
        raise ValueError("the supplied original column stream is incomplete")
    blocks = [[None for _ in range(3)] for _ in range(3)]
    for (m, n), matrix in accum.items():
        if m == n:
            for i in range(size):
                for j in range(i):
                    matrix[i][j] = matrix[j][i].conjugate()
        value = tuple(tuple(row) for row in matrix)
        blocks[m][n] = value
        blocks[n][m] = _adjoint(value)
    return Covariance(form, labels, tuple(tuple(row) for row in blocks), bits,
                      center_bits, tuple(consumed))


def weighted_blocks(covariance, interval):
    """Multiply by the full positive weight enclosure, never its midpoint alone."""

    if (not isinstance(covariance, Covariance)
        or not isinstance(interval, completed.bounds.Interval)):
        raise TypeError("a complete covariance and a declared interval are required")
    if interval.bits != covariance.bits or interval.lower <= 0:
        raise ValueError("a compatible strictly positive auxiliary weight interval is required")
    weight = _interval_ball(interval, center_bits=covariance.center_bits)
    blocks = [[None for _ in range(3)] for _ in range(3)]
    for m in range(3):
        for n in range(m, 3):
            matrix = [[c * weight for c in row] for row in covariance.blocks[m][n]]
            if m == n:
                for i in range(len(matrix)):
                    for j in range(i):
                        matrix[i][j] = matrix[j][i].conjugate()
            value = tuple(tuple(row) for row in matrix)
            blocks[m][n], blocks[n][m] = value, _adjoint(value)
    return tuple(tuple(row) for row in blocks)


def _parents():
    # Reuse the existing fresh source/archive guard. Its immutable decoded
    # section cache cannot conceal a changed original cochain archive.
    source_identity = original_sources._parents()
    verified = completed.verify_completed_output(expected_digest=COMPLETED_DIGEST)
    _, record = completed.fiber._verified_payload(completed.OUTPUT)
    digest, positive_record = completed.fiber._verified_payload(positive.OUTPUT)
    if (digest != "c95486f83301f30fe55906ae773981d3a18d5662b56587de769f9744638cd66e"
        or hashlib.sha256((ROOT / positive_record["proof"]).read_bytes()).hexdigest()
        != positive_record["proof_sha256"]):
        raise ValueError("the established positive auxiliary law changed")
    return verified, record, digest, source_identity


def original_columns(*, bits, center_bits):
    """Decode all actual archived columns; verification belongs at both boundaries."""

    with gzip.open(completed.MATRIX, "rb") as stream:
        for line in stream:
            column = decode_column(json.loads(line), bits=bits, center_bits=center_bits)
            index, coefficients = column
            forbidden = ((*coefficients[0][2:], *coefficients[1], *coefficients[2])
                         if index < 2655 else
                         (*coefficients[0][:2], *coefficients[1][2:], *coefficients[2][2:]))
            if any(c.radius != 0 or not c.center.is_zero() for c in forbidden):
                raise ValueError("the original injected/lifted exact block-zero pattern changed")
            yield column


@cache
def declared_covariance():
    """Execute full original unit-H INITIALIZER; unit input is explicit, not physical."""

    verified, parent, _positive_digest, source_identity = _parents()
    form = SectionForm(verified["exact_column_stream_sha256"], tuple(range(5345)),
                       (Rational(1),) * 5345, ())
    result = contract_columns(original_columns(bits=80, center_bits=80), form,
        basis_digest=verified["exact_column_stream_sha256"],
        fiber_labels=tuple(parent["fiber_basis_labels"]), bits=80, center_bits=80)
    after = _parents()
    if after[0] != verified or after[3] != source_identity:
        raise ValueError("an original complete source archive changed during covariance assembly")
    return result


def _matrix_record(matrix):
    return [[{"center": [str(c.center.a), str(c.center.b)], "radius": str(c.radius)}
             for c in row] for row in matrix]


def unit_determinant_certificate(covariance):
    """Use original block structure, not chosen parameters, for a uniform denominator."""

    if (not isinstance(covariance, Covariance)
        or covariance.form.indices != tuple(range(5345))
        or covariance.form.lower or covariance.form.diagonal != (Rational(1),) * 5345
        or len(covariance.fiber_labels) != 4):
        raise ValueError("the complete original unit-H covariance is required for this certificate")
    for m in range(3):
        for n in range(3):
            for i in range(4):
                for j in range(4):
                    allowed = ((i < 2) == (j < 2) if m == n == 0 else
                               i >= 2 and j < 2 if m == 0 else
                               i < 2 and j >= 2 if n == 0 else i < 2 and j < 2)
                    c = covariance.blocks[m][n][i][j]
                    if not allowed and (c.radius != 0 or not c.center.is_zero()):
                        raise ValueError(
                            "the complete covariance lost its original exact block pattern",
                        )
    certificates = []
    for start in (0, 2):
        matrix = tuple(tuple(covariance.blocks[0][0][i][j] for j in range(start, start + 2))
                       for i in range(start, start + 2))
        first, determinant = matrix[0][0], completed.bounded._determinant(matrix)
        if not first.center.b.is_zero() or not determinant.center.b.is_zero():
            raise ValueError("the Hermitian principal minor enclosures must have real centers")
        diagonal = completed.bounds.Interval(first.center.a - first.radius,
                                             first.center.a + first.radius, covariance.bits)
        det_interval = completed.bounds.Interval(determinant.center.a - determinant.radius,
                                                determinant.center.a + determinant.radius,
                                                covariance.bits)
        if diagonal.lower <= 0 or det_interval.lower <= 0:
            raise ValueError("the actual constituent Gram enclosure is not certified positive")
        certificates.append({"fiber_labels": list(covariance.fiber_labels[start:start + 2]),
            "first_principal_minor": completed.bounds._interval_record(diagonal),
            "determinant": completed.bounds._interval_record(det_interval)})
    lower = Rational(Fraction(certificates[0]["determinant"][0])) * Rational(
        Fraction(certificates[1]["determinant"][0]))
    return {"scope": "unit H; original certified domain; every complex a0,a1",
        "constituent_positive_minor_bounds": certificates,
        "all_complex_parameter_determinant_lower_bound": str(lower),
        "argument": "positive Schur complement A+Z(I-Ydagger Dinv Y)Zdagger >= A",
        "extension_parameter_choice_used": False,
        "inverse_norm_uniformly_bounded_on_affine_parameter_space": False}


def covariance_record():
    """Revalidate source bytes around immutable full assembly and weight evaluation."""

    verified, parent, positive_digest, source_identity = _parents()
    covariance = declared_covariance()
    frame, root_digest = completed.declared_frame("finite_chart")
    chart = positive.measure.ProjectionChart(0, 2, 0, 2, 0)
    local = positive.bounded_positive_measure(frame.point, chart, volume_scale=Eisenstein(1),
                                              covering_degree=9, bits=80)
    cover = local["cover_weight_without_pi_cubed"]
    quotient = local["quotient_weight_without_pi_cubed"]
    after = _parents()
    if after[0] != verified or after[3] != source_identity:
        raise ValueError("an original source archive changed during weighted covariance assembly")
    return {"schema": "alternate-section-covariance-v1",
        "completed_matrix_parent_digest": verified["artifact_digest"],
        "complete_matrix_archive_sha256": verified["matrix_archive_sha256"],
        "exact_column_stream_sha256": verified["exact_column_stream_sha256"],
        "positive_law_parent_digest": positive_digest, "root_parent_digest": root_digest,
        "original_section_source_digests": source_identity[0],
        "original_section_archive_sha256": source_identity[1],
        "proof_sha256": hashlib.sha256(PROOF.read_bytes()).hexdigest(),
        "configuration_name": parent["configuration_name"], "root_pair": parent["root_pair"],
        "chart_pivots": parent["chart_pivots"], "fiber_basis_labels": list(covariance.fiber_labels),
        "section_count": len(covariance.form.indices), "consumed_indices": list(
            covariance.consumed_indices), "twist_cover_degree": [14, 16, 1],
        "common_flat_character_twist": [1, 2],
        "coefficient_labels": ["1", "a0", "a1"],
        "coefficient_rule": "sum eta_m conjugate(eta_n) G_mn; eta=(1,a0,a1)",
        "section_form": {"input_kind": "explicit computational unit-H initializer only",
            "basis_digest": covariance.form.basis_digest,
            "diagonal": [str(d) for d in covariance.form.diagonal], "strict_lower_entries": []},
        "bound_bits": 80, "uncertain_center_bits": 80,
        "unweighted_blocks": [[_matrix_record(matrix) for matrix in row]
                              for row in covariance.blocks],
        "unit_family_determinant_certificate": unit_determinant_certificate(covariance),
        "cover_weight_without_pi_cubed": completed.bounds._interval_record(cover),
        "quotient_weight_without_pi_cubed": completed.bounds._interval_record(quotient),
        "weighted_cover_blocks_without_pi_cubed": [[_matrix_record(matrix) for matrix in row]
            for row in weighted_blocks(covariance, cover)],
        "weighted_quotient_blocks_without_pi_cubed": [[_matrix_record(matrix) for matrix in row]
            for row in weighted_blocks(covariance, quotient)],
        "residue_scale": ["1", "0"], "covering_degree": 9,
        "all_original_columns_consumed": True,
        "general_exact_positive_ldl_inputs_supported": True,
        "single_regression_domain_only": True,
        "extension_parameters_specialized": False,
        "unit_form_is_physical_or_canonical": False,
        "uncertain_zeros_pruned": False,
        "new_section_calculation_or_all_cochain_replay_performed": False,
        "hym_inverse_kernel_available": False,
        "line_twist_removed": False,
        "independent_sampling_cloud_available": False,
        "global_integrand_bounds_available": False,
        "controlled_integral_available": False,
        "ricci_flat_or_hym_metric_available": False,
        "harmonic_matter_or_higgs_metrics_available": False,
        "physical_yukawas_available": False, "common_stabilized_vacuum_available": False,
        "observations_used": False}


def write_covariance(path=OUTPUT):
    record = covariance_record()
    record["artifact_digest"] = hashlib.sha256(completed._canonical(record)).hexdigest()
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(record, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)
    return record


def read_covariance(path=OUTPUT):
    """Recompute every complete block, declared input, weight, source hash and scope."""

    record = json.loads(path.read_text(encoding="utf-8"))
    digest = record.pop("artifact_digest", None)
    if (digest != hashlib.sha256(completed._canonical(record)).hexdigest()
        or digest != hashlib.sha256(completed._canonical(covariance_record())).hexdigest()):
        raise ValueError(
            "the complete section covariance changed its source, basis, bounds or scope",
        )
    return record


if __name__ == "__main__":
    print(write_covariance()["artifact_digest"])
