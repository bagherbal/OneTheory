# The scalar trace and its explicit finite-cover frame

The standard two-equation ambient cover computes H3(O) as a single
k2 H5 coordinate. Its monomial has all eight exponents -1 on the full
ordered product cell (012,012,01). The raw one-term harmonic seed is
not a full cycle: its hypersurface differential is nonzero. The finite
perturbed inclusion gives the actual 55-term closed representative
z, with inclusion depth three. Both its literal top coefficient and
its transferred coordinate are exactly one. This fixes a cover trace
frame, not a matter or Higgs metric.

## Descent of the class, not a strict cochain average

Apply the actual P and T coordinate actions, including Koszul units
and ordered-cell signs. Pz-z has 30 terms. Its declared 16-term
primitive has full differential exactly Pz-z; the homotopy depth is
two. Tz-z is identically zero. Thus both deck generators act trivially
on the one-dimensional H3(O). No averaging of z or of a physical
product is needed, and Pz=z is not falsely asserted at cochain level.

In characteristic zero, invariants for a finite group are exact.
For the stated free quotient pi:cover-to-quotient, finite pushforward
and descent therefore identify H3(O_quotient) with invariant cover
H3(O). In this case the entire one-dimensional cover group is invariant.
Every closed scalar class has a unique descended class, even when a
chosen cochain representative is not strictly deck fixed. This is not
an assertion that arbitrary matter or Higgs cochains descend.

## Why the factor is one ninth in this frame

Serre duality pairs H3(O_cover) with H0(K_cover). Specify Omega_cover
to be the form dual to z with trace_cover(z)=1. Its scale has now been
stated explicitly. Trivial action on H3(O_cover) implies trivial action
on its dual H0(K_cover); hence this form descends uniquely. Specify
Omega_quotient by

```text
pi*Omega_quotient = Omega_cover.
```

The covering degree is the published free quotient's order, nine. For
a finite etale map, the algebra trace satisfies Tr_pi(pi*f)=degree*f:
on a local split fiber multiplication by f is the diagonal operator
with the same scalar on every sheet. The dualizing-sheaf trace is the
same finite trace after the etale identification K_cover=pi*K_quotient.
Compatibility of Serre trace with finite pushforward thus gives, for
alpha in H3(O_quotient),

```text
trace_cover(pi*alpha) = degree * trace_quotient(alpha).
```

Let eta be the unique quotient class with pi*eta=z. In the explicitly
descended volume frame, trace_quotient(eta)=1/9. For any complete closed
scalar S with cover residue s, its quotient trace is consequently s/9.
This is a direct finite-cover law, not a fitted normalization or an
adapter between unrelated physical theories. Exact split-algebra tests
over Rational and Eisenstein coefficients reproduce the local degree
factor independently of a carrier coefficient.

Rescaling a volume form rescales its trace functional. The recorded
cover frame and pullback relation must accompany any use of this factor;
it is not permission to hide a form scale in an unrelated basis. In
particular it is not canonical normalization of four-dimensional matter,
Higgs fields, or masses. Those still require metrics and a common vacuum.

## Scope

`alternate_up_quotient_trace.json` records the actual generator, full
deck-boundary digests, covering degree, published input digest, and
volume-frame convention. Its producer reconstructs all small cochains
and verifies their full differential identities. Regression attacks
reject a nonfree quotient, a different order, a different covering degree,
or an undeclared group before writing an artifact.

This trace certificate assigns no null-channel coefficient, determinant,
complete matrix, extension point, or physical Yukawa. Such assignments
still require the canonical product, complete closed inputs, same-Higgs
identification, and all necessary matrix entries. The ongoing scalar
evaluation is not marked complete by this independent normalization check.
