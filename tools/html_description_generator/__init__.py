# tools/html_description_generator/__init__.py
"""
Generador Simple de Descripciones HTML v2.0
Sistema simple de generación de descripciones HTML para productos individuales
"""

from .interface import render
from .generator import SimpleHTMLDescriptionGenerator
from .processor import process_single_product

__version__ = "2.0.0"
__all__ = [
    "render",
    "SimpleHTMLDescriptionGenerator",
    "process_single_product"
]