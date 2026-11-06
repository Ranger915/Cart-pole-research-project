# Tuning and Delay-Aware State Prediction in Cart-Pole Survival Boundaries

RAAGHAVAN MOOKIAH BARATHKUMAR · Version 1.0.0

[Repository](https://github.com/Ranger915/Cart-pole-research-project) · [Zenodo archive and DOI](https://doi.org/10.5281/zenodo.24017779)

Read [the manuscript PDF](revised_ieee_manuscript.pdf), [editable Word manuscript](revised_ieee_manuscript.docx), [Supplement S1 PDF](revised_detailed_derivations.pdf), or [editable supplement](revised_detailed_derivations.docx). The [combined review PDF](manuscript_with_supplement.pdf) attaches S1 after the article. The methodological response is supplied in Word and PDF. Extract a release ZIP and open START_HERE.html for a local reading, figure and movie index.

This simulation study compares point-mass and uniform-rod cart poles. It corrects covariance units, distinguishes estimator timing, calibrates derivative filtering and gains, extends covariance-ratio sweeps, includes known-delay state prediction, and reports first observed half-survival crossings with recrossing flags. Earlier architecture-only and observer-implementation interpretations are superseded. No new controller or universal architecture ranking is claimed.

At sigma = 1, Fig. 2 uses 192/200 point and 200/200 rod successes; the held-out dKF base cells in Table II/Fig. 6 use 485/500 and 499/500, respectively. Designs match; seeds and sample sizes differ. The actual evaluated maximum delays are 300 ms for point and 600 ms for rod; no reported crossing is right-censored. The 1200 ms administrative ceiling was unused.

The randomized push-onset check adds 269,000 trajectories across 269 paired cells, with all zero-phase reruns exactly matching the prior outcomes. The largest absolute survival changes are 2.8 percentage points at 60 ms and 5.4 points at local crossing anchors; seven cells change sides of 50%. This local check does not re-estimate a phase-averaged D50. Numerical details are in results/push_phase_summary.csv and the raw NPZ files.

## Reproduce

Install source/requirements.txt in a Python environment. Scientific computations used Python 3.13; Word authoring used Python 3.12. Recorded package versions are in results/runtime_versions.json. Use those versions for exact replay.

Run source/development.py, source/finalize_configs.py, source/boundaries.py, source/margins.py, source/audit.py, source/phase_check.py, source/revision_audit.py, source/videos.py, source/transcode_videos.py and source/figures.py in that order. Each script detects this extracted layout. Boundaries and phase runs reuse existing results/checkpoints. For a fresh campaign, start with source/ and results/equations_mathml.json in a clean copy; start clean after changing designs, noise, seeds or protocol. Existing result NPZ files are supplied for inspection without rerunning the entire campaign.

Run source/build_documents.py for editable Word files. Equations use Office16 MML2OMML.XSL; render_word.ps1 uses installed Microsoft Word to update fields and export PDFs. The QA Poppler executable path is host-specific. Scientific computations do not require Word. The attached combined PDF concatenates the manuscript and S1 without changing their individual page contents.

videos/ contains twelve ten-second H.264 MP4 comparisons: both models, delays 0/40/60 ms, pushes 5/10 N, fourteen configurations per movie. Each movie shows one paired illustrative realization with a fixed push onset, not an ensemble survival estimate. Failed states are frozen and commands zeroed at the next control update. Randomized-phase results are reported separately.

figures/ contains publication PNG/PDF figures and extra traces. results/ contains sweeps, held-out binary outcomes, boundary intervals, margins, paired intervention tests, phase sensitivity, trial census and validation records. source/final_archive.py checks scientific and document gates before packaging; its --history mode also requires a verified publication record.

Boundary intervals condition on the evaluated adaptive grid and fixed selected design. Ten-second survival, terminal dwell and local asymptotic stability are different outcomes. The velocity oracle has privileged measurements. The manuscript has not been peer reviewed; no hardware validation or journal acceptance is claimed.

## Rights and citation

All rights reserved; no reuse license is granted for original project material. See LICENSE.md. Third-party rights remain unchanged. Cite the versioned software/data archive using CITATION.bib; its DOI is not a journal-publication DOI.
