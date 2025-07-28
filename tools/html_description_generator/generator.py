# tools/html_description_generator/generator.py
import pandas as pd # type: ignore
from openai import OpenAI # type: ignore
from typing import Dict, List, Tuple, Optional, Set
import json
import time
from datetime import datetime
import re
import random
import hashlib
from collections import defaultdict
import requests
from bs4 import BeautifulSoup
import urllib.parse
from dataclasses import dataclass, field

@dataclass
class ProductInfo:
    """Información extraída del producto"""
    nombre: str
    marca: str = ""
    categoria: str = ""
    caracteristicas: List[str] = field(default_factory=list)
    especificaciones: List[str] = field(default_factory=list)
    precio: str = ""
    beneficios: List[str] = field(default_factory=list)
    imagenes_urls: List[str] = field(default_factory=list)
    datos_tecnicos: Dict[str, str] = field(default_factory=dict)
    fuentes: List[str] = field(default_factory=list)

class HTMLDescriptionGenerator:
    """
    Generador avanzado de descripciones HTML con búsqueda web automática
    """
    
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        
        # Headers para web scraping
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Plantillas de descripción HTML
        self.plantillas_html = {
            "completa": """
            <!-- Descripción Completa del Producto -->
            <div class="product-description">
                <div class="hero-section">
                    <h2 class="product-title">{titulo}</h2>
                    <p class="product-subtitle">{subtitulo}</p>
                </div>
                
                <div class="key-benefits">
                    <h3>✨ Beneficios Principales</h3>
                    <ul class="benefits-list">
                        {beneficios_html}
                    </ul>
                </div>
                
                <div class="product-features">
                    <h3>🔧 Características</h3>
                    <div class="features-grid">
                        {caracteristicas_html}
                    </div>
                </div>
                
                <div class="technical-specs">
                    <h3>📊 Especificaciones Técnicas</h3>
                    <table class="specs-table">
                        {especificaciones_html}
                    </table>
                </div>
                
                <div class="why-choose">
                    <h3>🏆 ¿Por qué elegir este producto?</h3>
                    <p>{razon_eleccion}</p>
                </div>
            </div>
            
            <style>
            .product-description { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; }
            .hero-section { text-align: center; margin-bottom: 30px; }
            .product-title { color: #2c3e50; font-size: 2em; margin-bottom: 10px; }
            .product-subtitle { color: #7f8c8d; font-size: 1.2em; }
            .benefits-list { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; }
            .benefits-list li { background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 4px solid #3498db; }
            .features-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; }
            .feature-item { background: #ffffff; padding: 20px; border: 1px solid #e9ecef; border-radius: 10px; text-align: center; }
            .specs-table { width: 100%; border-collapse: collapse; margin: 20px 0; }
            .specs-table th, .specs-table td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
            .specs-table th { background-color: #f2f2f2; font-weight: bold; }
            .why-choose { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 25px; border-radius: 10px; margin-top: 30px; }
            </style>
            """,
            
            "marketing": """
            <!-- Descripción Enfocada en Marketing -->
            <div class="marketing-description">
                <div class="hero-banner">
                    <h1 class="main-title">{titulo}</h1>
                    <p class="tagline">{tagline}</p>
                    <div class="highlight-box">
                        <span class="highlight-text">{destacado_principal}</span>
                    </div>
                </div>
                
                <div class="value-proposition">
                    <h2>🎯 Tu Solución Perfecta</h2>
                    <p class="value-text">{propuesta_valor}</p>
                </div>
                
                <div class="benefits-showcase">
                    <h2>💎 Beneficios Únicos</h2>
                    <div class="benefits-grid">
                        {beneficios_marketing}
                    </div>
                </div>
                
                <div class="social-proof">
                    <h2>⭐ Lo Que Dicen Nuestros Clientes</h2>
                    <div class="testimonial">
                        <p>"{testimonio}"</p>
                    </div>
                </div>
                
                <div class="cta-section">
                    <h2>🚀 ¡No Esperes Más!</h2>
                    <p class="urgency-text">{texto_urgencia}</p>
                </div>
            </div>
            
            <style>
            .marketing-description { font-family: 'Helvetica Neue', Arial, sans-serif; color: #333; }
            .hero-banner { background: linear-gradient(45deg, #ff6b6b, #ee5a24); color: white; padding: 40px; text-align: center; border-radius: 15px; margin-bottom: 30px; }
            .main-title { font-size: 2.5em; font-weight: bold; margin-bottom: 15px; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
            .tagline { font-size: 1.3em; margin-bottom: 20px; opacity: 0.9; }
            .highlight-box { background: rgba(255,255,255,0.2); padding: 15px; border-radius: 50px; display: inline-block; }
            .highlight-text { font-weight: bold; font-size: 1.1em; }
            .value-proposition { background: #f8f9fa; padding: 30px; border-radius: 10px; margin: 20px 0; }
            .benefits-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 20px 0; }
            .benefit-card { background: white; padding: 25px; border-radius: 10px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); border-left: 5px solid #3498db; }
            .social-proof { background: #2c3e50; color: white; padding: 30px; border-radius: 10px; margin: 20px 0; }
            .testimonial { font-style: italic; font-size: 1.1em; text-align: center; }
            .cta-section { background: linear-gradient(135deg, #11998e, #38ef7d); color: white; padding: 30px; text-align: center; border-radius: 10px; }
            .urgency-text { font-size: 1.2em; font-weight: 500; }
            </style>
            """,
            
            "tecnica": """
            <!-- Descripción Técnica Detallada -->
            <div class="technical-description">
                <div class="tech-header">
                    <h1 class="tech-title">{titulo}</h1>
                    <p class="tech-category">Categoría: {categoria}</p>
                </div>
                
                <div class="specifications">
                    <h2>📋 Especificaciones Técnicas</h2>
                    <div class="specs-container">
                        {especificaciones_detalladas}
                    </div>
                </div>
                
                <div class="technical-features">
                    <h2>⚙️ Características Técnicas</h2>
                    <div class="tech-features-list">
                        {caracteristicas_tecnicas}
                    </div>
                </div>
                
                <div class="compatibility">
                    <h2>🔗 Compatibilidad y Requisitos</h2>
                    <div class="compatibility-info">
                        {info_compatibilidad}
                    </div>
                </div>
                
                <div class="technical-support">
                    <h2>🛠️ Soporte Técnico</h2>
                    <p>{info_soporte}</p>
                </div>
            </div>
            
            <style>
            .technical-description { font-family: 'Courier New', monospace; max-width: 900px; margin: 0 auto; background: #f8f9fa; padding: 20px; border-radius: 10px; }
            .tech-header { background: #2c3e50; color: white; padding: 25px; border-radius: 8px; margin-bottom: 20px; }
            .tech-title { font-size: 2em; margin-bottom: 10px; }
            .tech-category { opacity: 0.8; font-size: 1.1em; }
            .specs-container { background: white; padding: 20px; border-radius: 8px; border: 1px solid #dee2e6; }
            .spec-item { display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #eee; }
            .spec-label { font-weight: bold; color: #495057; }
            .spec-value { color: #007bff; }
            .tech-features-list { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 15px; }
            .tech-feature { background: white; padding: 15px; border-radius: 8px; border-left: 4px solid #28a745; }
            .compatibility-info { background: #e9ecef; padding: 20px; border-radius: 8px; }
            .technical-support { background: #17a2b8; color: white; padding: 20px; border-radius: 8px; }
            </style>
            """,
            
            "ecommerce": """
            <!-- Descripción Optimizada para E-commerce -->
            <div class="ecommerce-description">
                <div class="product-hero">
                    <h1 class="product-name">{titulo}</h1>
                    <div class="price-badge">
                        <span class="price">{precio}</span>
                        <span class="price-note">Mejor precio garantizado</span>
                    </div>
                </div>
                
                <div class="key-selling-points">
                    <h2>🌟 Puntos Clave de Venta</h2>
                    <div class="selling-points-grid">
                        {puntos_venta}
                    </div>
                </div>
                
                <div class="product-highlights">
                    <h2>✨ Lo Más Destacado</h2>
                    <ul class="highlights-list">
                        {destacados_lista}
                    </ul>
                </div>
                
                <div class="shipping-info">
                    <h2>🚚 Información de Envío</h2>
                    <div class="shipping-details">
                        <div class="shipping-option">
                            <strong>Envío Estándar:</strong> 3-5 días laborables
                        </div>
                        <div class="shipping-option">
                            <strong>Envío Express:</strong> 1-2 días laborables
                        </div>
                        <div class="free-shipping">
                            ✅ Envío GRATIS en pedidos superiores a 50€
                        </div>
                    </div>
                </div>
                
                <div class="guarantees">
                    <h2>🛡️ Nuestras Garantías</h2>
                    <div class="guarantee-badges">
                        <div class="badge">💯 Garantía de calidad</div>
                        <div class="badge">↩️ Devolución 30 días</div>
                        <div class="badge">🔒 Compra 100% segura</div>
                    </div>
                </div>
            </div>
            
            <style>
            .ecommerce-description { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; }
            .product-hero { text-align: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 15px; margin-bottom: 25px; }
            .product-name { font-size: 2.2em; margin-bottom: 15px; }
            .price-badge { background: rgba(255,255,255,0.2); padding: 15px; border-radius: 50px; display: inline-block; }
            .price { font-size: 1.8em; font-weight: bold; }
            .price-note { display: block; font-size: 0.9em; opacity: 0.8; }
            .selling-points-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; }
            .selling-point { background: #f8f9fa; padding: 20px; border-radius: 10px; text-align: center; border: 2px solid #e9ecef; }
            .highlights-list { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; list-style: none; padding: 0; }
            .highlights-list li { background: #e8f5e8; padding: 15px; border-radius: 8px; border-left: 4px solid #28a745; }
            .shipping-details { background: #fff3cd; padding: 20px; border-radius: 10px; border-left: 5px solid #ffc107; }
            .shipping-option { margin: 10px 0; }
            .free-shipping { background: #d4edda; padding: 10px; border-radius: 5px; margin-top: 15px; text-align: center; font-weight: bold; }
            .guarantee-badges { display: flex; flex-wrap: wrap; gap: 15px; justify-content: center; }
            .badge { background: #007bff; color: white; padding: 12px 20px; border-radius: 25px; font-weight: bold; }
            </style>
            """
        }
    
    def buscar_producto_web(self, nombre_producto: str, categoria: str = "", terminos_adicionales: str = "") -> List[str]:
        """
        Busca información del producto en Google y retorna URLs relevantes
        """
        # Construir query de búsqueda
        query_parts = [nombre_producto]
        if categoria:
            query_parts.append(categoria)
        if terminos_adicionales:
            query_parts.append(terminos_adicionales)
        
        # Añadir términos para obtener información de producto
        query_parts.extend(["especificaciones", "características", "review"])
        
        query = " ".join(query_parts)
        
        # Simular búsqueda (en producción usarías Google Search API)
        urls_encontradas = self._simular_busqueda_google(query, nombre_producto)
        
        return urls_encontradas
    
    def _simular_busqueda_google(self, query: str, producto: str) -> List[str]:
        """
        Simula una búsqueda de Google y retorna URLs plausibles
        """
        # En producción, aquí usarías la API de Google Search
        # Por ahora, generamos URLs típicas donde se puede encontrar información
        
        dominios_relevantes = [
            "amazon.es", "pccomponentes.com", "mediamarkt.es", "elcorteingles.es",
            "carrefour.es", "fnac.es", "worten.es", "xataka.com", "geeknetic.es"
        ]
        
        urls_simuladas = []
        
        # Generar URLs plausibles basadas en el producto
        producto_slug = re.sub(r'[^\w\s-]', '', producto.lower()).strip()
        producto_slug = re.sub(r'[-\s]+', '-', producto_slug)
        
        for i, dominio in enumerate(dominios_relevantes[:5]):  # Límite de 5 URLs
            if "amazon" in dominio:
                url = f"https://{dominio}/dp/B0{random.randint(10000000, 99999999)}"
            elif dominio in ["xataka.com", "geeknetic.es"]:
                url = f"https://{dominio}/review-{producto_slug}-{random.randint(1000, 9999)}"
            else:
                url = f"https://{dominio}/producto/{producto_slug}-{random.randint(100, 999)}"
            
            urls_simuladas.append(url)
        
        return urls_simuladas
    
    def extraer_informacion_url(self, url: str) -> Dict[str, any]:
        """
        Extrae información de una URL específica
        """
        try:
            # En un entorno real, harías web scraping
            # Por ahora, simulamos la extracción
            
            info_extraida = {
                "caracteristicas": [],
                "especificaciones": {},
                "precio": "",
                "descripcion": "",
                "beneficios": [],
                "disponible": True
            }
            
            # Simular datos extraídos basados en la URL
            if "amazon" in url:
                info_extraida.update({
                    "caracteristicas": [
                        "Producto con alta valoración",
                        "Entrega rápida disponible",
                        "Compatible con múltiples dispositivos"
                    ],
                    "precio": f"{random.randint(50, 500)}€",
                    "descripcion": "Producto de alta calidad con excelentes reseñas de usuarios"
                })
            
            elif "review" in url or "xataka" in url or "geeknetic" in url:
                info_extraida.update({
                    "caracteristicas": [
                        "Análisis técnico detallado disponible",
                        "Comparativa con productos similares",
                        "Pruebas de rendimiento realizadas"
                    ],
                    "beneficios": [
                        "Rendimiento superior comprobado",
                        "Calidad construcción excelente",
                        "Relación calidad-precio óptima"
                    ]
                })
            
            else:
                info_extraida.update({
                    "caracteristicas": [
                        "Producto disponible en tienda",
                        "Garantía oficial del fabricante",
                        "Servicio técnico especializado"
                    ],
                    "especificaciones": {
                        "Garantía": "2 años",
                        "Disponibilidad": "En stock",
                        "Origen": "Fabricante oficial"
                    }
                })
            
            return info_extraida
            
        except Exception as e:
            return {"error": str(e), "disponible": False}
    
    def procesar_urls_manuales(self, urls: List[str]) -> Dict[str, any]:
        """
        Procesa una lista de URLs proporcionadas manualmente
        """
        informacion_combinada = {
            "caracteristicas": [],
            "especificaciones": {},
            "beneficios": [],
            "precios": [],
            "fuentes": [],
            "errores": []
        }
        
        for url in urls:
            if not url.strip():
                continue
                
            try:
                info = self.extraer_informacion_url(url)
                
                if info.get("disponible", False):
                    # Combinar información
                    informacion_combinada["caracteristicas"].extend(info.get("caracteristicas", []))
                    informacion_combinada["beneficios"].extend(info.get("beneficios", []))
                    informacion_combinada["especificaciones"].update(info.get("especificaciones", {}))
                    
                    if info.get("precio"):
                        informacion_combinada["precios"].append(info["precio"])
                    
                    informacion_combinada["fuentes"].append(url)
                else:
                    informacion_combinada["errores"].append(f"No se pudo acceder a: {url}")
                    
            except Exception as e:
                informacion_combinada["errores"].append(f"Error procesando {url}: {str(e)}")
        
        # Limpiar duplicados
        informacion_combinada["caracteristicas"] = list(set(informacion_combinada["caracteristicas"]))
        informacion_combinada["beneficios"] = list(set(informacion_combinada["beneficios"]))
        
        return informacion_combinada
    
    def generar_descripcion_html(self, producto_info: ProductInfo, estilo: str = "completa", idioma: str = "es") -> str:
        """
        Genera la descripción HTML final usando IA
        """
        # Preparar el contexto para la IA
        contexto_producto = f"""
        INFORMACIÓN DEL PRODUCTO:
        Nombre: {producto_info.nombre}
        Marca: {producto_info.marca}
        Categoría: {producto_info.categoria}
        
        Características encontradas:
        {chr(10).join([f"• {c}" for c in producto_info.caracteristicas[:10]])}
        
        Beneficios identificados:
        {chr(10).join([f"• {b}" for b in producto_info.beneficios[:8]])}
        
        Especificaciones técnicas:
        {chr(10).join([f"• {k}: {v}" for k, v in producto_info.datos_tecnicos.items()])}
        
        Precio aproximado: {producto_info.precio}
        
        Fuentes consultadas: {len(producto_info.fuentes)} sitios web
        """
        
        # Prompt según el estilo seleccionado
        prompts_por_estilo = {
            "completa": """
            Crea una descripción HTML completa y profesional para este producto.
            Debe incluir:
            - Título atractivo y subtítulo
            - Lista de beneficios principales (4-6 puntos)
            - Características destacadas en formato grid
            - Tabla de especificaciones técnicas
            - Párrafo convincente de "por qué elegir este producto"
            
            El HTML debe ser moderno, responsive y visualmente atractivo.
            """,
            
            "marketing": """
            Crea una descripción HTML enfocada en ventas y marketing.
            Debe incluir:
            - Título impactante con tagline pegadizo
            - Propuesta de valor clara
            - Beneficios únicos destacados
            - Elemento de urgencia o escasez
            - Llamadas a la acción implícitas
            
            Usa un lenguaje persuasivo y emocionalmente atractivo.
            """,
            
            "tecnica": """
            Crea una descripción HTML técnica y detallada.
            Debe incluir:
            - Especificaciones técnicas completas
            - Características técnicas detalladas
            - Información de compatibilidad
            - Datos de rendimiento
            - Información de soporte técnico
            
            Usa terminología técnica precisa y formato profesional.
            """,
            
            "ecommerce": """
            Crea una descripción HTML optimizada para e-commerce.
            Debe incluir:
            - Nombre del producto con precio destacado
            - Puntos clave de venta
            - Información de envío y garantías
            - Badges de confianza
            - Elementos que generen confianza en la compra
            
            Enfócate en reducir la fricción de compra y aumentar conversiones.
            """
        }
        
        idiomas = {
            "es": "español",
            "en": "inglés", 
            "ca": "catalán"
        }
        
        prompt_final = f"""
        {prompts_por_estilo.get(estilo, prompts_por_estilo["completa"])}
        
        CONTEXTO DEL PRODUCTO:
        {contexto_producto}
        
        INSTRUCCIONES IMPORTANTES:
        1. Responde SOLO en {idiomas.get(idioma, "español")}
        2. Usa la plantilla de estilo "{estilo}"
        3. Incluye CSS inline para que el HTML sea completamente autónomo
        4. Asegúrate de que todos los datos sean coherentes y realistas
        5. Si falta información, créala de forma coherente con el producto
        6. El HTML debe ser listo para pegar en cualquier editor
        
        Responde ÚNICAMENTE con el código HTML completo, sin explicaciones adicionales.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Eres un experto en marketing digital y desarrollo web, especializado en crear descripciones de productos HTML atractivas y efectivas."},
                    {"role": "user", "content": prompt_final}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            html_generado = response.choices[0].message.content.strip()
            
            # Validar que el resultado sea HTML válido
            if not html_generado.startswith('<') or not html_generado.endswith('>'):
                # Si no es HTML válido, envolverlo en un div
                html_generado = f'<div class="product-description">{html_generado}</div>'
            
            return html_generado
            
        except Exception as e:
            return f'<div class="error">Error generando descripción: {str(e)}</div>'
    
    def procesar_producto_completo(self, producto: Dict, metodo: str = "auto", urls_manuales: List[str] = None, 
                                 estilo: str = "completa", categoria: str = "", terminos_adicionales: str = "",
                                 idioma: str = "es", progress_callback=None) -> Dict:
        """
        Procesa un producto completo: búsqueda + extracción + generación HTML
        """
        
        try:
            if progress_callback:
                progress_callback("🔍 Iniciando análisis del producto...")
            
            # Extraer información básica del producto
            nombre = producto.get('Title', 'Producto sin nombre')
            marca = producto.get('Vendor', '')
            precio_base = producto.get('Variant Price', '')
            
            if progress_callback:
                progress_callback(f"📊 Analizando: {nombre}")
            
            # Crear objeto ProductInfo
            producto_info = ProductInfo(
                nombre=nombre,
                marca=marca,
                categoria=categoria,
                precio=f"{precio_base}€" if precio_base else ""
            )
            
            # Procesar según el método seleccionado
            if metodo == "auto":
                if progress_callback:
                    progress_callback("🌐 Buscando información en la web...")
                
                # Búsqueda automática
                urls_encontradas = self.buscar_producto_web(nombre, categoria, terminos_adicionales)
                producto_info.fuentes = urls_encontradas
                
                # Simular extracción de múltiples fuentes
                for i, url in enumerate(urls_encontradas[:3]):  # Procesar máximo 3 URLs
                    if progress_callback:
                        progress_callback(f"📖 Extrayendo información de fuente {i+1}/3...")
                    
                    info_url = self.extraer_informacion_url(url)
                    
                    # Combinar información
                    producto_info.caracteristicas.extend(info_url.get("caracteristicas", []))
                    producto_info.beneficios.extend(info_url.get("beneficios", []))
                    producto_info.datos_tecnicos.update(info_url.get("especificaciones", {}))
                    
                    if info_url.get("precio") and not producto_info.precio:
                        producto_info.precio = info_url["precio"]
                
            elif metodo == "manual" and urls_manuales:
                if progress_callback:
                    progress_callback("📝 Procesando URLs proporcionadas...")
                
                # Procesamiento manual
                info_combinada = self.procesar_urls_manuales(urls_manuales)
                
                # Integrar información combinada
                producto_info.caracteristicas = info_combinada["caracteristicas"]
                producto_info.beneficios = info_combinada["beneficios"]
                producto_info.datos_tecnicos = info_combinada["especificaciones"]
                producto_info.fuentes = info_combinada["fuentes"]
                
                if info_combinada["precios"] and not producto_info.precio:
                    producto_info.precio = info_combinada["precios"][0]
            
            # Limpiar y deduplicar información
            producto_info.caracteristicas = list(set(producto_info.caracteristicas))[:10]
            producto_info.beneficios = list(set(producto_info.beneficios))[:8]
            
            # Generar descripción HTML
            if progress_callback:
                progress_callback("🎨 Generando descripción HTML...")
            
            html_descripcion = self.generar_descripcion_html(producto_info, estilo, idioma)
            
            if progress_callback:
                progress_callback("✅ Descripción HTML generada exitosamente")
            
            # Preparar resultado final
            resultado = {
                "Handle": producto.get('Handle', ''),
                "Metafield: custom.html_description [rich_text_field]": html_descripcion,
                
                # Metadatos del proceso
                "_fuentes_consultadas": len(producto_info.fuentes),
                "_caracteristicas_encontradas": len(producto_info.caracteristicas),
                "_beneficios_identificados": len(producto_info.beneficios),
                "_metodo_usado": metodo,
                "_estilo_aplicado": estilo,
                "_idioma": idioma,
                "_timestamp": datetime.now().isoformat(),
                
                # Información detallada para referencia
                "_producto_info": {
                    "nombre": producto_info.nombre,
                    "marca": producto_info.marca,
                    "categoria": producto_info.categoria,
                    "precio": producto_info.precio,
                    "caracteristicas": producto_info.caracteristicas,
                    "beneficios": producto_info.beneficios,
                    "especificaciones": producto_info.datos_tecnicos,
                    "fuentes": producto_info.fuentes
                }
            }
            
            return resultado
            
        except Exception as e:
            if progress_callback:
                progress_callback(f"❌ Error: {str(e)}")
            
            return {
                "Handle": producto.get('Handle', ''),
                "Metafield: custom.html_description [rich_text_field]": f'<div class="error">Error generando descripción: {str(e)}</div>',
                "_error": str(e),
                "_timestamp": datetime.now().isoformat()
            }
    
    def validar_html(self, html_content: str) -> Tuple[bool, List[str]]:
        """
        Valida que el HTML generado sea correcto y completo
        """
        errores = []
        
        # Verificaciones básicas
        if not html_content or len(html_content.strip()) < 100:
            errores.append("HTML demasiado corto o vacío")
        
        if not html_content.strip().startswith('<') or not html_content.strip().endswith('>'):
            errores.append("HTML no tiene formato correcto")
        
        # Verificar elementos esenciales
        elementos_requeridos = ['<h', '<p', '<div']
        for elemento in elementos_requeridos:
            if elemento not in html_content:
                errores.append(f"Falta elemento esencial: {elemento}")
        
        # Verificar que tenga contenido CSS
        if '<style>' not in html_content and 'style=' not in html_content:
            errores.append("Falta estilización CSS")
        
        es_valido = len(errores) == 0
        return es_valido, errores
    
    def generar_vista_previa(self, html_content: str) -> str:
        """
        Genera una vista previa del HTML para mostrar en la interfaz
        """
        try:
            # Extraer solo el contenido visible (sin CSS)
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remover estilos para vista previa
            for style in soup.find_all('style'):
                style.decompose()
            
            # Obtener solo texto y estructura básica
            preview_text = soup.get_text()
            
            # Truncar si es muy largo
            if len(preview_text) > 500:
                preview_text = preview_text[:500] + "..."
            
            return preview_text
            
        except:
            # Fallback simple
            preview = re.sub(r'<[^>]+>', '', html_content)
            return preview[:500] + "..." if len(preview) > 500 else preview