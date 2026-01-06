# Guía de Usuario - SIDET

## Sistema Inteligente de Detección Temprana de Dengue

---

## 📖 Introducción

SIDET es un sistema avanzado de detección temprana de brotes de dengue que utiliza inteligencia artificial y análisis estadístico para identificar patrones anómalos en las regiones endémicas del Perú.

---

## 🚀 Inicio Rápido

### Requisitos Previos
- Python 3.10 o superior
- Windows, Linux o macOS

### Instalación

1. **Clonar o descargar el proyecto**
```bash
cd c:\nebula\sidet_dengue_peru
```

2. **Activar entorno virtual**
```bash
# Windows
.\venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **Verificar instalación**
```bash
python --version
pip list
```

---

## 📊 Uso del Dashboard

### Iniciar el Dashboard

```bash
streamlit run dashboard\app.py
```

El dashboard se abrirá automáticamente en tu navegador en `http://localhost:8501`

### Características del Dashboard

#### 1. **Panel de Control (Sidebar)**
- **Filtro por Región**: Selecciona una región específica o "Todas"
- **Rango de Fechas**: Define el período de análisis
- **Niveles de Alerta**: Filtra por tipo de alerta (normal, bajo, medio, alto, crítico)

#### 2. **KPIs Principales**
- Total de Alertas
- Alertas Críticas
- Alertas Altas
- Casos Totales
- Promedio Semanal

#### 3. **Pestaña: Resumen**
- Distribución de alertas por nivel de riesgo
- Alertas por región
- Tabla detallada con estadísticas por región

#### 4. **Pestaña: Series Temporales**
- Gráfico de casos actuales vs media histórica
- Evolución de niveles de riesgo en el tiempo
- Visualización interactiva con zoom y hover

#### 5. **Pestaña: Mapa Regional**
- Resumen de alertas por región
- Visualización geográfica (en desarrollo)

#### 6. **Pestaña: Alertas Activas**
- Alertas de las últimas 4 semanas
- Destacado de alertas críticas
- Tabla completa con detalles

---

## 🔄 Flujo de Trabajo

### Procesamiento de Datos

1. **Descargar datos del MINSA**
```bash
python src\data\01_download_minsa_data.py
```

2. **Preprocesar datos**
```bash
python src\data\02_preprocess_data.py
```

3. **Generar visualizaciones**
```bash
python src\visualization\03_generate_visualizations.py
```

4. **Crear características**
```bash
python src\features\04_create_features.py
```

5. **Entrenar modelos**
```bash
python src\models\05_train_anomaly_models.py
```

6. **Generar alertas**
```bash
python src\models\06_generate_alerts.py
```

---

## 📁 Estructura de Archivos

### Datos Procesados
- `data/processed/dengue_limpio.csv` - Datos limpios
- `data/processed/dengue_semanal.csv` - Agregación semanal
- `data/processed/dengue_features.csv` - Con features ML
- `data/processed/dengue_alertas.csv` - Sistema de alertas
- `data/processed/alertas_activas.csv` - Alertas recientes

### Modelos
- `models/saved/anomaly_models.pkl` - Modelos entrenados
- `models/saved/anomaly_scalers.pkl` - Escaladores
- `models/saved/feature_columns.pkl` - Columnas de features

### Visualizaciones
- `reports/figures/*.png` - Gráficos generados

---

## 🎯 Interpretación de Resultados

### Niveles de Alerta

| Nivel | Color | Descripción | Acción Recomendada |
|-------|-------|-------------|-------------------|
| **Normal** | 🟢 Verde | Sin desviación significativa | Monitoreo rutinario |
| **Bajo** | 🟡 Amarillo | 1.5σ de desviación | Vigilancia aumentada |
| **Medio** | 🟠 Naranja | 2.0σ de desviación | Preparación de recursos |
| **Alto** | 🔴 Rojo | 2.5σ de desviación | Activación de protocolos |
| **Crítico** | 🟣 Morado | 3.0σ de desviación | Respuesta inmediata |

### Métricas Clave

- **Z-Score**: Número de desviaciones estándar respecto a la media histórica
- **Consenso de Modelos**: Cantidad de modelos ML que detectaron anomalía (0-3)
- **Porcentaje de Incremento**: Cambio respecto a la media histórica

---

## 🔧 Solución de Problemas

### El dashboard no inicia
```bash
# Verificar que Streamlit esté instalado
pip install streamlit

# Verificar que los datos existan
dir data\processed
```

### Errores de datos faltantes
```bash
# Ejecutar el pipeline completo desde el inicio
python src\data\01_download_minsa_data.py
python src\data\02_preprocess_data.py
# ... continuar con los demás scripts
```

### Modelos no encontrados
```bash
# Reentrenar los modelos
python src\models\05_train_anomaly_models.py
```

---

## 📞 Soporte

Para preguntas o problemas:
- **Desarrollador**: Joel
- **Fuente de Datos**: MINSA - CDC Perú
- **Documentación**: Ver `RESUMEN_EJECUTIVO.md`

---

## 📝 Notas Importantes

1. Los datos se actualizan semanalmente desde el MINSA
2. Los modelos deben reentrenarse periódicamente con nuevos datos
3. Las alertas son indicativas y deben complementarse con análisis epidemiológico
4. El sistema es una herramienta de apoyo, no reemplaza el criterio médico

---

**Última Actualización**: Diciembre 2025  
**Versión**: 1.0
