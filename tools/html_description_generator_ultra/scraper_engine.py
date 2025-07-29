# tools/html_description_generator_ultra/scraper_engine.py
"""
Motor de Scraping Masivo Ultra-Potente
"""

import asyncio
import aiohttp
from scrapy import Spider, Request
from scrapy.crawler import CrawlerRunner
from twisted.internet import reactor, defer
from typing import Dict, List, Optional, Any
import pandas as pd
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import time
import random
import json

@dataclass
class ScrapingTarget:
    """Objetivo de scraping"""
    product_name: str
    urls: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    category: str = ""
    priority: str = "medium"  # high, medium, low
    expected_sites: List[str] = field(default_factory=list)

@dataclass
class ScrapedProduct:
    """Producto scrapeado"""
    name: str
    brand: str = ""
    price: str = ""
    description: str = ""
    specs: Dict[str, Any] = field(default_factory=dict)
    images: List[str] = field(default_factory=list)
    reviews: List[Dict] = field(default_factory=list)
    source_url: str = ""
    source_site: str = ""
    confidence_score: float = 0.0
    scraped_at: str = ""

class MassiveScrapingEngine:
    """
    Motor de Scraping Ultra-Potente con Scrapy y procesamiento paralelo
    """
    
    def __init__(self, max_concurrent: int = 50, max_workers: int = 10):
        self.max_concurrent = max_concurrent
        self.max_workers = max_workers
        self.results = []
        self.stats = {
            'total_targeted': 0,
            'total_scraped': 0,
            'successful': 0,
            'failed': 0,
            'start_time': None,
            'end_time': None
        }
        
        # Configuración de spiders especializados
        self.spider_configs = {
            'amazon': {
                'class': AmazonSpider,
                'selectors': {
                    'name': 'h1#title span::text',
                    'price': '.a-price-current .a-offscreen::text',
                    'description': '#feature-bullets ul li span::text',
                    'specs': '#productDetails_techSpec_section_1 tr',
                    'images': '#landingImage::attr(src)'
                },
                'max_concurrent': 20
            },
            'ebay': {
                'class': EbaySpider,
                'selectors': {
                    'name': 'h1#x-title-label-lbl::text',
                    'price': '.notranslate::text',
                    'description': '#viTabs_0_is .u-flL span::text',
                    'specs': '.specs table tr',
                    'images': '#icImg::attr(src)'
                },
                'max_concurrent': 15
            },
            'aliexpress': {
                'class': AliExpressSpider,
                'selectors': {
                    'name': 'h1.product-title-text::text',
                    'price': '.current-price .price::text',
                    'description': '.product-overview .content::text',
                    'specs': '.product-params .param',
                    'images': '.image-view img::attr(src)'
                },
                'max_concurrent': 10
            }
        }
    
    async def scrape_massive(self, targets: List[ScrapingTarget], 
                           progress_callback=None) -> List[ScrapedProduct]:
        """
        Scraping masivo de múltiples objetivos
        """
        self.stats['total_targeted'] = len(targets)
        self.stats['start_time'] = time.time()
        
        # Preparar URLs para cada spider
        spider_tasks = self._prepare_spider_tasks(targets)
        
        # Ejecutar spiders en paralelo
        tasks = []
        for spider_name, urls in spider_tasks.items():
            if urls:
                task = self._run_spider_async(spider_name, urls, progress_callback)
                tasks.append(task)
        
        # Esperar todos los spiders
        if tasks:
            spider_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Consolidar resultados
            for result in spider_results:
                if isinstance(result, list):
                    self.results.extend(result)
                elif isinstance(result, Exception):
                    print(f"Spider error: {result}")
        
        self.stats['end_time'] = time.time()
        self.stats['total_scraped'] = len(self.results)
        self.stats['successful'] = len([r for r in self.results if r.confidence_score > 0.5])
        self.stats['failed'] = self.stats['total_scraped'] - self.stats['successful']
        
        return self.results
    
    def _prepare_spider_tasks(self, targets: List[ScrapingTarget]) -> Dict[str, List[str]]:
        """Prepara tareas para cada spider"""
        
        spider_tasks = {name: [] for name in self.spider_configs.keys()}
        
        for target in targets:
            # Si tiene URLs específicas, usar esas
            if target.urls:
                for url in target.urls:
                    spider_name = self._identify_spider_for_url(url)
                    if spider_name:
                        spider_tasks[spider_name].append(url)
            
            # Si tiene keywords, generar URLs de búsqueda
            elif target.keywords:
                search_urls = self._generate_search_urls(target.keywords, target.expected_sites)
                for url in search_urls:
                    spider_name = self._identify_spider_for_url(url)
                    if spider_name:
                        spider_tasks[spider_name].append(url)
        
        return spider_tasks
    
    def _identify_spider_for_url(self, url: str) -> Optional[str]:
        """Identifica qué spider usar para una URL"""
        url_lower = url.lower()
        
        if 'amazon.' in url_lower:
            return 'amazon'
        elif 'ebay.' in url_lower:
            return 'ebay'
        elif 'aliexpress.' in url_lower:
            return 'aliexpress'
        
        return None
    
    def _generate_search_urls(self, keywords: List[str], sites: List[str]) -> List[str]:
        """Genera URLs de búsqueda para keywords"""
        
        search_patterns = {
            'amazon': 'https://www.amazon.com/s?k={keyword}',
            'ebay': 'https://www.ebay.com/sch/i.html?_nkw={keyword}',
            'aliexpress': 'https://www.aliexpress.com/wholesale?SearchText={keyword}'
        }
        
        urls = []
        for keyword in keywords:
            keyword_encoded = keyword.replace(' ', '+')
            for site in sites:
                if site.lower() in search_patterns:
                    pattern = search_patterns[site.lower()]
                    urls.append(pattern.format(keyword=keyword_encoded))
        
        return urls
    
    async def _run_spider_async(self, spider_name: str, urls: List[str], 
                               progress_callback=None) -> List[ScrapedProduct]:
        """Ejecuta un spider de forma asíncrona"""
        
        spider_config = self.spider_configs[spider_name]
        spider_class = spider_config['class']
        
        # Crear instancia del spider
        spider = spider_class(
            urls=urls,
            selectors=spider_config['selectors'],
            max_concurrent=spider_config['max_concurrent']
        )
        
        # Ejecutar spider
        results = await spider.scrape_urls_async()
        
        if progress_callback:
            progress_callback(f"✅ {spider_name}: {len(results)} productos scrapeados")
        
        return results

class BaseSpider:
    """Spider base para todos los sitios"""
    
    def __init__(self, urls: List[str], selectors: Dict[str, str], max_concurrent: int = 10):
        self.urls = urls
        self.selectors = selectors
        self.max_concurrent = max_concurrent
        self.session = None
        
        # Headers para evitar detección
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    
    async def scrape_urls_async(self) -> List[ScrapedProduct]:
        """Scraping asíncrono de URLs"""
        
        connector = aiohttp.TCPConnector(limit=self.max_concurrent)
        timeout = aiohttp.ClientTimeout(total=30)
        
        async with aiohttp.ClientSession(
            connector=connector, 
            timeout=timeout,
            headers=self.headers
        ) as session:
            
            self.session = session
            
            # Crear tareas para todas las URLs
            tasks = []
            for url in self.urls:
                task = self._scrape_single_url(url)
                tasks.append(task)
                
                # Limitar concurrencia
                if len(tasks) >= self.max_concurrent:
                    results = await asyncio.gather(*tasks, return_exceptions=True)
                    yield from self._process_results(results)
                    tasks = []
                
                # Delay aleatorio entre requests
                await asyncio.sleep(random.uniform(0.5, 2.0))
            
            # Procesar tareas restantes
            if tasks:
                results = await asyncio.gather(*tasks, return_exceptions=True)
                yield from self._process_results(results)
    
    async def _scrape_single_url(self, url: str) -> Optional[ScrapedProduct]:
        """Scrapea una URL individual"""
        
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    html = await response.text()
                    return self._parse_html(html, url)
                else:
                    print(f"Error {response.status} scraping {url}")
                    return None
        
        except Exception as e:
            print(f"Exception scraping {url}: {e}")
            return None
    
    def _parse_html(self, html: str, url: str) -> Optional[ScrapedProduct]:
        """Parsea HTML y extrae datos del producto"""
        
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extraer datos usando selectores
        product = ScrapedProduct(
            name=self._extract_text(soup, self.selectors.get('name', '')),
            price=self._extract_text(soup, self.selectors.get('price', '')),
            description=self._extract_text(soup, self.selectors.get('description', '')),
            source_url=url,
            source_site=self.__class__.__name__.replace('Spider', '').lower(),
            scraped_at=time.strftime('%Y-%m-%d %H:%M:%S')
        )
        
        # Extraer especificaciones
        specs = self._extract_specs(soup, self.selectors.get('specs', ''))
        product.specs = specs
        
        # Extraer imágenes
        images = self._extract_images(soup, self.selectors.get('images', ''))
        product.images = images
        
        # Calcular score de confianza
        product.confidence_score = self._calculate_confidence(product)
        
        return product if product.confidence_score > 0.3 else None
    
    def _extract_text(self, soup: BeautifulSoup, selector: str) -> str:
        """Extrae texto usando selector CSS"""
        try:
            element = soup.select_one(selector)
            return element.get_text(strip=True) if element else ""
        except:
            return ""
    
    def _extract_specs(self, soup: BeautifulSoup, selector: str) -> Dict[str, str]:
        """Extrae especificaciones técnicas"""
        specs = {}
        try:
            elements = soup.select(selector)
            for elem in elements[:10]:  # Máximo 10 specs
                # Lógica específica por sitio se implementa en subclases
                pass
        except:
            pass
        return specs
    
    def _extract_images(self, soup: BeautifulSoup, selector: str) -> List[str]:
        """Extrae URLs de imágenes"""
        images = []
        try:
            elements = soup.select(selector)
            for elem in elements[:5]:  # Máximo 5 imágenes
                src = elem.get('src') or elem.get('data-src')
                if src:
                    images.append(src)
        except:
            pass
        return images
    
    def _calculate_confidence(self, product: ScrapedProduct) -> float:
        """Calcula score de confianza del producto"""
        score = 0.0
        
        if product.name:
            score += 0.4
        if product.price:
            score += 0.2
        if product.description:
            score += 0.2
        if product.specs:
            score += 0.1
        if product.images:
            score += 0.1
        
        return min(score, 1.0)
    
    def _process_results(self, results: List) -> List[ScrapedProduct]:
        """Procesa resultados filtrando excepciones"""
        products = []
        for result in results:
            if isinstance(result, ScrapedProduct):
                products.append(result)
            elif isinstance(result, Exception):
                print(f"Scraping exception: {result}")
        return products

class AmazonSpider(BaseSpider):
    """Spider especializado para Amazon"""
    
    def _extract_specs(self, soup: BeautifulSoup, selector: str) -> Dict[str, str]:
        """Extrae specs específicas de Amazon"""
        specs = {}
        try:
            # Amazon tiene specs en tabla técnica
            spec_rows = soup.select('#productDetails_techSpec_section_1 tr')
            for row in spec_rows:
                cells = row.select('td')
                if len(cells) >= 2:
                    key = cells[0].get_text(strip=True)
                    value = cells[1].get_text(strip=True)
                    if key and value:
                        specs[key] = value
        except:
            pass
        return specs

class EbaySpider(BaseSpider):
    """Spider especializado para eBay"""
    
    def _extract_specs(self, soup: BeautifulSoup, selector: str) -> Dict[str, str]:
        """Extrae specs específicas de eBay"""
        specs = {}
        try:
            # eBay tiene specs en formato diferente
            spec_elements = soup.select('.u-flL.condText, .specs table tr')
            for elem in spec_elements:
                text = elem.get_text(strip=True)
                if ':' in text:
                    parts = text.split(':', 1)
                    if len(parts) == 2:
                        specs[parts[0].strip()] = parts[1].strip()
        except:
            pass
        return specs

class AliExpressSpider(BaseSpider):
    """Spider especializado para AliExpress"""
    
    def _extract_specs(self, soup: BeautifulSoup, selector: str) -> Dict[str, str]:
        """Extrae specs específicas de AliExpress"""
        specs = {}
        try:
            # AliExpress tiene specs en formato propio
            spec_elements = soup.select('.product-params .param')
            for elem in spec_elements:
                label = elem.select_one('.param-name')
                value = elem.select_one('.param-value')
                if label and value:
                    key = label.get_text(strip=True)
                    val = value.get_text(strip=True)
                    if key and val:
                        specs[key] = val
        except:
            pass
        return specs

# ==========================================
