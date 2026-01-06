# 🚀 Guía de Despliegue - Dashboard SIDET

Esta guía te ayudará a desplegar el dashboard SIDET en **Streamlit Community Cloud** de forma gratuita.

---

## 📋 Requisitos Previos

- ✅ Cuenta de GitHub (ya tienes el repositorio)
- ✅ Repositorio público en GitHub: `https://github.com/joeldevian/sidet-dengue-peru`
- ✅ Cuenta de correo electrónico

---

## 🌐 Opción 1: Streamlit Community Cloud (Recomendado)

### Ventajas
- ✅ **100% Gratuito** para proyectos públicos
- ✅ **Integración directa** con GitHub
- ✅ **Despliegue automático** al hacer push
- ✅ **Dominio personalizado** (sidet-dengue-peru.streamlit.app)
- ✅ **Sin configuración de servidor**

### Limitaciones
- 1 GB de RAM
- Recursos compartidos (puede ser lento con muchos usuarios)
- Solo para repositorios públicos

---

## 🚀 Pasos para Desplegar en Streamlit Cloud

### 1. Crear Cuenta en Streamlit Cloud

1. Ve a: **https://share.streamlit.io/**
2. Click en **"Sign up"** o **"Get started"**
3. Selecciona **"Continue with GitHub"**
4. Autoriza a Streamlit a acceder a tu cuenta de GitHub
5. Completa tu perfil

### 2. Crear Nueva Aplicación

1. Una vez dentro, click en **"New app"**
2. Completa los siguientes campos:

   **Repository:**
   ```
   joeldevian/sidet-dengue-peru
   ```

   **Branch:**
   ```
   main
   ```

   **Main file path:**
   ```
   dashboard/app.py
   ```

   **App URL (opcional):**
   ```
   sidet-dengue-peru
   ```
   (Esto creará: `sidet-dengue-peru.streamlit.app`)

3. Click en **"Deploy!"**

### 3. Esperar el Despliegue

- El proceso tarda **2-5 minutos**
- Verás logs en tiempo real
- Si hay errores, aparecerán en los logs

### 4. Verificar el Dashboard

Una vez desplegado:
- ✅ Verifica que el dashboard carga correctamente
- ✅ Prueba los filtros y visualizaciones
- ✅ Comparte la URL pública

---

## 🔧 Configuración Adicional (Opcional)

### Secrets Management

Si necesitas variables de entorno o API keys:

1. En Streamlit Cloud, ve a tu app
2. Click en **"⋮"** (menú) → **"Settings"**
3. Ve a la sección **"Secrets"**
4. Agrega tus secrets en formato TOML:

```toml
# Ejemplo
API_KEY = "tu-api-key"
DATABASE_URL = "tu-database-url"
```

### Configuración de Recursos

Para optimizar el rendimiento:

1. Ve a **Settings** → **"Resources"**
2. Ajusta según necesites (limitado en plan gratuito)

---

## 📊 Datos para el Dashboard

### Opción A: Usar Datos de Ejemplo (Recomendado para Demo)

El dashboard está configurado para funcionar con datos de ejemplo incluidos en el repositorio:
- `data/processed/predictions/predicciones_2026_2028.csv`
- `data/processed/predictions/alertas_predictivas.csv`
- `data/processed/predictions/alertas_criticas_12_meses.csv`

### Opción B: Generar Datos Completos

Para generar todos los datos:

```bash
# 1. Descargar datos del MINSA
python src/data/01_download_minsa_data.py

# 2. Preprocesar
python src/data/02_preprocess_data.py

# 3. Crear features
python src/features/04_create_features.py

# 4. Entrenar modelos
python src/models/05_train_anomaly_models.py
python src/models/07_train_forecasting_models.py

# 5. Generar alertas y predicciones
python src/models/06_generate_alerts.py
python src/models/08_generate_predictions.py
python src/models/09_generate_predictive_alerts.py
```

**Nota:** Los archivos grandes de datos están en `.gitignore` y no se suben a GitHub.

---

## 🐛 Troubleshooting

### Error: "ModuleNotFoundError"

**Solución:** Verifica que todas las dependencias estén en `requirements.txt`

### Error: "FileNotFoundError"

**Solución:** El dashboard está configurado para manejar datos faltantes. Verifica que los archivos de predicciones existan en `data/processed/predictions/`

### Dashboard muy lento

**Solución:**
- Reduce el tamaño de los datos
- Usa caché de Streamlit (`@st.cache_data`)
- Considera actualizar a plan de pago

### Error de memoria (OOM)

**Solución:**
- Reduce el tamaño de los datos
- Optimiza el código para usar menos memoria
- Considera desplegar en otra plataforma con más recursos

---

## 🔄 Actualizar el Dashboard

El dashboard se actualiza automáticamente cuando haces push a GitHub:

```bash
# 1. Hacer cambios en el código
git add .
git commit -m "feat: actualizar dashboard"
git push origin main

# 2. Streamlit Cloud detectará los cambios y re-desplegará automáticamente
```

---

## 🌟 Alternativas de Despliegue

### Opción 2: Render.com

**Ventajas:**
- Plan gratuito disponible
- Más recursos que Streamlit Cloud
- Soporte para múltiples frameworks

**Pasos:**
1. Crear cuenta en https://render.com
2. Crear nuevo "Web Service"
3. Conectar con GitHub
4. Configurar:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `streamlit run dashboard/app.py --server.port=$PORT --server.address=0.0.0.0`

### Opción 3: Hugging Face Spaces

**Ventajas:**
- Comunidad de ML/AI
- Integración con modelos de Hugging Face
- Gratuito para proyectos públicos

**Pasos:**
1. Crear cuenta en https://huggingface.co
2. Crear nuevo "Space"
3. Seleccionar "Streamlit" como SDK
4. Subir archivos o conectar con GitHub

### Opción 4: Railway.app

**Ventajas:**
- $5 de crédito gratis mensual
- Fácil configuración
- Buena documentación

**Pasos:**
1. Crear cuenta en https://railway.app
2. Crear nuevo proyecto desde GitHub
3. Railway detectará automáticamente Streamlit

---

## 📝 Checklist de Despliegue

- [ ] Cuenta de Streamlit Cloud creada
- [ ] Repositorio conectado
- [ ] Aplicación desplegada
- [ ] Dashboard funciona correctamente
- [ ] URL pública verificada
- [ ] README actualizado con link de demo
- [ ] Compartir con usuarios

---

## 🎯 Próximos Pasos

1. **Compartir la URL:**
   - Agrega el link en el README
   - Comparte en redes sociales
   - Presenta a stakeholders

2. **Monitorear:**
   - Revisa logs regularmente
   - Monitorea uso de recursos
   - Recopila feedback de usuarios

3. **Optimizar:**
   - Mejora rendimiento basado en uso real
   - Agrega nuevas funcionalidades
   - Actualiza datos regularmente

---

## 📞 Soporte

**Streamlit Community Cloud:**
- Documentación: https://docs.streamlit.io/streamlit-community-cloud
- Foro: https://discuss.streamlit.io/
- GitHub Issues: https://github.com/streamlit/streamlit/issues

**SIDET:**
- Issues: https://github.com/joeldevian/sidet-dengue-peru/issues

---

## 🎉 ¡Listo!

Tu dashboard SIDET ahora está disponible públicamente para ayudar en la detección temprana de dengue en Perú. 🦟🇵🇪

**URL de ejemplo:** `https://sidet-dengue-peru.streamlit.app`
