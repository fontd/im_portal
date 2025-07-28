# tools/html_description_generator/processor.py
import pandas as pd
import streamlit as st
from typing import Dict, List, Optional
import json
from datetime import datetime
import io
import zipfile
from .generator import HTMLDescriptionGenerator

def process_descriptions_streamlit(df: pd.DataFrame, limite_productos=None, api_key=None, 
                                 metodo="auto", urls_manuales=None, estilo="completa", 
                                 categoria="", terminos_adicionales="", idioma="es",
                                 progress_bar=None, status_text=None) -> tuple:
    """
    Procesa un DataFrame de productos y genera descripciones HTML
    
    Args:
        df: DataFrame con los productos
        limite_productos: Límite de productos a procesar
        api_key: API key de OpenAI
        metodo: "auto" para búsqueda automática, "manual" para URLs específicas
        urls_manuales: Lista de URLs cuando se usa método manual
        estilo: Estilo de descripción a generar
        categoria: Categoría del producto para búsqueda
        terminos_adicionales: Términos adicionales para búsqueda
        idioma: Idioma de la descripción
        progress_bar: Barra de progreso de Streamlit
        status_text: Texto de estado de Streamlit
    
    Returns:
        tuple: (df_results, stats_dict, errores_list)
    """
    
    if api_key is None:
        raise ValueError("API key es requerido")
    
    # Aplicar límite si se especifica
    if limite_productos is not None and limite_productos > 0:
        df = df.head(limite_productos)
    
    # Inicializar generador
    generator = HTMLDescriptionGenerator(api_key=api_key)
    
    # Preparar estructuras de resultados
    resultados = []
    estadisticas = {
        'total_productos': len(df),
        'procesados': 0,
        'exitosos': 0,
        'errores': 0,
        'metodo_usado': metodo,
        'estilo_aplicado': estilo,
        'idioma': idioma,
        'tiempo_inicio': datetime.now(),
        'fuentes_promedio': 0,
        'caracteristicas_promedio': 0
    }
    errores = []
    
    total_fuentes = 0
    total_caracteristicas = 0
    
    # Procesar cada producto
    for i, (idx, producto) in enumerate(df.iterrows()):
        try:
            # Actualizar progreso
            if progress_bar:
                progress = (i + 1) / len(df)
                progress_bar.progress(progress)
            
            # Extraer título de forma segura
            title = producto.get('Title', 'Producto sin título')
            if pd.isna(title) or title is None:
                title = 'Producto sin título'
            title_display = str(title)[:50]
            
            if status_text:
                status_text.text(f"Procesando {i + 1}/{len(df)}: {title_display}...")
            
            # Convertir fila a diccionario y limpiar NaN
            producto_dict = producto.to_dict()
            for key, value in producto_dict.items():
                if pd.isna(value):
                    producto_dict[key] = ""
            
            # Callback para progreso del generador
            def progress_callback(mensaje):
                if status_text:
                    status_text.text(f"Producto {i + 1}/{len(df)}: {mensaje}")
            
            # Procesar producto
            resultado = generator.procesar_producto_completo(
                producto=producto_dict,
                metodo=metodo,
                urls_manuales=urls_manuales if metodo == "manual" else None,
                estilo=estilo,
                categoria=categoria,
                terminos_adicionales=terminos_adicionales,
                idioma=idioma,
                progress_callback=progress_callback
            )
            
            if resultado and "_error" not in resultado:
                resultados.append(resultado)
                estadisticas['exitosos'] += 1
                
                # Acumular estadísticas
                total_fuentes += resultado.get('_fuentes_consultadas', 0)
                total_caracteristicas += resultado.get('_caracteristicas_encontradas', 0)
                
            else:
                # Manejar error
                safe_title = str(title) if title and not pd.isna(title) else 'Sin título'
                safe_handle = producto.get('Handle', 'Sin handle')
                if pd.isna(safe_handle):
                    safe_handle = 'Sin handle'
                
                error_msg = resultado.get('_error', 'Error desconocido') if resultado else 'No se pudo procesar'
                
                errores.append({
                    'producto': safe_title,
                    'handle': str(safe_handle),
                    'error': error_msg
                })
                estadisticas['errores'] += 1
                
        except Exception as e:
            # Manejo seguro de errores
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
        estadisticas['fuentes_promedio'] = round(total_fuentes / estadisticas['exitosos'], 1)
        estadisticas['caracteristicas_promedio'] = round(total_caracteristicas / estadisticas['exitosos'], 1)
    
    estadisticas['tiempo_total'] = str(datetime.now() - estadisticas['tiempo_inicio'])
    
    # Crear DataFrame de resultados
    if resultados:
        columnas_csv = [
            "Handle",
            "Metafield: custom.html_description [rich_text_field]"
        ]
        
        try:
            df_temp = pd.DataFrame(resultados)
            available_columns = [col for col in columnas_csv if col in df_temp.columns]
            
            if available_columns:
                df_results = df_temp[available_columns]
            else:
                df_results = df_temp
        except Exception as e:
            print(f"Error creating results DataFrame: {e}")
            df_results = pd.DataFrame()
    else:
        df_results = pd.DataFrame()
    
    return df_results, estadisticas, errores

def create_download_files(df_results: pd.DataFrame, estadisticas: dict, errores: list, 
                         resultados_completos: list = None) -> dict:
    """
    Crea los archivos para descargar
    
    Returns:
        dict: Diccionario con los archivos en formato bytes
    """
    archivos = {}
    
    # 1. CSV de resultados para Shopify
    if not df_results.empty:
        csv_buffer = io.StringIO()
        df_results.to_csv(csv_buffer, index=False, encoding='utf-8')
        archivos['descripciones_html_shopify.csv'] = csv_buffer.getvalue().encode('utf-8')
    
    # 2. Archivo HTML con todas las descripciones generadas
    if not df_results.empty and resultados_completos:
        html_completo = generar_archivo_html_completo(resultados_completos)
        archivos['todas_descripciones.html'] = html_completo.encode('utf-8')
    
    # 3. Reporte detallado
    reporte = f"""REPORTE DE GENERACIÓN DE DESCRIPCIONES HTML
==============================================
Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

CONFIGURACIÓN UTILIZADA
-----------------------
Método: {estadisticas.get('metodo_usado', 'No especificado')}
Estilo: {estadisticas.get('estilo_aplicado', 'No especificado')}
Idioma: {estadisticas.get('idioma', 'No especificado')}

RESUMEN EJECUTIVO
-----------------
Total de productos procesados: {estadisticas['total_productos']}
Descripciones exitosas: {estadisticas['exitosos']}
Productos con errores: {estadisticas['errores']}
Tasa de éxito: {(estadisticas['exitosos'] / estadisticas['total_productos'] * 100):.1f}%

ESTADÍSTICAS DE CALIDAD
-----------------------
Fuentes promedio consultadas: {estadisticas.get('fuentes_promedio', 0)}
Características promedio encontradas: {estadisticas.get('caracteristicas_promedio', 0)}
Tiempo total de procesamiento: {estadisticas['tiempo_total']}
"""
    
    if estadisticas['exitosos'] > 0:
        tiempo_por_producto = str(datetime.now() - estadisticas['tiempo_inicio'])
        reporte += f"Tiempo promedio por producto: {tiempo_por_producto}\n"
    
    if errores:
        reporte += "\nERRORES ENCONTRADOS\n"
        reporte += "-------------------\n"
        for error in errores:
            reporte += f"• {error['producto']} (Handle: {error['handle']})\n"
            reporte += f"  Error: {error['error']}\n\n"
    
    reporte += "\nINSTRUCCIONES DE USO\n"
    reporte += "--------------------\n"
    reporte += "1. Importa el archivo CSV en Shopify usando Matrixify\n"
    reporte += "2. Las descripciones se guardarán en el metafield 'custom.html_description'\n"
    reporte += "3. Configura tu tema para mostrar este metafield en la página de producto\n"
    reporte += "4. Las descripciones incluyen CSS inline para máxima compatibilidad\n"
    
    archivos['reporte_generacion.txt'] = reporte.encode('utf-8')
    
    # 4. JSON con datos completos
    if resultados_completos:
        datos_completos = {
            'estadisticas': convertir_datetime_a_string(estadisticas.copy()),
            'configuracion': {
                'metodo': estadisticas.get('metodo_usado'),
                'estilo': estadisticas.get('estilo_aplicado'),
                'idioma': estadisticas.get('idioma')
            },
            'resultados_muestra': resultados_completos[:3] if len(resultados_completos) > 3 else resultados_completos,
            'errores': errores
        }
        
        archivos['datos_completos.json'] = json.dumps(
            datos_completos, 
            indent=2, 
            ensure_ascii=False
        ).encode('utf-8')
    
    return archivos

def generar_archivo_html_completo(resultados: list) -> str:
    """
    Genera un archivo HTML con todas las descripciones para preview
    """
    html_inicio = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Descripciones HTML Generadas</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; }
            .header { background: #2c3e50; color: white; padding: 20px; border-radius: 10px; margin-bottom: 30px; text-align: center; }
            .producto-card { background: white; margin: 30px 0; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .producto-header { background: #3498db; color: white; padding: 15px; margin: -20px -20px 20px -20px; border-radius: 10px 10px 0 0; }
            .producto-info { background: #ecf0f1; padding: 10px; border-radius: 5px; margin-bottom: 20px; font-size: 0.9em; }
            .descripcion-html { border: 2px dashed #bdc3c7; padding: 20px; border-radius: 10px; background: #fefefe; }
            .separador { height: 3px; background: linear-gradient(45deg, #3498db, #2ecc71); margin: 40px 0; border-radius: 2px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎨 Descripciones HTML Generadas</h1>
                <p>Vista previa de todas las descripciones creadas - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
    """
    
    html_productos = ""
    
    for i, resultado in enumerate(resultados, 1):
        producto_info = resultado.get('_producto_info', {})
        html_descripcion = resultado.get('Metafield: custom.html_description [rich_text_field]', '')
        
        html_productos += f"""
        <div class="producto-card">
            <div class="producto-header">
                <h2>#{i} - {producto_info.get('nombre', 'Producto sin nombre')}</h2>
            </div>
            
            <div class="producto-info">
                <strong>Handle:</strong> {resultado.get('Handle', 'N/A')} | 
                <strong>Marca:</strong> {producto_info.get('marca', 'N/A')} | 
                <strong>Categoría:</strong> {producto_info.get('categoria', 'N/A')} | 
                <strong>Fuentes:</strong> {resultado.get('_fuentes_consultadas', 0)} | 
                <strong>Estilo:</strong> {resultado.get('_estilo_aplicado', 'N/A')}
            </div>
            
            <div class="descripcion-html">
                {html_descripcion}
            </div>
        </div>
        
        <div class="separador"></div>
        """
    
    html_fin = """
        </div>
    </body>
    </html>
    """
    
    return html_inicio + html_productos + html_fin

def create_zip_download(archivos: dict) -> bytes:
    """
    Crea un archivo ZIP con todos los archivos generados
    """
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for nombre_archivo, contenido in archivos.items():
            zip_file.writestr(nombre_archivo, contenido)
    
    return zip_buffer.getvalue()

def convertir_datetime_a_string(obj):
    """
    Convierte objetos datetime a string para serialización JSON
    """
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {k: convertir_datetime_a_string(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convertir_datetime_a_string(item) for item in obj]
    else:
        return obj

# Funciones auxiliares para validación

def validar_csv_productos(df: pd.DataFrame) -> tuple:
    """
    Valida que el CSV tenga las columnas necesarias para descripciones
    """
    columnas_requeridas = ['Handle', 'Title']
    columnas_recomendadas = ['Vendor', 'Variant Price', 'Tags']
    
    # Verificar columnas requeridas
    columnas_faltantes = [col for col in columnas_requeridas if col not in df.columns]
    if columnas_faltantes:
        return False, f"❌ Columnas requeridas faltantes: {', '.join(columnas_faltantes)}"
    
    # Verificar columnas recomendadas
    columnas_faltantes_rec = [col for col in columnas_recomendadas if col not in df.columns]
    
    if columnas_faltantes_rec:
        mensaje = f"✅ CSV válido. ⚠️ Columnas recomendadas faltantes: {', '.join(columnas_faltantes_rec)} (Se puede usar pero con información limitada)"
        return True, mensaje
    
    return True, "✅ CSV válido con todas las columnas recomendadas"

def estimar_tiempo_procesamiento(n_productos: int, metodo: str = "auto") -> str:
    """
    Estima el tiempo de procesamiento para descripciones HTML
    """
    # Estimaciones basadas en el método
    tiempo_por_producto = {
        "auto": 30,    # búsqueda web + generación
        "manual": 20   # solo procesamiento de URLs + generación
    }
    
    segundos_estimados = n_productos * tiempo_por_producto.get(metodo, 25)
    
    if segundos_estimados < 60:
        return f"{segundos_estimados} segundos"
    elif segundos_estimados < 3600:
        minutos = segundos_estimados // 60
        return f"{minutos} minutos"
    else:
        horas = segundos_estimados // 3600
        minutos = (segundos_estimados % 3600) // 60
        return f"{horas}h {minutos}m"

def obtener_muestra_productos(df: pd.DataFrame, n: int = 3) -> pd.DataFrame:
    """
    Obtiene una muestra de productos para preview
    """
    columnas_mostrar = ['Handle', 'Title', 'Vendor', 'Variant Price']
    columnas_disponibles = [col for col in columnas_mostrar if col in df.columns]
    
    muestra = df[columnas_disponibles].head(n).copy()
    
    # Truncar títulos largos
    if 'Title' in muestra.columns:
        muestra['Title'] = muestra['Title'].apply(
            lambda x: x[:40] + '...' if len(str(x)) > 40 else x
        )
    
    return muestra