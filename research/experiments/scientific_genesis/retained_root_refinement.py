"""Seed bounded exact root refinement from retained native certificates.

Owns:
    Literal restoration of subdivision root receipts and mesh-quantized Newton
    proposals for finer versions of the same captured auxiliary inputs.

Depends on:
    Existing actual cubic restrictions, exact Rouche witnesses, complete uniform
    root families, projective containment, and native named-frame admission.

Must not:
    Admit a Newton residual, reseed, change charts or streams, fall back to
    subdivision, replace a checkpoint, or infer global integration accuracy.

Phase 0:
    Research execution accelerator; no physical metric is supplied.
"""

from dataclasses import replace
from fractions import Fraction

from onetheory.core.errors import FailedConvergence
from onetheory.math.numbers import Eisenstein, Rational
from onetheory.math.polynomials import Polynomial

from . import native_section_continuation as continuation

draws, native = continuation.draws, continuation.native


def _configuration(address, policy, families):
    """Compose actual input restrictions with a caller-selected certified solver."""

    component, _ = address.choices()

    def line(input_address, frame):
        return native.BoundedLine(draws._cell(input_address, policy.input).coordinates,
                                  frame.pivot, frame.axes)

    if component == "A":
        first, second = line(address.first, policy.first), line(address.second, policy.second)
        base = draws._cell(address.base, policy.input).coordinates
        roots = tuple(families(native.actual_restriction(line_, base, side=side), index)
                      for index, (side, line_) in enumerate(((1, first), (2, second))))
        return native.LineBaseLineConfiguration(first, second, base, *roots)
    source, partner, frame, side = (
        (address.first, address.second, policy.second, 1) if component == "Bx" else
        (address.second, address.first, policy.first, 2)
    )
    source = draws._cell(source, policy.input).coordinates
    partner = line(partner, frame)
    cox = native.schoen_geometry().cover.cox
    f, g = (native.polynomial_value(p, source) for p in (cox.cubic_f, cox.cubic_g))
    base = (-g, f) if side == 1 else (-2*f, g)
    roots = families(native.actual_restriction(partner, base, side=3-side), 0)
    return native.PointLineConfiguration(source, side, partner, roots)


def _subdivision_depth(center):
    """Recover the dyadic square depth, not a guessed modulus precision.

    A depth-k midpoint of [-2,2]^2 has two odd numerators over 2^(k-1).
    The retained solver uses modulus_bits + k for its Taylor bounds.
    """

    depths = []
    for coordinate in (center.a, center.b):
        denominator = coordinate.denominator
        if (denominator < 2 or denominator & (denominator - 1)
                or coordinate.numerator % 2 == 0 or not -2 < coordinate < 2):
            raise ValueError("saved center is not a strict dyadic subdivision midpoint")
        depths.append(denominator.bit_length())
    if depths[0] != depths[1]:
        raise ValueError("saved subdivision midpoint coordinates have different depths")
    return depths[0]


def restore_family(cubic, record, policy):
    """Reprove the exact saved native certificates against the actual input cell."""

    disks = []
    for item in record["root_disks"]:
        center = Eisenstein(*(Rational(Fraction(value)) for value in item["center"]))
        if Rational(Fraction(item["radius"])) != policy.radius:
            raise ValueError("saved radius differs from the original declared radius")
        witness_policy = replace(policy, modulus_bits=policy.modulus_bits
                                 + _subdivision_depth(center))
        polynomial = Polynomial.from_coefficients(
            tuple(c.center for c in cubic.chart_coefficients(item["parameter_pivot"])),
            scalar_type=Eisenstein,
        )
        disks.append(native.UniformRootDisk(cubic, item["parameter_pivot"],
                     native._positive_witness(polynomial, center, witness_policy)))
    family = native.CompleteUncertainRoots(cubic, tuple(disks))
    if native._roots_record(family) != record:
        raise ValueError("saved native root receipt did not reproduce literally")
    return family


def restore_draw(address, policy, history):
    """Restore only a matching first-admission receipt; no roots are searched."""

    if (history.get("status") != "admitted" or history.get("root_parent_retained") is not False
            or history.get("address") != draws._address_record(address)
            or history.get("draw_policy") != draws._policy_record(policy)):
        raise ValueError("a matching original first-admission root receipt is required")
    records = history["all_root_families"]
    component, branch = address.choices()
    if (history.get("component") != component or history.get("selected_branch") != list(branch)
            or len(records) != (2 if component == "A" else 1)):
        raise ValueError("saved mixture component, root family count or branch changed")
    configuration = _configuration(address, policy,
        lambda cubic, index: restore_family(cubic, records[index], policy.root))
    return draws.CoupledDraw(address, policy, configuration, branch)


def refine_family(cubic, parent, policy, *, max_steps):
    """Use parent centers as proposals, accepting only existing exact certificates.

    max_steps is a separate explicit Newton cap; the old simultaneous-proposal
    iteration field is not reinterpreted. Every iterate is rounded in (1,omega)
    to the declared coefficient mesh. Failed certification consumes work, never
    changes the radius, chart, input or seed. No approximate root is exported.
    """

    if (not isinstance(cubic, native.UncertainCubic)
            or not isinstance(parent, native.CompleteUncertainRoots)
            or not isinstance(policy, native.roots.RootPolicy)):
        raise TypeError("actual cubic, complete parent and explicit root policy required")
    if type(max_steps) is not int or max_steps < 0:
        raise ValueError("Newton work cap must be a nonnegative integer")
    if policy.radius >= min(d.witness.radius for d in parent.disks):
        raise ValueError("same-root refinement requires a strictly smaller radius")
    disks, counts = [], []
    for old in parent.disks:
        coefficients = tuple(c.center for c in cubic.chart_coefficients(old.parameter_pivot))
        polynomial = Polynomial.from_coefficients(coefficients, scalar_type=Eisenstein)
        center = native.roots._quantize(old.witness.center, policy.coefficient_bits)
        for step in range(max_steps + 1):
            try:
                disk = native.UniformRootDisk(cubic, old.parameter_pivot,
                    native._positive_witness(polynomial, center, policy))
                if not draws._inside(disk, old):
                    raise ValueError("proposal lacks strict projective parent containment")
            except ValueError:
                disk = None
            if disk is not None:
                disks.append(disk)
                counts.append(step)
                break
            if step == max_steps:
                raise FailedConvergence("same-input Newton refinement exhausted its declared cap")
            # Horner evaluates the actual exact center polynomial and derivative.
            value, derivative = coefficients[-1], Eisenstein(0)
            for coefficient in reversed(coefficients[:-1]):
                derivative = derivative*center + value
                value = value*center + coefficient
            if derivative.is_zero():
                raise FailedConvergence("same-input Newton derivative vanishes exactly")
            center = native.roots._quantize(center - value/derivative, policy.coefficient_bits)
    family = native.CompleteUncertainRoots(cubic, tuple(disks))
    if draws._permutation(family, parent) != (0, 1, 2):
        raise ValueError("the complete refined family changed its retained ordering")
    return family, tuple(counts)


def refine_draw(parent, address, policy, *, max_steps):
    """Retain unresolved same-prefix work with its admitted native parent."""

    if not isinstance(parent, draws.CoupledDraw):
        raise TypeError("an existing admitted native root parent is required")
    if not isinstance(address, draws.DrawAddress) or not address.extends(parent.address):
        raise ValueError("every captured input prefix must extend its retained parent")
    if not isinstance(policy, draws.DrawPolicy):
        raise TypeError("an explicit native draw policy is required")
    if type(max_steps) is not int or max_steps < 0:
        raise ValueError("Newton work cap must be a nonnegative integer")
    old = parent.policy
    if ((policy.first, policy.second) != (old.first, old.second)
            or any(getattr(policy.input, key) < getattr(old.input, key)
                   for key in ("cell_bits", "bound_bits", "atan_terms", "taylor_terms"))
            or policy.root.coefficient_bits < old.root.coefficient_bits
            or policy.root.modulus_bits < old.root.modulus_bits
            or policy.root.radius >= old.root.radius):
        raise ValueError("keep named line frames and strictly refine declared input precision")
    c = parent.configuration
    families = ((c.first, c.second) if isinstance(c, native.LineBaseLineConfiguration)
                else (c.partner,))
    counts = []

    def solver(cubic, index):
        family, steps = refine_family(cubic, families[index], policy.root, max_steps=max_steps)
        counts.append(steps)
        return family

    try:
        configuration = _configuration(address, policy, solver)
        branch = draws._continued_branch(configuration, parent)
        return draws.CoupledDraw(address, policy, configuration, branch, parent), tuple(counts)
    except draws.PrefixExhausted as error:
        return draws.PendingDraw(address, policy, "prefix", str(error), parent), tuple(counts)
    except (ValueError, ZeroDivisionError, FailedConvergence) as error:
        pending = draws.PendingDraw(address, policy, "input/frame/root", str(error), parent)
        return pending, tuple(counts)
