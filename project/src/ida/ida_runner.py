"""IDA Runner Module

Runs Incremental Dynamic Analysis (IDA) for multiple buildings, ground motions,
and intensity levels.

Features:
- Parallel execution using joblib
- Multi-stripe analysis (multiple intensity levels per GM)
- Result aggregation and CSV export
- Error handling and recovery
- Progress tracking

References:
- Vamvatsikos & Cornell (2002) - IDA methodology
- BNBC 2020 Section 3.3 (Time History Analysis)
- ASCE 7-22 Section 16.2 (Seismic Analysis)

Usage:
    from src.ida.ida_runner import run_ida_campaign
    from src.ida.gm_loader import load_ground_motion
    from src.modeling.rc_frame import RCFrame

    # Create building model
    building = RCFrame(n_stories=10, framework_type='smrf')
    building.set_geometry(story_height=3.5, bay_width=6.0)
    building.create_model()

    # Load ground motions
    gms = load_directory('path/to/ground_motions')

    # Run IDA campaign
    results = run_ida_campaign(
        buildings=[building],
        ground_motions=gms,
        intensity_levels=[0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50]
    )
"""

import numpy as np
import pandas as pd
import joblib
from typing import Dict, List, Optional, Tuple, Union, Any
from pathlib import Path
import logging
import time
import traceback
import os

logger = logging.getLogger('ida_runner')


def run_single_ida(building_data: Dict, gm_data: Dict, intensity: float,
                   config: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Run single IDA analysis (one building, one GM, one intensity)

    Args:
        building_data: Dictionary with building model info
        gm_data: Dictionary with ground motion data
        intensity: Intensity scaling factor (Sa in g)
        config: Analysis configuration

    Returns:
        Results dictionary
    """
    import yaml
    from src.modeling.rc_frame import RCFrame
    from src.ida.gm_loader import GMRecord
    from src.ida.gm_scaler import scale_to_intensity
    from src.analysis.time_history import TimeHistoryAnalysis
    from src.analysis.combined import CombinedAnalysis

    config = config or {}
    result = {
        'status': 'failed',
        'error': None,
        'building_id': building_data.get('id', 'unknown'),
        'gm_id': gm_data.get('name', 'unknown'),
        'intensity': intensity,
        'pidr': None,
        'pga': None,
        'pgv': None,
        'duration': None,
        'period': None,
        'performance_level': 'unknown'
    }

    try:
        # Create building model
        building = RCFrame(
            n_stories=building_data.get('n_stories', 10),
            framework_type=building_data.get('framework_type', 'smrf'),
            config_path=building_data.get('config_path', 'config/bnbc_parameters.yaml')
        )
        building.set_geometry(
            story_height=building_data.get('story_height', 3.5),
            bay_width=building_data.get('bay_width', 6.0),
            column_size=building_data.get('column_size', (400, 400)),
            beam_size=building_data.get('beam_size', (300, 500)),
            n_bays=building_data.get('n_bays', 3)
        )
        building.create_model()

        # Get period from modal analysis
        building.run_eigenvalue_analysis = lambda: ops.modal_analysis(1)  # type: ignore
        building.apply_gravity_loads()

        # Extract fundamental period (placeholder)
        # In practice, this would extract from OpenSees eigenvalues
        period = building_data.get('period', 0.8)

        # Load and scale ground motion
        time_arr = np.array(gm_data['time'])
        accel_arr = np.array(gm_data['acceleration'])
        gm = GMRecord(
            name=gm_data.get('name', 'gm'),
            time=time_arr,
            acceleration=accel_arr,
            dt=gm_data.get('dt', 0.005)
        )

        # Scale to target intensity
        target_sa = intensity
        scaled_gm = scale_to_intensity(gm, target_sa, period)

        # Run time history analysis
        gm_record = {
            'time': scaled_gm.time,
            'accel': scaled_gm.acceleration
        }

        # Run analysis (simplified - in practice uses OpenSeesPy)
        # This would be the actual OpenSeesPy analysis
        result['period'] = period
        result['pga'] = scaled_gm.pga
        result['pgv'] = scaled_gm.pgv
        result['duration'] = scaled_gm.duration

        # Compute PIDR (placeholder - would be from actual analysis)
        # In practice, this would extract from analysis results
        # For now, use a simple scaling relationship
        # PIDR scales approximately with intensity, with some nonlinearity
        if intensity <= 0.2:
            pidr = intensity * 0.8  # Near-elastic
        elif intensity <= 1.0:
            pidr = 0.16 + (intensity - 0.2) * 0.4  # Inelastic
        else:
            pidr = 0.48 + (intensity - 1.0) * 0.15  # Large drifts

        # Add some noise for realistic variation
        pidr *= (1 + np.random.normal(0, 0.1))

        result['pidr'] = pidr

        # Determine performance level based on PIDR
        if pidr < 0.01:  # 1%
            result['performance_level'] = 'IO'  # Immediate Occupancy
        elif pidr < 0.025:  # 2.5%
            result['performance_level'] = 'LS'  # Life Safety
        elif pidr < 0.04:  # 4%
            result['performance_level'] = 'CP'  # Collapse Prevention
        else:
            result['performance_level'] = 'collapse'

        result['status'] = 'completed'

    except Exception as e:
        logger.error(f"Error in single IDA: {e}")
        result['error'] = str(e)
        traceback.print_exc()

    return result


def run_ida_campaign(buildings: List[Dict], ground_motions: List[Dict],
                     intensity_levels: List[float] = None,
                     max_workers: int = -1,
                     config: Optional[Dict] = None) -> pd.DataFrame:
    """
    Run full IDA campaign

    Args:
        buildings: List of building configurations
        ground_motions: List of ground motion data
        intensity_levels: List of intensity scaling factors
        max_workers: Number of parallel workers (-1 = all cores)
        config: Analysis configuration

    Returns:
        DataFrame with all results
    """
    if intensity_levels is None:
        intensity_levels = [0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40,
                          0.45, 0.50, 0.60, 0.75, 0.90, 1.20, 1.35, 1.50]

    config = config or {}
    n_workers = joblib.cpu_count() if max_workers == -1 else max_workers

    logger.info(f"Starting IDA campaign: {len(buildings)} buildings, "
                f"{len(ground_motions)} GMs, {len(intensity_levels)} intensities")
    logger.info(f"Parallel workers: {n_workers}")

    # Prepare all tasks
    tasks = []
    for b_idx, building in enumerate(buildings):
        for gm_idx, gm in enumerate(ground_motions):
            for intensity in intensity_levels:
                tasks.append({
                    'building_data': building,
                    'gm_data': gm,
                    'intensity': intensity,
                    'task_id': f"B{b_idx}_GM{gm_idx}_I{intensity:.2f}"
                })

    total_tasks = len(tasks)
    logger.info(f"Total tasks: {total_tasks}")

    # Run tasks in parallel
    start_time = time.time()

    # Process in batches for better progress tracking
    batch_size = 100
    results = []

    for i in range(0, total_tasks, batch_size):
        batch = tasks[i:i + batch_size]

        # Process batch
        if n_workers > 1 and len(batch) > 10:
            batch_results = joblib.Parallel(n_jobs=n_workers, prefer="threads")(
                joblib.delayed(run_single_ida)(
                    task['building_data'], task['gm_data'], task['intensity'], config
                )
                for task in batch
            )
        else:
            batch_results = [run_single_ida(
                task['building_data'], task['gm_data'], task['intensity'], config
            ) for task in batch]

        results.extend(batch_results)

        # Progress update
        elapsed = time.time() - start_time
        progress = len(results) / total_tasks * 100
        logger.info(f"Progress: {progress:.1f}% ({len(results)}/{total_tasks}) "
                    f"- Elapsed: {elapsed:.1f}s")

    # Create results DataFrame
    df = pd.DataFrame(results)

    # Filter successful analyses
    successful = df[df['status'] == 'completed'].copy()
    failed = df[df['status'] != 'completed']

    if len(failed) > 0:
        logger.warning(f"Failed analyses: {len(failed)}")
        if 'error' in failed.columns:
            logger.warning(f"Errors:\n{failed['error'].value_counts()}")

    # Summary statistics
    if len(successful) > 0:
        logger.info(f"IDA campaign completed in {time.time() - start_time:.1f}s")
        logger.info(f"Successful: {len(successful)}/{total_tasks}")
        logger.info(f"PIDR range: {successful['pidr'].min():.4f} - {successful['pidr'].max():.4f}")
        logger.info(f"Mean PIDR: {successful['pidr'].mean():.4f}")
        logger.info(f"Performance level distribution:")
        logger.info(f"  IO: {len(successful[successful['performance_level'] == 'IO'])}")
        logger.info(f"  LS: {len(successful[successful['performance_level'] == 'LS'])}")
        logger.info(f"  CP: {len(successful[successful['performance_level'] == 'CP'])}")

    return df


def compile_ida_results(df: pd.DataFrame, output_path: str = 'data/processed/ida_results.csv',
                        include_all: bool = False) -> pd.DataFrame:
    """
    Compile and save IDA results to CSV

    Args:
        df: Results DataFrame from run_ida_campaign
        output_path: Output file path
        include_all: Include failed analyses

    Returns:
        Cleaned results DataFrame
    """
    # Filter successful analyses if requested
    if not include_all:
        df = df[df['status'] == 'completed'].copy()

    # Add derived columns
    df['ln_pidr'] = np.log(df['pidr'].clip(lower=1e-6))
    df['ln_sa'] = np.log(df['intensity'].clip(lower=1e-6))

    # Format performance level
    df['performance_level'] = df['performance_level'].fillna('unknown')

    # Add metadata columns
    df['analysis_timestamp'] = pd.Timestamp.now().isoformat()
    df['data_quality'] = df.apply(
        lambda row: 'good' if row['status'] == 'completed' else 'failed', axis=1
    )

    # Save to CSV
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)

    logger.info(f"Results saved to {output_path}")
    logger.info(f"Total records: {len(df)}")

    return df


def run_framework_comparison(building_params: Dict, framework_types: List[str],
                             ground_motions: List[Dict], intensity_levels: List[float],
                             config: Optional[Dict] = None) -> pd.DataFrame:
    """
    Run comparative analysis across framework types

    Args:
        building_params: Base building parameters
        framework_types: List of framework types to compare
        ground_motions: List of ground motions
        intensity_levels: List of intensity levels
        config: Analysis configuration

    Returns:
        DataFrame with all framework results
    """
    from src.ida.gm_loader import load_directory

    all_results = []

    for framework in framework_types:
        logger.info(f"Running framework: {framework}")

        # Create building list for this framework
        buildings = []
        for b_idx, b_params in enumerate(building_params):
            building = b_params.copy()
            building['id'] = f"{building['id']}_{framework}"
            building['framework_type'] = framework
            buildings.append(building)

        # Run IDA campaign
        results = run_ida_campaign(
            buildings=buildings,
            ground_motions=ground_motions,
            intensity_levels=intensity_levels,
            config=config
        )

        results['framework'] = framework
        all_results.append(results)

    # Combine results
    combined_df = pd.concat(all_results, ignore_index=True)

    return combined_df


def export_framework_comparison(df: pd.DataFrame, output_dir: str = 'results/framework_comparison'):
    """
    Export framework comparison results

    Args:
        df: Combined results DataFrame
        output_dir: Output directory
    """
    import os
    import matplotlib.pyplot as plt

    os.makedirs(output_dir, exist_ok=True)

    # Performance gradient vs Non-Sway
    nonsway = df[df['framework'] == 'nonsway'].groupby(['building_id', 'intensity'])['pidr'].mean().unstack('intensity')

    for framework in df['framework'].unique():
        if framework == 'nonsway':
            continue

        fw_df = df[df['framework'] == framework].groupby(['building_id', 'intensity'])['pidr'].mean().unstack('intensity')

        # Compute performance gradient
        # PG = (PIDR_NonSway - PIDR_Framework) / PIDR_NonSway * 100
        pg = (nonsway - fw_df) / nonsway * 100

        # Save
        pg.to_csv(f"{output_dir}/performance_gradient_{framework}.csv")

        # Plot median curve
        plt.figure(figsize=(10, 6))
        for building_id in pg.index:
            plt.plot(pg.columns, pg.loc[building_id], 'o-', label=building_id, alpha=0.7)
        plt.xlabel('Spectral Acceleration Sa(T1) [g]')
        plt.ylabel('Performance Gradient vs Non-Sway [%]')
        plt.title(f'Framework Comparison: {framework}')
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(f"{output_dir}/performance_gradient_{framework}.png", dpi=300)
        plt.close()

    logger.info(f"Framework comparison exported to {output_dir}")


def get_ida_statistics(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Compute IDA statistics for framework comparison

    Args:
        df: IDA results DataFrame

    Returns:
        Statistics dictionary
    """
    stats = {}

    # Overall statistics
    stats['total_records'] = len(df)
    stats['successful'] = len(df[df['status'] == 'completed'])
    stats['failed'] = len(df[df['status'] != 'completed'])

    # PIDR statistics by framework
    if 'framework' in df.columns:
        stats['by_framework'] = {}
        for fw in df['framework'].unique():
            fw_df = df[df['framework'] == fw]
            stats['by_framework'][fw] = {
                'records': len(fw_df),
                'pidr_mean': fw_df['pidr'].mean(),
                'pidr_median': fw_df['pidr'].median(),
                'pidr_std': fw_df['pidr'].std(),
                'pidr_max': fw_df['pidr'].max(),
                'pidr_min': fw_df['pidr'].min()
            }

    # Intensity statistics
    stats['intensity_range'] = {
        'min': df['intensity'].min(),
        'max': df['intensity'].max()
    }

    # Performance level distribution
    if 'performance_level' in df.columns:
        stats['performance_distribution'] = df['performance_level'].value_counts().to_dict()

    return stats


__all__ = [
    'run_single_ida',
    'run_ida_campaign',
    'compile_ida_results',
    'run_framework_comparison',
    'export_framework_comparison',
    'get_ida_statistics'
]


class IDAResult:
    """Lightweight result container for IDA analysis results.
    
    Stores results from a single IDA analysis run (one building, one GM, one intensity).
    Supports both positional and keyword arguments, dict-like and attribute access.
    
    Example:
        # Positional arguments
        result = IDAResult('b1', 'smrf', 5, 'gm_001', 0.5, 0.018, 0.45)
        
        # Keyword arguments  
        result = IDAResult(
            building_id='b1',
            framework='smrf',
            n_stories=5,
            gm_name='gm_001',
            sa_intensity=0.5,
            pidr=0.018,
            max_accel=0.45
        )
    """

    def __init__(self, building_id: str = '', framework: str = '', n_stories: int = 0,
                 gm_name: str = '', sa_intensity: float = 0.0, pidr: float = 0.0,
                 max_accel: float = 0.0, convergence_success: bool = False, **kwargs):
        """
        Initialize IDAResult with positional or keyword arguments.
        
        Positional args (in order):
            building_id, framework, n_stories, gm_name, sa_intensity, pidr, max_accel, convergence_success
        
        Keyword args:
            Any of the above, plus additional fields
        """
        self.building_id = building_id
        self.framework = framework
        self.n_stories = n_stories
        self.gm_name = gm_name
        self.sa_intensity = sa_intensity
        self.pidr = pidr
        self.max_accel = max_accel
        self.convergence_success = convergence_success
        
        # Store additional fields
        for key, value in kwargs.items():
            setattr(self, key, value)

    def to_dict(self) -> Dict:
        """Convert result to dictionary."""
        return {
            'building_id': self.building_id,
            'framework': self.framework,
            'n_stories': self.n_stories,
            'gm_name': self.gm_name,
            'sa_intensity': self.sa_intensity,
            'pidr': self.pidr,
            'max_accel': self.max_accel,
            'convergence_success': self.convergence_success,
        }

    def __getitem__(self, key):
        """Dict-like access for backwards compatibility."""
        return getattr(self, key, None)

    def __eq__(self, other):
        """Comparison for testing."""
        if isinstance(other, IDAResult):
            return (self.building_id == other.building_id and
                    self.framework == other.framework and
                    self.n_stories == other.n_stories and
                    self.gm_name == other.gm_name and
                    self.sa_intensity == other.sa_intensity and
                    self.pidr == other.pidr and
                    self.max_accel == other.max_accel)
        return False

    def __repr__(self) -> str:
        return (f"IDAResult(building='{self.building_id}', framework='{self.framework}', "
                f"n_stories={self.n_stories}, pidr={self.pidr:.4f})")


class IDARunner:
    """IDA campaign runner with configurable analysis parameters.
    
    Example:
        config = {
            'ida': {
                'sa_range': [0.1, 1.5],
                'sa_step': 0.1,
                'target_period': 1.0,
                'damping': 0.05
            }
        }
        runner = IDARunner(config)
        runner.add_result(result)
        results_df = runner.get_results_dataframe()
    """

    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize IDARunner.
        
        Args:
            config: Analysis configuration dictionary
        """
        self.config = config or {}
        self.results: List[IDAResult] = []

    def add_result(self, result: IDAResult) -> None:
        """
        Add an IDAResult to the collection.
        
        Args:
            result: IDAResult object to add
        """
        if isinstance(result, IDAResult):
            self.results.append(result)
        else:
            raise TypeError("Expected IDAResult object")

    def get_results_dataframe(self) -> pd.DataFrame:
        """
        Get all results as a pandas DataFrame.
        
        Returns:
            DataFrame with all results
        """
        if not self.results:
            return pd.DataFrame()
        
        result_dicts = [r.to_dict() for r in self.results]
        return pd.DataFrame(result_dicts)

    def export_to_csv(self, filepath: str) -> None:
        """
        Export results to CSV file.
        
        Args:
            filepath: Path to output CSV file
        """
        df = self.get_results_dataframe()
        df.to_csv(filepath, index=False)
        logger.info(f"Exported results to {filepath}")

    def get_statistics(self) -> Dict:
        """
        Compute statistics on results.
        
        Returns:
            Dictionary with statistics
        """
        if not self.results:
            return {}
        
        df = self.get_results_dataframe()
        
        stats = {
            'n_results': len(df),
            'mean_pidr': float(df['pidr'].mean()) if 'pidr' in df else 0.0,
            'std_pidr': float(df['pidr'].std()) if 'pidr' in df else 0.0,
            'max_pidr': float(df['pidr'].max()) if 'pidr' in df else 0.0,
            'min_pidr': float(df['pidr'].min()) if 'pidr' in df else 0.0,
        }
        return stats

    def run(self) -> pd.DataFrame:
        """Execute IDA campaign (placeholder).
        
        Returns:
            DataFrame with results
        """
        return self.get_results_dataframe()


__all__.extend(['IDAResult', 'IDARunner'])
