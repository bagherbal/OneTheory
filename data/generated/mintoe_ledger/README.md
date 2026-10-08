# MinTOE ledger artifacts

`ledger.json` is the content-addressed output of
`research/experiments/mintoe_ledger/ledger.py`. Its `registered_predictions`
block is dated and SHA-256 pinned, and must never be regenerated with
different values after a corresponding measurement appears. Observations are
used only for terminal comparison.
