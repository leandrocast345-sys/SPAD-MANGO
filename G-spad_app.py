"""
spad_app.py
===========
Clase principal de la aplicación SPAD Pro: maneja la interfaz gráfica,
la captura de video desde la cámara IP, la captura y análisis de las
5 zonas de la hoja, y la comunicación con el historial en Excel.
"""

import time
import threading

import cv2
import numpy as np
import tkinter as tk
from PIL import Image, ImageTk

from config import (
    BG, PANEL, BORDER, ACCENT, ACCENT_WARM, TEXT_SEC, TEXT_DIM,
    RED, BLUE, FONT_MONO, FONT_BIG, NUM_CAPTURAS, URL_CAMARA,
)
from analisis import analizar_roi
from excel_db import ExcelDB
from ui_widgets import crear_boton, crear_panel_video, crear_metrica
from historial_window import mostrar_historial


class SPADApp:
    """Clase principal de la aplicación SPAD Pro, que maneja la interfaz gráfica y la lógica de captura y análisis de imágenes."""

    def __init__(self, window):
        """Inicializa la aplicación, configurando la ventana principal, los paneles de video y los botones de control."""
        self.window = window
        self.window.title("SPAD Pro — Analizador de Clorofila")
        self.window.configure(bg=BG)  # Configura el color de fondo de la ventana principal.
        self.window.resizable(False, False)  # Evita que la ventana sea redimensionable.

        self.PW, self.PH = 300, 210   # tamaño cada panel de cámara

        # Estado multi-captura
        self.capturas     = []   # lista de dicts {pv, pa, spad}
        self.frame_actual = None
        self.running      = True
        self.analizando   = False

        self.db = ExcelDB()   # historial persistente en Excel (spad_historial.xlsx)

        self._build_ui()
        # conexión con la cámara IP
        self.url = URL_CAMARA
        threading.Thread(target=self.stream_video, daemon=True).start()
        self.actualizar_vista_previa()

    # INTERFAZ GRÁFICA

    def _build_ui(self):
        # Encabezado
        hdr = tk.Frame(self.window, bg=BG)  # Marco para el encabezado de la aplicación.
        hdr.pack(fill="x", padx=20, pady=(16, 4))
        tk.Label(hdr, text="◈  SPAD PRO", bg=BG, fg=ACCENT,
                 font=("Segoe UI", 14, "bold")).pack(side="left")
        tk.Label(hdr, text="Análisis Multi-Zona de Clorofila",
                 bg=BG, fg=TEXT_SEC, font=("Segoe UI", 9)).pack(side="left", padx=10)
        self.lbl_status = tk.Label(hdr, text="● EN VIVO", bg=BG,
                                   fg=TEXT_DIM, font=("Segoe UI", 8, "bold"))
        self.lbl_status.pack(side="right")
        tk.Frame(self.window, bg=BORDER, height=1).pack(fill="x", padx=20, pady=4)

        # Fila superior: video en vivo + última captura
        top = tk.Frame(self.window, bg=BG)  # Fila superior con los paneles de video en vivo y última captura.
        top.pack(padx=20, pady=6)

        self.canvas_vid       = crear_panel_video(top, "VISTA EN VIVO", self.PW, self.PH)
        self.canvas_ultima    = crear_panel_video(top, "ÚLTIMA CAPTURA", self.PW, self.PH)
        self.canvas_verde     = crear_panel_video(top, "ZONA VERDE", self.PW, self.PH)
        self.canvas_amarilla  = crear_panel_video(top, "ZONA AMARILLA", self.PW, self.PH)

        # CAPTURAS DE ZONAS DE LA HOJA
        tk.Frame(self.window, bg=BORDER, height=1).pack(fill="x", padx=20, pady=(4, 2))
        strip_hdr = tk.Frame(self.window, bg=BG)
        strip_hdr.pack(fill="x", padx=20)
        tk.Label(strip_hdr, text="CAPTURAS DE ZONAS", bg=BG,
                 fg=TEXT_SEC, font=("Segoe UI", 7, "bold")).pack(side="left")
        self.lbl_n = tk.Label(strip_hdr, text="0 / 5", bg=BG,
                               fg=ACCENT, font=("Courier New", 9, "bold"))
        self.lbl_n.pack(side="right")

        self.strip_frame = tk.Frame(self.window, bg=BG)
        self.strip_frame.pack(padx=20, pady=(2, 6))

        self.thumbs      = []   # tk widgets: contenedores de miniaturas de cada zona capturada
        self.thumb_imgs  = []   # PhotoImage refs (evitar GC)
        self.spad_lbls   = []   # etiquetas SPAD por miniatura

        TW, TH = 180, 100  # Tamaño de cada miniatura
        for i in range(NUM_CAPTURAS):
            col = tk.Frame(self.strip_frame, bg=BORDER, padx=1, pady=1)
            col.pack(side="left", padx=4)
            inner = tk.Frame(col, bg=PANEL)
            inner.pack()
            tk.Label(inner, text=f"ZONA {i+1}", bg=PANEL, fg=TEXT_DIM,
                     font=("Segoe UI", 6, "bold")).pack(pady=(3, 0))
            c = tk.Canvas(inner, width=TW, height=TH, bg="#080F0B",
                           highlightthickness=0)
            c.pack(padx=0, pady=(1, 0))
            c.create_text(TW // 2, TH // 2, text=f"{i+1}", fill=TEXT_DIM,
                           font=("Courier New", 18), tags="num")
            lbl = tk.Label(inner, text="—", bg=PANEL, fg=TEXT_DIM,
                           font=("Courier New", 9, "bold"))
            lbl.pack(pady=(1, 3))
            self.thumbs.append((c, TW, TH))
            self.thumb_imgs.append(None)
            self.spad_lbls.append(lbl)

        # Botones
        btn_row = tk.Frame(self.window, bg=BG)
        btn_row.pack(pady=(4, 4))

        self.btn_cap = crear_boton(btn_row, " CAPTURAR ZONA",
                                    self.capturar_zona, ACCENT)
        self.btn_cap.pack(side="left", padx=6)

        self.btn_reset = crear_boton(btn_row, " REINICIAR",
                                      self.reiniciar, TEXT_SEC)
        self.btn_reset.pack(side="left", padx=6)

        self.btn_hist = crear_boton(btn_row, " HISTORIAL",
                                     self.mostrar_historial, BLUE)
        self.btn_hist.pack(side="left", padx=6)

        # Panel de resultados promedio
        tk.Frame(self.window, bg=BORDER, height=1).pack(fill="x", padx=20, pady=(4, 0))
        res_outer = tk.Frame(self.window, bg=BORDER)
        res_outer.pack(padx=20, pady=(0, 4), fill="x")
        res = tk.Frame(res_outer, bg=PANEL, padx=20, pady=12)
        res.pack(fill="x", padx=1, pady=1)

        spad_col = tk.Frame(res, bg=PANEL)  # Columna del valor SPAD promedio.
        spad_col.pack(side="left", padx=(0, 30))
        tk.Label(spad_col, text="SPAD PROMEDIO", bg=PANEL, fg=TEXT_SEC,
                 font=("Segoe UI", 8, "bold")).pack(anchor="w")
        self.lbl_spad = tk.Label(spad_col, text="—", bg=PANEL,
                                  fg=TEXT_DIM, font=FONT_BIG)
        self.lbl_spad.pack(anchor="w")
        tk.Label(spad_col, text="unidades relativas  (5 zonas)", bg=PANEL,
                 fg=TEXT_DIM, font=("Segoe UI", 8)).pack(anchor="w")

        tk.Frame(res, bg=BORDER, width=1).pack(side="left", fill="y", padx=10)

        met_col = tk.Frame(res, bg=PANEL)  # Columna de métricas (verde, amarillo, diagnóstico, desviación estándar).
        met_col.pack(side="left")
        self.lbl_verde    = crear_metrica(met_col, "Verde promedio",    "—%",  ACCENT)
        self.lbl_amarillo = crear_metrica(met_col, "Amarillo promedio", "—%",  ACCENT_WARM)
        self.lbl_diag     = crear_metrica(met_col, "Diagnóstico",       "Captura 5 zonas de la hoja", TEXT_SEC)
        self.lbl_std      = crear_metrica(met_col, "Desv. estándar",    "—",   TEXT_SEC)

        # Barra cromática
        bar_frame = tk.Frame(self.window, bg=BG)
        bar_frame.pack(padx=20, pady=(2, 4), fill="x")
        tk.Label(bar_frame, text="DISTRIBUCIÓN CROMÁTICA PROMEDIO", bg=BG,
                 fg=TEXT_SEC, font=("Segoe UI", 7, "bold")).pack(anchor="w")
        bar_outer = tk.Frame(bar_frame, bg=BORDER, height=10)
        bar_outer.pack(fill="x", pady=3)
        bar_outer.pack_propagate(False)
        self.bar_canvas = tk.Canvas(bar_outer, height=10, bg=TEXT_DIM,
                                     highlightthickness=0)
        self.bar_canvas.pack(fill="both")

        # Pie
        tk.Frame(self.window, bg=BORDER, height=1).pack(fill="x", padx=20, pady=(4, 0))
        footer = tk.Frame(self.window, bg=BG)
        footer.pack(fill="x", padx=20, pady=5)
        tk.Label(footer,
                 text="Captura 5 zonas distintas de la hoja → el sistema promedia y muestra el SPAD final  ·  Calibrar con SPAD-502 para valores absolutos",
                 bg=BG, fg=TEXT_DIM, font=("Segoe UI", 8)).pack(side="left")

    # Video
    def stream_video(self):
        """Captura el video en vivo desde la cámara IP en un hilo aparte, actualizando el estado de la conexión y el último frame disponible."""
        cap = cv2.VideoCapture(self.url)
        while self.running:
            ret, frame = cap.read()
            if ret:
                self.frame_actual = frame
                self.lbl_status.config(fg=ACCENT)
            else:
                self.lbl_status.config(fg=RED)
                time.sleep(0.5)
        cap.release()

    def _mostrar(self, img_bgr, canvas, overlay=None):
        """Muestra una imagen en un canvas de Tkinter, redimensionándola al tamaño del panel y dibujando un texto de superposición opcional."""
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb).resize((self.PW, self.PH))
        img_tk  = ImageTk.PhotoImage(img_pil)
        canvas.delete("nosig")
        canvas.create_image(0, 0, anchor="nw", image=img_tk)
        canvas.image = img_tk
        if overlay:
            canvas.create_text(6, self.PH - 14, anchor="w",
                                text=overlay, fill=ACCENT, font=FONT_MONO)

    def _mostrar_thumb(self, idx, img_bgr, spad):
        """Muestra una miniatura de la zona capturada y actualiza la etiqueta SPAD asociada."""
        c, TW, TH = self.thumbs[idx]
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb).resize((TW, TH))
        img_tk  = ImageTk.PhotoImage(img_pil)
        c.delete("num")
        c.create_image(0, 0, anchor="nw", image=img_tk)
        c.image = img_tk
        self.thumb_imgs[idx] = img_tk
        self.spad_lbls[idx].config(text=f"SPAD {spad:.1f}", fg=ACCENT)

    def actualizar_vista_previa(self):
        """Actualiza la vista previa en vivo, dibujando el recuadro de análisis y el número de zona actual. Se reprograma periódicamente."""
        if self.frame_actual is not None:
            h, w = self.frame_actual.shape[:2]
            x1, y1 = w // 10, h // 10
            x2, y2 = 9 * w // 10, 9 * h // 10
            fg = self.frame_actual.copy()
            cv2.rectangle(fg, (x1, y1), (x2, y2), (80, 160, 255), 2)  # Recuadro azul indicando la ROI que se analizará.
            L = 16
            for px, py, dx, dy in [(x1, y1, 1, 1), (x2, y1, -1, 1), (x1, y2, 1, -1), (x2, y2, -1, -1)]:  # Esquinas del recuadro de análisis.
                cv2.line(fg, (px, py), (px + dx * L, py), (80, 200, 255), 3)
                cv2.line(fg, (px, py), (px, py + dy * L), (80, 200, 255), 3)
            # Contador en vivo
            n = len(self.capturas)
            cv2.putText(fg, f"Zona {n+1}/5", (x1 + 6, y1 + 22),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (80, 220, 255), 1, cv2.LINE_AA)
            self._mostrar(fg, self.canvas_vid)
        self.window.after(30, self.actualizar_vista_previa)  # Reprograma la siguiente actualización en 30 ms.

    # Captura y análisis

    def capturar_zona(self):
        """Captura la zona de la hoja dentro del recuadro de análisis, la analiza y actualiza la interfaz con los resultados."""
        if self.frame_actual is None or self.analizando:
            return
        if len(self.capturas) >= NUM_CAPTURAS:
            return   # ya tenemos todas

        self.analizando = True
        self.btn_cap.config(state="disabled", text="Procesando…", fg=TEXT_DIM)

        def _run():
            """Procesa la captura en un hilo separado para no congelar la interfaz."""
            frame = self.frame_actual.copy()
            h, w  = frame.shape[:2]  # Altura y ancho del frame
            x1, y1 = w // 10, h // 10  # Coordenadas del recuadro de análisis (10% a 90% del ancho y alto)
            x2, y2 = 9 * w // 10, 9 * h // 10
            roi = frame[y1:y2, x1:x2]  # Recorte del frame para analizar solo la zona central
            res = analizar_roi(roi)
            if res is None:
                self.lbl_diag.config(
                    text="Muestra insuficiente — reencuadra la hoja", fg=RED)
                self.btn_cap.config(state="normal",
                                    text=" CAPTURAR ZONA", fg=ACCENT)
                self.analizando = False
                return

            pv, pa, spad, mask_v, mask_a = res
            idx = len(self.capturas)
            self.capturas.append({"pv": pv, "pa": pa, "spad": spad})

            # Mostrar última captura y sus máscaras
            self._mostrar(roi, self.canvas_ultima, overlay=f"Zona {idx+1} — SPAD {spad:.1f}")
            self._mostrar(cv2.bitwise_and(roi, roi, mask=mask_v),
                           self.canvas_verde,
                           overlay=f"Verde {pv:.1f}%")
            self._mostrar(cv2.bitwise_and(roi, roi, mask=mask_a),
                           self.canvas_amarilla,
                           overlay=f"Amarillo {pa:.1f}%")
            self._mostrar_thumb(idx, roi, spad)
            self.lbl_n.config(text=f"{idx+1} / {NUM_CAPTURAS}")

            if len(self.capturas) == NUM_CAPTURAS:
                self._calcular_promedio()
                self.btn_cap.config(state="disabled",
                                    text="5 zonas completadas", fg=TEXT_SEC)
            else:
                self.btn_cap.config(state="normal",
                                    text=f"CAPTURAR ZONA  ({idx+1}/{NUM_CAPTURAS})",
                                    fg=ACCENT)
            self.analizando = False

        threading.Thread(target=_run, daemon=True).start()

    def _calcular_promedio(self):
        """Calcula los promedios y la desviación estándar de las zonas capturadas, actualiza la UI y guarda la sesión en el Excel."""
        pvs   = [c["pv"]   for c in self.capturas]
        pas   = [c["pa"]   for c in self.capturas]
        spads = [c["spad"] for c in self.capturas]

        avg_pv   = np.mean(pvs)    # Promedio de los porcentajes de verde de las zonas capturadas.
        avg_pa   = np.mean(pas)    # Promedio de los porcentajes de amarillo de las zonas capturadas.
        avg_spad = np.mean(spads)  # Promedio de los valores SPAD de las zonas capturadas.
        std_spad = np.std(spads)   # Desviación estándar de los valores SPAD (variabilidad entre zonas).

        if avg_spad >= 45:  # Clorofila óptima
            diag, col = "Clorofila óptima ", ACCENT
        elif avg_spad >= 30:  # Clorofila moderada
            diag, col = "Nivel moderado — revisar", ACCENT_WARM
        else:
            diag, col = "Clorosis detectada ", RED

        self.lbl_spad.config(text=f"{avg_spad:.1f}", fg=ACCENT)
        self.lbl_verde.config(text=f"{avg_pv:.1f}%")
        self.lbl_amarillo.config(text=f"{avg_pa:.1f}%")
        self.lbl_diag.config(text=diag, fg=col)
        self.lbl_std.config(text=f"± {std_spad:.2f}  (variación entre zonas)")

        self._actualizar_barra(avg_pv, avg_pa)

        # Guarda la sesión (5 mediciones + promedio) en el Excel. No bloquea: solo se encola.
        self.db.guardar_sesion(self.capturas, avg_pv, avg_pa, avg_spad, std_spad, diag)

    def _actualizar_barra(self, pv, pa):
        """Actualiza la barra cromática con la distribución promedio de verde y amarillo."""
        self.bar_canvas.update_idletasks()
        W = self.bar_canvas.winfo_width()
        H = 10
        self.bar_canvas.delete("all")
        self.bar_canvas.create_rectangle(0, 0, W, H, fill=TEXT_DIM, outline="")
        xv = int(W * pv / 100)  # Posición final del rectángulo verde, proporcional al porcentaje de verde promedio.
        self.bar_canvas.create_rectangle(0, 0, xv, H, fill=ACCENT, outline="")
        xa = int(W * pa / 100)  # Posición final del rectángulo amarillo, proporcional al porcentaje de amarillo promedio.
        self.bar_canvas.create_rectangle(xv, 0, xv + xa, H, fill=ACCENT_WARM, outline="")

    def reiniciar(self):
        """Reinicia la aplicación: borra las capturas, restablece los valores mostrados y limpia los paneles."""
        self.capturas = []
        self.thumb_imgs = [None] * NUM_CAPTURAS
        for i, (c, TW, TH) in enumerate(self.thumbs):
            c.delete("all")
            c.create_text(TW // 2, TH // 2, text=f"{i+1}", fill=TEXT_DIM,
                           font=("Courier New", 18), tags="num")
            self.spad_lbls[i].config(text="—", fg=TEXT_DIM)

        self.lbl_n.config(text="0 / 5")
        self.lbl_spad.config(text="—", fg=TEXT_DIM)
        self.lbl_verde.config(text="—%")
        self.lbl_amarillo.config(text="—%")
        self.lbl_diag.config(text="Captura 5 zonas de la hoja", fg=TEXT_SEC)
        self.lbl_std.config(text="—")
        self.bar_canvas.delete("all")

        # Limpiar paneles
        for canvas in [self.canvas_ultima, self.canvas_verde, self.canvas_amarilla]:
            canvas.delete("all")
            canvas.create_text(self.PW // 2, self.PH // 2, text="SIN SEÑAL",
                                fill=TEXT_DIM, font=FONT_MONO, tags="nosig")

        self.btn_cap.config(state="normal",
                             text=" CAPTURAR ZONA", fg=ACCENT)

    # Historial (Excel)

    def mostrar_historial(self):
        """Abre la ventana con el historial de sesiones guardadas en el Excel (ver historial_window.py)."""
        mostrar_historial(self.window, self.db)

    def on_closing(self):
        """Maneja el cierre de la ventana principal: detiene el video, cierra el Excel ordenadamente y destruye la ventana."""
        self.running = False
        self.db.cerrar()
        self.window.destroy()
