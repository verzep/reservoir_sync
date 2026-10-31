"""Circle example with a smooth map (error 2), and steering lambda_perp through near-null data directions."""

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import numpy as np

from check_linear import random_exact_N, setup
from reservoir_sync.driven import drive, settle_source
from reservoir_sync.lyapunov import closed_loop_exponents_driven, extra_exponents, source_exponents
from reservoir_sync.readout import fit_readout, nrmse
from reservoir_sync.reservoirs import random_reservoir
from reservoir_sync.sources import SOURCES


def circle():
    rng = np.random.default_rng(3)
    n = 6
    W, V, Phi, L = setup(rng, n, normal_margin=4.0)
    N = random_exact_N(rng, Phi, 0.5)
    lam = np.linalg.eigvals(W + V @ N.T)

    def G(t):  # s = (cos t, -sin t) solves s' = L s; radial contraction -2 at rho = 1
        e = np.array([np.cos(t), -np.sin(t)])
        return L - 2 * np.outer(e, e)

    dt = 2e-3
    F, t = Phi.copy(), 0.0
    f = lambda t, F: W @ F + V - F @ G(t)
    for _ in range(int(30 / dt)):
        k1 = f(t, F); k2 = f(t + dt / 2, F + dt / 2 * k1); k3 = f(t + dt / 2, F + dt / 2 * k2); k4 = f(t + dt, F + dt * k3)
        F = F + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4); t += dt
    e_r = np.array([np.cos(t), -np.sin(t)])
    e_t = np.array([-np.sin(t), -np.cos(t)])
    print("closed-loop eigenvalues:", np.round(sorted(lam, key=lambda z: -z.real), 4))
    print("source exponents on circle: 0 (tangent), -2 (radial); kappa =", -np.linalg.eigvals(W).real.max())
    print("|N^T F e_t - e_t| =", np.linalg.norm(N.T @ F @ e_t - e_t), " |N^T F e_r - e_r| =", np.linalg.norm(N.T @ F @ e_r - e_r))


def steer(name="rossler", gamma=5.0, rho=0.9, sig=0.05, seed=1, alphas=(0, 1, 3, 10, 30, 100, 300, 1000)):
    source = SOURCES[name]()
    dt = min(0.01, 0.25 / gamma)
    res = random_reservoir(200, 3, "tanh", rho, sig, 0.5, gamma, None, seed)
    s0 = settle_source(source, dt, 50.0, seed=seed)
    nw, nt = int(20 / dt), int(100 / dt)
    run = drive(source, res, s0, np.zeros(200), dt, nw + 2 * nt)
    train, test = run[nw : nw + nt + 1], run[nw + nt :]
    N0 = fit_readout(train.R, train.S, 1e-6)
    Rc = train.R - train.R.mean(0)
    U, sv, Vt = np.linalg.svd(train.R, full_matrices=False)
    print("singular values of data (first, 50th, 100th, last):", sv[[0, 49, 99, 199]])
    lams = source_exponents(source, train.S[-1], dt, int(200 / dt))
    rng = np.random.default_rng(0)
    for trial in range(3):
        D = Vt[120:].T @ rng.normal(size=(80, 3))  # 80 weakest data directions
        D /= np.linalg.norm(D)
        for a in alphas:
            N = N0 + a * np.linalg.norm(N0) / 100 * D
            lam = closed_loop_exponents_driven(source, res, N, train.S[-1], train.R[-1], dt, int(150 / dt), 6)
            e = extra_exponents(lam, lams)
            print(f"trial {trial} |dN|/|N0|={a / 100:.2f}: train NRMSE {nrmse(train.S, train.R @ N):.2e} test {nrmse(test.S, test.R @ N):.2e} lambda_perp {e[0]:.3f}", flush=True)


if __name__ == "__main__":
    circle()
    steer()
