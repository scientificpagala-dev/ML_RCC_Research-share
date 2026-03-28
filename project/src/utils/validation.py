# validation.py - Model and analysis validation utilities
"""
Validation utilities for OpenSeesPy models and analysis results

Provides comprehensive checks for model correctness, convergence,
and result validity to ensure reliable seismic analysis.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Union, Any
import warnings
import os


class ModelValidator:
    """
    Validates OpenSeesPy model correctness and stability

    Checks geometry, materials, loads, and boundary conditions.
    """

    @staticmethod
    def validate_geometry(model_data: Dict) -> Dict[str, Any]:
        """
        Validate model geometry and connectivity

        Args:
            model_data: Dictionary containing model information

        Returns:
            Validation results dictionary
        """
        validation = {
            'status': 'PASS',
            'warnings': [],
            'errors': [],
            'checks': {}
        }

        # Check node coordinates
        nodes = model_data.get('nodes', {})
        if not nodes:
            validation['errors'].append("No nodes defined")
            validation['status'] = 'FAIL'
            return validation

        # Check for duplicate node IDs
        node_ids = list(nodes.keys())
        if len(node_ids) != len(set(node_ids)):
            validation['errors'].append("Duplicate node IDs found")
            validation['status'] = 'FAIL'

        # Check element connectivity
        elements = model_data.get('elements', {})
        for elem_id, elem_data in elements.items():
            node_tags = elem_data.get('node_tags', [])
            missing_nodes = [tag for tag in node_tags if tag not in nodes]
            if missing_nodes:
                validation['errors'].append(
                    f"Element {elem_id} references non-existent nodes: {missing_nodes}")
                validation['status'] = 'FAIL'

        # Check story heights
        story_heights = model_data.get('story_heights', [])
        if story_heights:
            if any(h <= 0 for h in story_heights):
                validation['warnings'].append("Zero or negative story heights found")

            # Check for reasonable height ranges (0.5m to 10m per story)
            unreasonable_heights = [h for h in story_heights if not 0.5 <= h <= 10.0]
            if unreasonable_heights:
                validation['warnings'].append(
                    f"Unreasonable story heights: {unreasonable_heights}")

        # Check column-to-beam ratios
        validation['checks']['geometry'] = len(validation['errors']) == 0

        return validation

    @staticmethod
    def validate_materials(model_data: Dict) -> Dict[str, Any]:
        """
        Validate material properties and definitions

        Args:
            model_data: Dictionary containing model information

        Returns:
            Validation results dictionary
        """
        validation = {
            'status': 'PASS',
            'warnings': [],
            'errors': [],
            'checks': {}
        }

        materials = model_data.get('materials', {})

        # Check for required material types
        required_types = {'concrete', 'steel'}
        defined_types = set()
        for mat_id, mat_data in materials.items():
            mat_type = mat_data.get('type', '').lower()
            defined_types.add(mat_type)

            # Validate material properties
            if mat_type == 'concrete01':
                required_props = ['fc', 'ec', 'fcu', 'ecu']
            elif mat_type == 'steel01':
                required_props = ['fy', 'e0', 'b']
            else:
                required_props = []

            missing_props = [prop for prop in required_props
                           if prop not in mat_data.get('properties', {})]
            if missing_props:
                validation['errors'].append(
                    f"Material {mat_id} missing properties: {missing_props}")

        missing_types = required_types - defined_types
        if missing_types:
            validation['warnings'].append(f"Missing material types: {missing_types}")

        # Check for reasonable property values
        for mat_id, mat_data in materials.items():
            props = mat_data.get('properties', {})

            # Concrete strength check
            if 'fc' in props:
                fc = props['fc']
                if not -100 <= fc <= -10:  # Negative for compression
                    validation['warnings'].append(
                        f"Material {mat_id}: unusual concrete strength {fc} MPa")

            # Steel yield strength check
            if 'fy' in props:
                fy = props['fy']
                if not 200 <= fy <= 800:
                    validation['warnings'].append(
                        f"Material {mat_id}: unusual steel yield strength {fy} MPa")

        validation['checks']['materials'] = len(validation['errors']) == 0

        return validation

    @staticmethod
    def validate_loads(model_data: Dict) -> Dict[str, Any]:
        """
        Validate load patterns and application

        Args:
            model_data: Dictionary containing model information

        Returns:
            Validation results dictionary
        """
        validation = {
            'status': 'PASS',
            'warnings': [],
            'errors': [],
            'checks': {}
        }

        loads = model_data.get('loads', {})

        # Check gravity loads
        gravity_loads = loads.get('gravity', {})
        if not gravity_loads:
            validation['warnings'].append("No gravity loads defined")

        # Check lateral loads
        lateral_loads = loads.get('lateral', {})
        if not lateral_loads:
            validation['warnings'].append("No lateral loads defined")

        # Validate load magnitudes
        for load_type, load_data in loads.items():
            if isinstance(load_data, dict):
                for component, values in load_data.items():
                    if isinstance(values, (list, np.ndarray)):
                        if any(abs(v) > 1e6 for v in values):  # Unreasonably large loads
                            validation['warnings'].append(
                                f"Very large {load_type} loads on {component}")

        validation['checks']['loads'] = len(validation['errors']) == 0

        return validation

    @staticmethod
    def validate_boundary_conditions(model_data: Dict) -> Dict[str, Any]:
        """
        Validate boundary conditions and constraints

        Args:
            model_data: Dictionary containing model information

        Returns:
            Validation results dictionary
        """
        validation = {
            'status': 'PASS',
            'warnings': [],
            'errors': [],
            'checks': {}
        }

        constraints = model_data.get('constraints', {})

        # Check for base fixity
        base_nodes = model_data.get('base_nodes', [])
        if base_nodes:
            fixed_dofs = constraints.get('fixed', {})
            unfixed_base = [node for node in base_nodes if node not in fixed_dofs]
            if unfixed_base:
                validation['errors'].append(
                    f"Base nodes not fixed: {unfixed_base}")
                validation['status'] = 'FAIL'

        # Check for rigid diaphragm constraints
        diaphragms = constraints.get('rigid_diaphragm', {})
        if not diaphragms:
            validation['warnings'].append("No rigid diaphragm constraints defined")

        validation['checks']['boundary_conditions'] = len(validation['errors']) == 0

        return validation

    @staticmethod
    def run_full_validation(model_data: Dict) -> Dict[str, Any]:
        """
        Run complete model validation

        Args:
            model_data: Dictionary containing model information

        Returns:
            Comprehensive validation results
        """
        validations = {
            'geometry': ModelValidator.validate_geometry(model_data),
            'materials': ModelValidator.validate_materials(model_data),
            'loads': ModelValidator.validate_loads(model_data),
            'boundary_conditions': ModelValidator.validate_boundary_conditions(model_data)
        }

        # Aggregate results
        overall_status = 'PASS'
        all_warnings = []
        all_errors = []

        for check_name, result in validations.items():
            if result['status'] == 'FAIL':
                overall_status = 'FAIL'
            all_warnings.extend(result['warnings'])
            all_errors.extend(result['errors'])

        return {
            'overall_status': overall_status,
            'detailed_results': validations,
            'total_warnings': len(all_warnings),
            'total_errors': len(all_errors),
            'warnings': all_warnings,
            'errors': all_errors
        }


class AnalysisValidator:
    """
    Validates analysis results and convergence

    Checks IDA curves, convergence, and result consistency.
    """

    @staticmethod
    def validate_ida_results(results_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Validate IDA analysis results

        Args:
            results_df: DataFrame containing IDA results

        Returns:
            Validation results dictionary
        """
        validation = {
            'status': 'PASS',
            'warnings': [],
            'errors': [],
            'checks': {}
        }

        # Check required columns
        required_cols = ['building_id', 'intensity_sa', 'pidr']
        missing_cols = [col for col in required_cols if col not in results_df.columns]
        if missing_cols:
            validation['errors'].append(f"Missing required columns: {missing_cols}")
            validation['status'] = 'FAIL'
            return validation

        # Check for valid PIDR values
        invalid_pidr = results_df[
            (results_df['pidr'] <= 0) |
            (results_df['pidr'] > 1.0) |
            results_df['pidr'].isna()
        ]
        if len(invalid_pidr) > 0:
            validation['errors'].append(f"Invalid PIDR values in {len(invalid_pidr)} records")
            validation['status'] = 'FAIL'

        # Check intensity range
        sa_range = results_df['intensity_sa'].agg(['min', 'max'])
        if sa_range['min'] < 0.01 or sa_range['max'] > 2.0:
            validation['warnings'].append(
                f"Unusual SA intensity range: {sa_range['min']:.3f} - {sa_range['max']:.3f} g")

        # Check for IDA curve monotonicity
        monotonic_issues = AnalysisValidator._check_ida_monotonicity(results_df)
        if monotonic_issues > len(results_df['building_id'].unique()) * 0.1:
            validation['warnings'].append(
                f"Monotonicity issues in {monotonic_issues} building IDA curves")

        # Check sample size per building
        samples_per_building = results_df.groupby('building_id').size()
        min_samples = samples_per_building.min()
        if min_samples < 5:
            validation['warnings'].append(
                f"Some buildings have very few samples: min = {min_samples}")

        validation['checks']['ida_results'] = len(validation['errors']) == 0

        return validation

    @staticmethod
    def _check_ida_monotonicity(results_df: pd.DataFrame) -> int:
        """Check IDA curve monotonicity for each building"""
        issues = 0

        for building_id in results_df['building_id'].unique():
            building_data = results_df[results_df['building_id'] == building_id]
            building_data = building_data.sort_values('intensity_sa')

            pidr_values = building_data['pidr'].values
            sa_values = building_data['intensity_sa'].values

            # Check for significant non-monotonicity
            for i in range(1, len(pidr_values)):
                if pidr_values[i] < pidr_values[i-1] * 0.7:  # 30% drop
                    issues += 1
                    break

        return issues

    @staticmethod
    def validate_convergence(analysis_log: Optional[str] = None,
                           convergence_data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Validate analysis convergence

        Args:
            analysis_log: Path to analysis log file or log content
            convergence_data: Dictionary with convergence information

        Returns:
            Validation results dictionary
        """
        validation = {
            'status': 'PASS',
            'warnings': [],
            'errors': [],
            'checks': {}
        }

        if analysis_log and os.path.exists(analysis_log):
            with open(analysis_log, 'r') as f:
                log_content = f.read()
        elif isinstance(analysis_log, str):
            log_content = analysis_log
        else:
            log_content = None

        if convergence_data:
            # Check convergence ratios
            if 'convergence_ratios' in convergence_data:
                ratios = convergence_data['convergence_ratios']
                failed_steps = sum(1 for r in ratios if r > 1e-6)  # Loose tolerance
                if failed_steps > len(ratios) * 0.05:  # More than 5% failed
                    validation['warnings'].append(
                        f"Convergence issues in {failed_steps}/{len(ratios)} steps")

            # Check iteration counts
            if 'iterations' in convergence_data:
                avg_iters = np.mean(convergence_data['iterations'])
                max_iters = np.max(convergence_data['iterations'])
                if avg_iters > 50:
                    validation['warnings'].append(
                        f"High average iterations: {avg_iters:.1f}")
                if max_iters > 100:
                    validation['warnings'].append(
                        f"Very high max iterations: {max_iters}")

        if log_content:
            # Check for common error patterns
            error_patterns = [
                'analysis failed',
                'convergence not achieved',
                'singular matrix',
                'negative pivot'
            ]

            for pattern in error_patterns:
                if pattern.lower() in log_content.lower():
                    validation['errors'].append(f"Analysis error detected: {pattern}")
                    validation['status'] = 'FAIL'

        validation['checks']['convergence'] = len(validation['errors']) == 0

        return validation

    @staticmethod
    def validate_ground_motion(gm_data: Dict[str, np.ndarray]) -> Dict[str, Any]:
        """
        Validate ground motion record

        Args:
            gm_data: Ground motion data dictionary

        Returns:
            Validation results dictionary
        """
        validation = {
            'status': 'PASS',
            'warnings': [],
            'errors': [],
            'checks': {}
        }

        # Check required fields
        required_fields = ['time', 'accel']
        missing_fields = [f for f in required_fields if f not in gm_data]
        if missing_fields:
            validation['errors'].append(f"Missing ground motion fields: {missing_fields}")
            validation['status'] = 'FAIL'
            return validation

        time = gm_data['time']
        accel = gm_data['accel']

        # Check array lengths
        if len(time) != len(accel):
            validation['errors'].append("Time and acceleration arrays have different lengths")
            validation['status'] = 'FAIL'

        # Check time step consistency
        if len(time) > 1:
            dt = np.diff(time)
            dt_std = np.std(dt)
            dt_mean = np.mean(dt)
            if dt_std / dt_mean > 0.01:  # More than 1% variation
                validation['warnings'].append("Inconsistent time steps in ground motion")

        # Check acceleration units (should be in g, roughly -2 to 2 for most earthquakes)
        accel_range = np.abs(accel).max()
        if accel_range > 5.0:
            validation['warnings'].append(f"Very high acceleration: {accel_range:.2f} g")
        elif accel_range < 0.01:
            validation['warnings'].append(f"Very low acceleration: {accel_range:.4f} g")

        # Check for PGA
        pga = np.abs(accel).max()
        if pga < 0.05:
            validation['warnings'].append(f"Low PGA: {pga:.3f} g")

        validation['checks']['ground_motion'] = len(validation['errors']) == 0

        return validation


class PerformanceValidator:
    """
    Validates performance metrics and ML model results

    Checks prediction accuracy, feature importance, and model stability.
    """

    @staticmethod
    def validate_ml_predictions(predictions: np.ndarray,
                              actuals: np.ndarray,
                              model_name: str = "Model") -> Dict[str, Any]:
        """
        Validate ML model predictions

        Args:
            predictions: Model predictions
            actuals: Actual values
            model_name: Name of the model for reporting

        Returns:
            Validation results dictionary
        """
        validation = {
            'status': 'PASS',
            'warnings': [],
            'errors': [],
            'metrics': {},
            'checks': {}
        }

        # Basic checks
        if len(predictions) != len(actuals):
            validation['errors'].append("Predictions and actuals have different lengths")
            validation['status'] = 'FAIL'
            return validation

        if len(predictions) == 0:
            validation['errors'].append("Empty prediction arrays")
            validation['status'] = 'FAIL'
            return validation

        # Calculate metrics
        errors = predictions - actuals
        mae = np.mean(np.abs(errors))
        mse = np.mean(errors**2)
        rmse = np.sqrt(mse)
        mape = np.mean(np.abs(errors / actuals)) * 100

        # R-squared
        ss_res = np.sum(errors**2)
        ss_tot = np.sum((actuals - np.mean(actuals))**2)
        r2 = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

        validation['metrics'] = {
            'mae': mae,
            'rmse': rmse,
            'mape': mape,
            'r2': r2,
            'n_samples': len(predictions)
        }

        # Performance checks
        if r2 < 0:
            validation['warnings'].append(f"{model_name}: Negative R² ({r2:.3f})")
        elif r2 < 0.5:
            validation['warnings'].append(f"{model_name}: Low R² ({r2:.3f})")

        if mape > 50:
            validation['warnings'].append(f"{model_name}: High MAPE ({mape:.1f}%)")

        # Check for prediction bounds
        pred_range = np.ptp(predictions)
        actual_range = np.ptp(actuals)
        if pred_range / actual_range > 2.0:
            validation['warnings'].append(f"{model_name}: Predictions have much wider range than actuals")

        validation['checks']['ml_predictions'] = len(validation['errors']) == 0

        return validation

    @staticmethod
    def validate_feature_importance(feature_importance: Dict[str, float],
                                  expected_features: List[str]) -> Dict[str, Any]:
        """
        Validate feature importance results

        Args:
            feature_importance: Dictionary of feature importances
            expected_features: List of expected feature names

        Returns:
            Validation results dictionary
        """
        validation = {
            'status': 'PASS',
            'warnings': [],
            'errors': [],
            'checks': {}
        }

        # Check for expected features
        missing_features = [f for f in expected_features if f not in feature_importance]
        if missing_features:
            validation['warnings'].append(f"Missing features in importance: {missing_features}")

        # Check importance values
        importance_values = list(feature_importance.values())
        if any(np.isnan(v) or np.isinf(v) for v in importance_values):
            validation['errors'].append("Invalid importance values (NaN or Inf)")
            validation['status'] = 'FAIL'

        # Check for zero importance
        zero_importance = [f for f, v in feature_importance.items() if abs(v) < 1e-6]
        if len(zero_importance) > len(feature_importance) * 0.5:
            validation['warnings'].append(f"Many features have zero importance: {len(zero_importance)}")

        # Check importance distribution
        if importance_values:
            total_importance = sum(abs(v) for v in importance_values)
            if total_importance < 0.1:
                validation['warnings'].append("Very low total feature importance")

        validation['checks']['feature_importance'] = len(validation['errors']) == 0

        return validation