"""Check predeclared independent-method case selection and frozen numerical policy.

Owns:
    Case boundaries and source/scope requirements without redoing native roots.

Depends on:
    The research independent-method checks and original population declaration.

Must not:
    Treat deterministic case selection as IID evidence or imply a global error bound.

Phase 0:
    Research comparison governance only.
"""

import pytest

from research.experiments.scientific_genesis import retained_numerical_checks as module


def test_independent_method_cases_cover_both_original_roles_without_the_postselected_spikes():
    assert module.CASES == (17, 101, 1819, 1980)
    assert all(i not in module.CASES for i in (526, 1360))
    assert sum(i < 1536 for i in module.CASES) == 2
    assert sum(i >= 1536 for i in module.CASES) == 2


@pytest.mark.parametrize("ordinal", (True, 0, 17.0, "17", 526, 1360))
def test_no_adaptive_replacement_or_numeric_aliases(ordinal):
    with pytest.raises(ValueError, match="predeclared"):
        module.output_path(ordinal)
