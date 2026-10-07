# Original full-section connection curvature

This experiment consumes the frozen original 5345 sections, unchanged local
relations, fixed extension point `(1, omega)`, chart `(0,0,0)`, and ordered pivot
rows `(0,2)` / `(0,1,2)`. It never reconstructs sections, redraws roots, drops
points, clips weights, or replaces the failed normal-Gram inverse. The unit
section form is the original computational `H0`, not physical normalization.

## Analytic differentiation

The exact section archive has 17 polynomial channels per original column.
Shared monomials and their first derivatives are evaluated by the frozen CSR
instructions. Derivatives lower exponents before multiplication; no division by
coordinate values is used, so zero coordinates are treated correctly.

The actual original mixed differential/outer cup supplies a 9-by-5 relation
matrix `B`. In the declared pivot/free rows the quotient is
`Q = I_free - B_free B_pivot^-1 I_pivot`. Its derivative uses
`d(B_free B_pivot^-1) = (dB_free - B_free B_pivot^-1 dB_pivot) B_pivot^-1`.
Consequently `dS = dQ A + Q dA`. Freezing `Q` at its center would omit actual
connection terms and is not allowed. Implicit tangent directions differentiate
the same two cover equations, eliminating `x2,u2` in local order `x1,u1,p1`.

For `P = S H0 S^dagger`, `h=P^-1`, take the Chern curvature
`F=bar-partial(h^-1 partial h)`, ordered as `dz_i wedge dbar z_j`.
In a constant whitened frame at the evaluated center, `P=I` and
`F_(i,bar j)=R_i R_j^dagger`, where
`R_i=partial_i S (I-S^dagger S)`. This uses only first jets and rank-four
fiber operations, never a 5345-by-5345 projector. The pointwise frame change is
treated as constant when differentiating, not as a holomorphic function of the
center. All columns participate. The declared condition/Hermiticity guards are
discovery failure conditions, not exact rank proofs or error certificates.

## Explicit reference background and untwisting

The reference Kähler form is `14 FS_x + 16 FS_u + FS_p`, pulled back from the
actual ambient projective factors, with `integral_CP1 FS=1` and local coefficient
`1/(2*pi)`. It lies on the retained polarization ray, but is **not Ricci-flat**.
The metric array stores the Hermitian convention `v^dagger g v`. Contracting
curvature uses the corresponding explicit inverse-index convention.

Twisting changes only scalar curvature. Subtracting `trace(F)/4 I` therefore
removes the line contribution without a separate scalar balanced solve. This
does not select a determinant-volume trivialization or export a normalized
SU(4) fiber metric. See Anderson--Braun--Ovrut,
[arXiv:1103.3041](https://arxiv.org/abs/1103.3041), equations (3.17), (3.28)--(3.30).

## Whole-population empirical diagnostic

All 2048 original old-cloud checkpoints are read and source/identity validated;
their arithmetic centers, sample addresses, roles, branches, precision and frame
receipts are preserved. Centers are not relabelled as exact variety points.
The old hold-out points have already been inspected and are not blind here.
This experiment does not touch the fresh live 16384-point request or workers.

The sampler law stays unchanged. Reference-volume importance weights follow
`dVol_FS/dVol_Omega=8 det(g)/|residue|^2`; the inherited omitted `pi^3` is restored
explicitly. The quotient reference volume is the independently calculated
ambient intersection `J^3/(6*9)`. The empirical diagnostic is
`tau = mean(weight_FS * sum(abs(eigenvalues(trace-free Lambda F))))/(2*pi*4*Vol)`.
Training and old validation roles are also reported separately. No aggregate
exists if even one original point fails. Finite empirical means do not certify
numerical uncertainty, moment hypotheses, integration accuracy or convergence.

The calculation is a new **reference connection residual**, not another balance
operator witness. It creates no matter/Higgs metric, canonical Yukawa, physical
vacuum or final prediction. Its intended next use is comparison with the actual
full-section `H1` connection and background refinement, retaining every point.
