"""Guard the exact reverse central direct-trace research path.

Owns:
    Input-boundary checks for the unresolved direct scalar trace.

Depends on:
    The research-only reverse central matter-leg experiment.

Must not:
    Claim a computed Yukawa value from a partial or nonclosed trace.

Phase 0:
    Fast regression for fail-closed reverse parameter selection.
"""

import pytest

from research.experiments.scientific_genesis.mixed_schoen_reverse_central_matter_leg import (
    reverse_central_direct_trace,
)


@pytest.mark.parametrize("parameter_index", (-1, 6))
def test_direct_trace_rejects_unavailable_parameters(parameter_index: int) -> None:
    """No source reconstruction starts for an out-of-basis parameter."""

    with pytest.raises(ValueError, match="parameter index is unavailable"):
        reverse_central_direct_trace(parameter_index)
