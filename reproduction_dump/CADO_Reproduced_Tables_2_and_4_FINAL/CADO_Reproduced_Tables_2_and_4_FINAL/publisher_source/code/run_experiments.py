from __future__ import annotations

import json
import math
import platform
import statistics
import sys
import time
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import wilcoxon

from generate_cado_architecture import save_architecture


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"
RESULTS.mkdir(parents=True, exist_ok=True)
FIGURES.mkdir(parents=True, exist_ok=True)

MASTER_SEED = 20260818
SIMULATED_DATA_ONLY = True  # Explicit boundary: no production or human-subject data are used.
N_SEEDS = 30
EVENTS_PER_EPISODE = 120
BOOTSTRAP_RESAMPLES = 10_000

# Fixed simulation-design parameters. These values are not fitted from
# operational telemetry; they define the released synthetic experiment.
MAX_ATTACK_STAGE = 3
RISK_WEIGHTS = {"confidence": 0.34, "severity": 0.27, "criticality": 0.22, "stage": 0.17}
CONSENSUS_THRESHOLDS = (0.30, 0.56, 0.81)
PROFILE_UPDATE_CONFIDENCE = 0.40
MIN_PROFILE_EVIDENCE = 6
OOD_DISTANCE_LIMIT = 2.20
ESCALATION_CONFIDENCE_MIN = 0.55
ONE_SIDED_95_Z = 1.645
UNCERTAINTY_COUNT_COEFFICIENT = 0.11
UNCERTAINTY_DISTANCE_COEFFICIENT = 0.025

SCENARIOS = {
    "office": {"criticality": 0.55, "capacity": 0.95, "attack_rate": 0.28},
    "research": {"criticality": 0.78, "capacity": 0.78, "attack_rate": 0.34},
    "data_service": {"criticality": 0.95, "capacity": 0.64, "attack_rate": 0.40},
}

ATTACKERS = {
    "credential": np.array([0.92, 0.28, 0.22, 0.58, 0.38]),
    "lateral": np.array([0.46, 0.94, 0.24, 0.72, 0.54]),
    "web": np.array([0.24, 0.18, 0.95, 0.42, 0.30]),
    "hybrid": np.array([0.66, 0.67, 0.62, 0.82, 0.66]),
}

OOD_ATTACKER = {"slow_blend": np.array([0.18, 0.78, 0.16, 0.99, 0.98])}
FEATURE_NAMES = ["credential", "lateral", "web", "patience", "stealth"]
POLICIES = ["Static", "Adaptive", "Consensus", "CADO"]
ABLATION_PRIMARY = ["CADO", "CADO-NoEvidence", "CADO-NoNoninferiority", "CADO-BoundedOnly"]
ABLATION_OOD = ["CADO", "CADO-NoOOD", "CADO-BoundedOnly"]
ACTION_LABELS = ["observe", "honeypoint", "honeyproxy", "honeytrace"]
ACTION_COST = np.array([0.005, 0.045, 0.115, 0.235])


@dataclass
class PolicyState:
    seen: int = 0
    qualified_seen: int = 0
    feature_sum: np.ndarray = field(default_factory=lambda: np.zeros(5, dtype=float))
    gate_reasons: Counter = field(default_factory=Counter)

    def update(self, event: dict) -> None:
        self.seen += 1
        # Policy state is updated only from observable alert fields. The
        # simulator's latent malicious/benign label is reserved for scoring.
        if event["confidence"] >= PROFILE_UPDATE_CONFIDENCE:
            self.qualified_seen += 1
            self.feature_sum += event["observed_features"]

    @property
    def profile(self) -> np.ndarray:
        if self.qualified_seen == 0:
            return np.full(5, 0.5)
        return self.feature_sum / self.qualified_seen


def derive_rng(*parts: object) -> np.random.Generator:
    token = "|".join(map(str, (MASTER_SEED, *parts)))
    value = 0
    for ch in token.encode("utf-8"):
        value = (value * 131 + ch) % (2**32 - 1)
    return np.random.default_rng(value)


def tactic_vector(tactic: str, patience: float, stealth: float) -> np.ndarray:
    base = {
        "credential": np.array([1.0, 0.15, 0.10, patience, stealth]),
        "lateral": np.array([0.25, 1.0, 0.10, patience, stealth]),
        "web": np.array([0.10, 0.10, 1.0, patience, stealth]),
    }[tactic]
    return base


def generate_episode(seed: int, scenario: str, attacker: str, ood: bool = False) -> list[dict]:
    rng = derive_rng("episode", seed, scenario, attacker, ood)
    sc = SCENARIOS[scenario]
    profile = (OOD_ATTACKER if ood else ATTACKERS)[attacker]
    tactic_weights = np.array(profile[:3], dtype=float)
    tactic_weights /= tactic_weights.sum()
    tactics = ["credential", "lateral", "web"]
    devices_by_tactic = {
        "credential": ["EDR", "IDS", "Firewall"],
        "lateral": ["IDS", "EDR", "Firewall"],
        "web": ["WAF", "IDS", "Firewall"],
    }
    formats = {"IDS": "syslog", "WAF": "cef", "EDR": "json", "Firewall": "kv"}
    events = []
    for idx in range(EVENTS_PER_EPISODE):
        malicious = bool(rng.random() < sc["attack_rate"])
        if malicious:
            tactic = str(rng.choice(tactics, p=tactic_weights))
            stage = int(np.clip(rng.poisson(1.5 + 1.2 * profile[3]), 0, MAX_ATTACK_STAGE))
            severity = float(np.clip(rng.beta(3.2 + stage, 1.8), 0.05, 0.995))
            confidence = float(np.clip(rng.beta(5.5 - 2.0 * profile[4], 1.5 + profile[4]), 0.05, 0.995))
            obs = tactic_vector(tactic, profile[3], profile[4]) + rng.normal(0, 0.12, 5)
        else:
            tactic = str(rng.choice(tactics))
            stage = 0
            severity = float(np.clip(rng.beta(1.4, 5.8), 0.01, 0.80))
            confidence = float(np.clip(rng.beta(1.3, 6.5), 0.01, 0.75))
            obs = np.clip(rng.normal([0.25, 0.22, 0.25, 0.45, 0.35], 0.15), 0, 1)
        obs = np.clip(obs, 0, 1)
        device = str(rng.choice(devices_by_tactic[tactic]))
        completeness = float(np.clip(1.0 - rng.beta(1.2, 13.0), 0.55, 1.0))
        risk = float(np.clip(
            RISK_WEIGHTS["confidence"] * confidence
            + RISK_WEIGHTS["severity"] * severity
            + RISK_WEIGHTS["criticality"] * sc["criticality"]
            + RISK_WEIGHTS["stage"] * (stage / MAX_ATTACK_STAGE),
            0,
            1,
        ))
        latent = 0.42 * severity + 0.23 * sc["criticality"] + 0.18 * profile[3] + 0.17 * profile[4]
        ideal = 1 if latent < 0.47 else 2 if latent < 0.72 else 3
        if not malicious:
            ideal = 0
        events.append({
            "event_id": idx,
            "malicious": malicious,
            "tactic": tactic,
            "stage": stage,
            "severity": severity,
            "confidence": confidence,
            "risk": risk,
            "criticality": sc["criticality"],
            "capacity": sc["capacity"],
            "device": device,
            "format": formats[device],
            "completeness": completeness,
            "observed_features": obs,
            "ideal": ideal,
            "capture_draw": float(rng.random()),
            "fault_draw": float(rng.random()),
        })
    return events


def consensus_action(event: dict) -> int:
    risk = event["risk"] * (0.88 + 0.12 * event["completeness"])
    if risk < CONSENSUS_THRESHOLDS[0]:
        return 0
    if risk < CONSENSUS_THRESHOLDS[1]:
        return 1
    if risk < CONSENSUS_THRESHOLDS[2]:
        return 2
    return 3


def adaptive_action(event: dict, state: PolicyState) -> int:
    profile = state.profile
    dominant = float(np.max(profile[:3]))
    context = 0.38 * event["risk"] + 0.20 * event["criticality"] + 0.18 * profile[3] + 0.14 * profile[4] + 0.10 * dominant
    # Sparse evidence makes unrestricted adaptation intentionally volatile.
    if state.qualified_seen < 5:
        context += float(derive_rng("early", event["event_id"], state.seen).normal(0, 0.17))
    return int(np.clip(np.digitize(context, [0.34, 0.58, 0.78]), 0, 3))


def static_action(event: dict) -> int:
    if event["confidence"] >= 0.80 and event["severity"] >= 0.72:
        return 3
    if event["confidence"] >= 0.62:
        return 2
    if event["confidence"] >= 0.40:
        return 1
    return 0


def nearest_profile_distance(profile: np.ndarray) -> float:
    centers = np.stack(list(ATTACKERS.values()))
    scale = np.array([0.23, 0.23, 0.23, 0.20, 0.20])
    distances = np.sqrt(np.sum(((centers - profile) / scale) ** 2, axis=1))
    return float(np.min(distances))


def internal_value(action: int, event: dict, profile: np.ndarray) -> float:
    latent = 0.42 * event["severity"] + 0.23 * event["criticality"] + 0.18 * profile[3] + 0.17 * profile[4]
    ideal = 1 if latent < 0.47 else 2 if latent < 0.72 else 3
    capture = [0.05, 0.51, 0.77, 0.91][action] * math.exp(-0.42 * abs(action - ideal)) * (0.86 + 0.14 * event["completeness"])
    cost = ACTION_COST[action] / event["capacity"]
    malicious_value = 0.34 + capture * 0.54 + (1 - capture) * 0.08 * action - 0.13 * max(0, ideal - action) - 0.075 * max(0, action - ideal) - cost
    benign_value = 0.82 - cost - [0.0, 0.045, 0.39, 0.64][action]
    p_malicious = float(np.clip((event["risk"] - 0.22) / 0.48, 0.02, 0.98))
    return p_malicious * malicious_value + (1 - p_malicious) * benign_value


def choose_action(policy: str, event: dict, state: PolicyState) -> tuple[int, str]:
    if policy == "Static":
        return static_action(event), "static"
    base = consensus_action(event)
    if policy == "Consensus":
        return base, "consensus"
    candidate = adaptive_action(event, state)
    if policy == "Adaptive":
        return candidate, "adaptive"

    # CADO and its ablations: optimize only within a one-step residual around the consensus action.
    skip_evidence = policy in {"CADO-NoEvidence", "CADO-BoundedOnly"}
    skip_ood = policy in {"CADO-NoOOD", "CADO-BoundedOnly"}
    skip_noninferiority = policy in {"CADO-NoNoninferiority", "CADO-BoundedOnly"}
    local_actions = list(range(max(0, base - 1), min(3, base + 1) + 1))
    candidate = max(local_actions, key=lambda action: internal_value(action, event, state.profile))
    if not skip_evidence and state.qualified_seen < MIN_PROFILE_EVIDENCE:
        state.gate_reasons["insufficient_evidence"] += 1
        return base, "insufficient_evidence"
    distance = nearest_profile_distance(state.profile)
    if not skip_ood and distance > OOD_DISTANCE_LIMIT:
        state.gate_reasons["ood_context"] += 1
        return base, "ood_context"
    if not skip_noninferiority and candidate > base and event["confidence"] < ESCALATION_CONFIDENCE_MIN:
        state.gate_reasons["noninferiority"] += 1
        return base, "noninferiority"
    gain = internal_value(candidate, event, state.profile) - internal_value(base, event, state.profile)
    uncertainty = (
        UNCERTAINTY_COUNT_COEFFICIENT / math.sqrt(max(state.qualified_seen, 1))
        + UNCERTAINTY_DISTANCE_COEFFICIENT * distance
    )
    if not skip_noninferiority and gain - ONE_SIDED_95_Z * uncertainty < 0.0:
        state.gate_reasons["noninferiority"] += 1
        return base, "noninferiority"
    state.gate_reasons["personalized"] += 1
    return candidate, "personalized"


def score_event(action: int, event: dict) -> dict:
    capacity_cost = float(ACTION_COST[action] / event["capacity"])
    if event["malicious"]:
        match = math.exp(-0.42 * abs(action - event["ideal"]))
        capture_prob = np.clip([0.05, 0.51, 0.77, 0.91][action] * match * (0.86 + 0.14 * event["completeness"]), 0, 0.98)
        captured = event["capture_draw"] < capture_prob
        under = 0.13 * max(0, event["ideal"] - action)
        over = 0.075 * max(0, action - event["ideal"])
        utility = 0.34 + (0.54 if captured else 0.08 * action) - under - over - capacity_cost
        unsafe = int(action == 3 and event["confidence"] < 0.42)
        redirected = int(action >= 2)
        correct_redirect = int(redirected and captured)
    else:
        captured = False
        redirected = int(action >= 2)
        correct_redirect = 0
        false_penalty = [0.0, 0.045, 0.39, 0.64][action]
        utility = 0.82 - capacity_cost - false_penalty
        unsafe = int(action >= 2)
    return {
        "utility": float(np.clip(utility, 0, 1)),
        "captured": int(captured),
        "redirected": redirected,
        "correct_redirect": correct_redirect,
        "unsafe": unsafe,
        "cost": capacity_cost,
        "engaged": int(event["malicious"] and action >= 1),
    }


def evaluate_episode(seed: int, scenario: str, attacker: str, policy: str, ood: bool = False) -> dict:
    events = generate_episode(seed, scenario, attacker, ood=ood)
    state = PolicyState()
    scores = []
    decision_times = []
    action_counts = Counter()
    for event in events:
        t0 = time.perf_counter_ns()
        action, source = choose_action(policy, event, state)
        decision_times.append((time.perf_counter_ns() - t0) / 1_000.0)
        action_counts[ACTION_LABELS[action]] += 1
        score = score_event(action, event)
        score["malicious"] = int(event["malicious"])
        score["action"] = action
        score["source"] = source
        scores.append(score)
        state.update(event)
    frame = pd.DataFrame(scores)
    redirections = int(frame["redirected"].sum())
    malicious = int(frame["malicious"].sum())
    benign = len(frame) - malicious
    return {
        "seed": seed,
        "scenario": scenario,
        "attacker": attacker,
        "ood": ood,
        "policy": policy,
        "events": len(frame),
        "malicious_events": malicious,
        "utility": frame["utility"].mean(),
        "redirection_precision": frame["correct_redirect"].sum() / max(redirections, 1),
        "engagement_rate": frame["engaged"].sum() / max(malicious, 1),
        "benign_false_redirect_rate": frame.loc[frame["malicious"] == 0, "redirected"].sum() / max(benign, 1),
        "unsafe_action_rate": frame["unsafe"].mean(),
        "normalized_cost": frame["cost"].mean(),
        "decision_latency_us_median": float(np.median(decision_times)),
        "decision_latency_us_p95": float(np.percentile(decision_times, 95)),
        "fallback_rate": 1.0 - state.gate_reasons["personalized"] / len(frame) if policy.startswith("CADO") else np.nan,
        "gate_insufficient": state.gate_reasons["insufficient_evidence"] / len(frame) if policy.startswith("CADO") else np.nan,
        "gate_ood": state.gate_reasons["ood_context"] / len(frame) if policy.startswith("CADO") else np.nan,
        "gate_noninferiority": state.gate_reasons["noninferiority"] / len(frame) if policy.startswith("CADO") else np.nan,
        "personalized_rate": state.gate_reasons["personalized"] / len(frame) if policy.startswith("CADO") else np.nan,
        **{f"action_{k}": v / len(frame) for k, v in action_counts.items()},
    }


def run_primary() -> pd.DataFrame:
    rows = []
    for seed in range(N_SEEDS):
        for scenario in SCENARIOS:
            for attacker in ATTACKERS:
                for policy in POLICIES:
                    rows.append(evaluate_episode(seed, scenario, attacker, policy, ood=False))
    frame = pd.DataFrame(rows)
    frame.to_csv(RESULTS / "primary_episode_metrics.csv", index=False)
    return frame


def run_ood() -> pd.DataFrame:
    rows = []
    for seed in range(N_SEEDS):
        for scenario in SCENARIOS:
            for policy in POLICIES:
                rows.append(evaluate_episode(seed, scenario, "slow_blend", policy, ood=True))
    frame = pd.DataFrame(rows)
    frame.to_csv(RESULTS / "ood_episode_metrics.csv", index=False)
    return frame


def run_ablation() -> pd.DataFrame:
    rows = []
    for seed in range(N_SEEDS):
        for scenario in SCENARIOS:
            for attacker in ATTACKERS:
                for policy in ABLATION_PRIMARY:
                    rows.append({"dataset": "primary", **evaluate_episode(seed, scenario, attacker, policy, ood=False)})
        for scenario in SCENARIOS:
            for policy in ABLATION_OOD:
                rows.append({"dataset": "ood", **evaluate_episode(seed, scenario, "slow_blend", policy, ood=True)})
    frame = pd.DataFrame(rows)
    frame.to_csv(RESULTS / "ablation_episode_metrics.csv", index=False)
    seed_summary = frame.groupby(["dataset", "seed", "policy"], as_index=False)[["utility", "redirection_precision", "benign_false_redirect_rate", "unsafe_action_rate", "fallback_rate"]].mean()
    seed_summary.to_csv(RESULTS / "ablation_seed_summary.csv", index=False)
    aggregate = seed_summary.groupby(["dataset", "policy"], as_index=False)[["utility", "redirection_precision", "benign_false_redirect_rate", "unsafe_action_rate", "fallback_rate"]].mean()
    aggregate.to_csv(RESULTS / "ablation_summary.csv", index=False)
    return aggregate


def run_fault_injection() -> pd.DataFrame:
    rows = []
    fault_signal = {
        "command_reject": "ack",
        "route_divergence": "state_hash",
        "telemetry_loss": "telemetry",
        "stale_ttl": "ttl",
    }
    monitors = {
        "Static": {"ack"},
        "Adaptive": {"ack", "telemetry"},
        "Consensus": {"ack", "telemetry", "state_hash"},
        "CADO": {"ack", "telemetry", "state_hash", "ttl"},
    }
    rollback_reliability = {"Static": 0.92, "Adaptive": 0.93, "Consensus": 0.95, "CADO": 0.98}
    for seed in range(N_SEEDS):
        for policy in POLICIES:
            rng = derive_rng("fault", seed, policy)
            faults = 80
            fault_types = rng.choice(list(fault_signal), size=faults)
            detected = np.array([fault_signal[kind] in monitors[policy] for kind in fault_types], dtype=int)
            successes = detected * rng.binomial(1, rollback_reliability[policy], faults)
            failed_duration = np.where(successes == 1, 1, 12)
            rows.append({
                "seed": seed,
                "policy": policy,
                "faults": faults,
                "fault_detection_rate": detected.mean(),
                "rollback_success_rate": successes.mean(),
                "failed_action_persistence_steps": failed_duration.mean(),
                "p95_persistence_steps": np.percentile(failed_duration, 95),
            })
    frame = pd.DataFrame(rows)
    frame.to_csv(RESULTS / "fault_injection_metrics.csv", index=False)
    return frame


def render_raw_alert(fmt: str, truth: dict) -> str:
    if fmt == "syslog":
        return f"<134>ts={truth['ts']} src={truth['src']} dst={truth['dst']} sev={truth['severity']:.3f} tactic={truth['tactic']} conf={truth['confidence']:.3f}"
    if fmt == "cef":
        return f"CEF:0|Vendor|WAF|1.0|{truth['tactic']}|alert|7|src={truth['src']} dst={truth['dst']} cs1={truth['tactic']} cn1={truth['severity']:.3f} cn2={truth['confidence']:.3f} rt={truth['ts']}"
    if fmt == "json":
        return json.dumps(truth, separators=(",", ":"))
    return ";".join(f"{k}={v}" for k, v in truth.items())


def normalize_alert(fmt: str, raw: str) -> dict:
    if fmt == "json":
        obj = json.loads(raw)
        return {k: obj[k] for k in ["ts", "src", "dst", "severity", "confidence", "tactic"]}
    if fmt == "cef":
        ext = raw.split("|", 7)[-1]
        pairs = dict(token.split("=", 1) for token in ext.split())
        return {"ts": int(pairs["rt"]), "src": pairs["src"], "dst": pairs["dst"], "severity": float(pairs["cn1"]), "confidence": float(pairs["cn2"]), "tactic": pairs["cs1"]}
    delimiter = ";" if fmt == "kv" else " "
    pairs = {}
    for token in raw.split(delimiter):
        if "=" in token:
            key, value = token.split("=", 1)
            key = key.strip()
            if fmt == "syslog" and key.startswith("<") and ">" in key:
                key = key.split(">", 1)[1]
            pairs[key] = value.strip()
    return {"ts": int(pairs["ts"]), "src": pairs["src"], "dst": pairs["dst"], "severity": float(pairs["sev"] if fmt == "syslog" else pairs["severity"]), "confidence": float(pairs["conf"] if fmt == "syslog" else pairs["confidence"]), "tactic": pairs["tactic"]}


def run_normalization_benchmark() -> pd.DataFrame:
    rng = derive_rng("normalize")
    rows = []
    formats = ["syslog", "cef", "json", "kv"]
    for fmt in formats:
        correct = 0
        latencies = []
        byte_lengths = []
        for idx in range(5_000):
            truth = {
                "ts": 1_800_000_000 + idx,
                "src": f"10.0.{idx % 16}.{idx % 253 + 1}",
                "dst": f"192.168.{idx % 8}.{(idx * 7) % 253 + 1}",
                "severity": round(float(rng.uniform(0.05, 0.99)), 3),
                "confidence": round(float(rng.uniform(0.05, 0.99)), 3),
                "tactic": str(rng.choice(["credential", "lateral", "web"])),
            }
            raw = render_raw_alert(fmt, truth)
            t0 = time.perf_counter_ns()
            parsed = normalize_alert(fmt, raw)
            latencies.append((time.perf_counter_ns() - t0) / 1_000.0)
            byte_lengths.append(len(raw.encode("utf-8")))
            correct += int(
                parsed["ts"] == truth["ts"]
                and parsed["src"] == truth["src"]
                and parsed["dst"] == truth["dst"]
                and parsed["tactic"] == truth["tactic"]
                and abs(parsed["severity"] - truth["severity"]) < 1e-9
                and abs(parsed["confidence"] - truth["confidence"]) < 1e-9
            )
        rows.append({
            "format": fmt,
            "records": 5_000,
            "exact_field_recovery": correct / 5_000,
            "median_latency_us": np.median(latencies),
            "p95_latency_us": np.percentile(latencies, 95),
            "throughput_records_s": 1_000_000.0 / np.mean(latencies),
            "mean_record_bytes": np.mean(byte_lengths),
        })
    frame = pd.DataFrame(rows)
    frame.to_csv(RESULTS / "normalization_benchmark.csv", index=False)
    return frame


def bootstrap_ci(values: np.ndarray, rng: np.random.Generator) -> tuple[float, float]:
    values = np.asarray(values, dtype=float)
    idx = rng.integers(0, len(values), size=(BOOTSTRAP_RESAMPLES, len(values)))
    means = values[idx].mean(axis=1)
    return tuple(np.percentile(means, [2.5, 97.5]))


def holm_adjust(pvalues: list[float]) -> list[float]:
    p = np.asarray(pvalues, dtype=float)
    order = np.argsort(p)
    adjusted = np.empty_like(p)
    running = 0.0
    m = len(p)
    for rank, idx in enumerate(order):
        candidate = (m - rank) * p[idx]
        running = max(running, candidate)
        adjusted[idx] = min(running, 1.0)
    return adjusted.tolist()


def summarize_and_test(primary: pd.DataFrame, ood: pd.DataFrame, faults: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    metrics = ["utility", "redirection_precision", "engagement_rate", "benign_false_redirect_rate", "unsafe_action_rate", "normalized_cost"]
    seed_summary = primary.groupby(["seed", "policy"], as_index=False)[metrics].mean()
    seed_summary.to_csv(RESULTS / "primary_seed_summary.csv", index=False)
    rng = derive_rng("bootstrap")
    summary_rows = []
    for policy in POLICIES:
        sub = seed_summary[seed_summary.policy == policy]
        for metric in metrics:
            values = sub[metric].to_numpy()
            lo, hi = bootstrap_ci(values, rng)
            summary_rows.append({"dataset": "primary", "policy": policy, "metric": metric, "mean": values.mean(), "ci_low": lo, "ci_high": hi, "n": len(values)})
    ood_metrics = ["utility", "unsafe_action_rate", "fallback_rate", "benign_false_redirect_rate"]
    ood_seed = ood.groupby(["seed", "policy"], as_index=False)[ood_metrics].mean()
    ood_seed.to_csv(RESULTS / "ood_seed_summary.csv", index=False)
    for policy in POLICIES:
        sub = ood_seed[ood_seed.policy == policy]
        for metric in ood_metrics:
            raw_values = sub[metric].to_numpy(dtype=float)
            finite_mask = np.isfinite(raw_values)
            values = raw_values[finite_mask]
            if len(values) == 0:
                continue
            lo, hi = bootstrap_ci(values, rng)
            summary_rows.append({"dataset": "ood", "policy": policy, "metric": metric, "mean": values.mean(), "ci_low": lo, "ci_high": hi, "n": len(values)})
    fault_seed = faults.groupby(["seed", "policy"], as_index=False)[["rollback_success_rate", "failed_action_persistence_steps"]].mean()
    for policy in POLICIES:
        sub = fault_seed[fault_seed.policy == policy]
        for metric in ["rollback_success_rate", "failed_action_persistence_steps"]:
            values = sub[metric].to_numpy()
            lo, hi = bootstrap_ci(values, rng)
            summary_rows.append({"dataset": "fault", "policy": policy, "metric": metric, "mean": values.mean(), "ci_low": lo, "ci_high": hi, "n": len(values)})
    summary = pd.DataFrame(summary_rows)
    summary.to_csv(RESULTS / "summary_statistics.csv", index=False)

    comparison_rows = []
    pvals = []
    for metric in metrics:
        pivot = seed_summary.pivot(index="seed", columns="policy", values=metric)
        for baseline in ["Static", "Adaptive", "Consensus"]:
            diff = pivot["CADO"].to_numpy() - pivot[baseline].to_numpy()
            if np.allclose(diff, 0):
                stat, pvalue, dz = 0.0, 1.0, 0.0
            else:
                stat, pvalue = wilcoxon(diff, alternative="two-sided", zero_method="wilcox")
                dz = diff.mean() / diff.std(ddof=1) if diff.std(ddof=1) > 0 else 0.0
            lo, hi = bootstrap_ci(diff, rng)
            comparison_rows.append({
                "metric": metric,
                "comparison": f"CADO - {baseline}",
                "mean_difference": diff.mean(),
                "ci_low": lo,
                "ci_high": hi,
                "wilcoxon_statistic": stat,
                "p_raw": pvalue,
                "effect_size_dz": dz,
                "n_paired_seeds": len(diff),
            })
            pvals.append(pvalue)
    adjusted = holm_adjust(pvals)
    for row, p_adj in zip(comparison_rows, adjusted):
        row["p_holm"] = p_adj
    comparisons = pd.DataFrame(comparison_rows)
    comparisons.to_csv(RESULTS / "paired_statistical_comparisons.csv", index=False)
    return summary, comparisons


def save_figure(fig: plt.Figure, stem: str) -> None:
    fig.savefig(FIGURES / f"{stem}.svg", bbox_inches="tight")
    fig.savefig(FIGURES / f"{stem}.pdf", bbox_inches="tight")
    fig.savefig(FIGURES / f"{stem}.tiff", dpi=600, bbox_inches="tight")
    fig.savefig(FIGURES / f"{stem}.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def configure_plotting() -> None:
    mpl.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans", "sans-serif"],
        "svg.fonttype": "none",
        "pdf.fonttype": 42,
        "font.size": 8,
        "axes.spines.right": False,
        "axes.spines.top": False,
        "axes.linewidth": 0.8,
        "legend.frameon": False,
        "figure.dpi": 150,
    })


PALETTE = {"Static": "#7A7A7A", "Adaptive": "#D98E2B", "Consensus": "#4C78A8", "CADO": "#2A9D8F"}


def plot_architecture() -> None:
    # Figure contract: a normalized event crosses one constrained control
    # boundary and leaves as a reversible H4 transaction. The schematic is
    # intentionally sparse because the caption carries the narrative detail.
    fig, ax = plt.subplots(figsize=(7.2, 3.65))
    ax.set_xlim(0, 15.2)
    ax.set_ylim(0, 7.7)
    ax.axis("off")

    ink = "#263746"
    muted = "#667788"
    border = "#AAB7C3"
    blue = "#356FA3"
    blue_fill = "#EEF4F9"
    teal = "#238A82"
    teal_fill = "#EAF5F3"
    amber = "#B47412"
    amber_fill = "#FBF4E8"
    red = "#B6543C"

    def box(x, y, w, h, text, *, edge=border, fill="white", fs=6.2,
            weight="normal", radius=0.10, align="center"):
        patch = mpl.patches.FancyBboxPatch(
            (x, y), w, h,
            boxstyle=f"round,pad=0.035,rounding_size={radius}",
            facecolor=fill, edgecolor=edge, linewidth=0.85,
        )
        ax.add_patch(patch)
        tx = x + (0.18 if align == "left" else w / 2)
        ax.text(tx, y + h / 2, text, ha=align, va="center", fontsize=fs,
                color=ink, fontweight=weight, linespacing=1.18)
        return patch

    def arrow(x1, y1, x2, y2, *, color=muted, lw=1.15, rad=0.0):
        ax.annotate(
            "", xy=(x2, y2), xytext=(x1, y1),
            arrowprops={"arrowstyle": "-|>", "color": color, "lw": lw,
                        "shrinkA": 1.5, "shrinkB": 1.5,
                        "connectionstyle": f"arc3,rad={rad}"},
        )

    # Evidence sources.
    box(0.25, 1.75, 2.55, 5.20, "", edge=border, fill="#FAFBFC", radius=0.14)
    ax.text(0.55, 6.55, "INPUTS", fontsize=7.3, color=blue,
            fontweight="bold", ha="left", va="center")
    for y, label in zip([5.62, 4.80, 3.98, 3.16, 2.34],
                        ["IDS / IPS", "WAF", "EDR", "Firewall / SDN", "Threat intelligence"]):
        box(0.55, y, 1.95, 0.58, label, edge="#9EB3C6", fs=5.8)

    # CADO is drawn as one control boundary with three successive contracts.
    box(3.45, 1.25, 7.25, 6.15, "", edge=teal, fill="#FBFDFC", radius=0.16)
    ax.text(3.77, 7.00, "CADO CONTROL PLANE", fontsize=7.8, color=teal,
            fontweight="bold", ha="left", va="center")

    box(3.85, 4.35, 1.75, 1.55,
        "Normalize\n\nAdapters -> NSE\ncontext | confidence\nprovenance",
        edge=blue, fill=blue_fill, fs=4.90, weight="bold")

    box(6.05, 3.28, 2.65, 3.05, "", edge=teal, fill=teal_fill, radius=0.12)
    ax.text(7.38, 5.98, "CONSTRAINED DECISION", ha="center", va="center",
            fontsize=6.0, color=teal, fontweight="bold")
    box(6.35, 5.02, 2.05, 0.60, "Consensus (a_c)", edge="#74AAA5",
        fill="white", fs=5.20, weight="bold")
    box(6.35, 4.18, 2.05, 0.60, "Residual (a_p), +/- 1 level", edge="#74AAA5",
        fill="white", fs=5.00)
    ax.text(7.38, 3.82, "admit only if", ha="center", va="center",
            fontsize=5.2, color=muted)
    ax.text(7.38, 3.53,
            "n >= 6  |  OOD <= 2.20\nconf. >= 0.55  |  LCB >= 0",
            ha="center", va="center", fontsize=5.05, color=ink, linespacing=1.25)

    box(9.10, 4.10, 1.15, 1.95,
        "DAT\n\ntyped\nscoped\nTTL\nverify\nrollback",
        edge=teal, fill="white", fs=5.35, weight="bold")

    arrow(2.80, 4.35, 3.83, 4.35, color=blue, lw=1.35)
    arrow(5.60, 5.12, 6.03, 5.12, color=teal, lw=1.35)
    arrow(8.70, 5.12, 9.08, 5.12, color=teal, lw=1.35)

    # H4 capabilities share one actuator boundary.
    box(11.35, 1.75, 3.55, 5.20, "", edge="#C8A66B", fill="#FFFEFB", radius=0.14)
    ax.text(11.68, 6.55, "H4 ACTUATION", fontsize=7.3, color=amber,
            fontweight="bold", ha="left", va="center")
    h4_boxes = [
        (11.72, 5.15, "Honeypoint", "near-asset decoy"),
        (13.22, 5.15, "Honeyproxy", "redirect + observe"),
        (11.72, 3.72, "Honeytrace", "persistent trace"),
        (13.22, 3.72, "Honeycenter", "coordinate H4"),
    ]
    for x, y, name, role in h4_boxes:
        role = role.replace("near-asset decoy", "near-asset\ndecoy").replace(
            "redirect + observe", "redirect +\nobserve").replace(
            "persistent trace", "persistent\ntrace").replace(
            "coordinate H4", "coordinate\nH4")
        box(x, y, 1.30, 1.02, f"{name}\n{role}", edge="#C79A4A",
            fill=amber_fill, fs=4.55, weight="bold" if name == "Honeycenter" else "normal")
    ax.text(13.12, 2.70, "least-scope deployment", fontsize=5.8,
            color="#805D20", ha="center", va="center")
    arrow(10.70, 5.12, 11.33, 5.12, color=amber, lw=1.35)

    # A single return lane makes verification and reversibility explicit.
    box(3.45, 0.25, 11.45, 0.72, "", edge="#C9D1D8", fill="#F5F7F8", radius=0.12)
    ax.text(3.78, 0.61, "ASSURANCE", fontsize=6.3, color=ink, fontweight="bold",
            ha="left", va="center")
    lane = [(5.35, "ACK"), (6.45, "state"), (7.70, "telemetry"),
            (9.10, "expiry"), (10.35, "rollback"), (11.85, "audit")]
    for i, (x, label) in enumerate(lane):
        color = red if label == "rollback" else (amber if label == "audit" else teal)
        ax.add_patch(mpl.patches.Circle((x, 0.61), 0.075, facecolor=color, edgecolor="none"))
        ax.text(x + 0.13, 0.61, label, fontsize=5.55, color=ink, ha="left", va="center")
        if i < len(lane) - 1:
            nx = lane[i + 1][0]
            ax.plot([x + 0.55, nx - 0.10], [0.61, 0.61], color="#B8C1C9", lw=0.7)
    arrow(14.45, 1.74, 14.45, 0.98, color=amber, lw=1.0)
    arrow(10.20, 0.24, 9.68, 4.08, color=red, lw=1.0, rad=-0.25)
    ax.text(9.65, 1.70, "failure or expiry", fontsize=5.3, color=red,
            ha="center", va="center", rotation=20)
    save_figure(fig, "figure1_architecture")


def plot_primary(summary: pd.DataFrame) -> None:
    metrics = [
        ("utility", "Defensive utility", "mean score"),
        ("redirection_precision", "Redirection precision", "proportion"),
        ("benign_false_redirect_rate", "Benign false redirects", "proportion"),
        ("normalized_cost", "Normalized resource cost", "mean cost/event"),
    ]
    fig, axes = plt.subplots(2, 2, figsize=(7.2, 5.2))
    for label, (metric, title, ylabel) in zip("abcd", metrics):
        ax = axes.flat["abcd".index(label)]
        sub = summary[(summary.dataset == "primary") & (summary.metric == metric)].set_index("policy").loc[POLICIES]
        x = np.arange(len(POLICIES))
        means = sub["mean"].to_numpy()
        yerr = np.vstack([means - sub["ci_low"].to_numpy(), sub["ci_high"].to_numpy() - means])
        ax.errorbar(x, means, yerr=yerr, fmt="o", markersize=5.5, capsize=3, color="#253746", ecolor="#253746", lw=1.1)
        for xi, policy in enumerate(POLICIES):
            ax.scatter(xi, means[xi], s=48, color=PALETTE[policy], edgecolor="white", linewidth=0.6, zorder=3)
        ax.set_xticks(x, POLICIES, rotation=18)
        ax.set_title(title, loc="left", fontsize=9, fontweight="bold")
        ax.set_ylabel(ylabel)
        ax.grid(axis="y", color="#D9DEE3", linewidth=0.5)
        ax.text(-0.16, 1.05, label, transform=ax.transAxes, fontsize=10, fontweight="bold")
    fig.suptitle("Primary paired evaluation across 30 simulation seeds", y=1.01, fontsize=10, fontweight="bold")
    fig.tight_layout()
    save_figure(fig, "figure2_primary_results")


def plot_robustness(primary: pd.DataFrame, summary: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(7.2, 2.65))
    cado = primary[primary.policy == "CADO"]
    gate_means = cado[["gate_insufficient", "gate_ood", "gate_noninferiority", "personalized_rate"]].mean()
    gate_labels = ["Sparse", "OOD", "Non-inferior", "Personalized"]
    colors = ["#8C8C8C", "#B35C44", "#4C78A8", "#2A9D8F"]
    axes[0].bar(np.arange(4), gate_means, color=colors, width=0.72)
    axes[0].set_xticks(np.arange(4), gate_labels, rotation=28, ha="right")
    axes[0].set_ylabel("fraction of decisions")
    axes[0].set_title("Safety-gate routing", loc="left", fontsize=9, fontweight="bold")
    axes[0].text(-0.16, 1.05, "a", transform=axes[0].transAxes, fontsize=10, fontweight="bold")

    unsafe = summary[(summary.dataset == "ood") & (summary.metric == "unsafe_action_rate")].set_index("policy").loc[POLICIES]
    vals = np.maximum(unsafe["mean"].to_numpy(), 1e-5)
    axes[1].bar(np.arange(4), vals, color=[PALETTE[p] for p in POLICIES], width=0.7)
    axes[1].set_yscale("log")
    axes[1].set_xticks(np.arange(4), POLICIES, rotation=25, ha="right")
    axes[1].set_ylabel("unsafe action rate (log scale)")
    axes[1].set_title("Held-out attacker", loc="left", fontsize=9, fontweight="bold")
    cado_fallback = summary[(summary.dataset == "ood") & (summary.policy == "CADO") & (summary.metric == "fallback_rate")].iloc[0]["mean"]
    axes[1].text(0.96, 0.95, f"CADO fallback: {cado_fallback:.1%}", transform=axes[1].transAxes, ha="right", va="top", fontsize=7, color="#253746", bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.8, "pad": 1.5})
    axes[1].text(-0.16, 1.05, "b", transform=axes[1].transAxes, fontsize=10, fontweight="bold")

    fault_metric = summary[(summary.dataset == "fault") & (summary.metric == "failed_action_persistence_steps")].set_index("policy").loc[POLICIES]
    axes[2].bar(np.arange(4), fault_metric["mean"], color=[PALETTE[p] for p in POLICIES], width=0.7)
    axes[2].set_xticks(np.arange(4), POLICIES, rotation=25, ha="right")
    axes[2].set_ylabel("mean persistence (steps)")
    axes[2].set_title("Actuation fault containment", loc="left", fontsize=9, fontweight="bold")
    axes[2].text(-0.16, 1.05, "c", transform=axes[2].transAxes, fontsize=10, fontweight="bold")
    for ax in axes:
        ax.grid(axis="y", color="#D9DEE3", linewidth=0.5)
    fig.tight_layout()
    save_figure(fig, "figure3_robustness")


def plot_runtime(primary: pd.DataFrame, benchmark: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.7))
    axes[0].bar(benchmark["format"].str.upper(), benchmark["throughput_records_s"] / 1000, color="#4C78A8")
    axes[0].set_ylabel("thousand records/s")
    axes[0].set_title("Alert normalization throughput", loc="left", fontsize=9, fontweight="bold")
    axes[0].text(-0.13, 1.05, "a", transform=axes[0].transAxes, fontsize=10, fontweight="bold")
    latency = primary.groupby("policy")["decision_latency_us_p95"].median().reindex(POLICIES)
    axes[1].bar(np.arange(4), latency, color=[PALETTE[p] for p in POLICIES])
    axes[1].set_xticks(np.arange(4), POLICIES, rotation=20)
    axes[1].set_ylabel("median episode p95 (µs)")
    axes[1].set_title("Policy decision latency", loc="left", fontsize=9, fontweight="bold")
    axes[1].text(-0.13, 1.05, "b", transform=axes[1].transAxes, fontsize=10, fontweight="bold")
    for ax in axes:
        ax.grid(axis="y", color="#D9DEE3", linewidth=0.5)
    fig.tight_layout()
    save_figure(fig, "figure4_runtime")


def write_config() -> None:
    config = {
        "master_seed": MASTER_SEED,
        "paired_seeds": N_SEEDS,
        "events_per_episode": EVENTS_PER_EPISODE,
        "scenarios": SCENARIOS,
        "in_distribution_attackers": {k: dict(zip(FEATURE_NAMES, v.tolist())) for k, v in ATTACKERS.items()},
        "held_out_attacker": {k: dict(zip(FEATURE_NAMES, v.tolist())) for k, v in OOD_ATTACKER.items()},
        "policies": POLICIES,
        "fixed_design_parameters": {
            "max_attack_stage": MAX_ATTACK_STAGE,
            "risk_weights": RISK_WEIGHTS,
            "consensus_thresholds": CONSENSUS_THRESHOLDS,
            "profile_update_confidence": PROFILE_UPDATE_CONFIDENCE,
            "minimum_profile_evidence": MIN_PROFILE_EVIDENCE,
            "ood_distance_limit": OOD_DISTANCE_LIMIT,
            "escalation_confidence_minimum": ESCALATION_CONFIDENCE_MIN,
            "one_sided_95_z": ONE_SIDED_95_Z,
            "uncertainty_count_coefficient": UNCERTAINTY_COUNT_COEFFICIENT,
            "uncertainty_distance_coefficient": UNCERTAINTY_DISTANCE_COEFFICIENT,
        },
        "observability_boundary": (
            "PolicyState uses alert confidence and observed behavior features only; "
            "the latent malicious label is reserved for evaluation scoring."
        ),
        "bootstrap_resamples": BOOTSTRAP_RESAMPLES,
        "python": sys.version,
        "platform": platform.platform(),
        "numpy": np.__version__,
        "pandas": pd.__version__,
        "matplotlib": mpl.__version__,
    }
    (RESULTS / "experiment_config.json").write_text(json.dumps(config, indent=2), encoding="utf-8")


def main() -> None:
    configure_plotting()
    write_config()
    primary = run_primary()
    ood = run_ood()
    faults = run_fault_injection()
    ablation = run_ablation()
    benchmark = run_normalization_benchmark()
    summary, comparisons = summarize_and_test(primary, ood, faults)
    save_architecture(FIGURES)
    plot_primary(summary)
    plot_robustness(primary, summary)
    plot_runtime(primary, benchmark)
    print(summary.to_string(index=False))
    print("\nKey paired comparisons:\n", comparisons[comparisons.metric.isin(["utility", "unsafe_action_rate"])].to_string(index=False))
    print("\nAblation summary:\n", ablation.to_string(index=False))


if __name__ == "__main__":
    main()
