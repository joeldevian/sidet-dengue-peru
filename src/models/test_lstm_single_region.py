# ============================================
# SCRIPT DE PRUEBA LSTM - UNA REGIÓN
# ============================================

import sys
from pathlib import Path

# Añadir directorio raíz al path
sys.path.append(str(Path(__file__).parent.parent.parent))

import pandas as pd
import numpy as np
from datetime import datetime

from config import (
    PROCESSED_DATA_DIR,
    FORECASTING_MODELS_DIR,
    FORECASTING_CONFIG
)

from src.models.forecasting_models import LSTMForecaster


def main():
    """Probar LSTM con una sola región"""
    print("\n" + "="*60)
    print("PRUEBA DE LSTM - UNA REGIÓN")
    print("="*60)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Cargar datos
    print("\nCargando datos...")
    filepath = PROCESSED_DATA_DIR / 'dengue_semanal.csv'
    df = pd.read_csv(filepath)
    df['fecha'] = pd.to_datetime(df['fecha'])
    
    # Seleccionar LORETO (región con más datos)
    region = 'LORETO'
    df_region = df[df['departamento'] == region].copy()
    df_region = df_region.sort_values('fecha').reset_index(drop=True)
    
    print(f"\n[OK] Región: {region}")
    print(f"[OK] Registros: {len(df_region)}")
    print(f"[OK] Rango: {df_region['fecha'].min()} a {df_region['fecha'].max()}")
    
    # Entrenar LSTM
    print("\n" + "="*60)
    print("ENTRENANDO LSTM")
    print("="*60)
    
    try:
        lstm = LSTMForecaster(lookback=52)
        lstm.fit(df_region, target_col='casos', epochs=30)
        
        print("\n✓ LSTM entrenado exitosamente")
        
        # Hacer predicción de prueba
        print("\nProbando predicción (52 semanas = 1 año)...")
        predictions, lower, upper = lstm.predict(steps=52)
        
        print(f"✓ Predicciones generadas: {len(predictions)} valores")
        print(f"  - Rango predicho: {predictions.min():.1f} - {predictions.max():.1f} casos")
        print(f"  - Media predicha: {predictions.mean():.1f} casos")
        
        # Guardar modelo
        FORECASTING_MODELS_DIR.mkdir(parents=True, exist_ok=True)
        filepath = FORECASTING_MODELS_DIR / f"{region}_lstm_test.pkl"
        lstm.save(str(filepath))
        print(f"\n✓ Modelo guardado en: {filepath}")
        
        print("\n" + "="*60)
        print("PRUEBA COMPLETADA EXITOSAMENTE ✓")
        print("="*60)
        
    except Exception as e:
        print(f"\n✗ Error durante el entrenamiento: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
