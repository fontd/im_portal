# tools/html_description_generator/processor.py
from .generator import SimpleHTMLDescriptionGenerator

# Este archivo se mantiene para compatibilidad pero la nueva herramienta
# no necesita procesamiento masivo, solo generación individual

def process_single_product(nombre_producto: str, codigo_barras: str = "", 
                         urls_especificas: list = None, idioma: str = "es", 
                         api_key: str = None) -> dict:
    """
    Procesa un solo producto y genera su descripción HTML
    
    Args:
        nombre_producto: Nombre del producto
        codigo_barras: Código de barras opcional
        urls_especificas: Lista de URLs específicas
        idioma: Idioma de generación
        api_key: API key de OpenAI
    
    Returns:
        dict: Resultado con HTML generado y metadatos
    """
    
    if not api_key:
        raise ValueError("API key es requerido")
    
    if not nombre_producto.strip():
        raise ValueError("Nombre del producto es requerido")
    
    try:
        # Inicializar generador
        generator = SimpleHTMLDescriptionGenerator(api_key=api_key)
        
        # Buscar información del producto
        product_data = generator.buscar_producto_simple(
            nombre_producto=nombre_producto,
            codigo_barras=codigo_barras,
            urls_especificas=urls_especificas
        )
        
        # Generar HTML
        html_description = generator.generar_html_limpio(product_data, idioma)
        
        # Validar HTML
        es_valido, errores = generator.validar_html_formato(html_description)
        
        # Preparar resultado
        resultado = {
            "success": True,
            "html": html_description,
            "product_data": {
                "nombre": product_data.nombre,
                "descripcion_corta": product_data.descripcion_corta,
                "ingredientes_activos": len(product_data.ingredientes_activos),
                "beneficios": len(product_data.beneficios),
                "fuentes_consultadas": product_data.fuentes_encontradas
            },
            "validation": {
                "es_valido": es_valido,
                "errores": errores
            },
            "config": {
                "idioma": idioma,
                "metodo": "manual" if urls_especificas else "auto"
            }
        }
        
        return resultado
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "html": "",
            "product_data": None
        }

# Funciones legacy mantenidas para compatibilidad
def process_descriptions_streamlit(*args, **kwargs):
    """Función legacy - La nueva herramienta no necesita procesamiento masivo"""
    raise NotImplementedError("Esta herramienta ahora procesa productos individuales")

def create_download_files(*args, **kwargs):
    """Función legacy - La nueva herramienta no genera archivos de descarga"""
    raise NotImplementedError("La nueva herramienta usa copy-paste directo")

def create_zip_download(*args, **kwargs):
    """Función legacy - La nueva herramienta no genera ZIPs"""
    raise NotImplementedError("La nueva herramienta usa copy-paste directo")

def validar_csv_productos(*args, **kwargs):
    """Función legacy - La nueva herramienta no usa CSV"""
    raise NotImplementedError("La nueva herramienta no requiere CSV")

def estimar_tiempo_procesamiento(*args, **kwargs):
    """Función legacy - La nueva herramienta procesa instantáneamente"""
    return "< 30 segundos por producto"

def obtener_muestra_productos(*args, **kwargs):
    """Función legacy - La nueva herramienta no usa muestras"""
    raise NotImplementedError("La nueva herramienta procesa un producto a la vez")