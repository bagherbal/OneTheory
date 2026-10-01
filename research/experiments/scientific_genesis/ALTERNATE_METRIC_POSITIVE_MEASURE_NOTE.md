# A positive auxiliary law on the same actual cover

This changes an integration proposal, not the target residue volume or the
carrier. It neither selects a physical Kahler class nor supplies a Ricci-flat
metric. The previously established A/9 law and its divergent third moment
remain correctly scoped historical results. Here the proposal is instead
the cube of the positive ambient FS sum, with the same hyperplane-integral
one convention in every factor.

## Positivity and bounded weights

Put `beta = FS_x + FS_u + FS_p`, restricted to the actual smooth compact
complete intersection. The product ambient form is Kahler; the embedding
has injective tangent map, so beta is positive on every nonzero tangent
vector of X, including the critical curves where A vanishes. This is an
auxiliary integration convention. Equal FS coefficients are not inferred
physical moduli or an approximation to the physical metric.

The residue volume rho is smooth and nowhere zero, as established by the
actual critical-fiber calculation and adjunction. The ratio

```text
W_positive = (integral_cover beta^3) * rho / beta^3
```

is smooth and strictly positive everywhere. Compactness implies a finite
maximum. Thus all its nonnegative moments under the ideal law
`beta^3/integral beta^3` are finite. This proves existence, not a numerical
value, of a global weight bound. The same conclusion holds after division
by the declared free quotient degree for descended invariant integrands.

## Exact mass and mixture

On X write `A=FS_x FS_u FS_p`, `Bx=FS_x^2 FS_u`, and `Bu=FS_x FS_u^2`.
Forms commute since their real degree is even. The terms FS_x^3, FS_u^3,
and FS_p^2 vanish by ambient factor dimensions. FS_x^2 FS_p is pulled
back from the first equation surface in P2 x P1, which has complex
dimension two, so it vanishes as a differential form; FS_u^2 FS_p
vanishes in the same way on the second equation surface. This is a
pointwise argument, not an inference from vanishing integrals alone.
Therefore

```text
beta^3 = 6A + 3Bx + 3Bu.
```

The actual complete-intersection class is `(3Hx+Hp)(3Hu+Hp)`.
Extracting the Hx^2 Hu^2 Hp coefficient gives

```text
integral A = 9; integral Bx = integral Bu = 3;
integral beta^3 = 6*9 + 3*3 + 3*3 = 72.

beta^3/72 = (3/4)*(A/9) + (1/8)*(Bx/3) + (1/8)*(Bu/3).
```

These probabilities follow from exact intersection masses, not variance
fitting, observational inputs, or arbitrary texture coefficients.

## The component probability laws

Independent uniform projective hyperplanes have expected intersection
currents equal to products of the corresponding normalized FS forms.
The zero-current construction is described by
[Braun, Brelidze, Douglas, and Ovrut](https://arxiv.org/abs/0712.3563v2).
We fix its proportionality constants separately using the above masses.

For A/9, draw independent SU-uniform first-plane line, P1 point, and
second-plane line, and choose one of all nine transverse intersection
roots uniformly. For Bx/3, draw an SU-uniform first-plane point and an
independent second-plane line. Equivalently the first point is the
intersection of two independent uniform first-plane lines: uniqueness
of the invariant probability law on CP2 gives the FS_x^2 point law.
Each generic configuration has three roots, so choose one of all three
uniformly. For Bu/3 exchange the roles of the planes, retaining the
asymmetry of the actual equations, not assuming factor exchange is a
physical symmetry. Selecting one root per independent configuration
avoids treating correlated roots from one configuration as independent
Monte Carlo samples.

For the fixed input x, the actual first equation determines
`[mu:nu]=[-G(x):F(x)]`. For fixed u the second determines
`[mu:nu]=[-2F(u):G(u)]`. Common F=G=0 base points do not determine a
base parameter and are explicitly rejected by the algebraic constructor.
They form a measure-zero exceptional set for the ideal uniform law, as
do nontransverse partner line intersections. Exact rational regression
inputs and rounded proposals are not evidence that the ideal law has
been implemented. A future finite-precision generator must bound its
proposal error; simply rejecting difficult positive-probability numerical
events and resampling would bias the law.

## Local density conventions and checked enclosures

On an explicitly regular projection chart with free coordinates (s,r,t),
use the original tangent rows in ambient order (s,z,r,w,t). For plane
affine coordinates q and tangent matrix T, let

```text
S = 1 + q^dagger q;
G_FS*pi = (S*I - q*q^dagger)/S^2;
Q = sum_factors T^dagger (G_FS*pi) T.
```

Then `beta^3 = 6 det(Q) dLebesgue / pi^3`. The factor six is the wedge
factorial; it is not an extra mass correction. The unchanged residue
volume has density |h|^2 in the same coordinates. Cover weights are
`72*pi^3*|h|^2/(6 det Q)`; quotient weights divide separately by the
declared covering degree. Pi remains explicit and no physical volume
normalization is silently supplied.

Circular coefficient bounds propagate original root certificates through
the actual derivatives, tangent frames, FS pullbacks, and determinant.
Hermitian symmetry proves the determinant is real; its circular bound
therefore gives an outward real interval. An interval containing zero
fails rather than substituting a center or a fallback density. All nine
roots on each of the two existing regression configurations are checked,
including infinity. These probes are not draws from the new mixture.
The exact three-root branch probes also retain actual projective roots,
not approximate points admitted as cover points.

## Remaining gate

The bounded code currently uses the original regular projection charts.
Critical-fiber charts need their own coordinate construction even though
the global positivity proof includes those fibers. Numerical global
weight bounds, controlled uniform proposals, critical-chart enclosures,
practical complete-section throughput, finite-cloud integration errors,
Ricci-flat/HYM convergence, matter overlaps, and a common vacuum remain
open. The positive-law result does not close physical normalization or
the independent Genesis-to-UV gap.
