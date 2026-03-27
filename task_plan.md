# Task Plan & Progress Tracking
## ML-Based Seismic Drift Prediction of RC Buildings Under BNBC 2020

**Date Created:** March 27, 2026  
**Last Updated:** March 27, 2026  
**Current Phase:** Phase 1 — Structural Modeling (Ready to Begin)  
**Python Version:** 3.12.1  
**Status:** ✅ **PROJECT INFRASTRUCTURE COMPLETE** | 📚 **ANALYSIS METHODS INTEGRATED**

---

## Executive Summary

The ML-Based Seismic Drift Research project is a 4-phase research initiative to develop Python-native machine learning surrogate models for predicting peak inter-story drift ratio (PIDR) of RC moment-resisting frame buildings designed under BNBC 2020.

**Key Analysis Methods Implemented:**
- **Response Spectrum Analysis (RSA)** — Design-level elastic analysis per BNBC 2020 / ASCE 7-22
- **Time History Analysis (THA)** — Nonlinear dynamic analysis under ground motion records
- **Pushover Analysis** — Static nonlinear (capacity) analysis with P-Delta effects
- **P-Delta Effects** — Geometric nonlinearity and stability index computation (θ)
- **Plastic Hinge Analysis** — Formation tracking, damage assessment, performance levels per FEMA P-58
- **Combined Methods** — Multi-stripe analysis, capacity spectrum method, ensemble analysis

**Current Status:** All project infrastructure + advanced analysis framework ready. Phase 1 implementation begins immediately.

---

## Completed Tasks (March 27, 2026)

### ✅ Environment Setup
- [x] Created Python 3.12.1 virtual environment (`.venv/`)
- [x] Installed 95+ project dependencies
- [x] Verified critical imports: OpenSeesPy, TensorFlow, XGBoost, SHAP

### ✅ Project Infrastructure
- [x] Created 27 directories (22 previous + 5 analysis-specific)
- [x] All Python modules with docstrings and references
- [x] Complete configuration files (BNBC, Analysis, ML settings)
- [x] `.gitignore`, `pyproject.toml`, `requirements.txt`

### ✅ NEW: Advanced Analysis Framework
- [x] `src/analysis/` module structure created with 6 analysis modules:
  - [x] `response_spectrum.py` — RSA implementation
  - [x] `time_history.py` — THA with dynamic integration (Newmark, HHT)
  - [x] `pushover.py` — Static nonlinear pushover
  - [x] `pdelta.py` — P-Delta effects & stability index
  - [x] `plastic_hinge.py` — Plastic hinge tracking & damage assessment
  - [x] `combined.py` — Multi-method combinations & ensemble analysis

### ✅ NEW: Extended Configuration Files
- [x] `config/analysis_config.yaml` — Expanded with 8 sections:
  - [x] **Response Spectrum Analysis** (modal extraction, combination methods, force distribution)
  - [x] **Time History Analysis** (Newmark integration, Rayleigh damping, scaling, nonlinear solver)
  - [x] **Pushover Analysis** (load patterns, control parameters, softening detection, performance point)
  - [x] **P-Delta Analysis** (stability index θ, geometric stiffness, instability detection)
  - [x] **Plastic Hinge Analysis** (hinge modeling, performance levels IO/LS/CP, acceptance criteria)
  - [x] **Combined Analysis** (CSM, multi-stripe, ensemble, uncertainty quantification)
  - [x] **Machine Learning** (existing — untouched)

- [x] `config/bnbc_parameters.yaml` — Expanded with:
  - [x] **Plastic Hinge Properties** (FEMA 356 / ASCE 41-23 moment-rotation relationships)
  - [x] **Performance Levels** (Operational, IO, LS, CP with PIDR thresholds)
  - [x] **Acceptance Criteria** (ASCE 41-23 chord rotation limits for beams, columns, shears, joints)

### ✅ NEW: Reference Standards Integration
- [x] Project integrated with comprehensive building codes:
  - BNBC 2020 (10 parts) — Bangladesh seismic design standard
  - ASCE 7-22 — US seismic design (for comparison)
  - ASCE 41-23 — Seismic evaluation & retrofit (24 MB, high-detail)
  - FEMA P-58 (Vols 1–7) — Performance-based seismic assessment
  - FEMA 356 — Prestandard for seismic rehabilitation
  - FEMA-440, 445, P-1050, P-2082 — Technical background documents
  - ACI Code, ASTM Standards (referenced for material design)

---

## Current Project Structure (Updated)

```
project/
├── src/
│   ├── modeling/                ✓ (RC frame base classes, materials, compliance)
│   ├── analysis/                ✓ NEW (6 advanced analysis modules)
│   │   ├── response_spectrum.py      (RSA implementation)
│   │   ├── time_history.py          (THA with dynamic integration)
│   │   ├── pushover.py              (Static nonlinear pushover)
│   │   ├── pdelta.py                (P-Delta & stability index)
│   │   ├── plastic_hinge.py         (Hinge tracking & damage)
│   │   └── combined.py              (Multi-method combinations)
│   ├── ida/                     ✓ (IDA pipeline — uses analysis modules)
│   ├── ml/                      ✓ (ML training & evaluation)
│   ├── utils/                   ✓ (Helpers & utilities)
│   └── visualization/           ✓ (Plotting & visualization)
├── config/
│   ├── bnbc_parameters.yaml     ✓ UPDATED (+ plastic hinge, performance levels)
│   └── analysis_config.yaml     ✓ UPDATED (+ 6 analysis method sections)
├── data/                         ✓ (raw, processed, metadata)
├── models/                       ✓ (openseespy, ml_models, checkpoints)
├── results/                      ✓ (figures, reports, tables)
├── notebooks/                    ✓ (01–04 analysis phases)
├── tests/                        ✓ (Unit & integration tests)
├── docs/
│   ├── BuildingCodes/
│   │   ├── BNBC/                (10 PDF files, BNBC 2020 standard)
│   │   ├── US/
│   │   │   ├── ASCE-7-22/       (3 files, seismic design)
│   │   │   ├── ACI_Code.pdf
│   │   │   └── ASTM-*.pdf
│   │   └── NL-Codes/
│   │       ├── ASCE 41-23.pdf   (24 MB, seismic rehabilitation)
│   │       ├── FEMA P-58/ (7 volumes)
│   │       ├── FEMA-*.pdf       (Technical background)
│   │       └── Fema356.pdf
│   └── (All standards referenced in code docstrings)
├── pyproject.toml               ✓ (Project metadata & tools)
├── requirements.txt             ✓ (Pinned dependencies)
├── .gitignore                   ✓ (Artifact exclusion)
└── task_plan.md                 ✓ THIS FILE (Progress tracking)
```

---

## Analysis Methodology: 4 Phases with 6 Methods

### Phase 1️⃣: Structural Modeling ← **CURRENT**
**Status:** ✅ Infrastructure Ready | ⏳ Implementation Pending
**Duration:** ~1–2 weeks  
**Deliverables:**
- [ ] Base RC frame models (5, 7, 10, 12, 15-story SMRF)
- [ ] Material definitions (Concrete01/02, Steel01/02)
- [ ] BNBC 2020 compliance checker
- [ ] Gravity load & lateral load application
- [ ] 5 building templates saved to `models/openseespy/`
- [ ] Verification notebook: `01_data_exploration/01_validate_frame_models.ipynb`

**Key Files:** `src/modeling/rc_frame.py`, `src/modeling/materials.py`, `src/modeling/bnbc_compliance.py`

---

### Phase 2️⃣: Analysis & Data Generation
**Status:** ⏳ Awaits Phase 1  
**Duration:** ~3–4 weeks  
**Analysis Methods Used:**  
1. **Response Spectrum Analysis (RSA)**
   - Modal analysis (eigenvalue extraction, 20 modes)
   - Design spectrum generation per BNBC 2020 Section 3.2
   - Modal response combination (CQC method)
   - Force distribution per BNBC 2020
   - Reference: `src/analysis/response_spectrum.py`

2. **Time History Analysis (THA)**
   - Nonlinear dynamic analysis under ground motion records
   - Newmark β integration scheme (γ=0.5, β=0.25)
   - Rayleigh damping for modal damping
   - Multi-stripe analysis: 15 intensity levels (0.05–1.50g)
   - Peak response tracking: PIDR, PGA, velocity, hysteresis
   - Reference: `src/analysis/time_history.py`, Config: `analysis_config.yaml` → `time_history_analysis`

3. **P-Delta Effects (Geometric Nonlinearity)**
   - Stability index θ computation per BNBC 2020 Section 3.2 / ASCE 7-22 Section 12.8.7
   - Corotational transformation in OpenSeesPy
   - Geometric stiffness matrix updates
   - Instability detection (θ_max allowed = 0.10 per BNBC)
   - Reference: `src/analysis/pdelta.py`, Config: `analysis_config.yaml` → `pdelta_analysis`

4. **Plastic Hinge Analysis** (Integrated with THA)
   - Hinge property assignment per FEMA 356 Section 5
   - Plastic hinge rotations tracked during THA
   - Performance level assessment:
     - **Immediate Occupancy (IO):** δ < 1.0%, chord rotation < 0.5%
     - **Life Safety (LS):** δ < 2.5%, chord rotation < 1.5–2.0%
     - **Collapse Prevention (CP):** δ < 4.0%, chord rotation < 2.5–3.0%
   - Damage index computation (Park-Ang method)
   - Reference: `src/analysis/plastic_hinge.py`, Config: `bnbc_parameters.yaml` → `plastic_hinge`, `performance_levels`, `acceptance_criteria`

**Deliverables:**
- [ ] Ground motion record preparation (PEER NGA database or equivalent)
- [ ] Ground motion scaling utilities per BNBC 2020 spectrum
- [ ] Multi-stripe THA pipeline (RSA + THA + P-Delta + Plastic Hinge)
- [ ] PIDR extraction & peak response computation
- [ ] Dataset: `data/processed/ida_results.csv`
  - Columns: building_id, zone, gm_id, intensity (Sa), pidr, pga, pv, residual_drift, hinge_rotations, damage_state, performance_level
  - Records: ~5,000–10,000+ (500 GMs × 15 intensities × 4 zones × 5 buildings)
- [ ] Data validation & QC reports
- [ ] Notebook: `02_ida_analysis/02_multi_stripe_tha_analysis.ipynb`

**Key Files:** `src/analysis/time_history.py`, `src/analysis/pdelta.py`, `src/analysis/plastic_hinge.py`, `src/analysis/combined.py`

**Configuration:**
- `analysis_config.yaml` → [`time_history_analysis`, `pdelta_analysis`, `plastic_hinge_analysis`, `multi_stripe`]
- `bnbc_parameters.yaml` → [`plastic_hinge`, `performance_levels`, `acceptance_criteria`]

---

### Phase 3️⃣: Machine Learning Pipeline
**Status:** ⏳ Awaits Phase 2 data  
**Duration:** ~2–3 weeks

**Analysis Method Used:**
5. **Combined Analysis: Multi-Stripe + Performance Assessment**
   - Ensemble learning from multiple analysis realizations
   - Cross-validation of THA vs Pushover results (optional advanced check)
   - Uncertainty quantification from ground motion variability (aleatory)

**Deliverables:**
- [ ] Feature engineering from structural + seismic parameters:
  - Structural: n_stories, period, height, column size, beam size, ρ_steel, fc', fy
  - Seismic: zone, pga, Sa @ T, distance to fault (if available)
  - Soil: site_class, Vs30
  - Target: PIDR, performance_level, hinge_damage_state
- [ ] Train/test split (80/20), validation (15% of training)
- [ ] Model training: LR, RF, XGBoost, ANN
- [ ] Hyperparameter optimization (Optuna, 50 trials)
- [ ] Model evaluation: R², RMSE, MAE, cross-validation
- [ ] SHAP analysis for feature importance
- [ ] Best model selection and save

**Key Files:** `src/ml/trainer.py`, `src/ml/evaluator.py`, `src/ml/shap_analyzer.py`  
**Output:** `models/ml_models/{best_model}`, `results/shap_analysis_*.png`

---

### Phase 4️⃣: Fragility Curves & Publication
**Status:** ⏳ Awaits Phase 3  
**Duration:** ~1–2 weeks

**Analysis Methods Used:**
6. **Combined: Pushover + Performance Assessment** (Optional advanced fragility)
   - Pushover analysis with P-Delta effects (static nonlinear)
   - Capacity spectrum method (RSA spectral displacement + Pushover capacity curve)
   - Link to ML predictions for rapid assessment

**Deliverables:**
- [ ] Performance level definitions (IO, LS, CP)
- [ ] Fragility curve generation using ML model:
  - P(Performance Level | Sa) for each zone
  - Three curves per zone: IO, LS, CP
- [ ] Visualization (PNG/PDF quality, 300 DPI)
- [ ] Publication-ready tables (Excel, LaTeX)
- [ ] Final research report & supplementary materials
- [ ] Reproducibility verification & parameter sensitivity

**Key Files:** `src/visualization/fragility_curves.py`  
**Output:** `results/figures/fragility_*.pdf`, `results/tables/results_summary.xlsx`

---

## Integration of Analysis Methods

### Architecture Diagram
```
Phase 1: Structural Modeling
    ↓
    RC Frame Templates (5–15 stories)
    ↓
─────────────────────────────────────────────────────
Phase 2: Analysis & Data Generation
    ↓
Response Spectrum Analysis (RSA)
    ↓ (Provides modal properties, base shear, design forces)
    ↓
Time History Analysis (THA) ← PRIMARY
    ├─ Newmark Integration (dt=0.005s)
    ├─ P-Delta Effects ← GEOMETRIC NONLINEARITY
    │   └─ Stability Index θ
    ├─ Plastic Hinge Analysis ← DAMAGE TRACKING
    │   ├─ Hinge rotations
    │   └─ Performance levels (IO/LS/CP)
    └─ Extract Peak Responses:
        ├─ PIDR (inter-story drift ratio)
        ├─ PGA, PV (peak acceleration, velocity)
        ├─ Hinge rotation states
        └─ Damage indices
    ↓
Pushover Analysis (Optional validation)
    ├─ Capacity curve (base shear vs.roof disp)
    ├─ Performance point identification
    └─ Compare with THA results
    ↓
Multi-Stripe Analysis (15 intensities × 500 GMs × 4 zones × 5 buildings)
    ↓
Dataset: ida_results.csv (~7,500–10,000 records)
    ↓
─────────────────────────────────────────────────────
Phase 3: Machine Learning Pipeline
    ↓
    Feature Engineering (24 structural + seismic features)
    ↓
    Model Training (LR, RF, XGBoost, ANN)
    ↓
    Best Model Selection (e.g., XGBoost with R²=0.91)
    ↓
    SHAP Feature Importance Analysis
    ↓
─────────────────────────────────────────────────────
Phase 4: Fragility Curves & Publication
    ↓
Generate Fragility Curves Using ML
    ├─ P(Performance Level | Seismic Intensity)
    └─ For all zones (I–IV)
    ↓
Publication Figures & Tables
    ↓
Research Paper (MDPI Buildings / Elsevier Structures)
```

---

## Reference Standards Mapping

| Analysis Method | Primary Reference | Supporting Standards | Config Section |
|---|---|---|---|
| **RSA** | BNBC 2020 §3.2, ASCE 7-22 §11 | FEMA-440 | `response_spectrum_analysis` |
| **THA** | BNBC 2020 §3.3, ASCE 7-22 §16.2 | FEMA P-58 Vol 1,2 | `time_history_analysis` |
| **Pushover** | ASCE 41-23 §3.4, FEMA 356 §4.4 | NIST GCR 17-917-45 | `pushover_analysis` |
| **P-Delta** | BNBC 2020 §3.2, ASCE 7-22 §12.8.7 | FEMA-350 | `pdelta_analysis` |
| **Plastic Hinge** | ASCE 41-23 §7, FEMA 356 §5 | FEMA P-58 (Performance Levels) | `plastic_hinge_analysis` |
| **Multi-Stripe** | FEMA P-58 Vol 1 | NIST GCR 17-917-45 | `combined_analysis` |

---

## Next Immediate Action Items

### 🚀 START: Phase 1 — Structural Modeling Implementation

#### Step 1: Review Configuration & Standards
```bash
cd /workspaces/ML_RCC_Research-share/project
source .venv/bin/activate

# Review BNBC parameters (seismic zones, materials, plastic hinge properties)
cat config/bnbc_parameters.yaml | head -100

# Review analysis configuration (all 6 methods + parameters)
cat config/analysis_config.yaml | grep -A 15 "^response_spectrum"

# Set up reference documents
ls -lh ../docs/BuildingCodes/BNBC/ | head -5
```

#### Step 2: Implement Base RC Frame Class (`src/modeling/rc_frame.py`)
- Create `RCFrame` class:
  ```python
  class RCFrame:
      def __init__(self, n_stories, story_height, zone, bnbc_params, column_section, beam_section)
      def create_model(self)  # Initialize OpenSeesPy with fiber sections
      def apply_gravity_loads(self)  # Floor loads per BNBC
      def validate_bnbc_compliance(self)  # Check code requirements
      def run_eigenvalue_analysis(self)  # Extract periods
      def save_model(self, filepath)
      def load_model(cls, filepath)
  ```

#### Step 3: Implement Material Class (`src/modeling/materials.py`)
- `ConcreteUnconfined` — Confined concrete (Concrete02)
- `ConcreteConfined` — For hoop reinf regions  
- `SteelRebar` — Steel reinforcement (Steel01/02)
- Load properties from `config/bnbc_parameters.yaml`

#### Step 4: Implement BNBC Compliance Checker (`src/modeling/bnbc_compliance.py`)
- Base shear calculation: V = Cs × W
- Period computation: Ta = 0.07 × h^0.75
- Story drift check: δ < 2.5% × story_height
- Stability index: θ = (P × Δ) / (V × h)
- Strength reduction factors (φ)

#### Step 5: Create 5 Building Templates
For each: 5-story, 7-story, 10-story, 12-story, 15-story
```python
from src.modeling import RCFrame
import yaml

with open('config/bnbc_parameters.yaml') as f:
    bnbc = yaml.safe_load(f)

for n_stories in [5, 7, 10, 12, 15]:
    frame = RCFrame(
        n_stories=n_stories,
        story_height=3.5,
        zone=3,  # Primary focus: Zone III (Dhaka)
        bnbc_params=bnbc,
        column_section={'width': 0.40, 'depth': 0.40},  # 40cm × 40cm
        beam_section={'width': 0.30, 'depth': 0.50}    #30cm × 50cm
    )
    frame.apply_gravity_loads()
    frame.validate_bnbc_compliance()
    frame.save_model(f'models/openseespy/frame_{n_stories}s_z3.json')
```

#### Step 6: Write Unit Tests (`tests/test_rc_frame.py`)
- Test model creation
- Gravity load application
- BNBC compliance (pass valid models, reject invalid)
- Period estimation within ±20% of expected
- Save/load integrity

#### Step 7: Create Verification Notebook
**File:** `notebooks/01_data_exploration/01_validate_frame_models.ipynb`
- Load 5 templates
- Plot mode shapes
- Verify periods vs analytical formula
- Visualize geometry & reinforcement
- Document all building properties

---

## Phase 2 Preparation (Preview)

Once Phase 1 is complete, Phase 2 will implement:

1. **Ground Motion Processing** (`src/ida/gm_scaler.py`)
   - Load GM records (PEER NGA database or equivalent for Bangladesh)
   - Scale to Sa @ T=0.5s using spectral matching or linear scaling
   - Multi-stripe: 15 intensity levels per GM

2. **Multi-Stripe THA Executor** (`src/analysis/combined.py` → `run_multi_stripe()`)
   - Loop: for each (building, GM, intensity):
     - Run THA with RSA modal properties from Phase 1
     - Apply P-Delta correction (stability index check)
     - Track plastic hinge rotations
     - Extract PIDR, PGA, damage state
     - Save to database

3. **Data Compilation** (`src/utils/data_compiler.py`)
   - Aggregate results from all analyses
   - Feature engineering (24 features from building + GM properties)
   - Output: `data/processed/ida_results.csv` (~10,000 rows)
   - Data quality checks (missing values, outliers, correlation analysis)

4. **QC Notebook** (`notebooks/02_ida_analysis/02_...

---

## Completed Tasks (March 27, 2026)

### ✅ Environment Setup
- [x] Created Python 3.12.1 virtual environment (`.venv/`)
- [x] Upgraded pip, setuptools, wheel to latest versions
- [x] Installed all 95+ project dependencies from `requirements.txt`
- [x] Verified critical imports: OpenSeesPy, TensorFlow, XGBoost, SHAP, scikit-learn

### ✅ Project Infrastructure
- [x] Created complete directory structure (22 directories):
  - `config/` — Configuration files for BNBC and analysis parameters
  - `src/` (5 submodules) — modeling, ida, ml, utils, visualization
  - `data/` (3 subdirs) — raw, processed, metadata
  - `models/` (3 subdirs) — openseespy, ml_models, checkpoints
  - `results/` (3 subdirs) — figures, reports, tables
  - `notebooks/` (4 subdirs) — organized by analysis phase
  - `tests/` — Unit and integration tests

### ✅ Configuration Files
- [x] `pyproject.toml` — Full project metadata, dependencies, tool configurations
  - Black, isort, mypy, pytest, coverage all configured
  - Optional dependency groups: dev, jupyter, ml, viz, docs, dev-all
  - Python 3.9+ support (running on 3.12.1)

- [x] `requirements.txt` — Pinned versions of 40+ packages including:
  - Scientific: NumPy, SciPy, Pandas, Scikit-learn
  - ML/DL: XGBoost, LightGBM, TensorFlow/Keras, SHAP
  - Structural: OpenSeesPy 3.8.0
  - Dev/Test: pytest, black, flake8, mypy, isort
  - Tracking: MLflow, Optuna
  - Viz: Matplotlib, Seaborn, Plotly, Folium

- [x] `config/bnbc_parameters.yaml` — BNBC 2020 reference data:
  - Seismic zones I–IV with PGA, Z_coeff, regional mappings
  - Site classifications A–E with Vs30 ranges and amplification factors
  - Building response modification factors (R) for RC SMRF
  - Design response spectrum parameters
  - Default material properties (concrete & steel)
  - Gravity load factors and floor height defaults

- [x] `config/analysis_config.yaml` — IDA and ML settings:
  - IDA parameters: IM (Sa @ T=0.5s), range (0.05–1.50g), time step (0.005s)
  - Convergence tolerances (1e-8), recording intervals
  - ML data split: 80/20 train/test, 5-fold CV
  - Model hyperparameters (RF, XGBoost, ANN)
  - SHAP analysis configuration
  - MLflow experiment tracking (optional)
  - Output format specifications (PNG @ 300 DPI, CSV/Excel tables)

### ✅ Python Module Structure
- [x] `src/__init__.py` — Top-level package with version info and submodule imports
- [x] `src/modeling/__init__.py` — OpenSeesPy RC frame models (SMRF)
- [x] `src/ida/__init__.py` — IDA analysis pipeline and ground motion processing
- [x] `src/ml/__init__.py` — ML model training, evaluation, SHAP analysis
- [x] `src/utils/__init__.py` — Helper functions and utilities
- [x] `src/visualization/__init__.py` — Plotting and visualization routines
- [x] `tests/__init__.py` — Test suite (ready for Phase 1 tests)

### ✅ Git & Documentation Setup
- [x] `.gitignore` — Comprehensive rules to exclude:
  - Virtual environments (`.venv/`)
  - Generated data (data/raw, data/processed, *.csv, *.h5)
  - Models and checkpoints (models/ml_models, *.pkl, *.joblib)
  - Results (results/figures, results/reports, *.png, *.pdf)
  - IDE files, Python cache, Jupyter checkpoints
  - Logs, temporary files, system files

- [x] `.github/copilot-instructions.md` — AI agent customization:
  - Project context, research goal, key features
  - Technology stack overview
  - Phase status and deliverables
  - Configuration file descriptions
  - Code conventions and patterns
  - Common workflows with code examples
  - Git practices and commit message format
  - Building code references & next steps

---

## Current Status & Verification

### Environment Status
```bash
✓ Python 3.12.1 active
✓ Virtual environment: /workspaces/ML_RCC_Research-share/project/.venv
✓ All 95+ dependencies installed successfully
✓ Critical imports verified:
  - openseespy.opensees
  - pandas
  - scikit-learn
  - tensorflow (CPU mode, no CUDA)
  - xgboost
  - shap
```

### Project Structure Status
```
project/
├── config/
│   ├── bnbc_parameters.yaml     ✓ (BNBC 2020 seismic zones, materials, design factors)
│   └── analysis_config.yaml     ✓ (IDA & ML hyperparameters)
├── src/
│   ├── modeling/                ✓ (Ready for Phase 1 - RC frame models)
│   ├── ida/                     ✓ (Ready for Phase 2 - IDA pipeline)
│   ├── ml/                      ✓ (Ready for Phase 3 - ML training)
│   ├── utils/                   ✓ (Ready for support functions)
│   └── visualization/           ✓ (Ready for plotting utilities)
├── data/
│   ├── raw/                     ✓ (Empty - ready for ground motion records)
│   ├── processed/               ✓ (Empty - ready for cleaned datasets)
│   └── metadata/                ✓ (Empty - ready for schema files)
├── models/
│   ├── openseespy/              ✓ (Ready for OpenSeesPy model templates)
│   ├── ml_models/               ✓ (Ready for trained models)
│   └── checkpoints/             ✓ (Ready for TensorFlow checkpoints)
├── results/
│   ├── figures/                 ✓ (Ready for plots & publication figures)
│   ├── reports/                 ✓ (Ready for analysis reports)
│   └── tables/                  ✓ (Ready for CSV/Excel exports)
├── notebooks/
│   ├── 01_data_exploration/     ✓ (Ready for EDA)
│   ├── 02_ida_analysis/         ✓ (Ready for IDA results)
│   ├── 03_ml_training/          ✓ (Ready for ML model development)
│   └── 04_results_analysis/     ✓ (Ready for final analysis)
├── tests/                       ✓ (Ready for pytest suite)
├── pyproject.toml               ✓ (Full metadata & tool configs)
├── requirements.txt             ✓ (All dependencies pinned)
└── .gitignore                   ✓ (Configured for large files, generated artifacts)
```

---

## Phase Breakdown & Timeline

### Phase 1: Structural Modeling ← **CURRENT**
**Status:** ✅ Infrastructure Ready | ⏳ Implementation Pending  
**Duration:** ~1–2 weeks  
**Deliverables:**
- [ ] `src/modeling/rc_frame.py` — Base RCFrame class
  - [ ] Properties: n_stories, story_height, column_section, beam_section, period
  - [ ] Methods: apply_gravity_loads(), apply_lateral_loads(), analyze(), save_model()
  - [ ] Constructor validation and error handling
  
- [ ] `src/modeling/materials.py` — Material definitions
  - [ ] Concrete01/Concrete02 for unconfined & confined concrete
  - [ ] Steel01/Steel02 for reinforcement
  - [ ] Default BNBC material properties from config
  
- [ ] `src/modeling/bnbc_compliance.py` — Design verification
  - [ ] Base shear calculation per BNBC 2020
  - [ ] Period estimation (Ta = Ct * h^0.75)
  - [ ] Story drift validation (max 2.5% for RC SMRF)
  - [ ] Strength reduction factor application (φ)
  
- [ ] Implement 5 building templates:
  - [ ] 5-story SMRF (T ≈ 0.5s)
  - [ ] 7-story SMRF (T ≈ 0.7s)
  - [ ] 10-story SMRF (T ≈ 1.0s)
  - [ ] 12-story SMRF (T ≈ 1.2s)
  - [ ] 15-story SMRF (T ≈ 1.5s)
  
- [ ] OpenSeesPy model setup:
  - [ ] Fiber sections for columns (Concrete + rebars)
  - [ ] Fiber sections for beams (Concrete + rebars)
  - [ ] Geometric nonlinearity (P-Delta transformation)
  - [ ] Node recorders (displacement, drift)
  - [ ] Element recorders (force, stress)
  
- [ ] Model verification:
  - [ ] Verify modal properties (period, mode shapes)
  - [ ] Gravity analysis stability
  - [ ] Lateral load distribution
  - [ ] Conservation of mass and energy
  
- [ ] Save templates:
  - [ ] models/openseespy/frame_5s_z1.json → models/openseespy/frame_15s_z4.json
  - [ ] Each zone × story combination

**Key Files:** `src/modeling/rc_frame.py`, `src/modeling/materials.py`, `src/modeling/bnbc_compliance.py`  
**Dependencies:** OpenSeesPy, PyYAML, NumPy, Pandas  
**Tests:** `tests/test_rc_frame.py`, `tests/test_bnbc_compliance.py`

---

### Phase 2: IDA Analysis & Data Generation
**Status:** ⏳ Awaits Phase 1  
**Duration:** ~2–3 weeks  
**Deliverables:**
- Ground motion record preparation (PEER, NGA database)
- Ground motion scaling per BNBC 2020 response spectrum
- IDA pipeline implementation
- PIDR extraction for all building-zone combinations
- Dataset compilation (CSV, HDF5 format)
- Data validation & QC checks

**Key Files:** `src/ida/ida_analysis.py`, `src/ida/gm_scaler.py`  
**Output:** `data/processed/ida_results.csv` (~20,000 records)

---

### Phase 3: Machine Learning Pipeline
**Status:** ⏳ Awaits Phase 2 data  
**Duration:** ~2–3 weeks  
**Deliverables:**
- Feature engineering (structural + seismic)
- Train/test set preparation
- Model training: LR, RF, XGBoost, ANN
- Hyperparameter optimization (Optuna)
- Model evaluation (R², RMSE, MAE, cross-validation)
- SHAP analysis for feature importance
- Best model selection and save

**Key Files:** `src/ml/trainer.py`, `src/ml/evaluator.py`, `src/ml/shap_analyzer.py`  
**Output:** `models/ml_models/{best_model}`, `results/shap_analysis_*.png`

---

### Phase 4: Fragility Curves & Publication
**Status:** ⏳ Awaits Phase 3  
**Duration:** ~1–2 weeks  
**Deliverables:**
- Performance level definitions (IO, LS, CP)
- Fragility curve generation
- Visualization (PNG, PDF quality)
- Publication-ready tables
- Paper figures and results summary
- Final report & reproducibility verification

**Key Files:** `src/visualization/fragility_curves.py`  
**Output:** `results/figures/fragility_*.pdf`, `results/tables/results_summary.xlsx`

---

## Next Immediate Action Items

### 🚀 START HERE: Phase 1 — Begin Structural Modeling (This Week)

#### Step 1: Review BNBC Configuration
```bash
cd /workspaces/ML_RCC_Research-share/project
source .venv/bin/activate
cat config/bnbc_parameters.yaml  # Review seismic zones & design factors
cat config/analysis_config.yaml   # Review IDA parameters
```

#### Step 2: Create Base RC Frame Class (`src/modeling/rc_frame.py`)
**Implement:**
- `RCFrame` class with:
  - Constructor: `__init__(n_stories, story_height, zone, bnbc_params, ...)`
  - Properties for column/beam dimensions, rebar ratios
  - Methods: `apply_gravity_loads()`, `validate_bnbc_compliance()`, `save_model()`
  - Fiber section definitions (Concrete01/02 + Steel01/02)
  - Geometric nonlinearity (P-Delta, corotational transformation)

**Pseudocode:**
```python
from openseespy import opensees as ops
import yaml

class RCFrame:
    def __init__(self, n_stories, story_height, zone, bnbc_params):
        self.n_stories = n_stories
        self.story_height = story_height
        self.zone = zone
        self.bnbc_params = bnbc_params
        self.model = None
    
    def create_model(self):
        # Initialize OpenSeesPy model
        ops.wipe()
        ops.model('basic', '-ndm', 2, '-ndf', 3)
        # Define materials, sections, elements, constraints
        # ... (see detailed implementation tasks below)
    
    def apply_gravity_loads(self):
        # Apply floor loads + self-weight
        # Run eigenvalue analysis for period verification
    
    def validate_bnbc_compliance(self):
        # Check: base shear, story drift < 2.5%, mass distribution
    
    def save_model(self, filepath):
        # Save model to JSON or pickle for Phase 2 reuse
```

#### Step 3: Create BNBC Material Definitions (`src/modeling/materials.py`)
**Implement:**
- Concrete material (Concrete01 with softening)
- Steel rebar material (Steel01 with Bauschinger effect)
- Default properties from `config/bnbc_parameters.yaml`
- Helper functions for expected strength calculations

#### Step 4: Create BNBC Compliance Checker (`src/modeling/bnbc_compliance.py`)
**Implement:**
- Base shear calculator: V = Cs × W
- Period formula: Ta = 0.07 × h^0.75 (for RC)
- Story drift check: δmax ≤ 0.025 × story_height
- Design force checks (flexure, shear, torsion)

#### Step 5: Create 5 Building Templates
**For each heights (5, 7, 10, 12, 15 stories):**
1. Instantiate `RCFrame` with typical dimensions:
   - Column: 400mm × 400mm RC section
   - Beam: 300mm × 500mm RC section
   - Rebar: 2% for columns, 1.5% for beams
   - f'c = 28 MPa (typical Bangladesh RC)
   
2. Apply gravity loads and verify period
3. Save as template: `models/openseespy/frame_{n}s_z{zone}.json`
4. Document in notebook: `notebooks/01_data_exploration/01_validate_frame_models.ipynb`

#### Step 6: Write Unit Tests (`tests/test_rc_frame.py`)
**Test:**
- Model instantiation with valid/invalid inputs
- Gravity load application
- BNBC compliance for expected violations
- Save/load cycle integrity
- Period estimation accuracy

#### Step 7: Documentation
**Create:**
- Docstrings for all classes and methods
- `docs/phase1_structural_modeling.md` with figures
- Example usage notebook: `notebooks/01_data_exploration/01_validate_frame_models.ipynb`

---

## Key Reminders & Best Practices

### Code Quality
- Follow **PEP 8** and **Google Python style guide**
- Use **type hints** for function signatures
- Write **comprehensive docstrings** (parameter types, return types, usage examples)
- Run **black** for formatting: `black src/`
- Run **flake8** for linting: `flake8 src/`
- Run **mypy** for type checking: `mypy src/`

### Testing
- Use **pytest** for unit tests: `pytest tests/ -v`
- Target **>80% code coverage**: `pytest tests/ --cov=src --cov-report=html`
- Fixtures for reusable test data (e.g., `bnbc_config`, `sample_frame`)
- Integration tests for multi-module workflows

### Version Control
- **Commit frequently** with descriptive messages:
  ```
  Phase 1: Create RCFrame class with gravity load application
  
  - Initialize OpenSeesPy model with nodeID tagging scheme
  - Define Concrete01/Steel01 materials from BNBC defaults
  - Implement gravity load application per floor height
  - Add validation against BNBC 2020 design constraints
  ```

- **Push to GitHub** after completing each deliverable
- Use **task_plan.md** to track progress

### File Organization
- Keep models in **`src/modeling/`** (no monolithic scripts)
- Use **relative imports**: `from src.modeling import RCFrame`
- Load configs via **PyYAML**: `yaml.safe_load(open('config/...'))`
- Save results to **`results/`** (never hardcode paths)

### OpenSeesPy Tips
- **Node IDs:** `floor*100 + node_num` (e.g., floor 3, node 2 → 302)
- **Element IDs:** Column: `floor*1000 + col_num`, Beam: `floor*2000 + beam_num`
- **Fiber sections:** Use at least 8×8 fibers per cross-section for accuracy
- **Recorders:** Record displacement every 10 steps minimum; use `node()` recorder
- **Analysis:** Use **Newton–Raphson** with **NormDispIncr** test (tol = 1e-8)

### Data Integrity
- Always validate BNBC parameters are loaded correctly
- Check that self-weight + live loads total correctly (sum over all floors)
- Verify period is reasonable: T ≈ 0.07 × h^0.75 (within ±20%)
- Ensure modal properties match building classification

---

## Success Criteria for Phase 1 Completion

✅ **Code:**
- [ ] `src/modeling/rc_frame.py` implemented and tested
- [ ] 5 building templates created and saved
- [ ] 80%+ test coverage for modeling module
- [ ] All code passes black, flake8, mypy checks

✅ **Documentation:**
- [ ] Docstrings on all public functions
- [ ] Example usage in `notebooks/01_data_exploration/01_validate_frame_models.ipynb`
- [ ] Phase 1 progress documented in this task_plan.md

✅ **Verification:**
- [ ] Modal periods within expected range (T ≈ 0.07h^0.75)
- [ ] Gravity analysis converges without warnings
- [ ] BNBC compliance checks pass for valid models
- [ ] Models save/load cycle works correctly

✅ **Git:**
- [ ] All code committed with descriptive messages
- [ ] `.gitignore` preventing accidental commits of generated files
- [ ] README.md updated with Phase 1 completion status

---

## Resources & References

### Project Documentation
- **README.md** — Full research master plan, objectives, timeline
- **recreation.md** — Directory structure, dependencies, setup guide
- `.github/copilot-instructions.md` — Agent customization with full context

### BNBC 2020 References
- **docs/BuildingCodes/BNBC/** — Official Bangladesh National Building Code seismic provisions
- Key sections:
  - 3.2 — Seismic hazard and ground motion
  - 6.3 — Design response spectra
  - 8.3 — RC moment-resisting frame design

### OpenSeesPy Documentation
- **https://openseespydoc.readthedocs.io/**
- Key examples:
  - Fiber sections: `https://openseespydoc.readthedocs.io/en/latest/src/fiberLineIntegration.html`
  - Material models: `https://openseespydoc.readthedocs.io/en/latest/src/uniaxialMaterials.html`
  - Nonlinear analysis: `https://openseespydoc.readthedocs.io/en/latest/src/geomTimeSeries.html`

### ML & ML Interpretability
- **SHAP:** https://shap.readthedocs.io/ (focus on TreeExplainer for RF/XGBoost)
- **Optuna:** https://optuna.readthedocs.io/ (hyperparameter tuning)
- **TensorFlow:** https://www.tensorflow.org/api_docs (for ANN training)

---

## Contact & Support

- **Project Lead:** Research Team
- **Supervisor:** [Your Advisor]
- **Repository:** ML_RCC_Research-share (GitHub)
- **Status Updates:** Update this task_plan.md weekly

---

## Integration of Analysis Methods

### Full Workflow: 6 Methods Across 4 Phases

```
PHASE 1: STRUCTURAL MODELING
    ↓
RC Frame Creation (Fiber Sections) + BNBC Compliance ✅
    ↓
5 Building Templates Saved (5, 7, 10, 12, 15-story)
    ↓
===================================================================
PHASE 2: ANALYSIS & DATA GENERATION (Multiple Methods)
    ↓
1. RESPONSE SPECTRUM ANALYSIS (RSA)
   └─ Modal property extraction
   └─ Design spectrum per BNBC 2020 §3.2
   └─ Peak story forces & drifts (elastic)
    ↓
2. TIME HISTORY ANALYSIS (THA) ← PRIMARY METHOD
   ├─ Newmark β integration (Δt=0.005s)
   ├─ Rayleigh damping (ξ=5%)
   ├─ Nonlinear solver (Newton-Raphson, tol=1e-8)
   └─ Extract: PIDR, PGA, PV, displacements
    ↓
3. P-DELTA EFFECTS (GEOMETRIC NONLINEARITY)
   ├─ Corotational transformation in OpenSeesPy
   ├─ Stability index θ = (P·Δ)/(V·h)
   ├─ θ_max check: 0.10 per BNBC 2020
   └─ Instability detection
    ↓
4. PLASTIC HINGE ANALYSIS
   ├─ Define hinges per FEMA 356 §5
   ├─ Track hinge rotations during THA
   ├─ Performance levels: IO (0.5%), LS (1.5%), CP (2.5%)
   ├─ Damage index: Park-Ang method
   └─ Accept/reject per ASCE 41-23 criteria
    ↓
5. MULTI-STRIPE EXECUTION
   ├─ 500 ground motions
   ├─ 15 intensity levels (0.05–1.50g Sa)
   ├─ 4 seismic zones
   ├─ 5 buildings
   └─ ~7,500–10,000 THA analyses total
    ↓
6. ENSEMBLE DATA COMPILATION
   └─ Results → data/processed/ida_results.csv
      (building_id, zone, gm_id, intensity, pidr, pga, 
       damage_state, performance_level, ...)
    ↓
===================================================================
PHASE 3: MACHINE LEARNING PIPELINE
    ↓
    Feature Engineering (24 features)
    + Model Training (LR, RF, XGBoost, ANN)
    + SHAP Feature Importance Analysis
    ↓
    Best Model: XGBoost (R² ≥ 0.90)
    ↓
===================================================================
PHASE 4: FRAGILITY CURVES & PUBLICATION
    ↓
    Generate Fragility Curves: P(Performance Level | Sa)
    + Publish 4 Zones × 3 Performance Levels = 12 Curves
    + Create Publication Figures & Tables
    ↓
    Research Paper (MDPI Buildings)
    6000–7500 words, 8–12 figures, 40–55 citations
```

---

## Standards Mapping: Methods to References

| Method | Standards | Config Section | Phase |
|--------|-----------|---|---|
| **RSA** | BNBC 2020 §3.2, ASCE 7-22 §11 | `response_spectrum_analysis` | 1–2 |
| **THA** | BNBC 2020 §3.3, ASCE 7-22 §16.2 | `time_history_analysis` | **2** |
| **Pushover** | ASCE 41-23 §3.4, FEMA 356 §4 | `pushover_analysis` | 4 (optional) |
| **P-Delta** | BNBC 2020 §3.2, ASCE 7-22 §12.8.7 | `pdelta_analysis` | **2** (THA) |
| **Plastic Hinge** | ASCE 41-23 §7, FEMA 356 §5 | `plastic_hinge_analysis` | **2** (THA) |
| **Multi-Stripe** | FEMA P-58 Vol 1-2 | `combined_analysis` → `multi_stripe` | **2** |

---

## Configuration Quick Reference

### Key Parameters by Analysis Method

**Response Spectrum Analysis** (`analysis_config.yaml`)
```yaml
response_spectrum_analysis:
  modal_analysis:
    n_modes: 20                    # Extract 20 modes
    method: "Shift-and-Invert"
  spectrum:
    type: "BNBC 2020"
    damping_ratio: 0.05            # 5% damping
    site_class: "D"
  modal_combination:
    method: "CQC"                  # Complete Quadratic Combination
```

**Time History Analysis** (`analysis_config.yaml`)
```yaml
time_history_analysis:
  integration:
    method: "Newmark"
    gamma: 0.5
    beta: 0.25                     # β = 0.25 for linear interpolation
    rayleigh_b: 0.0                # Stiffness-proportional damping
  time_integration:
    dt: 0.005                      # 5 ms time step
    duration: 30.0                 # 30 seconds analysis time
scaling:
    intensity_levels: [0.05, 0.10, ..., 1.50]  # 15 levels
```

**P-Delta Analysis** (`analysis_config.yaml`)
```yaml
pdelta_analysis:
  transformation: "Corotational"   # Large displacement formulation
  stability_index:
    theta_max_allowed: 0.10        # Per BNBC 2020: θ ≤ 0.10
    warn_threshold: 0.05
```

**Plastic Hinge Analysis** (`bnbc_parameters.yaml`)
```yaml
performance_levels:
  structural:
    immediate_occupancy:
      pidr_max: 0.010              # 1% inter-story drift
    life_safety:
      pidr_max: 0.025              # 2.5%
    collapse_prevention:
      pidr_max: 0.040              # 4%

acceptance_criteria:
  flexural:
    beam_chord_rotation_io: 0.010  # 1% radians (Immediate Occupancy)
    beam_chord_rotation_ls: 0.020  # 2% (Life Safety)
    beam_chord_rotation_cp: 0.030  # 3% (Collapse Prevention)
```

---

## Change Log

| Date | Component | Status | Notes |
|------|-----------|--------|-------|
| 2026-03-27 | Infrastructure | ✅ Complete | Dirs, config, deps, docs, AI instructions |
| 2026-03-27 | Analysis Framework | ✅ Complete | 6 analysis modules, extended configs |
| 2026-03-27 | Phase 1 | ⏳ Ready | Begin RC frame modeling |
| TBD | Phase 1 | ⏳ Pending | Base class + 5 templates |
| TBD | Phase 2 | ⏳ Pending | RSA + THA + P-Delta + Plastic Hinge |
| TBD | Phase 3 | ⏳ Pending | ML training (4 models) |
| TBD | Phase 4 | ⏳ Pending | Fragility curves + publication |

---

**Document Version:** 2.0  
**Last Updated:** March 27, 2026, 16:00 UTC  
**Status:** ✅ **FULLY INTEGRATED** — Infrastructure Complete + Analysis Methods Framework Ready  
**Components Ready:** 27 directories, 6 analysis modules, extended configs, 30+ reference standards  
**Next Action:** Begin Phase 1 — RC Frame Structural Modeling  
**Next Review:** Mid-April 2026 (Phase 1 completion)
