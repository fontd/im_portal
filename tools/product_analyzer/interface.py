# tools/product_analyzer/interface.py
import streamlit as st

def render(config):
    """Interfaz para análisis de productos"""
    st.markdown("""
    <div class="tool-card">
        <h2>📊 Análisis de Productos</h2>
        <p>Analiza el rendimiento y características de tus productos</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.info("🚧 Esta herramienta estará disponible próximamente.")