# `mintoe_ledger`

## Purpose

An evidence ledger for the MinTOE/ASHA hierarchy formulas
(`epsilon^4 = (9/5)(14/431)/(8 pi)` and the formulas built on it). It treats
them as **serious hypotheses**, neither as derived results nor as retired
ideas. It separates what the data can support from what the formula
construction supplies.

`ledger.py` holds:

* **A faithful port.** It reproduces MinTOE's own build outputs to better
  than 1e-9.
* **Terminal comparison** against `data/observations/terminal_comparison_2024.json`.
  About 20 observables are within ~1σ. δ_CP(PMNS) = 270° is under pressure,
  although its likelihood is non-Gaussian and the alternative fit sits 58°
  away.
* **Precision audit.** m_τ reproduces the *superseded* average 1776.86 to
  7e-8 and is −0.8σ from today's 1776.93. v reproduces 246.2197 GeV to 7e-8
  using a rounded Planck mass that differs from CODATA by 1.3e-4. Integer
  coefficients on S and S² up to ~1/S ≈ 774 make the S-expansion a
  positional number system, so those digits carry no evidence without a
  derivation.
* **Cores.** These are the formulas without S corrections.
  `ln(MbarP/v) ≈ 12π − √3/2` (0.27% in v) and
  `ln(v/(√2 m_τ)) ≈ 4π/3 + 3/10 + 7/72` (0.13% in m_τ) have nominal post-hoc
  probabilities of 1.4% and 2.3%. They are interesting, but the menus were
  chosen after the data.
* **Koide–Brannen.** The measured Q − 2/3 = (−2.2 ± 5.1)e-6 and the phase
  δ − 2/9 = (2.5 ± 6.3)e-6. Anchored only on the measured m_τ, they predict
  m_e and m_μ within 0.6σ. This regularity is real, predates MinTOE, and is
  the strongest thread for a theory to explain.
* **Registered predictions.** These are hash-pinned and dated: δ_CP(PMNS),
  normal ordering with m1 = 0, Σm_ν, m_ββ, the PMNS angles, Δm², m_H, m_τ,
  the CKM angles, |V_ub| and J. Upcoming tests include JUNO (Δm², θ12),
  DUNE and Hyper-K (δ_CP), HL-LHC (m_H), LHCb (γ) and cosmology (Σm_ν).

```bash
python -m research.experiments.mintoe_ledger.ledger
```

## Belongs here

Ports, comparisons, look-elsewhere accounting and registered predictions.

## Does not belong here

Retuning a formula after a new measurement, inserting observations into any
construction, or presenting a pull table as a derivation.

## Dependencies

The observation manifest, for terminal comparison only. Production must not
import this directory.

## Promotion condition

A formula can inform theory work only through a derivation that fixes its
constants in advance; a registered prediction is never edited after a
measurement.
