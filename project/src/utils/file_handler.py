# file_handler.py - File I/O utilities for OpenSeesPy models and results
"""
File handling utilities for OpenSeesPy model files, results, and data persistence

Supports saving/loading OpenSeesPy models, managing result files,
and handling large datasets efficiently.
"""

import os
import json
import pickle
import h5py
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
import yaml


class OpenSeesModelHandler:
    """
    Handles saving and loading OpenSeesPy model files

    Supports JSON format for model persistence and reconstruction.
    """

    @staticmethod
    def save_model(model_data: Dict, filepath: str) -> None:
        """
        Save OpenSeesPy model data to JSON file

        Args:
            model_data: Dictionary containing model information
            filepath: Path to save the model file
        """
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        # Convert numpy arrays to lists for JSON serialization
        serializable_data = OpenSeesModelHandler._make_serializable(model_data)

        with open(filepath, 'w') as f:
            json.dump(serializable_data, f, indent=2)

        print(f"Model saved to {filepath}")

    @staticmethod
    def load_model(filepath: str) -> Dict:
        """
        Load OpenSeesPy model data from JSON file

        Args:
            filepath: Path to the model file

        Returns:
            Dictionary containing model information
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Model file not found: {filepath}")

        with open(filepath, 'r') as f:
            model_data = json.load(f)

        # Convert lists back to numpy arrays where appropriate
        model_data = OpenSeesModelHandler._restore_arrays(model_data)

        print(f"Model loaded from {filepath}")
        return model_data

    @staticmethod
    def _make_serializable(obj: Any) -> Any:
        """Convert numpy arrays to lists for JSON serialization"""
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, dict):
            return {key: OpenSeesModelHandler._make_serializable(value)
                   for key, value in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [OpenSeesModelHandler._make_serializable(item) for item in obj]
        else:
            return obj

    @staticmethod
    def _restore_arrays(obj: Any) -> Any:
        """Convert lists back to numpy arrays where appropriate"""
        if isinstance(obj, dict):
            # Check if this looks like an array (has 'shape' and 'data' keys)
            if 'shape' in obj and 'data' in obj:
                return np.array(obj['data']).reshape(obj['shape'])
            else:
                return {key: OpenSeesModelHandler._restore_arrays(value)
                       for key, value in obj.items()}
        elif isinstance(obj, list):
            # Try to convert to numpy array if all elements are numbers
            try:
                arr = np.array(obj)
                if arr.dtype.kind in 'biufc':  # bool, int, uint, float, complex
                    return arr
                else:
                    return [OpenSeesModelHandler._restore_arrays(item) for item in obj]
            except (ValueError, TypeError):
                return [OpenSeesModelHandler._restore_arrays(item) for item in obj]
        else:
            return obj


class ResultsHandler:
    """
    Handles saving and loading analysis results

    Supports CSV, HDF5, and pickle formats for different use cases.
    """

    @staticmethod
    def save_ida_results(results_df: pd.DataFrame, filepath: str,
                        format: str = 'csv') -> None:
        """
        Save IDA results to file

        Args:
            results_df: DataFrame containing IDA results
            filepath: Path to save results
            format: File format ('csv', 'hdf5', 'pickle')
        """
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        if format == 'csv':
            results_df.to_csv(filepath, index=False)
        elif format == 'hdf5':
            with h5py.File(filepath, 'w') as f:
                # Convert DataFrame to HDF5
                for column in results_df.columns:
                    data = results_df[column].values
                    if data.dtype == 'object':
                        # Convert strings to fixed-length byte strings
                        max_len = max(len(str(x)) for x in data) if len(data) > 0 else 1
                        dt = h5py.special_dtype(vlen=str)
                        f.create_dataset(column, data=data.astype(str), dtype=dt)
                    else:
                        f.create_dataset(column, data=data)
        elif format == 'pickle':
            with open(filepath, 'wb') as f:
                pickle.dump(results_df, f)
        else:
            raise ValueError(f"Unsupported format: {format}")

        print(f"Results saved to {filepath} ({format} format)")

    @staticmethod
    def load_ida_results(filepath: str, format: Optional[str] = None) -> pd.DataFrame:
        """
        Load IDA results from file

        Args:
            filepath: Path to results file
            format: File format (auto-detected if None)

        Returns:
            DataFrame containing IDA results
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Results file not found: {filepath}")

        # Auto-detect format from extension
        if format is None:
            ext = Path(filepath).suffix.lower()
            if ext == '.csv':
                format = 'csv'
            elif ext in ['.h5', '.hdf5']:
                format = 'hdf5'
            elif ext == '.pkl':
                format = 'pickle'
            else:
                raise ValueError(f"Cannot auto-detect format for extension: {ext}")

        if format == 'csv':
            return pd.read_csv(filepath)
        elif format == 'hdf5':
            with h5py.File(filepath, 'r') as f:  # type: ignore
                data = {}
                for key in f.keys():
                    data[key] = f[key][:]  # type: ignore
                return pd.DataFrame(data)
        elif format == 'pickle':
            with open(filepath, 'rb') as f:
                return pickle.load(f)
        else:
            raise ValueError(f"Unsupported format: {format}")

    @staticmethod
    def save_recorder_data(recorder_data: Dict[str, np.ndarray],
                          filepath: str) -> None:
        """
        Save OpenSeesPy recorder data to HDF5 file

        Args:
            recorder_data: Dictionary of recorder arrays
            filepath: Path to save data
        """
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        with h5py.File(filepath, 'w') as f:
            for name, data in recorder_data.items():
                f.create_dataset(name, data=data, compression='gzip')

        print(f"Recorder data saved to {filepath}")

    @staticmethod
    def load_recorder_data(filepath: str) -> Dict[str, np.ndarray]:
        """
        Load OpenSeesPy recorder data from HDF5 file

        Args:
            filepath: Path to data file

        Returns:
            Dictionary of recorder arrays
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Recorder data file not found: {filepath}")

        recorder_data = {}
        with h5py.File(filepath, 'r') as f:  # type: ignore
            for name in f.keys():
                recorder_data[name] = f[name][:]  # type: ignore

        return recorder_data


class GroundMotionHandler:
    """
    Handles ground motion record files

    Supports various formats (PEER, ESM, etc.) and metadata management.
    """

    @staticmethod
    def load_ground_motion(filepath: str, format: str = 'peer',
                          dt: Optional[float] = None) -> Dict[str, np.ndarray]:
        """
        Load ground motion record from file

        Args:
            filepath: Path to ground motion file
            format: Format of the file ('peer', 'esm', 'csv')
            dt: Time step (if not in file)

        Returns:
            Dictionary with 'time', 'accel', and metadata
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Ground motion file not found: {filepath}")

        if format.lower() == 'peer':
            return GroundMotionHandler._load_peer_format(filepath)
        elif format.lower() == 'esm':
            return GroundMotionHandler._load_esm_format(filepath)
        elif format.lower() == 'csv':
            return GroundMotionHandler._load_csv_format(filepath, dt)
        else:
            raise ValueError(f"Unsupported format: {format}")

    @staticmethod
    def _load_peer_format(filepath: str) -> Dict[str, Any]:
        """Load PEER format ground motion file"""
        with open(filepath, 'r') as f:
            lines = f.readlines()

        # Parse header
        npts = int(lines[3].split()[1])
        dt = float(lines[4].split()[1])

        # Parse acceleration data
        accel_data = []
        for line in lines[5:]:
            if line.strip():
                accel_data.extend([float(x) for x in line.split()])

        accel = np.array(accel_data[:npts])
        time = np.arange(0, len(accel) * dt, dt)

        return {
            'time': time,
            'accel': accel,
            'dt': dt,
            'npts': npts,
            'format': 'peer'
        }

    @staticmethod
    def _load_esm_format(filepath: str) -> Dict[str, Any]:
        """Load ESM format ground motion file"""
        # ESM format parsing (simplified)
        data = np.loadtxt(filepath)
        time = data[:, 0]
        accel = data[:, 1]

        return {
            'time': time,
            'accel': accel,
            'dt': time[1] - time[0] if len(time) > 1 else None,
            'npts': len(accel),
            'format': 'esm'
        }

    @staticmethod
    def _load_csv_format(filepath: str, dt: Optional[float] = None) -> Dict[str, Any]:
        """Load CSV format ground motion file"""
        data = np.loadtxt(filepath, delimiter=',')
        if data.shape[1] == 1:
            # Only acceleration data
            accel = data.flatten()
            time = np.arange(0, len(accel) * (dt or 0.01), dt or 0.01)
        else:
            # Time and acceleration
            time = data[:, 0]
            accel = data[:, 1]

        return {
            'time': time,
            'accel': accel,
            'dt': time[1] - time[0] if len(time) > 1 else dt,
            'npts': len(accel),
            'format': 'csv'
        }

    @staticmethod
    def save_ground_motion(gm_data: Dict[str, np.ndarray], filepath: str,
                          format: str = 'csv') -> None:
        """
        Save ground motion data to file

        Args:
            gm_data: Ground motion data dictionary
            filepath: Path to save file
            format: Output format ('csv', 'peer')
        """
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        if format.lower() == 'csv':
            data = np.column_stack([gm_data['time'], gm_data['accel']])
            np.savetxt(filepath, data, delimiter=',', header='time,accel', comments='')
        elif format.lower() == 'peer':
            with open(filepath, 'w') as f:
                f.write("PEER Ground Motion Record\\n")
                f.write("Format: Time and Acceleration\\n")
                f.write(f"NPTS= {gm_data['npts']}\\n")
                f.write(f"DT= {gm_data['dt']}\\n")
                # Write acceleration data in chunks
                accel = gm_data['accel']
                for i in range(0, len(accel), 5):
                    chunk = accel[i:i+5]
                    f.write(' '.join(f'{x:.6f}' for x in chunk) + '\\n')
        else:
            raise ValueError(f"Unsupported format: {format}")

        print(f"Ground motion saved to {filepath} ({format} format)")


class ConfigHandler:
    """
    Handles configuration file operations

    Supports YAML and JSON configuration files.
    """

    @staticmethod
    def load_config(filepath: str) -> Dict:
        """
        Load configuration from YAML or JSON file

        Args:
            filepath: Path to config file

        Returns:
            Configuration dictionary
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Config file not found: {filepath}")

        ext = Path(filepath).suffix.lower()
        with open(filepath, 'r') as f:
            if ext in ['.yaml', '.yml']:
                return yaml.safe_load(f)
            elif ext == '.json':
                return json.load(f)
            else:
                raise ValueError(f"Unsupported config format: {ext}")

    @staticmethod
    def save_config(config: Dict, filepath: str) -> None:
        """
        Save configuration to file

        Args:
            config: Configuration dictionary
            filepath: Path to save config file
        """
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        ext = Path(filepath).suffix.lower()
        with open(filepath, 'w') as f:
            if ext in ['.yaml', '.yml']:
                yaml.dump(config, f, default_flow_style=False, indent=2)
            elif ext == '.json':
                json.dump(config, f, indent=2)
            else:
                raise ValueError(f"Unsupported config format: {ext}")

        print(f"Config saved to {filepath}")


class PathManager:
    """
    Manages project paths and directory structure

    Ensures consistent path handling across the project.
    """

    def __init__(self, project_root: Optional[str] = None):
        """Initialize path manager"""
        if project_root is None:
            # Assume we're in project/ directory
            self.project_root = Path(__file__).parent.parent.parent
        else:
            self.project_root = Path(project_root)

        self.paths = {
            'project': self.project_root,
            'src': self.project_root / 'src',
            'config': self.project_root / 'config',
            'data': {
                'raw': self.project_root / 'data' / 'raw',
                'processed': self.project_root / 'data' / 'processed',
                'metadata': self.project_root / 'data' / 'metadata'
            },
            'models': {
                'openseespy': self.project_root / 'models' / 'openseespy',
                'ml': self.project_root / 'models' / 'ml_models',
                'checkpoints': self.project_root / 'models' / 'checkpoints'
            },
            'results': {
                'figures': self.project_root / 'results' / 'figures',
                'reports': self.project_root / 'results' / 'reports',
                'tables': self.project_root / 'results' / 'tables'
            },
            'notebooks': self.project_root / 'notebooks',
            'tests': self.project_root / 'tests'
        }

    def get_path(self, *keys: str) -> Path:
        """
        Get path by key sequence

        Args:
            *keys: Path keys to navigate

        Returns:
            Path object
        """
        current: Union[Dict, Path, str] = self.paths
        for key in keys:
            if isinstance(current, dict):
                current = current[key]
            else:
                raise KeyError(f"Cannot navigate to {key}")

        if isinstance(current, (str, Path)):
            return Path(current)
        raise TypeError(f"Cannot convert {type(current)} to Path")

    def ensure_directories(self) -> None:
        """Create all necessary directories"""
        dirs_to_create = [
            self.paths['data']['raw'],
            self.paths['data']['processed'],
            self.paths['data']['metadata'],
            self.paths['models']['openseespy'],
            self.paths['models']['ml'],
            self.paths['models']['checkpoints'],
            self.paths['results']['figures'],
            self.paths['results']['reports'],
            self.paths['results']['tables']
        ]

        for dir_path in dirs_to_create:
            dir_path.mkdir(parents=True, exist_ok=True)

        print("All project directories ensured")