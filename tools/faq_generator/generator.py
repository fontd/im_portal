# tools/faq_generator/generator.py
import pandas as pd
from openai import OpenAI
from typing import Dict, List, Tuple, Optional, Set
import json
import time
from datetime import datetime
import re
import random
import hashlib
from collections import defaultdict
import numpy as np
from dataclasses import dataclass, field
import pickle
import os

@dataclass
class ProductProfile:
    """Perfil completo del producto con análisis profundo"""
    tipo_producto: str
    categoria_principal: str
    subcategorias: List[str]
    ingredientes_clave: List[str]
    beneficios_principales: List[str]
    tipo_piel_objetivo: List[str]
    rango_edad: str
    nivel_precio: str
    complejidad_uso: str
    tiempo_resultados: str
    compatibilidades: Dict[str, bool]
    contraindicaciones: List[str]
    momento_aplicacion: List[str]
    textura: str
    aroma: str
    packaging: str
    certificaciones: List[str]
    tecnologia_exclusiva: str
    comparacion_competencia: Dict[str, str]
    puntos_dolor_cliente: List[str]
    objeciones_compra: List[str]

class PremiumCosmeticsFAQGenerator:
    """
    Generador ULTRA-PREMIUM de FAQs v3.0
    Sistema de inteligencia contextual avanzada con anti-repetición absoluta
    """
    
    def __init__(self, api_key: str, cache_dir: str = "./faq_cache"):
        self.client = OpenAI(api_key=api_key)
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        
        # Cache de preguntas generadas para evitar repeticiones
        self.preguntas_historicas = self._cargar_historico()
        
        # Sistema de perfiles de compradores
        self.perfiles_compradores = {
            "experto": {
                "preocupaciones": ["composición química", "concentraciones", "pH", "estudios clínicos"],
                "lenguaje": "técnico",
                "profundidad": "muy alta"
            },
            "principiante": {
                "preocupaciones": ["facilidad de uso", "resultados visibles", "precio-valor", "seguridad"],
                "lenguaje": "simple",
                "profundidad": "media"
            },
            "luxury": {
                "preocupaciones": ["exclusividad", "experiencia sensorial", "packaging", "prestigio"],
                "lenguaje": "sofisticado",
                "profundidad": "alta"
            },
            "consciente": {
                "preocupaciones": ["sostenibilidad", "cruelty-free", "ingredientes naturales", "ética"],
                "lenguaje": "informativo",
                "profundidad": "alta"
            },
            "problemático": {
                "preocupaciones": ["solución específica", "compatibilidad", "irritación", "resultados rápidos"],
                "lenguaje": "empático",
                "profundidad": "muy alta"
            }
        }
        
        # Banco expandido de plantillas de preguntas con variaciones
        self.banco_preguntas_premium = {
            "eficacia": {
                "plantillas": [
                    "¿Cuánto tarda {producto} en mostrar resultados visibles en {problema_especifico}?",
                    "¿Qué porcentaje de mejora puedo esperar con {producto} en {timeframe}?",
                    "¿Cómo maximizo la efectividad de {producto} para {objetivo}?",
                    "¿Los resultados de {producto} son permanentes o reversibles?",
                    "¿Existe un período de purga al comenzar con {producto}?",
                    "¿Qué estudios respaldan la eficacia de {producto}?",
                    "¿Cómo sé si {producto} está funcionando correctamente en mi piel?",
                    "¿Puedo acelerar los resultados de {producto} de alguna manera?"
                ],
                "variables": {
                    "problema_especifico": ["manchas oscuras", "líneas finas", "poros dilatados", "textura irregular", "opacidad"],
                    "timeframe": ["2 semanas", "1 mes", "3 meses", "6 meses"],
                    "objetivo": ["anti-edad", "luminosidad", "hidratación profunda", "control de grasa"]
                }
            },
            "tecnica_aplicacion": {
                "plantillas": [
                    "¿Cuál es la cantidad exacta de {producto} que debo aplicar?",
                    "¿Qué técnica de masaje optimiza la absorción de {producto}?",
                    "¿Debo aplicar {producto} con las manos o con herramientas?",
                    "¿Importa la dirección de aplicación de {producto}?",
                    "¿Cuánto tiempo espero entre {producto} y el siguiente paso?",
                    "¿{producto} se aplica en piel húmeda o seca?",
                    "¿Puedo mezclar {producto} con otros productos?",
                    "¿Necesito preparar mi piel antes de aplicar {producto}?"
                ],
                "variables": {}
            },
            "compatibilidad_avanzada": {
                "plantillas": [
                    "¿Puedo usar {producto} si estoy en tratamiento con {tratamiento}?",
                    "¿{producto} es compatible con {ingrediente_activo}?",
                    "¿Interfiere {producto} con procedimientos estéticos como {procedimiento}?",
                    "¿Cómo incorporo {producto} si ya uso {rutina_existente}?",
                    "¿Hay algún ingrediente que neutralice la acción de {producto}?",
                    "¿Puedo usar {producto} en {condicion_piel} activa?",
                    "¿{producto} altera la eficacia de mi {otro_producto}?",
                    "¿Qué pH debe tener mi piel para usar {producto}?"
                ],
                "variables": {
                    "tratamiento": ["retinoides", "antibióticos tópicos", "corticoides", "isotretinoína"],
                    "ingrediente_activo": ["vitamina C", "niacinamida", "AHA/BHA", "retinol"],
                    "procedimiento": ["láser", "peeling", "microagujas", "botox"],
                    "rutina_existente": ["ácidos diarios", "vitamina C", "retinol nocturno"],
                    "condicion_piel": ["rosácea", "dermatitis", "acné", "melasma"],
                    "otro_producto": ["protector solar", "maquillaje", "sérum", "tratamiento médico"]
                }
            },
            "ciencia_ingredientes": {
                "plantillas": [
                    "¿Qué concentración de {ingrediente} contiene {producto} y por qué?",
                    "¿Cómo penetra {ingrediente} de {producto} en las capas de la piel?",
                    "¿El {ingrediente} en {producto} es de origen {origen}?",
                    "¿Qué tecnología de encapsulación usa {producto} para {ingrediente}?",
                    "¿A qué pH está formulado {producto} y cómo afecta su eficacia?",
                    "¿Qué tamaño molecular tiene el {ingrediente} en {producto}?",
                    "¿{producto} contiene {ingrediente} en su forma más biodisponible?",
                    "¿Cómo protege {producto} la estabilidad de {ingrediente}?"
                ],
                "variables": {
                    "ingrediente": ["ácido hialurónico", "vitamina C", "retinol", "péptidos", "niacinamida"],
                    "origen": ["marino", "botánico", "sintético", "biotecnológico"]
                }
            },
            "experiencia_sensorial": {
                "plantillas": [
                    "¿Qué textura exacta tiene {producto} y cómo se siente?",
                    "¿{producto} deja algún residuo o finish en la piel?",
                    "¿Tiene {producto} fragancia y de qué tipo?",
                    "¿Cómo es la experiencia completa de usar {producto}?",
                    "¿El color de {producto} es normal o indica algo?",
                    "¿Por qué {producto} tiene esa consistencia específica?",
                    "¿Es normal que {producto} produzca {sensacion}?",
                    "¿Cambia la textura de {producto} con la temperatura?"
                ],
                "variables": {
                    "sensacion": ["hormigueo", "calor", "frescor", "tensión"]
                }
            },
            "situaciones_especificas": {
                "plantillas": [
                    "¿Puedo usar {producto} en {clima} extremo?",
                    "¿Cómo adapto el uso de {producto} durante {estacion}?",
                    "¿{producto} es seguro durante {condicion_especial}?",
                    "¿Puedo llevar {producto} en {situacion_viaje}?",
                    "¿Afecta {factor_externo} la eficacia de {producto}?",
                    "¿Necesito ajustar {producto} según mi {factor_personal}?",
                    "¿Cómo conservo {producto} en {condicion_almacenamiento}?",
                    "¿{producto} requiere cuidados especiales en {escenario}?"
                ],
                "variables": {
                    "clima": ["húmedo", "seco", "frío", "caluroso"],
                    "estacion": ["verano", "invierno", "primavera", "otoño"],
                    "condicion_especial": ["embarazo", "lactancia", "menopausia", "adolescencia"],
                    "situacion_viaje": ["cabina de avión", "equipaje facturado", "climas extremos"],
                    "factor_externo": ["contaminación", "agua dura", "exposición solar", "aire acondicionado"],
                    "factor_personal": ["edad", "tipo de piel", "sensibilidad", "medicación"],
                    "condicion_almacenamiento": ["baño húmedo", "nevera", "calor extremo"],
                    "escenario": ["post-procedimiento", "piel sensibilizada", "brote activo"]
                }
            },
            "comparacion_inteligente": {
                "plantillas": [
                    "¿En qué se diferencia {producto} de versiones anteriores?",
                    "¿Por qué {producto} cuesta más que alternativas similares?",
                    "¿Qué hace único a {producto} frente a {competencia}?",
                    "¿Vale la pena cambiar de {producto_anterior} a {producto}?",
                    "¿Qué ventaja tecnológica tiene {producto} sobre otros?",
                    "¿Por qué elegir {producto} si ya uso {alternativa}?",
                    "¿Qué problema resuelve {producto} que otros no?",
                    "¿Cómo justifico la inversión en {producto}?"
                ],
                "variables": {
                    "competencia": ["productos genéricos", "otras marcas premium", "versiones anteriores"],
                    "producto_anterior": ["mi sérum actual", "mi crema habitual", "tratamientos caseros"],
                    "alternativa": ["productos médicos", "tratamientos en cabina", "otras marcas"]
                }
            },
            "troubleshooting": {
                "plantillas": [
                    "¿Qué hago si {producto} me causa {reaccion}?",
                    "¿Por qué {producto} no muestra resultados después de {tiempo}?",
                    "¿Es normal que {producto} {cambio_inesperado}?",
                    "¿Cómo sé si {producto} se ha estropeado?",
                    "¿Por qué mi piel reacciona así a {producto}?",
                    "¿Debo suspender {producto} si {situacion}?",
                    "¿Cómo minimizo {efecto_secundario} de {producto}?",
                    "¿Qué indica {sintoma} al usar {producto}?"
                ],
                "variables": {
                    "reaccion": ["rojez", "descamación", "granitos", "picor"],
                    "tiempo": ["2 semanas", "1 mes", "3 meses"],
                    "cambio_inesperado": ["cambia de color", "se separa", "huele diferente", "cristaliza"],
                    "situacion": ["tengo un evento importante", "mi piel está irritada", "empiezo otro tratamiento"],
                    "efecto_secundario": ["sequedad inicial", "purga", "sensibilidad"],
                    "sintoma": ["hormigueo", "tirantez", "brillo excesivo", "absorción lenta"]
                }
            }
        }
        
        # Sistema de respuestas contextuales
        self.plantillas_respuestas = {
            "datos_clinicos": [
                "Estudios clínicos demuestran que {dato_especifico} en {timeframe}.",
                "El {porcentaje}% de usuarios reportaron {beneficio} tras {periodo}.",
                "Tests dermatológicos confirman {resultado} con uso {frecuencia}."
            ],
            "instrucciones_precision": [
                "Aplique {cantidad} ({medida}) con movimientos {tecnica} durante {tiempo}.",
                "La técnica óptima incluye {paso1}, seguido de {paso2} para {objetivo}.",
                "Para máxima eficacia: {instruccion_detallada} en {zona} específicamente."
            ],
            "explicacion_cientifica": [
                "El {ingrediente} a {concentracion}% penetra hasta {capa_piel} donde {accion}.",
                "La tecnología {nombre_tecnologia} permite que {beneficio_tecnico}.",
                "Formulado a pH {valor} para {razon_cientifica} sin comprometer {aspecto}."
            ]
        }
        
        # Métricas avanzadas de calidad
        self.metricas_calidad = {
            "longitud_optima": {"min": 220, "max": 320, "ideal": 270},
            "complejidad_lexica": {"min": 0.4, "max": 0.7},  # Índice de diversidad léxica
            "densidad_informacion": {"min": 3, "ideal": 5},  # Datos por respuesta
            "especificidad": {"min": 0.6, "max": 0.9},  # Ratio términos específicos/genéricos
            "coherencia_tematica": {"min": 0.8}  # Similitud semántica pregunta-respuesta
        }
    
    def _cargar_historico(self) -> Set[str]:
        """Carga el histórico de preguntas para evitar repeticiones"""
        historico_path = os.path.join(self.cache_dir, "preguntas_historicas.pkl")
        if os.path.exists(historico_path):
            with open(historico_path, 'rb') as f:
                return pickle.load(f)
        return set()
    
    def _guardar_historico(self):
        """Guarda el histórico actualizado"""
        historico_path = os.path.join(self.cache_dir, "preguntas_historicas.pkl")
        with open(historico_path, 'wb') as f:
            pickle.dump(self.preguntas_historicas, f)
    
    def _generar_hash_pregunta(self, pregunta: str) -> str:
        """Genera hash único para cada pregunta"""
        pregunta_normalizada = re.sub(r'[^\w\s]', '', pregunta.lower())
        return hashlib.md5(pregunta_normalizada.encode()).hexdigest()
    
    def analizar_producto_ultra_profundo(self, producto: Dict) -> ProductProfile:
        """Análisis ultra-profundo del producto con IA"""
        descripcion = self.obtener_descripcion_producto(producto)
        titulo = producto.get('Title', '')
        precio = float(producto.get('Variant Price', 0))
        vendor = producto.get('Vendor', '')
        tags = producto.get('Tags', '')
        
        # Análisis contextual con GPT
        prompt_analisis = f"""
        Analiza este producto cosmético en profundidad y extrae un perfil COMPLETO:
        
        Producto: {titulo}
        Marca: {vendor}
        Precio: {precio}€
        Descripción: {descripcion[:1000]}
        Tags: {tags}
        
        Devuelve un JSON con TODOS estos campos (inventa datos coherentes si no están explícitos):
        {{
            "tipo_producto": "serum/crema/limpiador/etc",
            "categoria_principal": "antiedad/hidratante/tratamiento/etc",
            "subcategorias": ["lista de subcategorías"],
            "ingredientes_clave": ["lista de ingredientes principales"],
            "beneficios_principales": ["lista de beneficios específicos"],
            "tipo_piel_objetivo": ["normal", "seca", "grasa", "mixta", "sensible"],
            "rango_edad": "25-35/35-45/45+/todos",
            "nivel_precio": "premium/lujo/accesible",
            "complejidad_uso": "simple/moderada/avanzada",
            "tiempo_resultados": "inmediato/2-4 semanas/1-3 meses",
            "momento_aplicacion": ["mañana", "noche", "ambos"],
            "textura": "descripción específica",
            "tecnologia_exclusiva": "nombre o descripción de tecnología patentada",
            "puntos_dolor_cliente": ["preocupaciones que resuelve"],
            "objeciones_compra": ["posibles dudas del cliente"]
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Eres un experto en análisis de productos cosméticos."},
                    {"role": "user", "content": prompt_analisis}
                ],
                temperature=0.3
            )
            
            perfil_dict = json.loads(response.choices[0].message.content)
            
            # Completar campos faltantes con valores por defecto
            return ProductProfile(
                tipo_producto=perfil_dict.get('tipo_producto', 'cosmético'),
                categoria_principal=perfil_dict.get('categoria_principal', 'tratamiento'),
                subcategorias=perfil_dict.get('subcategorias', []),
                ingredientes_clave=perfil_dict.get('ingredientes_clave', []),
                beneficios_principales=perfil_dict.get('beneficios_principales', []),
                tipo_piel_objetivo=perfil_dict.get('tipo_piel_objetivo', ['todos']),
                rango_edad=perfil_dict.get('rango_edad', 'todos'),
                nivel_precio=perfil_dict.get('nivel_precio', 'premium'),
                complejidad_uso=perfil_dict.get('complejidad_uso', 'simple'),
                tiempo_resultados=perfil_dict.get('tiempo_resultados', '2-4 semanas'),
                compatibilidades={},
                contraindicaciones=[],
                momento_aplicacion=perfil_dict.get('momento_aplicacion', ['mañana', 'noche']),
                textura=perfil_dict.get('textura', 'ligera'),
                aroma='sin fragancia',
                packaging='elegante',
                certificaciones=[],
                tecnologia_exclusiva=perfil_dict.get('tecnologia_exclusiva', ''),
                comparacion_competencia={},
                puntos_dolor_cliente=perfil_dict.get('puntos_dolor_cliente', []),
                objeciones_compra=perfil_dict.get('objeciones_compra', [])
            )
        except:
            # Fallback a análisis básico
            return self._analisis_basico_fallback(producto)
    
    def _analisis_basico_fallback(self, producto: Dict) -> ProductProfile:
        """Análisis básico cuando falla el análisis con IA"""
        titulo = producto.get('Title', '').lower()
        precio = float(producto.get('Variant Price', 0))
        
        # Detectar tipo básico
        if 'serum' in titulo or 'sérum' in titulo:
            tipo = 'serum'
        elif 'crema' in titulo or 'cream' in titulo:
            tipo = 'crema'
        elif 'limpiador' in titulo or 'cleanser' in titulo:
            tipo = 'limpiador'
        else:
            tipo = 'tratamiento'
        
        return ProductProfile(
            tipo_producto=tipo,
            categoria_principal='tratamiento' if precio > 50 else 'cuidado básico',
            subcategorias=[],
            ingredientes_clave=[],
            beneficios_principales=[],
            tipo_piel_objetivo=['todos'],
            rango_edad='todos',
            nivel_precio='premium' if precio > 80 else 'medio',
            complejidad_uso='simple',
            tiempo_resultados='2-4 semanas',
            compatibilidades={},
            contraindicaciones=[],
            momento_aplicacion=['mañana', 'noche'],
            textura='ligera',
            aroma='sin fragancia',
            packaging='estándar',
            certificaciones=[],
            tecnologia_exclusiva='',
            comparacion_competencia={},
            puntos_dolor_cliente=[],
            objeciones_compra=[]
        )
    
    def generar_preguntas_ultra_contextuales(self, producto: Dict, perfil: ProductProfile, perfil_comprador: str) -> List[Dict]:
        """Genera preguntas ultra-específicas basadas en el contexto completo"""
        preguntas_generadas = []
        categorias_seleccionadas = random.sample(list(self.banco_preguntas_premium.keys()), 5)
        
        for categoria in categorias_seleccionadas:
            plantillas = self.banco_preguntas_premium[categoria]["plantillas"]
            variables = self.banco_preguntas_premium[categoria].get("variables", {})
            
            # Seleccionar plantilla no usada
            plantilla_base = None
            for plantilla in random.sample(plantillas, len(plantillas)):
                # Sustituir variables básicas
                pregunta = plantilla.replace("{producto}", producto.get('Title', 'este producto'))
                
                # Sustituir variables contextuales
                for var, opciones in variables.items():
                    if f"{{{var}}}" in pregunta:
                        opcion = random.choice(opciones)
                        pregunta = pregunta.replace(f"{{{var}}}", opcion)
                
                # Verificar que no se haya usado antes
                hash_pregunta = self._generar_hash_pregunta(pregunta)
                if hash_pregunta not in self.preguntas_historicas:
                    plantilla_base = pregunta
                    self.preguntas_historicas.add(hash_pregunta)
                    break
            
            if plantilla_base:
                # Personalizar según perfil del producto
                contexto_pregunta = self._personalizar_pregunta_perfil(plantilla_base, perfil, perfil_comprador)
                
                preguntas_generadas.append({
                    "categoria": categoria,
                    "pregunta": contexto_pregunta,
                    "perfil_comprador": perfil_comprador,
                    "contexto_producto": perfil
                })
        
        return preguntas_generadas
    
    def _personalizar_pregunta_perfil(self, pregunta: str, perfil: ProductProfile, perfil_comprador: str) -> str:
        """Personaliza la pregunta según el perfil del producto y comprador"""
        # Agregar contexto específico del producto
        if perfil.nivel_precio == "lujo" and "precio" in pregunta.lower():
            pregunta = pregunta.replace("?", " considerando su posicionamiento premium?")
        
        if perfil.ingredientes_clave and "ingrediente" in pregunta.lower():
            ingrediente = random.choice(perfil.ingredientes_clave[:3])
            pregunta = pregunta.replace("ingrediente activo", ingrediente)
        
        if perfil.puntos_dolor_cliente and "problema" in pregunta.lower():
            problema = random.choice(perfil.puntos_dolor_cliente)
            pregunta = pregunta.replace("problema específico", problema)
        
        return pregunta
    
    def generar_respuesta_ultra_contextual(self, pregunta: Dict, producto: Dict, perfil: ProductProfile) -> str:
        """Genera respuestas ultra-específicas y contextuales"""
        categoria = pregunta["categoria"]
        perfil_comprador = pregunta["perfil_comprador"]
        
        # Prompt ultra-específico
        prompt_respuesta = f"""
        Eres un dermatólogo experto respondiendo a un cliente {perfil_comprador}.
        
        PRODUCTO: {producto.get('Title')}
        PRECIO: {producto.get('Variant Price')}€
        PERFIL: {perfil.tipo_producto} - {perfil.categoria_principal}
        INGREDIENTES CLAVE: {', '.join(perfil.ingredientes_clave[:3])}
        BENEFICIOS: {', '.join(perfil.beneficios_principales[:3])}
        
        PREGUNTA: {pregunta['pregunta']}
        CATEGORÍA: {categoria}
        
        INSTRUCCIONES CRÍTICAS:
        1. Responde en EXACTAMENTE 220-320 caracteres (4-5 frases)
        2. Incluye MÍNIMO 3 de estos elementos:
           - Dato numérico específico (%, mg, días, etc.)
           - Instrucción práctica paso a paso
           - Referencia a ingrediente con su acción
           - Comparación o diferenciación
           - Consejo profesional basado en experiencia
        
        3. Usa lenguaje {self.perfiles_compradores[perfil_comprador]['lenguaje']}
        4. NO uses palabras genéricas: cosa, algo, etc, básicamente
        5. Sé ULTRA-ESPECÍFICO para ESTE producto exacto
        6. Incluye detalles que solo un experto conocería
        
        Responde SOLO con el texto de la respuesta, sin comillas ni formato.
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Experto dermatólogo con 20 años de experiencia. Respuestas precisas y específicas."},
                {"role": "user", "content": prompt_respuesta}
            ],
            temperature=0.8,
            max_tokens=150
        )
        
        return response.choices[0].message.content.strip()
    
    def validar_calidad_ultra(self, faqs: Dict) -> Tuple[bool, Dict]:
        """Validación ultra-estricta con métricas avanzadas"""
        metricas_detalladas = {}
        puntuacion_total = 0
        
        for i in range(1, 6):
            faq = faqs.get(f'faq{i}', {})
            pregunta = faq.get('pregunta', '')
            respuesta = faq.get('respuesta', '')
            
            metricas_faq = {
                'longitud_pregunta': len(pregunta.split()),
                'longitud_respuesta': len(respuesta),
                'datos_numericos': len(re.findall(r'\d+[%\s]*(mg|ml|%|días?|semanas?|meses?|€)', respuesta)),
                'terminos_tecnicos': sum(1 for term in ['dermatológicamente', 'clínicamente', 'activos', 'penetración', 'biodisponible', 'encapsulado'] if term in respuesta.lower()),
                'instrucciones': bool(re.search(r'(aplica|usa|masajea|espera|evita|combina)', respuesta.lower())),
                'especificidad': 1 - (sum(1 for palabra in ['cosa', 'algo', 'producto', 'esto'] if palabra in respuesta.lower()) / len(respuesta.split())),
                'diversidad_lexica': len(set(respuesta.lower().split())) / len(respuesta.split()) if respuesta else 0,
                'tiene_comparacion': bool(re.search(r'(mejor que|a diferencia de|mientras que|frente a)', respuesta.lower())),
                'formato_pregunta': pregunta.startswith('¿') and pregunta.endswith('?')
            }
            
            # Calcular puntuación
            puntuacion = 0
            
            # Longitud óptima
            if 220 <= metricas_faq['longitud_respuesta'] <= 320:
                puntuacion += 3
            elif 200 <= metricas_faq['longitud_respuesta'] <= 350:
                puntuacion += 2
            else:
                puntuacion += 1
            
            # Datos numéricos (crítico)
            puntuacion += min(metricas_faq['datos_numericos'] * 2, 6)
            
            # Términos técnicos
            puntuacion += min(metricas_faq['terminos_tecnicos'] * 1.5, 4)
            
            # Instrucciones prácticas
            if metricas_faq['instrucciones']:
                puntuacion += 2
            
            # Especificidad alta
            if metricas_faq['especificidad'] > 0.95:
                puntuacion += 3
            
            # Diversidad léxica
            if metricas_faq['diversidad_lexica'] > 0.6:
                puntuacion += 2
            
            # Comparación o diferenciación
            if metricas_faq['tiene_comparacion']:
                puntuacion += 2
            
            # Formato correcto
            if metricas_faq['formato_pregunta']:
                puntuacion += 1
            
            metricas_faq['puntuacion'] = puntuacion
            metricas_detalladas[f'faq{i}'] = metricas_faq
            puntuacion_total += puntuacion
        
        # Calcular métricas globales
        puntuacion_promedio = puntuacion_total / 5
        
        # Detectar patrones no deseados
        todas_respuestas = ' '.join([faqs[f'faq{i}']['respuesta'] for i in range(1, 6)])
        patrones_repetitivos = self._detectar_patrones_repetitivos(todas_respuestas)
        
        # Verificar diversidad de categorías
        diversidad_tematica = self._calcular_diversidad_tematica(faqs)
        
        # Calidad global
        calidad_niveles = {
            "LEGENDARIA": puntuacion_promedio >= 18,
            "EXCEPCIONAL": puntuacion_promedio >= 15,
            "EXCELENTE": puntuacion_promedio >= 12,
            "BUENA": puntuacion_promedio >= 9,
            "ACEPTABLE": puntuacion_promedio >= 6,
            "INSUFICIENTE": puntuacion_promedio < 6
        }
        
        calidad = next(nivel for nivel, condicion in calidad_niveles.items() if condicion)
        
        es_valido = (
            puntuacion_promedio >= 9 and
            patrones_repetitivos < 0.15 and
            diversidad_tematica > 0.7
        )
        
        metricas_globales = {
            'puntuacion_total': puntuacion_total,
            'puntuacion_promedio': puntuacion_promedio,
            'calidad': calidad,
            'patrones_repetitivos': patrones_repetitivos,
            'diversidad_tematica': diversidad_tematica,
            'detalle_faqs': metricas_detalladas,
            'es_valido': es_valido
        }
        
        return es_valido, metricas_globales
    
    def _detectar_patrones_repetitivos(self, texto: str) -> float:
        """Detecta frases o estructuras repetitivas"""
        frases = texto.split('.')
        frases_unicas = set(frases)
        return 1 - (len(frases_unicas) / len(frases) if frases else 1)
    
    def _calcular_diversidad_tematica(self, faqs: Dict) -> float:
        """Calcula la diversidad temática de las preguntas"""
        temas = []
        palabras_clave_por_tema = {
            'aplicacion': ['aplicar', 'usar', 'cantidad', 'técnica', 'masaje'],
            'ingredientes': ['ingrediente', 'activo', 'concentración', 'fórmula', 'contiene'],
            'resultados': ['resultado', 'tiempo', 'mejora', 'cambio', 'efecto'],
            'compatibilidad': ['combinar', 'mezclar', 'compatible', 'interferir', 'junto'],
            'seguridad': ['seguro', 'irritación', 'alergia', 'sensible', 'reacción']
        }
        
        for i in range(1, 6):
            pregunta = faqs[f'faq{i}']['pregunta'].lower()
            tema_detectado = 'otro'
            
            for tema, palabras in palabras_clave_por_tema.items():
                if any(palabra in pregunta for palabra in palabras):
                    tema_detectado = tema
                    break
            
            temas.append(tema_detectado)
        
        return len(set(temas)) / 5
    
    def generar_faqs_ultra_premium(self, producto: Dict, progress_callback=None, max_intentos: int = 3, modelo: str = "gpt-4") -> Dict:
        """Generación ultra-premium con sistema completo de optimización"""
        
        # Análisis ultra-profundo
        if progress_callback:
            progress_callback("🔍 Analizando producto en profundidad...")
        
        perfil = self.analizar_producto_ultra_profundo(producto)
        
        # Seleccionar perfil de comprador aleatorio para este producto
        perfil_comprador = random.choice(list(self.perfiles_compradores.keys()))
        
        mejor_resultado = None
        mejor_puntuacion = 0
        historial_completo = []
        
        for intento in range(max_intentos):
            if progress_callback:
                progress_callback(f"🎯 Generando FAQs premium (Intento {intento + 1}/{max_intentos})")
            
            try:
                # Generar preguntas contextuales
                preguntas = self.generar_preguntas_ultra_contextuales(producto, perfil, perfil_comprador)
                
                # Ensure we have at least 5 questions
                if len(preguntas) < 5:
                    if progress_callback:
                        progress_callback(f"⚠️ Solo se generaron {len(preguntas)} preguntas, reintentando...")
                    continue
                
                # Generar respuestas para cada pregunta
                faqs = {}
                for idx, pregunta_data in enumerate(preguntas[:5], 1):  # Limit to first 5
                    try:
                        respuesta = self.generar_respuesta_ultra_contextual(pregunta_data, producto, perfil)
                        
                        # Validar longitud y ajustar si es necesario
                        if len(respuesta) < 220:
                            respuesta = self._expandir_respuesta(respuesta, pregunta_data, perfil)
                        elif len(respuesta) > 320:
                            respuesta = self._comprimir_respuesta(respuesta)
                        
                        faqs[f'faq{idx}'] = {
                            'pregunta': pregunta_data['pregunta'],
                            'respuesta': respuesta
                        }
                    except Exception as e:
                        if progress_callback:
                            progress_callback(f"⚠️ Error generando FAQ {idx}: {str(e)}")
                        # Skip this FAQ and continue
                        continue
                
                # Ensure we have exactly 5 FAQs before proceeding
                if len(faqs) < 5:
                    if progress_callback:
                        progress_callback(f"⚠️ Solo se completaron {len(faqs)} FAQs, reintentando...")
                    continue
                
                # Validar calidad
                es_valido, metricas = self.validar_calidad_ultra(faqs)
                
                historial_completo.append({
                    'intento': intento + 1,
                    'calidad': metricas['calidad'],
                    'puntuacion': metricas['puntuacion_promedio'],
                    'metricas': metricas
                })
                
                if metricas['puntuacion_promedio'] > mejor_puntuacion:
                    mejor_puntuacion = metricas['puntuacion_promedio']
                    mejor_resultado = {
                        'faqs': faqs,
                        'metricas': metricas,
                        'perfil': perfil,
                        'perfil_comprador': perfil_comprador
                    }
                
                if progress_callback:
                    progress_callback(f"✨ Calidad: {metricas['calidad']} (Puntuación: {metricas['puntuacion_promedio']:.1f}/20)")
                
                # Si alcanzamos calidad excepcional o legendaria, paramos
                if metricas['calidad'] in ['LEGENDARIA', 'EXCEPCIONAL']:
                    if progress_callback:
                        progress_callback(f"🏆 ¡Calidad {metricas['calidad']} alcanzada!")
                    break
                
                # Esperar entre intentos
                if intento < max_intentos - 1:
                    time.sleep(1)
                    
            except Exception as e:
                if progress_callback:
                    progress_callback(f"⚠️ Error en intento {intento + 1}: {str(e)}")
                continue
        
        # Guardar histórico de preguntas
        self._guardar_historico()
        
        if mejor_resultado:
            # Preparar resultado final con toda la metadata
            resultado_final = self._preparar_resultado_final(producto, mejor_resultado, historial_completo)
            return resultado_final
        
        return None
    
    def _expandir_respuesta(self, respuesta: str, pregunta_data: Dict, perfil: ProductProfile) -> str:
        """Expande respuestas que son muy cortas"""
        expansion_prompts = [
            f" Específicamente, {random.choice(perfil.beneficios_principales[:2])}.",
            f" Los estudios confirman resultados en {random.randint(2, 8)} semanas.",
            f" Recomendado especialmente para {random.choice(perfil.tipo_piel_objetivo)}.",
            f" Su tecnología {perfil.tecnologia_exclusiva or 'avanzada'} garantiza máxima eficacia."
        ]
        
        if len(respuesta) < 220:
            respuesta += random.choice(expansion_prompts)
        
        return respuesta[:320]  # Asegurar no exceder el máximo
    
    def _comprimir_respuesta(self, respuesta: str) -> str:
        """Comprime respuestas que son muy largas manteniendo la información clave"""
        # Dividir en oraciones
        oraciones = re.split(r'(?<=[.!?])\s+', respuesta)
        
        # Priorizar oraciones con datos numéricos o términos técnicos
        oraciones_puntuadas = []
        for oracion in oraciones:
            puntos = 0
            if re.search(r'\d+', oracion):
                puntos += 2
            if any(term in oracion.lower() for term in ['específicamente', 'clínicamente', 'demostrado']):
                puntos += 1
            oraciones_puntuadas.append((oracion, puntos))
        
        # Ordenar por puntuación y reconstruir
        oraciones_puntuadas.sort(key=lambda x: x[1], reverse=True)
        
        respuesta_comprimida = ""
        for oracion, _ in oraciones_puntuadas:
            if len(respuesta_comprimida) + len(oracion) <= 320:
                respuesta_comprimida += oracion + " "
            else:
                break
        
        return respuesta_comprimida.strip()
    
    def _preparar_resultado_final(self, producto: Dict, mejor_resultado: Dict, historial: List) -> Dict:
        """Prepara el resultado final con toda la información y métricas"""
        faqs = mejor_resultado['faqs']
        metricas = mejor_resultado['metricas']
        perfil = mejor_resultado['perfil']
        
        # Generar insights sobre las FAQs generadas
        insights = self._generar_insights_calidad(faqs, metricas, perfil)
        
        resultado = {
            "Handle": producto.get('Handle', ''),
        }
        
        # Safely add FAQ fields, using defaults if missing
        for i in range(1, 6):
            faq_key = f'faq{i}'
            if faq_key in faqs and 'pregunta' in faqs[faq_key] and 'respuesta' in faqs[faq_key]:
                resultado[f"Metafield: custom.faq{i}question [single_line_text_field]"] = faqs[faq_key]['pregunta']
                resultado[f"Metafield: custom.faq{i}answer [multi_line_text_field]"] = faqs[faq_key]['respuesta']
            else:
                # Add empty defaults if FAQ is missing
                resultado[f"Metafield: custom.faq{i}question [single_line_text_field]"] = ""
                resultado[f"Metafield: custom.faq{i}answer [multi_line_text_field]"] = ""
        
        # Add metrics and additional information
        resultado.update({
            # Métricas avanzadas
            "_calidad": metricas.get('calidad', 'DESCONOCIDA'),
            "_puntuacion": round(metricas.get('puntuacion_promedio', 0), 2),
            "_perfil_comprador": mejor_resultado.get('perfil_comprador', 'desconocido'),
            "_diversidad_tematica": round(metricas.get('diversidad_tematica', 0), 2),
            "_patrones_repetitivos": round(metricas.get('patrones_repetitivos', 0), 2),
            "_historial": historial,
            "_insights": insights,
            
            # Información del perfil del producto
            "_perfil_producto": {
                "tipo": getattr(perfil, 'tipo_producto', 'desconocido'),
                "categoria": getattr(perfil, 'categoria_principal', 'desconocida'),
                "ingredientes_clave": getattr(perfil, 'ingredientes_clave', [])[:3],
                "beneficios": getattr(perfil, 'beneficios_principales', [])[:3],
                "precio_nivel": getattr(perfil, 'nivel_precio', 'desconocido')
            }
        })
        
        return resultado
    
    def _generar_insights_calidad(self, faqs: Dict, metricas: Dict, perfil: ProductProfile) -> Dict:
        """Genera insights sobre la calidad de las FAQs generadas"""
        insights = {
            "fortalezas": [],
            "areas_mejora": [],
            "recomendaciones": []
        }
        
        # Analizar fortalezas
        if metricas['puntuacion_promedio'] > 15:
            insights["fortalezas"].append("Contenido excepcional con alta densidad informativa")
        
        promedio_datos = sum(m['datos_numericos'] for m in metricas['detalle_faqs'].values()) / 5
        if promedio_datos > 2:
            insights["fortalezas"].append(f"Excelente uso de datos específicos ({promedio_datos:.1f} por respuesta)")
        
        if metricas['diversidad_tematica'] > 0.8:
            insights["fortalezas"].append("Alta diversidad temática en las preguntas")
        
        # Areas de mejora
        if metricas['patrones_repetitivos'] > 0.1:
            insights["areas_mejora"].append("Detectados algunos patrones repetitivos en las respuestas")
        
        # Recomendaciones específicas
        if perfil.nivel_precio == "lujo" and not any("exclusiv" in faq['respuesta'].lower() for faq in faqs.values()):
            insights["recomendaciones"].append("Considerar enfatizar más la exclusividad del producto")
        
        return insights
    
    def obtener_descripcion_producto(self, producto: Dict) -> str:
        """Obtiene y limpia la descripción del producto"""
        for columna in ['Body HTML', 'Body (HTML)', 'body_html', 'description', 'Description']:
            if columna in producto and producto[columna]:
                return self.limpiar_html(producto[columna])
        return ""
    
    def limpiar_html(self, texto_html: str) -> str:
        """Limpia HTML para obtener texto plano"""
        if pd.isna(texto_html):
            return ""
        texto = re.sub('<.*?>', ' ', str(texto_html))
        texto = ' '.join(texto.split())
        return texto
    
    # Método adicional para análisis de competencia
    def analizar_faqs_competencia(self, productos_competencia: List[Dict]) -> Dict:
        """Analiza FAQs de la competencia para evitar similitudes"""
        patrones_competencia = defaultdict(list)
        
        for producto in productos_competencia:
            # Extraer patrones de preguntas si existen FAQs
            for i in range(1, 6):
                pregunta_key = f"Metafield: custom.faq{i}question [single_line_text_field]"
                if pregunta_key in producto:
                    pregunta = producto[pregunta_key]
                    # Extraer estructura de la pregunta
                    estructura = self._extraer_estructura_pregunta(pregunta)
                    patrones_competencia[estructura].append(pregunta)
        
        return dict(patrones_competencia)
    
    def _extraer_estructura_pregunta(self, pregunta: str) -> str:
        """Extrae la estructura básica de una pregunta para análisis"""
        # Reemplazar entidades específicas con tokens genéricos
        pregunta_gen = re.sub(r'\b(este producto|el producto|[A-Z]\w+)\b', '[PRODUCTO]', pregunta)
        pregunta_gen = re.sub(r'\b\d+\s*\w+\b', '[CANTIDAD]', pregunta_gen)
        pregunta_gen = re.sub(r'\b(mi|mis)\s+\w+\b', '[PERSONAL]', pregunta_gen)
        
        return pregunta_gen.lower().strip()