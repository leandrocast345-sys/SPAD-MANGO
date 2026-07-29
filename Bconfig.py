"""
config.py
=========
Configuración global de la aplicación SPAD Pro: paleta de colores, fuentes
y constantes generales. Centralizar estos valores aquí permite cambiar el
"look & feel" de toda la app editando un solo archivo.
"""

import os

# Paleta de colores
BG          = "#09110D"  # Color de fondo principal de la ventana
PANEL       = "#141F18"  # Color de fondo de los paneles de video y resultados
BORDER      = "#1E3028"  # Color de borde de los paneles y divisores
ACCENT      = "#4ADE80"  # Color de acento principal (verde) para botones y texto destacado
ACCENT_WARM = "#FCD34D"  # Color de acento secundario (amarillo) para advertencias
TEXT_SEC    = "#6EAA84"  # Color de texto secundario (gris verdoso) para etiquetas y descripciones
TEXT_DIM    = "#2E4A38"  # Color de texto atenuado (gris oscuro) para información menos relevante
BTN_BG      = "#1A3B27"  # Color de fondo de los botones
BTN_HOVER   = "#255C3C"  # Color de fondo de los botones cuando el mouse pasa por encima
RED         = "#F87171"  # Color rojo para alertas y errores
BLUE        = "#60A5FA"  # Color azul para información destacada

# Fuentes
FONT_MONO = ("Courier New", 10)          # Fuente monoespaciada para mostrar valores de SPAD y porcentajes
FONT_BIG  = ("Courier New", 28, "bold")  # Fuente grande y en negrita para mostrar el valor SPAD promedio
FONT_MED  = ("Courier New", 13, "bold")  # Fuente mediana y en negrita para mostrar valores de SPAD individuales

# Parámetros generales de la app
NUM_CAPTURAS = 5   # zonas de la hoja a capturar
URL_CAMARA   = "http://192.168.1.1:81/stream"  # URL de la cámara IP (ajustar según la configuración de la cámara)

# Base de datos Excel
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "spad_historial.xlsx")  # Ruta del archivo Excel donde se guarda el historial, ubicado junto al script.
HEADERS_RESUMEN    = ["ID Sesion", "Fecha", "SPAD Promedio", "Verde Promedio %", "Amarillo Promedio %", "Desv. Estandar", "Diagnostico"]  # Encabezados de la hoja "Resumen" (una fila por sesión de 5 zonas).
HEADERS_MEDICIONES = ["ID Sesion", "Zona", "Verde %", "Amarillo %", "SPAD"]  # Encabezados de la hoja "Mediciones" (una fila por cada zona capturada).
