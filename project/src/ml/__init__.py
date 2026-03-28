"""Machine Learning Module

This module implements ML models for predicting peak inter-story drift ratio (PIDR)
of RC buildings from structural and seismic features across different framework types.

Key Classes:
- MLTrainer: Trains and evaluates ML models for individual framework types
- FrameworkComparisonTrainer: Compares model performance across frameworks
- ModelEvaluator: Computes performance metrics and validation
- SHAPAnalyzer: Generates SHAP-based feature importance analysis

Key Models Implemented:
- Linear Regression (scikit-learn)
- Random Forest (scikit-learn)
- XGBoost (xgboost)
- Artificial Neural Networks (TensorFlow/Keras)

Usage:
    from src.ml import MLTrainer
    import pandas as pd
    
    data = pd.read_csv('data/processed/training_data.csv')
    trainer = MLTrainer(data, config_path='config/analysis_config.yaml')
    
    models = trainer.train_all_models()
    trainer.evaluate_and_compare()
    trainer.generate_shap_plots()
    trainer.save_best_model('models/ml_models/')
"""

from .trainer import MLTrainer, FrameworkComparisonTrainer

__all__ = [
    'MLTrainer',
    'FrameworkComparisonTrainer'
]
