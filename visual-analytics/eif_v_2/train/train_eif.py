"""
EIF Training Pipeline — Optimized v6
======================================

Improvements over v5:
  [1] Adds community_fraud_rate (corr=0.779 with fraud) to feature set — was ignored before.
  [2] Adds ring_membership as a feature.
  [3] Removes device_reuse_count (negative correlation with fraud = hurts the model).
  [4] Improved interaction features focused on the strongest discriminators.
  [5] Threshold grid search: sweeps percentiles 1–20 to find the cutoff that
      maximises F1 on training data (instead of hard-coding the 5th percentile).
  [6] EIF hyperparameter search over ntrees × sample_size × ExtensionLevel.
      Best config is saved; all others are discarded.

Scoring direction reminder:
  compute_paths() returns a NORMALIZED ANOMALY SCORE (0 to 1).
    Score close to 1 → ANOMALY (fraud)
    Score close to 0 → NORMAL
  So:  preds = (scores >= threshold)
       AUC:     roc_auc_score(y, scores)
"""

import pandas as pd
import numpy as np
import joblib
import json
import time
from itertools import product
from pathlib import Path

from eif import iForest
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import f1_score, precision_score, recall_score, roc_auc_score

# ──────────────────────────────────────────────────────────────────────────────
# PATHS
# ──────────────────────────────────────────────────────────────────────────────

BASE_DIR = Path(__file__).resolve().parents[3]

DATA_PATH  = BASE_DIR / "shared-data" / "eif_features.csv"
MODEL_DIR  = BASE_DIR / "visual-analytics" / "eif_v_2" / "models"

SCALER_PATH     = MODEL_DIR / "eif_scaler.pkl"
MODEL_PATH      = MODEL_DIR / "eif_model.pkl"
TRAIN_DATA_PATH = MODEL_DIR / "eif_training_data.npy"
EVAL_PATH       = MODEL_DIR / "eif_eval.json"
META_PATH       = MODEL_DIR / "model_metadata.json"


# ──────────────────────────────────────────────────────────────────────────────
# RAW FEATURES
# Order must match inference.py expand_features — update that file too if changed.
# ──────────────────────────────────────────────────────────────────────────────

RAW_FEATURES = [
    "velocity_score",
    "burst_score",
    "suspicious_neighbor_count",
    "ip_reuse_count",
    "ja3_reuse_count",
    "community_fraud_rate_feat",   # strongest signal: corr=0.779 with fraud
    "ring_membership_feat",        # bimodal fraud signal
    "network_risk_score",
]


# ──────────────────────────────────────────────────────────────────────────────
# FEATURE EXPANSION
# Must stay identical to inference.py expand_features.
# ──────────────────────────────────────────────────────────────────────────────

def expand_features(row):
    velocity   = row["velocity_score"]
    burst      = row["burst_score"]
    neighbors  = row["suspicious_neighbor_count"]
    ip         = row["ip_reuse_count"]
    ja3        = row["ja3_reuse_count"]
    comm_fraud = row["community_fraud_rate_feat"]
    ring       = row["ring_membership_feat"]
    net_risk   = row["network_risk_score"]

    # Interaction terms — emphasise the strongest discriminators
    comm_ring       = comm_fraud * ring          # both high → almost certainly mule
    comm_burst      = comm_fraud * burst         # high community fraud + erratic balance
    comm_velocity   = comm_fraud * velocity      # high community fraud + fast tx
    neighbor_comm   = neighbors  * comm_fraud    # spread tx in a fraud community
    ip_comm         = ip         * comm_fraud    # address randomisation in fraud community
    velocity_burst  = velocity   * burst

    return [
        velocity, burst, neighbors,
        ip, ja3,
        comm_fraud, ring, net_risk,
        comm_ring, comm_burst, comm_velocity,
        neighbor_comm, ip_comm, velocity_burst,
    ]


FEATURE_NAMES = [
    "velocity", "burst", "neighbors",
    "ip", "ja3",
    "comm_fraud", "ring", "net_risk",
    "comm_ring", "comm_burst", "comm_velocity",
    "neighbor_comm", "ip_comm", "velocity_burst",
]


# ──────────────────────────────────────────────────────────────────────────────
# HYPERPARAMETER GRID
# ──────────────────────────────────────────────────────────────────────────────

NTREES_GRID       = [100, 200]
SAMPLE_SIZE_GRID  = [256]
EXT_LEVEL_GRID    = [0, 1]

# Percentile range to search for the best anomaly threshold (top 1-20% scores)
PERCENTILE_RANGE  = range(80, 100)   # 80th → 99th percentile


# ──────────────────────────────────────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────────────────────────────────────

def best_threshold_f1(scores, y):
    """Return (best_f1, best_threshold, best_pct) over PERCENTILE_RANGE."""
    best_f1 = -1
    best_thr = None
    best_pct = None
    for pct in PERCENTILE_RANGE:
        thr   = float(np.percentile(scores, pct))
        preds = (scores >= thr).astype(int)
        f1    = f1_score(y, preds, zero_division=0)
        if f1 > best_f1:
            best_f1  = f1
            best_thr = thr
            best_pct = pct
    return best_f1, best_thr, best_pct


def evaluate(scores, y, threshold):
    """Return full metrics dict given scores and threshold."""
    preds     = (scores >= threshold).astype(int)
    f1        = f1_score(y, preds, zero_division=0)
    precision = precision_score(y, preds, zero_division=0)
    recall    = recall_score(y, preds, zero_division=0)
    auc       = roc_auc_score(y, scores)
    return {"f1": float(f1), "precision": float(precision),
            "recall": float(recall), "auc": float(auc)}


# ──────────────────────────────────────────────────────────────────────────────
# PIPELINE
# ──────────────────────────────────────────────────────────────────────────────

print("\n🚀 Starting EIF Optimized Training Pipeline (v6)\n")
t0 = time.time()

# ── Load ──────────────────────────────────────────────────────────────────────
print("📂 Loading dataset:", DATA_PATH)
df = pd.read_csv(DATA_PATH)
print("Dataset shape:", df.shape)

missing = [f for f in RAW_FEATURES if f not in df.columns]
if missing:
    raise ValueError(f"Missing features in CSV: {missing}")
print("✅ All required features present")

df = df.replace([np.inf, -np.inf], np.nan).fillna(0)

# Labels
y = df["is_fraud"].values if "is_fraud" in df.columns else None
if y is not None:
    print(f"🏷️  Labels loaded — fraud rate: {y.mean():.4f}  ({y.sum()} / {len(y)})")
else:
    print("⚠️  No labels — will skip evaluation and threshold optimisation.")

# ── Feature expansion ─────────────────────────────────────────────────────────
print("\n⚙️  Expanding features")
expanded = df[RAW_FEATURES].apply(expand_features, axis=1, result_type="expand")
expanded.columns = FEATURE_NAMES
X = expanded.values
print("Expanded feature dimension:", X.shape)

# ── Scale ─────────────────────────────────────────────────────────────────────
# NOTE: StandardScaler (not RobustScaler) is used here because two features —
# community_fraud_rate_feat and ring_membership_feat — are extremely sparse
# (IQR=0 at 25th–75th percentile).  RobustScaler divides by IQR → inf for
# those features.  StandardScaler uses std-dev which is non-zero for all
# features and produces well-conditioned values for EIF.
print("\n⚙️  Applying StandardScaler")
scaler   = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Safety guard: clip any residual inf/nan (e.g. from constant features)
X_scaled = np.nan_to_num(X_scaled, nan=0.0, posinf=5.0, neginf=-5.0)

# ── Hyperparameter search ─────────────────────────────────────────────────────
if y is not None:
    print("\n🔍 Hyperparameter + threshold search")
    print(f"   Grid: ntrees={NTREES_GRID}  sample_size={SAMPLE_SIZE_GRID}  "
          f"ext_level={EXT_LEVEL_GRID}  percentiles=1–{max(PERCENTILE_RANGE)}")

    configs = list(product(NTREES_GRID, SAMPLE_SIZE_GRID, EXT_LEVEL_GRID))
    print(f"   Total configs: {len(configs)}\n")

    best_f1     = -1
    best_config = None
    best_model  = None
    best_scores = None
    best_thr    = None
    best_pct    = None

    for i, (ntrees, sample_size, ext_level) in enumerate(configs, 1):
        sample_size = min(sample_size, len(X_scaled))
        t_start = time.time()

        model = iForest(
            X_scaled,
            ntrees=ntrees,
            sample_size=sample_size,
            ExtensionLevel=ext_level,
        )
        scores = np.array(model.compute_paths(X_scaled))
        f1, thr, pct = best_threshold_f1(scores, y)

        elapsed = time.time() - t_start
        status  = "🏆 NEW BEST" if f1 > best_f1 else "  "
        print(f"[{i:02d}/{len(configs)}] ntrees={ntrees:4d}  "
              f"sample={sample_size:3d}  ext={ext_level}  "
              f"pct={pct:02d}  F1={f1:.4f}  ({elapsed:.1f}s)  {status}")

        if f1 > best_f1:
            best_f1     = f1
            best_config = (ntrees, sample_size, ext_level)
            best_model  = model
            best_scores = scores
            best_thr    = thr
            best_pct    = pct

    print(f"\n✅ Best config: ntrees={best_config[0]}  sample_size={best_config[1]}  "
          f"ext_level={best_config[2]}  threshold_pct={best_pct}  F1={best_f1:.4f}")

    model     = best_model
    scores    = best_scores
    threshold = best_thr

else:
    # No labels — train with sensible defaults, use 5th percentile
    print("\n🧠 Training with default config (no labels for optimisation)")
    model = iForest(
        X_scaled,
        ntrees=500,
        sample_size=min(256, len(X_scaled)),
        ExtensionLevel=1,
    )
    scores    = np.array(model.compute_paths(X_scaled))
    threshold = float(np.percentile(scores, 95))

# ── Path-length statistics ────────────────────────────────────────────────────
print("\n📊 Score statistics (higher = more anomalous)")
print("  min  (most normal):   ", round(scores.min(), 4))
print("  max  (most anomalous):", round(scores.max(), 4))
print("  mean:                 ", round(scores.mean(), 4))
print(f"\n🎯 Anomaly threshold: {threshold:.6f}  "
      f"(score >= threshold → flagged as anomaly)")

# ── Save artefacts ────────────────────────────────────────────────────────────
MODEL_DIR.mkdir(parents=True, exist_ok=True)
joblib.dump(scaler, SCALER_PATH)
np.save(TRAIN_DATA_PATH, X_scaled)
print("\n💾 Scaler saved:        ", SCALER_PATH)
print("💾 Training data saved: ", TRAIN_DATA_PATH)

# ── Evaluation ────────────────────────────────────────────────────────────────
if y is not None:
    print("\n📈 Final evaluation")
    metrics = evaluate(scores, y, threshold)
    metrics["threshold"] = float(threshold)

    with open(EVAL_PATH, "w") as f:
        json.dump(metrics, f, indent=2)

    print(f"\n╔══════════════════════════════╗")
    print(f"║   FINAL EVALUATION METRICS   ║")
    print(f"╠══════════════════════════════╣")
    print(f"║  F1        : {metrics['f1']:.4f}           ║")
    print(f"║  Precision : {metrics['precision']:.4f}           ║")
    print(f"║  Recall    : {metrics['recall']:.4f}           ║")
    print(f"║  AUC       : {metrics['auc']:.4f}           ║")
    print(f"╚══════════════════════════════╝")
else:
    metrics = {"threshold": float(threshold)}
    print("\n⚠️  No labels — skipping evaluation.")

# ── Metadata ──────────────────────────────────────────────────────────────────
ntrees_used, sample_used, ext_used = (
    best_config if y is not None else (500, min(256, len(X_scaled)), 1)
)
metadata = {
    "model":                "EIF",
    "version":              "v6",
    "raw_feature_dim":      len(RAW_FEATURES),
    "expanded_feature_dim": len(FEATURE_NAMES),
    "threshold":            float(threshold),
    "threshold_direction":  "gte",
    "threshold_percentile": int(best_pct) if y is not None else 95,
    "ntrees":               ntrees_used,
    "sample_size":          sample_used,
    "extension_level":      ext_used,
    "raw_features":         RAW_FEATURES,
    "expanded_features":    FEATURE_NAMES,
}
with open(META_PATH, "w") as f:
    json.dump(metadata, f, indent=2)

print("\n📦 Metadata saved:", META_PATH)

# ── Sample debug output ───────────────────────────────────────────────────────
print("\n🔬 Sample scores (higher = more anomalous)")
for i in range(min(5, len(scores))):
    flag = "⚠ ANOMALY" if scores[i] >= threshold else "✓ normal"
    lbl  = f"  label={int(y[i])}" if y is not None else ""
    print(f"  sample {i}: score={scores[i]:.4f}  {flag}{lbl}")

total_time = time.time() - t0
print(f"\n✅ EIF Training Complete  (total time: {total_time:.1f}s)\n")