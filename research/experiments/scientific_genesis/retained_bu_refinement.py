"""Compose retained Bu refinement with the native interval multiplication law.

Owns:
    Bu configuration construction, literal original receipt restoration and
    same-prefix continuation using the unchanged exact root certificates.

Depends on:
    The frozen retained-root family solver and existing native input, point-line,
    complete-root, ancestry and frame validators.

Must not:
    Change a root, scalar, chart or input policy, monkeypatch frozen modules,
    replace archived outcomes or accept Newton proposals without certificates.

Phase 0:
    Research execution repair only; no new geometry or physical result.
"""

from . import retained_root_refinement as original

draws, native = original.draws, original.native


def _configuration(address, policy, solver):
    """Use the exact native Bu base (-f * 2, g), with Ball on the left."""

    if address.choices()[0] != "Bu":
        raise ValueError("this construction owns only the Bu mixture component")
    source = draws._cell(address.second, policy.input).coordinates
    partner = native.BoundedLine(draws._cell(address.first, policy.input).coordinates,
                                 policy.first.pivot, policy.first.axes)
    cox = native.schoen_geometry().cover.cox
    f, g = (native.polynomial_value(p, source) for p in (cox.cubic_f, cox.cubic_g))
    cubic = native.actual_restriction(partner, (-f * 2, g), side=1)
    return native.PointLineConfiguration(source, 2, partner, solver(cubic))


def restore_draw(address, policy, history):
    """Reuse the original accelerator except its unsupported Bu scalar order."""

    if address.choices()[0] != "Bu":
        return original.restore_draw(address, policy, history)
    component, branch = address.choices()
    if (history.get("status") != "admitted"
            or history.get("root_parent_retained") is not False
            or history.get("address") != draws._address_record(address)
            or history.get("draw_policy") != draws._policy_record(policy)
            or history.get("component") != component
            or history.get("selected_branch") != list(branch)
            or len(history["all_root_families"]) != 1):
        raise ValueError("a matching original Bu first-admission receipt is required")
    configuration = _configuration(address, policy, lambda cubic: original.restore_family(
        cubic, history["all_root_families"][0], policy.root))
    return draws.CoupledDraw(address, policy, configuration, branch)


def refine_draw(parent, address, policy, *, max_steps):
    """Preserve the original ancestry and policy checks before Bu refinement."""

    if not isinstance(parent, draws.CoupledDraw):
        raise TypeError("an existing admitted native root parent is required")
    if not isinstance(address, draws.DrawAddress) or not address.extends(parent.address):
        raise ValueError("every captured input prefix must extend its retained parent")
    if address.choices()[0] != "Bu":
        return original.refine_draw(parent, address, policy, max_steps=max_steps)
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
    counts = []

    def solver(cubic):
        family, steps = original.refine_family(cubic, parent.configuration.partner,
                                             policy.root, max_steps=max_steps)
        counts.append(steps)
        return family

    try:
        configuration = _configuration(address, policy, solver)
        branch = draws._continued_branch(configuration, parent)
        return draws.CoupledDraw(address, policy, configuration, branch, parent), tuple(counts)
    except draws.PrefixExhausted as error:
        return draws.PendingDraw(address, policy, "prefix", str(error), parent), tuple(counts)
    except (ValueError, ZeroDivisionError, original.FailedConvergence) as error:
        pending = draws.PendingDraw(address, policy, "input/frame/root", str(error), parent)
        return pending, tuple(counts)
