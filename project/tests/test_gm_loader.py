"""Unit tests for Ground Motion Loader Module

Tests for loading, parsing, and validating ground motion records in various formats.
"""

import pytest
import numpy as np
import tempfile
import os
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.ida.gm_loader import GMRecord, load_ground_motion, generate_synthetic_gm


class TestGMRecord:
    """Test GMRecord class"""

    def test_gmrecord_initialization(self):
        """Test basic GM record initialization"""
        time = np.linspace(0, 10, 1000)
        accel = np.sin(2 * np.pi * 0.5 * time) * 0.1  # Simple sine wave
        
        gm = GMRecord("test_record", time, accel, dt=0.01)
        
        assert gm.name == "test_record"
        assert len(gm.time) == 1000
        assert len(gm.acceleration) == 1000
        assert gm.dt == 0.01
        np.testing.assert_array_equal(gm.time, time)

    def test_gmrecord_pga_computation(self):
        """Test PGA (Peak Ground Acceleration) computation"""
        time = np.linspace(0, 1, 100)
        accel = np.array([0.1 * i for i in range(100)])  # Linear increase
        
        gm = GMRecord("test", time, accel)
        
        assert gm.pga == pytest.approx(9.9, rel=0.1)  # Close to max acceleration

    def test_gmrecord_with_scaling(self):
        """Test GM record with scale factor"""
        time = np.linspace(0, 1, 100)
        accel = np.ones(100) * 0.1
        
        gm = GMRecord("test", time, accel, scale_factor=2.0)
        
        assert gm.scale_factor == 2.0
        np.testing.assert_array_almost_equal(gm.acceleration, np.ones(100) * 0.2)

    def test_gmrecord_intensity_measures(self):
        """Test computation of intensity measures"""
        time = np.linspace(0, 2, 1000)
        accel = 0.2 * np.sin(2 * np.pi * time)
        
        gm = GMRecord("test", time, accel)
        
        assert hasattr(gm, 'pga')
        assert hasattr(gm, 'pgv')
        assert hasattr(gm, 'pgd')
        assert hasattr(gm, 'cycles')
        assert hasattr(gm, 'duration')
        
        assert gm.pga > 0
        assert gm.pgv > 0
        assert gm.pgd > 0
        assert gm.cycles > 0


class TestLoadGroundMotion:
    """Test ground motion loading functions"""

    def test_load_from_two_column_file(self):
        """Test loading from two-column (time, accel) format"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            # Write test data
            f.write("# Test ground motion file\n")
            f.write("0.0 0.0\n")
            f.write("0.01 0.001\n")
            f.write("0.02 0.002\n")
            f.write("0.03 0.001\n")
            temp_file = f.name

        try:
            gm = load_ground_motion(temp_file)
            
            assert hasattr(gm, 'time')
            assert hasattr(gm, 'acceleration')
            assert len(gm.time) == 4
            assert gm.time[0] == 0.0
        finally:
            os.unlink(temp_file)

    def test_load_with_custom_delimiter(self):
        """Test loading with custom delimiter"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("0.0,0.0\n")
            f.write("0.01,0.001\n")
            f.write("0.02,0.002\n")
            temp_file = f.name

        try:
            gm = load_ground_motion(temp_file, delimiter=',')
            
            assert len(gm.time) == 3
            assert gm.time[1] == 0.01
        finally:
            os.unlink(temp_file)

    def test_load_nonexistent_file(self):
        """Test loading from nonexistent file raises error"""
        with pytest.raises((FileNotFoundError, IOError)):
            load_ground_motion('nonexistent_file.txt')

    def test_load_with_custom_scale(self):
        """Test loading with custom scale factor"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("0.0 0.1\n")
            f.write("0.01 0.2\n")
            temp_file = f.name

        try:
            gm = load_ground_motion(temp_file, scale_factor=2.0)
            
            assert gm.acceleration[0] == pytest.approx(0.2, rel=0.01)
            assert gm.acceleration[1] == pytest.approx(0.4, rel=0.01)
        finally:
            os.unlink(temp_file)


class TestSyntheticGM:
    """Test synthetic ground motion generation"""

    def test_synthetic_gm_basic(self):
        """Test basic synthetic GM generation"""
        gm = generate_synthetic_gm(
            duration=10.0,
            dt=0.01,
            n_modes=5,
            pga=0.2,
            periods=None
        )
        
        assert isinstance(gm, GMRecord)
        assert len(gm.acceleration) > 0
        assert gm.pga > 0

    def test_synthetic_gm_custom_periods(self):
        """Test synthetic GM with custom periods"""
        periods = [0.5, 1.0, 2.0]
        gm = generate_synthetic_gm(
            duration=5.0,
            dt=0.01,
            n_modes=3,
            pga=0.15,
            periods=periods
        )
        
        assert isinstance(gm, GMRecord)
        assert len(gm.acceleration) == int(5.0 / 0.01)

    def test_synthetic_gm_deterministic(self):
        """Test synthetic GM is deterministic with seed"""
        gm1 = generate_synthetic_gm(
            duration=2.0,
            dt=0.01,
            n_modes=3,
            pga=0.1,
            seed=42
        )
        
        gm2 = generate_synthetic_gm(
            duration=2.0,
            dt=0.01,
            n_modes=3,
            pga=0.1,
            seed=42
        )
        
        np.testing.assert_array_almost_equal(gm1.acceleration, gm2.acceleration)

    def test_synthetic_gm_varies_with_different_seed(self):
        """Test synthetic GM varies with different seed"""
        gm1 = generate_synthetic_gm(duration=2.0, dt=0.01, n_modes=3, pga=0.1, seed=42)
        gm2 = generate_synthetic_gm(duration=2.0, dt=0.01, n_modes=3, pga=0.1, seed=43)
        
        # Should be different
        assert not np.allclose(gm1.acceleration, gm2.acceleration)


class TestGMValidation:
    """Test ground motion validation"""

    def test_validate_pga_reasonable(self):
        """Test that PGA is within reasonable bounds"""
        time = np.linspace(0, 5, 500)
        accel = 0.3 * np.sin(2 * np.pi * 0.5 * time)
        
        gm = GMRecord("test", time, accel)
        
        # PGA should be positive and less than 2g for typical earthquakes
        assert 0 < gm.pga < 2.0

    def test_validate_duration_reasonable(self):
        """Test that duration is reasonable"""
        time = np.linspace(0, 30, 3000)
        accel = 0.2 * np.sin(2 * np.pi * 0.5 * time)
        
        gm = GMRecord("test", time, accel)
        
        # Duration should be positive and less than total time
        assert 0 < gm.duration <= (time[-1] - time[0])

    def test_gmrecord_respects_dt(self):
        """Test that dt is correctly calculated"""
        time = np.linspace(0, 1, 101)
        dt_expected = 0.01
        
        accel = np.sin(time)
        gm = GMRecord("test", time, accel)
        
        assert gm.dt == pytest.approx(dt_expected, rel=0.001)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
