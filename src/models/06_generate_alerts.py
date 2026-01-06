"""
Script para generar alertas del sistema SIDET
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.append(str(ROOT_DIR))

from config import PROCESSED_DATA_DIR, REGIONES_OBJETIVO
from src.models.alert_system import AlertSystem
import pandas as pd

def main():
    """Genera alertas del sistema"""
    
    print("=" * 70)
    print("GENERACIÓN DE ALERTAS - SIDET")
    print("=" * 70)
    
    # Cargar datos con anomalías detectadas
    input_path = PROCESSED_DATA_DIR / 'dengue_anomalias.csv'
    print(f"\nCargando datos desde: {input_path}")
    
    df = pd.read_csv(input_path)
    print(f"✓ Datos cargados: {len(df):,} registros")
    
    # Inicializar sistema de alertas
    alert_system = AlertSystem()
    
    # Generar alertas
    print("\nGenerando alertas...")
    df_alertas = alert_system.generar_alertas(df)
    
    # Guardar alertas completas
    output_path = PROCESSED_DATA_DIR / 'dengue_alertas.csv'
    df_alertas.to_csv(output_path, index=False)
    print(f"✓ Alertas guardadas en: {output_path}")
    
    # Generar reporte por región
    print("\n" + "=" * 70)
    print("REPORTE DE ALERTAS POR REGIÓN")
    print("=" * 70)
    
    reporte = alert_system.generar_reporte_alertas(df_alertas)
    print("\n" + reporte.to_string(index=False))
    
    # Guardar reporte
    reporte_path = PROCESSED_DATA_DIR / 'reporte_alertas.csv'
    reporte.to_csv(reporte_path, index=False)
    print(f"\n✓ Reporte guardado en: {reporte_path}")
    
    # Filtrar alertas activas (últimas 4 semanas)
    print("\n" + "=" * 70)
    print("ALERTAS ACTIVAS (ÚLTIMAS 4 SEMANAS)")
    print("=" * 70)
    
    alertas_activas = alert_system.filtrar_alertas_activas(df_alertas)
    
    if len(alertas_activas) > 0:
        print(f"\n✓ {len(alertas_activas)} alertas activas encontradas\n")
        
        # Mostrar las 10 alertas más críticas
        cols_mostrar = ['departamento', 'fecha', 'nivel_riesgo', 'casos_actual', 
                       'media_historica', 'z_score', 'consenso_modelos']
        print(alertas_activas[cols_mostrar].head(10).to_string(index=False))
        
        # Guardar alertas activas
        activas_path = PROCESSED_DATA_DIR / 'alertas_activas.csv'
        alertas_activas.to_csv(activas_path, index=False)
        print(f"\n✓ Alertas activas guardadas en: {activas_path}")
    else:
        print("\n✓ No hay alertas activas en las últimas 4 semanas")
    
    # Resumen por nivel de riesgo
    print("\n" + "=" * 70)
    print("DISTRIBUCIÓN DE ALERTAS POR NIVEL DE RIESGO")
    print("=" * 70)
    
    distribucion = df_alertas['nivel_riesgo'].value_counts().sort_index()
    total = len(df_alertas)
    
    for nivel, count in distribucion.items():
        porcentaje = (count / total) * 100
        print(f"{nivel.upper():12s}: {count:6,} ({porcentaje:5.2f}%)")
    
    print("\n" + "=" * 70)
    print("✓ GENERACIÓN DE ALERTAS COMPLETADA")
    print("=" * 70)

if __name__ == "__main__":
    main()
