"""Explain the H1 curvature anomaly as an in-sample leverage effect.

Owns:
    The exact leverage identity of the empirical inverse T-operator update,
    effective sample sizes of the recorded training weights, the in-sample
    versus out-of-sample split of the recorded H0/H1 curvature diagnostics,
    and a content-addressed falsifiable prediction for the next population.

Depends on:
    `full_trial_sample_factor.json` (training count, fiber rank, section count)
    and `retained_precise_population.json` (per-point weights, roles and
    curvature diagnostics), both unchanged.

Must not:
    Rebuild H1, drop or reweight samples, replace a failed sample, treat
    inspected validation as blind, or claim a Ricci-flat/HYM metric.

Phase 0:
    Research diagnosis; the identity is exact, the random-matrix inflation
    factors are heuristic and labelled as such.
"""

from __future__ import annotations

import hashlib
import json
import statistics
from dataclasses import asdict, dataclass
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
GENESIS = ROOT / "data/generated/scientific_genesis"
FACTOR = GENESIS / "full_trial_sample_factor.json"
POPULATION = GENESIS / "retained_precise_population.json"
EXPANDED = GENESIS / "expanded_trial_cloud_request.json"
OUTPUT = ROOT / "data/generated/metric_sampling/leverage_diagnosis.json"
WEIGHT = "omega_quotient_weight_without_pi_cubed_discovery"


@dataclass(frozen=True)
class LeverageDiagnosis:
    section_count: int
    fiber_rank: int
    training_count: int
    mean_leverage_fraction: str
    effective_training_size: float
    effective_ratio: float
    invertibility_threshold: int
    effective_size_below_threshold: bool
    h0_median_train: float
    h0_median_validation: float
    h1_median_train: float
    h1_median_validation: float
    h1_in_sample_ratio: float
    h0_in_sample_ratio: float
    h1_validation_tau: float
    h0_validation_tau: float
    next_training_count: int
    next_mean_leverage_fraction: str
    next_effective_gamma_estimate: float
    heuristic_inverse_inflation_now: float | None
    heuristic_inverse_inflation_next: float
    registered_prediction: str
    identity_status: str = "PROVED"
    random_matrix_status: str = "HEURISTIC"
    observations_used: bool = False


def mean_leverage_fraction(sections: int, rank: int, training: int) -> Fraction:
    """Exact average of tr(B_i)/rank over training points.

    With T = sum_i (w_i/n) M_i^dagger M_i invertible and
    B_i = (w_i/n) M_i T^-1 M_i^dagger, each B_i satisfies 0 <= B_i <= I
    (since T >= (w_i/n) M_i^dagger M_i) and sum_i tr(B_i) = tr(T^-1 T) = N.
    H1 = c T^-1 therefore pins M_i H1 M_i^dagger = c (n/w_i) B_i at training
    points while leaving its first jets unconstrained.
    """

    if rank * training < sections:
        raise ValueError("the training operator cannot be invertible")
    return Fraction(sections, rank * training)


def diagnose() -> LeverageDiagnosis:
    factor = json.loads(FACTOR.read_text())
    population = json.loads(POPULATION.read_text())
    sections, rank = factor["section_count"], factor["fiber_rank"]
    training = factor["training_count"]
    points = population["points"]
    train = [p for p in points if p["role"] == "training"]
    held = [p for p in points if p["role"] == "validation"]
    if len(train) != training or population["unresolved_ordinals"]:
        raise ValueError("the complete retained population does not match the factor")
    weights = [p[WEIGHT] for p in train]
    effective = sum(weights) ** 2 / sum(w * w for w in weights)
    threshold = -(-sections // rank)

    def median(rows: list[dict[str, object]], key: str) -> float:
        return statistics.median(row[key]["trace_free_l1"] for row in rows)  # type: ignore[index]

    h1_train, h1_held = median(train, "h1"), median(held, "h1")
    h0_train, h0_held = median(train, "h0"), median(held, "h0")
    request = json.loads(EXPANDED.read_text())
    next_training = int(request.get("training_count", 8192))
    ratio = effective / training
    gamma_now = sections / (rank * effective)
    gamma_next = sections / (rank * ratio * next_training)
    prediction = (
        f"For an H1 built by the same law from the {next_training}-point training "
        f"population (mean leverage {sections}/{rank * next_training}), the median "
        "trace-free curvature ratio training/validation must fall below 10 "
        f"(it is {h1_train / h1_held:.0f} now). A ratio of 10 or more refutes the "
        "leverage explanation of the H1 anomaly."
    )
    return LeverageDiagnosis(
        sections, rank, training, str(mean_leverage_fraction(sections, rank, training)),
        effective, ratio, threshold, effective < threshold,
        h0_train, h0_held, h1_train, h1_held, h1_train / h1_held, h0_train / h0_held,
        population["h1_role_tau_discovery"]["validation"],
        population["h0_role_tau_discovery"]["validation"],
        next_training, str(mean_leverage_fraction(sections, rank, next_training)),
        gamma_next,
        None if gamma_now >= 1 else 1 / (1 - gamma_now),
        1 / (1 - gamma_next),
        prediction,
    )


def write_artifact(path: Path = OUTPUT) -> dict[str, object]:
    record: dict[str, object] = {"schema": "metric-leverage-diagnosis-v1", **asdict(diagnose())}
    record["source_sha256"] = {
        str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in (FACTOR, POPULATION, EXPANDED)
    }
    payload = json.dumps(record, sort_keys=True, separators=(",", ":")).encode()
    record["artifact_digest"] = hashlib.sha256(payload).hexdigest()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return record


if __name__ == "__main__":
    print(write_artifact()["artifact_digest"])
