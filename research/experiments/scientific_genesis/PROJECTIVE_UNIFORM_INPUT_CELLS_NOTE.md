# Controlled projective input cells, not a cover sampling cloud

## Declared dependency

The existing positive-law-to-metrics edge requires controlled uniform projective
inputs. This experiment addresses precisely that prerequisite. Its outputs are
enclosures for input points or hyperplane covectors, **not** exact cover points,
intersection-root certificates, independent cover draws, or physical states.
The complete down/lepton replay remains the primary running calculation.

## Law and structural construction

For CP^n, n=1 or 2, take n independent uniform numbers U_i in [0,1), sort them,
and form their n+1 spacings W_j, including the endpoints zero and one. Take n
additional independent uniform phases V_j. Set

```
Z_0=sqrt(W_0), Z_j=sqrt(W_j)*exp(2*pi*i*V_j), j=1,...,n.
```

The ordered uniforms have constant density n! on the ordered simplex. The
spacing transformation has determinant one, hence W is Dirichlet(1,...,1).
Independent complex standard Gaussians have independent uniform phases and
independent exponential squared moduli. Changing their squared moduli to total
radius and normalized spacings gives density exp(-r)*r^n on r times constant
simplex density. Their direction is unitary invariant. Removing their common
phase therefore identifies the above projective law with normalized FS measure.
This gives the SU-uniform point law; the identical argument on dual coordinates
gives the hyperplane covector law. It is an auxiliary integration law, not a
quantum state ensemble used as physical input.

The unitary-invariant FS law is reviewed by
[Nechita and Pellegrini](https://arxiv.org/html/1201.5333). Its projective
hyperplane application is the zero-current integration construction in
[Braun et al.](https://arxiv.org/html/0712.3563v2). The spacing/Gaussian change
of variables above is the independent derivation used here.

## Finite input contract and errors

Every supplied integer k represents the **whole** dyadic cell
[k/2^q,(k+1)/2^q], never its midpoint alone. The integers are caller supplied;
the converter contains no random generator. The probability statement is
conditional on all 2n cell indices being independent uniform integers, or on
refinements of actual independent uniform bit streams. A fixed regression
tuple, seed, or pseudorandom generator does not prove that assumption.

Sorting is coordinatewise monotone, including repeated bins. Subtracting
successive sorted intervals with endpoint clipping encloses every spacing.
Integer square roots give outward rational square-root bounds. The alternating
atan series plus the exact identity pi=16 atan(1/5)-4 atan(1/239) bounds pi.
Finite sine/cosine Taylor polynomials have remainder at most
|theta|^(2N)/(2N)!. Their derivative bound one propagates both the phase-cell
width and the pi error. All work limits and bound precision are explicit.
No positive-probability cell is rejected because of tied bins or a zero weight.

Real/imaginary rectangular bounds are converted to the already established
Q(omega)-center circular representation. Since i=(1+2omega)/sqrt(3), an
outward interval for 1/sqrt(3) encloses the center conversion. A coordinate
disk's radius bounds its rectangle's L1 half-width plus this conversion error.
All disks enclose the *same coupled* unit representative, although they also
contain incompatible combinations. They must not be normalized independently.

If disk radii are r_j, the exact representative is within sum(r_j) of the
center vector in Euclidean norm. For two normalized representatives in the
same cell, their projective chordal distance sqrt(1-|v^dagger w|^2) is at most
2 sum(r_j). This bound
supports coupling error for Lipschitz functions on projective input space.
It is **not** a total-variation bound: the finite set of centers has total
variation distance one from the continuous FS law. Nor does it bound an
intersection integrand near a discriminant without additional analysis.

## Remaining edge

Uncertain input coefficients still need branch-complete certified intersection
roots and chart/frame bounds. Refining the original bit streams must retain
their probability law; rejecting difficult configurations and drawing others
would bias it. A selected root must be uniform among all roots of each fresh
configuration, with dependence of full root batches retained. Integrand bounds,
independent finite-cloud error control, practical section throughput, Ricci-flat
and HYM convergence, metrics, a common vacuum, and physical observables remain
unresolved. No production implementation is promoted by this experiment.
