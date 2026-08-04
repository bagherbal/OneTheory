# OneTheory

OneTheory is a code-first scientific engine for building a computational model of reality from mathematically defined objects, verified physical laws, executable state transitions, and terminal observables. The paper and the current standalone verifier are migration sources; this repository is not organized by paper chapters.

Reality is assembled from lower verified components. Missing physics remains missing: an unresolved prerequisite must remain explicit and must never be replaced by a guessed coefficient, synthetic matrix, fallback value, or speculative bridge. In particular, no native-origin interpretation is allowed to masquerade as a connection to the heterotic carrier. Failed routes remain research results or killed hypotheses, not production domains.

Production code lives under `src/onetheory` and may be consumed by `research`; production never imports research. Exact mathematics is kept separate from controlled numerical work, and measured observables are terminal comparison and falsification data rather than geometry or vacuum selectors. The concrete current physical model is the published one-Higgs heterotic Schoen carrier. `reality.py` is the sole composition root and may report an incomplete model when required dependencies are unresolved.

Simulation consumes the same physical laws and immutable state objects as scientific computation. It will eventually emit structured trajectories for external animation consumers, without introducing a second simplified physics implementation or rendering dependency.

The current phase creates architecture only. No scientific calculation, promoted physical object, CLI, or placeholder API is included.

## Dependency direction

```text
core → math → physics → models
              ↘
                engine
models + engine → reality
production → verification
production → research
```

The final two arrows mean “inspected or consumed by,” not reverse imports: verification inspects production from outside, and research may consume production while production must not import research.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
pip install -e .
pytest
```

The original DOCX paper and standalone Python program remain unchanged at the repository root as migration sources.
