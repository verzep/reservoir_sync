# Theory notes: what can be proved about closing the loop

Labels: PROVED (full proof here), SKETCH, CONJECTURE, FALSE. "Checked" means a numerical test on uranus; scripts are in `experiments/theory/`. Nothing here has been refereed. Proofs are mine and unreviewed.

Notation. A = A_c, B = B_c along the driven orbit, G = Dg(s(t)), F = Dphi(s(t)) when it exists, C(t) = Dpsi(r(t)) (= N^T for a linear decoder), Q = I - F C, J = A + B C, K(t,tau) = C(t) Phi(t,tau) B(tau), with ||Phi(t,tau)|| <= c e^{-kappa(t-tau)}.

**Short version.**
1. The paper has three errors, all repairable (section 1).
2. The transverse dynamics are zero dynamics. I - K factorizes exactly, in the nonlinear time-varying case, into a source-tangent factor and a reduced filter. This gives the right restricted gain, which certifies stability on tests where the naive gain cannot (section 3). The linear part of this picture is now mostly known (Saqib & Padoan 2026); the time-varying and non-differentiable forms appear new.
3. No closed form in (lambda_perp, largest CLE, loop gain) exists, and no function of CLEs and reconstruction error can decide stability, including for chaotic sources with non-differentiable phi (section 3.5).
4. Imperfect reconstruction: three theorems, none covering generic non-differentiable reservoirs on non-hyperbolic sources. Non-uniform transverse stability provably does not give an O(e) sup bound in general (section 4).

## 1. Audit of Section 3

**Prop. 1: correct.** Uniform contraction is not used. Solutions need only exist on M.

**Prop. 2: proof correct line by line.** Checked: segment averaging on the compact convex hull, robustness of contraction on (-inf,t], dominated convergence, N^T y = xi, both exponent bounds. Notes:
- A_s must be invariant in both time directions. Implicit in the paper.
- "Gain exactly one" should read "eigenvalue one": K xi = xi says nothing about the operator norm.
- Assumption 3 requires contraction on *every* orbit in A_s, including embedded fixed points and periodic orbits. The numerics measure the largest CLE for the natural measure, which does not verify the assumption.
- dim D is not constant on Lorenz: at the origin g = 0 and D has dimension one. "Constant dimension along the orbit" holds a.e., not on all of A_s.
- Extension to tempered contraction: not obtained. y is defined and solves y' = Jy for tempered xi, but N^T y = xi uses the limit r_eps - r, whose perturbation of A has only a continuity modulus. With phi Holder and unstable directions the perturbation decays backward and a tempered argument looks feasible (SKETCH, not done). Open.

**Spectrum claim: correct** for an ergodic measure and measurable invariant E, with the quotient norm (block-triangular cocycle). The identification of ker N^T with the quotient for k = d needs a tempered angle between E and ker N^T.

**ERROR 1 (Prop. 3, "E = TM"): false as stated.** E is built from backward-bounded directions, so it excludes all directions with negative exponents. For Lorenz k = 2 and dim TM = 3. Correct: E is contained in Im Dphi, a larger J-invariant bundle. Saqib & Padoan do not hit this because their assumptions make the exosystem neutral on its set (their A3 and A7), so range Pi is all of it.

**ERROR 2 (Prop. 3, eq. differential_inverse): N^T Dphi = I does not follow from exact reconstruction on A_s.** Differentiating gives it only on the tangent cone of A_s.
- FALSE, by example. Attracting circle (rho radial exponent -2, angular speed 1), linear reservoir with W Pi + V = Pi L0, N^T Pi = I. Reconstruction on A_s is exact. The closed-loop spectrum contains +-i, i.e. 0, 0, while the source has 0, -2. Checked with kappa = 4 > 2, so a smooth phi exists: |N^T F e_t - e_t| = 3.5e-12 and |N^T F e_r - e_r| = 0.70.
- **This is a live effect on real trained readouts, not a formality.** In rate-condition tanh runs (gamma = 20, rho = 0.5; Rössler all six, Lorenz sigma = 0.1 two) F was integrated along the orbit: |(N^T F - I) Q_2| < 5e-4 and |(N^T F - I) g|/|g| < 5e-4, where Q_2 is the leading two source directions, while |(N^T F - I) on the remaining direction| = 0.49 to 3.5 (Rössler) and 4.3 to 9.3 (Lorenz). So Prop. 2 holds to three decimals with an approximate readout, and N^T F = I fails on the stable direction even when phi is smooth. Consequently QA computed with a right inverse from F does not match J on these runs (examples: J third exponent -3.85 against QA top +0.28; -1.54 against -7.36). **The operator to use on trained readouts is Q_E J of 3.3, not QA of Prop. 3.** Also: only 7 of 21 Rössler rate runs have a J exponent within 0.5 of -5.37 (median distance 1.24), and 3 of 4 on Lorenz. With the bulk of exponents nearby, "within 0.5" is a weak test.
- Repair (PROVED): assume exactness on a neighbourhood, as in Bizyaeva et al. Prop. III.1 where the exact identity holds on X, or assume the tangent cones of A_s span R^d (a C^1 function vanishing on X has derivative vanishing on the tangent cone of X).
- With the repair, the computation in Prop. 3 is correct and needs only a bounded F solving F' = AF + B - FG with N^T F = I.

**ERROR 3 (Section 4, "only if" kernel invariance): false as a spectral claim.** QB = 0 also makes the transverse exponents conditional ones (3.4), without invariance. Checked: |QV| = 7e-15, |N^T W K| = 6.3, lambda_perp in spec(W) to 3e-15. Oishi et al. Theorem 1 has the linear case.

**Rate condition is not necessary (PROVED, checked).** The paper's Remark and J. Hart's heuristic say a direction with exponent below -kappa need not be reproduced. "Need not" is right, but failure is not forced: in family (F) of 3.2, kappa = 1.08 and J still has exponent -14.57 exactly, because phi is smooth by construction. Checked: J exponents (0.906, -0.002, -0.878, -14.57).

**Prop. 4: correct but very restrictive.** N^T A = M(t) N^T says the decoded variable obeys a closed equation; in the linear case shat' = L shat + N^T V (s - shat), a **Luenberger observer**. It is a separation principle for surrogates containing a model copy.

**Counterexample of Section 4: correct, but its attractor is a point.** A chaotic exact version is (F) in 3.2. Saqib & Padoan Sec. V-A have the sinusoidal one.

**Linear reservoir + chaos (PROVED; known).** s = T*s forces T(iw) = I on the spectral support; T is rational and strictly proper, so the support is finite. Saqib & Padoan Cor. 7 state the same restriction via a linear internal model. So eq. linear_fiber_relations is vacuous for chaotic sources.

Other sections checked and found correct: g_error_decomposition, affine forms, training_residual_identity, dmd_result, off_manifold_g_error, Lemma y = r' for xi = g.

## 2. General C^1 decoder

No reservoir structure is used: only f C^1, phi continuous mapping orbits to driven solutions, and uniform contraction for Prop. 2. All results hold for any synchronized surrogate.

**PROVED (same proofs).** Prop. 1 with psi phi = id; J = A + B C(t); u = C(t) Phi dx0 + int K u; Prop. 2 with C(t) y = xi (from psi(r_eps) - psi(r) = C w + o(|w|), w = O(eps)); the quotient definition; E cap ker C(t) = 0.

**PROVED (moving kernel; psi C^2, bounded F, CF = I).** Differentiating gives C'F + CF' = 0, and the F equation gives **CAF + CB + C'F = G**. For dx = F u + eta, u = C dx:

    u'   = G u + (C' + C A) eta
    eta' = (Q A - F C') eta = (Q A + Q') eta   on ker C(t)

The extra term is -F C' eta = -F D^2 psi(r)[r', eta], the turning of the kernel. Block-triangularity survives. Lost: flat fibers, fixed kernel, and exactness of the off-manifold formula.

**Prop. 4 reformulated (PROVED).** Hypothesis: Phi(t,tau) ker C(tau) = ker C(t), equivalently C' + CA = 0 on ker C. Then J = A on it, exponents <= -kappa, and the decoded quotient is C'R + CAR + CB for any right inverse R.

**Why this matters for linear readouts (PROVED).** If e is C^1 small on a neighbourhood, psi0 = (id+e)^{-1} psi is an exact decoder, and it is nonlinear even if psi is linear. So the nonlinear theory is the correct exact reference for imperfect linear readouts.

**SKETCH.** A C^2 submersive psi is locally a linear decoder in coordinates (psi, rho). Global existence near a merely continuous M was not established.

**Observation-driven variant (PROVED).** With drive h(s) and psi phi = h, invariance and semi-conjugacy hold; conjugacy needs phi injective.

## 3. Predictive criterion

lambda_perp is already computable before closing the loop (J along the driven orbit). The useful question is which simpler quantity decides or bounds it.

### 3.1 Linear case

Take W Hurwitz, W Pi + V = Pi L, N^T Pi = I, T(z) = N^T(z-W)^{-1}V. Substituting V = (z-W)Pi - Pi(z-L):

    I - T(z) = H(z) (zI - L),   H(z) = N^T (zI - W)^{-1} Pi,   det H(z) = chi_perp(z) / chi_W(z)

PROVED, checked to 3e-13. **The transverse eigenvalues are the zeros of H, i.e. the zero dynamics of (W, Pi, N^T).** Transverse stability is the minimum-phase property of the reservoir from tangent input to readout. The paper's counterexample has H = (z-1)/(z^2+2z+7).

Status: the spectral content (triangular form, assignability) is known from Saqib & Padoan; T = I at source eigenvalues is their moment matching; the characteristic equation det(I - T) = 0 and Nyquist are in Rivkind & Barak for fixed points. I did not find the factorization, the identification with zeros, or the items below in what I read.

Consequences (PROVED, checked):
- **Exact count.** (z+a)H(z), a > 0, has winding number equal to the number of unstable transverse eigenvalues. Checked 0 mismatches of 60.
- **Restricted small gain.** For any d x d matrix M: (zI + M)H(z) - I = (N^T W + M N^T)(z-W)^{-1} Pi. If its H-infinity norm is < 1 then H has no RHP zeros. The naive gain ||T|| is >= 1 always. Checked over 300 random cases with 146 stable: M = aI certifies 51, M = -N^T W R0 certifies 28, no false certificates.
- **Frequency integral (Jensen/Bode type, any N).** (1/2pi) int log|det(I-T(iw))| dw + (1/2) tr(N^T V) = sum over Re c_i > 0 of Re c_i, c_i the closed-loop eigenvalues. Checked to 5e-4 (quadrature). It is an exact closed form for the total unstable transverse rate.
- **Assignability for every d.** Identify ker N^T with R^n/Im Pi through a section sigma = sigma0 + Pi X. Then QW|ker becomes piW sigma0 + piW Pi X, a state-feedback problem. If (W, Pi) is controllable, any conjugate-closed multiset is attained by an exact N (Wonham). Checked d = 2 to 3e-7, including unstable targets. Known: Saqib & Padoan Remark 1 by PBH.
- **Cancellation.** For d = 1, lambda_perp is an eigenvalue of W iff there is a pole-zero cancellation, i.e. an unobservable or uncontrollable mode. Prop. 4 is the first, QV = 0 a form of the second.

### 3.2 Nonlinear time-varying, smooth: exact factorization (PROVED; appears new)

Assume a bounded F with F' = AF + B - FG, N^T F = I. Using d/dtau[Phi(t,tau)F(tau)] = Phi(F' - AF):

    (I - K)u = H[(d/dt - G)u] + N^T Phi(t,t0) F(t0) u(t0),   H(t,tau) = N^T Phi(t,tau) F(tau),  H(t,t) = I

The kernel of (d/dt - G) is the source tangent flow, the eigenvalue-one part of K. With v := u' - Gu = N^T A eta, eta0 = Q dx0 and w(t) := N^T Phi(t,t0) eta0:

    int_{t0}^t H(t,tau) v(tau) dtau = w(t)                     (first-kind Volterra)
    eta(t) = Phi(t,t0) eta0 - int Phi(t,tau) F(tau) v(tau) dtau

So lambda_perp < 0 iff the time-varying filter H has an exponentially stable inverse: eta' = QA eta is its inverse dynamics (for x' = Ax + Fv, y = N^T x, holding y = 0 forces v = -N^T A x). For any bounded M(t), differentiate and add M w:

    v(t) = (N^T A + M N^T)(t) Phi(t,t0) eta0 + int R_M(t,tau) v(tau) dtau,   R_M(t,tau) = -(N^T A(t) + M(t) N^T) Phi(t,tau) F(tau)

**Theorem (restricted small gain).** If sup_t int ||R_M(t,tau)|| e^{sigma(t-tau)} dtau < 1 for some 0 <= sigma < kappa and some bounded M, all transverse exponents are <= -sigma.
Proof. Set v_s = e^{sigma t} v. Then |v_s(t)| <= c' + g sup_{tau<=t}|v_s(tau)| with g < 1, so v = O(e^{-sigma t}). The eta formula with sigma < kappa gives the same rate for eta. QED.

Choice M = -N^T A R0, R0 = N(N^T N)^{-1}, gives R_M = -N^T A Q0 Phi F with Q0 = I - R0 N^T: **only the readout's sensitivity to invisible directions, times the invisible response to tangent input**. If N^T A Q0 = 0 the gain is zero, so Prop. 4 is the zero-gain case. If Q0 Phi F vanishes the gain also vanishes.

Direct corollary: lambda_perp <= -kappa + c ||F N^T A|_ker||, from QA = A - F N^T A.

**Exact test family (F).** Lorenz source, r = (y, z), h'(s_3) = amp sech^2((s_3-27)/4), c = (0,0,-1):

    y' = g(s) - k(y-s) + c (z - h(s)),   z' = h'(s_3) g_3(s) + D.(y-s) + E (z - h(s))

phi = (s, h(s)) and N^T = (I, 0) are exact. With chi = z - h(y) the closed loop is **exactly** y' = g(y) + c chi, chi' = a(y) chi, a = E + amp sech^2((y_3-27)/4). So lambda_perp = <a>, a closed form. CLEs are constant.

Checks:
| E, amp | J exponents | <a> | largest CLE |
|---|---|---|---|
| -1, 0.5 | 0.906, -0.002, -0.878, -14.57 | -0.876 | -1.08 |
| -1, 3 | 0.906, -0.001, -0.259, -14.57 | -0.258 | -1.08 |

Note the second row: lambda_perp exceeds the largest CLE by 0.82 with an exact, smooth, chaotic, transversely stable system.

Restricted gain with M = -N^T A R0 (kappa is the driven rate, truth from sup a):
| E, amp, D | kappa | gain at sigma = 0 | largest certified sigma tested | truth |
|---|---|---|---|---|
| -3, 0.5, 0.3 | 3.16 | 0.09 | 2.85 (0.98) | sup a = -2.5, <a> near -2.9 |
| -1, 0.5, 0.3 | 1.08 | 0.24 | 0.81 (0.81) | <a> = -0.88 |
| -0.2, 0.1, 0.3 | 0.26 | 0.34 | 0.13 (0.66) | sup a = -0.1 |
| -1, 3, 0.3 (non-uniform) | 1.08 | 1.13 | none | <a> = -0.26, sup a = 2 |
| 2, 0.5, 12 (unstable) | 1.0 | 6.4 | none | <a> > 0 |
| 0.5, 0.2, 5 (unstable) | 0.65 | 2.1 | none | <a> > 0 |

With M = 0 the gain was above 1 on every case (1.06, 1.09), so **the shift M is essential**. Note 0.13 and 0.81 are lower bounds on -lambda_perp that are consistent with truth, and that sigma < kappa limits certificates to rates below kappa. The certificate is a uniform one: it fails on the non-uniform stable case, which is correct behaviour for a sup-based gain (see 4.4).

Loop identity (PROVED): **N^T A F + N^T B = G**, so R_0(t,t) = N^T B - G. Zero-lag loop gain minus source Jacobian is the restricted gain at zero lag.

### 3.3 Non-differentiable phi: the quotient operator (PROVED; appears new)

Saqib & Padoan, Bizyaeva et al. do not treat this case. Let D be the admissible bundle, frame Xi(t) with Xi' = G Xi, Y the image frame (Y' = JY, N^T Y = Xi). Choose a C^1 left inverse L(t), L Xi = I_k. Write x = Y a + zeta with L N^T zeta = 0. Then zeta' = J zeta - Y a', and differentiating the constraint gives a' = (L' N^T + L N^T J) zeta, so

    zeta' = [J - Y (L' N^T + L N^T J)] zeta   on W(t) = ker(L N^T)

This is the quotient cocycle in coordinates (W(t) is complementary to E). If S(t) = ker L is G-invariant, L' = -LG, and using G u_S in S:

    zeta' = Q_E J zeta,   Q_E = I - Y L N^T

**So in the non-differentiable case QA is replaced by Q_E J, with k < d.** On ker N^T it is QA-like; on the extra d-k decoded directions the feedback B N^T survives. The source's stable exponents do not appear. The equation does not contain G on S, which is why those exponents are not reproduced in general. Checked for k = 2, d = 3 to 6e-10.

(I - K) analogue: with u = Xi a + u_S,

    u_S(t) = N^T Phi(t,t0) zeta0 - int N^T Phi(t,tau) Y(tau) a'(tau) dtau + int K(t,tau) u_S(tau) dtau

The gain-one part (Xi a) is deflated; the rest of K still acts on u_S.

**Is the leading transverse direction readout-invisible? Mostly, not always.** Representative zeta in W, ratio |N^T zeta|/(|N|_2 |zeta|); a random vector gives 0.07 to 0.12. Valid only for runs where the third QR direction is transverse. Rössler gamma = 5, rho = 0.9: 0.014, 0.014 (strongly invisible). Rössler gamma = 20, rho = 0.5: 0.10 to 0.13 (no better than random). Lorenz, all 12 runs (gamma = 1, 5, 20): 0.000 to 0.026 (strongly invisible). So "the transverse directions are the readout-invisible ones" is well supported on Lorenz and on Rössler at gamma = 5, but not on Rössler at gamma = 20, rho = 0.5, where the source is thinly sampled along its stable direction and the d - k decoded direction can matter. Small sample (3 runs per setting).

**Bound (PROVED).** lambda_perp <= -kappa + c sup ||Q_E B N^T|_W - Y L N^T A|_W||. Probably far too loose to be useful in practice (not tested on reservoirs).

**Sum rule without smoothness (PROVED, checked to 3e-10).**

    sum over quotient exponents = sum CLE + <tr C B> - sum over D exponents

with n-k quotient exponents, so (n-k) lambda_perp >= sum CLE + <tr C B> - sum_D lambda. This is a driven-phase instability certificate that needs no smooth phi and no exact source stable exponent. It is exact for n - k = 1. It explains one effect of an N^T B penalty: each unit of trace adds exactly one unit to the transverse sum. For large n it is weak, because the bulk of tr A dominates. Checked in (F) to three decimals.

**Riccati form (PROVED).** For any C^1 right inverse R and any N: u' = G_R u + N^T A eta, eta' = Q_R A eta + Z_R u, G_R = N^T(AR+B), Z_R = Q_R(AR+B) - R'. A bounded solution of Z_R = 0 is exactly a d-dimensional J-invariant complement of ker N^T. Whether one exists when phi is not C^1 is open.

### 3.4 Geometry (PROVED, checked)

- **Gap has no universal sign. "lambda_perp > largest CLE" is FALSE as a theorem.** Symmetric W, min-norm N: QW|ker is a compression, so lambda_perp <= lambda_max(W). Checked: max difference -1.6e-4 over 300 cases. The observed positive gap needs non-normality or obliquity.
- **Energy bound.** With F = R0 + Dzeta, Dzeta in ker N^T (phi = R0 s + zeta(s)): lambda_perp <= mu_2(A|ker) + ||Dzeta|| ||N^T A|_ker||. Checked: no violations in 300, median slack 6.5, so loose. Corollary: min-norm N, flat M, Euclidean contraction give stability. Instability is carried by the readout-invisible geometry and non-normality.
- **Passivity.** If S' + SA + A^T S <= -2 sigma S and S F = N M(t) (Q is S-orthogonal), lambda_perp <= -sigma. A positive-real condition on H.
- **Dual of Prop. 4.** The driven system in (u, eta) is u' = (G - N^T B)u + N^T A eta, eta' = -QB u + QA eta. Driven and closed-loop transverse blocks differ only through (QB)(N^T A). If QB = 0 or N^T A|ker = 0 the transverse exponents are CLEs.

### 3.5 No-go results

**Theorem (PROVED, checked).** There is no function of (the CLEs, e, the source) that decides lambda_perp, also for chaotic sources and non-differentiable phi.
Proof. Take any source g and the family y' = g(s) + k(s-y) + c eta, eta' = E eta + D(y-s), plus optionally a slave w' = -b w + y, with b below the source's contraction rate. Then phi = (s, 0, psi(s)) with psi generically non-differentiable, N^T = (I, 0, 0) gives e = 0. The driven (y, eta) block is [[-k, c],[D, E]]. Fix trace and determinant: k = E - tr, cD = -kE - det. Then the CLEs are fixed, while in the closed loop eta' = E eta, so lambda_perp = E is any real number. Checked: fixed eigenvalues -2 +- 3i with E = -2, 0.5, 3. QED.

Linear version (Saqib & Padoan eq. 32): same reservoir, different exact readout. The theorem above extends the principle to chaos and non-smooth maps, but with different reservoirs. For a fixed reservoir and chaotic source there is no family of exact readouts. An empirical analogue is tested below.

**Closed form: no (PROVED).** With n - k = 1, moving the second eigenvalue of W leaves the largest CLE and N^T V fixed and moves lambda_perp. So no formula in (lambda_perp, largest CLE, loop gain) alone exists. What exists: two-sided identities in the *sum* (3.3), an exact integral in the linear case (3.1), and sufficient gains (3.2).

**Empirical analogue for a fixed reservoir and chaotic source (checked, one reservoir, three random directions).** Rössler, gamma = 5, rho = 0.9, n = 200. N = N0 + Delta with Delta in the 80 weakest singular directions of the training data:
| |Delta|/|N0| | train NRMSE | lambda_perp, trials 1, 2, 3 |
|---|---|---|
| 0 | 6.4e-5 | 1.90, 1.90, 1.90 |
| 1 | 6.5e-5 | 3.03, 2.57, 2.07 |
| 3 | 6.7e-5 | 5.71, 8.49, 3.08 |
| 10 | 9e-5 | 16.9, 34.6, 4.46 |
Training error stays essentially flat while lambda_perp moves by an order of magnitude. Random directions destabilize; the largest stabilization seen was 1.90 to 1.77. This is the chaotic counterpart of Saqib & Padoan's free transverse modes, measured, not proved.

**Simple driven-phase predictors (checked, 108 runs per source, n = 200).** Spearman with lambda_perp within gamma = 1, 5, 20. Each cell n = 36:
| Quantity | Rössler | Lorenz |
|---|---|---|
| tr N^T B | +0.70, +0.86, +0.49 | +0.53, +0.70, +0.84 |
| largest CLE | +0.60, +0.46, +0.30 | +0.70, +0.64, +0.46 |
| mu_2(A|ker) | +0.57, +0.44, +0.32 | +0.75, +0.74, +0.61 |
| ||N^T A|ker|| | -0.06, -0.29, -0.13 | +0.48, +0.33, +0.20 |
tr N^T B beats the largest CLE in 5 of 6 cells, and keeps partial correlation 0.45 to 0.85 given the CLE. The CLE keeps 0.05 to 0.73 given the trace, so both carry information. Within a fixed sigma (n = 12) the ranking is mixed, and the CLE often wins at small sigma. The sign agrees with the sum rule, but the average shift (tr N^T B)/(n - k), about 0.1 to 0.4, is smaller than the gap, so the sum rule does not by itself explain the correlation. ||N^T A|ker||, the coupling in the bound, is a poor predictor alone. **No simple quantity replaces computing lambda_perp**, which is cheap anyway. Gap lambda_perp - largest CLE: positive in 108/108 on both sources, median +1.86 and +0.78.

**SKETCH, N^T B penalty on tanh reservoirs.** N^T B = gamma N^T D V and N^T A|ker = gamma N^T D W|ker share the factor N^T D(t), so penalizing the first also shrinks the coupling ||N^T A|_ker||, if V does not align badly. The loop identity suggests the natural target is N^T B near G rather than 0 (CONJECTURE).

## 4. Imperfect reconstruction

Bizyaeva et al. Prop. IV.1 give the Gronwall bound with closed-loop Lipschitz constant. That is the baseline (known), and it is PROVED there for any readout. Normal hyperbolicity relative to a manifold is the wrong frame when phi is merely continuous.

**4.1 Tube theorem under uniform transverse contraction (PROVED; no tangential hyperbolicity, no rate condition).**
Hypotheses: U compact trapping region of g with g inward on bdry U, m = min inward speed; A = cap Theta_t U; phi C^2 on a neighbourhood of U solving the sync identity; psi0 C^2 exact on U; the cocycle of L = QA + Q' over the semiflow on U satisfies ||Psi|| <= c e^{-sigma t}; L Lipschitz in s. The closed loop uses decoder psi with ||psi - psi0|| <= eps on a neighbourhood. By continuity, uniformity on A alone gives uniformity on a smaller U.
Proof. Coordinates shat = psi0(x), chi = x - phi(shat). Then chi' = L(shat) chi + O(|chi|^2) + O(delta) and shat' = g(shat) + O(|chi| + delta), delta = L_s eps. Let V(s,chi) = int_0^T |Psi(tau;s)chi|^2 dtau with c^2 e^{-2 sigma T} < 1/2. V is a quadratic form, Lipschitz in s, with derivative along the exact s-flow <= -|chi|^2/2. Along the perturbed motion the extra terms are O(|chi|^3 + delta|chi| + (|chi| + delta)|chi|^2). For a small tube: V' <= -2 sigma' V + c1 delta sqrt(V), so |chi(t)| <= c2 e^{-sigma' t}|chi(0)| + c3 delta / sigma'. If delta is small enough that the defect in shat' is below m, shat cannot leave U. So the tube is forward invariant. QED.

Corollaries (PROVED):
- **Upper semicontinuity.** shat is an O(delta)-pseudo-orbit of g on U. As Theta_T U enters any neighbourhood of A, closed-loop omega-limit sets converge to phi(A) as eps -> 0. This is a statement about attractor location, and no shadowing is needed.
- **Forecast bound in source coordinates.** |shat(t) - s(t)| <= eps_eff (e^{L_g t} - 1)/L_g + ..., eps_eff = c(1 + L_v/sigma') delta, with L_v = sup||C' + CA||. Compared with Bizyaeva Prop. IV.1 this replaces the closed-loop Lipschitz constant L_g(closed), which is large for a reservoir, by the source Lipschitz constant, at the price of the 1/sigma' factor and the hypothesis of transverse contraction.

Checked in (F) with psi = y + eps b z, kappa near 1 and source contraction 14.57, so normal hyperbolicity fails:
| E, amp | eps | median |chi| | sup |chi| |
|---|---|---|---|
| -1, 0.5 | 1e-4, 1e-3, 1e-2 | 3.4e-5, 3.4e-4, 3.4e-3 | 4.5e-5, 4.5e-4, 4.5e-3 |
| -2, 1 | 1e-4, 1e-3, 1e-2 | 1.1e-4, 1.1e-3, 1.1e-2 | 2.4e-4, 2.4e-3, 2.4e-2 |
Linear in eps and sup/median about 1.3 to 2. Median time to |shat - s| > 2 for E = -1, amp = 0.5: 11.3, 6.1, 1.9 at eps = 1e-6, 1e-4, 1e-2, slope about 1/lambda_1 in log(1/eps).

Subtlety: U must be chosen with care. On Lorenz, a trapping U containing C+- has a maximal invariant set larger than the chaotic attractor. Tube and upper semicontinuity then speak about that larger set.

Limit: a C^2 phi on U is the strong hypothesis. In generic filter-type reservoirs it requires the rate condition: 30/810 Lorenz and 163/810 Rössler runs.

**4.2 Converse Lyapunov: no regularity of phi at all (PROVED; standard argument, statement apparently not in this literature).**
Suppose G0 is Lipschitz with M invariant and dist(Xi_t x, M) <= c e^{-sigma0 t} dist(x, M) near M. Let |G - G0| <= delta near M. Then every solution of x' = G(x) starting close enough satisfies limsup dist(x(t), M) <= c' delta / sigma, for sigma < sigma0.
Proof. Let V(x) = sup_{t>=0} e^{sigma t} dist(Xi_t x, M). Pick T with c e^{(sigma-sigma0)T} <= 1: the sup is attained on [0,T], so V is Lipschitz with constant Lip = e^{(L+sigma)T}, and dist <= V <= c dist. Also V(Xi_h x) <= e^{-sigma h} V(x). Along x' = G(x): D+V <= -sigma V + Lip delta. QED.

**The regularity needed is on the decoder side.** G0 = f(x, psi0(x)) needs psi0 Lipschitz with psi0 phi = id on M, i.e. phi^{-1} Lipschitz, i.e. |phi(s)-phi(s')| >= c|s-s'|. This holds if Lip(e) < 1 on A, since |N||phi(s)-phi(s')| >= (1 - Lip e)|s-s'|. It does **not** need phi Lipschitz. By Kirszbraun, psi0 = psi - e-tilde with the same sup norm. So: small e in sup norm plus Lip(e) < 1 is what is needed, and this is checkable from data as the largest |e(s)-e(s')|/|s-s'| over nearby pairs (not yet tested). Checked on data: Rössler, largest ratio over nearest non-consecutive pairs is < 1 in 108/108 runs (median 0.011). Lorenz, < 1 in 79/108 (99th percentile < 1 in 90/108). These pairs are at distance about 0.2 to 0.4, so this bounds Lip(e) only at data resolution; it cannot exclude a rough small-scale e. Remaining hypothesis: exponential attraction of M, which is exactly what fails or is unverified on these sources.

**4.3 Getting exponential attraction with continuous phi (SKETCH; relies on standard theorems not re-derived here).** If A is uniformly hyperbolic and the quotient cocycle is uniformly contracting, E is continuous and dominates the quotient, so it has an invariant complement. Then M is a **hyperbolic set of the closed loop in R^n, with no smoothness of phi needed**. phi(W^u) lies in W^u(phi(s)) because backward differences decay exponentially. So W^u(M) is contained in M, the stable manifolds fill a neighbourhood by invariance of domain, and M is an exponentially attracting attractor. Structural stability then gives a nearby orbit-equivalent attractor under C^1-small perturbation, and 4.2 gives the C^0 version. Oishi et al. use HPS Theorem 5.5 for a partially hyperbolic analogue. Hara & Kokubu 2026 reportedly use structural stability and strong fiber contraction (unread). **Lorenz and Rössler are not uniformly hyperbolic, so this does not cover the paper's numerics.** Lorenz (singular hyperbolic) with a trapping cone field: CONJECTURE. Rössler: open.

Shadowing variant (SKETCH): Palmer-type shadowing along the driven orbit with a dichotomy for J gives a true orbit within c ||d||, with c of order 1/|lambda_perp| in the transverse part. It needs lambda_perp != 0, not < 0: the sign decides attracting versus saddle.

**4.4 Non-uniform: the O(e) sup bound is FALSE in general (checked), and a moment bound replaces it.**
<a> < 0 with positive rates on embedded orbits is the bubbling setting of Ashwin, Buescu, Stewart 1994. In (F) with E = -1, amp = 3, <a> = -0.26, a = 2 at the C+- fixed points:
| eps | median |chi| | 99.9% | sup, T = 8000 |
|---|---|---|---|
| 1e-5 | 9.3e-5 | 1.3e-2 | 3.8e-2 |
| 1e-4 | 9.2e-4 | 1.7e-1 | 5.7e-1 |
| 1e-3 | 1.3e-2 | 84 | 97 |
| 1e-2 | 86 | 86 | 90 |
Sup/median is about 400 to 600 at small eps, compared with 1.3 to 2 in the uniform case (where sup is also linear, e.g. 4.5e-5, 4.5e-3 at T = 8000). **At eps = 1e-3 a burst takes the trajectory permanently away (chi near 85), with lambda_perp < 0 and exact phi in the limit.** So in this example, a small readout error, negative transverse exponent, and a loss of the attractor coexist. This is an example of the paper's stable-but-failing runs, not a proof that those runs fail this way.

**Moment bound (PROVED at the linear level).** For eta' = L_perp(t) eta + d, |d| <= eps, with L(q) = lim (1/T) log E||Psi_perp(T)||^q < 0, q >= 1: Minkowski and invariance give ||eta||_{L^q(mu)} <= c eps q / |L(q)|, so mu{|eta| > x} <= (c eps q / (|L(q)| x))^q. L(q)/q interpolates from lambda_perp (q -> 0) to the uniform rate (q -> infinity). In (F) with E = -1, amp = 3: L(1) = -0.056, L(2) = +0.18, so tails have exponent between 1 and 2 (estimated from 1000 windows of length 20, so rare events are poorly sampled). Compare E = -1, amp = 0.5: L(q) < 0 at all tested q.
Nonlinear extension: not proved. It needs eta to remain in the linear region between bursts.

**Why do stable runs fail on real reservoirs? Tested; the conjecture gets weak support at best.** 108 runs per source; stable means lambda_perp < 0, fail means not on the source attractor after 1000 time units. Rössler: 49 stable, 12 fail. Lorenz: 101 stable, 25 fail.
| Predictor among stable runs | Rössler | Lorenz |
|---|---|---|
| AUC lambda_perp | 0.50 | 0.62 |
| AUC L(1), L(2), L(8) | 0.60, 0.60, 0.59 | 0.70, 0.71, 0.72 |
| AUC largest finite-time rate | 0.58 | 0.72 |
| AUC largest CLE | 0.35 | 0.50 |
| fail rate given L(2) > 0 vs <= 0 | 0.67 (n=9) vs 0.15 | 0.60 (n=5) vs 0.23 |
| fail rate given positive transverse rate at C+ | - | 0.33 (n=3) vs 0.24 |
| fail rate given positive transverse rate at C- | - | 0.83 (n=6) vs 0.21 |
| fail rate given stable closed-loop fixed point within 5 of a source fixed point | none found | 0.73 (n=11) vs 0.19 |
L(q) is estimated from 60 windows of length 10, so it is noisy, and AUCs have no correction for selection among predictors. The transverse rate at the Lorenz origin is positive in 91/101 runs because the reservoir extrapolates there (median |e| = 10), so **uniform transverse contraction essentially never holds on these Lorenz runs, and the hypotheses of 4.1 and 4.3 fail for them.**

**A separate, tangential mechanism (SKETCH).** For Lorenz at rho = 28, C+- have Re(eigenvalue) = +0.094 (Hopf at sigma(sigma+beta+3)/(sigma-beta-1) = 24.74). A readout error of order 0.09 in Dg-like terms can stabilize them, which is a failure of C^1 closeness in the *tangent* block, not of transverse stability. It accounts for 7 of the 23 fixed-point ends among stable Lorenz runs. The other 16 end at fixed points not within 5 of a source fixed point (untrained attractors, as in Hart). On Rössler this mechanism was not seen. So the failures of stable runs are heterogeneous, and I have no single criterion for them.

## 5. Literature

Reading depth is stated. The literature session's map is `docs/literature_map.md` on branch `literature-map`.

| Source | Read | Overlap |
|---|---|---|
| Saqib & Padoan arXiv:2610.08987 | Props. 2-4, Remark 1, Cor. 7, Sec. V | Linear reservoir, neutral linear exosystem: triangular form, transverse eigenvalues freely assignable, moment matching T = I at source eigenvalues, zero-error instability; nonlinear: invariant manifold and KKL map, local, no transverse operator. **Not there: chaotic sources, non-differentiable maps, time-varying transverse operator, zeros and factorization.** |
| Bizyaeva et al. arXiv:2610.04343 | Props. III.1, IV.1 | KKL view; exact on X iff closed-loop reproduces (our Prop. 1, and supports the repair of Error 2); finite-time Gronwall forecast bound. No transverse analysis (only named as a question). |
| Oishi et al. arXiv:2602.11069 | Theorem 1, Methods | Linear QB = 0: known. Controllability remark. Partially hyperbolic set via HPS 5.5. |
| Oishi et al. arXiv:2606.24303 | Abstract, keyword scan | No theorem overlap seen. Not read in full. |
| Hara & Kokubu 2024 | Full | Degenerate reservoir (no r dependence), conjugacy on the image; no stability theorem. |
| **Hara & Kokubu 2026** | **Unread: SIAM bot check blocks the page, no preprint found. BLOCKED.** | Snippet: fiber contraction, conjugacy. 4.3 cannot be called new until read. Needs the PDF from the user. |
| A. Hart 2024 Physica D | Keyword scan, one section | GS existence, linear form, embeddings, autonomous field on an embedded set. No stability theorem in scan. |
| J. Hart 2024 Chaos | Main argument, via fetch | Heuristic with no theorem: rate condition and "stay close to CLEs". Family (F) shows rate failure does not force loss of -14.57, and gives a gap. |
| Wong et al. arXiv:2408.04058 | Via fetch | Contraction of driven reservoir; closed-loop robustness stated as open. |
| Rivkind & Barak PRL 2017 | Key equations via fetch | G_CL = G_OL/(1-G_OL), Nyquist, for fixed points in mean-field: known principle for det(I-T) = 0. |
| Wikner et al. | Via literature map | N^T D B penalty known in substance. |
| Ashwin, Buescu, Stewart 1994 | Abstract | Bubbling: known. |
| Freudenberg & Looze 1985, Iglesias 2002, Byrnes-Isidori-Willems 1991, Palmer 1988, Andrieu & Praly 2006 | Secondary or snippets | Bode integral, LTV analogue, passivity and zero dynamics, shadowing, KKL: known in their fields. The sync identity for linear reservoirs is the KKL equation. |

Status of new results, provisional:
- Known: Prop. 1 in substance; finite-time bound; linear triangular form and assignability; QB = 0 linear; linear+chaos restriction; bubbling.
- Apparently new, as far as read: Prop. 2 as a theorem; nonlinear time-varying QA and moving-kernel term; time-varying factorization and restricted small gain; quotient operator Q_E J and the smoothness-free sum rule; loop identity; chaotic no-go; tube theorem with source-coordinate forecast bound; moment tail bound. Search for zero-dynamics treatments of RC found none (absence of evidence only).
- Elementary given the framework: the sum rule, loop identity, chaotic family. These are easy and could appear elsewhere in other notation.

## 6. Status by brief item

| Item | Status |
|---|---|
| 1. Audit | Done. Props. 1, 2, 4 and the spectrum claim hold. Three errors. Open: tempered version of Prop. 2 |
| 2. General decoder | PROVED (2), except straightening SKETCH |
| 3. Criterion, linear | PROVED, checked; spectral content known |
| 3. Criterion, smooth time-varying | PROVED, checked in family (F). Not tested on tanh reservoirs: the required F has N^T F != I there |
| 3. Criterion, non-differentiable | Operator and sum rule PROVED. A useful sharp gain: not obtained |
| 3. Closed form | Does not exist in the requested variables (PROVED) |
| 4. Smooth, uniform transverse | PROVED (tube) |
| 4. Continuous phi, general | PROVED conditional on exponential attraction and Lipschitz phi^{-1}. Getting attraction: SKETCH for hyperbolic sources, CONJECTURE for Lorenz, open for Rössler |
| 4. Non-uniform | O(e) sup bound FALSE in general; moment bound PROVED at linear level; nonlinear version open |
| 5. Literature | Done except Hara & Kokubu 2026 (blocked) and full texts noted above |

**Headline for a letter: no.** The strongest statement is structural: transverse stability is the zero dynamics of the reservoir, and neither CLEs nor reconstruction error constrain it, also for chaotic sources. Part of this is now out for linear systems, the proofs are short, and no sharp predictive law holds on real reservoirs: the certified gains need a smooth F, uniform contraction fails on Lorenz, and failures of stable runs are heterogeneous. This fits a long-format paper.
