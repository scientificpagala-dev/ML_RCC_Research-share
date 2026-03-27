"""Time History Analysis (THA) Module

Implements nonlinear dynamic time history analysis for buildings under
ground motion excitation.

Features:
- Dynamic integration (Newmark, HHT, etc.)
- Nonlinear element response tracking
- Peak response metrics (displacement, acceleration, drift)
- Hysteresis loop generation
- Dynamic instability detection
- Multi-stripe analysis (multiple GM intensities)

References:
- BNBC 2020, Section 3.3 (Time History Analysis)
- ASCE 41-23, Chapter 3 (Dynamic Analysis Procedures)
- OpenSeesPy Documentation (Dynamic Analysis)

Usage:
    from src.analysis.time_history import TimeHistoryAnalysis
    
    tha = TimeHistoryAnalysis(model, ground_motion_record)
    tha.set_analysis_parameters(dt=0.005, duration=30.0)
    tha.run_analysis()
    pidr = tha.compute_peak_inter_story_drift()
    pga = tha.extract_peak_acceleration()
"""

__all__ = []
