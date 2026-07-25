"""
analisis.py
Lógica de procesamiento de imagen: segmentación de color
y estimación del valor SPAD a partir de una región de interés (ROI).
"""

import cv2                          # OpenCV: procesamiento de imágenes
import numpy as np                  # NumPy: operaciones matemáticas sobre arrays (máscaras, conteos, etc.)


def analizar_roi(roi):  ## Analiza la región de interés (ROI) de la hoja y calcula los porcentajes de verde y amarillo, así como un valor SPAD estimado.
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)  ## Convierte la imagen de BGR a HSV para facilitar la segmentación de colores.
    mask_v = cv2.inRange(hsv, np.array([30, 40, 30]),  np.array([90, 255, 200]))  ## Crea una máscara binaria para los píxeles verdes dentro del rango especificado.
    mask_a = cv2.inRange(hsv, np.array([10, 40, 40]),  np.array([30, 255, 255]))  ## Crea una máscara binaria para los píxeles amarillos dentro del rango especificado.
    av = cv2.countNonZero(mask_v)  ## Cuenta el número de píxeles verdes en la máscara.
    aa = cv2.countNonZero(mask_a)  ## Cuenta el número de píxeles amarillos en la máscara.
    total = av + aa  ## Calcula el total de píxeles detectados (verdes + amarillos).
    if total < 500:  ## Si el total de píxeles detectados es menor a 500, se considera que la muestra es insuficiente para un análisis confiable.
        return None
    pv   = (av / total) * 100  ## Calcula el porcentaje de píxeles verdes respecto al total.
    pa   = (aa / total) * 100  ## Calcula el porcentaje de píxeles amarillos respecto al total.
    spad = 10 + (pv * 0.4)  ## Estima un valor SPAD basado en el porcentaje de verde, usando una correlación lineal simple (10 + 0.4 * pv).
    return pv, pa, spad, mask_v, mask_a  ## Devuelve los resultados del análisis: porcentaje de verde, porcentaje de amarillo, valor SPAD estimado y las máscaras binarias correspondientes.
