"""
video.py
Captura de video desde la cámara IP y visualización de frames
en los distintos paneles de la interfaz (mixin VideoMixin).
"""

import time

import cv2                          # OpenCV: captura y procesamiento de imágenes
from PIL import Image, ImageTk       # Pillow: convierte imágenes OpenCV a formato que Tkinter puede mostrar

from config import ACCENT, RED, FONT_MONO


class VideoMixin:
    """Métodos encargados del streaming de video y su renderizado en pantalla."""

    def stream_video(self):  ## Corre en un hilo separado: captura el video en vivo desde la cámara IP, actualiza el estado de la conexión y almacena el último frame capturado para su posterior análisis y visualización en la interfaz gráfica.
        cap = cv2.VideoCapture(self.url)  ## Abre la conexión con la cámara IP usando la URL de streaming.
        while self.running:  ## Bucle que se ejecuta mientras la aplicación siga activa (self.running controlado desde on_closing).
            ret, frame = cap.read()  ## Lee un frame del stream de video.
            if ret:  ## Si la lectura fue exitosa...
                self.frame_actual = frame  ## Guarda el frame actual para que otros métodos (vista previa, captura) lo usen.
                self.lbl_status.config(fg=ACCENT)  ## Pone la etiqueta de estado en verde (conexión activa).
            else:  ## Si falló la lectura (cámara desconectada, error de red, etc.)...
                self.lbl_status.config(fg=RED)  ## Pone la etiqueta de estado en rojo (conexión perdida).
                time.sleep(0.5)  ## Espera medio segundo antes de reintentar, para no saturar el hilo con reintentos.
        cap.release()  ## Libera el recurso de la cámara al salir del bucle (cierre de la app).

    def _mostrar(self, img_bgr, canvas, overlay=None):  ## Muestra una imagen en un canvas de Tkinter, convirtiendo la imagen de BGR a RGB y redimensionándola al tamaño del panel correspondiente. Si se proporciona un texto de superposición, se dibuja sobre la imagen.
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)  ## Convierte la imagen de BGR (formato OpenCV) a RGB (formato que espera Pillow).
        img_pil = Image.fromarray(img_rgb).resize((self.PW, self.PH))  ## Convierte el array de NumPy a imagen de Pillow y la redimensiona al tamaño del panel.
        img_tk  = ImageTk.PhotoImage(img_pil)  ## Convierte la imagen de Pillow a un formato que Tkinter puede mostrar en un Canvas.
        canvas.delete("nosig")  ## Elimina el texto "SIN SEÑAL" si todavía estaba presente en el canvas.
        canvas.create_image(0, 0, anchor="nw", image=img_tk)  ## Dibuja la imagen en la esquina superior izquierda del canvas.
        canvas.image = img_tk  ## Guarda una referencia a la imagen en el propio canvas para evitar que el recolector de basura la elimine.
        if overlay:  ## Si se pasó un texto de superposición (ej. "Zona 2 — SPAD 45.3")...
            canvas.create_text(6, self.PH - 14, anchor="w",
                                text=overlay, fill=ACCENT, font=FONT_MONO)  ## Dibuja el texto en la parte inferior izquierda del canvas, con la fuente monoespaciada.

    def _mostrar_thumb(self, idx, img_bgr, spad):  ## Muestra una miniatura de la zona capturada en el panel correspondiente, redimensionando la imagen al tamaño de la miniatura y actualizando la etiqueta SPAD asociada.
        c, TW, TH = self.thumbs[idx]  ## Recupera el canvas y las dimensiones de la miniatura correspondiente al índice de zona.
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)  ## Convierte la imagen capturada de BGR a RGB.
        img_pil = Image.fromarray(img_rgb).resize((TW, TH))  ## Redimensiona la imagen al tamaño de la miniatura (180x100 por defecto).
        img_tk  = ImageTk.PhotoImage(img_pil)  ## Convierte la imagen a formato Tkinter.
        c.delete("num")  ## Elimina el número de zona (placeholder) que se mostraba antes de la captura.
        c.create_image(0, 0, anchor="nw", image=img_tk)  ## Dibuja la miniatura en el canvas correspondiente.
        c.image = img_tk  ## Guarda una referencia local en el canvas para evitar que se recolecte como basura.
        self.thumb_imgs[idx] = img_tk  ## Guarda también la referencia en la lista general de miniaturas, por seguridad adicional.
        self.spad_lbls[idx].config(text=f"SPAD {spad:.1f}", fg=ACCENT)  ## Actualiza la etiqueta de esa miniatura con el valor SPAD calculado.

    def actualizar_vista_previa(self):  ### Actualiza la vista previa en vivo del video de la cámara IP, dibujando un recuadro de análisis en el centro del panel y mostrando el número de zona actual que se está capturando. Esta función se llama periódicamente para mantener la vista previa actualizada.
        if self.frame_actual is not None:  ## Solo dibuja si ya se ha recibido al menos un frame de la cámara.
            h, w = self.frame_actual.shape[:2]  ## Obtiene alto y ancho del frame actual.
            x1, y1 = w // 10, h // 10          ## Coordenada superior izquierda del recuadro de análisis (10% del ancho/alto).
            x2, y2 = 9 * w // 10, 9 * h // 10  ## Coordenada inferior derecha del recuadro de análisis (90% del ancho/alto).
            fg = self.frame_actual.copy()  ## Copia el frame para no modificar el original al dibujar encima.
            cv2.rectangle(fg, (x1, y1), (x2, y2), (80, 160, 255), 2)  ## Dibuja un recuadro azul en el centro del panel, indicando la región de interés (ROI) que se analizará al capturar.

            L = 16  ## Longitud en píxeles de las líneas diagonales de las esquinas del recuadro.
            for px, py, dx, dy in [(x1, y1, 1, 1), (x2, y1, -1, 1),
                                    (x1, y2, 1, -1), (x2, y2, -1, -1)]:  ## Itera sobre las 4 esquinas del recuadro para dibujar el efecto de "mira" en cada una.
                cv2.line(fg, (px, py), (px + dx * L, py), (80, 200, 255), 3)  ## Dibuja la línea horizontal de la esquina.
                cv2.line(fg, (px, py), (px, py + dy * L), (80, 200, 255), 3)  ## Dibuja la línea vertical de la esquina.

            # Contador en vivo
            n = len(self.capturas)  ## Obtiene el número de zonas capturadas hasta el momento.
            cv2.putText(fg, f"Zona {n+1}/5", (x1 + 6, y1 + 22),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (80, 220, 255), 1, cv2.LINE_AA)  ## Dibuja el texto con el número de zona actual en la esquina superior izquierda del recuadro.

            self._mostrar(fg, self.canvas_vid)  ## Muestra la imagen con el recuadro y el contador en el panel de video en vivo.

        self.window.after(30, self.actualizar_vista_previa)  ## Programa la siguiente actualización en 30 ms, manteniendo la vista previa en vivo de forma continua.
