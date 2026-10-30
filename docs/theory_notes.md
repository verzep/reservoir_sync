# Theory notes: what can be proved about closing the loop

Status of this document: **incomplete, written under a usage limit.**
- All derivations are by hand. **No numerical check was run** (uranus was never used). Items flagged "test" below are still open.
- Labels: PROVED (full proof here), SKETCH, CONJECTURE, FALSE. "PROVED" means proved here and not independently checked.
- Literature (section 5) was only partly read; each entry says how much.

Notation: A = A_c, B = B_c along the driven orbit, G = Dg(s(t)), F = Dphi(s(t)) when it exists, C(t) = Dpsi(r(t)) (= N^T for a linear decoder), Q = I - F C, J = A + B C, Phi = Phi_c, ||Phi(t,tau)|| <= c e^{-kappa(t-tau)}.

## 1. Audit of Section 3

**Prop. 1 (no-derivative conjugacy): correct.** Uniform contraction is not used, only continuity, compactness and uniqueness. Solutions of the closed loop need only exist on M, where they do.

**Prop. 2 (surviving tangents): proof correct line by line.** Checked: segment averaging on the compact convex hull, robustness of contraction on (-inf,t], dominated convergence, N^T y = xi, the exponent bounds. Remarks:
- A_s must be invariant in both time directions (the integral runs to -inf). Implicit in the paper.
- "Gain exactly one" should read "eigenvalue one": K xi = xi says nothing about the operator norm of K.
- Assumption 3 requires contraction on *every* orbit in A_s, including embedded fixed points and periodic orbits. The Lorenz origin is an example, and there dim D also drops because g = 0. The numerics measure the largest CLE for the natural measure only, which can be much more negative than -kappa. The paper's numerics therefore do not verify the assumption.

**Spectrum claim (exponents on E plus quotient = closed-loop spectrum): correct** for an ergodic measure, a measurable invariant E, and the quotient norm: a block-triangular cocycle has the union of the diagonal spectra. The identification of ker N^T with the quotient for k = d needs the angle between E and ker N^T to be tempered. This holds if xi -> y is bounded, which is clear for uniformly hyperbolic D.

**ERROR 1 (Prop. 3): "E = TM" is false as stated.** E is defined from backward-admissible directions. Those must be backward bounded, so they exclude every direction with a negative exponent. For Lorenz, k = 2 and dim TM = 3. Correct statement: E is contained in Im Dphi, which is a larger J-invariant bundle. Redefine the bundle in the smooth case.

**ERROR 2 / hidden assumption (Prop. 3, eq. differential_inverse): N^T Dphi = I does not follow from exact reconstruction on A_s.** Differentiating N^T phi = id on A_s gives the identity only on the tangent cone of A_s.
- Counterexample (PROVED): source with attracting circle rho' = -2(rho-1)-type radial dynamics, theta' = 1, so A_s is the unit circle with s(t) = (cos t, sin t). Take a linear reservoir with W Phi0 + V = Phi0 L0, where L0 is the rotation generator, and N^T Phi0 = I. Reconstruction on A_s is exact. The closed loop is the linear W + V N^T, whose spectrum contains +-i, i.e. exponents 0, 0. The source has exponents 0, -2. So the closed-loop spectrum is not "source exponents plus transverse exponents of QA", because -2 is absent.
- Repair: assume exactness on an open neighbourhood, or assume the tangent cones of A_s span R^d (LEMMA, PROVED: a C^1 function vanishing on X has derivative vanishing on the tangent cone of X). The cone condition plausibly holds for transversely Cantor attractors with phi C^1. Not checked for Lorenz.

With that repair, the *computation* in Prop. 3 is correct. It needs only a bounded F solving F' = AF + B - FG with N^T F = I; C^2 is more than necessary.

**ERROR 3 (Section 4): "They reduce to the same action on transverse directions only if A ker N^T subset ker N^T" is false as a spectral claim.** See the dual statement in 3.3: if Q B = 0 the transverse exponents are also CLEs, without kernel invariance. Explicit example: n = 2, N^T = (0,1), F = (f,1)^T an eigenvector of W with eigenvalue a, V = (mu - a)F. Then lambda_perp = b, the other eigenvalue of W, while N^T W e_1 != 0 in general.

**Prop. 4: proof correct, but the hypothesis is very restrictive.** N^T A = M(t) N^T says the decoded variable obeys a closed equation. In the linear case M + N^T V = L, i.e. shat' = L shat + N^T V (s - shat), which is a **Luenberger observer**. The proposition is a separation principle for surrogates containing a copy of the source model. It does not hold for a generic tanh reservoir.

**Further remarks.**
- The Section 4 counterexample is correct (checked: W Phi + V = Phi L, H(z) = (z-1)/(z^2+2z+7)), but its attractor is the single point {0}. A chaotic version (PROVED, by direct substitution): for any source g, take y' = g(s) + k(s-y) + C eta, eta' = E eta + D(y-s), with k > E > 0 and CD < -kE. Then phi(s) = (s,0) and N^T = (I,0) are exact, and the driven block [[-k,C],[D,E]] is Hurwitz. The closed loop has eta' = E eta, so lambda_perp = E > 0.
- **Linear reservoirs and chaos are incompatible with exactness (PROVED).** s = T*s with T(z) = N^T(z-W)^{-1}V forces T(iw) = I on the spectral support of s. T is rational and strictly proper, so T - I cannot vanish on an infinite set. Hence the spectrum is finite and the source quasi-periodic. Eq. linear_fiber_relations is vacuous for a chaotic source.
- Moreover, linear closed loops have no isolated nonlinear attractor. If the frequency set of the source exceeds its dimension, every frequency present is a closed-loop eigenvalue and lambda_perp = 0 exactly.

## 2. General C^1 decoder

No reservoir structure is used anywhere below: only f C^1, phi continuous mapping orbits to driven solutions, and (for Prop. 2) uniform contraction. The results hold for any synchronized surrogate.

**PROVED (same proofs).**
- Prop. 1 with psi phi = id. The closed-loop solution, the conjugacy and ghat = g follow from d/dt psi(r(t)) = s'.
- J = A + B C(t), with Volterra equation u = C(t) Phi dx0 + int K u, K = C(t) Phi(t,tau) B(tau).
- Prop. 2: C(t) y = xi, using psi(r_eps) - psi(r) = C w + o(|w|) and w = O(eps).
- Quotient definition of the transverse exponents, unchanged. E cap ker C(t) = 0.

**PROVED (moving kernel; psi C^2, phi smooth as in Prop. 3).** With CF = I, differentiating gives C'F + CF' = 0, and the F equation gives CAF + CB + C'F = G. For dx = F u + eta, u = C dx:

    u'   = G u + (C' + C A) eta
    eta' = (Q A - F C') eta = (Q A + Q') eta   on ker C(t)

The extra term is -F C' eta = -F D^2 psi(r)[r', eta]. It is the turning of the kernel. Block-triangularity survives. What is lost: flat fibers (the level sets of psi are curved, ker C is only their linearization) and the exact N^T-linearity of the off-manifold formula.

**Prop. 4 reformulated (PROVED).** Hypothesis: Phi(t,tau) ker C(tau) = ker C(t), i.e. the kernel bundle is driven-invariant, equivalently (C' + CA) = 0 on ker C when C is C^1 in t. Then J = A on it, its exponents are <= -kappa, and the decoded quotient is C' R + C A R + C B for any right inverse R.

**SKETCH.** A C^2 submersive psi is locally a linear decoder in coordinates (psi, rho); the extra term is the coordinate change. Global existence near a merely continuous M was not established.

**Observation-driven variant (PROVED).** If the drive is h(s) and psi phi = h, then invariance and semi-conjugacy still hold; conjugacy needs phi injective.

## 3. Predictive criterion

Remark: lambda_perp is already computable before closing the loop (J along the driven orbit). The useful question is which simpler quantities decide it.

### 3.1 Linear case: transverse spectrum = transmission zeros (PROVED)

Take W Hurwitz, W Phi + V = Phi L, N^T Phi = I, T(z) = N^T(z-W)^{-1}V. Substituting V = (z-W)Phi - Phi(z-L):

    I - T(z) = H(z) (zI - L),   H(z) = N^T (zI - W)^{-1} Phi
    det H(z) = chi_perp(z) / chi_W(z)

So the source factor is deflated exactly, and **the transverse eigenvalues are the zeros of H**, i.e. the zero dynamics of (W, Phi, N^T). Directly: holding y = N^T x at 0 forces x' = QWx. **Transverse stability is the minimum-phase property of the reservoir from tangent input to readout.** The counterexample is a non-minimum-phase filter.

Consequences (all PROVED):
- **Nyquist.** Winding of det(I - T(iw)) counts (unstable source eigenvalues + unstable transverse eigenvalues); the locus passes through 1 at imaginary source eigenvalues. Equivalent cleaner form: lambda_perp < 0 iff (z+a)H(z) has no RHP zeros, which is a winding count, with a > 0.
- **Restricted small gain.** (z+a)H(z) - I = N^T (W+a)(z-W)^{-1} Phi. If sup_w ||N^T (W+a)(iw-W)^{-1} Phi|| < 1 for some a > 0, all transverse eigenvalues are stable (Rouche). This is the right replacement for ||T||.
- **Exact frequency integral** (Jensen/Bode type; any N, no exactness needed):
  (1/2pi) int log|det(I - T(iw))| dw + (1/2) tr(N^T V) = sum over Re c_i > 0 of Re c_i, with c_i the closed-loop eigenvalues. For exact N, subtract the unstable source part to get the sum of unstable transverse rates.
- **Pole placement, a no-go.** For d = 1 and (W,Phi) controllable, N -> numerator of H is a bijection onto monic polynomials of degree n-1 under N^T Phi = 1, so **any transverse spectrum is attained by some exact N**. Zero training error and fixed CLEs therefore place no constraint on lambda_perp: **no function of the CLEs and the reconstruction error can decide stability.** Only d = 1 is proved; generic d > 1 is a CONJECTURE.
- **Cancellation.** For d = 1, lambda_perp equals an eigenvalue of W iff there is a pole-zero cancellation, i.e. an unobservable or uncontrollable mode. Prop. 4 is the unobservable case, Q V = 0 a controllable-subspace case.

### 3.2 Time-dependent: exact factorization and small gain (PROVED)

Requires bounded F with F' = AF + B - FG and N^T F = I. Using d/dtau[Phi(t,tau)F(tau)] = Phi(F' - AF):

    (I - K)u = H[(d/dt - G)u] + N^T Phi(t,t0) F(t0) u(t0),   H(t,tau) = N^T Phi(t,tau) F(tau),  H(t,t) = I

The kernel of (d/dt - G) is the source tangent flow, which is the gain-one part of K. With v := u' - G u = N^T A eta:

    v(t) = N^T A(t) Phi(t,t0) eta0 + int R(t,tau) v(tau) dtau,   R(t,tau) = -N^T A(t) Phi(t,tau) F(tau)
    eta(t) = Phi(t,t0) eta0 - int Phi(t,tau) F(tau) v(tau) dtau

**Theorem (restricted small gain).** If sup_t int ||R(t,tau)|| e^{sigma(t-tau)} dtau < 1 for some 0 <= sigma < kappa, then all transverse exponents are <= -sigma. Proof: a weighted Gronwall/contraction bound on v gives |v| <= const e^{-sigma t}, and the eta formula then gives the same rate. Corollaries:
- lambda_perp <= -kappa + c ||F N^T A|_ker||. This follows directly from QA = A - F N^T A and gives a closed form relating lambda_perp and kappa, with the *restricted* loop in place of B N^T.
- With rate condition Lambda < kappa, ||F|| <= c c_s ||B|| / (kappa - Lambda), so the bound diverges at the rate threshold. Likely loose (test).

**Loop identity (PROVED).** Applying N^T to the F equation: **N^T A F + N^T B = G.** So R(t,t) = N^T B - G. Zero-lag loop gain minus the source Jacobian is the restricted gain.

**Liouville sum rule (PROVED; first equality needs no exactness).**

    sum all J exponents = sum CLE + <tr C B>
    sum lambda_perp = sum CLE + <tr N^T B> - sum source exponents   (k = d or smooth case)

This gives a driven-phase certificate of instability: (n-d) lambda_perp_max >= the right side. For n = d+1 it is an **exact closed form**. Example, phi = (s, h(s)), with z-block A22 - Dh A12: lambda_perp = A22 - A12 <Dh>. It explains one effect of an N^T B penalty: each unit of trace adds one unit to the transverse sum. For n large the bound on the maximum is weak.

**Answer to the question asked: no closed form in (lambda_perp, largest CLE, loop gain) exists (PROVED).** With n = d+1, changing the second eigenvalue of W leaves the largest CLE and N^T V fixed but moves lambda_perp.

### 3.3 Geometry (PROVED)

- **Gap has no universal sign: "lambda_perp > largest CLE" is FALSE as a theorem.** W symmetric, n = 3, d = 2, min-norm N: QW|ker is a compression, so lambda_perp <= lambda_max(W) (Cauchy interlacing). The observed positive gap needs non-normality or obliquity.
- **Energy bound.** With R = N(N^T N)^{-1}, F = R + Dzeta, Dzeta in ker N^T (zeta from phi = Rs + zeta(s)):
  lambda_perp <= mu_2(A) + ||Dzeta|| ||N^T A|_ker||, with mu_2 the log norm. Corollary: min-norm N, linear phi and Euclidean-contracting A give stability. Instability is carried by the readout-invisible part of the tangent.
- **Passivity.** If S' + SA + A^T S <= -2 sigma S and S F = N M(t) (Q is S-orthogonal), then lambda_perp <= -sigma. This is a positive-real condition on H. The relevant control result is Byrnes-Isidori-Willems 1991 (section 5).
- **Dual of Prop. 4.** In (u, eta) the driven system is u' = (G - N^T B)u + N^T A eta, eta' = -QB u + QA eta. The driven and closed-loop transverse dynamics differ only through the product (QB)(N^T A). If QB = 0 or N^T A|ker = 0, the transverse exponents are CLEs. Kernel invariance is sufficient, not necessary.
- **Right-inverse block form (no phi derivative, any N).** For any C^1 right inverse R: u' = G_R u + N^T A eta, eta' = Q_R A eta + Z_R u, with G_R = N^T(AR+B), Z_R = Q_R(AR+B) - R'. Z_R = 0 is a Riccati equation for a J-invariant complement of ker N^T.

**SKETCH, penalty mechanism for tanh reservoirs.** N^T B = gamma N^T D V and N^T A|ker = gamma N^T D W|ker share the factor N^T D(t). Penalizing N^T B shrinks ||N^T D|| only if V does not align badly, so this is heuristic. The loop identity also suggests the target is N^T B close to G, not 0 (CONJECTURE, test).

## 4. Imperfect reconstruction

Normal hyperbolicity is not the right frame for merely continuous phi. Three different statements survive.

**4.1 Finite time (PROVED).** r(t) = phi(s(t)) solves r' = G(r) + d, |d| <= L_s |e|. Gronwall gives |x - r| <= (L_s E0 / Lambda)(e^{Lambda t} - 1).

**4.2 Reduction to an exact loop, smooth case (PROVED if De is small).** psi0 = (id+e)^{-1} psi is exact and C^1-close to psi. It is nonlinear even if psi is linear, so section 2 is needed here.

**4.3 Theorem: uniform transverse contraction only (PROVED under strong hypotheses; written as a proof outline, constants not tracked).**
Hypotheses: U is a trapping region of g; phi C^2 on U solves the sync identity; psi0 C^2 exact on U; the transverse cocycle on U is uniformly contracting at rate sigma. No tangential hyperbolicity and no comparison with source contraction rates is required for this conclusion.
Argument: chi = x - phi(psi0(x)) vanishes on the graph. A converse Lyapunov metric on the compact forward-invariant U gives |chi(t)| <= |chi0| e^{-sigma t} + c L_s E0 / sigma while the decoded state stays in U. The decoded state is then an O(E0/sigma)-pseudo-orbit of g, so it stays in U by the inward condition.
Conclusions: a forward-invariant tube of width O(E0/sigma), and as E0 -> 0 closed-loop omega-limit sets converge into phi(A) (upper semicontinuity).
**Limit:** a C^2 phi on U essentially requires the rate condition, so this covers only 30/810 Lorenz and 163/810 Rössler runs.

**4.4 Continuous phi, hyperbolic source (SKETCH, relies on standard theorems not re-derived).** If A is uniformly hyperbolic, e = 0, and the quotient cocycle is uniformly contracting, then E is continuous, dominated, and has an invariant complement, so M is a **hyperbolic set of the closed loop in R^n; no smoothness of phi is needed**. phi(W^u) lies in W^u(phi(s)), since backward differences decay exponentially, so W^u(M) is in M and M is an attractor by invariance of domain. Structural stability of hyperbolic sets then gives, under C^1-small perturbation, a nearby orbit-equivalent attractor at distance O(perturbation).
Without an exact reference (e != 0, no C^1 psi0 may exist): Palmer-type shadowing along the driven orbit, assuming J has an exponential dichotomy off the flow direction, gives a true orbit within c ||d||, with c of order 1/|lambda_perp| in the transverse part. Shadowing does not need lambda_perp < 0, only != 0: the sign decides attracting versus saddle. Lorenz and Rössler are not uniformly hyperbolic, so **this does not cover the paper's numerics**.

**4.5 Any attractor (SKETCH, standard Conley-type).** If M is asymptotically stable for the exact loop, then C^0-small perturbation leaves an attractor in any given neighbourhood.

**4.6 Non-uniform: the naive theorem is FALSE in general.** lambda_perp < 0 for the natural measure with positive transverse rates on embedded orbits is the bubbling setting of Ashwin-Buescu-Stewart 1994: low noise triggers intermittent bursts, so no O(e) sup bound can be expected. The example of 3.2 with sign-changing A22 - A12 Dh should realize this (test, not run).
Weaker statement (PROVED at the linear level only): for eta' = L_perp(t) eta + d, |d| <= eps, with moment exponent L(q) = lim (1/T) log E ||Psi_perp(T)||^q < 0 and q >= 1, Minkowski gives ||eta||_{L^q(mu)} <= c eps q / |L(q)|, so mu{|eta| > x} <= (c eps q / (|L(q)| x))^q. L(q)/q interpolates between lambda_perp (q -> 0) and the uniform rate (q -> inf).
Prediction (CONJECTURE): stable-by-lambda_perp runs that fail have L(q) > 0 at moderate q, or positive transverse rate at source fixed points. This is a cheap untested candidate for the 163/761 Lorenz and 72/297 Rössler failures.

## 5. Literature (partial)

| Source | How much was read | Overlap |
|---|---|---|
| Oishi et al. arXiv:2602.11069 | Theorems and methods sections of the full text | Their Theorem 1: Im B in an A-invariant subspace implies the remaining eigenvalues persist. This is the **linear case of QB = 0 (3.3): known**. They also state controllability lets feedback relocate all eigenvalues (compare pole placement) and use a partially hyperbolic set with HPS Theorem 5.5 for attraction (compare 4.4). I saw no zeros/factorization statement in the parts read; not read in full. |
| Oishi et al. arXiv:2606.24303 | Abstract, keyword scan | Same design programme under partial observation. No overlap seen; not read. |
| Hara & Kokubu 2024 | Introduction and setup only | Degenerate reservoir, logistic map, smooth conjugacy on the attractor (their Theorem 1). Overlaps Prop. 1 in spirit. Section 4 not read. |
| Hara & Kokubu 2026 | **Not read** (SIAM 403 again; no preprint found). Search snippet only: conjugacy under mild conditions. Slides located (math.bu.edu/BKT2024/slides/Hara.pdf) but download failed; a search snippet mentions fiber contraction and structural stability. | **Must be read before claiming 4.4 is new**; it may be closely related. |
| A. Hart 2024 Physica D (arXiv:2211.09515) | Keyword scan, one section | GS existence, linear closed form, embedding on fixed points; autonomous field diffeomorphic to source on an embedded open set (compare Prop. 1). No closed-loop stability theorem found in the scan. Note: this is Allen Hart; the rate condition is Joseph Hart (Chaos 2024), not re-read here. |
| Wikner et al. arXiv:2211.05262 | Search summary only | Jacobian regularization as comparison method. Exact form not verified. |
| Ashwin, Buescu, Stewart 1994 | Abstract-level | Bubbling (4.6): known. |
| Freudenberg & Looze 1985; Iglesias 2002 (LTV analogue) | Secondary sources | Frequency integral of 3.1 is the Bode type: known as control theory, its application here apparently new. |
| Byrnes, Isidori, Willems 1991 | Summary | Passivity and zero dynamics: known in control. |
| Palmer 1988; Chow, Lin, Palmer 1989 | Bibliographic | Shadowing via dichotomies: known. |

Status of results, **provisional, since the search was short and one search for a zero-dynamics treatment of RC found none (absence of evidence only)**:
- Prop. 1: known in substance (Hara-Kokubu, A. Hart for embeddings).
- Prop. 2, Prop. 4, the factorization and the zero-dynamics identification, the loop identity, the restricted small gain, the non-existence of exact linear reservoirs for chaos: apparently new in this setting, not verified.
- QB = 0: known in the linear case (Oishi). Observer reading of Prop. 4: standard observer structure, application apparently new.

## 6. Not done

- No numerics. Priority tests: sum rule on a tanh reservoir; the 4-d Lorenz example with phi = (s, h(s)); looseness of the small-gain bound; L(q) and fixed-point rates against failures.
- Hara & Kokubu 2026 and the remainder of Hara & Kokubu 2024, Joseph Hart 2024, Wikner; further observer and synchronization-stability search (e.g. master stability work).
- Full written proof of 4.3 with constants; verification of 4.4 against textbook statements.
