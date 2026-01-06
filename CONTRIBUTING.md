# Contribuyendo a SIDET

¡Gracias por tu interés en contribuir al Sistema Inteligente de Detección Temprana de Dengue! 🦟

## 🌟 Cómo Contribuir

### Reportar Bugs

Si encuentras un bug, por favor abre un [Issue](https://github.com/tu-usuario/sidet-dengue-peru/issues) con:

- **Descripción clara** del problema
- **Pasos para reproducir** el error
- **Comportamiento esperado** vs comportamiento actual
- **Capturas de pantalla** si es aplicable
- **Entorno**: Sistema operativo, versión de Python, etc.

### Sugerir Mejoras

Para sugerir nuevas características:

1. Verifica que no exista un Issue similar
2. Abre un nuevo Issue con la etiqueta `enhancement`
3. Describe claramente la funcionalidad propuesta
4. Explica por qué sería útil para el proyecto

### Pull Requests

1. **Fork** el repositorio
2. **Crea una rama** desde `main`:
   ```bash
   git checkout -b feature/nueva-funcionalidad
   ```
3. **Realiza tus cambios** siguiendo las guías de estilo
4. **Agrega tests** si es aplicable
5. **Commit** tus cambios con mensajes descriptivos:
   ```bash
   git commit -m "feat: agregar modelo de predicción XGBoost mejorado"
   ```
6. **Push** a tu fork:
   ```bash
   git push origin feature/nueva-funcionalidad
   ```
7. **Abre un Pull Request** con descripción detallada

## 📝 Guías de Estilo

### Código Python

- Seguir [PEP 8](https://pep8.org/)
- Usar **type hints** cuando sea posible
- Documentar funciones con **docstrings**
- Nombres de variables en **español** para consistencia con el dominio
- Nombres de funciones en **snake_case**

Ejemplo:
```python
def calcular_z_score(casos_actuales: int, media_historica: float, 
                     desviacion_estandar: float) -> float:
    """
    Calcula el Z-Score para detección de anomalías.
    
    Args:
        casos_actuales: Número de casos en la semana actual
        media_historica: Media histórica de casos
        desviacion_estandar: Desviación estándar histórica
        
    Returns:
        Z-Score calculado
    """
    return (casos_actuales - media_historica) / desviacion_estandar
```

### Commits

Usar [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` Nueva funcionalidad
- `fix:` Corrección de bug
- `docs:` Cambios en documentación
- `style:` Formato, sin cambios de código
- `refactor:` Refactorización de código
- `test:` Agregar o modificar tests
- `chore:` Tareas de mantenimiento

### Documentación

- Actualizar `README.md` si cambias funcionalidad principal
- Actualizar `GUIA_USUARIO.md` si cambias el dashboard o UX
- Agregar comentarios en código complejo
- Documentar nuevos modelos o algoritmos

## 🧪 Testing

Antes de enviar un PR:

```bash
# Verificar sintaxis
python -m py_compile src/**/*.py

# Ejecutar tests (si existen)
pytest tests/

# Verificar que el dashboard funciona
streamlit run dashboard/app.py
```

## 🎯 Áreas de Contribución

### Prioridad Alta
- 🔴 Mejoras en modelos predictivos
- 🔴 Optimización de rendimiento
- 🔴 Tests unitarios y de integración

### Prioridad Media
- 🟡 Nuevas visualizaciones en el dashboard
- 🟡 Integración con APIs externas (clima, etc.)
- 🟡 Documentación y tutoriales

### Prioridad Baja
- 🟢 Mejoras de UI/UX
- 🟢 Traducciones
- 🟢 Ejemplos adicionales

## 📋 Checklist para Pull Requests

- [ ] El código sigue las guías de estilo del proyecto
- [ ] He realizado una auto-revisión de mi código
- [ ] He comentado el código en áreas complejas
- [ ] He actualizado la documentación correspondiente
- [ ] Mis cambios no generan nuevos warnings
- [ ] He agregado tests que prueban mi funcionalidad
- [ ] Los tests nuevos y existentes pasan localmente

## 🤝 Código de Conducta

### Nuestro Compromiso

Este proyecto se compromete a proporcionar un ambiente acogedor y libre de acoso para todos.

### Comportamiento Esperado

- Usar lenguaje acogedor e inclusivo
- Respetar diferentes puntos de vista
- Aceptar críticas constructivas
- Enfocarse en lo mejor para la comunidad

### Comportamiento Inaceptable

- Lenguaje o imágenes sexualizadas
- Comentarios insultantes o despectivos
- Acoso público o privado
- Publicar información privada de otros

## 📞 Contacto

Para preguntas sobre contribuciones:
- Abre un [Issue](https://github.com/tu-usuario/sidet-dengue-peru/issues)
- Discute en [Discussions](https://github.com/tu-usuario/sidet-dengue-peru/discussions)

---

¡Gracias por contribuir a mejorar la salud pública en Perú! 🇵🇪
