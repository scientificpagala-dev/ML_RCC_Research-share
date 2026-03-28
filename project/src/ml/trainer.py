# trainer.py - ML Model Training for Seismic Drift Prediction
"""
Machine Learning Pipeline for Seismic Drift Prediction

Supports training separate models for different framework types:
- Non-Sway, OMRF, IMRF, SMRF
- Multiple algorithms: Linear Regression, Random Forest, XGBoost, Neural Networks
- Framework-specific feature engineering and hyperparameter tuning
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
import xgboost as xgb
import tensorflow as tf
import tensorflow.keras as keras  # type: ignore
import joblib
import yaml
import os
from typing import Dict, List, Optional, Tuple, Union
from pathlib import Path


class MLTrainer:
    """
    Machine Learning Trainer for Seismic Drift Prediction

    Trains and evaluates ML models for different framework types
    """

    def __init__(self, framework_type: str, config_path: str = 'config/analysis_config.yaml'):
        """
        Initialize ML trainer

        Args:
            framework_type: 'nonsway', 'omrf', 'imrf', 'smrf'
            config_path: Path to analysis configuration
        """
        self.framework_type = framework_type

        # Load configuration
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        self.ml_config = self.config.get('machine_learning', {})
        self.models = {}
        self.scaler = None
        self.feature_names = None

    def load_data(self, data_path: str) -> pd.DataFrame:
        """
        Load training data for the framework

        Args:
            data_path: Path to CSV file with IDA results

        Returns:
            Processed DataFrame
        """
        df = pd.read_csv(data_path)

        # Filter for framework type
        if 'framework' in df.columns:
            df = df[df['framework'] == self.framework_type]

        # Feature engineering
        df = self._engineer_features(df)

        return df

    def _engineer_features(self, df: Union[pd.DataFrame, pd.Series]) -> pd.DataFrame:
        """Engineer features for ML training"""
        # Convert Series to DataFrame if needed
        if isinstance(df, pd.Series):
            df = df.to_frame()
        
        # Basic features
        features = [
            'n_stories', 'total_height', 'fundamental_period',
            'column_area', 'beam_area', 'reinforcement_ratio',
            'seismic_zone_coeff', 'response_mod_factor', 'importance_factor',
            'ln_spectral_acceleration'
        ]

        # Framework-specific features
        if self.framework_type == 'smrf':
            features.extend(['confinement_factor', 'transverse_reinf_ratio'])
        elif self.framework_type in ['omrf', 'imrf']:
            features.extend(['light_confinement_factor'])

        # Create log-transformed target
        df['ln_pidr'] = np.log(df['peak_interstory_drift_ratio'].clip(lower=1e-6))

        # Ensure all features exist
        available_features = [f for f in features if f in df.columns]
        self.feature_names = available_features

        return df

    def prepare_data(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Prepare data for training

        Returns:
            X_train, X_test, y_train, y_test
        """
        X = df[self.feature_names].values
        y = df['ln_pidr'].values

        # Split data
        split_config = self.ml_config.get('data_split', {})
        test_size = split_config.get('test_ratio', 0.20)
        random_state = split_config.get('random_state', 42)

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )

        # Scale features
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        return X_train_scaled, X_test_scaled, y_train, y_test

    def train_all_models(self, X_train: np.ndarray, y_train: np.ndarray) -> Dict:
        """Train all configured ML models"""
        models_config = self.ml_config.get('models', {})

        # Linear Regression
        if models_config.get('linear_regression', {}).get('enabled', True):
            self.models['linear_regression'] = LinearRegression()
            self.models['linear_regression'].fit(X_train, y_train)

        # Random Forest
        if models_config.get('random_forest', {}).get('enabled', True):
            rf_config = models_config['random_forest'].get('hyperparameters', {})
            self.models['random_forest'] = RandomForestRegressor(**rf_config)
            self.models['random_forest'].fit(X_train, y_train)

        # XGBoost
        if models_config.get('xgboost', {}).get('enabled', True):
            xgb_config = models_config['xgboost'].get('hyperparameters', {})
            self.models['xgboost'] = xgb.XGBRegressor(**xgb_config)
            self.models['xgboost'].fit(X_train, y_train)

        # Neural Network
        if models_config.get('neural_network', {}).get('enabled', True):
            self.models['neural_network'] = self._train_neural_network(X_train, y_train)

        return self.models

    def _train_neural_network(self, X_train: np.ndarray, y_train: np.ndarray):
        """Train neural network model"""
        nn_config = self.ml_config['models']['neural_network']['hyperparameters']

        model = keras.Sequential()
        layers = nn_config.get('hidden_layers', [64, 32])

        # Input layer
        model.add(keras.layers.Input(shape=(X_train.shape[1],)))
        model.add(keras.layers.Dense(layers[0], activation='relu'))

        # Hidden layers
        for units in layers[1:]:
            model.add(keras.layers.Dense(units, activation='relu'))
            if nn_config.get('dropout_rate', 0) > 0:
                model.add(keras.layers.Dropout(nn_config['dropout_rate']))

        # Output layer
        model.add(keras.layers.Dense(1, activation='linear'))

        # Compile
        optimizer = nn_config.get('optimizer', 'adam')
        loss = nn_config.get('loss', 'mse')
        model.compile(optimizer=optimizer, loss=loss, metrics=['mae', 'mse'])

        # Train
        epochs = nn_config.get('epochs', 100)
        batch_size = nn_config.get('batch_size', 32)
        validation_split = nn_config.get('validation_split', 0.2)

        early_stopping = keras.callbacks.EarlyStopping(
            patience=nn_config.get('patience', 10),
            restore_best_weights=True
        )

        model.fit(X_train, y_train,
                 epochs=epochs,
                 batch_size=batch_size,
                 validation_split=validation_split,
                 callbacks=[early_stopping],
                 verbose=0)

        return model

    def evaluate_models(self, X_test: np.ndarray, y_test: np.ndarray) -> Dict:
        """Evaluate all trained models"""
        results = {}

        for model_name, model in self.models.items():
            # Predictions
            if model_name == 'neural_network':
                y_pred = model.predict(X_test).flatten()
            else:
                y_pred = model.predict(X_test)

            # Metrics
            r2 = r2_score(y_test, y_pred)
            rmse = np.sqrt(mean_squared_error(y_test, y_pred))
            mae = mean_absolute_error(y_test, y_pred)

            results[model_name] = {
                'r2': r2,
                'rmse': rmse,
                'mae': mae,
                'predictions': y_pred,
                'actual': y_test
            }

        return results

    def select_best_model(self, evaluation_results: Dict) -> str:
        """Select best model based on R² score"""
        best_model = max(evaluation_results.keys(),
                        key=lambda x: evaluation_results[x]['r2'])
        return best_model

    def save_models(self, output_dir: str = 'models/ml_models'):
        """Save trained models"""
        os.makedirs(output_dir, exist_ok=True)

        for model_name, model in self.models.items():
            if model_name == 'neural_network':
                # Save Keras model
                model_path = os.path.join(output_dir, f'{self.framework_type}_{model_name}.h5')
                model.save(model_path)
            else:
                # Save sklearn model
                model_path = os.path.join(output_dir, f'{self.framework_type}_{model_name}.joblib')
                joblib.dump(model, model_path)

        # Save scaler
        scaler_path = os.path.join(output_dir, f'{self.framework_type}_scaler.joblib')
        joblib.dump(self.scaler, scaler_path)

        # Save feature names
        feature_path = os.path.join(output_dir, f'{self.framework_type}_features.txt')
        if self.feature_names is not None:
            with open(feature_path, 'w') as f:
                f.write('\n'.join(self.feature_names))

    def cross_validate(self, X: np.ndarray, y: np.ndarray, cv_folds: int = 5) -> Dict:
        """Perform cross-validation for all models"""
        cv_results = {}

        for model_name, model in self.models.items():
            if model_name == 'neural_network':
                # Skip CV for neural networks (computationally expensive)
                cv_results[model_name] = {'mean_r2': None, 'std_r2': None}
                continue

            scores = cross_val_score(model, X, y, cv=cv_folds, scoring='r2')
            cv_results[model_name] = {
                'mean_r2': scores.mean(),
                'std_r2': scores.std(),
                'cv_folds': cv_folds
            }

        return cv_results


class FrameworkComparisonTrainer:
    """
    Trainer for comparing models across different framework types
    """

    def __init__(self, config_path: str = 'config/analysis_config.yaml'):
        """Initialize comparison trainer"""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        self.frameworks = ['nonsway', 'omrf', 'imrf', 'smrf']
        self.trainers = {}
        self.results = {}

    def train_all_frameworks(self, data_paths: Dict[str, str]):
        """
        Train models for all framework types

        Args:
            data_paths: Dict mapping framework to data file path
        """
        for framework in self.frameworks:
            if framework in data_paths:
                print(f"Training models for {framework}...")

                # Create trainer
                trainer = MLTrainer(framework, self.config)

                # Load and prepare data
                df = trainer.load_data(data_paths[framework])
                X_train, X_test, y_train, y_test = trainer.prepare_data(df)

                # Train models
                trainer.train_all_models(X_train, y_train)

                # Evaluate
                eval_results = trainer.evaluate_models(X_test, y_test)

                # Cross-validate
                cv_results = trainer.cross_validate(
                    np.vstack([X_train, X_test]),
                    np.concatenate([y_train, y_test])
                )

                # Store results
                self.trainers[framework] = trainer
                self.results[framework] = {
                    'evaluation': eval_results,
                    'cross_validation': cv_results,
                    'best_model': trainer.select_best_model(eval_results)
                }

    def generate_comparison_report(self) -> Dict:
        """Generate comparison report across frameworks"""
        report = {
            'frameworks': self.frameworks,
            'best_models': {},
            'performance_comparison': {},
            'recommendations': {}
        }

        for framework in self.frameworks:
            if framework in self.results:
                result = self.results[framework]
                best_model = result['best_model']
                best_r2 = result['evaluation'][best_model]['r2']

                report['best_models'][framework] = {
                    'model': best_model,
                    'r2_score': best_r2
                }

        # Framework performance ranking
        framework_ranking = sorted(
            report['best_models'].keys(),
            key=lambda x: report['best_models'][x]['r2_score'],
            reverse=True
        )

        report['performance_ranking'] = framework_ranking

        return report