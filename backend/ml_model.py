import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from datetime import datetime, timedelta
import joblib
import warnings
warnings.filterwarnings('ignore')

class MLModels:
    def __init__(self):
        self.xgboost_model = None
        self.random_forest_model = None
        self.feature_importance = None
        
    def prepare_feature_data(self, df):
        features = ['price', 'ram', 'storage', 'battery', 'camera_mp']
        X = df[features]
        y = df['units_sold']
        return X, y
    
    def train_regression_models(self, df):
        X, y = self.prepare_feature_data(df)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Train XGBoost
        self.xgboost_model = XGBRegressor(n_estimators=100, learning_rate=0.1, random_state=42)
        self.xgboost_model.fit(X_train, y_train)
        
        # Train Random Forest
        self.random_forest_model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.random_forest_model.fit(X_train, y_train)
        
        # Get feature importance
        self.feature_importance = pd.DataFrame({
            'feature': X.columns,
            'importance': self.xgboost_model.feature_importances_
        })
        
        # Evaluate models
        xgb_pred = self.xgboost_model.predict(X_test)
        rf_pred = self.random_forest_model.predict(X_test)
        
        metrics = {
            'xgboost': {
                'mae': mean_absolute_error(y_test, xgb_pred),
                'rmse': np.sqrt(mean_squared_error(y_test, xgb_pred)),
                'r2': r2_score(y_test, xgb_pred)
            },
            'random_forest': {
                'mae': mean_absolute_error(y_test, rf_pred),
                'rmse': np.sqrt(mean_squared_error(y_test, rf_pred)),
                'r2': r2_score(y_test, rf_pred)
            }
        }
        
        return metrics
    
    def predict_sales(self, features, model_name='xgboost'):
        if model_name == 'xgboost' and self.xgboost_model:
            return self.xgboost_model.predict([features])[0]
        elif model_name == 'random_forest' and self.random_forest_model:
            return self.random_forest_model.predict([features])[0]
        return 0
    
    def simple_time_series_forecast(self, df, periods=6):
        """Simple time series forecast using moving average"""
        if len(df) > 0:
            last_values = df['units_sold'].values[-3:]
            avg = np.mean(last_values)
            trend = np.polyfit(range(len(df)), df['units_sold'].values, 1)[0]
            
            forecasts = []
            for i in range(periods):
                next_val = avg + (trend * (i + 1))
                forecasts.append(max(0, next_val))
            
            return forecasts
        return [0] * periods
    
    def hybrid_prediction(self, features, time_series_weight=0.3, regression_weight=0.7):
        regression_pred = self.predict_sales(features)
        time_series_pred = regression_pred * 1.1  # Simple adjustment
        
        hybrid_pred = (regression_weight * regression_pred) + (time_series_weight * time_series_pred)
        return hybrid_pred