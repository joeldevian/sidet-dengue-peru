"""
Script principal para descargar los datos del MINSA
"""

import sys
from pathlib import Path

# Agregar el directorio raíz al path
ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.append(str(ROOT_DIR))

from config import DATASET_URLS, RAW_DATA_DIR
from src.data.download_data import descargar_dataset_minsa

def main():
    """Descarga el dataset principal de dengue"""
    
    url = DATASET_URLS['principal']
    output_file = RAW_DATA_DIR / 'dengue_2000_2024.csv'
    
    print("=" * 60)
    print("DESCARGA DE DATOS - SIDET")
    print("=" * 60)
    print(f"\nDataset: Vigilancia Epidemiológica de Dengue")
    print(f"Período: 2000-2024")
    print(f"Fuente: MINSA - CDC Perú")
    print(f"\nDestino: {output_file}")
    print("\nIniciando descarga...\n")
    
    exito = descargar_dataset_minsa(url, output_file)
    
    if exito:
        print("\n✓ Descarga completada exitosamente")
        print(f"Archivo guardado en: {output_file}")
    else:
        print("\n✗ Error en la descarga")
        print("Verifica tu conexión a internet y la URL del dataset")
        sys.exit(1)

if __name__ == "__main__":
    main()
