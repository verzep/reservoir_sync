# Literature map: a surrogate driven by a source, decoded, then closed on itself

Date of search: 30–31 October 2026. "Apparently new" means I looked in the places listed and did not find it. It is not a guarantee.

Evidence labels:
- **[text]**: I read the relevant passage in the full text.
- **[abstract]**: only the abstract or a search snippet.
- **[meta]**: only the bibliographic record was verified. Anything said about the paper is a lead, not an attribution.

## 0. Main findings

**Two preprints from this month sit directly on the paper's question:**

- **Bizyaeva, Castaños, Moreno, arXiv:2610.04343 (3 Oct 2026)**, "A KKL Observer Perspective on Reservoir Computing".
- **Saqib, Padoan, arXiv:2610.08987 (6 Oct 2026)**, "The internal model principle in reservoir computing".

They answer the brief's question about observers: **a synchronized response with a decoder is a known observer structure**, the Kazantzis–Kravaris/Luenberger (KKL) observer. The closed loop has also been derived in that literature as an "output predictor" (Janny et al. 2021). Section 3 says exactly what they leave open.

**Claim (i) as implemented in this repo is already published.** `readout.feedback_gram` (ridge + mu sum_t ||N^T B_t||^2, with B_t = D_s f(r_t, s_t)) is the continuous-time form of Wikner et al.'s Jacobian plus Tikhonov regularization, eq. (10) there.

**Hara & Kokubu 2026 is now read in full (Sec. 3a).** It takes nothing from the planned list. It is discrete-time, C^1, with strong fiber contraction, and its neighbourhood hypothesis (H) assumes the stability this paper studies. It does overlap the hyperbolic-set result in the theory notes.

**Claim (d) has classical roots.** Its integral is the directional form of the derivative construction in Stark 1999, and Rulkov & Afraimovich 2003 say in words why unstable directions should be harmless. The theorem itself was not found.

## 1. Classification

| Claim | Class | Decisive passage |
|---|---|---|
| (a) Conjugacy on the manifold; decoder differential maps velocities | **KNOWN** [text] | A. Hart 2024 Sec. 5; Bizyaeva Prop. III.1 B; Hara & Kokubu 2026 Thm 2.24 (discrete); Lu et al. 2018 II C; Stark 1999 Sec. 1.1 for the driven graph |
| (b) g_hat - g = e_dot + N^T d and its reading | **APPARENTLY NEW**, elementary | Absent from Bizyaeva Prop. IV.1, Janny Prop. 1, Saqib & Padoan [text] |
| (c) ker N^T transverse, Q A_c, block-triangular | **PARTLY KNOWN**: linear constant-coefficient case known [text]; ideal-decoder special case known [text]; nonlinear time-varying form for the actual readout apparently new | Saqib & Padoan Remark 1; Oishi Thm 1; Hara & Kokubu Thm 2.24 (4) |
| (d) Exponents survive without a differentiable map | **PARTLY KNOWN**: ingredients and heuristic known [text]; the theorem apparently new. Hara & Kokubu assume C^1, so no overlap [text]. Hunt–Ott–Yorke body unread | Stark 1999 Sec. 4.1; Rulkov & Afraimovich 2003 Sec. V |
| (e) Transverse differs from conditional; kernel condition | **PARTLY KNOWN**: difference known for LTI [text]; systematic gap and kernel condition apparently new. The draft's "only if" is false (theory notes) | Saqib & Padoan eq. (32); J. D. Hart 2024 II E; Oishi Thm 1 |
| (f) Exact counterexample | **KNOWN** for linear systems [text]; chaotic version not found | Saqib & Padoan Sec. V-A; Rivkind & Barak 2017 |
| (g) Transverse exponent predicts failure | **PARTLY KNOWN**: criterion known [text]; three-way comparison apparently new; 513/810 is the draft's own | Lu et al. III; Oishi; Saqib & Padoan Remark 1 |
| (h) W + V N^T = R_dot R^+, rank-deficient and ridge | **PARTLY KNOWN**: one line from DMD with known control [text]; explicit identity and ridge version not found | Proctor et al. 2016 eq. (17)–(18); Bollt 2021; Kaplan et al. 2026 |
| (i) N^T B penalty beats ridge | **KNOWN** as implemented [text]; only the fixed-B form and the loop-gain derivation remain | Wikner et al. 2024 eq. (10), Table 4 |

## 2. Evidence by claim

**(a)**
- Lu, Hunt, Ott [text, II C]: with exact post-processing, listening and predicting reservoirs agree, phi(A) is invariant, and its dynamics seen through psi are "equivalent" to those of A. Discrete time, continuous phi.
- A. G. Hart 2024 [text, Sec. 5]: if the map is an embedding on an open set, the autonomous system "defines a vector field on f(Omega) which is diffeomorphic to the source vector field". This is the draft's statement, in vector-field language.
- Bizyaeva Prop. III.1 B [text]: global minimizer, exact readout on the GS graph, and closed-loop reproduction are equivalent, for uniformly contracting reservoirs in continuous time.
- Hara & Kokubu 2024 [text, Thm 4 and Sec. 5.2]: proved only for a "degenerate" reservoir whose update does not depend on r; the view "has not been verified" in general. Hara & Kokubu 2026 [text, Sec. 3a]: Thm 2.24 gives the exact conjugacy for general reservoirs in discrete time; Thm 5.1 and 5.4 treat approximate readouts.
- The draft's no-derivative version for a linear readout adds only that no D phi is needed, and Bizyaeva's proof also uses only trajectories.

**(b)** Bizyaeva Prop. IV.1 [text, including proof]: forecast error at most eps(1 + L_w L_u (e^{L_g s} - 1)/L_g) plus an initialization term, by Gronwall. It uses the Lipschitz constant of the closed loop, with no time-derivative term and no decomposition. Janny Prop. 1 [text] bounds k L2 e^{-lambda h + L1 p}|z_0^y| from initial mismatch only. Saqib & Padoan treat exact readouts. Nothing read states the identity. It takes a few lines, so it has value as a reading rather than as a discovery. The system-identification literature on equation error against simulation error is unread (Narendra & Parthasarathy 1990 [meta]).

**(c)**
- Lu et al. [text, II D]: "it is not clear in advance which perturbations correspond to transverse Lyapunov exponents".
- Saqib & Padoan [text, Prop. 3, Remark 1], linear reservoir and exosystem with sigma(S) on the imaginary axis: (F + G Wout) Pi = Pi S. In coordinates (Pi^+ x, N^T x), where their N spans ker Pi^T, the matrix is block upper triangular, and they call the other block's eigenvalues "transverse".
- My remark: their complement is orthogonal to the invariant subspace, not the readout kernel, but quotient spectra do not depend on the complement, so in that setting the draft's Q A|ker gives the same numbers. On the draft's example both give +1.
- Oishi 2602.11069 [text, Thm 1, Cor. 2]: Im(Win) in an A-invariant subspace pins N-D' eigenvalues for any Wout.
- Also check: J acts as A_c on the kernel (V drops out). I found this in no paper, but it is immediate.

**(d)** This is the claim the brief says these sources decide.
- **Stark 1999 [text; I read Secs. 1, 1.4 and 4.1 closely, the rest by keyword scan].** Theorem 1.3: if lambda + (1+gamma) mu < 0, with mu the global bound on log||Df^{-1}||, then Phi is Whitney C^{1+gamma}. Theorem 1.7 is the non-uniform version on nested sets. The candidate derivative A* is the fixed point of the graph transform Gamma_L(phi,A)(x) = D1 g . Df^{-1} + D2 g . A(f^{-1}x) . Df^{-1} (Sec. 4.1), which contracts at rate lambda + mu. Unrolling this is exactly the discrete form of the draft's y(t) integral (my observation). **But Stark's condition is global in mu**, and he states no version direction by direction, no result below the rate, and nothing about a closed loop. "Unstable" appears only in his remark on centre-unstable manifolds, where he warns such manifolds are not unique, so x' need not lie in the one through x (Sec. 1.3). That warning is why the draft's admissibility hypothesis matters.
- **Rulkov & Afraimovich 2003 [text, final section]:** "it is possible to understand (although it is not so simple to prove) that the dependence on the unstable coordinate is non-essential in the hyperbolic situations". This is the physical content of (d), stated as a heuristic and not about exponents or closed loops.
- **Hunt, Ott, Yorke 1997: abstract only** (APS returned no PDF to a plain request). Secondary accounts read [text]: Fernandez & Quas 2018 give the condition Lyap(f^{-1}) + log gamma < 0 for Whitney differentiability and K gamma < 1 uniformly; the Chaos synchronization review (arXiv:2412.20649) gives the Hölder exponent as the ratio of transverse contraction to the smallest drive exponent; J. D. Hart 2024 II C gives lambda(filter) < lambda_j(drive) for smoothness. **I cannot exclude that the body discusses directional differentiability; this is the last thing to check.**
- Lu et al. [text]: much of the spectrum is reproduced "in practice" without guaranteed differentiability, no mechanism. Saqib & Padoan Prop. 6 (i) and A. Hart give integral formulas for the map, not for its derivative. Neither Bizyaeva nor Saqib & Padoan mention exponents or non-differentiable maps [text].
- **Verdict:** the integral is classical, and the reason it should work is folklore. What I found nowhere: N^T y = xi, its transfer to closed-loop exponents, and a statement below the rate condition. Present it as a direction-by-direction refinement of Stark, not as a new construction. Theory notes correct the draft here: E is not TM, since admissible directions exclude negative exponents.

**(e)**
- J. D. Hart 2024 [text, II E]: "one might expect" the non-target exponents to "stay close to the CLEs", with "We find that this is often the case". The draft's 808/810 and 810/810 contradict this directly. This is the sharpest empirical contribution.
- Saqib & Padoan eq. (32) [text]: lambda_tr = N^T F N + kappa N^T G, any real value attainable by an exact readout. So for LTI the transverse exponent is not bounded by the driven one.
- Oishi 2606.24303 [text] writes "Transverse Lyapunov exponents (TLEs), also called conditional Lyapunov exponents (CLEs)", so the conflation is live.
- Kaplan et al. 2604.05967 Thm III.2 [text]: for linear reservoirs with data second moments, exactly rank(C_rr) eigenvalues are dominant and the rest stay below -lambda. Their min-norm readout vanishes on ker C_rr. This needs comparing with the draft's instabilities, which need a readout component off the data.
- A_c ker N^T subset ker N^T: not found. **Correction from theory notes:** the draft's "only if" is false as a spectral claim, because Q B = 0 also gives coincidence. That is the nonlinear form of Oishi's input-side condition, so the condition should be stated as sufficient, with Oishi cited.

**(f)** Saqib & Padoan Sec. V-A [text]: a three-node linear reservoir driven by a sinusoid, every exact readout is Q Pi^+ + kappa N^T, unstable for kappa > 17.6 "despite zero training error", with a figure. Transients select kappa. Rivkind & Barak 2017 [text]: open-loop stability "does not guarantee stability of the closed loop". The draft's example has a decaying source whose attractor is a point, and it names the mechanism. **Keep it only as an illustration, and cite these.** Theory notes have a chaotic version by direct substitution; I found none in the literature, and that is the one worth keeping as a result.

**(g)** Lu et al. [text, III]: climate loss coincides with an exponent crossing zero. Lu & Bassett [text, App. A2]; Oishi 2602 [text]; Saqib & Padoan Remark 1 ("decided ... by the transverse eigenvalues"). J. D. Hart 2024 [text] reports the conditional exponent as the indicator. Du & Wang 2607.17909 [abstract and scan]: best spectral radius matches no Lyapunov edge and they propose a different index, using conditional exponents on the driven reservoir; a possible tension. I found no paper comparing the three predictors on one ensemble (searches in Sec. 6). The draft's Lorenz result, where training error predicts as well, must stay in the claim.

**(h)** Proctor, Brunton, Kutz 2016 [text, Sec. III-B]: with B known, X' - B Upsilon = A X, so A = (X' - B Upsilon) X^+. With X' = R_dot, B = V, Upsilon = S this gives W = (R_dot - V S) R^+, and with N^T = S R^+ then W + V N^T = R_dot R^+ (one line, mine). So the identity is the statement that known-input DMD plus the readout equals plain DMD. Bollt 2021 [text]: linear RC equals VAR, link to DMD "not complete", discrete with delays. Kaplan et al. [text]: Wout = U R^+, Wout Win = U B1^+ (Lemma IV.1), backward DMD on filtered history (Cor. IV.3), not (R_dot, R). Gulina & Mauroy 2021 [text, scan]: reservoir as EDMD dictionary, not the closed-loop generator. Ridge and rank-deficient versions: not found; I could not check them against the draft, which has only full rank. **Theory notes and Saqib & Padoan Cor. 7 [text] add a limit:** exact prediction with a linear reservoir requires a finite linear realization, so the exact case is impossible for chaos and the identity is a least-squares statement there.

**(i)** Wikner et al. 2024 [text; Sec. 2.3.2, 2.4, 3.2, 4, App. A]. Jacobian penalty eq. (10): beta_J sum ||W grad_u g_o(s_{j-1}, u_j)||_F^2 evaluated along the driven trajectory, the discrete form of the repo's sum_t ||N^T B_t||^2. Table 4 on Kuramoto–Sivashinsky (1000 test predictions):

| Regularization | Stable | Median valid time (Lyapunov times) |
|---|---|---|
| None | 0/1000 | 0.05 |
| Jacobian only | 0/1000 | 0.25 |
| Tikhonov only | 565/1000 | 0.71 |
| Jacobian + Tikhonov (K=1) | 1000/1000 | 2.88 |
| Noise + Tikhonov | 1000/1000 | 4.24 |
| LMNT + Tikhonov (K=4) | 1000/1000 | 4.27 |

What this means for (i):
- **Supports the claim:** combined with Tikhonov, the K=1 penalty beats Tikhonov alone in stability (1000/1000 against 565/1000). The repo's comparison is therefore a replication on other sources.
- **Limits it:** the penalty alone fails completely, so it cannot replace ridge. Wikner's own conclusion is that Jacobian + Tikhonov "make substantially less accurate short-term forecasts" than noise or LMNT, and App. A shows K=1 gives 2.88 rising to 4.27 at K=4. Any claim here needs a K > 1 and noise-training baseline.
- **What remains:** the fixed-B reduction for affine input, the loop-gain derivation from claim (b), and exponent-level evidence. My remark: `transverse_penalty` (||N^T A_c||) is not the same object, since LMNT at K=2 penalizes N^T A_c B. I did not find it, but did no dedicated search.
- Reinhart & Steil 2012 [abstract/snippet only, no open copy found] propose regularizing the reservoir as well, for output feedback.

## 3. What the two October preprints leave open

Both read in full, apart from figure-only material and routine setup. Both acknowledge each other.

| | Bizyaeva et al. 2610.04343 | Saqib & Padoan 2610.08987 |
|---|---|---|
| Setting | Continuous time, uniformly contracting nonlinear reservoir, general readout | Linear reservoir and linear exosystem (A3: distinct eigenvalues on the imaginary axis); nonlinear part local near an equilibrium with no stable or unstable exosystem modes (A5–A7) |
| Main results | Prop. III.1 equivalence; IV.1 Gronwall forecast bound; V.1 gap from linearity | Prop. 3 internal model; Remark 1 free transverse eigenvalues; Prop. 6 integral map; Cor. 7 linear reservoirs need linear realizations; Sec. V-A instability and infinite gain at signal frequency |
| Chaotic sources | Compact set allowed, so covered formally by III.1 and IV.1, but the bound grows as e^{L_g s} and says nothing on transverse stability. Chaos appears only as motivation | Excluded by A3 and A7 |
| Non-differentiable maps | Not addressed; Prop. V.1 assumes C^1 | Not addressed; C^2 by center manifold |
| Nonlinear time-varying transverse operator | Absent. "Transverse stability" appears only in the abstract, as something KKL theory could inform | Absent. Nonlinear section stops at the invariant manifold and immersion; Cor. 7 has no transverse analysis |
| Lyapunov exponents, conditional vs transverse | None | None; eigenvalues only |
| Numerics on trained chaotic reservoirs | None | None; a three-node sinusoid and a pendulum |
| Error identity (b), kernel condition | Absent | Absent |

Saqib & Padoan's conclusion explicitly lists as open "the interplay between the cost minimized by training and the closed-loop dynamics of the predictor", which is close to this paper's central question.

**Observer thread: closed-loop stability.** Janny et al. 2021 [text]: an output predictor is a contraction plus a generating model g(z) = G(z, psi(z)), and they use "open-loop" for what RC calls closed loop, so searches must use both words. Their Prop. 1 and 2 bound error only, growing exponentially with horizon. Andrieu & Praly 2006 [text, Thm 2.2] covers the driven observer only: continuity and uniform injectivity suffice, which parallels the draft's continuous assumption. **I found no closed-loop stability theorem in the KKL literature read or in one targeted search, except the linear Remark 1 above.** Bernard et al. 2022 survey and Nijmeijer & Mareels 1997 bodies are not read (Sec. 6), and neither decides a classification.

## 3a. Hara & Kokubu 2026 (read in full)

M. Hara, H. Kokubu, SIAM J. Appl. Dyn. Syst. 25(3), 1834–1867 (2026) [text, all 34 pages]. Quoted items below are from the PDF supplied by the user.

**Assumptions, precisely**

| Item | Statement | Where |
|---|---|---|
| Time | **Discrete only**: x_{n+1} = f(x_n), r_{n+1} = tau(A r + C phi(x) + b) | Sec. 1, eq. (1.1) |
| Source | M closed C^1 manifold, f in Diff^1(M), attractor Lambda, ergodic mu, supp mu = Lambda, x_0 generic | (T1), (T4), (*), (**) |
| Observation | phi: M to R^m a C^1 **embedding**, so effectively full state | Main Thm 5.1 |
| Reservoir | N > 2d; **strong fiber contraction** ||dF/dr|| < kappa << 1; rank D tau = N; (#) moment matrix invertible (dropped with ridge) | (R1)–(R3) |
| Smoothness of map | **C^1, by the C^r section theorem**, whose condition kappa ||Df^{-1}|| < 1 is the rate condition. Non-differentiable maps are excluded. Embedding for generic Omega | Thm 2.4, 2.15 |
| Target for semiconjugacy | f **positively expansive on Lambda** and POTP on Lambda | (T2), (T3) |
| Target for conjugacy | f **C^1 structurally stable** | (T2'), Thm 5.4 |
| Ideal decoder | gamma-hat = gamma compose pi, with pi the **normal tubular projection**, so constant on normal fibres | Lemma 2.23, Thm 2.24 |
| Neighbourhood control | **(H)**: d_C0(U)(gamma-hat, phi^{-1} W) small on a trapping region U of both attractors. **(H')**: same in C^1 for conjugacy. Called an "open problem" for (H') | Thm 5.1, 5.4, Rem. 1.3 |
| Hyperbolicity | Not assumed directly; enters as POTP and expansiveness, or structural stability. Authors say Anosov maps qualify, and that weaker conditions covering the logistic map and "the Lorenz equations" are future work | Rem. 1.3 |

**Results.** Thm 2.15: generic C^1 embedding for nonlinear reservoirs. Thm 2.24: closed loop on s(M) is C^1 conjugate to f, and s(Lambda) is an attractor of the ideal closed loop. Cor. 3.11: regression output is C^0 close to the ideal one. Thm 4.19 and 5.1: under (H), the trained closed loop is weakly semiconjugate to f on Gamma_W. Thm 5.4: under (H') and (T2'), topologically conjugate.

**Passage-level verdicts**

- **(a) Now firmly KNOWN, for discrete time.** Thm 2.24 (2): "(F-tilde_gamma, s(M)) and (f, M) is C^1 conjugate", by a one-line commutation, as in the draft. Approximate-readout versions (Thm 5.1, 5.4) go beyond the draft's exact case. The continuous-time statement rests on A. Hart and Bizyaeva.
- **(c) Not taken, but the decoder-fibre idea is there.** Thm 2.24 (4) shows the ideal closed loop contracts toward the manifold because gamma-hat is constant on normal fibres, and the proof is only dist(F(gamma(pi r), r), M) <= kappa |r - pi r|. There is no Q, no ker W, no variational equation, and no treatment of the fibres of the actual readout. **My reading in the draft's language:** gamma-hat is a decoder whose kernel is the normal bundle, so Q is orthogonal and ||Q A|| <= kappa. A trained W has oblique kernel and ||Q|| may be large. That gap is exactly what (c) measures, so HK is the special case that makes (c) look safe. Lu et al.'s remark that stability depends on the extension of psi is the same point.
- **(d) Not touched.** HK assumes C^1 and never discusses non-differentiable maps, tangent directions, or exponents; "Lyapunov" appears only in a reference title. **Claim (d) needs no change on this account.**
- **(e) Not touched directly.** No conditional or transverse exponents. It does supply a regime where driven contraction does carry over: kappa << 1 with the ideal decoder. This is compatible with the draft's gap, since neither condition holds for trained W.
- **(g) Not touched, and in some tension.** No exponents, no failure statistics, no predictor comparison. The tension is below: the Remark on Thm 5.1 says (H) holds with high probability for large N and T, yet the draft finds 513/810 transversely unstable runs on Rössler. Those runs fail any trapping-region hypothesis. The regimes differ (kappa << 1, N and T large; Rössler is also outside their class), so this is not a contradiction, but the paper must say why.

**Two points in HK to raise (my reading, to be checked by a dynamicist before anyone relies on them)**

1. **(H) carries the transverse stability, and Cor. 3.11 does not obviously supply it.** The corollary fixes "a small neighborhood" U of Gamma, then derives closeness on U from closeness on Gamma "because W_T, phi and gamma are continuous". Continuity at fixed W gives a neighbourhood depending on W, while Claim 5.3 needs F-tilde_W(closure U) inside U for a U whose trapping margin is fixed by the ideal system. A sketch of what (H) requires: on a tube of radius rho, sup_U |W - phi gamma-hat| is at least of order ||W restricted to normal directions|| rho, and the margin is of order (1 - kappa) rho, so (H) implies roughly L_x ||W_normal|| < 1 - kappa. That is a **small-gain condition on the readout in normal directions**, which is what the draft's transverse exponent and the N^T B gain measure. So (H) assumes away the failure this paper studies. Regression only controls W on the data.
2. **(T1) and (T2) together look vacuous as written.** Def. 4.12 takes positive expansiveness on Lambda with j >= 0, and f is a homeomorphism of Lambda by (T1). A homeomorphism of a compact metric space is positively expansive if and only if the space is finite (Richeson & Wiseman 2004 [abstract]). Directly: two points on one local stable manifold of an Anosov map never separate forward. So the sentence "every Anosov diffeomorphism ... satisfies assumptions (T1)–(T4)" does not hold for (T2) as defined; Cor. 4.11 gives two-sided expansiveness only. Natural repair: Rem. 4.18 notes the two-sided shadowing lemma covers the hyperbolic case when G is a homeomorphism, which restricts the closed loop. Thm 5.4 is unaffected. Smaller points: "Lip(pi) becomes arbitrarily small" in Claim 2.25 cannot hold since pi is idempotent, though the conclusion of Thm 2.24 (4) follows without it; and F-tilde_W uses phi^{-1}(W r), which is undefined when W r leaves phi(M).

Neither point is grounds to attack the paper. The theorems stand in their hypotheses and repaired form. The practical consequence is that citing "Hara & Kokubu prove trained reservoirs reproduce f" would overstate it.

**Comparison with `docs/theory_notes.md` Sec. 4 (ba76331)**

| Theory-notes result | Status against HK | What stays distinct |
|---|---|---|
| 4.1 Tube theorem (PROVED) | **Partly there.** Claim 5.3 (ii): under C^0 closeness to an exact decoder on U, the closed loop keeps a trapping region. No hyperbolicity is used in that step, as in the tube | Continuous time; actual readout kernel, with contraction of L = QA + Q' rather than kappa << 1 with normal fibres, so kappa near 1 is allowed (checked at kappa near 1); explicit radius O(delta/sigma); no fixed (H)-type gain assumption beyond contraction |
| 4.1 Upper semicontinuity | **Partly there.** Thm 5.1 gives h with d_0(h, id) < eps, so Gamma_W is near Gamma_gamma | Theory version needs no (T2), (T3) |
| 4.1 Forecast bound in source coordinates | **New relative to HK**, which has no forecast bound | Compare Bizyaeva Prop. IV.1 |
| 4.2 Converse Lyapunov | **Not there** as a statement. Same spirit as Claim 5.3 | No regularity of phi; requires only Lipschitz inverse. Standard argument, so small |
| 4.3 Hyperbolic set, structural stability (SKETCH) | **Conclusion already there** for C^1 maps and diffeos: Thm 5.4 (structural stability, C^1 closeness, conjugacy) and Thm 5.1 (shadowing, C^0, semiconjugacy) | Only the hypotheses differ: no C^1 phi, quotient contraction instead of kappa << 1, flows and hyperbolic sets rather than closed manifolds. Remains a SKETCH. Treat as a remark citing HK and Oishi, not a result |
| 4.3 Shadowing variant, saddle case (SKETCH) | **Partly there**: POTP tracing is HK's core tool | Dichotomy along the driven orbit and lambda_perp != 0 not assumed negative: not in HK |
| 4.4 Bubbling, moment bound | **Not there** | Non-uniform case is outside HK entirely |
| Sec. 3 factorization, chaotic no-go, quotient operator | **Not there** | No transverse operator in HK |

## 4. Threads

**Generalized synchronization.** Afraimovich et al. 1986; Pecora & Carroll 1990; Rulkov et al. 1995; Abarbanel et al. 1996; Kocarev & Parlitz 1996; Pyragas 1996; Pecora et al. 1997; Boccaletti et al. 2002; Badii et al. 1988; Pecora & Carroll 1996; Davies & Campbell 1996 [all meta]. Stark 1999 [text]; Stark 1997, Josić 1998 [abstract or meta]; Grigoryeva et al. 2021 [text, intro].

**Observers and estimation.** Kazantzis & Kravaris 1998 [meta]; Pachy et al. 2024 and Galimberti et al. 2026 (as reported by Bizyaeva). Parlitz 1996, So et al. 1993, Yu & Parlitz 2008, Yang et al. 2006, Duane et al. 2006, Abarbanel et al. 2009, Creveling et al. 2008, Morgül & Solak 1996, Nijmeijer 2001 [meta].

**Control.** Isidori & Byrnes 1990; Byrnes & Isidori 2003; Francis & Wonham 1976 [meta], used through Saqib & Padoan, who identify the invariance equation with the Francis–Byrnes–Isidori equations. Astolfi & Ortega 2003, Zames 1966 [meta].

**RC closed loop.** Platt 2021 [text]: "predictive GS"; train/test evaluation "gives no indication of the stability of the forecast". Hara & Kokubu 2024 [text]: one-step success with dynamic failure. Multistability: Flynn 2021, 2023; Röhm 2021; Gauthier 2022; Zhang & Cornelius 2023; Ceni 2020 [meta]. Zhang et al. 2025, Liu et al. PRR 2026, Santos & Bollt 2025 [abstract].

**Free-run failure in general.** Rivkind & Barak 2017 [text]; Mastrogiuseppe & Ostojic 2019 [abstract]. Williams & Zipser 1989; Doya 1992; Narendra & Parthasarathy 1990; Venkatraman et al. 2015; Mikhaeil et al. 2022; Park et al. 2024; Berry & Das 2025; Hess et al. 2023 (arXiv:2306.04406); Ross et al. 2011 (arXiv:1011.0686) [meta]. Lower priority: they do not address the driven-then-closed structure.

**Author's paper.** Verzelli, Alippi, Livi, Chaos 31, 083119 (2021) [text]: driven phase and generic targets, no closed loop ("in absence of an output feedback mechanism"), Theorem 2 on an injective map. No self-overlap. 34 citing papers screened by title.

## 5. Journals and pitch

- **Chaos** is the home of the physics line (Lu 2018, Platt 2021, Bollt 2021, J. D. Hart 2024, A. G. Hart 2025, Suetani & Parlitz 2026 in the special collection "Nonlinear Dynamics of Reservoir Computing"). Pitch: mechanism plus diagnostic.
- **PRL** carried Rivkind & Barak 2017 and Pathak 2018; PRE and PRR publish Kobayashi 2021, Grigoryeva 2021, Wong 2024, Zhang & Cornelius 2023, Liu 2026.
- **SIADS, JDDE, Nonlinearity, Physica D**: theorem-led.
- **Control preprints** (eess.SY): the two new papers pitch RC as a rediscovery of classical theory.

**Six to read in full** (one more than asked, because the two new preprints displaced the older list)
1. **Saqib & Padoan 2026.** Biggest threat: block-triangular form, free transverse modes, zero-error instability, for linear systems.
2. **Bizyaeva et al. 2026.** Threat to (a) and the framing; a source of theory to borrow.
3. **Stark 1999.** The classical root of (d).
4. **J. D. Hart 2024.** Support: the expectation (e) refutes.
5. **Oishi et al. 2602.11069.** Same failure story for nonlinear reservoirs, constructive fix, input-side dual.
6. **Wikner et al. 2024.** Decides (i).

## 6. Where I looked and what cannot be upgraded

**Searched:** OpenAlex citing lists of Verzelli 2021 (all, titles), Lu 2018, J. D. Hart 2024, Hara & Kokubu 2024, Platt 2021 (2023 on, keyword filtered on title and abstract). arXiv API on abstract terms: reservoir with transverse/readout, closed-loop/conditional Lyapunov, transversal/GS, DMD/closed-loop, internal model, spurious/closed-loop, echo state/output feedback/regularization, surrogate/vector field, teacher forcing/chaotic, loop gain, Luenberger/Kazantzis. About fifteen web searches. Most arXiv keyword queries returned little, and the KKL query found preprints that an earlier web search missed, so misses-only verdicts are weak evidence.

**Could not reach [text], and why:**
- **Hunt, Ott, Yorke 1997:** APS gave no PDF to a plain request; Hunt's page has no copy. Abstract plus three secondary accounts. **It could affect (d).**
- **Hara & Kokubu 2025 (Chaos), Reinhart & Steil 2012:** behind a bot check and a paywall. Neither decides a classification; Wikner settles (i).
- **Bernard et al. 2022, Nijmeijer & Mareels 1997:** downloads returned HTML. Neither decides a classification.

If the user saves the APS PDF, it can be read in minutes. Hara & Kokubu 2026 was read from the PDF the user supplied.

**Identifiers**
- New: arXiv:2610.04343, 2610.08987, 2604.05967, 2607.17909, 2602.11069, 2606.24303, 2211.09515 (A. Hart), 1802.06364 (Fernandez & Quas), 2412.20649 (review), 1409.6358 (Proctor).
- Verzelli 10.1063/5.0056425; Lu 2018 10.1063/1.5039508; Lu & Bassett 10.1063/5.0004344; J. D. Hart 10.1063/5.0196257; A. G. Hart 2024 10.1016/j.physd.2023.133956; A. G. Hart 2025 10.1063/5.0301957.
- Platt 10.1063/5.0066013; Bollt 10.1063/5.0024890; Suetani & Parlitz 10.1063/5.0283017; Wong 10.1103/PhysRevE.110.064219; Rivkind & Barak 10.1103/PhysRevLett.118.258101; Mastrogiuseppe & Ostojic 10.1162/neco_a_01187.
- Wikner 10.1016/j.neunet.2023.10.054; Reinhart & Steil 10.1016/j.neucom.2012.01.032; Zhang 10.1063/5.0262977; Liu 10.1103/5nbr-bqxb; Santos & Bollt 10.1063/5.0278709.
- Hara & Kokubu 10.1007/s10884-022-10159-w, 10.1137/24M1714617, 10.1063/5.0273628; Grigoryeva 10.1088/1361-6544/ace492, 10.1103/PhysRevE.103.062204.
- Andrieu & Praly 10.1137/040617066; Kazantzis & Kravaris 10.1016/S0167-6911(98)00017-6; Janny 10.1109/CDC45484.2021.9683277; Bernard 10.1016/j.arcontrol.2021.11.002; Nijmeijer & Mareels 10.1109/81.633877.
- Isidori & Byrnes 10.1109/9.45168; Byrnes & Isidori 10.1109/TAC.2003.817926; Francis & Wonham 10.1016/0005-1098(76)90006-6; Astolfi & Ortega 10.1109/TAC.2003.809820; Zames 10.1109/TAC.1966.1098316.
- Tu 10.3934/jcd.2014.1.391; Proctor 10.1137/15M1013857; Gulina & Mauroy 10.1063/5.0026380; Hunt, Ott, Yorke 10.1103/PhysRevE.55.4029; Stark 10.1016/S0167-2789(97)00167-X, 10.1017/S0143385799126555; Josić 10.1103/PhysRevLett.80.3053; Rulkov & Afraimovich 10.1103/PhysRevE.67.066218; Richeson & Wiseman 10.1155/S0161171204312184.
- Other papers named in Sec. 4 without a DOI here were resolved through Crossref or arXiv in this work, except Pachy 2024 and Galimberti 2026, cited only as reported by Bizyaeva et al.

## 7. Verdict

**Not new, cite instead:** (a); (f) as a linear example; "open-loop stability does not imply closed-loop stability"; the linear block-triangular picture; the observer identification; (i) as implemented.

**Defensible as new, strongest first:**
1. **The measured transverse/conditional gap on trained chaotic reservoirs**, against J. D. Hart 2024's expectation, and the three-way predictor comparison. Neither preprint has any Lyapunov or chaotic numerics.
2. **The transverse operator Q A_c on ker N^T for nonlinear reservoirs along a chaotic orbit.** This extends Saqib & Padoan Remark 1 and answers Lu et al.'s question. Theory notes' repairs apply (tangent cones, E not TM).
3. **Survival of unstable and neutral exponents below the rate condition.** New as a theorem, subject to the Hunt–Ott–Yorke body, and to be framed as a directional refinement of Stark.
4. **A chaotic exact counterexample** (theory notes), since the published ones are linear.
5. **Sufficient conditions for coincidence** (kernel invariance, dual to Oishi's Q B = 0).
6. **The error identity (b) and R_dot R^+**, as short organizing results.

**What Hara & Kokubu 2026 removes:** nothing in the list above. Theory notes 4.3 (hyperbolic set plus structural stability) is not new as a conclusion and stays a remark citing HK. The tube theorem stays, with HK's trapping-region step cited as the discrete strong-contraction antecedent, and its novelty stated as the actual-readout contraction, the explicit radius and the source-coordinate forecast bound. The draft's sentence on "neighborhood control of the learned readout" should cite this paper explicitly, and should say that (H) is the hypothesis this work examines.

**Pitch.** Before October the pitch was "state reconstruction determines the vector field, and stable synchronization does not protect the closed loop". That no longer stands as new. The better pitch: *closing the loop is known to be an observer feedback, with transverse modes that training leaves free; for chaotic sources, and without a smooth map, here is what determines them, why driven diagnostics mislead, and how often it fails.* Open by citing the KKL connection rather than presenting synchronization as the framing.

**Urgency: high, measured in weeks rather than months.** The overlap is under a month old, the two groups are in contact (Bizyaeva et al. "look forward to future collaboration"), Saqib & Padoan name the training-to-closed-loop interplay as open, and Kaplan et al. share authors with both. In my judgment the nonlinear transverse question is a natural next step for them, but no paper I read says so. Post a preprint once the theory-note errors are fixed; the numerics are the part they cannot quickly reproduce.
