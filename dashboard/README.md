# Ejecutar el dashboard de Streamlit

Para iniciar el dashboard, ejecuta:

```bash
streamlit run dashboard\app.py
```

El dashboard estará disponible en: http://localhost:8501

## Características del Dashboard

- **KPIs en tiempo real**: Total de alertas, alertas críticas, casos totales
- **Filtros interactivos**: Por región, rango de fechas y nivel de alerta
- **4 pestañas principales**:
  1. Resumen: Distribución de alertas y reporte por región
  2. Series Temporales: Gráficos de evolución de casos
  3. Mapa Regional: Visualización geográfica
  4. Alertas Activas: Alertas de las últimas 4 semanas

## Navegación

- Use la barra lateral para filtrar datos
- Explore las diferentes pestañas para ver distintas visualizaciones
- Las alertas críticas se destacan en rojo
