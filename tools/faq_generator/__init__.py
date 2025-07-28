# tools/faq_generator/__init__.py
"""
Generador Premium de FAQs v3.0
Sistema ultra-premium de generación de FAQs para productos cosméticos
"""

from .interface import render
from .processor import process_faqs_streamlit, create_download_files
from .generator import PremiumCosmeticsFAQGenerator

__version__ = "3.0.0"
__all__ = [
    "render",
    "process_faqs_streamlit", 
    "create_download_files",
    "PremiumCosmeticsFAQGenerator"
]