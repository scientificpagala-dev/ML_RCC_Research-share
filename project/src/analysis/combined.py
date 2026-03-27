"""Combined Analysis Methods Module

Implements multi-method analysis combinations and workflows:
- RSA + Pushover (Capacity Spectrum Method)
- THA + P-Delta effects
- Pushover + Plastic Hinge assessment
- Multi-stripe analysis (multiple ground motions × intensities)
- Analysis ensemble generation for ML training

Features:
- Sequential analysis execution
- Cross-method validation
- Result aggregation and comparison
- Uncertainty quantification
- Computational optimization (parallel processing)

References:
- NIST GCR 17-917-45 (Seismic Fragility Methodology)
- FEMA P-58, Vol. 1 (Methodology)
- ASCE 41-23, Chapter 3 (Analysis Selection)

Usage:
    from src.analysis.combined import CombinedAnalysis
    
    # Capacity-Spectrum Method (RSA + Pushover)
    csm = CombinedAnalysis(model, 'CSM')
    csm.run_rsa()
    csm.run_pushover()
    performance_point = csm.identify_performance_point()
    
    # Multi-stripe analysis (Phase 2 data generation)
    multi_stripe = CombinedAnalysis(model, 'MULTI_STRIPE')
    for gm_record in ground_motions:
        for intensity in intensity_levels:
            result = multi_stripe.run_tha(gm_record, intensity)
            results_db.append(result)
"""

__all__ = []
