# data_compiler.py - IDA Results Data Compilation and Processing
"""
Data compilation utilities for incremental dynamic analysis results

Handles aggregation of IDA results across different framework types,
data validation, and preparation for ML training.
"""

import pandas as pd
import numpy as np
import os
from pathlib import Path
from typing import Dict, List, Optional, Union
import yaml
import json


class IDADataCompiler:
    """
    Compiles and processes IDA results from multiple analyses

    Supports data from different framework types and consolidates
    into unified format for ML training.
    """

    def __init__(self, config_path: str = 'config/analysis_config.yaml'):
        """Initialize data compiler"""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        self.paths = self.config.get('paths', {})

    def compile_framework_results(self, framework_types: List[str],
                                results_dir: str = 'data/processed') -> pd.DataFrame:
        """
        Compile IDA results for multiple framework types

        Args:
            framework_types: List of framework types to compile
            results_dir: Directory containing result files

        Returns:
            Compiled DataFrame with all results
        """
        all_results = []

        for framework in framework_types:
            result_file = os.path.join(results_dir, f'ida_results_{framework}.csv')

            if os.path.exists(result_file):
                print(f"Loading {framework} results from {result_file}")
                df = pd.read_csv(result_file)
                df['framework'] = framework
                all_results.append(df)
            else:
                print(f"Warning: {result_file} not found")

        if not all_results:
            raise FileNotFoundError("No result files found")

        # Combine all results
        combined_df = pd.concat(all_results, ignore_index=True)

        # Validate and clean data
        combined_df = self._validate_and_clean(combined_df)

        # Add derived features
        combined_df = self._add_derived_features(combined_df)

        return combined_df

    def _validate_and_clean(self, df: pd.DataFrame) -> pd.DataFrame:
        """Validate and clean compiled data"""
        # Required columns
        required_cols = [
            'building_id', 'framework', 'zone', 'gm_id', 'intensity_sa',
            'pidr', 'base_shear', 'total_height', 'n_stories'
        ]

        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")

        # Remove rows with invalid PIDR values
        df = df[(df['pidr'] > 0) & (df['pidr'] < 1.0)].copy()  # type: ignore # PIDR must be between 0 and 1

        # Handle missing values
        df = df.dropna(subset=['pidr', 'intensity_sa'])

        # Ensure consistent data types
        df['building_id'] = df['building_id'].astype(str)
        df['framework'] = df['framework'].astype(str)
        df['zone'] = df['zone'].astype(int)
        df['n_stories'] = df['n_stories'].astype(int)

        return df

    def _add_derived_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add derived features for ML training"""
        # Log-transform spectral acceleration
        df['ln_sa'] = np.log(df['intensity_sa'].clip(lower=1e-6))

        # Building period approximation (BNBC 2020)
        df['approx_period'] = 0.0466 * df['total_height']**0.9

        # Seismic zone coefficient
        zone_coeffs = {1: 0.12, 2: 0.18, 3: 0.24, 4: 0.36}
        df['zone_coeff'] = df['zone'].map(zone_coeffs)

        # Response modification factor by framework
        r_factors = {
            'nonsway': 1.5,
            'omrf': 3.0,
            'imrf': 4.0,
            'smrf': 5.0
        }
        df['r_factor'] = df['framework'].map(r_factors)

        # Normalized base shear
        df['base_shear_normalized'] = df['base_shear'] / (df['total_height'] * df['n_stories'])

        # Drift ratio categories
        df['drift_category'] = pd.cut(df['pidr'],
                                    bins=[0, 0.005, 0.015, 0.025, 1.0],
                                    labels=['IO', 'LS', 'CP', 'CO'])

        return df

    def split_by_framework(self, df: pd.DataFrame,
                          output_dir: str = 'data/processed') -> Dict[str, str]:
        """
        Split compiled data by framework and save separate files

        Returns:
            Dictionary mapping framework to file path
        """
        os.makedirs(output_dir, exist_ok=True)
        framework_files = {}

        for framework in df['framework'].unique():
            framework_df = df[df['framework'] == framework].copy()
            output_file = os.path.join(output_dir, f'training_data_{framework}.csv')
            framework_df.to_csv(output_file, index=False)
            framework_files[framework] = output_file

        return framework_files

    def generate_data_summary(self, df: pd.DataFrame,
                            output_file: str = 'data/metadata/data_summary.json'):
        """Generate summary statistics for the compiled dataset"""
        summary = {
            'total_records': len(df),
            'frameworks': df['framework'].value_counts().to_dict(),
            'buildings': df['building_id'].nunique(),
            'ground_motions': df['gm_id'].nunique(),
            'intensity_levels': df['intensity_sa'].nunique(),
            'zones': sorted(df['zone'].unique()),
            'pidr_stats': {
                'mean': df['pidr'].mean(),
                'std': df['pidr'].std(),
                'min': df['pidr'].min(),
                'max': df['pidr'].max(),
                'median': df['pidr'].median()
            },
            'buildings_per_framework': df.groupby('framework')['building_id'].nunique().to_dict(),
            'records_per_zone': df.groupby('zone').size().to_dict()
        }

        # Save summary
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w') as f:
            json.dump(summary, f, indent=2)

        return summary

    def validate_ml_readiness(self, df: pd.DataFrame) -> Dict:
        """Validate that data is ready for ML training"""
        validation = {
            'status': 'OK',
            'issues': [],
            'recommendations': []
        }

        # Check sample size
        min_samples = 1000
        if len(df) < min_samples:
            validation['issues'].append(f"Insufficient samples: {len(df)} < {min_samples}")
            validation['status'] = 'WARNING'

        # Check feature completeness
        required_features = ['ln_sa', 'n_stories', 'total_height', 'zone_coeff', 'r_factor']
        missing_features = [f for f in required_features if f not in df.columns]
        if missing_features:
            validation['issues'].append(f"Missing features: {missing_features}")
            validation['status'] = 'ERROR'

        # Check target variable
        if 'pidr' not in df.columns:
            validation['issues'].append("Missing target variable: pidr")
            validation['status'] = 'ERROR'

        # Check for class imbalance (if categorical)
        if 'drift_category' in df.columns:
            category_counts = df['drift_category'].value_counts()
            min_class_samples = category_counts.min()
            if min_class_samples < 100:
                validation['recommendations'].append(
                    f"Some drift categories have few samples: min = {min_class_samples}")

        # Check for outliers
        pidr_q75 = df['pidr'].quantile(0.75)
        pidr_q25 = df['pidr'].quantile(0.25)
        iqr = pidr_q75 - pidr_q25
        outliers = df[df['pidr'] > pidr_q75 + 3*iqr]
        if len(outliers) > 0:
            validation['recommendations'].append(
                f"Found {len(outliers)} potential PIDR outliers")

        return validation


class DataQualityChecker:
    """Quality assurance for IDA datasets"""

    @staticmethod
    def check_ida_curves(df: pd.DataFrame) -> Dict:
        """Check IDA curve quality"""
        issues = []

        # Check for monotonicity (PIDR should generally increase with intensity)
        for building in df['building_id'].unique():
            building_data = df[df['building_id'] == building].sort_values('intensity_sa')
            pidr_values = building_data['pidr'].values

            # Simple monotonicity check
            non_monotonic = 0
            for i in range(1, len(pidr_values)):
                if pidr_values[i] < pidr_values[i-1] * 0.8:  # Allow some noise
                    non_monotonic += 1

            if non_monotonic > len(pidr_values) * 0.1:  # More than 10% non-monotonic
                issues.append(f"Building {building}: {non_monotonic} non-monotonic points")

        return {
            'total_buildings': df['building_id'].nunique(),
            'issues_found': len(issues),
            'issues': issues[:10]  # Limit to first 10 issues
        }

    @staticmethod
    def check_ground_motion_coverage(df: pd.DataFrame) -> Dict:
        """Check ground motion record coverage"""
        gm_counts = df.groupby(['building_id', 'gm_id']).size()

        coverage_stats = {
            'total_gm_records': df['gm_id'].nunique(),
            'buildings_per_gm': gm_counts.groupby('gm_id').size().mean(),
            'gm_per_building': gm_counts.groupby('building_id').size().mean(),
            'min_gm_per_building': gm_counts.groupby('building_id').size().min(),
            'max_gm_per_building': gm_counts.groupby('building_id').size().max()
        }

        return coverage_stats