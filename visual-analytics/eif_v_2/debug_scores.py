import pandas as pd, numpy as np
import sys
print("Starting...")
sys.stdout.flush()
from eif import iForest
print("eif imported")
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import f1_score
print("sklearn imported")

df = pd.read_csv("/home/rupali-jha/MULE_HUNTER/shared-data/eif_features.csv")
y  = df["is_fraud"].values
print("df loaded")
RAW_FEATURES = ["velocity_score", "burst_score", "suspicious_neighbor_count", "ip_reuse_count", "ja3_reuse_count", "community_fraud_rate_feat", "ring_membership_feat", "network_risk_score"]

def expand_features(row):
    return [
        row["velocity_score"],
        row["burst_score"],
        row["suspicious_neighbor_count"],
        row["ip_reuse_count"],
        row["ja3_reuse_count"],
        row["community_fraud_rate_feat"],
        row["ring_membership_feat"],
        row["network_risk_score"],
        row["community_fraud_rate_feat"] * row["ring_membership_feat"],
        row["community_fraud_rate_feat"] * row["burst_score"],
        row["community_fraud_rate_feat"] * row["velocity_score"],
        row["suspicious_neighbor_count"] * row["community_fraud_rate_feat"],
        row["ip_reuse_count"] * row["community_fraud_rate_feat"],
        row["velocity_score"] * row["burst_score"]
    ]

expanded = df[RAW_FEATURES].apply(expand_features, axis=1, result_type="expand")
X = expanded.values
print("X shape:", X.shape)
X_scaled = StandardScaler().fit_transform(X)
X_scaled = np.nan_to_num(X_scaled, nan=0.0, posinf=5.0, neginf=-5.0)
print("X scaled")

try:
    model = iForest(X_scaled, ntrees=200, sample_size=256, ExtensionLevel=0)
    print("model created")
    scores = np.array(model.compute_paths(X_scaled))
    print("scores computed")
except Exception as e:
    print("ERROR:", e)

pct5_lte = np.percentile(scores, 5)
pct20_lte = np.percentile(scores, 20)
print("pct compiled")
print("Correlation scores vs y:", np.corrcoef(scores, y)[0,1])
