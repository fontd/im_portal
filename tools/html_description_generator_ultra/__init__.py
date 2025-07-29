# tools/html_description_generator_ultra/__init__.py
"""
HTML Description Generator Ultra v1.0
Sistema ULTRA-POTENTE de generación de descripciones HTML con Scrapy masivo
"""

from .interface import render
from .scraper_engine import MassiveScrapingEngine
from .data_processor import UltraDataProcessor
from .html_generator import UltraHTMLGenerator

__version__ = "1.0.0"
__all__ = [
    "render",
    "MassiveScrapingEngine", 
    "UltraDataProcessor",
    "UltraHTMLGenerator"
]

# ==========================================
