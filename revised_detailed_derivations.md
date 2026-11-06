# Detailed Derivations and Reproducibility Supplement

This supplement develops the mechanical model, regulator and estimator equations, filter-aware gain redesign, timestamp-aware prediction, exact fractional-delay loop and statistical procedure used in the accompanying article. Classical mechanical and quadratic-control notation follows [1]. All displayed equations are editable Word equations. The supplied numerical data retain the declared development/held-out separation.

## 1 Coordinates energies and equations of motion

Let cart position be x and pole angle from upward vertical be θ. The pole COM is (X,Y) = (x + l sinθ, l cosθ). Differentiation gives Ẋ = v + lω cosθ and Ẏ = −lω sinθ. Squaring and adding eliminates the sine/cosine square terms:

[Editable equation 1: coordinates_x]

[Editable equation 2: coordinates_y]

[Editable equation 3: velocity]

[Editable equation 4: kinetic]

[Editable equation 5: potential]

[Editable equation 6: inertia_point]

[Editable equation 7: inertia_rod]

The generalized forces are Qx = u + fpush − bv and Qθ = 0. Applying d/dt(∂T/∂q̇) − ∂T/∂q + ∂V/∂q = Q yields (M+m)ẍ + ml cosθ θ̈ − ml sinθ ω² = u + fpush − bv and ml cosθ ẍ + Jθ̈ = mgl sinθ. The cross terms in the θ equation cancel exactly. The upright equilibrium is a potential-energy maximum, so the linearized angular gravitational coefficient is positive.

[Editable equation 8: mass]

[Editable equation 9: determinant]

[Editable equation 10: accel_x]

[Editable equation 11: accel_theta]

[Editable equation 12: energy]

In the acceleration equations, replace u by u + fpush when applying the external disturbance. With J = (1+ρ)ml², Δ = ml²[M + (M+m)ρ + m sin²θ] > 0 for M,m,l > 0 and ρ ≥ 0. The energy derivative is Ė = (u + fpush)v − bv². This balance checks the sign of gravity, friction and input coupling. The rod shares l with the point mass and has physical length 2l; equating physical pole length would define a different comparison.

## 2 Upright linearization and discretization

[Editable equation 13: linear_A]

[Editable equation 14: linear_B]

Linearization is about z = 0, u = 0. The input sign follows θ positive toward positive x. The controller convention u = −Kz therefore gives negative entries in K for these coordinates. Independent central differences of the nonlinear RHS check both Jacobians. Exact zero-order-hold discretization follows from the block exponential exp([[A,B],[0,0]]Ts); the upper blocks are F and G.

[Editable equation 15: discrete]

## Point nominal plant

## Rod nominal plant

Plant integration uses RK4 at 1 ms, whereas F and G are exact linear sample transitions at Ts = 10 ms. Step-halving verification compares the same held-control schedule, including push boundaries, at 1 ms and 0.5 ms. The integration tolerance is fixed before examining outcomes.

## 3 Continuous and discrete quadratic regulators

The nominal continuous cost is ∫(zᵀQz + Ru²)dt. Bryson limits 1 m, 1 m/s, 0.2 rad, 1 rad/s and 10 N give Q = diag(1,1,25,1), R = 0.01. Completing the Hamilton–Jacobi quadratic identity gives the stabilizing CARE and u = −R⁻¹BᵀPz.

[Editable equation 20: care]

[Editable equation 21: gain]

[Editable equation 22: law]

[Editable equation 23: dare]

[Editable equation 24: kd]

The discrete stage cost is Ts(zᵀQz + Ru²). The displayed DARE follows by substituting znext = Fz + Gu into the Bellman quadratic and minimizing with respect to u. An exact integral cost would introduce different weights and a state-input cross term; this study consistently uses the declared sampled-stage cost.

## Point regulator gains

## Rod regulator gains

## 4 Finite differences and local filter aware gain redesign

[Editable equation 29: fd]

[Editable equation 30: memory]

[Editable equation 31: velocity]

[Editable equation 32: ky]

[Editable equation 33: kh]

Here h stores the exponentially filtered previous measurement and h0 = y0; Kp and Kv select the position and velocity columns from K. Then u = −Ky y − Kh h. In the augmented state s = [z;h], Ag = [[F,0],[(1−α)C,αI]], Bg = [G;0], Cy = diag(C,I), Ko = [Ky,Kh] and Acl = Ag − BgKoCy. This realization includes the derivative filter in the loop. A fixed PD cascade also gives four gains K = −[ka kx, ka kv, ka, kw], so its linear implementation is in this same family.

Set Qg = diag(QTs,0), Qcl = Qg + (KoCy)ᵀR(KoCy)Ts and Bn = [−GKy;(1−α)I]. For a Schur-stable candidate, P sums the initial transient quadratic cost, and S is the stationary state covariance driven by independent measurement noise:

[Editable equation 34: lyapP]

[Editable equation 35: lyapS]

[Editable equation 36: h2cost]

N = 1000 samples represents ten seconds. The final term accounts for direct measurement-noise feedthrough to command effort. The initial augmented state is s0 = [0,0,0.1,0,0,0.1]ᵀ. Gain signs are preserved using K = Kbase diag(exp ℓi), with ℓi ∈ [−2.3,2.3]. A fixed-seed set of 120 random starts plus zero is ranked, and the best three seed Powell local searches. Unstable candidates receive a spectral-radius penalty and cannot be selected as stable designs. The surrogate omits saturation, delay, parameter errors and the unknown push; its purpose is a transparent filter-aware baseline rather than a global robust optimum.

All nine α values are evaluated with fixed K and with this redesign, where stable. Nonlinear development tasks select α afterward without using held-out outcomes. The JSON gain audit reports coefficients, objective values, local-search status and stability. The following tables give the final primary configurations; repeated settings retain separate diagnostic labels.

## Point primary gains

## Rod primary gains

Fig. S1. Full development α sweep: mean survival, terminal dwell and active-time RMS across the five declared tasks, for fixed and filter-aware redesigned gains. Each setting uses 200 paired trials per task.

## 5 Covariance units continuous observation and sampled filtering

Per-sample covariance Rm has units of squared measurement, whereas continuous white-noise spectral density Vc has units squared measurement times seconds. Averaging a white-noise measurement over Ts gives covariance Vc/Ts; matching this to Rm gives the stated conversion. Independent point samples do not define a finite continuous white-noise variance without such a bandwidth/averaging convention, so this is an explicit equivalent-noise convention rather than an assertion of exact continuous/discrete equivalence.

[Editable equation 37: units]

[Editable equation 38: dualcare]

[Editable equation 39: observergain]

[Editable equation 40: ratio]

The continuous dual CARE is AΣ + ΣAᵀ − ΣCᵀV⁻¹CΣ + σW = 0. Rescaling both σW and V by the same positive constant rescales Σ but leaves H invariant. Thus correcting V from Rm to RmTs is equivalent at Ts = 0.01 s to multiplying W by 100 in the legacy design. The numerical unit-ratio identity is checked independently for both plants. At extreme ratios, covariance and time rescaling condition the CARE solve; accepted solutions must have relative residual below 10⁻⁶ and stable observer poles.

For a causal continuous observer, the exact held transition is generated by the upper blocks of exp([[A−HC,B,H],[0,0,0],[0,0,0]]Ts). Its propagation over [tk−1,tk) uses u at k−1 and y at k−1, then u at k = −Kẑk. The legacy-current-sample diagnostic uses y at k in that same preceding-interval propagation. This alternative has a different sampled transfer and cannot be called a causal continuous implementation. The old-unit and corrected-unit legacy diagnostics share the exact same update, isolating units alone.

[Editable equation 41: covariance]

[Editable equation 42: kfgain]

[Editable equation 43: posterior]

[Editable equation 44: kfprior]

W = diag(10⁻⁶,0.04,10⁻⁶,0.04) is a continuous design covariance; Qd is its exact integral [2]. Rm = diag(0.005²,0.002²) is used directly in the discrete innovation covariance. Prediction uses the actual clipped command. The steady-state prior covariance is computed from the dual DARE; the gain updates the current prior with yk. At zero delay, the post-update compensator has Ac = (I−LC)(F−GKd) and transfer Kd(I−Ac z⁻¹)⁻¹L. Discrete and continuous regulator gains are not silently interchanged.

Each observer family is swept over σ = 10ʲ, j = −6,…,8. Because plant process noise is not drawn from W, neither observer is asserted statistically optimal for the nonlinear uncertain plant. The sweep is a bandwidth calibration study. Survival maxima are task dependent; dwell and effort need not peak at the same ratio. A finite tested maximum is distinguished from an identified unique continuous optimum. At σ = 10⁸, the discrete gain change from the preceding decade is below 10⁻⁴ in relative norm, documenting convergence toward the high-bandwidth limit.

Fig. S2. Full covariance-ratio trade-off: 60 ms/5 N survival and zero-delay/5 N terminal dwell and active RMS, across both models and both corrected observer families. The full tested multiplier range extends fourteen orders of magnitude.

## Point base estimator

## Rod base estimator

## 6 Timestamp aware prediction with held command history

Write τ = qTs + r, 0 ≤ r < Ts, Fs = exp(As), Gs = ∫₀ˢ exp(Aa)B da, and Qs = ∫₀ˢ exp(Aa)σW exp(Aᵀa) da. The incoming packet at tk observes timestamp sk = tk−τ; write s = sk in the forecast below. Stale timestamps remain exactly Ts apart, but their propagation interval may straddle two command holds. From the previous stale posterior to the new stale prior,

[Editable equation 51: staleprior]

The stale covariance propagates with F and Qd. Innovation yk − Cẑs− and gain Ps−Cᵀ(CPs−Cᵀ+Rm)⁻¹ update the stale state. At zero delay, the steady-state gain is used exactly, ensuring equality with the ordinary discrete filter. At nonzero delay, covariance is propagated from the first received timestamp. After that innovation, the present-time mean is

[Editable equation 52: fracforecast]

[Editable equation 53: predict]

The first partial interval lasts r with command u at k−q−1; the remaining q complete intervals use the chronological stored commands. The sum is written backward from the most recent input to avoid an indexing ambiguity. Before any valid packet arrives, the current mean propagates from the common known initial mean. The first stale update occurs at a timestamp between zero and Ts; its transition uses only the initial held command. The predictor never knows the external push, the trial-specific parameter perturbations or future commands.

For an exact linear model with known inputs, no unknown disturbance and consistent initial mean, integrating the stale posterior and command history recovers the current state. Hence deterministic delay disappears from regulation in that ideal limit. With stochastic process noise, prediction uncertainty accumulates during τ; with an unknown push or parameter errors, current-time extrapolation is imperfect. No infinite nonlinear delay tolerance is claimed. This predictor is a standard baseline from delayed-measurement filtering [3], not an algorithmic contribution.

## 7 Exact sampled measurement delay and local stability

For a fixed compensator ξnext = Acξ + Bcy and command u = −Ccξ − Dcy, reverse the nominal plant transition over r within the previous held-input segment. With Fr = exp(Ar), the fractional delayed output is

[Editable equation 54: fractionalY]

Here Fr⁻¹ = exp(−Ar); for r = 0 the input correction is zero. The augmented state contains z at k through k−q, commands at k−1 through k−q−1, and controller state ξk. The output expression determines y, then u; the plant advances using F and G, histories shift, and the compensator advances. The resulting finite matrix gives the exact nominal closed-loop spectral radius at that τ.

Zero-delay augmented radii are checked against an independently assembled python-control feedback interconnection. All gain crossovers are computed from state-space frequency responses below Nyquist. The smallest positive φm/ωgc estimates the first pure-delay crossing. Exact fractional-delay radii are evaluated on a 10 ms locator and bisected to 1 ms. The reported linear boundary is the bracket midpoint; half the bracket width is numerical resolution, not statistical uncertainty. Neither method certifies nonlinear survival under saturation or uncertainty.

[Editable equation 55: margin]

## 8 Paired experiments boundary estimation and censoring

Development uses seed 20261121 and 200 trials per each of five tasks. The coarse delay locator uses seed 20261124 and 100 trials per cell. Held-out boundary and fixed reference cells use seed 20261122 and 500 trials per cell. Four independent uniform parameter draws are generated once per trial and shared across all compared cases; at each control instant, a single two-channel measurement-noise draw per trial is likewise shared. This construction is independent of batching and case order, an invariant verified numerically. The pair represents a common realization, not independent observations across delays.

[Editable equation 56: d50]

[Editable equation 57: interpolate]

The held-out bracket is verified before bisection and expanded if necessary, with an administrative search ceiling of 1200 ms. The actual evaluated maxima are 300 ms for point and 600 ms for rod; no reported crossing is right-censored. A ±6 ms local integer grid around the final crossing checks local recrossings; some values were already queried and are reused. Coarse locator and held-out tables retain every evaluated delay. If survival is nonmonotone, the estimand is the first observed downward crossing, and observed upward recrossings are counted rather than forced into a monotone fit. An unobserved narrow dip between coarse locator points cannot be excluded.

Bootstrap seed 20261123 resamples 500 trial identities with replacement, recomputes all evaluated survival means, and interpolates the first crossing; 2,000 resamples yield 2.5th and 97.5th percentiles. Reported bounds round the bootstrap endpoints outward to integer milliseconds and include the observed grid crossing bracket; the unrounded interpolation intervals are also supplied. The intervals condition on the sampled adaptive delay grid and fixed selected design. They do not claim coverage of a repeated adaptive sampling/tuning procedure. A bootstrap realization that never crosses is excluded from finite quantiles and its occurrence is reported through the valid-resample count; a zero-delay or upper-limit censoring status takes precedence over any finite interval.

[Editable equation 58: wilson]

[Editable equation 59: delta]

Pointwise Wilson intervals [4] describe each fixed survival cell. For the 108 declared fixed-cell paired interventions, Δp is the mean within-trial success difference b − a. Positive values favor b. Seed 20261128 provides 2,000 paired bootstrap resamples. Exact McNemar tests use only the improved and worsened discordant pairs [5]; Holm correction is applied across all 108 p-values [6]. Adaptive D50 comparisons are not added to that family after inspecting outcomes. These tests quantify the specified interventions and are not a ranking of all controller theory.

Active RMS averages each trajectory’s squared clipped command over timesteps before its first failure, including the threshold-crossing step; full RMS uses all ten seconds, including the held command until the first control update after failure and zeros thereafter. Reported aggregate RMS is the mean of per-trial RMS values, not the square root of pooled effort. Terminal dwell is a separate binary event and requires survival. The zero-action tail after failure therefore cannot create a favorable active-effort result.

## 9 Full boundary results and verification

## Point held out boundaries

Fig. S3. One paired illustrative point realization at 60 ms/10 N, seed 20261125. Gray shading marks the unknown push and dotted horizontal lines mark failure or actuator limits. Failed states are frozen and commands are zeroed at the next control update. These trajectories illustrate behavior and do not estimate ensemble survival.

## Rod held out boundaries

Fig. S4. One paired illustrative rod realization at 60 ms/10 N, seed 20261125. Gray shading marks the unknown push and dotted horizontal lines mark failure or actuator limits. Failed states are frozen and commands are zeroed at the next control update. These trajectories illustrate behavior and do not estimate ensemble survival.

The revision validation report contains 158 recorded checks and diagnostics. It includes nonlinear Jacobians, integration step halving, covariance-unit gain identity, predictor equality at zero delay, exact known-model fractional-delay recovery, random held-command convolution, nominal closed-loop radii, case-order/batch invariance and interpolation. Riccati residual and pole checks are enforced for every design. Margin checks independently compare sampled interconnections. Video checks read the first and final frames and verify 240 frames at 24 fps.

The boundary campaign evaluates 596,000 nonlinear trajectories, including its independent locators. Development adds 96,000 trajectories across 18 derivative-filter configurations and 30 covariance settings per plant, five tasks and 200 trials. These counts exclude implementation checks and the 168 single-case video trajectories. The trial census and all queried cells are supplied to make the accounting auditable.

## Randomized push phase sensitivity

The phase check uses 500 matched trials per regime and 269 model-controller-push-delay cells. For each original first-crossing bracket [a,b], the queried delays are max(0,a−3), a, b, b+3 and 60 ms, with duplicates removed. Phase seed 20261106 draws independent uniform integers 0,…,9; the same phase draw is shared across configurations and models for each trial. A pulse starts at 2000 + phase integration steps and ends 100 steps later. Plant and measurement seed 20261122 is unchanged. All 269 fixed-phase reruns reproduce the archived binary survival outcomes exactly; the phase extension evaluates 269,000 trajectories.

Seed 20261107 supplies 2,000 trial-paired resamples for pointwise 95% intervals of randomized-minus-fixed survival. These exploratory intervals are not multiplicity-adjusted. Seven evaluated cells change sides of 50%; the largest observed absolute differences are 2.8 points at 60 ms and 5.4 points at local anchors. No new phase-averaged D50, global phase robustness or arbitrary-time disturbance tolerance is inferred. Raw trial outcomes, assignments and aggregate tables accompany this supplement.

Fig. S5. Randomized-minus-fixed push-phase sensitivity across all fourteen configurations, both push magnitudes and the queried local-crossing/60 ms cells. Each point compares 500 trial-paired realizations per regime; the diagonal is equality. The push starts at 2 s plus an independent uniform integer 0,…,9 ms and lasts 100 ms. This local sensitivity check does not re-estimate a full phase-averaged D50 curve.

## 10 Scope and reproducibility

Run development, boundary estimation, margins, audits, figures and videos with the supplied sources and recorded seeds. The document formatter uses editable Office Math and the supplied mechanical MathML. Regenerating Word/PDF on this host uses Microsoft Word 16; scientific computation does not require Word. No hardware data, identified sensor spectrum or verified journal acceptance is implied. Generalization requires additional plants, physical experiments, delay jitter/loss and broader tuning objectives.

## REFERENCES

[1] K. J. Åström and R. M. Murray, Feedback Systems: An Introduction for Scientists and Engineers. Princeton University Press, 2008. https://authors.library.caltech.edu/records/yzs24-xsx88

[2] C. F. Van Loan, “Computing integrals involving the matrix exponential,” IEEE Trans. Autom. Control, vol. 23, no. 3, pp. 395–404, 1978, doi: 10.1109/TAC.1978.1101743.

[3] T. D. Larsen, N. A. Andersen, O. Ravn, and N. K. Poulsen, “Incorporation of time delayed measurements in a discrete-time Kalman filter,” Proc. 37th IEEE Conf. Decision and Control, vol. 4, pp. 3972–3977, 1998, doi: 10.1109/CDC.1998.761918.

[4] E. B. Wilson, “Probable inference, the law of succession, and statistical inference,” J. Amer. Stat. Assoc., vol. 22, no. 158, pp. 209–212, 1927, doi: 10.1080/01621459.1927.10502953.

[5] Q. McNemar, “Note on the sampling error of the difference between correlated proportions or percentages,” Psychometrika, vol. 12, no. 2, pp. 153–157, 1947. https://pubmed.ncbi.nlm.nih.gov/20254758/

[6] S. Holm, “A simple sequentially rejective multiple test procedure,” Scandinavian J. Stat., vol. 6, no. 2, pp. 65–70, 1979. https://sci2s.ugr.es/keel/pdf/specific/articulo/0052_001.pdf