# tools/faq_generator/processor.py
import pandas as pd
import streamlit as st
from typing import Dict, List, Optional
import json
from datetime import datetime
import io
import zipfile
from .generator import PremiumCosmeticsFAQGenerator

def process_faqs_streamlit(df: pd.DataFrame, limite_productos=None, max_intentos=3, api_key=None, modelo_gpt="gpt-3.5-turbo", progress_bar=None, status_text=None) -> tuple:
    """
    Procesa un DataFrame de productos y genera FAQs usando el generador premium v3.0
    
    Args:
        df: DataFrame con los productos
        limite_productos: Límite de productos a procesar (opcional)
        max_intentos: Número máximo de intentos por producto
        api_key: API key de OpenAI
        modelo_gpt: Modelo GPT a utilizar
        progress_bar: Barra de progreso de Streamlit (opcional)
        status_text: Texto de estado de Streamlit (opcional)
    
    Returns:
        tuple: (df_results, stats_dict, errores_list)
    """
    
    # Validar parámetros requeridos
    if api_key is None:
        raise ValueError("API key es requerido")
    
    # Aplicar límite de productos si se especifica
    if limite_productos is not None and limite_productos > 0:
        df = df.head(limite_productos)
    
    # Inicializar generador
    generator = PremiumCosmeticsFAQGenerator(api_key=api_key)
    
    # Preparar estructuras de resultados
    resultados = []
    estadisticas = {
        'total_productos': len(df),
        'procesados': 0,
        'exitosos': 0,
        'errores': 0,
        'calidad_promedio': 0,
        'distribucion_calidad': {
            'LEGENDARIA': 0,
            'EXCEPCIONAL': 0,
            'EXCELENTE': 0,
            'BUENA': 0,
            'ACEPTABLE': 0,
            'INSUFICIENTE': 0
        },
        'tiempo_inicio': datetime.now()
    }
    errores = []
    
    # Procesar cada producto
    for i, (idx, producto) in enumerate(df.iterrows()):
        try:
            # Actualizar progreso
            if progress_bar:
                progress = (i + 1) / len(df)
                progress_bar.progress(progress)
            
            # Safe title extraction
            title = producto.get('Title', 'Producto sin título')
            if pd.isna(title) or title is None:
                title = 'Producto sin título'
            title_display = str(title)[:50]
            
            if status_text:
                status_text.text(f"Procesando {i + 1}/{len(df)}: {title_display}...")
            
            # Convertir fila a diccionario y limpiar valores NaN
            producto_dict = producto.to_dict()
            
            # Clean NaN values from the product dictionary
            for key, value in producto_dict.items():
                if pd.isna(value):
                    producto_dict[key] = ""
            
            # Callback para mostrar progreso del generador
            def progress_callback(mensaje):
                if status_text:
                    status_text.text(f"Producto {i + 1}/{len(df)}: {mensaje}")
            
            # Generar FAQs con el sistema premium
            resultado = generator.generar_faqs_ultra_premium(
                producto=producto_dict,
                progress_callback=progress_callback,
                max_intentos=max_intentos,
                modelo=modelo_gpt
            )
            
            if resultado:
                resultados.append(resultado)
                estadisticas['exitosos'] += 1
                estadisticas['distribucion_calidad'][resultado['_calidad']] += 1
                estadisticas['calidad_promedio'] += resultado['_puntuacion']
            else:
                # Safe error handling
                safe_title = str(title) if title and not pd.isna(title) else 'Sin título'
                safe_handle = producto.get('Handle', 'Sin handle')
                if pd.isna(safe_handle):
                    safe_handle = 'Sin handle'
                
                errores.append({
                    'producto': safe_title,
                    'handle': str(safe_handle),
                    'error': 'No se pudo generar FAQs después de todos los intentos'
                })
                estadisticas['errores'] += 1
                
        except Exception as e:
            # Safe error handling for exceptions
            safe_title = 'Sin título'
            safe_handle = 'Sin handle'
            
            try:
                title_val = producto.get('Title', 'Sin título')
                if not pd.isna(title_val) and title_val is not None:
                    safe_title = str(title_val)
                
                handle_val = producto.get('Handle', 'Sin handle')
                if not pd.isna(handle_val) and handle_val is not None:
                    safe_handle = str(handle_val)
            except:
                pass
            
            errores.append({
                'producto': safe_title,
                'handle': safe_handle,
                'error': str(e)
            })
            estadisticas['errores'] += 1
        
        estadisticas['procesados'] += 1
    
    # Calcular estadísticas finales
    if estadisticas['exitosos'] > 0:
        estadisticas['calidad_promedio'] = round(estadisticas['calidad_promedio'] / estadisticas['exitosos'], 2)
    
    estadisticas['tiempo_total'] = str(datetime.now() - estadisticas['tiempo_inicio'])
    
    # Crear DataFrame de resultados
    if resultados:
        # Extraer solo las columnas necesarias para el CSV
        columnas_csv = [
            "Handle",
            "Metafield: custom.faq1question [single_line_text_field]",
            "Metafield: custom.faq1answer [multi_line_text_field]",
            "Metafield: custom.faq2question [single_line_text_field]",
            "Metafield: custom.faq2answer [multi_line_text_field]",
            "Metafield: custom.faq3question [single_line_text_field]",
            "Metafield: custom.faq3answer [multi_line_text_field]",
            "Metafield: custom.faq4question [single_line_text_field]",
            "Metafield: custom.faq4answer [multi_line_text_field]",
            "Metafield: custom.faq5question [single_line_text_field]",
            "Metafield: custom.faq5answer [multi_line_text_field]"
        ]
        
        try:
            # Create DataFrame and safely select columns that exist
            df_temp = pd.DataFrame(resultados)
            available_columns = [col for col in columnas_csv if col in df_temp.columns]
            
            if available_columns:
                df_results = df_temp[available_columns]
            else:
                # If no expected columns exist, return all columns
                df_results = df_temp
        except Exception as e:
            # If DataFrame creation fails, create empty DataFrame
            print(f"Error creating results DataFrame: {e}")
            df_results = pd.DataFrame()
    else:
        df_results = pd.DataFrame()
    
    return df_results, estadisticas, errores

def create_download_files(df_results: pd.DataFrame, estadisticas: dict, errores: list) -> dict:
    """
    Crea los archivos para descargar
    
    Returns:
        dict: Diccionario con los archivos en formato bytes
    """
    archivos = {}
    
    # 1. CSV de resultados
    if not df_results.empty:
        csv_buffer = io.StringIO()
        df_results.to_csv(csv_buffer, index=False, encoding='utf-8')
        archivos['faqs_shopify.csv'] = csv_buffer.getvalue().encode('utf-8')
    
    # 2. Reporte de calidad
    reporte = f"""REPORTE DE GENERACIÓN DE FAQs
=============================
Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

RESUMEN EJECUTIVO
-----------------
Total de productos procesados: {estadisticas['total_productos']}
Productos exitosos: {estadisticas['exitosos']}
Productos con errores: {estadisticas['errores']}
Tasa de éxito: {(estadisticas['exitosos'] / estadisticas['total_productos'] * 100):.1f}%

CALIDAD DE FAQs GENERADAS
-------------------------
Puntuación promedio: {estadisticas['calidad_promedio']}/20

Distribución de calidad:
"""
    
    for calidad, cantidad in estadisticas['distribucion_calidad'].items():
        if cantidad > 0:
            porcentaje = cantidad / estadisticas['exitosos'] * 100 if estadisticas['exitosos'] > 0 else 0
            reporte += f"  • {calidad}: {cantidad} productos ({porcentaje:.1f}%)\n"
    
    reporte += f"\nTiempo total de procesamiento: {estadisticas['tiempo_total']}\n"
    
    if errores:
        reporte += "\nERRORES ENCONTRADOS\n"
        reporte += "-------------------\n"
        for error in errores:
            reporte += f"• {error['producto']} (Handle: {error['handle']})\n"
            reporte += f"  Error: {error['error']}\n\n"
    
    archivos['reporte_calidad.txt'] = reporte.encode('utf-8')
    
    # 3. JSON con datos completos (incluyendo métricas)
    if not df_results.empty:
        # Create JSON-serializable version of estadisticas
        estadisticas_json = estadisticas.copy()
        
        # Convert datetime objects to strings
        if 'tiempo_inicio' in estadisticas_json:
            if isinstance(estadisticas_json['tiempo_inicio'], datetime):
                estadisticas_json['tiempo_inicio'] = estadisticas_json['tiempo_inicio'].isoformat()
        
        # Convert any other datetime objects that might be nested
        def convert_datetime_to_string(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            elif isinstance(obj, dict):
                return {k: convert_datetime_to_string(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_datetime_to_string(item) for item in obj]
            else:
                return obj
        
        estadisticas_json = convert_datetime_to_string(estadisticas_json)
        
        archivos['faqs_completo.json'] = json.dumps(
            estadisticas_json, 
            indent=2, 
            ensure_ascii=False
        ).encode('utf-8')
    
    return archivos

def create_zip_download(archivos: dict) -> bytes:
    """
    Crea un archivo ZIP con todos los archivos
    """
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for nombre_archivo, contenido in archivos.items():
            zip_file.writestr(nombre_archivo, contenido)
    
    return zip_buffer.getvalue()

# Funciones auxiliares para la interfaz

def validar_csv_productos(df: pd.DataFrame) -> tuple:
    """
    Valida que el CSV tenga las columnas necesarias
    
    Returns:
        tuple: (es_valido, mensaje_error)
    """
    columnas_requeridas = ['Handle', 'Title']
    columnas_recomendadas_base = ['Variant Price', 'Vendor', 'Tags']
    
    # Verificar columnas requeridas
    columnas_faltantes = [col for col in columnas_requeridas if col not in df.columns]
    if columnas_faltantes:
        return False, f"❌ Columnas requeridas faltantes: {', '.join(columnas_faltantes)}"
    
    # Verificar que haya al menos una columna de descripción
    columnas_descripcion = ['Body HTML', 'Body (HTML)', 'body_html', 'description', 'Description']
    tiene_descripcion = any(col in df.columns for col in columnas_descripcion)
    
    if not tiene_descripcion:
        return False, "❌ No se encontró ninguna columna de descripción del producto"
    
    # Verificar columnas recomendadas (excluyendo descripción ya que la verificamos arriba)
    columnas_faltantes_rec = [col for col in columnas_recomendadas_base if col not in df.columns]
    
    if columnas_faltantes_rec:
        mensaje = f"✅ CSV válido. ⚠️ Columnas recomendadas faltantes: {', '.join(columnas_faltantes_rec)}"
        return True, mensaje
    
    return True, "✅ CSV válido con todas las columnas recomendadas"

def obtener_muestra_productos(df: pd.DataFrame, n: int = 5) -> pd.DataFrame:
    """
    Obtiene una muestra de productos para preview
    """
    columnas_mostrar = ['Handle', 'Title', 'Vendor', 'Variant Price']
    columnas_disponibles = [col for col in columnas_mostrar if col in df.columns]
    
    muestra = df[columnas_disponibles].head(n).copy()
    
    # Truncar títulos largos
    if 'Title' in muestra.columns:
        muestra['Title'] = muestra['Title'].apply(lambda x: x[:50] + '...' if len(str(x)) > 50 else x)
    
    return muestra

def estimar_tiempo_procesamiento(n_productos: int, modelo: str = "gpt-3.5-turbo") -> str:
    """
    Estima el tiempo de procesamiento
    """
    # Estimaciones basadas en experiencia
    tiempo_por_producto = {
        "gpt-3.5-turbo": 15,  # segundos
        "gpt-4": 25  # segundos
    }
    
    segundos_estimados = n_productos * tiempo_por_producto.get(modelo, 20)
    
    if segundos_estimados < 60:
        return f"{segundos_estimados} segundos"
    elif segundos_estimados < 3600:
        minutos = segundos_estimados // 60
        return f"{minutos} minutos"
    else:
        horas = segundos_estimados // 3600
        minutos = (segundos_estimados % 3600) // 60
        return f"{horas}h {minutos}m"