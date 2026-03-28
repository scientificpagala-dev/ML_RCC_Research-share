# logger.py - Logging utilities for the project
"""
Logging utilities for consistent logging across the project

Provides structured logging with different levels and output formats
for analysis tracking and debugging.
"""

import logging
import logging.handlers
import os
from pathlib import Path
from typing import Optional, Dict, Any
import sys


class ProjectLogger:
    """
    Configurable logger for the seismic analysis project

    Supports console and file logging with structured formatting.
    """

    def __init__(self, name: str = 'seismic_analysis',
                 log_level: str = 'INFO',
                 log_dir: str = 'logs',
                 console: bool = True,
                 file_logging: bool = True):
        """
        Initialize the project logger

        Args:
            name: Logger name
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_dir: Directory for log files
            console: Enable console logging
            file_logging: Enable file logging
        """
        self.name = name
        self.log_level = getattr(logging, log_level.upper(), logging.INFO)
        self.log_dir = Path(log_dir)
        self.console = console
        self.file_logging = file_logging

        # Create logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(self.log_level)

        # Remove existing handlers
        self.logger.handlers.clear()

        # Set up formatters
        self._setup_formatters()

        # Add handlers
        if console:
            self._add_console_handler()

        if file_logging:
            self._add_file_handler()

    def _setup_formatters(self):
        """Set up logging formatters"""
        # Detailed formatter for file logging
        self.file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # Simple formatter for console logging
        self.console_formatter = logging.Formatter(
            '%(levelname)s - %(message)s'
        )

    def _add_console_handler(self):
        """Add console logging handler"""
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.log_level)
        console_handler.setFormatter(self.console_formatter)
        self.logger.addHandler(console_handler)

    def _add_file_handler(self):
        """Add rotating file handler"""
        # Ensure log directory exists
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Create rotating file handler (10MB max, 5 backups)
        log_file = self.log_dir / f'{self.name}.log'
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=10*1024*1024, backupCount=5
        )
        file_handler.setLevel(self.log_level)
        file_handler.setFormatter(self.file_formatter)
        self.logger.addHandler(file_handler)

    def get_logger(self) -> logging.Logger:
        """Get the configured logger instance"""
        return self.logger

    def log_analysis_start(self, analysis_type: str, **kwargs):
        """Log the start of an analysis"""
        self.logger.info(f"Starting {analysis_type} analysis")
        if kwargs:
            self.logger.debug(f"Analysis parameters: {kwargs}")

    def log_analysis_end(self, analysis_type: str, status: str = 'completed',
                        duration: Optional[float] = None, **kwargs):
        """Log the end of an analysis"""
        message = f"{analysis_type} analysis {status}"
        if duration is not None:
            message += f" in {duration:.2f} seconds"

        if status.lower() == 'completed':
            self.logger.info(message)
        elif status.lower() == 'failed':
            self.logger.error(message)
        else:
            self.logger.warning(message)

        if kwargs:
            self.logger.debug(f"Analysis results: {kwargs}")

    def log_model_info(self, model_info: Dict[str, Any]):
        """Log model information"""
        self.logger.info("Model configuration:")
        for key, value in model_info.items():
            self.logger.info(f"  {key}: {value}")

    def log_performance_metrics(self, metrics: Dict[str, float],
                               prefix: str = "Performance"):
        """Log performance metrics"""
        self.logger.info(f"{prefix} metrics:")
        for metric, value in metrics.items():
            if isinstance(value, float):
                self.logger.info(f"  {metric}: {value:.4f}")
            else:
                self.logger.info(f"  {metric}: {value}")


class AnalysisLogger:
    """
    Specialized logger for seismic analysis tracking

    Provides methods for logging analysis progress, convergence,
    and results with structured output.
    """

    def __init__(self, analysis_name: str, log_dir: str = 'logs/analysis'):
        """Initialize analysis logger"""
        self.analysis_name = analysis_name
        self.project_logger = ProjectLogger(
            name=f'analysis_{analysis_name}',
            log_dir=log_dir
        )
        self.logger = self.project_logger.get_logger()

    def log_ida_progress(self, building_id: str, intensity: float,
                        pidr: float, step: int, total_steps: int):
        """Log IDA analysis progress"""
        self.logger.info(
            f"IDA Progress: Building {building_id} - "
            f"Step {step}/{total_steps} - SA={intensity:.3f}g - PIDR={pidr:.4f}"
        )

    def log_convergence_info(self, iteration: int, residual: float,
                           convergence_tol: float):
        """Log convergence information"""
        status = "converged" if residual <= convergence_tol else "iterating"
        self.logger.debug(
            f"Convergence: Iteration {iteration} - "
            f"Residual {residual:.2e} - {status}"
        )

    def log_model_validation(self, validation_results: Dict[str, Any]):
        """Log model validation results"""
        status = validation_results.get('overall_status', 'UNKNOWN')
        errors = validation_results.get('total_errors', 0)
        warnings = validation_results.get('total_warnings', 0)

        self.logger.info(f"Model validation: {status} ({errors} errors, {warnings} warnings)")

        if errors > 0:
            for error in validation_results.get('errors', [])[:5]:  # First 5 errors
                self.logger.error(f"  ERROR: {error}")

        if warnings > 0:
            for warning in validation_results.get('warnings', [])[:3]:  # First 3 warnings
                self.logger.warning(f"  WARNING: {warning}")

    def log_ml_training(self, model_name: str, epoch: Optional[int] = None,
                       metrics: Optional[Dict[str, float]] = None):
        """Log ML training progress"""
        message = f"Training {model_name}"
        if epoch is not None:
            message += f" - Epoch {epoch}"

        self.logger.info(message)

        if metrics:
            for metric, value in metrics.items():
                self.logger.debug(f"  {metric}: {value:.4f}")

    def log_error(self, error_msg: str, exception: Optional[Exception] = None):
        """Log error with optional exception details"""
        self.logger.error(error_msg)
        if exception:
            self.logger.error(f"Exception: {type(exception).__name__}: {str(exception)}")


def create_logger(name: str = 'seismic_analysis',
                 log_level: str = 'INFO',
                 log_dir: str = 'logs') -> logging.Logger:
    """
    Create a configured logger instance

    Args:
        name: Logger name
        log_level: Logging level
        log_dir: Log directory

    Returns:
        Configured logger instance
    """
    project_logger = ProjectLogger(name, log_level, log_dir)
    return project_logger.get_logger()


def setup_logging(log_level: str = 'INFO', log_dir: str = 'logs',
                 console: bool = True, file_logging: bool = True) -> None:
    """
    Set up logging for the entire application

    Args:
        log_level: Global logging level
        log_dir: Directory for log files
        console: Enable console logging
        file_logging: Enable file logging
    """
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    # Remove existing handlers
    root_logger.handlers.clear()

    # Add handlers based on configuration
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, log_level.upper(), logging.INFO))
        console_formatter = logging.Formatter('%(levelname)s - %(name)s - %(message)s')
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)

    if file_logging:
        os.makedirs(log_dir, exist_ok=True)
        file_handler = logging.handlers.RotatingFileHandler(
            os.path.join(log_dir, 'seismic_analysis.log'),
            maxBytes=10*1024*1024, backupCount=5
        )
        file_handler.setLevel(getattr(logging, log_level.upper(), logging.INFO))
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(name)s - %(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)


# Global logger instance
default_logger = None

def get_default_logger() -> logging.Logger:
    """Get the default project logger"""
    global default_logger
    if default_logger is None:
        default_logger = create_logger()
    return default_logger