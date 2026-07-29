# SPAD Pro — Analizador de Clorofila Multi-Zona

## Integrantes

- Castillo Castillo Leandro Said
- Ramirez Rosado Robert Anthony
- Viera Hidalgo Gabriel David
- Castillo Sullon Elmer Joel
- Ramírez Ipanaque Alfredo Aldair
- Trelles Flores Néstor Ivan
- Peña Jimenez Esthy Kobel

## Descripción general

**SPAD Pro** es una aplicación de escritorio con interfaz gráfica (Tkinter) que estima de forma no invasiva el contenido relativo de clorofila en hojas de cultivo, a partir del análisis de color de imágenes capturadas por una **cámara IP en tiempo real**. El sistema captura 5 zonas distintas de una misma hoja, calcula el porcentaje de píxeles verdes y amarillos en cada zona mediante procesamiento de imágenes (OpenCV), estima un valor tipo **SPAD** (Soil Plant Analysis Development) a partir de ese porcentaje, promedia las 5 mediciones y guarda automáticamente el historial de cada sesión en un archivo Excel (`spad_historial.xlsx`), sin depender de una base de datos SQL.

## Problema que aborda

La medición del estado nutricional/fotosintético de un cultivo (nivel de clorofila) tradicionalmente requiere:
- Equipos comerciales especializados (ej. medidor SPAD-502), de costo elevado y de acceso limitado para pequeños productores o proyectos educativos/de investigación con presupuesto reducido.
- Un proceso manual, punto por punto, sin un registro histórico centralizado y fácil de auditar.

Esto dificulta el monitoreo continuo, económico y accesible del estado de salud de las plantas, especialmente en contextos donde no se cuenta con instrumentación de laboratorio.

## Solución propuesta

Un prototipo de bajo costo que:
1. Se conecta a una **cámara IP** (streaming HTTP) para capturar imágenes de la hoja en tiempo real.
2. Segmenta los píxeles verdes y amarillos de cada zona capturada usando el espacio de color **HSV**.
3. Calcula un valor SPAD estimado mediante una correlación lineal simple basada en el porcentaje de verde detectado.
4. Repite la captura en **5 zonas** de la misma hoja para reducir el error de una sola muestra puntual, y calcula el promedio y la desviación estándar entre zonas.
5. Genera un diagnóstico cualitativo (ej. clorofila óptima / moderada / baja) según el valor SPAD promedio.
6. Registra automáticamente cada sesión (resumen + las 5 mediciones individuales) en un archivo **Excel** (`openpyxl`), usando un hilo dedicado y una cola (`queue`) para que el guardado no bloquee ni congele la interfaz ni el análisis de video.
7. Permite consultar, revisar y eliminar sesiones desde una ventana de **historial** dentro de la misma aplicación.

## Objetivos

- Implementar una herramienta de monitoreo de clorofila accesible, sin necesidad de hardware especializado, únicamente con una cámara IP y una computadora.
- Automatizar la captura, el análisis de color y el cálculo del valor SPAD estimado en tiempo real, sin intervención manual del cálculo.
- Mantener un historial persistente y estructurado de las mediciones (por sesión y por zona) que pueda auditarse o exportarse fácilmente al estar en formato Excel.
- Garantizar una interfaz responsiva, evitando que las operaciones de E/S (lectura/escritura de archivos, conexión de red) bloqueen el hilo principal de la interfaz gráfica.

## Limitaciones

- **No es un valor SPAD certificado**: la estimación se basa en una correlación lineal simple (`SPAD ≈ 10 + 0.4 × %verde`) derivada de estudios generales, y **no reemplaza una calibración real con un medidor SPAD-502**. Los valores deben tomarse como una referencia relativa, no absoluta.
- La precisión depende fuertemente de las **condiciones de iluminación** al momento de la captura (luz natural variable, sombras, reflejos), ya que la segmentación de color se basa en rangos HSV fijos.
- Requiere una **cámara IP con streaming HTTP accesible en la red local** (la URL del stream está fija en el código: `http://192.168.1.1:81/stream`); no soporta cámaras USB directamente ni múltiples fuentes de video simultáneas.
- El umbral mínimo de píxeles detectados (500) puede descartar zonas con hojas muy pequeñas o capturas mal encuadradas, sin ofrecer retroalimentación detallada del motivo del descarte.
- No incluye un modelo de machine learning ni una validación estadística rigurosa frente a mediciones de laboratorio; es un prototipo académico/demostrativo.
- El historial en Excel no está pensado para grandes volúmenes de datos concurrentes ni para múltiples usuarios escribiendo al mismo tiempo (es de uso local, mono-usuario).
- La interfaz y el tamaño de ventana no son responsivos (`resizable(False, False)`), por lo que no se adapta a distintas resoluciones de pantalla.

## Dataset

Este proyecto **no utiliza un dataset público**. Las imágenes se generan en tiempo real mediante la captura directa desde una cámara IP conectada a la red local, por lo que no existen datos preexistentes ni un enlace de descarga asociado.

## Sistema operativo y entorno de trabajo

El proyecto tiene dos componentes con entornos distintos: la **aplicación de escritorio** (Python) y el **firmware de la cámara** (ESP32-CAM, Arduino).

| Ítem | Detalle |
|---|---|
| Sistema operativo | Windows |
| Lenguaje (app de escritorio) | Python 3.x |
| Entorno de ejecución (app de escritorio) | Script de escritorio (interfaz gráfica Tkinter, ejecución local) |
| Lenguaje/firmware (cámara) | C/C++ (Arduino), sobre el core Arduino-ESP32 |
| Entorno de desarrollo (cámara) | Arduino IDE 1.8.19+ o 2.x, con soporte de placas ESP32 |
| Hardware de captura | Módulo **ESP32-CAM (AI Thinker)**, configurado como Access Point WiFi propio |
| Fuente de video | Streaming HTTP servido por el ESP32-CAM (`http://192.168.1.1:81/stream`) |
| Persistencia de datos | Archivo local `spad_historial.xlsx` (Excel), generado junto al script |

> Nota: verifica y ajusta la versión exacta de Python instalada en tu equipo (recomendado **Python 3.10+**) ejecutando `python --version` en la terminal (CMD/PowerShell).

## Paquetes y versiones utilizadas

| Paquete | Versión de referencia | Uso en el proyecto |
|---|---|---|
| `opencv-python` | 4.13.0 | Captura y procesamiento de imágenes (conversión de color, máscaras HSV) |
| `Pillow` | 12.1.1 | Conversión de frames de OpenCV a formato compatible con Tkinter |
| `numpy` | 2.4.4 | Operaciones matemáticas sobre arrays (rangos de color, cálculos) |
| `openpyxl` | 3.1.5 | Lectura y escritura del historial en formato Excel (.xlsx) |
| `tkinter` | Incluido en la instalación estándar de Python | Interfaz gráfica de usuario |

> ⚠️ Estas versiones son de referencia. Para reflejar **exactamente** las versiones que usaste en tu entorno de desarrollo en Windows, abre una terminal (CMD/PowerShell) en la carpeta del proyecto (con el entorno virtual activado, si usas uno) y ejecuta:
> ```bash
> pip freeze > requirements.txt
> ```
> Esto generará un archivo `requirements.txt` con las versiones exactas instaladas en tu máquina, que puedes anexar o reemplazar en esta sección.

## Instalación rápida (aplicación de escritorio - Python)

```bash
pip install opencv-python pillow numpy openpyxl
```

## Ejecución (aplicación de escritorio - Python)

```bash
python SPAD_PROYECTO_FINAL.py
```

Antes de ejecutar, asegúrate de:
1. Editar la variable `self.url` en el código con la dirección IP real de tu cámara (por defecto: `http://192.168.1.1:81/stream`).
2. Tener la cámara IP conectada y accesible en la misma red local que el equipo donde corre el script.

---

## Firmware de la cámara (ESP32-CAM) — Modo Access Point

La "cámara IP" que consume la aplicación de Python **no es una cámara IP comercial**: es un módulo **ESP32-CAM (modelo AI Thinker)** programado como servidor de streaming, que además se configura como su propio **punto de acceso WiFi (Access Point)**. El ESP32-CAM crea su propia red WiFi y la computadora se conecta a esa red para recibir el stream de video, sin necesidad de un router intermedio.

### Archivos del firmware

| Archivo | Rol |
|---|---|
| `esp32camAP.ino` | Sketch principal: configura la cámara, crea el Access Point WiFi y arranca el servidor de streaming. |
| `app_httpd.cpp` | Implementa el servidor HTTP (`/stream`, captura de frames, endpoints de control de la cámara). |
| `camera_pins.h` | Define el mapeo de pines GPIO según el modelo de placa ESP32-CAM seleccionado. |
| `camera_index.h` | Página web / interfaz HTML embebida que sirve el servidor para el panel de control de la cámara. |

### 1. Estructura de carpeta requerida (Arduino IDE)

El Arduino IDE **exige que el archivo `.ino` esté dentro de una carpeta con el mismo nombre exacto**. Antes de abrir el proyecto, organiza los 4 archivos así:

```
esp32camAP/
├── esp32camAP.ino
├── app_httpd.cpp
├── camera_index.h
└── camera_pins.h
```

> ⚠️ Importante: la carpeta debe llamarse **`esp32camAP`** (idéntico al nombre del `.ino`, sin la extensión), y los 4 archivos deben estar juntos, en el mismo nivel, dentro de esa carpeta. Si el `.ino` está suelto o el nombre de la carpeta no coincide, Arduino IDE no compilará correctamente el proyecto.

### 2. Instalar el soporte de placas ESP32 en Arduino IDE

1. Abre **Arduino IDE** → `Archivo` → `Preferencias`.
2. En **"Gestor de URLs Adicionales de Tarjetas"**, agrega:
   ```
   https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
   ```
3. Ve a `Herramientas` → `Placa` → `Gestor de Tarjetas`, busca **"esp32"** (por Espressif Systems) e instálalo.

### 3. Librerías necesarias

Este proyecto **no requiere instalar librerías adicionales desde el Gestor de Librerías**. Todo lo que usa el firmware (`esp_camera.h`, `WiFi.h`, `esp_http_server.h`, `img_converters.h`, `fb_gfx.h`, etc.) ya viene incluido automáticamente al instalar el **paquete de placas ESP32** del paso anterior (forma parte del "core" de Arduino-ESP32, específicamente del ejemplo `CameraWebServer`).

Lo único indispensable es:
- **Paquete de placas ESP32** (Arduino-ESP32 core) — ver paso 2.
- **Arduino IDE 1.8.19 o superior**, o **Arduino IDE 2.x** (recomendado).

### 4. Selección de placa y configuración antes de subir el código

En `Herramientas`, configura:

| Opción | Valor |
|---|---|
| Placa | `AI Thinker ESP32-CAM` (dentro de `ESP32 Arduino`) |
| Partition Scheme | `Huge APP (3MB No OTA/1MB SPIFFS)` |
| PSRAM | `Enabled` |
| Puerto | El puerto COM donde se detecta el ESP32-CAM |

En `esp32camAP.ino`, el modelo de cámara ya está fijado en el código como:
```cpp
#define CAMERA_MODEL_AI_THINKER
```
(no es necesario cambiar nada aquí si usas el módulo AI Thinker estándar).

### 5. Conexión física para subir el sketch (modo programación)

El ESP32-CAM no tiene puerto USB propio, por lo que se necesita un **programador FTDI/USB-Serial (5V)** conectado así:

- Conectar el pin **GPIO0 a GND** (esto pone al módulo en modo flasheo/programación).
- Conectar TX/RX del programador cruzados con RX/TX del ESP32-CAM.
- Alimentar con 5V.
- Presionar el botón **RESET** del ESP32-CAM antes de subir el código.
- Una vez subido el sketch, **desconectar GPIO0 de GND** y volver a resetear para que arranque en modo normal (no programación).

### 6. Credenciales del Access Point (deben coincidir con la app de Python)

El sketch configura el ESP32-CAM como Access Point con estos valores por defecto (definidos en `esp32camAP.ino`):

```cpp
const char* ssid     = "ESP32CAM";
const char* password = "subscribenow";
IPAddress local_ip(192,168,1,1);
```

Esto significa que, al encender el ESP32-CAM, se crea una red WiFi llamada **`ESP32CAM`** (contraseña `subscribenow`), y el servidor de streaming queda disponible en `http://192.168.1.1:81/stream` — **la misma URL que ya está fija en `SPAD_PROYECTO_FINAL.py`** (`self.url`). Si cambias el SSID, la contraseña o la IP en el `.ino`, recuerda actualizar también la URL correspondiente en el script de Python.

### 7. Flujo de uso completo

1. Sube el firmware al ESP32-CAM siguiendo los pasos anteriores.
2. Enciende el ESP32-CAM (ya sin GPIO0 a GND) → se crea la red WiFi `ESP32CAM`.
3. Desde la computadora Windows donde correrás `SPAD_PROYECTO_FINAL.py`, conéctate a esa red WiFi (`ESP32CAM` / `subscribenow`).
4. Ejecuta la aplicación de Python; esta se conectará automáticamente a `http://192.168.1.1:81/stream` para mostrar el video en vivo y realizar las capturas de las 5 zonas.
