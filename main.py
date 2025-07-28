# main.py - Archivo principal de Streamlit
import streamlit as st
from utils.config import setup_page_config, load_custom_css
from utils.sidebar import render_sidebar
from tools import faq_generator, html_description_generator, product_analyzer, coming_soon
from utils.footer import render_footer

def main():
    """Función principal de la aplicación"""
    # Configuración inicial
    setup_page_config()
    load_custom_css()
    
    # Header principal
    st.markdown("""
    <div class="main-header">
        <h1>🛒 Shopify Automation Platform</h1>
        <p>Automatiza tus procesos de Shopify con herramientas potenciadas por IA</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Renderizar sidebar y obtener configuración
    config = render_sidebar()
    
    # Enrutador principal - dirigir a la herramienta seleccionada
    route_to_tool(config)
    
    # Footer SOLO si no hay procesamiento activo
    # Usar session_state para controlar cuándo mostrar el footer
    if not st.session_state.get('processing_active', False):
        render_footer()

def route_to_tool(config):
    """Enrutador que dirige a la herramienta seleccionada"""
    herramienta = config['herramienta_seleccionada']
    
    if herramienta == "🤖 Generador de FAQs":
        faq_generator.render(config)
    elif herramienta == "🎨 Generador de Descripciones HTML":
        html_description_generator.render(config)
    elif herramienta == "📊 Análisis de Productos":
        product_analyzer.render(config)
    else:
        coming_soon.render(config)

if __name__ == "__main__":
    main()