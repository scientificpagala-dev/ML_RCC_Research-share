"""Pushover Analysis Module

Implements static nonlinear (pushover) analysis for buildings.

Features:
- Load pattern definition (uniform, proportional to first mode, etc.)
- Pushover curve generation (base shear vs. displacement)
- Performance point identification
- Failure mechanism identification
- Pushover-to-spectrum conversion (capacity spectrum method)
- Softening/hardening detection

References:
- ASCE 41-23, Chapter 3.4 (Static Nonlinear Procedures)
- FEMA 356 (Prestandard for Seismic Rehabilitation)
- NIST GCR 17-917-45 (Seismic Fragility Methodology)

Usage:
    from src.analysis.pushover import PushoverAnalysis
    
    pushover = PushoverAnalysis(model, config)
    pushover.define_load_pattern('proportional_first_mode')
    pushover.run_analysis(target_drift=0.05)
    pushover_curve = pushover.get_pushover_curve()
    performance_point = pushover.identify_performance_point()
"""

__all__ = []
