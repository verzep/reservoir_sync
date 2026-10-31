# Literature map: a surrogate driven by a source, decoded, then closed on itself

Date of search: 30–31 October 2026. "Apparently new" means I looked in the places listed and did not find it. It is not a guarantee.

Evidence labels:
- **[text]**: I read the relevant passage in the full text.
- **[abstract]**: only the abstract or a search snippet.
- **[meta]**: only the bibliographic record was verified. Anything said about the paper is a lead, not an attribution.

## 0. The main finding

Two preprints from this month sit directly on the paper's question:

- **Bizyaeva, Castaños, Moreno, arXiv:2610.04343 (3 Oct 2026)**, "A KKL Observer Perspective on Reservoir Computing".
- **Saqib, Padoan, arXiv:2610.08987 (6 Oct 2026)**, "The internal model principle in reservoir computing".

They answer the brief's question about observers: **yes, a synchronized response with a decoder is a known observer structure.** It is a Kazantzis–Kravaris/Luenberger (KKL) observer, and the closed loop has been derived in that literature as an "output predictor" (Janny et al. 2021). These preprints take (a) and, for linear systems, (c) and (f). They leave open chaotic sources, differentiability, the readout kernel as an explicit fibre, and the numerics. The paper must cite both and be repositioned around what they leave open.

## 1. Classification

| Claim | Class | Decisive sources |
|---|---|---|
| (a) Conjugacy on the manifold; decoder differential maps velocities | **KNOWN** | A. Hart 2024 Sec. 5; Bizyaeva et al. Prop. III.1; Lu et al. 2018 Sec. II C; Lu & Bassett 2020 |
| (b) g_hat - g = e_dot + N^T d and its reading | **APPARENTLY NEW**, but elementary | Not in Bizyaeva Prop. IV.1 (a Lipschitz bound) or elsewhere read |
| (c) ker N^T transverse, Q A_c, block-triangular | **PARTLY KNOWN**: known for linear reservoir and linear source; nonlinear time-varying form apparently new | Saqib & Padoan Remark 1; Oishi et al. Thm 1 (input side); Lu et al. pose the gap |
| (d) Exponents survive without a differentiable map, via backward integral | **APPARENTLY NEW** as a theorem; observation known; two unread sources could overlap | Lu et al. (observation); Saqib & Padoan Prop. 6 (integral for the map only); Stark 1999 unread |
| (e) Transverse differs from conditional; kernel invariance condition | **PARTLY KNOWN**: qualitative difference known; systematic gap and the condition apparently new | Saqib & Padoan eq. (32); Hart 2024 expects the opposite; Oishi et al. give the input-side dual |
| (f) Exact counterexample | **KNOWN** | Saqib & Padoan Sec. V-A; Rivkind & Barak 2017 |
| (g) Transverse exponent predicts failure; common failure | **PARTLY KNOWN**: criterion known; three-way comparison apparently new; 513/810 is the draft's own | Lu et al.; Lu & Bassett; Oishi et al.; Saqib & Padoan Remark 1 |
| (h) W + V N^T = R_dot R^+, rank-deficient and ridge | **PARTLY KNOWN**: DMD link known; this identity and the ridge version apparently new | Bollt 2021; Kaplan et al. 2026 |
| (i) Penalty on N^T B beats ridge | **PARTLY KNOWN, largely in substance**: state-dependent form published; fixed-B form and direct comparison not found | Wikner et al. 2024 |

## 2. Evidence by claim

**(a)**
- Lu, Hunt, Ott [text, II C]: with exact post-processing, listening and predicting reservoirs agree, phi(A) is invariant, and its dynamics seen through psi are "equivalent" to those of A. Discrete time, continuous phi.
- A. G. Hart 2024 [text, Sec. 5]: if the synchronization map is an embedding on an open set, the autonomous system "defines a vector field on f(Omega) which is diffeomorphic to the source vector field". This is the draft's continuous-time statement, in vector-field language.
- Bizyaeva et al. [text, Prop. III.1 B]: global minimizer, exact readout on the GS graph, and closed-loop reproduction are equivalent, for contracting reservoirs in continuous time.
- Hara & Kokubu 2024 [text, Thm 1 and 4]: proved only for a "degenerate" reservoir whose update does not depend on r. They say explicitly that the view "has not been verified" in general. Hara & Kokubu 2026 [abstract]: "under certain assumptions" the reservoir is semiconjugate in a weak sense or conjugate.
- The only addition in the draft is that for a linear readout no derivative of phi is needed (Prop. no_derivative). That is a small corollary, since Bizyaeva's proof also uses only trajectories.

**(b)** Bizyaeva Prop. IV.1 [text] bounds forecast error by epsilon(1 + L_omega L_u (e^{L_g s} - 1)/L_g) plus an initialization term. It uses readout error and Lipschitz constants, with no time-derivative term and no decomposition. Prop. V.1 bounds the gap from linearity. Saqib & Padoan treat exact readouts only, and Lu et al. stop at "approximately invariant". Nothing read states the identity. It takes a few lines, so it has value as a reading rather than as a discovery. Equation (training_residual_identity) in the draft is the part least likely to be found elsewhere under this name, though the system-identification literature on equation error against simulation error is unread.

**(c)**
- Lu et al. [text, II D]: "it is not clear in advance which perturbations correspond to transverse Lyapunov exponents". The draft answers this.
- Saqib & Padoan [text, Prop. 3, Remark 1], linear reservoir and linear neutral exosystem: (F + G Wout) Pi = Pi S. In coordinates (Pi^+ x, N^T x), where their N spans ker Pi^T, the matrix is block upper triangular, and they name the other block's eigenvalues "transverse". Their complement is orthogonal to the invariant subspace, not the readout kernel.
- My remark: spectra on a quotient do not depend on the complement, so in that setting the draft's Q A|ker gives the same numbers. Check on the draft's example: both give +1. So the block-triangular idea is not new for constant coefficients. What remains distinct: nonlinear reservoirs, the time-varying Q(s(t)) along a chaotic orbit, J = A_c on the kernel (V drops out), and the flat fibres.
- Oishi et al. 2602.11069 [text, Thm 1, Cor. 2]: Im(Win) in an A-invariant subspace pins N-D' eigenvalues for any Wout. Input-side analogue, using an orthogonal frame.

Saqib & Padoan's nonlinear section (Lemma 5, Prop. 6, Cor. 7) [text] covers invariant manifolds and readout existence but, in what I read, no transverse operator. Its assumptions (A7) require a stable, Poisson-stable equilibrium with sigma(S0) on the imaginary axis, and the results are local. As I read them this excludes the positive-exponent setting of a chaotic attractor around an unstable equilibrium, so the chaotic case is left open.

**(d)** Lu et al. [text]: reproduced "in practice" without guaranteed differentiability, no mechanism. Oishi et al. [text] use the same numerical recipe. Saqib & Padoan Prop. 6 (i) gives pi(w) = integral e^{Ft} G l(phi_{-t} w) dt [text], and A. Hart 2024 has a closed form for linear reservoirs [text, grep level]. The draft's y(t) is formally the derivative of that integral along admissible directions (my observation), so the construction is natural and its novelty lies in three statements: it holds without differentiability, N^T y = xi, and the exponent carries to the closed loop. I found these nowhere, but **Stark 1999 [abstract] studies Whitney smoothness of invariant graphs over closed subsets with non-uniform rates and is unread, and Hunt–Ott–Yorke 1997 is abstract only.** Read both before claiming this.

**(e)**
- J. D. Hart 2024 [text, II E]: "one might expect" the non-target exponents to "stay close to the CLEs", with "We find that this is often the case". The draft's 808/810 and 810/810 contradict this directly. This is the sharpest empirical contribution.
- Saqib & Padoan eq. (32): lambda_tr = N^T F N + kappa N^T G with any real value attainable by an exact readout [text]. So the LTI transverse exponent is not bounded by the driven one. The principle is out, for a linear reservoir.
- Oishi 2606.24303 [text] writes "Transverse Lyapunov exponents (TLEs), also called conditional Lyapunov exponents (CLEs)", so the conflation is live.
- Oishi 2602.11069 [text, Methods] says that when every TLE lies below the most negative target exponent, the map is differentiable. That is stated for TLEs where Hunt–Ott–Yorke type conditions use conditional exponents, so it may be worth a remark once the sources are read.
- Kaplan et al. 2604.05967 Thm III.2 [text]: under its assumptions exactly q = rank(C_rr) eigenvalues are dominant and the rest stay below -lambda. A positive result in a linear infinite-data setting. It needs comparing with the draft's instability, since the draft's unstable mode sits in the data-free direction, and their min-norm readout vanishes on ker C_rr.
- A_c ker N^T subset ker N^T: not found anywhere. Oishi's condition is its dual.

**(f)** Saqib & Padoan Sec. V-A [text]: a three-node linear reservoir driven by a sinusoid, every exact readout is Q Pi^+ + kappa N^T, unstable for kappa > 17.6 "despite zero training error", with a figure of the divergence. They also show the training transient selects kappa. Rivkind & Barak 2017 [text]: open-loop stability "does not guarantee stability of the closed loop". The draft's example differs only in using a decaying source and in having the mechanism named. **Keep it as an illustration and cite these.** Saqib & Padoan's point that transients and regularization select the transverse modes should be read against the draft's section on ridge.

**(g)** Lu et al. [text]: climate loss coincides with an exponent crossing zero. Lu & Bassett [text, App. A2]; Oishi et al. [text, spurious slow modes]; Saqib & Padoan Remark 1 ("decided ... by the transverse eigenvalues"). Hart 2024 reports the maximal conditional exponent as the indicator. Du & Wang 2607.17909 [abstract] report that the best spectral radius matches no Lyapunov edge and propose a different index; possible tension to check. I found no paper comparing transverse exponent, conditional exponent and training error as predictors on one ensemble, in the Lu 2018 forward citations (174 of 376 from 2023 on, keyword-filtered) or the arXiv queries in section 5. The draft's Lorenz result (training error predicts as well) must stay in the claim.

**(h)** Bollt 2021 [text]: linear RC equals VAR; link to DMD "not complete", in discrete time with delays. Kaplan et al. [text]: Wout = U R^+ and Wout Win = U B1^+ (Lemma IV.1), and a backward DMD representation for diagonal reservoirs on filtered history (Cor. IV.3). Their DMD matrix is built on filtered input, not on (R_dot, R). Tu et al. 2014 [meta] for exact DMD. W + V N^T = R_dot R^+ was not found, and it takes one line from R_dot = W R + V S. I could not check rank-deficient or ridge versions against the draft, which has only full rank. Proctor et al. 2016 (DMD with control) and Gulina & Mauroy 2021 are unread and are the first place to look.

**(i)** Wikner et al. 2024 [text]: LMNT penalty beta_L sum ||W grad_u(j,k)||_F^2, and "In the case where K = 1, this regularization matrix is identical to the Jacobian regularization matrix". For K = 1 and affine input this is ||N^T D B||. **An important nuance:** in their Kuramoto–Sivashinsky test, Jacobian regularization *alone* gave "very low" valid times and was always unstable, while it worked combined with Tikhonov. So a pure ||N^T B|| penalty needs testing against that result. Kaplan's Wout Win = U B1^+ gives the quantity in closed form for diagonal reservoirs. Reinhart & Steil 2012 [abstract/snippet only] propose reservoir regularization for output feedback.

## 3. Threads

**Generalized synchronization.** Afraimovich et al. 1986; Pecora & Carroll 1990; Rulkov et al. 1995; Abarbanel et al. 1996; Kocarev & Parlitz 1996; Pyragas 1996; Pecora et al. 1997; Boccaletti et al. 2002; Badii et al. 1988; Pecora & Carroll 1996; Davies & Campbell 1996 [all meta]. Hunt, Ott, Yorke 1997 [abstract]: exponent conditions for differentiable GS, Hölder exponent otherwise. Stark 1999 [abstract], Josić 1998 [abstract]: normal hyperbolicity. Stark 1997 [meta]. Grigoryeva et al. 2021 [text, intro]: differentiable GS theorem.

**Observers.**
- Andrieu & Praly 2006 [text, Thm 2.2]: Lf T = A T + B(h), with T continuous and uniformly injective and A Hurwitz, gives a continuous left inverse T* with convergence. Continuity is enough, which parallels the draft's continuous assumption. Dimension bound 2n+2 [abstract].
- Kazantzis & Kravaris 1998 [meta]. Bizyaeva's account [text]: nonlinear contracting KKL via Pachy et al. 2024 and Galimberti et al. 2026 (not independently checked).
- Janny et al. 2021 [text, framework]: contraction plus generating model g(z) = G(z, psi(z)), which is the closed loop itself, with no mention of transverse stability in my keyword scan. Bizyaeva et al. call it a rediscovery of the reservoir setup.
- Nijmeijer & Mareels 1997 [abstract]: revisits synchronization through observers.
- Parlitz 1996, So et al. 1993, Yu & Parlitz 2008, Yang et al. 2006, Duane et al. 2006, Abarbanel et al. 2009, Creveling et al. 2008, Morgül & Solak 1996, Nijmeijer 2001 [meta].

**Control.** Isidori & Byrnes 1990; Byrnes & Isidori 2003; Francis & Wonham 1976 [meta], used through Saqib & Padoan, who identify the invariance equation with the Francis–Byrnes–Isidori equations. Astolfi & Ortega 2003, Zames 1966 [meta]; no one I read links immersion and invariance or small gain to reservoirs, and the draft's Volterra loop looks like a small-gain setting (my remark).

**RC closed loop.** A. Hart 2024, Lu & Bassett 2020, Oishi x2, Hart 2024, Platt 2021 [text] (the "predictive GS" and auxiliary test; train/test evaluation "gives no indication of the stability of the forecast"). Hara & Kokubu 2024 [text] show one-step success with dynamic failure and exhibit fixed points beyond the data. Multistability: Flynn 2021, 2023; Röhm 2021; Gauthier 2022; Zhang & Cornelius 2023; Ceni 2020 [meta]. Zhang et al. 2025 [abstract]: NGRC can lose stability with more data. Liu et al. PRR 2026 [abstract]: dynamic bias for stability, a design paper. Santos & Bollt 2025 [abstract].

**Free-run failure in general.** Rivkind & Barak 2017 [text]; Mastrogiuseppe & Ostojic 2019 [abstract, readout-input geometry determines stability class]. Williams & Zipser 1989; Doya 1992; Narendra & Parthasarathy 1990; Venkatraman et al. 2015; Mikhaeil et al. 2022; Park et al. 2024; Berry & Das 2025; Hess et al. 2023; Ross et al. 2011 [meta, the last two verified on arXiv by title]. Unread beyond that; lower priority because they do not address the driven-then-closed structure.

**Author's paper.** Verzelli, Alippi, Livi, Chaos 31, 083119 (2021) [text]: covers driven phase and generic targets, says the dynamics are unchanged "in absence of an output feedback mechanism", with Theorem 2 on an injective map. Nothing on the closed loop, so no self-overlap. 34 citing papers screened by title; those opened are cited above.

## 4. Journals and pitch

- **Chaos** is the home of the physics line (Lu 2018, Platt 2021, Bollt 2021, J. D. Hart 2024, A. G. Hart 2025, Suetani & Parlitz 2026 in the special collection "Nonlinear Dynamics of Reservoir Computing"). Pitch: mechanism plus diagnostic.
- **PRL** carried Rivkind & Barak 2017 and Pathak 2018; PRE and PRR publish Kobayashi 2021, Grigoryeva 2021, Wong 2024, Zhang & Cornelius 2023, Liu 2026.
- **SIADS, JDDE, Nonlinearity, Physica D**: theorem-led.
- **Control preprints** (eess.SY): the two new papers pitch RC as a rediscovery of classical theory.

Given section 0, a pitch of "reservoirs learn the vector field" or "stable synchronization does not imply a stable closed loop" will not stand as new. A pitch that could: *what controls transverse stability for chaotic sources, why the driven diagnostic misleads, and what happens without a smooth map.*

**Six to read in full** (one more than asked, because the two new preprints displaced the older list)
1. **Saqib & Padoan 2026.** Biggest threat: block-triangular form, free transverse modes, zero-error instability, all for linear systems.
2. **Bizyaeva et al. 2026.** Threat to (a) and the framing; also a source of theory to borrow.
3. **Lu, Hunt, Ott 2018.** Baseline, and poses the open question (c) answers.
4. **Oishi et al. 2602.11069.** Same failure story for nonlinear reservoirs, constructive fix, input-side dual of (e).
5. **J. D. Hart 2024.** Support: the expectation that (e) refutes.
6. **Wikner et al. 2024.** Threat to (i), and evidence against Jacobian-only penalties.

## 5. Where I looked and what is left

**Searched:** OpenAlex citing lists of Verzelli 2021 (all, titles), Lu 2018, Hart 2024, Hara & Kokubu 2024, Platt 2021 (2023 on, keyword filtered on title and abstract). arXiv API on abstract terms: reservoir with transverse/readout, closed-loop/conditional Lyapunov, transversal/GS, DMD/closed-loop, internal model, spurious/closed-loop, echo state/output feedback/regularization, surrogate/vector field, teacher forcing/chaotic, loop gain; plus Luenberger/Kazantzis. About ten web searches. Note: most of the arXiv keyword queries returned little or nothing, and the KKL query found preprints that an earlier broad web search missed, so a misses-only verdict is weak evidence.

**Not read:**
- **Hara & Kokubu 2026:** the SIAM page stops at a Cloudflare check, so abstract only. Its assumptions matter for (a) and (d); the user can open it directly.
- **Bernard et al. 2022** survey (download failed), **Reinhart & Steil 2012** (paywalled), **Nijmeijer & Mareels** body.
- **Stark 1999, Hunt–Ott–Yorke 1997** bodies.
- Everything marked [meta].

**Identifiers**
- New: arXiv:2610.04343, 2610.08987, 2604.05967, 2607.17909, 2602.11069, 2606.24303, 2211.09515 (A. Hart).
- Verzelli 10.1063/5.0056425; Lu 2018 10.1063/1.5039508; Lu & Bassett 10.1063/5.0004344; J. D. Hart 10.1063/5.0196257; A. G. Hart 2024 10.1016/j.physd.2023.133956; A. G. Hart 2025 10.1063/5.0301957.
- Platt 10.1063/5.0066013; Bollt 10.1063/5.0024890; Suetani & Parlitz 10.1063/5.0283017; Wong 10.1103/PhysRevE.110.064219; Rivkind & Barak 10.1103/PhysRevLett.118.258101; Mastrogiuseppe & Ostojic 10.1162/neco_a_01187.
- Wikner 10.1016/j.neunet.2023.10.054; Reinhart & Steil 10.1016/j.neucom.2012.01.032; Zhang 10.1063/5.0262977; Liu 10.1103/5nbr-bqxb; Santos & Bollt 10.1063/5.0278709.
- Hara & Kokubu 10.1007/s10884-022-10159-w, 10.1137/24M1714617; Grigoryeva 10.1088/1361-6544/ace492, 10.1103/PhysRevE.103.062204.
- Andrieu & Praly 10.1137/040617066; Kazantzis & Kravaris 10.1016/S0167-6911(98)00017-6; Janny 10.1109/CDC45484.2021.9683277; Bernard 10.1016/j.arcontrol.2021.11.002; Nijmeijer & Mareels 10.1109/81.633877.
- Isidori & Byrnes 10.1109/9.45168; Byrnes & Isidori 10.1109/TAC.2003.817926; Francis & Wonham 10.1016/0005-1098(76)90006-6; Astolfi & Ortega 10.1109/TAC.2003.809820; Zames 10.1109/TAC.1966.1098316.
- Tu 10.3934/jcd.2014.1.391; Proctor 10.1137/15M1013857; Gulina & Mauroy 10.1063/5.0026380; Hunt, Ott, Yorke 10.1103/PhysRevE.55.4029; Stark 10.1016/S0167-2789(97)00167-X, 10.1017/S0143385799126555; Josić 10.1103/PhysRevLett.80.3053.
- Papers named only in section 3 without a DOI here were resolved through Crossref in this work, except Pachy 2024 and Galimberti 2026, which are cited only as reported by Bizyaeva et al.

## 6. Verdict

**Not new, cite instead:** (a); (f); the principle that open-loop stability does not imply closed-loop stability; the block-triangular transverse picture for linear systems; the observer identification itself.

**Defensible as new:**
1. The transverse operator Q A_c on ker N^T for nonlinear reservoirs along a chaotic orbit, plus J = A_c on the kernel. This extends Saqib & Padoan's linear statement and answers Lu et al.'s question.
2. Survival of source exponents without a differentiable map (subject to reading Stark 1999 and Hunt–Ott–Yorke).
3. The kernel-invariance condition (dual to Oishi et al.).
4. The measured systematic gap between transverse and conditional exponents, contradicting Hart 2024's expectation, and the three-way predictor comparison.
5. The error identity and W + V N^T = R_dot R^+, as short organizing results, not headlines.

**Not to claim:** (i) as a new idea; at most the fixed-B form and a comparison, tested against Wikner's Jacobian-only failure.

**Timing:** the linear-system overlap appeared this month in control-theory preprints, and those authors state further work is planned. Extending to chaotic sources is the natural next step for them, so posting soon matters.
