# rc_frame.py - Parametric RC Frame Model Generator
"""
Parametric Reinforced Concrete Frame Model Generator for OpenSeesPy

This module provides classes for creating parametric RC moment-resisting frame
models with different framework types (Non-Sway, OMRF, IMRF, SMRF) compliant
with BNBC 2020 seismic design provisions.

Classes:
    RCFrame: Main parametric frame generator
    FrameGeometry: Frame geometric properties
    FrameMaterials: Material definitions for different framework types
"""

import openseespy.opensees as ops
import numpy as np
import yaml
from typing import Dict, List, Optional, Tuple, Union
from pathlib import Path


class FrameGeometry:
    """Geometric properties of RC frame building"""

    def __init__(self, n_stories: int, story_heights: List[float],
                 bay_widths: List[float], column_sizes: List[Tuple[float, float]],
                 beam_sizes: List[Tuple[float, float]]):
        """
        Initialize frame geometry

        Args:
            n_stories: Number of stories
            story_heights: Height of each story [m]
            bay_widths: Width of each bay [m]
            column_sizes: (width, depth) for each story [mm]
            beam_sizes: (width, depth) for each story [mm]
        """
        self.n_stories = n_stories
        self.story_heights = story_heights
        self.bay_widths = bay_widths
        self.column_sizes = column_sizes
        self.beam_sizes = beam_sizes

        # Derived properties
        self.total_height = sum(story_heights)
        self.n_bays = len(bay_widths)
        self.floor_levels = np.cumsum([0] + story_heights)

    @classmethod
    def create_uniform(cls, n_stories: int, story_height: float,
                      n_bays: int, bay_width: float,
                      column_size: Tuple[float, float],
                      beam_size: Tuple[float, float]) -> 'FrameGeometry':
        """Create uniform frame geometry"""
        story_heights = [story_height] * n_stories
        bay_widths = [bay_width] * n_bays
        column_sizes = [column_size] * n_stories
        beam_sizes = [beam_size] * n_stories

        return cls(n_stories, story_heights, bay_widths, column_sizes, beam_sizes)


class FrameMaterials:
    """Material definitions for different framework types"""

    def __init__(self, framework_type: str, config: Dict):
        """
        Initialize materials based on framework type

        Args:
            framework_type: 'nonsway', 'omrf', 'imrf', 'smrf'
            config: BNBC configuration dictionary
        """
        self.framework_type = framework_type
        self.config = config
        self.materials = {}

        # Load default material properties
        defaults = config.get('default_materials', {})
        concrete_props = defaults.get('concrete', {})
        steel_props = defaults.get('steel_rebar', {})

        # Framework-specific parameters
        fw_params = config.get(f'{framework_type}_parameters', {})

        # Create materials
        self._create_concrete_materials(concrete_props, fw_params)
        self._create_steel_materials(steel_props, fw_params)

    def _create_concrete_materials(self, concrete_props: Dict, fw_params: Dict):
        """Create concrete materials based on framework type"""
        fc = concrete_props.get('fc_prime', 28.0)  # MPa
        confinement = fw_params.get('detailing', {}).get('column_confinement', 'none')

        if confinement == 'none':
            # Unconfined concrete (Concrete01)
            self.materials['concrete_unconfined'] = {
                'type': 'Concrete01',
                'fpc': -fc,
                'epsc0': -0.002,
                'fpcu': -0.2 * fc,
                'epsU': -0.006
            }
            self.materials['concrete_confined'] = self.materials['concrete_unconfined']

        elif confinement in ['light', 'moderate']:
            # Lightly/moderately confined (Concrete02)
            self.materials['concrete_unconfined'] = {
                'type': 'Concrete01',
                'fpc': -fc,
                'epsc0': -0.002,
                'fpcu': -0.2 * fc,
                'epsU': -0.006
            }
            # Confined concrete with slight enhancement
            fcc = fc * 1.1  # 10% enhancement
            self.materials['concrete_confined'] = {
                'type': 'Concrete02',
                'fpc': -fc,
                'epsc0': -0.002,
                'fpcu': -0.3 * fc,
                'epsU': -0.01,
                'lambda': 0.1,
                'ft': 0.1 * fc,
                'Ets': 0.05 * concrete_props.get('modulus_elasticity', 25000)
            }

        else:  # heavy confinement (Mander model)
            # Use Concrete02 with Mander confinement parameters
            fcc = fc * 1.3  # 30% enhancement for heavy confinement
            epscc = 0.004 + 0.0007 * fc  # Mander strain
            self.materials['concrete_confined'] = {
                'type': 'Concrete02',
                'fpc': -fcc,
                'epsc0': -epscc,
                'fpcu': -0.2 * fcc,
                'epsU': -0.02,
                'lambda': 0.1,
                'ft': 0.1 * fcc,
                'Ets': 0.05 * concrete_props.get('modulus_elasticity', 25000)
            }
            self.materials['concrete_unconfined'] = {
                'type': 'Concrete01',
                'fpc': -fc,
                'epsc0': -0.002,
                'fpcu': -0.2 * fc,
                'epsU': -0.006
            }

    def _create_steel_materials(self, steel_props: Dict, fw_params: Dict):
        """Create steel materials"""
        fy = steel_props.get('yield_strength', 420.0)  # MPa
        Es = steel_props.get('elastic_modulus', 200000.0)  # MPa

        # Steel01 (elastic-plastic)
        self.materials['steel'] = {
            'type': 'Steel01',
            'Fy': fy,
            'E0': Es,
            'b': 0.01  # Strain hardening ratio
        }

        # Steel02 (Menegotto-Pinto) for more accurate cyclic behavior
        self.materials['steel_menengotto'] = {
            'type': 'Steel02',
            'Fy': fy,
            'E0': Es,
            'b': 0.01,
            'R0': 18.5,
            'cR1': 0.925,
            'cR2': 0.15
        }


class RCFrame:
    """
    Parametric RC Moment-Resisting Frame Model

    Supports multiple framework types with different detailing requirements:
    - Non-Sway Frames (R=1.5)
    - Ordinary MRF (R=3)
    - Intermediate MRF (R=4)
    - Special MRF (R=5)
    """

    def __init__(self, n_stories: int, framework_type: str = 'smrf',
                 config_path: str = 'config/bnbc_parameters.yaml'):
        """
        Initialize RC frame model

        Args:
            n_stories: Number of stories
            framework_type: Framework type ('nonsway', 'omrf', 'imrf', 'smrf')
            config_path: Path to BNBC configuration file
        """
        self.n_stories = n_stories
        self.framework_type = framework_type.lower()

        # Load configuration
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        # Framework-specific parameters
        self.fw_params = self.config.get(f'{self.framework_type}_parameters', {})

        # Initialize components
        self.geometry: Optional[FrameGeometry] = None
        self.materials: Optional[FrameMaterials] = None
        self.nodes = {}
        self.elements = {}
        self.loads = {}

        # Analysis state
        self.model_created = False
        self.gravity_applied = False

    def set_geometry(self, story_height: float = 3.5, bay_width: float = 6.0,
                    column_size: Tuple[float, float] = (400, 400),
                    beam_size: Tuple[float, float] = (300, 500),
                    n_bays: int = 3):
        """
        Set frame geometry

        Args:
            story_height: Height of each story [m]
            bay_width: Width of each bay [m]
            column_size: (width, depth) [mm]
            beam_size: (width, depth) [mm]
            n_bays: Number of bays
        """
        self.geometry = FrameGeometry.create_uniform(
            self.n_stories, story_height, n_bays, bay_width,
            column_size, beam_size
        )

    @property
    def n_bays(self) -> int:
        """Get number of bays from geometry"""
        if self.geometry is None:
            raise ValueError("Geometry must be set to access n_bays")
        return self.geometry.n_bays

    def create_model(self):
        """Create OpenSeesPy model"""
        if self.geometry is None:
            raise ValueError("Geometry must be set before creating model")

        # Initialize OpenSees model
        ops.wipe()  # type: ignore
        ops.model('basic', '-ndm', 2, '-ndf', 3)  # type: ignore  # 2D model with 3 DOF

        # Create materials
        self.materials = FrameMaterials(self.framework_type, self.config)
        self._define_materials()

        # Create geometry
        self._create_nodes()
        self._create_elements()

        # Apply boundary conditions
        self._apply_boundary_conditions()

        self.model_created = True

    def _define_materials(self):
        """Define materials in OpenSees"""
        if self.materials is None:
            raise ValueError("Materials must be initialized before defining")
        
        for mat_name, mat_props in self.materials.materials.items():
            mat_type = mat_props['type']
            args = [k for k, v in mat_props.items() if k != 'type']

            if mat_type == 'Concrete01':
                ops.uniaxialMaterial('Concrete01', mat_name, *args)  # type: ignore
            elif mat_type == 'Concrete02':
                ops.uniaxialMaterial('Concrete02', mat_name, *args)  # type: ignore
            elif mat_type == 'Steel01':
                ops.uniaxialMaterial('Steel01', mat_name, *args)  # type: ignore
            elif mat_type == 'Steel02':
                ops.uniaxialMaterial('Steel02', mat_name, *args)  # type: ignore

    def _create_nodes(self):
        """Create nodes for frame"""
        assert self.geometry is not None, "Geometry must be set"
        node_id = 1

        for story in range(self.n_stories + 1):  # Include roof
            y_coord = self.geometry.floor_levels[story] * 1000  # Convert to mm

            for bay in range(self.n_bays + 1):  # Include rightmost column line
                x_coord = sum(self.geometry.bay_widths[:bay]) * 1000  # Convert to mm

                # Create node
                ops.node(node_id, x_coord, y_coord)  # type: ignore

                # Store node reference
                self.nodes[f'floor_{story}_bay_{bay}'] = node_id
                node_id += 1

    def _create_elements(self):
        """Create frame elements"""
        assert self.geometry is not None, "Geometry must be set"
        element_id = 1

        # Create columns
        for story in range(self.n_stories):
            for bay in range(self.n_bays + 1):  # Column lines
                node_i = self.nodes[f'floor_{story}_bay_{bay}']
                node_j = self.nodes[f'floor_{story+1}_bay_{bay}']

                # Column section properties
                col_size = self.geometry.column_sizes[story]
                A_col = col_size[0] * col_size[1]  # Area in mm²
                I_col = col_size[0] * col_size[1]**3 / 12  # Moment of inertia in mm⁴

                # Create fiber section for column
                section_id = self._create_column_section(story, col_size)

                # Create element
                ops.element('nonlinearBeamColumn', element_id, node_i, node_j,  # type: ignore
                           5, section_id, 1)  # 5 integration points

                self.elements[f'column_{story}_{bay}'] = element_id
                element_id += 1

        # Create beams
        for story in range(1, self.n_stories + 1):  # Skip ground floor
            for bay in range(self.n_bays):
                node_i = self.nodes[f'floor_{story}_bay_{bay}']
                node_j = self.nodes[f'floor_{story}_bay_{bay+1}']

                # Beam section properties
                beam_size = self.geometry.beam_sizes[story-1]
                A_beam = beam_size[0] * beam_size[1]
                I_beam = beam_size[0] * beam_size[1]**3 / 12

                # Create fiber section for beam
                section_id = self._create_beam_section(story-1, beam_size)

                # Create element
                ops.element('nonlinearBeamColumn', element_id, node_i, node_j,  # type: ignore
                           5, section_id, 1)

                self.elements[f'beam_{story}_{bay}'] = element_id
                element_id += 1

    def _create_column_section(self, story: int, size: Tuple[float, float]) -> int:
        """Create fiber section for column"""
        section_id = len(self.elements) + 1000  # Unique section ID

        width, depth = size
        cover = 40  # mm concrete cover

        # Create section
        ops.section('Fiber', section_id)  # type: ignore

        # Concrete fibers
        ops.patch('rect', 'concrete_confined', 10, 10,  # type: ignore
                 -width/2, -depth/2, width/2, depth/2)

        # Steel reinforcement
        rho_long = self.fw_params.get('design_factors', {}).get('longitudinal_reinforcement_ratio', 0.015)
        n_bars = self._calculate_longitudinal_bars(width, depth, rho_long)

        # Corner bars
        bar_dia = 16  # mm
        ops.layer('straight', 'steel', n_bars, bar_dia,  # type: ignore
                 -width/2 + cover, -depth/2 + cover,
                 -width/2 + cover, depth/2 - cover)

        return section_id

    def _create_beam_section(self, story: int, size: Tuple[float, float]) -> int:
        """Create fiber section for beam"""
        section_id = len(self.elements) + 2000  # Unique section ID

        width, depth = size
        cover = 40  # mm

        # Create section
        ops.section('Fiber', section_id)  # type: ignore

        # Concrete fibers
        ops.patch('rect', 'concrete_unconfined', 8, 8,  # type: ignore
                 -width/2, -depth/2, width/2, depth/2)

        # Steel reinforcement
        rho_top = 0.012  # Top reinforcement ratio
        rho_bot = 0.020  # Bottom reinforcement ratio

        bar_dia = 12  # mm

        # Top steel
        n_top = int(rho_top * width * depth / (np.pi * (bar_dia/2)**2))
        ops.layer('straight', 'steel', n_top, bar_dia,  # type: ignore
                 -width/2 + cover, depth/2 - cover - bar_dia/2,
                 width/2 - cover, depth/2 - cover - bar_dia/2)

        # Bottom steel
        n_bot = int(rho_bot * width * depth / (np.pi * (bar_dia/2)**2))
        ops.layer('straight', 'steel', n_bot, bar_dia,  # type: ignore
                 -width/2 + cover, -depth/2 + cover + bar_dia/2,
                 width/2 - cover, -depth/2 + cover + bar_dia/2)

        return section_id

    def _calculate_longitudinal_bars(self, width: float, depth: float, rho: float) -> int:
        """Calculate number of longitudinal bars"""
        bar_dia = 16  # mm
        bar_area = np.pi * (bar_dia/2)**2
        total_area = width * depth
        return max(4, int(rho * total_area / bar_area))  # Minimum 4 bars

    def _apply_boundary_conditions(self):
        """Apply boundary conditions (fixed base)"""
        # Fix base nodes (story 0)
        for bay in range(self.n_bays + 1):
            node_id = self.nodes[f'floor_0_bay_{bay}']
            ops.fix(node_id, 1, 1, 1)  # type: ignore  # Fix all DOF

    def apply_gravity_loads(self, floor_load: float = 4.0, roof_load: float = 3.0):
        """Apply gravity loads"""
        assert self.geometry is not None, "Geometry must be set"
        if not self.model_created:
            raise ValueError("Model must be created before applying loads")

        # Create load pattern
        ops.timeSeries('Constant', 1)  # type: ignore
        ops.pattern('Plain', 1, 1)  # type: ignore

        # Floor loads (uniformly distributed)
        for story in range(1, self.n_stories + 1):
            load_intensity = floor_load if story < self.n_stories else roof_load

            # Apply to beam nodes
            for bay in range(self.n_bays):
                node_id = self.nodes[f'floor_{story}_bay_{bay}']
                # Distributed load on beam (half to each node)
                beam_load = load_intensity * self.geometry.bay_widths[bay] / 2
                ops.load(node_id, 0, -beam_load, 0)  # type: ignore  # Vertical load

        self.gravity_applied = True

    def save_model(self, filepath: str):
        """Save model to JSON file"""
        assert self.geometry is not None, "Geometry must be set"
        assert self.materials is not None, "Materials must be set"
        
        model_data = {
            'framework_type': self.framework_type,
            'n_stories': self.n_stories,
            'geometry': {
                'story_heights': self.geometry.story_heights,
                'bay_widths': self.geometry.bay_widths,
                'column_sizes': self.geometry.column_sizes,
                'beam_sizes': self.geometry.beam_sizes
            },
            'materials': self.materials.materials,
            'nodes': self.nodes,
            'elements': self.elements
        }

        import json
        with open(filepath, 'w') as f:
            json.dump(model_data, f, indent=2)

    @classmethod
    def load_model(cls, filepath: str) -> 'RCFrame':
        """Load model from JSON file"""
        import json
        with open(filepath, 'r') as f:
            model_data = json.load(f)

        frame = cls(model_data['n_stories'], model_data['framework_type'])
        # Restore geometry and recreate model
        geom_data = model_data['geometry']
        frame.set_geometry(
            story_height=geom_data['story_heights'][0],  # Assume uniform
            bay_width=geom_data['bay_widths'][0],
            column_size=geom_data['column_sizes'][0],
            beam_size=geom_data['beam_sizes'][0],
            n_bays=len(geom_data['bay_widths'])
        )
        frame.create_model()

        return frame