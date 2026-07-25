"""
ui.py
Construcción de la interfaz gráfica de SPAD Pro (Tkinter).
Se implementa como un mixin (UIBuilderMixin) que la clase principal
SPADApp combina junto con los demás mixins de la aplicación.
"""

import tkinter as tk

from config import (
    BG, PANEL, BORDER, ACCENT, ACCENT_WARM, TEXT_SEC, TEXT_DIM,
    BTN_BG, BTN_HOVER, FONT_MONO, FONT_BIG, NUM_CAPTURAS,
)


class UIBuilderMixin:
    """Métodos encargados de construir todos los widgets de la interfaz."""

    def _build_ui(self):  ## Construye toda la interfaz gráfica de la aplicación: encabezado, paneles de video, tira de miniaturas, botones y panel de resultados.

        # Encabezado
        hdr = tk.Frame(self.window, bg=BG)  ## Crea un marco para el encabezado de la aplicación, con un fondo del color definido en BG.
        hdr.pack(fill="x", padx=20, pady=(16, 4))  ## Empaqueta el marco del encabezado ocupando todo el ancho disponible, con padding horizontal de 20 px y vertical de 16 px arriba y 4 px abajo.
        tk.Label(hdr, text="◈  SPAD PRO", bg=BG, fg=ACCENT,
                 font=("Segoe UI", 14, "bold")).pack(side="left")  ## Título principal de la app, alineado a la izquierda del encabezado.
        tk.Label(hdr, text="Análisis Multi-Zona de Clorofila",
                 bg=BG, fg=TEXT_SEC, font=("Segoe UI", 9)).pack(side="left", padx=10)  ## Subtítulo descriptivo junto al título.
        self.lbl_status = tk.Label(hdr, text="● EN VIVO", bg=BG,
                                   fg=TEXT_DIM, font=("Segoe UI", 8, "bold"))  ## Etiqueta de estado de conexión con la cámara (cambia de color según stream_video).
        self.lbl_status.pack(side="right")  ## Alinea la etiqueta de estado a la derecha del encabezado.
        tk.Frame(self.window, bg=BORDER, height=1).pack(fill="x", padx=20, pady=4)  ## Línea divisoria horizontal debajo del encabezado.

        # Fila superior: video en vivo + última captura
        top = tk.Frame(self.window, bg=BG)  ## Crea un marco para la fila superior que contendrá los 4 paneles de video.
        top.pack(padx=20, pady=6)  ## Empaqueta el marco de la fila superior con padding horizontal de 20 px y vertical de 6 px.

        self.canvas_vid      = self._panel(top, "VISTA EN VIVO")      ## Panel de video en vivo, donde se muestra la transmisión de la cámara IP.
        self.canvas_ultima   = self._panel(top, "ÚLTIMA CAPTURA")     ## Panel para mostrar la última captura realizada.
        self.canvas_verde    = self._panel(top, "ZONA VERDE")        ## Panel para mostrar la zona verde detectada usando la máscara binaria correspondiente.
        self.canvas_amarilla = self._panel(top, "ZONA AMARILLA")     ## Panel para mostrar la zona amarilla detectada usando la máscara binaria correspondiente.

        ## CAPTURAS DE ZONAS DE LA HOJA
        tk.Frame(self.window, bg=BORDER, height=1).pack(fill="x", padx=20, pady=(4, 2))  ## Línea divisoria entre la fila superior de paneles y la sección de capturas.
        strip_hdr = tk.Frame(self.window, bg=BG)  ## Crea un marco para el encabezado de la sección de capturas de zonas.
        strip_hdr.pack(fill="x", padx=20)
        tk.Label(strip_hdr, text="CAPTURAS DE ZONAS", bg=BG,
                 fg=TEXT_SEC, font=("Segoe UI", 7, "bold")).pack(side="left")  ## Título de la sección de miniaturas.
        self.lbl_n = tk.Label(strip_hdr, text="0 / 5", bg=BG,
                               fg=ACCENT, font=("Courier New", 9, "bold"))  ## Contador de zonas capturadas (ej. "2 / 5").
        self.lbl_n.pack(side="right")

        self.strip_frame = tk.Frame(self.window, bg=BG)  ## Marco contenedor de todas las miniaturas de zonas.
        self.strip_frame.pack(padx=20, pady=(2, 6))

        self.thumbs      = []   # tk widgets ## Contenedores (canvas) de miniaturas de cada zona capturada.
        self.thumb_imgs  = []   # PhotoImage refs (evitar GC) ## Referencias a las imágenes de las miniaturas para que el recolector de basura no las elimine.
        self.spad_lbls   = []   # etiquetas SPAD por miniatura ## Etiquetas que muestran el valor SPAD correspondiente a cada miniatura.

        TW, TH = 180, 100  ## Tamaño (ancho, alto) de cada miniatura.
        for i in range(NUM_CAPTURAS):  ## Itera sobre el número de capturas definidas (5 zonas) creando un contenedor de miniatura por cada una.
            col = tk.Frame(self.strip_frame, bg=BORDER, padx=1, pady=1)  ## Marco exterior de la miniatura (funciona como borde).
            col.pack(side="left", padx=4)
            inner = tk.Frame(col, bg=PANEL)  ## Marco interior de la miniatura, con el color de panel.
            inner.pack()
            tk.Label(inner, text=f"ZONA {i+1}", bg=PANEL, fg=TEXT_DIM,
                     font=("Segoe UI", 6, "bold")).pack(pady=(3, 0))  ## Etiqueta con el número de zona.
            c = tk.Canvas(inner, width=TW, height=TH, bg="#080F0B",
                           highlightthickness=0)  ## Canvas donde se dibujará la miniatura de la imagen capturada.
            c.pack(padx=0, pady=(1, 0))
            c.create_text(TW // 2, TH // 2, text=f"{i+1}", fill=TEXT_DIM,
                           font=("Courier New", 18), tags="num")  ## Número de zona mostrado en el centro mientras no hay captura (placeholder).
            lbl = tk.Label(inner, text="—", bg=PANEL, fg=TEXT_DIM,
                           font=("Courier New", 9, "bold"))  ## Etiqueta que mostrará el valor SPAD de esa zona una vez capturada.
            lbl.pack(pady=(1, 3))
            self.thumbs.append((c, TW, TH))  ## Guarda el canvas junto a su ancho/alto para usarlo luego en _mostrar_thumb.
            self.thumb_imgs.append(None)     ## Reserva un espacio para la referencia de imagen de esta miniatura.
            self.spad_lbls.append(lbl)       ## Guarda la etiqueta SPAD para poder actualizarla después.

        # Botones
        btn_row = tk.Frame(self.window, bg=BG)  ## Crea un marco para contener los botones de control de la aplicación.
        btn_row.pack(pady=(4, 4))  ## Empaqueta el marco de botones con padding vertical de 4 px arriba y abajo.

        self.btn_cap = self._btn(btn_row, " CAPTURAR ZONA",
                                  self.capturar_zona, ACCENT)  ## Botón principal para capturar la siguiente zona de la hoja.
        self.btn_cap.pack(side="left", padx=6)

        self.btn_reset = self._btn(btn_row, " REINICIAR",
                                    self.reiniciar, TEXT_SEC)  ## Botón secundario para reiniciar toda la sesión de capturas.
        self.btn_reset.pack(side="left", padx=6)  ## Empaqueta el botón de reinicio a la izquierda, con padding de 6 px entre botones.

        # Panel de resultados promedio
        tk.Frame(self.window, bg=BORDER, height=1).pack(fill="x", padx=20, pady=(4, 0))  ## Línea divisoria entre la sección de capturas y el panel de resultados.
        res_outer = tk.Frame(self.window, bg=BORDER)  ## Marco exterior del panel de resultados (funciona como borde).
        res_outer.pack(padx=20, pady=(0, 4), fill="x")
        res = tk.Frame(res_outer, bg=PANEL, padx=20, pady=12)  ## Marco interior del panel de resultados, con el color de panel.
        res.pack(fill="x", padx=1, pady=1)

        spad_col = tk.Frame(res, bg=PANEL)  ## Crea la columna que mostrará el valor SPAD promedio.
        spad_col.pack(side="left", padx=(0, 30))
        tk.Label(spad_col, text="SPAD PROMEDIO", bg=PANEL, fg=TEXT_SEC,
                 font=("Segoe UI", 8, "bold")).pack(anchor="w")
        self.lbl_spad = tk.Label(spad_col, text="—", bg=PANEL,
                                  fg=TEXT_DIM, font=FONT_BIG)  ## Etiqueta grande con el valor SPAD promedio final.
        self.lbl_spad.pack(anchor="w")  ## Empaqueta la etiqueta SPAD promedio alineada a la izquierda.
        tk.Label(spad_col, text="unidades relativas  (5 zonas)", bg=PANEL,
                 fg=TEXT_DIM, font=("Segoe UI", 8)).pack(anchor="w")

        tk.Frame(res, bg=BORDER, width=1).pack(side="left", fill="y", padx=10)  ## Línea vertical divisoria entre la columna SPAD y la columna de métricas.

        met_col = tk.Frame(res, bg=PANEL)  ## Crea la columna de métricas: verde, amarillo, diagnóstico y desviación estándar.
        met_col.pack(side="left")  ## Empaqueta la columna de métricas a la izquierda, junto a la columna de SPAD promedio.
        self.lbl_verde    = self._metric(met_col, "Verde promedio",    "—%",  ACCENT)
        self.lbl_amarillo = self._metric(met_col, "Amarillo promedio", "—%",  ACCENT_WARM)
        self.lbl_diag     = self._metric(met_col, "Diagnóstico",       "Captura 5 zonas de la hoja", TEXT_SEC)
        self.lbl_std      = self._metric(met_col, "Desv. estándar",    "—",   TEXT_SEC)

        # Barra cromática
        bar_frame = tk.Frame(self.window, bg=BG)  ## Crea un marco para contener la barra cromática (distribución verde/amarillo).
        bar_frame.pack(padx=20, pady=(2, 4), fill="x")
        tk.Label(bar_frame, text="DISTRIBUCIÓN CROMÁTICA PROMEDIO", bg=BG,
                 fg=TEXT_SEC, font=("Segoe UI", 7, "bold")).pack(anchor="w")
        bar_outer = tk.Frame(bar_frame, bg=BORDER, height=10)  ## Marco contenedor de la barra (borde).
        bar_outer.pack(fill="x", pady=3)
        bar_outer.pack_propagate(False)  ## Evita que el marco cambie de tamaño según su contenido, manteniendo el alto fijo en 10 px.
        self.bar_canvas = tk.Canvas(bar_outer, height=10, bg=TEXT_DIM,
                                     highlightthickness=0)  ## Canvas donde se dibujan los rectángulos verde/amarillo proporcionales.
        self.bar_canvas.pack(fill="both")

        # Pie
        tk.Frame(self.window, bg=BORDER, height=1).pack(fill="x", padx=20, pady=(4, 0))  ## Línea divisoria entre el panel de resultados y el pie de página.
        footer = tk.Frame(self.window, bg=BG)
        footer.pack(fill="x", padx=20, pady=5)
        tk.Label(footer,
                 text="Captura 5 zonas distintas de la hoja → el sistema promedia y muestra el SPAD final  ·  Calibrar con SPAD-502 para valores absolutos",
                 bg=BG, fg=TEXT_DIM, font=("Segoe UI", 8)).pack(side="left")  ## Texto de ayuda/instrucciones al pie de la ventana.

    def _panel(self, parent, titulo):  ## Crea un panel de video con un título; se usa para vista en vivo, última captura, zona verde y zona amarilla.
        wrapper = tk.Frame(parent, bg=BORDER, padx=1, pady=1)  ## Marco exterior del panel (actúa como borde de 1 px).
        wrapper.pack(side="left", padx=5)
        inner = tk.Frame(wrapper, bg=PANEL)  ## Marco interior del panel, con el color de fondo PANEL.
        inner.pack()
        tk.Label(inner, text=titulo, bg=PANEL, fg=TEXT_SEC,
                 font=("Segoe UI", 7, "bold")).pack(anchor="w", padx=5, pady=(3, 0))  ## Título del panel (ej. "VISTA EN VIVO").
        c = tk.Canvas(inner, width=self.PW, height=self.PH,
                       bg="#080F0B", highlightthickness=0)  ## Canvas donde se dibuja la imagen del panel (video o captura).
        c.pack(padx=0, pady=(2, 4))
        c.create_text(self.PW // 2, self.PH // 2, text="SIN SEÑAL",
                       fill=TEXT_DIM, font=FONT_MONO, tags="nosig")  ## Texto "SIN SEÑAL" mostrado mientras no hay imagen (se borra al mostrar la primera imagen).
        return c

    def _btn(self, parent, texto, cmd, color):  ## Crea un botón con estilo personalizado y efecto hover, usado para los controles de la app.
        b = tk.Button(parent, text=texto, command=cmd,
                      bg=BTN_BG, fg=color,
                      activebackground=BTN_HOVER, activeforeground=color,
                      font=("Segoe UI", 11, "bold"),
                      relief="flat", bd=0, padx=24, pady=8, cursor="hand2")  ## Configura el botón: colores, fuente, sin relieve ni borde y cursor de mano.
        b.bind("<Enter>", lambda e: b.config(bg=BTN_HOVER))  ## Cambia el color de fondo cuando el mouse entra en el botón.
        b.bind("<Leave>", lambda e: b.config(bg=BTN_BG))     ## Restaura el color de fondo original cuando el mouse sale del botón.
        return b

    def _metric(self, parent, label, valor, color):  ## Crea un widget de métrica (etiqueta + valor), usado en el panel de resultados promedio.
        row = tk.Frame(parent, bg=PANEL)  ## Marco de la fila que contendrá la etiqueta y el valor.
        row.pack(anchor="w", pady=1)
        tk.Label(row, text=f"{label}:", bg=PANEL, fg=TEXT_SEC,
                 font=("Segoe UI", 8), width=20, anchor="w").pack(side="left")  ## Etiqueta descriptiva de la métrica (ej. "Verde promedio:").
        lbl = tk.Label(row, text=valor, bg=PANEL, fg=color,
                        font=("Segoe UI", 9, "bold"))  ## Etiqueta con el valor actual de la métrica (se actualiza dinámicamente).
        lbl.pack(side="left", padx=4)
        return lbl
