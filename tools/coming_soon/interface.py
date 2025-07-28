# tools/coming_soon/interface.py
import streamlit as st

def render(config):
    """Interfaz para herramientas futuras"""
    st.markdown("""
    <div class="tool-card">
        <h2>🔮 Próximamente...</h2>
        <p>Más herramientas de automatización en desarrollo</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🛠️ Herramientas en desarrollo:")
    st.markdown("""
    - 🖼️ **Generador de Descripciones de Imágenes**
    - 📧 **Automatizador de Email Marketing**  
    - 🏷️ **Optimizador de Tags y SEO**
    - 📊 **Dashboard de Analytics**
    - 🤖 **Chatbot de Atención al Cliente**
    """)