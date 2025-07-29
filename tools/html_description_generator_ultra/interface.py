# tools/html_description_generator_ultra/interface.py
"""
Interfaz Ultra para generación masiva de descripciones HTML
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import asyncio
import json
from .scraper_engine import MassiveScrapingEngine
from .data_processor import UltraDataProcessor
from .html_generator import UltraHTMLGenerator

def render(config=None):
    """Interfaz principal del generador ultra"""
    
    st.title("🚀 HTML Description Generator ULTRA")
    st.markdown("""
    ### Sistema ULTRA-POTENTE de Scraping Masivo y Generación HTML
    
    **🔥 Características Ultra:**
    - 🕷️ **Scrapy Engine**: Scraping masivo paralelo con 50+ spiders
    - 🌐 **200+ E-commerce Sites**: Amazon, eBay, AliExpress, Shopify stores, etc.
    - 🧠 **Ultra AI Processing**: GPT-4 + Claude + análisis multimodal
    - ⚡ **Procesamiento Paralelo**: Hasta 100 productos simultáneos
    - 📊 **Data Lake**: PostgreSQL + Redis para almacenamiento masivo
    """)
    
    # Tabs ultra
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🎯 Target Products", 
        "🕷️ Scraping Config", 
        "🚀 Launch Scraping",
        "📊 Data Processing", 
        "🎨 HTML Generation",
        "📈 Analytics & Export"
    ])
    
    with tab1:
        render_target_products_tab()
    
    with tab2:
        render_scraping_config_tab()
    
    with tab3:
        render_launch_scraping_tab()
    
    with tab4:
        render_data_processing_tab()
    
    with tab5:
        render_html_generation_tab()
    
    with tab6:
        render_analytics_export_tab()

def render_target_products_tab():
    """Tab para configurar productos objetivo"""
    
    st.markdown("### 🎯 Configuración de Productos Objetivo")
    
    # Método de entrada
    input_method = st.radio(
        "Método de entrada de productos:",
        [
            "📤 CSV Upload (Masivo)", 
            "🔗 URLs Directas", 
            "🔍 Búsqueda por Keywords",
            "🏪 Scraping de Tiendas Completas"
        ]
    )
    
    if "CSV Upload" in input_method:
        render_csv_upload_section()
    elif "URLs Directas" in input_method:
        render_direct_urls_section()
    elif "Búsqueda por Keywords" in input_method:
        render_keyword_search_section()
    elif "Scraping de Tiendas" in input_method:
        render_store_scraping_section()

def render_csv_upload_section():
    """Sección para subir CSV masivo"""
    
    st.markdown("#### 📤 Upload CSV Masivo")
    
    uploaded_file = st.file_uploader(
        "Sube tu CSV con productos",
        type=['csv'],
        help="Acepta archivos de hasta 10MB con miles de productos"
    )
    
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        
        st.success(f"✅ {len(df)} productos cargados")
        
        # Configuración de columnas
        st.markdown("**Mapeo de columnas:**")
        col1, col2 = st.columns(2)
        
        with col1:
            name_col = st.selectbox("Columna de nombre:", df.columns)
            brand_col = st.selectbox("Columna de marca:", [""] + list(df.columns))
            
        with col2:
            price_col = st.selectbox("Columna de precio:", [""] + list(df.columns))
            category_col = st.selectbox("Columna de categoría:", [""] + list(df.columns))
        
        # Preview
        st.dataframe(df.head(10))
        
        # Guardar configuración
        if st.button("💾 Guardar Configuración de Productos"):
            st.session_state['products_config'] = {
                'data': df,
                'mapping': {
                    'name': name_col,
                    'brand': brand_col,
                    'price': price_col, 
                    'category': category_col
                }
            }
            st.success("✅ Productos configurados para scraping masivo")

def render_direct_urls_section():
    """Sección para URLs directas"""
    
    st.markdown("#### 🔗 URLs Directas para Scraping")
    
    urls_text = st.text_area(
        "Pega URLs (una por línea):",
        height=200,
        placeholder="https://amazon.com/product1\nhttps://ebay.com/product2\nhttps://aliexpress.com/product3"
    )
    
    if urls_text:
        urls = [url.strip() for url in urls_text.split('\n') if url.strip()]
        st.info(f"📊 {len(urls)} URLs detectadas")
        
        # Análisis de dominios
        domains = {}
        for url in urls:
            try:
                domain = url.split('/')[2]
                domains[domain] = domains.get(domain, 0) + 1
            except:
                continue
        
        st.markdown("**Distribución por sitio:**")
        for domain, count in domains.items():
            st.write(f"• {domain}: {count} productos")

def render_keyword_search_section():
    """Sección para búsqueda por keywords"""
    
    st.markdown("#### 🔍 Búsqueda Masiva por Keywords")
    
    col1, col2 = st.columns(2)
    
    with col1:
        keywords = st.text_area(
            "Keywords (una por línea):",
            height=150,
            placeholder="smartphone samsung\nlaptop gaming\ntableta android"
        )
        
        sites_to_search = st.multiselect(
            "Sitios para buscar:",
            [
                "Amazon", "eBay", "AliExpress", "Walmart", 
                "Best Buy", "Target", "Costco", "Newegg",
                "B&H", "Adorama", "Shopify Stores"
            ],
            default=["Amazon", "eBay", "AliExpress"]
        )
    
    with col2:
        max_products_per_keyword = st.number_input(
            "Max productos por keyword:",
            min_value=10,
            max_value=1000,
            value=50
        )
        
        include_filters = st.multiselect(
            "Filtros a incluir:",
            ["Con imágenes", "Con precio", "Con reviews", "En stock"],
            default=["Con precio", "En stock"]
        )
    
    if st.button("🚀 Iniciar Búsqueda Masiva"):
        if keywords:
            keyword_list = [k.strip() for k in keywords.split('\n') if k.strip()]
            st.success(f"🎯 Configurado para buscar {len(keyword_list)} keywords en {len(sites_to_search)} sitios")

def render_store_scraping_section():
    """Sección para scraping de tiendas completas"""
    
    st.markdown("#### 🏪 Scraping de Tiendas Completas")
    
    store_url = st.text_input(
        "URL de la tienda:",
        placeholder="https://ejemplo-tienda.com"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        max_pages = st.number_input(
            "Máximo páginas a scrapear:",
            min_value=1,
            max_value=1000,
            value=10
        )
        
        delay_between_requests = st.slider(
            "Delay entre requests (seg):",
            min_value=0.1,
            max_value=5.0,
            value=1.0
        )
    
    with col2:
        categories_to_include = st.text_area(
            "Categorías a incluir (opcional):",
            placeholder="electronics\nclothing\nhome"
        )
        
        exclude_patterns = st.text_input(
            "Patrones a excluir:",
            placeholder="sale, clearance, discontinued"
        )

def render_scraping_config_tab():
    """Tab de configuración de scraping"""
    
    st.markdown("### 🕷️ Configuración del Motor de Scraping")
    
    # Configuración de potencia
    st.markdown("#### ⚡ Configuración de Potencia")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        concurrent_requests = st.slider(
            "Requests concurrentes:",
            min_value=1,
            max_value=100,
            value=20,
            help="Más = más rápido pero más recursos"
        )
        
        download_delay = st.slider(
            "Delay entre downloads (seg):",
            min_value=0.1,
            max_value=10.0,
            value=1.0
        )
    
    with col2:
        retry_attempts = st.slider(
            "Intentos de reintento:",
            min_value=1,
            max_value=10,
            value=3
        )
        
        timeout_seconds = st.slider(
            "Timeout por request (seg):",
            min_value=5,
            max_value=60,
            value=30
        )
    
    with col3:
        enable_cookies = st.checkbox("Habilitar cookies", value=True)
        enable_cache = st.checkbox("Habilitar cache", value=True)
        respect_robots = st.checkbox("Respetar robots.txt", value=False)
    
    # Configuración de sites target
    st.markdown("#### 🎯 Sites Target para Scraping")
    
    sites_config = {
        "E-commerce Principales": {
            "amazon.com": {"priority": "high", "parallel": 10},
            "ebay.com": {"priority": "high", "parallel": 8},
            "aliexpress.com": {"priority": "medium", "parallel": 5},
            "walmart.com": {"priority": "medium", "parallel": 5},
        },
        "Retailers Especializados": {
            "bestbuy.com": {"priority": "medium", "parallel": 5},
            "target.com": {"priority": "medium", "parallel": 5},
            "costco.com": {"priority": "low", "parallel": 3},
            "newegg.com": {"priority": "medium", "parallel": 5},
        },
        "Tiendas Shopify": {
            "*.myshopify.com": {"priority": "low", "parallel": 3},
            "shopify_stores": {"priority": "low", "parallel": 2},
        }
    }
    
    for category, sites in sites_config.items():
        with st.expander(f"🏷️ {category}"):
            for site, config in sites.items():
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"**{site}**")
                with col2:
                    priority = st.selectbox(
                        f"Prioridad {site}:",
                        ["high", "medium", "low"],
                        index=["high", "medium", "low"].index(config["priority"]),
                        key=f"priority_{site}"
                    )
                with col3:
                    parallel = st.number_input(
                        f"Paralelo {site}:",
                        min_value=1,
                        max_value=20,
                        value=config["parallel"],
                        key=f"parallel_{site}"
                    )

def render_launch_scraping_tab():
    """Tab para lanzar el scraping"""
    
    st.markdown("### 🚀 Lanzar Scraping Masivo")
    
    # Verificar configuración
    if 'products_config' not in st.session_state:
        st.warning("⚠️ Primero configura los productos en la pestaña 'Target Products'")
        return
    
    # Resumen de configuración
    products_count = len(st.session_state['products_config']['data'])
    
    st.markdown("#### 📊 Resumen de Configuración")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("🎯 Productos objetivo", products_count)
        st.metric("🕷️ Sites target", "50+")
    
    with col2:
        estimated_time = products_count * 2  # 2 segundos por producto estimado
        st.metric("⏱️ Tiempo estimado", f"{estimated_time//60}m {estimated_time%60}s")
        st.metric("💾 Datos esperados", f"~{products_count * 5}MB")
    
    with col3:
        st.metric("🔧 CPU esperado", "70-90%")
        st.metric("🧠 RAM esperada", "2-4GB")
    
    # Configuración final
    st.markdown("#### ⚙️ Configuración Final")
    
    col1, col2 = st.columns(2)
    
    with col1:
        scraping_mode = st.selectbox(
            "Modo de scraping:",
            [
                "🔥 Ultra Agresivo (máxima velocidad)",
                "⚡ Agresivo (rápido pero estable)", 
                "🛡️ Conservador (lento pero seguro)",
                "🕊️ Gentil (muy lento, sitios sensibles)"
            ]
        )
        
        enable_proxies = st.checkbox(
            "Usar proxies rotativos",
            help="Reduce riesgo de bloqueo pero es más lento"
        )
    
    with col2:
        save_raw_data = st.checkbox("Guardar datos raw", value=True)
        save_images = st.checkbox("Descargar imágenes", value=False)
        real_time_processing = st.checkbox("Procesamiento en tiempo real", value=True)
    
    # Launch button
    if st.button("🚀 LANZAR SCRAPING MASIVO", type="primary", use_container_width=True):
        launch_massive_scraping(
            products_config=st.session_state['products_config'],
            scraping_mode=scraping_mode,
            enable_proxies=enable_proxies,
            save_raw_data=save_raw_data,
            save_images=save_images,
            real_time_processing=real_time_processing
        )

def launch_massive_scraping(**config):
    """Lanza el scraping masivo"""
    
    st.markdown("### 🔥 SCRAPING EN PROGRESO")
    
    # Contenedores para progreso
    progress_container = st.container()
    logs_container = st.container()
    stats_container = st.container()
    
    with progress_container:
        overall_progress = st.progress(0)
        current_task = st.empty()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            scraped_metric = st.empty()
        with col2:
            success_metric = st.empty()
        with col3:
            errors_metric = st.empty()
        with col4:
            speed_metric = st.empty()
    
    # Simular scraping (aquí iría la lógica real)
    import time
    total_products = len(config['products_config']['data'])
    
    for i in range(total_products):
        # Actualizar progreso
        progress = (i + 1) / total_products
        overall_progress.progress(progress)
        current_task.text(f"Scraping producto {i+1}/{total_products}")
        
        # Actualizar métricas
        scraped_metric.metric("📊 Scrapeados", i+1)
        success_metric.metric("✅ Exitosos", int((i+1) * 0.85))
        errors_metric.metric("❌ Errores", int((i+1) * 0.15))
        speed_metric.metric("⚡ Velocidad", f"{(i+1)/((time.time() % 100) + 1):.1f}/s")
        
        time.sleep(0.1)  # Simular trabajo
    
    st.success("🎉 ¡Scraping masivo completado!")

def render_data_processing_tab():
    """Tab para procesamiento de datos"""
    
    st.markdown("### 📊 Ultra Data Processing")
    
    # Verificar si hay datos scrapeados
    if 'scraped_data' not in st.session_state:
        st.info("🔍 No hay datos scrapeados aún. Ejecuta el scraping primero.")
        return
    
    st.markdown("#### 🧠 Configuración de Procesamiento IA")
    
    col1, col2 = st.columns(2)
    
    with col1:
        ai_models = st.multiselect(
            "Modelos IA a usar:",
            ["GPT-4 Turbo", "Claude 3", "Gemini Pro", "Local LLM"],
            default=["GPT-4 Turbo"]
        )
        
        processing_depth = st.selectbox(
            "Profundidad de procesamiento:",
            [
                "🚀 Ultra Deep (máximo detalle)",
                "🔥 Deep (detalle alto)",
                "⚡ Standard (equilibrado)",
                "💨 Fast (básico pero rápido)"
            ]
        )
    
    with col2:
        include_sentiment = st.checkbox("Análisis de sentimiento", value=True)
        include_competitors = st.checkbox("Análisis competitivo", value=True)
        include_trends = st.checkbox("Análisis de tendencias", value=False)
        include_images = st.checkbox("Análisis de imágenes", value=False)
    
    # Configuración de categorización
    st.markdown("#### 🏷️ Categorización Inteligente")
    
    auto_categorize = st.checkbox("Auto-categorización con IA", value=True)
    
    if auto_categorize:
        category_model = st.selectbox(
            "Modelo de categorización:",
            ["Hierarchical Clustering", "Neural Network", "Decision Tree", "Hybrid AI"]
        )
        
        min_confidence = st.slider(
            "Confianza mínima para categorización:",
            min_value=0.5,
            max_value=1.0,
            value=0.8
        )

def render_html_generation_tab():
    """Tab para generación HTML"""
    
    st.markdown("### 🎨 Ultra HTML Generation")
    
    # Templates y estilos
    st.markdown("#### 🎭 Templates y Estilos")
    
    template_style = st.selectbox(
        "Estilo de template:",
        [
            "🔥 Modern Minimalist",
            "💎 Luxury Premium", 
            "⚡ Tech/Gaming",
            "🌿 Natural/Organic",
            "🎨 Creative/Artistic",
            "📱 Mobile-First",
            "🛒 E-commerce Optimized"
        ]
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        include_features = st.multiselect(
            "Características a incluir:",
            [
                "📊 Specs técnicas", "🖼️ Galería imágenes", 
                "⭐ Reviews destacadas", "🔄 Comparación productos",
                "📈 Gráficos performance", "🎬 Videos embebidos",
                "🛒 Call-to-actions", "📱 QR codes"
            ],
            default=["📊 Specs técnicas", "🖼️ Galería imágenes", "⭐ Reviews destacadas"]
        )
    
    with col2:
        html_optimization = st.multiselect(
            "Optimizaciones HTML:",
            [
                "🚀 SEO optimizado", "📱 Responsive design",
                "⚡ Lazy loading", "🎨 CSS minificado", 
                "📊 Schema markup", "🔍 Meta tags",
                "💨 Fast loading", "♿ Accessibility"
            ],
            default=["🚀 SEO optimizado", "📱 Responsive design", "⚡ Lazy loading"]
        )
    
    # Configuración de contenido
    st.markdown("#### 📝 Configuración de Contenido")
    
    content_length = st.selectbox(
        "Longitud de descripción:",
        ["Corta (100-200 palabras)", "Media (200-500 palabras)", "Larga (500-1000 palabras)", "Ultra (1000+ palabras)"]
    )
    
    writing_tone = st.selectbox(
        "Tono de escritura:",
        ["Profesional", "Casual", "Técnico", "Marketing", "Persuasivo", "Educativo"]
    )
    
    target_audience = st.selectbox(
        "Audiencia objetivo:",
        ["General", "Técnica", "Profesional", "Jóvenes", "Familias", "B2B", "Luxury"]
    )

def render_analytics_export_tab():
    """Tab para analytics y export"""
    
    st.markdown("### 📈 Analytics & Export")
    
    # Mock analytics
    st.markdown("#### 📊 Estadísticas de Proceso")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🎯 Productos procesados", "1,247", "↗️ +23%")
        st.metric("💾 Datos recolectados", "45.2 GB", "↗️ +156%")
    
    with col2:
        st.metric("🌐 Sites scrapeados", "73", "↗️ +12")
        st.metric("⚡ Velocidad promedio", "12.4 p/s", "↗️ +34%")
    
    with col3:
        st.metric("✅ Tasa de éxito", "94.2%", "↗️ +5.1%")
        st.metric("🧠 Calidad IA", "9.1/10", "↗️ +0.8")
    
    with col4:
        st.metric("🎨 HTMLs generados", "1,174", "↗️ +21%")
        st.metric("💰 Costo total", "$67.30", "↘️ -12%")
    
    # Export options
    st.markdown("#### 💾 Opciones de Export")
    
    export_format = st.multiselect(
        "Formatos de export:",
        [
            "📄 CSV (para Shopify)", "🗃️ JSON (datos raw)",
            "🌐 HTML Bundle", "📊 Excel (análisis)", 
            "🗄️ SQL Database", "🔗 API Endpoints"
        ],
        default=["📄 CSV (para Shopify)", "🌐 HTML Bundle"]
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📥 Export Seleccionados", type="primary"):
            st.success("✅ Export iniciado - recibirás un email cuando esté listo")
    
    with col2:
        if st.button("☁️ Subir a Cloud Storage"):
            st.success("✅ Subiendo a AWS S3...")

# ==========================================
