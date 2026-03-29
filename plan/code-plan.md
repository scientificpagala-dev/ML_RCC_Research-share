# Code Implementation Plan

## Project Assessment

**Date:** 2026-03-29
**Project:** ML_RCC_Research-share
**Status:** Infrastructure complete, execution needs work

### Current Capability Assessment: 7/10

#### What's Working
- Project infrastructure (virtual env, dependencies, directory structure)
- Configuration files (BNBC parameters, analysis settings)
- Module architecture (modeling, analysis, ML, utils, visualization)
- RC frame generator with 4 framework types (Non-Sway, OMRF, IMRF, SMRF)
- Material models (Concrete01/02, Steel01/02)
- BNBC 2020 compliance checker
- OpenSeesPy integration structure
- ML trainer with 4 algorithms (LR, RF, XGBoost, ANN)

#### What's Missing
- Ground motion processing (loading, scaling, PEER NGA integration)
- Complete IDA pipeline orchestration
- Data compilation and export scripts
- Visualization and plotting utilities
- Fragility curve generation
- SHAP feature importance analysis
- Unit test suite
- Actual OpenSeesPy analysis execution (many modules are placeholders)

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

### Phase 1: Ground Motion Processing (Week 1)

**Files to create:**
- `src/ida/gm_loader.py` - Load ground motions from PEER NGA format
- `src/ida/gm_scaler.py` - Scale GMs to target Sa(T1)
- `src/ida/gm_database.py` - Interface to GM database

**Deliverables:**
```python
# gm_loader.py
def load_ground_motion(filepath: str) -> GMRecord:
    """Load ground motion from file"""

# gm_scaler.py
def scale_to_intensity(gm: GMRecord, target_sa: float, period: float) -> GMRecord:
    """Scale GM to target spectral acceleration"""
```

---

### Phase 2: IDA Pipeline (Week 2)

**Files to create:**
- `src/ida/ida_runner.py` - Main IDA orchestration
- `src/ida/result_collector.py` - Aggregate analysis results

**Deliverables:**
- Run multi-stripe IDA: N buildings × M GMs × K intensities
- Export to `data/processed/ida_results.csv`

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
