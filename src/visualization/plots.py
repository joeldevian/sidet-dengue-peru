"""
Módulo de visualización de datos de dengue
Funciones para crear gráficos y análisis visual
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import logging
from typing import List, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DengueVisualizer:
    """Clase para visualización de datos de dengue"""
    
    def __init__(self, figsize=(14, 8), style='seaborn-v0_8-darkgrid'):
        """
        Inicializa el visualizador
        
        Args:
            figsize: Tamaño de figuras por defecto
            style: Estilo de matplotlib
        """
        self.figsize = figsize
        plt.style.use(style)
        sns.set_palette('husl')
        
    def plot_serie_temporal_region(self, df: pd.DataFrame, region: str, 
                                   col_fecha: str = 'fecha', col_casos: str = 'casos',
                                   col_departamento: str = 'departamento',
                                   save_path: Path = None):
        """
        Grafica la serie temporal de casos para una región
        
        Args:
            df: DataFrame con datos agregados
            region: Nombre de la región
            col_fecha: Columna de fecha
            col_casos: Columna de casos
            col_departamento: Columna de departamento
            save_path: Ruta para guardar la figura
        """
        logger.info(f"Graficando serie temporal para {region}")
        
        # Filtrar datos de la región
        df_region = df[df[col_departamento] == region].copy()
        df_region = df_region.sort_values(col_fecha)
        
        # Crear figura
        fig, ax = plt.subplots(figsize=self.figsize)
        
        # Graficar serie temporal
        ax.plot(df_region[col_fecha], df_region[col_casos], 
               linewidth=1.5, color='steelblue', alpha=0.7)
        
        # Agregar media móvil de 4 semanas
        df_region['ma_4'] = df_region[col_casos].rolling(window=4, center=True).mean()
        ax.plot(df_region[col_fecha], df_region['ma_4'], 
               linewidth=2.5, color='darkred', label='Media Móvil (4 semanas)')
        
        # Configurar gráfico
        ax.set_title(f'Serie Temporal de Casos de Dengue - {region}', 
                    fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Fecha', fontsize=12)
        ax.set_ylabel('Número de Casos', fontsize=12)
        ax.legend(loc='upper left')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Figura guardada en: {save_path}")
        
        plt.close()  # Cerrar figura en lugar de mostrar
        
    def plot_comparacion_regiones(self, df: pd.DataFrame, regiones: List[str],
                                 col_fecha: str = 'fecha', col_casos: str = 'casos',
                                 col_departamento: str = 'departamento',
                                 save_path: Path = None):
        """
        Compara series temporales de múltiples regiones
        
        Args:
            df: DataFrame con datos agregados
            regiones: Lista de regiones a comparar
            col_fecha: Columna de fecha
            col_casos: Columna de casos
            col_departamento: Columna de departamento
            save_path: Ruta para guardar la figura
        """
        logger.info(f"Comparando {len(regiones)} regiones")
        
        fig, axes = plt.subplots(len(regiones), 1, figsize=(14, 4*len(regiones)))
        
        if len(regiones) == 1:
            axes = [axes]
        
        for i, region in enumerate(regiones):
            df_region = df[df[col_departamento] == region].copy()
            df_region = df_region.sort_values(col_fecha)
            
            axes[i].plot(df_region[col_fecha], df_region[col_casos], 
                        linewidth=1, alpha=0.6)
            
            # Media móvil
            df_region['ma_8'] = df_region[col_casos].rolling(window=8, center=True).mean()
            axes[i].plot(df_region[col_fecha], df_region['ma_8'], 
                        linewidth=2, color='darkred', label='Media Móvil (8 semanas)')
            
            axes[i].set_title(region, fontsize=14, fontweight='bold')
            axes[i].set_ylabel('Casos', fontsize=11)
            axes[i].grid(True, alpha=0.3)
            axes[i].legend()
        
        axes[-1].set_xlabel('Fecha', fontsize=12)
        
        plt.suptitle('Comparación de Series Temporales por Región', 
                    fontsize=16, fontweight='bold', y=1.001)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Figura guardada en: {save_path}")
        
        plt.close()  # Cerrar figura en lugar de mostrar
        
    def plot_estacionalidad(self, df: pd.DataFrame, region: str,
                           col_fecha: str = 'fecha', col_casos: str = 'casos',
                           col_departamento: str = 'departamento',
                           save_path: Path = None):
        """
        Analiza y grafica la estacionalidad de casos
        
        Args:
            df: DataFrame con datos agregados
            region: Nombre de la región
            col_fecha: Columna de fecha
            col_casos: Columna de casos
            col_departamento: Columna de departamento
            save_path: Ruta para guardar la figura
        """
        logger.info(f"Analizando estacionalidad para {region}")
        
        # Filtrar y preparar datos
        df_region = df[df[col_departamento] == region].copy()
        df_region[col_fecha] = pd.to_datetime(df_region[col_fecha])
        df_region['mes'] = df_region[col_fecha].dt.month
        df_region['año'] = df_region[col_fecha].dt.year
        
        # Crear figura con subplots
        fig, axes = plt.subplots(1, 2, figsize=(16, 6))
        
        # Boxplot por mes
        monthly_data = df_region.groupby('mes')[col_casos].apply(list)
        axes[0].boxplot([monthly_data[i] if i in monthly_data.index else [] 
                        for i in range(1, 13)],
                       labels=['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun',
                              'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'])
        axes[0].set_title(f'Distribución Mensual de Casos - {region}', 
                         fontsize=14, fontweight='bold')
        axes[0].set_ylabel('Número de Casos', fontsize=12)
        axes[0].set_xlabel('Mes', fontsize=12)
        axes[0].grid(True, alpha=0.3, axis='y')
        
        # Promedio por mes
        monthly_avg = df_region.groupby('mes')[col_casos].mean()
        axes[1].bar(range(1, 13), monthly_avg, color='steelblue', alpha=0.7)
        axes[1].set_title(f'Promedio de Casos por Mes - {region}', 
                         fontsize=14, fontweight='bold')
        axes[1].set_ylabel('Promedio de Casos', fontsize=12)
        axes[1].set_xlabel('Mes', fontsize=12)
        axes[1].set_xticks(range(1, 13))
        axes[1].set_xticklabels(['E', 'F', 'M', 'A', 'M', 'J', 
                                'J', 'A', 'S', 'O', 'N', 'D'])
        axes[1].grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Figura guardada en: {save_path}")
        
        plt.close()  # Cerrar figura en lugar de mostrar
        
    def plot_heatmap_anual(self, df: pd.DataFrame, region: str,
                          col_fecha: str = 'fecha', col_casos: str = 'casos',
                          col_departamento: str = 'departamento',
                          save_path: Path = None):
        """
        Crea un heatmap de casos por año y semana
        
        Args:
            df: DataFrame con datos agregados
            region: Nombre de la región
            col_fecha: Columna de fecha
            col_casos: Columna de casos
            col_departamento: Columna de departamento
            save_path: Ruta para guardar la figura
        """
        logger.info(f"Creando heatmap para {region}")
        
        # Filtrar y preparar datos
        df_region = df[df[col_departamento] == region].copy()
        df_region[col_fecha] = pd.to_datetime(df_region[col_fecha])
        df_region['año'] = df_region[col_fecha].dt.year
        df_region['semana'] = df_region[col_fecha].dt.isocalendar().week
        
        # Crear pivot table
        pivot = df_region.pivot_table(values=col_casos, 
                                      index='semana', 
                                      columns='año', 
                                      aggfunc='sum',
                                      fill_value=0)
        
        # Crear heatmap
        fig, ax = plt.subplots(figsize=(16, 10))
        sns.heatmap(pivot, cmap='YlOrRd', cbar_kws={'label': 'Casos'}, 
                   linewidths=0.5, ax=ax)
        
        ax.set_title(f'Heatmap de Casos de Dengue por Semana y Año - {region}', 
                    fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Año', fontsize=12)
        ax.set_ylabel('Semana Epidemiológica', fontsize=12)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Figura guardada en: {save_path}")
        
        plt.close()  # Cerrar figura en lugar de mostrar
        
    def generar_reporte_estadistico(self, df: pd.DataFrame, regiones: List[str],
                                    col_casos: str = 'casos',
                                    col_departamento: str = 'departamento') -> pd.DataFrame:
        """
        Genera reporte estadístico por región
        
        Args:
            df: DataFrame con datos agregados
            regiones: Lista de regiones
            col_casos: Columna de casos
            col_departamento: Columna de departamento
            
        Returns:
            DataFrame con estadísticas por región
        """
        logger.info("Generando reporte estadístico")
        
        stats = []
        
        for region in regiones:
            df_region = df[df[col_departamento] == region]
            
            stats.append({
                'Región': region,
                'Total Casos': df_region[col_casos].sum(),
                'Promedio Semanal': df_region[col_casos].mean(),
                'Mediana': df_region[col_casos].median(),
                'Desv. Estándar': df_region[col_casos].std(),
                'Mínimo': df_region[col_casos].min(),
                'Máximo': df_region[col_casos].max(),
                'Percentil 75': df_region[col_casos].quantile(0.75),
                'Percentil 95': df_region[col_casos].quantile(0.95)
            })
        
        return pd.DataFrame(stats)
