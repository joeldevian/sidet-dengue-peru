"""
Sistema de Alertas Temprana para Dengue
Clasifica el nivel de riesgo y genera alertas automáticas
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import logging
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AlertSystem:
    """Sistema de alertas temprana para detección de brotes de dengue"""
    
    def __init__(self, umbrales: Dict = None):
        """
        Inicializa el sistema de alertas
        
        Args:
            umbrales: Diccionario con umbrales personalizados
        """
        # Umbrales por defecto (en desviaciones estándar)
        self.umbrales = umbrales or {
            'bajo': 1.5,
            'medio': 2.0,
            'alto': 2.5,
            'critico': 3.0
        }
        
        # Colores para visualización
        self.colores = {
            'normal': '#2ecc71',
            'bajo': '#f1c40f',
            'medio': '#e67e22',
            'alto': '#e74c3c',
            'critico': '#8e44ad'
        }
    
    def calcular_nivel_riesgo_estadistico(self, casos_actual: float, 
                                         media_historica: float,
                                         std_historica: float) -> Tuple[str, float]:
        """
        Calcula el nivel de riesgo basado en desviaciones estándar
        
        Args:
            casos_actual: Número de casos actual
            media_historica: Media histórica
            std_historica: Desviación estándar histórica
            
        Returns:
            Tupla (nivel_riesgo, z_score)
        """
        # Calcular z-score
        if std_historica == 0:
            z_score = 0
        else:
            z_score = (casos_actual - media_historica) / std_historica
        
        # Clasificar nivel de riesgo
        if z_score >= self.umbrales['critico']:
            nivel = 'critico'
        elif z_score >= self.umbrales['alto']:
            nivel = 'alto'
        elif z_score >= self.umbrales['medio']:
            nivel = 'medio'
        elif z_score >= self.umbrales['bajo']:
            nivel = 'bajo'
        else:
            nivel = 'normal'
        
        return nivel, z_score
    
    def calcular_nivel_riesgo_anomalia(self, anomalia_if: int, anomalia_lof: int,
                                      anomalia_ocsvm: int, score_if: float = None) -> Tuple[str, int]:
        """
        Calcula el nivel de riesgo basado en detección de anomalías
        
        Args:
            anomalia_if: Anomalía detectada por Isolation Forest (0/1)
            anomalia_lof: Anomalía detectada por LOF (0/1)
            anomalia_ocsvm: Anomalía detectada por One-Class SVM (0/1)
            score_if: Score de Isolation Forest (opcional)
            
        Returns:
            Tupla (nivel_riesgo, consenso)
        """
        # Contar cuántos modelos detectaron anomalía
        consenso = anomalia_if + anomalia_lof + anomalia_ocsvm
        
        # Clasificar según consenso
        if consenso == 3:
            nivel = 'critico'  # Los 3 modelos coinciden
        elif consenso == 2:
            nivel = 'alto'  # 2 de 3 modelos coinciden
        elif consenso == 1:
            nivel = 'medio'  # Solo 1 modelo detectó anomalía
        else:
            nivel = 'normal'  # Ningún modelo detectó anomalía
        
        return nivel, consenso
    
    def calcular_nivel_riesgo_combinado(self, casos_actual: float,
                                       media_historica: float,
                                       std_historica: float,
                                       anomalia_if: int = 0,
                                       anomalia_lof: int = 0,
                                       anomalia_ocsvm: int = 0) -> Dict:
        """
        Calcula el nivel de riesgo combinando métodos estadísticos y ML
        
        Args:
            casos_actual: Número de casos actual
            media_historica: Media histórica
            std_historica: Desviación estándar histórica
            anomalia_if: Anomalía Isolation Forest
            anomalia_lof: Anomalía LOF
            anomalia_ocsvm: Anomalía One-Class SVM
            
        Returns:
            Diccionario con información de riesgo
        """
        # Método estadístico
        nivel_estadistico, z_score = self.calcular_nivel_riesgo_estadistico(
            casos_actual, media_historica, std_historica
        )
        
        # Método de anomalías
        nivel_anomalia, consenso = self.calcular_nivel_riesgo_anomalia(
            anomalia_if, anomalia_lof, anomalia_ocsvm
        )
        
        # Combinar ambos métodos (tomar el más severo)
        niveles_orden = ['normal', 'bajo', 'medio', 'alto', 'critico']
        idx_estadistico = niveles_orden.index(nivel_estadistico)
        idx_anomalia = niveles_orden.index(nivel_anomalia)
        
        nivel_final = niveles_orden[max(idx_estadistico, idx_anomalia)]
        
        return {
            'nivel_riesgo': nivel_final,
            'nivel_estadistico': nivel_estadistico,
            'nivel_anomalia': nivel_anomalia,
            'z_score': z_score,
            'consenso_modelos': consenso,
            'casos_actual': casos_actual,
            'media_historica': media_historica,
            'desviacion_media': casos_actual - media_historica,
            'porcentaje_incremento': ((casos_actual - media_historica) / media_historica * 100) if media_historica > 0 else 0
        }
    
    def generar_alertas(self, df: pd.DataFrame, 
                       col_casos: str = 'casos',
                       col_departamento: str = 'departamento',
                       col_fecha: str = 'fecha',
                       ventana_historica: int = 52) -> pd.DataFrame:
        """
        Genera alertas para todo el dataset
        
        Args:
            df: DataFrame con datos y anomalías detectadas
            col_casos: Columna de casos
            col_departamento: Columna de departamento
            col_fecha: Columna de fecha
            ventana_historica: Semanas para calcular media histórica
            
        Returns:
            DataFrame con alertas generadas
        """
        logger.info("Generando alertas...")
        
        df_alertas = df.copy()
        df_alertas[col_fecha] = pd.to_datetime(df_alertas[col_fecha])
        
        # Calcular estadísticas históricas por región
        df_alertas['media_historica'] = df_alertas.groupby(col_departamento)[col_casos].transform(
            lambda x: x.rolling(window=ventana_historica, min_periods=1).mean().shift(1)
        )
        
        df_alertas['std_historica'] = df_alertas.groupby(col_departamento)[col_casos].transform(
            lambda x: x.rolling(window=ventana_historica, min_periods=1).std().shift(1)
        )
        
        # Inicializar columnas de alerta
        alertas = []
        
        for idx, row in df_alertas.iterrows():
            # Obtener valores de anomalías si existen
            anomalia_if = row.get('anomalia_if', 0)
            anomalia_lof = row.get('anomalia_lof', 0)
            anomalia_ocsvm = row.get('anomalia_ocsvm', 0)
            
            # Calcular nivel de riesgo
            info_riesgo = self.calcular_nivel_riesgo_combinado(
                casos_actual=row[col_casos],
                media_historica=row['media_historica'],
                std_historica=row['std_historica'],
                anomalia_if=anomalia_if,
                anomalia_lof=anomalia_lof,
                anomalia_ocsvm=anomalia_ocsvm
            )
            
            alertas.append(info_riesgo)
        
        # Agregar información de alertas al DataFrame
        alertas_df = pd.DataFrame(alertas)
        df_resultado = pd.concat([df_alertas.reset_index(drop=True), alertas_df], axis=1)
        
        logger.info(f"✓ Alertas generadas: {len(df_resultado):,} registros")
        
        return df_resultado
    
    def filtrar_alertas_activas(self, df_alertas: pd.DataFrame,
                               niveles_minimos: List[str] = ['medio', 'alto', 'critico'],
                               col_fecha: str = 'fecha',
                               ultimas_semanas: int = 4) -> pd.DataFrame:
        """
        Filtra alertas activas recientes
        
        Args:
            df_alertas: DataFrame con alertas
            niveles_minimos: Niveles mínimos a incluir
            col_fecha: Columna de fecha
            ultimas_semanas: Número de semanas recientes a considerar
            
        Returns:
            DataFrame con alertas activas
        """
        df_alertas[col_fecha] = pd.to_datetime(df_alertas[col_fecha])
        
        # Filtrar por nivel de riesgo
        df_filtrado = df_alertas[df_alertas['nivel_riesgo'].isin(niveles_minimos)].copy()
        
        # Filtrar por fecha reciente
        fecha_limite = df_alertas[col_fecha].max() - timedelta(weeks=ultimas_semanas)
        df_filtrado = df_filtrado[df_filtrado[col_fecha] >= fecha_limite]
        
        # Ordenar por nivel de riesgo y fecha
        orden_niveles = {'critico': 0, 'alto': 1, 'medio': 2, 'bajo': 3, 'normal': 4}
        df_filtrado['orden_riesgo'] = df_filtrado['nivel_riesgo'].map(orden_niveles)
        df_filtrado = df_filtrado.sort_values(['orden_riesgo', col_fecha], ascending=[True, False])
        df_filtrado = df_filtrado.drop('orden_riesgo', axis=1)
        
        logger.info(f"Alertas activas encontradas: {len(df_filtrado)}")
        
        return df_filtrado
    
    def generar_reporte_alertas(self, df_alertas: pd.DataFrame,
                               col_departamento: str = 'departamento') -> pd.DataFrame:
        """
        Genera reporte resumen de alertas por región
        
        Args:
            df_alertas: DataFrame con alertas
            col_departamento: Columna de departamento
            
        Returns:
            DataFrame con resumen por región
        """
        logger.info("Generando reporte de alertas...")
        
        resumen = []
        
        for region in df_alertas[col_departamento].unique():
            df_region = df_alertas[df_alertas[col_departamento] == region]
            
            # Contar alertas por nivel
            conteo_niveles = df_region['nivel_riesgo'].value_counts()
            
            resumen.append({
                'region': region,
                'total_registros': len(df_region),
                'alertas_criticas': conteo_niveles.get('critico', 0),
                'alertas_altas': conteo_niveles.get('alto', 0),
                'alertas_medias': conteo_niveles.get('medio', 0),
                'alertas_bajas': conteo_niveles.get('bajo', 0),
                'casos_promedio': df_region['casos_actual'].mean(),
                'casos_maximo': df_region['casos_actual'].max(),
                'z_score_promedio': df_region['z_score'].mean(),
                'z_score_maximo': df_region['z_score'].max()
            })
        
        df_resumen = pd.DataFrame(resumen)
        df_resumen = df_resumen.sort_values('alertas_criticas', ascending=False)
        
        logger.info("✓ Reporte generado")
        
        return df_resumen


    # ============================================
    # SISTEMA DE ALERTAS PREDICTIVAS
    # ============================================
    
    def calcular_nivel_riesgo_predictivo(self, casos_predichos: float,
                                         media_historica: float) -> Tuple[str, float]:
        """
        Calcula el nivel de riesgo predictivo basado en incremento esperado
        
        Args:
            casos_predichos: Número de casos predichos
            media_historica: Media histórica de la región
            
        Returns:
            Tupla (nivel_riesgo, porcentaje_incremento)
        """
        if media_historica == 0:
            porcentaje_incremento = 0
        else:
            porcentaje_incremento = (casos_predichos - media_historica) / media_historica
        
        # Clasificar según incremento esperado
        if porcentaje_incremento > 1.0:  # >100% incremento
            nivel = 'critico'
        elif porcentaje_incremento > 0.60:  # 60-100% incremento
            nivel = 'alerta_temprana'
        elif porcentaje_incremento > 0.30:  # 30-60% incremento
            nivel = 'preparacion'
        elif porcentaje_incremento > 0.10:  # 10-30% incremento
            nivel = 'vigilancia'
        else:  # <10% incremento
            nivel = 'normal'
        
        return nivel, porcentaje_incremento
    
    def generar_alertas_predictivas(self, df_predicciones: pd.DataFrame,
                                    df_historico: pd.DataFrame,
                                    col_casos_pred: str = 'casos_predichos_ensamble',
                                    col_region: str = 'region',
                                    col_fecha: str = 'fecha') -> pd.DataFrame:
        """
        Genera alertas predictivas basadas en predicciones futuras
        
        Args:
            df_predicciones: DataFrame con predicciones futuras
            df_historico: DataFrame con datos históricos
            col_casos_pred: Columna con casos predichos
            col_region: Columna de región
            col_fecha: Columna de fecha
            
        Returns:
            DataFrame con alertas predictivas
        """
        logger.info("Generando alertas predictivas...")
        
        df_pred = df_predicciones.copy()
        df_pred[col_fecha] = pd.to_datetime(df_pred[col_fecha])
        
        # Calcular media histórica por región
        medias_historicas = df_historico.groupby('departamento')['casos'].mean().to_dict()
        
        # Generar alertas
        alertas_predictivas = []
        
        for idx, row in df_pred.iterrows():
            region = row[col_region]
            casos_pred = row[col_casos_pred]
            fecha = row[col_fecha]
            
            # Obtener media histórica
            media_hist = medias_historicas.get(region, casos_pred)
            
            # Calcular nivel de riesgo
            nivel, incremento = self.calcular_nivel_riesgo_predictivo(casos_pred, media_hist)
            
            # Calcular intervalo de confianza si existe
            lower = row.get('intervalo_inferior_95', casos_pred * 0.85)
            upper = row.get('intervalo_superior_95', casos_pred * 1.15)
            
            alertas_predictivas.append({
                'region': region,
                'fecha': fecha,
                'año': fecha.year,
                'mes': fecha.month,
                'semana': fecha.isocalendar().week,
                'casos_predichos': casos_pred,
                'media_historica': media_hist,
                'incremento_esperado': incremento,
                'porcentaje_incremento': incremento * 100,
                'nivel_riesgo_predictivo': nivel,
                'intervalo_inferior': lower,
                'intervalo_superior': upper,
                'rango_incertidumbre': upper - lower
            })
        
        df_alertas = pd.DataFrame(alertas_predictivas)
        
        logger.info(f"✓ Alertas predictivas generadas: {len(df_alertas):,} registros")
        
        # Resumen por nivel de riesgo
        resumen = df_alertas['nivel_riesgo_predictivo'].value_counts()
        logger.info(f"Distribución de alertas:")
        for nivel, count in resumen.items():
            logger.info(f"  - {nivel}: {count} ({count/len(df_alertas)*100:.1f}%)")
        
        return df_alertas
    
    def filtrar_alertas_predictivas_criticas(self, df_alertas_pred: pd.DataFrame,
                                             niveles_criticos: List[str] = ['alerta_temprana', 'critico'],
                                             meses_adelante: int = 12) -> pd.DataFrame:
        """
        Filtra alertas predictivas críticas en los próximos meses
        
        Args:
            df_alertas_pred: DataFrame con alertas predictivas
            niveles_criticos: Niveles de riesgo a incluir
            meses_adelante: Número de meses hacia adelante a considerar
            
        Returns:
            DataFrame con alertas críticas
        """
        df_filtrado = df_alertas_pred[
            df_alertas_pred['nivel_riesgo_predictivo'].isin(niveles_criticos)
        ].copy()
        
        # Filtrar por horizonte temporal
        fecha_limite = df_alertas_pred['fecha'].min() + pd.DateOffset(months=meses_adelante)
        df_filtrado = df_filtrado[df_filtrado['fecha'] <= fecha_limite]
        
        # Ordenar por nivel de riesgo y fecha
        orden_niveles = {
            'critico': 0,
            'alerta_temprana': 1,
            'preparacion': 2,
            'vigilancia': 3,
            'normal': 4
        }
        df_filtrado['orden_riesgo'] = df_filtrado['nivel_riesgo_predictivo'].map(orden_niveles)
        df_filtrado = df_filtrado.sort_values(['orden_riesgo', 'fecha'], ascending=[True, True])
        df_filtrado = df_filtrado.drop('orden_riesgo', axis=1)
        
        logger.info(f"Alertas predictivas críticas (próximos {meses_adelante} meses): {len(df_filtrado)}")
        
        return df_filtrado
    
    def generar_recomendaciones_predictivas(self, nivel_riesgo: str) -> Dict[str, List[str]]:
        """
        Genera recomendaciones según el nivel de riesgo predictivo
        
        Args:
            nivel_riesgo: Nivel de riesgo ('normal', 'vigilancia', 'preparacion', 'alerta_temprana', 'critico')
            
        Returns:
            Diccionario con recomendaciones
        """
        recomendaciones = {
            'normal': {
                'acciones': [
                    'Mantener vigilancia epidemiológica rutinaria',
                    'Continuar con campañas de prevención estándar',
                    'Monitorear indicadores entomológicos'
                ],
                'prioridad': 'Baja',
                'tiempo_anticipacion': 'N/A'
            },
            'vigilancia': {
                'acciones': [
                    'Intensificar vigilancia epidemiológica',
                    'Reforzar campañas de eliminación de criaderos',
                    'Preparar stock de insumos médicos',
                    'Capacitar personal de salud'
                ],
                'prioridad': 'Media',
                'tiempo_anticipacion': '3-6 meses'
            },
            'preparacion': {
                'acciones': [
                    'Activar plan de contingencia',
                    'Realizar fumigación preventiva en zonas de riesgo',
                    'Aumentar stock de pruebas diagnósticas',
                    'Coordinar con hospitales para ampliar capacidad',
                    'Intensificar campañas de comunicación a la población'
                ],
                'prioridad': 'Alta',
                'tiempo_anticipacion': '2-4 meses'
            },
            'alerta_temprana': {
                'acciones': [
                    'Implementar plan de contingencia completo',
                    'Fumigación masiva en áreas identificadas',
                    'Movilizar brigadas de salud',
                    'Establecer centros de atención temporal',
                    'Declarar alerta sanitaria regional',
                    'Coordinar con autoridades locales y nacionales'
                ],
                'prioridad': 'Muy Alta',
                'tiempo_anticipacion': '1-3 meses'
            },
            'critico': {
                'acciones': [
                    'Declarar emergencia sanitaria',
                    'Movilización total de recursos',
                    'Implementar cerco epidemiológico',
                    'Activar hospitales de campaña',
                    'Solicitar apoyo nacional e internacional',
                    'Fumigación ultra-localizada inmediata',
                    'Comunicación de crisis a la población'
                ],
                'prioridad': 'Crítica',
                'tiempo_anticipacion': '0-2 meses'
            }
        }
        
        return recomendaciones.get(nivel_riesgo, recomendaciones['normal'])
