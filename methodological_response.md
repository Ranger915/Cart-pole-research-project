# Response to Methodological Review

The four criticisms identify confounding in the previous comparison. The revised paper withdraws the architecture-only survival headline and the observer-implementation attribution. The changes below are supported by new computations, not a reinterpretation of the old grid.

## 1 Baseline tuning and covariance units

Accepted. The legacy continuous observer used per-sample variance as a continuous spectral density. The corrected equivalent density is Vc = RmTs. Its gain equals that from the old density and 100 times W, verified to relative error below 3 × 10⁻¹² in both models. The earlier “49.4-point observer effect” is not retained as an implementation finding. A unit-only pair preserves the old update; a second diagnostic makes the held-measurement propagation causal.

[Editable equation 1: units]

A nine-value α sweep now includes α = 0 and α = 0.8, both with fixed LQR gains and with local filter-aware gain redesign. Selection uses five predeclared development tasks, with 200 paired trials each. The selected α values are 0.0 and 0.1 with fixed gains, and 0.4 and 0.6 after redesign. Thus the former single-constant comparison is explicitly tested rather than defended.

Both corrected continuous and discrete observer families now sweep σ = 10⁻⁶ to 10⁸. The range extends well past the previous endpoint at 10. The paper reports the full survival/dwell/effort curves and the development selection rule. It calls selected values the best tested settings, not continuous global optima; high-end plateaus and the discrete gain’s limiting convergence are documented. Quiet regulation and force noise remain visible alongside delayed survival.

## 2 Delay aware estimator baseline

Accepted. The original filter is renamed and interpreted as a delay-unaware robustness baseline. A known-delay timestamp-aware filter now updates at the stale measurement time and predicts to the control time with recorded clipped commands. Exact partial-input intervals handle noninteger sample delays. It does not receive the external push or true uncertain parameters. Base and development-selected covariance versions are both included.

The predictor equals the ordinary discrete filter exactly at zero delay and recovers the no-delay linear trajectory to below 10⁻⁸ for tested delays, including 1, 9, 37 and 115 ms. Random command-history convolution is checked independently. The paper cites established delayed-measurement Kalman filtering [1] and makes no novelty claim for the predictor.

## 3 Validate margins against the actual loop and survival

Accepted. For point PD and legacy cLQG, PM/ωgc predicts 34.9 ms and 56.2 ms despite similar phase margins. Their exact fractional-delay lifted boundaries are 34.5 and 56.5 ms. Crossover frequency resolves the missing part of that linear comparison.

The new margin figure compares both linear predictions directly with the held-out nonlinear D50 values for both push sizes and both models. It does not equate local instability with finite-horizon survival. A fixed-compensator PM division is not applied to a delay-dependent predictor. The abstract no longer claims margins alone explain nonlinear ranking. Doyle’s 1978 result is background rather than a proposed contribution.

## 4 Replace the cliff cell with survival boundaries

Accepted. Each primary configuration now has a separate 5 N and 10 N D50 estimate for each model. A 100-trial locator seed establishes candidate brackets; 500 held-out paired trials verify them and bisect to 1 ms. Local grids check recrossings, and 2,000 trial-paired resamples give pointwise intervals conditional on the evaluated grid. The paper states the finite horizon, interpolation, censoring and interval limitations explicitly.

## 5 Further manuscript checks and reproducibility

Equation (1) now includes the full coupled force balance and its mass matrix. At σ = 1, the development dKF cells are 192/200 (96.0%) for point and 200/200 (100%) for rod; the held-out cells are 485/500 (97.0%) and 499/500 (99.8%). The figure now marks the base points and identifies both seeds and sample sizes. The nominal discrete filter designs agree numerically across those comparisons.

The abstract now states first observed crossings. The initial 300 ms locator is distinguished from bracket expansion: actual tested maxima are 300 ms for point and 600 ms for rod; 1200 ms is an unused administrative ceiling. The tuning-near-boundary and predictor-reuse caveats are stated plainly beside Table I. The title now says Delay-Aware State Prediction, the gap is framed as a scoped attribution question, and each document numbers references by first appearance.

The randomized push-phase extension adds 269,000 trajectories across 269 paired cells, with exact recovery of all fixed-phase survival outcomes. Supplement S1 reports its limits and pointwise paired intervals. The supplement is attached separately and in a combined review PDF; version 1.0.0 of the repository and archive provides the reproduction files. Original material is distributed with all rights reserved, as requested.

[Project repository](https://github.com/Ranger915/Cart-pole-research-project)

[Archive DOI 10.5281/zenodo.24017779](https://doi.org/10.5281/zenodo.24017779)

## Revised claim and remaining scope

The revised contribution is an empirical calibration and boundary-attribution study. It does not establish a new controller, infer a universal architecture ranking, or equate ten-second survival with stabilization. Simulation-only scope, local gain redesign, known constant delay, design rather than identified process covariance, and conditional boundary uncertainty remain explicit limitations. The accompanying article, detailed derivations, result tables, source and videos supersede the earlier headline interpretation.

[1] T. D. Larsen, N. A. Andersen, O. Ravn, and N. K. Poulsen, “Incorporation of time delayed measurements in a discrete-time Kalman filter,” Proc. 37th IEEE Conf. Decision and Control, vol. 4, pp. 3972–3977, 1998, doi: 10.1109/CDC.1998.761918.