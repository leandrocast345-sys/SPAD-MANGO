# 🌿 SPAD Pro — Analizador de Clorofila Multi-Zona

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

| Ítem | Detalle |
|---|---|
| Sistema operativo | Windows |
| Lenguaje | Python 3.x |
| Entorno de ejecución | Script de escritorio (interfaz gráfica Tkinter, ejecución local) |
| Fuente de video | Cámara IP vía streaming HTTP (`http://<ip>:81/stream`) |
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

## Instalación rápida

```bash
pip install opencv-python pillow numpy openpyxl
```

## Ejecución

```bash
python SPAD_PROYECTO_FINAL.py
```

Antes de ejecutar, asegúrate de:
1. Editar la variable `self.url` en el código con la dirección IP real de tu cámara (por defecto: `http://192.168.1.1:81/stream`).
2. Tener la cámara IP conectada y accesible en la misma red local que el equipo donde corre el script.
