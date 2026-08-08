# External algebra reproduction

This directory contains the independent SageMath reproduction path for the
computable-carrier frontier. The script imports no OneTheory Python module. It
recomputes the I3/I6 baseline, both curvilinear Hilbert--Burch resolutions, all
six maximal-minor covers, graded Chern data, projective cocycles, and the dP9
deck atlas from plain Sage polynomial matrices. It also reproduces the exact
rank-four determinant parity obstruction, the formal zero-index identity, and
the bounded lawful-twist counts for the current curvilinear Chern type. The
same script independently derives the complete target-line dimension
frontier and excludes index three across every curvilinear Chern type admitted
by the Tier B bound without assuming individual line descent.

For the invariant monomial frontier, Sage independently recomputes the three
Betti dimension functions, all 1,200 index-three topologies, and the 340 cases
whose constituent determinant classes descend. It separately constructs the
two explicit length-six Hilbert--Burch resolutions, derives their graded
quotient actions at every topology-relevant shift, and verifies that shifts
minus six and zero each have three common character rays. For all twelve
surviving rays it also checks the full three-chart maximal-minor cover, exact
graded projective cocycles, and the rank-two constituent inputs required for
descent. The external scope does not include action calculations for the
rejected length-three or length-nine resolutions, nor the unresolved rank-four
outer extension.

The pinned runtime is the Docker image `sagemath/sagemath:10.6`; the resolved
image digest and command output belong in the generated carrier artifact after
the image has run successfully. A missing container or a discrepancy is a
promotion failure, never an automatic fallback to the Python result.

Run from the repository root:

```bash
docker run --rm -v "$PWD:/workspace:ro" \
  --entrypoint bash sagemath/sagemath:10.6 -lc \
  'cp /workspace/research/experiments/computable_carrier/external/verify.sage /tmp/verify.sage && sage /tmp/verify.sage'
```

The copy into `/tmp` is required because Sage preparse writes a temporary
Python file beside its input script; the repository mount intentionally stays
read-only during independent verification.

The curvilinear descent result is conditional on the published free
order-nine Schoen quotient. The script verifies the exact equivariant sheaf
data to which finite free-quotient descent applies; it does not claim to
re-prove the published freeness theorem or select a physical constituent.
