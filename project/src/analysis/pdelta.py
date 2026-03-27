"""P-Delta Analysis Module

Implements geometric nonlinearity (P-Delta) effects in structural analysis.

Features:
- P-Delta transformation in OpenSeesPy
- Stability index computation (θ)
- Story stability verification per BNBC 2020 / ASCE 7-22
- Geometric stiffness matrix updates
- Instability detection and warnings
- Interaction with Response Spectrum, Time History, and Pushover analyses

References:
- BNBC 2020, Section 3.2 (P-Delta Effects)
- ASCE 7-22, Section 12.8.7 (Stability Coefficient θ)
- OpenSeesPy P-Delta Transformation Documentation

Usage:
    from src.analysis.pdelta import PdeltaAnalysis
    
    pdelta = PdeltaAnalysis(model, config)
    theta_max = pdelta.compute_stability_index()
    is_stable = pdelta.check_stability(theta_max)
    
    # In combined analysis:
    if is_stable:
        pushover_with_pdelta = pushover.include_pdelta_effects()
"""

__all__ = []
