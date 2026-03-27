"""Plastic Hinge Formation & Tracking Module

Implements plastic hinge analysis for moment-resisting frames.

Features:
- Plastic hinge property assignment (moment-curvature)
- Hinge formation detection and tracking
- Performance level assessment (IO, LS, CP per FEMA P-58)
- Hinge rotation computation
- Damage index calculation
- Fragility curve basis generation

References:
- ASCE 41-23, Chapter 7 (Nonlinear Modeling Parameters)
- FEMA 356, Chapter 5 (Modeling Acceptance Criteria)
- FEMA P-58 (Performance Assessment Methodology)

Usage:
    from src.analysis.plastic_hinge import PlasticHingeAnalyzer
    
    hinge_analyzer = PlasticHingeAnalyzer(model, config)
    hinges = hinge_analyzer.define_hinges('RC_BEAM_COLUMN_JOINT')
    
    # After analysis:
    hinge_rotations = hinge_analyzer.compute_hinge_rotations(response)
    damage_state = hinge_analyzer.assess_performance_level(hinge_rotations)
    fragility_input = hinge_analyzer.generate_fragility_input()
"""

__all__ = []
