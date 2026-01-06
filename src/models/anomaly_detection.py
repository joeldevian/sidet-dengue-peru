"""
Módulo de modelos de detección de anomalías para dengue
Implementa diferentes algoritmos de ML para detectar brotes anómalos
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from sklearn.svm import OneClassSVM
from sklearn.preprocessing import StandardScaler
from typing import Dict, List, Tuple
import logging
import joblib
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AnomalyDetector:
    """Clase para detección de anomalías en casos de dengue"""
    
    def __init__(self, contamination=0.1):
        """
        Inicializa el detector de anomalías
        
        Args:
            contamination: Proporción esperada de anomalías (0.1 = 10%)
        """
        self.contamination = contamination
        self.models = {}
        self.scalers = {}
        self.feature_columns = None
        
    def preparar_datos(self, df: pd.DataFrame, feature_cols: List[str],
                      target_col: str = 'casos') -> Tuple[pd.DataFrame, np.ndarray]:
        """
        Prepara los datos para entrenamiento
        
        Args:
            df: DataFrame con features
            feature_cols: Lista de columnas de features
            target_col: Columna objetivo
            
        Returns:
            DataFrame y array de features
        """
        logger.info(f"Preparando datos con {len(feature_cols)} features...")
        
        # Eliminar filas con NaN
        df_clean = df[feature_cols + [target_col]].dropna()
        
        # Extraer features
        X = df_clean[feature_cols].values
        
        logger.info(f"✓ Datos preparados: {len(df_clean):,} registros")
        
        return df_clean, X
    
    def entrenar_isolation_forest(self, X: np.ndarray, region: str) -> IsolationForest:
        """
        Entrena modelo Isolation Forest
        
        Args:
            X: Array de features
            region: Nombre de la región
            
        Returns:
            Modelo entrenado
        """
        logger.info(f"Entrenando Isolation Forest para {region}...")
        
        # Escalar datos
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Entrenar modelo
        model = IsolationForest(
            contamination=self.contamination,
            random_state=42,
            n_estimators=100,
            max_samples='auto',
            n_jobs=-1
        )
        model.fit(X_scaled)
        
        # Guardar scaler y modelo
        self.scalers[f'if_{region}'] = scaler
        self.models[f'if_{region}'] = model
        
        logger.info(f"✓ Isolation Forest entrenado para {region}")
        
        return model
    
    def entrenar_lof(self, X: np.ndarray, region: str) -> LocalOutlierFactor:
        """
        Entrena modelo Local Outlier Factor
        
        Args:
            X: Array de features
            region: Nombre de la región
            
        Returns:
            Modelo entrenado
        """
        logger.info(f"Entrenando LOF para {region}...")
        
        # Escalar datos
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Entrenar modelo
        model = LocalOutlierFactor(
            contamination=self.contamination,
            n_neighbors=20,
            novelty=True,  # Para poder predecir nuevos datos
            n_jobs=-1
        )
        model.fit(X_scaled)
        
        # Guardar scaler y modelo
        self.scalers[f'lof_{region}'] = scaler
        self.models[f'lof_{region}'] = model
        
        logger.info(f"✓ LOF entrenado para {region}")
        
        return model
    
    def entrenar_ocsvm(self, X: np.ndarray, region: str) -> OneClassSVM:
        """
        Entrena modelo One-Class SVM
        
        Args:
            X: Array de features
            region: Nombre de la región
            
        Returns:
            Modelo entrenado
        """
        logger.info(f"Entrenando One-Class SVM para {region}...")
        
        # Escalar datos
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Entrenar modelo
        model = OneClassSVM(
            nu=self.contamination,  # nu es similar a contamination
            kernel='rbf',
            gamma='auto'
        )
        model.fit(X_scaled)
        
        # Guardar scaler y modelo
        self.scalers[f'ocsvm_{region}'] = scaler
        self.models[f'ocsvm_{region}'] = model
        
        logger.info(f"✓ One-Class SVM entrenado para {region}")
        
        return model
    
    def detectar_anomalias(self, df: pd.DataFrame, feature_cols: List[str],
                          region: str, col_departamento: str = 'departamento') -> pd.DataFrame:
        """
        Detecta anomalías usando los modelos entrenados
        
        Args:
            df: DataFrame con datos
            feature_cols: Columnas de features
            region: Región a analizar
            col_departamento: Columna de departamento
            
        Returns:
            DataFrame con predicciones de anomalías
        """
        logger.info(f"Detectando anomalías para {region}...")
        
        # Filtrar por región
        df_region = df[df[col_departamento] == region].copy()
        
        # Verificar que las features existen
        features_disponibles = [col for col in feature_cols if col in df_region.columns]
        
        # Eliminar filas con NaN en features
        df_clean = df_region.dropna(subset=features_disponibles).copy()
        
        # Extraer features para predicción
        X = df_clean[features_disponibles].values
        
        logger.info(f"Datos preparados: {len(df_clean):,} registros con {len(features_disponibles)} features")
        
        # Predecir con cada modelo
        for model_type in ['if', 'lof', 'ocsvm']:
            model_key = f'{model_type}_{region}'
            
            if model_key in self.models:
                # Escalar datos
                X_scaled = self.scalers[model_key].transform(X)
                
                # Predecir (-1 = anomalía, 1 = normal)
                predictions = self.models[model_key].predict(X_scaled)
                
                # Convertir a binario (1 = anomalía, 0 = normal)
                df_clean[f'anomalia_{model_type}'] = (predictions == -1).astype(int)
                
                # Obtener scores
                if model_type == 'if':
                    scores = self.models[model_key].score_samples(X_scaled)
                    df_clean[f'score_{model_type}'] = scores
        
        # Crear consenso de anomalías (al menos 2 de 3 modelos)
        anomaly_cols = [f'anomalia_{mt}' for mt in ['if', 'lof', 'ocsvm']]
        df_clean['anomalia_consenso'] = (df_clean[anomaly_cols].sum(axis=1) >= 2).astype(int)
        
        logger.info(f"✓ Anomalías detectadas: {df_clean['anomalia_consenso'].sum():,}")
        
        return df_clean
    
    def entrenar_todos_modelos(self, df: pd.DataFrame, feature_cols: List[str],
                               regiones: List[str], col_departamento: str = 'departamento'):
        """
        Entrena todos los modelos para todas las regiones
        
        Args:
            df: DataFrame con features
            feature_cols: Columnas de features
            regiones: Lista de regiones
            col_departamento: Columna de departamento
        """
        logger.info("=" * 70)
        logger.info("ENTRENANDO MODELOS DE DETECCIÓN DE ANOMALÍAS")
        logger.info("=" * 70)
        
        self.feature_columns = feature_cols
        
        for region in regiones:
            logger.info(f"\n--- Región: {region} ---")
            
            # Filtrar datos de la región
            df_region = df[df[col_departamento] == region]
            df_clean, X = self.preparar_datos(df_region, feature_cols)
            
            # Entrenar los 3 modelos
            self.entrenar_isolation_forest(X, region)
            self.entrenar_lof(X, region)
            self.entrenar_ocsvm(X, region)
        
        logger.info("\n" + "=" * 70)
        logger.info(f"✓ ENTRENAMIENTO COMPLETADO")
        logger.info(f"  Total de modelos entrenados: {len(self.models)}")
        logger.info("=" * 70)
    
    def guardar_modelos(self, output_dir: Path):
        """
        Guarda los modelos entrenados
        
        Args:
            output_dir: Directorio de salida
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Guardar modelos
        models_path = output_dir / 'anomaly_models.pkl'
        joblib.dump(self.models, models_path)
        
        # Guardar scalers
        scalers_path = output_dir / 'anomaly_scalers.pkl'
        joblib.dump(self.scalers, scalers_path)
        
        # Guardar feature columns
        features_path = output_dir / 'feature_columns.pkl'
        joblib.dump(self.feature_columns, features_path)
        
        logger.info(f"✓ Modelos guardados en: {output_dir}")
    
    def cargar_modelos(self, input_dir: Path):
        """
        Carga modelos previamente entrenados
        
        Args:
            input_dir: Directorio con modelos
        """
        models_path = input_dir / 'anomaly_models.pkl'
        scalers_path = input_dir / 'anomaly_scalers.pkl'
        features_path = input_dir / 'feature_columns.pkl'
        
        self.models = joblib.load(models_path)
        self.scalers = joblib.load(scalers_path)
        self.feature_columns = joblib.load(features_path)
        
        logger.info(f"✓ Modelos cargados desde: {input_dir}")
