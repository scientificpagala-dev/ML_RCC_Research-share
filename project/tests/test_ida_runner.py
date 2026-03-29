"""Unit tests for IDA Runner Module

Tests for Incremental Dynamic Analysis execution and result aggregation.
"""

import pytest
import sys
import os
import tempfile
import numpy as np
import pandas as pd
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Mock openseespy
sys.modules['openseespy'] = MagicMock()
sys.modules['openseespy.opensees'] = MagicMock()

from src.ida.ida_runner import IDARunner, IDAResult
from src.ida.gm_loader import GMRecord


class TestIDAResult:
    """Test IDAResult class"""

    def test_result_initialization(self):
        """Test IDAResult initialization"""
        result = IDAResult(
            building_id='building_1',
            framework='smrf',
            n_stories=5,
            gm_name='earthquake_001',
            sa_intensity=0.5,
            pidr=0.018,
            max_accel=0.45,
            convergence_success=True
        )
        
        assert result.building_id == 'building_1'
        assert result.framework == 'smrf'
        assert result.n_stories == 5
        assert result.pidr == 0.018
        assert result.convergence_success is True

    def test_result_to_dict(self):
        """Test converting result to dictionary"""
        result = IDAResult(
            building_id='building_1',
            framework='smrf',
            n_stories=5,
            gm_name='earthquake_001',
            sa_intensity=0.5,
            pidr=0.018,
            max_accel=0.45
        )
        
        result_dict = result.to_dict()
        
        assert isinstance(result_dict, dict)
        assert result_dict['building_id'] == 'building_1'
        assert result_dict['pidr'] == 0.018

    def test_result_dataframe(self):
        """Test creating DataFrame from results"""
        results = [
            IDAResult('b1', 'smrf', 5, 'gm_1', 0.3, 0.010, 0.30),
            IDAResult('b1', 'smrf', 5, 'gm_1', 0.5, 0.015, 0.45),
            IDAResult('b1', 'smrf', 5, 'gm_1', 0.7, 0.025, 0.60),
        ]
        
        df = pd.DataFrame([r.to_dict() for r in results])
        
        assert len(df) == 3
        assert 'pidr' in df.columns
        assert 'sa_intensity' in df.columns
        assert all(df['pidr'] >= 0)


class TestIDARunner:
    """Test IDARunner class"""

    def test_ida_runner_initialization(self):
        """Test IDARunner initialization"""
        config = {
            'ida': {
                'sa_range': [0.1, 1.5],
                'sa_step': 0.1,
                'n_iterations': 10,
                'target_period': 1.0,
                'damping': 0.05
            },
            'analysis': {
                'dt': 0.01,
                'duration': 20.0
            }
        }
        
        runner = IDARunner(config)
        
        assert runner.config == config
        assert hasattr(runner, 'results')

    def test_ida_runner_result_storage(self):
        """Test that results are properly stored"""
        config = {
            'ida': {
                'sa_range': [0.1, 1.5],
                'sa_step': 0.1,
                'target_period': 1.0,
                'damping': 0.05
            },
            'analysis': {
                'dt': 0.01,
                'duration': 20.0
            }
        }
        
        runner = IDARunner(config)
        
        # Add mock results
        result = IDAResult('b1', 'smrf', 5, 'gm_1', 0.3, 0.010, 0.30)
        runner.add_result(result)
        
        assert len(runner.results) == 1
        assert runner.results[0] == result

    def test_ida_runner_multiple_results(self):
        """Test storing multiple results"""
        config = {
            'ida': {
                'sa_range': [0.1, 1.5],
                'sa_step': 0.1,
                'target_period': 1.0,
                'damping': 0.05
            },
            'analysis': {
                'dt': 0.01,
                'duration': 20.0
            }
        }
        
        runner = IDARunner(config)
        
        for i in range(5):
            result = IDAResult('b1', 'smrf', 5, 'gm_1', 0.1 + i*0.1, 0.010 + i*0.002, 0.30)
            runner.add_result(result)
        
        assert len(runner.results) == 5

    def test_ida_runner_export_csv(self):
        """Test exporting results to CSV"""
        config = {
            'ida': {
                'sa_range': [0.1, 1.5],
                'sa_step': 0.1,
                'target_period': 1.0,
                'damping': 0.05
            },
            'analysis': {
                'dt': 0.01,
                'duration': 20.0
            }
        }
        
        runner = IDARunner(config)
        
        # Add results
        for i in range(3):
            result = IDAResult('b1', 'smrf', 5, f'gm_{i}', 0.3, 0.010, 0.30)
            runner.add_result(result)
        
        # Export to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            temp_file = f.name
        
        try:
            runner.export_to_csv(temp_file)
            
            # Verify file was created
            assert os.path.exists(temp_file)
            
            # Verify contents
            df = pd.read_csv(temp_file)
            assert len(df) == 3
            assert 'pidr' in df.columns
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    def test_ida_runner_statistics(self):
        """Test computing statistics from results"""
        config = {
            'ida': {
                'sa_range': [0.1, 1.5],
                'sa_step': 0.1,
                'target_period': 1.0,
                'damping': 0.05
            },
            'analysis': {
                'dt': 0.01,
                'duration': 20.0
            }
        }
        
        runner = IDARunner(config)
        
        # Add results with known statistics
        pidrs = [0.010, 0.015, 0.020, 0.025, 0.030]
        for i, pidr in enumerate(pidrs):
            result = IDAResult('b1', 'smrf', 5, f'gm_{i}', 0.3, pidr, 0.30)
            runner.add_result(result)
        
        # Get summary statistics
        pidr_values = [r.pidr for r in runner.results]
        
        assert min(pidr_values) == 0.010
        assert max(pidr_values) == 0.030
        assert np.mean(pidr_values) == 0.020


class TestIDAEdgeCases:
    """Test edge cases for IDA analysis"""

    def test_ida_with_convergence_failures(self):
        """Test handling of convergence failures"""
        results = [
            IDAResult('b1', 'smrf', 5, 'gm_1', 0.3, 0.010, 0.30, convergence_success=True),
            IDAResult('b1', 'smrf', 5, 'gm_1', 0.5, None, None, convergence_success=False),
            IDAResult('b1', 'smrf', 5, 'gm_1', 0.7, 0.025, 0.60, convergence_success=True),
        ]
        
        # Convert to DataFrame
        result_dicts = []
        for r in results:
            d = r.to_dict()
            result_dicts.append(d)
        
        df = pd.DataFrame(result_dicts)
        
        # Filter successful runs
        df_success = df[df['convergence_success'] == True]
        
        assert len(df_success) == 2
        assert len(df) == 3

    def test_ida_very_low_intensity(self):
        """Test IDA result with very low intensity"""
        result = IDAResult(
            building_id='b1',
            framework='smrf',
            n_stories=5,
            gm_name='gm_1',
            sa_intensity=0.05,  # Very low
            pidr=0.001,  # Very small drift
            max_accel=0.05
        )
        
        assert result.sa_intensity == 0.05
        assert result.pidr == 0.001
        assert result.pidr > 0

    def test_ida_very_high_intensity(self):
        """Test IDA result with very high intensity"""
        result = IDAResult(
            building_id='b1',
            framework='smrf',
            n_stories=5,
            gm_name='gm_1',
            sa_intensity=2.0,  # Very high
            pidr=0.10,  # Large drift (collapse prevention)
            max_accel=1.80
        )
        
        assert result.sa_intensity == 2.0
        assert result.pidr == 0.10


class TestIDAIntegration:
    """Integration tests for IDA pipeline"""

    def test_ida_multi_building_multi_gm(self):
        """Test IDA across multiple buildings and ground motions"""
        config = {
            'ida': {
                'sa_range': [0.1, 1.0],
                'sa_step': 0.2,
                'target_period': 1.0,
                'damping': 0.05
            },
            'analysis': {
                'dt': 0.01,
                'duration': 20.0
            }
        }
        
        runner = IDARunner(config)
        
        # Simulate multi-building, multi-GM analysis
        buildings = ['b1_5s', 'b2_7s', 'b3_10s']
        gms = ['gm_001', 'gm_002', 'gm_003']
        sa_values = np.arange(0.1, 1.1, 0.2)
        
        count = 0
        for building in buildings:
            for gm in gms:
                for sa in sa_values:
                    # Simulate increasing drift with intensity
                    pidr = 0.003 + 0.02 * sa ** 1.2
                    result = IDAResult(
                        building_id=building,
                        framework='smrf',
                        n_stories=int(building.split('_')[1].replace('s', '')),
                        gm_name=gm,
                        sa_intensity=sa,
                        pidr=pidr,
                        max_accel=0.9*sa
                    )
                    runner.add_result(result)
                    count += 1
        
        assert len(runner.results) == count
        assert len(runner.results) == len(buildings) * len(gms) * len(sa_values)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
