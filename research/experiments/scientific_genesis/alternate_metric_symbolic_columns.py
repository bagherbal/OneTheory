"""Compile the original finite lifting functional over its exact coefficient ring.

Owns:
    Point-independent raw generator polynomials in explicit normalized charts,
    with original section ordering and separate constant/a0/a1 coefficients.

Depends on:
    Original finite-pole encoding, arrow columns, raw homotopy and deck columns,
    the certified finite series, exact Laurent/polynomial algebra and quotient frames.

Must not:
    Replace cochains or carrier data, select extension moduli, identify numerical
    stream digests across points, infer practical sampling or provide physical metrics.

Phase 0:
    Research coefficient-ring compilation; complete execution and convergence
    remain separate gates.
"""

import gzip
import hashlib
import json
from collections import defaultdict
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from tempfile import NamedTemporaryFile
from time import perf_counter

from onetheory.math.numbers import Eisenstein
from onetheory.math.polynomials import Polynomial
from onetheory.math.sheaves import LaurentPolynomial

from . import alternate_metric_bounded_matrix as archive
from . import alternate_metric_bounded_support as original
from . import uncertain_cover_frames as domains

VARIABLES = ("x0", "x1", "x2", "u0", "u1", "u2", "p0", "p1")
OUTPUT = domains.OUTPUT.with_name("alternate_metric_symbolic_columns.json")
MATRIX = OUTPUT.with_suffix(".polynomials.jsonl.gz")
PROOF = Path(__file__).with_name("ALTERNATE_METRIC_SYMBOLIC_COLUMNS_NOTE.md")


def _source_signature():
    return tuple(tuple(sorted(part.items())) for part in domains._parents())


def _generator_labels():
    first = original.fiber.lifts.first._context()[0].left.objects[:4]
    second = original.fiber.lifts.second._context()[0].left.objects[:5]
    if any(o.position != 0 for o in (*first, *second)):
        raise ValueError("the original nine-generator order changed")
    return tuple(f"V1:{o.name}" for o in first) + tuple(f"V2:{o.name}" for o in second)


def section_basis_identity():
    """Identify the ACTUAL original sections without any point or chart data.

    This records the same ordered cochain sources and certified universal lift,
    not an identification between unrelated spaces. Numerical stream hashes are
    deliberately absent. Fresh bytes are checked even when decoded inputs are cached.
    """

    lifts = original.fiber.lifts
    parents, streams, _ = lifts._inputs()
    archives = {}
    for name, path in (("first", lifts.first.OUTPUT), ("second", lifts.second.OUTPUT),
                       ("invariants", lifts.INVARIANTS), ("cone", lifts.second.CONE)):
        digest, record = original.fiber._verified_payload(path)
        if digest != parents[name]:
            raise ValueError("an original global section source changed")
        if name in ("first", "second"):
            archive_path = domains.ROOT / record["section_archive"]
            actual = archive._file_digest(archive_path)
            if actual != record["section_archive_sha256"]:
                raise ValueError("an original global section archive changed")
            archives[record["section_archive"]] = actual
    _, cone = original.fiber._verified_payload(lifts.second.CONE)
    certificate_path = lifts.OUTPUT.with_name("alternate_metric_lift_operator_certificate.json")
    certificate_digest, certificate = original.fiber._verified_payload(certificate_path)
    if (certificate_digest !=
        "6870cdf9bc875777e8ded58e6b434d865204b8aa9aa69c6194e5b5463d55eb82"
        or certificate["rank_four_section_basis_available"] is not True
        or certificate["full_universal_lift_formula_certified"] is not True):
        raise ValueError("the actual original universal section certificate changed")
    proof_path = PROOF.with_name("ALTERNATE_METRIC_LIFT_OPERATOR_CERTIFICATE_NOTE.md")
    if hashlib.sha256(proof_path.read_bytes()).hexdigest() != (
        "fd34381d477f91bcd912771dbefcc9b39f95c5499850e19b427b5673433e7820"
    ):
        raise ValueError("the actual original universal section proof changed")
    record = {"schema": "original-metric-section-basis-identity-v1",
              "source_artifact_digests": parents, "source_archive_sha256": archives,
              "universal_lift_certificate_digest": certificate_digest,
              "constituent_counts": [len(s) for s in streams],
              "section_count": sum(len(s) for s in streams),
              "twist_cover_degree": lifts.structural_certificate()["twist_cover_degree"],
              "parameter_ring": cone["parameter_ring"], "parameter_order": cone["parameters"],
              "basis_order": "original injected V1 then original universal outer-lifted V2",
              "numeric_point_or_chart_input": False}
    record["artifact_digest"] = hashlib.sha256(archive._canonical(record)).hexdigest()
    return record


def _zero():
    return LaurentPolynomial.zero(8, scalar_type=Eisenstein)


def _monomial(exponents, scalar=1):
    return LaurentPolynomial.monomial(exponents, scalar, scalar_type=Eisenstein)


def _bounded_polynomial_value(polynomial, coordinates):
    """Compose existing monomial bounds with exact coefficients, sharing powers.

    This uses the original per-coordinate bound policy and positive-power
    monomial cache. Correlations are not replaced by independence assumptions.
    """

    if polynomial.variable_count != len(coordinates):
        raise ValueError("original exact polynomial and coordinate dimensions must agree")
    result = coordinates[0]._coerce(0)
    for exponents, coefficient in polynomial.terms:
        result = result + original._monomial(coordinates, exponents) * coefficient
    return result


@dataclass(frozen=True, slots=True, init=False)
class PolynomialCoefficients:
    """Exact regular coefficients on ORIGINAL encoded pole labels.

    These are an internal linear representation, not newly asserted closed
    physical cochains. Laurent poles stay on the original basis labels.
    """

    terms: tuple

    def __init__(self, terms=()):
        values = {}
        for basis, coefficient in terms:
            if (not isinstance(basis, original.OuterCechBasis)
                or not isinstance(coefficient, LaurentPolynomial)
                or coefficient.variable_count != 8
                or coefficient.scalar_type is not Eisenstein):
                raise TypeError(
                    "original pole labels and the named exact coefficient ring required",
                )
            if any(e < 0 for m, _ in coefficient.terms for e in m):
                raise ValueError("symbolic regular coefficients cannot contain Laurent poles")
            values[basis] = values.get(basis, _zero()) + coefficient
        object.__setattr__(self, "terms", tuple((b, c) for b, c in sorted(values.items())
                                               if not c.is_zero()))

    def __add__(self, other):
        if not isinstance(other, PolynomialCoefficients):
            raise TypeError("the same original polynomial coefficient representation required")
        return PolynomialCoefficients(self.terms + other.terms)

    def scale(self, scalar):
        return PolynomialCoefficients(tuple((b, c.scale(scalar)) for b, c in self.terms))

    def is_zero(self):
        return not self.terms


def _linear_columns(cochain, columns):
    return PolynomialCoefficients(tuple((target, c.scale(scalar)) for b, c in cochain.terms
                                        for target, scalar in columns(b)))


def _homotopy(cochain):
    return _linear_columns(cochain, original._homotopy_column)


class _PolynomialPerturbation:
    """Extend the EXISTING original arrow unit columns over regular polynomials."""

    def __init__(self, compiler, power):
        self.compiler, self.power = compiler, power
        self.column_images = {}

    def perturbation(self, cochain):
        result = []
        for basis, coefficient in cochain.terms:
            if basis.u_monomial != (basis.component.ambient_degree[1], 0, 0):
                raise ValueError("an original pole label lost its dummy second-plane grading")
            if basis not in self.column_images:
                terms = []
                for b, residual_x, arrow_u, scalar in original.support._original_column_terms(
                    self.compiler.target, basis,
                ):
                    encoded, positive = original.support._x_pole_encoding(b, residual_x)
                    value = self.compiler.channel_monomial(self.power, positive, arrow_u, scalar)
                    terms.append((encoded, value))
                self.column_images[basis] = PolynomialCoefficients(tuple(terms))
            result.extend((b, coefficient * c) for b, c in self.column_images[basis].terms)
        return PolynomialCoefficients(tuple(result))


@dataclass(frozen=True, slots=True)
class CompiledColumn:
    """Original section coefficients before the point-dependent quotient projection."""

    basis_index: int
    chart: tuple
    source_signature: tuple
    constant_generators: tuple
    first_parameter_generators: tuple

    def __post_init__(self):
        if type(self.basis_index) is not int or not 0 <= self.basis_index < 5345:
            raise ValueError("an ORIGINAL compiled section index required")
        if (not isinstance(self.chart, tuple) or len(self.chart) != 3
            or any(type(i) is not int or not 0 <= i < n
                   for i, n in zip(self.chart, (3, 3, 2), strict=True))):
            raise ValueError("an explicit original compiled chart required")
        if (not isinstance(self.source_signature, tuple)
            or len(self.source_signature) != 2
            or any(not isinstance(part, tuple) or any(
                not isinstance(pair, tuple) or len(pair) != 2
                or any(not isinstance(value, str) for value in pair) for pair in part)
                for part in self.source_signature)
            or not isinstance(self.constant_generators, tuple)
            or len(self.constant_generators) != 9
            or not isinstance(self.first_parameter_generators, tuple)
            or len(self.first_parameter_generators) != 2
            or any(not isinstance(g, tuple) or len(g) != 4
                   for g in self.first_parameter_generators)):
            raise ValueError("immutable original nine-generator and two-parameter shapes required")
        pivots = (self.chart[0], 3 + self.chart[1], 6 + self.chart[2])
        for group in (self.constant_generators, *self.first_parameter_generators):
            for polynomial in group:
                if (not isinstance(polynomial, Polynomial)
                    or polynomial.variable_count != 8 or polynomial.scalar_type is not Eisenstein
                    or any(m[i] for m, _ in polynomial.terms for i in pivots)):
                    raise ValueError("exact polynomials in the explicit normalized chart required")

    def evaluate(self, frame, *, source_signature):
        if not isinstance(frame, original.bounded.BoundedFiberFrame):
            raise TypeError("an actual determinant-certified bounded quotient frame required")
        if frame.point.chart != self.chart or source_signature != self.source_signature:
            raise ValueError("symbolic columns require their original source identity and chart")
        coordinates = (*frame.point.x, *frame.point.u, *frame.point.p)
        def value(polynomial):
            return _bounded_polynomial_value(polynomial, coordinates)

        constant = original.bounded._columns((tuple(value(p) for p in self.constant_generators),))
        projected = original.bounded._multiply(frame.projections[0], constant)
        zeros = (frame.point.x[0]._coerce(0),) * 5
        corrections = tuple(original.bounded._add(
            original.bounded._multiply(frame.projections[0], original.bounded._columns((
                tuple(value(p) for p in polynomials) + zeros,
            ))), original.bounded._multiply(projection, constant),
        ) for polynomials, projection in zip(self.first_parameter_generators,
                                             frame.projections[1:], strict=True))
        return projected, *corrections


class SymbolicCompiler:
    """Compile every original index on demand, independently of any numerical point.

    A chart is explicit engineering input, not geometry selection. No numeric
    center or tolerance enters the exact compilation. Per-frame projections
    remain the original determinant-certified ones at evaluation time.
    """

    def __init__(self, chart):
        if (not isinstance(chart, tuple) or len(chart) != 3
            or any(type(i) is not int or not 0 <= i < n
                   for i, n in zip(chart, (3, 3, 2), strict=True))):
            raise ValueError("three explicit valid original chart pivots required")
        original.support.regular.regularity_premises()
        self.chart, self.cell = chart, tuple((i,) for i in chart)
        self.normalized_pivots = (chart[0], 3 + chart[1], 6 + chart[2])
        self.source_signature = _source_signature()
        self.target, actions, _ = original.fiber.lifts.first._context()
        if any(c.ambient_degree[0] < 0 for c in self.target.components.values()):
            raise ValueError("positive first-plane ambient grading required")
        self.action = actions[0]
        self.operators = tuple(_PolynomialPerturbation(self, power) for power in range(3))
        self.functional_values, self.unit_values, self.columns = {}, {}, {}
        self.series_depths = set()
        self.arrows = {}
        for power in range(3):
            for parameter, extension in enumerate(original.fiber.lifts._inputs()[2]):
                grouped = defaultdict(list)
                for b, c in extension.terms:
                    component = self.target.components[
                        b.component.left_index, 0, b.component.koszul_summand,
                    ]
                    label = component, b.x_monomial, b.p_monomial, b.cell
                    grouped[b.component.right_index, b.cell[2][-1]].append((label,
                        self.channel_monomial(power, (0, 0, 0), b.u_monomial, c)))
                self.arrows[power, parameter] = grouped

    def channel_monomial(self, power, x, u, scalar=1):
        if type(power) is not int or not 0 <= power <= 2:
            raise ValueError("an actual original Reynolds channel required")
        x, u, scalar = tuple(x), tuple(u), Eisenstein.coerce(scalar)
        if len(x) != 3 or len(u) != 3 or any(type(e) is not int or e < 0 for e in x + u):
            raise ValueError("only original regular coordinate powers may be compiled")
        for _ in range(power):
            unit, x = original._monomial_action(x, self.action.x_images)
            scalar *= unit
            unit, u = original._monomial_action(u, self.action.u_images)
            scalar *= unit
        return self._chart_monomial(x + u + (0, 0), scalar)

    def _chart_monomial(self, exponents, scalar=1):
        if len(exponents) != 8 or any(type(e) is not int for e in exponents):
            raise ValueError("eight actual integer powers in the named coordinate order required")
        if any(e < 0 and i not in self.normalized_pivots for i, e in enumerate(exponents)):
            raise ValueError("a Laurent pole escaped the explicitly normalized chart pivots")
        return _monomial(tuple(0 if i in self.normalized_pivots else e
                               for i, e in enumerate(exponents)), scalar)

    def _functional(self, power, basis):
        if (type(power) is not int or not 0 <= power <= 2
            or not isinstance(basis, original.OuterCechBasis) or basis.total_degree != 1):
            raise ValueError("an original degree-one unit and Reynolds channel required")
        component = basis.component
        if self.target.components.get((component.left_index, component.right_index,
                                       component.koszul_summand)) != component:
            raise ValueError("the pole unit belongs to an incompatible original target")
        key = power, basis
        if key in self.functional_values:
            return self.functional_values[key]
        unit = PolynomialCoefficients(((basis, _monomial((0,) * 8)),))
        primitive, depth = original.perturbed_homotopy(unit, self.operators[power],
                                                      homotopy=_homotopy)
        if depth > 5:
            raise ValueError("the original certified finite lifting bound was exceeded")
        self.series_depths.add(depth)
        corrected = PolynomialCoefficients(tuple((b, c.scale(Eisenstein(1) /
            original._artificial_deck_phase(b, power, self.action))) for b, c in primitive.terms))
        for _ in range(power):
            corrected = _linear_columns(corrected, original._deck_column)
        coordinates = [_zero()] * 4
        for b, c in corrected.terms:
            if (b.cell != self.cell or b.component.koszul_summand != "k0"
                or self.target.left.objects[b.component.left_index].position != 0):
                continue
            exponents = tuple(min(e, 0) for e in b.x_monomial) + (0, 0, 0) + b.p_monomial
            coordinates[b.component.left_index] += c * self._chart_monomial(exponents)
        result = tuple(c.scale(Eisenstein(-1) / 3) for c in coordinates)
        self.functional_values[key] = result
        return result

    def _unit_correction(self, power, parameter, key):
        cache_key = power, parameter, key
        if cache_key not in self.unit_values:
            index, x, p, chart = key
            terms = []
            for (component, ax, ap, cell), coefficient in self.arrows[
                power, parameter,
            ].get((index, chart), ()):
                b = original.OuterCechBasis(component,
                    tuple(a + b for a, b in zip(x, ax, strict=True)),
                    (component.ambient_degree[1], 0, 0),
                    tuple(a + b for a, b in zip(p, ap, strict=True)), cell)
                encoded, positive = original.support._x_pole_encoding(b)
                terms.append((encoded, coefficient * self.channel_monomial(
                    power, positive, (0, 0, 0),
                )))
            result = [_zero()] * 4
            for b, c in PolynomialCoefficients(tuple(terms)).terms:
                result = [left + right * c for left, right in zip(
                    result, self._functional(power, b), strict=True)]
            self.unit_values[cache_key] = tuple(result)
        return self.unit_values[cache_key]

    def _regular_polynomial(self, value):
        pivots = (self.chart[0], 3 + self.chart[1], 6 + self.chart[2])
        terms = tuple((tuple(0 if i in pivots else e for i, e in enumerate(m)), c)
                      for m, c in value.terms)
        result = LaurentPolynomial(terms, variable_count=8, scalar_type=Eisenstein)
        if any(e < 0 for m, _ in result.terms for e in m):
            raise ValueError("a Laurent pole escaped the explicitly normalized chart pivots")
        return Polynomial(result.terms, variable_count=8, scalar_type=Eisenstein)

    def compile_basis(self, index):
        if type(index) is not int or not 0 <= index < 5345:
            raise ValueError("an ORIGINAL basis index in range(5345) required")
        if index in self.columns:
            return self.columns[index]
        first = index < 2655
        streams = original.fiber.lifts._inputs()[1]
        record = streams[0 if first else 1][index if first else index - 2655]
        constant = [_zero()] * 9
        for obj, m, chart, pair in record["terms"]:
            if chart == self.chart[2]:
                constant[obj if first else 4 + obj] += self._chart_monomial(
                    tuple(m), Eisenstein(*pair),
                )
        corrections = []
        for parameter in range(2):
            value = [_zero()] * 4
            if not first:
                for power in range(3):
                    sources = {}
                    for obj, m, chart, pair in record["terms"]:
                        key = obj, tuple(m[:3]), tuple(m[6:]), chart
                        c = self.channel_monomial(power, (0, 0, 0), tuple(m[3:6]),
                                                  Eisenstein(*pair))
                        sources[key] = sources.get(key, _zero()) + c
                    for key, c in sources.items():
                        if not c.is_zero():
                            value = [a + b * c for a, b in zip(value,
                                self._unit_correction(power, parameter, key), strict=True)]
            corrections.append(tuple(self._regular_polynomial(p) for p in value))
        result = CompiledColumn(index, self.chart, self.source_signature,
            tuple(self._regular_polynomial(p) for p in constant), tuple(corrections))
        self.columns[index] = result
        return result

    def evaluate_basis(self, frame, index):
        before = _source_signature()
        if before != self.source_signature:
            raise ValueError("an original source changed after symbolic compilation")
        result = self.compile_basis(index).evaluate(frame, source_signature=before)
        if _source_signature() != before:
            raise ValueError("an original source changed during symbolic evaluation")
        return result


def column_record(column):
    """Serialize exact raw coefficients, never a point-dependent numeric matrix."""

    def polynomial_record(polynomial):
        return [[list(m), [str(c.a), str(c.b)]] for m, c in polynomial.terms]

    return {"basis_index": column.basis_index,
            "constant_generators": [polynomial_record(p) for p in column.constant_generators],
            "first_parameter_generators": [[polynomial_record(p) for p in group]
                                           for group in column.first_parameter_generators]}


def parse_column(record, *, index, chart, source_signature):
    """Independent exact parser validates shapes, normalization and original order."""

    if (not isinstance(record, dict) or type(record.get("basis_index")) is not int
        or record["basis_index"] != index
        or set(record) != {"basis_index", "constant_generators", "first_parameter_generators"}):
        raise ValueError("original complete symbolic column ordering and fields required")
    if (not isinstance(record["constant_generators"], list)
        or len(record["constant_generators"]) != 9
        or not isinstance(record["first_parameter_generators"], list)
        or len(record["first_parameter_generators"]) != 2
        or any(not isinstance(g, list) or len(g) != 4
               for g in record["first_parameter_generators"])):
        raise ValueError("the original raw generator and parameter shapes changed")

    def polynomial(raw):
        if not isinstance(raw, list):
            raise ValueError("a canonical exact polynomial term list required")
        terms = []
        for term in raw:
            if (not isinstance(term, list) or len(term) != 2
                or not isinstance(term[1], list) or len(term[1]) != 2
                or any(not isinstance(c, str) for c in term[1])):
                raise ValueError("explicit exact rational coefficient pairs required")
            terms.append((term[0], Eisenstein(*(Fraction(c) for c in term[1]))))
        return Polynomial(terms, variable_count=8, scalar_type=Eisenstein)

    column = CompiledColumn(index, chart, source_signature,
        tuple(polynomial(p) for p in record["constant_generators"]),
        tuple(tuple(polynomial(p) for p in g) for g in record["first_parameter_generators"]))
    if archive._canonical(column_record(column)) != archive._canonical(record):
        raise ValueError("symbolic columns must have canonical normalized exact coefficients")
    if index < 2655 and any(not p.is_zero() for g in column.first_parameter_generators for p in g):
        raise ValueError("injected original sections cannot acquire outer coefficients")
    unused = column.constant_generators[4:] if index < 2655 else column.constant_generators[:4]
    if any(not p.is_zero() for p in unused):
        raise ValueError("original constituent generators cannot be relabeled")
    return column


def verify_archive(path, *, chart, source_signature):
    """Parse every original polynomial column; no lifting construction is rerun."""

    digest, count, terms = hashlib.sha256(), 0, 0
    with gzip.open(path, "rb") as stream:
        for line in stream:
            raw = json.loads(line)
            column = parse_column(raw, index=count, chart=chart, source_signature=source_signature)
            if line != archive._canonical(raw) + b"\n":
                raise ValueError("symbolic stream encoding must be canonical")
            terms += sum(len(p.terms) for group in (column.constant_generators,
                *column.first_parameter_generators) for p in group)
            digest.update(line)
            count += 1
    if count != 5345:
        raise ValueError("complete compilation must contain all 5345 original section columns")
    return {"section_count": count, "polynomial_count": count * 17,
            "exact_polynomial_term_count": terms,
            "exact_polynomial_stream_sha256": digest.hexdigest()}


def write_complete_chart(*, progress=None):
    """Execute the complete original basis in the explicit first normalized chart."""

    compiler = SymbolicCompiler((0, 0, 0))
    before = compiler.source_signature
    start = perf_counter()
    with NamedTemporaryFile(dir=OUTPUT.parent, prefix=".symbolic_columns_", delete=False) as raw:
        temporary = Path(raw.name)
    try:
        with temporary.open("wb") as raw, gzip.GzipFile(filename="", mode="wb",
                                                       fileobj=raw, mtime=0) as stream:
            for index in range(5345):
                record = column_record(compiler.compile_basis(index))
                stream.write(archive._canonical(record) + b"\n")
                if progress is not None and (index % 250 == 0 or index == 5344):
                    progress({"last_original_index": index,
                              "functional_units": len(compiler.functional_values),
                              "unit_residual_keys": len(compiler.unit_values),
                              "elapsed_seconds": perf_counter() - start})
        verified = verify_archive(temporary, chart=compiler.chart, source_signature=before)
        if _source_signature() != before:
            raise ValueError("an original source changed during complete symbolic compilation")
        record = {"schema": "alternate-metric-symbolic-columns-v1",
            "original_source_signature": before,
            "variables": VARIABLES, "chart_pivots": compiler.chart,
            "proof_sha256": hashlib.sha256(PROOF.read_bytes()).hexdigest(),
            "original_constituent_counts": [2655, 2690],
            "raw_generator_order": _generator_labels(),
            "parameter_order": ["constant", "a0", "a1"],
            "matrix_archive": str(MATRIX.relative_to(domains.ROOT)),
            "matrix_archive_sha256": archive._file_digest(temporary),
            "matrix_archive_bytes": temporary.stat().st_size,
            **verified,
            "functional_unit_count": len(compiler.functional_values),
            "original_unit_residual_key_count": len(compiler.unit_values),
            "observed_series_depths": sorted(compiler.series_depths),
            "complete_original_basis_compiled": True,
            "numerical_point_used_for_compilation": False,
            "every_chart_compiled": False, "independent_all_column_cochain_replay": False,
            "practical_multi_point_throughput_certified": False,
            "independent_cloud_available": False, "controlled_integral_available": False,
            "ricci_flat_or_hym_metric_available": False, "physical_yukawas_available": False,
            "common_stabilized_vacuum_available": False, "extension_point_selected": False,
            "observations_used": False}
        record["artifact_digest"] = hashlib.sha256(archive._canonical(record)).hexdigest()
        archive._install_unchanged_or_new(temporary, MATRIX)
        with NamedTemporaryFile(dir=OUTPUT.parent, prefix=".symbolic_columns_meta_",
                                delete=False) as raw:
            metadata = Path(raw.name)
        try:
            metadata.write_text(json.dumps(record, sort_keys=True, indent=2) + "\n",
                                encoding="utf-8")
            archive._install_unchanged_or_new(metadata, OUTPUT)
        finally:
            metadata.unlink(missing_ok=True)
        return record
    finally:
        temporary.unlink(missing_ok=True)


def verify_completed_chart(*, expected_digest):
    """Validate trusted complete execution without repeating the exact compiler."""

    before = _source_signature()
    digest, record = original.fiber._verified_payload(OUTPUT)
    if digest != expected_digest:
        raise ValueError("the completed symbolic execution changed its trusted digest")
    required = {"schema": "alternate-metric-symbolic-columns-v1",
        "original_source_signature": before, "variables": VARIABLES, "chart_pivots": (0, 0, 0),
        "proof_sha256": hashlib.sha256(PROOF.read_bytes()).hexdigest(),
        "original_constituent_counts": [2655, 2690],
        "raw_generator_order": _generator_labels(),
        "parameter_order": ["constant", "a0", "a1"],
        "matrix_archive": str(MATRIX.relative_to(domains.ROOT)),
        "matrix_archive_sha256": archive._file_digest(MATRIX),
        "matrix_archive_bytes": MATRIX.stat().st_size,
        **verify_archive(MATRIX, chart=(0, 0, 0), source_signature=before),
        "complete_original_basis_compiled": True}
    for flag in ("numerical_point_used_for_compilation", "every_chart_compiled",
                 "independent_all_column_cochain_replay",
                 "practical_multi_point_throughput_certified",
                 "independent_cloud_available", "controlled_integral_available",
                 "ricci_flat_or_hym_metric_available", "physical_yukawas_available",
                 "common_stabilized_vacuum_available", "extension_point_selected",
                 "observations_used"):
        required[flag] = False
    archive._require_scope(record, required)
    if _source_signature() != before or archive._file_digest(MATRIX) != required[
        "matrix_archive_sha256"]:
        raise ValueError("an original source or polynomial stream changed during audit")
    return {"artifact_digest": digest, **record}


def read_completed_columns(*, expected_digest):
    """Load all exact original polynomials only after trusted execution validation."""

    metadata = verify_completed_chart(expected_digest=expected_digest)
    before = _source_signature()
    with gzip.open(MATRIX, "rb") as stream:
        result = tuple(parse_column(json.loads(line), index=index,
            chart=(0, 0, 0), source_signature=before) for index, line in enumerate(stream))
    if (len(result) != 5345 or _source_signature() != before
        or archive._file_digest(MATRIX) != metadata["matrix_archive_sha256"]):
        raise ValueError("an original symbolic source or complete stream changed while loading")
    return result


if __name__ == "__main__":
    print(write_complete_chart(progress=lambda r: print(json.dumps(r), flush=True))[
        "artifact_digest"], flush=True)
