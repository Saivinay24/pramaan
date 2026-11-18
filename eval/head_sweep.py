#!/usr/bin/env python3
"""Pick the head architecture on the interim features before the full run.

Trains on every seen family, evaluates per-family EER on held-out clips (clean, 4 s) and
on the unseen cloner. Reports wall time. Cheap, runs in a minute.
"""
import sys, os, time
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
from pramaan.model import eer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
from sklearn.svm import SVC

path = sys.argv[1] if len(sys.argv) > 1 else "eval/results/features_interim.npz"
z = np.load(path, allow_pickle=True)
X, y = z["X"], z["y"].astype(int)
cid, cond, pre, gen = z["clip_id"].astype(str), z["condition"].astype(str), z["prefix_s"].astype(float), z["generator"].astype(str)
parent = z["parent"].astype(str); group = np.where(parent != "", parent, cid)
rng = np.random.default_rng(0)
units = np.array(sorted(set(group))); rng.shuffle(units)
n = len(units); tr_g, te_g = set(units[:int(.75 * n)]), set(units[int(.75 * n):])
seen = [g for g in ["xtts_v2", "freevc24", "encodec", "mac_say", "mms_vits", "kokoro"] if (gen == g).any()]
full = (pre == 4.0) & (cond == "clean")
tr = np.isin(group, list(tr_g)) & full & ((y == 0) | np.isin(gen, seen))
te = np.isin(group, list(te_g)) & full
print(f"train {tr.sum()} rows, seen {seen}")

# per-family sample weights: each family (and bona) carries equal total weight
def weights(m):
    g = np.where(y[m] == 0, "bona", gen[m]); w = np.ones(m.sum())
    for k in set(g):
        w[g == k] = 1.0 / (g == k).sum()
    return w / w.mean()

configs = {
    "pca64_lr": Pipeline([("sc", StandardScaler()), ("pca", PCA(64, random_state=0)), ("lr", LogisticRegression(C=1.0, max_iter=4000))]),
    "lr_c0.02": Pipeline([("sc", StandardScaler()), ("lr", LogisticRegression(C=0.02, max_iter=4000))]),
    "pca256_lr": Pipeline([("sc", StandardScaler()), ("pca", PCA(256, random_state=0)), ("lr", LogisticRegression(C=0.1, max_iter=4000))]),
    "mlp256": Pipeline([("sc", StandardScaler()), ("mlp", MLPClassifier((256,), alpha=1e-2, max_iter=300, early_stopping=True, random_state=0))]),
    "svm_rbf": Pipeline([("sc", StandardScaler()), ("pca", PCA(256, random_state=0)), ("svm", SVC(C=1.0, kernel="rbf", probability=False))]),
}
for name, pipe in configs.items():
    t0 = time.time()
    last = pipe.steps[-1][0]
    kw = {f"{last}__sample_weight": weights(tr)} if last in ("lr", "svm") else {}
    pipe.fit(X[tr], y[tr], **kw)
    s = pipe.decision_function(X[te]) if hasattr(pipe, "decision_function") else pipe.predict_proba(X[te])[:, 1]
    out = []
    for g in seen + ["chatterbox"]:
        m = (y[te] == 0) | (gen[te] == g)
        e, _ = eer(s[m], y[te][m]); out.append(f"{g} {e*100:5.1f}")
    print(f"{name:10s} {time.time()-t0:5.1f}s | " + " | ".join(out))
