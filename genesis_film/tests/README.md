# Film tests

These tests check the Genesis film's NumPy engine (`physics.py`, `cosmos.py`)
without Manim. They cover the formulas behind every drawn shape. They also
check the seams where one cosmic painter hands over to the next: those must
paint identical pixels, so the film has no jumps.

```bash
pytest genesis_film/tests
```

The repository's `tests/` tree guards the production engine and research
results. The film is presentation software, so its tests live here instead.
