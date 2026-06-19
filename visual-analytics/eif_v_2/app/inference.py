"""
EIF Inference  —  Fixed v5
============================

Bugs fixed vs previous version:
  [1] INVERTED SIGMOID (critical)
      compute_paths() returns path LENGTH. Shorter = anomaly.
      Previous:  score = sigmoid(-k * (raw - threshold))
        → raw < threshold (anomaly) gives sigmoid(+k*...) < 0.5  ← LOW score for fraud
        → raw > threshold (normal)  gives sigmoid(-k*...) > 0.5  ← HIGH score for legit
        → completely backwards
      Fixed:     score = sigmoid(+k * (threshold - raw))
        → raw < threshold (anomaly): threshold-raw > 0 → sigmoid > 0.5 ← HIGH fraud score ✓
        → raw > threshold (normal):  threshold-raw < 0 → sigmoid < 0.5 ← LOW fraud score ✓

  [2] RELATIVE TRAIN_DATA_PATH (caused silent score=0 crashes)
      Previous: TRAIN_DATA_PATH = "models/eif_training_data.npy"
      This is evaluated at module IMPORT time. If uvicorn is started from any directory
      other than eif_v_2/, np.load() throws FileNotFoundError, the module fails to
      import, FastAPI never starts, and EifService.onErrorResume() silently returns
      score=0.0 for every single transaction.
      Fixed: derive absolute path from MODEL_DIR (imported from config).

  [3] FEATURE_EXPLANATIONS merge was overwriting config values with an empty dict
      if _DERIVED_EXPLANATIONS had a key collision. Fixed with explicit precedence.
"""

import joblib
import json
import numpy as np
from pathlib import Path

from eif import iForest

from .config import (
    MODEL_DIR,          # [FIX 2] now exported from config so we can build absolute paths
    SCALER_PATH,
    METADATA_PATH,
    FEATURE_EXPLANATIONS,
)

FEATURE_NAMES = [
    "velocity", "burst", "neighbors",
    "ip", "ja3",
    "comm_fraud", "ring", "net_risk",
    "comm_ring", "comm_burst", "comm_velocity",
    "neighbor_comm", "ip_comm", "velocity_burst",
]

# Merge explanations — derived keys extend the base dict from config
_DERIVED_EXPLANATIONS = {
    "comm_ring":         "High community fraud combined with money laundering ring membership",
    "comm_burst":        "Erratic transaction bursts in a high-risk network neighborhood",
    "comm_velocity":     "High transaction velocity within a fraudulent community",
    "neighbor_comm":     "Activity spread across risky peers within coordinated fraud rings",
    "ip_comm":           "Infrastructure IP sharing detected within a fraud cluster",
    "velocity_burst":    "High transaction velocity concurrent with account balance bursts",
}
# Config explanations take precedence for any overlapping keys
ALL_EXPLANATIONS = {**_DERIVED_EXPLANATIONS, **FEATURE_EXPLANATIONS}

# [FIX 2] Absolute path — safe regardless of uvicorn startup directory
TRAIN_DATA_PATH = MODEL_DIR / "eif_training_data.npy"


print("\n🚀 Loading EIF service...")

# ── Load scaler ───────────────────────────────────────────────────────────────
scaler = joblib.load(SCALER_PATH)
print("✅ Scaler loaded")

# ── Load metadata ─────────────────────────────────────────────────────────────
with open(METADATA_PATH) as f:
    metadata = json.load(f)

# threshold is the anomaly boundary (e.g. 95th percentile)
# EIF score >= threshold  →  anomaly  →  fraud score > 0.5
threshold = metadata.get("threshold", 0.0)
print(f"✅ Threshold loaded: {threshold:.4f}  (score ≥ this → anomaly)")

# ── Load training data ────────────────────────────────────────────────────────
training_data = np.load(str(TRAIN_DATA_PATH))
print(f"✅ Training data loaded: shape={training_data.shape}")

# ── Rebuild EIF model ─────────────────────────────────────────────────────────
model = iForest(
    training_data,
    ntrees=metadata.get("ntrees", 100),
    sample_size=metadata.get("sample_size", min(256, len(training_data))),
    ExtensionLevel=metadata.get("extension_level", 0),
)
print("✅ EIF model rebuilt from dynamic metadata")
print("✅ Service ready\n")


# ── Feature expansion ─────────────────────────────────────────────────────────

def expand_features(features):
    """
    Expand 8 raw features to 14 by adding cross-product signals.
    Input order must match config.py FEATURE_NAMES exactly.
    """
    velocity, burst, neighbors, ip, ja3, comm_fraud, ring, net_risk = features

    comm_ring       = comm_fraud * ring
    comm_burst      = comm_fraud * burst
    comm_velocity   = comm_fraud * velocity
    neighbor_comm   = neighbors  * comm_fraud
    ip_comm         = ip         * comm_fraud
    velocity_burst  = velocity   * burst

    return [
        velocity, burst, neighbors,
        ip, ja3,
        comm_fraud, ring, net_risk,
        comm_ring, comm_burst, comm_velocity,
        neighbor_comm, ip_comm, velocity_burst,
    ]


# ── Feature importance ────────────────────────────────────────────────────────

def compute_feature_importance(model, X_scaled, base_path_length):
    """
    Estimate per-feature contribution by zeroing each feature and measuring
    the change in path length.

    A POSITIVE impact means: zeroing this feature made the path LONGER
    (i.e. the feature was contributing to the SHORT path = anomaly signal).
    We sort by abs(impact) so the biggest contributors surface first.
    """
    impacts = {}
    for i, name in enumerate(FEATURE_NAMES):
        X_copy = X_scaled.copy()
        X_copy[0, i] = 0.0
        new_path = model.compute_paths(X_copy)[0]
        # Positive: feature pushed score UP (toward anomaly)
        impacts[name] = float(new_path - base_path_length)
    return impacts


# ── Explanation builder ───────────────────────────────────────────────────────

def generate_explanation(top_factors: dict) -> str:
    reasons = [
        ALL_EXPLANATIONS[k]
        for k in top_factors
        if k in ALL_EXPLANATIONS
    ]
    if not reasons:
        return "No strong anomaly signals detected."
    return ", ".join(reasons) + "."


# ── Main scoring function ─────────────────────────────────────────────────────

def score_eif(features):
    """
    Score a transaction using the Extended Isolation Forest.

    Parameters
    ----------
    features : list of 8 floats
        [velocity_score, burst_score, suspicious_neighbor_count,
         ip_reuse_count, ja3_reuse_count, community_fraud_rate_feat, ring_membership_feat, network_risk_score]

    Returns
    -------
    score       : float in [0, 1]  — higher = more anomalous = higher fraud risk
    top_factors : dict[str, float] — top 3 contributing features
    explanation : str              — human-readable explanation
    """
    print("\n──────────────────────────────")
    print("🧪 EIF INFERENCE")
    print("──────────────────────────────")
    print("Raw features:", features)

    if len(features) != 8:
        raise ValueError(f"Expected 8 features, got {len(features)}")

    # 1. Expand
    expanded = expand_features(features)
    X = np.array(expanded, dtype=np.float64).reshape(1, -1)

    # 2. Scale
    X_scaled = scaler.transform(X)

    # 3. Get score from EIF
    #    compute_paths() returns a normalized anomaly score [0, 1]
    #      score ~ 1.0 → ANOMALY
    #      score ~ 0.0 → NORMAL
    raw_path = float(model.compute_paths(X_scaled)[0])
    print(f"EIF Score: {raw_path:.4f}  |  threshold: {threshold:.4f}")

    # 4. [FIX 1] Convert raw score → final calibrated score [0, 1]
    #
    #    We want:  raw_path >> threshold  →  score → 1.0  (definitely anomalous)
    #              raw_path == threshold  →  score = 0.5  (decision boundary)
    #              raw_path << threshold  →  score → 0.0  (definitely normal)
    #
    #    Formula: sigmoid(+k * (raw_path - threshold))
    k     = 6.0
    score = float(1.0 / (1.0 + np.exp(-k * (raw_path - threshold))))
    print(f"Final score: {score:.4f}")

    # 5. Feature importance
    impacts     = compute_feature_importance(model, X_scaled, raw_path)
    top_3       = sorted(impacts.items(), key=lambda x: abs(x[1]), reverse=True)[:3]
    top_factors = dict(top_3)

    # 6. Explanation
    explanation = generate_explanation(top_factors)

    print(f"Top factors: {top_factors}")
    print(f"Explanation: {explanation}")
    print("──────────────────────────────\n")

    return score, top_factors, explanation