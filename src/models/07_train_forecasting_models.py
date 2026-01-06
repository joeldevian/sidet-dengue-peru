# ============================================
# SCRIPT DE ENTRENAMIENTO DE MODELOS DE FORECASTING
# ============================================

import sys
from pathlib import Path

# Añadir directorio raíz al path
sys.path.append(str(Path(__file__).parent.parent.parent))

import pandas as pd
import numpy as np
from datetime import datetime
import pickle

from config import (
    PROCESSED_DATA_DIR,
    FORECASTING_MODELS_DIR,
    REGIONES_OBJETIVO,
    FORECASTING_CONFIG,
    ENSEMBLE_WEIGHTS
)

from src.models.forecasting_models import (
    SARIMAForecaster,
    ProphetForecaster,
    LSTMForecaster,
    XGBoostForecaster,
    EnsembleForecaster
)


def load_data():
    """Cargar datos semanales procesados"""
    print("\n" + "="*60)
    print("CARGANDO DATOS")
    print("="*60)
    
    filepath = PROCESSED_DATA_DIR / 'dengue_semanal.csv'
    df = pd.read_csv(filepath)
    
    # Asegurar que fecha sea datetime
    df['fecha'] = pd.to_datetime(df['fecha'])
    
    print(f"[OK] Datos cargados: {len(df)} registros")
    print(f"[OK] Rango de fechas: {df['fecha'].min()} a {df['fecha'].max()}")
    print(f"[OK] Regiones: {df['departamento'].unique()}")
    
    return df


def train_models_for_region(df_region: pd.DataFrame, region_name: str):
    """
    Entrenar todos los modelos para una región específica
    
    Args:
        df_region: DataFrame con datos de la región
        region_name: Nombre de la región
    
    Returns:
        Dictionary con modelos entrenados
    """
    print(f"\n{'='*60}")
    print(f"ENTRENANDO MODELOS PARA: {region_name}")
    print(f"{'='*60}")
    print(f"Registros disponibles: {len(df_region)}")
    
    # Ordenar por fecha
    df_region = df_region.sort_values('fecha').reset_index(drop=True)
    
    models = {}
    
    # 1. SARIMA
    print(f"\n[1/4] Entrenando SARIMA...")
    try:
        sarima = SARIMAForecaster()
        sarima.fit(df_region, target_col='casos')
        models['sarima'] = sarima
        print("✓ SARIMA entrenado exitosamente")
    except Exception as e:
        print(f"✗ Error en SARIMA: {e}")
        models['sarima'] = None
    
    # 2. Prophet
    print(f"\n[2/4] Entrenando Prophet...")
    try:
        prophet = ProphetForecaster()
        prophet.fit(df_region, date_col='fecha', target_col='casos')
        models['prophet'] = prophet
        print("✓ Prophet entrenado exitosamente")
    except Exception as e:
        print(f"✗ Error en Prophet: {e}")
        models['prophet'] = None
    
    
    # 3. LSTM
    print(f"\n[3/4] Entrenando LSTM...")
    try:
        lstm = LSTMForecaster(lookback=52)
        lstm.fit(df_region, target_col='casos', epochs=30)  # Reducido de 50 a 30
        models['lstm'] = lstm
        print("✓ LSTM entrenado exitosamente")
    except Exception as e:
        print(f"✗ Error en LSTM: {e}")
        models['lstm'] = None
    
    # 4. XGBoost
    print(f"\n[4/4] Entrenando XGBoost...")
    try:
        xgboost = XGBoostForecaster(lookback=52)
        xgboost.fit(df_region, target_col='casos')
        models['xgboost'] = xgboost
        print("✓ XGBoost entrenado exitosamente")
    except Exception as e:
        print(f"✗ Error en XGBoost: {e}")
        models['xgboost'] = None
    
    return models


def save_models(models_dict: dict, region_name: str):
    """Guardar modelos entrenados"""
    print(f"\nGuardando modelos para {region_name}...")
    
    # Crear directorio si no existe
    FORECASTING_MODELS_DIR.mkdir(parents=True, exist_ok=True)
    
    for model_name, model in models_dict.items():
        if model is not None:
            filepath = FORECASTING_MODELS_DIR / f"{region_name}_{model_name}.pkl"
            model.save(str(filepath))
            print(f"✓ {model_name} guardado en: {filepath}")


def main():
    """Función principal"""
    print("\n" + "="*60)
    print("ENTRENAMIENTO DE MODELOS DE FORECASTING - SIDET")
    print("="*60)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Cargar datos
    df = load_data()
    
    # Entrenar modelos por región
    all_models = {}
    
    for region in REGIONES_OBJETIVO:
        # Filtrar datos de la región
        df_region = df[df['departamento'] == region].copy()
        
        if len(df_region) < 100:
            print(f"\n⚠ Advertencia: {region} tiene muy pocos datos ({len(df_region)} registros). Saltando...")
            continue
        
        # Entrenar modelos
        models = train_models_for_region(df_region, region)
        
        # Guardar modelos
        save_models(models, region)
        
        # Almacenar en diccionario general
        all_models[region] = models
    
    # Resumen final
    print("\n" + "="*60)
    print("RESUMEN DE ENTRENAMIENTO")
    print("="*60)
    
    for region, models in all_models.items():
        print(f"\n{region}:")
        for model_name, model in models.items():
            status = "✓ Entrenado" if model is not None else "✗ Falló"
            print(f"  - {model_name}: {status}")
    
    print("\n" + "="*60)
    print("ENTRENAMIENTO COMPLETADO")
    print("="*60)
    print(f"Modelos guardados en: {FORECASTING_MODELS_DIR}")
    

if __name__ == "__main__":
    main()
