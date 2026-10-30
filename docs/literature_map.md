# Literature map: a surrogate driven by a source, decoded, then closed on itself

**Status: partial.** The session hit its usage limit before the map was finished. Section 5 lists what is missing.
"Apparently new" below means "not found in the limited search listed in section 5". It is not a clearance.

Evidence labels:
- **[text]**: I read the relevant passage in the full text.
- **[abstract]**: only the abstract or a search snippet.
- **[meta]**: only the bibliographic record was verified (Crossref). The paper was not read, and anything said about it comes from memory or is a lead to check.

## 1. Classification

| Claim | Class | Basis |
|---|---|---|
| (a) Conjugacy on the synchronization manifold; decoder differential maps velocities | **KNOWN** (conjugacy); differential statement is an elementary corollary | Lu, Hunt, Ott 2018 Sec. II C; Lu & Bassett 2020; Hara & Kokubu [abstract] |
| (b) g_hat - g = e_dot + N^T d, with its coordinate-change and feedback-defect reading | **APPARENTLY NEW** as an explicit identity, but elementary | Not found; thinly searched |
| (c) ker N^T as explicit transverse direction, Q A_c, block-triangular form | **PARTLY KNOWN** | Lu et al. pose the gap; Oishi et al. give an input-side analogue |
| (d) Unstable and neutral exponents survive without differentiability, by the backward integral | **PARTLY KNOWN**: observation known, proof apparently new | Lu et al.; Oishi et al. |
| (e) Transverse differs from conditional; A_c ker N^T subset ker N^T | **PARTLY KNOWN**: expectation stated in the literature, systematic gap and condition apparently new | Hart 2024; Oishi 2026 |
| (f) Exact counterexample | **PARTLY KNOWN**: principle known, this explicit example not found | Rivkind & Barak 2017 |
| (g) Transverse exponent predicts failure; common failure | **PARTLY KNOWN**: criterion known, head-to-head comparison apparently new | Lu et al.; Lu & Bassett; Oishi et al. |
| (h) W + V N^T = R_dot R^+, rank-deficient and ridge versions | **PARTLY KNOWN**: connection known, identity not found | Bollt 2021; Kaplan et al. 2026; Tu et al. 2014 |
| (i) Penalty on N^T B stabilizes better than ridge | **LARGELY KNOWN IN SUBSTANCE** | Wikner et al. 2024; Reinhart & Steil 2012 [abstract] |

## 2. Evidence by claim

**(a)** Lu, Hunt, Ott [text, Sec. II C] treat the idealized case: with exact post-processing the listening and predicting reservoirs agree exactly, phi(A) is invariant for the predicting reservoir, and its dynamics seen through psi are "equivalent" to the dynamics of A seen through h. This is discrete time and uses only a continuous phi. Lu & Bassett [text, Sec. on the testing phase] say the same with phi = psi^-1. Grigoryeva, Hart, Ortega 2023 [text, intro only] frame the synchronization as giving a topological conjugacy. The draft's Prop. on the conjugacy should be presented as a restatement.

**(b)** I found no paper stating the identity. The extended search on learned vector field error and reconstruction returned only generalized-synchronization and embedding papers. It follows in a few lines, so the value lies in the reading rather than the proof. An existing paper could have it in other notation, for instance the system-identification literature on equation error against simulation error, which I did not check.

**(c)** Lu et al. [text, Sec. II D]: for the predicting reservoir "it is not clear in advance which perturbations correspond to transverse Lyapunov exponents". They also stress that stability depends on how psi is extended off phi(A). This is the gap the draft answers, and the draft already quotes it. Oishi et al. 2026 [text, Thm 1, Cor. 2] is the closest structural result: if Im(Win) lies in an A-invariant subspace V, then N-D' eigenvalues of A + Win Wout stay at those of A for *any* Wout, and V stays invariant. That is the input-side counterpart of the draft's output-side A ker N^T subset ker N^T. It is a statement about matrix spectra plus a QR-based transverse block (I - Q Q^T) on an orthogonal frame, not an oblique projector built from D phi N^T. I did not find ker N^T used this way.

**(d)** Lu et al. [text]: much of the spectrum can be reproduced "in practice" even without guaranteed differentiability. No mechanism is given. Oishi et al. [text, Methods] and Lu et al. both use the same numerical recipe, computing along the driven trajectory and removing the target exponents. I found no proof of the backward-integral kind, but I did not read Stark 1997/1999 or Hara & Kokubu, which are where one would most likely appear.

**(e)** Hart 2024 [text, Sec. II E]: one "might expect" some autonomous exponents to replicate the target while the others "stay close to the CLEs", and "We find that this is often the case". The draft's 808/810 and 810/810 gaps contradict this directly, so this is the sharpest point of contact. Oishi et al. 2606.24303 [text, Sec. II] writes "Transverse Lyapunov exponents (TLEs), also called conditional Lyapunov exponents (CLEs)", so the two are conflated in current work, which helps motivate (e). Oishi 2602.11069 [text, Methods] does keep CLE and TLE apart in the sense of removing target exponents, and it claims differentiability when all TLEs lie below the most negative target exponent. The draft could check that claim, since it uses TLEs where the Hunt–Ott–Yorke type condition concerns CLEs.

**(f)** Rivkind & Barak 2017 [text]: "asymptotic stability of the open loop system (2) does not guarantee stability of the closed loop system (1)". Their analysis uses open-loop gain, G_CL = G_OL (1 - G_OL)^-1, for trained fixed points in mean-field theory. So the principle has been in PRL since 2017, and control theory would treat it as standard (I did not source that). The draft should not pitch (f) as surprising. What is distinct is exact reconstruction with explicit exponents and the kernel-invariance mechanism. The draft's matrices check by hand: A + V N^T = [[1,0],[-1,-1]].

**(g)** Lu et al. [text]: the transition from accurate to inaccurate climate corresponds to a Lyapunov exponent crossing zero, and transient duration is related to its value. Lu & Bassett [text, App. A2] repeat this. Oishi et al. [text] attribute failures to transverse instability from spurious slow modes. Hart 2024 [text] instead reports the maximal CLE as the performance indicator, which is the view the draft challenges. I found no comparison of transverse exponent, conditional exponent and training error as predictors on one ensemble, but the search was not exhaustive. The 513/810 figure is the draft's own, so it needs no literature support. Note that the draft reports training error predicting as well as lambda_perp on Lorenz, so the claim has to stay source-dependent.

**(h)** Bollt 2021 [text, Sec. on DMD]: the fully linear RC is a VAR, and the DMD connection is real but "not complete". K from exact DMD and the VAR(1) companion A need not coincide. Bollt uses discrete time and a delay form, and states no closed-loop generator identity. Kaplan, Padoan, Bizyaeva 2026 [text, abstract and Cor. IV.3 heading] show that training data generate an invariant subspace of the trained linear reservoir, and link diagonal reservoirs to a *backward* DMD matrix. It is the nearest recent work, so read it in full. Tu et al. 2014 [meta] is the exact-DMD reference. DMD with control (Proctor et al. 2016) [meta] and Gulina & Mauroy 2021 [meta] are unread. The draft currently has only the full-row-rank case; I could not check the rank-deficient and ridge versions against the draft.

**(i)** Wikner et al. 2024 [text, Sec. 2.3.2, 2.4]: the LMNT regularizer is beta_L sum ||W grad_u(j,k)||_F^2, with grad_u the Jacobian of features with respect to past input. For K = 1 "this regularization matrix is identical to the Jacobian regularization matrix". With K = 1 and affine input this is ||N^T D B||, a state-dependent version of ||N^T B||. A search snippet of that paper's abstract says that reservoirs with Tikhonov only are stable only for some realizations, whereas Jacobian, noise or LMNT regularization combined with Tikhonov stabilize when strong enough. Reinhart & Steil 2012 [abstract/snippet] study regularization and stability with output feedback. Zhang et al. 2407.08641 [abstract] cover NGRC instability, and a snippet says noise regularization helps. **The paper can claim at most the fixed-B simplification and its derivation from the loop gain, and should cite Wikner.**

## 3. Other threads

**Synchronization and drive-response [meta unless noted].** Afraimovich et al. 1986; Pecora & Carroll 1990; Rulkov et al. 1995; Abarbanel et al. 1996 (auxiliary system); Kocarev & Parlitz 1996; Pyragas 1996; Hunt, Ott, Yorke 1997; Stark 1997, 1999; Josić 1998; Pecora et al. 1997; Boccaletti et al. 2002. Nondifferentiability from filtering: Badii et al. 1988; Pecora & Carroll 1996; Davies & Campbell 1996.

**Observers and estimation [meta; not read].** Nijmeijer & Mareels 1997; Morgül & Solak 1996; Nijmeijer 2001; Parlitz 1996; So et al. 1993; Yu & Parlitz 2008; Yang et al. 2006; Duane et al. 2006; Abarbanel et al. 2009; Creveling et al. 2008.

*Unverified lead, from memory and not from reading:* a response dz/dt = Az + By with an injective map and a left inverse looks like a Kazantzis–Kravaris/Luenberger observer (Kazantzis & Kravaris 1998; Andrieu & Praly 2006), and the invariance equation looks like the synchronization identity. Output regulation (Isidori & Byrnes 1990; Byrnes & Isidori 2003; Francis & Wonham 1976) and immersion and invariance (Astolfi & Ortega 2003) may also overlap. One search found no paper framing a reservoir as a KKL observer. Bernard, Andrieu, Astolfi 2022 is the survey to start from. **For a general physics journal this is the largest open risk to claims (a)–(c).**

**Multistability [meta].** Flynn et al. 2021, 2023; Flynn & Amann 2024; Röhm et al. 2021; Gauthier et al. 2022; Zhang & Cornelius 2023; Ceni et al. 2020. Hart 2024 [text] notes untrained attractors are reachable even when reconstruction is locally stable.

**Training error small, free run fails [meta unless noted].** Williams & Zipser 1989; Doya 1992; Narendra & Parthasarathy 1990; Venkatraman et al. 2015; Mikhaeil et al. 2022; Park et al. 2024; Berry & Das 2025; Haluszczynski & Räth 2019; Storm et al. 2022 [abstract]; Kobayashi et al. 2021; Margazoglou & Magri 2023; Platt et al. 2023. Platt et al. 2021 [text] introduce "predictive generalized synchronization" and use the auxiliary test, and they say the usual train/test evaluation "gives no indication of the stability of the forecast". Mastrogiuseppe & Ostojic 2019 [abstract] tie stability classes to the geometry of the readout relative to the input vectors, which is a possible overlap with (c) and (i).

**Author's paper.** Verzelli, Alippi, Livi, Chaos 31, 083119 (2021) [text]. It covers the driven phase and generic targets with the reservoir not fed back: it says "in absence of an output feedback mechanism" the dynamics are unchanged. Its Theorems 1–2 give necessary and sufficient conditions for realizable learning (Theorem 2: an injective F), and it assumes a smooth phi. It says nothing about the closed loop, so there is no self-overlap. OpenAlex lists 34 citing papers. I screened titles only. Those to open: Suetani & Parlitz 2026; Wong et al. 2024 [abstract]; Hart 2025.

## 4. Journals and pitch (from papers seen)

- **Chaos** is the main home: Lu 2018, Platt 2021, Bollt 2021, Hart 2024, Suetani & Parlitz 2026 (in a special collection, "Nonlinear Dynamics of Reservoir Computing"). The pitch is a physical mechanism plus a numerical diagnostic.
- **PRE / PRR / PRL:** Kobayashi 2021, Grigoryeva 2021, Wong 2024, Zhang & Cornelius 2023; Rivkind & Barak 2017 is the one PRL with a closed-loop stability result.
- **SIADS, J. Dyn. Diff. Eq., Nonlinearity:** theorem-led work (Hara & Kokubu, Grigoryeva et al.).
- **Neural Networks:** regularization (Wikner).
- Oishi et al. are preprints, so I have no venue for them.

**Five to read in full**
1. **Lu, Hunt, Ott 2018.** Already has (a), the transverse criterion and the numerical recipe. It is the baseline and also poses the open question that (c) answers.
2. **Oishi et al., arXiv:2602.11069.** The largest current threat: same failure mechanism, input-side invariant-subspace theorem, and a constructive fix.
3. **Hart 2024.** Support: the CLE expectation is what (e) refutes numerically.
4. **Wikner et al. 2024.** Direct threat to (i).
5. **Hara & Kokubu 2024 / 2026.** Unread, and may contain conjugacy and stability results that bear on (a) and (d). Rivkind & Barak 2017 is the runner-up, for (f).

## 5. What was and was not checked

**Searched:** the OpenAlex citing list for the 2021 paper; Crossref; about six web searches on KKL and reservoirs, CLE vs TLE and null space, closing-loop regularization, linear reservoir and DMD, vector-field error.

**Not done:**
- Hara & Kokubu full text. Direct downloads failed, and I opened the SIAM page in the browser pane but did not read it. Theorem statements are unverified.
- Everything marked [meta], including the whole observer and control thread.
- Forward citations of Lu 2018, Hart 2024 and Oishi. Backward references were only partly followed.
- Verification of the following from a source I fetched: Hess et al. 2023 and Ross et al. 2011 were not resolved by Crossref, so they are left out above. Verify before citing.

**Identifiers**
- Verzelli 10.1063/5.0056425; Lu 2018 10.1063/1.5039508; Lu & Bassett 10.1063/5.0004344 (arXiv:1807.05214)
- Hart 2024 10.1063/5.0196257; Hart 2025 10.1063/5.0301957; Platt 2021 10.1063/5.0066013; Bollt 10.1063/5.0024890
- Suetani & Parlitz 10.1063/5.0283017; Wong 2024 10.1103/PhysRevE.110.064219; Rivkind & Barak 10.1103/PhysRevLett.118.258101
- Mastrogiuseppe & Ostojic 10.1162/neco_a_01187; Wikner 10.1016/j.neunet.2023.10.054; Reinhart & Steil 10.1016/j.neucom.2012.01.032
- Hara & Kokubu 10.1007/s10884-022-10159-w and 10.1137/24M1714617; Grigoryeva 10.1088/1361-6544/ace492 and 10.1103/PhysRevE.103.062204
- Tu 10.3934/jcd.2014.1.391; Proctor 10.1137/15M1013857; Gulina & Mauroy 10.1063/5.0026380; Storm 10.1088/2632-2153/aca1f6
- Kobayashi 10.1103/PhysRevE.104.044215; Hunt, Ott, Yorke 10.1103/PhysRevE.55.4029; Stark 10.1016/S0167-2789(97)00167-X and 10.1017/S0143385799126555; Josić 10.1103/PhysRevLett.80.3053
- Nijmeijer & Mareels 10.1109/81.633877; Kazantzis & Kravaris 10.1016/S0167-6911(98)00017-6; Andrieu & Praly 10.1137/040617066; Bernard et al. 10.1016/j.arcontrol.2021.11.002
- Isidori & Byrnes 10.1109/9.45168; Byrnes & Isidori 10.1109/TAC.2003.817926; Francis & Wonham 10.1016/0005-1098(76)90006-6; Astolfi & Ortega 10.1109/TAC.2003.809820; Narendra & Parthasarathy 10.1109/72.80202
- Preprints: arXiv:2602.11069, 2606.24303, 2604.05967, 2407.08641. Other papers named in section 3 were resolved through Crossref during this session, but their DOIs are not reproduced here.

## 6. Verdict

The setting, the on-manifold conjugacy, the transverse criterion, and "open-loop stable does not imply closed-loop stable" are all known, and the paper should say so.

The defensible new content, subject to section 5:
1. The readout kernel as the explicit transverse direction, with the projected equation and the kernel-invariance condition. This answers the question Lu et al. leave open.
2. The proof that source exponents survive without a differentiable map.
3. The measured, systematic gap between transverse and conditional exponents, contrary to the expectation in Hart 2024.
4. The vector-field error identity, as a clean organizing result rather than a deep one.

Do not claim (i) as new. Before submission, check the observer/KKL literature and Hara & Kokubu.
