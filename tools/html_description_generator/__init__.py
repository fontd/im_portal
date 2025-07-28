# tools/html_description_generator/__init__.py
"""
Generador de Descripciones HTML v1.0
Sistema avanzado de generación de descripciones HTML con búsqueda web automática
"""

from .interface import render
from .processor import process_descriptions_streamlit, create_download_files
from .generator import HTMLDescriptionGenerator

__version__ = "1.0.0"
__all__ = [
    "render",
    "process_descriptions_streamlit", 
    "create_download_files",
    "HTMLDescriptionGenerator"
]