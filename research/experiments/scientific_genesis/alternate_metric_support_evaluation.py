"""Evaluate certified metric sections through finite first-plane pole sectors.

Owns:
    Exact point-functional compression retaining negative first-plane powers,
    specializing only regular coefficients, and reusing identical encoded
    residuals without replacing the actual universal section basis.

Depends on:
    The actual regular-u evaluator, original mixed perturbation and homotopy,
    explicit deck coordinate actions, and declared local quotient frames.

Must not:
    Evaluate a pole at zero, export an encoded cochain as a physical section,
    change a basis or extension point, infer metrics, or use observations.

Phase 0:
    Research-only finite-support compression; numerical sampling remains open.
"""

from dataclasses import dataclass, field

from onetheory.math.numbers import Eisenstein
from research.experiments.computable_carrier.schoen_serre_outer_transfer import (
    OuterCechBasis,
    SparseOuterCechCochain,
)
from research.experiments.computable_carrier.schoen_sparse_actions import _monomial_action

from . import alternate_metric_specialized_evaluation as regular
from .mixed_schoen_common_dga import perturbed_homotopy


def _positive(powers):
    return tuple(max(e, 0) for e in powers)


def _encode_x_term(basis, coefficient, x, powers=None):
    """Preserve poles; put artificial homogeneous degree at the first regular index."""

    powers = basis.x_monomial if powers is None else powers
    negative = tuple(min(e, 0) for e in powers)
    regular_indices = tuple(i for i, e in enumerate(powers) if e >= 0)
    if not regular_indices:
        raise ValueError("the actual positive-degree target must have a regular x coordinate")
    degree = basis.component.ambient_degree[0]
    dummy_degree = degree - sum(negative)
    if dummy_degree < 0:
        raise ValueError("the declared ambient degree cannot encode this pole sector")
    coefficient *= regular._monomial(x, _positive(powers))
    if coefficient.is_zero():
        return ()
    encoded = list(negative)
    encoded[regular_indices[0]] = dummy_degree
    return ((OuterCechBasis(
        basis.component, tuple(encoded), basis.u_monomial, basis.p_monomial, basis.cell,
    ), coefficient),)


def encode_x(cochain, x):
    """Apply a linear point-functional encoding, not Laurent specialization."""

    return SparseOuterCechCochain(tuple(
        term for basis, coefficient in cochain.terms
        for term in _encode_x_term(basis, coefficient, x)
    ))


@dataclass(slots=True)
class _SupportPerturbation:
    """Apply original polynomial arrows to encoded pole sectors exactly."""

    target: object
    x: tuple[Eisenstein, ...]
    u: tuple[Eisenstein, ...]
    column_images: dict = field(default_factory=dict)

    def perturbation(self, cochain):
        result = []
        for b, c in cochain.terms:
            if b.u_monomial != (b.component.ambient_degree[1], 0, 0):
                raise ValueError("an encoded coefficient lost its explicit u grading")
            if b not in self.column_images:
                self.column_images[b] = self._column(b)
            result.extend((target, c * coefficient)
                          for target, coefficient in self.column_images[b].terms)
        return SparseOuterCechCochain(tuple(result))

    def _column(self, source):
        """Compile one unit with the ORIGINAL operator; extend only by linearity."""

        dummy_x = _positive(source.x_monomial)
        source_u_degree = source.component.ambient_degree[1]
        image = self.target.perturbation(SparseOuterCechCochain(((source, Eisenstein(1)),)))
        result = []
        for b, c in image.terms:
            arrow_u = (b.u_monomial[0] - source_u_degree, *b.u_monomial[1:])
            c *= regular._monomial(self.u, arrow_u)
            if c.is_zero():
                continue
            encoded_u = OuterCechBasis(
                b.component, b.x_monomial, (sum(b.u_monomial), 0, 0),
                b.p_monomial, b.cell,
            )
            residual_x = tuple(a - d for a, d in zip(b.x_monomial, dummy_x, strict=True))
            result.extend(_encode_x_term(encoded_u, c, self.x, residual_x))
        return SparseOuterCechCochain(tuple(result))


class SupportEvaluator(regular.SpecializedEvaluator):
    """Evaluate the same basis using cached finite-pole residual classes."""

    def __init__(self, frame):
        super().__init__(frame)
        if any(c.ambient_degree[0] < 0 for c in self.target.components.values()):
            raise ValueError("positive first-plane ambient grading is required")
        self.x_channels = [frame.point.x]
        for _ in range(2):
            self.x_channels.append(regular._pullback_point(self.x_channels[-1], self.p.x_images))
        self.operators = [
            _SupportPerturbation(self.target, x, u)
            for x, u in zip(self.x_channels, self.u_channels, strict=True)
        ]
        self.residual_values = {}

    def _unit_correction(self, power, parameter, key):
        cache_key = power, parameter, key
        if cache_key in self.unit_values:
            return self.unit_values[cache_key]
        index, x, p, chart = key
        residual = []
        for (component, ax, ap, cell), c in self.arrows[power, parameter].get((index, chart), ()):
            b = OuterCechBasis(
                component, tuple(a + b for a, b in zip(x, ax, strict=True)),
                (component.ambient_degree[1], 0, 0),
                tuple(a + b for a, b in zip(p, ap, strict=True)), cell,
            )
            residual.extend(_encode_x_term(b, c, self.x_channels[power]))
        encoded = SparseOuterCechCochain(tuple(residual))
        residual_key = power, parameter, encoded
        if residual_key in self.residual_values:
            value = self.residual_values[residual_key]
        else:
            primitive, depth = perturbed_homotopy(encoded, self.operators[power])
            if depth > 5:
                raise ValueError("the actual finite-support filtration exceeded its bound")
            corrected = []
            for b, c in primitive.terms:
                # Only artificial positive powers have already been evaluated.
                # Preserve the actual deck phase of every retained Laurent pole.
                dummy_x, dummy_u = _positive(b.x_monomial), b.u_monomial
                scalar = Eisenstein(1)
                for _ in range(power):
                    unit, dummy_x = _monomial_action(dummy_x, self.p.x_images)
                    scalar *= unit
                    unit, dummy_u = _monomial_action(dummy_u, self.p.u_images)
                    scalar *= unit
                corrected.append((b, c / scalar))
            pulled = SparseOuterCechCochain(tuple(corrected))
            for _ in range(power):
                pulled = regular.fiber.lifts.first._action(pulled, 0)
            coordinates = [Eisenstein(0)] * 4
            for b, c in pulled.terms:
                if (b.cell != self.frame.point.cell or b.component.koszul_summand != "k0"
                    or self.target.left.objects[b.component.left_index].position != 0):
                    continue
                monomial = tuple(min(e, 0) for e in b.x_monomial) + (0, 0, 0) + b.p_monomial
                if monomial not in self.numerators:
                    self.numerators[monomial] = self.frame.point.monomial(monomial)
                obj = b.component.left_index
                coordinates[obj] += c * self.numerators[monomial] / self.line_frames[obj]
            value = self.projection.matmul(regular.fiber._columns((tuple(coordinates),))).scale(
                Eisenstein(-1) / 3,
            )
            self.residual_values[residual_key] = value
        self.unit_values[cache_key] = value
        return value
