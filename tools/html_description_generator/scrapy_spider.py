"""
Spider de Scrapy para scraping avanzado de productos cosméticos
"""

import scrapy
import json
from typing import Dict, List, Optional
import time
import logging

class CosmeticProductSpider(scrapy.Spider):
    name = 'cosmetic_product'
    
    # Headers personalizados para evitar detección
    custom_headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Cache-Control': 'no-cache',
    }
    
    def __init__(self, product_name: str = "", brand: str = "", *args, **kwargs):
        super(CosmeticProductSpider, self).__init__(*args, **kwargs)
        self.product_name = product_name
        self.brand = brand
        self.results = []
        
        # Sitios especializados en cosmética
        self.cosmetic_sites = [
            'sephora.com',
            'ulta.com', 
            'douglas.es',
            'perfumesclub.com',
            'lookfantastic.com',
            'beautybay.com',
            'notino.es',
            'primor.eu'
        ]
    
    def start_requests(self):
        """Genera las solicitudes iniciales"""
        
        queries = self._generate_search_queries()
        
        for query in queries[:3]:  # Limitar a 3 queries principales
            for site in self.cosmetic_sites[:4]:  # Top 4 sitios
                search_url = f"https://www.google.com/search?q=site:{site} {query}"
                
                yield scrapy.Request(
                    url=search_url,
                    headers=self.custom_headers,
                    callback=self.parse_search_results,
                    meta={
                        'query': query,
                        'site': site,
                        'download_delay': 2  # Delay between requests
                    }
                )
    
    def _generate_search_queries(self) -> List[str]:
        """Genera queries de búsqueda inteligentes"""
        
        queries = []
        
        # Query principal
        if self.product_name:
            queries.append(f'"{self.product_name}"')
        
        # Query con marca
        if self.brand and self.product_name:
            queries.append(f'"{self.brand}" "{self.product_name}"')
        
        # Query con términos adicionales
        if self.product_name:
            queries.append(f'"{self.product_name}" ingredients review')
            queries.append(f'"{self.product_name}" benefits description')
        
        return queries[:5]  # Máximo 5 queries
    
    def parse_search_results(self, response):
        """Analiza los resultados de búsqueda"""
        
        site = response.meta['site']
        query = response.meta['query']
        
        # Extraer enlaces relevantes
        product_links = response.css('a[href*="' + site + '"]::attr(href)').getall()
        
        for link in product_links[:3]:  # Top 3 resultados por sitio
            if self._is_product_url(link):
                yield scrapy.Request(
                    url=link,
                    headers=self.custom_headers,
                    callback=self.parse_product_page,
                    meta={
                        'source_site': site,
                        'search_query': query,
                        'download_delay': 3
                    }
                )
    
    def _is_product_url(self, url: str) -> bool:
        """Determina si una URL es de un producto"""
        
        product_indicators = [
            '/product/', '/p/', '/item/', '/beauty/', '/cosmetics/',
            'serum', 'cream', 'treatment', 'makeup', 'skincare'
        ]
        
        url_lower = url.lower()
        return any(indicator in url_lower for indicator in product_indicators)
    
    def parse_product_page(self, response):
        """Extrae información de la página del producto"""
        
        try:
            product_info = {
                'source_url': response.url,
                'source_site': response.meta['source_site'],
                'search_query': response.meta['search_query'],
                'scraped_at': time.time()
            }
            
            # Extraer título del producto
            title_selectors = [
                'h1::text',
                '.product-title::text',
                '.product-name::text',
                '[data-testid="product-name"]::text',
                '.pdp-product-name::text'
            ]
            product_info['title'] = self._extract_first_text(response, title_selectors)
            
            # Extraer descripción
            desc_selectors = [
                '.product-description::text',
                '.product-details::text',
                '.product-summary::text',
                '[data-testid="product-description"]::text',
                '.description p::text',
                '.overview::text'
            ]
            product_info['description'] = self._extract_first_text(response, desc_selectors)
            
            # Extraer ingredientes
            ingredient_selectors = [
                '.ingredients::text',
                '.ingredient-list::text',
                '[data-testid="ingredients"]::text',
                '.product-ingredients::text',
                '.formula::text',
                '.composition::text'
            ]
            product_info['ingredients'] = self._extract_first_text(response, ingredient_selectors)
            
            # Extraer precio
            price_selectors = [
                '.price::text',
                '.product-price::text',
                '[data-testid="price"]::text',
                '.price-current::text',
                '.sale-price::text'
            ]
            product_info['price'] = self._extract_first_text(response, price_selectors)
            
            # Extraer beneficios
            benefits_selectors = [
                '.benefits li::text',
                '.features li::text',
                '.key-benefits li::text',
                '.product-benefits li::text'
            ]
            product_info['benefits'] = response.css(' , '.join(benefits_selectors)).getall()[:5]
            
            # Calcular score de relevancia
            product_info['relevance_score'] = self._calculate_relevance(product_info)
            
            # Solo devolver si tiene información útil
            if product_info['relevance_score'] > 0.3:
                self.results.append(product_info)
                yield product_info
            
        except Exception as e:
            self.logger.error(f"Error parsing product page {response.url}: {e}")
    
    def _extract_first_text(self, response, selectors: List[str]) -> str:
        """Extrae el primer texto encontrado usando múltiples selectores"""
        
        for selector in selectors:
            try:
                text = response.css(selector).get()
                if text and len(text.strip()) > 5:
                    return text.strip()[:500]  # Máximo 500 caracteres
            except:
                continue
        
        return ""
    
    def _calculate_relevance(self, product_info: Dict) -> float:
        """Calcula score de relevancia del producto"""
        
        score = 0.0
        
        # Puntuación por contenido encontrado
        if product_info.get('title'):
            score += 0.3
            # Bonus si el título contiene el producto buscado
            if self.product_name.lower() in product_info['title'].lower():
                score += 0.2
        
        if product_info.get('description') and len(product_info['description']) > 50:
            score += 0.2
        
        if product_info.get('ingredients'):
            score += 0.2
        
        if product_info.get('benefits'):
            score += 0.1 * min(len(product_info['benefits']), 3)
        
        if product_info.get('price'):
            score += 0.1
        
        # Bonus por sitio confiable
        trusted_sites = ['sephora', 'ulta', 'douglas']
        if any(site in product_info.get('source_site', '') for site in trusted_sites):
            score += 0.2
        
        return min(score, 1.0)

class ScrapyProductSearcher:
    """
    Interfaz para usar Scrapy desde el generador principal
    """
    
    def __init__(self):
        self.results = []
    
    def search_product(self, product_name: str, brand: str = "") -> List[Dict]:
        """
        Busca información del producto usando Scrapy
        """
        
        try:
            from scrapy.crawler import CrawlerProcess
            from scrapy.utils.project import get_project_settings
            
            # Configuración personalizada para Scrapy
            settings = get_project_settings()
            settings.update({
                'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                'ROBOTSTXT_OBEY': False,  # No respetar robots.txt para este caso
                'DOWNLOAD_DELAY': 2,
                'RANDOMIZE_DOWNLOAD_DELAY': True,
                'CONCURRENT_REQUESTS': 4,
                'CONCURRENT_REQUESTS_PER_DOMAIN': 2,
                'AUTOTHROTTLE_ENABLED': True,
                'AUTOTHROTTLE_START_DELAY': 1,
                'AUTOTHROTTLE_MAX_DELAY': 5,
                'AUTOTHROTTLE_TARGET_CONCURRENCY': 2.0,
                'COOKIES_ENABLED': True,
                'LOG_LEVEL': 'WARNING'  # Reducir logging
            })
            
            process = CrawlerProcess(settings)
            
            # Crear y ejecutar spider
            spider = CosmeticProductSpider(
                product_name=product_name,
                brand=brand
            )
            
            process.crawl(spider)
            process.start(stop_after_crawl=True)
            
            return spider.results
            
        except Exception as e:
            logging.error(f"Error en búsqueda con Scrapy: {e}")
            return []
    
    def search_product_async(self, product_name: str, brand: str = "") -> List[Dict]:
        """
        Versión asíncrona de la búsqueda (para usar en Streamlit)
        """
        
        # Para Streamlit, usamos una versión simplificada
        # que no bloquea el hilo principal
        try:
            import threading
            import queue
            
            results_queue = queue.Queue()
            
            def run_spider():
                try:
                    results = self.search_product(product_name, brand)
                    results_queue.put(results)
                except Exception as e:
                    results_queue.put([])
            
            # Ejecutar en hilo separado con timeout
            thread = threading.Thread(target=run_spider)
            thread.daemon = True
            thread.start()
            thread.join(timeout=30)  # Timeout de 30 segundos
            
            try:
                return results_queue.get_nowait()
            except queue.Empty:
                return []
                
        except Exception as e:
            logging.error(f"Error en búsqueda asíncrona: {e}")
            return []
