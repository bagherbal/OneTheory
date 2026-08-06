# External algebra reproduction

This directory contains the independent SageMath reproduction path for the
computable-carrier frontier. The script imports no OneTheory Python module. It
recomputes the I3/I6 maximal minors and the exact block transition cocycle from
plain Sage polynomial matrices.

The pinned runtime is the Docker image `sagemath/sagemath:10.6`; the resolved
image digest and command output belong in the generated carrier artifact after
the image has run successfully. A missing container or a discrepancy is a
promotion failure, never an automatic fallback to the Python result.

Run from the repository root:

```bash
docker run --rm -v "$PWD:/workspace:ro" \
  --entrypoint bash sagemath/sagemath:10.6 -lc \
  'cp /workspace/research/experiments/computable_carrier/external/verify.sage /tmp/verify.sage && sage /tmp/verify.sage'

The copy into `/tmp` is required because Sage preparse writes a temporary
Python file beside its input script; the repository mount intentionally stays
read-only during independent verification.
```
