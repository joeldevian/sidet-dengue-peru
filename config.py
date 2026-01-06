# ============================================
# CONFIGURACIÓN GENERAL DEL PROYECTO SIDET
# Sistema Inteligente de Detección Temprana de Dengue
# ============================================

import os
from pathlib import Path

# Rutas del proyecto
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / 'data'
RAW_DATA_DIR = DATA_DIR / 'raw'
PROCESSED_DATA_DIR = DATA_DIR / 'processed'
EXTERNAL_DATA_DIR = DATA_DIR / 'external'
REPORTS_DIR = BASE_DIR / 'reports'
FIGURES_DIR = REPORTS_DIR / 'figures'

# Regiones endémicas objetivo
REGIONES_OBJETIVO = [
    'LORETO',
    'PIURA',
    'UCAYALI',
    'SAN MARTIN',
    'JUNIN'
]

# URLs de datasets
DATASET_URLS = {
    'principal': 'https://www.datosabiertos.gob.pe/sites/default/files/datos_abiertos_vigilancia_dengue_2000_2024.csv',
    'piura': 'https://www.datosabiertos.gob.pe/dataset/casos-de-dengue-en-la-región-piura-gobierno-regional-piura'
}

# Parámetros de análisis
PERIODO_ANALISIS = {
    'año_inicio': 2000,
    'año_fin': 2024
}

# Parámetros de modelos
RANDOM_STATE = 42
TEST_SIZE = 0.2

# Umbrales de alerta
UMBRALES_ALERTA = {
    'bajo': 1.5,      # 1.5 desviaciones estándar
    'medio': 2.0,     # 2.0 desviaciones estándar
    'alto': 2.5,      # 2.5 desviaciones estándar
    'critico': 3.0    # 3.0 desviaciones estándar
}

# Configuración de visualización
PLOT_CONFIG = {
    'figsize': (14, 8),
    'dpi': 100,
    'style': 'seaborn-v0_8-darkgrid'
}

# Colores por nivel de alerta
COLORES_ALERTA = {
    'normal': '#2ecc71',
    'bajo': '#f1c40f',
    'medio': '#e67e22',
    'alto': '#e74c3c',
    'critico': '#8e44ad'
}

# ============================================
# CONFIGURACIÓN DE PREDICCIÓN PROSPECTIVA
# ============================================

# Parámetros de predicción
FORECASTING_CONFIG = {
    'horizonte_prediccion': 156,  # 3 años en semanas (52 * 3)
    'año_inicio_prediccion': 2026,
    'año_fin_prediccion': 2028,
    'intervalo_confianza': [0.80, 0.95],
    'modelos_activos': ['sarima', 'prophet', 'lstm', 'xgboost']
}

# Pesos para ensamble de modelos (deben sumar 1.0)
ENSEMBLE_WEIGHTS = {
    'sarima': 0.25,
    'prophet': 0.30,
    'lstm': 0.25,
    'xgboost': 0.20
}

# Rutas de modelos de forecasting
FORECASTING_MODELS_DIR = BASE_DIR / 'models' / 'saved' / 'forecasting'
PREDICTIONS_DIR = PROCESSED_DATA_DIR / 'predictions'

# Parámetros para backtesting
BACKTESTING_CONFIG = {
    'test_years': 2,  # Últimos 2 años para validación
    'train_start_year': 2000,
    'metrics': ['mae', 'rmse', 'mape']
}

# Niveles de alerta predictiva
UMBRALES_ALERTA_PREDICTIVA = {
    'normal': 0.10,        # <10% incremento esperado
    'vigilancia': 0.30,    # 10-30% incremento
    'preparacion': 0.60,   # 30-60% incremento
    'alerta_temprana': 1.0, # 60-100% incremento
    'critico': float('inf') # >100% incremento
}

# Colores para alertas predictivas
COLORES_ALERTA_PREDICTIVA = {
    'normal': '#27ae60',
    'vigilancia': '#f39c12',
    'preparacion': '#e67e22',
    'alerta_temprana': '#e74c3c',
    'critico': '#9b59b6'
}
