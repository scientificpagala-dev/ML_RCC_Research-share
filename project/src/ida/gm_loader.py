"""Ground Motion Loader Module

Loads ground motion records from PEER NGA West2 database format and other formats.

Features:
- Load PEER NGA West2 ASCII format
- Extract time history and acceleration data
- Compute PGA, PGV, and other intensity measures
- Validate ground motion format
- Support for synthetic ground motion generation

References:
- PEER NGA West2 Database: https://ngawest2.berkeley.edu
- BNBC 2020 Section 3.3 (Ground Motion Selection)
- ASCE 7-22 Section 16.2 (Seismic Analysis)

Usage:
    from src.ida.gm_loader import load_ground_motion, GMRecord

    # Load from file
    gm = load_ground_motion('records/earthquake_001.txt')

    # Load with custom scaling
    gm = load_ground_motion('records/earthquake_002.txt', scale_factor=1.5)

    # Access data
    time = gm.time
    accel = gm.acceleration
    pga = gm.pga  # Peak ground acceleration (g)
    pgv = gm.pgv  # Peak ground velocity (cm/s)
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Union
from pathlib import Path
import logging
import os

logger = logging.getLogger('gm_loader')


class GMRecord:
    """
    Ground Motion Record container

    Stores ground motion time history and computed intensity measures.
    """

    def __init__(self, name: str, time: np.ndarray, acceleration: np.ndarray,
                 dt: Optional[float] = None, scale_factor: float = 1.0):
        """
        Initialize ground motion record

        Args:
            name: Record identifier
            time: Time array [seconds]
            acceleration: Acceleration array [g]
            dt: Time step [seconds] (optional, computed from time array)
            scale_factor: Scaling factor applied to acceleration
        """
        self.name = name
        self.time = np.asarray(time, dtype=np.float64)
        self.acceleration = np.asarray(acceleration, dtype=np.float64) * scale_factor
        self.scale_factor = scale_factor

        # Compute time step if not provided
        if dt is not None:
            self.dt = dt
        elif len(time) > 1:
            self.dt = time[1] - time[0]
        else:
            self.dt = 0.005  # Default

        # Compute intensity measures
        self._compute_im()

    def _compute_im(self) -> None:
        """Compute intensity measures from acceleration history"""
        # Peak Ground Acceleration (g)
        self.pga = float(np.max(np.abs(self.acceleration)))

        # Peak Ground Velocity (cm/s) - integrate acceleration
        self.pgv = float(np.max(np.abs(np.cumsum(self.acceleration) * self.dt * 981)))  # Convert to cm/s

        # Peak Ground Displacement (cm)
        self.pgd = float(np.max(np.abs(np.cumsum(np.cumsum(self.acceleration)) * self.dt**2 * 981)))

        # Number of cycles (zero crossings / 2)
        accel_centered = self.acceleration - np.mean(self.acceleration)
        zero_crossings = np.sum(np.diff(np.sign(accel_centered)) != 0)
        self.cycles = zero_crossings / 2

        # Duration (significant duration)
        threshold = 0.05 * self.pga  # 5% of PGA
        significant_mask = np.abs(self.acceleration) > threshold
        if np.any(significant_mask):
            start_idx = np.argmax(significant_mask)
            # Find end
            end_mask = significant_mask[::-1]
            end_idx = len(significant_mask) - 1 - np.argmax(end_mask)
            self.duration = float((end_idx - start_idx) * self.dt)
        else:
            self.duration = float(len(self.acceleration) * self.dt)

    def scale(self, new_scale: float) -> 'GMRecord':
        """Return new record with scaled acceleration"""
        new_record = GMRecord(
            name=self.name,
            time=self.time.copy(),
            acceleration=self.acceleration.copy() / self.scale_factor,  # Descale first
            dt=self.dt,
            scale_factor=new_scale
        )
        return new_record

    def get_as_arrays(self) -> Tuple[np.ndarray, np.ndarray]:
        """Return time and acceleration as arrays"""
        return self.time.copy(), self.acceleration.copy()

    def __repr__(self) -> str:
        return (f"GMRecord('{self.name}': n={len(self.time)} points, "
                f"PGA={self.pga:.4f}g, duration={self.duration:.1f}s)")


def load_from_peer_nga(filepath: str, scale_factor: float = 1.0) -> GMRecord:
    """
    Load ground motion from PEER NGA West2 ASCII format

    PEER NGA format (typical):
    - Comment lines start with #
    - First non-comment line: number of points, dt
    - Remaining lines: acceleration values (multiple per line)

    Args:
        filepath: Path to ASCII file
        scale_factor: Scaling factor to apply

    Returns:
        GMRecord object
    """
    with open(filepath, 'r') as f:
        lines = f.readlines()

    # Filter comment lines
    data_lines = [line.strip() for line in lines if line.strip() and not line.strip().startswith('#')]

    if not data_lines:
        raise ValueError(f"No data found in {filepath}")

    # Parse header line (first non-comment line)
    header = data_lines[0].split()
    n_points = int(header[0])
    dt = float(header[1])  # Time step in seconds

    # Parse acceleration data
    accel_values = []
    for line in data_lines[1:]:
        values = line.split()
        for val in values:
            try:
                accel_values.append(float(val))
            except ValueError:
                continue

    if len(accel_values) != n_points:
        logger.warning(f"Expected {n_points} points, got {len(accel_values)}")

    # Create time array
    time = np.arange(0, n_points * dt, dt)[:n_points]
    accel = np.array(accel_values[:n_points], dtype=np.float64)

    # Extract filename without extension as name
    name = Path(filepath).stem

    return GMRecord(name=name, time=time, acceleration=accel, dt=dt, scale_factor=scale_factor)


def load_from_csv(filepath: str, time_col: str = 'time', accel_col: str = 'accel',
                  scale_factor: float = 1.0) -> GMRecord:
    """
    Load ground motion from CSV file

    Args:
        filepath: Path to CSV file
        time_col: Name of time column
        accel_col: Name of acceleration column
        scale_factor: Scaling factor to apply

    Returns:
        GMRecord object
    """
    df = pd.read_csv(filepath)

    time = df[time_col].values
    accel = df[accel_col].values

    # Compute dt from time array
    dt = None
    if len(time) > 1:
        dt = np.median(np.diff(time))

    name = Path(filepath).stem

    return GMRecord(name=name, time=time, acceleration=accel, dt=dt, scale_factor=scale_factor)


def load_from_npy(filepath: str, scale_factor: float = 1.0) -> GMRecord:
    """
    Load ground motion from NumPy .npy format

    Expected format: dict with 'time' and 'acceleration' arrays

    Args:
        filepath: Path to .npy file
        scale_factor: Scaling factor to apply

    Returns:
        GMRecord object
    """
    data = np.load(filepath, allow_pickle=True).item()

    time = data.get('time')
    accel = data.get('acceleration')

    if time is None or accel is None:
        raise ValueError("Expected 'time' and 'acceleration' keys in .npy file")

    name = Path(filepath).stem

    return GMRecord(name=name, time=time, acceleration=accel, scale_factor=scale_factor)


def load_ground_motion(filepath: str, scale_factor: float = 1.0) -> GMRecord:
    """
    Load ground motion from file, auto-detecting format

    Args:
        filepath: Path to ground motion file
        scale_factor: Scaling factor to apply

    Returns:
        GMRecord object

    Raises:
        ValueError: If file format is not recognized
    """
    ext = Path(filepath).suffix.lower()

    if ext in ['.txt', '.dat']:
        return load_from_peer_nga(filepath, scale_factor)
    elif ext == '.csv':
        return load_from_csv(filepath)
    elif ext == '.npy':
        return load_from_npy(filepath, scale_factor)
    else:
        # Try PEER NGA format first
        try:
            return load_from_peer_nga(filepath, scale_factor)
        except Exception as e1:
            # Try CSV
            try:
                return load_from_csv(filepath)
            except Exception as e2:
                raise ValueError(
                    f"Could not load {filepath}: {e1} (PEER NGA), {e2} (CSV)"
                )


def load_directory(directory: str, pattern: str = '*.txt',
                   scale_factor: float = 1.0) -> Dict[str, GMRecord]:
    """
    Load multiple ground motions from directory

    Args:
        directory: Path to directory containing GM files
        pattern: Glob pattern for files
        scale_factor: Scaling factor to apply to all records

    Returns:
        Dictionary mapping filename to GMRecord
    """
    gm_records = {}
    dir_path = Path(directory)

    for filepath in dir_path.glob(pattern):
        try:
            gm = load_ground_motion(str(filepath), scale_factor)
            gm_records[gm.name] = gm
            logger.info(f"Loaded {filepath.name}: {gm}")
        except Exception as e:
            logger.warning(f"Failed to load {filepath.name}: {e}")

    return gm_records


def generate_synthetic_gm(name: str = 'synthetic', duration: float = 30.0,
                          dt: float = 0.005, pga: float = 0.2,
                          frequency_band: Tuple[float, float] = (0.5, 2.0),
                          seed: Optional[int] = None) -> GMRecord:
    """
    Generate synthetic ground motion record

    Uses filtered white noise with target PGA and frequency content.

    Args:
        name: Record name
        duration: Duration in seconds
        dt: Time step in seconds
        pga: Target peak ground acceleration (g)
        frequency_band: (f_min, f_max) in Hz
        seed: Random seed for reproducibility

    Returns:
        GMRecord object
    """
    if seed is not None:
        np.random.seed(seed)

    n_points = int(duration / dt)

    # Generate white noise
    white_noise = np.random.normal(0, 1, n_points)

    # Create bandpass filter in frequency domain
    freqs = np.fft.rfftfreq(n_points, dt)
    fft = np.fft.rfft(white_noise)

    # Apply bandpass filter (Gaussian window around center frequency)
    f_center = np.sqrt(frequency_band[0] * frequency_band[1])
    f_width = (frequency_band[1] - frequency_band[0]) / 2

    filter_mask = np.exp(-0.5 * ((freqs - f_center) / f_width) ** 2)
    filter_mask[freqs < frequency_band[0]] = 0
    filter_mask[freqs > frequency_band[1]] = 0

    filtered_fft = fft * filter_mask
    synthetic = np.fft.irfft(filtered_fft, n=n_points)

    # Scale to target PGA
    current_pga = np.max(np.abs(synthetic))
    if current_pga > 0:
        synthetic = synthetic * (pga / current_pga)

    # Create time array
    time = np.arange(0, duration, dt)[:n_points]

    return GMRecord(name=name, time=time, acceleration=synthetic, dt=dt, scale_factor=1.0)


def generate_burst_waveform(name: str = 'burst', duration: float = 20.0,
                            dt: float = 0.005, pga: float = 0.3,
                            num_cycles: int = 5) -> GMRecord:
    """
    Generate synthetic ground motion with dominant frequency content

    Uses a damped harmonic burst approach to create motion with
    controlled frequency content, suitable for modal analysis.

    Args:
        name: Record name
        duration: Duration in seconds
        dt: Time step in seconds
        pga: Target peak ground acceleration (g)
        num_cycles: Number of dominant cycles

    Returns:
        GMRecord object
    """
    np.random.seed(42)  # For reproducibility

    n_points = int(duration / dt)
    time = np.linspace(0, duration, n_points)

    # Determine dominant period (typical for RC buildings: 0.5-1.5s)
    T_dominant = 0.8  # seconds
    f_dominant = 1.0 / T_dominant

    # Generate damped harmonic bursts
    synthetic = np.zeros(n_points)
    n_bursts = max(3, num_cycles // 2)

    for i in range(n_bursts):
        # Random start time and phase
        t_start = np.random.uniform(0, duration - 5)
        phase = np.random.uniform(0, 2 * np.pi)

        # Create burst envelope (Gaussian)
        burst_width = np.random.uniform(2, 5)  # seconds
        envelope = np.exp(-0.5 * ((time - t_start) / burst_width) ** 2)

        # Create oscillatory component
        oscillation = np.sin(2 * np.pi * f_dominant * (time - t_start) + phase)

        # Combined burst
        synthetic += envelope * oscillation

    # Scale to target PGA
    current_pga = np.max(np.abs(synthetic))
    if current_pga > 0:
        synthetic = synthetic * (pga / current_pga)

    return GMRecord(name=name, time=time, acceleration=synthetic, dt=dt, scale_factor=1.0)


def validate_ground_motion(gm: GMRecord, min_duration: float = 10.0,
                           min_pga: float = 0.001) -> Dict[str, Union[bool, List[str]]]:
    """
    Validate ground motion record

    Checks:
    - Sufficient duration
    - Reasonable PGA
    - No NaN/Inf values
    - Monotonic time array

    Args:
        gm: GMRecord to validate
        min_duration: Minimum required duration (seconds)
        min_pga: Minimum required PGA (g)

    Returns:
        Validation result dictionary with 'valid' flag and 'issues' list
    """
    issues = []

    # Check for NaN/Inf
    if np.any(np.isnan(gm.acceleration)):
        issues.append("Contains NaN values in acceleration")

    if np.any(np.isinf(gm.acceleration)):
        issues.append("Contains Inf values in acceleration")

    # Check duration
    if gm.duration < min_duration:
        issues.append(f"Duration {gm.duration:.1f}s < minimum {min_duration}s")

    # Check PGA
    if gm.pga < min_pga:
        issues.append(f"PGA {gm.pga:.4f}g < minimum {min_pga}g")

    # Check time array
    if not np.all(np.diff(gm.time) >= 0):
        issues.append("Time array is not monotonic")

    # Check dt consistency
    if len(gm.time) > 1:
        dts = np.diff(gm.time)
        dt_std = np.std(dts)
        if dt_std > 0.01 * gm.dt:
            issues.append(f"Time step varies (std={dt_std:.4f}s)")

    return {
        'valid': len(issues) == 0,
        'issues': issues,
        'pga': gm.pga,
        'duration': gm.duration,
        'n_points': len(gm.time)
    }


# File extensions supported
SUPPORTED_EXTENSIONS = {
    '.txt': 'PEER NGA ASCII',
    '.dat': 'PEER NGA ASCII',
    '.csv': 'CSV format',
    '.npy': 'NumPy format'
}


__all__ = [
    'GMRecord',
    'load_from_peer_nga',
    'load_from_csv',
    'load_from_npy',
    'load_ground_motion',
    'load_directory',
    'generate_synthetic_gm',
    'generate_burst_waveform',
    'validate_ground_motion',
    'SUPPORTED_EXTENSIONS'
]
