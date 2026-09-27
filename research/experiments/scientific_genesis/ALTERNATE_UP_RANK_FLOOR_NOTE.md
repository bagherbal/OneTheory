# Exact rank floor of the alternate up sector

On the frozen nonsplit `I6-ray-0-1` component, the two Wilson sectors
each have one `E` class and two lifted `F` classes. Exterior degree
forces the `E–E` entry to zero and makes every mixed entry independent
of the outer coordinates. The four already-computed common-cover
scalar residues are nonzero. Order rows as `E(0,0), F(0,0):0,
F(0,0):5` and columns as `E(1,0), F(1,0):0, F(1,0):5`.

In the declared ordered cup convention, the first row's `F` entries
are `B=(3/2, (-9-6ω)/14)`. Reversing the earlier `E(1,0)–F(0,0)`
contractions gives the first column's `F` entries
`C=(-3ω/2, (-3-9ω)/14)`. The matrix therefore has the form

```text
Y(a) = [ 0   B ]
       [ C   D(a) ],       D(a)=a0 D0+a1 D1.
```

`D0` and `D1` are **uncomputed**, not generic or fitted values. The
minor using the first `F` row and first `F` column is `-B0*C0=9ω/4`.
All four such mixed minors are nonzero in the saved exact bases. Thus
the holomorphic rank is at least two for every nonsplit point of the
frozen family, regardless of the unknown `F–F` block. In particular,
this family cannot have a rank-zero or rank-one up matrix at this
order. The determinant remains an unknown linear form in `(a0,a1)`;
rank three has **not** been established.

These are ordered, unnormalized *cover* residues. Their numerical
minor values change under basis and quotient-trace normalization,
but invertible changes preserve nonvanishing and rank. The underlying
Higgs cohomology class exists by the acyclic determinant filtration;
its full same-cone representative remains to be constructed. The
missing physical calculation is the parameter-linear `F–F` block,
followed by quotient normalization, metrics, and a stabilized vacuum.
