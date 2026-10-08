"""Research namespace for sampling diagnostics of the trial metric iteration.

Owns:
    Exact leverage identities of the empirical inverse T-operator, effective
    sample sizes of the recorded weights, and registered predictions for
    future populations.

Depends on:
    Completed retained-population and sample-factor artifacts.

Must not:
    Change samples, weights, sections or H factors, certify a metric, or be
    imported by production.

Phase 0:
    Research diagnostics only; no Ricci-flat or HYM metric is supplied.
"""
