# materials.py - Material Models for RC Frame Analysis
"""
Material models for reinforced concrete frame analysis in OpenSeesPy

Provides concrete and steel material models with framework-specific properties
compliant with BNBC 2020 and ACI 318 requirements.
"""

import openseespy.opensees as ops
import numpy as np
from typing import Dict, List, Optional


class ConcreteMaterial:
    """Concrete material models"""

    @staticmethod
    def create_unconfined(fc: float, name: str = "concrete_unconfined"):
        """
        Create unconfined concrete material (Concrete01)

        Args:
            fc: Compressive strength [MPa]
            name: Material name
        """
        fpc = -fc  # Negative for compression
        epsc0 = -0.002  # Strain at peak stress
        fpcu = -0.2 * fc  # Crushing strength
        epsU = -0.006  # Ultimate strain

        ops.uniaxialMaterial('Concrete01', name, fpc, epsc0, fpcu, epsU)  # type: ignore
        return name

    @staticmethod
    def create_confined(fc: float, confinement_factor: float = 1.0,
                       name: str = "concrete_confined"):
        """
        Create confined concrete material (Concrete02 - Mander model)

        Args:
            fc: Unconfined compressive strength [MPa]
            confinement_factor: Enhancement factor (1.0 = unconfined, 1.3 = heavily confined)
            name: Material name
        """
        fcc = -fc * confinement_factor
        epscc = -0.004 - 0.0007 * fc  # Mander strain equation
        fpcu = -0.2 * fc * confinement_factor
        epsU = -0.02

        # Concrete02 parameters
        lambda_param = 0.1
        ft = 0.1 * fc * confinement_factor  # Tensile strength
        Ets = 0.05 * 4700 * np.sqrt(fc)  # Tension softening stiffness

        ops.uniaxialMaterial('Concrete02', name, fcc, epscc, fpcu, epsU,  # type: ignore
                           lambda_param, ft, Ets)
        return name


class SteelMaterial:
    """Steel reinforcement material models"""

    @staticmethod
    def create_elastic_plastic(fy: float, Es: float = 200000,
                              name: str = "steel"):
        """
        Create elastic-plastic steel material (Steel01)

        Args:
            fy: Yield strength [MPa]
            Es: Elastic modulus [MPa]
            name: Material name
        """
        b = 0.01  # Strain hardening ratio
        ops.uniaxialMaterial('Steel01', name, fy, Es, b)  # type: ignore
        return name

    @staticmethod
    def create_menengotto_pinto(fy: float, Es: float = 200000,
                               name: str = "steel_mp"):
        """
        Create Menegotto-Pinto steel material for cyclic analysis (Steel02)

        Args:
            fy: Yield strength [MPa]
            Es: Elastic modulus [MPa]
            name: Material name
        """
        b = 0.01  # Strain hardening ratio
        R0 = 18.5  # Initial value of curvature parameter
        cR1 = 0.925  # Curvature parameter
        cR2 = 0.15  # Curvature parameter

        ops.uniaxialMaterial('Steel02', name, fy, Es, b, R0, cR1, cR2)  # type: ignore
        return name


class MaterialManager:
    """Manager for framework-specific material definitions"""

    def __init__(self, framework_type: str, config: Dict):
        """
        Initialize material manager

        Args:
            framework_type: 'nonsway', 'omrf', 'imrf', 'smrf'
            config: BNBC configuration dictionary
        """
        self.framework_type = framework_type
        self.config = config
        self.materials_created = []

    def create_all_materials(self):
        """Create all materials for the framework type"""
        # Get framework-specific parameters
        fw_params = self.config.get(f'{self.framework_type}_parameters', {})
        defaults = self.config.get('default_materials', {})

        # Concrete properties
        fc = defaults.get('concrete', {}).get('fc_prime', 28.0)

        # Steel properties
        fy = defaults.get('steel_rebar', {}).get('yield_strength', 420.0)
        Es = defaults.get('steel_rebar', {}).get('elastic_modulus', 200000.0)

        # Framework-specific confinement
        confinement = fw_params.get('detailing', {}).get('column_confinement', 'none')

        if confinement == 'none':
            conf_factor = 1.0
        elif confinement == 'light':
            conf_factor = 1.1
        elif confinement == 'moderate':
            conf_factor = 1.2
        elif confinement == 'heavy':
            conf_factor = 1.3
        else:
            conf_factor = 1.0

        # Create materials
        ConcreteMaterial.create_unconfined(fc, "concrete_unconfined")
        ConcreteMaterial.create_confined(fc, conf_factor, "concrete_confined")

        SteelMaterial.create_menengotto_pinto(fy, Es, "steel")

        self.materials_created = ["concrete_unconfined", "concrete_confined", "steel"]

        return self.materials_created

    def get_material_properties(self) -> Dict:
        """Get material properties dictionary"""
        return {
            'concrete_unconfined': {
                'type': 'Concrete01',
                'source': 'materials.py'
            },
            'concrete_confined': {
                'type': 'Concrete02',
                'source': 'materials.py'
            },
            'steel': {
                'type': 'Steel02',
                'source': 'materials.py'
            }
        }


# Backwards-compatible aliases expected by tests / older code
ConcreteModel = ConcreteMaterial
SteelModel = SteelMaterial

__all__ = [
    'ConcreteMaterial', 'ConcreteModel', 'SteelMaterial', 'SteelModel', 'MaterialManager'
]