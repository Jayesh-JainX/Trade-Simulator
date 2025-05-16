import numpy as np
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from utils.logger import logger

class SlippageModel:
    def __init__(self):
        self.linear_model = LinearRegression()
        self.quantile_model = GradientBoostingRegressor(loss='quantile', alpha=0.95)
        self.scaler = StandardScaler()
        self.is_fitted = False

    def prepare_features(self, orderbook_data, volume):
        """
        Prepare features from orderbook data for slippage prediction
        """
        try:
            # Extract relevant features from orderbook
            bid_prices = np.array([float(price) for price, _ in orderbook_data['bids']])
            ask_prices = np.array([float(price) for price, _ in orderbook_data['asks']])
            bid_volumes = np.array([float(vol) for _, vol in orderbook_data['bids']])
            ask_volumes = np.array([float(vol) for _, vol in orderbook_data['asks']])

            # Calculate features
            spread = ask_prices[0] - bid_prices[0]
            mid_price = (ask_prices[0] + bid_prices[0]) / 2
            depth_imbalance = np.sum(bid_volumes[:5]) / (np.sum(bid_volumes[:5]) + np.sum(ask_volumes[:5]))
            price_impact = spread / mid_price

            features = np.array([
                volume,
                spread,
                depth_imbalance,
                price_impact,
                np.sum(bid_volumes[:5]),
                np.sum(ask_volumes[:5])
            ]).reshape(1, -1)

            return features

        except Exception as e:
            logger.error(f"Error preparing features: {e}")
            return None

    def fit(self, features, target):
        """
        Fit both linear and quantile regression models
        """
        try:
            # Split data for training and validation
            X_train, X_val, y_train, y_val = train_test_split(features, target, test_size=0.2)

            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_val_scaled = self.scaler.transform(X_val)

            # Fit models
            self.linear_model.fit(X_train_scaled, y_train)
            self.quantile_model.fit(X_train_scaled, y_train)

            # Validate models
            linear_score = self.linear_model.score(X_val_scaled, y_val)
            logger.info(f"Linear model R2 score: {linear_score:.4f}")

            self.is_fitted = True

        except Exception as e:
            logger.error(f"Error fitting slippage models: {e}")

    def predict(self, features):
        """
        Make predictions using both models
        """
        try:
            if not self.is_fitted:
                logger.warning("Models not fitted yet, returning default values")
                return np.zeros(len(features))

            # Scale features
            features_scaled = self.scaler.transform(features)

            # Get predictions from both models
            linear_pred = self.linear_model.predict(features_scaled)
            quantile_pred = self.quantile_model.predict(features_scaled)

            # Combine predictions (use quantile for risk management)
            final_pred = np.maximum(linear_pred, quantile_pred)

            return final_pred

        except Exception as e:
            logger.error(f"Error making slippage predictions: {e}")
            return np.zeros(len(features))

class MakerTakerModel:
    def __init__(self):
        self.model = LogisticRegression()
        self.scaler = StandardScaler()
        self.is_fitted = False

    def fit(self, features, target):
        try:
            # Scale features
            features_scaled = self.scaler.fit_transform(features)
            self.model.fit(features_scaled, target)
            self.is_fitted = True

        except Exception as e:
            logger.error(f"Error fitting maker/taker model: {e}")

    def predict_proba(self, features):
        try:
            if not self.is_fitted:
                logger.warning("Model not fitted yet, returning default values")
                return np.array([[0.5, 0.5]])

            features_scaled = self.scaler.transform(features)
            return self.model.predict_proba(features_scaled)

        except Exception as e:
            logger.error(f"Error predicting maker/taker probabilities: {e}")
            return np.array([[0.5, 0.5]])

# Create global instances
slippage_model = SlippageModel()
maker_taker_model = MakerTakerModel()

def estimate_slippage(features, target=None):
    """
    Wrapper function for slippage estimation
    """
    if target is not None:
        slippage_model.fit(features, target)
    return slippage_model

def maker_taker_ratio(features, target=None):
    """
    Wrapper function for maker/taker prediction
    """
    if target is not None:
        maker_taker_model.fit(features, target)
    return maker_taker_model
