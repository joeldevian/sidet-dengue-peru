"""
Script para entrenar modelos de detección de anomalías
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.append(str(ROOT_DIR))

from config import PROCESSED_DATA_DIR, REGIONES_OBJETIVO
from src.models.anomaly_detection import AnomalyDetector
import pandas as pd

def main():
    """Entrena los modelos de detección de anomalías"""
    
    print("=" * 70)
    print("ENTRENAMIENTO DE MODELOS - SIDET")
    print("=" * 70)
    
    # Cargar datos con features
    input_path = PROCESSED_DATA_DIR / 'dengue_features.csv'
    print(f"\nCargando datos desde: {input_path}")
    
    df = pd.read_csv(input_path)
    print(f"✓ Datos cargados: {len(df):,} registros, {len(df.columns)} columnas")
    
    # Seleccionar features para el modelo
    # Excluir columnas no numéricas y la columna objetivo
    exclude_cols = ['departamento', 'fecha', 'casos', 'ano', 'semana']
    feature_cols = [col for col in df.columns if col not in exclude_cols]
    
    print(f"\nFeatures seleccionadas: {len(feature_cols)}")
    print(f"Primeras 10 features: {feature_cols[:10]}")
    
    # Inicializar detector
    detector = AnomalyDetector(contamination=0.05)  # 5% de anomalías esperadas
    
    # Entrenar modelos para todas las regiones
    detector.entrenar_todos_modelos(df, feature_cols, REGIONES_OBJETIVO)
    
    # Guardar modelos
    models_dir = ROOT_DIR / 'models' / 'saved'
    detector.guardar_modelos(models_dir)
    
    # Detectar anomalías en datos de entrenamiento
    print("\n" + "=" * 70)
    print("DETECTANDO ANOMALÍAS EN DATOS DE ENTRENAMIENTO")
    print("=" * 70)
    
    resultados = []
    for region in REGIONES_OBJETIVO:
        df_anomalias = detector.detectar_anomalias(df, feature_cols, region)
        resultados.append(df_anomalias)
        
        n_anomalias = df_anomalias['anomalia_consenso'].sum()
        pct_anomalias = (n_anomalias / len(df_anomalias)) * 100
        
        print(f"\n{region}:")
        print(f"  Total registros: {len(df_anomalias):,}")
        print(f"  Anomalías detectadas: {n_anomalias:,} ({pct_anomalias:.2f}%)")
    
    # Guardar resultados
    df_resultados = pd.concat(resultados, ignore_index=True)
    output_path = PROCESSED_DATA_DIR / 'dengue_anomalias.csv'
    df_resultados.to_csv(output_path, index=False)
    
    print("\n" + "=" * 70)
    print("✓ ENTRENAMIENTO COMPLETADO")
    print("=" * 70)
    print(f"Modelos guardados en: {models_dir}")
    print(f"Resultados guardados en: {output_path}")
    print("=" * 70)

if __name__ == "__main__":
    main()
