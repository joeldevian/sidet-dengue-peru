# ============================================
# MODELOS DE PREDICCIÓN PROSPECTIVA - SIDET
# ============================================

import numpy as np
import pandas as pd
import warnings
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import pickle

# Machine Learning
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error
import xgboost as xgb

# Series Temporales
from statsmodels.tsa.statespace.sarimax import SARIMAX
from pmdarima import auto_arima
from prophet import Prophet

# Deep Learning
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Reducir logs de TensorFlow
import tensorflow as tf
from tensorflow.keras import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping

warnings.filterwarnings('ignore')


class BaseForecaster:
    """Clase base para todos los modelos de forecasting"""
    
    def __init__(self, name: str):
        self.name = name
        self.model = None
        self.scaler = None
        self.is_fitted = False
        
    def fit(self, data: pd.DataFrame):
        """Entrenar el modelo"""
        raise NotImplementedError
        
    def predict(self, steps: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Predecir valores futuros
        Returns: (predicciones, intervalo_inferior, intervalo_superior)
        """
        raise NotImplementedError
        
    def save(self, filepath: str):
        """Guardar modelo entrenado"""
        with open(filepath, 'wb') as f:
            pickle.dump(self, f)
            
    @staticmethod
    def load(filepath: str):
        """Cargar modelo guardado"""
        with open(filepath, 'rb') as f:
            return pickle.load(f)


class SARIMAForecaster(BaseForecaster):
    """Modelo SARIMA para predicción de series temporales"""
    
    def __init__(self):
        super().__init__('SARIMA')
        self.order = None
        self.seasonal_order = None
        
    def fit(self, data: pd.DataFrame, target_col: str = 'casos'):
        """
        Entrenar modelo SARIMA con auto-selección de parámetros
        
        Args:
            data: DataFrame con columna de fecha y casos
            target_col: Nombre de la columna objetivo
        """
        print(f"[{self.name}] Entrenando modelo...")
        
        # Preparar datos
        y = data[target_col].values
        
        # Auto-ARIMA para encontrar mejores parámetros
        print(f"[{self.name}] Buscando mejores parámetros con Auto-ARIMA...")
        auto_model = auto_arima(
            y,
            seasonal=True,
            m=52,  # Estacionalidad semanal anual
            max_p=3, max_q=3, max_P=2, max_Q=2,
            max_d=2, max_D=1,
            trace=False,
            error_action='ignore',
            suppress_warnings=True,
            stepwise=True
        )
        
        self.order = auto_model.order
        self.seasonal_order = auto_model.seasonal_order
        
        print(f"[{self.name}] Parámetros óptimos: order={self.order}, seasonal_order={self.seasonal_order}")
        
        # Entrenar modelo final
        self.model = SARIMAX(
            y,
            order=self.order,
            seasonal_order=self.seasonal_order,
            enforce_stationarity=False,
            enforce_invertibility=False
        )
        
        self.model = self.model.fit(disp=False)
        self.is_fitted = True
        
        print(f"[{self.name}] Modelo entrenado exitosamente")
        
    def predict(self, steps: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Predecir valores futuros con intervalos de confianza"""
        if not self.is_fitted:
            raise ValueError("Modelo no entrenado. Ejecutar fit() primero.")
            
        # Predicción
        forecast = self.model.get_forecast(steps=steps)
        predictions = forecast.predicted_mean
        
        # Intervalos de confianza (95%)
        conf_int = forecast.conf_int(alpha=0.05)
        lower = conf_int.iloc[:, 0].values
        upper = conf_int.iloc[:, 1].values
        
        # Asegurar que no haya valores negativos
        predictions = np.maximum(predictions, 0)
        lower = np.maximum(lower, 0)
        upper = np.maximum(upper, 0)
        
        return predictions, lower, upper


class ProphetForecaster(BaseForecaster):
    """Modelo Prophet de Facebook para predicción"""
    
    def __init__(self):
        super().__init__('Prophet')
        self.holidays = self._get_peru_holidays()
        
    def _get_peru_holidays(self) -> pd.DataFrame:
        """Obtener días festivos de Perú"""
        holidays = pd.DataFrame({
            'holiday': 'peru_holiday',
            'ds': pd.to_datetime([
                '2024-01-01', '2024-03-28', '2024-03-29', '2024-05-01',
                '2024-06-29', '2024-07-28', '2024-07-29', '2024-08-30',
                '2024-10-08', '2024-11-01', '2024-12-08', '2024-12-25',
                '2025-01-01', '2025-04-17', '2025-04-18', '2025-05-01',
                '2025-06-29', '2025-07-28', '2025-07-29', '2025-08-30',
                '2025-10-08', '2025-11-01', '2025-12-08', '2025-12-25',
                '2026-01-01', '2026-04-02', '2026-04-03', '2026-05-01',
                '2026-06-29', '2026-07-28', '2026-07-29', '2026-08-30',
                '2026-10-08', '2026-11-01', '2026-12-08', '2026-12-25',
            ]),
            'lower_window': 0,
            'upper_window': 1,
        })
        return holidays
        
    def fit(self, data: pd.DataFrame, date_col: str = 'fecha', target_col: str = 'casos'):
        """
        Entrenar modelo Prophet
        
        Args:
            data: DataFrame con columnas de fecha y casos
            date_col: Nombre de la columna de fecha
            target_col: Nombre de la columna objetivo
        """
        print(f"[{self.name}] Entrenando modelo...")
        
        # Preparar datos en formato Prophet (ds, y)
        df_prophet = pd.DataFrame({
            'ds': pd.to_datetime(data[date_col]),
            'y': data[target_col].values
        })
        
        # Crear y entrenar modelo
        self.model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=False,
            seasonality_mode='multiplicative',
            holidays=self.holidays,
            interval_width=0.95
        )
        
        self.model.fit(df_prophet)
        self.is_fitted = True
        
        print(f"[{self.name}] Modelo entrenado exitosamente")
        
    def predict(self, steps: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Predecir valores futuros con intervalos de confianza"""
        if not self.is_fitted:
            raise ValueError("Modelo no entrenado. Ejecutar fit() primero.")
            
        # Crear dataframe de fechas futuras
        future = self.model.make_future_dataframe(periods=steps, freq='W')
        
        # Predicción
        forecast = self.model.predict(future)
        
        # Obtener solo las predicciones futuras
        predictions = forecast['yhat'].values[-steps:]
        lower = forecast['yhat_lower'].values[-steps:]
        upper = forecast['yhat_upper'].values[-steps:]
        
        # Asegurar que no haya valores negativos
        predictions = np.maximum(predictions, 0)
        lower = np.maximum(lower, 0)
        upper = np.maximum(upper, 0)
        
        return predictions, lower, upper




class LSTMForecaster(BaseForecaster):
    """Modelo LSTM (Deep Learning) para predicción"""
    
    def __init__(self, lookback: int = 52):
        super().__init__('LSTM')
        self.lookback = lookback  # Ventana de observación (52 semanas = 1 año)
        self.scaler = MinMaxScaler()
        
    def _create_sequences(self, data: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Crear secuencias para LSTM"""
        X, y = [], []
        for i in range(len(data) - self.lookback):
            X.append(data[i:i + self.lookback])
            y.append(data[i + self.lookback])
        return np.array(X), np.array(y)
        
    def fit(self, data: pd.DataFrame, target_col: str = 'casos', epochs: int = 30):
        """
        Entrenar modelo LSTM
        
        Args:
            data: DataFrame con casos
            target_col: Nombre de la columna objetivo
            epochs: Número de épocas de entrenamiento (reducido a 30 por defecto)
        """
        print(f"[{self.name}] Entrenando modelo...")
        
        # Preparar datos
        values = data[target_col].values.reshape(-1, 1)
        scaled_data = self.scaler.fit_transform(values)
        
        # Crear secuencias
        X, y = self._create_sequences(scaled_data)
        X = X.reshape((X.shape[0], X.shape[1], 1))
        
        print(f"[{self.name}] Secuencias creadas: {X.shape[0]} muestras")
        
        # Crear modelo
        self.model = Sequential([
            LSTM(50, activation='relu', return_sequences=True, input_shape=(self.lookback, 1)),
            Dropout(0.2),
            LSTM(50, activation='relu'),
            Dropout(0.2),
            Dense(1)
        ])
        
        self.model.compile(optimizer='adam', loss='mse', metrics=['mae'])
        
        # Early stopping más agresivo para reducir tiempo de entrenamiento
        early_stop = EarlyStopping(
            monitor='loss', 
            patience=3,  # Reducido de 5 a 3
            restore_best_weights=True,
            verbose=1
        )
        
        print(f"[{self.name}] Entrenando red neuronal (máx {epochs} épocas)...")
        history = self.model.fit(
            X, y,
            epochs=epochs,
            batch_size=32,
            verbose=0,
            callbacks=[early_stop]
        )
        
        print(f"[{self.name}] Entrenamiento completado en {len(history.history['loss'])} épocas")
        
        # Guardar última secuencia para predicciones
        self.last_sequence = scaled_data[-self.lookback:]
        self.is_fitted = True
        
        print(f"[{self.name}] Modelo entrenado exitosamente")
        
    def predict(self, steps: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Predecir valores futuros"""
        if not self.is_fitted:
            raise ValueError("Modelo no entrenado. Ejecutar fit() primero.")
            
        predictions = []
        current_sequence = self.last_sequence.copy()
        
        # Predicción iterativa
        for _ in range(steps):
            # Preparar input
            X_input = current_sequence.reshape((1, self.lookback, 1))
            
            # Predecir
            pred_scaled = self.model.predict(X_input, verbose=0)
            
            # Actualizar secuencia
            current_sequence = np.append(current_sequence[1:], pred_scaled, axis=0)
            predictions.append(pred_scaled[0, 0])
        
        # Desescalar predicciones
        predictions = np.array(predictions).reshape(-1, 1)
        predictions = self.scaler.inverse_transform(predictions).flatten()
        
        # Intervalos de confianza (estimados como ±15%)
        lower = predictions * 0.85
        upper = predictions * 1.15
        
        # Asegurar que no haya valores negativos
        predictions = np.maximum(predictions, 0)
        lower = np.maximum(lower, 0)
        upper = np.maximum(upper, 0)
        
        return predictions, lower, upper




class XGBoostForecaster(BaseForecaster):
    """Modelo XGBoost para predicción con features engineered"""
    
    def __init__(self, lookback: int = 52):
        super().__init__('XGBoost')
        self.lookback = lookback
        self.feature_columns = []
        
    def _create_features(self, data: pd.DataFrame, target_col: str = 'casos') -> pd.DataFrame:
        """Crear features para XGBoost"""
        df = data.copy()
        
        # Lags
        for lag in [1, 2, 4, 8, 12, 26, 52]:
            df[f'lag_{lag}'] = df[target_col].shift(lag)
        
        # Rolling statistics
        for window in [4, 12, 26, 52]:
            df[f'rolling_mean_{window}'] = df[target_col].rolling(window=window).mean()
            df[f'rolling_std_{window}'] = df[target_col].rolling(window=window).std()
        
        # Features temporales
        if 'fecha' in df.columns:
            df['fecha'] = pd.to_datetime(df['fecha'])
            df['semana_año'] = df['fecha'].dt.isocalendar().week
            df['mes'] = df['fecha'].dt.month
            df['trimestre'] = df['fecha'].dt.quarter
        
        # Tendencia
        df['tendencia'] = np.arange(len(df))
        
        return df
        
    def fit(self, data: pd.DataFrame, target_col: str = 'casos'):
        """
        Entrenar modelo XGBoost
        
        Args:
            data: DataFrame con casos y fecha
            target_col: Nombre de la columna objetivo
        """
        print(f"[{self.name}] Entrenando modelo...")
        
        # Crear features
        df_features = self._create_features(data, target_col)
        
        # Eliminar filas con NaN
        df_features = df_features.dropna()
        
        # Separar features y target
        self.feature_columns = [col for col in df_features.columns 
                                if col not in [target_col, 'fecha', 'departamento']]
        
        X = df_features[self.feature_columns]
        y = df_features[target_col]
        
        # Entrenar modelo
        self.model = xgb.XGBRegressor(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            random_state=42,
            objective='reg:squarederror'
        )
        
        self.model.fit(X, y, verbose=False)
        
        # Guardar últimos datos para predicciones
        self.last_data = data.copy()
        self.is_fitted = True
        
        print(f"[{self.name}] Modelo entrenado exitosamente")
        
    def predict(self, steps: int, target_col: str = 'casos') -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Predecir valores futuros"""
        if not self.is_fitted:
            raise ValueError("Modelo no entrenado. Ejecutar fit() primero.")
            
        predictions = []
        df_extended = self.last_data.copy()
        
        # Predicción iterativa
        for i in range(steps):
            # Crear features
            df_features = self._create_features(df_extended, target_col)
            df_features = df_features.dropna()
            
            # Obtener última fila
            X_input = df_features[self.feature_columns].iloc[[-1]]
            
            # Predecir
            pred = self.model.predict(X_input)[0]
            
            # Añadir predicción al dataframe
            new_row = df_extended.iloc[[-1]].copy()
            new_row[target_col] = pred
            if 'fecha' in new_row.columns:
                new_row['fecha'] = pd.to_datetime(new_row['fecha'].values[0]) + timedelta(weeks=1)
            
            df_extended = pd.concat([df_extended, new_row], ignore_index=True)
            predictions.append(pred)
        
        predictions = np.array(predictions)
        
        # Intervalos de confianza (estimados como ±20%)
        lower = predictions * 0.80
        upper = predictions * 1.20
        
        # Asegurar que no haya valores negativos
        predictions = np.maximum(predictions, 0)
        lower = np.maximum(lower, 0)
        upper = np.maximum(upper, 0)
        
        return predictions, lower, upper


class EnsembleForecaster:
    """Sistema de ensamble que combina múltiples modelos"""
    
    def __init__(self, weights: Dict[str, float] = None):
        """
        Args:
            weights: Diccionario con pesos para cada modelo
                    Ejemplo: {'sarima': 0.25, 'prophet': 0.30, 'lstm': 0.25, 'xgboost': 0.20}
        """
        self.models = {}
        self.weights = weights or {
            'sarima': 0.25,
            'prophet': 0.30,
            'lstm': 0.25,
            'xgboost': 0.20
        }
        
    def add_model(self, name: str, model: BaseForecaster):
        """Añadir modelo al ensamble"""
        self.models[name] = model
        
    def predict(self, steps: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Predecir usando ensamble de modelos
        
        Returns:
            (predicciones_ensamble, intervalo_inferior, intervalo_superior)
        """
        if not self.models:
            raise ValueError("No hay modelos en el ensamble")
            
        all_predictions = []
        all_lower = []
        all_upper = []
        
        # Obtener predicciones de cada modelo
        for name, model in self.models.items():
            if model.is_fitted:
                pred, lower, upper = model.predict(steps)
                weight = self.weights.get(name, 1.0 / len(self.models))
                
                all_predictions.append(pred * weight)
                all_lower.append(lower * weight)
                all_upper.append(upper * weight)
        
        # Combinar predicciones
        ensemble_pred = np.sum(all_predictions, axis=0)
        ensemble_lower = np.sum(all_lower, axis=0)
        ensemble_upper = np.sum(all_upper, axis=0)
        
        return ensemble_pred, ensemble_lower, ensemble_upper
    
    def get_individual_predictions(self, steps: int) -> Dict[str, Tuple[np.ndarray, np.ndarray, np.ndarray]]:
        """Obtener predicciones individuales de cada modelo"""
        predictions = {}
        
        for name, model in self.models.items():
            if model.is_fitted:
                predictions[name] = model.predict(steps)
                
        return predictions
