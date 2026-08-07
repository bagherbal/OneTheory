# External algebra reproduction

This directory contains the independent SageMath reproduction path for the
computable-carrier frontier. The script imports no OneTheory Python module. It
recomputes the I3/I6 baseline, both curvilinear Hilbert--Burch resolutions, all
six maximal-minor covers, graded Chern data, projective cocycles, and the dP9
deck atlas from plain Sage polynomial matrices.

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
