# Low-energy closure experiments

This directory contains unresolved carrier-specific investigations needed to
connect the Schoen effective-action boundary to a controlled low-energy
prediction.

Experiments may consume production mathematics and generic low-energy laws, but
they must not be imported by `src/onetheory`. A result may leave this directory
only after its inputs, provenance, independent certificate, leakage status, and
scientific review are recorded. The experiment must then become a thin
reproducer of the promoted production function rather than a second runtime
implementation.

Carrier-specific work belongs here when it concerns missing Kähler, gauge
kinetic, metric, instanton, threshold, hidden-sector, vacuum, or prediction
inputs. Synthetic algorithm tests belong under `tests/`; they are not evidence
for a physical carrier output.
