"""
captura.py
Lógica de captura de zonas, cálculo de promedios/diagnóstico,
reinicio del estado y cierre de la aplicación (mixin CapturaMixin).
"""

import threading                     # Permite correr el análisis en un hilo separado sin congelar la UI

import cv2                          # OpenCV: procesamiento de imágenes
import numpy as np                  # NumPy: promedios y desviación estándar

from analisis import analizar_roi
from config import ACCENT, ACCENT_WARM, TEXT_SEC, TEXT_DIM, RED, FONT_MONO, NUM_CAPTURAS


class CapturaMixin:
    """Métodos encargados de la captura de zonas y el cálculo de resultados."""

    def capturar_zona(self):  ## Captura la zona de la hoja que se encuentra dentro del recuadro de análisis en el panel de video en vivo, analiza la región de interés (ROI) para calcular los porcentajes de verde y amarillo, así como un valor SPAD estimado, y actualiza la interfaz gráfica con los resultados obtenidos.
        if self.frame_actual is None or self.analizando:  ## No hace nada si aún no hay video o si ya hay un análisis en curso.
            return
        if len(self.capturas) >= NUM_CAPTURAS:  ## No hace nada si ya se completaron las 5 zonas requeridas.
            return   # ya tenemos todas

        self.analizando = True  ## Marca que hay un análisis en curso, para evitar capturas simultáneas.
        self.btn_cap.config(state="disabled", text="Procesando…", fg=TEXT_DIM)  ## Deshabilita el botón de captura mientras se procesa la imagen.

        def _run():  ## Función interna que se ejecuta en un hilo separado para procesar la captura de la zona de la hoja, evitando que la interfaz gráfica se congele durante el análisis.
            frame = self.frame_actual.copy()  ## Copia el frame actual para analizarlo sin interferir con el hilo de video.
            h, w  = frame.shape[:2]  ## Altura y ancho del frame.
            x1, y1 = w // 10, h // 10          ## Coordenadas superior izquierda del recuadro de análisis (10% del ancho/alto).
            x2, y2 = 9 * w // 10, 9 * h // 10  ## Coordenadas inferior derecha del recuadro de análisis (90% del ancho/alto).
            roi = frame[y1:y2, x1:x2]  ## Recorte del frame para analizar solo la zona central (misma región que se dibuja en la vista previa).
            res = analizar_roi(roi)  ## Llama a la función de análisis para obtener pv, pa, spad y las máscaras de color.

            if res is None:  ## Si la muestra fue insuficiente (menos de 500 píxeles detectados)...
                self.lbl_diag.config(
                    text="Muestra insuficiente — reencuadra la hoja", fg=RED)  ## Muestra un mensaje de error en el diagnóstico.
                self.btn_cap.config(state="normal",
                                    text=" CAPTURAR ZONA", fg=ACCENT)  ## Vuelve a habilitar el botón de captura para reintentar.
                self.analizando = False  ## Libera el flag de análisis en curso.
                return

            pv, pa, spad, mask_v, mask_a = res  ## Desempaqueta los resultados del análisis.
            idx = len(self.capturas)  ## Índice de la nueva captura (0 a 4).
            self.capturas.append({"pv": pv, "pa": pa, "spad": spad})  ## Guarda los resultados de esta zona en la lista de capturas.

            # Mostrar última captura y sus máscaras
            self._mostrar(roi, self.canvas_ultima, overlay=f"Zona {idx+1} — SPAD {spad:.1f}")  ## Muestra la imagen de la zona capturada en el panel "ÚLTIMA CAPTURA".
            self._mostrar(cv2.bitwise_and(roi, roi, mask=mask_v),
                           self.canvas_verde,
                           overlay=f"Verde {pv:.1f}%")  ## Aplica la máscara verde a la imagen y la muestra en el panel "ZONA VERDE".
            self._mostrar(cv2.bitwise_and(roi, roi, mask=mask_a),
                           self.canvas_amarilla,
                           overlay=f"Amarillo {pa:.1f}%")  ## Aplica la máscara amarilla a la imagen y la muestra en el panel "ZONA AMARILLA".
            self._mostrar_thumb(idx, roi, spad)  ## Actualiza la miniatura correspondiente con la imagen y el valor SPAD de esta zona.
            self.lbl_n.config(text=f"{idx+1} / {NUM_CAPTURAS}")  ## Actualiza el contador de zonas capturadas (ej. "3 / 5").

            if len(self.capturas) == NUM_CAPTURAS:  ## Si ya se completaron las 5 zonas...
                self._calcular_promedio()  ## Calcula y muestra los resultados promedio finales.
                self.btn_cap.config(state="disabled",
                                    text="5 zonas completadas", fg=TEXT_SEC)  ## Deshabilita el botón de captura ya que no se necesitan más zonas.
            else:  ## Si todavía faltan zonas por capturar...
                self.btn_cap.config(state="normal",
                                    text=f"CAPTURAR ZONA  ({idx+1}/{NUM_CAPTURAS})",
                                    fg=ACCENT)  ## Reactiva el botón mostrando el progreso actual.
            self.analizando = False  ## Libera el flag de análisis en curso.

        threading.Thread(target=_run, daemon=True).start()  ## Lanza el análisis en un hilo daemon separado, para no bloquear la interfaz gráfica.

    def _calcular_promedio(self):  ## Calcula los promedios de los porcentajes de verde y amarillo, así como el valor SPAD promedio y la desviación estándar entre las zonas capturadas, actualizando la interfaz gráfica con los resultados obtenidos y proporcionando un diagnóstico basado en el valor SPAD promedio.
        pvs   = [c["pv"]   for c in self.capturas]  ## Lista de porcentajes de verde de todas las zonas capturadas.
        pas   = [c["pa"]   for c in self.capturas]  ## Lista de porcentajes de amarillo de todas las zonas capturadas.
        spads = [c["spad"] for c in self.capturas]  ## Lista de valores SPAD de todas las zonas capturadas.

        avg_pv   = np.mean(pvs)    # Calcula el promedio de los porcentajes de verde de las zonas capturadas.
        avg_pa   = np.mean(pas)    # Calcula el promedio de los porcentajes de amarillo de las zonas capturadas.
        avg_spad = np.mean(spads)  # Calcula el promedio de los valores SPAD de las zonas capturadas.
        std_spad = np.std(spads)   # Calcula la desviación estándar de los valores SPAD, indicando la variabilidad entre zonas.

        if avg_spad >= 45:  # Clorofila óptima
            diag, col = "Clorofila óptima ", ACCENT
        elif avg_spad >= 30:  ## Clorofila moderada
            diag, col = "Nivel moderado — revisar", ACCENT_WARM
        else:  ## Clorosis (deficiencia de clorofila)
            diag, col = "Clorosis detectada ", RED

        self.lbl_spad.config(text=f"{avg_spad:.1f}", fg=ACCENT)  ## Actualiza la etiqueta grande con el valor SPAD promedio.
        self.lbl_verde.config(text=f"{avg_pv:.1f}%")  ## Actualiza la etiqueta con el porcentaje de verde promedio.
        self.lbl_amarillo.config(text=f"{avg_pa:.1f}%")  ## Actualiza la etiqueta con el porcentaje de amarillo promedio.
        self.lbl_diag.config(text=diag, fg=col)  ## Actualiza el diagnóstico textual, con su color correspondiente (verde/amarillo/rojo).
        self.lbl_std.config(text=f"± {std_spad:.2f}  (variación entre zonas)")  ## Actualiza la etiqueta de desviación estándar.

        self._actualizar_barra(avg_pv, avg_pa)  ## Redibuja la barra cromática con los nuevos promedios.

    def _actualizar_barra(self, pv, pa):  ## Actualiza la barra cromática que muestra la distribución promedio de los colores verde y amarillo en las zonas capturadas, dibujando rectángulos proporcionales a los porcentajes de verde y amarillo calculados.
        self.bar_canvas.update_idletasks()  ## Fuerza la actualización de la geometría del canvas para obtener su ancho real.
        W = self.bar_canvas.winfo_width()  ## Ancho actual del canvas de la barra, en píxeles.
        H = 10  ## Alto fijo de la barra, en píxeles.
        self.bar_canvas.delete("all")  ## Limpia cualquier dibujo previo en la barra.
        self.bar_canvas.create_rectangle(0, 0, W, H, fill=TEXT_DIM, outline="")  ## Dibuja el fondo completo de la barra (color atenuado).
        xv = int(W * pv / 100)  ## Calcula la posición final del rectángulo verde, proporcional al porcentaje de verde promedio.
        self.bar_canvas.create_rectangle(0, 0, xv, H, fill=ACCENT, outline="")  ## Dibuja el segmento verde de la barra.
        xa = int(W * pa / 100)  ## Calcula el ancho del rectángulo amarillo, proporcional al porcentaje de amarillo promedio.
        self.bar_canvas.create_rectangle(xv, 0, xv + xa, H, fill=ACCENT_WARM, outline="")  ## Dibuja el segmento amarillo de la barra, justo después del segmento verde.

    def reiniciar(self):  ## Reinicia la aplicación, borrando todas las capturas de zonas realizadas, restableciendo los valores de SPAD y porcentajes a sus valores iniciales y limpiando los paneles de video y miniaturas.
        self.capturas = []  ## Reinicia la lista de capturas, eliminando todas las zonas capturadas previamente.
        self.thumb_imgs = [None] * NUM_CAPTURAS  ## Reinicia las referencias de imágenes de las miniaturas.
        for i, (c, TW, TH) in enumerate(self.thumbs):  ## Itera sobre cada miniatura para restaurar su estado inicial (número de zona, sin imagen).
            c.delete("all")  ## Borra el contenido actual de la miniatura.
            c.create_text(TW // 2, TH // 2, text=f"{i+1}", fill=TEXT_DIM,
                           font=("Courier New", 18), tags="num")  ## Vuelve a dibujar el número de zona como placeholder.
            self.spad_lbls[i].config(text="—", fg=TEXT_DIM)  ## Restaura la etiqueta SPAD de esa miniatura a su valor inicial.

        self.lbl_n.config(text="0 / 5")  ## Reinicia el contador de zonas capturadas.
        self.lbl_spad.config(text="—", fg=TEXT_DIM)  ## Reinicia la etiqueta de SPAD promedio.
        self.lbl_verde.config(text="—%")  ## Reinicia la etiqueta de verde promedio.
        self.lbl_amarillo.config(text="—%")  ## Reinicia la etiqueta de amarillo promedio.
        self.lbl_diag.config(text="Captura 5 zonas de la hoja", fg=TEXT_SEC)  ## Restaura el mensaje inicial de diagnóstico.
        self.lbl_std.config(text="—")  ## Reinicia la etiqueta de desviación estándar.
        self.bar_canvas.delete("all")  ## Limpia la barra cromática.

        # Limpiar paneles
        for canvas in [self.canvas_ultima, self.canvas_verde, self.canvas_amarilla]:  ## Itera sobre los paneles de última captura, zona verde y zona amarilla, restaurando el mensaje "SIN SEÑAL".
            canvas.delete("all")  ## Borra cualquier contenido previo del panel.
            canvas.create_text(self.PW // 2, self.PH // 2, text="SIN SEÑAL",
                                fill=TEXT_DIM, font=FONT_MONO, tags="nosig")  ## Dibuja el texto "SIN SEÑAL" en el centro del panel.

        self.btn_cap.config(state="normal",
                             text=" CAPTURAR ZONA", fg=ACCENT)  ## Habilita nuevamente el botón de captura para iniciar una nueva ronda de 5 zonas.

    def on_closing(self):  ## Maneja el evento de cierre de la ventana principal, deteniendo la captura de video y destruyendo la ventana para finalizar la aplicación de manera ordenada.
        self.running = False  ## Señala al hilo de stream_video que debe detenerse (rompe su bucle while).
        self.window.destroy()  ## Cierra la ventana principal de Tkinter.
