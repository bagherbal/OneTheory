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

The direct-primitive shortcut fails an exact closure test. For `a0`, the
cup of the outer extension with the left null matter class is a full
degree-two cycle with 49,504 terms. Its 2,560 syzygy terms lie outside
the existing A/F0-only determinant contraction. Discarding them leaves
a scalar cochain whose full differential is nonzero. Thus neither the
null primitive nor the truncated contraction defines a first-order
F–F coefficient. The reproducible screen is
`alternate_up_null_shortcut_screen.py`; a full same-cone exterior Higgs
chain map and syzygy-compatible contraction remain necessary.
