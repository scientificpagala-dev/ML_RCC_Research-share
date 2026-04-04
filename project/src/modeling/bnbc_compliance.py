# bnbc_compliance.py - BNBC 2020 Compliance Checker
"""
BNBC 2020 Seismic Design Compliance Checker

Validates RC frame designs against Bangladesh National Building Code 2020
seismic design provisions for different framework types.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
import yaml


class BNBCComplianceChecker:
    """
    BNBC 2020 Seismic Design Compliance Checker

    Checks compliance with:
    - Response reduction factors (R)
    - Base shear calculations
    - Story drift limits
    - Detailing requirements
    - Stability index (θ)
    """

    def __init__(self, config_path: str = 'config/bnbc_parameters.yaml'):
        """Initialize compliance checker with BNBC parameters"""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

    def check_framework_compliance(self, framework_type: str, building_params: Dict) -> Dict:
        """
        Check overall framework compliance

        Args:
            framework_type: 'nonsway', 'omrf', 'imrf', 'smrf'
            building_params: Dictionary with building properties

        Returns:
            Compliance report dictionary
        """
        fw_params = self.config.get(f'{framework_type}_parameters', {})

        report = {
            'framework_type': framework_type,
            'checks': {},
            'overall_compliant': True,
            'warnings': [],
            'errors': []
        }

        # Check response reduction factor
        report['checks']['response_factor'] = self._check_response_factor(
            framework_type, fw_params
        )

        # Check detailing requirements
        report['checks']['detailing'] = self._check_detailing_requirements(
            framework_type, fw_params, building_params
        )

        # Check base shear
        if 'base_shear' in building_params:
            report['checks']['base_shear'] = self._check_base_shear(
                framework_type, building_params, fw_params
            )

        # Check story drifts
        if 'story_drifts' in building_params:
            report['checks']['story_drifts'] = self._check_story_drifts(
                framework_type, building_params['story_drifts'], fw_params
            )

        # Check stability
        if 'stability_index' in building_params:
            report['checks']['stability'] = self._check_stability_index(
                building_params['stability_index']
            )

        # Summarize compliance
        for check_name, check_result in report['checks'].items():
            if not check_result['compliant']:
                report['overall_compliant'] = False
                if check_result['severity'] == 'error':
                    report['errors'].append(f"{check_name}: {check_result['message']}")
                else:
                    report['warnings'].append(f"{check_name}: {check_result['message']}")

        return report

    def _check_response_factor(self, framework_type: str, fw_params: Dict) -> Dict:
        """Check response reduction factor compliance"""
        expected_r = fw_params.get('response_modification_factor', 1.0)

        # BNBC 2020 Table 2.7.4 limits
        r_limits = {
            'nonsway': 1.5,
            'omrf': 3.0,
            'imrf': 4.0,
            'smrf': 5.0
        }

        actual_r = r_limits.get(framework_type, 1.0)

        compliant = abs(actual_r - expected_r) < 0.01

        return {
            'compliant': compliant,
            'expected': expected_r,
            'actual': actual_r,
            'message': f"R factor {'OK' if compliant else 'incorrect'}",
            'severity': 'error' if not compliant else 'info'
        }

    def _check_detailing_requirements(self, framework_type: str, fw_params: Dict,
                                    building_params: Dict) -> Dict:
        """Check detailing requirements"""
        detailing = fw_params.get('detailing', {})

        issues = []

        # Check column confinement
        confinement = detailing.get('column_confinement', 'none')
        if framework_type == 'smrf' and confinement != 'heavy':
            issues.append("SMRF requires heavy column confinement")

        # Check transverse reinforcement spacing
        max_spacing = detailing.get('transverse_reinforcement_spacing', 450.0)
        if framework_type == 'smrf' and max_spacing > 150.0:
            issues.append("SMRF transverse reinforcement spacing exceeds 150mm limit")

        # Check longitudinal reinforcement ratio
        min_rho = detailing.get('longitudinal_reinforcement_ratio', 0.01)
        if 'actual_rho' in building_params:
            actual_rho = building_params['actual_rho']
            if actual_rho < min_rho:
                issues.append(f"Longitudinal reinforcement ratio {actual_rho:.3f} < minimum {min_rho:.3f}")

        compliant = len(issues) == 0

        return {
            'compliant': compliant,
            'issues': issues,
            'message': 'Detailing requirements met' if compliant else f"Issues: {', '.join(issues)}",
            'severity': 'error' if not compliant else 'info'
        }

    def _check_base_shear(self, framework_type: str, building_params: Dict, fw_params: Dict) -> Dict:
        """Check base shear calculation"""
        R = fw_params.get('response_modification_factor', 1.0)
        I = building_params.get('importance_factor', 1.0)
        W = building_params.get('seismic_weight', 0.0)
        Sa = building_params.get('spectral_acceleration', 0.0)

        # BNBC 2020 base shear formula: V = (Sa/R) × I × W
        expected_V = (Sa / R) * I * W
        actual_V = building_params.get('base_shear', 0.0)

        # Allow 10% tolerance
        tolerance = 0.10
        compliant = abs(actual_V - expected_V) / expected_V <= tolerance

        return {
            'compliant': compliant,
            'expected': expected_V,
            'actual': actual_V,
            'tolerance': tolerance,
            'message': f"Base shear within {tolerance*100:.0f}% tolerance" if compliant else f"Base shear outside tolerance",
            'severity': 'warning' if not compliant else 'info'
        }

    def _check_story_drifts(self, framework_type: str, story_drifts: List[float], fw_params: Dict) -> Dict:
        """Check story drift limits"""
        drift_limit = fw_params.get('design_factors', {}).get('story_drift_limit', 0.025)

        max_drift = max(story_drifts) if story_drifts else 0.0
        compliant = max_drift <= drift_limit

        return {
            'compliant': compliant,
            'max_drift': max_drift,
            'limit': drift_limit,
            'message': f"Max drift {max_drift:.3f} {'≤' if compliant else '>'} limit {drift_limit:.3f}",
            'severity': 'error' if not compliant else 'info'
        }

    def _check_stability_index(self, theta: float) -> Dict:
        """Check stability index (θ)"""
        # BNBC 2020 Section 3.2: θ ≤ 0.10 for most buildings, 0.25 for tall flexible
        limit = 0.10  # Conservative limit
        compliant = theta <= limit

        return {
            'compliant': compliant,
            'stability_index': theta,
            'limit': limit,
            'message': f"Stability index {theta:.3f} {'≤' if compliant else '>'} limit {limit:.3f}",
            'severity': 'error' if not compliant else 'info'
        }

    def calculate_base_shear(self, framework_type: str, W: float, Sa: float,
                           I: float = 1.0, site_class: str = 'D') -> float:
        """
        Calculate design base shear per BNBC 2020

        Args:
            framework_type: Framework type
            W: Seismic weight [kN]
            Sa: Spectral acceleration at T1
            I: Importance factor
            site_class: Site class for Fa/Fv factors

        Returns:
            Design base shear [kN]
        """
        fw_params = self.config.get(f'{framework_type}_parameters', {})
        R = fw_params.get('response_modification_factor', 1.0)

        # Apply site amplification (simplified)
        site_factors = self.config.get('site_classes', {}).get(site_class, {})
        Fa = site_factors.get('fa', 1.0)
        Fv = site_factors.get('fv', 1.0)

        # Simplified: assume SDS = SD1 = Sa for calculation
        SDS = Sa * Fa
        SD1 = Sa * Fv

        # Base shear: V = (SDS/R) × I × W (simplified)
        V = (SDS / R) * I * W

        return V

    def calculate_period(self, building_params: Dict) -> float:
        """
        Calculate fundamental period per BNBC 2020

        Args:
            building_params: Building parameters dict

        Returns:
            Fundamental period [seconds]
        """
        # BNBC 2020 approximate formula: T = Ct × H^x
        Ct = 0.0466
        x = 0.90  # For RC moment frames

        H = building_params.get('total_height', 0.0)  # meters

        if H > 0:
            T = Ct * H**x
        else:
            T = 0.0

        return T

    def get_framework_requirements(self, framework_type: str) -> Dict:
        """Get all requirements for a framework type"""
        fw_params = self.config.get(f'{framework_type}_parameters', {})

        return {
            'response_modification_factor': fw_params.get('response_modification_factor', 1.0),
            'overstrength_factor': fw_params.get('overstrength_factor', 2.0),
            'deflection_amplification': fw_params.get('deflection_amplification', 1.0),
            'story_drift_limit': fw_params.get('design_factors', {}).get('story_drift_limit', 0.025),
            'detailing': fw_params.get('detailing', {}),
            'p_delta_effects': fw_params.get('p_delta_effects', True)
        }


# Backwards-compatible alias for older code/tests
BNBCCompliance = BNBCComplianceChecker

__all__ = [
    'BNBCComplianceChecker', 'BNBCCompliance'
]


def check_seismic_zone(zone: int) -> Dict:
    """Return seismic zone parameters for given zone number (1-4)."""
    config_path = 'config/bnbc_parameters.yaml'
    try:
        with open(config_path, 'r') as f:
            cfg = yaml.safe_load(f)
    except FileNotFoundError:
        cfg = {
            'seismic_zones': {
                1: {'pga': 0.05, 'z_coeff': 0.12},
                2: {'pga': 0.10, 'z_coeff': 0.18},
                3: {'pga': 0.15, 'z_coeff': 0.24},
                4: {'pga': 0.20, 'z_coeff': 0.36}
            }
        }

    zones = cfg.get('seismic_zones', {})
    # Support integer or string keys
    if isinstance(list(zones.keys())[0], str):
        # Convert from 'Zone3' style if necessary
        mapping = {}
        for k, v in zones.items():
            num = ''.join([c for c in k if c.isdigit()])
            if num:
                mapping[int(num)] = v
        zones = mapping

    if zone not in zones:
        raise KeyError(f"Unknown seismic zone: {zone}")

    params = zones[zone]
    # Ensure keys
    return {'pga': float(params.get('pga', 0.0)), 'z_coeff': float(params.get('z_coeff', 0.0))}


def check_response_modification(framework: str) -> float:
    """Return recommended response modification factor R for a framework."""
    mapping = {
        'nonsway': 1.5,
        'omrf': 3.5,
        'imrf': 6.0,
        'smrf': 8.0
    }
    if framework not in mapping:
        raise KeyError(f"Unknown framework: {framework}")
    return float(mapping[framework])


def check_design_spectrum(zone: int, periods: List[float]) -> List[float]:
    """Return simplified BNBC design spectrum values for given periods."""
    params = check_seismic_zone(zone)
    z = params['z_coeff']
    # Simple proportional spectrum: Sa = z * (1 + 1/T) for demonstration
    vals = []
    for T in periods:
        if T <= 0:
            vals.append(float(z))
        else:
            vals.append(float(z * (1.0 + 1.0 / max(T, 0.01))))
    return vals


def check_story_drift(framework: str, classification: str = 'normal') -> float:
    """Return story drift limit for framework and classification."""
    base = 0.025  # default 2.5%
    if framework == 'smrf':
        base = 0.03
    elif framework == 'nonsway':
        base = 0.02

    if classification == 'special':
        base *= 0.8

    return float(base)


class BNBCCompliance:
    """Lightweight compatibility wrapper used by tests."""

    def __init__(self, config: Dict):
        self.config = config
        self.seismic_zone = int(config.get('seismic_zone', config.get('zone', 3)))
        self.site_class = config.get('site_class', 'D')
        self.framework_type = config.get('framework_type', 'smrf')

    def check_all(self) -> Dict:
        results = {
            'seismic_zone': check_seismic_zone(self.seismic_zone),
            'response_modification': check_response_modification(self.framework_type),
            'design_spectrum': check_design_spectrum(self.seismic_zone, [0.1, 0.5, 1.0, 2.0]),
            'story_drift_limit': check_story_drift(self.framework_type, 'normal'),
            'warnings': [],
            'errors': []
        }
        # Simple checks
        if results['seismic_zone']['pga'] <= 0:
            results['errors'].append('PGA not positive')

        return results


__all__.extend(['check_seismic_zone', 'check_response_modification', 'check_design_spectrum',
                 'check_story_drift', 'BNBCCompliance'])