"""Attractor statistics, long-run exponents and integration windows of the sources.

    python experiments/calibrate_sources.py --workers 20 --out results/source_scan/calibration.json

For each source: mean and std per component, the dominant period (peak of the
power spectrum), the fastest rate on the attractor (99.9th percentile of the
spectral norm of Dg), and the exponents at step dt and dt / 2. The metadata
values of dysts (chaotic_attractors.json) are listed for comparison.
"""

import os

for var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(var, "1")

import argparse
import json
import multiprocessing as mp
from pathlib import Path

import numpy as np

from reservoir_sync.integrate import simulate
from reservoir_sync.lyapunov import source_exponents
from reservoir_sync.sources import SOURCES

DYSTS_SPECTRA = {  # lyapunov_spectrum_estimated in dysts/data/chaotic_attractors.json
    "lorenz": [1.091, 0.030, -14.916],
    "rossler": [0.0763, 0.0075, -5.741],
    "shimizu_morioka": [0.0440, -0.0000, -1.410],
    "sprott_jerk": [0.0674, -0.0008, -2.135],
    "genesio_tesi": [0.0997, 0.0004, -0.528],
    "arneodo": [0.2429, -0.0006, -1.217],
    "aizawa": [0.0895, 0.0203, -0.309],
    "hadley": [0.3117, -0.0011, -0.427],
    "lorenz84": [1.047, -0.045, -2.252],
    "rucklidge": [0.1829, -0.0039, -3.215],
    "halvorsen": [0.586, -0.032, -4.688],
    "thomas": [0.759, 0.057, -6.422],
    "chen": [2.047, -0.050, -11.842],
    "qi_chen": [3.888, 0.134, -43.836],
    "lu_chen": [0.665, 0.145, -22.570],
    "dadras": [0.473, 0.006, -11.158],
    "moore_spiegel": [0.407, -0.022, -1.198],
    "hyper_lorenz": [0.293, 0.247, 0.047, -13.118],
    "lorenz_stenflo": [0.449, 0.026, -2.736, -3.421],
    "hyper_xu": [1.042, 0.207, -0.003, -13.698],
}


def calibrate(name):
    source = SOURCES[name]()
    # first pass: a step from the fastest rate along a short run
    dt = 2e-3
    s = simulate(source.g, source.s0, dt, 100000)[50000:]
    if not np.all(np.isfinite(s)):
        return {"name": name, "error": "diverged at dt=2e-3"}
    rates = np.array([np.linalg.norm(source.Dg(x), 2) for x in s[::20]])
    fast = float(np.quantile(rates, 0.999))
    dt = min(0.01, 0.2 / fast)
    # dominant period over a run of many cycles
    s0 = s[-1]
    guess = abs(np.mean(source.g(s[:1000]) ** 2)) ** 0.5
    n_steps = min(2_000_000, int(round(2000.0 / dt)))
    traj = simulate(source.g, s0, dt, n_steps)
    x = traj[n_steps // 10 :]
    mean, std = x.mean(0), x.std(0)
    # stationarity: means of the two halves, in stds
    half = len(x) // 2
    drift = float(np.max(np.abs(x[:half].mean(0) - x[half:].mean(0)) / std))
    power = sum(np.abs(np.fft.rfft(c - c.mean())) ** 2 / np.var(c) for c in x.T)
    freqs = np.fft.rfftfreq(len(x), dt)
    period = float(1 / freqs[1:][np.argmax(power[1:])])
    t_lyap = 5000.0
    lam = source_exponents(source, traj[-1], dt, min(2_000_000, int(t_lyap / dt)))
    lam2 = source_exponents(source, traj[-1], dt / 2, min(2_000_000, int(t_lyap / (dt / 2))))
    return {
        "name": name, "dim": source.dim, "mean": mean.tolist(), "std": std.tolist(),
        "drift": drift, "period": period, "fast_rate": fast, "dt": dt,
        "lyap": lam.tolist(), "lyap_half_dt": lam2.tolist(),
        "t_lyap_used": min(2_000_000, int(t_lyap / dt)) * dt,
        "dysts": DYSTS_SPECTRA.get(name), "g_rms": float(guess),
    }


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--workers", type=int, default=20)
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()
    with mp.get_context("spawn").Pool(a.workers) as pool:
        rows = pool.map(calibrate, sorted(SOURCES))
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps({r["name"]: r for r in rows}, indent=1))
    for r in rows:
        if "error" in r:
            print(r["name"], r["error"])
            continue
        print(f"{r['name']:16s} d={r['dim']} dt={r['dt']:.4f} T={r['period']:7.3f} fast={r['fast_rate']:7.1f} drift={r['drift']:.2f} "
              f"lyap={np.round(r['lyap'], 3)} half_dt={np.round(r['lyap_half_dt'], 3)} dysts={r['dysts']}")


if __name__ == "__main__":
    main()
