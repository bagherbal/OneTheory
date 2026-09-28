# Null-channel reduction of the alternate up determinant

On the frozen nonsplit alternate `P¹` carrier, the exact mixed cover
blocks in the declared ordered basis are

```text
B = (3/2, (-9-6ω)/14)
C = (-3ω/2, (-3-9ω)/14)^T.
```

Both first entries are nonzero. The strict second-constituent null
combinations are `seed5 - ρ seed0`, with `ρ=(2-ω)/7` in the left
character `(0,0)` and `ρ=(-3-2ω)/7` in the right character `(1,0)`.
These are the same exact ratios independently found in the reduced
Yoneda evaluations. Define `L=(-C1/C0,1)` and `R=(-B1/B0,1)`.

For the *unknown* parameter-linear second/second block
`D(a)=a0 D0+a1 D1`, a formal four-indeterminate determinant proves

```text
det [ 0   B ] = -B0*C0 * L^T D(a) R
    [ C   D ] = (9ω/4) * L^T D(a) R.
```

Thus **only two scalar coefficients**, `L^T D0 R` and `L^T D1 R`,
decide whether generic rank three is possible. Their values have not
been computed. The other six second/second entries may later be needed
for the complete matrix, but are not needed for this first rank test.

At the full common-cover cochain level, each null Yoneda combination
`h∘seed5 - ρ(h∘seed0)` contains 144 terms. Exact contraction solves
`D primitive = null evaluation` with a 90-term primitive in each
character sector. The content-addressed artifact records both
primitive digests and their exact identities. These homotopies make
the next null-to-null same-cone calculation concrete; they do **not**
by themselves supply the exterior Higgs correction or an F–F Yukawa
coefficient. All scalar values here are unnormalized cover values.

The direct-primitive shortcut fails an exact closure test, but its
defect is **not** evidence that syzygy truncation caused the failure.
Pairing with the A-line is the global Hilbert–Burch maximal-minor row:
it kills the two syzygies exactly, kills A itself, and kills all
constituent extension arrows because those land in A. The polynomial
map commutes with the Čech and Koszul differentials without minor
inversion. Its orientation agrees with all six local Plücker forms.

For `a0`, the cup `z=e0∪b_L` is a full degree-two cycle with 49,504
terms, including 2,560 syzygy terms. The certified A-line map evaluates
the full cochain, mapping those syzygies to zero. If `u_R` is the
90-term null primitive, then `d u_R=h∪b_R` is nonzero. The exact
25,780-term scalar therefore obeys the expected Leibniz identity

```text
d P_A(z,u_R) = P_A(z,d u_R).
```

Both sides have precisely the same 9,692 terms; there is no remainder.
This is a verified chain pairing, not a Yukawa coefficient. The
v2 screen in `alternate_up_null_shortcut_screen.py` supersedes the
earlier diagnostic that rejected syzygy inputs to the scoped helper.

The needed first-order scalar is the *complete* variation of
`ψ_L∧ψ_R∧H`. With `ψ_i=b_i+aν x_iν`, `H=h+aν kν`,
`d x_iν=-eν∪b_i`, and `d kν=-eν·h`, its coefficient is

```text
x_Lν∧b_R∧h + b_L∧x_Rν∧h + b_L∧b_R∧kν.
```

Only the sum is required to be closed. The known matter corrections
already supply the first two inputs; the determinant-line Higgs
correction remains missing. Changing a matter primitive by a closed
E-class in the same declared character sector changes this scalar
only by a mixed pairing,
which vanishes by the defining null condition. Changing a Higgs
primitive by a closed determinant-line class is cohomologically
irrelevant because that endpoint is acyclic. Thus the two determinant
coefficients are independent of these primitive choices, once the
full first-order product is constructed. Parameter-linearity makes
this first-order calculation sufficient for the universal rank test;
no extension point need be selected.
