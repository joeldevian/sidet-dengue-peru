"""
Script para explorar la estructura del dataset descargado
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.append(str(ROOT_DIR))

from config import RAW_DATA_DIR
import pandas as pd

def main():
    """Explora la estructura del dataset"""
    
    data_path = RAW_DATA_DIR / 'dengue_2000_2024.csv'
    
    print("=" * 70)
    print("EXPLORACIÓN DE ESTRUCTURA DEL DATASET")
    print("=" * 70)
    print(f"\nArchivo: {data_path}\n")
    
    # Cargar solo las primeras filas para explorar
    print("Cargando muestra (1000 registros)...\n")
    df = pd.read_csv(data_path, nrows=1000, on_bad_lines='skip')
    
    print(f"✓ Registros cargados: {len(df)}")
    print(f"✓ Columnas encontradas: {len(df.columns)}\n")
    
    print("=" * 70)
    print("COLUMNAS DEL DATASET:")
    print("=" * 70)
    for i, col in enumerate(df.columns, 1):
        print(f"{i:2d}. {col}")
    
    print("\n" + "=" * 70)
    print("PRIMERAS 5 FILAS:")
    print("=" * 70)
    print(df.head())
    
    print("\n" + "=" * 70)
    print("INFORMACIÓN DEL DATASET:")
    print("=" * 70)
    df.info()
    
    print("\n" + "=" * 70)
    print("VALORES ÚNICOS EN COLUMNAS CLAVE:")
    print("=" * 70)
    
    # Intentar identificar columnas importantes
    for col in df.columns:
        col_lower = col.lower()
        if any(keyword in col_lower for keyword in ['depart', 'region', 'año', 'ano', 'year', 'semana', 'week']):
            unique_count = df[col].nunique()
            print(f"\n{col}:")
            print(f"  Valores únicos: {unique_count}")
            if unique_count < 20:
                print(f"  Valores: {df[col].unique()[:10]}")

if __name__ == "__main__":
    main()
