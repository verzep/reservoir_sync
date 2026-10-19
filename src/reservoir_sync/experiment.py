"""One train / test / diagnose run, shared by the experiment scripts.

For one source and one random reservoir:

1. drive the reservoir (washout, train, test segments) and fit the readout;
2. field errors on the train and test segments (e, e_dot, feedback, g_hat - g);
3. free-running prediction from the end of training (valid time);
4. Lyapunov spectra: source, conditional (CLEs), closed loop along the
   synchronized trajectory and along the free run;
5. the invariance leak of ker N^T and a generalized-synchronization check
   (two reservoirs from different initial states, same drive).
"""

import time
from dataclasses import asdict, dataclass

import numpy as np

from .closed_loop import field_errors, run_autonomous, summarize_field_errors, valid_time
from .driven import DrivenRun, drive, joint_field, settle_source
from .integrate import simulate
from .lyapunov import (
    closed_loop_exponents_driven,
    closed_loop_exponents_free,
    conditional_exponents,
    extra_exponents,
    source_exponents,
)
from .readout import fit_readout, nrmse
from .reservoirs import random_reservoir
from .sources import SOURCES
from .transverse import invariance_leak


@dataclass
class Config:
    source: str = "lorenz"
    kind: str = "tanh"
    n: int = 200
    spectral_radius: float = 0.9
    input_scale: float = 0.05
    bias_scale: float = 0.5
    gamma: float = 1.0
    density: float | None = None
    beta: float = 1e-6
    seed: int = 0
    dt: float = 0.01
    t_washout: float = 20.0
    t_train: float = 100.0
    t_test: float = 25.0
    t_lyap: float = 200.0
    k: int = 10
    leak_stride: int = 20


def _steps(t, dt):
    return int(round(t / dt))


def _finite_list(x):
    return [None if not np.isfinite(v) else float(v) for v in np.asarray(x)]


def run(cfg: Config) -> dict:
    t_start = time.time()
    source = SOURCES[cfg.source]()
    dt = min(cfg.dt, 0.25 / cfg.gamma)  # keep gamma * dt small for RK4
    res = random_reservoir(
        cfg.n, source.dim, cfg.kind, cfg.spectral_radius, cfg.input_scale,
        cfg.bias_scale, cfg.gamma, cfg.density, cfg.seed,
    )
    s0 = settle_source(source, dt, 50.0, seed=cfg.seed)
    n_wash, n_train, n_test = (_steps(t, dt) for t in (cfg.t_washout, cfg.t_train, cfg.t_test))
    full = drive(source, res, s0, np.zeros(res.n), dt, n_wash + n_train + n_test)
    i_end = n_wash + n_train
    train, test = full[n_wash : i_end + 1], full[i_end:]

    N = fit_readout(train.R, train.S, cfg.beta)
    out = {"config": asdict(cfg), "dt_used": dt}
    out["train_nrmse"] = nrmse(train.S, train.R @ N)
    out["test_nrmse_driven"] = nrmse(test.S, test.R @ N)
    out["train_field"] = summarize_field_errors(field_errors(source, res, N, train))
    out["test_field"] = summarize_field_errors(field_errors(source, res, N, test))

    with np.errstate(all="ignore"):
        free = run_autonomous(res, N, train.R[-1], dt, n_test)
    out["valid_time"] = valid_time(test.S, free @ N, dt)

    # generalized synchronization: a second reservoir copy from a random state
    rng = np.random.default_rng(cfg.seed + 1000)
    r_other = rng.uniform(-1, 1, res.n)
    z = simulate(
        joint_field(source, res), np.concatenate([full.S[n_wash], r_other]), dt, n_train
    )
    other = DrivenRun(dt, z[:, : source.dim], z[:, source.dim :])
    out["gs_distance_final"] = float(np.linalg.norm(other.R[-1] - train.R[-1]))
    out["gs_distance_initial"] = float(np.linalg.norm(r_other - full.R[n_wash]))

    n_lyap = _steps(cfg.t_lyap, dt)
    s_sync, r_sync = train.S[-1], train.R[-1]
    lam_src = source_exponents(source, s_sync, dt, n_lyap)
    lam_cle = conditional_exponents(source, res, s_sync, r_sync, dt, n_lyap, cfg.k)
    lam_cl_driven = closed_loop_exponents_driven(source, res, N, s_sync, r_sync, dt, n_lyap, cfg.k)
    lam_cl_free = closed_loop_exponents_free(res, N, r_sync, dt, n_lyap, cfg.k)
    out["lyap_source"] = _finite_list(lam_src)
    out["lyap_cle"] = _finite_list(lam_cle)
    out["lyap_closed_driven"] = _finite_list(lam_cl_driven)
    out["lyap_closed_free"] = _finite_list(lam_cl_free)
    out["valid_time_lyap"] = out["valid_time"] * float(lam_src[0])
    # rate condition for a differentiable synchronization map
    out["smooth_sync_condition"] = bool(lam_cle[0] < lam_src[-1])
    extra = extra_exponents(lam_cl_driven, lam_src)
    out["lambda_perp_driven"] = float(extra[0]) if extra.size else None
    extra = extra_exponents(lam_cl_free, lam_src)
    out["lambda_perp_free"] = float(extra[0]) if extra.size and np.isfinite(extra[0]) else None

    stride = slice(None, None, cfg.leak_stride)
    out["invariance_leak"] = invariance_leak(res, N, train.R[stride], train.S[stride])
    out["seconds"] = time.time() - t_start
    return out
