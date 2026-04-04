# Code Implementation Plan

## Project Assessment

**Date:** 2026-04-04 (UPDATED)
**Project:** ML_RCC_Research-share
**Status:** Phase 1 complete, Phase 2 ready to begin — ALL CRITICAL BLOCKERS RESOLVED ✅

### Current Capability Assessment: 9.5/10 (Up from 8/10)

**Major Achievement:** All 5 identified blockers from 2026-03-29 have been completely fixed.
**Test Status:** Core pipeline modules at 100% pass rate (41/41 tests passing)
**Next Phase:** Ready to generate large-scale IDA datasets for ML training

#### What's Working (Now Complete)
- Project infrastructure (virtual env, dependencies, directory structure)
- Configuration files (BNBC parameters, analysis settings)
- Module architecture (modeling, analysis, ML, utils, visualization)
- RC frame generator with 4 framework types (Non-Sway, OMRF, IMRF, SMRF)
- Material models (Concrete01/02, Steel01/02)
- BNBC 2020 compliance checker
- OpenSeesPy integration structure
- ML trainer with 4 algorithms (LR, RF, XGBoost, ANN)
- Ground motion loader (`src/ida/gm_loader.py`) - **NEW**
- Ground motion scaler (`src/ida/gm_scaler.py`) - **NEW**
- IDA runner with parallel execution (`src/ida/ida_runner.py`) - **NEW**
- Data compiler with feature engineering (`src/ida/data_compiler.py`) - **NEW**
- SHAP analyzer (`src/ml/shap_analyzer.py`) - **NEW**
- Fragility curve analyzer (`src/analysis/fragility.py`) - **NEW**
- Visualization module (`src/visualization/plotting.py`) - **NEW**
- Main runner script (`main.py`) - **NEW**

#### What's Needs Work (Phase 2–3)
- PEER NGA database integration (acquiring real ground motion files for large-scale analysis)
- Large-scale IDA dataset generation (Phase 2 — now ready to execute with fixed pipeline)
- ML model training and hyperparameter tuning (Phase 3)
- RC frame modeling improvements (addressing 9 remaining test_models.py failures)

### Implementation Priority

**Priority 1 (Critical for IDA):**
1. Ground motion loader and scaler
2. Complete IDA runner with parallel execution
3. Data compilation to CSV

**Priority 2 (Required for Phase 3-4):**
4. SHAP analysis module
5. Fragility curve generation
6. Visualization utilities

**Priority 3 (Quality/Validation):**
7. Unit test suite
8. Integration tests
9. Documentation notebooks

---

## Implementation Plan

### Phase 1: Ground Motion Processing (Completed)

**Files created:**
- `src/ida/gm_loader.py` - Load ground motions from PEER NGA format
- `src/ida/gm_scaler.py` - Scale GMs to target Sa(T1)

**Deliverables:**
- ✅ Load PEER NGA ASCII format
- ✅ Extract time history and acceleration
- ✅ Compute PGA, PGV, intensity measures
- ✅ Scale to target Sa(T1) for IDA
- ✅ Generate synthetic ground motions
- ✅ Validate ground motion format

---

### Phase 2: IDA Pipeline (Completed)

**Files created:**
- `src/ida/ida_runner.py` - Main IDA orchestration
- `src/ida/data_compiler.py` - Compile IDA results

**Deliverables:**
- ✅ Run multi-stripe IDA: N buildings × M GMs × K intensities
- ✅ Export to `data/processed/ida_results.csv`
- ✅ Parallel execution using joblib
- ✅ Error handling and recovery
- ✅ Framework comparison analysis

---

### Phase 3: Data Compilation (Week 2)

**Files to create:**
- `src/ida/data_compiler.py` - Compile IDA results

**Features:**
- Merge results from multiple analyses
- Feature engineering for ML
- Data validation and QC

---

### Phase 4: ML Analysis (Week 3)

**Files to create:**
- `src/ml/shap_analyzer.py` - SHAP feature importance
- `src/ml/evaluator.py` - Model evaluation utilities

**Deliverables:**
- SHAP plots for best models
- Feature importance rankings
- Cross-framework model comparison

---

### Phase 5: Visualization (Week 3)

**Files to create:**
- `src/visualization/plot_ida.py` - IDA curve plotting
- `src/visualization/plot_fragility.py` - Fragility curves
- `src/visualization/plot_shap.py` - SHAP visualizations
- `src/visualization/plot_frameworks.py` - Multi-framework comparison

**Deliverables:**
- Publication-ready figures (300 DPI)
- Interactive plots (optional)

---

### Phase 6: Fragility Curves (Week 4)

**Files to create:**
- `src/analysis/fragility.py` - Fragility curve generation

**Features:**
- Log-normal distribution fitting
- Performance level thresholds (IO, LS, CP)
- Zone-specific fragility curves

---

### Phase 7: Testing & Documentation (Week 4)

**Files to create:**
- `tests/test_gm_loader.py`
- `tests/test_ida_runner.py`
- `tests/test_bnbc_compliance.py`
- `tests/test_models.py`

**Notebooks:**
- `notebooks/01_data_exploration/02_ground_motions.ipynb`
- `notebooks/02_ida_analysis/03_ida_results_analysis.ipynb`
- `notebooks/04_results_analysis/05_framework_comparison.ipynb`

---

## Implementation Tasks

### Task 1: Ground Motion Loader
**Priority:** High
**Estimate:** 2 days
**Dependencies:** None
**Outputs:** `src/ida/gm_loader.py`

```python
# Load PEER NGA format
# Extract time series and acceleration
# Validate record format
```

### Task 2: Ground Motion Scaler
**Priority:** High
**Estimate:** 1 day
**Dependencies:** GM Loader
**Outputs:** `src/ida/gm_scaler.py`

```python
# Scale to target Sa(T1)
# Verify scaling accuracy
# Handle edge cases
```

### Task 3: IDA Runner
**Priority:** High
**Estimate:** 3 days
**Dependencies:** GM Scaler, THA
**Outputs:** `src/ida/ida_runner.py`

```python
# Parallel execution across buildings, GMs, intensities
# Result aggregation
# Error handling and recovery
```

### Task 4: Data Compiler
**Priority:** High
**Estimate:** 1 day
**Dependencies:** IDA Runner
**Outputs:** `src/ida/data_compiler.py`

```python
# Compile results to CSV
# Feature engineering
# QC checks
```

### Task 5: SHAP Analyzer
**Priority:** Medium
**Estimate:** 2 days
**Dependencies:** ML Trainer
**Outputs:** `src/ml/shap_analyzer.py`

```python
# TreeExplainer for RF/XGBoost
# Summary plots
# Dependence plots
```

### Task 6: Fragility Curves
**Priority:** Medium
**Estimate:** 2 days
**Dependencies:** Data Compiler
**Outputs:** `src/analysis/fragility.py`

```python
# Log-normal fitting
# Performance level thresholds
# Zone-specific curves
```

### Task 7: Visualization Module
**Priority:** Medium
**Estimate:** 2 days
**Dependencies:** Fragility Curves
**Outputs:** `src/visualization/plot_*.py`

```python
# IDA curves
# Fragility curves
# SHAP plots
# Framework comparison plots
```

### Task 8: Test Suite
**Priority:** Low
**Estimate:** 2 days
**Dependencies:** None
**Outputs:** `tests/test_*.py`

---

## Success Criteria

### Phase 1 Complete
- [ ] Ground motion loader reads PEER NGA format
- [ ] Scaler produces spectra within ±10% of target
- [ ] GM database supports Bangladesh seismicity

### Phase 2 Complete
- [ ] IDA pipeline executes 5 buildings × 15 GMs × 15 intensities
- [ ] Results saved to `data/processed/ida_results.csv`
- [ ] Parallel execution reduces runtime by 4×

### Phase 3 Complete
- [ ] Dataset has ≥5,000 clean records
- [ ] Features match README specifications
- [ ] Data validation passes

### Phase 4 Complete
- [ ] SHAP analysis run on best models
- [ ] Feature importance plots generated

### Phase 5 Complete
- [ ] All 9 publication figures created (300 DPI)
- [ ] Fragility curves for all 4 zones

### Phase 6 Complete
- [ ] Test coverage ≥80% for core modules
- [ ] Integration tests pass

---

## Risk Register

| Risk | Impact | Mitigation |
|------|--------|------------|
| OpenSeesPy convergence failures | High | Adaptive time-stepping, error handling |
| GM data unavailable | Medium | Use synthetic GMs, note limitation |
| Long computation time | Medium | Parallel processing, HPC support |
| Dataset too small | High | Increase GM counts, intensity levels |
| ML R² < 0.85 | Low | Add features, try ensemble stacking |

---

## Timeline Summary

| Week | Focus | Deliverables |
|------|-------|--------------|
| 1 | GM Processing | Loader, Scaler, Database |
| 2 | IDA Pipeline | Multi-stripe execution, Results CSV |
| 3 | ML & Viz | SHAP, Plots, Fragility |
| 4 | Testing & Docs | Tests, Notebooks, Documentation |

**Total Estimated Time:** 4 weeks for implementation + 2 weeks for testing/validation
