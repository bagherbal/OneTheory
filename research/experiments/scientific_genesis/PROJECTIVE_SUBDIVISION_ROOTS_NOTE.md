# Native projective root admission by explicit subdivision

## Claim and meaningful dependency

The simultaneous root proposer has bounded work and verified output, but no
global convergence proof for its declared seeds. The new method is selected
explicitly **instead of** that proposer. It does not catch its failure and
reseed it. It reuses the original `RootDisk`, `UniformRootDisk`, and
`CompleteUncertainRoots` certificates on the unchanged actual cubic pencils.

For a nonzero binary cubic with three simple projective roots, sufficiently
small coefficient cells and sufficiently fine positive target radii admit
three native uniform certificates in finite subdivision work. The stated
same-stream refinement schedule therefore eventually admits the root families
almost surely, conditional on the existing independent infinite fair input
streams. This supplies a constructive admission route, not a proof that the
old proposer converges or that all finite input cells are admissible.

## Covering, exclusion and admission

Use both caller-ordered parameter charts, not an automatically changed line
basis. The old single parameter-chart pivots are explicitly superseded by this
caller-declared two-chart atlas; the original ordered line axes are unchanged.
In either chart write z=a+b omega with real a,b and
omega=-1/2+i sqrt(3)/2. If |z|<=1, then |b|<=2/sqrt(3)<2 and
|a|<=1+1/sqrt(3)<2. Every projective point has |z|<=1 in at least one of
the two charts, including infinity as zero in the reciprocal chart. Thus
the two initial coefficient squares [-2,2]^2 cover the entire parameter P1.
A coefficient square of width h lies in the disk |z-c|<=h, by the triangle
inequality. Square boundaries are included; no boundary root is thrown away.

Let p be the exact center polynomial of one chart and t_k=p^(k)(c)/k!.
The existing integer-square-root routine supplies rational bounds L_k,U_k
for |t_k|. For coefficient disk errors e_j, set
E(R)=sum_j e_j (upper(|c|)+R)^j. All polynomials in the coefficient cell
differ from p by at most E(R) on |z-c|<=R, regardless of coefficient
correlations. If L_0>sum_(k>=1) U_k h^k+E(h), the whole square is zero-free
for every member. Otherwise it is retained for refinement or admission.

Admission at the **caller-declared fixed positive radius r** requires
L_1 r>U_0+sum_(k>=2) U_k r^k+E(r). The native uniform certificate implements
this strict inequality, so Rouche against t_1(z-c) gives one simple root
for every member. Even an exactly vanishing center residual keeps radius r:
a moving coefficient family must not become a false exact singleton root.
The method attempts admission only once h<r/8. Candidate failure is not a
returned root or an exclusion: that square continues in the queue.

Admitted disks must satisfy the existing strict projective disjointness test.
Three disjoint one-root disks exhaust homogeneous degree three for every
nonzero member, regardless of affine degree drops. An infinity branch is
covered by a positive reciprocal disk, not a dropped leading coefficient.

A square contained in a previously admitted disk needs no further proposal.
In the same chart, |c-d|+h<r suffices. In opposite charts, for |c|>h,

    |1-dc|+|d|h < r (|c|-h)

implies |1/z-d|<r throughout the square disk. Rational upper/lower modulus
bounds certify this implication. No approximate reciprocal center is used.
Finite work/depth exhaustion returns explicit failure; it is not zero-free.

## Eventual finite admission: deterministic argument

Fix a limiting simple binary cubic. Choose compact, disjoint neighborhoods
of its three roots in the above charts, and a positive minimum separation in
projective coordinates. At each root alpha, p'(alpha) is nonzero. Taylor
expansion in a fixed small neighborhood gives, with constants independent of
refinement,

    p(c)=p'(alpha)(c-alpha)+O(|c-alpha|^2),
    p'(c)=p'(alpha)+O(|c-alpha|).

Away from these neighborhoods, |p| has a positive minimum on the two compact
squares. Thus small coefficient errors and fine modulus bounds make every
sufficiently small outside square zero-free. Inside a root neighborhood the
above expansions show: if a square of width h<r/8 is not excluded, its center
is within h(1+o(1))+o(r) of the root when coefficient errors are o(r).
For sufficiently small r this is less than r/3. The linear Rouche margin
then exceeds, for example, |p'(alpha)|r/2 after all quadratic, coefficient,
and modulus errors. Such a square admits a uniform positive-radius disk.

All accepted centers are within r/3 of their unique limiting roots once
refinement is sufficiently fine. Disks at different roots are therefore
strictly projectively disjoint, and each accepted disk contains a root
neighborhood of radius at least r/2. Duplicates cannot be admitted as distinct
roots. At widths h=o(r), duplicate-root squares are either contained in the
existing disk or excluded. Hence breadth-first subdivision admits one disk
at each root in finite work. This argument uses uniform Taylor margins,
not convergence of a root iteration or an exhaustive grid of physical points.

For the explicit schedule at level j>=2 use:

    root radius         2^-j
    input cell bits     4j
    input bound bits    8j
    atan terms          4j
    trig Taylor terms   8j
    modulus bits        8j, plus current square depth
    maximum depth       4j
    maximum cells       2^(8j)

Keep the same line frames and extend all original exposed bit prefixes. At
level j this means exposing the first 4j bits of every spacing/phase stream,
the first three component bits, and up to 2j bits of each root-selector stream.
Stop reading a root selector at its first accepted pair; it then needs no
further bits. An all-11 selector must expose more of the **same** stream at
later levels. `refinement_address` implements these limits on caller-supplied
prefixes and fails rather than padding unavailable bits. Merely keeping a
fixed exhausted root-selector prefix forever is not the theorem schedule.
Off spacing boundaries, ties, and named-pivot zeros, the input maps and the actual pencil
restrictions are locally smooth, with bounded derivatives and denominators.
Their coefficient radii and center displacement are O(2^-4j). The alternating
atan remainder is O(5^-8j); the trigonometric factorial remainder decays faster
than 2^-4j; explicit dyadic rounding is O(2^-8j). Coefficient errors are thus
o(2^-j), as required. The root policy's old proposal mesh and iteration cap
are **unused** by this method, not quietly interpreted as subdivision work.

At depth 2j+C, widths and modulus errors are o(r), so the preceding margins
hold for all unhandled root neighborhoods; all other cells are excluded or
contained. The constant C depends on the fixed limiting cubic and frames,
not j. Even the deliberately pessimistic complete-tree count through this
depth is 2 sum_(k=0)^(2j+C) 4^k, which is eventually below 2^(8j); depth
2j+C is eventually below 4j. Thus the **actual declared caps**, not merely
an unspecified unlimited computation, eventually suffice. The caps are not
allocations and the executed adaptive queue need not visit the full tree.

## Almost-sure scope on the actual auxiliary configurations

The input parameter products of projective spaces are irreducible. Named
line-pivot zero sets, source-pencil base points, and binary-cubic discriminant
zeros are proper algebraic sets. The actual native certificates executed for
each A, Bx and Bu regression enclose three simple partner roots and provide
nonvanishing witnesses for the relevant discriminants. Both A restrictions
are checked. Therefore these discriminants are not identically zero on their
actual parameter domains. The uniform projective input law is absolutely
continuous with smooth volume, so these proper sets have probability zero.
Uniform spacing ties/endpoints also have probability zero. A ternary selector
requiring k consecutive rejected `11` pairs has probability 4^-k, tending to
zero. Its terminating digit is independent of its stopping length: the joint
probability of k rejected pairs then any specified accepted digit is 4^-(k+1),
the same for all three digits. Thus delays in selector exposure do not favor
a root label. This is a conditional law argument, not RNG certification.

Apply the deterministic result to the complement of these null sets.
Component and root selectors remain separate independent streams. The root
algorithm and its fixed schedule/order do not use the selected root digits
to choose a more favorable configuration. All three roots are certified before
one native branch is chosen. Consequently first admission preserves the
existing mixture law, conditional on the declared input assumption.

After first admission, disk order is not branch identity. The controller retains
the native parent and uses the existing projective-containment bijection before
selecting its continued branch. Any prefix replacement, line-frame change,
precision decrease or increased radius is rejected. Numerical failure retains
the most recent admitted parent through later attempts. This matching also
allows an explicitly requested method change for an **already admitted** parent,
but never silently treats the fresh method's first-admission index as that root.

The limiting root lies strictly inside its parent's certified projective disk.
As coefficient errors and r_j tend to zero, the corresponding new disk is
eventually strictly inside that parent disk (using the reciprocal chart when
needed). The finite root families therefore eventually have a unique containment
bijection. This proves eventual **same-root continuation**, not only new-root
admission. Three actual regression addresses execute the schedule at levels
8 then 12, with an intervening failed cell cap that retains the parent. Their
selected roots are continued by native containment, not by sorting indices.
Reusing the old literal regression addresses for separate first-admission
tests is not asserted to continue those earlier, differently ordered samples.
No independent cloud or complete frame/integrand controller is executed here.

## Independent attacks and remaining gates

Independent Fraction-pair Taylor expansion, exact known-root membership,
norm and projective separation inequalities check the actual certificates.
Tests include a moving infinity root, widely separated affine magnitudes,
repeated roots, unresolved clusters, finite caps, deficient prefixes and a
deliberately forbidden simultaneous proposer. Actual A/Bx/Bu executions keep
their source/base coupling and all 9/3/3 branches. The stored source/proof
hashes and native outputs are reconstructed by the trusted reader.

Original sources, physical carrier parameters and normalization are unchanged.
The method has no success-rate estimate or practical expected-work theorem.
It establishes a root-admission and continuation route, not complete
frame/integrand admission, independent entropy inputs,
controlled integration error, Ricci-flat/HYM convergence, matter metrics,
canonical Yukawas, a common vacuum or Genesis-to-UV derivation. Unresolved
finite-prefix requests must still be retained, never discarded or replaced.
