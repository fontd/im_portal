# utils/sidebar.py - Lógica del sidebar
import streamlit as st
import os

def render_sidebar():
    """Renderiza el sidebar y retorna la configuración"""
    with st.sidebar:
        st.title("🔧 Herramientas")
        
        # Lista de herramientas
        st.markdown("**Selecciona una herramienta:**")
        herramienta_seleccionada = st.radio(
            "herramientas",
            ["🤖 Generador de FAQs", "📊 Análisis de Productos", "🔮 Próximamente..."],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        st.markdown("### ⚙️ Configuración")
        
        # Configuración de API Key
        api_key = st.text_input(
            "OpenAI API Key:",
            value=os.getenv('OPENAI_API_KEY', ''),
            type="password",
            help="Tu clave de API de OpenAI"
        )
        
        # Selector de modelo GPT
        modelo_gpt = st.selectbox(
            "Modelo GPT:",
            [
                "gpt-3.5-turbo",
                "gpt-3.5-turbo-16k", 
                "gpt-4",
                "gpt-4-turbo-preview",
                "gpt-4o"
            ],
            index=0,
            help="Selecciona el modelo de OpenAI"
        )
        
        # Info del modelo
        _show_model_info(modelo_gpt)
        _show_api_status(api_key)
        
        return {
            'herramienta_seleccionada': herramienta_seleccionada,
            'api_key': api_key,
            'modelo_gpt': modelo_gpt
        }

def _show_model_info(modelo_gpt):
    """Muestra información del modelo seleccionado"""
    costos_modelo = {
        "gpt-3.5-turbo": "💰 Económico (~$0.003/1K tokens)",
        "gpt-3.5-turbo-16k": "💰 Económico + Contexto largo", 
        "gpt-4": "💎 Premium (~$0.03/1K tokens)",
        "gpt-4-turbo-preview": "💎 Premium + Rápido",
        "gpt-4o": "🚀 Último modelo (más caro)"
    }
    st.caption(costos_modelo.get(modelo_gpt, ""))

def _show_api_status(api_key):
    """Muestra el estado de la API Key"""
    if api_key:
        st.success("✅ API Key configurada")
    else:
        st.error("❌ API Key requerida")