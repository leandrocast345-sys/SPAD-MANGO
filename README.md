# SPAD Pro — Analizador de Clorofila en Hojas de Mango

Aplicación de escritorio (Tkinter + OpenCV) que estima de forma no invasiva el
contenido relativo de clorofila (valor SPAD) en hojas de mango, a partir del
análisis de color de imágenes capturadas por una cámara IP.

---

## 1. Descripción general

SPAD Pro es una herramienta de visión por computadora que permite capturar,
en tiempo real, distintas zonas de una hoja de mango a través de una cámara
IP y estimar su valor SPAD (Soil Plant Analysis Development), un indicador
ampliamente usado en agronomía para evaluar el estado nutricional y la salud
fotosintética de un cultivo a partir del contenido de clorofila.

El sistema captura 5 zonas distintas de una misma hoja, segmenta los píxeles
verdes y amarillos de cada zona mediante el espacio de color HSV, calcula un
valor SPAD estimado por zona y finalmente promedia los resultados para
entregar un diagnóstico general (clorofila óptima, nivel moderado o
clorosis) junto con su desviación estándar.

## 2. Problema que aborda

La medición del índice SPAD en campo se realiza tradicionalmente con
medidores portátiles ópticos (p. ej. SPAD-502), instrumentos de costo
elevado, de uso manual y limitados a mediciones puntuales hoja por hoja.
Esto dificulta:

- El monitoreo frecuente y a gran escala de plantaciones de mango.
- La detección temprana de clorosis o deficiencias nutricionales en
  grandes extensiones de cultivo.
- El acceso a esta tecnología por parte de pequeños y medianos productores,
  debido al costo de los equipos certificados.

## 3. Solución propuesta

Se propone un sistema de bajo costo basado en visión por computadora que:

1. Se conecta a una cámara IP orientada hacia la hoja de mango.
2. Guía al usuario para capturar 5 zonas representativas de la hoja mediante
   un recuadro de encuadre en pantalla.
3. Segmenta cada zona en píxeles "verdes" y "amarillos" usando umbrales en
   el espacio de color HSV.
4. Estima un valor SPAD por zona mediante una correlación lineal simple con
   el porcentaje de píxeles verdes (`SPAD = 10 + 0.4 × %verde`).
5. Promedia las 5 zonas y presenta un diagnóstico visual (color/etiqueta)
   junto con la variabilidad (desviación estándar) entre zonas.

Esto permite una estimación rápida, repetible y de bajo costo, útil como
herramienta de apoyo y monitoreo — no como reemplazo de un medidor SPAD
certificado.

## 4. Objetivos

### Objetivo general
Desarrollar una aplicación de escritorio que estime el valor SPAD de hojas
de mango a partir del análisis de color de imágenes capturadas por cámara
IP, como alternativa accesible a los medidores SPAD portátiles.

### Objetivos específicos
- Implementar la captura de video en tiempo real desde una cámara IP sin
  bloquear la interfaz gráfica (uso de hilos).
- Segmentar automáticamente los píxeles verdes y amarillos de una hoja
  mediante procesamiento de imagen en el espacio HSV.
- Calcular un valor SPAD estimado por zona y promediar múltiples zonas para
  reducir el error de una sola medición.
- Presentar los resultados de forma clara mediante una interfaz gráfica con
  paneles de video, miniaturas de capturas, métricas y diagnóstico.

## 5. Limitaciones

- **Correlación aproximada, no calibrada científicamente**: la fórmula
  `SPAD = 10 + 0.4 × %verde` es una aproximación lineal genérica y **no**
  reemplaza la calibración con un medidor SPAD-502 u otro instrumento
  certificado. Se recomienda calibrar los umbrales HSV y la fórmula con
  mediciones de referencia antes de un uso productivo.
- **Sensibilidad a la iluminación**: la segmentación por color en HSV es
  sensible a cambios de luz ambiental, sombras y balance de blancos de la
  cámara, lo que puede afectar la precisión de la estimación.
- **Dependencia de la cámara IP**: requiere una cámara IP accesible por red
  local (stream HTTP) y una URL de conexión válida configurada en el código
  (`app.py`, atributo `self.url`).
- **Sin persistencia de datos**: los resultados no se guardan en disco ni en
  base de datos; se pierden al reiniciar o cerrar la aplicación.
- **Sin corrección de perspectiva ni distancia**: no se compensan variaciones
  de distancia hoja-cámara, ángulo de toma ni distorsión del lente.
- **Interfaz de escritorio únicamente**: no cuenta con versión web ni móvil,
  y no es multiplataforma probado (ver sección 7).

## 6. Estructura del proyecto

```
spad_pro/
├── main.py        # Punto de entrada de la aplicación
├── app.py          # Clase principal SPADApp (combina los mixins)
├── config.py       # Colores, fuentes y constantes globales
├── analisis.py     # Lógica de segmentación de color y cálculo de SPAD
├── ui.py           # Construcción de la interfaz gráfica (Tkinter)
├── video.py        # Streaming de cámara IP y actualización de vista previa
├── captura.py      # Captura de zonas, promedios, diagnóstico y reinicio
├── requirements.txt
└── README.md
```

## 7. Entorno de desarrollo y pruebas

| Ítem | Detalle |
|---|---|
| Sistema operativo | Windows 10 / 11 *(ajusta según tu equipo)* |
| Editor / IDE | Visual Studio Code |
| Lenguaje | Python *(ver versión exacta abajo)* |
| Interfaz gráfica | Tkinter (Tcl/Tk 8.6, incluido con Python) |
| Gestor de paquetes | pip |

> **Cómo obtener tus datos exactos:** abre la terminal integrada de VS Code
> (`Ctrl + ñ` o menú *Terminal → Nueva Terminal*) y ejecuta:
> ```powershell
> python --version
> pip show opencv-python
> pip show pillow
> pip show numpy
> ```
> Reemplaza los valores de esta tabla y de la sección 8 con lo que te
> devuelvan esos comandos.

## 8. Versiones de los paquetes utilizados

| Paquete | Versión | Uso en el proyecto |
|---|---|---|
| [opencv-python](https://pypi.org/project/opencv-python/) (`cv2`) | *(completar)* | Captura de video, conversión de color BGR↔HSV↔RGB, segmentación por máscaras, dibujo de recuadros/texto sobre los frames |
| [Pillow](https://pypi.org/project/Pillow/) (`PIL`) | *(completar)* | Conversión de arrays de imagen (NumPy/OpenCV) a un formato compatible con Tkinter (`ImageTk.PhotoImage`) |
| [NumPy](https://pypi.org/project/numpy/) | *(completar)* | Operaciones con arrays, cálculo de promedios y desviación estándar de los valores SPAD |
| `tkinter` | Tcl/Tk 8.6 (incluido en Python) | Interfaz gráfica de escritorio |
| `threading` | Módulo estándar de Python | Ejecutar el streaming de video y el análisis de imagen sin bloquear la UI |
| `time` | Módulo estándar de Python | Pausas cortas al reintentar conexión con la cámara |

Completa la columna "Versión" con el resultado de `pip show` (sección 7).
En Windows normalmente instalarás `opencv-python` (versión estándar, con
soporte de GUI) — es el paquete correcto para este proyecto, ya que la
visualización de imágenes la maneja Tkinter.

Puedes generar un `requirements.txt` fiel a tu propio entorno con:
```bash
pip freeze > requirements.txt
```

## 9. Instalación y ejecución

```bash
# 1. Crear y activar un entorno virtual (recomendado)
python -m venv venv
source venv/bin/activate        # En Windows: venv\Scripts\activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar la URL de la cámara IP en app.py
#    self.url = "http://TU_IP:PUERTO/video"

# 4. Ejecutar la aplicación
python main.py
```

## 10. Uso

1. Al abrir la app, se muestra el video en vivo con un recuadro guía.
2. Encuadra la hoja de mango dentro del recuadro y presiona **CAPTURAR ZONA**.
3. Repite el proceso para 5 zonas distintas de la hoja.
4. Al completar las 5 capturas, la aplicación muestra el SPAD promedio, el
   porcentaje de verde/amarillo, la desviación estándar y un diagnóstico.
5. Usa **REINICIAR** para borrar las capturas y comenzar una nueva medición.
