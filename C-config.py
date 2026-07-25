"""
config.py
Configuración visual y constantes globales de SPAD Pro.
Colores, fuentes y parámetros de la aplicación.
"""

# Colores de la interfaz
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
FONT_MONO = ("Courier New", 10)          # Fuente monoespaciada para valores de SPAD y porcentajes
FONT_BIG  = ("Courier New", 28, "bold")  # Fuente grande para el valor SPAD promedio
FONT_MED  = ("Courier New", 13, "bold")  # Fuente mediana para valores de SPAD individuales

# Parámetros de la app
NUM_CAPTURAS = 5   # zonas de la hoja a capturar

# Notas sobre las variables usadas en el análisis:
#   pv     = porcentaje de píxeles verdes  (0-100)
#   pa     = porcentaje de píxeles amarillos (0-100)
#   spad   = valor SPAD estimado (correlación basada en estudios generales con el verde)
#   mask_v = máscara binaria de píxeles verdes
#   mask_a = máscara binaria de píxeles amarillos
