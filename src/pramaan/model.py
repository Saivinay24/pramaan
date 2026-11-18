"""The trainable part of Pramaan: a tiny head over the frozen frontend, plus calibration.

Frozen XLS-R does the representation work (Pascu et al., Interspeech 2024: a frozen SSL
frontend with a small head generalises out of domain far better than fine-tuning). The head
only draws a boundary, trains in seconds on CPU, and is the only thing that ever trains.

Calibration is isotonic regression fit on a held-out split that contains several generator
families. Cross-entropy heads are overconfident; isotonic re-maps raw scores to empirical
probabilities without assuming a sigmoid shape, which is what survives generator shift.
"""
import os, pickle
import numpy as np
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


class Head:
    """Standardise, then one logistic boundary over the full 2048-d embedding.

    Chosen by eval/head_sweep.py against PCA+LR, an MLP and an RBF-SVM: strong L2 (C=0.02)
    with per-family sample weights generalised best to the unseen cloner. Per-family weights
    matter: without them the easiest family (neural-codec resynthesis) dominates the loss
    and the boundary drifts away from the harder ones.
    """

    def __init__(self, C=0.02, seed=0):
        self.pipe = Pipeline([
            ("sc", StandardScaler()),
            ("lr", LogisticRegression(C=C, max_iter=4000, random_state=seed)),
        ])

    @staticmethod
    def family_weights(y, groups):
        g = np.where(np.asarray(y) == 0, "bona", np.asarray(groups).astype(str))
        w = np.ones(len(g))
        for k in set(g):
            w[g == k] = 1.0 / (g == k).sum()
        return w / w.mean()

    def fit(self, X, y, groups=None):
        w = self.family_weights(y, groups) if groups is not None else None
        self.pipe.fit(X, y, lr__sample_weight=w)
        return self

    def raw(self, X):
        """Log-odds of synthetic. Unbounded and deliberately uncalibrated."""
        return self.pipe.decision_function(np.atleast_2d(X))

    @property
    def n_trainable(self):
        lr = self.pipe.named_steps["lr"]
        return int(lr.coef_.size + lr.intercept_.size)


class IsotonicCalibrator:
    """Raw score -> P(synthetic), monotone, non-parametric, clipped away from 0 and 1."""

    def __init__(self, eps=0.01):
        self.iso = IsotonicRegression(out_of_bounds="clip", y_min=eps, y_max=1 - eps)
        self.fitted = False
        self.levels = np.array([0.5])

    def fit(self, scores, y):
        s, y = np.asarray(scores, float), np.asarray(y)
        if len(np.unique(y)) < 2:
            return self
        self.iso.fit(s, y)
        self.fitted = True
        # Isotonic regression on near-separable data is a step function with a handful of
        # distinct outputs. Those steps are the only probabilities this calibrator can ever
        # emit, so a threshold is only meaningful if it sits on one of them. Recorded here
        # because band_from_genuine() needs the step grid, not a continuous quantile.
        self.levels = np.unique(self.iso.predict(s))
        return self

    def predict_proba(self, scores):
        s = np.atleast_1d(np.asarray(scores, float))
        if not self.fitted:
            return np.full(len(s), 0.5)
        return self.iso.predict(s)


def band_from_genuine(p_genuine, levels, fpr_budget, human_quantile=0.90):
    """The Gate's commit band, derived from BONA FIDE calibrated scores alone.

    Ported from the parent repo's eval/select_operating_point.py, which measured on
    2026-09-03 that spoof score location does not transfer across cloners while genuine
    score location does. No spoof clip of any generator, seen or held out, informs this
    threshold, so a new cloner cannot leak into the operating point even in principle.
    The false-positive budget is the single stated design choice.

      tau_clone  the lowest calibrator step STRICTLY above the (1 - fpr_budget) quantile of
                 genuine probabilities. Strictly above matters: the isotonic floor is a point
                 mass, so a threshold placed on it would commit SYNTHETIC on every genuine
                 clip sitting exactly at the floor.
      tau_human  the human_quantile quantile of the same genuine probabilities, so that
                 share of genuine callers is cleared by the passive layer.

    Returns (tau_clone, tau_human). tau_clone = 1.0 means this channel and prefix never
    commit SYNTHETIC inside the budget, which is a refusal to decide, not a pass.
    """
    v = np.asarray(p_genuine, float)
    lv = np.sort(np.asarray(levels, float))
    q = float(np.quantile(v, 1.0 - fpr_budget))
    above = lv[lv > q]
    tau_clone = float(above[0]) if above.size else 1.0
    tau_human = float(np.quantile(v, human_quantile))
    if tau_human >= tau_clone:                      # keep the band ordered and non-empty
        below = lv[lv < tau_clone]
        tau_human = float(below[-1]) if below.size else 0.0
    return tau_clone, tau_human


def eer(scores, y):
    """Equal error rate and the threshold that achieves it. Higher score = more synthetic."""
    scores, y = np.asarray(scores, float), np.asarray(y)
    order = np.argsort(-scores)
    ys = y[order]
    n_pos, n_neg = int((ys == 1).sum()), int((ys == 0).sum())
    if n_pos == 0 or n_neg == 0:
        return float("nan"), float("nan")
    tp, fp = np.cumsum(ys == 1), np.cumsum(ys == 0)
    fnr, fpr = 1 - tp / n_pos, fp / n_neg
    i = int(np.nanargmin(np.abs(fnr - fpr)))
    return float((fnr[i] + fpr[i]) / 2), float(scores[order][i])


def auroc(scores, y):
    from sklearn.metrics import roc_auc_score
    y = np.asarray(y)
    if len(np.unique(y)) < 2:
        return float("nan")
    return float(roc_auc_score(y, scores))


def ece(p, y, n_bins=10):
    p, y = np.asarray(p, float), np.asarray(y, float)
    edges = np.linspace(0, 1, n_bins + 1)
    out = 0.0
    for i in range(n_bins):
        m = (p > edges[i]) & (p <= edges[i + 1]) if i else (p >= edges[i]) & (p <= edges[i + 1])
        if m.any():
            out += m.mean() * abs(y[m].mean() - p[m].mean())
    return float(out)


def save_bundle(path, **kw):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        pickle.dump(kw, f)


def load_bundle(path):
    with open(path, "rb") as f:
        return pickle.load(f)
