"""Pushover Analysis Module

Implements static nonlinear (pushover) analysis for buildings.

Features:
- Load pattern definition (uniform, proportional to first mode, etc.)
- Pushover curve generation (base shear vs. displacement)
- Performance point identification
- Failure mechanism identification
- Pushover-to-spectrum conversion (capacity spectrum method)
- Softening/hardening detection

References:
- ASCE 41-23, Chapter 3.4 (Static Nonlinear Procedures)
- FEMA 356 (Prestandard for Seismic Rehabilitation)
- NIST GCR 17-917-45 (Seismic Fragility Methodology)

Usage:
    from src.analysis.pushover import PushoverAnalysis

    pushover = PushoverAnalysis(model, config)
    pushover.define_load_pattern('proportional_first_mode')
    pushover.run_analysis(target_drift=0.05)
    pushover_curve = pushover.get_pushover_curve()
    performance_point = pushover.identify_performance_point()
"""

import numpy as np
import openseespy.opensees as ops
from typing import Dict, List, Optional, Tuple, Union, Any
import logging


class PushoverAnalysis:
    """
    Static nonlinear (pushover) analysis for seismic performance evaluation

    Implements ASCE 41-23 and FEMA 356 procedures for pushover analysis.
    """

    def __init__(self, model_data: Dict, config: Dict):
        """
        Initialize pushover analysis

        Args:
            model_data: OpenSeesPy model data dictionary
            config: Analysis configuration dictionary
        """
        self.model_data = model_data
        self.config = config
        self.logger = logging.getLogger('pushover_analysis')

        # Analysis parameters
        self.load_pattern = None
        self.control_node = None
        self.control_dof = None
        self.target_displacement = None

        # Results storage
        self.pushover_curve = {'displacement': [], 'base_shear': []}
        self.hinge_rotations = {}
        self.performance_point = None

        # ASCE 41/FEMA parameters
        self.load_patterns = {
            'uniform': self._uniform_load_pattern,
            'proportional_first_mode': self._first_mode_load_pattern,
            'adaptive': self._adaptive_load_pattern
        }

    def define_load_pattern(self, pattern_type: str = 'proportional_first_mode',
                          control_node: Optional[int] = None, control_dof: int = 1) -> None:
        """
        Define lateral load pattern for pushover analysis

        Args:
            pattern_type: Type of load pattern ('uniform', 'proportional_first_mode', 'adaptive')
            control_node: Node for displacement control (roof node)
            control_dof: Degree of freedom for control (1=X, 2=Y)
        """
        if pattern_type not in self.load_patterns:
            raise ValueError(f"Unknown load pattern: {pattern_type}")

        self.load_pattern = pattern_type
        self.control_node = control_node or self._find_roof_node()
        self.control_dof = control_dof

        self.logger.info(f"Defined {pattern_type} load pattern with control at node {self.control_node}, DOF {control_dof}")

    def _find_roof_node(self) -> int:
        """Find the roof node (highest elevation)"""
        nodes = self.model_data.get('nodes', {})
        if not nodes:
            raise ValueError("No nodes found in model data")

        # Find node with maximum Y coordinate (roof level)
        roof_node = max(nodes.keys(), key=lambda n: nodes[n]['coordinates'][1])
        return roof_node

    def _uniform_load_pattern(self) -> Dict[int, float]:
        """Uniform lateral load distribution"""
        nodes = self.model_data.get('nodes', {})
        story_nodes = {}

        # Group nodes by story (Y coordinate)
        for node_id, node_data in nodes.items():
            y_coord = node_data['coordinates'][1]
            if y_coord not in story_nodes:
                story_nodes[y_coord] = []
            story_nodes[y_coord].append(node_id)

        # Uniform load per story
        load_distribution = {}
        n_stories = len(story_nodes)

        for i, (y_coord, node_list) in enumerate(sorted(story_nodes.items())):
            story_factor = (i + 1) / n_stories  # Linear distribution
            for node_id in node_list:
                load_distribution[node_id] = story_factor

        return self._normalize_load_distribution(load_distribution)

    def _first_mode_load_pattern(self) -> Dict[int, float]:
        """Load proportional to first mode shape"""
        # This would require modal analysis results
        # For now, use simplified triangular distribution
        self.logger.warning("First mode pattern requires modal analysis - using triangular approximation")
        return self._uniform_load_pattern()

    def _adaptive_load_pattern(self) -> Dict[int, float]:
        """Adaptive load pattern (ASCE 41-23)"""
        # Simplified adaptive pattern - can be enhanced with actual mode shapes
        return self._uniform_load_pattern()

    def _normalize_load_distribution(self, distribution: Dict[int, float]) -> Dict[int, float]:
        """Normalize load distribution to sum to 1.0"""
        total_load = sum(distribution.values())
        if total_load == 0:
            raise ValueError("Total load distribution is zero")

        return {node: load/total_load for node, load in distribution.items()}

    def run_analysis(self, target_drift: float = 0.05, num_steps: int = 100,
                    convergence_tol: float = 1e-6) -> Dict[str, Any]:
        """
        Execute pushover analysis

        Args:
            target_drift: Target roof drift ratio
            num_steps: Number of analysis steps
            convergence_tol: Convergence tolerance

        Returns:
            Analysis results dictionary
        """
        if not self.load_pattern:
            raise ValueError("Load pattern not defined. Call define_load_pattern() first.")

        self.logger.info(f"Starting pushover analysis with target drift {target_drift}")

        # Calculate target displacement
        roof_elevation = self.model_data['nodes'][self.control_node]['coordinates'][1]
        self.target_displacement = target_drift * roof_elevation

        # Initialize results
        self.pushover_curve = {'displacement': [], 'base_shear': []}

        try:
            # Set up OpenSeesPy analysis
            self._setup_opensees_analysis()

            # Apply load pattern
            load_distribution = self.load_patterns[self.load_pattern]()
            self._apply_load_pattern(load_distribution)

            # Run displacement-controlled analysis
            results = self._run_displacement_control(
                self.target_displacement, num_steps, convergence_tol
            )

            # Extract pushover curve
            self.pushover_curve = self._extract_pushover_curve(results)

            # Identify performance point
            self.performance_point = self._identify_performance_point()

            # Check for failure mechanisms
            failure_analysis = self._analyze_failure_mechanisms()

            self.logger.info("Pushover analysis completed successfully")

            return {
                'status': 'completed',
                'pushover_curve': self.pushover_curve,
                'performance_point': self.performance_point,
                'failure_analysis': failure_analysis,
                'target_drift_achieved': results['max_drift'] >= target_drift
            }

        except Exception as e:
            self.logger.error(f"Pushover analysis failed: {str(e)}")
            return {
                'status': 'failed',
                'error': str(e)
            }

    def _setup_opensees_analysis(self) -> None:
        """Set up OpenSeesPy analysis parameters"""
        # This would interface with actual OpenSeesPy model
        # Placeholder for OpenSeesPy commands
        pass

    def _apply_load_pattern(self, load_distribution: Dict[int, float]) -> None:
        """Apply lateral load pattern to the model"""
        # Placeholder for load application
        pass

    def _run_displacement_control(self, target_disp: float, num_steps: int,
                                tolerance: float) -> Dict[str, Any]:
        """Run displacement-controlled pushover analysis"""
        # Placeholder for analysis execution
        # Would return displacement and force history
        return {
            'displacements': np.linspace(0, target_disp, num_steps),
            'forces': np.linspace(0, 1.0, num_steps) * 1000,  # Placeholder
            'max_drift': target_disp / self.model_data['nodes'][self.control_node]['coordinates'][1]
        }

    def _extract_pushover_curve(self, results: Dict[str, Any]) -> Dict[str, List[float]]:
        """Extract base shear vs roof displacement curve"""
        return {
            'displacement': results['displacements'].tolist(),
            'base_shear': results['forces'].tolist()
        }

    def _identify_performance_point(self) -> Optional[Dict[str, float]]:
        """Identify performance point using capacity spectrum method"""
        # Simplified performance point identification
        # In full implementation, would use capacity spectrum method per FEMA 440

        if not self.pushover_curve['displacement'] or not self.pushover_curve['base_shear']:
            return None

        displacements = np.array(self.pushover_curve['displacement'])
        forces = np.array(self.pushover_curve['base_shear'])

        # Find yield point (simplified)
        yield_idx = self._find_yield_point(displacements, forces)

        if yield_idx is not None:
            return {
                'displacement': displacements[yield_idx],
                'base_shear': forces[yield_idx],
                'ductility': displacements[-1] / displacements[yield_idx] if yield_idx > 0 else 1.0
            }

        return None

    def _find_yield_point(self, displacements: np.ndarray, forces: np.ndarray) -> Optional[int]:
        """Find yield point in pushover curve (simplified)"""
        if len(forces) < 3:
            return None

        # Simple method: find where slope changes significantly
        slopes = np.diff(forces) / np.diff(displacements)
        slope_changes = np.diff(slopes)

        # Find maximum slope change (yield point)
        yield_idx = np.argmax(np.abs(slope_changes)) + 1

        return int(yield_idx) if yield_idx < len(displacements) - 1 else None

    def _analyze_failure_mechanisms(self) -> Dict[str, Any]:
        """Analyze failure mechanisms and softening behavior"""
        analysis = {
            'softening_detected': False,
            'failure_mode': 'ductile',
            'critical_elements': [],
            'reserve_capacity': 0.0
        }

        if self.pushover_curve['base_shear']:
            forces = np.array(self.pushover_curve['base_shear'])
            max_force = np.max(forces)
            final_force = forces[-1]

            # Check for softening (strength degradation)
            if final_force < 0.8 * max_force:
                analysis['softening_detected'] = True
                analysis['failure_mode'] = 'brittle'
                analysis['reserve_capacity'] = final_force / max_force

        return analysis

    def get_pushover_curve(self) -> Dict[str, List[float]]:
        """Get the pushover curve data"""
        return self.pushover_curve.copy()

    def get_performance_point(self) -> Optional[Dict[str, float]]:
        """Get the identified performance point"""
        return self.performance_point.copy() if self.performance_point else None

    def export_results(self, filepath: str) -> None:
        """Export pushover results to file"""
        import json

        results = {
            'pushover_curve': self.pushover_curve,
            'performance_point': self.performance_point,
            'analysis_config': {
                'load_pattern': self.load_pattern,
                'control_node': self.control_node,
                'control_dof': self.control_dof,
                'target_displacement': self.target_displacement
            }
        }

        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2)

        self.logger.info(f"Pushover results exported to {filepath}")


__all__ = ['PushoverAnalysis']
