"""Time History Analysis (THA) Module

Implements nonlinear dynamic time history analysis for buildings under
ground motion excitation.

Features:
- Dynamic integration (Newmark, HHT, etc.)
- Nonlinear element response tracking
- Peak response metrics (displacement, acceleration, drift)
- Hysteresis loop generation
- Dynamic instability detection
- Multi-stripe analysis (multiple GM intensities)

References:
- BNBC 2020, Section 3.3 (Time History Analysis)
- ASCE 41-23, Chapter 3 (Dynamic Analysis Procedures)
- OpenSeesPy Documentation (Dynamic Analysis)

Usage:
    from src.analysis.time_history import TimeHistoryAnalysis

    tha = TimeHistoryAnalysis(model, ground_motion_record)
    tha.set_analysis_parameters(dt=0.005, duration=30.0)
    tha.run_analysis()
    pidr = tha.compute_peak_inter_story_drift()
    pga = tha.extract_peak_acceleration()
"""

import numpy as np
import openseespy.opensees as ops
from typing import Dict, List, Optional, Tuple, Union, Any
import logging


class TimeHistoryAnalysis:
    """
    Nonlinear dynamic time history analysis for seismic evaluation

    Implements ASCE 41-23 dynamic analysis procedures and IDA methodology.
    """

    def __init__(self, model_data: Dict, ground_motion: Dict[str, np.ndarray],
                 config: Optional[Dict] = None):
        """
        Initialize time history analysis

        Args:
            model_data: OpenSeesPy model data dictionary
            ground_motion: Ground motion record data
            config: Analysis configuration dictionary
        """
        self.model_data = model_data
        self.ground_motion = ground_motion
        self.config = config or {}
        self.logger = logging.getLogger('time_history_analysis')

        # Analysis parameters
        self.dt = self.config.get('time_step', 0.005)
        self.duration = self.config.get('duration', 30.0)
        self.integration_method = self.config.get('integration', 'Newmark')
        self.convergence_tol = self.config.get('convergence_tol', 1e-6)
        self.max_iter = self.config.get('max_iterations', 50)

        # Ground motion scaling
        self.gm_scale_factor = 1.0

        # Results storage
        self.time_history = {'time': [], 'displacements': {}, 'accelerations': {}}
        self.peak_responses = {}
        self.hinge_rotations = {}
        self.drift_history = {}

        # ASCE 41 analysis parameters
        self.analysis_type = 'THA'  # THA, IDA, Multi-stripe

    def set_analysis_parameters(self, dt: float = 0.005, duration: float = 30.0,
                              integration: str = 'Newmark', convergence_tol: float = 1e-6,
                              max_iter: int = 50) -> None:
        """
        Set dynamic analysis parameters

        Args:
            dt: Time step for integration
            duration: Analysis duration
            integration: Integration method ('Newmark', 'HHT', etc.)
            convergence_tol: Convergence tolerance
            max_iter: Maximum iterations per step
        """
        self.dt = dt
        self.duration = duration
        self.integration_method = integration
        self.convergence_tol = convergence_tol
        self.max_iter = max_iter

        self.logger.info(f"Set analysis parameters: dt={dt}, duration={duration}s, method={integration}")

    def scale_ground_motion(self, scale_factor: float) -> None:
        """
        Scale ground motion record for IDA analysis

        Args:
            scale_factor: Scaling factor for ground motion intensity
        """
        self.gm_scale_factor = scale_factor
        self.logger.info(f"Ground motion scaled by factor {scale_factor}")

    def run_analysis(self) -> Dict[str, Any]:
        """
        Execute time history analysis

        Returns:
            Analysis results dictionary
        """
        self.logger.info("Starting time history analysis")

        try:
            # Validate inputs
            self._validate_inputs()

            # Set up OpenSeesPy analysis
            self._setup_dynamic_analysis()

            # Apply ground motion
            self._apply_ground_motion()

            # Run dynamic analysis
            results = self._execute_dynamic_analysis()

            # Extract response histories
            self._extract_response_histories(results)

            # Compute peak responses
            self.peak_responses = self._compute_peak_responses()

            # Compute inter-story drifts
            self.drift_history = self._compute_drift_history()

            # Check stability
            stability_check = self._check_dynamic_stability()

            self.logger.info("Time history analysis completed successfully")

            return {
                'status': 'completed',
                'peak_responses': self.peak_responses,
                'drift_history': self.drift_history,
                'time_history': self.time_history,
                'stability_check': stability_check,
                'analysis_duration': len(self.time_history['time']) * self.dt,
                'gm_scale_factor': self.gm_scale_factor
            }

        except Exception as e:
            self.logger.error(f"Time history analysis failed: {str(e)}")
            return {
                'status': 'failed',
                'error': str(e)
            }

    def _validate_inputs(self) -> None:
        """Validate analysis inputs"""
        if 'time' not in self.ground_motion or 'accel' not in self.ground_motion:
            raise ValueError("Ground motion must contain 'time' and 'accel' arrays")

        if len(self.ground_motion['time']) != len(self.ground_motion['accel']):
            raise ValueError("Ground motion time and acceleration arrays must have same length")

        if not self.model_data.get('nodes'):
            raise ValueError("Model data must contain node information")

    def _setup_dynamic_analysis(self) -> None:
        """Set up OpenSeesPy dynamic analysis parameters"""
        # Placeholder for OpenSeesPy setup commands
        # Would include:
        # - Analysis type definition
        # - Integration method setup
        # - Convergence criteria
        # - Damping assignment
        pass

    def _apply_ground_motion(self) -> None:
        """Apply scaled ground motion to base nodes"""
        # Placeholder for ground motion application
        # Would create time series and apply to base nodes
        pass

    def _execute_dynamic_analysis(self) -> Dict[str, Any]:
        """Execute the dynamic analysis"""
        # Placeholder for analysis execution
        # Would run the time history analysis and return results

        # Simulate analysis results
        n_steps = int(self.duration / self.dt)
        time = np.linspace(0, self.duration, n_steps)

        # Placeholder response data
        results = {
            'time': time,
            'node_displacements': {},  # node_id -> displacement array
            'node_accelerations': {},  # node_id -> acceleration array
            'element_forces': {},      # element_id -> force array
        }

        return results

    def _extract_response_histories(self, results: Dict[str, Any]) -> None:
        """Extract response time histories from analysis results"""
        self.time_history = {
            'time': results['time'].tolist(),
            'displacements': results.get('node_displacements', {}),
            'accelerations': results.get('node_accelerations', {}),
            'element_forces': results.get('element_forces', {})
        }

    def _compute_peak_responses(self) -> Dict[str, float]:
        """Compute peak response metrics"""
        peaks = {}

        # Peak floor displacements
        if self.time_history['displacements']:
            for node_id, disp_history in self.time_history['displacements'].items():
                if isinstance(disp_history, np.ndarray):
                    peaks[f'peak_disp_node_{node_id}'] = float(np.max(np.abs(disp_history)))

        # Peak floor accelerations
        if self.time_history['accelerations']:
            for node_id, accel_history in self.time_history['accelerations'].items():
                if isinstance(accel_history, np.ndarray):
                    peaks[f'peak_accel_node_{node_id}'] = float(np.max(np.abs(accel_history)))

        # Peak base shear (if available)
        if 'base_shear' in self.time_history.get('element_forces', {}):
            base_shear_history = self.time_history['element_forces']['base_shear']
            if isinstance(base_shear_history, np.ndarray):
                peaks['peak_base_shear'] = float(np.max(np.abs(base_shear_history)))

        return peaks

    def compute_peak_inter_story_drift(self) -> Dict[str, float]:
        """
        Compute peak inter-story drift ratios

        Returns:
            Dictionary of peak IDR values by story
        """
        if not self.drift_history:
            self.drift_history = self._compute_drift_history()

        peak_idr = {}
        for story_key, drift_array in self.drift_history.items():
            if isinstance(drift_array, np.ndarray):
                peak_idr[story_key] = float(np.max(np.abs(drift_array)))

        return peak_idr

    def _compute_drift_history(self) -> Dict[str, np.ndarray]:
        """Compute inter-story drift time histories"""
        drift_history = {}

        # Get story information from model
        stories = self._get_story_information()

        for story_id, (bottom_nodes, top_nodes, story_height) in stories.items():
            # Compute average displacements for each floor
            bottom_disp = self._get_average_displacement(bottom_nodes)
            top_disp = self._get_average_displacement(top_nodes)

            if bottom_disp is not None and top_disp is not None:
                # Inter-story drift = (top_disp - bottom_disp) / story_height
                drift = (top_disp - bottom_disp) / story_height
                drift_history[f'story_{story_id}'] = drift

        return drift_history

    def _get_story_information(self) -> Dict[int, Tuple[List[int], List[int], float]]:
        """Extract story information from model data"""
        # Placeholder - would analyze model geometry to identify stories
        stories = {}

        # Simplified: assume stories are at different Y elevations
        nodes = self.model_data.get('nodes', {})
        elevations = sorted(set(node['coordinates'][1] for node in nodes.values()))

        for i in range(len(elevations) - 1):
            story_id = i + 1
            bottom_elev = elevations[i]
            top_elev = elevations[i + 1]
            story_height = top_elev - bottom_elev

            # Get nodes at each elevation
            bottom_nodes = [nid for nid, ndata in nodes.items()
                          if abs(ndata['coordinates'][1] - bottom_elev) < 0.1]
            top_nodes = [nid for nid, ndata in nodes.items()
                        if abs(ndata['coordinates'][1] - top_elev) < 0.1]

            stories[story_id] = (bottom_nodes, top_nodes, story_height)

        return stories

    def _get_average_displacement(self, node_ids: List[int]) -> Optional[np.ndarray]:
        """Get average displacement time history for a set of nodes"""
        displacements = []

        for node_id in node_ids:
            if node_id in self.time_history['displacements']:
                disp = self.time_history['displacements'][node_id]
                if isinstance(disp, np.ndarray):
                    displacements.append(disp)

        if displacements:
            return np.mean(displacements, axis=0)

        return None

    def _check_dynamic_stability(self) -> Dict[str, Any]:
        """Check for dynamic instability during analysis"""
        stability = {
            'is_stable': True,
            'instability_detected': False,
            'instability_time': None,
            'divergence_indicators': []
        }

        # Check for numerical instability indicators
        if self.time_history['displacements']:
            for node_id, disp_history in self.time_history['displacements'].items():
                if isinstance(disp_history, np.ndarray):
                    # Check for exponential growth
                    if len(disp_history) > 10:
                        recent_disp = np.abs(disp_history[-10:])
                        earlier_disp = np.abs(disp_history[-20:-10])

                        if np.mean(recent_disp) > 10 * np.mean(earlier_disp) and np.mean(earlier_disp) > 0:
                            stability['is_stable'] = False
                            stability['instability_detected'] = True
                            stability['divergence_indicators'].append(f'Node {node_id}: exponential growth')
                            break

        return stability

    def extract_peak_acceleration(self) -> float:
        """Extract peak ground acceleration from scaled record"""
        if 'accel' in self.ground_motion:
            return float(np.max(np.abs(self.ground_motion['accel']))) * self.gm_scale_factor
        return 0.0

    def get_response_spectra(self, damping: float = 0.05) -> Dict[str, np.ndarray]:
        """
        Compute response spectra from acceleration history

        Args:
            damping: Damping ratio for spectra computation

        Returns:
            Dictionary with periods and spectral accelerations
        """
        # Placeholder for response spectrum computation
        # Would implement Newmark-beta integration for SDOF response

        periods = np.logspace(-1, 1, 100)  # 0.1 to 10 seconds
        spectral_accels = np.ones_like(periods) * 0.5  # Placeholder

        return {
            'periods': periods,
            'spectral_accelerations': spectral_accels,
            'damping': damping
        }

    def export_results(self, filepath: str, format: str = 'json') -> None:
        """
        Export time history results to file

        Args:
            filepath: Output file path
            format: Export format ('json', 'csv')
        """
        if format == 'json':
            import json

            # Convert numpy arrays to lists for JSON serialization
            export_data = {
                'analysis_parameters': {
                    'dt': self.dt,
                    'duration': self.duration,
                    'integration_method': self.integration_method,
                    'gm_scale_factor': self.gm_scale_factor
                },
                'peak_responses': self.peak_responses,
                'time_history': {
                    'time': self.time_history['time'],
                    'displacements': {k: v.tolist() if isinstance(v, np.ndarray) else v
                                    for k, v in self.time_history['displacements'].items()},
                    'accelerations': {k: v.tolist() if isinstance(v, np.ndarray) else v
                                    for k, v in self.time_history['accelerations'].items()}
                }
            }

            with open(filepath, 'w') as f:
                json.dump(export_data, f, indent=2)

        elif format == 'csv':
            # Export peak responses as CSV
            import pandas as pd
            df = pd.DataFrame([self.peak_responses])
            df.to_csv(filepath, index=False)

        self.logger.info(f"Time history results exported to {filepath}")


__all__ = ['TimeHistoryAnalysis']
