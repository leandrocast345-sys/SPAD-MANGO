"""
analisis.py
===========
Lógica de procesamiento de imagen: analiza una región de interés (ROI) de
una hoja y estima su valor SPAD (correlación con el porcentaje de verde),
además de los porcentajes de píxeles verdes y amarillos.

Este módulo no depende de Tkinter ni de la interfaz gráfica, por lo que
puede reutilizarse en scripts de línea de comandos, notebooks o pruebas
automatizadas.
"""

import cv2
import numpy as np

# Notas sobre los valores devueltos por analizar_roi():
#   pv     = porcentaje de píxeles verdes  (0-100)
#   pa     = porcentaje de píxeles amarillos (0-100)
#   spad   = valor SPAD estimado (correlación basada en estudios generales con el verde)
#   mask_v = máscara binaria de píxeles verdes
#   mask_a = máscara binaria de píxeles amarillos


def analizar_roi(roi):
    """
    Analiza la región de interés (ROI) de la hoja y calcula los porcentajes
    de verde y amarillo, así como un valor SPAD estimado.

    Parámetros
    ----------
    roi : np.ndarray
        Recorte de la imagen (en formato BGR, como lo entrega OpenCV) que
        contiene la zona de la hoja a analizar.

    Retorna
    -------
    tuple (pv, pa, spad, mask_v, mask_a) o None si la muestra es insuficiente.
    """
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)  # Convierte la imagen de BGR a HSV para facilitar la segmentación de colores.
    mask_v = cv2.inRange(hsv, np.array([30, 40, 30]),  np.array([90, 255, 200]))  # Máscara binaria para los píxeles verdes dentro del rango especificado.
    mask_a = cv2.inRange(hsv, np.array([10, 40, 40]),  np.array([30, 255, 255]))  # Máscara binaria para los píxeles amarillos dentro del rango especificado.
    av = cv2.countNonZero(mask_v)  # Cuenta el número de píxeles verdes en la máscara.
    aa = cv2.countNonZero(mask_a)  # Cuenta el número de píxeles amarillos en la máscara.
    total = av + aa  # Total de píxeles detectados (verdes + amarillos).
    if total < 500:  # Si el total de píxeles detectados es menor a 500, la muestra es insuficiente para un análisis confiable.
        return None
    pv   = (av / total) * 100  # Porcentaje de píxeles verdes respecto al total.
    pa   = (aa / total) * 100  # Porcentaje de píxeles amarillos respecto al total.
    spad = 10 + (pv * 0.4)  # Estima un valor SPAD basado en el porcentaje de verde (correlación lineal simple).
    return pv, pa, spad, mask_v, mask_a
