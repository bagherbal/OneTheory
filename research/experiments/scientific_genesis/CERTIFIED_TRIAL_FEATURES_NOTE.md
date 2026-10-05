# Integer enclosures for the full retained trial kernel

## Question and scope

The original independent trial cloud used all 5,345 sections, but did not bound
input-cell or binary64 errors. This experiment asks whether its unchanged full
operator can be enclosed without reconstructing the cochains or trusting
floating-point rounding. A positive result closes finite-cloud numerical error
control, not IID, practical statistical accuracy, HYM convergence, or a vacuum.
The parameters remain the explicitly selected computational point `(1, omega)`.
The unit-H form remains nonphysical; the covering degree remains nine and the
common pi-cubed factor remains explicitly omitted.

## Arithmetic proof

A disk stores integers `(x,y,r)` on the caller-declared mesh `M=2^b`, denoting
the complex center `(x+iy)/M` with circular radius `r/M`. Its center modulus
upper bound in mesh units is the integer ceiling of `sqrt(x*x+y*y)`, computed
with integer square root. No floating operation enters an enclosure.

Addition sums centers and radii exactly. Multiplication computes the Gaussian
center product as integers, then floors each coordinate back to the same mesh.
If a coordinate was displaced, the total displacement is less than `sqrt(2)/M`
and hence at most `2/M`; exact products add no displacement radius. If `u,v`
bound the old center moduli, the new radius in mesh units is at most
`ceil((u*r2+v*r1+r1*r2)/M)` plus that displacement allowance. These are ordinary
complex disk inclusion inequalities, not a hardware rounding assumption.

Rational inputs are embedded by exact fraction arithmetic. The embedding of
`a+b*omega` uses the exact real coordinate `a-b/2` and an integer-square-root
bracket for `sqrt(3)` in its imaginary coordinate. Its embedding error and
original circular radius are both included. Saved binary64 references are
interpreted as their exact dyadic rational values, including subnormals; they
are not treated as exact physical sections. Mesh incompatibility is rejected.

The complete original polynomial stream supplies every exact coefficient.
Compilation shares the same 83,523 monomials across 90,865 polynomials and
3,621,141 terms. Powers, monomials, all polynomial sums, original bounded
quotient projections, and the explicit two parameters are enclosed. There is
no selected-column approximation, numerical root, or generic physical matrix.

## Full-operator error theorem

Let `S` be the true four-by-N section evaluation at any actual point in the
retained certified cell. Let `Q` be the saved four-by-N numerical reference,
interpreted exactly as dyadic numbers, and `C` its saved lower-triangular row
preconditioner. Nonzero diagonal entries prove `C` invertible. It is a numerical
coordinate transformation, not physical field normalization. Put `A=C*S`.

Integer disk evaluation supplies uniform bounds

`||Q Q† - I4||_F <= rho`, and `||A-Q||_F <= epsilon`.

If `rho<1`, `Q` has rank four and its smallest singular value is at least
`sqrt(1-rho)`. The triangle inequality gives
`sigma_min(A) >= sqrt(1-rho)-epsilon`. An exact dyadic lower bound `s` for the
first square root is used. If `epsilon>=s`, this certificate remains unresolved;
that is neither a rank-deficiency theorem nor permission to replace a sample.

Otherwise let `P` and `R` be the orthogonal projectors onto the row spaces of
`A` and `Q`. For the column isometry `V=A†(A A†)^(-1/2)`,

`||(I-R)V||_F <= epsilon/(s-epsilon)`.

Indeed `(I-R)A†=(I-R)(A-Q)†`, since `(I-R)Q†=0`. Equal-rank orthogonal
projectors satisfy `||P-R||_F^2=2||(I-R)V||_F^2`. Finally
`||R-Q†Q||_F=||Q Q†-I4||_F<=rho`, by singular-value decomposition. Thus

`||P-Q†Q||_F <= sqrt(2)*epsilon/(s-epsilon)+rho`.

Because `C` is invertible, `P=S†(S S†)^(-1)S` is the original unit-H projector,
not a changed metric. Both square-root bounds are obtained by integer arithmetic.
The `rho` term is essential: the saved numerical Q is not exactly orthonormal.

For a certified true quotient weight `w` in `[L,U]` and exact dyadic saved
reference `w0>0`, the weighted error is bounded by

`w0*projector_error + 2*max(abs(w0-L), abs(w0-U))`.

Here the true rank-four projector has Frobenius norm two. Averaging these
bounds over **every** original sample bounds the entire finite-cloud operator,
including input-cell and reference arithmetic error, without a dense N-by-N
matrix. No admitted-subset mean is allowed when a sample lacks a certificate.

## Retention and limits

The original trusted receipts, sample archives, root families, chart, pivot
order, and all source signatures remain fixed. Original levels 12 and 16 are
replayed and checked against the archived frame. Any further refinement uses
the same captured streams and the existing certified containment controller.
The old reference kernel is retained rather than overwritten. Failures retain
their original identities and unresolved reason.

Initial testing on original sample 13 at level 16 did not resolve the
perturbation gate. This motivates finer same-sample cells, not resampling or
calling small orthogonality residuals an error certificate. Certification of
the finite cloud, even if successful, cannot invert its rank-at-most-64 sample
operator or make the very loose existing global statistical bound useful.
At least 1,337 samples remain necessary, not sufficient, for a full inverse
update. Physical matter/Higgs metrics and normalized Yukawas remain unavailable.
