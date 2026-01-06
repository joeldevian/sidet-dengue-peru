"""
Módulo de ingeniería de características para datos de dengue
Funciones para crear features derivadas y transformaciones
"""

import pandas as pd
import numpy as np
from typing import List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DengueFeatureEngineer:
    """Clase para ingeniería de características de datos de dengue"""
    
    def __init__(self):
        """Inicializa el ingeniero de características"""
        pass
    
    def crear_features_temporales(self, df: pd.DataFrame, col_fecha: str = 'fecha') -> pd.DataFrame:
        """
        Crea características temporales a partir de la fecha
        
        Args:
            df: DataFrame con datos
            col_fecha: Columna de fecha
            
        Returns:
            DataFrame con features temporales agregadas
        """
        logger.info("Creando características temporales...")
        
        df_copy = df.copy()
        df_copy[col_fecha] = pd.to_datetime(df_copy[col_fecha])
        
        # Características temporales básicas
        df_copy['año'] = df_copy[col_fecha].dt.year
        df_copy['mes'] = df_copy[col_fecha].dt.month
        df_copy['trimestre'] = df_copy[col_fecha].dt.quarter
        df_copy['semana_año'] = df_copy[col_fecha].dt.isocalendar().week
        df_copy['dia_año'] = df_copy[col_fecha].dt.dayofyear
        
        # Características cíclicas (para capturar estacionalidad)
        df_copy['mes_sin'] = np.sin(2 * np.pi * df_copy['mes'] / 12)
        df_copy['mes_cos'] = np.cos(2 * np.pi * df_copy['mes'] / 12)
        df_copy['semana_sin'] = np.sin(2 * np.pi * df_copy['semana_año'] / 52)
        df_copy['semana_cos'] = np.cos(2 * np.pi * df_copy['semana_año'] / 52)
        
        logger.info(f"✓ Creadas {8} características temporales")
        
        return df_copy
    
    def crear_features_lag(self, df: pd.DataFrame, col_casos: str = 'casos',
                          lags: List[int] = [1, 2, 4, 8, 12],
                          col_departamento: str = 'departamento') -> pd.DataFrame:
        """
        Crea características de lag (valores pasados)
        
        Args:
            df: DataFrame con datos
            col_casos: Columna de casos
            lags: Lista de lags a crear
            col_departamento: Columna de departamento
            
        Returns:
            DataFrame con features de lag
        """
        logger.info(f"Creando características de lag: {lags}")
        
        df_copy = df.copy()
        
        # Crear lags por región
        for lag in lags:
            df_copy[f'casos_lag_{lag}'] = df_copy.groupby(col_departamento)[col_casos].shift(lag)
        
        logger.info(f"✓ Creadas {len(lags)} características de lag")
        
        return df_copy
    
    def crear_features_rolling(self, df: pd.DataFrame, col_casos: str = 'casos',
                              windows: List[int] = [4, 8, 12, 26],
                              col_departamento: str = 'departamento') -> pd.DataFrame:
        """
        Crea características de ventanas móviles (rolling)
        
        Args:
            df: DataFrame con datos
            col_casos: Columna de casos
            windows: Lista de tamaños de ventana
            col_departamento: Columna de departamento
            
        Returns:
            DataFrame con features rolling
        """
        logger.info(f"Creando características rolling: {windows}")
        
        df_copy = df.copy()
        
        # Crear rolling features por región
        for window in windows:
            # Media móvil
            df_copy[f'casos_ma_{window}'] = df_copy.groupby(col_departamento)[col_casos].transform(
                lambda x: x.rolling(window=window, min_periods=1).mean()
            )
            
            # Desviación estándar móvil
            df_copy[f'casos_std_{window}'] = df_copy.groupby(col_departamento)[col_casos].transform(
                lambda x: x.rolling(window=window, min_periods=1).std()
            )
            
            # Máximo móvil
            df_copy[f'casos_max_{window}'] = df_copy.groupby(col_departamento)[col_casos].transform(
                lambda x: x.rolling(window=window, min_periods=1).max()
            )
        
        logger.info(f"✓ Creadas {len(windows) * 3} características rolling")
        
        return df_copy
    
    def crear_features_diferencias(self, df: pd.DataFrame, col_casos: str = 'casos',
                                   periods: List[int] = [1, 4, 52],
                                   col_departamento: str = 'departamento') -> pd.DataFrame:
        """
        Crea características de diferencias (cambios)
        
        Args:
            df: DataFrame con datos
            col_casos: Columna de casos
            periods: Lista de períodos para diferencias
            col_departamento: Columna de departamento
            
        Returns:
            DataFrame con features de diferencias
        """
        logger.info(f"Creando características de diferencias: {periods}")
        
        df_copy = df.copy()
        
        # Crear diferencias por región
        for period in periods:
            df_copy[f'casos_diff_{period}'] = df_copy.groupby(col_departamento)[col_casos].diff(period)
            df_copy[f'casos_pct_change_{period}'] = df_copy.groupby(col_departamento)[col_casos].pct_change(period)
        
        logger.info(f"✓ Creadas {len(periods) * 2} características de diferencias")
        
        return df_copy
    
    def crear_features_estadisticas(self, df: pd.DataFrame, col_casos: str = 'casos',
                                    col_departamento: str = 'departamento') -> pd.DataFrame:
        """
        Crea características estadísticas por región
        
        Args:
            df: DataFrame con datos
            col_casos: Columna de casos
            col_departamento: Columna de departamento
            
        Returns:
            DataFrame con features estadísticas
        """
        logger.info("Creando características estadísticas...")
        
        df_copy = df.copy()
        
        # Estadísticas por región
        stats = df_copy.groupby(col_departamento)[col_casos].agg([
            ('casos_media_region', 'mean'),
            ('casos_std_region', 'std'),
            ('casos_max_region', 'max'),
            ('casos_min_region', 'min')
        ]).reset_index()
        
        # Merge con el dataframe original
        df_copy = df_copy.merge(stats, on=col_departamento, how='left')
        
        # Crear ratio respecto a la media regional
        df_copy['casos_ratio_media'] = df_copy[col_casos] / df_copy['casos_media_region']
        
        # Z-score por región
        df_copy['casos_zscore'] = (df_copy[col_casos] - df_copy['casos_media_region']) / df_copy['casos_std_region']
        
        logger.info("✓ Creadas 6 características estadísticas")
        
        return df_copy
    
    def crear_todas_features(self, df: pd.DataFrame, col_fecha: str = 'fecha',
                            col_casos: str = 'casos', col_departamento: str = 'departamento') -> pd.DataFrame:
        """
        Crea todas las características de una vez
        
        Args:
            df: DataFrame con datos
            col_fecha: Columna de fecha
            col_casos: Columna de casos
            col_departamento: Columna de departamento
            
        Returns:
            DataFrame con todas las features
        """
        logger.info("=" * 70)
        logger.info("CREANDO TODAS LAS CARACTERÍSTICAS")
        logger.info("=" * 70)
        
        df_features = df.copy()
        
        # 1. Features temporales
        df_features = self.crear_features_temporales(df_features, col_fecha)
        
        # 2. Features de lag
        df_features = self.crear_features_lag(df_features, col_casos, col_departamento=col_departamento)
        
        # 3. Features rolling
        df_features = self.crear_features_rolling(df_features, col_casos, col_departamento=col_departamento)
        
        # 4. Features de diferencias
        df_features = self.crear_features_diferencias(df_features, col_casos, col_departamento=col_departamento)
        
        # 5. Features estadísticas
        df_features = self.crear_features_estadisticas(df_features, col_casos, col_departamento=col_departamento)
        
        # Eliminar filas con NaN en features críticos (debido a lags y rolling)
        features_iniciales = len(df_features)
        df_features = df_features.dropna(subset=[f'casos_lag_{lag}' for lag in [1, 2, 4]])
        features_finales = len(df_features)
        
        logger.info("=" * 70)
        logger.info(f"✓ PROCESO COMPLETADO")
        logger.info(f"  Registros iniciales: {features_iniciales:,}")
        logger.info(f"  Registros finales: {features_finales:,}")
        logger.info(f"  Total de columnas: {len(df_features.columns)}")
        logger.info(f"  Features creadas: {len(df_features.columns) - len(df.columns)}")
        logger.info("=" * 70)
        
        return df_features
