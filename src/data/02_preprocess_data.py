"""
Script para ejecutar el preprocesamiento completo de datos
"""

import sys
from pathlib import Path

# Agregar directorio raíz al path
ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.append(str(ROOT_DIR))

from config import RAW_DATA_DIR, PROCESSED_DATA_DIR, REGIONES_OBJETIVO
from src.data.preprocessing import DengueDataPreprocessor
import pandas as pd

def main():
    """Ejecuta el pipeline de preprocesamiento"""
    
    print("=" * 70)
    print("PREPROCESAMIENTO DE DATOS - SIDET")
    print("=" * 70)
    
    # Inicializar preprocesador
    preprocessor = DengueDataPreprocessor(REGIONES_OBJETIVO)
    
    # Rutas de archivos
    input_file = RAW_DATA_DIR / 'dengue_2000_2024.csv'
    output_file = PROCESSED_DATA_DIR / 'dengue_limpio.csv'
    output_agregado = PROCESSED_DATA_DIR / 'dengue_semanal.csv'
    
    print(f"\n1. Cargando datos desde: {input_file}")
    print("   (Esto puede tomar varios minutos...)\n")
    
    # Cargar datos completos
    df = preprocessor.cargar_datos_completos(str(input_file))
    
    print(f"\n2. Limpiando datos...")
    df_clean = preprocessor.limpiar_datos(df)
    
    print(f"\n3. Filtrando regiones objetivo...")
    df_filtrado = preprocessor.filtrar_regiones_objetivo(df_clean)
    
    print(f"\n4. Creando columna de fecha...")
    df_con_fecha = preprocessor.crear_columna_fecha(df_filtrado)
    
    print(f"\n5. Guardando datos limpios...")
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    df_con_fecha.to_csv(output_file, index=False)
    print(f"   ✓ Guardado en: {output_file}")
    
    print(f"\n6. Agregando por semana epidemiológica...")
    df_semanal = preprocessor.agregar_por_semana(df_con_fecha)
    
    print(f"\n7. Guardando datos agregados...")
    df_semanal.to_csv(output_agregado, index=False)
    print(f"   ✓ Guardado en: {output_agregado}")
    
    print(f"\n8. Generando reporte de calidad...")
    reporte = preprocessor.generar_reporte_calidad(df_semanal)
    
    print("\n" + "=" * 70)
    print("RESUMEN DEL PREPROCESAMIENTO")
    print("=" * 70)
    print(f"Registros originales:     {len(df):,}")
    print(f"Registros filtrados:      {len(df_filtrado):,}")
    print(f"Registros semanales:      {len(df_semanal):,}")
    print(f"Período:                  {df_semanal['fecha'].min()} a {df_semanal['fecha'].max()}")
    print(f"Memoria utilizada:        {reporte['memoria_mb']:.2f} MB")
    print("=" * 70)
    print("\n✓ Preprocesamiento completado exitosamente\n")

if __name__ == "__main__":
    main()
