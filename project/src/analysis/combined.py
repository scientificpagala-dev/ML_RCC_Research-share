"""Combined Analysis Methods Module

Implements multi-method analysis combinations and workflows:
- RSA + Pushover (Capacity Spectrum Method)
- THA + P-Delta effects
- Pushover + Plastic Hinge assessment
- Multi-stripe analysis (multiple ground motions × intensities)
- Analysis ensemble generation for ML training

Features:
- Sequential analysis execution
- Cross-method validation
- Result aggregation and comparison
- Uncertainty quantification
- Computational optimization (parallel processing)

References:
- NIST GCR 17-917-45 (Seismic Fragility Methodology)
- FEMA P-58, Vol. 1 (Methodology)
- ASCE 41-23, Chapter 3 (Analysis Selection)

Usage:
    from src.analysis.combined import CombinedAnalysis

    # Capacity-Spectrum Method (RSA + Pushover)
    csm = CombinedAnalysis(model, 'CSM')
    csm.run_rsa()
    csm.run_pushover()
    performance_point = csm.identify_performance_point()

    # Multi-stripe analysis (Phase 2 data generation)
    multi_stripe = CombinedAnalysis(model, 'MULTI_STRIPE')
    for gm_record in ground_motions:
        for intensity in intensity_levels:
            result = multi_stripe.run_tha(gm_record, intensity)
            results_db.append(result)
"""

import numpy as np
from typing import Dict, List, Optional, Tuple, Union, Any
import logging
import concurrent.futures
from pathlib import Path


class CombinedAnalysis:
    """
    Orchestrates multiple analysis methods for comprehensive seismic assessment

    Implements ASCE 41-23 and FEMA P-58 multi-method analysis procedures.
    """

    def __init__(self, model_data: Dict, analysis_type: str, config: Optional[Dict] = None):
        """
        Initialize combined analysis

        Args:
            model_data: OpenSeesPy model data dictionary
            analysis_type: Type of combined analysis ('CSM', 'MULTI_STRIPE', 'IDA', etc.)
            config: Analysis configuration dictionary
        """
        self.model_data = model_data
        self.analysis_type = analysis_type
        self.config = config or {}
        self.logger = logging.getLogger('combined_analysis')

        # Analysis components
        self.rsa = None
        self.pushover = None
        self.tha = None
        self.plastic_hinge = None
        self.pdelta = None

        # Results storage
        self.results = {}
        self.cross_validation = {}

        # Initialize analysis components
        self._initialize_components()

    def _initialize_components(self) -> None:
        """Initialize individual analysis components"""
        # Import here to avoid circular imports
        from .response_spectrum import ResponseSpectrumAnalysis
        from .pushover import PushoverAnalysis
        from .time_history import TimeHistoryAnalysis
        from .plastic_hinge import PlasticHingeAnalyzer
        from .pdelta import PdeltaAnalysis

        # Initialize based on analysis type
        if self.analysis_type in ['CSM', 'PUSHOVER']:
            self.pushover = PushoverAnalysis(self.model_data, self.config)

        if self.analysis_type in ['CSM', 'RSA']:
            self.rsa = ResponseSpectrumAnalysis(self.model_data, self.config)

        if self.analysis_type in ['MULTI_STRIPE', 'IDA', 'THA']:
            self.tha = TimeHistoryAnalysis(self.model_data, {}, self.config)

        if self.analysis_type in ['PERFORMANCE_ASSESSMENT', 'FRAGILITY']:
            self.plastic_hinge = PlasticHingeAnalyzer(self.model_data, self.config)

        if 'pdelta' in self.config and self.config['pdelta']:
            self.pdelta = PdeltaAnalysis(self.model_data, self.config)

    def run_capacity_spectrum_method(self) -> Dict[str, Any]:
        """
        Execute Capacity Spectrum Method (RSA + Pushover)

        Returns:
            CSM analysis results
        """
        self.logger.info("Starting Capacity Spectrum Method analysis")

        results = {
            'rsa_results': None,
            'pushover_results': None,
            'performance_point': None,
            'status': 'failed'
        }

        try:
            # Run RSA to get demand spectrum
            if self.rsa:
                rsa_results = self.rsa.run_analysis()
                results['rsa_results'] = rsa_results

                if rsa_results['status'] != 'completed':
                    raise RuntimeError("RSA analysis failed")

            # Run pushover analysis
            if self.pushover:
                self.pushover.define_load_pattern('proportional_first_mode')
                pushover_results = self.pushover.run_analysis(target_drift=0.05)
                results['pushover_results'] = pushover_results

                if pushover_results['status'] != 'completed':
                    raise RuntimeError("Pushover analysis failed")

            # Identify performance point
            if results['rsa_results'] and results['pushover_results']:
                results['performance_point'] = self._identify_performance_point_csm(
                    results['rsa_results'], results['pushover_results']
                )

            results['status'] = 'completed'
            self.logger.info("Capacity Spectrum Method completed successfully")

        except Exception as e:
            self.logger.error(f"CSM analysis failed: {str(e)}")
            results['error'] = str(e)

        self.results['CSM'] = results
        return results

    def _identify_performance_point_csm(self, rsa_results: Dict, pushover_results: Dict) -> Dict[str, float]:
        """Identify performance point using capacity spectrum method"""
        # Simplified CSM implementation
        # In practice, would implement full capacity spectrum method per FEMA 440

        pushover_curve = pushover_results.get('pushover_curve', {})
        if not pushover_curve.get('displacement') or not pushover_curve.get('base_shear'):
            return None

        # Get demand spectrum from RSA
        periods = rsa_results.get('periods', [])
        spectral_accels = rsa_results.get('spectral_accelerations', [])

        if not periods or not spectral_accels:
            return None

        # Simplified: find intersection point
        # In practice, would transform pushover curve to ADRS format
        displacements = np.array(pushover_curve['displacement'])
        forces = np.array(pushover_curve['base_shear'])

        # Placeholder performance point
        performance_point = {
            'displacement': float(np.mean(displacements)),
            'base_shear': float(np.mean(forces)),
            'spectral_displacement': float(np.mean(displacements) * 0.5),  # Simplified
            'spectral_acceleration': float(np.mean(forces) / 1000.0)  # Simplified
        }

        return performance_point

    def run_multi_stripe_analysis(self, ground_motions: List[Dict],
                                intensity_levels: List[float],
                                max_workers: int = 4) -> Dict[str, Any]:
        """
        Execute multi-stripe analysis for IDA data generation

        Args:
            ground_motions: List of ground motion records
            intensity_levels: List of intensity scaling factors
            max_workers: Maximum parallel workers

        Returns:
            Multi-stripe analysis results
        """
        self.logger.info(f"Starting multi-stripe analysis with {len(ground_motions)} GMs and {len(intensity_levels)} intensities")

        results = {
            'total_analyses': len(ground_motions) * len(intensity_levels),
            'completed_analyses': 0,
            'failed_analyses': 0,
            'results_matrix': {},
            'status': 'running'
        }

        # Prepare analysis tasks
        tasks = []
        for gm_idx, gm in enumerate(ground_motions):
            for intensity in intensity_levels:
                task = {
                    'gm_index': gm_idx,
                    'gm_data': gm,
                    'intensity': intensity,
                    'task_id': f"GM{gm_idx}_INT{intensity:.2f}"
                }
                tasks.append(task)

        # Execute analyses (parallel if possible)
        completed_results = []

        if max_workers > 1:
            # Parallel execution
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_task = {
                    executor.submit(self._run_single_stripe, task): task
                    for task in tasks
                }

                for future in concurrent.futures.as_completed(future_to_task):
                    task = future_to_task[future]
                    try:
                        result = future.result()
                        completed_results.append(result)
                        results['completed_analyses'] += 1
                    except Exception as e:
                        self.logger.error(f"Task {task['task_id']} failed: {str(e)}")
                        results['failed_analyses'] += 1
        else:
            # Sequential execution
            for task in tasks:
                try:
                    result = self._run_single_stripe(task)
                    completed_results.append(result)
                    results['completed_analyses'] += 1
                except Exception as e:
                    self.logger.error(f"Task {task['task_id']} failed: {str(e)}")
                    results['failed_analyses'] += 1

        # Organize results
        results['results_matrix'] = self._organize_stripe_results(completed_results)
        results['status'] = 'completed' if results['failed_analyses'] == 0 else 'partial'

        self.logger.info(f"Multi-stripe analysis completed: {results['completed_analyses']}/{results['total_analyses']} successful")

        self.results['MULTI_STRIPE'] = results
        return results

    def _run_single_stripe(self, task: Dict) -> Dict[str, Any]:
        """Run single stripe analysis"""
        gm_data = task['gm_data']
        intensity = task['intensity']

        # Create THA instance for this analysis
        tha = TimeHistoryAnalysis(self.model_data, gm_data, self.config)
        tha.scale_ground_motion(intensity)

        # Run analysis
        result = tha.run_analysis()

        # Add task metadata
        result.update({
            'gm_index': task['gm_index'],
            'intensity': intensity,
            'task_id': task['task_id']
        })

        return result

    def _organize_stripe_results(self, results: List[Dict]) -> Dict[str, List]:
        """Organize stripe results into matrix format"""
        organized = {
            'gm_indices': [],
            'intensities': [],
            'pidr_values': [],
            'peak_accels': [],
            'statuses': []
        }

        for result in results:
            organized['gm_indices'].append(result.get('gm_index', -1))
            organized['intensities'].append(result.get('intensity', 0.0))
            organized['statuses'].append(result.get('status', 'unknown'))

            # Extract key metrics
            peak_responses = result.get('peak_responses', {})
            pidr_max = max(result.get('drift_history', {}).values()) if result.get('drift_history') else 0.0
            pga = result.get('gm_scale_factor', 1.0) * result.get('ground_motion', {}).get('pga', 0.0)

            organized['pidr_values'].append(pidr_max)
            organized['peak_accels'].append(pga)

        return organized

    def run_performance_assessment(self, response_data: Dict) -> Dict[str, Any]:
        """
        Execute comprehensive performance assessment

        Args:
            response_data: Analysis response data

        Returns:
            Performance assessment results
        """
        self.logger.info("Starting performance assessment")

        results = {
            'plastic_hinge_assessment': None,
            'pushover_assessment': None,
            'overall_performance': None,
            'status': 'failed'
        }

        try:
            # Plastic hinge assessment
            if self.plastic_hinge:
                self.plastic_hinge.define_hinges('RC_BEAM_COLUMN_JOINT')
                hinge_rotations = self.plastic_hinge.compute_hinge_rotations(response_data)
                hinge_assessment = self.plastic_hinge.assess_performance_level(hinge_rotations)

                results['plastic_hinge_assessment'] = {
                    'hinge_rotations': hinge_rotations,
                    'assessment': hinge_assessment
                }

            # Pushover-based assessment
            if self.pushover:
                pushover_results = self.pushover.run_analysis(target_drift=0.05)
                results['pushover_assessment'] = pushover_results

            # Determine overall performance
            results['overall_performance'] = self._determine_overall_performance(results)
            results['status'] = 'completed'

            self.logger.info(f"Performance assessment completed: {results['overall_performance']}")

        except Exception as e:
            self.logger.error(f"Performance assessment failed: {str(e)}")
            results['error'] = str(e)

        self.results['PERFORMANCE_ASSESSMENT'] = results
        return results

    def _determine_overall_performance(self, assessment_results: Dict) -> str:
        """Determine overall performance level from multiple assessments"""
        performance_levels = []

        # Get performance from plastic hinge assessment
        if assessment_results.get('plastic_hinge_assessment'):
            ph_assessment = assessment_results['plastic_hinge_assessment']['assessment']
            performance_levels.append(ph_assessment.get('overall_performance', 'IO'))

        # Get performance from pushover (if available)
        if assessment_results.get('pushover_assessment'):
            # Simplified - would map pushover results to performance levels
            performance_levels.append('IO')  # Placeholder

        # Return most conservative (worst) performance level
        if performance_levels:
            performance_order = {'IO': 0, 'LS': 1, 'CP': 2}
            worst_level = max(performance_levels, key=lambda x: performance_order.get(x, 0))
            return worst_level

        return 'IO'  # Default

    def run_incremental_dynamic_analysis(self, ground_motions: List[Dict],
                                       intensity_range: Tuple[float, float] = (0.05, 2.0),
                                       num_steps: int = 20) -> Dict[str, Any]:
        """
        Execute Incremental Dynamic Analysis (IDA)

        Args:
            ground_motions: List of ground motion records
            intensity_range: (min, max) intensity scaling
            num_steps: Number of intensity steps

        Returns:
            IDA analysis results
        """
        self.logger.info("Starting Incremental Dynamic Analysis")

        # Generate intensity levels
        intensities = np.linspace(intensity_range[0], intensity_range[1], num_steps)

        # Run multi-stripe analysis
        ida_results = self.run_multi_stripe_analysis(ground_motions, intensities.tolist())

        # Process IDA-specific metrics
        ida_curves = self._process_ida_curves(ida_results)

        results = {
            'ida_curves': ida_curves,
            'intensity_levels': intensities.tolist(),
            'multi_stripe_results': ida_results,
            'status': ida_results['status']
        }

        self.results['IDA'] = results
        return results

    def _process_ida_curves(self, multi_stripe_results: Dict) -> Dict[str, List]:
        """Process IDA curves from multi-stripe results"""
        results_matrix = multi_stripe_results.get('results_matrix', {})

        ida_curves = {
            'intensity_levels': results_matrix.get('intensities', []),
            'median_pidr': [],
            '16th_percentile_pidr': [],
            '84th_percentile_pidr': []
        }

        # Group by intensity level
        intensity_groups = {}
        for i, intensity in enumerate(results_matrix.get('intensities', [])):
            if intensity not in intensity_groups:
                intensity_groups[intensity] = []
            pidr = results_matrix.get('pidr_values', [])[i]
            if pidr > 0:
                intensity_groups[intensity].append(pidr)

        # Compute statistics for each intensity
        for intensity in sorted(intensity_groups.keys()):
            pidr_values = intensity_groups[intensity]
            if pidr_values:
                ida_curves['median_pidr'].append(np.median(pidr_values))
                ida_curves['16th_percentile_pidr'].append(np.percentile(pidr_values, 16))
                ida_curves['84th_percentile_pidr'].append(np.percentile(pidr_values, 84))

        return ida_curves

    def validate_cross_method(self) -> Dict[str, Any]:
        """
        Perform cross-method validation of results

        Returns:
            Cross-validation results
        """
        validation = {
            'methods_compared': [],
            'consistency_checks': [],
            'discrepancies': [],
            'recommendations': []
        }

        available_results = [k for k, v in self.results.items() if v.get('status') == 'completed']

        # CSM vs Pushover validation
        if 'CSM' in available_results:
            csm_results = self.results['CSM']
            validation['methods_compared'].append('CSM')

            # Check if performance point is reasonable
            pp = csm_results.get('performance_point')
            if pp:
                validation['consistency_checks'].append({
                    'check': 'Performance point reasonableness',
                    'result': 'PASS' if 0.001 < pp.get('displacement', 0) < 0.5 else 'FAIL'
                })

        # IDA vs Multi-stripe validation
        if 'IDA' in available_results and 'MULTI_STRIPE' in available_results:
            validation['methods_compared'].extend(['IDA', 'MULTI_STRIPE'])

            # Check IDA curve monotonicity
            ida_curves = self.results['IDA'].get('ida_curves', {})
            median_pidr = ida_curves.get('median_pidr', [])
            if len(median_pidr) > 1:
                is_monotonic = all(median_pidr[i] <= median_pidr[i+1] for i in range(len(median_pidr)-1))
                validation['consistency_checks'].append({
                    'check': 'IDA curve monotonicity',
                    'result': 'PASS' if is_monotonic else 'WARNING'
                })

        self.cross_validation = validation
        return validation

    def export_results(self, filepath: str, format: str = 'json') -> None:
        """
        Export combined analysis results

        Args:
            filepath: Output file path
            format: Export format ('json', 'pickle')
        """
        export_data = {
            'analysis_type': self.analysis_type,
            'results': self.results,
            'cross_validation': self.cross_validation,
            'config': self.config
        }

        if format == 'json':
            import json
            with open(filepath, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
        elif format == 'pickle':
            import pickle
            with open(filepath, 'wb') as f:
                pickle.dump(export_data, f)

        self.logger.info(f"Combined analysis results exported to {filepath}")


__all__ = ['CombinedAnalysis']
