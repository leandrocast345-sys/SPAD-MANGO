"""
app.py
Clase principal de la aplicación SPAD Pro. Combina los mixins de
interfaz (UIBuilderMixin), video (VideoMixin) y captura (CapturaMixin)
en una sola clase, tal como funcionaba en el archivo original.
"""

import threading                     # Permite correr el video en un hilo separado sin congelar la UI

from config import BG
from ui import UIBuilderMixin
from video import VideoMixin
from captura import CapturaMixin


class SPADApp(UIBuilderMixin, VideoMixin, CapturaMixin):  ## Clase principal de la aplicación SPAD Pro, que maneja la interfaz gráfica y la lógica de captura y análisis de imágenes. Hereda los métodos de los tres mixins: UI, video y captura.

    def __init__(self, window):  ## Inicializa la aplicación, configurando la ventana principal, los paneles de video y los botones de control.
        self.window = window
        self.window.title("SPAD Pro — Analizador de Clorofila")
        self.window.configure(bg=BG)  ## Configura el color de fondo de la ventana principal.
        self.window.resizable(False, False)  ## Evita que la ventana sea redimensionable.

        self.PW, self.PH = 300, 210  # tamaño de cada panel de cámara

        # Estado multi-captura
        self.capturas     = []   # lista de dicts {pv, pa, spad}
        self.frame_actual = None
        self.running      = True
        self.analizando   = False

        self._build_ui()  ## Construye toda la interfaz gráfica (método definido en UIBuilderMixin).

        ## conexion con la cámara IP
        self.url = "PONES TU DIRECCION IP HTTP/stream"  ## Dirección del stream de la cámara IP (reemplazar por la IP real).
        threading.Thread(target=self.stream_video, daemon=True).start()  ## Inicia el hilo de captura de video en segundo plano (método definido en VideoMixin).
        self.actualizar_vista_previa()  ## Arranca el ciclo de actualización de la vista previa en vivo (método definido en VideoMixin).
