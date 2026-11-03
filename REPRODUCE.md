# Reproducing the paper

*Learn to Synchronize, Fail to Predict: What Training Cannot See in Surrogates of Chaotic Systems* (Pietro Verzelli).

**Archive of the result files: TBD (Zenodo).** Until it exists, the figures that need scan results can only be made by
rerunning the scans (thousands of runs, many CPU-hours; `WORKERS` sets the number of processes).

## Quick path: figures from archived results

```
git clone https://github.com/verzep/reservoir_sync && cd reservoir_sync
uv sync --locked && uv run pytest
# download and unpack the archive into results/ (link above), then
bash experiments/paper_figures.sh results figures
```

`results/` must contain `night_2026-10-20/{lorenz,rossler}_long.jsonl` and `source_scan/` (see the table). The five
figures that need no results can be made alone with
`uv run python experiments/figures_paper.py --out figures --only counterexample overview opening family bubbling`.

All commands run from the repository root; `python` means `uv run --locked python`.

## Figures

Seeds: in a scan, `seed` sets both the random reservoir and the source's initial condition (`settle_source`); the
second reservoir copy of the synchronization check uses `seed + 1000`; Lyapunov QR starts and end-state sampling use
fixed seed 0.

| Paper figure (file) | Function | Input | Command that produced the input | Seeds |
|---|---|---|---|---|
| Fig. `fig:overview` (`fig_overview.pdf`) | `figures_paper.py: fig_overview` | none (Rössler, computed in the figure) | – | reservoirs 1 and 21 |
| Fig. `fig:opening` (`fig_opening.pdf`) | `figures_paper.py: fig_opening` | none; recomputes the two runs and their λ⊥ over 2000 time units (a few minutes) | – (the two runs were picked from `rossler_long.jsonl`: γ = 5, ρ = 0.5, σ = 0.05) | 1 and 21 |
| Fig. `fig:counterexample` (`fig_counterexample.pdf`) | `figures_paper.py: fig_counterexample` | none (2-d linear example) | – | none |
| Fig. `fig:family` (`fig_family.pdf`) | `figures_paper.py: fig_family` | none (exact Lorenz family) | – | Lorenz orbit seed 0 |
| Fig. `fig:bubbling` (`fig_bubbling.pdf`) | `figures_paper.py: fig_bubbling` | none (same family, T = 8000) | – | seed 0 |
| Fig. `fig:predictors` (`fig_predictors.pdf`) | `figures_paper.py: fig_predictors` | `night_2026-10-20/lorenz_long.jsonl`, `rossler_long.jsonl` | `bash experiments/scans/night_long.sh results/night_2026-10-20` (810 runs per source; recovered from `batch_long.sh` on tethys, where Rössler ran at `fc4fcdf` and Lorenz at `e3c3e7b`, both on main). Rerun check (current code, uv.lock, uranus): 3 settings × seeds 0, 21 per source reproduce λ⊥, valid time, training error and the closed-loop exponents bit for bit, although the originals ran on tethys with NumPy 2.5.4 | 0–29 per setting |
| Fig. `fig:sources` (`fig_sources.pdf`) | `figures_paper.py: fig_sources` | `source_scan/sources_lambda.csv`, `source_scan/sources_lambdaoff.csv` | `bash experiments/scans/run_source_scan.sh results/source_scan` (calibration, `scan_lambda.jsonl`), `bash experiments/scans/run_source_scan_controls.sh results/source_scan` (`scan_lambdaoff.jsonl`), then `python experiments/analyze_sources.py results/source_scan --arms lambda lambdaoff` | 0–9 per setting |
| Fig. `fig:gap` (`fig_gap.pdf`) | `figures_paper.py: fig_gap` | as `fig:predictors` | as `fig:predictors` | 0–29 |
| Fig. `fig:tangent_survival` (`fig_tangent_survival.pdf`) | `figures_paper.py: fig_tangent_survival` | as `fig:predictors` | as `fig:predictors` | 0–29 |
| Fig. `fig:failure_end_state` (`fig_failure_end_state.pdf`) | `figure_night.py` (`--out …/fig_failure_end_state.pdf`) | as `fig:predictors` | as `fig:predictors` | 0–29 |

## Numbers in the text that come from analyses, not figures

| Where (paper) | Number(s) | Script / command | Input |
|---|---|---|---|
| Sec. 3, opening example | training errors 5.75e-5 / 5.76e-5, largest CLE −2.97 / −2.98, λ⊥ −1.00 / +0.25, median valid times 4.8 / 0.5 | all four recomputed and printed by `fig_opening` (`figures_paper.opening_diagnostics`, the same computation as `experiment.run`, checked in `tests/test_provenance.py`); originally the records of `rossler_long.jsonl` with γ = 5, ρ = 0.5, σ = 0.05, seeds 1 and 21 | none |
| Sec. 4, exact family | closed-loop spectrum 0.906, −0.001, −0.259, −14.57; ⟨E + h'⟩ = −0.258; zero at a₀ ≈ 4; parameters k = 5, D₃ = 0.3 (defaults of `Fam`); E > 0 example E = 1, D₃ = 6, a₀ = 0.5: CLEs −0.27, −3.73, −5, −5, ⟨E + h'⟩ = 1.13, spectrum 1.10, 0.89, 0.02, −14.56 over T = 400 (`spectrum_check(Fam(E=1, amp=0.5, D=6), T=400)`) | ⟨E + h'⟩ and the zero are printed by `fig_family`; the spectrum: `experiments/theory/check_lorenz.py` | none |
| Sec. 4, bubbling table | median and sup of \|χ\| for ε = 1e-5 … 1e-2, T = 8000 | median and sup printed by `fig_bubbling`; the 99.9% column (and 50/90/99/99.99%): `cd experiments/theory && PYTHONPATH=../../src python check_gain2.py` (its `free_chi` runs at E = −1, a₀ = 3, seed 0; recomputed 2026-11-03: 1.34e-2, 0.171, 84.5, 86.5) | none |
| Sec. 4, end of bubbling | 108 runs per source: Lorenz 101 stable / 25 failed, Rössler 49 / 12 | `cd experiments/theory && PYTHONPATH=../../src python check_tanh.py lorenz 4 tanh_lorenz.jsonl` (and `rossler`; optional 4th argument: workers), then `python analyze_tanh.py --threshold -0.05 tanh_lorenz.jsonl tanh_rossler.jsonl`. Rerun 2026-11-03 on tethys: same counts at thresholds 0 and −0.05 (no λ⊥ in [−0.05, 0)) | its own runs (27 settings × seeds 0–3) |
| Sec. 5.1 | within-γ ρ(λ⊥, valid time) −0.94 / −0.81; training error −0.02 / −0.86; partial correlations −0.56, −0.25, −0.58; 513 / 810 and 49 / 810 unstable | `python experiments/analyze_night.py <night>/rossler_long.jsonl --source rossler` (and `lorenz`); the ρ values are also in the `fig_predictors` titles; unstable counts in section 3 | `night_2026-10-20/*_long.jsonl` |
| Sec. 4, restricted gain | gains 0.09 / 0.24 / 0.34 at (E, a₀) = (−3, 0.5), (−1, 0.5), (−0.2, 0.1); 1.13 at (−1, 3) (σ = 0, D₃ = 0.3); M = 0: 1.06, 1.09 | `gain_Q0` in `experiments/theory/check_gain2.py`; the M = 0 values are `gains()` in `check_lorenz.py` at σ = 0 ("weighted gain of R"): 1.062 at (E, a₀) = (−3, 0.5) and 1.085 at (−1, 0.5), D₃ = 0.3, T = 60 (the two cases in its `__main__`) | none |
| Sec. 5.2, 19-system statistics | exponent ratios λ₁/\|λ_min\| 0.013 … 0.58 (column `ratio` of `sources_<arm>.csv`, from `calibration.json`); 5103 = 19 × 270 runs minus the 27 of `sprott_jerk` seed 3, whose source diverges (`results/source_scan/OVERVIEW.md` on uranus); ρ(λ⊥, valid time) −0.49 … −0.91; unstable fractions 0.14 (Aizawa) … 0.91 (Thomas); law tests (ρ = −0.18 [−0.67, 0.37] for the ratio, ≤ 8% variance explained out of sample, training error 0.72 / 0.04 in native time); rate condition 0.42 vs 0.46; offset: lower in 18 of 19, by 0.21 on average, Lorenz 0.03 | `python experiments/analyze_sources.py results/source_scan --arms raw lambda freq lambdaoff` (per-source tables, `laws.csv`, rate-condition table, `paired_lambda_lambdaoff.csv`) | `source_scan/` |
| Sec. 5.2 | pooled unstable fractions by spectral radius (0.24, 0.46, 0.68) and input scale (0.30, 0.43, 0.65) | `python experiments/analyze_sources.py results/source_scan --arms lambda --pooled` (pooled over the 5103 runs; 0.6455 for input scale 0.1; the mean over sources would give 0.64) | `source_scan/scan_lambda.jsonl` |
| Sec. 5.2, bias table | independent random bias 0.20 vs offset 0.25 vs original bias 0.46, lower in all 19 systems; no bias: 0.97 unstable, median λ⊥ −0.15 → +3.5, valid time 2.2 → 0.55, 0.96 among runs with training error < 0.01 | `uv run --locked --with pandas python experiments/bias_arms.py results/source_scan`; inputs from `bash experiments/scans/run_bias.sh` and `run_bias0.sh`. "Lower in all 19" holds for the independent bias; the offset is higher than bias 0.5 for Thomas (0.911 vs 0.907) | `source_scan/scan_bias.jsonl`, `scan_bias0.jsonl`, `scan_lambda.jsonl`, `scan_lambdaoff.jsonl` |
| Sec. 5.2, dose response | unstable fraction 0.97, 0.90, 0.79, 0.66, 0.60, 0.46 for bias 0, 0.01, 0.03, 0.1, 0.2, 0.5; CLE −0.99; readout norm 1.6e3 → 1.2e3; Rössler 0.36, Lorenz 0.03, Thomas ≈ 0.9; slope bound 0.77 b (max \|tanh''\| = 4/(3√3), analytic) | `uv run --locked --with pandas python experiments/bias_dose.py results/source_scan` (readout norm: median `N_norm`, 1626 at bias 0, 1248 at 0.03); input from `bash experiments/scans/run_smallbias.sh` | `source_scan/scan_bias0.jsonl`, `scan_smallbias.jsonl`, `scan_lambda.jsonl`, `scan_bias.jsonl` |
| Sec. 5.3 | λ⊥ > largest CLE in 808 / 810 (Lorenz) and 810 / 810 (Rössler); median gaps +0.70, +2.15 | `analyze_night.py … --sections 7` (counts also in the `fig_gap` titles) | `night_2026-10-20/*_long.jsonl` |
| Sec. 5.4 | rate test passes in 30 / 810 and 163 / 810; among runs failing it, both exponents within 0.05 in 626 / 731 stable and 9 / 49 unstable (Lorenz), 215 / 221 and 374 / 426 (Rössler) | field `rate_test_passes` (`smooth_sync_condition` in the old files) and `lyap_closed_driven` of the long scans; `analyze_night.py … --sections 7`. These counts pick the exponents nearest to λ₁ and to 0 independently; with distinct picks (as `fig_tangent_survival` now draws them) Rössler gives 214 / 221 and 365 / 426, Lorenz is unchanged | `night_2026-10-20/*_long.jsonl` |
| Sec. 5.5 | end states 272 / 513 fixed point, 220 / 513 cycle (Rössler unstable); 163 / 761 (Lorenz stable, fixed point); 52 / 297 and 20 / 297 (Rössler stable) | `analyze_night.py` (section 3) | `night_2026-10-20/*_long.jsonl` |
| Sec. 5.6, Lorenz origin | transverse rate at the Lorenz origin positive in 91 of 101 stable runs of the 108-run set, median \|e\| = 10 | `experiments/theory/check_tanh.py lorenz 4 <out.jsonl>` + `analyze_tanh.py` | its own runs |
| Sec. 5.6, exactness | \|(NᵀF − I)g\|/\|g\| < 5e-4; NᵀF − I 0.49–3.5 (Rössler), 4.3–9.3 (Lorenz) | `experiments/theory/check_defect.py` | its own runs |
| Sec. 5.6, zero-dynamics check | 631 runs passing the rate test; 67 runs within 0.01 (four systems), median difference 0.03, same sign 66 / 67; 0.22 at 0.03–0.1; 380 / 631 beyond 0.1; 74 runs with a negative source exponent on top | `python experiments/zero_dyn_check.py results/source_scan/scan_lambda.jsonl results/source_scan/zero_dyn.jsonl 40`, then `python experiments/zero_dyn_analyze.py results/source_scan/zero_dyn.jsonl` (bins by \|NᵀF − I\|) | `source_scan/scan_lambda.jsonl` |
| Sec. 5.6, free transverse modes | one Rössler reservoir (γ = 5, ρ = 0.9): training error 6.4e-5 → 9e-5, λ⊥ 1.9 → 4.5 … 34.6 | `experiments/theory/check_null.py` (`steer`) | none |

## Caveats

- **Old result files have no provenance.** Records written before this version of `experiment.run` carry no git
  commit, library versions or thread settings, and this cannot be added after the fact. New records have a
  `provenance` field (`git describe --always --dirty`, Python, NumPy, SciPy, `OMP/OPENBLAS/MKL_NUM_THREADS`).
- **Chaotic trajectories are machine dependent.** Free runs and valid times amplify floating-point differences, so
  individual trajectories (and the opening figure's two runs) may differ across machines, CPUs and BLAS builds, or
  with other thread settings; the scripts set the BLAS thread variables to 1. Statistics over runs (fractions,
  correlations, medians) should not change.
- `uv.lock` pins Python 3.12, NumPy 2.5.3, SciPy 1.18.1 and Matplotlib 3.11.2. The paper's figure PDFs were written
  by Matplotlib 3.11.2; which versions produced the older scan files is not recorded.
- The 19-system figure's caption speaks of bootstrap intervals; `analyze_sources.py` computes Wilson score intervals
  (`unstable_lo`, `unstable_hi`).
