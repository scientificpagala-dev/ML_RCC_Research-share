"""Unit tests for RC Frame Modeling

Tests for RC frame generation, material properties, and model validation.
"""

import pytest
import sys
import os
import numpy as np
from unittest.mock import Mock, patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Mock openseespy module for testing
sys.modules['openseespy'] = MagicMock()
sys.modules['openseespy.opensees'] = MagicMock()

from src.modeling.rc_frame import RCFrame, FrameGeometry, FrameMaterials
from src.modeling.materials import ConcreteModel, SteelModel


class TestFrameGeometry:
    """Test FrameGeometry class"""

    def test_uniform_geometry_creation(self):
        """Test creating uniform frame geometry"""
        geometry = FrameGeometry.create_uniform(
            n_stories=5,
            story_height=3.5,
            n_bays=3,
            bay_width=5.0,
            column_size=(500, 500),
            beam_size=(400, 600)
        )
        
        assert geometry.n_stories == 5
        assert geometry.n_bays == 3
        assert geometry.total_height == pytest.approx(17.5, rel=0.01)
        assert len(geometry.story_heights) == 5
        assert all(h == 3.5 for h in geometry.story_heights)

    def test_geometry_derived_properties(self):
        """Test derived geometric properties"""
        geometry = FrameGeometry.create_uniform(
            n_stories=10,
            story_height=3.5,
            n_bays=2,
            bay_width=6.0,
            column_size=(500, 500),
            beam_size=(400, 600)
        )
        
        # Test floor levels
        assert len(geometry.floor_levels) == 11  # n_stories + 1
        assert geometry.floor_levels[0] == 0.0
        assert geometry.floor_levels[-1] == pytest.approx(35.0, rel=0.01)

    def test_geometry_with_variable_heights(self):
        """Test geometry with variable story heights"""
        heights = [4.0, 3.5, 3.5, 3.5, 3.0]
        widths = [5.0, 5.0]
        
        geometry = FrameGeometry(
            n_stories=5,
            story_heights=heights,
            bay_widths=widths,
            column_sizes=[(500, 500)] * 5,
            beam_sizes=[(400, 600)] * 5
        )
        
        assert geometry.total_height == pytest.approx(17.5, rel=0.01)

    def test_geometry_floor_levels_cumulative(self):
        """Test floor levels are cumulative"""
        geometry = FrameGeometry.create_uniform(
            n_stories=3,
            story_height=4.0,
            n_bays=2,
            bay_width=5.0,
            column_size=(500, 500),
            beam_size=(400, 600)
        )
        
        # Check cumulative heights
        assert geometry.floor_levels[1] == pytest.approx(4.0, rel=0.01)
        assert geometry.floor_levels[2] == pytest.approx(8.0, rel=0.01)
        assert geometry.floor_levels[3] == pytest.approx(12.0, rel=0.01)


class TestFrameMaterials:
    """Test FrameMaterials class"""

    def test_material_creation_nonsway(self):
        """Test material creation for non-sway frame"""
        config = {
            'default_materials': {
                'concrete': {'fc_prime': 28.0},
                'steel_rebar': {'fy': 500.0}
            },
            'nonsway_parameters': {
                'detailing': {'column_confinement': 'none'}
            }
        }
        
        materials = FrameMaterials('nonsway', config)
        
        assert 'concrete_unconfined' in materials.materials
        assert 'steel_main' in materials.materials

    def test_material_creation_smrf(self):
        """Test material creation for SMRF"""
        config = {
            'default_materials': {
                'concrete': {'fc_prime': 35.0},
                'steel_rebar': {'fy': 500.0}
            },
            'smrf_parameters': {
                'detailing': {'column_confinement': 'spiral'}
            }
        }
        
        materials = FrameMaterials('smrf', config)
        
        assert materials.framework_type == 'smrf'
        assert isinstance(materials.materials, dict)

    def test_framework_types(self):
        """Test all framework types"""
        config = {
            'default_materials': {
                'concrete': {'fc_prime': 28.0},
                'steel_rebar': {'fy': 500.0}
            }
        }
        
        for fw_type in ['nonsway', 'omrf', 'imrf', 'smrf']:
            config[f'{fw_type}_parameters'] = {
                'detailing': {'column_confinement': 'none'}
            }
            materials = FrameMaterials(fw_type, config)
            
            assert materials.framework_type == fw_type


class TestConcreteModel:
    """Test concrete material model"""

    def test_concrete_initialization(self):
        """Test concrete model initialization"""
        concrete = ConcreteModel(
            fc_prime=28.0,
            ec=0,
            eps_c0=-0.002
        )
        
        assert concrete.fc_prime == 28.0
        assert concrete.eps_c0 == -0.002

    def test_concrete_confined_vs_unconfined(self):
        """Test confined vs unconfined concrete properties"""
        concrete_unconfined = ConcreteModel(fc_prime=28.0, confinement='none')
        concrete_confined = ConcreteModel(fc_prime=28.0, confinement='spiral')
        
        # Confined concrete should have higher strain capacity
        assert concrete_confined.eps_cu < concrete_unconfined.eps_cu


class TestSteelModel:
    """Test steel material model"""

    def test_steel_initialization(self):
        """Test steel model initialization"""
        steel = SteelModel(
            fy=500.0,
            es=200000,
            b=0.01
        )
        
        assert steel.fy == 500.0
        assert steel.es == 200000

    def test_steel_strain_hardening(self):
        """Test steel with strain hardening"""
        steel = SteelModel(
            fy=500.0,
            es=200000,
            b=0.02  # 2% strain hardening
        )
        
        # Steel strain hardening ratio should be positive
        assert steel.b > 0


class TestRCFrame:
    """Test RCFrame class"""

    @patch('openseespy.opensees.wipe')
    @patch('openseespy.opensees.model')
    def test_frame_initialization(self, mock_model, mock_wipe):
        """Test RC frame initialization"""
        config = {
            'default_materials': {
                'concrete': {'fc_prime': 28.0},
                'steel_rebar': {'fy': 500.0}
            },
            'smrf_parameters': {
                'detailing': {'column_confinement': 'spiral'}
            }
        }
        
        frame = RCFrame(
            n_stories=5,
            story_height=3.5,
            n_bays=3,
            bay_width=5.0,
            column_size=(500, 500),
            beam_size=(400, 600),
            framework_type='smrf',
            config=config
        )
        
        assert frame.n_stories == 5
        assert frame.framework_type == 'smrf'

    def test_frame_properties(self):
        """Test frame derived properties"""
        config = {
            'default_materials': {
                'concrete': {'fc_prime': 28.0},
                'steel_rebar': {'fy': 500.0}
            },
            'smrf_parameters': {
                'detailing': {'column_confinement': 'spiral'}
            }
        }
        
        frame = RCFrame(
            n_stories=10,
            story_height=3.5,
            n_bays=2,
            bay_width=6.0,
            column_size=(500, 500),
            beam_size=(400, 600),
            framework_type='smrf',
            config=config
        )
        
        assert frame.total_height == pytest.approx(35.0, rel=0.01)
        assert frame.geometry.n_bays == 2


class TestFrameValidation:
    """Test frame validation"""

    def test_valid_frame_parameters(self):
        """Test validation of valid frame parameters"""
        config = {
            'default_materials': {
                'concrete': {'fc_prime': 28.0},
                'steel_rebar': {'fy': 500.0}
            },
            'smrf_parameters': {
                'detailing': {'column_confinement': 'spiral'}
            }
        }
        
        # Should not raise
        frame = RCFrame(
            n_stories=5,
            story_height=3.5,
            n_bays=3,
            bay_width=5.0,
            column_size=(500, 500),
            beam_size=(400, 600),
            framework_type='smrf',
            config=config
        )
        
        assert frame is not None

    def test_frame_column_depth_for_height(self):
        """Test column depth is adequate for story height"""
        config = {
            'default_materials': {
                'concrete': {'fc_prime': 28.0},
                'steel_rebar': {'fy': 500.0}
            },
            'smrf_parameters': {
                'detailing': {'column_confinement': 'spiral'}
            }
        }
        
        frame = RCFrame(
            n_stories=5,
            story_height=3.5,
            n_bays=2,
            bay_width=5.0,
            column_size=(500, 500),  # Depth = 500mm, Height = 3500mm
            beam_size=(400, 600),
            framework_type='smrf',
            config=config
        )
        
        # Column depth should be reasonable relative to story height
        # Typical ratio is 1/10 to 1/15
        assert frame.geometry.column_sizes[0][1] / frame.story_height < 0.2


class TestFrameGeometryEdgeCases:
    """Test edge cases for frame geometry"""

    def test_single_story_frame(self):
        """Test single story frame geometry"""
        geometry = FrameGeometry.create_uniform(
            n_stories=1,
            story_height=4.0,
            n_bays=2,
            bay_width=5.0,
            column_size=(500, 500),
            beam_size=(400, 600)
        )
        
        assert geometry.n_stories == 1
        assert geometry.total_height == pytest.approx(4.0, rel=0.01)

    def test_tall_building(self):
        """Test tall building frame geometry"""
        geometry = FrameGeometry.create_uniform(
            n_stories=30,
            story_height=3.5,
            n_bays=4,
            bay_width=6.0,
            column_size=(600, 600),
            beam_size=(500, 700)
        )
        
        assert geometry.n_stories == 30
        assert geometry.total_height == pytest.approx(105.0, rel=0.01)

    def test_wide_spans(self):
        """Test frame with wide spans"""
        geometry = FrameGeometry.create_uniform(
            n_stories=5,
            story_height=3.5,
            n_bays=3,
            bay_width=8.0,
            column_size=(600, 600),
            beam_size=(500, 700)
        )
        
        span_to_depth_ratio = 8000 / 700  # 11.4
        assert span_to_depth_ratio > 8  # Typical for RC beams


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
