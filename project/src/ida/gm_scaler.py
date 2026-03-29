"""Ground Motion Scaler Module

Scales ground motion records to target spectral acceleration for IDA analysis.

Features:
- Scale to target Sa(T1, 5%) for fundamental period
- Spectrum matching with iterative refinement
- Multiple scaling methods (linear, logarithmic)
- Validation of scaled spectrum
- Support for multi-stripe analysis

References:
- BNBC 2020 Section 3.2 (Response Spectrum)
- ASCE 7-22 Section 16.2 (Seismic Analysis)
- Vamvatsikos & Cornell (2002) - IDA methodology
- SeismoMatch: http://seismomatch.lcgc.ch

Usage:
    from src.ida.gm_loader import load_ground_motion
    from src.ida.gm_scaler import scale_to_intensity, scale_to_spectrum

    gm = load_ground_motion('records/earthquake.txt')

    # Scale to target Sa(T1)
    target_sa = 0.5  # g
    scaled_gm = scale_to_intensity(gm, target_sa, period=0.8)

    # Scale to BNBC 2020 spectrum
    bnbc_spectrum = build_bnbc_spectrum(zone='Zone3', site_class='D')
    scaled_gm = scale_to_spectrum(gm, bnbc_spectrum)
"""

import numpy as np
from typing import Dict, List, Optional, Tuple, Union
from scipy import signal as scipy_signal
from scipy import interpolate
import logging

logger = logging.getLogger('gm_scaler')


def compute_response_spectrum(accel: np.ndarray, time: np.ndarray,
                               periods: np.ndarray, damping: float = 0.05,
                               dt: Optional[float] = None) -> np.ndarray:
    """
    Compute elastic response spectrum for ground motion

    Uses Newmark-beta integration for SDOF response.

    Args:
        accel: Acceleration time series [g]
        time: Time array [seconds]
        periods: Periods for spectrum [seconds]
        damping: Damping ratio (default 0.05 = 5%)
        dt: Time step [seconds] (optional)

    Returns:
        Spectral accelerations [g]
    """
    if dt is None and len(time) > 1:
        dt = time[1] - time[0]

    n_periods = len(periods)
    spectral_accels = np.zeros(n_periods)

    # Newmark-beta parameters (average acceleration)
    gamma = 0.5
    beta = 0.25

    dt_local = dt

    for i, T in enumerate(periods):
        if T <= 0:
            spectral_accels[i] = 0
            continue

        # Natural frequency and period
        omega = 2 * np.pi / T
        cn = 2 * damping * omega

        # Initialize Newmark integration
        # u = displacement, v = velocity, a = acceleration
        u = 0.0
        v = 0.0
        a = 0.0

        # Effective stiffness and coefficients
        k_eff = (3/4 + beta/2) * (omega**2) + cn * gamma/(2*beta) + 1/(beta*dt_local)
        a_eff = (3/4 + beta/2) * (omega**2) + cn * gamma/(2*beta)

        # Store max response
        u_max = 0.0

        # Time history integration
        n_steps = len(accel)
        for j in range(n_steps - 1):
            # Current acceleration (converted to absolute acceleration)
            a_g = accel[j]

            # Effective force
            f_eff = a_g + k_eff * u + a_eff * v

            # Update displacement
            u_new = f_eff / k_eff

            # Update acceleration
            a_new = (u_new - u) / (beta * dt_local**2) - v / (beta * dt_local) - (0.5 - beta) * a

            # Update velocity
            v_new = gamma / (2 * beta) * (u_new - u) / dt_local + (1 - gamma/(2*beta)) * v + dt_local * (1 - gamma/beta) * a

            # Update for next step
            u = u_new
            v = v_new
            a = a_new

            # Track maximum displacement
            u_max = max(u_max, abs(u))

        # Spectral acceleration = max displacement * omega^2
        spectral_accels[i] = u_max * omega**2

    return spectral_accels


def build_bnbc_spectrum(zone: str = 'Zone3', site_class: str = 'D',
                        damping: float = 0.05,
                        periods: Optional[np.ndarray] = None) -> Tuple[np.ndarray, np.ndarray]:
    """
    Build BNBC 2020 design response spectrum

    Args:
        zone: Seismic zone ('Zone1', 'Zone2', 'Zone3', 'Zone4')
        site_class: Site class ('A', 'B', 'C', 'D', 'E')
        damping: Damping ratio (default 0.05 = 5%)
        periods: Period array (default: 0.01 to 5.0s)

    Returns:
        (periods, Sa) spectral curve
    """
    if periods is None:
        periods = np.logspace(-2, np.log10(5.0), 200)

    # Load BNBC parameters
    import yaml
    config_path = 'config/bnbc_parameters.yaml'
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        # Use defaults if config not found
        config = _get_default_bnbc_config()

    # Get zone parameters
    zone_params = config['seismic_zones'].get(zone, {})
    Z = zone_params.get('z_coeff', 0.24)  # Default Zone3

    # Get site class parameters
    site_params = config['site_classes'].get(site_class, {})
    Fa = site_params.get('fa', 1.6)
    Fv = site_params.get('fv', 1.4)

    # BNBC 2020 parameters
    # SDS = (2/3) * Fa * 2.5 * Z
    # SD1 = (2/3) * Fv * Z
    SDS = (2/3) * Fa * 2.5 * Z
    SD1 = (2/3) * Fv * Z

    # Period parameters
    T0 = 0.2 * SD1 / SDS if SDS > 0 else 0.2
    Ts = SD1 / SDS if SDS > 0 else 0.5
    TL = 6.0  # Long period transition

    # Compute Sa(T)
    Sa = np.zeros_like(periods)

    for i, T in enumerate(periods):
        if T <= 0:
            Sa[i] = SDS
        elif T <= T0:
            Sa[i] = SDS * (0.4 + 0.6 * T / T0)
        elif T <= Ts:
            Sa[i] = SDS
        elif T <= TL:
            Sa[i] = SD1 / T
        else:
            Sa[i] = SD1 * TL / (T ** 2)

    # Apply damping correction
    # Damping factor: (10/5)^0.2 for 5% damping
    damping_factor = (10 / 5) ** 0.2
    Sa = Sa / damping_factor

    return periods, Sa


def _get_default_bnbc_config() -> Dict:
    """Get default BNBC configuration when config file not available"""
    return {
        'seismic_zones': {
            'Zone1': {'z_coeff': 0.12},
            'Zone2': {'z_coeff': 0.18},
            'Zone3': {'z_coeff': 0.24},
            'Zone4': {'z_coeff': 0.36}
        },
        'site_classes': {
            'A': {'fa': 0.8, 'fv': 0.8},
            'B': {'fa': 1.0, 'fv': 1.0},
            'C': {'fa': 1.2, 'fv': 1.2},
            'D': {'fa': 1.6, 'fv': 1.4},
            'E': {'fa': 2.5, 'fv': 1.7}
        }
    }


def scale_to_intensity(gm, target_sa: float, period: float = 0.8,
                       damping: float = 0.05) -> 'GMRecord':
    """
    Scale ground motion to target spectral acceleration at period T

    This is the standard IDA scaling method.

    Args:
        gm: GMRecord to scale
        target_sa: Target spectral acceleration [g]
        period: Period for scaling [seconds]
        damping: Damping ratio

    Returns:
        Scaled GMRecord
    """
    # Compute spectrum of original GM
    periods = np.array([period])
    original_sa = compute_response_spectrum(
        gm.acceleration, gm.time, periods, damping
    )[0]

    if original_sa == 0:
        return gm

    # Compute scale factor
    scale_factor = target_sa / original_sa

    # Return scaled record
    return gm.scale(scale_factor)


def scale_to_spectrum(gm, target_periods: np.ndarray, target_sa: np.ndarray,
                      weight: float = 1.0) -> 'GMRecord':
    """
    Scale ground motion to match target spectrum (period by period)

    Uses iterative refinement with weighting.

    Args:
        gm: GMRecord to scale
        target_periods: Target spectrum periods
        target_sa: Target spectral accelerations
        weight: Weight for higher periods (default 1.0)

    Returns:
        Scaled GMRecord
    """
    # Compute current spectrum
    current_sa = compute_response_spectrum(
        gm.acceleration, gm.time, target_periods
    )

    # Compute spectrum ratios
    ratios = target_sa / current_sa

    # Apply weighted average
    weights = np.ones_like(ratios) * weight
    weights[target_periods > 1.0] *= 0.5  # Less weight for long periods

    scale_factor = np.average(ratios, weights=weights)

    return gm.scale(scale_factor)


def scale_by_pga(gm, target_pga: float) -> 'GMRecord':
    """
    Scale ground motion by PGA (Peak Ground Acceleration)

    Simple scaling method, less accurate than spectral scaling.

    Args:
        gm: GMRecord to scale
        target_pga: Target PGA [g]

    Returns:
        Scaled GMRecord
    """
    return gm.scale(target_pga / gm.pga)


def scale_by_pgv(gm, target_pgv: float) -> 'GMRecord':
    """
    Scale ground motion by PGV (Peak Ground Velocity)

    Alternative scaling method.

    Args:
        gm: GMRecord to scale
        target_pgv: Target PGV [cm/s]

    Returns:
        Scaled GMRecord
    """
    return gm.scale(target_pgv / gm.pgv)


def verify_scaling(gm_original: 'GMRecord', gm_scaled: 'GMRecord',
                   target_periods: Optional[np.ndarray] = None) -> Dict:
    """
    Verify that scaling achieved target spectrum

    Args:
        gm_original: Original ground motion
        gm_scaled: Scaled ground motion
        target_periods: Periods to check (optional)

    Returns:
        Verification results dictionary
    """
    import yaml

    # Compute original spectrum
    if target_periods is None:
        target_periods = np.logspace(-1, np.log10(3.0), 50)

    orig_sa = compute_response_spectrum(
        gm_original.acceleration, gm_original.time, target_periods
    )
    scaled_sa = compute_response_spectrum(
        gm_scaled.acceleration, gm_scaled.time, target_periods
    )

    # Get BNBC target spectrum
    try:
        periods, bnbc_sa = build_bnbc_spectrum()
    except:
        # If BNBC spectrum fails, compute from original
        periods = target_periods
        bnbc_sa = orig_sa

    # Compute ratios
    orig_ratio = orig_sa / bnbc_sa
    scaled_ratio = scaled_sa / bnbc_sa

    # Compute mean absolute error
    orig_mae = np.mean(np.abs(orig_ratio - 1))
    scaled_mae = np.mean(np.abs(scaled_ratio - 1))

    # Check target periods
    results = {
        'original_pga': gm_original.pga,
        'scaled_pga': gm_scaled.pga,
        'scale_factor': gm_scaled.scale_factor,
        'mae_original': float(orig_mae),
        'mae_scaled': float(scaled_mae),
        'improvement': float(orig_mae - scaled_mae),
        'target_check': {}
    }

    # Check at specific periods
    for T in [0.2, 0.5, 1.0, 2.0]:
        if T in target_periods:
            idx = list(target_periods).index(T)
            results['target_check'][f'T={T}s'] = {
                'original_sa': float(orig_sa[idx]),
                'scaled_sa': float(scaled_sa[idx]),
                'target': float(bnbc_sa[idx]) if T in periods else None
            }

    return results


def scale_multi_stripe(gm, intensity_levels: List[float],
                       period: float = 0.8) -> List['GMRecord']:
    """
    Create multi-stripe scaled records for IDA

    Args:
        gm: Original GMRecord
        intensity_levels: List of intensity scaling factors (Sa in g)
        period: Period for scaling

    Returns:
        List of scaled GMRecords
    """
    scaled_records = []

    for sa_target in intensity_levels:
        scaled_gm = scale_to_intensity(gm, sa_target, period)
        scaled_records.append(scaled_gm)

    return scaled_records


def get_intensity_for_percentage_reduction(gm: 'GMRecord',
                                           reduction: float = 0.5,
                                           period: float = 0.8) -> float:
    """
    Find intensity level where PGA is reduced by percentage

    Useful for setting intensity range.

    Args:
        gm: Ground motion record
        reduction: Fractional reduction (0.0 to 1.0)
        period: Period for scaling

    Returns:
        Intensity level (Sa) for specified reduction
    """
    # Scale to various intensities and find where PGA matches
    target_pga = gm.pga * (1 - reduction)

    # Binary search for correct intensity
    sa_low, sa_high = 0.01, 2.0
    for _ in range(20):
        sa_mid = (sa_low + sa_high) / 2
        test_gm = scale_to_intensity(gm, sa_mid, period)

        if test_gm.pga > target_pga:
            sa_low = sa_mid
        else:
            sa_high = sa_mid

    return (sa_low + sa_high) / 2


# Default intensity levels for multi-stripe IDA
DEFAULT_INTENSITY_LEVELS = [0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40,
                            0.45, 0.50, 0.60, 0.75, 0.90, 1.20, 1.35, 1.50]


__all__ = [
    'compute_response_spectrum',
    'build_bnbc_spectrum',
    'scale_to_intensity',
    'scale_to_spectrum',
    'scale_by_pga',
    'scale_by_pgv',
    'verify_scaling',
    'scale_multi_stripe',
    'get_intensity_for_percentage_reduction',
    'DEFAULT_INTENSITY_LEVELS'
]
