# Progress — ML Surrogate Modelling of Seismic Drift (BNBC 2020 RC Frames)

This file is the single source of truth for checklist progress across the site (`index.html`, Sheets 02–04). It works two ways:

- **File → site:** each sheet fetches this file on load and checks the matching boxes. Tick items here directly — in a text editor, or by clicking checkboxes right in GitHub's rendered view if this is pushed to a repo — and reload the sheet to see it reflected.
- **Site → file:** each sheet has an **Export progress.md** button that downloads an updated copy of this file with that sheet's current checkbox states merged in. Replace this file (or commit the download) to persist what you checked in the browser.

Keep the `<!-- id:... -->` comments intact — that's how the site matches a line here to a checkbox there. Reword the visible text freely; the site only reads the `[ ]`/`[x]` and the id.

Progress isn't graded by percentage here — Sheet 02's phases matter more than Sheet 04's reading list. Use the numbers as a pulse check, not a scoreboard.

---

## Sheet 02 · Research Roadmap

### PH 0 — Environment & codebase orientation
- [ ] Clone the repo, create/activate a Python 3.12 venv (not 3.14 — OpenSeesPy incompatibility noted in the repo) <!-- id:c0-1 -->
- [ ] Install requirements.txt; run `pip list | grep -E "openseespy|tensorflow|xgboost|shap"` and read the real versions printed <!-- id:c0-2 -->
- [ ] Run `python -c "import openseespy.opensees as ops; ops.wipe(); print('OK')"` yourself — this is the single highest-value 10 seconds in the whole plan <!-- id:c0-3 -->
- [ ] Read `.github/copilot-instructions.md` in full <!-- id:c0-4 -->
- [ ] Read `config/bnbc_parameters.yaml` and `config/analysis_config.yaml` top to bottom <!-- id:c0-5 -->
- [ ] Skim `task_plan.md` for the version of the plan the codebase was actually built against <!-- id:c0-6 -->

### PH 0.5 — Independent verification (added — not in the repo's own plan)
- [ ] Read `project/src/modeling/rc_frame.py` line by line against your own RC design knowledge — fiber discretisation, Concrete02/Steel02 parameters, load path <!-- id:c05-1 -->
- [ ] Regenerate the 80 Phase 1 models yourself via `generate_phase1_models()` rather than trusting the checked-in JSON files <!-- id:c05-2 -->
- [ ] Hand-calculate T ≈ 0.0466·H^0.9 for 3 models across the height range and compare to the eigenvalue period the code reports <!-- id:c05-3 -->
- [ ] Hand-calculate base shear for one building; compare to `apply_lateral_loads()` output <!-- id:c05-4 -->
- [ ] Resolve the Life Safety threshold conflict (2.0% vs 2.5%) — pick one, record why, fix it in one place <!-- id:c05-5 -->
- [ ] Confirm current Buildings journal metrics directly on mdpi.com rather than trusting either number in the docs <!-- id:c05-6 -->
- [ ] Run the existing 85+ pytest suite yourself; read 10 of the tests to see what they actually assert (code runs vs. code is engineering-correct are different claims) <!-- id:c05-7 -->

### PH 1 — Structural modelling
- [ ] Confirm 80 files exist in `models/openseespy/`, each 10–50 KB (repo's own sanity range) <!-- id:c1-1 -->
- [ ] Spot-check that Non-Sway / OMRF / IMRF / SMRF at the same height & zone actually differ in confinement/reinforcement per BNBC Table 2.7.4, not just in a label <!-- id:c1-2 -->
- [ ] Run gravity-only analysis on 5 models spanning the height range; confirm convergence and that reactions balance applied load <!-- id:c1-3 -->
- [ ] Confirm no soft-storey or obviously unstable configuration slipped through the parametric generator <!-- id:c1-4 -->

### PH 2 — Ground motions & the real IDA campaign
- [ ] Open several of the "32–40 verified" ground-motion files directly — confirm they're real time-history data, not placeholder metadata <!-- id:c2-1 -->
- [ ] Cross-check 3–4 records' magnitude/distance against the PEER NGA-West2 database yourself <!-- id:c2-2 -->
- [ ] Verify each record's scaled spectrum lands within ±10% of the BNBC target at T1 (README §7.2 procedure) <!-- id:c2-3 -->
- [ ] Time a small pilot campaign on your own hardware; extrapolate a real wall-clock estimate instead of trusting the repo's 8–12 hr figure, which predates the scope growing to 80 buildings <!-- id:c2-4 -->
- [ ] Decide local overnight run vs. ~1–3 hr cloud run (~$10–20 quoted — verify current pricing before booking) <!-- id:c2-5 -->
- [ ] Launch the full campaign; monitor via the log tail command in `START_HERE.md` <!-- id:c2-6 -->
- [ ] QC the output before touching Phase 3: PIDR in a physically sane 0.1–8% range, no NaNs, roughly monotonic with intensity, spot-checked against your Sheet 03 Project 2 curve <!-- id:c2-7 -->

### PH 3 — ML training on the real dataset
- [ ] Run `run_phase3_ml.py` against the real `ida_results_verified.csv` <!-- id:c3-1 -->
- [ ] Compare resulting R²/RMSE/MAE against the repo's placeholder table — expect a difference, that table was never real data <!-- id:c3-2 -->
- [ ] Re-run SHAP; confirm top features make physical sense (Sa, period, zone should dominate — investigate if something odd tops the list) <!-- id:c3-3 -->
- [ ] 5-fold cross-validate; confirm CV R² is consistent with the held-out test R² within ~±0.05 <!-- id:c3-4 -->
- [ ] If best R² is below 0.90, run 2–3 rounds of real feature engineering/tuning — then stop and accept whatever the honest ceiling is <!-- id:c3-5 -->
- [ ] Save the best model + scaler together; you'll need both for Phase 4 <!-- id:c3-6 -->

### PH 4 — Fragility curves & figures
- [ ] Confirm final IO/LS/CP thresholds (post PH 0.5 resolution) before fitting anything <!-- id:c4-1 -->
- [ ] Fit the log-linear cloud regression ln(PIDR) = a + b·ln(Sa) per zone <!-- id:c4-2 -->
- [ ] Compute dispersion β and median capacity θ per performance level per zone <!-- id:c4-3 -->
- [ ] Generate the 9 required figures (spectra, model schematic, IDA curves ×2, fragility ×2, ML comparison, SHAP ×2) at ≥300 dpi <!-- id:c4-4 -->
- [ ] Compile the 5 required tables (archetypes, model properties, GM records, ML comparison, fragility parameters) <!-- id:c4-5 -->
- [ ] Sanity-check fragility medians against ASCE 41-23 acceptance criteria where comparable studies exist <!-- id:c4-6 -->

### PH 5 — Framework comparative analysis
- [ ] Compute the Performance Gradient (% PIDR improvement vs. Non-Sway) at multiple intensities <!-- id:c5-1 -->
- [ ] Compute the Framework Complexity Index (reinforcement volume × fabrication hours, normalised to Non-Sway) <!-- id:c5-2 -->
- [ ] Compute the Cost-Benefit Ratio and locate the Pareto frontier "sweet spot" <!-- id:c5-3 -->
- [ ] Build Figures 6a–6d (multi-framework gradient, complexity trade-off, zone-dependent selection, fragility overlay) <!-- id:c5-4 -->
- [ ] Run ANOVA across frameworks per intensity level; draft the practical framework-selection matrix <!-- id:c5-5 -->

### PH 6 — Writing
- [ ] §2 Building Models (700–900 words) — easiest, start here <!-- id:c6-1 -->
- [ ] §3 OpenSeesPy Methodology (800–1000 words) <!-- id:c6-2 -->
- [ ] §4 Ground Motions & IDA (600–800 words) <!-- id:c6-3 -->
- [ ] §5 ML Framework (800–1000 words) <!-- id:c6-4 -->
- [ ] §6 Results incl. 6a Framework Comparison (2,000–2,500 words) — the section that matters most <!-- id:c6-5 -->
- [ ] §7 Discussion (600–800 words) <!-- id:c6-6 -->
- [ ] §1 Introduction (800–1000 words) — write last, now that you know what you found <!-- id:c6-7 -->
- [ ] §8 Conclusions (300–400 words) + Abstract (250 words) — very last <!-- id:c6-8 -->

### PH 7 — Review, similarity check & formatting
- [ ] Self-review every equation, figure and table number against in-text references <!-- id:c7-1 -->
- [ ] Similarity check (Turnitin/iThenticate or institutional equivalent) — target <15% <!-- id:c7-2 -->
- [ ] Reformat to the current MDPI Buildings template, downloaded fresh from the journal site <!-- id:c7-3 -->
- [ ] Write a one-page cover letter — why it fits the journal's scope, why it matters <!-- id:c7-4 -->
- [ ] Confirm data-availability statement — repo URL, dataset upload plan (Zenodo/Mendeley Data) <!-- id:c7-5 -->

### PH 8 — Submission & revision
- [ ] Submit via the journal portal with all supplementary files (code repo link, dataset link) <!-- id:c8-1 -->
- [ ] Track first-decision timing — 2026 median for Buildings is ~15 days <!-- id:c8-2 -->
- [ ] Prepare a point-by-point response-to-reviewers document as soon as comments arrive <!-- id:c8-3 -->
- [ ] Budget 2–6 weeks of real revision work once reviews land — timing of the review itself isn't in your control <!-- id:c8-4 -->

## Sheet 03 · Preparation Projects

### Preparation Project 01 · Structural scripting — Single-Frame Sanity Check
- [ ] Install OpenSeesPy in a clean venv; confirm `import openseespy.opensees` works <!-- id:p1-1 -->
- [ ] Work through OpenSeesPy's basic model-building examples (nodes, elements, fix, mass) <!-- id:p1-2 -->
- [ ] Define Concrete02 (unconfined + Mander-confined core) and Steel02 by hand with real values (f′c = 25 MPa, fy = 415 MPa) <!-- id:p1-3 -->
- [ ] Build one fiber column section and one fiber beam section <!-- id:p1-4 -->
- [ ] Define geometry: 3 storeys, 3.5 m storey height, 1 bay, 6 m wide (matches the repo's own convention) <!-- id:p1-5 -->
- [ ] Assign nodes, forceBeamColumn elements, fixed-base boundary conditions <!-- id:p1-6 -->
- [ ] Apply gravity loads (dead + live per BNBC), run gravity analysis, confirm convergence <!-- id:p1-7 -->
- [ ] Check column axial reactions sum to applied load — hand-calc cross-check <!-- id:p1-8 -->
- [ ] Run eigenvalue analysis; extract T1; compare to T ≈ 0.0466·H^0.9 <!-- id:p1-9 -->
- [ ] Write the one-page memo: geometry, materials, T1 comparison, what surprised you <!-- id:p1-10 -->

### Preparation Project 02 · Nonlinear dynamics — One Building, One Earthquake, One IDA Curve
- [ ] Register a PEER NGA-West2 account <!-- id:p2-1 -->
- [ ] Select 1 record matching Bangladesh-relevant criteria (M 6.0–7.5, R 20–150 km, soil C/D) <!-- id:p2-2 -->
- [ ] Download the record; plot the raw acceleration time-history yourself <!-- id:p2-3 -->
- [ ] Compute the record's own response spectrum Sa at your frame's T1 <!-- id:p2-4 -->
- [ ] Compute the BNBC target spectrum for one zone; compute the scale factor <!-- id:p2-5 -->
- [ ] Extend the Project 1 script with a nonlinear time-history analysis (Newmark-β, Rayleigh damping) <!-- id:p2-6 -->
- [ ] Implement an adaptive time-stepping fallback for non-convergence <!-- id:p2-7 -->
- [ ] Loop the same record through 8–10 increasing scale factors, 0.1g → ~2.0g Sa <!-- id:p2-8 -->
- [ ] Extract peak inter-storey drift ratio at each level <!-- id:p2-9 -->
- [ ] Apply the PIDR ≥ 10% collapse stopping rule <!-- id:p2-10 -->
- [ ] Plot the curve; write the methods note <!-- id:p2-11 -->

### Preparation Project 03 · Data science — ML Sprint on a Public Structural Dataset
- [ ] Download the UCI Concrete Compressive Strength dataset (1,030 rows, 8 features) <!-- id:p3-1 -->
- [ ] EDA: distributions, correlation matrix, confirm no missing values <!-- id:p3-2 -->
- [ ] Split 65/15/20 train/val/test — matching the repo's own Phase 3 convention <!-- id:p3-3 -->
- [ ] Fit StandardScaler on the training set only; apply to val/test — deliberately notice how easy this is to get backwards <!-- id:p3-4 -->
- [ ] Train a Linear Regression baseline <!-- id:p3-5 -->
- [ ] Train a Random Forest <!-- id:p3-6 -->
- [ ] Train an XGBoost model with early stopping <!-- id:p3-7 -->
- [ ] 5-fold cross-validate each model <!-- id:p3-8 -->
- [ ] Compare R² / RMSE / MAE across models in one table <!-- id:p3-9 -->
- [ ] Run SHAP's TreeExplainer on the best model; generate a summary and a dependence plot <!-- id:p3-10 -->
- [ ] Write one paragraph: do the top SHAP features (cement, age, water/cement ratio) match civil-engineering intuition? <!-- id:p3-11 -->

### Preparation Project 04 · Statistics & writing — Fragility Micro-Paper
- [ ] Gather ≥6–8 (Sa, PIDR) pairs — reuse Project 2's curve if it has enough points; otherwise supplement with clearly-labelled illustrative data, never disguised as real <!-- id:p4-1 -->
- [ ] Fit the log-linear regression ln(PIDR) = a + b·ln(Sa) <!-- id:p4-2 -->
- [ ] Compute dispersion β as the standard deviation of the residuals <!-- id:p4-3 -->
- [ ] Compute P(LS | Sa) = Φ[(ln(Sa) − ln(θ))/β] at the IO/LS/CP thresholds <!-- id:p4-4 -->
- [ ] Plot the fragility curve <!-- id:p4-5 -->
- [ ] Set up a Zotero (or Mendeley) library; add the repo's core-10 references <!-- id:p4-6 -->
- [ ] Read 3–5 of those in full — especially Vamvatsikos & Cornell (2002) and one Kazemi et al. paper — not just the abstracts <!-- id:p4-7 -->
- [ ] Write the mock manuscript, following the repo's own section/word-target style <!-- id:p4-8 -->
- [ ] Get one honest outside read on clarity — the cheap rehearsal for the real peer review <!-- id:p4-9 -->

### Preparation Project 05 · Cross-tool verification (optional) — Second Tool, Same Building
- [ ] Get Abaqus/CAE running — the free Student Edition (1,000-node limit) is enough for one simple frame <!-- id:p5-1 -->
- [ ] Build the same geometry (3 storeys, 3.5 m storey height, 1 bay, 6 m wide) as a continuum/solid model <!-- id:p5-2 -->
- [ ] Define concrete via Concrete Damaged Plasticity with matching f′c = 25 MPa; work out what each CDP parameter (dilation angle, eccentricity, fb0/fc0, K, viscosity) physically represents rather than pasting in defaults <!-- id:p5-3 -->
- [ ] Model reinforcement as embedded rebar, matching Project 01's reinforcement ratio as closely as practical <!-- id:p5-4 -->
- [ ] Mesh the model; run it at two mesh densities and see how sensitive the result is — a question OpenSeesPy's fiber approach mostly sidesteps <!-- id:p5-5 -->
- [ ] Run a frequency step; extract T1 — you now have three independent numbers for the same building (Abaqus, OpenSeesPy, BNBC hand-calc) <!-- id:p5-6 -->
- [ ] Run a displacement-controlled static pushover; plot base shear vs. roof drift <!-- id:p5-7 -->
- [ ] Write a short comparison note: where the two tools agreed, where they diverged, and your best explanation why <!-- id:p5-8 -->

## Sheet 04 · Skills & Expertise Tracker

### 01 — Python engineering fundamentals
- [ ] Confirm comfort with venv/pip workflows pinned to Python 3.12 specifically <!-- id:s1-1 -->
- [ ] Do one "code archaeology" pass: read `rc_frame.py` and `phase1_generator.py` line by line, annotate what each part does <!-- id:s1-2 -->
- [ ] Run `pytest -v` locally; read at least 3 pass/fail outputs and understand exactly what's being asserted <!-- id:s1-3 -->
- [ ] Skim `.github/workflows/tests.yml` to understand what the CI pipeline actually checks <!-- id:s1-4 -->
- [ ] Practice one full git workflow — branch, commit, review your own diff — on a fork <!-- id:s1-5 -->

### 02 — OpenSeesPy & nonlinear structural dynamics
- [ ] Complete Prep Projects 01 and 02 (Sheet 03) <!-- id:s2-1 -->
- [ ] Work through 3–5 OpenSeesPy official example scripts beyond your own <!-- id:s2-2 -->
- [ ] Read enough of Portwood Digital to recognise "convergence," "corotational" and "force-based element" on sight <!-- id:s2-3 -->
- [ ] Explain Concrete02 vs Concrete01 and Steel02 vs Steel01 from memory <!-- id:s2-4 -->
- [ ] Explain Newmark-β (γ = 0.5, β = 0.25) and why the repo uses those specific values <!-- id:s2-5 -->
- [ ] Explain what a forceBeamColumn element does differently from a displacement-based element <!-- id:s2-6 -->

### 03 — Earthquake engineering theory
- [ ] Read Vamvatsikos & Cornell (2002) in full — the IDA paper itself <!-- id:s3-1 -->
- [ ] Read FEMA 356 Ch. 5 (plastic hinge / component acceptance criteria) — already in your `docs/` <!-- id:s3-2 -->
- [ ] Read the relevant ASCE 41-23 chapter on performance levels <!-- id:s3-3 -->
- [ ] Skim the FEMA P-58 Vol. 1 methodology overview <!-- id:s3-4 -->
- [ ] Complete Prep Projects 02 and 04 <!-- id:s3-5 -->

### 04 — BNBC 2020 & design-code fluency
- [ ] Re-read BNBC 2020 Part 6 Ch. 2 (seismic provisions) with `config/bnbc_parameters.yaml` open side by side <!-- id:s4-1 -->
- [ ] Cross-reference every Z, Fa, Fv, R and I value in the yaml against the actual code table <!-- id:s4-2 -->
- [ ] Compare BNBC 2020's approach to ASCE 7-22's equivalent provisions — divergences are good discussion-section material later <!-- id:s4-3 -->
- [ ] Confirm the Non-Sway/OMRF/IMRF/SMRF detailing table matches BNBC Table 2.7.4 exactly, value for value <!-- id:s4-4 -->

### 05 — Machine learning & statistics
- [ ] Complete Prep Project 03 <!-- id:s5-1 -->
- [ ] Kaggle Learn: Intro to Machine Learning + Intermediate Machine Learning (free, ~3–5 hrs each) <!-- id:s5-2 -->
- [ ] Understand random forest vs. gradient boosting mechanically — not just "one usually scores higher" <!-- id:s5-3 -->
- [ ] Read SHAP's own documentation theory page <!-- id:s5-4 -->
- [ ] Understand what ANOVA is actually testing in the Phase 5 framework-comparison context <!-- id:s5-5 -->
- [ ] Understand lognormal distribution basics (median vs. dispersion) for fragility fitting <!-- id:s5-6 -->

### 06 — Software engineering practice for research code
- [ ] Refresh pytest basics — fixtures, assert, parametrize — if unfamiliar <!-- id:s6-1 -->
- [ ] Write 1–2 new unit tests for a function you didn't write, matching the existing test style <!-- id:s6-2 -->
- [ ] Understand what the multi-Python-version CI matrix (3.9–3.12) is actually protecting against <!-- id:s6-3 -->
- [ ] Practice reading a git diff carefully before merging your own changes <!-- id:s6-4 -->

### 07 — Scientific & academic writing for publication
- [ ] Complete Prep Project 04 <!-- id:s7-1 -->
- [ ] Read MDPI Buildings' Instructions for Authors cover to cover <!-- id:s7-2 -->
- [ ] Set up Zotero or Mendeley; import the repo's core-10 reference list <!-- id:s7-3 -->
- [ ] Study one recently-published Buildings paper on a related topic for structure and tone calibration <!-- id:s7-4 -->
- [ ] Draft a one-paragraph novelty statement early — it anchors the whole introduction later <!-- id:s7-5 -->

### 08 — Auditing AI-generated research code & claims
- [ ] For every "✅ Complete" claim in the repo's docs, personally reproduce it once before relying on it <!-- id:s8-1 -->
- [ ] Treat every pre-filled numeric result (R², RMSE, timing estimates) as a placeholder until you've regenerated it yourself <!-- id:s8-2 -->
- [ ] Keep a personal, dated verification log — separate from the repo's own self-reported status files <!-- id:s8-3 -->
- [ ] When two of the repo's own documents disagree (Sheet 01 lists several), resolve to one source of truth and record why <!-- id:s8-4 -->

### 09 — Abaqus / SIMULIA — continuum FEA for concrete
- [ ] Complete Prep Project 05 <!-- id:s9-1 -->
- [ ] Understand what each CDP parameter (dilation angle, eccentricity, fb0/fc0 ratio, K, viscosity) physically represents, not just which defaults to type in <!-- id:s9-2 -->
- [ ] Understand continuum/solid element meshing trade-offs (element type, integration scheme, mesh density) against OpenSeesPy's 1D fiber-section approach <!-- id:s9-3 -->
- [ ] Compare embedded-rebar constraint modelling (Abaqus) against explicit fiber-layer reinforcement (OpenSeesPy) conceptually <!-- id:s9-4 -->
- [ ] Skim Abaqus's own concrete-modelling example problems (bundled with the Student Edition documentation) for calibration guidance <!-- id:s9-5 -->
