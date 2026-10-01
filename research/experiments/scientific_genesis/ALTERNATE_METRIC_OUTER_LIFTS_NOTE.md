# Universal metric-section lifting formula

This construction is conditional on the frozen alternate heterotic carrier.
It retains both symbolic parameters `a0,a1`, the I6 ray `(0,1)`, the common
determinant repair `[1,2]`, and the declared twist `H=(14,16,1)`. It does not
choose a point of the extension space or replace the bundle by a direct sum.

## Why a finite homotopy suffices

Let `C` be the actual full standard-cover complex for `V1(H)` and write its
differential as `D=d+Delta`, where `d` is the structurally signed product
Čech differential. The existing ambient contraction satisfies
`d h+h d=1-i p`. Its reduced coordinates are the ambient line cohomology
of each actual object/Koszul summand, with the structural degree included.

The 24 component profiles give exactly these raw reduced dimensions:

```text
degree -3:   8,640
degree -2:  72,504
degree -1: 177,966
degree  0: 137,997
positive degrees: zero
```

These are not final cohomology dimensions. Incoming differentials and the
known higher transgression remain present; the argument uses only the absence
of degree-one coordinates. Independent binomial Künneth calculations check
every component rather than importing the final section count.

Assign object weights `A:2`, `F0:1`, `F1:0` and Koszul weights
`k0:2`, `k1:1`, `k2:0`. The raw homotopy preserves their sum, which lies
between zero and four. Each Hilbert--Burch or equation arrow raises it.
For every mixed extension term, the object gain minus its Koszul wedge
degree is strictly positive; this condition is checked against the complete
source term set, not inferred from its object direction alone.
Therefore `(h Delta)^5=0` on the entire target complex.

The [homological perturbation lemma](https://arxiv.org/abs/math/0403266)
then gives, in the repository's positive-contraction sign convention,

```text
h' = (1+h Delta)^(-1) h = sum(j=0..4) (-h Delta)^j h.
D h'+h' D = 1-i' p'.
```

Crainic's convention is `i p=1+d h_C+h_C d`; here `h=-h_C`, explaining
the minus signs in the finite expansion. The lemma supplies the general
operator identity, while the component profiles and actual arrow filtration
supply its carrier-specific hypotheses. Because the reduced degree-one
space is zero, `p' r=0` for any closed degree-one residual. Thus
`D h' r=r`; no large transferred linear solve or new coefficient choice is
required. This conclusion is stronger than four successful numerical-style
probes, but its implementation still deserves independent operator review.

## The actual universal section

For any saved V2 section `s`, use the saved strict outer cocycles `e0,e1`:

```text
r_i = e_i cup s
b_i = -Reynolds(h' r_i)
section(a0,a1) = (a0*b0+a1*b1, s).
```

The constructor checks `D r_i=0`, `D h' r_i=r_i`, and the final coefficient
identity `D b_i+r_i=0`. It also checks strict invariance. T is diagonal on
the actual monomials and objects, so it commutes with the ambient contraction;
the code checks T fixation before using the explicit normalized P average
`(1+P+P^2)/3`. There is no automatic substitute if that premise fails.

`universal_section(index)` constructs exact immutable block cochains for
every index in `range(5345)`. Indices below 2,655 inject the full certified
V1 basis. The remaining indices lift the complete 2,690-vector actual V2
basis. The H0 exact sequence and its vanishing H1 obstruction prove that
these blocks give the required basis mathematically. This is an executable
construction from explicit saved inputs, not 5,345 separately archived
expanded cochains. The two exact parameter coefficients are never combined
by selecting an extension coordinate.

## Verification boundary

The artifact records actual subline and nonsplit quotient probes, including
all four coefficient hashes, term counts, full differential identities, and
strict repaired actions. Tests reconstruct the outer products independently
by suffix-cell composition, without using the common cup implementation.
They independently recompute every ambient component and attack the mixed
Koszul contribution to the filtration bound.

Complete independent replay of all 2,690 universal lifts has **not** been
performed. The machine-readable scope keeps `rank_four_section_basis_available`
false until independent full-formula certification or complete coefficient
replay closes that gate. Neither existence of the constructor nor probe
agreement establishes a numerical metric. Local rank-four fiber evaluation,
Ricci-flat/HYM convergence, normalized Yukawas, a common stabilized vacuum,
the other flavor sectors, and Genesis-to-UV derivation remain unresolved.

Reproducer:

```bash
python -m research.experiments.scientific_genesis.alternate_metric_outer_lifts
```
