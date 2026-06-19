"""
EIF Feature Dataset Builder
============================
Builds eif_features.csv from nodes.csv with:
  - All rows (no row-level filtering)
  - is_fraud label preserved
  - community_fraud_rate + ring_membership added directly (highest corr with fraud)
  - Dead feature flow_risk_score removed (in_out_ratio is 0 everywhere)
  - Correlation-based column drop removed (was silently dropping key features)
"""

import pandas as pd
import numpy as np
from pathlib import Path

BASE_DIR  = Path(__file__).resolve().parents[2]
DATA_PATH = BASE_DIR / "shared-data" / "nodes.csv"
OUT_PATH  = BASE_DIR / "shared-data" / "eif_features.csv"

df = pd.read_csv(DATA_PATH)
print(f"Loaded nodes.csv: {df.shape}")

# ------------------------------------------------
# Safety clips
# ------------------------------------------------
df["amount_entropy"]   = df["amount_entropy"].clip(lower=0)
df["account_age_days"] = df["account_age_days"].clip(lower=1)

# ------------------------------------------------
# 1. Behaviour Features
# ------------------------------------------------
df["velocity_score"] = df["tx_velocity_7d"] / (df["account_age_days"] + 1)
df["burst_score"]    = df["balance_std"]    / (df["balance_mean"] + 1)

# ------------------------------------------------
# 2. Network / Graph Features  (strongest signals)
# ------------------------------------------------
# community_fraud_rate: corr=0.779 with is_fraud — top discriminator
df["community_fraud_rate_feat"] = df["community_fraud_rate"].clip(0, 1)

# ring_membership: corr=0.039 (but very bimodal — almost all fraud has ring_membership=1)
df["ring_membership_feat"] = df["ring_membership"].clip(0, 1)

# ------------------------------------------------
# 3. Transaction Spread Signals
# ------------------------------------------------
# fan_out_ratio is actually LOWER for fraud (0.189 fraud vs 0.292 normal)
# suspicious_neighbor_count still captures volume via tx_count multiplication
df["suspicious_neighbor_count"] = (
    df["fan_out_ratio"] * df["tx_count"]
).clip(0, 20)

# ------------------------------------------------
# 4. Infrastructure Risk Signals
# ------------------------------------------------
# ip_reuse_count via addr_entropy: corr=0.332 with fraud
df["ip_reuse_count"] = (df["addr_entropy"] * 3).clip(0, 10)

# ja3_reuse_count: risky_email signal (risky_email corr is near 0, safe to keep)
df["ja3_reuse_count"] = (
    df["risky_email"] * 5 + (1 - df["device_consistency"]) * 3
).clip(0, 10)

# device_reuse_count: corr=-0.079 with fraud (counterintuitive — REMOVED from features,
# device_consistency is actually higher for fraudsters in this dataset)

# ------------------------------------------------
# 5. Composite Network Risk
#    (pagerank + community_fraud_rate + ring_membership weighted sum)
# ------------------------------------------------
df["network_risk_score"] = (
    df["pagerank"] * 10000
    + df["community_fraud_rate"] * 5
    + df["ring_membership"] * 3
)

# ------------------------------------------------
# Final Feature Set
# ------------------------------------------------
FEATURE_NAMES = [
    "velocity_score",
    "burst_score",
    "suspicious_neighbor_count",
    "ip_reuse_count",
    "ja3_reuse_count",
    "community_fraud_rate_feat",   # NEW — corr=0.779, top signal
    "ring_membership_feat",        # NEW — strong bimodal fraud signal
    "network_risk_score",
]

eif_df = df[FEATURE_NAMES].copy()

# Preserve label for supervised evaluation during training
if "is_fraud" in df.columns:
    eif_df["is_fraud"] = df["is_fraud"].values
    fraud_rate = eif_df["is_fraud"].mean()
    print(f"Label included. Fraud rate: {fraud_rate:.4f} ({eif_df['is_fraud'].sum()} / {len(eif_df)})")
else:
    print("⚠️  No is_fraud column found — label not included.")

# ------------------------------------------------
# Save
# ------------------------------------------------
eif_df.to_csv(OUT_PATH, index=False)
print(f"✅ Saved: {OUT_PATH}")
print(f"   Shape: {eif_df.shape}")
print(f"   Columns: {eif_df.columns.tolist()}")
print(eif_df.describe().to_string())