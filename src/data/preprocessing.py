"""
Módulo de preprocesamiento de datos de dengue
Funciones para limpieza, normalización y transformación de datos
"""

import pandas as pd
import numpy as np
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DengueDataPreprocessor:
    """Clase para preprocesamiento de datos de dengue"""
    
    def __init__(self, regiones_objetivo: List[str]):
        """
        Inicializa el preprocesador
        
        Args:
            regiones_objetivo: Lista de regiones a analizar
        """
        self.regiones_objetivo = [r.upper() for r in regiones_objetivo]
        
    def cargar_datos_completos(self, filepath: str, chunksize: int = 50000) -> pd.DataFrame:
        """
        Carga el dataset completo por chunks para evitar problemas de memoria
        
        Args:
            filepath: Ruta al archivo CSV
            chunksize: Tamaño de chunks para lectura
            
        Returns:
            DataFrame completo
        """
        logger.info(f"Cargando datos desde: {filepath}")
        logger.info(f"Usando chunks de {chunksize:,} registros")
        
        chunks = []
        total_rows = 0
        
        try:
            # Parámetros para manejar CSV con formato inconsistente (pandas 2.x)
            for i, chunk in enumerate(pd.read_csv(
                filepath, 
                sep=';',  # El CSV usa punto y coma como delimitador
                chunksize=chunksize, 
                low_memory=False,
                encoding='utf-8',
                on_bad_lines='skip'  # Saltar líneas problemáticas (pandas 2.x)
            )):
                chunks.append(chunk)
                total_rows += len(chunk)
                if (i + 1) % 5 == 0:
                    logger.info(f"Procesados {total_rows:,} registros...")
            
            df = pd.concat(chunks, ignore_index=True)
            logger.info(f"✓ Dataset completo cargado: {len(df):,} registros")
            return df
            
        except Exception as e:
            logger.error(f"Error al cargar datos: {str(e)}")
            raise
    
    def limpiar_datos(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Limpia y normaliza los datos
        
        Args:
            df: DataFrame original
            
        Returns:
            DataFrame limpio
        """
        logger.info("Iniciando limpieza de datos...")
        df_clean = df.copy()
        
        # Normalizar nombres de columnas
        df_clean.columns = df_clean.columns.str.lower().str.strip()
        
        # Normalizar texto en columnas categóricas
        text_columns = df_clean.select_dtypes(include=['object']).columns
        for col in text_columns:
            if col in df_clean.columns:
                df_clean[col] = df_clean[col].str.upper().str.strip()
        
        # Eliminar duplicados
        duplicados_antes = len(df_clean)
        df_clean = df_clean.drop_duplicates()
        duplicados_eliminados = duplicados_antes - len(df_clean)
        
        if duplicados_eliminados > 0:
            logger.info(f"Eliminados {duplicados_eliminados:,} registros duplicados")
        
        logger.info("✓ Limpieza completada")
        return df_clean
    
    def filtrar_regiones_objetivo(self, df: pd.DataFrame, col_departamento: str = 'departamento') -> pd.DataFrame:
        """
        Filtra el dataset por las regiones objetivo
        
        Args:
            df: DataFrame completo
            col_departamento: Nombre de la columna de departamento
            
        Returns:
            DataFrame filtrado
        """
        logger.info(f"Filtrando por regiones objetivo: {', '.join(self.regiones_objetivo)}")
        
        if col_departamento not in df.columns:
            logger.warning(f"Columna '{col_departamento}' no encontrada")
            return df
        
        df_filtrado = df[df[col_departamento].isin(self.regiones_objetivo)].copy()
        
        logger.info(f"✓ Registros filtrados: {len(df_filtrado):,} de {len(df):,}")
        logger.info(f"  Porcentaje: {(len(df_filtrado)/len(df)*100):.1f}%")
        
        # Mostrar distribución por región
        logger.info("\nDistribución por región:")
        for region in self.regiones_objetivo:
            count = len(df_filtrado[df_filtrado[col_departamento] == region])
            logger.info(f"  {region}: {count:,} registros")
        
        return df_filtrado
    
    def crear_columna_fecha(self, df: pd.DataFrame, col_ano: str = 'ano', 
                           col_semana: str = 'semana') -> pd.DataFrame:
        """
        Crea columna de fecha a partir de año y semana epidemiológica
        
        Args:
            df: DataFrame
            col_ano: Nombre de columna de año
            col_semana: Nombre de columna de semana
            
        Returns:
            DataFrame con columna fecha
        """
        logger.info("Creando columna de fecha...")
        
        df_copy = df.copy()
        
        try:
            # Crear fecha como primer día de la semana epidemiológica
            df_copy['fecha'] = pd.to_datetime(
                df_copy[col_ano].astype(str) + '-W' + df_copy[col_semana].astype(str).str.zfill(2) + '-1',
                format='%Y-W%W-%w',
                errors='coerce'
            )
            
            # Contar fechas inválidas
            fechas_invalidas = df_copy['fecha'].isna().sum()
            if fechas_invalidas > 0:
                logger.warning(f"Fechas inválidas: {fechas_invalidas:,}")
            
            logger.info("✓ Columna fecha creada")
            
        except Exception as e:
            logger.error(f"Error al crear columna fecha: {str(e)}")
            raise
        
        return df_copy
    
    def agregar_por_semana(self, df: pd.DataFrame, col_departamento: str = 'departamento',
                          col_ano: str = 'ano', col_semana: str = 'semana') -> pd.DataFrame:
        """
        Agrega datos por semana epidemiológica y región
        
        Args:
            df: DataFrame con datos individuales
            col_departamento: Columna de departamento
            col_ano: Columna de año
            col_semana: Columna de semana
            
        Returns:
            DataFrame agregado por semana
        """
        logger.info("Agregando datos por semana epidemiológica...")
        
        # Agrupar y contar casos
        df_agregado = df.groupby([col_departamento, col_ano, col_semana]).size().reset_index(name='casos')
        
        # Crear columna de fecha
        df_agregado['fecha'] = pd.to_datetime(
            df_agregado[col_ano].astype(str) + '-W' + df_agregado[col_semana].astype(str).str.zfill(2) + '-1',
            format='%Y-W%W-%w',
            errors='coerce'
        )
        
        # Ordenar por fecha
        df_agregado = df_agregado.sort_values(['fecha', col_departamento]).reset_index(drop=True)
        
        logger.info(f"✓ Datos agregados: {len(df_agregado):,} registros semanales")
        
        return df_agregado
    
    def generar_reporte_calidad(self, df: pd.DataFrame) -> Dict:
        """
        Genera reporte de calidad de datos
        
        Args:
            df: DataFrame a analizar
            
        Returns:
            Diccionario con métricas de calidad
        """
        logger.info("Generando reporte de calidad de datos...")
        
        reporte = {
            'total_registros': len(df),
            'total_columnas': len(df.columns),
            'valores_faltantes': df.isnull().sum().to_dict(),
            'porcentaje_faltantes': ((df.isnull().sum() / len(df)) * 100).to_dict(),
            'tipos_datos': df.dtypes.astype(str).to_dict(),
            'memoria_mb': df.memory_usage(deep=True).sum() / 1024**2
        }
        
        logger.info("✓ Reporte generado")
        
        return reporte
