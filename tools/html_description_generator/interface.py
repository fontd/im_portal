# tools/html_description_generator/interface.py
import streamlit as st
import pandas as pd
from datetime import datetime
from .processor import (
    process_descriptions_streamlit,
    create_download_files,
    create_zip_download,
    validar_csv_productos,
    estimar_tiempo_procesamiento,
    obtener_muestra_productos
)

def render(config=None):
    """Función principal para renderizar la interfaz de generación HTML"""
    
    st.title("🧪 Generador de Descripciones HTML para Cosmética")
    st.markdown("---")
    
    # Crear pestañas
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📤 Cargar Productos", 
        "⚙️ Configuración", 
        "🚀 Generar Descripciones",
        "🧪 Probar Producto Individual",  # Nueva pestaña
        "📊 Resultados"
    ])
    
    with tab1:
        render_upload_tab()
    
    with tab2:
        render_config_tab()
    
    with tab3:
        render_generation_tab()
    
    with tab4:
        render_test_individual_tab()  # Nueva función
    
    with tab5:
        render_results_tab()

def render_upload_tab():
    """Tab para cargar productos"""
    
    st.markdown("### Paso 1: Cargar archivo CSV de productos")
    
    # Mostrar formato esperado
    with st.expander("📋 Ver formato esperado del CSV"):
        st.markdown("""
        **Columnas requeridas:**
        - `Handle`: Identificador único del producto
        - `Title`: Nombre del producto
        
        **Columnas recomendadas:**
        - `Vendor`: Marca/Fabricante
        - `Variant Price`: Precio del producto
        - `Tags`: Etiquetas del producto
        """)
        
        # Ejemplo
        ejemplo_df = pd.DataFrame({
            'Handle': ['smartphone-samsung-s24', 'laptop-macbook-pro'],
            'Title': ['Samsung Galaxy S24 Ultra', 'MacBook Pro 14" M3'],
            'Vendor': ['Samsung', 'Apple'],
            'Variant Price': [1199.99, 2299.99],
            'Tags': ['smartphone, android, premium', 'laptop, apple, professional']
        })
        st.dataframe(ejemplo_df)
    
    # Upload de archivo
    uploaded_file = st.file_uploader(
        "Selecciona tu archivo CSV",
        type=['csv'],
        help="El archivo debe estar en formato CSV con codificación UTF-8"
    )
    
    if uploaded_file is not None:
        try:
            # Leer CSV
            df = pd.read_csv(uploaded_file, encoding='utf-8')
            
            # Validar formato
            es_valido, mensaje = validar_csv_productos(df)
            
            if es_valido:
                st.success(mensaje)
                
                # Guardar en session state
                st.session_state['productos_df'] = df
                st.session_state['archivo_nombre'] = uploaded_file.name
                
                # Mostrar resumen
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total de productos", len(df))
                with col2:
                    marcas_unicas = df['Vendor'].nunique() if 'Vendor' in df.columns else 'N/A'
                    st.metric("Marcas únicas", marcas_unicas)
                with col3:
                    precio_promedio = f"${df['Variant Price'].mean():.2f}" if 'Variant Price' in df.columns else 'N/A'
                    st.metric("Precio promedio", precio_promedio)
                
                # Mostrar muestra
                st.markdown("### 👀 Vista previa de productos")
                muestra_df = obtener_muestra_productos(df, n=3)
                st.dataframe(muestra_df, use_container_width=True)
                
            else:
                st.error(mensaje)
                
        except Exception as e:
            st.error(f"Error al leer el archivo: {str(e)}")
            st.markdown("**Sugerencias:**")
            st.markdown("- Asegúrate de que el archivo esté en formato CSV")
            st.markdown("- Verifica que use codificación UTF-8")
            st.markdown("- Revisa que tenga las columnas requeridas")

def render_config_tab():
    """Tab de configuración"""
    
    st.markdown("### ⚙️ Configuración de generación")
    
    # API Key del sidebar
    sidebar_api_key = st.session_state.get('sidebar_config', {}).get('api_key', '')
    
    if sidebar_api_key:
        st.success("✅ API Key configurada desde la barra lateral")
        st.session_state['openai_api_key'] = sidebar_api_key
    else:
        st.warning("⚠️ Configura tu API Key en la barra lateral")
        st.session_state['openai_api_key'] = ""
    
    # Método de búsqueda
    st.markdown("### 🔍 Método de búsqueda")
    
    metodo = st.radio(
        "Selecciona el método de obtención de información:",
        ["🌐 Búsqueda automática en web", "📝 URLs específicas (manual)"],
        help="Automática busca info en web, Manual usa URLs que proporcionas"
    )
    
    st.session_state['metodo_seleccionado'] = "auto" if "automática" in metodo.lower() else "manual"
    
    # Configuración según método
    if st.session_state['metodo_seleccionado'] == "auto":
        st.info("🤖 El sistema buscará automáticamente información del producto en múltiples fuentes web")
        
        col1, col2 = st.columns(2)
        with col1:
            categoria_global = st.selectbox(
                "Categoría global (opcional)",
                ["", "smartphone", "laptop", "tablet", "auriculares", "smartwatch", 
                 "camara", "gaming", "hogar-inteligente", "electrodomesticos", "otro"],
                help="Categoría para mejorar la búsqueda"
            )
            st.session_state['categoria_global'] = categoria_global
        
        with col2:
            terminos_adicionales = st.text_input(
                "Términos adicionales de búsqueda",
                placeholder="especificaciones, review, precio...",
                help="Términos extra para la búsqueda web"
            )
            st.session_state['terminos_adicionales'] = terminos_adicionales
    
    else:  # Manual
        st.info("📝 Proporciona 2-3 URLs de donde extraer información del producto")
        
        # URLs manuales
        st.markdown("**URLs de fuentes:**")
        
        if 'urls_manuales' not in st.session_state:
            st.session_state['urls_manuales'] = ["", "", ""]
        
        urls_actualizadas = []
        for i in range(3):
            url = st.text_input(
                f"URL {i+1}",
                value=st.session_state['urls_manuales'][i],
                placeholder=f"https://ejemplo.com/producto-{i+1}",
                key=f"url_{i}"
            )
            urls_actualizadas.append(url)
        
        st.session_state['urls_manuales'] = urls_actualizadas
        
        # Mostrar URLs válidas
        urls_validas = [url for url in urls_actualizadas if url.strip() and url.startswith('http')]
        if urls_validas:
            st.success(f"✅ {len(urls_validas)} URLs válidas configuradas")
        else:
            st.warning("⚠️ No hay URLs válidas configuradas")
    
    # Configuración de estilo
    st.markdown("### 🎨 Configuración de estilo")
    
    col1, col2 = st.columns(2)
    
    with col1:
        estilo = st.selectbox(
            "Estilo de descripción",
            [
                "completa", 
                "marketing", 
                "tecnica", 
                "ecommerce", 
                "comparativa"
            ],
            format_func=lambda x: {
                "completa": "📄 Completa - Información detallada y profesional",
                "marketing": "🎯 Marketing - Enfocada en ventas y conversión", 
                "tecnica": "⚙️ Técnica - Especificaciones y datos técnicos",
                "ecommerce": "🛒 E-commerce - Optimizada para tienda online",
                "comparativa": "📊 Comparativa - Destaca vs competencia"
            }[x],
            help="Cada estilo tiene diferente enfoque y estructura"
        )
        st.session_state['estilo_seleccionado'] = estilo
    
    with col2:
        idioma = st.selectbox(
            "Idioma de generación",
            ["es", "en", "ca"],
            format_func=lambda x: {"es": "🇪🇸 Español", "en": "🇬🇧 English", "ca": "🇪🇸 Català"}[x],
            help="Idioma en el que se generará la descripción"
        )
        st.session_state['idioma_seleccionado'] = idioma
    
    # Preview del estilo seleccionado
    with st.expander(f"👀 Vista previa del estilo '{estilo.title()}'"):
        mostrar_preview_estilo(estilo)
    
    # Estimación de tiempo y costo  
    if 'productos_df' in st.session_state and sidebar_api_key:
        st.markdown("### 💰 Estimación de recursos")
        
        df = st.session_state['productos_df']
        n_productos = len(df)
        metodo_est = st.session_state.get('metodo_seleccionado', 'auto')
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            tiempo_estimado = estimar_tiempo_procesamiento(n_productos, metodo_est)
            st.metric("⏱️ Tiempo estimado", tiempo_estimado)
        
        with col2:
            # Estimación de costo (aproximada)
            tokens_por_producto = 1500 if metodo_est == "auto" else 1000
            costo_estimado = n_productos * tokens_por_producto * 0.00003  # Precio aproximado GPT-4
            st.metric("💵 Costo estimado", f"${costo_estimado:.2f}")
        
        with col3:
            st.metric("📊 Productos a procesar", n_productos)

def mostrar_preview_estilo(estilo: str):
    """Muestra un preview del estilo seleccionado"""
    
    previews = {
        "completa": """
        **Estructura:**
        - Título y subtítulo del producto
        - Lista de beneficios principales
        - Grid de características
        - Tabla de especificaciones técnicas
        - Párrafo "¿Por qué elegir este producto?"
        
        **Ideal para:** Productos que necesitan información completa y detallada
        """,
        
        "marketing": """
        **Estructura:**
        - Banner hero con título impactante
        - Propuesta de valor única
        - Beneficios únicos destacados
        - Prueba social/testimonios
        - Elementos de urgencia y CTA
        
        **Ideal para:** Maximizar conversiones y ventas
        """,
        
        "tecnica": """
        **Estructura:**
        - Especificaciones técnicas detalladas
        - Características técnicas avanzadas
        - Información de compatibilidad
        - Requisitos del sistema
        - Información de soporte técnico
        
        **Ideal para:** Productos tecnológicos y especializados
        """,
        
        "ecommerce": """
        **Estructura:**
        - Nombre del producto con precio destacado
        - Puntos clave de venta
        - Información de envío y garantías
        - Badges de confianza
        - Políticas de devolución
        
        **Ideal para:** Tiendas online que buscan reducir fricción de compra
        """,
        
        "comparativa": """
        **Estructura:**
        - Comparación con productos similares
        - Ventajas competitivas destacadas
        - Tabla comparativa de características
        - Razones para elegir este producto
        - Diferenciadores únicos
        
        **Ideal para:** Productos en mercados competitivos
        """
    }
    
    st.markdown(previews.get(estilo, "Preview no disponible"))

def render_generation_tab():
    """Tab de generación de descripciones"""
    
    st.markdown("### 🚀 Generar Descripciones HTML")
    
    # Verificar prerequisitos
    if 'productos_df' not in st.session_state:
        st.warning("⚠️ Primero debes cargar un archivo CSV en la pestaña 'Cargar Productos'")
        return
    
    if 'openai_api_key' not in st.session_state or not st.session_state['openai_api_key']:
        st.warning("⚠️ Primero debes configurar tu API Key en la pestaña 'Configuración'")
        return
    
    df = st.session_state['productos_df']
    
    # Opciones de procesamiento
    st.markdown("### Opciones de procesamiento")
    
    col1, col2 = st.columns(2)
    
    with col1:
        procesar_todos = st.checkbox("Procesar todos los productos", value=True)
    
    with col2:
        if not procesar_todos:
            max_productos = st.number_input(
                "Número de productos a procesar",
                min_value=1,
                max_value=len(df),
                value=min(5, len(df))
            )
        else:
            max_productos = len(df)
    
    # Resumen de configuración
    st.markdown("### 📋 Resumen de configuración")
    
    config_actual = {
        "Productos a procesar": max_productos,
        "Método": st.session_state.get('metodo_seleccionado', 'auto'),
        "Estilo": st.session_state.get('estilo_seleccionado', 'completa'),
        "Idioma": st.session_state.get('idioma_seleccionado', 'es')
    }
    
    col1, col2 = st.columns(2)
    for i, (key, value) in enumerate(config_actual.items()):
        col = col1 if i % 2 == 0 else col2
        with col:
            st.info(f"**{key}:** {value}")
    
    # Botón de generación
    if st.button("🎨 Generar Descripciones HTML", type="primary", use_container_width=True):
        
        # Preparar datos
        df_procesar = df.head(max_productos) if not procesar_todos else df
        
        # Obtener configuración
        metodo = st.session_state.get('metodo_seleccionado', 'auto')
        urls_manuales = st.session_state.get('urls_manuales', []) if metodo == 'manual' else None
        estilo = st.session_state.get('estilo_seleccionado', 'completa')
        categoria = st.session_state.get('categoria_global', '')
        terminos = st.session_state.get('terminos_adicionales', '')
        idioma = st.session_state.get('idioma_seleccionado', 'es')
        
        # Contenedores para progreso
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Procesar
        with st.spinner("Generando descripciones HTML de calidad premium..."):
            try:
                df_results, stats, errores = process_descriptions_streamlit(
                    df=df_procesar,
                    limite_productos=max_productos,
                    api_key=st.session_state['openai_api_key'],
                    metodo=metodo,
                    urls_manuales=urls_manuales,
                    estilo=estilo,
                    categoria=categoria,
                    terminos_adicionales=terminos,
                    idioma=idioma,
                    progress_bar=progress_bar,
                    status_text=status_text
                )
                
                # Guardar resultados
                st.session_state['ultimos_resultados_html'] = {
                    'df': df_results,
                    'stats': stats,
                    'errores': errores,
                    'timestamp': datetime.now(),
                    'config': config_actual
                }
                
                # Mostrar resultados
                st.success(f"✅ Proceso completado en {stats['tiempo_total']}")
                
                # Métricas de resultado
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        "Descripciones exitosas",
                        stats['exitosos'],
                        f"{(stats['exitosos']/stats['total_productos']*100):.0f}%"
                    )
                
                with col2:
                    st.metric(
                        "Fuentes promedio",
                        stats['fuentes_promedio'],
                        "🌐"
                    )
                
                with col3:
                    st.metric(
                        "Características promedio",
                        stats['caracteristicas_promedio'],
                        "📊"
                    )
                
                with col4:
                    st.metric("Errores", stats['errores'], "❌" if stats['errores'] > 0 else "✅")
                
                # Mostrar errores si hay
                if errores:
                    with st.expander(f"⚠️ Ver errores ({len(errores)})"):
                        for error in errores:
                            st.error(f"**{error['producto']}**: {error['error']}")
                
                # Continuar en pestaña de resultados
                st.info("🎉 ¡Proceso completado! Ve a la pestaña 'Resultados' para descargar y ver las descripciones generadas.")
                
            except Exception as e:
                st.error(f"❌ Error durante el procesamiento: {str(e)}")
                st.markdown("**Posibles causas:**")
                st.markdown("- API Key incorrecta o sin créditos")
                st.markdown("- URLs inaccesibles (en modo manual)")
                st.markdown("- Error de conexión")

def render_test_individual_tab():
    """Nueva pestaña para probar productos individuales con logs en tiempo real"""
    
    st.markdown("### 🧪 Prueba de Producto Individual")
    st.markdown("Prueba el sistema avanzado de búsqueda con un solo producto y ve el progreso en tiempo real.")
    
    # Verificar API Key
    if 'openai_api_key' not in st.session_state or not st.session_state['openai_api_key']:
        st.warning("⚠️ Primero debes configurar tu API Key en la pestaña 'Configuración'")
        return
    
    # Formulario de entrada
    with st.form("test_individual_form"):
        st.markdown("#### 📝 Información del Producto")
        
        col1, col2 = st.columns(2)
        
        with col1:
            nombre_producto = st.text_input(
                "Nombre del Producto *", 
                placeholder="Ej: L'Oréal Revitalift Vitamin C Serum",
                help="Nombre completo del producto cosmético"
            )
            
            codigo_barras = st.text_input(
                "Código de Barras (opcional)", 
                placeholder="1234567890123",
                help="Código de barras para búsqueda más precisa"
            )
        
        with col2:
            metodo = st.selectbox(
                "Método de Búsqueda",
                options=["Automática (recomendado)", "URLs específicas"],
                help="Automática usa búsqueda web inteligente"
            )
            
            idioma = st.selectbox(
                "Idioma de la descripción",
                options=["es", "en"],
                index=0,
                help="Idioma para generar la descripción HTML"
            )
        
        # URLs específicas (si se selecciona ese método)
        urls_especificas = []
        if "específicas" in metodo:
            st.markdown("#### 🔗 URLs Específicas")
            for i in range(3):
                url = st.text_input(f"URL {i+1}", key=f"url_{i}")
                if url.strip():
                    urls_especificas.append(url.strip())
        
        submitted = st.form_submit_button("🚀 Iniciar Búsqueda Avanzada", type="primary")
    
    # Procesar cuando se envía el formulario
    if submitted:
        if not nombre_producto.strip():
            st.error("❌ El nombre del producto es obligatorio")
            return
        
        # Crear contenedores para el progreso
        st.markdown("### 📊 Progreso en Tiempo Real")
        
        # Placeholder para logs
        log_container = st.empty()
        
        try:
            # Inicializar generador
            from .generator import SimpleHTMLDescriptionGenerator
            generator = SimpleHTMLDescriptionGenerator(api_key=st.session_state['openai_api_key'])
            
            # Mostrar inicio
            with log_container.container():
                st.write("🚀 **Iniciando búsqueda avanzada...**")
                progress_logs = []
            
            # Determinar método
            metodo_busqueda = "manual" if "específicas" in metodo else "auto"
            
            # Ejecutar búsqueda
            if metodo_busqueda == "auto":
                product_data = generator.buscar_informacion_web_real(
                    nombre_producto=nombre_producto,
                    codigo_barras=codigo_barras
                )
            else:
                product_data = generator.buscar_producto_simple(
                    nombre_producto=nombre_producto,
                    codigo_barras=codigo_barras,
                    urls_especificas=urls_especificas
                )
            
            # Mostrar logs de progreso
            logs = generator.get_progress_logs()
            with log_container.container():
                st.write("#### 📋 Registro de Actividad:")
                for log in logs:
                    status_emoji = {
                        "info": "ℹ️", "success": "✅", "warning": "⚠️",
                        "error": "❌", "search": "🔍", "processing": "⚙️", "ai": "🤖"
                    }
                    emoji = status_emoji.get(log["status"], "📝")
                    st.write(f"{emoji} **[{log['timestamp']}]** {log['message']}")
            
            # Generar HTML
            st.write("🎨 **Generando HTML con máxima calidad...**")
            html_description = generator.generar_html_limpio(product_data, idioma)
            
            # Validar HTML
            es_valido, errores = generator.validar_html_formato(html_description)
            
            # Mostrar resultados
            st.markdown("### ✅ Resultado")
            
            if es_valido:
                st.success("✅ Descripción HTML generada correctamente")
            else:
                st.warning(f"⚠️ HTML con advertencias: {', '.join(errores)}")
            
            # Estadísticas
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("🌐 Fuentes", product_data.fuentes_encontradas, help="Fuentes web consultadas")
            with col2:
                st.metric("🧪 Ingredientes", len(product_data.ingredientes_activos), help="Ingredientes activos identificados")
            with col3:
                st.metric("📝 Beneficios", len(product_data.beneficios), help="Beneficios encontrados")
            with col4:
                st.metric("📏 Longitud HTML", len(html_description), help="Caracteres en el HTML generado")
            
            # Mostrar HTML generado
            st.markdown("### 📄 HTML Generado")
            
            # Crear pestañas para ver el resultado
            tab_preview, tab_html, tab_copy = st.tabs(["👁️ Vista Previa", "📝 Código HTML", "📋 Copiar"])
            
            with tab_preview:
                st.markdown("#### Vista previa del HTML:")
                st.markdown(html_description, unsafe_allow_html=True)
            
            with tab_html:
                st.markdown("#### Código HTML:")
                st.code(html_description, language='html')
            
            with tab_copy:
                st.markdown("#### Copiar al portapapeles:")
                st.text_area("HTML para copiar:", html_description, height=300)
                
                # Botón para copiar
                escaped_html = html_description.replace('`', '\\`')
                copy_button_html = f"""
                <button onclick="navigator.clipboard.writeText(`{escaped_html}`).then(() => alert('¡HTML copiado al portapapeles!'))">
                    📋 Copiar HTML
                </button>
                """
                st.markdown(copy_button_html, unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"❌ Error al generar la descripción: {str(e)}")
            
            # Mostrar logs de depuración si están disponibles
            try:
                if 'generator' in locals():
                    logs = generator.get_progress_logs()
                    if logs:
                        with st.expander("🔍 Ver logs de depuración"):
                            for log in logs:
                                st.write(f"**[{log['timestamp']}]** {log['message']}")
            except:
                pass
            
            with st.expander("🐛 Detalles técnicos del error"):
                st.code(str(e))


def render_results_tab():
    """Tab de resultados y descargas"""
    
    st.markdown("### 📊 Resultados y descargas")
    
    if 'ultimos_resultados_html' not in st.session_state:
        st.info("No hay resultados previos. Genera descripciones en la pestaña 'Generar Descripciones'")
        return
    
    resultados = st.session_state['ultimos_resultados_html']
    df_results = resultados['df']
    stats = resultados['stats']
    errores = resultados['errores']
    config = resultados['config']
    
    # Información de la generación
    st.markdown(f"**Última generación:** {resultados['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Resumen ejecutivo
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total procesados", stats['total_productos'])
        st.metric("Exitosos", stats['exitosos'])
    
    with col2:
        st.metric("Fuentes promedio", stats['fuentes_promedio'])
        st.metric("Características promedio", stats['caracteristicas_promedio'])
    
    with col3:
        st.metric("Tiempo total", stats['tiempo_total'])
        tasa_exito = (stats['exitosos'] / stats['total_productos'] * 100) if stats['total_productos'] > 0 else 0
        st.metric("Tasa de éxito", f"{tasa_exito:.1f}%")
    
    # Configuración utilizada
    with st.expander("⚙️ Configuración utilizada"):
        for key, value in config.items():
            st.markdown(f"**{key}:** {value}")
    
    # Vista previa de descripciones
    if not df_results.empty:
        st.markdown("### 👀 Vista previa de descripciones generadas")
        
        # Selector de producto para preview
        productos_disponibles = df_results['Handle'].tolist()
        producto_selected = st.selectbox(
            "Selecciona un producto para ver su descripción:",
            productos_disponibles,
            format_func=lambda x: f"{x} ({df_results[df_results['Handle']==x].iloc[0].get('Handle', x)})"
        )
        
        if producto_selected:
            producto_data = df_results[df_results['Handle'] == producto_selected].iloc[0]
            html_description = producto_data.get('Metafield: custom.html_description [rich_text_field]', '')
            
            if html_description:
                st.markdown("**HTML generado:**")
                with st.expander("Ver código HTML", expanded=False):
                    st.code(html_description, language='html')
                
                st.markdown("**Vista previa renderizada:**")
                st.components.v1.html(html_description, height=600, scrolling=True)
    
    # Opciones de descarga
    st.markdown("### 💾 Descargar resultados")
    
    if not df_results.empty:
        try:
            # Preparar resultados completos para archivos adicionales
            resultados_completos = []
            for _, row in df_results.iterrows():
                resultados_completos.append(row.to_dict())
            
            archivos = create_download_files(df_results, stats, errores, resultados_completos)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if 'descripciones_html_shopify.csv' in archivos:
                    st.download_button(
                        label="📄 CSV para Shopify",
                        data=archivos['descripciones_html_shopify.csv'],
                        file_name=f"descripciones_html_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        help="CSV listo para importar en Shopify"
                    )
            
            with col2:
                if 'todas_descripciones.html' in archivos:
                    st.download_button(
                        label="🌐 HTML completo",
                        data=archivos['todas_descripciones.html'],
                        file_name=f"todas_descripciones_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                        mime="text/html",
                        help="Archivo HTML con todas las descripciones"
                    )
            
            with col3:
                if 'reporte_generacion.txt' in archivos:
                    st.download_button(
                        label="📊 Reporte detallado",
                        data=archivos['reporte_generacion.txt'],
                        file_name=f"reporte_html_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                        mime="text/plain",
                        help="Reporte completo del proceso"
                    )
            
            with col4:
                try:
                    zip_data = create_zip_download(archivos)
                    st.download_button(
                        label="🗂️ Descargar todo (ZIP)",
                        data=zip_data,
                        file_name=f"descripciones_completo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                        mime="application/zip",
                        help="Todos los archivos en un ZIP"
                    )
                except Exception as zip_error:
                    st.error(f"Error creando ZIP: {str(zip_error)}")
        
        except Exception as download_error:
            st.error(f"Error creando archivos de descarga: {str(download_error)}")
    
    # Instrucciones de uso
    with st.expander("📚 Instrucciones de uso en Shopify"):
        st.markdown("""
        ### Cómo usar las descripciones HTML generadas:
        
        1. **Importar en Shopify:**
           - Ve a Apps > Matrixify
           - Selecciona "Import" > "Products"
           - Sube el archivo CSV descargado
           - Mapea la columna "html_description" al metafield personalizado
        
        2. **Configurar en tu tema:**
           ```liquid
           {{ product.metafields.custom.html_description }}
           ```
        
        3. **Verificar visualización:**
           - Las descripciones incluyen CSS inline
           - Son responsive y compatibles con la mayoría de temas
           - Puedes personalizar los estilos editando el CSS
        
        4. **Tips adicionales:**
           - Haz backup antes de importar
           - Prueba con un producto primero
           - Revisa que el HTML se vea correctamente en tu tema
        """)
    
    # Estadísticas adicionales
    if stats['exitosos'] > 0:
        st.markdown("### 📈 Estadísticas detalladas")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Distribución por configuración:**")
            st.info(f"Método usado: {stats.get('metodo_usado', 'N/A')}")
            st.info(f"Estilo aplicado: {stats.get('estilo_aplicado', 'N/A')}")
            st.info(f"Idioma: {stats.get('idioma', 'N/A')}")
        
        with col2:
            st.markdown("**Calidad de información:**")
            if stats['fuentes_promedio'] > 0:
                st.success(f"✅ Buena cobertura de fuentes ({stats['fuentes_promedio']} promedio)")
            else:
                st.warning("⚠️ Información limitada de fuentes")
            
            if stats['caracteristicas_promedio'] >= 5:
                st.success(f"✅ Rica en características ({stats['caracteristicas_promedio']} promedio)")
            else:
                st.info(f"ℹ️ Características encontradas: {stats['caracteristicas_promedio']} promedio")