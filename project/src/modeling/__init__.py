"""OpenSeesPy Structural Modeling Module

This module provides classes and functions for creating parametric RC
moment-resisting frame models in OpenSeesPy, compliant with BNBC 2020
seismic design provisions for multiple framework types.

Key Classes:
- RCFrame: Parametric RC frame generator for different framework types
- FrameGeometry: Frame geometric properties
- FrameMaterials: Material definitions with framework-specific properties
- MaterialManager: Manager for framework-specific material creation
- BNBCComplianceChecker: BNBC 2020 design verification and base shear calculation

Usage:
    from src.modeling import RCFrame
    import yaml
    
    with open('config/bnbc_parameters.yaml') as f:
        bnbc = yaml.safe_load(f)
    
    frame = RCFrame(n_stories=10, story_height=3.5, zone=3, bnbc_params=bnbc)
    frame.apply_gravity_loads()
    frame.validate_bnbc_compliance()
    frame.save_model('models/openseespy/frame_10s_z3.json')
"""

from .rc_frame import RCFrame, FrameGeometry, FrameMaterials
from .materials import MaterialManager, ConcreteMaterial, SteelMaterial
from .bnbc_compliance import BNBCComplianceChecker

__all__ = [
    'RCFrame',
    'FrameGeometry',
    'FrameMaterials',
    'MaterialManager',
    'ConcreteMaterial',
    'SteelMaterial',
    'BNBCComplianceChecker'
]
