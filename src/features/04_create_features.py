"""
Script para ejecutar ingeniería de características
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.append(str(ROOT_DIR))

from config import PROCESSED_DATA_DIR
from src.features.feature_engineering import DengueFeatureEngineer
import pandas as pd

def main():
    """Ejecuta la ingeniería de características"""
    
    print("=" * 70)
    print("INGENIERÍA DE CARACTERÍSTICAS - SIDET")
    print("=" * 70)
    
    # Cargar datos procesados
    input_path = PROCESSED_DATA_DIR / 'dengue_semanal.csv'
    output_path = PROCESSED_DATA_DIR / 'dengue_features.csv'
    
    print(f"\nCargando datos desde: {input_path}")
    df = pd.read_csv(input_path)
    print(f"✓ Datos cargados: {len(df):,} registros, {len(df.columns)} columnas")
    
    # Inicializar feature engineer
    fe = DengueFeatureEngineer()
    
    # Crear todas las características
    print("\nCreando características...")
    df_features = fe.crear_todas_features(df)
    
    # Guardar datos con features
    print(f"\nGuardando datos con features en: {output_path}")
    df_features.to_csv(output_path, index=False)
    print(f"✓ Datos guardados exitosamente")
    
    # Mostrar resumen
    print("\n" + "=" * 70)
    print("RESUMEN DE CARACTERÍSTICAS CREADAS")
    print("=" * 70)
    print(f"Columnas originales:  {len(df.columns)}")
    print(f"Columnas finales:     {len(df_features.columns)}")
    print(f"Features nuevas:      {len(df_features.columns) - len(df.columns)}")
    print(f"Registros finales:    {len(df_features):,}")
    print("=" * 70)
    
    print("\n✓ Ingeniería de características completada\n")

if __name__ == "__main__":
    main()
