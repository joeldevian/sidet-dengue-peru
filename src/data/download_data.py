"""
Utilidades para descarga de datos del MINSA
"""

import requests
import pandas as pd
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def descargar_dataset_minsa(url: str, output_path: Path, chunk_size: int = 8192) -> bool:
    """
    Descarga el dataset del MINSA de forma segura
    
    Args:
        url: URL del dataset
        output_path: Ruta donde guardar el archivo
        chunk_size: Tamaño de chunks para descarga (evita problemas de memoria)
    
    Returns:
        bool: True si la descarga fue exitosa
    """
    try:
        logger.info(f"Iniciando descarga desde: {url}")
        
        # Realizar petición con streaming para archivos grandes
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        # Crear directorio si no existe
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Descargar por chunks
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        progress = (downloaded / total_size) * 100
                        logger.info(f"Progreso: {progress:.1f}%")
        
        logger.info(f"Descarga completada: {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error en descarga: {str(e)}")
        return False


def cargar_datos_dengue(filepath: Path, nrows: int = None) -> pd.DataFrame:
    """
    Carga el dataset de dengue con manejo de memoria
    
    Args:
        filepath: Ruta al archivo CSV
        nrows: Número de filas a cargar (None para todas)
    
    Returns:
        DataFrame con los datos
    """
    try:
        logger.info(f"Cargando datos desde: {filepath}")
        
        # Cargar con tipos de datos optimizados
        df = pd.read_csv(
            filepath,
            nrows=nrows,
            low_memory=False,
            encoding='utf-8'
        )
        
        logger.info(f"Datos cargados: {len(df)} registros, {len(df.columns)} columnas")
        return df
        
    except Exception as e:
        logger.error(f"Error al cargar datos: {str(e)}")
        raise
