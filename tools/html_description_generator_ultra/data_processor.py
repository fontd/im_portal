# tools/html_description_generator_ultra/data_processor.py
"""
Procesador Ultra de Datos con IA Múltiple
"""

import pandas as pd
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import json
import asyncio
import aiohttp
from openai import OpenAI
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

@dataclass
class ProcessedProduct:
    """Producto procesado con IA"""
    # Datos originales
    raw_data: Dict[str, Any] = field(default_factory=dict)
    
    # Datos procesados
    unified_name: str = ""
    unified_brand: str = ""
    unified_category: str = ""
    unified_price: float = 0.0
    
    # Descripción mejorada
    ai_description: str = ""
    key_features: List[str] = field(default_factory=list)
    technical_specs: Dict[str, str] = field(default_factory=dict)
    
    # Análisis de mercado
    competitor_analysis: Dict[str, Any] = field(default_factory=dict)
    price_analysis: Dict[str, Any] = field(default_factory=dict)
    sentiment_score: float = 0.0
    
    # Metadatos
    processing_quality: str = ""  # excellent, good, average, poor
    confidence_score: float = 0.0
    processing_time: float = 0.0

class UltraDataProcessor:
    """
    Procesador Ultra de Datos con IA Múltiple y Análisis Avanzado
    """
    
    def __init__(self, openai_api_key: str, max_workers: int = 20):
        self.openai_client = OpenAI(api_key=openai_api_key)
        self.max_workers = max_workers
        
        # Configuración de modelos IA
        self.ai_models = {
            'gpt4_turbo': {
                'model': 'gpt-4-turbo-preview',
                'max_tokens': 2000,
                'temperature': 0.3,
                'use_for': ['description', 'analysis', 'categorization']
            },
            'gpt35_turbo': {
                'model': 'gpt-3.5-turbo',
                'max_tokens': 1500,
                'temperature': 0.5,
                'use_for': ['features', 'specs', 'sentiment']
            }
        }
        
        # Prompts especializados
        self.prompts = {
            'unify_product': """
            Analiza estos datos de producto de múltiples fuentes y unifica la información:
            
            DATOS MÚLTIPLES:
            {product_data}
            
            Unifica y mejora la información en JSON:
            {{
                "unified_name": "nombre unificado y mejorado",
                "unified_brand": "marca identificada",
                "unified_category": "categoría específica",
                "unified_price": precio_promedio_numerico,
                "confidence_indicators": ["indicador1", "indicador2"]
            }}
            """,
            
            'generate_description': """
            Genera una descripción ultra-detallada para este producto basándote en toda la información disponible:
            
            PRODUCTO: {product_name}
            MARCA: {brand}
            CATEGORÍA: {category}
            ESPECIFICACIONES: {specs}
            FUENTES: {sources_count} fuentes diferentes
            
            Genera una descripción HTML de alta calidad (400-600 palabras) que incluya:
            - Introducción atractiva
            - Características técnicas principales
            - Beneficios específicos
            - Información de uso/aplicación
            - Comparación con competidores (sutil)
            
            Usa un tono profesional pero accesible.
            """,
            
            'extract_features': """
            Extrae las características clave más importantes de este producto:
            
            DATOS: {product_data}
            
            Identifica las 8-10 características más relevantes y valiosas.
            Responde en JSON:
            {{
                "key_features": [
                    {{"feature": "nombre", "value": "valor", "importance": "high/medium/low"}},
                    ...
                ]
            }}
            """,
            
            'competitive_analysis': """
            Realiza un análisis competitivo de este producto:
            
            PRODUCTO: {product_name}
            CATEGORÍA: {category}
            PRECIO: {price}
            
            Analiza y responde en JSON:
            {{
                "positioning": "posicionamiento en el mercado",
                "price_competitiveness": "análisis de precio vs competencia",
                "unique_selling_points": ["USP1", "USP2"],
                "market_segment": "segmento objetivo",
                "competitive_advantages": ["ventaja1", "ventaja2"]
            }}
            """
        }
    
    async def process_products_ultra(self, scraped_products: List[Dict], 
                                   progress_callback=None) -> List[ProcessedProduct]:
        """
        Procesamiento ultra de productos con IA múltiple
        """
        
        if progress_callback:
            progress_callback("🚀 Iniciando procesamiento ultra con IA múltiple...")
        
        # Agrupar productos similares
        grouped_products = self._group_similar_products(scraped_products)
        
        if progress_callback:
            progress_callback(f"📊 {len(grouped_products)} grupos de productos identificados")
        
        # Procesar cada grupo en paralelo
        processed_products = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {}
            
            for i, product_group in enumerate(grouped_products):
                future = executor.submit(self._process_product_group, product_group, i)
                futures[future] = i
            
            # Recoger resultados conforme van completándose
            for future in as_completed(futures):
                group_index = futures[future]
                try:
                    processed_product = future.result()
                    if processed_product:
                        processed_products.append(processed_product)
                    
                    if progress_callback:
                        progress_callback(f"✅ Grupo {group_index + 1}/{len(grouped_products)} procesado")
                
                except Exception as e:
                    if progress_callback:
                        progress_callback(f"❌ Error procesando grupo {group_index + 1}: {str(e)}")
        
        # Análisis final y ranking
        final_products = self._final_analysis_and_ranking(processed_products)
        
        if progress_callback:
            progress_callback(f"🎉 Procesamiento ultra completado: {len(final_products)} productos finales")
        
        return final_products
    
    def _group_similar_products(self, products: List[Dict]) -> List[List[Dict]]:
        """Agrupa productos similares por nombre/marca/categoría"""
        
        groups = []
        used_indices = set()
        
        for i, product in enumerate(products):
            if i in used_indices:
                continue
            
            # Crear nuevo grupo con este producto
            group = [product]
            used_indices.add(i)
            
            # Buscar productos similares
            for j, other_product in enumerate(products[i+1:], i+1):
                if j in used_indices:
                    continue
                
                if self._are_similar_products(product, other_product):
                    group.append(other_product)
                    used_indices.add(j)
            
            groups.append(group)
        
        return groups
    
    def _are_similar_products(self, product1: Dict, product2: Dict) -> bool:
        """Determina si dos productos son similares"""
        
        # Comparar nombres (similarity básica)
        name1 = product1.get('name', '').lower()
        name2 = product2.get('name', '').lower()
        
        if not name1 or not name2:
            return False
        
        # Similarity simple por palabras en común
        words1 = set(name1.split())
        words2 = set(name2.split())
        
        if len(words1) == 0 or len(words2) == 0:
            return False
        
        overlap = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        similarity = overlap / union if union > 0 else 0
        
        return similarity > 0.4  # 40% de similarity
    
    def _process_product_group(self, product_group: List[Dict], group_index: int) -> Optional[ProcessedProduct]:
        """Procesa un grupo de productos similares"""
        
        start_time = time.time()
        
        try:
            # Unificar información del grupo
            unified_data = self._unify_product_data(product_group)
            
            # Generar descripción con IA
            ai_description = self._generate_ai_description(unified_data)
            
            # Extraer características clave
            key_features = self._extract_key_features(product_group)
            
            # Análisis competitivo
            competitive_analysis = self._analyze_competition(unified_data)
            
            # Crear producto procesado
            processed_product = ProcessedProduct(
                raw_data={'sources': product_group, 'count': len(product_group)},
                unified_name=unified_data.get('unified_name', ''),
                unified_brand=unified_data.get('unified_brand', ''),
                unified_category=unified_data.get('unified_category', ''),
                unified_price=unified_data.get('unified_price', 0.0),
                ai_description=ai_description,
                key_features=key_features,
                competitive_analysis=competitive_analysis,
                processing_time=time.time() - start_time
            )
            
            # Calcular calidad y confianza
            processed_product.confidence_score = self._calculate_processing_confidence(processed_product)
            processed_product.processing_quality = self._determine_quality_level(processed_product)
            
            return processed_product
        
        except Exception as e:
            print(f"Error processing group {group_index}: {e}")
            return None
    
    def _unify_product_data(self, product_group: List[Dict]) -> Dict[str, Any]:
        """Unifica datos de múltiples fuentes usando IA"""
        
        try:
            # Preparar datos para la IA
            product_data_str = json.dumps(product_group, indent=2, ensure_ascii=False)
            
            prompt = self.prompts['unify_product'].format(
                product_data=product_data_str[:3000]  # Limitar tamaño
            )
            
            response = self.openai_client.chat.completions.create(
                model=self.ai_models['gpt4_turbo']['model'],
                messages=[
                    {"role": "system", "content": "Eres un experto en análisis y unificación de datos de productos de e-commerce."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.ai_models['gpt4_turbo']['max_tokens'],
                temperature=self.ai_models['gpt4_turbo']['temperature']
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
        
        except Exception as e:
            print(f"Error unifying product data: {e}")
            # Fallback: usar primer producto del grupo
            return {
                'unified_name': product_group[0].get('name', ''),
                'unified_brand': product_group[0].get('brand', ''),
                'unified_category': 'General',
                'unified_price': 0.0
            }
    
    def _generate_ai_description(self, unified_data: Dict) -> str:
        """Genera descripción ultra-detallada con IA"""
        
        try:
            prompt = self.prompts['generate_description'].format(
                product_name=unified_data.get('unified_name', ''),
                brand=unified_data.get('unified_brand', ''),
                category=unified_data.get('unified_category', ''),
                specs=json.dumps(unified_data.get('technical_specs', {})),
                sources_count=unified_data.get('sources_count', 1)
            )
            
            response = self.openai_client.chat.completions.create(
                model=self.ai_models['gpt4_turbo']['model'],
                messages=[
                    {"role": "system", "content": "Eres un copywriter experto especializado en descripciones de productos de e-commerce. Creas contenido persuasivo, informativo y optimizado para SEO."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.ai_models['gpt4_turbo']['max_tokens'],
                temperature=0.4
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            print(f"Error generating AI description: {e}")
            return f"Producto de alta calidad: {unified_data.get('unified_name', 'Producto')}"
    
    def _extract_key_features(self, product_group: List[Dict]) -> List[str]:
        """Extrae características clave de los productos"""
        
        features = []
        
        try:
            # Combinar todas las especificaciones
            all_specs = {}
            for product in product_group:
                specs = product.get('specs', {})
                if isinstance(specs, dict):
                    all_specs.update(specs)
            
            prompt = self.prompts['extract_features'].format(
                product_data=json.dumps(all_specs, indent=2)[:2000]
            )
            
            response = self.openai_client.chat.completions.create(
                model=self.ai_models['gpt35_turbo']['model'],
                messages=[
                    {"role": "system", "content": "Eres un experto en análisis de características de productos."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.3
            )
            
            result = json.loads(response.choices[0].message.content)
            features = [f"{item['feature']}: {item['value']}" for item in result.get('key_features', [])]
        
        except Exception as e:
            print(f"Error extracting features: {e}")
            # Fallback: usar specs directamente
            for product in product_group:
                specs = product.get('specs', {})
                if isinstance(specs, dict):
                    for key, value in list(specs.items())[:5]:
                        features.append(f"{key}: {value}")
        
        return features[:8]  # Máximo 8 características
    
    def _analyze_competition(self, unified_data: Dict) -> Dict[str, Any]:
        """Análisis competitivo del producto"""
        
        try:
            prompt = self.prompts['competitive_analysis'].format(
                product_name=unified_data.get('unified_name', ''),
                category=unified_data.get('unified_category', ''),
                price=unified_data.get('unified_price', 0)
            )
            
            response = self.openai_client.chat.completions.create(
                model=self.ai_models['gpt4_turbo']['model'],
                messages=[
                    {"role": "system", "content": "Eres un analista de mercado especializado en e-commerce y productos de consumo."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            return json.loads(response.choices[0].message.content)
        
        except Exception as e:
            print(f"Error in competitive analysis: {e}")
            return {
                "positioning": "Posición competitiva en el mercado",
                "price_competitiveness": "Precio competitivo en su segmento",
                "unique_selling_points": ["Características únicas", "Valor diferencial"],
                "market_segment": unified_data.get('unified_category', 'General')
            }
    
    def _calculate_processing_confidence(self, product: ProcessedProduct) -> float:
        """Calcula confianza del procesamiento"""
        
        score = 0.0
        
        # Datos básicos
        if product.unified_name:
            score += 0.2
        if product.unified_brand:
            score += 0.1
        if product.unified_price > 0:
            score += 0.1
        
        # Contenido IA
        if len(product.ai_description) > 200:
            score += 0.3
        if len(product.key_features) >= 5:
            score += 0.2
        
        # Análisis
        if product.competitive_analysis:
            score += 0.1
        
        return min(score, 1.0)
    
    def _determine_quality_level(self, product: ProcessedProduct) -> str:
        """Determina nivel de calidad del procesamiento"""
        
        if product.confidence_score >= 0.9:
            return "excellent"
        elif product.confidence_score >= 0.7:
            return "good"
        elif product.confidence_score >= 0.5:
            return "average"
        else:
            return "poor"
    
    def _final_analysis_and_ranking(self, processed_products: List[ProcessedProduct]) -> List[ProcessedProduct]:
        """Análisis final y ranking de productos"""
        
        # Ordenar por confianza y calidad
        processed_products.sort(
            key=lambda p: (p.confidence_score, len(p.ai_description), len(p.key_features)), 
            reverse=True
        )
        
        # Filtrar productos de baja calidad
        high_quality_products = [
            p for p in processed_products 
            if p.processing_quality in ['excellent', 'good'] and p.confidence_score > 0.6
        ]
        
        return high_quality_products

# ==========================================
