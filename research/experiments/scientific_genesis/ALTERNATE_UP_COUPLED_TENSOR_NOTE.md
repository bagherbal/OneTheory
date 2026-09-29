# Coupled tensor comparison on the fixed ordered cover

This note concerns the actual rank-three pushout R and its coherent
quotient Q. It does not select an extension point, evaluate a scalar
pairing, or assign physical Yukawa entries. The actual-input gates below
are implemented in `alternate_up_coupled_tensor_comparison.py` and passed
for both coefficients; its writer refuses a certificate if either fails.

## The missing coherence is a fillable chain defect

Let Delta be the ordered product-cell Alexander--Whitney diagonal and H
the established chain homotopy of degree one with
`boundary H + H boundary = Delta - flip Delta`. Define the triple-output
chain operator

```text
J = (Delta tensor id) H
    - (id tensor H) Delta
    - flip_23 (H tensor id) Delta.
```

The tensor-operator sign in `id tensor H` and the graded output flip are
essential. Coassociativity of Delta gives
`boundary J + J boundary = 0`. J is nonzero on product cells: this is
the already-demonstrated failure of the strict first-slot Hirsch rule,
not a failure of the original commutator homotopy.

Each cell is a product of ordered simplices. Contract the triple output
chain to the triple of its first ordered carrier vertices. The tensor
contraction is the ordinary first-vertex cone in one factor, preceded
by vertex projections and followed by identities. Preceding positive
degrees are killed by those projections. No coefficient is fitted.

Define the degree-two chain operator recursively on cell dimension:

```text
K(c) = C(J(c) + K(boundary c)).
```

By induction the argument is a positive-degree cycle supported in c:
its boundary is `-J(boundary c) + J(boundary c) = 0`. The carrier
contraction fills this cycle exactly. Consequently

```text
boundary K - K boundary = J.
```

The construction is finite because faces have smaller dimension. It
retains the chosen ordering explicitly and only uses subcells of the
input carrier. An independent product-chain boundary implementation
verifies both identities on all 147 cells; the filler has positive
degree and no augmentation ambiguity in this construction.

Dualize minus K to obtain the scalar cochain operation T of degree -2.
With the full scalar differential, its identity is

```text
dT(a,b,c) - T(da,b,c)
    - (-1)^|a| T(a,db,c)
    - (-1)^(|a|+|b|) T(a,b,dc)
  = H(ab,c) - (-1)^|a| a H(b,c)
    - (-1)^(|b||c|) H(a,c)b.
```

Extending to the ambient Koszul complex uses the ordinary triple cup
crossing sign `Cech(a)*Koszul(b) + (Cech(a)+Cech(b))*Koszul(c)`.
T has even degree, so it introduces no extra total structural sign.
Full scalar regression tests include the hypersurface differential and
every ordered triple of Koszul subsets. Matrix and shifted-object
inputs are refused: T acts on explicitly extracted scalar coefficients.

## A two-row triangular complex

Declare distinct even objects A and B. Polynomial arrows are global
two-term-resolution maps and do not meet A or B. There are two mixed rows:
alpha into A, beta into B. No row leaves B; alpha does not leave A.
Beta may act on A. Check alpha as a closed degree-one Hom row against
the polynomial skeleton and beta against the complete inner complex.

The coefficients here are actual differential-action coefficients:
minus the stored coefficient for parent degree zero, unchanged for
parent degree one. Their scalar degrees are `1+p_j`. The row identities
are, schematically,

```text
d alpha_j = -sum_k alpha_k m_kj
d beta_j  = -beta_A alpha_j - sum_k beta_k m_kj
d beta_A  = 0.
```

Only terms permitted by degree are present. In particular, odd scalar
coefficients are not required to be individually closed.

The relation `A wedge B` is differential invariant: its only possible
new image is `B wedge B=0`. Kill this relation, not a fibrewise
subbundle assertion. This is the natural coherent pushout quotient.

Use the structural-first raw wedge W. For `a=|u|-p_i`, the additive
rank-one corrections N_alpha and N_beta each have coefficient
`(-1)^(a p_j) H(row_j,u_i) cup v_j` in `e_i wedge target`.
Their remaining Leibniz defect in `e_i wedge B` is exactly

```text
-(-1)^(p_i+a p_j) J_cochain(beta_A,alpha_j,u_i) cup v_j.
```

The extra term beta_A acting on the output of N_alpha and the beta
correction applied to an alpha input supply the two product terms of
this J; the beta row's differential supplies its first term.

Define M in that same slot with coefficient
`(-1)^(a p_j) T(beta_A,alpha_j,u_i) cup v_j`. Its full differential
cancels precisely the displayed defect. Polynomial syzygy terms
cancel by the closed row identities and strict naturality with global
polynomials. The remaining mixed outputs land in A wedge B, A wedge A,
or B wedge B and vanish in the declared quotient. Thus

```text
P_Q = W - N_alpha - N_beta + M
D_Q P_Q(u,v) = P_Q(D_R u,v) + (-1)^|u| P_Q(u,D_R v).
```

This is a structural statement for arbitrary homogeneous inputs,
not just selected closed matter. Degree-zero local products are the
ordinary wedge: the positive-cover homotopies vanish there.
An explicit mathematical noncycle pair makes the additive shortcut
fail by one term; M restores the full identity. Further attacks include
syzygies, odd diagonals, and gauges containing both Koszul equations.

## Actual presentation and the evaluation boundary

Construct R from the actual F and the fixed global map E-to-B1:
its outer row is the full `q_E(e_nu)` for each declared coefficient
nu=0,1. Retain k2 terms with the ordered subset `(1,2)`; they are not
single-equation terms. The first coefficient has 540 such terms.
The old zero/single-equation storage is therefore insufficient for R,
although it correctly represented the original constituent arrows.

The quotient has 38 objects. Its B-first pairs are the seven objects
of K=B1 tensor I6 B2; its remaining pairs are the 31 objects of exterior F.
The verifier compares every line and internal degree, all polynomial
arrows, the complete inner mixed block, and the entire normalized
connecting arrow with the existing quotient cone. It also checks
the full Leibniz identity using an actual strict syzygy primitive and
the actual right null matter cochain, without pretending the latter
is closed in R before its B component is supplied. The actual null
matter images have 21,756 and 20,301 terms; the two 47-term products
have full differentials with 1,479 and 1,307 terms respectively.
Both equal the complete sum of the differentiated-slot products.
The certificate digest is
`6f26314328265adfd2878100e70babdcfce78dfee0ce09304a9e4efd34a17626`.

The source sheaf morphism V-to-R is the fixed global polynomial map
q_E on E and identity on F. Its cone compatibility is the defining
equality `beta=q_E(e)`. This is a direct pushout, not an invented
identification between unrelated theories. The ordered-cover H and T
corrections supply the tensor coherence needed for its quotient product.

The next computation must evaluate this product on the **complete**
actual cone matter lifts and the existing quotient Higgs cocycle
`(h_K,kappa)`, then check trace and equivariance conventions. The earlier
closed ordered scalar screens are not silently reused as its entries.
Until that evaluation and identification are checked, no null-to-null
coefficient, complete matrix, physical rank, or normalized observable
is assigned. Canonical metrics and a common vacuum remain missing.
