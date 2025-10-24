"""
Machine Learning Price Predictor for Product Price Tracker
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, r2_score
from typing import Dict, List, Tuple, Optional
import pickle
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PricePredictor:
    """ML model to predict future price trends"""

    def __init__(self, model_type: str = 'random_forest'):
        self.model_type = model_type
        self.model = None
        self.scaler = StandardScaler()
        self.is_trained = False
        self.feature_names = []
        self.model_path = "ml/models/"

        # Create models directory
        os.makedirs(self.model_path, exist_ok=True)

        # Initialize model
        if model_type == 'random_forest':
            self.model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                n_jobs=-1
            )
        elif model_type == 'linear_regression':
            self.model = LinearRegression()
        else:
            raise ValueError(f"Unsupported model type: {model_type}")

    def prepare_features(self, price_history: pd.DataFrame) -> pd.DataFrame:
        """
        Extract features from price history for ML model

        Features extracted:
        - Day of week (0-6)
        - Day of month (1-31)
        - Week of month (1-5)
        - Month of year (1-12)
        - Moving averages (7, 14, 30 days)
        - Price volatility (rolling standard deviation)
        - Price momentum (rate of change)
        - Seasonal patterns
        """
        if price_history.empty:
            return pd.DataFrame()

        df = price_history.copy()

        # Ensure timestamp is datetime
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.set_index('timestamp')

        # Sort by timestamp
        df = df.sort_index()

        # Basic time features
        df['day_of_week'] = df.index.dayofweek
        df['day_of_month'] = df.index.day
        df['week_of_month'] = (df.index.day - 1) // 7 + 1
        df['month'] = df.index.month
        df['quarter'] = df.index.quarter

        # Cyclical encoding for periodic features
        df['day_of_week_sin'] = np.sin(2 * np.pi * df['day_of_week'] / 7)
        df['day_of_week_cos'] = np.cos(2 * np.pi * df['day_of_week'] / 7)
        df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
        df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)

        # Moving averages
        df['ma_3'] = df['price'].rolling(window=3, min_periods=1).mean()
        df['ma_7'] = df['price'].rolling(window=7, min_periods=1).mean()
        df['ma_14'] = df['price'].rolling(window=14, min_periods=1).mean()
        df['ma_30'] = df['price'].rolling(window=30, min_periods=1).mean()

        # Price volatility (rolling standard deviation)
        df['volatility_7'] = df['price'].rolling(window=7, min_periods=1).std()
        df['volatility_14'] = df['price'].rolling(window=14, min_periods=1).std()
        df['volatility_30'] = df['price'].rolling(window=30, min_periods=1).std()

        # Price momentum (rate of change)
        df['momentum_3'] = df['price'].pct_change(periods=3)
        df['momentum_7'] = df['price'].pct_change(periods=7)
        df['momentum_14'] = df['price'].pct_change(periods=14)

        # Price position relative to moving averages
        df['price_vs_ma7'] = (df['price'] - df['ma_7']) / df['ma_7']
        df['price_vs_ma14'] = (df['price'] - df['ma_14']) / df['ma_14']
        df['price_vs_ma30'] = (df['price'] - df['ma_30']) / df['ma_30']

        # Lag features (previous prices)
        df['price_lag_1'] = df['price'].shift(1)
        df['price_lag_3'] = df['price'].shift(3)
        df['price_lag_7'] = df['price'].shift(7)

        # Min/Max prices in rolling windows
        df['min_price_7'] = df['price'].rolling(window=7, min_periods=1).min()
        df['max_price_7'] = df['price'].rolling(window=7, min_periods=1).max()
        df['min_price_30'] = df['price'].rolling(window=30, min_periods=1).min()
        df['max_price_30'] = df['price'].rolling(window=30, min_periods=1).max()

        # Price range features
        df['price_range_7'] = df['max_price_7'] - df['min_price_7']
        df['price_range_30'] = df['max_price_30'] - df['min_price_30']

        # Fill NaN values
        df = df.fillna(method='bfill').fillna(method='ffill')

        # Store feature names
        self.feature_names = [col for col in df.columns if col != 'price']

        return df.dropna()

    def train(self, price_history: pd.DataFrame, product_id: int = None) -> Dict:
        """
        Train the price prediction model

        Args:
            price_history: DataFrame with columns ['timestamp', 'price']
            product_id: Optional product ID for model versioning

        Returns:
            Training metrics dictionary
        """
        logger.info(f"Training {self.model_type} model with {len(price_history)} data points")

        # Prepare features
        features_df = self.prepare_features(price_history)

        if features_df.empty or len(features_df) < 10:
            logger.warning("Insufficient data for training (need at least 10 data points)")
            return {"error": "Insufficient data"}

        # Prepare training data
        X = features_df[self.feature_names].values
        y = features_df['price'].values

        # Split into train/test (80/20)
        split_idx = int(0.8 * len(X))
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]

        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        # Train model
        self.model.fit(X_train_scaled, y_train)
        self.is_trained = True

        # Evaluate model
        y_pred_train = self.model.predict(X_train_scaled)
        y_pred_test = self.model.predict(X_test_scaled)

        metrics = {
            "train_mae": mean_absolute_error(y_train, y_pred_train),
            "test_mae": mean_absolute_error(y_test, y_pred_test),
            "train_r2": r2_score(y_train, y_pred_train),
            "test_r2": r2_score(y_test, y_pred_test),
            "training_samples": len(X_train),
            "test_samples": len(X_test),
            "features": len(self.feature_names)
        }

        logger.info(f"Model trained successfully. Test R²: {metrics['test_r2']:.3f}, Test MAE: {metrics['test_mae']:.2f}")

        # Save model
        if product_id:
            self.save_model(f"model_product_{product_id}")

        return metrics

    def predict_next_days(self, recent_history: pd.DataFrame, days: int = 7) -> Dict:
        """
        Predict prices for the next N days

        Args:
            recent_history: Recent price history (at least 30 days recommended)
            days: Number of days to predict (default: 7)

        Returns:
            Dictionary with predictions, dates, and confidence intervals
        """
        if not self.is_trained:
            logger.error("Model not trained yet")
            return {"error": "Model not trained"}

        # Prepare features from recent history
        features_df = self.prepare_features(recent_history)

        if features_df.empty:
            return {"error": "Insufficient recent history"}

        predictions = []
        confidence_intervals = []
        prediction_dates = []

        # Get the last known data point
        last_data = features_df.iloc[-1:].copy()
        last_date = features_df.index[-1]

        for day in range(1, days + 1):
            # Create future date
            future_date = last_date + timedelta(days=day)
            prediction_dates.append(future_date)

            # Update time-based features for future date
            future_features = last_data.copy()
            future_features.index = [future_date]

            # Update time features
            future_features['day_of_week'] = future_date.dayofweek
            future_features['day_of_month'] = future_date.day
            future_features['week_of_month'] = (future_date.day - 1) // 7 + 1
            future_features['month'] = future_date.month
            future_features['quarter'] = future_date.quarter

            # Update cyclical encodings
            future_features['day_of_week_sin'] = np.sin(2 * np.pi * future_date.dayofweek / 7)
            future_features['day_of_week_cos'] = np.cos(2 * np.pi * future_date.dayofweek / 7)
            future_features['month_sin'] = np.sin(2 * np.pi * future_date.month / 12)
            future_features['month_cos'] = np.cos(2 * np.pi * future_date.month / 12)

            # Prepare features for prediction
            X_future = future_features[self.feature_names].values
            X_future_scaled = self.scaler.transform(X_future)

            # Make prediction
            pred_price = self.model.predict(X_future_scaled)[0]
            predictions.append(pred_price)

            # Calculate confidence interval (simplified approach)
            if hasattr(self.model, 'estimators_'):  # Random Forest
                tree_predictions = [tree.predict(X_future_scaled)[0] for tree in self.model.estimators_]
                std_pred = np.std(tree_predictions)
                confidence_intervals.append((pred_price - 1.96 * std_pred, pred_price + 1.96 * std_pred))
            else:
                # Simple confidence interval for other models
                confidence_intervals.append((pred_price * 0.95, pred_price * 1.05))

            # Update last_data with predicted price for next iteration
            last_data.iloc[0, last_data.columns.get_loc('price')] = pred_price

        return {
            "predictions": predictions,
            "dates": prediction_dates,
            "confidence_intervals": confidence_intervals,
            "prediction_horizon": days
        }

    def get_buy_recommendation(self, predictions: List[float], current_price: float = None) -> Dict:
        """
        Generate buy/wait recommendation based on predictions

        Args:
            predictions: List of predicted prices
            current_price: Current product price

        Returns:
            Recommendation dictionary
        """
        if not predictions:
            return {"recommendation": "INSUFFICIENT_DATA", "reason": "No predictions available"}

        min_price = min(predictions)
        min_price_day = predictions.index(min_price)
        max_price = max(predictions)

        if current_price is None:
            current_price = predictions[0]  # Use first prediction as current

        # Calculate potential savings
        potential_savings = current_price - min_price
        potential_savings_pct = (potential_savings / current_price) * 100

        # Decision logic
        if min_price_day == 0:  # Lowest price is today
            recommendation = "BUY_NOW"
            reason = "Lowest price predicted today!"
            confidence = 0.9
        elif potential_savings_pct > 10:  # Significant savings expected
            recommendation = f"WAIT_{min_price_day}_DAYS"
            reason = f"Price expected to drop by ${potential_savings:.2f} ({potential_savings_pct:.1f}%)"
            confidence = 0.8
        elif potential_savings_pct > 5:  # Moderate savings
            recommendation = f"WAIT_{min_price_day}_DAYS"
            reason = f"Moderate price drop expected: ${potential_savings:.2f} ({potential_savings_pct:.1f}%)"
            confidence = 0.7
        else:  # Small savings
            recommendation = "BUY_NOW"
            reason = "Price is relatively stable, minimal savings expected"
            confidence = 0.6

        return {
            "recommendation": recommendation,
            "reason": reason,
            "confidence": confidence,
            "potential_savings": potential_savings,
            "potential_savings_pct": potential_savings_pct,
            "best_buy_day": min_price_day,
            "price_volatility": max_price - min_price
        }

    def get_feature_importance(self) -> Dict:
        """Get feature importance from trained model"""
        if not self.is_trained or not hasattr(self.model, 'feature_importances_'):
            return {}

        importance_dict = dict(zip(self.feature_names, self.model.feature_importances_))
        # Sort by importance
        sorted_features = sorted(importance_dict.items(), key=lambda x: x[1], reverse=True)

        return dict(sorted_features)

    def save_model(self, filename: str):
        """Save trained model and scaler"""
        if not self.is_trained:
            logger.warning("Cannot save untrained model")
            return

        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_names': self.feature_names,
            'model_type': self.model_type,
            'trained_at': datetime.now()
        }

        filepath = os.path.join(self.model_path, f"{filename}.pkl")
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)

        logger.info(f"Model saved to {filepath}")

    def load_model(self, filename: str) -> bool:
        """Load trained model and scaler"""
        filepath = os.path.join(self.model_path, f"{filename}.pkl")

        if not os.path.exists(filepath):
            logger.error(f"Model file not found: {filepath}")
            return False

        try:
            with open(filepath, 'rb') as f:
                model_data = pickle.load(f)

            self.model = model_data['model']
            self.scaler = model_data['scaler']
            self.feature_names = model_data['feature_names']
            self.model_type = model_data['model_type']
            self.is_trained = True

            logger.info(f"Model loaded from {filepath}")
            return True

        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return False


class TrendAnalyzer:
    """Analyze price trends and patterns"""

    @staticmethod
    def detect_trend(prices: List[float], window: int = 7) -> str:
        """
        Detect overall trend in prices

        Returns: 'UPWARD', 'DOWNWARD', or 'STABLE'
        """
        if len(prices) < window:
            return 'INSUFFICIENT_DATA'

        recent_prices = prices[-window:]

        # Calculate linear regression slope
        x = np.arange(len(recent_prices))
        slope = np.polyfit(x, recent_prices, 1)[0]

        # Determine trend based on slope
        if abs(slope) < 0.01:  # Very small slope
            return 'STABLE'
        elif slope > 0:
            return 'UPWARD'
        else:
            return 'DOWNWARD'

    @staticmethod
    def calculate_volatility(prices: List[float]) -> float:
        """Calculate price volatility (coefficient of variation)"""
        if len(prices) < 2:
            return 0.0

        mean_price = np.mean(prices)
        std_price = np.std(prices)

        return (std_price / mean_price) * 100 if mean_price > 0 else 0.0

    @staticmethod
    def find_support_resistance(prices: List[float]) -> Dict:
        """Find support and resistance levels"""
        if len(prices) < 10:
            return {"support": None, "resistance": None}

        # Simple approach: use quantiles
        support = np.percentile(prices, 25)
        resistance = np.percentile(prices, 75)

        return {
            "support": support,
            "resistance": resistance,
            "current_vs_support": ((prices[-1] - support) / support * 100) if support > 0 else 0,
            "current_vs_resistance": ((prices[-1] - resistance) / resistance * 100) if resistance > 0 else 0
        }


# Example usage
if __name__ == "__main__":
    # Create sample data
    dates = pd.date_range(start='2024-01-01', periods=100, freq='D')
    prices = 100 + np.cumsum(np.random.randn(100) * 2)  # Random walk around 100

    sample_data = pd.DataFrame({
        'timestamp': dates,
        'price': prices
    })

    # Initialize and train model
    predictor = PricePredictor()
    metrics = predictor.train(sample_data)
    print("Training metrics:", metrics)

    # Make predictions
    recent_data = sample_data.tail(30)  # Last 30 days
    predictions = predictor.predict_next_days(recent_data, days=7)
    print("Predictions:", predictions)

    # Get recommendation
    if 'predictions' in predictions:
        recommendation = predictor.get_buy_recommendation(predictions['predictions'])
        print("Recommendation:", recommendation)
