# utils/footer.py - Footer de la aplicación
import streamlit as st
from datetime import datetime

def render_footer():
    """Renderiza el footer de la aplicación"""
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 🛒 Shopify Automation Platform")
        st.markdown("Automatiza tus procesos de Shopify con IA")
    
    with col2:
        st.markdown("### 🔗 Enlaces útiles")
        st.markdown("""
        - [Documentación de Shopify](https://shopify.dev/)
        - [Matrixify](https://matrixify.app/)
        - [OpenAI API](https://openai.com/api/)
        """)
    
    with col3:
        st.markdown("### ℹ️ Información")
        st.markdown(f"""
        **Versión:** 2.0  
        **Última actualización:** {datetime.now().strftime('%Y-%m-%d')}  
        **Compatibilidad:** Todos los modelos GPT  
        """)