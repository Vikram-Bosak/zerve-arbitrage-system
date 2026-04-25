"""
ML Models Module - Machine learning models for prediction and analysis
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging
import pickle
import os

from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, mean_squared_error, classification_report
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

from config import Config
from utils import logger, normalize_data

class MLPredictor:
    """Machine learning predictor for market movements"""
    
    def __init__(self):
        """Initialize ML predictor"""
        self.config = Config
        self.models = {}
        self.scalers = {}
        
        logger.info("MLPredictor initialized")
    
    def prepare_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Prepare features for ML models
        
        Args:
            data: Raw market data
            
        Returns:
            DataFrame with features
        """
        logger.info("Preparing features for ML models...")
        
        features = data.copy()
        
        # Price-based features
        features['price_spread'] = features['yes_price'] - features['no_price']
        features['price_ratio'] = features['yes_price'] / (features['no_price'] + 0.001)
        features['total_implied_prob'] = features['yes_price'] + features['no_price']
        
        # Volume-based features
        features['volume_per_liquidity'] = features['volume'] / (features['liquidity'] + 1)
        features['log_volume'] = np.log1p(features['volume'])
        features['log_liquidity'] = np.log1p(features['liquidity'])
        
        # Platform encoding
        platform_dummies = pd.get_dummies(features['platform'], prefix='platform')
        features = pd.concat([features, platform_dummies], axis=1)
        
        # Market category encoding (simplified)
        features['category_election'] = features['market'].str.contains('election', case=False, na=False).astype(int)
        features['category_fed'] = features['market'].str.contains('fed|rate', case=False, na=False).astype(int)
        features['category_tech'] = features['market'].str.contains('ai|tech', case=False, na=False).astype(int)
        features['category_sports'] = features['market'].str.contains('sport', case=False, na=False).astype(int)
        features['category_climate'] = features['market'].str.contains('climate|weather', case=False, na=False).astype(int)
        
        # Time-based features
        features['hour'] = pd.to_datetime(features['timestamp']).dt.hour
        features['day_of_week'] = pd.to_datetime(features['timestamp']).dt.dayofweek
        
        # Select numeric features
        numeric_features = features.select_dtypes(include=[np.number]).columns
        
        logger.info(f"Prepared {len(numeric_features)} features")
        return features[numeric_features]
    
    def train_movement_predictor(
        self,
        data: pd.DataFrame,
        target_col: str = 'yes_price'
    ) -> Dict:
        """
        Train model to predict price movements
        
        Args:
            data: Training data
            target_col: Target column name
            
        Returns:
            Training results
        """
        logger.info(f"Training movement predictor for {target_col}...")
        
        # Prepare features
        features = self.prepare_features(data)
        
        # Create target (next period price change)
        features['target'] = features[target_col].shift(-1)
        features = features.dropna()
        
        if len(features) < self.config.MIN_TRAINING_SAMPLES:
            logger.warning(f"Insufficient data for training: {len(features)} samples")
            return {'success': False, 'error': 'Insufficient data'}
        
        # Split features and target
        X = features.drop(['target', target_col], axis=1)
        y = features['target']
        
        # Train/test split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train model
        model = GradientBoostingRegressor(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            random_state=42
        )
        
        model.fit(X_train_scaled, y_train)
        
        # Evaluate
        train_pred = model.predict(X_train_scaled)
        test_pred = model.predict(X_test_scaled)
        
        train_mse = mean_squared_error(y_train, train_pred)
        test_mse = mean_squared_error(y_test, test_pred)
        
        # Cross-validation
        cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5)
        
        results = {
            'success': True,
            'model': model,
            'scaler': scaler,
            'train_mse': train_mse,
            'test_mse': test_mse,
            'cv_mean': cv_scores.mean(),
            'cv_std': cv_scores.std(),
            'feature_importance': dict(zip(X.columns, model.feature_importances_))
        }
        
        # Save model
        model_name = f"movement_predictor_{target_col}"
        self.models[model_name] = model
        self.scalers[model_name] = scaler
        
        logger.info(f"Movement predictor trained. Test MSE: {test_mse:.6f}")
        
        return results
    
    def train_arbitrage_classifier(
        self,
        opportunities: List[Dict]
    ) -> Dict:
        """
        Train classifier to predict successful arbitrage
        
        Args:
            opportunities: List of arbitrage opportunities
            
        Returns:
            Training results
        """
        logger.info("Training arbitrage classifier...")
        
        if len(opportunities) < self.config.MIN_TRAINING_SAMPLES:
            logger.warning("Insufficient opportunities for training")
            return {'success': False, 'error': 'Insufficient data'}
        
        # Prepare features
        df = pd.DataFrame(opportunities)
        
        features = pd.DataFrame({
            'arbitrage': df['arbitrage'],
            'volume': df['volume'],
            'liquidity': df['liquidity'],
            'price_spread': abs(df['price1'] - df['price2']),
            'platform_match': (df['platform1'] != df['platform2']).astype(int)
        })
        
        # Create target (successful if arbitrage > threshold)
        features['target'] = (df['arbitrage'] > self.config.MIN_ARBITRAGE_PERCENTAGE).astype(int)
        
        X = features.drop('target', axis=1)
        y = features['target']
        
        # Train/test split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train model
        model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        
        model.fit(X_train_scaled, y_train)
        
        # Evaluate
        train_pred = model.predict(X_train_scaled)
        test_pred = model.predict(X_test_scaled)
        
        train_accuracy = accuracy_score(y_train, train_pred)
        test_accuracy = accuracy_score(y_test, test_pred)
        
        results = {
            'success': True,
            'model': model,
            'scaler': scaler,
            'train_accuracy': train_accuracy,
            'test_accuracy': test_accuracy,
            'feature_importance': dict(zip(X.columns, model.feature_importances_))
        }
        
        # Save model
        self.models['arbitrage_classifier'] = model
        self.scalers['arbitrage_classifier'] = scaler
        
        logger.info(f"Arbitrage classifier trained. Test accuracy: {test_accuracy:.3f}")
        
        return results
    
    def predict_movement(
        self,
        data: pd.DataFrame,
        target_col: str = 'yes_price'
    ) -> np.ndarray:
        """
        Predict price movements
        
        Args:
            data: Market data
            target_col: Target column
            
        Returns:
            Predictions
        """
        model_name = f"movement_predictor_{target_col}"
        
        if model_name not in self.models:
            logger.error(f"Model {model_name} not trained")
            return np.array([])
        
        # Prepare features
        features = self.prepare_features(data)
        
        # Scale features
        scaler = self.scalers[model_name]
        X_scaled = scaler.transform(features)
        
        # Predict
        model = self.models[model_name]
        predictions = model.predict(X_scaled)
        
        logger.info(f"Generated {len(predictions)} predictions")
        return predictions
    
    def predict_arbitrage_success(
        self,
        opportunities: List[Dict]
    ) -> List[float]:
        """
        Predict probability of successful arbitrage
        
        Args:
            opportunities: List of opportunities
            
        Returns:
            List of success probabilities
        """
        if 'arbitrage_classifier' not in self.models:
            logger.error("Arbitrage classifier not trained")
            return [0.0] * len(opportunities)
        
        # Prepare features
        df = pd.DataFrame(opportunities)
        
        features = pd.DataFrame({
            'arbitrage': df['arbitrage'],
            'volume': df['volume'],
            'liquidity': df['liquidity'],
            'price_spread': abs(df['price1'] - df['price2']),
            'platform_match': (df['platform1'] != df['platform2']).astype(int)
        })
        
        # Scale features
        scaler = self.scalers['arbitrage_classifier']
        X_scaled = scaler.transform(features)
        
        # Predict probabilities
        model = self.models['arbitrage_classifier']
        probabilities = model.predict_proba(X_scaled)[:, 1]
        
        logger.info(f"Generated {len(probabilities)} success probability predictions")
        return probabilities
    
    def save_models(self, directory: str = None):
        """
        Save trained models to disk
        
        Args:
            directory: Directory to save models
        """
        if directory is None:
            directory = self.config.MODELS_DIR
        
        os.makedirs(directory, exist_ok=True)
        
        for model_name, model in self.models.items():
            filepath = os.path.join(directory, f"{model_name}.pkl")
            with open(filepath, 'wb') as f:
                pickle.dump(model, f)
            
            # Save scaler
            scaler = self.scalers.get(model_name)
            if scaler:
                scaler_path = os.path.join(directory, f"{model_name}_scaler.pkl")
                with open(scaler_path, 'wb') as f:
                    pickle.dump(scaler, f)
        
        logger.info(f"Saved {len(self.models)} models to {directory}")
    
    def load_models(self, directory: str = None):
        """
        Load trained models from disk
        
        Args:
            directory: Directory to load models from
        """
        if directory is None:
            directory = self.config.MODELS_DIR
        
        if not os.path.exists(directory):
            logger.warning(f"Models directory not found: {directory}")
            return
        
        # Load models
        for filename in os.listdir(directory):
            if filename.endswith('.pkl') and not filename.endswith('_scaler.pkl'):
                model_name = filename.replace('.pkl', '')
                filepath = os.path.join(directory, filename)
                
                with open(filepath, 'rb') as f:
                    self.models[model_name] = pickle.load(f)
                
                # Load scaler
                scaler_path = os.path.join(directory, f"{model_name}_scaler.pkl")
                if os.path.exists(scaler_path):
                    with open(scaler_path, 'rb') as f:
                        self.scalers[model_name] = pickle.load(f)
        
        logger.info(f"Loaded {len(self.models)} models from {directory}")

if __name__ == "__main__":
    # Test ML predictor
    from data_collector import DataCollector
    
    # Collect data
    collector = DataCollector()
    raw_data = collector.collect_all_data()
    normalized_data = collector.normalize_market_data(raw_data)
    
    # Train models
    predictor = MLPredictor()
    
    # Train movement predictor
    movement_results = predictor.train_movement_predictor(normalized_data)
    print(f"Movement Predictor Results: {movement_results}")
    
    # Save models
    predictor.save_models()
    
    print("\nML models test completed successfully!")
