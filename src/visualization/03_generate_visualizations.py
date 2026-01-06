"""
Script para generar visualizaciones y análisis exploratorio
"""

import sys
from pathlib import Path

# Configurar matplotlib para modo no interactivo
import matplotlib
matplotlib.use('Agg')  # Backend no interactivo

ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.append(str(ROOT_DIR))

from config import PROCESSED_DATA_DIR, FIGURES_DIR, REGIONES_OBJETIVO
from src.visualization.plots import DengueVisualizer
import pandas as pd

def main():
    """Genera visualizaciones del análisis exploratorio"""
    
    print("=" * 70)
    print("ANÁLISIS EXPLORATORIO Y VISUALIZACIÓN - SIDET")
    print("=" * 70)
    
    # Cargar datos procesados
    data_path = PROCESSED_DATA_DIR / 'dengue_semanal.csv'
    print(f"\nCargando datos desde: {data_path}")
    
    df = pd.read_csv(data_path)
    df['fecha'] = pd.to_datetime(df['fecha'])
    
    print(f"✓ Datos cargados: {len(df):,} registros")
    print(f"  Período: {df['fecha'].min()} a {df['fecha'].max()}")
    print(f"  Regiones: {df['departamento'].nunique()}")
    
    # Crear directorio de figuras
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    
    # Inicializar visualizador
    viz = DengueVisualizer()
    
    print("\n" + "=" * 70)
    print("GENERANDO VISUALIZACIONES")
    print("=" * 70)
    
    # 1. Comparación de regiones
    print("\n1. Comparando series temporales de todas las regiones...")
    viz.plot_comparacion_regiones(
        df, 
        REGIONES_OBJETIVO,
        save_path=FIGURES_DIR / 'comparacion_regiones.png'
    )
    
    # 2. Análisis por región
    for region in REGIONES_OBJETIVO:
        print(f"\n2. Analizando {region}...")
        
        # Serie temporal
        viz.plot_serie_temporal_region(
            df, 
            region,
            save_path=FIGURES_DIR / f'serie_temporal_{region.lower().replace(" ", "_")}.png'
        )
        
        # Estacionalidad
        viz.plot_estacionalidad(
            df, 
            region,
            save_path=FIGURES_DIR / f'estacionalidad_{region.lower().replace(" ", "_")}.png'
        )
        
        # Heatmap
        viz.plot_heatmap_anual(
            df, 
            region,
            save_path=FIGURES_DIR / f'heatmap_{region.lower().replace(" ", "_")}.png'
        )
    
    # 3. Reporte estadístico
    print("\n3. Generando reporte estadístico...")
    stats = viz.generar_reporte_estadistico(df, REGIONES_OBJETIVO)
    
    print("\n" + "=" * 70)
    print("ESTADÍSTICAS POR REGIÓN")
    print("=" * 70)
    print(stats.to_string(index=False))
    
    # Guardar reporte
    stats_path = PROCESSED_DATA_DIR / 'estadisticas_regiones.csv'
    stats.to_csv(stats_path, index=False)
    print(f"\n✓ Reporte guardado en: {stats_path}")
    
    print("\n" + "=" * 70)
    print("✓ ANÁLISIS EXPLORATORIO COMPLETADO")
    print("=" * 70)
    print(f"\nFiguras guardadas en: {FIGURES_DIR}")
    print(f"Total de figuras generadas: {len(list(FIGURES_DIR.glob('*.png')))}")

if __name__ == "__main__":
    main()
