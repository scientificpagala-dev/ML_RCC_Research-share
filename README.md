# Research Master Plan
## ML-Based Seismic Drift Prediction of RC Buildings Under BNBC 2020
### Using OpenSeesPy IDA + Python Machine Learning

**Author:** [Your Name]
**Institution:** [Your University/Institute]
**Target Journal:** MDPI *Buildings* / Elsevier *Structures*
**Document Version:** 1.0 | Last Updated: 2025

---

## TABLE OF CONTENTS

1. [Ultimate Goal](#1-ultimate-goal)
2. [Paper Structure & Deliverables](#2-paper-structure--deliverables)
3. [Mathematical Framework](#3-mathematical-framework)
4. [Phase-by-Phase Execution Plan](#4-phase-by-phase-execution-plan)
5. [Structural Modelling Plan](#5-structural-modelling-plan)
6. [OpenSeesPy Coding Plan](#6-openseespy-coding-plan)
7. [IDA Analysis Plan](#7-ida-analysis-plan)
8. [Machine Learning Pipeline](#8-machine-learning-pipeline)
9. [Figures & Tables for Paper](#9-figures--tables-for-paper)
10. [Timeline & Milestones](#10-timeline--milestones)
11. [Tools & Software Stack](#11-tools--software-stack)
12. [References & Citation Strategy](#12-references--citation-strategy)
13. [Novelty Checklist](#13-novelty-checklist)
14. [Risk Register](#14-risk-register)

---

## 1. ULTIMATE GOAL

### 1.1 One-Line Research Statement
> Develop the first open-source, Python-native ML surrogate model that can instantly predict peak inter-story drift ratio (PIDR) of RC moment frame buildings designed under BNBC 2020, trained on OpenSeesPy incremental dynamic analysis data across all four seismic zones of Bangladesh.

### 1.2 Why This Matters
- BNBC 2020 updated seismic zones significantly from BNBC 2006 — existing fragility/ML studies are outdated
- Traditional IDA is computationally expensive (hours per building); an ML surrogate reduces this to milliseconds
- Bangladesh engineers have no fast tool for seismic drift screening under the new code
- Fully open-source pipeline → reproducible research → higher journal credibility

### 1.3 Research Objectives
- **Objective 1:** Build parametric RC SMRF models (5–15 stories) in OpenSeesPy compliant with BNBC 2020
- **Objective 2:** Run IDA with scaled ground motion records to generate a large seismic response dataset
- **Objective 3:** Train and compare ML models (LR, RF, XGBoost, ANN) to predict PIDR
- **Objective 4:** Generate seismic fragility curves for IO, LS, CP performance levels
- **Objective 5:** Identify key structural and seismic parameters driving drift using SHAP analysis
- **Objective 6:** Conduct comparative seismic performance analysis between Non-Sway, OMRF, IMRF, and SMRF configurations to identify the cost-benefit "sweet spot" of framework complexity vs. performance improvement across all BNBC 2020 seismic zones

### 1.4 Research Questions
1. Can ML models accurately predict PIDR from structural and seismic features with R² > 0.90?
2. Which features (period, zone, soil class, height) are most influential on seismic drift?
3. How do fragility curves differ across BNBC 2020 seismic zones (Z = 0.12 to 0.36)?
4. Does building height or seismic zone coefficient dominate drift response?
5. What is the seismic performance gradient between Non-Sway, OMRF, IMRF, and SMRF configurations across different building heights?
6. What is the optimal framework selection (Non-Sway/OMRF/IMRF/SMRF) balancing design complexity and seismic performance improvement across BNBC 2020 zones?

---

## 2. PAPER STRUCTURE & DELIVERABLES

### 2.1 Proposed Title Options
**Option A (Detailed):**
*"Machine Learning-Based Prediction of Seismic Inter-Story Drift in RC Moment Frames Designed Per BNBC 2020 Using OpenSeesPy Incremental Dynamic Analysis"*

**Option B (Concise):**
*"ML Surrogate Models for Seismic Drift Prediction of Bangladesh RC Buildings Under BNBC 2020"*

**Option C (Methods-forward):**
*"An Open-Source OpenSeesPy–Python Framework for Seismic Fragility and Drift Prediction of RC Buildings in Bangladesh"*

### 2.2 Paper Sections & Word Targets

| Section | Content | Target Words |
|---------|---------|-------------|
| Abstract | Problem, method, key results, conclusion | 250 words |
| 1. Introduction | Motivation, BNBC 2020 context, literature gap, objectives | 800–1000 |
| 2. Building Models | Parametric RC frame description (SMRF & OMRF), BNBC 2020 compliance | 700–900 |
| 3. OpenSeesPy Methodology | Fiber sections, materials, verification | 800–1000 |
| 4. Ground Motions & IDA | GM selection, scaling, IDA procedure | 600–800 |
| 5. Dataset & ML Framework | Feature engineering, model training, validation | 800–1000 |
| 6. Results | IDA curves, fragility, ML performance, SHAP | 1200–1500 |
| 6a. Framework Comparative Analysis | Non-Sway, OMRF, IMRF, SMRF seismic performance gradients, multi-framework cost-benefit analysis, optimal framework selection guide | 800–1000 |
| 7. Discussion | Implications, SMRF design rationale, practical use, framework selection guide | 600–800 |
| 8. Conclusions | Key findings, framework recommendations, future work | 300–400 |
| References | 45–65 citations | — |
| **Total** | | **~7000–8500 words** |

### 2.3 Target Journals

| Journal | Impact Factor | Open Access | Typical Review Time |
|---------|--------------|-------------|-------------------|
| *Buildings* (MDPI) | 3.1 | Yes (APC ~1800 CHF) | 4–6 weeks |
| *Structures* (Elsevier) | 3.9 | Optional | 8–12 weeks |
| *Engineering Structures* (Elsevier) | 5.5 | Optional | 10–16 weeks |
| *ASCE J. Structural Engineering* | 4.0 | Optional | 12–20 weeks |
| *Asian Journal of Civil Engineering* | 1.8 | No | 6–10 weeks |

**Recommendation:** Submit first to *Buildings* (MDPI) — fastest turnaround, open access, strong track record for this type of study.

---

## 3. MATHEMATICAL FRAMEWORK

### 3.1 BNBC 2020 Design Spectrum

The BNBC 2020 elastic design spectrum is defined as:

```
Sa(T) = SDS × [0.4 + 0.6(T/T0)]     for  0 ≤ T ≤ T0
Sa(T) = SDS                           for  T0 ≤ T ≤ Ts
Sa(T) = SD1 / T                       for  Ts ≤ T ≤ TL
Sa(T) = SD1 × TL / T²                 for  T > TL
```

Where:
- `SDS = (2/3) × Fa × 2.5 × Z`  — design short-period spectral acceleration
- `SD1 = (2/3) × Fv × Z`        — design 1-second spectral acceleration
- `T0  = 0.2 × SD1/SDS`         — lower transition period
- `Ts  = SD1/SDS`                — upper transition period
- `TL  = 6.0 s`                  — long-period transition
- `Fa, Fv` — site amplification factors (Table 2.5.4, BNBC 2020)

**Seismic Zone Coefficients (BNBC 2020):**

| Zone | Z | Representative City | Soil SD Fa | Soil SD Fv |
|------|---|---------------------|-----------|-----------|
| Zone 1 | 0.12 | Rajshahi | 1.6 | 2.4 |
| Zone 2 | 0.20 | Dhaka | 1.6 | 2.4 |
| Zone 3 | 0.28 | Chittagong | 1.6 | 2.4 |
| Zone 4 | 0.36 | Sylhet | 1.6 | 2.4 |

**BNBC 2020 Approximate Period:**
```
T_approx = Ct × H^x
where Ct = 0.0466, x = 0.90  (RC moment frames)
H = total building height (m)
```

**BNBC 2020 Base Shear:**
```
V = (Sa(T1) / R) × I × W
where:
  R = response reduction factor (5 for SMRF, 3 for IMRF)
  I = importance factor (1.0 residential, 1.25 office)
  W = seismic weight = DL + 0.25×LL
```

---

### 3.2 Incremental Dynamic Analysis (IDA)

IDA scales a ground motion record to increasing intensity levels and records the structural response at each level.

**Intensity Measure (IM):**
```
IM = Sa(T1, 5%)  — spectral acceleration at fundamental period T1
                   with 5% damping
```

**Damage Measure (DM):**
```
DM = PIDR = max over all stories { |Δu_i| / h_i }

where:
  Δu_i = relative horizontal displacement between story i and i-1
  h_i  = height of story i
```

**IDA Curve:**
- X-axis: Sa(T1, 5%) in units of g
- Y-axis: PIDR (dimensionless, expressed as %)
- One curve per ground motion record
- Multiple curves → IDA stripe → statistical summary

**Collapse Definition:**
```
Structural collapse is defined as PIDR ≥ 10%
(consistent with FEMA P695 and ATC-63)
```

**Median IDA Curve:**
```
Sa_median(PIDR = θ) = exp[ (1/n) × Σ ln(Sa_i(θ)) ]
```

---

### 3.3 Seismic Fragility Analysis

Fragility curve = probability that structural demand exceeds a performance threshold given a seismic intensity.

**Log-normal Fragility Model (Cloud Analysis Method):**

Step 1 — Fit log-linear regression in log-log space:
```
ln(PIDR) = a + b × ln(Sa) + ε
where ε ~ N(0, β²_D|IM)
```

Step 2 — Compute dispersion:
```
β_D|IM = std[ ln(PIDR_i) - (a + b×ln(Sa_i)) ]
```

Step 3 — Fragility curve:
```
P(LS | Sa) = Φ[ (ln(Sa) - ln(θ_LS)) / β ]

where:
  θ_LS = median Sa at which P(PIDR > PIDR_LS) = 0.50
  β    = total log-standard deviation (dispersion)
  Φ    = standard normal CDF
```

**Performance Levels (FEMA 356 / BNBC 2020 aligned):**

| Level | Abbreviation | PIDR Threshold | Expected Damage |
|-------|-------------|---------------|-----------------|
| Immediate Occupancy | IO | 1.0% | Minor cracking, fully functional |
| Life Safety | LS | 2.0% | Significant damage, occupants safe |
| Collapse Prevention | CP | 4.0% | Severe damage, collapse imminent |
| Collapse | CO | ≥ 10.0% | Total/partial collapse |

---

### 3.4 Machine Learning Framework

**Target Variable:**
```
y = ln(PIDR)   ← log-normal transformation (standard in earthquake engineering)
```

**Feature Vector (input to ML model):**
```
X = [n_stories, H_total, T1, bay_width, n_bays,
     col_b, col_h, beam_h, fc, fy, ρ_col,
     Z, R, I, soil_class (one-hot),
     ln(Sa)]

Total: ~15–18 features
```

**Model Performance Metrics:**
```
R² = 1 - Σ(yi - ŷi)² / Σ(yi - ȳ)²           (coefficient of determination)
RMSE = √[ (1/n) × Σ(yi - ŷi)² ]              (root mean squared error)
MAE  = (1/n) × Σ|yi - ŷi|                    (mean absolute error)
```

**K-Fold Cross-Validation:**
```
CV_score = (1/k) × Σ R²_fold_k    (k=5 or k=10)
```

**XGBoost Objective:**
```
L(θ) = Σ l(yi, ŷi) + Σ Ω(fk)
where Ω(f) = γT + (1/2)λ||w||²
(regularized tree ensemble)
```

**SHAP Feature Importance:**
```
φi = Σ [|S|!(p-|S|-1)!/p!] × [f(S∪{i}) - f(S)]
     S⊆F\{i}

Interpretation: φi is the marginal contribution of feature i
to the model prediction, averaged over all feature orderings.
```

---

### 3.5 Fiber Section Mechanics

**Concrete02 — Modified Kent-Scott-Park Model:**
```
Stress-strain for confined concrete (Mander model):
  fcc  = fc × [1 + 3.3 × (fl/fc)]        ← confined strength
  εcc  = εco × [1 + 5 × (fcc/fc - 1)]    ← confined strain

where:
  fl = 0.5 × ke × ρs × fyh               ← effective lateral confining pressure
  ke = confinement effectiveness factor
  ρs = volumetric ratio of transverse steel
```

**Steel02 — Menegotto-Pinto Model:**
```
σ = E0 × ε × [ (1-b)/√(1+|ε/εy|^R) + b ]

where:
  b  = strain hardening ratio (0.01)
  R  = transition curve parameter (18.5)
  εy = yield strain = Fy/E0
```

**Section Moment-Curvature:**
```
M = ∫∫ σ(ε) × y × dA     (integration over fiber areas)
φ = εtop / c              (curvature at any load step)
```

**Inter-story Drift Ratio:**
```
PIDR_story_i = |u_i - u_{i-1}| / h_i

where:
  u_i = absolute lateral displacement at floor i
  h_i = height of story i
```

---

### 3.6 Framework Comparative Analysis: Non-Sway, OMRF, IMRF, SMRF Seismic Performance

**Context:**
The research extends beyond SMRF to conduct a comprehensive comparative analysis of four RC moment frame types under BNBC 2020: Non-Sway Frames, Ordinary Moment Resisting Frames (OMRF), Intermediate Moment Resisting Frames (IMRF), and Special Moment Resisting Frames (SMRF). This analysis identifies performance gradients, cost-benefit trade-offs, and optimal design selections across building heights and seismic zones.

**Framework Definitions (BNBC 2020 Section 2.3.2 & Table 2.7.4):**

| Property | Non-Sway Frame | OMRF | IMRF | SMRF |
|----------|----------------|------|------|------|
| Response Reduction Factor R | 1.5 | 3.0 | 4.0 | 5.0 |
| Detailing Ductility | Low (2Δ) | Moderate (3Δ) | Moderate-High (5Δ) | High (8Δ) |
| Column Bar Spacing | 450 mm max | 300 mm max | 200 mm max | 150 mm max |
| Concrete Confinement | None | Light | Moderate | Heavy (Mander model) |
| Beam-Column Joint Shear Reinforcement | None | Minimal | Partial | Full double-layers |
| P-Delta Effects | Negligible | Considered | Considered | Considered |
| Design Base Shear | V = Sa×W | V = (Sa/R)×W, R=3 | V = (Sa/R)×W, R=4 | V = (Sa/R)×W, R=5 |

**Non-Sway Frames:** Buildings where lateral displacement is minimal and P-Delta effects are negligible. Typically low-rise structures or those with high stiffness. Analysis assumes no geometric nonlinearity.

**OMRF:** Ordinary Moment Resisting Frames with basic detailing requirements. Suitable for low to moderate seismic zones.

**IMRF:** Intermediate Moment Resisting Frames with enhanced detailing compared to OMRF but less stringent than SMRF. Balances cost and performance.

**SMRF:** Special Moment Resisting Frames with highest ductility and detailing requirements. Required for high seismic zones or tall buildings.

**Comparative Analysis Metrics:**

1. **Performance Gradient (ΔDrift):**
   ```
   Performance_Gradient_Framework_A_vs_B = (PIDR_B - PIDR_A) / PIDR_B × 100%
                        → measures % improvement of Framework A over Framework B
   ```

2. **Framework Complexity Index (FCI):**
   ```
   FCI_Framework = (Reinforcement_Volume / Reinforcement_Volume_NonSway) 
                 × (Fabrication_Hours / Fabrication_Hours_NonSway)
       → normalized measure of design/construction complexity relative to Non-Sway
   ```

3. **Cost-Benefit Ratio (Performance per Unit Complexity):**
   ```
   Cost_Benefit_Framework = Performance_Gradient_vs_NonSway / FCI_Framework
               → sweet spot = maximum value of this ratio across frameworks
   ```

4. **Framework-Shift Index (FSI):**
   ```
   FSI_Framework_vs_Reference = ln(PIDR_Framework / PIDR_Reference)
      → logarithmic performance transition measure relative to reference framework
   ```

**Comparative Analysis Methodology:**

1. **Model Creation:**
   - Create identical building archetype sets for all four frameworks: Non-Sway, OMRF, IMRF, SMRF
   - Same floor heights, bay widths, story counts (5, 7, 10, 12, 15)
   - Scale reinforcement ratios and detailing per BNBC 2020 design equations for each framework type
   - Non-Sway: no confinement, minimal reinforcement; OMRF: light confinement; IMRF: moderate; SMRF: heavy Mander confinement

2. **IDA Execution (Parallel):**
   - Run identical multi-stripe IDA for all four frameworks
   - Same ground motion records, same intensity range
   - For Non-Sway: exclude P-Delta effects in analysis
   - Extract PIDR curves for direct comparison across all types

3. **Performance Gradient Computation:**
   - Compute median IDA curves for each building class and framework type
   - Plot all four frameworks side-by-side for each building height
   - Calculate % improvement relative to Non-Sway at multiple intensity levels
   - Identify intensity ranges where higher framework types provide maximum advantage

4. **Visualization & Analysis:**
   - **Figure 6a: Multi-Framework Performance Gradient Graph** — PIDR vs Sa(T1) for all frameworks
     - X-axis: Spectral acceleration Sa (g)
     - Y-axis: PIDR (%)
     - Show curves for Non-Sway, OMRF, IMRF, SMRF
     - Color-code by framework type
   
   - **Figure 6b: Framework-Shift Visualization** — Performance vs Complexity Trade-off
     - X-axis: Framework Complexity Index (FCI)
     - Y-axis: Performance Gradient (%) or Cost-Benefit Ratio
     - Each point = one framework type × building height × zone combination
     - Show Pareto frontier of optimal framework selections
   
   - **Figure 6c: Zone-Dependent Framework Selection** — Performance gain varies by seismic zone
     - Subplots for Zones I–IV
     - Show performance gradient curves per zone for all frameworks
     - Demonstrate optimal framework choice based on zone and height
   
   - **Figure 6d: Fragility Curve Comparison** — P(LS | Sa) for all frameworks
     - Overlay fragility curves for Non-Sway, OMRF, IMRF, SMRF
     - Show rightward shift with increasing framework sophistication

5. **Statistical Comparison:**
   - ANOVA for PIDR differences across frameworks at each intensity
   - Correlation: building height vs performance gradient for each framework type
   - Fragility curve comparison: P(LS | Sa) across all frameworks

**Key Deliverables (Phase 5):**
- Framework model templates for Non-Sway, OMRF, IMRF, SMRF (5, 7, 10, 12, 15 stories each)
- IDA results for all framework types (matched ground motions and intensities)
- Multi-framework cost-benefit analysis table (FCI, Performance Gradient, Optimal Framework Selection for each building × zone)
- Performance gradient visualization figures (Figs 6a, 6b, 6c, 6d)
- Fragility curve overlay plots (all frameworks for each zone)
- Engineering recommendations: Framework selection matrix based on building height, seismic zone, and performance requirements

---

## 4. PHASE-BY-PHASE EXECUTION PLAN

### Phase 0 — Environment Setup *(Week 1)*
- [ ] Install Python 3.12 (not 3.14 — OpenSeesPy incompatible)
- [ ] Create virtual environment: `py -3.12 -m venv .venv`
- [ ] Install packages: `pip install openseespy numpy pandas matplotlib scipy scikit-learn xgboost shap joblib seaborn`
- [ ] Verify OpenSeesPy: `python -c "import openseespy.opensees as ops; ops.wipe(); print('OK')"`
- [ ] Set up VS Code with Python 3.12 interpreter
- [ ] Create project folder structure (see Section 6.1)

---

### Phase 1 — Literature Review *(Weeks 1–2)*
- [ ] Read and annotate 15 core papers (list in Section 12)
- [ ] Extract: methodology gaps, model parameters, IDA procedures used
- [ ] Write 500-word literature synthesis identifying your exact gap
- [ ] Confirm novelty: no ML+IDA+BNBC 2020 combination exists yet

---

### Phase 2 — Building Model Development *(Weeks 2–4)*
- [ ] Define 5 representative building archetypes (see Section 5)
- [ ] Code single building model in OpenSeesPy (2D SMRF)
- [ ] Verify modal periods against BNBC 2020 approximate formula
- [ ] Verify gravity analysis (check column axial loads match hand calc)
- [ ] Expand to parametric loop: 50–100 building variants
- [ ] Document all assumptions (units, confinement model, joint rigidity)

---

### Phase 3 — Ground Motion Selection *(Week 3)*
- [ ] Download 10–20 records from PEER NGA West2 database
- [ ] Select records matching Bangladesh tectonic setting (magnitude 6.0–7.5, R=20–150km)
- [ ] Scale to BNBC 2020 target spectrum using SeismoMatch or Python
- [ ] Verify spectral matching (within ±10% of target Sa)
- [ ] Store as .txt files: one column of acceleration in g, constant dt

---

### Phase 4 — IDA Campaign *(Weeks 4–7)*
- [ ] Code single IDA function (one building, one GM, scale range)
- [ ] Test with 1 building × 1 GM to verify convergence
- [ ] Add adaptive time-stepping for non-convergence
- [ ] Add collapse detection (PIDR ≥ 10%)
- [ ] Run full campaign: ~50 buildings × 15 GMs × 15 scale factors = ~11,250 runs
- [ ] Save all results to master CSV

---

### Phase 5 — Dataset Construction *(Week 7)*
- [ ] Clean dataset: remove collapse runs, check for outliers
- [ ] Feature engineering: compute ln(Sa), ln(PIDR), T1, H_total
- [ ] One-hot encode soil class
- [ ] Check dataset size: target ≥ 5,000 non-collapse data points
- [ ] EDA: plot distributions, correlation matrix, IDA curves

---

### Phase 6 — ML Training & Validation *(Weeks 8–9)*
- [ ] Split data: 80% train / 20% test (stratified by zone)
- [ ] Train 4 models: LR (baseline), RF, XGBoost, ANN
- [ ] Hyperparameter tuning: GridSearchCV for RF and XGBoost
- [ ] 5-fold cross-validation for all models
- [ ] SHAP analysis on best model
- [ ] Compare R², RMSE, MAE across all models

---

### Phase 7 — Fragility Curves *(Week 9)*
- [ ] Compute fragility curves per zone using cloud analysis
- [ ] Fit log-normal CDF (θ, β) at IO, LS, CP levels
- [ ] Plot fragility curves for all 4 BNBC zones
- [ ] Compare with published studies (if any exist for Bangladesh)

---

### Phase 8 — Writing *(Weeks 9–12)*
- [ ] Write Section 2 (building models) — easiest, start here
- [ ] Write Section 3 (OpenSeesPy methodology)
- [ ] Write Section 4 (ground motions and IDA)
- [ ] Write Section 5 (ML framework)
- [ ] Write Section 6 (results) — most important
- [ ] Write Section 1 (introduction) — write last
- [ ] Write abstract — very last
- [ ] Format references (use Mendeley or Zotero)

---

### Phase 9 — Review & Submission *(Weeks 12–14)*
- [ ] Self-review: check all equations, figures, table numbering
- [ ] Similarity check (Turnitin or iThenticate) — aim < 15%
- [ ] Format to journal template (download from journal website)
- [ ] Write cover letter (1 page max)
- [ ] Submit via journal portal

---

## 5. STRUCTURAL MODELLING PLAN

### 5.1 Building Archetypes (Parametric Matrix)

| ID | Stories | H (m) | Bay Width | n_Bays | Col (mm) | Beam (mm) | f'c (MPa) | Zone |
|----|---------|-------|-----------|--------|----------|-----------|-----------|------|
| B01 | 5 | 15 | 5.0 | 4 | 350×350 | 300×450 | 25 | Zone 2 |
| B02 | 8 | 24 | 5.0 | 4 | 400×400 | 300×500 | 25 | Zone 2 |
| B03 | 10 | 30 | 5.0 | 4 | 400×400 | 300×500 | 25 | Zone 2 |
| B04 | 12 | 36 | 5.0 | 4 | 450×450 | 300×550 | 28 | Zone 2 |
| B05 | 15 | 45 | 5.0 | 4 | 500×500 | 300×600 | 28 | Zone 2 |
| B06–B10 | Repeat B01–B05 | — | 6.0m bays | — | — | — | — | Zone 4 |
| B11–B15 | Repeat B01–B05 | — | 5.0m bays | — | — | — | — | Zone 1 |
| B16–B20 | Repeat B01–B05 | — | 5.0m bays | — | — | — | — | Zone 3 |

**Minimum target: 20 building archetypes × 4 zones = 80 unique models**

### 5.2 Material Properties

| Material | Property | Value | Standard |
|----------|----------|-------|----------|
| Concrete (unconfined) | f'c | 25 MPa (typ.), 28 MPa (high) | BNBC 2020 / ACI 318 |
| Concrete (confined core) | fcc | 1.3 × f'c (Mander) | ACI 318 |
| Steel | fy | 415 MPa (Grade 60) | BNBC 2020 |
| Steel | Es | 200,000 MPa | — |
| Steel | Strain hardening | 1% | — |

### 5.3 Load Cases (BNBC 2020)

```
Dead Load (DL):   Self-weight + 3.0 kN/m² (finishes + MEP)
Live Load (LL):   2.0 kN/m² (residential)
Wall Load:        10 kN/m (running load on beams)

BNBC 2020 Seismic Weight:
  W = DL + 0.25 × LL

Load Combinations for design:
  1. 1.4D
  2. 1.2D + 1.6L
  3. 1.2D + 1.0L ± 1.0E
  4. 0.9D ± 1.0E
```

### 5.4 OpenSeesPy Model Assumptions

| Assumption | Choice | Justification |
|-----------|--------|--------------|
| Frame type | 2D planar frame | Standard for parametric IDA studies |
| Element type | forceBeamColumn | Distributed plasticity, most accurate |
| Damping | 5% Rayleigh (modes 1 & 3) | Standard for RC buildings |
| Joint rigidity | Rigid (no joint element) | Simplification; note as limitation |
| Foundation | Fixed base | Conservative assumption |
| Slab | Not modeled (seismic weight via mass) | Standard 2D simplification |
| Geometric nonlinearity | PDelta (columns) | Required for tall buildings |
| P-Delta | Included via geomTransf PDelta | BNBC 2020 requirement |

---

## 6. OPENSEESPY CODING PLAN

### 6.1 Project Folder Structure

```
opensees_bnbc2020/
│
├── models/
│   ├── building_params.py       ← BuildingParams class
│   ├── rc_frame_model.py        ← RCFrameModel class (OpenSeesPy)
│   └── materials.py             ← Material definitions
│
├── analysis/
│   ├── gravity.py               ← Gravity analysis runner
│   ├── modal.py                 ← Modal analysis, period extraction
│   ├── pushover.py              ← Pushover analysis (optional)
│   └── ida_runner.py            ← IDA campaign manager
│
├── ground_motions/
│   ├── records/                 ← .txt files from PEER NGA
│   ├── gm_selector.py           ← Select and scale GMs
│   └── spectrum_match.py        ← Scale to BNBC 2020 target
│
├── data/
│   ├── raw/                     ← Raw IDA output CSVs
│   ├── processed/               ← Cleaned ML-ready dataset
│   └── ida_master_dataset.csv   ← Final compiled dataset
│
├── ml/
│   ├── feature_engineering.py   ← Build feature matrix
│   ├── train_models.py          ← Train RF, XGBoost, ANN, LR
│   ├── evaluate.py              ← R², RMSE, cross-validation
│   ├── shap_analysis.py         ← SHAP feature importance
│   └── fragility.py             ← Fragility curve generation
│
├── plots/
│   ├── plot_spectra.py          ← BNBC 2020 design spectra
│   ├── plot_ida_curves.py       ← IDA strip plots
│   ├── plot_fragility.py        ← Fragility curve plots
│   ├── plot_ml_results.py       ← Predicted vs actual, SHAP
│   └── figures/                 ← Output PNG files (300 dpi)
│
├── utils/
│   ├── units.py                 ← Unit conversion helpers
│   └── convergence.py           ← Adaptive time-stepping
│
├── main.py                      ← Master runner (runs full pipeline)
├── config.py                    ← All global settings
└── requirements.txt             ← Package list
```

### 6.2 Key Code Modules — Specification

#### `config.py` — Central settings
```python
# All parameters in one place — change here, propagates everywhere
STORY_HEIGHTS     = [5, 8, 10, 12, 15]
BAY_WIDTHS        = [5.0, 6.0]
ZONES             = ['Zone1', 'Zone2', 'Zone3', 'Zone4']
SOIL_CLASSES      = ['SC', 'SD']
SCALE_FACTORS     = [0.1, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.5, 1.8, 2.0, 2.5, 3.0]
COLLAPSE_DRIFT    = 0.10       # 10% PIDR = collapse
DAMPING_RATIO     = 0.05       # 5% Rayleigh
N_PARALLEL_JOBS   = -1         # Use all CPU cores
RESULTS_DIR       = 'data/raw'
DATASET_PATH      = 'data/ida_master_dataset.csv'
```

#### `ida_runner.py` — Core IDA loop
```python
def run_ida_campaign(building_list, gm_list, scale_factors, n_jobs=-1):
    """
    Run full IDA campaign in parallel.
    Returns: master DataFrame with all results
    """
    tasks = [(b, gm, sf) for b in building_list
                          for gm in gm_list
                          for sf in scale_factors]

    results = Parallel(n_jobs=n_jobs)(
        delayed(run_single_nltha)(b, gm, sf) for b, gm, sf in tasks
    )
    return pd.DataFrame([r for r in results if r is not None])
```

#### `train_models.py` — ML training
```python
MODELS = {
    'Linear Regression': LinearRegression(),
    'Random Forest'    : RandomForestRegressor(n_estimators=300, n_jobs=-1),
    'XGBoost'          : XGBRegressor(n_estimators=400, learning_rate=0.05),
    'ANN'              : MLPRegressor(hidden_layer_sizes=(128, 64, 32), max_iter=1000),
}
# Train all, compare R²/RMSE, save best model
```

---

## 7. IDA ANALYSIS PLAN

### 7.1 Ground Motion Selection Criteria (PEER NGA)

| Criterion | Target Value | Rationale |
|-----------|-------------|-----------|
| Magnitude (Mw) | 6.0 – 7.5 | Relevant for Bangladesh seismicity |
| Epicentral distance | 20 – 150 km | Near-to-moderate field |
| Site condition | Soil class C/D (NEHRP) | Matches BNBC 2020 SC/SD |
| Number of records | 15–20 records | Minimum for statistical validity |
| Recommended records | El Centro, Chi-Chi, Kobe, Northridge, Landers, Imperial Valley | Well-characterized |

### 7.2 Ground Motion Scaling Procedure
```
1. Compute target spectrum: BNBC 2020 Sa(T) for each zone
2. Compute record Sa(T1, 5%) from each GM's response spectrum
3. Scale factor = Sa_target(T1) / Sa_record(T1)
4. Apply scale factor to accelerogram
5. Verify: scaled spectrum within ±10% of target at T1
```

### 7.3 IDA Scale Factor Range

| Scale Factor | Expected Response | Purpose |
|-------------|-------------------|---------|
| 0.1 – 0.5g | Elastic / minor yielding | Define elastic behavior |
| 0.5 – 1.0g | Significant yielding | Design-level response |
| 1.0 – 2.0g | Severe damage | Beyond design basis |
| 2.0 – 3.0g | Approach collapse | Collapse fragility |
| > 3.0g | Collapse plateau | Stop analysis |

### 7.4 Convergence Strategy

```python
# Adaptive time-step algorithm (in order of attempts)
def analyze_adaptive(n_steps, dt_base):
    for dt in [dt_base, dt_base/2, dt_base/4, dt_base/8]:
        ok = ops.analyze(1, dt)
        if ok == 0:
            return True
    # If all fail → declare non-convergence → record as collapse
    return False
```

---

## 8. MACHINE LEARNING PIPELINE

### 8.1 Feature Engineering

| Feature | Symbol | How Computed | Unit |
|---------|--------|-------------|------|
| Number of stories | n | Building parameter | — |
| Total height | H | n × story_height | m |
| Fundamental period | T1 | OpenSeesPy eigen() | s |
| Bay width | L | Building parameter | m |
| Column width | b_col | Building parameter | mm |
| Column depth | h_col | Building parameter | mm |
| Beam depth | h_beam | Building parameter | mm |
| Concrete strength | f'c | Material | MPa |
| Steel yield strength | fy | Material | MPa |
| Column rebar ratio | ρ_col | Design parameter | — |
| Zone coefficient | Z | BNBC 2020 | — |
| Response reduction | R | BNBC 2020 | — |
| Importance factor | I | BNBC 2020 | — |
| Soil class | SC/SD | One-hot encoded | — |
| Log spectral accel. | ln(Sa) | From GM + scaling | ln(g) |
| **Target: log PIDR** | **ln(PIDR)** | **From IDA** | **—** |

### 8.2 Model Hyperparameters

**Random Forest:**
```python
RandomForestRegressor(
    n_estimators    = 300,
    max_features    = 'sqrt',
    min_samples_leaf= 2,
    max_depth       = None,   # grow fully
    random_state    = 42,
    n_jobs          = -1
)
```

**XGBoost:**
```python
XGBRegressor(
    n_estimators      = 400,
    learning_rate     = 0.05,
    max_depth         = 6,
    subsample         = 0.8,
    colsample_bytree  = 0.8,
    reg_alpha         = 0.1,
    reg_lambda        = 1.0,
    random_state      = 42
)
```

**ANN (MLP):**
```python
MLPRegressor(
    hidden_layer_sizes  = (128, 64, 32),
    activation          = 'relu',
    solver              = 'adam',
    learning_rate_init  = 0.001,
    max_iter            = 1000,
    early_stopping      = True,
    validation_fraction = 0.1,
    random_state        = 42
)
```

### 8.3 Validation Strategy

```
Total dataset split:
  ├── 80% Training set
  │    └── 5-fold cross-validation (hyperparameter tuning)
  └── 20% Test set (held out — NEVER seen during training)

Report on test set:
  - R² (coefficient of determination)
  - RMSE (root mean squared error in ln scale)
  - MAE (mean absolute error)
  - Predicted vs Actual scatter plot
```

### 8.4 SHAP Analysis (Feature Importance)

```python
import shap

explainer   = shap.TreeExplainer(best_model)     # RF or XGBoost
shap_values = explainer.shap_values(X_test)

# Global importance (mean |SHAP|)
shap.summary_plot(shap_values, X_test,
                  plot_type='bar', show=False)

# Detailed beeswarm plot
shap.summary_plot(shap_values, X_test, show=False)

# Dependence plot for top feature
shap.dependence_plot('ln_Sa', shap_values, X_test)
```

---

## 9. FIGURES & TABLES FOR PAPER

### 9.1 Required Figures (minimum 8 figures)

| Fig. | Title | Script | Section |
|------|-------|--------|---------|
| Fig. 1 | BNBC 2020 design spectra — all 4 zones (SD soil) | `plot_spectra.py` | §2 |
| Fig. 2 | Schematic of OpenSeesPy 2D RC frame model with fiber section detail | Manual/draw | §3 |
| Fig. 3 | IDA curves for representative building (10-story, Zone 2) | `plot_ida_curves.py` | §4 |
| Fig. 4 | IDA curves — effect of building height (5 vs 10 vs 15 stories) | `plot_ida_curves.py` | §4 |
| Fig. 5 | Seismic fragility curves — IO, LS, CP — Zone 2 Dhaka | `plot_fragility.py` | §4 |
| Fig. 6 | Seismic fragility comparison — all 4 BNBC zones at LS level | `plot_fragility.py` | §4 |
| Fig. 7 | ML model comparison: Predicted vs Actual PIDR (4 subplots) | `plot_ml_results.py` | §5 |
| Fig. 8 | SHAP beeswarm plot — feature importance for best model | `shap_analysis.py` | §5 |
| Fig. 9 | SHAP dependence plot — ln(Sa) and T1 vs PIDR | `shap_analysis.py` | §5 |

### 9.2 Required Tables (minimum 5 tables)

| Table | Title | Section |
|-------|-------|---------|
| Table 1 | Building archetype parameters (all 20 models) | §2 |
| Table 2 | OpenSeesPy model properties and assumptions | §3 |
| Table 3 | Selected ground motion records (name, Mw, R, PGA, scale factor) | §4 |
| Table 4 | ML model performance comparison (R², RMSE, MAE, training time) | §5 |
| Table 5 | Fragility parameters (θ, β) at IO/LS/CP for each zone | §4 |

---

## 10. TIMELINE & MILESTONES

```
WEEK 01 │ ████ Environment setup, literature reading
WEEK 02 │ ████ Literature review + gap statement
WEEK 03 │ ████ Single building model coded + verified
WEEK 04 │ ████ Parametric building loop (20+ models)
WEEK 05 │ ████ Ground motion selection and scaling
WEEK 06 │ ████ IDA single model — test run + debug
WEEK 07 │ ████ Full IDA campaign (parallel run)
WEEK 08 │ ████ Dataset cleaning + EDA + feature engineering
WEEK 09 │ ████ ML training + validation + SHAP
WEEK 10 │ ████ Fragility curves
WEEK 11 │ ████ Writing: Sections 2, 3, 4, 5
WEEK 12 │ ████ Writing: Section 6 (Results) + 7 (Discussion)
WEEK 13 │ ████ Writing: Introduction + Abstract
WEEK 14 │ ████ Final review + formatting + submission
```

### Key Milestones

| Milestone | Target Week | Success Criterion |
|-----------|------------|-----------------|
| M1: First model runs | Week 3 | T1 matches BNBC formula ± 15% |
| M2: First IDA curve | Week 6 | Monotonically increasing, no spurious collapse |
| M3: Dataset complete | Week 8 | ≥ 5,000 clean data points |
| M4: Best ML R² > 0.90 | Week 9 | XGBoost or RF achieves R² ≥ 0.90 |
| M5: All figures ready | Week 10 | All 9 figures at 300 dpi |
| M6: Draft complete | Week 13 | All sections written |
| M7: Submitted | Week 14 | Journal portal confirmation |

---

## 11. TOOLS & SOFTWARE STACK

### 11.1 Core Stack

| Tool | Version | Purpose | Install |
|------|---------|---------|---------|
| Python | **3.12** (not 3.14) | Core language | python.org |
| OpenSeesPy | 3.8.0.0 | Structural FEM + IDA | `pip install openseespy` |
| NumPy | latest | Numerical arrays | `pip install numpy` |
| Pandas | latest | Dataset management | `pip install pandas` |
| Matplotlib | latest | Plotting | `pip install matplotlib` |
| SciPy | latest | Statistics, fitting | `pip install scipy` |
| Scikit-learn | latest | ML models | `pip install scikit-learn` |
| XGBoost | latest | XGBoost model | `pip install xgboost` |
| SHAP | latest | Feature importance | `pip install shap` |
| Joblib | latest | Parallel processing | `pip install joblib` |
| Seaborn | latest | Statistical plots | `pip install seaborn` |

**One-line install:**
```bash
pip install openseespy numpy pandas matplotlib scipy scikit-learn xgboost shap joblib seaborn
```

### 11.2 Additional Tools

| Tool | Purpose | Cost |
|------|---------|------|
| VS Code | Code editor | Free |
| Jupyter Notebook | EDA and prototyping | Free |
| Mendeley / Zotero | Reference manager | Free |
| PEER NGA West2 | Ground motion database | Free (register) |
| SeismoMatch | GM spectrum matching | Free |
| Turnitin / iThenticate | Plagiarism check | May need institutional access |
| Overleaf | LaTeX writing (optional) | Free tier available |
| Git + GitHub | Version control | Free |

---

## 12. REFERENCES & CITATION STRATEGY

### 12.1 Must-Cite Papers (Core 10)

1. **Kazemi et al. (2023)** — ML + IDA for RC frames, 165 buildings, Archives of Civil Engineering → cite as primary IDA-ML methodology
2. **Kazemi et al. (2024)** — ML fragility with Python (XGBoost, ANN), Engineering Applications of AI → cite for ML+fragility pipeline
3. **Vamvatsikos & Cornell (2002)** — Original IDA paper, Earthquake Eng. Struct. Dyn. → always cite for IDA definition
4. **Mangalathu et al. (2020)** — ML for seismic fragility, Engineering Structures → cite for ML fragility approach
5. **BNBC 2020** — Bangladesh National Building Code, Part VI Chapter 2 → cite for all seismic parameters
6. **Momin et al. (2024)** — Seismic evaluation of RC building in Bangladesh, Springer → cite for regional context
7. **Rahman et al. (2026)** — BNBC 2020 RC building ETABS analysis, AJCE → cite as existing BNBC 2020 study without ML
8. **Mahi et al. (2025)** — Irregular RC buildings under BNBC 2020, ResearchGate → cite as Bangladesh study
9. **FEMA 356 (2000)** — Performance-based seismic design → cite for IO/LS/CP thresholds
10. **Solorzano et al. (2024)** — opseestools, SoftwareX → cite for OpenSeesPy + Python pipeline justification

### 12.2 Citation Format
- Use numbered references [1], [2] style (common in Buildings, Structures)
- Manage with Mendeley or Zotero
- Export to journal-specific format when submitting

---

## 13. NOVELTY CHECKLIST

Before submission, verify ALL boxes are checked:

- [ ] **First ML surrogate** for PIDR prediction of buildings designed per BNBC 2020
- [ ] **Covers all 4 BNBC 2020 seismic zones** (Z = 0.12 to 0.36) in one study
- [ ] **OpenSeesPy fiber section IDA** — more rigorous than ETABS/SAP2000 lumped plasticity
- [ ] **Fully open-source pipeline** — all code available (GitHub), fully reproducible
- [ ] **SHAP analysis** — physically interpretable feature importance for seismic engineering
- [ ] **Practical output** — engineers can predict PIDR in milliseconds without running FEM
- [ ] **Fragility curves per zone** — comparison of Zone 1 vs Zone 4 fragility not done before
- [ ] **Dataset published** — upload CSV to Zenodo or Mendeley Data (increases citations)

**Novelty statement for cover letter:**
> *"To the best of our knowledge, this is the first study to develop ML surrogate models for seismic inter-story drift prediction of RC moment-resisting frames designed under BNBC 2020, using an entirely open-source OpenSeesPy-based IDA framework. The study covers all four seismic zones of Bangladesh and provides fragility curves and a publicly available dataset — tools currently absent from the Bangladesh seismic engineering literature."*

---

## 14. RISK REGISTER

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| OpenSeesPy convergence failures in IDA | High | Medium | Adaptive time-stepping; classify non-convergence as collapse |
| Dataset too small (< 3000 rows) | Medium | High | Increase scale factor increments; add more GM records |
| ML R² < 0.85 | Low | High | Add more building variants; try ensemble stacking |
| Real GM records unavailable | Medium | Low | Use well-validated synthetic GMs; note as limitation |
| Python version incompatibility | High | Medium | Use Python 3.12 only; document in requirements.txt |
| Journal rejection on scope | Low | Medium | Pre-check aims and scope on journal website before submission |
| Computation time too long | Medium | Medium | Use joblib parallel; run on university HPC if available |

---

## APPENDIX A — Quick Reference Equations

```
T_approx  = 0.0466 × H^0.90              (BNBC 2020 period)
SDS       = (2/3) × Fa × 2.5 × Z        (design spectrum short-period)
SD1       = (2/3) × Fv × Z              (design spectrum 1-sec)
V_base    = (Sa(T1)/R) × I × W          (base shear)
PIDR_i    = |u_i - u_{i-1}| / h_i       (inter-story drift ratio)
P(LS|Sa)  = Φ[(ln(Sa) - ln(θ))/β]      (fragility probability)
ln(PIDR)  = a + b×ln(Sa)                (cloud regression)
R²        = 1 - SS_res/SS_tot           (model accuracy)
```

## APPENDIX B — Recommended Reading Order

1. BNBC 2020, Part VI, Chapter 2 (seismic provisions)
2. Vamvatsikos & Cornell (2002) — IDA methodology
3. Kazemi et al. (2023) — ML + IDA pipeline
4. Mangalathu et al. (2020) — ML fragility
5. OpenSeesPy documentation: https://openseespydoc.readthedocs.io

---

*Document maintained by [Your Name] | Version 1.0 | 2025*
*Update this document at each phase milestone.*
