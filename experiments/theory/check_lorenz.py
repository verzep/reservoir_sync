"""Exact nonlinear test family (docs/theory_notes.md, section 3.2, 4).

Lorenz source, r = (y, z), phi(s) = (s, h(s_3)), h' = -sech^2((s_3-m)/w) amplitude via c:

    y' = g(s) - k (y - s) + c (z - h(s))
    z' = h'(s_3) g_3(s) + D . (y - s) + E (z - h(s))

Readout N^T = (I, 0) is exact. With chi = z - h(y), the closed loop is exactly
    y' = g(y) + c chi,   chi' = a(y) chi,   a(y) = E - c_3 h'(y_3).
An imperfect linear readout psi = y + eps b z gives e(s) = eps b h(s).
"""

import multiprocessing as mp
import sys

import numpy as np


def g(s, sig=10.0, rho=28.0, bet=8 / 3):
    return np.array([sig * (s[1] - s[0]), s[0] * (rho - s[2]) - s[1], s[0] * s[1] - bet * s[2]])


def Dg(s, sig=10.0, rho=28.0, bet=8 / 3):
    return np.array([[-sig, sig, 0], [rho - s[2], -1, -s[0]], [s[1], s[0], -bet]])


class Fam:
    def __init__(self, E=-1.0, amp=0.5, m=27.0, w=4.0, k=5.0, D=0.3):
        self.E, self.amp, self.m, self.w, self.k = E, amp, m, w, k
        self.c3 = -1.0
        self.c = np.array([0.0, 0.0, self.c3])
        self.D = np.array([0.0, 0.0, D])
        A = np.zeros((4, 4))
        A[:3, :3] = -k * np.eye(3)
        A[:3, 3] = self.c
        A[3, :3] = self.D
        A[3, 3] = E
        self.A = A
        self.N = np.zeros((4, 3))
        self.N[:3, :3] = np.eye(3)

    def h(self, s3):  # h' = amp sech^2, so a = E - c3 h' = E + amp sech^2
        return self.amp * self.w * np.tanh((s3 - self.m) / self.w)

    def dh(self, s3):
        return self.amp / np.cosh((s3 - self.m) / self.w) ** 2

    def a(self, s3):
        return self.E - self.c3 * self.dh(s3)

    def f(self, x, s):
        y, z = x[:3], x[3]
        hs = self.h(s[2])
        gs = g(s)
        return np.concatenate([gs - self.k * (y - s) + self.c * (z - hs),
                               [self.dh(s[2]) * gs[2] + self.D @ (y - s) + self.E * (z - hs)]])

    def B(self, s):
        G = Dg(s)
        gs = g(s)
        dh = self.dh(s[2])
        d2h = -2 * self.amp / self.w * np.tanh((s[2] - self.m) / self.w) / np.cosh((s[2] - self.m) / self.w) ** 2
        Dhv = np.array([0, 0, dh])
        top = G + self.k * np.eye(3) - np.outer(self.c, Dhv)
        bot = d2h * gs[2] * np.array([0, 0, 1.0]) + dh * G[2] - self.D - self.E * Dhv
        return np.vstack([top, bot])

    def F(self, s):
        return np.vstack([np.eye(3), [0, 0, self.dh(s[2])]])


def rk4(fun, x, dt):
    k1 = fun(x); k2 = fun(x + dt / 2 * k1); k3 = fun(x + dt / 2 * k2); k4 = fun(x + dt * k3)
    return x + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)


def settle(dt=0.002, T=50.0, seed=0):
    rng = np.random.default_rng(seed)
    s = np.array([1.0, 1.0, 20.0]) + rng.normal(size=3)
    for _ in range(int(T / dt)):
        s = rk4(g, s, dt)
    return s


def spectrum_check(fam, T=1500.0, dt=0.002):
    """QR exponents of J along the driven orbit, and the check against source + <a>."""
    s = settle(dt)
    Y = np.eye(4)
    Ys = np.eye(3)
    logs, logs_s = np.zeros(4), np.zeros(3)
    n = int(T / dt)
    a_int = 0.0
    trB = 0.0
    fd_err = 0.0
    x = np.concatenate([s, [fam.h(s[2])]])
    for i in range(n):
        J = fam.A + fam.B(s) @ fam.N.T
        G = Dg(s)
        if i % 500 == 0:  # B and the driven solution against finite differences and exact phi
            eps = 1e-6
            FD = np.column_stack([(fam.f(x, s + eps * e) - fam.f(x, s - eps * e)) / (2 * eps) for e in np.eye(3)])
            fd_err = max(fd_err, np.abs(FD - fam.B(s)).max())
        a_int += fam.a(s[2]) * dt
        trB += np.trace(fam.N.T @ fam.B(s)) * dt
        # Euler-free: frozen J over one step, RK4 on the frozen-in-time matrices is enough at this dt
        Y = Y + dt * J @ (Y + dt / 2 * J @ (Y + dt / 3 * J @ (Y + dt / 4 * J @ Y)))
        Ys = Ys + dt * G @ (Ys + dt / 2 * G @ (Ys + dt / 3 * G @ (Ys + dt / 4 * G @ Ys)))
        s = rk4(g, s, dt)
        x = np.concatenate([s, [fam.h(s[2])]])
        if (i + 1) % 25 == 0:
            Y, R = np.linalg.qr(Y); logs += np.log(np.abs(np.diag(R)))
            Ys, R = np.linalg.qr(Ys); logs_s += np.log(np.abs(np.diag(R)))
    lamJ = np.sort(logs / T)[::-1]
    lamS = np.sort(logs_s / T)[::-1]
    cle = np.linalg.eigvals(fam.A)
    print(f"  J exps {np.round(lamJ, 3)}  source {np.round(lamS, 3)}  <a> = {a_int / T:.3f}  CLE {np.round(cle, 3)}")
    print(f"  sum rule: sum J {lamJ.sum():.3f} vs tr A + <tr N^T B> {np.trace(fam.A) + trB / T:.3f}; "
          f"sum perp {lamJ.sum() - lamS.sum():.3f}; B finite-diff err {fd_err:.1e}")


def gains(fam, T=60.0, dt=0.01):
    """Restricted small-gain and direct bound for the family, along one orbit."""
    from scipy.linalg import expm
    s = settle()
    Fs = []
    for _ in range(int(T / dt)):
        s = rk4(g, s, dt)
        Fs.append(fam.F(s))
    Fs = np.array(Fs)
    NA = fam.N.T @ fam.A
    best = None
    lags = np.arange(0, 2000)
    P = np.array([expm(fam.A * l * dt) for l in lags])
    NAP = NA @ P  # (lag, 3, 4)
    kappa = -np.linalg.eigvals(fam.A).real.max()
    for sigma in [0.0, 0.25 * kappa, 0.5 * kappa]:
        vals = []
        for t in range(len(Fs) - 1, len(Fs) - 1 - 2000, -40):
            ls = lags[lags <= t]
            nrm = np.linalg.norm(NAP[ls] @ Fs[t - ls], 2, axis=(1, 2))
            vals.append(np.sum(nrm * np.exp(sigma * ls * dt)) * dt)
        print(f"  sigma={sigma:.3f}: weighted gain of R = {max(vals):.3f}")
    K = np.array([[0, 0, 0, 1.0]]).T
    c = np.linalg.norm([np.linalg.norm(expm(fam.A * t), 2) * np.exp(kappa * t) for t in np.arange(0, 20, 0.05)], np.inf)
    dirb = -kappa + c * max(np.linalg.norm(F @ NA @ K, 2) for F in Fs)
    print(f"  kappa={kappa:.3f}, C={c:.2f}, direct bound lambda_perp <= {dirb:.3f}; true sup a = {fam.E + fam.amp:.3f}")


def free_chi(args):
    """Closed loop with imperfect linear readout psi = y + eps b z; statistics of chi = z - h(y)."""
    E, amp, eps, T, seed = args
    fam = Fam(E=E, amp=amp)
    b = np.array([1.0, 1.0, 1.0]) / np.sqrt(3)
    dt = 0.002
    s = settle(dt, seed=seed)
    x = np.concatenate([s, [fam.h(s[2])]])
    fun = lambda x: fam.f(x, x[:3] + eps * b * x[3])
    n = int(T / dt)
    chi = np.empty(n // 5)
    a_vals = np.empty(n // 5)
    for i in range(n):
        x = rk4(fun, x, dt)
        if i % 5 == 0:
            chi[i // 5] = x[3] - fam.h(x[2])
            a_vals[i // 5] = fam.a(x[2])
        if not np.all(np.isfinite(x)) or np.abs(x).max() > 1e4:
            return dict(E=E, amp=amp, eps=eps, seed=seed, diverged=True, t=i * dt)
    chi = np.abs(chi[len(chi) // 10 :])
    qs = np.quantile(chi, [0.5, 0.9, 0.99, 0.999, 0.9999])
    return dict(E=E, amp=amp, eps=eps, seed=seed, diverged=False, qs=qs.tolist(), sup=float(chi.max()),
                z3max=float(x[2]))


def moments(E, amp, T_w=20.0, total=20000.0, dt=0.004, seed=1):
    fam = Fam(E=E, amp=amp)
    s = settle(dt, seed=seed)
    m = int(T_w / dt)
    n = int(total / T_w)
    I = np.empty(n)
    for j in range(n):
        acc = 0.0
        for _ in range(m):
            s = rk4(g, s, dt)
            acc += fam.a(s[2]) * dt
        I[j] = acc
    out = {}
    for q in [0.5, 1, 2, 3, 4, 6, 8]:
        mx = (q * I).max()
        out[q] = (mx + np.log(np.mean(np.exp(q * I - mx)))) / T_w
    return I.mean() / T_w, out


if __name__ == "__main__":
    print("== Spectrum and sum rule")
    for E, amp in [(-1.0, 0.5), (-1.0, 3.0), (2.0, 0.5)]:
        print(f" E={E} amp={amp}")
        fam = Fam(E=E, amp=amp)
        spectrum_check(fam)
    print("== Gains")
    for E, amp in [(-3.0, 0.5), (-1.0, 0.5)]:
        print(f" E={E} amp={amp}")
        gains(Fam(E=E, amp=amp))
    print("== Moment exponents L(q) (window 20)")
    for E, amp in [(-1.0, 0.5), (-2.0, 3.0), (-1.0, 3.0)]:
        m, L = moments(E, amp)
        print(f" E={E} amp={amp}: mean a {m:.3f}; L(q): " + ", ".join(f"{q}:{v:.3f}" for q, v in L.items()))
    print("== Tube and bubbling: |chi| quantiles (50,90,99,99.9,99.99) and sup")
    tasks = [(E, amp, eps, 1000.0, 0) for E, amp in [(-1.0, 0.5), (-0.5, 0.25), (-2.0, 1.0), (-1.0, 3.0)] for eps in [1e-4, 1e-3, 1e-2]]
    with mp.Pool(10) as p:
        for r in p.imap(free_chi, tasks):
            if r["diverged"]:
                print(f" E={r['E']} amp={r['amp']} eps={r['eps']}: diverged at t={r['t']:.1f}")
            else:
                print(f" E={r['E']} amp={r['amp']} eps={r['eps']}: " + " ".join(f"{q:.2e}" for q in r["qs"]) + f" sup {r['sup']:.2e}")
