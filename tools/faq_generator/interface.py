# tools/faq_generator/interface.py
import streamlit as st
import pandas as pd
import os
from datetime import datetime
import json
from .processor import (
    process_faqs_streamlit, 
    create_download_files,
    create_zip_download,
    validar_csv_productos,
    obtener_muestra_productos,
    estimar_tiempo_procesamiento
)

def render(config=None):
    """Renderiza la interfaz del generador de FAQs"""
    
    # Store config in session state if provided
    if config:
        st.session_state['sidebar_config'] = config
    
    st.title("🎯 Generador Premium de FAQs v3.0")
    st.markdown("""
    ### Sistema Ultra-Premium de Generación de FAQs
    
    **Características:**
    - 🧠 Análisis profundo con IA de cada producto
    - 🎲 Sistema anti-repetición con memoria persistente
    - 📊 8 categorías de preguntas con variaciones infinitas
    - ⭐ Sistema de calidad: LEGENDARIA > EXCEPCIONAL > EXCELENTE
    - 🎨 Perfiles de compradores (experto, luxury, principiante, etc.)
    """)
    
    # Tabs principales
    tab1, tab2, tab3, tab4 = st.tabs(["📤 Cargar Productos", "⚙️ Configuración", "🚀 Generar FAQs", "📊 Historial"])
    
    with tab1:
        render_upload_tab()
    
    with tab2:
        render_config_tab()
    
    with tab3:
        render_generation_tab()
    
    with tab4:
        render_history_tab()

def render_upload_tab():
    """Tab para cargar el CSV de productos"""
    
    st.markdown("### Paso 1: Cargar archivo CSV de productos")
    
    # Mostrar formato esperado
    with st.expander("📋 Ver formato esperado del CSV"):
        st.markdown("""
        **Columnas requeridas:**
        - `Handle`: Identificador único del producto
        - `Title`: Nombre del producto
        
        **Columnas recomendadas:**
        - `Body HTML` o `Body (HTML)`: Descripción del producto
        - `Variant Price`: Precio del producto
        - `Vendor`: Marca/Fabricante
        - `Tags`: Etiquetas del producto
        """)
        
        # Ejemplo de CSV
        ejemplo_df = pd.DataFrame({
            'Handle': ['serum-vitamina-c', 'crema-retinol-noche'],
            'Title': ['Serum Vitamina C 20%', 'Crema Retinol 0.3%'],
            'Body HTML': ['<p>Serum concentrado con vitamina C...</p>', '<p>Crema de noche con retinol...</p>'],
            'Variant Price': [45.99, 67.99],
            'Vendor': ['SkinLab', 'Premium Cosmetics']
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
                muestra_df = obtener_muestra_productos(df, n=5)
                st.dataframe(muestra_df)
                
                # Análisis de calidad de datos
                with st.expander("📊 Análisis de calidad de datos"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Productos sin descripción:**")
                        sin_descripcion = 0
                        for col in ['Body HTML', 'Body (HTML)', 'body_html']:
                            if col in df.columns:
                                sin_descripcion = df[col].isna().sum()
                                break
                        
                        if sin_descripcion > 0:
                            st.warning(f"{sin_descripcion} productos sin descripción")
                        else:
                            st.success("✅ Todos los productos tienen descripción")
                    
                    with col2:
                        st.markdown("**Productos sin precio:**")
                        if 'Variant Price' in df.columns:
                            sin_precio = df['Variant Price'].isna().sum()
                            if sin_precio > 0:
                                st.warning(f"{sin_precio} productos sin precio")
                            else:
                                st.success("✅ Todos los productos tienen precio")
                        else:
                            st.info("Columna de precio no encontrada")
                
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
    
    # API Key (use from sidebar)
    sidebar_api_key = st.session_state.get('sidebar_config', {}).get('api_key', '')
    
    if sidebar_api_key:
        st.success("✅ API Key configurada desde la barra lateral")
        st.session_state['openai_api_key'] = sidebar_api_key
    else:
        st.warning("⚠️ Configura tu API Key en la barra lateral")
        st.session_state['openai_api_key'] = ""
    
    # Configuración del modelo (mostrar el seleccionado en sidebar)
    st.markdown("### 🧠 Configuración del modelo")
    
    # Get model from sidebar config
    current_model = st.session_state.get('sidebar_config', {}).get('modelo_gpt', 'gpt-3.5-turbo')
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Modelo de IA seleccionado:**")
        st.info(f"🤖 {current_model}")
        
        # Show model info
        if "gpt-4" in current_model:
            st.caption("💎 GPT-4: Máxima calidad, ideal para productos premium")
        elif "gpt-3.5" in current_model:
            st.caption("⚡ GPT-3.5: Buena calidad, más rápido y económico")
        
        st.caption("💡 Para cambiar el modelo, usa el selector en la barra lateral")
    
    with col2:
        max_intentos = st.number_input(
            "Intentos máximos por producto",
            min_value=1,
            max_value=5,
            value=3,
            help="Número de intentos para alcanzar calidad óptima"
        )
        st.session_state['max_intentos'] = max_intentos
    
    # Configuración avanzada
    with st.expander("🔧 Configuración avanzada"):
        st.markdown("### Criterios de calidad")
        
        col1, col2 = st.columns(2)
        
        with col1:
            calidad_minima = st.select_slider(
                "Calidad mínima aceptable",
                options=["ACEPTABLE", "BUENA", "EXCELENTE", "EXCEPCIONAL"],
                value="BUENA",
                help="FAQs por debajo de este nivel se reintentarán"
            )
            st.session_state['calidad_minima'] = calidad_minima
        
        with col2:
            longitud_respuesta = st.slider(
                "Longitud de respuestas (caracteres)",
                min_value=150,
                max_value=350,
                value=(220, 320),
                help="Rango óptimo de longitud para las respuestas"
            )
            st.session_state['longitud_respuesta'] = longitud_respuesta
        
        # Cache y memoria
        st.markdown("### 💾 Cache y memoria")
        
        usar_cache = st.checkbox(
            "Usar cache de preguntas históricas",
            value=True,
            help="Evita repetir preguntas ya generadas anteriormente"
        )
        st.session_state['usar_cache'] = usar_cache
        
        if st.button("🗑️ Limpiar cache de preguntas"):
            # Aquí iría la lógica para limpiar el cache
            st.success("Cache limpiado exitosamente")
    
    # Estimación de costos
    sidebar_api_key = st.session_state.get('sidebar_config', {}).get('api_key', '')
    if 'productos_df' in st.session_state and sidebar_api_key:
        st.markdown("### 💰 Estimación de costos")
        
        df = st.session_state['productos_df']
        n_productos = len(df)
        
        # Precios aproximados por 1K tokens
        precios = {
            "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002},
            "gpt-4": {"input": 0.03, "output": 0.06}
        }
        
        # Estimación de tokens por producto (aproximado)
        tokens_por_producto = 2000  # Promedio estimado
        
        # Get current model for cost estimation
        current_model = st.session_state.get('sidebar_config', {}).get('modelo_gpt', 'gpt-3.5-turbo')
        
        # Map model names to pricing keys
        if "gpt-4" in current_model:
            pricing_key = "gpt-4"
        else:
            pricing_key = "gpt-3.5-turbo"
        
        precio_modelo = precios[pricing_key]
        costo_estimado = n_productos * tokens_por_producto * (precio_modelo["input"] + precio_modelo["output"]) / 1000
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            tiempo_estimado = estimar_tiempo_procesamiento(n_productos, current_model)
            st.metric("⏱️ Tiempo estimado", tiempo_estimado)
        
        with col2:
            st.metric("💵 Costo estimado", f"${costo_estimado:.2f}")
        
        with col3:
            st.metric("📊 Productos a procesar", n_productos)

def render_generation_tab():
    """Tab de generación de FAQs"""
    
    st.markdown("### 🚀 Generar FAQs")
    
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
                value=min(10, len(df))
            )
        else:
            max_productos = len(df)
    
    # Mostrar resumen
    current_model = st.session_state.get('sidebar_config', {}).get('modelo_gpt', 'gpt-3.5-turbo')
    st.info(f"📋 Se procesarán {max_productos} productos con el modelo {current_model}")
    
    # Botón de generación
    if st.button("🎯 Generar FAQs Premium", type="primary", use_container_width=True):
        
        # Preparar datos
        df_procesar = df.head(max_productos) if not procesar_todos else df
        
        # Contenedores para progreso
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Procesar
        with st.spinner("Generando FAQs de calidad premium..."):
            try:
                # Get current model from sidebar config
                current_model = st.session_state.get('sidebar_config', {}).get('modelo_gpt', 'gpt-3.5-turbo')
                
                df_results, stats, errores = process_faqs_streamlit(
                    df=df_procesar,
                    limite_productos=max_productos,
                    max_intentos=st.session_state.get('max_intentos', 3),
                    api_key=st.session_state['openai_api_key'],
                    modelo_gpt=current_model,
                    progress_bar=progress_bar,
                    status_text=status_text
                )
                
                # Guardar resultados en session state
                st.session_state['ultimos_resultados'] = {
                    'df': df_results,
                    'stats': stats,
                    'errores': errores,
                    'timestamp': datetime.now()
                }
                
                # Mostrar resultados
                st.success(f"✅ Proceso completado en {stats['tiempo_total']}")
                
                # Métricas de resultado
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        "Productos exitosos",
                        stats['exitosos'],
                        f"{(stats['exitosos']/stats['total_productos']*100):.0f}%"
                    )
                
                with col2:
                    st.metric(
                        "Calidad promedio",
                        f"{stats['calidad_promedio']}/20",
                        "⭐" * int(stats['calidad_promedio'] / 4)
                    )
                
                with col3:
                    # Safe handling of quality distribution
                    if stats['distribucion_calidad'] and any(v > 0 for v in stats['distribucion_calidad'].values()):
                        calidad_top = max(stats['distribucion_calidad'].items(), key=lambda x: x[1])[0]
                        st.metric("Calidad más común", calidad_top)
                    else:
                        st.metric("Calidad más común", "N/A")
                
                with col4:
                    st.metric("Errores", stats['errores'], "❌" if stats['errores'] > 0 else "✅")
                
                # Distribución de calidad
                if stats['exitosos'] > 0:
                    st.markdown("### 📊 Distribución de calidad")
                    
                    # Safe creation of quality distribution columns
                    calidades_con_datos = [(k, v) for k, v in stats['distribucion_calidad'].items() if v > 0]
                    
                    if calidades_con_datos:
                        cols = st.columns(len(calidades_con_datos))
                        
                        for idx, (calidad, cantidad) in enumerate(calidades_con_datos):
                            if idx < len(cols):
                                with cols[idx]:
                                    porcentaje = cantidad / stats['exitosos'] * 100
                                    st.metric(calidad, cantidad, f"{porcentaje:.0f}%")
                
                # Mostrar errores si hay
                if errores:
                    with st.expander(f"⚠️ Ver errores ({len(errores)})"):
                        for error in errores:
                            st.error(f"**{error['producto']}**: {error['error']}")
                
                # Opciones de descarga
                st.markdown("### 💾 Descargar resultados")
                
                try:
                    archivos = create_download_files(df_results, stats, errores)
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if 'faqs_shopify.csv' in archivos:
                            st.download_button(
                                label="📄 Descargar CSV para Shopify",
                                data=archivos['faqs_shopify.csv'],
                                file_name=f"faqs_shopify_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                mime="text/csv"
                            )
                        else:
                            st.info("CSV no disponible")
                    
                    with col2:
                        if 'reporte_calidad.txt' in archivos:
                            st.download_button(
                                label="📊 Descargar reporte de calidad",
                                data=archivos['reporte_calidad.txt'],
                                file_name=f"reporte_calidad_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                                mime="text/plain"
                            )
                        else:
                            st.info("Reporte no disponible")
                    
                    with col3:
                        try:
                            zip_data = create_zip_download(archivos)
                            st.download_button(
                                label="🗂️ Descargar todo (ZIP)",
                                data=zip_data,
                                file_name=f"faqs_completo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                                mime="application/zip"
                            )
                        except Exception as zip_error:
                            st.error(f"Error creando ZIP: {str(zip_error)}")
                
                except Exception as download_error:
                    st.error(f"Error creando archivos de descarga: {str(download_error)}")
                    st.markdown("Los resultados están disponibles pero hay un problema con los archivos de descarga.")
                
                # Vista previa de resultados
                if not df_results.empty:
                    with st.expander("👀 Ver muestra de FAQs generadas"):
                        # Mostrar las primeras 2 FAQs del primer producto
                        primer_producto = df_results.iloc[0]
                        
                        st.markdown(f"**Producto:** {primer_producto['Handle']}")
                        
                        for i in range(1, 3):
                            st.markdown(f"**FAQ {i}:**")
                            st.info(primer_producto[f'Metafield: custom.faq{i}question [single_line_text_field]'])
                            st.success(primer_producto[f'Metafield: custom.faq{i}answer [multi_line_text_field]'])
                            st.markdown("---")
                
            except Exception as e:
                st.error(f"❌ Error durante el procesamiento: {str(e)}")
                st.markdown("**Posibles causas:**")
                st.markdown("- API Key incorrecta o sin créditos")
                st.markdown("- Formato de datos incorrecto")
                st.markdown("- Error de conexión")
                
                # Log detallado en expander
                with st.expander("Ver detalles del error"):
                    st.code(str(e))

def render_history_tab():
    """Tab de historial y estadísticas"""
    
    st.markdown("### 📊 Historial y estadísticas")
    
    if 'ultimos_resultados' not in st.session_state:
        st.info("No hay resultados previos. Genera FAQs en la pestaña 'Generar FAQs'")
        return
    
    resultados = st.session_state['ultimos_resultados']
    stats = resultados['stats']
    
    # Información de la última generación
    st.markdown(f"**Última generación:** {resultados['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Resumen ejecutivo
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total procesados", stats['total_productos'])
        st.metric("Exitosos", stats['exitosos'])
    
    with col2:
        st.metric("Calidad promedio", f"{stats['calidad_promedio']}/20")
        tasa_exito = (stats['exitosos'] / stats['total_productos'] * 100) if stats['total_productos'] > 0 else 0
        st.metric("Tasa de éxito", f"{tasa_exito:.1f}%")
    
    with col3:
        st.metric("Tiempo total", stats['tiempo_total'])
        if stats['exitosos'] > 0:
            tiempo_promedio = stats['tiempo_total'].split(':')
            # Convertir a segundos totales (aproximado)
            segundos_totales = int(tiempo_promedio[0]) * 3600 + int(tiempo_promedio[1]) * 60 + float(tiempo_promedio[2])
            segundos_por_producto = segundos_totales / stats['exitosos']
            st.metric("Tiempo por producto", f"{segundos_por_producto:.1f}s")
    
    # Análisis de calidad detallado
    st.markdown("### 🎯 Análisis de calidad detallado")
    
    # Crear DataFrame para visualización
    calidad_data = []
    for calidad, cantidad in stats['distribucion_calidad'].items():
        if cantidad > 0:
            calidad_data.append({
                'Nivel de Calidad': calidad,
                'Cantidad': cantidad,
                'Porcentaje': f"{(cantidad / stats['exitosos'] * 100):.1f}%" if stats['exitosos'] > 0 else "0%"
            })
    
    if calidad_data:
        df_calidad = pd.DataFrame(calidad_data)
        st.dataframe(df_calidad, use_container_width=True)
    
    # Insights y recomendaciones
    st.markdown("### 💡 Insights y recomendaciones")
    
    # Generar insights basados en los resultados
    insights = []
    
    if stats['calidad_promedio'] >= 15:
        insights.append("🌟 **Excelente calidad general**: Las FAQs generadas tienen un nivel excepcional de detalle y especificidad.")
    elif stats['calidad_promedio'] >= 10:
        insights.append("✅ **Buena calidad general**: Las FAQs cumplen con los estándares de calidad esperados.")
    else:
        insights.append("⚠️ **Calidad mejorable**: Considera usar GPT-4 o ajustar los parámetros para mejorar la calidad.")
    
    if stats['distribucion_calidad'].get('LEGENDARIA', 0) > 0:
        insights.append(f"🏆 **{stats['distribucion_calidad']['LEGENDARIA']} productos alcanzaron calidad LEGENDARIA**: El máximo nivel posible.")
    
    if stats['errores'] > 0:
        porcentaje_errores = (stats['errores'] / stats['total_productos'] * 100)
        if porcentaje_errores > 10:
            insights.append(f"❌ **Alta tasa de errores ({porcentaje_errores:.1f}%)**: Revisa la calidad de los datos de entrada.")
        else:
            insights.append(f"⚠️ **{stats['errores']} errores detectados**: Revisa los productos que fallaron.")
    
    # Mostrar insights
    for insight in insights:
        st.markdown(insight)
    
    # Estadísticas de uso del cache
    st.markdown("### 💾 Estadísticas del cache")
    
    # Simulación de estadísticas del cache (en producción, estas vendrían del generador)
    col1, col2 = st.columns(2)
    
    with col1:
        # Aquí podrías obtener el número real de preguntas en cache
        st.info("El sistema mantiene un historial de todas las preguntas generadas para evitar repeticiones.")
    
    with col2:
        if st.button("🔄 Actualizar estadísticas"):
            st.rerun()
    
    # Exportar historial completo
    if st.button("📥 Exportar historial completo"):
        # Aquí podrías implementar la exportación del historial completo
        st.success("Funcionalidad en desarrollo")

# Funciones auxiliares para mejorar la experiencia

def mostrar_ejemplos_faqs():
    """Muestra ejemplos de FAQs de alta calidad"""
    
    ejemplos = {
        "LEGENDARIA": {
            "pregunta": "¿Qué concentración de retinol encapsulado contiene Midnight Renewal Serum y cómo maximizo su eficacia?",
            "respuesta": "Contiene 0.3% de retinol puro en microesferas TimeRelease™ que liberan el activo durante 8 horas, minimizando irritación. Aplica 3 gotas en rostro limpio y seco, espera 2 minutos antes del hidratante. Los estudios clínicos muestran 47% de reducción en arrugas profundas tras 12 semanas. Para máxima eficacia, úsalo cada noche alternando con vitamina C en las mañanas."
        },
        "EXCEPCIONAL": {
            "pregunta": "¿Puedo combinar el Serum Vitamina C 20% con mi rutina de ácidos?",
            "respuesta": "Sí, pero con precauciones específicas. Usa la vitamina C por la mañana y los ácidos (AHA/BHA) por la noche, nunca simultáneamente. La fórmula estabilizada con ácido ferúlico al 1% mantiene un pH de 3.5 que no interfiere si respetas 12 horas entre aplicaciones. Introduce gradualmente: primero 3 días solo vitamina C, luego alterna con ácidos."
        }
    }
    
    for calidad, ejemplo in ejemplos.items():
        st.markdown(f"**Ejemplo de calidad {calidad}:**")
        st.info(f"❓ {ejemplo['pregunta']}")
        st.success(f"💡 {ejemplo['respuesta']}")
        st.markdown("---")

# Configuración de estilos personalizados
def aplicar_estilos_personalizados():
    """Aplica estilos CSS personalizados"""
    
    st.markdown("""
    <style>
    /* Mejorar la apariencia de las métricas */
    [data-testid="metric-container"] {
        background-color: rgba(28, 131, 225, 0.1);
        border: 1px solid rgba(28, 131, 225, 0.2);
        padding: 10px;
        border-radius: 10px;
        margin: 5px 0;
    }
    
    /* Estilo para los expanders */
    .streamlit-expanderHeader {
        background-color: rgba(28, 131, 225, 0.05);
        border-radius: 5px;
    }
    
    /* Botones más atractivos */
    .stButton > button {
        border-radius: 20px;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 10px rgba(0,0,0,0.2);
    }
    
    /* Progress bar personalizada */
    .stProgress > div > div > div {
        background-color: #1c83e1;
    }
    </style>
    """, unsafe_allow_html=True)