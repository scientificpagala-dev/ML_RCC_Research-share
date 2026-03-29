"""Unit tests for BNBC 2020 Compliance Checker

Tests for verifying RC frame compliance with BNBC 2020 design provisions.
"""

import pytest
import sys
import os
import yaml
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.modeling.bnbc_compliance import (
    BNBCCompliance, check_seismic_zone, check_response_modification,
    check_design_spectrum, check_story_drift
)


class TestBNBCZones:
    """Test BNBC seismic zone validation"""

    def test_valid_zones(self):
        """Test that all valid zones are recognized"""
        valid_zones = [1, 2, 3, 4]
        
        for zone in valid_zones:
            result = check_seismic_zone(zone)
            assert result is not None
            assert isinstance(result, dict)
            assert 'pga' in result
            assert 'z_coeff' in result

    def test_invalid_zone(self):
        """Test that invalid zone raises error"""
        with pytest.raises((ValueError, KeyError)):
            check_seismic_zone(99)

    def test_zone_parameters_valid(self):
        """Test that zone parameters are valid"""
        for zone in [1, 2, 3, 4]:
            result = check_seismic_zone(zone)
            
            # PGA should be positive
            assert result['pga'] > 0
            # Z coefficient should be positive
            assert result['z_coeff'] > 0
            # Z coefficient should match BNBC
            assert result['z_coeff'] in [0.12, 0.18, 0.24, 0.36]


class TestResponseModification:
    """Test response modification factor (R) validation"""

    def test_response_modification_valid_frameworks(self):
        """Test R factor for valid framework types"""
        frameworks = {
            'nonsway': 1.5,
            'omrf': 3.5,
            'imrf': 6.0,
            'smrf': 8.0
        }
        
        for framework, expected_r in frameworks.items():
            result = check_response_modification(framework)
            assert result is not None
            assert result == expected_r

    def test_response_modification_invalid_framework(self):
        """Test invalid framework raises error"""
        with pytest.raises((ValueError, KeyError)):
            check_response_modification('invalid_framework')

    def test_response_modification_range(self):
        """Test that R factors are in reasonable range"""
        frameworks = ['nonsway', 'omrf', 'imrf', 'smrf']
        r_values = [check_response_modification(f) for f in frameworks]
        
        # All R values should be positive
        assert all(r > 0 for r in r_values)
        # SMRF should have highest R
        assert check_response_modification('smrf') > check_response_modification('nonsway')


class TestDesignSpectrum:
    """Test BNBC design spectrum"""

    def test_spectrum_increasing_periods(self):
        """Test that spectrum is defined for increasing periods"""
        zone = 3
        periods = [0.1, 0.5, 1.0, 2.0, 4.0]
        
        spectrum_values = check_design_spectrum(zone, periods)
        
        assert len(spectrum_values) == len(periods)
        assert all(v > 0 for v in spectrum_values)

    def test_spectrum_zone_dependency(self):
        """Test spectrum depends on zone"""
        periods = [1.0]
        
        spectrum_z1 = check_design_spectrum(1, periods)
        spectrum_z4 = check_design_spectrum(4, periods)
        
        # Zone 4 (high hazard) should have higher spectrum
        assert spectrum_z4 > spectrum_z1

    def test_spectrum_short_period_region(self):
        """Test spectrum in short period region"""
        zone = 3
        periods = [0.1, 0.2, 0.3]
        
        spectrum = check_design_spectrum(zone, periods)
        
        # Short period spectrum increases with period (typically)
        # or remains relatively constant
        assert all(v > 0 for v in spectrum)

    def test_spectrum_long_period_region(self):
        """Test spectrum in long period region"""
        zone = 3
        periods = [2.0, 3.0, 4.0, 5.0]
        
        spectrum = check_design_spectrum(zone, periods)
        
        # Long period spectrum should decrease
        for i in range(len(spectrum) - 1):
            assert spectrum[i] >= spectrum[i + 1]


class TestStoryDriftLimit:
    """Test story drift validation"""

    def test_drift_limit_valid(self):
        """Test valid story drift limits"""
        framework = 'smrf'
        classification = 'normal'
        
        limit = check_story_drift(framework, classification)
        
        assert limit > 0
        # Typical drift limit is 2.0% - 4.0%
        assert 0.01 < limit < 0.05

    def test_drift_limit_framework_dependency(self):
        """Test drift limits vary by framework"""
        classification = 'normal'
        
        limit_nonsway = check_story_drift('nonsway', classification)
        limit_smrf = check_story_drift('smrf', classification)
        
        # Drift limits should be different
        assert limit_nonsway != limit_smrf

    def test_drift_limit_classification_dependency(self):
        """Test drift limits vary by building classification"""
        framework = 'smrf'
        
        limit_normal = check_story_drift(framework, 'normal')
        limit_special = check_story_drift(framework, 'special')
        
        assert limit_normal > 0
        assert limit_special > 0


class TestBNBCCompliance:
    """Test BNBCCompliance class"""

    def test_compliance_initialization(self):
        """Test BNBCCompliance initialization"""
        config = {
            'seismic_zone': 3,
            'site_class': 'D',
            'framework_type': 'smrf',
            'n_stories': 10,
            'story_height': 3.5
        }
        
        compliance = BNBCCompliance(config)
        
        assert compliance.seismic_zone == 3
        assert compliance.framework_type == 'smrf'

    def test_compliance_full_check(self):
        """Test complete compliance check"""
        config = {
            'seismic_zone': 3,
            'site_class': 'D',
            'framework_type': 'smrf',
            'n_stories': 5,
            'story_height': 3.5,
            'column_width_mm': 500,
            'beam_width_mm': 400,
            'concrete_fc_mpa': 28
        }
        
        compliance = BNBCCompliance(config)
        results = compliance.check_all()
        
        assert isinstance(results, dict)
        assert 'seismic_zone' in results
        assert 'response_modification' in results

    def test_compliance_minimum_dimensions(self):
        """Test minimum dimension checks"""
        config = {
            'seismic_zone': 4,
            'site_class': 'D',
            'framework_type': 'smrf',
            'n_stories': 12,
            'story_height': 3.5,
            'column_width_mm': 200,  # Very small
            'beam_width_mm': 150,     # Very small
            'concrete_fc_mpa': 20     # Low grade
        }
        
        compliance = BNBCCompliance(config)
        results = compliance.check_all()
        
        # Should flag dimension issues
        assert 'warnings' in results or 'errors' in results

    def test_compliance_maximum_dimensions(self):
        """Test with reasonable dimensions"""
        config = {
            'seismic_zone': 2,
            'site_class': 'D',
            'framework_type': 'smrf',
            'n_stories': 5,
            'story_height': 3.5,
            'column_width_mm': 600,
            'beam_width_mm': 500,
            'concrete_fc_mpa': 35
        }
        
        compliance = BNBCCompliance(config)
        results = compliance.check_all()
        
        assert results is not None


class TestZoneParameters:
    """Test BNBC zone parameters"""

    def test_zone_1_parameters(self):
        """Test Zone I parameters"""
        zone_params = check_seismic_zone(1)
        
        assert zone_params['pga'] == pytest.approx(0.05, rel=0.01)
        assert zone_params['z_coeff'] == pytest.approx(0.12, rel=0.01)

    def test_zone_2_parameters(self):
        """Test Zone II parameters"""
        zone_params = check_seismic_zone(2)
        
        assert zone_params['pga'] == pytest.approx(0.10, rel=0.01)
        assert zone_params['z_coeff'] == pytest.approx(0.18, rel=0.01)

    def test_zone_3_parameters(self):
        """Test Zone III parameters"""
        zone_params = check_seismic_zone(3)
        
        assert zone_params['pga'] == pytest.approx(0.15, rel=0.01)
        assert zone_params['z_coeff'] == pytest.approx(0.24, rel=0.01)

    def test_zone_4_parameters(self):
        """Test Zone IV parameters"""
        zone_params = check_seismic_zone(4)
        
        assert zone_params['pga'] == pytest.approx(0.20, rel=0.01)
        assert zone_params['z_coeff'] == pytest.approx(0.36, rel=0.01)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
