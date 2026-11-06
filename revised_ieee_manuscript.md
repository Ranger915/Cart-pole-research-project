# Tuning and Delay-Aware State Prediction in Cart-Pole Survival Boundaries

Abstract—Controller rankings near a delay-induced failure cliff can reflect filter tuning, noise units and stale-data handling as much as feedback architecture. We study point-mass and uniform-rod cart poles with equal mass and centre-of-mass distance. A paired nonlinear benchmark corrects the continuous observer covariance units, sweeps finite-difference filtering with fixed and redesigned gains, and extends process-to-measurement covariance ratios across fourteen orders of magnitude. Tunings are selected on independent development trials. A timestamp-aware Kalman predictor is compared with filters that deliberately treat delayed measurements as current. Held-out batches of 500 trials estimate the first observed downward crossings of 50% ten-second survival on the evaluated delay grid, with 1 ms local brackets for 5 N and 10 N pushes. For the point model, the reference finite-difference first observed crossing is 51.9 ms at 5 N, while filter-aware redesign reaches 60.7 ms. The base discrete filter first observed crossings are 66.3 and 44.1 ms; delay-aware prediction gives 252.2 and 125.5 ms. Phase margin divided by crossover closely predicts nominal sampled-loop instability but is tested separately against nonlinear survival. Survival, terminal dwell and active-time effort expose distinct noise-versus-lag trade-offs. The contribution is a calibrated and reproducible boundary comparison, not a new estimator or a general controller hierarchy.

Index Terms—Cart pole, delayed measurements, Kalman prediction, baseline calibration, sampled control, survival boundary.

## I INTRODUCTION

The inverted pendulum remains useful for studying unstable mechanical systems and constrained feedback [1]. Its simplicity also makes controller comparisons sensitive to seemingly minor implementation choices. A derivative filter changes loop dynamics, a covariance ratio changes estimator bandwidth, and a delayed measurement requires a timestamp-consistent update. A favorable success rate at one delay does not isolate any one of these mechanisms.

Comparisons of LQG-oriented pendulum control [2] and broader control families [3] already exist. Reproducible benchmark environments support disturbances in inputs, measurements and inertia [4], [5]. Delayed-measurement Kalman filtering and state augmentation are established methods [6], and the absence of general LQG margin guarantees is classical [7]. Consequently, neither a PID/LQR/LQG comparison, a predictor, nor the observation that a filtered loop has different margins constitutes algorithmic novelty.

The question addressed here is narrower than proposing another pendulum controller: for a specified task and information set, which apparent delay advantages persist after correcting noise units and sample timing, calibrating derivative filters and gains, and using known measurement age? Existing comparative studies [2], [3] assess controller performance, benchmark suites [4], [5] provide repeatable environments, and delayed-estimation theory [6] provides the predictor. We do not claim a missing general benchmark or new predictor theory. Our empirical contribution is the controlled combination of these checks in two matched inertia models, with trial-paired first observed crossings, their recrossings, and direct comparisons with nominal linear delay predictions. This is a case-specific attribution study, not evidence that the combination is absent from all earlier literature.

## II MODEL AND TASK

The state is z = [x, v, θ, ω]ᵀ, with θ measured from upright and positive toward positive cart displacement. Cart mass M = 1 kg, pole mass m = 0.1 kg, centre-of-mass distance l = 0.5 m, viscous cart friction b = 0.1 N s/m and g = 9.81 m/s² define the nominal plants. Let I = ρml² and J = I + ml². The point model uses ρ = 0; the uniform rod uses ρ = 1/3 and total length 2l. Thus the two plants share COM distance rather than tip length.

[Editable equation 1: full_dynamics]

Equation (1) gives the complete coupled dynamics, including the clipped command u, external push fpush, cart friction and centrifugal term. Here Mq is the generalized mass matrix and J = I + ml². Its determinant is positive for the declared positive masses. The attached supplement derives both accelerations, energy balance, linearization and exact sampled transitions. Gains are designed for each nominal inertia model.

The nonlinear plant uses fourth-order Runge–Kutta integration at 1 ms and a 10 ms control period with zero-order-held commands clipped to ±10 N. The initial state is [0,0,0.1,0]ᵀ. An unannounced external push of 5 N or 10 N acts from 2.0 through 2.1 s, after command clipping. Each trial independently draws M, m, l and b uniformly within ±20% of nominal and holds them fixed. Position and angle measurements have independent per-sample standard deviations 0.005 m and 0.002 rad. No Gaussian process noise is injected into the plant; W is an estimator design covariance for unmodelled dynamics.

[Editable equation 2: delay]

The delay τ is constant and known only to the predictor. Measurements refer to the actual 1 ms plant history, permitting fractional control-sample delays. Noise is generated at 100 Hz for each arriving packet. No packet predates initialization: controllers hold the known initial packet until a valid delayed packet arrives. The estimator initial mean is the stated initial state; the predictor uses a conservative steady-state prior covariance. All other filters intentionally ignore packet age.

A trial survives if |θ| ≤ 0.5 rad and |x| ≤ 2.4 m throughout ten seconds. Failure freezes the state immediately and sets commands to zero at the next scheduled control update. Terminal dwell additionally requires |θ| ≤ 0.002 rad and |x| ≤ 0.02 m continuously over the final second. Active-time RMS force divides effort by time before termination; full-horizon RMS is supplied separately. Neither low effort after failure nor finite-horizon survival is described as successful stabilization.

## III BASELINES AND CALIBRATION

All LQR designs use Q = diag(1,1,25,1), R = 0.01 and u = −Kẑ. The continuous regulator uses CARE. The discrete regulator uses exact ZOH dynamics and stage weights QTs and RTs, a stated sampled-stage approximation rather than an exact intersample cost. The velocity oracle transports exact velocities with noisy positions and is an informational reference, not a position-only implementation.

[Editable equation 3: fd]

The finite-difference reference uses α = 0.8. We sweep α ∈ {0,0.1,0.2,0.4,0.6,0.8,0.9,0.95,0.98}, first keeping continuous LQR gains fixed. A second sweep redesigns the four gains while including filter memory in the closed loop. The local static-output-feedback objective combines the nominal initial-condition quadratic transient and a ten-second stationary-noise H₂ surrogate. It is solved from multiple starts with bounded gain multipliers; it is not a global or delay-robust optimum. PD reference and LQR-FD are the same four-gain filtered feedback family after their gains are specified, so their labels are not treated as independent architecture classes.

Fig. 1. Development sweep over nine finite-difference filter coefficients, with fixed continuous LQR gains and a local filter-aware gain redesign. Each point averages five declared tasks and 200 paired trials per task. Tuning uses development data only; no global optimality is asserted.

Continuous Kalman design requires a measurement spectral density rather than per-sample variance. Under the equivalent independently sampled/boxcar-average white-noise convention we use

[Editable equation 4: units]

At Ts = 0.01 s, inserting Rm directly gives a spectral density 100 times too large. Multiplying W by 100 with the legacy V produces the same gain as correcting V, to a verified relative error below 3 × 10⁻¹². This is a covariance-ratio intervention and cannot be attributed solely to observer implementation. Continuous and discrete filtering are still different sampled algorithms, so the conversion alone does not make their gains identical.

We retain a legacy-current-sample update solely to isolate the unit correction: both its old-unit and corrected-unit versions integrate the newly received sample over the preceding interval before computing control. This timing is not presented as a causal continuous-observer implementation. The causal version instead propagates with the previous held sample and previous clipped command, then holds the newly received sample for the next interval. Discrete filters predict with the known clipped command and then update, using exact Qd [8] and Rm.

The corrected causal continuous observer and discrete filter are each swept over Wσ = σW for σ = 10ʲ, j = −6,…,8, with fixed feedback gains. The Kalman gain depends on the ratio W/V, not their common magnitude. Selection maximizes mean survival across the five development tasks (0 ms/5 N, 40 ms/5 N, 60 ms/5 N, 0 ms/10 N, 60 ms/10 N), then mean dwell and finally minimizes active RMS. Each setting uses 200 trial-paired runs per task. The same declared task weights apply to each family. Selected tunings are frozen before boundary estimation; all sweep points remain available.

Fig. 2. Development survival at 60 ms/5 N over σ = 10⁻⁶ through 10⁸. Squares mark dKF at σ = 1: point dKF 192/200 (96.0%) versus held-out 485/500 (97.0%); rod dKF 200/200 (100.0%) versus held-out 499/500 (99.8%). Fig. 2 uses seed 20261121 and 200 trials per point; Table II/Fig. 6 use seed 20261122 and 500. Solid curves are dKF; dashed curves are causal cKF. The selection objective averages all five declared tasks.

The selected fixed-gain α values are 0.0 and 0.1 for point and rod, respectively. Filter-aware redesign selects 0.4 and 0.6. The selected continuous-observer multipliers are 10 and 1; discrete-filter multipliers are 10 and 100. These are best tested development settings under the declared lexicographic objective. Decade-spaced maxima and high-end plateaus do not identify a unique continuous optimum or a universal performance advantage. The supplement gives the complete dwell and effort sweeps.

## IV KNOWN DELAY PREDICTION

The delay-unaware discrete design fuses stale measurements as current and is therefore a robustness baseline. The predictor instead maintains an estimate at the measurement timestamp, performs the Kalman innovation there, and propagates it to the current control time with recorded clipped commands. For τ = qTs,

[Editable equation 5: predict]

For τ = qTs + r, 0 ≤ r < Ts, exact fractional transitions integrate the partial held-input intervals; the supplement provides the full expression. Unknown external push values and perturbed plant parameters are never supplied to the predictor. We evaluate both the base covariance and the multiplier selected for the delay-unaware discrete filter, without retuning the predictor on held-out data. This is an established known-delay baseline [6], not a proposed new filtering method. At zero delay it matches the ordinary discrete filter exactly. With the nominal linear model, noise-free measurements and no unknown push, it reproduces the zero-delay trajectory for tested delays up to 115 ms, with maximum error below 10⁻⁸.

## V DELAY BOUNDARIES AND UNCERTAINTY

[Editable equation 6: d50]

Here pT is the ten-second survival probability at the fixed push magnitude. A separate 100-trial locator seed evaluates 0,20,40,60,80,100,150,200 and 300 ms. Held-out batches use 500 new trials, verify and expand the bracket if needed, and bisect to a 1 ms crossing interval. A local 1 ms grid around the crossing checks recrossings. The initial locator ends at 300 ms, but brackets may expand up to an administrative search ceiling of 1200 ms. The largest delays actually evaluated were 300 ms for the point model and 600 ms for the rod; rod-predictor brackets expanded from 300 to 600 ms before refinement. All 56 reported crossings are interior, so none is right-censored. Interpolated D50 values and 95% intervals use 2,000 paired resamples of trial identities, preserving each trial’s uncertainty and noise sequence across delays. Intervals are pointwise and conditional on the evaluated adaptive grid; they do not incorporate a repeated tuning search, certify monotonic survival, or provide simultaneous coverage. Coarse locator and local-grid recrossings are audited explicitly.

The development, locator and held-out seeds are distinct. Common random numbers are invariant to case ordering and batch size. A first observed downward half-survival crossing is reported; below-half survival at zero delay and failure to cross by the tested limit would be censored, not assigned a fictitious optimum. Fixed 0,40 and 60 ms cells support paired intervention effects with bootstrap intervals and exact McNemar tests; Holm correction covers all 108 declared comparisons [9], [10], [11].

Fig. 3. Held-out point model first observed downward crossings of 50% ten-second survival for 5 N and 10 N pushes. Bars are 95% trial-paired bootstrap intervals conditional on evaluated delays; local numerical crossing brackets are 1 ms. A cross at zero denotes survival below 50% without added delay. These are not monotone delay limits or stability certificates.

Fig. 4. Held-out rod model first observed downward crossings of 50% ten-second survival for 5 N and 10 N pushes. Bars are 95% trial-paired bootstrap intervals conditional on evaluated delays; local numerical crossing brackets are 1 ms. A cross at zero denotes survival below 50% without added delay. These are not monotone delay limits or stability certificates.

Table I compares designs tuned on tasks that include 40 and 60 ms delays, near some of the crossings measured here. New Monte Carlo seeds separate trial realizations; this is not an out-of-delay-distribution tuning test. The predictor reuses the delay-unaware discrete filter’s selected covariance ratio. Four-gain derivative redesign and scalar Kalman-ratio sweeps have unequal tuning budgets, so these are declared calibrated designs rather than equally optimized controller classes.

TABLE I  FIRST OBSERVED 50 PERCENT SURVIVAL CROSSINGS IN MS

For point-mass base dLQG, D50 changes from 66.3 [66.0, 67.0] ms at 5 N to 44.1 [43.0, 45.0] ms at 10 N. The corresponding base-predictor values are 252.2 [250.0, 254.0] and 125.5 [123.0, 128.0] ms. Thus a single 60 ms success rate cannot stand for delay robustness. The tuned filter and filter-aware derivative baseline also alter the ranking; boundary and tuning information are necessary to interpret individual success cells.

## VI MARGINS AND NONLINEAR RESULTS

For each fixed compensator we compute all nominal zero-delay sampled gain crossovers, retaining positive phase margins φmi in radians. A pure added-delay estimate is

[Editable equation 7: margin]

We independently form the exact fractional-measurement-delay closed loop by augmenting plant history, held command history and controller state, and bracket the first observed spectral-radius crossing at one millisecond. This validates the linear calculation against the actual sampled implementation, rather than borrowing a full-state LQR margin. A predictor changes with τ, so the fixed-loop division is not applied to it. In its ideal known-model setting, prediction removes deterministic measurement age from nominal regulation; unknown disturbances and model errors still limit the nonlinear task.

The point PD and legacy-observer phase margins are 27.3° and 27.8°, yet their crossover frequencies are 13.66 and 8.65 rad/s. The resulting estimates are 34.9 and 56.2 ms, compared with exact lifted boundaries of 34.5 and 56.5 ms. Similar phase margins therefore do not imply similar delay margins. Across fixed loops, the maximum discrepancy between the phase-based estimate and the midpoint of the one-millisecond lifted bracket is 0.5 ms.

Fig. 5. Phase-based nominal delay estimates versus nonlinear ten-second survival boundaries. The diagonal is equality. Exact lifted linear predictions, tabulated in the supplement, closely match the phase-based values. Predictors are omitted because their compensators depend on delay.

Figure 5 tests, rather than assumes, the link to nonlinear survival. Linear loss of local asymptotic stability, bounded saturated oscillation and finite-horizon failure are different events. Parameter perturbations change poles and crossings; pushes excite nonlinear excursions; command clipping can either prolong bounded survival or prevent recovery. Consequently, mismatch with D50 is an empirical result and not evidence that phase margin has failed as a local linear metric. We do not claim that margins alone explain the nonlinear ranking, and do not present the established LQG-margin limitation [7] as a novel result.

Fig. 6. Paired held-out checks isolate the covariance-unit correction within the legacy update, then enforce causal observer timing and compare delay-unaware and timestamp-aware discrete estimators. Each cell has 500 trials and pointwise Wilson intervals.

At point-model 60 ms/5 N, correcting units alone changes survival from 46.2% to 41.0%. The causal corrected continuous observer gives 5.6%, while a discrete filter retaining the same continuous regulator gain gives 92.4% and the discrete regulator gives 97.0%. Thus the unit error is real, but a unit correction alone does not recover the discrete-filter result in this task. The diagnostic with continuous K separates regulator discretization from the estimator update; neither change is treated as a universal implementation advantage.

Fig. 7. Local one-millisecond held-out survival curves around each first observed half-survival crossing. Bands are pointwise Wilson intervals. Recrossings are retained: a single monotone collapse is not assumed, and reported boundary intervals condition on the evaluated delay grid.

The local curves in Fig. 7 retain upward half-survival recrossings. These can arise from the interaction of sampled measurement age, saturated trajectories and finite-horizon criteria; their presence prevents a claim of a unique monotone failure cliff. The full queried grid and recrossing counts are therefore part of the result, and D50 consistently denotes the first observed crossing.

TABLE II  POINT MODEL NOISE LAG AND EFFORT TRADE OFF

Table II and the full sweeps show why survival alone is an incomplete objective. Low-bandwidth observation can improve quiet regulation and reduce force noise while increasing lag; aggressive observation or unfiltered differences can improve a delayed survival cell while increasing effort and destroying the strict terminal dwell event. Values on this frontier are not evidence for an inherent continuous-versus-discrete or derivative-versus-Kalman hierarchy. The velocity oracle is explicitly excluded from deployable rankings because it has additional information.

A paired onset-phase check shifts the push by an independent uniformly drawn integer from 0 through 9 ms while keeping its 100 ms duration and the same parameter and noise realizations. Across 269 cells, the largest observed absolute survival change is 2.8 percentage points at 60 ms and 5.4 points at queried local crossing anchors; 7 cells change sides of 50%. Point-model base dKF at 60 ms/5 N changes from 97.0% to 94.2% (paired difference -2.8 points, pointwise 95% interval -4.2 to -1.6). Supplement S1 gives the protocol, Fig. S5 and full tables. This check does not estimate a complete phase-averaged delay curve or prove monotone survival.

## VII LIMITATIONS AND CONCLUSION

Cross-model differences include model-specific gains and therefore do not isolate inertia with a fixed controller. The primary task fixes push onset and duration. The added onset-phase check varies only the position of that push within one control period; it does not cover arbitrary disturbance times or randomized durations, and does not identify every cause of survival recrossing.

These results are simulation evidence for one plant scale, initialization, uncertainty law, measurement-noise level, command limit and ten-second horizon. Process covariance is a tuning device rather than an identified physical-noise spectrum. Filter-aware redesign is local and nominal; neither its gain search nor the predictor covariance is claimed globally optimal. Delay is fixed and exactly timestamped; jitter, packet loss, unknown initial conditions, sensor bias, friction nonlinearities and actuator dynamics require additional evaluation. Confidence intervals quantify trial variability under the declared distribution, not modelling uncertainty or hardware reliability.

The contribution is the controlled boundary study and its reproducibility: covariance-unit correction, causal timing, filter and gain calibration, known-delay prediction and a tested link between linear margins and nonlinear survival. Noise units, tuning objectives and packet timestamps must accompany task-specific controller comparisons. The results support an empirical methods and benchmarking study; they do not establish a new control method or a general controller hierarchy.

Data availability—Supplementary Material S1, Detailed Derivations and Reproducibility Supplement, is attached as a separate PDF and editable Word file. The versioned software, data, scientific figures and illustrative movies are archived with the repository release [12]. Each movie is a single paired realization, not a Monte Carlo success estimate.

[Project repository](https://github.com/Ranger915/Cart-pole-research-project)

[Archive DOI 10.5281/zenodo.24017779](https://doi.org/10.5281/zenodo.24017779)

[Supplement S1 PDF](https://zenodo.org/records/24017779/files/revised_detailed_derivations.pdf?download=1)

## REFERENCES

[1] K. J. Åström and R. M. Murray, Feedback Systems: An Introduction for Scientists and Engineers. Princeton University Press, 2008. https://authors.library.caltech.edu/records/yzs24-xsx88

[2] M. Rani and S. S. Kamlu, “Optimal LQG controller design for inverted pendulum systems using a comprehensive approach,” Scientific Reports, vol. 15, art. 4692, 2025, doi: 10.1038/s41598-025-85581-3.

[3] S. Irfan, L. Zhao, S. Ullah, A. Mehmood, and M. F. U. Butt, “Control strategies for inverted pendulum: A comparative analysis of linear, nonlinear, and artificial intelligence approaches,” PLOS ONE, vol. 19, no. 3, e0298093, 2024, doi: 10.1371/journal.pone.0298093.

[4] Z. Yuan et al., “safe-control-gym: A unified benchmark suite for safe learning-based control and reinforcement learning in robotics,” arXiv:2109.06325v4, 2022. https://arxiv.org/abs/2109.06325

[5] Y. Duan, X. Chen, R. Houthooft, J. Schulman, and P. Abbeel, “Benchmarking deep reinforcement learning for continuous control,” Proc. ICML, PMLR, vol. 48, pp. 1329–1338, 2016. https://proceedings.mlr.press/v48/duan16.html

[6] T. D. Larsen, N. A. Andersen, O. Ravn, and N. K. Poulsen, “Incorporation of time delayed measurements in a discrete-time Kalman filter,” Proc. 37th IEEE Conf. Decision and Control, vol. 4, pp. 3972–3977, 1998, doi: 10.1109/CDC.1998.761918.

[7] J. C. Doyle, “Guaranteed margins for LQG regulators,” IEEE Trans. Autom. Control, vol. 23, no. 4, pp. 756–757, 1978, doi: 10.1109/TAC.1978.1101812.

[8] C. F. Van Loan, “Computing integrals involving the matrix exponential,” IEEE Trans. Autom. Control, vol. 23, no. 3, pp. 395–404, 1978, doi: 10.1109/TAC.1978.1101743.

[9] E. B. Wilson, “Probable inference, the law of succession, and statistical inference,” J. Amer. Stat. Assoc., vol. 22, no. 158, pp. 209–212, 1927, doi: 10.1080/01621459.1927.10502953.

[10] Q. McNemar, “Note on the sampling error of the difference between correlated proportions or percentages,” Psychometrika, vol. 12, no. 2, pp. 153–157, 1947. https://pubmed.ncbi.nlm.nih.gov/20254758/

[11] S. Holm, “A simple sequentially rejective multiple test procedure,” Scandinavian J. Stat., vol. 6, no. 2, pp. 65–70, 1979. https://sci2s.ugr.es/keel/pdf/specific/articulo/0052_001.pdf

[12] R. M. Barathkumar, “Tuning and Delay-Aware State Prediction in Cart-Pole Survival Boundaries”, software and data, ver. 1.0.0, Zenodo, 2026, doi: 10.5281/zenodo.24017779. Repository: https://github.com/Ranger915/Cart-pole-research-project.