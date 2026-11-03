"""Checks of the linear-case claims in docs/theory_notes.md (section 3.1, 3.3, 1).

Linear reservoir, oscillator source, exact readout by construction. No integration except the circle example.
"""

import numpy as np
from scipy.integrate import quad
from scipy.linalg import null_space, solve_sylvester
from scipy.signal import place_poles


def setup(rng, n, om=1.0, sym=False, normal_margin=0.5):
    W = rng.normal(size=(n, n)) / np.sqrt(n)
    if sym:
        W = (W + W.T) / 2
    W = W - (np.max(np.linalg.eigvals(W).real) + normal_margin) * np.eye(n)
    L = np.array([[0.0, om], [-om, 0.0]])
    Phi = rng.normal(size=(n, 2))
    V = Phi @ L - W @ Phi
    return W, V, Phi, L


def random_exact_N(rng, Phi, scale=1.0):
    n = Phi.shape[0]
    N0 = Phi @ np.linalg.inv(Phi.T @ Phi)
    return N0 + scale * null_space(Phi.T) @ rng.normal(size=(n - 2, 2))


def perp_eigs(W, Phi, N):
    K = null_space(N.T)
    Q = np.eye(len(W)) - Phi @ N.T
    return np.linalg.eigvals(K.T @ Q @ W @ K)


def match(a, b):
    a, b = list(a), list(b)
    err = 0.0
    for x in a:
        j = int(np.argmin(np.abs(np.array(b) - x)))
        err = max(err, abs(b[j] - x))
        b.pop(j)
    return err


def check_factorization(rng, trials=200):
    fac, spec, detH = 0.0, 0.0, 0.0
    for _ in range(trials):
        n = rng.integers(4, 15)
        W, V, Phi, L = setup(rng, n)
        N = random_exact_N(rng, Phi, rng.uniform(0, 3))
        J = W + V @ N.T
        lam = np.linalg.eigvals(J)
        p = perp_eigs(W, Phi, N)
        spec = max(spec, match(np.concatenate([p, [1j, -1j]]), lam))
        z = rng.normal() + 1j * rng.normal()
        Rz = np.linalg.inv(z * np.eye(n) - W)
        T = N.T @ Rz @ V
        H = N.T @ Rz @ Phi
        fac = max(fac, np.linalg.norm(np.eye(2) - T - H @ (z * np.eye(2) - L)))
        ratio = np.prod(z - p) / np.prod(z - np.linalg.eigvals(W))
        detH = max(detH, abs(np.linalg.det(H) - ratio) / abs(ratio))
    print(f"factorization err {fac:.2e}; spectrum = source + zeros err {spec:.2e}; det H err {detH:.2e}")


def check_bode(rng, trials=30):
    worst = 0.0
    for _ in range(trials):
        n = rng.integers(4, 10)
        W, V, Phi, L = setup(rng, n)
        N = random_exact_N(rng, Phi, rng.uniform(0, 3))
        lam = np.linalg.eigvals(W + V @ N.T)
        rhs = np.sum(lam.real[lam.real > 1e-9])

        def integrand(w):
            T = N.T @ np.linalg.solve(1j * w * np.eye(n) - W, V)
            return np.log(abs(np.linalg.det(np.eye(2) - T)))

        pts = [-1.0, 1.0]
        I = sum(quad(integrand, a, b, limit=400)[0] for a, b in [(-5e3, -1), (-1, 1), (1, 5e3)]) if False else None
        # the integrand is even with log singularity at |w| = 1
        I = 2 * (quad(integrand, 0, 1, limit=400)[0] + quad(integrand, 1, 50, limit=400)[0]
                 + quad(integrand, 50, 1e5, limit=800)[0])
        # tail beyond 1e5: log|det(I-T)| ~ Re tr(-T), T ~ N^T V / (i w) + N^T W V / (i w)^2 is O(1/w^2)
        lhs = I / (2 * np.pi) + 0.5 * np.trace(N.T @ V)
        worst = max(worst, abs(lhs - rhs))
    print(f"Bode/Jensen identity max |lhs-rhs| = {worst:.2e}")


def winding(f, wmax=1e4, m=400001):
    w = np.tan(np.linspace(-np.pi / 2 + 1e-5, np.pi / 2 - 1e-5, m))
    w = w[np.abs(w) < wmax]
    v = np.array([f(x) for x in w[:: max(1, len(w) // 40000)]])
    return np.sum(np.angle(v[1:] / v[:-1])) / (2 * np.pi)


def check_nyquist_and_gain(rng, trials=300):
    bad_ny, n_uns = 0, 0
    cert, cert_viol, a_grid = 0, 0, [0.1, 0.3, 1.0, 3.0, 10.0]
    w_grid = np.concatenate([[0.0], np.logspace(-3, 3, 300)])
    for t in range(trials):
        n = rng.integers(4, 9)
        W, V, Phi, L = setup(rng, n)
        N = random_exact_N(rng, Phi, rng.uniform(0, 3))
        p = perp_eigs(W, Phi, N)
        uns = int(np.sum(p.real > 0))
        n_uns += uns > 0
        if t < 60:
            a = 1.0

            def f(w):
                return np.linalg.det((1j * w + a) * N.T @ np.linalg.solve(1j * w * np.eye(n) - W, Phi))

            wn = -winding(f)  # zeros in RHP minus poles in RHP (none) of (z+a)H, contour clockwise
            if abs(wn - uns) > 0.2:
                bad_ny += 1
        best = np.inf
        for a in a_grid:
            g = max(np.linalg.norm(N.T @ (W + a * np.eye(n)) @ np.linalg.solve(1j * w * np.eye(n) - W, Phi), 2)
                    for w in w_grid)
            best = min(best, g)
        if best < 1:
            cert += 1
            cert_viol += uns > 0
    print(f"Nyquist count mismatches {bad_ny}/60; unstable runs {n_uns}/{trials}; "
          f"small-gain certified {cert}, of which unstable {cert_viol}")


def check_pole_placement(rng, trials=100):
    worst = 0.0
    exact = 0.0
    for _ in range(trials):
        n = rng.integers(5, 12)
        W, V, Phi, L = setup(rng, n)
        target = rng.uniform(-5, 3, size=n - 2)  # includes unstable targets
        # quotient coordinates: pi = K0^T with K0 basis of Phi^perp, sigma0 = K0
        K0 = null_space(Phi.T)
        Abar = K0.T @ W @ K0
        Bbar = K0.T @ W @ Phi
        # sigma = K0 + Phi X; pi W sigma = Abar + Bbar X, so place eig(Abar - Bbar F) with X = -F
        target = target + 1e-3 * np.arange(n - 2)
        F = place_poles(Abar, Bbar, target, method="YT").gain_matrix
        X = -F
        K = K0 + Phi @ X  # the kernel of N^T
        # N^T Phi = I and N^T K = 0
        M = np.hstack([Phi, K])
        N = (np.linalg.inv(M)[:2, :]).T
        exact = max(exact, np.linalg.norm(N.T @ Phi - np.eye(2)))
        spec = np.linalg.eigvals(W + V @ N.T)
        worst = max(worst, match(np.concatenate([target, [1j, -1j]]), spec))
    print(f"pole placement (d=2): max spectrum error {worst:.2e}; max |N^T Phi - I| {exact:.2e}")


def check_geometry(rng, trials=300):
    # symmetric W with min-norm N: compression, lambda_perp <= lambda_max(W)
    gap = -np.inf
    for _ in range(trials):
        n = rng.integers(4, 15)
        W, V, Phi, L = setup(rng, n, sym=True)
        N = Phi @ np.linalg.inv(Phi.T @ Phi)
        gap = max(gap, perp_eigs(W, Phi, N).real.max() - np.linalg.eigvals(W).real.max())
    print(f"symmetric W, min-norm N: max(lambda_perp - lambda_max(W)) = {gap:.2e} (must be <= 0)")
    # energy bound for any exact N
    viol = 0
    slack = []
    for _ in range(trials):
        n = rng.integers(4, 15)
        W, V, Phi, L = setup(rng, n)
        N = random_exact_N(rng, Phi, rng.uniform(0, 2))
        K = null_space(N.T)
        R = N @ np.linalg.inv(N.T @ N)
        Dz = Phi - R
        mu2 = np.linalg.eigvalsh((K.T @ (W + W.T) @ K) / 2).max()
        bound = mu2 + np.linalg.norm(Dz, 2) * np.linalg.norm(N.T @ W @ K, 2)
        lp = perp_eigs(W, Phi, N).real.max()
        viol += lp > bound + 1e-9
        slack.append(bound - lp)
    print(f"energy bound violations {viol}/{trials}; median slack {np.median(slack):.2f}")
    # dual of Prop 4: range(Phi) W-invariant (so QV = 0), kernel not invariant
    n = 6
    w, U = np.linalg.eig(W := (lambda A: A - (np.linalg.eigvals(A).real.max() + 0.5) * np.eye(n))(rng.normal(size=(n, n))))
    real_vecs = []
    idx = np.argsort(np.abs(w.imag))
    # build a real 2-d invariant subspace
    i = idx[0] if abs(w[idx[0]].imag) > 1e-9 else None
    if i is None:
        reals = [j for j in range(n) if abs(w[j].imag) < 1e-9][:2]
        Phi = U[:, reals].real
    else:
        Phi = np.column_stack([U[:, i].real, U[:, i].imag])
    Phi = np.linalg.qr(Phi)[0]
    L = np.array([[0.0, 1.0], [-1.0, 0.0]])
    V = Phi @ L - W @ Phi
    N = random_exact_N(rng, Phi, 1.0)
    K = null_space(N.T)
    print("dual: |QV| =", f"{np.linalg.norm((np.eye(n) - Phi @ N.T) @ V):.2e}",
          "|N^T W K| =", f"{np.linalg.norm(N.T @ W @ K):.2f}",
          "match of lambda_perp in eig(W):", f"{match(perp_eigs(W, Phi, N), list(np.linalg.eigvals(W))):.2e}")


def check_paper_counterexample():
    A = np.array([[1.0, 10.0], [-1.0, -3.0]])
    V = np.array([[-10.0], [2.0]])
    F = np.array([[0.0], [1.0]])
    N = np.array([[0.0], [1.0]])
    print("counterexample: N^T A F + N^T V =", (N.T @ A @ F + N.T @ V).item(), "(G = -1);",
          "zero of H from Q A:", ((np.eye(2) - F @ N.T) @ A)[0, 0])


def check_chaotic_family():
    # same driven block spectrum, arbitrary E = lambda_perp
    for E in [-2.0, 0.5, 3.0]:
        tr, det = -4.0, 13.0  # driven eigenvalues -2 +- 3i
        k = E - tr
        CD = -k * E - det
        Mat = np.array([[-k, 1.0], [CD, E]])
        print(f"E={E}: driven eigs {np.round(np.linalg.eigvals(Mat), 6)}, lambda_perp = {E}")


def check_circle(rng):
    # A_s = unit circle; exact on the circle only. Source tangent has radial exponent -2.
    n = 6
    W, V, Phi, L = setup(rng, n)
    N = random_exact_N(rng, Phi, 0.5)
    lam = np.linalg.eigvals(W + V @ N.T)
    # F solves F' = W F + V - F G along the cycle, in the rotating frame G = L0 - 2 e_r e_r^T.
    # Bounded periodic solution by Floquet: integrate forward (kappa > 0, G bounded) until periodic.
    def G(t):
        e = np.array([np.cos(t), np.sin(t)])
        return np.array([[0.0, 1.0], [-1.0, 0.0]]) * (-1) * (-1) - 2 * np.outer(e, e)
    dt = 2e-3
    F = Phi.copy()
    t = 0.0
    for _ in range(int(60 / dt)):
        f = lambda t, F: W @ F + V - F @ G(t)
        k1 = f(t, F); k2 = f(t + dt / 2, F + dt / 2 * k1); k3 = f(t + dt / 2, F + dt / 2 * k2); k4 = f(t + dt, F + dt * k3)
        F = F + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4); t += dt
    e_t = np.array([-np.sin(t), np.cos(t)]) if False else None
    print("circle: closed-loop eigs nearest 0:", np.round(sorted(lam, key=abs)[:2], 6),
          "| source exponents 0, -2 | spectral abscissa W", round(np.linalg.eigvals(W).real.max(), 3))
    print("circle: N^T F at end of run =\n", np.round(N.T @ F, 3))


if __name__ == "__main__":
    rng = np.random.default_rng(0)
    check_factorization(rng)
    check_bode(rng)
    check_nyquist_and_gain(rng)
    check_pole_placement(rng)
    check_geometry(rng)
    check_paper_counterexample()
    check_chaotic_family()
    check_circle(rng)
