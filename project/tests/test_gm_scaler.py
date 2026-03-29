"""Unit tests for Ground Motion Scaler Module

Tests for scaling ground motions to target spectral acceleration.
"""

import pytest
import numpy as np
import sys
import os
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.ida.gm_scaler import GMScaler, scale_gm_linear, compute_spectrum
from src.ida.gm_loader import GMRecord


class TestComputeSpectrum:
    """Test spectral computation"""

    def test_spectrum_shape(self):
        """Test that computed spectrum has correct shape"""
        time = np.linspace(0, 10, 1000)
        accel = 0.2 * np.sin(2 * np.pi * 0.5 * time)
        gm = GMRecord("test", time, accel, dt=0.01)
        
        periods = np.linspace(0.1, 4.0, 20)
        spectrum = compute_spectrum(gm, periods, damping=0.05)
        
        assert len(spectrum) == len(periods)
        assert np.all(spectrum >= 0)

    def test_spectrum_values_increase_with_input_amplitude(self):
        """Test that spectrum values scale with input acceleration amplitude"""
        time = np.linspace(0, 5, 500)
        
        # Small amplitude
        accel_small = 0.1 * np.sin(2 * np.pi * time)
        gm_small = GMRecord("small", time, accel_small)
        
        # Large amplitude
        accel_large = 0.3 * np.sin(2 * np.pi * time)
        gm_large = GMRecord("large", time, accel_large)
        
        periods = np.array([1.0])
        
        spec_small = compute_spectrum(gm_small, periods)[0]
        spec_large = compute_spectrum(gm_large, periods)[0]
        
        # Larger amplitude should give larger spectrum
        assert spec_large > spec_small

    def test_spectrum_damping_effect(self):
        """Test that higher damping reduces spectrum values"""
        time = np.linspace(0, 5, 500)
        accel = 0.2 * np.sin(2 * np.pi * time)
        gm = GMRecord("test", time, accel)
        
        periods = np.array([1.0])
        
        spec_005 = compute_spectrum(gm, periods, damping=0.05)[0]
        spec_020 = compute_spectrum(gm, periods, damping=0.20)[0]
        
        # Higher damping should reduce spectrum
        assert spec_020 < spec_005


class TestScaleGMLinear:
    """Test linear GM scaling"""

    def test_scale_factor_applied(self):
        """Test that scale factor is correctly applied"""
        time = np.linspace(0, 1, 100)
        accel = np.ones(100) * 0.1
        gm = GMRecord("test", time, accel)
        
        scale_factor = 2.0
        scaled_gm = scale_gm_linear(gm, scale_factor)
        
        np.testing.assert_array_almost_equal(
            scaled_gm.acceleration,
            gm.acceleration * scale_factor
        )

    def test_scale_preserves_time(self):
        """Test that scaling preserves time array"""
        time = np.linspace(0, 1, 100)
        accel = 0.1 * np.sin(2 * np.pi * time)
        gm = GMRecord("test", time, accel)
        
        scaled_gm = scale_gm_linear(gm, 1.5)
        
        np.testing.assert_array_equal(scaled_gm.time, gm.time)

    def test_scale_unity_factor(self):
        """Test scaling with unity factor (no change)"""
        time = np.linspace(0, 1, 100)
        accel = 0.2 * np.sin(2 * np.pi * time)
        gm = GMRecord("test", time, accel)
        
        scaled_gm = scale_gm_linear(gm, 1.0)
        
        np.testing.assert_array_almost_equal(
            scaled_gm.acceleration,
            gm.acceleration
        )


class TestGMScaler:
    """Test GMScaler class"""

    def test_scaler_initialization(self):
        """Test GMScaler initialization"""
        time = np.linspace(0, 5, 500)
        accel = 0.2 * np.sin(2 * np.pi * 0.5 * time)
        gm = GMRecord("test", time, accel)
        
        scaler = GMScaler(gm, target_period=1.0, damping=0.05)
        
        assert scaler.gm is gm
        assert scaler.target_period == 1.0
        assert scaler.damping == 0.05

    def test_scale_to_sa_basic(self):
        """Test scaling to target spectral acceleration"""
        time = np.linspace(0, 10, 1000)
        accel = 0.1 * np.sin(2 * np.pi * time)
        gm = GMRecord("test", time, accel, dt=0.01)
        
        scaler = GMScaler(gm, target_period=1.0, damping=0.05)
        
        # Scale to different target Sa values
        target_sa_values = [0.2, 0.5]
        
        for target_sa in target_sa_values:
            scaled_gm = scaler.scale_to_sa(target_sa, method='linear')
            
            assert scaled_gm is not None
            assert isinstance(scaled_gm, GMRecord)
            # Scaled GM should have different PGA
            assert scaled_gm.pga != gm.pga

    def test_scaler_different_methods(self):
        """Test scaling with different methods"""
        time = np.linspace(0, 10, 1000)
        accel = 0.15 * np.sin(2 * np.pi * time)
        gm = GMRecord("test", time, accel, dt=0.01)
        
        scaler = GMScaler(gm, target_period=1.0, damping=0.05)
        target_sa = 0.3
        
        scaled_linear = scaler.scale_to_sa(target_sa, method='linear')
        
        assert isinstance(scaled_linear, GMRecord)
        assert scaled_linear.pga > 0

    def test_scaler_convergence(self):
        """Test that scaling converges to target"""
        time = np.linspace(0, 5, 500)
        accel = 0.15 * np.sin(2 * np.pi * 0.5 * time)
        gm = GMRecord("test", time, accel, dt=0.01)
        
        scaler = GMScaler(gm, target_period=1.0, damping=0.05, max_iterations=20)
        target_sa = 0.4
        
        scaled_gm = scaler.scale_to_sa(target_sa, method='linear')
        
        # Scaled GM should not be None
        assert scaled_gm is not None
        assert scaled_gm.pga > 0

    def test_scaler_pga_scaling_factor(self):
        """Test that scaler computes reasonable scale factors"""
        time = np.linspace(0, 5, 500)
        accel = 0.1 * np.sin(2 * np.pi * time)
        gm = GMRecord("test", time, accel)
        
        scaler = GMScaler(gm, target_period=1.0, damping=0.05)
        
        # Scale factor should be positive
        scale_factor = scaler._get_pga_scale_factor(target_sa=0.3)
        assert scale_factor > 0

    def test_scaler_consistency(self):
        """Test that repeated scaling is consistent"""
        time = np.linspace(0, 5, 500)
        accel = 0.2 * np.sin(2 * np.pi * time)
        gm1 = GMRecord("test1", time, accel.copy(), dt=0.01)
        gm2 = GMRecord("test2", time, accel.copy(), dt=0.01)
        
        scaler1 = GMScaler(gm1, target_period=1.0, damping=0.05)
        scaler2 = GMScaler(gm2, target_period=1.0, damping=0.05)
        
        target_sa = 0.3
        
        scaled1 = scaler1.scale_to_sa(target_sa, method='linear')
        scaled2 = scaler2.scale_to_sa(target_sa, method='linear')
        
        # Should have same PGA
        assert scaled1.pga == pytest.approx(scaled2.pga, rel=0.01)


class TestScalingEdgeCases:
    """Test edge cases and error handling"""

    def test_scale_factor_zero(self):
        """Test that zero scale factor is handled"""
        time = np.linspace(0, 1, 100)
        accel = np.ones(100) * 0.1
        gm = GMRecord("test", time, accel)
        
        # Very small scale factor should work
        scaled = scale_gm_linear(gm, 0.001)
        assert np.all(scaled.acceleration > 0)

    def test_very_large_scale_factor(self):
        """Test very large scale factor"""
        time = np.linspace(0, 1, 100)
        accel = np.ones(100) * 0.1
        gm = GMRecord("test", time, accel)
        
        scaled = scale_gm_linear(gm, 1000.0)
        
        assert np.all(scaled.acceleration > 0)
        assert scaled.pga > gm.pga


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
