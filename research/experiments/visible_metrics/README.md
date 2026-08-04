# Visible metrics experiment

This experiment audits the exact inputs needed to compile the positive-twist
section basis and open the numerical metric path for the published one-Higgs
Schoen carrier.

The `audit.py` module records the reusable production compiler, the frozen
carrier presentation, and each carrier artifact required after it. It stops at
the first absent physical input: the four non-split extension cocycles in one
common Čech basis. The generic multigraded section machinery belongs in
`src/onetheory/math/`; this directory may contain only reproducible audits,
input inventories, and narrowly scoped experiments.

No guessed extension, random section, sampled global-generation proof, fitted
metric, or observed quantity belongs here. Numerical benchmarks may be added
only as separate reproducible experiments and cannot certify the carrier.

This research area may depend on production math, model, engine, and
verification code. Production code must not import it. Promotion requires a
complete exact artifact, independent certificate, scientific review, and tests
in the real production domain.
