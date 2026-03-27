"""Response Spectrum Analysis (RSA) Module

Implements elastic response spectrum analysis for buildings.

Features:
- Design spectrum generation (BNBC 2020 / ASCE 7-22)
- Modal analysis (eigenvalue extraction)
- Modal response combination (SRSS, CQC, etc.)
- Response spectrum computation
- Force distribution per BNBC 2020 procedures

References:
- BNBC 2020, Section 3.2 (Response Spectrum)
- ASCE 7-22, Chapter 11 (Seismic Design Procedures)
- FEMA-440 (Recommended Seismic Design Criteria)

Usage:
    from src.analysis.response_spectrum import ResponseSpectrumAnalysis
    
    rsa = ResponseSpectrumAnalysis(model, bnbc_config, site_class='D')
    eigenvalues, eigenvectors = rsa.extract_modes(n_modes=10)
    base_shear = rsa.compute_base_shear()
    floor_forces = rsa.distribute_forces()
"""

__all__ = []
