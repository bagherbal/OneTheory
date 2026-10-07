# `metric_sampling`

## Purpose

This experiment diagnoses the trial metric iteration's main anomaly without
changing any sample, weight, section or H factor. The retained-population H1
has full-population curvature residual `tau ≈ 796`, far above the proved
continuum bound `tau <= 9/2`.

`leverage.py` shows the anomaly is an **in-sample leverage effect**:

* **Exact identity.** For `T = sum_i (w_i/n) M_i^† M_i` and the project's update
  `H1 = c T^-1`, each training block `B_i = (w_i/n) M_i T^-1 M_i^†` satisfies
  `0 <= B_i <= I`, and `sum_i tr B_i = N`. With `N = 5345` sections and
  `n = 1536` rank-four training samples, the mean leverage is
  `5345/6144 = 87%` of its maximum. H1 pins the fiber metric at every training
  point near its sampled value and leaves its derivatives unconstrained.
* **Effective size.** The recorded training weights have effective size
  `(Σw)²/Σw² ≈ 1258`, below the invertibility threshold `⌈5345/4⌉ = 1337`.
* **Observed split.** The median H1 trace-free curvature is 1612 on training
  points against 7.6 on validation points, a ratio of 212. For H0 the ratio is
  1.02. Out of sample, H1 lowers `tau` from 1.02 to 0.39. Those validation
  points were inspected earlier, so this is evidence, not a blind test.

**Registered prediction** (content-addressed in
`data/generated/metric_sampling/leverage_diagnosis.json`): an H1 built by the
same law from the 8192-point training population (mean leverage
`5345/32768 ≈ 16%`) must have a training/validation median curvature ratio
below 10. A ratio of 10 or more refutes this explanation.

```bash
python -m research.experiments.metric_sampling.leverage
```

## Belongs here

Exact leverage and conditioning identities, effective-sample-size audits,
and registered predictions for the metric populations.

## Does not belong here

Rebuilt H factors, reweighted or dropped samples, ridge or pseudoinverse
repairs, or any claim of a Ricci-flat or HYM metric.

## Dependencies

Reads unchanged scientific-genesis artifacts. Production must not import it.

## Promotion condition

A diagnosis may inform production metric code only after the registered
prediction is tested on the fresh population and independently reviewed.
