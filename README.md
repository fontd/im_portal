# 🛒 Shopify Automation Platform

Un sistema completo de automatización para Shopify potenciado por IA, diseñado para optimizar y acelerar la gestión de productos.

## 🌟 Características Principales

### 🤖 Generador Premium de FAQs v3.0
- **Análisis profundo con IA**: Utiliza GPT-3.5 y GPT-4 para generar FAQs contextuales
- **Sistema anti-repetición**: Memoria persistente que evita preguntas duplicadas
- **8 categorías de preguntas**: Cobertura completa de todas las necesidades del cliente
- **Sistema de calidad**: Clasificación automática (LEGENDARIA > EXCEPCIONAL > EXCELENTE)
- **Perfiles de compradores**: Adapta las preguntas según diferentes tipos de clientes

### 📊 Análisis de Productos
- Análisis automático de datos de productos
- Identificación de patrones y tendencias
- Recomendaciones de optimización

### 🔮 Herramientas Futuras
- Generador de descripciones de productos
- Optimizador de SEO
- Análisis de competencia

## 🚀 Tecnologías

- **Frontend**: Streamlit
- **IA**: OpenAI GPT-3.5/GPT-4
- **Datos**: Pandas, NumPy
- **Containerización**: Docker
- **Lenguaje**: Python 3.8+

## 📋 Requisitos

- Python 3.8 o superior
- API Key de OpenAI
- Docker (opcional)

## 🛠️ Instalación

### Opción 1: Instalación Local

1. Clona el repositorio:
```bash
git clone https://github.com/tu-usuario/shopify-automation-platform.git
cd shopify-automation-platform
```

2. Instala las dependencias:
```bash
pip install -r requirements.txt
```

3. Configura las variables de entorno:
```bash
cp .env.example .env
# Edita .env y añade tu API Key de OpenAI
```

4. Ejecuta la aplicación:
```bash
streamlit run main.py
```

### Opción 2: Docker

1. Construye y ejecuta con Docker Compose:
```bash
docker-compose up --build
```

2. Accede a la aplicación en `http://localhost:8501`

## 📖 Uso

### Generador de FAQs

1. **Cargar productos**: Sube un archivo CSV con tus productos de Shopify
2. **Configurar IA**: Selecciona el modelo GPT y ajusta los parámetros
3. **Generar FAQs**: Ejecuta el proceso y descarga los resultados
4. **Importar a Shopify**: Usa el CSV generado para actualizar los metafields

#### Formato de CSV requerido:
```csv
Handle,Title,Body HTML,Variant Price,Vendor,Tags
producto-1,Serum Vitamina C,<p>Descripción...</p>,45.99,Marca,vitamina-c serum
```

## 🔧 Configuración

### Variables de Entorno
- `OPENAI_API_KEY`: Tu clave API de OpenAI
- `STREAMLIT_SERVER_PORT`: Puerto del servidor (opcional, por defecto 8501)

### Modelos Soportados
- `gpt-3.5-turbo`: Económico y rápido
- `gpt-4`: Máxima calidad (más costoso)
- `gpt-4-turbo-preview`: Equilibrio entre calidad y velocidad

## 📊 Características del Generador de FAQs

### Categorías de Preguntas
1. **Composición e ingredientes**
2. **Modo de uso y aplicación**
3. **Beneficios y resultados**
4. **Compatibilidad y combinaciones**
5. **Seguridad y contraindicaciones**
6. **Comparaciones y diferencias**
7. **Compra y garantías**
8. **Mantenimiento y conservación**

### Sistema de Calidad
- **LEGENDARIA** (18-20 puntos): Máxima calidad con detalles específicos
- **EXCEPCIONAL** (15-17 puntos): Alta calidad con información técnica
- **EXCELENTE** (12-14 puntos): Buena calidad con datos relevantes
- **BUENA** (9-11 puntos): Calidad estándar
- **ACEPTABLE** (6-8 puntos): Calidad mínima
- **INSUFICIENTE** (0-5 puntos): Requiere mejoras

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Añadir nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 🐛 Reportar Bugs

Si encuentras algún bug, por favor abre un issue en GitHub con:
- Descripción del problema
- Pasos para reproducirlo
- Logs de error (si los hay)
- Sistema operativo y versión de Python

---

⭐ Si este proyecto te es útil, ¡considera darle una estrella en GitHub!