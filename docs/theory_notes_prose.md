# What can be proved about closing the loop

*Working notes, written out in prose. Rewritten from `docs/theory_notes.md` on branch `theory-notes` (34af5e0), which remains the reference. Each statement keeps its status: **[PROVED]** means the full proof is given here, **[SKETCH]**, **[CONJECTURE]** and **[FALSE]** mean what they say, and "checked" means a numerical test on uranus, with scripts in `experiments/theory/`. Nothing here has been refereed. The proofs are unreviewed.*

## I. Introduction

Consider a system whose equations we do not know, the *source*, and a second system that we are free to choose, the *surrogate*. During the listening phase the surrogate is driven by the source and, if all goes well, its state becomes a function of the source state. In the fitting phase we train a decoder that reads the source state back from the surrogate. Then, in the autonomous phase, we close the loop: the decoded output replaces the input, and the surrogate runs on its own.

The question of these notes is what the first two phases determine about the third. We find four things.

1. The draft of Section 3 contains three errors, all of which can be repaired (Sec. III).
2. The transverse dynamics of the closed loop are *zero dynamics*. The closed-loop operator $I-\mathcal K$ factorizes exactly, also in the nonlinear time-varying case, into a factor describing the source tangent flow and a reduced filter. This yields the right restricted gain, which certifies stability on tests where the naive gain cannot (Sec. V). The linear part of this picture is now mostly known (Saqib & Padoan 2026), whereas the time-varying and non-differentiable forms appear new.
3. No closed form in $\lambda_\perp$, the largest conditional Lyapunov exponent (CLE) and the loop gain exists, and no function of the CLEs and the reconstruction error can decide stability, also for chaotic sources with a non-differentiable synchronization map (Sec. V F).
4. For imperfect reconstruction we have three theorems, none of which covers generic non-differentiable reservoirs on non-hyperbolic sources. Non-uniform transverse stability provably does not give an $O(e)$ supremum bound in general (Sec. VI).

The reader interested in a one-line verdict can go to Sec. VIII: this material fits a long-format paper and does not supply a headline for a letter.

## II. Setting and notation

The source obeys $\dot s=g(s)$ and the surrogate $\dot r=f(r,s)$. We say that the two are in generalized synchronization if $r=\phi(s)$ on the attractor $\mathcal A_s$, where $\phi$ is the synchronization function, and we write $\mathcal M=\phi(\mathcal A_s)$. The decoder is $\hat s=\psi(r)$, and the closed loop is $\dot r=f(r,\psi(r))$.

Along a driven orbit we use the following shorthand: $A=A_c=D_rf$ and $B=B_c=D_sf$; $G=Dg(s(t))$; $F=D\phi(s(t))$ when it exists; $C(t)=D\psi(r(t))$, which equals $N^\top$ for a linear decoder; $Q=I-FC$; the closed-loop Jacobian $J=A+BC$; and the kernel $\mathcal K(t,\tau)=C(t)\Phi(t,\tau)B(\tau)$, where the driven transition matrix satisfies $\|\Phi(t,\tau)\|\le ce^{-\kappa(t-\tau)}$. Propositions 1 to 4 and the Assumption 3 are those of Section 3 of the draft (`main.tex` at commit `1179bfe`, repaired in `0af04f9`).

## III. Audit of the draft

We checked the draft line by line. Most of it stands, and it is worth saying first what does.

**Proposition 1 is correct.** Uniform contraction is not used, and solutions need only exist on $\mathcal M$.

**The proof of Proposition 2 is correct line by line.** We checked the segment averaging on the compact convex hull, the robustness of contraction on $(-\infty,t]$, dominated convergence, $N^\top y=\xi$ and both exponent bounds. Four points need care. First, $\mathcal A_s$ must be invariant in both time directions, which the draft left implicit. Second, "gain exactly one" should read "eigenvalue one", since $\mathcal K\xi=\xi$ says nothing about the operator norm. Third, Assumption 3 asks for contraction on *every* orbit in $\mathcal A_s$, including embedded fixed points and periodic orbits, whereas the numerics measure the largest CLE for the natural measure. The numerics therefore do not verify the assumption. Fourth, $\dim\mathcal D$ is not constant on Lorenz: at the origin $g=0$ and $\mathcal D$ has dimension one, so "constant dimension along the orbit" holds almost everywhere and not on all of $\mathcal A_s$.

It is natural to compare Proposition 2 with Hunt, Ott and Yorke (1997, HOY). The two are consistent, and Proposition 2 is not contained in HOY. Their Eq. (16), $e_p\cdot\nabla\phi=(\lambda_{xp}-Y)^{-1}We_{xp}$, is a periodic-point heuristic for the same object as $y(t)$, stated under their condition (5). Their Hölder exponent concerns the worst direction, the contracting one. They say that the attractor is smooth in expanding directions, but they do not state that $\phi$ is differentiable along them when (5) fails, and they give heuristics rather than theorems. Proposition 2 is thus the complement: $\phi$ is differentiable along the centre-unstable directions even at Hölder exponent below one. The past-history view of HOY also shows what the proof should need, namely that the integral requires only past-history response contraction at $x$, against the backward growth of $\xi$ along that orbit. This supports a pointwise version.

The extension to tempered contraction was not obtained. One can define $y$ for tempered $\xi$ and it solves $\dot y=Jy$, but $N^\top y=\xi$ uses the limit $r_\varepsilon-r$, whose perturbation of $A$ has only a continuity modulus. With $\phi$ Hölder and unstable directions the perturbation decays backward, and a tempered argument looks feasible **[SKETCH, not done]**. This remains open.

**The spectrum claim is correct** for an ergodic measure and a measurable invariant $\mathcal E$, with the quotient norm (the cocycle is block triangular). Identifying $\ker N^\top$ with the quotient for $k=d$ needs a tempered angle between $\mathcal E$ and $\ker N^\top$.

### A. Three errors

**Error 1: "$\mathcal E=T\mathcal M$" in Proposition 3 is false as stated.** The bundle $\mathcal E$ is built from backward-bounded directions, and therefore excludes all directions with negative exponents. For Lorenz, $k=2$ whereas $\dim T\mathcal M=3$. The correct statement is that $\mathcal E$ is contained in $\operatorname{Im}D\phi$, a larger $J$-invariant bundle. Saqib & Padoan do not meet this problem because their assumptions make the exosystem neutral on its set (their A3 and A7), so that the range of $\Pi$ is all of it.

**Error 2: $N^\top D\phi=I$ does not follow from exact reconstruction on $\mathcal A_s$.** Differentiating gives it only on the tangent cone of $\mathcal A_s$. The stronger statement is **[FALSE]**, as an example shows. Take an attracting circle, with radial exponent $-2$ and angular speed $1$, and a linear reservoir with $W\Pi+V=\Pi L_0$ and $N^\top\Pi=I$. Reconstruction on $\mathcal A_s$ is exact, yet the closed-loop spectrum contains $\pm i$, that is, exponents $0,0$, while the source has $0,-2$. We checked this with $\kappa=4>2$, so that a smooth $\phi$ exists: $|N^\top Fe_t-e_t|=3.5\cdot10^{-12}$ and $|N^\top Fe_r-e_r|=0.70$.

One might dismiss this as a formality, but it is a live effect on real trained readouts. In the tanh runs satisfying the typical-point rate condition ($\gamma=20$, $\rho=0.5$; all six on Rössler, two with $\sigma=0.1$ on Lorenz) we integrated $F$ along the orbit. We find $|(N^\top F-I)Q_2|<5\cdot10^{-4}$ and $|(N^\top F-I)g|/|g|<5\cdot10^{-4}$, where $Q_2$ denotes the leading two source directions, while on the remaining direction $|N^\top F-I|$ is $0.49$ to $3.5$ on Rössler and $4.3$ to $9.3$ on Lorenz. So Proposition 2 holds to three decimals with an approximate readout, and $N^\top F=I$ fails on the stable direction even when $\phi$ is smooth. As a consequence, $QA$ computed with a right inverse from $F$ does not match $J$ on these runs (for example, a third $J$ exponent of $-3.85$ against a top $QA$ exponent of $+0.28$, and $-1.54$ against $-7.36$). **The operator to use on trained readouts is therefore $Q_{\mathcal E}J$ of Sec. V D, and not the $QA$ of Proposition 3.** We also note that only 7 of 21 Rössler rate runs have a $J$ exponent within $0.5$ of $-5.37$ (median distance $1.24$), and 3 of 4 on Lorenz. With the bulk of the exponents nearby, "within $0.5$" is a weak test.

The repair **[PROVED]** is to assume exactness on a neighbourhood, as in Bizyaeva et al. Prop. III.1 where the exact identity holds on $X$, or to assume that the tangent cones of $\mathcal A_s$ span $\mathbb R^d$, since a $C^1$ function vanishing on $X$ has derivative vanishing on the tangent cone of $X$. This agrees with HOY, whose differentiability is defined on the attractor, including directions across the fractal, and who exclude "empty" contracting directions. Nonempty directions are pinned, and empty ones are not; the circle is the empty case, and it needs no rate condition on the radial direction. With the repair, the computation in Proposition 3 is correct, and it needs only a bounded $F$ solving $\dot F=AF+B-FG$ with $N^\top F=I$.

**Error 3: the "only if" of kernel invariance in Section 4 is false as a spectral claim.** The condition $QB=0$ also makes the transverse exponents conditional ones (Sec. V E), without invariance. Checked: $|QV|=7\cdot10^{-15}$, $|N^\top WK|=6.3$, and $\lambda_\perp$ in the spectrum of $W$ to $3\cdot10^{-15}$. Oishi et al. Theorem 1 has the linear case.

### B. The rate condition

**The rate condition is not necessary.** This is known for smoothness, and **[PROVED and checked]** for reproduction. HOY already note that exact synchronism stays smooth when their condition fails, and that a generic perturbation restores Hölder behaviour with a small constant $K$. Family (F) of Sec. V C is this non-generic case: $\kappa=1.08$, $\phi$ is smooth by construction, and the $J$ exponents are $(0.906,-0.002,-0.878,-14.57)$. We checked further by forcing $f$ with $\varepsilon(\cos0.3s_2,0,0,\sin0.3s_1)$, so that $\phi$ is generically no longer smooth by HOY (not measured directly). This leaves the $J$ exponent at $-14.54$ for $\varepsilon$ up to $5$. Reproducing the negative exponent is thus robust here, even though it is outside the smooth setting, because $J$ is a small perturbation of a dominated block system **[SKETCH]**.

**The rate condition as stated in the draft needs correcting.** The sufficient condition of HOY is *pointwise, at every $x$ on the attractor, with past-history exponents*: $h_r(x)>h_d(x)$, where $h_d$ is the most negative exponent whose direction is nonempty, that is, meets the attractor beyond $x$. At a typical point it gives smoothness only almost everywhere (HOY attribute almost-everywhere results to Stark). A dense set of measure zero can have Hölder exponent $h_r/h_d<1$, as in their baker-map example, where the graph is visibly wrinkled while the typical condition holds. So "$\lambda_{\rm CLE}<\lambda_{\min}$" computed with natural-measure exponents, the draft's count, is not a condition for a $C^1$ map. The exponent of HOY is also the source of the rate condition, which the draft credits to Lu et al. and J. Hart.

We tested this at embedded fixed points, a necessary test of the sufficient condition, on the scan's typical-condition runs. On Rössler ($h_d=5.69$) it holds in 15 of 21. **On Lorenz the origin has $h_r=11.1$ to $12.3$ against $h_d=22.83$, so 0 of 4 pass.** It is important to note that this failure blocks only the sufficient condition of HOY. We did not determine whether the $-22.83$ direction is nonempty at the origin, and the failure does not itself prove non-differentiability.

### C. Remaining statements

**Proposition 4 is correct but very restrictive.** The hypothesis $N^\top A=M(t)N^\top$ says that the decoded variable obeys a closed equation; in the linear case $\dot{\hat s}=L\hat s+N^\top V(s-\hat s)$, a **Luenberger observer**. It is a separation principle for surrogates containing a model copy.

**The counterexample of Section 4 is correct, but its attractor is a point.** A chaotic exact version is (F) in Sec. V C. Saqib & Padoan Sec. V-A have the sinusoidal one.

**A linear reservoir with a chaotic source [PROVED; known].** The relation $s=T*s$ forces $T(i\omega)=I$ on the spectral support. Since $T$ is rational and strictly proper, the support is finite. Saqib & Padoan Cor. 7 state the same restriction through a linear internal model. So Eq. `linear_fiber_relations` of the draft is vacuous for chaotic sources.

The other sections were checked and found correct: `g_error_decomposition`, the affine forms, `training_residual_identity`, `dmd_result`, `off_manifold_g_error`, and the lemma that $y=\dot r$ for $\xi=g$.

## IV. Beyond the linear decoder

No reservoir structure has been used so far: only that $f$ is $C^1$, that $\phi$ is continuous and maps orbits to driven solutions, and uniform contraction for Proposition 2. All results hold for any synchronized surrogate. It is then natural to ask whether the linear decoder matters.

The following hold with the same proofs **[PROVED]**: Proposition 1 with $\psi\circ\phi=\mathrm{id}$; $J=A+BC(t)$; $u=C(t)\Phi\,\delta x_0+\int\mathcal Ku$; Proposition 2 with $C(t)y=\xi$, from $\psi(r_\varepsilon)-\psi(r)=Cw+o(|w|)$ with $w=O(\varepsilon)$; the quotient definition; and $\mathcal E\cap\ker C(t)=0$.

What changes is that the kernel moves **[PROVED; $\psi$ is $C^2$, $F$ bounded, $CF=I$]**. Differentiating gives $\dot CF+C\dot F=0$, and the equation for $F$ gives $CAF+CB+\dot CF=G$. For $\delta x=Fu+\eta$ with $u=C\delta x$,
$$\dot u=Gu+(\dot C+CA)\eta,\qquad \dot\eta=(QA-F\dot C)\eta=(QA+\dot Q)\eta\quad\text{on }\ker C(t).$$
The extra term $-F\dot C\eta=-FD^2\psi(r)[\dot r,\eta]$ is the turning of the kernel. Block-triangularity survives, whereas the flat fibers, the fixed kernel and the exactness of the off-manifold formula are lost.

Proposition 4 is reformulated as follows **[PROVED]**. If $\Phi(t,\tau)\ker C(\tau)=\ker C(t)$, equivalently $\dot C+CA=0$ on $\ker C$, then $J=A$ on it, the exponents are at most $-\kappa$, and the decoded quotient is $\dot CR+CAR+CB$ for any right inverse $R$.

This is not only a generalization for its own sake. If $e$ is $C^1$ small on a neighbourhood, then $\psi_0=(\mathrm{id}+e)^{-1}\circ\psi$ is an exact decoder, and it is nonlinear even if $\psi$ is linear **[PROVED]**. The nonlinear theory is thus the correct exact reference for imperfect linear readouts.

Two further remarks. A $C^2$ submersive $\psi$ is locally a linear decoder in coordinates $(\psi,\rho)$, although global existence near a merely continuous $\mathcal M$ was not established **[SKETCH]**. And for a drive $h(s)$ with $\psi\circ\phi=h$, invariance and semi-conjugacy hold, while conjugacy needs $\phi$ injective **[PROVED]**.

## V. What decides transverse stability

The exponent $\lambda_\perp$ can already be computed before closing the loop, using $J$ along the driven orbit. The useful question is therefore which simpler quantity decides or bounds it.

### A. The linear case

Take $W$ Hurwitz, $W\Pi+V=\Pi L$, $N^\top\Pi=I$ and $T(z)=N^\top(z-W)^{-1}V$. Substituting $V=(z-W)\Pi-\Pi(z-L)$ gives
$$I-T(z)=H(z)(zI-L),\qquad H(z)=N^\top(zI-W)^{-1}\Pi,\qquad\det H(z)=\chi_\perp(z)/\chi_W(z).$$
This is **[PROVED, checked to $3\cdot10^{-13}$]**. In words: **the transverse eigenvalues are the zeros of $H$, that is, the zero dynamics of $(W,\Pi,N^\top)$**. Transverse stability is the minimum-phase property of the reservoir from tangent input to readout. The counterexample of the draft has $H=(z-1)/(z^2+2z+7)$.

On the status of this: the spectral content (triangular form, assignability) is known from Saqib & Padoan; $T=I$ at source eigenvalues is their moment matching; the characteristic equation $\det(I-T)=0$ and the Nyquist argument are in Rivkind & Barak for fixed points. We did not find the factorization, the identification with zeros, or the items below in what we read.

Several consequences follow **[PROVED, checked]**.

- *Exact count.* The winding number of $(z+a)H(z)$, $a>0$, equals the number of unstable transverse eigenvalues. Checked: 0 mismatches of 60.
- *Restricted small gain.* For any $d\times d$ matrix $M$, $(zI+M)H(z)-I=(N^\top W+MN^\top)(z-W)^{-1}\Pi$. If its $H_\infty$ norm is below one, $H$ has no zeros in the right half plane. The naive gain $\|T\|$ is always at least one. Checked over 300 random cases with 146 stable: $M=aI$ certifies 51, $M=-N^\top WR_0$ certifies 28, and there are no false certificates.
- *Frequency integral (Jensen/Bode type, any $N$).* $\frac1{2\pi}\int\log|\det(I-T(i\omega))|d\omega+\frac12\operatorname{tr}(N^\top V)=\sum_{\operatorname{Re}c_i>0}\operatorname{Re}c_i$, with $c_i$ the closed-loop eigenvalues. Checked to $5\cdot10^{-4}$ (quadrature). This is an exact closed form for the total unstable transverse rate.
- *Assignability for every $d$.* Identify $\ker N^\top$ with $\mathbb R^n/\operatorname{Im}\Pi$ through a section $\sigma=\sigma_0+\Pi X$. Then $QW|_{\ker}$ becomes $\pi W\sigma_0+\pi W\Pi X$, a state-feedback problem. If $(W,\Pi)$ is controllable, any conjugate-closed multiset is attained by an exact $N$ (Wonham). Checked for $d=2$ to $3\cdot10^{-7}$, including unstable targets. Known: Saqib & Padoan Remark 1, by PBH.
- *Cancellation.* For $d=1$, $\lambda_\perp$ is an eigenvalue of $W$ if and only if there is a pole-zero cancellation, i.e. an unobservable or uncontrollable mode. Proposition 4 is the first, and $QV=0$ is a form of the second.

### B. The time-varying case

We now let the linearization vary along a chaotic orbit **[PROVED; appears new]**. Assume a bounded $F$ with $\dot F=AF+B-FG$ and $N^\top F=I$. Using $\frac{d}{d\tau}[\Phi(t,\tau)F(\tau)]=\Phi(\dot F-AF)$, one finds
$$(I-\mathcal K)u=H\left[\left(\tfrac{d}{dt}-G\right)u\right]+N^\top\Phi(t,t_0)F(t_0)u(t_0),\qquad H(t,\tau)=N^\top\Phi(t,\tau)F(\tau),\quad H(t,t)=I.$$
The kernel of $d/dt-G$ is the source tangent flow, the eigenvalue-one part of $\mathcal K$. With $v:=\dot u-Gu=N^\top A\eta$, $\eta_0=Q\delta x_0$ and $w(t):=N^\top\Phi(t,t_0)\eta_0$ we get
$$\int_{t_0}^tH(t,\tau)v(\tau)d\tau=w(t),\qquad\eta(t)=\Phi(t,t_0)\eta_0-\int\Phi(t,\tau)F(\tau)v(\tau)d\tau.$$
So $\lambda_\perp<0$ if and only if the time-varying filter $H$ has an exponentially stable inverse: $\dot\eta=QA\eta$ is its inverse dynamics, since for $\dot x=Ax+Fv$, $y=N^\top x$, holding $y=0$ forces $v=-N^\top Ax$. For any bounded $M(t)$, differentiating and adding $Mw$ gives
$$v(t)=(N^\top A+MN^\top)(t)\Phi(t,t_0)\eta_0+\int R_M(t,\tau)v(\tau)d\tau,\qquad R_M(t,\tau)=-(N^\top A(t)+M(t)N^\top)\Phi(t,\tau)F(\tau).$$

**Theorem 1 (Restricted small gain).** *If $\sup_t\int\|R_M(t,\tau)\|e^{\sigma(t-\tau)}d\tau<1$ for some $0\le\sigma<\kappa$ and some bounded $M$, all transverse exponents are at most $-\sigma$.*

*Proof.* Set $v_\sigma=e^{\sigma t}v$. Then $|v_\sigma(t)|\le c'+g\sup_{\tau\le t}|v_\sigma(\tau)|$ with $g<1$, so $v=O(e^{-\sigma t})$. The formula for $\eta$ with $\sigma<\kappa$ gives the same rate for $\eta$. $\square$

The choice $M=-N^\top AR_0$ with $R_0=N(N^\top N)^{-1}$ gives $R_M=-N^\top AQ_0\Phi F$, with $Q_0=I-R_0N^\top$: **only the readout's sensitivity to invisible directions, times the invisible response to tangent input**. If $N^\top AQ_0=0$ the gain is zero, so Proposition 4 is the zero-gain case. If $Q_0\Phi F$ vanishes the gain also vanishes. A direct corollary is $\lambda_\perp\le-\kappa+c\|FN^\top A|_{\ker}\|$, from $QA=A-FN^\top A$.

Finally, there is a loop identity **[PROVED]**: $N^\top AF+N^\top B=G$, so $R_0(t,t)=N^\top B-G$. The zero-lag loop gain minus the source Jacobian is the restricted gain at zero lag.

### C. An exact test family

To test these statements we need a system where the answer is known. Let the source be Lorenz, $r=(y,z)$, $h'(s_3)=a_0\operatorname{sech}^2((s_3-27)/4)$ (`amp` $=a_0$), $c=(0,0,-1)$, and define family (F):
$$\dot y=g(s)-k(y-s)+c(z-h(s)),\qquad\dot z=h'(s_3)g_3(s)+D\cdot(y-s)+E(z-h(s)).$$
Then $\phi=(s,h(s))$ and $N^\top=(I,0)$ are exact. With $\chi=z-h(y)$ the closed loop is **exactly** $\dot y=g(y)+c\chi$, $\dot\chi=a(y)\chi$, with $a=E+a_0\operatorname{sech}^2((y_3-27)/4)$. Hence $\lambda_\perp=\langle a\rangle$ in closed form, and the CLEs are constant.

| $E,a_0$ | $J$ exponents | $\langle a\rangle$ | largest CLE |
|---|---|---|---|
| $-1,0.5$ | $0.906,-0.002,-0.878,-14.57$ | $-0.876$ | $-1.08$ |
| $-1,3$ | $0.906,-0.001,-0.259,-14.57$ | $-0.258$ | $-1.08$ |

The second row is worth noting: $\lambda_\perp$ exceeds the largest CLE by $0.82$ in an exact, smooth, chaotic, transversely stable system.

We then test the restricted gain with $M=-N^\top AR_0$, where $\kappa$ is the driven rate and the truth comes from $\sup a$:

| $E,a_0,D$ | $\kappa$ | gain at $\sigma=0$ | largest certified $\sigma$ tested | truth |
|---|---|---|---|---|
| $-3,0.5,0.3$ | $3.16$ | $0.09$ | $2.85$ ($0.98$) | $\sup a=-2.5$, $\langle a\rangle$ near $-2.9$ |
| $-1,0.5,0.3$ | $1.08$ | $0.24$ | $0.81$ ($0.81$) | $\langle a\rangle=-0.88$ |
| $-0.2,0.1,0.3$ | $0.26$ | $0.34$ | $0.13$ ($0.66$) | $\sup a=-0.1$ |
| $-1,3,0.3$ (non-uniform) | $1.08$ | $1.13$ | none | $\langle a\rangle=-0.26$, $\sup a=2$ |
| $2,0.5,12$ (unstable) | $1.0$ | $6.4$ | none | $\langle a\rangle>0$ |
| $0.5,0.2,5$ (unstable) | $0.65$ | $2.1$ | none | $\langle a\rangle>0$ |

With $M=0$ the gain was above one on every case ($1.06$, $1.09$), so **the shift $M$ is essential**. The values $0.13$ and $0.81$ are lower bounds on $-\lambda_\perp$ consistent with the truth, and $\sigma<\kappa$ limits certificates to rates below $\kappa$. The certificate is a uniform one, and it fails on the non-uniform stable case, which is correct behaviour for a supremum-based gain (see Sec. VI D).

### D. A non-differentiable map: the quotient operator

**[PROVED; appears new.]** Saqib & Padoan and Bizyaeva et al. do not treat this case. Let $\mathcal D$ be the admissible bundle, with frame $\Xi(t)$, $\dot\Xi=G\Xi$, and $Y$ the image frame, $\dot Y=JY$, $N^\top Y=\Xi$. Choose a $C^1$ left inverse $L(t)$ with $L\Xi=I_k$. Write $x=Ya+\zeta$ with $LN^\top\zeta=0$. Then $\dot\zeta=J\zeta-Y\dot a$, and differentiating the constraint gives $\dot a=(\dot LN^\top+LN^\top J)\zeta$, so
$$\dot\zeta=[J-Y(\dot LN^\top+LN^\top J)]\zeta\quad\text{on }W(t)=\ker(LN^\top).$$
This is the quotient cocycle in coordinates, since $W(t)$ is complementary to $\mathcal E$. If $S(t)=\ker L$ is $G$-invariant, then $\dot L=-LG$, and using $Gu_S\in S$ we get
$$\dot\zeta=Q_{\mathcal E}J\zeta,\qquad Q_{\mathcal E}=I-YLN^\top.$$
**So in the non-differentiable case $QA$ is replaced by $Q_{\mathcal E}J$, with $k<d$.** On $\ker N^\top$ it behaves like $QA$, and on the extra $d-k$ decoded directions the feedback $BN^\top$ survives. The source's stable exponents do not appear: the equation does not contain $G$ on $S$, which is why those exponents are not reproduced in general. Checked for $k=2$, $d=3$ to $6\cdot10^{-10}$.

The analogue for $I-\mathcal K$, with $u=\Xi a+u_S$, reads
$$u_S(t)=N^\top\Phi(t,t_0)\zeta_0-\int N^\top\Phi(t,\tau)Y(\tau)\dot a(\tau)d\tau+\int\mathcal K(t,\tau)u_S(\tau)d\tau.$$
The gain-one part $\Xi a$ is deflated, whereas the rest of $\mathcal K$ still acts on $u_S$.

**Is the leading transverse direction invisible to the readout?** Mostly, but not always. We take a representative $\zeta$ in $W$ and the ratio $|N^\top\zeta|/(\|N\|_2|\zeta|)$; a random vector gives $0.07$ to $0.12$. This is valid only for runs where the third QR direction is transverse. On Rössler with $\gamma=5$, $\rho=0.9$ we find $0.014$, $0.014$ (strongly invisible); on Rössler with $\gamma=20$, $\rho=0.5$, $0.10$ to $0.13$ (no better than random); on Lorenz, in all 12 runs ($\gamma=1,5,20$), $0.000$ to $0.026$ (strongly invisible). So "the transverse directions are the readout-invisible ones" is well supported on Lorenz and on Rössler at $\gamma=5$, but not on Rössler at $\gamma=20$, $\rho=0.5$, where the source is thinly sampled along its stable direction and the $d-k$ decoded direction can matter. The sample is small (3 runs per setting).

There is a bound **[PROVED]**, $\lambda_\perp\le-\kappa+c\sup\|Q_{\mathcal E}BN^\top|_W-YLN^\top A|_W\|$, which is probably far too loose to be useful in practice (not tested on reservoirs).

**A sum rule without smoothness [PROVED, checked to $3\cdot10^{-10}$].** One has
$$\sum\text{quotient exponents}=\sum\text{CLE}+\langle\operatorname{tr}CB\rangle-\sum_{\mathcal D}\lambda,$$
with $n-k$ quotient exponents, so $(n-k)\lambda_\perp\ge\sum\text{CLE}+\langle\operatorname{tr}CB\rangle-\sum_{\mathcal D}\lambda$. This is a driven-phase instability certificate that needs no smooth $\phi$ and no exact source stable exponent, and it is exact for $n-k=1$. It explains one effect of an $N^\top B$ penalty: each unit of trace adds exactly one unit to the transverse sum. For large $n$ it is weak, because the bulk of $\operatorname{tr}A$ dominates. Checked in (F) to three decimals.

**A Riccati form [PROVED].** For any $C^1$ right inverse $R$ and any $N$: $\dot u=G_Ru+N^\top A\eta$, $\dot\eta=Q_RA\eta+Z_Ru$, with $G_R=N^\top(AR+B)$ and $Z_R=Q_R(AR+B)-\dot R$. A bounded solution of $Z_R=0$ is exactly a $d$-dimensional $J$-invariant complement of $\ker N^\top$. Whether one exists when $\phi$ is not $C^1$ is open.

### E. Geometry **[PROVED, checked]**

- *The gap has no universal sign, and "$\lambda_\perp>$ largest CLE" is [FALSE] as a theorem.* For symmetric $W$ and minimum-norm $N$, $QW|_{\ker}$ is a compression, so $\lambda_\perp\le\lambda_{\max}(W)$. Checked: maximum difference $-1.6\cdot10^{-4}$ over 300 cases. The observed positive gap needs non-normality or obliquity.
- *Energy bound.* With $F=R_0+D\zeta$, $D\zeta$ in $\ker N^\top$ ($\phi=R_0s+\zeta(s)$): $\lambda_\perp\le\mu_2(A|_{\ker})+\|D\zeta\|\|N^\top A|_{\ker}\|$. Checked: no violations in 300, median slack $6.5$, so it is loose. As a corollary, minimum-norm $N$, flat $\mathcal M$ and Euclidean contraction give stability. Instability is carried by the readout-invisible geometry and non-normality.
- *Passivity.* If $\dot S+SA+A^\top S\le-2\sigma S$ and $SF=NM(t)$ ($Q$ is $S$-orthogonal), then $\lambda_\perp\le-\sigma$. This is a positive-real condition on $H$.
- *Dual of Proposition 4.* The driven system in $(u,\eta)$ is $\dot u=(G-N^\top B)u+N^\top A\eta$, $\dot\eta=-QBu+QA\eta$. Driven and closed-loop transverse blocks differ only through $(QB)(N^\top A)$. If $QB=0$ or $N^\top A|_{\ker}=0$ the transverse exponents are CLEs.

### F. What cannot decide it

**Theorem 2 [PROVED, checked].** *There is no function of the CLEs, $e$ and the source that decides $\lambda_\perp$, also for chaotic sources and non-differentiable $\phi$.*

*Proof.* Take any source $g$ and the family $\dot y=g(s)+k(s-y)+c\eta$, $\dot\eta=E\eta+D(y-s)$, optionally with a slave $\dot w=-bw+y$, with $b$ below the source's contraction rate. Then $\phi=(s,0,\psi(s))$ with $\psi$ generically non-differentiable, and $N^\top=(I,0,0)$ gives $e=0$. The driven $(y,\eta)$ block is $\begin{pmatrix}-k&c\\D&E\end{pmatrix}$. Fix trace and determinant by $k=E-\operatorname{tr}$, $cD=-kE-\det$. Then the CLEs are fixed, while in the closed loop $\dot\eta=E\eta$, so $\lambda_\perp=E$ is any real number. Checked with fixed eigenvalues $-2\pm3i$ and $E=-2,0.5,3$. $\square$

*(Editorial note added in this rewrite: for $d>1$ with a scalar gain $k$, the other $y$ directions have rate $-k$, which moves with $E$. The proof needs $K=\operatorname{diag}(k,k_0,\dots)$ with $c,D$ along one axis, and $E>-b$ with the slave. `main.tex` states it that way. This correction has not been reviewed.)*

The linear version is Saqib & Padoan eq. (32): the same reservoir with a different exact readout. Theorem 2 extends the principle to chaos and non-smooth maps, but with different reservoirs. For a fixed reservoir and chaotic source there is no family of exact readouts, and an empirical analogue is tested below.

**No closed form exists [PROVED].** With $n-k=1$, moving the second eigenvalue of $W$ leaves the largest CLE and $N^\top V$ fixed and moves $\lambda_\perp$. So no formula in ($\lambda_\perp$, largest CLE, loop gain) alone exists. What exists are two-sided identities in the *sum* (Sec. V D), an exact integral in the linear case (Sec. V A) and sufficient gains (Sec. V B).

**An empirical analogue for a fixed reservoir and chaotic source** (checked; one reservoir, three random directions). On Rössler with $\gamma=5$, $\rho=0.9$, $n=200$, we set $N=N_0+\Delta$ with $\Delta$ in the 80 weakest singular directions of the training data:

| $\|\Delta\|/\|N_0\|$ | train NRMSE | $\lambda_\perp$, trials 1, 2, 3 |
|---|---|---|
| $0$ | $6.4\cdot10^{-5}$ | $1.90,1.90,1.90$ |
| $1$ | $6.5\cdot10^{-5}$ | $3.03,2.57,2.07$ |
| $3$ | $6.7\cdot10^{-5}$ | $5.71,8.49,3.08$ |
| $10$ | $9\cdot10^{-5}$ | $16.9,34.6,4.46$ |

The training error stays essentially flat while $\lambda_\perp$ moves by an order of magnitude. In machine-learning terms, the fit does not see this quantity. Random directions destabilize, and the largest stabilization seen was $1.90$ to $1.77$. This is the chaotic counterpart of the free transverse modes of Saqib & Padoan, measured and not proved.

**Simple driven-phase predictors** (checked; 108 runs per source, $n=200$). We report the Spearman correlation with $\lambda_\perp$ within $\gamma=1,5,20$, each cell having $n=36$:

| Quantity | Rössler | Lorenz |
|---|---|---|
| $\operatorname{tr}N^\top B$ | $+0.70,+0.86,+0.49$ | $+0.53,+0.70,+0.84$ |
| largest CLE | $+0.60,+0.46,+0.30$ | $+0.70,+0.64,+0.46$ |
| $\mu_2(A|_{\ker})$ | $+0.57,+0.44,+0.32$ | $+0.75,+0.74,+0.61$ |
| $\|N^\top A|_{\ker}\|$ | $-0.06,-0.29,-0.13$ | $+0.48,+0.33,+0.20$ |

$\operatorname{tr}N^\top B$ beats the largest CLE in 5 of 6 cells and keeps a partial correlation of $0.45$ to $0.85$ given the CLE. The CLE keeps $0.05$ to $0.73$ given the trace, so both carry information. Within a fixed $\sigma$ ($n=12$) the ranking is mixed, and the CLE often wins at small $\sigma$. The sign agrees with the sum rule, but the average shift $(\operatorname{tr}N^\top B)/(n-k)$, about $0.1$ to $0.4$, is smaller than the gap, so the sum rule does not by itself explain the correlation. $\|N^\top A|_{\ker}\|$, the coupling in the bound, is a poor predictor alone. **No simple quantity replaces computing $\lambda_\perp$**, which is cheap anyway. The gap $\lambda_\perp-$ largest CLE is positive in 108/108 on both sources, with median $+1.86$ and $+0.78$.

**An $N^\top B$ penalty on tanh reservoirs [SKETCH].** Since $N^\top B=\gamma N^\top DV$ and $N^\top A|_{\ker}=\gamma N^\top DW|_{\ker}$ share the factor $N^\top D(t)$, penalizing the first also shrinks the coupling $\|N^\top A|_{\ker}\|$, if $V$ does not align badly. The loop identity suggests that the natural target is $N^\top B$ near $G$ rather than $0$ **[CONJECTURE]**.

## VI. Imperfect reconstruction

We now relax realizability. For any readout, Bizyaeva et al. Prop. IV.1 give a Gronwall bound with the closed-loop Lipschitz constant, which is the known baseline, proved there. Normal hyperbolicity relative to a manifold is the wrong frame when $\phi$ is merely continuous, so we look for something else.

### A. A tube theorem under uniform transverse contraction

**Theorem 3 [PROVED; no tangential hyperbolicity, no rate condition].** *Let $U$ be a compact trapping region of $g$ with $g$ inward on $\partial U$, $m$ the minimum inward speed, and $\mathcal A=\bigcap\Theta_tU$. Let $\phi$ be $C^2$ on a neighbourhood of $U$ solving the synchronization identity, $\psi_0$ be $C^2$ and exact on $U$, and let the cocycle of $L=QA+\dot Q$ over the semiflow on $U$ satisfy $\|\Psi\|\le ce^{-\sigma t}$, with $L$ Lipschitz in $s$. The closed loop uses a decoder $\psi$ with $\|\psi-\psi_0\|\le\varepsilon$ on a neighbourhood. Then a tube is forward invariant, with $|\chi(t)|\le c_2e^{-\sigma't}|\chi(0)|+c_3\delta/\sigma'$, where $\delta=L_s\varepsilon$.* By continuity, uniformity on $\mathcal A$ alone gives uniformity on a smaller $U$.

*Proof.* Use coordinates $\hat s=\psi_0(x)$, $\chi=x-\phi(\hat s)$. Then $\dot\chi=L(\hat s)\chi+O(|\chi|^2)+O(\delta)$ and $\dot{\hat s}=g(\hat s)+O(|\chi|+\delta)$. Let $V(s,\chi)=\int_0^T|\Psi(\tau;s)\chi|^2d\tau$ with $c^2e^{-2\sigma T}<1/2$. $V$ is a quadratic form, Lipschitz in $s$, with derivative along the exact $s$-flow at most $-|\chi|^2/2$. Along the perturbed motion the extra terms are $O(|\chi|^3+\delta|\chi|+(|\chi|+\delta)|\chi|^2)$. For a small tube, $\dot V\le-2\sigma'V+c_1\delta\sqrt V$, which gives the bound. If $\delta$ is small enough that the defect in $\dot{\hat s}$ is below $m$, $\hat s$ cannot leave $U$. So the tube is forward invariant. $\square$

Two corollaries follow **[PROVED]**. The first is *upper semicontinuity*: $\hat s$ is an $O(\delta)$ pseudo-orbit of $g$ on $U$, and as $\Theta_TU$ enters any neighbourhood of $\mathcal A$, closed-loop $\omega$-limit sets converge to $\phi(\mathcal A)$ as $\varepsilon\to0$. This is a statement about the location of the attractor, and no shadowing is needed. The second is a *forecast bound in source coordinates*: $|\hat s(t)-s(t)|\le\varepsilon_{\rm eff}(e^{L_gt}-1)/L_g+\dots$, with $\varepsilon_{\rm eff}=c(1+L_v/\sigma')\delta$ and $L_v=\sup\|\dot C+CA\|$. Compared with Bizyaeva Prop. IV.1 this replaces the closed-loop Lipschitz constant, which is large for a reservoir, by the source Lipschitz constant, at the price of the $1/\sigma'$ factor and the hypothesis of transverse contraction.

We checked this in (F) with $\psi=y+\varepsilon bz$, $\kappa$ near $1$ and source contraction $14.57$, so that normal hyperbolicity fails:

| $E,a_0$ | $\varepsilon$ | median $|\chi|$ | sup $|\chi|$ |
|---|---|---|---|
| $-1,0.5$ | $10^{-4},10^{-3},10^{-2}$ | $3.4\cdot10^{-5},3.4\cdot10^{-4},3.4\cdot10^{-3}$ | $4.5\cdot10^{-5},4.5\cdot10^{-4},4.5\cdot10^{-3}$ |
| $-2,1$ | $10^{-4},10^{-3},10^{-2}$ | $1.1\cdot10^{-4},1.1\cdot10^{-3},1.1\cdot10^{-2}$ | $2.4\cdot10^{-4},2.4\cdot10^{-3},2.4\cdot10^{-2}$ |

The width is linear in $\varepsilon$, with supremum over median about $1.3$ to $2$. The median time to $|\hat s-s|>2$ for $E=-1$, $a_0=0.5$ is $11.3$, $6.1$, $1.9$ at $\varepsilon=10^{-6},10^{-4},10^{-2}$, with slope about $1/\lambda_1$ in $\log(1/\varepsilon)$.

There is a subtlety: $U$ must be chosen with care. On Lorenz, a trapping $U$ containing $C_\pm$ has a maximal invariant set larger than the chaotic attractor, and the tube and upper semicontinuity then speak about that larger set.

The theorem also has a clear limit. A $C^2$ map $\phi$ on $U$ is the strong hypothesis, and **30/810 and 163/810 are upper bounds, not counts of runs that satisfy it**. Those counts use the typical-point condition, whereas the theorem needs differentiability at every point of $\mathcal A$ (the HOY condition at all $x$, where it is applied as a sufficient condition), and also an extension to the open set $U$ off the attractor, which HOY do not provide. In the 108-run scan: Rössler has 21 typical, 15 after the fixed-point test (further orbits untested); Lorenz has 4 typical, 0 after it.

This can be relaxed **[PROVED; the small-$K$ remark of HOY motivates it]**. The proof uses the actual system only through $\sup|G-G_0|\le\delta$, so the $C^2$ hypothesis applies to a *reference* $(f_0,\phi_0,\psi_0)$ and not to the actual reservoir, whose $\phi$ may be only Hölder. Family (F) with small unmatched forcing is an example: a Hölder map with small $K$ near a smooth reference. For a generic filter-type reservoir such a reference with bounded $F_0$ and contracting $Q_0A$ does not obviously exist: mollifying $\phi$ at scale $h$ gives a defect $O(h^\gamma)$ but $\|F_0\|$ of order $h^{\gamma-1}$, which destroys uniform contraction **[SKETCH]**. So the relaxation covers near-observer surrogates and not generic random reservoirs.

### B. A converse Lyapunov argument

**Theorem 4 [PROVED; standard argument, statement apparently not in this literature].** *Suppose $G_0$ is Lipschitz with $\mathcal M$ invariant and $\operatorname{dist}(\Xi_tx,\mathcal M)\le ce^{-\sigma_0t}\operatorname{dist}(x,\mathcal M)$ near $\mathcal M$. Let $|G-G_0|\le\delta$ near $\mathcal M$. Then every solution of $\dot x=G(x)$ starting close enough satisfies $\limsup\operatorname{dist}(x(t),\mathcal M)\le c'\delta/\sigma$, for $\sigma<\sigma_0$.* No regularity of $\phi$ is required.

*Proof.* Let $V(x)=\sup_{t\ge0}e^{\sigma t}\operatorname{dist}(\Xi_tx,\mathcal M)$. Pick $T$ with $ce^{(\sigma-\sigma_0)T}\le1$: the supremum is attained on $[0,T]$, so $V$ is Lipschitz with constant $e^{(L+\sigma)T}$, and $\operatorname{dist}\le V\le c\operatorname{dist}$. Also $V(\Xi_hx)\le e^{-\sigma h}V(x)$. Along $\dot x=G(x)$: $D^+V\le-\sigma V+\mathrm{Lip}\,\delta$. $\square$

**The regularity needed is on the decoder side.** $G_0=f(x,\psi_0(x))$ needs $\psi_0$ Lipschitz with $\psi_0\circ\phi=\mathrm{id}$ on $\mathcal M$, that is, $\phi^{-1}$ Lipschitz, $|\phi(s)-\phi(s')|\ge c|s-s'|$. This holds if $\mathrm{Lip}(e)<1$ on $\mathcal A$, since $\|N\||\phi(s)-\phi(s')|\ge(1-\mathrm{Lip}\,e)|s-s'|$, and it does **not** need $\phi$ Lipschitz. By Kirszbraun, $\psi_0=\psi-\tilde e$ with the same supremum norm. So what is needed is small $e$ in supremum norm plus $\mathrm{Lip}(e)<1$, and this can be checked from data as the largest $|e(s)-e(s')|/|s-s'|$ over nearby pairs. We checked this on data: on Rössler the largest ratio over nearest non-consecutive pairs is below one in 108/108 runs (median $0.011$), and on Lorenz in 79/108 (99th percentile below one in 90/108). These pairs are at distance about $0.2$ to $0.4$, so this bounds $\mathrm{Lip}(e)$ only at data resolution. **Fine-scale evidence points the other way:** in the rate-condition runs $De$ on the stable direction is $0.49$ to $3.5$ (Rössler) and $4.3$ to $9.3$ (Lorenz). If that direction is nonempty in the sense of HOY, this gives $\mathrm{Lip}(e)>1$ at small scale in most of them and the route through $\mathrm{Lip}(e)<1$ fails, although $\phi^{-1}$ could still be Lipschitz by another argument. The remaining hypothesis is the exponential attraction of $\mathcal M$, which is exactly what fails or is unverified on these sources.

### C. Exponential attraction with a continuous map **[SKETCH; relies on standard theorems not re-derived here]**

If $\mathcal A$ is uniformly hyperbolic and the quotient cocycle is uniformly contracting, then $\mathcal E$ is continuous and dominates the quotient, so it has an invariant complement. Then $\mathcal M$ is a **hyperbolic set of the closed loop in $\mathbb R^n$, with no smoothness of $\phi$ needed**. $\phi(W^u)$ lies in $W^u(\phi(s))$, because backward differences decay exponentially. So $W^u(\mathcal M)$ is contained in $\mathcal M$, the stable manifolds fill a neighbourhood by invariance of domain, and $\mathcal M$ is an exponentially attracting attractor. Structural stability then gives a nearby orbit-equivalent attractor under a $C^1$-small perturbation, and Theorem 4 gives the $C^0$ version. Oishi et al. use HPS Theorem 5.5 for a partially hyperbolic analogue. The structural-stability and shadowing route is that of Hara & Kokubu 2026 (Sec. VII A), in a smooth, strongly contracting, discrete-time setting. **Lorenz and Rössler are not uniformly hyperbolic, so this does not cover the numerics of the paper.** For Lorenz (singular hyperbolic) with a trapping cone field this is a **[CONJECTURE]**, and for Rössler it is open.

There is also a shadowing variant **[SKETCH]**. Palmer-type shadowing along the driven orbit with a dichotomy for $J$ gives a true orbit within $c\|d\|$, with $c$ of order $1/|\lambda_\perp|$ in the transverse part. It needs $\lambda_\perp\ne0$, not $\lambda_\perp<0$: the sign decides attracting versus saddle.

### D. The non-uniform case

One may hope that $\lambda_\perp<0$ suffices. **An $O(e)$ supremum bound is [FALSE] in general (checked).** The situation $\langle a\rangle<0$ with positive rates on embedded orbits is the bubbling setting of Ashwin, Buescu, Stewart 1994. In (F) with $E=-1$, $a_0=3$ we have $\langle a\rangle=-0.26$, and $a=2$ at the fixed points $C_\pm$:

| $\varepsilon$ | median $|\chi|$ | 99.9% | sup, $T=8000$ |
|---|---|---|---|
| $10^{-5}$ | $9.3\cdot10^{-5}$ | $1.3\cdot10^{-2}$ | $3.8\cdot10^{-2}$ |
| $10^{-4}$ | $9.2\cdot10^{-4}$ | $1.7\cdot10^{-1}$ | $5.7\cdot10^{-1}$ |
| $10^{-3}$ | $1.3\cdot10^{-2}$ | $84$ | $97$ |
| $10^{-2}$ | $86$ | $86$ | $90$ |

The ratio of supremum to median is about 400 to 600 at small $\varepsilon$, compared with $1.3$ to $2$ in the uniform case, where the supremum is also linear (for example $4.5\cdot10^{-5}$, $4.5\cdot10^{-3}$ at $T=8000$). **At $\varepsilon=10^{-3}$ a burst takes the trajectory permanently away ($\chi$ near $85$), with $\lambda_\perp<0$ and exact $\phi$ in the limit.** So in this example a small readout error, a negative transverse exponent and a loss of the attractor coexist. This is an example of the stable-but-failing runs of the paper, and not a proof that those runs fail this way.

A moment bound replaces the supremum bound **[PROVED at the linear level]**. For $\dot\eta=L_\perp(t)\eta+d$, $|d|\le\varepsilon$, with $L(q)=\lim\frac1T\log\mathbb E\|\Psi_\perp(T)\|^q<0$, $q\ge1$, Minkowski and invariance give $\|\eta\|_{L^q(\mu)}\le c\varepsilon q/|L(q)|$, so $\mu\{|\eta|>x\}\le(c\varepsilon q/(|L(q)|x))^q$. The quantity $L(q)/q$ interpolates from $\lambda_\perp$ ($q\to0$) to the uniform rate ($q\to\infty$). In (F) with $E=-1$, $a_0=3$: $L(1)=-0.056$, $L(2)=+0.18$, so the tails have exponent between 1 and 2 (estimated from 1000 windows of length 20, so rare events are poorly sampled). In comparison, for $E=-1$, $a_0=0.5$, $L(q)<0$ at all tested $q$. The nonlinear extension is not proved: it needs $\eta$ to remain in the linear region between bursts.

**Why do stable runs fail on real reservoirs?** We tested the conjecture that this mechanism is responsible, and it gets weak support at best. We use 108 runs per source; stable means $\lambda_\perp<0$ and fail means not on the source attractor after 1000 time units. Rössler has 49 stable runs of which 12 fail, and Lorenz 101 stable of which 25 fail.

| Predictor among stable runs | Rössler | Lorenz |
|---|---|---|
| AUC $\lambda_\perp$ | $0.50$ | $0.62$ |
| AUC $L(1),L(2),L(8)$ | $0.60,0.60,0.59$ | $0.70,0.71,0.72$ |
| AUC largest finite-time rate | $0.58$ | $0.72$ |
| AUC largest CLE | $0.35$ | $0.50$ |
| fail rate given $L(2)>0$ vs $\le0$ | $0.67$ ($n=9$) vs $0.15$ | $0.60$ ($n=5$) vs $0.23$ |
| fail rate given positive transverse rate at $C_+$ | - | $0.33$ ($n=3$) vs $0.24$ |
| fail rate given positive transverse rate at $C_-$ | - | $0.83$ ($n=6$) vs $0.21$ |
| fail rate given stable closed-loop fixed point within 5 of a source fixed point | none found | $0.73$ ($n=11$) vs $0.19$ |

$L(q)$ is estimated from 60 windows of length 10, so it is noisy, and the AUCs have no correction for selection among predictors. The transverse rate at the Lorenz origin is positive in 91/101 runs because the reservoir extrapolates there (median $|e|=10$), so **uniform transverse contraction essentially never holds on these Lorenz runs, and the hypotheses of Theorem 3 and Sec. VI C fail for them.**

There is also a separate, tangential mechanism **[SKETCH]**. For Lorenz at $\rho=28$, $C_\pm$ have real part of the eigenvalue $+0.094$ (Hopf at $\sigma(\sigma+\beta+3)/(\sigma-\beta-1)=24.74$). A readout error of order $0.09$ in $Dg$-like terms can stabilize them, which is a failure of $C^1$ closeness in the *tangent* block and not of transverse stability. It accounts for 7 of the 23 fixed-point ends among stable Lorenz runs. The other 16 end at fixed points not within 5 of a source fixed point (untrained attractors, as in Hart). On Rössler this mechanism was not seen. The failures of stable runs are thus heterogeneous, and we have no single criterion for them.

## VII. Relation to the literature

Reading depth matters for what follows, so we state it. The map of the literature session is `docs/literature_map.md` on branch `literature-map`.

| Source | Read | Overlap |
|---|---|---|
| Saqib & Padoan arXiv:2610.08987 | Props. 2-4, Remark 1, Cor. 7, Sec. V | Linear reservoir, neutral linear exosystem: triangular form, transverse eigenvalues freely assignable, moment matching $T=I$ at source eigenvalues, zero-error instability; nonlinear: invariant manifold and KKL map, local, no transverse operator. **Not there: chaotic sources, non-differentiable maps, time-varying transverse operator, zeros and factorization.** |
| Bizyaeva et al. arXiv:2610.04343 | Props. III.1, IV.1 | KKL view; exact on $X$ iff closed-loop reproduces (our Prop. 1, and supports the repair of Error 2); finite-time Gronwall forecast bound. No transverse analysis (only named as a question). |
| Oishi et al. arXiv:2602.11069 | Theorem 1, Methods | Linear $QB=0$: known. Controllability remark. Partially hyperbolic set via HPS 5.5. |
| Oishi et al. arXiv:2606.24303 | Abstract, keyword scan | No theorem overlap seen. Not read in full. |
| Hara & Kokubu 2024 | Full | Degenerate reservoir (no $r$ dependence), conjugacy on the image; no stability theorem. |
| Hara & Kokubu 2026 (SIADS 25, 1834) | Sections 2.1, 2.3 (statements), 2.24, 3, 4, 5 read; embedding proof of 2.15 and Appendix A skimmed | See Sec. VII A. Discrete time, smooth section, strong fiber contraction. Technique of Sec. VI C is there; hypotheses and conclusions differ. Three issues found in the paper. |
| A. Hart 2024 Physica D | Keyword scan, one section | GS existence, linear form, embeddings, autonomous field on an embedded set. No stability theorem in scan. |
| J. Hart 2024 Chaos | Main argument, via fetch | Heuristic with no theorem: rate condition and "stay close to CLEs". Family (F) shows rate failure does not force loss of $-14.57$, and gives a gap. |
| Wong et al. arXiv:2408.04058 | Via fetch | Contraction of driven reservoir; closed-loop robustness stated as open. |
| Hunt, Ott, Yorke 1997 PRE 55, 4029 | Full | Pointwise DGS condition, Hölder exponent $h_r/h_d$, empty directions, exact synchronism as non-generic exception, small $K$. Heuristic plus example, no theorem. Source of the rate condition. See Sec. III. |
| Rivkind & Barak PRL 2017 | Key equations via fetch | $G_{CL}=G_{OL}/(1-G_{OL})$, Nyquist, for fixed points in mean-field: known principle for $\det(I-T)=0$. |
| Wikner et al. | Via literature map | $N^\top DB$ penalty known in substance. |
| Ashwin, Buescu, Stewart 1994 | Abstract | Bubbling: known. |
| Freudenberg & Looze 1985, Iglesias 2002, Byrnes-Isidori-Willems 1991, Palmer 1988, Andrieu & Praly 2006 | Secondary or snippets | Bode integral, LTV analogue, passivity and zero dynamics, shadowing, KKL: known in their fields. The sync identity for linear reservoirs is the KKL equation. |

The status of the new results is provisional.

- *Partly known after reading Hara & Kokubu 2026:* the hyperbolic route of Sec. VI C (technique known; continuous-$\phi$ and given-decoder form not there), and the qualitative persistence of an attractor under $C^0$-small decoder error, part of Secs. VI A-B (discrete, special decoder, no rate).
- *Known:* Proposition 1 in substance; the finite-time bound; the linear triangular form and assignability; linear $QB=0$; the restriction for linear reservoir with chaos; bubbling.
- *Apparently new, as far as read:* Proposition 2 as a theorem; nonlinear time-varying $QA$ and the moving-kernel term; the time-varying factorization and restricted small gain; the quotient operator $Q_{\mathcal E}J$ and the smoothness-free sum rule; the loop identity; the chaotic no-go; the quantitative tube theorem for a given oblique decoder (rate $\sigma$, width $O(\delta/\sigma)$, no fiber-norm condition) with source-coordinate forecast bound; the Lemma of Sec. VII A on hypothesis (H); the moment tail bound. A search for zero-dynamics treatments of RC found none, which is absence of evidence only.
- *Elementary given the framework:* the sum rule, the loop identity and the chaotic family. These are easy and could appear elsewhere in other notation.

### A. Hara & Kokubu 2026 against these notes

**What it proves.** The setting is $f$ on a closed manifold $M$, an attractor $\Lambda$ and a strongly fiber-contracting reservoir map $F$ ($\kappa\ll1$), so that the $C^1$ section theorem gives a $C^1$ invariant section $s$, generically an embedding (Thm. 2.15). The ideal decoder is $\hat\gamma=\gamma\circ\pi$, with $\pi$ a $C^1$ tubular projection on $s(M)$ (Thm. 2.24). Then $s(\Lambda)$ is an attractor of the ideal autonomous reservoir. Regression gives $W$ with small $L^2$ error, hence $C^0$ (Thm. 3.8, Cor. 3.11). Under hypothesis (H), $C^0(U)$ closeness of $W$ to the ideal decoder on a trapping region $U$, the closed loop has an attractor in $U$, weakly semiconjugate to $f$ (Thm. 5.1). Under (H'), $C^1$ closeness, and $f$ $C^1$ structurally stable, it is conjugate (Thm. 5.4). They name Lorenz and logistic maps as outside these hypotheses, and when (H') holds as open.

**The hyperbolic-set result (Sec. VI C) is partly there, and its status stays [SKETCH].** Theirs uses structural stability or shadowing plus expansivity, with $\phi$ smooth by construction, $\kappa\ll1$, and stability built into the decoder extension. Ours has flows, $\phi$ merely continuous, an *arbitrary given* exact decoder, and quotient contraction of $J$ as the hypothesis, with the hyperbolicity of $\mathcal M$ in $\mathbb R^n$ deduced from $J$ rather than from fiber contraction. Continuous $\phi$, non-normal kernels and transverse exponents are not in theirs. Theirs has, and ours does not, the genericity of the embedding, the learning-phase result, weak semiconjugacy under $C^0$ closeness only, and discrete time. So the technique is known and should be credited, whereas the hyperbolic-set statement for a continuous $\phi$ and a given decoder appears new but is still only a sketch.

**The tube theorem (Sec. VI A) is partly there qualitatively, and the quantitative form is apparently new. Its status stays [PROVED].** Their Claim 5.3 is the discrete qualitative core of upper semicontinuity: $C^0$ closeness preserves a trapping region, so an attractor stays in $U$. It needs no source hyperbolicity either (their T2 and T3 serve the semiconjugacy). The difference is that theirs has an epsilon-delta, no rate, and a decoder with normal fibers, where contraction is automatic. Ours has rate $\sigma$, width $O(\delta/\sigma)$, a given oblique decoder, smooth $\phi$, no bound on the Euclidean fiber norm, and the source-coordinate forecast bound. Theorem 4 (converse Lyapunov) needs no smooth $s$, also unlike theirs.

**Why their stability is automatic, and how these notes generalize it [PROVED].** On a decoder with $\hat\gamma(r)=\hat\gamma(\pi r)$, $\tilde F(r)-\tilde F(\pi r)$ sees only the fiber map. So $\kappa<1$ and $\pi$ the nearest-point projection give $\operatorname{dist}(\tilde Fr,s(M))\le\kappa\operatorname{dist}(r,s(M))$. In our notation this is $QA$ with $Q$ orthogonal, the energy bound of Sec. V E with $D\zeta=0$. For a retraction along oblique fibers, $|r-\pi r|\le\|Q\|\operatorname{dist}(r,s(M))$, so the one-step condition becomes **$\kappa\|Q\|<1$**, the discrete form of $\lambda_\perp\le-\kappa+c\|FN^\top A|_{\ker}\|$. The extension is a design choice in their theorem, as Lu et al. also stress. A trained $W$ has its own fixed kernel, and for curved $s(M)$ a constant kernel cannot be normal everywhere.

**Lemma (neighbourhood control) [PROVED]: hypothesis (H) is a hidden small gain.** The closeness used in Claim 5.3 is $L_s\sup_U|W-\phi\hat\gamma|\le(1-\kappa)\rho/2$ for a tube of radius $\rho$. For $|\eta|=\rho$ normal at $\pi r$, $\hat\gamma$ is unchanged, so $W\eta=(W-g)(r)-(W-g)(\pi r)$, hence
$$L_s\|W\text{ on the normal space}\|\le1-\kappa.$$
So the sufficient closeness in (H) requires the naive loop-gain bound on all normal directions, a *necessary consequence of that margin*, and not of the conclusion. Also, for a linear $W$ and $C^2$ $g$ with Lipschitz derivative constant $L$ on a ball of radius $\rho$: $\|W-Dg(x)\|\le2\sup|W-g|/\rho+L\rho/2$, so $C^0$ closeness on a fixed open tube gives $C^1$ closeness at scale $\rho$. This is why the tube width matters.

We checked a flow analogue, $L_s\|N\text{ on normal}\|$ against $|\mu_2(A)|$, with $n=200$, $\gamma=20$, $\rho=0.5$, in rate-condition runs with finite $F$, the most contracting setting tried. On Rössler $L_s\|N_n\|=129$ to $283$ against $|\mu_2|=8.0$ to $9.3$; on Lorenz $648$ and $1131$ against $11.6$ and $11.7$. So it fails by a factor of 16 to 100, and $N$ is almost entirely normal ($\|N_n\|$ differs from $\|N\|$ by under 1%). Yet many runs in this setting are transversely stable. Therefore **the margin behind (H) is far stronger than transverse stability on these reservoirs**: it is sufficient and does not describe them. These are finite $n$, not their large-$N$, $\kappa\ll1$ regime, and the flow form is our analogue and not their statement. Related numbers: the median of $|N^\top A\text{ on }\ker|/\kappa$ over the scans is $39$ to $1292$, with minimum $8.8$.

**Comparison with $\lambda_\perp$.** (H') implies a transverse block near the one for the ideal decoder, so $\lambda_\perp<0$ is a necessary consequence of it in their regime. Hence every unstable run fails (H'), and the data of Error 2 ($N^\top F-I$ of order $0.5$ to $9$ on the stable direction) mean that (H') fails on those directions even when $\lambda_\perp<0$, for any extension whose tangent part reproduces $\phi^{-1}$ on $\mathcal M$. This speaks to their open question about (H'): with a linear $W$ and $\hat\gamma=\gamma\circ\pi$, $W$ would have to approximate $Dg(x)$ at all $x$, which forces $Dg$ nearly constant, i.e. a nearly flat representation. Another extension of $\gamma$ is therefore needed (e.g. $\psi_0$ of Sec. IV, as in Thm. 5.4 they are free to choose), and then the attractor property no longer follows from Thm. 2.24(4): it is the transverse stability condition. (H) ($C^0$ only) does not imply $\lambda_\perp<0$ in general (Theorem 4 tolerates $C^0$-small rough perturbations). For a linear $W$, though, the numbers above and 0 of 66 unstable scan runs staying on the source attractor suggest that (H) with small $U$ fails whenever $\lambda_\perp>0$ **[CONJECTURE]**.

**Weak semiconjugacy allows collapse.** $h$ need not be onto, so $\Gamma_W$ may be, for example, a stable fixed point or cycle. Thm. 5.1 thus does not exclude the tangential failure of Sec. VI D.

**Issues in their paper. These are our reading, unreviewed: verify before citing, and consider telling the authors.**

1. *Claim 2.25 proof (minor).* "Lip($\pi$) becomes arbitrarily small with the diameter of $U$" cannot hold, since a projection has Lipschitz constant at least one, and $\epsilon'$ is limited by $\kappa$, not by $U$. The conclusion is still true for $\kappa<1$, by the one-line distance argument above.
2. *(T1) with (T2) (significant).* Positive expansivity on $\Lambda$ is used in Lemma 4.17 and Thm. 4.19. With $f$ a diffeomorphism and $f(\Lambda)=\Lambda$, $f$ on $\Lambda$ is a positively expansive homeomorphism of a compact metric space, so $\Lambda$ is finite (Schwartzman; Richeson & Wiseman 2004; Coven & Keane 2006). The paper's statement that Anosov diffeomorphisms satisfy (T1)-(T4) conflicts with its Definition 4.12: two points on a stable leaf stay close for all $j\ge0$. So Thm. 5.1 as written applies only to finite attractors. A repair **[SKETCH]** is to use two-sided expansivity and bi-infinite tracing as in Walters, for $G$ a homeomorphism on $\Gamma_G$. Tanh reservoirs are injective when $A+CW$ is invertible, so the conclusion likely survives in that case. Thm. 5.4 does not use T2 or T3 and is not affected.
3. *Uniformity in $\|W\|$ (significant).* Three steps need a bound on $\|W\|$ that is not stated: Prop. 3.5, where the error is $c\kappa$-type with $c$ containing $\|W^\dagger\|$, chosen after $\kappa$; Prop. 3.9, whose $\delta$ depends on $C=\|D\psi\|$, while Cor. 3.11 applies it to a family $\psi=W_{T,\Omega}s-\phi$; and the extension from $C^0(\Gamma)$ to $C^0(U)$ "because continuous", which needs $\|W\|\rho$ small. As $W_{T,\Omega}$ depends on $N$ and $T$, the Remark that (H) holds with high probability seems to need $\|W\|$ control, i.e. $\kappa$ and $U$ chosen after $W$. That is exactly the product appearing in the Lemma above, and it is the quantity the steering test of Sec. V F moves while the data error stays flat. We did not find a counterexample to their probabilistic statement. This is a gap, not a refutation.

## VIII. Conclusions

The state of each item is the following.

| Item | Status |
|---|---|
| Audit | Done. Props. 1, 2, 4 and the spectrum claim hold. Three errors. Open: tempered version of Prop. 2 |
| General decoder | **[PROVED]** (Sec. IV), except straightening **[SKETCH]** |
| Criterion, linear | **[PROVED]**, checked; spectral content known |
| Criterion, smooth time-varying | **[PROVED]**, checked in family (F). Not tested on tanh reservoirs: the required $F$ has $N^\top F\ne I$ there |
| Criterion, non-differentiable | Operator and sum rule **[PROVED]**. A useful sharp gain: not obtained |
| Closed form | Does not exist in the requested variables **[PROVED]** |
| Smooth, uniform transverse | **[PROVED]** (tube), with $C^2$ needed only of a nearby reference; run counts corrected to upper bounds |
| Continuous $\phi$, general | **[PROVED]** conditional on exponential attraction and Lipschitz $\phi^{-1}$. Getting attraction: **[SKETCH]** for hyperbolic sources, **[CONJECTURE]** for Lorenz, open for Rössler |
| Non-uniform | $O(e)$ supremum bound **[FALSE]** in general; moment bound **[PROVED]** at linear level; nonlinear version open |
| Literature | Done, including Hara & Kokubu 2026 (Sec. VII A); other partial readings as noted |

Is any of this a headline for a letter? We believe not. The strongest statement is structural: transverse stability is the zero dynamics of the reservoir, and neither the CLEs nor the reconstruction error constrain it, also for chaotic sources. Part of this is now out for linear systems, the proofs are short, and no sharp predictive law holds on real reservoirs: the certified gains need a smooth $F$, uniform contraction fails on Lorenz, and failures of stable runs are heterogeneous. This fits a long-format paper.
