# ============================================
# SCRIPT DE GENERACIÓN DE ALERTAS PREDICTIVAS
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
    PREDICTIONS_DIR,
    UMBRALES_ALERTA_PREDICTIVA,
    COLORES_ALERTA_PREDICTIVA
)

from src.models.alert_system import AlertSystem


def main():
    """Función principal"""
    print("\n" + "="*60)
    print("GENERACIÓN DE ALERTAS PREDICTIVAS - SIDET")
    print("="*60)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Cargar predicciones
    print("\n[1/3] Cargando predicciones...")
    predictions_file = PREDICTIONS_DIR / 'predicciones_2026_2028.csv'
    
    if not predictions_file.exists():
        print(f"✗ Error: No se encontró el archivo de predicciones")
        print(f"  Esperado en: {predictions_file}")
        print(f"\n  Ejecuta primero: python src/models/08_generate_predictions.py")
        return
    
    df_predicciones = pd.read_csv(predictions_file)
    df_predicciones['fecha'] = pd.to_datetime(df_predicciones['fecha'])
    
    print(f"✓ Predicciones cargadas: {len(df_predicciones):,} registros")
    print(f"  - Regiones: {df_predicciones['region'].nunique()}")
    print(f"  - Rango de fechas: {df_predicciones['fecha'].min().date()} a {df_predicciones['fecha'].max().date()}")
    
    # Cargar datos históricos
    print("\n[2/3] Cargando datos históricos...")
    historical_file = PROCESSED_DATA_DIR / 'dengue_semanal.csv'
    
    if not historical_file.exists():
        print(f"✗ Error: No se encontró el archivo de datos históricos")
        return
    
    df_historico = pd.read_csv(historical_file)
    df_historico['fecha'] = pd.to_datetime(df_historico['fecha'])
    
    print(f"✓ Datos históricos cargados: {len(df_historico):,} registros")
    
    # Generar alertas predictivas
    print("\n[3/3] Generando alertas predictivas...")
    alert_system = AlertSystem(umbrales=UMBRALES_ALERTA_PREDICTIVA)
    
    df_alertas_predictivas = alert_system.generar_alertas_predictivas(
        df_predicciones=df_predicciones,
        df_historico=df_historico,
        col_casos_pred='casos_predichos_ensamble',
        col_region='region',
        col_fecha='fecha'
    )
    
    # Guardar alertas predictivas
    output_file = PREDICTIONS_DIR / 'alertas_predictivas.csv'
    df_alertas_predictivas.to_csv(output_file, index=False)
    
    print(f"\n✓ Alertas predictivas guardadas en: {output_file}")
    
    # Filtrar alertas críticas (próximos 12 meses)
    print("\n" + "="*60)
    print("ALERTAS CRÍTICAS - PRÓXIMOS 12 MESES")
    print("="*60)
    
    df_criticas = alert_system.filtrar_alertas_predictivas_criticas(
        df_alertas_predictivas,
        niveles_criticos=['alerta_temprana', 'critico'],
        meses_adelante=12
    )
    
    if len(df_criticas) > 0:
        print(f"\n⚠ Se encontraron {len(df_criticas)} alertas críticas:")
        print("\nTop 10 alertas más urgentes:")
        print("-" * 80)
        
        for idx, row in df_criticas.head(10).iterrows():
            print(f"\n{idx+1}. {row['region']} - {row['fecha'].strftime('%Y-%m-%d')}")
            print(f"   Nivel: {row['nivel_riesgo_predictivo'].upper()}")
            print(f"   Casos predichos: {row['casos_predichos']:.0f}")
            print(f"   Incremento esperado: {row['porcentaje_incremento']:.1f}%")
            
            # Obtener recomendaciones
            recomendaciones = alert_system.generar_recomendaciones_predictivas(
                row['nivel_riesgo_predictivo']
            )
            print(f"   Prioridad: {recomendaciones['prioridad']}")
            print(f"   Tiempo de anticipación: {recomendaciones['tiempo_anticipacion']}")
        
        # Guardar alertas críticas
        output_criticas = PREDICTIONS_DIR / 'alertas_criticas_12_meses.csv'
        df_criticas.to_csv(output_criticas, index=False)
        print(f"\n✓ Alertas críticas guardadas en: {output_criticas}")
    else:
        print("\n✓ No se detectaron alertas críticas para los próximos 12 meses")
    
    # Resumen por región
    print("\n" + "="*60)
    print("RESUMEN POR REGIÓN")
    print("="*60)
    
    resumen = df_alertas_predictivas.groupby('region').agg({
        'casos_predichos': ['mean', 'max'],
        'porcentaje_incremento': 'mean',
        'nivel_riesgo_predictivo': lambda x: x.value_counts().index[0]  # Nivel más frecuente
    }).round(2)
    
    print("\n", resumen)
    
    # Distribución de alertas por nivel
    print("\n" + "="*60)
    print("DISTRIBUCIÓN DE ALERTAS POR NIVEL DE RIESGO")
    print("="*60)
    
    distribucion = df_alertas_predictivas['nivel_riesgo_predictivo'].value_counts()
    print("\n", distribucion)
    print(f"\nPorcentajes:")
    for nivel, count in distribucion.items():
        porcentaje = count / len(df_alertas_predictivas) * 100
        print(f"  - {nivel}: {porcentaje:.1f}%")
    
    print("\n" + "="*60)
    print("PROCESO COMPLETADO EXITOSAMENTE")
    print("="*60)
    print(f"\nArchivos generados:")
    print(f"  1. {output_file}")
    if len(df_criticas) > 0:
        print(f"  2. {output_criticas}")
    

if __name__ == "__main__":
    main()
