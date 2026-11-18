#!/usr/bin/env python3
"""Measure the frozen frontend's forward latency on this laptop, CPU and MPS.

Real-time factor = forward time / audio seconds. A streaming detector re-scores a sliding
window every hop, so CPU seconds per call second = latency / hop, and streams per core is
the reciprocal. That is the honest capacity number, not 1/RTF.
"""
import json, os, sys, time
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
from pramaan.frontend import Frontend
from pramaan.config import HOP_S

OUT = os.path.join(ROOT, "eval", "results", "latency.json")


def bench(device, window_s, n=15):
    fe = Frontend(device=device)
    x = np.random.default_rng(0).standard_normal(int(window_s * 16000)).astype(np.float32) * 0.1
    for _ in range(3):
        fe.embed(x)
    ts = []
    for _ in range(n):
        t0 = time.perf_counter(); fe.embed(x); ts.append(time.perf_counter() - t0)
    med = float(np.median(ts))
    return dict(device=fe.device, window_s=window_s, median_ms=med * 1000, rtf=med / window_s,
                p90_ms=float(np.percentile(ts, 90)) * 1000)


def main():
    rows = []
    for dev in ["mps", "cpu"]:
        for w in [1.5, 2.0, 4.0]:
            r = bench(dev, w); rows.append(r)
            print(f"{r['device']:4s} {w:.1f}s window: {r['median_ms']:.1f} ms  RTF {r['rtf']:.4f}")
    cpu4 = [r for r in rows if r["device"] == "cpu" and r["window_s"] == 4.0][0]
    mps4 = [r for r in rows if r["device"] == "mps" and r["window_s"] == 4.0][0]
    cap = {}
    for name, r in [("cpu", cpu4), ("mps", mps4)]:
        for hop in [HOP_S, 1.0]:
            per_sec = r["median_ms"] / 1000 / hop
            cap[f"{name}_hop_{hop}"] = dict(hop_s=hop, cpu_seconds_per_call_second=per_sec,
                                            streams_per_core=1 / per_sec,
                                            cores_for_200_seats=int(np.ceil(200 * per_sec)))
    out = dict(rows=rows, capacity=cap, note="capacity assumes 100% seat concurrency, which is pessimistic")
    json.dump(out, open(OUT, "w"), indent=2)
    print(json.dumps(cap, indent=1))


if __name__ == "__main__":
    main()
