# ============================================
# SCRIPT DE GENERACIÓN DE PREDICCIONES
# ============================================

import sys
from pathlib import Path

# Añadir directorio raíz al path
sys.path.append(str(Path(__file__).parent.parent.parent))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pickle

from config import (
    PROCESSED_DATA_DIR,
    FORECASTING_MODELS_DIR,
    REGIONES_OBJETIVO,
    FORECASTING_CONFIG,
    ENSEMBLE_WEIGHTS
)

from src.models.forecasting_models import (
    BaseForecaster,
    EnsembleForecaster
)


def load_model(region: str, model_name: str) -> BaseForecaster:
    """Cargar modelo entrenado"""
    filepath = FORECASTING_MODELS_DIR / f"{region}_{model_name}.pkl"
    
    if not filepath.exists():
        print(f"⚠ Advertencia: Modelo {model_name} no encontrado para {region}")
        return None
    
    return BaseForecaster.load(str(filepath))


def generate_future_dates(start_date: pd.Timestamp, steps: int) -> pd.DatetimeIndex:
    """Generar fechas futuras semanales"""
    return pd.date_range(start=start_date, periods=steps, freq='W')


def predict_for_region(region: str, steps: int):
    """
    Generar predicciones para una región
    
    Args:
        region: Nombre de la región
        steps: Número de semanas a predecir
    
    Returns:
        DataFrame con predicciones
    """
    print(f"\n{'='*60}")
    print(f"GENERANDO PREDICCIONES PARA: {region}")
    print(f"{'='*60}")
    
    # Cargar modelos
    models = {}
    for model_name in ['sarima', 'prophet', 'lstm', 'xgboost']:
        model = load_model(region, model_name)
        if model is not None:
            models[model_name] = model
    
    if not models:
        print(f"✗ No hay modelos disponibles para {region}")
        return None
    
    print(f"✓ Modelos cargados: {list(models.keys())}")
    
    # Crear ensamble
    ensemble = EnsembleForecaster(weights=ENSEMBLE_WEIGHTS)
    for name, model in models.items():
        ensemble.add_model(name, model)
    
    # Generar predicciones
    print(f"\nGenerando predicciones para {steps} semanas...")
    
    # Predicción del ensamble
    ensemble_pred, ensemble_lower, ensemble_upper = ensemble.predict(steps)
    
    # Predicciones individuales
    individual_preds = ensemble.get_individual_predictions(steps)
    
    # Obtener última fecha de datos
    df = pd.read_csv(PROCESSED_DATA_DIR / 'dengue_semanal.csv')
    df['fecha'] = pd.to_datetime(df['fecha'])
    df_region = df[df['departamento'] == region]
    last_date = df_region['fecha'].max()
    
    # Generar fechas futuras
    future_dates = generate_future_dates(last_date + timedelta(weeks=1), steps)
    
    # Crear DataFrame de resultados
    results = pd.DataFrame({
        'region': region,
        'fecha': future_dates,
        'año': future_dates.year,
        'semana': future_dates.isocalendar().week,
        'casos_predichos_ensamble': ensemble_pred,
        'intervalo_inferior_95': ensemble_lower,
        'intervalo_superior_95': ensemble_upper,
    })
    
    # Añadir predicciones individuales
    for model_name, (pred, lower, upper) in individual_preds.items():
        results[f'casos_predichos_{model_name}'] = pred
        results[f'{model_name}_lower'] = lower
        results[f'{model_name}_upper'] = upper
    
    print(f"✓ Predicciones generadas exitosamente")
    print(f"  - Rango de fechas: {future_dates[0].date()} a {future_dates[-1].date()}")
    print(f"  - Casos promedio predichos: {ensemble_pred.mean():.1f}")
    print(f"  - Rango de predicción: {ensemble_pred.min():.1f} - {ensemble_pred.max():.1f}")
    
    return results


def calculate_prediction_stats(df_predictions: pd.DataFrame) -> pd.DataFrame:
    """Calcular estadísticas de las predicciones"""
    stats = df_predictions.groupby('region').agg({
        'casos_predichos_ensamble': ['mean', 'std', 'min', 'max'],
        'intervalo_inferior_95': 'mean',
        'intervalo_superior_95': 'mean'
    }).round(2)
    
    return stats


def main():
    """Función principal"""
    print("\n" + "="*60)
    print("GENERACIÓN DE PREDICCIONES PROSPECTIVAS - SIDET")
    print("="*60)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Horizonte de predicción: {FORECASTING_CONFIG['año_inicio_prediccion']} - {FORECASTING_CONFIG['año_fin_prediccion']}")
    
    # Número de semanas a predecir
    steps = FORECASTING_CONFIG['horizonte_prediccion']
    print(f"Semanas a predecir: {steps} ({steps/52:.1f} años)")
    
    # Generar predicciones para cada región
    all_predictions = []
    
    for region in REGIONES_OBJETIVO:
        predictions = predict_for_region(region, steps)
        
        if predictions is not None:
            all_predictions.append(predictions)
    
    if not all_predictions:
        print("\n✗ No se generaron predicciones para ninguna región")
        return
    
    # Combinar todas las predicciones
    df_all_predictions = pd.concat(all_predictions, ignore_index=True)
    
    # Guardar predicciones
    output_dir = PROCESSED_DATA_DIR / 'predictions'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / 'predicciones_2026_2028.csv'
    df_all_predictions.to_csv(output_file, index=False)
    
    print("\n" + "="*60)
    print("RESUMEN DE PREDICCIONES")
    print("="*60)
    
    # Estadísticas por región
    stats = calculate_prediction_stats(df_all_predictions)
    print("\nEstadísticas por región:")
    print(stats)
    
    print("\n" + "="*60)
    print("PREDICCIONES GENERADAS EXITOSAMENTE")
    print("="*60)
    print(f"Archivo guardado: {output_file}")
    print(f"Total de predicciones: {len(df_all_predictions)} registros")
    print(f"Regiones: {df_all_predictions['region'].nunique()}")
    

if __name__ == "__main__":
    main()
